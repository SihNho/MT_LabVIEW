# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_167-a1-3.json
# ---
r"""prep_c167_a1_3_explore - card 167-a1-3 (OFFLINE, stored json only): prints the SHAPES of the closure inputs (p6_facts F1 rows,
p6_crows rows, the RBW Error List, the P5 graph keys) and the frame-keyed vigraph.computation_diff(S1, 7815af09) rows with their
before/after sources, so the closure script is written against measured shapes. Calls stagekit.s1_frame_graph, vigraph.build4 /
computation_diff, jev_candidates.node_labels_default; no logic of its own beyond printing.
PREDICTION CONTRACT: cdiff rows 26 (= plan_ring_p5s02e.json finalized.end_cdiff_rows), no LabVIEW.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c167_a1_3_explore.log -- py -u tools/bench/prep_c167_a1_3_explore.py"""
import json, os, sys                                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import stagekit as K, vigraph as V, jev_candidates as JC                                    # noqa: E401,E402
import prep_c156_a1_1_lib as L                                                              # noqa: E402
B = "tools/bench/"
J = L.J
f = J(B + "p6_facts.json")
print("p6_facts keys", list(f.keys()))
for k, v in f.items():
    s = json.dumps(v)
    print("== p6_facts", k, type(v).__name__, len(v) if hasattr(v, "__len__") else "", s[:700])
F1 = f.get("F1") or f.get("f1")
if isinstance(F1, dict):
    print("F1 dict keys", list(F1.keys()))
c = J(B + "p6_crows.json")
print("p6_crows keys", list(c.keys()))
for k, v in c.items():
    print("== p6_crows", k, json.dumps(v)[:1200])
e = J(B + "errorlist_D1_ring_p6rbw_20261012_191349.json")
print("EL after", json.dumps(e)[:2500])
gr = J(B + "graph_ring_p5s02e_20261012_173009.json")
print("graph keys", list(gr.keys()), "terminals0", json.dumps(gr["terminals"][0]), "objs0", json.dumps(gr["objs"][0]))
print("owners sample", list(gr["owners"].items())[:5], "loops0", json.dumps(gr["loops"][0])[:400])
lab = JC.node_labels_default()
S1f = K.s1_frame_graph(lab)
G = V.build4(gr["terminals"], gr["objs"], gr["loops"], lab, gr["fs_tunnel_pairs"], frame_keyed=True)
cd = V.computation_diff(S1f, G)
print("CDIFF rows", len(cd["rows"]), "added", len(cd["computation_nodes_added"]), "removed", len(cd["computation_nodes_removed"]))
for r in cd["rows"]:
    print("ROW", json.dumps(r)[:900])
print("renames", len(cd["renames"]))
want = J(B + "plan_ring_p5s02e.json")["finalized"]["end_cdiff_rows"]
got = sorted(str(r["sink"]) for r in cd["rows"])
print("vs end_cdiff_rows: only got", sorted(set(got) - set(want)), "only want", sorted(set(want) - set(got)))
print("G keys", sorted(G.keys())[:40])
print("G rows sample", json.dumps(list(G["rows"].values())[0])[:600])
s1 = J("docs/wiki/subvi/D1_s1_copy.json")
print("S1 terminal0", json.dumps(s1["terminals"][0]))
print(L.protocol.result_line(L.protocol.make_result(1 if len(cd["rows"]) == 26 else 0, 0 if len(cd["rows"]) == 26 else 1, None, [])))
