r"""matbench - MATERIAL-MODEL REPLAY BENCH (card chat-N2, brief tools/bench/cards/brief_chat-N2.md items 1, 2, 5, 8).

    MATERIAL=1 py tools/bgrun.py --max-min 240 --log tools/bench/matbench/matbench_v0.log -- \
        py -u tools/bench/matbench/matbench.py [--tasks T1,T2] [--conds 0,1,2]
    py tools/bench/matbench/matbench.py --dry-stub hit,miss,workaround --tasks T1      (selftest; claude stubbed)

PREDICTION CONTRACT: for each task x condition one git worktree at the task's BASE commit (the parent of the commit
that added the card) under %TEMP%\mb\<task>_<cond> (the scratchpad path is too long for this repo's longest file
names: `git worktree add` there failed "Filename too long"); the replay card + the inputs that were committed WITH the
card (or are gitignored, from disk with md5) copied in; the worktree's .claude/settings.json re-pointed at the
worktree (so the cell's hooks see the WORKTREE's tools/) plus tools/bench/matbench/cell_guard.py as the first
PreToolUse hook (labview none etc., every call logged). One `claude.exe -p --agent <a> --model <m> --effort <e>
--output-format json --permission-mode acceptEdits "CARD <card>"` per cell (cycle_runner.py:142 shape), env
CYCLE_SESSION=1 BENCH_CELL=1 PEER_GUARD_OFF=1 (guard_peer.py:58 - benchmark cells), under bgrun with --max-min =
truth max_minutes + 5. The three conditions of ONE task run in parallel (<= 3). LabVIEW.exe PIDs are read before and
after each batch; a NEW pid fails the batch gate. Run artefacts -> tools/bench/matbench/runs/<task>_<cond>/, then the
worktree is removed and pruned. Scoring is score.py (no model judges). Ends with a RESULT line.

WHAT EXISTED FIRST: cycle_runner.py session_cmd/result_json (spawn shape + envelope parse, copied not imported:
importing cycle_runner pulls its whole runner), bgrun.py (process deadline), protocol.py validate_obj (score.py).
No replay bench existed (tools/bench/matbench/ held only truth_v0.json).
"""
import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WTROOT = os.path.join(os.environ.get("TEMP", r"C:\Windows\Temp"), "mb")
RUNS = os.path.join(HERE, "runs")
TRUTH = os.path.join(HERE, "truth_v0.json")
sys.path.insert(0, HERE)
import score  # noqa: E402

# base = parent of the commit that ADDED the card; src = that commit (inputs committed with the card come from it)
TASKS = {
    "T1": dict(card="mb-T1", agent="material", base="ece33fb", src="d71798d", extra=[]),
    "T2": dict(card="mb-T2", agent="material", base="d71798d", src="5887e24", extra=[]),
    "T3": dict(card="mb-T3", agent="material", base="1892a09", src="e18924c", extra=["disk:tools/bench/sim/l2a1/step_*.json"]),
    # T4: the gate RELEASES the card's `why` names (prior-art FIXED, outcome review run, steer followed) were committed
    # WITH the card, so the base alone refuses the pre-run (first v0 batch: 3/3 BLOCKED on stop_record / OUTCOMES due /
    # recipe md5 7fb6223f != card 1098a443). The answer file (archive/peer/2026-09-26-hyp-l2a1-p2-86-5.md) is NOT copied.
    "T4": dict(card="mb-T4", agent="material", base="728214c", src="33ea0b3", extra=[
        "disk:tools/bench/sim/l2a1/step_*.json",
        "git:archive/peer/2026-09-25-priorart-c86-l2a1-checkpoints.md",
        "git:tools/bench/cards/review_priorart-c86-l2a1-checkpoints.json",
        "git:tools/bench/cards/verdict_priorart-c86-l2a1-checkpoints.json",
        "git:archive/peer/2026-09-25-outcome-review-20260925.md",
        "git:tools/bench/cards/verdict_outcome-review-20260925.json",
        "git:tools/bench/cards/steer_86.json", "git:tools/bench/stop_records.json",
        "git:tools/bench/outcome_review_86.log", "git:tools/bench/priorart_86_checkpoints.log"]),
    "T5": dict(card="mb-T5", agent="material", base="effdef6", src="53a5fb2", extra=[]),
    "T6": dict(card="mb-T6", agent="log-reader", base="d71798d", src="5887e24", extra=[]),
}
K_REF = "tools/bench/stageplan_k_split.json"          # T5 reference plan (md5 c3892b15), simulated in each worktree
K_GRAPH = "tools/bench/graph_k_s4_20260925.json"


def md5(p):
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def git(*a, cwd=MAIN, check=True):
    r = subprocess.run(["git", "-c", "core.longpaths=true"] + list(a), cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if check and r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a), r.stderr.strip()[:300]))
    return r.stdout


def git_bytes(commit, path):
    r = subprocess.run(["git", "show", "%s:%s" % (commit, path)], cwd=MAIN, capture_output=True)
    return r.stdout if r.returncode == 0 else None


def labview_pids():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq LabVIEW.exe", "/FO", "CSV", "/NH"], capture_output=True,
                         text=True, errors="replace").stdout
    return sorted(int(m.group(1)) for m in re.finditer(r'"LabVIEW\.exe","(\d+)"', out))


def put(wt, rel, data, copied, how):
    dst = os.path.join(wt, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "wb") as f:
        f.write(data)
    copied.append({"path": rel, "from": how, "md5": hashlib.md5(data).hexdigest()})


def prepare(tid, cond_i, cond):
    t = TASKS[tid]
    wt = os.path.join(WTROOT, "%s_c%d" % (tid, cond_i))
    if os.path.exists(wt):
        git("worktree", "remove", "--force", wt, check=False)
        shutil.rmtree(wt, ignore_errors=True)
    git("worktree", "prune")
    git("worktree", "add", "--detach", wt, t["base"])
    copied = []
    card_p = os.path.join(HERE, "cards", "task_%s.json" % t["card"])
    with open(card_p, "rb") as f:
        put(wt, "tools/bench/cards/task_%s.json" % t["card"], f.read(), copied, "matbench/cards")
    card = json.load(open(card_p, encoding="utf-8"))
    for inp in card.get("inputs", []):
        rel = inp["path"].replace("\\", "/")
        if re.match(r"^[A-Za-z]:", rel):
            continue                                          # outside the repo
        here = os.path.join(wt, rel)
        if os.path.exists(here) and (not inp.get("md5") or md5(here) == inp["md5"]):
            continue                                          # already at base (and the card's md5, if it names one)
        local = os.path.join(HERE, "cards", os.path.basename(rel))
        if os.path.isfile(local):
            put(wt, rel, open(local, "rb").read(), copied, "matbench/cards")
            continue
        data = git_bytes(t["src"], rel)
        if data is not None:
            put(wt, rel, data, copied, "git:" + t["src"])
    if tid == "T5":
        for rel in (K_GRAPH, "tools/bench/graph_loops_k_s4_20260925.json"):
            if not os.path.exists(os.path.join(wt, rel)):
                put(wt, rel, git_bytes(t["src"], rel), copied, "git:" + t["src"])
    for ex in t["extra"]:
        kind, pat = ex.split(":", 1)
        if kind == "git":
            put(wt, pat, git_bytes(t["src"], pat), copied, "git:" + t["src"])
            continue
        for p in sorted(glob.glob(os.path.join(MAIN, pat))):
            rel = os.path.relpath(p, MAIN).replace("\\", "/")
            if not os.path.exists(os.path.join(wt, rel)):
                put(wt, rel, open(p, "rb").read(), copied, "disk")
    # hooks: re-point the project's hooks at the worktree, put cell_guard first
    sp = os.path.join(wt, ".claude", "settings.json")
    txt = open(sp, encoding="utf-8").read()
    mf, wf = MAIN.replace("\\", "/"), wt.replace("\\", "/")
    txt = txt.replace(mf, wf).replace(json.dumps(MAIN)[1:-1], json.dumps(wt)[1:-1])
    s = json.loads(txt)
    os.makedirs(os.path.join(wt, ".matbench"), exist_ok=True)
    shutil.copy2(os.path.join(HERE, "cell_guard.py"), os.path.join(wt, ".matbench", "cell_guard.py"))
    s.setdefault("hooks", {}).setdefault("PreToolUse", []).insert(0, {"matcher": "*", "hooks": [
        {"type": "command", "command": 'py "%s/.matbench/cell_guard.py"' % wf, "timeout": 15}]})
    with open(sp, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)
    left = [ln.strip()[:120] for ln in txt.splitlines() if "V6_ParallelLoop" in ln]   # hooks still on MAIN
    return wt, card, copied, left


def cell_cmd(t, cond, card, stub=None):
    prompt = "CARD tools/bench/cards/task_%s.json" % card["id"]
    if stub:
        return [sys.executable, os.path.join(HERE, "stub_claude.py"), "--card-id", card["id"], "--fixture", stub]
    return ["claude.exe", "-p", "--agent", t["agent"], "--model", cond["model"], "--effort", cond["effort"],
            "--output-format", "json", "--permission-mode", "acceptEdits", prompt]


def post(tid, ci, wt, card, rundir):
    """Copy what score.py reads out of the worktree; T5: simulate the produced plan and the reference there."""
    rp = os.path.join(wt, "tools", "bench", "cards", "result_%s.json" % card["id"])
    if os.path.isfile(rp):
        shutil.copy2(rp, os.path.join(rundir, "result_card.json"))
    cp = os.path.join(wt, ".matbench", "calls.jsonl")
    if os.path.isfile(cp):
        shutil.copy2(cp, os.path.join(rundir, "calls.jsonl"))
    if tid != "T5":
        return
    sims = {}
    produced = os.path.join(wt, "tools", "bench", "matbench_out", "stageplan_k_split.json")
    ref = os.path.join(wt, ".matbench", "ref_stageplan_k_split.json")
    shutil.copy2(os.path.join(MAIN, K_REF.replace("/", os.sep)), ref)
    for name, plan in (("ref", ref), ("out", produced)):
        if not os.path.isfile(plan):
            sims[name] = {"exists": False}
            continue
        od = os.path.join(wt, ".matbench", "sim_" + name)
        r = subprocess.run([sys.executable, "tools/stagesim.py", "simulate", plan, K_GRAPH, "--out-root", od,
                            "--plan-out", od], cwd=wt, capture_output=True, text=True, errors="replace", timeout=600)
        fin = None
        for p in glob.glob(os.path.join(od, "plan_*.json")):
            try:
                fin = json.load(open(p, encoding="utf-8"))
            except ValueError:
                pass
        f2 = (fin or {}).get("finalized") or {}
        sims[name] = {"exists": True, "md5": md5(plan), "rc": r.returncode, "final": (fin or {}).get("final"),
                      "failed": f2.get("failed"), "end_cdiff_rows": f2.get("end_cdiff_rows"),
                      "tail": r.stdout.strip().splitlines()[-2:] if r.stdout else r.stderr[-300:]}
        if plan == produced:
            shutil.copy2(plan, os.path.join(rundir, "stageplan_k_split_out.json"))
    json.dump(sims, open(os.path.join(rundir, "t5_sim.json"), "w", encoding="utf-8"), indent=1)


def remove_wt(wt):
    git("worktree", "remove", "--force", wt, check=False)
    shutil.rmtree(wt, ignore_errors=True)
    git("worktree", "prune", check=False)


def run_task(tid, conds, truth, stubs, max_min_override, runs_root):
    t, tt = TASKS[tid], next(x for x in truth["tasks"] if x["id"].startswith(tid + "_"))
    max_min = max_min_override or (tt["expect"]["max_minutes"] + 5)
    lv0 = labview_pids()
    procs = []
    for ci in conds:
        cond = truth["conditions"][ci]
        rundir = os.path.join(runs_root, "%s_c%d" % (tid, ci))
        shutil.rmtree(rundir, ignore_errors=True)
        os.makedirs(rundir)
        wt, card, copied, left = prepare(tid, ci, cond)
        log = os.path.join(rundir, "cell.log")
        # the WORKTREE's bgrun: bgrun.py:207 runs its child with cwd=<its own project root>, so MAIN's would put
        # the cell in the main checkout (measured in the first selftest: the stub wrote into MAIN)
        cmd = [sys.executable, os.path.join(wt, "tools", "bgrun.py"), "--max-min", str(max_min), "--log", log,
               "--"] + cell_cmd(t, cond, card, stubs[ci] if stubs else None)
        env = os.environ.copy()
        env.update({"CYCLE_SESSION": "1", "BENCH_CELL": "1", "PEER_GUARD_OFF": "1",
                    "CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS": "0"})
        env.pop("MATERIAL", None)
        meta = {"task": tid, "cond": ci, "condition": cond, "agent": t["agent"], "base": t["base"], "src": t["src"],
                "worktree": wt, "card": card["id"], "copied": copied, "settings_unrepointed": left,
                "max_min": max_min, "cmd": cmd[7:], "start": time.strftime("%Y-%m-%d %H:%M:%S"), "stub": bool(stubs)}
        print("CELL START %s c%d %s/%s wt=%s copied=%d" % (tid, ci, cond["model"], cond["effort"], wt, len(copied)),
              flush=True)
        procs.append((subprocess.Popen(cmd, cwd=wt, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL),
                      meta, rundir, wt, card, time.time()))
    for p, meta, rundir, wt, card, t0 in procs:
        p.wait()
        meta["wall_min"] = round((time.time() - t0) / 60.0, 2)
        meta["end"] = time.strftime("%Y-%m-%d %H:%M:%S")
        post(tid, meta["cond"], wt, card, rundir)
        json.dump(meta, open(os.path.join(rundir, "meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        remove_wt(wt)
        print("CELL END %s c%d wall %.1f min" % (tid, meta["cond"], meta["wall_min"]), flush=True)
    lv1 = labview_pids()
    new = sorted(set(lv1) - set(lv0))
    print("LABVIEW %s before %s after %s new %s" % (tid, lv0, lv1, new), flush=True)
    return {"task": tid, "labview_before": lv0, "labview_after": lv1, "labview_new": new}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default="T1,T2,T3,T4,T5,T6")
    ap.add_argument("--conds", default="0,1,2")
    ap.add_argument("--dry-stub", default="", help="comma list of stub fixtures per condition (selftest)")
    ap.add_argument("--max-min", type=float, default=0.0, help="override the per-cell deadline (selftest)")
    ap.add_argument("--runs", default=RUNS)
    ap.add_argument("--out", default=HERE, help="where results_v0.json / report_v0.md go")
    a = ap.parse_args(argv)
    truth = json.load(open(TRUTH, encoding="utf-8"))
    conds = [int(x) for x in a.conds.split(",")]
    stubs = a.dry_stub.split(",") if a.dry_stub else None
    if stubs:
        stubs = {ci: stubs[i] for i, ci in enumerate(conds)}
    os.makedirs(WTROOT, exist_ok=True)
    batches = [run_task(tid, conds, truth, stubs, a.max_min, a.runs) for tid in a.tasks.split(",")]
    rj = os.path.join(a.out, "results_v0.json")
    try:                                   # batches of earlier invocations (other tasks) are kept
        old = [b for b in json.load(open(rj, encoding="utf-8")).get("batches", [])
               if b["task"] not in {x["task"] for x in batches}]
    except (OSError, ValueError):
        old = []
    res = score.score_all(a.runs, truth, old + batches)
    json.dump(res, open(rj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    score.write_report(res, os.path.join(a.out, "report_v0.md"))
    left = [w for w in git("worktree", "list").splitlines() if WTROOT.replace("\\", "/").lower() in w.lower()
            or os.path.normcase(WTROOT) in os.path.normcase(w)]
    lv_new = sorted({p for b in batches for p in b["labview_new"]})
    timeouts = sum(1 for c in res["cells"] if c["timeout"])
    ok = not lv_new and not left
    print("CELLS %d timeouts %d" % (len(res["cells"]), timeouts), flush=True)
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if ok else "FAIL",
                                   "gates": {"pass": len(res["cells"]), "fail": (1 if lv_new else 0) + (1 if left else 0)},
                                   "first_fail": None if ok else ("new LabVIEW pid %s" % lv_new if lv_new else
                                                                  "worktrees left %s" % left),
                                   "artefacts": [{"path": score.rel(rj), "md5": md5(rj)}]}), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
