"""caseop_chain.py - fresh LabVIEW -> build OpBuildCase_v0 (erdosmiller Create Case Structure.vi) with the generic creator recipe.
The backend-selectable tracking subVI (TRACK_kernel_v1) needs a real Case Structure: the unselected backend must NOT execute."""
import os, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
for tag, args, to in (("lv_restart", [os.path.join(TOOLS, "lv_restart.py")], 400),
                      ("build_opcase", ["-u", os.path.join(TOOLS, "recipes", "build_opcreator.py"),
                                        "--creator", "Create Case Structure.vi", "--op", "OpBuildCase_v0", "--max-terms", "14"], 900)):
    try:
        rc = subprocess.run([sys.executable] + args, timeout=to, cwd=ROOT).returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"{tag} rc {rc}", flush=True)
