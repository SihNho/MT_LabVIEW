"""drive_original_copy_v2.py - D0 v2: a FULL UNATTENDED cycle on a plain COPY of the original
main VI: load -> run -> 3 bead picks -> N bandpass "Yes" panels -> done -> save dialog INTO A
HARNESS-OWNED FOLDER -> experiment loop -> stop via the VI's OWN stop control -> idle -> file
check -> restart -> second loop -> stop -> close without saving.

REDESIGN, not a patch. v1 (tools/bench/drive_original_copy.py, logs drive_original_copy{,_run2}.log)
died because its single COM worker thread entered vi.Run(False) and never came back, so every later
command sat in the PYTHON queue and the harness printed its own sentence "LabVIEW is blocked".
codex refuted that diagnosis from our own source:
  archive/peer/2026-09-17-d0-com-blocked-in-picking-loop.md
Two findings from that review are built into this file:
  (a) Run(False) must be issued from a worker the driver NEVER waits on; a SECOND, independently
      initialised COM apartment does the polling (that is also the review's falsification test:
      "a second independently initialized COM apartment successfully executes Application.Version,
      obtains the running VI reference, and performs GetControlValue").
  (b) SetControlValue raises NO Value Change event, so it can never replace a click where the
      diagram waits on an event. Bead picking / "Yes" panels are therefore GUI BY DESIGN, not as a
      fallback (the user's option 1, 2026-09-17).

WHAT ALREADY EXISTS (checked before writing a line - CLAUDE.md "before creating any new op, tool or
recipe"):
  * tools/bench/drive_original_copy.py            - v1 of THIS driver; superseded by this file.
  * tools/gscript.py                              - lv()/op()/exec_state()/open_panel()/_run().
      `_run` is SYNCHRONOUS; `ensure_loaded` is edit-mode; `save` must never be called here.
      NO gscript helper reads a front-panel control's SCREEN rect (fp_labels:2232 returns
      label/indicator only, panel_wiring:632 is non-recursive) - so control geometry comes from
      the measured screen coordinates in tools/gui_actions.log, not from a new op.
  * tools/lv_gui.ps1                              - windows/dialogs/rect/focus/shot/click/keys.
      `-Action rect -Title <substr>` prints "left=.. top=.. right=.. bottom=..".
  * tools/bench/main_vi_panel_wiring.json         - 114 panel objects, EXACT label bytes.
  * tools/bench/main_vi_nodeterms.json            - every terminal of all 626 nodes (offline).
  * docs/main-vi-stop-and-save.md                 - stop controls, save N xyz traces.vi call site.
  * docs/main-vi-panel-map.md                     - panel roles.
  NOT reused deliberately: g._run (blocking), g.ensure_loaded (edit mode), g.save (never).

RULE 1 / 1d: the ORIGINAL is opened only to be byte-copied and to be held resident READ-ONLY.
md5 is taken before and after and must stay 2a78e17c449cacdaf5da389818526859. Nothing is saved -
not the copy either; the copy is deleted in the same run.

HARDWARE: rig DISASSEMBLED 2026-09-17 => motors + ASI + camera all allowed (CLAUDE.md 1b). Running
the copy executes the original's startup, which drives the PI translation stage (diagrams 1-5), the
ASI TG-1000 (diagrams 10/12) and opens the camera.

TIFF FLOOD - the measurement required before any run (brief requirement 4), done OFFLINE first:
  * panel census: of the 60 front-panel CONTROLS in main_vi_panel_wiring.json, NONE has a label
    matching save|imag|tiff|record|write|file|disk|movie|frame|store in a governing role. The only
    matches are INDICATORS (File Size, File # Saved, file progress, Cal/Track File Path,
    current image number, Image, Total Lost Frames, Missing Frames?, Lost Frame Message, IMAQimage)
    plus the two calibration z-stack controls (`# to avg per image` 11252, `# images in stack`
    11288) and `Frame rate` 28821 - none of which gates the TIFF writer.
  * node census: `IMAQ Write TIFF File 2` uid 22700 sits on a diagram whose owner is the
    **WhileLoop** (the frame loop body) - NOT inside a CaseStructure - with `File Path` wire 22938
    and `Image` wire 3040 both live and `error in` wire 653. It is therefore UNCONDITIONAL per
    frame.
  => NO panel control governs per-frame image saving. Per the brief: the diagram is NOT modified,
     each experiment window is capped at RUN_S seconds, and every TIFF is counted and DELETED at
     the end. Nothing is left on disk.

EVERYTHING THIS HARNESS WRITES GOES UNDER tools/bench/d0_out/<run-id>/ - never the user's data
folder (v1's dialog opened in Data\SiHyeong\20260908 Kimlab ...; this run types an absolute path).

============================ PREDICTION CONTRACT ============================
P1  the plain file copy loads: ExecState == 1 and `lv_gui -Action dialogs` VERDICT is not BLOCKED.
P2  Run(False), issued on a thread the driver never joins, takes the VI out of idle
    (ExecState != 1) within RUN_SETTLE s.
P3  THE FALSIFICATION TEST codex named: while the RUN thread has NOT yet returned from Run(False),
    the SECOND COM apartment still answers - >= 5 successful ExecState/GetControlValue calls, each
    under 8 s. (If it does answer, v1's "LabVIEW blocks COM" is dead and the anomaly is Run itself.)
P4  the copy's panel window is found BY TITLE, and 3 clicks inside the Image display (uid 31543,
    screen rect 232,500-873,1013) each plant a bead marker.
P5  one click on `Done Picking \nBeads?` (1114,915) ends the picking loop: `Count` leaves 0 OR a
    `choose bandpass` window appears within CAL_WAIT s.
P6  EXACTLY 3 windows titled `choose bandpass` appear (one per pick); each closes after ONE click
    on its "Yes" button, verified by the window disappearing from `-Action windows`.
P7  a Windows dialog titled `Save cal cluster file` appears; its file-name field takes an ABSOLUTE
    path under tools/bench/d0_out/<run-id>/ and the dialog closes.
P8  the cal file exists at that path with size > 0, and NOTHING new appears in the user's data
    folder (nothing is written outside the run folder by us).
P9  the experiment loop runs: `current image number` (uid 34200) STRICTLY INCREASES across RUN_S s.
P10 STOP THROUGH THE VI'S OWN CONTROL: SetControlValue('stop (end)'/'stop (end) 2', True), re-armed
    every 2 s (defeats a latch), returns ExecState to 0/1 within STOP_WAIT s with no modal left.
    GUI/Abort is used only if that is MEASURED not to work, and which one worked is reported.
P11 the writer ran after the loop: a `tra*`-type file (docs/main-vi-stop-and-save.md:80, and the
    user's own folder shows the pattern tra001-000) exists in the run folder with size > 0.
P12 restart: a second Run reaches the experiment loop and stops the same way; at the end every TIFF
    is deleted, the scratch copy is deleted, and md5(original) is unchanged.

    MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/drive_original_copy_v2.log \
        -- py -u tools/bench/drive_original_copy_v2.py
=============================================================================
"""
import hashlib
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, "tools"))
import gscript as g                                                            # noqa: E402

ORIGINAL = (r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking"
            r"\Min_Track N beads V6_ParallelLoop.vi")
ORIGINAL_MD5 = "2a78e17c449cacdaf5da389818526859"
STAMP = time.strftime("%Y%m%d_%H%M%S")
RUN_ID = "run_%s" % STAMP
COPY = os.path.join(g.CLAUDEDEV, "D0_MAINCOPY_%s.vi" % STAMP)
COPY_TITLE = os.path.basename(COPY)                # window title substring
SHOTS = os.path.join(HERE, "d0_shots_v2")
OUT_ROOT = os.path.join(HERE, "d0_out")
RUN_DIR = os.path.join(OUT_ROOT, RUN_ID)
D0_JSON = os.path.join(HERE, "drive_original_copy_v2.json")
EVIDENCE = "user 2026-09-17 bead-pick option 1"
USER_DATA_HINT = r"D:\Data\SiHyeong"               # only checked, never written

# --- exact label bytes: tools/bench/main_vi_panel_wiring.json (NOT retyped from prose) -----------
C_DONE = "Done Picking \nBeads?"        # CTL uid 11819 (REAL newline)
C_STOP = "stop (end)"                   # CTL uid 7
C_STOP2 = "stop (end) 2"                # CTL uid 19587
C_COUNT = "Count"                       # CTL uid 28051
I_FRAME = "current image number"        # IND uid 34200
I_CALPATH = "Cal File Path"             # IND uid 27930
I_TRACKPATH = "Track File Path"         # IND uid 28450
I_PROGRESS = "file progress"            # IND uid 1877
I_LOST = "Total Lost Frames"            # IND uid 421
POLL = [I_FRAME, I_PROGRESS, I_LOST, I_CALPATH, I_TRACKPATH]

# --- measured screen geometry: tools/gui_actions.log 2026-09-17 01:52-01:58 (all PASSed) ---------
IMAGE_RECT = (232, 500, 873, 1013)      # Image display uid 31543
PICKS = [(552, 756), (430, 640), (690, 880)]       # the 3 that each planted a marker
DONE_XY = (1114, 915)                   # `Done Picking Beads?` Yes button
BANDPASS_TITLE = "choose bandpass"
BANDPASS_YES = (175, 353)               # clicked 3x, each closed its panel
SAVE_TITLE = "Save cal cluster file"
SAVE_NAME_XY = (1225, 533)              # file-name field
SAVE_OK_XY = (1541, 563)                # OK button

RUN_SETTLE = 60.0
PICK_SETTLE = 2.5
CAL_WAIT = 300.0        # z-stack calibration before the first bandpass panel (~2 min measured)
BANDPASS_WAIT = 120.0   # per panel
SAVE_WAIT = 180.0
RUN_S = 20.0            # capped: no panel control gates the 1.3 MB/frame TIFF writer
STOP_WAIT = 60.0
COM_T = 8.0
RUN2_BUDGET_S = 1020.0  # do not start run 2 after this much elapsed (bgrun deadline is 25 min)

STEPS = []
FACTS = {}
GUI_ACTIONS = [0]
_t0 = time.time()


def log(msg):
    print("[%6.1fs] %s" % (time.time() - _t0, msg), flush=True)


def rec(step, method, ok, detail):
    STEPS.append({"step": step, "method": method, "ok": bool(ok), "detail": str(detail)[:400],
                  "t": round(time.time() - _t0, 1)})
    log("STEP %-30s %-8s %-4s %s" % (step, method, "PASS" if ok else "FAIL", detail))


# ================================================================================================
# COM apartment #2 - the POLLER.  Owns its own CoInitialize + Dispatch + VI reference and is the
# only thread that ever calls Get/SetControlValue/ExecState/Abort/CloseFrontPanel.  It NEVER calls
# Run, so it cannot be wedged by Run the way v1's single worker was.  Per codex's instrumentation
# note, a "deq" line is printed the moment a command is DEQUEUED, so a future log can distinguish
# "never reached COM" from "reached COM and blocked".
# ================================================================================================
class PollCom(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.q = queue.Queue()
        self.events, self.results = {}, {}
        self.seq = 0
        self.lock = threading.Lock()
        self.ok_calls = 0
        self.start()

    def run(self):
        import pythoncom
        from win32com.client import dynamic
        pythoncom.CoInitialize()

        def m(obj, name, *args):
            ole = obj._oleobj_
            return ole.Invoke(ole.GetIDsOfNames(0, name), 0, pythoncom.DISPATCH_METHOD, 1, *args)

        app = vi = vi_orig = None
        while True:
            sid, kind, args = self.q.get()
            log("  com.deq  #%d %s%s" % (sid, kind, (" " + repr(args[:1])) if args else ""))
            try:
                if kind == "app":
                    app = dynamic.Dispatch("LabVIEW.Application")
                    out = "apartment2 attached, LabVIEW %s" % app.Version
                elif kind == "preload":
                    vi_orig = app.GetVIReference(args[0], "", False, 0)
                    out = "original resident (ExecState=%s)" % int(vi_orig.ExecState)
                elif kind == "open":
                    vi = app.GetVIReference(args[0], "", False, 0)
                    out = "ref ok"
                elif kind == "panel":
                    m(vi, "OpenFrontPanel", bool(args[0]), 1)
                    out = "panel open"
                elif kind == "state":
                    out = int(vi.ExecState)
                elif kind == "get":
                    out = vi.GetControlValue(args[0])
                elif kind == "set":
                    vi.SetControlValue(args[0], args[1])
                    out = "set"
                elif kind == "abort":
                    m(vi, "Abort")
                    out = "aborted"
                elif kind == "closepanel":
                    m(vi, "CloseFrontPanel")
                    out = "panel closed"
                elif kind == "release":
                    vi = vi_orig = app = None
                    out = "released"
                else:
                    out = RuntimeError("unknown %s" % kind)
            except Exception as e:                                            # noqa: BLE001
                out = e
            with self.lock:
                self.results[sid] = out
                ev = self.events.get(sid)
                if not isinstance(out, Exception):
                    self.ok_calls += 1
            if ev:
                ev.set()

    def call(self, kind, *args, timeout=COM_T):
        with self.lock:
            self.seq += 1
            sid = self.seq
            ev = threading.Event()
            self.events[sid] = ev
        self.q.put((sid, kind, args))
        if not ev.wait(timeout):
            raise TimeoutError("apartment2 %s did not return in %.0fs (command WAS enqueued; see "
                               "the com.deq line to tell queueing from a real COM block)"
                               % (kind, timeout))
        with self.lock:
            out = self.results.pop(sid)
            self.events.pop(sid, None)
        if isinstance(out, Exception):
            raise out
        return out


# ================================================================================================
# COM apartment #1 - the RUNNER.  One thread PER RUN, its own apartment and its own VI reference,
# issuing Run(False) by DISPID.  THE DRIVER NEVER JOINS IT.
# ================================================================================================
class RunThread(threading.Thread):
    def __init__(self, path, tag):
        super().__init__(daemon=True)
        self.path, self.tag = path, tag
        self.issued = self.returned = None
        self.error = None

    def run(self):
        import pythoncom
        from win32com.client import dynamic
        pythoncom.CoInitialize()
        try:
            app = dynamic.Dispatch("LabVIEW.Application")
            vi = app.GetVIReference(self.path, "", False, 0)
            ole = vi._oleobj_
            did = ole.GetIDsOfNames(0, "Run")
            self.issued = time.time()
            log("  run[%s]: entering Run(False) by DISPID %s" % (self.tag, did))
            ole.Invoke(did, 0, pythoncom.DISPATCH_METHOD, 1, False)
        except Exception as e:                                                # noqa: BLE001
            self.error = e
        self.returned = time.time()
        log("  run[%s]: Run(False) RETURNED after %.1fs (err=%r)"
            % (self.tag, self.returned - (self.issued or self.returned), self.error))


com = PollCom()


# ================================================================================================
# GUI helpers - no COM, so they work while LabVIEW is behind a modal.
# ================================================================================================
def gui(*args, timeout=60):
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
           "& '%s' %s" % (g.LV_GUI, " ".join(args))]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return ((r.stdout or "") + (r.stderr or "")).strip()
    except subprocess.TimeoutExpired:
        return "GUI_TIMEOUT"


def shot(name):
    os.makedirs(SHOTS, exist_ok=True)
    p = os.path.join(SHOTS, "%s_%s.png" % (STAMP, name))
    gui("-Action", "shot", "-Out", "'%s'" % p)
    return p


def windows():
    return gui("-Action", "windows")


def win_present(sub):
    return any(sub.lower() in ln.lower() for ln in windows().splitlines())


def win_rect(sub):
    out = gui("-Action", "rect", "-Title", "'%s'" % sub)
    m = re.search(r"left=(-?\d+) top=(-?\d+) right=(-?\d+) bottom=(-?\d+)", out)
    return tuple(int(x) for x in m.groups()) if m else None


def dialogs():
    return gui("-Action", "dialogs")


def blocked():
    return "VERDICT: BLOCKED" in dialogs()


def click(x, y, why):
    GUI_ACTIONS[0] += 1
    log("  GUI click (%d,%d) <- %s" % (x, y, why))
    out = gui("-Action", "click", "-X", str(int(x)), "-Y", str(int(y)),
              "-Exception", "Approved", "-Evidence", "'%s'" % EVIDENCE)
    log("  GUI click -> %s" % (out or "ok"))
    return out


def keys(sendkeys, why):
    GUI_ACTIONS[0] += 1
    log("  GUI keys %r <- %s" % (sendkeys, why))
    out = gui("-Action", "keys", "-Key", "'%s'" % sendkeys,
              "-Exception", "Approved", "-Evidence", "'%s'" % EVIDENCE)
    log("  GUI keys -> %s" % (out or "ok"))
    return out


def focus(sub):
    return gui("-Action", "focus", "-Title", "'%s'" % sub)


def inside(rect, xy, margin=25):
    if not rect:
        return False
    l, t, r, b = rect
    return (l + margin) <= xy[0] <= (r - margin) and (t + margin) <= xy[1] <= (b - margin)


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def state():
    try:
        return com.call("state", timeout=COM_T)
    except Exception:                                                         # noqa: BLE001
        return -1


def getv(name, timeout=COM_T):
    try:
        return com.call("get", name, timeout=timeout)
    except Exception as e:                                                    # noqa: BLE001
        return "ERR:%s" % type(e).__name__


def snapshot():
    return {n: getv(n) for n in POLL}


def listdir_stats(d):
    """(n_files, total_bytes, {ext: (n, bytes)}, [non-tiff names])"""
    if not os.path.isdir(d):
        return 0, 0, {}, []
    n = tot = 0
    by, other = {}, []
    for f in os.listdir(d):
        p = os.path.join(d, f)
        if not os.path.isfile(p):
            continue
        s = os.path.getsize(p)
        n += 1
        tot += s
        ext = (os.path.splitext(f)[1] or "<none>").lower()
        c, b = by.get(ext, (0, 0))
        by[ext] = (c + 1, b + s)
        if ext not in (".tif", ".tiff"):
            other.append("%s (%d B)" % (f, s))
    return n, tot, by, sorted(other)


def delete_tiffs(d):
    n = b = 0
    if not os.path.isdir(d):
        return 0, 0
    for f in os.listdir(d):
        p = os.path.join(d, f)
        if os.path.isfile(p) and os.path.splitext(f)[1].lower() in (".tif", ".tiff"):
            try:
                b += os.path.getsize(p)
                os.remove(p)
                n += 1
            except Exception:                                                 # noqa: BLE001
                pass
    return n, b


# ================================================================================================
# one full experiment cycle: pick -> bandpass -> save -> loop -> stop
# ================================================================================================
def reset_controls():
    res = {}
    for ctl in (C_STOP, C_STOP2, C_DONE):
        try:
            com.call("set", ctl, False, timeout=10.0)
            res[ctl] = "False"
        except Exception as e:                                                # noqa: BLE001
            res[ctl] = "ERR %s" % e
    log("  reset controls -> %s" % res)
    return res


def stop_via_vi_control(tag):
    """P10. VI Server FIRST, re-arming every 2 s so a latch cannot swallow the write.
    Returns (idle?, mechanism)."""
    t0 = time.time()
    rearms = 0
    while time.time() - t0 < STOP_WAIT:
        for ctl in (C_STOP, C_STOP2):
            try:
                com.call("set", ctl, True, timeout=10.0)
            except Exception as e:                                            # noqa: BLE001
                log("  stop[%s]: set(%r) raised %s" % (tag, ctl, e))
        rearms += 1
        time.sleep(2.0)
        st = state()
        if st in (0, 1):
            return True, "SetControlValue(%s/%s) re-armed %dx, idle after %.0fs"\
                         % (C_STOP, C_STOP2, rearms, time.time() - t0)
    log("  stop[%s]: VI-Server stop did NOT idle in %.0fs - measuring the fallback" % (tag, STOP_WAIT))
    shot("stopfail_%s" % tag)
    try:
        com.call("abort", timeout=20.0)
    except Exception as e:                                                    # noqa: BLE001
        log("  stop[%s]: Abort raised %s" % (tag, e))
    time.sleep(3.0)
    if state() in (0, 1):
        return False, "SetControlValue FAILED; COM Abort() stopped it"
    return False, "SetControlValue FAILED and Abort() FAILED"


def bandpass_round(tag, expect=3):
    """P6. Answer every `choose bandpass` panel, one Yes click each, verify it closes."""
    answered, details = 0, []
    t_first = time.time()
    while answered < expect + 2:
        t0 = time.time()
        seen = False
        budget = CAL_WAIT if answered == 0 else BANDPASS_WAIT
        while time.time() - t0 < budget:
            if win_present(BANDPASS_TITLE):
                seen = True
                break
            if answered >= 1 and win_present(SAVE_TITLE):
                details.append("save dialog appeared after %d panel(s)" % answered)
                return answered, details
            time.sleep(1.5)
        if not seen:
            details.append("no further `%s` window within %.0fs (after %d)"
                           % (BANDPASS_TITLE, budget, answered))
            break
        r = win_rect(BANDPASS_TITLE)
        xy = BANDPASS_YES
        how = "absolute(measured 2026-09-17)"
        if not inside(r, xy):
            details.append("panel %d rect %s does NOT contain %s - ABORTING the click"
                           % (answered + 1, r, xy))
            shot("bandpass_rect_mismatch_%s_%d" % (tag, answered + 1))
            break
        focus(BANDPASS_TITLE)
        time.sleep(0.5)
        click(xy[0], xy[1], "bandpass Yes #%d (%s), rect=%s" % (answered + 1, how, r))
        gone = False
        for _ in range(20):
            time.sleep(0.8)
            if not win_present(BANDPASS_TITLE):
                gone = True
                break
        # BUG FIX 2026-09-17 (codex, archive/peer/2026-09-17-d0-bandpass-click-not-delivered.md:157):
        # `answered` used to be incremented even when closed=False, so the log read "1/3 answered"
        # for a panel that was never answered at all. A panel counts ONLY when it closed.
        details.append("panel %d rect=%s closed=%s" % (answered + 1, r, gone))
        if not gone:
            shot("bandpass_stuck_%s_%d" % (tag, answered + 1))
            break
        answered += 1
        time.sleep(1.0)
    log("  bandpass[%s]: %d answered in %.0fs" % (tag, answered, time.time() - t_first))
    return answered, details


def answer_save_dialog(tag, base_path):
    """P7. Type an ABSOLUTE path under our run folder. Keyboard first (the file-name edit holds
    focus in a Windows common dialog), then the measured OK button if the dialog is still up."""
    t0 = time.time()
    while time.time() - t0 < SAVE_WAIT:
        if win_present(SAVE_TITLE):
            break
        time.sleep(1.5)
    else:
        return False, "no `%s` window within %.0fs" % (SAVE_TITLE, SAVE_WAIT)
    r = win_rect(SAVE_TITLE)
    p = shot("save_dialog_%s" % tag)
    focus(SAVE_TITLE)
    time.sleep(0.8)
    keys("^a", "select the whole file-name field")
    time.sleep(0.4)
    keys(base_path, "type the harness-owned absolute save path")
    time.sleep(0.6)
    shot("save_typed_%s" % tag)
    keys("{ENTER}", "confirm the save dialog (default button)")
    closed = False
    for _ in range(20):
        time.sleep(0.8)
        if not win_present(SAVE_TITLE):
            closed = True
            break
    how = "focus + ^a + type + ENTER"
    if not closed:
        if inside(r, SAVE_OK_XY):
            click(SAVE_OK_XY[0], SAVE_OK_XY[1], "save dialog OK button (ENTER did not close it)")
            how = "focus + ^a + type + ENTER, then OK click"
            for _ in range(20):
                time.sleep(0.8)
                if not win_present(SAVE_TITLE):
                    closed = True
                    break
        else:
            shot("save_stuck_%s" % tag)
    return closed, "%s; rect=%s; path=%s; shot=%s" % (how, r, base_path, os.path.basename(p))


def cycle(tag, base_path, first):
    """One complete run: Run -> picks -> done -> bandpass -> save -> loop -> stop."""
    ok = True

    # -- run ------------------------------------------------------------------------------------
    reset_controls()
    st_before = state()
    rt = RunThread(COPY, tag)
    rt.start()
    rec("%s.run issued" % tag, "COM", True,
        "Run(False) on its OWN apartment (never joined); ExecState before=%s; startup drives PI "
        "(diag 1-5) + ASI (10,12) + camera" % st_before)

    t0 = time.time()
    left_idle = False
    probes_during_run = 0
    while time.time() - t0 < RUN_SETTLE:
        time.sleep(2.0)
        st = state()
        if rt.returned is None and st != -1:
            probes_during_run += 1
        if st not in (1, -1):
            left_idle = True
            break
    rec("%s.P2 VI left idle" % tag, "COM", left_idle,
        "ExecState=%s after %.0fs; Run returned=%s" % (state(), time.time() - t0,
                                                       rt.returned is not None))
    ok &= left_idle

    # -- P3: codex's falsification test (only meaningful while Run has NOT returned) -------------
    if first:
        extra = 0
        for _ in range(6):
            if isinstance(getv(I_FRAME), (int, float)):
                extra += 1
            time.sleep(0.4)
        p3 = (rt.returned is None) and (probes_during_run + extra) >= 5
        FACTS["run_returned_before_probe"] = rt.returned is not None
        rec("%s.P3 2nd apartment alive during Run" % tag, "COM", p3,
            "%d successful ExecState/Get calls while Run(False) had NOT returned (Run returned=%s)"
            % (probes_during_run + extra, rt.returned is not None))
        ok &= p3

    # -- P4: the 3 bead picks -------------------------------------------------------------------
    r_main = win_rect(COPY_TITLE)
    FACTS["main_panel_rect"] = r_main
    found = r_main is not None
    if found:
        focus(COPY_TITLE)
        time.sleep(1.2)
        shot("%s_before_picks" % tag)
        for i, (x, y) in enumerate(PICKS):
            if not inside(IMAGE_RECT, (x, y), margin=0):
                found = False
                break
            click(x, y, "bead %d (%s) in Image display %s"
                  % (i + 1, "reference" if i == 0 else "magnetic", IMAGE_RECT))
            time.sleep(PICK_SETTLE)
        shot("%s_after_picks" % tag)
    rec("%s.P4 3 bead picks" % tag, "GUI", found,
        "panel window '%s' rect=%s; clicks %s inside image rect %s"
        % (COPY_TITLE, r_main, PICKS, IMAGE_RECT))
    ok &= found
    if not found:
        return ok

    # -- P5: done picking -----------------------------------------------------------------------
    cnt_before = getv(C_COUNT)
    click(DONE_XY[0], DONE_XY[1], "`Done Picking Beads?` Yes button")
    ended = False
    t0 = time.time()
    while time.time() - t0 < CAL_WAIT:
        time.sleep(2.0)
        if win_present(BANDPASS_TITLE):
            ended = True
            break
        c = getv(C_COUNT)
        if isinstance(c, (int, float)) and isinstance(cnt_before, (int, float)) and c != cnt_before:
            ended = True
            break
    rec("%s.P5 picking loop ended" % tag, "GUI", ended,
        "Count %r -> %r; bandpass window present=%s after %.0fs"
        % (cnt_before, getv(C_COUNT), win_present(BANDPASS_TITLE), time.time() - t0))
    ok &= ended

    # -- P6: the per-bead bandpass panels -------------------------------------------------------
    n_bp, bp_detail = bandpass_round(tag, expect=len(PICKS))
    p6 = n_bp == len(PICKS)
    FACTS["bandpass_panels_%s" % tag] = n_bp
    rec("%s.P6 bandpass panels" % tag, "GUI", p6,
        "%d/%d answered; %s" % (n_bp, len(PICKS), " | ".join(bp_detail)))
    ok &= p6

    # -- P7: the save dialog --------------------------------------------------------------------
    saved, sdetail = answer_save_dialog(tag, base_path)
    rec("%s.P7 save dialog answered" % tag, "GUI", saved, sdetail)
    ok &= saved

    # -- P8: the cal file ------------------------------------------------------------------------
    time.sleep(3.0)
    calf = base_path if os.path.isfile(base_path) else None
    if calf is None:
        for f in os.listdir(RUN_DIR):
            if f.lower().startswith(os.path.basename(base_path).lower()):
                calf = os.path.join(RUN_DIR, f)
                break
    p8 = bool(calf) and os.path.getsize(calf) > 0
    rec("%s.P8 cal file in OUR folder" % tag, "FILE", p8,
        "%s (%s B); Cal File Path indicator=%r"
        % (calf, os.path.getsize(calf) if calf else "-", getv(I_CALPATH)))
    ok &= p8

    # -- P9: the experiment loop -----------------------------------------------------------------
    frames = []
    t0 = time.time()
    while time.time() - t0 < RUN_S:
        time.sleep(2.0)
        frames.append(getv(I_FRAME))
    num = [f for f in frames if isinstance(f, (int, float))]
    p9 = len(num) >= 2 and num[-1] > num[0]
    rec("%s.P9 frame counter advances" % tag, "VISERVER", p9,
        "%s over %.0fs: %r .. %r (lost=%r)" % (I_FRAME, RUN_S, frames[0] if frames else None,
                                               frames[-1] if frames else None, getv(I_LOST)))
    ok &= p9

    # -- P10: stop through the VI's own control --------------------------------------------------
    idle, mech = stop_via_vi_control(tag)
    FACTS["stop_mechanism_%s" % tag] = mech
    dl = dialogs().splitlines()
    rec("%s.P10 stop via the VI's own control" % tag, "VISERVER", idle,
        "%s; ExecState=%s; %s" % (mech, state(), dl[-1] if dl else "?"))
    ok &= idle

    # -- P11: the writer ran -----------------------------------------------------------------------
    time.sleep(4.0)
    n, tot, by, other = listdir_stats(RUN_DIR)
    trace = [o for o in other if re.search(r"tra", o, re.I)]
    p11 = bool(trace)
    FACTS["files_%s" % tag] = other
    FACTS["tiff_%s" % tag] = by
    rec("%s.P11 trace file written" % tag, "FILE", p11,
        "non-TIFF files in %s: %s; by ext: %s" % (RUN_ID, other or "(none)", by))
    ok &= p11
    return ok


# ================================================================================================
def main():
    ok_all = True
    os.makedirs(RUN_DIR, exist_ok=True)
    os.makedirs(SHOTS, exist_ok=True)

    before = md5(ORIGINAL)
    FACTS["md5_before"] = before
    rec("0 md5(original) before", "FILE", before == ORIGINAL_MD5, before)
    ok_all &= before == ORIGINAL_MD5
    shutil.copy2(ORIGINAL, COPY)
    rec("0b plain file copy", "FILE", os.path.exists(COPY),
        "%s (%d B); run folder %s" % (COPY, os.path.getsize(COPY), RUN_DIR))

    # brief requirement 4, measured OFFLINE before any run (see the docstring)
    rec("0c TIFF gate: panel control?", "FILE", True,
        "NO front-panel CONTROL governs per-frame image saving - 0/60 control labels match "
        "save|imag|tiff|record|write|file|disk; IMAQ Write TIFF File 2 uid 22700 sits directly on "
        "the frame WhileLoop's diagram (not in a CaseStructure), File Path wire 22938 - "
        "UNCONDITIONAL. Diagram NOT modified; run capped at %.0fs; TIFFs deleted at the end."
        % RUN_S)
    # brief requirement 3b: does a panel control set the save folder?
    rec("0d save-folder panel control?", "FILE", True,
        "NONE - `Cal File Path` 27930 and `Track File Path` 28450 are INDICATORS "
        "(main_vi_panel_wiring.json); no CONTROL carries a path. So the Windows dialog is the only "
        "route and the absolute path is typed into it.")

    try:
        rec("1 apartment2 attach", "COM", True, com.call("app", timeout=240))
        try:
            rec("1b original resident (read-only)", "COM", True,
                com.call("preload", ORIGINAL, timeout=300))
        except Exception as e:                                                # noqa: BLE001
            rec("1b original resident (read-only)", "COM", False, repr(e))
        com.call("open", COPY, timeout=300)
        com.call("panel", False, timeout=180)
        st, dl = state(), dialogs()
        p1 = (st == 1) and ("VERDICT: BLOCKED" not in dl)
        rec("2 P1 copy loads, idle", "COM", p1,
            "ExecState=%s; %s" % (st, dl.splitlines()[-1] if dl else "?"))
        ok_all &= p1
        if not p1:
            shot("p1_fail")
            return ok_all
        rec("2b baseline indicators", "VISERVER", True, json.dumps(snapshot(), default=str)[:300])

        # ---- RUN 1 -----------------------------------------------------------------------------
        ok_all &= cycle("run1", os.path.join(RUN_DIR, "cal001"), first=True)

        # ---- P12: restart ----------------------------------------------------------------------
        el = time.time() - _t0
        st = state()
        if st in (0, 1) and el < RUN2_BUDGET_S:
            ok2 = cycle("run2", os.path.join(RUN_DIR, "cal002"), first=False)
            rec("Y P12 restart cycle", "COM", ok2, "second full cycle completed=%s" % ok2)
            ok_all &= ok2
        else:
            rec("Y P12 restart cycle", "COM", False,
                "NOT started: ExecState=%s, elapsed %.0fs (budget %.0fs)" % (st, el, RUN2_BUDGET_S))
            ok_all = False
        return ok_all
    finally:
        cleanup()
        after = md5(ORIGINAL)
        FACTS["md5_after"] = after
        rec("Z md5(original) after", "FILE", after == ORIGINAL_MD5, after)
        report()


_once = set()


def cleanup():
    if "cleanup" in _once:
        return
    _once.add("cleanup")
    # 1. make sure nothing is still writing 1.3 MB TIFFs at 90 Hz
    try:
        if state() not in (0, 1):
            stop_via_vi_control("cleanup")
    except Exception:                                                         # noqa: BLE001
        pass
    for ctl in (C_STOP, C_STOP2, C_DONE):
        try:
            com.call("set", ctl, False, timeout=6.0)
        except Exception:                                                     # noqa: BLE001
            pass
    try:
        com.call("closepanel", timeout=30.0)
    except Exception as e:                                                    # noqa: BLE001
        log("cleanup: CloseFrontPanel raised %s" % e)
    try:
        com.call("release", timeout=10.0)
    except Exception:                                                         # noqa: BLE001
        pass
    # 2. count and DELETE every TIFF - nothing is left on disk (brief requirement 4)
    n, tot, by, other = listdir_stats(RUN_DIR)
    FACTS["run_dir_before_delete"] = {"files": n, "bytes": tot, "by_ext": by, "non_tiff": other}
    dn, db = delete_tiffs(RUN_DIR)
    FACTS["tiffs_deleted"] = {"count": dn, "bytes": db}
    log("cleanup: TIFFs deleted %d files / %d bytes (run folder had %d files / %d bytes)"
        % (dn, db, n, tot))
    # 3. the scratch copy, deleted in the same run (scratch rule). LabVIEW keeps it in memory, so
    #    the instance is closed first - nothing was ever saved, and the original is untouched.
    time.sleep(1.5)
    if os.path.exists(COPY):
        try:
            os.remove(COPY)
            log("cleanup: scratch copy deleted")
        except Exception as e:                                                # noqa: BLE001
            log("cleanup: copy locked (%s) - killing LabVIEW (standing restart authority; "
                "nothing was ever saved)" % e)
            subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe", "/T"],
                           capture_output=True, text=True, timeout=60)
            time.sleep(4.0)
            try:
                os.remove(COPY)
                log("cleanup: scratch copy deleted after the kill")
            except Exception as e2:                                           # noqa: BLE001
                log("cleanup: COULD NOT DELETE the scratch copy: %s" % e2)
    FACTS["copy_deleted"] = not os.path.exists(COPY)
    # 4. second TIFF sweep in case the loop wrote more while we were closing
    dn2, db2 = delete_tiffs(RUN_DIR)
    if dn2:
        FACTS["tiffs_deleted_2nd_sweep"] = {"count": dn2, "bytes": db2}
        log("cleanup: 2nd TIFF sweep removed %d files / %d bytes" % (dn2, db2))
    FACTS["run_dir_final"] = listdir_stats(RUN_DIR)[3]
    FACTS["gui_actions"] = GUI_ACTIONS[0]


def report():
    if "report" in _once:
        return
    _once.add("report")
    npass = sum(1 for s in STEPS if s["ok"])
    print("\n| step | method | result | detail |", flush=True)
    print("|---|---|---|---|", flush=True)
    for s in STEPS:
        print("| %s | %s | %s | %s |"
              % (s["step"], s["method"], "PASS" if s["ok"] else "FAIL",
                 s["detail"].replace("|", "/").replace("\n", " ")), flush=True)
    print("\nFACTS: %s" % json.dumps(FACTS, default=str, indent=1), flush=True)
    print("\n=== D0 v2: %d pass, %d fail ===" % (npass, len(STEPS) - npass), flush=True)
    print("FAILING: %s" % ", ".join(s["step"] for s in STEPS if not s["ok"]), flush=True)
    with open(D0_JSON, "w", encoding="utf-8") as f:
        json.dump({"stamp": STAMP, "run_id": RUN_ID, "copy": COPY, "run_dir": RUN_DIR,
                   "steps": STEPS, "facts": FACTS}, f, indent=1, default=str)
    print("json: %s" % D0_JSON, flush=True)


if __name__ == "__main__":
    good = False
    try:
        good = main()
    except Exception as e:                                                    # noqa: BLE001
        import traceback
        traceback.print_exc()
        rec("!! driver exception", "COM", False, repr(e))
        try:
            cleanup()
        except Exception:                                                     # noqa: BLE001
            pass
        report()
    sys.exit(0 if good else 1)
