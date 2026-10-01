r"""diag_c126_6_cross - card 126-6 STEP B (brief_126-6.md, PD255(g)): on a never-saved P3a byte copy, the 3-frame FS of diag_c126_4_fs.py
in case #22694's False frame, then ONE multi-border crossing each by connect_term_uid (plan diag_c126_6_cross_plan.json):
 B1 BufNum #6897 (SubVI #6810 on #639, outside the case) -> Max & Min x in FS frame 3 (case + FS borders)
 B2 While #637 i #644 (on #639) -> Max & Min x in FS frame 2 (case + FS borders)
 B3 pool: IMAQ Create #23099 'New Image' #23289 in For #23093 body #23169 -> Index Array 'array' (copy of the work's #3163) in FS frame 2.
Per crossing: census delta, op Is Broken?, joints / free ends of every new wire, tunnels (rows + owner), new LoopTunnels' IndexMode
(gscript.tunnels = OpTunnels_v0, toolkit-capabilities.md:25); then wire_remove_loose_ends on EVERY new wire, same reads; END Error List total+loose.
PRIOR ART: diag_c126_4_fs.py (FS build + cross reads, same shape); connect_nested_v2 is a dangling wrapper (gscript.py:3523) - not used;
a refusal by connect_term_uid is reported, not routed around (return at first unexpected result).
PREDICTION: K F1 F2 CEN as 126-4; S0 one source + one sink terminal per crossing; B1/B2/B3 op err ''; R echo == uid, err ''. Census,
tunnels, Is Broken?, IndexMode, free ends and Error List are MEASUREMENTS. X bed md5 unchanged, scratch deleted, LabVIEW gone.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/diag_c126_6_cross.log -- py -u tools/bench/diag_c126_6_cross.py"""
import json, os, sys                                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K; g = K.g                                                               # noqa: E402,E702
PL = json.load(open(os.path.join(HERE, "diag_c126_6_cross_plan.json"), encoding="utf-8"))
DON, DONM = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"]
DRY = bool(getattr(g.report_all, "_dry", False))
CASE, FF0, XS = PL["case"], PL["false_frame"], PL["crossings"]
BASE_EL, OUT = os.path.join(HERE, PL["errorlist_base"]), {}
s = K.Stage(DON, DONM, "scratch_c126_6_cross", preload=False, deadline_min=38, reserve_s=150,
            out_json=os.path.join(HERE, "diag_c126_6_cross.json"), task="card 126-6 STEP B")
def dec(r):
    J = [list(x) for x in (r or {}).get("joints") or []]
    return {"joints": len(J), "loose": sum(1 for x in J if int(x[1]) & 0x100), "terms": sum(1 for x in J if int(x[1]) & 0x1),
            "free": [(i, list(x[0])) for i, x in enumerate(J) if int(x[2]) == 1 and not int(x[1]) & 0x1]}
def terms(W):
    import allterms
    return [] if DRY else allterms.read_terms(W, allterms.OP_ALLTERMS_V1)[0]
def row(r): return (r["owner_class"], r["owner_uid"], r["term_name"], r["is_source"], r["frame_diagram"], r["wire_uid"])
def owner(W, u):
    g._c97_paths(); import build_d1_v0 as B                                                  # noqa: E401,E702
    return list(B.owner_of(W, u, strict=False) or [])
def by_class(c0, c1): return dict((c, sum(1 for u in set(c1) - set(c0) if c1[u] == c)) for c in set(c1[u] for u in set(c1) - set(c0)))
def wires_read(W, ws):
    return dict((w, {"present": w in g.uids(W, "Wire"), "joints": dec(g.wire_joints(W, w)) if w in g.uids(W, "Wire") else None}) for w in ws)
def errlist(W, tag):
    import errorlist_check as EC
    EC._lv_imports(); R = {"gui_acts_outer": [], "errors": []}; EC.open_diagram(W, R)       # noqa: E702
    r = EC.E.read(W, os.path.join(HERE, "errorlist_c126_6_%s_%s_raw.json" % (tag, s.stamp)), log=lambda m: None, on_item=None)
    base, cc = EC.class_counts(json.load(open(BASE_EL, encoding="utf-8"))["items"]), EC.class_counts(r.get("items"))
    lk = lambda d: sum(v for k, v in d.items() if "haslooseends" in k)                       # noqa: E731
    o = {"n": r.get("n_reported"), "items": len(r.get("items") or []), "base_items": sum(base.values()), "loose": lk(cc), "base_loose": lk(base),
         "errors": (r.get("errors") or [])[:2]}
    s.fact("EL %s TOTAL %s (bed %s), wire has loose ends %s (bed %s), window N %s, errors %s" % (tag, o["items"], o["base_items"], o["loose"],
           o["base_loose"], o["n"], o["errors"]))
    return o
def cross(W, x, snk):
    tag, src = x["tag"], int(x["src"])
    c0, w0, lt0 = s.census_snapshot(), set(g.uids(W, "Wire")), set(g.uids(W, "LoopTunnel"))
    cw = s._op("connect_term_uid", lambda: g.connect_term_uid(W, snk, src), "%s #%s <- #%s" % (tag, snk, src))
    res = cw["result"] or {}
    if not s.gate("%s connect_term_uid op err '' (no fallback route)" % tag, DRY or (res and not cw["err"] and not res.get("err")), cw) or DRY:
        return DRY
    c1, wn = s.census_snapshot(), sorted(set(g.uids(W, "Wire")) - w0)
    new, rows = dict((u, c1[u]) for u in set(c1) - set(c0)), terms(W)
    tun = dict((u, {"class": c, "owner": owner(W, u), "faces": [row(r) for r in rows if int(r["owner_uid"]) == u]})
               for u, c in new.items() if "Tunnel" in c)
    for u in sorted(set(g.uids(W, "LoopTunnel")) - lt0):
        t = g.tunnels(W, g._uid_index(W, "LoopTunnel", u))
        tun.setdefault(u, {"owner": owner(W, u)}).update(index_mode=t["index_mode"], uid_echo=t["uid"])
    o = {"op": res, "census": by_class(c0, c1), "gone": sorted(set(c0) - set(c1)), "new_wires": wn, "tunnels": tun,
         "wires_before": wires_read(W, wn), "es": g.exec_state(W)}
    s.fact("CENSUS %s %s" % (tag, json.dumps(o["census"], sort_keys=True)))
    s.fact("%s Is Broken? %s; tunnels %s; wires BEFORE RemoveLooseEnds %s; ES %s" % (tag, res.get("broken"), json.dumps(tun, sort_keys=True,
           default=str), o["wires_before"], o["es"]))
    c4, rle = s.census_snapshot(), {}
    for w in wn:
        rle[w] = g.wire_remove_loose_ends(W, w)
        s.gate("%s R RemoveLooseEnds w%s echo == uid, err ''" % (tag, w), rle[w]["echo"] == w and not rle[w]["err"], rle[w])
    c5 = s.census_snapshot()
    o.update(rle=rle, census_rle={"new": by_class(c4, c5), "gone": by_class(c5, c4)}, wires_after=wires_read(W, wn), es_after=g.exec_state(W))
    s.fact("CENSUS-RLE %s %s; RLE %s; wires AFTER %s; ES %s" % (tag, json.dumps(o["census_rle"], sort_keys=True), rle, o["wires_after"], o["es_after"]))
    OUT[tag] = o
    return True
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
    m3 = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, f3[2], "Max & Min", (60, 40)), "Max & Min -> frame 3")["result"]
    m2 = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, f3[1], "Max & Min", (60, 40)), "Max & Min -> frame 2")["result"]
    ia = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, f3[1], "Index Array", (60, 160), donor={"donor": W, "uid": PL["ia_donor_uid"]}),
               "Index Array (#%s) -> frame 2" % PL["ia_donor_uid"])["result"]
    rows = terms(W)
    pick = lambda u, src, nm: dict((int(r["term_uid"]), r) for r in rows if int(r["owner_uid"]) == int(u or 0) and bool(r["is_source"]) == src and str(r["term_name"]) == nm)  # noqa: E731
    srcs = [dict((int(r["term_uid"]), r) for r in rows if int(r["term_uid"]) == int(x["src"]) and bool(r["is_source"])
                 and int(r["frame_diagram"]) == int(x["src_frame"])) for x in XS]
    snks = [pick(m3, False, "x"), pick(m2, False, "x"), pick(ia, False, "array")]
    ok = DRY or all(len(v) == 1 for v in srcs + snks)
    if not s.gate("S0 one source (dedup by term uid, on its frame) + one sink terminal per crossing", ok, [[len(v) for v in srcs], [len(v) for v in snks]]):
        return s.dump()
    for x, sk in zip(XS, snks):
        if not cross(W, x, 0 if DRY else list(sk)[0]):
            break
    if not DRY:
        OUT["el_end"] = errlist(W, "cross_end")
    s.gate("X bed md5 unchanged", K.md5(DON) == DONM, K.md5(DON))
    json.dump(OUT, open(os.path.join(HERE, "diag_c126_6_cross_out.json"), "w", encoding="utf-8"), default=str, indent=1)
    s.dump()
if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
