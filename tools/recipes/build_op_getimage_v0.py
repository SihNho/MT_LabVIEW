# ---
# labview: build
# hardware: none
# ---
r"""build_op_getimage_v0.py - card chat-PI1c (retry of chat-PI1b): build claudeDev\OpGetImage_v0.vi =
(vi path, Traverse class + index) -> NODE reference -> Node.Get Image 6358C01 -> Write PNG File.vi, plus GObject
Position/Bounds and a GObject.UID echo on the same reference; then its op-hygiene record.

WHY THE RETRY. chat-PI1b swept VI Server:GObject 632A401..40F and found no Image output (build_op_getimage_v0.log:8-23).
External source (labviewwiki Node_class/Get_Image_method, fetched by the judgement session 2026-10-16): Get Image is a
method of the NODE class, ID 6358C01, inputs Image Depth (I32 1/4/8/24, default 8) and Background Color (U32), output
Image Data (the Graphics-Formats image cluster that Write PNG File.vi takes). Hypothesis review
archive/peer/2026-10-16-hypothesis-op-getimage.md: "partly" - the brief mixed Control.Get Image (6331C0C) with
Node.Get Image; its M1b and UID-echo points are applied below.

WHY A DIFFERENT DONOR. `UID to GObject Reference.vi` (donor OpOwnerChain_v1, used by chat-PI1b) outputs a GObject-typed
reference; a Node-class Invoke needs a Node-typed wire (a class conflict otherwise, docs/labview/references/
vi-scripting.md:232-242). The proven cast route is the c97 typed-control seed on donor OpSetIndexMode_v0
(Traverse(Class Name, index) -> Index Array -> To More Specific Class; tools/bench/diag_c97_tools_opbuild.py retarget(),
used for OpCaseFrames_v1 / OpTunnelUseDefault_v0 and the Node-seeded OpCreateIndicatorNested_v0,
docs/toolkit-capabilities.md:78). The seed is a control made on the `reference` input of a VI Server:Node property node
(GObject Position 632A800 + Bounds 632A803). The caller maps a UID to the Traverse index with gscript._uid_index and
CHECKS the UID echo. Helpers: tools/bench/pi_shots_lib.py (Rec, sweep, get_image) and, IMPORTED, the typed-seed
builder B / retarget / uid_echo of tools/bench/diag_c100_verbs_build.py:67-166 (prior-art review
archive/peer/2026-10-16-priorart-op-getimage-v2.md B3). Verbs used: build_invoke, build_property, drop_subvi, wire, wire_control,
create_control, create_indicator, delete_object, net_map, node_terms_uid, panel_wiring, save, exec_state,
set_auto_error_handling, hygiene_run.

PREDICTION (gates):
  M1  a VI Server:Node Invoke with ID 6358C01 on a scratch EMPTY_v0 copy has terminals named `Image Depth`,
      `BG Color` and `Image Data` (quoted in full; chat-PI1d: 'BG Color' = Background Color, judgement-accepted).
      FATAL: otherwise the run returns before any build.
  M1b (recorded, hypothesis review 3b) the same ID on a VI Server:GObject Invoke has NO `Image Depth` terminal.
  M2  a VI Server:Node property node 632A800 + 632A803 has outputs `Position`, `Bounds`.
  B1  donor copy ExecState 1;  R1/R2 IndexMode PN deleted ES 1, Node seed -> TMSC -> Position/Bounds PN ES 1.
  B3  Get Image Invoke's `reference` reads the TMSC output; ES 1.  B4 Write PNG File.vi dropped, Image Data -> its
      image sink, Get Image error out -> its error in, a path control on its path sink.  B5 UID echo PN on the TMSC.
  B6  ExecState 1 -> scripted save.  B7 COLD ExecState 1 in a fresh LabVIEW.  Labels JSON written.
  F1  (hygiene warm-up) on a byte copy of the donor, Traverse('Node')[0]: echo == that node's uid, all three error
      outputs empty, the PNG exists and opens in PIL (its size and the node's Bounds are recorded).
  H1  gscript.hygiene_run: 2,000 calls (20 rounds x 100, copy recycled), 0 errors, handles flat +-100 -> PASS record
      tools/bench/op_hygiene/OpGetImage_v0.json.
No VI under study is opened or run; only op VIs run. Scratch deleted; LabVIEW killed (nothing saved) and verified gone.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/build_op_getimage_v0d.log -- py -u tools/recipes/build_op_getimage_v0.py
"""
import os, sys, json, shutil, time, tempfile                                         # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench")); sys.path.insert(0, os.path.join(ROOT, "tools"))  # noqa: E702
import pi_shots_lib as L                                                             # noqa: E402
import gscript as g                                                                  # noqa: E402
# the typed-seed builder B / retarget / uid_echo, IMPORTED (prior-art v2 B3): import side effect g._run.__defaults__ =
# (6.0, 180.0) == gscript's own defaults (gscript.py:584), and its gate() prints to its own G dict - re-gated here.
import diag_c100_verbs_build as C100                                                 # noqa: E402
CD = g.CLAUDEDEV
DONOR = os.path.join(CD, "OpSetIndexMode_v0.vi")
EMPTY = os.path.join(CD, "EMPTY_v0.vi")
OP = L.OP_PATH
SCR = os.path.join(CD, "scratch_getimage_%s.vi" % time.strftime("%H%M%S"))
PNG_VI = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\picture\png.llb\Write PNG File.vi"
NODE, GOBJ, MID = "VI Server:Node", "VI Server:GObject", "6358C01"
WANT = ("Image Depth", "BG Color", "Image Data")   # chat-PI1d: LabVIEW's short name for Background Color (accepted)
STD = L.STD
HYG_DIR = os.path.join(L.OUTDIR, "hygiene_tmp")    # card chat-PI1d rule: hygiene PNGs here, deleted after the record
HYG_PNG = os.path.join(HYG_DIR, "opgetimage_hyg.png")
os.makedirs(HYG_DIR, exist_ok=True)
s = L.Rec("build_op_getimage_v0d")
sweep, tl = L.sweep, L.tl


def names(by, uid):
    return [r["name"] for r in by[uid][1] if r["name"] not in STD]


def check_method():
    s.head("[1] Node.Get Image %s on a scratch copy of EMPTY_v0" % MID)
    shutil.copyfile(EMPTY, SCR); g.open_panel(SCR); time.sleep(1.0)                  # noqa: E702
    gi = int(g.build_invoke(SCR, NODE, MID, (40, 40))[0]["uid"]); by = sweep(SCR)    # noqa: E702
    s.fact("Node %s -> Invoke #%s terminals %s" % (MID, gi, tl(by, gi)))
    s.R["method"] = {"class": NODE, "id": MID, "terminals": tl(by, gi)}
    s.gate("M1 Node-class Invoke %s has terminals %s" % (MID, "/".join(WANT)), all(w in names(by, gi) for w in WANT),
           names(by, gi), fatal=True)
    try:
        go = int(g.build_invoke(SCR, GOBJ, MID, (400, 40))[0]["uid"]); by = sweep(SCR)  # noqa: E702
        s.fact("GObject %s -> Invoke #%s terminals %s" % (MID, go, tl(by, go)))
        s.gate("M1b GObject-class Invoke %s has no Image Depth terminal" % MID, "Image Depth" not in names(by, go), names(by, go))
    except Exception as e:                                                           # noqa: BLE001
        s.fact("M1b GObject-class build_invoke raised %s" % str(e)[:160])
    pn = int(g.build_property(SCR, NODE, [("632A800", False), ("632A803", False)], (40, 400))[0]["uid"])
    by = sweep(SCR); outs = [r["name"] for r in by[pn][1] if r["is_source"] and r["name"] not in STD]  # noqa: E702
    s.fact("Node PN 632A800+632A803 terminals %s" % tl(by, pn))
    s.gate("M2 Node property outputs named Position and Bounds", outs == ["Position", "Bounds"], outs, fatal=True)
    try:
        g.close_panel(SCR)
    except Exception:                                                                # noqa: BLE001
        pass


def build():
    s.head("[2] donor copy OpSetIndexMode_v0 -> OpGetImage_v0"); s.fact("handles after restart %s" % L.restart())  # noqa: E702
    b = C100.B(os.path.basename(DONOR), os.path.basename(OP))
    s.gate("B1 donor copy ExecState 1", g.exec_state(OP) == 1, "", fatal=True)
    tm, pn = C100.retarget(b, "OpGetImage_v0", NODE, [("632A800", False), ("632A803", False)], (900, 450))
    s.gate("R1/R2 IndexMode PN deleted + Node seed -> TMSC -> Position/Bounds PN, ES 1 (C100.retarget)", bool(tm), (tm, pn),
           fatal=True)
    s.head("[3] Invoke Node.Get Image %s on the TMSC output" % MID)
    gi = int(g.build_invoke(OP, NODE, MID, (900, 60))[0]["uid"]); b.inv0.add(gi)    # noqa: E702
    b.w(tm, "specific class reference", gi, "reference", sc="Function", dc="Invoke", branch=True)
    _n, trow = b.terms(tm); _n, grow = b.terms(gi)                                   # noqa: E702
    tw = next(r["wire"] for r in trow if r["name"] == "specific class reference" and r["is_source"])
    gw = next(r["wire"] for r in grow if r["name"] == "reference" and not r["is_source"])
    es = g.exec_state(OP)
    s.fact("Get Image #%s terminals %s" % (gi, [(r["i"], r["name"], r["is_source"], r["wire"]) for r in grow]))
    s.gate("B3 Get Image.reference reads the TMSC output, ES 1", tw == gw != 0 and es == 1, (tw, gw, es), fatal=True)
    lab = {"controls": {}, "indicators": {}}
    for nm in ("Image Depth", "BG Color"):
        lab["controls"][nm] = b.ctl(gi, nm)
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
    b.w(gi, "Image Data", wp, img_in, sc="Invoke", dc="SubVI")
    b.w(gi, "error out", wp, ein, sc="Invoke", dc="SubVI")
    _n, wrow = b.terms(wp)
    wired = {r["name"]: r["wire"] for r in wrow if not r["is_source"]}
    s.gate("B4c Image Data and error wires land on Write PNG", wired.get(img_in) and wired.get(ein), wired)
    lab["controls"]["png_path"] = b.ctl(wp, path_in)
    lab["indicators"]["png_err"] = b.ind(wp, "error out")
    s.head("[5] Position/Bounds indicators + UID echo")
    lab["indicators"]["Position"] = b.ind(pn, "Position")
    lab["indicators"]["Bounds"] = b.ind(pn, "Bounds")
    lab["indicators"]["pn_err"] = b.ind(pn, "error out")
    u = C100.uid_echo(b, tm, (900, 750))
    lab["indicators"]["UID"] = b.ind(u, "UID")
    lab["indicators"]["echo_err"] = b.ind(u, "error out")
    s.gate("B5 every control/indicator created", None not in list(lab["controls"].values()) + list(lab["indicators"].values()), lab)
    g.set_auto_error_handling(OP, False); b.purge()                                  # noqa: E702
    es = g.exec_state(OP); s.gate("B6 ExecState 1 before the save", es == 1, es, fatal=True)  # noqa: E702
    g.save(OP)
    lab["all_controls"] = [r["label"] for r in g.panel_wiring(OP) if not r["indicator"]]
    lab.update({"op": OP, "md5": L.md5(OP), "method": s.R.get("method"), "donor": DONOR, "tmsc": tm, "pn": pn,
                "get_image": gi, "write_png": wp, "echo_pn": u, "seed_class": NODE})
    json.dump(lab, open(L.LABELS, "w", encoding="utf-8"), indent=1); s.fact("labels -> %s %s" % (L.LABELS, lab))  # noqa: E702
    try:
        g.close_panel(OP)
    except Exception:                                                                # noqa: BLE001
        pass
    s.head("[6] cold re-read"); s.fact("handles after restart %s" % L.restart())    # noqa: E702
    es2 = g.exec_state(OP); s.gate("B7 ExecState 1 COLD in a fresh LabVIEW", es2 == 1, es2, fatal=True)  # noqa: E702
    s.R["op"] = {"path": OP, "md5": L.md5(OP)}
    s.arts += [OP, L.LABELS]


W = {}


def warm(copy):
    uid0 = int(g.report_all(copy, "Node")[0]["uid"]); W["uid0"] = uid0              # noqa: E702
    if os.path.exists(HYG_PNG):
        os.remove(HYG_PNG)
    r = L.get_image(copy, uid0, HYG_PNG, cls="Node", index=0)
    from PIL import Image
    size = Image.open(HYG_PNG).size if os.path.exists(HYG_PNG) else None
    s.fact("F1 Traverse('Node')[0] uid %s -> %s; PNG size %s" % (uid0, r, size))
    s.R["F1"] = {"uid": uid0, "out": r, "png_size": size}
    s.gate("F1 echo == uid, no errors, PNG written and readable",
           r["echo"] == uid0 and not (r["err_png"] or r["err_pn"] or r["err_echo"]) and size is not None, r, fatal=True)


def workload(copy):
    r = L.get_image(copy, W["uid0"], HYG_PNG, cls="Node", index=0)
    if r["echo"] != W["uid0"]:
        return "echo %s != %s" % (r["echo"], W["uid0"])
    return r["err_png"] or r["err_pn"] or r["err_echo"] or ""


def main():
    s.head("[0] restart LabVIEW"); s.fact("handles after restart %s" % L.restart())  # noqa: E702
    check_method()
    build()
    s.head("[7] op hygiene (gscript.hygiene_run, 2,000 calls)")
    rec = g.hygiene_run(OP, workload, DONOR, total=2000, per_round=100, recycle=True, warm=warm, card="chat-PI1d",
                        log="tools/bench/build_op_getimage_v0d.log", say=s.fact,
                        workload_text="warm F1 then 20 rounds x 100 OpGetImage_v0 calls (Traverse('Node')[0], depth 24, "
                                      "PNG to tools/bench/pi_shots_20261016/hygiene_tmp, deleted after the record) on a fresh never-saved byte copy of OpSetIndexMode_v0.vi per round")
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
import glob                                                                          # noqa: E402
for p in glob.glob(os.path.join(CD, "scratch_hyg_OpGetImage_v0_*.vi")):            # a copy a failed warm-up left open
    try:
        os.remove(p); s.fact("removed left hygiene copy %s" % os.path.basename(p))  # noqa: E702
    except Exception as e:                                                           # noqa: BLE001
        s.fact("hygiene copy delete failed %s" % e)
s.gate("H4 scratch deleted: %s (+ hygiene copies)" % os.path.basename(SCR),
       not os.path.exists(SCR) and not glob.glob(os.path.join(CD, "scratch_hyg_OpGetImage_v0_*.vi")))
sys.exit(s.finish(os.path.join(L.OUTDIR, "build_op_getimage_v0d.json")))
