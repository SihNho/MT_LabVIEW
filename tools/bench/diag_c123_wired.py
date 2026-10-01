r"""diag_c123_wired - card 123-7 STEP 1 (PD248(b)(d), brief_123-7.md): ONE LabVIEW run on ONE never-saved byte copy of the P2b bed
(plan diag_c123_wired_plan.json). EXISTING TOOLS (checked): gscript.case_wired/struct_copy_nested (card 123-5) now purge their junk
Invoke (gscript._purge_new_invokes); gscript.term_index replaces the bench tidx helpers' silent index-0 fallback; stagekit
net_sources (OpWireSource_v5 walk) counts a wire's terminals; stagekit connect_from_wire (OpConnectFromWire_v0) carries the ORDERED
Is Broken? readback (NAMES.md:1088-1094). Donor DonorCase_v0.vi reused (no rebuild). No new op VI.
PREDICTION (gates): K0 donor md5 df825c18. S1a E1 'x' <- #6810 by connect_nested_v1: source wire == 3747, E1 x wire == 3747,
w3747 terminals +1. S1a2 E2 'x' <- w3747 by connect_from_wire: UID 2 == 3747, Is Broken? False, E2 x wire == 3747, terminals +1 again.
S1b term_index(unknown name) -> ValueError. S1c case_wired: CaseStructure +1 owned by #639, Diagram +2, frames {False, True},
selector wire == E1 'x = y?' wire != 0, invoke_left [], new-object census has NO Invoke (Invoke uid set unchanged). X bed md5 unchanged.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c123_wired.log -- py -u tools/bench/diag_c123_wired.py"""
import json, os, sys, time                                                                  # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K                                                                        # noqa: E402
g = K.g
PL = json.load(open(os.path.join(HERE, "diag_c123_wired_plan.json"), encoding="utf-8"))
BED, BEDM, LP, DN, EQ, BN, CA = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"], PL["loop"], PL["donor"], PL["eq"], PL["bufnum"], PL["case"]
DON, OUTJ, SV, OM = os.path.join(g.CLAUDEDEV, DN["file"]), os.path.join(HERE, "diag_c123_wired.json"), os.path.join(HERE, "scratch_verify"), os.path.join(HERE, "opmodels", "case_wired.json")
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(BED, BEDM, "scratch_c123_wired", preload=False, deadline_min=17, reserve_s=150, out_json=OUTJ, task="card 123-7")
NC = K.mod("build_opconnectnested_v1")
OUT = {}
def ti(W, node, name, src):
    return s.safe("term_index #{0} {1!r}".format(node, name), lambda: g.term_index(W, LP["body"], node, name, src), (0, 0, 0, {}))[0]
def nsinks(w):
    r = s.net_sources(w, n=40) or {}
    return len([x for x in (r.get("walk") or []) if isinstance(x, dict) and x.get("owner_uid") and not x.get("err")]), r
def objs(W):
    return s.safe("objs", lambda: dict((int(o["uid"]), o["class"]) for o in g.report_all(W, "GObject")), {})[0] or {}
def delta(o0, o1):
    nw = set(o1) - set(o0)
    return dict((c, sum(1 for u in nw if o1[u] == c)) for c in set(o1[u] for u in nw))
def s1(W):
    e1 = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, LP["body"], EQ["prim"], tuple(EQ["pos"]), donor={"donor": W, "uid": EQ["uid"]}), "Equal? E1 $work").get("result")
    bd, bn, bt, brow = ti(W, BN["node"], BN["name"], True)
    xd, xn, xt, _x0 = ti(W, e1, EQ["x"], False)
    w = int((brow or {}).get("wire") or 0)
    k0, _ = nsinks(w)
    rx = s._op("connect_nested_v1", lambda: NC.connect_nested_v1(W, xd, xn, xt, bd, bn, bt, json.load(open(NC.MAP_OUT, encoding="utf-8"))), "E1 x <- #6810").get("result")
    _d, _n, _t, x1 = ti(W, e1, EQ["x"], False)
    k1, _ = nsinks(w)
    a = {"src_wire": w, "x_wire": int((x1 or {}).get("wire") or 0), "sinks_before": k0, "sinks_after": k1, "connect": rx, "src_row": brow}
    s.gate("S1a E1 #{0} x <- #6810 (connect_nested_v1): src wire == {1}, x wire == src wire, w terminals +1".format(e1, BN["wire"]),
           DRY or (w == BN["wire"] and a["x_wire"] == w and k1 == k0 + 1), a)
    e2 = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, LP["body"], EQ["prim"], tuple(EQ["pos2"]), donor={"donor": W, "uid": EQ["uid"]}), "Equal? E2 $work").get("result")
    yd, yn, yt, _y0 = ti(W, e2, EQ["x"], False)
    _k, walk = nsinks(w)
    si = [x.get("i") for x in (walk.get("walk") or []) if isinstance(x, dict) and x.get("is_source")]
    rc = s.connect_from_wire(yd, yn, yt, w, si[0] if si else 0).get("result")
    sub = rc[3] if isinstance(rc, tuple) and len(rc) > 3 else {}
    _d, _n, _t, x2 = ti(W, e2, EQ["x"], False)
    k2, _ = nsinks(w)
    b = {"src_index": si, "connect": rc, "x_wire": int((x2 or {}).get("wire") or 0), "sinks_after": k2}
    s.gate("S1a2 E2 #{0} x <- w{1} (connect_from_wire): UID 2 == w, Is Broken? False, x wire == w, terminals +1".format(e2, w),
           DRY or (len(si) == 1 and int(sub.get("UID 2") or 0) == w and sub.get("Is Broken?") is False and b["x_wire"] == w and k2 == k1 + 1), b)
    neg = s.safe("negative term_index", lambda: g.term_index(W, LP["body"], e1, CA["bad_term"], True), None)
    s.gate("S1b term_index(unknown name) -> ValueError (no index-0 fallback)", DRY or "ValueError" in str(neg[1]), str(neg[1])[:300])
    i0 = set(g.uids(W, "Invoke")) if not DRY else set()
    o0 = objs(W)
    rec = s._op("case_wired", lambda: g.case_wired(W, LP["body"], e1, EQ["out"], tuple(CA["pos"]), donor={"donor": DON, "uid": DN["uid"]}), "case on #{0} <- E1 #{1}".format(LP["body"], e1))
    o1 = objs(W); nb = delta(o0, o1); r = rec.get("result") if isinstance(rec.get("result"), dict) else {}   # noqa: E702
    i1 = set(g.uids(W, "Invoke")) if not DRY else set()
    nm = dict(zip(r.get("names") or [], r.get("frames") or []))
    ok = bool(r) and not r.get("op_err") and r.get("selector_wire") and r.get("selector_wire") == r.get("src_wire") and not r.get("invoke_left") \
        and sorted(nm) == sorted(CA["want_names"]) and nb.get("CaseStructure") == 1 and nb.get("Diagram") == 2 and not nb.get("Invoke") and i1 == i0
    s.gate("S1c case_wired: CaseStructure +1, Diagram +2, frames {0}, selector wire == src wire, NO Invoke left".format(CA["want_names"]),
           DRY or ok, {"call": {k: v for k, v in r.items() if not k.startswith("terms")}, "new_by_class": nb, "invoke_delta": sorted(i1 - i0), "err": rec.get("err")})
    s.fact("CENSUS case_wired (after purge) {0}".format(json.dumps(nb, sort_keys=True)))
    OUT["s1"] = {"e1": e1, "e2": e2, "a": a, "a2": b, "negative": str(neg[1])[:300], "case": r, "new_by_class": nb, "fits": bool(ok), "frames_by_name": nm}
def body(_):
    s.start(); s.discard_work(); W = s.work                                                   # noqa: E702
    s.gate("K0 donor DonorCase_v0.vi md5 == {0}".format(DN["md5"]), DRY or K.md5(DON) == DN["md5"])
    s.safe("S1", lambda: s1(W))
    if not DRY:
        jd, x = lambda q, o: json.dump(o, open(q, "w", encoding="utf-8"), indent=1, default=str), OUT.get("s1") or {}
        p = os.path.join(SV, "gscript.case_wired_c123_7_{0}.json".format(s.stamp))
        jd(p, {"function": "gscript.case_wired (struct_copy_nested OpPrimCopyNested_v0 + connect_nested_v1 + case_frames + _purge_new_invokes)",
               "status": "PASS" if x.get("fits") else "FAIL", "t": time.time(), "card": "123-7", "log": "tools/bench/diag_c123_wired.log", "input_md5": BEDM, "s1": x})
        c = x.get("case") or {}
        jd(OM, {"schema": "opmodel/1", "op": "case_wired", "wrapper": "gscript.case_wired / stagexec create route 'case_wired'", "sim": {"same_diagram": True},
                "measured_on": PL["input"]["vi"] + " " + BEDM + " (never-saved byte copy)", "n_samples": 1, "verdict": "PASS" if x.get("fits") else "FAIL",
                "supersedes": "card 123-5 sample (pre-purge, Invoke +1)",
                "samples": [{"raw": os.path.relpath(p, HERE), "fits": bool(x.get("fits")), "target": {"diagram": LP["body"], "src_node": x.get("e1"), "src_term": EQ["out"]},
                             "common": {"new_objs_by_class": x.get("new_by_class"), "names": c.get("names"), "n_frames": len(c.get("frames") or []), "purged": c.get("purged")}}]})
        s.fact("RECORDS {0} {1}".format(p, OM))
    s.dump()
if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
