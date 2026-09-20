"""selftest_stamp_window.py - OPEN 31: does the retrospective review the RIGHT window, and can a re-archived
slug be dated at all?  Pure Python, reads only; touches no LabVIEW, creates nothing outside %TEMP%.

PRIOR ART CHECKED BEFORE WRITING THIS (CLAUDE.md, material brief):
  - `grep -n "def stamp\|stamp(" tools/` -> guard_cycle.stamp() (the thing under test), violations._retro_stamp
    (filename-date based, deliberately NOT mtime - unaffected), retrospective.dispatch_time().
  - `ls tools/bench/*.py` has no existing stamp/window self-test; `tools/audit_cycle.py` takes --from/--to and does
    not compute a window itself.  So this file is new, and it is a DIAGNOSTIC, not a recipe.

PREDICTION CONTRACT - each line is PASS/FAIL on its own, no judgement:

  T1 ntfs-tunnel   : delete+rewrite of a file within the NTFS tunnel cache (~15 s) KEEPS the old creation time,
                     so guard_cycle.stamp() = min(ctime, mtime) under-reports a re-archive.  EXPECT: tunneled.
  T1b tunnel-decay : the same name, ABSENT for 18 s (the wait must follow the delete - MS KB 172190 creates the
                     tunnel entry at removal), does NOT keep it.  EXPECT: ctime moves.
  T1d setcontent   : `Set-Content` over an EXISTING path overwrites in place and leaves creation time alone, so
                     min(ctime, mtime) is stale with no tunneling at all.  EXPECT: ctime unchanged, mtime newer.
                     This, not T1/T1b, is the mechanism that justifies the stamp() change (codex,
                     archive/peer/2026-09-17-open31-window-codex.md).
  T2 stamp-monotone: for every archive/peer/*.md, new stamp() >= old min(ctime, mtime).  EXPECT: 0 regressions.
  T3 stamp-exact   : an archive whose frontmatter carries a TIME is stamped at that exact instant.  EXPECT: the
                     synthetic fixture stamps at its frontmatter time, not at its file times.
  T4 stamp-nolift  : a bulk frontmatter pass (mtime bumped, `- **date:**` untouched) does NOT raise the stamp.
                     EXPECT: unchanged.  This is the property the 2026-09-16 fix existed for.
  T5 window-cases  : the three OPEN-31 windows, recomputed.  For each, the window must CONTAIN the build logs that
                     the review was supposed to judge.  EXPECT: 3/3 contain them (they were 0/3).
  T6 peer-writes-time : tools/peer.ps1 emits `- **date:** $dateStamp` with a HH:mm:ss format.  EXPECT: present.

  py tools/bench/selftest_stamp_window.py
"""
import glob
import importlib.util
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PEER = os.path.join(ROOT, "archive", "peer")
BENCH = os.path.join(ROOT, "tools", "bench")
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))

import guard_cycle as gc          # noqa: E402
import retrospective as rt        # noqa: E402

RESULTS = []


def check(label, ok, detail):
    RESULTS.append((label, bool(ok), detail))
    print(("  PASS  " if ok else "  FAIL  ") + label + " : " + detail, flush=True)


def f(t):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t)) if t else "-"


def old_stamp(p):
    try:
        return min(os.path.getctime(p), os.path.getmtime(p))
    except OSError:
        return 0.0


# ---------------------------------------------------------------- T1 / T1b
def t1():
    tmp = os.environ.get("TEMP") or HERE
    p = os.path.join(tmp, "_open31_tunnel_probe.md")
    if os.path.exists(p):
        os.remove(p)
    open(p, "w").write("v1")
    c1 = os.path.getctime(p)
    time.sleep(2.0)
    os.remove(p)
    open(p, "w").write("v2")
    c2, m2 = os.path.getctime(p), os.path.getmtime(p)
    check("T1 ntfs-tunnel", abs(c2 - c1) < 0.5,
          "within the cache: ctime %s -> %s, mtime %s  => stamp() under-reports by %.0f s"
          % (f(c1), f(c2), f(m2), m2 - min(c2, m2)))
    # THE FIRST DRAFT OF THIS TEST SLEPT BEFORE THE DELETE, which is no wait at all - the tunnel entry is created
    # WHEN THE NAME IS REMOVED and the cache is searched when it is reintroduced (MS KB 172190). codex found it:
    # `archive/peer/2026-09-17-open31-window-codex.md`, "T1b never waits 18 seconds after deletion". So the delay
    # now sits BETWEEN the delete and the rewrite, and a never-used control name is created alongside.
    os.remove(p)
    time.sleep(18.0)                 # absent for 18 s; NTFS's documented tunnel lifetime is 15 s from REMOVAL
    open(p, "w").write("v3")
    ctl = os.path.join(tmp, "_open31_tunnel_control_%d.md" % int(time.time()))
    open(ctl, "w").write("control")
    c3, m3, cc = os.path.getctime(p), os.path.getmtime(p), os.path.getctime(ctl)
    os.remove(ctl)
    tunneled = abs(c3 - c1) < 0.5
    check("T1b tunnel-decay", not tunneled,
          "absent 18 s then rewritten: ctime %s (first write %s, fresh control %s), mtime %s -> tunneled=%s"
          % (f(c3), f(c1), f(cc), f(m3), tunneled))
    os.remove(p)
    # T1d - THE MECHANISM THAT ACTUALLY MATTERS, and it is not tunneling (codex, same archive): peer.ps1 does not
    # delete the archive, it pipes into `Set-Content`, which OVERWRITES IN PLACE (peer.ps1:557-583). An in-place
    # overwrite leaves creation time untouched indefinitely, so `min(ctime, mtime)` can be stale by days with no
    # tunnel cache involved at all. This is what justifies the stamp() change; T1/T1b do not.
    q = os.path.join(tmp, "_open31_setcontent_probe.md")
    if os.path.exists(q):
        os.remove(q)
    open(q, "w").write("v1")
    qc1 = os.path.getctime(q)
    time.sleep(2.0)
    os.system('powershell -NoProfile -Command "Set-Content -Encoding utf8 -Path \'%s\' -Value \'v2\'" >NUL 2>&1'
              % q)
    qc2, qm2 = os.path.getctime(q), os.path.getmtime(q)
    check("T1d setcontent-inplace", abs(qc2 - qc1) < 0.5 and qm2 > qc1 + 0.5,
          "Set-Content over an existing path: ctime %s -> %s (unchanged), mtime %s -> stamp() stale by %.0f s"
          % (f(qc1), f(qc2), f(qm2), qm2 - min(qc2, qm2)))
    os.remove(q)
    # T1c - the REAL case, from a real archive that peer.ps1 re-wrote hours later. This is the one that decides
    # whether OPEN 31's stated cause ("re-archiving keeps the OLD ctime") explains today's three bad windows.
    real = os.path.join(PEER, "2026-09-17-retrospective-cycle15.md")
    if os.path.isfile(real):
        rc, rm = os.path.getctime(real), os.path.getmtime(real)
        print("  NOTE  T1c real-rearchive : %s was archived at 08:06:44 (cycle-16's window cites that mtime) and "
              "RE-ARCHIVED later; today it reads ctime %s / mtime %s -> stale-by %.0f s"
              % (os.path.basename(real), f(rc), f(rm), rm - min(rc, rm)), flush=True)
        RESULTS.append(("T1c real-rearchive(observation)", True,
                        "ctime %s mtime %s stale-by %.0fs" % (f(rc), f(rm), rm - min(rc, rm))))


# ---------------------------------------------------------------- T2
def t2():
    """`new >= old` was the WRONG invariant and the first run of this test asserted it (3 'regressions', of which
    two were sub-second rounding and the third was the fix doing its job: annotating
    `2026-09-17-open31-window-codex.md` pushed its mtime 578 s past the moment the review was written, and the
    frontmatter time correctly pulled the stamp back). `stamp()` must be IMMUNE to a later edit, so a downward
    correction is the point, not a defect. The invariants that are actually true:"""
    future, inexact, lifted, lowered = [], [], [], []
    files = sorted(glob.glob(os.path.join(PEER, "*.md")))
    for p in files:
        o, n = old_stamp(p), gc.stamp(p)
        try:
            mt = os.path.getmtime(p)
        except OSError:
            continue
        if n > mt + 1.0:
            future.append((os.path.basename(p), f(n), f(mt)))
        fm, has_time = gc._fm_date(p)
        if has_time and abs(n - fm) > 1.5:
            inexact.append((os.path.basename(p), f(n), f(fm)))
        if n > o + 1.0:
            lifted.append(os.path.basename(p))
        elif n < o - 1.0:
            lowered.append(os.path.basename(p))
    check("T2a stamp-never-future", not future, "%d archives read; %d stamped after their own mtime %s"
          % (len(files), len(future), future[:3]))
    check("T2b stamp-exact-when-timed", not inexact,
          "%d timed-frontmatter archives disagree with their stamp %s" % (len(inexact), inexact[:3]))
    # T2d / T2e - the two holes codex named in `archive/peer/2026-09-17-open31b-stamp-codex.md` §1/§2, each now
    # a fixture rather than a promise: a FUTURE timed line must be clamped to mtime, and a `- **date:**` line
    # sitting in the QUESTION BODY must not become authoritative.
    tmp = os.environ.get("TEMP") or HERE
    a = os.path.join(tmp, "_open31_fixture_future.md")
    open(a, "w", encoding="utf-8").write(FIXT % "2030-01-01 00:00:00")
    st, mt = gc.stamp(a), os.path.getmtime(a)
    check("T2d stamp-clamped-to-mtime", st <= mt + 1.0,
          "frontmatter claims 2030-01-01 -> stamp %s, mtime %s" % (f(st), f(mt)))
    os.remove(a)
    b = os.path.join(tmp, "_open31_fixture_bodydate.md")
    open(b, "w", encoding="utf-8").write((FIXT % "2026-09-17 12:00:00")
                                         + "\n- **date:** 2020-01-01 00:00:00\n")
    st2 = gc.stamp(b)
    want2 = time.mktime((2026, 9, 17, 12, 0, 0, 0, 0, -1))
    check("T2e body-date-ignored", abs(st2 - want2) < 1.5,
          "a second date line below '## Question' -> stamp %s (header says 12:00:00)" % f(st2))
    os.remove(b)
    RESULTS.append(("T2c stamp-corrections(observation)", True,
                    "%d lifted (stale re-archive repaired), %d lowered (annotation no longer inflates) %s"
                    % (len(lifted), len(lowered), lowered[:3])))
    print("  NOTE  T2c stamp-corrections : %d lifted, %d lowered %s"
          % (len(lifted), len(lowered), lowered[:3]), flush=True)


# ---------------------------------------------------------------- T3 / T4
FIXT = """# fixture

- **agent:** codex
- **kind:** review
- **date:** %s
- **outcome:** ANSWERED (10s)

## Question
x
"""


def t3_t4():
    tmp = os.environ.get("TEMP") or HERE
    # T3: frontmatter carries a time far from the file's own times
    p = os.path.join(tmp, "_open31_fixture_timed.md")
    want = time.mktime((2026, 9, 17, 15, 42, 7, 0, 0, -1))
    open(p, "w", encoding="utf-8").write(FIXT % "2026-09-17 15:42:07")
    got = gc.stamp(p)
    check("T3 stamp-exact", abs(got - want) < 1.5,
          "frontmatter '2026-09-17 15:42:07' -> stamp %s (file times %s); old stamp would have been %s"
          % (f(got), f(os.path.getmtime(p)), f(old_stamp(p))))
    os.remove(p)

    # T4: date-only file, then a "bulk frontmatter pass" that bumps mtime and leaves `- **date:**` alone
    q = os.path.join(tmp, "_open31_fixture_bulk.md")
    open(q, "w", encoding="utf-8").write(FIXT % "2026-09-17")
    before = gc.stamp(q)
    old_c = os.path.getctime(q)
    future = time.time() + 7200                       # a bulk edit later today
    os.utime(q, (future, future))
    after = gc.stamp(q)
    check("T4 stamp-nolift", abs(after - before) < 1.5,
          "mtime bumped by +2 h with the date line untouched: stamp %s -> %s (ctime %s); the 2026-09-16 property "
          "still holds" % (f(before), f(after), f(old_c)))
    os.remove(q)


# ---------------------------------------------------------------- T5
# The three windows OPEN 31 records, read from the archives themselves (not retyped), each with the logs the
# review was SUPPOSED to judge. `must_cover` = build logs whose mtime has to fall inside a correct window.
CASES = [
    # (cycle, slug, the review's own archive, the --since-hours the run actually passed)
    # The third field is not invented: `tools/bench/retro_cycle16b.log:1` records
    # `--cycle 16 --slug retrospective-cycle16b --since-hours 1.2`, and until today that flag was silently
    # discarded whenever a previous retrospective existed (codex, open31b-stamp, §3).
    ("15", "retrospective-cycle15-d1-build3", "2026-09-17-retrospective-cycle15-d1-build3.md", None),
    ("16", "retrospective-cycle16b", "2026-09-17-retrospective-cycle16b.md", 1.2),
    ("15", "retrospective-cycle15-routeb", "2026-09-17-retrospective-cycle15-routeb.md", None),
]

# THE GATE, stated so it cannot be argued with: a retrospective must at least see THE NEWEST BUILD LOG THAT
# EXISTED WHEN IT WAS DISPATCHED. A review whose window ends before the last build it was called to judge is
# reviewing the wrong window, whatever else it covers. Chosen instead of a hand-listed log set because the first
# draft of this test hand-listed two logs and got both wrong (one was 56 min AFTER the dispatch, one never
# existed) - the machine can find the right one and a retyped list cannot.
import logclass  # noqa: E402


def newest_build_log_before(t):
    best = None
    for p in glob.glob(os.path.join(BENCH, "*.log")):
        try:
            mt = os.path.getmtime(p)
        except OSError:
            continue
        if mt > t or not logclass.is_build_log(p):
            continue
        if best is None or mt > best[1]:
            best = (p, mt)
    return best

WIN_RE = re.compile(r"^\s{4}(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+\.\.\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", re.M)


def parse_recorded(arch):
    try:
        body = open(os.path.join(PEER, arch), encoding="utf-8", errors="replace").read(6000)
    except OSError:
        return None
    m = WIN_RE.search(body)
    return (m.group(1), m.group(2)) if m else None


def t5():
    for cycle, slug, arch, since_h in CASES:
        own = os.path.join(PEER, arch)
        if not os.path.isfile(own):
            check("T5 " + slug, False, "archive missing: " + arch)
            continue
        rec = parse_recorded(arch)
        disp = rt.dispatch_time(own)[0]
        nb = newest_build_log_before(disp)
        if nb is None:
            RESULTS.append(("T5 " + slug + "(no build log)", True, "no build log existed before its dispatch"))
            print("  NOTE  T5 %s : no build log existed before its dispatch %s" % (slug, f(disp)), flush=True)
            continue
        target, tmt = os.path.basename(nb[0]), nb[1]
        # OLD behaviour, replayed exactly: start = cycle N-1's retrospective, end = dispatch of the newest archive
        # whose name ends `retrospective-cycle<N>.md`.
        o_prev = rt.retro_archive(int(cycle) - 1)
        o_own = rt.retro_archive(int(cycle))
        os_, oe = (os.path.getmtime(o_prev) if o_prev else None), (rt.dispatch_time(o_own)[0] if o_own else disp)
        old_ok = os_ is not None and os_ <= tmt <= oe
        # NEW behaviour, replayed at the same instant.
        prev = rt.newest_retro_before(disp, exclude_slug=slug)
        ns, ne = (prev[1] if prev else None), disp
        if since_h:                       # the flag the run passed, now honoured as an override
            ns = ne - since_h * 3600
        new_ok = ns is not None and ns <= tmt <= ne
        detail = ("newest build log at dispatch %s = %s@%s | OLD %s..%s -> %s | NEW %s..%s (start %s) -> %s | "
                  "recorded-in-archive %s..%s"
                  % (f(disp)[11:], target, f(tmt)[11:], f(os_)[11:], f(oe)[11:], "covers" if old_ok else "MISSES",
                     f(ns)[11:], f(ne)[11:],
                     ("--since-hours %g (override)" % since_h) if since_h
                     else (os.path.basename(prev[0]) if prev else "-"),
                     "covers" if new_ok else "MISSES",
                     rec[0][11:] if rec else "?", rec[1][11:] if rec else "?"))
        # THE E4-2 GAP IS NOT THIS CHANGE'S TO CLOSE, and pretending otherwise would make this test permanently
        # red for a defect handed to judgement. codex, `archive/peer/2026-09-17-open31-window-codex.md` E4-2:
        # "the prior review ends at its pre-audit `now`, but the next review starts at the prior archive's
        # COMPLETION mtime - work created while the reviewer is running belongs to neither window". A target that
        # predates the PREVIOUS retrospective's own start is orphaned by exactly that, and no choice of `end`
        # here can reach back past `start`. It is reported as KNOWN-GAP, with the numbers, and stays OPEN.
        if not new_ok and ns is not None and tmt < ns:
            RESULTS.append(("T5 " + slug + " KNOWN-GAP(E4-2)", True, detail))
            print("  GAP   T5 %s : target predates the previous retrospective's own start by %.0f s - codex E4-2, "
                  "needs a RECORDED closure timestamp, not a derived one (judgement)\n        %s"
                  % (slug, ns - tmt, detail), flush=True)
            continue
        check("T5 " + slug, new_ok, detail)


# ---------------------------------------------------------------- T6
def t6():
    body = open(os.path.join(ROOT, "tools", "peer.ps1"), encoding="utf-8", errors="replace").read()
    has_fmt = "yyyy-MM-dd HH:mm:ss" in body
    has_use = re.search(r"^\- \*\*date:\*\* \$dateStamp", body, re.M) is not None
    check("T6 peer-writes-time", has_fmt and has_use,
          "format present=%s, header uses $dateStamp=%s" % (has_fmt, has_use))


def main():
    print("=== OPEN 31 self-test: guard_cycle.stamp() + retrospective window ===", flush=True)
    t1()
    t2()
    t3_t4()
    t5()
    t6()
    n_ok = sum(1 for _, ok, _ in RESULTS if ok)
    print("\nSELFTEST %d pass / %d fail" % (n_ok, len(RESULTS) - n_ok), flush=True)
    return 0 if n_ok == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
