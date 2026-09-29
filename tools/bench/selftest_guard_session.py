r"""Self-test for tools/hooks/guard_session.py and guard_bash.py's retrospective marker.

Touches NO LabVIEW, spawns NO agents: it feeds synthetic PreToolUse JSON on stdin to the two hooks as
subprocesses and asserts their exit codes (0 = allow, 2 = refuse), exactly as the harness would.

PREDICTION CONTRACT (checked below, 18 gates; G15-G18 added 2026-09-24 cycle 73):
  G15-G16 under CYCLE_SESSION=1 a SendMessage to an agent id / `log-reader` is REFUSED (exit 2)
  G17     without CYCLE_SESSION (the interactive chat) the same SendMessage is ALLOWED and COUNTED (card chat-L2)
  G19-G20 a SendMessage resume past the cap / after the retrospective is REFUSED (card chat-L2; 20 gates)
  G18     under CYCLE_SESSION=1 a SendMessage to `main` is ALLOWED
  G1-G6   dispatches 1..6 of material / its Fable rungs / log-reader are ALLOWED; G7 the counter reaches 6
  G8-G9   the 7th dispatch (material or a Fable rung) is REFUSED with "CYCLE DISPATCH CAP" + "WRITE NEXT AND EXIT"
          (card chat-N1 (4b): cap 8 -> 6)
  G10     an uncounted subagent_type (`Explore`) is ALLOWED even at the cap, and does not move the counter
  G11     a non-Agent tool name is ALLOWED (the hook only speaks about Agent/Task)
  G12     in a FRESH session, `py tools/bgrun.py ... -- py tools/retrospective.py --cycle 9` is allowed by
          guard_bash AND sets retro_done=true in that session's state file
  G13     the next `material` dispatch in that session is REFUSED with "CYCLE IS CLOSED"
  G14     `retrospective_v1.py` and `grep retrospective.py` do NOT set retro_done (command position, frozen v1)
  SCOPE (f), 2026-09-29 (user "수정안대로 진행하도록"): G1-G13 run under CYCLE_SESSION=1 (the cap and the retrospective
  close bind runner cycle sessions only); G19/G20 re-pinned: in the chat they are ALLOWED.
  G21     chat: 8 dispatches allowed and counted (no cap)
  G22     chat: a dispatch after a turn above CHAT_CONTEXT_LIMIT is REFUSED ("CHAT CONTEXT")
  G23     chat: unreadable transcript fails open      G24 chat after a retro mark allowed
  G25     a cycle session ignores the chat context rule (its cap still refuses)
  G26     cycle: Workflow counts as a dispatch (7th refused)   G27 chat: Workflow bound by the context rule only
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
SID_D = "selftest-gs-chat"
SID_E = "selftest-gs-wfcycle"

RESULTS = []


def gate(label, ok, detail=""):
    RESULTS.append((label, bool(ok)))
    print("  %-4s %-46s %s" % ("ok" if ok else "BAD", label, detail), flush=True)


def call(script, payload, cycle=False):
    env = dict(os.environ)
    env.pop("CYCLE_SESSION", None)
    if cycle:
        env["CYCLE_SESSION"] = "1"
    p = subprocess.run([sys.executable, script], input=json.dumps(payload), text=True,
                       capture_output=True, encoding="utf-8", errors="replace", timeout=60, env=env)
    return p.returncode, (p.stderr or "")


def agent_call(sid, sub, cycle=True, transcript=None):
    payload = {"session_id": sid, "tool_name": "Agent", "tool_input": {"subagent_type": sub, "prompt": "x"}}
    if transcript:
        payload["transcript_path"] = transcript
    return call(GUARD_SESSION, payload, cycle=cycle)


def fake_transcript(tokens):
    """A transcript JSONL whose last assistant turn used `tokens` input tokens (split over the three fields)."""
    p = os.path.join(os.environ.get("TEMP", "."), "gs_selftest_transcript_%d_%d.jsonl" % (os.getpid(), tokens))
    with open(p, "w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "assistant", "message": {"usage": {"input_tokens": 1}}}) + "\n")
        f.write(json.dumps({"type": "user", "message": {"content": "hi"}}) + "\n")
        f.write(json.dumps({"type": "assistant", "message": {"usage": {
            "input_tokens": 10, "cache_creation_input_tokens": 90, "cache_read_input_tokens": tokens - 100}}}) + "\n")
    return p


def bash_call(sid, cmd):
    return call(GUARD_BASH, {"session_id": sid, "tool_name": "Bash",
                             "tool_input": {"command": cmd, "run_in_background": True}})


def cleanup():
    for sid in (SID_A, SID_B, SID_C, SID_D, SID_E):
        p = guard_session.state_path(guard_session.SAFE_RE.sub("_", sid))
        if os.path.isfile(p):
            os.remove(p)


def main():
    cleanup()
    env_off = os.environ.pop("BENCH_CELL", None)   # this test IS the thing under test
    # card chat-L2: isolate guard_bash's NEXT gate from the LIVE tools/bench/next_snapshot.md5 / next.json (G12/G13
    # failed in chat-L1 because the live pair hashed equal). A snapshot path that does not exist = "no runner
    # snapshot", which is the interactive-session case this test models.
    os.environ["NEXT_SNAPSHOT"] = os.path.join(os.environ.get("TEMP", "."), "gs_selftest_no_snapshot_%d.md5" % os.getpid())
    os.environ["NEXT_JSON"] = os.path.join(os.environ.get("TEMP", "."), "gs_selftest_no_next_%d.json" % os.getpid())
    if env_off is not None:
        print("  note: BENCH_CELL was set and is ignored for this run", flush=True)

    # G1-G6 : the cap is 6 (card chat-N1 (4b), was 8), so six dispatches pass; a Fable rung counts too
    kinds = ["material", "log-reader", "material-fable-low", "material", "material-fable-medium", "log-reader"]
    for i in range(1, 7):
        rc, _ = agent_call(SID_A, kinds[i - 1])
        gate("G%d dispatch %d (%s) allowed" % (i, i, kinds[i - 1]), rc == 0, "exit %d" % rc)
    st = guard_session.load(guard_session.SAFE_RE.sub("_", SID_A))
    gate("G7 counter reached 6 (Fable rungs counted)", st.get("dispatches") == 6, "counter %s" % st.get("dispatches"))
    # G9 : the seventh is refused, and the refusal says write NEXT and exit
    rc, err = agent_call(SID_A, "material")
    gate("G9 seventh dispatch refused", rc == 2 and "CYCLE DISPATCH CAP" in err and "WRITE NEXT AND EXIT" in err,
         "exit %d, counter %s" % (rc, st.get("dispatches")))
    rc, err = agent_call(SID_A, "material-fable-low")
    gate("G8 seventh as a Fable rung refused too", rc == 2 and "CYCLE DISPATCH CAP" in err, "exit %d" % rc)
    # G10 : an uncounted agent type passes even at the cap and does not move the counter
    rc, _ = agent_call(SID_A, "Explore")
    after = guard_session.load(guard_session.SAFE_RE.sub("_", SID_A))
    gate("G10 uncounted subagent_type allowed", rc == 0 and after.get("dispatches") == 6,
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
    def send(to, cycle, sid=SID_C):
        env = dict(os.environ)
        env.pop("CYCLE_SESSION", None)
        if cycle:
            env["CYCLE_SESSION"] = "1"
        p = subprocess.run([sys.executable, GUARD_SESSION], input=json.dumps(
            {"session_id": sid, "tool_name": "SendMessage", "tool_input": {"to": to, "message": "go on"}}),
            text=True, capture_output=True, encoding="utf-8", errors="replace", timeout=60, env=env)
        return p.returncode, p.stderr or ""
    rc, err = send("a1b2c3d4-material", True)
    gate("G15 SendMessage to an agent refused in cycle", rc == 2 and "NEW foreground Agent" in err, "exit %d" % rc)
    rc, err = send("log-reader", True)
    gate("G16 SendMessage to log-reader refused in cycle", rc == 2, "exit %d" % rc)
    n0 = guard_session.load(guard_session.SAFE_RE.sub("_", SID_C)).get("dispatches", 0)
    rc, _ = send("a1b2c3d4-material", False)
    n1 = guard_session.load(guard_session.SAFE_RE.sub("_", SID_C)).get("dispatches", 0)
    gate("G17 interactive SendMessage allowed AND counted", rc == 0 and n1 == n0 + 1,
         "exit %d, counter %s -> %s" % (rc, n0, n1))
    rc, _ = send("main", True)
    gate("G18 SendMessage to main allowed in cycle", rc == 0, "exit %d" % rc)
    # G19-G20 (re-pinned 2026-09-29, scope (f)): in the CHAT a SendMessage resume past 6 / after a retrospective mark
    # is ALLOWED - the cap and the retrospective close bind runner cycle sessions only
    rc, err = send("a1b2c3d4-material", False, sid=SID_A)
    gate("G19 chat SendMessage past 6 allowed", rc == 0, "exit %d" % rc)
    rc, err = send("a1b2c3d4-material", False, sid=SID_B)
    gate("G20 chat SendMessage after retro mark allowed", rc == 0, "exit %d" % rc)

    # G21-G27 : scope (f), user 2026-09-29 "수정안대로 진행하도록"
    small, big = fake_transcript(200_000), fake_transcript(600_000)
    for i in range(1, 9):
        rc, _ = agent_call(SID_D, "material", cycle=False, transcript=small)
        if rc != 0:
            break
    std = guard_session.load(guard_session.SAFE_RE.sub("_", SID_D))
    gate("G21 chat: 8 dispatches allowed and counted", rc == 0 and std.get("dispatches") == 8,
         "exit %d, counter %s" % (rc, std.get("dispatches")))
    rc, err = agent_call(SID_D, "material", cycle=False, transcript=big)
    gate("G22 chat over the context limit refused", rc == 2 and "CHAT CONTEXT" in err, "exit %d" % rc)
    rc, _ = agent_call(SID_D, "material", cycle=False, transcript=os.path.join(ROOT, "no_such_transcript.jsonl"))
    gate("G23 chat, unreadable transcript -> fail open", rc == 0, "exit %d" % rc)
    rc, _ = agent_call(SID_B, "material", cycle=False, transcript=small)
    gate("G24 chat after a retro mark allowed", rc == 0, "exit %d" % rc)
    rc, err = agent_call(SID_A, "material", cycle=True, transcript=big)
    gate("G25 cycle session ignores the chat context rule (cap refuses)", rc == 2 and "CYCLE DISPATCH CAP" in err,
         "exit %d" % rc)

    def wf(sid, cycle, transcript=None):
        payload = {"session_id": sid, "tool_name": "Workflow", "tool_input": {"script": "export const meta = {}"}}
        if transcript:
            payload["transcript_path"] = transcript
        return call(GUARD_SESSION, payload, cycle=cycle)
    for i in range(1, 7):
        rc, _ = wf(SID_E, True)
    rc7, err7 = wf(SID_E, True)
    gate("G26 cycle: Workflow counted, 7th refused", rc == 0 and rc7 == 2 and "CYCLE DISPATCH CAP" in err7,
         "exit %d / %d" % (rc, rc7))
    rc, _ = wf(SID_D, False, small)
    rc2, err2 = wf(SID_D, False, big)
    gate("G27 chat: Workflow allowed under the limit, refused over it", rc == 0 and rc2 == 2 and "CHAT CONTEXT" in err2,
         "exit %d / %d" % (rc, rc2))
    for p in (small, big):
        try:
            os.remove(p)
        except OSError:
            pass

    cleanup()
    good = sum(1 for _, ok in RESULTS if ok)
    print("SUMMARY %d/%d gates pass" % (good, len(RESULTS)), flush=True)
    return 0 if good == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
