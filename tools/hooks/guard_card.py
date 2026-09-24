"""PreToolUse hook (every tool except Bash/PowerShell, which guard_bash.py covers by calling the same function):
session protocol v1, C2 - a card-carrying sub-agent is BOUND to its task/1 card and every call is checked against the
card's flags (docs/session-protocol.md, "Flags and who enforces them" + the MEASURED binding rule).

The logic lives in ONE place, `tools/protocol.py hook_decision()`; this file is only the stdin/exit-code shell so the
same decision can be registered for Edit/Write/NotebookEdit (write + status_edit flags) and for the read tools (an
unbound card agent is refused everything except `py tools/protocol.py bind <card>`).

Registration (in .claude/settings.json, PreToolUse):
    {"matcher": "Edit|Write|NotebookEdit|MultiEdit|Read|Glob|Grep|WebFetch|WebSearch|Agent|Task",
     "hooks": [{"type": "command", "command": "py \"<root>/tools/hooks/guard_card.py\"", "timeout": 10}]}
The main session (payload without agent_id) and agent types that take no card are never affected.
Exit 2 = refuse (stderr goes back to the agent); 0 = allow. A crash here allows (a broken guard must not wedge
every session) and is logged.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
LOG = os.path.join(TOOLS, "bench", "cards", "guard_card.log")


def log(line):
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write("%s | %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), line.replace("\n", " ")[:400]))
    except OSError:
        pass


def decide(payload):
    """(exit_code, message). Shared by main() and guard_bash.py."""
    try:
        if TOOLS not in sys.path:
            sys.path.insert(0, TOOLS)
        import protocol
        ok, msg = protocol.hook_decision(payload)
    except Exception as e:      # noqa: BLE001
        log("GUARD ERROR (allowed) %s: %s" % (type(e).__name__, e))
        return 0, None
    if msg:
        log("%s %s %s | %s" % ("ALLOW" if ok else "REFUSE", payload.get("agent_type"), payload.get("agent_id"), msg))
    return (0 if ok else 2), msg


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:           # noqa: BLE001
        return 0
    if payload.get("tool_name") in ("Bash", "PowerShell"):
        return 0                # guard_bash.py makes this decision for shell tools (one decision per call)
    rc, msg = decide(payload)
    if rc:
        sys.stderr.write("BLOCKED by tools/hooks/guard_card.py (session protocol v1): %s\n" % msg)
    return rc


if __name__ == "__main__":
    sys.exit(main())
