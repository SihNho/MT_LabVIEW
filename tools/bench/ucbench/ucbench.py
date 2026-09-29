r"""ucbench - ULTRACODE bench: one Workflow-orchestrating session vs single sessions on LARGE known-answer-set tasks
(card chat-B3; user 2026-09-29 "이걸 벤치해보자. 사실 이게 핵심이거든").

    py tools/bgrun.py --material --max-min N --log tools/bench/ucbench/<x>.log -- py -u tools/bench/ucbench/ucbench.py
        --probe                                  2-agent Workflow in a claude -p cell with the guard (leak probes)
        --lock                                   leak-check every task at its base, pin key md5s -> tasks_lock.json
        --stub [--tasks ..]                      dry run: cells replaced by stub_uc.py, scorer by its stub
        --tasks L1 --arms SMX,SH,UC --reps 1     smoke / full run (real cells)  [--par 6] [--cap-min 60] [--guard-usd X]

PREDICTION CONTRACT: one git worktree per TASK at its base commit under %TEMP%\ucb\<task> (decbench.prepare, imported,
WTROOT re-pointed), hooks re-pointed with uc_guard.py first (= decbench dec_guard + Workflow allowed ONLY when the arm
sets UCBENCH_ALLOW_WORKFLOW=1, no worktree isolation). Arms: SMX = claude-opus-5-5/max, SH = claude-opus-5-5/high,
UC = claude-opus-5-5/high whose prompt starts with the `ultracode` keyword and whose cell may call Workflow (the
sub-agents inherit the model/effort unless the script overrides). Every cell: `claude.exe -p --model M --effort E
--output-format stream-json --verbose --permission-mode acceptEdits --strict-mcp-config --disallowedTools Agent Task
WebSearch WebFetch` (+ `--allowedTools Workflow` for UC), prompt on stdin, env CYCLE_SESSION=1 BENCH_CELL=1
PEER_GUARD_OFF=1. A rate-limit/overload death is INVALID and re-run from the start (<= 3). Scoring uc_score.py: per
answer, claims parsed, mechanical key match + one blind claude-opus-5-5/high scorer cell in the task worktree (tools
read-only, arm hidden, agent/workflow wording stripped) -> recall, precision, false claims. LabVIEW pids before/after:
a new pid fails the run. Ends with a RESULT line.

WHAT EXISTED FIRST: decbench (prepare / leak_check / remove_wt / RL_RE - imported), matbench (git, git_bytes, md5,
labview_pids, score.envelope), cell_guard + dec_guard (wrapped by uc_guard). New here: stream-json accounting of
Workflow calls and sub-agents, the set-valued (recall/precision) scorer, the probe.
"""
import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(BENCH, "matbench"), os.path.join(BENCH, "decbench"), HERE]
import matbench as MB  # noqa: E402
import score as MS  # noqa: E402
import decbench as DB  # noqa: E402
import uc_score as US  # noqa: E402

MAIN = MB.MAIN
TMP = os.environ.get("TEMP", r"C:\Windows\Temp")
DB.WTROOT = os.path.join(TMP, "ucb")
SCRATCH = os.path.join(TMP, "ucb", "scratch")
OPUS = "claude-opus-5-5"
# UC = the CLI's own ultracode mode: `--effort ultracode` ("xhigh + dynamic workflow orchestration", claude 2.1.281
# binary string; measured 2026-09-29: a -p cell at that effort reports the "Ultracode is on" system message, while the
# bare prompt keyword did NOT turn it on - probe_V1_keyword.json)
# SXH (card chat-B4, chat decision 2): single session at xhigh = UC's own main-loop effort, isolates orchestration
ARMS = {"SMX": (OPUS, "max", False), "SH": (OPUS, "high", False), "SXH": (OPUS, "xhigh", False),
        "UC": (OPUS, "ultracode", True)}
UC_KEY = "ultracode"
# decbench's rate-limit regex + the CLI's plan-limit wording (a limit death is INVALID, re-run from the start)
RL2 = re.compile(DB.RL_RE.pattern + r"|hit your \w*\s*limit|limit reached|session limit|weekly limit", re.I)
PRINT_LOCK = threading.Lock()
SEM = threading.Semaphore(6)


def say(*a):
    with PRINT_LOCK:
        print(*a, flush=True)


def prepare(task):
    """decbench.prepare (worktree at base + copies + dec_guard first), then swap dec_guard for uc_guard."""
    wt, copied = DB.prepare(task)
    for f in ("uc_guard.py",):
        shutil.copy2(os.path.join(HERE, f), os.path.join(wt, ".decbench", f))
    sp = os.path.join(wt, ".claude", "settings.json")
    txt = open(sp, encoding="utf-8").read().replace("/.decbench/dec_guard.py", "/.decbench/uc_guard.py")
    with open(sp, "w", encoding="utf-8") as f:
        f.write(txt)
    import glob as _g
    for rd in task.get("redact", []):                  # answer-bearing LINES in files whose EXISTENCE is part of the key
        rx, n = re.compile(rd["re"]), 0
        for root in rd["roots"]:
            for dp, dns, fns in os.walk(os.path.join(wt, root)):
                for fn in fns:
                    p = os.path.join(dp, fn)
                    try:
                        if os.path.getsize(p) > 8_000_000:
                            continue
                        raw = open(p, "rb").read()
                    except OSError:
                        continue
                    if b"\0" in raw[:4096]:
                        continue
                    lines = raw.decode("utf-8", "replace").splitlines(True)
                    new = ["[line redacted by ucbench]\n" if rx.search(ln) else ln for ln in lines]
                    if new != lines:
                        with open(p, "w", encoding="utf-8", newline="") as f:
                            f.write("".join(new))
                        n += 1
                        copied.append({"path": os.path.relpath(p, wt).replace("\\", "/"), "from": "redacted",
                                       "md5": ""})
    for rel in task.get("blank", []):                  # answer-computing tools whose EXISTENCE is part of the key
        p = os.path.join(wt, rel.replace("/", os.sep))
        if os.path.isfile(p):
            with open(p, "w", encoding="utf-8") as f:
                f.write("# emptied by the benchmark harness (ucbench): this tool would compute the answer directly\n")
            copied.append({"path": rel, "from": "blanked", "md5": ""})
    for pat in task.get("remove", []):                 # files that must not be at base (answer-bearing tools/outputs)
        for p in sorted(_g.glob(os.path.join(wt, pat.replace("/", os.sep)))):
            if os.path.isfile(p):
                os.remove(p)
                copied.append({"path": os.path.relpath(p, wt).replace("\\", "/"), "from": "removed", "md5": ""})
    return wt, copied


def parse_stream(text):
    """stream-json -> (result envelope, init tools, top-level tool_use counts, workflow errors)."""
    env, tools, uses, errs = {}, [], {}, []
    for ln in text.splitlines():
        if not ln.startswith("{"):
            continue
        try:
            e = json.loads(ln)
        except ValueError:
            continue
        t = e.get("type")
        if t == "system" and e.get("subtype") == "init":
            tools = e.get("tools") or []
        elif t == "result":
            env = e
        elif t == "assistant" and not e.get("parent_tool_use_id"):
            for c in (e.get("message") or {}).get("content") or []:
                if c.get("type") == "tool_use":
                    uses[c.get("name")] = uses.get(c.get("name"), 0) + 1
        elif t == "user":
            for c in (e.get("message") or {}).get("content") or []:
                if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("is_error"):
                    s = json.dumps(c.get("content"))[:300]
                    if "orkflow" in s or "No such tool" in s:
                        errs.append(s)
    return env, tools, uses, errs


def calls_summary(path):
    rows = []
    if os.path.isfile(path):
        for ln in open(path, encoding="utf-8"):
            try:
                rows.append(json.loads(ln))
            except ValueError:
                pass
    subs = sorted({r.get("agent_id") for r in rows if r.get("agent_id")})
    return rows, {"calls": len(rows), "sub_agents": len(subs), "sub_calls": sum(1 for r in rows if r.get("agent_id")),
                  "refused": sum(1 for r in rows if r.get("decision") == "REFUSE"),
                  "workflow_calls": sum(1 for r in rows if r.get("tool") == "Workflow")}


def run_cell(wt, rundir, name, arm, prompt, stub, cap_min, attempt, allow_workflow=None, extra_args=()):
    model, effort, uc = ARMS[arm]
    uc = uc if allow_workflow is None else allow_workflow
    cd = os.path.join(rundir, name)
    os.makedirs(cd, exist_ok=True)
    scr = os.path.join(SCRATCH, "%s_%s_%s_%d" % (os.path.basename(os.path.dirname(rundir)), os.path.basename(rundir),
                                                 name, attempt))
    os.makedirs(scr, exist_ok=True)
    if stub:
        cmd = [sys.executable, os.path.join(HERE, "stub_uc.py"), "--fixture", stub]
    else:
        cmd = ["claude.exe", "-p", "--model", model, "--effort", effort, "--output-format", "stream-json", "--verbose",
               "--permission-mode", "acceptEdits", "--strict-mcp-config", "--disallowedTools", "Agent", "Task",
               "WebSearch", "WebFetch"] + (["--allowedTools", "Workflow"] if uc else []) + list(extra_args)
    env = os.environ.copy()
    env.pop("MATERIAL", None)
    env.update({"CYCLE_SESSION": "1", "BENCH_CELL": "1", "PEER_GUARD_OFF": "1", "CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS": "0",
                "MATBENCH_WT": wt, "MATBENCH_LOG": os.path.join(cd, "calls.jsonl"), "DECBENCH_SCRATCH": scr,
                "DECBENCH_ATTEMPT": str(attempt), "UCBENCH_ALLOW_WORKFLOW": "1" if uc else "0"})
    log = os.path.join(cd, "cell.log")
    with SEM:
        t0 = time.time()
        with open(log, "wb") as out:
            p = subprocess.Popen(cmd, cwd=wt, env=env, stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT)
            p.stdin.write(prompt.encode("utf-8"))
            p.stdin.close()
            try:
                rc, tag = p.wait(timeout=cap_min * 60), "END"
            except subprocess.TimeoutExpired:
                subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
                rc, tag = p.wait(), "TIMEOUT"
        mins = (time.time() - t0) / 60.0
    with open(log, "ab") as out:
        out.write(("\nBGRUN %s rc=%s after %ds\n" % (tag, rc, mins * 60)).encode())
    text = MS.rd(log)
    env_j, tools, uses, wf_errs = parse_stream(text)
    if not env_j:
        env_j = MS.envelope(text) or {}
    _, cs = calls_summary(os.path.join(cd, "calls.jsonl"))
    mu = env_j.get("modelUsage") or {}
    tok = {k: sum(int(v.get(k) or 0) for v in mu.values()) for k in ("inputTokens", "outputTokens",
                                                                      "cacheReadInputTokens", "cacheCreationInputTokens")}
    invalid = bool(env_j.get("is_error") and RL2.search(str(env_j.get("result", "")))) or \
        (not env_j and bool(RL2.search(text)))
    return {"name": name, "arm": arm, "model": model, "effort": effort, "uc": uc, "rc": rc, "timeout": tag == "TIMEOUT",
            "minutes": round(mins, 2), "usd": float(env_j.get("total_cost_usd") or 0.0), "turns": env_j.get("num_turns"),
            "answer": env_j.get("result") or "", "invalid_ratelimit": invalid, "workflow_in_tools": "Workflow" in tools,
            "top_tool_uses": uses, "workflow_errors": wf_errs[:3], "calls": cs, "tokens": tok,
            "models_used": sorted(mu.keys())}


# ------------------------------------------------------------------------------------------------------------ probe
PROBE_PROMPT = """This is a harness probe, not a real task. Use the Workflow tool with an INLINE script (no worktree isolation) that runs
exactly TWO agents in parallel and returns both of their final texts:
  agent 1 prompt: "Use the Glob tool to list three files under tools/hooks/ in the current working directory. Return
                   only their relative paths, one per line."
  agent 2 prompt: "Do these three things and report, for each, either ALLOWED plus what you saw, or the exact refusal
                   text you received: (a) Read the file %s ; (b) run the Bash command: git log -1 --oneline ;
                   (c) use the Write tool to write the text PROBE to %s"
After the workflow returns, answer with: (1) whether a system reminder in this session told you ultracode is on (yes/no,
quote it if yes); (2) the Workflow runId; (3) both agents' returns verbatim. If the Workflow tool is not available or
fails, say exactly what error you got and stop - do NOT do the agents' work yourself."""


def probe(a):
    base = a.probe_base
    canary = os.path.join(HERE, "canary_main.txt")
    wprobe = os.path.join(HERE, "probe_write_by_cell.txt")
    if os.path.exists(wprobe):
        os.remove(wprobe)
    task = {"id": "probe", "base": base, "copy": []}
    runs = os.path.join(HERE, "runs", a.tag)
    wt, _ = prepare(task)
    say("PROBE worktree %s at %s" % (wt, base))
    out, gates, fails = [], 0, []
    variants = [("V2_effort_ultracode", ()), ]      # V1 (prompt keyword, effort high): probe_V1_keyword.json
    try:
        for vname, extra in variants:
            rundir = os.path.join(runs, "probe", vname)
            shutil.rmtree(rundir, ignore_errors=True)
            os.makedirs(rundir)
            c = run_cell(wt, rundir, "c0", "UC", PROBE_PROMPT % (canary, wprobe), a.stub, 15, 1, extra_args=extra)
            rows, cs = calls_summary(os.path.join(rundir, "c0", "calls.jsonl"))
            full = MS.rd(os.path.join(rundir, "c0", "cell.log"))
            sub_rows = [r for r in rows if r.get("agent_id")]
            chk = {
                "workflow_in_init_tools": c["workflow_in_tools"],
                "workflow_tool_used": c["top_tool_uses"].get("Workflow", 0) > 0,
                "sub_agent_calls_hooked": cs["sub_calls"] > 0,
                "canary_read_refused": any(r["decision"] == "REFUSE" and "canary_main" in (r.get("cmd") or "")
                                           for r in sub_rows),
                "git_refused": any(r["decision"] == "REFUSE" and re.search(r"\bgit\b", r.get("cmd") or "")
                                   for r in sub_rows),
                "main_write_refused": any(r["decision"] == "REFUSE" and "probe_write_by_cell" in (r.get("cmd") or "")
                                          for r in sub_rows),
                "canary_token_absent": "UCBENCH-CANARY-7f3a91" not in full,
                "main_write_absent": not os.path.exists(wprobe),
            }
            rec = {"variant": vname, "cell": {k: v for k, v in c.items() if k != "answer"}, "checks": chk,
                   "answer": c["answer"], "sub_rows": sub_rows[:40]}
            out.append(rec)
            json.dump(rec, open(os.path.join(rundir, "probe.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            say("PROBE %s usd %.3f min %.1f checks %s" % (vname, c["usd"], c["minutes"], json.dumps(chk)))
            say("PROBE %s answer: %s" % (vname, c["answer"][:1500].replace("\n", " | ")))
            gates += len(chk)
            fails += ["%s %s" % (vname, k) for k, v in chk.items() if not v]
            if chk["workflow_tool_used"]:
                break
    finally:
        DB.remove_wt(wt)
    art = os.path.join(HERE, "probe_%s.json" % a.tag)
    json.dump(out, open(art, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return art, gates, fails


# ------------------------------------------------------------------------------------------------------------ tasks
def load_tasks():
    d = json.load(open(os.path.join(HERE, "tasks.json"), encoding="utf-8"))
    return d, {t["id"]: t for t in d["tasks"]}


def key_md5(t):
    return hashlib.md5(json.dumps(t["key"], sort_keys=True, ensure_ascii=True).encode()).hexdigest()


def question(doc, t, uc):
    return doc["preamble"] + "\n\n" + t["question"] + "\n\n" + doc["answer_format"]   # identical for every arm


def lock(a, doc, tasks, ids):
    lock_p = os.path.join(HERE, "tasks_lock.json")
    try:
        lk = json.load(open(lock_p, encoding="utf-8"))
    except (OSError, ValueError):
        lk = {"schema": "ucbench-lock/1", "tasks": {}}
    lk["made"] = time.strftime("%Y-%m-%d %H:%M:%S")
    fails = []
    for tid in ids:
        t = tasks[tid]
        wt, copied = prepare(t)
        hits = DB.leak_check(wt, {"leak": t.get("leak", []), "absent": t.get("absent", [])})
        present = [p for p in t.get("present", []) if not os.path.exists(os.path.join(wt, p))]
        kre = US.key_regex_selfcheck(t)          # every key item's regexes compile and hit its own reference text
        size = sum(1 for _ in _files(wt))
        lk["tasks"][tid] = {"base": MB.git("rev-parse", t["base"]).strip(), "key_md5": key_md5(t), "key_n": len(t["key"]),
                            "copied": copied, "leak": "PASS" if not hits else "LEAKED", "leak_hits": hits[:20],
                            "present_missing": present, "key_selfcheck": kre, "files_at_base": size}
        DB.remove_wt(wt)
        ok = not hits and not present and not kre
        say("LOCK %s base %s key %d md5 %s leak %s missing %s keycheck %s files %d" % (
            tid, t["base"], len(t["key"]), key_md5(t)[:8], "PASS" if not hits else "LEAKED", present, kre, size))
        if not ok:
            fails.append("%s lock: leak %s missing %s keycheck %s" % (tid, hits[:2], present, kre[:2]))
    json.dump(lk, open(lock_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return lock_p, len(ids), fails


def _files(wt):
    for root, dirs, files in os.walk(wt):
        dirs[:] = [d for d in dirs if d not in (".git", ".decbench")]
        for f in files:
            yield os.path.join(root, f)


def run_arm(doc, t, wt, arm, rep, runs, stub, cap_min):
    rundir = os.path.join(runs, t["id"], "%s_r%d" % (arm, rep))
    q = question(doc, t, ARMS[arm][2])
    for attempt in (1, 2, 3):
        shutil.rmtree(rundir, ignore_errors=True)
        os.makedirs(rundir)
        c = run_cell(wt, rundir, "c0", arm, q, stub and ("uc" if ARMS[arm][2] else "single"), cap_min, attempt)
        if c["invalid_ratelimit"]:
            say("INVALID %s %s r%d attempt %d: rate-limit/overload - requeued from the start" % (t["id"], arm, rep, attempt))
            json.dump(c, open(rundir + "_invalid_a%d.json" % attempt, "w", encoding="utf-8"), indent=1)
            time.sleep(0 if stub else 60)
            continue
        rec = {"task": t["id"], "arm": arm, "rep": rep, "attempt": attempt,
               **{k: v for k, v in c.items() if k not in ("answer", "name")}, "answer": c["answer"]}
        with open(os.path.join(rundir, "answer.md"), "w", encoding="utf-8") as f:
            f.write(c["answer"])
        say("ARM END %s %s r%d usd %.2f min %.1f workflow %s subagents %d" % (
            t["id"], arm, rep, c["usd"], c["minutes"], c["top_tool_uses"].get("Workflow", 0), c["calls"]["sub_agents"]))
        return rec
    return {"task": t["id"], "arm": arm, "rep": rep, "invalid": True, "usd": 0.0}


def score_all(doc, tasks, recs, runs, stub, cap_min, par):
    """one blind scorer cell per answer (arm hidden), in a fresh worktree of the task's base."""
    by_task = {}
    for r in recs:
        if not r.get("invalid"):
            by_task.setdefault(r["task"], []).append(r)
    usd = [0.0]
    lk = threading.Lock()

    def one(tid, r, wt):
        t = tasks[tid]
        label = hashlib.md5(("%s%s%s" % (tid, r["arm"], r["rep"])).encode()).hexdigest()[:6]
        claims = US.parse_claims(r["answer"])
        prompt = US.blind_prompt(t, question(doc, t, False), US.strip_arm(r["answer"]), claims, label)
        rundir = os.path.join(runs, tid, "score_%s" % label)
        got = None
        for attempt in (1, 2, 3):
            shutil.rmtree(rundir, ignore_errors=True)
            os.makedirs(rundir)
            c = run_cell(wt, rundir, "scorer", "SH", prompt, stub and "scorer", cap_min, attempt, allow_workflow=False)
            with lk:
                usd[0] += c["usd"]
            got = US.parse_blind(c["answer"], t, claims)
            json.dump({"label": label, "attempt": attempt, "raw": c["answer"], "parsed": got}, open(
                os.path.join(rundir, "blind.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            if got and not c["invalid_ratelimit"]:
                break
            say("SCORER %s %s attempt %d unusable" % (tid, label, attempt))
            time.sleep(0 if stub else 30)
        r["claims_n"] = len(claims)
        r["mech"] = US.mechanical(r["answer"], t)
        r["blind"] = got or {}
        r["score"] = US.metrics(t, claims, r["mech"], got or {})
        r["counts"] = US.count_score(r["answer"], t)
        r["scorer_label"] = label
    for tid, rs in by_task.items():
        wt, _ = prepare(tasks[tid])
        try:
            with cf.ThreadPoolExecutor(max(1, min(par, len(rs)))) as ex:
                for f in [ex.submit(one, tid, r, wt) for r in rs]:
                    f.result()
        finally:
            DB.remove_wt(wt)
    return usd[0]


def main(argv=None):
    global SEM
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--probe-base", default="HEAD~150")
    ap.add_argument("--lock", action="store_true")
    ap.add_argument("--tasks", default="")
    ap.add_argument("--arms", default="SMX,SH,SXH,UC")
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--par", type=int, default=6)
    ap.add_argument("--cap-min", type=float, default=60.0)
    ap.add_argument("--stub", default="")
    ap.add_argument("--no-score", action="store_true")
    ap.add_argument("--guard-usd", type=float, default=400.0)
    ap.add_argument("--tag", default="run")
    a = ap.parse_args(argv)
    SEM = threading.Semaphore(a.par)
    os.makedirs(DB.WTROOT, exist_ok=True)
    lv0, gates, fails = MB.labview_pids(), 0, []
    if a.probe:
        art, gates, fails = probe(a)
    elif a.lock:
        doc, tasks = load_tasks()
        ids = [x for x in a.tasks.split(",") if x] or list(tasks)
        art, gates, fails = lock(a, doc, tasks, ids)
    else:
        doc, tasks = load_tasks()
        ids = [x for x in a.tasks.split(",") if x] or list(tasks)
        lk = json.load(open(os.path.join(HERE, "tasks_lock.json"), encoding="utf-8"))["tasks"]
        bad = [i for i in ids if lk.get(i, {}).get("key_md5") != key_md5(tasks[i]) or lk[i]["leak"] != "PASS"]
        if bad:
            say("REFUSED: key md5 changed or leak not PASS: %s" % bad)
            print("RESULT " + json.dumps({"schema": "result-line/1", "status": "FAIL", "gates": {"pass": 0, "fail": 1},
                                          "first_fail": "unlocked tasks %s" % bad, "artefacts": []}), flush=True)
            return 1
        runs = os.path.join(HERE, "runs", a.tag)
        os.makedirs(runs, exist_ok=True)
        jobs = [(tid, arm, r) for tid in ids for arm in a.arms.split(",") for r in range(1, a.reps + 1)]
        left = {tid: sum(1 for j in jobs if j[0] == tid) for tid in ids}
        wts, spent, wlock = {}, [0.0], threading.Lock()

        def job(tid, arm, rep):
            with wlock:
                if tid not in wts:
                    wts[tid] = prepare(tasks[tid])[0]
                wt = wts[tid]
            if spent[0] > a.guard_usd:
                say("COST GUARD %.2f > %.2f: skip %s %s r%d" % (spent[0], a.guard_usd, tid, arm, rep))
                rec = {"task": tid, "arm": arm, "rep": rep, "invalid": True, "skipped": True, "usd": 0.0}
            else:
                rec = run_arm(doc, tasks[tid], wt, arm, rep, runs, a.stub, a.cap_min)
            with wlock:
                spent[0] += rec.get("usd") or 0.0
                left[tid] -= 1
                if left[tid] == 0:
                    DB.remove_wt(wts.pop(tid))
            return rec
        with cf.ThreadPoolExecutor(a.par) as ex:
            recs = [f.result() for f in [ex.submit(job, *j) for j in jobs]]
        score_usd = 0.0 if a.no_score else score_all(doc, tasks, recs, runs, a.stub, a.cap_min, a.par)
        per_arm = US.aggregate(recs)
        res = {"schema": "ucbench-results/1", "tag": a.tag, "par": a.par, "stub": a.stub or None, "tasks": ids,
               "per_arm": per_arm, "score_usd": round(score_usd, 3), "spent_usd": round(spent[0] + score_usd, 3),
               "records": recs}
        art = os.path.join(HERE, "results_%s.json" % a.tag)
        json.dump(res, open(art, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        US.write_report(os.path.join(HERE, "report_%s.md" % a.tag), per_arm, recs,
                        "tag %s, par %d, stub %s, spent $%.2f (scorer $%.2f)" % (a.tag, a.par, a.stub or "no",
                                                                                res["spent_usd"], score_usd))
        gates = len(recs)
        fails += ["%s %s r%s invalid" % (r["task"], r["arm"], r["rep"]) for r in recs if r.get("invalid")]
        fails += ["%s %s r%s unscored" % (r["task"], r["arm"], r["rep"]) for r in recs
                  if not r.get("invalid") and not a.no_score and not r.get("blind")]
        if a.stub:
            fails += US.stub_expectations(recs)
    leftwt = [w for w in MB.git("worktree", "list").splitlines() if DB.WTROOT.replace("\\", "/").lower() in
              w.replace("\\", "/").lower()]
    new = sorted(set(MB.labview_pids()) - set(lv0))
    fails += (["new LabVIEW pid %s" % new] if new else []) + (["worktrees left %s" % leftwt] if leftwt else [])
    say("WORKTREES LEFT %d; LABVIEW NEW %s" % (len(leftwt), new))
    for f in fails[:10]:
        say("FAIL " + f)
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "FAIL" if fails else "PASS",
                                  "gates": {"pass": gates - len(fails), "fail": len(fails)},
                                  "first_fail": fails[0] if fails else None,
                                  "artefacts": [{"path": MS.rel(art), "md5": MB.md5(art)}]}), flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
