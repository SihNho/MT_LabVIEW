"""drive_original_copy_v3.py - D0 v3: the full unattended cycle, with a TOKEN-GATED click.

v3 changes exactly ONE mechanism against v2 (tools/bench/drive_original_copy_v2.py): every click
that must be DELIVERED to a subVI panel now goes through `lv_gui.ps1 -Action clickprobe`, which
performs the same click and returns the Windows input state around it as one JSON line. The
harness then reads that record instead of believing the tool's echo. Everything else - the second
COM apartment, the never-joined RunThread, the picks, the save dialog, the TIFF accounting - is
IMPORTED from v2 unchanged.

WHY (measured, not assumed): D0 v2's P6 failed identically twice; codex refuted the "event
structure not ready" explanation and pointed out that `-Action click` reports success when its
FUNCTION RETURNS - `mouse_event` has no return value, `Focus` discards SetForegroundWindow's, and
Windows can eat an activating click (MA_ACTIVATEANDEAT).
  archive/peer/2026-09-17-d0-bandpass-click-not-delivered.md
  tools/bench/d0_clickprobe.py + .log - the discriminating experiment this file is built on.

NOT A BLIND RETRY LOOP (codex's item 4, refused explicitly): the bandpass panel reuses the same
title, rect and Yes coordinate for every bead, so a late click plus a scheduled retry could accept
bead 1 and land on bead 2. A second attempt is issued ONLY when the previous attempt's own JSON
record PROVES the click was not delivered (SetForegroundWindow false, foreground not the target at
button-down, or WindowFromPoint's root not the target) AND the same panel is still present with an
unchanged rect. If the record says the click WAS correctly targeted and the panel still did not
close, the harness STOPS - that is the H2 case and it is reported, not guessed at.

WHAT ALREADY EXISTS (checked first): drive_original_copy_v2.py (reused wholesale by import),
d0_clickprobe.py (the probe helper pattern), tools/lv_gui.ps1 (clickprobe), gscript (not used -
nothing is scripted or saved here).

PREDICTION CONTRACT
 R1  copy loads: ExecState == 1, no blocking modal.
 R2  Run(False) on its own never-joined apartment takes the VI out of idle.
 R3  3 bead picks land in the Image display (uid 31543, rect 232,500-873,1013).
 R4  `Done Picking Beads?` ends the picking loop.
 R5  EXACTLY 3 `choose bandpass` panels, each CLOSED by a token-gated click; `answered` counts a
     panel only when it closed (the v2 counting bug codex found, fixed in v2 in the same session).
 R6  the `Save cal cluster file` dialog takes an ABSOLUTE path under tools/bench/d0_out/<run-id>/.
 R7  the cal file exists there with size > 0.
 R8  the frame loop runs: `current image number` strictly increases over RUN_S = 20 s.
 R9  STOP: SetControlValue('stop (end)'/'stop (end) 2', True) re-armed every 2 s. Measured two
     ways - the frame counter FREEZING (the loop ended) and ExecState returning to 0/1. Which
     mechanism actually stopped it is reported either way. NOTE: no screen coordinate for
     `stop (end)` has ever been measured (the control sits outside the panel window's visible area
     at 1920x1080 - see tools/bench/d0_shots_v2/20260917_021053_run1_after_picks.png), so the GUI
     fallback is unavailable and the recorded fallback is COM Abort, as in v2.
 R10 `save N xyz traces.vi` (#6384, diagram 19, AFTER the loop) writes a trace file into the run
     folder - its `base path/filename` and `cal cluster path` come off the frame loop's tunnels
     (docs/main-vi-stop-and-save.md), i.e. from the path we typed, so no second dialog is expected.
 R11 RESTART: a second Run takes the VI out of idle again and survives 15 s; it is then stopped by
     the same ladder and the panel closed.
 R12 every TIFF is counted and DELETED, the scratch copy is deleted in the same run, and
     md5(original) == 2a78e17c449cacdaf5da389818526859 before AND after.

    MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/drive_original_copy_v3.log \
        -- py -u tools/bench/drive_original_copy_v3.py
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, "tools"))

import drive_original_copy_v2 as d0                                            # noqa: E402

d0.D0_JSON = os.path.join(HERE, "drive_original_copy_v3.json")
PROBE_JSON = os.path.join(HERE, "drive_original_copy_v3_clickrecords.json")

rec, log, getv, state, shot = d0.rec, d0.log, d0.getv, d0.state, d0.shot
RECORDS = []

RUN_S = 20.0            # frame-loop window; the TIFF writer is unconditional at ~118 MB/s
RESTART_S = 15.0        # brief: restart, 15 s, stop, close
STOP_WAIT = 60.0
FREEZE_N = 3            # consecutive unchanged frame-counter samples == the loop ended


# ---------------------------------------------------------------------------------------------
# the token-gated click
# ---------------------------------------------------------------------------------------------
def clickprobe(title, x, y, why):
    d0.GUI_ACTIONS[0] += 1
    log("  CLICKPROBE '%s' (%d,%d) <- %s" % (title, x, y, why))
    out = d0.gui("-Action", "clickprobe", "-Title", "'%s'" % title,
                 "-X", str(int(x)), "-Y", str(int(y)),
                 "-Exception", "Approved", "-Evidence", "'%s'" % d0.EVIDENCE, timeout=90)
    obj = None
    for line in (out or "").splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                obj = json.loads(line)
                break
            except Exception as e:                                             # noqa: BLE001
                log("  clickprobe: JSON parse failed: %s" % e)
    RECORDS.append({"why": why, "title": title, "xy": [x, y], "json": obj,
                    "raw": None if obj else out})
    return obj


def delivered(j):
    """The four discriminators, read from the record. True == the click was correctly targeted."""
    if not j:
        return {}, False
    c = {"sfw_ret": bool(j.get("setforegroundwindow", {}).get("ret")),
         "fg_after_sfw_is_target": bool(j.get("fg_after_sfw_is_target")),
         "fg_at_buttondown_is_target": bool(j.get("fg_at_buttondown_is_target")),
         "wfp_press_root_is_target": bool(j.get("wfp_press_xy", {}).get("root_is_target"))}
    return c, all(c.values())


def gated_click_hwnd(title, x, y, why, max_attempts=2):
    """Click the window currently titled `title` at (x,y) and require THAT HWND to die.

    THE TOKEN IS THE HWND, NOT THE TITLE. Measured 2026-09-17 by tools/bench/d0_clickprobe.py:
    the v2 click WAS delivered - `after_500ms.alive` was FALSE, i.e. the target hwnd 19728546 was
    destroyed within 500 ms - and a DIFFERENT hwnd (19794082) with the IDENTICAL title
    "choose bandpass v2.vi" took its place. v2's progress test `win_present(BANDPASS_TITLE)` is
    title-based, so it read the successor panel as "the same panel did not close" and declared the
    click lost. The click was never the problem; the predicate was.

    A second attempt is issued ONLY if the record proves the click was NOT delivered (a failing
    foreground/point check) AND the same hwnd is still alive. Never a blind retry.
    Returns (ok, hwnd_clicked, detail)."""
    notes = []
    for attempt in range(1, max_attempts + 1):
        r = d0.win_rect(title)
        if not d0.inside(r, (x, y)):
            notes.append("attempt %d: rect %s does not contain %s - NO click" % (attempt, r, (x, y)))
            return False, None, "; ".join(notes)
        j = clickprobe(title, x, y, "%s (attempt %d)" % (why, attempt))
        c, targeted = delivered(j)
        if not j:
            notes.append("attempt %d: clickprobe returned no JSON" % attempt)
            return False, None, "; ".join(notes)
        hwnd = j.get("target", {}).get("hwnd")
        dead = (j.get("after_500ms", {}).get("alive") is False)
        succ = j.get("fg_after_click", {}) or {}
        notes.append("attempt %d hwnd=%s rect=%s checks=%s target_hwnd_dead_within_500ms=%s "
                     "successor_hwnd=%s" % (attempt, hwnd, r, c, dead, succ.get("hwnd")))
        if dead:
            return True, hwnd, "; ".join(notes)
        if targeted:
            notes.append("STOP: record says the click WAS correctly targeted yet hwnd %s is still "
                         "alive - that is the deferral case; NOT retrying blind" % hwnd)
            return False, hwnd, "; ".join(notes)
        notes.append("record proves NOT delivered (%s) -> one more attempt on the same hwnd"
                     % [k for k, v in c.items() if not v])
    return False, None, "; ".join(notes)


# ---------------------------------------------------------------------------------------------
def frame_series(seconds, every=2.0):
    vals = []
    t0 = time.time()
    while time.time() - t0 < seconds:
        time.sleep(every)
        vals.append(getv(d0.I_FRAME))
    return vals


def stop_measured(tag):
    """R9. SetControlValue first, re-armed; measured by BOTH the frame counter freezing and
    ExecState. Returns (stopped, mechanism, detail)."""
    t0 = time.time()
    rearms = 0
    frozen = 0
    last = getv(d0.I_FRAME)
    first_freeze_t = None
    while time.time() - t0 < STOP_WAIT:
        for ctl in (d0.C_STOP, d0.C_STOP2):
            try:
                d0.com.call("set", ctl, True, timeout=10.0)
            except Exception as e:                                             # noqa: BLE001
                log("  stop[%s]: set(%r) raised %s" % (tag, ctl, e))
        rearms += 1
        time.sleep(2.0)
        cur = getv(d0.I_FRAME)
        if isinstance(cur, (int, float)) and isinstance(last, (int, float)) and cur == last:
            frozen += 1
            if frozen == FREEZE_N and first_freeze_t is None:
                first_freeze_t = time.time() - t0
        else:
            frozen = 0
        last = cur
        st = state()
        if st in (0, 1):
            return True, "SetControlValue", ("idle after %.0fs, %d re-arms; frame counter froze at "
                                             "%s (last=%r)" % (time.time() - t0, rearms,
                                                               first_freeze_t, cur))
        if frozen >= FREEZE_N and time.time() - t0 > 20:
            return True, "SetControlValue (loop ended, VI still finishing)", \
                   ("frame counter unchanged %d samples (=%r) after %.0fs, %d re-arms; ExecState=%s"
                    % (frozen, cur, time.time() - t0, rearms, st))
    shot("v3_stopfail_%s" % tag)
    detail = ("SetControlValue re-armed %d times over %.0fs did NOT stop it (frame counter still "
              "%r, ExecState=%s). GUI fallback UNAVAILABLE: no screen coordinate for `stop (end)` "
              "has ever been measured - the control is outside the panel window's visible area."
              % (rearms, STOP_WAIT, last, state()))
    log("  stop[%s]: %s" % (tag, detail))
    try:
        d0.com.call("abort", timeout=20.0)
    except Exception as e:                                                     # noqa: BLE001
        log("  stop[%s]: Abort raised %s" % (tag, e))
    time.sleep(3.0)
    if state() in (0, 1):
        return False, "COM Abort", detail
    return False, "NOTHING STOPPED IT", detail


# ---------------------------------------------------------------------------------------------
def main():
    ok = True
    os.makedirs(d0.RUN_DIR, exist_ok=True)
    os.makedirs(d0.SHOTS, exist_ok=True)

    before = d0.md5(d0.ORIGINAL)
    d0.FACTS["md5_before"] = before
    rec("0 md5(original) before", "FILE", before == d0.ORIGINAL_MD5, before)
    ok &= before == d0.ORIGINAL_MD5
    shutil.copy2(d0.ORIGINAL, d0.COPY)
    rec("0b plain file copy", "FILE", os.path.exists(d0.COPY),
        "%s -> run folder %s" % (d0.COPY, d0.RUN_DIR))

    base_path = os.path.join(d0.RUN_DIR, "cal001")
    try:
        rec("1 apartment2 attach", "COM", True, d0.com.call("app", timeout=240))
        try:
            rec("1b original resident (read-only)", "COM", True,
                d0.com.call("preload", d0.ORIGINAL, timeout=300))
        except Exception as e:                                                 # noqa: BLE001
            rec("1b original resident (read-only)", "COM", False, repr(e))
        d0.com.call("open", d0.COPY, timeout=300)
        d0.com.call("panel", False, timeout=180)
        st, dl = state(), d0.dialogs()
        r1 = (st == 1) and ("VERDICT: BLOCKED" not in dl)
        rec("2 R1 copy loads, idle", "COM", r1,
            "ExecState=%s; %s" % (st, dl.splitlines()[-1] if dl else "?"))
        ok &= r1
        if not r1:
            shot("v3_r1_fail")
            return ok

        # ---- R2 run ----------------------------------------------------------------------------
        d0.reset_controls()
        rt = d0.RunThread(d0.COPY, "v3run1")
        rt.start()
        t0 = time.time()
        left = False
        while time.time() - t0 < d0.RUN_SETTLE:
            time.sleep(2.0)
            if state() not in (1, -1):
                left = True
                break
        rec("3 R2 VI left idle", "COM", left,
            "ExecState=%s after %.0fs; Run returned=%s (Run over ActiveX behaves as Wait Until "
            "Done=TRUE - measured twice in v2)" % (state(), time.time() - t0, rt.returned is not None))
        ok &= left
        if not left:
            shot("v3_run_fail")
            return ok

        # ---- R3 picks --------------------------------------------------------------------------
        r_main = d0.win_rect(d0.COPY_TITLE)
        d0.FACTS["main_panel_rect"] = r_main
        d0.focus(d0.COPY_TITLE)
        time.sleep(1.2)
        shot("v3_before_picks")
        for i, (x, y) in enumerate(d0.PICKS):
            d0.click(x, y, "bead %d in Image display %s" % (i + 1, d0.IMAGE_RECT))
            time.sleep(d0.PICK_SETTLE)
        shot("v3_after_picks")
        rec("4 R3 3 bead picks", "GUI", r_main is not None,
            "panel rect=%s; %s inside %s" % (r_main, d0.PICKS, d0.IMAGE_RECT))

        # ---- R4 done picking -------------------------------------------------------------------
        cnt_before = getv(d0.C_COUNT)
        d0.click(d0.DONE_XY[0], d0.DONE_XY[1], "`Done Picking Beads?` Yes button")
        ended = False
        t0 = time.time()
        while time.time() - t0 < d0.CAL_WAIT:
            time.sleep(2.0)
            if d0.win_present(d0.BANDPASS_TITLE):
                ended = True
                break
            c = getv(d0.C_COUNT)
            if isinstance(c, (int, float)) and isinstance(cnt_before, (int, float)) and c != cnt_before:
                ended = True
        rec("5 R4 picking loop ended", "GUI", ended,
            "Count %r -> %r after %.0fs; bandpass present=%s"
            % (cnt_before, getv(d0.C_COUNT), time.time() - t0, d0.win_present(d0.BANDPASS_TITLE)))
        ok &= ended

        # ---- R5 the bandpass panels, HWND-gated ---------------------------------------------------
        # The COUNT is not assumed to be 3. The probe measured that answering one panel opens a
        # SUCCESSOR panel with the same title (same bead # on screen, now carrying the filtered
        # image), so "one Yes per bead" is a guess the machine has not confirmed. The loop is
        # driven by the machine instead: keep answering distinct HWNDs until the save dialog
        # appears or no bandpass window is left, bounded by BP_CAP.
        BP_CAP = 12
        answered, details, hwnds = 0, [], []
        stop_reason = "cap"
        while answered < BP_CAP:
            t0 = time.time()
            budget = d0.CAL_WAIT if answered == 0 else d0.BANDPASS_WAIT
            seen = False
            while time.time() - t0 < budget:
                if d0.win_present(d0.SAVE_TITLE):
                    stop_reason = "save dialog appeared after %d panel(s)" % answered
                    break
                if d0.win_present(d0.BANDPASS_TITLE):
                    seen = True
                    break
                time.sleep(1.5)
            if not seen:
                if stop_reason == "cap":
                    stop_reason = ("no `%s` window within %.0fs (after %d)"
                                   % (d0.BANDPASS_TITLE, budget, answered))
                break
            time.sleep(3.0)          # let the panel settle; codex: "too early" must be excluded
            cnt_pre = getv(d0.C_COUNT)
            good, hwnd, note = gated_click_hwnd(
                d0.BANDPASS_TITLE, d0.BANDPASS_YES[0], d0.BANDPASS_YES[1],
                "bandpass Yes #%d" % (answered + 1))
            # gemini's falsification handle (archive/peer/2026-09-17-d0-bandpass-hwnd-token-agy.md):
            # HWND death proves ONE CALL of the subVI ended, NOT that a bead was accepted. The main
            # VI's own `Count` is the only bead-level progress signal an external harness can read,
            # so it is recorded around every click instead of being inferred from the window count.
            cnt_post = getv(d0.C_COUNT)
            details.append("panel %d: hwnd_died=%s Count %r->%r | %s"
                           % (answered + 1, good, cnt_pre, cnt_post, note))
            if not good:
                shot("v3_bandpass_stuck_%d" % (answered + 1))
                stop_reason = "panel %d did not close" % (answered + 1)
                break
            answered += 1
            hwnds.append(hwnd)
            time.sleep(1.0)
        # The TERMINAL STATE is the save dialog, never the click cap (gemini: "Detect the terminal
        # state explicitly ... never on an arbitrary click cap"). BP_CAP is a safety bound only; if
        # it is what ended the loop, R5 FAILS even when `answered` reached len(PICKS).
        r5 = d0.win_present(d0.SAVE_TITLE)
        d0.FACTS["bandpass_answered"] = answered
        d0.FACTS["bandpass_hwnds"] = hwnds
        rec("6 R5 bandpass panels (HWND-gated)", "GUI", r5,
            "%d panel(s) closed, distinct hwnds %s; stop: %s || %s"
            % (answered, hwnds, stop_reason, " || ".join(details)))
        ok &= r5
        if not r5:
            return ok

        # ---- R6 save dialog ----------------------------------------------------------------------
        saved, sdetail = d0.answer_save_dialog("v3", base_path)
        rec("7 R6 save dialog answered", "GUI", saved, sdetail)
        ok &= saved

        # ---- R7 cal file -------------------------------------------------------------------------
        time.sleep(3.0)
        calf = base_path if os.path.isfile(base_path) else None
        if calf is None and os.path.isdir(d0.RUN_DIR):
            for f in os.listdir(d0.RUN_DIR):
                if f.lower().startswith(os.path.basename(base_path).lower()):
                    calf = os.path.join(d0.RUN_DIR, f)
                    break
        r7 = bool(calf) and os.path.getsize(calf) > 0
        rec("8 R7 cal file in OUR folder", "FILE", r7,
            "%s (%s B); Cal File Path indicator=%r"
            % (calf, os.path.getsize(calf) if calf else "-", getv(d0.I_CALPATH)))
        ok &= r7

        # ---- R8 the frame loop --------------------------------------------------------------------
        vals = frame_series(RUN_S)
        num = [v for v in vals if isinstance(v, (int, float))]
        r8 = len(num) >= 2 and num[-1] > num[0]
        rec("9 R8 frame counter advances", "VISERVER", r8,
            "%s over %.0fs: %r .. %r (lost=%r)"
            % (d0.I_FRAME, RUN_S, vals[0] if vals else None, vals[-1] if vals else None,
               getv(d0.I_LOST)))
        ok &= r8

        # ---- R9 stop ------------------------------------------------------------------------------
        stopped, mech, sdet = stop_measured("run1")
        d0.FACTS["stop_mechanism_run1"] = "%s | %s" % (mech, sdet)
        rec("10 R9 stop via the VI's own control", "VISERVER", stopped, "%s -- %s" % (mech, sdet))
        ok &= stopped

        # ---- R10 the trace file --------------------------------------------------------------------
        time.sleep(5.0)
        n, tot, by, other = listdir_now()
        trace = [o for o in other if "tra" in o.lower()]
        r10 = bool(trace)
        d0.FACTS["non_tiff_files_run1"] = other
        d0.FACTS["by_ext_run1"] = by
        rec("11 R10 trace file written", "FILE", r10,
            "non-TIFF files: %s; by ext: %s" % (other or "(none)", by))
        ok &= r10

        # ---- R11 restart ---------------------------------------------------------------------------
        st = state()
        if st in (0, 1):
            rt2 = d0.RunThread(d0.COPY, "v3run2")
            rt2.start()
            t0 = time.time()
            left2 = False
            while time.time() - t0 < d0.RUN_SETTLE:
                time.sleep(2.0)
                if state() not in (1, -1):
                    left2 = True
                    break
            if left2:
                time.sleep(RESTART_S)
            st2, mech2, det2 = stop_measured("run2")
            d0.FACTS["stop_mechanism_run2"] = "%s | %s" % (mech2, det2)
            rec("12 R11 restart + %.0fs + stop" % RESTART_S, "COM", left2,
                "restart left idle=%s; stopped=%s by %s -- %s" % (left2, st2, mech2, det2))
            ok &= left2
        else:
            rec("12 R11 restart + %.0fs + stop" % RESTART_S, "COM", False,
                "NOT started: ExecState=%s after run 1's stop" % st)
            ok = False
        return ok
    finally:
        with open(PROBE_JSON, "w", encoding="utf-8") as f:
            json.dump(RECORDS, f, indent=1, default=str)
        log("click records -> %s" % PROBE_JSON)
        d0.cleanup()
        after = d0.md5(d0.ORIGINAL)
        d0.FACTS["md5_after"] = after
        rec("Z md5(original) after", "FILE", after == d0.ORIGINAL_MD5, after)
        d0.report()


def listdir_now():
    return d0.listdir_stats(d0.RUN_DIR)


if __name__ == "__main__":
    good = False
    try:
        good = main()
    except Exception as e:                                                     # noqa: BLE001
        import traceback
        traceback.print_exc()
        rec("!! v3 exception", "COM", False, repr(e))
        try:
            d0.cleanup()
        except Exception:                                                      # noqa: BLE001
            pass
        d0.report()
    sys.exit(0 if good else 1)
