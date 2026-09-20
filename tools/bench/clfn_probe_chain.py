"""clfn_probe_chain.py - which import-wizard functional global makes NI Create.vi kill LabVIEW?
Three variants, a fresh LabVIEW for each (lv_restart), then clfn_sample.py --set <globals>; after each, is LabVIEW alive?"""
import os, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)


def run(args, timeout, tag):
    try:
        r = subprocess.run(args, timeout=timeout, cwd=ROOT); rc = r.returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"{tag} rc {rc}", flush=True); return rc


VARIANTS = (("D Path only (GPU dll)", "Path", []),
            ("E basic4 kernel32/GetTickCount", "Function Name,Path,Calling Convention,Reentrant", ["--dll", r"C:\Windows\System32\kernel32.dll", "--fn", "GetTickCount"]))
for tag, sets, extra in VARIANTS:
    print("\n===== variant", tag, flush=True)
    run([sys.executable, os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart")
    run([sys.executable, "-u", os.path.join(TOOLS, "bench", "clfn_sample.py"), "--set", sets] + extra, 600, "sample " + tag)
    alive = subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-Process LabVIEW -ErrorAction SilentlyContinue) -ne $null"],
                           capture_output=True, text=True).stdout.strip()
    print("LabVIEW alive after", tag, ":", alive, flush=True)
