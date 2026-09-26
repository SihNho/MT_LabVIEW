r"""diag_c99c_bench - card 99-3 (escalation rung 1 of 99-2 F3/F4; PD212(e)/(h)5). MEASURE ONLY, two scratch benches, RUN
(card flag run_vi, scratch_c99c_* only), then deleted. D1_s1_copy.vi is never opened (stagekit pins its md5).
FOUND FIRST (reused, nothing new built): diag_c99b_bench.py - strip of HARNESS_copyloop (T0 PASS diag_c99b_bench2.log:26)
and temp-CLFN typed controls (T1 PASS :29); the copyloop timing method (build_harness_copyloop.py: Python-side time of ONE
COM Run, ~2 ms fixed per run in copyloop_bench.json); gscript connect_ctl_ind / tunnels / set_index_mode / drop_subvi into a
For body / wire_control / panel_wiring; stagekit.move_in. Terminal names from S1's graph (par1359_95_graph.json 29009,
28233, 28180). NO t0stamp CLFN in any timed path: 99-2's F3 read ExecState 0 twice with a non-const Adapt-to-Type CLFN
on a 3-D DBL shift register, and connect into an Adapt-to-Type CLFN is a known stall (gscript.connect_terminals doc).
F3 (scratch_c99c_f3_*): For(N=NITER const). A = empty body. RUN 2 (review archive/peer/2026-09-26-c99c-bench-t4.md):
    B1 = run 1's route RE-READ - indicator into the body, outside 'ring' control -> it, tunnel IndexMode read before AND
    after set_index_mode(0), ExecState twice 0.5 s apart (claim-1 test; not a gate). If B1 reads 1, B runs there (one
    indicator write of the whole [NB][2][NPT] DBL ring per iteration from a loop-invariant tunnel). Else B2 on a fresh
    scratch_c99c_f3b_*: BOTH terminals in the body, wired there (one control read + one indicator write = UPPER bound).
    DEVIATION from the card: NO shift register (an SR needs a pass-through node in its path; the only one our verbs create
    is 99-2's CLFN). Discriminator: B with a 1-bead ring (a real per-iteration copy scales with size).
F4 (scratch_c99c_f4_*): For over bead rows (auto-indexed rowZ/rowF [n][NPT]) with S1's own vi.lib subVIs: Median Filter.vi
    (X<-rowZ[i], left/right rank<-hw), Smoothing Filter Coefficients.vi (half-width<-hw) -> FIR Filter (DBL).vi
    (X<-rowF[i]); hw = 1 = both S1 half-width defaults; rowZ carries S1's Subtract (raw - Exp Baseline) in the data. One COM
    Run = one frame's set; per call(15) = (mean T15 - mean T1) * 15/14 (the fixed COM cost cancels); raw T15 also reported.
PREDICTION CONTRACT: T0 strip 0/0/0/0; T1 'ring' + one indicator; T2 F3-A ES 1; T3 ring read back [NB][2][NPT]; T4 F3-B
 indicator wired inside the body, ES 1; T6 rowZ/rowF/hw; T7 body terminals wired + ES 1; T8 rows/hw read back; K/H pins
 (S1 3e3d23ce), nothing saved, both scratches deleted, LabVIEW gone (Z). RESULT line last (C6).
"""
import json, math, os, random, shutil, struct, subprocess, sys, time                    # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE)
for p in (TOOLS, os.path.join(TOOLS, "gpu"), os.path.join(TOOLS, "recipes")):
    sys.path.insert(0, p)
import stagekit as K                                                             # noqa: E402
import gscript as g                                                              # noqa: E402
import clfn_params as cp                                                         # noqa: E402

PL = json.load(open(os.path.join(HERE, "diag_c99c_benchplan.json"), encoding="utf-8"))
Z = PL["sizes"]; NB, D1, NPT, NITER, NCALL, REP = (int(Z[k]) for k in ("NB", "D1", "NPT", "NITER", "NCALL", "REP"))
FILL, HW, EXPB, HWD, NCD = float(Z["FILL"]), int(Z["HW"]), float(Z["EXP_BASELINE"]), int(Z["HW_DISC"]), int(Z["NCALL_DISC"])
POS = dict((k, tuple(v)) for k, v in PL["pos"].items())
DRY = bool(getattr(g.count, "_dry", False))          # stage_prerun's stubbed gscript: skip what only a live run can do
DLL = os.path.join(K.CLAUDEDEV, "t0stamp.dll"); EMPTY = os.path.join(K.CLAUDEDEV, "EMPTY_v0.vi")
LIB = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Analysis\3filter.llb"
MEDIAN, FIR, COEF = (os.path.join(LIB, n) for n in ("Median Filter.vi", "FIR Filter (DBL).vi", "Smoothing Filter Coefficients.vi"))
STAMP = time.strftime("%Y%m%d_%H%M%S")
F4P = os.path.join(K.CLAUDEDEV, "scratch_c99c_f4_%s.vi" % STAMP)
F3BP = os.path.join(K.CLAUDEDEV, "scratch_c99c_f3b_%s.vi" % STAMP)
s = K.Stage(os.path.join(K.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"], "diag_c99c_bench", work_name="scratch_c99c_f3_%s.vi" % STAMP,
            preload=False, deadline_min=47, reserve_s=240.0, out_json=os.path.join(HERE, "diag_c99c_bench.json"), task="card 99-3 F3/F4")
bp = K.mod("bench_prep")


def rec(name, kind, num, passing, dims):
    r = cp.record(name, kind, num, passing, dims); return r[:-5] + bytes([0]) + r[-4:]


RET = rec("return value", "num", "I32", "value", 0)
F_T3 = (struct.pack(">i", 2) + RET + rec("ring", "arr", "DBL", "handle", 3)).hex()
F_T4 = (struct.pack(">i", 4) + RET + rec("rowZ", "arr", "DBL", "handle", 2) + rec("rowF", "arr", "DBL", "handle", 2)
        + rec("hw", "num", "I32", "value", 0)).hex()


def purge(W, inv0):
    for o in g.new_since(W, "Invoke", inv0):
        ids = [x["uid"] for x in g.report(W, "Invoke")]
        if o["uid"] in ids:
            g.delete_object(W, "Invoke", ids.index(o["uid"]))


def node_index(W, didx, uid, nmax=40):
    if DRY:
        return 0
    for k in range(nmax):
        u, _rows = g.node_terms_uid(W, didx, k)
        if u == uid:
            return k
        if not u:
            break
    raise RuntimeError("uid %r not in Diagram[%d].Nodes[]" % (uid, didx))


def trows(W, didx, uid):
    return {} if DRY else dict((r["name"], r["wire"]) for r in g.node_terms_uid(W, didx, node_index(W, didx, uid))[1] if not r["is_source"])


def body_of(W):
    return 1 if DRY else [d["i"] for d in g.report(W, "Diagram") if d["owner"] == "ForLoop"][0]


def pidx(W, label):
    return 0 if DRY else [i for i, l, _ind in g.fp_labels(W) if l == label][0]


def temp_ctls(W, flat, pos, terms, indicator_term=None):
    """a typed temp CLFN -> create_control per terminal (+ one indicator) -> delete the CLFN (diag_c99b T1)."""
    inv0 = g.uids(W, "Invoke")
    uT, _nt, _e = g.build_clfn(W, pos, DLL, "stamp", flat); purge(W, inv0)
    labs = []
    for t in terms:
        _n, lab = g.create_control(W, node_index(W, 0, uT), t); labs.append(lab); purge(W, inv0)
    fp0 = {l for _, l, _ in g.fp_labels(W)}
    if indicator_term is not None:
        g.create_indicator(W, node_index(W, 0, uT), indicator_term); purge(W, inv0)
    ind = ["dry"] if DRY else [l for _, l, _ in g.fp_labels(W) if l not in fp0]
    g.delete_object(W, "CallLibrary", 0 if DRY else [o["uid"] for o in g.report(W, "CallLibrary")].index(uT))
    g.remove_bad_wires_scripted(W); purge(W, inv0)
    return labs, ind


def timed(W, tag, n, per, poll):
    vi = g.op(W); ts = []
    for _k in range(n):
        t0 = time.perf_counter(); g._run(vi, poll_s=poll, hard_timeout_s=300.0); ts.append(time.perf_counter() - t0)
    q = sorted(ts); m = sum(ts) / max(1, len(ts))
    r = {"runs": n, "per_run_units": per, "mean_ms": round(m * 1e3, 4), "median_ms": round(q[len(q) // 2] * 1e3, 4) if q else None,
         "min_ms": round(q[0] * 1e3, 4) if q else None, "max_ms": round(q[-1] * 1e3, 4) if q else None,
         "p10_ms": round(q[len(q) // 10] * 1e3, 4) if q else None, "p90_ms": round(q[(len(q) * 9) // 10] * 1e3, 4) if q else None,
         "mean_per_unit_us": round(m * 1e6 / per, 3)}
    s.fact("TIME %s: %r" % (tag, r)); s.R.setdefault("times", {})[tag] = r
    return m


def f3(W):
    s.head("[F3] strip the HARNESS_copyloop copy, ring control + indicator, empty For(N)")
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
    labs, ind = temp_ctls(W, F_T3, POS["temp3"], (6,), indicator_term=7)
    s.gate("T1 ring control + ONE indicator from the temp CLFN (DBL [%d][%d][%d])" % (NB, D1, NPT), labs == ["ring"] and len(ind) == 1, (labs, ind), fatal=True)
    f0 = g.uids(W, "ForLoop"); g.for_loop(W, POS["for3"])
    uF = 0 if DRY else [u for u in g.uids(W, "ForLoop") if u not in f0][0]
    s.fact("For #%s N const %r" % (uF, g.create_const_loop_term(W, "for_n", node_index(W, 0, uF), value=NITER)))
    s.gate("T2 F3-A (empty For, N const) ExecState 1", s.es("F3-A built") == 1, fatal=True)
    vi = g.op(W); big = tuple(0.5 * (k % 7) for k in range(NPT))
    ring = lambda nb: tuple(tuple(big for _ in range(D1)) for _ in range(nb))     # noqa: E731
    vi.SetControlValue("ring", ring(NB)); v = () if DRY else vi.GetControlValue("ring")
    dims = (len(v), len(v[0]), len(v[0][0])) if v else ()
    s.gate("T3 'ring' read back [%d][%d][%d] = %.1f MB" % (NB, D1, NPT, NB * D1 * NPT * 8 / 1e6), DRY or dims == (NB, D1, NPT), repr(dims), fatal=True)
    h0 = bp.labview_handles()
    for tag, closed in (("A-open", False), ("A-closed", True)):
        if closed:
            g.close_panel(W)
        timed(W, "F3 " + tag, REP, NITER, 120.0)
        if closed:
            g.open_panel(W)
    s.head("[F3] B1 = run 1's route RE-READ (review c99c-bench-t4 s4): indicator into the body, outside control -> it")
    cts = [] if DRY else g.report(W, "ControlTerminal")          # create_indicator(t7) sits RIGHT of the CLFN, the control LEFT
    iu = 0 if DRY else max(cts, key=lambda o: o["pos"][0])["uid"]
    s.fact("ControlTerminals (uid, pos) %r -> indicator #%s" % ([(o["uid"], o["pos"]) for o in cts], iu))
    g.open_panel(W); s.move_in(iu, body_of(W), POS["ind3_in"])
    s.fact("connect_ctl_ind ring -> %s: err %r" % (ind[0], g.connect_ctl_ind(W, pidx(W, ind[0]), pidx(W, "ring"))))
    nt = 0 if DRY else int(g.count(W, "LoopTunnel") or 0)
    t0_ = g.tunnels(W, 0) if nt == 1 else {}
    if nt == 1:
        g.set_index_mode(W, 0, 0)
    t1_ = g.tunnels(W, 0) if nt == 1 else {}
    e1 = s.es("B1 after IndexMode 0"); time.sleep(0.5); e2 = s.es("B1 +0.5 s")
    s.R["b1"] = {"tunnels": nt, "mode_before": t0_.get("index_mode"), "mode_after": t1_.get("index_mode"), "es": [e1, e2]}
    s.fact("B1 (claim-1 test): %d tunnel(s), IndexMode before %r -> after %r, ExecState %r / %r" % (nt, t0_.get("index_mode"), t1_.get("index_mode"), e1, e2))
    WB, route = W, "tunnel"
    if DRY or e2 != 1:
        WB, route = f3_inside(), "inside"
    s.gate("T4 F3-B runnable (route %s): ExecState 1" % route, DRY or s.es("B ready", target=WB) == 1, fatal=True)
    s.R["f3_b_route"] = route
    for tag, nb, closed in (("B-open", NB, False), ("B-open-1bead", 1, False), ("B-closed", NB, True)):
        vi = g.op(WB); vi.SetControlValue("ring", ring(nb))
        if closed:
            g.close_panel(WB)
        timed(WB, "F3 %s (%s)" % (tag, route), REP, NITER, 120.0)
        if closed:
            g.open_panel(WB)
    s.R["f3_handles"] = [h0, bp.labview_handles()]; s.fact("F3 handles before/after the runs %r" % s.R["f3_handles"])


def f3_inside():
    """B2 on a FRESH scratch: both ring terminals in the For body, control -> indicator on that diagram (no tunnel)."""
    s.head("[F3] B2 = both ring terminals INTO a fresh For body, wired there (B1 did not read ExecState 1)")
    shutil.copyfile(EMPTY, F3BP); time.sleep(0.4); g.ensure_loaded(F3BP); W = F3BP
    labs, ind = temp_ctls(W, F_T3, POS["temp3"], (6,), indicator_term=7)
    s.gate("T1b ring control + ONE indicator on %s" % os.path.basename(W), labs == ["ring"] and len(ind) == 1, (labs, ind), fatal=True)
    f0 = g.uids(W, "ForLoop"); g.for_loop(W, POS["for3"])
    uF = 0 if DRY else [u for u in g.uids(W, "ForLoop") if u not in f0][0]
    s.fact("B2 For #%s N const %r" % (uF, g.create_const_loop_term(W, "for_n", node_index(W, 0, uF), value=NITER)))
    cts = [] if DRY else g.report(W, "ControlTerminal")
    iu = 0 if DRY else max(cts, key=lambda o: o["pos"][0])["uid"]
    cu = 0 if DRY else min(cts, key=lambda o: o["pos"][0])["uid"]
    s.fact("B2 ControlTerminals (uid, pos) %r -> control #%s, indicator #%s" % ([(o["uid"], o["pos"]) for o in cts], cu, iu))
    MV = K.mod("build_d1_v0")
    for u, p in ((cu, POS["ctl3_in"]), (iu, POS["ind3_in"])):
        s.fact("B2 move_in #%s: %r" % (u, MV.move_in(W, u, body_of(W), p)))
    s.fact("B2 connect_ctl_ind ring -> %s: err %r" % (ind[0], g.connect_ctl_ind(W, pidx(W, ind[0]), pidx(W, "ring"))))
    nt = 0 if DRY else int(g.count(W, "LoopTunnel") or 0)
    pw = {} if DRY else dict((r["label"], r["wire"]) for r in g.panel_wiring(W))
    s.fact("B2 wires %r, %d tunnel(s)" % (pw, nt))
    s.gate("T4b B2: 'ring' -> indicator on ONE wire, 0 tunnels", DRY or (pw.get("ring") and pw.get("ring") == pw.get(ind[0]) and nt == 0), repr(pw))
    return W


def rows(nb, fill):
    """ring rows 0/1 per bead: the first fill*NPT samples hold noisy data, the rest the Initialize Array element 0;
    row 0 carries S1's Subtract (raw - Exp Baseline), so its empty part is -EXPB, as in S1."""
    n, rng, Zr, Fr = int(NPT * fill), random.Random(7), [], []
    for b in range(nb):
        z, f = [], []
        for k in range(NPT):
            e = rng.random() - 0.5
            z.append((40.0 * e + 25.0 * math.sin(k / 300.0 + b) if k < n else 0.0) - EXPB)
            f.append(5.0 + 0.3 * e if k < n else 0.0)
        Zr.append(tuple(z)); Fr.append(tuple(f))
    return tuple(Zr), tuple(Fr)


def f4():
    s.head("[F4] the moved set on %s" % os.path.basename(F4P))
    shutil.copyfile(EMPTY, F4P); time.sleep(0.4); g.ensure_loaded(F4P); W = F4P
    labs, _i = temp_ctls(W, F_T4, POS["temp4"], (6, 8, 10))
    s.gate("T6 rowZ/rowF/hw controls created", labs == ["rowZ", "rowF", "hw"], repr(labs), fatal=True)
    g.for_loop(W, POS["for4"]); body = body_of(W)
    for p, key in ((MEDIAN, "median"), (COEF, "coef"), (FIR, "fir")):
        g.drop_subvi(W, p, body, POS[key])
    sv = [] if DRY else g.subvis(W, body); order = [] if DRY else [o["uid"] for o in g.report(W, "SubVI")]
    key = lambda nm: "med" if "Median" in nm else "fir" if "FIR Filter" in nm else "coef" if "Coefficients" in nm else nm   # noqa: E731
    U = dict((key(str(x.get("name", ""))), int(x["uid"])) for x in sv) if not DRY else {"med": 0, "coef": 0, "fir": 0}
    ix = dict((k, 0 if DRY else order.index(u)) for k, u in U.items()); s.fact("F4 subVIs %r Traverse idx %r" % (U, ix))
    g.wire_control(W, ["rowZ"], "SubVI", ix["med"], ["X"]); g.wire_control(W, ["rowF"], "SubVI", ix["fir"], ["X"])
    g.wire_control(W, ["hw"], "SubVI", ix["med"], ["left rank"])
    g.wire_control(W, ["hw"], "SubVI", ix["med"], ["right rank"], branch=True)
    g.wire_control(W, ["hw"], "SubVI", ix["coef"], ["half-width"], branch=True)
    g.wire(W, "SubVI", ix["coef"], "forward coefficients", "SubVI", ix["fir"], "FIR Coefficients")
    pw = {} if DRY else dict((r["label"], r["wire"]) for r in g.panel_wiring(W)); modes = {}
    for i in range(0 if DRY else int(g.count(W, "LoopTunnel") or 0)):
        t = g.tunnels(W, i); lab = next((l for l, w in pw.items() if w and w == t.get("out_wire")), None)
        want = None if lab is None else (1 if lab in ("rowZ", "rowF") else 0); modes[i] = (lab, t.get("index_mode"), want)
        if want is not None and t.get("index_mode") != want:
            g.set_index_mode(W, i, want)
    T = dict((k, trows(W, body, u)) for k, u in U.items())
    need = {"med": ("X", "left rank", "right rank"), "coef": ("half-width",), "fir": ("X", "FIR Coefficients")}
    bare = [(k, n) for k, ns in need.items() for n in ns if not (T.get(k) or {}).get(n)]
    s.gate("T7 F4 body terminals wired (bare %r; tunnels %r) and ExecState 1" % (bare, modes), DRY or (not bare and s.es("F4 built", target=W) == 1), "", fatal=True)
    vi = g.op(W); vi.SetControlValue("hw", HW); h0 = bp.labview_handles()
    data = dict(((nb, fl), rows(nb, fl)) for nb in (1, NB) for fl in (1.0, FILL))
    g.close_panel(W)          # run 1: an OPEN panel made every COM Run ~25 ms (UI-tick bound) and hid n15-n1; F3 A-closed ~1.5 ms
    vi = g.op(W)
    for rep in range(REP):
        for nb, fl in ((1, 1.0), (NB, 1.0), (1, FILL), (NB, FILL)):
            vi.SetControlValue("rowZ", data[(nb, fl)][0]); vi.SetControlValue("rowF", data[(nb, fl)][1])
            if rep == 0 and not DRY:
                a, b2, h = vi.GetControlValue("rowZ"), vi.GetControlValue("rowF"), vi.GetControlValue("hw")
                s.gate("T8 rows read back n=%d fill=%.2f: [%d][%d] x2, hw %d" % (nb, fl, nb, NPT, HW),
                       len(a) == nb and len(a[0]) == NPT and len(b2) == nb and int(h) == HW, (len(a), len(a[0]), int(h)), fatal=True)
            timed(W, "F4 n%d fill%.2f r%d" % (nb, fl, rep), NCALL, 1, 6.0)
    # DEAD-CODE discriminator (both 'Filtered X' outputs are unwired): a wider window must cost more IF the filters run
    vi.SetControlValue("hw", HWD)
    for nb in (1, NB):
        vi.SetControlValue("rowZ", data[(nb, 1.0)][0]); vi.SetControlValue("rowF", data[(nb, 1.0)][1])
        timed(W, "F4DISC hw%d n%d fill1.00" % (HWD, nb), NCD, 1, 6.0)
    vi.SetControlValue("hw", HW)
    s.R["f4_handles"] = [h0, bp.labview_handles()]; s.fact("F4 handles before/after the runs %r" % s.R["f4_handles"])


def body(_st):
    W = s.start(); s.scratches.extend([s.work, F4P, F3BP])   # close() restarts LabVIEW (no save) and deletes them
    s.R["no_vi_was_run"] = False; s.R["verification_level"] = "FUNCTIONAL timing on scratch benches only"
    try:
        f3(W)
    except Exception as e:                               # noqa: BLE001 - F4 is independent of F3: record, keep measuring
        s.gate("F3 completed (%s)" % type(e).__name__, False, str(e)[:90])
    f4()


if __name__ == "__main__":
    rc = K.run(body, s)
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"], capture_output=True)
        time.sleep(4)
        s.gate("Z LabVIEW gone at exit", "LabVIEW.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True).stdout)
    except RuntimeError as e:          # the dry run blocks subprocess (stage_prerun fences); a live run never raises here
        print("  (exit kill skipped: %s)" % e)
    s.dump(); sys.exit(s.summary())
