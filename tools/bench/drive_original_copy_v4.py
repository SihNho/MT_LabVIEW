r"""drive_original_copy_v4.py - D0 on the 4.5 COPY: the v3 driver RETARGETED, plus four deltas.

WHAT IS REUSED, WHAT IS NEW (the one line the brief asks for)
  REUSED, unchanged, by import: the whole v2 scaffold - the SECOND COM apartment (`PollCom`), the
  NEVER-JOINED `RunThread`, `rec/log/getv/state/shot/gui/click/keys/focus/win_rect/win_present/
  dialogs/inside/md5/listdir_stats/report`, and `answer_save_dialog` (the file-dialog handler);
  and from v3 the HWND-TOKEN click gate (`clickprobe` + `delivered` + `gated_click_hwnd`), copied
  here only because it must call this file's geometry.
  NEW: the 4.5 retarget (target VI, md5, no file copy at all), the read-only PANEL PARAMETER
  RECORD, the runtime-DERIVED screen geometry (the 4.5 panel's rect has never been measured), the
  explicit three-`choose bandpass` contract step, the VI-SERVER-ONLY single-write stop test, the
  `motor_gate.py --session start` wrapper + the post-run `TMX?` re-read, and a cleanup that NEVER
  deletes or saves the copy.

PRIOR ART (checked before writing a line - archive/peer/2026-09-18-priorart-d0-harness.md,
ACCEPTED IN FULL by the cycle-30 judgement session):
  B1  every clause of cycle27-plan Pre-decided 3 already ran 16/16 rc=0 on a PLAIN COPY, in
      tools/bench/drive_original_copy_v3.py + .log - so nothing here is built from scratch.
  B2  from-scratch variants ALREADY FAILED: one COM worker inside Run(False) (ActiveX Run behaves
      as Wait-Until-Done=TRUE), a TITLE-based panel predicate, and an unverified click. All three
      are avoided by inheriting v2/v3 rather than re-implementing them.
  B3  the helpers that exist: tools/lv_gui.ps1:32,:629-631,:732-733 (clickprobe, gated exactly like
      click), tools/bench/drive_original_copy_v2.py:205-215 and tools/bench/p2_open_copy.py:25-31
      (preload the original read-only, THEN open the copy).
  So this file adds ONLY the four deltas the review said the retarget needs.

THE TARGET (delta 1)
  ORIGINAL  G:\...\2. Tracking\Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi
            md5 c39f36e0675339673b707c59f0784fee - preloaded READ-ONLY, never opened for writing,
            never saved, md5 taken before AND after (rule 1).
  COPY      C:\Program Files\...\LabVIEW 2026\user.lib\claudeDev\Track_D0_copy_20260918.vi
            ALREADY EXISTS (the user ran it by hand in P2). This harness RUNS it and NOTHING else:
            it is never re-copied, never saved, never deleted, and its md5 is taken before AND
            after as the proof of that.
  The v3 target (the V6 working copy, md5 2a78e17c...) carried Claude's 2026-09-01 per-frame TIFF
  fixture; the 4.5 copy does NOT - uids 22700/23020/23175/22703 are ABSENT
  (tools/bench/diag_d0_trace_path.log:31-37). So no TIFF flood is expected; a sweep still runs.

DELTA 2 - PANEL PARAMETERS ARE RECORDED, NEVER SET
  The values saved in the copy are the ones the user last used. Writing one would be a computation
  change in disguise (rule 1a). So every front-panel CONTROL (60 of them, exact label bytes from
  tools/bench/d0_inventory.json) is READ and logged before the run and after it. The ONLY values
  this harness ever writes are the three control-flow booleans `stop (end)`, `stop (end) 2`,
  `Done Picking \nBeads?` - and those are latches, not parameters; writing the stops False while
  idle is step 1 of the peer's own discriminating test
  (archive/peer/2026-09-17-d0v3-stop-heuristic.md:32).

DELTA 3 - THE THREE `choose bandpass` PANELS ARE AN EXPLICIT CONTRACT STEP
  v3's step list omitted them and the harness stalled
  (archive/peer/2026-09-17-d0-bandpass-click-not-delivered.md;
  tools/bench/drive_original_copy_v3.py:11-13,:118-127). They sit BETWEEN the done button and the
  save dialog. Answering one opens a SUCCESSOR with the identical title, so the token is the HWND,
  never the title, and the TERMINAL state is the save dialog, never a click cap.

DELTA 4 - STOP IS VI-SERVER ONLY
  `stop (end)` uid 7 has NO screen coordinate and never has had one (the control sits outside the
  panel window's visible area at 1920x1080) - so it is NOT clicked, in either leg. The stop is the
  peer's discriminating test verbatim (archive/peer/2026-09-17-d0v3-stop-heuristic.md:32,:53-56):
  both stops False while idle with readback, then ONE `True` write each, no re-arm, no GUI, polling
  BOTH control values and `ExecState`. Only if that fails does the re-armed ladder run (still VI
  Server), and COM Abort is cleanup-only and always reported as such.
  It also fixes the v3 SCORING defect the same review found: v3's R11 was gated on `left2` (did the
  restart leave idle), never on the stop (drive_original_copy_v3.py:415-418). Here every leg's stop
  is its own gate.

DELTA 5 - THE MOTOR-GATE WRAPPER (cycle27-plan Pre-decided 4)
  Rig state is 조립/ASSEMBLED. Running the copy executes the original's device init, which drives
  the PI stage and the ASI. The run therefore BEGINS with `py tools/motor_gate.py --session start`
  and REFUSES to proceed unless it returns 0 with a verified readback. `--session end` is NEVER
  called: the controller limits stay on for unattended runs. After the run a second `--session
  start` is issued purely to READ the limits back - its sender prints `before: POS?=.. TMN?=..
  TMX?=.. ERR?=..` before it writes anything (tools/motor_send_pi.ps1:52), which is the post-run
  `TMX?` the brief asks for. There is no read-only PI mode in the gate.

THE GEOMETRY PROBLEM, STATED HONESTLY
  The 4.5 copy's panel has NEVER been measured on screen: `diag_d0_inventory` gate B1 FAILED - no
  traverse class returns a panel uid, so class/position are not reachable over our COM path
  (tools/bench/diag_d0_inventory.log:56). The only measured coordinates in the fleet are v3's, on
  the V6 copy, 2026-09-17. Both panels carry the SAME 114 objects with the SAME uids, so this file
  re-derives every click point as an OFFSET INSIDE the panel window rect measured at run time, from
  v3's rect and points. That is an inference, and it is NOT trusted: every click is gated on a
  machine-readable consequence instead (the `Count` control moving, a bandpass window appearing,
  the clicked HWND dying), and the derived rect/points are printed so a failure is diagnosable.

================================ PREDICTION CONTRACT ================================
 G0  motor gate: `--session start` exits 0, readback PI TMN=0 TMX=39 + FRF=1 with POS unchanged.
     A non-zero exit ABORTS the whole run before LabVIEW is touched.
 G1  md5(ORIGINAL) == c39f36e0675339673b707c59f0784fee BEFORE.
 G2  the copy EXISTS at the claudeDev path; its md5 is recorded BEFORE. No file is copied.
 G3  apartment2 attaches, the ORIGINAL is resident read-only, the copy opens ExecState == 1 and no
     dialog is BLOCKING.
 G4  PANEL RECORD: >= 55 of the 60 front-panel CONTROLS return a value. NOTHING is written.
 G5  geometry: the panel window is found by title and its rect is within +-40 px of v3's V6 rect in
     WIDTH and HEIGHT (if not, the derived points are flagged - the run continues and the machine
     checks below decide).
 -- per leg (leg 1 = run1/cal001, leg 2 = run2/cal002; the whole cycle runs TWICE) --
 L.a R2  Run(False) on its own never-joined apartment takes the VI out of idle within RUN_SETTLE.
 L.b R3  3 picks land inside the DERIVED Image rect; `Count` is read before and after each.
 L.c R4  the done click ends the picking loop: a bandpass window appears OR `Count` changes.
 L.d R5  EXACTLY 3 `choose bandpass` panels, each closed by an HWND-token-gated click, and the
         TERMINAL state is the save dialog - never the click cap.
 L.e R6  the save dialog takes an ABSOLUTE path under tools/bench/d0_out/<run-id>/.
 L.f R7  the cal file exists there with size > 0.
 L.g R8  `current image number` (uid 34200) STRICTLY INCREASES over RUN_S s.
 L.h R9  STOP, VI SERVER ONLY, ONE write each, NO re-arm, NO click: ExecState returns to 0/1 within
         STOP_WAIT s. Both stop control values and ExecState are polled throughout.
 L.i R10 a `tra*` file exists in the run folder with size > 0.
 G23 md5(COPY) AFTER == md5(COPY) BEFORE, and the copy still exists (never saved, never deleted).
 G24 md5(ORIGINAL) AFTER == c39f36e0675339673b707c59f0784fee.
 G25 post-run motor read: `TMX?` still 39.

    py tools/bgrun.py --material --max-min 25 --log tools/bench/drive_original_copy_v4.log \
        -- py -u tools/bench/drive_original_copy_v4.py
====================================================================================
"""
import json
import os
import re
import subprocess
import sys
import time

# The sender's normalised pre-write limit line, ANCHORED at both ends (STATUS.md OPEN 55).
# Producer: tools/motor_send_pi.ps1:52.  `$` alone would also accept a trailing "\r" from a
# PowerShell pipe, which is exactly the tolerance wanted, and nothing else.
PRELIMITS_RE = re.compile(r"^PRELIMITS\s+TMN=([-+0-9.eE]+)\s+TMX=([-+0-9.eE]+)\s*$")

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)          # NOTE: v2 calls this "PROJECT" but it is the tools/ dir
ROOT = os.path.dirname(PROJECT)          # the actual project root - motor_gate.py lives under it
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, "tools"))
sys.path.insert(0, HERE)

import drive_original_copy_v2 as d0                                            # noqa: E402
from bench_prep import labview_handles                                         # noqa: E402

# ---------------------------------------------------------------------------------------------
# DELTA 1 - the retarget.  Every path/predicate v3 pointed at the V6 copy now points here.
# ---------------------------------------------------------------------------------------------
ORIGINAL = (r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking"
            r"\Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi")
ORIGINAL_MD5 = "c39f36e0675339673b707c59f0784fee"
COPY = (r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
        r"\Track_D0_copy_20260918.vi")
INVENTORY_JSON = os.path.join(HERE, "d0_inventory.json")

STAMP = time.strftime("%Y%m%d_%H%M%S")
RUN_ID = "v4_%s" % STAMP
RUN_DIR = os.path.join(HERE, "d0_out", RUN_ID)
SHOTS = os.path.join(HERE, "d0_shots_v4")

d0.ORIGINAL = ORIGINAL
d0.ORIGINAL_MD5 = ORIGINAL_MD5
d0.COPY = COPY
d0.COPY_TITLE = os.path.basename(COPY)
d0.RUN_DIR = RUN_DIR
d0.SHOTS = SHOTS
d0.STAMP = STAMP
d0.RUN_ID = RUN_ID
d0.D0_JSON = os.path.join(HERE, "drive_original_copy_v4.json")

D0_JSON = d0.D0_JSON
PROBE_JSON = os.path.join(HERE, "drive_original_copy_v4_clickrecords.json")

rec, log, getv, state, shot = d0.rec, d0.log, d0.getv, d0.state, d0.shot
RECORDS = []
FACTS = d0.FACTS

# --- exact label bytes (d0.C_* come from tools/bench/main_vi_panel_wiring.json; the 4.5 copy's own
# --- inventory confirms every one of them, tools/bench/diag_d0_inventory.log:43,:59,:108,:138,:151)
C_STOP, C_STOP2, C_DONE, C_COUNT = d0.C_STOP, d0.C_STOP2, d0.C_DONE, d0.C_COUNT
I_FRAME, I_CALPATH, I_TRACKPATH = d0.I_FRAME, d0.I_CALPATH, d0.I_TRACKPATH

# --- v3's MEASURED geometry on the V6 copy, 2026-09-17 (tools/bench/drive_original_copy_v3.log:27,
# --- :242). Used ONLY as offsets inside a rect measured at run time - see "THE GEOMETRY PROBLEM".
V6_PANEL_RECT = (-6, 51, 1930, 1107)
V6_IMAGE_RECT = (232, 500, 873, 1013)
V6_PICKS = [(552, 756), (430, 640), (690, 880)]
V6_DONE_XY = (1114, 915)
V6_BANDPASS_RECT = (29, 72, 1060, 874)
V6_BANDPASS_YES = (175, 353)
BANDPASS_TITLE = d0.BANDPASS_TITLE            # "choose bandpass"
SAVE_TITLE = d0.SAVE_TITLE                    # "Save cal cluster file"

RUN_SETTLE = 60.0
PICK_SETTLE = 2.5
CAL_WAIT_1 = 300.0
CAL_WAIT_2 = 240.0
BANDPASS_WAIT = 120.0
BP_CAP = 12
RUN_S = 20.0
STOP_WAIT = 60.0
STOP_POLL = 1.0
RUN2_BUDGET_S = 1020.0
PANEL_RECORD_BUDGET_S = 150.0

GEO = {}                    # filled by derive_geometry()
MOTOR = {}


# =============================================================================================
# DELTA 5 - the motor gate wrapper
# =============================================================================================
def motor_gate(why):
    """Run `py tools/motor_gate.py --session start` and parse its readback. Returns (rc, text)."""
    log("  motor_gate --session start  <- %s" % why)
    try:
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "motor_gate.py"),
                            "--session", "start"],
                           capture_output=True, text=True, timeout=300, cwd=ROOT)
        text = ((r.stdout or "") + (r.stderr or "")).strip()
        rcode = r.returncode
    except Exception as e:                                                     # noqa: BLE001
        text, rcode = "motor_gate raised %r" % e, 99
    for line in text.splitlines():
        log("    | %s" % line)
    return rcode, text


def parse_motor(text):
    """Pull the machine-readable lines out of the gate's output, without importing its parsers on a
    path that could fail: `PRELIMITS TMN=.. TMX=..`, `before: POS?=.. TMN?=.. TMX?=..`,
    `LIMITS TMN=..`, `REFSTATE ..`."""
    out = {}
    for line in (text or "").splitlines():
        s = line.strip()
        if s.startswith("before:"):
            out.setdefault("before_lines", []).append(s)
        if PRELIMITS_RE.match(s):
            out.setdefault("prelimits_lines", []).append(s)
        if s.startswith("LIMITS TMN="):
            out.setdefault("limits_lines", []).append(s)
        if s.startswith("REFSTATE"):
            out.setdefault("refstate_lines", []).append(s)
        if s.startswith("RESULT: controller limits are"):
            out.setdefault("result_lines", []).append(s)
        if s.startswith("SESSION START"):
            out.setdefault("session_lines", []).append(s)
    return out


def _last_field_float(tok):
    """A PI reply token carries the VALUE IN ITS LAST `=`-separated field.  The controller answers a
    per-axis query as `<cmd>=<axis>=<value>` (`TMX?=1=39.00000`) and a scalar one as
    `<cmd>=<value>` (`TMX=39`).  Splitting on the FIRST `=` therefore yields `1=39.00000` on the
    per-axis form, float() raises, and the caller reports None while the line it just read says 39
    - the false red that failed gate 93 of the v5 run (tools/bench/drive_original_copy_v5.log:439).
    Returns a float, or None when there is no value or it is not numeric."""
    parts = tok.split("=")
    if len(parts) < 2:
        return None
    try:
        return float(parts[-1])
    except ValueError:
        return None


def prelimits_from(text):
    """The sender's NORMALISED pre-write limit line, read with an ANCHORED whole-line regex.

    tools/motor_send_pi.ps1:52 prints `PRELIMITS TMN=<n> TMX=<n>` from its own `Num` parser (:41)
    BEFORE the SPA write, so this reader never has to know that the controller answers a per-axis
    query as `<cmd>=<axis>=<value>`.  Anchored on both ends: a log-decorated copy (`    | PRELIMITS
    ...`) and a line with extra trailing fields are BOTH rejected, so a label or format change at the
    sender fails loudly here instead of falling through to some other line.
    Returns (tmn, tmx, line) from the LAST matching line, or (None, None, None)."""
    hit = (None, None, None)
    for line in (text or "").splitlines():
        s = line.strip()
        m = PRELIMITS_RE.match(s)
        if m:
            try:
                hit = (float(m.group(1)), float(m.group(2)), s)
            except ValueError:                                                 # pragma: no cover
                hit = (None, None, None)
    return hit


def tmx_from(text):
    """What the controller HELD when the gate arrived, i.e. the post-LabVIEW-run TMX?.  Returns
    (value_or_None, the line it came from).  Precedence, and why it is not negotiable:

      1. `PRELIMITS TMN=<n> TMX=<n>` - the sender's own normalised PRE-write line (anchored regex).
      2. else the raw `before:` line's `TMX?=` token (also pre-write, same port open).
      3. else (None, the `before:` line if one exists, otherwise a placeholder).  This is the
         TERMINAL case: there is no fourth rule and `LIMITS` is NEVER consulted, in any mode.

    Why `LIMITS` is not a source at all (JUDGEMENT DECISION, cycle 34, STATUS.md OPEN 55 - applied
    cycle 35; the former rule 4 is deleted, and the function is deliberately NOT mode-aware):
    in `limits-set` mode - the ONLY mode any production call site uses (`motor_gate.py:375`) - the
    sender prints `LIMITS` AFTER the SPA write (motor_send_pi.ps1:58/:78), so as an answer to "what
    limit did the controller HOLD when the gate arrived?" it can only ever echo the number we
    ourselves just sent.  A source that is structurally incapable of being evidence is removed, not
    routed around.  `before:`/`PRELIMITS` = "still 39 after the run"; `LIMITS` = "did we just set
    39"; taking the second for the first is a SILENT FALSE GREEN on a motor-limit check, measured on
    the pre-2026-09-18 code (tools/bench/tmx_fallthrough_before.log:4 -> 39.0 off the LIMITS line,
    :10 -> 12.0).  Nothing is lost: `motor_gate.py:377-378` already verifies the written value, and
    limits-set always emits `PRELIMITS` (rule 1) or a literal `TMX?=` (rule 2).
    The cost of the deletion is a `--mode send` transcript now answering None; that makes the
    value-only gate (`:1012`, `tmx == 39.0`) FAIL = a false RED that refuses motion - the safe
    direction.  No production call site is in send mode.
    archive/peer/2026-09-18-tmx-lastfield-parse.md Q2/Q3;
    archive/peer/2026-09-18-tmx-selftest-contract.md."""
    p = parse_motor(text)
    _ptmn, ptmx, pline = prelimits_from(text)
    if ptmx is not None:
        return ptmx, pline
    for s in p.get("before_lines", []):
        for tok in s.split():
            if tok.startswith("TMX?="):
                return _last_field_float(tok), s
    before = p.get("before_lines", [])
    if before:
        return None, before[-1]
    return None, "(no TMX line in the gate's output)"


def selftest_tmx():
    """`py tools/bench/drive_original_copy_v4.py --selftest` - pure-function, no COM, no motor, no
    port, no LabVIEW.  Covers the per-axis form `<cmd>=<axis>=<value>`, the plain `<cmd>=<value>`
    form, malformed lines, and - since 2026-09-18, STATUS.md OPEN 55 - the FALL-THROUGH: a `before:`
    line that exists but carries no `TMX?=` token must answer None, never the post-write `LIMITS`
    line.  Since 2026-09-18 (cycle 35) rule 4 is DELETED, so `LIMITS` is never an answer in any mode
    and the two former "LIMITS fallback" cases now pin None, joined by a third that pins the same
    for a PRE-write (send-mode) LIMITS line.
    PREDICTION CONTRACT: 17 pass / 0 fail.  The five 2026-09-18 cases are DISCRIMINATING, not merely
    green - the same fixtures were run through the unpatched parser first and are on record in
    tools/bench/tmx_fallthrough_before.log:4 (39.0 instead of None) and :10 (12.0 instead of 39.0);
    tools/bench/tmx_fallthrough_probe.py re-runs them against whatever is on disk."""
    cases = [
        # (label, gate text, expected value, expected substring of the line reported)
        # MACHINE RECORD. The gate's RAW stdout line, exactly as motor_gate() hands it to
        # parse_motor: tools/motor_send_pi.ps1:52 writes `before: ...` FLUSH-LEFT and
        # tools/motor_gate.py:369 re-emits it with one whole-block .strip(), no per-line
        # decoration.  The "    | " seen in the log is added afterwards by log() at line 211.
        ("before/per-axis (the real v5 line)",
         "before: POS?=1=30.00000 TMN?=1=0.00000 TMX?=1=39.00000 ERR?=0",
         39.0, "TMX?=1=39.00000"),
        # MECHANISM PROOF, kept deliberately: the log-decorated form of the SAME line must be
        # REJECTED by parse_motor (it requires startswith("before:")).  This is the string whose
        # first run failed; keeping it preserves the evidence instead of deleting it.
        ("log-decorated line is NOT parsed",
         "    | before: POS?=1=30.00000 TMN?=1=0.00000 TMX?=1=39.00000 ERR?=0",
         None, "no TMX line"),
        # TOLERANCE ONLY - the C-863.11 answers a travel query as `<axis>=<value>`, so this sender
        # cannot emit the plain form; the case guards the brief's tolerance requirement, it is not
        # a machine record (peer 2026-09-18-tmx-lastfield-parse.md, Q2).
        ("before/plain (tolerance only)",
         "before: POS?=0.00000 TMN?=0 TMX?=39.00000 ERR?=0",
         39.0, "TMX?=39.00000"),
        ("before/negative per-axis",
         "before: TMX?=1=-2.50000",
         -2.5, "TMX?=1=-2.50000"),
        ("before wins over LIMITS",
         "before: TMX?=1=39.00000\nLIMITS TMN=0 TMX=12 SPA15=12 SPA30=0",
         39.0, "before:"),
        # ---------------------------------------------------------------------------------------
        # RULE 4 IS DELETED (cycle-34 judgement, applied cycle 35).  These two fixtures are the
        # SAME strings that used to answer 39.0 off the post-write `LIMITS` line; their expected
        # value is now None.  A pre-write `LIMITS` line is never the answer - see the third case
        # below, which pins exactly that sentence, and tmx_from()'s docstring for why.
        # ---------------------------------------------------------------------------------------
        ("LIMITS-only transcript answers None (rule 4 deleted)",
         "LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0",
         None, "no TMX line"),
        ("LIMITS-only / per-axis form also answers None",
         "LIMITS TMN=0 TMX=1=39.00000 SPA15=39 SPA30=0",
         None, "no TMX line"),
        # THE PIN the brief asks for: "a pre-write `LIMITS` line is never the answer".  A `--mode
        # send` transcript prints LIMITS BEFORE any transmit, so this line really is pre-write and
        # really does hold the controller's held value - and it STILL must not be used, because the
        # reader cannot tell it apart from the post-write one and no production call site is ever
        # in send mode.  Value None => the value-only gate fails => a false RED, the safe direction.
        ("a PRE-write (send-mode) LIMITS line is never the answer either",
         "MODE send\nLIMITS TMN=0 TMX=39 SPA15=39 SPA30=0\nSENT SPA 1 0x15 39",
         None, "no TMX line"),
        ("malformed value",
         "before: TMX?=1=thirty-nine",
         None, "thirty-nine"),
        ("empty value",
         "before: TMX?=",
         None, "TMX?="),
        # The VALUE was, and stays, None.  Only the REPORTED LINE changed on 2026-09-18: it used to
        # be the placeholder "(no TMX line in the gate's output)", because the old code had walked
        # past the `before:` line into the LIMITS fallback and found nothing there either.  It now
        # names the `before:` line it actually read and rejected, which is the whole point of the
        # fix - so this case's expected line was updated, its expected value was not.
        ("no TMX anywhere (reports the before: line it read)",
         "before: POS?=1=0.00000 ERR?=0",
         None, "before: POS?=1=0.00000"),
        ("no TMX and no before: line at all",
         "REFSTATE RON=0 FRF=1 POS=0.00000 POS_BEFORE=0.00000 ERR=0",
         None, "no TMX line"),
        # ---------------------------------------------------------------------------------------
        # STATUS.md OPEN 55 - THE SILENT FALSE GREEN.  These five cases are the whole point of the
        # 2026-09-18 patch; the ten above all passed WHILE the fault was live (tmx_selftest.log:1-12
        # = 10 pass / 0 fail), which is why a fall-through case had to be written by hand.
        # ---------------------------------------------------------------------------------------
        # THE FAULT.  A `before:` line with no TMX?= token, plus the POST-WRITE LIMITS line that
        # motor_send_pi.ps1:58 prints AFTER `SPA 1 0x15 39`.  Measured against the UNPATCHED parser
        # (tools/bench/tmx_fallthrough_before.log:4): got=39.0 off `LIMITS ...` - the gate reporting
        # back the number it had just written, and PASSING a motor-limit check on an ASSEMBLED rig
        # without ever reading what the controller held after the LabVIEW run.
        ("FALL-THROUGH: before: without TMX?= never reads LIMITS",
         "before: POS?=1=30.00000 TMN?=1=0.00000 ERR?=0\nLIMITS TMN=0 TMX=39 SPA15=39 SPA30=0",
         None, "before: POS?=1=30.00000"),
        # The same fixture with the sender's new normalised line present: the PRE-write value wins,
        # and it is a DIFFERENT number from the post-write LIMITS line, so the two cannot be confused.
        # Unpatched, this returned 12.0 (tools/bench/tmx_fallthrough_before.log:10).
        ("PRELIMITS beats a post-write LIMITS",
         "PRELIMITS TMN=0 TMX=39\nbefore: POS?=1=30.00000 TMN?=1=0.00000 ERR?=0\n"
         "LIMITS TMN=0 TMX=12 SPA15=12 SPA30=0",
         39.0, "PRELIMITS TMN=0 TMX=39"),
        # The regex is anchored at BOTH ends, so a label/format change at the sender fails loudly
        # instead of silently matching something else:
        ("PRELIMITS anchored left: a log-decorated copy is NOT read",
         "    | PRELIMITS TMN=0 TMX=12\nbefore: POS?=1=30.00000 TMX?=1=39.00000 ERR?=0",
         39.0, "TMX?=1=39.00000"),
        ("PRELIMITS anchored right: trailing fields are NOT read",
         "PRELIMITS TMN=0 TMX=12 SPA15=12\nbefore: POS?=1=30.00000 TMX?=1=39.00000 ERR?=0",
         39.0, "TMX?=1=39.00000"),
        # An unreadable reply makes motor_send_pi.ps1 print the field EMPTY ("-f $null"); the anchored
        # regex must then NOT match, and with no TMX?= token either the answer is None, not a number.
        ("PRELIMITS with an empty field is NOT read",
         "PRELIMITS TMN= TMX=\nbefore: POS?=1=30.00000 ERR?=0\nLIMITS TMN=0 TMX=39 SPA15=39 SPA30=0",
         None, "before: POS?=1=30.00000"),
    ]
    npass = 0
    for label, text, want, want_line in cases:
        got, line = tmx_from(text)
        ok = (got == want) and (want_line in line)
        npass += 1 if ok else 0
        # the INPUT is printed on a failure (peer's cheapest discriminating test): it separates
        # "the parser is wrong" from "the fixture string is not what production feeds it".
        print("  %s | %-40s | got=%r line=%r (want %r)%s"
              % ("PASS" if ok else "FAIL", label, got, line, want,
                 "" if ok else "  text=%r" % text), flush=True)
    print("SELFTEST tmx_from: %d pass / %d fail" % (npass, len(cases) - npass), flush=True)
    return npass == len(cases)


# =============================================================================================
# DELTA 3 helper - the HWND-token click, copied from v3 because it must call this file's geometry
# (tools/bench/drive_original_copy_v3.py:84-152; logic unchanged)
# =============================================================================================
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
    if not j:
        return {}, False
    c = {"sfw_ret": bool(j.get("setforegroundwindow", {}).get("ret")),
         "fg_after_sfw_is_target": bool(j.get("fg_after_sfw_is_target")),
         "fg_at_buttondown_is_target": bool(j.get("fg_at_buttondown_is_target")),
         "wfp_press_root_is_target": bool(j.get("wfp_press_xy", {}).get("root_is_target"))}
    return c, all(c.values())


def gated_click_hwnd(title, x, y, why, max_attempts=2):
    """THE TOKEN IS THE HWND, NOT THE TITLE (v3's finding). A second attempt is issued ONLY if the
    record proves the click was NOT delivered AND the same hwnd is still alive - never blind."""
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
            notes.append("STOP: the record says the click WAS correctly targeted yet hwnd %s is "
                         "still alive - the deferral case; NOT retrying blind" % hwnd)
            return False, hwnd, "; ".join(notes)
        notes.append("record proves NOT delivered (%s) -> one more attempt on the same hwnd"
                     % [k for k, v in c.items() if not v])
    return False, None, "; ".join(notes)


# =============================================================================================
# geometry: derive this panel's points from the rect measured NOW + v3's measured offsets
# =============================================================================================
def _off(pt, ref_rect):
    return (pt[0] - ref_rect[0], pt[1] - ref_rect[1])


def _apply(off, rect):
    return (rect[0] + off[0], rect[1] + off[1])


def derive_geometry():
    """Returns (ok, detail). Fills GEO with image_rect / picks / done_xy for THIS panel window."""
    r = d0.win_rect(d0.COPY_TITLE)
    GEO["panel_rect"] = r
    GEO["v6_panel_rect"] = V6_PANEL_RECT
    if not r:
        return False, "panel window '%s' not found by title" % d0.COPY_TITLE
    w, h = r[2] - r[0], r[3] - r[1]
    w6, h6 = V6_PANEL_RECT[2] - V6_PANEL_RECT[0], V6_PANEL_RECT[3] - V6_PANEL_RECT[1]
    GEO["size_now"], GEO["size_v6"] = (w, h), (w6, h6)
    GEO["size_delta"] = (w - w6, h - h6)
    tl = _apply(_off((V6_IMAGE_RECT[0], V6_IMAGE_RECT[1]), V6_PANEL_RECT), r)
    br = _apply(_off((V6_IMAGE_RECT[2], V6_IMAGE_RECT[3]), V6_PANEL_RECT), r)
    GEO["image_rect"] = (tl[0], tl[1], br[0], br[1])
    GEO["picks"] = [_apply(_off(p, V6_PANEL_RECT), r) for p in V6_PICKS]
    GEO["done_xy"] = _apply(_off(V6_DONE_XY, V6_PANEL_RECT), r)
    GEO["bandpass_yes_offset"] = _off(V6_BANDPASS_YES, V6_BANDPASS_RECT)
    close = abs(w - w6) <= 40 and abs(h - h6) <= 40
    return close, ("panel rect=%s size=%s (v3/V6 rect=%s size=%s, delta=%s); derived image_rect=%s "
                   "picks=%s done=%s bandpass_yes_offset=%s"
                   % (r, GEO["size_now"], V6_PANEL_RECT, GEO["size_v6"], GEO["size_delta"],
                      GEO["image_rect"], GEO["picks"], GEO["done_xy"],
                      GEO["bandpass_yes_offset"]))


def bandpass_yes_now():
    r = d0.win_rect(BANDPASS_TITLE)
    if not r:
        return None, None
    return _apply(GEO["bandpass_yes_offset"], r), r


# =============================================================================================
# DELTA 2 - RECORD the panel parameters.  Nothing is written.
# =============================================================================================
def control_labels():
    """The exact label bytes of the 60 front-panel CONTROLS of THIS copy, from the read-only
    inventory measured 2026-09-18 (tools/bench/d0_inventory.json -> panel_rows)."""
    try:
        with open(INVENTORY_JSON, encoding="utf-8") as f:
            inv = json.load(f)
    except Exception as e:                                                     # noqa: BLE001
        log("  control_labels: %s unreadable (%r)" % (INVENTORY_JSON, e))
        return []
    rows = inv.get("panel_rows") or []
    return [r["label"] for r in rows if r.get("indicator") is False and r.get("label")]


def record_panel(tag):
    """READ every control. NEVER write. Returns (n_read, n_err, dict)."""
    labels = control_labels()
    vals, errs = {}, 0
    t0 = time.time()
    truncated = None
    for lab in labels:
        if time.time() - t0 > PANEL_RECORD_BUDGET_S:
            truncated = lab
            break
        v = getv(lab, timeout=4.0)
        if isinstance(v, str) and v.startswith("ERR:"):
            errs += 1
        vals[lab] = v
    FACTS["panel_record_%s" % tag] = vals
    FACTS["panel_record_%s_meta" % tag] = {"labels": len(labels), "read": len(vals), "errors": errs,
                                           "truncated_at": truncated,
                                           "seconds": round(time.time() - t0, 1)}
    log("  panel record [%s]: %d/%d controls read, %d errors, %.0fs%s"
        % (tag, len(vals), len(labels), errs, time.time() - t0,
           (", TRUNCATED at %r" % truncated) if truncated else ""))
    for lab in sorted(vals):
        log("    PARAM %-40r = %r" % (lab, vals[lab]))
    return len(vals) - errs, errs, vals


# =============================================================================================
# DELTA 4 - the stop.  VI SERVER ONLY.  `stop (end)` uid 7 is NEVER clicked.
# =============================================================================================
def stop_single_write(tag):
    """The peer's discriminating test verbatim (archive/peer/2026-09-17-d0v3-stop-heuristic.md:32):
    ONE `True` write to each stop control, NO re-arm, NO GUI, polling BOTH control values and
    ExecState. Returns (idle, seconds, trace)."""
    trace = []
    for ctl in (C_STOP, C_STOP2):
        try:
            d0.com.call("set", ctl, True, timeout=10.0)
            trace.append("write %r=True" % ctl)
        except Exception as e:                                                 # noqa: BLE001
            trace.append("write %r RAISED %s" % (ctl, e))
    t0 = time.time()
    while time.time() - t0 < STOP_WAIT:
        time.sleep(STOP_POLL)
        st = state()
        s1, s2, fr = getv(C_STOP), getv(C_STOP2), getv(I_FRAME)
        trace.append("t=%.1f ExecState=%s %r=%r %r=%r frame=%r"
                     % (time.time() - t0, st, C_STOP, s1, C_STOP2, s2, fr))
        if st in (0, 1):
            return True, time.time() - t0, trace
    return False, time.time() - t0, trace


def stop_rearmed(tag):
    """Only reached if the single-write test did not idle the VI. Still VI SERVER ONLY."""
    t0 = time.time()
    rearms = 0
    while time.time() - t0 < STOP_WAIT:
        for ctl in (C_STOP, C_STOP2):
            try:
                d0.com.call("set", ctl, True, timeout=10.0)
            except Exception as e:                                             # noqa: BLE001
                log("  stop[%s]: set(%r) raised %s" % (tag, ctl, e))
        rearms += 1
        time.sleep(2.0)
        if state() in (0, 1):
            return True, time.time() - t0, rearms
    return False, time.time() - t0, rearms


def stop_measured(tag):
    """Returns (stopped_by_vi_server, mechanism, detail). Abort is NEVER used here - cleanup owns
    it, and a run that needed Abort is reported as a FAILED stop."""
    idle, secs, trace = stop_single_write(tag)
    FACTS["stop_trace_%s" % tag] = trace
    if idle:
        return True, "SetControlValue ONE write each, no re-arm", \
               "idle after %.1fs; %s" % (secs, " | ".join(trace[-4:]))
    idle2, secs2, rearms = stop_rearmed(tag)
    if idle2:
        return True, "SetControlValue RE-ARMED (the single write did NOT idle it)", \
               ("single-write test failed after %.0fs, then %d re-arms idled it after %.0fs; "
                "single-write trace tail: %s" % (secs, rearms, secs2, " | ".join(trace[-4:])))
    shot("v4_stopfail_%s" % tag)
    return False, "NOTHING IN VI SERVER STOPPED IT", \
           ("one write each: not idle in %.0fs; then %d re-arms: not idle in %.0fs; ExecState=%s; "
            "frame=%r. `stop (end)` uid 7 has NO screen coordinate, so there is no GUI fallback by "
            "design; COM Abort is left to cleanup and is reported there."
            % (secs, rearms, secs2, state(), getv(I_FRAME)))


# =============================================================================================
# one full leg: run -> picks -> done -> 3 bandpass -> save -> loop -> stop -> trace file
# =============================================================================================
def leg(tag, n, base_path, cal_wait):
    """n = the gate-number base, so leg 1 numbers 10.. and leg 2 numbers 20.. ."""
    ok = True

    # ---- L.a R2 run ----------------------------------------------------------------------------
    resets = {}
    for ctl in (C_STOP, C_STOP2, C_DONE):
        try:
            d0.com.call("set", ctl, False, timeout=10.0)
            resets[ctl] = getv(ctl)
        except Exception as e:                                                 # noqa: BLE001
            resets[ctl] = "ERR %s" % e
    rec("%d %s.pre reset+readback of the 3 control-flow booleans" % (n, tag), "VISERVER", True,
        "%r (step 1 of the peer's stop test; NO panel PARAMETER is written)" % resets)

    rt = d0.RunThread(COPY, "v4_%s" % tag)
    rt.start()
    t0 = time.time()
    left = False
    while time.time() - t0 < RUN_SETTLE:
        time.sleep(2.0)
        if state() not in (1, -1):
            left = True
            break
    rec("%d %s.R2 VI left idle" % (n + 1, tag), "COM", left,
        "ExecState=%s after %.0fs; Run returned=%s (ActiveX Run behaves as Wait-Until-Done=TRUE - "
        "measured twice in v2, which is why this thread is never joined)"
        % (state(), time.time() - t0, rt.returned is not None))
    ok &= left
    if not left:
        shot("v4_%s_run_fail" % tag)
        return ok

    # ---- L.b R3 the 3 bead picks ----------------------------------------------------------------
    d0.focus(d0.COPY_TITLE)
    time.sleep(1.2)
    shot("v4_%s_before_picks" % tag)
    counts = [getv(C_COUNT)]
    all_inside = True
    for i, (x, y) in enumerate(GEO["picks"]):
        # The derived points are inside the derived image rect BY CONSTRUCTION, so that is not a
        # check. The real one is that they fall inside the panel window actually on screen now.
        if not d0.inside(GEO["panel_rect"], (x, y), margin=5):
            all_inside = False
            log("  pick %d %s is OUTSIDE the measured panel window rect %s - NOT clicked"
                % (i + 1, (x, y), GEO["panel_rect"]))
            continue
        d0.click(x, y, "bead %d (%s) in the derived Image rect %s"
                 % (i + 1, "reference" if i == 0 else "magnetic", GEO["image_rect"]))
        time.sleep(PICK_SETTLE)
        counts.append(getv(C_COUNT))
    shot("v4_%s_after_picks" % tag)
    rec("%d %s.R3 3 bead picks" % (n + 2, tag), "GUI", all_inside,
        "derived picks=%s inside=%s; `Count` across the picks: %s"
        % (GEO["picks"], GEO["image_rect"], counts))
    ok &= all_inside

    # ---- L.c R4 the done button -----------------------------------------------------------------
    cnt_before = getv(C_COUNT)
    dx, dy = GEO["done_xy"]
    if not d0.inside(GEO["panel_rect"], (dx, dy), margin=5):
        rec("%d %s.R4 picking loop ended" % (n + 3, tag), "GUI", False,
            "the derived `Done Picking \\nBeads?` point %s is OUTSIDE the measured panel rect %s - "
            "NOT clicked" % (GEO["done_xy"], GEO["panel_rect"]))
        shot("v4_%s_done_outside" % tag)
        return False
    d0.click(dx, dy, "`Done Picking \\nBeads?` (uid 11819) Yes button, derived %s" % (GEO["done_xy"],))
    ended = False
    t0 = time.time()
    while time.time() - t0 < cal_wait:
        time.sleep(2.0)
        if d0.win_present(BANDPASS_TITLE) or d0.win_present(SAVE_TITLE):
            ended = True
            break
        c = getv(C_COUNT)
        if isinstance(c, (int, float)) and isinstance(cnt_before, (int, float)) and c != cnt_before:
            ended = True
    rec("%d %s.R4 picking loop ended" % (n + 3, tag), "GUI", ended,
        "Count %r -> %r after %.0fs; bandpass present=%s; save present=%s"
        % (cnt_before, getv(C_COUNT), time.time() - t0,
           d0.win_present(BANDPASS_TITLE), d0.win_present(SAVE_TITLE)))
    ok &= ended
    if not ended:
        shot("v4_%s_done_fail" % tag)
        return ok

    # ---- L.d R5 DELTA 3: the three `choose bandpass` panels --------------------------------------
    answered, details, hwnds = 0, [], []
    stop_reason = "cap"
    while answered < BP_CAP:
        t0 = time.time()
        budget = cal_wait if answered == 0 else BANDPASS_WAIT
        seen = False
        while time.time() - t0 < budget:
            if d0.win_present(SAVE_TITLE):
                stop_reason = "save dialog appeared after %d panel(s)" % answered
                break
            if d0.win_present(BANDPASS_TITLE):
                seen = True
                break
            time.sleep(1.5)
        if not seen:
            if stop_reason == "cap":
                stop_reason = ("no `%s` window within %.0fs (after %d)"
                               % (BANDPASS_TITLE, budget, answered))
            break
        time.sleep(3.0)                    # let the panel settle - "clicked too early" excluded
        yes, brect = bandpass_yes_now()
        if yes is None:
            stop_reason = "panel %d: rect vanished before the click" % (answered + 1)
            break
        if answered == 0:
            shot("v4_%s_bandpass1" % tag)
        cnt_pre = getv(C_COUNT)
        good, hwnd, note = gated_click_hwnd(BANDPASS_TITLE, yes[0], yes[1],
                                            "bandpass Yes #%d" % (answered + 1))
        cnt_post = getv(C_COUNT)
        details.append("panel %d: rect=%s derived_yes=%s hwnd_died=%s Count %r->%r | %s"
                       % (answered + 1, brect, yes, good, cnt_pre, cnt_post, note))
        if not good:
            shot("v4_%s_bandpass_stuck_%d" % (tag, answered + 1))
            stop_reason = "panel %d did not close" % (answered + 1)
            break
        answered += 1
        hwnds.append(hwnd)
        time.sleep(1.0)
    # The TERMINAL state is the save dialog, NEVER the click cap.
    r5 = d0.win_present(SAVE_TITLE) and answered == 3
    FACTS["bandpass_answered_%s" % tag] = answered
    FACTS["bandpass_hwnds_%s" % tag] = hwnds
    rec("%d %s.R5 the three `choose bandpass` panels (HWND-gated)" % (n + 4, tag), "GUI", r5,
        "%d panel(s) closed (contract: exactly 3), distinct hwnds %s; terminal=%s || %s"
        % (answered, hwnds, stop_reason, " || ".join(details)))
    ok &= r5
    if not d0.win_present(SAVE_TITLE):
        return ok

    # ---- L.e R6 the save dialog (inherited from v2 unchanged) ------------------------------------
    saved, sdetail = d0.answer_save_dialog("v4_%s" % tag, base_path)
    rec("%d %s.R6 save dialog answered (there is NO save-path CONTROL on this panel - `Cal File "
        "Path` 27930 / `Track File Path` 28450 / `File # Saved` 6 are INDICATORS, so a file dialog "
        "is the only route)" % (n + 5, tag), "GUI", saved, sdetail)
    ok &= saved

    # ---- L.f R7 the cal file ---------------------------------------------------------------------
    time.sleep(3.0)
    calf = base_path if os.path.isfile(base_path) else None
    if calf is None and os.path.isdir(RUN_DIR):
        for f in os.listdir(RUN_DIR):
            if f.lower().startswith(os.path.basename(base_path).lower()):
                calf = os.path.join(RUN_DIR, f)
                break
    r7 = bool(calf) and os.path.getsize(calf) > 0
    rec("%d %s.R7 cal file in OUR folder" % (n + 6, tag), "FILE", r7,
        "%s (%s B); `Cal File Path` indicator=%r"
        % (calf, os.path.getsize(calf) if calf else "-", getv(I_CALPATH)))
    ok &= r7

    # ---- L.g R8 the experiment loop --------------------------------------------------------------
    vals = []
    t0 = time.time()
    while time.time() - t0 < RUN_S:
        time.sleep(2.0)
        vals.append(getv(I_FRAME))
    num = [v for v in vals if isinstance(v, (int, float))]
    r8 = len(num) >= 2 and num[-1] > num[0]
    FACTS["frames_%s" % tag] = vals
    rec("%d %s.R8 frame counter advances" % (n + 7, tag), "VISERVER", r8,
        "%s over %.0fs: %r .. %r (lost=%r)"
        % (I_FRAME, RUN_S, vals[0] if vals else None, vals[-1] if vals else None, getv(d0.I_LOST)))
    ok &= r8

    # ---- L.h R9 DELTA 4: the stop, VI SERVER ONLY -------------------------------------------------
    stopped, mech, sdet = stop_measured(tag)
    FACTS["stop_mechanism_%s" % tag] = "%s | %s" % (mech, sdet)
    rec("%d %s.R9 stop through the VI's OWN control, VI SERVER ONLY (uid 7 is never clicked)"
        % (n + 8, tag), "VISERVER", stopped, "%s -- %s" % (mech, sdet))
    ok &= stopped

    # ---- L.i R10 the trace file -------------------------------------------------------------------
    time.sleep(5.0)
    _n, _tot, by, other = d0.listdir_stats(RUN_DIR)
    trace = [o for o in other if "tra" in o.lower()]
    r10 = bool(trace)
    FACTS["files_%s" % tag] = other
    FACTS["by_ext_%s" % tag] = by
    rec("%d %s.R10 trace file written" % (n + 9, tag), "FILE", r10,
        "non-TIFF files: %s; by ext: %s; `Track File Path` indicator=%r"
        % (other or "(none)", by, getv(I_TRACKPATH)))
    ok &= r10
    return ok


# =============================================================================================
def main():
    ok = True
    os.makedirs(RUN_DIR, exist_ok=True)
    os.makedirs(SHOTS, exist_ok=True)

    FACTS["handles_before"] = labview_handles()
    log("LabVIEW handles BEFORE %s (None/0 = not running yet)" % FACTS["handles_before"])

    # ---- G0 the motor gate, BEFORE LabVIEW is touched -------------------------------------------
    rc0, txt0 = motor_gate("cycle27-plan Pre-decided 4: an unattended run of the copy executes the "
                           "original's device init, which drives the PI stage and the ASI")
    p0 = parse_motor(txt0)
    MOTOR["start_rc"] = rc0
    MOTOR["start_parsed"] = p0
    g0 = (rc0 == 0)
    rec("0 G0 motor gate --session start", "MOTOR", g0,
        "exit=%d; %s; %s; %s" % (rc0,
                                 (p0.get("limits_lines") or ["(no LIMITS line)"])[-1],
                                 (p0.get("refstate_lines") or ["(no REFSTATE line)"])[-1],
                                 (p0.get("session_lines") or ["(no SESSION line)"])[-1]))
    if not g0:
        rec("0a RUN REFUSED", "MOTOR", False,
            "the gate did not verify the controller limits, so the VI is NOT started "
            "(cycle27-plan Pre-decided 4: refuse the run if the readback fails)")
        return False

    # ---- G1/G2 the two files ---------------------------------------------------------------------
    before = d0.md5(ORIGINAL)
    FACTS["md5_original_before"] = before
    rec("1 G1 md5(ORIGINAL) before", "FILE", before == ORIGINAL_MD5, before)
    ok &= before == ORIGINAL_MD5

    exists = os.path.isfile(COPY)
    cbefore = d0.md5(COPY) if exists else None
    FACTS["md5_copy_before"] = cbefore
    rec("2 G2 the D0 copy exists (NOTHING is copied, saved or deleted)", "FILE", exists,
        "%s (%s B) md5=%s" % (COPY, os.path.getsize(COPY) if exists else "-", cbefore))
    ok &= exists
    if not exists:
        return ok

    try:
        # ---- G3 attach / preload / open -----------------------------------------------------------
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
            shot("v4_g3_fail")
            return ok

        # ---- G4 DELTA 2: RECORD the panel parameters ----------------------------------------------
        nread, nerr, _ = record_panel("before")
        g4 = nread >= 55
        rec("6 G4 panel parameters RECORDED (never set)", "VISERVER", g4,
            "%d of 60 controls returned a value, %d errors; the harness writes NO parameter - the "
            "values saved in the copy are the ones the user last used" % (nread, nerr))
        ok &= g4

        # ---- G5 derive the screen geometry ---------------------------------------------------------
        g5, gdetail = derive_geometry()
        rec("7 G5 panel geometry derived from v3's V6 offsets", "GUI", g5, gdetail)
        if not g5:
            log("  NOTE: G5 failed only means the derived points are less trustworthy; the run "
                "continues and the machine-level checks (Count, bandpass window, HWND death) decide.")
        ok &= g5
        if not GEO.get("picks"):
            return ok

        # ---- LEG 1 ---------------------------------------------------------------------------------
        ok &= leg("run1", 10, os.path.join(RUN_DIR, "cal001"), CAL_WAIT_1)

        # ---- LEG 2 - the whole cycle again (Pre-decided 3: "repeats once") -------------------------
        el = time.time() - d0._t0
        st = state()
        if st in (0, 1) and el < RUN2_BUDGET_S:
            ok &= leg("run2", 20, os.path.join(RUN_DIR, "cal002"), CAL_WAIT_2)
        else:
            rec("20 run2 RESTART LEG", "COM", False,
                "NOT started: ExecState=%s, elapsed %.0fs (budget %.0fs)" % (st, el, RUN2_BUDGET_S))
            ok = False
        return ok
    finally:
        cleanup()
        report()


_once = set()


def cleanup():
    if "cleanup" in _once:
        return
    _once.add("cleanup")
    # 1. nothing may be left running
    aborted = None
    try:
        if state() not in (0, 1, -1):
            stopped, mech, det = stop_measured("cleanup")
            log("cleanup: stop -> %s (%s) %s" % (stopped, mech, det))
            if not stopped:
                try:
                    d0.com.call("abort", timeout=20.0)
                    time.sleep(3.0)
                    aborted = "COM Abort used in cleanup; ExecState after = %s" % state()
                except Exception as e:                                         # noqa: BLE001
                    aborted = "COM Abort raised %s" % e
                log("cleanup: %s" % aborted)
    except Exception as e:                                                     # noqa: BLE001
        log("cleanup: stop path raised %r" % e)
    FACTS["cleanup_abort"] = aborted

    # 2. the panel record AFTER the run, then leave every control-flow boolean False
    try:
        record_panel("after")
    except Exception as e:                                                     # noqa: BLE001
        log("cleanup: panel record after raised %r" % e)
    for ctl in (C_STOP, C_STOP2, C_DONE):
        try:
            d0.com.call("set", ctl, False, timeout=6.0)
        except Exception:                                                      # noqa: BLE001
            pass
    try:
        d0.com.call("closepanel", timeout=30.0)
    except Exception as e:                                                     # noqa: BLE001
        log("cleanup: CloseFrontPanel raised %s" % e)
    try:
        d0.com.call("release", timeout=10.0)
    except Exception:                                                          # noqa: BLE001
        pass

    # 3. file accounting. This copy has NO TIFF writer (uids 22700/23020/23175/22703 ABSENT,
    #    tools/bench/diag_d0_trace_path.log:31-37), so the sweep is expected to remove nothing.
    n, tot, by, other = d0.listdir_stats(RUN_DIR)
    FACTS["run_dir"] = {"path": RUN_DIR, "files": n, "bytes": tot, "by_ext": by, "non_tiff": other}
    dn, db = d0.delete_tiffs(RUN_DIR)
    FACTS["tiffs_deleted"] = {"count": dn, "bytes": db}
    log("cleanup: run folder %d files / %d bytes; TIFFs deleted %d / %d bytes" % (n, tot, dn, db))

    # 4. THE COPY IS NEVER DELETED AND NEVER SAVED - the md5 is the proof.
    cafter = d0.md5(COPY) if os.path.isfile(COPY) else None
    FACTS["md5_copy_after"] = cafter
    same = (cafter is not None and cafter == FACTS.get("md5_copy_before"))
    rec("90 G23 md5(COPY) unchanged - the copy was RUN, never saved, never deleted", "FILE", same,
        "%s -> %s (exists=%s)" % (FACTS.get("md5_copy_before"), cafter, os.path.isfile(COPY)))

    after = d0.md5(ORIGINAL)
    FACTS["md5_original_after"] = after
    rec("91 G24 md5(ORIGINAL) after", "FILE", after == ORIGINAL_MD5, after)

    FACTS["handles_after"] = labview_handles()
    log("LabVIEW handles AFTER %s (before %s)" % (FACTS["handles_after"], FACTS.get("handles_before")))

    # 5. post-run motor read. There is no read-only PI mode in the gate; `--session start` prints
    #    `before: POS?=.. TMN?=.. TMX?=..` from the controller BEFORE it writes anything
    #    (tools/motor_send_pi.ps1:52), which is exactly the TMX? re-read the brief asks for.
    #    `--session end` is NEVER called: the limits stay on for unattended runs.
    rc1, txt1 = motor_gate("post-run TMX? re-read (cycle27-plan Pre-decided 4: the 39 mm ceiling is "
                           "RAM-only and the axis lost FRF? once before)")
    tmx, line = tmx_from(txt1)
    p1 = parse_motor(txt1)
    MOTOR["after_rc"] = rc1
    MOTOR["after_tmx"] = tmx
    MOTOR["after_parsed"] = p1
    FACTS["motor"] = MOTOR
    rec("92 G25 post-run TMX? still 39", "MOTOR", tmx == 39.0,
        "TMX?=%r from %r; gate exit=%d; %s; %s"
        % (tmx, line, rc1, (p1.get("limits_lines") or ["(no LIMITS line)"])[-1],
           (p1.get("refstate_lines") or ["(no REFSTATE line)"])[-1]))

    FACTS["gui_actions"] = d0.GUI_ACTIONS[0]
    FACTS["geometry"] = GEO
    with open(PROBE_JSON, "w", encoding="utf-8") as f:
        json.dump(RECORDS, f, indent=1, default=str)
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
    print("\nFACTS: %s" % json.dumps(FACTS, default=str, indent=1)[:12000], flush=True)
    with open(D0_JSON, "w", encoding="utf-8") as f:
        json.dump({"stamp": STAMP, "run_id": RUN_ID, "copy": COPY, "original": ORIGINAL,
                   "run_dir": RUN_DIR, "steps": steps, "facts": FACTS, "geometry": GEO,
                   "motor": MOTOR}, f, indent=1, default=str)
    print("json: %s" % D0_JSON, flush=True)
    print("\n=== D0 v4: %d pass, %d fail ===" % (npass, len(steps) - npass), flush=True)
    print("FAILING: %s" % ", ".join(s["step"] for s in steps if not s["ok"]), flush=True)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        # pure-function check of tmx_from; opens nothing, drives nothing.
        sys.exit(0 if selftest_tmx() else 1)
    good = False
    try:
        good = main()
    except Exception as e:                                                      # noqa: BLE001
        import traceback
        traceback.print_exc()
        rec("!! v4 exception", "COM", False, repr(e))
        try:
            cleanup()
        except Exception:                                                       # noqa: BLE001
            pass
        report()
    sys.exit(0 if good else 1)
