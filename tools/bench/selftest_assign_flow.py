# ---
# labview: none
# hardware: none
# ---
r"""Self-test for the PURPOSE FLOW (card chat-A1, user 2026-10-04): tools/hooks/guard_assign.py, the (h) roles in
tools/hooks/guard_session.py, and tools/cycle_runner.py --flow purpose with STUB sessions.

NO LabVIEW, NO agents, NO `claude -p`: the hook is fed synthetic PreToolUse JSON on stdin (as the harness does), and the
runner's judgement / assignment sessions are replaced by --dry-cmd / --assign-dry-cmd stand-ins written to a temp dir.
Hook state files go to tools/bench/session_selftest-af-*.json and are deleted at the end.

PREDICTION CONTRACT (gates):
  H1  CYCLE_ROLE=judgement: a `material` dispatch is REFUSED ("PURPOSE FLOW"); `log-reader` is ALLOWED
  H2  CYCLE_ROLE=assign: 8 card dispatches with PASS results are all ALLOWED (MAX_DISPATCHES=6 does not bind)
  H3  a card with neither advances nor unblocks is REFUSED as a PLAIN refusal (no sticky hand-back)
  H4  (a) unexplained FAIL, its one retry ALLOWED, the retry FAILs unexplained -> next dispatch HANDBACK a, then sticky
  H5  one explained (address) FAIL does not hand back; the same class a second time -> HANDBACK b
  H6  (c) writes reaching the plan file / CLAUDE.md / tools/hooks, a memory-limit change, a disjoint goal id -> HANDBACK c;
      the same memory-limit change NAMED by the purpose -> ALLOWED
  H7  (d) decisions_pending gains an open item -> HANDBACK d; a result BLOCKED on device `user` -> HANDBACK d
  H8  cap-time (t0 181 min ago) / cap-usd (transcript + subagents estimate 65 USD >= 60, duplicates de-duplicated) /
      backstop (config 3 -> the 4th dispatch) each -> HANDBACK with that trigger
  H9  no ASSIGN_STATE -> REFUSED (fails closed)
  H10 runner_verdict: met with evidence -> PURPOSE_MET; a missing evidence row -> purpose-unproven; envelope 61 USD ->
      cap-usd; no result file -> no-result; a sticky hook trigger wins over a PURPOSE_MET file
  R1  runner, purpose met: ASSIGN start + end PURPOSE_MET, no HANDBACK line, a valid assign/1 card, exit 0
  R2  runner, the session CLAIMS PURPOSE_MET while trigger a stands -> HANDBACK a (overridden), a valid handback/1 with
      card rows; the hand-back judgement (PURPOSE_PHASE=handback, HANDBACK_RECORD set) revises next.json -> round 2 ->
      PURPOSE_MET; round 2's assign card carries handback_in
  R3  runner, no result -> HANDBACK no-result; the judgement leaves next.json unchanged -> "the cycle closes"
  R4  runner, always HANDBACK with max_handbacks_per_cycle 2 -> HANDBACK-LIMIT after round 2
  R5  runner, envelope total_cost_usd 61 -> HANDBACK cap-usd
  R6  --flow legacy: no ASSIGN line; dry run without --assign-dry-cmd: "skipped"; judgement leaving next.json
      unchanged: "no NEW purpose"
Output avoids the strings bgrun/guard_peer scan for (`rc=<n>`, a line starting with FAIL).
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
HOOKS = os.path.join(ROOT, "tools", "hooks")
GS = os.path.join(HOOKS, "guard_session.py")
RUNNER = os.path.join(ROOT, "tools", "cycle_runner.py")
sys.path.insert(0, HOOKS)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import guard_assign as GA  # noqa: E402
import protocol  # noqa: E402

RESULTS = []
SIDS = []
PURPOSE = {"act": "P4 session 3 build on the s02 file", "pass": ["scratch gates pass", "adopted file saved"],
           "plan": {"path": "docs/d1/ring-p4b.md", "md5": None}, "advances": ["M3", "R1"], "unblocks": None,
           "task_kind": "build", "note": None}


def gate(label, ok, detail=""):
    RESULTS.append((label, bool(ok)))
    print("  %-4s %-60s %s" % ("ok" if ok else "BAD", label, str(detail)[:150]), flush=True)


def hook(env_extra, sub, prompt, sid, transcript=None):
    env = dict(os.environ)
    for k in ("CYCLE_SESSION", "CYCLE_ROLE", "ASSIGN_STATE", "ASSIGN_CONFIG", "BENCH_CELL"):
        env.pop(k, None)
    env["CYCLE_SESSION"] = "1"
    env.update(env_extra)
    SIDS.append(sid)
    payload = {"tool_name": "Agent", "session_id": sid, "tool_input": {"subagent_type": sub, "prompt": prompt}}
    if transcript:
        payload["transcript_path"] = transcript
    p = subprocess.run([sys.executable, GS], input=json.dumps(payload), text=True, capture_output=True,
                       encoding="utf-8", errors="replace", timeout=60, env=env)
    return p.returncode, (p.stderr or "") + (p.stdout or "")


def mk_card(d, cid, advances=("M3",), write=("tools/bench/x_*.py",), goal="build step", retry=None, unblocks=None):
    c = {"schema": "task/1", "id": cid, "kind": "build", "goal": goal,
         "flags": {"labview": "none", "gui": False, "hardware": "none", "run_vi": False, "write": list(write),
                   "status_edit": False, "git_commit": False, "peers": []},
         "budget": {"failures": 2, "minutes": 30}}
    if advances:
        c["advances"] = list(advances)
    if unblocks:
        c["unblocks"] = unblocks
    if retry:
        c["retry_of_card"] = retry
    p = os.path.join(d, "task_%s.json" % cid)
    json.dump(c, open(p, "w", encoding="utf-8"))
    return p


def mk_result(d, cid, status="PASS", ff=None, blocked=None):
    r = {"schema": "result/1", "id": cid, "status": status, "gates": {"pass": 1, "fail": 0 if status == "PASS" else 1},
         "first_fail": ff, "blocked_by": blocked, "artefacts": [], "facts": [], "open": [],
         "cost": {"usd": None, "minutes": 1, "labview_runs": 0}, "note": ""}
    time.sleep(0.05)
    json.dump(r, open(os.path.join(d, "result_%s.json" % cid), "w", encoding="utf-8"))


def fresh_state(tmp, name, purpose=None, t0=None, decisions=None):
    st = os.path.join(tmp, "state_%s.json" % name)
    GA.new_state(st, 1, 1, purpose or PURPOSE, "0" * 32, decisions or os.path.join(tmp, "no_decisions.json"), t0)
    return st


def env_for(st, cfg):
    return {"CYCLE_ROLE": "assign", "ASSIGN_STATE": st, "ASSIGN_CONFIG": cfg}


def hook_tests(tmp, cfg):
    cards = os.path.join(tmp, "cards")
    os.makedirs(cards, exist_ok=True)
    # H1
    c = mk_card(cards, "h1")
    r1, o1 = hook({"CYCLE_ROLE": "judgement"}, "material", "CARD %s" % c, "selftest-af-h1")
    r2, _ = hook({"CYCLE_ROLE": "judgement"}, "log-reader", "read log x", "selftest-af-h1b")
    gate("H1 judgement refuses material, allows log-reader", r1 == 2 and "PURPOSE FLOW" in o1 and r2 == 0, (r1, r2))
    # H2
    st = fresh_state(tmp, "h2")
    codes = []
    for i in range(8):
        cp = mk_card(cards, "h2-%d" % i)
        codes.append(hook(env_for(st, cfg), "material", "CARD %s" % cp, "selftest-af-h2")[0])
        mk_result(cards, "h2-%d" % i)
    gate("H2 eight dispatches allowed in the assign role", codes == [0] * 8, codes)
    # H3
    st = fresh_state(tmp, "h3")
    cp = mk_card(cards, "h3", advances=())
    r, o = hook(env_for(st, cfg), "material", "CARD %s" % cp, "selftest-af-h3")
    gate("H3 unscoped card: plain refusal, no hand-back", r == 2 and "neither" in o and not GA.state_load(st)["handback"], r)
    # H4 (a)
    st = fresh_state(tmp, "h4")
    e = env_for(st, cfg)
    ra = hook(e, "material", "CARD %s" % mk_card(cards, "h4a"), "selftest-af-h4")[0]
    mk_result(cards, "h4a", "FAIL", "GATE X17 created node class Foo, plan says Bar")
    rb = hook(e, "material", "CARD %s" % mk_card(cards, "h4b", retry="h4a"), "selftest-af-h4")[0]
    mk_result(cards, "h4b", "FAIL", "GATE W1 lost data wire at node 77")
    rc_, oc = hook(e, "material", "CARD %s" % mk_card(cards, "h4c"), "selftest-af-h4")
    rd, od = hook(e, "log-reader", "read the log", "selftest-af-h4")
    gate("H4 (a) unexplained fail after its one retry -> HANDBACK a, sticky",
         ra == 0 and rb == 0 and rc_ == 2 and "a-unexplained-after-retry" in oc and rd == 2 and "HANDBACK REQUIRED" in od,
         (ra, rb, rc_, rd))
    # H5 (b)
    st = fresh_state(tmp, "h5")
    e = env_for(st, cfg)
    addr = "ADDRESS-UNRESOLVED Local #-20 terminal 'value' does not bind uniquely"
    r5a = hook(e, "material", "CARD %s" % mk_card(cards, "h5a"), "selftest-af-h5")[0]
    mk_result(cards, "h5a", "FAIL", addr)
    r5b = hook(e, "material", "CARD %s" % mk_card(cards, "h5b"), "selftest-af-h5")[0]
    mk_result(cards, "h5b", "FAIL", addr.replace("#-20", "#-31"))
    r5c, o5c = hook(e, "material", "CARD %s" % mk_card(cards, "h5c"), "selftest-af-h5")
    kind = GA.classify({"first_fail": addr, "status": "FAIL"})[0]
    gate("H5 one explained fail passes, the same class twice -> HANDBACK b",
         kind == "address" and r5a == 0 and r5b == 0 and r5c == 2 and "b-same-class-twice" in o5c, (kind, r5a, r5b, r5c))
    # H6 (c)
    cases = [("plan", dict(write=["docs/d1/**"])), ("claude", dict(write=["CLAUDE.md"])),
             ("hooks", dict(write=["tools/hooks/guard_bash.py"])), ("x10", dict(goal="raise the X10 cut to 750 MB")),
             ("scope", dict(advances=["M8"]))]
    got = []
    for name, kw in cases:
        st = fresh_state(tmp, "h6" + name)
        r, o = hook(env_for(st, cfg), "material", "CARD %s" % mk_card(cards, "h6" + name, **kw), "selftest-af-h6" + name)
        got.append((name, r, "c-outside-purpose" in o))
    pp = dict(PURPOSE, **{"pass": PURPOSE["pass"] + ["raise the X10 cut to 750 MB per PD340"]})
    st = fresh_state(tmp, "h6named", purpose=pp)
    rn = hook(env_for(st, cfg), "material", "CARD %s" % mk_card(cards, "h6named", goal="raise the X10 cut to 750 MB"),
              "selftest-af-h6named")[0]
    gate("H6 (c) plan / CLAUDE.md / hooks / memory limit / scope -> HANDBACK c; purpose-named change allowed",
         all(r == 2 and hit for _n, r, hit in got) and rn == 0, (got, rn))
    # H7 (d)
    dec = os.path.join(tmp, "decisions_pending.json")
    json.dump({"schema": "decisions-pending/1", "items": []}, open(dec, "w", encoding="utf-8"))
    st = fresh_state(tmp, "h7", decisions=dec)
    e = env_for(st, cfg)
    r7a = hook(e, "material", "CARD %s" % mk_card(cards, "h7a"), "selftest-af-h7")[0]
    json.dump({"schema": "decisions-pending/1", "items": [{"id": "D-x", "status": "open"}]}, open(dec, "w", encoding="utf-8"))
    r7b, o7b = hook(e, "material", "CARD %s" % mk_card(cards, "h7b"), "selftest-af-h7")
    st = fresh_state(tmp, "h7u")
    e = env_for(st, cfg)
    hook(e, "material", "CARD %s" % mk_card(cards, "h7u"), "selftest-af-h7u")
    mk_result(cards, "h7u", "BLOCKED", None, {"device": "user", "message": "which cut?"})
    r7c, o7c = hook(e, "material", "CARD %s" % mk_card(cards, "h7v"), "selftest-af-h7u")
    gate("H7 (d) decisions grew / BLOCKED on user -> HANDBACK d",
         r7a == 0 and r7b == 2 and "d-user-question" in o7b and r7c == 2 and "d-user-question" in o7c, (r7a, r7b, r7c))
    # H8 caps
    st = fresh_state(tmp, "h8t", t0=time.time() - 181 * 60)
    r8t, o8t = hook(env_for(st, cfg), "material", "CARD %s" % mk_card(cards, "h8t"), "selftest-af-h8t")
    tr = os.path.join(tmp, "sess.jsonl")
    line = {"type": "assistant", "message": {"id": "m1", "model": "claude-sonnet-5-5",
                                             "usage": {"input_tokens": 0, "output_tokens": 3_000_000}}}
    with open(tr, "w", encoding="utf-8") as f:
        f.write(json.dumps(line) + "\n" + json.dumps(line) + "\n")           # same message id twice = once
    os.makedirs(os.path.join(tmp, "sess", "subagents"), exist_ok=True)
    sub = {"type": "assistant", "message": {"id": "m2", "model": "claude-opus-5-5",
                                            "usage": {"output_tokens": 1_750_000}}}
    with open(os.path.join(tmp, "sess", "subagents", "agent-x.jsonl"), "w", encoding="utf-8") as f:
        f.write(json.dumps(sub) + "\n")
    usd = GA.usd_estimate(tr, GA.load_config(cfg)["prices_per_mtok"])
    st = fresh_state(tmp, "h8u")
    r8u, o8u = hook(env_for(st, cfg), "material", "CARD %s" % mk_card(cards, "h8u"), "selftest-af-h8u", transcript=tr)
    cfg3 = os.path.join(tmp, "cfg_backstop.json")
    json.dump(dict(GA.load_config(cfg), backstop_cards=3), open(cfg3, "w", encoding="utf-8"))
    st = fresh_state(tmp, "h8b")
    bcodes = []
    for i in range(4):
        bcodes.append(hook(env_for(st, cfg3), "material", "CARD %s" % mk_card(cards, "h8b%d" % i), "selftest-af-h8b")[0])
        mk_result(cards, "h8b%d" % i)
    gate("H8 cap-time / cap-usd (estimate %s) / backstop -> HANDBACK" % usd,
         r8t == 2 and "cap-time" in o8t and abs((usd or 0) - 65.0) < 0.01 and r8u == 2 and "cap-usd" in o8u
         and bcodes == [0, 0, 0, 2], (r8t, usd, r8u, bcodes))
    # H9
    r9, o9 = hook({"CYCLE_ROLE": "assign", "ASSIGN_CONFIG": cfg}, "material", "CARD %s" % mk_card(cards, "h9"), "selftest-af-h9")
    gate("H9 no ASSIGN_STATE fails closed", r9 == 2 and "no readable assignment state" in o9, r9)
    # H10 runner_verdict
    st = fresh_state(tmp, "h10")
    res = os.path.join(tmp, "ar.json")
    good = {"schema": "assign-result/1", "cycle": 1, "round": 1, "status": "PURPOSE_MET", "cards": ["x"],
            "pass_evidence": [{"item": 0, "met": True, "evidence": ["result_x.json"]},
                              {"item": 1, "met": True, "evidence": ["result_y.json"]}], "handback": None}
    json.dump(good, open(res, "w", encoding="utf-8"))
    v1 = GA.runner_verdict(st, res, 1.0, 0, GA.load_config(cfg))[:2]
    v2 = GA.runner_verdict(st, res, 61.0, 0, GA.load_config(cfg))[:2]
    json.dump(dict(good, pass_evidence=good["pass_evidence"][:1]), open(res, "w", encoding="utf-8"))
    v3 = GA.runner_verdict(st, res, 1.0, 0, GA.load_config(cfg))[:2]
    v4 = GA.runner_verdict(st, os.path.join(tmp, "none.json"), 1.0, 0, GA.load_config(cfg))[:2]
    json.dump(good, open(res, "w", encoding="utf-8"))
    s = GA.state_load(st)
    s["handback"] = {"trigger": "b-same-class-twice", "detail": "x"}
    GA.state_save(st, s)
    v5 = GA.runner_verdict(st, res, 1.0, 0, GA.load_config(cfg))[:2]
    gate("H10 runner_verdict met / cap-usd / unproven / no-result / sticky wins",
         v1 == ("PURPOSE_MET", None) and v2 == ("HANDBACK", "cap-usd") and v3 == ("HANDBACK", "purpose-unproven")
         and v4 == ("HANDBACK", "no-result") and v5 == ("HANDBACK", "b-same-class-twice"), (v1, v2, v3, v4, v5))


JUDGE = r'''import json, os, sys, time
bench, mode = sys.argv[1], sys.argv[2]
p = os.path.join(bench, "next.json")
phase = os.environ.get("PURPOSE_PHASE", "")
with open(os.path.join(bench, "judge_calls.txt"), "a") as f:
    f.write("%s|%s|%s\n" % (os.environ.get("CYCLE_ROLE"), phase, os.environ.get("HANDBACK_RECORD", "")))
if mode == "keep" and os.path.exists(p):
    print("judge kept next.json"); sys.exit(0)
if phase == "handback" and mode == "keep-on-handback":
    print("judge closed the cycle"); sys.exit(0)
json.dump({"schema": "next/1", "cycle": 1, "act": "stub purpose", "task_kind": "build", "plan": None,
           "pass": ["item zero", "item one"], "blocked_by": None, "stop_requested": False, "advances": ["M3"],
           "note": "%s %s" % (phase or "purpose", time.time())}, open(p, "w", encoding="utf-8"))
print("judge wrote next.json")
'''

ASSIGN = r'''import json, os, subprocess, sys, time
GS, mode, ctr = sys.argv[1], sys.argv[2], sys.argv[3]
res_path, st_path = os.environ["ASSIGN_RESULT"], os.environ["ASSIGN_STATE"]
cards = os.path.dirname(res_path)
rnd = json.load(open(st_path, encoding="utf-8"))["round"]
sid = "selftest-af-run-%d-%d" % (os.getpid(), rnd)
with open(ctr, "a") as f:
    f.write(sid + "\n")
def card(cid, retry=None):
    c = {"schema": "task/1", "id": cid, "kind": "build", "goal": "stub", "advances": ["M3"],
         "flags": {"labview": "none", "gui": False, "hardware": "none", "run_vi": False, "write": ["tools/bench/x_*.py"],
                   "status_edit": False, "git_commit": False, "peers": []}, "budget": {"failures": 2, "minutes": 30}}
    if retry: c["retry_of_card"] = retry
    p = os.path.join(cards, "task_%s.json" % cid); json.dump(c, open(p, "w", encoding="utf-8")); return p
def dispatch(cid, retry=None):
    pl = {"tool_name": "Agent", "session_id": sid, "tool_input": {"subagent_type": "material", "prompt": "CARD " + card(cid, retry)}}
    return subprocess.run([sys.executable, GS], input=json.dumps(pl), text=True, capture_output=True).returncode
def result(cid, status, ff=None):
    time.sleep(0.05)
    json.dump({"schema": "result/1", "id": cid, "status": status, "gates": {"pass": 1, "fail": 0 if status == "PASS" else 1},
               "first_fail": ff, "blocked_by": None, "artefacts": [], "facts": [], "open": [], "cost": {"usd": None,
               "minutes": 1, "labview_runs": 0}, "note": ""}, open(os.path.join(cards, "result_%s.json" % cid), "w", encoding="utf-8"))
def write(status, ev=True):
    d = {"schema": "assign-result/1", "cycle": 1, "round": rnd, "status": status, "cards": [],
         "pass_evidence": [{"item": i, "met": True, "evidence": ["stub evidence"]} for i in range(2)] if ev else [],
         "handback": None if status == "PURPOSE_MET" else {"reason": "stub hand-back"}}
    json.dump(d, open(res_path, "w", encoding="utf-8"))
def met():
    print("dispatch", dispatch("r%d-ok" % rnd)); result("r%d-ok" % rnd, "PASS"); write("PURPOSE_MET")
def trig_a_claim_met():
    dispatch("r%d-a" % rnd); result("r%d-a" % rnd, "FAIL", "GATE X17 created node class Foo, plan says Bar")
    dispatch("r%d-b" % rnd, "r%d-a" % rnd); result("r%d-b" % rnd, "FAIL", "GATE W1 lost data wire at node 77")
    print("third dispatch", dispatch("r%d-c" % rnd)); write("PURPOSE_MET")
if mode == "met": met()
elif mode == "hb-then-met": (trig_a_claim_met() if rnd == 1 else met())
elif mode == "noresult": print("no result written")
elif mode == "always-hb": write("HANDBACK", ev=False)
elif mode == "cost": met(); print(json.dumps({"type": "result", "total_cost_usd": 61.0}))
'''


def runner_tests(tmp, cfg):
    judge = os.path.join(tmp, "judge.py")
    assign = os.path.join(tmp, "assign.py")
    open(judge, "w", encoding="utf-8").write(JUDGE)
    open(assign, "w", encoding="utf-8").write(ASSIGN)
    gs_copy = os.path.join(tmp, "gs_path.txt")
    ctr = os.path.join(tmp, "assign_sids.txt")
    # the assign stub takes the hook path as argv[1]; --assign-dry-cmd is whitespace-split, and ROOT has spaces, so the
    # stub reaches the hook through a space-free launcher in the temp dir
    launcher = os.path.join(tmp, "gs.py")
    open(launcher, "w", encoding="utf-8").write(
        "import runpy, sys\nsys.argv = [%r]\nrunpy.run_path(%r, run_name='__main__')\n" % (GS, GS))
    open(gs_copy, "w").write(GS)

    def case(name, jmode, amode, cfg_path=cfg, extra=(), seed_next=False):
        d = os.path.join(tmp, "run_" + name)
        bench = os.path.join(d, "bench")
        os.makedirs(bench, exist_ok=True)
        if seed_next:
            json.dump({"schema": "next/1", "cycle": 0, "act": "seeded", "task_kind": "build", "plan": None, "pass": [],
                       "blocked_by": None, "stop_requested": False, "advances": ["M3"]},
                      open(os.path.join(bench, "next.json"), "w", encoding="utf-8"))
        sp = os.path.join(d, "STATUS.md")
        open(sp, "w", encoding="utf-8").write("# STATUS (self-test)\n\n## NEXT\nx\n")
        args = [sys.executable, RUNNER, "--dry-cmd", "%s %s %s %s" % (sys.executable, judge, bench, jmode),
                "--cycles", "1", "--status", sp, "--bench-dir", bench, "--max-min", "3", "--assign-config", cfg_path,
                "--peer-dir", os.path.join(d, "peer"), "--goalmap", os.path.join(d, "goalmap.json")] + list(extra)
        if amode:
            args += ["--assign-dry-cmd", "%s %s %s %s %s" % (sys.executable, assign, launcher, amode, ctr)]
        env = dict(os.environ)
        for k in ("CYCLE_SESSION", "CYCLE_ROLE", "ASSIGN_STATE", "ASSIGN_CONFIG", "BENCH_CELL"):
            env.pop(k, None)
        p = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=900, env=env)
        log = open(os.path.join(bench, "cycle_runner.log"), encoding="utf-8").read() \
            if os.path.exists(os.path.join(bench, "cycle_runner.log")) else ""
        return p.returncode, log, bench

    rc, log, bench = case("met", "write", "met")
    ac = os.path.join(bench, "cards", "assign_1_1.json")
    ok_card = os.path.exists(ac) and protocol.validate_obj(json.load(open(ac, encoding="utf-8")))[0]
    gate("R1 purpose met", rc == 0 and "round 1 | start" in log and "| PURPOSE_MET" in log and "HANDBACK |" not in log
         and ok_card, (rc, ok_card))

    rc, log, bench = case("hb", "write", "hb-then-met")
    hb = os.path.join(bench, "cards", "handback_1_1.json")
    hbd = json.load(open(hb, encoding="utf-8")) if os.path.exists(hb) else {}
    calls = open(os.path.join(bench, "judge_calls.txt")).read().splitlines() if os.path.exists(
        os.path.join(bench, "judge_calls.txt")) else []
    a2 = os.path.join(bench, "cards", "assign_1_2.json")
    a2d = json.load(open(a2, encoding="utf-8")) if os.path.exists(a2) else {}
    # 2 card rows: r1-a and its retry r1-b; the third dispatch was REFUSED by the hand-back, so it was never recorded
    hb_ok = bool(hbd) and protocol.validate_obj(hbd)[0] and [c.get("id") for c in hbd.get("cards") or []] == ["r1-a", "r1-b"]
    judged = any(c.startswith("judgement|handback|") and c.endswith("handback_1_1.json") for c in calls)
    gate("R2 claimed MET overridden -> HANDBACK a -> judged -> round 2 MET",
         rc == 0 and "a-unexplained-after-retry" in log and hb_ok and judged
         and "CHANGED - assignment round 2" in log and "round 2 | end" in log and log.count("| PURPOSE_MET") == 1
         and (a2d.get("handback_in") or "").endswith("handback_1_1.json"),
         (rc, hb_ok, judged, len(hbd.get("cards") or []), calls[-1:] if calls else None))
    if not (hb_ok and judged):
        for ln in log.splitlines():
            if ln.startswith(("ASSIGN", "HANDBACK", "CYCLE 1")):
                print("       | " + ln[:300], flush=True)

    rc, log, bench = case("noresult", "keep-on-handback", "noresult")
    gate("R3 no result -> HANDBACK no-result -> unchanged closes", rc == 0 and "| no-result |" in log
         and "unchanged - the cycle closes" in log, rc)

    cfg2 = os.path.join(tmp, "cfg_hb2.json")
    json.dump(dict(GA.load_config(cfg), max_handbacks_per_cycle=2), open(cfg2, "w", encoding="utf-8"))
    rc, log, bench = case("limit", "write", "always-hb", cfg_path=cfg2)
    gate("R4 always HANDBACK -> HANDBACK-LIMIT after round 2", rc == 0 and "HANDBACK-LIMIT" in log
         and "round 2 | end" in log and "round 3" not in log, rc)

    rc, log, bench = case("cost", "write", "cost")
    gate("R5 envelope 61 USD -> HANDBACK cap-usd", rc == 0 and "HANDBACK |" in log and "cap-usd" in log, rc)

    rc_l, log_l, _b = case("legacy", "write", "met", extra=["--flow", "legacy"])
    rc_s, log_s, _b = case("skip", "write", None)
    rc_k, log_k, _b = case("keep", "keep", "met", seed_next=True)
    gate("R6 legacy: no ASSIGN; dry without stand-in: skipped; unchanged next.json: no NEW purpose",
         rc_l == 0 and "ASSIGN |" not in log_l and "skipped (dry run without --assign-dry-cmd)" in log_s
         and "no NEW purpose" in log_k, (rc_l, rc_s, rc_k))
    for line in open(ctr).read().splitlines() if os.path.exists(ctr) else []:
        SIDS.append(line.strip())


def main():
    tmp = tempfile.mkdtemp(prefix="assignflow_")
    if " " in tmp or " " in sys.executable:
        print("  BAD  a temp or interpreter path contains a space (the dry-cmd stand-ins are whitespace-split)", flush=True)
        return 1
    cfg = os.path.join(tmp, "cfg.json")
    json.dump(GA.load_config(GA.DEFAULT_CONFIG), open(cfg, "w", encoding="utf-8"))
    try:
        hook_tests(tmp, cfg)
        runner_tests(tmp, cfg)
    finally:
        for sid in set(SIDS):
            for f in glob.glob(os.path.join(ROOT, "tools", "bench", "session_%s.json*" % sid)):
                try:
                    os.remove(f)
                except OSError:
                    pass
        shutil.rmtree(tmp, ignore_errors=True)
    good = sum(1 for _, ok in RESULTS if ok)
    bad = [lab for lab, ok in RESULTS if not ok]
    print("SUMMARY %d/%d gates pass" % (good, len(RESULTS)), flush=True)
    print(protocol.result_line(protocol.make_result(good, len(bad), bad[0] if bad else None)), flush=True)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
