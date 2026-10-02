"""Self-test of tools/hooks/guard_agent_exit.py (SubagentStop hook, card chat-E1). Offline: no LabVIEW, GUI or hardware.

PREDICTION CONTRACT: 11 cases, each = (expected exit code, expected guard-log marker or None); all 11 pass, 0 fail.
  A live child named in this agent's transcript            -> 2
  B same run after a BGRUN END line                         -> 0
  C dead PID, no END                                        -> 0, log DEAD-NO-END
  D live run named only in ANOTHER agent's transcript       -> 0
  E unreadable stdin (not JSON)                             -> 0, log FAIL-OPEN
  F transcript path missing, no ledger binding              -> 0
  G loop breaker: refusals 1..3 -> 2, the 4th               -> 0, log LOOP-BREAKER
  H reused log: last START older than this agent's call     -> 0
  I ledger attribution (no transcript; card bound in active.json, launches.jsonl row) -> 2
  J quoted path with spaces and `--log=` form               -> 2
  K hook_event_name Stop (not a sub-agent)                  -> 0
Fixtures live in a temp dir; the dummy child is a real short-lived python sleep process, killed at the end.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(PROJECT, "tools"))
import protocol  # noqa: E402

HOOK = os.path.join(PROJECT, "tools", "hooks", "guard_agent_exit.py")
T = tempfile.mkdtemp(prefix="gae_selftest_")
os.makedirs(os.path.join(T, "tools", "bench", "cards"))
GLOG = os.path.join(T, "guard.log")
STATE = os.path.join(T, "state.json")
ENV = dict(os.environ, GUARD_AGENT_EXIT_PROJECT=T, GUARD_AGENT_EXIT_LOG=GLOG, GUARD_AGENT_EXIT_STATE=STATE,
           PROTOCOL_ACTIVE=os.path.join(T, "active.json"), PROTOCOL_LAUNCHES=os.path.join(T, "launches.jsonl"))
NOW_ISO = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
OLD_ISO = datetime.fromtimestamp(time.time() + 3600, timezone.utc).isoformat().replace("+00:00", "Z")


def lt(dt=0):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + dt))


def bgrun_log(rel, pid, start_dt=0, ended=False):
    p = os.path.join(T, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write("BGRUN START %s limit 5 min: py -u tools/recipes/x.py\nBGRUN PID %d\nprogress\n" % (lt(start_dt), pid))
        if ended:
            f.write("BGRUN END rc=0 after 3s\n")
    return p


def transcript(name, cmds, ts=NOW_ISO):
    p = os.path.join(T, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "user", "timestamp": ts, "message": {"content": "go"}}) + "\n")
        for c in cmds:
            f.write(json.dumps({"type": "assistant", "timestamp": ts, "message": {"content": [
                {"type": "text", "text": "launching"},
                {"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": c}}]}}) + "\n")
    return p


def cmd_for(log):
    return "cd \"%s\" && py tools/bgrun.py --material --max-min 5 --log %s -- py -u tools/recipes/x.py" % (T, log)


def ev(agent, tp=None, event="SubagentStop"):
    return {"session_id": "s1", "transcript_path": os.path.join(T, "main.jsonl"), "cwd": T,
            "hook_event_name": event, "agent_id": agent, "agent_type": "material",
            "agent_transcript_path": tp, "stop_hook_active": False, "last_assistant_message": "waiting"}


def call(payload):
    data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
    r = subprocess.run([sys.executable, HOOK], input=data, capture_output=True, env=ENV, timeout=30)
    return r.returncode, r.stderr.decode("utf-8", "replace")


def glog():
    try:
        return open(GLOG, encoding="utf-8").read()
    except FileNotFoundError:
        return ""


def reset_state():
    if os.path.exists(STATE):
        os.remove(STATE)


results = []


def check(label, got_rc, want_rc, marker=None, extra=""):
    ok = got_rc == want_rc and (marker is None or marker in glog())
    results.append((label, ok))
    print("%s %s rc=%s want=%s%s %s" % ("PASS" if ok else "FAIL", label, got_rc, want_rc,
                                        (" marker=" + marker) if marker else "", extra[:160].replace("\n", " ")))


child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
dead = subprocess.Popen([sys.executable, "-c", "pass"])
dead.wait()
try:
    # A / B
    la = bgrun_log("tools/bench/a.log", child.pid)
    ta = transcript("agentA.jsonl", [cmd_for("tools/bench/a.log")])
    rc, err = call(ev("A", ta)); check("A live-child-refused", rc, 2, extra=err)
    reset_state()
    with open(la, "a", encoding="utf-8") as f:
        f.write("BGRUN END rc=0 after 9s\n")
    rc, err = call(ev("A", ta)); check("B ended-allowed", rc, 0, extra=err)
    # C
    bgrun_log("tools/bench/c.log", dead.pid)
    tc = transcript("agentC.jsonl", [cmd_for("tools/bench/c.log")])
    rc, err = call(ev("C", tc)); check("C dead-pid-allowed", rc, 0, "DEAD-NO-END", err)
    # D: live run named only in agent Other's transcript; agent D launched nothing
    bgrun_log("tools/bench/d.log", child.pid)
    transcript("agentOther.jsonl", [cmd_for("tools/bench/d.log")])
    td = transcript("agentD.jsonl", ["py tools/protocol.py bind x"])
    rc, err = call(ev("D", td)); check("D other-agent-run-allowed", rc, 0, extra=err)
    # E
    rc, err = call(b"\xff not json {"); check("E unreadable-input-allowed", rc, 0, "FAIL-OPEN", err)
    # F
    rc, err = call(ev("F", os.path.join(T, "missing.jsonl"))); check("F missing-transcript-allowed", rc, 0, extra=err)
    # G loop breaker
    reset_state()
    bgrun_log("tools/bench/g.log", child.pid)
    tg = transcript("agentG.jsonl", [cmd_for("tools/bench/g.log")])
    rcs = [call(ev("G", tg))[0] for _ in range(4)]
    check("G loop-breaker-4th-allowed", rcs[3], 0, "LOOP-BREAKER", "rcs=%s" % rcs)
    results[-1] = (results[-1][0], results[-1][1] and rcs[:3] == [2, 2, 2])
    # H reused log: START 1 h before this agent's launch call
    reset_state()
    bgrun_log("tools/bench/h.log", child.pid, start_dt=-3600)
    th = transcript("agentH.jsonl", [cmd_for("tools/bench/h.log")])
    rc, err = call(ev("H", th)); check("H reused-old-log-allowed", rc, 0, extra=err)
    # I ledger attribution
    reset_state()
    bgrun_log("tools/bench/i.log", child.pid)
    with open(ENV["PROTOCOL_ACTIVE"], "w", encoding="utf-8") as f:
        json.dump({"I": {"card": "task_x.json", "id": "card-I", "bound": lt(-60)}}, f)
    with open(ENV["PROTOCOL_LAUNCHES"], "w", encoding="utf-8") as f:
        f.write(json.dumps({"card": "card-I", "log": "i.log", "t": lt(-30)}) + "\n")
        f.write(json.dumps({"card": "card-other", "log": "d.log", "t": lt(-30)}) + "\n")
    rc, err = call(ev("I", None)); check("I ledger-attribution-refused", rc, 2, extra=err)
    # J quoted path with spaces + --log=
    reset_state()
    bgrun_log("my dir/j.log", child.pid)
    bgrun_log("tools/bench/j2.log", child.pid)
    tj = transcript("agentJ.jsonl", ["py tools/bgrun.py --max-min 5 --log \"%s\" -- py -u x.py"
                                     % os.path.join(T, "my dir", "j.log"),
                                     "py tools/bgrun.py --max-min 5 --log=tools/bench/j2.log -- py -u y.py"])
    rc, err = call(ev("J", tj))
    check("J quoted-and-equals-forms-refused", rc, 2, extra=err)
    results[-1] = (results[-1][0], results[-1][1] and "j.log" in err and "j2.log" in err)
    # K
    reset_state()
    rc, err = call(ev("A2", transcript("agentK.jsonl", [cmd_for("tools/bench/g.log")]), event="Stop"))
    check("K stop-event-not-guarded", rc, 0, extra=err)
finally:
    child.kill()
    child.wait()
    shutil.rmtree(T, ignore_errors=True)

n_pass = sum(1 for _, ok in results if ok)
n_fail = len(results) - n_pass
ff = next((l for l, ok in results if not ok), None)
print("SUMMARY %d pass / %d fail" % (n_pass, n_fail))
print(protocol.result_line(protocol.make_result(n_pass, n_fail, ff)))
sys.exit(0 if n_fail == 0 else 1)
