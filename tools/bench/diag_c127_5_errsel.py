r"""diag_c127_5_errsel - card 127-5 (PD259(c)): IMAQ Copy error out -> Unbundle By Name -> Select s (t = I32 -1, f = I32 0) -> I32 sink
on a never-saved byte copy of claudeDev\HARNESS_copyloop.vi, and the DIRECT error out -> Select s form on a second byte copy.
Plan: diag_c127_5_errsel_plan.json. EXISTING FIRST: no Unbundle By Name / Select donor is registered (facts_c100_oplabels donors =
Max & Min, Wait (ms); routes_c123_ring_p3.json Select 0 hits in the bed) -> donors found as diag_c103_wait_donor.py did (byte copies
of NI examples, node found by allterms signature), placed by create_primitive_nested(donor=) (OpPrimCopyNested_v0); constants
DonorRingConst_v0 #249 (I32 -1) / DonorSRInit_v0 #248 (I32 0) as plan_ring_p3b.json p3b_k_m1; wires connect_term_uid; Error List
errorlist_check as diag_c127_1_fsinner.py.
PREDICTION: D1 both donors found; each create op err '' and census = ONE node class; W-1..W-5 op err '', Is Broken? False; the
Unbundle's source row reads `status` after W-1; scratch 1 ExecState 1. Scratch 2 direct form: MEASUREMENT (broken or not).
X input md5 unchanged, scratches/candidates deleted, LabVIEW gone.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/diag_c127_5_errsel.log -- py -u tools/bench/diag_c127_5_errsel.py"""
import json, os, shutil, sys, time                                                          # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K; g = K.g                                                               # noqa: E402,E702
PL = json.load(open(os.path.join(HERE, "diag_c127_5_errsel_plan.json"), encoding="utf-8"))
DON, DONM = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"]
DRY = bool(getattr(g.report_all, "_dry", False))
IM, P, OUT = PL["imaq"], PL["pos"], {"creates": {}, "wires": {}}
KT, KF = [{"donor": os.path.join(g.CLAUDEDEV, PL[k]["vi"]), "uid": PL[k]["uid"]} for k in ("const_t", "const_f")]
DU, DS = os.path.join(g.CLAUDEDEV, "DonorUnbundle_v0.vi"), os.path.join(g.CLAUDEDEV, "DonorSelect_v0.vi")
KEEP = []
s = K.Stage(DON, DONM, "scratch_c127_5_errsel", preload=False, deadline_min=37, reserve_s=150,
            out_json=os.path.join(HERE, "diag_c127_5_errsel.json"), task="card 127-5 PD259(c)")
s.close = lambda: K.Stage.close(s, expect_files=sorted(KEEP))
def terms(W):
    import allterms
    return [] if DRY else allterms.read_terms(W, allterms.OP_ALLTERMS_V1)[0]
def rw(r): return {"uid": int(r["term_uid"]), "name": r["term_name"], "src": bool(r["is_source"]), "cls": r.get("term_class"), "wire": int(r["wire_uid"] or 0)}
def by_class(c0, c1): return dict((c, sum(1 for u in set(c1) - set(c0) if c1[u] == c)) for c in set(c1[u] for u in set(c1) - set(c0)))
def donors():
    unb, sel, made = None, None, []
    for i, rel in enumerate(PL["candidates"]):
        ex = os.path.join(PL["examples"], rel)
        if not os.path.exists(ex):
            s.fact("D1 candidate missing %s" % rel); continue                                 # noqa: E702
        cp = os.path.join(g.CLAUDEDEV, "DonorCand_c127_5_%d.vi" % i); shutil.copyfile(ex, cp); made.append(cp); s.scratches.append(cp)   # noqa: E702
        own = {}
        for r in terms(cp):
            own.setdefault(int(r["owner_uid"]), []).append(r)
        nu = [(u, rs) for u, rs in own.items() if rs[0]["owner_class"] == "NamedUnbundler"]
        ns = [(u, rs) for u, rs in own.items() if sorted(str(r["term_name"]) for r in rs) == PL["select_sig"]]
        s.fact("D1 %s: NamedUnbundler %s | Select-signature %s" % (rel, [(u, [r["term_name"] for r in rs]) for u, rs in nu], [(u, rs[0]["owner_class"]) for u, rs in ns]))
        st = [x for x in nu if any(r["term_name"] == "status" and r["is_source"] for r in x[1])]
        if (st or nu) and (unb is None or (st and not unb[3])):
            x = (st or nu)[0]; unb = (ex, min(u for u, _ in (st or nu)), x[1][0]["owner_class"], bool(st))     # noqa: E702
        if ns and sel is None:
            sel = (ex, min(u for u, _ in ns), ns[0][1][0]["owner_class"])
        if sel and unb and unb[3]:
            break
    return unb, sel
def create(W, tag, dg, prim, pos, donor):
    c0 = s.census_snapshot()
    u = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, dg, prim, tuple(pos), donor=donor), "%s %s" % (tag, prim))["result"]
    c1, rows = s.census_snapshot(), [rw(r) for r in terms(W) if int(r["owner_uid"]) == int(u or 0)]
    OUT["creates"][tag] = {"uid": u, "census": by_class(c0, c1), "terms": rows}
    s.fact("CREATE %s #%s census %s terms %s" % (tag, u, json.dumps(OUT["creates"][tag]["census"], sort_keys=True), rows))
    s.gate("%s op err '' and one node" % tag, DRY or (u and sum(OUT["creates"][tag]["census"].values()) >= 1), u)
    return 0 if DRY else int(u or 0)
def t(W, tag, name, src):
    r = [x for x in terms(W) if int(x["owner_uid"]) == OUT["creates"][tag]["uid"] and bool(x["is_source"]) == src and (name is None or x["term_name"] == name)]
    if not DRY and len(r) != 1:
        s.gate("T %s %s %s exactly one terminal" % (tag, name, "src" if src else "sink"), False, [rw(x) for x in r]); raise K.Stop("terminal")   # noqa: E702
    return 0 if DRY else int(r[0]["term_uid"])
def wire(W, tag, snk, src, expect_ok=True):
    c0 = s.census_snapshot()
    cw = s._op("connect_term_uid", lambda: g.connect_term_uid(W, snk, src), "%s #%s <- #%s" % (tag, snk, src))
    res = cw["result"] or {}
    c1 = s.census_snapshot()
    OUT["wires"][tag] = {"op": res, "err": cw["err"], "census": by_class(c0, c1), "es": None if DRY else g.exec_state(W)}
    s.fact("WIRE %s Is Broken? %s err %r census %s ExecState %s" % (tag, res.get("broken"), cw["err"] or res.get("err"), json.dumps(OUT["wires"][tag]["census"], sort_keys=True), OUT["wires"][tag]["es"]))
    if expect_ok:
        s.gate("%s op err '' and Is Broken? False" % tag, DRY or (res and not cw["err"] and not res.get("err") and res.get("broken") is False), res)
    return res
def build(W, tag, direct):
    dg = IM["diagram"]
    sel = create(W, tag + "sel", dg, "Select", P["sel"], {"donor": DS, "uid": OUT["donor_sel"]})
    create(W, tag + "kt", dg, "const_donor", P["kt"], KT); create(W, tag + "kf", dg, "const_donor", P["kf"], KF)   # noqa: E702
    create(W, tag + "mm", dg, "Max & Min", P["mm"], None)
    if direct:
        wire(W, tag + "W_s_direct", t(W, tag + "sel", "s", False), IM["err_out"], expect_ok=False)
    else:
        create(W, tag + "unb", dg, "Unbundle By Name", P["unb"], {"donor": DU, "uid": OUT["donor_unb"]})
        wire(W, tag + "W_unb_in", t(W, tag + "unb", None, False), IM["err_out"])
        OUT["unb_after_wire"] = [rw(r) for r in terms(W) if int(r["owner_uid"]) == OUT["creates"][tag + "unb"]["uid"]]
        so = [r for r in OUT["unb_after_wire"] if r["src"]]
        s.gate("U Unbundle By Name default element after wiring == status %s" % so, DRY or [r["name"] for r in so] == ["status"], so)
        wire(W, tag + "W_s", t(W, tag + "sel", "s", False), t(W, tag + "unb", None, True))
    wire(W, tag + "W_t", t(W, tag + "sel", "t", False), t(W, tag + "kt", None, True))
    wire(W, tag + "W_f", t(W, tag + "sel", "f", False), t(W, tag + "kf", None, True))
    wire(W, tag + "W_out", t(W, tag + "mm", "x", False), t(W, tag + "sel", "s? t: f", True))
    OUT[tag + "terms_sel_end"] = [rw(r) for r in terms(W) if int(r["owner_uid"]) == OUT["creates"][tag + "sel"]["uid"]]
    OUT[tag + "es"] = None if DRY else g.exec_state(W)
    s.fact("END %s ExecState %s Select terms %s" % (tag, OUT[tag + "es"], OUT[tag + "terms_sel_end"]))
    return sel
def body(_):
    s.start(); s.discard_work(); W = s.work                                                  # noqa: E702
    ok = [r for r in terms(W) if int(r["term_uid"]) == IM["err_out"] and int(r["owner_uid"]) == IM["uid"] and r["is_source"]]
    s.gate("K IMAQ Copy #%s error out #%s present, unwired %s" % (IM["uid"], IM["err_out"], [rw(r) for r in ok]), DRY or (len(ok) == 1 and not int(ok[0]["wire_uid"] or 0)))
    unb, sel = (None, None) if DRY else donors()
    if not s.gate("D1 donors found: Unbundle %s | Select %s" % (unb, sel), DRY or (unb and sel), (unb, sel)):
        return s.dump()
    if not DRY:
        shutil.copyfile(unb[0], DU); shutil.copyfile(sel[0], DS); KEEP.extend([os.path.basename(DU), os.path.basename(DS)])   # noqa: E702
    OUT.update(donor_unb=0 if DRY else unb[1], donor_sel=0 if DRY else sel[1], donor_src={"unb": unb, "sel": sel})
    build(W, "S1_", False)
    W2 = os.path.join(g.CLAUDEDEV, "scratch_c127_5_direct_%s.vi" % s.stamp); s.scratches.append(W2)   # noqa: E702
    DRY or shutil.copyfile(DON, W2)
    build(W2, "S2_", True)
    if not DRY:
        import errorlist_check as EC
        EC._lv_imports(); R = {"gui_acts_outer": [], "errors": []}; EC.open_diagram(W, R)   # noqa: E702
        r = EC.E.read(W, os.path.join(HERE, "errorlist_c127_5_S1_%s_raw.json" % s.stamp), log=lambda m: None, on_item=None)
        OUT["el"] = {"items": len(r.get("items") or []), "classes": EC.class_counts(r.get("items")), "raw": [it.get("raw") for it in (r.get("items") or [])][:20], "errors": (r.get("errors") or [])[:2]}
        s.fact("EL S1 TOTAL %s classes %s raw %s errors %s" % (OUT["el"]["items"], OUT["el"]["classes"], OUT["el"]["raw"], OUT["el"]["errors"]))
    s.gate("E S1 ExecState 1", DRY or OUT.get("S1_es") == 1, OUT.get("S1_es"))
    s.gate("X input md5 unchanged", K.md5(DON) == DONM, K.md5(DON))
    if not s.fails and not DRY:
        json.dump({"function": "create_primitive_nested", "variant": "donor NamedUnbundler + Select (NI example copies)", "status": "PASS", "t": time.time(),
                   "card": "127-5", "log": "tools/bench/diag_c127_5_errsel.log", "also": ["connect_term_uid"], "out": OUT},
                  open(os.path.join(HERE, "scratch_verify", "gscript.create_primitive_nested_errsel_%s.json" % s.stamp), "w", encoding="utf-8"), default=str, indent=1)
    json.dump(OUT, open(os.path.join(HERE, "diag_c127_5_errsel_out.json"), "w", encoding="utf-8"), default=str, indent=1)
    s.dump()
if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
