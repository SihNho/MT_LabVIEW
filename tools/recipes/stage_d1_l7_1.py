r"""stage_d1_l7_1 - cycle 70 BUILD L7-1 (docs/d1-loop12-17-split-plan.md §2 L7-1, Pre-decided 156-164) FROM claudeDev\D1_s3_loop15.vi (md5
1a11d92a) in a FRESH LabVIEW: move `save trace.vi` #376 from #639 (loop 1.1) into body #23405 of loop 1.7 = WhileLoop #23041 (163); two new
SR pairs on #23041 (error chain for #24/#1108, accumulator for #15/#51); wire #376 <-> them (4 rows) + each new LEFT's initial value off the
SAME source as the original pair (#4910 w4969, #781 w3543): all six via jev_candidates -> jev_pairs.decide(by_rule) -> Stage.from_decision.
Cross-loop/L7-R/tunnel rows stay OPEN (164). PRIOR ART: stagekit verbs, build_d1_v0.owner_of, wiki_build.read_live, vigraph, jev_*; m4a/m4b
shape; build_d1_m3a2 (SR init on the loop border). No op built. CONTRACT (offline l7_1_predict.py -> .log 5/0, l7_1_prediction.json; PD 132):
 (a) #376's 12 rows: in-1.7 4 (i0 i1 i2 i10) + 2 SR-init rows | cross-loop OPEN 3 (i5 w4517 #2626, i7 w3268 frame index, i8 w1397 #3052) |
     L7-R 1 (i4 -> #5020 -> #6384) | split 1 (i3 file progress: #3453 on 1.1 = OPEN, #1929 -> #6384/#2048 = L7-R) | top-level tunnel 3
     (i6 #3644, i9 #2294, i11 #5096; not in 164's DO list -> unwired, OPEN).
 P1 #376 owned by #23405 after move_in, ALL its terminals bare (d1-build-plan.md:201: a move CUTS crossing wires).
 P2 all 6 Jev rows act and execute without error; LeftIn/init ordered second pass delta 0, Is Broken? False.
 P3 WhileLoop/Local/ControlTerminal/SubVI deltas 0 (tripwire).  ExecState RECORDED ONLY (132; the OPEN rows leave inputs bare).
 (b) computation_diff(S1,new) == the 11 predicted rows (#376 i5 i6 i8 i9 i11; #2048 array/length; #3453; #6384 error in/file # to append/
     actual # data points); NOT i7 (iteration terminal = scheduling, ASSUMPTION A), NOT #376 error in/total data array in (pairs reproduce S1).
 (c) diff(bed,new): nodes_added == the 4 new SRs; removed subset of {3644,2294,1929,5020} (sim []; d1-build-plan.md:199 LoopTunnel -2 on a
     move); removed wire edges touch #376/a removed tunnel, added ones a new SR. SAVE: ES 1 script, ES 0 gui_save (§3 rule 6).
    py tools/bgrun.py --material --max-min 45 --log tools/bench/stage_d1_l7_1.log -- py -u tools/recipes/stage_d1_l7_1.py"""
import copy, json, os, sys, time                                                   # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, vigraph as V, jev_candidates as JC, jev_pairs as JP  # noqa: E401,E402
BED, BED_MD5, STAMP = os.path.join(K.CLAUDEDEV, "D1_s3_loop15.vi"), "1a11d92aacabf7ec844d65b8af19f39f", time.strftime("%Y%m%d_%H%M%S")
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PRED, LOOPS = J(K.BENCH, "l7_1_prediction.json"), J(K.BENCH, "graph_loops_m4b_20260924.json")["loops"]
WIKI = J(K.ROOT, "docs", "wiki", "subvi", JC.BED_KEY + ".json")
L17, B17, F686, TUN_OK = 23041, 23405, 686, {3644, 2294, 1929, 5020}
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

def jev_run(s, G, intents, tag):
    decs = []
    for iid, it, line, fix in intents:
        c = JC.candidates(G, it)
        decs.append(dict(JP.decide(line, c, by_rule=True, risk_gates=False), id=iid))
        d = decs[-1]
        fix(d["exec"]) if "exec" in d else None
        s.fact("JEV {0}: {1} pairs, best p {2}, action {3}, op {4}/{5}, row {6}, {7}".format(iid, len(c["pairs"]), d["pair_p"], d["action"], d["op"], d.get("variant"), d["row_key"], {k: d["evidence"].get(k) for k in ("reason", "margin")}))
    _p, rec = JP.write_record("l7_1_" + tag, BED_MD5, [i[2] for i in intents], [], decs, time.time())
    s.gate("P2a {0}: every Jev row acts".format(tag), all(d["action"] == "wire" for d in decs), [(d["id"], d["action"]) for d in decs], fatal=True)
    bad = [(r["id"], r.get("error"), r.get("failed_layer")) for r in s.from_decision(rec, "l7_1_" + tag) if r.get("error") or r.get("failed_layer")]
    s.gate("P2b {0}: every row executed without an error".format(tag), not bad, bad, fatal=True)

def body(s):
    print(__doc__, flush=True)
    s.start()
    s.discard_work()                                   # until a save lands, the byte copy of the bed is a scratch
    B = K.mod("build_d1_v0")
    s.fact("HANDLES after opening the bed: {0!r}".format(K.mod("bench_prep").labview_handles()))
    s.es("P0 bed on open")
    o = [B.owner_of(s.work, u) for u in (B17, L17, 376)]
    s.gate("P0 #23405 owned by #23041, #23041 on #686, #376 on #639", [x[1] for x in o] == [L17, F686, 639], o, fatal=True)
    b, Gb = dict((c, s.count(c)) for c in CLS), lg(s, "bed")
    s.head("[1] move #376 into body #23405, then two SR pairs on #23041")
    s.move_in(376, B.diag_index(s.work, B17), (4760, 6765))
    s.junk_purge("after move_in")
    _l, rows = s.wired_terminals(376, tag="P1 #376 after the move")
    ow, wired = B.owner_of(s.work, 376), [(r["name"], r["wire"]) for r in rows if r.get("has_wire")]
    s.gate("P1 #376 owned by #23405, every terminal bare", ow[1] == B17 and rows and not wired, (ow, len(rows), wired), fatal=True)
    [add_sr(s, k, y) for k, y in (("err", 120), ("acc", 180))]                    # distinct TOPs (vigraph TOP pairing fallback)
    E, A = SR["err"], SR["acc"]
    srx = lambda k: lambda ex: ex.__setitem__("sr", {"loop_uid": L17, "loop_class": "WhileLoop", "right_uid": SR[k]["right"], "right_uids": A["rights"]})  # noqa: E731
    s.head("[2] Jev rows: #376 <-> the new registers (typed side first)")
    jev_run(s, lg(s, "after SRs"), [
        ("err_R", {"src": 376, "dst": E["right"]}, "save trace.vi #376 output 'error out' feeds the NEW error-chain RIGHT shift register (replaces #24) of loop 1.7", srx("err")),
        ("err_L", {"src": E["left"], "dst": 376}, "the NEW error-chain LEFT shift register (replaces #1108) feeds save trace.vi #376 input 'error in'", srx("err")),
        ("acc_R", {"src": 376, "dst": A["right"]}, "save trace.vi #376 output 'total data array out' feeds the NEW accumulator RIGHT shift register (replaces #15)", srx("acc")),
        ("acc_L", {"src": A["left"], "dst": 376}, "the NEW accumulator LEFT shift register (replaces #51) feeds save trace.vi #376 input 'total data array in'", srx("acc"))], "body")
    s.head("[3] Jev rows: initial values off the SAME sources as the original pairs (Pre-decided 164)")
    G2 = lg(s, "after body rows")
    nm = dict((k, [G2["rows"][x]["term_name"] for x in V.terminals(G2, node=SR[k]["left"], is_source=False)][0]) for k in SR)
    brd = lambda k: lambda ex: ex.__setitem__("dst", {"uid": L17, "term": nm[k], "diagram": F686, "owner_class": "WhileLoop", "term_class": "Terminal"})  # noqa: E731
    jev_run(s, G2, [
        ("err_init", {"src": {"nodes": [4910]}, "dst": E["left"]}, "the error-cluster constant #4910 that initialises the original #1108 initialises the NEW error-chain LEFT register (outer)", brd("err")),
        ("acc_init", {"src": {"nodes": [781]}, "dst": A["left"]}, "Initialize Array #781 that initialises the original #51 initialises the NEW accumulator LEFT register (outer)", brd("acc"))], "init")
    s.head("[4] ordered second pass (42(b)) on the LeftIn and init wires")
    for lab, src, u, t, dg in (("err_L", E["left"], 376, "error in", B17), ("acc_L", A["left"], 376, "total data array in", B17),
                               ("err_init", 4910, L17, nm["err"], F686), ("acc_init", 781, L17, nm["acc"], F686)):
        s.expect_is_broken_false(lab, lambda src=src, u=u, t=t, dg=dg: s.cfw_second_pass(src, {"uid": u, "term": t, "diagram": dg, "owner_class": "", "term_class": ""}))
    s.junk_purge("final")
    a = dict((c, s.count(c)) for c in CLS)
    s.gate("P3 WhileLoop/Local/ControlTerminal/SubVI delta 0", all(a[c] == b[c] for c in CLS[:4]), "{0} -> {1}".format(b, a))
    s.es("after all rows (RECORDED, not a gate)")
    s.head("[5] live map -> computation_diff(S1,new) / diff(bed,new)")
    Gn = lg(s, "new")
    cd = V.computation_diff(JC.load(JC.S1_KEY), Gn)
    for r in cd["rows"]:
        s.fact("CDIFF ROW {0}".format(dict((k, V.show(v) if k == "sink" else v) for k, v in r.items())))
    got, want = set((V.key_parts(r["sink"])[0], V.key_parts(r["sink"])[2]) for r in cd["rows"]), set((p["node"], p["term"]) for p in PRED["cdiff_rows"])
    s.gate("PB computation_diff(S1,new) rows == the 11 predicted", got == want, {"extra": sorted(got - want), "missing": sorted(want - got)})
    d, new = V.diff(Gb, Gn), {E["right"], E["left"], A["right"], A["left"]}
    rem, add, gone = sorted(K.uid_edges(Gb) - K.uid_edges(Gn)), sorted(K.uid_edges(Gn) - K.uid_edges(Gb)), set(d["nodes_removed"])
    s.fact("diff(bed,new) nodes_added {0} removed {1}; uid-keyed wire/fs edges removed {2} added {3}".format(d["nodes_added"], d["nodes_removed"], rem, add))
    s.gate("PC1 nodes_added == the 4 new SRs; nodes_removed subset of {3644,2294,1929,5020}", set(d["nodes_added"]) == new and gone <= TUN_OK, (d["nodes_added"], d["nodes_removed"]))
    br, ba = [e for e in rem if not {e[1], e[3]} & ({376} | gone)], [e for e in add if not {e[1], e[3]} & new]
    s.gate("PC2 removed edges touch #376 or a removed tunnel; added ones touch a new SR", not br and not ba, (br, ba))
    shot = lambda n: g._lv_gui("-Action", "shot", "-Out", '"{0}"'.format(os.path.join(K.BENCH, "l7_1_{0}_{1}.png".format(STAMP, n))))  # noqa: E731
    m = (shot("before_save"), s.save(broken_ok=True), shot("after_save"))[1]    # capture -> save (mtime-confirmed) -> capture
    s.gate("PS artefact saved, md5 differs from the bed; bed md5 unchanged", m and m != BED_MD5 and K.md5(BED) == BED_MD5, (m, K.md5(BED)))
    if m:
        s.scratches.remove(s.work)                     # saved -> the work copy IS the artefact (discard_work undone)
    s.R["l7_1"] = {"final": s.work, "md5": m, "bytes": os.path.getsize(s.work), "sr": SR, "cdiff_rows": len(cd["rows"])}
    s.dump()

if __name__ == "__main__":
    st = K.Stage(BED, BED_MD5, "stage_d1_l7_1", preload=False, deadline_min=42, work_name="D1_l7_1_{0}.vi".format(STAMP), pins=tuple(K.DEFAULT_PINS) + (("S3 loop15 bed", BED, BED_MD5),))
    sys.exit((K.run(body, st), K.mod("bench_prep").restart_labview())[0])
