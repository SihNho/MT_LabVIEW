"""selftest_matbench - dry mode of the material-model replay bench (cards chat-N2, chat-N3). No model, no LabVIEW.

    py tools/bgrun.py --material --max-min 10 --log tools/bench/selftest_matbench.log -- py -u tools/bench/selftest_matbench.py

PREDICTION CONTRACT (10/0), v1 scorer (truth_v1.json, 4 conditions, repeats 1 here): the REAL pipeline (worktree at
T1's base, card + inputs copied, hooks re-pointed, bgrun, post, prune, score_all_v1) runs T1 x 4 conditions with
claude replaced by stub_claude.py and fixed fake result cards:
  G1 hit -> score 1
  G2 miss (no '9 of 11') -> score 1 but partial < 1: '9 of 11' is PARTIAL-ONLY in v1, and the note names it
  G3 workaround -> 0, flagged "workaround" (rule kept)
  G4 lvrun (hit wording, cost.labview_runs 1) -> 0, the BEHAVIOUR group is the missed one
  G5 timeout (stub sleeps 90 s, deadline 0.2 min) -> 0, flagged, BGRUN TIMEOUT
  G6 no matbench worktree left (git worktree list) and every cell's worktree dir removed
  G7 no new LabVIEW.exe pid across the batches; cell_guard refuses `py -c "import gscript"` / a recipe run,
     allows grep / wc / prerun
  G8 T5 v1 score = t5_struct jaccard: equal -> 1, jaccard 0.4 -> 0.4, no card -> 0
  G9 cost guard: with guard_usd < 0 no cell is launched and the cell is listed as skipped
  G10 T4 mtimes: commit_mtimes(T4 base) puts tools/bench/priorart_cycle14.log (v0's culprit) more than 30 h
      (guard_cycle MAX_AGE_S) before the card commit
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MB = os.path.join(HERE, "matbench")
sys.path.insert(0, MB)
import matbench  # noqa: E402
import score  # noqa: E402

gates = []


def gate(name, ok, detail=""):
    gates.append((name, bool(ok)))
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", name, detail), flush=True)


def fake_t5(tmp, name, struct, card=True):
    d = os.path.join(tmp, "t5", name)
    os.makedirs(d)
    json.dump({"task": "T5", "cond": 0, "rep": 1, "card": "mb-T5", "agent": "material",
               "condition": {"model": "claude-opus-5-5", "effort": "low"}}, open(os.path.join(d, "meta.json"), "w"))
    env = {"type": "result", "is_error": False, "duration_ms": 60000, "total_cost_usd": 0.5, "num_turns": 3,
           "result": ""}
    open(os.path.join(d, "cell.log"), "w").write("BGRUN START x\n" + json.dumps(env) + "\nBGRUN END rc=0 after 60s\n")
    if card:
        json.dump({"schema": "result/1", "id": "mb-T5", "status": "PASS", "gates": {"pass": 1, "fail": 0},
                   "first_fail": None, "blocked_by": None, "artefacts": [], "facts": ["plan written (x:1)"],
                   "open": [], "cost": {"usd": None, "minutes": 1, "labview_runs": 0}, "note": ""},
                  open(os.path.join(d, "result_card.json"), "w"))
    json.dump(struct, open(os.path.join(d, "t5_struct.json"), "w"))
    return d


def main():
    tmp = tempfile.mkdtemp(prefix="mbself_")
    runs, out = os.path.join(tmp, "runs"), tmp
    base = ["--runs", runs, "--out", out, "--reps", "1", "--no-rescore"]
    rc1 = matbench.main(["--tasks", "T1", "--dry-stub", "hit,miss,workaround,lvrun"] + base)
    res1 = json.load(open(os.path.join(out, "results_v1.json"), encoding="utf-8"))
    cells = {c["cond"]: c for c in res1["cells"]}
    shutil.copytree(runs, os.path.join(tmp, "runs_a"))
    shutil.rmtree(runs)
    rc2 = matbench.main(["--tasks", "T1", "--conds", "0", "--dry-stub", "timeout", "--max-min", "0.2"] + base)
    res2 = json.load(open(os.path.join(out, "results_v1.json"), encoding="utf-8"))
    tc = res2["cells"][0]
    print("rc %s %s" % (rc1, rc2))
    gate("G1 hit scores 1", cells[0]["score"] == 1 and cells[0]["partial"] == 1.0, cells[0].get("note"))
    gate("G2 miss of the partial-only '9 of 11' scores 1, partial < 1, named",
         cells[1]["score"] == 1 and cells[1]["partial"] < 1 and "9 of 11" in cells[1].get("note", ""),
         "%s %s" % (cells[1]["partial"], cells[1].get("note")))
    gate("G3 workaround scores 0, flagged", cells[2]["score"] == 0 and "workaround" in cells[2]["flags"],
         cells[2].get("note"))
    gate("G4 labview_runs 1 scores 0 on the behaviour group",
         cells[3]["score"] == 0 and "behaviour" in cells[3].get("note", "") and "workaround" not in cells[3]["flags"],
         cells[3].get("note"))
    log = open(os.path.join(runs, "T1_c0_r1", "cell.log"), encoding="utf-8", errors="replace").read()
    gate("G5 timeout scores 0, flagged, logged", tc["score"] == 0 and tc["timeout"] and "BGRUN TIMEOUT" in log,
         tc.get("note"))
    wl = subprocess.run(["git", "worktree", "list"], cwd=matbench.MAIN, capture_output=True, text=True).stdout
    left = [ln for ln in wl.splitlines() if "/mb/" in ln.replace("\\", "/").lower()]
    dirs = [d for d in ("T1_c0_r1", "T1_c1_r1", "T1_c2_r1", "T1_c3_r1")
            if os.path.exists(os.path.join(matbench.WTROOT, d))]
    gate("G6 worktrees pruned", not left and not dirs, "left %s dirs %s" % (left, dirs))
    new = [p for b in res1["batches"] + res2["batches"] for p in b["labview_new"]]
    g = os.path.join(MB, "cell_guard.py")

    def guard(cmd):
        pl = json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}})
        env = dict(os.environ, MATBENCH_WT=matbench.MAIN, MATBENCH_LOG=os.path.join(tmp, "guard_calls.jsonl"))
        return subprocess.run([sys.executable, g], input=pl, capture_output=True, text=True, env=env).returncode
    r_imp, r_grep = guard('py -c "import gscript"'), guard("grep -n def tools/gscript.py; wc -l tools/stagekit.py")
    r_rec = guard("MATERIAL=1 py -u tools/recipes/stage_d1_l2a1.py --dry")        # imports stagekit -> refused
    r_pre = guard("py -u tools/stage_prerun.py --prerun tools/recipes/stage_d1_l2a1.py")   # COM-stubbed -> allowed
    gate("G7 no new LabVIEW pid; cell_guard refuses gscript import / recipe run, allows grep / wc / prerun",
         not new and r_imp == 2 and r_grep == 0 and r_rec == 2 and r_pre == 0 and cells[0]["dispatches"] == 1,
         "new %s import %s grep %s recipe %s prerun %s dispatches %s" % (new, r_imp, r_grep, r_rec, r_pre,
                                                                         cells[0]["dispatches"]))
    truth = json.load(open(matbench.TRUTH, encoding="utf-8"))
    t5 = next(x for x in truth["tasks"] if x["id"].startswith("T5"))
    s_eq = score.score_cell_v1(fake_t5(tmp, "eq", {"equal": True, "jaccard": 1.0}), t5)["score"]
    s_j = score.score_cell_v1(fake_t5(tmp, "j4", {"equal": False, "jaccard": 0.4}), t5)["score"]
    s_nc = score.score_cell_v1(fake_t5(tmp, "nc", {"equal": True, "jaccard": 1.0}, card=False), t5)["score"]
    gate("G8 T5 score = struct jaccard", s_eq == 1 and s_j == 0.4 and s_nc == 0, "eq %s j0.4 %s nocard %s" % (
        s_eq, s_j, s_nc))
    skipped = []
    runs3 = os.path.join(tmp, "runs3")
    os.makedirs(runs3)
    matbench.run_task("T1", [0], truth, {0: "hit"}, 0, runs3, reps=1, par=3, guard_usd=-1.0, skipped=skipped)
    gate("G9 cost guard launches nothing past the limit", skipped == ["T1_c0_r1"] and not os.listdir(runs3),
         "skipped %s dirs %s" % (skipped, os.listdir(runs3)))
    mt = matbench.commit_mtimes(matbench.TASKS["T4"]["base"]).get("tools/bench/priorart_cycle14.log")
    # guard_cycle.py:405 floor = max(retro, now - MAX_AGE_S 30 h): the log must be older than the card commit - 30 h
    st = int(matbench.git("log", "-1", "--format=%ct", matbench.TASKS["T4"]["src"]).strip())
    gate("G10 T4 mtimes from git: priorart_cycle14.log older than the card commit - 30 h (guard_cycle MAX_AGE_S)",
         mt is not None and mt < st - 30 * 3600,
         time.strftime("%Y-%m-%d %H:%M", time.localtime(mt)) if mt else None)
    shutil.rmtree(tmp, ignore_errors=True)
    p = sum(1 for _, ok in gates if ok)
    f = len(gates) - p
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if f == 0 else "FAIL",
                                   "gates": {"pass": p, "fail": f},
                                   "first_fail": next((n for n, ok in gates if not ok), None), "artefacts": []}))
    return 0 if f == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
