# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c156_p5s02a_scratch.log:553-555
# ---
r"""prep_c158_a3_1_census - card 158-a3-1 (PD386(c)): write the c158-a2-2 scratch's MEASURED new-object census into plan_ring_p5s02a_pred.json
`census` with `census_overall: MEASURED-SCRATCH` (the precedent tools/bench/diag_c148_a2_4_census.py:52, its parse now the shared
stagekit.scratch_census). No number is typed: the census is the ONE 'CENSUS-ALL new uids by class (every class)' line of the LAST segment
of diag_c156_p5s02a_scratch.log (the c158-a2-2 run) and must equal diag_c156_p5s02a_scratch_sum.json census_all.new_by_class. ALL classes
are written (as the precedent): RingSession.SRC = the pred's census classes, so CEN2 then compares every class.
Only `census`, `census_overall`, `census_source` change; plan md5 key unchanged.
PREDICTION: C0-C3 PASS.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c158_a3_1_census.log -- py -u tools/bench/prep_c158_a3_1_census.py"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K  # noqa: E402
import protocol  # noqa: E402

LOG, SJ = os.path.join(K.BENCH, "diag_c156_p5s02a_scratch.log"), os.path.join(K.BENCH, "diag_c156_p5s02a_scratch_sum.json")
PRED, PLAN = os.path.join(K.BENCH, "plan_ring_p5s02a_pred.json"), os.path.join(K.BENCH, "plan_ring_p5s02a.json")
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)


gate("C0 inputs md5 == card (pred 31d8e9be, plan 4284c22a)", K.md5(PRED).startswith("31d8e9be") and K.md5(PLAN).startswith("4284c22a"), (K.md5(PRED), K.md5(PLAN)))
meas, ln_no, seg0 = K.scratch_census(LOG, SJ)
gate("C1 one CENSUS-ALL line in the last segment (from line {0}) == the run summary".format(seg0), ln_no == 555, (ln_no, meas))
if all(ok for _l, ok in gates):
    p = K.jload(PRED)
    json.dump(p, open(os.path.join(K.BENCH, "sim", "ring_p5s02a_c158", "pred_before_a3.json"), "w", encoding="utf-8"), indent=1)
    old = {"census": p.get("census"), "census_overall": p.get("census_overall")}
    p["census"] = dict(sorted(meas.items()))
    p["census_overall"] = "MEASURED-SCRATCH"
    p["census_source"] = {"card": "158-a3-1", "decided": "PD386(c): the c158-a2-2 scratch census becomes the retry's prediction; CEN2 requires equality",
                          "log": "tools/bench/diag_c156_p5s02a_scratch.log", "line": ln_no, "segment_from": seg0, "log_md5": K.md5(LOG),
                          "expect": "CENSUS-ALL new uids by class (every class)",
                          "what": "stagekit.census_gate counts NEW uids per class (after - before); re-used uids are not new", "previous": old}
    json.dump(p, open(PRED, "w", encoding="utf-8"), indent=1)
    chk = K.jload(PRED)
    gate("C2 pred census written == measured; census_overall MEASURED-SCRATCH", chk["census"] == meas and chk["census_overall"] == "MEASURED-SCRATCH", K.md5(PRED))
    orig = K.jload(PRED.replace("plan_ring_p5s02a_pred.json", "sim/ring_p5s02a_c158/pred_before_a3.json"))
    changed = sorted(k for k in set(chk) | set(orig) if chk.get(k) != orig.get(k))
    gate("C3 plan md5 key unchanged; only census / census_overall / census_source differ from the copy taken before", chk["plan"]["md5"] == K.md5(PLAN)
         and changed == ["census", "census_overall", "census_source"], changed)
    print("  FACT measured new-by-class {0} (log line {1})".format(json.dumps(meas, sort_keys=True), ln_no), flush=True)
n = sum(1 for _l, ok in gates if ok)
ff = next((lab for lab, ok in gates if not ok), None)
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, [{"path": "tools/bench/plan_ring_p5s02a_pred.json", "md5": K.md5(PRED)}] if ff is None else [])),
      flush=True)
sys.exit(0 if ff is None else 1)
