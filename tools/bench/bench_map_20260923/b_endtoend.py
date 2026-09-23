r"""B - END-TO-END, ZERO LLM TURNS (plan step 5b B), on a DATED SCRATCH of S1. The real bed is never touched.

DAMAGE: M3a-1's 11 severed wires. In S1 (original bytes) 9 of them exist, each ONE source -> ONE sink on the frame-
loop body (639); 23502/23540 were CREATED by S3b and are not in S1 (reported, not severable). Each of the 9 is
DELETED whole - on a single-sink wire that severs both ends; the bed's 4 half-wires (1731/3947/9635/7337) carry no
edge either, so the graph damage is identical (a dangling half-wire cannot be minted by any op on disk).
PIPELINE, code only: re-read -> intent per row ("restore the S1 connection of severed wire W", mechanical from the
S1 graph) -> jev_candidates.candidates -> jev_pairs.decide(by_rule=True, risk_gates=False: Pre-decided 143/144;
PAIR acts only if A5 kept it acting, at A5's threshold) -> decision record -> stagekit.from_decision -> re-read.
ARM 2 (ORACLE VERDICT, labelled): the same rows with the KNOWN S1 pair as the verdict and the same op rule, so the
op and execution layers are measured even when the verdict layer hands every row to the LLM.
PREDICTION CONTRACT (plan): 11/11 restored to their S1 endpoints, ExecState 1, computation_diff empty, diff empty;
every miss named by layer (candidate / verdict / op / execution).

    MATERIAL=1 py tools/bgrun.py --max-min 45 --log tools/bench/bench_map_b.log -- py -u tools/bench/bench_map_20260923/b_endtoend.py
"""
import json
import os
import sys
import time

import common as C
from common import K, V, JC
import jev_pairs as JP                                                             # noqa: E402


def sr_info(G0, d):
    """exec.sr for a wire_sr row: the right register (the LEFT's partner is read off S1's `sr` edges) + its loop."""
    ex = d["exec"]
    if d["variant"] == "LeftIn":
        left = ex["src"]["uid"]
        right = next(V.key_parts(a)[0] for k, a, b, _i in G0["edges"] if k == "sr" and V.key_parts(b)[0] == left)
    else:
        right = ex["dst"]["uid"]
    L = next(l for l in C.s1_loops() if right in l["right_uids"])
    return {"loop_uid": L["loop_uid"], "loop_class": L["class"], "right_uid": right, "right_uids": L["right_uids"]}


def body(s):
    T0 = time.time()
    s.start()
    s.discard_work()
    G0 = C.s1_graph()
    a5 = json.load(open(os.path.join(C.HERE, "a5_heldout.json"), encoding="utf-8"))
    th = JP.thresholds()
    th["pair"] = dict(th["pair"], act=a5["pair_act_threshold_for_B"] or th["pair"]["act"], acts=a5["pair_keeps_acting"])
    s.fact("PAIR in B: acts={0} act={1} (A5 held-out)".format(th["pair"]["acts"], th["pair"]["act"]))
    s.head("[0] sever")
    truth, rows = {}, {}
    for w in C.SEVERED:
        e = C.wire_edge(G0, w)
        rows[w] = {"wire": w, "in_s1": bool(e)}
        if e:
            truth[w] = e[0][1:]
            rows[w]["sever"] = "deleted whole wire (1 src -> 1 sink in S1)"
            before = set(C.g.uids(s.work, "Wire"))
            rows[w]["sever_op"] = s.delete_wire(w, "sever")["err"]
            gone = sorted(before - set(C.g.uids(s.work, "Wire")))       # v2: the delete VERIFIED by the Wire census
            rows[w]["uids_gone"] = gone
            s.gate("B0a delete w{0} removed exactly that uid".format(w), gone == [w], gone)
        else:
            rows[w]["sever"] = "NOT IN S1 - created by S3b; nothing to sever, nothing to restore on S1"
    s.es("after sever")
    Gs = C.live_graph(s.work, G0, "b_severed")
    ds = V.diff(G0, Gs)
    TUN = (9623, 11348, 11220)          # input tunnels whose feed was cut (v2, peer 2026-09-23 bench-map-b §4)
    inner = set(e[:3] for e in G0["edges"] if e[0] == "wire" and V.key_parts(e[1])[0] in TUN)
    ren = set(e for e in ds["edges_removed"] if "'VISA out'" in V.show(e[1]) + V.show(e[2])) - \
        set(("wire",) + t for t in truth.values())
    other = set(ds["edges_removed"]) - set(("wire",) + t for t in truth.values()) - inner - ren
    s.R["b_sever"] = {"diff_rows": sorted(C.show_row(r) for r in C.edge_rows(ds)), "counts": ds["counts"],
                      "flags_on_tunnels": [f for f in Gs["flags"] if any(V.key_parts(k)[0] in TUN + (4334, 4344, 7468)
                                                                         for k in f["src"] + f["sink"])],
                      "rows": dict((str(n), [dict((k, Gs["rows"][x][k]) for k in ("term_name", "is_source", "wire_uid",
                                                                                   "term_class")) for x in
                                             V.terminals(Gs, node=n)]) for n in TUN + (4334, 4344))}
    for f in s.R["b_sever"]["flags_on_tunnels"]:
        s.fact("SEVER flag {0}".format(f))
    s.gate("B0 damage = 9 cut + {0} tunnel-inner edges + {1} renamed 'VISA out' edges, nothing else".format(
        len(inner & set(ds["edges_removed"])), len(ren)),
           not other and inner <= set(ds["edges_removed"]) and len(ds["edges_added"]) == len(ren),
           "{0}; unexplained removed {1}".format(ds["counts"], [C.show_row(("-",) + r) for r in sorted(other)][:6]))
    s.head("[1] intents -> candidates -> Jev verdicts -> decision record (no LLM)")
    t1 = time.time()
    ints, cands, decs, oracle = [], [], [], []
    for w, (sk, dk) in sorted(truth.items()):
        a, b = G0["rows"][sk], G0["rows"][dk]
        it = {"id": w, "src": a["node"], "dst": b["node"], "src_hint": a["term_name"], "dst_hint": b["term_name"],
              "line": "restore the S1 connection of severed wire {0}: node #{1} ({2}) output {3!r} -> node #{4} ({5}) "
                      "input {6!r}".format(w, a["node"], G0["cls"][a["node"]], a["term_name"], b["node"],
                                           G0["cls"][b["node"]], b["term_name"])}
        c = JC.candidates(Gs, it)
        keys = [(p["src"]["key"], p["dst"]["key"]) for p in c["pairs"]]
        (msk, hs), (mdk, hd) = JC.map_key(Gs, sk, G0), JC.map_key(Gs, dk, G0)   # v2: renamed terminals (137 caveat)
        tk = (msk, mdk)
        rows[w].update({"n_candidates": len(keys), "truth_in_candidates": tk in keys, "truth_key_map": [hs, hd]})
        d = JP.decide(it["line"], c, G_orig=G0, G_new=Gs, orig_sink_key=dk, th=th, by_rule=True, risk_gates=False,
                      top_diagram=None)
        d["id"] = w
        if d.get("op") == "wire_sr":
            d["exec"]["sr"] = sr_info(G0, d)
        best_ok = (d["row_key"]["src_uid"], d["row_key"]["src_term"], d["row_key"]["dst_uid"], d["row_key"]["dst_term"]) \
            == (a["node"], Gs["rows"][msk]["term_name"] if msk else None, b["node"],
                Gs["rows"][mdk]["term_name"] if mdk else None)
        ps = sorted((x["p"] for x in d["evidence"].get("pairs", []) if x["p"] is not None), reverse=True)
        rows[w].update({"best_is_truth": best_ok, "best_p": d["pair_p"], "action": d["action"], "op": d["op"],
                        "op_by": d["evidence"].get("op_decided_by"), "risk_p": d["risk_p"],
                        "layer": d["evidence"].get("failed_layer"), "jev_calls": d["jev_calls"],
                        "at_step5_0.70": bool(ps and ps[0] >= 0.70 and (len(ps) < 2 or ps[1] < 0.70)) and best_ok})
        ints.append(it), cands.append(c), decs.append(d)
        if tk in keys:
            ct = c["pairs"][keys.index(tk)]
            op, var, why = JP.op_rule(ct)
            o = {"id": w, "row_key": ct["row_key"], "op": op, "variant": var, "action": "wire" if op else "llm",
                 "evidence": {"failed_layer": None if op else "op", "op_rule": why},
                 "exec": {"src": ct["src"], "dst": ct["dst"]}}
            if op == "wire_sr":
                o["exec"]["sr"] = sr_info(G0, o)
            oracle.append(o)
        s.row("w{0}".format(w), {k: rows[w].get(k) for k in ("truth_in_candidates", "n_candidates", "best_is_truth",
                                                           "best_p", "action", "op", "layer")})
    p1, rec = JP.write_record("bench_map_b", K.md5(C.S1), ints, cands, decs, t1, extra={"oracle_arm": oracle})
    s.fact("decision record {0}: {1} Jev calls, ${2}".format(p1, rec["jev_calls"], rec["cost"]["usd_est"]))
    s.head("[2] ARM 1 - the pipeline's own record")
    r1 = s.from_decision(rec, "arm1")
    done = set(r["id"] for r in r1 if r["action"] == "wire" and not r.get("error"))
    s.head("[3] ARM 2 - ORACLE verdict, same op rule, same executor")
    r2 = s.from_decision({"decisions": [o for o in oracle if o["id"] not in done]}, "arm2")
    for r in r1 + r2:
        rows[r["id"]].setdefault("exec", []).append({k: r.get(k) for k in ("action", "op", "how", "error", "failed_layer")})
    es = s.es("after repair")
    s.head("[4] re-read, diff, computation_diff")
    Gr = C.live_graph(s.work, G0, "b_repaired")
    dr, cd = V.diff(G0, Gr), V.computation_diff(G0, Gr)
    have = set((k, a, b) for k, a, b, _i in Gr["edges"])
    for w in C.SEVERED:
        rows[w]["restored_exact_s1_key"] = w in truth and ("wire",) + truth[w] in have
        mk = [JC.map_key(Gr, k, G0)[0] for k in truth[w]] if w in truth else [None, None]
        rows[w]["restored"] = rows[w]["restored_exact_s1_key"] or (None not in mk and ("wire", mk[0], mk[1]) in have)
        rows[w]["restored_as"] = [V.show(k) for k in mk if k]
    s.R["b"] = {"rows": rows, "diff_counts": dr["counts"], "diff_rows": sorted(C.show_row(r) for r in C.edge_rows(dr)),
                "cdiff_rows": cd["rows"], "cdiff_nodes_added": cd["computation_nodes_added"],
                "cdiff_nodes_removed": cd["computation_nodes_removed"], "exec_state": es, "record": p1,
                "jev_calls": rec["jev_calls"], "jev_usd": rec["cost"]["usd_est"], "wall_s": round(time.time() - T0, 1)}
    for w in C.SEVERED:
        s.fact("ROW w{0}: {1}".format(w, json.dumps(rows[w], default=str)[:600]))
    n = sum(rows[w]["restored"] for w in C.SEVERED)
    s.gate("B1 all 11 rows restored to their S1 endpoints", n == 11, "{0}/11".format(n))
    s.gate("B2 ExecState 1", es == 1, es)
    s.gate("B3 computation_diff(S1, repaired) empty", not (cd["rows"] or cd["computation_nodes_added"] or
                                                          cd["computation_nodes_removed"]),
           "{0} rows, +{1} -{2} nodes".format(len(cd["rows"]), len(cd["computation_nodes_added"]),
                                              len(cd["computation_nodes_removed"])))
    s.gate("B4 diff(S1, repaired) empty", not C.edge_rows(dr), dr["counts"])
    s.fact("wall {0:.0f}s; Jev {1} calls ${2}".format(time.time() - T0, rec["jev_calls"], rec["cost"]["usd_est"]))
    s.dump()


if __name__ == "__main__":
    st = K.Stage(C.S1, C.S1_MD5, "bench_map_b", preload=False, deadline_min=42,
                 task="connectivity-map step 5b B: end-to-end, zero LLM turns, on a scratch of S1")
    sys.exit(K.run(body, st))
