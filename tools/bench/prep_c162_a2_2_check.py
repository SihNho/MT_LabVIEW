# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_162-a2-2.md
# ---
r"""prep_c162_a2_2_check - card 162-a2-2 step 1 (OFFLINE, no LabVIEW, no COM). A MEASUREMENT, no edit.
(a) fresh md5 of the five files pinned at selftest_c161_delckpt.py:137-138 vs the pins written there;
(b) JSON top-level key compare plan_ring_p5s02b_pred.json (now) vs sim/ring_p5s02b_c162/pred_before_a1_2.json (before card 162-a1-2).
Prior art: prep_c162_a2_1_pinsweep.py did the full ast sweep (log :41-45); this re-reads only the delckpt pins. md5 + Gates CALLED from
tools/invcheck.py. PREDICTION CONTRACT: G1 the only unequal pin is plan_ring_p5s02b_pred.json a1fd43fb -> 4cef0a8c; G2 before-file md5
a1fd43fb; G3 the differing keys are exactly census, census_overall, census_source (none added / removed).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c162_a2_2_check.log -- py -u tools/bench/prep_c162_a2_2_check.py"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import invcheck as IC                                                                       # noqa: E402  md5 + Gates (shared)

PINS = {"tools/stagesim.py": "95a162ba", "tools/stagekit.py": "9b8f82c1", "tools/stage_prerun.py": "7605116f",
        "tools/bench/plan_ring_p5s02b.json": "f4520b10", "tools/bench/plan_ring_p5s02b_pred.json": "a1fd43fb"}  # as at selftest_c161_delckpt.py:137-138
BEFORE = "tools/bench/sim/ring_p5s02b_c162/pred_before_a1_2.json"
NOW = "tools/bench/plan_ring_p5s02b_pred.json"
P = lambda r: os.path.join(ROOT, r)

G = IC.Gates()
got = dict((k, IC.md5(P(k))[:8]) for k in PINS)
for k in sorted(PINS):
    print("PIN | {0} | pinned {1} | now {2} | {3}".format(k, PINS[k], got[k], "EQUAL" if got[k] == PINS[k] else "STALE"), flush=True)
stale = sorted(k for k in PINS if got[k] != PINS[k])
G("G1 only unequal pin = pred a1fd43fb -> 4cef0a8c", stale == [NOW] and got[NOW] == "4cef0a8c", stale)
G("G2 before-file md5 = a1fd43fb", IC.md5(P(BEFORE))[:8] == "a1fd43fb", IC.md5(P(BEFORE)))
a, b = json.load(open(P(BEFORE), encoding="utf-8")), json.load(open(P(NOW), encoding="utf-8"))
diff = sorted(k for k in set(a) | set(b) if a.get(k, "<absent>") != b.get(k, "<absent>"))   # changed OR added OR removed
print("FACT keys before {0} / now {1}; only-before {2}; only-now {3}; differ {4}".format(
    len(a), len(b), sorted(set(a) - set(b)), sorted(set(b) - set(a)), diff), flush=True)
# run 1 (11:33:23) required equal key sets; census_source is a key ADDED by 162-a1-2 (diag_c162_a1_2_facts.md:40 "changed keys exactly
# [census, census_overall, census_source]") - the gate now counts added keys as differing, removed keys must be none
G("G3 differing keys == census, census_overall, census_source; none removed", not (set(a) - set(b))
  and diff == ["census", "census_overall", "census_source"], diff)
print(G.result(), flush=True)
sys.exit(0 if not G.failed else 1)
