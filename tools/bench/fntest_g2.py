# ---
# labview: build
# hardware: none
# ---
r"""fntest_g2 - card chat-F3b: the 58 functions of the P4 v18 plans, for real, on a scratch copy of claudeDev\EMPTY_v0.vi built in
the P4 ORDER (a SubVI FIRST - loop_in's default source is Traverse('SubVI')[0], gscript.py:1530 - a While, a While in its body,
the P4 donors), then the connect/delete/stop/SR/RLE/const routes, each verb through stagexec.LVBackend as the Executor calls
it (stagexec.py:2377-2485). EXISTING FIRST: fntest_g1's creates re-run as the bed build (fntest_g1.py is at RETRY_CAP 2/2,
stage_runs.jsonl:109-110); fntest_lib FT/Bed/Kit; diag_c139_3_run, diag_c137_5_routes. Wait/Select 'Function', RAS
'GrowableFunction' (measured, PRIM-GATE logs). PREDICTION: every positive case PASS (verb returns, read-back holds); both
negative double deletes end no_output; each of the 58 gets a record; handles after the routes within +-100 per 20 calls of
the post-bed level; scratches deleted; LabVIEW gone. A function FAIL is recorded with its numbers (a finding, not a fix).
py tools/bgrun.py --material --max-min 25 --log tools/bench/fntest_g2.log -- py -u tools/bench/fntest_g2.py"""
import os, shutil, sys                                                                        # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)                     # noqa: E702
import fntest_lib as L                                                                          # noqa: E402
import stagekit as K; g = K.g                                                                    # noqa: E402,E702
CD = K.CLAUDEDEV; EMPTY, EMPTY_MD5 = os.path.join(CD, "EMPTY_v0.vi"), "6544be40470e80763764089fd2767f2a"   # noqa: E702
DON =dict((k, {"donor": os.path.join(CD, f), "uid": u}) for k, f, u in (("wait", "OpWaitDonor_v0.vi", 163), ("sel", "DonorErrSel_MergeErrors.vi", 529),
           ("ras", "DonorRAS1D_v0.vi", 175), ("i32", "DonorSRInit_v0.vi", 248), ("boolf", "DonorBoolF_v0.vi", 126)))
LOG, PTS = os.path.join(HERE, "fntest_g2.log"), os.path.join(CD, "PathToStr.vi")
FNTEST = "per-function scratch test"                    # stage_prerun.fntest_release (card chat-F3, fp-42)
FNDIR = os.path.join(CD, "fntest"); os.makedirs(FNDIR, exist_ok=True)                           # noqa: E702
SV = os.path.join(FNDIR, "fntest_g2_save.vi")
s = K.Stage(EMPTY, EMPTY_MD5, "fntest_g2", preload=False, deadline_min=22, reserve_s=150, task="card chat-F3b G2", work_dir=FNDIR)
T, LVV = L.FT(s, "fntest_g2", card="chat-F3b"), []
NOOUT = lambda verb: lambda err, ops: (len(ops) == 1 and ops[0][0] == verb and ops[0][1] == "no_output", {"verb": verb})   # noqa: E731
CFW, NST = ["stagekit.op:connect_from_wire", "recipes.build_opconnectfromwire_v0.connect_from_wire"], ["stagekit.op:connect_nested_v1", "recipes.build_opconnectnested_v1.connect_nested_v1"]   # noqa: E702


def body(_):
    try:
        cases(_)
    finally:
        if LVV:
            s.R["fn_verdicts"] = T.commit(LOG, LVV[0]); s.dump()                                 # noqa: E702


def cases(_):
    s.start(); s.discard_work(); W = s.work                                                      # noqa: E702
    X, bp = K.mod("stagexec"), K.mod("bench_prep")                                               # noqa: E702
    be = X.LVBackend(s, []); B = L.Bed(s, be); k = L.Kit(T, B, be, W, g); LVV.append("LabVIEW " + str(g.lv().Version))   # noqa: E702
    need, mk, prim, con, LO, H = k.need, k.mk, k.prim, k.con, k.LO, {"start": bp.labview_handles()}   # noqa: E702
    D0 = k.r0()
    # ---------------------------------------------------------------- A: the bed, in the P4 order (SubVI first)
    mk(["stagekit.op:drop_subvi"], "A1 PathToStr subVI on D0 BEFORE any loop", "subvi", {"subvi_path": PTS}, {"diagram": D0, "pos": [300, 200]}, "SubVI")
    w = mk(["stagekit.op:loop_in"], "A2 While W on D0 (a SubVI present)", "while", {}, {"diagram": D0, "pos": [400, 40]}, "WhileLoop")
    WL, WB = (int(w["uid"]), int(w["body"])) if w else (None, None)
    w1 = mk(["stagekit.op:loop_in"], "A3 While W1 inside W's body (P4 p4_w1)", "while", {}, {"diagram": WB, "pos": [600, 300]}, "WhileLoop")
    W1L, W1B = (int(w1["uid"]), int(w1["body"])) if w1 else (None, None)
    WT1, SEL = prim("A4 Wait WT1 in W1B (P4 p4_wait)", W1B, DON["wait"], "Wait (ms)", [40, 40], "Function"), prim("A4 Select SEL in W1B (P4 p4_rbA_sel)", W1B, DON["sel"], "Select", [200, 40], "Function")
    RAS = prim("A4 Replace Array Subset in WB (P4 p4_rp27928_c)", WB, DON["ras"], "Replace Array Subset", [400, 40], "GrowableFunction")
    WT = dict((i, prim("A4 Wait WT%d in WB" % i, WB, DON["wait"], "Wait (ms)", [40, 100 * i], "Function")) for i in (2, 3, 4, 6, 7, 8, 9, 10, 11))
    K1, KB = prim("A4 I32 const K1 on D0", D0, DON["i32"], "const_donor", [40, 300]), prim("A4 Bool F const KB on D0 (P4 p4_c_stopall_f)", D0, DON["boolf"], "const_donor", [40, 400])
    fs = mk(["stagekit.op:struct_copy_nested"], "A5 Flat Sequence in WB (P4 p4_fs_n2)", "fs_create", {}, {"diagram": WB, "pos": [600, 700]}, "FlatSequence")
    WT[5] = prim("A5 Wait WT5 in the FS frame f0", int(fs["frames"][0]) if fs else None, DON["wait"], "Wait (ms)", [20, 20], "Function")
    B.read()
    mk(["stagekit.op:indicator_on_const"], "A6 indicator StopAll born on KB (P4 p4_i_stopall_k)", "indicator", {"label": "StopAll"}, {"diagram": D0, "born_on": B.ts(KB, None, True)}, "ControlTerminal")
    for i, lab in ((2, "Ind1"), (7, "Ind2")):
        mk(["stagekit.op:indicator_nested"], "A7 indicator %s on WT%d out (visible)" % (lab, i), "indicator", {"label": lab, "visible": True}, {"diagram": WB, "born_on": B.ts(WT[i], None, True)}, "ControlTerminal")
    mk([], "A8 control Ctl1 on WT8 input (the ctl route's source)", "control", {"label": "Ctl1"}, {"diagram": WB, "on": B.ts(WT[8], None, False)}, "ControlTerminal")
    LR = [mk(["stagekit.op:create_local_read", "stagekit.op:move_in", "recipes.build_d1_v0.move_in"], "A9 local read StopAll into %s" % n, "local_read", {"label": "StopAll"}, {"diagram": d, "pos": [20, 160]}, "Local") for n, d in (("W1B", W1B), ("WB", WB))]
    mk(["stagekit.op:create_local_write"], "A10 local write StopAll in WB (P4 p4_lw_stopall_639)", "local_write", {"label": "StopAll"}, {"diagram": WB, "pos": [200, 160]}, "Local")
    B.read()
    mk(["stagekit.op:create_const_on_term"], "A11 const 1 on WT1 input (P4 p4_wait_k)", "const_on_term", {"value": 1}, {"diagram": W1B, "on": B.ts(WT1, None, False)}, "Constant", uid=False)
    sr, ro, lo = k.add_sr("A12 add SR on W (P4 p4_sr_last)", WL, D0)
    B.read(); H["bed"], N0 = bp.labview_handles(), len(T.calls); s.fact("HANDLES after the bed {0} (start {1}); OWNERS {2}".format(H["bed"], H["start"], be.addr.owners))   # noqa: E702
    # ---------------------------------------------------------------- B: the routes (each case re-reads after itself)
    con(["stagekit.op:wire_const_sr"], "B1 const_sr K1 -> SR left OUTER face (P4 p4_w_klast)", B.ts(K1, None, True), lo)
    for nm, var, t in (("B2 wire_sr LeftIn: SR left inner -> WT2 input (P4 p4_w_last_gt)", "LeftIn", B.ts(WT[2], None, False)),
                       ("B3 wire_sr RightIn: WT3 out -> SR right inner (P4 p4_w_sel_last)", "RightIn", B.ts(WT[3], None, True))):
        need(nm, sr, t) and T.case(["stagekit.op:wire_sr"], nm, lambda var=var, t=t: be.wire_sr(var, WL, sr[0], t, list(B.real), {}), lambda o, t=t: B.wired_after(t))
    for nm, loop, lr in (("B4 stop: W1 cond <- local read StopAll in W1B (P4 p4_w_or_cond)", W1L, LR[0]), ("B4b stop: W cond <- local read StopAll in WB (P4 p4_w_stop12)", WL, LR[1])):
        src = B.ts(int(lr["uid"]), None, True) if lr else None
        need(nm, loop, src) and T.case(["stagekit.op:stop_from_node"], nm, lambda loop=loop, src=src: be.stop(loop, src, list(B.real), {}), lambda o, src=src: B.wired_after(src))
    con(NST, "B5 nested: WT4 out (bare) -> SEL.t in W1B, a crossing into W1", B.ts(WT[4], None, True), B.ts(SEL, "t", False))
    con(CFW, "B6 cfw: WT4 out (wired) -> WT6 input, same diagram (P4 p4_rp27928_arr)", B.ts(WT[4], None, True), B.ts(WT[6], None, False))
    con(NST, "B7 nested: SEL out -> RAS index, a crossing out of W1", B.ts(SEL, None, True), B.ts(RAS, "index", False))
    rw, dst = B.wire_of(B.ts(RAS, "index", False)), B.ts(WT[10], None, False)
    TS = next((int(x["owner_uid"]) for x in B.real if x["owner_class"] == "LoopTunnel" and x.get("term_class") == "OuterTerminal" and x["is_source"] and rw and int(x["wire_uid"] or 0) == rw), None)
    need("B8 branch", TS, dst) and T.case(CFW, "B8 branch: W1's output tunnel OUTER face -> WT10 input (P4 p4_w_idx_transpos)", lambda: be.branch(TS, dst, list(B.real), LO, {}, side="outer"), lambda o: B.wired_after(dst))
    src, dst = B.ts(WT[4], None, True), B.ts(WT[5], None, False)
    ctu = need("B9 connect_term_uid", src, dst) and T.case(["stagekit.op:connect_term_uid"], "B9 connect_term_uid fs_border: WT4 out (wired) -> WT5 input in the FS frame (P4 p4_x_bufdiff)",
                                                         lambda: be.connect_term_uid(src, dst, list(B.real), {"variant": "fs_border"}), lambda o: B.wired_after(dst))
    w5 = B.wire_of(dst) if ctu else None
    need("B10 RLE", w5) and T.case(["stagekit.op:wire_remove_loose_ends"], "B10 RLE on the FS-crossing wire w%s (P4 rle after a border)" % w5, lambda: be.rle([w5], {}),
                                   lambda o: (all(r.get("echo") == w5 and not r.get("broken_after") and not r.get("err") for r in o["rle"]), {"rle": o["rle"]}))
    # ---------------------------------------------------------------- D: deletes, then the three ControlTerminal routes on the bare terminals
    B.read()
    for n, lab in enumerate(("Ind1", "Ind2", "Ctl1"), 1):
        w = B.wire_of(B.ct(lab))
        dw = need("D%d delete_wire" % n, w) and T.case(["stagekit.op:delete_wire", "recipes.build_opfsinnertunnelconnect_v0.del_wire"], "D%d delete_wire w%s (%s's wire)" % (n, w, lab),
                                                      lambda w=w: be.delete_wire(w, {}), lambda o, w=w: (B.read() is not None and not any(int(x["wire_uid"] or 0) == w for x in B.real), {"wire": w}))
        if n == 1 and dw:
            T.negcase(["stagekit.op:delete_wire"], "D1n delete_wire w%s AGAIN (plan neg-double)" % w, lambda w=w: be.delete_wire(w, {}), NOOUT("delete_wire"))
    B.read()
    con(["stagekit.op:wire_indicators"], "B11 indicator route: WT3 out (wired) -> Ind1 (bare; P4 p4_rbA_re1)", B.ts(WT[3], None, True), B.ct("Ind1"))
    con(["stagekit.op:wire_ctlsink"], "B12 ctlsink: WT7 out (bare) -> Ind2 (bare; P4 p4_rbR_out)", B.ts(WT[7], None, True), B.ct("Ind2"))
    con(["stagekit.op:wire_control"], "B13 ctl: control Ctl1 (bare) -> WT8 input (wire_control)", B.ct("Ctl1"), B.ts(WT[8], None, False))
    c9, c11 = B.cls_of(WT[9]), B.cls_of(WT[11])
    do = need("D4 delete_object", c9) and T.case(["stagekit.op:delete_object", "recipes.build_opfsinnertunnelconnect_v0.del_node"], "D4 delete_object %s #%s (P4 p4_rp27928_do)" % (c9, WT[9]),
                                                 lambda: be.delete_object(c9, WT[9], {}), lambda o: (WT[9] not in g.uids(W, c9), {"cls": c9}))
    do and T.negcase(["stagekit.op:delete_object", "gscript.delete_object"], "D4n delete_object #%s AGAIN (plan neg-double)" % WT[9], lambda: be.delete_object(c9, WT[9], {}), NOOUT("delete_object"))
    i11 = s.uid_index(c11, WT[11]) if c11 else None
    need("D5 gscript.delete_object", i11) and T.case(["gscript.delete_object"], "D5 gscript.delete_object(verify=True) on WT11 (plan pos)", lambda: g.delete_object(W, c11, i11, verify=True),
                                                     lambda o: (WT[11] not in g.uids(W, c11), {"returned": str(o)[:120]}))
    H["routes"], N1 = bp.labview_handles(), len(T.calls)
    s.fact("HANDLES after the routes {0}: {1:+d} over {2} recorded calls since the bed ({3})".format(H["routes"], H["routes"] - H["bed"], N1 - N0, H))
    k.r1()
    shutil.copyfile(EMPTY, SV); s.scratches.append(SV)                                          # noqa: E702 ---- save/close on a runnable byte copy
    T.case(["gscript.save", "gscript.close_panel", "gscript.ensure_loaded"], "S1 save + close a runnable scratch copy", lambda: (g.ensure_loaded(SV), g.save(SV), g.close_panel(SV)),
           lambda r: (os.path.exists(SV), {"save": str(r[1])[:200], "md5_after": K.md5(SV)}))
    s.drop_scratch(SV, "S1"); s.fact("HANDLES end {0} ({1})".format(bp.labview_handles(), H))   # noqa: E702


if __name__ == "__main__":
    rc = K.run(body, s); K.mod("stagexec").kill_labview_at_exit(); sys.exit(rc)                  # noqa: E702
