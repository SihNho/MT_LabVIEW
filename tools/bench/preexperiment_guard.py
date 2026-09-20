"""preexperiment_guard.py - at T+N minutes, make sure NO LabVIEW.exe is running before a real experiment.

User, 2026-09-17: "약 1시간 뒤에 실험 예정". The material session was told to release LabVIEW by T-20; this is the
mechanical backstop (CLAUDE.md: restart/kill authority is standing). It sleeps, then kills any LabVIEW.exe, verifies
none remains, and checks the working copy's md5. Run detached under bgrun:

  py tools/bgrun.py --detach --max-min 50 --log tools/bench/preexperiment_guard.log -- py -u tools/bench/preexperiment_guard.py 42
"""
import hashlib
import subprocess
import sys
import time

MAIN = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
EXPECT = "2a78e17c449cacdaf5da389818526859"


def lv_running():
    out = subprocess.run(["tasklist"], capture_output=True, text=True).stdout
    return "LabVIEW.exe" in out


def main():
    minutes = float(sys.argv[1]) if len(sys.argv) > 1 else 42.0
    print(f"sleeping {minutes} min", flush=True)
    time.sleep(minutes * 60)
    print(f"T+{minutes:.0f} check {time.strftime('%H:%M:%S')}", flush=True)
    if lv_running():
        print("LabVIEW STILL RUNNING - killing (standing restart/kill permission)", flush=True)
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Get-Process LabVIEW -ErrorAction SilentlyContinue | Stop-Process -Force"],
                       capture_output=True, text=True)
        time.sleep(5)
        print("after kill:", "STILL RUNNING" if lv_running() else "none", flush=True)
    else:
        print("no LabVIEW process - clean", flush=True)
    md5 = hashlib.md5(open(MAIN, "rb").read()).hexdigest()
    print(f"working-copy md5 {md5} ({'OK' if md5 == EXPECT else 'CHANGED!'})", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
