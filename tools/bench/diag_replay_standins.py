r"""diag_replay_standins - card 76-5 (m8 plan PD18(a)(b), PD16(c)): the two IMAQdx Get Image stand-ins, built by SCRIPT from a
copy of replay_imaqdx_pane_base.vi (65e999d9) in the NI Moving-Objects Target (copy_in precondition, stage_d1_m4b.py:101-106).
PRIMITIVE ROUTE = copy_by_index from S1 (D1_s1_copy.vi): Increment #1978, Decrement #9179|#29956, Q&R #2136. No generic
creator was built: the external search on record (archive/peer/2026-09-23-c68-m4-prims.md Q1; skill vi-scripting.md:52-70,
NI forum) gives only LV2009 style ids, "unverified on LV2026", and NI's own advice to copy from a donor.
FRAME PATH = String[] control (NAMES.md:966) + Index Array + StrToPath.vi (stage2-assembly-step-b.md:40: no Format Into
String, its copied arity is the donor's). COUNTER = For loop, N from an auto-indexed 1-element String[] (NAMES.md:962),
UNINITIALISED shift register, Increment in the body; k+1 leaves by a border wire (tunnel forced IndexMode 0), Decrement -> k.
frame = paths[k mod 10044] = f(k mod 10044) (PD18(a)); buf: BN Out = BN In; cal: BN Out = k. Session/error pass through.
PREDICTION: A1-A2 two free String[] controls; A3 one For loop, its tunnel IndexMode 1; A4-A5 3 copies, UID guard; A6 one
register; A7 LeftIn -> Inc.x wired; A8 Inc.x+1 -> Dec.x crosses by ONE new tunnel, IndexMode 0 after the flip; A9 RightIn
(branch, same wire uid); A10-A16 each sink wired; B1 buf ES 1 -> defaults + save -> file; B2 cal: BN pass-through wire
deleted, Dec -> BN Out, ES 1 -> save -> file; C1 fresh LabVIEW: both ES 1 COLD, VI.Name has no ':'; C2 pane per slot
(label, direction) == IMAQdx Get Image.vi; C3 replace #529 in a get-buff scratch by each: every wire kept, ES 1.
    MATERIAL=1 py tools/bgrun.py --max-min 50 --log tools/bench/replay_vis_76d.log -- py -u tools/bench/diag_replay_standins.py"""
import os, sys, shutil                                                                   # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diag_replay_lib as L                                                              # noqa: E402
K, g = L.K, L.g
PRE = L.pins()


def body(s):
    s.start(); shutil.copyfile(L.S1, g.MOVE_SRC); W = s.work
    s.gate("K4 MOVE_SRC holds S1's bytes", K.md5(g.MOVE_SRC) == L.S1_MD5, fatal=True)
    don = {}
    for k, cands in (("inc", (1978,)), ("dec", (9179, 29956)), ("qr", (2136, 10068, 29240))):
        don[k] = next(((L.donor_class(u), u) for u in cands if L.donor_class(u)), (None, None))
    s.gate("D0 donors found in S1", all(c for c, _u in don.values()), don, fatal=True)
    once = L.str_array_ctl(s, W, "A1"); paths = L.str_array_ctl(s, W, "A2")
    d0 = {int(d["uid"]) for d in g.report_all(W, "Diagram")}; t0 = {int(o["uid"]) for o in g.report_all(W, "LoopTunnel")}
    g.for_loop(W, (650, 80), tunnels=[once], indexing=[True])
    bu = [int(d["uid"]) for d in g.report_all(W, "Diagram") if int(d["uid"]) not in d0]; fl = int(g.report_all(W, "ForLoop")[0]["uid"])
    tn = [o["i"] for o in g.report_all(W, "LoopTunnel") if int(o["uid"]) not in t0]
    s.gate("A3 one For loop + one body, its tunnel IndexMode 1", len(bu) == 1 and len(tn) == 1 and g.tunnels(W, tn[0])["index_mode"] == 1, (bu, tn), fatal=True)
    inc = s.copy_in(don["inc"][0], don["inc"][1], bu[0], (60, 60), "A4 inc")
    dec = L.copy_top(s, don["dec"][0], don["dec"][1], "A5 dec"); qr = L.copy_top(s, don["qr"][0], don["qr"][1], "A5 qr")
    li = s.uid_index("ForLoop", fl); r0 = set(g.loop_cast(W, li, "ForLoop")["shift_reg_uids"]); ru = g.add_shift_reg(W, li, 120, "ForLoop")
    regs = g.loop_cast(W, li, "ForLoop")["shift_reg_uids"]; sr = {"loop_index": li, "k": regs.index(ru) if ru in regs else -1}
    s.gate("A6 Shift Registers[] == before + {new uid}", set(regs) == r0 | {ru}, (sorted(r0), regs, ru), fatal=True); s.junk_purge("A6")
    wb = L.walk(W, L.diag_index(W, bu[0])); ni, ri = wb[inc][0], wb[inc][2]; s.fact("Inc body terms {0}".format([(r["name"], r["is_source"]) for r in ri]))
    xin, xout = L.term(ri, "x", False)["i"], L.term(ri, "x+1", True)["i"]
    g.wire_sr("LeftIn", W, sr["loop_index"], sr["k"], node_index=ni, term_index=xin, class_name="ForLoop")
    s.gate("A7 LeftIn -> Increment.x wired", L.term(L.walk(W, L.diag_index(W, bu[0]))[inc][2], "x", False)["wire"] != 0, fatal=True)
    wt = L.walk(W, 0); dx = L.tname(wt[dec][2], lambda n: n == "x", False); dy = L.tname(wt[dec][2], lambda n: True, True)
    t1 = {int(o["uid"]) for o in g.report_all(W, "LoopTunnel")}
    g.wire(W, don["inc"][0], L.fidx(W, don["inc"][0], inc), "x+1", don["dec"][0], L.fidx(W, don["dec"][0], dec), dx)
    nt = [o["i"] for o in g.report_all(W, "LoopTunnel") if int(o["uid"]) not in t1]
    if len(nt) == 1 and g.tunnels(W, nt[0])["index_mode"] == 1:
        g.set_index_mode(W, nt[0], 0)
    s.gate("A8 Inc.x+1 -> Dec.x: one new tunnel, IndexMode 0", len(nt) == 1 and g.tunnels(W, nt[0])["index_mode"] == 0, nt, fatal=True)
    w_inc = L.term(L.walk(W, L.diag_index(W, bu[0]))[inc][2], "x+1", True)["wire"]
    g.wire_sr("RightIn", W, sr["loop_index"], sr["k"], node_index=ni, term_index=xout, class_name="ForLoop")
    s.gate("A9 RightIn <- Inc.x+1 (branch, same wire)", w_inc and L.term(L.walk(W, L.diag_index(W, bu[0]))[inc][2], "x+1", True)["wire"] == w_inc, w_inc)
    wt = L.walk(W, 0); qx, qy = L.term(wt[qr][2], "x", False), L.term(wt[qr][2], "y", False); qr_r = "x-y*floor(x/y)"
    g.wire(W, don["dec"][0], L.fidx(W, don["dec"][0], dec), dy, don["qr"][0], L.fidx(W, don["qr"][0], qr), "x")
    b = {l for _i, l, ind in g.fp_labels(W) if not ind}; g.create_control(W, wt[qr][0], qy["i"])
    nfr = [l for _i, l, ind in g.fp_labels(W) if not ind and l not in b][-1]; s.fact("Q&R y control {0!r}; x term {1}".format(nfr, qx))
    ia = int(g.build_index_array(W, (900, 300))[0]["uid"]); ii = L.fidx(W, "IndexArray", ia)
    g.wire_control(W, [paths], "IndexArray", ii, ["array"])
    g.wire(W, don["qr"][0], L.fidx(W, don["qr"][0], qr), qr_r, "IndexArray", ii, "index")
    su = []
    for p, xy in ((L.S_VI, (1050, 300)), (L.R_VI, (1250, 300))):
        before = g.uids(W, "SubVI"); g.drop_subvi(W, p, 0, xy); su.append([u for u in g.uids(W, "SubVI") if u not in before][0])
    stp, rdf = su; wt = L.walk(W, 0); s.fact("ReadFile terms {0}".format([(r["name"], r["is_source"]) for r in wt[rdf][2]]))
    g.wire(W, "IndexArray", ii, "element", "SubVI", L.fidx(W, "SubVI", stp), "string")
    g.wire(W, "SubVI", L.fidx(W, "SubVI", stp), "path", "SubVI", L.fidx(W, "SubVI", rdf), "File Path")
    FP = [(l, ind) for _i, l, ind in g.fp_labels(W)]; lab = lambda pred, ind: [l for l, i2 in FP if pred(l) and i2 == ind][0]  # noqa: E731
    img_in, img_out = "Image In", "Image Out"                       # exact labels (review 2026-09-25-76-5-a16 s2)
    s.gate("A15 BN In / Mode are distinct panel indices", L.pidx(W, "Buffer Number In") != L.pidx(W, "Buffer Number Mode (Next)"), fatal=True)
    g.wire_control(W, [img_in], "SubVI", L.fidx(W, "SubVI", rdf), ["Image"])
    wt = L.walk(W, 0); s.fact("connect_ctl Image Out: {0}".format(g.connect_ctl(W, L.pidx(W, img_out), wt[rdf][0], L.term(wt[rdf][2], "Image Out", True)["i"])))
    for snk, src in (("Session Out", "Session In"), ("error out", "error in"), ("Buffer Number Out", "Buffer Number In")):   # run 1: a prefix match took 'Buffer Number Mode (Next)'
        s.fact("ctl->ind {0!r} <- {1!r}: {2}".format(snk, src, g.connect_ctl_ind(W, L.pidx(W, snk), L.pidx(W, src))))
    pw = {r["label"]: r for r in g.panel_wiring(W)}; s.R["panel"] = pw
    s.gate("A16 every pane object except Mode + the three new controls wired; BN Out on BN In's wire", all(pw[l]["wire"] for l, _i in FP if "Mode" not in l)
           and pw["Buffer Number Out"]["wire"] == pw["Buffer Number In"]["wire"] and not pw["Buffer Number Mode (Next)"]["wire"], dict((l, pw[l]["wire"]) for l, _i in FP), fatal=True)
    if not s.gate("B1 buf ExecState 1 before the defaults", s.es("B1") == 1):
        before = {(d, u, r["name"]): r["wire"] for d in range(len(g.report_all(W, "Diagram"))) for u, (_n, _l, rs) in L.walk(W, d).items() for r in rs}
        s.broken_wire_count(allow_mutation=True, tag="B1 localiser (nothing is saved after this)")
        after = {(d, u, r["name"]): r["wire"] for d in range(len(g.report_all(W, "Diagram"))) for u, (_n, _l, rs) in L.walk(W, d).items() for r in rs}
        s.fact("B1 terminals that LOST their wire to Remove Bad Wires: {0}".format(sorted(k for k, w in before.items() if w and not after.get(k))))
        raise K.Stop("B1 buf ExecState 0 - localised above, nothing saved")
    s.fact("make_default -> {0} B".format(g.make_default(W, {once: ["1"], paths: L.frame_paths(), nfr: L.N_FR})))
    shutil.copyfile(W, L.BUF); s.R["buf"] = {"path": L.BUF, "md5": K.md5(L.BUF)}; s.fact("SAVED buf {0}".format(s.R["buf"]))
    s.gate("B1b the run-1 buf (BN Out <- Mode, md5 0d537725...) is overwritten", s.R["buf"]["md5"] != "0d5377256895b548dc6fe41e1bb2cdf0", fatal=True)
    bno = "Buffer Number Out"
    g.delete_object(W, "Wire", L.fidx(W, "Wire", {r["label"]: r for r in g.panel_wiring(W)}[bno]["wire"]), verify=False)
    wt = L.walk(W, 0); s.fact("connect_ctl BN Out <- Dec: {0}".format(g.connect_ctl(W, L.pidx(W, bno), wt[dec][0], L.term(wt[dec][2], dy, True)["i"])))
    pw = {r["label"]: r for r in g.panel_wiring(W)}; bni = "Buffer Number In"
    s.gate("B2 cal: BN Out wired to Dec's wire, BN In bare, ES 1", pw[bno]["wire"] == L.term(L.walk(W, 0)[dec][2], dy, True)["wire"]
           and pw[bni]["wire"] == 0 and s.es("B2") == 1, (pw[bno]["wire"], pw[bni]["wire"]), fatal=True)
    g.save(W); shutil.copyfile(W, L.CAL); s.R["cal"] = {"path": L.CAL, "md5": K.md5(L.CAL)}; s.fact("SAVED cal {0}".format(s.R["cal"]))
    s.head("[C] fresh LabVIEW: cold reads, pane, type check by replace"); s.restart()
    gi = L.pane_dirs(L.GI); s.R["gi_pane"] = gi
    for tag, p in (("buf", L.BUF), ("cal", L.CAL)):
        with g.vi_ref(p) as v:
            nm = str(v.Name)
        s.gate("C1 {0} ExecState 1 COLD, VI.Name {1!r} has no library".format(tag, nm), g.exec_state(p) == 1 and ":" not in nm)
        pd = L.pane_dirs(p); dd = dict((k, (gi.get(k), pd.get(k))) for k in set(gi) | set(pd) if gi.get(k) != pd.get(k))
        s.gate("C2 {0} pane diff per slot (label, direction) vs IMAQdx Get Image.vi == empty".format(tag), not dd, dd)
        sc = s.scratch("gb" + tag, source=L.GB); w0 = {r["name"]: bool(r["wire"]) for r in L.walk(sc, 0).get(529, (0, 0, []))[2] if r["name"]}
        rep = g.replace_object(sc, 529, p); nu = rep["new_uid"]; w1 = {r["name"]: bool(r["wire"]) for r in L.walk(sc, 0).get(nu, (0, 0, []))[2] if r["name"]}
        s.gate("C3 {0}: replace #529 keeps every wire (slot types compatible), ES 1".format(tag), w0 and w1 == w0 and g.exec_state(sc) == 1, (rep, w0, w1))
        s.drop_scratch(sc, "C3 " + tag)
    s.dump()


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])

    def summary(self):
        L.tail(self, FXL, (L.S1_MD5,))
        return K.Stage.summary(self)


if __name__ == "__main__":
    g.restore_move_fixtures(); FXL = K.fixture_listing()
    st = St(L.BASE, L.BASE_MD5, "replay_vis_76d", preload=False, deadline_min=45, work_dir=os.path.dirname(g.MOVE_DST),
            work_name=os.path.basename(g.MOVE_DST), pins=tuple(K.DEFAULT_PINS[:1]) + PRE, task="76-5",
            out_json=os.path.join(K.BENCH, "replay_vis_76d.json"))
    sys.exit(K.run(body, st))
