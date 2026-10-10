# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-3-4.md
# ---
r"""prep_c164_a3_4_pd399 - card 164-3-4 (OFFLINE, json only): adds the PD399(a) wire expectations (docs/d1/ring-p5c.md:114-123) to
plan_ring_p5s02d_pred.json as key `pd399a`. prep_c164_a2_3_lib.pred takes no parameter for a wire_remove_loose_ends row (OPEN in the
facts), so this driver adds the section; every value is READ (base graph 3d5196ab, the plan's sim step files, the plan rows), none typed.
Judgement of the assignment (brief_164-3-4.md:11-12): "w23460 absent" = 0 terminal rows (the sim keeps the Wire object with 0 rows,
diag_c164_a3_3_facts.md:35-38, recorded only); w23519 end sinks == its base sinks minus those owned by the deleted nodes.
Shared calls: prep_c164_a2_3_lib.wires_of / objs_of / md5 / J / rel, prep_c156_a1_1_lib.Gate.
PREDICTION CONTRACT: P0 pred keyed to plan 725cd68e; G1 base: w23460 endpoints all owned by #23042 / #23501, w23519 has >= 1 sink outside
them; S1 w23460: rows at step n-1 > 0, 0 rows at step n (dw_23460) and at the end; S2 w23519 at the step of rle_23519 and at the end: source
set == base source set, sink set == base sinks outside the deleted nodes ({t23450, t23241, t7606} per diag_c164_a3_1_facts.md:11-12); W.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c164_a3_4_pd399.log -- py -u tools/bench/prep_c164_a3_4_pd399.py"""
import json, os, sys                                                                        # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep_c164_a2_3_lib as LB                                                             # noqa: E402
B, J, md5, rel, ROOT = LB.B, LB.J, LB.md5, LB.rel, LB.ROOT
PLAN, PP = os.path.join(B, "plan_ring_p5s02d.json"), os.path.join(B, "plan_ring_p5s02d_pred.json")
DW_ID, RLE_ID = "dw_23460", "rle_23519"                                                     # plan row ids (plan_ring_p5s02d.json:143,161)
g = LB.L.Gate(width=1200)
P, PR = J(PLAN), J(PP)
PIN = sys.argv[1] if len(sys.argv) > 1 else "725cd68e"                                     # card 164-3-6: the re-made plan's pin as argv[1]
g("P0 pred keyed to the plan md5 {0} (pin {1})".format(md5(PLAN)[:8], PIN), PR["plan"]["md5"] == md5(PLAN) and md5(PLAN).startswith(PIN), PR["plan"])
A = P["actions"]
pos = dict((a["id"], n) for n, a in enumerate(A, 1))
dw, rle = A[pos[DW_ID] - 1], A[pos[RLE_ID] - 1]
DEL = set(int(a["uid"]) for a in A if a["op"] == "delete_object")
base = J(os.path.join(ROOT, P["finalized"]["base"]["path"]))
SFN = dict((int(x["n"]), x) for x in P["finalized"]["step_files"])
st = lambda n: J(os.path.join(ROOT, SFN[n]["path"]))["state"]                               # noqa: E731


def ends(state, wu):
    rows = [t for t in state["terminals"] if t.get("wire_uid") == wu]
    return (rows, sorted(int(t["term_uid"]) for t in rows if t.get("is_source")),
            sorted(int(t["term_uid"]) for t in rows if not t.get("is_source")))


w1, w2 = int(dw["wire_uid"]), int(rle["wire_uid"])
b1, _s, _k = ends(base, w1)
b2, b2src, _b2snk = ends(base, w2)
own1 = sorted(set(int(t["owner_uid"]) for t in b1))
out2 = sorted(int(t["term_uid"]) for t in b2 if not t.get("is_source") and int(t["owner_uid"]) not in DEL)
g("G1 base 3d5196ab: w{0} owners {1} subset of the deleted nodes {2}; w{3} sinks outside them {4} (>= 1)".format(w1, own1, sorted(DEL), w2, out2),
  bool(b1) and set(own1) <= DEL and len(out2) >= 1)
n1, n2, N = pos[DW_ID], pos[RLE_ID], len(A)
r_pre, r_post, r_end = ends(st(n1 - 1), w1)[0], ends(st(n1), w1)[0], ends(st(N), w1)[0]
oe = w1 in LB.objs_of(st(N))
g("S1 w{0}: {1} row(s) at step {2}, 0 at step {3} ({4}) and 0 at the end (step {5}); Wire object at the end in sim objs: {6} (recorded only)".format(
  w1, len(r_pre), n1 - 1, n1, DW_ID, N, oe), len(r_pre) > 0 and not r_post and not r_end)
_r, s_src, s_snk = ends(st(n2), w2)
_r, e_src, e_snk = ends(st(N), w2)
g("S2 w{0} at step {1} ({2}) src {3} sinks {4}; at the end src {5} sinks {6}; expected src {7} sinks {8}".format(
  w2, n2, RLE_ID, s_src, s_snk, e_src, e_snk, b2src, out2), s_src == e_src == b2src and s_snk == e_snk == sorted(out2))
PR["pd399a"] = {
    "rule": "docs/d1/ring-p5c.md PD399(a) (:114-123) + the assignment's judgement (tools/bench/cards/brief_164-3-4.md:11-12): 'w23460 absent' = "
            "0 terminal rows; w23519 sinks after wire_remove_loose_ends == its base sinks outside the deleted nodes",
    "deleted_nodes": sorted(DEL),
    "w_delete": {"id": DW_ID, "A": 52 + n1, "wire_uid": w1, "base_owners": own1, "rows_before": len(r_pre), "rows_after": 0, "rows_end": 0,
                 "real_expect": "no terminal row carries wire_uid {0} after op {1}; Wire object expected absent too (sim keeps it, "
                                "tools/stagesim.py:1446-1448, diag_c164_a3_3_facts.md:35)".format(w1, DW_ID)},
    "w_loose": {"id": RLE_ID, "A": 52 + n2, "wire_uid": w2, "source_terms": b2src, "sink_terms_expected": sorted(out2),
                "sim_at_step": {"src": s_src, "sinks": s_snk}, "sim_end": {"src": e_src, "sinks": e_snk},
                "real_expect": "after wire_remove_loose_ends the wire keeps source {0} and exactly the sinks {1}".format(b2src, sorted(out2))},
    "evidence": {"base": {"path": P["finalized"]["base"]["path"], "md5": md5(os.path.join(ROOT, P["finalized"]["base"]["path"]))},
                 "step_files": [SFN[k]["path"] for k in (n1 - 1, n1, n2, N)], "maker": "tools/bench/prep_c164_a3_4_pd399.py"}}
json.dump(PR, open(PP, "w", encoding="utf-8"), indent=1)
g("W pred re-read: pd399a present, plan md5 unchanged", J(PP).get("pd399a", {}).get("w_loose", {}).get("sink_terms_expected") == sorted(out2)
  and J(PP)["plan"]["md5"] == md5(PLAN))
print("FACT md5 {0} {1}".format(md5(PP), rel(PP)), flush=True)
sys.exit(g.result([{"path": rel(PP), "md5": md5(PP)}]))
