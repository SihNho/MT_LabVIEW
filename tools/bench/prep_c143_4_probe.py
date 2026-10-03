"""card 143-4 probe (offline, read-only): graph/plan structure for the rebase uid-reuse fix. No LabVIEW."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
B = os.path.join(ROOT, "tools", "bench")
g = json.load(open(os.path.join(B, "graph_ring_p4s02_20261003_112505.json"), encoding="utf-8"))
print("graph keys", list(g.keys()))
print("objs[:3]", (g.get("objs") or [])[:3])
print("term[0]", g["terminals"][0])
p = json.load(open(os.path.join(B, "plan_ring_p4_s03v18.json"), encoding="utf-8"))
print("plan keys", {k: type(v).__name__ for k, v in p.items()})
print("base", p.get("base"))
print("n actions", len(p["actions"]), "a0", p["actions"][0])
ops = {}
for a in p["actions"]:
    for k in a:
        ops.setdefault(k, 0)
        ops[k] += 1
print("action keys", ops)
txt = json.dumps(p)
for u in (23276, 29071, 29299):
    print("plan text contains", u, str(u) in txt)
s02 = json.load(open(os.path.join(B, "plan_ring_p4_s02v18.json"), encoding="utf-8"))
print("s02 base", s02.get("base"), "finalized.base", (s02.get("finalized") or {}).get("base"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagexec as SX                                                              # noqa: E402
ra = json.load(open(os.path.join(B, "plan_ring_p4_rasrest.json"), encoding="utf-8"))
nm = set()
SX._ints_in(ra.get("actions"), nm)
SX._ints_in(ra.get("open_rows"), nm)
print("rasrest names 28004/28979:", 28004 in nm, 28979 in nm, "6942/6805:", 6942 in nm, 6805 in nm)
n3 = set()
SX._ints_in(p.get("actions"), n3)
SX._ints_in(p.get("open_rows"), n3)
print("s03 named ints n", len(n3), "contains 23276/29071/29299:", [u for u in (23276, 29071, 29299) if u in n3])
print("s03 finalized keys", list((p.get("finalized") or {}).keys()))
pv = json.load(open(os.path.join(ROOT, p["base"]["path"]), encoding="utf-8"))
print("FACT prov rows owner -20:", [(r["term_uid"], r.get("term_name"), r.get("owner_class"), r.get("is_source"), r.get("wire_uid"))
                                    for r in pv["terminals"] if r.get("owner_uid") == -20])
print("FACT prov objs -20:", [o for o in pv.get("objs") or [] if isinstance(o, dict) and o.get("uid") == -20])
print("FACT s03 actions naming -20:", [a["id"] for a in p["actions"] if "-20" in json.dumps({k: v for k, v in a.items() if k != "why"})])


