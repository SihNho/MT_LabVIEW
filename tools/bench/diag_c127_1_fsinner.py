r"""diag_c127_1_fsinner - card 127-1 STEP A (brief_127-1.md, PD257(d)): on a never-saved P3a byte copy, the 3-frame FS of
diag_c126_6_cross.py in case #22694's False frame; FIRST crossings exactly as 126-6 B2/B1 (connect_term_uid, then
wire_remove_loose_ends on every new wire): While #637 i #644 -> Max & Min x in FS frames[1]; BufNum #6897 -> frames[2]. Then the
4 P3b 2nd+ sinks (rat1/rar1/raf1 = i, latest = BufNum) as SAME-FRAME wires from that FS outer tunnel's INNER face:
connect_term_uid(next Max & Min x, inner-face term uid). Plan: diag_c127_1_fsinner_plan.json.
PRIOR ART: diag_c126_6_cross.py (FS build, cross reads, errlist), diag_c126_4_fs.py; gscript.case_frame_wire is CaseStructure-only
(case_inner_face raises on another owner, gscript.py:5163) so the inner face is read from OpAllTerms_v1 rows (owner = tunnel,
frame_diagram = frame, is_source) as 126-6's tunnel 'faces' showed (diag_c126_6_cross.log:50).
PREDICTION: K F1 F2 CEN S0 as 126-6; A_* census == plan predict (126-6 B2/B1); one new FS outer tunnel and ONE inner face on the
frame; 2nd sinks: op err '', census delta in {} / {Wire: 1}, FS outer tunnel count UNCHANGED. Is Broken?, joints, Error List are
MEASUREMENTS. Stops at the first prediction miss. X bed md5 unchanged, scratch deleted, LabVIEW gone.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/diag_c127_1_fsinner.log -- py -u tools/bench/diag_c127_1_fsinner.py"""
import json, os, sys                                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K; g = K.g                                                               # noqa: E402,E702
PL = json.load(open(os.path.join(HERE, "diag_c127_1_fsinner_plan.json"), encoding="utf-8"))
DON, DONM = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"]
DRY = bool(getattr(g.report_all, "_dry", False))
CASE, FF0, SP = PL["case"], PL["false_frame"], PL["second_predict"]
BASE_EL, OUT = os.path.join(HERE, PL["errorlist_base"]), {}
s = K.Stage(DON, DONM, "scratch_c127_1_fsinner", preload=False, deadline_min=42, reserve_s=150,
            out_json=os.path.join(HERE, "diag_c127_1_fsinner.json"), task="card 127-1 STEP A")
def dec(r):
    J = [list(x) for x in (r or {}).get("joints") or []]
    return {"joints": len(J), "loose": sum(1 for x in J if int(x[1]) & 0x100), "terms": sum(1 for x in J if int(x[1]) & 0x1),
            "free": [(i, list(x[0])) for i, x in enumerate(J) if int(x[2]) == 1 and not int(x[1]) & 0x1]}
def terms(W):
    import allterms
    return [] if DRY else allterms.read_terms(W, allterms.OP_ALLTERMS_V1)[0]
def row(r): return (r["owner_class"], r["owner_uid"], r["term_name"], r["is_source"], r["frame_diagram"], r["wire_uid"])
def by_class(c0, c1): return dict((c, sum(1 for u in set(c1) - set(c0) if c1[u] == c)) for c in set(c1[u] for u in set(c1) - set(c0)))
def nfst(c): return sum(1 for v in c.values() if v == "FlatSequenceOuterTunnel")
def wires_read(W, ws):
    cur = set(g.uids(W, "Wire"))
    return dict((w, dec(g.wire_joints(W, w)) if w in cur else "GONE") for w in ws)
def errlist(W, tag):
    import errorlist_check as EC
    EC._lv_imports(); R = {"gui_acts_outer": [], "errors": []}; EC.open_diagram(W, R)       # noqa: E702
    r = EC.E.read(W, os.path.join(HERE, "errorlist_c127_1_%s_%s_raw.json" % (tag, s.stamp)), log=lambda m: None, on_item=None)
    cc = EC.class_counts(r.get("items"))
    o = {"items": len(r.get("items") or []), "loose": sum(v for k, v in cc.items() if "haslooseends" in k), "errors": (r.get("errors") or [])[:2]}
    s.fact("EL %s TOTAL %s, wire has loose ends %s, errors %s" % (tag, o["items"], o["loose"], o["errors"]))
    return o
def wire(W, tag, snk, src, inner=None):
    c0, w0 = s.census_snapshot(), set(g.uids(W, "Wire"))
    srcw = sorted(set(int(r["wire_uid"] or 0) for r in terms(W) if int(r["term_uid"]) == src) - {0})
    cw = s._op("connect_term_uid", lambda: g.connect_term_uid(W, snk, src), "%s #%s <- #%s" % (tag, snk, src))
    res = cw["result"] or {}
    if not s.gate("%s connect_term_uid op err ''" % tag, DRY or (res and not cw["err"] and not res.get("err")), cw):
        return None
    if DRY:
        return {"dry": True}
    c1, wn = s.census_snapshot(), sorted(set(g.uids(W, "Wire")) - w0)
    rows = terms(W)
    ws = sorted(set(wn) | set(srcw) | set(int(r["wire_uid"] or 0) for r in rows if int(r["term_uid"]) == src) - {0})
    tun = dict((u, [row(r) for r in rows if int(r["owner_uid"]) == u]) for u in set(c1) - set(c0) if "Tunnel" in c1[u])
    o = {"op": res, "census": by_class(c0, c1), "gone": sorted(set(c0) - set(c1)), "new_wires": wn, "src_wires_before": srcw,
         "fs_outer_tunnels": [nfst(c0), nfst(c1)], "tunnels": tun, "before_rle": wires_read(W, ws)}
    s.fact("CENSUS %s %s" % (tag, json.dumps(o["census"], sort_keys=True)))
    s.fact("%s Is Broken? %s; FS outer tunnels %s -> %s; gone %s; new wires %s; tunnels %s" % (tag, res.get("broken"), o["fs_outer_tunnels"][0],
           o["fs_outer_tunnels"][1], o["gone"], wn, json.dumps(tun, default=str)))
    s.fact("%s wires BEFORE RemoveLooseEnds %s" % (tag, o["before_rle"]))
    c4, cur = s.census_snapshot(), set(g.uids(W, "Wire"))
    o["rle"] = dict((w, g.wire_remove_loose_ends(W, w)) for w in ws if w in cur)
    for w, r in o["rle"].items():
        s.gate("%s R RemoveLooseEnds w%s echo == uid, err ''" % (tag, w), r["echo"] == w and not r["err"], r)
    c5 = s.census_snapshot()
    o.update(census_rle={"new": by_class(c4, c5), "gone": by_class(c5, c4)}, after_rle=wires_read(W, ws), c0=c0, c1=c1)
    s.fact("CENSUS-RLE %s %s; wires AFTER %s; ES %s" % (tag, json.dumps(o["census_rle"], sort_keys=True), o["after_rle"], g.exec_state(W)))
    OUT[tag] = dict((k, v) for k, v in o.items() if k not in ("c0", "c1"))
    return o
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
    s._op("fs_add_frame", lambda: g.fs_add_frame(W, fs, 0, True), "after 0"); s._op("fs_add_frame", lambda: g.fs_add_frame(W, fs, 1, True), "after 1")  # noqa: E702
    f3 = [0, 0, 0] if DRY else g.fs_frames(W, fs)["frames"]
    s.census_gate("CEN census delta of FS copy + 2 Add Frame == FlatSequence 1 + Diagram 3", c0, s.census_snapshot(), {"FlatSequence": 1, "Diagram": 3})
    if not s.gate("F2 3 frames %s" % f3, len(f3) == 3, f3):
        return s.dump()
    mm = dict((k, [s._op("create_primitive_nested", lambda p=p: g.create_primitive_nested(W, f3[int(k)], "Max & Min", tuple(p)), "MM -> f%s %s" % (k, p))["result"]
                   for p in ps]) for k, ps in PL["sink_positions"].items())
    rows = terms(W)
    x = dict((k, [[int(r["term_uid"]) for r in rows if int(r["owner_uid"]) == int(u or 0) and not r["is_source"] and str(r["term_name"]) == "x"] for u in v]) for k, v in mm.items())
    if not s.gate("S0 one x per Max & Min %s" % x, DRY or all(len(t) == 1 for v in x.values() for t in v), x):
        return s.dump()
    xq = dict((k, [0 if DRY else t[0] for t in v]) for k, v in x.items())
    face = {}
    for a in PL["first"]:
        k = str(a["frame"]); o = wire(W, a["tag"], xq[k].pop(0), int(a["src"]))           # noqa: E702
        if o is None:
            return s.dump()
        if DRY:
            face[a["tag"]] = {"inner": [0]}; continue                                    # noqa: E702
        if not s.gate("%s census == 126-6 measured %s" % (a["tag"], a["predict"]), o["census"] == a["predict"], o["census"]):
            return s.dump()
        tn = [u for u in set(o["c1"]) - set(o["c0"]) if o["c1"][u] == "FlatSequenceOuterTunnel"]
        inn = [r for r in terms(W) if tn and int(r["owner_uid"]) == tn[0] and int(r["frame_diagram"]) == int(f3[a["frame"]]) and r["is_source"]]
        face[a["tag"]] = {"tunnel": tn, "inner": [int(r["term_uid"]) for r in inn], "inner_rows": [row(r) for r in inn], "frame_diagram": f3[a["frame"]]}
        s.fact("FACE %s %s" % (a["tag"], face[a["tag"]]))
        if not s.gate("%s one new FS outer tunnel, one inner face on frame #%s" % (a["tag"], f3[a["frame"]]), len(tn) == 1 and len(inn) == 1, face[a["tag"]]):
            return s.dump()
    OUT.update(faces=face, el_first=None if DRY else errlist(W, "first"))
    fk = dict((a["tag"], str(a["frame"])) for a in PL["first"])
    for b in PL["second"]:
        o = wire(W, b["tag"], xq[fk[b["of"]]].pop(0), face[b["of"]]["inner"][0])
        if o is None:
            break
        if DRY:
            continue
        OUT[b["tag"]].update(row=b["row"], el=errlist(W, b["tag"]))
        ok = o["census"] in SP["allowed_deltas"] and o["fs_outer_tunnels"][0] == o["fs_outer_tunnels"][1]
        if not s.gate("%s census in %s and FS outer tunnels unchanged" % (b["tag"], SP["allowed_deltas"]), ok, (o["census"], o["fs_outer_tunnels"])):
            break
    s.gate("X bed md5 unchanged", K.md5(DON) == DONM, K.md5(DON))
    json.dump(OUT, open(os.path.join(HERE, "diag_c127_1_fsinner_out.json"), "w", encoding="utf-8"), default=str, indent=1)
    s.dump()
if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
