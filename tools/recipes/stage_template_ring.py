# ---
# labview: build
# hardware: none
# ---
r"""stage_template_ring - TEMPLATE of a ring stage recipe as INPUTS + CALLS (card chat-T7, docs/script-writing.md, docs/d1/result-gates.md PD377).
A new batch writes tools/recipes/stage_d1_ring_<batch>.py with THIS shape: the INPUTS block below set to its own files, and the same calls.
Every gate's logic lives once in tools/stagekit.py (RingSession, pb_check, sink_gate_spec / sink_gate_read, ...); a recipe never re-types it.
The worked example's inputs are P5-1a's (plan_ring_p5s01a.json, card 154-a3-2b), so `stage_prerun --dry / --prerun` of this file can be
compared line for line with tools/recipes/stage_d1_ring_p5s01a.py (the copy-made recipe it replaces as the pattern; that one ran and is kept).
Behaviour == stage_d1_ring_p5s01a.py:124-191 except PB, which compares by POSITION (stagekit.pb_check, gate-fp fp-70, PD371(b)/PD373).
The TEMPLATE itself refuses a real launch (it would rebuild an adopted step); a dry / prerun run is allowed.
Sink gates: one per census row of SG_CENSUS_FILE with needs_sink_gate (stagekit.RingSession.SINK_GATES), read by script.
FRESH LabVIEW -> claudeDev\<NAME>_<ts>.vi (rule-6 GUI save, ExecState 0 by design) = an in-between file; the FIRST run of a batch is its
full SCRATCH run on a byte copy (stage_template_ring_scratch.py shape). ROWS ONLY FROM PLAN; expected values only from PRED. No new op.
PREDICTION (numbers in PRED): SG one declared sink gate per census row; L1 actions -> pred ops; E1 every checkpoint == sim; NG crossing tunnel
names == step files'; PRIM created primitives' labels == plan prims; FR created objects on the sim end's frames; D new/lost wires == sim's;
TD every base terminal that was wired stays wired, identities lost == plan deletes; CEN2 == pred census; PB cdiff(S1, end) slots == pred rows
by POSITION (FATAL, before save); HB handles <= +700; PS saved, input unchanged. X10 = pred memory_pred.
    py tools/stage_prerun.py --dry tools/recipes/stage_template_ring.py        (a batch: py tools/bgrun.py --material ... -- py -u <its recipe>)"""
import os, sys                                                                      # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402

# ---- INPUTS: the only lines a new batch changes -------------------------------------------------------------------------------------
PLAN = os.path.join(K.BENCH, "plan_ring_p5s01a.json")                               # ONE literal each: stage_prerun.plan_files reads them
PRED = os.path.join(K.BENCH, "plan_ring_p5s01a_pred.json")
LICENCE = os.path.join(K.BENCH, "plan_ring_p5s01a_licence.json")
SG_CENSUS_FILE = os.path.join(K.BENCH, "prep_c154_a3_2b_session.json")
NAME, KEY, CARD = "D1_ring_p5s01a", "ring_p5s01a", "card chat-T7 TEMPLATE (inputs of 154-a3-2b RING P5-1a)"
OUT_JSON = os.path.join(K.BENCH, "launch_template_ring.json")
ES_TEXT = "after all rows (ExecState 0 expected: P5-1a's in-between file is broken by design)"
LEVEL = "STRUCTURAL, in-between file of P5 (P5-1a), broken by design, never run"

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
    if not DRY and os.path.basename(__file__).startswith("stage_template_"):
        sys.exit("stage_template_ring is a TEMPLATE: write tools/recipes/stage_d1_ring_<batch>.py with its own INPUTS block and launch that")
    st = K.Stage(BASE["vi"], BASE["md5"], NAME, preload=False, deadline_min=45, out_json=OUT_JSON, task=CARD)
    rc = K.run(body, st)
    DRY or SX.kill_labview_at_exit()
    sys.exit(rc)
