r"""diag_c123_casetun - card 123-9 STEP 1 (PD249(d), brief_123-9.md): ONE LabVIEW run on ONE never-saved byte copy of the P2b bed
(plan diag_c123_casetun_plan.json). EXISTING TOOLS (checked): gscript.case_wired (123-7, purge inside), create_primitive_nested
($work donor, 123-7), term_index, connect_nested_v1 (cross-diagram writer), stagekit net_sources / connect_from_wire (ordered
Is Broken? readback, NAMES.md:1088-1094), node_terms_uids. NO verb addresses a SelectorTunnel INNER face (stagexec FACE_ROUTES:
owner Terms[] for OUTER faces only) - so S1-8 only tries a Terminals[] entry of the case that the read itself shows; none = FAIL fact.
PREDICTION (gates): K0 donor md5 df825c18. C case_wired: frames {False, True}. T-in: I1 'x' <- #6810 across the border: wire delta
+2 (outer + inner wire), SelectorTunnel +1, I1 x wired, Is Broken? False on the ordered second pass. T-out: I2 'x' <- I1 'x+1':
SelectorTunnel +1 more, I2 x wired, Is Broken? False. F case Terminals[] after = selector + 2 outer faces (+ inner faces if listed).
P True-frame pass-through: an unwired source + an unwired sink entry exist on the case's Terminals[] and connect_nested_v1 wires them.
X bed md5 unchanged, LabVIEW gone.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c123_casetun.log -- py -u tools/bench/diag_c123_casetun.py"""
import json, os, sys, time                                                                  # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K                                                                        # noqa: E402
g = K.g
PL = json.load(open(os.path.join(HERE, "diag_c123_casetun_plan.json"), encoding="utf-8"))
BED, BEDM, LP, DN, EQ, IN, BN, CA = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"], PL["loop"], PL["donor"], PL["eq"], PL["inc"], PL["bufnum"], PL["case"]
DON, OUTJ, SV = os.path.join(g.CLAUDEDEV, DN["file"]), os.path.join(HERE, "diag_c123_casetun.json"), os.path.join(HERE, "scratch_verify")
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(BED, BEDM, "scratch_c123_casetun", preload=False, deadline_min=17, reserve_s=150, out_json=OUTJ, task="card 123-9")
NC = K.mod("build_opconnectnested_v1")
LAB = lambda: json.load(open(NC.MAP_OUT, encoding="utf-8"))                                   # noqa: E731
OUT = {}
def ti(W, diag, node, name, src):
    return s.safe("term_index #{0} {1!r}".format(node, name), lambda: g.term_index(W, diag, node, name, src), (0, 0, 0, {}))[0]
def objs(W):
    return s.safe("objs", lambda: dict((int(o["uid"]), o["class"]) for o in g.report_all(W, "GObject")), {})[0] or {}
def delta(o0, o1):
    nw = set(o1) - set(o0)
    return dict((c, sum(1 for u in nw if o1[u] == c)) for c in set(o1[u] for u in nw))
def wire_of(W, diag, node, name, src):
    return int(((ti(W, diag, node, name, src) or (0, 0, 0, {}))[3] or {}).get("wire") or 0)
def second_pass(W, diag, node, name, w, tag):
    walk = (s.net_sources(w, n=40) or {}).get("walk") or []
    si = [x.get("i") for x in walk if isinstance(x, dict) and x.get("is_source")]
    d, n, t, _r = ti(W, diag, node, name, False)
    rc = s.connect_from_wire(d, n, t, w, si[0] if si else 0).get("result")
    sub = rc[3] if isinstance(rc, tuple) and len(rc) > 3 else {}
    return {"tag": tag, "wire": w, "src_index": si, "uid2": sub.get("UID 2"), "is_broken": sub.get("Is Broken?"),
            "walk": [{k: x.get(k) for k in ("i", "owner_class", "owner_uid", "is_source", "term_uid", "term_class", "diagram_uid", "err") if k in x} for x in walk if isinstance(x, dict)]}
def case_rows(W, c):
    di = g._uid_index(W, "Diagram", LP["body"])
    return g.node_terms_uids(W, di, g._node_index(W, di, c)), di
def s1(W):
    o0 = objs(W)
    e1 = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, LP["body"], EQ["prim"], tuple(EQ["pos"]), donor={"donor": W, "uid": EQ["uid"]}), "Equal? E1 $work").get("result")
    rec = s._op("case_wired", lambda: g.case_wired(W, LP["body"], e1, EQ["out"], tuple(CA["pos"]), donor={"donor": DON, "uid": DN["uid"]}), "case on #639 <- E1").get("result") or {}
    nm = dict(zip(rec.get("names") or [], rec.get("frames") or []))
    c = rec.get("case")
    s.gate("C case_wired: frames {0}".format(CA["want_names"]), DRY or sorted(nm) == sorted(CA["want_names"]), {"names": nm, "case": c}, fatal=True)
    fF, fT = int(nm.get("False") or 0), int(nm.get("True") or 0)
    (_e0, rows0), _di = s.safe("case rows before", lambda: case_rows(W, c), ((0, []), 0))[0]
    oa = objs(W)
    i1 = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, fF, IN["prim"], tuple(IN["pos_in"]), donor={"donor": W, "uid": IN["uid"]}), "Increment I1 in False #{0}".format(fF)).get("result")
    xd, xn, xt, _x = ti(W, fF, i1, IN["x"], False)
    bd, bn, bt, _b = ti(W, LP["body"], BN["node"], BN["name"], True)
    w0 = s.count("Wire")
    rin = s._op("connect_nested_v1", lambda: NC.connect_nested_v1(W, xd, xn, xt, bd, bn, bt, LAB()), "I1 x <- #6810 (input tunnel)").get("result")
    ob = objs(W); dIn = delta(oa, ob); wIn = s.count("Wire") - w0                              # noqa: E702
    wx = wire_of(W, fF, i1, IN["x"], False)
    s.gate("T-in I1 #{0} x <- #6810 across the case border: SelectorTunnel +1, I1 x wired".format(i1), DRY or (dIn.get("SelectorTunnel") == 1 and wx != 0),
           {"connect": rin, "new_by_class": dIn, "wire_delta": wIn, "x_wire": wx})
    i2 = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, LP["body"], IN["prim"], tuple(IN["pos_out"]), donor={"donor": W, "uid": IN["uid"]}), "Increment I2 on #639").get("result")
    sd, sn_, st_, _s = ti(W, LP["body"], i2, IN["x"], False)
    qd, qn, qt, _q = ti(W, fF, i1, IN["out"], True)
    w1 = s.count("Wire")
    rout = s._op("connect_nested_v1", lambda: NC.connect_nested_v1(W, sd, sn_, st_, qd, qn, qt, LAB()), "I2 x <- I1 x+1 (output tunnel)").get("result")
    oc = objs(W); dOut = delta(ob, oc); wOut = s.count("Wire") - w1                             # noqa: E702
    w2x = wire_of(W, LP["body"], i2, IN["x"], False)
    s.gate("T-out I2 #{0} x <- I1 x+1 across the border: SelectorTunnel +1, I2 x wired".format(i2), DRY or (dOut.get("SelectorTunnel") == 1 and w2x != 0),
           {"connect": rout, "new_by_class": dOut, "wire_delta": wOut, "x_wire": w2x})
    p_in = second_pass(W, fF, i1, IN["x"], wx, "I1 x (inner face of the input tunnel, False)")
    p_out = second_pass(W, LP["body"], i2, IN["x"], w2x, "I2 x (outer face of the output tunnel)")
    s.gate("B Is Broken? False on both ordered second passes", DRY or (p_in["is_broken"] is False and p_out["is_broken"] is False), {"in": p_in, "out": p_out})
    wq = wire_of(W, fF, i1, IN["out"], True)
    p_q = {"wire": wq, "walk": [{k: x.get(k) for k in ("i", "owner_class", "owner_uid", "is_source", "term_uid", "term_class", "diagram_uid") if k in x}
                                for x in ((s.net_sources(wq, n=40) or {}).get("walk") or []) if isinstance(x, dict)]}
    (_e1, rows1), di = s.safe("case rows after", lambda: case_rows(W, c), ((0, []), 0))[0]
    sel = int(rec.get("selector_term") or 0)
    rest = [r for r in rows1 if int(r.get("uid") or 0) != sel and not int(r.get("wire") or 0)]
    srcs, snks = [r for r in rest if r["is_source"]], [r for r in rest if not r["is_source"]]
    s.fact("CASE TERMS before {0} / after {1}: {2}".format(len(rows0), len(rows1), json.dumps(rows1, default=str)[:1500]))
    rt = None
    if (len(srcs) == 1 and len(snks) == 1) or DRY:
        cn = g._node_index(W, di, c)
        ki, ko = (0, 0) if DRY else (int(snks[0]["i"]), int(srcs[0]["i"]))
        rt = s._op("connect_nested_v1", lambda: NC.connect_nested_v1(W, di, cn, ki, di, cn, ko, LAB()), "True pass-through via case Terms[]").get("result")
    (_e2, rows2), _d = s.safe("case rows final", lambda: case_rows(W, c), ((0, []), 0))[0]
    s.gate("P True-frame pass-through: one unwired source + one unwired sink on the case's Terminals[] and connect_nested_v1 wires them",
           DRY or (rt is not None and isinstance(rt, tuple) and int(rt[0] or 0) == 1 and not rt[2]),
           {"unwired_sources": srcs, "unwired_sinks": snks, "connect": rt, "rows_final": rows2})
    nb = delta(o0, objs(W))
    s.fact("CENSUS casetun total {0}".format(json.dumps(nb, sort_keys=True)))
    OUT["s1"] = {"e1": e1, "case": {k: v for k, v in rec.items() if not k.startswith("terms")}, "frames": nm, "i1": i1, "i2": i2,
                 "tin": {"connect": rin, "new_by_class": dIn, "wire_delta": wIn, "x_wire": wx}, "tout": {"connect": rout, "new_by_class": dOut, "wire_delta": wOut, "x_wire": w2x},
                 "pass_in": p_in, "pass_out": p_out, "inc_out_wire": p_q, "case_rows_before": rows0, "case_rows_after": rows1, "case_rows_final": rows2,
                 "true_connect": rt, "census": nb}
def body(_):
    s.start(); s.discard_work(); W = s.work                                                   # noqa: E702
    s.gate("K0 donor DonorCase_v0.vi md5 == {0}".format(DN["md5"]), DRY or K.md5(DON) == DN["md5"])
    s.safe("S1", lambda: s1(W))
    if not DRY:
        p = os.path.join(SV, "gscript.case_data_tunnel_c123_9_{0}.json".format(s.stamp))
        json.dump({"function": "case data tunnels by connect_nested_v1 across a case_wired border + True inner->inner", "t": time.time(), "card": "123-9",
                   "log": "tools/bench/diag_c123_casetun.log", "input_md5": BEDM, "s1": OUT.get("s1")}, open(p, "w", encoding="utf-8"), indent=1, default=str)
        s.fact("RECORDS {0}".format(p))
    s.dump()
if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
