"""build_opqueue_all.py - run build_opqueue.py for obtain, enqueue, dequeue, release in sequence; stop at the first
failure (a cmd /c chain is mangled by Git Bash's path conversion, hence this runner).
  py tools/bgrun.py --max-min 25 --log tools/bench/build_opqueue.log -- py -u tools/recipes/build_opqueue_all.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for kind in ("obtain", "enqueue", "dequeue", "release"):
    print(f"\n######## {kind} ########", flush=True)
    rc = subprocess.call([sys.executable, "-u", os.path.join(HERE, "build_opqueue.py"), kind])
    if rc != 0:
        print(f"STOP: {kind} build returned {rc}", flush=True)
        sys.exit(rc)
print("\nALL FOUR QUEUE OPS BUILT", flush=True)
