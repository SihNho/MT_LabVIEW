"""T5 STRUCTURE check (card chat-N2) - pure Python, no model, no LabVIEW. Run after matbench's T5 batch.

    MATERIAL=1 py tools/bgrun.py --max-min 20 --log tools/bench/matbench/t5_struct.log -- py -u tools/bench/matbench/t5_struct.py

WHY: truth_v0's T5 metric ("end computation_diff rows == the reference plan's end rows") was measured to be
DEGENERATE on this base: the reference plan's end rows are the 15 rows the BASE graph already has before any action
(stagesim first_divergent n=0 'base', rows_from_here 15), so a plan that does nothing meets it. This script adds the
STRUCTURAL comparison: in one worktree at T5's base, simulate the reference plan and every produced plan, and compare
each end state with the reference's end state as three sets relative to the base (step_00):
  moved   = {(uid, new owner)} for original objects whose owner changed
  added   = wire edges (source endpoint -> sink endpoint) present at the end but not in the base
  removed = wire edges present in the base but not at the end
An endpoint is (owner uid, term name) for an original object and ("new", owner class, owner's owner) for an object
the plan created (negative uid), so creation order does not matter. The EMPTY plan (the base itself) is scored too.
Writes runs/T5_c<n>/t5_struct.json and runs/t5_struct_summary.json. Ends with a RESULT line.
"""
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import matbench as M  # noqa: E402


def load_state(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)["state"]


def sig(state):
    objs = {o["uid"]: o for o in state["objs"]}

    def ep(t):
        u = t.get("owner_uid")
        if isinstance(u, int) and u < 0:
            o = objs.get(u, {})
            return ("new", t.get("owner_class"), o.get("owner"), t.get("term_name"))
        return (u, t.get("term_name"))
    nets = {}
    for t in state["terminals"]:
        w = t.get("wire_uid")
        if w:
            nets.setdefault(w, []).append(t)
    edges = set()
    for ts in nets.values():
        for s in (x for x in ts if x.get("is_source")):
            for k in (x for x in ts if not x.get("is_source")):
                edges.add((ep(s), ep(k)))
    owners = {u: o.get("owner") for u, o in objs.items() if isinstance(u, int) and u >= 0}
    return edges, owners


def delta(base, end):
    be, bo = base
    ee, eo = end
    moved = {(u, str(eo[u])) for u in eo if u in bo and str(eo[u]) != str(bo[u])}
    return {"moved": moved, "added": ee - be, "removed": be - ee}


def simulate(wt, plan, name):
    od = os.path.join(wt, ".matbench", "struct_" + name)
    r = subprocess.run([sys.executable, "tools/stagesim.py", "simulate", plan, M.K_GRAPH, "--out-root", od,
                        "--plan-out", od], cwd=wt, capture_output=True, text=True, errors="replace", timeout=900)
    steps = sorted(glob.glob(os.path.join(od, "*", "step_*.json")))
    return steps, r.returncode


def cmp(ref_d, d):
    out = {}
    tot_i = tot_u = 0
    for k in ("moved", "added", "removed"):
        a, b = {json.dumps(x, sort_keys=True, default=str) for x in d[k]}, \
               {json.dumps(x, sort_keys=True, default=str) for x in ref_d[k]}
        out[k] = {"n": len(a), "ref_n": len(b), "common": len(a & b), "missing": sorted(b - a)[:8],
                  "extra": sorted(a - b)[:8]}
        tot_i += len(a & b)
        tot_u += len(a | b)
    out["equal"] = all(out[k]["missing"] == [] and out[k]["extra"] == [] and out[k]["n"] == out[k]["ref_n"]
                       for k in ("moved", "added", "removed"))
    out["jaccard"] = round(tot_i / float(tot_u), 3) if tot_u else 1.0
    return out


def main():
    truth = json.load(open(M.TRUTH, encoding="utf-8"))
    wt, _card, _copied, _left = M.prepare("T5", 9, truth["conditions"][0])
    try:
        ref = os.path.join(wt, ".matbench", "ref_stageplan_k_split.json")
        os.makedirs(os.path.dirname(ref), exist_ok=True)
        with open(os.path.join(M.MAIN, M.K_REF.replace("/", os.sep)), "rb") as f, open(ref, "wb") as g:
            g.write(f.read())
        rsteps, rc = simulate(wt, ref, "ref")
        base = sig(load_state(rsteps[0]))
        ref_d = delta(base, sig(load_state(rsteps[-1])))
        summary = {"ref": {"steps": len(rsteps), "rc": rc, "moved": len(ref_d["moved"]), "added": len(ref_d["added"]),
                           "removed": len(ref_d["removed"])},
                   "empty_plan": cmp(ref_d, {"moved": set(), "added": set(), "removed": set()}), "cells": {}}
        print("REF steps %d moved %d added %d removed %d" % (len(rsteps), *(len(ref_d[k]) for k in ("moved", "added",
                                                                                                "removed"))))
        print("EMPTY plan equal=%s jaccard=%s" % (summary["empty_plan"]["equal"], summary["empty_plan"]["jaccard"]))
        for rd in sorted(glob.glob(os.path.join(M.RUNS, "T5_c*"))):
            plan = os.path.join(rd, "stageplan_k_split_out.json")
            name = os.path.basename(rd)
            if not os.path.isfile(plan):
                res = {"equal": False, "jaccard": 0.0, "note": "no plan"}
            else:
                steps, rc = simulate(wt, plan, name)
                res = cmp(ref_d, delta(base, sig(load_state(steps[-1])))) if len(steps) > 1 else \
                    {"equal": False, "jaccard": 0.0, "note": "sim produced %d steps rc %s" % (len(steps), rc)}
            json.dump(res, open(os.path.join(rd, "t5_struct.json"), "w", encoding="utf-8"), indent=1, default=str)
            summary["cells"][name] = {"equal": res["equal"], "jaccard": res["jaccard"]}
            print("CELL %s equal=%s jaccard=%s" % (name, res["equal"], res["jaccard"]), flush=True)
        json.dump(summary, open(os.path.join(M.RUNS, "t5_struct_summary.json"), "w", encoding="utf-8"), indent=1,
                  default=str)
    finally:
        M.remove_wt(wt)
    ok = summary["empty_plan"]["equal"] is False
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if ok else "FAIL",
                                   "gates": {"pass": 1 if ok else 0, "fail": 0 if ok else 1},
                                   "first_fail": None if ok else "empty plan equals the reference structurally",
                                   "artefacts": []}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
