r"""diag_d0_pickloop_liveness.py - IS THE BEAD-PICKING LOOP ITERATING AT ALL?

THE QUESTION (cycle-31 dispatch, after tools/bench/drive_original_copy_v4.log 2026-09-18 17:25)
  v4's done click did not end the picking loop; `Count` stuck at 1, `current image number` stuck at
  0, both stop Booleans written True were never consumed, ExecState stayed 2 for 303 s. Competing
  explanations: (A) the click missed the button, (B) the loop is not iterating at all because it is
  starved of camera frames, so NO front-panel control is ever read. This file separates them by
  measuring the loop's LIVENESS *before* any click is made.

WHAT IS REUSED, WHAT IS NEW (rule: check what exists before building)
  REUSED BY IMPORT, not re-implemented (`import drive_original_copy_v4 as v4`, which itself imports
  drive_original_copy_v2 as d0 and retargets it to the 4.5 copy):
    - the SECOND COM apartment `d0.com` (PollCom) and the NEVER-JOINED `d0.RunThread`
    - `d0.getv / state / rec / log / shot / gui / win_present / win_rect / dialogs / inside / md5 /
       focus / listdir_stats`
    - v4's HWND-TOKEN click gate `v4.clickprobe` + `v4.delivered` (tools/bench/
      drive_original_copy_v4.py:259-316), i.e. the delivery-proving path, NOT `-Action click`
    - v4's retarget of every path (`d0.ORIGINAL`, `d0.COPY`, `d0.COPY_TITLE`) and its
      `v4.derive_geometry()` / `v4.motor_gate()` / `v4.tmx_from()` / `v4.record_panel` machinery
    - `bench_prep.labview_handles` for the handle count
  NEW here, and only this: the five liveness measurements L1-L5, the indicator shortlist built
  MECHANICALLY from tools/bench/d0_inventory.json (no retyped label bytes), and the deliberate
  OMISSION of the three bead picks - this run clicks the done button and nothing else, so `Count`
  staying 0 is itself a reading.

SEARCHED FIRST (docs/toolkit-capabilities.md, `ls tools/recipes tools/bench`, `grep "^def "
tools/gscript.py`): no existing tool polls a running VI's indicators for liveness; the closest are
d0.snapshot() (5 fixed labels, no timing) and tools/bench/diag_d0_inventory.py (static, VI not
running). So L1/L2/L4 are new; every mechanism they stand on is imported.

SAFETY
  - The ORIGINAL `Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi` is preloaded READ-ONLY and
    its md5 is taken BEFORE and AFTER (rule 1). Neither VI is ever saved; the copy is never
    deleted; its md5 is taken before and after too.
  - NO panel PARAMETER is written (rule 1a). The only writes are the control-flow Booleans
    `stop (end)`, `stop (end) 2`, `Done Picking \nBeads?` set FALSE before the run, plus the
    cleanup COM Abort - the VI-Server stop is ALREADY MEASURED as not consumed, so it is not
    retried here.
  - Rig state is 조립/ASSEMBLED. Running the copy executes the original's device init, which drives
    the PI stage and the ASI, so the run is wrapped in `py tools/motor_gate.py --session start` and
    REFUSES to proceed on a non-zero exit. `--session end` is never called; the post-run read is a
    second `--session start` whose sender prints `before: ... TMX?=..` before writing anything.
  - ONE GUI click in the whole run (L3), through clickprobe, `-Exception Approved -Evidence "user
    2026-09-17 bead-pick option 1"`.

============================== PREDICTION CONTRACT ==============================
 G0  motor gate `--session start` exits 0. Non-zero ABORTS before LabVIEW is touched.
 G1  md5(ORIGINAL) == c39f36e0675339673b707c59f0784fee BEFORE.
 G2  the copy exists; md5 recorded BEFORE; nothing is copied.
 G3  apartment2 attaches, the ORIGINAL is resident read-only, the copy opens ExecState == 1, no
     BLOCKING dialog.
 G4  geometry: the panel window is found by title; its rect is printed with the delta against v3's
     V6 rect and with the brief's literal done point (1114,915) marked inside/outside.
 G5  the VI leaves idle within RUN_SETTLE after Run(False) on its own never-joined apartment.
 L1  BEFORE any click: `current image number` (uid 34200) polled every 2 s for 30 s.
     PREDICTION: if the acquisition is live the sequence STRICTLY INCREASES (PASS); if it is
     starved every reading is 0 (FAIL). Either outcome is a result; the gate records which.
 L2  in the same window, every indicator whose label names a frame/rate/error/IMAQ/camera/time
     signal (selected by regex from d0_inventory.json) is read twice, 20 s apart.
     PREDICTION: at least 12 of them return a value (not `ERR:`); any that CHANGES between the two
     reads proves some loop in the VI is iterating.
 L3  ONE clickprobe on `Done Picking \nBeads?` uid 11819 at the brief's literal (1114,915).
     PREDICTION: the record's four delivery checks (setforegroundwindow / fg_after_sfw_is_target /
     fg_at_buttondown_is_target / wfp_press_root_is_target) are ALL true => the click WAS delivered
     to the panel window at that point. PASS = all four true.
 L4  AFTER that click: `current image number` and `Count` (uid 28051) polled every 2 s for 30 s,
     and `choose bandpass` / `Save cal cluster file` window presence checked each time.
     PREDICTION (ours, the one under test): if the loop is frame-starved, both stay flat and no
     window appears.
 L5  ExecState is read and recorded at EVERY stage (after open, after run, after L1, after L3,
     after L4, after abort).
 G6  cleanup: COM Abort returns the VI to ExecState 0/1.
 G7  md5(COPY) AFTER == BEFORE and the copy still exists.
 G8  md5(ORIGINAL) AFTER == c39f36e0675339673b707c59f0784fee.
 G9  post-run motor read: `TMX?` still 39 (may FAIL with 'access denied' while LabVIEW still owns
     COM3/COM4 - that exact outcome was measured in v4 and is reported verbatim, not re-diagnosed).

    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_d0_pickloop_liveness.log \
        -- py -u tools/bench/diag_d0_pickloop_liveness.py
=================================================================================
"""
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "tools"))
sys.path.insert(0, HERE)

import drive_original_copy_v4 as v4                                             # noqa: E402
import drive_original_copy_v2 as d0                                             # noqa: E402
from bench_prep import labview_handles                                          # noqa: E402

rec, log, getv, state, shot = d0.rec, d0.log, d0.getv, d0.state, d0.shot
FACTS = d0.FACTS

ORIGINAL = v4.ORIGINAL
ORIGINAL_MD5 = v4.ORIGINAL_MD5
COPY = v4.COPY
INVENTORY_JSON = v4.INVENTORY_JSON

C_STOP, C_STOP2, C_DONE, C_COUNT = d0.C_STOP, d0.C_STOP2, d0.C_DONE, d0.C_COUNT
I_FRAME = d0.I_FRAME
BANDPASS_TITLE, SAVE_TITLE = d0.BANDPASS_TITLE, d0.SAVE_TITLE

STAMP = time.strftime("%Y%m%d_%H%M%S")
SHOTS = os.path.join(HERE, "d0_shots_liveness")
OUT_JSON = os.path.join(HERE, "diag_d0_pickloop_liveness.json")
d0.SHOTS = SHOTS
d0.STAMP = STAMP

DONE_LITERAL = (1114, 915)          # the brief's literal point - the one v4 clicked
RUN_SETTLE = 60.0
L1_S = 30.0
L4_S = 30.0
POLL_S = 2.0
IND_TIMEOUT = 4.0
IND_CAP = 24

STAGES = []                          # L5: (tag, ExecState, seconds)
LIVE = {}


def stage(tag):
    st = state()
    STAGES.append({"stage": tag, "ExecState": st, "t": round(time.time() - d0._t0, 1)})
    log("  L5 ExecState @%-22s = %s" % (tag, st))
    return st


# =============================================================================================
# L2 - the indicator shortlist, built MECHANICALLY from the read-only inventory (no retyped bytes)
# =============================================================================================
IND_RE = re.compile(r"frame|fps|rate|\bhz\b|error|imaq|cam|session|image|lost|missing|"
                    r"progress|time|visa|width|height|file", re.I)


def indicator_shortlist():
    try:
        with open(INVENTORY_JSON, encoding="utf-8") as f:
            inv = json.load(f)
    except Exception as e:                                                      # noqa: BLE001
        log("  indicator_shortlist: %s unreadable (%r)" % (INVENTORY_JSON, e))
        return []
    rows = inv.get("panel_rows") or []
    labs = [r["label"] for r in rows
            if r.get("indicator") is True and r.get("label") and IND_RE.search(r["label"])]
    # `current image number` first, then inventory order; de-duplicated; capped.
    out = [I_FRAME] + [l for l in labs if l != I_FRAME]
    seen, ded = set(), []
    for l in out:
        if l not in seen:
            seen.add(l)
            ded.append(l)
    return ded[:IND_CAP]


def read_indicators(labels, tag):
    vals = {}
    for lab in labels:
        vals[lab] = getv(lab, timeout=IND_TIMEOUT)
    log("  L2[%s] read %d indicators" % (tag, len(vals)))
    for lab in labels:
        log("    IND %-34r = %r" % (lab, vals[lab]))
    return vals


def poll_frame(seconds, tag, also_count=False):
    """Poll `current image number` (and optionally `Count`) every POLL_S s. Returns the list of
    (t, frame[, count]) tuples and the window-presence readings."""
    seq, wins = [], []
    t0 = time.time()
    while time.time() - t0 < seconds:
        f = getv(I_FRAME)
        row = {"t": round(time.time() - t0, 1), "frame": f}
        if also_count:
            row["count"] = getv(C_COUNT)
            # ONE `-Action windows` call per iteration, both titles parsed out of it (two separate
            # win_present() calls would double the powershell cost inside a 30 s budget).
            wtxt = d0.windows().lower()
            row["bandpass"] = BANDPASS_TITLE.lower() in wtxt
            row["save"] = SAVE_TITLE.lower() in wtxt
            wins.append((row["bandpass"], row["save"]))
        seq.append(row)
        log("    %s t=%4.1fs %s" % (tag, row["t"], {k: v for k, v in row.items() if k != "t"}))
        time.sleep(POLL_S)
    return seq, wins


def numeric(seq, key="frame"):
    return [r[key] for r in seq if isinstance(r.get(key), (int, float))
            and not isinstance(r.get(key), bool)]


# =============================================================================================
def main():
    ok = True
    os.makedirs(SHOTS, exist_ok=True)
    FACTS["handles_before"] = labview_handles()
    log("LabVIEW handles BEFORE %s (None/0 = not running yet)" % FACTS["handles_before"])

    # ---- G0 the motor gate, BEFORE LabVIEW is touched -------------------------------------------
    rc0, txt0 = v4.motor_gate("rig 조립: running the copy executes the original's device init, "
                              "which drives the PI stage and the ASI")
    p0 = v4.parse_motor(txt0)
    g0 = (rc0 == 0)
    rec("0 G0 motor gate --session start", "MOTOR", g0,
        "exit=%d; %s; %s" % (rc0, (p0.get("limits_lines") or ["(no LIMITS line)"])[-1],
                             (p0.get("refstate_lines") or ["(no REFSTATE line)"])[-1]))
    if not g0:
        rec("0a RUN REFUSED", "MOTOR", False, "the gate did not verify the controller limits, so "
                                              "the VI is NOT started")
        return False

    # ---- G1/G2 the two files ---------------------------------------------------------------------
    before = d0.md5(ORIGINAL)
    FACTS["md5_original_before"] = before
    rec("1 G1 md5(ORIGINAL) before", "FILE", before == ORIGINAL_MD5, before)
    ok &= before == ORIGINAL_MD5

    exists = os.path.isfile(COPY)
    cbefore = d0.md5(COPY) if exists else None
    FACTS["md5_copy_before"] = cbefore
    rec("2 G2 the D0 copy exists (nothing copied, saved or deleted)", "FILE", exists,
        "%s md5=%s" % (COPY, cbefore))
    ok &= exists
    if not exists:
        return ok

    try:
        # ---- G3 attach / preload / open -----------------------------------------------------------
        rec("3 G3a apartment2 attach", "COM", True, d0.com.call("app", timeout=240))
        try:
            rec("4 G3b ORIGINAL resident READ-ONLY", "COM", True,
                d0.com.call("preload", ORIGINAL, timeout=300))
        except Exception as e:                                                  # noqa: BLE001
            rec("4 G3b ORIGINAL resident READ-ONLY", "COM", False, repr(e))
        d0.com.call("open", COPY, timeout=300)
        d0.com.call("panel", False, timeout=180)
        st, dl = stage("after open"), d0.dialogs()
        g3 = (st == 1) and ("VERDICT: BLOCKED" not in dl)
        rec("5 G3c copy loads, idle, unblocked", "COM", g3,
            "ExecState=%s; %s" % (st, dl.splitlines()[-1] if dl else "?"))
        ok &= g3
        FACTS["handles_after_open"] = labview_handles()
        if not g3:
            shot("liveness_g3_fail")
            return ok

        # ---- G4 geometry (measured, NOT used to move the click) ------------------------------------
        gclose, gdetail = v4.derive_geometry()
        prect = v4.GEO.get("panel_rect")
        lit_inside = d0.inside(prect, DONE_LITERAL, margin=5)
        FACTS["geometry"] = dict(v4.GEO)
        FACTS["done_literal"] = DONE_LITERAL
        FACTS["done_literal_inside_panel"] = lit_inside
        rec("6 G4 panel geometry measured", "GUI", bool(prect),
            "%s || the brief's literal done point %s is %s the live panel rect; v4's DERIVED done "
            "point would be %s (recorded, NOT clicked - this run reproduces v4's literal click)"
            % (gdetail, DONE_LITERAL, "INSIDE" if lit_inside else "OUTSIDE", v4.GEO.get("done_xy")))

        # ---- the three control-flow Booleans to False (no PARAMETER is written) ---------------------
        resets = {}
        for ctl in (C_STOP, C_STOP2, C_DONE):
            try:
                d0.com.call("set", ctl, False, timeout=10.0)
                resets[ctl] = getv(ctl)
            except Exception as e:                                              # noqa: BLE001
                resets[ctl] = "ERR %s" % e
        rec("7 pre reset+readback of the 3 control-flow booleans", "VISERVER", True,
            "%r (no panel PARAMETER is written - rule 1a)" % resets)

        # ---- G5 run --------------------------------------------------------------------------------
        rt = d0.RunThread(COPY, "liveness")
        rt.start()
        t0 = time.time()
        left = False
        while time.time() - t0 < RUN_SETTLE:
            time.sleep(2.0)
            if state() not in (1, -1):
                left = True
                break
        stage("after Run")
        rec("8 G5 VI left idle after Run(False)", "COM", left,
            "ExecState=%s after %.0fs; Run returned=%s"
            % (state(), time.time() - t0, rt.returned is not None))
        ok &= left
        if not left:
            shot("liveness_run_fail")
            return ok
        d0.focus(d0.COPY_TITLE)
        time.sleep(1.0)
        shot("liveness_before_click")

        # ---- L1 the frame counter BEFORE any click --------------------------------------------------
        seq1, _ = poll_frame(L1_S, "L1")
        LIVE["L1"] = seq1
        n1 = numeric(seq1)
        l1_rising = len(n1) >= 2 and n1[-1] > n1[0]
        l1_allzero = bool(n1) and all(v == 0 for v in n1)
        stage("after L1")
        rec("9 L1 `current image number` BEFORE any click", "VISERVER", l1_rising,
            "%d readings over %.0fs: %r ; strictly-increasing=%s ; all-zero=%s (PASS means the "
            "acquisition is live; FAIL with all-zero means it is starved)"
            % (len(seq1), L1_S, [r["frame"] for r in seq1], l1_rising, l1_allzero))
        FACTS["L1_all_zero"] = l1_allzero
        FACTS["L1_rising"] = l1_rising

        # ---- L2 the indicator sweep, twice ---------------------------------------------------------
        labs = indicator_shortlist()
        FACTS["L2_labels"] = labs
        v_a = read_indicators(labs, "A")
        time.sleep(20.0)
        v_b = read_indicators(labs, "B")
        errs = [l for l in labs if isinstance(v_a.get(l), str) and str(v_a[l]).startswith("ERR:")]
        changed = [l for l in labs if repr(v_a.get(l)) != repr(v_b.get(l))]
        LIVE["L2_A"], LIVE["L2_B"] = v_a, v_b
        FACTS["L2_changed"] = changed
        stage("after L2")
        rec("10 L2 indicator sweep (frame/rate/error/IMAQ/camera/time), read twice 20 s apart",
            "VISERVER", (len(labs) - len(errs)) >= 12,
            "%d indicators selected by regex from the inventory, %d returned a value, %d ERR; "
            "CHANGED between the two reads: %s"
            % (len(labs), len(labs) - len(errs), len(errs), changed or "(none)"))

        # ---- L3 ONE clickprobe on the done button ---------------------------------------------------
        cnt_before, frame_before = getv(C_COUNT), getv(I_FRAME)
        prect_now = d0.win_rect(d0.COPY_TITLE)          # re-measured immediately before the click
        if not d0.inside(prect_now, DONE_LITERAL, margin=5):
            # Safety, same guard v4 applies at R4: a point outside the live panel rect would land in
            # whatever window is underneath it. Not clicked; the stage is recorded as a FAIL.
            j, checks, deliv = None, {}, False
            l3_note = ("NOT CLICKED: the literal point %s is OUTSIDE the panel rect measured "
                       "immediately before the click, %s" % (DONE_LITERAL, prect_now))
        else:
            j = v4.clickprobe(d0.COPY_TITLE, DONE_LITERAL[0], DONE_LITERAL[1],
                              "`Done Picking \\nBeads?` uid 11819 at the brief's literal point")
            checks, deliv = v4.delivered(j)
            l3_note = "clicked; panel rect at click time %s" % (prect_now,)
        FACTS["L3_checks"] = checks
        FACTS["L3_record"] = j
        stage("after L3")
        rec("11 L3 ONE clickprobe on `Done Picking \\nBeads?` (1114,915)", "GUI", deliv,
            "%s || delivery checks=%s -> delivered=%s ; target hwnd=%s alive_after_500ms=%s ; "
            "Count %r -> %r"
            % (l3_note, checks, deliv, (j or {}).get("target", {}).get("hwnd"),
               (j or {}).get("after_500ms", {}).get("alive"), cnt_before, getv(C_COUNT)))
        shot("liveness_after_click")

        # ---- L4 frame + Count AFTER the click -------------------------------------------------------
        seq4, wins = poll_frame(L4_S, "L4", also_count=True)
        LIVE["L4"] = seq4
        n4 = numeric(seq4)
        c4 = numeric(seq4, "count")
        bandpass_seen = any(w[0] for w in wins) or d0.win_present(BANDPASS_TITLE)
        save_seen = any(w[1] for w in wins) or d0.win_present(SAVE_TITLE)
        l4_moved = (len(n4) >= 2 and n4[-1] > n4[0]) or (len(c4) >= 2 and c4[-1] != c4[0]) \
            or bandpass_seen or save_seen
        stage("after L4")
        rec("12 L4 `current image number` + `Count` AFTER the click", "VISERVER", l4_moved,
            "frames=%r counts=%r ; `choose bandpass` window appeared=%s ; save dialog appeared=%s ; "
            "frame %r -> %r ; Count %r -> %r"
            % ([r["frame"] for r in seq4], [r.get("count") for r in seq4], bandpass_seen, save_seen,
               frame_before, seq4[-1]["frame"] if seq4 else None, cnt_before,
               seq4[-1].get("count") if seq4 else None))
        FACTS["L4_bandpass_seen"] = bandpass_seen
        FACTS["L4_save_seen"] = save_seen
        return ok
    finally:
        cleanup()
        report()


_once = set()


def cleanup():
    if "cleanup" in _once:
        return
    _once.add("cleanup")
    aborted = None
    try:
        if state() not in (0, 1, -1):
            try:
                d0.com.call("abort", timeout=20.0)
                time.sleep(3.0)
                aborted = "COM Abort issued; ExecState after = %s" % state()
            except Exception as e:                                              # noqa: BLE001
                aborted = "COM Abort raised %s" % e
            log("cleanup: %s" % aborted)
    except Exception as e:                                                      # noqa: BLE001
        log("cleanup: abort path raised %r" % e)
    FACTS["cleanup_abort"] = aborted
    st = stage("after abort")
    rec("90 G6 COM Abort returns the VI to idle", "COM", st in (0, 1),
        "%s ; ExecState=%s (the VI-Server stop is ALREADY MEASURED as not consumed - v4 - so it is "
        "not retried here)" % (aborted, st))

    for ctl in (C_STOP, C_STOP2, C_DONE):
        try:
            d0.com.call("set", ctl, False, timeout=6.0)
        except Exception:                                                       # noqa: BLE001
            pass
    try:
        d0.com.call("closepanel", timeout=30.0)
    except Exception as e:                                                      # noqa: BLE001
        log("cleanup: CloseFrontPanel raised %s" % e)
    try:
        d0.com.call("release", timeout=10.0)
    except Exception:                                                           # noqa: BLE001
        pass

    cafter = d0.md5(COPY) if os.path.isfile(COPY) else None
    FACTS["md5_copy_after"] = cafter
    rec("91 G7 md5(COPY) unchanged - run, never saved, never deleted", "FILE",
        cafter is not None and cafter == FACTS.get("md5_copy_before"),
        "%s -> %s (exists=%s)" % (FACTS.get("md5_copy_before"), cafter, os.path.isfile(COPY)))

    after = d0.md5(ORIGINAL)
    FACTS["md5_original_after"] = after
    rec("92 G8 md5(ORIGINAL) after", "FILE", after == ORIGINAL_MD5, after)

    FACTS["handles_after"] = labview_handles()
    log("LabVIEW handles AFTER %s (before %s)" % (FACTS["handles_after"],
                                                  FACTS.get("handles_before")))

    rc1, txt1 = v4.motor_gate("post-run TMX? re-read (the 39 mm ceiling is RAM-only)")
    tmx, line = v4.tmx_from(txt1)
    FACTS["motor_after"] = {"rc": rc1, "tmx": tmx, "line": line}
    rec("93 G9 post-run TMX? still 39", "MOTOR", tmx == 39.0,
        "TMX?=%r from %r; gate exit=%d" % (tmx, line, rc1))


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
    print("\nL5 ExecState BY STAGE: %s" % json.dumps(STAGES), flush=True)
    print("\nL1 SEQUENCE: %s" % json.dumps(LIVE.get("L1", []), default=str), flush=True)
    print("\nL4 SEQUENCE: %s" % json.dumps(LIVE.get("L4", []), default=str), flush=True)
    print("\nL2 A: %s" % json.dumps(LIVE.get("L2_A", {}), default=str), flush=True)
    print("\nL2 B: %s" % json.dumps(LIVE.get("L2_B", {}), default=str), flush=True)
    print("\nFACTS: %s" % json.dumps(FACTS, default=str, indent=1)[:12000], flush=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"stamp": STAMP, "copy": COPY, "original": ORIGINAL, "steps": steps,
                   "stages": STAGES, "live": LIVE, "facts": FACTS}, f, indent=1, default=str)
    print("json: %s" % OUT_JSON, flush=True)
    print("\n=== D0 pickloop liveness: %d pass, %d fail ===" % (npass, len(steps) - npass),
          flush=True)
    print("FAILING: %s" % ", ".join(s["step"] for s in steps if not s["ok"]), flush=True)


if __name__ == "__main__":
    good = False
    try:
        good = main()
    except Exception as e:                                                      # noqa: BLE001
        import traceback
        traceback.print_exc()
        rec("!! liveness exception", "COM", False, repr(e))
        try:
            cleanup()
        except Exception:                                                       # noqa: BLE001
            pass
        report()
    sys.exit(0 if good else 1)
