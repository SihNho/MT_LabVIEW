r"""c73_l7r_live - cycle 73 L7-R, READ-ONLY live census of the L7-1 file BEFORE the prediction contract is written
(Pre-decided 132: every predicted value names what determines it; no L7-1 graph is on disk, facts log M1 says so).
Works on a dated SCRATCH copy (stagekit.discard_work), saves nothing, runs no VI, touches no hardware.
EXISTING (checked first): stagekit.Stage (start/discard/close), the L7-1b recipe's `lg` live-graph recipe
(stage_d1_l7_1b.py:20-26, re-used verbatim), gscript.tunnels (index_mode), gscript.node_terms_uid, vigraph.
PREDICTION: K1 input md5 e5c7d68b...; #376 owned by 23405; the rows printed are FACTS (no gate beyond K1/P0).
    MATERIAL=1 py tools/bgrun.py --max-min 20 --log tools/bench/c73_l7r_live.log -- py -u tools/bench/c73_l7r_live.py"""
import copy, json, os, sys                                                          # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, vigraph as V, jev_candidates as JC  # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                  # noqa: E731
IN, IN_MD5 = os.path.join(K.CLAUDEDEV, "D1_l7_1_20260924_060431.vi"), "e5c7d68b56d018131f2ebf0df656fdd6"
SR = J(K.BENCH, "stage_d1_l7_1a.json")["l7_1a"]["sr"]
LOOPS = J(K.BENCH, "graph_loops_m4b_20260924.json")["loops"]
WIKI = J(K.ROOT, "docs", "wiki", "subvi", JC.BED_KEY + ".json")
L17 = 23041
UIDS = (376, 2048, 6384, 3453, 3052, 2626, 1929, 5020, 15, 51, 24, 1108, 24083, 24133, 24150, 24187, 24357, 24361, 25223)


def lg(s, tag):
    loops = copy.deepcopy(LOOPS)
    for L in (x for x in loops if x["loop_uid"] == L17):
        L["right_uids"], L["left_of"] = max((v["rights"] for v in SR.values()), key=len), dict((str(v["right"]), [v["left"]]) for v in SR.values())
    lv = K.mod("wiki_build").read_live(s.work, fs_pairs=WIKI["fs_tunnel_pairs"])
    s.fact("LIVE MAP [{0}] {1}".format(tag, lv["secs"]))
    return JC.from_parts({"terminals": lv["terminals"], "graph_summary": WIKI["graph_summary"]}, lv["objs"], loops, JC.node_labels_default(), lv["fs_tunnel_pairs"], tag), lv


def body(s):
    s.start(); s.discard_work()                                                     # noqa: E702
    s.fact("HANDLES after open {0!r}".format(K.mod("bench_prep").labview_handles()))
    o = K.mod("build_d1_v0").owner_of(s.work, 376)
    s.gate("P0 #376 owned by #23405", o[1] == 23405, o)
    G, lv = lg(s, "L7-1")
    s.fact("CLASSES {0}".format(dict((u, G["cls"].get(u)) for u in UIDS)))
    own = dict((o_["uid"], o_["owner"]) for o_ in lv["objs"])
    s.fact("OWNERS {0}".format(dict((u, own.get(u)) for u in UIDS)))
    for u in UIDS:
        for k in V.terminals(G, node=u):
            r = G["rows"][k]
            w = int(r.get("wire_uid") or 0)
            peers = sorted(set(V.show(x) for x in V.wire_terminals(G, w) if x != k)) if w else []
            s.fact("TERM #{0} {1} {2!r} src={3} tuid={4} w{5} -> {6}".format(u, r["term_class"], r["term_name"], r["is_source"], r.get("term_uid"), w, peers))
    diags = g.report_all(s.work, "Diagram")
    di = dict((int(d["uid"]), d["i"]) for d in diags)
    s.fact("DIAGRAM idx 686={0} 23405={1} 639={2}".format(di.get(686), di.get(23405), di.get(639)))
    for dg, u in ((686, L17), (686, 2048), (686, 6384), (23405, 376), (639, 3052)):
        labels = g.node_labels(s.work, di[dg])
        uids = [int(r["uid"]) for r in labels]
        if u in uids:
            echo, rows = g.node_terms_uid(s.work, di[dg], uids.index(u))
            s.fact("NODETERMS D#{0} #{1} echo {2}: {3}".format(dg, u, echo, [(r["i"], r["name"], r["is_source"], r["wire"]) for r in rows]))
        else:
            s.fact("NODETERMS D#{0} #{1} NOT in Nodes[]".format(dg, u))
    for u in (1929, 5020, 24357, 24361, 25223):
        li = s.uid_index("LoopTunnel", u)
        t = g.tunnels(s.work, li) if li is not None else {}
        s.fact("TUNNEL #{0} idx {1}: index_mode {2} out_wire {3} in_wires {4} out_name {5!r} in_names {6!r}".format(
            u, li, t.get("index_mode"), t.get("out_wire"), t.get("in_wires"), t.get("out_name"), t.get("in_names")))
    S1 = JC.load(JC.S1_KEY)
    for GG, tag in ((S1, "S1"), (G, "L7-1")):
        cons = sorted(set(V.show(b) for k, a, b, _i in GG["edges"] if k in ("wire", "fs") and V.key_parts(a)[0] == 3052))
        s.fact("CONSUMERS #3052 [{0}] {1}".format(tag, cons))
    for u in (15, 51, 24, 1108, 1929, 5020):
        cons = sorted(set(V.show(b) for k, a, b, _i in G["edges"] if k in ("wire", "fs") and V.key_parts(a)[0] == u))
        s.fact("CONSUMERS carrier #{0} [L7-1] {1}".format(u, cons))
    cd = V.computation_diff(S1, G)
    for r in cd["rows"]:
        s.fact("CDIFF L7-1 ROW {0}".format(dict((k, V.show(v) if k == "sink" else v) for k, v in r.items())))
    fp = s.safe("fp_labels", lambda: g.fp_labels(s.work))[0]
    s.fact("FP labels containing 'progress': {0!r}".format([x for x in (fp or []) if "progress" in str(x)]))
    s.fact("census {0}".format(dict((c, s.count(c)) for c in ("WhileLoop", "LoopTunnel", "RightShiftRegister", "LeftShiftRegister", "ControlTerminal", "Wire"))))
    s.es("L7-1 as opened")


if __name__ == "__main__":
    st = K.Stage(IN, IN_MD5, "c73_l7r_live", preload=False, deadline_min=17)
    sys.exit(K.run(body, st))
