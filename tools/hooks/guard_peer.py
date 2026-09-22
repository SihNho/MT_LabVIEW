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

JEV REVIEW LADDER (2026-09-22, docs/jev-integration-plan.md 2차 #1, USER-APPROVED 17:3x). One rung above the
discharge, and the only Jev insertion that CHANGES a rule rather than mechanising one: before asking "is this
already reviewed?", the gate asks which of three kinds the failure is. `our-script-bug` (our own Python died, or
every failing gate row is the gate's own expectation being wrong) releases the build and is recorded in
tools/bench/jev_ladder_allowed.jsonl; `already-reviewed-class` hands the decision to the ordinary discharge, which
can still only cite an exchange that passed review_quality(); `new-problem` changes nothing. It acts only at
p >= 0.80 on the consensus mean of five asks. See main().

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
import time

HERE = os.path.dirname(os.path.abspath(__file__))
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


def newest_failing_log():
    best = None
    for p in glob.glob(os.path.join(BENCH, "*.log")):
        # A peer-review transcript is not a build log. 2026-09-15 12:5x: `peer_wrong_owner_node.log` blocked the very
        # build its review had just approved, because the reviewer's own sentence "Fail the build on inequality..."
        # matched the failure pattern. Review logs are evidence, never the thing under test.
        # EXTENDED 2026-09-15 evening: the rule was written for `peer_*` only, so the retrospective, outcome-review
        # and prior-art dispatchers - which quote historical failures verbatim in their answers - were still being
        # read as builds. `priorart_test_run1.log` blocked the next run because the reviewer had CITED
        # `build_opgeterrors.log`'s "STOP: not saved / rc=5". Third time this session that a fix landed in one guard
        # and not its sibling; the pattern now lives in one place per hook.
        if logclass.is_review_log(p) or SELFTEST_LOG_RE.match(os.path.basename(p)):
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
        if FAILURE_RE.search(last):
            best = (p, st.st_mtime, last)
    return best


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


def main():
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
    allow, jev_line = False, None
    ladder_allow, ladder_line = None, None
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
        import jev_gate
        ladder_allow, ladder_line = jev_gate.jev_ladder(path, text)
    except Exception:                    # noqa: BLE001 - a gate must degrade to its old behaviour, never wedge
        ladder_allow, ladder_line = None, None
    if ladder_allow is True:
        return 0
    if ladder_allow is False:
        allow, jev_line = False, ladder_line          # the discharge already ran inside the ladder
    else:
        try:
            import jev_gate
            allow, jev_line = jev_gate.jev_discharge(path, text)
        except Exception:                # noqa: BLE001
            allow, jev_line = False, None
    if allow:
        return 0
    if jev_line:
        sys.stderr.write(jev_line + "\n"
                         "  (advisory only: below the discharge threshold, so the block below stands.)\n\n")

    first = next((ln.strip() for ln in text.splitlines() if FAILURE_RE.search(ln)), "(see the log)")
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
        "benchmark cells.\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
