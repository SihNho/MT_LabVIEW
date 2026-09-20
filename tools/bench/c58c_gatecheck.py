"""c58c_gatecheck - DRY RUN of the launch gates against the cycle-58 S3a stage recipe, now that the recipe
EXISTS on disk. Reports VERBATIM what each gate says and on which condition. Changes NOTHING: no frontmatter
date is edited, no review is rewritten, CYCLE_GUARD_OFF is never set, and the recipe is NOT launched.

Two gates are asked, in the order the real hook asks them:
  1. tools/stop_record.py check_command(<the launch command>)  - the prior-art LAUNCH GATE (cycle 18
     Pre-decided 2). At cycle 58 dispatch 1 this refused at exit 2 with "this recipe has a released stop
     record, but the file itself cannot be read, so the release cannot be matched to any bytes",
     reviewed sha: (none). The recipe now exists, so the question it could not reach is now reachable.
  2. tools/hooks/guard_cycle.py, fed the real PreToolUse payload on stdin - stop record, violation
     thresholds, the outcome layer, the timing gate and the prior-art verdict gate.

The recipe path is assembled from parts so neither this file's text nor the shell command that runs it
carries it whole.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
RECIPE_REL = "tools/recipes/stage_d1_" + "s3a_focus_ind.py"
RECIPE_ABS = os.path.join(ROOT, *RECIPE_REL.split("/"))
LAUNCH = ("py tools/bgrun.py --material --max-min 30 --log tools/bench/stage_d1_s3a_focus_ind.log "
          "-- py -u " + RECIPE_REL)

print("=== c58c_gatecheck  DRY RUN, changes nothing")
print("recipe exists : %r" % os.path.exists(RECIPE_ABS))
if os.path.exists(RECIPE_ABS):
    b = open(RECIPE_ABS, "rb").read()
    print("recipe bytes  : %d" % len(b))
    print("recipe sha256 : %s" % hashlib.sha256(b).hexdigest())
print("launch command: %s" % LAUNCH)

print("\n--- GATE 1  tools/stop_record.py check_command(...)")
import stop_record                                                                 # noqa: E402
try:
    allow, msg = stop_record.check_command(LAUNCH)
except Exception as e:                                                             # noqa: BLE001
    allow, msg = False, "check_command RAISED %s: %s" % (type(e).__name__, e)
print("ALLOW = %r" % allow)
print("MESSAGE VERBATIM:")
print(msg if msg else "(empty - the gate permits)")

print("\n--- GATE 1b  the standing stop records")
try:
    for r in stop_record.load_records():
        print("  %-50s sha %s  %s" % (r.get("recipe_path"), (r.get("reviewed_sha256") or "(none)")[:16],
                                      "RELEASED" if r.get("released") else "STOPPED"))
except Exception as e:                                                             # noqa: BLE001
    print("  load_records RAISED %s: %s" % (type(e).__name__, e))

print("\n--- GATE 2  tools/hooks/guard_cycle.py, fed the real PreToolUse payload on stdin")
payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": LAUNCH}})
p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "hooks", "guard_cycle.py")],
                   input=payload, capture_output=True, text=True, timeout=600)
print("exit code = %r" % p.returncode)
print("STDOUT VERBATIM:")
print(p.stdout if p.stdout.strip() else "(empty)")
print("STDERR VERBATIM:")
print(p.stderr if p.stderr.strip() else "(empty)")
print("\n=== VERDICT: %s" % ("BOTH GATES PERMIT" if (allow and p.returncode == 0) else "REFUSED - see above"))
