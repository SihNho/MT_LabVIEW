r"""s1_savedcopy_census.py - READ-ONLY structural census of the SAVED COPY vs the ORIGINAL. EDITS NOTHING,
SAVES NOTHING, touches no motor and no camera.

WHY (cycle 46, act 4 brief): `tools/recipes/stage_d1_s1.py` phase A made the first COM `SaveInstrument` save of
a copy of the main VI this project has ever made - on an UNEDITED byte copy, with the ORIGINAL preloaded
read-only. The bytes moved (473,317 -> 475,141 B, md5 2a78e17c... -> e0112963...) and the saved copy then read
`ExecState` 1 COLD where a pristine byte copy reads 0 (`tools/bench/stage_d1_s1.log:36`,`:57`). WHAT THE SAVE
WROTE IS UNMEASURED. This file measures ONE thing: whether any of the nine pinned structural counts moved.
It reports the numbers; it decides nothing and it changes no gate anywhere.

WHAT ALREADY EXISTS - checked before a line was written (CLAUDE.md "check what already exists"):
  * `gscript.count` (`tools/gscript.py:1005`) - one op run per class, already built. NO NEW OP is created here.
  * `tools/bench/s0_op_census.py` - the same read-only-census SHAPE (fresh instance, per-VI loop, JSON out),
    but over the four traverse OP VIs, not over the main VI; it does not censusfor these nine classes.
  * `tools/recipes/stage_d1_s1.py:462-465` - the phase-C `{c: g.count(TARGET, c) for c in BEFORE}` census of
    ONE VI (the working copy). This file runs that same census over TWO VIs and prints the delta; the pinned
    expectation is the same dict, `build_d1_routeb_v7.py:427-428`.
  * `fresh()` and `Preload` are cut VERBATIM from `tools/recipes/stage_d1_s1.py:254-289`, so the reading is
    taken under exactly the condition phase A's save was taken under.
  * `tools/bench/bench_prep.labview_handles` - the handle reader, already built.

PREDICTION CONTRACT - printed before anything runs. Gates are PASS/FAIL; only the two md5 gates are FATAL,
because this is a MEASUREMENT, not a build:
  G0  (FATAL) the ORIGINAL's md5 is the pin `2a78e17c449cacdaf5da389818526859` BEFORE the run.
  G1  the saved arm `D1_s1arm_savetest.vi` is on disk and reads md5 `e0112963cc1b9e3be29d2bb053ba9029`,
      475,141 B - i.e. it is the file phase A left, not a later copy.
  G2  both VIs return an integer for each of the nine classes Diagram / Node / Wire / LoopTunnel /
      ControlTerminal / WhileLoop / Local / SubVI / Function.
  G3  the ORIGINAL's census equals the pinned BEFORE dict (Diagram 170 - Node 626 - Wire 1902 - LoopTunnel 132 -
      ControlTerminal 114 - WhileLoop 3 - Local 8 - SubVI 98 - Function 181), `build_d1_routeb_v7.py:427-428`.
      A FAIL here means the PIN is stale, not that the original changed - its md5 is gated separately.
  G4  the saved arm's census equals the ORIGINAL's, class by class. NO PREDICTION IS OFFERED for the outcome;
      both a match and a difference are the finding the brief asked for, and neither is interpreted here.
  G5  `ref_counts()['live'] == 0` at the end (reference hygiene).
  G6  (FATAL) the ORIGINAL's md5 is still the pin AFTER the run.

  py tools/bgrun.py --material --max-min 25 --log tools/bench/s1_savedcopy_census.log -- py -u tools/bench/s1_savedcopy_census.py
"""
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import gscript as g                                                              # noqa: E402
from bench_prep import labview_handles                                           # noqa: E402

ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
ARM = os.path.join(g.CLAUDEDEV, "D1_s1arm_savetest.vi")
ARM_MD5 = "e0112963cc1b9e3be29d2bb053ba9029"
ARM_SIZE = 475141
OUT = os.path.join(HERE, "s1_savedcopy_census.json")

# the exact nine, pinned at `tools/recipes/build_d1_routeb_v7.py:427-428`
PIN = dict(Diagram=170, Node=626, Wire=1902, LoopTunnel=132, ControlTerminal=114, WhileLoop=3, Local=8,
           SubVI=98, Function=181)
CLASSES = list(PIN)

g._run.__defaults__ = (6.0, 180.0)
passes, fails = [], []
REC = {"original": {"path": ORIGINAL, "md5_pin": ORIG_MD5}, "arm": {"path": ARM, "md5_pin": ARM_MD5},
       "pin": PIN, "census": {}, "delta": {}}


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=False):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{('  ' + detail) if detail else ''}", flush=True)
    if not ok and fatal:
        raise Stop(name)
    return ok


def fact(line):
    print(f"  FACT  {line}", flush=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def fresh(tag):
    """VERBATIM from `tools/recipes/stage_d1_s1.py:254-266`: a FRESH LabVIEW instance (standing restart
    authority, CLAUDE.md section 3), then rebind every cached proxy via `gscript.reset()`."""
    g.reset()
    try:
        rc = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "lv_restart.py")],
                            capture_output=True, text=True, timeout=600)
        fact(f"{tag}: lv_restart rc={rc.returncode}: {(rc.stdout or '').strip().splitlines()[-1:]}")
    except Exception as e:                                                        # noqa: BLE001
        fact(f"{tag}: lv_restart FAILED ({type(e).__name__}: {e})")
    g.reset()
    fact(f"{tag}: LabVIEW handles after the restart: {labview_handles()} (fresh baseline ~31,500)")


class Preload:
    """VERBATIM from `tools/recipes/stage_d1_s1.py:270-289`: hold the ORIGINAL resident READ-ONLY for the
    duration of the census. No panel is opened on it, nothing is run, nothing is saved. The single COM proxy
    is dropped in `__exit__` - the only name that ever holds it."""

    def __init__(self, tag):
        self.tag, self.app, self.vi = tag, None, None

    def __enter__(self):
        import pythoncom
        from win32com.client import dynamic
        pythoncom.CoInitialize()
        self.app = dynamic.Dispatch("LabVIEW.Application")
        self.vi = self.app.GetVIReference(ORIGINAL, "", False, 0)
        fact(f"{self.tag}: ORIGINAL resident READ-ONLY (LabVIEW {self.app.Version}), its own ExecState "
             f"{int(self.vi.ExecState)}; nothing opened on it, nothing saved")
        return self

    def __exit__(self, *exc):
        self.vi = None
        self.app = None
        fact(f"{self.tag}: preload references released; refs {g.ref_counts()}")
        return False


def census(tag, path):
    got = {}
    for c in CLASSES:
        try:
            got[c] = int(g.count(path, c))
        except Exception as e:                                                    # noqa: BLE001
            got[c] = f"ERROR {type(e).__name__}: {e}"
        print(f"    {tag} {c:16s} {got[c]}", flush=True)
    return got


def main():
    print(__doc__.split("PREDICTION CONTRACT")[1].split('"""')[0], flush=True)
    print(f"s1_savedcopy_census: ORIGINAL {ORIGINAL}", flush=True)
    print(f"s1_savedcopy_census: ARM      {ARM}", flush=True)

    m0 = md5(ORIGINAL)
    REC["original"]["md5_before"] = m0
    REC["original"]["size"] = os.path.getsize(ORIGINAL)
    fact(f"G0 ORIGINAL md5 BEFORE {m0}, {REC['original']['size']} B")
    gate("G0 the ORIGINAL's md5 is the pin BEFORE the run", m0 == ORIG_MD5, m0, fatal=True)

    REC["arm"]["exists"] = os.path.exists(ARM)
    if REC["arm"]["exists"]:
        REC["arm"]["md5"] = md5(ARM)
        REC["arm"]["size"] = os.path.getsize(ARM)
        fact(f"G1 ARM md5 {REC['arm']['md5']}, {REC['arm']['size']} B")
    gate("G1 the saved arm is on disk with phase A's md5 and size",
         REC["arm"].get("md5") == ARM_MD5 and REC["arm"].get("size") == ARM_SIZE,
         f"{REC['arm'].get('md5')} / {REC['arm'].get('size')}", fatal=True)

    fact(f"handles at entry: {labview_handles()}; refs {g.ref_counts()}")
    fresh("F0")

    with Preload("P0"):
        time.sleep(1.0)
        print("\n  === CENSUS: the ORIGINAL (read-only, resident)", flush=True)
        co = census("ORIG", ORIGINAL)
        print("\n  === CENSUS: the SAVED ARM", flush=True)
        ca = census("ARM ", ARM)

    REC["census"] = {"original": co, "arm": ca}
    ok_int = all(isinstance(co[c], int) and isinstance(ca[c], int) for c in CLASSES)
    gate("G2 both VIs returned an integer for all nine classes", ok_int,
         f"{[c for c in CLASSES if not (isinstance(co[c], int) and isinstance(ca[c], int))]}")

    print("\n  === SIDE BY SIDE  (delta = arm - original)", flush=True)
    print(f"    {'class':16s} {'ORIGINAL':>10s} {'SAVED ARM':>10s} {'delta':>8s} {'pin':>6s}", flush=True)
    for c in CLASSES:
        d = (ca[c] - co[c]) if (isinstance(co[c], int) and isinstance(ca[c], int)) else "n/a"
        REC["delta"][c] = d
        print(f"    {c:16s} {str(co[c]):>10s} {str(ca[c]):>10s} {str(d):>8s} {PIN[c]:>6d}", flush=True)

    off_pin = {c: (PIN[c], co[c]) for c in CLASSES if co[c] != PIN[c]}
    gate("G3 the ORIGINAL's census equals the pinned BEFORE dict", not off_pin, f"{off_pin} (empty = all match)")
    diff = {c: (co[c], ca[c]) for c in CLASSES if co[c] != ca[c]}
    REC["classes_that_differ"] = diff
    gate("G4 the saved arm's census equals the ORIGINAL's, class by class", not diff,
         f"{diff} (empty = identical) - NO prediction was offered; this line is the FINDING either way")

    rc_ = g.ref_counts()
    REC["ref_counts"] = rc_
    REC["handles_end"] = labview_handles()
    fact(f"ref_counts {rc_}; handles {REC['handles_end']}")
    gate("G5 no VI Server reference left live", rc_["live"] == 0, str(rc_))

    m1 = md5(ORIGINAL)
    REC["original"]["md5_after"] = m1
    fact(f"G6 ORIGINAL md5 AFTER {m1}")
    gate("G6 the ORIGINAL's md5 is still the pin AFTER the run", m1 == ORIG_MD5, m1, fatal=True)


if __name__ == "__main__":
    rc = 0
    try:
        main()
    except Stop as s:
        print(f"  FACT  STOP at a fatal gate: {s}", flush=True)
        rc = 1
    except Exception as e:                                                        # noqa: BLE001
        import traceback
        traceback.print_exc()
        print(f"  FACT  UNHANDLED {type(e).__name__}: {e}", flush=True)
        rc = 2
    finally:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(REC, f, indent=1, default=str)
        print(f"\nRESULT {len(passes)} PASS / {len(fails)} FAIL; artefact {OUT}", flush=True)
        if fails:
            print(f"  failing: {fails}", flush=True)
    sys.exit(rc if not fails else (rc or 1))
