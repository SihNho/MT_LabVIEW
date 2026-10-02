r"""selftest_x10_c141_1 - card 141-1 item 4 (offline): X10 REFUSES a plan whose base is PROVISIONAL (stagesim's simulated end,
no measured input load) instead of falling back to the model start_mb (x10_plan_start returns None for it, stage_prerun.py
x10_plan_start). Uses the measured session-1 plan tools/bench/plan_ring_p4_s01.json (140-3, ff041e6c, bed base) and a %TEMP% copy
of it whose top-level base carries provisional {path, md5}.
PREDICTION: P1 x10_base_provisional(copy) True, (real) False; P2 x10_gate on the copy: ok False, why names PROVISIONAL, no run
modelled; P3 x10_gate on the real plan: not refused for provisional, one run modelled at the measured start (606.1);
P4 x10_plan_start(copy) None (unchanged).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_x10_c141_1.log -- py -u tools/bench/selftest_x10_c141_1.py"""
import json, os, sys, tempfile                                                           # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR                                                 # noqa: E401,E402
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:600]), flush=True)


REAL = os.path.join(ROOT, "tools", "bench", "plan_ring_p4_s01.json")
RECIPE = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p4_s01.py")
p = json.load(open(REAL, encoding="utf-8"))
q = json.loads(json.dumps(p))
q["base"] = dict(q["base"], provisional={"path": q["base"]["path"], "md5": q["base"]["md5"]})
COPY = os.path.join(tempfile.gettempdir(), "selftest_x10_c141_1_prov.json")
json.dump(q, open(COPY, "w", encoding="utf-8"), indent=1)
kinds = [o["kind"] for o in SX.compile_plan(p)]
cps = sorted({0, len(kinds)} | set(k for k, x in enumerate(kinds, 1) if x in SX.BIND_KINDS))
gate("P1 x10_base_provisional: copy True, real False", SPR.x10_base_provisional(COPY) and not SPR.x10_base_provisional(REAL))
ok2, d2 = SPR.x10_gate(RECIPE, [{"plan": COPY, "kinds": kinds, "checkpoints": cps}])
gate("P2 x10_gate refuses the provisional base (no fallback start)", not ok2 and "PROVISIONAL" in str(d2.get("why")) and not d2.get("runs"),
     {"why": d2.get("why"), "runs": len(d2.get("runs") or [])})
ok3, d3 = SPR.x10_gate(RECIPE, [{"plan": REAL, "kinds": kinds, "checkpoints": cps}])
r3 = (d3.get("runs") or [{}])[0]
gate("P3 the real plan is modelled at its measured start (606.1), not refused for provisional",
     "PROVISIONAL" not in str(d3.get("why")) and len(d3.get("runs") or []) == 1 and abs(float(r3.get("start_mb") or 0) - 606.1) < 0.05,
     {"ok": ok3, "start": r3.get("start_mb"), "exec_peak": r3.get("exec_peak_mb"), "peak": r3.get("peak_mb"), "why": d3.get("why")})
gate("P4 x10_plan_start(copy) is None (unchanged)", SPR.x10_plan_start(COPY) is None)
os.remove(COPY)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
