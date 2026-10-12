# ---
# labview: none
# hardware: none
# ---
"""PreToolUse hook for the LEAN-RULES BENCH arm only (discussion tools/bench/debate/lean-rules-01, user 2026-10-13
"벤치 돌려. 그리고 승인함"; "모터 훅은 반드시 체크 해야돼"). Wired ONLY in the lean worktree's .claude/settings.json;
the main project keeps every hook.

Keeps, unchanged, by CALLING guard_bash's own functions:
  1. the motor gate (guard_bash.motor_gate_check) - every motion command through tools/motor_gate.py;
  2. the LabVIEW routing - a LabVIEW-touching command runs backgrounded through bgrun, or with a timeout <= 30 s.
Adds:
  3. no file-tool write to *.vi / *.ctl / *.lvlib / *.lvproj (rule 10) or into the originals' folders.
  4. no bypass env var set on a command (PEER_GUARD_OFF, CYCLE_GUARD_OFF, LV_GUARD_OFF, MATERIAL_GUARD_OFF).
Saving outside claudeDev is refused in code by gscript.save / gui_save (gscript.py:2486, 2603).
Exit 0 = pass, 2 = refuse (stderr says why).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import guard_bash as GB                                                      # noqa: E402

VI_EXT_RE = re.compile(r"\.(vi|ctl|lvlib|lvproj)$", re.I)
ORIGINALS_RE = re.compile(r"zz_LabView VI[\\/]+(background VIs|AAA_UNIST[\\/]+2\. Tracking[\\/]+[^\\/]+\.vi$)", re.I)
BYPASS_RE = re.compile(r"\b(PEER_GUARD_OFF|CYCLE_GUARD_OFF|LV_GUARD_OFF|MATERIAL_GUARD_OFF)\b")


def decide(data):
    """(rc, message) for one PreToolUse payload: rc 0 = pass, 2 = refuse."""
    tool = data.get("tool_name")
    ti = data.get("tool_input") or {}
    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        p = ti.get("file_path") or ti.get("notebook_path") or ""
        if VI_EXT_RE.search(p) or ORIGINALS_RE.search(p):
            return 2, "BLOCKED by guard_lean (rule 10 / originals): no file-tool write to %s" % p
        return 0, None
    if tool not in ("Bash", "PowerShell"):
        return 0, None
    cmd = ti.get("command", "") or ""
    if BYPASS_RE.search(cmd):
        return 2, "BLOCKED by guard_lean: a guard-bypass env var on a command (rule 7)"
    if GB.motor_gate_check(cmd):                     # writes its own refusal text to stderr
        return 2, None
    if not GB.LABVIEW_RE.search(cmd) or GB.offline_scripts_only(cmd):
        return 0, None
    if ti.get("run_in_background"):
        if GB.BGRUN_RE.search(cmd):
            return 0, None
        return 2, "BLOCKED by guard_lean: a backgrounded LabVIEW command runs through `py tools/bgrun.py --max-min N --log <f> -- <cmd>`"
    t = ti.get("timeout", ti.get("timeout_ms"))
    if t is not None and int(t) <= GB.MAX_FG_MS:
        return 0, None
    return 2, "BLOCKED by guard_lean: a LabVIEW-touching command needs run_in_background (bgrun) or a timeout <= 30 s (got %s)" % t


def _selftest():
    mv = {"tool_name": "Bash", "tool_input": {"command": "powershell -File tools/motor_send_pi.ps1 -Cmd 'MOV 1 5'"}}
    ok = [decide({"tool_name": "Bash", "tool_input": {"command": "git status"}})[0] == 0,
          decide(mv)[0] == 2,
          decide({"tool_name": "Write", "tool_input": {"file_path": r"C:\x\a.vi"}})[0] == 2,
          decide({"tool_name": "Bash", "tool_input": {"command": "PEER_GUARD_OFF=1 py x.py"}})[0] == 2]
    assert all(ok), ok
    print("RESULT {\"selftest\": \"PASS\", \"cases\": %d}" % len(ok))


def main():
    if "--selftest" in sys.argv:
        _selftest()
        return 0
    try:
        data = json.load(sys.stdin)
    except Exception:      # noqa: BLE001
        return 0
    rc, msg = decide(data)
    if rc and msg:
        sys.stderr.write(msg + "\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
