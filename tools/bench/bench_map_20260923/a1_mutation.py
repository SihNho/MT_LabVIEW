r"""A1 - MUTATION TEST of the connectivity map (plan step 5b A1), on a DATED SCRATCH of S1 (deleted at the end).

KNOWN ANSWER: 8 wires deleted + 1 wire added = exactly 9 changed EDGE rows in diff(S1, mutated), keyed by owner uid
+ terminal name (Pre-decided 137). The edits go through `stagekit.from_decision` (8 `delete` rows + 1 `wire` row,
op by `jev_pairs.op_rule` - Pre-decided 143), so the executor is exercised too.
  8 deletions: single-source single-sink wires whose BOTH ends are computation nodes (not a tunnel, register,
     structure, front-panel terminal, Local/Global - vigraph.is_scheduling / FP), sampled with seed 20260923.
  1 addition : on the frame-loop body (diagram 639), the first (by uid) UNWIRED `error out` source -> UNWIRED
     `error in (no error)` sink on two different Property nodes, the sink not reaching the source (no cycle).
PREDICTION CONTRACT
  C0 control: diff(S1 wiki graph, fresh read of the UNMUTATED scratch) has 0 edge rows / 0 node / 0 terminal changes
  C1 diff(S1, mutated) edge rows == the 9 expected: precision 1.0, recall 1.0 (0 missed, 0 spurious)
  C2 no node / terminal added or removed after the junk purge; changed_sinks == 9
  H  scratch deleted, refs opened == closed, S1 + pins unchanged, nothing left in claudeDev

    MATERIAL=1 py tools/bgrun.py --max-min 30 --log tools/bench/bench_map_a1.log -- py -u tools/bench/bench_map_20260923/a1_mutation.py
"""
import random
import sys
import time

import common as C
from common import K, V
import jev_pairs as JP                                                             # noqa: E402


def body(s):
    s.start()
    s.discard_work()
    G0 = C.s1_graph()
    s.head("[C0] control: the UNMUTATED scratch read fresh vs the S1 wiki graph")
    Gc = C.live_graph(s.work, G0, "a1_control")
    dc = V.diff(G0, Gc)
    s.fact("fresh read: {0}".format(Gc["live"]))
    s.gate("C0 control diff is empty", not C.edge_rows(dc) and not dc["nodes_added"] and not dc["nodes_removed"]
           and not dc["terminals_added"] and not dc["terminals_removed"],
           "{0}; nodes +{1}/-{2}; terminals +{3}/-{4}".format(dc["counts"], len(dc["nodes_added"]),
                                                            len(dc["nodes_removed"]), len(dc["terminals_added"]),
                                                            len(dc["terminals_removed"])))
    s.head("[1] choose the 9 mutations from the S1 graph")
    node_ok = lambda n: not V.is_scheduling(G0, n) and G0["cls"].get(n) != V.FP_CLASS
    pool = []
    for w in sorted(set(e[3] for e in G0["edges"] if e[0] == "wire")):
        es = C.wire_edge(G0, w)
        if len(es) == 1 and all(node_ok(V.key_parts(k)[0]) for k in es[0][1:]):
            pool.append(w)
    dels = sorted(random.Random(C.SEED).sample(pool, 8))
    expect = set(("-",) + C.wire_edge(G0, w)[0] for w in dels)
    rows = [{"id": "del w{0}".format(w), "action": "delete", "exec": {"wire_uid": w}} for w in dels]
    for w in dels:
        s.fact("DELETE w{0}: {1}".format(w, C.show_row(("-",) + C.wire_edge(G0, w)[0])))
    free = lambda name, src: sorted(k for k, r in G0["rows"].items() if r["term_name"] == name and not r["wire_uid"]
                                    and bool(r["is_source"]) == src and int(r.get("frame_diagram") or 0) == C.BODY
                                    and G0["cls"].get(r["node"]) == "Property")
    add = None
    for a in free("error out", True):
        for b in free("error in (no error)", False):
            na, nb = V.key_parts(a)[0], V.key_parts(b)[0]
            if na != nb and not V.path(G0, nb, na):
                add = (a, b)
                break
        if add:
            break
    s.gate("K4 a legal unwired pair exists for the ADD row", add is not None, add and [V.show(x) for x in add])
    cand = {"src": dict(JC_row(G0, add[0]), key=add[0]), "dst": dict(JC_row(G0, add[1]), key=add[1])}
    op, variant, why = JP.op_rule(cand)
    s.fact("ADD {0} -> {1}; op_rule -> {2} ({3})".format(V.show(add[0]), V.show(add[1]), op, why))
    rows.append({"id": "add", "action": "wire", "op": op, "variant": variant,
                 "exec": {"src": cand["src"], "dst": cand["dst"]}})
    expect.add(("+", "wire", add[0], add[1]))
    s.head("[2] execute through stagekit.from_decision")
    t0 = time.time()
    res = s.from_decision({"decisions": rows}, "a1")
    s.fact("from_decision {0:.1f}s; errors {1}".format(time.time() - t0, [r.get("error") for r in res if r.get("error")]))
    s.es("after mutation")
    s.head("[3] re-read + diff")
    Gm = C.live_graph(s.work, G0, "a1_mutated")
    d = V.diff(G0, Gm)
    obs = set((r[0], r[1], r[2], r[3]) for r in C.edge_rows(d))
    hit, miss, spur = obs & expect, expect - obs, obs - expect
    prec = len(hit) / len(obs) if obs else 0.0
    rec_ = len(hit) / len(expect)
    for r in sorted(miss):
        s.fact("MISSED  {0}".format(C.show_row(r)))
    for r in sorted(spur):
        s.fact("SPURIOUS {0}".format(C.show_row(r)))
    s.R["a1"] = {"deleted": dels, "added": list(add), "expected": sorted(expect), "observed": sorted(obs),
                 "precision": prec, "recall": rec_, "counts": d["counts"], "nodes_added": d["nodes_added"],
                 "nodes_removed": d["nodes_removed"], "terminals_added": d["terminals_added"],
                 "terminals_removed": d["terminals_removed"], "read_secs": Gm["live"]["secs"],
                 "control_counts": dc["counts"], "from_decision": res}
    s.gate("C1 diff lists exactly the 9 rows: precision {0:.3f} recall {1:.3f}".format(prec, rec_),
           prec == 1.0 and rec_ == 1.0, "expected {0} observed {1} missed {2} spurious {3}".format(
               len(expect), len(obs), len(miss), len(spur)))
    s.gate("C2 no node/terminal added or removed; changed_sinks == 9",
           not (d["nodes_added"] or d["nodes_removed"] or d["terminals_added"] or d["terminals_removed"])
           and d["counts"]["changed_sinks"] == 9, "{0}; nodes +{1} -{2}".format(d["counts"], d["nodes_added"][:4],
                                                                              d["nodes_removed"][:4]))
    s.dump()


def JC_row(G, key):
    return C.JC.term_row(G, key)


if __name__ == "__main__":
    st = K.Stage(C.S1, C.S1_MD5, "bench_map_a1", preload=False, deadline_min=28,
                 task="connectivity-map step 5b A1: mutation test (8 deletes + 1 add) on a scratch of S1")
    sys.exit(K.run(body, st))
