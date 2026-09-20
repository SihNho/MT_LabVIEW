r"""build_opwiresource_v4.py - OpWireSource_v4.vi = v3 plus proof that the owner-UID branch reads what it claims.

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

  py tools/bgrun.py --max-min 20 --log tools/bench/build_opwiresource_v4.log -- py -u tools/recipes/build_opwiresource_v4.py [--test-only]
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
from build_opwiresource_v3 import OP as OP_V2, MAP_OUT as MAP_V2  # noqa: E402

must, walk, term = B.must, B.walk, B.term
g._run.__defaults__ = (6.0, 120.0)
OP = os.path.join(g.CLAUDEDEV, "OpWireSource_v4.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opwiresource_v4_labels.json")
OUT_JSON = os.path.join(os.path.dirname(HERE), "bench", "wire10850_terminals_v4.json")
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
        must("S OpWireSource_v4.vi and its labels exist from a passed build", os.path.exists(OP) and "cast_class" in labels, str(labels))
        return test(labels)
    must("S the v3 op exists", os.path.exists(OP_V2))
    with open(MAP_V2, encoding="utf-8") as f:
        labels = json.load(f)
    print(f"   LabVIEW pid before: {lv_pid()}", flush=True)
    fresh()
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(OP_V2, OP); time.sleep(0.3)
    g.open_panel(OP); time.sleep(0.8)
    es = [("copy of v3", g.exec_state(OP))]
    must("A the copied v3 op is runnable", es[-1][1] == 1, str(es))
    w = walk(OP, 0)
    fi = lambda cls, u: [o["uid"] for o in g.report_all(OP, cls)].index(u)
    # WIRING DUMP of the owner-uid branch: the review (…-owner-uid-constant-3628) is right that 3628 is not evidence
    # about anything until the branch is shown to read the indexed terminal's owner. Print the topology instead of
    # asserting it, then add Generic.'ClassName' on the CAST OUTPUT - the very object whose UID is printed.
    pnO = next(u for u, v in w.items() if term(v[2], "Owner", True))
    tmscs = [u for u, v in w.items() if term(v[2], "specific class reference", True)]
    for u in [pnO] + tmscs:
        print(f"   WIRING uid {u} label {w[u][1]!r}: "
              f"{[(r['name'], 'src' if r['is_source'] else 'sink', r['wire']) for r in w[u][2]]}", flush=True)
    w_owner = term(w[pnO][2], "Owner", True)["wire"]
    cast = [u for u in tmscs if term(w[u][2], "reference", False)["wire"] == w_owner]
    must("A exactly one cast node is fed by Generic.'Owner'", len(cast) == 1,
         f"{[(u, term(w[u][2], 'reference', False)['wire']) for u in tmscs]} vs Owner wire {w_owner}")
    cast = cast[0]
    w_cast = term(w[cast][2], "specific class reference", True)["wire"]
    uid_nodes = [u for u, v in w.items() if term(v[2], "UID", True) and term(v[2], "reference", False)["wire"] == w_cast]
    must("A exactly one UID node is fed by that cast's output", len(uid_nodes) == 1,
         f"cast out wire {w_cast}; UID nodes {[(u, term(w[u][2], 'reference', False)['wire']) for u, v in w.items() if term(v[2], 'UID', True)]}")
    print(f"   WIRING owner wire {w_owner} -> cast {cast} -> out wire {w_cast} -> UID node {uid_nodes[0]}", flush=True)
    pnCO = prop_node("VI Server:Generic", "6327803", "ClassName", (2700, 1800))
    g.wire(OP, "Function", fi("Function", cast), "specific class reference", "Property", fi("Property", pnCO), "reference", branch=True)
    w = walk(OP, 0)
    must("B cast output -> the new ClassName node on both ends",
         term(w[pnCO][2], "reference", False)["wire"] == w_cast, str(w_cast))
    es.append(("class-of-cast-output node", g.exec_state(OP)))
    add_indicator(pnCO, "ClassName", "cast_class", labels)
    add_indicator(pnCO, "error out", "errCO", labels)
    es.append(("indicators", g.exec_state(OP)))
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
