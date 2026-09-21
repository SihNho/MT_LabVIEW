"""diag_c68_quote2 - the SPACED-title quoting test the first quote test missed.

Run 3's failing focus candidates all contained SPACES ("WORK_...vi Front Panel"); the first test used
the space-free "LabVIEW" and both quote forms worked. A spaced title is where list2cmdline's \"...\"
escaping can split the argument. Compare, for a title WITH spaces (existence not required - a mangled
argument errors/behaves differently from a clean "no window matching"):
  double-quote form (gui_save's, gscript.py:2025-2041) vs single-quote form (every other call site).
Also runs the REAL positive case: opens the bed copy's panel so a spaced FP title exists, then tries to
focus it both ways. Pre-decided 63: hygiene-only gates. The one open_panel is on a scratch copy.
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
STAMP = time.strftime("%Y%m%d_%H%M%S")
WORK = os.path.join(g.CLAUDEDEV, "QT_%s.vi" % STAMP)
OUT = os.path.join(BENCH, "diag_c68_quote2.json")
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "results": {}, "handles": {}}


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


def try_focus(tag, arg):
    out = ""
    try:
        out = g._lv_gui("-Action", "focus", "-Title", arg)
    except Exception as e:                                                         # noqa: BLE001
        out = "RAISED %s: %s" % (type(e).__name__, str(e)[:300])
    fact("%s -Title %r -> %r" % (tag, arg, out.strip()[:300]))
    R["results"][tag] = {"arg": arg, "out": out[:500]}
    dump()
    return out


def main():
    print("=== diag_c68_quote2 %s - spaced-title quoting" % STAMP, flush=True)
    R["handles"]["before"] = labview_handles()
    # ---- negative case: a spaced title that exists nowhere
    try_focus("[N-double]", '"No Such Window Title"')
    try_focus("[N-single]", "'No Such Window Title'")
    # ---- positive case: a real spaced FP title
    shutil.copy2(BED, WORK)
    name = os.path.basename(WORK)
    try:
        g.open_panel(WORK)
        o1 = try_focus("[P-double]", '"%s Front Panel"' % name)
        o2 = try_focus("[P-single]", "'%s Front Panel'" % name)
        fact("*** VERDICT MATERIAL: double focused=%r, single focused=%r on the REAL spaced title - "
             "if only single focuses, gui_save's double-quote form is the bug for every spaced title, "
             "which is every VI window title ***" % ("focused" in o1, "focused" in o2))
    finally:
        try:
            g.close_panel(WORK)
        except Exception:                                                          # noqa: BLE001
            pass
        if os.path.exists(WORK):
            try:
                os.remove(WORK)
            except Exception as e:                                                 # noqa: BLE001
                fact("scratch remove failed: %r" % e)
        gate("H scratch %s is gone" % name, not os.path.exists(WORK))
        ff = D.file_facts("H THE BED AFTER", BED)
        gate("H THE BED md5 STILL its pin 26c54ff7", ff.get("md5") == BED_MD5, ff.get("md5"))
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
