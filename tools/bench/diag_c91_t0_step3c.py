r"""diag_c91_t0_step3c - card 91-1 (B)+(C)+(D-save) = PD197(h) step 3 in ONE LabVIEW session:
(B) a per-wire-class probe on a SCRATCH byte copy of S1 (`scratch_c91_probe_<ts>.vi`): for every distinct stamp wire
    (i I32 w3268, bool[] w5859, error cluster w541, U8 image w19465, image-data cluster w19468, picture w19429, and the
    four (A) tunnel wires w32890 / w11352 / w4906 / w19441 from tools/bench/t0_tunnel_sites_s1.json) place ONE stamp
    (CLFN + I32 constant on t6 + branch on t8), read ExecState, then delete the CLFN and the constant by uid, Remove Bad
    Wires (scratch only), and read ExecState + the site wire's sink count back.
(C) on the WORK copy `claudeDev\D1_s1_t0_<ts>.vi`: sites 0,2,8,10,11,12,13,20 (t0_sites_s1.json) + tunnel sites 3 (w32890),
    4 (w11352, shared with 5), 6 (w4906, shared with 7), 16 (w19441, shared with 17) - ALL at While-body level
    (Diagram[43]=#639 / Diagram[99]=#15266 / Diagram[20]=#25392). A wire whose (B) probe read ExecState 0 after the
    stamp is SKIPPED and logged (card pass (C)). ExecState is read after EVERY site.
    PD197(h) gates per site: Sk.2 constant created; Sk.3 CLFN re-found BY UID after every purge and node_terms_uid echo
    == CLFN uid, t6 wired; Sk.4 branch: err '', Is Broken? False, exactly ONE new sink on the site wire and its OWNER
    uid == the CLFN uid (rule-1a hazard 5.4), t8 wire == site wire; Sk.5 ExecState 1 after the site; on the FIRST
    ExecState 0 the site's CLFN + constant are deleted by uid, Remove Bad Wires, ExecState re-read, site logged REFUSED.
(D) E1 ExecState 1; CD computation_diff(S1,new): 0 rows, removed [], added == 2 x sites done, classes in
    {CallLibrary, DigitalNumericConstant}; S4 saved BY SCRIPT (ExecState 1 only) with a new md5. Q1 LabVIEW gone; Q2 pins.
FOUND FIRST (nothing new built): diag_c90_t0_step3b.py (md5 9cb6f8d1, the base; its one_site is re-cut here with the
three review gates), gscript.node_terms_uid:966 (uid echo), stagekit.delete_object (del_node by uid), stagekit
.broken_wire_count (Remove Bad Wires, allow_mutation on the scratch), g.uids, OpCreateConstOnTerm_v0 (WhileLoop only:
docs/toolkit-capabilities.md:70, 101-102 - every site here IS a While body), stagekit.connect_from_wire, wire_source_owner.
The scratch is a manual byte copy (stagekit.scratch() would name it by the stage name; the card's write glob is
claudeDev/scratch_c91_*), registered in s.scratches so close() deletes it; s.work is SWAPPED to the scratch during (B).
    py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c91_t0_step3c.log -- py -u tools/bench/diag_c91_t0_step3c.py
RUN 2 (the skip in run 1 was keyed by wire, so the `i` sites 10/20 were skipped; probe table reused, keyed by class):
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c91_t0_step3c_r2.log -- py -u tools/bench/diag_c91_t0_step3c.py --reuse-probe tools/bench/t0_sites_s1_step3c_run1.json
"""
import json, os, shutil, struct, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE)
for p in (TOOLS, os.path.join(TOOLS, "gpu"), os.path.join(TOOLS, "recipes")):
    sys.path.insert(0, p)
import stagekit as K                                                             # noqa: E402
import gscript as g                                                              # noqa: E402
import clfn_params as cp                                                         # noqa: E402
import vigraph as V                                                              # noqa: E402

DLL = os.path.join(K.CLAUDEDEV, "t0stamp.dll")
SRC = os.path.join(K.CLAUDEDEV, "D1_s1_copy.vi"); SRC_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"
EXTRA = [("kswap", os.path.join(K.CLAUDEDEV, "D1_s1_kswap_20260926_004935.vi")), ("L2-A1 bed", os.path.join(K.CLAUDEDEV, "D1_l2_a1_20260925_235224.vi"))]
PINS = tuple(K.DEFAULT_PINS) + tuple((n, p, K.md5(p)) for n, p in EXTRA)
STAMP = time.strftime("%Y%m%d_%H%M%S")
REUSE = sys.argv[sys.argv.index("--reuse-probe") + 1] if "--reuse-probe" in sys.argv else None   # run 2: a COPY of run 1's JSON
s = K.Stage(SRC, SRC_MD5, "diag_c91_t0_step3c", work_name="D1_s1_t0_%s.vi" % STAMP, pins=PINS, preload=False, deadline_min=48,
            out_json=os.path.join(HERE, "t0_sites_s1_step3c%s.json" % ("_r2" if REUSE else "")), task="card 91-1 step 3 (PD197(h))")
T_SITE, T_ANY = 6, 8
TUN = {r["site"]: r for r in json.load(open(os.path.join(HERE, "t0_tunnel_sites_s1.json"), encoding="utf-8"))["rows"]}
# (site, wire, Diagram traverse index, diagram uid, holding While uid, class label)
SITES = [(0, 3268, 43, 639, 637, "i I32"), (2, 5859, 43, 639, 637, "bool[]"), (3, TUN[3]["chosen"]["wire_uid"], 43, 639, 637, "For tunnel (Median #30306)"),
         (4, TUN[4]["chosen"]["wire_uid"], 43, 639, 637, "For tunnel (Median #29009 + FIR #28233, site 5 shares)"),
         (6, TUN[6]["chosen"]["wire_uid"], 43, 639, 637, "case tunnel (plot Z #6085 + plot dZ #5696, site 7 shares)"),
         (8, 541, 43, 639, 637, "error cluster"), (10, 19372, 99, 15266, 15173, "i I32"), (11, 19465, 99, 15266, 15173, "U8 image"),
         (12, 19468, 99, 15266, 15173, "image data"), (13, 19429, 99, 15266, 15173, "picture"),
         (16, TUN[16]["chosen"]["wire_uid"], 99, 15266, 15173, "case tunnel (circle #16788 + text #16827, site 17 shares)"),
         (20, 34066, 20, 25392, 25380, "i I32")]
PROBE = [x for x in SITES if x[0] not in (10, 20)]              # one probe per DISTINCT wire class (sites 10/20 repeat `i` I32)


def rec(name, kind, num, passing, dims, const=0):
    r = cp.record(name, kind, num, passing, dims); return r[:-5] + bytes([const]) + r[-4:]


FLAT_STAMP = (struct.pack(">i", 3) + rec("return value", "num", "I32", "value", 0) + rec("site", "num", "I32", "value", 0)
              + rec("any", "any", None, "value", 0, const=1)).hex()


def const_on_term(W, cls, li, n, t, value):
    C = K.mod("build_opcreateconstonterm_v0"); lab = json.load(open(os.path.join(K.BENCH, "opcreateconstonterm_labels.json"), encoding="utf-8"))
    vi = g.op(C.OP); vi.SetControlValue(lab["uid_ind"], 0); vi.SetControlValue(lab["err_ind"], (False, 0, "")); vi.SetControlValue("vi path", W)
    vi.SetControlValue(lab["loop_class"], cls); vi.SetControlValue(lab["loop_index"], int(li)); vi.SetControlValue(lab["index_node"], int(n)); vi.SetControlValue(lab["index_term"], int(t))
    vi.SetControlValue(lab["value_ctl"], int(value)); g._run(vi)
    out = dict(err=g._err(vi, "error out") or "", inv_err=g._err(vi, lab["err_ind"]) or "", created_uid=None)
    try:
        out["created_uid"] = int(vi.GetControlValue(lab["uid_ind"])) or None
    except Exception:                                                              # noqa: BLE001
        pass
    return out


def wire_terms(W, wire):
    rows = [x for x in K.mod("build_opconnectfromwire_v0").wire_source_owner(W, wire, n=12) if x.get("owner_uid")]
    return rows, [x for x in rows if x.get("is_source")], [x for x in rows if not x.get("is_source")]


def refind(W, u, didx, tag):
    """PD197(h): the CLFN is re-found BY UID after every purge; the node_terms_uid echo must equal the uid."""
    f = (K.mod("build_d1_m3a1").find_node(W, u, [didx], tag, quiet=True).get("found") or {}); n = f.get("nodes_index")
    echo, terms = (g.node_terms_uid(W, didx, n) if n is not None else (None, []))
    return f, n, echo, terms


def stamp(W, k, site, wire, didx, duid, loop_uid, tag):
    """One stamp at While-body level. Returns (row, ok)."""
    row = {"site": site, "wire": wire, "diagram": didx, "loop_uid": loop_uid, "clfn": None, "const": None}
    rows0, src, sinks0 = wire_terms(W, wire); row["src_owner"] = [(x.get("owner_class"), x.get("owner_uid"), x.get("i")) for x in src]; row["sinks_before"] = len(sinks0)
    s.fact("%s w%d BEFORE: %d terminal(s), source %r, %d sink(s)" % (tag, wire, len(rows0), row["src_owner"], len(sinks0)))
    s.node_mark(tag); u, nt, e = g.build_clfn(W, (200 + 70 * k, 60), DLL, "stamp", FLAT_STAMP); row["clfn"] = u
    s.gate("%s.1 CLFN #%d built at top level (%d terms)" % (tag, u, nt), bool(u) and nt == 6, repr(e))
    s.junk_purge(tag + " after build", hints=[0]); s.move_in(u, didx, (1400 + 30 * k, 900 + 60 * (k % 4))); s.junk_purge(tag + " after move", hints=[didx, 0])
    f, n, echo, _t = refind(W, u, didx, tag)
    li = s.uid_index("WhileLoop", loop_uid); r = const_on_term(W, "WhileLoop", li, n, T_SITE, site) if n is not None else {"err": "CLFN not found on Diagram[%d]" % didx}
    row["const"] = r.get("created_uid"); s.junk_purge(tag + " after const", hints=[didx, 0])
    s.gate("%s.2 constant #%r on WhileLoop[%r].N[%r].t%d (err %r / %r)" % (tag, r.get("created_uid"), li, n, T_SITE, r.get("err"), r.get("inv_err")), bool(r.get("created_uid")) and not (r.get("err") or r.get("inv_err")))
    f, n, echo, terms = refind(W, u, didx, tag + " refind"); w6 = next((t["wire"] for t in terms if t["i"] == T_SITE), 0)
    s.gate("%s.3 CLFN re-found by uid on Diagram[%d]=#%d N[%r], uid echo %r == #%d, t%d wire %r" % (tag, didx, duid, n, echo, u, T_SITE, w6), f.get("diagram_uid") == duid and echo == u and w6 != 0)
    if not (f.get("diagram_uid") == duid and echo == u and w6 != 0) or not src:
        return row, False
    r = s.connect_from_wire(didx, n, T_ANY, wire, int(src[0]["i"])); res = r.get("result") or (None, None, "no result", {}); sub = res[3] if len(res) > 3 else {}
    s.junk_purge(tag + " after branch", hints=[didx, 0]); f, n, echo, terms = refind(W, u, didx, tag + " refind2"); w8 = next((t["wire"] for t in terms if t["i"] == T_ANY), 0)
    rows1, _s1, sinks1 = wire_terms(W, wire); key0 = set((x.get("owner_uid"), x.get("i")) for x in sinks0)
    new = [x for x in sinks1 if (x.get("owner_uid"), x.get("i")) not in key0]; owners = [x.get("owner_uid") for x in new]
    row["branch"] = {"err": r.get("err") or res[2], "is_broken": sub.get("Is Broken?"), "t8_wire": w8, "sinks_after": len(sinks1), "new_sink_owners": owners}
    s.fact("%s w%d AFTER: %d sink(s) (was %d); NEW sink owner(s) %r (CLFN #%d); op readback %r" % (tag, wire, len(sinks1), len(sinks0), owners, u, sub))
    ok4 = not row["branch"]["err"] and sub.get("Is Broken?") is False and owners == [u] and w8 == wire and echo == u
    s.gate("%s.4 branch w%d -> t%d: err %r, Is Broken? %r, exactly one new sink owned by #%d (%r), t8 wire %r == site wire" % (tag, wire, T_ANY, row["branch"]["err"], sub.get("Is Broken?"), u, owners, w8), ok4)
    return row, ok4


def unstamp(W, row, tag, wire):
    """PD197(h) 5.5 / probe cleanup: delete the site's CLFN + constant BY UID, Remove Bad Wires, re-read."""
    for cls, uid in (("CallLibrary", row.get("clfn")), ("DigitalNumericConstant", row.get("const"))):
        if uid:
            s.delete_object(cls, uid, tag)
    bw = s.broken_wire_count(target=W, allow_mutation=True, tag=tag)
    alive = wire in g.uids(W, "Wire"); _r, _src, sinks = wire_terms(W, wire) if alive else ([], [], [])
    es = s.es("%s after delete + Remove Bad Wires" % tag)
    s.fact("%s UNSTAMP: bad wires removed %r, site wire w%d alive %r with %d sink(s), ExecState %r" % (tag, bw.get("bad"), wire, alive, len(sinks), es))
    return {"bad_removed": bw.get("bad"), "wire_alive": alive, "sinks_after_delete": len(sinks), "es_after_delete": es}


def body(_stage):
    W = s.start(); B = {}
    if REUSE:   # run 2 (06:0x): run 1 (diag_c91_t0_step3c.log:706) measured all 10 classes ES 1/1; its skip was keyed by WIRE, so the
        #        `i` sites 10/20 (same CLASS as site 0, not probed twice) were skipped. The probe table is REUSED, keyed by class.
        B = {v["class"]: v for v in json.load(open(REUSE, encoding="utf-8"))["probe"].values()}
        s.fact("PROBE TABLE REUSED from %s (run 1, 10 classes): %r" % (os.path.basename(REUSE), [(c, v["es_after_stamp"]) for c, v in B.items()]))
    else:
        s.head("[B] PER-WIRE-CLASS PROBE on a scratch byte copy (retrospective-cycle90 fault 1)")
        sc = os.path.join(K.CLAUDEDEV, "scratch_c91_probe_%s.vi" % STAMP); shutil.copyfile(SRC, sc); time.sleep(0.4); s.scratches.append(sc)
        s.gate("B0 scratch %s is a byte copy of S1" % os.path.basename(sc), K.md5(sc) == SRC_MD5, fatal=True)
        s.safe("ensure_loaded(scratch)", lambda: g.ensure_loaded(sc)); s.work = sc; s._nodes = None; s.es("scratch after open")
        for k, (site, wire, didx, duid, loop_uid, cls) in enumerate(PROBE):
            tag = "B%02d" % site; row, ok = stamp(sc, k, site, wire, didx, duid, loop_uid, tag); es = s.es("%s after stamp [%s]" % (tag, cls))
            s.gate("%s.5 [%s] w%d ExecState after the stamp == 1 (got %r)" % (tag, cls, wire, es), es == 1)
            un = unstamp(sc, row, tag, wire); s.gate("%s.6 [%s] after delete: wire alive, sinks back to %d, ExecState 1 (got %r)" % (tag, cls, row["sinks_before"], un["es_after_delete"]),
                                                      un["wire_alive"] and un["sinks_after_delete"] == row["sinks_before"] and un["es_after_delete"] == 1)
            B[cls] = {"site": site, "wire": wire, "class": cls, "branch_ok": ok, "es_after_stamp": es, "unstamp": un}
        s.R["probe"] = B; s.fact("PROBE TABLE wire -> (class, branch ok, ES after stamp, ES after delete): %r" % [(v["wire"], c, v["branch_ok"], v["es_after_stamp"], v["unstamp"]["es_after_delete"]) for c, v in B.items()])
        s.work = W; s._nodes = None; s.safe("close_panel(scratch)", lambda: g.close_panel(sc)); s.es("work after the probe")
    s.head("[C] THE BUILD on %s - every stamp at While-body level" % os.path.basename(W))
    rows, done, table, first0, skipped = [], [], [], None, []
    for k, (site, wire, didx, duid, loop_uid, cls) in enumerate(SITES):
        if B.get(cls, {}).get("es_after_stamp") != 1:
            s.fact("S%02d SKIPPED: probe of class [%s] read ExecState %r after the stamp (card pass (C))" % (site, cls, B.get(cls, {}).get("es_after_stamp"))); skipped.append(site); continue
        tag = "S%02d" % site; row, ok = stamp(W, k, site, wire, didx, duid, loop_uid, tag); es = s.es("after %s [%s]" % (tag, cls)); row["es_after"] = es; row["class"] = cls
        s.gate("%s.5 [%s] ExecState after site %d == 1 (got %r)" % (tag, cls, site, es), es == 1)
        if es != 1 and first0 is None:
            first0 = {"site": site, "wire": wire, "class": cls}; s.fact("FIRST SITE WITH ExecState %r: site %d w%d [%s] -> deleted (PD197(h) 5.5)" % (es, site, wire, cls))
            row["refused"] = unstamp(W, row, tag + " REFUSED", wire); es = row["refused"]["es_after_delete"]
            s.gate("%s.6 REFUSED site removed: ExecState back to 1 (got %r)" % (tag, es), es == 1); ok = False
        rows.append(row); table.append((site, ok, es))
        if ok and es == 1:
            done.append(site)
    s.R.update({"rows_t0": rows, "sites_done": done, "sites_skipped": skipped, "es_table": table, "first_es0": first0})
    s.fact("ES TABLE site -> (ok, ExecState after): %r; done %r; skipped %r" % (table, done, skipped))
    es = s.es("after all sites"); s.gate("E1 ExecState 1 after %d/%d sites" % (len(done), len(SITES)), es == 1)
    JC, Wb = K.mod("jev_candidates"), K.mod("wiki_build"); G1 = JC.load(JC.S1_KEY)
    lv = Wb.read_live(W, fs_pairs=G1["wiki"]["fs_tunnel_pairs"]); loops = json.load(open(JC._newest("graph_loops_s1_*.json"), encoding="utf-8"))["loops"]
    G2 = JC.from_parts({"terminals": lv["terminals"], "graph_summary": G1["wiki"]["graph_summary"]}, lv["objs"], loops, JC.node_labels_default(), lv["fs_tunnel_pairs"], "t0")
    cd = V.computation_diff(G1, G2); s.R["cdiff"] = {"rows": cd["rows"], "added": cd["computation_nodes_added"], "removed": cd["computation_nodes_removed"]}
    for y in cd["rows"][:20]:
        s.fact("CDIFF ROW %r" % y)
    cls = sorted(set(a["class"] for a in cd["computation_nodes_added"]))
    s.gate("CD computation_diff(S1,new): rows %d, removed %d, added %d (classes %r) == 2 x %d sites" % (len(cd["rows"]), len(cd["computation_nodes_removed"]), len(cd["computation_nodes_added"]), cls, len(done)),
           not cd["rows"] and not cd["computation_nodes_removed"] and len(cd["computation_nodes_added"]) == 2 * len(done) and set(cls) <= {"CallLibrary", "DigitalNumericConstant", "Constant"})
    if es != 1:
        s.fact("NOT SAVED: ExecState %r" % es); s.discard_work(); return
    m = s.save(); s.R["t0_vi"] = {"path": W, "md5": m, "bytes": os.path.getsize(W) if os.path.exists(W) else None, "sites": done}
    s.gate("S4 artefact md5 differs from the input", bool(m) and m != SRC_MD5, m); s.fact("T0_VI %s md5 %s" % (W, m))


if __name__ == "__main__":
    K.run(body, s)
    s.head("[Q] COM Quit, verify LabVIEW gone")
    try:      # run 2 (diag_c91_t0_step3c_r2.log:759): COM Quit blocked 90 s and the uncaught TimeoutExpired ended the script rc=1
        r = subprocess.run([sys.executable, "-c", "import win32com.client as w\nw.Dispatch('LabVIEW.Application').Quit()\n"], capture_output=True, text=True, timeout=90)
    except subprocess.TimeoutExpired:
        r = subprocess.CompletedProcess([], 124); s.fact("COM Quit blocked 90 s -> falling through to the taskkill branch")
    t0 = time.time()
    while "labview" in subprocess.run("tasklist", capture_output=True, text=True).stdout.lower() and time.time() - t0 < 60:
        time.sleep(2)
    gone = "labview" not in subprocess.run("tasklist", capture_output=True, text=True).stdout.lower()
    if not gone:
        subprocess.run(["taskkill", "/F", "/T", "/IM", "LabVIEW.exe"], capture_output=True); time.sleep(5)
        gone = "labview" not in subprocess.run("tasklist", capture_output=True, text=True).stdout.lower()
    s.gate("Q1 LabVIEW gone (quit rc %d, forced=%s)" % (r.returncode, not gone), gone)
    s.gate("Q2 md5 pins after quit", s.pin_check("FINAL")); s.dump()
    sys.exit(s.summary())
