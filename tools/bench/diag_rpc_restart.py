r"""diag_rpc_restart.py - the reviewer's raw discriminator for run 4's 0x800706BA after a LabVIEW kill
(archive/peer/2026-09-15-opconstvalue-run4-rpc-after-restart-no-labview.md). NO preflight, NO retries: kill LabVIEW,
reset gscript, then Dispatch -> Application.Version -> g.op(OP) -> g.report(MAIN, 'StringConstant'), marking the LabVIEW
pid + process creation time and elapsed seconds at every boundary, printing repr/args/traceback of the first failure.

predict (H1, the reviewer's top rank): either Dispatch or the first cheap call fails / the pid vanishes early, and MAIN is
never reached. If op(OP) succeeds and only report(MAIN) fails, the MAIN hierarchy becomes the leading trigger.

  py tools/bgrun.py --max-min 8 --log tools/bench/diag_rpc_restart.log -- py -u tools/bench/diag_rpc_restart.py
"""
import os
import subprocess
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

OP = os.path.join(g.CLAUDEDEV, "OpConstValue_v1.vi")
MAIN = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
T0 = time.time()


def pid():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "$p = Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1; "
                          "if ($p) { '{0} {1}' -f $p.Id, $p.StartTime.ToString('HH:mm:ss') }"],
                         capture_output=True, text=True, timeout=30).stdout.strip()
    return out or "none"


def mark(what):
    print(f"   [{time.time() - T0:6.1f}s] {what}: LabVIEW {pid()}", flush=True)


def kill_reset():
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "$p = Get-Process LabVIEW -ErrorAction SilentlyContinue; if ($p) { Stop-Process -Id $p.Id -Force; Start-Sleep -Seconds 8 }"],
                   capture_output=True, text=True, timeout=60)
    g.reset()


def main():
    mark("start")
    if "--warm" in sys.argv:
        # run 2 (04:19) started with NO LabVIEW alive, so it never reproduced run 4's precondition: an instance launched
        # and used (cached op proxies) by THIS process, then killed, then relaunched by the same process.
        g.lv().Version; g.op(OP); n = len(g.report(MAIN, "StringConstant"))
        mark(f"warm phase done (report MAIN -> {n})")
    kill_reset()
    mark("after kill+reset")
    steps = [
        ("Dispatch", lambda: g.lv()),
        ("Application.Version", lambda: g.lv().Version),
        ("g.op(OP)", lambda: g.op(OP)),
        ("g.report(MAIN, StringConstant)", lambda: len(g.report(MAIN, "StringConstant"))),
        ("g.report(MAIN, StringConstant) again", lambda: len(g.report(MAIN, "StringConstant"))),
    ]
    for name, fn in steps:
        mark(f"before {name}")
        try:
            r = fn()
            # never str() a dispatch object: win32com's __str__ INVOKES its default member (run 1 died exactly there)
            shown = r if isinstance(r, (int, float, str)) else type(r).__name__
            mark(f"after {name} -> {str(shown)[:40]}")
        except Exception as e:
            mark(f"FAILED {name}")
            print(f"OBSERVED EXC {name}: {e!r}\n   args={getattr(e, 'args', None)}\n{traceback.format_exc()[-1200:]}", flush=True)
            for k in range(4):
                time.sleep(15); mark(f"post-failure watch {k + 1}")
            return 1
    for k in range(2):
        time.sleep(15); mark(f"post-success watch {k + 1}")
    print("SUMMARY all five steps succeeded on the fresh instance (H1 not reproduced this run)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
