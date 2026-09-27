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
import re
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


# PURE-PYTHON SELF-TEST EXEMPTION (card 81-1, 2026-09-25): `stagexec.py` imports stagekit/gscript inside LVBackend
# and lv_run, so the source scan calls ANY launch of it LabVIEW-touching - including `stagexec.py selftest`, which
# runs on a synthetic graph and asserts itself that nothing LabVIEW-side was imported (stagexec.py T14). Card 80-4
# was given `labview: read` only to get past this. Exempted BY COMMAND, never by filename: the whole command must be
# exactly that self-test (optionally after `cd <dir> &&`, an env prefix, and a bgrun wrapper), and only a refusal
# on the labview flag is lifted; every other flag, and an unbound agent, is still refused.
_Q = r"(?:\"[^\"]*\"|'[^']*'|[^\s\"';&|]+)"
PURE_SELFTEST_RE = re.compile(
    r"^\s*(?:cd\s+" + _Q + r"\s*&&\s*)?"
    r"(?:(?:\$env:)?[A-Z_]+\s*=\s*['\"]?\w*['\"]?\s*;?\s+)*"
    r"(?:py(?:thon)?(?:\.exe)?\s+(?:-u\s+)?[\"']?[^\s\"';&|]*bgrun\.py[\"']?\s+(?:--[\w-]+(?:\s+(?!--)" + _Q +
    r")?\s+)*--\s+)?"
    r"py(?:thon)?(?:\.exe)?\s+(?:-u\s+)?(?:\"([^\"]*)\"|'([^']*)'|([^\s\"';&|]+))\s+selftest\s*$", re.I)


def pure_selftest(cmd):
    """True only for THIS project's tools/stagexec.py (relative `tools/stagexec.py` or its absolute path)."""
    m = PURE_SELFTEST_RE.match(cmd or "")
    if not m:
        return False
    p = (m.group(1) or m.group(2) or m.group(3) or "").replace("\\", "/")
    if re.match(r"^(?:\./)?tools/stagexec\.py$", p, re.I):
        return True
    want = os.path.normcase(os.path.abspath(os.path.join(TOOLS, "stagexec.py")))
    return bool(re.match(r"^[A-Za-z]:/", p)) and os.path.normcase(os.path.abspath(p)) == want


def _install_launch_units(protocol):
    """card 111-3 (docs/violation-decisions.md device-failed 20:20, guard_card.log:371): the card flags judge the .py
    files a command RUNS through the ONE shared rule, tools/launchunit.py - `py -m <module> X` launches the module, X is
    an argument. protocol._launched_scripts (a token regex that read `pyflakes X` as "python pyflakes X") is kept as the
    detector; launchunit.drop_module_args only removes an entry that it sees ONLY as a READ-ONLY module's argument
    (pyflakes, pycodestyle, py_compile ...), never one it sees launched, and never a second occurrence the regex saw;
    what launchunit sees RUN and the regex missed (any other module's argument, a `-m` module that is a project file)
    is added. Installed once per process."""
    if getattr(protocol._launched_scripts, "_launchunit", False):
        return
    import launchunit as LU
    orig = protocol._launched_scripts

    def launched(cmd):
        out = LU.drop_module_args(cmd, orig(cmd), protocol.ROOT)
        have = set(LU.norm(p, protocol.ROOT) for p in out)
        for p in LU.launched_py(cmd, protocol.ROOT):   # + what only launchunit sees run: a non-read-only module's
            if os.path.isfile(p) and LU.norm(p, protocol.ROOT) not in have:   # argument (`py -m pdb X`), `-m tools.recipes.x`
                out.append(p)
                have.add(LU.norm(p, protocol.ROOT))
        return out
    launched._launchunit = True
    protocol._launched_scripts = launched


def decide(payload):
    """(exit_code, message). Shared by main() and guard_bash.py."""
    try:
        if TOOLS not in sys.path:
            sys.path.insert(0, TOOLS)
        import protocol
        try:
            _install_launch_units(protocol)
        except Exception as e:  # noqa: BLE001 - keep protocol's own (stricter) detector, never fail open
            log("LAUNCHUNIT ERROR (protocol detector kept) %s: %s" % (type(e).__name__, e))
        ok, msg = protocol.hook_decision(payload)
        cmd = (payload.get("tool_input") or {}).get("command", "") \
            if payload.get("tool_name") in ("Bash", "PowerShell") else ""
        if not ok and msg and "flags.labview is " in msg and pure_selftest(cmd):
            log("EXEMPT %s %s | pure-Python self-test by command: %s" % (
                payload.get("agent_type"), payload.get("agent_id"), cmd[:200]))
            return 0, None
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
