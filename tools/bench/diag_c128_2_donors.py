r"""diag_c128_2_donors - card 128-2 (B)+(C1)+(C2), PD260(c). Plan of record: diag_c128_2_donors_plan.json (every uid, name, path).
EXISTING FIRST: 127-5's donor census (7 NI examples, 0 hits, row counts unlogged; reviews archive/peer/2026-10-02-c128-2-errsel-donor.md,
-bedcensus.md); bed + D1_s1_copy offline census = diag_c128_2_bedcensus_run2.log (NamedUnbundler 12 / Unbundler 3, 0 Select, primitive
terminal names populated). No PrimIndex reader exists (grep: 0) -> primitives by owner_class + terminal names. Routes:
create_primitive_nested(donor=) gscript.py:4782, case_wired :5067, case_frame_wire :5176, connect_term_uid :5130, errorlist_check.
PREDICTION: every candidate copy is NOT an empty read; >= 1 NamedUnbundler with a 'status' source among the error.llb copies; Select:
MEASUREMENT. C1 runs only with both donors (else NOT ATTEMPTED + reason). C2: case_wired op err '', frame names MEASURED (expected
'No Error'/'Error'), every wire Is Broken? False, ExecState 1. Input md5 unchanged, every copy deleted, LabVIEW gone.
    py tools/bgrun.py --material --max-min 38 --log tools/bench/diag_c128_2_donors.log -- py -u tools/bench/diag_c128_2_donors.py"""
import collections, json, os, shutil, sys                                                  # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K; g = K.g                                                               # noqa: E402,E702
PL = json.load(open(os.path.join(HERE, "diag_c128_2_donors_plan.json"), encoding="utf-8"))
DRY = bool(getattr(g.report_all, "_dry", False))
DON, DONM, IM, P, NM = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"], PL["imaq"], PL["pos"], PL["names"]
D, ERR = IM["diagram"], IM["err_out"]
KT, KF = [{"donor": os.path.join(g.CLAUDEDEV, PL[k]["vi"]), "uid": PL[k]["uid"]} for k in ("const_t", "const_f")]
CANDS = [os.path.join(PL["vilib_dir"], n) for n in PL["vilib"]] + [os.path.join(g.CLAUDEDEV, n) for n in PL["claudedev_donors"]]
ORIG3 = os.path.join(os.path.dirname(g.PROJECT), PL["original"])
BED, BED_UNB = os.path.join(g.CLAUDEDEV, PL["bed"]["vi"]), PL["bed"]["unb_uid"]
OUT = {"census": {}, "c1": {}, "c2": {}}
s = K.Stage(DON, DONM, "scratch_c128_2", preload=False, deadline_min=35, reserve_s=150,
            out_json=os.path.join(HERE, "diag_c128_2_donors.json"), task="card 128-2 PD260(c)")
s.close = lambda: K.Stage.close(s, expect_files=[])
def terms(W):
    import allterms
    return [] if DRY else allterms.read_terms(W, allterms.OP_ALLTERMS_V1)[0]
def nm(x): return "".join(str(x).split()).lower()
def census(tag, src, i):
    cp = os.path.join(g.CLAUDEDEV, "DonorCand_c128_2_%s.vi" % i); shutil.copyfile(src, cp); s.scratches.append(cp)   # noqa: E702
    objs, e1 = s.safe("CENSUS %s report_all" % tag, lambda: g.report_all(cp, "GObject"), [])
    rows, e2 = s.safe("CENSUS %s read_terms" % tag, lambda: terms(cp), [])
    own = collections.defaultdict(list)
    for r in rows:
        own[int(r["owner_uid"])].append(r)
    unb = {u: [(r["term_name"], r["is_source"]) for r in rs] for u, rs in own.items() if rs[0]["owner_class"] in ("NamedUnbundler", "Unbundler")}
    sel = [u for u, rs in own.items() if set(NM["sel_in"]) <= {nm(r["term_name"]) for r in rs if not r["is_source"]} and sum(r["is_source"] for r in rs) == 1]
    fsig = collections.Counter((rs[0]["owner_class"], tuple(sorted(str(r["term_name"]) for r in rs))) for rs in own.values() if rs[0]["owner_class"] in ("Function", "Comparison"))
    rec = {"src": src, "gobjects": len(objs), "terminal_rows": len(rows), "owners": len(own), "empty_read": not objs or not rows,
           "errors": [e1, e2], "classes": dict(collections.Counter(str(o["class"]) for o in objs).most_common()),
           "unbundlers": {str(u): v for u, v in unb.items()}, "select": [(u, own[u][0]["owner_class"], [r["term_name"] for r in own[u]]) for u in sel],
           "function_sigs": [[list(k), n] for k, n in fsig.most_common(30)],
           "status_unb": [u for u, v in unb.items() if any(n == NM["status"] and sv for n, sv in v)]}
    OUT["census"][tag] = rec
    s.fact("CENSUS %s: GObjects %d, terminal rows %d, owners %d%s; Unbundlers %s; status-Unbundle %s; Select %s; classes %s"
           % (tag, len(objs), len(rows), len(own), " EMPTY READ" if rec["empty_read"] else "", json.dumps(rec["unbundlers"])[:500],
              rec["status_unb"], rec["select"], json.dumps(rec["classes"])[:600]))
    s.fact("CENSUS %s Function/Comparison signatures %s" % (tag, rec["function_sigs"][:20]))
    return cp, rec, sel
def create(W, tag, dg, prim, pos, donor):
    c0 = s.census_snapshot(W)
    u = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, dg, prim, tuple(pos), donor=donor), "%s %s" % (tag, prim))["result"]
    c1 = s.census_snapshot(W); new = collections.Counter(c1[x] for x in set(c1) - set(c0))   # noqa: E702
    rows = [{"uid": int(r["term_uid"]), "name": r["term_name"], "src": bool(r["is_source"]), "cls": r.get("term_class"), "wire": int(r["wire_uid"] or 0)} for r in terms(W) if int(r["owner_uid"]) == int(u or 0)]
    OUT.setdefault("creates", {})[tag] = {"uid": u, "census": dict(new), "terms": rows}
    s.fact("CREATE %s #%s census %s terms %s" % (tag, u, dict(new), rows))
    s.gate("%s op err '' and a node" % tag, DRY or u, u)
    return (0 if DRY else int(u or 0)), rows
def pick(rows, name, src): return [0] if DRY else [r["uid"] for r in rows if r["src"] == src and (name is None or nm(r["name"]) == nm(name))]
def wire(W, tag, snk, src):
    c0 = s.census_snapshot(W); cw = s._op("connect_term_uid", lambda: g.connect_term_uid(W, snk, src), "%s #%s <- #%s" % (tag, snk, src))   # noqa: E702
    c1 = s.census_snapshot(W); res = cw["result"] or {}   # noqa: E702
    OUT.setdefault("wires", {})[tag] = {"op": res, "err": cw["err"], "census": dict(collections.Counter(c1[x] for x in set(c1) - set(c0)))}
    s.fact("WIRE %s Is Broken? %s err %r census %s" % (tag, res.get("broken"), cw["err"], OUT["wires"][tag]["census"]))
    s.gate("%s op err '' and Is Broken? False" % tag, DRY or (res and not cw["err"] and res.get("broken") is False), res)
def errorlist(W, tag):
    import errorlist_check as EC
    EC._lv_imports(); R = {"gui_acts_outer": [], "errors": []}; EC.open_diagram(W, R)   # noqa: E702
    r = EC.E.read(W, os.path.join(HERE, "errorlist_c128_2_%s_%s_raw.json" % (tag, s.stamp)), log=lambda m: None, on_item=None)
    OUT["el_" + tag] = {"items": len(r.get("items") or []), "classes": EC.class_counts(r.get("items")), "raw": [it.get("raw") for it in (r.get("items") or [])][:20]}
    s.fact("EL %s TOTAL %s classes %s raw %s" % (tag, OUT["el_" + tag]["items"], OUT["el_" + tag]["classes"], OUT["el_" + tag]["raw"]))
def body(_):
    s.start(); s.discard_work(); W = s.work                                                  # noqa: E702
    don = {"unb": {"donor": DON, "uid": 0}, "sel": {"donor": DON, "uid": 0}} if DRY else {"unb": None, "sel": None}
    for i, src in enumerate([] if DRY else CANDS):
        cp, rec, sel = census(os.path.basename(src), src, i)
        s.gate("B %s not an EMPTY READ" % os.path.basename(src), not rec["empty_read"], (rec["gobjects"], rec["terminal_rows"]))
        if rec["status_unb"] and not don["unb"]:
            don["unb"] = {"donor": cp, "uid": int(rec["status_unb"][0]), "source": src}    # every copy is a scratch: deleted at close
        if sel and not don["sel"]:
            don["sel"] = {"donor": cp, "uid": int(sel[0]), "source": src}
    if not don["unb"] and don["sel"] and not DRY:
        bc = os.path.join(g.CLAUDEDEV, "DonorCand_c128_2_bed.vi"); shutil.copyfile(BED, bc); s.scratches.append(bc)   # noqa: E702
        don["unb"] = {"donor": bc, "uid": BED_UNB, "source": BED}; s.fact("Unbundle donor = bed byte copy #%s (no 'status' element)" % BED_UNB)   # noqa: E702
    s.fact("DONORS %s" % don)
    if not (don["unb"] and don["sel"]):
        OUT["c1"] = {"status": "NOT ATTEMPTED", "why": "no %s donor in the B census" % " / ".join(k for k in ("unb", "sel") if not don[k])}
        s.fact("C1 NOT ATTEMPTED: %s" % OUT["c1"]["why"])
    else:
        u, ur = create(W, "C1unb", D, "Unbundle By Name", P["unb"], don["unb"]); sl, sr = create(W, "C1sel", D, "Select", P["sel"], don["sel"])   # noqa: E702
        kt, ktr = create(W, "C1kt", D, "const_donor", P["kt"], KT); kf, kfr = create(W, "C1kf", D, "const_donor", P["kf"], KF)   # noqa: E702
        mm, mr = create(W, "C1mm", D, "Max & Min", P["mm"], None)
        wire(W, "C1_W_unb_in", pick(ur, None, False)[0], ERR)
        ua = [r for r in terms(W) if int(r["owner_uid"]) == u]; OUT["c1"]["unb_after"] = [(r["term_name"], r["is_source"]) for r in ua]   # noqa: E702
        s.fact("C1 Unbundle after wire %s" % OUT["c1"]["unb_after"]); so = [0] if DRY else [int(r["term_uid"]) for r in ua if r["is_source"]]   # noqa: E702
        a, b, c = NM["sel_in"]
        wire(W, "C1_W_s", pick(sr, a, False)[0], so[0]); wire(W, "C1_W_t", pick(sr, b, False)[0], pick(ktr, None, True)[0])   # noqa: E702
        wire(W, "C1_W_f", pick(sr, c, False)[0], pick(kfr, None, True)[0]); wire(W, "C1_W_out", pick(mr, NM["sink_x"], False)[0], pick(sr, None, True)[0])   # noqa: E702
        OUT["c1"]["es"] = None if DRY else g.exec_state(W); s.fact("C1 ExecState %s" % OUT["c1"]["es"]); DRY or errorlist(W, "C1")   # noqa: E702
    W2 = os.path.join(g.CLAUDEDEV, "scratch_c128_2_case_%s.vi" % s.stamp); s.scratches.append(W2); DRY or shutil.copyfile(DON, W2)   # noqa: E702
    cw = s._op("case_wired", lambda: g.case_wired(W2, D, IM["uid"], IM["err_name"], P["case"]), "C2 case selector <- IMAQ Copy error out")
    c = {} if DRY else (cw["result"] or {}); OUT["c2"]["case"] = {k: c.get(k) for k in ("case", "selector_term", "selector_wire", "src_wire", "names", "frames", "exec_state", "op_err", "terms_after")}   # noqa: E702
    s.fact("C2 case %s names %s frames %s selector w%s src w%s err %r" % (c.get("case"), c.get("names"), c.get("frames"), c.get("selector_wire"), c.get("src_wire"), cw["err"]))
    s.gate("C2 case_wired op err '' and selector wired", DRY or (not cw["err"] and c.get("selector_wire")), cw["err"])
    fr = [0, 0] if DRY else (c.get("frames") or [])
    if len(fr) == 2:
        mm, mr = create(W2, "C2mm", D, "Max & Min", P["mm2"], None)
        kt, ktr = create(W2, "C2kt", int(fr[1]), "const_donor", P["k_in_frame"], KT); kf, kfr = create(W2, "C2kf", int(fr[0]), "const_donor", P["k_in_frame"], KF)   # noqa: E702
        wire(W2, "C2_W_frame1_out", pick(mr, NM["sink_x"], False)[0], pick(ktr, None, True)[0])
        tun = [0] if DRY else sorted({int(r["owner_uid"]) for r in terms(W2) if r["owner_class"] == "SelectorTunnel" and int(r["wire_uid"] or 0)})
        OUT["c2"]["tunnels"] = tun; s.fact("C2 SelectorTunnels (wired) after the frame-1 wire %s" % tun)   # noqa: E702
        kn = "" if DRY else (kfr[0]["name"] if kfr else "")
        r0 = s._op("case_frame_wire", lambda: g.case_frame_wire(W2, int(c.get("case") or 0), 0, {"node": kf, "term": kn}, {"tunnel": max(tun)}), "C2 frame 0 const -> tunnel")
        s.fact("WIRE C2_W_frame0 %s err %r" % (r0["result"], r0["err"])); s.gate("C2_W_frame0 op err '' and Is Broken? False", DRY or (not r0["err"] and (r0["result"] or {}).get("broken") is False), r0["result"])   # noqa: E702
    OUT["c2"]["es"] = None if DRY else g.exec_state(W2); s.fact("C2 ExecState %s" % OUT["c2"]["es"]); DRY or errorlist(W2, "C2")   # noqa: E702
    DRY or census("ORIGINAL_3StateClamping", ORIG3, "orig")
    s.gate("X input md5 unchanged", K.md5(DON) == DONM, K.md5(DON))
    json.dump(OUT, open(os.path.join(HERE, "diag_c128_2_donors_out.json"), "w", encoding="utf-8"), default=str, indent=1)
    s.dump()
if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
