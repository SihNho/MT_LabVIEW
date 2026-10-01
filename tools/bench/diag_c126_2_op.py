r"""diag_c126_2_op - card 126-2 STEP 0 + STEP 1 (brief_126-2.md, PD253(d)): the Wire method that cleans up ONE wire, an op that invokes it
by uid, its hygiene, and its effect on stub w27378 of a never-saved P3a byte copy.
EXISTING FIRST: no op invokes a Wire METHOD (gscript: wire_joints/OpWireJoints_v1 reads Joints[] only; the connect ops read Is Broken?
inside); Wire method ids exist only in a peer answer (peer_c90_orphan_wires.log:84) -> MEASURED here the FS_METHODS way
(diag_c125_4fsm.py: build_invoke per candidate id, the Invoke's own method-terminal name). Op built as diag_c125_5_opfs.py build_adder
(OpSetIndexMode_v0 copy, retarget, build_invoke); hygiene = gscript.hygiene_run (card 126-1); Error List = lv_errorlist.read with
on_item=None (= errorlist_check --count-only's walk) IN-PROCESS on the never-saved copy (a file-copy read cannot see in-memory edits);
per-class counts = errorlist_check.class_counts; the copy's STARTING counts = the recorded read of the same bed md5
(errorlist_D1_ring_p3a_20261001_180540_20261001_181801.json, 55 items).
PREDICTION: M1 exactly ONE of Wire 6370C00..0F makes an Invoke whose method terminal is 'Clean Up Wire' / B OpWireCleanUp_v0 ES 1, saved,
COLD ES 1 / H hygiene_run 2,000 calls on byte copies of the NI For Loop example: PASS (0 errors, h_closed +-100) / S1 w27378 present,
cleanup echo 27378 err '' (the AFTER values are a MEASUREMENT, no prediction) / X bed md5 unchanged, scratch deleted, LabVIEW gone.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/diag_c126_2_op.log -- py -u tools/bench/diag_c126_2_op.py"""
import json, os, shutil, sys, time, traceback                                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import diag_c100_verbs_build as V                                                          # noqa: E402
import allterms                                                                            # noqa: E402
import errorlist_check as EC                                                               # noqa: E402
g, P, bench_prep, gate, fact, md5 = V.g, V.P, V.bench_prep, V.gate, V.fact, V.md5             # noqa: E702
CD, KEY = g.CLAUDEDEV, "OpWireCleanUp_v0"
OP = os.path.join(CD, KEY + ".vi")
EX = os.path.join(CD, "NIScriptingExamples", "Structures", "VI Scripting with Structures - For Loop.vi")
BED, BEDM, WSTUB = os.path.join(CD, "D1_ring_p3a_20261001_180540.vi"), "4dfa44aac8fb32f706b3eb792ee7d3cc", 27378
BASE_EL = os.path.join(HERE, "errorlist_D1_ring_p3a_20261001_180540_20261001_181801.json")
TS, SCRS, OUT = time.strftime("%Y%m%d_%H%M%S"), [], {}
g._run.__defaults__ = (6.0, 120.0)


def scr(tag, src):
    p = os.path.join(CD, "scratch_c126_2_%s_%s.vi" % (tag, TS)); shutil.copyfile(src, p); SCRS.append(p); time.sleep(0.2); return p  # noqa: E702


def probe():
    t = scr("probe", EX); g.ensure_loaded(t); hits = {}                                      # noqa: E702
    for k in range(16):
        mid, inv0 = "6370C%02X" % k, set(g.uids(t, "Invoke"))
        try:
            g.build_invoke(t, "VI Server:Wire", mid, (40 + 160 * (k % 8), 300 + 120 * (k // 8))); e = ""   # noqa: E702
        except Exception as ex:                                                              # noqa: BLE001
            e = str(ex)[:120]
        names = []
        for u in sorted(set(g.uids(t, "Invoke")) - inv0):
            _e, rr = g.node_terms_uids(t, 0, g._node_index(t, 0, u))
            names = [str(r["name"]) for r in rr if str(r["name"]) not in V.STD]
        fact("PROBE Wire %s" % mid, (e, names))
        if names and names[0] != "Method":
            hits[names[0]] = mid
    g.close_panel(t)
    OUT["WIRE_METHODS"] = hits
    return gate("M1 exactly one Wire candidate is 'Clean Up Wire' %s" % hits, "Clean Up Wire" in hits, hits) and hits["Clean Up Wire"]


def build(mid):
    for p in (OP,):
        os.path.exists(p) and os.remove(p)
    b = V.B("OpSetIndexMode_v0.vi", KEY + ".vi")
    if not gate("B D donor OpSetIndexMode_v0 copy ES 1", g.exec_state(b.op) == 1):
        return False
    tm, p = V.retarget(b, KEY, "VI Server:Wire", [("632A813", False), ("6371004", False)], (900, 450))
    if not tm:
        return False
    b.w(tm, "error out", p, "error in (no error)", sc="Function", branch=b.wired(tm, "error out", True))
    inv = int(g.build_invoke(b.op, "VI Server:Wire", mid, (1100, 450))[-1]["uid"]); b.inv0.add(inv); b.purge()  # noqa: E702
    fact("B Invoke census", [(r["i"], r["name"], r["is_source"]) for r in b.terms(inv)[1]])
    b.w(tm, "specific class reference", inv, "reference", sc="Function", dc="Invoke", branch=True)
    b.w(p, "error out", inv, "error in (no error)", dc="Invoke")
    p2 = b.pn("VI Server:Wire", [("6371004", False)], (1300, 450))
    b.w(inv, "reference out", p2, "reference", sc="Invoke")
    b.w(inv, "error out", p2, "error in (no error)", sc="Invoke")
    o1, o2 = b.data(p, True), b.data(p2, True); fact("B PN outputs", (o1, o2))                 # noqa: E702
    lab = {"UID": b.ind(p, o1[0]), "before": b.ind(p, o1[1]), "after": b.ind(p2, o2[0]), "Err": b.ind(p2, "error out"),
           "method": mid, "uids": {"tmsc": tm, "pn": p, "inv": inv, "pn2": p2}}
    b.finish(KEY, lab)
    return KEY in V.LAB


def hyg():
    st = {}

    def warm(c):
        st["uid"] = int(g.report_all(c, "Wire")[0]["uid"])

    def work(c):
        if st.get("path") != c:
            st["path"], st["i"] = c, g._uid_index(c, "Wire", st["uid"])
        return g.wire_cleanup(c, st["uid"], index=st["i"])["err"]
    rec = g.hygiene_run(OP, work, EX, total=2000, per_round=100, recycle=True, warm=warm, card="126-2", log="tools/bench/diag_c126_2_op.log",
                        check=lambda c: [] if st["uid"] in g.uids(c, "Wire") else ["wire #%s gone" % st["uid"]], say=lambda m: fact("HYG", m),
                        workload_text="Wire.Clean Up Wire on the first Wire of fresh never-saved byte copies of %s, 20 x 100" % os.path.basename(EX))
    return gate("H hygiene_run %s: %s calls, %s errors, max dev %s" % (KEY, rec["calls"], rec["errors"], rec["max_dev_closed"]), rec["status"] == "PASS", rec)


def dec(r):
    J = [list(x) for x in (r or {}).get("joints") or []]
    return {"joints": len(J), "loose": sum(1 for x in J if int(x[1]) & 0x100), "terms": sum(1 for x in J if int(x[1]) & 0x1),
            "free": [(i, list(x[0])) for i, x in enumerate(J) if int(x[2]) == 1 and not int(x[1]) & 0x1]}


def reads(t, w, tag):
    present = w in g.uids(t, "Wire")
    rows = allterms.read_terms(t, allterms.OP_ALLTERMS_V1)[0]
    on = [(r["owner_class"], r["owner_uid"], r["term_name"], bool(r["is_source"]), r["term_uid"]) for r in rows if int(r["wire_uid"] or 0) == w]
    r = {"present": present, "joints": dec(g.wire_joints(t, w)) if present else None, "terms": on, "es": g.exec_state(t)}
    fact("S1 %s w%s" % (tag, w), r)
    return r


def errlist(t, tag):
    EC._lv_imports(); R = {"gui_acts_outer": [], "errors": []}                               # noqa: E702
    R["bd"] = EC.open_diagram(t, R)
    r = EC.E.read(t, os.path.join(HERE, "errorlist_c126_2_%s_%s_raw.json" % (tag, TS)), log=lambda m: None, on_item=None)
    cc = EC.class_counts(r.get("items"))
    fact("EL %s: N %s items %d errors %s" % (tag, r.get("n_reported"), len(r.get("items") or []), (r.get("errors") or [])[:3]), cc)
    return {"n": r.get("n_reported"), "items": len(r.get("items") or []), "counts": cc}


def delta(a, b):
    return dict((k, (a.get(k, 0), b.get(k, 0))) for k in sorted(set(a) | set(b)) if a.get(k, 0) != b.get(k, 0))


def step1():
    t = scr("s1", BED); g.open_panel(t); time.sleep(1)                                      # noqa: E702
    c0 = dict((int(o["uid"]), str(o["class"])) for o in g.report_all(t, "GObject"))
    b = reads(t, WSTUB, "BEFORE")
    if not gate("S1 w%s present on the byte copy" % WSTUB, b["present"], b):
        return
    cu = g.wire_cleanup(t, WSTUB); fact("S1 wire_cleanup", cu)                               # noqa: E702
    gate("S1 cleanup echo %s err ''" % WSTUB, cu["echo"] == WSTUB and not cu["err"], cu)
    a = reads(t, WSTUB, "AFTER")
    c1 = dict((int(o["uid"]), str(o["class"])) for o in g.report_all(t, "GObject"))
    cd = {"new": sorted((c1[u], u) for u in set(c1) - set(c0)), "gone": sorted((c0[u], u) for u in set(c0) - set(c1))}
    fact("S1 census delta", cd)
    base = EC.class_counts(json.load(open(BASE_EL, encoding="utf-8"))["items"])
    el = errlist(t, "s1_after")
    fact("S1 Error List per-class delta vs the bed's recorded 55 (before, after)", delta(base, el["counts"]))
    OUT["step1"] = {"before": b, "cleanup": cu, "after": a, "census": cd, "errlist_after": el, "errlist_delta": delta(base, el["counts"])}
    g.close_panel(t)


try:
    bench_prep.restart_labview(); g.reset(); time.sleep(3)                                   # noqa: E702
    mid = probe()
    if mid and build(mid):
        V.LAB["WIRE_METHODS"] = OUT["WIRE_METHODS"]; json.dump(V.LAB, open(g.C126_LABELS, "w", encoding="utf-8"), indent=1)  # noqa: E702
        g.reset(); bench_prep.restart_labview(); g.reset(); time.sleep(3)                   # noqa: E702
        if gate("C COLD ExecState 1", g.exec_state(OP) == 1, md5(OP)) and hyg():
            step1()
    gate("X bed md5 unchanged", md5(BED) == BEDM, md5(BED))
except Exception as e:                                                                    # noqa: BLE001
    traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300])  # noqa: E702
finally:
    json.dump(OUT, open(os.path.join(HERE, "diag_c126_2_op_out.json"), "w", encoding="utf-8"), default=str, indent=1)
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
