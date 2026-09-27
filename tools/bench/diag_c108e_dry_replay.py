"""diag_c108e_dry_replay - card 108-5 G3 negative: replay the diag_c108b_dry.log case (a top-level dry of
tools/recipes/stage_d1_l2a3.py whose row 2 is UNROUTABLE) against the patched tools/stage_prerun.py.

PRIOR ART: tools/bench/diag_c108b_dry.log (the case: FACT UNROUTABLE at :39, 'DRY PASS' at :42, PASS record at
prerun_records.jsonl:213); selftest_stage_prerun_c106e.py (same subprocess shape). No LabVIEW: stage_prerun --dry
replaces the COM layer. Records go to a TEMP file (PRERUN_RECORDS), so the real prerun_records.jsonl is not touched.

PREDICTION: R0 recipe md5 == 3fcefd3b... and plan md5 == 7cab639c... (the 108-2 inputs; else the replay is not the
case and the run says so); R1 the dry exits rc != 0; R2 its output carries an UNROUTABLE line and '=== DRY FAIL';
R3 the temp records file holds exactly one 'dry' record and its status is FAIL (no PASS record).
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P  # noqa: E402

RECIPE = os.path.join(ROOT, "tools", "recipes", "stage_d1_l2a3.py")
PLAN = os.path.join(ROOT, "tools", "bench", "plan_l2a3.json")
REC = os.path.join(os.environ.get("TEMP", "."), "c108e_dry_replay_records.jsonl")
res = []


def gate(label, ok, detail=""):
    res.append(bool(ok))
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


gate("R0 replay inputs == the 108-2 case (recipe 3fcefd3b, plan 7cab639c)",
     md5(RECIPE) == "3fcefd3bcc37bff171152b0ff8337bf8" and md5(PLAN) == "7cab639cb145113b86a152c49ec14b76",
     (md5(RECIPE), md5(PLAN)))
if os.path.exists(REC):
    os.remove(REC)
p = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "stage_prerun.py"), "--dry", RECIPE],
                   cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
                   env=dict(os.environ, PRERUN_RECORDS=REC), timeout=300)
out = p.stdout + p.stderr
for ln in out.splitlines():
    if "UNROUTABLE" in ln or ln.startswith("=== DRY") or ln.startswith("RESULT"):
        print("    | " + ln[:300], flush=True)
gate("R1 dry rc != 0", p.returncode != 0, "rc=%d" % p.returncode)
gate("R2 an UNROUTABLE line and '=== DRY FAIL' in the output",
     "UNROUTABLE acts" in out and "=== DRY FAIL" in out, "")
recs = [json.loads(x) for x in open(REC, encoding="utf-8")] if os.path.exists(REC) else []
gate("R3 exactly one dry record, status FAIL (no PASS record)",
     len(recs) == 1 and recs[0].get("kind") == "dry" and recs[0].get("status") == "FAIL",
     [(r.get("kind"), r.get("status"), (r.get("first_fail") or "")[:120]) for r in recs])
npass, nfail = sum(res), len(res) - sum(res)
first = None if all(res) else "R%d" % res.index(False)
print("=== %d pass / %d fail" % (npass, nfail), flush=True)
print(P.result_line(P.make_result(npass, nfail, first)), flush=True)
sys.exit(0 if nfail == 0 else 1)
