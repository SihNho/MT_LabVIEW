r"""logclass.py - ONE definition of "is this log a build, or is it the machinery watching the build?"

WHY THIS FILE EXISTS. The same regex was copy-pasted into three places, and by 2026-09-16 it had already diverged:

    tools/audit_cycle.py      ^(peer_|retro|outcome_review|prior_?art)
    tools/hooks/guard_peer.py ^(peer_|retro|outcome_review|prior_?art)
    tools/hooks/guard_cycle.py ^(peer_|retro|outcome_review|prior_?art|audit_cycle|violations)   <- two terms ahead

Every widening was paid for by a false positive that blocked or mis-reported real work, four times over:

  1. 2026-09-15 12:5x  a reviewer's own sentence ("Fail the build on inequality...") was read out of `peer_*.log` as
     a build failure, and blocked the very build that review had approved (guard_peer).
  2. 2026-09-15         `retrospective.py` runs under bgrun, so its runner log is always NEWER than the review it
     produces - the cycle gate re-armed on the review that was meant to open it. A deadlock, not a strict check.
  3. 2026-09-15         the same for the outcome review and the compliance audit (guard_cycle only).
  4. 2026-09-16         `stall_pid*.log` counted as build logs, so audit A1 reported "NO BGRUN line" for two files
     that are RECORDS written by lv_stallcheck.ps1, not runs. Fixed here rather than in a fourth copy.

The lesson is CLAUDE.md's own: when a rule is broken twice, move it into one place. A classifier that three files
each maintain separately is three classifiers.

WHAT COUNTS AS A BUILD. A build log records an attempt to change or measure the LabVIEW artefact - a recipe or a
bench script run under bgrun. Everything else in tools/bench/ is the review and monitoring machinery observing that
work: peer dispatchers, the retrospective, the outcome review, the prior-art review, the compliance audit, the slug
tally, and the stall watchdog's records. Those are EVIDENCE about a cycle, never the thing under test - so they must
not gate a build, must not count toward a cycle's cost, and must not be scanned for failure strings.

KNOWN LIMIT, recorded rather than silently fixed. This classifies by FILENAME, which is a proxy. The honest test is
what the log's own `BGRUN START` line invoked: a build is one that ran something under `tools/recipes/` or
`tools/bench/`, and `tools/bench/probe_bgrun_inner.log` - a self-test of the bgrun runner that shells out to
`Write-Output` and never touches LabVIEW - is a build by name and not by nature. Moving to the content test would
change the audit's historical counts, so it is proposed, not done. See `is_build_log()`.

THE EXCLUSION IS ROLE-DEPENDENT - DO NOT COLLAPSE IT TO ONE LIST. Writing this file nearly introduced a fifth
bug: `stall_pid*.log` must be INVISIBLE to the build audit (it is not a run, so "no BGRUN line" is meaningless) and
VISIBLE to guard_peer, whose FAILURE_RE matches `^STALL:` on purpose - the user made recurring stall alerts a
mandatory peer-review trigger on 2026-09-14 ("이런 에러들도 반복되는 것 같으니 피어리뷰 반드시 필요하겠어. 규율에
적용하도록"). A single flat exclusion would have switched that rule off silently, which is precisely the kind of
quiet capability loss this project keeps paying for. Hence two predicates, not one.
"""
import os
import re

# Logs written BY a review dispatcher. Their contents quote failures verbatim on purpose, so they are evidence and
# never the thing under test. Excluded in EVERY role.
REVIEW_LOG_RE = re.compile(
    r"^("
    r"peer_"            # peer.ps1 dispatch transcripts - a reviewer's prose is not a build's output
    r"|retro"           # retrospective.py's runner log, always newer than the review it archives
    r"|outcome_review"  # the outcome layer's runner log
    r"|prior_?art"      # the prior-art layer's runner log
    r"|audit_cycle"     # the compliance audit reading logs is not a run that produced one
    r"|violations"      # the slug tally, likewise
    # REGISTERED AT BIRTH, NOT AFTER THE FIFTH FALSE POSITIVE (2026-09-16). The prior-art review of
    # docs/doc-lint-plan.md fired `already-failed` on exactly this: four dispatchers have broken this project by
    # having an unregistered log name, and `doc_ingest` is the fifth - its output is CONTRADICTIONS QUOTED VERBATIM
    # from documents, so audit_cycle's FAILURE_RE (`STOP at gate|VERDICT: BROKEN|FAIL`) would match a document's own
    # words and charge them to the cycle as build failures. `doc_lint` likewise prints the literal word FAIL by
    # design. Both are machinery: they read documents, they never touch the artefact.
    r"|doc_ingest"      # the ingest dispatcher's runner log - quotes documents verbatim, including their FAIL lines
    r"|doc_lint"        # the document linter prints PASS/WARN/FAIL about DOCUMENTS, never about a build
    r"|ingest_"         # a per-run ingest log (doc_ingest writes tools/bench/ingest_<date>.log)
    # REGISTERED AT BIRTH (2026-09-17), the same way `doc_ingest`/`doc_lint` were. `tools/cycle_runner.py` writes
    # `cycle_<n>.log` (one JUDGEMENT SESSION's whole transcript, which quotes gate refusals, "-> FAIL" lines and
    # failing logs verbatim by construction) and `cycle_runner.log` (its own ledger). A session transcript is
    # EVIDENCE ABOUT a cycle, never the thing under test: unregistered, it would arm guard_peer on the reviewer's
    # own quotations, count as a build in guard_cycle's retrospective budget, and make bgrun end rc=1 on any
    # session that merely printed a failure it had read. Note the trailing underscore - the historical
    # `cycle3_toolkit.log` / `cycle3b_toolkit.log` are REAL builds and keep counting as such.
    r"|cycle_"
    r")", re.I)

# Records that are OBSERVATIONS rather than runs. Not builds - but still real failure evidence, so guard_peer must
# keep seeing them. lv_stallcheck.ps1 writes these; they contain a `STALL:` line and never a `BGRUN START`.
WATCHDOG_LOG_RE = re.compile(r"^(stall_)", re.I)


def is_review_log(path):
    """Written by the review machinery. Excluded from build accounting AND from failure scanning."""
    return bool(REVIEW_LOG_RE.match(os.path.basename(path)))


def is_build_log(path):
    """Records an attempt to build or measure the artefact - the thing a cycle is made of.

    Use this for cycle accounting and bgrun-discipline checks (audit_cycle A1/A2, guard_cycle). Do NOT use it for
    failure scanning: a watchdog record is not a build, but it IS a failure that owes a review.
    """
    b = os.path.basename(path)
    return not (REVIEW_LOG_RE.match(b) or WATCHDOG_LOG_RE.match(b))


# The command a bgrun log's own `BGRUN START` line invoked. bgrun writes exactly:
#     BGRUN START 2026-09-22 08:10:56 limit 50.0 min: py -u tools/recipes/build_d1_m3a3.py
# (tools/bgrun.py:172). Only the LAST run in the file counts - bgrun APPENDS, so a rerun under a different command
# must not be judged by an earlier one. This is the same "read the command, not the filename" scoping guard_peer.py
# uses for the Jev exemption (:177-181): a filename-only rule can be laundered by naming a file anything.
_RECIPE_CMD_RE = re.compile(r"(?:^|[\s\"'=])(?:[\w./\\:-]*[\\/])?tools[\\/]recipes[\\/][\w.-]+\.py", re.I)
_FLAG_RE = re.compile(r"^-")


def last_bgrun_command(path):
    """The command string of the log's LAST `BGRUN START` line, or "" when the file has none."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read().lstrip("﻿")
    except OSError:
        return ""
    if "BGRUN START" not in text:
        return ""
    head = (text.rsplit("BGRUN START", 1)[-1].splitlines() or [""])[0]
    return head.split(" min: ", 1)[1].strip() if " min: " in head else ""


def is_recipe_build_log(path):
    """True only when this log's OWN last run INVOKED a `tools/recipes/*.py` file.

    ADDED 2026-09-22 for `docs/cycle27-plan.md` Pre-decided 112, and used by `guard_cycle.py`'s retrospective
    BUDGET SET ONLY. The gate's question is "has a CYCLE been built?", and its command-side pattern (`BUILD_RE`)
    already answers it with `tools/recipes/*.py`; the LOG side had drifted wider and was counting a model-API
    trial (`jev_trial.log`) and a hook self-test (`selftest_guard_peer_jev.log`) as cycle builds - 16 logs, of
    which the oldest and the newest build nothing in LabVIEW at all.

    `is_build_log` IS DELIBERATELY NOT TOUCHED. `guard_peer.py` arms the mandatory failed-prediction review off
    it, and a failing DIAGNOSTIC must keep arming that; narrowing the shared predicate would have switched the
    rule off silently - the exact quiet-capability-loss class this file's docstring was written about. Two
    predicates, not one, for the same reason `is_review_log` and `is_build_log` are two.

    A recipe named in a log's PROSE does not count: the test is the command in command position. `cp a.py
    tools/recipes/b.py` (the shape that trips `BUILD_RE`, STATUS "Where to look" hint 4) is not a recipe run
    either - the first non-flag `.py` token is what the interpreter executes, and here that is `cp`'s source.
    """
    if not is_build_log(path):
        return False
    cmd = last_bgrun_command(path)
    if not cmd:
        return False
    script = next((t for t in cmd.split() if t.lower().endswith(".py") and not _FLAG_RE.match(t)), "")
    return bool(script) and bool(_RECIPE_CMD_RE.search(" " + script))


# A JUDGEMENT SESSION IS NOT A REVIEW. `tools/cycle_runner.py` spawns exactly one headless judgement session per
# cycle - `claude.exe -p --model opus --effort max --output-format json ...` (cycle_runner.py:116) - under bgrun,
# writing `tools/bench/cycle_<n>.log` (:413). `REVIEW_LOG_RE` already keeps that transcript out of the BUILD set,
# which is right, but `audit_cycle` then summed its `total_cost_usd` into the REVIEW cost line. Cycle 64's audit
# printed `C4 ... REVIEWS 125 min 45 s; cost $63.9903 from 4 log(s)`, of which $51.6216 and ~102 min were the
# session itself (`tools/bench/cycle_59.log:62`); the three real reviews were $12.3687 and 1,490 s. So the device
# built to make the cost argument factual reported reviews as 94% of a cycle that spent ~19% of its wall-clock on
# them - `VIOLATION: device-failed` in `archive/peer/2026-09-22-retrospective-cycle64.md`, accepted in full.
# The session's spend is real and stays VISIBLE (audit_cycle's C4c); it is simply not review traffic.
_JUDGEMENT_PROGRAMS = ("claude", "claude.exe")
# Filename fallback, used ONLY when the file carries no `BGRUN START` at all: `tools/bench/cycle_runner.log` is the
# runner's own ledger, not a run. Same trailing underscore as REVIEW_LOG_RE, so `cycle3_toolkit.log` (a real 2026-09
# build) is untouched; `cycle_runner.log` matches on the `cycle_` prefix.
JUDGEMENT_LOG_RE = re.compile(r"^cycle_", re.I)


def command_program(cmd):
    """The PROGRAM a bgrun command line invokes - lower-cased basename, "" for an empty command.

    `MATERIAL=1 py -u tools/recipes/x.py` -> `py`; `C:\\...\\python.exe ...` -> `python.exe`. Leading env
    assignments are skipped because bgrun logs them in front of the program; a quoted program is unquoted.
    """
    for tok in cmd.split():
        bare = tok.strip("\"'")
        if "=" in os.path.basename(bare.replace("\\", "/")) and not bare.startswith("-"):
            continue                      # MATERIAL=1 and friends sit in front of the program
        return os.path.basename(bare.replace("\\", "/")).lower()
    return ""


def is_judgement_session_log(path):
    """True when this log records a whole JUDGEMENT SESSION spawned by `tools/cycle_runner.py`.

    Scoped the way `is_recipe_build_log` is - by the log's OWN last `BGRUN START` COMMAND, never by the filename
    when a sounder signal exists. The command's program is `claude.exe`; a PEER dispatch is not this even though
    it may dispatch the claude peer, because `peer.ps1` runs as `powershell -Command & 'tools/peer.ps1' -Agent
    claude ...` and the program in command position is `powershell`. The filename is consulted only for a file
    with no `BGRUN START` line at all (the runner's ledger).

    A `cycle_<n>.log` whose own run was the runner's DRY stand-in (`python -c "print('dry')"`) is deliberately
    False: it is not a judgement session and it spent nothing. This predicate reclassifies COST ONLY - it does not
    touch `is_build_log` (guard_peer arms the mandatory failed-prediction review off that) or `is_review_log`
    (a judgement transcript is still machinery, still excluded from builds and from failure scanning).
    """
    cmd = last_bgrun_command(path)
    if cmd:
        return command_program(cmd) in _JUDGEMENT_PROGRAMS
    return bool(JUDGEMENT_LOG_RE.match(os.path.basename(path)))


def split(paths):
    """(build_logs, machinery_logs) for cycle accounting - watchdog records group with the machinery."""
    builds, machinery = [], []
    for p in paths:
        (builds if is_build_log(p) else machinery).append(p)
    return builds, machinery
