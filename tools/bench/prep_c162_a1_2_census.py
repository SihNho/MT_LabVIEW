# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c161_p5s02b_scratch.log:153
# ---
r"""prep_c162_a1_2_census - card 162-a1-2 (PD392(c)): write the step-2 scratch's MEASURED new-object census into plan_ring_p5s02b_pred.json
`census` with `census_overall: MEASURED-SCRATCH`. COPY of prep_c158_a3_1_census.py (card 158-a3-1, ran) with ONLY: log / sum / pred / plan
paths p5s02a -> p5s02b (log = the recipe's own LOG constant diag_c161_p5s02b_scratch.log), the md5 pins (pred a1fd43fb, plan f4520b10),
the expected line number (153), the before-copy dir (sim/ring_p5s02b_c162) and the census_source text. The parse is the shared
stagekit.scratch_census (the ONE 'CENSUS-ALL new uids by class (every class)' line of the LAST log segment, which the scratch computed from
its whole-VI graph reads before / after, == the run summary's census_all.new_by_class). No number is typed.
Only `census`, `census_overall`, `census_source` change; plan md5 key unchanged.
PREDICTION: C0-C3 PASS.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c162_a1_2_census.log -- py -u tools/bench/prep_c162_a1_2_census.py"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K  # noqa: E402
import protocol  # noqa: E402

LOG, SJ = os.path.join(K.BENCH, "diag_c161_p5s02b_scratch.log"), os.path.join(K.BENCH, "diag_c161_p5s02b_scratch_sum.json")
PRED, PLAN = os.path.join(K.BENCH, "plan_ring_p5s02b_pred.json"), os.path.join(K.BENCH, "plan_ring_p5s02b.json")
BEFORE = os.path.join(K.BENCH, "sim", "ring_p5s02b_c162", "pred_before_a1_2.json")
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)


gate("C0 inputs md5 == card (pred a1fd43fb, plan f4520b10)", K.md5(PRED).startswith("a1fd43fb") and K.md5(PLAN).startswith("f4520b10"), (K.md5(PRED), K.md5(PLAN)))
meas, ln_no, seg0 = K.scratch_census(LOG, SJ)
gate("C1 one CENSUS-ALL line in the last segment (from line {0}) == the run summary".format(seg0), ln_no == 153, (ln_no, meas))
if all(ok for _l, ok in gates):
    p = K.jload(PRED)
    os.makedirs(os.path.dirname(BEFORE), exist_ok=True)
    json.dump(p, open(BEFORE, "w", encoding="utf-8"), indent=1)
    old = {"census": p.get("census"), "census_overall": p.get("census_overall")}
    p["census"] = dict(sorted(meas.items()))
    p["census_overall"] = "MEASURED-SCRATCH"
    p["census_source"] = {"card": "162-a1-2", "decided": "PD392(c): the step-2 scratch census is recorded into the pred; CEN2 stays an equality",
                          "log": "tools/bench/diag_c161_p5s02b_scratch.log", "line": ln_no, "segment_from": seg0, "log_md5": K.md5(LOG),
                          "expect": "CENSUS-ALL new uids by class (every class)",
                          "what": "stagekit.census_gate counts NEW uids per class (after - before); re-used uids are not new", "previous": old}
    json.dump(p, open(PRED, "w", encoding="utf-8"), indent=1)
    chk = K.jload(PRED)
    gate("C2 pred census written == measured; census_overall MEASURED-SCRATCH", chk["census"] == meas and chk["census_overall"] == "MEASURED-SCRATCH", K.md5(PRED))
    orig = K.jload(BEFORE)
    changed = sorted(k for k in set(chk) | set(orig) if chk.get(k) != orig.get(k))
    gate("C3 plan md5 key unchanged; only census / census_overall / census_source differ from the copy taken before", chk["plan"]["md5"] == K.md5(PLAN)
         and changed == ["census", "census_overall", "census_source"], changed)
    print("  FACT measured new-by-class {0} (log line {1}); pred md5 a1fd43fb -> {2}".format(json.dumps(meas, sort_keys=True), ln_no, K.md5(PRED)), flush=True)
n = sum(1 for _l, ok in gates if ok)
ff = next((lab for lab, ok in gates if not ok), None)
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, [{"path": "tools/bench/plan_ring_p5s02b_pred.json", "md5": K.md5(PRED)}] if ff is None else [])),
      flush=True)
sys.exit(0 if ff is None else 1)
