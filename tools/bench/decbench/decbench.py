r"""decbench - DECISION BENCH: steering / troubleshooting / peer review on known-answer past cases (card chat-B1).

    py tools/bgrun.py --material --max-min N --log tools/bench/decbench/<x>.log -- py -u tools/bench/decbench/decbench.py
        --lock                                   pin rubric md5s + leak-check every case (worktree made and removed)
        --stub hit|miss|ratelimit [--cases ..]   dry run, claude replaced by stub_dec.py
        --cases S1-pool-overload --reps 1        smoke / full run (real cells)   [--par 10] [--guard-usd X]

PREDICTION CONTRACT: one git worktree per CASE at its base commit under %TEMP%\db\<case> (shared by every arm-run of
that case: cells are read-only, dec_guard refuses every write outside the cell's own scratch dir), `copy` files put in
from their later commit, hooks re-pointed at the worktree with dec_guard.py first. Worktree add/remove/prune run
behind ONE lock (git index races); cells run concurrently through a semaphore of --par (default 10, user 2026-09-29).
Arms: H / XH / MX = claude-opus-5-5 high / xhigh / max, FL = claude-fable-5-1 low, PAR = 3 claude-opus-5-5/high lens
cells then 1 synthesiser that must refute before merging (cost = sum). A cell dying on a rate-limit / overload error is
INVALID and its arm-run is re-queued from the start (<= 3 attempts, never partial). Cell cap --cap-min (30). Every cell:
`claude.exe -p --model M --effort E --output-format json --permission-mode acceptEdits --strict-mcp-config
--disallowedTools Agent Task WebSearch WebFetch`, prompt on stdin, env CYCLE_SESSION=1 BENCH_CELL=1 PEER_GUARD_OFF=1.
LabVIEW pids read before and after; a new pid fails the run. Scoring dec_score.py (mechanical + one blind scorer cell per
case). Ends with a RESULT line.

WHAT EXISTED FIRST: matbench (worktree-at-base, put/git/git_bytes/md5/labview_pids/remove_wt - imported, not copied),
cell_guard.py (wrapped by dec_guard.py), score.envelope (json envelope parse). Nothing measured judgement-level work.
"""
import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time

POSIX = os.name != "nt"                  # cloud port 2026-10-02: Linux runs need TEMP set before matbench/cell_guard read it
if POSIX:
    os.environ.setdefault("TEMP", tempfile.gettempdir())

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "matbench"))
sys.path.insert(0, HERE)
import matbench as MB  # noqa: E402
import score as MS  # noqa: E402
import dec_score as DS  # noqa: E402

MAIN = MB.MAIN
if POSIX:                                # no tasklist / LabVIEW on Linux
    MB.labview_pids = lambda: []
CLAUDE = "claude" if POSIX else "claude.exe"
TMP = os.environ.get("TEMP", r"C:\Windows\Temp")
WTROOT, SCRATCH = os.path.join(TMP, "db"), os.path.join(TMP, "db", "scratch")
OPUS, FABLE, SONNET = "claude-opus-5-5", "claude-fable-5-1", "claude-sonnet-5-5"
ARMS = {"H": (OPUS, "high"), "XH": (OPUS, "xhigh"), "MX": (OPUS, "max"), "FL": (FABLE, "low"), "PAR": (OPUS, "high"),
        "SH": (SONNET, "high"), "SMX": (SONNET, "max")}
LENSES = ["LENS: attack CORRECTNESS - is every step of the obvious reading actually true in the files?",
          "LENS: look for an ALTERNATIVE CAUSE or alternative next act that fits the same evidence better.",
          "LENS: ask WHAT WOULD FALSIFY each candidate answer, and check the files for that observation."]
SYNTH = ("\n\nThree independent analysts answered this same question (below). Before merging, try to REFUTE each of "
         "their main claims against the files; keep only what survives. Then give YOUR final answer in the required "
         "format.\n\n%s")
RL_RE = re.compile(r"rate.?limit|overloaded|\b429\b|\b529\b|usage limit|too many requests", re.I)
WT_LOCK, PRINT_LOCK = threading.Lock(), threading.Lock()
SEM = None


def say(*a):
    with PRINT_LOCK:
        print(*a, flush=True)


def rubric_md5(case):
    return hashlib.md5(json.dumps(case["rubric"], sort_keys=True, ensure_ascii=True).encode()).hexdigest()


def load():
    d = json.load(open(os.path.join(HERE, "cases.json"), encoding="utf-8"))
    return d, {c["id"]: c for c in d["cases"]}


def question(doc, case):
    t = doc["templates"]
    return t["preamble"] + t[case["category"]].format(**case["fields"])


def prepare(case):
    wt = os.path.join(WTROOT, case["id"])
    with WT_LOCK:
        if os.path.exists(wt):
            MB.git("worktree", "remove", "--force", wt, check=False)
            shutil.rmtree(wt, ignore_errors=True)
        MB.git("worktree", "prune")
        MB.git("worktree", "add", "--detach", wt, case["base"])
    copied = []
    for c in case.get("copy", []):
        data = MB.git_bytes(c["from"], c["path"])
        if data is None:
            raise RuntimeError("copy %s:%s missing" % (c["from"], c["path"]))
        if c.get("lines"):
            a, b = c["lines"]
            data = b"".join(data.splitlines(True)[a - 1:b])
        MB.put(wt, c["path"], data, copied, "git:" + c["from"])
    sp = os.path.join(wt, ".claude", "settings.json")
    txt = open(sp, encoding="utf-8").read()
    wf = wt.replace("\\", "/")
    txt = txt.replace(MAIN.replace("\\", "/"), wf).replace(json.dumps(MAIN)[1:-1], json.dumps(wt)[1:-1])
    s = json.loads(txt)
    os.makedirs(os.path.join(wt, ".decbench"), exist_ok=True)
    for f in (os.path.join(os.path.dirname(HERE), "matbench", "cell_guard.py"), os.path.join(HERE, "dec_guard.py")):
        shutil.copy2(f, os.path.join(wt, ".decbench", os.path.basename(f)))
    s.setdefault("hooks", {}).setdefault("PreToolUse", []).insert(0, {"matcher": "*", "hooks": [
        {"type": "command", "command": '%s "%s/.decbench/dec_guard.py"' % (sys.executable if POSIX else "py", wf),
         "timeout": 15}]})
    with open(sp, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)
    return wt, copied


def remove_wt(wt):
    with WT_LOCK:
        MB.remove_wt(wt)


def leak_check(wt, case):
    pats = [re.compile(p, re.I) for p in case.get("leak", [])]
    hits = ["ABSENT-VIOLATED " + p for p in case.get("absent", []) if os.path.exists(os.path.join(wt, p))]
    for root, dirs, files in os.walk(wt):
        dirs[:] = [d for d in dirs if d not in (".git", ".decbench")]
        for fn in files:
            p = os.path.join(root, fn)
            try:
                if os.path.getsize(p) > 8_000_000:
                    continue
                with open(p, "rb") as f:
                    raw = f.read()
            except OSError:
                continue
            if b"\0" in raw[:4096]:
                continue
            txt = raw.decode("utf-8", "replace")
            for rx in pats:
                m = rx.search(txt)
                if m:
                    hits.append("%s: %r" % (os.path.relpath(p, wt).replace("\\", "/"), m.group(0)[:60]))
    return hits


def run_cell(wt, rundir, name, model, effort, prompt, stub, cap_min, attempt):
    cd = os.path.join(rundir, name)
    os.makedirs(cd, exist_ok=True)
    scr = os.path.join(SCRATCH, "%s_%s_%d" % (os.path.basename(rundir), name, attempt))
    os.makedirs(scr, exist_ok=True)
    cmd = ([sys.executable, os.path.join(HERE, "stub_dec.py"), "--fixture", stub] if stub else
           [CLAUDE, "-p", "--model", model, "--effort", effort, "--output-format", "json",
            "--permission-mode", "acceptEdits", "--strict-mcp-config", "--disallowedTools",
            "Agent", "Task", "WebSearch", "WebFetch"])
    env = os.environ.copy()
    env.pop("MATERIAL", None)
    env.update({"CYCLE_SESSION": "1", "BENCH_CELL": "1", "PEER_GUARD_OFF": "1", "CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS": "0",
                "MATBENCH_WT": wt, "MATBENCH_LOG": os.path.join(cd, "calls.jsonl"), "DECBENCH_SCRATCH": scr,
                "DECBENCH_ATTEMPT": str(attempt)})
    log = os.path.join(cd, "cell.log")
    with SEM:
        t0 = time.time()
        with open(log, "wb") as out:
            out.write(("BGRUN START %s decbench cell %s %s/%s attempt %d\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), name,
                                                                          model, effort, attempt)).encode())
            out.flush()
            p = subprocess.Popen(cmd, cwd=wt, env=env, stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT,
                                 start_new_session=POSIX)
            p.stdin.write(prompt.encode("utf-8"))
            p.stdin.close()
            try:
                rc, tag = p.wait(timeout=cap_min * 60), "END"
            except subprocess.TimeoutExpired:
                if POSIX:
                    os.killpg(p.pid, signal.SIGKILL)
                else:
                    subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
                rc, tag = p.wait(), "TIMEOUT"
        mins = (time.time() - t0) / 60.0
    with open(log, "ab") as out:
        out.write(("\nBGRUN %s rc=%s after %ds\n" % (tag, rc, mins * 60)).encode())
    text = MS.rd(log)
    env_j = MS.envelope(text) or {}
    ncalls = sum(1 for _ in open(os.path.join(cd, "calls.jsonl"), encoding="utf-8")) \
        if os.path.isfile(os.path.join(cd, "calls.jsonl")) else 0
    invalid = bool(env_j.get("is_error") and RL_RE.search(str(env_j.get("result", "")))) or \
        (not env_j and bool(RL_RE.search(text)))
    return {"name": name, "model": model, "effort": effort, "rc": rc, "timeout": tag == "TIMEOUT",
            "minutes": round(mins, 2), "usd": float(env_j.get("total_cost_usd") or 0.0), "turns": env_j.get("num_turns"),
            "tools": ncalls, "answer": env_j.get("result") or "", "invalid_ratelimit": invalid,
            "models_used": sorted((env_j.get("modelUsage") or {}).keys())}


def run_arm(doc, case, wt, arm, rep, runs, stub, cap_min):
    rundir = os.path.join(runs, case["id"], "%s_r%d" % (arm, rep))
    model, effort = ARMS[arm]
    q = question(doc, case)
    for attempt in (1, 2, 3):
        shutil.rmtree(rundir, ignore_errors=True)
        os.makedirs(rundir)
        t0 = time.time()
        if arm != "PAR":
            cells = [run_cell(wt, rundir, "c0", model, effort, q, stub, cap_min, attempt)]
            final = cells[0]
        else:
            with cf.ThreadPoolExecutor(3) as ex:
                futs = [ex.submit(run_cell, wt, rundir, "lens%d" % i, model, effort, q + "\n\n" + LENSES[i], stub,
                                  cap_min, attempt) for i in range(3)]
                cells = [f.result() for f in futs]
            if not any(c["invalid_ratelimit"] for c in cells):
                ans = "\n\n".join("=== ANALYST %d ===\n%s" % (i + 1, c["answer"].strip()[:9000]) for i, c in enumerate(cells))
                final = run_cell(wt, rundir, "synth", model, effort, q + SYNTH % ans, stub, cap_min, attempt)
                cells.append(final)
        if any(c["invalid_ratelimit"] for c in cells):
            say("INVALID %s %s r%d attempt %d: rate-limit/overload - requeued from the start" % (case["id"], arm, rep,
                                                                                               attempt))
            json.dump({"attempt": attempt, "cells": cells}, open(rundir + "_invalid_a%d.json" % attempt, "w",
                                                                  encoding="utf-8"), indent=1)
            time.sleep(0 if stub else 60)
            continue
        final = cells[-1]
        rec = {"case": case["id"], "arm": arm, "rep": rep, "model": model, "effort": effort, "attempt": attempt,
               "usd": round(sum(c["usd"] for c in cells), 4), "minutes": round((time.time() - t0) / 60.0, 2),
               "cell_minutes": round(sum(c["minutes"] for c in cells), 2),
               "turns": sum(c["turns"] or 0 for c in cells), "tools": sum(c["tools"] for c in cells),
               "timeout": any(c["timeout"] for c in cells), "cells": [{k: v for k, v in c.items() if k != "answer"}
                                                                     for c in cells],
               "answer": final["answer"], "mech": DS.mechanical(final["answer"], case["rubric"])}
        with open(os.path.join(rundir, "answer.md"), "w", encoding="utf-8") as f:
            f.write(final["answer"])
        json.dump(rec, open(os.path.join(rundir, "meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        say("ARM END %s %s r%d usd %.2f min %.1f mech %s" % (case["id"], arm, rep, rec["usd"], rec["minutes"],
                                                             DS.combine(rec["mech"], case["rubric"])))
        return rec
    return {"case": case["id"], "arm": arm, "rep": rep, "invalid": True, "usd": 0.0}


def blind(doc, case, recs, runs, stub, cap_min):
    answers = {"%s_r%d" % (r["arm"], r["rep"]): r["answer"] for r in recs if not r.get("invalid")}
    if not answers:
        return
    prompt, labels = DS.blind_prompt(case, question(doc, case), answers, seed=rubric_md5(case))
    sd = os.path.join(WTROOT, "scorer_" + case["id"])
    os.makedirs(sd, exist_ok=True)
    rundir = os.path.join(runs, case["id"])
    usd = 0.0
    for attempt in (1, 2, 3):                  # chat-B2: an unparsable / rate-limited scorer cell is re-run whole
        c = run_cell(sd, rundir, "blind_scorer", OPUS, "high", prompt, stub and "scorer", cap_min, attempt)
        usd += c["usd"]
        json.dump({"labels": labels, "attempt": attempt, "cell": {k: v for k, v in c.items() if k != "answer"},
                   "raw": c["answer"]}, open(os.path.join(rundir, "blind.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        got = DS.parse_blind(c["answer"], labels, case["rubric"])
        if got and not c["invalid_ratelimit"] and all(got.get(k) for k in labels.values()):
            break
        say("BLIND %s attempt %d unusable (ratelimit %s, parsed %d/%d)" % (case["id"], attempt, c["invalid_ratelimit"],
                                                                        sum(1 for k in labels.values() if got.get(k)),
                                                                        len(labels)))
        time.sleep(0 if stub else 60)
    c["usd"] = usd
    for r in recs:
        r["blind"] = got.get("%s_r%d" % (r["arm"], r.get("rep", 0)), {})
    shutil.rmtree(sd, ignore_errors=True)
    return c["usd"]


def main(argv=None):
    global SEM
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default="")
    ap.add_argument("--arms", default="H,XH,MX,FL,PAR")
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--par", type=int, default=10, help="concurrent claude cells (user 2026-09-29: default 10)")
    ap.add_argument("--cap-min", type=float, default=30.0)
    ap.add_argument("--stub", default="")
    ap.add_argument("--lock", action="store_true")
    ap.add_argument("--no-blind", action="store_true")
    ap.add_argument("--guard-usd", type=float, default=600.0)
    ap.add_argument("--runs", default=os.path.join(HERE, "runs"))
    ap.add_argument("--tag", default="run")
    ap.add_argument("--report-v1", default="", help="also write the chat-B2 report (report_v1.py) to this path")
    a = ap.parse_args(argv)
    SEM = threading.Semaphore(a.par)
    doc, cases = load()
    ids = [x for x in a.cases.split(",") if x] or list(cases)
    os.makedirs(WTROOT, exist_ok=True)
    lock_p = os.path.join(HERE, "cases_lock.json")
    lv0, gates, fails = MB.labview_pids(), 0, []
    if a.lock:
        try:                                   # --cases X re-locks X and keeps the other entries
            lock = json.load(open(lock_p, encoding="utf-8"))
        except (OSError, ValueError):
            lock = {"schema": "decbench-lock/1", "cases": {}}
        lock["made"] = time.strftime("%Y-%m-%d %H:%M:%S")
        lock["cases"] = {k: v for k, v in lock["cases"].items() if k in cases}
        for cid in ids:
            c = cases[cid]
            wt, copied = prepare(c)
            hits = leak_check(wt, c)
            lock["cases"][cid] = {"base": MB.git("rev-parse", c["base"]).strip(), "rubric_md5": rubric_md5(c),
                                  "copied": copied, "leak": "PASS" if not hits else "LEAKED", "leak_hits": hits}
            remove_wt(wt)
            say("LOCK %s base %s rubric %s leak %s %s" % (cid, c["base"], rubric_md5(c)[:8], "PASS" if not hits else
                                                         "LEAKED", hits[:3]))
            gates += 1
            if hits:
                fails.append("%s leaked" % cid)
        json.dump(lock, open(lock_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        art = lock_p
    else:
        lock = json.load(open(lock_p, encoding="utf-8"))["cases"]
        bad = [c for c in ids if lock.get(c, {}).get("rubric_md5") != rubric_md5(cases[c]) or lock[c]["leak"] != "PASS"]
        if bad:
            say("REFUSED: rubric md5 changed or leak not PASS: %s" % bad)
            print("RESULT " + json.dumps({"schema": "result-line/1", "status": "FAIL", "gates": {"pass": 0, "fail": 1},
                                          "first_fail": "unlocked cases %s" % bad, "artefacts": []}), flush=True)
            return 1
        runs = os.path.join(a.runs, a.tag)
        os.makedirs(runs, exist_ok=True)
        jobs = [(cid, arm, r) for cid in ids for arm in a.arms.split(",") for r in range(1, a.reps + 1)]
        left = {cid: sum(1 for j in jobs if j[0] == cid) for cid in ids}
        wts, recs, spent = {}, [], [0.0]
        wlock = threading.Lock()

        def job(cid, arm, rep):
            with wlock:
                if cid not in wts:
                    wts[cid] = prepare(cases[cid])[0]
                wt = wts[cid]
            if spent[0] > a.guard_usd:
                say("COST GUARD %.2f > %.2f: skip %s %s r%d" % (spent[0], a.guard_usd, cid, arm, rep))
                rec = {"case": cid, "arm": arm, "rep": rep, "invalid": True, "skipped": True, "usd": 0.0}
            else:
                rec = run_arm(doc, cases[cid], wt, arm, rep, runs, a.stub, a.cap_min)
            with wlock:
                spent[0] += rec.get("usd") or 0.0
                left[cid] -= 1
                if left[cid] == 0:
                    remove_wt(wts.pop(cid))
            return rec
        with cf.ThreadPoolExecutor(a.par) as ex:
            recs = [f.result() for f in [ex.submit(job, *j) for j in jobs]]
        blind_usd = 0.0
        if not a.no_blind:                     # one scorer cell per case, concurrently (chat-B2; SEM still caps cells)
            with cf.ThreadPoolExecutor(max(1, min(a.par, len(ids)))) as ex:
                bfs = [ex.submit(blind, doc, cases[cid], [r for r in recs if r["case"] == cid], runs, a.stub, a.cap_min)
                       for cid in ids]
                blind_usd += sum((f.result() or 0) for f in bfs)
        per_arm = DS.aggregate(recs, cases)
        dis = DS.disagreements(recs)
        res = {"schema": "decbench-results/1", "tag": a.tag, "par": a.par, "stub": a.stub or None, "cases": ids,
               "per_arm": per_arm, "blind_usd": round(blind_usd, 3), "spent_usd": round(spent[0] + blind_usd, 3),
               "disagreements": dis, "records": recs}
        art = os.path.join(HERE, "results_%s.json" % a.tag)
        json.dump(res, open(art, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        DS.write_report(os.path.join(HERE, "report_%s.md" % a.tag), per_arm, recs, dis,
                        "tag %s, par %d, stub %s, spent $%.2f (blind $%.2f)" % (a.tag, a.par, a.stub or "no",
                                                                               res["spent_usd"], blind_usd))
        gates = len(recs)
        fails += ["%s %s r%s invalid" % (r["case"], r["arm"], r["rep"]) for r in recs if r.get("invalid")]
        if a.report_v1:                        # card chat-B2: the full-run report in the same process
            import report_v1 as RV
            try:
                if RV.main(["--tag", a.tag, "--out", a.report_v1, "--embedded"]):
                    fails.append("report_v1 gates failed (see REPORT_V1 line)")
            except Exception as e:             # noqa: BLE001  (results json is already on disk)
                fails.append("report_v1 %s: %s" % (type(e).__name__, e))
    leftwt = [w for w in MB.git("worktree", "list").splitlines() if os.path.normcase(WTROOT) in os.path.normcase(w)
              or WTROOT.replace("\\", "/").lower() in w.lower()]
    new = sorted(set(MB.labview_pids()) - set(lv0))
    fails += (["new LabVIEW pid %s" % new] if new else []) + (["worktrees left %s" % leftwt] if leftwt else [])
    say("WORKTREES LEFT %d; LABVIEW NEW %s" % (len(leftwt), new))
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "FAIL" if fails else "PASS",
                                  "gates": {"pass": gates - len(fails), "fail": len(fails)},
                                  "first_fail": fails[0] if fails else None,
                                  "artefacts": [{"path": MS.rel(art), "md5": MB.md5(art)}]}), flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
