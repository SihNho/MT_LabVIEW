# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-a2-3.md
# ---
"""diag_c164_a2_3_inspect - card 164-a2-3 (OFFLINE, read-only): print the step-4 plan's actions, finalized keys, step files and the
session table, so the makers are written against the real keys."""
import json, os, sys                                                                        # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
J = lambda p: json.load(open(os.path.join(B, p), encoding="utf-8"))                          # noqa: E731
p = J("plan_ring_p5s02d.json")
print("PLAN keys", list(p))
print("PLAN base", json.dumps(p.get("base"))[:600])
fz = p["finalized"]
print("FZ keys", list(fz))
print("FZ base", json.dumps(fz.get("base")), "open_rows_match", fz.get("open_rows_match"), "final", p.get("final"))
for a in p["actions"]:
    print("ACT", json.dumps(a)[:700])
for x in fz.get("step_files") or []:
    print("SF", json.dumps(x))
print("SUMMARY", json.dumps(fz.get("summary"))[:1500])
print("CDIFF", json.dumps(fz.get("end_cdiff_rows"))[:800])
s = J("prep_c164_a2_2_session.json")
print("SESS keys", list(s))
for k in s:
    print("SESS", k, json.dumps(s[k])[:2500])
sys.exit(0)
