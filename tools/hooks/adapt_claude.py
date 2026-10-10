# ---
# labview: none
# hardware: none
# ---
"""adapt_claude.py - Claude Code PreToolUse hook -> guardcore.judge -> exit 2 + stderr (card chat-X2).

NOT WIRED INTO .claude/settings.json (card rule: Claude's live behaviour stays unchanged until this adapter is proven
identical and the chat decides to switch). guardcore.judge runs the very hooks settings.json runs today, per tool name
(guardcore.CHAIN), plus rules that only ADD refusals (R1-R6). The output is Claude's native hook form: exit 2 with the
reason on stderr = block; exit 0 = allow.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import guardcore  # noqa: E402

SHELL = ("Bash", "PowerShell")
WRITE = {"Write": "write", "Edit": "edit", "MultiEdit": "edit", "NotebookEdit": "edit"}
AGENT = ("Agent", "Task", "SendMessage", "Workflow")
READ = ("Read", "Glob", "Grep", "WebFetch", "WebSearch")


def to_event(p):
    """Claude PreToolUse payload -> guardcore event."""
    tool = str(p.get("tool_name") or "")
    ti = p.get("tool_input") or {}
    meta = {k: p.get(k) for k in ("session_id", "agent_id", "agent_type", "transcript_path") if p.get(k)}
    cwd = p.get("cwd") or guardcore.ROOT
    if tool in SHELL:
        return guardcore.event("claude", tool, "shell", command=ti.get("command") or "", shell=tool,
                               timeout_ms=ti.get("timeout"), background=bool(ti.get("run_in_background")),
                               cwd=cwd, meta=meta, tool_input=ti)
    if tool in WRITE:
        fp = ti.get("file_path") or ti.get("notebook_path") or ""
        ev = guardcore.event("claude", tool, WRITE[tool],
                             paths=[{"op": WRITE[tool], "old": None, "new": fp}] if fp else None,
                             content=ti.get("content"), cwd=cwd, meta=meta, tool_input=ti)
        ev["claude_tool"] = tool
        return ev
    if tool in AGENT:
        return guardcore.event("claude", tool, "agent", cwd=cwd, meta=meta, tool_input=ti)
    if tool in READ:
        return guardcore.event("claude", tool, "read", cwd=cwd, meta=meta, tool_input=ti)
    return guardcore.event("claude", tool, "other", cwd=cwd, meta=meta, tool_input=ti)


def render(verdict, why):
    """(stderr text, exit code): Claude's native form."""
    if verdict == "allow":
        return "", 0
    return "BLOCKED by tools/hooks/guardcore.py: %s\n" % (why or "refused"), 2


def main():
    try:
        p = json.load(sys.stdin)
        ev = to_event(p)
        verdict, why = guardcore.judge(ev)
        guardcore.log(ev, verdict, why)
    except Exception as e:     # noqa: BLE001 - fail closed
        verdict, why = "deny", "guardcore adapter error %s: %s (fail closed)" % (type(e).__name__, str(e)[:200])
    err, rc = render(verdict, why)
    if err:
        sys.stderr.write(err)
    return rc


if __name__ == "__main__":
    sys.exit(main())
