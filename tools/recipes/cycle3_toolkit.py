"""cycle3_toolkit.py - ONE runner for the three stage-2 step-B toolkit items (docs/stage2-assembly-step-b.md, revised
route; CLAUDE.md usage discipline: one LabVIEW batch = one runner = one notification):
  1. OpForLoop_v1            build_opforloop_v1.py            (For-loop input tunnels by control name, indexing flags)
  2. register ops, ForLoop   build_opaddshiftreg_v0.py + build_opwiresr_v0.py with SR_SEED=For
                             (OpAddShiftRegF_v0, OpWireSRF_{LeftIn,RightIn,LeftOutNode,LeftOutCtl}_v0)
  3. StrToPath.vi            build_strtopath.py               (String To Path sub-VI for the replay loop)
Each item is its own process (a failure stops the chain: RECOVERY_LOCKED - the next batch is a reviewed one).
  py tools/bgrun.py --max-min 40 --log tools/bench/cycle3_toolkit.log -- py -u tools/recipes/cycle3_toolkit.py
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
ITEMS = [
    ("1 OpForLoop_v1", ["build_opforloop_v1.py"], {}),
    ("2a OpAddShiftRegF_v0", ["build_opaddshiftreg_v0.py"], {"SR_SEED": "For"}),
    ("2b OpWireSRF_*_v0", ["build_opwiresr_v0.py"], {"SR_SEED": "For"}),
    ("3 StrToPath.vi", ["build_strtopath.py"], {}),
]


def main():
    for name, args, env in ITEMS:
        print(f"\n################ {name}  {time.strftime('%H:%M:%S')}", flush=True)
        e = dict(os.environ); e.update(env); e["PYTHONIOENCODING"] = "utf-8"
        rc = subprocess.call([PY, "-u", os.path.join(HERE, args[0])] + args[1:], env=e)
        print(f"################ {name} -> rc {rc}  {time.strftime('%H:%M:%S')}", flush=True)
        if rc != 0:
            print(f"\nSTOP: {name} failed (rc {rc}). Nothing further built; next batch after review.", flush=True)
            return rc
    print("\nALL DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
