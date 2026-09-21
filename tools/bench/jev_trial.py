r"""jev_trial.py - MEASURE, do not adopt: can TypeSafe's Jev judge "same failure class?" better than our regex?

USER ORDER 2026-09-22 ("Jev 테스트 먼저"). NO LabVIEW IS TOUCHED BY THIS FILE: it reads tools/bench/*.log off disk
and makes HTTPS calls to api.typesafe.ai. No COM, no VISA, no motor, no camera, no GUI, no .vi is opened.

WHAT ALREADY EXISTS (checked before writing, per the material-session rule):
  - tools/logclass.py            -> the ONE definition of build-vs-machinery log. REUSED, not re-implemented.
  - tools/cycle_runner.py:190-259 -> RECIPE_RE / GATE_FAIL_RE / failed_recipes(). The baseline under test. Its
    regexes are COPIED HERE VERBATIM (not imported) because importing cycle_runner executes module-level setup and
    the brief forbids modifying it; the copies are marked BASELINE- and must stay byte-equal to their originals.
  - tools/bench/*.log            -> 216 failing build logs exist (scan 2026-09-22), so no log had to be generated.
  - no existing pair-similarity or log-clustering tool was found in tools/ or tools/bench/.

THE QUESTION. cycle_runner fires a firefighter cycle when the SAME recipe, or the SAME first failing gate line,
fails in two consecutive cycles. Both tests are string equality after normalisation. This measures how often that
string test agrees with the real answer - "would a fix for one fix the other?" - and whether a model does better.

PREDICTION CONTRACT (written before any call; the run is a FAILED PREDICTION if these do not hold):
  P1  The pair set is written to tools/bench/jev_trial.json BEFORE the first API call, and the file is re-written
      with results afterwards. A crashed run therefore still leaves the labelled pairs on disk.
  P2  Exactly len(PAIRS) <= 40 API calls are made, one per pair, each with exactly one noul question.
  P3  Every call returns {"type":"noul","noul": p} with 0 <= p <= 1, or is recorded as an ERROR pair (p=None) and
      excluded from accuracy/Brier. 429/529 are retried up to 3 times with backoff; any other status is an error.
  P4  BASELINE ACCURACY ON THE **POSITIVE** BLOCK IS 100% BY CONSTRUCTION and is NOT evidence about the baseline:
      those labels ARE the runner's own notion (brief step 1a). Only the HARD block, whose labels were set by
      reading the two summaries, can separate the two judges. The report states this next to every number.
  P5  The API key is read from the user environment and NEVER printed, logged, written to JSON, or passed as an
      argument (bgrun records command lines, so an argument would land in the log).

DEVIATION FROM THE BRIEF, recorded rather than quietly taken. The brief lists `build_s0_closeref_v1/v3` under the
POSITIVE block. Reading the two logs shows v1 stops at gate G3c (a census expectation about OpReportAll_v1's
property-node chain) and v3 gets past that and stops at G5 (the repaired op will not compile, ExecState 0) - the
brief's own definition of a HARD pair ("same recipe but a clearly different first gate"). Filing it as POSITIVE
would have written a label I believe is wrong into the ground truth, so it is filed as HARD with a written reason.
The `build_d1_routeb_v3..v7` and `build_d1_m3a*`/2026-09-21-22 families are used as the brief directs.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

# The console here is cp949: a replacement char from a log would crash a print mid-run and lose the calls
# already paid for. Never let the report die on an encoding.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # ...\tools
ROOT = os.path.dirname(ROOT)                                            # project root
BENCH = os.path.join(ROOT, "tools", "bench")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import logclass  # noqa: E402  - the one classifier

OUT_JSON = os.path.join(BENCH, "jev_trial.json")
API_URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"
MAX_CALLS = 40
THRESHOLD = 0.5

# ---------------------------------------------------------------- BASELINE (verbatim from cycle_runner.py)
BASELINE_BGRUN_START_RE = re.compile(r"^BGRUN START .*? min:\s*(.*)$", re.M)
BASELINE_BGRUN_FAIL_RE = re.compile(r"^BGRUN (?:END rc=([1-9]\d*)|TIMEOUT)", re.M)
BASELINE_GATE_FAIL_RE = re.compile(
    r"^\**\s*(FAIL\b[^\n]{0,120})|^BGRUN INNER FAILURE:.*?first:\s*([^\n]{0,120})", re.M)
BASELINE_RECIPE_RE = re.compile(r"^\s*(?:MATERIAL=1\s+)?(?:\S*[\\/])?py(?:thon)?(?:\.exe)?\s+(?:-\S+\s+)*"
                                r"(?:\S*[\\/])?tools[\\/]recipes[\\/]([\w.\-]+\.py)", re.I)
# cycle_runner only recognises tools/recipes/. Most of this project's failing runs are tools/bench/ diagnostics,
# so the baseline is ALSO given the bench form - a strictly more generous reading of its own rule, so the
# comparison cannot be won by handicapping it.
SCRIPT_RE = re.compile(r"^\s*(?:MATERIAL=1\s+)?(?:\S*[\\/])?py(?:thon)?(?:\.exe)?\s+(?:-\S+\s+)*"
                       r"(?:\S*[\\/])?tools[\\/](?:recipes|bench)[\\/]([\w.\-]+\.py)", re.I)

# a FAIL line written any of the three ways this project writes them
FAIL_LINE_RE = re.compile(r"^[ \t]*\*{0,2}\s*FAIL\b.*$", re.M)
INNER_FIRST_RE = re.compile(r"^BGRUN INNER FAILURE:.*?first:\s*(.*)$", re.M)


def read(p):
    with open(p, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def normalise(s):
    """uids and long numbers -> '#', hashes/timestamps flattened. Mirrors the baseline's own normalisation so the
    model is not handed an identifying detail the regex has already thrown away."""
    s = re.sub(r"\b[0-9a-f]{32}\b", "<md5>", s)
    s = re.sub(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}", "<ts>", s)
    s = re.sub(r"#\d+", "#", s)
    s = re.sub(r"\b\d{3,}\b", "#", s)
    s = s.replace(ROOT, "<root>")
    return s


def summarise(logname):
    """Compact failure summary of ONE log: script, how it ended, the first failing gate line + context.

    FALLBACK, documented because it extends the brief: ~40% of this project's failing logs carry no `FAIL` line at
    all (the routeb v3..v7 family dies on an unhandled RuntimeError). For those the summary is the final traceback
    instead, otherwise the pair would be two blanks and the trial would measure nothing.
    """
    txt = read(os.path.join(BENCH, logname))
    starts = list(BASELINE_BGRUN_START_RE.finditer(txt))
    if not starts:
        raise RuntimeError("no BGRUN START in %s" % logname)
    m = starts[-1]
    cmd, seg = m.group(1), txt[m.end():]
    f = BASELINE_BGRUN_FAIL_RE.search(seg)
    ended = "TIMEOUT" if (f and f.group(1) is None) else ("rc=" + f.group(1) if f else "?")
    sm = SCRIPT_RE.search(cmd)
    script = sm.group(1) if sm else "?"

    lines = seg.splitlines()
    fl = FAIL_LINE_RE.search(seg)
    where, body = None, []
    if fl:
        idx = seg[:fl.start()].count("\n")
        lo, hi = max(0, idx - 4), min(len(lines), idx + 11)
        body, where = lines[lo:hi], "first FAIL line + context"
    else:
        tb = seg.rfind("Traceback (most recent call last)")
        if tb >= 0:
            idx = seg[:tb].count("\n")
            body, where = lines[idx:idx + 15], "final traceback (no FAIL line in this log)"
        else:
            im = INNER_FIRST_RE.search(seg)
            if im:
                body, where = [im.group(0)], "bgrun inner-failure line"
            else:
                body = [ln for ln in lines if ln.strip()][-15:]
                where = "last non-empty lines (no FAIL line, no traceback)"
    body = [ln[:300] for ln in body]
    # HOW THE RUN ENDED, for every log alike: the last few lines before BGRUN END carry the summary gate count or
    # the terminal exception. Added because several HARD labels turn on the DIFFERENCE between "reached its own
    # summary with N failing gates" and "died on an unhandled exception", which the first FAIL line cannot show.
    # Applied uniformly to all 40 logs, never per pair.
    tail = [ln[:300] for ln in lines if ln.strip()][-6:]
    s = "log: %s\nscript: %s\nended: %s\nextract: %s\n%s\n--- how the run ended (last lines) ---\n%s" % (
        logname, script, ended, where, "\n".join(body), "\n".join(tail))
    return normalise(s)[:3200]


def baseline_signature(logname):
    """(recipe_key, gate_key) exactly as cycle_runner.failed_recipes() computes them."""
    txt = read(os.path.join(BENCH, logname))
    starts = list(BASELINE_BGRUN_START_RE.finditer(txt))
    m = starts[-1]
    cmd, seg = m.group(1), txt[m.end():]
    sm = SCRIPT_RE.search(cmd)
    recipe = re.sub(r"_v\d+(?=\.py$)", "", sm.group(1).lower()) if sm else None
    g = BASELINE_GATE_FAIL_RE.search(seg)
    gate = None
    if g:
        sig = re.sub(r"#\d+|\b\d{3,}\b", "#", g.group(1) or g.group(2) or "").lower()
        gate = re.sub(r"\s+", " ", sig).strip()[:60]
        if not gate:
            gate = None
    return recipe, gate


def baseline_same(a, b):
    ra, ga = baseline_signature(a)
    rb, gb = baseline_signature(b)
    if ra and rb and ra == rb:
        return True, "same recipe key '%s'" % ra
    if ga and gb and ga == gb:
        return True, "same gate sig '%s'" % ga
    return False, "recipe %r vs %r ; gate %r vs %r" % (ra, rb, ga, gb)


# ---------------------------------------------------------------- THE PAIR SET
# label: True = SAME failure class (a fix for one would fix the other). POSITIVE/NEGATIVE labels follow the
# brief's construction; HARD labels were set by READING both summaries - reason recorded per pair.
PAIRS = [
    # ---- POSITIVE (15): the runner's own notion. See P4: not evidence about the baseline.
    ("POS", "build_d1_routeb_v3_run6.log", "build_d1_routeb_v4_run7.log", True, ""),
    ("POS", "build_d1_routeb_v4_run7.log", "build_d1_routeb_v5_run8.log", True, ""),
    ("POS", "build_d1_routeb_v5_run8.log", "build_d1_routeb_v6_run9.log", True, ""),
    ("POS", "build_d1_routeb_v6_run9.log", "build_d1_routeb_v7_run10.log", True, ""),
    ("POS", "build_d1_routeb_v3_run6.log", "build_d1_routeb_v7_run10.log", True, ""),
    ("POS", "build_d1_routeb_v0.log", "build_d1_routeb_v0_run2.log", True, ""),
    ("POS", "build_d1_routeb_v0_run2.log", "build_d1_routeb_v0_run3.log", True, ""),
    ("POS", "build_opfstunnelterm_v0.log", "build_opfstunnelterm_v0_run2.log", True, ""),
    ("POS", "diag_s58_boolcarrier.log", "diag_s58_boolcarrier_run1.log", True, ""),
    ("POS", "diag_s58_boolcarrier_run1.log", "diag_s58_boolcarrier_run2.log", True, ""),
    ("POS", "build_opconnectnested_v1.log", "build_opconnectnested_v1_run2.log", True, ""),
    ("POS", "build_opconnectfromwire_v0.log", "build_opconnectfromwire_v0_run2.log", True, ""),
    ("POS", "diag_count_indicator.log", "diag_count_indicator_run2.log", True, ""),
    ("POS", "c62f_astcheck.log", "c64e_astcheck.log", True, ""),
    ("POS", "c64e_astcheck.log", "c65_astcheck.log", True, ""),

    # ---- NEGATIVE (15): different script AND different first gate, and manifestly different subject matter.
    ("NEG", "motor_gate2_live.log", "diag_s58_boolcarrier.log", False, ""),
    ("NEG", "build_s0_closeref_v3.log", "diag_c66c_coercion.log", False, ""),
    ("NEG", "diag_d0_inventory.log", "c53_row_class.log", False, ""),
    ("NEG", "drive_original_copy_v5.log", "diag_c67_addsr.log", False, ""),
    ("NEG", "build_opfstunnelterm_v0.log", "diag_c62_s3b_rows.log", False, ""),
    ("NEG", "diag_movein_set.log", "motor_gate2_live.log", False, ""),
    ("NEG", "reverse_census_walk.log", "diag_s3b_l0_createlocal.log", False, ""),
    ("NEG", "diag_qdonor2_stage.log", "diag_c65_s3b_row2c.log", False, ""),
    ("NEG", "diag_s56_transport2.log", "diag_c66_s3b_m3.log", False, ""),
    ("NEG", "replay_netmap_truncation.log", "diag_c61_localdir_write.log", False, ""),
    ("NEG", "diag_fstunnel_orphan_timeline.log", "diag_s57_typepair.log", False, ""),
    ("NEG", "c74_gate10_m3a2.log", "diag_d0_pickloop_liveness.log", False, ""),
    ("NEG", "diag_c64_connect_v2.log", "drive_original_copy_v4.log", False, ""),
    ("NEG", "diag_s57_ctmove_wire.log", "diag_c62_branch.log", False, ""),
    ("NEG", "diag_c66b_s3b_m3.log", "build_opconnectnested_v1.log", False, ""),

    # ---- HARD (10): labelled by reading both summaries. One sentence of reason each.
    ("HARD", "c63_astcheck.log", "c65_astcheck.log", False,
     "Same script (c60c_astcheck.py, our static recipe checker) but gate 3 (allow_broken=True never passed) and "
     "gate 7 (move_in neither imported nor called) are two unrelated defects in two different recipes it was "
     "pointed at, so fixing one changes nothing about the other - the regex's recipe-name test says SAME here "
     "because it identifies the CHECKER rather than the thing checked."),
    ("HARD", "c63_astcheck.log", "c74_gate10_m3a2.log", False,
     "Same checker script again, but gate 3 is a missing allow_broken argument while gate 10 is a %-format "
     "arity mismatch on one literal in a different recipe; unrelated defects sharing only the tool that found them."),
    ("HARD", "build_s0_closeref_v1.log", "build_s0_closeref_v3.log", False,
     "Same recipe family after the _vN strip, and both roll up to the same summary gate G-A0, but v1 never got "
     "past G3c (its model of OpReportAll_v1's property-node chain was wrong) while v3 got past that and produced "
     "ops that do not compile (G5, ExecState 0) - a fix for the census expectation does not make the op runnable."),
    ("HARD", "build_opfstunnelterm_v1_run1.log", "diag_fstunnel_preclean_twins.log", True,
     "Different script names (a build recipe vs a diagnostic) but the identical first gate B4 with identical "
     "ExecState readings - the diagnostic was written to reproduce the build's failure, so it is the same defect."),
    ("HARD", "build_opfstunnelterm_v0.log", "build_opfstunnelterm_v1_run1.log", False,
     "Same recipe after the _vN strip, but v0 died at gate Z on a wire-count/branch mismatch (40->40, no new "
     "tunnel) while v1 got a built op and died at B4 on the typed chain's legality - v1 exists because v0's "
     "defect was already fixed, so they are consecutive different failures of one effort, not one failure."),
    ("HARD", "diag_s2_scaffold.log", "wait_diag_s2.log", True,
     "Different script names (diag_s2_scaffold.py vs wait_bgrun_end.py) but wait_bgrun_end is a WAITER that tails "
     "the other log and re-prints its result, so the two logs report literally the same G12 failure of the same run."),
    ("HARD", "diag_c66_s3b_m3.log", "diag_c66b_s3b_m3.log", False,
     "Consecutive probes of the same M3 stage whose names differ only by the 'b' (so the _vN strip does NOT merge "
     "them), but c66 fails on a node sitting at an unexpected POSITION plus a watched wire on a structure terminal, "
     "while c66b gets all seven objects moved and fails on ExecState 0 - the second is the next question, not the same."),
    ("HARD", "diag_c65_s3b_row2.log", "diag_c65_s3b_row2b.log", False,
     "Same stage and adjacent names, but row2 fails because a source uid does not resolve to a live Traverse index "
     "while row2b fails because the ControlTerminal census and the diagram's Nodes[] list do not intersect at all - "
     "the second is a deeper, different fact about addressability that would not be fixed by repairing the first."),
    ("HARD", "diag_c62_s3b_rows.log", "diag_c62_s3b_build.log", True,
     "Different script names and different first gates (B1_c 'no top-level Nodes[] index for the source' vs B1_g "
     "'the new wire's far end is the LOCAL'), but both are the same route failing at the same precondition - the "
     "source is addressable only on an inner diagram - and both then skip B2 for want of a saved file."),
    ("HARD", "build_d1_routeb_v0_run3.log", "build_d1_routeb_v3_run6.log", False,
     "Same recipe key after the _vN strip, so the regex calls them one failure, but v0 ran to its own summary "
     "(84 pass/3 fail, S3w NO-ROUTE by the route's own gate) while v3 died on an unhandled RuntimeError when "
     "g.count(LoopTunnel) hit 'Traverse Failed' - a clean gate verdict and a crashed traverse are not one class."),
]


# ---------------------------------------------------------------- LABEL CORRECTIONS (post-hoc, evidence-carrying)
# Found by READING the logs after run 1, not by looking at any p value. Each of these three pairs is a POSITIVE
# ONLY under the brief's construction "same recipe basename => same failure class". The logs show the script was
# REPAIRED between the two runs, so run 2 is a different, later defect - i.e. each is a HARD pair by the brief's
# own definition ("same recipe but a clearly different first gate"), and its true label is DIFF.
#
# Applied by `--rescore`, which makes NO API call: it re-scores the p values already on disk, so the trial stays
# inside its 40-call budget. BOTH scorings are reported - the as-specified one and the corrected one - because
# re-labelling after seeing results is exactly the move that needs its evidence shown rather than asserted.
CORRECTIONS = [
    ("build_opconnectnested_v1.log", "build_opconnectnested_v1_run2.log", False,
     "run 1 died at gate Vx on a Python bug (EXC unhashable type: 'dict'), 15 pass/1 fail; run 2 is the repaired "
     "script reaching 31 pass/1 fail and failing T3 'the For loop is on the expected diagram' - fixing the dict "
     "bug does not put the For loop on the expected diagram."),
    ("build_opconnectfromwire_v0.log", "build_opconnectfromwire_v0_run2.log", False,
     "run 1 stopped at T2a2 because a PRECONDITION was false (the sink terminal was not bare, wire 5979); run 2 "
     "gets past that and fails T2c2, where the op's own `Wire.Is Broken?` reads True on the wire it created - a "
     "precondition bug and a broken-wire bug are two defects."),
    ("diag_count_indicator.log", "diag_count_indicator_run2.log", False,
     "run 1 failed G3/G4a and then crashed with FileNotFoundError on a doubled path ('tools\\tools\\bench\\...'); "
     "run 2 is the repaired script, ending 12 pass/1 fail at G6 'every terminal of w# resolved to an owner' "
     "(3 of 4) - the path bug and the unresolved owner are unrelated."),
]


def rescore():
    """Re-score the SAVED results under the corrected labels. Makes no API call."""
    d = json.load(open(OUT_JSON, "r", encoding="utf-8"))
    rows = d["pairs"]
    idx = {(r["log_a"], r["log_b"]): r for r in rows}
    print("=== jev_trial --rescore: corrected labels, NO API call (p values are the ones already on disk) ===\n")
    applied = 0
    for a, b, newlab, why in CORRECTIONS:
        r = idx.get((a, b))
        if r is None:
            print("  ?? correction has no matching pair: %s / %s" % (a, b))
            continue
        print("  CORRECTED %s vs %s : %s -> %s\n      %s" % (
            a, b, "SAME" if r["label"] else "DIFF", "SAME" if newlab else "DIFF", why))
        r["label_original"] = r["label"]
        r["label"] = bool(newlab)
        r["group"] = "HARD-corrected"
        r["reason"] = why
        applied += 1
    print("\n  %d correction(s) applied.\n" % applied)

    scored = [r for r in rows if r.get("jev") is not None]

    def acc(rs, which):
        if not rs:
            return float("nan"), 0, 0
        n = sum(1 for r in rs if (r["regex"] if which == "regex" else (r["jev"] >= THRESHOLD)) == r["label"])
        return n / len(rs), n, len(rs)

    print("=" * 78)
    print("CORRECTED RESULTS (threshold %.2f, %d scored)" % (THRESHOLD, len(scored)))
    print("=" * 78)
    print("%-16s %-24s %-24s" % ("block", "regex accuracy", "jev accuracy"))
    summary = {}
    for grp in ("POS", "NEG", "HARD", "HARD-corrected", "ALL"):
        rs = scored if grp == "ALL" else [r for r in scored if r["group"] == grp]
        ra, rn, rt = acc(rs, "regex")
        ja, jn, jt = acc(rs, "jev")
        summary[grp] = dict(n=rt, regex_acc=ra, regex_n=rn, jev_acc=ja, jev_n=jn)
        if rt:
            print("%-16s %-24s %-24s" % (grp, "%5.1f%% (%d/%d)" % (ra * 100, rn, rt),
                                         "%5.1f%% (%d/%d)" % (ja * 100, jn, jt)))
    # all pairs labelled by READING (the only ones that can separate the judges)
    read_rs = [r for r in scored if r["group"] in ("HARD", "HARD-corrected")]
    ra, rn, rt = acc(read_rs, "regex")
    ja, jn, jt = acc(read_rs, "jev")
    print("\nORDERED READING - every pair whose label was set by READING the logs (%d pairs):" % rt)
    print("   regex %5.1f%% (%d/%d)   |   jev %5.1f%% (%d/%d)" % (ra * 100, rn, rt, ja * 100, jn, jt))

    brier = sum((r["jev"] - (1.0 if r["label"] else 0.0)) ** 2 for r in scored) / len(scored)
    brier_regex = sum(((1.0 if r["regex"] else 0.0) - (1.0 if r["label"] else 0.0)) ** 2
                      for r in scored) / len(scored)
    print("\nBrier under corrected labels: jev %.4f | regex-as-0/1 %.4f" % (brier, brier_regex))

    print("\n--- REMAINING DISAGREEMENTS WITH THE CORRECTED LABEL ---")
    for r in scored:
        jv = r["jev"] >= THRESHOLD
        tags = ([] + (["JEV-WRONG"] if jv != r["label"] else []) +
                (["REGEX-WRONG"] if r["regex"] != r["label"] else []))
        if tags:
            print("  %-15s %-33s %-33s label=%-4s regex=%-4s jev=%.3f  %s" % (
                r["group"], r["log_a"][:33], r["log_b"][:33], "SAME" if r["label"] else "DIFF",
                "SAME" if r["regex"] else "DIFF", r["jev"], "+".join(tags)))

    d["corrected"] = dict(summary=summary, brier_jev=brier, brier_regex=brier_regex,
                          corrections=[{"log_a": a, "log_b": b, "label": l, "why": w} for a, b, l, w in CORRECTIONS])
    json.dump(d, open(OUT_JSON, "w", encoding="utf-8"), indent=1)
    print("\nraw -> %s" % OUT_JSON)
    print("\n=== jev_trial --rescore: %d pairs re-scored, %d label(s) corrected, 0 API calls ===" % (
        len(scored), applied))
    return 0


def get_key():
    k = os.environ.get("TYPESAFE_API_KEY")
    if k:
        return k
    # This session's process was started before the user set the variable, so it is in the USER scope only.
    # winreg reads that scope directly. The value is never printed, logged, or passed as an argument.
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as h:
            v, _ = winreg.QueryValueEx(h, "TYPESAFE_API_KEY")
            if v:
                return v
    except Exception:
        pass
    return None


QUESTION = {
    "type": "noul",
    "instructions": (
        "Two failing build logs from one LabVIEW VI-scripting project are given as log_a and log_b. Each is a "
        "compact extract: the script that ran, how the run ended, and the first failing gate line with context "
        "(uids and long numbers are replaced by '#'). Decide whether they fail for the SAME underlying reason - "
        "i.e. whether one fix would clear both. Judge the defect, not the file names: two different scripts can "
        "hit one defect, and one script can fail two unrelated ways on different runs."
    ),
    "criteria": {
        "true": ("The two runs are blocked by the same underlying defect, so a single fix would clear both. "
                 "Examples: the same script re-run with no change; a diagnostic written to reproduce a build's "
                 "failure, hitting the identical gate; two runs stopped by one broken operation."),
        "false": ("The two runs are blocked by different underlying defects, so fixing one would leave the other "
                  "failing. This includes consecutive versions of one script that got past the earlier defect and "
                  "died on a new one, and two unrelated defects that merely share the tool that reported them."),
    },
}


def ask(key, sa, sb, timeout=90):
    body = json.dumps({
        "model": MODEL,
        "state": {"log_a": sa, "log_b": sb},
        "questions": {"same_failure_class": QUESTION},
    }).encode("utf-8")
    req = urllib.request.Request(API_URL, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + key)
    delay = 3.0
    last = None
    for attempt in range(4):           # 1 try + 3 retries (P3)
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read().decode("utf-8", "replace")
            return json.loads(raw), time.time() - t0, None
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            last = "HTTP %s %s" % (e.code, detail)
            if e.code in (429, 529) and attempt < 3:
                print("    %s - backing off %.0fs" % (last[:80], delay), flush=True)
                time.sleep(delay)
                delay *= 2
                continue
            return None, time.time() - t0, last
        except Exception as e:                       # network/timeout/parse
            last = "%s: %s" % (type(e).__name__, str(e)[:200])
            if attempt < 3:
                time.sleep(delay)
                delay *= 2
                continue
            return None, time.time() - t0, last
    return None, 0.0, last


def extract_noul(resp):
    """Pull the noul probability out of the response without assuming one envelope shape."""
    if not isinstance(resp, dict):
        return None
    stack = [resp]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            if cur.get("type") == "noul" and isinstance(cur.get("noul"), (int, float)):
                return float(cur["noul"])
            if isinstance(cur.get("noul"), (int, float)) and "instructions" not in cur:
                return float(cur["noul"])
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur)
    return None


def find_usage(resp):
    if isinstance(resp, dict):
        for k in ("usage", "token_usage", "tokens"):
            if isinstance(resp.get(k), dict):
                return resp[k]
        for v in resp.values():
            u = find_usage(v)
            if u:
                return u
    return None


def main():
    print("=== jev_trial: does Jev judge 'same failure class' better than the runner's regex? ===")
    print("NO LabVIEW is touched by this run. Reads tools/bench/*.log + HTTPS to api.typesafe.ai.\n")

    # --- pair set, labels and BASELINE first. Written to disk BEFORE any API call (P1).
    missing = []
    for _, a, b, _, _ in PAIRS:
        for f in (a, b):
            if not os.path.isfile(os.path.join(BENCH, f)):
                missing.append(f)
    if missing:
        print("FAIL setup: missing log(s): %s" % sorted(set(missing)))
        return 1
    if len(PAIRS) > MAX_CALLS:
        print("FAIL setup: %d pairs exceeds the %d-call cap" % (len(PAIRS), MAX_CALLS))
        return 1

    # every log used must be a BUILD log by the project's one classifier, never review machinery
    bad = [f for _, a, b, _, _ in PAIRS for f in (a, b) if not logclass.is_build_log(f)]
    if bad:
        print("FAIL setup: non-build log(s) in the pair set: %s" % sorted(set(bad)))
        return 1

    rows = []
    for group, a, b, label, reason in PAIRS:
        sa, sb = summarise(a), summarise(b)
        same, why = baseline_same(a, b)
        rows.append(dict(group=group, log_a=a, log_b=b, label=bool(label), reason=reason,
                         regex=same, regex_why=why, summary_a=sa, summary_b=sb,
                         jev=None, latency_s=None, error=None))

    n_logs = len(set([r["log_a"] for r in rows] + [r["log_b"] for r in rows]))
    print("PAIRS: %d (POS %d / NEG %d / HARD %d) over %d distinct failing build logs" % (
        len(rows), sum(r["group"] == "POS" for r in rows), sum(r["group"] == "NEG" for r in rows),
        sum(r["group"] == "HARD" for r in rows), n_logs))
    json.dump({"stage": "pairs-only (pre-API)", "pairs": rows}, open(OUT_JSON, "w", encoding="utf-8"), indent=1)
    print("PASS P1 pair set written BEFORE any API call -> %s\n" % OUT_JSON)

    print("--- HARD pair labels (set by reading; these are the only pairs that can separate the two judges) ---")
    for r in rows:
        if r["group"] == "HARD":
            print("  %s | %s  vs  %s\n      label=%s regex=%s :: %s" % (
                r["group"], r["log_a"], r["log_b"], "SAME" if r["label"] else "DIFF",
                "SAME" if r["regex"] else "DIFF", r["reason"]))
    print()

    key = get_key()
    if not key:
        print("FAIL TYPESAFE_API_KEY is not readable (neither process env nor HKCU\\Environment). STOPPING - "
              "pairs and baseline are on disk; re-run once the variable is visible to this process.")
        json.dump({"stage": "pairs-only (no key)", "pairs": rows},
                  open(OUT_JSON, "w", encoding="utf-8"), indent=1)
        return 2
    print("key: present (length %d), read from %s. Never printed or logged.\n" % (
        len(key), "process env" if os.environ.get("TYPESAFE_API_KEY") else "HKCU Environment"))

    # --- the calls
    usage_tot, n_err = {}, 0
    consec_err = 0
    for i, r in enumerate(rows, 1):
        resp, dt, err = ask(key, r["summary_a"], r["summary_b"])
        r["latency_s"] = round(dt, 2)
        if err:
            r["error"] = err
            n_err += 1
            consec_err += 1
            print("  [%2d/%d] %-7s ERROR %s" % (i, len(rows), r["group"], err[:110]))
            # Do not burn 40 calls on a wrong envelope or a bad key: 3 in a row means the request shape or the
            # credential is wrong, which is a fact to report, not something to repeat 37 more times.
            if consec_err >= 3:
                print("\nABORT: 3 consecutive failures - the request shape or the credential is wrong. "
                      "Reporting what was measured rather than repeating it.")
                break
            continue
        consec_err = 0
        p = extract_noul(resp)
        if p is None:
            r["error"] = "no noul in response: " + json.dumps(resp)[:200]
            n_err += 1
            print("  [%2d/%d] %-7s NO-NOUL %s" % (i, len(rows), r["group"], json.dumps(resp)[:110]))
            continue
        r["jev"] = p
        u = find_usage(resp)
        if u:
            r["usage"] = u
            for k, v in u.items():
                if isinstance(v, (int, float)):
                    usage_tot[k] = usage_tot.get(k, 0) + v
        ok_j = (p >= THRESHOLD) == r["label"]
        ok_r = r["regex"] == r["label"]
        print("  [%2d/%d] %-7s label=%-4s regex=%-4s jev=%.3f  %s%s  (%.1fs)" % (
            i, len(rows), r["group"], "SAME" if r["label"] else "DIFF",
            "SAME" if r["regex"] else "DIFF", p,
            "J" + ("ok" if ok_j else "XX"), " R" + ("ok" if ok_r else "XX"), dt))

    # --- report
    scored = [r for r in rows if r["jev"] is not None]

    def acc(rs, which):
        if not rs:
            return float("nan"), 0, 0
        n = sum(1 for r in rs if (r["regex"] if which == "regex" else (r["jev"] >= THRESHOLD)) == r["label"])
        return n / len(rs), n, len(rs)

    print("\n" + "=" * 78)
    print("RESULTS  (threshold %.2f ; %d scored, %d errored)" % (THRESHOLD, len(scored), n_err))
    print("=" * 78)
    print("%-6s %-26s %-26s" % ("block", "regex accuracy", "jev accuracy"))
    summary = {}
    for grp in ("POS", "NEG", "HARD", "ALL"):
        rs = scored if grp == "ALL" else [r for r in scored if r["group"] == grp]
        ra, rn, rt = acc(rs, "regex")
        ja, jn, jt = acc(rs, "jev")
        summary[grp] = dict(n=rt, regex_acc=ra, regex_n=rn, jev_acc=ja, jev_n=jn)
        print("%-6s %-26s %-26s" % (grp, "%5.1f%% (%d/%d)" % (ra * 100, rn, rt) if rt else "n/a",
                                    "%5.1f%% (%d/%d)" % (ja * 100, jn, jt) if jt else "n/a"))
    print("\nP4 REMINDER: the POS block's labels ARE the regex's own rule, so its 100% there is arithmetic, not")
    print("             evidence. The ORDERED READING is the HARD block, labelled by reading the logs.")

    brier = sum((r["jev"] - (1.0 if r["label"] else 0.0)) ** 2 for r in scored) / len(scored) if scored else None
    brier_h = [r for r in scored if r["group"] == "HARD"]
    brier_hard = (sum((r["jev"] - (1.0 if r["label"] else 0.0)) ** 2 for r in brier_h) / len(brier_h)
                  if brier_h else None)
    # the regex as a 0/1 forecast, for a like-for-like Brier
    brier_regex = (sum(((1.0 if r["regex"] else 0.0) - (1.0 if r["label"] else 0.0)) ** 2 for r in scored)
                   / len(scored) if scored else None)
    lat = [r["latency_s"] for r in rows if r["latency_s"]]
    print("\nBrier (Jev, all scored): %s   (HARD only): %s   (regex as 0/1, all scored): %s" % (
        "%.4f" % brier if brier is not None else "n/a",
        "%.4f" % brier_hard if brier_hard is not None else "n/a",
        "%.4f" % brier_regex if brier_regex is not None else "n/a"))
    print("latency: mean %.2fs, min %.2fs, max %.2fs over %d calls" % (
        sum(lat) / len(lat), min(lat), max(lat), len(lat)) if lat else "latency: n/a")
    print("usage totals reported by the API: %s" % (json.dumps(usage_tot) if usage_tot else
                                                    "NONE - the response carried no usage/cost field"))

    print("\n--- DISAGREEMENTS WITH THE LABEL ---")
    dis = []
    for r in scored:
        jv = r["jev"] >= THRESHOLD
        tags = []
        if jv != r["label"]:
            tags.append("JEV-WRONG")
        if r["regex"] != r["label"]:
            tags.append("REGEX-WRONG")
        if tags:
            dis.append((r, tags))
            print("  %-5s %-34s %-34s label=%-4s regex=%-4s jev=%.3f  %s" % (
                r["group"], r["log_a"][:34], r["log_b"][:34], "SAME" if r["label"] else "DIFF",
                "SAME" if r["regex"] else "DIFF", r["jev"], "+".join(tags)))
    if not dis:
        print("  (none)")
    print("\n--- WHERE THE TWO JUDGES DISAGREE WITH EACH OTHER ---")
    for r in scored:
        if (r["jev"] >= THRESHOLD) != r["regex"]:
            print("  %-5s %-34s %-34s regex=%-4s jev=%.3f -> label=%s (%s)" % (
                r["group"], r["log_a"][:34], r["log_b"][:34], "SAME" if r["regex"] else "DIFF",
                r["jev"], "SAME" if r["label"] else "DIFF",
                "jev right" if (r["jev"] >= THRESHOLD) == r["label"] else "regex right"))

    json.dump({"stage": "complete", "threshold": THRESHOLD, "model": MODEL,
               "summary": summary, "brier_jev": brier, "brier_jev_hard": brier_hard,
               "brier_regex": brier_regex,
               "latency_mean_s": (sum(lat) / len(lat)) if lat else None,
               "usage_totals": usage_tot, "n_errors": n_err, "pairs": rows},
              open(OUT_JSON, "w", encoding="utf-8"), indent=1)
    print("\nraw -> %s" % OUT_JSON)

    npass = len(scored)
    print("\n=== jev_trial: %d/%d pairs scored, %d error(s) ===" % (npass, len(rows), n_err))
    return 0 if n_err == 0 else 1


if __name__ == "__main__":
    sys.exit(rescore() if "--rescore" in sys.argv else main())
