# ---
# labview: none
# hardware: none
# evidence: tools/hooks/guard_cycle.py:231-238
# ---
"""prep_c164_a3_4_release - card 164-3-4 (OFFLINE, read-only): asks the gates' OWN functions whether the FIXED lines added to
archive/peer/2026-10-10-priorart-priorart-c164-a2-3-p5s02d.md release it: guard_cycle.released_slugs (the verdict gate, :749) and
guard_cycle.fixed_claim per recipe (premature_build's disposition exemption, :520), stop_record.record_state for each STOP RECORD of the
two recipes (no stamp: record_state writes nothing; stop_record.check_command would stamp tools/bench/stop_records.json, outside this
card's write globs), and stage_prerun.check_launch on the full scratch command. Calls only.
PREDICTION: released == {settled-already, contradicted}, rejected []; both recipes claimed AND released; both records state 'released'."""
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

REV = os.path.join(ROOT, "archive", "peer", "2026-10-10-priorart-priorart-c164-a2-3-p5s02d.md")
RECIPES = ("tools/recipes/stage_d1_ring_p5s02d.py", "tools/recipes/stage_d1_ring_p5s02d_scratch.py")
CMD = ("py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c164_p5s02d_scratch.log "
       "-- py -u tools/recipes/stage_d1_ring_p5s02d_scratch.py --unverified-card tools/bench/cards/task_164-3-5.json")
g = L.Gate(fatal_default=False)
body = open(REV, encoding="utf-8", errors="replace").read()
rel_ok, bad = GC.released_slugs(REV, body)
print("RELEASED {0} REJECTED {1} review_time {2}".format(sorted(rel_ok), bad, GC.review_time(REV, body)), flush=True)
g("V verdict gate: released_slugs == {settled-already, contradicted}, nothing rejected", rel_ok >= {"settled-already", "contradicted"} and not bad, (rel_ok, bad))
for r in RECIPES:
    c, ok, why = GC.fixed_claim(REV, body, os.path.join(ROOT, r))
    print("FIXEDCLAIM {0} claimed {1} released {2} why '{3}'".format(r, c, ok, why), flush=True)
    g("F premature_build disposition: {0} claimed and released".format(r), c and ok, why)
recs = SR.load_records()
for i, rec in enumerate(recs):
    if SR._rel(rec.get("recipe_path")) in [SR._rel(x) for x in RECIPES]:
        kind, state, line, why, cur = SR.record_state(recs, i)
        print("STOPREC {0} reviewed_sha {1} review {2} -> kind {3} state {4} decision(build) {5} line '{6}' why '{7}'".format(
            rec.get("recipe_path"), (rec.get("reviewed_sha256") or "")[:12], rec.get("review_file"), kind, state,
            SR.DECISION.get((kind, state, "build")), line[:120], why[:200]), flush=True)
        if rec.get("review_file", "").endswith("c164-a2-3-p5s02d.md"):
            g("S stop record {0}: state released".format(rec.get("recipe_path")), state == "released", state)
print("SCRATCH LOG exists: {0}; launch card exists: {1}".format(os.path.exists(os.path.join(ROOT, "tools", "bench", "diag_c164_p5s02d_scratch.log")),
      os.path.exists(os.path.join(ROOT, "tools", "bench", "cards", "task_164-3-5.json"))), flush=True)
ok, why = P.check_launch(CMD)
print("CHECKLAUNCH {0} {1}".format("ALLOW" if ok else "REFUSE", why.strip()[:900]), flush=True)
sys.exit(g.result())
