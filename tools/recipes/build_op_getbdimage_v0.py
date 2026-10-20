# ---
# labview: build
# hardware: none
# evidence: tools/bench/cards/brief_chat-PI2.md
# ---
r"""build_op_getbdimage_v0.py - card chat-PI2: build claudeDev\OpGetBDImage_v0.vi = (vi path, PNG path) ->
Open VI Reference -> VI.Block Diagram: Get Image Scaled (VI class, method ID 42C; Image Depth 24 at call time, Maximum
Width / Maximum Height UNWIRED = the actual size) -> Write PNG File.vi; then its op-hygiene record.

EXISTING FIRST (checked 2026-10-19): Node.Get Image 6358C01 / OpGetImage_v0 (chat-PI1d) images ONE node and needs a
Traverse index; there is no whole-diagram image op (grep 'Get Image Scaled|42C' over docs/vi-server-ids.json,
docs/toolkit-capabilities.md, docs/NAMES.md: none). Method source: https://labviewwiki.org/wiki/VI_class/Block_Diagram.Get_Image_Scaled_method
(fetched by the judgement session 2026-10-19, brief). Pattern = tools/recipes/build_op_getimage_v0.py (chat-PI1d): the
same IMPORTED typed builder B (tools/bench/diag_c100_verbs_build.py:67-140: copy donor, purge junk Invokes, wire by uid,
ctl/ind by terminal name), the same Write PNG File.vi tail and terminal names (build_op_getimage_v0d.log:48), the same
gscript.hygiene_run. A VI-class Invoke on the donor's `Open VI Reference.vi reference` by g.wire(branch=True) is the
route OpBuildIA_v0 used for a VI-class Property (tools/bench/build_keystone.log:1738-1740 'accepted'); connect2 on the
same branch made a BAD wire once (tools/bench/diag_bdloaded_reader.log:13) - so g.wire (via B.w), never connect2.
DONOR = claudeDev\OpReport_v3.vi (5 nodes: Open VI Reference -> Traverse -> Index Array -> 2 PNs, NO Close Reference,
docs/toolkit-capabilities.md:441,527) - a pure reader, so the donor branch that stays in the op has no side effect and
no Close Reference can race the new branch. Shared wrapper: pi_shots_lib.get_bd_image (+ png_stats for the blank check).

PREDICTION (gates):
  M1  a `VI Server:VI` Invoke with ID 42C on a scratch EMPTY_v0 copy has EXACTLY the data terminals GetDiagramImageScaled,
      img depth, img data, max width, max height (LabVIEW short names, measured build_op_getbdimage_v0.log:8; the wiki's
      long names Image Depth / Image Data / Maximum Width / Maximum Height also accepted, case-insensitive; judgement
      chat-PI2b; review archive/peer/2026-10-19-hypothesis-op-getbdimage.md R1). FATAL otherwise.
  B1  donor copy ExecState 1.  B2 the Open VI Reference node (source `vi reference`) is a Function.
  B3  Invoke 42C `reference` reads the SAME wire as `vi reference` (branch); ES 1.
  B4  Write PNG File.vi dropped; Image Data -> `image data`, Invoke error out -> `error in (no error)`; a control on
      `path to PNG file`, an indicator on Write PNG `error out`; a control on `Image Depth`.
  B6  ExecState 1 -> scripted save.  B7 COLD ExecState 1 in a fresh LabVIEW.  Labels JSON written.
  F1  (hygiene warm-up) on a fresh byte copy of the donor: error '' and the PNG opens in PIL, 24-bit RGB, not blank.
  H1  gscript.hygiene_run: 2,000 calls (20 x 100, copy recycled), 0 errors, handles flat +-100 -> PASS record
      tools/bench/op_hygiene/OpGetBDImage_v0.json.  H2 hygiene PNG folder deleted.
No VI under study is opened or run; only op VIs run. Scratch deleted; LabVIEW killed (nothing saved) and verified gone.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/build_op_getbdimage_v0b.log -- py -u tools/recipes/build_op_getbdimage_v0.py
"""
import os, sys, json, shutil, time, glob                                             # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench")); sys.path.insert(0, os.path.join(ROOT, "tools"))  # noqa: E702
import pi_shots_lib as L                                                             # noqa: E402
import gscript as g                                                                  # noqa: E402
import diag_c100_verbs_build as C100                                                 # noqa: E402  (typed builder B, imported)
CD = g.CLAUDEDEV
DONOR = os.path.join(CD, "OpReport_v3.vi")
EMPTY = os.path.join(CD, "EMPTY_v0.vi")
OP = L.BD_OP_PATH
SCR = os.path.join(CD, "scratch_getbdimage_%s.vi" % time.strftime("%H%M%S"))
PNG_VI = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\picture\png.llb\Write PNG File.vi"
VIC, MID = "VI Server:VI", "42C"
STD = L.STD
HYG_DIR = os.path.join(L.OUTDIR, "hygiene_tmp_bd")
HYG_PNG = os.path.join(HYG_DIR, "opgetbdimage_hyg.png")
os.makedirs(HYG_DIR, exist_ok=True)
s = L.Rec("build_op_getbdimage_v0")
sweep, tl = L.sweep, L.tl


def names(by, uid):
    return [r["name"] for r in by[uid][1] if r["name"] not in STD]


def check_method():
    s.head("[1] VI.Block Diagram: Get Image Scaled %s on a scratch copy of EMPTY_v0" % MID)
    shutil.copyfile(EMPTY, SCR); g.open_panel(SCR); time.sleep(1.0)                  # noqa: E702
    gi = int(g.build_invoke(SCR, VIC, MID, (40, 40))[0]["uid"]); by = sweep(SCR)     # noqa: E702
    nm = names(by, gi)
    s.fact("VI %s -> Invoke #%s terminals %s" % (MID, gi, tl(by, gi)))
    s.R["method"] = {"class": VIC, "id": MID, "terminals": tl(by, gi)}
    # chat-PI2b (judgement: short OR long names, case-insensitive; hypothesis review R1: an EXACT list, not "contains")
    want = [("img depth", "image depth"), ("img data", "image data"), ("max width", "maximum width"),
            ("max height", "maximum height")]
    low = sorted(set(n.lower() for n in nm))
    ok = all(any(a in low for a in pair) for pair in want) and len(low) == 1 + len(want) and \
        "getdiagramimagescaled" in low
    s.gate("M1 VI-class Invoke %s terminals = GetDiagramImageScaled + img depth/img data/max width/max height (short or "
           "long, case-insensitive, nothing else)" % MID, ok, nm, fatal=True)
    try:
        g.close_panel(SCR)
    except Exception:                                                                # noqa: BLE001
        pass


def build():
    s.head("[2] donor copy OpReport_v3 -> OpGetBDImage_v0"); s.fact("handles after restart %s" % L.restart())  # noqa: E702
    b = C100.B(os.path.basename(DONOR), os.path.basename(OP))
    s.gate("B1 donor copy ExecState 1", g.exec_state(OP) == 1, "", fatal=True)
    by = sweep(OP)
    ovr = next((u for u, (_n, rows) in by.items() if any(r["name"] == "vi reference" and r["is_source"] for r in rows)), None)
    fn = g.uids(OP, "Function")
    s.gate("B2 Open VI Reference (source 'vi reference') found and is a Function", ovr is not None and ovr in fn, (ovr, fn),
           fatal=True)
    s.head("[3] Invoke VI.Get Image Scaled %s on the vi reference (branch)" % MID)
    gi = int(g.build_invoke(OP, VIC, MID, (900, 60))[0]["uid"]); b.inv0.add(gi)     # noqa: E702
    b.w(ovr, "vi reference", gi, "reference", sc="Function", dc="Invoke", branch=True)
    _n, orow = b.terms(ovr); _n, grow = b.terms(gi)                                  # noqa: E702
    ow = next(r["wire"] for r in orow if r["name"] == "vi reference" and r["is_source"])
    gw = next(r["wire"] for r in grow if r["name"] == "reference" and not r["is_source"])
    es = g.exec_state(OP)
    s.fact("Get Image Scaled #%s terminals %s" % (gi, [(r["i"], r["name"], r["is_source"], r["wire"]) for r in grow]))
    s.gate("B3 Invoke.reference reads the vi reference wire, ES 1", ow == gw != 0 and es == 1, (ow, gw, es), fatal=True)
    lab = {"controls": {}, "indicators": {}}
    t_depth = next(r["name"] for r in grow if r["name"].lower() in ("img depth", "image depth") and not r["is_source"])
    t_data = next(r["name"] for r in grow if r["name"].lower() in ("img data", "image data") and r["is_source"])
    s.fact("measured terminal names used: depth %r, data %r" % (t_depth, t_data))
    lab["controls"]["Image Depth"] = b.ctl(gi, t_depth)          # key kept: pi_shots_lib.get_bd_image reads it
    s.head("[4] Write PNG File.vi")
    sv0 = set(g.uids(OP, "SubVI")); g.drop_subvi(OP, PNG_VI, 0, (1300, 60)); b.purge()  # noqa: E702
    wp = [u for u in g.uids(OP, "SubVI") if u not in sv0]
    s.gate("B4a exactly one new SubVI (Write PNG File.vi)", len(wp) == 1, wp, fatal=True)
    wp = wp[0]; _n, wrow = b.terms(wp)                                               # noqa: E702
    s.fact("Write PNG #%s terminals %s" % (wp, [(r["i"], r["name"], r["is_source"]) for r in wrow]))
    sinks = [r["name"] for r in wrow if not r["is_source"]]
    img_in = next((n for n in sinks if "image" in n.lower()), None)
    path_in = next((n for n in sinks if "path" in n.lower()), None)
    ein = next((n for n in sinks if n.startswith("error in")), None)
    s.gate("B4b Write PNG has image / path / error-in sinks", None not in (img_in, path_in, ein), (img_in, path_in, ein), fatal=True)
    b.w(gi, t_data, wp, img_in, sc="Invoke", dc="SubVI")
    b.w(gi, "error out", wp, ein, sc="Invoke", dc="SubVI")
    _n, wrow = b.terms(wp)
    wired = {r["name"]: r["wire"] for r in wrow if not r["is_source"]}
    _n, grow2 = b.terms(gi)
    dout = next((r["wire"] for r in grow2 if r["name"] == t_data and r["is_source"]), 0)
    s.gate("B4c Image Data and error wires land on Write PNG, and the Invoke's OUT-side %r carries the image wire "
           "(review R3)" % t_data, bool(wired.get(img_in) and wired.get(ein)) and dout == wired.get(img_in),
           (wired, dout))
    lab["controls"]["png_path"] = b.ctl(wp, path_in)
    lab["indicators"]["png_err"] = b.ind(wp, "error out")
    s.gate("B5 every control/indicator created", None not in list(lab["controls"].values()) + list(lab["indicators"].values()), lab)
    _n, grow = b.terms(gi)
    s.fact("Get Image Scaled inputs wired after build %s" % [(r["name"], r["wire"]) for r in grow if not r["is_source"]])
    g.set_auto_error_handling(OP, False); b.purge()                                  # noqa: E702
    es = g.exec_state(OP); s.gate("B6 ExecState 1 before the save", es == 1, es, fatal=True)  # noqa: E702
    g.save(OP)
    lab["all_controls"] = [r["label"] for r in g.panel_wiring(OP) if not r["indicator"]]
    lab.update({"op": OP, "md5": L.md5(OP), "method": s.R.get("method"), "donor": DONOR, "ovr": ovr,
                "get_image_scaled": gi, "write_png": wp})
    json.dump(lab, open(L.BD_LABELS, "w", encoding="utf-8"), indent=1); s.fact("labels -> %s %s" % (L.BD_LABELS, lab))  # noqa: E702
    try:
        g.close_panel(OP)
    except Exception:                                                                # noqa: BLE001
        pass
    s.head("[5] cold re-read"); s.fact("handles after restart %s" % L.restart())    # noqa: E702
    es2 = g.exec_state(OP); s.gate("B7 ExecState 1 COLD in a fresh LabVIEW", es2 == 1, es2, fatal=True)  # noqa: E702
    s.R["op"] = {"path": OP, "md5": L.md5(OP)}
    s.arts += [OP, L.BD_LABELS]


def warm(copy):
    if os.path.exists(HYG_PNG):
        os.remove(HYG_PNG)
    r = L.get_bd_image(copy, HYG_PNG)
    st = L.png_stats(HYG_PNG) if os.path.exists(HYG_PNG) else None
    s.fact("F1 whole diagram of %s -> %s; PNG %s" % (os.path.basename(copy), r, st))
    s.R["F1"] = {"out": r, "png": st}
    s.gate("F1 no error, PNG written, RGB, not blank",
           not r["err_png"] and st is not None and st["mode"] == "RGB" and not st["blank"], (r, st), fatal=True)


def workload(copy):
    return L.get_bd_image(copy, HYG_PNG)["err_png"]


def main():
    s.head("[0] restart LabVIEW"); s.fact("handles after restart %s" % L.restart())  # noqa: E702
    check_method()
    build()
    s.head("[6] op hygiene (gscript.hygiene_run, 2,000 calls)")
    rec = g.hygiene_run(OP, workload, DONOR, total=2000, per_round=100, recycle=True, warm=warm, card="chat-PI2b",
                        log="tools/bench/build_op_getbdimage_v0b.log", say=s.fact,
                        workload_text="warm F1 then 20 rounds x 100 OpGetBDImage_v0 calls (whole diagram, Image Depth 24, "
                                      "PNG to tools/bench/pi_shots_20261016/hygiene_tmp_bd, deleted after the record) on a fresh never-saved byte copy of OpReport_v3.vi per round")
    s.fact("hygiene record %s" % {k: rec.get(k) for k in ("status", "calls", "errors", "error_samples", "max_dev_closed", "refs_live_delta")})
    s.gate("H1 op-hygiene record PASS", rec.get("status") == "PASS", rec.get("status"))
    s.arts.append(g.op_hygiene_record_path(OP))
    shutil.rmtree(HYG_DIR, ignore_errors=True)
    s.gate("H2 hygiene PNGs deleted after the record (%s)" % HYG_DIR, not os.path.exists(HYG_DIR))


try:
    main()
except L.StopRun as e:
    s.fact("STOPPED at gate: %s" % e)
except Exception as e:                                                               # noqa: BLE001
    import traceback; traceback.print_exc(); s.gate("the run completed without an unhandled exception", False, str(e)[:200])  # noqa: E702
try:
    s.fact("ref_counts %s" % (g.ref_counts(),))
except Exception:                                                                    # noqa: BLE001
    pass
s.gate("H7 LabVIEW gone at exit (killed, nothing saved)", L.kill_and_verify())
if os.path.exists(SCR):
    try:
        os.remove(SCR)
    except Exception as e:                                                           # noqa: BLE001
        s.fact("scratch delete failed %s" % e)
for p in glob.glob(os.path.join(CD, "scratch_hyg_OpGetBDImage_v0_*.vi")):          # a copy a failed warm-up left open
    try:
        os.remove(p); s.fact("removed left hygiene copy %s" % os.path.basename(p))  # noqa: E702
    except Exception as e:                                                           # noqa: BLE001
        s.fact("hygiene copy delete failed %s" % e)
shutil.rmtree(HYG_DIR, ignore_errors=True)
s.gate("H4 scratch deleted: %s (+ hygiene copies)" % os.path.basename(SCR),
       not os.path.exists(SCR) and not glob.glob(os.path.join(CD, "scratch_hyg_OpGetBDImage_v0_*.vi")))
sys.exit(s.finish(os.path.join(L.OUTDIR, "build_op_getbdimage_v0.json")))
