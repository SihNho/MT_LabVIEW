r"""selftest_protocol.py - session protocol v1 core (docs/session-protocol.md; tools/protocol.py; docs/protocol/*.json;
the C6 RESULT line in tools/stagekit.py and tools/motor_gate.py; tools/bgrun.py reading it). NO LABVIEW: every case is
a pure function, a JSON file in a temp dir, or a nested bgrun over a throwaway fixture script that only prints.

PRIOR ART CHECKED: tools/bench/selftest_bgrun_fail_scan.py (nested-bgrun method, reused), selftest_stagekit.py
(new_stage() fixture shape, reused), selftest_motor_fail_exit.py (motor half of C6 - not repeated here).

PREDICTION CONTRACT (every row PASS; the last line is this test's own RESULT line)
  S1-S9  each schema accepts its example: the six ```json blocks and the RESULT line of docs/session-protocol.md,
         instantiated (`a|b|c` -> a, md5 `...` -> 32 zeros, slug `...` -> device-failed) with `advances` added to task
         and next; goalmap / decisions-pending from inline fixtures shaped exactly as the brief
  R1-R9  refusals: an unknown field (every kind), `why` 301 chars, advances AND unblocks missing (task, next),
         advances empty, facts 11 items, open 4 items, a goal id not in the goal map, a malformed schema name
  P1-P7  result_line/parse_result_line: round trip; LAST of several; None without one; malformed -> FAIL;
         run_verdict any-fail; log_verdict legacy for a pre-switch run, rc-only after; first_fail_signature
  C1-C3  CLI validate exit 0 / exit 1 with a one-line reason; `new` writes a skeleton card
  B1-B5  nested bgrun: RESULT FAIL + exit 0 -> rc 1 with `(RESULT:`; FAIL/rc=2 text + exit 0, no RESULT -> rc 0 (body
         scan removed); RESULT PASS -> rc 0; RESULT PASS + exit 3 -> rc 3; a RESULT FAIL in a peer_*.log -> rc 0
  K1-K4  stagekit: summary() ends with RESULT (first_fail = first failing gate); run() exception -> first_fail = the
         exception text; an uncaught exception -> a RESULT FAIL line last; a gate after summary() is re-printed at exit
"""
import copy
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import protocol as P  # noqa: E402

BGRUN = os.environ.get("BGRUN_UNDER_TEST") or os.path.join(TOOLS, "bgrun.py")
TMP = tempfile.mkdtemp(prefix="selftest_protocol_")
rows = []


def gate(label, ok, detail=""):
    rows.append((bool(ok), label))
    print("  {0}  {1}{2}".format("PASS" if ok else "FAIL", label, ("  " + str(detail)[:160]) if detail else ""),
          flush=True)


# ------------------------------------------------------------------------------------------------ examples
def inst(v, key=None):
    if isinstance(v, dict):
        return {k: inst(x, k) for k, x in v.items()}
    if isinstance(v, list):
        return [inst(x, key) for x in v]
    if isinstance(v, str):
        if v == "..." and key == "md5":
            return "0" * 32
        if v == "..." and key == "slug":
            return "device-failed"
        if "|" in v and " " not in v:
            return v.split("|")[0]
    return v


def doc_examples():
    doc = open(os.path.join(ROOT, "docs", "session-protocol.md"), encoding="utf-8").read()
    out = {}
    for block in re.findall(r"```json\n(.*?)```", doc, re.S):
        d = json.loads(block)
        out[d["schema"]] = inst(d)
    m = re.search(r"^RESULT (\{.*\})$", doc, re.M)
    out["result-line/1"] = inst(json.loads(m.group(1)))
    return out


GOALMAP_FIX = {"schema": "goalmap/1",
               "requirements": [{"id": "R2.3", "title": "Camera acquisition in its own loop",
                                 "source": "project-requirements/parallelization-requirement.md:15", "status": "open"}],
               "milestones": [{"id": "M5", "title": "Loop 1.3 split out", "requirements": ["R2.3"],
                               "done_when": "scheduler in its own loop; ExecState 1", "status": "open",
                               "evidence": []}],
               "current": {"milestone": "M5", "stage": "plan"}}
DECISIONS_FIX = {"schema": "decisions-pending/1",
                 "items": [{"id": "d-1", "asked": "2026-09-24T18:30:00+09:00", "by": "cycle 74",
                            "question": "Run D1_s3_loop15.vi functionally now?", "options": ["yes", "no", "later"],
                            "recommendation": "later", "blocks": ["M5"], "status": "open", "answer": None,
                            "answered_at": None}]}
GOAL_IDS = {"R2.3", "M5"}


def schema_cases():
    ex = doc_examples()
    ex["task/1"]["advances"] = ["R2.3", "M5"]
    ex["next/1"]["advances"] = ["M5"]
    ex["goalmap/1"] = GOALMAP_FIX
    ex["decisions-pending/1"] = DECISIONS_FIX
    for i, k in enumerate(sorted(ex), 1):
        ok, why = P.validate_obj(ex[k], GOAL_IDS)
        gate("S%d %s accepts its example" % (i, k), ok, why)
    # refusals
    for k in sorted(ex):
        bad = copy.deepcopy(ex[k])
        bad["surprise"] = 1
        ok, why = P.validate_obj(bad)
        gate("R1 %s refuses an unknown field" % k, not ok and "unknown field" in why, why)
    t = copy.deepcopy(ex["task/1"])
    t["why"] = "x" * 301
    ok, why = P.validate_obj(t)
    gate("R2 task refuses a 301-char why", not ok and "why" in why, why)
    for k in ("task/1", "next/1"):
        b = copy.deepcopy(ex[k])
        b.pop("advances", None)
        ok, why = P.validate_obj(b)
        gate("R3 %s refuses missing advances+unblocks" % k, not ok, why)
        b["advances"] = []
        ok, why = P.validate_obj(b)
        gate("R4 %s refuses an EMPTY advances" % k, not ok, why)
        b.pop("advances")
        b["unblocks"] = "M5"
        ok, why = P.validate_obj(b, GOAL_IDS)
        gate("R5 %s accepts unblocks alone (a pure tooling task)" % k, ok, why)
    r = copy.deepcopy(ex["result/1"])
    r["facts"] = ["f"] * 11
    gate("R6 result refuses 11 facts", not P.validate_obj(r)[0], P.validate_obj(r)[1])
    r = copy.deepcopy(ex["result/1"])
    r["open"] = ["q"] * 4
    gate("R7 result refuses 4 open items", not P.validate_obj(r)[0], P.validate_obj(r)[1])
    t = copy.deepcopy(ex["task/1"])
    t["advances"] = ["M99"]
    ok, why = P.validate_obj(t, GOAL_IDS)
    gate("R8 a goal id not in the goal map is refused", not ok and "M99" in why, why)
    ok, why = P.validate_obj({"schema": "task"})
    gate("R9 a malformed schema name is refused", not ok, why)
    return ex


def result_cases():
    d = P.make_result(5, 1, "G3 wire landed", [{"path": "claudeDev/x.vi", "md5": "0" * 32}])
    line = P.result_line(d)
    back = P.parse_result_line("noise\n" + line + "\n")
    gate("P1 result_line -> parse_result_line round trip", back == d, line)
    two = P.result_line(P.make_result(1, 0)) + "\nmid\n" + line + "\n"
    gate("P2 parse_result_line returns the LAST line", P.parse_result_line(two) == d)
    gate("P3 no RESULT line -> None", P.parse_result_line("  FAIL  x\nRESULT: REJECTED\n") is None)
    mal = P.parse_result_line('RESULT {"schema":"result-line/1","status":"PASS"}\n')
    gate("P4 a malformed RESULT line reads as FAIL", mal is not None and P.result_failed(mal), mal)
    seg = ("BGRUN START 2026-09-30 10:00:00 limit 5 min: bash chain\n" + P.result_line(P.make_result(0, 1, "refused"))
           + "\n" + P.result_line(P.make_result(1, 0)) + "\nBGRUN END rc=0 after 3s\n")
    v = P.run_verdict(seg)
    gate("P5 run_verdict: ANY failing RESULT fails the run", v["failed"] and v["first_fail"] == "refused", v)
    legacy_re = re.compile(r"^\s*FAIL\b", re.M)
    old = "BGRUN START 2026-09-20 10:00:00 limit 5 min: py x.py\n  FAIL  G1\nBGRUN END rc=0 after 1s\n"
    new = "BGRUN START 2026-09-30 10:00:00 limit 5 min: py x.py\n  FAIL  G1\nBGRUN END rc=0 after 1s\n"
    a, b = P.log_verdict(old, legacy_re), P.log_verdict(new, legacy_re)
    gate("P6 log_verdict: legacy rule before SWITCH_TS, exit code after",
         a["failed"] and a["source"] == "legacy" and not b["failed"] and b["source"] == "rc", (a["source"], b["source"]))
    gsig = re.compile(r"^\**\s*(FAIL\b[^\n]{0,120})", re.M)
    s1 = P.first_fail_signature(seg)
    s2 = P.first_fail_signature(old, gsig, P.last_segment(old)[0])
    s3 = P.first_fail_signature(new, gsig, P.last_segment(new)[0])
    gate("P7 first_fail_signature: RESULT / legacy / none", (s1, s2, s3) == ("refused", "FAIL  G1", None), (s1, s2, s3))


def cli_cases(ex):
    good = os.path.join(TMP, "task_ok.json")
    json.dump(ex["task/1"], open(good, "w", encoding="utf-8"), ensure_ascii=False)
    bad = dict(ex["task/1"], extra=1)
    badp = os.path.join(TMP, "task_bad.json")
    json.dump(bad, open(badp, "w", encoding="utf-8"), ensure_ascii=False)
    r1 = subprocess.run([sys.executable, os.path.join(TOOLS, "protocol.py"), "validate", good, "--no-goalmap"],
                        capture_output=True, text=True, encoding="utf-8")
    r2 = subprocess.run([sys.executable, os.path.join(TOOLS, "protocol.py"), "validate", badp, "--no-goalmap"],
                        capture_output=True, text=True, encoding="utf-8")
    gate("C1 CLI validate: exit 0 on a valid card", r1.returncode == 0 and r1.stdout.startswith("OK"), r1.stdout)
    gate("C2 CLI validate: exit 1 + one-line reason", r2.returncode == 1 and r2.stdout.count("\n") == 1
         and "unknown field" in r2.stdout, r2.stdout)
    old = P.CARDS_DIR
    P.CARDS_DIR = os.path.join(TMP, "cards")
    try:
        rc = P.main(["new", "task", "--id", "74-03"])
    finally:
        P.CARDS_DIR = old
    card = os.path.join(TMP, "cards", "task_74-03.json")
    gate("C3 `new task --id 74-03` writes tools/bench/cards-shaped task_74-03.json", rc == 0 and os.path.exists(card)
         and json.load(open(card, encoding="utf-8"))["id"] == "74-03")


def bgrun(code, tag, logname=None):
    src = os.path.join(TMP, tag + ".py")
    open(src, "w", encoding="utf-8").write(code)
    log = os.path.join(TMP, logname or (tag + ".log"))
    subprocess.run([sys.executable, BGRUN, "--max-min", "1", "--log", log, "--", sys.executable, "-u", src],
                   capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=ROOT)
    ends = re.findall(r"(?m)^BGRUN END rc=(\d+)(.*)$", open(log, encoding="utf-8", errors="replace").read())
    return (int(ends[-1][0]), ends[-1][1]) if ends else (-1, "")


def bgrun_cases():
    fail = P.result_line(P.make_result(2, 1, "G2 x"))
    ok = P.result_line(P.make_result(3, 0))
    c, t = bgrun("print('  PASS  G1')\nprint(%r)\n" % fail, "b1")
    gate("B1 RESULT FAIL + exit 0 -> rc 1 with (RESULT:", c == 1 and "(RESULT:" in t, (c, t))
    c, t = bgrun("print('  FAIL  quoted gate')\nprint('probe exit=1 rc=2')\nprint('=== 3 fail ===')\n", "b2")
    gate("B2 FAIL / rc=2 text, no RESULT, exit 0 -> rc 0 (body scan removed)", c == 0, (c, t))
    c, t = bgrun("print(%r)\n" % ok, "b3")
    gate("B3 RESULT PASS + exit 0 -> rc 0", c == 0, (c, t))
    c, t = bgrun("import sys\nprint(%r)\nsys.exit(3)\n" % ok, "b4")
    gate("B4 RESULT PASS + exit 3 -> rc 3 (exit code still counts)", c == 3, (c, t))
    c, t = bgrun("print(%r)\n" % fail, "b5", logname="peer_selftest_protocol_fixture.log")
    gate("B5 a RESULT FAIL inside a peer_*.log is not the run's verdict -> rc 0", c == 0, (c, t))


def stagekit_run(body, tag):
    src = os.path.join(TMP, tag + ".py")
    open(src, "w", encoding="utf-8").write(
        "import os, sys, tempfile\nsys.path.insert(0, %r)\nimport stagekit as K\n"
        "s = K.Stage(os.path.join(tempfile.gettempdir(), 'stagekit_selftest_input.vi'), 'deadbeef', 'sp_case',"
        " fresh=False, preload=False, pins=(), out_json=os.path.join(tempfile.gettempdir(), 'sp_case.json'))\n"
        % TOOLS + body)
    p = subprocess.run([sys.executable, "-u", src], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=ROOT)
    lines = [l for l in p.stdout.splitlines() if l.strip()]
    return p.returncode, (lines[-1] if lines else ""), p.stdout


def stagekit_cases():
    rc, last, _ = stagekit_run("s.gate('g1', True)\ns.gate('g2 bad', False)\nsys.exit(s.summary())\n", "k1")
    d = P.parse_result_line(last)
    gate("K1 summary() ends with RESULT FAIL, first_fail = first failing gate",
         rc == 1 and d and d["status"] == "FAIL" and d["gates"] == {"pass": 1, "fail": 1} and d["first_fail"] == "g2 bad",
         last)
    rc, last, _ = stagekit_run("def fn(st):\n    st.gate('g1', True)\n    raise ValueError('boom 42')\n"
                               "K.Stage.close = lambda self, expect_files=None: self.summary()\n"
                               "sys.exit(K.run(fn, s))\n", "k2")
    d = P.parse_result_line(last)
    gate("K2 run(): exception -> RESULT FAIL, first_fail = the exception text",
         d and d["status"] == "FAIL" and "boom 42" in (d["first_fail"] or ""), last)
    rc, last, _ = stagekit_run("s.gate('g1', True)\nraise RuntimeError('uncaught 7')\n", "k3")
    d = P.parse_result_line(last)
    gate("K3 uncaught exception -> a RESULT FAIL line is LAST", rc != 0 and d and d["status"] == "FAIL"
         and "uncaught 7" in (d["first_fail"] or ""), last)
    rc, last, _ = stagekit_run("s.gate('g1', True)\ns.summary()\ns.gate('late', False)\n", "k4")
    d = P.parse_result_line(last)
    gate("K4 a gate after summary() -> RESULT re-printed at exit", d and d["gates"] == {"pass": 1, "fail": 1}, last)


def main():
    print("=== selftest_protocol (no LabVIEW) ===", flush=True)
    ex = schema_cases()
    result_cases()
    cli_cases(ex)
    bgrun_cases()
    stagekit_cases()
    nbad = sum(1 for r in rows if not r[0])
    print("=== %d pass / %d fail" % (len(rows) - nbad, nbad), flush=True)
    first = next((r[1] for r in rows if not r[0]), None)
    print(P.result_line(P.make_result(len(rows) - nbad, nbad, first)), flush=True)
    return 1 if nbad else 0


if __name__ == "__main__":
    sys.exit(main())
