# ---
# labview: none
# hardware: none
# evidence: tools/hooks/guard_cycle.py:231-238
# ---
"""prep_c165_a3_3_release - card 165-3-3 (OFFLINE, read-only): the step-5 form of prep_c164_a3_4_release.py (calls only): the prior-art verdict of
archive/peer/2026-10-10-priorart-priorart-c165-a3-3-p5s02e.md as the gates read it (guard_cycle.released_slugs, guard_cycle.fixed_claim per recipe),
stop_record.record_state for every STOP RECORD of the two step-5 recipes (no stamp), and stage_prerun.check_launch on the full scratch command in
BOTH forms (the brief's: --unverified-card before `--`; step 4's: after the recipe path), plus the scratch log's absence.
PREDICTION: none for the verdict (read as found); both recipes' records listed with their state; check_launch printed per form."""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for _p in (ROOT, os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "hooks"), os.path.join(ROOT, "tools", "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import guard_cycle as GC  # noqa: E402
import stop_record as SR  # noqa: E402
import stage_prerun as P  # noqa: E402
import prep_c156_a1_1_lib as L  # noqa: E402  Gate (shared)

REV = os.path.join(ROOT, "archive", "peer", "2026-10-10-priorart-priorart-c165-a3-3-p5s02e.md")
RECIPES = ("tools/recipes/stage_d1_ring_p5s02e.py", "tools/recipes/stage_d1_ring_p5s02e_scratch.py")
CMDS = {"brief": "py tools/bgrun.py --material --max-min 50 --unverified-card tools/bench/cards/task_165-3-4.json --log tools/bench/diag_c165_p5s02e_scratch.log "
                 "-- py -u tools/recipes/stage_d1_ring_p5s02e_scratch.py",
        "step4": "py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c165_p5s02e_scratch.log "
                 "-- py -u tools/recipes/stage_d1_ring_p5s02e_scratch.py --unverified-card tools/bench/cards/task_165-3-4.json"}
g = L.Gate(fatal_default=False)
body = open(REV, encoding="utf-8", errors="replace").read() if os.path.exists(REV) else ""
print("REVIEW {0} exists {1}; PRIOR-ART lines {2}".format(os.path.relpath(REV, ROOT), bool(body), [ln for ln in body.splitlines() if ln.startswith("PRIOR-ART:")]), flush=True)
rel_ok, bad = GC.released_slugs(REV, body)
print("RELEASED {0} REJECTED {1} review_time {2}".format(sorted(rel_ok), bad, GC.review_time(REV, body)), flush=True)
for r in RECIPES:
    c, ok, why = GC.fixed_claim(REV, body, os.path.join(ROOT, r))
    print("FIXEDCLAIM {0} claimed {1} released {2} why '{3}'".format(r, c, ok, why), flush=True)
recs = SR.load_records()
n = 0
for i, rec in enumerate(recs):
    if SR._rel(rec.get("recipe_path")) in [SR._rel(x) for x in RECIPES]:
        kind, state, line, why, cur = SR.record_state(recs, i)
        n += 1
        print("STOPREC {0} reviewed_sha {1} review {2} -> kind {3} state {4} decision(build) {5} line '{6}' why '{7}'".format(
            rec.get("recipe_path"), (rec.get("reviewed_sha256") or "")[:12], rec.get("review_file"), kind, state,
            SR.DECISION.get((kind, state, "build")), line[:120], why[:200]), flush=True)
print("STOPREC count for the two recipes: {0}".format(n), flush=True)
print("SCRATCH LOG exists: {0}; launch card exists: {1}".format(os.path.exists(os.path.join(ROOT, "tools", "bench", "diag_c165_p5s02e_scratch.log")),
      os.path.exists(os.path.join(ROOT, "tools", "bench", "cards", "task_165-3-4.json"))), flush=True)
for k, cmd in CMDS.items():
    ok, why = P.check_launch(cmd)
    print("CHECKLAUNCH {0} {1} {2}".format(k, "ALLOW" if ok else "REFUSE", why.strip()[:900]), flush=True)
    g("check_launch {0} form evaluated".format(k), True)
sys.exit(g.result())
