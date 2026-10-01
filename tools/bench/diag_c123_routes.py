r"""diag_c123_routes - card 123-3 (PD246(e), brief_123-3.md): ONE LabVIEW run on ONE never-saved byte copy of the P2b bed (plan diag_c123_routes_plan.json).
EXISTING TOOLS FIRST (checked): no SR-init route (connect_route refused const -> register face); a loop face is its loop's Terminals[] entry (Addr._triple,
PD185) and OpConstWire_v1's sink ladder is TMSC(Node)->Terminals[], so S2 = NEW verbs gscript.sr_init_const/wire_const_sr + stagexec route 'const_sr' on EXISTING
ops (OpPrimCopyNested_v0, OpConstWire_v1): no new op VI. U32 donor: none -> DonorSRInit_v0.vi from EMPTY_v0. S1 reuses case_in, $work, connect_nested_v1, tunnels.
PREDICTION (S2, gates): D1-D3 donor values == plan, ES 1; per register: exactly ONE new bare sink on #637's Terminals[], wire delta 1, op error '',
face wire != 0, const owned by Diagram #686, value == plan, face type == I32 / U32. S1 = FACTS (ROW lines), never gated. X bed md5 unchanged.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/diag_c123_routes.log -- py -u tools/bench/diag_c123_routes.py"""
import json, os, shutil, sys, time                                                          # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K                                                                        # noqa: E402
g = K.g
PL = json.load(open(os.path.join(HERE, "diag_c123_routes_plan.json"), encoding="utf-8"))
BED, BEDM, LP, DN, DI = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"], PL["loop"], PL["donor_new"], PL["donor_i32"]
DON, OUTJ, SV, OM = os.path.join(g.CLAUDEDEV, DN["file"]), os.path.join(HERE, "diag_c123_routes.json"), os.path.join(HERE, "scratch_verify"), os.path.join(HERE, "opmodels", "sr_init_const.json")
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(BED, BEDM, "scratch_c123_routes", preload=False, deadline_min=42, reserve_s=180, out_json=OUTJ, task="card 123-3")
C, NC, BD, TB = K.mod("build_opcreateconstonterm_v0"), K.mod("build_opconnectnested_v1"), K.mod("build_d1_v0"), K.mod("build_track_v6_core")
TUNC, OUT = ("LoopTunnel", "Tunnel", "SelectorTunnel", "FlatSequenceOuterTunnel", "FlatSequenceInnerTunnel"), {"s2": [], "s1": {}}
def donor():
    import pythoncom; from win32com.client import VARIANT                                  # noqa: E401,E702
    os.path.exists(DON) and os.remove(DON); shutil.copyfile(os.path.join(g.CLAUDEDEV, DN["empty"]), DON); g.open_panel(DON)   # noqa: E702
    d0 = g.uids(DON, "Diagram"); g.while_loop(DON, (200, 200)); body = sorted(g.uids(DON, "Diagram") - d0)[0]   # noqa: E702
    lab, rec = json.load(open(os.path.join(HERE, "opcreateconstonterm_labels.json"), encoding="utf-8")), {}
    for k, (key, v) in enumerate(sorted(DN["values"].items())):
        w = g.create_primitive_nested(DON, body, DN["wait"], (40 + 160 * k, 60)); bi = g._uid_index(DON, "Diagram", body)   # noqa: E702
        ni = g._node_index(DON, bi, w); t = [r["i"] for r in g.node_terms_uid(DON, bi, ni)[1] if r["name"] == DN["ms_term"] and not r["is_source"]][0]   # noqa: E702
        rec[key] = C.create_const_on_term(DON, 0, ni, t, lab, value=VARIANT(pythoncom.VT_UI4, int(v)))["created_uid"]
    f0 = g.uids(DON, "ForLoop"); g.for_loop(DON, (200, 500)); uf = sorted(g.uids(DON, "ForLoop") - f0)[0]   # noqa: E702
    rec["i32_zero"] = g.create_const_loop_term(DON, "for_n", TB.walk(DON, 0)[uf][0], value=int(DN["i32_zero"]))["created_uid"]
    g.create_const_loop_term(DON, "while_cond", 0)
    got, want = dict((k, g.read_const_value(DON, u)) for k, u in rec.items()), dict(DN["values"], i32_zero=DN["i32_zero"]); s.fact("DONOR READ {0}".format(json.dumps(got, default=str)[:900]))   # noqa: E702
    s.gate("D1 donor constants created {0}".format(rec), all(rec.values()), rec); s.gate("D2 donor values read back == plan {0}".format(want), all(got[k].get("value") == want[k] and not got[k].get("err") for k in rec))   # noqa: E702
    if s.gate("D3 donor ExecState 1 -> saved", g.exec_state(DON) == 1):
        g.save(DON); g.close_panel(DON); rec.update(md5=K.md5(DON), types=dict((k, got[k].get("type")) for k in got)); s.fact("DONOR RECORD {0}".format(rec))   # noqa: E702
    return rec
def faces(W):
    di = g._uid_index(W, "Diagram", LP["owner"]); e, rows = g.node_terms_uids(W, di, g._node_index(W, di, LP["uid"]))   # noqa: E702
    return dict((int(r["uid"]), r) for r in rows) if e == LP["uid"] else {}
def s2(W, case, dons):
    f0 = s.safe("faces before", lambda: faces(W), {})[0] or {}
    rr = s.add_sr_row({"loop_uid": LP["uid"]}, tag="S2-" + case["tag"])
    f1 = s.safe("faces after", lambda: faces(W), {})[0] or {}
    new = dict((u, r) for u, r in f1.items() if u not in f0); sk = [u for u, r in new.items() if not r["is_source"] and not int(r["wire"] or 0)]   # noqa: E702
    s.gate("S2-{0} add_shift_reg: exactly ONE new bare sink among #637's new Terminals[] entries".format(case["tag"]), DRY or len(sk) == 1, new)
    face = sk[0] if sk else 0
    dn = {"donor": os.path.join(g.CLAUDEDEV, DI["file"]), "uid": DI["uid"]} if case["donor"] == "donor_i32" else {"donor": DON, "uid": dons.get(case["donor"])}
    objs = lambda: s.safe("objs", lambda: dict((int(o["uid"]), o["class"]) for o in g.report_all(W, "GObject")), {})[0] or {}   # noqa: E731
    o0 = objs(); rec = s._op("wire_const_sr", lambda: g.sr_init_const(W, LP["uid"], face, LP["owner"], dn, tuple(case["pos"])), "sr_init_const #{0} face #{1} donor {2}".format(LP["uid"], face, dn))   # noqa: E702
    o1 = objs(); nbc = dict((c, sum(1 for u in set(o1) - set(o0) if o1[u] == c)) for c in set(o1[u] for u in set(o1) - set(o0)))   # noqa: E702
    res = rec.get("result") if isinstance(rec.get("result"), dict) else {}; cu = res.get("const_uid")   # noqa: E702
    cv, tt = s.safe("read_const_value", lambda: g.read_const_value(W, cu), {})[0] or {}, s.safe("read_term_type face", lambda: g.read_term_type(W, face), {})[0] or {}
    own, ty = s.safe("owner_of const", lambda: list(BD.owner_of(W, cu, strict=False)), None)[0], (tt.get("types") or {}).get("top_name") if isinstance(tt, dict) else None
    S = {"tag": case["tag"], "register": rr if isinstance(rr, dict) else None, "new_entries": new, "new_by_class": nbc, "face": face, "donor": dn, "call": res, "op_err": rec.get("err"),
         "const_value": cv.get("value"), "const_type": cv.get("type"), "const_route": cv.get("route"), "face_type": ty, "const_owner": own}
    ok = bool(res) and res.get("wire_delta") == 1 and not res.get("op_err") and res.get("face_wire") and own == ["Diagram", LP["owner"]] \
        and cv.get("value") == case["want_value"] and ty == case["want_type"]
    s.gate("S2-{0} SR init: wire +1, op err '', face wired, const on #{1}, value {2}, face type {3}".format(case["tag"], LP["owner"], case["want_value"], case["want_type"]), DRY or ok, S)
    OUT["s2"].append(dict(S, fits=bool(ok)))
def tidx(W, diag, node, pred):
    di = g._uid_index(W, "Diagram", diag); ni = g._node_index(W, di, node); u, rows = g.node_terms_uids(W, di, ni)   # noqa: E702
    t = [r for r in rows if pred(r)]
    return di, ni, (t[0]["i"] if t else 0), (t[0].get("uid") if t else 0), rows
def dup(W, diag, uid, pos, tag):
    return s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, diag, tag, pos, donor={"donor": W, "uid": uid}), "{0} $work #{1} -> #{2}".format(tag, uid, diag)).get("result")
def census(W):
    return dict((c, set(s.safe("uids " + c, lambda: g.uids(W, c), set())[0] or ())) for c in TUNC)
def s1(W):
    O, a, c = OUT["s1"], PL["s1a"], PL["s1c"]
    for k, p in enumerate(PL["s1b"]):
        u = dup(W, LP["body"], p["uid"], (PL["s1_pos"]["b"][0] + PL["s1_pos"]["dx"] * k, PL["s1_pos"]["b"][1]), p["prim"])
        cl = s.safe("class", lambda: [x for x in ("Comparison", "Function", "GrowableFunction", "Node") if u in g.uids(W, x)], [])[0]
        tr = s.safe("terms", lambda: tidx(W, LP["body"], u, lambda r: True)[4], [])[0]
        O.setdefault("b", []).append({"prim": p["prim"], "donor": p["uid"], "new": u, "classes": cl, "terms": tr}); s.row("S1b {0} $work dup".format(p["prim"]), {"uid": u, "classes": cl, "terms": tr})   # noqa: E702
    eq = O["b"][0]["new"] if O.get("b") else 0
    sink, c0 = dup(W, LP["body"], c["sink_donor"], tuple(PL["s1_pos"]["sink"]), "IndexArray"), census(W)
    dd, dn, dt, du, _r = s.safe("sink idx", lambda: tidx(W, LP["body"], sink, lambda r: not r["is_source"] and str(r["name"]).startswith(c["sink_prefix"])), (0, 0, 0, 0, []))[0]
    sd, sn, st, _u, _r = s.safe("src idx", lambda: tidx(W, c["src_diagram"], c["src_node"], lambda r: r.get("uid") == c["src_term"]), (0, 0, 0, 0, []))[0]
    rc = s._op("connect_nested_v1", lambda: NC.connect_nested_v1(W, dd, dn, dt, sd, sn, st, json.load(open(NC.MAP_OUT, encoding="utf-8"))), "S1c")
    c1 = census(W); nt = dict((k, sorted(c1[k] - c0[k])) for k in TUNC)
    own = dict((u, s.safe("own", lambda: list(BD.owner_of(W, u, strict=False)), None)[0]) for k in TUNC for u in nt[k])
    fl = [s.safe("tunnels", lambda: g.tunnels(W, g._uid_index(W, "LoopTunnel", u)), {})[0] for u in nt["LoopTunnel"] if (own.get(u) or [0, 0])[1] == PL["for"]["uid"]]
    ty = s.safe("sink type", lambda: g.read_term_type(W, du), {})[0] or {}
    O["c"] = {"call": rc, "new_tunnels": nt, "owners": own, "for_tunnels": fl, "sink_term": du, "sink_type": (ty.get("types") or {}).get("canon")}; s.row("S1c For output tunnel", O["c"])   # noqa: E702
    t0 = set(g.uids(W, "Tunnel")) if not DRY else set()
    ci = s._op("case_in", lambda: g.case_in(W, LP["body"], tuple(a["case_pos"]), a["selector_label"], tuple(a["frames"])), "S1a").get("result") or {}
    cu = ci.get("case") if isinstance(ci, dict) else 0
    O["a"] = {"case_in": ci, "new_tunnels": sorted(set(g.uids(W, "Tunnel")) - t0) if not DRY else []}
    xd, xn, xt, _u, _r = s.safe("eq x", lambda: tidx(W, LP["body"], eq, lambda r: r["name"] == a["eq_x"] and not r["is_source"]), (0, 0, 0, 0, []))[0]
    bd_, bn, bt, _u, _r = s.safe("bufnum", lambda: tidx(W, LP["body"], a["bufnum_node"], lambda r: r["name"] == a["bufnum_name"] and r["is_source"]), (0, 0, 0, 0, []))[0]
    O["a"]["x"] = s._op("connect_nested_v1", lambda: NC.connect_nested_v1(W, xd, xn, xt, bd_, bn, bt, json.load(open(NC.MAP_OUT, encoding="utf-8"))), "S1a x <- BufNum").get("result")
    cd, cn, _t, _u, crows = s.safe("case terms", lambda: tidx(W, LP["body"], cu, lambda r: True), (0, 0, 0, 0, []))[0]
    sel = [r for r in crows if not r["is_source"]]; _d, _n, et, _u, _r = s.safe("eq out", lambda: tidx(W, LP["body"], eq, lambda r: r["is_source"]), (0, 0, 0, 0, []))[0]   # noqa: E702
    O["a"].update(case_terms=crows, selector_candidates=sel)
    O["a"]["sel"] = s._op("connect_nested_v1", lambda: NC.connect_nested_v1(W, cd, cn, sel[0]["i"] if sel else 0, xd, xn, et, json.load(open(NC.MAP_OUT, encoding="utf-8"))), "S1a selector <- Equal?").get("result")
    fr = s.safe("frames after", lambda: g.case_frames(W, cu), {})[0] or {}; O["a"]["frames_after"] = fr   # noqa: E702
    nm = dict(zip(fr.get("names") or [], fr.get("frames") or []))
    O["a"]["frame_dup"] = dup(W, nm.get("False") or nm.get("0, Default") or 0, PL["s1b"][1]["uid"], (60, 60), a["frame_dup"]) if (nm or DRY) else None
    O["a"]["terms_after"] = s.safe("case terms after", lambda: tidx(W, LP["body"], cu, lambda r: True)[4], [])[0]; s.row("S1a case_in in While body", O["a"])   # noqa: E702
def body(_):
    s.start(); s.discard_work(); W = s.work                                                   # noqa: E702
    dons = {} if DRY else donor()
    if not DRY:
        _c = s.close; s.close = lambda expect_files=None: _c(expect_files=[DN["file"]])      # noqa: E702 - the saved donor is this run's one intended file
    for case in PL["sr_cases"]:
        s2(W, case, dons)
    s.safe("S1 measurements", lambda: s1(W))
    if not DRY:
        jd, ok, p = lambda q, o: json.dump(o, open(q, "w", encoding="utf-8"), indent=1, default=str), all(x["fits"] for x in OUT["s2"]), os.path.join(SV, "gscript.sr_init_const_c123_{0}.json".format(s.stamp))
        jd(p, {"function": "gscript.sr_init_const (stagexec 'const_sr' -> wire_const_sr, OpConstWire_v1)", "status": "PASS" if ok else "FAIL", "t": time.time(), "card": "123-3", "log": "tools/bench/diag_c123_routes.log", "input_md5": BEDM, "donor": dict(dons, path=DON), "samples": OUT["s2"]})
        jd(os.path.join(SV, "s1.routes_c123_{0}.json".format(s.stamp)), {"function": "S1 (case_in in a While body, $work donors, For output tunnel 'nested')", "status": "FACTS", "t": time.time(), "card": "123-3", "log": "tools/bench/diag_c123_routes.log", "s1": OUT["s1"]})
        jd(OM, {"schema": "opmodel/1", "op": "sr_init_const", "wrapper": "gscript.sr_init_const / stagexec connect_route 'const_sr'", "sim": {"same_diagram": True}, "measured_on": PL["input"]["vi"] + " " + BEDM + " (never-saved byte copy)",
                "n_samples": len(OUT["s2"]), "verdict": "PASS" if ok else "FAIL", "samples": [{"raw": os.path.relpath(p, HERE), "fits": x["fits"], "target": {"loop": LP["uid"], "face": x["face"], "diagram": LP["owner"]},
                "common": {"new_objs_by_class": x["new_by_class"], "new_loop_entries": x["new_entries"], "wire_delta": (x["call"] or {}).get("wire_delta"), "value": x["const_value"], "face_type": x["face_type"]}} for x in OUT["s2"]]})
        s.fact("RECORDS {0} {1}".format(p, OM))
    s.dump()
if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
