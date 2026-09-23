r"""A2 + A3 - the map's two readers against INDEPENDENT or FRESH reads (plan step 5b), on a DATED SCRATCH of S1.

A2  200 random wires (seed 20260923, from the wires with exactly one source terminal) read by `OpWireSource_v5`
    (UID-addressed, one call per wire, `build_opconnectfromwire_v0.wire_source_owner`, n = the map's terminal
    count + 2 so the walk runs past the last terminal): its per-terminal (owner uid, is_source) multiset must equal
    the map's rows of that wire (OpAllTerms_v1, read fresh on the same scratch). Reported twice: SOURCE owner only
    (the step-1 T6 form) and the FULL endpoint multiset.
A3  the 58 FlatSequenceOuterTunnels: a FRESH `read_tunnel` (wiki_build.read_fs_tunnels, OpFsTunnelTerm_v0) vs the
    wiki's `fs_tunnel_pairs` (same op, 17:0x) = 58/58 {term_a, term_b}; and, INDEPENDENTLY, the two faces vs the
    fresh OpAllTerms_v1 rows OWNED by that FSOT = 58/58. The 518 FSIT uids are read too, reported as a FACT.
PREDICTION CONTRACT: A2 200/200 on both forms; A3 58/58 on both forms; H hygiene as stagekit.

    MATERIAL=1 py tools/bgrun.py --max-min 30 --log tools/bench/bench_map_a23.log -- py -u tools/bench/bench_map_20260923/a23_readers.py
"""
import collections
import random
import sys
import time

import common as C
from common import K, W, g


def body(s):
    s.start()
    s.discard_work()
    wiki = C.JC.load(C.JC.S1_KEY)["wiki"]
    s.head("[A2] 200 random wires vs OpWireSource_v5")
    t0 = time.time()
    rows, t_read = C.W.A.read_terms(s.work, op=C.W.A.OP_ALLTERMS_V1)
    s.fact("OpAllTerms_v1 fresh: {0} rows in {1:.1f}s".format(len(rows), t_read))
    by_wire = collections.defaultdict(list)
    for r in rows:
        if r["wire_uid"]:
            by_wire[r["wire_uid"]].append(r)
    pool = sorted(w for w, rs in by_wire.items() if sum(1 for r in rs if r["is_source"]) == 1)
    picks = sorted(random.Random(C.SEED).sample(pool, 200))
    WS = K.mod("build_opconnectfromwire_v0").wire_source_owner
    src_ok, full_ok, bad, per = 0, 0, [], []
    for w in picks:
        t1 = time.time()
        walk, err = s.safe("wire_source_owner w{0}".format(w), lambda u=w: WS(s.work, u, n=len(by_wire[u]) + 2), [])
        per.append(time.time() - t1)
        got = sorted((int(x["owner_uid"]), bool(x["is_source"])) for x in (walk or []) if x.get("owner_uid"))
        want = sorted((int(r["owner_uid"]), bool(r["is_source"])) for r in by_wire[w])
        gs, ws_ = [o for o, src in got if src], [o for o, src in want if src]
        src_ok += gs == ws_
        full_ok += got == want
        if got != want:
            bad.append({"wire": w, "map": want, "op": got, "err": err,
                        "op_tail": [x for x in (walk or []) if not x.get("owner_uid")][:1]})
    for b in bad[:12]:
        s.fact("A2 differs w{0}: map {1} | op {2} | tail {3}".format(b["wire"], b["map"], b["op"], b["op_tail"]))
    s.R["a2"] = {"picks": picks, "source_agree": src_ok, "full_agree": full_ok, "diffs": bad,
                 "per_call_s_median": sorted(per)[len(per) // 2], "total_s": round(time.time() - t0, 1)}
    s.gate("A2 SOURCE owner agrees on 200/200", src_ok == 200, "{0}/200".format(src_ok))
    s.gate("A2 FULL endpoint multiset agrees on 200/200", full_ok == 200, "{0}/200".format(full_ok))
    s.head("[A3] the 58 FSOT faces: fresh read_tunnel vs the wiki, and vs the fresh terminal rows")
    objs = [dict(o, pos=tuple(o["pos"])) for o in g.report_all(s.work, "GObject")]
    t0 = time.time()
    fresh = W.read_fs_tunnels(s.work, objs)
    s.fact("read_fs_tunnels: {0} tunnels in {1:.1f}s".format(len(fresh), time.time() - t0))
    wk = dict((p["uid"], p) for p in wiki["fs_tunnel_pairs"])
    owned = collections.defaultdict(set)
    for r in rows:
        owned[r["owner_uid"]].add(r["term_uid"])
    res = {}
    for cls in ("FlatSequenceOuterTunnel", "FlatSequenceInnerTunnel"):
        fr = [p for p in fresh if p["class"] == cls]
        same = [p for p in fr if p["uid"] in wk and (p["term_a"], p["term_b"]) == (wk[p["uid"]]["term_a"],
                                                                                    wk[p["uid"]]["term_b"])
                and p["term_a"] and p["term_b"]]
        indep = [p for p in fr if {p["term_a"], p["term_b"]} <= owned.get(p["uid"], set()) and p["term_a"]]
        res[cls] = {"n": len(fr), "fresh_eq_wiki": len(same), "faces_in_owned_rows": len(indep),
                    "diff_uids": sorted(p["uid"] for p in fr if p not in same)[:20]}
        s.fact("A3 {0}: {1}".format(cls, res[cls]))
    o = res["FlatSequenceOuterTunnel"]
    s.R["a3"] = res
    s.gate("A3 FSOT fresh read == wiki fs_tunnel_pairs 58/58", o["n"] == 58 and o["fresh_eq_wiki"] == 58,
           "{0}/{1}".format(o["fresh_eq_wiki"], o["n"]))
    s.gate("A3 FSOT faces == the OpAllTerms_v1 rows that FSOT owns 58/58", o["faces_in_owned_rows"] == 58,
           "{0}/{1}".format(o["faces_in_owned_rows"], o["n"]))
    s.dump()


if __name__ == "__main__":
    st = K.Stage(C.S1, C.S1_MD5, "bench_map_a23", preload=False, deadline_min=40,
                 task="connectivity-map step 5b A2+A3: reader cross-checks on a scratch of S1")
    sys.exit(K.run(body, st))
