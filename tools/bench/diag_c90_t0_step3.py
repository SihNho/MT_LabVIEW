r"""diag_c90_t0_step3 - card 90-5 = PD196(d) step 3: claudeDev\D1_s1_t0_<ts>.vi = byte copy of D1_s1_copy.vi + one t0stamp
CLFN per PD197(c) site, each in the site's OWN diagram, param1 `site` = a constant, param2 `any` = a BRANCH of the listed wire.

FOUND FIRST (nothing new built): gscript.build_clfn (top level only, place.log PL1) + stagekit.move_in (uid -> Diagram[idx],
PL2-4 uid echo); gscript.create_const_loop_term('for_n') = OpCreateConstTop_v0 (Terminal.Create Constant on ANY top-level
node terminal, sets Value; toolkit-capabilities:71); stagekit.connect_from_wire = OpConnectFromWire_v0 (sink Diagram[d].Nodes
[n].Terms[t] <- Wire(uid).Terms[i], reads Is Broken?); build_opconnectfromwire_v0.wire_source_owner (which Terms[i] is the
wire's source); build_d1_m3a1.find_node (uid -> diagram/nodes index); jev_candidates.load(S1)+wiki_build.read_live+
vigraph.computation_diff (the rule-1a diff, stage_d1_l2a1.py:98-106). Site table = tools/bench/t0_sites_s1.json (card 90-4).
SITE 1 (frame grab in #637): the wiki lists NO grab in #637 - IMAQdx Grab #15403 sits on the display body #15266 and
IMAQdx Get Image #22692 on frame diagram 22650 (diag_c90_t0_wikiq.log) -> reported and OMITTED per the card. 17 sites.
CONSTANT PLACEMENT: run 1 (diag_c90_t0_step3.log:24-30) MEASURED that a constant created at top level does NOT survive
move_in of both ends (t6 wire 0, tunnels unchanged). Run 2: the CLFN is moved first, then the constant is created IN PLACE
by OpCreateConstOnTerm_v0 addressed as <loop class>[i].Diagram.Nodes[n].Terms[6] - WhileLoop for the 7 body sites, ForLoop
(owner read live by owner_of) for the 5 For-body sites; the 4 case-frame sites (6, 7, 14, 15) are SKIPPED and reported:
no creator addresses a CaseStructure frame. Run 1 also measured that a BRANCH adds no Wire object (delta 0, Is Broken?
False) - the gate is now the CLFN's t8 wire uid == the site wire. Junk Invokes are purged after every creator (run 1 left 9).
PREDICTION CONTRACT: per site Sk.1 CLFN built (1 new CallLibrary) Sk.2 constant created (uid, no error) Sk.3 both moved,
tunnel counts unchanged, CLFN t6 wired Sk.4 branch: connect_from_wire err '' and Is Broken? False, wire delta +1;
E1 ExecState 1 after all sites; CD computation_diff(S1, new): 0 rows, removed [], added == 2 x sites of classes
{CallLibrary, DigitalNumericConstant}; S1-S3 saved by script, cold re-read ES 1; H gates; Q1 LabVIEW gone; Q2 pins.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/diag_c90_t0_step3.log -- py -u tools/bench/diag_c90_t0_step3.py
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
s = K.Stage(SRC, SRC_MD5, "diag_c90_t0_step3", work_name="D1_s1_t0_%s.vi" % STAMP, pins=PINS, preload=False, deadline_min=38,
            out_json=os.path.join(HERE, "t0_sites_s1_step3.json"), task="card 90-5 step 3")
T_SITE, T_ANY = 6, 8                                   # CLFN param k: in at 4+2k (r3 script: site ctl on t6); any in = t8
# (site, wire uid, Diagram traverse index, diagram uid, holding While uid or None) - PD197(c) + t0_sites_s1.json chains
SITES = [(0, 3268, 43, 639, 637), (2, 5859, 43, 639, 637), (3, 25157, 50, 29894, None), (4, 24106, 74, 7911, None),
         (5, 28509, 74, 7911, None), (6, 363, 76, 2235, None), (7, 7109, 75, 2265, None), (8, 541, 43, 639, 637),
         (10, 19372, 99, 15266, 15173), (11, 19465, 99, 15266, 15173), (12, 19468, 99, 15266, 15173),
         (13, 19429, 99, 15266, 15173), (14, 16210, 132, 16013, None), (15, 16183, 132, 16013, None),
         (16, 16898, 137, 16621, None), (17, 16895, 137, 16621, None), (20, 34066, 20, 25392, 25380)]
TUN = ("Tunnel", "LoopTunnel", "SelectorTunnel")


def rec(name, kind, num, passing, dims, const=0):
    r = cp.record(name, kind, num, passing, dims); return r[:-5] + bytes([const]) + r[-4:]


FLAT_STAMP = (struct.pack(">i", 3) + rec("return value", "num", "I32", "value", 0) + rec("site", "num", "I32", "value", 0)
              + rec("any", "any", None, "value", 0, const=1)).hex()


def top_index(W, uid):
    return next((k for k, r in enumerate(g.node_labels(W, 0)) if r["uid"] == uid), None)


def const_on_term(W, cls, li, n, t, value):
    """build_opcreateconstonterm_v0.create_const_on_term:364 with the loop CLASS a parameter (run 1 measured: a constant
    created at top level does NOT survive move_in of both ends - t6 wire 0, so the constant must be created IN PLACE)."""
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


def one_site(W, k, site, wire, didx, duid, loop_uid, cls):
    tag = "S%02d" % site; M = K.mod("build_d1_m3a1"); F = K.mod("build_opconnectfromwire_v0"); row = {"site": site, "wire": wire, "diagram": didx, "loop_class": cls}
    s.node_mark(tag); u, nt, e = g.build_clfn(W, (200 + 70 * k, 60), DLL, "stamp", FLAT_STAMP); row["clfn"] = u
    s.gate("%s.1 CLFN #%d built at top level (%d terms)" % (tag, u, nt), bool(u) and nt == 6, repr(e))
    s.junk_purge(tag + " after build", hints=[0]); pos = (1400 + 30 * k, 900 + 60 * (k % 4))
    s.move_in(u, didx, pos); f = (M.find_node(W, u, [didx], tag, quiet=True).get("found") or {}); n = f.get("nodes_index"); row["found"] = f
    li = s.uid_index(cls, loop_uid); r = const_on_term(W, cls, li, n, T_SITE, site); row["const"] = r
    s.junk_purge(tag + " after const", hints=[didx, 0])
    s.gate("%s.2 constant #%r on %s[%d].N[%r].t%d (err %r / %r)" % (tag, r.get("created_uid"), cls, li, n, T_SITE, r.get("err"), r.get("inv_err")), bool(r.get("created_uid")) and not (r.get("err") or r.get("inv_err")))
    terms = g.node_terms(W, didx, n) if n is not None else []; w6 = next((t["wire"] for t in terms if t["i"] == T_SITE), 0); row["t6_wire"] = w6
    ok3 = f.get("diagram_uid") == duid and w6 != 0
    s.gate("%s.3 CLFN on Diagram[%d]=#%d N[%r], t%d wire %r" % (tag, didx, duid, n, T_SITE, w6), ok3)
    if not ok3:
        return row, False
    src = [x for x in F.wire_source_owner(W, wire, n=8) if x.get("is_source")]
    if not src:
        s.gate("%s.4 wire %d has a source terminal" % (tag, wire), False); return row, False
    r = s.connect_from_wire(didx, n, T_ANY, wire, int(src[0]["i"])); res = r.get("result") or (None, None, "no result", {})
    sub = res[3] if len(res) > 3 else {}; s.junk_purge(tag + " after branch", hints=[didx, 0])
    w8 = next((t["wire"] for t in g.node_terms(W, didx, n) if t["i"] == T_ANY), 0)
    row["branch"] = {"err": r.get("err") or res[2], "is_broken": sub.get("Is Broken?"), "t8_wire": w8}
    s.gate("%s.4 branch of w%d -> t%d: err %r, Is Broken? %r, t8 wire %r (a BRANCH adds no Wire object)" % (tag, wire, T_ANY, row["branch"]["err"], sub.get("Is Broken?"), w8),
           not row["branch"]["err"] and sub.get("Is Broken?") is False and w8 == wire)
    return row, True


def body(_stage):
    W = s.start(); s.es("after open"); rows = []; done = []; B = K.mod("build_d1_v0")
    s.fact("SITE 1 OMITTED: no frame-grab node in loop #637 (Grab #15403 is on #15266, Get Image #22692 on #22650) - card 90-5 pass 1")
    for k, (site, wire, didx, duid, loop_uid) in enumerate(SITES):
        cls = "WhileLoop"
        if not loop_uid:                                  # For body: its owner loop read live (owner_of strict uid echo); a case frame has no `.Diagram`
            ocls, ouid = s.safe("owner_of(#%d)" % duid, lambda: B.owner_of(W, duid, strict=True), (None, None))[0] or (None, None)
            s.fact("S%02d owner of diagram #%d: %r #%r" % (site, duid, ocls, ouid))
            if ocls != "ForLoop":
                s.fact("S%02d SKIPPED: diagram #%d is a %r frame - OpCreateConstOnTerm_v0 addresses Loop.Diagram only (no constant creator for a case frame)" % (site, duid, ocls))
                rows.append({"site": site, "skipped": ocls}); continue
            cls, loop_uid = "ForLoop", ouid
        row, ok = one_site(W, k, site, wire, didx, duid, loop_uid, cls); rows.append(row)
        if ok:
            done.append(site)
    s.R["rows_t0"] = rows; s.R["sites_done"] = done
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
