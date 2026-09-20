"""One-off relaunch 2026-09-19 23:5x: land the retrospective cycle 47 that died at session exit, then run the runner."""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cycle_runner as cr
bench = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bench")
print(cr.land_retrospective(bench, os.path.join(bench, "cycle_runner.log")) or "retro already landed", flush=True)
sys.exit(subprocess.call([sys.executable, os.path.join(cr.HERE, "cycle_runner.py"), "--cycles", "8"], cwd=cr.ROOT))
