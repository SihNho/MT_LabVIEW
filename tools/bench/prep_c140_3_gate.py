r"""prep_c140_3_gate - card 140-3 item 1 (offline, no LabVIEW, no COM). PD321(b) GATE: on the bed's real graph
(graph_ring_p3b2b_20261002_133824.json, 50595c62), wire w23255's source terminal and EVERY sink; PASS only if every sink is a terminal
of #10171 (the 1.2 scaffold `x = y?`, deleted by v14 action 2). Also prints v14 actions 1..4 (the ones v15 replaces).
Prior art: graph row fields as read by prep_c140_2_s01.py:88,177 (owner_uid, term_uid, wire_uid, is_source, term_name).
PREDICTION CONTRACT: M0 graph md5 == 50595c62; W1 w23255 has exactly one source row and >= 1 sink row; GS every sink owner == 10171.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c140_3_gate.log -- py -u tools/bench/prep_c140_3_gate.py"""
import hashlib, json, os, sys                                                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
GRAPH, V14 = os.path.join(B, "graph_ring_p3b2b_20261002_133824.json"), os.path.join(B, "plan_ring_p4_v14.json")
G = {"pass": 0, "fail": 0, "first": None}
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                             # noqa: E731


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


gate("M0 graph md5 == 50595c62 / v14 == 22f58271", md5(GRAPH) == "50595c62d0332a94bf066538cf20c0ae" and md5(V14) == "22f582715e3d303ea0625fbe98bb590e")
g = json.load(open(GRAPH, encoding="utf-8"))
rows = [r for r in g["terminals"] if r.get("wire_uid") == 23255]
for r in rows:
    print("W23255 ROW", json.dumps(r, ensure_ascii=True)[:400])
own = [r for r in g["terminals"] if r.get("owner_uid") == 10171]
for r in own:
    print("N10171 TERM", json.dumps(r, ensure_ascii=True)[:400])
srcs = [r for r in rows if r.get("is_source")]
sinks = [r for r in rows if not r.get("is_source")]
gate("W1 w23255: one source row, >= 1 sink row", len(srcs) == 1 and len(sinks) >= 1, {"src": len(srcs), "sinks": len(sinks)})
gate("GS every sink of w23255 is a terminal of #10171", bool(sinks) and all(r.get("owner_uid") == 10171 for r in sinks),
     [(r.get("owner_uid"), r.get("term_uid"), r.get("term_name")) for r in sinks])
for w in sorted(set(r.get("wire_uid") for r in own if r.get("wire_uid"))):
    print("WIRE on #10171", w, [(r.get("owner_uid"), r.get("term_name"), r.get("is_source")) for r in g["terminals"] if r.get("wire_uid") == w])
for k, a in enumerate(json.load(open(V14, encoding="utf-8"))["actions"][:4], 1):
    print("V14 #{0}".format(k), json.dumps(a, ensure_ascii=True)[:500])
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
