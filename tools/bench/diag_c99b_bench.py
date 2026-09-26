r"""diag_c99b_bench - card 99-2 F3 + F4 on two NEW scratch VIs (claudeDev\scratch_c99b_*), built from EMPTY_v0 by script,
RUN (card flag run_vi, scratch only), timed by t0stamp v2 CLFN stamps, then deleted. D1_s1_copy.vi is never opened.

FOUND FIRST (reused, nothing new built): diag_c90_t0stamp_scratch.py (temp typed CLFN -> create_control/indicator gives
typed array controls; FLAT_STAMP record; graceful COM Quit flushes the DLL at DLL_PROCESS_DETACH; t0_siteSS_pidP.bin =
int64 [freq, stamps...]); gscript.for_loop / create_const_loop_term('for_n') (77-3 cold) / add_shift_reg + wire_sr
ForLoop (INDEX rows 37-39) / drop_subvi / wire_control / wire / set_index_mode; stagekit.Stage.move_in (c90/c91 moved
stamp CLFNs and probe_move_ctlterm moved ControlTerminals into bodies). Subvi paths: main_vi_subvis.json:237-300
(Median Filter.vi, FIR Filter (DBL).vi = the instance #28233 resolves to, Smoothing Filter Coefficients.vi).
Ring shape: diag_c99b_lvread.json (#8972 element repr, #8984 dim 1) + '# FD points' 20000 (facts_c99_display.json F1b).

F3 (scratch A): ctl `ring` [NB][D1][20000] -> For(N=NITER) shift register; body: stamp(site 0 unwired, `any` NON-const =
     an in-place modifier) left->right. Blocks: A-open, A-closed (panel), then the `ring` INDICATOR's terminal is moved into
     the body and wired from the left SR (the L1 branch): B-open, B-closed. Per-iteration = diff of consecutive site-0 stamps.
F4 (scratch B): ctls rowZ,rowF [NB][20000] DBL, hw I32 (=1, the panel defaults of both half-widths) ; stamp A(site 1,
     `any`<-hw) -> hw into a For body holding Median Filter (X<-rowZ[i], left/right rank<-hw), Smoothing Filter
     Coefficients (half-width<-hw) -> FIR Filter (DBL) (X<-rowF[i]); Median 'Filtered X' -> indexing out -> stamp B(site 2).
     Per call = B - A, NCALL COM runs. NOT included vs S1's set: IndexArray #8741, Subtract #8764, Split #27716, Bundler
     #11310, BuildArray #11261, #8323 write (all O(20000) copies, no filters).
PREDICTION CONTRACT: T1 typed controls created (labels) T2 For N const created, SR wired, stamp in body, ExecState 1 (A)
 T3 A blocks ran NITER iterations each T4 indicator moved into body + wired, ExecState 1 (B) T5 B blocks ran
 T6 F4 VI ExecState 1 (indexing on rowZ/rowF, N from them) T7 NCALL runs T8 stamp files hold the expected counts after a
 graceful quit T9 handles flat +-100 over the F4 runs  + stagekit K/H gates, LabVIEW gone (Z). RESULT line last (C6).
"""
import glob, json, os, shutil, struct, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE)
for p in (TOOLS, os.path.join(TOOLS, "gpu"), os.path.join(TOOLS, "recipes")):
    sys.path.insert(0, p)
import stagekit as K                                                             # noqa: E402
import gscript as g                                                              # noqa: E402
import clfn_params as cp                                                         # noqa: E402

DLL = os.path.join(K.CLAUDEDEV, "t0stamp.dll"); OUTDIR = os.path.join(K.CLAUDEDEV, "t0stamp_out")
EMPTY = os.path.join(K.CLAUDEDEV, "EMPTY_v0.vi")
LIB = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Analysis\3filter.llb"
MEDIAN, FIR, COEF = (os.path.join(LIB, n) for n in ("Median Filter.vi", "FIR Filter (DBL).vi", "Smoothing Filter Coefficients.vi"))
PL = json.load(open(os.path.join(HERE, "diag_c99b_benchplan.json"), encoding="utf-8"))
NB, NPT, NITER, NCALL = (int(PL["sizes"][k]) for k in ("NB", "NPT", "NITER", "NCALL"))
POS = dict((k, tuple(v)) for k, v in PL["pos"].items())
DRY = bool(getattr(g.count, "_dry", False))          # stage_prerun's stubbed gscript: skip what only a live run can do
RD =json.load(open(os.path.join(HERE, "diag_c99b_lvread.json"), encoding="utf-8"))
D1 = int(str(RD["consts"]["8984"]["text"]).strip())
ELEM = {0: "EXT", 1: "DBL", 2: "SGL", 3: "I32"}.get(int(RD["consts"]["8972"]["repr"]), "DBL")   # VI Server Representation enum (3 = I32, docs/toolkit-capabilities.md:70)
STAMP = time.strftime("%Y%m%d_%H%M%S")
F4P = os.path.join(K.CLAUDEDEV, "scratch_c99b_f4_%s.vi" % STAMP)
# F3's base is HARNESS_copyloop.vi (md5 eb8dad78, terminal-list graph tools/bench/graph_harness_copyloop_c95.json - the
# launch gate's dry run needs one; EMPTY_v0 has none), STRIPPED of every node and panel object first (as diag_c90 did).
BASE3 = os.path.join(K.CLAUDEDEV, "HARNESS_copyloop.vi")
s = K.Stage(BASE3, "eb8dad78209440fbbb9d87afad3d8ad6", "diag_c99b_bench", work_name="scratch_c99b_f3_%s.vi" % STAMP, preload=False, deadline_min=55,
            reserve_s=240.0, out_json=os.path.join(HERE, "diag_c99b_bench.json"), task="card 99-2 F3/F4")


def rec(name, kind, num, passing, dims, const=0):
    r = cp.record(name, kind, num, passing, dims); return r[:-5] + bytes([const]) + r[-4:]


def flat(*recs):
    return (struct.pack(">i", len(recs)) + b"".join(recs)).hex()


RET = rec("return value", "num", "I32", "value", 0)
F_STAMP_C = flat(RET, rec("site", "num", "I32", "value", 0), rec("any", "any", None, "value", 0, const=1))
F_STAMP_NC = flat(RET, rec("site", "num", "I32", "value", 0), rec("any", "any", None, "value", 0, const=0))
F_T3 = flat(RET, rec("ring", "arr", ELEM, "handle", 3))
F_T4 = flat(RET, rec("rowZ", "arr", "DBL", "handle", 2), rec("rowF", "arr", "DBL", "handle", 2), rec("hw", "num", "I32", "value", 0))


def purge(W, inv0):
    for o in g.new_since(W, "Invoke", inv0):
        ids = [x["uid"] for x in g.report(W, "Invoke")]
        if o["uid"] in ids:
            g.delete_object(W, "Invoke", ids.index(o["uid"]))


def cl_i(W, uid):
    if DRY:
        return 0
    return [o["uid"] for o in g.report(W, "CallLibrary")].index(uid)


def node_index(W, didx, uid, nmax=40):
    if DRY:
        return 0
    for k in range(nmax):
        u, _rows = g.node_terms_uid(W, didx, k)
        if u == uid:
            return k
        if not u:
            break
    raise RuntimeError("uid %d not in Diagram[%d].Nodes[]" % (uid, didx))


def diag_of(W, owner_cls):
    if DRY:
        return [1]
    return [d["i"] for d in g.report(W, "Diagram") if d["owner"] == owner_cls]


def panel_index(W, label):
    if DRY:
        return 0
    return [i for i, l, _ind in g.fp_labels(W) if l == label][0]


def new_uid(before, after):
    if DRY:
        return 0
    return [u for u in after if u not in before][0]


def ring_value():
    row = tuple(float((k * 7919) % 1000) / 7.0 for k in range(NPT))
    return tuple(tuple(row for _ in range(D1)) for _ in range(NB))


def rows_value(off):
    return tuple(tuple(float(((k + b * 31 + off) * 7919) % 1000) / 7.0 for k in range(NPT)) for b in range(NB))


def strip(W):
    s.head("[F3] strip the HARNESS_copyloop copy (every node, then every panel object)")
    for cls in ("Node", "ControlTerminal"):
        for _k in range(int(g.count(W, cls) or 0) + 2):
            if not g.count(W, cls):
                break
            try:
                g.delete_object(W, cls, 0)
            except RuntimeError as e:
                if "expected 1 object gone" not in str(e):
                    raise
        g.remove_bad_wires_scripted(W)
    c = {k: g.count(W, k) for k in ("Node", "ControlTerminal", "Wire", "ForLoop")}
    s.gate("T0 stripped: no node, no panel object, no wire", not any(c.values()), repr(c), fatal=True)


def build_f3(W):
    strip(W)
    s.head("[F3] build: ring ctl + indicator, For(N) + SR, NON-const stamp in the body")
    inv0 = g.uids(W, "Invoke")
    uT, nt, e = g.build_clfn(W, POS["temp3"], DLL, "stamp", F_T3); purge(W, inv0)
    kT = node_index(W, 0, uT)
    _n, lab = g.create_control(W, kT, 6); purge(W, inv0)
    fp0 = {l for _, l, _ in g.fp_labels(W)}
    g.create_indicator(W, node_index(W, 0, uT), 7); purge(W, inv0)
    ind = [l for _, l, _ in g.fp_labels(W) if l not in fp0] if not DRY else ["dry"]
    s.gate("T1 typed ring control + indicator from the temp CLFN (%s [%d][%d][%d])" % (ELEM, NB, D1, NPT), lab == "ring" and len(ind) == 1, "ctl %r ind %r" % (lab, ind))
    g.delete_object(W, "CallLibrary", cl_i(W, uT)); g.remove_bad_wires_scripted(W); purge(W, inv0)
    ctl_uids_before_for = {o["uid"] for o in g.report(W, "ControlTerminal")}
    f0 = g.uids(W, "ForLoop"); g.for_loop(W, POS["for3"]); uF = new_uid(f0, g.uids(W, "ForLoop"))
    r = g.create_const_loop_term(W, "for_n", node_index(W, 0, uF), value=NITER)
    s.fact("For #%s N const %r" % (uF, r))
    g.add_shift_reg(W, 0, POS["sr_y"][1], "ForLoop")
    g.wire_sr("LeftOutCtl", W, 0, 0, ctl_index=panel_index(W, "ring"), class_name="ForLoop")
    body = diag_of(W, "ForLoop")[0]
    uS, nt, e = g.build_clfn(W, POS["stamp3"], DLL, "stamp", F_STAMP_NC); purge(W, inv0)
    s.move_in(uS, body, POS["stamp3_in"]); purge(W, inv0)
    kS = node_index(W, body, uS)
    # CLFN terminal layout (diag_c90_t0stamp_scratch.py:4): t2/t3 error, param k in 4+2k / out 5+2k; params are
    # (0 return value, 1 site, 2 any) -> `any` in = t8, out = t9. Run 1 (diag_c99b_bench.log:32) wired t6/t7 = `site`.
    g.wire_sr("LeftIn", W, 0, 0, node_index=kS, term_index=8, class_name="ForLoop")
    g.wire_sr("RightIn", W, 0, 0, node_index=kS, term_index=9, class_name="ForLoop")
    es = s.es("F3 variant A built")
    if not DRY:        # review archive/peer/2026-09-26-c99b-bench-t2.md s4: print the table whatever ExecState says
        _u, rows = g.node_terms_uid(W, body, kS)
        s.fact("stamp terminals in the body: %r" % [(r["i"], r["name"], r["is_source"], r["wire"]) for r in rows])
    s.gate("T2 F3-A ExecState 1 (For N, SR init from ring, stamp in body)", es == 1, "body D[%s] stamp node %s" % (body, kS), fatal=True)
    return body, [u for u in (o["uid"] for o in g.report(W, "ControlTerminal")) if u in ctl_uids_before_for], ind[0]


def run_block(W, tag, n_runs, closed):
    vi = g.op(W)
    if closed:
        g.close_panel(W); vi = g.op(W)
    t0 = time.time()
    for _k in range(n_runs):
        g._run(vi, poll_s=30.0, hard_timeout_s=120.0)
    s.fact("BLOCK %s: %d run(s) x %d iterations in %.1f s (panel %s)" % (tag, n_runs, NITER, time.time() - t0, "closed" if closed else "open"))
    if closed:
        g.open_panel(W)
    return n_runs * NITER


def f3(W):
    body, ctl_uids, ind_label = build_f3(W)
    vi = g.op(W); vi.SetControlValue("ring", ring_value())
    order = []
    order.append(("A-open", run_block(W, "A-open", 1, False)))
    order.append(("A-closed", run_block(W, "A-closed", 1, True)))
    s.gate("T3 F3-A blocks ran", True, repr(order))
    s.head("[F3] variant B: move the indicator terminal into the body, wire it from the left SR (the L1 branch)")
    inv0 = g.uids(W, "Invoke")
    cts = g.report(W, "ControlTerminal")
    fpl = g.fp_labels(W)
    ind_uid = None
    for o in cts:          # the indicator = the ControlTerminal that is not the ring control's (2 ControlTerminals exist)
        if o["owner"] != "ForLoop":
            ind_uid = o["uid"] if ind_uid is None else ind_uid
    cand = [o["uid"] for o in cts]
    s.fact("ControlTerminals %r fp %r" % ([(o["uid"], o["pos"]) for o in cts], fpl))
    # identify by wire state: the ring control's terminal is wired (to the SR), the indicator's is bare
    bare = []
    for o in cts:
        k = node_index(W, 0, o["uid"])
        _u, rows = g.node_terms_uid(W, 0, k)
        if rows and not rows[0]["wire"]:
            bare.append(o["uid"])
    if DRY:
        bare = [0]
    s.fact("bare ControlTerminals (the indicator) %r of %r" % (bare, cand))
    if len(bare) != 1:
        raise K.Stop("T4 indicator terminal not unique: %r" % bare)
    s.move_in(bare[0], body, POS["ind3_in"]); purge(W, inv0)
    kI = node_index(W, body, bare[0])
    g.wire_sr("LeftIn", W, 0, 0, node_index=kI, term_index=0, class_name="ForLoop")
    es = s.es("F3 variant B built")
    s.gate("T4 F3-B indicator in the body, wired from the left SR, ExecState 1", es == 1, "ind node %s" % kI, fatal=True)
    order.append(("B-open", run_block(W, "B-open", 1, False)))
    order.append(("B-closed", run_block(W, "B-closed", 1, True)))
    s.gate("T5 F3-B blocks ran", True, repr(order))
    s.R["f3_order"] = order
    return order


def f4():
    s.head("[F4] build the moved-set bench on %s" % os.path.basename(F4P))
    shutil.copyfile(EMPTY, F4P); time.sleep(0.4); g.ensure_loaded(F4P); W = F4P
    inv0 = g.uids(W, "Invoke")
    uT, nt, e = g.build_clfn(W, POS["temp4"], DLL, "stamp", F_T4); purge(W, inv0)
    labs = []
    for t in (6, 8, 10):
        _n, lab = g.create_control(W, node_index(W, 0, uT), t); labs.append(lab); purge(W, inv0)
    s.gate("T6a rowZ/rowF/hw controls created", labs == ["rowZ", "rowF", "hw"], repr(labs))
    g.delete_object(W, "CallLibrary", cl_i(W, uT)); g.remove_bad_wires_scripted(W); purge(W, inv0)
    uA = g.build_clfn(W, POS["stampA"], DLL, "stamp", F_STAMP_C)[0]; purge(W, inv0)
    uB = g.build_clfn(W, POS["stampB"], DLL, "stamp", F_STAMP_C)[0]; purge(W, inv0)
    sites = []
    for u in (uA, uB):
        _n, lab = g.create_control(W, node_index(W, 0, u), 6); sites.append(lab); purge(W, inv0)
    g.wire_control(W, ["hw"], "CallLibrary", cl_i(W, uA), ["any"])
    g.for_loop(W, POS["for4"]); body = diag_of(W, "ForLoop")[0]
    for p, key in ((MEDIAN, "median"), (COEF, "coef"), (FIR, "fir")):
        g.drop_subvi(W, p, body, POS[key])
    idx = {"med": 0, "coef": 1, "fir": 2}
    if not DRY:
        sv = g.subvis(W, body)
        order = [o["uid"] for o in g.report(W, "SubVI")]
        idx = {}
        for x in sv:
            nm = str(x.get("name", ""))
            key = "med" if "Median" in nm else "fir" if "FIR Filter" in nm else "coef" if "Coefficients" in nm else nm
            idx[key] = order.index(int(x["uid"]))
        s.fact("SubVI Traverse indices %r (subvis %r)" % (idx, [(x.get("uid"), x.get("name")) for x in sv]))
    g.wire_control(W, ["rowZ"], "SubVI", idx["med"], ["X"])
    g.wire_control(W, ["rowF"], "SubVI", idx["fir"], ["X"])
    iA = cl_i(W, uA)
    g.wire(W, "CallLibrary", iA, "any", "SubVI", idx["med"], "left rank")
    for dst, term in ((idx["med"], "right rank"), (idx["coef"], "half-width")):
        g.wire(W, "CallLibrary", iA, "any", "SubVI", dst, term, branch=True)
    g.wire(W, "SubVI", idx["coef"], "forward coefficients", "SubVI", idx["fir"], "FIR Coefficients")
    g.wire(W, "SubVI", idx["med"], "Filtered X", "CallLibrary", cl_i(W, uB), "any")
    nt_ = g.count(W, "LoopTunnel"); s.fact("LoopTunnels %d; ExecState before index modes %r" % (nt_, g.exec_state(W)))
    for ti in (0, 1):
        g.set_index_mode(W, ti, 1)
    es = s.es("F4 built", target=W)
    if es != 1:      # the tunnel order was not rowZ,rowF: try every pair of tunnels once, report which one ran
        for ti in (0, 1):
            g.set_index_mode(W, ti, 0)
        for a in range(nt_):
            for b in range(a + 1, nt_):
                g.set_index_mode(W, a, 1); g.set_index_mode(W, b, 1)
                if g.exec_state(W) == 1:
                    s.fact("index modes set on tunnels %d,%d" % (a, b)); es = 1; break
                g.set_index_mode(W, a, 0); g.set_index_mode(W, b, 0)
            if es == 1:
                break
    s.gate("T6 F4 ExecState 1 (indexing rowZ/rowF, hw regular, Median out indexing)", es == 1, "", fatal=True)
    vi = g.op(W)
    vi.SetControlValue("rowZ", rows_value(0)); vi.SetControlValue("rowF", rows_value(500)); vi.SetControlValue("hw", 1)
    vi.SetControlValue(sites[0], 1); vi.SetControlValue(sites[1], 2)
    bp = K.mod("bench_prep"); hs, t0 = [], time.time()
    for k in range(NCALL):
        g._run(vi, poll_s=30.0, hard_timeout_s=120.0)
        if k in (0, NCALL // 2, NCALL - 1):
            hs.append(bp.labview_handles())
    s.fact("F4 %d runs in %.1f s; handles %r" % (NCALL, time.time() - t0, hs))
    s.gate("T7 F4 ran %d calls" % NCALL, True)
    if not DRY:
        s.gate("T9 handles flat +-100 over the F4 runs", max(hs) - min(hs) <= 100, repr(hs))
    s.R["f4_handles"] = hs


def q(v, p):
    return v[min(len(v) - 1, int(len(v) * p))]


def read_stamps(order):
    s.head("[Q] graceful COM Quit (flushes the DLL), verify gone, read the stamps")
    if DRY:
        return
    r = subprocess.run([sys.executable, "-c", "import win32com.client as w\nw.Dispatch('LabVIEW.Application').Quit()\n"], capture_output=True, text=True, timeout=90)
    t0 = time.time()
    while "labview" in subprocess.run("tasklist", capture_output=True, text=True).stdout.lower() and time.time() - t0 < 60:
        time.sleep(2)
    gone = "labview" not in subprocess.run("tasklist", capture_output=True, text=True).stdout.lower()
    s.gate("Q1 LabVIEW quit gracefully (rc %d)" % r.returncode, gone)
    g.reset()
    files = sorted(glob.glob(os.path.join(OUTDIR, "t0_site*_pid*.bin")), key=os.path.getmtime)
    newest = {}
    for p in files:
        if os.path.getmtime(p) >= s.t0:
            newest[os.path.basename(p)[3:9]] = p
    data = {}
    for site, p in newest.items():
        b = open(p, "rb").read(); n = len(b) // 8; v = struct.unpack("<%dq" % n, b[:n * 8]); data[site] = (float(v[0]), v[1:])
    s.fact("stamp files this run: %r" % {k: (os.path.basename(p), len(data[k][1])) for k, p in newest.items()})
    res = {}
    if "site00" in data:
        f, st = data["site00"]; pos = 0
        for tag, n in order:
            seg = st[pos:pos + n]; pos += n
            d = sorted((seg[i + 1] - seg[i]) / f * 1e6 for i in range(len(seg) - 1))
            if d:
                res[tag] = {"n": len(d), "median_us": round(q(d, .5), 3), "p99_us": round(q(d, .99), 3), "max_us": round(d[-1], 1)}
            s.fact("F3 %s per-iteration us: %r" % (tag, res.get(tag)))
        s.gate("T8a site00 holds %d stamps" % pos, len(st) == pos, "have %d" % len(st))
    if "site01" in data and "site02" in data:
        f = data["site01"][0]; a, b = data["site01"][1], data["site02"][1]; n = min(len(a), len(b))
        d = sorted((b[i] - a[i]) / f * 1e3 for i in range(n))
        res["F4"] = {"n": n, "median_ms": round(q(d, .5), 3), "p99_ms": round(q(d, .99), 3), "min_ms": round(d[0], 3), "max_ms": round(d[-1], 3)}
        s.fact("F4 per call (15 beads, Median+Coef+FIR) ms: %r" % res["F4"])
        s.gate("T8b site01/site02 hold %d stamps each" % NCALL, len(a) == NCALL and len(b) == NCALL, "%d/%d" % (len(a), len(b)))
    s.R["results"] = res
    for p in (s.work, F4P):
        for _k in range(4):
            try:
                if os.path.exists(p):
                    os.remove(p)
                break
            except Exception as e:                                                  # noqa: BLE001
                s.fact("delete %s: %s" % (os.path.basename(p), str(e)[:80])); time.sleep(3)
        s.gate("H4 scratch deleted: %s" % os.path.basename(p), not os.path.exists(p))


def body(_st):
    for p in glob.glob(os.path.join(K.CLAUDEDEV, "scratch_c99b_f[34]_*.vi")):   # run 1 left its F3 scratch (H6, log:47)
        if p not in (s.work, F4P):
            os.remove(p); s.fact("removed a previous run's scratch %s" % os.path.basename(p))
    W = s.start()
    bp = K.mod("bench_prep"); s.R["handles_start"] = bp.labview_handles()
    s.fact("ring %s [%d][%d][%d] = %.1f MB; D1 from #8984 %r, elem repr %r" % (ELEM, NB, D1, NPT, NB * D1 * NPT * 8 / 1e6, RD["consts"]["8984"].get("text"), RD["consts"]["8972"].get("repr")))
    try:
        order = f3(W)
        s.R["no_vi_was_run"] = False; s.R["verification_level"] = "FUNCTIONAL on scratch benches only"
        f4()
    except BaseException:
        s.scratches.extend([s.work, F4P])      # a stopped run: close() restarts LabVIEW and deletes both (no stamp flush)
        raise
    s.R["handles_end"] = bp.labview_handles()
    s.fact("handles start %r end %r" % (s.R["handles_start"], s.R["handles_end"]))
    read_stamps(order)


if __name__ == "__main__":
    rc = K.run(body, s)
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"], capture_output=True)
        time.sleep(4)
        s.gate("Z LabVIEW gone at exit", "LabVIEW.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True).stdout)
    except RuntimeError as e:          # the dry run blocks subprocess (stage_prerun fences); a live run never raises here
        print("  (exit kill skipped: %s)" % e)
    s.dump(); sys.exit(s.summary())
