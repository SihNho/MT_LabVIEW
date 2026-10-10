# ---
# labview: build
# hardware: none
# ---
r"""stage_d1_ring_p5s02d - card 164-3-4 (WRITTEN, NOT LAUNCHED; re-made from card 164-a2-3's recipe for the re-made plan), RING P5-2 step 4
(docs/d1/ring-p5c.md PD397(d), PD398, PD399): on the saved p5s02c file (claudeDev\D1_ring_p5s02c_20261010_125755.vi 564d8cbe, path/md5 read
from the plan's base graph 3d5196ab), apply the 19 actions of plan_ring_p5s02d.json 97837e2a = groups J + K3 A53..A71 (J in the P4 delete
form, PD399(a): delete the scaffold stop wire #23489, delete_wire #23460, delete scaffold stop #23042 and in-tunnel #23501,
wire_remove_loose_ends #23519, Local read LR7 'records final (1.2 to 1.7)', Equal? EQ7 into the loop cond; K3: SR SK3 on loop #23041, init
const KI3, case tunnels OK3 / IK3 through register_end_case_border and the pass wire w_k3pass on frame #31517; tools/bench/prep_c164_a3_1_mk.py;
numbers in plan_ring_p5s02d_pred.json, prep_c164_a3_4_pred.py / _pd399.py). Licence plan_ring_p5s02d_licence.json; sink-gate census
prep_c164_a3_4_session.json (0 rows).
Shape = the pair shape of stage_d1_ring_p5s02c.py on stagekit.RingSession (PD390(c), docs/script-writing.md rules 1-2): only plan / pred / licence
/ census file / names / output name differ; every gate is CALLED.
FRESH LabVIEW -> claudeDev\D1_ring_p5s02d_<ts>.vi (rule-6 GUI save, ExecState 0 by design) = an in-between file of step P5-2 (not counted,
D-2026-10-02-02). The FIRST run is the full SCRATCH run on a byte copy (stage_d1_ring_p5s02d_scratch.py). ROWS ONLY FROM PLAN; expected values
only from PRED.
PREDICTION (numbers in PRED): SG 0 sink gates; L1 19 actions -> 15 ops == pred kinds; E1 every checkpoint [0,1,2,6,7,11,12,14,15] == sim; NG;
PRIM; FR; D; TD; CEN2 (Wire by ENDS, PD389(b); census UNPREDICTED until the scratch measures it); PB by POSITION (FATAL, before save); HB
handles <= +700; PS saved, input unchanged.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/launch_c164_p5s02d.log -- py -u tools/recipes/stage_d1_ring_p5s02d.py"""
import os, sys                                                                      # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402

# ---- INPUTS -------------------------------------------------------------------------------------------------------------------------
PLAN = os.path.join(K.BENCH, "plan_ring_p5s02d.json")                               # ONE literal each: stage_prerun.plan_files reads them
PRED = os.path.join(K.BENCH, "plan_ring_p5s02d_pred.json")
LICENCE = os.path.join(K.BENCH, "plan_ring_p5s02d_licence.json")
SG_CENSUS_FILE = os.path.join(K.BENCH, "prep_c164_a3_4_session.json")
NAME, KEY, CARD = "D1_ring_p5s02d", "ring_p5s02d", "card 164-3-4 RING P5-2 step 4"
OUT_JSON = os.path.join(K.BENCH, "launch_c164_p5s02d.json")
ES_TEXT = "after all rows (ExecState 0 expected: P5-2 step 4's in-between file is broken by design)"
LEVEL = "STRUCTURAL, in-between file of P5 (P5-2 step 4), broken by design, never run"

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
