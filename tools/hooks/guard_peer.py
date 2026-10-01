"""PreToolUse hook (Bash | PowerShell): a FAILED PREDICTION blocks the next build until a peer review exists.

WHY THIS IS A HOOK AND NOT A RULE. CLAUDE.md already says, in prose, that a failed prediction triggers mandatory
peer review. On 2026-09-13 that rule was skipped FOUR TIMES in one stretch of work while the rule was sitting in
the context window. The user named the reason exactly:

    "아니 그런데 규약을 셋팅해도 그럼 자꾸 회피한다는거잖아"

Prose rules do not fire at the moment of decision, and each individual skip is locally cheap - the same dynamic
the project already diagnosed for GUI clicking. The one thing that demonstrably worked here was `lv_gui.ps1`
REFUSING the action, which ended six rounds of GUI-creep at once. So this refuses too.

WHAT IT DOES. Before any command that runs a recipe or bench script, it looks at the most recent build/probe log
under tools/bench/. If that log recorded a prediction that did not hold - an `OBSERVED: EXC`, a step marked
'exc', or a BROKEN verdict - then a file must exist in archive/peer/ whose mtime is LATER than the log's. If not,
the command is blocked.

WHY THAT ARTEFACT. The gate has to demand something that cannot be produced by writing a sentence. "I considered
alternatives" is free; an archived peer exchange timestamped after the failure is not. The check is deliberately
on mtime rather than on content, because content checks invite writing a file to satisfy the checker.

WHO CAN LIFT IT (amended 2026-09-18, user's decision, TRIAL). Until today only codex or gemini could: the claude
peer shared the asking session's priors, so it could not be the framing adversary (D3, 2026-09-15). Codex is now
at 9 % of its weekly quota, and the user moved codex's roles onto claude sub-sessions "우선은 지금 말한 방법으로
몇 번 돌려보자". So an ANSWERED `-Agent claude -Role hypothesis` exchange (opus, effort max, web search, run under
codex's exact constraints) now discharges a failed prediction as well. Every other claude role still cannot.

JEV DISCHARGE (2026-09-22, docs/jev-integration-plan.md row #1). On the path that was about to BLOCK, the newest
accepted reviews are scored against this failure by tools/bench/jev_gate.py; at p >= 0.80 (user 2026-09-22) the build is allowed and
the charge is written into that review's own disposition section as `JEV-DISCHARGE: <log> (<ts>, p=<p>)`. It can
only ever cite an exchange that already passed review_quality() - so the adversary rule is untouched - and with no
key, an API error or any exception the gate behaves exactly as it did before. See main() for the full note.

ONE REVIEW PER ROW PER CYCLE (2026-09-22, user-approved "전부 적용해보자"). The FIRST rung, above both Jev
insertions and costing no model call: on the path that was about to BLOCK, an accepted review younger than six
hours that NAMES the failing log's own script (basename from the log's `BGRUN START` line, `_v\d+` stripped)
discharges it. A staged build re-runs one row as v3, v5, v7 and each re-run used to buy its own review of the
same row. Releases are recorded as `RULE-SAME-ROW` in tools/bench/jev_gate.log and as a `SAME-ROW:` citation in
the cited review's own disposition section. See same_row_review() and main().

JEV REVIEW LADDER (2026-09-22, docs/jev-integration-plan.md 2차 #1, USER-APPROVED 17:3x). One rung above the
discharge, and the only Jev insertion that CHANGES a rule rather than mechanising one: before asking "is this
already reviewed?", the gate asks which of three kinds the failure is. `our-script-bug` (our own Python died, or
every failing gate row is the gate's own expectation being wrong) releases the build and is recorded in
tools/bench/jev_ladder_allowed.jsonl; `already-reviewed-class` hands the decision to the ordinary discharge, which
can still only cite an exchange that passed review_quality(); `new-problem` changes nothing. It acts only at
p >= 0.80 on the consensus mean of five asks. See main().
Since 2026-09-24 (user, 03:5x) the verdict DRIVES the next action: every JEV-LADDER line and every allow/refuse
message ends `NEXT-ACTION: ...` (script bug -> patch and rerun, no review, no judgement turn; reviewed class ->
apply the cited review's disposition; otherwise -> hypothesis review owed), and the verdict is computed once per
(log path, log md5) - tools/bench/jev_ladder_cache.jsonl.

DELIBERATE LIMITS, stated so nobody mistakes this for more than it is:
  * It gates the NEXT build, not the analysis in between - reading logs, writing docs and dispatching the peer
    itself all pass.
  * `peer.ps1` invocations always pass, or the gate would block its own remedy.
  * It cannot tell a *good* review from a perfunctory one. It enforces that the step happened, not its quality.
  * PEER_GUARD_OFF=1 disables it, for benchmark cells that inherit project settings (same escape hatch as
    guard_bash.py's LV_GUARD_OFF). The main session never sets it.

Exit code 2 = block (stderr goes back to Claude); 0 = allow.
"""
import glob
import json
import os
import re
import sys
import threading
import time

# A HOOK THAT OUTLIVES ITS TIMEOUT IS AN ALLOW (repair 2026-09-24, cycle 71; docs/violation-decisions.md
# `## repeated-failure-class - 2026-09-24 03:53`). `.claude/settings.json` gives this hook 15 s, and Claude Code
# treats a PreToolUse hook that runs out its timeout as a NON-BLOCKING error - the tool call goes ahead. The Jev
# rungs below are network calls with 25 s per-call timeouts and 5-sample consensus: the offline replay of the
# cycle-70 launch that went through (tools/bench/replay_guard_peer_c70.py, tools/bench/replay_guard_peer_c70.log)
# measured ladder 22 s + discharge 98 s + gate-row advisory 18 s = 139 s on a case whose verdict, run to the end,
# was BLOCK. Live, the ladder line landed at 03:26:08 (13 s in) and the process was killed during the discharge, so
# stage_d1_l7_1_r2 launched at 03:26:11 with run 1's failure unreviewed. So: the Jev rungs run under HOOK_BUDGET_S
# of wall time counted from the start of main() (interpreter start-up is the remaining ~5 s margin), and when the budget runs out the gate FAILS CLOSED (blocks) and starts one detached
# `--warm` process that finishes the same ladder/discharge in the background, so that its caches
# (jev_ladder_cache.jsonl, jev_discharge_cache.json) answer the retry instantly. Self-test:
# tools/bench/selftest_guard_peer_budget.py.
HOOK_BUDGET_S = 10.0
WARM_TTL_S = 600

HERE =os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BENCH = os.path.join(ROOT, "tools", "bench")
PEER = os.path.join(ROOT, "archive", "peer")

# Commands that RUN something (a recipe or a bench script). Reading a log is not running a build.
RUNS_RE = re.compile(r"py[\w.]*\s+(?:-u\s+)?[^\s|;&]*tools[\\/](?:recipes|bench)[\\/][^\s|;&]*\.py|"
                     r"bgrun\.py", re.I)
# The CYCLE RUNNER is not a build (2026-09-21 11:5x): `bgrun.py ... -- py tools/cycle_runner.py` only spawns the
# judgement session that will itself dispatch the owed review; blocking the runner on a failing log left by a
# session the 600-min cap killed mid-cycle deadlocks the loop (nobody is left to dispatch anything).
RUNNER_RE = re.compile(r"tools[\\/]cycle_runner\.py|tools[\\/](?:bench[\\/])?jev_?[\w]*\.py", re.I)   # + Jev scripts: user 2026-09-22 "Jev는 면제" (no LabVIEW)
# The remedy itself, and pure inspection, must never be blocked.
EXEMPT_RE = re.compile(r"peer\.ps1|guard_peer|--help|\b(cat|head|tail|sed|grep|less|type|wc|ls|dir)\b", re.I)

# THE REMEDY, as one list instead of a hardcoded regex in main() (2026-09-16). `RUNS_RE` matches bare `bgrun.py`,
# so every backgrounded command counts as a build - including the REVIEW RUNNERS, which are thin wrappers around
# `peer.ps1` and are literally this gate's own remedy. A prior-art review dispatched the way STATUS.md prescribes,
# `py tools/bgrun.py -- py tools/prior_art_review.py ...`, was refused with "dispatch a peer first", which is a
# deadlock: the gate demanded a review and then blocked the review. `guard_cycle.py` has exempted these five
# runners since it was written; this file had not, the same two-copies-of-one-list drift CLAUDE.md records for the
# log classifier. Note `EXEMPT_RE` above is NOT what main() consults - it was deliberately narrowed after
# archive/peer/2026-09-14-stall-alert-wrappers-false-positive.md, so a build whose ARGUMENTS merely contain `dir`
# or `head` is not exempt. Nothing about which BUILDS are gated changes here.
REMEDY_RE = re.compile(r"peer\.ps1|guard_peer|"
                       r"tools[\\/](?:prior_art_review|retrospective|violations|audit_cycle|outcome_review)\.py",
                       re.I)

# `STALL:` = a record written by tools/lv_stallcheck.ps1 (2026-09-14, user: recurring stall alerts need peer review
# "규율에 적용하도록"): a stalled COM client is the failed prediction "this client finishes".
# `-> FAIL:` / `  FAIL  ` = a probe/test's own prediction-contract row (2026-09-14: test_opsubvis.log failed four
# contract rows without any of the older markers, so the gate would not have fired on it).
#
# `**FAIL**` ADDED 2026-09-20 (cycle 53, Pre-decided 37(i); recorded in docs/violation-decisions.md under
# `## device-failed - 2026-09-20 05:34`). The line above documents the fleet's gate row as `  FAIL  ` and the
# pattern matched exactly that - but the cycle-50/52 diagnostics print the MARKDOWN-BOLD form, `  **FAIL**  `
# (tools/bench/diag_movein_set.log:57, and bgrun's own INNER FAILURE echo at :128). The asterisks sit between the
# line start and `FAIL`, so the anchor `^\s*` could never reach the word, and a run whose prediction failed passed
# this gate unseen. `bgrun.py:215` and `audit_cycle.py:76` had both already been repaired for the same blind spot
# (`device-failed` rounds 4 and 5) and this hook was the third copy that never was. TWO ENDS, deliberately: the
# emitters under tools/bench/ now print the documented `  FAIL  ` (so nothing new inherits the bold form) AND the
# pattern tolerates up to two asterisks (so every log already on disk, and any recipe still printing it, is seen).
# `\*{0,2}` is NOT a loosening of the prose rule: the anchor, the word boundary and the `^\s*` prefix are all
# unchanged, so a sentence that merely CONTAINS the word FAIL still does not match.
# Self-test: tools/bench/selftest_guard_peer_failre.py (bold log -> seen failing; passing log -> still passing).
FAILURE_RE = re.compile(r"OBSERVED:\s*EXC|'exc'|VERDICT:\s*BROKEN|STOP:|BGRUN TIMEOUT|^STALL:"
                        r"|^\s*(?:->\s*)?\*{0,2}FAIL\b",
                        re.I | re.M)
MAX_AGE_S = 6 * 3600          # only recent failures gate; an old log is history, not an open loop
# SINGLE DEFINITION (2026-09-16 lint): this list lived here, in guard_cycle.py and in audit_cycle.py, and had
# already drifted two terms apart. It now lives in tools/logclass.py.
# THIS gate uses `is_review_log`, NOT `is_build_log` - the difference matters. A `stall_pid*.log` is not a build,
# but it IS a failure that owes a peer review (user, 2026-09-14), and FAILURE_RE matches its `^STALL:` line on
# purpose. Excluding non-builds here would switch that rule off silently.
sys.path.insert(0, os.path.join(ROOT, "tools"))
import logclass  # noqa: E402
import protocol  # noqa: E402

# C6 (session protocol v1, user-approved 2026-09-24). A run's verdict is its own `RESULT {...}` line(s) - any
# status != PASS or gates.fail > 0 - and, when it printed none, its exit code (`BGRUN END rc!=0` / TIMEOUT). The
# FAILURE_RE text scan above is kept ONLY for runs that STARTED before protocol.SWITCH_TS and carry no RESULT line,
# so no historical verdict changes. `^STALL:` is not a script-body scan but the watchdog's own record format
# (lv_stallcheck.ps1 writes no BGRUN lines), so it still arms the gate at any date (user 2026-09-14).
STALL_RE = re.compile(r"^STALL:", re.M)


def log_failure(text, mtime=None):
    """(failed, first failure line) for the LAST run of a WHOLE log text - protocol.log_verdict with this hook's
    legacy rule for pre-switch runs."""
    ts, cmd, seg = protocol.last_segment(text)
    if cmd and (protocol.all_result_lines(seg) or not protocol.is_legacy(ts, mtime)):
        m = STALL_RE.search(seg)
        if m:
            return True, (seg[m.start():].splitlines() or [""])[0].strip()
        v = protocol.run_verdict(seg)
        return bool(v["failed"]), v.get("first_fail") or "(see the log)"
    # LEGACY: a pre-switch run without a RESULT line, or not a bgrun run at all - EXACTLY the old reading, including
    # its segmentation (after the last `BGRUN START` substring), so no historical verdict changes.
    last = text.rsplit("BGRUN START", 1)[-1] if "BGRUN START" in text else text
    first = next((ln.strip() for ln in last.splitlines() if FAILURE_RE.search(ln)), None)
    return bool(FAILURE_RE.search(last)), first or "(see the log)"


def log_failure_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return log_failure(f.read().lstrip("﻿"), os.path.getmtime(path))
    except OSError:
        return False, "(see the log)"

# A SELF-TEST OF A FAILURE PATTERN IS A FILE FULL OF FAILURE-SHAPED TEXT (2026-09-20, cycle 53, judgement's
# decision). This is the SAME carve-out `peer_*.log` has carried since 2026-09-15 - "the gate reads build logs
# only; review logs are evidence, never the thing under test" - applied to the one other file class that quotes
# failure strings by construction. It arrived as a real regression an hour after FAILURE_RE was widened:
# `tools/bench/selftest_guard_peer_failre.log` became the newest failing log on its OWN FIXTURE line,
# `PASS  C5 a bgrun timeout  | BGRUN T~MEOUT after 1200s`, and blocked every material run in the cycle - a gate
# armed by its own test. Prior record for the class: STATUS.md's cycle-46 OPEN (b), "logclass.py counts
# `selftest_*.log` as a build".
#
# DELIBERATELY LOCAL, NOT IN logclass.REVIEW_LOG_RE. That list is consumed by bgrun (inner-failure scanning) and
# audit_cycle (cycle accounting) as well, and a self-test that genuinely FAILS must still end `BGRUN END rc=1`
# and must still be counted - otherwise a broken gate's own test could fail silently, which is worse than the
# regression being fixed. Only the "does this failure owe a PEER REVIEW" question is answered no here: a
# self-test's failing row is a bug in the test or in the tool it tests, to be fixed, not a failed prediction
# about the LabVIEW machine that a peer must attack.
# THE NAME IS THE CONTRACT: a file that is NOT a self-test must never be called `selftest_*`.
SELFTEST_LOG_RE = re.compile(r"^selftest_", re.I)
# ⚠️ SUPERSEDED FOR BGRUN LOGS 2026-09-25 (card 77-1; `device-failed`, archive/peer/2026-09-25-retrospective-cycle76.md,
# threshold 1). "The name is the contract" failed: `tools/bench/selftest_make_default.log` is a self-test BY NAME whose
# command (`py -u tools/bench/selftest_make_default.py`) builds, saves and cold-reads a scratch VI IN LABVIEW; its
# prediction failed (S3 2/3 values, rc=1) and the filename exemption hid it from this gate, so no JEV-LADDER line was
# ever written (tools/bench/jev_gate.log:887). The exemption is now decided by the log's LAST `BGRUN START` COMMAND -
# the rule logclass.command_kind (card 76-2) and the Jev half (STATUS OPEN 57) already follow: excluded only when
# every in-scope script in python command position is a `selftest_*.py` whose import closure never reaches LabVIEW
# (`selftest_exempt`). The filename rule survives ONLY for a file with no BGRUN START at all (logclass's "" case).
_LV_MODULES = {"gscript", "stagekit", "pythoncom", "win32com", "comtypes"}   # the COM path to LabVIEW
# CODE, not prose: a bare mention in a comment (this file's own docstring names lv_gui.ps1) must not mark a script -
# measured on the first self-test run, C9b: jev_gate -> guard_peer matched on its own comments. GUI clicks go through
# gscript._lv_gui / stagekit, both already in _LV_MODULES.
_LV_TEXT_RE = re.compile(r"Dispatch\(\s*[\"']LabVIEW\.Application", re.I)
_IMPORT_RE = re.compile(r"^\s*(?:from\s+([\w.]+)\s+import\b|import\s+([\w., ]+?)(?:\s+as\s+\w+)?\s*(?:#.*)?$)", re.M)
_SELFTEST_SCRIPT_RE = re.compile(r"(?:^|[\\/])selftest_[^\\/]*\.py$", re.I)


def _module_names(src):
    names = []
    for m in _IMPORT_RE.finditer(src):
        if m.group(1):
            names.append(m.group(1).split(".")[0])
        else:
            names += [x.strip().split(" ")[0].split(".")[0] for x in m.group(2).split(",") if x.strip()]
    return names


def script_touches_labview(script, _seen=None):
    """True when `script` (a path) or any PROJECT module it imports, transitively, reaches LabVIEW: imports one of
    _LV_MODULES or calls Dispatch on the LabVIEW application class. FAILS CLOSED: an unreadable script counts as True."""
    seen = _seen if _seen is not None else set()
    key = os.path.normcase(os.path.abspath(script))
    if key in seen:
        return False
    seen.add(key)
    try:
        with open(script, "r", encoding="utf-8", errors="replace") as f:
            src = f.read()
    except OSError:
        return True
    if _LV_TEXT_RE.search(src):
        return True
    dirs = [os.path.dirname(key), os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench"),
            os.path.join(ROOT, "tools", "hooks")]
    for name in _module_names(src):
        if name in _LV_MODULES:
            return True
        for d in dirs:
            cand = os.path.join(d, name + ".py")
            if os.path.isfile(cand):
                if script_touches_labview(cand, seen):
                    return True
                break
    return False


def selftest_exempt(start_line):
    """True when a bgrun START line's run is a PURE-PYTHON self-test: every in-scope script in python command position
    is a `selftest_*.py` and none of them reaches LabVIEW (`script_touches_labview`). Decided by the command only."""
    cmd = start_line.split(" min: ", 1)[1] if " min: " in start_line else start_line
    scripts = [next(g for g in m.groups() if g) for m in _CMDPOS_PY_RE.finditer(cmd)]
    scoped = [s for s in scripts if _SCOPE_SCRIPT_RE.search(s)]
    if not scoped or not all(_SELFTEST_SCRIPT_RE.search(s) for s in scoped):
        return False
    # gate-fp fp-11 (card 125-1): a MEASURED offline self-test entry (protocol.OFFLINE_SELFTESTS) is not followed into
    # function-local imports it never executes (stagexec.py:2058-2059 via selftest_case_frame_c124.py:27).
    ab = [s if os.path.isabs(s) else os.path.join(ROOT, s) for s in scoped]
    return not any(script_touches_labview(s) and not protocol.offline_selftest(s, cmd) for s in ab)


def _rel(p):
    """`os.path.relpath` that cannot raise - the SAME helper `tools/hooks/guard_cycle.py:518` has carried since
    2026-09-17, copied here because this hook never got it (the project's own "a fix landed in one guard and not
    its sibling" pattern, CLAUDE.md). On Windows `relpath` throws `ValueError: path is on mount 'C:', start on
    mount 'G:'` for a path on another drive; this hook formats a BENCH path into its refusal message, so a
    fixture log in a TEMP dir on C: made the hook itself raise instead of refusing -
    `tools/bench/jev_discharge.log:21-26`, rc=99. A refusal message is not worth a traceback."""
    try:
        return os.path.relpath(p, ROOT)
    except ValueError:
        return p


_FIRST_PY_RE = re.compile(r"\"([^\"]*\.py)\"|'([^']*\.py)'|([^\s\"'|;&]*\.py)\b", re.I)
_CMDPOS_PY_RE = re.compile(r"(?:^|[\s;&|(])py(?:thon)?[\w.]*\s+(?:-[\w-]+\s+)*"
                           r"(?:\"([^\"]*\.py)\"|'([^']*\.py)'|([^\s\"'|;&]*\.py))", re.I)
_SCOPE_SCRIPT_RE = re.compile(r"(?:^|[\\/])tools[\\/](?:recipes|bench)[\\/][^\\/]+\.py$", re.I)
_JEV_SCRIPT_RE = re.compile(r"(?:^|[\\/])jev[\w]*\.py$", re.I)


def in_prediction_scope(start_line):
    """True when a bgrun START line's command runs a tools/recipes/*.py or tools/bench/*.py script (not a Jev one)."""
    cmd = start_line.split(" min: ", 1)[1] if " min: " in start_line else start_line
    # IN SCOPE when ANY script in PYTHON COMMAND POSITION is a tools/recipes|bench script (not Jev) - judgement
    # 2026-09-24 (card chat-B4), after review archive/peer/2026-09-24-chatb3-samerow.md: a START line that quotes the
    # bgrun call (`py tools/bgrun.py ... -- py <script>`, the samerow fixture) and a utility prefix
    # (`py -u tools/lv_restart.py; py -u tools/recipes/build_d1_v0.py`, tools/bench/build_d1_v0_run4.log:1) are both
    # judged by the recipe/bench script. `py -c` probes stay out; .ps1 motor scripts stay with motor_gate.
    scripts = [next(g for g in m.groups() if g) for m in _CMDPOS_PY_RE.finditer(cmd)]
    return any(_SCOPE_SCRIPT_RE.search(s) and not _JEV_SCRIPT_RE.search(s) for s in scripts)


# THE JEV LEDGERS ARE NOT BUILD LOGS - EXCLUDED BY PATH (card 101-2, PD213(g)1, 2026-09-26). tools/bench/jev_gate.log
# (and its jev_*.log / jev_*.jsonl siblings) is the ledger this very hook and jev_gate.py APPEND to: every refusal
# writes a JEV-LADDER line, and JEV-GATEROW lines quote the gated log's `STOP` rows verbatim. The file has no
# BGRUN START, so the command-scoped Jev exemption below never saw it, and it became the "newest failing log" -
# re-arming the gate on the lines its own refusals had just written (tools/bench/cards/result_101-1.json: every
# Bash call of card 101-1 refused, archive/peer/2026-09-26-c100-6-jevgate.md). Keyed on the PATH (a file directly
# in BENCH whose basename starts `jev_`), never on content; no other log is affected.
JEV_LEDGER_RE = re.compile(r"^jev_[\w.-]*\.(?:log|jsonl)$", re.I)


def is_jev_ledger(p):
    """True for tools/bench/jev_*.log|.jsonl (BENCH resolved at call time, so a self-test's redirected BENCH counts)."""
    if not JEV_LEDGER_RE.match(os.path.basename(p)):
        return False
    return (os.path.normcase(os.path.dirname(os.path.abspath(p))) ==
            os.path.normcase(os.path.abspath(BENCH)))


def newest_failing_log():
    best = None
    for p in glob.glob(os.path.join(BENCH, "*.log")):
        if is_jev_ledger(p):
            continue
        # A peer-review transcript is not a build log. 2026-09-15 12:5x: `peer_wrong_owner_node.log` blocked the very
        # build its review had just approved, because the reviewer's own sentence "Fail the build on inequality..."
        # matched the failure pattern. Review logs are evidence, never the thing under test.
        # EXTENDED 2026-09-15 evening: the rule was written for `peer_*` only, so the retrospective, outcome-review
        # and prior-art dispatchers - which quote historical failures verbatim in their answers - were still being
        # read as builds. `priorart_test_run1.log` blocked the next run because the reviewer had CITED
        # `build_opgeterrors.log`'s "STOP: not saved / rc=5". Third time this session that a fix landed in one guard
        # and not its sibling; the pattern now lives in one place per hook.
        if logclass.is_review_log(p):
            continue
        try:
            st = os.stat(p)
        except OSError:
            continue
        if time.time() - st.st_mtime > MAX_AGE_S:
            continue
        if best is not None and st.st_mtime <= best[1]:
            continue
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                text = f.read().lstrip("﻿")        # a PowerShell-written log may carry a BOM; `^STALL:` must still anchor
        except OSError:
            continue
        # Only the LAST run in the file counts: bgrun appends, so a rerun that succeeded after a reviewed failure
        # must not re-close the loop (2026-09-14 11:1x: build_oppanelwiring_v0.log run 2 succeeded, the file's
        # mtime moved past the review, and the gate re-armed on run 1's STOP line).
        last = text.rsplit("BGRUN START", 1)[-1] if "BGRUN START" in text else text
        # THE JEV EXEMPTION, THE OTHER HALF OF IT (user, 2026-09-22: "Jev는 면제"; CLAUDE.md, the Jev exception
        # paragraph: "Jev scripts (tools/jev*.py, tools/bench/jev_*.py) are EXEMPT from the failed-prediction and
        # material gates - they touch no LabVIEW"). That decision was wired into RUNNER_RE, which exempts a Jev
        # script as a COMMAND, and nowhere else - so a Jev script's own log still ARMED this gate against every
        # other run. It did, measurably: tools/bench/jev_discharge.log (a self-test bundle whose FIXTURE text
        # quotes "STOP:" and "FAIL" lines by construction, the same "a gate armed by its own test" class
        # SELFTEST_LOG_RE exists for) blocked cycle 68's read-only LabVIEW diagnostic at 09:0x.
        # SCOPED BY THE COMMAND, NOT BY THE FILENAME: the exemption applies only when the log's LAST run was
        # started on a Jev script, which is exactly what the user exempted. A build that merely mentions Jev in
        # its output is untouched, and every non-Jev failure still gates.
        if RUNNER_RE.search((last.splitlines() or [""])[0]):
            continue
        # SCOPE = RECIPES AND BENCH SCRIPTS ONLY (session protocol v1 wiring, task card chat-B, 2026-09-24). A failed
        # PREDICTION is a recipe's or a diagnostic's; a bgrun run of a tools/*.py UTILITY (motor_gate, wiki_build,
        # doc_lint, cycle_runner, ...) or of a non-python command is machinery, not a prediction under test, and a
        # Jev script is exempt by the user's 2026-09-22 ruling. Decided by the FIRST `.py` token of the run's own
        # command, never by the log name. Files without a BGRUN START (the `STALL:` watchdog records) still gate.
        if "BGRUN START" in text and not in_prediction_scope((last.splitlines() or [""])[0]):
            continue
        # SELF-TEST EXEMPTION BY COMMAND (card 77-1): a pure-Python self-test is excluded; a self-test whose command
        # reaches LabVIEW gates like any diagnostic. No BGRUN START at all -> the old filename rule (logclass's "").
        if "BGRUN START" in text:
            if selftest_exempt((last.splitlines() or [""])[0]):
                continue
        elif SELFTEST_LOG_RE.match(os.path.basename(p)):
            continue
        if log_failure(text, st.st_mtime)[0]:
            best = (p, st.st_mtime, last)
    return best


# card chat-P1 1(d): the OFFLINE tools whose import closure reaches LabVIEW modules but which, in these modes, never open
# COM (stage_prerun stubs it; stagesim is the simulator). Matched per launched script, with the mode flag required.
OFFLINE_MODES = {"stage_prerun.py": re.compile(r"--(?:dry|prerun|rebase|check-launch|control-lint|buildarray-check|"
                                               r"opmodel-conformance|selftest-control-lint)\b"),
                 "stagesim.py": re.compile(r"\b(?:simulate|selftest)\b")}
BGRUN_NAME = "bgrun.py"          # the deadline runner: its CHILD is what runs; the wrapper itself is not judged


def offline_command(cmd):
    """True when every python script `cmd` launches (protocol._launched_scripts) is the bgrun wrapper, an OFFLINE_MODES
    tool in its offline mode, or a script whose import closure never reaches LabVIEW (script_touches_labview False).
    No launched script at all -> False (nothing to judge, the old gate applies)."""
    scripts = protocol._launched_scripts(cmd or "")
    judged = 0
    for s in scripts:
        b = os.path.basename(s).lower()
        if b == BGRUN_NAME:
            continue
        judged += 1
        mode = OFFLINE_MODES.get(b)
        if mode is not None and mode.search(cmd):
            continue
        if protocol.offline_selftest(s, cmd):          # gate-fp fp-11 (card 125-1): measured offline self-test
            continue
        if script_touches_labview(s):
            return False
    return judged > 0


def offline_card(payload, cmd):
    """The card id when the CALLER is a sub-agent bound to a task/1 card with flags.labview == 'none' and `cmd` is
    offline_command; else None. The binding is protocol's (tools/bench/cards/active.json), never the prompt text."""
    aid = (payload or {}).get("agent_id")
    if not aid:
        return None
    try:
        b = protocol.binding(aid)
        if not b:
            return None
        card = protocol.load_card(protocol._abs(b["card"]), None)
    except Exception:                    # noqa: BLE001 - unreadable binding/card: not exempt
        return None
    if str((card.get("flags") or {}).get("labview") or "none") != "none":
        return None
    return card.get("id") if offline_command(cmd) else None


def offline_cmd_lv_card(payload, cmd, log_path):
    """gate-fp fp-10 (card 125-1), the REVERSE of offline_card: (card id, labview flag) when the caller is bound to a card
    with flags.labview read/build, `cmd` is offline_command, and the failing `log_path` is NOT in that card's launch
    ledger (protocol.card_owns_log; unreadable ledger = owned = gated). Else None. The card's own failing log, an
    LV-touching command, an unbound caller and a labview:none card (offline_card's case) are not handled here."""
    aid = (payload or {}).get("agent_id")
    if not aid:
        return None
    try:
        b = protocol.binding(aid)
        if not b:
            return None
        card = protocol.load_card(protocol._abs(b["card"]), None)
    except Exception:                    # noqa: BLE001 - unreadable binding/card: not exempt
        return None
    lv = str((card.get("flags") or {}).get("labview") or "none")
    if lv == "none" or not offline_command(cmd):
        return None
    if protocol.card_owns_log(card.get("id"), log_path):
        return None
    return card.get("id"), lv


def failure_names(path, text):
    """The names a peer exchange must mention to count as a review OF this failure: the log's basename and every
    tools/recipes|bench script named in the log (its BGRUN START line names the recipe). Peer-attacked 2026-09-14:
    without this, ANY newer archive file - about anything - lifted the gate."""
    names = {os.path.basename(path)}
    for m in re.finditer(r"tools[\\/](?:recipes|bench)[\\/]([\w.-]+\.py)", text):
        names.add(m.group(1))
    return names


# WHAT COUNTS AS A REVIEW, beyond "a file appeared" (both added 2026-09-15):
#   * OUTCOME must be ANSWERED. A TIMEOUT / QUOTA / ERROR exchange is precisely what rule 5 calls
#     "told you NOTHING" - the gate used to accept one as a completed review, which is the same
#     false positive the rule was written to prevent (an `-Agent agy` typo dying instantly).
#   * THE AGENT MUST BE AN ADVERSARY. The claude peer (added the same day) is this project's rule and
#     consistency auditor, not the framing adversary: it shares the asking session's priors, so a
#     claude-only review did not discharge a FAILED PREDICTION (user's decision D3, 2026-09-15).
#
#     D3 AMENDED 2026-09-18 (user's decision, a TRIAL: "Codex 잔여량이 생각보다 얼마 남지 않음. 주간 한도 9%
#     남았음. 아무래도 Codex가 수행중인 역할을 fable로 구동하는게 어떨까 싶음." / "우선은 지금 말한 방법으로
#     몇 번 돌려보자"). ONE claude role now discharges a failed prediction: `hypothesis` - opus at effort MAX,
#     with WebSearch and WebFetch, running under codex's exact constraints (read-only, the adversarial
#     preamble, a bounded timeout, archived to archive/peer/). That role was built and self-tested on
#     2026-09-17 and both its arms ANSWERED; what changes today is only WHO the gate accepts, because codex
#     is at 9 % of its weekly quota and a gate that demands an agent the project cannot call is a stop, not a
#     safeguard. `-Agent claude` in ANY OTHER role is still not an adversary, and codex/gemini still count.
#     The `role:` frontmatter line is written by peer.ps1 from 2026-09-18; archives written before that carry
#     no role line, so a claude archive is read as `hypothesis` only when its model line says opus + effort
#     max - the routing that role is the only one to produce.
ADVERSARY_AGENTS = ("codex", "gemini")
CLAUDE_ADVERSARY_ROLE = "hypothesis"


def _claude_is_adversary(body):
    """True when a `-Agent claude` archive came from the ONE role that discharges a failed prediction."""
    r = re.search(r"^\-\s*\*\*role:\*\*\s*([\w()/-]+)", body, re.M)
    if r:
        return r.group(1).strip().lower() == CLAUDE_ADVERSARY_ROLE
    m = re.search(r"^\-\s*\*\*model:\*\*\s*(.+)$", body, re.M)
    model = (m.group(1) if m else "").lower()
    return "opus" in model and "effort max" in model


def review_quality(body):
    """(ok, reason) - why this archived exchange does or does not count as a failed-prediction review."""
    m = re.search(r"^\-\s*\*\*outcome:\*\*\s*(\w+)", body, re.M)
    outcome = (m.group(1) if m else "").upper()
    if not m:
        return True, ""          # pre-2026-09-15 archives carry no outcome line; do not retro-invalidate them
    if outcome != "ANSWERED":
        return False, f"outcome {outcome} - the call told you nothing"
    a = re.search(r"^\-\s*\*\*agent:\*\*\s*(\w+)", body, re.M)
    agent = (a.group(1) if a else "").lower()
    # 2026-10-01: `-Kind fact` (no -Agent) now goes to gemini first. A fact answer is a lookup, not a framing
    # adversary, for EVERY agent - without this line a default gemini fact archive would discharge a failed prediction.
    k = re.search(r"^\-\s*\*\*kind:\*\*\s*(\w+)", body, re.M)
    if k and k.group(1).lower() == "fact":
        return False, "kind fact is a lookup, not a framing adversary (needs a review: codex, gemini or claude/hypothesis)"
    if agent == "claude":
        if _claude_is_adversary(body):
            return True, ""
        return False, ("agent claude in a non-hypothesis role is the rule/consistency audit, not a framing "
                       "adversary (needs -Role hypothesis: opus, effort max)")
    if agent and agent not in ADVERSARY_AGENTS:
        return False, f"agent {agent} is not a framing adversary (needs codex, gemini or claude/hypothesis)"
    return True, ""


def newest_bound_peer(after_mtime, names):
    """A peer archive file newer than `after_mtime` that names the failure AND counts as a review.
    Returns (path, None) on success, or (None, [rejection reasons]) so the block message can say why
    an exchange that looks like a review was not accepted."""
    rejected = []
    for p in glob.glob(os.path.join(PEER, "*.md")):
        try:
            # CREATION time on Windows (st_ctime): filling in an OLD review's verdict lines must not re-open the gate for
            # a NEW failure (2026-09-14 13:1x: editing an earlier review lifted the gate on build_harness_display run 1).
            # Measured 2026-09-15: a bulk rewrite of all 216 archives moved every mtime to one instant and left every
            # ctime intact, so min(ctime, mtime) held the line - the "bulk edit opens the gate" hole does not exist.
            st = os.stat(p)
            born = min(st.st_ctime, st.st_mtime) if os.name == "nt" else st.st_mtime
            if born <= after_mtime:
                continue
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                body = f.read()
        except OSError:
            continue
        if not any(n in body for n in names):
            continue
        ok, why = review_quality(body)
        if ok:
            return p, None
        rejected.append(f"{os.path.basename(p)}: {why}")
    return None, rejected


# --- DEVICE: do not buy review N+1 while review N is undisposed -------------------------------------
# Added 2026-09-16, answering `repeated-failure-class` at its 4th occurrence (docs/violation-decisions.md, Round 2).
# Cycle 10 bought SIX prior-art/plan reviews in one afternoon - 48 min 40 s and $28.5530 - of a plan that changed
# under every reviewer, while 23 archived reviews sat with a blank "What was done with it" section. rev3 says in
# writing that five ACCEPTED rev2 findings were still unedited when rev3 was dispatched. So the money bought the
# same findings repeatedly, and the countable precondition is not "a recipe failed again" (round 1 rightly said a
# filename counter cannot see that) but "a review of kind K was dispatched while the newest archived review of
# kind K had not been disposed". That is readable straight off the archive, and unlike a "cite a census log" rule
# it cannot be satisfied by a token edit: the disposition has to say what was done with each finding.
REVIEW_KINDS = (("priorart", re.compile(r"prior_art_review\.py|-Slug\s+\S*priorart", re.I)),
                ("retrospective", re.compile(r"retrospective\.py|-Slug\s+\S*retrospective", re.I)))
DISPOSITION_H = "## What was done with it"
PLACEHOLDER_RE = re.compile(r"^\s*\(?\s*claude fills in\s*\)?\s*$", re.I | re.M)


def undisposed(kind):
    """The newest archived review of `kind` whose disposition section is missing, empty or still the placeholder."""
    files = sorted(glob.glob(os.path.join(PEER, f"*{kind}*.md")), key=os.path.getmtime)
    if not files:
        return None
    newest = files[-1]
    try:
        with open(newest, encoding="utf-8", errors="replace") as f:
            body = f.read()
    except OSError:
        return None
    if DISPOSITION_H not in body:
        return newest, "has no disposition section at all"
    tail = body.split(DISPOSITION_H, 1)[1]
    stripped = PLACEHOLDER_RE.sub("", tail).strip()
    if len(stripped) < 80:
        return newest, "disposition is empty or still the placeholder"
    return None


# --- ONE REVIEW PER ROW PER CYCLE (a RULE CHANGE; user-approved 2026-09-22 "전부 적용해보자") -----------
# WHAT CHANGES. CLAUDE.md section 5 says a failed prediction owes an adversarial review, full stop, and this
# hook has enforced it per FAILING LOG. A staged build re-runs the SAME row of the SAME stage many times in one
# cycle - v3, v5, v7 of one recipe, each writing its own log - and each re-run bought its own review of what is,
# in the project's own words, one row. So: the FIRST failure of a script buys the review, and every later
# failure of the SAME script inside SIX HOURS cites it instead of buying another.
#
# WHAT IT CANNOT DO, deliberately, so this stays one rung and not a hole:
#   * It only ever cites an exchange that ALREADY passed review_quality() - ANSWERED, from codex, gemini or
#     `-Agent claude -Role hypothesis`. A TIMEOUT exchange releases nothing; a claude audit releases nothing.
#   * SAME SCRIPT, by the name in the log's own last `BGRUN START` line, `_v\d+` stripped, and the review has
#     to be ABOUT that script: its subject script (review_subject_scripts - a `Script:` line, else the first
#     path-qualified script in `## Question`) must equal the log's stem exactly. A mere mention does not count
#     (tightened 2026-09-25, card 79-2). A review of a different row, or of the same row yesterday, does not match.
#   * It spends NO Jev call and asks no model: this rung is mechanical, and it runs BEFORE the ladder so the
#     cheapest branch is also the first one.
#   * Every release is written twice - `RULE-SAME-ROW` in tools/bench/jev_gate.log AND a `SAME-ROW:` citation
#     inside the review's own `## What was done with it` - so the audit can count what ran without a new review.
#     The citation is NOT a release line (`FIXED:` / `REFUTED:` / `PRIOR-ART:`), so it cannot release a
#     prior-art verdict, and it does not move the review's creation time.
SAME_ROW_AGE_S = 6 * 3600
SCRIPT_IN_CMD_RE = re.compile(r"tools[\\/](?:recipes|bench)[\\/]([\w.-]+)\.py", re.I)
VSUFFIX_RE = re.compile(r"_v\d+$", re.I)
QUESTION_SEC_RE = re.compile(r"^##\s+Question\s*$(.*?)(?=^##\s|\Z)", re.M | re.S)
TASK_SLUG_RE = re.compile(r"^\-\s*\*\*(?:task|slug):\*\*.*$", re.M | re.I)   # unused here since 79-2; jev_wave3a_trials.py imports it


def log_script(text):
    """The script name a log's LAST run was started on, `_v\\d+` stripped - or None.

    Reads the `BGRUN START` line only (bgrun writes the whole command there). The LAST match on that line is
    taken, because the line reads `py tools/bgrun.py --log tools/bench/x.log -- py -u tools/recipes/stage.py`
    and the thing that RAN is what follows the `--`; `bgrun.py` itself is not under recipes/ or bench/, so it
    never matches. Accepts text that still carries the `BGRUN START` marker and text already split on it
    (which is what newest_failing_log hands back)."""
    seg = text.rsplit("BGRUN START", 1)[-1] if "BGRUN START" in text else text
    first = (seg.splitlines() or [""])[0]
    names = SCRIPT_IN_CMD_RE.findall(first)
    if not names:
        return None
    return VSUFFIX_RE.sub("", names[-1])


# TIGHTENED 2026-09-25 (card 79-2; retrospective-cycle78 finding 6, jev_gate.log:952): the old matcher accepted
# ANY mention of the stem anywhere in the Question (a bare-word `re.search`), so `drive_m8_replay_s1_78.log` was
# discharged by the endianness review of `tools/bench/m8b_replay_compare.py`, whose Question only said
# "drive_m8.tra_rows' earlier count". The row is now the review's SUBJECT script, read in this order:
#   1. a `Script:` line in `## Question` (the path-qualified scripts on that line);
#   2. else the FIRST path-qualified `tools/(recipes|bench)/X.py` in `## Question` (a dispatch names its subject
#      first). Bare words (`drive_m8.tra_rows`) and scripts named only in the Answer never count.
# Match is EXACT on the stem after `_v\d+` is stripped - `drive_m8` no longer matches `drive_m8_replay`.
# Peer archives carry no machine-readable task-script field (census 2026-09-25: no `task:`/`slug:` header in any
# review; review/1 has no script field; the `verdict-card:` header points at the OUTPUT verdict/1 card, not the
# input review card, and a review card's attachments are rendered INTO the Question) - so this is a convention on
# the question text, stated as such. The `- **task:**`/`- **slug:**` header route is dropped: no archive has one.
SCRIPT_LINE_RE = re.compile(r"^\s*Script\s*:(.*)$", re.M | re.I)


def review_subject_scripts(body):
    """The set of script stems (`_v\\d+` stripped) this review was dispatched ABOUT - empty when it names none."""
    q = QUESTION_SEC_RE.search(body)
    if not q:
        return set()
    qtext = q.group(1)
    for line in SCRIPT_LINE_RE.findall(qtext):
        names = SCRIPT_IN_CMD_RE.findall(line)
        if names:
            return {VSUFFIX_RE.sub("", n).lower() for n in names}
    first = SCRIPT_IN_CMD_RE.search(qtext)
    return {VSUFFIX_RE.sub("", first.group(1)).lower()} if first else set()


def review_names_script(body, stem):
    """True when this archive's SUBJECT script (review_subject_scripts) is exactly `stem`, `_v\\d+` stripped.
    A mere mention - in the Question's prose, a header, or the Answer - is not a review OF that script."""
    return VSUFFIX_RE.sub("", stem).lower() in review_subject_scripts(body)


def same_row_review(log_path, text, now=None):
    """(review path, script stem, age in minutes) for the NEWEST accepted review of this failing log's own
    script within SAME_ROW_AGE_S - or None. No model call, no network."""
    stem = log_script(text)
    if not stem:
        return None
    now = time.time() if now is None else now
    best = None
    for p in glob.glob(os.path.join(PEER, "*.md")):
        try:
            st = os.stat(p)
            born = min(st.st_ctime, st.st_mtime) if os.name == "nt" else st.st_mtime
            if now - born > SAME_ROW_AGE_S:
                continue
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                body = f.read()
        except OSError:
            continue
        if not review_names_script(body, stem):
            continue
        ok, _why = review_quality(body)
        if not ok:
            continue
        if best is None or born > best[1]:
            best = (p, born)
    if best is None:
        return None
    return best[0], stem, max(0.0, (now - best[1]) / 60.0)


def _gate_log(line):
    """One line to tools/bench/jev_gate.log, resolved at CALL time so a redirected BENCH isolates it."""
    try:
        with open(os.path.join(BENCH, "jev_gate.log"), "a", encoding="utf-8") as fh:
            fh.write(line.rstrip("\n") + "\n")
    except OSError:
        pass


# --- GATE-ROW VERDICTS AS ADVISORY CONTEXT (docs/jev-integration-plan.md 2nd wave #2; user 2026-09-23) --------
# On the path that is about to BLOCK, every FAIL row of the failing run gets one 3-way reading - `defect` /
# `prediction-error` / `reading-artefact` - printed beside the ladder's line and appended to jev_gate.log. So the
# reviewer being dispatched, and the judgement session reading this refusal, see whether a 12-FAIL run is twelve
# defects or one blind reader WITHOUT anyone having to ask for it.
#
# IT IS NEVER A DISCHARGE BASIS. It does not touch `allow`, it is printed only when the block already stands, and
# the measurement says why it may not be more: 68 rows, strict 36.8 %, 78.1 % on the p>=0.70 judgements alone,
# and a clear bias - `ExecState` 0 rows read as `prediction-error`. A signal for a human, not a release.
#
# ONCE PER LOG FILE. tools/bench/jev_gaterow_state.json remembers (path, mtime, size), so a session that retries a
# build ten times against the same failing log pays for the rows once. The state write is atomic because a cycle
# cell may read it at any moment; a corrupt or missing file means "not yet asked", i.e. it fails toward spending
# one reading, never toward wedging the hook.
GATEROW_STATE = os.path.join(BENCH, "jev_gaterow_state.json")


def _gaterow_seen(path, mark=True):
    """True when this exact log revision has already been read. Never raises."""
    try:
        st = os.stat(path)
        key = "%s|%d|%d" % (os.path.basename(path), int(st.st_mtime), st.st_size)
    except OSError:
        return True                       # unreadable: there is nothing to ask about
    state = {}
    try:
        with open(GATEROW_STATE, encoding="utf-8") as fh:
            state = json.load(fh)
        if not isinstance(state, dict):
            state = {}
    except (OSError, ValueError):
        state = {}
    if key in (state.get("seen") or {}):
        return True
    if mark:
        seen = state.get("seen") or {}
        seen[key] = time.strftime("%Y-%m-%d %H:%M:%S")
        if len(seen) > 64:                # keep the file small; drop the oldest by recorded time
            for k in sorted(seen, key=lambda k: seen[k])[:len(seen) - 64]:
                seen.pop(k, None)
        try:
            tmp = GATEROW_STATE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump({"seen": seen}, fh, ensure_ascii=False, indent=1)
            os.replace(tmp, GATEROW_STATE)
        except OSError:
            pass
    return False


def gaterow_advisory(path):
    """Print and log the per-row verdicts of the failing run. Returns the lines; the caller ignores them."""
    lines = []
    if os.environ.get("JEV_ADVISORY_OFF") == "1":
        return lines
    try:
        if _gaterow_seen(path):
            return lines
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
        import jev_gaterow
        block = jev_gaterow.verdicts_for(path)      # the cheap hook-side variant: <=5 rows x 2 samples, 25 s
        if not block:
            return lines
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        for row in block.splitlines():
            if not row.strip():
                continue
            line = "JEV-GATEROW | %s | %s" % (os.path.basename(path), row)
            lines.append(line)
            _gate_log("%s | %s | gaterow-guard_peer" % (ts, line))
        if lines:
            sys.stderr.write(
                "\n".join(lines) + "\n  (advisory context for the review below - per FAIL row: defect / "
                "prediction-error / reading-artefact. NEVER a discharge basis; measured 78.1 % on the p>=0.70\n"
                "   judgements only, and it under-reads `defect`. docs/jev-integration-plan.md 2nd wave #2)\n\n")
    except Exception:                      # noqa: BLE001 - an advisory reading may never wedge a gate
        return lines
    return lines


def cite_same_row(review_path, log_name, ts):
    """Write `SAME-ROW: <log> (<ts>)` into the review's disposition section, ONCE per log."""
    line = "SAME-ROW: %s (%s)" % (log_name, ts)
    try:
        with open(review_path, "r", encoding="utf-8", errors="replace") as f:
            body = f.read()
        if ("SAME-ROW: " + log_name) in body:
            return True                       # already charged to this review; one citation per log
        with open(review_path, "a", encoding="utf-8") as f:
            if DISPOSITION_H not in body:
                f.write("\n\n" + DISPOSITION_H + "\n")
            f.write("\n" + line + "\n  This later failure of the SAME script was released without buying a new "
                    "peer review: one review per row per cycle (CLAUDE.md, user 2026-09-22). The review above "
                    "is the evidence; this line records which re-run was charged to it.\n")
        return True
    except OSError:
        return False


def _bounded(fn, seconds):
    """(finished, value) - run fn() in a daemon thread for at most `seconds`. An exception counts as finished
    with value None (every Jev rung already degrades to the old path on error). Never raises."""
    box = {}

    def run():
        try:
            box["v"] = fn()
        except Exception:                 # noqa: BLE001
            box["v"] = None
    t = threading.Thread(target=run, daemon=True)
    t.start()
    t.join(max(0.0, seconds))
    return (not t.is_alive()), box.get("v")


def _jev_decide(path, text):
    """The two Jev rungs exactly as main() ran them before the budget: ladder first, the ordinary discharge only
    when the ladder did not act. Returns (ladder_allow, ladder_line, allow, jev_line)."""
    sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
    import jev_gate
    try:
        ladder_allow, ladder_line = jev_gate.jev_ladder(path, text)
    except Exception:                    # noqa: BLE001 - a gate must degrade to its old behaviour, never wedge
        ladder_allow, ladder_line = None, None
    if ladder_allow is True:
        return True, ladder_line, True, None
    if ladder_allow is False:
        return False, ladder_line, False, ladder_line   # the discharge already ran inside the ladder
    try:
        allow, jev_line = jev_gate.jev_discharge(path, text)
    except Exception:                    # noqa: BLE001
        allow, jev_line = False, None
    return None, ladder_line, allow, jev_line


WARM_STATE = os.path.join(BENCH, "jev_warm_state.json")


def _spawn_warmer(path):
    """Start ONE detached `guard_peer.py --warm <log>` per (log, size, mtime) per WARM_TTL_S. Returns a short
    status word for the refusal message. Never raises."""
    try:
        st = os.stat(path)
        key = "%s|%d|%d" % (os.path.basename(path), int(st.st_mtime), st.st_size)
        try:
            with open(WARM_STATE, encoding="utf-8") as fh:
                state = json.load(fh)
            if not isinstance(state, dict):
                state = {}
        except (OSError, ValueError):
            state = {}
        if time.time() - float(state.get(key, 0)) < WARM_TTL_S:
            return "already warming"
        import subprocess
        base = 0x00000008 | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)     # DETACHED_PROCESS
        argv = [sys.executable, os.path.abspath(__file__), "--warm", path]
        for flags in (base | 0x01000000, base):                                     # + BREAKAWAY_FROM_JOB, then without
            try:
                subprocess.Popen(argv, cwd=ROOT, creationflags=flags, stdin=subprocess.DEVNULL,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
                break
            except OSError:
                continue
        else:
            return "warmer could not start"
        state[key] = time.time()
        if len(state) > 64:
            for k in sorted(state, key=lambda k: state[k])[:len(state) - 64]:
                state.pop(k, None)
        tmp = WARM_STATE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(state, fh)
        os.replace(tmp, WARM_STATE)
        return "warmer started"
    except Exception:                    # noqa: BLE001
        return "warmer not started"


def warm(path):
    """`--warm <log>`: finish the Jev rungs for this log outside the hook, so their caches answer the retry."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read().lstrip("﻿")
    except OSError:
        return 0
    last = text.rsplit("BGRUN START", 1)[-1] if "BGRUN START" in text else text
    try:
        _jev_decide(path, last)
    except Exception:                    # noqa: BLE001
        pass
    return 0


def main():
    t_main = time.time()
    if os.environ.get("PEER_GUARD_OFF") == "1":
        return 0
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    cmd = (payload.get("tool_input") or {}).get("command") or ""
    if not cmd:
        return 0

    for kind, pat in REVIEW_KINDS:
        if pat.search(cmd):
            hit = undisposed(kind)
            if hit:
                path, why = hit
                sys.stderr.write(
                    f"BLOCKED by tools/hooks/guard_peer.py: the previous {kind} review is UNDISPOSED.\n"
                    f"  review : {_rel(path)}\n"
                    f"  reason : {why}\n\n"
                    "Cycle 10 bought six reviews of a moving plan for $28.55 and never disposed them, so later\n"
                    "reviews kept returning findings that earlier ones had already returned and that nobody had\n"
                    "acted on. Write that review's 'What was done with it' section first - per finding: accepted\n"
                    "and where the edit landed, or refuted and against which file and line - then dispatch.\n"
                    "Reading, diagnostics and every OTHER kind of peer dispatch stay open.\n")
                return 2
            break

    if not RUNS_RE.search(cmd) or RUNNER_RE.search(cmd):
        return 0
    # Peer-attacked 2026-09-14 (archive/peer/2026-09-14-stall-alert-wrappers-false-positive.md s3): the read-word
    # exemptions used to apply to the WHOLE command, so a build whose arguments contained `dir`/`type`/`head` was
    # exempt. A command that runs a build is exempt only if it is the remedy itself.
    if REMEDY_RE.search(cmd):
        return 0

    failing = newest_failing_log()
    if not failing:
        return 0
    path, mtime, text = failing
    names = failure_names(path, text)
    hit, rejected = newest_bound_peer(mtime, names)
    if hit:
        return 0          # a peer exchange NAMING this failure was archived after it - the loop is closed

    # --- RULE-OFFLINE-CARD (card chat-P1 item 1(d), user 2026-09-28) ------------------------------------------
    # newest_failing_log() is GLOBAL: in the pipeline, the LabVIEW card's failing log would block the offline prep card
    # running beside it. A caller BOUND to a task/1 card with flags.labview == "none" whose command launches nothing
    # that reaches LabVIEW (offline_command) cannot act on the failed prediction, so it is not the build this gate
    # holds back. Every other caller - the LabVIEW card, the judgement session, an unbound agent - is gated as before.
    oc = offline_card(payload, cmd)
    if oc:
        line = "RULE-OFFLINE-CARD | %s | %s not gated for card %s (flags.labview none; command offline)" % (
            time.strftime("%Y-%m-%d %H:%M:%S"), _rel(path), oc)
        sys.stderr.write(line + "\n")
        _gate_log(line)
        return 0
    # --- RULE-OFFLINE-CMD (gate-fp fp-10, card 125-1): the reverse - an offline command under a LabVIEW card is not held
    # back by a failing log that card did not launch (launch ledger). Its own failing log still gates it.
    ol = offline_cmd_lv_card(payload, cmd, path)
    if ol:
        line = "RULE-OFFLINE-CMD | %s | %s not gated for card %s (flags.labview %s; command offline; log not launched " \
               "by this card)" % (time.strftime("%Y-%m-%d %H:%M:%S"), _rel(path), ol[0], ol[1])
        sys.stderr.write(line + "\n")
        _gate_log(line)
        return 0

    # --- ONE REVIEW PER ROW PER CYCLE (the rule above; BEFORE the ladder, because it costs nothing) ---------
    sr = same_row_review(path, text)
    if sr:
        rp, stem, age_min = sr
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        line = "RULE-SAME-ROW | %s | %s discharged by %s (same script %s, age %d min)" % (
            ts, _rel(path), os.path.basename(rp), stem, int(round(age_min)))
        sys.stderr.write(line + "\n  (one review per row per cycle - user 2026-09-22; no new review is owed "
                         "for a later failure of the same script inside 6 h.)\n")
        _gate_log(line)
        cite_same_row(rp, os.path.basename(path), ts)
        return 0

    # --- RULE-GATE-FP (card chat-P1 item 3, user 2026-09-28) --------------------------------------------------
    # A failing log named by an OPEN tools/bench/gate_fp_queue.jsonl entry whose gate is a CHECKER (guard_* or
    # checker:<stage_prerun|stagekit|...>) and whose first failure line is not a LabVIEW observation is a false positive
    # of our own gate, queued with file:line evidence for a batch drain - not a failed prediction about the machine.
    # At most ONE such entry per gate per cycle (tools/gate_fp.py discharge_for_log). A LabVIEW observation never.
    try:
        import gate_fp
        fp_e, _fp_why = gate_fp.discharge_for_log(path, log_failure_file(path)[1])
    except Exception:                    # noqa: BLE001 - the queue is optional; a broken reader never releases
        fp_e = None
    if fp_e:
        line = "RULE-GATE-FP | %s | %s discharged by %s (gate %s, queued %s: %s)" % (
            time.strftime("%Y-%m-%d %H:%M:%S"), _rel(path), fp_e.get("id"), fp_e.get("gate"), fp_e.get("iso"),
            str(fp_e.get("why"))[:120])
        sys.stderr.write(line + "\n  (a checker's false positive, queued for a batch drain - not a failed prediction; "
                         "one per gate per cycle.)\n")
        _gate_log(line)
        return 0

    # --- JEV DISCHARGE (docs/jev-integration-plan.md row #1; user 2026-09-22) ------------------------------
    # THE MECHANISATION OF AN EXISTING RULE, NOT A NEW EXEMPTION. CLAUDE.md section 5 already says: "check
    # archive/peer/ for the same question before re-asking - re-asking wastes quota the session may need later."
    # Nothing enforced it, and the gate's binding test is deliberately crude (creation time + a NAME appearing in
    # the body), so a review that demonstrably attacks the very prediction a later run reports still leaves the
    # gate armed when it was archived three minutes too early, or when the next run writes the same failure under
    # a new log name. That is not a missing review; it is a missing citation.
    #
    # So, only on the path that was about to BLOCK, the newest accepted reviews are scored against this failure.
    # At p >= jev_gate.DISCHARGE_P the build is allowed AND the charge is written into that review's own
    # "## What was done with it" section, so the audit sees which failure was released against which review. In
    # the unknown band the gate blocks exactly as before and only says so. No key, an API error, an old-format
    # response or ANY exception => the old behaviour, unchanged.
    #
    # WHAT THIS CANNOT DO: it cannot invent a review. It only ever cites an exchange that already passed
    # review_quality() above - ANSWERED, from codex, gemini or claude/hypothesis - so the adversary requirement
    # and D3 are untouched. It writes no release line (`FIXED:` / `REFUTED:` / `PRIOR-ART:`) and does not move a
    # review's creation time, so it cannot release a prior-art verdict or retro-bind an old review by a side
    # effect. Measured before wiring: tools/bench/jev_discharge_trial.py over 40 labelled pairs.
    #
    # --- THE REVIEW LADDER (2차 #1, USER-APPROVED 2026-09-22 17:3x), one rung ABOVE the discharge -------------
    # The discharge below asks one question: "is this failure already reviewed?". The ladder asks first which
    # KIND of failure this is, because two of the three kinds that reach this gate never needed an adversary:
    #   our-script-bug         -> ALLOW. Our own Python died, or every failing row is the gate's own arithmetic
    #                             being wrong (gate D7's "#637 terminals 48 -> 47", gate K2's "Wire 1905"). There
    #                             is no claim about the machine for a peer to attack. Recorded in
    #                             tools/bench/jev_ladder_allowed.jsonl so the audit can count these releases.
    #   already-reviewed-class -> the ORDINARY discharge decides, unchanged. The ladder cannot invent a review:
    #                             a citation still has to pass review_quality(), so a TIMEOUT exchange does not
    #                             release anything. When the discharge says no, the block below stands and the
    #                             discharge is NOT consulted twice.
    #   new-problem            -> nothing happens here; the old path runs exactly as it did.
    # It acts only at p >= 0.80 on the consensus mean of five asks. No key, an error or the unknown band means
    # the old path, byte for byte. Measured before wiring on today's own 16 reviews and their triggering logs
    # (tools/bench/jev_ladder_set.json, tools/bench/jev_wave2a.log).
    # BUDGETED (repair 2026-09-24, see HOOK_BUDGET_S): both Jev rungs run in one bounded call. Out of budget ->
    # FAIL CLOSED: the block below stands, one detached warmer finishes the rungs so the retry is answered from cache.
    finished, got = _bounded(lambda: _jev_decide(path, text), HOOK_BUDGET_S - (time.time() - t_main))
    if not finished:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        warm_status = _spawn_warmer(path)
        line = ("JEV-BUDGET | %s | %s | ladder/discharge still running after %.1fs of the hook's %.0fs budget: "
                "BLOCK stands (fail closed); %s - retry in a minute and the cached verdict answers at once" % (
                    ts, os.path.basename(path), time.time() - t_main, HOOK_BUDGET_S, warm_status))
        _gate_log(line)
        sys.stderr.write(line + "\n")
        got = None
    ladder_allow, ladder_line, allow, jev_line = got if got else (None, None, False, None)
    # NEXT-ACTION (user 2026-09-24 03:5x): the verdict DRIVES the next step, it does not only lift the gate. Every
    # ladder line ends `| NEXT-ACTION: ...`; the same text is written to stderr on allow AND on refuse, and the
    # newest JEV-LADDER line for the log in tools/bench/jev_gate.log is the one sessions read first. Exit codes
    # are unchanged.
    if ladder_allow is True:
        if ladder_line:
            sys.stderr.write(ladder_line + "\n")
        return 0
    if allow:
        try:
            import jev_gate
            sys.stderr.write(jev_gate.ladder_after_discharge(path, jev_line) + "\n")
        except Exception:                # noqa: BLE001 - reporting only; the allow stands
            pass
        return 0
    if ladder_line and ladder_line != jev_line:
        sys.stderr.write(ladder_line + "\n")
    if jev_line:
        sys.stderr.write(jev_line + "\n"
                         "  (advisory only: below the discharge threshold, so the block below stands.)\n\n")

    # The block stands. Give the reviewer and the judgement session the per-row verdicts, unasked (2nd wave #2).
    # Advisory only, so it gets whatever budget is left and is simply skipped when none is (repair 2026-09-24).
    left = HOOK_BUDGET_S - (time.time() - t_main)
    if left > 1.0:
        _bounded(lambda: gaterow_advisory(path), left)

    first = log_failure_file(path)[1]
    if rejected:
        sys.stderr.write("NOT ACCEPTED as the review of this failure:\n  " + "\n  ".join(rejected) + "\n\n")
    sys.stderr.write(
        "BLOCKED by tools/hooks/guard_peer.py (CLAUDE.md: a FAILED PREDICTION triggers mandatory peer review).\n"
        f"  latest failing log : {_rel(path)}\n"
        f"  first failure line : {first[:200]}\n"
        "\n"
        "Before the next build, dispatch a peer to ATTACK the explanation you formed for this failure:\n"
        "  py tools/bgrun.py --max-min 14 --log tools/bench/peer_<slug>.log -- \\\n"
        "     powershell -NoProfile -File tools/peer.ps1 -Agent claude -Role hypothesis -TimeoutSec 780 \\\n"
        "     -Slug <slug> -TaskFile <file with: ATTACK this claim ...>\n"
        "\n"
        "The block lifts once archive/peer/ holds an exchange that (a) is newer than that log, (b) NAMES the failure\n"
        f"    - any of: {', '.join(sorted(names))}  (put the log or script name in the -Task),\n"
        "    (c) ended with outcome ANSWERED, and (d) came from an ADVERSARY: codex, gemini, or\n"
        "    `-Agent claude -Role hypothesis` (opus / effort max / web) - the last one added 2026-09-18 while\n"
        "    codex's weekly quota is at 9 % (user's decision, a trial).\n"
        "A `-Agent claude` exchange in ANY OTHER role is this project's rule/consistency audit - dispatch it too if\n"
        "it helps, but it cannot discharge a failed prediction on its own (user's decision, 2026-09-15).\n"
        "Reading logs, writing docs and dispatching the peer are never blocked. Set PEER_GUARD_OFF=1 only inside\n"
        "benchmark cells.\n"
        "NEXT-ACTION: hypothesis review owed (old path)\n")
    return 2


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--warm":
        sys.exit(warm(sys.argv[2]))
    _rc = main()
    # os._exit, not sys.exit: a Jev thread cut off by the budget may still be inside a network call, and the
    # verdict must reach Claude Code now, not after interpreter shutdown has waited on anything.
    try:
        sys.stderr.flush()
        sys.stdout.flush()
    except Exception:                    # noqa: BLE001
        pass
    os._exit(_rc)
