# ---
# labview: none
# hardware: none
# ---
"""Self-test: guard_bash Codex compatibility (chat 2026-10-10, found by the user's Codex chat).
1. a `py tools/*.py` launch whose every script declares `labview: none` + `hardware: none` passes without a timeout
   (Codex tool input carries none), in plain / PowerShell-wrapped / argv-list / Codex-field / quoted-absolute forms;
2. every LabVIEW-scoped launch is still refused without a timeout or bgrun - including the quoted absolute path that
   LABVIEW_RE did not see before, an argv list, and a none-script chained with a LabVIEW one;
3. an argv-list command no longer crashes the hook. Feeds the hook real PreToolUse JSON in a subprocess."""
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")).replace("\\", "/")
HOOK = os.path.join(ROOT, "tools", "hooks", "guard_bash.py")
SAY = 'py tools/debate_gdoc.py say --dir tools/bench/debate/x/relay "hi"'
LV = "py tools/bench/guardcore_fake/sentinel_lv.py"          # header labview: build, a fake target
CASES = [  # (name, tool_name, command, extra tool_input, extra top-level, expect_blocked)
    ("say_plain", "Bash", SAY, {}, {}, False),
    ("say_pwsh_wrapped", "Bash", 'powershell.exe -NoProfile -Command "%s"' % SAY.replace('"', '\\"'), {}, {}, False),
    ("say_argv_list", "Bash", ["powershell.exe", "-NoProfile", "-Command", SAY], {}, {}, False),
    ("say_codex_fields", "Bash", SAY, {}, {"turn_id": "t", "model": "gpt-6.1-sol", "session_id": "s"}, False),
    ("say_quoted_abs", "Bash", 'py "%s/tools/debate_gdoc.py" say --dir x "hi"' % ROOT, {}, {}, False),
    ("lv_plain", "Bash", LV, {}, {}, True),
    ("lv_quoted_abs", "Bash", 'py "%s/tools/bench/guardcore_fake/sentinel_lv.py"' % ROOT, {}, {}, True),
    ("lv_argv_list", "Bash", ["powershell.exe", "-Command", LV], {}, {"turn_id": "t"}, True),
    ("say_then_lv", "Bash", SAY + " && " + LV, {}, {}, True),
    ("lv_gui_action", "PowerShell", "& .\\tools\\lv_gui.ps1 -Action ping", {}, {}, True),
    ("py_c_gscript", "Bash", 'py -c "import gscript"', {}, {}, True),
    # guardcore-fix-20261010 (structure-equal-02 round 4): a file name ending .py before a tools/ path is not a launch
    ("rg_two_py_files", "Bash", "rg -n 'def |STOP' tools/debate_relay.py tools/debate_gdoc.py", {}, {}, False),
    ("rg_lv_file_listed", "Bash", "rg -n x tools/bench/a.py tools/bench/guardcore_fake/sentinel_lv.py", {}, {}, False),
    ("pyexe_path_lv", "Bash", "C:\\Windows\\py.exe tools/bench/guardcore_fake/sentinel_lv.py", {}, {}, True),
    ("python_lv", "Bash", "python tools/bench/guardcore_fake/sentinel_lv.py", {}, {}, True),
    ("rg_then_lv", "Bash", "rg -n x tools/a.py; py tools/bench/guardcore_fake/sentinel_lv.py", {}, {}, True),
]
# guardcore-fix-20261010: the three exact read-only Codex tool names pass adapt_codex; code execution and look-alike
# names stay refused (exact names only, no prefix match).
CODEX_TOOLS = [("mcp__codex_apps__google_drive__fetch", False), ("webrun", False), ("clocksleep", False),
               ("mcp__node_repl__js", True), ("mcp__codex_apps__google_drive__write", True),
               ("mcp__codex_apps__google_drive__fetchx", True), ("webrun2", True)]
ADAPT_CODEX = os.path.join(ROOT, "tools", "hooks", "adapt_codex.py")


def codex_tool(name):
    ev = {"hook_event_name": "PreToolUse", "tool_name": name, "tool_input": {}, "cwd": ROOT, "turn_id": "t",
          "session_id": "s", "model": "gpt-6.1-sol"}
    p = subprocess.run([sys.executable, ADAPT_CODEX], input=json.dumps(ev), capture_output=True, text=True,
                       encoding="utf-8", timeout=120)
    return '"deny"' in (p.stdout or ""), p.returncode


def run(name, tool, cmd, ti_extra, top_extra):
    ev = {"hook_event_name": "PreToolUse", "tool_name": tool, "cwd": ROOT, "tool_input": dict({"command": cmd}, **ti_extra)}
    ev.update(top_extra)
    p = subprocess.run([sys.executable, HOOK], input=json.dumps(ev), capture_output=True, text=True, encoding="utf-8",
                       timeout=60)
    return p.returncode, (p.stderr or "").strip().replace("\n", " ")[:140]


def main():
    fails = 0
    for name, tool, cmd, ti, top, expect in CASES:
        rc, err = run(name, tool, cmd, ti, top)
        ok = (rc == 2) == expect and rc in (0, 2)
        fails += not ok
        print("%s  %-18s rc=%d %s" % ("PASS" if ok else "FAIL", name, rc, err if not ok else ""))
    for name, expect_deny in CODEX_TOOLS:
        denied, rc = codex_tool(name)
        ok = denied == expect_deny and rc == 0
        fails += not ok
        print("%s  codex tool %-40s denied=%s rc=%d" % ("PASS" if ok else "FAIL", name, denied, rc))
    total = len(CASES) + len(CODEX_TOOLS)
    print("RESULT %s" % json.dumps({"schema": "result-line/1", "status": "PASS" if not fails else "FAIL",
                                    "pass": total - fails, "fail": fails}))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
