r"""Self-test for tools/hooks/guard_session.py and guard_bash.py's retrospective marker.

Touches NO LabVIEW, spawns NO agents: it feeds synthetic PreToolUse JSON on stdin to the two hooks as
subprocesses and asserts their exit codes (0 = allow, 2 = refuse), exactly as the harness would.

PREDICTION CONTRACT (checked below, 18 gates; G15-G18 added 2026-09-24 cycle 73):
  G15-G16 under CYCLE_SESSION=1 a SendMessage to an agent id / `log-reader` is REFUSED (exit 2)
  G17     without CYCLE_SESSION (the interactive chat) the same SendMessage is ALLOWED
  G18     under CYCLE_SESSION=1 a SendMessage to `main` is ALLOWED
  G1-G8   dispatches 1..8 of `material` / `log-reader` are ALLOWED (exit 0) and the counter reaches 8
  G9      the 9th dispatch is REFUSED (exit 2) with "CYCLE DISPATCH CAP"
  G10     an uncounted subagent_type (`Explore`) is ALLOWED even at the cap, and does not move the counter
  G11     a non-Agent tool name is ALLOWED (the hook only speaks about Agent/Task)
  G12     in a FRESH session, `py tools/bgrun.py ... -- py tools/retrospective.py --cycle 9` is allowed by
          guard_bash AND sets retro_done=true in that session's state file
  G13     the next `material` dispatch in that session is REFUSED with "CYCLE IS CLOSED"
  G14     `retrospective_v1.py` and `grep retrospective.py` do NOT set retro_done (command position, frozen v1)
State files are written under tools/bench/session_<id>.json with throwaway ids and deleted at the end.
Output deliberately avoids the strings bgrun/guard_peer scan for (`rc=<n>`, a line starting with FAIL).
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
HOOKS = os.path.join(ROOT, "tools", "hooks")
GUARD_SESSION = os.path.join(HOOKS, "guard_session.py")
GUARD_BASH = os.path.join(HOOKS, "guard_bash.py")
sys.path.insert(0, HOOKS)
import guard_session  # noqa: E402

SID_A = "selftest-gs-cap"
SID_B = "selftest-gs-retro"
SID_C = "selftest-gs-nomark"

RESULTS = []


def gate(label, ok, detail=""):
    RESULTS.append((label, bool(ok)))
    print("  %-4s %-46s %s" % ("ok" if ok else "BAD", label, detail), flush=True)


def call(script, payload):
    p = subprocess.run([sys.executable, script], input=json.dumps(payload), text=True,
                       capture_output=True, encoding="utf-8", errors="replace", timeout=60)
    return p.returncode, (p.stderr or "")


def agent_call(sid, sub):
    return call(GUARD_SESSION, {"session_id": sid, "tool_name": "Agent",
                                "tool_input": {"subagent_type": sub, "prompt": "x"}})


def bash_call(sid, cmd):
    return call(GUARD_BASH, {"session_id": sid, "tool_name": "Bash",
                             "tool_input": {"command": cmd, "run_in_background": True}})


def cleanup():
    for sid in (SID_A, SID_B, SID_C):
        p = guard_session.state_path(guard_session.SAFE_RE.sub("_", sid))
        if os.path.isfile(p):
            os.remove(p)


def main():
    cleanup()
    env_off = os.environ.pop("BENCH_CELL", None)   # this test IS the thing under test
    if env_off is not None:
        print("  note: BENCH_CELL was set and is ignored for this run", flush=True)

    # G1-G8 : the cap is 8, so eight dispatches pass
    for i in range(1, 9):
        rc, _ = agent_call(SID_A, "material" if i % 2 else "log-reader")
        gate("G%d dispatch %d allowed" % (i, i), rc == 0, "exit %d" % rc)
    st = guard_session.load(guard_session.SAFE_RE.sub("_", SID_A))
    # G9 : the ninth is refused
    rc, err = agent_call(SID_A, "material")
    gate("G9 ninth dispatch refused", rc == 2 and "CYCLE DISPATCH CAP" in err,
         "exit %d, counter %s" % (rc, st.get("dispatches")))
    # G10 : an uncounted agent type passes even at the cap and does not move the counter
    rc, _ = agent_call(SID_A, "Explore")
    after = guard_session.load(guard_session.SAFE_RE.sub("_", SID_A))
    gate("G10 uncounted subagent_type allowed", rc == 0 and after.get("dispatches") == 8,
         "exit %d, counter %s" % (rc, after.get("dispatches")))
    # G11 : not an Agent call at all
    rc, _ = call(GUARD_SESSION, {"session_id": SID_A, "tool_name": "Bash",
                                 "tool_input": {"command": "echo hi"}})
    gate("G11 non-Agent tool allowed", rc == 0, "exit %d" % rc)

    # G12 : the retrospective is allowed and closes the cycle
    rc, err = bash_call(SID_B, "py tools/bgrun.py --max-min 10 --log tools/bench/retro.log "
                               "-- py tools/retrospective.py --cycle 9")
    stb = guard_session.load(guard_session.SAFE_RE.sub("_", SID_B))
    gate("G12 retrospective allowed and recorded", rc == 0 and stb.get("retro_done") is True,
         "exit %d, retro_done %s" % (rc, stb.get("retro_done")))
    # G13 : and the next material dispatch in that session is refused
    rc, err = agent_call(SID_B, "material")
    gate("G13 dispatch after retrospective refused", rc == 2 and "CYCLE IS CLOSED" in err, "exit %d" % rc)

    # G14 : v1 and a mere mention do not close anything
    bash_call(SID_C, "py tools/retrospective_v1.py --cycle 9")
    bash_call(SID_C, "grep -n retrospective.py tools/hooks/guard_bash.py")
    stc = guard_session.load(guard_session.SAFE_RE.sub("_", SID_C))
    gate("G14 v1 and grep do not close the cycle", stc.get("retro_done") is False,
         "retro_done %s" % stc.get("retro_done"))

    # G15-G18 : SendMessage resume refused in a cycle session only (violation-decisions 2026-09-24 05:54)
    def send(to, cycle):
        env = dict(os.environ)
        env.pop("CYCLE_SESSION", None)
        if cycle:
            env["CYCLE_SESSION"] = "1"
        p = subprocess.run([sys.executable, GUARD_SESSION], input=json.dumps(
            {"session_id": SID_C, "tool_name": "SendMessage", "tool_input": {"to": to, "message": "go on"}}),
            text=True, capture_output=True, encoding="utf-8", errors="replace", timeout=60, env=env)
        return p.returncode, p.stderr or ""
    rc, err = send("a1b2c3d4-material", True)
    gate("G15 SendMessage to an agent refused in cycle", rc == 2 and "NEW foreground Agent" in err, "exit %d" % rc)
    rc, err = send("log-reader", True)
    gate("G16 SendMessage to log-reader refused in cycle", rc == 2, "exit %d" % rc)
    rc, _ = send("a1b2c3d4-material", False)
    gate("G17 interactive chat SendMessage untouched", rc == 0, "exit %d" % rc)
    rc, _ = send("main", True)
    gate("G18 SendMessage to main allowed in cycle", rc == 0, "exit %d" % rc)

    cleanup()
    good = sum(1 for _, ok in RESULTS if ok)
    print("SUMMARY %d/%d gates pass" % (good, len(RESULTS)), flush=True)
    return 0 if good == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
