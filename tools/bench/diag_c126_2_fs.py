r"""diag_c126_2_fs - card 126-2 STEP 2 (brief_126-2.md): diag_c125_5_fsscr.py (md5 fd2d339f, 15/0 in card 126-1) re-run UNCHANGED in its
build path on a fresh never-saved P3a byte copy (plan diag_c126_2_fs_plan.json = its plan + row M-1), plus a READ-ONLY tail after its
last gate while the copy is still open: the new wires with ONE terminal and the new FlatSequenceInnerTunnels with no wire (found the
126-1 way, uids differ per run), the Error List per-class counts (lv_errorlist.read on_item=None = errorlist_check --count-only's walk,
in-process) vs the bed's recorded 55, then gscript.wire_cleanup (OpWireCleanUp_v0, card 126-2 STEP 0) on each one-terminal wire: its
Is Broken? before/after, wire_joints and presence after, census delta, Error List again.
PREDICTION: the 125-5 gates as before (K F1 F2 CEN W1 W2 X); M the tail's reads complete (cleanup echo == uid, err ''); the tail's VALUES
are a measurement (no prediction decides anything). X bed md5 unchanged, scratch deleted, LabVIEW gone.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/diag_c126_2_fs.log -- py -u tools/bench/diag_c126_2_fs.py"""
import json, os, sys, time                                                                  # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K                                                                         # noqa: E402
g = K.g
PL = json.load(open(os.path.join(HERE, "diag_c126_2_fs_plan.json"), encoding="utf-8"))
DON, DONM = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"]
DRY = bool(getattr(g.report_all, "_dry", False))
CASE, FF0 = PL["case"], PL["false_frame"]
CONST = {"donor": os.path.join(g.CLAUDEDEV, PL["const_donor"]["vi"]), "uid": PL["const_donor"]["uid"]}
BASE_EL = os.path.join(HERE, PL["errorlist_base"])
s = K.Stage(DON, DONM, "scratch_c126_2_fs", preload=False, deadline_min=38, reserve_s=150,
            out_json=os.path.join(HERE, "diag_c126_2_fs.json"), task="card 126-2 STEP 2")
OUT = {}


def dec(r):
    J = [list(x) for x in (r or {}).get("joints") or []]
    return {"joints": len(J), "loose": sum(1 for x in J if int(x[1]) & 0x100), "terms": sum(1 for x in J if int(x[1]) & 0x1),
            "free": [(i, list(x[0])) for i, x in enumerate(J) if int(x[2]) == 1 and not int(x[1]) & 0x1]}


def terms(W):
    import allterms
    return allterms.read_terms(W, allterms.OP_ALLTERMS_V1)[0]


def errlist(W, tag):
    import errorlist_check as EC
    EC._lv_imports(); R = {"gui_acts_outer": [], "errors": []}; EC.open_diagram(W, R)       # noqa: E702
    r = EC.E.read(W, os.path.join(HERE, "errorlist_c126_2_%s_%s_raw.json" % (tag, s.stamp)), log=lambda m: None, on_item=None)
    base, cc = EC.class_counts(json.load(open(BASE_EL, encoding="utf-8"))["items"]), EC.class_counts(r.get("items"))
    d = dict((k, (base.get(k, 0), cc.get(k, 0))) for k in sorted(set(base) | set(cc)) if base.get(k, 0) != cc.get(k, 0))
    s.fact("EL %s: N %s items %d errors %s; per-class delta vs the bed's 55 (bed, now) %s" % (tag, r.get("n_reported"), len(r.get("items") or []),
           (r.get("errors") or [])[:2], d))
    return {"n": r.get("n_reported"), "items": len(r.get("items") or []), "delta": d}


def tail(W, wn, jt, c3):
    rows = terms(W)
    one = [w for w in wn if jt.get(w, {}).get("terms") == 1]
    tuns = [u for u, c in c3.items() if c == "FlatSequenceInnerTunnel"]
    bare = [u for u in tuns if not any(int(r["owner_uid"]) == u and int(r["wire_uid"] or 0) for r in rows)]
    for w in one:
        s.fact("ONE-TERMINAL w%s on %s" % (w, [(r["owner_class"], r["owner_uid"], r["term_name"], r["is_source"], r["frame_diagram"]) for r in rows if int(r["wire_uid"] or 0) == w]))
    s.fact("FS tunnels %s, with no wire %s" % (sorted(tuns), bare))
    OUT.update(one_terminal=one, tunnels_unwired=bare, el_after_connect=errlist(W, "fs_after_connect"))
    c4 = s.census_snapshot()
    for w in one:
        cu = g.wire_cleanup(W, w)
        pres = w in g.uids(W, "Wire")
        OUT.setdefault("cleanup", {})[w] = {"op": cu, "present_after": pres, "joints_after": dec(g.wire_joints(W, w)) if pres else None}
        s.fact("CLEANUP w%s %s" % (w, OUT["cleanup"][w]))
        s.gate("M cleanup w%s echo == uid, err ''" % w, cu["echo"] == w and not cu["err"], cu)
    c5 = s.census_snapshot()
    OUT["census_cleanup"] = {"new": sorted((c5[u], u) for u in set(c5) - set(c4)), "gone": sorted((c4[u], u) for u in set(c4) - set(c5))}
    s.fact("CENSUS cleanup delta %s; ES %s" % (OUT["census_cleanup"], g.exec_state(W)))
    OUT["el_after_cleanup"] = errlist(W, "fs_after_cleanup")


def body(_):
    s.start(); s.discard_work(); W = s.work                                                  # noqa: E702
    fr = g.case_frames(W, CASE); names = [str(n).strip() for n in fr["names"]]              # noqa: E702
    ff = FF0 if DRY else (int(fr["frames"][names.index("False")]) if "False" in names else 0)
    s.gate("K case #%s frames %s, False = Diagram #%s" % (CASE, names, ff), DRY or ff == FF0, fr)
    c0 = s.census_snapshot()
    cp = s._op("struct_copy_nested", lambda: g.struct_copy_nested(W, ff, "FlatSequence", g.fs_donor(), (60, 60)), "FS -> #%s" % ff)["result"] or {}
    fs = 1 if DRY else int(cp.get("uid") or 0)
    s.gate("F1 one new FlatSequence #%s owned by Diagram #%s" % (fs, ff), DRY or bool(fs), cp)
    if not fs:
        return s.dump()
    f1 = g.fs_frames(W, fs)
    a1 = s._op("fs_add_frame", lambda: g.fs_add_frame(W, fs, 0, True), "after 0")["result"] or {}
    a2 = s._op("fs_add_frame", lambda: g.fs_add_frame(W, fs, 1, True), "after 1")["result"] or {}
    f3 = g.fs_frames(W, fs)["frames"]
    s.gate("F2 3 frames; first stays leftmost; add(0,T) new at 1, add(1,T) new at 2", DRY or (len(f3) == 3 and f3[0] == f1["frames"][0]
           and f3[1] == a1.get("new_frame") and f3[2] == a2.get("new_frame")), (f1, f3))
    f3 = [0, 0, 0] if DRY else f3
    s.census_gate("CEN census delta of FS copy + 2 Add Frame == FlatSequence 1 + Diagram 3", c0, s.census_snapshot(), {"FlatSequence": 1, "Diagram": 3})
    if len(f3) != 3:
        return s.dump()
    k = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, f3[0], "I32 const", (40, 40), donor=CONST), "const -> frame 1")["result"]
    m = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, f3[1], "Max & Min", (60, 40)), "Max & Min -> frame 2")["result"]
    rows = terms(W)
    src = [r for r in rows if int(r["owner_uid"]) == int(k or 0) and r["is_source"]]
    snk = [r for r in rows if int(r["owner_uid"]) == int(m or 0) and not r["is_source"] and str(r["term_name"]) == "x"]
    if not DRY and not (len(src) == 1 and len(snk) == 1):
        s.gate("W0 exactly one const output and one Max & Min x", False, (len(src), len(snk)))
        return s.dump()
    ku, su = (0, 0) if DRY else (int(snk[0]["term_uid"]), int(src[0]["term_uid"]))
    c2, wb = s.census_snapshot(), set(g.uids(W, "Wire"))
    cw = s._op("connect_term_uid", lambda: g.connect_term_uid(W, ku, su), "x <- const")["result"] or {}
    c3, wn = s.census_snapshot(), sorted(set(g.uids(W, "Wire")) - wb)
    tun = [(c3[u], u) for u in sorted(set(c3) - set(c2)) if "Tunnel" in c3[u] or "Terminal" in c3[u]]
    s.gate("W1 op err '', Is Broken? False, >= 1 tunnel-class object new %s" % tun, DRY or (cw and not cw.get("err") and cw.get("broken") is False and bool(tun)), (cw, tun))
    jt = dict((w, dec(g.wire_joints(W, w))) for w in wn)
    s.fact("JOINTS %s" % jt)
    s.gate("W2 wire_joints free ends 0 on every new wire %s" % wn, DRY or (bool(jt) and all(not v["free"] for v in jt.values())), jt)
    if not DRY:
        tail(W, wn, jt, dict((u, c3[u]) for u in set(c3) - set(c2)))
    s.gate("X bed md5 unchanged", K.md5(DON) == DONM, K.md5(DON))
    json.dump(OUT, open(os.path.join(HERE, "diag_c126_2_fs_out.json"), "w", encoding="utf-8"), default=str, indent=1)
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
