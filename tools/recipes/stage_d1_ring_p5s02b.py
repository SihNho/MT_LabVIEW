# ---
# labview: build
# hardware: none
# ---
r"""stage_d1_ring_p5s02b - card 160-c3-1 (WRITTEN, NOT LAUNCHED), RING P5-2 step 2 (docs/d1/ring-p5b.md PD388(a), PD390(c)(f), PD391): on the
saved p5s02a file (claudeDev\D1_ring_p5s02a_20261010_023239.vi 94ffff94, path/md5 read from the plan's base graph 7ac24924), apply the 20
actions of plan_ring_p5s02b.json = delete_wire w10394, A24..A40 (groups F3 G H) and the two PD391(a) sink-only stub deletes w24264 / w24300
before A32 / A39 (tools/bench/prep_c160_b3_1_mk.py; numbers in plan_ring_p5s02b_pred.json, prep_c160_c3_1_pred.py). Licence
plan_ring_p5s02b_licence.json; sink-gate census prep_c160_c3_1_session.json (0 rows).
Shape = the pair shape of stage_d1_ring_p5s02a.py on stagekit.RingSession (PD390(c), docs/script-writing.md rules 1-2): only plan / pred / licence
/ census file / names / output name differ; every gate is CALLED.
FRESH LabVIEW -> claudeDev\D1_ring_p5s02b_<ts>.vi (rule-6 GUI save, ExecState 0 by design) = an in-between file of step P5-2 (not counted,
D-2026-10-02-02). The FIRST run is the full SCRATCH run on a byte copy (stage_d1_ring_p5s02b_scratch.py). ROWS ONLY FROM PLAN; expected values
only from PRED.
PREDICTION (numbers in PRED): SG 0 sink gates; L1 20 actions -> 10 ops == pred kinds; E1 every checkpoint [0,2,3,5,7,9,10] == sim; NG; PRIM; FR;
D; TD; CEN2 (Wire by ENDS, PD389(b); census UNPREDICTED until the scratch measures it); PB by POSITION (FATAL, before save); HB handles <= +700;
PS saved, input unchanged.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/launch_c161_p5s02b.log -- py -u tools/recipes/stage_d1_ring_p5s02b.py"""
import os, sys                                                                      # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402

# ---- INPUTS -------------------------------------------------------------------------------------------------------------------------
PLAN = os.path.join(K.BENCH, "plan_ring_p5s02b.json")                               # ONE literal each: stage_prerun.plan_files reads them
PRED = os.path.join(K.BENCH, "plan_ring_p5s02b_pred.json")
LICENCE = os.path.join(K.BENCH, "plan_ring_p5s02b_licence.json")
SG_CENSUS_FILE = os.path.join(K.BENCH, "prep_c160_c3_1_session.json")
NAME, KEY, CARD = "D1_ring_p5s02b", "ring_p5s02b", "card 160-c3-1 RING P5-2 step 2"
OUT_JSON = os.path.join(K.BENCH, "launch_c161_p5s02b.json")
ES_TEXT = "after all rows (ExecState 0 expected: P5-2 step 2's in-between file is broken by design)"
LEVEL = "STRUCTURAL, in-between file of P5 (P5-2 step 2), broken by design, never run"

# ---- CALLS --------------------------------------------------------------------------------------------------------------------------
RS = K.RingSession(PLAN, PRED, LICENCE, SG_CENSUS_FILE)
BASE, DRY, SG_CENSUS, SGS, SINK_GATES, SINK_FNS = RS.BASE, RS.DRY, RS.SG_CENSUS, RS.SGS, RS.SINK_GATES, RS.SINK_FNS   # the scratch pair reads these


def body(s):
    print(__doc__, flush=True)
    RS.gate_l0(s)
    s.start()
    s.discard_work()
    h0 = RS.handles()
    c0 = RS.census_snapshot(s)                     # whole-VI read 1 (kept in the recipe source: stage_prerun X10 counts it here)
    RS.executor(s)
    real = RS.run(s)
    if real is None:                               # ExecStop: resume file + stop report already written
        return
    RS.gates_ng_fr_d(s, real)
    dc = RS.gate_cen2(s, c0, RS.census_snapshot(s))   # whole-VI read 2
    RS.gate_td(s, real)
    s.es(ES_TEXT)
    rk = RS.gate_pb(s, real)
    RS.finish(s, h0, rk, dc, KEY, LEVEL)


if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], NAME, preload=False, deadline_min=45, out_json=OUT_JSON, task=CARD)
    rc = K.run(body, st)
    DRY or SX.kill_labview_at_exit()
    sys.exit(rc)
