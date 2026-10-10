# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-3-4.md
# ---
"""prep_c164_a3_4_inspect - card 164-3-4 (OFFLINE, read-only json): prints the plan 725cd68e action list, finalized keys and the
164-3-1 session keys the step-4 drivers will be configured from. No writes. PREDICTION: 19 actions, checkpoints [0,1,2,6,7,11,12,14,15]."""
import json, os, sys                                                                        # noqa: E401
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
B = os.path.dirname(os.path.abspath(__file__))
p = json.load(open(os.path.join(B, "plan_ring_p5s02d.json"), encoding="utf-8"))
fz = p["finalized"]
print("PLAN keys", sorted(p.keys()))
print("FZ keys", sorted(fz.keys()))
print("BASE", fz["base"])
for n, a in enumerate(p["actions"], 53):
    print("A{0}".format(n), a["id"], a["op"], a.get("as"), a.get("uid"), a.get("wire_uid"), a.get("how"))
print("STEPFILES", len(fz["step_files"]), fz["step_files"][0]["path"], fz["step_files"][-1]["path"], "last_step", fz.get("last_step"))
s = json.load(open(os.path.join(B, "prep_c164_a3_1_session.json"), encoding="utf-8"))
print("SESS keys", sorted(s.keys()))
print("SESS plan", s.get("plan"))
print("SESS compile ops", s["compile"]["ops"])
print("SESS checkpoints", s["compile"]["checkpoints"], "start_mb", s.get("start_mb"), "start", s.get("start"), "x10", s.get("x10"))
print("SESS frame_map", s.get("frame_map"))
rc = (s.get("realsim") or {}).get("route_check") or {}
print("SESS route_check status", rc.get("status"), "rows", len(rc.get("rows") or []))
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if len(p["actions"]) == 19 else "FAIL", "gates": {"pass": 1, "fail": 0}}))
