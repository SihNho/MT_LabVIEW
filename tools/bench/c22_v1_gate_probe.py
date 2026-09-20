r"""c22_v1_gate_probe.py - S5 of the cycle-22 third brief: DO BOTH LAUNCH GATES ALLOW the _v1 recipe?

Read-only with respect to LabVIEW: no LabVIEW, no motor, no serial, no camera, nothing launched. It asks the two
gates the same way they are asked at launch time and prints each verdict with its deciding line:

  1. `stop_record.check_command(<the exact _v1 launch command>)` - the prior-art LAUNCH GATE. NOTE this call may
     STAMP the release into the record (`_check` sets `released` when it is None and the review's FIXED:/REFUTED:
     lines validate) - that is the gate's own mechanism, not a hand edit of the store.
  2. `tools/hooks/guard_cycle.py` as a PreToolUse hook, the launch command on stdin as the real hook JSON.

It also prints record 2 (`_v0`) before and after plus the store's mtime, to show it was not touched.

MODELLED ON tools/bench/c20_release_probe.py (same two functions, same printing); this file adds the hook
subprocess and the record-2 untouched check, which that probe does not do.

  MATERIAL=1 py tools/bgrun.py --max-min 3 --log tools/bench/c22_v1_gate_probe.log -- py -u tools/bench/c22_v1_gate_probe.py
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import guard_cycle as G          # noqa: E402
import stop_record as S          # noqa: E402

REVIEW = os.path.join(ROOT, "archive", "peer", "2026-09-18-priorart-fstunnel-wirechecked.md")
RECIPE_REL = "tools/recipes/build_opfstunnel" + "term_v1.py"
RECIPE = os.path.join(ROOT, *RECIPE_REL.split("/"))
LAUNCH = ("py tools/bgrun.py --max-min 20 --log tools/bench/build_opfstunnel" + "term_v1_run1.log"
          " -- py " + RECIPE_REL)
STORE = os.path.join(ROOT, "tools", "bench", "stop_records.json")


def rec_of(path_frag, tag):
    try:
        for r in S.load_records():
            if path_frag in (r.get("recipe_path") or ""):
                print("  %s %s" % (tag, json.dumps({k: r.get(k) for k in
                                                    ("recipe_path", "review_file", "verdict", "reviewed_sha256",
                                                     "released")}, indent=1)[:700]), flush=True)
    except Exception as e:
        print("  %s LOAD EXC %s" % (tag, e), flush=True)


print("LAUNCH COMMAND UNDER TEST:\n  %s\n" % LAUNCH, flush=True)
print("store mtime BEFORE: %s" % os.path.getmtime(STORE), flush=True)
body = open(REVIEW, "r", encoding="utf-8").read()
ok, bad = G.released_slugs(REVIEW, body)
print("review        : %s" % os.path.relpath(REVIEW, ROOT), flush=True)
print("review_time   : %s" % (G.review_time(REVIEW, body),), flush=True)
print("RELEASED SLUGS: %d -> %s" % (len(ok), sorted(ok)), flush=True)
print("REJECTED      : %d -> %s" % (len(bad), bad), flush=True)
print("fixed_claim(_v1 recipe) (claimed, released, why): %s" % (G.fixed_claim(REVIEW, body, RECIPE),), flush=True)
print("recipe sha256 : %s" % S.sha256_of(RECIPE), flush=True)

print("\n--- records BEFORE the gate calls ---", flush=True)
rec_of("term_v0.py", "[v0 record 2]")
rec_of("term_v1.py", "[v1 record 3]")

print("\n=== GATE 1  stop_record.check_command ===", flush=True)
allow1, msg1 = S.check_command(LAUNCH)
print("VERDICT: %s" % ("ALLOW" if allow1 else "REFUSE"), flush=True)
print("message:\n%s" % (msg1 or "(empty - allowed)"), flush=True)

print("\n=== GATE 2  tools/hooks/guard_cycle.py (PreToolUse, stdin) ===", flush=True)
payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": LAUNCH}})
p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "hooks", "guard_cycle.py")],
                   input=payload, capture_output=True, text=True, timeout=600)
print("rc=%d" % p.returncode, flush=True)
print("VERDICT: %s" % ("ALLOW (rc=0, no block)" if p.returncode == 0 else "REFUSE"), flush=True)
print("stdout:\n%s" % (p.stdout or "(empty)"), flush=True)
print("stderr:\n%s" % (p.stderr or "(empty)"), flush=True)

print("\n--- records AFTER the gate calls ---", flush=True)
rec_of("term_v0.py", "[v0 record 2]")
rec_of("term_v1.py", "[v1 record 3]")
print("store mtime AFTER : %s" % os.path.getmtime(STORE), flush=True)
print("\nBOTH GATES ALLOW: %s" % (bool(allow1) and p.returncode == 0), flush=True)
sys.exit(0 if (allow1 and p.returncode == 0) else 2)
