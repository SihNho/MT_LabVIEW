r"""l2a1_real_80_derive - card 80-6, ONE-OFF, run BEFORE stagesim.op_move_in is refitted (pure Python, no LabVIEW).
The 80-5 tunflip run (tools/bench/l2a1_facts_80.py tunflip) did not save the real terminal table; it saved the stagexec.compare
of (old sim) vs (real read) and the real source->sink flips vs the base. The real read's edge/dangling sets are therefore
    E_real = E_oldsim - only_sim_edges + only_real_edges ;  D_real = D_oldsim - dangling_sim_only + dangling_real_only
and the real flips = unpredicted + predicted-and-seen. This script re-runs the OLD sim exactly as l2a1_facts_80.py:140-147 did
(same graph, same closure, same model), asserts that re-run reproduces the recorded per-run compare against that reconstruction
(so the reconstruction is self-consistent), and writes tools/bench/sim/l2a1_real_80.json for selftest_stagesim_l2a1_80.py."""
import json, os, sys                                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE); sys.path.insert(0, os.path.dirname(B))  # noqa: E702
import stagesim as SS, stagexec as SX, jev_candidates as JC, vigraph as V, protocol   # noqa: E401,E402
GA, CT, BODY = [5540, 9647, 10247, 10445, 10950, 17289, 10969, 10757], [17487, 5634], 23166
GP, FJ, TJ = (os.path.join(B, n) for n in ("l2a1_graph_k_80.json", "l2a1_facts_80.json", "l2a1_tunflip_80.json"))
OUT = os.path.join(HERE, "l2a1_real_80.json")


def closure(O, T, S):                                  # verbatim copy of tools/bench/l2a1_facts_80.py:40-46
    D, grow = set(), {S}
    while grow:
        f = set(d for d, (c, u) in O.items() if u in grow) - D
        D |= f
        grow = set(u for u, (c, d) in O.items() if d in f and c == "Diagram" and u not in D) - {S}
    return {S} | set(V.node_of(r) for r in T if int(r.get("frame_diagram") or 0) in D), D


F, gr, TF = (json.load(open(p, encoding="utf-8")) for p in (FJ, GP, TJ))
O = dict((int(k), tuple(v)) for k, v in F["owners"].items()); T = V.dedupe_rows(gr["terminals"])[0]   # noqa: E702
B0 = dict((r["term_uid"], r) for r in T)
S1, lab, P = JC.load(JC.S1_KEY), JC.node_labels_default(), SS.model_for("move_in", SS.load_models())[0]
out, ok = {"schema": "l2a1_real/1", "graph": {"path": "tools/bench/l2a1_graph_k_80.json", "md5": SS.md5_file(GP)},
           "tunflip": {"path": "tools/bench/l2a1_tunflip_80.json", "md5": SS.md5_file(TJ)}, "model_params": P, "runs": {}}, True
for run in TF["runs"]:
    us = run["moved"]
    clo = set().union(*[closure(O, T, u)[0] for u in us])
    st = SS.base_state(gr); res, _c = SS.op_move_in(st, {"nodes": sorted(clo), "dest_diagram": BODY}, P, S1, lab)
    E, D = SX.edges(SX.dedupe(st["terminals"]))
    c = run["compare"]
    Er = (E - set(map(tuple, c["only_sim_edges"]))) | set(map(tuple, c["only_real_edges"]))
    Dr = (D - set(c["dangling_sim_only"])) | set(c["dangling_real_only"])
    pred = set(f["term_uid"] for f in res["tunnel_flips"])
    flips = sorted(set(u[1] for u in run["unpredicted"]) |
                   set(t for t in pred if False))            # pred_seen is 0 on every run (l2a1_tunflip_80.log:195,215,235)
    seen = sum(v["pred_seen"] for v in run["branches"].values())
    # self-consistency: the recorded compare == (E,D) vs (Er,Dr) with the run's allow_either
    allow = set(res["allow_either"])
    d_sim = sorted(t for t in D - Dr if not (t in allow))
    d_real = sorted(t for t in Dr - D)
    same = (sorted(E - Er) == sorted(map(tuple, c["only_sim_edges"])) and d_sim == c["dangling_sim_only"]
            and d_real == c["dangling_real_only"])
    ok = ok and same and seen == 0
    print("RUN {0}: closure {1} old-sim flips {2} real flips {3} pred_seen {4} allow {5} self-consistent {6}".format(
        run["key"], len(clo), len(pred), len(flips), seen, sorted(allow), same))
    out["runs"][run["key"]] = {"moved_order": us, "closure_nodes": sorted(clo), "edges": sorted(Er), "dangling": sorted(Dr),
                               "flips_src_to_snk": flips, "real_wire_of_flipped": dict((str(u[1]), u[3]) for u in run["unpredicted"]),
                               "recorded_compare_n": c["n"], "old_sim_flips": sorted(pred),
                               # allow_either terms the old sim left dangling: the recorded compare IGNORED them when the real
                               # read had them unwired, so their real dangling state is NOT recoverable -> excluded from D checks
                               "either": sorted(allow & D)}
json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
print("WROTE", OUT, SS.md5_file(OUT))
print(protocol.result_line(protocol.make_result(1 if ok else 0, 0 if ok else 1, None if ok else "reconstruction not self-consistent")))
sys.exit(0 if ok else 1)
