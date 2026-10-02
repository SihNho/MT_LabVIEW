r"""diag_c136_1_routes - card 136-1 items 1-3 (brief_136.md, PD295(e)): P4's UNMEASURED routes U1 U2 U3 U5 U6 and W1's stop via Or,
on ONE never-saved byte copy of the bed (plan diag_c136_1_routes_plan.json: every uid, donor, label, position). The draft's own
donors ($work = the bed) are used, so the measurement is on the P4 draft's real shapes (Local 'Num' array, the bed's Or #10247).
PRIOR ART (reused, no new op): diag_c126_6_cross.py (cross + census + tunnel faces + RLE + Error List shape), diag_c127_5_errsel.py
(create + terminal pick + wire), stagexec LVBackend.create/stop (loop_in 'while', local_read + move_in, OpStopFromNode_v0),
stagekit.const_row (OpCreateConstOnTerm_v0), gscript.read_const_value, build_d1_v0.loop_end_ref, gscript.wire_remove_loose_ends.
PREDICTION: every create op err ''; A2/U5/U6/U1/U3/W1 wires op err '' and Is Broken? False (crossings after RLE); KMX read back;
WS cond wire == Or out wire; Error List / census / tunnels / class+value of KMX before and after t are MEASUREMENTS.
X bed md5 unchanged, byte copy deleted, LabVIEW gone.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c136_1_routes.log -- py -u tools/bench/diag_c136_1_routes.py"""
import json, os, sys, time                                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K; g = K.g                                                               # noqa: E402,E702
PL = json.load(open(os.path.join(HERE, "diag_c136_1_routes_plan.json"), encoding="utf-8"))
BED, BEDM, P, DN, N, POS, LB = PL["input"]["vi"], PL["input"]["md5"], PL["parent"], PL["donors"], PL["names"], PL["pos"], PL["labels"]
DRY, OUT = bool(getattr(g.report_all, "_dry", False)), {"creates": {}, "wires": {}}
s = K.Stage(BED, BEDM, "scratch_c136_1_routes", preload=False, deadline_min=28, reserve_s=150,
            out_json=os.path.join(HERE, "diag_c136_1_routes.json"), task="card 136-1 items 1-3")
def terms(W):
    import allterms
    return [] if DRY else allterms.read_terms(W, allterms.OP_ALLTERMS_V1)[0]
def by_class(c0, c1): return dict((c, sum(1 for u in set(c1) - set(c0) if c1[u] == c)) for c in set(c1[u] for u in set(c1) - set(c0)))
def dn(k): return {"donor": s.work if DN[k]["donor"] == "$work" else DN[k]["donor"], "uid": DN[k]["uid"]}
def create(tag, dg, prim, k):
    c0 = s.census_snapshot()
    u = s._op("create_primitive_nested", lambda: g.create_primitive_nested(s.work, dg, prim, tuple(POS[tag]), donor=dn(k) if k else None), "%s %s" % (tag, prim))["result"]
    OUT["creates"][tag] = {"uid": u, "census": by_class(c0, s.census_snapshot())}
    s.fact("CREATE %s #%s census %s" % (tag, u, OUT["creates"][tag]["census"]))
    s.gate("C %s op err '' and a node" % tag, DRY or u, u)
    return 0 if DRY else int(u or 0)
def local(tag, label, body):
    r = {"uid": 0} if DRY else (s.create_local_read(label, tag=tag)["result"] or {})   # dry: panel_wiring is not in the offline graph
    u = int(r.get("uid") or 0); s.move_in(u, s.uid_index("Diagram", body), tuple(POS[tag]))   # noqa: E702
    OUT["creates"][tag] = {"uid": u}; s.gate("C %s Local read %r moved into #%s" % (tag, label, body), DRY or u, r)   # noqa: E702
    return u
def t(rows, owner, src, name=None):
    r = [x for x in rows if int(x["owner_uid"]) == int(owner) and bool(x["is_source"]) == src and (name is None or x["term_name"] == name)]
    s.gate("T #%s %s %s: exactly one terminal" % (owner, name, "src" if src else "sink"), DRY or len({int(x["term_uid"]) for x in r}) == 1, [(x["term_uid"], x["term_name"]) for x in r][:6])
    return 0 if DRY or not r else int(r[0]["term_uid"])
def wire(tag, snk, src, rle=False):
    W = s.work; c0, w0, lt0 = s.census_snapshot(), set(g.uids(W, "Wire")), set(g.uids(W, "Tunnel"))   # noqa: E702
    cw = s._op("connect_term_uid", lambda: g.connect_term_uid(W, snk, src), "%s #%s <- #%s" % (tag, snk, src)); res = cw["result"] or {}   # noqa: E702
    o = {"op": res, "err": cw["err"], "census": by_class(c0, s.census_snapshot()), "gone_wires": sorted(w0 - set(g.uids(W, "Wire"))),
         "new_wires": sorted(set(g.uids(W, "Wire")) - w0), "new_tunnels": sorted(set(g.uids(W, "Tunnel")) - lt0)}
    if rle and not DRY:
        o["rle"] = dict((w, g.wire_remove_loose_ends(W, w)) for w in o["new_wires"] if w in g.uids(W, "Wire"))
        o["broken_after_rle"] = [w for w, r in o["rle"].items() if r.get("broken_after") or r.get("err")]
    o["es"] = None if DRY else g.exec_state(W); OUT["wires"][tag] = o                        # noqa: E702
    s.fact("WIRE %s Is Broken? %s err %r census %s gone %s new %s tunnels %s rle %s ES %s" % (tag, res.get("broken"), cw["err"], json.dumps(o["census"], sort_keys=True),
           o["gone_wires"], o["new_wires"], o["new_tunnels"], o.get("rle"), o["es"]))
    ok = res and not cw["err"] and (not o.get("broken_after_rle", []) if rle else res.get("broken") is False)
    s.gate("W %s op err '' and Is Broken? False%s" % (tag, " after RLE" if rle else ""), DRY or ok, res)
    return o
def kread(tag, u):
    r = s.safe("read_const_value #%s" % u, lambda: g.read_const_value(s.work, u), {})[0] or {}
    OUT[tag] = {k: r.get(k) for k in ("cls", "value", "type", "text", "wire", "err")}; s.fact("KMX %s %s" % (tag, OUT[tag]))   # noqa: E702
def stop(loop, body, src_node, name):
    W = s.work; d = s.uid_index("Diagram", body); n = g._node_index(W, d, src_node)          # noqa: E702
    ti = [int(r["i"]) for r in g.node_terms(W, d, n) if r["name"] == name and r["is_source"]]
    lab = json.load(open(os.path.join(HERE, "opstopfromnode_labels.json"), encoding="utf-8"))
    def _c():
        vs = g.op(os.path.join(g.CLAUDEDEV, "OpStopFromNode_v0.vi"))
        for k, v in (("vi path", W), ("Class Name", "WhileLoop"), ("index", s.uid_index("WhileLoop", loop)), (lab["index_node"], n), (lab["index_term"], ti[0])):
            vs.SetControlValue(k, v)
        g._run(vs); return g._err(vs, "error out") or ""                                     # noqa: E702
    rec = s._op("stop_from_node", _c, "WS #%s cond <- N[%s].t%s (%r)" % (loop, n, ti, name))
    le = K.mod("build_d1_v0").loop_end_ref(W, s.uid_index("WhileLoop", loop)); OUT["stop"] = {"op": rec["err"] or rec["result"], "loop_end_ref": le}   # noqa: E702
    return le
def body(_):
    s.start(); s.discard_work(); W = s.work                                                  # noqa: E702
    b0 = set(g.uids(W, "Diagram")) if not DRY else set()
    ws = s._op("loop_in", lambda: g.loop_in("while", W, s.uid_index("Diagram", P), tuple(POS["ws"])), "while on #%s" % P)["result"]
    wb = (sorted(set(g.uids(W, "Diagram")) - b0) or [0])[0] if not DRY else 0
    s.gate("A1 one While #%s with ONE new body Diagram #%s" % (ws, wb), DRY or (ws and wb), ws); ws = 0 if DRY else int(ws)   # noqa: E702
    ks, iai = create("ks", wb, "const_donor", "k_i32_0"), create("iai", P, "Index Array", "ia")
    R = terms(W); OUT["A2"] = wire("A2 IAI.index <- KS (body -> parent)", t(R, iai, False, N["ia_idx"]), t(R, ks, True))   # noqa: E702
    R = terms(W); ts = (OUT["A2"]["new_tunnels"] or [0])[0]                                  # noqa: E702
    face = [r for r in R if int(r["owner_uid"]) == ts and int(r["frame_diagram"]) == P]
    OUT["ts_faces"] = [(r["term_uid"], r["term_name"], r["is_source"], r["frame_diagram"], r["wire_uid"]) for r in R if int(r["owner_uid"]) == ts]
    s.fact("TS #%s faces %s; index_mode %s" % (ts, OUT["ts_faces"], None if DRY or not ts else g.tunnels(W, s.uid_index("LoopTunnel", ts)).get("index_mode")))
    s.gate("A2b TS #%s has ONE outer face on #%s, wired" % (ts, P), DRY or (len(face) == 1 and int(face[0]["wire_uid"] or 0)), OUT["ts_faces"])
    cp = s._op("struct_copy_nested", lambda: g.struct_copy_nested(W, P, "FlatSequence", g.fs_donor(), tuple(POS["fs"])), "FS -> #%s" % P)["result"] or {}
    f0 = 0 if DRY else int((cp.get("new_diagrams") or [0])[0]); s.gate("A3 FS #%s frame f0 #%s" % (cp.get("uid"), f0), DRY or f0, cp)   # noqa: E702
    ian, eq2 = create("ian", f0, "Index Array", "ia"), create("eq2", P, "Equal?", "eq")
    R = terms(W); wire("U5 IAN.index (FS f0) <- TS outer face", t(R, ian, False, N["ia_idx"]), 0 if DRY or not face else int(face[0]["term_uid"]), rle=True)   # noqa: E702
    R = terms(W); wire("U6 EQ2.y (#%s) <- IAN.element (FS f0 exit)" % P, t(R, eq2, False, "y"), t(R, ian, True, N["ia_el"]), rle=True)   # noqa: E702
    lrn, gt, km1, sel = local("lrn", LB["num"], wb), create("gt", wb, "Greater?", "greater"), create("km1", wb, "const_donor", "k_i32_m1"), create("sel", wb, "Select", "select")
    amm, lt, orr, lrs = create("amm", wb, "Array Max & Min", "amm"), create("lt", wb, "Less?", "less"), create("or", wb, "Or", "or"), local("lrs", LB["stop"], wb)
    kc = {"result": {}} if DRY else s.const_row({"loop_uid": ws, "body_diagram": wb, "node": sel, "term": "f", "value": PL["k_max"]}, tag="U2 KMX on Select.f")
    kmx = 0 if DRY else int(((kc.get("result") or {}).get("created_uid")) or 0)
    s.gate("U2 KMX created on Select.f before t is wired (#%s)" % kmx, DRY or (kmx and not (kc.get("result") or {}).get("err")), kc.get("result")); DRY or kread("before_t", kmx)   # noqa: E702
    R = terms(W)
    wire("U1a GT.x <- Num", t(R, gt, False, "x"), t(R, lrn, True)); wire("U1b GT.y <- I32 -1", t(R, gt, False, "y"), t(R, km1, True))   # noqa: E702
    wire("U1c Select.t <- Num (branch)", t(R, sel, False, "t"), t(R, lrn, True)); DRY or kread("after_t", kmx)   # noqa: E702
    wire("U3 Select.s <- GT out (Boolean array)", t(R, sel, False, "s"), t(R, gt, True, N["gt_out"]))
    wire("U3b AMM.array <- Select out", t(R, amm, False, N["amm_in"]), t(R, sel, True, N["sel_out"]))
    wire("U3c LT.x <- AMM.min value", t(R, lt, False, "x"), t(R, amm, True, N["amm_min"])); wire("U3d LT.y <- KMX (branch)", t(R, lt, False, "y"), t(R, kmx, True))   # noqa: E702
    wire("W1a Or.x <- LT out", t(R, orr, False, "x"), t(R, lt, True, N["lt_out"])); wire("W1b Or.y <- stop (end) Local", t(R, orr, False, "y"), t(R, lrs, True))   # noqa: E702
    le = {} if DRY else stop(ws, wb, orr, N["or_out"]); ow = 0 if DRY else [int(r["wire_uid"] or 0) for r in terms(W) if int(r["term_uid"]) == t(R, orr, True, N["or_out"])][:1]   # noqa: E702
    s.fact("W1 WS cond read-back %s; Or out wire %s" % (le, ow)); s.gate("W1c WS cond wired from the Or (cond wire == Or out wire)", DRY or (le.get("cond_wire_uid") and [le.get("cond_wire_uid")] == ow), (le, ow))   # noqa: E702
    OUT["es_end"] = None if DRY else g.exec_state(W); s.fact("ExecState end %s" % OUT["es_end"])   # noqa: E702
    if not DRY:
        EC = K.mod("errorlist_check"); EC._lv_imports(); RR = {"gui_acts_outer": [], "errors": []}; EC.open_diagram(W, RR)   # noqa: E702
        r = EC.E.read(W, os.path.join(HERE, "errorlist_c136_1_routes_%s_raw.json" % s.stamp), log=lambda m: None, on_item=None)
        base, cc = EC.class_counts(json.load(open(os.path.join(HERE, PL["errorlist_base"]), encoding="utf-8"))["items"]), EC.class_counts(r.get("items"))
        OUT["el"] = {"items": len(r.get("items") or []), "n": r.get("n_reported"), "extra": {k: cc[k] - base.get(k, 0) for k in cc if cc[k] > base.get(k, 0)},
                     "missing": {k: base[k] - cc.get(k, 0) for k in base if base[k] > cc.get(k, 0)}, "errors": (r.get("errors") or [])[:2]}
        s.fact("EL end TOTAL %s (window N %s, bed 51) extra %s missing %s errors %s" % (OUT["el"]["items"], OUT["el"]["n"], OUT["el"]["extra"], OUT["el"]["missing"], OUT["el"]["errors"]))
    s.gate("X bed md5 unchanged", K.md5(BED) == BEDM, K.md5(BED))
    if not DRY:
        json.dump({"function": "connect_term_uid", "variant": "c136-1 P4 routes U1 U2 U3 U5 U6 W1-Or", "status": "PASS" if not s.fails else "FAIL", "t": time.time(),
                   "card": "136-1", "log": "tools/bench/diag_c136_1_routes.log", "fails": s.fails, "out": OUT},
                  open(os.path.join(HERE, "scratch_verify", "gscript.connect_term_uid_c136_1_%s.json" % s.stamp), "w", encoding="utf-8"), default=str, indent=1)
    json.dump(OUT, open(os.path.join(HERE, "diag_c136_1_routes_out.json"), "w", encoding="utf-8"), default=str, indent=1)
    s.dump()
if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
