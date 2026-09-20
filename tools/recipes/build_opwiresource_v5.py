r"""build_opwiresource_v5.py - OpWireSource_v5.vi = v4 with the owner-UID branch REWIRED to the right Owner node,
with reference provenance asserted (the single build-time gate the review asked for).

Why: v2 reported wire 10850's source as constant uid 3628 while the 180-object constant scan says constant 10739
feeds that wire. The review (archive/peer/2026-09-15-constant-vs-wire-source-uid-contradiction.md) supplies the
hypothesis my op could not see - **H5: the wire has TWO sources and is therefore broken** - and the algorithm that
settles it: enumerate the whole `Wire.Terminals[]`, and for each terminal read `Is Source?`, its owner, and its
reciprocal `Connected Wire`; then require exactly one terminal that is a source AND whose connected wire is the wire
asked about. "No error" proves the property read worked, never that the diagram is sound.

Added to v2 (all UPCASTS - Terminal and Wire both inherit GObject/Generic, so no further cast is needed):
  Terms[] --Index Array[`term index` control]--> Terminal.'Is Source?' 634A003 (short name IsSource) -> indicator
                                             --> Terminal.'Wire' (Connected Wire 634A000) -> GObject.'UID' -> indicator
The existing Owner -> ClassName / TMSC2 -> UID chain keeps reporting the owner of the SAME indexed terminal.

Gates = predictions: one new control on the Index Array's `index` (so the element is selectable), each new property
node carrying its SHORT-named source terminal, wire uids equal on both ends, ExecState 1 before the single save.
TEST (read-only; MAIN md5 in an outer finally): walk terminal indices 0..5 of wire 10850 and print
(is source?, owner class/uid, reciprocal wire uid) for each; REQUIRE exactly one source terminal whose reciprocal
wire is 10850 - and report whether its owner is 3628 or 10739, which is the answer the reseed work is waiting for.

  py tools/bgrun.py --max-min 20 --log tools/bench/build_opwiresource_v5.log -- py -u tools/recipes/build_opwiresource_v5.py [--test-only]
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
from build_opwiresource_v4 import OP as OP_V2, MAP_OUT as MAP_V2  # noqa: E402

must, walk, term = B.must, B.walk, B.term
g._run.__defaults__ = (6.0, 120.0)
OP = os.path.join(g.CLAUDEDEV, "OpWireSource_v5.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opwiresource_v5_labels.json")
OUT_JSON = os.path.join(os.path.dirname(HERE), "bench", "wire10850_terminals_v5.json")
TARGET_WIRE = 10850
CLAIMS = {10739: "the constant scan's answer (value I32 0)", 3628: "the v2 wire-walk's answer"}
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


def main():
    if "--test-only" in sys.argv:
        fresh()
        with open(MAP_OUT, encoding="utf-8") as f:
            labels = json.load(f)
        must("S OpWireSource_v5.vi and its labels exist from a passed build", os.path.exists(OP) and "cast_class" in labels, str(labels))
        return test(labels)
    must("S the v4 op exists", os.path.exists(OP_V2))
    with open(MAP_V2, encoding="utf-8") as f:
        labels = json.load(f)
    print(f"   LabVIEW pid before: {lv_pid()}", flush=True)
    fresh()
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(OP_V2, OP); time.sleep(0.3)
    g.open_panel(OP); time.sleep(0.8)
    es = [("copy of v4", g.exec_state(OP))]
    must("A the copied v4 op is runnable", es[-1][1] == 1, str(es))
    w = walk(OP, 0)
    fi = lambda cls, u: [o["uid"] for o in g.report_all(OP, cls)].index(u)
    # v4 localised the defect (peer ...-v4-wrong-owner-node-localised, CONFIRMED): the op has TWO nodes exposing an
    # 'Owner' output. OpReport_v3's identity node describes the TRAVERSED object - its owner is a Diagram whose uid
    # (3628) never changes with the terminal index. The right node is the one FED BY the Terms[] Index Array element.
    tw = next(u for u, v in w.items() if term(v[2], "Terms[]", True))
    w_terms = term(w[tw][2], "Terms[]", True)["wire"]
    ia = next(u for u, v in w.items() if term(v[2], "array", False) and term(v[2], "array", False)["wire"] == w_terms)
    el_w = term(w[ia][2], "element", True)["wire"]
    owners = [u for u, v in w.items() if term(v[2], "Owner", True)]
    for u in owners:
        print(f"   WIRING Owner candidate {u}: reference wire {term(w[u][2], 'reference', False)['wire']} "
              f"(Terms[] element wire is {el_w}); Owner out {term(w[u][2], 'Owner', True)['wire']}", flush=True)
    right = [u for u in owners if term(w[u][2], "reference", False)["wire"] == el_w]
    must("A exactly one Owner node is fed by the Terms[] Index Array element", len(right) == 1, str(right))
    pnO = right[0]
    w_owner = term(w[pnO][2], "Owner", True)["wire"]
    uid_nodes = [u for u, v in w.items() if term(v[2], "UID", True)]
    tmscs = [u for u, v in w.items() if term(v[2], "specific class reference", True)]
    cast = [u for u in tmscs
            if any(term(w[x][2], "reference", False)["wire"] == term(w[u][2], "specific class reference", True)["wire"]
                   for x in uid_nodes)]
    must("A exactly one cast feeds a UID node (that is the owner-uid branch)", len(cast) == 1, str(cast))
    cast = cast[0]
    old_ref = term(w[cast][2], "reference", False)["wire"]
    print(f"   WIRING owner-uid branch: cast {cast} is fed by wire {old_ref}; the correct Owner output is {w_owner}", flush=True)
    if old_ref != w_owner:
        ws = [o["uid"] for o in g.report_all(OP, "Wire")]
        must("B the cast's current input wire exists", old_ref in ws, str(old_ref))
        g.delete_object(OP, "Wire", ws.index(old_ref), verify=False); g.remove_bad_wires_scripted(OP)
        es.append(("wrong Owner wire removed", g.exec_state(OP)))
        g.wire(OP, "Property", fi("Property", pnO), "Owner", "Function", fi("Function", cast), "reference", branch=True)
    w = walk(OP, 0)
    a = term(w[pnO][2], "Owner", True)["wire"]; b = term(w[cast][2], "reference", False)["wire"]
    must("B REFERENCE PROVENANCE: the cast's reference comes from the Terms[]-element Owner node", a and a == b, f"{a}/{b}")
    es.append(("owner-uid branch rewired", g.exec_state(OP)))
    if es[-1][1] != 1:
        # peer ...-v5-still-broken-after-rewire ranks H1 first: deleting wire 523 probably cut a SECOND sink. The
        # cheapest localisation is the terminal dump I already have - every SINK with wire 0, plus everything that
        # claims the new wire - so print it and repair the orphans instead of guessing.
        w = walk(OP, 0)
        orphans = [(u, w[u][1], r["name"]) for u in w for r in w[u][2]
                   if not r["is_source"] and r["wire"] == 0 and not r["name"].lower().startswith("error")]
        claim = [(u, w[u][1], r["name"]) for u in w for r in w[u][2] if r["wire"] == w_owner]
        print(f"   DIAG unwired sinks after the rewire: {orphans}", flush=True)
        print(f"   DIAG terminals on the Owner wire {w_owner}: {claim}", flush=True)
        # H1 repair: any node that USED to hang on the deleted wire is re-fed from the same Owner output.
        for u, lab, name in orphans:
            if name == "reference" and u not in (cast,):
                try:
                    g.wire(OP, "Property", fi("Property", u), "reference", "Property", fi("Property", pnO), "Owner", branch=True)
                except Exception:
                    g.wire(OP, "Property", fi("Property", pnO), "Owner", "Property", fi("Property", u), "reference", branch=True)
                print(f"   DIAG re-fed node {u} ({lab}) 'reference' from the Owner output", flush=True)
        es.append(("orphaned references re-fed", g.exec_state(OP)))
        print(f"OBSERVED ExecState per step: {es}", flush=True)
    must("B the op is runnable after the rewire", es[-1][1] == 1, str(es))
    print(f"OBSERVED ExecState per step: {es}", flush=True)
    must("C op runnable before the save", es[-1][1] == 1, str(es))
    g.save(OP); g.close_panel(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)
    print(f"   labels {labels}", flush=True)
    return test(labels)


def read_terminal(vi, labels, wire_uid, idx):
    for lab in (labels["ownercls"], labels["cls_back"]):
        vi.SetControlValue(lab, "POISON")
    for lab in (labels["uid_back"], labels["owner_uid"], labels["recip_wire"]):
        vi.SetControlValue(lab, 0)
    vi.SetControlValue(labels["is_source"], False); vi.SetControlValue(labels["cast_class"], "POISON")
    vi.SetControlValue("vi path", MAIN); vi.SetControlValue(labels["uid_in"], wire_uid); vi.SetControlValue(labels["term_index"], idx)
    try:
        g._run(vi); err = g._err(vi, "error out") or ""
    except Exception as e:
        err = f"EXC {str(e)[:80]}"
    errs = " ".join(x for x in (g._err(vi, labels[k]) or "" for k in ("errL", "errT", "errO", "errU", "errG", "errS", "errWU", "errCO")) if x)
    r = dict(wire=wire_uid, index=idx, uid_back=int(vi.GetControlValue(labels["uid_back"])),
             wire_class=vi.GetControlValue(labels["cls_back"]), is_source=bool(vi.GetControlValue(labels["is_source"])),
             owner_class=vi.GetControlValue(labels["ownercls"]), owner_uid=int(vi.GetControlValue(labels["owner_uid"])),
             recip_wire=int(vi.GetControlValue(labels["recip_wire"])), cast_class=vi.GetControlValue(labels["cast_class"]),
             err=err, errs=errs)
    print(f"OBSERVED: wire {wire_uid} Terms[{idx}] source={r['is_source']} owner {r['owner_class']!r:.26} uid {r['owner_uid']} "
          f"reciprocal wire {r['recip_wire']} | cast-output class {r['cast_class']!r:.26} {err[:24]} {errs[:50]}", flush=True)
    return r


def test(labels):
    vi = g.op(OP)
    try:
        rows = []
        for i in range(6):
            r = read_terminal(vi, labels, TARGET_WIRE, i)
            if r["errs"] and r["owner_uid"] == 0 and not r["is_source"]:
                print(f"   (index {i} past the end of Terms[] - stopping)", flush=True)
                break
            rows.append(r)
        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=1, default=str)
        must("T0 at least one terminal was read without error", rows and not rows[0]["err"], str(rows[:1]))
        srcs = [r for r in rows if r["is_source"] and r["recip_wire"] == TARGET_WIRE]
        print(f"SUMMARY wire {TARGET_WIRE}: {len(rows)} terminals read, {sum(1 for r in rows if r['is_source'])} report "
              f"Is Source? TRUE, {len(srcs)} of those also point back at this wire", flush=True)
        for r in srcs:
            print(f"   SOURCE: owner {r['owner_class']} uid {r['owner_uid']} = {CLAIMS.get(r['owner_uid'], 'neither previous claim')}", flush=True)
        must("T1 the wire has EXACTLY ONE source terminal whose reciprocal wire is itself (else the net is broken "
             "or ambiguous and neither earlier claim may be trusted)", len(srcs) == 1,
             str([(r["index"], r["is_source"], r["owner_uid"], r["recip_wire"]) for r in rows]))
        must("T2 the cast output denotes the SAME object as the owner (class equality) for the source terminal",
             srcs[0]["cast_class"] == srcs[0]["owner_class"], f"cast {srcs[0]['cast_class']!r} vs owner {srcs[0]['owner_class']!r}")
        must("T3 that single source is one of the two claimed constants", srcs[0]["owner_uid"] in CLAIMS,
             f"{srcs[0]['owner_uid']} vs {sorted(CLAIMS)}")
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
