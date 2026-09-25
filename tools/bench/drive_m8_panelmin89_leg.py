r"""drive_m8_panelmin89_leg.py - card 89-4 Part 1 (PD195(d), review A2 of profiler_run_plan_89.md §6): ONE `s1` leg of
drive_m8.py in which the copy's FRONT PANEL IS MINIMIZED through COM (ActiveX `VirtualInstrument.FPState`, fact2.md:31)
from the moment the experiment loop starts (right after L9's save dialog is answered) until just before L12's stop.
FOUND FIRST: drive_m8.py (thin wrapper; its argv is parsed at import, so sys.argv is set BEFORE the import);
drive_original_copy_v5.leg (monolithic L1..L13 - `d0.answer_save_dialog` and `stop_with_fallback` are looked up by name at
call time, so patching those two names inserts minimize/restore WITHOUT editing v5); drive_original_copy_v2.Com (a fixed
verb set with no FPState verb -> `MinCom` below is a second private COM apartment holding its own GetVIReference of the
run copy, released before v5.cleanup). No VI is edited; nothing is clicked for the minimize (no GUI act).
    py -u tools/bench/drive_m8_panelmin89_leg.py --minimize|--control --picks 15 --run-s 120 [--dry]
PREDICTION CONTRACT (PM gates, printed as `GATE PM..` lines; drive_m8's M1..M8 stand unchanged):
 PM1 FPState read BEFORE the write is 1 (Standard)          PM2 after `FPState = 4` the readback is 4 (Minimized)
 PM3 lv_gui `rect` of the panel after the write is iconic (left <= -30000) or the window is no longer listed
 PM4 restore before L12: `FPState = 1` reads back 1 and the rect is back on screen (left > -30000)
 control leg (--control): FPState is READ once at the same point (expect 1) and never written; PM2..PM4 pass by construction.
 --dry: drive_m8's dry stubs replace v5.leg, so the patched names are never reached; only the argv plumbing is exercised.
"""
import json, os, sys, threading, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                            # noqa: E402
A = sys.argv[1:]
MIN = "--minimize" in A
assert MIN or "--control" in A, "--minimize or --control"
sys.argv = [sys.argv[0]] + [a for a in A if a not in ("--minimize", "--control")] + ["--leg", "s1"]
import drive_m8                                                                 # noqa: E402  (argv parsed here)
import drive_original_copy_v5 as v5                                             # noqa: E402
d0 = v5.d0
MODE = "min" if MIN else "ctl"
PM, FACTS = {}, {"mode": MODE, "events": []}
STD, MINI = 1, 4                     # FP.State enum as PREDICTED (Standard / Minimized); PM1/PM2 test it, never assume it


def log(m):
    print("[panelmin %s] %s" % (MODE, m), flush=True); FACTS["events"].append("%.1f %s" % (time.time(), m))


class MinCom(threading.Thread):
    """Private COM apartment: open(path) / get -> int(FPState) / set(n) / release. Every call has a deadline."""
    def __init__(self):
        super().__init__(daemon=True); self.q, self.res, self.ev, self.n = [], {}, {}, 0
        self.lk = threading.Lock(); self.cv = threading.Condition(self.lk); self.start()

    def run(self):
        import pythoncom
        from win32com.client import dynamic
        pythoncom.CoInitialize(); app = vi = None
        while True:
            with self.cv:
                while not self.q: self.cv.wait()
                sid, kind, a = self.q.pop(0)
            try:
                if kind == "open":
                    app = dynamic.Dispatch("LabVIEW.Application"); vi = app.GetVIReference(a[0], "", False, 0); out = "ref ok"
                elif kind == "get": out = int(vi.FPState)
                elif kind == "set": vi.FPState = int(a[0]); out = int(vi.FPState)
                elif kind == "release": vi = app = None; out = "released"
                else: out = RuntimeError(kind)
            except Exception as e:                                             # noqa: BLE001
                out = e
            with self.lk:
                self.res[sid] = out; ev = self.ev.get(sid)
            if ev: ev.set()

    def call(self, kind, *a, timeout=15.0):
        with self.cv:
            self.n += 1; sid = self.n; ev = threading.Event(); self.ev[sid] = ev; self.q.append((sid, kind, a)); self.cv.notify()
        if not ev.wait(timeout): raise TimeoutError("MinCom %s blocked >%.0fs" % (kind, timeout))
        with self.lk: out = self.res.pop(sid); self.ev.pop(sid, None)
        if isinstance(out, Exception): raise out
        return out


mc = MinCom()


def rect():
    try: return d0.win_rect(d0.COPY_TITLE)
    except Exception as e:                                                     # noqa: BLE001
        return "ERR %r" % e


real_save = d0.answer_save_dialog
real_stop = v5.stop_with_fallback


def counters(key):
    """`Total Lost Frames` + `current image number` through the driver's own apartment, so lost frames can be DIFFERENCED
    over the minimized window (review c89-panelmin-dry-t5: the indicator is cumulative from the loop start)."""
    try: FACTS[key] = {"lost": v5.getv(d0.I_LOST), "frame": v5.getv(v5.I_FRAME), "t": time.time()}
    except Exception as e:                                                     # noqa: BLE001
        FACTS[key] = "ERR %r" % e
    log("%s: %r" % (key, FACTS[key]))


def save_then_minimize(tag, base_path):
    r = real_save(tag, base_path)
    try:
        mc.call("open", v5.COPY, timeout=60); s0 = mc.call("get"); FACTS["fpstate_before"] = s0; FACTS["rect_before"] = rect()
        counters("counters_at_minimize")
        PM["PM1 FPState before == %d (Standard)" % STD] = (s0 == STD)
        log("FPState before=%r rect=%r" % (s0, FACTS["rect_before"]))
        if MIN:
            s1 = mc.call("set", MINI); time.sleep(1.5); s2 = mc.call("get"); rc2 = rect()
            FACTS.update({"fpstate_set_ret": s1, "fpstate_after_min": s2, "rect_after_min": rc2, "t_minimized": time.time()})
            PM["PM2 FPState after write == %d (Minimized)" % MINI] = (s2 == MINI)
            # review: `None` = lv_gui threw (title not found) and is NOT proof of a minimized window unless PM2 read back 4
            PM["PM3 panel rect iconic after minimize"] = (isinstance(rc2, tuple) and rc2[0] <= -30000) or (rc2 is None and s2 == MINI)
            log("minimized: set->%r get->%r rect=%r" % (s1, s2, rc2))
        else:
            PM["PM2 control: FPState not written"] = True; PM["PM3 control: rect recorded"] = isinstance(FACTS["rect_before"], tuple)
    except Exception as e:                                                     # noqa: BLE001
        log("minimize step RAISED %r" % e); FACTS["minimize_error"] = repr(e)
        PM["PM1 FPState before == %d (Standard)" % STD] = PM.get("PM1 FPState before == %d (Standard)" % STD, False)
        PM["PM2 FPState after write == %d (Minimized)" % MINI] = False
    return r


_restored = []


def restore_then_stop(tag):
    if _restored:                       # review: v5.cleanup() calls stop_with_fallback by name a SECOND time -> never re-run the restore
        return real_stop(tag)
    _restored.append(tag)
    counters("counters_at_restore")
    if MIN:
        try:
            s3 = mc.call("set", STD); time.sleep(1.5); s4 = mc.call("get"); rc4 = rect()
            FACTS.update({"fpstate_after_restore": s4, "rect_after_restore": rc4, "t_restored": time.time()})
            PM["PM4 restore: FPState == %d and rect on screen" % STD] = (s4 == STD) and isinstance(rc4, tuple) and rc4[0] > -30000
            log("restored: set->%r get->%r rect=%r" % (s3, s4, rc4))
        except Exception as e:                                                 # noqa: BLE001
            log("restore RAISED %r" % e); FACTS["restore_error"] = repr(e); PM["PM4 restore: FPState == %d and rect on screen" % STD] = False
    else:
        PM["PM4 control: nothing to restore"] = True
    try: mc.call("release")
    except Exception as e:                                                     # noqa: BLE001
        log("release raised %r" % e)
    return real_stop(tag)


d0.answer_save_dialog = save_then_minimize
v5.stop_with_fallback = restore_then_stop

ok = drive_m8.main()
if not PM: PM["PM0 minimize point never reached (leg did not get to L9)"] = drive_m8.DRY
FACTS["frames_series"] = v5.FACTS.get("frames_run1"); FACTS["lost"] = None
for s in d0.STEPS:
    if "run1.L11" in s["step"]:
        import re; m = re.search(r"\(lost=(.*?)\)$", s["detail"]); FACTS["lost"] = m.group(1) if m else None
jp = os.path.join(HERE, "m8_panelmin_89_%s_pm.json" % MODE)
json.dump({"pm": PM, "facts": FACTS, "drive_m8_ok": ok, "dry": drive_m8.DRY}, open(jp, "w"), indent=1, default=str)
for k, v in PM.items(): print("GATE %-52s %s" % (k, "PASS" if v else "FAIL"), flush=True)
bad = [k for k, v in PM.items() if not v] + ([] if ok else ["drive_m8 M-gates"])
print(P.result_line(P.make_result(len(PM) + (1 if ok else 0), len(bad), bad[0] if bad else None,
                                  [{"path": os.path.relpath(jp, ROOT), "md5": drive_m8.md5(jp)}])), flush=True)
sys.stdout.flush(); os._exit(0 if not bad else 1)
