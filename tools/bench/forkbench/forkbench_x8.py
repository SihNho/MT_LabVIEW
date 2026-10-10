# ---
# labview: none
# hardware: none
# offline-args: prep
# evidence: tools/bench/cards/brief_chat-X8.md
# ---
"""Card chat-X8: FORK (continued purpose session, --fork-session) vs FRESH judgement session on 3 real hand-backs.

Existing tools checked first: tools/bench/matbench/ (replay bench of material cards, not judgement hand-backs) and
tools/cycle_runner.py (spawns the real hand-back sessions; its prompt = judge_prompt + "HANDBACK <path>", and the exact
text sent is the first user message of the real hand-back transcript, which is what `prep` copies). Nothing here
re-implements either; this file only wires claude -p calls and records.

Subcommands
  prep            find sids, copy each real hand-back prompt, collect ground truth -> forkbench/cases_x8.json
  run [case arm]  run arms (all 6 by default, 3 at a time); raw output -> forkbench/raw_<case>_<arm>.json
  blind           random A/B per case (key -> forkbench/key_x8.json), blind files -> forkbench/blind_<case>.md
  score           one claude -p scorer per case, reads only the blind file text (no tools) -> forkbench/score_<case>.json
  report          forkbench/report_x8.md + RESULT line

Prediction contract
  run: every arm exits rc 0 within 900 s with a JSON result; the purpose transcript md5 and line count are identical
       before and after every FORK call; each fork session id differs from the purpose sid. Any miss = gate FAIL.
  score: one JSON object per case with keys A and B.
"""
import concurrent.futures as cf
import hashlib
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

OUT = os.path.join(ROOT, "tools", "bench", "forkbench")
BENCH = os.path.join(ROOT, "tools", "bench")
TRANS = os.path.join(os.path.expanduser("~"), ".claude", "projects",
                     "G--Codes-LabVIEW-Codes-MinLab-zz-LabView-VI-AAA-UNIST-2--Tracking-V6-ParallelLoop")
MODEL, EFFORT, TIMEOUT_S = "claude-opus-5-5", "high", 900
BENCH_LINE = "\nBENCH: do not write any file; output the next.json you would write as a JSON block\n"
ARM_TOOLS = ["--tools", "Read,Glob,Grep", "--allowedTools", "Read", "Glob", "Grep",
             "--disallowedTools", "Write", "Edit", "Bash", "PowerShell", "Agent", "Task", "NotebookEdit", "Skill",
             "WebFetch", "WebSearch", "--strict-mcp-config"]

# cycle log of the PURPOSE session, the real hand-back log, the real judging time, and the next-round evidence
CASES = [
    {"case": "165_1", "purpose_log": "cycle_165.log", "hb_log": "cycle_165_handback_1.log", "judged": "16:31",
     "next_round": ["cards/handback_165_2.json", "cycle_165_handback_2.log"],
     "next_round_line": "runner_supervisor.log ASSIGN cycle 165 round 2 -> HANDBACK (route check refuses inner faces)"},
    {"case": "165_2", "purpose_log": "cycle_165.log", "hb_log": "cycle_165_handback_2.log", "judged": "16:46",
     "next_round": ["cards/handback_165_3.json"],
     "next_round_line": "runner_supervisor.log ASSIGN cycle 165 round 3 -> HANDBACK, then HANDBACK-LIMIT (cycle closes)"},
    {"case": "164_2", "purpose_log": "cycle_164.log", "hb_log": "cycle_164_handback_2.log", "judged": "14:38",
     "next_round": ["cards/assign_result_164_3.json"],
     "next_round_line": "runner_supervisor.log:551 ASSIGN cycle 164 round 3 end -> PURPOSE_MET, all 17 pass items met"},
]


def md5_file(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def line_count(p):
    with open(p, "rb") as f:
        return sum(1 for _ in f)


def last_json(text):
    """Last line of `text` that parses as a JSON object with a session_id, or None."""
    for line in reversed(text.splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                j = json.loads(line)
            except ValueError:
                continue
            if isinstance(j, dict) and "session_id" in j:
                return j
    return None


def transcript(sid):
    return os.path.join(TRANS, sid + ".jsonl")


def entries(sid):
    with open(transcript(sid), encoding="utf-8") as f:
        for line in f:
            try:
                yield json.loads(line)
            except ValueError:
                continue


def first_user_text(sid):
    for j in entries(sid):
        if j.get("type") == "user":
            c = j["message"]["content"]
            return c if isinstance(c, str) else "".join(x.get("text", "") for x in c if isinstance(x, dict))
    return None


def next_json_writes(sid):
    """Every Write/Edit the real session made to tools/bench/next.json (input dicts, in order)."""
    out = []
    for j in entries(sid):
        if j.get("type") != "assistant":
            continue
        for c in j["message"].get("content", []):
            if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") in ("Write", "Edit"):
                fp = str(c.get("input", {}).get("file_path", "")).replace("\\", "/")
                if fp.endswith("tools/bench/next.json"):
                    out.append({"tool": c["name"], "input": c["input"]})
    return out


def prep():
    os.makedirs(OUT, exist_ok=True)
    cases = []
    for c in CASES:
        psid = last_json(open(os.path.join(BENCH, c["purpose_log"]), encoding="utf-8", errors="replace").read())["session_id"]
        hj = last_json(open(os.path.join(BENCH, c["hb_log"]), encoding="utf-8", errors="replace").read())
        hsid = hj["session_id"]
        prompt = first_user_text(hsid)
        ppath = os.path.join(OUT, "prompt_%s.txt" % c["case"])
        with open(ppath, "w", encoding="utf-8", newline="") as f:
            f.write(prompt)
        writes = next_json_writes(hsid)
        nr = {}
        for p in c["next_round"]:
            txt = open(os.path.join(BENCH, p), encoding="utf-8", errors="replace").read()
            nr[p] = (last_json(txt) or {}).get("result", "")[-3000:] if p.endswith(".log") else txt[:4000]
        truth = {"real_judge_result": hj.get("result", ""), "real_next_json_writes": writes,
                 "real_judge_cost_usd": hj.get("total_cost_usd"), "real_judge_ms": hj.get("duration_ms"),
                 "next_round": nr, "next_round_line": c["next_round_line"]}
        with open(os.path.join(OUT, "truth_%s.json" % c["case"]), "w", encoding="utf-8") as f:
            json.dump(truth, f, indent=1, ensure_ascii=False)
        cases.append(dict(c, purpose_sid=psid, hb_sid=hsid, prompt_md5=hashlib.md5(prompt.encode("utf-8")).hexdigest(),
                          prompt_chars=len(prompt), purpose_md5=md5_file(transcript(psid)),
                          purpose_lines=line_count(transcript(psid)), next_json_writes=len(writes)))
        print("PREP", c["case"], "purpose", psid, "hb", hsid, "prompt", len(prompt), "next.json writes", len(writes))
    with open(os.path.join(OUT, "cases_x8.json"), "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=1)
    print(protocol.result_line({"status": "PASS", "gates": {"pass": len(cases), "fail": 0}, "first_fail": None,
                                "artefacts": [{"path": "tools/bench/forkbench/cases_x8.json",
                                               "md5": md5_file(os.path.join(OUT, "cases_x8.json"))}]}))


def arm_env():
    e = os.environ.copy()
    for k in ("CLAUDECODE", "CYCLE_ROLE", "ASSIGN_STATE", "ASSIGN_RESULT", "PURPOSE_PHASE", "HANDBACK_RECORD"):
        e.pop(k, None)
    e.update({"BENCH_CELL": "1", "CYCLE_SESSION": "1", "CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS": "0"})
    return e


def tool_reads(sid, since_epoch):
    """Paths the arm read/searched after it started (Read file_path, Grep/Glob path) from its own transcript."""
    paths = []
    for j in entries(sid):
        ts = j.get("timestamp")
        if ts:
            try:
                t = time.mktime(time.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S")) - time.timezone
            except ValueError:
                t = since_epoch
            if t < since_epoch - 5:
                continue
        if j.get("type") != "assistant":
            continue
        for c in j["message"].get("content", []):
            if isinstance(c, dict) and c.get("type") == "tool_use":
                inp = c.get("input", {})
                paths.append([c.get("name"), inp.get("file_path") or inp.get("path") or "", inp.get("pattern", "")])
    return paths


def run_one(case, arm):
    cases = {c["case"]: c for c in json.load(open(os.path.join(OUT, "cases_x8.json"), encoding="utf-8"))}
    c = cases[case]
    prompt = open(os.path.join(OUT, "prompt_%s.txt" % case), encoding="utf-8").read() + BENCH_LINE
    cmd = ["claude", "-p", "--model", MODEL, "--effort", EFFORT, "--output-format", "json"] + ARM_TOOLS
    if arm == "fork":
        cmd = ["claude", "-p", "--resume", c["purpose_sid"], "--fork-session", "--model", MODEL, "--effort", EFFORT,
               "--output-format", "json"] + ARM_TOOLS
    pt = transcript(c["purpose_sid"])
    before = (md5_file(pt), line_count(pt))
    t0 = time.time()
    p = subprocess.Popen(cmd, cwd=ROOT, env=arm_env(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=True)
    try:
        out, err = p.communicate(prompt.encode("utf-8"), timeout=TIMEOUT_S)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
        out, err = p.communicate()
        rc = "TIMEOUT"
    secs = round(time.time() - t0, 1)
    after = (md5_file(pt), line_count(pt))
    out_s, err_s = out.decode("utf-8", "replace"), err.decode("utf-8", "replace")
    with open(os.path.join(OUT, "raw_%s_%s.json" % (case, arm)), "w", encoding="utf-8") as f:
        f.write(out_s)
    if err_s.strip():
        with open(os.path.join(OUT, "raw_%s_%s.stderr.txt" % (case, arm)), "w", encoding="utf-8") as f:
            f.write(err_s)
    j = last_json(out_s) or {}
    sid = j.get("session_id")
    u = j.get("usage") or {}
    reads = tool_reads(sid, t0) if sid and os.path.exists(transcript(sid)) else []
    rec = {"case": case, "arm": arm, "rc": rc, "seconds": secs, "session_id": sid, "is_error": j.get("is_error"),
           "cost_usd": j.get("total_cost_usd"), "num_turns": j.get("num_turns"),
           "input_tokens": u.get("input_tokens"), "cache_read": u.get("cache_read_input_tokens"),
           "cache_create": u.get("cache_creation_input_tokens"), "output_tokens": u.get("output_tokens"),
           "purpose_before": before, "purpose_after": after, "purpose_unchanged": before == after,
           "sid_differs": (sid != c["purpose_sid"]) if sid else None, "tool_calls": reads}
    with open(os.path.join(OUT, "rec_%s_%s.json" % (case, arm)), "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    with open(os.path.join(OUT, "answer_%s_%s.md" % (case, arm)), "w", encoding="utf-8") as f:
        f.write(j.get("result", "") or "")
    print("RUN", case, arm, "rc", rc, "s", secs, "sid", sid, "usd", rec["cost_usd"], "unchanged", rec["purpose_unchanged"],
          "tools", len(reads), flush=True)
    return rec


def run(args):
    jobs = [(a[0], a[1])] if (a := args) else [(c["case"], arm) for arm in ("fork", "fresh") for c in CASES]
    recs = []
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        for r in ex.map(lambda x: run_one(*x), jobs):
            recs.append(r)
    fails = [r for r in recs if r["rc"] != 0 or not r["session_id"] or r["is_error"]
             or (r["arm"] == "fork" and (not r["purpose_unchanged"] or not r["sid_differs"]))]
    print(protocol.result_line({"status": "FAIL" if fails else "PASS",
                                "gates": {"pass": len(recs) - len(fails), "fail": len(fails)},
                                "first_fail": ("%s/%s rc %s" % (fails[0]["case"], fails[0]["arm"], fails[0]["rc"]))
                                if fails else None}))


def blind():
    key = {}
    rnd = random.SystemRandom()
    for c in CASES:
        arms = ["fork", "fresh"]
        rnd.shuffle(arms)
        key[c["case"]] = {"A": arms[0], "B": arms[1]}
        truth = json.load(open(os.path.join(OUT, "truth_%s.json" % c["case"]), encoding="utf-8"))
        writes = "\n\n".join(json.dumps(w["input"], ensure_ascii=False)[:6000] for w in truth["real_next_json_writes"])
        nr = "\n\n".join("### %s\n%s" % (k, v) for k, v in truth["next_round"].items())
        parts = ["# Blind case %s" % c["case"],
                 "## GROUND TRUTH 1 - what the real judge decided (its final message)\n" + truth["real_judge_result"],
                 "## GROUND TRUTH 2 - what the real judge wrote to next.json\n" + (writes or "(none captured)"),
                 "## GROUND TRUTH 3 - what the NEXT assignment round then found (" + truth["next_round_line"] + ")\n" + nr]
        for lab in ("A", "B"):
            ans = open(os.path.join(OUT, "answer_%s_%s.md" % (c["case"], key[c["case"]][lab])), encoding="utf-8").read()
            parts.append("## ANSWER %s\n%s" % (lab, ans))
        with open(os.path.join(OUT, "blind_%s.md" % c["case"]), "w", encoding="utf-8") as f:
            f.write("\n\n".join(parts))
    with open(os.path.join(OUT, "key_x8.json"), "w", encoding="utf-8") as f:
        json.dump(key, f, indent=1)
    print("BLIND written; key in key_x8.json (scorer never sees it)")


SCORER = """You score two answers (A and B) to the same judgement task blind, against ground truth. Output ONLY one JSON
object, no prose: {"A": {"decision_match": "yes|partial|no", "mistake_avoided": "yes|partial|no|n/a",
"evidence": 0|1|2, "why": "<=200 chars"}, "B": {...same...}}.
- decision_match: does the answer's next.json/plan reach the same decision as GROUND TRUTH 1/2 (same next act, same
  scope split, same order)? partial = same direction, different scope or order.
- mistake_avoided: GROUND TRUTH 3 says what the next round then hit. yes = the answer's plan foresees and prevents that
  failure (names the cause or adds the check that would catch it before the launch); partial = mentions the risk without
  a preventing step; no = would hit it too; n/a = the next round succeeded (then judge: would the answer's plan also
  have succeeded? put that in why and use yes/no for whether it keeps the parts that made it succeed).
- evidence: 0 = no file:line citations; 1 = some; 2 = its key claims are each tied to a file:line.
Do not reward length. The two answers are in random order.

"""


def score():
    tmp = tempfile.mkdtemp(prefix="forkbench_scorer_")
    for c in CASES:
        body = open(os.path.join(OUT, "blind_%s.md" % c["case"]), encoding="utf-8").read()
        cmd = ["claude", "-p", "--model", MODEL, "--effort", EFFORT, "--output-format", "json", "--safe-mode",
               "--tools", "", "--strict-mcp-config"]
        t0 = time.time()
        p = subprocess.run(cmd, cwd=tmp, env=arm_env(), input=(SCORER + body).encode("utf-8"), capture_output=True,
                           timeout=TIMEOUT_S, shell=True)
        j = last_json(p.stdout.decode("utf-8", "replace")) or {}
        res = j.get("result", "")
        m = re.search(r"\{.*\}", res, re.S)
        try:
            sc = json.loads(m.group(0)) if m else None
        except ValueError:
            sc = None
        rec = {"case": c["case"], "score": sc, "raw": res, "cost_usd": j.get("total_cost_usd"),
               "seconds": round(time.time() - t0, 1), "rc": p.returncode}
        with open(os.path.join(OUT, "score_%s.json" % c["case"]), "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=1, ensure_ascii=False)
        print("SCORE", c["case"], "ok" if sc else "UNPARSED", rec["cost_usd"], flush=True)
    ok = all(json.load(open(os.path.join(OUT, "score_%s.json" % c["case"]), encoding="utf-8"))["score"] for c in CASES)
    print(protocol.result_line({"status": "PASS" if ok else "FAIL", "gates": {"pass": int(ok), "fail": int(not ok)},
                                "first_fail": None if ok else "scorer output unparsed"}))


CITE_RE = re.compile(r"[\w./\\-]+\.(?:py|md|json|log|txt|ps1):\d+")


def later_reads(case_def, tool_calls):
    """Files the arm opened that were modified after the real hand-back session started (repo has moved on)."""
    head = open(os.path.join(BENCH, case_def["hb_log"]), encoding="utf-8", errors="replace").readline()
    m = re.search(r"BGRUN START (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)", head)
    t0 = time.mktime(time.strptime(m.group(1), "%Y-%m-%d %H:%M:%S"))
    out = []
    for name, path, _pat in tool_calls:
        if name == "Read" and path and os.path.isfile(path) and os.path.getmtime(path) > t0:
            out.append(os.path.relpath(path, ROOT).replace("\\", "/"))
    return out


def report():
    key = json.load(open(os.path.join(OUT, "key_x8.json"), encoding="utf-8"))
    rows = []
    for c in CASES:
        sc = json.load(open(os.path.join(OUT, "score_%s.json" % c["case"]), encoding="utf-8"))
        truth = json.load(open(os.path.join(OUT, "truth_%s.json" % c["case"]), encoding="utf-8"))
        for lab in ("A", "B"):
            arm = key[c["case"]][lab]
            r = json.load(open(os.path.join(OUT, "rec_%s_%s.json" % (c["case"], arm)), encoding="utf-8"))
            ans = open(os.path.join(OUT, "answer_%s_%s.md" % (c["case"], arm)), encoding="utf-8").read()
            s = (sc["score"] or {}).get(lab, {})
            rows.append({"case": c["case"], "arm": arm, "label": lab, "decision": s.get("decision_match"),
                         "avoided": s.get("mistake_avoided"), "evidence": s.get("evidence"), "why": s.get("why", ""),
                         "cites": len(CITE_RE.findall(ans)), "usd": r["cost_usd"], "in": r["input_tokens"],
                         "cache_read": r["cache_read"], "cache_create": r["cache_create"], "out": r["output_tokens"],
                         "min": round(r["seconds"] / 60, 1), "turns": r["num_turns"], "tools": len(r["tool_calls"]),
                         "unchanged": r["purpose_unchanged"], "sid_differs": r["sid_differs"], "sid": r["session_id"],
                         "later_reads": later_reads(c, r["tool_calls"]),
                         "real_usd": truth["real_judge_cost_usd"],
                         "real_min": round((truth["real_judge_ms"] or 0) / 60000, 1)})
    with open(os.path.join(OUT, "rows_x8.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=1, ensure_ascii=False)
    print(json.dumps(rows, ensure_ascii=False))
    print(protocol.result_line({"status": "PASS", "gates": {"pass": len(rows), "fail": 0}, "first_fail": None,
                                "artefacts": [{"path": "tools/bench/forkbench/rows_x8.json",
                                               "md5": md5_file(os.path.join(OUT, "rows_x8.json"))}]}))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "prep"
    {"prep": lambda: prep(), "run": lambda: run(sys.argv[2:4]), "blind": lambda: blind(), "score": lambda: score(),
     "report": lambda: report()}[cmd]()
