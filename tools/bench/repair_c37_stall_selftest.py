"""repair_c37_stall_selftest.py - the test for cycle 37's ONE-CLAUSE repair of tools/lv_stallcheck.ps1.
No LabVIEW, no motor, no camera, no .vi is touched.

WHAT ALREADY EXISTED (checked before writing a line, CLAUDE.md "before creating any new op/tool/recipe"):
  * tools/lv_stallcheck.ps1          - the watchdog being repaired (one clause added, no new device)
  * tools/bench/repair_c36_selftest.py - the SAME test shape and the SAME bgrun->py->python leaf topology;
    this file reuses its stallcheck() invocation, its pids_with()/children() probes and its gate() reporting
  * tools/bgrun.py                   - the runner used to give each fake leaf a real bgrun ancestor
Nothing new is built: this is the repair's test, per the user's standing "장치는 더 만들지 말고" order.

THE REPAIR UNDER TEST (archive/peer/2026-09-18-stall-waitlogs-c37.md, section 5): the freshness skip used to
read ONLY the ANCESTOR's `bgrun --log`. It now also skips when ANY log path named on the LEAF's own bound
command line was written within $LogFreshSeconds - "flag only if EVERY log path on the leaf's own command line
is also stale". That is the file a waiter (tools/wait_logs.py) is actually watching.

PREDICTION CONTRACT - what must be true if the repair works:
  G1  a leaf whose OWN command line names a FRESH log is NOT flagged          (the false-positive class dies)
  G2  a leaf whose OWN command line names a STALE log IS still flagged        (a waiter on a dead job still fires)
  G3  a leaf with NO log on its own command line IS still flagged             (real clients: stall_pid11424:3,
                                                                               stall_pid3792:3 - coverage kept)
  G4  the skip in G1 is attributed to the NEW clause, not to some other test  (-Explain names it)
All three leaves run at once under one watchdog pass, with the ancestor bgrun logs deliberately stale, so the
only thing that can separate them is the new clause.

SECOND CLAUSE UNDER TEST (2026-09-19, same cycle, judgement's call): a LEAF WHOSE OWN COMMAND LINE INVOKES
`tools/wait_logs.py` IS SKIPPED UNCONDITIONALLY - it holds no LabVIEW client, so the watchdog's sentence cannot
be true of it. Two further gates, and the leaf is built to be structurally IDENTICAL to G2's (its own bgrun
ancestor, one log on its command line, that log stale) so that G2 passing is the counterfactual: the only
difference between the leaf that fires and the leaf that does not is the wait_logs.py name.
  G5  a wait_logs.py leaf with EVERY log on its command line stale is NOT flagged
  G6  that skip is attributed to the wait_logs clause                            (-Explain names it)

THIRD CLAUSE UNDER TEST (2026-09-19, cycle 39, the ONE-LINE repair authorised by the judgement session at
lv_stallcheck.ps1:273): the GATING `stall_pid*.log` - the file guard_peer.py blocks the next build on - is
written ONLY when the dialog check at :257 returns `VERDICT: BLOCKED`. Every one of the SIX records this
watchdog has produced said "no modal dialog" while the accused job was alive and finished normally, so its
precision is 0/6 and each record cost a paid peer review to clear. The advisory systemMessage is unchanged:
the watchdog still SAYS what it sees, it just no longer gates a build on an unconfirmed sighting.
  G7  a flagged leaf whose dialog check says "no modal dialog" writes NO record   (the 0/6 class stops gating)
  G8  a flagged leaf whose dialog check says `VERDICT: BLOCKED` still writes one  (coverage kept)
Both drive the verdict deterministically by running a COPY of the watchdog beside a STUB `lv_gui.ps1`, because
:256 resolves that script through $PSScriptRoot; no real modal dialog and no edit to lv_gui.ps1 is involved.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PS1 = os.path.join(ROOT, "tools", "lv_stallcheck.ps1")
PY = sys.executable

FRESH_MARK = "C37FRESHMARK"
STALE_MARK = "C37STALEMARK"
NOLOG_MARK = "C37NOLOGMARK"
WAIT_MARK = "C37WAITMARK"

gates = []


def gate(name, ok, detail=""):
    gates.append((name, ok, detail))
    print(("  PASS " if ok else "  -> FAIL ") + name + ("  | " + detail if detail else ""), flush=True)


def run(cmd, timeout=180):
    return subprocess.run(cmd, cwd=ROOT, stdin=subprocess.DEVNULL, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=timeout)


def stallcheck(state, record, extra=()):
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", PS1,
           "-StallSeconds", "3", "-DeltaWindowSeconds", "2", "-LogFreshSeconds", "3",
           "-SamplePath", state, "-RecordPath", record] + list(extra)
    r = run(cmd, timeout=120)
    return r.stdout or "", r.stderr or ""


def pids_with(mark):
    r = run(["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match '" + mark + "' -and "
             "$_.CommandLine -notmatch 'Where-Object' } | ForEach-Object { \"$($_.ProcessId)\" }"], timeout=90)
    return [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip().isdigit()]


def children(procid):
    r = run(["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq " + str(procid) + " } | "
             "ForEach-Object { \"$($_.ProcessId) $($_.Name)\" }"], timeout=90)
    return [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip()]


print("=== repair_c37_stall_selftest: lv_stallcheck.ps1 leaf-command-line freshness clause ===", flush=True)
tmp = tempfile.mkdtemp(prefix="c37stall_")
state = os.path.join(tmp, "samples.txt")
record = os.path.join(tmp, "stall_record.log")
fresh_log = os.path.join(tmp, "watched_fresh.log")
stale_log = os.path.join(tmp, "watched_stale.log")
# The waiter's watched file carries the marker IN ITS NAME, because a wait_logs.py leaf takes no free-form
# argument to hang a marker on - its command line is `--seconds N <log> [<log> ...]` and nothing else.
wait_log = os.path.join(tmp, "watched_" + WAIT_MARK + ".log")
for p, txt in ((fresh_log, "growing\n"), (stale_log, "written once and abandoned\n"),
               (wait_log, "written once and abandoned\n")):
    with open(p, "w", encoding="utf-8") as f:
        f.write(txt)

# Three fake leaves, each under its OWN bgrun (so the ancestor walk finds a --log, as repair 2 of cycle 36
# requires) and each launched through the `py` launcher so the python.exe underneath is a TRUE leaf - the same
# topology repair_c36_selftest.py:89-94 measured and the same one every real bgrun job in this project has.
jobs = []
for mark, tail in ((FRESH_MARK, " " + fresh_log), (STALE_MARK, " " + stale_log), (NOLOG_MARK, "")):
    joblog = os.path.join("tools", "bench", "stall_selftest_c37_" + mark.lower() + ".log")
    code = "import time;time.sleep(60)  # " + mark + tail
    pr = subprocess.Popen([PY, "-u", os.path.join("tools", "bgrun.py"), "--material", "--max-min", "3",
                           "--log", joblog, "--", "py", "-c", code],
                          cwd=ROOT, stdin=subprocess.DEVNULL,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    jobs.append((mark, pr, joblog))
    print(f"  launched {mark} leaf under bgrun log {joblog}", flush=True)

# The FOURTH leaf: a REAL tools/wait_logs.py, under its own bgrun, watching one file that is already stale and
# will never be touched again. Same topology as the STALE leaf of G2 in every respect except the script name.
_waitjoblog = os.path.join("tools", "bench", "stall_selftest_c37_" + WAIT_MARK.lower() + ".log")
_waitpr = subprocess.Popen([PY, "-u", os.path.join("tools", "bgrun.py"), "--material", "--max-min", "3",
                            "--log", _waitjoblog, "--",
                            "py", "-u", os.path.join("tools", "wait_logs.py"), "--seconds", "60", wait_log],
                           cwd=ROOT, stdin=subprocess.DEVNULL,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
jobs.append((WAIT_MARK, _waitpr, _waitjoblog))
print(f"  launched {WAIT_MARK} wait_logs.py leaf under bgrun log {_waitjoblog}", flush=True)

time.sleep(8)  # > StallSeconds(3), and long enough that every bgrun log is stale at LogFreshSeconds=3
for mark, _, _ in jobs:
    ps = pids_with(mark)
    print(f"  processes carrying {mark}: {ps}", flush=True)
    for sp in ps:
        print(f"    children of {sp}: {children(sp)}", flush=True)

os.utime(fresh_log, None)                 # the watched file is GROWING
out1, err1 = stallcheck(state, record)    # run 1: CPU baseline only, can never flag
time.sleep(4)
os.utime(fresh_log, None)                 # still growing at the instant of the verdict
out2, err2 = stallcheck(state, record)    # run 2: the delta window has elapsed
print(f"  watchdog run1 stdout {len(out1)} chars, run2 stdout {len(out2)} chars", flush=True)
if err2.strip():
    print("  watchdog stderr: " + err2.strip()[:300], flush=True)

os.utime(fresh_log, None)
outx, errx = stallcheck(state, os.path.join(tmp, "explain_record.log"), extra=["-Explain"])
watched = {}
for mark, _, _ in jobs:
    for pid in pids_with(mark):
        watched[pid] = mark
explains = {}
for ln in (outx or "").splitlines():
    m = re.match(r"EXPLAIN pid (\d+):", ln.strip())
    if m and m.group(1) in watched:
        explains.setdefault(watched[m.group(1)], []).append(ln.strip())
        print("    [explain] " + watched[m.group(1)] + " " + ln.strip()[:190], flush=True)

body = ""
if os.path.exists(record):
    with open(record, encoding="utf-8", errors="replace") as f:
        body = f.read()
    print("  --- stall record written by the test ---", flush=True)
    for ln in body.splitlines():
        print("    | " + ln[:200], flush=True)
else:
    print("  (no stall record written)", flush=True)

msg2 = ""
try:
    msg2 = json.loads(out2).get("systemMessage", "") if out2.strip() else ""
except Exception:
    msg2 = out2

# A leaf is "named" if the marker appears in the stall RECORD (its `cmd pid ...` line) OR - and from the
# 2026-09-19 repair this is the only channel left when no modal dialog is present, because then no record is
# written at all - in the advisory systemMessage, where the leaf is identified by its bgrun job log
# `tools/bench/stall_selftest_c37_<mark>.log`. The marker is lower-cased in that file name.
def named(mark, body_txt, msg_txt):
    return (mark in body_txt) or (mark.lower() in (msg_txt or "").lower())


print("  systemMessage (run 2): " + (msg2 or "(empty)")[:400], flush=True)
gate("G1 leaf whose own command line names a FRESH log is NOT flagged",
     not named(FRESH_MARK, body, msg2),
     f"marker {FRESH_MARK} absent from record and message")
gate("G2 leaf whose own command line names a STALE log IS still flagged",
     named(STALE_MARK, body, msg2),
     f"marker {STALE_MARK} present" if named(STALE_MARK, body, msg2)
     else "the watchdog named no leaf carrying the marker")
gate("G3 leaf with NO log on its command line IS still flagged (real-client coverage)",
     named(NOLOG_MARK, body, msg2),
     f"marker {NOLOG_MARK} present" if named(NOLOG_MARK, body, msg2)
     else "the watchdog named no leaf carrying the marker")
gate("G4 the G1 skip is attributed to the NEW clause",
     any("log on its own command line is fresh" in ln for ln in explains.get(FRESH_MARK, [])),
     "; ".join(explains.get(FRESH_MARK, ["(no EXPLAIN line for the fresh leaf)"]))[:200])
gate("G5 a tools/wait_logs.py leaf with every log on its command line STALE is NOT flagged",
     not named(WAIT_MARK, body, msg2),
     f"marker {WAIT_MARK} absent from record and message (G2 is the counterfactual: same shape, fires)")
gate("G6 the G5 skip is attributed to the wait_logs clause",
     any("wait_logs.py waiter" in ln for ln in explains.get(WAIT_MARK, [])),
     "; ".join(explains.get(WAIT_MARK, ["(no EXPLAIN line for the waiter leaf)"]))[:200])

# cleanup: kill each bgrun tree, then report what its log ends with
for mark, pr, joblog in jobs:
    subprocess.run(["taskkill", "/F", "/T", "/PID", str(pr.pid)], capture_output=True, text=True)
    try:
        pr.wait(timeout=30)
    except subprocess.TimeoutExpired:
        pass
    jp = os.path.join(ROOT, joblog)
    last = ""
    if os.path.exists(jp):
        with open(jp, encoding="utf-8", errors="replace") as f:
            ls = [l.rstrip("\n") for l in f if l.strip()]
        last = ls[-1] if ls else ""
    print(f"  {mark} job log last line: {last[:150]}", flush=True)
    # Scratch artefacts are created and deleted in the same run (CLAUDE.md rule 4). These bgrun logs are also
    # *.log files under tools/bench/, which is exactly what guard_peer.py scans - leaving them would let a test
    # fixture gate a real build.
    try:
        os.remove(jp)
    except OSError:
        pass

# ---------------------------------------------------------------------------------------------------------
# PHASE 2 (2026-09-19, cycle 39, judgement-authorised ONE-LINE repair at lv_stallcheck.ps1:273):
# THE GATING `stall_pid*.log` IS WRITTEN ONLY WHEN THE DIALOG CHECK RETURNS `VERDICT: BLOCKED`.
# The watchdog's precision was 0/6 - six records, six live-and-finishing jobs, every one of them saying
# "no modal dialog", and each one blocking the next build through guard_peer.py until a paid review cleared it.
#
#   G7  a flagged leaf whose dialog check says "no modal dialog" writes NO record (the message still fires)
#   G8  a flagged leaf whose dialog check says VERDICT: BLOCKED still writes one
#
# The dialog verdict is produced by `& (Join-Path $PSScriptRoot 'lv_gui.ps1') -Action dialogs` (:256), so the
# only way to drive both branches deterministically - without touching the real lv_gui.ps1 or needing a real
# modal dialog on a shared LabVIEW - is to run a COPY of the watchdog beside a STUB sibling of that name.
# $PSScriptRoot is used for nothing else that matters here: both -SamplePath and -RecordPath are passed, and
# relative job-log paths simply fail Test-Path, which leaves the leaf flagged (exactly what these two gates
# need). One fresh leaf, its own bgrun ancestor, no log on its own command line - the G3 shape.
DLG_MARK = "C37DLGMARK"
stub_dirs = {}
for name, verdict in (("clear", "VERDICT: clear"), ("blocked", "VERDICT: BLOCKED")):
    d = os.path.join(tmp, "stub_" + name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "lv_stallcheck.ps1"), "w", encoding="utf-8") as f:
        with open(PS1, encoding="utf-8") as src:
            f.write(src.read())
    with open(os.path.join(d, "lv_gui.ps1"), "w", encoding="utf-8") as f:
        f.write("param([string]$Action)\nWrite-Output '" + verdict + "'\n")
    stub_dirs[name] = d


def stallcheck_at(script_dir, state, record):
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
           "-File", os.path.join(script_dir, "lv_stallcheck.ps1"),
           "-StallSeconds", "3", "-DeltaWindowSeconds", "2", "-LogFreshSeconds", "3",
           "-SamplePath", state, "-RecordPath", record]
    r = run(cmd, timeout=120)
    return r.stdout or "", r.stderr or ""


_dlgjoblog = os.path.join("tools", "bench", "stall_selftest_c37_" + DLG_MARK.lower() + ".log")
_dlgpr = subprocess.Popen([PY, "-u", os.path.join("tools", "bgrun.py"), "--material", "--max-min", "3",
                           "--log", _dlgjoblog, "--",
                           "py", "-c", "import time;time.sleep(120)  # " + DLG_MARK],
                          cwd=ROOT, stdin=subprocess.DEVNULL,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"  launched {DLG_MARK} leaf under bgrun log {_dlgjoblog} (phase 2: dialog gating)", flush=True)
time.sleep(7)
state2 = os.path.join(tmp, "samples_dlg.txt")
rec_clear = os.path.join(tmp, "dlg_clear_record.log")
rec_blocked = os.path.join(tmp, "dlg_blocked_record.log")
stallcheck_at(stub_dirs["clear"], state2, rec_clear)          # CPU baseline only
time.sleep(4)
out_clear, _ = stallcheck_at(stub_dirs["clear"], state2, rec_clear)
time.sleep(4)
out_blocked, _ = stallcheck_at(stub_dirs["blocked"], state2, rec_blocked)
try:
    msg_clear = json.loads(out_clear).get("systemMessage", "") if out_clear.strip() else ""
except Exception:
    msg_clear = out_clear
try:
    msg_blocked = json.loads(out_blocked).get("systemMessage", "") if out_blocked.strip() else ""
except Exception:
    msg_blocked = out_blocked
body_blocked = ""
if os.path.exists(rec_blocked):
    with open(rec_blocked, encoding="utf-8", errors="replace") as f:
        body_blocked = f.read()
_flagged_clear = named(DLG_MARK, "", msg_clear)
_flagged_blocked = named(DLG_MARK, body_blocked, msg_blocked)
print(f"  phase2 clear-run flagged the leaf: {_flagged_clear}; record on disk: {os.path.exists(rec_clear)}",
      flush=True)
print(f"  phase2 blocked-run flagged the leaf: {_flagged_blocked}; record on disk: "
      f"{os.path.exists(rec_blocked)}", flush=True)
for ln in body_blocked.splitlines()[:2]:
    print("    | " + ln[:200], flush=True)

gate("G7 'no modal dialog' writes NO gating record (the leaf IS still flagged in the message)",
     _flagged_clear and not os.path.exists(rec_clear),
     f"flagged={_flagged_clear}, record_exists={os.path.exists(rec_clear)}; "
     + ("message says NOT WRITTEN" if "NOT WRITTEN" in msg_clear else "message does NOT say NOT WRITTEN"))
gate("G8 'VERDICT: BLOCKED' still writes the gating record",
     os.path.exists(rec_blocked) and "STALL:" in body_blocked and _flagged_blocked,
     f"record_exists={os.path.exists(rec_blocked)}, has STALL line={'STALL:' in body_blocked}, "
     f"flagged={_flagged_blocked}")

subprocess.run(["taskkill", "/F", "/T", "/PID", str(_dlgpr.pid)], capture_output=True, text=True)
try:
    _dlgpr.wait(timeout=30)
except subprocess.TimeoutExpired:
    pass
try:
    os.remove(os.path.join(ROOT, _dlgjoblog))   # never leave a *.log under tools/bench (guard_peer scans it)
except OSError:
    pass

npass = sum(1 for _, ok, _ in gates if ok)
print(f"=== repair_c37_stall_selftest: {npass} pass, {len(gates) - npass} fail ===", flush=True)
sys.exit(0 if npass == len(gates) else 1)
