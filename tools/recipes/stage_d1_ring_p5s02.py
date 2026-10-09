# ---
# labview: build
# hardware: none
# ---
r"""stage_d1_ring_p5s02 - card 155-a4-1 (WRITTEN, NOT LAUNCHED), RING P5-2 step 1 (docs/d1/ring-p5.md PD374(b)(d), PD376(d), PD378(c)): on the
ADOPTED P5-1 file (claudeDev\D1_ring_p5s01_20261009_124542.vi 7f2582ae, path/md5 read from the plan's base graph 6716c499), apply the actions of
plan_ring_p5s02.json = actions 1..29 / ops 1..19 of the P5-2 input plan plan_ring_p5s02_all.json (refnum SR on 1.7 + Dequeue (100 ms) + Release on
686; Case on 'timed out?'; #376 / #3052 / #3453 moved into its False frame and re-wired; t5; in-tunnels #24357 / #24361 / #25223; #376 'error in'
from LSR #24133), X10 MAIN 680.0 at the start 603.4 = measured P5-1 load 597.5 + op-0 read; planned DIRECTLY on the real P5-1 graph
(tools/bench/prep_c155_a4_1_mk.py, no rebase). X11 / licence plan_ring_p5s02_licence.json (prep_c155_a4_1_licence.py).
Shape = tools/recipes/stage_template_ring.py (INPUTS + CALLS into stagekit.RingSession), the same pair shape as stage_d1_ring_p5s01b.py: only plan
path / pred / licence / session table / names / output name differ (docs/script-writing.md rules 1-2).
Sink gates: one per census row of prep_c155_a4_1_session.json with needs_sink_gate (measured 0), read by script.
FRESH LabVIEW -> claudeDev\D1_ring_p5s02_<ts>.vi (rule-6 GUI save, ExecState 0 by design) = an in-between file of step P5 (P5-2 is cut by X10).
The FIRST run is the full SCRATCH run on a byte copy (stage_d1_ring_p5s02_scratch.py). ROWS ONLY FROM PLAN; expected values only from PRED.
PREDICTION (numbers in PRED): SG one declared sink gate per census row; L1 actions -> pred ops; E1 every checkpoint == sim; NG crossing tunnel
names == step files'; PRIM created primitives' labels == plan prims; FR created objects on the sim end's frames; D new/lost wires == sim's;
TD every base terminal that was wired stays wired, identities lost == plan deletes; CEN2 == pred census; PB cdiff(S1, end) slots == pred rows
by POSITION (FATAL, before save); HB handles <= +700; PS saved, input unchanged. X10 = pred memory_pred.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/launch_c155_p5s02.log -- py -u tools/recipes/stage_d1_ring_p5s02.py"""
import os, sys                                                                      # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402

# ---- INPUTS -------------------------------------------------------------------------------------------------------------------------
PLAN = os.path.join(K.BENCH, "plan_ring_p5s02.json")                                # ONE literal each: stage_prerun.plan_files reads them
PRED = os.path.join(K.BENCH, "plan_ring_p5s02_pred.json")
LICENCE = os.path.join(K.BENCH, "plan_ring_p5s02_licence.json")
SG_CENSUS_FILE = os.path.join(K.BENCH, "prep_c155_a4_1_session.json")
NAME, KEY, CARD = "D1_ring_p5s02", "ring_p5s02", "card 155-a4-1 RING P5-2 step 1"
OUT_JSON = os.path.join(K.BENCH, "launch_c155_p5s02.json")
ES_TEXT = "after all rows (ExecState 0 expected: P5-2 step 1's in-between file is broken by design)"
LEVEL = "STRUCTURAL, in-between file of P5 (P5-2 step 1 of 2), broken by design, never run"

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
