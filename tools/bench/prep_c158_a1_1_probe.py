# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_158-a1-1.md
# ---
r"""prep_c158_a1_1_probe - card 158-a1-1 part (a), OFFLINE on recorded data: is there a (body diagram idx, node idx, terminal idx)
triple for the wire-0 inner faces #24360 / #24367 (ops 16/17 of plan_ring_p5s02a) on body #23405 of WhileLoop #23041?
CALLS (no copies): stagexec.SimReader / Addr / _StateHolder / V.node_of / listed_as_node / tunnel_owner, on sim step_15 and the
executor's prev steps (15 / 16 for ops 16 / 17).
PREDICTION: the inner face rows exist (owner LoopTunnel, frame 23405); SimReader lists on body 23405 only the nodes whose rows sit
there and are listed_as_node (a tunnel is not); NO node_terms list on ANY diagram carries uid 24360 / 24367 (the loop's Terminals[]
lists outer faces only, SimReader.node_terms) -> no Nodes[] triple exists for either face.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c158_a1_1_probe.log -- py -u tools/bench/prep_c158_a1_1_probe.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
import stagexec as SX  # noqa: E402

G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:600]), flush=True)


P = json.load(open(os.path.join(HERE, "plan_ring_p5s02a.json"), encoding="utf-8"))
STEPS = dict((int(s["n"]), os.path.join(ROOT, s["path"])) for s in P["finalized"]["step_files"])
for sn in (15, 16):
    st = json.load(open(STEPS[sn], encoding="utf-8"))["state"]
    rd = SX.SimReader(SX._StateHolder(st))
    dl = rd.diagrams()
    print("FACT step_{0:02d} owners[23405] = {1}; body in diagram list: {2} (idx {3})".format(
        sn, (st.get("owners") or {}).get("23405"), 23405 in dl, dl.index(23405) if 23405 in dl else None), flush=True)
    for t in (24360, 24367):
        rows = [r for r in st["terminals"] if r["term_uid"] == t]
        for r in rows:
            print("FACT step_{0:02d} row #{1}: owner {2} #{3} {4} frame {5} wire {6} src {7} node_of {8} listed_as_node {9}".format(
                sn, t, r["owner_class"], r["owner_uid"], r["term_class"], r["frame_diagram"], r["wire_uid"], r["is_source"],
                SX.V.node_of(r), SX.listed_as_node(r)), flush=True)
        hits = []
        for di in range(len(dl)):
            for ni, u in enumerate(rd.node_uids(di)):
                if t in rd.node_term_uids(di, ni):
                    hits.append((dl[di], di, u, ni, rd.node_term_uids(di, ni).index(t)))
        gate("N step_{0:02d} #{1}: no Diagram.Nodes[] entry on any diagram lists it in its Terminals[]".format(sn, t), not hits, hits)
    di = dl.index(23405)
    nodes = rd.node_uids(di)
    print("FACT step_{0:02d} body 23405 Nodes[] = {1} (loop 23041 listed: {2}; tunnels 24357/24361 listed: {3})".format(
        sn, nodes, 23041 in nodes, [u for u in (24357, 24361) if u in nodes]), flush=True)
    par = [d for d in dl if 23041 in rd.node_uids(dl.index(d))]
    for d in par:
        ni = rd.node_uids(dl.index(d)).index(23041)
        print("FACT step_{0:02d} loop 23041 on diagram #{1}: Terminals[] uids {2}".format(sn, d, rd.node_term_uids(dl.index(d), ni)), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
