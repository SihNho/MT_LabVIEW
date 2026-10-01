r"""diag_c126_4_fs - card 126-4 STEP 2 (brief_126-4.md, PD254(e)): diag_c126_2_fs.py's FS build (3 frames in case #22694's False frame,
frame-1 const -> frame-2 Max & Min) on a never-saved P3a byte copy, EXTENDED: case-frame Quotient & Remainder 'x-y*floor(x/y)' (plan "qr")
-> Max & Min x in FS frame 1, then a SECOND sink from the same source -> Max & Min x in FS frame 3 (connect_term_uid). Per crossing:
census delta, op Is Broken?, joints of every wire on the source + every new wire, tunnels made (rows with frame_diagram). Tail: one-terminal
wires (reads, then gscript.wire_remove_loose_ends), unwired FS inner tunnels, Error List count-only per class vs the bed's recorded 55.
PREDICTION: K F1 F2 CEN W1 as in 126-2; S0 one qr source on Diagram #27219 + one x per Max & Min; Q1/Q3 op err ''; R echo == uid, err ''.
Every VALUE (Is Broken?, tunnels, free ends, Error List) is a MEASUREMENT. X bed md5 unchanged, scratch deleted, LabVIEW gone.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/diag_c126_4_fs.log -- py -u tools/bench/diag_c126_4_fs.py"""
import json, os, sys                                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K; g = K.g                                                               # noqa: E402,E702
PL = json.load(open(os.path.join(HERE, "diag_c126_4_fs_plan.json"), encoding="utf-8"))
DON, DONM = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"]
DRY = bool(getattr(g.report_all, "_dry", False))
CASE, FF0, QR, XT = PL["case"], PL["false_frame"], PL["qr"], PL["sink_term"]
CONST = {"donor": os.path.join(g.CLAUDEDEV, PL["const_donor"]["vi"]), "uid": PL["const_donor"]["uid"]}
BASE_EL, OUT = os.path.join(HERE, PL["errorlist_base"]), {}
s = K.Stage(DON, DONM, "scratch_c126_4_fs", preload=False, deadline_min=38, reserve_s=150,
            out_json=os.path.join(HERE, "diag_c126_4_fs.json"), task="card 126-4 STEP 2")
def dec(r):
    J = [list(x) for x in (r or {}).get("joints") or []]
    return {"joints": len(J), "loose": sum(1 for x in J if int(x[1]) & 0x100), "terms": sum(1 for x in J if int(x[1]) & 0x1),
            "free": [(i, list(x[0])) for i, x in enumerate(J) if int(x[2]) == 1 and not int(x[1]) & 0x1]}
def terms(W):
    import allterms
    return [] if DRY else allterms.read_terms(W, allterms.OP_ALLTERMS_V1)[0]
def row(r): return (r["owner_class"], r["owner_uid"], r["term_name"], r["is_source"], r["frame_diagram"], r["wire_uid"])
def errlist(W, tag):
    import errorlist_check as EC
    EC._lv_imports(); R = {"gui_acts_outer": [], "errors": []}; EC.open_diagram(W, R)       # noqa: E702
    r = EC.E.read(W, os.path.join(HERE, "errorlist_c126_4_%s_%s_raw.json" % (tag, s.stamp)), log=lambda m: None, on_item=None)
    base, cc = EC.class_counts(json.load(open(BASE_EL, encoding="utf-8"))["items"]), EC.class_counts(r.get("items"))
    d = dict((k, (base.get(k, 0), cc.get(k, 0))) for k in sorted(set(base) | set(cc)) if base.get(k, 0) != cc.get(k, 0))
    s.fact("EL %s: N %s items %d errors %s; per-class delta vs the bed's 55 (bed, now) %s" % (tag, r.get("n_reported"), len(r.get("items") or []),
           (r.get("errors") or [])[:2], d))
    return {"n": r.get("n_reported"), "items": len(r.get("items") or []), "delta": d}
def cross(W, tag, snk, src):
    c0, w0 = s.census_snapshot(), set(g.uids(W, "Wire"))
    cw = s._op("connect_term_uid", lambda: g.connect_term_uid(W, snk, src), "%s x <- qr" % tag)["result"] or {}
    c1, wn = s.census_snapshot(), sorted(set(g.uids(W, "Wire")) - w0)
    new, rows = dict((u, c1[u]) for u in set(c1) - set(c0)), terms(W)
    ws = sorted(set(wn) | set(int(r["wire_uid"] or 0) for r in rows if int(r["term_uid"]) == src and int(r["wire_uid"] or 0)))
    jt = dict((w, dec(g.wire_joints(W, w))) for w in ws if not DRY)
    tun = dict((u, [row(r) for r in rows if int(r["owner_uid"]) == u]) for u, c in new.items() if "Tunnel" in c)
    OUT[tag] = {"op": cw, "census_new": sorted((c, u) for u, c in new.items()), "gone": sorted(set(c0) - set(c1)), "new_wires": wn,
                "joints": jt, "tunnels": tun, "src_wires": ws}
    s.fact("%s %s" % (tag, OUT[tag]))
    s.gate("%s op err '' (values are a measurement)" % tag, DRY or (cw and not cw.get("err")), cw)
    return wn, jt, new
def tail(W, wn, jt, cnew):
    rows = terms(W)
    one = [w for w in wn if jt.get(w, {}).get("terms") == 1]
    bare = [u for u, c in cnew.items() if c == "FlatSequenceInnerTunnel" and not any(int(r["owner_uid"]) == u and int(r["wire_uid"] or 0) for r in rows)]
    for w in one:
        s.fact("ONE-TERMINAL w%s on %s" % (w, [row(r) for r in rows if int(r["wire_uid"] or 0) == w]))
    s.fact("FS inner tunnels with no wire %s; ES %s" % (bare, g.exec_state(W)))
    OUT.update(one_terminal=one, tunnels_unwired=bare, el_after_connect=errlist(W, "fs_after_connect"))
    c4 = s.census_snapshot()
    for w in one:
        cu = g.wire_remove_loose_ends(W, w); pres = w in g.uids(W, "Wire")                  # noqa: E702
        OUT.setdefault("rle", {})[w] = {"op": cu, "present_after": pres, "joints_after": dec(g.wire_joints(W, w)) if pres else None,
                                        "terms_after": [row(r) for r in terms(W) if int(r["wire_uid"] or 0) == w]}
        s.fact("RLE w%s %s" % (w, OUT["rle"][w]))
        s.gate("R RemoveLooseEnds w%s echo == uid, err ''" % w, cu["echo"] == w and not cu["err"], cu)
    if one:
        c5 = s.census_snapshot()
        OUT["census_rle"] = {"new": sorted((c5[u], u) for u in set(c5) - set(c4)), "gone": sorted((c4[u], u) for u in set(c4) - set(c5))}
        s.fact("CENSUS RemoveLooseEnds delta %s; ES %s" % (OUT["census_rle"], g.exec_state(W)))
        OUT["el_after_rle"] = errlist(W, "fs_after_rle")
def body(_):
    s.start(); s.discard_work(); W = s.work                                                  # noqa: E702
    fr = g.case_frames(W, CASE); names = [str(n).strip() for n in fr["names"]]              # noqa: E702
    ff = FF0 if DRY else (int(fr["frames"][names.index("False")]) if "False" in names else 0)
    s.gate("K case #%s frames %s, False = Diagram #%s" % (CASE, names, ff), DRY or ff == FF0, fr)
    c0 = s.census_snapshot()
    cp = s._op("struct_copy_nested", lambda: g.struct_copy_nested(W, ff, "FlatSequence", g.fs_donor(), (60, 60)), "FS -> #%s" % ff)["result"] or {}
    fs = 1 if DRY else int(cp.get("uid") or 0)
    if not s.gate("F1 one new FlatSequence #%s owned by Diagram #%s" % (fs, ff), DRY or bool(fs), cp):
        return s.dump()
    f1 = g.fs_frames(W, fs)
    a1 = s._op("fs_add_frame", lambda: g.fs_add_frame(W, fs, 0, True), "after 0")["result"] or {}
    a2 = s._op("fs_add_frame", lambda: g.fs_add_frame(W, fs, 1, True), "after 1")["result"] or {}
    f3 = g.fs_frames(W, fs)["frames"]
    s.gate("F2 3 frames; first stays leftmost; add(0,T) new at 1, add(1,T) new at 2", DRY or (len(f3) == 3 and f3[0] == f1["frames"][0]
           and f3[1] == a1.get("new_frame") and f3[2] == a2.get("new_frame")), (f1, f3))
    f3 = [0, 0, 0] if DRY else f3
    s.census_gate("CEN census delta of FS copy + 2 Add Frame == FlatSequence 1 + Diagram 3", c0, s.census_snapshot(), {"FlatSequence": 1, "Diagram": 3})
    if len(f3) != 3:
        return s.dump()
    k = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, f3[0], "I32 const", (40, 40), donor=CONST), "const -> frame 1")["result"]
    m = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, f3[1], "Max & Min", (60, 40)), "Max & Min -> frame 2")["result"]
    m1 = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, f3[0], "Max & Min", (60, 140)), "Max & Min -> frame 1")["result"]
    m3 = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, f3[2], "Max & Min", (60, 40)), "Max & Min -> frame 3")["result"]
    rows = terms(W)
    pick = lambda u, src, nm=None: [r for r in rows if int(r["owner_uid"]) == int(u or 0) and bool(r["is_source"]) == src and (nm is None or str(r["term_name"]) == nm)]  # noqa: E731
    ks, mx, x1, x3, q = pick(k, True), pick(m, False, XT), pick(m1, False, XT), pick(m3, False, XT), pick(QR["owner"], True, QR["term"])
    ok = DRY or (all(len(v) == 1 for v in (ks, mx, x1, x3, q)) and int(q[0]["frame_diagram"]) == QR["frame"])
    if not s.gate("S0 one const output, one x on each Max & Min, one qr source on Diagram #%s" % QR["frame"], ok, [len(v) for v in (ks, mx, x1, x3, q)]):
        return s.dump()
    tu = (lambda v: 0 if DRY else int(v[0]["term_uid"]))
    c2, wb = s.census_snapshot(), set(g.uids(W, "Wire"))
    cw = s._op("connect_term_uid", lambda: g.connect_term_uid(W, tu(mx), tu(ks)), "x <- const")["result"] or {}
    c3, wn = s.census_snapshot(), sorted(set(g.uids(W, "Wire")) - wb)
    tun = [(c3[u], u) for u in sorted(set(c3) - set(c2)) if "Tunnel" in c3[u] or "Terminal" in c3[u]]
    s.gate("W1 op err '', Is Broken? False, >= 1 tunnel-class object new %s" % tun, DRY or (cw and not cw.get("err") and cw.get("broken") is False and bool(tun)), (cw, tun))
    jt = dict((w, dec(g.wire_joints(W, w))) for w in wn if not DRY)
    s.fact("W1 JOINTS %s (free ends are a measurement)" % jt)
    n1, j1, e1 = cross(W, "Q1", tu(x1), tu(q))
    n3, j3, e3 = cross(W, "Q3", tu(x3), tu(q))
    if not DRY:
        cnew = dict((u, c3[u]) for u in set(c3) - set(c2)); cnew.update(e1); cnew.update(e3)  # noqa: E702
        jt.update(j1); jt.update(j3); tail(W, sorted(set(wn) | set(n1) | set(n3) | set(j1) | set(j3)), jt, cnew)  # noqa: E702
    s.gate("X bed md5 unchanged", K.md5(DON) == DONM, K.md5(DON))
    json.dump(OUT, open(os.path.join(HERE, "diag_c126_4_fs_out.json"), "w", encoding="utf-8"), default=str, indent=1)
    s.dump()
if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
