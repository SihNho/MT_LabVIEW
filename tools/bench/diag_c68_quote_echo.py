"""diag_c68_quote_echo - the TWO discriminating tests named by archive/peer/2026-09-22-c71-run3.md.

TEST 1 (the review's Failure-2 test, no GUI mutation): is gui_save's DOUBLE-quoted `-Title` form mangled
by list2cmdline while the single-quoted form (every other gscript call site) works? Compare
  focus -Title "LabVIEW"   (gui_save's form, gscript.py:2025-2041)
  focus -Title 'LabVIEW'   (the working form, gscript.py:1664 etc.)
Different outcomes => the quoting is the bug and the fix is four characters in gui_save.
Also prints the exact list2cmdline string PowerShell receives for the double-quote form.

TEST 2 (the review's Failure-1 test, read-only): is `OpWireSource_v5` input-determined or
history-determined? The ordering PD86 skipped, on a FRESH LabVIEW and a plain copy of the bed:
  1. walk LIVE wire 9649            -> expect its real rows
  2. walk 2147483646 (never existed) -> NULL => input-determined ; 9649's rows => HISTORY-DETERMINED
  3. walk LIVE wire 9113            -> expect its real rows
  4. walk 2147483646 again          -> 9113's rows would clinch history-determined
Pre-decided 63: gates on HYGIENE only; every measurement is a FACT line. No mutation of any VI.
"""
import json
import os
import shutil
import subprocess
import sys
import time

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                              # noqa: BLE001
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench"),
           os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import gscript as g                                                                # noqa: E402
import diag_s2_scaffold as D                                                       # noqa: E402
from bench_prep import labview_handles                                             # noqa: E402
from build_opconnectfromwire_v0 import wire_source_owner as WIRE_TERMS             # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
BED = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi")
BED_MD5 = "26c54ff784cb5cea21edbd214d2cc3a0"
ORIGINAL, ORIG_MD5 = D.ORIGINAL, D.ORIG_MD5
PINS = (("ORIGINAL", ORIGINAL, ORIG_MD5), ("THE BED", BED, BED_MD5))
UID_LIVE_1, UID_LIVE_2, UID_GHOST = 9649, 9113, 2147483646

STAMP = time.strftime("%Y%m%d_%H%M%S")
WORK = os.path.join(g.CLAUDEDEV, "QE_%s.vi" % STAMP)
OUT = os.path.join(BENCH, "diag_c68_quote_echo.json")
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "handles": {}, "quote": {}, "echo": {},
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


def walk(tag, uid):
    rows, err = [], ""
    try:
        rows = WIRE_TERMS(WORK, int(uid)) or []
    except Exception as e:                                                         # noqa: BLE001
        err = "%s: %s" % (type(e).__name__, str(e)[:300])
    real = [(t.get("i"), t.get("is_source"), t.get("owner_class"), t.get("owner_uid"), t.get("recip"))
            for t in rows if t.get("owner_uid")]
    fact("%s OpWireSource_v5(UID 2 = %r): %d row(s), %d with a REAL owner%s -> %r"
         % (tag, uid, len(rows), len(real), (" ; ERROR " + err) if err else "", real))
    R["echo"][tag] = {"uid": uid, "real_rows": real, "error": err}
    dump()
    return real


def main():
    print("=== diag_c68_quote_echo %s" % STAMP, flush=True)
    R["handles"]["before"] = labview_handles()
    for tag, path, pin in PINS:
        ff = D.file_facts("H %s BEFORE" % tag, path)
        gate("H %s md5 == its pin %s" % (tag, pin[:8]), ff.get("md5") == pin, ff.get("md5"))

    # ---- TEST 1: the quoting comparison (needs any live LabVIEW window; 'LabVIEW' matches by substring)
    ps1 = os.path.join(ROOT, "tools", "lv_gui.ps1")
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps1,
           "-Action", "focus", "-Title", '"LabVIEW"']
    fact("[Q] list2cmdline of the DOUBLE-quote form: %r" % subprocess.list2cmdline(cmd))
    out_dq = ""
    try:
        out_dq = g._lv_gui("-Action", "focus", "-Title", '"LabVIEW"')
    except Exception as e:                                                         # noqa: BLE001
        out_dq = "RAISED %s: %s" % (type(e).__name__, str(e)[:300])
    fact("[Q] focus -Title \"LabVIEW\" (gui_save's form)  -> %r" % out_dq.strip()[:300])
    out_sq = ""
    try:
        out_sq = g._lv_gui("-Action", "focus", "-Title", "'LabVIEW'")
    except Exception as e:                                                         # noqa: BLE001
        out_sq = "RAISED %s: %s" % (type(e).__name__, str(e)[:300])
    fact("[Q] focus -Title 'LabVIEW' (the working form) -> %r" % out_sq.strip()[:300])
    dq_ok, sq_ok = ("focused" in out_dq), ("focused" in out_sq)
    R["quote"] = {"double_quote_out": out_dq[:500], "single_quote_out": out_sq[:500],
                  "double_focused": dq_ok, "single_focused": sq_ok}
    fact("*** [Q] VERDICT MATERIAL: double-quote focused=%r, single-quote focused=%r - different => "
         "the quoting IS the gui_save bug (fix gscript.py:2025-2041); both focused => quoting exonerated "
         "***" % (dq_ok, sq_ok))

    # ---- TEST 2: fresh instance, then live -> ghost -> live -> ghost
    fact("[E] fresh LabVIEW restart so the op VI's indicators start from nothing")
    D.fresh("[E] restart for the echo-order test")
    R["handles"]["after_restart"] = labview_handles()
    shutil.copy2(BED, WORK)
    ff = D.file_facts("[E] scratch copy", WORK)
    gate("H the scratch starts byte-identical to the bed", ff.get("md5") == BED_MD5, ff.get("md5"))
    try:
        r1 = walk("[E1 LIVE %d]" % UID_LIVE_1, UID_LIVE_1)
        r2 = walk("[E2 GHOST %d after a LIVE read]" % UID_GHOST, UID_GHOST)
        r3 = walk("[E3 LIVE %d]" % UID_LIVE_2, UID_LIVE_2)
        r4 = walk("[E4 GHOST %d after the second LIVE read]" % UID_GHOST, UID_GHOST)
        echo2, echo4 = (r2 == r1 and bool(r1)), (r4 == r3 and bool(r3))
        if not r2 and not r4:
            v = ("INPUT-DETERMINED: both ghost reads nulled straight after live reads - the reader "
                 "answers from its input; PD86 outcome A stands after all, on the ordering that counts")
        elif echo2 or echo4:
            v = ("HISTORY-DETERMINED: ghost read(s) returned the previous live rows (E2==E1 %r, E4==E3 %r)"
                 " - the reader echoes stale state; NO identity conclusion read through it is sound"
                 % (echo2, echo4))
        else:
            v = "MIXED: E2 %r ; E4 %r - neither clean null nor clean echo; judgement decides" % (r2, r4)
        R["echo"]["verdict"] = v
        fact("*** [E] %s ***" % v)
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
        gate("H scratch %s is gone" % os.path.basename(WORK), not os.path.exists(WORK))
        for tag, path, pin in PINS:
            ff2 = D.file_facts("H %s AFTER" % tag, path)
            gate("H %s md5 STILL its pin %s" % (tag, pin[:8]), ff2.get("md5") == pin, ff2.get("md5"))
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
