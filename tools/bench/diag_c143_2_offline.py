r"""diag_c143_2_offline - card 143-2 steps 2-3, OFFLINE (no LabVIEW, no COM): identify the 2 extra Error List items of P4 session 2's
scratch file D1_ring_p4s02_20261003_110001.vi from its real graph (graph_ring_p4s02_20261003_112505.json, card 143-2 step 1) and compare
with the s01 real graph, the s02v18 SIMULATED end (sim/ring_p4_s03v18_s02end/base_provisional.json) and s03v18's first actions.
PRIOR ART: none for this exact compare; reads graph JSON in the shape written by diag_c141_3_graph.py / diag_c143_1_graph.py.
PREDICTION (hypothesis H, judgement): (a) exactly one While with an unwired conditional terminal = #10170 (loop 1.2, body #23166);
(b) exactly one Local with all terminals unwired = #6902 (StopAll read, symbol -20); both also open in the sim end; s03's first action
p4_w_stop12 wires -20 -> #10170 cond. H' (alternative): (d) lists a terminal unwired in s02 that was wired in s01 and is NOT a planned cut.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c143_2_offline.log -- py -u tools/bench/diag_c143_2_offline.py"""
import json, os, sys                                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                                              # noqa: E402
S02 = os.path.join(HERE, "graph_ring_p4s02_20261003_112505.json")
S01 = os.path.join(HERE, "graph_ring_p4s01_20261002_234419.json")
SIM = os.path.join(HERE, "sim", "ring_p4_s03v18_s02end", "base_provisional.json")
P03 = os.path.join(HERE, "plan_ring_p4_s03v18.json")
P02 = os.path.join(HERE, "plan_ring_p4_s02v18.json")
BOUND = {-2: 6869, -8: 6859, -14: 6850, -16: 29516, -18: 6899, -20: 6902}       # diag_c143_1_scratch.log:125,211,313,321,346,382
L = lambda f: json.load(open(f, encoding="utf-8"))                                         # noqa: E731
g2, g1, gs, p3, p2 = L(S02), L(S01), L(SIM), L(P03), L(P02)
OUT, ok = {}, []
OWN = g2["owners"]


def wired(r):
    w = r.get("wire_uid")
    return w not in (None, 0, "", "0")


def by_owner(g):
    d = {}
    for r in g["terminals"]:
        d.setdefault(r.get("owner_uid"), []).append(r)
    return d


def objcls(g):
    return dict((o.get("uid"), o.get("class")) for o in g.get("objs", []))


def analyse(g, tag):
    bo, oc = by_owner(g), objcls(g)
    wl = [u for u, c in oc.items() if c == "WhileLoop"]
    for u in sorted(set(r.get("owner_uid") for r in g["terminals"] if r.get("owner_class") == "WhileLoop")):
        u in wl or wl.append(u)                                                              # noqa: E701
    a = []
    for u in sorted(wl, key=lambda x: int(x)):
        # run 1 (diag_c143_2_offline.log): a WhileLoop owns NO terminal row; its conditional terminal is the '' SINK row owned by
        # its body Diagram (s01: #23246 on body #23166 wired by w23310). Body diagrams from the s02 real graph's owners map.
        bodies = [int(d) for d, v in OWN.items() if v[0] == "WhileLoop" and int(v[1]) == int(u)]
        rows = [r for d in bodies for r in bo.get(d, [])]
        names = sorted(set(r.get("term_name") for r in rows))
        seen, cond = set(), []
        for r in rows:
            if r.get("owner_class") == "Diagram" and r.get("term_name") == "" and not r.get("is_source") and r["term_uid"] not in seen:
                seen.add(r["term_uid"]); cond.append(dict(r, body=r.get("owner_uid")))           # noqa: E702
        a.append({"while": u, "rows": len(rows), "names": names[:12], "cond_rows": cond,
                  "cond_unwired": [r for r in cond if not wired(r)]})
    loc = []
    lu = sorted(set([u for u, c in oc.items() if c == "Local"] + [r.get("owner_uid") for r in g["terminals"] if r.get("owner_class") == "Local"]),
                key=lambda x: int(x))
    for u in lu:
        rows = bo.get(u, [])
        un = [r for r in rows if not wired(r)]
        if un or not rows:
            loc.append({"local": u, "rows": rows, "unwired": un})
    c = [r for r in bo.get(23166, []) if r.get("term_name") == ""]
    print("== {0}: {1} While loops, {2} Locals ({3} with an unwired terminal or no row)".format(tag, len(wl), len(lu), len(loc)))
    return {"while": a, "locals_open": loc, "t23166_blank": c, "while_open": [x for x in a if x["cond_unwired"] or not x["cond_rows"]],
            "t23435": [r for r in g["terminals"] if r.get("term_uid") == 23435]}


R2, R1, RS = analyse(g2, "s02 real"), analyse(g1, "s01 real"), analyse(gs, "s02v18 sim end")
for tag, R in (("s02", R2), ("s01", R1), ("sim", RS)):
    print("-- {0} (a) While loops with cond unwired / no cond row:".format(tag))
    for x in R["while_open"]:
        print("   While #{0}: rows {1} names {2} cond_rows {3}".format(x["while"], x["rows"], x["names"], x["cond_rows"]))
    print("-- {0} (b) Locals with unwired terminals:".format(tag))
    for x in R["locals_open"]:
        print("   Local #{0}: {1}".format(x["local"], x["rows"]))
    print("-- {0} (c) #23166 '' rows: {1}".format(tag, R["t23166_blank"]))
    print("-- {0} LoopTunnel #23417 inner #23435 rows: {1}".format(tag, R["t23435"][:1]))
OUT["s02"], OUT["s01"], OUT["sim"] = R2, R1, RS
k = lambda r: (r.get("term_uid"), r.get("owner_uid"), r.get("term_name"))                 # noqa: E731
w1 = dict((k(r), r) for r in g1["terminals"] if wired(r))
s2 = dict((k(r), r) for r in g2["terminals"])
newly = [dict(s2[x], s01_wire=w1[x].get("wire_uid")) for x in w1 if x in s2 and not wired(s2[x])]
print("-- (d) unwired in s02, wired in s01 (key term_uid, owner_uid, name): {0}".format(len(newly)))
for r in newly:
    print("   ", r)
OUT["newly_unwired"] = newly
cuts = p2.get("cuts") or p2.get("cut_set") or None
print("-- s02v18 plan keys: {0}".format(list(p2.keys())))
A3 = p3["actions"]
print("-- s03v18 first 3 actions:")
for i, a in enumerate(A3[:3], 1):
    print("   ", i, json.dumps(a)[:500])
OUT["s03_first"] = A3[0]
s02_open = [x["while"] for x in R2["while_open"]]
s02_loc = [x["local"] for x in R2["locals_open"]]
sim_open = [BOUND.get(x["while"], x["while"]) for x in RS["while_open"]]
sim_loc = [BOUND.get(x["local"], x["local"]) for x in RS["locals_open"]]
f = A3[0]
fdst, fsrc = f.get("dst", {}).get("uid"), BOUND.get(f.get("src", {}).get("uid"), f.get("src", {}).get("uid"))
print("FACT s02 open While {0}; open Locals {1}; sim open While {2} (symbols mapped); sim open Locals {3}".format(s02_open, s02_loc, sim_open, sim_loc))
print("FACT s03 first action {0}: src {1} (real #{2}) -> dst #{3}.{4}".format(f.get("id"), f.get("src"), fsrc, fdst, f.get("dst", {}).get("term")))
OUT["summary"] = {"s02_open_while": s02_open, "s02_open_locals": s02_loc, "sim_open_while": sim_open, "sim_open_locals": sim_loc,
                  "s03_first": {"id": f.get("id"), "src_real": fsrc, "dst": fdst}, "newly_unwired_n": len(newly)}
json.dump(OUT, open(os.path.join(HERE, "diag_c143_2_offline.json"), "w", encoding="utf-8"), indent=1, default=str)
print("WROTE tools/bench/diag_c143_2_offline.json")
gates = [("H-a s02 open While == [10170]", s02_open == [10170]), ("H-b s02 open Locals == [6902]", s02_loc == [6902]),
         ("H-sim s02 open sets also open in the sim end", set(s02_open) <= set(sim_open) and set(s02_loc) <= set(sim_loc)),
         ("H-s03 first action wires #6902 -> #10170", fsrc == 6902 and fdst == 10170)]
for lab, v in gates:
    print("  {0}  {1}".format("PASS" if v else "FAIL", lab))
npass = sum(1 for _, v in gates if v)
import hashlib                                                                               # noqa: E402
_m = hashlib.md5(open(os.path.join(HERE, "diag_c143_2_offline.json"), "rb").read()).hexdigest()
print(protocol.result_line(protocol.make_result(npass, len(gates) - npass, next((lab for lab, v in gates if not v), None),
                                                [{"path": "tools/bench/diag_c143_2_offline.json", "md5": _m}])))
