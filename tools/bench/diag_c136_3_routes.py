r"""diag_c136_3_routes - card 136-3 items 2-3 (PD299(b), PD193(a)): diag_c136_1_routes.py (136-1, md5 be8f6513, never run), SAME plan
diag_c136_1_routes_plan.json (20 rows), ops, donors, gates; whole-VI reads cut to part start/end: terminals looked up PER NODE
(node_labels of one diagram + node_terms_uids, uid echo); census only around U5/U6; parts A (WS+A2) -> B (body U1-U3 W1) -> C (FS U5 U6).
WHOLE-VI READ CALL SITES (all via rd(), each once, none in a loop): R1 Diagram D0 | R2 Diagram D1 | R3 WhileLoop | R4 Diagram D2 |
U5: R5 census, R6 census, R7 Wire | U6: R8 census, R9 census, R10 Wire  => R = 1 + 10 = 11; dry N 26 -> 687.2 MB <= 690.
HIDDEN in helpers: Stage._op.node_mark report_all('Node') per _op; const_row uid_index + address + junk_purge; local panel_wiring.
PREDICTION: every op err ''; Is Broken? False (U5/U6 after RLE); WS cond wire == Or out wire; census/EL/KMX are MEASUREMENTS.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c136_3_routes.log -- py -u tools/bench/diag_c136_3_routes.py"""
import json, os, sys, time                                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K; g = K.g                                                               # noqa: E402,E702
PL = json.load(open(os.path.join(HERE, "diag_c136_1_routes_plan.json"), encoding="utf-8"))
BED, BEDM, P, DN, N, POS, LB = PL["input"]["vi"], PL["input"]["md5"], PL["parent"], PL["donors"], PL["names"], PL["pos"], PL["labels"]
DRY, OUT = bool(getattr(g.report_all, "_dry", False)), {"creates": {}, "wires": {}, "reads": []}
s = K.Stage(BED, BEDM, "scratch_c136_3_routes", preload=False, deadline_min=28, reserve_s=150,
            out_json=os.path.join(HERE, "diag_c136_3_routes.json"), task="card 136-3 items 2-3")
def rd(tag, cls):                                                                           # the ONLY whole-VI read helper
    OUT["reads"].append(tag); rows = [] if DRY else g.report_all(s.work, cls)               # noqa: E702
    return dict((int(r["uid"]), i) for i, r in enumerate(rows)) if cls != "GObject" else dict((int(r["uid"]), str(r["class"])) for r in rows)
def delta(c0, c1):
    new, gone = set(c1) - set(c0), set(c0) - set(c1)
    return {"new": dict((c, sum(1 for u in new if c1[u] == c)) for c in set(c1[u] for u in new)), "gone": sorted(gone),
            "new_wires": sorted(u for u in new if c1[u] == "Wire"), "new_tunnels": sorted(u for u in new if "Tunnel" in c1[u])}
def nt(di, uid, src, name=None):                                                            # PER NODE terminal lookup
    if DRY:
        return 0
    echo, rows = g.node_terms_uids(s.work, di, g._node_index(s.work, di, uid))
    r = [x for x in rows if bool(x["is_source"]) == src and (name is None or x["name"] == name)]
    s.gate("T #%s %s %s: node echo + exactly one terminal" % (uid, name, "src" if src else "sink"), echo == int(uid) and len(r) == 1, [(x["uid"], x["name"], x["wire"]) for x in r][:6])
    return int(r[0]["uid"]) if len(r) == 1 else 0
def create(tag, dg, prim, k):
    u = s._op("create_primitive_nested", lambda: g.create_primitive_nested(s.work, dg, prim, tuple(POS[tag]), donor=dn(k) if k else None), "%s %s" % (tag, prim))["result"]
    OUT["creates"][tag] = {"uid": u}; s.gate("C %s op err '' and a node" % tag, DRY or u, u)  # noqa: E702
    return 0 if DRY else int(u or 0)
def dn(k): return {"donor": s.work if DN[k]["donor"] == "$work" else DN[k]["donor"], "uid": DN[k]["uid"]}
def local(tag, label, body, bidx):
    r = {"uid": 0} if DRY else (s.create_local_read(label, tag=tag)["result"] or {})
    u = int(r.get("uid") or 0); s.move_in(u, bidx, tuple(POS[tag]))                          # noqa: E702
    OUT["creates"][tag] = {"uid": u}; s.gate("C %s Local read %r moved into #%s" % (tag, label, body), DRY or u, r)   # noqa: E702
    return u
def wire(tag, snk, src, rle=False):
    W = s.work; c0 = rd("census before " + tag, "GObject") if rle else None                  # noqa: E702
    cw = s._op("connect_term_uid", lambda: g.connect_term_uid(W, snk, src), "%s #%s <- #%s" % (tag, snk, src)); res = cw["result"] or {}   # noqa: E702
    o = {"op": res, "err": cw["err"]}
    if rle and not DRY:
        o.update(delta(c0, rd("census after " + tag, "GObject"))); wi = rd("Wire index " + tag, "Wire")   # noqa: E702
        o["rle"] = dict((w, g.wire_remove_loose_ends(W, w, index=wi[w])) for w in o["new_wires"] if w in wi)
        o["broken_after_rle"] = [w for w, r in o["rle"].items() if r.get("broken_after") or r.get("err")]
    o["es"] = None if DRY else g.exec_state(W); OUT["wires"][tag] = o                        # noqa: E702
    s.fact("WIRE %s Is Broken? %s err %r delta %s rle %s ES %s" % (tag, res.get("broken"), cw["err"], json.dumps({k: o.get(k) for k in ("new", "gone", "new_wires", "new_tunnels")}, sort_keys=True), o.get("rle"), o["es"]))
    ok = res and not cw["err"] and (not o.get("broken_after_rle", []) if rle else res.get("broken") is False)
    s.gate("W %s op err '' and Is Broken? False%s" % (tag, " after RLE" if rle else ""), DRY or ok, res)
    return o
def kread(tag, u):
    r = s.safe("read_const_value #%s" % u, lambda: g.read_const_value(s.work, u), {})[0] or {}; OUT[tag] = {k: r.get(k) for k in ("cls", "value", "type", "text", "wire", "err")}; s.fact("KMX %s %s" % (tag, OUT[tag]))   # noqa: E702
def face(pidx, ws):                                                                         # WS's own Terminals[] on #P
    rows = [] if DRY else g.node_terms_uids(s.work, pidx, g._node_index(s.work, pidx, ws))[1]
    return [(r["uid"], r["name"], r["is_source"], r["wire"]) for r in rows]
def body(_):
    s.start(); s.discard_work(); W = s.work                                                  # noqa: E702
    D0 = rd("A start Diagram", "Diagram")                                                    # ---- part A: WS + A2
    ws = s._op("loop_in", lambda: g.loop_in("while", W, D0.get(P, 0), tuple(POS["ws"])), "while on #%s" % P)["result"]
    D1 = rd("A after loop_in Diagram", "Diagram"); wb = (sorted(set(D1) - set(D0)) or [0])[0]   # noqa: E702
    s.gate("A1 one While #%s with ONE new body Diagram #%s" % (ws, wb), DRY or (ws and len(set(D1) - set(D0)) == 1), ws); ws = 0 if DRY else int(ws); pi, bi = D1.get(P, 0), D1.get(wb, 0)   # noqa: E702
    ks, iai = create("ks", wb, "const_donor", "k_i32_0"), create("iai", P, "Index Array", "ia")
    OUT["A2"] = wire("A2 IAI.index <- KS (body -> parent)", nt(pi, iai, False, N["ia_idx"]), nt(bi, ks, True))
    f = face(pi, ws); out = [x for x in f if x[2] and int(x[3] or 0)]; OUT["ws_faces_after_A2"] = f   # noqa: E702
    s.fact("WS #%s Terminals[] after A2 %s" % (ws, f)); s.gate("A2b WS has ONE wired source face (TS outer face) on #%s" % P, DRY or len(out) == 1, f)   # noqa: E702
    lrn, gt, km1, sel = local("lrn", LB["num"], wb, bi), create("gt", wb, "Greater?", "greater"), create("km1", wb, "const_donor", "k_i32_m1"), create("sel", wb, "Select", "select")   # B
    amm, lt, orr, lrs = create("amm", wb, "Array Max & Min", "amm"), create("lt", wb, "Less?", "less"), create("or", wb, "Or", "or"), local("lrs", LB["stop"], wb, bi)
    kc = {"result": {}} if DRY else s.const_row({"loop_uid": ws, "body_diagram": wb, "node": sel, "term": "f", "value": PL["k_max"]}, tag="U2 KMX on Select.f")
    kmx = 0 if DRY else int(((kc.get("result") or {}).get("created_uid")) or 0)
    s.gate("U2 KMX created on Select.f before t is wired (#%s)" % kmx, DRY or (kmx and not (kc.get("result") or {}).get("err")), kc.get("result")); DRY or kread("before_t", kmx)   # noqa: E702
    wire("U1a GT.x <- Num", nt(bi, gt, False, "x"), nt(bi, lrn, True)); wire("U1b GT.y <- I32 -1", nt(bi, gt, False, "y"), nt(bi, km1, True))   # noqa: E702
    wire("U1c Select.t <- Num (branch)", nt(bi, sel, False, "t"), nt(bi, lrn, True)); DRY or kread("after_t", kmx)   # noqa: E702
    wire("U3 Select.s <- GT out (Boolean array)", nt(bi, sel, False, "s"), nt(bi, gt, True, N["gt_out"]))
    wire("U3b AMM.array <- Select out", nt(bi, amm, False, N["amm_in"]), nt(bi, sel, True, N["sel_out"]))
    wire("U3c LT.x <- AMM.min value", nt(bi, lt, False, "x"), nt(bi, amm, True, N["amm_min"])); wire("U3d LT.y <- KMX (branch)", nt(bi, lt, False, "y"), nt(bi, kmx, True))   # noqa: E702
    wire("W1a Or.x <- LT out", nt(bi, orr, False, "x"), nt(bi, lt, True, N["lt_out"])); wire("W1b Or.y <- stop (end) Local", nt(bi, orr, False, "y"), nt(bi, lrs, True))   # noqa: E702
    WL = rd("B end WhileLoop", "WhileLoop")
    if not DRY:
        n = g._node_index(W, bi, orr); ti = [int(r["i"]) for r in g.node_terms(W, bi, n) if r["name"] == N["or_out"] and r["is_source"]]   # noqa: E702
        lab = json.load(open(os.path.join(HERE, "opstopfromnode_labels.json"), encoding="utf-8"))
        def _c():
            vs = g.op(os.path.join(g.CLAUDEDEV, "OpStopFromNode_v0.vi"))
            for k, v in (("vi path", W), ("Class Name", "WhileLoop"), ("index", WL[ws]), (lab["index_node"], n), (lab["index_term"], ti[0])):
                vs.SetControlValue(k, v)
            g._run(vs); return g._err(vs, "error out") or ""                                 # noqa: E702
        rec = s._op("stop_from_node", _c, "WS #%s cond <- N[%s].t%s" % (ws, n, ti))
        le = K.mod("build_d1_v0").loop_end_ref(W, WL[ws]); ow = [x["wire"] for x in g.node_terms(W, bi, n) if x["name"] == N["or_out"] and x["is_source"]]   # noqa: E702
        OUT["stop"] = {"op": rec["err"] or rec["result"], "loop_end_ref": le, "or_out_wire": ow}
        s.fact("W1 WS cond read-back %s; Or out wire %s" % (le, ow)); s.gate("W1c WS cond wired from the Or (cond wire == Or out wire)", le.get("cond_wire_uid") and [le.get("cond_wire_uid")] == ow, (le, ow))   # noqa: E702
    cp = s._op("struct_copy_nested", lambda: g.struct_copy_nested(W, P, "FlatSequence", g.fs_donor(), tuple(POS["fs"])), "FS -> #%s" % P)["result"] or {}   # ---- part C
    f0 = 0 if DRY else int((cp.get("new_diagrams") or [0])[0]); s.gate("A3 FS #%s frame f0 #%s" % (cp.get("uid"), f0), DRY or f0, cp)   # noqa: E702
    D2 = rd("C start Diagram", "Diagram"); pi, fi = D2.get(P, 0), D2.get(f0, 0)              # noqa: E702
    ian, eq2 = create("ian", f0, "Index Array", "ia"), create("eq2", P, "Equal?", "eq")
    tsf = 0 if DRY else int(([x for x in face(pi, ws) if x[2] and int(x[3] or 0)] or [(0,)])[0][0])
    OUT["U5"] = wire("U5 IAN.index (FS f0) <- TS outer face", nt(fi, ian, False, N["ia_idx"]), tsf, rle=True)
    OUT["ws_faces_after_U5"] = face(pi, ws); s.fact("WS #%s Terminals[] after U5 %s (before A2-read %s)" % (ws, OUT["ws_faces_after_U5"], OUT.get("ws_faces_after_A2")))   # noqa: E702
    OUT["U6"] = wire("U6 EQ2.y (#%s) <- IAN.element (FS f0 exit)" % P, nt(pi, eq2, False, "y"), nt(fi, ian, True, N["ia_el"]), rle=True)
    OUT["es_end"] = None if DRY else g.exec_state(W); s.fact("ExecState end %s; whole-VI reads %d %s" % (OUT["es_end"], len(OUT["reads"]), OUT["reads"]))   # noqa: E702
    if not DRY:
        EC = K.mod("errorlist_check"); EC._lv_imports(); RR = {"gui_acts_outer": [], "errors": []}; EC.open_diagram(W, RR)   # noqa: E702
        r = EC.E.read(W, os.path.join(HERE, "errorlist_c136_3_routes_%s_raw.json" % s.stamp), log=lambda m: None, on_item=None)
        base, cc = EC.class_counts(json.load(open(os.path.join(HERE, PL["errorlist_base"]), encoding="utf-8"))["items"]), EC.class_counts(r.get("items"))
        OUT["el"] = {"items": len(r.get("items") or []), "n": r.get("n_reported"), "extra": {k: cc[k] - base.get(k, 0) for k in cc if cc[k] > base.get(k, 0)},
                     "missing": {k: base[k] - cc.get(k, 0) for k in base if base[k] > cc.get(k, 0)}, "errors": (r.get("errors") or [])[:2]}
        s.fact("EL end TOTAL %s (window N %s, bed 51) extra %s missing %s errors %s" % (OUT["el"]["items"], OUT["el"]["n"], OUT["el"]["extra"], OUT["el"]["missing"], OUT["el"]["errors"]))
    s.gate("X bed md5 unchanged", K.md5(BED) == BEDM, K.md5(BED))
    if not DRY:
        json.dump({"function": "connect_term_uid", "variant": "c136-3 P4 routes U1 U2 U3 U5 U6 W1-Or (reads PD193(a))", "status": "PASS" if not s.fails else "FAIL",
                   "t": time.time(), "card": "136-3", "log": "tools/bench/diag_c136_3_routes.log", "fails": s.fails, "out": OUT},
                  open(os.path.join(HERE, "scratch_verify", "gscript.connect_term_uid_c136_3_%s.json" % s.stamp), "w", encoding="utf-8"), default=str, indent=1)
    json.dump(OUT, open(os.path.join(HERE, "diag_c136_3_routes_out.json"), "w", encoding="utf-8"), default=str, indent=1)
    s.dump()
if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
