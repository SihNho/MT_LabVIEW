# ---
# labview: read
# hardware: camera
# ---
r"""fr90_abba - p64_abba.py (NOT edited) with its leg script pointed at fr90_leg.py (p64_leg + the `# of Auto-Reset` read).
Every refusal, gate, move and summary is p64_abba's. Same arguments as p64_abba.py (without --live = dry).
Retry 1 (C1): p64_abba's leg-start checks are extended by one refusal, evaluated before EVERY leg (and in the dry): the leg's
out-root and run folder must be ABSOLUTE and lie under <V6_lean>\tools\bench\lean_bench\out_p64\ (resolved real path, compared
case-insensitively); else the leg is REFUSED (gate line printed, the leg script and LabVIEW are not started).
    py -u tools/bench/lean_bench/fr90_abba.py --a-src <vi> --a-md5 <m> --b-src <vi> --b-md5 <m> --o-src <vi> --o-md5 <m>
          --hz 90 --run-s 120 --order ABBAO [--live] [--out-root <absolute dir under out_p64>]
    py tools/bench/lean_bench/fr90_abba.py --c1-selftest      (offline: relative / outside refused, the intended one accepted)"""
import os, sys                                                                            # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import p64_abba as PA                                                                     # noqa: E402
PA.LEG_PY = os.path.join(HERE, "fr90_leg.py")
OUT_P64 = os.path.join(HERE, "out_p64")
_orig_start_checks = PA.start_checks


def path_ok(p):
    """C1 for one path: (ok, text). Absolute (drive + root) and its real path strictly under out_p64, case-insensitive."""
    if not p:
        return False, "empty path"
    if not (os.path.isabs(p) and os.path.splitdrive(p)[0]):
        return False, "%r is not absolute" % p
    base = os.path.normcase(os.path.realpath(OUT_P64)).rstrip("\\/") + os.sep
    real = os.path.normcase(os.path.realpath(p))
    if not real.startswith(base):
        return False, "%r resolves to %r, not under %r" % (p, real, base)
    return True, "%r under out_p64" % p


def c1_check(out_root):
    """The leg's out-root and its run folder (M8_RUN_ROOT once run_abba has set it, else <out-root>\\run). Returns reasons."""
    run = os.environ.get("M8_RUN_ROOT") or os.path.join(out_root or "", "run")
    why = []
    for name, p in (("out-root", out_root), ("run folder", run)):
        ok, txt = path_ok(p)
        print("GATE C1 %-10s absolute and under out_p64: %s  %s" % (name, "PASS" if ok else "FAIL", txt), flush=True)
        if not ok:
            why.append("C1 output path: %s %s" % (name, txt))
    return why


def start_checks(cfg, arm, src, pin):
    return c1_check(cfg.get("out_root")) + _orig_start_checks(cfg, arm, src, pin)


PA.start_checks = start_checks                                                           # run_leg and the dry look it up at call time


def selftest():
    keep = os.environ.pop("M8_RUN_ROOT", None)
    cases = [("relative (run-1 attempt 2 form)", "tools/bench/lean_bench/out_p64/fr90/s0_a2", False),
             ("absolute, outside out_p64", os.path.join(HERE, "out_latest2", "x"), False),
             ("absolute, out_p64 itself", OUT_P64, False),
             ("absolute, escapes by ..", os.path.join(OUT_P64, "..", "out_latest2"), False),
             ("other drive", r"C:\Temp\out_p64\fr90", False),
             ("intended, upper-case", os.path.join(HERE, "OUT_P64", "fr90r1", "s0").upper(), True),
             ("intended", os.path.join(OUT_P64, "fr90r1", "s0"), True)]
    bad = 0
    for name, p, want in cases:
        got = not c1_check(p)
        bad += got != want
        print("CASE %-34s %-70s accepted=%s want=%s %s" % (name, p, got, want, "OK" if got == want else "WRONG"), flush=True)
    if keep is not None:
        os.environ["M8_RUN_ROOT"] = keep
    print("C1 SELFTEST %s (%d / %d)" % ("PASS" if not bad else "FAIL", len(cases) - bad, len(cases)), flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(selftest() if "--c1-selftest" in sys.argv else PA.main(sys.argv[1:]))
