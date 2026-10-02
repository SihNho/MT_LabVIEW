r"""diag_c137_5_routes - card 137-5 (PD307(a)): diag_c137_1_routes.py (a8fe5ea5) with body CONSTANTS ks/km1/kmx found by allterms.read_terms:68
(OP_ALLTERMS_V1 :43) by OWNER UID as diag_c137_3_lookup.py:50-52 (a new-body const is not in Diagram.Nodes[], diag_c137_3_lookup.log:36-39); all
other lookups = 137-1's ni(). ONE read_terms after all three consts exist => A2 moved after the B creates + U2; locals go to the D1 body index.
WHOLE-VI READ SITES (rd()/kterms(), each once, none in a loop): R1 Diagram D0 | R2 Diagram D1 | R3 read_terms consts | R4 WhileLoop | R5 Diagram
D2 | U5: R6 R7 census R8 Wire | U6: R9 R10 census R11 Wire => R = 1 (k 0) + 11 = 12; N 26 -> 606.1+12*2.53+26*1.38+17.4 = 689.7 MB <= 690.
HIDDEN (not in R, as 137-1): node_mark per _op; const_row uid_index+address+junk_purge; local panel_wiring; ni node_labels; kread report_all/class.
PREDICTION: every op err ''; Is Broken? False (U5/U6 after RLE); WS cond wire == Or out wire; ni lookups 22 dry / 26 real, const 3.
py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c137_5_routes.log -- py -u tools/bench/diag_c137_5_routes.py"""
import json, os, sys, time                                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes")); import stagekit as K; g = K.g   # noqa: E402,E702
PL = json.load(open(os.path.join(HERE, "diag_c136_1_routes_plan.json"), encoding="utf-8"))
BED, BEDM, P, DN, N, POS, LB = PL["input"]["vi"], PL["input"]["md5"], PL["parent"], PL["donors"], PL["names"], PL["pos"], PL["labels"]
DRY, OUT, AT = bool(getattr(g.report_all, "_dry", False)), {"creates": {}, "wires": {}, "reads": [], "lookups": [], "klookups": [], "moved": []}, K.mod("allterms")
FIX, WIRE, OK, ND, KT = {}, {}, {}, {"n": 0}, {}                # stale Diagram index -> found index; terminal uid -> wire; route ok; const uid -> read_terms rows
s = K.Stage(BED, BEDM, "scratch_c137_5_routes", preload=False, deadline_min=28, reserve_s=150, out_json=os.path.join(HERE, "diag_c137_5_routes.json"), task="card 137-5 items 1-4")
def rd(tag, cls):                                                                           # whole-VI read helper (report_all)
    OUT["reads"].append(tag); rows = [] if DRY else g.report_all(s.work, cls)               # noqa: E702
    if cls == "Diagram": ND["n"] = len(rows); FIX.clear()                                   # noqa: E701,E702
    return dict((int(r["uid"]), i) for i, r in enumerate(rows)) if cls != "GObject" else dict((int(r["uid"]), str(r["class"])) for r in rows)
def kterms(owners):                                                                         # the ONE read_terms: body-constant rows by owner uid
    rows = AT.read_terms(s.work, op=AT.OP_ALLTERMS_V1)[0]; OUT["reads"].append("read_terms consts"); [KT.setdefault(int(x["owner_uid"]), []).append(x) for x in ([] if DRY else rows) if int(x["owner_uid"]) in owners]   # noqa: E702
def kt(uid):                                                                                # const SOURCE terminal from the read_terms snapshot
    OUT["klookups"].append(int(uid or 0)); r = [x for x in KT.get(int(uid or 0), []) if x["is_source"]]   # noqa: E702
    if DRY: return 0                                                                        # noqa: E701
    s.gate("K #%s: read_terms owner rows + exactly one source terminal" % uid, len(r) == 1, [(x["term_uid"], x["term_name"], x["wire_uid"], x.get("frame_diagram")) for x in r][:4])
    WIRE.update((int(x["term_uid"]), int(x["wire_uid"] or 0)) for x in r); return int(r[0]["term_uid"]) if len(r) == 1 else 0   # noqa: E702
def ni(di, uid):                                                                            # (diagram index, node index) of #uid, MEASURED
    OUT["lookups"].append(int(uid or 0)); d0 = FIX.get(di, di)                              # noqa: E702
    if DRY: return di, 0                                                                    # noqa: E701
    for d in [d0] + sorted((j for j in range(ND["n"]) if j != d0), key=lambda j: abs(j - d0)):
        order = [int(r["uid"]) for r in (s.safe("node_labels D[%s]" % d, lambda: g.node_labels(s.work, d), [])[0] or [])]
        if int(uid) in order and d != d0: FIX[di] = d; OUT["moved"].append((int(uid), di, d0, d)); s.fact("LOOKUP #%s: Diagram[%s] miss, found on Diagram[%s] (cached %s)" % (uid, d0, d, di))   # noqa: E701,E702
        if int(uid) in order: return d, order.index(int(uid))                               # noqa: E701
    raise ValueError("#%s on no Diagram[0..%s] (cached %s)" % (uid, ND["n"] - 1, di))
def delta(c0, c1): new, gone = set(c1) - set(c0), set(c0) - set(c1); return {"new": dict((c, sum(1 for u in new if c1[u] == c)) for c in set(c1[u] for u in new)), "gone": sorted(gone), "new_wires": sorted(u for u in new if c1[u] == "Wire"), "new_tunnels": sorted(u for u in new if "Tunnel" in c1[u])}   # noqa: E702
def nt(di, uid, src, name=None):                                                            # PER NODE terminal lookup (non-constants)
    d, n = ni(di, uid)
    if DRY: return 0                                                                        # noqa: E701
    echo, rows = g.node_terms_uids(s.work, d, n); r = [x for x in rows if bool(x["is_source"]) == src and (name is None or x["name"] == name)]
    s.gate("T #%s %s %s: node echo + exactly one terminal" % (uid, name, "src" if src else "sink"), echo == int(uid) and len(r) == 1, [(x["uid"], x["name"], x["wire"]) for x in r][:6])
    WIRE.update((int(x["uid"]), int(x["wire"] or 0)) for x in r); return int(r[0]["uid"]) if len(r) == 1 else 0   # noqa: E702
def create(tag, dg, prim, k): u = s._op("create_primitive_nested", lambda: g.create_primitive_nested(s.work, dg, prim, tuple(POS[tag]), donor=dn(k) if k else None), "%s %s" % (tag, prim))["result"]; OUT["creates"][tag] = {"uid": u}; s.gate("C %s op err '' and a node" % tag, DRY or u, u); return 0 if DRY else int(u or 0)   # noqa: E702
def dn(k): return {"donor": s.work if DN[k]["donor"] == "$work" else DN[k]["donor"], "uid": DN[k]["uid"]}
def local(tag, label, body, dest): r = {"uid": 0} if DRY else (s.create_local_read(label, tag=tag)["result"] or {}); u = int(r.get("uid") or 0); s.move_in(u, dest, tuple(POS[tag])); OUT["creates"][tag] = {"uid": u}; s.gate("C %s Local read %r moved into #%s (found on Diagram[%s])" % (tag, label, body, dest), DRY or (u and ni(dest, u)[0] == dest), r); return u   # noqa: E702
def wire(tag, snk, src, rle=False):
    W, k = s.work, tag.split()[0]; c0 = rd("census before " + k, "GObject") if rle else None    # noqa: E702
    cw = s._op("connect_term_uid", lambda: g.connect_term_uid(W, snk, src), "%s #%s <- #%s" % (tag, snk, src)); res = cw["result"] or {}   # noqa: E702
    o = {"op": res, "err": cw["err"], "src_wire_before": WIRE.get(src)}
    if rle and not DRY:
        o.update(delta(c0, rd("census after " + k, "GObject"))); wi = rd("Wire index " + k, "Wire")   # noqa: E702
        o["rle"] = dict((w, g.wire_remove_loose_ends(W, w, index=wi[w])) for w in o["new_wires"] if w in wi)
        o["broken_after_rle"] = [w for w, r in o["rle"].items() if r.get("broken_after") or r.get("err")]; o["src_wire_recreated"] = bool(o["src_wire_before"]) and o["src_wire_before"] in o["gone"]   # noqa: E702
    o["es"] = None if DRY else g.exec_state(W); OUT["wires"][k] = o                          # noqa: E702
    s.fact("WIRE %s Is Broken? %s err %r delta %s rle %s ES %s" % (tag, res.get("broken"), cw["err"], json.dumps({x: o.get(x) for x in ("new", "gone", "new_wires", "new_tunnels", "src_wire_recreated")}, sort_keys=True), o.get("rle"), o["es"]))
    ok = res and not cw["err"] and (not o.get("broken_after_rle", []) if rle else res.get("broken") is False)
    OK[k] = bool(DRY or ok); s.gate("W %s op err '' and Is Broken? False%s" % (tag, " after RLE" if rle else ""), DRY or ok, res); return o   # noqa: E702
def kread(tag, u): r = s.safe("read_const_value #%s" % u, lambda: g.read_const_value(s.work, u), {})[0] or {}; OUT[tag] = {k: r.get(k) for k in ("cls", "value", "type", "text", "wire", "err")}; s.fact("KMX %s %s" % (tag, OUT[tag]))   # noqa: E702
def face(pidx, ws):                                                                         # WS's own Terminals[] on #P
    d, n = ni(pidx, ws); rows = [] if DRY else g.node_terms_uids(s.work, d, n)[1]           # noqa: E702
    WIRE.update((int(r["uid"]), int(r["wire"] or 0)) for r in rows); return [(r["uid"], r["name"], r["is_source"], r["wire"]) for r in rows]   # noqa: E702
def body(_):
    s.start(); s.discard_work(); W = s.work                                                  # noqa: E702
    D0 = rd("A start Diagram", "Diagram")                                                    # ---- part A: WS + creates (B creates before A2: ONE read_terms)
    ws = s._op("loop_in", lambda: g.loop_in("while", W, D0.get(P, 0), tuple(POS["ws"])), "while on #%s" % P)["result"]
    D1 = rd("A after loop_in Diagram", "Diagram"); wb = (sorted(set(D1) - set(D0)) or [0])[0]   # noqa: E702
    s.gate("A1 one While #%s with ONE new body Diagram #%s" % (ws, wb), DRY or (ws and len(set(D1) - set(D0)) == 1), ws); ws = 0 if DRY else int(ws); pi, bi = D1.get(P, 0), D1.get(wb, 0)   # noqa: E702
    ks, iai = create("ks", wb, "const_donor", "k_i32_0"), create("iai", P, "Index Array", "ia")
    lrn, gt, km1, sel = local("lrn", LB["num"], wb, bi), create("gt", wb, "Greater?", "greater"), create("km1", wb, "const_donor", "k_i32_m1"), create("sel", wb, "Select", "select")
    amm, lt, orr, lrs = create("amm", wb, "Array Max & Min", "amm"), create("lt", wb, "Less?", "less"), create("or", wb, "Or", "or"), local("lrs", LB["stop"], wb, bi)
    kc = {"result": {}} if DRY else s.const_row({"loop_uid": ws, "body_diagram": wb, "node": sel, "term": "f", "value": PL["k_max"]}, tag="U2 KMX on Select.f")
    kmx = 0 if DRY else int(((kc.get("result") or {}).get("created_uid")) or 0)
    OK["U2"] = s.gate("U2 KMX created on Select.f before t is wired (#%s)" % kmx, DRY or (kmx and not (kc.get("result") or {}).get("err")), kc.get("result")); DRY or kread("before_t", kmx)   # noqa: E702
    kterms({ks, km1, kmx}); fd = dict((u, sorted(set(x.get("frame_diagram") for x in KT.get(u, [])))) for u in (ks, km1, kmx)); s.fact("KT consts by owner uid %s frame_diagram %s" % ({u: len(KT.get(u, [])) for u in (ks, km1, kmx)}, fd))   # noqa: E702
    s.gate("K0 ks/km1/kmx rows all on body #%s (read_terms frame_diagram)" % wb, DRY or all(v == [wb] for v in fd.values()), fd)
    OUT["A2"] = wire("A2 IAI.index <- KS (body -> parent)", nt(pi, iai, False, N["ia_idx"]), kt(ks))
    f = face(pi, ws); out = [x for x in f if x[2] and int(x[3] or 0)]; OUT["ws_faces_after_A2"] = f   # noqa: E702
    s.fact("WS #%s Terminals[] after A2 %s" % (ws, f)); OK["A2b"] = s.gate("A2b WS has ONE wired source face (TS outer face) on #%s" % P, DRY or len(out) == 1, f)   # noqa: E702
    wire("U1a GT.x <- Num", nt(bi, gt, False, "x"), nt(bi, lrn, True)); wire("U1b GT.y <- I32 -1", nt(bi, gt, False, "y"), kt(km1))   # noqa: E702
    wire("U1c Select.t <- Num (branch)", nt(bi, sel, False, "t"), nt(bi, lrn, True)); DRY or kread("after_t", kmx)   # noqa: E702
    wire("U3 Select.s <- GT out (Boolean array)", nt(bi, sel, False, "s"), nt(bi, gt, True, N["gt_out"]))
    wire("U3b AMM.array <- Select out", nt(bi, amm, False, N["amm_in"]), nt(bi, sel, True, N["sel_out"]))
    wire("U3c LT.x <- AMM.min value", nt(bi, lt, False, "x"), nt(bi, amm, True, N["amm_min"])); wire("U3d LT.y <- KMX (branch)", nt(bi, lt, False, "y"), kt(kmx))   # noqa: E702
    wire("W1a Or.x <- LT out", nt(bi, orr, False, "x"), nt(bi, lt, True, N["lt_out"])); wire("W1b Or.y <- stop (end) Local", nt(bi, orr, False, "y"), nt(bi, lrs, True))   # noqa: E702
    WL = rd("B end WhileLoop", "WhileLoop")
    if not DRY:
        bo, n = ni(bi, orr); ti = [int(r["i"]) for r in g.node_terms(W, bo, n) if r["name"] == N["or_out"] and r["is_source"]]; lab = json.load(open(os.path.join(HERE, "opstopfromnode_labels.json"), encoding="utf-8"))   # noqa: E702
        def _c():
            vs = g.op(os.path.join(g.CLAUDEDEV, "OpStopFromNode_v0.vi"))
            [vs.SetControlValue(k, v) for k, v in (("vi path", W), ("Class Name", "WhileLoop"), ("index", WL[ws]), (lab["index_node"], n), (lab["index_term"], ti[0]))]; g._run(vs); return g._err(vs, "error out") or ""   # noqa: E702
        rec = s._op("stop_from_node", _c, "WS #%s cond <- N[%s].t%s" % (ws, n, ti))
        le = K.mod("build_d1_v0").loop_end_ref(W, WL[ws]); ow = [x["wire"] for x in g.node_terms(W, bo, n) if x["name"] == N["or_out"] and x["is_source"]]   # noqa: E702
        OUT["stop"] = {"op": rec["err"] or rec["result"], "loop_end_ref": le, "or_out_wire": ow}; s.fact("W1 WS cond read-back %s; Or out wire %s" % (le, ow)); OK["W1c"] = s.gate("W1c WS cond wired from the Or (cond wire == Or out wire)", le.get("cond_wire_uid") and [le.get("cond_wire_uid")] == ow, (le, ow))   # noqa: E702
    cp = s._op("struct_copy_nested", lambda: g.struct_copy_nested(W, P, "FlatSequence", g.fs_donor(), tuple(POS["fs"])), "FS -> #%s" % P)["result"] or {}   # ---- part C
    f0 = 0 if DRY else int((cp.get("new_diagrams") or [0])[0]); s.gate("A3 FS #%s frame f0 #%s" % (cp.get("uid"), f0), DRY or f0, cp)   # noqa: E702
    ian, eq2 = create("ian", f0, "Index Array", "ia"), create("eq2", P, "Equal?", "eq")     # creates BEFORE the part-C Diagram read
    D2 = rd("C start Diagram", "Diagram"); pi, fi = D2.get(P, 0), D2.get(f0, 0)              # noqa: E702
    tsf = 0 if DRY else int(([x for x in face(pi, ws) if x[2] and int(x[3] or 0)] or [(0,)])[0][0])
    OUT["U5"] = wire("U5 IAN.index (FS f0) <- TS outer face", nt(fi, ian, False, N["ia_idx"]), tsf, rle=True)
    OUT["ws_faces_after_U5"] = face(pi, ws); s.fact("WS #%s Terminals[] after U5 %s (before A2-read %s)" % (ws, OUT["ws_faces_after_U5"], OUT.get("ws_faces_after_A2")))   # noqa: E702
    OUT["U6"] = wire("U6 EQ2.y (#%s) <- IAN.element (FS f0 exit)" % P, nt(pi, eq2, False, "y"), nt(fi, ian, True, N["ia_el"]), rle=True)
    nl, nk = len(OUT["lookups"]), len(OUT["klookups"]); s.gate("L lookups reached: ni %d (want %d), const %d (want 3)" % (nl, 22 if DRY else 26, nk), nl == (22 if DRY else 26) and nk == 3, OUT["moved"])   # noqa: E702
    OUT["es_end"] = None if DRY else g.exec_state(W); s.fact("ExecState end %s; whole-VI reads %d %s; lookup moves %s" % (OUT["es_end"], len(OUT["reads"]), OUT["reads"], OUT["moved"]))   # noqa: E702
    RT = {"A2": ["A2", "A2b"], "U1": ["U1a", "U1b", "U1c"], "U2": ["U2"], "U3": ["U3", "U3b", "U3c", "U3d"], "U5": ["U5"], "U6": ["U6"], "W1-Or": ["W1a", "W1b", "W1c"]}; OUT["routes"] = dict((r, {"pass": all(OK.get(t, DRY) for t in ts), "broken": [(OUT["wires"].get(t) or {}).get("op", {}).get("broken") for t in ts], "census": {t: {x: (OUT["wires"].get(t) or {}).get(x) for x in ("new", "gone", "new_tunnels", "src_wire_recreated")} for t in ts if t in ("U5", "U6")}}) for r, ts in RT.items())
    [s.fact("ROUTE %s %s Is Broken? %s census %s" % (r, "PASS" if v["pass"] else "FAIL", v["broken"], v["census"] or "not read (R budget, PD193(a))")) for r, v in OUT["routes"].items()]
    if not DRY:
        EC = K.mod("errorlist_check"); EC._lv_imports(); RR = {"gui_acts_outer": [], "errors": []}; EC.open_diagram(W, RR)   # noqa: E702
        r = EC.E.read(W, os.path.join(HERE, "errorlist_c137_5_routes_%s_raw.json" % s.stamp), log=lambda m: None, on_item=None)
        base, cc = EC.class_counts(json.load(open(os.path.join(HERE, PL["errorlist_base"]), encoding="utf-8"))["items"]), EC.class_counts(r.get("items"))
        OUT["el"] = {"items": len(r.get("items") or []), "n": r.get("n_reported"), "extra": {k: cc[k] - base.get(k, 0) for k in cc if cc[k] > base.get(k, 0)}, "missing": {k: base[k] - cc.get(k, 0) for k in base if base[k] > cc.get(k, 0)}, "errors": (r.get("errors") or [])[:2]}
        s.fact("EL end (count read, no double-clicks) TOTAL %s (window N %s, bed 51) extra %s missing %s errors %s" % (OUT["el"]["items"], OUT["el"]["n"], OUT["el"]["extra"], OUT["el"]["missing"], OUT["el"]["errors"]))
    s.gate("X bed md5 unchanged", K.md5(BED) == BEDM, K.md5(BED))
    if not DRY:
        OUT["scratch_md5"] = K.md5(W) if os.path.exists(W) else None
        json.dump({"function": "connect_term_uid", "variant": "c137-5 P4 routes A2 U1 U2 U3 U5 U6 W1-Or (body consts by read_terms owner uid)", "status": "PASS" if not s.fails else "FAIL", "t": time.time(), "card": "137-5",
                   "log": "tools/bench/diag_c137_5_routes.log", "fails": s.fails, "out": OUT}, open(os.path.join(HERE, "scratch_verify", "gscript.connect_term_uid_c137_5_%s.json" % s.stamp), "w", encoding="utf-8"), default=str, indent=1)
    json.dump(OUT, open(os.path.join(HERE, "diag_c137_5_routes_out.json"), "w", encoding="utf-8"), default=str, indent=1); s.dump()   # noqa: E702
if __name__ == "__main__":
    rc = K.run(body, s); DRY or K.mod("stagexec").kill_labview_at_exit(); sys.exit(rc)     # noqa: E702
