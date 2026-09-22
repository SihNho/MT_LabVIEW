r"""selftest_audit_c4c_split.py - `tools/audit_cycle.py:cost_split` + `tools/logclass.py:is_judgement_session_log`.

WHAT IS UNDER TEST. The cycle-64 retrospective's `VIOLATION: device-failed` (accepted in full,
`archive/peer/2026-09-22-retrospective-cycle64.md`): audit_cycle's C4 line charged the JUDGEMENT SESSION's own
bgrun to REVIEW cost. Cycle 64's audit printed

    C4 wall-clock inside bgrun, REVIEWS 125 min 45 s; cost $63.9903 from 4 log(s) that report one
    C5 total wall-clock 132 min 56 s  (reviews are 94% of it)

of which $51.6216 and 6,055 s were `tools/bench/cycle_59.log:62` (`"total_cost_usd":51.62158950000003`), the
session itself. The three real reviews were $12.3687 (6.3017 + 2.6899 + 3.3771) and 1,490 s. A cost line wrong by
5.2x in composition is the fault the device exists to prevent, so the repair MOVES the number (C4c) rather than
dropping it: C4 + C4c must still reconstruct the old figures to the cent.

PRIOR ART, CHECKED BEFORE A LINE WAS WRITTEN (`grep "^def " tools/logclass.py`, `ls tools/bench/selftest_*.py`,
`grep -n "C3 |C4 |cost" tools/audit_cycle.py`): `selftest_audit_cost_window.py` covers `window_runs()` (the round-6
per-RUN clipping) and is NOT touched by this repair; `selftest_logclass_recipebuild.py` (24/0) covers
`is_recipe_build_log`, the Pre-decided 112 predicate, and likewise does not look at cost. Nothing existing asserts
WHO a machinery log belongs to. The classifier reuses `logclass.last_bgrun_command`, written for Pre-decided 112,
instead of a second command parser.

PREDICTION CONTRACT, WRITTEN BEFORE THE RUN. Window = cycle 64's own audit window, 2026-09-22 01:09:00 ..
02:52:00 (the audit header printed `01:09 .. 02:51`; its `until` was "now", a few seconds past 02:51, and
cycle_59.log's last write is 02:51:36 - one minute is added so the same five machinery files are selected).
  G1  machinery set = cycle_58.log, cycle_59.log, peer_c74_gate10.log, peer_c74_m3a2_fmt.log, priorart_c74_m3a2.log
  G2  is_judgement_session_log: True for both cycle_*.log, False for all three review logs
  G3  C4c  judgement cost  == $51.6216 from exactly 1 log, and that log is cycle_59.log
  G4  C4c  judgement wall-clock == 6,055 s  (cycle_59.log's own `BGRUN END rc=0 after 6055s`)
  G5  C4   review cost == $12.3687 from exactly 3 logs   (the three real reviews, still counted as reviews)
  G6  C4   review wall-clock == 1,490 s
  G7  C4+C4c == $63.9903 and 7,545 s - the LITERAL figures the broken C4 printed: nothing is dropped
  G8  C5 total (builds 431 s + reviews + judgement) == 7,976 s = 132 min 56 s, UNCHANGED by the repair
  G9  cycle_58.log contributes 0 s and $0 (its run STARTED before the window; window_runs still clips)
  G10 a REAL review log is still a review: priorart/peer logs are not judgement, and their dollars are in C4
  G11 a BUILD log is still not a review: build_d1_m3a2.log is_build_log True, never in the machinery set
  G12 the shared predicates did not move: is_build_log / is_review_log unchanged on every fixture
  G13 synthetic scoping - `powershell ... peer.ps1 -Agent claude` is NOT a judgement session (program is
      powershell); `claude.exe -p` IS; `MATERIAL=1 py -u tools/recipes/x.py` is not; a no-BGRUN `cycle_runner.log`
      falls back to the filename; `cycle3_toolkit.log` (a real 2026-09 build) never does
  G14 the neighbouring self-tests re-run UNCHANGED as subprocesses, tallies read back
Every case is a FAIL if it disagrees. No LabVIEW is touched by this file.
"""
import glob
import os
import re
import subprocess
import sys
import tempfile
import time

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                              # noqa: BLE001
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import logclass                                                                    # noqa: E402
import audit_cycle                                                                 # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
passes, fails = [], []

# The cycle-64 window and the literal numbers that cycle's audit printed.
WIN_FROM, WIN_TO = "2026-09-22 01:09:00", "2026-09-22 02:52:00"
J_COST, J_SECS, J_LOG = 51.6216, 6055, "cycle_59.log"
R_COST, R_SECS, R_LOGS = 12.3687, 1490, 3
OLD_C4_COST, OLD_C4_SECS = 63.9903, 7545          # what C4 printed when the session was charged to reviews
BUILD_SECS, OLD_C5_SECS = 431, 7976               # C3 and C5, both unchanged by this repair


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
    return ok


def fact(line):
    print(("  FACT  %s" % line).encode("ascii", "replace").decode("ascii"), flush=True)


def head(t):
    print("\n---------- %s" % t, flush=True)


def write(tmp, name, body):
    p = os.path.join(tmp, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
    return p


def ts(s):
    return time.mktime(time.strptime(s, "%Y-%m-%d %H:%M:%S"))


BG = "BGRUN START 2026-09-22 08:10:56 limit 50.0 min: %s\n"


def main():
    print("=" * 100, flush=True)
    print("=== selftest_audit_c4c_split - the C3/C4/C4c cost split, on cycle 59's literal numbers", flush=True)
    print("=" * 100, flush=True)

    head("[1] THE REAL WINDOW - cycle 64's audit, %s .. %s" % (WIN_FROM, WIN_TO))
    cut, until = ts(WIN_FROM), ts(WIN_TO)
    logs = [p for p in glob.glob(os.path.join(BENCH, "*.log")) if cut <= os.path.getmtime(p) <= until]
    builds, machinery = logclass.split(logs)
    names = sorted(os.path.basename(p) for p in machinery)
    fact("build logs %d ; machinery logs %d -> %s" % (len(builds), len(machinery), names))
    gate("G1 the machinery set is the five files cycle 64 saw",
         names == ["cycle_58.log", "cycle_59.log", "peer_c74_gate10.log", "peer_c74_m3a2_fmt.log",
                   "priorart_c74_m3a2.log"], str(names))

    for n, want in (("cycle_58.log", True), ("cycle_59.log", True), ("peer_c74_gate10.log", False),
                    ("peer_c74_m3a2_fmt.log", False), ("priorart_c74_m3a2.log", False)):
        p = os.path.join(BENCH, n)
        if not os.path.isfile(p):
            gate("G2 %s exists on disk" % n, False, p)
            continue
        got = logclass.is_judgement_session_log(p)
        fact("%s program %r ; command %r" % (n, logclass.command_program(logclass.last_bgrun_command(p)),
                                             logclass.last_bgrun_command(p)[:90]))
        gate("G2 %s is_judgement_session_log is %r" % (n, want), got == want, "got %r" % got)

    head("[2] THE SPLIT ITSELF - cost_split over that window")
    cs = audit_cycle.cost_split(machinery, cut, until)
    for k in ("rsecs", "rcost", "rcosted", "rseen", "jsecs", "jcost", "jcosted", "jseen", "jlogs"):
        fact("cost_split[%s] = %r" % (k, cs[k]))
    gate("G3 C4c judgement cost is $%.4f from exactly 1 log, and it is %s" % (J_COST, J_LOG),
         round(cs["jcost"], 4) == J_COST and cs["jcosted"] == 1 and cs["jlogs"] == [J_LOG],
         "got $%.4f from %d log(s) %r" % (cs["jcost"], cs["jcosted"], cs["jlogs"]))
    gate("G4 C4c judgement wall-clock is %d s" % J_SECS, cs["jsecs"] == J_SECS, "got %d" % cs["jsecs"])
    gate("G5 C4 review cost is $%.4f from exactly %d logs" % (R_COST, R_LOGS),
         round(cs["rcost"], 4) == R_COST and cs["rcosted"] == R_LOGS,
         "got $%.4f from %d log(s)" % (cs["rcost"], cs["rcosted"]))
    gate("G6 C4 review wall-clock is %d s" % R_SECS, cs["rsecs"] == R_SECS, "got %d" % cs["rsecs"])
    gate("G7 NOTHING IS DROPPED: C4 + C4c reconstructs the broken line, $%.4f and %d s"
         % (OLD_C4_COST, OLD_C4_SECS),
         round(cs["rcost"] + cs["jcost"], 4) == OLD_C4_COST and cs["rsecs"] + cs["jsecs"] == OLD_C4_SECS,
         "got $%.4f and %d s" % (cs["rcost"] + cs["jcost"], cs["rsecs"] + cs["jsecs"]))
    bsecs = 0
    for p in builds:
        for seg in audit_cycle.window_runs(audit_cycle.read(p), cut, until):
            for m in re.finditer(r"BGRUN (?:END rc=\d+|TIMEOUT killed) after (\d+)s", seg):
                bsecs += int(m.group(1))
    gate("G8 C3 builds %d s and C5 total %d s are UNCHANGED by the repair" % (BUILD_SECS, OLD_C5_SECS),
         bsecs == BUILD_SECS and bsecs + cs["rsecs"] + cs["jsecs"] == OLD_C5_SECS,
         "got C3 %d s, C5 %d s" % (bsecs, bsecs + cs["rsecs"] + cs["jsecs"]))
    only58 = audit_cycle.cost_split([os.path.join(BENCH, "cycle_58.log")], cut, until)
    gate("G9 cycle_58.log contributes 0 s / $0 - its run STARTED before the window (window_runs still clips)",
         only58["jsecs"] == 0 and only58["jcost"] == 0.0,
         "got %d s / $%.4f" % (only58["jsecs"], only58["jcost"]))
    only_rev = audit_cycle.cost_split([os.path.join(BENCH, n) for n in
                                       ("peer_c74_gate10.log", "peer_c74_m3a2_fmt.log", "priorart_c74_m3a2.log")],
                                      cut, until)
    gate("G10 A REAL REVIEW STILL COUNTS AS A REVIEW: the three review logs alone give $%.4f in C4 and $0 in C4c"
         % R_COST,
         round(only_rev["rcost"], 4) == R_COST and only_rev["jcost"] == 0.0 and only_rev["jcosted"] == 0,
         "got C4 $%.4f / C4c $%.4f" % (only_rev["rcost"], only_rev["jcost"]))

    head("[3] A BUILD LOG IS STILL A BUILD - the shared predicates did not move")
    bl = os.path.join(BENCH, "build_d1_m3a2.log")
    gate("G11 build_d1_m3a2.log is_build_log True, is_review_log False, is_judgement_session_log False",
         os.path.isfile(bl) and logclass.is_build_log(bl) is True and logclass.is_review_log(bl) is False
         and logclass.is_judgement_session_log(bl) is False,
         "exists=%r build=%r review=%r judge=%r" % (os.path.isfile(bl), logclass.is_build_log(bl),
                                                    logclass.is_review_log(bl),
                                                    logclass.is_judgement_session_log(bl)))
    gate("G11b a build log never enters the machinery set that feeds C4/C4c",
         bl not in machinery and bl in builds)
    for n in ("cycle_59.log", "peer_c74_gate10.log"):
        p = os.path.join(BENCH, n)
        gate("G12 %s is STILL is_review_log True / is_build_log False (unchanged)" % n,
             logclass.is_review_log(p) is True and logclass.is_build_log(p) is False)

    head("[4] SYNTHETIC SCOPING - the COMMAND decides, not the filename")
    tmp = tempfile.mkdtemp(prefix="c4c_st_")
    cases = [
        ("G13a a cycle-runner judgement session", "cycle_99.log",
         BG % "claude.exe -p --model opus --effort max --output-format json --permission-mode acceptEdits xx", True),
        ("G13b a peer dispatch OF the claude peer (program is powershell)", "peer_x.log",
         BG % "powershell -NoProfile -Command & 'tools/peer.ps1' -Agent claude -Role hypothesis -Slug x", False),
        ("G13c the prior-art review runner", "priorart_x.log",
         BG % "py -u tools/prior_art_review.py --slug x", False),
        ("G13d a recipe build under MATERIAL=1", "build_x.log",
         BG % "MATERIAL=1 py -u tools/recipes/build_d1_m3a3.py", False),
        ("G13e cycle_runner.log - the ledger, no BGRUN line: filename fallback", "cycle_runner.log",
         "2026-09-22 09:58 runner stopped\n", True),
        ("G13f cycle3_toolkit.log - a REAL 2026-09 build, no underscore after `cycle`", "cycle3_toolkit.log",
         "some build output with no bgrun line\n", False),
        ("G13g a dry-run stand-in in a cycle_*.log spends nothing and is not a session", "cycle_98.log",
         BG % "C:\\Python310\\python.exe -c print('dry')", False),
        ("G13h an absolute-path claude.exe", "cycle_97.log",
         BG % "C:\\Users\\KimLab\\AppData\\Local\\claude\\claude.exe -p --model fable --effort low x", True),
        ("G13i LAST run wins: a peer dispatch appended after a session", "cycle_96.log",
         BG % "claude.exe -p --model opus x" + "noise\n" + BG % "powershell -File tools/peer.ps1 -Agent codex",
         False),
    ]
    for label, name, body, want in cases:
        p = write(tmp, name, body)
        got = logclass.is_judgement_session_log(p)
        gate("%s -> %r" % (label, want), got == want,
             "got %r ; program %r" % (got, logclass.command_program(logclass.last_bgrun_command(p))))
    sess = write(tmp, "cycle_95.log",
                 BG % "claude.exe -p x" + 'COST: $9.0000  in 1 / out 1\nBGRUN END rc=0 after 100s\n')
    rev = write(tmp, "peer_y.log",
                BG % "powershell -File tools/peer.ps1 -Agent codex"
                + 'COST: $1.5000  in 1 / out 1\nBGRUN END rc=0 after 30s\n')
    cs2 = audit_cycle.cost_split([sess, rev], ts("2026-09-22 08:00:00"), ts("2026-09-22 09:00:00"))
    gate("G13j synthetic pair splits 9.00/100s to C4c and 1.50/30s to C4",
         (round(cs2["jcost"], 4), cs2["jsecs"], round(cs2["rcost"], 4), cs2["rsecs"]) == (9.0, 100, 1.5, 30),
         "got %r" % [cs2["jcost"], cs2["jsecs"], cs2["rcost"], cs2["rsecs"]])
    gate("G13k seen==parsed on both sides (the C4b visibility half still holds)",
         cs2["jseen"] == cs2["jcosted"] == 1 and cs2["rseen"] == cs2["rcosted"] == 1,
         "jseen %d/%d rseen %d/%d" % (cs2["jseen"], cs2["jcosted"], cs2["rseen"], cs2["rcosted"]))

    head("[5] THE NEIGHBOURING SELF-TESTS, RE-RUN UNCHANGED")
    for st in ("selftest_logclass_recipebuild.py", "selftest_guard_peer_jev.py", "selftest_guard_peer_failre.py",
               "selftest_audit_cost_window.py"):
        p = os.path.join(BENCH, st)
        if not os.path.isfile(p):
            gate("G14 %s exists" % st, False, p)
            continue
        try:
            env = dict(os.environ, MATERIAL="1")
            r = subprocess.run([sys.executable, "-u", p], cwd=ROOT, capture_output=True, text=True,
                               timeout=600, env=env)
            tail = (r.stdout or "")[-4000:]
            m = re.findall(r"(\d+)\s*pass\s*/\s*(\d+)\s*fail", tail, re.I)
            nfail = int(m[-1][1]) if m else None
            fact("%s rc=%r ; tally %r ; last line %r"
                 % (st, r.returncode, m[-1] if m else None,
                    ([ln for ln in tail.splitlines() if ln.strip()] or [""])[-1][:160]))
            gate("G14 %s still passes UNCHANGED (rc 0, 0 failures)" % st,
                 r.returncode == 0 and (nfail == 0 or nfail is None),
                 "rc=%r nfail=%r" % (r.returncode, nfail))
        except Exception as e:                                                     # noqa: BLE001
            gate("G14 %s still passes UNCHANGED" % st, False, "%s: %s" % (type(e).__name__, str(e)[:200]))

    print("\n" + "=" * 100, flush=True)
    print("=== GATES: %d pass / %d fail%s" % (len(passes), len(fails),
                                              ("; failing: " + ", ".join(fails)) if fails else ""), flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
