# ---
# labview: build
# hardware: none
# ---
r"""stage_d1_ring_p5s02e - card 165-3-3 (WRITTEN, NOT LAUNCHED), RING P5-2 step 5 (docs/d1/ring-p5c.md PD400, PD401, PD402): on the saved p5s02d
file (claudeDev\D1_ring_p5s02d_20261010_152518.vi 6dcd5c3d, path/md5 read from the plan's base graph 2a5fa0c4), apply the 13 actions of
plan_ring_p5s02e.json fd23974e = K3f (A72-73: delete_wire of the sink-only stub w10362 on LoopTunnel #5204's inner face t8776, then w_k3f
OK3.outer -> t8776), K4 (A74-82: SR SK4 on loop #23041, init const KI4, case tunnels OK4 / IK4 through register_end_case_border, pass wire w_k4pass
on frame #31517), K4f (A83-84: delete_wire of the stub w25232 on LoopTunnel #10404's inner face t24342, then w_k4f OK4.outer -> t24342);
tools/bench/prep_c165_a3_2_mk.py. PRIME-SKIP of #8776 / #24342 (stagexec 1d5309f4, card 165-3-1). Licence plan_ring_p5s02e_licence.json;
sink-gate census prep_c165_a3_3_sg.json (0 rows).
Shape = the pair shape of stage_d1_ring_p5s02d.py on stagekit.RingSession (docs/script-writing.md rules 1-2): only plan / pred / licence /
census file / names / output name differ; every gate is CALLED.
FRESH LabVIEW -> claudeDev\D1_ring_p5s02e_<ts>.vi (rule-6 GUI save, ExecState 0 by design; file name per brief_165-3-3.md:19-20 - PD400(c)
names the full-prefix result the P5 FINAL D1_ring_p5_<ts>.vi, broken file 6 of 6: the adopting card decides the name). The FIRST run is the full SCRATCH run on a byte copy (stage_d1_ring_p5s02e_scratch.py). ROWS ONLY FROM PLAN; expected values
only from PRED.
PREDICTION (numbers in PRED, prep_c165_a3_3_pred.py / _pd402.py): SG 0 sink gates; L1 13 actions -> 9 ops == pred kinds; E1 every checkpoint
[0,1,3,4,6,7,8,9] == sim; NG; PRIM; FR; D; TD; CEN2 (Wire by ENDS, PD389(b); census UNPREDICTED until the scratch measures it); PB by POSITION
(FATAL, before save); HB handles <= +700; PS saved, input unchanged. X10 start 609.8, MAIN 665.0 <= 675; Error List predicted 49 (upper 51).
    py tools/bgrun.py --material --max-min 50 --log tools/bench/launch_c165_p5s02e.log -- py -u tools/recipes/stage_d1_ring_p5s02e.py"""
import os, sys                                                                      # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402

# ---- INPUTS -------------------------------------------------------------------------------------------------------------------------
PLAN = os.path.join(K.BENCH, "plan_ring_p5s02e.json")                               # ONE literal each: stage_prerun.plan_files reads them
PRED = os.path.join(K.BENCH, "plan_ring_p5s02e_pred.json")
LICENCE = os.path.join(K.BENCH, "plan_ring_p5s02e_licence.json")
SG_CENSUS_FILE = os.path.join(K.BENCH, "prep_c165_a3_3_sg.json")
NAME, KEY, CARD = "D1_ring_p5s02e", "ring_p5s02e", "card 165-3-3 RING P5-2 step 5"
OUT_JSON = os.path.join(K.BENCH, "launch_c165_p5s02e.json")
ES_TEXT = "after all rows (ExecState 0 expected: P5-2 step 5's file is broken by design)"
LEVEL = "STRUCTURAL, P5-2 step 5 file (full prefix K3f + K4 + K4f), broken by design, never run"

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
