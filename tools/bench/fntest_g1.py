# ---
# labview: build
# hardware: none
# ---
r"""fntest_g1 - card chat-F3 group 1: the CREATE verbs and the READS, run for real on a scratch copy of claudeDev\EMPTY_v0.vi.
EXISTING FIRST: the verbs are called through stagexec.LVBackend.create / add_sr exactly as the Executor calls them (the
P4 v18 create routes), the gscript functions are observed through fncontract's outcome record (tools/bench/fntest_lib.py).
Bed (created here, deleted at close): While W on D0 (+ body WB), Wait (ms) x4 on D0 + 1 in WB, I32 const on D0, Bool
const in WB, Flat Sequence (+1 frame), Case, PathToStr subVI, indicators ind1/ind2 (+1 on a const), locals, one SR.
PREDICTION: every case PASS (each verb returns its uid, the census moves by exactly its declared delta); handles after the
cases within +-100 per 20 calls of the post-bed level; ExecState read; scratch + save scratch deleted; LabVIEW gone.
py tools/bgrun.py --material --max-min 25 --log tools/bench/fntest_g1.log -- py -u tools/bench/fntest_g1.py"""
import os, shutil, sys                                                                        # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)                     # noqa: E702
import fntest_lib as L                                                                          # noqa: E402
import stagekit as K; g = K.g                                                                    # noqa: E402,E702
CD = K.CLAUDEDEV; EMPTY, EMPTY_MD5 = os.path.join(CD, "EMPTY_v0.vi"), "6544be40470e80763764089fd2767f2a"   # noqa: E702
DON = {"i32": {"donor": os.path.join(CD, "DonorSRInit_v0.vi"), "uid": 248}, "boolf": {"donor": os.path.join(CD, "DonorBoolF_v0.vi"), "uid": 126}}
LOG = os.path.join(HERE, "fntest_g1.log")
FNTEST = "per-function scratch test"                    # stage_prerun.fntest_release (card chat-F3, fp-42)
FNDIR = os.path.join(CD, "fntest"); os.makedirs(FNDIR, exist_ok=True)                           # noqa: E702
SV = os.path.join(FNDIR, "fntest_g1_save.vi")
s = K.Stage(EMPTY, EMPTY_MD5, "fntest_g1", preload=False, deadline_min=22, reserve_s=150, task="card chat-F3 G1", work_dir=FNDIR)
T, LVV = L.FT(s, "fntest_g1"), []


def body(_):
    try:
        cases(_)
    finally:
        if LVV:
            s.R["fn_verdicts"] = T.commit(LOG, LVV[0]); s.dump()                                 # noqa: E702


def cases(_):
    s.start(); s.discard_work(); W = s.work                                                      # noqa: E702
    X, bp = K.mod("stagexec"), K.mod("bench_prep")                                               # noqa: E702
    be = X.LVBackend(s, []); LVV.append("LabVIEW " + str(g.lv().Version)); s.fact("HANDLES at start {0}".format(bp.labview_handles()))   # noqa: E702
    cnt = lambda c: g.count(W, c)                                                                 # noqa: E731
    r0 = T.case(["gscript.count", "gscript.report_all", "gscript.uids", "gscript.exec_state"], "R0 empty bed reads agree",
                lambda: (cnt("Diagram"), g.report_all(W, "Diagram"), sorted(int(u) for u in g.uids(W, "Diagram")), g.exec_state(W)),
                lambda r: (r[0] == len(r[1]) == len(r[2]) == 1 and sorted(int(x["uid"]) for x in r[1]) == r[2] and r[3] == 1,
                           {"count": r[0], "report_all": len(r[1]), "uids": r[2], "exec_state": r[3]}))
    D0 = int(g.report_all(W, "Diagram")[0]["uid"])

    def mk(fns, name, route, a, args, real=(), cls=None, delta=1):
        c0 = cnt(cls) if cls else None
        return T.case(fns, name, lambda: be.create(route, dict(a, id=name), args, list(real), {}),
                      lambda o: ((not cls or cnt(cls) - c0 == delta) and bool(o.get("uid")), {"out": {k: o.get(k) for k in ("uid", "body", "frames", "new_frame", "how")}, "census": cls and (c0, cnt(cls))}))
    w = mk(["stagekit.op:loop_in"], "C1 while on D0", "while", {}, {"diagram": D0, "pos": [400, 40]}, cls="WhileLoop")
    WL, WB = int(w["uid"]), int(w["body"])
    P = ["stagekit.op:create_primitive_nested"]
    wt = [mk(P, "C2 Wait%d on D0" % i, "primitive", {"prim": "Wait (ms)"}, {"diagram": D0, "pos": [40, 40 + 70 * i]}, cls="Node")["uid"] for i in range(4)]
    wb = mk(P, "C3 Wait in WB", "primitive", {"prim": "Wait (ms)"}, {"diagram": WB, "pos": [60, 60]}, cls="Node")["uid"]
    mk(P, "C4 I32 const on D0 (donor)", "primitive", {"prim": "const_donor", "donor": DON["i32"]}, {"diagram": D0, "pos": [300, 300]}, cls="Constant")
    mk(P, "C5 Bool const in WB (donor)", "primitive", {"prim": "const_donor", "donor": DON["boolf"]}, {"diagram": WB, "pos": [160, 20]}, cls="Constant")
    fs = mk(["stagekit.op:struct_copy_nested"], "C6 Flat Sequence on D0", "fs_create", {}, {"diagram": D0, "pos": [40, 400]}, cls="FlatSequence")
    mk(["stagekit.op:case_in"], "C7 Case on D0", "case", {"label": "sel", "frames": ["False", "True"]}, {"diagram": D0, "pos": [600, 300]}, cls="CaseStructure")
    mk(["stagekit.op:drop_subvi"], "C8 PathToStr subVI on D0", "subvi", {"subvi_path": os.path.join(CD, "PathToStr.vi")}, {"diagram": D0, "pos": [300, 200]}, cls="SubVI")
    real = be.read(); be.addr.owners = L.owners_of(be.last_objs)                                # noqa: E702
    s.fact("OWNERS {0}".format(be.addr.owners))
    if fs:
        mk(["stagekit.op:fs_add_frame"], "C9 FS add frame", "fs_frame", {}, {"diagram": int(fs["frames"][0])}, real, cls="Diagram")
    real = be.read()
    for k, (n, lab) in enumerate(((wt[0], "ind1"), (wt[1], "ind2"))):
        mk(["stagekit.op:indicator_nested"], "C10 indicator %s on Wait%d out" % (lab, k), "indicator", {"label": lab, "visible": True},
           {"diagram": D0, "born_on": L.term(real, n, None, True)["term_uid"]}, real, cls="ControlTerminal")
        real = be.read()
    be.addr.owners = L.owners_of(be.last_objs)
    mk(["stagekit.op:create_const_on_term"], "C11 const on WaitB.in", "const_on_term", {"value": 5}, {"diagram": WB, "on": L.term(real, wb, None, False)["term_uid"]}, real, cls="Constant")
    real = be.read(); kc = [x for x in real if x["owner_class"] == "Constant" and int(x["frame_diagram"]) == WB and x["is_source"] and x["wire_uid"]]   # noqa: E702
    if len(kc) == 1:
        mk(["stagekit.op:indicator_on_const"], "C12 indicator on the WB const", "indicator", {"label": "ind3"}, {"diagram": WB, "born_on": kc[0]["term_uid"]}, real, cls="ControlTerminal")
    else:
        T.harness_err("C12 indicator on the WB const", "wired WB const rows: {0}".format(len(kc)))
    mk(["stagekit.op:create_local_read", "stagekit.op:move_in", "recipes.build_d1_v0.move_in"], "C13 local read ind1 -> WB", "local_read", {"label": "ind1"}, {"diagram": WB, "pos": [20, 120]}, cls="Local")
    mk(["stagekit.op:create_local_write"], "C14 local write ind2 in WB", "local_write", {"label": "ind2"}, {"diagram": WB, "pos": [200, 120]}, cls="Local")
    sr0 = len(g.report_all(W, "LeftShiftRegister"))
    T.case(["stagekit.op:add_shift_reg"], "C15 add SR on W", lambda: be.add_sr(WL, 120, {}),
           lambda o: (len(g.report_all(W, "LeftShiftRegister")) == sr0 + 1 and g.shift_reg(W, s.uid_index("WhileLoop", WL), 0).get("uid"),
                      {"left_sr": (sr0, len(g.report_all(W, "LeftShiftRegister"))), "shift_reg0": g.shift_reg(W, s.uid_index("WhileLoop", WL), 0), "left0": g.shift_reg_left(W, s.uid_index("WhileLoop", WL), 0)}))
    dl = [int(x["uid"]) for x in g.report_all(W, "Diagram")]                                              # ---- reads on the built bed
    T.case(["gscript.node_labels", "gscript.node_terms_uid", "gscript.node_terms"], "R1 node reads on D0/WB", lambda: [(g.node_labels(W, dl.index(d)), g.node_terms_uid(W, dl.index(d), 0), g.node_terms(W, dl.index(d), 0)) for d in (D0, WB)],
           lambda r: (all(len(a) >= 1 and b and c for a, b, c in r), {"labels": [[x.get("label") for x in a][:8] for a, _b, _c in r], "terms0": [(b if not isinstance(b, list) else len(b)) for _a, b, _c in r]}))
    T.case(["gscript.panel_wiring"], "R2 panel_wiring", lambda: g.panel_wiring(W), lambda r: (sorted(x["label"] for x in r) == ["ind1", "ind2", "ind3"], {"labels": [x["label"] for x in r]}))
    T.case(["gscript.exec_state", "gscript.wire_health"], "R3 exec_state + wire_health", lambda: (g.exec_state(W), g.wire_health(W)), lambda r: (r[0] in (0, 1), {"es": r[0], "wire_health": str(r[1])[:200]}))
    h1 = bp.labview_handles(); s.fact("HANDLES after the cases {0}".format(h1))
    shutil.copyfile(EMPTY, SV); s.scratches.append(SV)                                          # noqa: E702 ---- save/close on a runnable byte copy
    T.case(["gscript.save", "gscript.close_panel", "gscript.ensure_loaded"], "S1 save + close a runnable scratch", lambda: (g.ensure_loaded(SV), g.save(SV), g.close_panel(SV)),
           lambda r: (os.path.exists(SV), {"save": str(r[1])[:200], "md5_after": K.md5(SV)}))
    s.drop_scratch(SV, "S1"); s.fact("HANDLES end {0} (after cases {1})".format(bp.labview_handles(), h1))   # noqa: E702


if __name__ == "__main__":
    rc = K.run(body, s); K.mod("stagexec").kill_labview_at_exit(); sys.exit(rc)                  # noqa: E702
