r"""prep_c142_5_probe - card 142-5: offline read of the plan/graph chain for the rebind key fix. No LabVIEW, writes nothing.
PREDICTION: rasrest's provisional base chain resolves; uids 28004/28979 are in the s01 BEFORE graph under owners other than
in the real s01 graph (PD325(a): #27928/#28916 before vs #6942/#6805 real); v18 names its base."""
import json, os, sys                                                               # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.dirname(B))
import protocol as P                                                               # noqa: E402
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(R, p), encoding="utf-8"))   # noqa: E731
ok = 0
for p in ("tools/bench/plan_ring_p4_rasrest.json", "tools/bench/plan_ring_p4_v18.json", "tools/bench/plan_ring_p4_s02.json"):
    if not os.path.isfile(os.path.join(R, p)):
        print("  FACT  missing", p)
        continue
    d = J(p)
    print("  FACT  {0}: stage={1} actions={2} keys={3}".format(p, d.get("stage"), len(d.get("actions") or []), sorted(d)))
    print("        base={0}".format(json.dumps(d.get("base"))[:500]))
    print("        finalized.base={0}".format(json.dumps((d.get("finalized") or {}).get("base"))[:300]))
d = J("tools/bench/plan_ring_p4_rasrest.json")
so = d["base"].get("sim_of") or {}
pn = J(so["plan"])
bn = (pn.get("finalized") or {}).get("base") or pn.get("base")
print("  FACT  N plan {0} base {1}".format(so.get("plan"), bn))
bf, pv, rl = J(bn["path"]), J(d["base"]["path"]), J("tools/bench/graph_ring_p4s01_20261002_234419.json")
for nm, g in (("before", bf), ("prov", pv), ("real", rl)):
    for r in g["terminals"]:
        if r["term_uid"] in (28004, 28979) or r.get("owner_uid") in (27928, 28916, 6942, 6805):
            print("  FACT  {0}: term {1} owner {2} {3} name {4!r} class {5} src {6} wire {7}".format(
                nm, r["term_uid"], r.get("owner_uid"), r.get("owner_class"), r.get("term_name"), r.get("term_class"),
                r.get("is_source"), r.get("wire_uid")))
    ok += 1
print(P.result_line(P.make_result(ok, 3 - ok, None)), flush=True)
