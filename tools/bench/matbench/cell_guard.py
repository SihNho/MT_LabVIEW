"""matbench cell guard (card chat-N2) - PreToolUse hook installed ONLY in a replay worktree's .claude/settings.json.

A replay cell is a top-level `claude -p` session, so the project's card hook (guard_card, agent_id-keyed) does not
bind it; this hook enforces the replay card's flags instead (labview none, run_vi false, gui false, hardware none,
peers [], git_commit false, write = the worktree + %TEMP%) and logs EVERY tool call to <wt>/.matbench/calls.jsonl,
from which score.py counts dispatches and refusals. Pure stdlib, no LabVIEW. Exit 2 = refuse, 0 = allow.

Why a regex scan and not protocol.check_command: the worktree sits at an OLD commit whose protocol.py differs per
task; one guard for every cell keeps the refusal rule identical across tasks and conditions.
"""
import json
import os
import re
import sys
import time

WT = os.environ.get("MATBENCH_WT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # <wt>/.matbench/x
LOG = os.environ.get("MATBENCH_LOG") or os.path.join(WT, ".matbench", "calls.jsonl")   # overrides: selftest only
TEMP = os.path.normcase(os.path.abspath(os.environ.get("TEMP", os.environ.get("TMP", "C:/Windows/Temp"))))

# anything that reaches LabVIEW / the GUI / hardware / a peer / git history
# (EXECUTION patterns only: grepping or reading a file that merely NAMES these is allowed)
BAN_CMD = re.compile(r"\bimport\s+(gscript|stagekit|stagexec)\b|\bfrom\s+(gscript|stagekit|stagexec)\s+import|"
                     r"win32com|comtypes|pythoncom|lv_gui\.ps1\s+-Action|peer\.ps1\s+-|-File\s+\S*peer\.ps1|"
                     r"&\s*[\"']?[^\"'\s]*LabVIEW\.exe|Start-Process|motor_gate\.py\s+-|motor_send|"
                     r"\bgit\s+(commit|push|worktree|checkout|reset|stash|rebase|merge|switch|restore|clean)\b",
                     re.I)
BAN_SRC = re.compile(r"^\s*(import|from)\s+(gscript|stagekit|stagexec|win32com|comtypes|pythoncom)\b|"
                     r"Dispatch\(\s*['\"]LabVIEW|lv_gui\.ps1|motor_gate", re.I | re.M)
# pure-Python tools that stub COM themselves (stage_prerun: "dry run + pre-run of a RECIPE with COM stubbed")
SRC_OK = {"bgrun.py", "stage_prerun.py", "stagesim.py", "protocol.py", "vigraph.py", "jev_candidates.py"}
# only a .py in EXECUTION position (after py/python and its flags) is source-scanned; `grep x tools/stagekit.py`,
# `wc -l`, `ls` merely name it (matbench v0 first launch: 2 false refusals of that kind, relaunched after this fix)
PY_RE = re.compile(r"(?:^|[\s;&|(\\/])(?:py|python3?)(?:\.exe)?[\"']?\s+(?:-[A-Za-z]\s+)*"
                   r"(?:\"([^\"]+\.py)\"|'([^']+\.py)'|([^\s\"';&|]+\.py))", re.I)
WRITE_TOOLS = ("Edit", "Write", "NotebookEdit", "MultiEdit")


def log(rec):
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        rec["t"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass


def inside(p, root):
    p = os.path.normcase(os.path.abspath(p))
    return p == root or p.startswith(root.rstrip("\\/") + os.sep)


def check_cmd(cmd):
    m = BAN_CMD.search(cmd or "")
    if m:
        return "replay card: labview/gui/hardware none, peers [], git_commit false - command names %r" % m.group(0)
    for mm in PY_RE.finditer(cmd or ""):
        t = next(g for g in mm.groups() if g)
        p = t if os.path.isabs(t) else os.path.join(WT, t)
        if os.path.basename(p) in SRC_OK or not os.path.isfile(p):
            continue
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                src = f.read()
        except OSError:
            continue
        s = BAN_SRC.search(src)
        if s:
            return "replay card: labview none - %s imports/uses %r" % (t, s.group(0).strip())
    return None


def decide(payload):
    tool = payload.get("tool_name") or ""
    ti = payload.get("tool_input") or {}
    if tool in ("Bash", "PowerShell"):
        return check_cmd(ti.get("command", ""))
    if tool in WRITE_TOOLS:
        fp = ti.get("file_path") or ti.get("notebook_path") or ""
        if not fp:
            return None
        fp = fp if os.path.isabs(fp) else os.path.join(WT, fp)
        if not (inside(fp, os.path.normcase(os.path.abspath(WT))) or inside(fp, TEMP)):
            return "replay card: write only inside the worktree or %%TEMP%% (got %s)" % fp
        if re.search(r"\.(vi|ctl|lvlib|lvproj)$", fp, re.I):
            return "replay card: no .vi writes"
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:           # noqa: BLE001
        return 0
    try:
        why = decide(payload)
    except Exception as e:      # noqa: BLE001  (a guard crash REFUSES here: a replay cell must never reach LabVIEW)
        why = "cell_guard error %s: %s" % (type(e).__name__, e)
    ti = payload.get("tool_input") or {}
    log({"tool": payload.get("tool_name"), "agent_type": payload.get("agent_type"),
         "cmd": (ti.get("command") or ti.get("file_path") or ti.get("subagent_type") or ti.get("pattern") or "")[:300],
         "decision": "REFUSE" if why else "ALLOW", "why": why})
    if why:
        sys.stderr.write("BLOCKED by matbench cell_guard: %s\n" % why)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
