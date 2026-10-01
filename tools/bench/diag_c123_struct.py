r"""diag_c123_struct - card 123-5 S1/S2 (PD246(c) A4/A5, PD247(c), brief_123-5.md): ONE LabVIEW run on ONE never-saved byte copy of the P2b bed
(plan diag_c123_struct_plan.json). EXISTING TOOLS FIRST (checked): case_in's selector is a panel control by label (PD247(c)); OpPrimCopyNested_v0
(GObject.Move duplicate) copies ANY object onto a nested diagram; connect_nested_v1 wires same-diagram triples; case_frames reads frames. So S1 =
NEW verbs gscript.struct_copy_nested + case_wired on EXISTING ops, donor DonorCase_v0.vi (build_case on a byte copy of OpCaseFrames_v1): no new op VI.
No Flat Sequence creator route exists (no FS donor, no frame-add op, no Diagrams[] reader op): S2 records facts only (Create Sequence.vi panel).
PREDICTION (gates): D1 donor case created, ES 1, saved. S1a Equal? on #639, x wire +1, y const wired. S1b bad source name -> ValueError, no new case.
S1c case_wired: CaseStructure +1 owned by #639, Diagram +2 (frames), op error '', wire delta 1, selector wire == Equal? output wire != 0,
frame names {False, True} on the two new frame Diagrams. X bed md5 unchanged.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c123_struct.log -- py -u tools/bench/diag_c123_struct.py"""
import json, os, shutil, sys, time                                                          # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K                                                                        # noqa: E402
g = K.g
PL = json.load(open(os.path.join(HERE, "diag_c123_struct_plan.json"), encoding="utf-8"))
BED, BEDM, LP, DN, EQ, BN, CA = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"], PL["loop"], PL["donor"], PL["eq"], PL["bufnum"], PL["case"]
DON, OUTJ, SV, OM = os.path.join(g.CLAUDEDEV, DN["file"]), os.path.join(HERE, "diag_c123_struct.json"), os.path.join(HERE, "scratch_verify"), os.path.join(HERE, "opmodels", "case_wired.json")
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(BED, BEDM, "scratch_c123_struct", preload=False, deadline_min=27, reserve_s=150, out_json=OUTJ, task="card 123-5")
NC, CC = K.mod("build_opconnectnested_v1"), K.mod("build_opcreateconstonterm_v0")
OUT = {}
def donor():
    os.path.exists(DON) and os.remove(DON); shutil.copyfile(os.path.join(g.CLAUDEDEV, DN["from"]), DON); g.open_panel(DON)   # noqa: E702
    c = s._op("build_case", lambda: g.build_case(DON, tuple(DN["pos"]), DN["selector_label"], (), tuple(DN["frames"])), "donor case").get("result") or {}
    cu = int(c.get("uid") or 0) if isinstance(c, dict) else 0
    fr = s.safe("donor frames", lambda: g.case_frames(DON, cu), {})[0] or {}
    s.gate("D1 donor case created on DonorCase_v0 top level #{0}, frames {1}".format(cu, fr.get("names")), bool(cu), fr)
    rec = {"case_uid": cu, "frames": fr}
    if s.gate("D2 donor ExecState 1 -> saved", g.exec_state(DON) == 1):
        g.save(DON); g.close_panel(DON); rec["md5"] = K.md5(DON); s.fact("DONOR RECORD {0}".format(json.dumps(rec, default=str)))   # noqa: E702
    return rec
def tidx(W, diag, node, pred):
    di = g._uid_index(W, "Diagram", diag); ni = g._node_index(W, di, node); u, rows = g.node_terms_uids(W, di, ni)   # noqa: E702
    t = [r for r in rows if pred(r)]
    return di, ni, (t[0]["i"] if t else 0), rows
def objs(W):
    return s.safe("objs", lambda: dict((int(o["uid"]), o["class"]) for o in g.report_all(W, "GObject")), {})[0] or {}
def delta(o0, o1):
    nw = set(o1) - set(o0)
    return dict((c, sum(1 for u in nw if o1[u] == c)) for c in set(o1[u] for u in nw))
def s1(W, dr):
    eq = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, LP["body"], EQ["prim"], tuple(EQ["pos"]), donor={"donor": W, "uid": EQ["uid"]}), "Equal? $work").get("result")
    xd, xn, xt, _r = s.safe("eq x", lambda: tidx(W, LP["body"], eq, lambda r: r["name"] == EQ["x"] and not r["is_source"]), (0, 0, 0, []))[0]
    bd, bn, bt, _r = s.safe("bufnum", lambda: tidx(W, LP["body"], BN["node"], lambda r: r["name"] == BN["name"] and r["is_source"]), (0, 0, 0, []))[0]
    rx = s._op("connect_nested_v1", lambda: NC.connect_nested_v1(W, xd, xn, xt, bd, bn, bt, json.load(open(NC.MAP_OUT, encoding="utf-8"))), "Equal? x <- BufNum").get("result")
    _d, yn, yt, _r = s.safe("eq y", lambda: tidx(W, LP["body"], eq, lambda r: r["name"] == EQ["y"] and not r["is_source"]), (0, 0, 0, []))[0]
    ry = s._op("create_const_on_term", lambda: CC.create_const_on_term(W, s.uid_index("WhileLoop", LP["uid"]), yn, yt, json.load(open(os.path.join(HERE, "opcreateconstonterm_labels.json"), encoding="utf-8")), value=EQ["y_value"]), "Equal? y const")
    s.gate("S1a Equal? #{0} on #{1}: x wire +1, y const wired".format(eq, LP["body"]), DRY or (bool(eq) and isinstance(rx, tuple) and rx[0] == 1 and not rx[2] and not (ry.get("result") or {}).get("err")), {"x": rx, "y": ry.get("result")})
    n0 = set(g.uids(W, "CaseStructure")) if not DRY else set()
    bad = s.safe("negative", lambda: g.case_wired(W, LP["body"], eq, CA["bad_term"], tuple(CA["pos"]), donor={"donor": DON, "uid": dr.get("case_uid")}), None)
    s.gate("S1b bad source name -> ValueError, no new CaseStructure", DRY or ("ValueError" in str(bad[1]) and set(g.uids(W, "CaseStructure")) == n0), str(bad[1])[:300])
    o0 = objs(W)
    rec = s._op("case_wired", lambda: g.case_wired(W, LP["body"], eq, EQ["out"], tuple(CA["pos"]), donor={"donor": DON, "uid": dr.get("case_uid")}), "case on #{0} <- Equal? #{1}".format(LP["body"], eq))
    o1 = objs(W); nb = delta(o0, o1); r = rec.get("result") if isinstance(rec.get("result"), dict) else {}   # noqa: E702
    nm = dict(zip(r.get("names") or [], r.get("frames") or []))
    ok = bool(r) and r.get("wire_delta") == 1 and not r.get("op_err") and r.get("selector_wire") and r.get("selector_wire") == r.get("src_wire") \
        and sorted(nm) == sorted(CA["want_names"]) and sorted(nm.values()) == sorted(r.get("new_diagrams") or []) and nb.get("CaseStructure") == 1 and nb.get("Diagram") == 2
    s.gate("S1c case_wired: CaseStructure +1 on #{0}, Diagram +2, wire +1, selector wire == Equal? output wire, frames {1}".format(LP["body"], CA["want_names"]), DRY or ok, {"call": {k: v for k, v in r.items() if not k.startswith("terms")}, "new_by_class": nb, "err": rec.get("err")})
    s.row("S1c selector terminals before/after", {"before": r.get("terms_before"), "after": r.get("terms_after")})
    OUT["s1"] = {"eq": eq, "x": rx, "y": ry.get("result"), "negative": str(bad[1])[:300], "case": r, "new_by_class": nb, "fits": bool(ok), "frames_by_name": nm}
    if not DRY and nm:
        fe = s.safe("frame dup check", lambda: g.create_primitive_nested(W, nm.get("False") or 0, EQ["prim"], (40, 40), donor={"donor": W, "uid": EQ["uid"]}), None)
        s.row("S1d a node placed into the False frame (frame diagram addressable)", {"uid": fe[0], "err": str(fe[1])[:200]})
def body(_):
    s.start(); s.discard_work(); W = s.work                                                   # noqa: E702
    dr = {} if DRY else donor()
    if not DRY:
        _c = s.close; s.close = lambda expect_files=None: _c(expect_files=[DN["file"]])      # noqa: E702 - the saved donor is this run's one intended file
    s.safe("S1", lambda: s1(W, dr))
    fl = s.safe("S2 Create Sequence.vi panel", lambda: g.fp_labels(PL["s2"]["erdos_seq"], max_n=30), [])[0] or []
    s.fact("S2 FACT Erdos Miller Create Sequence.vi front panel (index, label, is_indicator): {0}".format(fl)); OUT["s2"] = {"create_sequence_panel": fl}   # noqa: E702
    if not DRY:
        jd, x = lambda q, o: json.dump(o, open(q, "w", encoding="utf-8"), indent=1, default=str), OUT.get("s1") or {}
        p = os.path.join(SV, "gscript.case_wired_c123_{0}.json".format(s.stamp))
        jd(p, {"function": "gscript.case_wired (struct_copy_nested OpPrimCopyNested_v0 + connect_nested_v1 OpConnectNested_v1 + case_frames)", "status": "PASS" if x.get("fits") else "FAIL",
               "t": time.time(), "card": "123-5", "log": "tools/bench/diag_c123_struct.log", "input_md5": BEDM, "donor": dict(dr, path=DON), "s1": x, "s2": OUT["s2"]})
        c = x.get("case") or {}
        jd(OM, {"schema": "opmodel/1", "op": "case_wired", "wrapper": "gscript.case_wired / stagexec create route 'case_wired'", "sim": {"same_diagram": True},
                "measured_on": PL["input"]["vi"] + " " + BEDM + " (never-saved byte copy)", "n_samples": 1, "verdict": "PASS" if x.get("fits") else "FAIL",
                "samples": [{"raw": os.path.relpath(p, HERE), "fits": bool(x.get("fits")), "target": {"diagram": LP["body"], "src_node": x.get("eq"), "src_term": EQ["out"]},
                             "common": {"new_objs_by_class": x.get("new_by_class"), "wire_delta": c.get("wire_delta"), "names": c.get("names"), "n_frames": len(c.get("frames") or [])}}]})
        s.fact("RECORDS {0} {1}".format(p, OM))
    s.dump()
if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
