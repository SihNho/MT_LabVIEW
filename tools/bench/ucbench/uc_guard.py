"""ucbench cell guard (card chat-B3) - PreToolUse hook installed ONLY in a ucbench worktree (<wt>/.decbench/).

= decbench's dec_guard (no git, no main checkout, no memory store, reads only in the worktree / scratch, writes only in
the scratch dir, LabVIEW/GUI/hardware/peer bans via matbench cell_guard), plus exactly ONE widening for the UC arm:
the `Workflow` tool is allowed when UCBENCH_ALLOW_WORKFLOW=1 and its script carries no `isolation` option (a
worktree-isolated agent would make git worktrees behind the guard's back). Every call is logged with agent_id /
agent_type, so the probe can show that workflow sub-agents' calls pass through this same hook.
Exit 2 = refuse, 0 = allow.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cell_guard as CG  # noqa: E402
import dec_guard as DG  # noqa: E402

WF_ON = os.environ.get("UCBENCH_ALLOW_WORKFLOW") == "1"


def decide(payload):
    tool = payload.get("tool_name") or ""
    ti = payload.get("tool_input") or {}
    if tool == "Workflow":
        if not WF_ON:
            return "ucbench: Workflow is allowed only in the UC arm"
        blob = json.dumps(ti, ensure_ascii=False)
        if re.search(r"isolation", blob):
            return "ucbench: worktree isolation is not allowed in a benchmark cell (agents stay in this checkout)"
        sp = ti.get("scriptPath") or ""
        if sp and not (CG.inside(sp, DG.WT) or CG.inside(sp, DG.SCR) or CG.inside(sp, CG.TEMP)
                       or ".claude" in sp.replace("\\", "/")):
            return "ucbench: scriptPath outside the cell (got %s)" % sp
        return None
    if tool in DG.READ_TOOLS and own_session_file(payload):
        return None
    return DG.decide(payload)


def own_session_file(payload):
    """smoke 2026-09-29: 12 of 12 refusals were reads of the cell's OWN persisted tool results (large Grep/Read output
    that Claude Code spills to ~/.claude/projects/<cwd>/<session_id>/... or %TEMP%/claude/<cwd>/<session_id>/...).
    Allowed only under those two roots AND only when the path carries THIS cell's session_id (sub-agents share the
    parent's), so an arm can never read another arm's session files of the same task worktree."""
    ti = payload.get("tool_input") or {}
    p, sid = ti.get("file_path") or ti.get("path") or "", payload.get("session_id") or ""
    if not p or len(sid) < 8:
        return False
    roots = [os.path.join(os.path.expanduser("~"), ".claude", "projects"), os.path.join(CG.TEMP, "claude")]
    np_ = os.path.normcase(os.path.abspath(p))
    return any(CG.inside(np_, os.path.normcase(os.path.abspath(r))) for r in roots) and sid.lower() in np_.lower()


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:           # noqa: BLE001
        return 0
    try:
        why = decide(payload)
    except Exception as e:      # noqa: BLE001  (a guard crash refuses)
        why = "uc_guard error %s: %s" % (type(e).__name__, e)
    ti = payload.get("tool_input") or {}
    CG.log({"tool": payload.get("tool_name"), "agent_id": payload.get("agent_id"),
            "agent_type": payload.get("agent_type"),
            "cmd": str(ti.get("command") or ti.get("file_path") or ti.get("path") or ti.get("pattern")
                       or (ti.get("script") or "")[:120] or "")[:300],
            "decision": "REFUSE" if why else "ALLOW", "why": why})
    if why:
        sys.stderr.write("BLOCKED by ucbench uc_guard: %s\n" % why)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
