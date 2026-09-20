"""diagram_tree_validate.py - Step 0, phase 1: prove the diagram-membership method before spending an hour on the main VI.

The method for "which While loop holds what" is: walk every Diagram index with `net_map`, whose per-node first field is the
node UID (confirmed 2026-09-12 during the motion audit), and pair that with `report("Diagram")`, which gives each diagram's
OWNING STRUCTURE CLASS. What the API does NOT give is an explicit parent link from a subdiagram back to its structure node,
so reconstructing the tree leans on the Traverse ordering — an assumption, not a fact.

This validates the assumption against VIs whose structure we built ourselves and therefore know exactly:

NOTE (2026-09-12, first run): a Diagram object's TOP-LEVEL owner reports as the EMPTY STRING, not "TopLevelDiagram" —
the first run's data was perfect and only the assertion string was wrong.

  TRACK_kernel_v1.vi   built 2026-09-10: one Case Structure uid 154, frame 0 holds PARALLEL_kernel_v3 uid 155,
                       frame 1 holds GPU_kernel_v1 uid 156, and 3 Diagrams in total.
    predict: exactly one diagram owned by TopLevelDiagram and it contains uid 154;
             two diagrams owned by CaseStructure, one containing 155 and the other 156, and NOT both in one.
  PARALLEL_kernel_v3.vi  2 Diagrams: the top level and a For Loop's inner diagram.
    predict: one TopLevelDiagram, one owned by ForLoop, and the kernel subVI sits on the ForLoop one.

If the predictions hold, the walk over the main VI can be trusted. If they do not, the ordering assumption is wrong and the
tree needs a different construction before any conclusion about the frame loop is drawn.
  py tools/bgrun.py --max-min 15 --log tools/bench/diagram_tree_validate.log -- py -u tools/bench/diagram_tree_validate.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

TRACK = os.path.join(g.CLAUDEDEV, "TRACK_kernel_v1.vi")
PAR = os.path.join(g.CLAUDEDEV, "PARALLEL_kernel_v3.vi")
g._run.__defaults__ = (6.0, 45.0)


def walk(path):
    """{diagram index: (owner class, [node uid, ...])} for every diagram of `path`."""
    dias = g.report(path, "Diagram")
    print(f"   Diagram objects: {len(dias)} -> owners {[d['owner'] for d in dias]}", flush=True)
    out = {}
    for k in range(len(dias)):
        try:
            nodes, _ = g.net_map(path, diagram_index=k, max_nodes=80, max_terms=20)
        except Exception as e:
            print(f"   diagram {k}: net_map failed {str(e)[:100]}", flush=True)
            out[k] = (dias[k]["owner"], None); continue
        uids = [uid for uid, _lbl, _t in nodes.values()]
        out[k] = (dias[k]["owner"], uids)
        print(f"   diagram {k:2} owner={dias[k]['owner']:<18} node uids={uids}", flush=True)
    return out


def main():
    g._lv = None
    ok = True

    print("\n=== TRACK_kernel_v1 (built 2026-09-10: case 154, CPU frame 155, GPU frame 156) ===", flush=True)
    t = walk(TRACK)
    subs = {o["uid"]: o["pos"] for o in g.report(TRACK, "SubVI")}
    cases = [o["uid"] for o in g.report(TRACK, "CaseStructure")]
    print(f"   SubVI uids {sorted(subs)} | CaseStructure uids {cases}", flush=True)
    top = [k for k, (own, u) in t.items() if own in ("", "TopLevelDiagram")]
    frames = [k for k, (own, u) in t.items() if own == "CaseStructure"]
    print(f"   top-level diagram index {top}, case-frame diagram indices {frames}", flush=True)
    if len(top) != 1 or len(frames) != 2:
        print("   FAIL: expected 1 top-level diagram and 2 case frames", flush=True); ok = False
    else:
        case_uid = cases[0] if cases else None
        if case_uid is not None and case_uid not in (t[top[0]][1] or []):
            print(f"   FAIL: the Case Structure uid {case_uid} is not on the top-level diagram", flush=True); ok = False
        holders = {k: [u for u in (t[k][1] or []) if u in subs] for k in frames}
        print(f"   subVIs per case frame: {holders}", flush=True)
        sets = [set(v) for v in holders.values()]
        if any(len(s) != 1 for s in sets) or sets[0] == sets[1]:
            print("   FAIL: each case frame should hold exactly one DIFFERENT kernel subVI", flush=True); ok = False
        else:
            print("   PASS: the two kernels are on separate case-frame diagrams, as built", flush=True)

    print("\n=== PARALLEL_kernel_v3 (a For Loop with the bead kernel inside) ===", flush=True)
    p = walk(PAR)
    psubs = {o["uid"] for o in g.report(PAR, "SubVI")}
    loops = [k for k, (own, u) in p.items() if own == "ForLoop"]
    print(f"   SubVI uids {sorted(psubs)} | ForLoop-owned diagram indices {loops}", flush=True)
    if len(loops) != 1:
        print("   FAIL: expected exactly one ForLoop-owned diagram", flush=True); ok = False
    elif not (psubs & set(p[loops[0]][1] or [])):
        print("   FAIL: the kernel subVI is not on the ForLoop diagram", flush=True); ok = False
    else:
        print("   PASS: the kernel subVI sits on the ForLoop's inner diagram", flush=True)

    print(f"\nVALIDATION: {'PASS - the main-VI walk can be trusted' if ok else 'FAIL - do not walk the main VI yet'}", flush=True)
    return 0 if ok else 5


if __name__ == "__main__":
    sys.exit(main())
