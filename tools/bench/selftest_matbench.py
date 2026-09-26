"""selftest_matbench - dry mode of the material-model replay bench (card chat-N2, brief item 7). No model, no LabVIEW.

    MATERIAL=1 py tools/bgrun.py --max-min 10 --log tools/bench/selftest_matbench.log -- py -u tools/bench/selftest_matbench.py

PREDICTION CONTRACT (6/0): the REAL pipeline (worktree at T1's base, card + inputs copied, hooks re-pointed, bgrun,
post, prune, score) runs T1 x 3 conditions with claude replaced by stub_claude.py and fixed fake result cards:
  G1 hit -> score 1          G2 miss -> score 0, note names the missed "9 of 11" group
  G3 workaround -> 0, flagged "workaround"       G4 timeout (stub sleeps 90 s, deadline 0.2 min) -> 0, flagged, BGRUN TIMEOUT
  G5 no matbench worktree left (git worktree list) and every cell's worktree dir removed
  G6 no new LabVIEW.exe pid across the batches; cell_guard refuses `py -c "import gscript"` and allows a grep naming it
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MB = os.path.join(HERE, "matbench")
sys.path.insert(0, MB)
import matbench  # noqa: E402

gates = []


def gate(name, ok, detail=""):
    gates.append((name, bool(ok)))
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", name, detail), flush=True)


def main():
    tmp = tempfile.mkdtemp(prefix="mbself_")
    runs, out = os.path.join(tmp, "runs"), tmp
    rc1 = matbench.main(["--tasks", "T1", "--dry-stub", "hit,miss,workaround", "--runs", runs, "--out", out])
    res1 = json.load(open(os.path.join(out, "results_v0.json"), encoding="utf-8"))
    cells = {c["cond"]: c for c in res1["cells"]}
    shutil.copytree(runs, os.path.join(tmp, "runs_a"))
    rc2 = matbench.main(["--tasks", "T1", "--conds", "0", "--dry-stub", "timeout", "--max-min", "0.2",
                         "--runs", runs, "--out", out])
    res2 = json.load(open(os.path.join(out, "results_v0.json"), encoding="utf-8"))
    tc = res2["cells"][0]
    print("rc %s %s" % (rc1, rc2))
    gate("G1 hit scores 1", cells[0]["score"] == 1 and cells[0]["partial"] == 1.0, cells[0].get("note"))
    gate("G2 miss scores 0 and names the missed group", cells[1]["score"] == 0 and "9 of 11" in cells[1].get("note", ""),
         cells[1].get("note"))
    gate("G3 workaround scores 0, flagged", cells[2]["score"] == 0 and "workaround" in cells[2]["flags"],
         cells[2].get("note"))
    log = open(os.path.join(runs, "T1_c0", "cell.log"), encoding="utf-8", errors="replace").read()
    gate("G4 timeout scores 0, flagged, logged", tc["score"] == 0 and tc["timeout"] and "BGRUN TIMEOUT" in log,
         tc.get("note"))
    wl = subprocess.run(["git", "worktree", "list"], cwd=matbench.MAIN, capture_output=True, text=True).stdout
    left = [ln for ln in wl.splitlines() if "/mb/" in ln.replace("\\", "/").lower()]
    dirs = [d for d in ("T1_c0", "T1_c1", "T1_c2") if os.path.exists(os.path.join(matbench.WTROOT, d))]
    gate("G5 worktrees pruned", not left and not dirs, "left %s dirs %s" % (left, dirs))
    new = [p for b in res1["batches"] + res2["batches"] for p in b["labview_new"]]
    g = os.path.join(MB, "cell_guard.py")

    def guard(cmd):
        pl = json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}})
        env = dict(os.environ, MATBENCH_WT=matbench.MAIN, MATBENCH_LOG=os.path.join(tmp, "guard_calls.jsonl"))
        return subprocess.run([sys.executable, g], input=pl, capture_output=True, text=True, env=env).returncode
    r_imp, r_grep = guard('py -c "import gscript"'), guard("grep -n def tools/gscript.py; wc -l tools/stagekit.py")
    r_rec = guard("MATERIAL=1 py -u tools/recipes/stage_d1_l2a1.py --dry")        # imports stagekit -> refused
    r_pre = guard("py -u tools/stage_prerun.py --prerun tools/recipes/stage_d1_l2a1.py")   # COM-stubbed -> allowed
    gate("G6 no new LabVIEW pid; cell_guard refuses gscript import / recipe run, allows grep / wc / prerun",
         not new and r_imp == 2 and r_grep == 0 and r_rec == 2 and r_pre == 0 and cells[0]["dispatches"] == 1,
         "new %s import %s grep %s recipe %s prerun %s dispatches %s" % (new, r_imp, r_grep, r_rec, r_pre,
                                                                         cells[0]["dispatches"]))
    shutil.rmtree(tmp, ignore_errors=True)
    p = sum(1 for _, ok in gates if ok)
    f = len(gates) - p
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if f == 0 else "FAIL",
                                   "gates": {"pass": p, "fail": f},
                                   "first_fail": next((n for n, ok in gates if not ok), None), "artefacts": []}))
    return 0 if f == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
