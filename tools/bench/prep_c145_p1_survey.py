# ---
# labview: none
# hardware: none
# ---
import json, os, hashlib
os.chdir(r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop")
J = lambda p: json.load(open(p, encoding="utf-8"))
p = J("tools/bench/plan_ring_p4_s04v18.json")
print("base", p.get("base"))
fz = p.get("finalized") or {}
print("fz.base", fz.get("base"))
sf = fz.get("step_files") or []
print("steps", len(sf), sf[-1] if sf else None)
print("acts", len(p["actions"]), p["actions"][0]["id"], p["actions"][-1]["id"], "final", p.get("final"))
q = J("tools/bench/plan_ring_p4_s04v18_pred.json")
print("pred", q["memory_pred"]["start_mb"], q["memory_pred"]["start_cite"], q["memory_pred"]["peak_mb"], q["errorlist"]["predicted_total"], q["plan"], q.get("card"))
print("el rule", q["errorlist"]["rule"][:600])
s = J("tools/bench/prep_c144_p1_session.json")
print({k: s.get(k) for k in ("ops", "first", "last", "actions", "start_mb", "peak_mb", "next_op", "next_peak_mb")})
if sf and os.path.isfile(sf[-1]["path"]):
    print("end md5", hashlib.md5(open(sf[-1]["path"], "rb").read()).hexdigest())
    st = J(sf[-1]["path"])["state"]
    print("end sym", st.get("sym"), "neg", st.get("neg"))
