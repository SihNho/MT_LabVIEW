r"""diag_c132_4_diff - card 132-4 step 3 (brief_132-2.md part B): REAL graph of the saved P3b-1 bed vs the simulator's END graph of
P3b-1 (tools/bench/sim/ring_p3b1/, last step). OFFLINE, no LabVIEW. Facts only, no verdict on whether a difference matters.
PRIOR ART: errorlist_expect_p3b2.prof (wire -> [sources, sinks] from terminal rows), reused as is.
PREDICTION (contract): C1 both files load and carry terminals + objs; C2 the count table prints (objs, objs by class group, terminal
rows, distinct wire uids, one-sided wires); C3 #6810's terminals exist in both graphs and every wire on them is listed with
its terminals on both sides; C4 the one-sided ('loose-end') wire sets are compared by terminal SIGNATURE (owner uid, or
'new:<class>' for a created object, + terminal name + direction), so a swap inside the class is visible.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c132_4_diff.log -- py -u tools/bench/diag_c132_4_diff.py"""
import collections, glob, json, os, sys                                            # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(B))
import protocol as P                                                                # noqa: E402
REAL = sorted(glob.glob(os.path.join(B, "graph_ring_p3b1_*.json")))[-1]
SIM = sorted(glob.glob(os.path.join(B, "sim", "ring_p3b1", "step_*.json")))[-1]
NODE = 6810
J = lambda p: json.load(open(p, encoding="utf-8"))                                  # noqa: E731
res = []


def gate(name, ok, det=""):
    res.append((name, bool(ok)))
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(det)[:1500]), flush=True)


def prof(terms):
    w = collections.defaultdict(lambda: [0, 0])
    for t in terms:
        if t.get("wire_uid") not in (None, 0, -1):
            w[int(t["wire_uid"])][0 if t.get("is_source") else 1] += 1
    return w


def sig(t):
    o = int(t.get("owner_uid") or 0)
    return ("{0}".format(o) if o > 0 else "new:" + str(t.get("owner_class"))) + "." + str(t.get("term_name")) + \
        (".src" if t.get("is_source") else ".snk")


def side(terms, w):
    return sorted("#{0} {1} {2} '{3}'".format(t.get("owner_uid"), t.get("owner_class"), "src" if t.get("is_source") else "snk",
                                              t.get("term_name")) for t in terms if t.get("wire_uid") == w)


r, s = J(REAL), J(SIM)["state"]
RT, ST = r.get("terminals") or [], s.get("terminals") or []
gate("C1 both graphs load with terminals + objs", RT and ST and r.get("objs") and s.get("objs"),
     (os.path.basename(REAL), os.path.relpath(SIM, B)))
rp, sp = prof(RT), prof(ST)
groups = lambda objs: collections.Counter("Wire" if o["class"] == "Wire" else "Diagram" if "Diagram" in o["class"]  # noqa: E731
                                          else "Terminal/Tunnel" if ("Tunnel" in o["class"] or o["class"].endswith("Register")
                                                                     or o["class"] == "Terminal") else "node" for o in objs)
gr, gs = groups(r["objs"]), groups(s["objs"])
one = lambda p: sorted(k for k, v in p.items() if not v[0] or not v[1])            # noqa: E731
table = [("objs", len(r["objs"]), len(s["objs"]))] + [("objs " + k, gr.get(k, 0), gs.get(k, 0)) for k in sorted(set(gr) | set(gs))] + [
    ("terminal rows", len(RT), len(ST)), ("distinct wire uids (terminals)", len(rp), len(sp)),
    ("one-sided wires", len(one(rp)), len(one(sp))), ("loops", len(r.get("loops") or []), len(s.get("loops") or []))]
for k, a, b in table:
    print("  FACT  COUNT {0:34s} real {1:6d}  sim {2:6d}  d {3:+d}".format(k, a, b, a - b), flush=True)
gate("C2 count table printed", True, len(table))
for nm, T, pp in (("REAL", RT, rp), ("SIM", ST, sp)):
    mine = [t for t in T if int(t.get("owner_uid") or 0) == NODE]
    print("  FACT  {0} #{1} terminals: {2}".format(nm, NODE, [(t.get("term_name"), "src" if t.get("is_source") else "snk",
                                                               t.get("wire_uid")) for t in mine]), flush=True)
    for w in sorted(set(t.get("wire_uid") for t in mine if t.get("wire_uid") not in (None, 0, -1))):
        print("  FACT  {0} #{1} net w{2} {3}/{4}{5}: {6}".format(nm, NODE, w, pp[w][0], pp[w][1],
                                                              " LOOSE" if not pp[w][0] or not pp[w][1] else "", side(T, w)), flush=True)
r_mine = [t for t in RT if int(t.get("owner_uid") or 0) == NODE]
gate("C3 #{0} terminals in both graphs".format(NODE), r_mine and [t for t in ST if int(t.get("owner_uid") or 0) == NODE], len(r_mine))
rs = dict((w, sorted(sig(t) for t in RT if t.get("wire_uid") == w)) for w in one(rp))
ss = dict((w, sorted(sig(t) for t in ST if t.get("wire_uid") == w)) for w in one(sp))
rk, sk = collections.Counter(tuple(v) for v in rs.values()), collections.Counter(tuple(v) for v in ss.values())
only_r, only_s = rk - sk, sk - rk
for nm, d, src in (("REAL-only", only_r, rs), ("SIM-only", only_s, ss)):
    for k in sorted(d):
        ws = [w for w, v in src.items() if tuple(v) == k]
        print("  FACT  LOOSE {0} wire(s) {1}: {2}".format(nm, ws, list(k)), flush=True)
print("  FACT  LOOSE same signature in both: {0}; real-only {1}; sim-only {2}".format(
    sum((rk & sk).values()), sum(only_r.values()), sum(only_s.values())), flush=True)
gate("C4 one-sided wire sets compared by terminal signature", True, (len(rs), len(ss)))
npass, nfail = sum(1 for _n, c in res if c), sum(1 for _n, c in res if not c)
print(P.result_line(P.make_result(npass, nfail, next((n for n, c in res if not c), None))), flush=True)
sys.stdout.flush()
os._exit(1 if nfail else 0)
