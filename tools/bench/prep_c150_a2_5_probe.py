# ---
# labview: none
# hardware: none
# ---
"""prep_c150_a2_5_probe - card 150-a2-5 read-only probe (OFFLINE): s06 Error List files (md5, item count, total), the 150-a1-1 session table keys,
the rebased s07 plan's base / finalized summary and the s06 licence form. Writes nothing.
PREDICTION CONTRACT: prints only; RESULT PASS when every file loads."""
import hashlib, json, os, sys                                                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
J = lambda p: json.load(open(p, encoding="utf-8"))                                          # noqa: E731
short = lambda v, n=300: v if len(str(v)) < n else str(v)[:n] + "..."                      # noqa: E731
ex = os.path.join(B, "errorlist_expected_D1_ring_p4s06_20261008_174730.json")
e = J(ex)
print("EXP", md5(ex), dict((k, short(v)) for k, v in e.items()))
for n in ("errorlist_D1_ring_p4s06_20261008_174730_20261008_175750.json", "errorlist_D1_ring_p4s06_20261008_174730_20261008_181243.json"):
    d = J(os.path.join(B, n))
    print("READ", n, md5(os.path.join(B, n)), len(d.get("items") or []), d.get("total"), sorted(d.keys()))
s = J(os.path.join(B, "prep_c150_a1_1_session.json"))
print("SESS", dict((k, short(v, 200)) for k, v in s.items()))
p = J(os.path.join(B, "plan_ring_p4_s07v18.json"))
print("PLAN keys", sorted(p.keys()), "actions", len(p["actions"]), "final", p.get("final"))
print("PLAN base", short(p.get("base"), 600))
fz = p.get("finalized") or {}
print("FZ keys", sorted(fz.keys()))
print("FZ base", short(fz.get("base"), 400), "rebase", short(fz.get("rebase"), 600))
lic = J(os.path.join(B, "plan_ring_p4_s06v18_licence.json"))
print("LIC6", json.dumps(lic)[:2400])
print(protocol.result_line(protocol.make_result(1, 0, None, [])), flush=True)
