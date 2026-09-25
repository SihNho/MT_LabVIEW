r"""k_contract_79 - card 79-3 S1 CONTRACT for stage K (docs/d1-loop12-17-split-plan.md Pre-decided 177(c)(d)), READ-ONLY on
a dated scratch copy of claudeDev\D1_s4_loop17.vi (md5 4b621946..., deleted at close). NO VI run, no original opened, no
motor/ASI/camera, no GUI.
EXISTING TOOLS (checked first, nothing new built): stagekit.Stage (pins, scratch, hygiene); wiki_build.read_live (the
p0_c69_census.py graph dump, shape of graph_s3_loop15_20260924.json - the simulator's base); q_c68_srpair.mloops's
loop table recipe (gscript.loop_cast + shift_reg_left); gscript.tunnels (IndexMode, stage_d1_l7_r.py TM); build_d1_v0
.owner_of; vigraph.computation_diff; tools/bench/k_facts_79.json (every uid below is READ from it, none typed).
No terminal-level graph of D1_s4_loop17 existed (k_facts_79.py:3), so this run also WRITES the simulator base:
  tools/bench/graph_k_s4_<date>.json (terminals + objs, md5 = the bed's) and graph_loops_k_s4_<date>.json.
PREDICTIONS:
  C0 the dump reproduces the L7 record: computation_diff(S1, live bed) rows == exactly (376 'current frame data array
     in') + (376 'frame index') (tools/bench/cdiff_blindspot_74.log:49).
  C1 (177(d)) t8's wire (the bed wire k_facts names) carries EXACTLY 2 ControlTerminal sinks; each is an object of
     class ControlTerminal, reads is_source False (an indicator), and the wire's ONLY source is #5058 t8. Any other
     finding => STOP (fatal gate; judgement decides).
  C2 (177(c)) the six 'from-tunnel' originals are LoopTunnels owned by the 1.1 loop; their IndexMode is RECORDED
     (predicted 0 = non-indexed, rule 1a whole-array parameters), never changed here.
  C3 body of the K move is a Diagram owned by the 1.2 WhileLoop (Pre-decided 163), the loop sits on the same diagram
     as the six FSIT feeds.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/k_contract_79.log -- py -u tools/bench/k_contract_79.py
"""
import json, os, sys, time                                                         # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, vigraph as V, jev_candidates as JC                           # noqa: E401,E402

g, B, DATE = K.g, K.BENCH, time.strftime("%Y%m%d")
KF = json.load(open(os.path.join(B, "k_facts_79.json"), encoding="utf-8"))
BED, BED_MD5 = KF["bed"], KF["bed_md5"]
WIKI = json.load(open(os.path.join(K.ROOT, "docs", "wiki", "subvi", JC.BED_KEY + ".json"), encoding="utf-8"))
ROWS = dict((r["t"], r) for r in KF["rows"])


def mloops(s, path):
    loops = []
    for cls in ("WhileLoop", "ForLoop"):
        for i in range(g.count(path, cls)):
            r = g.loop_cast(path, i, cls)
            L = {"class": cls, "index": i, "loop_uid": int(r["loop_uid"]), "left_of": {},
                 "right_uids": [int(u) for u in r["shift_reg_uids"]]}
            for k, u in enumerate(L["right_uids"] if cls == "WhileLoop" else []):
                x, _e = s.safe("{0}[{1}] reg {2}".format(cls, i, k), lambda: g.shift_reg_left(path, i, k, class_name=cls))
                if x and x.get("uid") == u and x.get("left_uids") and not x.get("errors"):
                    L["left_of"][str(u)] = [int(v) for v in x["left_uids"]]
            loops.append(L)
    return loops


def main(s):
    s.start(); s.discard_work(); bp = K.mod("bench_prep")                          # noqa: E702
    h0 = bp.labview_handles(); s.fact("HANDLES after open {0!r}".format(h0))       # noqa: E702
    lv = K.mod("wiki_build").read_live(s.work, fs_pairs=WIKI["fs_tunnel_pairs"])
    gp = os.path.join(B, "graph_k_s4_{0}.json".format(DATE))
    json.dump({"vi": BED, "md5": BED_MD5, "terminals": lv["terminals"], "objs": lv["objs"], "secs": lv["secs"]},
              open(gp, "w", encoding="utf-8"))
    s.fact("LIVE {0} terminals, {1} objects, {2} -> {3} md5 {4}".format(len(lv["terminals"]), len(lv["objs"]), lv["secs"], gp, K.md5(gp)))
    loops = mloops(s, s.work)
    lp = os.path.join(B, "graph_loops_k_s4_{0}.json".format(DATE))
    json.dump({"vi": BED, "md5": BED_MD5, "loops": loops, "by": "k_contract_79 (loop_cast + shift_reg_left)"}, open(lp, "w", encoding="utf-8"), indent=1)
    s.fact("LOOPS {0} -> {1} md5 {2}".format([(L["loop_uid"], len(L["right_uids"]), len(L["left_of"])) for L in loops], lp, K.md5(lp)))
    G = JC.from_parts({"terminals": lv["terminals"], "graph_summary": WIKI["graph_summary"]}, lv["objs"], loops,
                      JC.node_labels_default(), lv["fs_tunnel_pairs"], "k_s4")
    S1 = JC.load(JC.S1_KEY)
    cd = V.computation_diff(S1, G)
    got = sorted(set((V.key_parts(r["sink"])[0], V.key_parts(r["sink"])[2]) for r in cd["rows"]))
    for r in cd["rows"]:
        s.fact("CDIFF ROW {0}".format(dict((k, V.show(v) if k == "sink" else v) for k, v in r.items())))
    s.gate("C0 computation_diff(S1, live bed) == the two carried L7 rows (cdiff_blindspot_74.log:49)",
           len(got) == 2 and all(n == 376 for n, _t in got) and {t for _n, t in got} == {"current frame data array in", "frame index"}, got)
    T, cls = lv["terminals"], dict((int(o["uid"]), o["class"]) for o in lv["objs"])
    t8 = ROWS[8]
    kern = next(r for r in T if r["term_uid"] == t8["term_uid"])
    w = kern["wire_uid"]
    on = [r for r in T if r["wire_uid"] == w]
    srcs = [r for r in on if r["is_source"]]
    ct = [r for r in on if r.get("term_class") == "ControlTerminal"]
    ind = [{"obj": V.node_of(r), "class": cls.get(V.node_of(r)), "name": r["term_name"], "is_source": r["is_source"],
            "owner": r["owner_uid"], "frame_diagram": r["frame_diagram"]} for r in ct]
    s.fact("C1 t8 wire w{0} (k_facts w{1}): sources {2}; ControlTerminal sinks {3}".format(
        w, t8["bed_wire"], [(r["owner_uid"], r["term_name"]) for r in srcs], ind))
    ok1 = (w == t8["bed_wire"] and len(ct) == 2 and all(x["class"] == "ControlTerminal" and not x["is_source"] for x in ind)
           and [r["term_uid"] for r in srcs] == [t8["term_uid"]])
    s.gate("C1 (177(d)) exactly 2 ControlTerminal INDICATOR sinks on t8's wire, its only source = #5058 t8", ok1, ind, fatal=True)
    B_ = K.mod("build_d1_v0")
    tm = {}
    for t, r in sorted(ROWS.items()):
        if "from-tunnel" not in (r.get("rw") or ""):
            continue
        u = r["other"][0]["uid"]
        x = g.tunnels(s.work, s.uid_index("LoopTunnel", u))
        o = s.safe("owner_of #{0}".format(u), lambda: B_.owner_of(s.work, u), ("?", 0))[0]
        tm[str(u)] = {"t": t, "index_mode": x.get("index_mode"), "owner": o, "feed": r["via"][0]["outer"][0]["ends"][0]["uid"] if r.get("via") else None}
        s.fact("C2 t{0} original #{1}: IndexMode {2}, owner {3}, tunnels() {4}".format(t, u, x.get("index_mode"), o, x))
    s.gate("C2 (177(c)) six originals read, IndexMode RECORDED (predicted 0 each)", len(tm) == 6 and all(v["index_mode"] in (0, 1) for v in tm.values()),
           dict((k, v["index_mode"]) for k, v in tm.items()))
    body = G["tree"]["parent"]
    s.fact("C3 objs: {0}".format([(o["uid"], o["class"], o["pos"], o["owner"]) for o in lv["objs"] if o["class"] == "WhileLoop"]))
    json.dump({"graph": {"path": "tools/bench/" + os.path.basename(gp), "md5": K.md5(gp)},
               "loops": {"path": "tools/bench/" + os.path.basename(lp), "md5": K.md5(lp)},
               "indicators": ind, "t8_wire": w, "index_modes": tm, "cdiff_rows": got,
               "diagram_parent": dict((str(k), v) for k, v in body.items())},
              open(os.path.join(B, "k_contract_79_data.json"), "w", encoding="utf-8"), indent=1)   # run 1 wrote k_contract_79.json, which Stage.close() then overwrote with its own record
    s.fact("HANDLES end {0!r}".format(bp.labview_handles()))


if __name__ == "__main__":
    pins = tuple(K.DEFAULT_PINS) + (("BED D1_s4_loop17", BED, BED_MD5),)
    st = K.Stage(BED, BED_MD5, "k_contract_79", preload=False, deadline_min=27, reserve_s=240, pins=pins,
                 task="card 79-3 S1: base graph + loops of the S4 bed, 177(d) indicator class, 177(c) IndexModes")
    sys.exit(K.run(main, st))
