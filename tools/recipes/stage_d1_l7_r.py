r"""stage_d1_l7_r - cycle 73 L7-R (Pre-decided 175, executed, not re-decided). INPUT D1_l7_1_20260924_060431.vi (e5c7d68b...), FRESH LabVIEW ->
claudeDev\D1_s4_loop17.vi ("1.7 whole except the two QRT rows": t5 w4517, t7 w3268 OPEN). CONTRACT tools/bench/l7_r_predict.log; ALL row data READ from
l7_r_prediction.json. PRIOR ART reused: stage_d1_l7_1b.py (lg, Jev S1-mapped argmax, 2nd pass), stage_d1_m3a4.py (retire + RBW), stagekit verbs,
connect_nested_v1 (LabVIEW makes the border tunnel, toolkit-capabilities.md:68), gscript.tunnels/set_index_mode, census c73_l7r_live.log. No new op.
    MATERIAL=1 py tools/bgrun.py --max-min 40 --log tools/bench/stage_d1_l7_r.log -- py -u tools/recipes/stage_d1_l7_r.py"""
import copy, json, os, sys                                                         # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, vigraph as V, jev_candidates as JC, jev_pairs as JP  # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
IN, IN_MD5 = os.path.join(K.CLAUDEDEV, "D1_l7_1_20260924_060431.vi"), "e5c7d68b56d018131f2ebf0df656fdd6"
PINS = (("S3 loop15 bed", os.path.join(K.CLAUDEDEV, "D1_s3_loop15.vi"), "1a11d92aacabf7ec844d65b8af19f39f"), ("L7-1a file", os.path.join(K.CLAUDEDEV, "D1_l7_1a_20260924_035656.vi"), "34aaadf14091ee156e0950725de48bdf"))
SR, LOOPS, WIKI, P = J(K.BENCH, "stage_d1_l7_1a.json")["l7_1a"]["sr"], J(K.BENCH, "graph_loops_m4b_20260924.json")["loops"], J(K.ROOT, "docs", "wiki", "subvi", JC.BED_KEY + ".json"), J(K.BENCH, "l7_r_prediction.json")
L17, B17, F686, TIE = 23041, 23405, 686, dict(((u, n), i) for u, n, i in P["tie"])
T4 = lambda L: sorted((tuple(x) for x in L), key=repr)                             # noqa: E731 (key=repr: edges mix 'TFP'/'*' with ints - run 1 TypeError)

def lg(s, tag, gone=()):
    loops = [dict(L, right_uids=[u for u in L["right_uids"] if u not in gone]) for L in copy.deepcopy(LOOPS)]
    for L in (x for x in loops if x["loop_uid"] == L17):
        L["right_uids"], L["left_of"] = max((v["rights"] for v in SR.values()), key=len), dict((str(v["right"]), [v["left"]]) for v in SR.values())
    lv = K.mod("wiki_build").read_live(s.work, fs_pairs=WIKI["fs_tunnel_pairs"]); s.fact("LIVE MAP [{0}] {1}".format(tag, lv["secs"]))  # noqa: E702
    return JC.from_parts({"terminals": lv["terminals"], "graph_summary": WIKI["graph_summary"]}, lv["objs"], loops, JC.node_labels_default(), lv["fs_tunnel_pairs"], tag)

def trow(s, dg, u, i):
    di = next(d["i"] for d in g.report_all(s.work, "Diagram") if int(d["uid"]) == dg); ni = [int(r["uid"]) for r in g.node_labels(s.work, di)].index(u)  # noqa: E702
    echo, rows = g.node_terms_uid(s.work, di, ni); return di, ni, echo, [x for x in rows if int(x["i"]) == i][0]  # noqa: E702

def at(s, dg, u, name, is_src):
    """First resolution BY NAME (Pre-decided 174); the one ambiguous name (#2048 'length') is tie-broken by the index its S1 wire used (anchored by A0)."""
    if (u, name) not in TIE:
        return s.address({"uid": u, "term": name, "diagram": dg, "owner_class": "", "term_class": ""}, is_src)[0]
    di, ni, echo, r = trow(s, dg, u, TIE[(u, name)])
    s.gate("A1 #{0} Terminals[{1}] is the unwired {2!r} sink (name tie-break)".format(u, TIE[(u, name)], name), echo == u and r["name"] == name and not r["wire"] and not r["is_source"], r, fatal=True)
    return di, ni, TIE[(u, name)]

def nested(s, tag, src, dst):
    N, (sd, sn, st), (dd, dn, dt) = K.mod("build_opconnectnested_v1"), at(s, src[0], src[1], src[2], True), at(s, dst[0], dst[1], dst[2], False)
    r = s._op("connect_nested_v1", lambda: N.connect_nested_v1(s.work, dd, dn, dt, sd, sn, st, json.load(open(N.MAP_OUT, encoding="utf-8"))), tag); s.junk_purge(tag)  # noqa: E702
    s.gate("W {0} connect_nested_v1: no error, wire delta >= 1".format(tag), not r["err"] and r["result"] and not r["result"][2] and r["result"][0] >= 1, r["result"] or r["err"], fatal=True)

def tunnel_row(s, tag, src_term, dst, old, TM):
    before = set(g.uids(s.work, "LoopTunnel")); nested(s, tag, (B17, 376, src_term), dst); new = sorted(set(g.uids(s.work, "LoopTunnel")) - before)  # noqa: E702
    t = g.tunnels(s.work, s.uid_index("LoopTunnel", new[0])) if len(new) == 1 else {}; s.fact("NEW TUNNEL {0}: {1} {2}".format(tag, new, t))  # noqa: E702
    s.gate("T {0} exactly one new LoopTunnel, owned by #23041".format(tag), len(new) == 1 and K.mod("build_d1_v0").owner_of(s.work, new[0])[1] == L17, new, fatal=True)
    if t.get("index_mode") != TM[old]:
        s._op("set_index_mode", lambda: g.set_index_mode(s.work, s.uid_index("LoopTunnel", new[0]), TM[old]), "#{0} -> {1}".format(new[0], TM[old]))
        t = g.tunnels(s.work, s.uid_index("LoopTunnel", new[0]))
    s.gate("T {0} IndexMode {1} == original #{2}'s {3}".format(tag, t.get("index_mode"), old, TM[old]), t.get("index_mode") == TM[old], t, fatal=True)
    return new[0], t["out_wire"]

def second(s, sym, lab, srcs, u, t, tu):
    """42(b) ordered 2nd pass, the sink addressed by verify_term_uid ONLY now (Pre-decided 174); the source owner is the first listed that owns it."""
    for x in (sym.get(y, y) for y in srcs):
        try:
            return s.cfw_second_pass(x, {"uid": u, "term": t, "verify_term_uid": tu, "diagram": B17 if u == 376 else F686, "owner_class": "", "term_class": ""})
        except IndexError:
            s.fact("2nd pass {0}: #{1} is not the source owner on the sink's wire".format(lab, x))
    return {}

def body(s):
    print(__doc__, flush=True); s.start(); s.discard_work(); B = K.mod("build_d1_v0")  # noqa: E702
    h0 = K.mod("bench_prep").labview_handles(); s.fact("HANDLES after open (baseline) {0!r}".format(h0)); s.es("P0 on open")  # noqa: E702
    sc = s.scratch("mvprobe", source=IN)                                           # PMV: same instance, BEFORE any edit of the work copy
    r, e = s.safe("PMV move_in #3453", lambda: B.move_in(sc, 3453, B.diag_index(sc, B17), P["moves"][1][1]))
    o = s.safe("PMV owner", lambda: B.owner_of(sc, 3453))[0]; s.drop_scratch(sc, "PMV")  # noqa: E702
    s.gate("PMV move_in of ControlTerminal #3453 on a dated scratch: no error, owner == Diagram #23405", not e and o and o[1] == B17, (r, e, o), fatal=True)
    G0, S1 = lg(s, "L7-1 input"), JC.load(JC.S1_KEY)
    fi = lambda G: all(not G["rows"][k]["wire_uid"] for k in V.terminals(G, node=376, name="frame index"))  # noqa: E731
    s.gate("P1 #376 'frame index' is UNWIRED on the input (t7 stays OPEN)", fi(G0), V.terminals(G0, node=376, name="frame index"))
    c3052 = [sorted(set(V.show(b) for k, a, b, _i in GG["edges"] if k in ("wire", "fs") and V.key_parts(a)[0] == 3052)) for GG in (S1, G0)]
    s.gate("P2 #3052 sole consumer: S1 == [#376 'saved file refnum'], L7-1 == [] (other consumer => STOP)", c3052 == [["#376 Terminal 'saved file refnum'"], []], c3052, fatal=True)
    TM = dict((u, g.tunnels(s.work, s.uid_index("LoopTunnel", u)).get("index_mode")) for u in (1929, 5020)); s.fact("ORIGINAL IndexMode {0}".format(TM))  # noqa: E702
    a0 = (trow(s, F686, 2048, 3)[3], [G0["rows"][k]["wire_uid"] for k in V.terminals(G0, node=2048, term_uid=3182)])  # review c73-l7r-dryrun-negtest test 2
    s.gate("A0 #2048 Terminals[3] carries w4337 AND terminal uid 3182 carries w4337 (index 3 == uid 3182, BEFORE any edit)", a0[0]["wire"] == 4337 and a0[1] == [4337], a0, fatal=True)
    for w in P["del_w"]: s.delete_wire(w, "del")                                   # noqa: E701
    left = sorted(set(P["del_w"]) & set(g.uids(s.work, "Wire"))); s.gate("D1 the {0} wires are gone by uid".format(len(P["del_w"])), not left, left, fatal=True)  # noqa: E702
    for u, pos in P["moves"]:
        s.move_in(u, B.diag_index(s.work, B17), tuple(pos)); s.junk_purge("after move_in #{0}".format(u)); o = B.owner_of(s.work, u)  # noqa: E702
        s.gate("M #{0} owned by #23405 after move_in".format(u), o[1] == B17, o, fatal=True)
    G1 = lg(s, "after deletes + moves")
    for iid, it, (side, _nu, nt), line in P["s1map"]:                              # 168/171: Jev VERIFIES the S1-mapped pair, it does not gate on p
        d = JP.decide(line, JC.candidates(G1, it), by_rule=True, risk_gates=False); rk = d["row_key"]  # noqa: E702
        s.fact("ROWMODE {0} RULE-S1-MAPPED cands={1} p={2} margin={3} top={4} line={5!r}".format(iid, len(d["evidence"].get("pairs", [])), d["pair_p"], d["evidence"].get("margin"), rk, line))
        s.gate("P3 {0} Jev top candidate == the S1-mapped pair".format(iid), (rk["src_uid"], rk["dst_uid"]) == (it["src"], it["dst"]) and rk[side + "_term"] == nt, rk, fatal=True)
    TFP, wfp = tunnel_row(s, "tun_fp", "file progress", (F686, 2048, "length"), 1929, TM)  # FIRST: no #2048 edit between A0 and the tie-break but the deletes
    hit = [x for x in K.mod("build_opconnectfromwire_v0").wire_source_owner(s.work, wfp, n=6) if x.get("owner_uid") == TFP and x.get("is_source")]; dd, dn, dt = at(s, F686, 6384, "actual # data points", False)  # noqa: E702
    rr = s.connect_from_wire(dd, dn, dt, wfp, int(hit[0]["i"])) if len(hit) == 1 else {"err": "hits {0}".format(hit), "result": None}; s.junk_purge("tun_fp_b")  # noqa: E702
    s.gate("W tun_fp_b branch off the new tunnel's outer wire: no error", not rr["err"] and rr["result"] and not rr["result"][2], (hit, rr["result"], rr["err"]), fatal=True)
    nested(s, "acc_out", (F686, L17, ""), (F686, 2048, "array")); nested(s, "err_out", (F686, L17, "error out"), (F686, 6384, "error in"))  # noqa: E702
    TFN, _w = tunnel_row(s, "tun_fn", "file number to append out", (F686, 6384, "file # to append"), 5020, TM)
    nested(s, "ref_in", (B17, 3052, "File # Saved"), (B17, 376, "saved file refnum"))
    rw = s.wire_indicators(s.uid_index("SubVI", 376), ["file progress"], ["file progress"], diagram_index=B.diag_index(s.work, B17))
    s.gate("W fp_ind wire_indicators: no error other than its own post-wiring ExecState check", not rw["err"] or "target BROKEN after wiring" in rw["err"], rw["err"], fatal=True)
    for lab, srcs, u, t, tu in P["second"]: s.expect_is_broken_false(lab, lambda a=(lab, srcs, u, t, tu): second(s, {"TFP": TFP, "TFN": TFN}, *a))  # noqa: E701
    s.es("after all rows (warm, RECORDED)"); G2 = lg(s, "after rows"); gone = set(u for _c, u in P["retire"])  # noqa: E702
    for cls, u in P["retire"]:
        live = sorted(V.show(k) for k in V.reach4(G2, [u]) if V.key_parts(k)[0] not in gone)
        s.gate("L live consumers of retired carrier {0} #{1} == 0 (reach4, completed graph), BEFORE the deletes".format(cls, u), not live, live, fatal=True)
    for cls, u in P["retire"]: s.delete_object(cls, u, "retire")                   # noqa: E701
    left = [(c, u) for c, u in P["retire"] if u in g.uids(s.work, c)]; s.gate("R the 6 carriers are gone", not left, left, fatal=True)  # noqa: E702
    G3 = lg(s, "after retire", gone); rb = s.broken_wire_count(allow_mutation=True, tag="L7-R RBW"); Gn = lg(s, "after RBW", gone)  # noqa: E702
    s.gate("RBW removed no live uid edge (edges after retire == after RBW)", K.uid_edges(G3) == K.uid_edges(Gn), (sorted(K.uid_edges(G3) ^ K.uid_edges(Gn)), rb))
    for x in (cd := V.computation_diff(S1, Gn))["rows"]: s.fact("CDIFF ROW {0}".format(dict((k, V.show(v) if k == "sink" else v) for k, v in x.items())))  # noqa: E701
    got = sorted(set((V.key_parts(x["sink"])[0], V.key_parts(x["sink"])[2]) for x in cd["rows"]))
    s.fact("CDIFF-DIAGTERM: computation_diff reports a row for #376 'frame index' (w3268, diagram-terminal source, unwired): {0}".format((376, "frame index") in got))
    s.gate("PB computation_diff(S1,new) rows == exactly the w4517 row (FATAL, before save)", got == T4(P["cdiff"]), got, fatal=True); s.gate("P1b #376 'frame index' still UNWIRED on the output", fi(Gn), "")  # noqa: E702
    nm = lambda e: (e[0], {TFP: "TFP", TFN: "TFN"}.get(e[1], e[1]), "*" if e[1] in (TFP, TFN) else e[2], {TFP: "TFP", TFN: "TFN"}.get(e[3], e[3]), "*" if e[3] in (TFP, TFN) else e[4])  # noqa: E731
    E0, En = K.uid_edges(G0), K.uid_edges(Gn); rem, add = T4(nm(e) for e in E0 - En), T4(nm(e) for e in En - E0)  # noqa: E702
    s.fact("DIFF(L7-1,new) uid edges removed {0} added {1}".format(rem, add))
    for lab, a, b in (("PC1 removed", rem, T4(P["removed"])), ("PC2 added", add, T4(P["added"]))): s.gate("{0} uid edges == predicted".format(lab), a == b, {"extra": T4(set(a) - set(b)), "missing": T4(set(b) - set(a))})  # noqa: E701
    d = V.diff(G0, Gn); s.gate("PC3 nodes removed == the 6 carriers, added == the 2 new tunnels", set(d["nodes_removed"]) == gone and set(d["nodes_added"]) == {TFP, TFN}, (d["nodes_removed"], d["nodes_added"]))
    s.fact("CENSUS after {0}".format(dict((c, s.count(c)) for c in ("WhileLoop", "Local", "ControlTerminal", "SubVI", "LoopTunnel", "RightShiftRegister", "LeftShiftRegister", "Wire"))))
    h1 = K.mod("bench_prep").labview_handles(); s.fact("PH handles RECORDED, not gated (prior-art c73-l7r-r2 A3: editing runs grow, run 1 45,641 -> 46,120): post-load {0} -> before-save {1} (delta {2}); H5 refs opened==closed is the leak gate".format(h0, h1, (h1 or 0) - (h0 or 0)))  # noqa: E702
    shot = lambda n: g._lv_gui("-Action", "shot", "-Out", '"{0}"'.format(os.path.join(K.BENCH, "l7_r_{0}_{1}.png".format(s.stamp, n))))  # noqa: E731
    m = (shot("before_save"), s.save(broken_ok=True), shot("after_save"))[1]
    s.gate("PS artefact saved, md5 differs from the input; input unchanged", m and m != IN_MD5 and K.md5(IN) == IN_MD5, (m, K.md5(IN))); _x = m and m != IN_MD5 and s.scratches.remove(s.work)  # noqa: E702
    s.R["l7_r"] = {"final": s.work, "md5": m, "bytes": os.path.getsize(s.work) if os.path.exists(s.work) else None, "tunnels": [TFP, TFN], "cdiff_rows": got, "handles": [h0, h1]}; s.dump()  # noqa: E702

if __name__ == "__main__":
    st = K.Stage(IN, IN_MD5, "stage_d1_l7_r", preload=False, deadline_min=37, work_name="D1_s4_loop17.vi", pins=tuple(K.DEFAULT_PINS) + PINS)
    sys.exit((K.run(body, st), K.mod("bench_prep").restart_labview())[0])
