r"""prep_c139_5_probe - card 139-5 pass 2 (offline, no LabVIEW): read the bed graph graph_ring_p3b2b_20261002_133824.json
(50595c62) for base While #10170's body diagram #23166: its conditional-terminal row (unnamed Diagram-owned 'Terminal' sink,
stagesim.cond_row's definition), the wire on it and that wire's source, and which v12 action removes that wire.
PREDICTION CONTRACT: exactly one cond row on #23166 = t23246, wire 23310, source on #10171 (x=y?, S2 scaffold);
v12 action p4_dw_23310 (delete_wire 23310) is action 1, before p4_w_stop12; #10170 is in the loops table.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c139_5_probe.log -- py -u tools/bench/prep_c139_5_probe.py"""
import json, os, sys                                     # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
g = json.load(open(os.path.join(B, "graph_ring_p3b2b_20261002_133824.json"), encoding="utf-8"))
P = json.load(open(os.path.join(B, "plan_ring_p4_v12.json"), encoding="utf-8"))
G = {"pass": 0, "fail": 0, "first": None}


def gate(ok, label, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:600]), flush=True)


print("graph keys", sorted(g.keys()) if isinstance(g, dict) else type(g))
T = g.get("terminals") or []
ow = g.get("owners") or {}
print("owners[23166] =", ow.get("23166"))
body = [int(b) for b, cu in ow.items() if int(cu[1] or 0) == 10170]
print("bodies of #10170:", body)
rows = [r for r in T if r.get("owner_uid") in body]
for r in rows:
    print("BODYROW", json.dumps(r, sort_keys=True)[:400])
cond = [r for r in rows if r["owner_class"] == "Diagram" and r["term_class"] == "Terminal" and not r["is_source"]]
# run 1 (log :24): the RAW graph lists t23246 twice (identical rows); stagesim dedupes on load (stagesim.py:309-310,
# V.dedupe_rows), so cond_row sees ONE row - count distinct terminals, as the simulator does
cond = list(dict((r["term_uid"], r) for r in cond).values())
gate(len(cond) == 1 and cond[0]["term_uid"] == 23246, "exactly one DISTINCT cond row on #10170's body = t23246 (deduped as stagesim)", [c["term_uid"] for c in cond])
w = cond[0]["wire_uid"] if cond else None
srcs = [r for r in T if w and r.get("wire_uid") == w and r.get("is_source")]
for r in [r for r in T if w and r.get("wire_uid") == w]:
    print("WIREROW w{0}".format(w), json.dumps(r, sort_keys=True)[:400])
gate(w == 23310 and len(srcs) == 1 and srcs[0].get("owner_uid") == 10171, "cond's incoming wire = w23310 from #10171", (w, [(s.get("owner_uid"), s.get("term_name")) for s in srcs]))
A = P["actions"]
ids = [a["id"] for a in A]
rm = [(i, a["id"], a["op"]) for i, a in enumerate(A, 1) if a.get("wire_uid") == w or (a["op"] == "delete_object" and srcs and a.get("uid") == srcs[0].get("owner_uid"))]
print("v12 actions removing w{0} / its source node: {1}; p4_w_stop12 = #{2}".format(w, rm, ids.index("p4_w_stop12") + 1))
gate(rm and rm[0][1] == "p4_dw_23310" and rm[0][0] < ids.index("p4_w_stop12") + 1, "v12 removes w23310 (p4_dw_23310) before p4_w_stop12", rm)
loops = g.get("loops") or []
L = [x for x in loops if int(x.get("loop_uid", 0)) == 10170]
print("loops[10170] =", L)
gate(len(L) == 1, "#10170 in the loops table", len(L))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
