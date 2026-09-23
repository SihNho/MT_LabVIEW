r"""stage_d1_l7_1b - cycle 71 L7-1b (split plan PD 165/166/168-171). INPUT = the SAVED L7-1a file (tools/bench/stage_d1_l7_1a.json), FRESH
LabVIEW. 9 rows: 4 S1-MAPPED body rows (PD168: wired iff Jev TOP == mapped pair, else STOP), 2 SR-init RULE rows (PD165; Jev logged, STOP if
p<0.30), 3 tunnel RULE rows (PD166, no Jev). Corrected intent lines (PD171(1)). PB computation_diff FATAL before save (PD170(c)). PD172: the 3
L7-R edges are BASELINE (gate PC3). PD173: second pass by TERMINAL UID (stagekit.address/match_term_uid). PRIOR ART: stage_d1_l7_1.py copied; changed: input, SRs read not created, lines, modes, PB fatal. CONTRACT: l7_1b_predict.log.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/stage_d1_l7_1b.log -- py -u tools/recipes/stage_d1_l7_1b.py"""
import copy, json, os, sys, time                                                   # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, vigraph as V, jev_candidates as JC, jev_pairs as JP  # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
A1 = J(K.BENCH, "stage_d1_l7_1a.json")["l7_1a"]
BED, BED_MD5, SR = A1["final"], A1["md5"], A1["sr"]
S3, S3_MD5, STAMP = os.path.join(K.CLAUDEDEV, "D1_s3_loop15.vi"), "1a11d92aacabf7ec844d65b8af19f39f", time.strftime("%Y%m%d_%H%M%S")
PRED, LOOPS = J(K.BENCH, "l7_1_prediction.json"), J(K.BENCH, "graph_loops_m4b_20260924.json")["loops"]
WIKI = J(K.ROOT, "docs", "wiki", "subvi", JC.BED_KEY + ".json")
L17, B17, F686, TUN_OK = 23041, 23405, 686, {3644, 2294, 1929, 5020}
BASE = {("wire", 1929, 2043, 2048, 3182), ("wire", 1929, 2043, 6384, 6480), ("wire", 5020, 5050, 6384, 6511)}  # PD172: L7-R rows, baseline-absent
CLS = ("WhileLoop", "Local", "ControlTerminal", "SubVI", "LoopTunnel", "Wire")
WHO = {"err": "the error chain (save trace.vi #376 'error out' -> 'error in')", "acc": "save trace.vi #376's output 'total data array out'"}

def lg(s, tag):
    loops = copy.deepcopy(LOOPS)
    for L in (x for x in loops if x["loop_uid"] == L17):
        L["right_uids"], L["left_of"] = max((v["rights"] for v in SR.values()), key=len), dict((str(v["right"]), [v["left"]]) for v in SR.values())
    lv = K.mod("wiki_build").read_live(s.work, fs_pairs=WIKI["fs_tunnel_pairs"])
    s.fact("LIVE MAP [{0}] {1}".format(tag, lv["secs"]))
    return JC.from_parts({"terminals": lv["terminals"], "graph_summary": WIKI["graph_summary"]}, lv["objs"], loops, JC.node_labels_default(), lv["fs_tunnel_pairs"], tag)

def src_of(G, node, tc):
    return sorted(set((V.key_parts(a)[0], G["rows"][a]["term_name"]) for k, a, b, _i in G["edges"] if k == "wire" and V.key_parts(b)[0] == node and G["rows"][b]["term_class"] == tc))
def nm(G, u, tc, src, f="term_name"):
    return ([G["rows"][x][f] for x in V.terminals(G, node=u, is_source=src) if G["rows"][x]["term_class"] == tc] or ["<no such terminal>"])[0]
def execute(s, decs, tag):
    _p, rec = JP.write_record("l7_1b_" + tag, BED_MD5, [d.get("line", d["id"]) for d in decs], [], decs, time.time())
    bad = [(r["id"], r.get("error"), r.get("failed_layer")) for r in s.from_decision(rec, "l7_1b_" + tag) if r.get("error") or r.get("failed_layer")]
    s.gate("P2b {0}: every row executed without an error".format(tag), not bad, bad, fatal=True)

def body(s):
    print(__doc__, flush=True); s.start(); s.discard_work()                        # noqa: E702
    S1, B = JC.load(JC.S1_KEY), K.mod("build_d1_v0")
    s.fact("INPUT L7-1a {0} md5 {1}; SR {2}; HANDLES after open {3!r}".format(BED, BED_MD5, SR, K.mod("bench_prep").labview_handles())); s.es("P0 on open")  # noqa: E702
    o = B.owner_of(s.work, 376); s.gate("P0 #376 owned by #23405", o[1] == B17, o, fatal=True)  # noqa: E702
    E, A, decs = SR["err"], SR["acc"], []
    b, G1 = dict((c, s.count(c)) for c in CLS), lg(s, "L7-1a")                   # PD173: sink terminal uids recorded BEFORE wiring
    TU = dict((x, [int(G1["rows"][y]["term_uid"]) for y in V.terminals(G1, node=376, is_source=False) if G1["rows"][y]["term_name"] == n]) for x, n in (("err_L", "error in"), ("acc_L", "total data array in")))
    for iid, k, it, want in (("err_R", "err", {"src": 376, "dst": E["right"]}, (376, "error out", E["right"])),
                             ("err_L", "err", {"src": E["left"], "dst": 376}, (E["left"], None, 376, "error in")),
                             ("acc_R", "acc", {"src": 376, "dst": A["right"]}, (376, "total data array out", A["right"])),
                             ("acc_L", "acc", {"src": A["left"], "dst": 376}, (A["left"], None, 376, "total data array in"))):
        if iid.endswith("_R"):
            line = ("save trace.vi #376 output {0!r} feeds the NEW {1} RIGHT shift register #{2} of loop 1.7 (WhileLoop #23041) through its INNER terminal, "
                    "which reads {3!r} on the live object; the register carries {4}.").format(want[1], "error-chain" if k == "err" else "accumulator", want[2], nm(G1, want[2], "InnerTerminal", False), WHO[k])
            mapped = lambda r, w=want: (r["src_uid"], r["src_term"], r["dst_uid"]) == w  # noqa: E731
        else:
            line = ("the NEW {0} LEFT shift register #{1} of loop 1.7 (WhileLoop #23041), INNER terminal reading {2!r} on the live object, carries {3} "
                    "and feeds save trace.vi #376 input {4!r}.").format("error-chain" if k == "err" else "accumulator", want[0], nm(G1, want[0], "InnerTerminal", True), WHO[k], want[3])
            mapped = lambda r, w=want: (r["src_uid"], r["dst_uid"], r["dst_term"]) == (w[0], w[2], w[3])  # noqa: E731
        c = JC.candidates(G1, it)
        d = dict(JP.decide(line, c, by_rule=True, risk_gates=False), id=iid, line=line)
        top_ok = mapped(d["row_key"])
        s.fact("ROWMODE {0} RULE-S1-MAPPED cands={1} p={2} margin={3} top==mapped {4} jev_action={5} line={6!r}".format(iid, len(c["pairs"]), d["pair_p"], d["evidence"].get("margin"), top_ok, d["action"], line))
        s.gate("P2a {0} Jev top candidate == the S1-mapped pair".format(iid), top_ok, d["row_key"], fatal=True)
        d.update(action="wire", decided_by="RULE-S1-MAPPED")
        d.get("exec", {})["sr"] = {"loop_uid": L17, "loop_class": "WhileLoop", "right_uid": SR[k]["right"], "right_uids": A["rights"]}
        decs.append(d)
    execute(s, decs, "body")
    G2, rules = lg(s, "after body rows"), []                                       # RULE rows: SR init (PD165) + tunnels (PD166)
    for iid, src, k, old in (("err_init", 4910, "err", 1108), ("acc_init", 781, "acc", 51)):
        c = JC.candidates(G2, {"src": {"nodes": [src]}, "dst": SR[k]["left"]})
        p = c["pairs"][0]["src"] if len(c["pairs"]) == 1 else {}
        ok = len(c["pairs"]) == 1 and [(p["uid"], p["term"])] == src_of(S1, old, "OuterTerminal")
        s.gate("P2a {0} RULE-SINGLE-CANDIDATE: 1 legal pair and source == S1 source of #{1} outer".format(iid, old), ok, (len(c["pairs"]), p.get("uid"), p.get("term"), src_of(S1, old, "OuterTerminal")), fatal=True)
        n_, TU[iid] = nm(G2, SR[k]["left"], "OuterTerminal", False), [int(nm(G2, SR[k]["left"], "OuterTerminal", False, "term_uid"))]
        line = ("{0} #{1} output {2!r} - the value that initialises the ORIGINAL register #{3} - initialises the NEW {4} LEFT shift register #{5} of loop 1.7 "
                "(WhileLoop #23041) through its OUTER terminal. That register carries {6}, so its outer terminal now reads {7!r}.").format(
                    "the error-cluster constant" if k == "err" else "Initialize Array", src, p["term"], old, "error-chain" if k == "err" else "accumulator", SR[k]["left"], WHO[k], n_)
        pj, sp, _e = JP.ask_pair(line, c["pairs"][0])
        s.fact("ROWMODE {0} RULE-SINGLE-CANDIDATE jev_p={1} spread={2} line={3!r}".format(iid, pj, (sp or {}).get("spread"), line))
        s.gate("P2a {0} Jev logged check p >= 0.30 (PD171(3))".format(iid), pj is not None and pj >= 0.30, pj, fatal=True)
        rules.append({"id": iid, "action": "wire", "op": "connect_from_wire", "variant": None, "decided_by": "RULE-SINGLE-CANDIDATE", "exec": {
            "src": dict((x, p.get(x)) for x in ("uid", "term", "term_uid", "term_class", "owner_class", "diagram", "wire_uid")),
            "dst": {"uid": L17, "term": n_, "diagram": F686, "owner_class": "WhileLoop", "term_class": "Terminal"}}, "nm": n_})
    for iid, old, sink in (("tun_cal", 3644, "cal cluster path"), ("tun_size", 2294, "file size"), ("tun_path", 5096, "selected path")):
        ok_ = [x for x in V.terminals(G2, node=old) if G2["rows"][x]["term_class"] == "OuterTerminal"]
        w = int(G2["rows"][ok_[0]]["wire_uid"]) if ok_ else 0
        live = sorted(set((G2["rows"][x]["node"], G2["rows"][x]["term_name"]) for x in V.wire_terminals(G2, w) if G2["rows"][x]["is_source"])) if w else []
        s1 = src_of(S1, old, "OuterTerminal")
        s.fact("ROWMODE {0} RULE-PD166 outer w{1} live {2} S1 {3}".format(iid, w, live, s1))
        s.gate("P2a {0} RULE-PD166: live outer feed source == S1 source of #{1} outer (uid)".format(iid, old), w and [x[0] for x in live] == [x[0] for x in s1], s1, fatal=True)
        rules.append({"id": iid, "action": "wire", "op": "connect_from_wire", "variant": "tunnel_outer", "decided_by": "RULE-PD166", "exec": {
            "src": {"uid": old, "term": "", "term_class": "InnerTerminal", "owner_class": "LoopTunnel", "diagram": 639, "wire_uid": 0, "outer_wire": w},
            "dst": {"uid": 376, "term": sink, "diagram": B17, "owner_class": "SubVI", "term_class": "Terminal"}}})
    s.gate("P2c sink terminal uids recorded at first resolution, exactly one per row (PD173)", all(len(v) == 1 for v in TU.values()), TU, fatal=True)
    execute(s, rules, "rules")
    for lab, src, u, t, dg in (("err_L", E["left"], 376, "error in", B17), ("acc_L", A["left"], 376, "total data array in", B17),
                               ("err_init", 4910, L17, rules[0]["nm"], F686), ("acc_init", 781, L17, rules[1]["nm"], F686)):
        s.expect_is_broken_false(lab, lambda src=src, u=u, t=t, dg=dg, tu=TU[lab][0]: s.cfw_second_pass(src, {"uid": u, "term": t, "term_uid": tu, "diagram": dg, "owner_class": "", "term_class": ""}))
    s.junk_purge("final"); a = dict((c, s.count(c)) for c in CLS)  # noqa: E702
    s.gate("P3 WhileLoop/Local/ControlTerminal/SubVI delta 0", all(a[c] == b[c] for c in CLS[:4]), "{0} -> {1}".format(b, a)); s.es("after all rows (warm, RECORDED)")  # noqa: E702
    Gn = lg(s, "new"); cd = V.computation_diff(S1, Gn)  # noqa: E702
    for r in cd["rows"]:
        s.fact("CDIFF ROW {0}".format(dict((k, V.show(v) if k == "sink" else v) for k, v in r.items())))
    got, want = set((V.key_parts(r["sink"])[0], V.key_parts(r["sink"])[2]) for r in cd["rows"]), set((p["node"], p["term"]) for p in PRED["cdiff_rows"])
    s.gate("PB computation_diff(S1,new) rows == the {0} predicted (FATAL, before save)".format(len(want)), got == want, {"extra": sorted(got - want), "missing": sorted(want - got)}, fatal=True)
    d, srs, E1, En = V.diff(G1, Gn), set(u for v in SR.values() for u in (v["right"], v["left"])), K.uid_edges(G1), K.uid_edges(Gn)
    tun, gone, rem, add = set(d["nodes_added"]), set(d["nodes_removed"]), sorted(E1 - En), sorted(En - E1)
    s.fact("diff(L7-1a,new) nodes_added {0} removed {1}; uid edges removed {2} added {3}".format(sorted(tun), sorted(gone), rem, add))
    s.gate("PC1 nodes_added == 3 new LoopTunnels; removed subset of {3644,2294,1929,5020}", len(tun) == 3 and all(Gn["cls"].get(u) == "LoopTunnel" for u in tun) and gone <= TUN_OK, (sorted(tun), sorted(gone)))
    br, ba = [e for e in rem if not {e[1], e[3]} & gone], [e for e in add if not {e[1], e[3]} & (srs | tun | {376})]
    s.gate("PC2 removed edges touch a removed tunnel; added ones touch a new SR/tunnel/#376", not br and not ba, (br, ba))
    s.gate("PC3 PD172 BASELINE: the 3 L7-R edges #1929/#5020 -> #2048/#6384 absent in L7-1a AND in new", not (BASE & (E1 | En)), sorted(BASE & (E1 | En)))
    shot = lambda n: g._lv_gui("-Action", "shot", "-Out", '"{0}"'.format(os.path.join(K.BENCH, "l7_1b_{0}_{1}.png".format(STAMP, n))))  # noqa: E731
    m = (shot("before_save"), s.save(broken_ok=True), shot("after_save"))[1]
    s.gate("PS artefact saved, md5 differs from input; input + S3 bed md5 unchanged", m and m != BED_MD5 and K.md5(BED) == BED_MD5 and K.md5(S3) == S3_MD5, (m, K.md5(BED), K.md5(S3)))
    _x = m and m != BED_MD5 and s.scratches.remove(s.work); s.R["l7_1b"] = {"final": s.work, "md5": m, "bytes": os.path.getsize(s.work) if os.path.exists(s.work) else None, "tunnels": sorted(tun), "cdiff_rows": len(cd["rows"])}
    s.dump()
if __name__ == "__main__":
    st = K.Stage(BED, BED_MD5, "stage_d1_l7_1b", preload=False, deadline_min=42, work_name="D1_l7_1_{0}.vi".format(STAMP),
                 pins=tuple(K.DEFAULT_PINS) + (("S3 loop15 bed", S3, S3_MD5), ("L7-1a file", BED, BED_MD5)))
    sys.exit((K.run(body, st), K.mod("bench_prep").restart_labview())[0])
