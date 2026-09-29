"""decbench cell guard (card chat-B1) - PreToolUse hook installed ONLY in a decbench worktree (<wt>/.decbench/).

Reuses matbench's cell_guard (copied beside it) for the LabVIEW/GUI/hardware/peer bans and the call log, and adds the
decision-bench isolation a READ-ONLY question needs: no git at all (git history would reveal the answer), no
sub-agents / web / MCP, reads only inside the worktree or the cell's own scratch dir, writes only in the scratch dir,
and no command or path that names the main checkout (V6_ParallelLoop) or the memory store (.claude/projects).
Env set by decbench.py: MATBENCH_WT (worktree), MATBENCH_LOG (this cell's calls.jsonl), DECBENCH_SCRATCH.
Exit 2 = refuse, 0 = allow.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cell_guard as CG  # noqa: E402

WT = os.path.normcase(os.path.abspath(CG.WT))
SCR = os.path.normcase(os.path.abspath(os.environ.get("DECBENCH_SCRATCH") or os.path.join(CG.TEMP, "db_scratch")))
BAN_TOOL = re.compile(r"^(Agent|Task|WebSearch|WebFetch|Skill|Artifact\w*|mcp__.*)$")
BAN_TXT = re.compile(r"\bgit\b|V6_ParallelLoop|\.claude[\\/]+projects|[\\/]db[\\/]+scratch[\\/]", re.I)
READ_TOOLS = ("Read", "Grep", "Glob", "LS")


def decide(payload):
    tool = payload.get("tool_name") or ""
    ti = payload.get("tool_input") or {}
    if BAN_TOOL.match(tool):
        return "decbench: tool %s is not allowed in a read-only benchmark cell" % tool
    if tool in ("Bash", "PowerShell"):
        cmd = ti.get("command", "") or ""
        low = cmd
        for s in {SCR, os.environ.get("DECBENCH_SCRATCH") or SCR}:
            for form in (s, s.replace("\\", "/")):
                low = re.sub(re.escape(form), "", low, flags=re.I)
        m = BAN_TXT.search(low)
        if m:
            return "decbench: command names %r (no git, no main checkout, no memory store)" % m.group(0)
        return CG.check_cmd(cmd)
    if tool in READ_TOOLS:
        p = ti.get("file_path") or ti.get("path") or ""
        if not p:
            return None
        p = p if os.path.isabs(p) else os.path.join(WT, p)
        if not (CG.inside(p, WT) or CG.inside(p, SCR)):
            return "decbench: read only inside the checkout (got %s)" % p
        return None
    if tool in CG.WRITE_TOOLS:
        fp = ti.get("file_path") or ti.get("notebook_path") or ""
        fp = fp if os.path.isabs(fp) else os.path.join(WT, fp)
        if not CG.inside(fp, SCR):
            return "decbench: read-only cell - write only in the scratch dir %s" % SCR
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:           # noqa: BLE001
        return 0
    try:
        why = decide(payload)
    except Exception as e:      # noqa: BLE001  (a guard crash refuses)
        why = "dec_guard error %s: %s" % (type(e).__name__, e)
    ti = payload.get("tool_input") or {}
    CG.log({"tool": payload.get("tool_name"),
            "cmd": str(ti.get("command") or ti.get("file_path") or ti.get("path") or ti.get("pattern") or "")[:300],
            "decision": "REFUSE" if why else "ALLOW", "why": why})
    if why:
        sys.stderr.write("BLOCKED by decbench dec_guard: %s\n" % why)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
