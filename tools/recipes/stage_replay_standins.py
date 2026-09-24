r"""stage_replay_standins - card 77-4 (m8 plan PD18(a)(b), PD19(a)(c), PD20(a)(c)): rebuild the three replay VIs.
FOUND FIRST: tools/bench/diag_replay_standins.py (76-5 build: donors, For/SR counter, ReadFile chain - reused here with
three changes), diag_replay_gbtest.py (the #529 swap + census/edge diff), diag_replay_lib.py (every lookup helper),
create_const_loop_term (For N MEASURED cold, 77d 16/0; Q&R.y top-level NOT measured: gates A8+C2 decide), make_default.
CHANGES vs 76-5: N=1 and 10044 are DIAGRAM constants (PD19(a)); error in -> IMAQ ReadFile -> error out (PD19(c)); the
path String[] stays a panel default, read back COLD. Rows/values/names: tools/bench/plans/plan_replay_77.json.
PREDICTION: A* every create/copy/wire lands (fatal); N const wired to N, Q&R.y const wired; B1 buf ES 1 -> saved;
B2 cal ES 1 -> saved; G1 get-buff #529 calls IMAQdx Get Image.vi; G2 callee diff == #529 only, wire-edge diff 0 after
the uid remap, ES 1, saved; COLD (fresh LabVIEW): C1 each of the 3 ES 1 + no library in VI.Name; C2 N text '1' and
modulus text '10044' in buf AND cal (repr recorded = counter type); C3 path default 10044 entries f00000..f10043;
C4 pane per slot == IMAQdx Get Image.vi (stand-ins) / get buff image-lost frames.vi (copy); C5 cold callee census.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/stage_replay_77.log -- py -u tools/recipes/stage_replay_standins.py"""
import json, os, shutil, sys                                                             # noqa: E401
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bench"))
import diag_replay_lib as L                                                              # noqa: E402
K, g = L.K, L.g
P = json.load(open(os.path.join(K.BENCH, "plans/plan_replay_77.json"), encoding="utf-8"))
T, V, C = P["terms"], P["values"], K.mod("build_opcreateconstonterm_v0")
lab = lambda W, n: L.pidx(W, T[n])                                                       # noqa: E731
def const_top(s, W, u, tname, value, tag):
    """a diagram constant on top-level node #u's sink `tname` (create_const_loop_term 'for_n' = Nodes[].Terminals[])"""
    wt = L.walk(W, 0); r = L.term(wt[u][2], tname, False)
    c0 = g.uids(W, "Constant"); o = g.create_const_loop_term(W, "for_n", wt[u][0], value, term_index=r["i"])
    cu = L.new1(W, "Constant", c0); w = L.term(L.walk(W, 0)[u][2], tname, False)["wire"]
    s.gate("{0} const {1} on #{2}.{3!r}: inv_err '', one new constant, sink wired".format(tag, value, u, tname),
           not o.get("inv_err") and not o.get("err") and cu and w, (o, cu, w), fatal=True)
    return cu
def body(s):
    s.start(); shutil.copyfile(L.S1, g.MOVE_SRC); W = s.work; R = s.R
    paths = L.str_array_ctl(s, W, "A1")
    don = dict((k, next(((L.donor_class(u), u) for u in c if L.donor_class(u)), (None, None))) for k, c in P["donors"].items())
    s.gate("A0 donors found in S1", all(c for c, _u in don.values()), don, fatal=True)
    f0, d0 = g.uids(W, "ForLoop"), g.uids(W, "Diagram"); g.for_loop(W, (650, 80))
    fl, bu = L.new1(W, "ForLoop", f0), L.new1(W, "Diagram", d0)
    wt = L.walk(W, 0); c0 = g.uids(W, "Constant")
    o = g.create_const_loop_term(W, "for_n", wt[fl][0], V["N"], term_index=wt[fl][2][0]["i"] if wt[fl][2] else 0)
    R["N_uid"] = L.new1(W, "Constant", c0); nw = (L.walk(W, 0)[fl][2] or [L.DUMMY])[0]["wire"]
    s.gate("A2 For N const: inv_err '', one constant, N wired", not o.get("inv_err") and R["N_uid"] and nw, (o, nw), fatal=True)
    inc = L.copy_to(s, don["inc"][0], don["inc"][1], bu, (60, 60), "A3 inc")
    dec = L.copy_to(s, don["dec"][0], don["dec"][1], None, None, "A3 dec")
    qr = L.copy_to(s, don["qr"][0], don["qr"][1], None, None, "A3 qr")
    li = L.fidx(W, "ForLoop", fl); ru = g.add_shift_reg(W, li, 120, "ForLoop")
    regs = g.loop_cast(W, li, "ForLoop")["shift_reg_uids"]; k = regs.index(ru) if ru in regs else -1
    s.gate("A4 one shift register", len(regs) == 1 and k == 0, (regs, ru), fatal=True)
    wb = L.walk(W, L.diag_index(W, bu)); ni, ri = wb[inc][0], wb[inc][2]
    g.wire_sr("LeftIn", W, li, k, node_index=ni, term_index=L.term(ri, T["inc_in"], False)["i"], class_name="ForLoop")
    s.gate("A5 LeftIn -> Inc.x", L.term(L.walk(W, L.diag_index(W, bu))[inc][2], T["inc_in"], False)["wire"], fatal=True)
    t1 = g.uids(W, "LoopTunnel"); dx = T["dec_in"]; dy = L.tname(L.walk(W, 0)[dec][2], lambda n: True, True)
    g.wire(W, don["inc"][0], L.fidx(W, don["inc"][0], inc), T["inc_out"], don["dec"][0], L.fidx(W, don["dec"][0], dec), dx)
    tn = L.fidx(W, "LoopTunnel", L.new1(W, "LoopTunnel", t1))
    _ = g.tunnels(W, tn)["index_mode"] == 1 and g.set_index_mode(W, tn, 0)              # auto-indexed -> last value
    s.gate("A6 Inc.x+1 -> Dec.x through one tunnel, IndexMode 0", g.tunnels(W, tn)["index_mode"] == 0, tn, fatal=True)
    wi = L.term(L.walk(W, L.diag_index(W, bu))[inc][2], T["inc_out"], True)["wire"]
    g.wire_sr("RightIn", W, li, k, node_index=ni, term_index=L.term(ri, T["inc_out"], True)["i"], class_name="ForLoop")
    s.gate("A7 RightIn <- Inc.x+1 (same wire)", wi and L.term(L.walk(W, L.diag_index(W, bu))[inc][2], T["inc_out"], True)["wire"] == wi)
    g.wire(W, don["dec"][0], L.fidx(W, don["dec"][0], dec), dy, don["qr"][0], L.fidx(W, don["qr"][0], qr), T["qr_x"])
    R["mod_uid"] = const_top(s, W, qr, T["qr_y"], V["modulus"], "A8")
    ia = int(g.build_index_array(W, (900, 300))[0]["uid"]); ii = L.fidx(W, "IndexArray", ia)
    g.wire_control(W, [paths], "IndexArray", ii, [T["ia_arr"]])
    g.wire(W, don["qr"][0], L.fidx(W, don["qr"][0], qr), T["qr_r"], "IndexArray", ii, T["ia_idx"])
    su = []
    for p, xy in ((L.S_VI, (1050, 300)), (L.R_VI, (1250, 300))):
        b = g.uids(W, "SubVI"); g.drop_subvi(W, p, 0, xy); su.append(L.new1(W, "SubVI", b))
    stp, rdf = su; sx = lambda u: L.fidx(W, "SubVI", u)                                  # noqa: E731
    g.wire(W, "IndexArray", ii, T["ia_el"], "SubVI", sx(stp), T["stp_in"])
    g.wire(W, "SubVI", sx(stp), T["stp_out"], "SubVI", sx(rdf), T["rf_path"])
    g.wire_control(W, [T["img_in"]], "SubVI", sx(rdf), [T["rf_img"]])
    g.wire_control(W, [T["err_in"]], "SubVI", sx(rdf), [T["rf_err_in"]])
    for ind, src in (("img_out", "rf_img_out"), ("err_out", "rf_err_out")):
        wt = L.walk(W, 0); s.fact("connect_ctl {0}: {1}".format(ind, g.connect_ctl(W, lab(W, ind), wt[rdf][0], L.term(wt[rdf][2], T[src], True)["i"])))
    for snk, src in (("ses_out", "ses_in"), ("bn_out", "bn_in")):
        s.fact("ctl->ind {0} <- {1}: {2}".format(snk, src, g.connect_ctl_ind(W, lab(W, snk), lab(W, src))))
    wr = dict((n, L.pwire(W, T[n])) for n in ("img_in", "img_out", "err_in", "err_out", "ses_in", "ses_out", "bn_in", "bn_out", "mode"))
    R["panel"] = wr
    s.gate("A9 pane: all wired except Mode; BN Out on BN In's wire; error in != Session wire", all(v for n, v in wr.items() if n != "mode")
           and not wr["mode"] and wr["bn_out"] == wr["bn_in"] and wr["err_in"] != wr["ses_in"], wr, fatal=True)
    s.gate("B1 buf ExecState 1", s.es("B1") == 1, fatal=True)
    s.fact("make_default paths -> {0}".format(g.make_default(W, {paths: L.frame_paths()})))
    shutil.copyfile(W, L.BUF); R["buf"] = {"path": L.BUF, "md5": K.md5(L.BUF), "paths_label": paths}; s.fact("SAVED buf {0}".format(R["buf"]))
    g.delete_object(W, "Wire", L.fidx(W, "Wire", L.pwire(W, T["bn_out"])), verify=False)
    wt = L.walk(W, 0); s.fact("connect_ctl bn_out <- Dec: {0}".format(g.connect_ctl(W, lab(W, "bn_out"), wt[dec][0], L.term(wt[dec][2], dy, True)["i"])))
    s.gate("B2 cal: BN Out on Dec's wire, BN In bare, ES 1", L.pwire(W, T["bn_out"]) == L.term(L.walk(W, 0)[dec][2], dy, True)["wire"]
           and not L.pwire(W, T["bn_in"]) and s.es("B2") == 1, fatal=True)
    g.save(W); shutil.copyfile(W, L.CAL); R["cal"] = {"path": L.CAL, "md5": K.md5(L.CAL)}; s.fact("SAVED cal {0}".format(R["cal"]))
    s.head("[G] get-buff copy: replace ONLY #{0}".format(P["get_buff_node"])); gb = P["get_buff_node"]
    shutil.copyfile(L.GB, L.GBF); c0 = L.census(L.GBF)
    s.gate("G1 #{0} calls IMAQdx Get Image.vi".format(gb), str(c0.get(gb, "")).endswith("IMAQdx Get Image.vi"), c0, fatal=True)
    E0 = L.edges(K.mod("wiki_build").read_live(L.GBF, fs_pairs=[]), {}); r = g.replace_object(L.GBF, gb, L.BUF); nu = r["new_uid"]
    c1 = L.census(L.GBF); dd = dict((u, (c0.get(u), c1.get(u))) for u in set(c0) | set(c1) if c0.get(u) != c1.get(u))
    E1 = L.edges(K.mod("wiki_build").read_live(L.GBF, fs_pairs=[]), {nu: gb})
    s.gate("G2 replace clean; callee diff == #{0} -> buf only; wire-edge diff 0 after remap ({1} edges); ES 1".format(gb, len(E0)),
           not (r["err"] or r["err_replace"]) and nu and set(dd) <= {gb, nu} and os.path.normcase(str(c1.get(nu))) == os.path.normcase(L.BUF)
           and E0 == E1 and g.exec_state(L.GBF) == 1, (r, dd, sorted(E0 ^ E1)[:6]), fatal=True)
    g.save(L.GBF); R["gbf"] = {"path": L.GBF, "md5": K.md5(L.GBF), "new_uid": nu}; s.fact("SAVED get-buff {0}".format(R["gbf"])); s.dump()
    s.head("[C] COLD: fresh LabVIEW, every dependency read back before any test"); s.restart(); gi = L.pane_dirs(L.GI)
    for tag, p, ref in (("buf", L.BUF, gi), ("cal", L.CAL, gi), ("gbf", L.GBF, L.pane_dirs(L.GB))):
        with g.vi_ref(p) as v:
            nm = str(v.Name)
        s.gate("C1 {0} ExecState 1 COLD, VI.Name {1!r} has no library".format(tag, nm), g.exec_state(p) == 1 and ":" not in nm)
        pd = L.pane_dirs(p); s.gate("C4 {0} pane per slot == reference".format(tag), pd == ref, dict((q, (ref.get(q), pd.get(q))) for q in set(ref) | set(pd) if ref.get(q) != pd.get(q)))
    for tag, p in (("buf", L.BUF), ("cal", L.CAL)):
        cn, cm = C.read_const(p, R["N_uid"]), C.read_const(p, R["mod_uid"]); R["cold_" + tag] = {"N": cn, "mod": cm}
        s.gate("C2 {0} COLD N text '1' + modulus '10044' (repr N {1}, counter/modulus repr {2})".format(tag, cn.get("repr"), cm.get("repr")),
               str(cn.get("text")).strip() == "1" and str(cm.get("text")).strip() == "10044" and not (cn.get("err") or cm.get("err")), (cn, cm))
    with g.vi_ref(L.BUF) as v:
        pv = list(v.GetControlValue(paths) or [])
    s.gate("C3 buf COLD path default: 10044 entries f00000 .. f10043", len(pv) == L.N_FR and pv[:1] == L.frame_paths()[:1] and pv[-1:] == L.frame_paths()[-1:], (len(pv), pv[:1], pv[-1:]))
    s.gate("C5 get-buff COLD callee census == warm", L.census(L.GBF) == c1, L.census(L.GBF))
    R["mode_const"] = C.read_const(L.GBF, P["mode_const"]); s.fact("MODE #{0} (PD20(c)) read_const {1}".format(P["mode_const"], R["mode_const"])); s.dump()
class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])
    def summary(self):
        L.tail(self, FXL, (L.S1_MD5,)); return K.Stage.summary(self)
if __name__ == "__main__":
    g.restore_move_fixtures(); FXL = K.fixture_listing()
    st = St(L.BASE, L.BASE_MD5, "stage_replay_77", preload=False, deadline_min=35, work_dir=os.path.dirname(g.MOVE_DST),
            work_name=os.path.basename(g.MOVE_DST), pins=tuple(K.DEFAULT_PINS[:1]) + L.pins(), task="77-4",
            out_json=os.path.join(K.BENCH, "replay_vis_77.json"))
    sys.exit(K.run(body, st))
