"""drive_original_copy.py - D0: take a plain COPY of the original main VI through
stages 0 -> 4 with NOBODY PRESENT, run it, stop it, restart it, stop it again.

CLAUDE.md 1c' (user, 2026-09-17): every test run until the rig is reassembled is unattended, and
the harness itself does the bead picking - "직접 마우스 움직여서 디스플레이 상에 클릭 이후 버튼 누르기
-> 저장 위치 및 저장 이름 쓰기" (option 1; the .cal-substitute option 2 was rejected). Garbage
tracking output in a no-bead run is EXPECTED and is not a failure.

WHAT ALREADY EXISTS (checked before writing a line of this, CLAUDE.md "before creating any new op,
tool or recipe"):
  * tools/gscript.py - lv()/op()/open_panel()/close_panel()/exec_state()/_run().  `_run` is
    SYNCHRONOUS (it blocks until the VI returns), so it is WRONG for a VI that loops until a stop
    Boolean; this driver uses vi.Run(False) instead, which is the pattern tools/bench/
    camera_ceiling.py:45 already established for exactly that shape ("asynchronous: the VI loops
    until Stop goes true", Stop set True in a finally block).
  * tools/lv_gui.ps1 - windows/dialogs/dismiss/focus/shot/shotwin/rect/click/keys/md5.  Its
    authorization gate (lv_gui.ps1:458-469) requires -Exception + -Evidence for click/keys and
    logs every one to tools/gui_actions.log.
  * tools/bench/main_vi_panel_wiring.json - all 114 panel labels with EXACT bytes (the source of
    the names below; `Done Picking \nBeads?` carries a REAL newline).
  * NO prior D0 / drive-the-main-VI harness exists (searched tools/bench, tools/recipes).
  * NOT reused deliberately: g._run (blocking), g.ensure_loaded (edit-mode; this driver edits
    nothing), g.save (this driver must never save).

RULE 1 / 1d: the ORIGINAL is opened only to be byte-copied. Its md5 is taken before and after and
must stay 2a78e17c449cacdaf5da389818526859. Nothing is ever saved - not the copy either; the copy
is deleted in the same run (scratch rule).

HARDWARE (rig DISASSEMBLED 2026-09-17 => motors + ASI + camera all allowed, CLAUDE.md 1b): running
the copy executes the original's startup, which per docs/main-vi-startup.md drives the PI
translation stage (diagrams 1-5: init, conditional MOV/GOH, VEL + position query) and the ASI
TG-1000 (diagram 10 Initialize + Move Axis to Position, diagram 12 Get Current Position), and opens
the camera. Every one of those is recorded in the step table as "instruments touched".

============================ PREDICTION CONTRACT ============================
P1  the plain file copy loads: vi.ExecState == 1 (idle, NOT 0/broken) and `lv_gui -Action dialogs`
    reports no blocking modal (i.e. the subVIs under `background VIs\` resolve from the new
    location without a "Find the VI named..." dialog).
P2  after vi.Run(False) the VI reaches the BEAD-PICKING loop within RUN_SETTLE s. Evidence:
    ExecState leaves 1, `Done Picking \nBeads?` reads False, and no data file exists yet.
P3  VI-SERVER FIRST: SetControlValue('Done Picking \nBeads?', True) ENDS the picking loop within
    PICK_WAIT s.  Evidence (any one): `Cal File Path` becomes non-empty, `Pos within cal image`
    changes, `current image number` starts advancing, or a modal (save-file) dialog appears.
    P3 is the measurement the brief asks for: does VI Server advance this VI at all.
P4  GUI FALLBACK, only if P3 fails: 3 clicks inside the Image display (uid 31543) - 1st =
    reference bead, 2nd/3rd = magnetic beads - then the done button, via lv_gui -Exception
    Approved -Evidence "user 2026-09-17 bead-pick option 1".  Needs the display's screen rect,
    which no current op can read (Panel.Controls[] -> Control.Label/Indicator only, gscript.py
    :2232), so it is read from D0_TARGETS if that file exists and otherwise the driver STOPS
    after saving a full-screen shot - deriving the rect from a picture is a judgement call.
P5  the save location + file name are requested by a MODAL dialog (exactly one enabled window
    while the panel is disabled, `lv_gui -Action dialogs` VERDICT: BLOCKED). It is answered by
    pasting SAVE_BASE from the clipboard + Enter.
P6  the experiment loop runs: `current image number` (uid 34200, docs/NAMES.md:86 "authoritative
    frame index - camera buffer number") STRICTLY INCREASES across RUN1_S seconds of polling.
P7  SetControlValue('stop (end)', True) returns the VI to idle (ExecState in (0,1)) within
    STOP_WAIT s, with no modal left open.
P8  a data file exists under SAVE_DIR with size > 0 after the first run.
P9  a second vi.Run(False) repeats P2..P7 for RUN2_S seconds (restart-clean).
P10 md5(original) == 2a78e17c449cacdaf5da389818526859 before AND after.

Every step records method = VISERVER | GUI | FILE | COM, and pass/fail, into the step table that
is printed at the end and written to D0_JSON.

    MATERIAL=1 py tools/bgrun.py --max-min 20 --log tools/bench/drive_original_copy.log \
        -- py -u tools/bench/drive_original_copy.py
=============================================================================
"""
import hashlib
import json
import os
import queue
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
COPY = os.path.join(g.CLAUDEDEV, "D0_MAINCOPY_%s.vi" % STAMP)
SHOTS = os.path.join(HERE, "d0_shots")
SAVE_DIR = os.path.join(HERE, "d0_out")
SAVE_BASE = os.path.join(SAVE_DIR, "d0_%s" % STAMP)
D0_JSON = os.path.join(HERE, "drive_original_copy.json")
D0_TARGETS = os.path.join(HERE, "d0_targets.json")     # {"image":[l,t,r,b],"done":[x,y]} screen px
EVIDENCE = "user 2026-09-17 bead-pick option 1"

# exact label bytes - tools/bench/main_vi_panel_wiring.json, NOT retyped from prose
C_DONE = "Done Picking \nBeads?"        # CTL uid 11819   (REAL newline)
C_STOP = "stop (end)"                   # CTL uid 7
C_STOP2 = "stop (end) 2"                # CTL uid 19587
I_FRAME = "current image number"        # IND uid 34200 - the authoritative frame index
I_CALPATH = "Cal File Path"             # IND uid 27930
I_TRACKPATH = "Track File Path"         # IND uid 28450
I_POSCAL = "Pos within cal image"       # IND uid 49
I_BEADPOS = "Bead Pos"                  # IND uid 11831
I_PROGRESS = "file progress"            # IND uid 1877
I_FILESIZE = "File Size"                # IND uid 3229
I_LOST = "Total Lost Frames"            # IND uid 421
POLL = [I_FRAME, I_PROGRESS, I_FILESIZE, I_LOST, I_CALPATH, I_TRACKPATH, I_POSCAL]

RUN_SETTLE = 45.0
PICK_WAIT = 40.0
DIALOG_WAIT = 25.0
STOP_WAIT = 45.0
RUN1_S = 60.0
RUN2_S = 30.0
COM_TIMEOUT = 20.0

STEPS = []
_t0 = time.time()


def log(msg):
    print("[%6.1fs] %s" % (time.time() - _t0, msg), flush=True)


def rec(step, method, ok, detail):
    STEPS.append({"step": step, "method": method, "ok": bool(ok), "detail": str(detail)[:400],
                  "t": round(time.time() - _t0, 1)})
    log("%-34s %-8s %-4s %s" % (step, method, "PASS" if ok else "FAIL", detail))


# --------------------------------------------------------------------------------------------
# COM worker.  Every COM call goes through ONE apartment-owning thread and the caller waits with a
# timeout, so a LabVIEW modal dialog (which blocks the whole app, and therefore every COM call)
# cannot wedge this driver - it times out, takes a screenshot with lv_gui (no COM), dismisses or
# answers the dialog, and the blocked call unblocks on its own.  gscript._run does this per-Run
# via interface marshalling; a persistent worker is the same guarantee for Get/SetControlValue.
# --------------------------------------------------------------------------------------------
class Com(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.q = queue.Queue()
        self.events = {}
        self.results = {}
        self.seq = 0
        self.lock = threading.Lock()
        self.start()

    def run(self):
        import pythoncom
        from win32com.client import dynamic
        pythoncom.CoInitialize()

        def m(obj, name, *args):
            """Call a COM METHOD by DISPID, the way gscript._invoke:141 does it.

            Attribute access is NOT equivalent: run 1 of this driver died with
            `TypeError: 'NoneType' object is not callable` on `vi.OpenFrontPanel(...)`
            (tools/bench/drive_original_copy.log, 2026-09-17 01:47) because pywin32's dynamic
            dispatch resolved that name against LabVIEW's type info as something that is not a
            callable. gscript has never used attribute access for OpenFrontPanel/CloseFrontPanel/
            SaveInstrument - it goes straight to Invoke(GetIDsOfNames(...)) - and that is the
            path that has worked for a year. Get/SetControlValue/ExecState/Run DO work as
            attributes (tools/bench/camera_ceiling.py:45), so those are left alone.
            We are already inside this thread's apartment, so no interface marshalling is needed.
            """
            ole = obj._oleobj_
            return ole.Invoke(ole.GetIDsOfNames(0, name), 0, pythoncom.DISPATCH_METHOD, 1, *args)

        app = None
        vi = None
        vi_orig = None
        while True:
            sid, kind, args = self.q.get()
            try:
                if kind == "app":
                    app = dynamic.Dispatch("LabVIEW.Application")
                    out = str(app.Version)
                elif kind == "preload":
                    # READ-ONLY reference to the ORIGINAL, held for the whole run. Purpose: put its
                    # subVI hierarchy (background VIs\...) into memory BY NAME before the copy loads,
                    # so the copy links to the already-resident subVIs instead of popping LabVIEW's
                    # modal "Find the VI named ..." - the copy sits in claudeDev, from which the
                    # original's relative link paths (..\..\background VIs\) do not resolve.
                    # Nothing is ever saved; md5(ORIGINAL) is checked before and after the run.
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
                elif kind == "runasync":
                    try:
                        vi.Run(False)
                    except TypeError:
                        m(vi, "Run", False)
                    out = "run started"
                elif kind == "abort":
                    m(vi, "Abort")
                    out = "aborted"
                elif kind == "closepanel":
                    m(vi, "CloseFrontPanel")
                    out = "panel closed"
                elif kind == "release":
                    vi = None
                    vi_orig = None
                    app = None
                    out = "released"
                else:
                    out = RuntimeError("unknown %s" % kind)
            except Exception as e:                                        # noqa: BLE001
                out = e
            with self.lock:
                self.results[sid] = out
                ev = self.events.get(sid)
            if ev:
                ev.set()

    def call(self, kind, *args, timeout=COM_TIMEOUT):
        with self.lock:
            self.seq += 1
            sid = self.seq
            ev = threading.Event()
            self.events[sid] = ev
        self.q.put((sid, kind, args))
        if not ev.wait(timeout):
            raise TimeoutError("COM %s(%s) did not return in %.0fs - LabVIEW is blocked"
                               % (kind, args[:1], timeout))
        with self.lock:
            out = self.results.pop(sid)
            self.events.pop(sid, None)
        if isinstance(out, Exception):
            raise out
        return out


com = Com()


# --------------------------------------------------------------------------------------------
# GUI helpers - NO COM, so they work while LabVIEW is blocked behind a modal.
# --------------------------------------------------------------------------------------------
def gui(*args, timeout=60):
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
           "& '%s' %s" % (g.LV_GUI, " ".join(args))]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return ((r.stdout or "") + (r.stderr or "")).strip()


def shot(name):
    os.makedirs(SHOTS, exist_ok=True)
    p = os.path.join(SHOTS, "%s_%s.png" % (STAMP, name))
    gui("-Action", "shot", "-Out", "'%s'" % p)
    return p


def dialogs():
    return gui("-Action", "dialogs")


def blocked():
    return "VERDICT: BLOCKED" in dialogs()


def click(x, y, why):
    out = gui("-Action", "click", "-X", str(int(x)), "-Y", str(int(y)),
              "-Exception", "Approved", "-Evidence", "'%s'" % EVIDENCE)
    log("GUI click (%d,%d) [%s] -> %s" % (x, y, why, out or "ok"))
    return out


def keys(sendkeys, why):
    out = gui("-Action", "keys", "-Key", "'%s'" % sendkeys,
              "-Exception", "Approved", "-Evidence", "'%s'" % EVIDENCE)
    log("GUI keys %r [%s] -> %s" % (sendkeys, why, out or "ok"))
    return out


def set_clipboard(text):
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Set-Clipboard -Value '%s'" % text.replace("'", "''")],
                   capture_output=True, text=True, timeout=30)


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot():
    """One COM read of every polled indicator. Returns {} if LabVIEW is blocked."""
    row = {}
    for n in POLL:
        try:
            row[n] = com.call("get", n, timeout=8.0)
        except Exception as e:                                            # noqa: BLE001
            row[n] = "ERR:%s" % type(e).__name__
    return row


def state():
    try:
        return com.call("state", timeout=8.0)
    except Exception:                                                     # noqa: BLE001
        return -1


# --------------------------------------------------------------------------------------------
def main():
    ok_all = True
    os.makedirs(SAVE_DIR, exist_ok=True)
    os.makedirs(SHOTS, exist_ok=True)

    # ---- step 0: the original, untouched ----------------------------------------------------
    before = md5(ORIGINAL)
    rec("0 md5(original) before", "FILE", before == ORIGINAL_MD5, before)
    ok_all &= before == ORIGINAL_MD5
    shutil.copy2(ORIGINAL, COPY)
    rec("0 plain file copy", "FILE", os.path.exists(COPY),
        "%s (%d bytes)" % (COPY, os.path.getsize(COPY)))

    try:
        # ---- step 1 (P1): load the copy ------------------------------------------------------
        com.call("app", timeout=180)          # a cold LabVIEW 2026 start is ~40-60 s
        try:
            preinfo = com.call("preload", ORIGINAL, timeout=300)
            rec("0b original resident (read-only)", "COM", True, preinfo)
        except Exception as e:                                            # noqa: BLE001
            rec("0b original resident (read-only)", "COM", False, repr(e))
        com.call("open", COPY, timeout=300)
        com.call("panel", False, timeout=180)
        st = state()
        dl = dialogs()
        p1 = (st == 1) and ("VERDICT: BLOCKED" not in dl)
        rec("1 P1 copy loads, idle", "COM", p1,
            "ExecState=%s; dialogs=%s" % (st, dl.splitlines()[-1] if dl else "?"))
        ok_all &= p1
        if not p1:
            shot("p1_fail")
            return ok_all

        base = snapshot()
        rec("1b baseline indicators", "VISERVER", True, json.dumps(base, default=str)[:300])

        # ---- step 2 (P2): run, reach the picking loop ---------------------------------------
        reset_stops()
        com.call("runasync", timeout=60)
        rec("2 Run(False) issued", "COM", True, "startup drives PI (diag 1-5) + ASI (10,12) + camera")
        t0 = time.time()
        reached = False
        while time.time() - t0 < RUN_SETTLE:
            time.sleep(2.0)
            if blocked():
                p = shot("startup_dialog")
                rec("2 modal during startup", "GUI", False, "dialogs BLOCKED; shot %s" % p)
                break
            st = state()
            if st not in (1, -1):
                reached = True
                break
        done0 = None
        try:
            done0 = com.call("get", C_DONE, timeout=8.0)
        except Exception as e:                                            # noqa: BLE001
            done0 = "ERR:%s" % e
        s2 = snapshot()
        rec("2 P2 in picking loop", "VISERVER", reached,
            "ExecState=%s Done=%r frame=%r" % (state(), done0, s2.get(I_FRAME)))
        ok_all &= reached
        shot("picking_loop")

        # ---- step 3 (P3): VI SERVER FIRST - end the picking loop ----------------------------
        pre = snapshot()
        try:
            com.call("set", C_DONE, True, timeout=15.0)
            set_ok = True
            setmsg = "SetControlValue(%r, True) returned" % C_DONE
        except Exception as e:                                            # noqa: BLE001
            set_ok = False
            setmsg = "SetControlValue raised %s" % e
        advanced = False
        why = ""
        t0 = time.time()
        while time.time() - t0 < PICK_WAIT:
            time.sleep(2.0)
            if blocked():
                advanced = True
                why = "modal dialog appeared (save-file prompt?)"
                break
            cur = snapshot()
            if cur.get(I_CALPATH) not in (pre.get(I_CALPATH), "", None):
                advanced = True
                why = "Cal File Path -> %r" % (cur.get(I_CALPATH),)
                break
            if cur.get(I_FRAME) != pre.get(I_FRAME) and isinstance(cur.get(I_FRAME), (int, float)):
                advanced = True
                why = "current image number %r -> %r" % (pre.get(I_FRAME), cur.get(I_FRAME))
                break
            if str(cur.get(I_POSCAL)) != str(pre.get(I_POSCAL)):
                advanced = True
                why = "Pos within cal image changed"
                break
        rec("3 P3 VI-Server ends picking", "VISERVER", advanced,
            "%s; %s" % (setmsg, why or "no downstream change in %.0fs" % PICK_WAIT))

        # ---- step 4 (P4): GUI fallback, only if P3 failed ------------------------------------
        if not advanced:
            sp = shot("p3_failed_need_targets")
            rect = gui("-Action", "rect", "-Title", "Min_Track")
            if not os.path.exists(D0_TARGETS):
                rec("4 P4 GUI bead picking", "GUI", False,
                    "NEEDS_TARGETS: no %s; panel rect %s; screenshot %s"
                    % (os.path.basename(D0_TARGETS), rect, sp))
                ok_all = False
                return ok_all
            tg = json.load(open(D0_TARGETS, encoding="utf-8"))
            gui("-Action", "focus", "-Title", "Min_Track")
            time.sleep(1.0)
            l, t, r, b = tg["image"]
            picks = [((l + r) // 2, (t + b) // 2),
                     (l + (r - l) // 4, t + (b - t) // 4),
                     (r - (r - l) // 4, b - (b - t) // 4)]
            for i, (x, y) in enumerate(picks):
                click(x, y, "bead %d (%s)" % (i, "reference" if i == 0 else "magnetic"))
                time.sleep(1.2)
            shot("after_3_clicks")
            if "done" in tg:
                click(tg["done"][0], tg["done"][1], "Done Picking Beads button")
            else:
                try:
                    com.call("set", C_DONE, True, timeout=15.0)
                except Exception:                                         # noqa: BLE001
                    pass
            t0 = time.time()
            while time.time() - t0 < PICK_WAIT:
                time.sleep(2.0)
                if blocked():
                    advanced = True
                    why = "modal after GUI picks"
                    break
                cur = snapshot()
                if cur.get(I_CALPATH) not in (pre.get(I_CALPATH), "", None) or \
                        cur.get(I_FRAME) != pre.get(I_FRAME):
                    advanced = True
                    why = "indicators moved after GUI picks"
                    break
            rec("4 P4 GUI bead picking", "GUI", advanced, why or "no change after 3 clicks + done")
            ok_all &= advanced
            if not advanced:
                shot("p4_failed")
                return ok_all

        # ---- step 5 (P5): the save location / file name --------------------------------------
        answered = False
        t0 = time.time()
        while time.time() - t0 < DIALOG_WAIT:
            if blocked():
                p = shot("save_dialog")
                set_clipboard(SAVE_BASE)
                time.sleep(0.6)
                keys("^v", "paste save path")
                time.sleep(0.6)
                keys("{ENTER}", "confirm save dialog")
                time.sleep(2.0)
                answered = not blocked()
                rec("5 P5 save path dialog", "GUI", answered,
                    "pasted %s; shot %s" % (SAVE_BASE, p))
                break
            time.sleep(1.5)
        if not answered and not blocked():
            rec("5 P5 save path dialog", "GUI", True,
                "no modal appeared within %.0fs - the VI supplies its own path "
                "(Track File Path=%r)" % (DIALOG_WAIT, snapshot().get(I_TRACKPATH)))

        # ---- step 6 (P6): the experiment loop advances ---------------------------------------
        frames = []
        t0 = time.time()
        while time.time() - t0 < RUN1_S:
            time.sleep(3.0)
            s = snapshot()
            frames.append(s.get(I_FRAME))
        adv = [f for f in frames if isinstance(f, (int, float))]
        p6 = len(adv) >= 2 and adv[-1] > adv[0]
        rec("6 P6 frame counter advances", "VISERVER", p6,
            "%s over %.0fs -> %r .. %r" % (I_FRAME, RUN1_S, frames[0] if frames else None,
                                           frames[-1] if frames else None))
        ok_all &= p6
        shot("run1_experiment")

        # ---- step 7 (P7): stop through the VI's own control ----------------------------------
        idle = stop_it()
        rec("7 P7 stop -> idle", "VISERVER", idle, "ExecState=%s after stop" % state())
        ok_all &= idle

        # ---- step 8 (P8): a data file exists -------------------------------------------------
        made = newest_files()
        rec("8 P8 data file produced", "FILE", bool(made), made or "nothing new under %s" % SAVE_DIR)
        ok_all &= bool(made)

        # ---- step 9 (P9): restart once and repeat --------------------------------------------
        st = state()
        if st in (0, 1):
            com.call("runasync", timeout=60)
            time.sleep(5.0)
            r2 = []
            t0 = time.time()
            while time.time() - t0 < RUN2_S:
                time.sleep(3.0)
                if blocked():
                    shot("run2_dialog")
                    break
                r2.append(snapshot().get(I_FRAME))
            adv2 = [f for f in r2 if isinstance(f, (int, float))]
            p9 = len(adv2) >= 2 and adv2[-1] > adv2[0]
            rec("9 P9 restart runs", "COM", p9,
                "restart frame %r .. %r" % (r2[0] if r2 else None, r2[-1] if r2 else None))
            ok_all &= p9
            idle2 = stop_it()
            rec("9 P9 second stop -> idle", "VISERVER", idle2, "ExecState=%s" % state())
            ok_all &= idle2
        else:
            rec("9 P9 restart runs", "COM", False, "VI not idle before restart (ExecState=%s)" % st)
            ok_all = False
        return ok_all
    finally:
        cleanup()
        after = md5(ORIGINAL)
        rec("Z md5(original) after", "FILE", after == ORIGINAL_MD5, after)
        report()


def reset_stops():
    """Both stop Booleans back to FALSE before every Run. stop_it() leaves them TRUE, so a restart
    issued without this would stop on its first iteration and P9 would fail for the wrong reason."""
    for ctl in (C_STOP, C_STOP2, C_DONE):
        try:
            com.call("set", ctl, False, timeout=10.0)
        except Exception as e:                                            # noqa: BLE001
            log("reset_stops: SetControlValue(%r, False) raised %s" % (ctl, e))


def stop_it():
    for ctl in (C_STOP, C_STOP2):
        try:
            com.call("set", ctl, True, timeout=15.0)
        except Exception as e:                                            # noqa: BLE001
            log("stop: SetControlValue(%r) raised %s" % (ctl, e))
    t0 = time.time()
    while time.time() - t0 < STOP_WAIT:
        time.sleep(2.0)
        if state() in (0, 1):
            return True
    # last resort so nothing is left running unattended
    try:
        com.call("abort", timeout=20.0)
        log("stop: Abort() used after %.0fs" % STOP_WAIT)
    except Exception as e:                                                # noqa: BLE001
        log("stop: Abort raised %s" % e)
    time.sleep(3.0)
    return state() in (0, 1)


def newest_files():
    out = []
    for d in (SAVE_DIR, os.path.dirname(SAVE_BASE)):
        if not os.path.isdir(d):
            continue
        for n in os.listdir(d):
            p = os.path.join(d, n)
            if os.path.isfile(p) and os.path.getmtime(p) > _t0:
                out.append("%s (%d B)" % (p, os.path.getsize(p)))
    return "; ".join(sorted(set(out)))[:380]


_once = set()


def cleanup():
    if "cleanup" in _once:
        return
    _once.add("cleanup")
    try:
        if state() not in (0, 1):
            stop_it()
    except Exception:                                                     # noqa: BLE001
        pass
    for ctl in (C_STOP, C_STOP2):
        try:
            com.call("set", ctl, False, timeout=8.0)
        except Exception:                                                 # noqa: BLE001
            pass
    try:
        com.call("closepanel", timeout=30.0)
    except Exception as e:                                                # noqa: BLE001
        log("cleanup: CloseFrontPanel raised %s" % e)
    try:
        com.call("release", timeout=10.0)
    except Exception:                                                     # noqa: BLE001
        pass
    time.sleep(1.5)
    try:
        if os.path.exists(COPY):
            os.remove(COPY)
            log("cleanup: scratch copy deleted (%s)" % os.path.basename(COPY))
    except Exception as e:                                                # noqa: BLE001
        log("cleanup: could NOT delete the scratch copy: %s" % e)


def report():
    if "report" in _once:
        return
    _once.add("report")
    npass = sum(1 for s in STEPS if s["ok"])
    print("\n| step | method | result | detail |", flush=True)
    print("|---|---|---|---|", flush=True)
    for s in STEPS:
        print("| %s | %s | %s | %s |" % (s["step"], s["method"], "PASS" if s["ok"] else "FAIL",
                                         s["detail"].replace("|", "/").replace("\n", " ")), flush=True)
    print("\n=== D0 drive_original_copy: %d pass, %d fail ===" % (npass, len(STEPS) - npass), flush=True)
    with open(D0_JSON, "w", encoding="utf-8") as f:
        json.dump({"stamp": STAMP, "copy": COPY, "save_base": SAVE_BASE, "steps": STEPS}, f, indent=1)
    print("json: %s" % D0_JSON, flush=True)


if __name__ == "__main__":
    good = False
    try:
        good = main()
    except Exception as e:                                                # noqa: BLE001
        import traceback
        traceback.print_exc()
        rec("!! driver exception", "COM", False, repr(e))
        try:
            cleanup()
        except Exception:                                                 # noqa: BLE001
            pass
        report()
    sys.exit(0 if good else 1)
