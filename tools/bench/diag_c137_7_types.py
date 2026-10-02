r"""diag_c137_7_types - card 137-7 (PD309(a)): WHY U3 (Select.s <- Greater? on an array) and U6 (FS f0 exit wire) came back broken
(diag_c137_5_routes.log:108-110,127-129,167-169). Built on diag_c137_5_routes.py (ffef9235) helpers; prior tools found and reused:
gscript.read_term_type (OpTermDataType_v0, docs/NAMES.md:486-492), allterms.read_terms (OP_ALLTERMS_V1 :43, every terminal with wire +
owner + frame), gscript.wire_remove_loose_ends (broken_before/after), errorlist_check (EL). Plan diag_c137_7_plan.json. Scratch byte copy.
ALL creates first, then ONE read_terms gives every terminal uid by (owner uid, name, direction) - no per-node Diagram lookups.
WHOLE-VI READ SITES (each once, none in a loop): R1 Diagram D0 | R2 read_terms after creates | R3 read_terms after wiring | R4 Wire
index (RLE) => R = 1 (k 0) + 4 = 5; N = 39 ops -> 606.1+5*2.53+39*1.38+17.4 = 690.0 MB (X10 counts R = 1 + 2 read_terms).
HIDDEN (not in R): connect_term_uid's Terminal uid_index per wire, const_row's address/uid_index, read_term_type echo fallbacks (<= 4).
Review archive/peer/2026-10-02-c137-7-hyp-c137-5-routes.md applied: Select out found as its ONLY source (name 's? t:f', diag_c128_2_donors
.log:62, not the plan's 's? t: f'); C4 replaced by C5 = scalar-Boolean s control (GT5.x <- I32 0); U6' = exit from an IAN whose array is wired.
PREDICTION (review sec.1): array-s C1 C2 C3 Is Broken? True, C5 False; U6 outer broken True; U6' unknown; every op err ''; type echo == uid.
py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c137_7_types.log -- py -u tools/bench/diag_c137_7_types.py"""
import json, os, sys, time                                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes")); import stagekit as K; g = K.g   # noqa: E402,E702
Q = json.load(open(os.path.join(HERE, "diag_c137_7_plan.json"), encoding="utf-8")); PL = json.load(open(os.path.join(HERE, Q["base_plan"]), encoding="utf-8"))   # noqa: E702
BED, BEDM, P, DN, N, POS, LB, LOOP = PL["input"]["vi"], PL["input"]["md5"], PL["parent"], PL["donors"], PL["names"], Q["pos"], PL["labels"], Q["loop_uid"]
DRY, AT = bool(getattr(g.report_all, "_dry", False)), K.mod("allterms")
OUT, RT, FB = {"creates": {}, "wires": {}, "types": {}, "reads": []}, {"rows": []}, {"n": 0}
s = K.Stage(BED, BEDM, "scratch_c137_7_types", preload=False, deadline_min=28, reserve_s=150, out_json=os.path.join(HERE, "diag_c137_7_types.json"), task="card 137-7 items 2-5")
def dn(k): return {"donor": s.work if DN[k]["donor"] == "$work" else DN[k]["donor"], "uid": DN[k]["uid"]}
def create(tag, dg, prim, k): u = s._op("create_primitive_nested", lambda: g.create_primitive_nested(s.work, dg, prim, tuple(POS[tag]), donor=dn(k)), "%s %s" % (tag, prim))["result"]; OUT["creates"][tag] = u; s.gate("C %s op err '' and a node" % tag, DRY or u, u); return 0 if DRY else int(u or 0)   # noqa: E702
def terms(tag):                                                                             # ONE whole-VI terminal read
    rows = AT.read_terms(s.work, op=AT.OP_ALLTERMS_V1)[0]; OUT["reads"].append(tag); RT["rows"] = [] if DRY else list(rows); s.fact("read_terms %s: %d rows" % (tag, len(RT["rows"])))   # noqa: E702
def T(owner, src, name=None, but=None):                                                     # terminal uid by owner + direction (+ name / all but `but`)
    if DRY: return 0                                                                        # noqa: E701
    r = [x for x in RT["rows"] if x["owner_uid"] == int(owner) and x["is_source"] == src and (name is None or x["term_name"] == name) and x["term_name"] != but]
    s.gate("T #%s %s %s: exactly one terminal" % (owner, name, "src" if src else "sink"), len(r) == 1, [(x["term_uid"], x["term_name"], x["wire_uid"]) for x in r][:6]); return int(r[0]["term_uid"]) if len(r) == 1 else 0   # noqa: E702
def wire(tag, snk, src):
    cw = s._op("connect_term_uid", lambda: g.connect_term_uid(s.work, snk, src), "%s #%s <- #%s" % (tag, snk, src)); res = cw["result"] or {}   # noqa: E702
    OUT["wires"][tag] = {"wire": res.get("wire_uid"), "broken": res.get("broken"), "err": cw["err"]}; s.fact("WIRE %s Is Broken? %s wire %s err %r" % (tag, res.get("broken"), res.get("wire_uid"), cw["err"]))   # noqa: E702
    s.gate("W %s op err ''" % tag, DRY or (res and not cw["err"]), res); return res.get("wire_uid")   # noqa: E702
def ttype(tag, tu):                                                                         # data type of terminal #tu, index from read_terms #2
    if DRY or not tu: return None                                                           # noqa: E701
    ix = [i for i, x in enumerate(RT["rows"]) if x["term_uid"] == int(tu)]
    r = s.safe("read_term_type %s #%s" % (tag, tu), lambda: g.read_term_type(s.work, tu, index=ix[0] if ix else None), {})[0] or {}
    if "echo" in str(r.get("err")) and FB["n"] < 4: FB["n"] += 1; r = s.safe("read_term_type (re-read index) %s" % tag, lambda: g.read_term_type(s.work, tu), {})[0] or {}   # noqa: E701,E702
    ty = r.get("types") or {}; OUT["types"][tag] = {"term": int(tu), "canon": ty.get("canon"), "top": ty.get("top_name"), "err": r.get("err"), "echo": r.get("echo")}   # noqa: E702
    s.fact("TYPE %-14s #%s %s (top %s) err %r" % (tag, tu, ty.get("canon"), ty.get("top_name"), r.get("err"))); return ty.get("canon")   # noqa: E702
def endpoints(tag, w):                                                                      # every terminal on wire #w (read_terms #2)
    e = [(x["term_uid"], x["term_name"], x["is_source"], x["owner_uid"], x["owner_class"], x.get("frame_diagram")) for x in RT["rows"] if w and x["wire_uid"] == int(w)]
    OUT["wires"].setdefault("ends_" + tag, e); s.fact("ENDS %s wire %s: %d terminal(s), %d source(s): %s" % (tag, w, len(e), sum(1 for x in e if x[2]), e)); return e   # noqa: E702
def body(_):
    s.start(); s.discard_work(); W = s.work                                                  # noqa: E702
    D0 = [] if DRY else g.report_all(W, "Diagram"); OUT["reads"].append("Diagram D0"); pi = 0 if DRY else [int(r["uid"]) for r in D0].index(P)   # noqa: E702
    lr = {"uid": 0} if DRY else (s.create_local_read(LB["num"], tag="lrn")["result"] or {}); lrn = int(lr.get("uid") or 0); s.move_in(lrn, pi, tuple(POS["lrn"]))   # noqa: E702
    km1, ka, kb = create("km1", P, "const_donor", "k_i32_m1"), create("kA", P, "const_donor", "k_i32_0"), create("kB", P, "const_donor", "k_i32_m1")
    gt = [create("gt%d" % i, P, "Greater?", "greater") for i in (1, 2, 3, 5)]; sel = [create("sel%d" % i, P, "Select", "select") for i in (0, 1, 2, 3, 5)]   # noqa: E702
    kc_ = {"result": {}} if DRY else s.const_row({"loop_uid": LOOP, "body_diagram": P, "node": sel[1], "term": "f", "value": PL["k_max"]}, tag="KMX on SEL1.f")
    kmx = 0 if DRY else int(((kc_.get("result") or {}).get("created_uid")) or 0); s.gate("U2 KMX created on SEL1.f before t (#%s)" % kmx, DRY or (kmx and not (kc_.get("result") or {}).get("err")), kc_.get("result"))   # noqa: E702
    cp = s._op("struct_copy_nested", lambda: g.struct_copy_nested(W, P, "FlatSequence", g.fs_donor(), tuple(POS["fs"])), "FS -> #%s" % P)["result"] or {}
    f0 = 0 if DRY else int((cp.get("new_diagrams") or [0])[0]); s.gate("A3 FS #%s frame f0 #%s" % (cp.get("uid"), f0), DRY or f0, cp)   # noqa: E702
    ian, eq2, ian2, eq3 = create("ian", f0, "Index Array", "ia"), create("eq2", P, "Equal?", "eq"), create("ian2", f0, "Index Array", "ia"), create("eq3", P, "Equal?", "eq")
    terms("after creates")
    num = T(lrn, True)
    wire("GT1.x <- Num", T(gt[0], False, "x"), num); wire("GT1.y <- I32 -1", T(gt[0], False, "y"), T(km1, True))   # noqa: E702
    [wire("GT%d.x <- Num" % (i + 1), T(gt[i], False, "x"), num) for i in (1, 2)]; wire("GT5.x <- I32 0 (scalar)", T(gt[3], False, "x"), T(ka, True))   # noqa: E702
    wire("C3 SEL1.t <- Num", T(sel[1], False, "t"), num)
    wire("C1 SEL2.t <- Num", T(sel[2], False, "t"), num); wire("C1 SEL2.f <- Num", T(sel[2], False, "f"), num)   # noqa: E702
    wire("C2 SEL3.t <- I32 0", T(sel[3], False, "t"), T(ka, True)); wire("C2 SEL3.f <- I32 -1", T(sel[3], False, "f"), T(kb, True))   # noqa: E702
    wire("C5 SEL5.t <- Num", T(sel[4], False, "t"), num); wire("C5 SEL5.f <- Num", T(sel[4], False, "f"), num)   # noqa: E702
    for c, i, j in (("C3", 1, 1), ("C1", 2, 2), ("C2", 3, 3), ("C5", 4, 5)): wire("%s SEL%d.s <- GT%d out" % (c, j, j), T(sel[i], False, "s"), T(gt[i - 1], True, N["gt_out"]))   # noqa: E701
    wire("U6 EQ2.y <- IAN.element (FS f0 exit)", T(eq2, False, "y"), T(ian, True))
    wire("U6' IAN2.array <- Num (FS entry)", T(ian2, False, but=N["ia_idx"]), num); wire("U6' EQ3.y <- IAN2.element (FS f0 exit)", T(eq3, False, "y"), T(ian2, True))   # noqa: E702
    terms("after wiring")                                                                    # ---- types, endpoints (index valid until RLE)
    ttype("Num", T(lrn, True)); [ttype(k, T(u, True)) for k, u in (("km1", km1), ("kA I32 0", ka), ("kB I32 -1", kb), ("KMX", kmx))]   # noqa: E702
    [ttype("GT%d %s" % (j, n), T(gt[i], n == N["gt_out"], n)) for i, j in enumerate((1, 2, 3, 5)) for n in ("x", "y", N["gt_out"])]
    [ttype("SEL%d %s" % (j, n or "out"), T(sel[i], n is None, n)) for i, j in enumerate((0, 1, 2, 3, 5)) for n in ("s", "t", "f", None)]
    [ttype("%s %s" % (k, tg), T(u, sr, n, but=b)) for k, u in (("IAN", ian), ("IAN2", ian2)) for tg, n, b, sr in (("out", None, None, True), ("index", N["ia_idx"], None, False), ("array", None, N["ia_idx"], False))]
    [ttype("%s y" % k, T(u, False, "y")) for k, u in (("EQ2", eq2), ("EQ3", eq3))]
    W6 = {} if DRY else dict((k, ([x["wire_uid"] for x in RT["rows"] if x["owner_uid"] == u and x["is_source"] == sr and (sr or x["term_name"] == "y")] + [0])[0]) for k, u, sr in (("U6 inner", ian, True), ("U6 outer", eq2, False), ("U6' inner", ian2, True), ("U6' outer", eq3, False)))
    E6 = dict((k, endpoints(k, w)) for k, w in W6.items()); tun = sorted(set(x[3] for e in E6.values() for x in e if "Tunnel" in str(x[4]))); OUT["u6_tunnels"] = tun   # noqa: E702
    [ttype("face #%s %s" % (x[0], "src" if x[1] else "sink"), x[0]) for x in sorted(set((t[0], t[2]) for e in E6.values() for t in e if t[3] in tun))]
    ws = sorted(set(w for w in [x["wire_uid"] for x in RT["rows"] if x["owner_uid"] in set([lrn, km1, ka, kb, kmx] + gt + sel)] + list(W6.values()) if w)) if not DRY else []
    [endpoints("w%s" % w, w) for w in ws if w not in W6.values()]
    WI = {} if DRY else dict((int(r["uid"]), i) for i, r in enumerate(g.report_all(W, "Wire"))); OUT["reads"].append("Wire index")   # noqa: E702
    OUT["rle"] = dict((w, s.safe("RLE w%s" % w, lambda: g.wire_remove_loose_ends(W, w, index=WI.get(w)), {})[0]) for w in ws)   # Is Broken? before/after per wire
    [s.fact("BROKEN w%s before %s after %s err %r" % (w, (r or {}).get("broken_before"), (r or {}).get("broken_after"), (r or {}).get("err"))) for w, r in OUT["rle"].items()]
    OUT["es_end"] = None if DRY else g.exec_state(W); s.fact("ExecState end %s; whole-VI reads %s; echo fallbacks %d" % (OUT["es_end"], OUT["reads"], FB["n"]))   # noqa: E702
    bad = [k for k, v in OUT["types"].items() if v.get("err")]; s.gate("Y every type read err '' (echo == uid)", DRY or not bad, bad)   # noqa: E702
    if not DRY:
        EC = K.mod("errorlist_check"); EC._lv_imports(); RR = {"gui_acts_outer": [], "errors": []}; EC.open_diagram(W, RR)   # noqa: E702
        r = EC.E.read(W, os.path.join(HERE, "errorlist_c137_7_types_%s_raw.json" % s.stamp), log=lambda m: None, on_item=None)
        X = json.load(open(os.path.join(HERE, PL["errorlist_base"]), encoding="utf-8"))           # the expected file: keys 'total' + 'expected'
        OUT["el"] = {"items": len(r.get("items") or []), "n": r.get("n_reported"), "base_total": X.get("total"), "base_entries": len(X.get("expected") or []), "classes": EC.class_counts(r.get("items")), "errors": (r.get("errors") or [])[:2]}
        s.fact("EL end (count read) TOTAL %s (window N %s, bed expected total %s) classes %s errors %s" % (OUT["el"]["items"], OUT["el"]["n"], OUT["el"]["base_total"], OUT["el"]["classes"], OUT["el"]["errors"]))
    s.gate("X bed md5 unchanged", K.md5(BED) == BEDM, K.md5(BED))
    if not DRY:
        OUT["scratch_md5"] = K.md5(W) if os.path.exists(W) else None
        json.dump({"function": "read_term_type", "variant": "c137-7 U3 Select combos C1-C4 + SEL0 + U6 FS exit types/endpoints/Is Broken?", "status": "PASS" if not s.fails else "FAIL", "t": time.time(), "card": "137-7",
                   "log": "tools/bench/diag_c137_7_types.log", "fails": s.fails, "out": OUT}, open(os.path.join(HERE, "scratch_verify", "gscript.read_term_type_c137_7_%s.json" % s.stamp), "w", encoding="utf-8"), default=str, indent=1)
    json.dump(OUT, open(os.path.join(HERE, "diag_c137_7_types_out.json"), "w", encoding="utf-8"), default=str, indent=1); s.dump()   # noqa: E702
if __name__ == "__main__":
    rc = K.run(body, s); DRY or K.mod("stagexec").kill_labview_at_exit(); sys.exit(rc)     # noqa: E702
