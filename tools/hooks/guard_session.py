r"""PreToolUse hook (Agent): ONE SESSION = ONE CYCLE, mechanically.

CLAUDE.md section 3 item 2 ("Session = one cycle - ENFORCED BY A RUNNER", user decision 2026-09-17,
"2번으로 가자. Opus max", after a 15-hour session): a judgement session reads STATUS.md + the current plan,
runs ONE cycle (delegate -> decide -> retrospective -> STATUS NEXT) and EXITS; `tools/cycle_runner.py` spawns
the next one fresh. The failure mode this hook removes is the one the user actually saw: a session that keeps
going after its cycle is finished, so the context grows all night and the expensive model re-reads it every turn.

Prose cannot enforce "now stop" on the session that is enjoying itself. So two refusals, both counted in a file:

  (a) DISPATCH CAP. The 9th `material` / `log-reader` dispatch in one session is refused. Eight is what a cycle
      has cost when it was run well; past that the session is carrying a second cycle.
  (b) AFTER THE RETROSPECTIVE, THE CYCLE IS CLOSED. Once `tools/retrospective.py` has run in this session
      (recorded by `tools/hooks/guard_bash.py`, which sees the command), any further material dispatch is
      refused. A retrospective reviews a cycle; work done after it belongs to a cycle nobody reviewed.
  (c) NO SendMessage RESUME in a cycle session (CYCLE_SESSION=1), 2026-09-24 - see send_message_refusal().

STATE: `tools/bench/session_<session_id>.json` = {"dispatches": n, "retro_done": bool, ...}. A file, not a
memory - CLAUDE.md: "a rule whose counter is my memory is not a rule at all". `.json`, so no log gate globs it.

BENCH_CELL set => exit 0 immediately (same exemption lv_stallcheck.ps1 uses): benchmark cells spawned by the
harness dispatch agents by construction and are not cycles.

Exit code 2 = block (stderr goes back to Claude); 0 = allow.
Self-test: `py tools/bench/selftest_guard_session.py` (synthetic stdin JSON, no LabVIEW, no agents spawned).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BENCH = os.path.join(ROOT, "tools", "bench")

MAX_DISPATCHES = 8
# The two agents a cycle's material work goes through (.claude/agents/). Every other subagent_type - the peer
# roles, Explore, a one-off general-purpose search - is not a cycle's work and is never counted or refused.
COUNTED = {"material", "log-reader"}
# This harness names the sub-agent tool `Agent`; older Claude Code builds name it `Task`. Matching both costs
# nothing and stops the hook from becoming silently inert after an upgrade (the defect guard_cycle's PRIOR_ART_RE
# had for a day: a gate that never fires looks exactly like a gate that passes).
AGENT_TOOLS = ("Agent", "Task")
SAFE_RE = re.compile(r"[^A-Za-z0-9._-]")


def session_id(data=None):
    sid = ""
    if isinstance(data, dict):
        sid = str(data.get("session_id") or "")
    sid = sid or os.environ.get("CLAUDE_SESSION_ID") or "unknown"
    return SAFE_RE.sub("_", sid)[:80]


def state_path(sid):
    return os.path.join(BENCH, "session_%s.json" % sid)


def load(sid):
    try:
        with open(state_path(sid), encoding="utf-8") as f:
            d = json.load(f)
        if isinstance(d, dict):
            d.setdefault("dispatches", 0)
            d.setdefault("retro_done", False)
            return d
    except (OSError, ValueError):
        pass
    return {"dispatches": 0, "retro_done": False}


def save(sid, d):
    try:
        os.makedirs(BENCH, exist_ok=True)
        with open(state_path(sid), "w", encoding="utf-8") as f:
            json.dump(d, f)
    except OSError:
        pass


def mark_retro_done(sid):
    """Called by tools/hooks/guard_bash.py when it sees the retrospective being run in this session.

    It lives here, not there, so there is ONE definition of the session state file (logclass.py's lesson:
    a classifier that three files each maintain separately is three classifiers)."""
    d = load(sid)
    if not d.get("retro_done"):
        d["retro_done"] = True
        save(sid, d)
    return d


def send_message_refusal(data):
    """(c) NO RESUME BY SendMessage IN A CYCLE SESSION (docs/violation-decisions.md "repeated-failure-class -
    2026-09-24 05:54"; cycle 71 lost 57 min: a judgement session resumed a material agent with SendMessage, which
    runs it in the BACKGROUND, then polled build logs after that agent had already stopped on a gate refusal).

    Scope: CYCLE_SESSION=1 only (the interactive chat is untouched). The target's subagent_type is NOT visible to a
    PreToolUse hook - the Agent tool returns the agent id only after the spawn, and a cycle session's in-process
    agents are the material/log-reader ones by construction - so every SendMessage in a cycle session is refused
    except to "main" (a background agent reporting to its parent). Returns the refusal text or ''."""
    if data.get("tool_name") != "SendMessage" or not os.environ.get("CYCLE_SESSION"):
        return ""
    to = str((data.get("tool_input") or {}).get("to") or "").strip()
    if to.lower() == "main":
        return ""
    return ("BLOCKED by tools/hooks/guard_session.py: NO SendMessage RESUME IN A CYCLE SESSION (to=%r).\n\n"
            "SendMessage resumes a material/log-reader agent in the BACKGROUND; cycle 71 then polled logs for 57 min\n"
            "after that agent had stopped (docs/violation-decisions.md, repeated-failure-class 2026-09-24 05:54).\n"
            "Dispatch a NEW foreground Agent (subagent_type material or log-reader) with the full brief instead;\n"
            "it blocks until it returns.\n" % to)


def main():
    if os.environ.get("BENCH_CELL"):
        return 0
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    why = send_message_refusal(data)
    if why:
        sys.stderr.write(why)
        return 2
    ti = data.get("tool_input") or {}
    if data.get("tool_name") == "SendMessage":
        # card chat-L2: a SendMessage RESUME is a dispatch - it restarts a material/log-reader agent's work, so it
        # counts against MAX_DISPATCHES and is refused after the retrospective like a new Agent call. The target's
        # subagent_type is not visible here (see send_message_refusal), so every resume counts except to "main".
        if str(ti.get("to") or "").strip().lower() in ("", "main"):
            return 0
        sub = "sendmessage-resume"
    elif data.get("tool_name") in AGENT_TOOLS:
        sub = str(ti.get("subagent_type") or "").strip().lower()
        if sub not in COUNTED:
            return 0
    else:
        return 0
    sid = session_id(data)
    st = load(sid)
    if st.get("retro_done"):
        sys.stderr.write(
            "BLOCKED by tools/hooks/guard_session.py: THIS SESSION'S CYCLE IS CLOSED BY ITS RETROSPECTIVE.\n"
            "  session state : %s (dispatches=%s, retro_done=true)\n\n"
            "CLAUDE.md section 3 item 2: a session runs ONE cycle - delegate, decide, run the retrospective,\n"
            "write STATUS.md's NEXT line, stop. Work started after the retrospective belongs to a cycle that\n"
            "nobody reviewed, and it is what makes a session grow all night.\n"
            "Write the NEXT line and end the session; `tools/cycle_runner.py` spawns the next cycle fresh.\n"
            % (os.path.relpath(state_path(sid), ROOT), st.get("dispatches")))
        return 2
    n = int(st.get("dispatches", 0)) + 1
    if n > MAX_DISPATCHES:
        sys.stderr.write(
            "BLOCKED by tools/hooks/guard_session.py: CYCLE DISPATCH CAP REACHED (%d material/log-reader "
            "dispatches).\n"
            "  session state : %s\n\n"
            "Eight dispatches is a cycle's worth of material work; past that this session is carrying a second\n"
            "cycle, which CLAUDE.md section 3 item 2 forbids. Close this one: run the retrospective if it is\n"
            "owed, write STATUS.md's NEXT line, and let the runner start a fresh session - a fresh session beats\n"
            "compacting a long one.\n"
            % (MAX_DISPATCHES, os.path.relpath(state_path(sid), ROOT)))
        return 2
    st["dispatches"] = n
    st["last_subagent"] = sub
    save(sid, st)
    return 0


if __name__ == "__main__":
    sys.exit(main())
