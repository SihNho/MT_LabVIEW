r"""diag_c90_t0_step3b - card 90-6 (escalation 2 of 90-5) = PD196(d) step 3 on the PD197(g) route:
claudeDev\D1_s1_t0_<ts>.vi = byte copy of D1_s1_copy.vi + one t0stamp CLFN per site, each in the site's OWN diagram,
param1 `site` (t6) = an I32 constant created IN PLACE, param2 `any` (t8) = a BRANCH of the site wire.

FOUND FIRST (nothing new built; the run-2 script diag_c90_t0_step3.py md5 24da7f2d is the base): gscript.build_clfn (top
level only) + stagekit.move_in (OpMoveIn_v0, uid echo) + OpCreateConstOnTerm_v0 with the loop CLASS a parameter
(Traverse(<cls>)[i] -> To More Specific Class Loop -> Diagram.Nodes[n].Terms[t]; WhileLoop measured 22/0, ForLoop is
MEASURED HERE) + stagekit.connect_from_wire (OpConnectFromWire_v0, reads Is Broken? and the sink's wire uid `UID 2`)
+ build_opconnectfromwire_v0.wire_source_owner (every terminal on a wire with is_source -> the SINK COUNT reader)
+ build_d1_v0.owner_of (strict uid echo) + build_d1_m3a1.find_node + purge_junk (Invoke with ZERO wired terminals only,
so the bare CLFN is never purged) + jev_candidates/wiki_build/vigraph.computation_diff.
PD197(g) route per site: build_clfn at top level -> purge -> move_in -> const_on_term IN PLACE -> purge -> branch ->
purge -> ExecState READ (the measurement: the first site that turns ExecState 0 is named). Case-frame sites 6/7/14/15
are NOT attempted (PD197(g) scope); site 1 dropped (no grab node in #637).
PREDICTION CONTRACT: per site Sk.1 CLFN built (6 terms) Sk.2 constant created in place (uid, err '') Sk.3 CLFN found on
the site diagram (uid echo), t6 wired Sk.4 branch: err '', Is Broken? False, sink count on the site wire +1, t8 wire ==
site wire Sk.5 ExecState after the site == 1 (RECORDED per site; the table is the deliverable even when it fails);
E1 ExecState 1 after all sites; CD computation_diff(S1,new): 0 rows, removed [], added == 2 x sites, classes in
{CallLibrary, DigitalNumericConstant}; S4 saved by script with a new md5 (only if ExecState 1); H gates; Q1 LabVIEW
gone; Q2 pins. Sites 3/4/5/16/17 need owner_of(diagram) == ForLoop; a non-ForLoop owner is SKIPPED and reported.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/diag_c90_t0_step3b.log -- py -u tools/bench/diag_c90_t0_step3b.py
"""
import json, os, struct, subprocess, sys, time
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
s = K.Stage(SRC, SRC_MD5, "diag_c90_t0_step3b", work_name="D1_s1_t0_%s.vi" % STAMP, pins=PINS, preload=False, deadline_min=43,
            out_json=os.path.join(HERE, "t0_sites_s1_step3b.json"), task="card 90-6 step 3")
T_SITE, T_ANY = 6, 8                                   # CLFN param k: in at 4+2k (site ctl on t6); any in = t8
# (site, wire uid, Diagram traverse index, diagram uid, holding While uid or None=For body, owner read live)
SITES = [(0, 3268, 43, 639, 637), (2, 5859, 43, 639, 637), (8, 541, 43, 639, 637),
         (10, 19372, 99, 15266, 15173), (11, 19465, 99, 15266, 15173), (12, 19468, 99, 15266, 15173),
         (13, 19429, 99, 15266, 15173), (20, 34066, 20, 25392, 25380)]
# RUN 1 (diag_c90_t0_step3b.log:172,213,253,573,613) MEASURED: OpCreateConstOnTerm_v0 with Class Name 'ForLoop' -> the
# invoke's error 1055 on all 5 For-body sites (3/4/5/16/17; mechanism unmeasured - cast vs index, review
# archive/peer/2026-09-26-c90-t0step3b-forloop.md section 1), the CLFN left bare, ExecState 1 -> 0 at site 3 and never back.
# Run 2 = the While-body sites only (ES stayed 1 after sites 0 and 2 in run 1); For bodies need another creator route (judgement).
FOR_SITES = {3: (25157, 50), 4: (24106, 74), 5: (28509, 74), 16: (16898, 137), 17: (16895, 137)}
NOT_ATTEMPTED = {6: 363, 7: 7109, 14: 16210, 15: 16183}     # case-frame sites, PD197(g): wait for the For-body route


def rec(name, kind, num, passing, dims, const=0):
    r = cp.record(name, kind, num, passing, dims); return r[:-5] + bytes([const]) + r[-4:]


FLAT_STAMP = (struct.pack(">i", 3) + rec("return value", "num", "I32", "value", 0) + rec("site", "num", "I32", "value", 0)
              + rec("any", "any", None, "value", 0, const=1)).hex()


def const_on_term(W, cls, li, n, t, value):
    """build_opcreateconstonterm_v0.create_const_on_term:364 with the loop CLASS a parameter."""
    C = K.mod("build_opcreateconstonterm_v0"); lab = json.load(open(os.path.join(K.BENCH, "opcreateconstonterm_labels.json"), encoding="utf-8"))
    vi = g.op(C.OP); vi.SetControlValue(lab["uid_ind"], 0); vi.SetControlValue(lab["err_ind"], (False, 0, "")); vi.SetControlValue("vi path", W)
    try:                                                                           # review section 5 (claim 3): the scrub is read back
        s.fact("UID 4 right after scrub -> %r" % vi.GetControlValue(lab["uid_ind"]))
    except Exception as ex:                                                        # noqa: BLE001
        s.fact("UID 4 read after scrub raised %s" % str(ex)[:80])
    vi.SetControlValue(lab["loop_class"], cls); vi.SetControlValue(lab["loop_index"], int(li)); vi.SetControlValue(lab["index_node"], int(n)); vi.SetControlValue(lab["index_term"], int(t))
    vi.SetControlValue(lab["value_ctl"], int(value)); g._run(vi)
    out = dict(err=g._err(vi, "error out") or "", inv_err=g._err(vi, lab["err_ind"]) or "", created_uid=None)
    try:
        out["created_uid"] = int(vi.GetControlValue(lab["uid_ind"])) or None
    except Exception:                                                              # noqa: BLE001
        pass
    return out


def wire_terms(W, wire):
    F = K.mod("build_opconnectfromwire_v0")
    rows = [x for x in F.wire_source_owner(W, wire, n=12) if x.get("owner_uid")]
    return rows, [x for x in rows if x.get("is_source")], [x for x in rows if not x.get("is_source")]


def one_site(W, k, site, wire, didx, duid, loop_uid, cls):
    tag = "S%02d" % site; M = K.mod("build_d1_m3a1"); row = {"site": site, "wire": wire, "diagram": didx, "loop_class": cls, "loop_uid": loop_uid}
    rows0, src, sinks0 = wire_terms(W, wire); row["src_owner"] = [(x.get("owner_class"), x.get("owner_uid"), x.get("i")) for x in src]; row["sinks_before"] = len(sinks0)
    s.fact("%s wire w%d BEFORE: %d terminal(s), source %r, %d sink(s)" % (tag, wire, len(rows0), row["src_owner"], len(sinks0)))
    s.node_mark(tag); u, nt, e = g.build_clfn(W, (200 + 70 * k, 60), DLL, "stamp", FLAT_STAMP); row["clfn"] = u
    s.gate("%s.1 CLFN #%d built at top level (%d terms)" % (tag, u, nt), bool(u) and nt == 6, repr(e))
    s.junk_purge(tag + " after build", hints=[0]); pos = (1400 + 30 * k, 900 + 60 * (k % 4))
    row["es_bare_top"] = s.es("%s CLFN bare at top level" % tag)          # review c90-t0step3b-forloop section 5 (claim 2)
    s.move_in(u, didx, pos)
    s.junk_purge(tag + " after move", hints=[didx, 0])            # review r2-indexshift 5.1: no junk exists while an index is used
    f = (M.find_node(W, u, [didx], tag, quiet=True).get("found") or {}); n = f.get("nodes_index"); row["found"] = f
    row["es_bare_body"] = s.es("%s CLFN bare in the body" % tag)
    li = s.uid_index(cls, loop_uid); r = const_on_term(W, cls, li, n, T_SITE, site); row["const"] = r
    s.junk_purge(tag + " after const", hints=[didx, 0])
    row["es_after_const"] = s.es("%s after the constant, before the branch" % tag)   # review 5.3: t6 vs t8
    s.gate("%s.2 constant #%r on %s[%r].N[%r].t%d (err %r / %r)" % (tag, r.get("created_uid"), cls, li, n, T_SITE, r.get("err"), r.get("inv_err")), bool(r.get("created_uid")) and not (r.get("err") or r.get("inv_err")))
    # RUN 2 MEASURED (diag_c90_t0_step3b_r2.log:48-62, :268-281): move_in's junk Invoke can sort BEFORE the CLFN in Nodes[],
    # so the purge SHIFTS the CLFN's index by -1; every read after a purge re-finds the node by uid (NOT YET RERUN).
    f = (M.find_node(W, u, [didx], tag + " refind", quiet=True).get("found") or {}); n2 = f.get("nodes_index")
    if n2 != n:
        s.fact("%s Nodes index after the purge: %r -> %r (re-found by uid)" % (tag, n, n2)); n = n2; row["found_after_purge"] = f
    terms = g.node_terms(W, didx, n) if n is not None else []; w6 = next((t["wire"] for t in terms if t["i"] == T_SITE), 0); row["t6_wire"] = w6
    ok3 = f.get("diagram_uid") == duid and w6 != 0
    s.gate("%s.3 CLFN on Diagram[%d]=#%d N[%r], t%d wire %r" % (tag, didx, duid, n, T_SITE, w6), ok3)
    if not ok3 or not src:
        if not src:
            s.gate("%s.4 wire %d has a source terminal" % (tag, wire), False)
        return row, False
    r = s.connect_from_wire(didx, n, T_ANY, wire, int(src[0]["i"])); res = r.get("result") or (None, None, "no result", {})
    sub = res[3] if len(res) > 3 else {}; s.junk_purge(tag + " after branch", hints=[didx, 0])
    n3 = (M.find_node(W, u, [didx], tag + " refind2", quiet=True).get("found") or {}).get("nodes_index")   # same shift hazard after this purge
    if n3 is not None and n3 != n:
        s.fact("%s Nodes index after the branch purge: %r -> %r" % (tag, n, n3)); n = n3
    w8 = next((t["wire"] for t in g.node_terms(W, didx, n) if t["i"] == T_ANY), 0)
    rows1, _src1, sinks1 = wire_terms(W, wire)
    row["branch"] = {"err": r.get("err") or res[2], "is_broken": sub.get("Is Broken?"), "uid2": sub.get("UID 2"), "t8_wire": w8, "sinks_after": len(sinks1)}
    s.fact("%s wire w%d AFTER: %d terminal(s), %d sink(s) (was %d); op readback %r" % (tag, wire, len(rows1), len(sinks1), len(sinks0), sub))
    s.gate("%s.4 branch of w%d -> t%d: err %r, Is Broken? %r, sinks %d -> %d (+1), t8 wire %r == site wire" % (tag, wire, T_ANY, row["branch"]["err"], sub.get("Is Broken?"), len(sinks0), len(sinks1), w8),
           not row["branch"]["err"] and sub.get("Is Broken?") is False and len(sinks1) == len(sinks0) + 1 and w8 == wire)
    return row, True


def body(_stage):
    W = s.start(); s.es("after open"); rows = []; done = []; table = []; first0 = None; B = K.mod("build_d1_v0")
    s.fact("SITE 1 DROPPED (PD197(g)); case-frame sites NOT ATTEMPTED: %r; For-body sites NOT ATTEMPTED in run 2 (run 1: OpCreateConstOnTerm_v0 'ForLoop' -> 1055): %r" % (NOT_ATTEMPTED, FOR_SITES))
    for k, (site, wire, didx, duid, loop_uid) in enumerate(SITES):
        cls = "WhileLoop"
        if not loop_uid:                                  # For body: its owner loop read live (owner_of strict uid echo)
            ocls, ouid = s.safe("owner_of(#%d)" % duid, lambda: B.owner_of(W, duid, strict=True), (None, None))[0] or (None, None)
            s.fact("S%02d owner of diagram #%d: %r #%r" % (site, duid, ocls, ouid))
            if ocls != "ForLoop":
                s.fact("S%02d SKIPPED: diagram #%d owner is %r, not ForLoop" % (site, duid, ocls))
                rows.append({"site": site, "skipped": ocls}); continue
            cls, loop_uid = "ForLoop", ouid
        row, ok = one_site(W, k, site, wire, didx, duid, loop_uid, cls)
        es = s.es("after S%02d" % site); row["es_after"] = es; rows.append(row); table.append((site, ok, es))
        s.gate("S%02d.5 ExecState after site %d == 1 (got %r)" % (site, site, es), es == 1)
        if es != 1 and first0 is None:
            first0 = {"site": site, "wire": wire, "src_owner": row.get("src_owner"), "diagram": didx, "loop_class": cls, "branch": row.get("branch")}
            s.fact("FIRST SITE WITH ExecState %r: site %d, wire w%d from %r, on %s Diagram[%d]; node error text NOT READABLE (VI.Get Errors 452 unbuilt)" % (es, site, wire, row.get("src_owner"), cls, didx))
        if ok:
            done.append(site)
    s.R["rows_t0"] = rows; s.R["sites_done"] = done; s.R["es_table"] = table; s.R["first_es0"] = first0
    s.fact("ES TABLE site -> (branch ok, ExecState after): %r" % table)
    es = s.es("after all sites"); s.gate("E1 ExecState 1 after %d/%d sites" % (len(done), len(SITES)), es == 1)
    JC, Wb = K.mod("jev_candidates"), K.mod("wiki_build"); G1 = JC.load(JC.S1_KEY)
    lv = Wb.read_live(W, fs_pairs=G1["wiki"]["fs_tunnel_pairs"]); s.fact("LIVE MAP %r" % lv["secs"])
    loops = json.load(open(JC._newest("graph_loops_s1_*.json"), encoding="utf-8"))["loops"]
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
    s.gate("S4 artefact md5 differs from the input", bool(m) and m != SRC_MD5, m)
    s.fact("T0_VI %s md5 %s" % (W, m))


if __name__ == "__main__":
    rc = K.run(body, s)
    s.head("[Q] COM Quit, verify LabVIEW gone")
    r = subprocess.run([sys.executable, "-c", "import win32com.client as w\nw.Dispatch('LabVIEW.Application').Quit()\n"], capture_output=True, text=True, timeout=90)
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
