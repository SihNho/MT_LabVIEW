"""cycle3b_toolkit.py - ONE runner: OpMoveByIndex_v0 (the primitive copier) then StrToPath.vi (its functional test =
the cycle-3 item 3 that failed three times on the label route). Stops at the first non-zero rc.
  py tools/bgrun.py --max-min 25 --log tools/bench/cycle3b_toolkit.log -- py -u tools/recipes/cycle3b_toolkit.py
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ITEMS = [("1 OpMoveByIndex_v0", "build_opmovebyindex.py"), ("2 StrToPath.vi", "build_strtopath.py")]


def main():
    for name, script in ITEMS:
        print(f"\n################ {name}  {time.strftime('%H:%M:%S')}", flush=True)
        e = dict(os.environ); e["PYTHONIOENCODING"] = "utf-8"
        rc = subprocess.call([sys.executable, "-u", os.path.join(HERE, script)], env=e)
        print(f"################ {name} -> rc {rc}  {time.strftime('%H:%M:%S')}", flush=True)
        if rc != 0:
            print(f"\nSTOP: {name} failed (rc {rc}).", flush=True)
            return rc
    print("\nALL DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
