r"""diag_c132_5_unbound - card 132-5 (tool build, self-test iteration): for the created sim nodes the new rebind leaves
unbound, print each row, its wire's other ends, whether those ends are pre-existing, and the real terminals on the real
wire of a pre-existing end. Offline, read only.
PREDICTION: U1 rows printed for the 8 unbound nodes.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c132_5_unbound.log -- py -u tools/bench/diag_c132_5_unbound.py"""
import json, os, sys                                                                # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.dirname(B))
import protocol as P, vigraph as V                                                 # noqa: E401,E402
J = lambda p: json.load(open(os.path.join(R, p), encoding="utf-8"))               # noqa: E731
plan = J("tools/bench/plan_ring_p3b2.json")
pv = J(plan["base"]["path"])["terminals"]
bf = J("tools/bench/graph_ring_p3a_20261001_190155.json")["terminals"]
rl = J("tools/bench/graph_ring_p3b1_20261002_073225.json")["terminals"]
old = set(r["term_uid"] for r in bf)
rrow = dict((r["term_uid"], r) for r in rl)
sw, rw = {}, {}
for r in pv:
    r.get("wire_uid") and sw.setdefault(r["wire_uid"], []).append(r)              # noqa: E701
for r in rl:
    r.get("wire_uid") and rw.setdefault(r["wire_uid"], []).append(r)              # noqa: E701
U = (-5, -9, -18, -20, -25, -27, -32, -37, -42)
n = 0
for r in pv:
    if V.node_of(r) not in U:
        continue
    n += 1
    ends = [o for o in sw.get(r.get("wire_uid"), []) if o["term_uid"] != r["term_uid"]] if r.get("wire_uid") else []
    print("  ROW  #{0} {1} t{2} {3!r} src={4} w{5} f{6}".format(V.node_of(r), V.node_class(r), r["term_uid"], r["term_name"],
          r["is_source"], r.get("wire_uid"), r.get("frame_diagram")), flush=True)
    for o in ends:
        pre = o["term_uid"] > 0
        line = "       end t{0} {1} #{2} {3!r} pre={4} inreal={5}".format(o["term_uid"], o["owner_class"], o["owner_uid"],
                                                                      o["term_name"], pre, o["term_uid"] in rrow)
        if pre and o["term_uid"] in rrow:
            ro = rrow[o["term_uid"]]
            line += " realw={0} on it: {1}".format(ro.get("wire_uid"), [(x["term_uid"], x["owner_class"], x["owner_uid"],
                      x["term_name"], x["term_uid"] not in old, x.get("frame_diagram")) for x in rw.get(ro.get("wire_uid"), [])
                      if x["term_uid"] != o["term_uid"]][:6])
        print(line[:700], flush=True)
ok = n > 0
print("{0}  U1 rows printed  {1}".format("PASS" if ok else "FAIL", n), flush=True)
print(P.result_line(P.make_result(int(ok), int(not ok), None if ok else "U1")), flush=True)
sys.stdout.flush()
os._exit(0 if ok else 1)
