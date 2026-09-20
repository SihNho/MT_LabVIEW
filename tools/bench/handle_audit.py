"""handle_audit.py — where do LabVIEW's kernel handles come from? (rule verification, 2026-09-06)

Run through the deadline runner:
  py tools/bgrun.py --max-min 12 --log tools/bench/handle_audit.log -- py -u tools/bench/handle_audit.py

Phases (each prints LabVIEW HandleCount before/after and the delta):
  A  20x report() from THIS process (reporter op runs; refs cached in gscript._cache)
  B  a CHILD process doing 20x report() then exiting normally   -> does exit return handles?
  C  10x open_panel / revert / close_panel on a scratch copy of GUIBENCH_v0
  D  10x drop_subvi + revert on the scratch (a mutating erdosmiller op)
  E  a child doing report() in a loop, KILLED mid-work (taskkill /F)  -> leak from a dead client?
  F  20x lv_gui actions (windows/rect, no COM)                          -> GUI layer alone
Prediction contract: A grows a little (cached refs) and B returns to baseline (refs released at
exit); C/D small; E leaves handles behind (never released); F ~0. Whatever is observed decides the
rule text in CLAUDE.md.
"""
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

PROJECT = os.path.dirname(os.path.dirname(HERE))
T = os.path.join(g.CLAUDEDEV, "GUIBENCH_v0.vi")
SCR = os.path.join(g.CLAUDEDEV, "SCRATCH_handles.vi")
EM = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting\Create Index Array.vi"
g._run.__defaults__ = (6.0, 60.0)


def handles():
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "(Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1).HandleCount"],
                       capture_output=True, text=True)
    return int(r.stdout.strip() or 0)


def phase(name, fn):
    time.sleep(2); h0 = handles(); t0 = time.time()
    fn()
    time.sleep(3); h1 = handles()
    print(f"{name}: handles {h0} -> {h1}  delta {h1 - h0:+d}  ({time.time() - t0:.0f}s)", flush=True)


CHILD = ("import sys, os; sys.path.insert(0, r'%s'); import gscript as g; g._lv=None; T=r'%s'\n"
         "for i in range(%d): g.report(T, 'Invoke')\nprint('child done', flush=True)")


def main():
    g._lv = None
    print("baseline handles", handles(), flush=True)
    phase("A 20x report (this process)", lambda: [g.report(T, "Invoke") for _ in range(20)])

    def b():
        r = subprocess.run([sys.executable, "-c", CHILD % (os.path.dirname(HERE), T, 20)], capture_output=True, text=True, timeout=300)
        print("   child:", r.stdout.strip()[-40:], r.stderr.strip()[-80:], flush=True)
    phase("B child 20x report + clean exit", b)

    shutil.copyfile(T, SCR)

    def c():
        for _ in range(10):
            g.open_panel(SCR); g.revert(SCR); g.close_panel(SCR)
    phase("C 10x open_panel/revert/close_panel", c)

    def d():
        g.open_panel(SCR)
        for _ in range(10):
            g.drop_subvi(SCR, EM, 0, (300, 700)); g.revert(SCR)
        g.close_panel(SCR)
    phase("D 10x drop_subvi + revert (scratch)", d)

    def e():
        p = subprocess.Popen([sys.executable, "-c", CHILD % (os.path.dirname(HERE), T, 400)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(6)
        subprocess.run(["taskkill", "/F", "/PID", str(p.pid)], capture_output=True)
        p.wait()
        print("   child killed mid-loop", flush=True)
    phase("E child killed mid-work", e)

    def f():
        for _ in range(20):
            g._lv_gui("-Action", "windows")
    phase("F 20x lv_gui windows (no COM)", f)

    # after everything: does releasing this process's cached refs return handles? (measured by the runner's END line + a later manual read)
    try:
        os.remove(SCR); print("scratch deleted", flush=True)
    except Exception as ex:
        print("scratch delete:", str(ex)[:80], flush=True)
    print("final handles (this process still alive)", handles(), flush=True)


if __name__ == "__main__":
    main()
