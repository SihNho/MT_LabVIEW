r"""p0_c69_census - cycle 69 P0 (docs/d1-loop12-17-split-plan.md). MATERIAL, READ-ONLY on a dated scratch copy of
claudeDev\D1_s3_loop15.vi (deleted at close). NO VI run, no original opened, no motor/ASI/camera.
EXISTING TOOLS (checked first, nothing new built): stagekit.Stage (pins, restart, scratch, hygiene), wiki_build.read_live
+ jev_candidates.from_parts (= Stage.live_graph, stagekit.py:802), the bed's machine loop table
graph_loops_m4b_20260924.json (md5 1a11d92a = this bed, q_c68_srpair), build_d1_v0.owner_of (OpOwnerChain_v1).
PREDICTIONS: K1/H2 bed md5 1a11d92a before and after; B0 owner(#23166)=WhileLoop #10170, owner(#23405)=#23041;
  (1) both bodies hold no plan L2/L7 node (the plan says they are unassigned, Pre-decided 150);
  (2) ForLoops #1359/#29874 hold 0 right SRs (loop table) -> RECORDED: left-SR TOP collisions per body;
  (3) handles: base (60 s after restart) -> +~20.4k after open (q_c68 log) -> close: RECORDED, not predicted;
  (4) every plan row's uid exists on the bed; rows RECORDED as name / wire / uid-only / missing.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/p0_c69_census.log -- py -u tools/bench/p0_c69_census.py
"""
import collections, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import vigraph as V                                                                # noqa: E402
import jev_candidates as JC                                                        # noqa: E402

g, B, DATE = K.g, K.BENCH, time.strftime("%Y%m%d")
BED, BED_MD5 = os.path.join(K.CLAUDEDEV, "D1_s3_loop15.vi"), "1a11d92aacabf7ec844d65b8af19f39f"
L2 = [5540, 9647, 10247, 10445, 10950, 17289, 10969, 10757, 1359, 2222, 2626, 6104, 8885, 9833, 11261, 29874, 10686, 5058]
L7 = [376]
BODIES = {23166: 10170, 23405: 23041}
TOUCH_WHILE = (637, 10170, 23041)
J = lambda n: json.load(open(os.path.join(B, n), encoding="utf-8"))


def main(s):
    bp, OW = K.mod("bench_prep"), K.mod("build_d1_v0").owner_of
    s.restart(); time.sleep(60)
    h = {"base_60s_after_restart": bp.labview_handles()}
    s.start(); s.discard_work(); time.sleep(60)
    h["after_open_60s"] = bp.labview_handles()
    s.fact("H3a handles base {0} -> after open (+60 s) {1}".format(h["base_60s_after_restart"], h["after_open_60s"]))
    W, Gr = K.mod("wiki_build"), JC.load(JC.BED_KEY)
    lv = W.read_live(s.work, fs_pairs=Gr["wiki"]["fs_tunnel_pairs"])
    loops = J("graph_loops_m4b_20260924.json")["loops"]
    G = JC.from_parts({"terminals": lv["terminals"], "graph_summary": Gr["wiki"]["graph_summary"]}, lv["objs"], loops,
                      JC.node_labels_default(), lv["fs_tunnel_pairs"], "s3_loop15")
    with open(os.path.join(B, "graph_s3_loop15_{0}.json".format(DATE)), "w", encoding="utf-8") as f:
        json.dump({"vi": BED, "md5": BED_MD5, "terminals": lv["terminals"], "objs": lv["objs"], "secs": lv["secs"]}, f)
    s.fact("LIVE {0} terminals, {1} objects, {2}".format(len(lv["terminals"]), len(lv["objs"]), lv["secs"]))
    fd = collections.defaultdict(set)                           # node uid -> frame diagrams of its terminals
    for r in lv["terminals"]:
        fd[int(r["owner_uid"])].add(int(r.get("frame_diagram") or 0))
    own = {}
    def owner(u):
        if u not in own:
            own[u], _e = s.safe("owner_of #{0}".format(u), lambda: OW(s.work, u), ("?", 0))
        return own[u]
    # (1) O1: node sets of the two unassigned loops, and where every plan node sits now
    for d, lp in BODIES.items():
        oc = owner(d)
        s.gate("B0 body #{0} is owned by WhileLoop #{1}".format(d, lp), oc[1] == lp, oc)
        inside = sorted(u for u, ds in fd.items() if d in ds)
        s.fact("O1 body #{0} (loop #{1}) holds {2} node(s): {3}".format(d, lp, len(inside), [
            (u, G["cls"].get(u), G["labels"].get(u, "")) for u in inside]))
        s.row("O1 plan L2/L7 nodes inside #{0}".format(d), sorted(set(inside) & set(L2 + L7)), [])
    where = {}
    for u in L2 + L7:
        where[u] = {"cls": G["cls"].get(u), "frame_diagrams": sorted(fd.get(u, ())), "owner": owner(u)}
        s.fact("O1 plan #{0} {1}: terminal frames {2}, owner {3}".format(u, where[u]["cls"], where[u]["frame_diagrams"],
                                                                         where[u]["owner"]))
    # (2) left-SR TOP values per loop body; collisions; which loops the plan touches
    pos = dict((o["uid"], o["pos"]) for o in lv["objs"])
    lefts = [o["uid"] for o in lv["objs"] if o["class"] == "LeftShiftRegister"]
    by_body = collections.defaultdict(list)
    for u in lefts:
        inner = [int(r["frame_diagram"]) for r in lv["terminals"] if int(r["owner_uid"]) == u and "Inner" in (r.get("term_class") or "")]
        by_body[inner[0] if inner else 0].append((u, pos[u][1]))
    touched = set(TOUCH_WHILE) | {1359, 29874}
    for L in loops:                                             # a loop nested inside a moved node is touched too
        u, chain = L["loop_uid"], []
        x = u
        for _k in range(10):
            c = owner(x)
            if not c[1] or c[1] == x:
                break
            chain.append(c[1]); x = c[1]
        if set(chain) & set(L2 + L7):
            touched.add(u)
        s.fact("SR loop {0} #{1}: rights {2}, chain {3}".format(L["class"], u, L["right_uids"], chain[:8]))
    coll = {}
    for d, ls in sorted(by_body.items()):
        lp = owner(d)
        tops = collections.Counter(t for _u, t in ls)
        dup = sorted((t, [u for u, tt in ls if tt == t]) for t, n in tops.items() if n > 1)
        coll[d] = {"loop": lp, "lefts": ls, "collisions": dup, "touched": lp[1] in touched}
        s.fact("SR body #{0} of {1}{2}: lefts(uid,TOP) {3}; TOP collisions {4}".format(
            d, lp, " TOUCHED" if lp[1] in touched else "", sorted(ls), dup))
    s.row("J4 TOP collisions in touched loops", [(d, c["loop"], c["collisions"]) for d, c in coll.items()
                                                 if c["touched"] and c["collisions"]], "RECORDED")
    # (4) plan rows vs the live graph
    owed = set(L2 + L7)
    v0 = [dict(zip(("uid", "i", "name", "is_source", "wire"), r)) for r in J("build_d1_v0.json")["cut"] if r[0] in owed]
    rs = [r for r in J("d1_rewire_sources.json")["rows"] if r["uid"] in owed]
    s.fact("R v0 rows {0}; rewire_sources rows {1}".format(len(v0), len(rs)))
    k0, k1 = {(r["uid"], r["i"]) for r in v0}, {(r["uid"], r["i"]) for r in rs}
    s.row("R rows only in build_d1_v0 / only in d1_rewire_sources", (sorted(k0 - k1), sorted(k1 - k0)), "([], [])")
    res, tally = [], collections.Counter()
    for r in {(r["uid"], r["i"]): r for r in v0 + rs}.values():
        mine = [G["rows"][k] for k in V.terminals(G, node=r["uid"])]
        how = ("name" if r["name"] and any(m["term_name"] == r["name"] and m["is_source"] == r["is_source"] for m in mine)
               else "wire" if any(m["wire_uid"] == r["wire"] for m in mine) else "uid-only" if mine or r["uid"] in G["cls"]
               else "missing")
        tally[how] += 1
        res.append(dict(r, resolved_by=how, set="L7" if r["uid"] in L7 else "L2"))
    s.fact("R resolution over {0} distinct rows: {1}".format(len(res), dict(tally)))
    for x in res:
        if x["resolved_by"] in ("uid-only", "missing"):
            s.fact("R UNRESOLVED #{0} t{1} {2!r} src={3} w{4} -> {5}".format(x["uid"], x["i"], x["name"], x["is_source"],
                                                                            x["wire"], x["resolved_by"]))
    with open(os.path.join(B, "split_rows_l2l7.json"), "w", encoding="utf-8") as f:
        json.dump({"bed": BED, "md5": BED_MD5, "rows": res, "tally": tally, "where": where, "sr_bodies": {str(k): v for k, v in coll.items()},
                   "handles": h}, f, indent=1, default=str)
    s.safe("close_panel(work)", lambda: g.close_panel(s.work)); time.sleep(30)
    h["after_close_30s"] = bp.labview_handles()
    s.fact("H3b handles after close (+30 s) {0}; refs {1}".format(h["after_close_30s"], g.ref_counts()))


if __name__ == "__main__":
    pins = tuple(K.DEFAULT_PINS) + (("BED D1_s3_loop15", BED, BED_MD5),)
    st = K.Stage(BED, BED_MD5, "p0_c69_census", fresh=False, preload=False, deadline_min=28, reserve_s=240, pins=pins,
                 task="cycle 69 P0: O1 loop node sets, SR TOP collisions, handles open/close, L2/L7 row resolution")
    sys.exit(K.run(main, st))
