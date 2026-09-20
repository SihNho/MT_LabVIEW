import os, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
def run(args, timeout, tag):
    r = subprocess.run(args, timeout=timeout, cwd=ROOT); print(f"{tag} rc {r.returncode}", flush=True); return r.returncode
run([sys.executable, os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart")
for creator, op in (("Create Flatten to String.vi", "OpBuildFlatten_v0"), ("Create Unflatten from String.vi", "OpBuildUnflatten_v0")):
    run([sys.executable, os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart")          # fresh instance per op: no stale in-memory copies
    run([sys.executable, "-u", os.path.join(TOOLS, "recipes", "build_opcreator.py"), "--creator", creator, "--op", op, "--max-terms", "14"], 900, "build " + op)
