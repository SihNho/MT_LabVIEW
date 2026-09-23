r"""stage_d1_l7_1a - cycle 71 (runner 70) L7-1a (docs/d1-loop12-17-split-plan.md Pre-decided 169; 163 = loop 1.7 is
WhileLoop #23041, body #23405). FROM claudeDev\D1_s3_loop15.vi (1a11d92a), FRESH LabVIEW: move #376 into body #23405;
add the two NEW SR pairs on #23041 (err replaces #24/#1108, acc replaces #15/#51); WIRE NOTHING; save
claudeDev\D1_l7_1a_<ts>.vi (broken by design -> stagekit.save(broken_ok=True) = gui_save, CLAUDE.md split-rule 6,
evidence "user 2026-09-22 broken-intermediate save"; shot before/after = capture -> act -> capture).
PRIOR ART: the move + SR steps are copied UNCHANGED from tools/recipes/stage_d1_l7_1.py (lines 29-35, 46-56), which ran
them clean twice (stage_d1_l7_1.log:80-90, stage_d1_l7_1_r2.log:71-81); stagekit / wiki_build.read_live / vigraph.diff /
build_d1_v0.owner_of used unchanged. No op, no Jev, no wiring row.
CONTRACT (written before the run to tools/bench/l7_1a_predict.log): P0 owners as S3; P1 #376 owned by #23405, 12
terminals all bare; PD diff(bed,new): nodes_added == exactly the 4 new SR uids, nodes_removed == [], every removed
uid-edge touches #376, no uid-edge added; P3 WhileLoop/Local/ControlTerminal/SubVI/LoopTunnel counts delta 0;
PS saved, md5 != bed, bed md5 unchanged; H2/H3/H5 (bed unchanged, pins, refs opened == closed). ExecState RECORDED ONLY.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/stage_d1_l7_1a.log -- py -u tools/recipes/stage_d1_l7_1a.py"""
import copy, json, os, sys, time                                                   # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, jev_candidates as JC, vigraph as V             # noqa: E401,E402
BED, BED_MD5, STAMP = os.path.join(K.CLAUDEDEV, "D1_s3_loop15.vi"), "1a11d92aacabf7ec844d65b8af19f39f", time.strftime("%Y%m%d_%H%M%S")
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
LOOPS = J(K.BENCH, "graph_loops_m4b_20260924.json")["loops"]
WIKI = J(K.ROOT, "docs", "wiki", "subvi", JC.BED_KEY + ".json")
L17, B17, F686 = 23041, 23405, 686
CLS, SR = ("WhileLoop", "Local", "ControlTerminal", "SubVI", "LoopTunnel", "Wire"), {}


def lg(s, tag):                                        # live map; 1.7's new pairs MACHINE-paired (shift_reg_left)
    loops = copy.deepcopy(LOOPS)
    for L in (x for x in loops if x["loop_uid"] == L17 and SR):
        L["right_uids"], L["left_of"] = max((v["rights"] for v in SR.values()), key=len), dict((str(v["right"]), [v["left"]]) for v in SR.values())
    lv = K.mod("wiki_build").read_live(s.work, fs_pairs=WIKI["fs_tunnel_pairs"])
    s.fact("LIVE MAP [{0}] {1}".format(tag, lv["secs"]))
    return JC.from_parts({"terminals": lv["terminals"], "graph_summary": WIKI["graph_summary"]}, lv["objs"], loops, JC.node_labels_default(), lv["fs_tunnel_pairs"], tag)


def add_sr(s, key, y):
    li = s.uid_index("WhileLoop", L17)
    right = int(s.add_shift_reg(li, y_position=y)["result"])
    rights = [int(g.shift_reg(s.work, li, k)["uid"]) for k in range(len(SR) + 1)]  # #23041 held 0 registers (P0)
    SR[key] = {"right": right, "left": int(g.shift_reg_left(s.work, li, rights.index(right))["left"]["uid"]), "rights": rights}
    s.junk_purge("add_sr " + key)
    s.fact("NEW SR [{0}] on #{1}: {2}".format(key, L17, SR[key]))


def body(s):
    print(__doc__, flush=True); s.start(); s.discard_work()   # until a save lands, the byte copy is a scratch  # noqa: E702
    B = K.mod("build_d1_v0")
    s.fact("HANDLES after opening the bed: {0!r}".format(K.mod("bench_prep").labview_handles())); s.es("P0 bed on open")  # noqa: E702
    o = [B.owner_of(s.work, u) for u in (B17, L17, 376)]
    s.gate("P0 #23405 owned by #23041, #23041 on #686, #376 on #639", [x[1] for x in o] == [L17, F686, 639], o, fatal=True)
    b, Gb = dict((c, s.count(c)) for c in CLS), lg(s, "bed")
    s.move_in(376, B.diag_index(s.work, B17), (4760, 6765)); s.junk_purge("after move_in")  # noqa: E702
    rows = s.wired_terminals(376, tag="P1 #376 after the move")[1]; ow, wired = B.owner_of(s.work, 376), [(r["name"], r["wire"]) for r in rows if r.get("has_wire")]  # noqa: E702
    s.gate("P1 #376 owned by #23405, 12 terminals, every terminal bare", ow[1] == B17 and len(rows) == 12 and not wired, (ow, len(rows), wired), fatal=True)
    [add_sr(s, k, y) for k, y in (("err", 120), ("acc", 180))]                    # distinct TOPs (vigraph TOP pairing fallback)
    s.junk_purge("final")
    a = dict((c, s.count(c)) for c in CLS)
    s.fact("census before {0} -> after {1}".format(b, a))
    s.gate("P3 WhileLoop/Local/ControlTerminal/SubVI/LoopTunnel delta 0", all(a[c] == b[c] for c in CLS[:5]), "{0} -> {1}".format(b, a))
    s.es("after move + SRs (RECORDED ONLY)")
    Gn, srs = lg(s, "new"), set(u for v in SR.values() for u in (v["right"], v["left"]))
    d = V.diff(Gb, Gn)
    rem, add = sorted(K.uid_edges(Gb) - K.uid_edges(Gn)), sorted(K.uid_edges(Gn) - K.uid_edges(Gb))
    s.fact("diff(bed,new) nodes_added {0} removed {1}".format(sorted(d["nodes_added"]), sorted(d["nodes_removed"])))
    s.fact("diff(bed,new) uid-keyed wire/fs edges removed ({0}) {1}".format(len(rem), rem))
    s.fact("diff(bed,new) uid-keyed wire/fs edges added ({0}) {1}".format(len(add), add))
    n376 = sorted(set(Gn["rows"][k].get("frame_diagram") for k in V.terminals(Gn, node=376)))
    s.fact("#376 terminal frame_diagram in the new graph: {0}".format(n376))
    s.gate("PD1 nodes_added == exactly the 4 new SR uids {0}".format(sorted(srs)), set(d["nodes_added"]) == srs and len(srs) == 4, sorted(d["nodes_added"]))
    s.gate("PD2 nodes_removed == []", not d["nodes_removed"], sorted(d["nodes_removed"]))
    s.gate("PD3 every removed uid-edge touches #376; no uid-edge added", all(376 in (e[1], e[3]) for e in rem) and not add,
           ([e for e in rem if 376 not in (e[1], e[3])], add))
    shot = lambda n: g._lv_gui("-Action", "shot", "-Out", '"{0}"'.format(os.path.join(K.BENCH, "l7_1a_{0}_{1}.png".format(STAMP, n))))  # noqa: E731
    m = (shot("before_save"), s.save(broken_ok=True), shot("after_save"))[1]    # capture -> save (mtime-confirmed) -> capture
    s.gate("PS artefact saved, md5 differs from the bed; bed md5 unchanged", m and m != BED_MD5 and K.md5(BED) == BED_MD5, (m, K.md5(BED)))
    _x = m and m != BED_MD5 and s.scratches.remove(s.work)   # saved -> the work copy IS the artefact
    s.R["l7_1a"] ={"final": s.work, "md5": m, "bytes": os.path.getsize(s.work) if os.path.exists(s.work) else None, "sr": SR}
    s.dump()


if __name__ == "__main__":
    st = K.Stage(BED, BED_MD5, "stage_d1_l7_1a", preload=False, deadline_min=28, work_name="D1_l7_1a_{0}.vi".format(STAMP), pins=tuple(K.DEFAULT_PINS) + (("S3 loop15 bed", BED, BED_MD5),))
    sys.exit((K.run(body, st), K.mod("bench_prep").restart_labview())[0])
