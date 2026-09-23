r"""l7_1_predict - cycle 70, L7-1's PREDICTION CONTRACT derived OFFLINE (pure Python, no LabVIEW, no model).
Inputs: tools/bench/graph_s3_loop15_20260924.json (the bed's terminal table, P0), graph_loops_m4b_20260924.json (machine SR
pairing, P0), split_rows_l2l7.json (#376's 12 rows), the rowD wiki's fs_tunnel_pairs, S1 via jev_candidates.load.
Method: build the bed graph exactly as stagekit.live_graph does (JC.from_parts), check computation_diff(S1,bed)=0 (baseline),
then SIMULATE L7-1 on the terminal table (Pre-decided 164): #376 -> frame 23405 with every wire cut (d1-build-plan.md:201 "the
move CUTS the wires that crossed the old border"), two new SR pairs on #23041 (fake uids 9000001..4), the 4 in-1.7 rows and the
2 SR-init rows (branches of w4969 / w3543) made; then computation_diff(S1,sim) and diff(bed,sim) ARE the prediction.
PRIOR ART: vigraph.build4/diff/computation_diff, jev_candidates.from_parts/load - used unchanged; nothing new built.
    MATERIAL=1 py tools/bgrun.py --max-min 5 --log tools/bench/l7_1_predict.log -- py -u tools/bench/l7_1_predict.py"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import jev_candidates as JC                                                        # noqa: E402
import vigraph as V                                                                # noqa: E402

B = lambda f: os.path.join(HERE, f)                                                # noqa: E731
GR = json.load(open(B("graph_s3_loop15_20260924.json"), encoding="utf-8"))
LOOPS = json.load(open(B("graph_loops_m4b_20260924.json"), encoding="utf-8"))["loops"]
ROWS = [r for r in json.load(open(B("split_rows_l2l7.json"), encoding="utf-8"))["rows"] if r["uid"] == 376]
WIKI = json.load(open(os.path.join(os.path.dirname(HERE), "..", "docs", "wiki", "subvi", JC.BED_KEY + ".json"),
                      encoding="utf-8"))
REC = {"terminals": GR["terminals"], "graph_summary": WIKI["graph_summary"]}
R1, L1, R2, L2 = 9000001, 9000002, 9000003, 9000004
SRS = ((R1, L1, "error out", 4969, 9200001, 9200002), (R2, L2, "total data array out", 3543, 9200003, 9200004))
CLASS = {0: "in-1.7", 1: "in-1.7", 2: "in-1.7", 10: "in-1.7", 5: "cross-loop OPEN", 7: "cross-loop OPEN",
         8: "cross-loop OPEN", 4: "L7-R", 3: "cross-loop OPEN + L7-R (split net)",
         6: "top-level tunnel (L7-1 rule row, PD166)", 9: "top-level tunnel (L7-1 rule row, PD166)",
         11: "top-level tunnel (L7-1 rule row, PD166)"}
PASS = []


def gate(label, ok, detail=""):
    PASS.append(bool(ok))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, detail), flush=True)


def graph(terms, objs, loops, key):
    return JC.from_parts(dict(REC, terminals=terms), objs, loops, JC.node_labels_default(), WIKI["fs_tunnel_pairs"], key)


print("---------- [a] #376's 12 rows, classified (split_rows_l2l7.json + graph_s3_loop15)")
for r in ROWS:
    print("  ROW  i{0:<2} {1!r:34} w{2:<5} {3:<22} -> {4}".format(r["i"], r["name"], r["wire"], r["action"], CLASS[r["i"]]))
cnt = {}
for c in CLASS.values():
    cnt[c] = cnt.get(c, 0) + 1
print("  FACT  class counts {0}; plus 2 SR-init rows (#4910 -> new L1 outer via w4969, #781 -> new L2 outer via w3543)".format(cnt))
gate("A1 12 rows for #376, every one classified", len(ROWS) == 12 and all(r["i"] in CLASS for r in ROWS), len(ROWS))
S1 = JC.load(JC.S1_KEY)
Gb = graph(GR["terminals"], GR["objs"], LOOPS, "bed")
cd0 = V.computation_diff(S1, Gb)
gate("B0 baseline computation_diff(S1, bed-as-built-here) == 0 rows", not cd0["rows"], len(cd0["rows"]))
terms, objs, loops = copy.deepcopy(GR["terminals"]), list(GR["objs"]), copy.deepcopy(LOOPS)
names = {}
for t in terms:
    if t["owner_uid"] == 376:
        t["frame_diagram"], names[t["term_name"]] = 23405, t
        t["wire_uid"] = 0
tu = 9100001
for i, (r, l, nm, init_w, w_in, w_out) in enumerate(SRS):
    y = 6600 + 60 * i
    objs += [{"uid": r, "class": V.SR_R, "pos": [6000, y], "owner": "WhileLoop"},
             {"uid": l, "class": V.SR_L, "pos": [4587, y], "owner": "WhileLoop"}]
    names[nm]["wire_uid"] = w_in                                            # #376 output -> right inner
    names["error in" if i == 0 else "total data array in"]["wire_uid"] = w_out  # left inner -> #376 input
    for own, cls, tc, src, fd, w in ((r, V.SR_R, "OuterTerminal", True, 686, 0), (r, V.SR_R, "InnerTerminal", False, 23405, w_in),
                                     (l, V.SR_L, "OuterTerminal", False, 686, init_w), (l, V.SR_L, "InnerTerminal", True, 23405, w_out)):
        terms.append({"term_uid": tu, "term_name": nm, "is_source": src, "wire_uid": w, "owner_uid": own,
                      "owner_class": cls, "frame_diagram": fd, "term_class": tc})
        tu += 1
# Pre-decided 166 (rerun 2026-09-24): i6/i9/i11 re-made as NEW tunnels on #23041 off the SAME outer feed (tunnel_outer,
# PD146); the old tunnel is deleted as an orphan when every inner wire reads 0 (#3644, #2294; #5096 still feeds #23175).
TUN = ((9000011, 3644, "cal cluster path", 21, 9200011), (9000012, 2294, "file size", 2362, 9200012),
       (9000013, 5096, "selected path", 5104, 9200013))
for nt, old, sink, outer_w, w in TUN:
    objs.append({"uid": nt, "class": "LoopTunnel", "pos": [4587, 6700], "owner": "WhileLoop"})
    names[sink]["wire_uid"] = w
    for tc, src, fd, ww in (("OuterTerminal", False, 686, outer_w), ("InnerTerminal", True, 23405, w)):
        terms.append({"term_uid": tu, "term_name": "", "is_source": src, "wire_uid": ww, "owner_uid": nt,
                      "owner_class": "LoopTunnel", "frame_diagram": fd, "term_class": tc})
        tu += 1
ORPH = set(o for _n, o, _s, _w, _x in TUN if not [t for t in terms if t["owner_uid"] == o and t["term_class"] == "InnerTerminal" and t["wire_uid"]])
terms = [t for t in terms if t["owner_uid"] not in ORPH]
objs = [o for o in objs if o["uid"] not in ORPH]
print("  FACT  orphan tunnels deleted in the sim (PD146): {0}".format(sorted(ORPH)))
for L in loops:
    if L["loop_uid"] == 23041:
        L["right_uids"], L["left_of"] = [R1, R2], {str(R1): [L1], str(R2): [L2]}
Gs = graph(terms, objs, loops, "sim")
cd = V.computation_diff(S1, Gs)
print("---------- [b] PREDICTED computation_diff(S1, new) rows")
pred = []
for r in cd["rows"]:
    node, _c, name, _o = V.key_parts(r["sink"])
    pred.append({"node": node, "class": r["class"], "term": name, "before": [V.show(x) for x in r["before"] or []],
                 "after": [V.show(x) for x in r["after"] or []]})
    print("  ROW  #{0} {1} {2!r}: before {3} -> after {4}".format(node, r["class"], name, pred[-1]["before"], pred[-1]["after"]))
print("  FACT  {0} predicted CDIFF rows; computation nodes added {1} removed {2}".format(
    len(pred), cd["computation_nodes_added"], cd["computation_nodes_removed"]))
ok376 = [p for p in pred if p["node"] == 376 and p["term"] in ("error in", "total data array in")]
gate("B1 #376 'error in' / 'total data array in' are NOT CDIFF rows (the new SR pairs reproduce S1's sources)", not ok376, ok376)
d = V.diff(Gb, Gs)
nd = lambda k: V.key_parts(k)[0]                                                    # noqa: E731
er = sorted(set((nd(a), nd(b)) for _k, a, b in d["edges_removed"]))
ea = sorted(set((nd(a), nd(b)) for _k, a, b in d["edges_added"]))
print("---------- [c] PREDICTED diff(bed, new)")
print("  FACT  nodes_added {0} nodes_removed {1}".format(d["nodes_added"], d["nodes_removed"]))
print("  FACT  edges_removed (node pairs) {0}".format(er))
print("  FACT  edges_added (node pairs) {0}".format(ea))
NEW = {R1, L1, R2, L2} | set(t[0] for t in TUN)
gate("C1 every removed edge touches #376 or an orphan tunnel", all(set(e) & ({376} | ORPH) for e in er), [e for e in er if not set(e) & ({376} | ORPH)])
gate("C2 every added edge touches a new SR / new tunnel", all(set(e) & NEW for e in ea), ea)
out = {"rows": [dict(i=r["i"], name=r["name"], wire=r["wire"], cls=CLASS[r["i"]]) for r in ROWS], "class_counts": cnt,
       "cdiff_rows": pred, "fake_sr": {"R1": R1, "L1": L1, "R2": R2, "L2": L2}, "orphans": sorted(ORPH),
       "nodes_added": d["nodes_added"], "nodes_removed": d["nodes_removed"],
       "edges_removed_nodes": er, "edges_added_nodes": ea}
json.dump(out, open(B("l7_1_prediction.json"), "w", encoding="utf-8"), indent=1)
print("=== GATES: {0} pass / {1} fail".format(sum(PASS), len(PASS) - sum(PASS)))
sys.exit(0 if all(PASS) else 1)
