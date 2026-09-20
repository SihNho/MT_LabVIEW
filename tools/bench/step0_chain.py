"""step0_chain.py - validate the diagram-membership method, and only if it passes, walk the main VI.

The gate matters: the tree reconstruction leans on Traverse ordering, so it is proven on VIs we built ourselves before an
hour is spent on a 170-diagram VI whose answer we cannot check independently.
  py tools/bgrun.py --max-min 55 --log tools/bench/step0.log -- py -u tools/bench/step0_chain.py
"""
import os, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
BENCH = os.path.join(TOOLS, "bench")


def run(args, timeout, tag):
    try:
        rc = subprocess.run([sys.executable] + args, timeout=timeout, cwd=ROOT).returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"\n#### {tag} rc {rc}", flush=True); return rc


run([os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart")
if run(["-u", os.path.join(BENCH, "diagram_tree_validate.py")], 600, "validate") != 0:
    print("GATE FAILED: not walking the main VI", flush=True); sys.exit(5)
run([os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart before the main walk")
rc = run(["-u", os.path.join(BENCH, "diagram_tree_main.py")], 3000, "main walk")
if rc == 1 or rc == 4:
    print("partial walk; the checkpoint lets a rerun resume", flush=True)
sys.exit(0)
