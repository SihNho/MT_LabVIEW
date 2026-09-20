r"""SELF-TEST for the 2026-09-20 repair of `tools/hooks/guard_peer.py`'s FAILURE_RE (cycle 53, Pre-decided 37(i)).

WHAT WAS BROKEN. `guard_peer.py:71` documents the fleet's gate row as `  FAIL  ` and FAILURE_RE ended
`^\s*(?:->\s*)?FAIL\b`, which matches exactly that. The cycle-50/52 diagnostics print the MARKDOWN-BOLD form,
`  **FAIL**  ` (tools/bench/diag_movein_set.log:57; bgrun's INNER FAILURE echo at :128 repeats it). The asterisks
sit between the line start and the word, so the anchor could never reach `FAIL`, and a run whose prediction failed
passed the mandatory-review gate unseen. `bgrun.py:215` and `audit_cycle.py:76` had both already been repaired for
the same blind spot (`device-failed` rounds 4 and 5); this hook was the third copy of the list that never was.

WHAT WAS REPAIRED - BOTH ENDS, because the regex alone is the wrong half:
  (a) FAILURE_RE tolerates up to two asterisks: `^\s*(?:->\s*)?\*{0,2}FAIL\b`;
  (b) every gate emitter under tools/bench/ now prints the documented `  FAIL  `, so no new script inherits the
      bold form by copy-paste (the bold literal is how all ~35 of them came to say it).

WHAT THIS FILE CHECKS. The hook's LIVE pattern, imported from the hook itself - never a copy pasted in here, which
is the failure mode this whole class of bug is made of.

  A-gates  the repair works    : the bold log is seen failing NOW and was NOT seen failing under the old pattern.
  B-gates  nothing regressed   : a passing log is still not flagged, under old AND new.
  C-gates  the old vocabulary  : `  FAIL  `, `-> FAIL`, STALL, TIMEOUT, EXC, BROKEN, STOP still match.
  D-gates  no loosening        : prose that merely CONTAINS the word, `**FAILURE**`, and PASS rows do NOT match.
  E-gate   the emitters        : no tools/bench/*.py prints the bold form at the START of a line any more.

Plus a BLAST RADIUS section (facts only, no gates): every tools/bench build log the WIDENED pattern flags that the
OLD one did not, with its mtime, age, first failing line and whether an archive/peer review newer than it already
covers it. Widening a gate makes previously invisible failures visible, and each one blocks the next build until a
review exists - so the size of that set is a measurement the next cycle needs, not a surprise it should discover.

OUTPUT IS SANITISED ON PURPOSE. This script prints log lines that contain failure markers. If it printed them
verbatim, its own log would be read as a failing run by bgrun, audit_cycle and the very hook under test - a
self-poisoning test. Every echoed line goes through `safe()`, which breaks each marker with a `~`, and is
prefixed with `| `. A `FAIL` in this log is therefore always THIS script's own verdict, never quoted evidence.

Prior art checked before writing (CLAUDE.md, "check what already exists"): `tools/bench/selftest_bgrun_fail_scan.py`
(bgrun's copy of the same scan), `tools/bench/selftest_guard_cycle_rerun.py`, `tools/bench/selftest_motor_gate2.py`,
`tools/bench/selftest_cycle_runner_ff.py`. None of them tests guard_peer's FAILURE_RE; there was no reader for it.

Run:  MATERIAL=1 py tools/bgrun.py --max-min 6 --log tools/bench/selftest_guard_peer_failre.log \
          -- py -u tools/bench/selftest_guard_peer_failre.py
"""
import glob
import importlib.util
import os
import re
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BENCH = os.path.join(ROOT, "tools", "bench")
PEER = os.path.join(ROOT, "archive", "peer")
HOOK = os.path.join(ROOT, "tools", "hooks", "guard_peer.py")

BOLD_LOG = os.path.join(BENCH, "diag_movein_set.log")      # cycle 52's failing diagnostic: `  **FAIL**  P6`
PASS_LOG = os.path.join(BENCH, "verify_d1_s2.log")         # cycle 52's 23 pass / 0 fail verification

# The pattern EXACTLY as it stood before this repair (guard_peer.py:73, git-less project - transcribed from the
# file's own pre-edit text and kept here only as the BEFORE arm of the comparison).
OLD_RE = re.compile(r"OBSERVED:\s*EXC|'exc'|VERDICT:\s*BROKEN|STOP:|BGRUN TIMEOUT|^STALL:|^\s*(?:->\s*)?FAIL\b",
                    re.I | re.M)

passes, fails = [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""), flush=True)
    return ok


_MARKERS = (("FAIL", "F~IL"), ("STALL:", "STALL~"), ("STOP:", "STOP~"), ("BGRUN TIMEOUT", "BGRUN T~MEOUT"),
            ("OBSERVED: EXC", "OBSERVED~ EXC"), ("OBSERVED:EXC", "OBSERVED~EXC"),
            ("VERDICT: BROKEN", "VERDICT~ BROKEN"), ("'exc'", "'e~c'"))


_RC_RE = re.compile(r"\b(exit|rc)(\s*=\s*)([1-9]\d*)", re.I)


def safe(s):
    """Neutralise every failure marker so this script's own log is never read as a failing run.

    Covers bgrun's scan as well as guard_peer's: run 1 of this self-test ended `BGRUN END rc=1 (inner failure)`
    with 22/0 gates passing, because the C8 sample line quoted a real STOP row ending `rc=5` and bgrun's
    `\\b(?:exit|rc)\\s*=\\s*([1-9]\\d*)` alternative read the quotation as this run's own exit code. A test that
    cannot print its evidence without failing itself is the same class of bug it is testing.
    """
    out = s.rstrip()
    for a, b in _MARKERS:
        out = out.replace(a, b).replace(a.lower(), b.lower())
    return _RC_RE.sub(lambda m: "%s%s~%s" % (m.group(1), m.group(2), m.group(3)), out)


def _first_arg(tail):
    """The first argument of a `% ( ... )` tuple, split at the top-level comma only."""
    j = tail.find("(")
    if j < 0:
        return tail.strip()
    depth, buf = 0, []
    for ch in tail[j:]:
        if ch in "([{":
            depth += 1
            if depth == 1:
                continue
        elif ch in ")]}":
            depth -= 1
            if depth == 0:
                break
        elif ch == "," and depth == 1:
            break
        buf.append(ch)
    return "".join(buf).strip()


def emits_at_line_start(ln):
    """True when this source line prints `**FAIL**` as the FIRST thing on the printed line.

    That is the only position guard_peer's anchored pattern can ever see, so it is the only position the repair
    has to clear. A bold verdict in the MIDDLE of a sentence is invisible to the anchor whether it is bolded or
    not - and there the asterisks are what still lets audit_cycle's unanchored `\\*\\*FAIL\\*\\*` alternative see
    it, so removing them would LOSE a reader rather than gain one. Classified, not guessed: an f-string is a
    line-start emitter when the bold literal sits inside the string's FIRST `{...}` field; a %-format is one when
    the bold literal sits in the FIRST argument of its tuple; a bare literal when the string opens with it.
    """
    m = re.search(r'''(?:print|say)\(\s*\(?\s*([fr]*)(["'])(.*?)(?<!\\)\2''', ln, re.S)
    if not m:
        return "**FAIL**" in ln and ln.lstrip().startswith(("print", "say"))
    prefix, head, tail = m.group(1), m.group(3), ln[m.end():]
    body = re.sub(r"^(?:\\n)?\s*", "", head)
    if body.startswith("**FAIL**"):
        return True
    if "f" in prefix:
        g = re.match(r"\{([^{}]*)\}", body)
        return bool(g and "**FAIL**" in g.group(1))
    if body.startswith("%s"):
        return "**FAIL**" in _first_arg(tail)
    return False


def load_hook():
    spec = importlib.util.spec_from_file_location("guard_peer_under_test", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def last_run(text):
    """The slice guard_peer actually scans: bgrun APPENDS, so only the last run in the file counts."""
    return text.rsplit("BGRUN START", 1)[-1] if "BGRUN START" in text else text


def read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read().lstrip("﻿")


def first_hit(rx, text):
    for ln in text.splitlines():
        if rx.search(ln):
            return ln.strip()
    return ""


def main():
    t0 = time.time()
    print("=== selftest_guard_peer_failre - guard_peer.py FAILURE_RE, both ends of the 37(i) repair ===", flush=True)
    gp = load_hook()
    NEW_RE = gp.FAILURE_RE
    print("  hook file : %s" % HOOK, flush=True)
    print("  OLD pattern : %s" % safe(OLD_RE.pattern), flush=True)
    print("  NEW pattern : %s" % safe(NEW_RE.pattern), flush=True)
    print("  (patterns above are printed with failure markers broken by '~' - see the docstring)", flush=True)

    # ---- A: the repair does what it was made for -------------------------------------------------
    print("\n--- A: the bold-FAIL log is now SEEN ---", flush=True)
    if not gate("A0 the bold reference log exists", os.path.isfile(BOLD_LOG), BOLD_LOG):
        print("\n=== 0 pass / 1 fail - cannot continue without the reference log ===", flush=True)
        return 1
    bold_txt = last_run(read(BOLD_LOG))
    gate("A1 NEW pattern flags diag_movein_set.log as failing", bool(NEW_RE.search(bold_txt)),
         "| " + safe(first_hit(NEW_RE, bold_txt))[:110])
    gate("A2 OLD pattern did NOT flag it (this is the defect being repaired)", not OLD_RE.search(bold_txt))
    bolded = [ln for ln in bold_txt.splitlines() if re.match(r"^\s*\*\*FAIL\*\*", ln)]
    gate("A3 that log really carries the bold gate row", len(bolded) >= 1,
         "%d bold row(s); first: | %s" % (len(bolded), safe(bolded[0])[:90] if bolded else ""))

    # ---- B: nothing that used to pass now fails --------------------------------------------------
    print("\n--- B: a passing log is still read as passing ---", flush=True)
    if gate("B0 the passing reference log exists", os.path.isfile(PASS_LOG), PASS_LOG):
        pass_txt = last_run(read(PASS_LOG))
        gate("B1 NEW pattern does NOT flag verify_d1_s2.log", not NEW_RE.search(pass_txt),
             "| " + safe(first_hit(NEW_RE, pass_txt))[:110] if NEW_RE.search(pass_txt) else "")
        gate("B2 OLD pattern did not flag it either (so B1 is not a new tolerance)", not OLD_RE.search(pass_txt))

    # ---- C: the documented vocabulary still matches ----------------------------------------------
    print("\n--- C: every form the hook already had still matches ---", flush=True)
    for label, sample in (("C1 the documented gate row `  FAIL  `", "  FAIL  G12 ExecState is 1"),
                          ("C2 the arrow form `  -> FAIL`", "  -> FAIL: contract row 3"),
                          ("C3 the bold form (the repair)", "  **FAIL**  P6 #48 is on Diagram #686"),
                          ("C4 a stall record", "STALL: pid 21044 no COM answer for 900 s"),
                          ("C5 a bgrun timeout", "BGRUN TIMEOUT after 1200s"),
                          ("C6 an observed exception", "OBSERVED: EXC error 1057"),
                          ("C7 a broken verdict", "VERDICT: BROKEN"),
                          ("C8 a stop line", "STOP: not saved / rc=5"),
                          ("C9 the step marker", "step 4 'exc' To More Specific Class")):
        gate(label, bool(NEW_RE.search(sample)), "| " + safe(sample))

    # ---- D: the widening did not loosen the rule -------------------------------------------------
    print("\n--- D: what must still NOT match (a sentence is not a gate row) ---", flush=True)
    for label, sample in (("D1 the word inside prose", "the build did not FAIL, it was killed"),
                          ("D2 a longer word at line start", "  **FAILURE** counts are summarised below"),
                          ("D3 a passing gate row", "  PASS  G12 ExecState is 1"),
                          ("D4 a zero-fail summary", "=== 23 pass / 0 fail ==="),
                          ("D5 an emitter's own source line", "    print('PASS' if ok else 'FAIL')")):
        gate(label, not NEW_RE.search(sample), "| " + safe(sample))

    # ---- E: the other end - the emitters ---------------------------------------------------------
    print("\n--- E: no tools/bench/*.py prints the bold form at the START of a line ---", flush=True)
    start_bold, midline_bold = [], []
    for p in sorted(glob.glob(os.path.join(BENCH, "*.py"))):
        if os.path.abspath(p) == os.path.abspath(__file__):
            continue
        for i, ln in enumerate(read(p).splitlines(), 1):
            # A FULL-LINE COMMENT PRINTS NOTHING. The repair added `# \`FAIL\`, NOT \`**FAIL**\` ...` above each
            # emitter it changed, and counting those as surviving bold emitters made the INFO list read as 45
            # untouched sites when the real number is the handful below. Only executable lines are classified.
            if "**FAIL**" not in ln or ln.lstrip().startswith("#"):
                continue
            (start_bold if emits_at_line_start(ln) else midline_bold).append("%s:%d" % (os.path.basename(p), i))
    gate("E1 no line-start bold emitter remains under tools/bench/", not start_bold,
         ", ".join(start_bold[:8]) if start_bold else "0 found")
    print("  INFO  bold literals left mid-line / in prose (invisible to the anchor either way, so the bold "
          "form is what keeps audit_cycle able to see them): %d" % len(midline_bold), flush=True)
    for m in midline_bold:
        print("        %s" % m, flush=True)

    # ---- F: the gate must not be armed by its own test -------------------------------------------
    # Added the same hour the repair shipped. Widening FAILURE_RE made THIS log - which quotes `BGRUN TIMEOUT`,
    # `STOP:` and a bold FAIL as FIXTURES - the newest failing log, and every material run in the cycle was
    # refused by the gate its own self-test had armed. The fix is an exclusion in guard_peer's log SELECTION
    # (`SELFTEST_LOG_RE`), never a weaker pattern: F1 pins that the pattern still matches this file's contents,
    # so F2 can only be passing because the selection skipped it.
    print("\n--- F: guard_peer must not arm on selftest_*.log (its fixtures are failure-shaped by design) ---",
          flush=True)
    own_log = os.path.join(BENCH, "selftest_guard_peer_failre.log")
    if os.path.isfile(own_log):
        gate("F1 the pattern DOES match this self-test's own log text (so F2 is the exclusion, not a loophole)",
             bool(NEW_RE.search(last_run(read(own_log)))))
    gate("F2 guard_peer has a selftest exclusion in its log selection", hasattr(gp, "SELFTEST_LOG_RE"))
    gate("F3 it is name-scoped: a real diagnostic log is NOT excluded",
         not gp.SELFTEST_LOG_RE.match("diag_movein_set.log") and
         bool(gp.SELFTEST_LOG_RE.match("selftest_guard_peer_failre.log")))
    nf = gp.newest_failing_log()
    gate("F4 newest_failing_log() is not a selftest_*.log", not nf or
         not os.path.basename(nf[0]).lower().startswith("selftest_"),
         "now: %s" % (os.path.relpath(nf[0], ROOT) if nf else "(no failing log in the 6 h window)"))

    # ---- BLAST RADIUS: newly visible failures, facts only -----------------------------------------
    print("\n--- BLAST RADIUS (no gates): build logs the WIDENED pattern flags and the OLD one did not ---",
          flush=True)
    print("  a log within guard_peer's 6 h window (MAX_AGE_S=%d) and NOT covered by a newer archived review "
          "will block the next build." % gp.MAX_AGE_S, flush=True)
    now = time.time()
    rows = []
    for p in sorted(glob.glob(os.path.join(BENCH, "*.log"))):
        if gp.logclass.is_review_log(p):
            continue                       # a reviewer quoting a failure is evidence, never the thing under test
        try:
            txt = last_run(read(p))
            st = os.stat(p)
        except OSError:
            continue
        if OLD_RE.search(txt) or not NEW_RE.search(txt):
            continue
        names = gp.failure_names(p, txt)
        hit, _ = gp.newest_bound_peer(st.st_mtime, names)
        rows.append((st.st_mtime, os.path.relpath(p, ROOT), first_hit(NEW_RE, txt),
                     os.path.relpath(hit, ROOT) if hit else ""))
    rows.sort(reverse=True)
    print("  newly flagged: %d log(s)" % len(rows), flush=True)
    for mt, rel, line, cover in rows:
        age_h = (now - mt) / 3600.0
        print("   * %s" % rel, flush=True)
        print("       mtime %s  age %.1f h  %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mt)), age_h,
                                                   "WITHIN the 6 h gating window" if age_h * 3600 <= gp.MAX_AGE_S
                                                   else "older than the window - history, not an open loop"),
              flush=True)
        print("       first flagged line: | %s" % safe(line)[:150], flush=True)
        print("       covering review   : %s" % (cover if cover else "NONE newer than the log"), flush=True)

    npass, nfail = len(passes), len(fails)
    print("\n=== %d pass / %d fail ===  (%.1f s)" % (npass, nfail, time.time() - t0), flush=True)
    if fails:
        print("  not passing: %s" % "; ".join(fails), flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
