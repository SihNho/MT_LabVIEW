"""spec_chain.py - self-healing runner for the SPEC wiring reads: kill any stalled reader, restart LabVIEW, run the stages
(each resumes past the VIs already saved), and if a stage produces no log line for STALL_S seconds kill it, restart LabVIEW
and retry once. Run under bgrun (process-level deadline is still the guarantee):
  py tools/bgrun.py --max-min 90 --log tools/bench/spec_chain.log -- py -u tools/bench/spec_chain.py
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
STALL_S = 150
STAGES = [("spec_read", os.path.join(HERE, "spec_read.py"), os.path.join(HERE, "spec_read_stage.log")),
          ("spec_read_more", os.path.join(HERE, "spec_read_more.py"), os.path.join(HERE, "spec_read_more_stage.log"))]


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def kill_readers():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'spec_read' -and $_.ProcessId -ne %d } | "
                          "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue; $_.ProcessId }" % os.getpid()],
                         capture_output=True, text=True, timeout=60)
    log("killed readers:", out.stdout.split())


def restart_labview():
    log("restarting LabVIEW")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "lv_restart.py")], capture_output=True, text=True, timeout=400)
    log("lv_restart rc", r.returncode, (r.stdout + r.stderr)[-300:].replace("\n", " | "))


def run_stage(name, script, logfile):
    f = open(logfile, "a", encoding="utf-8")
    p = subprocess.Popen([sys.executable, "-u", script], stdout=f, stderr=subprocess.STDOUT, cwd=ROOT)
    last = os.path.getsize(logfile); t_last = time.time()
    while p.poll() is None:
        time.sleep(5)
        sz = os.path.getsize(logfile)
        if sz != last:
            last, t_last = sz, time.time()
        elif time.time() - t_last > STALL_S:
            log(f"{name}: STALL ({STALL_S}s without a log line) - killing pid {p.pid}")
            subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
            f.close(); return "stalled"
    f.close()
    log(f"{name}: exit {p.returncode}")
    return "ok" if p.returncode == 0 else "failed"


def main():
    kill_readers()
    restart_labview()
    for name, script, logfile in STAGES:
        for attempt in (1, 2):
            log(f"== {name} attempt {attempt}")
            r = run_stage(name, script, logfile)
            if r == "ok":
                break
            log(f"{name}: {r}; see {logfile}")
            restart_labview()
        else:
            log(f"{name}: gave up after 2 attempts")
    log("CHAIN DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
