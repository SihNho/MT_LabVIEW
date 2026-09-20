"""d0_probe.py - finish D0's measurement on the ALREADY-RUNNING copy.

Context (tools/bench/drive_original_copy_run2.log + tools/bench/d0_shots/*.png, 2026-09-17):
the driver got the copy loaded and running, then EVERY COM call blocked while the VI sat in the
bead-picking loop. Three `lv_gui` clicks on the image display (552,756 / 430,640 / 690,880) each
planted a bead marker, and a fourth on the `Done Picking Beads?` "Yes" button (1114,915) ended the
loop - the display switched to the white calibration view with three ROI patches, `Count` 0 -> 1,
`Focus Pos (Cal)` 3.4. So the picking gate IS passable by the user's option-1 mechanism.

This probe answers what is left, WITHOUT restarting anything:
  Q1 does COM work again now that the picking loop is over?  (the block was the loop, or it wasn't)
  Q2 does the experiment loop advance `current image number`?
  Q3 is a save path/name asked for - and what is in `Track File Path` / `Cal File Path`?
  Q4 does SetControlValue('stop (end)', True) return the VI to idle?
The copy's FILE was deleted by the driver's cleanup while the VI was still in memory, so the
reference is taken BY NAME (LabVIEW resolves a VI already in memory by name) with the full path as
a fallback.  Nothing is saved; the original is md5-checked at both ends.

    MATERIAL=1 py tools/bgrun.py --max-min 8 --log tools/bench/d0_probe.log -- py -u tools/bench/d0_probe.py
"""
import hashlib
import json
import os
import queue
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
import gscript as g                                                            # noqa: E402

ORIGINAL = (r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking"
            r"\Min_Track N beads V6_ParallelLoop.vi")
ORIGINAL_MD5 = "2a78e17c449cacdaf5da389818526859"
VINAME = "D0_MAINCOPY_20260917_014823.vi"
C_STOP = "stop (end)"
C_STOP2 = "stop (end) 2"
C_DONE = "Done Picking \nBeads?"
POLL = ["current image number", "file progress", "File Size", "Total Lost Frames",
        "Cal File Path", "Track File Path", "Count", "Focus Pos (Cal)", "File # Saved"]
_t0 = time.time()
ROWS = []


def log(m):
    print("[%6.1fs] %s" % (time.time() - _t0, m), flush=True)


class Com(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.q = queue.Queue(); self.ev = {}; self.res = {}; self.n = 0
        self.lk = threading.Lock(); self.start()

    def run(self):
        import pythoncom
        from win32com.client import dynamic
        pythoncom.CoInitialize()
        app = None; vi = None
        while True:
            sid, kind, args = self.q.get()
            try:
                if kind == "app":
                    app = dynamic.Dispatch("LabVIEW.Application"); out = str(app.Version)
                elif kind == "byname":
                    vi = app.GetVIReference(args[0], "", False, 0); out = "ref by name ok"
                elif kind == "get":
                    out = vi.GetControlValue(args[0])
                elif kind == "set":
                    vi.SetControlValue(args[0], args[1]); out = "set"
                elif kind == "state":
                    out = int(vi.ExecState)
                elif kind == "release":
                    vi = None; app = None; out = "released"
                else:
                    out = RuntimeError(kind)
            except Exception as e:                                             # noqa: BLE001
                out = e
            with self.lk:
                self.res[sid] = out; e2 = self.ev.get(sid)
            if e2:
                e2.set()

    def call(self, kind, *a, timeout=10.0):
        with self.lk:
            self.n += 1; sid = self.n; ev = threading.Event(); self.ev[sid] = ev
        self.q.put((sid, kind, a))
        if not ev.wait(timeout):
            raise TimeoutError("COM %s blocked >%.0fs" % (kind, timeout))
        with self.lk:
            out = self.res.pop(sid); self.ev.pop(sid, None)
        if isinstance(out, Exception):
            raise out
        return out


com = Com()


def gui(*a):
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
                        "& '%s' %s" % (g.LV_GUI, " ".join(a))], capture_output=True, text=True, timeout=60)
    return ((r.stdout or "") + (r.stderr or "")).strip()


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def snap():
    row = {}
    for n in POLL:
        try:
            row[n] = com.call("get", n, timeout=8.0)
        except Exception as e:                                                 # noqa: BLE001
            row[n] = "ERR:%s" % type(e).__name__
    return row


def rec(q, ok, detail):
    ROWS.append({"q": q, "ok": bool(ok), "detail": str(detail)[:400]})
    log("%-38s %-4s %s" % (q, "PASS" if ok else "FAIL", detail))


def main():
    before = md5(ORIGINAL)
    rec("md5(original) before", before == ORIGINAL_MD5, before)
    com.call("app", timeout=120)
    com.call("byname", VINAME, timeout=60)

    # Q1 - is COM usable now that the picking loop is over?
    try:
        st = com.call("state", timeout=10.0)
        rec("Q1 COM responsive after picking", True, "ExecState=%s (2=running top level)" % st)
    except Exception as e:                                                     # noqa: BLE001
        rec("Q1 COM responsive after picking", False, repr(e))
        rec("Q1 dialogs", False, gui("-Action", "dialogs").splitlines()[-1])
        return False

    # Q2/Q3 - watch the counters for 60 s
    hist = []
    for _ in range(12):
        s = snap()
        hist.append(s)
        log("sample %s" % json.dumps(s, default=str)[:260])
        time.sleep(5.0)
    frames = [h["current image number"] for h in hist if isinstance(h["current image number"], (int, float))]
    rec("Q2 current image number advances", len(frames) >= 2 and frames[-1] > frames[0],
        "%r .. %r over 60 s" % (frames[0] if frames else None, frames[-1] if frames else None))
    last = hist[-1]
    rec("Q3 save paths", bool(last.get("Track File Path")) or bool(last.get("Cal File Path")),
        "Track File Path=%r  Cal File Path=%r  File # Saved=%r"
        % (last.get("Track File Path"), last.get("Cal File Path"), last.get("File # Saved")))
    rec("Q3 modal dialog present?", True, gui("-Action", "dialogs").splitlines()[-1])
    gui("-Action", "shot", "-Out", "'%s'" % os.path.join(HERE, "d0_shots", "probe_running.png"))

    # Q4 - stop through the VI's own control
    for c in (C_STOP, C_STOP2):
        try:
            com.call("set", c, True, timeout=15.0)
            log("set %r True ok" % c)
        except Exception as e:                                                 # noqa: BLE001
            log("set %r raised %s" % (c, e))
    idle = False
    t0 = time.time()
    while time.time() - t0 < 60:
        time.sleep(2.0)
        try:
            if com.call("state", timeout=8.0) in (0, 1):
                idle = True
                break
        except Exception:                                                      # noqa: BLE001
            pass
    rec("Q4 stop -> idle", idle, "ExecState now %s" % (com.call("state", timeout=8.0) if idle else "?"))
    gui("-Action", "shot", "-Out", "'%s'" % os.path.join(HERE, "d0_shots", "probe_after_stop.png"))
    return all(r["ok"] for r in ROWS)


if __name__ == "__main__":
    good = False
    try:
        good = main()
    except Exception as e:                                                     # noqa: BLE001
        import traceback
        traceback.print_exc()
        rec("!! probe exception", False, repr(e))
    finally:
        try:
            com.call("release", timeout=10.0)
        except Exception:                                                      # noqa: BLE001
            pass
        after = md5(ORIGINAL)
        rec("md5(original) after", after == ORIGINAL_MD5, after)
        np = sum(1 for r in ROWS if r["ok"])
        print("\n| question | result | detail |\n|---|---|---|", flush=True)
        for r in ROWS:
            print("| %s | %s | %s |" % (r["q"], "PASS" if r["ok"] else "FAIL",
                                        r["detail"].replace("|", "/")), flush=True)
        print("\n=== D0 probe: %d pass, %d fail ===" % (np, len(ROWS) - np), flush=True)
        json.dump(ROWS, open(os.path.join(HERE, "d0_probe.json"), "w", encoding="utf-8"), indent=1)
    sys.exit(0 if good else 1)
