# ---
# labview: none
# hardware: none
# ---
"""guardcore.py - ONE judgement for a tool call, shared by the Claude Code and Codex adapters (card chat-X2).

Why (user 2026-10-10 "좋음. 진행하도록", discussion token-efficiency-01 rounds 16, STATE agreed): the project must run
from Claude Code OR Codex sessions with the SAME safety rules. So the rules are not re-written per backend: each adapter
turns its backend's hook JSON into a NORMALIZED EVENT, `judge(event)` decides, and the adapter writes the verdict in its
backend's format (tools/hooks/adapt_claude.py, tools/hooks/adapt_codex.py).

What judge() calls - the EXISTING guards, unchanged, exactly the chain .claude/settings.json runs today:
    shell  (Bash / PowerShell)            -> guard_bash, guard_peer, guard_cycle      (.claude/settings.json PreToolUse)
    write / edit / patch, per file path  -> guard_card (as Write / Edit)             (card flags.write, bound agents)
    read   (Read / Glob / Grep / Web*)    -> guard_card
    agent  (Agent / Task)                 -> guard_card, guard_session
    agent  (SendMessage / Workflow)       -> guard_session
Each is called in-process through its own main() with a Claude-shaped payload on a fake stdin (exit 2 / SystemExit(2) /
a JSON deny = deny; its stderr is the reason). Nothing inside those files is copied here (docs/script-writing.md rule 1).

Plus the rules that until now lived OUTSIDE code or did not exist (each one only ever ADDS a refusal):
  R1 .vi-family write ban (was .claude/settings.json:27-35 deny rules only): add/modify/delete/rename of a LabVIEW
     binary - BOTH the old and the new path of a rename are checked.
  R2 originals path ban (CLAUDE.md rule 1): any write under `zz_LabView VI\\background VIs\\` or to the reference VI.
  R3 runner sessions (env CYCLE_SESSION=1) never write hook files: assign_config.json never_in_runner_globs plus the
     Codex/Claude hook configs (.codex/**, .claude/settings*.json) - user 2026-10-08.
  R4 one LabVIEW at a time at COMMAND level: a command that launches a tools/ script whose scope header says
     labview read|build is refused while a LabVIEW process is already running (CLAUDE.md "one COM client at a time"; the
     card-level check is guard_session's). GUARDCORE_ASSUME_LABVIEW=1 makes the probe say "running" (stricter only).
  R5 unknown tool name: DENIED (fail closed) unless it is on READ_ONLY_TOOLS.
  R6 a patch whose body cannot be parsed into files: DENIED (the adapter sets kind "patch" with paths=None).
  R7 (CANDIDATE cand-shellguard-01, card chat-X9) write/edit/patch of an `agent_write_denied` path
     (.claude/settings.local.json) - every agent write refused; shell writes to protected files are refused by the
     shell chain (guard_bash -> protected_write.shell_decision).

Verification level of the whole thing (said in every report, card chat-X2): EXECUTOR PATH VERIFIED / OUTSIDE THE
EXECUTOR ONLY SECONDARY DEFENCE - command-string checks see text, not what a process does; the final allowance is the
executor's check (bgrun + stage_prerun.check_launch), and this module is the screen in front of it.

Self-test: tools/bench/selftest_guardcore.py (every case in both formats, identical verdicts).
"""
import contextlib
import io
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
for _d in (HERE, TOOLS):
    if _d not in sys.path:
        sys.path.insert(0, _d)

LOG = os.environ.get("GUARDCORE_LOG") or os.path.join(HERE, "guardcore.log")

# R1 - the four extensions of .claude/settings.json:27-35, plus the other LabVIEW binary/library kinds.
VI_FAMILY = (".vi", ".ctl", ".lvlib", ".lvproj", ".vit", ".ctt", ".llb", ".lvclass", ".xctl", ".lvlibp", ".xnode")
# R2 - CLAUDE.md rule 1: the reference VI and everything in `zz_LabView VI\background VIs\`.
ORIGINALS_RE = re.compile(r"(?:^|[\\/])background VIs(?:[\\/]|$)|Min_Track N beads 4\.5_KimLabMTroom_3StateClamping",
                          re.I)
# R3 - extra hook-config globs beside assign_config.json's never_in_runner_globs.
RUNNER_EXTRA_GLOBS = [".codex/**", ".claude/settings.json", ".claude/settings.local.json"]
ASSIGN_CONFIG = os.path.join(TOOLS, "bench", "assign", "assign_config.json")
# R5 - tools that cannot change anything. Everything else not handled by a kind is refused.
READ_ONLY_TOOLS = {
    "Read", "Glob", "Grep", "LS", "WebSearch", "WebFetch", "NotebookRead", "TodoWrite", "ToolSearch",   # Claude
    "update_plan", "view_image", "list_mcp_resources", "list_mcp_resource_templates", "read_mcp_resource",  # Codex
    "web_search", "list_files", "search", "read_file",
    # guardcore-fix-20261010 (Claude + GPT agreed, discussion structure-equal-02 round 4; user: apply on both agreeing):
    # three EXACT read-only Codex names seen refused in guardcore.log - no prefix match; mcp__node_repl__js stays refused
    "mcp__codex_apps__google_drive__fetch", "webrun", "clocksleep",
}
LV_IMAGE = "LabVIEW" + "." + "exe"     # the process image name, read from tasklist only (R4); never started here
KINDS = ("shell","write", "edit", "patch", "agent", "read", "other")

# The Claude PreToolUse chain per Claude tool name (.claude/settings.json "PreToolUse" matchers).
CHAIN = {
    "Bash": ("guard_bash", "guard_peer", "guard_cycle"),
    "PowerShell": ("guard_bash", "guard_peer", "guard_cycle"),
    "Write": ("guard_card",), "Edit": ("guard_card",), "MultiEdit": ("guard_card",), "NotebookEdit": ("guard_card",),
    "Read": ("guard_card",), "Glob": ("guard_card",), "Grep": ("guard_card",),
    "WebFetch": ("guard_card",), "WebSearch": ("guard_card",),
    "Agent": ("guard_card", "guard_session"), "Task": ("guard_card", "guard_session"),
    "SendMessage": ("guard_session",), "Workflow": ("guard_session",),
}


def event(backend, tool_name, kind, command="", shell=None, timeout_ms=None, background=False, paths=(),
          content=None, cwd=None, meta=None, tool_input=None):
    """A normalized event dict. paths = [{"op": add|modify|delete|rename|write|edit, "old": p|None, "new": p|None}]
    (None = unparseable patch, refused by R6). meta = session_id / agent_id / agent_type / transcript_path."""
    if kind not in KINDS:
        kind = "other"
    return {"backend": backend, "tool_name": tool_name, "kind": kind, "command": command or "",
            "shell": shell, "timeout_ms": timeout_ms, "background": bool(background),
            "paths": None if paths is None else list(paths), "content": content, "cwd": cwd or ROOT,
            "meta": dict(meta or {}), "tool_input": dict(tool_input or {})}


# ------------------------------------------------------------------ path rules R1-R3
def _abs(p, cwd=None):
    p = str(p or "")
    return os.path.normpath(p if os.path.isabs(p) else os.path.join(cwd or ROOT, p))


def _all_paths(ev):
    out = []
    for e in ev.get("paths") or []:
        for k in ("old", "new"):
            if e.get(k):
                out.append((e.get("op") or "write", k, _abs(e[k], ev.get("cwd"))))
    return out


def vi_family_ban(ev):
    """R1: reason or None."""
    for op, side, p in _all_paths(ev):
        if p.lower().endswith(VI_FAMILY):
            return ("LabVIEW binary write ban (CLAUDE.md rule 1; was .claude/settings.json deny rules): %s of %s path "
                    "%s. A .vi/.ctl/.lvlib/.lvproj changes only inside LabVIEW, saved under user.lib\\claudeDev."
                    % (op, side, _rel(p)))
    return None


def originals_ban(ev):
    """R2: reason or None."""
    for op, side, p in _all_paths(ev):
        if ORIGINALS_RE.search(p):
            return "originals are never modified (CLAUDE.md rule 1): %s of %s path %s" % (op, side, _rel(p))
    return None


def runner_globs():
    """never_in_runner_globs from tools/bench/assign/assign_config.json + RUNNER_EXTRA_GLOBS (unreadable: tools/hooks/**)."""
    try:
        with open(ASSIGN_CONFIG, encoding="utf-8") as f:
            g = list(json.load(f).get("never_in_runner_globs") or [])
    except (OSError, ValueError):
        g = ["tools/hooks/**"]
    return g + [x for x in RUNNER_EXTRA_GLOBS if x not in g]


def runner_hook_ban(ev):
    """R3: reason or None. Only when the session is a runner cycle session (CYCLE_SESSION set)."""
    env = ev.get("meta", {}).get("env") or os.environ
    if not env.get("CYCLE_SESSION"):
        return None
    import protocol
    globs = runner_globs()
    for op, side, p in _all_paths(ev):
        if protocol.path_in_globs(p, globs):
            return ("runner sessions never edit hook files (user 2026-10-08, never_in_runner_globs %s): %s of %s path %s"
                    % (globs, op, side, _rel(p)))
    return None


def agent_denied_ban(ev):
    """R7 (CANDIDATE cand-shellguard-01, card chat-X9): reason or None - a write/edit/patch touching a path on
    tools/rules_protected.json `agent_write_denied` (.claude/settings.local.json). Shell forms are judged by guard_bash
    (the shell chain above); both call tools/hooks/protected_write.py."""
    import protected_write
    return protected_write.agent_write_decision(ev.get("paths") or [], ev.get("cwd"))


def _rel(p):
    try:
        return os.path.relpath(p, ROOT).replace("\\", "/")
    except ValueError:
        return p


# ------------------------------------------------------------------ R4 command-level LabVIEW exclusivity
def labview_running():
    """True when the LabVIEW process image is in tasklist (or GUARDCORE_ASSUME_LABVIEW=1). Read-only process list;
    unreadable tasklist -> False (the executor's own checks still run; this rule only adds a refusal)."""
    if os.environ.get("GUARDCORE_ASSUME_LABVIEW") == "1":
        return True
    try:
        q = subprocess.run(["tasklist", "/FI", "IMAGENAME eq " + LV_IMAGE, "/NH"], capture_output=True, text=True,
                           timeout=10)
        return LV_IMAGE.lower() in (q.stdout or "").lower()
    except (OSError, subprocess.SubprocessError):
        return False


def labview_launches(cmd):
    """[(rel path, labview level)] of tools/ scripts this command RUNS whose scope header says labview read|build."""
    try:
        import scope_header as SH
        return [(_rel(p), lv) for p, lv, _hw, _prob in SH.launch_scope(cmd) if lv in ("read", "build")]
    except Exception:          # noqa: BLE001 - a broken reader adds no refusal
        return []


def concurrency_ban(ev, probe=None):
    """R4: reason or None."""
    lv = labview_launches(ev.get("command") or "")
    if not lv:
        return None
    if not (probe or labview_running)():
        return None
    return ("one LabVIEW at a time (CLAUDE.md 'one COM client at a time'): a LabVIEW process is already running and this "
            "command launches %s. Wait for the running one to end and LabVIEW to close, then launch."
            % ", ".join("%s (labview %s)" % x for x in lv))


# ------------------------------------------------------------------ the existing guards, called through their main()
@contextlib.contextmanager
def _env(over):
    old = {k: os.environ.get(k) for k in over}
    try:
        for k, v in over.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = str(v)
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def call_guard(modname, payload, env=None):
    """(rc, reason) of one existing hook's main() on `payload`. rc 2 = deny. An exception inside the guard is reported
    as rc 0 with a note - exactly what each guard does for itself when run by Claude (they fail open on their own
    errors, deliberately; see guard_card.decide, guard_bash.stop_gate)."""
    import importlib
    try:
        mod = importlib.import_module(modname)
    except Exception as e:     # noqa: BLE001
        return 0, "%s not importable (%s: %s) - skipped as Claude would skip a crashing hook" % (
            modname, type(e).__name__, e)
    out, err = io.StringIO(), io.StringIO()
    old_in = sys.stdin
    rc = 0
    try:
        sys.stdin = io.StringIO(json.dumps(payload))
        with _env(env or {}), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                r = mod.main()
                rc = int(r or 0)
            except SystemExit as e:
                rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 2)
    except Exception as e:     # noqa: BLE001
        return 0, "%s raised %s: %s" % (modname, type(e).__name__, str(e)[:200])
    finally:
        sys.stdin = old_in
    so = out.getvalue().strip()
    if so.startswith("{"):
        try:
            d = json.loads(so)
            h = d.get("hookSpecificOutput") or {}
            if h.get("permissionDecision") == "deny" or d.get("decision") == "block":
                return 2, h.get("permissionDecisionReason") or d.get("reason") or so
        except ValueError:
            pass
    return (2 if rc == 2 else 0), err.getvalue().strip() or None


def claude_payload(ev, tool_name, tool_input):
    m = ev.get("meta") or {}
    p = {"hook_event_name": "PreToolUse", "tool_name": tool_name, "tool_input": tool_input,
         "session_id": m.get("session_id") or "", "cwd": ev.get("cwd") or ROOT}
    for k in ("agent_id", "agent_type", "transcript_path"):
        if m.get(k):
            p[k] = m[k]
    return p


def _chain(names, payload, env):
    for n in names:
        rc, why = call_guard(n, payload, env)
        if rc == 2:
            return "%s: %s" % (n, (why or "refused (no reason written)").strip())
    return None


def _patch_tool(op):
    return "Write" if op in ("add", "write") else "Edit"


# ------------------------------------------------------------------ THE judgement
def judge(ev, probe=None):
    """('allow' | 'deny', reason). The order: own path rules (R6, R1-R3), then the existing guards, then R4."""
    kind, tool = ev.get("kind"), ev.get("tool_name") or ""
    env = (ev.get("meta") or {}).get("env_over") or {}
    if kind in ("write", "edit", "patch"):
        if ev.get("paths") is None or (kind == "patch" and not ev.get("paths")):
            return "deny", "patch body could not be parsed into files - refused (fail closed)"
        for rule in (vi_family_ban, originals_ban, runner_hook_ban, agent_denied_ban):
            why = rule(ev)
            if why:
                return "deny", why
        for e in ev["paths"]:
            for side in ("old", "new"):
                if not e.get(side):
                    continue
                t = ev.get("claude_tool") if ev.get("claude_tool") in CHAIN else _patch_tool(e.get("op"))
                why = _chain(CHAIN[t], claude_payload(ev, t, {"file_path": _abs(e[side], ev.get("cwd"))}), env)
                if why:
                    return "deny", why
        return "allow", None
    if kind == "shell":
        t = ev.get("shell") if ev.get("shell") in ("Bash", "PowerShell") else "Bash"
        ti = {"command": ev.get("command") or ""}
        if ev.get("timeout_ms") is not None:
            ti["timeout"] = int(ev["timeout_ms"])
        if ev.get("background"):
            ti["run_in_background"] = True
        why = _chain(CHAIN[t], claude_payload(ev, t, ti), env)
        if why:
            return "deny", why
        why = concurrency_ban(ev, probe)
        return ("deny", why) if why else ("allow", None)
    if kind in ("agent", "read"):
        names = CHAIN.get(tool) or (CHAIN["Agent"] if kind == "agent" else ())
        if kind == "read" and tool not in CHAIN and tool not in READ_ONLY_TOOLS:
            return "deny", "unknown read tool %r - refused (fail closed)" % tool
        why = _chain(names, claude_payload(ev, tool if tool in CHAIN else "Agent", ev.get("tool_input") or {}), env)
        return ("deny", why) if why else ("allow", None)
    if tool in READ_ONLY_TOOLS:
        return "allow", None
    return "deny", ("unknown tool %r - refused (fail closed; guardcore READ_ONLY_TOOLS lists what passes unchecked)"
                    % tool)


def log(ev, verdict, why):
    """One line per decision (tools/hooks/guardcore.log). Never raises."""
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (
                time.strftime("%Y-%m-%d %H:%M:%S"), ev.get("backend"), ev.get("tool_name"), verdict,
                (ev.get("command") or json.dumps([(e.get("op"), e.get("old"), e.get("new"))
                                                  for e in (ev.get("paths") or [])]))[:200].replace("\n", " "),
                (why or "")[:300].replace("\n", " ")))
    except OSError:
        pass
