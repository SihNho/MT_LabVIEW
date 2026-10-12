# ---
# labview: none
# hardware: none
# ---
r"""x10_bench - GPT vs Claude on matbench T1,T2,T3,T5,T6 (card chat-X10e; briefs chat-X10/X10b/X10c).

    py tools/bench/matbench/x10_bench.py claude [--tasks T1,T2,T3,T5,T6] [--reps 2] [--max-min 20]
    py tools/bench/matbench/x10_bench.py score  [--seed N]          (blind A/B scoring of x10/runs, then unblind)

The Claude arm = matbench.run_task with truth_v1's condition 2 (claude-opus-5-5 / high, agent per task) - "as
before" - each cell under its worktree's bgrun with the SAME per-cell deadline as the GPT cell (--max-min, 20 min,
card pass 2). The GPT arm runs separately (codex_arm.py gpt-bench; one fixed cell, serial). Both write
x10/runs/<task>_c<ci>_r<rep>/ (Claude c2, GPT c9).

Blind scoring: per task a random A/B assignment of the two arms is drawn and WRITTEN (x10/blind_mapping.json) before any
cell is scored; every run dir is copied to x10/blind/<task>_c<0|1>_r<rep>/ with meta.condition replaced by "arm/A|B";
score.score_all_v1 scores the blind copies against a truth whose conditions are [arm/A, arm/B]; only then is the
mapping applied (x10/results_x10.json). The scorer is mechanical (no model judges), so the blinding guards only the
bookkeeping; the cell logs themselves still name their model (a Claude envelope's modelUsage, a Codex thread).

PREDICTION CONTRACT (claude): 10 cells (5 tasks x 2 repeats), each ends (bgrun END or TIMEOUT <= 20 min), no new
LabVIEW pid, no worktree left; ends with a RESULT line. (score): every run dir with a meta.json is scored once;
mapping file written before results; RESULT line.

WHAT EXISTED FIRST: matbench.run_task / score.score_all_v1 (called, not copied); codex_arm.run_task_cell (GPT arm).
"""
import argparse
import glob
import json
import os
import random
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
X10 = os.path.join(HERE, "x10")
RUNS = os.path.join(X10, "runs")
sys.path.insert(0, HERE)
import matbench  # noqa: E402
import score  # noqa: E402

CLAUDE_CI = 2           # truth_v1 condition 2 = claude-opus-5-5 / high (the default material model)


def result_line(status, p, f, first_fail=None, artefacts=None):
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": status, "gates": {"pass": p, "fail": f},
                                   "first_fail": first_fail, "artefacts": artefacts or []}), flush=True)


def run_claude(tasks, reps, max_min, runs=RUNS):
    truth = json.load(open(matbench.TRUTH, encoding="utf-8"))
    os.makedirs(matbench.WTROOT, exist_ok=True)
    os.makedirs(runs, exist_ok=True)
    skipped, batches = [], []
    for tid in tasks:
        batches.append(matbench.run_task(tid, [CLAUDE_CI], truth, None, max_min, runs, reps, 3,
                                         truth.get("cost_guard_usd"), skipped))
    json.dump({"batches": batches, "skipped": skipped}, open(os.path.join(X10, "claude_batches.json"), "w",
                                                             encoding="utf-8"), indent=1)
    lv_new = sorted({p for b in batches for p in b["labview_new"]})
    left = [w for w in matbench.git("worktree", "list").splitlines()
            if os.path.normcase(matbench.WTROOT) in os.path.normcase(w.replace("/", os.sep))]
    n = len(glob.glob(os.path.join(runs, "*_c%d_r*" % CLAUDE_CI)))
    print("CLAUDE cells %d spent $%.2f lv_new %s left %s skipped %s" % (n, matbench.spent(runs), lv_new, left,
                                                                       skipped), flush=True)
    bad = (["new LabVIEW pid %s" % lv_new] if lv_new else []) + (["worktrees left %s" % left] if left else [])
    result_line("FAIL" if bad else "PASS", n, len(bad), bad[0] if bad else None)
    return 1 if bad else 0


def blind_score(seed=None, runs=RUNS):
    truth = json.load(open(matbench.TRUTH, encoding="utf-8"))
    dirs = sorted(d for d in glob.glob(os.path.join(runs, "*_c*_r*")) if os.path.isfile(os.path.join(d, "meta.json")))
    arms = sorted({json.load(open(os.path.join(d, "meta.json"), encoding="utf-8"))["cond"] for d in dirs})
    rng = random.Random(seed)
    tasks = sorted({os.path.basename(d).split("_")[0] for d in dirs})
    mapping = {}
    for t in tasks:
        a = list(arms)
        rng.shuffle(a)
        mapping[t] = {"A": a[0], "B": a[1] if len(a) > 1 else None}
    mp = os.path.join(X10, "blind_mapping.json")
    json.dump({"written": time.strftime("%Y-%m-%d %H:%M:%S"), "seed": seed, "arms": {"2": "claude-opus-5-5/high",
               "9": "gpt-6.1-sol/high"}, "mapping": mapping}, open(mp, "w", encoding="utf-8"), indent=1)
    bdir = os.path.join(X10, "blind")
    shutil.rmtree(bdir, ignore_errors=True)
    for d in dirs:
        meta = json.load(open(os.path.join(d, "meta.json"), encoding="utf-8"))
        t, ci = meta["task"], meta["cond"]
        letter = "A" if mapping[t]["A"] == ci else "B"
        nd = os.path.join(bdir, "%s_c%d_r%d" % (t, 0 if letter == "A" else 1, meta.get("rep", 1)))
        shutil.copytree(d, nd)
        meta["condition"] = {"model": "arm", "effort": letter, "agent": meta.get("agent")}
        meta["cond"] = 0 if letter == "A" else 1
        json.dump(meta, open(os.path.join(nd, "meta.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    btruth = dict(truth, conditions=[{"agent": "*", "model": "arm", "effort": "A"},
                                     {"agent": "*", "model": "arm", "effort": "B"}])
    res = score.score_all_v1(bdir, btruth, tasks=tasks)
    json.dump(res, open(os.path.join(X10, "results_x10_blind.json"), "w", encoding="utf-8"), indent=1,
              ensure_ascii=False, default=str)
    # unblind
    for c in res["cells"]:
        letter = c["ckey"].split("/")[-1]
        ci = mapping[c["task"]][letter]
        c["blind"] = letter
        c["arm"] = {2: "claude-opus-5-5/high", 9: "gpt-6.1-sol/high"}.get(ci, str(ci))
        src = os.path.join(runs, "%s_c%d_r%d" % (c["task"], ci, c["rep"]))
        c["rundir"] = score.rel(src)
        meta = json.load(open(os.path.join(src, "meta.json"), encoding="utf-8"))
        env = score.cell_envelope(score.rd(os.path.join(src, "cell.log")))
        c["usage"] = (env or {}).get("usage")
        c["permission_denials"] = len((env or {}).get("permission_denials") or [])
        for k in ("wall_min", "rollout", "relative_path_refusals", "hook_blocks", "failed_commands", "commands",
                  "turns", "errors"):
            if k in meta:
                c[k] = meta[k]
    out = os.path.join(X10, "results_x10.json")
    json.dump({"mapping": mapping, "cells": res["cells"]}, open(out, "w", encoding="utf-8"), indent=1,
              ensure_ascii=False, default=str)
    for c in sorted(res["cells"], key=lambda x: (x["task"], x["arm"], x["rep"])):
        print("CELL %s %-22s r%s blind %s score %s partial %s min %s wall %s usd %s refusals %d rel %s note %s" % (
            c["task"], c["arm"], c["rep"], c["blind"], c["score"], c["partial"], c["minutes"], c.get("wall_min"),
            c["usd"], len(c["refusals"]), c.get("relative_path_refusals"), (c.get("note") or "")[:200]), flush=True)
    result_line("PASS", len(res["cells"]), 0, None, [{"path": score.rel(out), "md5": matbench.md5(out)},
                                                    {"path": score.rel(mp), "md5": matbench.md5(mp)}])
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["claude", "score"])
    ap.add_argument("--tasks", default="T1,T2,T3,T5,T6")
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--max-min", type=float, default=20.0)
    ap.add_argument("--seed", type=int, default=None)
    a = ap.parse_args(argv)
    if a.what == "claude":
        return run_claude(a.tasks.split(","), a.reps, a.max_min)
    return blind_score(a.seed)


if __name__ == "__main__":
    sys.exit(main())
