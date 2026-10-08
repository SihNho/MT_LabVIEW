# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c153_b2_1_pre_t6.log:51
# ---
r"""diag_c153_b2_1_s06pos - card 153-b2-1: FACTS only (no fix, no retry) for the failed rescore gate 'S1 vs s06 PB'
(tools/bench/diag_c153_b2_1_rescore.log): node #2626's sink rows, OLD (name-keyed, git HEAD vigraph 13be0847) vs NEW (position-keyed) and
the NEW renames, on the same graphs diag_c153_b2_1_rescore.py builds (S1 frame-keyed vs s06 PB graph). Prints, writes nothing else.
PREDICTION: none gating; prints rows.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c153_b2_1_s06pos.log -- py -u tools/bench/diag_c153_b2_1_s06pos.py"""
import copy, json, os, sys                                                          # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)   # noqa: E702
import diag_c153_b2_1_rescore as R                                                  # noqa: E402
V, K, JC, J, B = R.V, R.K, R.JC, R.J, R.B
VO, _m = R.old_vigraph()
LAB = JC.node_labels_default(); s1p = J(os.path.join(JC.WIKI, JC.S1_KEY + ".json"))   # noqa: E702
S1f = V.build4(s1p["terminals"], J(JC._newest("graph_objs_s1_*.json"))["objects"], J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB,
               s1p["fs_tunnel_pairs"], frame_keyed=True)
st, pf, sf, gf = R.STAGES[0]
P, GR = J(B(pf)), J(B(gf))
BASE, L = J(P["finalized"]["base"]["path"]), J(P["finalized"]["step_files"][-1]["path"])["state"]
pbr, restored, _u = K.pb_rename_rows(BASE["terminals"], L["terminals"], GR["terminals"], None)
G1 = V.build4(pbr, GR["objs"], copy.deepcopy(L["loops"]), LAB, BASE.get("fs_tunnel_pairs", BASE.get("fs_pairs")), frame_keyed=True)
PA, PB = V.pos_keys(S1f), V.pos_keys(G1)
for tag, Gx, Px in (("S1", S1f, PA), ("s06", G1, PB)):
    for r in Gx["by_node"].get(2626, []):
        print("  FACT  {0} #2626 pos {1} key {2!r} wire {3}".format(tag, Px[r["key"]][1:], r["key"], r["wire_uid"]), flush=True)
print("  FACT  pb_rename_rows restored {0}".format(restored), flush=True)
o, n = VO.computation_diff_frame(S1f, G1), V.computation_diff_frame(S1f, G1)
for tag, cd in (("OLD", o), ("NEW", n)):
    for r in cd["rows"]:
        if r["node"] == 2626:
            print("  FACT  {0} row sink {1!r} before {2} after {3}".format(tag, r["sink"], r["before"], r["after"]), flush=True)
print("  FACT  NEW renames on #2626 {0}".format([x for x in n["renames"] if x["node"] == 2626]), flush=True)
print("  FACT  OLD rows not on #2626 == NEW rows not on #2626: {0}".format(
    sorted(r["sink"] for r in o["rows"] if r["node"] != 2626) == sorted(r["sink"] for r in n["rows"] if r["node"] != 2626)), flush=True)
print(R.protocol.result_line(R.protocol.make_result(1, 0, None)), flush=True)
