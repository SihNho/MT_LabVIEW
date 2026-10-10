# ---
# labview: none
# hardware: none
# ---
"""adapt_codex.py - Codex CLI PreToolUse hook -> guardcore.judge -> Codex deny JSON (card chat-X2).

Configured in the project layer `.codex/hooks.json` (PreToolUse, no matcher = every tool). Facts it relies on (installed
Codex 0.162.0; sources in docs/guardcore.md): stdin JSON {session_id, turn_id, cwd, hook_event_name, model,
permission_mode, tool_name, tool_input, tool_use_id}; shell commands arrive as tool_name "Bash" with tool_input.command;
file edits arrive as tool_name "apply_patch" with the patch text somewhere in tool_input; a deny is ONE JSON object on
stdout {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
"permissionDecisionReason": "..."}} with exit 0 (the exit-2 path was reported to FAIL OPEN on Windows in 0.144.x);
any other non-zero exit is a hook failure that Codex logs and SKIPS (fail open) - so this file never exits non-zero and
turns its own crash into a deny (fail closed).

apply_patch: the patch body is parsed into per-file {op, old, new} - Add / Delete / Update / Update+Move to (rename) -
and guardcore checks BOTH paths of a rename. A body that yields no file is denied (guardcore R6).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import guardcore  # noqa: E402

SHELL_TOOLS = {"bash", "shell", "shell_command", "exec_command", "local_shell", "launch-process", "powershell"}
PATCH_TOOLS = {"apply_patch", "applypatch", "apply-patch"}
WRITE_TOOLS = {"write": "Write", "edit": "Edit", "multiedit": "MultiEdit"}
RAW_LOG = os.environ.get("GUARDCORE_CODEX_RAW")      # set only for a capture run: every payload appended as JSON

BEGIN_RE = re.compile(r"\*\*\*\s*Begin Patch")
HDR_RE = re.compile(r"^\*\*\*\s*(Add|Delete|Update) File:\s*(.+?)\s*$")
MOVE_RE = re.compile(r"^\*\*\*\s*Move to:\s*(.+?)\s*$")


def find_patch(obj):
    """The first string inside `obj` (dict/list/str, any depth) that contains '*** Begin Patch', else None."""
    if isinstance(obj, str):
        return obj if BEGIN_RE.search(obj) else None
    if isinstance(obj, dict):
        obj = list(obj.values())
    if isinstance(obj, (list, tuple)):
        for v in obj:
            r = find_patch(v)
            if r:
                return r
    return None


def parse_patch(body):
    """[{op, old, new, content}] from an apply_patch body; [] when no file header is found.
    Add -> op add (new); Delete -> op delete (old); Update -> op modify (old = new); Update + Move to -> op rename."""
    out, cur = [], None
    for line in (body or "").splitlines():
        m = HDR_RE.match(line)
        if m:
            kind, p = m.group(1), m.group(2)
            cur = {"add": {"op": "add", "old": None, "new": p, "content": []},
                   "delete": {"op": "delete", "old": p, "new": None, "content": None},
                   "update": {"op": "modify", "old": p, "new": p, "content": None}}[kind.lower()]
            out.append(cur)
            continue
        m = MOVE_RE.match(line)
        if m and cur is not None and cur["op"] == "modify":
            cur["op"], cur["new"] = "rename", m.group(1)
            continue
        if cur is not None and cur["op"] == "add" and line.startswith("+"):
            cur["content"].append(line[1:])
    for e in out:
        if isinstance(e.get("content"), list):
            e["content"] = "\n".join(e["content"])
    return out


def _command_of(ti):
    """(command string, shell name). A list command ['powershell', '-Command', x] / ['bash', '-lc', x] yields x."""
    c = ti.get("command", ti.get("cmd", ""))
    shell = "PowerShell" if os.name == "nt" else "Bash"
    if isinstance(c, (list, tuple)):
        parts = [str(x) for x in c]
        head = os.path.basename(parts[0]).lower() if parts else ""
        if head.startswith(("bash", "sh", "zsh")):
            shell = "Bash"
        if head.startswith(("bash", "sh", "zsh", "powershell", "pwsh", "cmd")) and len(parts) >= 2:
            c = parts[-1]
        else:
            c = " ".join(parts)
    c = str(c or "")
    if re.match(r"^\s*(?:bash|sh)(?:\.exe)?\s+-l?c\b", c):
        shell = "Bash"
    return c, shell


def to_event(p):
    """Codex PreToolUse payload -> guardcore event."""
    tool = str(p.get("tool_name") or "")
    ti = p.get("tool_input") if isinstance(p.get("tool_input"), dict) else {"input": p.get("tool_input")}
    meta = {k: p.get(k) for k in ("session_id", "agent_id", "agent_type", "transcript_path", "turn_id") if p.get(k)}
    cwd = p.get("cwd") or guardcore.ROOT
    low = tool.lower()
    if low in SHELL_TOOLS:
        cmd, shell = _command_of(ti)
        tmo = ti.get("timeout_ms", ti.get("timeout"))
        return guardcore.event("codex", tool, "shell", command=cmd, shell=shell,
                               timeout_ms=int(tmo) if isinstance(tmo, (int, float)) else None,
                               cwd=cwd, meta=meta, tool_input=ti)
    if low in PATCH_TOOLS:
        body = find_patch(ti)
        files = parse_patch(body) if body else []
        return guardcore.event("codex", tool, "patch", paths=files if files else None, cwd=cwd, meta=meta,
                               tool_input={"patch_chars": len(body or "")})
    if low in WRITE_TOOLS:
        fp = ti.get("file_path") or ti.get("path") or ""
        kind = "write" if low == "write" else "edit"
        ev = guardcore.event("codex", tool, kind, paths=[{"op": kind, "old": None, "new": fp}] if fp else None,
                             content=ti.get("content"), cwd=cwd, meta=meta, tool_input=ti)
        ev["claude_tool"] = WRITE_TOOLS[low]
        return ev
    return guardcore.event("codex", tool, "other", cwd=cwd, meta=meta, tool_input=ti)


def render(verdict, why):
    """(stdout text, exit code). Allow = empty stdout, exit 0. Deny = the three-field JSON, exit 0."""
    if verdict == "allow":
        return "", 0
    return json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                              "permissionDecisionReason": "BLOCKED by tools/hooks/guardcore.py: " +
                                              (why or "refused")}}), 0


def main():
    raw = sys.stdin.read()
    try:
        p = json.loads(raw)
        if RAW_LOG:
            try:
                with open(RAW_LOG, "a", encoding="utf-8") as f:
                    f.write(json.dumps(p)[:20000] + "\n")
            except OSError:
                pass
        if p.get("hook_event_name") not in (None, "PreToolUse"):
            return 0
        ev = to_event(p)
        verdict, why = guardcore.judge(ev)
        guardcore.log(ev, verdict, why)
    except Exception as e:     # noqa: BLE001 - fail CLOSED: a non-2 crash would be skipped by Codex (fail open)
        verdict, why = "deny", "guardcore adapter error %s: %s (fail closed)" % (type(e).__name__, str(e)[:200])
    out, rc = render(verdict, why)
    if out:
        sys.stdout.write(out)
        sys.stderr.write((why or "")[:2000] + "\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
