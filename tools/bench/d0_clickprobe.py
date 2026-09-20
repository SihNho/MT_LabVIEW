"""d0_clickprobe.py - THE DISCRIMINATING EXPERIMENT for "the bandpass Yes click is not delivered".

Cycle 15, D0 v3 session. This is a READER, not another attempt at the thing that failed
(CLAUDE.md "When a diagnosis is GUESSED twice, build the reader"). D0 v2's P6 failed identically
twice - one click at the measured (175,353) on `choose bandpass v2.vi`'s Yes button left the panel
unchanged two minutes later - and codex refuted the "event structure not ready" explanation:
  archive/peer/2026-09-17-d0-bandpass-click-not-delivered.md
Its finding: `lv_gui -Action click` prints success when its FUNCTION RETURNS, not when a control
receives the message. So the project has no evidence channel for "the click landed". This run opens
one.

WHAT ALREADY EXISTS (checked before writing - CLAUDE.md "before creating any new op, tool, recipe"):
  * tools/bench/drive_original_copy_v2.py - the WHOLE drive-to-the-panel path (load, second COM
    apartment, RunThread, picks, Done Picking). REUSED BY IMPORT here; not one line is re-derived.
    Its `bandpass_round` counting bug (codex's item 4) is fixed in that file in the same session.
  * tools/lv_gui.ps1 - gets ONE new action, `clickprobe`, authorised by the judgement session:
    a single click IDENTICAL to `click`, with SetForegroundWindow's return, GetForegroundWindow
    before/after, WindowFromPoint at the click and the real press point, GUITHREADINFO of the
    target's thread before/after, and the target's title/rect 500 ms later - one JSON line.
    It passes the SAME GUI gate as `click` (-Exception + -Evidence) and is logged the same way.
  * tools/gscript.py - not used for anything here (no edit, no save; the VI is run, not scripted).

PREDICTION CONTRACT
  Q0  BASELINE. A clickprobe on the copy's own title bar (a click that certainly reaches a window)
      returns valid JSON with setforegroundwindow.ret=true and fg_after_sfw_is_target=true. This is
      the control: it says what a DELIVERED click looks like on this machine, this session.
  Q1  the v2 path still reaches the first `choose bandpass` panel (P1-P5 unchanged).
  Q2  after the panel has been up >= 10 s (codex's "rules out too early"), ONE clickprobe on
      (175,353) returns JSON. Exactly one click is issued. There is NO retry loop anywhere here.
  H1 (foreground / z-order race) is CONFIRMED if any of:
        setforegroundwindow.ret == false
        fg_after_sfw_is_target == false
        fg_at_buttondown_is_target == false
        wfp_press_xy.root_is_target == false
      => the click activated a window or was eaten (MA_ACTIVATEANDEAT); remedy = token-gated click.
  H2 (panel lock / deferral) is CONFIRMED if ALL of the above are correct and the panel is still
      present 30 s later - especially with a non-zero hwndCapture / hwndMenuOwner. Remedy is NOT
      guessed here: the JSON is reported and the judgement session decides.
  Q3  whatever the verdict, the VI is stopped and the copy deleted in the same run, and
      md5(original) == 2a78e17c449cacdaf5da389818526859 before AND after.

    MATERIAL=1 py tools/bgrun.py --max-min 15 --log tools/bench/d0_clickprobe.log \
        -- py -u tools/bench/d0_clickprobe.py
"""
import json
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, "tools"))

import drive_original_copy_v2 as d0                                            # noqa: E402

# keep v2's own report file untouched
d0.D0_JSON = os.path.join(HERE, "d0_clickprobe.json")
PROBE_JSON = os.path.join(HERE, "d0_clickprobe_records.json")

rec, log, getv, state, shot = d0.rec, d0.log, d0.getv, d0.state, d0.shot
RECORDS = []


def clickprobe(title, x, y, why):
    """ONE instrumented click. Returns (dict|None, raw_text)."""
    d0.GUI_ACTIONS[0] += 1
    log("  CLICKPROBE '%s' (%d,%d) <- %s" % (title, x, y, why))
    out = d0.gui("-Action", "clickprobe", "-Title", "'%s'" % title,
                 "-X", str(int(x)), "-Y", str(int(y)),
                 "-Exception", "Approved", "-Evidence", "'%s'" % d0.EVIDENCE,
                 timeout=90)
    obj = None
    for line in (out or "").splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                obj = json.loads(line)
                break
            except Exception as e:                                             # noqa: BLE001
                log("  clickprobe: JSON parse failed: %s" % e)
    RECORDS.append({"why": why, "title": title, "xy": [x, y], "raw": out, "json": obj})
    log("  CLICKPROBE raw -> %s" % out)
    return obj, out


def checks(j):
    """The four H1 discriminators, straight from the JSON."""
    if not j:
        return {}, False
    c = {
        "sfw_ret": bool(j.get("setforegroundwindow", {}).get("ret")),
        "fg_after_sfw_is_target": bool(j.get("fg_after_sfw_is_target")),
        "fg_at_buttondown_is_target": bool(j.get("fg_at_buttondown_is_target")),
        "wfp_press_root_is_target": bool(j.get("wfp_press_xy", {}).get("root_is_target")),
    }
    return c, all(c.values())


def main():
    ok = True
    os.makedirs(d0.RUN_DIR, exist_ok=True)
    os.makedirs(d0.SHOTS, exist_ok=True)

    before = d0.md5(d0.ORIGINAL)
    d0.FACTS["md5_before"] = before
    rec("0 md5(original) before", "FILE", before == d0.ORIGINAL_MD5, before)
    ok &= before == d0.ORIGINAL_MD5
    shutil.copy2(d0.ORIGINAL, d0.COPY)
    rec("0b plain file copy", "FILE", os.path.exists(d0.COPY), d0.COPY)

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
        p1 = (st == 1) and ("VERDICT: BLOCKED" not in dl)
        rec("2 Q1 copy loads, idle", "COM", p1,
            "ExecState=%s; %s" % (st, dl.splitlines()[-1] if dl else "?"))
        ok &= p1
        if not p1:
            shot("q1_fail")
            return ok

        # ---- Q0 BASELINE: what a click that certainly reaches a window looks like ---------------
        r_main = d0.win_rect(d0.COPY_TITLE)
        d0.FACTS["main_panel_rect"] = r_main
        if r_main:
            bx = (r_main[0] + r_main[2]) // 2
            by = r_main[1] + 12                      # the title bar: a no-op click
            j0, _ = clickprobe(d0.COPY_TITLE, bx, by, "BASELINE title-bar click on the copy's panel")
            c0, all0 = checks(j0)
            rec("3 Q0 baseline clickprobe", "GUI", bool(j0) and all0,
                "title bar (%d,%d) checks=%s" % (bx, by, c0))
            ok &= bool(j0)
        else:
            rec("3 Q0 baseline clickprobe", "GUI", False, "panel window not found by title")
            ok = False
            return ok

        # ---- run ---------------------------------------------------------------------------------
        d0.reset_controls()
        rt = d0.RunThread(d0.COPY, "probe")
        rt.start()
        t0 = time.time()
        left_idle = False
        while time.time() - t0 < d0.RUN_SETTLE:
            time.sleep(2.0)
            if state() not in (1, -1):
                left_idle = True
                break
        rec("4 VI left idle", "COM", left_idle,
            "ExecState=%s after %.0fs; Run returned=%s"
            % (state(), time.time() - t0, rt.returned is not None))
        ok &= left_idle
        if not left_idle:
            shot("run_fail")
            return ok

        # ---- picks -------------------------------------------------------------------------------
        d0.focus(d0.COPY_TITLE)
        time.sleep(1.2)
        shot("probe_before_picks")
        for i, (x, y) in enumerate(d0.PICKS):
            d0.click(x, y, "bead %d in Image display %s" % (i + 1, d0.IMAGE_RECT))
            time.sleep(d0.PICK_SETTLE)
        shot("probe_after_picks")
        rec("5 3 bead picks", "GUI", True, "%s inside %s" % (d0.PICKS, d0.IMAGE_RECT))

        # ---- done picking ------------------------------------------------------------------------
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
            if isinstance(c, (int, float)) and isinstance(cnt_before, (int, float)) \
                    and c != cnt_before:
                ended = True
        rec("6 picking loop ended / bandpass panel up", "GUI", ended,
            "Count %r -> %r; bandpass present=%s after %.0fs"
            % (cnt_before, getv(d0.C_COUNT), d0.win_present(d0.BANDPASS_TITLE), time.time() - t0))
        ok &= ended
        if not d0.win_present(d0.BANDPASS_TITLE):
            shot("no_bandpass")
            return False

        # ---- Q2: ONE instrumented click, after >= 10 s ---------------------------------------------
        t_up = time.time()
        time.sleep(12.0)                      # codex: >= 10 s rules out "the click was too early"
        r_bp = d0.win_rect(d0.BANDPASS_TITLE)
        xy = d0.BANDPASS_YES
        shot("bandpass_before_probe")
        if not d0.inside(r_bp, xy):
            rec("7 Q2 clickprobe", "GUI", False,
                "panel rect %s does NOT contain %s - NO click issued" % (r_bp, xy))
            return False
        j, raw = clickprobe(d0.BANDPASS_TITLE, xy[0], xy[1],
                            "the bandpass Yes button, %.0fs after the panel appeared"
                            % (time.time() - t_up))
        c, all_ok = checks(j)
        rec("7 Q2 clickprobe returned JSON", "GUI", bool(j), "checks=%s" % c)
        ok &= bool(j)

        # ---- did the panel close? (watch only - NO second click) -----------------------------------
        closed = False
        t0 = time.time()
        while time.time() - t0 < 30.0:
            time.sleep(1.5)
            if not d0.win_present(d0.BANDPASS_TITLE):
                closed = True
                break
        shot("bandpass_after_probe")
        gti = (j or {}).get("gti_after_click", {})
        capture = gti.get("hwndCapture", 0)
        menu = gti.get("hwndMenuOwner", 0)

        if j and not all_ok:
            verdict = "H1 CONFIRMED (foreground/z-order): failing checks %s" \
                      % [k for k, v in c.items() if not v]
        elif j and all_ok and not closed:
            verdict = ("H2 CONFIRMED (delivered but deferred/locked): all four checks correct, "
                       "panel still present 30 s later; hwndCapture=%s hwndMenuOwner=%s flags=%s"
                       % (capture, menu, gti.get("flags")))
        elif j and all_ok and closed:
            verdict = ("NEITHER as written: all four checks correct AND the panel CLOSED - the "
                       "instrumented (activate-verify-click) path works where the blind click did "
                       "not. Supports the H1 remedy (verify before clicking) without showing a "
                       "failing check at this attempt.")
        else:
            verdict = "INCONCLUSIVE: clickprobe returned no JSON (raw=%r)" % (raw or "")[:200]

        d0.FACTS["verdict"] = verdict
        d0.FACTS["checks"] = c
        d0.FACTS["panel_closed_after_probe"] = closed
        d0.FACTS["probe_json"] = j
        rec("8 VERDICT", "GUI", bool(j), verdict)
        log("VERDICT: %s" % verdict)
        log("PROBE JSON VERBATIM: %s" % json.dumps(j) if j else "PROBE JSON: none")
        return ok
    finally:
        with open(PROBE_JSON, "w", encoding="utf-8") as f:
            json.dump(RECORDS, f, indent=1, default=str)
        log("probe records -> %s" % PROBE_JSON)
        d0.cleanup()
        after = d0.md5(d0.ORIGINAL)
        d0.FACTS["md5_after"] = after
        rec("Z md5(original) after", "FILE", after == d0.ORIGINAL_MD5, after)
        d0.report()


if __name__ == "__main__":
    good = False
    try:
        good = main()
    except Exception as e:                                                     # noqa: BLE001
        import traceback
        traceback.print_exc()
        rec("!! probe exception", "COM", False, repr(e))
        try:
            d0.cleanup()
        except Exception:                                                      # noqa: BLE001
            pass
        d0.report()
    sys.exit(0 if good else 1)
