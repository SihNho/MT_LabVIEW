"""sweep_subvis_main.py - subVI IDENTITY for every call site on every diagram of the main VI, by OpSubVIs_v0.

Fills the gap every 2026-09-14 document left open ("which VI does node X call"): one op run per diagram
(170 diagrams x ~1 s), reading VI Name / VI Path / UID arrays. Cross-checked against the Step-0 cache
tools/bench/diagram_tree_main.json: per diagram the UID set must equal (diagram uids  n  subvis keys); every
mismatch is printed and counted, never silently absorbed. Output: tools/bench/main_vi_subvis.json
    {"vi": ..., "diagrams": {"43": [{"uid": 5058, "name": "...", "path": "..."}, ...], ...},
     "by_uid": {"5058": {"diagram": 43, "name": ..., "path": ...}}, "callees": {"<name>": [uids...]},
     "mismatches": [...]}
Read-only against the main VI (opened by reference through the op, never edited or saved).
  py tools/bgrun.py --max-min 15 --log tools/bench/sweep_subvis_main.log -- py -u tools/bench/sweep_subvis_main.py
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

TREE = json.load(open(os.path.join(HERE, "diagram_tree_main.json"), encoding="utf-8"))
MAIN = TREE["vi"]
OUT = os.path.join(HERE, "main_vi_subvis.json")
g._run.__defaults__ = (6.0, 120.0)


def run_op(target, diagram_index):
    rows, err = g.subvis(target, diagram_index, purge=False, strict=False)     # OpSubVIs_v1: 0 junk/call measured (T0)
    return [r["name"] for r in rows], [r["path"] for r in rows], [r["uid"] for r in rows], err


def main():
    g._lv = None
    subvis = {int(k) for k in TREE["subvis"].keys()}
    out = {"vi": MAIN, "diagrams": {}, "by_uid": {}, "callees": {}, "mismatches": []}
    t0 = time.time()
    total = 0
    for k in sorted(TREE["diagrams"], key=int):
        expect = set(TREE["diagrams"][k]["uids"]) & subvis
        try:
            names, paths, uids, err = run_op(MAIN, int(k))
        except Exception as e:
            out["mismatches"].append({"diagram": int(k), "why": f"EXC {str(e)[:120]}"})
            print(f"diagram {k}: EXC {str(e)[:120]}", flush=True)
            continue
        rows = [{"uid": u, "name": n, "path": p} for n, p, u in zip(names, paths, uids)]
        out["diagrams"][k] = rows
        total += len(rows)
        if err or set(uids) != expect:
            out["mismatches"].append({"diagram": int(k), "err": err, "op": sorted(uids), "cache": sorted(expect)})
            print(f"diagram {k}: MISMATCH err={err!r} op={sorted(uids)} cache={sorted(expect)}", flush=True)
        for r in rows:
            out["by_uid"][str(r["uid"])] = {"diagram": int(k), "name": r["name"], "path": r["path"]}
            out["callees"].setdefault(r["name"], []).append(r["uid"])
        if rows:
            print(f"diagram {k:>3} ({TREE['diagrams'][k]['owner'] or 'top'}): " +
                  ", ".join(f"{r['name']}#{r['uid']}" for r in rows), flush=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print(f"\n{total} subVI call sites on {len(out['diagrams'])} diagrams, {len(out['callees'])} distinct callees, "
          f"{len(out['mismatches'])} mismatches, {time.time() - t0:.0f} s -> {OUT}", flush=True)
    print("callees by call count:", flush=True)
    for name, us in sorted(out["callees"].items(), key=lambda kv: -len(kv[1])):
        print(f"   {len(us):3d}  {name}", flush=True)
    return 0 if not out["mismatches"] else 3


if __name__ == "__main__":
    sys.exit(main())
