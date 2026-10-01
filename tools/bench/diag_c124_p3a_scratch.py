r"""diag_c124_p3a_scratch - card 124-5 decision 3 (brief_124-4.md 'Scratch proof'): ONE LabVIEW run on ONE never-saved byte copy of the
P2b bed (plan diag_c124_p3a_scratch_plan.json). EXISTING TOOLS (checked): stagekit add_sr_row (add_shift_reg + shift_reg_left),
gscript.sr_init_const (123-3, route const_sr), create_primitive_nested ($work donors, 123-3/123-9), case_wired (123-7, purge inside),
term_index, case_frames, case_inner_face / case_frame_wire / connect_term_uid (124-1; connect_term_uid purges since 124-5), allterms
OpAllTerms_v1 frame_diagram (a register's inner face is a terminal, not a Nodes[] entry - result_124-3.json). No new op VI.
PREDICTION (gates): K0 donors md5. A1 one new bare sink on #637. A2 face wired, op err ''. A3 frames {False, True}. A5 exactly one
left inner source + one right inner sink on #639. R1/R2: wire != 0, Is Broken? False, ONE new tunnel owned by the case, one inner
face per frame, Invoke +0. R3 (True)/R4 (False): wire != 0, Is Broken? False, Invoke +0; R4's branch is a ROW (measured, not gated).
X bed md5 unchanged, scratch deleted, LabVIEW gone.
    py tools/bgrun.py --material --max-min 25 --log tools/bench/diag_c124_p3a_scratch.log -- py -u tools/bench/diag_c124_p3a_scratch.py"""
import json, os, sys, time                                                                  # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K                                                                        # noqa: E402
g = K.g
PL = json.load(open(os.path.join(HERE, "diag_c124_p3a_scratch_plan.json"), encoding="utf-8"))
BED, BEDM, LP, SD, CD, EQ, IN, QR = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"], PL["loop"], PL["sr_donor"], PL["case_donor"], PL["eq"], PL["inc"], PL["qr"]
OUTJ, SV = os.path.join(HERE, "diag_c124_p3a_scratch.json"), os.path.join(HERE, "scratch_verify")
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(BED, BEDM, "scratch_c124_p3a", preload=False, deadline_min=22, reserve_s=150, out_json=OUTJ, task="card 124-5")
OUT = {}
objs = lambda W: s.safe("objs", lambda: s.census_snapshot(W), {})[0] or {}                    # noqa: E731
delta = lambda o0, o1: dict((c, sum(1 for u in set(o1) - set(o0) if o1[u] == c)) for c in set(o1[u] for u in set(o1) - set(o0)))   # noqa: E731
inv = lambda W: set(s.safe("Invoke uids", lambda: g.uids(W, "Invoke"), set())[0] or ())     # noqa: E731
def owned(W, owner):
    A = K.mod("allterms")
    rows = s.safe("OpAllTerms_v1", lambda: A.read_terms(W, A.OP_ALLTERMS_V1)[0], [])[0] or []
    return [{k: r.get(k) for k in ("term_uid", "is_source", "wire_uid", "frame_diagram", "owner_class")} for r in rows if int(r["owner_uid"]) == int(owner)]
def faces(W, tun, n):
    return [s.safe("case_inner_face #{0} f{1}".format(tun, k), lambda k=k: g.case_inner_face(W, tun, k), None)[0] for k in range(n)]
def tuid(W, diag, node, name, src):
    return int((s.safe("term_index #{0} {1!r}".format(node, name), lambda: g.term_index(W, diag, node, name, src), (0, 0, 0, {}))[0][3] or {}).get("uid") or 0)
def step(W, tag, fn):
    o0, i0 = objs(W), inv(W)
    rec = s._op("case_frame_wire" if tag[:2] in ("R3", "R4") else "connect_term_uid", fn, tag)
    o1, i1 = objs(W), inv(W)
    nb, di = delta(o0, o1), sorted(i1 - i0)
    s.fact("CENSUS {0} {1}".format(tag, json.dumps(nb, sort_keys=True)))
    s.fact("INVOKE {0} delta {1}".format(tag, di))
    return (rec.get("result") if isinstance(rec.get("result"), dict) else {}), nb, di, o1, rec.get("err")
def tunnel_row(W, tag, fn, case, n):
    r, nb, di, o1, err = step(W, tag, fn)
    new = [u for u, c in o1.items() if "Tunnel" in c and u not in OUT.get("seen", {})]
    OUT["seen"] = o1
    BD = K.mod("build_d1_v0")
    own = dict((u, s.safe("owner_of", lambda: list(BD.owner_of(W, u, strict=False)), None)[0]) for u in new)
    tun = new[0] if len(new) == 1 else 0
    fs = faces(W, tun, n) if tun else []
    rec = {"call": r, "err": err, "new_by_class": nb, "invoke_delta": di, "new_tunnels": [(u, o1[u]) for u in new], "owners": own,
           "faces_per_frame": fs, "tunnel_terms": owned(W, tun) if tun else []}
    ok = r.get("wire_uid") and r.get("broken") is False and tun and (own.get(tun) or [0, 0])[1] == case and all(fs) and not di
    s.gate("{0}: wire != 0, Is Broken? False, ONE new tunnel owned by case #{1}, one inner face per frame, Invoke +0".format(tag, case), DRY or ok, rec)
    OUT[tag.split()[0]] = dict(rec, fits=bool(ok))
    return tun
def frame_row(W, tag, fn):
    r, nb, di, _o1, err = step(W, tag, fn)
    ok = r.get("wire_uid") and r.get("broken") is False and not di
    s.gate("{0}: wire != 0, Is Broken? False, Invoke +0".format(tag), DRY or ok, {"call": r, "err": err, "new_by_class": nb, "invoke_delta": di})
    OUT[tag.split()[0]] = {"call": r, "err": err, "new_by_class": nb, "invoke_delta": di, "fits": bool(ok)}
    return r
def lfaces(W):
    di = g._uid_index(W, "Diagram", LP["owner"]); e, rows = g.node_terms_uids(W, di, g._node_index(W, di, LP["uid"]))   # noqa: E702
    return dict((int(r["uid"]), r) for r in rows) if e == LP["uid"] else {}
def s1(W):
    f0 = s.safe("loop faces before", lambda: lfaces(W), {})[0] or {}
    rr = s.add_sr_row({"loop_uid": LP["uid"]}, tag="A1") or {}
    f1 = s.safe("loop faces after", lambda: lfaces(W), {})[0] or {}
    sk = [u for u, r in f1.items() if u not in f0 and not r["is_source"] and not int(r["wire"] or 0)]
    s.gate("A1 add_shift_reg on #{0}: exactly ONE new bare sink (left outer face)".format(LP["uid"]), DRY or len(sk) == 1, {"sr": rr, "new_bare_sinks": sk}, fatal=True)
    dn = {"donor": os.path.join(g.CLAUDEDEV, SD["file"]), "uid": SD["uid"]}
    a2 = s._op("wire_const_sr", lambda: g.sr_init_const(W, LP["uid"], sk[0] if sk else 0, LP["owner"], dn, tuple(SD["pos"])), "A2 sr_init_const I32 0").get("result") or {}
    s.gate("A2 sr_init_const: face wired, op err ''", DRY or (a2.get("face_wire") and not a2.get("op_err")), a2)
    e1 = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, LP["body"], EQ["prim"], tuple(EQ["pos"]), donor={"donor": W, "uid": EQ["uid"]}), "A3 Equal? E1").get("result")
    cw = s._op("case_wired", lambda: g.case_wired(W, LP["body"], e1, EQ["out"], tuple(CD["pos"]), donor={"donor": os.path.join(g.CLAUDEDEV, CD["file"]), "uid": CD["uid"]}), "A3 case <- E1").get("result") or {}
    names, c = list(cw.get("names") or []), cw.get("case")
    s.gate("A3 case_wired: frames {False, True}", DRY or sorted(names) == ["False", "True"], {"names": names, "frames": cw.get("frames"), "case": c, "purged": cw.get("purged")}, fatal=True)
    iF, iT = (names.index("False"), names.index("True")) if not DRY else (0, 1)
    fF = int((cw.get("frames") or [0, 0])[iF]) if not DRY else 0
    i1 = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, fF, IN["prim"], tuple(IN["pos"]), donor={"donor": W, "uid": IN["uid"]}), "A4 Increment I1 False").get("result")
    q1 = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, fF, QR["prim"], tuple(QR["pos"]), donor={"donor": W, "uid": QR["uid"]}), "A4 Q&R Q1 False").get("result")
    L, R = owned(W, rr.get("left") or 0), owned(W, rr.get("right") or 0)
    li = [x for x in L if x["is_source"] and int(x["frame_diagram"] or 0) == LP["body"]]
    ri = [x for x in R if not x["is_source"] and int(x["frame_diagram"] or 0) == LP["body"]]
    s.gate("A5 register inner faces on #{0}: one left source, one right sink".format(LP["body"]), DRY or (len(li) == 1 and len(ri) == 1), {"left": L, "right": R}, fatal=True)
    lu, ru = (int(li[0]["term_uid"]), int(ri[0]["term_uid"])) if not DRY else (0, 0)
    OUT.update(sr=rr, a2=a2, e1=e1, case=c, names=names, frames=cw.get("frames"), i1=i1, q1=q1, left_terms=L, right_terms=R, seen=objs(W), inv_start=sorted(inv(W)))
    x_u, x1_u = tuid(W, fF, i1, IN["x"], False), tuid(W, fF, i1, IN["out"], True)
    tin = tunnel_row(W, "R1 I1.x <- SR left inner", lambda: g.connect_term_uid(W, x_u, lu), c, len(names))
    tout = tunnel_row(W, "R2 SR right inner <- I1.x+1", lambda: g.connect_term_uid(W, ru, x1_u), c, len(names))
    frame_row(W, "R3 True: tin -> tout", lambda: g.case_frame_wire(W, c, iT, {"tunnel": tin}, {"tunnel": tout}))
    wb = [x["wire_uid"] for x in owned(W, tin) if int(x["frame_diagram"] or 0) == fF]
    r4 = frame_row(W, "R4 False: tin -> Q1.x", lambda: g.case_frame_wire(W, c, iF, {"tunnel": tin}, {"node": q1, "term": QR["x"]}))
    wa = [x["wire_uid"] for x in owned(W, tin) if int(x["frame_diagram"] or 0) == fF]
    OUT["R4"]["branch"] = s.row("R4 branch: tin False-face wire before/after vs Q1.x wire", {"before": wb, "after": wa, "q1x_wire": r4.get("wire_uid"),
                                "branched_existing": bool(wb) and r4.get("wire_uid") in wb})
    OUT["final"] = {"tin_terms": owned(W, tin), "tout_terms": owned(W, tout), "tin_faces": faces(W, tin, len(names)), "tout_faces": faces(W, tout, len(names)),
                    "left_terms": owned(W, rr.get("left") or 0), "right_terms": owned(W, rr.get("right") or 0), "invoke_total_delta": sorted(inv(W) - set(OUT["inv_start"]))}
    s.row("FINAL per-frame faces and register terminals", OUT["final"])
    s.gate("I Invoke +0 over R1-R4", DRY or not OUT["final"]["invoke_total_delta"], OUT["final"]["invoke_total_delta"])
    s.es("after R4")
def body(_):
    s.start(); s.discard_work(); W = s.work                                                   # noqa: E702
    for d in (SD, CD):
        s.gate("K0 donor {0} md5 == {1}".format(d["file"], d["md5"][:8]), DRY or K.md5(os.path.join(g.CLAUDEDEV, d["file"])) == d["md5"])
    s.safe("S1", lambda: s1(W))
    if not DRY:
        OUT.pop("seen", None)
        ok = all(OUT.get(k, {}).get("fits") for k in ("R1", "R2", "R3", "R4")) and not s.fails
        p = os.path.join(SV, "gscript.connect_term_uid_case_frame_wire_c124_5_{0}.json".format(s.stamp))
        json.dump({"function": "gscript.connect_term_uid (OpConnectTermUid_v0 + purge) and case_frame_wire on a case_wired case: register inner faces across the border, True/False inner wires",
                   "status": "PASS" if ok else "FAIL", "t": time.time(), "card": "124-5", "log": "tools/bench/diag_c124_p3a_scratch.log", "input_md5": BEDM, "s1": OUT},
                  open(p, "w", encoding="utf-8"), indent=1, default=str)
        s.fact("RECORDS {0}".format(p))
    s.dump()
if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
