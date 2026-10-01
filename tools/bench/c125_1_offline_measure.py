r"""Card 125-1 (gate-fp fp-11/12/13): MEASURE that each protocol.OFFLINE_SELFTESTS entry, run in its listed form, never
opens COM. Each entry runs in a child process in which every COM entry point to an out-of-process server -
win32com.client Dispatch / DispatchEx / GetActiveObject / GetObject, win32com.client.dynamic Dispatch / DumbDispatch,
win32com.client.gencache EnsureDispatch, pythoncom CoCreateInstance / CoCreateInstanceEx - is replaced by a TRIPWIRE
that counts the call and raises BEFORE anything reaches LabVIEW. The tripwire is installed lazily by an __import__ hook
the moment the self-test itself imports a COM module (nothing is pre-imported; this harness opens no COM).
Parent also compares the LabVIEW.exe process count before / after.

PREDICTION CONTRACT: for every entry: child exit 0 AND trips 0; LabVIEW.exe count after == before (== 0 expected).
Prior art checked: tools/bench/selftest_op_hygiene* (fp-2) replaces pythoncom/win32com in sys.modules wholesale -
that would break gscript's import; a call-level tripwire keeps the import path real. No existing COM tripwire harness
in tools/ (grep 'tripwire' tools/ -> none before this file). Ends with a RESULT line.
"""
import os
import runpy
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))


def child(script, args, tripfile):
    def trip(*a, **k):
        with open(tripfile, "a", encoding="utf-8") as f:
            f.write("TRIP %r\n" % (a[:1],))
        raise RuntimeError("TRIPWIRE: COM entry point called %r" % (a[:1],))
    # LAZY: patched right after the self-test itself imports a COM module, never pre-imported here - stagexec's own
    # selftest gate T14 asserts nothing LabVIEW-side is in sys.modules (stagexec.py:4071); the first version of this
    # harness pre-imported win32com and tripped exactly that gate (c125_1_offline_measure.log run 1).
    import builtins
    targets = (("win32com.client", ("Dispatch", "DispatchEx", "GetActiveObject", "GetObject")),
               ("win32com.client.dynamic", ("Dispatch", "DumbDispatch")),
               ("win32com.client.gencache", ("EnsureDispatch",)),
               ("pythoncom", ("CoCreateInstance", "CoCreateInstanceEx")))
    done = set()
    real_import = builtins.__import__

    def patch():
        for modname, names in targets:
            m = sys.modules.get(modname)
            if m is not None and modname not in done:
                done.add(modname)
                for n in names:
                    if hasattr(m, n):
                        setattr(m, n, trip)

    def hooked(*a, **k):
        r = real_import(*a, **k)
        if len(done) < len(targets):
            patch()
        return r
    builtins.__import__ = hooked
    os.chdir(ROOT)
    sys.argv = [script] + list(args)
    sys.path.insert(0, os.path.dirname(script))
    try:
        runpy.run_path(script, run_name="__main__")
        rc = 0
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    with open(tripfile + ".mods", "w", encoding="utf-8") as f:
        f.write(",".join(m for m in ("gscript", "stagekit", "win32com", "pythoncom") if m in sys.modules))
    sys.stdout.flush()
    os._exit(rc)


def lv_count():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq LabVIEW.exe"], capture_output=True, text=True).stdout
    return sum(1 for ln in out.splitlines() if ln.lower().startswith("labview.exe"))


def main():
    import protocol as P
    res = []
    before = lv_count()
    print("LabVIEW.exe before: %d" % before, flush=True)
    for rel, arg in sorted(P.OFFLINE_SELFTESTS.items()):
        script = os.path.join(ROOT, rel)
        tf = os.path.join(tempfile.gettempdir(), "c125_trip_%d_%s.txt" % (os.getpid(), os.path.basename(rel)))
        if os.path.exists(tf):
            os.remove(tf)
        t0 = time.time()
        p = subprocess.run([sys.executable, "-u", os.path.abspath(__file__), "--child", script, tf] +
                           ([arg] if arg else []), cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=900)
        trips = open(tf, encoding="utf-8").read().count("TRIP ") if os.path.exists(tf) else 0
        mods = open(tf + ".mods", encoding="utf-8").read() if os.path.exists(tf + ".mods") else "?"
        print("    COM-side modules imported (never called if trips 0): [%s]" % mods, flush=True)
        tail = [ln for ln in p.stdout.splitlines() if ln.startswith("RESULT ")][-1:] or p.stdout.splitlines()[-1:]
        ok = p.returncode == 0 and trips == 0
        res.append((rel, ok))
        print("  %s  %-48s arg=%-9s rc=%s trips=%d %.0fs | %s" % ("PASS" if ok else "BAD ", rel, arg, p.returncode,
              trips, time.time() - t0, (tail[0] if tail else "")[:160]), flush=True)
        if p.returncode != 0:
            print("    stderr tail: %s" % p.stderr[-600:].replace("\n", " | "), flush=True)
    after = lv_count()
    res.append(("LabVIEW.exe count unchanged (%d -> %d)" % (before, after), after == before))
    print("  %s  LabVIEW.exe after: %d" % ("PASS" if after == before else "BAD ", after), flush=True)
    npass = sum(1 for _r, ok in res if ok)
    nfail = len(res) - npass
    print(P.result_line(P.make_result(npass, nfail, next((r for r, ok in res if not ok), None))), flush=True)
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--child":
        child(sys.argv[2], sys.argv[4:], sys.argv[3])
    sys.exit(main())
