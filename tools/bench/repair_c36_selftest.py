"""repair_c36_selftest.py - ONE runner for cycle 36's STEP 0: the two device REPAIRS + their tests + the
stall reviewer's four falsification probes. No LabVIEW, no motor, no camera, no .vi is touched.

WHAT ALREADY EXISTED (checked before writing a line, CLAUDE.md "before creating any new op/tool/recipe"):
  * tools/bgrun.py            - the background runner (patched here, 1 line + comment: BGRUN_LOG)
  * tools/lv_stallcheck.ps1   - the stall watchdog (patched here: (pid,CreationDate) bind + no-bgrun-log skip)
  * tools/audit_cycle.py:242  - already READS os.environ["BGRUN_LOG"]; nothing ever set it
  * tools/bench/selftest_bgrun_fail_scan.py, tools/bench/selftest_motor_gate2.py, tools/bench/tmx_selftest*.py
    - the project's existing self-test shape, which this file follows (named gates, PASS/FAIL, rc)
  No new DEVICE is built here (user's standing no-more-devices order): both changes are repairs of existing
  tools, and this file is their test.

PREDICTION CONTRACT - what must be true if the repairs work:
  G1  a benign sleep-poller with NO bgrun job log among its ancestors is NOT named a stalled client
  G2  a genuine stalled client (a leaf under bgrun, its job log stale, CPU flat) IS still named
  G3  a bgrun child's environment carries BGRUN_LOG == the --log path of ITS OWN runner (not an outer one)
  G4  bgrun still works end to end: a trivial command's log ends with a `BGRUN END` line
  G5  this runner's own environment carries BGRUN_LOG (= the outer runner's log) - the direct-child case
Probes F1-F4 are the stall reviewer's falsification tests (tools/bench/peer_stall_c35.log:50-53); they are
REPORTED, never gated - they are about a past record, not about this patch.
M1 reports, for the four logs STATUS names as missing their BGRUN END line, what the file actually ends with.
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
BENCH = os.path.join(ROOT, "tools", "bench")
PS1 = os.path.join(ROOT, "tools", "lv_stallcheck.ps1")
PY = sys.executable

BENIGN_MARK = "C36BENIGNMARK"
STALL_MARK = "C36STALLMARK"

gates = []


def gate(name, ok, detail=""):
    gates.append((name, ok, detail))
    print(("  PASS " if ok else "  -> FAIL ") + name + ("  | " + detail if detail else ""), flush=True)


def run(cmd, timeout=180):
    return subprocess.run(cmd, cwd=ROOT, stdin=subprocess.DEVNULL, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=timeout)


def stallcheck(state, record, extra=()):
    """One invocation of the watchdog with the test's own state file and record path."""
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", PS1,
           "-StallSeconds", "3", "-DeltaWindowSeconds", "2", "-LogFreshSeconds", "3",
           "-SamplePath", state, "-RecordPath", record] + list(extra)
    r = run(cmd, timeout=120)
    return r.stdout or "", r.stderr or ""


# ---------------------------------------------------------------- 1. lv_stallcheck.ps1
print("=== repair_c36_selftest: lv_stallcheck.ps1 + bgrun.py repairs ===", flush=True)
tmp = tempfile.mkdtemp(prefix="c36stall_")
state = os.path.join(tmp, "samples.txt")
record = os.path.join(tmp, "stall_record.log")
inner_log = os.path.join("tools", "bench", "stall_selftest_c36_inner.log")

# (a) BENIGN: a sleep-poller whose parent exits at once, so the ancestor walk finds no bgrun --log.
#     Spawned through a throwaway launcher that writes the grandchild's pid to a file and then dies.
#     THE GRANDCHILD'S STREAMS MUST GO TO DEVNULL and the pid must travel by FILE, not by stdout: run 1 of
#     this test (20:51:55) hung for the full bgrun deadline because the grandchild inherited the launcher's
#     stdout PIPE, so subprocess.run() waited on a pipe that a 300 s sleeper was holding open - and on
#     Windows even the post-timeout kill() only kills the launcher, after which communicate() waits again.
pidfile = os.path.join(tmp, "benign_pid.txt")
launcher = ("import subprocess,sys;"
            "p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(300)  # " + BENIGN_MARK + "'],"
            "stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);"
            "open(r'" + pidfile + "','w').write(str(p.pid))")
run([PY, "-c", launcher], timeout=60)
benign_pid = 0
if os.path.exists(pidfile):
    with open(pidfile) as f:
        benign_pid = int((f.read() or "0").strip() or 0)
print(f"  benign poller pid {benign_pid} (parent exited; no bgrun ancestor)", flush=True)

# (b) GENUINE: a leaf under bgrun whose job log is written once at START and then goes stale.
# THE CHILD IS LAUNCHED THROUGH THE `py` LAUNCHER, not through python.exe directly, because that is the real
# topology every bgrun job in this project has (`-- py -u tools/...`) and the difference decides the answer:
# bgrun creates its child with CREATE_NO_WINDOW, the console that allocates gets a conhost.exe child, and run 3
# of this test (20:58:32) showed the watchdog dropping the direct python.exe leaf as "wrapper (has a live
# child)". With the launcher in between, conhost attaches to py.exe and the python.exe underneath is a true
# leaf - exactly as pid 11536 was in the cycle-35 record. The child list is printed below, measured not assumed.
inner = subprocess.Popen([PY, "-u", os.path.join("tools", "bgrun.py"), "--material", "--max-min", "3",
                          "--log", inner_log, "--",
                          "py", "-c", "import time;time.sleep(30)  # " + STALL_MARK],
                         cwd=ROOT, stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(5)


def pids_with(mark):
    r = run(["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match '" + mark + "' -and "
             "$_.CommandLine -notmatch 'Where-Object' } | ForEach-Object { $_.ProcessId }"], timeout=90)
    return [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip().isdigit()]


def children(procid):
    r = run(["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq " + str(procid) + " } | "
             "ForEach-Object { \"$($_.ProcessId) $($_.Name)\" }"], timeout=90)
    return [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip()]


stall_pids = pids_with(STALL_MARK)
print(f"  processes carrying {STALL_MARK}: {stall_pids} (the leaf is the one with no child)", flush=True)
for sp in stall_pids + ([str(benign_pid)] if benign_pid else []):
    print(f"    children of {sp}: {children(sp)}", flush=True)

out1, err1 = stallcheck(state, record)          # run 1: takes the CPU baseline, can never flag
time.sleep(4)
out2, err2 = stallcheck(state, record)          # run 2: the delta window has elapsed
print(f"  watchdog run1 stdout {len(out1)} chars, run2 stdout {len(out2)} chars", flush=True)
if err2.strip():
    print("  watchdog stderr: " + err2.strip()[:300], flush=True)
# Diagnostic pass: one line per candidate saying which test excluded it. Read-only, no record is written.
outx, errx = stallcheck(state, os.path.join(tmp, "explain_record.log"), extra=["-Explain"])
watched = set(stall_pids) | ({str(benign_pid)} if benign_pid else set())
for ln in (outx or "").splitlines():
    m = re.match(r"EXPLAIN pid (\d+):", ln.strip())
    if m and m.group(1) in watched:
        print("    [explain] " + ln.strip()[:190], flush=True)

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

gate("G1 benign sleep-poller with no bgrun job log is NOT flagged",
     BENIGN_MARK not in body and BENIGN_MARK not in msg2,
     f"marker {BENIGN_MARK} absent from record and message")
gate("G2 genuine stalled client under bgrun IS still flagged",
     STALL_MARK in body,
     f"marker {STALL_MARK} present in the stall record" if STALL_MARK in body
     else "the watchdog named no client carrying the marker")

# cleanup: kill the benign poller, let the inner bgrun finish so its log gets its END line
if benign_pid:
    subprocess.run(["taskkill", "/F", "/T", "/PID", str(benign_pid)], capture_output=True, text=True)
try:
    inner.wait(timeout=120)
except subprocess.TimeoutExpired:
    subprocess.run(["taskkill", "/F", "/T", "/PID", str(inner.pid)], capture_output=True, text=True)
inner_tail = ""
ip = os.path.join(ROOT, inner_log)
if os.path.exists(ip):
    with open(ip, encoding="utf-8", errors="replace") as f:
        lines = [l.rstrip("\n") for l in f if l.strip()]
    inner_tail = lines[-1] if lines else ""
print(f"  inner job log last line: {inner_tail}", flush=True)

# ---------------------------------------------------------------- 2. bgrun.py BGRUN_LOG + end to end
print("=== bgrun.py: BGRUN_LOG in the child environment, and end-to-end ===", flush=True)
probe_log = os.path.join("tools", "bench", "probe_bgrun_env_c36.log")
pp = os.path.join(ROOT, probe_log)
if os.path.exists(pp):
    os.remove(pp)
r = run([PY, "-u", os.path.join("tools", "bgrun.py"), "--material", "--max-min", "2", "--log", probe_log, "--",
         PY, "-c", "import os;print('CHILD_BGRUN_LOG=' + repr(os.environ.get('BGRUN_LOG')))"], timeout=180)
with open(pp, encoding="utf-8", errors="replace") as f:
    plines = [l.rstrip("\n") for l in f if l.strip()]
print("  --- probe_bgrun_env_c36.log ---", flush=True)
for ln in plines:
    print("    | " + ln[:200], flush=True)
child_val = next((l.split("=", 1)[1] for l in plines if l.startswith("CHILD_BGRUN_LOG=")), "")
end_line = next((l for l in plines if l.startswith("BGRUN END") or l.startswith("BGRUN TIMEOUT")), "")
gate("G3 bgrun child sees BGRUN_LOG = its OWN runner's --log path",
     os.path.basename(probe_log) in child_val and "None" not in child_val,
     f"child read {child_val}")
gate("G4 bgrun still ends the log with a BGRUN END line (end-to-end)",
     end_line.startswith("BGRUN END"), end_line or "no END/TIMEOUT line in the probe log")
gate("G5 this runner's own environment carries BGRUN_LOG (direct child case)",
     bool(os.environ.get("BGRUN_LOG")), repr(os.environ.get("BGRUN_LOG")))

# ---------------------------------------------------------------- 3. M1 - the four logs STATUS calls END-less
print("=== M1: the four logs STATUS NEXT item (e) says lost their BGRUN END guarantee ===", flush=True)
for n in ("diag_fstunnelterm_v2_panelcost", "p2_open_copy", "prose_cycle25", "wait_runner_exit"):
    p = os.path.join(BENCH, n + ".log")
    if not os.path.exists(p):
        print(f"  {n}.log: MISSING", flush=True)
        continue
    with open(p, encoding="utf-8", errors="replace") as f:
        ls = [l.rstrip("\n") for l in f if l.strip()]
    mt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(p)))
    has_end = any(l.startswith("BGRUN END") or l.startswith("BGRUN TIMEOUT") for l in ls)
    has_detach = any(l.startswith("BGRUN DETACH") for l in ls)
    print(f"  {n}.log  lines={len(ls)} mtime={mt} has_END={has_end} has_DETACH_line={has_detach}", flush=True)
    print(f"      first: {ls[0][:170]}", flush=True)
    print(f"      last : {ls[-1][:170]}", flush=True)

# ---------------------------------------------------------------- 4. F1-F4, the stall reviewer's probes
print("=== F1-F4: the stall reviewer's falsification probes (peer_stall_c35.log:50-53) ===", flush=True)
r = run(["powershell", "-NoProfile", "-Command",
         "Get-CimInstance Win32_Process -Filter 'ProcessId=11536' | "
         "Select-Object ProcessId,CreationDate,CommandLine | Format-List | Out-String -Width 220"], timeout=90)
p11536 = (r.stdout or "").strip()
print("  [F1 probe] Get-CimInstance Win32_Process -Filter \"ProcessId=11536\" ->", flush=True)
print("    | " + (p11536.replace("\n", "\n    | ") if p11536 else "(no row: pid 11536 does not exist now)"), flush=True)
alive_11536 = "11536" in p11536

crl = os.path.join(BENCH, "cycle_runner.log")
stop_hits = []
if os.path.exists(crl):
    with open(crl, encoding="utf-8", errors="replace") as f:
        for i, ln in enumerate(f, 1):
            if "RUNNER STOP" in ln:
                stop_hits.append(f"{i}: {ln.strip()[:150]}")
    crl_mt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(crl)))
else:
    crl_mt = "(missing)"
print(f"  [F2/F3 probe] cycle_runner.log mtime={crl_mt}, RUNNER STOP lines={len(stop_hits)}", flush=True)
for h in stop_hits[-3:]:
    print("    | " + h, flush=True)

r = run(["powershell", "-NoProfile", "-Command",
         "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'cycle_runner' } | "
         "Select-Object ProcessId,CreationDate | Format-List | Out-String -Width 200"], timeout=90)
live_runner = (r.stdout or "").strip()
print("  [F4 probe] live cycle_runner.py processes ->", flush=True)
print("    | " + (live_runner.replace("\n", "\n    | ") if live_runner else "(none)"), flush=True)

c21 = os.path.join(BENCH, "cycle_21.log")
c21_end = "(missing)"
if os.path.exists(c21):
    with open(c21, encoding="utf-8", errors="replace") as f:
        ls = [l.rstrip("\n") for l in f if l.strip()]
    c21_end = "HAS BGRUN END/TIMEOUT" if any(l.startswith(("BGRUN END", "BGRUN TIMEOUT")) for l in ls) else "no END line"
    print(f"  [F4 probe] cycle_21.log lines={len(ls)} -> {c21_end}; last: {ls[-1][:150]}", flush=True)

wre = os.path.join(BENCH, "wait_runner_exit.log")
wre_end = ""
if os.path.exists(wre):
    with open(wre, encoding="utf-8", errors="replace") as f:
        ws = [l.rstrip("\n") for l in f if l.strip()]
    wre_end = ws[-1] if ws else ""
print(f"  [F2 cross-check] wait_runner_exit.log (the bgrun job of pid 11536) last line: {wre_end}", flush=True)

print(f"  F1 satisfied (pid 11536 row exists with a CreationDate != 2026-09-18 19:33:35): "
      f"{'see the row above' if alive_11536 else 'NO - no such process now, so F1 cannot be evaluated'}", flush=True)
print(f"  F2 satisfied (pid gone AND no RUNNER STOP after 19:33:35): "
      f"{not alive_11536 and not stop_hits}", flush=True)
print(f"  F3 satisfied (pid alive AND a RUNNER STOP exists): {alive_11536 and bool(stop_hits)}", flush=True)
print(f"  F4 satisfied (no live cycle_runner AND cycle_21.log has no BGRUN END): "
      f"{(not live_runner) and c21_end == 'no END line'}", flush=True)

# ---------------------------------------------------------------- summary
npass = sum(1 for _, ok, _ in gates if ok)
print(f"=== repair_c36_selftest: {npass} pass, {len(gates) - npass} fail ===", flush=True)
sys.exit(0 if npass == len(gates) else 1)
