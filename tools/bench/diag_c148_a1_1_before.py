# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c148_a1_1_before.py:51
# ---
r"""diag_c148_a1_1_before - card 148-a1-1: show that each NEW self-test case FAILS on the pre-fix code. Runs ONE self-test
(argv[1]) in-process with the four edited modules (stage_prerun, guard_cycle, guard_write, guard_assign) loaded from their
git HEAD blobs (= the card-input bytes 61d6f590 / c080fb7a / 391a8324 / b9dc09bb) under their REAL __file__ paths, so their
ROOT/BENCH resolve as in the project. Writes nothing; `git show` is the only subprocess. No LabVIEW, no COM.

WHAT EXISTED: nothing loads a HEAD blob as a module here (grep -l "spec_from_loader\|git show HEAD" tools/bench/*.py: none).
PREDICTION: the self-test exits NON-ZERO and prints the FAIL rows of exactly this card's new cases; its pre-existing cases
PASS. The last line is `BEFORE <test>: rc <n>` + a RESULT line whose gate is "pre-fix run is non-zero".
"""
import hashlib
import importlib.util
import os
import runpy
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "hooks"))
import protocol as P  # noqa: E402

MODS = {"stage_prerun": ("tools/stage_prerun.py", "61d6f5902e9d2a05156b0d202d90fdea"),
        "guard_cycle": ("tools/hooks/guard_cycle.py", "c080fb7a5f06370b5c989bb6b2b5ce73"),
        "guard_write": ("tools/hooks/guard_write.py", "391a832448bce5cdbec2233317bf09c1"),
        "guard_assign": ("tools/hooks/guard_assign.py", "b9dc09bb935d23b5649e852886e1ebc7")}


def load_head(name, relp, want):
    b = subprocess.run(["git", "show", "HEAD:" + relp], cwd=ROOT, capture_output=True, timeout=60).stdout
    got = hashlib.md5(b).hexdigest()
    if got != want:
        raise SystemExit("HEAD blob of %s is %s, not the card input %s" % (relp, got, want))
    spec = importlib.util.spec_from_loader(name, loader=None)
    m = importlib.util.module_from_spec(spec)
    m.__file__ = os.path.join(ROOT, relp.replace("/", os.sep))
    sys.modules[name] = m
    exec(compile(b.decode("utf-8"), m.__file__, "exec"), m.__dict__)
    print("  FACT  %s loaded from HEAD (md5 %s)" % (relp, got[:8]), flush=True)


def main():
    test = sys.argv[1]
    import scope_header as SH
    h, err = SH.read(os.path.join(HERE, test))
    if err or not h or h.get("labview") != "none" or h.get("hardware") != "none" or not test.startswith("selftest_"):
        raise SystemExit("refused: %s is not a labview-none/hardware-none selftest (%s)" % (test, err or h))
    for n, (relp, want) in MODS.items():
        load_head(n, relp, want)
    sys.argv = [test]
    try:
        runpy.run_path(os.path.join(HERE, test), run_name="__main__")
        rc = 0
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else 1
    except Exception as e:                                                         # noqa: BLE001
        print("  FACT  pre-fix run raised %s: %s" % (type(e).__name__, str(e)[:160]), flush=True)
        rc = "raised"
    ok = rc != 0
    print("BEFORE %s: rc %s (%s)" % (test, rc, "non-zero as predicted" if ok else "ZERO - prediction NOT met"), flush=True)
    print(P.result_line(P.make_result(1 if ok else 0, 0 if ok else 1, None if ok else "pre-fix run is non-zero")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
