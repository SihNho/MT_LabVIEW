r"""diag_c125_5_fsscr - card 125-5 STEP 1 scratch (brief_125-5.md, PD252(e)): a 3-frame Flat Sequence in the FALSE frame of case #22694 on
a never-saved byte copy of the P3a bed (plan diag_c125_5_fsscr_plan.json; stagekit shape of diag_c125_4fsm.py, which passed the dry gate).
EXISTING FIRST: first frame = struct_copy_nested (OpPrimCopyNested_v0, gscript.py struct_copy_nested) of the EMPTY 1-frame FS in
claudeDev\DonorFs_v0.vi (gscript.fs_donor, built by diag_c125_5_opfs.py); frames = gscript.fs_add_frame / fs_frames (new ops
OpFsAddFrame_v0 / OpFsDiagrams_v0, hygiene records op_hygiene/); constant donor DonorSRInit_v0 #248 (I32 0, PD246); Max & Min =
the registered primitive donor; wire = connect_term_uid (OpConnectTermUid_v0); terminals by allterms (OpAllTerms_v1); joints = wire_joints.
PREDICTION: K case #22694 frames False/True, False = Diagram #27219 / F1 one new FlatSequence owned by #27219 / F2 two Add Frames ->
3 frames, the first frame stays leftmost, each add's new frame right of its reference / CEN census delta FlatSequence 1 + Diagram 3 /
W1 the frame-1 constant -> frame-2 Max & Min `x` wire: op err '', Is Broken? False, ONE new tunnel object (class read back) /
W2 wire_joints free ends 0 on every new wire / X bed md5 unchanged, scratch deleted, LabVIEW gone.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c125_5_fsscr.log -- py -u tools/bench/diag_c125_5_fsscr.py"""
import json, os, sys, time                                                                  # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K                                                                         # noqa: E402
g = K.g
PL = json.load(open(os.path.join(HERE, "diag_c125_5_fsscr_plan.json"), encoding="utf-8"))
DON, DONM = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"]
DRY = bool(getattr(g.report_all, "_dry", False))
CASE, CONST = 22694, {"donor": os.path.join(g.CLAUDEDEV, "DonorSRInit_v0.vi"), "uid": 248}
s = K.Stage(DON, DONM, "scratch_c125_5_fsscr", preload=False, deadline_min=28, reserve_s=150,
            out_json=os.path.join(HERE, "diag_c125_5_fsscr.json"), task="card 125-5 STEP 1")
OUT = {}


def dec(r):
    J = [list(x) for x in (r or {}).get("joints") or []]
    return {"joints": len(J), "loose": sum(1 for x in J if int(x[1]) & 0x100), "terms": sum(1 for x in J if int(x[1]) & 0x1),
            "free": [(i, list(x[0])) for i, x in enumerate(J) if int(x[2]) == 1 and not int(x[1]) & 0x1]}


def terms(W):
    import allterms
    return allterms.read_terms(W, allterms.OP_ALLTERMS_V1)[0]


def body(_):
    s.start(); s.discard_work(); W = s.work                                                  # noqa: E702
    if DRY:
        return s.dump()
    fr = g.case_frames(W, CASE); names = [str(n).strip() for n in fr["names"]]              # noqa: E702
    ff = int(fr["frames"][names.index("False")]) if "False" in names else 0
    s.gate("K case #%s frames %s, False = Diagram #%s" % (CASE, names, ff), ff == 27219, fr)
    c0, w0 = s.census_snapshot(), set(g.uids(W, "Wire"))
    cp = s._op("struct_copy_nested", lambda: g.struct_copy_nested(W, ff, "FlatSequence", g.fs_donor(), (60, 60)), "FS -> #%s" % ff)["result"] or {}
    fs = int(cp.get("uid") or 0)
    s.gate("F1 one new FlatSequence #%s owned by Diagram #%s (new diagrams %s)" % (fs, ff, cp.get("new_diagrams")), bool(fs), cp)
    if not fs:
        return s.dump()
    f1 = g.fs_frames(W, fs)
    a1 = s._op("fs_add_frame", lambda: g.fs_add_frame(W, fs, 0, True), "after 0")["result"] or {}
    a2 = s._op("fs_add_frame", lambda: g.fs_add_frame(W, fs, 1, True), "after 1")["result"] or {}
    f3 = g.fs_frames(W, fs)["frames"]
    OUT.update(fs=fs, frames_1=f1, add1=a1, add2=a2, frames=f3)
    s.fact("FRAMES left->right %s (start %s, add1 new %s, add2 new %s)" % (f3, f1["frames"], a1.get("new_frame"), a2.get("new_frame")))
    s.gate("F2 3 frames; first stays leftmost; add(0,T) new at 1, add(1,T) new at 2", len(f3) == 3 and f3[0] == f1["frames"][0]
           and f3[1] == a1.get("new_frame") and f3[2] == a2.get("new_frame"), (f1, f3))
    c1 = s.census_snapshot()
    for u in sorted(set(c1) - set(c0)):
        s.fact("CENSUS-NEW class %s #%s" % (c1[u], u))
    OUT["census"] = s.census_gate("CEN census delta of FS copy + 2 Add Frame == FlatSequence 1 + Diagram 3", c0, c1, {"FlatSequence": 1, "Diagram": 3})
    if len(f3) != 3:
        return s.dump()
    k = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, f3[0], "I32 const", (40, 40), donor=CONST), "const -> frame 1")["result"]
    m = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, f3[1], "Max & Min", (60, 40)), "Max & Min -> frame 2")["result"]
    rows = terms(W)
    src = [r for r in rows if int(r["owner_uid"]) == int(k or 0) and r["is_source"]]
    snk = [r for r in rows if int(r["owner_uid"]) == int(m or 0) and not r["is_source"] and str(r["term_name"]) == "x"]
    s.fact("TERMS const #%s src %s | Max & Min #%s x %s" % (k, [(r["term_uid"], r["frame_diagram"]) for r in src], m, [(r["term_uid"], r["frame_diagram"]) for r in snk]))
    if not (len(src) == 1 and len(snk) == 1):
        s.gate("W0 exactly one const output and one Max & Min x", False, (len(src), len(snk)))
        return s.dump()
    c2, wb = s.census_snapshot(), set(g.uids(W, "Wire"))
    cw = s._op("connect_term_uid", lambda: g.connect_term_uid(W, int(snk[0]["term_uid"]), int(src[0]["term_uid"])), "x <- const")["result"] or {}
    c3, wn = s.census_snapshot(), sorted(set(g.uids(W, "Wire")) - wb)
    tun = [(c3[u], u) for u in sorted(set(c3) - set(c2)) if "Tunnel" in c3[u] or "Terminal" in c3[u]]
    for u in sorted(set(c3) - set(c2)):
        s.fact("CENSUS-NEW-W class %s #%s" % (c3[u], u))
    rows = terms(W)
    path = [(r["owner_class"], r["owner_uid"], r["term_name"], r["is_source"], r["frame_diagram"], r["wire_uid"]) for r in rows if int(r["wire_uid"] or 0) in wn]
    s.fact("WIRE %s new wires %s; terminals on them %s" % (cw, wn, path))
    s.gate("W1 op err '', Is Broken? False, >= 1 tunnel-class object new %s" % tun, cw and not cw.get("err") and cw.get("broken") is False and bool(tun), (cw, tun))
    jt = dict((w, dec(g.wire_joints(W, w))) for w in wn)
    s.fact("JOINTS %s" % jt)
    s.gate("W2 wire_joints free ends 0 on every new wire %s" % wn, bool(jt) and all(not v["free"] for v in jt.values()), jt)
    OUT.update(wire=cw, new_wires=wn, tunnels=tun, path=path, joints=jt, census_wire=dict((c3[u], c3[u]) for u in set(c3) - set(c2)))
    s.gate("X bed md5 unchanged", K.md5(DON) == DONM, K.md5(DON))
    if not s.fails:
        json.dump({"function": "fs_add_frame", "status": "PASS", "t": time.time(), "card": "125-5", "log": "tools/bench/diag_c125_5_fsscr.log",
                   "also": ["fs_frames", "fs_donor"], "out": OUT}, open(os.path.join(HERE, "scratch_verify", "fs_add_frame_%s.json" % s.stamp), "w",
                  encoding="utf-8"), default=str, indent=1)
    json.dump(OUT, open(os.path.join(HERE, "diag_c125_5_fsscr_out.json"), "w", encoding="utf-8"), default=str, indent=1)
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
