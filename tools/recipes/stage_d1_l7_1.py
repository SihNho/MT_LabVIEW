r"""stage_d1_l7_1 run 2 - cycle 70 L7-1 (d1-loop12-17-split-plan.md PD 156-166) FROM claudeDev\D1_s3_loop15.vi (1a11d92a), FRESH LabVIEW: #376 ->
body #23405 of 1.7 #23041; 2 new SR pairs; 4 body rows by Jev PAIR (>=2 cands); SR-init rows #4910 w4969 / #781 w3543 = RULE-SINGLE-CANDIDATE (165);
i6/i9/i11 = NEW tunnels off the SAME outer feed as #3644/#2294/#5096 (166, tunnel_outer). i5/i7/i8 + L7-R rows OPEN (164). Run 1 stopped at
P2a (stage_d1_l7_1.log:124-126, acc_init p=0.582). PRIOR ART: stagekit, build_d1_v0, wiki_build.read_live, vigraph, jev_*, build_d1_m3a2. No op.
CONTRACT (offline l7_1_predict.py -> l7_1_predict_r2.log 5/0 -> l7_1_prediction.json; PD 132): P1 #376 in #23405, all terminals bare.
 P2a body rows act at p>=0.75; init rows 1 candidate + source == S1's (uid+term); tunnel rows live outer-feed source uid == S1's. P2b no error;
 LeftIn/init 2nd pass delta 0, Is Broken? False. P3 WhileLoop/Local/ControlTerminal/SubVI delta 0. ExecState RECORDED ONLY.
 (b) computation_diff(S1,new) == 8 rows: #376 current frame data array in / saved file refnum; #2048 array / length; #3453; #6384 actual # data
 points / error in / file # to append (NOT i6/i9/i11, NOT i7). (c) nodes_added == 4 SRs + 3 LoopTunnels; removed subset {3644,2294,1929,5020}.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/stage_d1_l7_1_r2.log -- py -u tools/recipes/stage_d1_l7_1.py"""
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

def src_of(G, node, tc):                               # (uid, term) of every wire source feeding `node`'s `tc` terminal
    return sorted(set((V.key_parts(a)[0], G["rows"][a]["term_name"]) for k, a, b, _i in G["edges"] if k == "wire" and V.key_parts(b)[0] == node and G["rows"][b]["term_class"] == tc))

def execute(s, decs, tag):
    _p, rec = JP.write_record("l7_1_" + tag, BED_MD5, [d.get("line", d["id"]) for d in decs], [], decs, time.time())
    bad = [(r["id"], r.get("error"), r.get("failed_layer")) for r in s.from_decision(rec, "l7_1_" + tag) if r.get("error") or r.get("failed_layer")]
    s.gate("P2b {0}: every row executed without an error".format(tag), not bad, bad, fatal=True)

def body(s):
    print(__doc__, flush=True); s.start(); s.discard_work()   # until a save lands, the byte copy of the bed is a scratch  # noqa: E702
    B, S1 = K.mod("build_d1_v0"), JC.load(JC.S1_KEY)
    s.fact("HANDLES after opening the bed: {0!r}".format(K.mod("bench_prep").labview_handles())); s.es("P0 bed on open")  # noqa: E702
    o = [B.owner_of(s.work, u) for u in (B17, L17, 376)]
    s.gate("P0 #23405 owned by #23041, #23041 on #686, #376 on #639", [x[1] for x in o] == [L17, F686, 639], o, fatal=True)
    b, Gb = dict((c, s.count(c)) for c in CLS), lg(s, "bed")
    s.move_in(376, B.diag_index(s.work, B17), (4760, 6765)); s.junk_purge("after move_in")  # noqa: E702
    rows = s.wired_terminals(376, tag="P1 #376 after the move")[1]; ow, wired = B.owner_of(s.work, 376), [(r["name"], r["wire"]) for r in rows if r.get("has_wire")]  # noqa: E702
    s.gate("P1 #376 owned by #23405, every terminal bare", ow[1] == B17 and rows and not wired, (ow, len(rows), wired), fatal=True)
    [add_sr(s, k, y) for k, y in (("err", 120), ("acc", 180))]                    # distinct TOPs (vigraph TOP pairing fallback)
    E, A = SR["err"], SR["acc"]
    s.head("[2] Jev PAIR rows (>=2 candidates, PD 165): #376 <-> the new registers, typed side first")
    G1, decs = lg(s, "after SRs"), []
    for iid, it, k, line in (("err_R", {"src": 376, "dst": E["right"]}, "err", "save trace.vi #376 output 'error out' feeds the NEW error-chain RIGHT shift register (replaces #24) of loop 1.7"),
                             ("err_L", {"src": E["left"], "dst": 376}, "err", "the NEW error-chain LEFT shift register (replaces #1108) feeds save trace.vi #376 input 'error in'"),
                             ("acc_R", {"src": 376, "dst": A["right"]}, "acc", "save trace.vi #376 output 'total data array out' feeds the NEW accumulator RIGHT shift register (replaces #15)"),
                             ("acc_L", {"src": A["left"], "dst": 376}, "acc", "the NEW accumulator LEFT shift register (replaces #51) feeds save trace.vi #376 input 'total data array in'")):
        c = JC.candidates(G1, it)
        d = dict(JP.decide(line, c, by_rule=True, risk_gates=False), id=iid, line=line)
        d.get("exec", {})["sr"] = {"loop_uid": L17, "loop_class": "WhileLoop", "right_uid": SR[k]["right"], "right_uids": A["rights"]}
        s.fact("JEV {0}: {1} pairs, best p {2}, action {3}, op {4}/{5}, row {6}, {7}".format(iid, len(c["pairs"]), d["pair_p"], d["action"], d["op"], d.get("variant"), d["row_key"], {x: d["evidence"].get(x) for x in ("reason", "margin")}))
        decs.append((len(c["pairs"]), d))
    s.gate("P2a body: every >=2-candidate row acts at threshold", all(n >= 2 and d["action"] == "wire" for n, d in decs), [(d["id"], n, d["action"]) for n, d in decs], fatal=True)
    execute(s, [d for _n, d in decs], "body")
    s.head("[3] RULE rows: SR init (PD 165 RULE-SINGLE-CANDIDATE) + top-level tunnels (PD 166 tunnel_outer)")
    G2, rules = lg(s, "after body rows"), []
    for iid, src, k, old in (("err_init", 4910, "err", 1108), ("acc_init", 781, "acc", 51)):
        c = JC.candidates(G2, {"src": {"nodes": [src]}, "dst": SR[k]["left"]})
        p = c["pairs"][0]["src"] if len(c["pairs"]) == 1 else {}
        ok = len(c["pairs"]) == 1 and [(p["uid"], p["term"])] == src_of(S1, old, "OuterTerminal")
        s.gate("P2a {0} RULE-SINGLE-CANDIDATE: 1 legal pair and source == S1 source of #{1} outer".format(iid, old), ok, (len(c["pairs"]), p.get("uid"), p.get("term"), src_of(S1, old, "OuterTerminal")), fatal=True)
        nm = [G2["rows"][x]["term_name"] for x in V.terminals(G2, node=SR[k]["left"], is_source=False)][0]
        rules.append({"id": iid, "action": "wire", "op": "connect_from_wire", "variant": None, "decided_by": "RULE-SINGLE-CANDIDATE", "exec": {
            "src": dict((x, p.get(x)) for x in ("uid", "term", "term_uid", "term_class", "owner_class", "diagram", "wire_uid")),
            "dst": {"uid": L17, "term": nm, "diagram": F686, "owner_class": "WhileLoop", "term_class": "Terminal"}}, "nm": nm})
    for iid, old, sink in (("tun_cal", 3644, "cal cluster path"), ("tun_size", 2294, "file size"), ("tun_path", 5096, "selected path")):
        ok_ = [x for x in V.terminals(G2, node=old) if G2["rows"][x]["term_class"] == "OuterTerminal"]
        w = int(G2["rows"][ok_[0]]["wire_uid"]) if ok_ else 0
        live = sorted(set((G2["rows"][x]["node"], G2["rows"][x]["term_name"]) for x in V.wire_terminals(G2, w) if G2["rows"][x]["is_source"])) if w else []
        s1 = src_of(S1, old, "OuterTerminal")
        s.gate("P2a {0} RULE-PD166: live outer feed w{1} source {2} == S1 source of #{3} outer (uid)".format(iid, w, live, old), w and [x[0] for x in live] == [x[0] for x in s1], s1, fatal=True)
        rules.append({"id": iid, "action": "wire", "op": "connect_from_wire", "variant": "tunnel_outer", "decided_by": "RULE-PD166", "exec": {
            "src": {"uid": old, "term": "", "term_class": "InnerTerminal", "owner_class": "LoopTunnel", "diagram": 639, "wire_uid": 0, "outer_wire": w},
            "dst": {"uid": 376, "term": sink, "diagram": B17, "owner_class": "SubVI", "term_class": "Terminal"}}})
    s.fact("RULE ROWS: {0}".format([(r["id"], r["decided_by"]) for r in rules])); execute(s, rules, "rules")  # noqa: E702
    s.head("[4] ordered second pass (42(b)) on the LeftIn and init wires")
    for lab, src, u, t, dg in (("err_L", E["left"], 376, "error in", B17), ("acc_L", A["left"], 376, "total data array in", B17),
                               ("err_init", 4910, L17, rules[0]["nm"], F686), ("acc_init", 781, L17, rules[1]["nm"], F686)):
        s.expect_is_broken_false(lab, lambda src=src, u=u, t=t, dg=dg: s.cfw_second_pass(src, {"uid": u, "term": t, "diagram": dg, "owner_class": "", "term_class": ""}))
    s.junk_purge("final")
    a = dict((c, s.count(c)) for c in CLS)
    s.gate("P3 WhileLoop/Local/ControlTerminal/SubVI delta 0", all(a[c] == b[c] for c in CLS[:4]), "{0} -> {1}".format(b, a)); s.es("after all rows (RECORDED)")  # noqa: E702
    Gn = lg(s, "new"); cd = V.computation_diff(S1, Gn)  # noqa: E702
    for r in cd["rows"]:
        s.fact("CDIFF ROW {0}".format(dict((k, V.show(v) if k == "sink" else v) for k, v in r.items())))
    got, want = set((V.key_parts(r["sink"])[0], V.key_parts(r["sink"])[2]) for r in cd["rows"]), set((p["node"], p["term"]) for p in PRED["cdiff_rows"])
    s.gate("PB computation_diff(S1,new) rows == the {0} predicted".format(len(want)), got == want, {"extra": sorted(got - want), "missing": sorted(want - got)})
    d, srs = V.diff(Gb, Gn), {E["right"], E["left"], A["right"], A["left"]}
    tun, gone = set(d["nodes_added"]) - srs, set(d["nodes_removed"])
    rem, add = sorted(K.uid_edges(Gb) - K.uid_edges(Gn)), sorted(K.uid_edges(Gn) - K.uid_edges(Gb))
    s.fact("diff(bed,new) nodes_added {0} removed {1}; uid-keyed wire/fs edges removed {2} added {3}".format(d["nodes_added"], d["nodes_removed"], rem, add))
    s.gate("PC1 nodes_added == 4 new SRs + 3 new LoopTunnels; removed subset of {3644,2294,1929,5020}", srs <= set(d["nodes_added"]) and len(tun) == 3
           and all(Gn["cls"].get(u) == "LoopTunnel" for u in tun) and gone <= TUN_OK, (d["nodes_added"], d["nodes_removed"]))
    br, ba = [e for e in rem if not {e[1], e[3]} & ({376} | gone)], [e for e in add if not {e[1], e[3]} & (srs | tun)]
    s.gate("PC2 removed edges touch #376 or a removed tunnel; added ones touch a new SR/tunnel", not br and not ba, (br, ba))
    shot = lambda n: g._lv_gui("-Action", "shot", "-Out", '"{0}"'.format(os.path.join(K.BENCH, "l7_1_{0}_{1}.png".format(STAMP, n))))  # noqa: E731
    m = (shot("before_save"), s.save(broken_ok=True), shot("after_save"))[1]    # capture -> save (mtime-confirmed) -> capture
    s.gate("PS artefact saved, md5 differs from the bed; bed md5 unchanged", m and m != BED_MD5 and K.md5(BED) == BED_MD5, (m, K.md5(BED)))
    _x = m and s.scratches.remove(s.work)              # saved -> the work copy IS the artefact (discard_work undone)
    s.R["l7_1"] = {"final": s.work, "md5": m, "bytes": os.path.getsize(s.work), "sr": SR, "tunnels": sorted(tun), "cdiff_rows": len(cd["rows"])}
    s.dump()

if __name__ == "__main__":
    st = K.Stage(BED, BED_MD5, "stage_d1_l7_1", preload=False, deadline_min=42, work_name="D1_l7_1_{0}.vi".format(STAMP), pins=tuple(K.DEFAULT_PINS) + (("S3 loop15 bed", BED, BED_MD5),))
    sys.exit((K.run(body, st), K.mod("bench_prep").restart_labview())[0])
