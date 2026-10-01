r"""diag_c132_5_rows - card 132-5: RECORD the full terminal rows of the two created objects whose names differ (FSIT, Unbundler),
sim vs real, with the other ends of their wires, and the negative uids the P3b-2 plan references. Offline, read only.
PREDICTION: R1 one created FSIT and one created Unbundler on each side; R2 every negative uid the plan references is printed.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c132_5_rows.log -- py -u tools/bench/diag_c132_5_rows.py"""
import json, os, sys, re                                                            # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.dirname(B))
import protocol as P, vigraph as V                                                 # noqa: E401,E402
J = lambda p: json.load(open(os.path.join(R, p), encoding="utf-8"))               # noqa: E731
plan = J("tools/bench/plan_ring_p3b2.json")
provd = J(plan["base"]["path"])
prov = provd.get("terminals")
before = J("tools/bench/graph_ring_p3a_20261001_190155.json")["terminals"]
real = J("tools/bench/graph_ring_p3b1_20261002_073225.json")["terminals"]
print("  FACT  row keys {0}".format(sorted(prov[0].keys())), flush=True)
old_t = set(r["term_uid"] for r in before)
created = {"SIM": [r for r in prov if V.node_of(r) < 0], "REAL": [r for r in real if r["term_uid"] not in old_t]}
allrows = {"SIM": prov, "REAL": real}
n = {}
for nm in ("SIM", "REAL"):
    byw = {}
    for r in allrows[nm]:
        if r.get("wire_uid"):
            byw.setdefault(r["wire_uid"], []).append(r)
    for r in created[nm]:
        c = V.node_class(r)
        if c not in ("FlatSequenceInnerTunnel", "Unbundler"):
            continue
        n[(nm, c)] = n.get((nm, c), set()) | {V.node_of(r)}
        others = [(o["owner_class"], o["owner_uid"], o.get("term_name"), o["term_uid"], o["is_source"])
                  for o in byw.get(r.get("wire_uid"), []) if o["term_uid"] != r["term_uid"]] if r.get("wire_uid") else []
        rr = dict((k, v) for k, v in r.items() if k not in ("owner_class",))
        print("  FACT  {0} {1}: {2}  OTHER ENDS {3}".format(nm, c, rr, others), flush=True)
neg = set()
s = json.dumps(plan.get("actions"))
for m in re.finditer(r'(?<![\w.])(-\d+)', s):
    neg.add(int(m.group(1)))
simneg = set(V.node_of(r) for r in created["SIM"]) | set(r["term_uid"] for r in created["SIM"]) | \
    set(r["wire_uid"] for r in created["SIM"] if isinstance(r.get("wire_uid"), int) and r["wire_uid"] < 0)
print("  FACT  plan negative ints referenced (intersect created sim uids): {0}".format(sorted(neg & simneg)), flush=True)
cls = dict((V.node_of(r), V.node_class(r)) for r in created["SIM"])
cls.update(dict((r["term_uid"], "term of {0} #{1} {2!r} src={3}".format(V.node_class(r), V.node_of(r), r.get("term_name"),
                 r["is_source"])) for r in created["SIM"]))
for u in sorted(neg & simneg):
    print("  FACT  plan ref {0}: {1}".format(u, cls.get(u, "wire")), flush=True)
ok1 = all(len(n.get((a, b), ())) == 1 for a in ("SIM", "REAL") for b in ("FlatSequenceInnerTunnel", "Unbundler"))
print("{0}  R1 one created FSIT + one Unbundler each side  {1}".format("PASS" if ok1 else "FAIL",
      dict(("{0}/{1}".format(*k), sorted(v)) for k, v in n.items())), flush=True)
print(P.result_line(P.make_result(int(ok1), int(not ok1), None if ok1 else "R1")), flush=True)
sys.stdout.flush()
os._exit(0 if ok1 else 1)
