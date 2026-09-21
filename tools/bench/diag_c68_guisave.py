"""diag_c68_guisave - THE DISCRIMINATING TEST for the gui_save mtime failure (cycle 57 firefighter).

FAILED PREDICTION: Pre-decided 88 predicted `save(WORK, allow_broken=True)` -> gui_save leaves a file;
the run's answer was `file mtime did not move after Ctrl+S on every candidate window`
(tools/bench/build_d1_m3a1.log:1967) - the SAME signature as run 10 (build_d1_routeb_v7_run10.log:367).

HYPOTHESIS H1 (this test discriminates): Ctrl+S on a broken COPY OF THE MAIN VI raises a MODAL DIALOG
(save-changes-to-subVIs / missing-subVI class), and gui_save's unconditional Esc (sent to dismiss the
File-menu activation, tools/gscript.py:2054) CANCELS that dialog - so the save never completes and the
mtime never moves. Evidence for: the before-capture shows the run began behind the Getting Started
window; the after-capture shows NO dialog (Esc had dismissed it). Against: the 2026-08-30 measurement
"File>Save handles a broken VI fine" - but that was a small op VI with no dirty subVI hierarchy.
H2 (alternative): Ctrl+S never reaches the VI window at all (focus theft), so no dialog ever appears.

THE TEST, replicating gui_save's exact key sequence but reading the screen BETWEEN ^s and Esc:
  copy bed -> scratch; delete ONE wire by COM (broken, dirty, ExecState 0 - a SCRATCH, deleted at exit);
  open_panel; focus the Front Panel; H5 title-bar click; send ^s; then IMMEDIATELY
  `lv_gui -Action dialogs` + a screenshot + mtime read; THEN Esc; dialogs + mtime again.
  H1 predicts: a modal dialog in the first dialogs read, gone after Esc, mtime never moves (or moves
  only if the dialog is answered affirmatively). H2 predicts: no dialog at either read.

Pre-decided 63: gates on HYGIENE only. No motor/ASI/camera. The one GUI sequence here is the same
approved class gui_save itself uses (Approved: user 2026-09-17 bead-pick option 1 does not apply;
the applicable evidence is Pre-decided 88's rider - this diagnostic exists to verify that GUI act).
"""
import json
import os
import shutil
import sys
import time

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                              # noqa: BLE001
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench")):
    sys.path.insert(0, _p)
import gscript as g                                                                # noqa: E402
import diag_s2_scaffold as D                                                       # noqa: E402
from bench_prep import labview_handles                                             # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
BED = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi")
BED_MD5 = "26c54ff784cb5cea21edbd214d2cc3a0"
ORIGINAL, ORIG_MD5 = D.ORIGINAL, D.ORIG_MD5
PINS = (("ORIGINAL", ORIGINAL, ORIG_MD5), ("THE BED", BED, BED_MD5))

STAMP = time.strftime("%Y%m%d_%H%M%S")
WORK = os.path.join(g.CLAUDEDEV, "GS_%s.vi" % STAMP)
OUT = os.path.join(BENCH, "diag_c68_guisave.json")
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "handles": {}, "steps": {},
     "gating_policy": "Pre-decided 63: HYGIENE ONLY"}


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  %r" % detail) if detail else ""), flush=True)


def fact(line):
    facts.append(line)
    print("  FACT  %s" % line, flush=True)


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    json.dump(R, open(OUT, "w", encoding="utf-8"), indent=1, default=repr)


def lv(*args):
    out = ""
    try:
        out = g._lv_gui(*args)
    except Exception as e:                                                         # noqa: BLE001
        out = "ERROR %s: %s" % (type(e).__name__, str(e)[:200])
    return out


def main():
    print("=== diag_c68_guisave %s - does Ctrl+S on a broken main-VI copy raise a modal that Esc then "
          "cancels?" % STAMP, flush=True)
    R["handles"]["before"] = labview_handles()
    for tag, path, pin in PINS:
        ff = D.file_facts("H %s BEFORE" % tag, path)
        gate("H %s md5 == its pin %s" % (tag, pin[:8]), ff.get("md5") == pin, ff.get("md5"))
    shutil.copy2(BED, WORK)
    name = os.path.basename(WORK)
    try:
        # ---- break it: delete the FIRST wire the census hands out (a SCRATCH - rule 1 untouched)
        rows = g.report_all(WORK, "Wire")
        w0 = rows[0]["uid"] if rows else None
        fact("[1] Wire census %d row(s); deleting wire #%r to break the scratch" % (len(rows or []), w0))
        try:
            g.delete_object(WORK, "Wire", int(w0))
            fact("[1] delete_object(Wire %r) returned" % w0)
        except Exception as e:                                                     # noqa: BLE001
            fact("[1] delete_object raised %s: %s" % (type(e).__name__, str(e)[:200]))
        es = g.exec_state(WORK)
        fact("[1] ExecState after the wire delete: %r (0 = broken, the state under test)" % es)

        # ---- gui_save's exact sequence, instrumented between ^s and Esc
        g.open_panel(WORK)
        mt0 = os.path.getmtime(WORK)
        for title in ("%s Block Diagram" % name, "%s Front Panel" % name, name):
            out = lv("-Action", "focus", "-Title", '"%s"' % title)
            fact("[2] focus %r -> %s" % (title, out.strip()[:120]))
            if "focused" not in out:
                continue
            time.sleep(0.8)
            import re as _re
            m = _re.search(r"left=(-?\d+) top=(-?\d+) right=(-?\d+)",
                           lv("-Action", "rect", "-Title", '"%s"' % title))
            if m:
                L, T, Rr = (int(x) for x in m.groups())
                lv("-Action", "click", "-X", str(min(L + 300, Rr - 120)), "-Y", str(T + 10),
                   "-Exception", "Approved",
                   "-Evidence", "diag_c68_guisave: gui_save H5 title-bar click, replicated for the "
                                "Pre-decided 88 discriminating test")
                time.sleep(0.4)
            lv("-Action", "keys", "-Key", "^s", "-WaitMs", "2500", "-Exception", "Approved",
               "-Evidence", "diag_c68_guisave: replicate gui_save Ctrl+S to read the screen BEFORE Esc")
            # ---- THE READ gui_save NEVER TAKES: what is on screen between ^s and Esc?
            dlg1 = lv("-Action", "dialogs")
            shot1 = os.path.join(BENCH, "guisave_between_%s.png" % STAMP)
            lv("-Action", "shot", "-Out", "'%s'" % shot1)
            mt1 = os.path.getmtime(WORK)
            fact("[3] BETWEEN ^s AND Esc: dialogs -> %r" % dlg1.strip()[:400])
            fact("[3] BETWEEN ^s AND Esc: capture %s (exists %r) ; mtime moved %r"
                 % (os.path.basename(shot1), os.path.exists(shot1), mt1 > mt0))
            R["steps"]["between"] = {"dialogs": dlg1, "mtime_moved": mt1 > mt0, "shot": shot1}
            lv("-Action", "key", "-Key", "esc")
            time.sleep(0.6)
            dlg2 = lv("-Action", "dialogs")
            mt2 = os.path.getmtime(WORK)
            fact("[4] AFTER Esc: dialogs -> %r ; mtime moved %r" % (dlg2.strip()[:400], mt2 > mt0))
            R["steps"]["after_esc"] = {"dialogs": dlg2, "mtime_moved": mt2 > mt0}
            fact("*** VERDICT MATERIAL: H1 (modal cancelled by Esc) is %s; H2 (keys never landed) is %s "
                 "- judged from the dialogs lines above, not asserted here ***"
                 % ("SUPPORTED" if ("VERDICT: clear" not in dlg1 and dlg1.strip()) else "NOT supported",
                    "SUPPORTED" if ("VERDICT: clear" in dlg1 and mt2 <= mt0) else "NOT supported"))
            break
    finally:
        try:
            g.close_panel(WORK)
        except Exception:                                                          # noqa: BLE001
            pass
        # close any straggler dialog state before deleting: one more Esc is diagnostic-class
        lv("-Action", "key", "-Key", "esc")
        if os.path.exists(WORK):
            try:
                os.remove(WORK)
            except Exception as e:                                                 # noqa: BLE001
                fact("scratch remove failed: %r" % e)
        gate("H scratch %s is gone" % name, not os.path.exists(WORK))
        for tag, path, pin in PINS:
            ff = D.file_facts("H %s AFTER" % tag, path)
            gate("H %s md5 STILL its pin %s" % (tag, pin[:8]), ff.get("md5") == pin, ff.get("md5"))
        rc = g.ref_counts()
        gate("H refs opened == closed and 0 live", rc.get("live") == 0, rc)
        R["handles"]["after"] = labview_handles()
        gate("H handle count read at entry and exit",
             isinstance(R["handles"].get("before"), int) and isinstance(R["handles"].get("after"), int),
             "%r -> %r" % (R["handles"].get("before"), R["handles"].get("after")))
        dump()
        print("\n=== GATES: %d pass / %d fail%s" % (len(passes), len(fails),
                                                    ("; failing: " + ", ".join(fails)) if fails else ""),
              flush=True)
        print("=== JSON: %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
