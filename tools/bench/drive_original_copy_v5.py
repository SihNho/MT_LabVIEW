r"""drive_original_copy_v5.py - D0 on the 4.5 COPY.  v4 with ONE change: every click point is
LOCATED on this VI's own running panel, in a screenshot taken in this run.

WHAT IS REUSED, WHAT IS NEW (the one line the brief asks for)
  REUSED WHOLESALE, by import, exactly as v4 did:
    `drive_original_copy_v2` (as d4.d0) - the second COM apartment `PollCom`, the NEVER-JOINED
      `RunThread`, rec/log/getv/state/shot/gui/click/keys/focus/win_rect/win_present/dialogs/
      inside/md5/listdir_stats/delete_tiffs, and `answer_save_dialog` (the keyboard file-dialog
      handler - it types an absolute path, so it needs no coordinate at all).
    `drive_original_copy_v4` (as d4) - the 4.5 retarget, the motor-gate wrapper + `parse_motor` /
      `tmx_from`, the read-only PANEL RECORD, the HWND-TOKEN click gate (`clickprobe`,
      `delivered`, `gated_click_hwnd`, v3's logic), and the stop ladder `stop_single_write` /
      `stop_rearmed`.
    v3's geometry constants are imported ONLY to be printed beside what we measure.  NOTHING is
      derived from them.
  NEW, and only this:
    (1) `tools/bench/d0_locate.py` - locate the `Done Picking \nBeads?` Yes button, each
        `choose bandpass` Yes button and the IMAQ image display IN THE SCREENSHOT OF THIS RUN.
    (2) every click is preceded by a capture, followed by a capture, and confirmed by a
        machine-readable consequence (marker count / a window / an hwnd death).
    (3) the stop tries VI Server FIRST now that the experiment loop is actually running, and
        FALLS BACK to COM Abort, recording which one worked and its latency.
    (4) the post-run `TMX?` re-read happens only AFTER LabVIEW has exited.

THE RULE THIS IMPLEMENTS
  `archive/peer/2026-09-18-d0v4-picking-loop-frozen.md` ACCEPTED: the picking loop was live and
  the click missed.  EVERY click point used on Track_D0_copy_20260918.vi must be LOCATED on that
  VI's own running panel; no coordinate may be inherited from the V6 copy.  v4's gate 7 compared
  WINDOW RECTS, which say nothing about control positions, and control positions are unreadable
  over our COM path (`tools/bench/diag_d0_inventory.log:56`), so the screenshot IS the
  measurement.  User rule 2026-09-18 17:5x = `docs/cycle27-plan.md` Pre-decided 9.

WHAT WAS MEASURED BEFORE THIS FILE WAS WRITTEN (on `tools/bench/p3_done_check.png`, a capture of
THIS copy's own running panel at 2026-09-18 17:28, search rect (0,51,1920,1080)):
    `Done Picking \nBeads?` Yes button  box (1155,848)-(1200,876)  CENTRE (1177,862)
    caption "Yes" 25x12 px, template score 0.00; next-best red-captioned button 19.16 at (1175,511)
    the point v4 actually clicked                                          (1114,915)
        => 63 px left of and 53 px below the button's centre; outside the button entirely.
    image display                      box (297,451)-(937,963) = 640x512 (the 1280x1024 camera
                                       at half scale - an independent check that the box is right)
  Those numbers are the REFERENCE PATCH's provenance and the expectation; they are NOT clicked.
  Every leg re-locates from its own fresh capture and clicks what it finds there.

TARGET
  ORIGINAL  G:\...\2. Tracking\Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi
            md5 c39f36e0675339673b707c59f0784fee - preloaded READ-ONLY, md5 before AND after.
  COPY      C:\Program Files\...\LabVIEW 2026\user.lib\claudeDev\Track_D0_copy_20260918.vi
            RUN only: never copied, never saved, never deleted; md5 before AND after.

================================ PREDICTION CONTRACT ================================
 G0  `py tools/motor_gate.py --session start` exits 0 BEFORE LabVIEW opens COM3/COM4.  A non-zero
     exit ABORTS the run before LabVIEW is touched.  `--session end` is NEVER called.
 G1  md5(ORIGINAL) == c39f36e0675339673b707c59f0784fee BEFORE.
 G2  the copy exists; md5 recorded.  No file is copied.
 G3  apartment2 attaches, the ORIGINAL is resident read-only, the copy opens ExecState == 1,
     no dialog BLOCKING.
 G4  PANEL RECORD: >= 55 of the 60 front-panel CONTROLS return a value.  NOTHING is written.
 G5  the panel window's rect is readable at run time (recorded, not used to derive any click).
 -- per leg (leg 1 = run1/cal001, leg 2 = run2/cal002; the whole cycle runs TWICE) --
 L1  Run(False) on its own never-joined apartment takes the VI out of idle within RUN_SETTLE.
 L2  the IMAQ image display is LOCATED in this leg's own capture, >= 200x150 px, inside the panel.
 L3  3 picks at fractions of THAT located rect; the capture AFTER shows >= 3 more red markers
     inside it than the capture BEFORE (the VI drew them -> the loop is alive AND the clicks
     landed).  This is the post-click readback the review said was missing.
 L4  the `Done Picking \nBeads?` Yes button is LOCATED in a capture taken after the picks:
     exactly one red-captioned button survives shape + caption + template filtering, template
     score <= 12.0 and at most half the runner-up's.  Its box and centre are logged and a crop is
     saved beside the log.
 L5  clickprobe (never `-Action click`) at that centre reports the click DELIVERED to the panel
     hwnd (all four checks true).
 L6  BRIEF STEP 5: a `choose bandpass` window is present within 30 s of the click.  NOTE: the
     z-stack calibration between the click and the first panel was measured at ~2 min on the V6
     copy (`drive_original_copy_v2.py:147`), so this gate may FAIL on timing alone; L7 is the
     one that says whether the picking loop ended.
 L7  the picking loop ended: a `choose bandpass` or the save dialog appears within CAL_WAIT.
 L8  EXACTLY 3 `choose bandpass` panels, each Yes button LOCATED in that panel's own capture and
     closed by an HWND-token-gated click; the TERMINAL state is the save dialog, never the cap.
 L9  the save dialog takes an ABSOLUTE path under tools/bench/d0_out/<run-id>/ (keyboard only -
     there is NO save-path and NO save-name CONTROL on this panel: `Cal File Path` 27930,
     `Track File Path` 28450 and `File # Saved` 6 are INDICATORS, so the destination arrives
     through `ReadWriteFile` uid 26615's file dialog).
 L10 the cal file exists there with size > 0.
 L11 `current image number` (uid 34200) STRICTLY INCREASES over RUN_S = 30 s.  It read 0 for the
     whole of v4's run because the VI never left the picking stage.
 L12 STOP: the VI-Server write is tried FIRST (the stop Booleans are read inside Diagram#639, the
     frame-loop body, so this is the first run in which a write to them can mean anything);
     then re-armed writes; then COM Abort.  WHICH one worked and its latency are recorded.
 L13 a `tra*` file exists in the run folder with size > 0.
 G90 md5(COPY) AFTER == BEFORE, and the copy still exists (never saved, never deleted).
 G91 md5(ORIGINAL) AFTER == c39f36e0675339673b707c59f0784fee.
 G92 LabVIEW has EXITED before the motor port is touched (v4's G25 failed because the VI still
     owned COM3 - an ordering fact, not a limit change).
 G93 post-run motor read: `TMX?` still 39.

    py tools/bgrun.py --material --max-min 30 --log tools/bench/drive_original_copy_v5.log \
        -- py -u tools/bench/drive_original_copy_v5.py
====================================================================================
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "tools"))
sys.path.insert(0, HERE)

import drive_original_copy_v4 as d4                                            # noqa: E402
import d0_locate as L                                                          # noqa: E402
from bench_prep import labview_handles                                         # noqa: E402

d0 = d4.d0

ORIGINAL, ORIGINAL_MD5, COPY = d4.ORIGINAL, d4.ORIGINAL_MD5, d4.COPY

STAMP = time.strftime("%Y%m%d_%H%M%S")
RUN_ID = "v5_%s" % STAMP
RUN_DIR = os.path.join(HERE, "d0_out", RUN_ID)
SHOTS = os.path.join(HERE, "d0_shots_v5")
EVID = os.path.join(HERE, "d0_evidence_v5")

d0.RUN_DIR = RUN_DIR
d0.SHOTS = SHOTS
d0.STAMP = STAMP
d0.RUN_ID = RUN_ID
d0.D0_JSON = os.path.join(HERE, "drive_original_copy_v5.json")
d4.RUN_DIR = RUN_DIR
d4.SHOTS = SHOTS

D0_JSON = d0.D0_JSON
PROBE_JSON = os.path.join(HERE, "drive_original_copy_v5_clickrecords.json")

rec, log, getv, state, shot = d0.rec, d0.log, d0.getv, d0.state, d0.shot
FACTS = d0.FACTS
C_STOP, C_STOP2, C_DONE, C_COUNT = d0.C_STOP, d0.C_STOP2, d0.C_DONE, d0.C_COUNT
I_FRAME, I_CALPATH, I_TRACKPATH = d0.I_FRAME, d0.I_CALPATH, d0.I_TRACKPATH
BANDPASS_TITLE, SAVE_TITLE = d0.BANDPASS_TITLE, d0.SAVE_TITLE

# v3's V6 constants, imported ONLY so the log can print what we did NOT use.
V6_DONE_XY = d4.V6_DONE_XY                       # (1114, 915) - the point that missed
V6_IMAGE_RECT = d4.V6_IMAGE_RECT                 # (232, 500, 873, 1013)

# the reference measurement, from p3_done_check.png - printed for comparison, never clicked
REF_DONE_BOX = (1155, 848, 1200, 876)
REF_DONE_CENTRE = (1177, 862)

RUN_SETTLE = 60.0
PICK_SETTLE = 2.5
BANDPASS_GATE_S = 30.0        # brief step 5
CAL_WAIT_1 = 300.0
CAL_WAIT_2 = 240.0
BANDPASS_WAIT = 150.0
BP_CAP = 8
RUN_S = 30.0
STOP_WAIT = 45.0
RUN2_BUDGET_S = 1150.0
EXIT_WAIT_S = 240.0

PICK_FRACS = [(0.40, 0.60), (0.21, 0.37), (0.61, 0.84)]   # inside the LOCATED display rect
LOC = {}


# =============================================================================================
# capture -> locate -> act -> capture -> confirm
# =============================================================================================
def capture(name):
    p = shot(name)
    for _ in range(12):
        if os.path.isfile(p) and os.path.getsize(p) > 100000:
            return p
        time.sleep(0.5)
    return p if os.path.isfile(p) else None


def panel_rect():
    return d0.win_rect(d0.COPY_TITLE)


def probe_click(title, x, y, why):
    """clickprobe (the delivery-proven path) + the delivery verdict.  Returns (delivered, j)."""
    j = d4.clickprobe(title, x, y, why)
    checks, ok = d4.delivered(j)
    log("  probe_click %s -> delivered=%s %s (NOTE: lv_gui presses at x+1 = %d)"
        % ((x, y), ok, checks, x + 1))
    return ok, j, checks


def locate_done(png, prect, tag):
    """Returns (centre, detail, crop_path).  Nothing is inherited: the search rect is the panel
    window measured now, and the winner is decided by pixels in THIS png."""
    rect = prect or (0, 0, 1920, 1080)
    best, why, cands = L.pick_by_template(png, rect)
    passing = [c for c in cands if "centre" in c]
    detail = ("search rect %s in %s; %d red clusters, %d passed shape, winner=%s | %s"
              % (rect, os.path.basename(png), len(cands), len(passing),
                 best and best["centre"], why))
    if best is None:
        for c in passing:
            log("    candidate %s box=%s caption=%s score=%s"
                % (c["centre"], c.get("button_box"), c["caption_size"], c.get("template_score")))
        return None, detail, None
    os.makedirs(EVID, exist_ok=True)
    crop = os.path.join(EVID, "%s_%s_done_button.png" % (STAMP, tag))
    try:
        L.save_crop(png, best["button_box"], crop)
    except Exception as e:                                                     # noqa: BLE001
        log("  save_crop failed: %r" % e)
        crop = None
    detail += ("; BOX=%s SIZE=%s CENTRE=%s (reference measured 2026-09-18 17:28: box=%s "
               "centre=%s; the point v4 INHERITED from the V6 copy and missed: %s, delta %s)"
               % (best["button_box"], best["button_size"], best["centre"], REF_DONE_BOX,
                  REF_DONE_CENTRE, V6_DONE_XY,
                  (best["centre"][0] - V6_DONE_XY[0], best["centre"][1] - V6_DONE_XY[1])))
    return best["centre"], detail, crop


def locate_bandpass_yes(png, brect):
    best, cands = L.locate_red_yes_button(png, brect, wmin=15, wmax=70, hmin=8, hmax=40)
    passing = [c for c in cands if "centre" in c]
    if len(passing) != 1:
        return None, ("%d red-captioned buttons passed inside %s (expected exactly 1): %s"
                      % (len(passing), brect, [c["centre"] for c in passing]))
    c = passing[0]
    return c["centre"], ("box=%s size=%s caption=%s red_px=%d"
                         % (c["button_box"], c["button_size"], c["caption_size"], c["red_px"]))


# =============================================================================================
# the stop - VI Server FIRST, then re-arm, then COM Abort.  Which one worked is the measurement.
# =============================================================================================
def stop_with_fallback(tag):
    """Returns (stopped, mechanism, latency_s, detail)."""
    t0 = time.time()
    d4.STOP_WAIT = STOP_WAIT
    idle, secs, trace = d4.stop_single_write(tag)
    FACTS["stop_trace_%s" % tag] = trace
    if idle:
        return True, "VI SERVER SetControlValue, ONE write each, no re-arm", secs, \
               "idle after %.1fs; %s" % (secs, " | ".join(trace[-3:]))
    idle2, secs2, rearms = d4.stop_rearmed(tag)
    if idle2:
        return True, "VI SERVER SetControlValue, RE-ARMED", time.time() - t0, \
               ("single write did not idle it in %.0fs; %d re-arms idled it after %.0fs"
                % (secs, rearms, secs2))
    shot("v5_stopfail_%s" % tag)
    ta = time.time()
    try:
        d0.com.call("abort", timeout=20.0)
        time.sleep(3.0)
        st = state()
        if st in (0, 1):
            return True, "COM Abort (VI SERVER DID NOT STOP IT)", time.time() - t0, \
                   ("single write %.0fs + %d re-arms %.0fs both failed; Abort idled it in %.1fs "
                    "(ExecState=%s)" % (secs, rearms, secs2, time.time() - ta, st))
        return False, "NOTHING STOPPED IT (Abort included)", time.time() - t0, \
               "ExecState=%s after Abort; frame=%r" % (st, getv(I_FRAME))
    except Exception as e:                                                     # noqa: BLE001
        return False, "COM Abort RAISED", time.time() - t0, repr(e)


# =============================================================================================
# one leg
# =============================================================================================
def leg(tag, n, base_path, cal_wait):
    ok = True
    resets = {}
    for ctl in (C_STOP, C_STOP2, C_DONE):
        try:
            d0.com.call("set", ctl, False, timeout=10.0)
            resets[ctl] = getv(ctl)
        except Exception as e:                                                 # noqa: BLE001
            resets[ctl] = "ERR %s" % e
    rec("%d %s.pre reset+readback of the 3 control-flow booleans" % (n, tag), "VISERVER", True,
        "%r (no panel PARAMETER is written)" % resets)

    # ---- L1 run ---------------------------------------------------------------------------------
    rt = d0.RunThread(COPY, "v5_%s" % tag)
    rt.start()
    t0 = time.time()
    left = False
    while time.time() - t0 < RUN_SETTLE:
        time.sleep(2.0)
        if state() not in (1, -1):
            left = True
            break
    rec("%d %s.L1 VI left idle" % (n + 1, tag), "COM", left,
        "ExecState=%s after %.0fs; Run returned=%s" % (state(), time.time() - t0,
                                                       rt.returned is not None))
    ok &= left
    if not left:
        capture("v5_%s_run_fail" % tag)
        return ok

    # ---- L2 LOCATE the image display -------------------------------------------------------------
    d0.focus(d0.COPY_TITLE)
    time.sleep(1.5)
    prect = panel_rect()
    before_png = capture("v5_%s_before_picks" % tag)
    img, iwhy = (None, "no capture") if not before_png else \
        L.locate_image_display(before_png, prect or (0, 0, 1920, 1080))
    rec("%d %s.L2 IMAQ display LOCATED in this leg's own capture" % (n + 2, tag), "GUI", bool(img),
        "panel rect=%s; %s; (v3's V6 rect, NOT used: %s)" % (prect, iwhy, V6_IMAGE_RECT))
    ok &= bool(img)
    if not img:
        return ok
    LOC["image_%s" % tag] = img

    # ---- L3 the 3 picks, at fractions of the LOCATED rect, verified by the markers ---------------
    m_before = L.count_red_markers(before_png, img)
    picks, delivered_all = [], True
    for i, (fx, fy) in enumerate(PICK_FRACS):
        px = int(img[0] + fx * (img[2] - img[0]))
        py = int(img[1] + fy * (img[3] - img[1]))
        picks.append((px, py))
        okd, _j, _c = probe_click(d0.COPY_TITLE, px, py,
                                  "bead %d (%s) at fraction %s of the LOCATED display rect %s"
                                  % (i + 1, "reference" if i == 0 else "magnetic", (fx, fy), img))
        delivered_all &= okd
        time.sleep(PICK_SETTLE)
    after_png = capture("v5_%s_after_picks" % tag)
    m_after = L.count_red_markers(after_png, img) if after_png else []
    grew = len(m_after) - len(m_before)
    l3 = grew >= 3
    rec("%d %s.L3 3 picks landed - CONFIRMED BY THE MARKERS THE VI DREW" % (n + 3, tag), "GUI", l3,
        "picks=%s in located rect %s; red markers inside it %d -> %d (delta %d, contract >= 3); "
        "all clicks delivered=%s; marker boxes after=%s"
        % (picks, img, len(m_before), len(m_after), grew, delivered_all,
           [m[0] for m in m_after][:6]))
    ok &= l3
    FACTS["picks_%s" % tag] = {"points": picks, "markers_before": len(m_before),
                               "markers_after": len(m_after)}

    # ---- L4 LOCATE the done button ----------------------------------------------------------------
    prect = panel_rect()
    done_png = capture("v5_%s_before_done" % tag)
    centre, dwhy, crop = (None, "no capture", None) if not done_png else \
        locate_done(done_png, prect, tag)
    rec("%d %s.L4 `Done Picking \\nBeads?` Yes button LOCATED on THIS VI's own panel"
        % (n + 4, tag), "GUI", bool(centre), "%s; evidence crop=%s" % (dwhy, crop))
    ok &= bool(centre)
    if not centre:
        return ok
    LOC["done_%s" % tag] = {"centre": centre, "crop": crop, "why": dwhy}

    # ---- L5 the click -----------------------------------------------------------------------------
    cnt_before = getv(C_COUNT)
    okd, j, checks = probe_click(d0.COPY_TITLE, centre[0], centre[1],
                                 "`Done Picking \\nBeads?` (uid 11819) Yes, LOCATED at %s" % (centre,))
    capture("v5_%s_after_done" % tag)
    rec("%d %s.L5 done click DELIVERED (clickprobe, never -Action click)" % (n + 5, tag), "GUI",
        okd, "%s; target hwnd=%s; pressed at %s" % (checks, (j or {}).get("target", {}).get("hwnd"),
                                                    (centre[0] + 1, centre[1])))
    ok &= okd

    # ---- L6 brief step 5: the 30 s gate -----------------------------------------------------------
    t0 = time.time()
    bp30 = False
    while time.time() - t0 < BANDPASS_GATE_S:
        if d0.win_present(BANDPASS_TITLE) or d0.win_present(SAVE_TITLE):
            bp30 = True
            break
        time.sleep(1.5)
    rec("%d %s.L6 `choose bandpass` within 30 s (brief step 5)" % (n + 6, tag), "GUI", bp30,
        "present=%s after %.0fs; the V6 copy needed ~2 min of z-stack calibration first "
        "(drive_original_copy_v2.py:147), so a FAIL here is a TIMING statement, not a verdict on "
        "the click - L7 is the verdict" % (bp30, time.time() - t0))

    # ---- L7 the picking loop really ended ---------------------------------------------------------
    ended = bp30
    while not ended and (time.time() - t0) < cal_wait:
        time.sleep(2.0)
        if d0.win_present(BANDPASS_TITLE) or d0.win_present(SAVE_TITLE):
            ended = True
    rec("%d %s.L7 picking loop ended" % (n + 7, tag), "GUI", ended,
        "Count %r -> %r after %.0fs; bandpass present=%s; save present=%s"
        % (cnt_before, getv(C_COUNT), time.time() - t0, d0.win_present(BANDPASS_TITLE),
           d0.win_present(SAVE_TITLE)))
    ok &= ended
    if not ended:
        capture("v5_%s_done_fail" % tag)
        return ok

    # ---- L8 the three `choose bandpass` panels, each Yes LOCATED in its own capture ---------------
    answered, details, hwnds = 0, [], []
    stop_reason = "cap"
    while answered < BP_CAP:
        t1 = time.time()
        seen = False
        while time.time() - t1 < BANDPASS_WAIT:
            if d0.win_present(SAVE_TITLE):
                stop_reason = "save dialog appeared after %d panel(s)" % answered
                break
            if d0.win_present(BANDPASS_TITLE):
                seen = True
                break
            time.sleep(1.5)
        if not seen:
            if stop_reason == "cap":
                stop_reason = "no `%s` window within %.0fs (after %d)" % (BANDPASS_TITLE,
                                                                         BANDPASS_WAIT, answered)
            break
        time.sleep(3.0)
        brect = d0.win_rect(BANDPASS_TITLE)
        png = capture("v5_%s_bandpass%d" % (tag, answered + 1))
        yes, ywhy = (None, "no capture") if not png else locate_bandpass_yes(png, brect)
        if yes is None:
            stop_reason = "panel %d: Yes button NOT located (%s)" % (answered + 1, ywhy)
            details.append(stop_reason)
            break
        good, hwnd, note = d4.gated_click_hwnd(BANDPASS_TITLE, yes[0], yes[1],
                                               "bandpass Yes #%d LOCATED at %s" % (answered + 1, yes))
        details.append("panel %d: rect=%s LOCATED yes=%s (%s) hwnd_died=%s | %s"
                       % (answered + 1, brect, yes, ywhy, good, note))
        if not good:
            capture("v5_%s_bandpass_stuck_%d" % (tag, answered + 1))
            stop_reason = "panel %d did not close" % (answered + 1)
            break
        answered += 1
        hwnds.append(hwnd)
        time.sleep(1.0)
    l8 = d0.win_present(SAVE_TITLE) and answered == 3
    FACTS["bandpass_%s" % tag] = {"answered": answered, "hwnds": hwnds, "terminal": stop_reason}
    rec("%d %s.L8 the three `choose bandpass` panels (Yes LOCATED, HWND-gated)" % (n + 8, tag),
        "GUI", l8, "%d closed (contract 3), hwnds %s; terminal=%s || %s"
        % (answered, hwnds, stop_reason, " || ".join(details)))
    ok &= l8
    if not d0.win_present(SAVE_TITLE):
        return ok

    # ---- L9 the save dialog (keyboard only - no coordinate exists to inherit) ---------------------
    saved, sdetail = d0.answer_save_dialog("v5_%s" % tag, base_path)
    rec("%d %s.L9 save dialog answered by keyboard" % (n + 9, tag), "GUI", saved, sdetail)
    ok &= saved

    # ---- L10 the cal file --------------------------------------------------------------------------
    time.sleep(3.0)
    calf = base_path if os.path.isfile(base_path) else None
    if calf is None and os.path.isdir(RUN_DIR):
        for f in os.listdir(RUN_DIR):
            if f.lower().startswith(os.path.basename(base_path).lower()):
                calf = os.path.join(RUN_DIR, f)
                break
    l10 = bool(calf) and os.path.getsize(calf) > 0
    rec("%d %s.L10 cal file in OUR folder" % (n + 10, tag), "FILE", l10,
        "%s (%s B); `Cal File Path` indicator=%r"
        % (calf, os.path.getsize(calf) if calf else "-", getv(I_CALPATH)))
    ok &= l10

    # ---- L11 the experiment loop ------------------------------------------------------------------
    vals = []
    t0 = time.time()
    while time.time() - t0 < RUN_S:
        time.sleep(2.0)
        vals.append(getv(I_FRAME))
    num = [v for v in vals if isinstance(v, (int, float))]
    l11 = len(num) >= 2 and num[-1] > num[0]
    FACTS["frames_%s" % tag] = vals
    rec("%d %s.L11 frame counter advances (it read 0 all run in v4)" % (n + 11, tag), "VISERVER",
        l11, "%s over %.0fs: %r .. %r (lost=%r)"
        % (I_FRAME, RUN_S, vals[0] if vals else None, vals[-1] if vals else None,
           getv(d0.I_LOST)))
    ok &= l11

    # ---- L12 the stop ------------------------------------------------------------------------------
    stopped, mech, lat, sdet = stop_with_fallback(tag)
    FACTS["stop_%s" % tag] = {"mechanism": mech, "latency_s": round(lat, 1), "detail": sdet}
    rec("%d %s.L12 stop - VI Server FIRST, COM Abort as the fallback" % (n + 12, tag), "VISERVER",
        stopped, "WORKED: %s after %.1fs -- %s" % (mech, lat, sdet))
    ok &= stopped

    # ---- L13 the trace file -------------------------------------------------------------------------
    time.sleep(5.0)
    _n, _tot, by, other = d0.listdir_stats(RUN_DIR)
    trace = [o for o in other if "tra" in o.lower()]
    l13 = bool(trace)
    FACTS["files_%s" % tag] = other
    rec("%d %s.L13 trace file written" % (n + 13, tag), "FILE", l13,
        "non-TIFF files: %s; by ext: %s; `Track File Path` indicator=%r"
        % (other or "(none)", by, getv(I_TRACKPATH)))
    ok &= l13
    return ok


# =============================================================================================
def main():
    ok = True
    os.makedirs(RUN_DIR, exist_ok=True)
    os.makedirs(SHOTS, exist_ok=True)
    os.makedirs(EVID, exist_ok=True)

    FACTS["handles_before"] = labview_handles()
    log("LabVIEW handles BEFORE %s" % FACTS["handles_before"])
    log("reference patch: %s (exists=%s)" % (L.REF_DONE, os.path.isfile(L.REF_DONE)))

    rc0, txt0 = d4.motor_gate("cycle27-plan Pre-decided 4: running the copy executes the "
                              "original's device init, which drives the PI stage and the ASI")
    p0 = d4.parse_motor(txt0)
    FACTS["motor_start"] = {"rc": rc0, "parsed": p0}
    g0 = (rc0 == 0)
    rec("0 G0 motor gate --session start (BEFORE LabVIEW opens COM3/COM4)", "MOTOR", g0,
        "exit=%d; %s; %s; %s" % (rc0, (p0.get("limits_lines") or ["(no LIMITS)"])[-1],
                                 (p0.get("refstate_lines") or ["(no REFSTATE)"])[-1],
                                 (p0.get("session_lines") or ["(no SESSION)"])[-1]))
    if not g0:
        rec("0a RUN REFUSED", "MOTOR", False,
            "the gate did not verify the controller limits, so the VI is NOT started")
        return False

    before = d0.md5(ORIGINAL)
    FACTS["md5_original_before"] = before
    rec("1 G1 md5(ORIGINAL) before", "FILE", before == ORIGINAL_MD5, before)
    ok &= before == ORIGINAL_MD5

    exists = os.path.isfile(COPY)
    cbefore = d0.md5(COPY) if exists else None
    FACTS["md5_copy_before"] = cbefore
    rec("2 G2 the D0 copy exists (nothing copied, saved or deleted)", "FILE", exists,
        "%s (%s B) md5=%s" % (COPY, os.path.getsize(COPY) if exists else "-", cbefore))
    ok &= exists
    if not exists:
        return ok

    try:
        rec("3 G3a apartment2 attach", "COM", True, d0.com.call("app", timeout=240))
        try:
            rec("4 G3b ORIGINAL resident READ-ONLY", "COM", True,
                d0.com.call("preload", ORIGINAL, timeout=300))
        except Exception as e:                                                 # noqa: BLE001
            rec("4 G3b ORIGINAL resident READ-ONLY", "COM", False, repr(e))
        d0.com.call("open", COPY, timeout=300)
        d0.com.call("panel", False, timeout=180)
        st, dl = state(), d0.dialogs()
        g3 = (st == 1) and ("VERDICT: BLOCKED" not in dl)
        rec("5 G3c copy loads, idle, unblocked", "COM", g3,
            "ExecState=%s; %s" % (st, dl.splitlines()[-1] if dl else "?"))
        ok &= g3
        FACTS["handles_after_open"] = labview_handles()
        if not g3:
            capture("v5_g3_fail")
            return ok

        nread, nerr, _ = d4.record_panel("before")
        g4 = nread >= 55
        rec("6 G4 panel parameters RECORDED (never set)", "VISERVER", g4,
            "%d of 60 controls returned a value, %d errors" % (nread, nerr))
        ok &= g4

        pr = panel_rect()
        FACTS["panel_rect"] = pr
        rec("7 G5 panel window rect read LIVE (recorded; NO click is derived from it)", "GUI",
            bool(pr), "rect=%s; v3's V6 rect %s is printed for contrast only - v4's gate 7 "
                      "compared these two and passed while the control positions differed"
            % (pr, d4.V6_PANEL_RECT))
        ok &= bool(pr)

        ok &= leg("run1", 10, os.path.join(RUN_DIR, "cal001"), CAL_WAIT_1)

        el = time.time() - d0._t0
        st = state()
        if st in (0, 1) and el < RUN2_BUDGET_S:
            ok &= leg("run2", 30, os.path.join(RUN_DIR, "cal002"), CAL_WAIT_2)
        else:
            rec("30 run2 RESTART LEG", "COM", False,
                "NOT started: ExecState=%s, elapsed %.0fs (budget %.0fs)" % (st, el, RUN2_BUDGET_S))
            ok = False
        return ok
    finally:
        cleanup()
        report()


_once = set()


def labview_running():
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "(Get-Process LabVIEW -ErrorAction SilentlyContinue | "
                        "Measure-Object).Count"], capture_output=True, text=True)
    try:
        return int((r.stdout or "0").strip() or 0) > 0
    except ValueError:
        return True


def cleanup():
    if "cleanup" in _once:
        return
    _once.add("cleanup")
    try:
        if state() not in (0, 1, -1):
            stopped, mech, lat, det = stop_with_fallback("cleanup")
            log("cleanup: stop -> %s (%s, %.1fs) %s" % (stopped, mech, lat, det))
            FACTS["cleanup_stop"] = {"stopped": stopped, "mechanism": mech, "latency_s": lat}
    except Exception as e:                                                     # noqa: BLE001
        log("cleanup: stop path raised %r" % e)

    try:
        d4.record_panel("after")
    except Exception as e:                                                     # noqa: BLE001
        log("cleanup: panel record after raised %r" % e)
    for ctl in (C_STOP, C_STOP2, C_DONE):
        try:
            d0.com.call("set", ctl, False, timeout=6.0)
        except Exception:                                                      # noqa: BLE001
            pass
    FACTS["handles_after"] = labview_handles()
    log("LabVIEW handles AFTER %s (before %s)" % (FACTS["handles_after"],
                                                  FACTS.get("handles_before")))
    try:
        d0.com.call("closepanel", timeout=30.0)
    except Exception as e:                                                     # noqa: BLE001
        log("cleanup: CloseFrontPanel raised %s" % e)
    try:
        d0.com.call("release", timeout=10.0)
    except Exception:                                                          # noqa: BLE001
        pass

    n, tot, by, other = d0.listdir_stats(RUN_DIR)
    FACTS["run_dir"] = {"path": RUN_DIR, "files": n, "bytes": tot, "by_ext": by, "non_tiff": other}
    dn, db = d0.delete_tiffs(RUN_DIR)
    FACTS["tiffs_deleted"] = {"count": dn, "bytes": db}
    log("cleanup: run folder %d files / %d bytes; TIFFs deleted %d / %d bytes" % (n, tot, dn, db))

    cafter = d0.md5(COPY) if os.path.isfile(COPY) else None
    FACTS["md5_copy_after"] = cafter
    rec("90 G90 md5(COPY) unchanged - RUN, never saved, never deleted", "FILE",
        cafter is not None and cafter == FACTS.get("md5_copy_before"),
        "%s -> %s (exists=%s)" % (FACTS.get("md5_copy_before"), cafter, os.path.isfile(COPY)))
    after = d0.md5(ORIGINAL)
    FACTS["md5_original_after"] = after
    rec("91 G91 md5(ORIGINAL) after", "FILE", after == ORIGINAL_MD5, after)

    # --- G92: LabVIEW must be GONE before the motor port is touched (v4's G25 was a port-busy
    #     false failure: the VI still owned COM3/COM4).  Standing restart permission covers the
    #     forced kill if it will not exit on its own.
    t0 = time.time()
    while labview_running() and (time.time() - t0) < EXIT_WAIT_S:
        time.sleep(5.0)
    killed = False
    if labview_running():
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"],
                       capture_output=True)
        killed = True
        time.sleep(10.0)
    gone = not labview_running()
    rec("92 G92 LabVIEW exited before the motor port is touched", "PROC", gone,
        "waited %.0fs; forced kill used=%s; running now=%s" % (time.time() - t0, killed,
                                                               not gone))

    rc1, txt1 = d4.motor_gate("post-run TMX? re-read, AFTER LabVIEW released COM3/COM4")
    tmx, line = d4.tmx_from(txt1)
    p1 = d4.parse_motor(txt1)
    FACTS["motor_after"] = {"rc": rc1, "tmx": tmx, "parsed": p1}
    rec("93 G93 post-run TMX? still 39", "MOTOR", tmx == 39.0,
        "TMX?=%r from %r; gate exit=%d; %s; %s"
        % (tmx, line, rc1, (p1.get("limits_lines") or ["(no LIMITS)"])[-1],
           (p1.get("refstate_lines") or ["(no REFSTATE)"])[-1]))

    FACTS["gui_actions"] = d0.GUI_ACTIONS[0]
    FACTS["located"] = LOC
    with open(PROBE_JSON, "w", encoding="utf-8") as f:
        json.dump(d4.RECORDS, f, indent=1, default=str)
    log("click records -> %s" % PROBE_JSON)


def report():
    if "report" in _once:
        return
    _once.add("report")
    steps = d0.STEPS
    npass = sum(1 for s in steps if s["ok"])
    print("\n| step | method | result | detail |", flush=True)
    print("|---|---|---|---|", flush=True)
    for s in steps:
        print("| %s | %s | %s | %s |"
              % (s["step"], s["method"], "PASS" if s["ok"] else "FAIL",
                 s["detail"].replace("|", "/").replace("\n", " ")), flush=True)
    print("\nLOCATED: %s" % json.dumps(LOC, default=str, indent=1), flush=True)
    print("\nFACTS: %s" % json.dumps(FACTS, default=str, indent=1)[:12000], flush=True)
    with open(D0_JSON, "w", encoding="utf-8") as f:
        json.dump({"stamp": STAMP, "run_id": RUN_ID, "copy": COPY, "original": ORIGINAL,
                   "run_dir": RUN_DIR, "steps": steps, "facts": FACTS, "located": LOC},
                  f, indent=1, default=str)
    print("json: %s" % D0_JSON, flush=True)
    print("\n=== D0 v5: %d pass, %d fail ===" % (npass, len(steps) - npass), flush=True)
    print("FAILING: %s" % ", ".join(s["step"] for s in steps if not s["ok"]), flush=True)


if __name__ == "__main__":
    good = False
    try:
        good = main()
    except Exception as e:                                                      # noqa: BLE001
        import traceback
        traceback.print_exc()
        rec("!! v5 exception", "COM", False, repr(e))
        try:
            cleanup()
        except Exception:                                                       # noqa: BLE001
            pass
        report()
    sys.exit(0 if good else 1)
