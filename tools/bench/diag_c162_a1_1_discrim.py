# ---
# labview: none
# hardware: none
# evidence: archive/peer/2026-10-10-c162-a1-1-checklaunch.md:84-94
# ---
"""Card 162-a1-1: the review's cheapest discriminating test (archive/peer/2026-10-10-c162-a1-1-checklaunch.md:84-94), OFFLINE, writes nothing.
In this process only, stage_prerun.unverified_card_names is replaced to return (['CEN2 new-object census'], None) (a TRUE label prefix), then
check_launch runs on the exact command of diag_c162_a1_1_checklaunch.log:3. Also prints the prerun_records rows for the scratch recipe's sha256.
PREDICTION (claim 4): ALLOW. Review's alternative: REFUSE 'no prerun PASS record'."""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stage_prerun as P  # noqa: E402

CMD = ("py tools/bgrun.py --material --max-min 50 --unverified-card tools/bench/cards/task_162-a1-1.json --log tools/bench/diag_c161_p5s02b_scratch.log "
       "-- py -u tools/recipes/stage_d1_ring_p5s02b_scratch.py")
SCR = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s02b_scratch.py")
sha = P.sha256(SCR)
rows = [r for r in P.read_records() if r.get("sha256") == sha]
print("FACT scratch sha256 {0}; records for it: {1}".format(sha[:12], [(r.get("kind"), r.get("status"), r.get("iso"), r.get("dry_rule")) for r in rows]),
      flush=True)
P.unverified_card_names = lambda cmd: (["CEN2 new-object census"], None)
ok, why = P.check_launch(CMD)
print("{0} {1}".format("ALLOW" if ok else "REFUSE", why.strip()), flush=True)
g = [("check_launch with a true CEN2 prefix ALLOW (claim 4)", ok)]
for lab, v in g:
    print("GATE {0} | {1}".format("PASS" if v else "FAIL", lab), flush=True)
nf = sum(1 for _, v in g if not v)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if nf == 0 else "FAIL", "gates": {"pass": len(g) - nf, "fail": nf},
                              "first_fail": next((lab for lab, v in g if not v), None), "artefacts": []}), flush=True)
sys.exit(1 if nf else 0)
