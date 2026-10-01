r"""diag_c126_4_op - card 126-4 STEP 0 + STEP 1 (brief_126-4.md, PD254(c), PD253(d)); retry of diag_c126_2_op.py (FAIL = its gate M1
matched a spaced literal 'Clean Up Wire'; LabVIEW's data names are CleanUpWire / RemoveLooseEnds, diag_c126_2_op.log:8,11).
EXISTING FIRST: Wire method ids already MEASURED (diag_c126_2_op.log:3-18) -> no probe; ONE op on 6370C08, M1 = the built Invoke's
method terminal is LabVIEW's data name 'RemoveLooseEnds' (id AND name). Op built as diag_c126_2_op.build (OpSetIndexMode_v0 copy,
retarget, build_invoke); gscript.wire_remove_loose_ends (renamed from wire_cleanup) calls it; hygiene = gscript.hygiene_run only
(PD242(b): recycle the never-saved scratch at fixed call counts); Error List = lv_errorlist.read on_item=None (= errorlist_check
--count-only --role scratch's walk) IN-PROCESS on the never-saved P3a byte copy, BEFORE and AFTER.
PREDICTION: M1 Invoke 6370C08 method terminal == 'RemoveLooseEnds' / B OpWireRemoveLooseEnds_v0 ES 1, saved, COLD ES 1 / H hygiene_run
2,000 calls on byte copies of the NI For Loop example: PASS (0 errors, wire kept, h_closed +-100, refs live 0) / S1 w27378 present,
BEFORE joints LOOSE >= 1 (joint 3, diag_c125_joints.log:26,39), op echo 27378 err '', Error List BEFORE == the bed's recorded 55 / the AFTER
values are a MEASUREMENT (no prediction) / X bed md5 unchanged, scratch deleted, LabVIEW gone.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c126_4_op.log -- py -u tools/bench/diag_c126_4_op.py"""
import json, os, shutil, sys, time, traceback                                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import diag_c100_verbs_build as V                                                          # noqa: E402
import allterms                                                                            # noqa: E402
import errorlist_check as EC                                                               # noqa: E402
g, P, bench_prep, gate, fact, md5 = V.g, V.P, V.bench_prep, V.gate, V.fact, V.md5             # noqa: E702
CD, KEY, MID, MNAME = g.CLAUDEDEV, "OpWireRemoveLooseEnds_v0", "6370C08", "RemoveLooseEnds"
OP = os.path.join(CD, KEY + ".vi")
EX = os.path.join(CD, "NIScriptingExamples", "Structures", "VI Scripting with Structures - For Loop.vi")
BED, BEDM, WSTUB = os.path.join(CD, "D1_ring_p3a_20261001_180540.vi"), "4dfa44aac8fb32f706b3eb792ee7d3cc", 27378
BASE_EL = os.path.join(HERE, "errorlist_D1_ring_p3a_20261001_180540_20261001_181801.json")
TS, SCRS, OUT = time.strftime("%Y%m%d_%H%M%S"), [], {}
g._run.__defaults__ = (6.0, 120.0)


def build():
    os.path.exists(OP) and os.remove(OP)
    b = V.B("OpSetIndexMode_v0.vi", KEY + ".vi")
    if not gate("B D donor OpSetIndexMode_v0 copy ES 1", g.exec_state(b.op) == 1):
        return False
    tm, p = V.retarget(b, KEY, "VI Server:Wire", [("632A813", False), ("6371004", False)], (900, 450))
    if not tm:
        return False
    b.w(tm, "error out", p, "error in (no error)", sc="Function", branch=b.wired(tm, "error out", True))
    inv = int(g.build_invoke(b.op, "VI Server:Wire", MID, (1100, 450))[-1]["uid"]); b.inv0.add(inv); b.purge()  # noqa: E702
    names = [str(r["name"]) for r in b.terms(inv)[1] if str(r["name"]) not in V.STD]
    if not gate("M1 Invoke %s method terminal == %r (id AND data name) %s" % (MID, MNAME, names), names[:1] == [MNAME], names):
        return False
    b.w(tm, "specific class reference", inv, "reference", sc="Function", dc="Invoke", branch=True)
    b.w(p, "error out", inv, "error in (no error)", dc="Invoke")
    p2 = b.pn("VI Server:Wire", [("6371004", False)], (1300, 450))
    b.w(inv, "reference out", p2, "reference", sc="Invoke")
    b.w(inv, "error out", p2, "error in (no error)", sc="Invoke")
    o1, o2 = b.data(p, True), b.data(p2, True); fact("B PN outputs", (o1, o2))                 # noqa: E702
    lab = {"UID": b.ind(p, o1[0]), "before": b.ind(p, o1[1]), "after": b.ind(p2, o2[0]), "Err": b.ind(p2, "error out"),
           "method": MID, "method_name": MNAME, "uids": {"tmsc": tm, "pn": p, "inv": inv, "pn2": p2}}
    b.finish(KEY, lab)
    return KEY in V.LAB


def hyg():
    st = {}

    def warm(c):
        st["uid"] = int(g.report_all(c, "Wire")[0]["uid"])

    def work(c):
        if st.get("path") != c:
            st["path"], st["i"] = c, g._uid_index(c, "Wire", st["uid"])
        return g.wire_remove_loose_ends(c, st["uid"], index=st["i"])["err"]
    rec = g.hygiene_run(OP, work, EX, total=2000, per_round=100, recycle=True, warm=warm, card="126-4", log="tools/bench/diag_c126_4_op.log",
                        check=lambda c: [] if st["uid"] in g.uids(c, "Wire") else ["wire #%s gone" % st["uid"]], say=lambda m: fact("HYG", m),
                        workload_text="Wire.RemoveLooseEnds 6370C08 on the first (healthy) Wire of fresh never-saved byte copies of %s, 20 x 100"
                        % os.path.basename(EX))
    return gate("H hygiene_run %s: %s calls, %s errors, max dev %s, refs %s" % (KEY, rec["calls"], rec["errors"], rec["max_dev_closed"],
                rec["refs_live_delta"]), rec["status"] == "PASS", rec)


def dec(r):
    J = [list(x) for x in (r or {}).get("joints") or []]
    return {"joints": len(J), "loose": sum(1 for x in J if int(x[1]) & 0x100), "terms": sum(1 for x in J if int(x[1]) & 0x1),
            "free": [(i, list(x[0])) for i, x in enumerate(J) if int(x[2]) == 1 and not int(x[1]) & 0x1], "raw": J}


def reads(t, w, tag):
    present = w in g.uids(t, "Wire")
    rows = allterms.read_terms(t, allterms.OP_ALLTERMS_V1)[0]
    on = [(r["owner_class"], r["owner_uid"], r["term_name"], bool(r["is_source"]), r["term_uid"]) for r in rows if int(r["wire_uid"] or 0) == w]
    r = {"present": present, "joints": dec(g.wire_joints(t, w)) if present else None, "terms": on, "es": g.exec_state(t)}
    fact("S1 %s w%s" % (tag, w), r)
    return r


def errlist(t, tag, base):
    EC._lv_imports(); R = {"gui_acts_outer": [], "errors": []}                               # noqa: E702
    EC.open_diagram(t, R)
    r = EC.E.read(t, os.path.join(HERE, "errorlist_c126_4_%s_%s_raw.json" % (tag, TS)), log=lambda m: None, on_item=None)
    cc = EC.class_counts(r.get("items"))
    d = dict((k, (base.get(k, 0), cc.get(k, 0))) for k in sorted(set(base) | set(cc)) if base.get(k, 0) != cc.get(k, 0))
    fact("EL %s: N %s items %d errors %s; per-class delta vs the bed's 55 (bed, now) %s" % (tag, r.get("n_reported"), len(r.get("items") or []),
         (r.get("errors") or [])[:3], d), cc)
    return {"n": r.get("n_reported"), "items": len(r.get("items") or []), "counts": cc, "delta": d}


def step1():
    t = os.path.join(CD, "scratch_c126_4_s1_%s.vi" % TS); shutil.copyfile(BED, t); SCRS.append(t); time.sleep(0.3)  # noqa: E702
    g.open_panel(t); time.sleep(1)                                                          # noqa: E702
    base = EC.class_counts(json.load(open(BASE_EL, encoding="utf-8"))["items"])
    e0 = errlist(t, "s1_before", base)
    gate("S1 Error List BEFORE == the bed's recorded 55, per-class delta {}", e0["items"] == 55 and not e0["delta"], e0)
    c0 = dict((int(o["uid"]), str(o["class"])) for o in g.report_all(t, "GObject"))
    b = reads(t, WSTUB, "BEFORE")
    ok = gate("S1 w%s present, BEFORE loose joints >= 1" % WSTUB, b["present"] and b["joints"]["loose"] >= 1, b)
    OUT["step1"] = {"errlist_before": e0, "before": b}
    if not ok:
        return
    cu = g.wire_remove_loose_ends(t, WSTUB); fact("S1 wire_remove_loose_ends", cu)           # noqa: E702
    gate("S1 op echo %s err ''" % WSTUB, cu["echo"] == WSTUB and not cu["err"], cu)
    a = reads(t, WSTUB, "AFTER")
    c1 = dict((int(o["uid"]), str(o["class"])) for o in g.report_all(t, "GObject"))
    cd = {"new": sorted((c1[u], u) for u in set(c1) - set(c0)), "gone": sorted((c0[u], u) for u in set(c0) - set(c1))}
    fact("S1 census delta", cd)
    e1 = errlist(t, "s1_after", base)
    OUT["step1"].update(op=cu, after=a, census=cd, errlist_after=e1)
    g.close_panel(t)


try:
    bench_prep.restart_labview(); g.reset(); time.sleep(3)                                   # noqa: E702
    if build():
        json.dump(V.LAB, open(g.C126_LABELS, "w", encoding="utf-8"), indent=1)
        g.reset(); bench_prep.restart_labview(); g.reset(); time.sleep(3)                   # noqa: E702
        if gate("C COLD ExecState 1", g.exec_state(OP) == 1, md5(OP)) and hyg():
            step1()
    gate("X bed md5 unchanged", md5(BED) == BEDM, md5(BED))
except Exception as e:                                                                    # noqa: BLE001
    traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300])  # noqa: E702
finally:
    json.dump(OUT, open(os.path.join(HERE, "diag_c126_4_op_out.json"), "w", encoding="utf-8"), default=str, indent=1)
    V.subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    gate("X LabVIEW gone", "labview.exe" not in V.subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower())
    for p in SCRS:
        os.path.exists(p) and os.remove(p)
    gate("X scratch copies deleted", not any(os.path.exists(p) for p in SCRS), len(SCRS))
    bad = [k for k, v in V.G.items() if not v]
    arts = [{"path": p, "md5": md5(p)} for p in (OP, g.C126_LABELS) if os.path.exists(p)]
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(V.G) - len(bad), len(bad), bad), flush=True)
    print(P.result_line(P.make_result(len(V.G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
    sys.exit(1 if bad else 0)
