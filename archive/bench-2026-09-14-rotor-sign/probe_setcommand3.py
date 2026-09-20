"""probe_setcommand3.py - READ-ONLY, NO HARDWARE: the SAVED front-panel values of a scratch copy of SetCommand.vi
(GetControlValue without running). If the author saved the VI after a real run, 'read buffer' / 'read buffer 2' still
hold a genuine controller reply, which fixes the reply format (hex digit count, terminator) without touching the rotor.
Also the Ring's numeric value and the numeric inputs' defaults.
  py tools/bgrun.py --max-min 5 --log tools/bench/probe_setcommand3.log -- py -u tools/bench/probe_setcommand3.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = r"C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Autonics Motor\SetCommand.vi"
S = os.path.join(g.CLAUDEDEV, f"SCRATCH_setcommand3_{os.getpid()}.vi")


def main():
    g._lv = None
    shutil.copyfile(SRC, S); time.sleep(0.3)
    try:
        vi = g.op(S)
        for name in ("VISA resource name", "Ring", "Numeric", "Baseline Startpoint", "Pos_degree", "read buffer", "read buffer 2", "*(type *) &x", "error out"):
            try:
                v = vi.GetControlValue(name)
                print(f"  {name!r:24s} = {v!r}" + (f"  (len {len(v)}, bytes {v.encode('latin-1', 'replace')!r})" if isinstance(v, str) else ""), flush=True)
            except Exception as e:
                print(f"  {name!r:24s} EXC {str(e)[:120]}", flush=True)
    finally:
        os.remove(S)
    return 0


if __name__ == "__main__":
    sys.exit(main())
