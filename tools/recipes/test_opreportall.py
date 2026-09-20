"""test_opreportall.py - ACCEPTANCE for OpReportAll_v0: same answers as report(), and how much faster?

The build recipe proved only that the op assembles (ExecState 1). CLAUDE.md: structural is not functional. Two
things have to be true before anything is built on this, and they are different questions:

  CORRECTNESS   report_all(target, cls) returns exactly what report(target, cls) returns - same objects, same
                uid/class/pos/owner, same ORDER. An op that returns plausible-looking arrays in a different
                order would corrupt every downstream index-based lookup silently.
  SPEED         the whole point. Baseline measured 2026-09-13: one op run is 10.4 ms on a small VI and
                960.8 ms on the main VI, and report() pays that ONCE PER OBJECT (626 nodes -> 618 s measured).

PROTOCOL - two targets, because they answer different questions:
  A. a SMALL scratch VI       -> correctness, cheap, every class
  B. the MAIN VI working copy -> the speed claim, on the VI the bottleneck was actually measured on.
     READ-ONLY (CLAUDE.md rule 1c allows headless COM reads of the main VI; nothing here writes or saves).

Timing is honest about what it includes: both paths are timed end to end from Python, warm (one discard run
first), so the number is what a caller actually waits for - not an internal figure.

  py tools/bgrun.py --max-min 40 --log tools/bench/test_opreportall.log -- py -u tools/recipes/test_opreportall.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SMALL_SRC = os.path.join(g.CLAUDEDEV, "GUIBENCH_v0.vi")
SMALL = os.path.join(g.CLAUDEDEV, "SCRATCH_reportall_small.vi")
MAIN = (r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking"
        r"\Min_Track N beads V6_ParallelLoop.vi")
g._run.__defaults__ = (6.0, 300.0)      # the main VI's Open VI Reference is ~1 s; a full sweep is minutes


def compare(target, cls, name):
    """Run both paths, compare object-for-object, and time them. Returns a result row."""
    print(f"\n---- {name}: class {cls!r} ----", flush=True)
    try:
        n = g.count(target, cls)
    except Exception as e:
        print(f"   count failed: {str(e)[:200]}", flush=True)
        return None
    print(f"   {n} objects", flush=True)
    if n == 0:
        return None

    try:
        t0 = time.time()
        new = g.report_all(target, cls)
        t_new = time.time() - t0
    except Exception as e:
        print(f"   report_all FAILED: {str(e)[:300]}", flush=True)
        return (name, cls, n, None, None, f"report_all failed: {str(e)[:120]}")
    print(f"   report_all: {len(new):4d} rows in {t_new:7.2f} s", flush=True)

    t0 = time.time()
    old = g.report(target, cls)
    t_old = time.time() - t0
    print(f"   report    : {len(old):4d} rows in {t_old:7.2f} s", flush=True)

    # CORRECTNESS. Compare the full tuple, in order - an order difference is a real defect, not cosmetic.
    if len(new) != len(old):
        verdict = f"LENGTH MISMATCH new={len(new)} old={len(old)}"
    else:
        diffs = []
        for a, b in zip(new, old):
            ka = (a["uid"], a["class"], tuple(a["pos"]), a["owner"])
            kb = (b["uid"], b["class"], tuple(b["pos"]), b["owner"])
            if ka != kb:
                diffs.append((ka, kb))
        if diffs:
            verdict = f"{len(diffs)} ROW MISMATCHES, first: {diffs[0]}"
            # An order-only difference is worth separating from a content difference.
            if sorted(map(str, (tuple(x[0]) for x in diffs))) == sorted(map(str, (tuple(x[1]) for x in diffs))):
                verdict += "  (same SET, different ORDER)"
        else:
            verdict = "IDENTICAL"
    speed = (t_old / t_new) if t_new > 0 else float("inf")
    print(f"   correctness: {verdict}", flush=True)
    print(f"   speed-up   : {speed:.1f}x", flush=True)
    return (name, cls, n, t_new, t_old, verdict)


def main():
    g._lv = None
    rows = []

    # ---------------- A. small VI: correctness ----------------
    print("======== A. SMALL VI - correctness ========", flush=True)
    try:
        g.close_panel(SMALL)
        time.sleep(0.3)
    except Exception:
        pass
    if os.path.exists(SMALL):
        try:
            os.remove(SMALL)
        except OSError:
            pass
    shutil.copyfile(SMALL_SRC, SMALL)
    g.open_panel(SMALL)
    time.sleep(0.8)
    g.report_all(SMALL, "Node")            # warm-up, discarded
    for cls in ("Node", "Wire", "ControlTerminal", "Diagram"):
        r = compare(SMALL, cls, "small")
        if r:
            rows.append(r)
    try:
        g.close_panel(SMALL)
        time.sleep(0.3)
        os.remove(SMALL)
        print("\nscratch small VI deleted", flush=True)
    except Exception as e:
        print("\nsmall cleanup:", str(e)[:120], flush=True)

    # ---------------- B. main VI: the speed claim ----------------
    # READ ONLY. Nothing here opens a panel, edits or saves - report/report_all only traverse.
    print("\n======== B. MAIN VI (read-only) - the speed claim ========", flush=True)
    if not os.path.exists(MAIN):
        print("   main VI working copy not found; skipping the speed half", flush=True)
    else:
        for cls in ("Property", "Node"):
            r = compare(MAIN, cls, "main")
            if r:
                rows.append(r)

    # ---------------- summary ----------------
    print("\n################ SUMMARY ################", flush=True)
    print(f"{'target':7} {'class':16} {'n':>5} {'report_all':>11} {'report':>10} {'speed':>7}  verdict", flush=True)
    ok = True
    for name, cls, n, t_new, t_old, verdict in rows:
        sp = f"{t_old / t_new:.1f}x" if (t_new and t_old) else "-"
        tn = f"{t_new:.2f}s" if t_new else "FAIL"
        to = f"{t_old:.2f}s" if t_old else "-"
        print(f"{name:7} {cls:16} {n:5d} {tn:>11} {to:>10} {sp:>7}  {verdict}", flush=True)
        if verdict != "IDENTICAL":
            ok = False
    print("\nVERDICT:", "PASS - report_all is a drop-in replacement" if ok else
          "FAIL - do NOT switch report() over yet; see the mismatching rows above", flush=True)
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
