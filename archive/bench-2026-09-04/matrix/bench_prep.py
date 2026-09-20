"""bench_prep.py — make LabVIEW ready for the next matrix cell, recovering if needed.

  py tools\\bench\\bench_prep.py            # revert GUIBENCH_v0, ensure its BD is open, COM answers
  py tools\\bench\\bench_prep.py --restart  # force a LabVIEW restart first

Steps: (1) kill stray python; (2) Esc to clear any menu state; (3) COM alive? else restart
LabVIEW; (4) close any BENCH_*/stray VI windows, delete leftover BENCH_*.vi; (5) revert
GUIBENCH_v0 and open its block diagram; (6) report window list + ExecState.
Prints one JSON line so the caller can log it.
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

PROJECT = os.path.dirname(os.path.dirname(HERE))
TARGET = os.path.join(g.CLAUDEDEV, "GUIBENCH_v0.vi")
LV_EXE = r"C:\Program Files\National Instruments\LabVIEW 2026\LabVIEW.exe"


def ps(*args):
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
           "& .\\tools\\lv_gui.ps1 " + " ".join(a if a.replace("-", "").replace(".", "").isalnum()
                                                else f'"{a}"' for a in args)]
    r = subprocess.run(cmd, cwd=PROJECT, capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


def com_alive(timeout_s=40):
    """Alive = Application.Version answers AND a real VI Run (exec_state of the bench VI) returns
    within RUN_PROBE_S. Two 180 s Run hangs on 2026-09-05 passed the Version check; the probe runs
    in a child process so a hung Run can be killed and answered with a LabVIEW restart."""
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        try:
            g._lv = None
            g.lv().Version
            break
        except Exception:
            time.sleep(4)
    else:
        return False
    probe = [sys.executable, "-c",
             "import sys; sys.path.insert(0, r'%s'); import gscript as g; g._lv=None; print(g.exec_state(r'%s'))"
             % (os.path.dirname(HERE), TARGET)]
    try:
        r = subprocess.run(probe, cwd=PROJECT, capture_output=True, text=True, timeout=RUN_PROBE_S)
        return r.returncode == 0 and r.stdout.strip() in ("0", "1")
    except subprocess.TimeoutExpired:
        return False


RUN_PROBE_S = 60


def restart_labview():
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"], capture_output=True)
    time.sleep(5)
    subprocess.run(["powershell", "-NoProfile", "-Command", f"Start-Process '{LV_EXE}'"], capture_output=True)
    time.sleep(45)


def main():
    out = {"restarted": False, "actions": []}
    # Kill stray python COM clients, but never ourselves or our parent (matrix_run.py is python
    # too — the first smoke run killed its own driver here, 2026-09-05).
    # Never the driver (matrix_run.py) or a verifier — a cell that decides to run bench_prep itself
    # would otherwise kill the driver that is waiting on it (suspected cause of three silent driver
    # deaths on 2026-09-05). Only stray gscript/COM clients are fair game.
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    f"Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object {{ "
                    f"$_.ProcessId -ne {os.getpid()} -and $_.ProcessId -ne {os.getppid()} -and "
                    f"$_.CommandLine -notlike '*matrix_run*' -and $_.CommandLine -notlike '*verify_op*' -and "
                    f"$_.CommandLine -notlike '*bench_prep*' }} | ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force }}"],
                   capture_output=True)
    # Orphaned benchmark cells (a `claude -p "You are benchmark cell ..."` whose driver died) would
    # drive the GUI concurrently with the next cell: end them first (their run is invalid anyway).
    orphan = subprocess.run(["powershell", "-NoProfile", "-Command",
                             "Get-CimInstance Win32_Process -Filter \"Name='claude.exe'\" | Where-Object "
                             "{ $_.CommandLine -like '*You are benchmark cell*' } | ForEach-Object "
                             "{ taskkill /F /T /PID $_.ProcessId | Out-Null; $_.ProcessId }"],
                            capture_output=True, text=True)
    if orphan.stdout.strip():
        out["actions"].append("killed orphan cell pid " + " ".join(orphan.stdout.split()))
    try:
        ps("-Action", "key", "-Key", "esc")
    except Exception:
        pass
    if "--restart" in sys.argv or not com_alive():
        restart_labview(); out["restarted"] = True
        if not com_alive(90):
            out["error"] = "LabVIEW not answering after restart"; print(json.dumps(out)); return 2
    # stray scratch VIs
    for f in os.listdir(g.CLAUDEDEV):
        if f.startswith("BENCH_") and f.endswith(".vi"):
            p = os.path.join(g.CLAUDEDEV, f)
            try:
                g.close_panel(p)
            except Exception:
                pass
            try:
                os.remove(p); out["actions"].append(f"deleted {f}")
            except Exception as e:
                out["actions"].append(f"could not delete {f}: {e}")
    # bench VI: revert + open panel + open BD
    g.open_panel(TARGET)
    time.sleep(1.5)        # 2026-09-05 00:08: revert immediately after OpenFrontPanel hung 180 s
    try:
        g.revert(TARGET)
    except Exception as e:
        out["actions"].append(f"revert: {e}")
    wins = ps("-Action", "windows")
    if "GUIBENCH_v0.vi Block Diagram" not in wins:
        ps("-Action", "focus", "-Title", "GUIBENCH_v0.vi Front Panel")
        time.sleep(0.4)
        ps("-Action", "keys", "-Key", "^e", "-WaitMs", "1800", "-Exception", "Approved",
           "-Evidence", "bench prep: open GUIBENCH BD")
        wins = ps("-Action", "windows")
        out["actions"].append("opened BD")
    out["bd_open"] = "GUIBENCH_v0.vi Block Diagram" in wins
    # Leave the BLOCK DIAGRAM in front: the first matrix cell (haiku-low, 2026-09-05) started with
    # the front panel on top and never found the diagram again.
    ps("-Action", "focus", "-Title", "GUIBENCH_v0.vi Block Diagram")
    time.sleep(0.3)
    wins = ps("-Action", "windows")
    # A cell may leave the floating Context Help window open (haiku-low did); it can cover targets
    # for the next cell. Ctrl+H toggles it off.
    if "Context Help" in wins:
        ps("-Action", "keys", "-Key", "^h", "-WaitMs", "600", "-Exception", "Approved",
           "-Evidence", "bench prep: close stray Context Help")
        ps("-Action", "focus", "-Title", "GUIBENCH_v0.vi Block Diagram")
        wins = ps("-Action", "windows")
        out["actions"].append("closed Context Help" if "Context Help" not in wins else "Context Help still open")
    out["exec_state"] = g.exec_state(TARGET)
    out["windows"] = [w for w in wins.splitlines() if w.strip()]
    print(json.dumps(out, ensure_ascii=False))
    return 0 if out["bd_open"] and out["exec_state"] == 1 else 1


if __name__ == "__main__":
    sys.exit(main())
