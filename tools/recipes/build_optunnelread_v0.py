r"""build_optunnelread_v0.py - OpTunnelRead_v0.vi: the INNER terminals of a case/loop tunnel, per frame.

Derived from OpWireSource_v5 (verified 12/12) by retargeting its cast from `Wire` to `Tunnel` and replacing
`Wire.Terms[]` with `Tunnel.Inside Terminals[]` 6356000. Everything downstream is reused unchanged (Is Source?, the
reciprocal Connected Wire -> UID, Owner -> ClassName and cast -> UID), and `Terminal.Diagram` 634A002 -> `UID` is
added so each inner terminal can be mapped to its FRAME - the inner-terminal array order is NOT documented as frame
order (peer 2026-09-15-case-frame-reader-property-ids).

Census B needs it: Case #5540's two outputs are driven by SelectorTunnel 6016 (`x,y,z array`) and 5680
(`Bead is good? array in`) - measured by OpWireSource_v5 in tools/bench/diag_case5540_tunnels.log - and the question
is what each FRAME puts on them.

Gates = predictions: the Tunnel-typed seed appears and the VI stays runnable at every save boundary; reference
provenance is asserted on every rewire (seed -> cast 'target class', cast -> Inside Terminals[], InsideTerms[] ->
Index Array 'array', element -> Diagram -> UID); ExecState 1 before the single save.
TEST (read-only, MAIN md5 in an outer finally): walk both tunnels' inner terminals; each must name its frame diagram
and its inner wire, and the two tunnels must report the SAME set of frame diagrams (they belong to one case).

  py tools/bgrun.py --max-min 20 --log tools/bench/build_optunnelread_v0.log -- py -u tools/recipes/build_optunnelread_v0.py [--test-only]
"""
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402
import build_track_v6_core as B  # noqa: E402
from build_opconstvalue_v1 import MAIN, com_preflight, lv_pid, fresh  # noqa: E402
from build_opwiresource_v5 import OP as OP_V5, MAP_OUT as MAP_V5  # noqa: E402

must, walk, term = B.must, B.walk, B.term
g._run.__defaults__ = (6.0, 120.0)
OP = os.path.join(g.CLAUDEDEV, "OpTunnelRead_v0.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "optunnelread_labels.json")
OUT_JSON = os.path.join(os.path.dirname(HERE), "bench", "case5540_frames.json")
TUNNELS = ((6016, "#5540 output -> x,y,z array"), (5680, "#5540 output -> Bead is good? array in"))
MAIN_BASE = (hashlib.md5(open(MAIN, "rb").read()).hexdigest(), os.path.getmtime(MAIN))


def prop_node(cls, pid, short, pos):
    pn0 = g.uids(OP, "Property")
    g.build_property(OP, cls, [(pid, False)], pos)
    new = [u for u in g.uids(OP, "Property") if u not in pn0]
    must(f"exactly one new Property node ({cls.split(':')[1]}.{short})", len(new) == 1, str(new))
    w = walk(OP, 0)
    must(f"the node has '{short}' as a SOURCE", term(w[new[0]][2], short, True) is not None,
         str([(r["name"], r["is_source"]) for r in w[new[0]][2]]))
    return new[0]


def add_indicator(uid, name, key, labels):
    w = walk(OP, 0)
    rows0 = {r["uid"]: r for r in g.panel_wiring(OP)}
    g.create_indicator(OP, w[uid][0], term(w[uid][2], name, True)["i"])
    rows1 = {r["uid"]: r for r in g.panel_wiring(OP)}
    new = [r for u, r in rows1.items() if u not in rows0]
    must(f"exactly one new panel object for '{name}' ({key})", len(new) == 1, str(new))
    must(f"it is an INDICATOR with a unique label ({key})",
         new[0]["indicator"] and sum(1 for r in rows1.values() if r["label"] == new[0]["label"]) == 1, str(new[0]))
    labels[key] = new[0]["label"]


def drop_wire(uid):
    ws = [o["uid"] for o in g.report_all(OP, "Wire")]
    if uid in ws:
        g.delete_object(OP, "Wire", ws.index(uid), verify=False)


def main():
    if "--test-only" in sys.argv:
        fresh()
        with open(MAP_OUT, encoding="utf-8") as f:
            labels = json.load(f)
        must("S OpTunnelRead_v0.vi and its labels exist from a passed build", os.path.exists(OP) and "frame_uid" in labels, str(labels))
        return test(labels)
    must("S the v5 op exists", os.path.exists(OP_V5))
    with open(MAP_V5, encoding="utf-8") as f:
        labels = json.load(f)
    print(f"   LabVIEW pid before: {lv_pid()}", flush=True)
    fresh()
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(OP_V5, OP); time.sleep(0.3)
    g.open_panel(OP); time.sleep(0.8)
    es = [("copy of v5", g.exec_state(OP))]
    must("A the copied v5 op is runnable", es[-1][1] == 1, str(es))
    fi = lambda cls, u: [o["uid"] for o in g.report_all(OP, cls)].index(u)
    # A: the Inside Terminals[] reader and a Tunnel-typed seed taken from its own reference (create_control leaves the
    #    control WIRED, so the VI stays runnable - a broken VI cannot be saved)
    pnI = prop_node("VI Server:Tunnel", "6356000", "InsideTerms[]", (1100, 2400))
    w = walk(OP, 0)
    rows0 = {r["uid"]: r for r in g.panel_wiring(OP)}
    g.create_control(OP, w[pnI][0], term(w[pnI][2], "reference", False)["i"])
    rows1 = {r["uid"]: r for r in g.panel_wiring(OP)}
    new_ctl = [r for u, r in rows1.items() if u not in rows0]
    must("A exactly one new control (Tunnel-typed seed)", len(new_ctl) == 1, str(new_ctl))
    labels["seedT"] = new_ctl[0]["label"]
    es.append(("Inside Terminals[] node + Tunnel seed (wired)", g.exec_state(OP)))
    must("A runnable with the seed wired", es[-1][1] == 1, str(es))
    # B: retarget the lookup cast Wire -> Tunnel and feed the Index Array from Inside Terminals[]
    w = walk(OP, 0)
    tw = next(u for u, v in w.items() if term(v[2], "Terms[]", True))
    w_terms = term(w[tw][2], "Terms[]", True)["wire"]
    ia = next(u for u, v in w.items() if term(v[2], "array", False) and term(v[2], "array", False)["wire"] == w_terms)
    w_castout = term(w[tw][2], "reference", False)["wire"]
    cast1 = next(u for u, v in w.items() if term(v[2], "specific class reference", True)
                 and term(v[2], "specific class reference", True)["wire"] == w_castout)
    print(f"   WIRING Terms[] node {tw} (out wire {w_terms}) -> Index Array {ia}; lookup cast {cast1}", flush=True)
    pw = {r["label"]: r for r in g.panel_wiring(OP)}
    drop_wire(w_terms)                              # Terms[] -> IA.array
    drop_wire(pw[labels["seedW"]]["wire"])          # Wire seed -> cast target class
    drop_wire(pw[labels["seedT"]]["wire"])          # Tunnel seed -> InsideTerms node (re-made below)
    # the obsolete Wire.Terms[] node goes FIRST: while it exists it still consumes the cast's output, which would make
    # the next connection a branch rather than the single feed this op wants (run 1, 13:2x).
    # NO Remove Bad Wires inside this window (runs 2-3, 13:3x): with the Index Array's `array` input momentarily
    # unwired, its `element` output loses its type, every wire downstream of it counts as broken, and Remove Bad Wires
    # deletes the whole terminal-reader chain - which is what the orphan dump showed. Repair the graph first, clean up
    # after (the reviewer listed exactly this as a plausible cause).
    g.delete_object(OP, "Property", fi("Property", tw), verify=False)
    es.append(("old wiring + Wire.Terms[] node removed (VI broken here - never saved in this state)", g.exec_state(OP)))
    g.wire_control(OP, [labels["seedT"]], "Function", fi("Function", cast1), ["target class"])
    # deleting the sink NODE leaves the wire stub hanging off the source, so this connection is a BRANCH; the stub is
    # cleaned up by the single Remove Bad Wires at the END of the edit (never inside the window - runs 2-3).
    g.wire(OP, "Function", fi("Function", cast1), "specific class reference", "Property", fi("Property", pnI), "reference", branch=True)
    g.wire(OP, "Property", fi("Property", pnI), "InsideTerms[]", "IndexArray", fi("IndexArray", ia), "array")
    w = walk(OP, 0); pw = {r["label"]: r for r in g.panel_wiring(OP)}
    must("B PROVENANCE Tunnel seed -> cast 'target class'",
         pw[labels["seedT"]]["wire"] and pw[labels["seedT"]]["wire"] == term(w[cast1][2], "target class", False)["wire"])
    a = term(w[cast1][2], "specific class reference", True)["wire"]; b = term(w[pnI][2], "reference", False)["wire"]
    must("B PROVENANCE cast output -> Inside Terminals[] node", a and a == b, f"{a}/{b}")
    a = term(w[pnI][2], "InsideTerms[]", True)["wire"]; b = term(w[ia][2], "array", False)["wire"]
    must("B PROVENANCE Inside Terminals[] -> Index Array 'array'", a and a == b, f"{a}/{b}")
    g.remove_bad_wires_scripted(OP)          # the ONE cleanup, after the graph is whole again
    es.append(("retargeted to Tunnel.Inside Terminals[] (+ single cleanup)", g.exec_state(OP)))
    if es[-1][1] != 1:
        # the localisation that worked in OpWireSource_v5: print every unwired SINK instead of guessing which edge
        # the deletions took with them (a wire is one object shared by every sink).
        w = walk(OP, 0)
        orphans = [(u, w[u][1], r["name"]) for u in w for r in w[u][2]
                   if not r["is_source"] and r["wire"] == 0 and not r["name"].lower().startswith("error")]
        print(f"   DIAG unwired sinks after the retarget: {orphans}", flush=True)
        # run 3 taught the obvious: terminal readers must be re-fed from the Index Array ELEMENT, never from the cast
        # (the cast carries a Tunnel; those nodes consume a Terminal).
        for u, lab, name in orphans:
            if name == "reference" and u != pnI:
                g.wire(OP, "IndexArray", fi("IndexArray", ia), "element", "Property", fi("Property", u),
                       "reference", branch=True)
                print(f"   DIAG re-fed node {u} ({lab}) 'reference' from the Index Array element", flush=True)
        es.append(("orphaned references re-fed from the element", g.exec_state(OP)))
        print(f"OBSERVED ExecState per step: {es}", flush=True)
    must("B runnable after the retarget", es[-1][1] == 1, str(es))
    # C: which FRAME each inner terminal belongs to
    w = walk(OP, 0)
    el_w = term(w[ia][2], "element", True)["wire"]
    pnD = prop_node("VI Server:Terminal", "634A002", "Diagram", (1900, 2400))
    g.wire(OP, "IndexArray", fi("IndexArray", ia), "element", "Property", fi("Property", pnD), "reference", branch=True)
    pnDU = prop_node("VI Server:GObject", "632A813", "UID", (2300, 2400))
    g.wire(OP, "Property", fi("Property", pnD), "Diagram", "Property", fi("Property", pnDU), "reference")
    w = walk(OP, 0)
    must("C PROVENANCE the Diagram node reads the indexed element",
         term(w[pnD][2], "reference", False)["wire"] == el_w, str(el_w))
    a = term(w[pnD][2], "Diagram", True)["wire"]; b = term(w[pnDU][2], "reference", False)["wire"]
    must("C Diagram -> UID on both ends (Diagram inherits GObject)", a and a == b, f"{a}/{b}")
    add_indicator(pnDU, "UID", "frame_uid", labels)
    add_indicator(pnDU, "error out", "errD", labels)
    es.append(("frame reader", g.exec_state(OP)))
    print(f"OBSERVED ExecState per step: {es}", flush=True)
    must("C op runnable before the save", es[-1][1] == 1, str(es))
    g.save(OP); g.close_panel(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)
    print(f"   labels {labels}", flush=True)
    return test(labels)


def read_inner(vi, labels, tunnel_uid, idx):
    for lab in (labels["ownercls"], labels["cls_back"]):
        vi.SetControlValue(lab, "POISON")
    for lab in (labels["uid_back"], labels["owner_uid"], labels["recip_wire"], labels["frame_uid"]):
        vi.SetControlValue(lab, 0)
    vi.SetControlValue(labels["is_source"], False)
    vi.SetControlValue("vi path", MAIN); vi.SetControlValue(labels["uid_in"], tunnel_uid)
    vi.SetControlValue(labels["term_index"], idx)
    try:
        g._run(vi); err = g._err(vi, "error out") or ""
    except Exception as e:
        err = f"EXC {str(e)[:80]}"
    errs = " ".join(x for x in (g._err(vi, labels[k]) or "" for k in ("errL", "errO", "errU", "errG", "errS", "errWU", "errCO", "errD")) if x)
    r = dict(tunnel=tunnel_uid, index=idx, uid_back=int(vi.GetControlValue(labels["uid_back"])),
             tunnel_class=vi.GetControlValue(labels["cls_back"]), is_source=bool(vi.GetControlValue(labels["is_source"])),
             owner_class=vi.GetControlValue(labels["ownercls"]), owner_uid=int(vi.GetControlValue(labels["owner_uid"])),
             inner_wire=int(vi.GetControlValue(labels["recip_wire"])), frame_uid=int(vi.GetControlValue(labels["frame_uid"])),
             err=err, errs=errs)
    print(f"OBSERVED: tunnel {tunnel_uid} ({r['tunnel_class']!r:.18}) inner[{idx}] frame(diagram) {r['frame_uid']} "
          f"wire {r['inner_wire']} source={r['is_source']} owner {r['owner_class']!r:.22} uid {r['owner_uid']} "
          f"{err[:20]} {errs[:40]}", flush=True)
    return r


def test(labels):
    vi = g.op(OP)
    try:
        out = {}
        for tun, role in TUNNELS:
            rows = []
            for i in range(8):
                r = read_inner(vi, labels, tun, i)
                if r["errs"] and r["inner_wire"] == 0 and r["frame_uid"] == 0:
                    break
                rows.append(r)
            out[tun] = rows
            print(f"RESULT tunnel {tun} ({role}): {len(rows)} inner terminals -> "
                  f"{[(r['index'], r['frame_uid'], r['inner_wire']) for r in rows]}", flush=True)
        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in out.items()}, f, indent=1, default=str)
        must("T1 both tunnels report at least two inner terminals (one per case frame)",
             all(len(v) >= 2 for v in out.values()), str({k: len(v) for k, v in out.items()}))
        must("T2 every inner terminal names its frame diagram and its inner wire",
             all(r["frame_uid"] and r["inner_wire"] for v in out.values() for r in v),
             str([(r["index"], r["frame_uid"], r["inner_wire"]) for v in out.values() for r in v]))
        must("T3 the two tunnels report the SAME set of frame diagrams (they belong to one case structure)",
             {r["frame_uid"] for r in out[TUNNELS[0][0]]} == {r["frame_uid"] for r in out[TUNNELS[1][0]]},
             str([sorted({r["frame_uid"] for r in v}) for v in out.values()]))
        n_ok = sum(1 for _n, p in B.PASS if p)
        print(f"\nSUMMARY {n_ok}/{len(B.PASS)} PASS", flush=True)
        return 0 if B.PASS and n_ok == len(B.PASS) else 1
    finally:
        same = (hashlib.md5(open(MAIN, "rb").read()).hexdigest(), os.path.getmtime(MAIN)) == MAIN_BASE
        print(f"   {'PASS' if same else 'FAIL'} T(finally) the main VI file is byte-identical and untouched", flush=True)
        B.PASS.append(("T(finally) main VI untouched", same))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except B.Stop as e:
        print(f"\nSTOP at gate: {e}", flush=True); sys.exit(1)
    except Exception as e:
        import traceback
        print(f"\nOBSERVED EXC {str(e)[:300]}\n{traceback.format_exc()[-1500:]}", flush=True); sys.exit(1)
