# ---
# labview: none
# hardware: none
# ---
"""PreToolUse check: chat sessions while the user runs an EXPERIMENT (G:\\Codes\\rig\\RULES.md section 5; user
2026-10-21 "승인", item C4 of G:\\Codes\\rig\\proposals\\2026-10-21-labview2scr-decisions.md).

While G:\\Codes\\rig\\rig_lock.json says `experiment` (other lab users run the rig without any chat):
  BLOCKED  devices (camera SDKs, COM ports / VISA, motor commands incl. motor_gate / rig_session / rig_recover, the
           Arduino), any tools/ script whose scope header is not `labview: none` + `hardware: none`, LabVIEW launch /
           VI Server / ActiveX / scripting (also attaching to the experiment's running LabVIEW), process kills, lock
           acquire / take-stale / break-mutex, installs and system changes, screen clicks and keys;
  ALLOWED  everything else: reading, data analysis, logs, discussion, `riglock.py status`, `set-state` on the user's
           words, read-only screenshots (`lv_gui.ps1 -Action shot|shotwin|windows|...`, desktop screenshot / zoom).
No PC-load rule (the user: sessions never start work on their own). Not disabled by any env var.

Called from guard_bash.py (Bash / PowerShell, before every other gate) and wired directly in .claude/settings.json for
the desktop-control tools (mcp computer-use / browser `computer`). Reads the lock file directly (no mutex: the file is
replaced atomically). Missing file = no lock system = pass; a file that exists but cannot be read = treated as
experiment (fail closed). RIG_LOCK_JSON overrides the path (self-test only).
Exit 0 = pass, 2 = refuse (stderr says why). `py tools/hooks/guard_experiment.py --selftest` runs its own checks.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCK_JSON = os.environ.get("RIG_LOCK_JSON") or r"G:\Codes\rig\rig_lock.json"

# A segment that only READS (its first word): never blocked, even if it names a device script.
READER_RE = re.compile(r"^\s*(?:cat|head|tail|sed|grep|rg|less|more|type|wc|ls|dir|find|echo|diff|stat|file|"
                       r"Get-Content|Select-String|Get-ChildItem|Get-Item|Test-Path|Write-Output|git\s+(?:log|show|"
                       r"diff|status|blame|grep|ls-files))\b", re.I)
LV_GUI_READ_ACTIONS = ("windows", "dialogs", "shot", "shotwin", "rect", "ping", "crop", "cursor", "md5")
BLOCK = [
    ("device: camera SDK", re.compile(r"imaqdx|niimaq|\bIMAQ\b|atmcd|andor|pyAndor|\bpylon\b|\bjai\b|eBUS|"
                                      r"camera_\w+\.py", re.I)),
    ("device: COM port / VISA / Arduino", re.compile(
        r"System\.IO\.Ports|SerialPort|\bimport\s+serial\b|\bserial\.Serial\b|pyvisa|\bvisa\b|\bASRL\d|"
        r"\bmode\s+COM\d|\\\\\.\\COM\d|\bCOM\d+\b|arduino|avrdude|platformio", re.I)),
    ("device: motor command", re.compile(
        r"motor_gate\.py|rig_session\.py|rig_recover\.py|motor_send_pi\.ps1|motor_asi_io\.ps1|motor_rotor_io\.ps1|"
        r"read_motor_anchor\.ps1|serial_roundtrip|hw_rotor\w*\.py|drive_original_copy\w*\.py|RAWCMD|"
        r"\bMOVREL\b|\bMOVE\s+[XYZ]\s*=|\bMOV\s+[-+0-9]|\bMVR\b|\bGOH\b", re.I)),
    ("LabVIEW launch / VI Server / ActiveX / scripting", re.compile(
        r"LabVIEW\.exe|LabVIEW\.Application|LabVIEWCLI|\bg-?cli\b|win32com|Dispatch\s*\(|comtypes|"
        r"\bimport\s+(?:gscript|lvclick|kb_com|stagekit)\b|\bfrom\s+(?:gscript|lvclick|kb_com|stagekit)\b|"
        r"lv_restart\.py", re.I)),
    ("process kill", re.compile(r"\btaskkill\b|\btskill\b|Stop-Process|\bkill\s+-?\d|\bpkill\b|\bkillall\b|"
                                r"wmic\s+process\b.*\b(?:delete|terminate)\b|\.Kill\s*\(|\.terminate\s*\(", re.I)),
    ("rig lock acquire / take-stale / break-mutex", re.compile(
        r"riglock(?:\.py)?\b.*\b(?:acquire|take-stale|take_stale|break-mutex|break_mutex)\b", re.I)),
    ("install / system change", re.compile(
        r"\bpip3?\s+(?:install|uninstall)\b|-m\s+pip\s+(?:install|uninstall)\b|\bwinget\b|\bchoco\b|\bmsiexec\b|"
        r"\bnpm\s+(?:install|i)\s+-g\b|Install-Module|Install-Package|\breg\s+(?:add|delete|import)\b|"
        r"Set-ItemProperty|New-ItemProperty|Remove-ItemProperty|\bbcdedit\b|\bpowercfg\s+/(?:change|set|s)\b|"
        r"\bschtasks\s+/(?:create|delete|change|run)\b|Register-ScheduledTask|Unregister-ScheduledTask|"
        r"\bsc(?:\.exe)?\s+(?:config|stop|start|delete|create)\b|Set-Service|Stop-Service|Start-Service|"
        r"Restart-Computer|Stop-Computer|\bshutdown\b|\bsetx\b|\bnetsh\b|Set-ExecutionPolicy|Disable-PnpDevice|"
        r"Enable-PnpDevice|\bpnputil\b|\bdevcon\b", re.I)),
]
LV_GUI_RE = re.compile(r"lv_gui\.ps1\b.*?-Action\s+['\"]?(\w+)", re.I)
SEG_SPLIT_RE = re.compile(r"\|\||&&|[;|\n]")
# desktop-control tools: only these actions are read-only
MCP_READ_ACTIONS = ("screenshot", "zoom", "cursor_position", "wait")


def experiment_on(path=None):
    """(on, why). Missing file -> off. Unreadable / invalid -> on (fail closed)."""
    path = path or LOCK_JSON
    if not os.path.exists(path):
        return False, "no rig_lock.json"
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        v = ((doc or {}).get("rig_state") or {}).get("value")
    except Exception as e:                                   # noqa: BLE001
        return True, "rig_lock.json unreadable (%s) - treated as experiment" % type(e).__name__
    return v == "experiment", "rig_state %s" % v


def _script_scope_problem(cmd):
    """A tools/ script the command launches that may touch LabVIEW or hardware (scope header), or None."""
    try:
        sys.path.insert(0, os.path.dirname(HERE))
        import scope_header as SH
        for p, lv, hw, prob in SH.launch_scope(cmd):
            if prob or lv != "none" or hw != "none":
                return "%s (labview %s, hardware %s%s)" % (os.path.basename(p), lv, hw, ", " + prob if prob else "")
    except Exception:                                        # noqa: BLE001 - the regexes below still apply
        return None
    return None


def shell_reason(cmd):
    """Why this shell command is blocked during an experiment, or None."""
    m = LV_GUI_RE.search(cmd)
    if m and m.group(1).lower() not in LV_GUI_READ_ACTIONS:
        return "screen click / key / window change (lv_gui.ps1 -Action %s; read-only actions: %s)" % (
            m.group(1), ", ".join(LV_GUI_READ_ACTIONS))
    for seg in SEG_SPLIT_RE.split(cmd):
        if not seg.strip() or READER_RE.search(seg):
            continue
        if re.search(r"riglock(?:\.py)?\b.*\b(?:status|set-state)\b", seg, re.I) and not BLOCK[5][1].search(seg):
            continue
        if LV_GUI_RE.search(seg):                            # a read-only lv_gui action (checked above)
            continue
        for what, rx in BLOCK:
            hit = rx.search(seg)
            if hit:
                return "%s (%r)" % (what, hit.group(0))
    prob = _script_scope_problem(cmd)
    if prob:
        return "a tools/ script that may touch LabVIEW or hardware: %s" % prob
    return None


def decide(data, lock_path=None):
    """(rc, message) for one PreToolUse payload: rc 0 = pass, 2 = refuse."""
    tool = data.get("tool_name") or ""
    ti = data.get("tool_input") or {}
    on, why = experiment_on(lock_path)
    if not on:
        return 0, None
    reason = None
    if tool in ("Bash", "PowerShell"):
        cmd = ti.get("command", "") or ""
        if isinstance(cmd, list):
            cmd = " ".join(str(x) for x in cmd)
        reason = shell_reason(cmd)
    elif tool.startswith("mcp__") and re.search(r"computer|browser_batch", tool, re.I):
        actions = [ti.get("action")] + [((x or {}).get("input") or {}).get("action") for x in ti.get("actions") or []]
        bad = [a for a in actions if a and a not in MCP_READ_ACTIONS]
        if bad:
            reason = "screen click / key / scroll on the desktop or a page (%s); only %s are allowed" % (
                ", ".join(bad), ", ".join(MCP_READ_ACTIONS))
    if not reason:
        return 0, None
    return 2, ("BLOCKED by tools/hooks/guard_experiment.py (G:\\Codes\\rig\\RULES.md section 5): the user is running an "
               "EXPERIMENT (%s) - other lab users have the rig. Blocked: %s.\nAllowed now: reading, data analysis, "
               "logs, discussion, `py G:\\Codes\\rig\\riglock.py status`, set-state on the user's words, read-only "
               "screenshots. Wait for the user to say the experiment is over." % (why, reason))


def _selftest():
    import tempfile
    d = tempfile.mkdtemp(prefix="guard_experiment_")
    lk = os.path.join(d, "rig_lock.json")
    res = []

    def put(state):
        with open(lk, "w", encoding="utf-8") as f:
            json.dump({"schema": 1, "rig_state": {"value": state}, "holder": None}, f)

    def sh(c, tool="Bash"):
        return decide({"tool_name": tool, "tool_input": {"command": c}}, lk)[0]

    def t(name, cond):
        res.append(cond)
        print("%s  %s" % ("PASS" if cond else "FAIL", name))

    blocked = ["py tools/motor_gate.py --device pi --command \"MOV 1 5\" --execute",
               "py tools/bgrun.py --max-min 20 --log x.log -- py -u tools/rig_session.py --purpose x -- py a.py",
               "py tools/rig_recover.py --order \"user: 복구해\"",
               "powershell -File tools/motor_send_pi.ps1 -Mode send",
               "py -c \"import serial; serial.Serial('COM4')\"",
               "[System.IO.Ports.SerialPort]::new('COM3')",
               "py -c \"import imaqdx_ctypes\"",
               "py -c \"import win32com.client as w; w.Dispatch('LabVIEW.Application')\"",
               "& 'C:\\Program Files\\National Instruments\\LabVIEW 2026\\LabVIEW.exe' x.vi",
               "py -c \"import gscript\"",
               "taskkill /F /IM LabVIEW.exe",
               "Stop-Process -Name LabVIEW",
               "py G:/Codes/rig/riglock.py acquire --holder x --purpose y --pid 1",
               "py G:/Codes/rig/riglock.py acquire --holder x --purpose y --pid 1 --take-stale --reason r",
               "py G:/Codes/rig/riglock.py break-mutex --order x",
               "pip install numba",
               "winget install foo",
               "reg add HKCU\\Software\\x /v y /d z",
               "schtasks /create /tn x /tr y",
               "& .\\tools\\lv_gui.ps1 -Action click -X 1 -Y 2",
               "& .\\tools\\lv_gui.ps1 -Action keys -Text abc",
               "py tools/hw_rotor_read.py",
               "echo x; taskkill /PID 1234 /F",
               "py tools/lv_restart.py"]
    allowed = ["cat G:/Data/x.tra", "grep -n MOV tools/motor_gate.py", "git log --oneline -5",
               "py G:/Codes/rig/riglock.py status",
               "py G:/Codes/rig/riglock.py set-state 조립 --by chat --note \"user: 실험 마침\"",
               "& .\\tools\\lv_gui.ps1 -Action shot -Out x.png", "& .\\tools\\lv_gui.ps1 -Action windows",
               "py -c \"import numpy as np; print(np.load('G:/Data/a.npy').mean())\"",
               "ls tools/bench", "Get-Content STATUS.md -TotalCount 20",
               "py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- py -u tools/hooks/guard_experiment.py"
               " --selftest"]
    put("assembled")
    t("assembled: every device command passes (this hook only acts in an experiment)",
      all(sh(c) == 0 for c in blocked))
    put("experiment")
    for c in blocked:
        t("experiment blocks: %s" % c[:70], sh(c) == 2)
    for c in allowed:
        t("experiment allows: %s" % c[:70], sh(c) == 0)
    t("experiment: desktop click blocked",
      decide({"tool_name": "mcp__computer-use__computer", "tool_input": {"action": "left_click"}}, lk)[0] == 2)
    t("experiment: desktop screenshot allowed",
      decide({"tool_name": "mcp__computer-use__computer", "tool_input": {"action": "screenshot"}}, lk)[0] == 0)
    t("experiment: batch with a key press blocked", decide({"tool_name": "mcp__Claude_Browser__browser_batch",
                                                            "tool_input": {"actions": [{"name": "computer", "input": {
                                                                "action": "screenshot"}}, {"name": "computer",
                                                                "input": {"action": "key"}}]}}, lk)[0] == 2)
    t("experiment: Read tool passes", decide({"tool_name": "Read", "tool_input": {"file_path": "x"}}, lk)[0] == 0)
    with open(lk, "w") as f:
        f.write("{torn")
    t("unreadable lock file -> treated as experiment (device blocked)", sh(blocked[0]) == 2)
    os.remove(lk)
    t("no lock file -> pass", sh(blocked[0]) == 0)
    n_ok = sum(res)
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if n_ok == len(res) else "FAIL",
                                  "gates": {"pass": n_ok, "fail": len(res) - n_ok}, "first_fail": None,
                                  "artefacts": []}))
    return 0 if n_ok == len(res) else 1


def main():
    if "--selftest" in sys.argv[1:]:
        return _selftest()
    try:
        data = json.load(sys.stdin)
    except Exception:                                        # noqa: BLE001
        return 0
    rc, msg = decide(data)
    if rc:
        sys.stderr.write(msg + "\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
