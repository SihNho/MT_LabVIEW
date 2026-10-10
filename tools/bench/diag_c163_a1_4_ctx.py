# ---
# labview: none
# hardware: none
# evidence: tools/bench/prep_c163_a1_3_dry.log
# ---
r"""diag_c163_a1_4_ctx - card 163-a1-4 Part 1, OFFLINE (stored files only). Measures what stagekit.pb_inherit_ctx holds for plan_ring_p5s02c.json
and what pb_inherited_row says for the two blocked #376 PB rows ('error in', 'total data array in'), on the sim end re-keyed by the dry's bindings
(G1 := Gsimb, the same construction as selftest_c161_pbinherit.py:43-48; the dry's eq_diff was [] so real == sim re-keyed).
Existing functions found and CALLED (no logic copied): stagekit.pb_inherit_ctx / pb_check_bound / pb_bound_rows / frame_tag_map / frame_src_resolve
/ pb_inherited_row / pred_end_graph / case_move_frames; stagexec.bind_state.
PREDICTION: chain ends at p5s02b; ctx frames {376,3052,3453: [31506]}; case 31308 -> [31506, 31517]; R0 == end for both sinks; class 1 fails on the
S1 uid multiset ([a,a,b,b] vs [a,b]) and on frame 31517 not inherited; class 2 fails on (i) (base after != []) since this plan has no connect.
Usage: py tools/bgrun.py --material --max-min 10 --log tools/bench/diag_c163_a1_4_ctx.log -- py -u tools/bench/diag_c163_a1_4_ctx.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import stagekit as K  # noqa: E402
import protocol  # noqa: E402

V, SX, JC = K.pure("vigraph"), K.pure("stagexec"), K.pure("jev_candidates")
LAB = JC.node_labels_default()
S1f = K.s1_frame_graph(LAB)
P = K.jload(K.BENCH, "plan_ring_p5s02c.json")
PRED = K.jload(K.BENCH, "plan_ring_p5s02c_pred.json")
FS = K.jload(K.ROOT, P["finalized"]["base"]["path"]).get("fs_tunnel_pairs")
FLAT = {-1: 10000001, -2: 10000004, -7: 10000007, -10: 10000010, -13: 10000015, -19: 10000021}   # the dry's bindings (prep_c163_a1_3_dry.log STEPX 01-07)
L = K.jload(K.ROOT, P["finalized"]["step_files"][-1]["path"])["state"]
Gb = K.pred_end_graph(SX.bind_state(L, {"obj": FLAT, "term": {}, "diag": {}})[0], LAB, FS)
Gp = K.pred_end_graph(L, LAB, FS)
mf = K.case_move_frames(P, L, FLAT)
ctx = K.pb_inherit_ctx(P, FLAT, labels=LAB, fs_pairs=FS, S1f=S1f, V=V)
print("CTX chain", [c["plan"] for c in ctx["chain"]], "missing", ctx["missing"])
print("CTX frames", dict((n, sorted(f)) for n, f in ctx["frames"].items()))
print("CTX cases", ctx["cases"])
print("CTX made", ctx["made"], "tunnel_case", ctx["tunnel_case"])
print("CTX connects", ctx["connects"])
r = K.pb_check_bound(S1f, Gb, Gp, Gb, PRED["cdiff_rows"], P["open_rows"], mf, (), V, inherit=ctx)
print("PB ok", r["ok"], "eq_diff", r["eq_diff"], "blocked", [x["sink"] for x in r["blocked"]], "left", r["pairs_extra_left"],
      "recorded", [(x["sink"], x.get("class")) for x in r["recorded"]])
by, fm, RB = dict((y["sink"], y) for y in r["old"]["cd"]["rows"]), K.frame_tag_map(Gb), K.pb_bound_rows(r["old"]["cd"], Gb, V)
for nm in ("error in", "total data array in"):
    s = [k for k in by if k.startswith("376|") and k.split("|")[2] == nm][0]
    res = [K.frame_src_resolve(x, fm) for x in by[s]["after"]]
    print("SINK", s, "| R0", ctx["R0"].get(s), "| bound_end", RB.get(s), "| R0==end", ctx["R0"].get(s) == RB.get(s))
    print("     after0", ctx["after0"].get(s), "| connect", ctx["connects"].get((376, nm)), "| res", res)
    print("     verdict", K.pb_inherited_row(s, by[s], res, Gb, S1f, RB.get(s), ctx))
bad = r["eq_diff"] or len(r["blocked"]) != 2
print(protocol.result_line(protocol.make_result(1 if not bad else 0, 1 if bad else 0, "unexpected PB shape" if bad else None, [])), flush=True)
