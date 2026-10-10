# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_161-a3-2.md
# ---
r"""prep_c161_a3_2_x10 - card 161-a3-2 (OFFLINE, json only, PD394(b)): the X10 numbers of P5-2 step 2 RESTATED on the shared checkpoint rule
(stagexec.checkpoint_ops via prep_c156_a1_1_lib.main_of, 161-a3-1) -> NEW record prep_c161_a3_2_x10.json. The b3-1 session table
(prep_c160_b3_1_session.json `x10`, made on the old BIND|{0,n} rule) is READ for the old numbers and START_ASSUMED, never edited.
Also restates lib --selftest T3 (155 step 1, plan_ring_p5s02.json at prep_c155_a4_1_session.json start_mb), same cause.
No arithmetic here: every number comes from L.main_of. The record pins the md5 of every file that decides the numbers; the pred maker
(prep_c160_c3_1_pred.py X10) refuses a record whose pins differ.
PREDICTION: P5-2 step 2 at START_ASSUMED 603.4: exec_peak 659.9, MAIN 665.0 <= 675 (prep_c161_a3_1_pred.log:10); T3 682.5 (prep_c161_a3_1_lib.log:5).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c161_a3_2_x10.log -- py -u tools/bench/prep_c161_a3_2_x10.py"""
import json, os, sys                                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import stagexec as SX, stage_prerun as SPR                                                  # noqa: E401,E402
import prep_c156_a1_1_lib as L                                                              # noqa: E402
B, T = os.path.join(ROOT, "tools", "bench"), os.path.join(ROOT, "tools")
RRP, SESS, OUT = os.path.join(B, "plan_ring_p5s02b.json"), os.path.join(B, "prep_c160_b3_1_session.json"), os.path.join(B, "prep_c161_a3_2_x10.json")
P155, S155, LIMIT = os.path.join(B, "plan_ring_p5s02.json"), os.path.join(B, "prep_c155_a4_1_session.json"), 675.0
PINNED = [RRP, SESS, P155, S155, SPR.MEMORY_MODEL, os.path.join(T, "stagexec.py"), os.path.join(T, "stage_prerun.py"), os.path.join(T, "stagekit.py"),
          os.path.join(B, "prep_c156_a1_1_lib.py")]
gate = L.Gate()
MODEL, S = SPR.load_memory_model(), L.J(SESS)
ops = SX.compile_plan(L.J(RRP))
MAIN, mp, cps = L.main_of(len(ops), [o["kind"] for o in ops], SX, SPR, MODEL, S["start_mb"])
ops5 = SX.compile_plan(L.J(P155))
S5 = L.J(S155)
M5, _mp5, cps5 = L.main_of(len(ops5), [o["kind"] for o in ops5], SX, SPR, MODEL, S5["start_mb"])
print("FACT X10 p5s02b at START_ASSUMED {0}: checkpoints {1} exec_peak {2} MAIN {3} (old BIND rule: exec_peak {4} MAIN {5}); T3 155 step 1: {6} ops MAIN {7} "
      "(old {8})".format(S["start_mb"], list(cps), mp["peak_mb"], MAIN, S["x10"]["exec_peak"], S["x10"]["main"], len(ops5), M5, S5["main_peak_mb"]), flush=True)
rec = {"schema": "x10-record/1", "card": "161-a3-2", "cause": "PD394(b) checkpoint rule: MAIN on the shared stagexec.checkpoint_ops set (161-a3-1) instead of the "
       "hand-coded BIND|{0,n}; the b3-1 session x10 was made on the old rule", "rule_fn": "prep_c156_a1_1_lib.main_of -> stagexec.checkpoint_ops + stage_prerun.x10_model_peak",
       "plan": L.rel(RRP), "start_assumed_mb": S["start_mb"], "ops": len(ops), "checkpoints": list(cps), "R": mp["R"], "exec_peak": mp["peak_mb"], "main": MAIN,
       "limit_mb": LIMIT, "old": {"from": L.rel(SESS) + " x10", "exec_peak": S["x10"]["exec_peak"], "main": S["x10"]["main"]},
       "lib_t3": {"plan": L.rel(P155), "session": L.rel(S155), "start_mb": S5["start_mb"], "ops": len(ops5), "checkpoints": list(cps5), "main": M5,
                  "old_main": S5["main_peak_mb"]},
       "pins": dict((L.rel(p), L.md5(p)) for p in PINNED)}
gate("X10R MAIN {0} at START_ASSUMED {1} <= {2} (> limit = hand back); checkpoints == stagexec.checkpoint_ops {3}".format(MAIN, S["start_mb"], LIMIT, list(cps)),
     MAIN <= LIMIT and mp["ok"] and tuple(cps) == SX.checkpoint_ops(ops), mp)
json.dump(rec, open(OUT, "w", encoding="utf-8"), indent=1)
gate.ARTS.append({"path": L.rel(OUT), "md5": L.md5(OUT)})
gate("W record written; old session file untouched (md5 {0})".format(rec["pins"][L.rel(SESS)][:8]), L.J(OUT)["main"] == MAIN and L.md5(SESS).startswith("e5279899"))
sys.exit(gate.result())
