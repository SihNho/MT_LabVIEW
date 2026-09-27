r"""diag_c110_stepcdiff - card 110-1 P3 OFFLINE: frame-keyed cdiff(S1, a stagesim step state) with before/after per row, for the node
uids in argv[2:] (all rows when none). No LabVIEW. Same construction as tools/bench/diag_c108b_graph.py offline().
    py tools/bgrun.py --material --max-min 3 --log <log> -- py -u tools/bench/diag_c110_stepcdiff.py <step.json> [uid ...]"""
import json, os, sys                                                                # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P, vigraph as V, jev_candidates as JC                            # noqa: E401,E402
st = json.load(open(sys.argv[1], encoding="utf-8"))
st = st.get("state") or st
want = set(int(x) for x in sys.argv[2:])
lab, s1p = JC.node_labels_default(), json.load(open(os.path.join(JC.WIKI, JC.S1_KEY + ".json"), encoding="utf-8"))
S1f = V.build4(s1p["terminals"], json.load(open(JC._newest("graph_objs_s1_*.json"), encoding="utf-8"))["objects"],
               json.load(open(JC._newest("graph_loops_s1_*.json"), encoding="utf-8"))["loops"], lab, s1p["fs_tunnel_pairs"], frame_keyed=True)
G1 = V.build4(st["terminals"], st["objs"], st["loops"], lab, st.get("fs_pairs") or st.get("fs_tunnel_pairs"), frame_keyed=True)
cd = V.computation_diff_frame(S1f, G1)
for y in cd["rows"]:
    if not want or int(y["node"]) in want:
        print("ROW {0}".format(dict((k, V.show(v) if k == "sink" else v) for k, v in y.items())), flush=True)
print("STATE KEYS", sorted(st.keys()), "rows", len(cd["rows"]), flush=True)
for r in st["terminals"]:
    if want and int(r["owner_uid"]) in want and r["term_name"] in ("x,y,z array", "x,y,z array out", ""):
        print("  T", r, flush=True)
print(P.result_line(P.make_result(1, 0, None)), flush=True)
