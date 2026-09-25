r"""diag_c90_t0stamp_scratch - card 90-1 step 2: ONE t0stamp CLFN fed a BRANCH of a 2-D U16 wire, on a NEW scratch VI, by script.

FOUND FIRST: gscript.build_clfn (OpCLFNParams/Pre/Build, tools/gpu/clfn_params.record: kind "any" = Adapt to Type, Adapt Format
By Value = Handles by Value), create_control/create_indicator (CLFN terminal layout from build_harness_gpu2.log:92-105: t2 error
in, t3 error out, param k in at 4+2k / out at 5+2k), wire() by terminal name (the route that never stalls on Adapt-to-Type CLFNs,
gscript.py:2686-2689), wire_control(branch=True), build_index_array + NAMES.md:229 (`array`), stagekit.Stage (pins, restart,
save, hygiene), bench_prep.labview_handles, cycle_runner LV_QUIT_SRC (graceful quit -> DLL_PROCESS_DETACH flush).
DIAGRAM (all top level):  ctl `img` (2-D U16, made by create_control on a TEMPORARY typed CLFN, then that node is deleted)
   img -> IndexArray.array -> indicator (the consumer);  img BRANCH -> A.any
   X = stamp(site ctl, any <- branch of that ctl)  --error-->  A = stamp(site ctl 2, any <- img)  --error-->  B = stamp(site ctl 3, any <- ctl 3)
   Per run k: A_k - X_k = LabVIEW's array handling in front of A + one call; B_k - A_k = one call with a scalar. Their difference is
   the 2-D array cost (a 2.6 MB copy would be >= 100 us; a handle pass is ~0).
PREDICTION CONTRACT (gates): T1 `img` control exists (label) T2 temp CLFN deleted T3 3 CallLibrary nodes  T4 all required inputs wired,
   ExecState 1  T5 1100 runs, stamp files for sites 5/7/9 exist with >= 1024 records each before quit  T6 handles flat +-100 over runs
   1..21  T7 negative: site 64 -> X returns 1, no t0_site64 file  T8 saved by SaveInstrument, ExecState 1 re-read  T9 quit graceful,
   LabVIEW gone, tails flushed (counts == 1101 / 1101 / 1101)  + stagekit K/S/H gates.  RESULT line last (C6).
"""
import glob, os, struct, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gpu"))
import stagekit as K                                                             # noqa: E402
import gscript as g                                                              # noqa: E402
import clfn_params as cp                                                         # noqa: E402
DLL = os.path.join(K.CLAUDEDEV, "t0stamp.dll"); OUT = os.path.join(K.CLAUDEDEV, "t0stamp_out"); NRUN = 1100
SRC = os.path.join(K.CLAUDEDEV, "FPTARGET_v0.vi")
EXTRA = [("kswap", os.path.join(K.CLAUDEDEV, "D1_s1_kswap_20260926_004935.vi")), ("L2-A1 bed", os.path.join(K.CLAUDEDEV, "D1_l2_a1_20260925_235224.vi"))]
PINS = tuple(K.DEFAULT_PINS) + tuple((n, p, K.md5(p)) for n, p in EXTRA)
STAMP = time.strftime("%Y%m%d_%H%M%S")
s = K.Stage(SRC, K.md5(SRC), "diag_c90_t0stamp", work_name="t0stamp_scratch_%s.vi" % STAMP, pins=PINS, preload=False, deadline_min=40,
            out_json=os.path.join(HERE, "diag_c90_t0stamp_scratch.json"), task="card 90-1 step 2")


def _ts(msg):
    print("  STAMP %s %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


def _restart_stamped():
    """Run 2 instrumentation (card 90-3): the SAME three steps as bench_prep.restart_labview, each stamped, so a
    second silence in the RESTART section names the blocked step. Run 1 printed nothing after 'BEFORE the restart: 0'."""
    bp = K.mod("bench_prep")
    _ts("restart: Stop-Process LabVIEW")
    subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"], capture_output=True, timeout=60)
    _ts("restart: sleep 5"); time.sleep(5)
    _ts("restart: Start-Process LabVIEW")
    subprocess.run(["powershell", "-NoProfile", "-Command", "Start-Process '%s'" % bp.LV_EXE], capture_output=True, timeout=60)
    _ts("restart: sleep 45"); time.sleep(45)
    _ts("restart: done; next = labview_handles")


def _handles_stamped():
    _ts("labview_handles: enter"); n = _ORIG_HANDLES(); _ts("labview_handles: %r" % n); return n


_ORIG_HANDLES = K.mod("bench_prep").labview_handles
K.mod("bench_prep").restart_labview = _restart_stamped
K.mod("bench_prep").labview_handles = _handles_stamped


def rec(name, kind, num, passing, dims, const=0):
    r = cp.record(name, kind, num, passing, dims); return r[:-5] + bytes([const]) + r[-4:]     # field 10 `Const` sits before Minimum Size


FLAT_STAMP = (struct.pack(">i", 3) + rec("return value", "num", "I32", "value", 0) + rec("site", "num", "I32", "value", 0)
              + rec("any", "any", None, "value", 0, const=1)).hex()
FLAT_TEMP = (struct.pack(">i", 2) + rec("return value", "num", "I32", "value", 0) + rec("img", "arr", "U16", "handle", 2)).hex()


def cl_i(uid):
    return [o["uid"] for o in g.report(W, "CallLibrary")].index(uid)


def purge(inv0):
    for o in g.new_since(W, "Invoke", inv0):
        ids = [x["uid"] for x in g.report(W, "Invoke")]
        if o["uid"] in ids:
            g.delete_object(W, "Invoke", ids.index(o["uid"]))


def body(_stage):
    global W
    W = s.start(); s.head("[3] strip the FPTARGET copy, then build")
    while g.count(W, "Node"):
        try:
            g.delete_object(W, "Node", 0)
        except RuntimeError as e:
            if "expected 1 object gone" not in str(e):
                raise
            break
    g.remove_bad_wires_scripted(W)
    while g.count(W, "ControlTerminal"):
        g.delete_object(W, "ControlTerminal", 0)
    g.remove_bad_wires_scripted(W); inv0 = g.uids(W, "Invoke")
    s.fact("stripped: nodes %d wires %d fp %d" % (g.count(W, "Node"), g.count(W, "Wire"), len(g.fp_labels(W))))
    uT, nt, e = g.build_clfn(W, (300, 500), DLL, "stamp", FLAT_TEMP); purge(inv0)
    new, lab = g.create_control(W, g.count(W, "Node") - 1, 6)                          # param 1 in = t6
    s.gate("T1 2-D U16 control created on the temp CLFN's `img` terminal", bool(new) and lab == "img", "label %r terms %d errs %r" % (lab, nt, e))
    g.delete_object(W, "CallLibrary", cl_i(uT)); g.remove_bad_wires_scripted(W); purge(inv0)
    s.gate("T2 temp CLFN deleted, `img` control kept", g.count(W, "CallLibrary") == 0 and any(l == "img" for _, l, _ in g.fp_labels(W)))
    ia = g.build_index_array(W, (600, 500))[0]; purge(inv0)
    g.wire_control(W, ["img"], "IndexArray", 0, ["array"]); g.create_indicator(W, g.count(W, "Node") - 1, 1); purge(inv0)
    us = []
    for y in (150, 300, 450):
        us.append(g.build_clfn(W, (900, y), DLL, "stamp", FLAT_STAMP)[0]); purge(inv0)
    s.gate("T3 three stamp CLFN nodes", g.count(W, "CallLibrary") == 3, str(us))
    labs = []
    for k, u in enumerate(us):
        _new, lab = g.create_control(W, g.count(W, "Node") - 3 + k, 6); labs.append(lab); purge(inv0)
    s.fact("site controls %r" % labs)
    g.wire_control(W, [labs[0]], "CallLibrary", cl_i(us[0]), ["any"], branch=True)
    g.wire_control(W, ["img"], "CallLibrary", cl_i(us[1]), ["any"], branch=True)
    g.wire_control(W, [labs[2]], "CallLibrary", cl_i(us[2]), ["any"], branch=True)
    g.wire(W, "CallLibrary", cl_i(us[0]), "error out", "CallLibrary", cl_i(us[1]), "error in (no error)")
    g.wire(W, "CallLibrary", cl_i(us[1]), "error out", "CallLibrary", cl_i(us[2]), "error in (no error)")
    fp0 = {l for _, l, _ in g.fp_labels(W)}; g.create_indicator(W, g.count(W, "Node") - 3, 5); purge(inv0)   # X return value out = t5
    ret_lab = [l for _, l, _ in g.fp_labels(W) if l not in fp0][0]
    g.remove_bad_wires_scripted(W); es = s.es("after wiring")
    s.gate("T4 ExecState 1 with every required input wired", es == 1, "wires %d nodes %d ret indicator %r" % (g.count(W, "Wire"), g.count(W, "Node"), ret_lab))
    if es != 1:
        raise K.Stop("T4")
    s.head("[4] RUN %d times" % NRUN); vi = g.op(W); bp = K.mod("bench_prep")
    vi.SetControlValue("img", [[(r * 1280 + c) & 0xFFFF for c in range(1280)] for r in range(1024)])
    for lab, site in zip(labs, (5, 7, 9)):
        vi.SetControlValue(lab, site)
    hs, t0 = [], time.time()
    for k in range(NRUN):
        g._run(vi, poll_s=30.0, hard_timeout_s=60.0)
        if k in (0, 10, 20):
            hs.append(bp.labview_handles())
    s.fact("%d runs in %.1f s (%.1f ms/run incl. COM)" % (NRUN, time.time() - t0, (time.time() - t0) / NRUN * 1e3))
    files = {p: os.path.getsize(p) for p in glob.glob(os.path.join(OUT, "t0_site*.bin"))}
    s.gate("T5 stamp files for sites 05/07/09 exist with >= 1024 records before quit",
           all(any("site%02d_" % z in p and n >= 8 * 1025 for p, n in files.items()) for z in (5, 7, 9)), repr(files))
    s.gate("T6 LabVIEW handles flat +-100 over runs 1/11/21", max(hs) - min(hs) <= 100, repr(hs))
    vi.SetControlValue(labs[0], 64); g._run(vi, poll_s=30.0, hard_timeout_s=60.0); r64 = vi.GetControlValue(ret_lab); vi.SetControlValue(labs[0], 5)
    s.gate("T7 negative: site 64 -> return %r, no site64 file" % r64, r64 == 1 and not glob.glob(os.path.join(OUT, "t0_site64*")))
    s.R["no_vi_was_run"] = False; s.R["verification_level"] = "FUNCTIONAL (the scratch ran %d times)" % NRUN
    g._cache.pop(W, None); del vi
    s.save(); s.gate("T8 saved artefact ExecState 1", s.R["saves"].get("exec_state_before") == 1)


def quit_and_read():
    s.head("[5] graceful COM Quit (DLL_PROCESS_DETACH flushes the tails), verify gone, read the stamp files")
    r = subprocess.run([sys.executable, "-c", "import win32com.client as w\nw.Dispatch('LabVIEW.Application').Quit()\n"], capture_output=True, text=True, timeout=90)
    t0 = time.time()
    while "labview" in subprocess.run("tasklist", capture_output=True, text=True).stdout.lower() and time.time() - t0 < 60:
        time.sleep(2)
    gone = "labview" not in subprocess.run("tasklist", capture_output=True, text=True).stdout.lower()
    if not gone:
        subprocess.run(["taskkill", "/F", "/T", "/IM", "LabVIEW.exe"], capture_output=True); time.sleep(5)
        gone = "labview" not in subprocess.run("tasklist", capture_output=True, text=True).stdout.lower()
    s.gate("T9a LabVIEW gone (quit rc %d, forced=%s)" % (r.returncode, not gone), gone)
    data = {}
    for p in sorted(glob.glob(os.path.join(OUT, "t0_site*.bin"))):
        b = open(p, "rb").read(); n = len(b) // 8; v = struct.unpack("<%dq" % n, b[:n * 8]); data[os.path.basename(p)[3:9]] = (v[0], v[1:])
    s.fact("stamp files: %r" % {k: len(v[1]) for k, v in data.items()})
    # Run 2 (JEV-LADDER our-script-bug p=0.766, 03:59:58): the T7 negative run sets site ctl 1 to 64, so X does NOT
    # stamp site 05 on run NRUN+1 (return 1, no write - by design D arg). Expect NRUN for 05 and NRUN+1 for 07/09.
    want = {"site05": NRUN, "site07": NRUN + 1, "site09": NRUN + 1}
    ok = all(k in data and len(data[k][1]) == n for k, n in want.items())
    s.gate("T9b tails flushed: sites 05/07/09 hold %d/%d/%d stamps" % (NRUN, NRUN + 1, NRUN + 1), ok)
    if all(k in data for k in ("site05", "site07", "site09")):
        f = float(data["site05"][0]); n = min(len(data[k][1]) for k in ("site05", "site07", "site09"))
        ax = sorted((data["site07"][1][k] - data["site05"][1][k]) / f * 1e6 for k in range(n))
        ba = sorted((data["site09"][1][k] - data["site07"][1][k]) / f * 1e6 for k in range(n))
        q = lambda v, p: v[min(len(v) - 1, int(len(v) * p))]
        s.fact("A-X (array in front of A + 1 call) us: median %.2f p99 %.2f n=%d" % (q(ax, .5), q(ax, .99), n))
        s.fact("B-A (1 call, scalar) us: median %.2f p99 %.2f n=%d" % (q(ba, .5), q(ba, .99), n))
        s.fact("array cost = median(A-X) - median(B-A) = %.2f us  (a 2.6 MB copy would be >= 100 us)" % (q(ax, .5) - q(ba, .5)))


if __name__ == "__main__":
    rc = K.run(body, s)
    quit_and_read()
    s.gate("T10 md5 pins after quit", s.pin_check("FINAL")); s.dump()
    sys.exit(s.summary())
