"""PreToolUse hook (Bash | PowerShell): a cycle cannot START until the previous one was reviewed as a cycle.

WHY THIS IS A HOOK. `guard_peer.py` makes every FAILED PREDICTION reviewable; nothing makes the CYCLE reviewable.
The user named the gap on 2026-09-15: "피어 리뷰를 통해 판단 및 실행 구조에 대한 비평은 할 수 없는 것 같아". A
retrospective that runs "when Claude remembers" is a retrospective that runs when it is convenient - the same
dynamic that made the GUI rule and the failed-prediction rule need refusals rather than reminders.

WHAT IT DOES. Before a command that starts a BUILD (a recipe under tools/recipes), it checks two things:

  1. If the previous cycle produced build logs and no retrospective exists that is NEWER than the newest of them,
     the build is blocked until `py tools/retrospective.py --cycle N` has run and been archived.
  2. If `tools/violations.py --due` reports a slug at or over its threshold, the build is blocked until a
     mechanical device for that slug exists - the device, not another promise.

Diagnostics stay open: bench scripts, log reading, doc writing, peer dispatch and the retrospective itself all pass,
because the remedy must never be blocked by the gate that demands it.

CYCLE_GUARD_OFF=1 disables it (benchmark cells only; the main session never sets it).
Exit code 2 = block (stderr goes back to Claude); 0 = allow.
"""
import glob
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BENCH = os.path.join(ROOT, "tools", "bench")
PEER = os.path.join(ROOT, "archive", "peer")
# Only a RECIPE run starts a cycle's construction. Bench/diagnostic scripts are how a cycle is understood.
# The path must be in COMMAND POSITION - directly after a python invocation. Until 2026-09-15 this matched the
# path anywhere in the command line, so a read-only one-liner that merely CONTAINED the string 'tools/recipes/*.py'
# (inside a glob, measuring how big an index would be) was blocked as if it were a build. This gate's own
# docstring promises that diagnostics are never blocked; guard_peer.py's RUNS_RE already had the stricter form.
# The capture group was added 2026-09-16 for the `premature-build` device below, which needs the RECIPE FILE
# itself (to compare its mtime against the newest prior-art review). `.search()` truthiness is unaffected.
BUILD_RE = re.compile(r"\bpy(?:thon)?[\w.]*\s+(?:-\S+\s+)*([^\s|;&]*tools[\\/]recipes[\\/][^\s|;&]*\.py)", re.I)
EXEMPT_RE = re.compile(r"retrospective\.py|violations\.py|audit_cycle\.py|outcome_review\.py|prior_art_review\.py|"
                       r"peer\.ps1|guard_|--help|"
                       r"\b(cat|head|tail|sed|grep|less|type|wc|ls|dir)\b", re.I)
MAX_AGE_S = 30 * 3600          # a cycle older than this is history; it does not gate today's work
# How much work counts as "a cycle" before its retrospective is overdue. Deliberately generous: the point is to
# stop a cycle from ending unreviewed, not to interrupt one in progress. Cycles 1-7 ran roughly 5-20 logs each.
# RAISED 10 -> 30 builds and 8 -> 24 h by card chat-P1 item 2b (user 2026-09-28 "1~4번은 적용하도록"): the retrospective
# now runs every THIRD cycle or when tools/retro_due.py says it is due, so this budget is only the BACKSTOP for a
# retrospective that never came (cycle_runner._retro_debt reads these same two constants).
CYCLE_BUILD_BUDGET = 30
CYCLE_HOURS = 24.0


# A REVIEW'S OWN RUNNER LOG IS NOT A BUILD LOG (2026-09-15). `retrospective.py` runs under bgrun, so its log gets
# its final line AFTER peer.ps1 has already archived the review - the log is therefore always NEWER than the
# retrospective it produced, and the gate re-armed on the very review that was meant to open it. That is a deadlock,
# not a strict check: no retrospective run this way could ever satisfy it. guard_peer.py learned the same lesson
# about `peer_*.log` on 2026-09-15 12:5x ("review logs are evidence, never the thing under test"); the exclusion was
# never mirrored here. Same for the outcome review and the compliance audit.
# SINGLE DEFINITION (2026-09-16 lint): this list lived in three files and had drifted two terms apart, so a fix in
# one never reached the others - four false positives were paid for that way. It now lives in tools/logclass.py.
# This gate asks "has a CYCLE been built?", so it wants `is_build_log`: watchdog records are excluded here (they are
# observations, not runs) while guard_peer deliberately keeps seeing them as failures.
sys.path.insert(0, os.path.join(ROOT, "tools"))
import logclass  # noqa: E402
import stop_record  # noqa: E402  - the LAUNCH gate (cycle 18); it imports THIS module lazily, so no cycle


# The verdict vocabulary prior_art_review.py defines. An allowlist keeps a stray line from inventing a slug that
# blocks forever, and keeps the question's own menu line out of the tally.
PRIOR_ART_SLUGS = {"settled-already", "refuted-already", "contradicted", "unread-evidence",
                   "already-built", "already-failed", "helper-exists", "already-measured", "novel"}
PRIOR_ART_RE = re.compile(r"^PRIOR-ART:[ \t]*([a-z-]+)", re.M)

# THE SECOND RELEASE FORM: `FIXED:` (2026-09-16). The gate's own refusal says "if the review is right, change the
# plan instead" - and then accepted only `REFUTED:`, i.e. only the branch where the review is WRONG. A cycle-11
# review round whose four findings were all correct and all acted on had no honest line to write, and the build it
# had improved could not run. STATUS.md had recorded the hole as "the obvious repair" since that morning.
# Strictness is deliberately NOT lowered: `REFUTED:` needs a citation a human can open, so `FIXED:` needs a file
# the MACHINE can check - the cited path must exist, must have changed after the review, and the claim must sit in
# the section every review owes anyway ("What was done with it"). An assertion still releases nothing.
#     FIXED: <slug> - <path>:<line> - <one sentence saying what changed>
# The separator may be '-', an en dash or an em dash; the path may be backticked.
FIXED_RE = re.compile(r"^FIXED:[ \t]*([a-z-]+)[ \t]*[-–—][ \t]*`?([^\s`:]+(?::[^\s`:]+)*?)`?:(\d+)"
                      r"[ \t]*[-–—][ \t]*(\S.*)$", re.M)
DISPOSITION_MARK = "## What was done with it"


def review_time(path, body):
    """(instant, basis) - the moment the review's findings existed, which a fix must post-date.

    NOT `stamp()` here, and that is MEASURED, not assumed (2026-09-16): the Edit tool rewrites a file rather than
    writing in place, and on this filesystem the rewrite MOVES CREATION TIME - a scratch file created at
    ...071.522 and edited once reported ctime ...077.909. So for an archived review, `min(ctime, mtime)` is the
    time of its ANNOTATION, not of its first write. Using it would have refused the very first real `FIXED:` line:
    rev3's archive stamps 18:42:09 (when its disposition table was added) while the recipe fix it records as
    accepted stamps 18:40:40. `stamp()` stays correct for its own job - `frontmatter.py` writes in place, so a
    bulk frontmatter pass still cannot inflate it - but it cannot serve as "when was this review written".
    So: the frontmatter date is used when the file has one. These archives carry `- **date:** YYYY-MM-DD` with NO
    time (peer.ps1 writes the date only), so the practical basis is MIDNIGHT OF THE REVIEW'S DATE; a fix made
    earlier the same day therefore counts, and a fix predating the review's day does not. If peer.ps1 ever writes
    a time too, the finer comparison is used automatically. Files with no date at all fall back to `stamp()`.
    """
    m = re.search(r"^\-\s*\*\*date:\*\*\s*(\d{4})-(\d{2})-(\d{2})(?:[ T](\d{2}):(\d{2})(?::(\d{2}))?)?", body, re.M)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if m.group(4):
            t = time.mktime((y, mo, d, int(m.group(4)), int(m.group(5)), int(m.group(6) or 0), 0, 0, -1))
            return t, "frontmatter date+time %s-%s-%s %s:%s" % (m.group(1), m.group(2), m.group(3),
                                                                m.group(4), m.group(5))
        t = time.mktime((y, mo, d, 0, 0, 0, 0, 0, -1))
        return t, "frontmatter date %s (no time in the file -> midnight)" % m.group(0).split()[-1]
    return stamp(path), "file stamp (min ctime/mtime) - the review carries no frontmatter date"


def fixed_citations(path, body):
    """(slugs, cited_paths, rejected) for the VALID `FIXED:` lines of one review.

    `cited_paths` is the set of normcase'd absolute paths a valid line cites. It is what the
    `premature_build` (b)-exemption of 2026-09-17 (d1-build-plan.md §11g.3) reads: a FIXED line already proves,
    mechanically, that the cited file EXISTS and was CHANGED AFTER the review - which is exactly the question
    "was this recipe edited as the disposition of its own review?". Nothing new is validated here; the same
    line is simply read for its path as well as for its slug.
    """
    ok, paths, bad = set(), set(), []
    if DISPOSITION_MARK not in body:
        if re.search(r"^FIXED:", body, re.M):
            bad.append(("(any)", "the FIXED line(s) are not in a '%s' section - that section is missing"
                        % DISPOSITION_MARK))
        return ok, paths, bad
    head, section = body.split(DISPOSITION_MARK, 1)
    for m in re.finditer(r"^FIXED:.*$", head, re.M):        # outside the disposition section: never releases
        bad.append(("(any)", "a FIXED line sits ABOVE '%s'; only that section releases: %s"
                    % (DISPOSITION_MARK, m.group(0)[:90])))
    rt, basis = review_time(path, body)
    for m in FIXED_RE.finditer(section):
        slug, rel = m.group(1), m.group(2)
        if slug not in PRIOR_ART_SLUGS:
            bad.append((slug, "not a prior-art verdict slug"))
            continue
        fp = os.path.normpath(os.path.join(ROOT, rel.replace("/", os.sep)))
        if not os.path.isfile(fp):
            bad.append((slug, "cited path does not exist under the project: %s" % rel))
            continue
        try:
            fm = os.path.getmtime(fp)
        except OSError:
            bad.append((slug, "cited path is unreadable: %s" % rel))
            continue
        if fm <= rt:
            bad.append((slug, "%s last changed %s, which is NOT after the review (%s) - a fix must post-date the "
                              "finding it answers" % (rel, time.strftime("%Y-%m-%d %H:%M", time.localtime(fm)),
                                                      basis)))
            continue
        ok.add(slug)
        paths.add(os.path.normcase(os.path.abspath(fp)))
    return ok, paths, bad


def fixed_claim(path, body, target):
    """(claimed, released, why) for ONE file cited by ONE review - CLAUDE.md:449's conditions, per citation.

    Added 2026-09-18 (cycle 20, step 1) because `premature_build` could only ever ASK whether a release was
    valid, never whether one had been ATTEMPTED AND FAILED. CLAUDE.md:449 says a `FIXED:` release needs (a) the
    cited path to exist, (b) it to have changed AFTER the review, (c) the line to sit under the disposition
    heading. `fixed_citations` implements all three - but `premature_build` consulted it only inside the
    `if not newer:` branch, i.e. only when the recipe was ALREADY newer than the review, where (b) is true by
    construction and can never reject. So condition (b) has never refused anything. A statement of the form
    "this edit is that review's disposition" that FAILS the filesystem check must not be worth more than no
    statement at all - it must refuse.

      claimed  - a `FIXED:` line ANYWHERE in the review cites exactly this file (above the heading counts: an
                 attempted release is a claim, and (c) is then the reason it fails);
      released - that citation passes (a), (b) and (c), i.e. `fixed_citations` accepted it;
      why      - which condition it failed, in the refusal's own words (empty when released or unclaimed).
    """
    tn = os.path.normcase(os.path.abspath(target))
    _ok, cited, _bad = fixed_citations(path, body)
    if tn in cited:
        return True, True, ""
    rt, basis = review_time(path, body)
    sec_at = body.find(DISPOSITION_MARK)
    for m in FIXED_RE.finditer(body):
        slug, rel = m.group(1), m.group(2)
        fp = os.path.normpath(os.path.join(ROOT, rel.replace("/", os.sep)))
        if os.path.normcase(os.path.abspath(fp)) != tn:
            continue
        if sec_at < 0 or m.start() < sec_at:
            return True, False, ("(c) the FIXED line sits ABOVE '%s'; only that section releases" % DISPOSITION_MARK)
        if slug not in PRIOR_ART_SLUGS:
            return True, False, "`%s` is not a prior-art verdict slug" % slug
        if not os.path.isfile(fp):
            return True, False, "(a) the cited path does not exist under the project: %s" % rel
        try:
            fm = os.path.getmtime(fp)
        except OSError:
            return True, False, "(a) the cited path is unreadable: %s" % rel
        if fm <= rt:
            return True, False, ("(b) %s last changed %s, which is NOT after the review (%s) - a fix must "
                                 "post-date the finding it answers"
                                 % (rel, time.strftime("%Y-%m-%d %H:%M", time.localtime(fm)), basis))
        return True, False, "the citation did not validate"
    return False, False, ""


def fixed_slugs(path, body):
    """Slugs released by a VALID `FIXED:` line, and the rejected lines with the reason each was rejected."""
    ok, _paths, bad = fixed_citations(path, body)
    return ok, bad


# THE `REFUTED:` HALF, LIFTED OUT OF main() (2026-09-18, cycle 18). It lived as an inline `re.findall` inside the
# verdict gate below, which was fine while this file was the only reader of a release line. `tools/stop_record.py`
# is now a second reader (the LAUNCH gate: guard_cycle stops the BUILD, stop_record stops the RUN), and the
# project's own lesson about copied predicates - tools/logclass.py's docstring, four false positives paid for a
# regex that lived in three files - says the second caller is the moment to make it one function. stop_record.py
# IMPORTS this; it does not restate the conditions.
REFUTED_RE = re.compile(r"^REFUTED:\s*([a-z-]+)", re.M)


def released_slugs(path, body):
    """(released, rejected) - the ONE definition of "which slugs does this review file release?".

    Released = a bare `REFUTED: <slug>` line (the citation is prose a human checks) or a `FIXED:` line that passes
    every machine-checked condition in `fixed_citations`. `rejected` carries the FIXED lines that failed, with the
    reason, so a refusal can say WHY the release did not count."""
    fixed, bad = fixed_slugs(path, body)
    return set(REFUTED_RE.findall(body)) | fixed, bad


FM_DATE_RE = re.compile(r"^\-\s*\*\*date:\*\*\s*(\d{4})-(\d{2})-(\d{2})"
                        r"(?:[ T](\d{2}):(\d{2})(?::(\d{2}))?)?", re.M)


def _fm_date(p):
    """(instant, has_time) from the archive's own `- **date:**` line, or (None, False).

    FAIL-CLOSED PARSING (codex, `archive/peer/2026-09-17-open31b-stamp-codex.md` §2, which found that the first
    version "is not actually a frontmatter parser"): it read 4,000 characters and matched anywhere in them, so a
    date line that a peer's QUESTION or a later hand edit put in the body could become authoritative. Now the
    search is restricted to the text ABOVE `## Question` - peer.ps1 emits the header before the task
    (`tools/peer.ps1`, the archive heredoc) - and MORE THAN ONE match in that header is treated as no date at
    all rather than as the first one.
    """
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            head = f.read(4000)
    except OSError:
        return None, False
    head = head.split("## Question", 1)[0]
    ms = FM_DATE_RE.findall(head)
    if len(ms) != 1:
        return None, False
    m = FM_DATE_RE.search(head)
    if not m:
        return None, False
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if m.group(4):
        return time.mktime((y, mo, d, int(m.group(4)), int(m.group(5)), int(m.group(6) or 0), 0, 0, -1)), True
    return time.mktime((y, mo, d, 0, 0, 0, 0, 0, -1)), False


def stamp(p):
    """A timestamp a BULK EDIT cannot inflate (user's instruction, 2026-09-16: "고칠 것") - and that a RE-ARCHIVE
    cannot DEFLATE (OPEN 31, 2026-09-17).

    `newest_retrospective()` used to pick by mtime, and `tools/frontmatter.py` rewrites the mtime of every file in
    `archive/peer/` in one pass - 216 of them on 2026-09-15. So a cosmetic frontmatter run made the newest
    retrospective look newer than every build log and SILENTLY OPENED THIS GATE. A gate that a formatting tool can
    open is not a gate. `audit_cycle.py` had already hit this and switched to the date in the filename; the lesson
    never reached here. `min(ctime, mtime)` keeps the moment the file was first written: a later bulk edit raises
    mtime and leaves creation time alone, so the pair's minimum is stable.

    === THE OPPOSITE DEFECT, MEASURED 2026-09-17 ===
    That same minimum is WRONG in the other direction when peer.ps1 RE-ARCHIVES a slug. On this NTFS volume,
    deleting a file and writing the same name back KEEPS THE OLD CREATION TIME (tunneling - measured directly:
    write at 16:37:43, delete + rewrite at 16:37:45, ctime still 16:37:43; a plain overwrite likewise). So for any
    slug archived twice, `min(ctime, mtime)` is the FIRST EVER write and the second review is invisible to every
    gate that calls this - which is OPEN 31's "re-archiving an existing slug keeps the OLD ctime and the gate never
    sees the new review".

    The only stamp a re-archive updates and a bulk frontmatter pass does not is the archive's OWN TEXT, so:
      1. frontmatter `- **date:** YYYY-MM-DD HH:MM[:SS]` -> use it exactly (peer.ps1 has written a time since
         2026-09-17);
      2. frontmatter with a DATE only (every archive written before that) -> `max(min(ctime, mtime), midnight of
         that date)`. A re-archive on a later day therefore lifts to that day instead of staying at the original
         ctime; a bulk edit still cannot lift anything, because it does not touch the `date:` line;
      3. no frontmatter date at all -> the old `min(ctime, mtime)`.
    Case 2 is deliberately conservative (midnight, not mtime): it repairs a stale stamp by at most the difference
    between two calendar days and can never be inflated by a formatting tool.
    """
    try:
        base = min(os.path.getctime(p), os.path.getmtime(p))
    except OSError:
        base = 0.0
    fm, has_time = _fm_date(p)
    if fm is None:
        return base
    try:
        mt = os.path.getmtime(p)
    except OSError:
        return base
    # NEVER LATER THAN THE FILE'S OWN mtime (codex §1, same archive): "'never later than mtime' is not an
    # invariant of stamp(); it is merely true of the current corpus - a future or edited timed line is returned
    # exactly". Too HIGH is the fail-OPEN direction for `newest_retrospective()` (max wins, so builds vanish from
    # the window) and for `premature_build()` (a review appears to postdate recipe text it never saw). Clamping
    # costs nothing and removes that direction entirely.
    if has_time:
        return min(fm, mt)
    return min(max(base, fm), mt)


def newest_build_log():
    best = None
    for p in glob.glob(os.path.join(BENCH, "*.log")):
        if not logclass.is_build_log(p):
            continue
        try:
            t = os.path.getmtime(p)
        except OSError:
            continue
        if time.time() - t > MAX_AGE_S:
            continue
        if best is None or t > best[1]:
            best = (p, t)
    return best


def newest_retrospective():
    """The newest retrospective THAT ACTUALLY RETURNED AN ANSWER.

    Added 2026-09-15 after cycle 8's retrospective TIMED OUT at peer.ps1's 180 s default and still archived a file.
    That file was newer than every build log, so this gate would have opened on a review that, in rule 5's own
    words, "told you NOTHING". It is the same defect that was fixed in guard_peer.py the same afternoon - the
    outcome line was written but never read - and fixing it in one place was not enough.
    Files with no `outcome:` line at all are pre-2026-09-15 archives and still count."""
    best = None
    for p in glob.glob(os.path.join(PEER, "*retrospective*.md")):
        try:
            t = stamp(p)                      # NOT getmtime - a frontmatter pass would move it; see stamp()
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                head = f.read(4000)
        except OSError:
            continue
        m = re.search(r"^\-\s*\*\*outcome:\*\*\s*(\w+)", head, re.M)
        if m and m.group(1).upper() != "ANSWERED":
            continue
        if best is None or t > best[1]:
            best = (p, t)
    return best


RECIPE_ARG_RE = re.compile(r"--recipe(?:\s+|=)(\"[^\"]+\"|'[^']+'|\S+)")


def running_review_recipes(body):
    """card chat-P1 1(c): the normcase'd absolute recipe paths the LAST `BGRUN START` line of a prior-art log names with
    `--recipe`; set() for a `--no-recipe` review; None when there is no START line or it carries neither (fail closed)."""
    starts = [ln for ln in body.splitlines() if ln.startswith("BGRUN START")]
    if not starts:
        return None
    line = starts[-1]
    got = [m.group(1).strip("\"'") for m in RECIPE_ARG_RE.finditer(line)]
    if not got:
        return set() if "--no-recipe" in line else None
    return set(os.path.normcase(os.path.abspath(g if os.path.isabs(g) else os.path.join(ROOT, g.replace("/", os.sep))))
               for g in got)


def premature_build(cmd):
    """THE DEVICE FOR `premature-build` (docs/violation-decisions.md, 2026-09-16 19:16, round 3).

    Occurrences: cycles 7, 9, 11. The cycle-11 instance is a clock fact, not an opinion: `priorart_cycle11.log`
    dispatched 16:24:00 and ran 427 s, while `build_opdelete_v1.log` started 16:26:10 - the build was launched
    five minutes INSIDE its own prior-art review, and that review's finding 5 predicted the build's failure before
    the log did. A rule about patience is exactly the kind that fades after a compaction, so it becomes a refusal.

    Two conditions, both read off the filesystem, returning the refusal text or None:

      (a) a prior-art review is STILL RUNNING - any `tools/bench/priorart_*.log` newer than the newest
          retrospective that carries no `BGRUN END` / `BGRUN TIMEOUT` line. (bgrun always writes one of those, so
          its absence means the dispatch has not returned.)
      (b) the build has NO prior-art review of its own - no `archive/peer/*priorart*.md` is newer than the recipe
          FILE being run. Editing the recipe after its review re-arms this, which is the point: the review that
          matters is the one that saw this text.

    (b) APPLIES ONLY TO A RECIPE'S FIRST RUN AFTER ITS REVIEW (judgement decision, 2026-09-17, cycle 15).
    The prior-art question is "has this already been built/measured/failed here" - a question about the DIRECTION,
    which a review answers once. A RE-RUN after a failed prediction is a different question, and it already has its
    own mandatory gate: `guard_peer.py` refuses the next build until a peer review newer than the failing log is
    archived. Charging a second prior-art round to every repair made the two gates redundant and expensive - cycle
    15 paid FIVE prior-art rounds (~45 min) on ONE probe (`priorart_loopendref`, `..._rev2`, `moveinto_rev4/5/6`),
    and round 5 returned `novel`, i.e. it had nothing left to say. So:

        if a BUILD LOG named `tools/bench/<recipe-stem>*.log` is NEWER than the newest prior-art review,
        this recipe has ALREADY RUN ONCE under that review -> a re-run is allowed, however often the file is
        edited, and the failed prediction is guard_peer's business, not this gate's.

    (b) HAS A SECOND EXEMPTION (judgement decision, 2026-09-17, `docs/d1-build-plan.md` §11g.3), for the recipe
    that has NOT yet run at all - the review-then-fix-then-run path:

        if the NEWEST prior-art review's "What was done with it" section carries a valid
        `FIXED: <slug> - <this recipe>:<line> - ...` line, the edit IS that review's disposition -> ALLOWED.

    Valid means what the verdict gate already means by it (`fixed_citations`): the line sits under the
    disposition heading, the cited path exists, and it changed AFTER the review. So the release is a statement
    the filesystem checks, not an assertion. Self-tested by `tools/bench/selftest_guard_cycle_fixed.py`.

    AND THE SAME CLAIM REFUSES WHEN IT FAILS THAT CHECK (2026-09-18, cycle 20 step 1; STATUS OPEN 43). The
    exemption used to be evaluated only inside `if not newer:`, where the recipe is newer than the review by
    definition and CLAUDE.md:449 condition (b) can never reject - so (b) had never refused anything, and in the
    opposite case (a review NEWER than the recipe) the gate allowed without reading the disposition at all. The
    newest review's claim on this recipe is now read FIRST, via `fixed_claim()`: it allows when the line
    validates, REFUSES when a line cites this recipe and fails (a), (b) or (c), and changes nothing when no line
    mentions it.

    Both exemptions require a prior-art review to EXIST: with none archived at all, (b) still blocks, because then
    nothing ever reviewed this direction. It is deliberately keyed on the review's stamp rather than on the recipe's
    mtime - the repair edit always post-dates the failing run, so keying on the recipe would never fire.

    Only RECIPE builds reach here (BUILD_RE, command position, EXEMPT_RE already applied). Diagnostics under
    tools/bench, doc writes, peer dispatches and the reviews themselves are never touched.
    """
    retro = newest_retrospective()
    floor = max(retro[1] if retro else 0.0, time.time() - MAX_AGE_S)
    m = BUILD_RE.search(cmd)
    rel = (m.group(1) if m else "").strip().strip("'\"")
    fp = (rel if os.path.isabs(rel) else os.path.normpath(os.path.join(ROOT, rel.replace("/", os.sep)))) if rel else ""
    for p in sorted(glob.glob(os.path.join(BENCH, "priorart_*.log"))):
        try:
            if os.path.getmtime(p) < floor:
                continue
            body = open(p, "r", encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if "BGRUN END" not in body and "BGRUN TIMEOUT" not in body:
            # (a) SCOPED TO THIS RECIPE (card chat-P1 item 1(c), user 2026-09-28): the pipeline runs a prep card's
            # prior-art review for stage N+1 WHILE stage N's recipe launches. A running review blocks only the recipe
            # its own `BGRUN START` names with `--recipe` (a `--no-recipe` review names none and blocks no recipe); a
            # review whose START line is missing, or carries neither flag, is treated as naming this one (fail closed).
            named = running_review_recipes(body)
            if named is not None and fp and os.path.normcase(os.path.abspath(fp)) not in named:
                continue
            return ("BLOCKED by tools/hooks/guard_cycle.py: a PRIOR-ART REVIEW IS STILL RUNNING.\n"
                    f"  running review log : {_rel(p)}  (no BGRUN END/TIMEOUT line yet)\n\n"
                    "Device for the `premature-build` slug (cycles 7, 9, 11 - see docs/violation-decisions.md,\n"
                    "round 3). In cycle 11 a build started 2 min into its own prior-art review, and that review's\n"
                    "finding 5 predicted the failure the build then produced. Wait for the dispatch to end, read\n"
                    "its verdicts, write the disposition, then build.\n")
    if not rel:
        return None
    if not os.path.isfile(fp):
        return None                      # cannot judge a recipe that is not on disk; the run will fail by itself
    try:
        rmt = os.path.getmtime(fp)
    except OSError:
        return None
    revs = [(p, stamp(p)) for p in glob.glob(os.path.join(PEER, "*priorart*.md"))]
    newer = [p for p, t in revs if t > rmt]
    latest = max(revs, key=lambda x: x[1]) if revs else None
    # === CLAUDE.md:449 CONDITION (b) - FIRST ENFORCEMENT, 2026-09-18 (cycle 20 step 1; STATUS OPEN 43) ===
    # This check used to live INSIDE `if not newer:`, which is the branch where the recipe is already newer than
    # every review - so (b) ("the cited path was last changed AFTER the review") was true by construction there
    # and could not reject. In the opposite case, a review NEWER than the recipe, the gate returned None before
    # looking at the review's disposition at all: an invalid `FIXED:` line citing this very recipe was worth
    # exactly as much as no line. That is the inversion `selftest_guard_cycle_fixed.py` T6 has always caught
    # (T6 = a FIXED line citing a recipe last changed BEFORE the review -> must REFUSE, observed ALLOWED).
    # Now the newest review's claim on THIS recipe is read first, and it decides in both directions:
    #   released (a+b+c pass)      -> allowed, whatever the mtimes say (the old disposition exemption);
    #   claimed but NOT released   -> REFUSED, naming the condition that failed (the enforcement that was missing);
    #   no claim at all            -> unchanged: fall through to the mtime rule below.
    # Nothing that validated before stops validating: a valid FIXED line still allows, and a review that never
    # mentions this recipe is judged exactly as it was.
    if latest:
        try:
            with open(latest[0], "r", encoding="utf-8", errors="replace") as f:
                _rbody = f.read()
        except OSError:
            _rbody = ""
        claimed, released, why = fixed_claim(latest[0], _rbody, fp)
        if released:
            return None
        if claimed:
            return ("BLOCKED by tools/hooks/guard_cycle.py: this recipe's `FIXED:` RELEASE DOES NOT VALIDATE.\n"
                    f"  recipe        : {rel}  (last changed "
                    f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(rmt))})\n"
                    f"  review        : {_rel(latest[0])}\n"
                    f"  why it failed : {why}\n\n"
                    "CLAUDE.md:449 - a `FIXED:` line releases only when (a) the cited path exists, (b) it was last\n"
                    "changed AFTER the review, and (c) the line sits under '" + DISPOSITION_MARK + "'.\n"
                    "A promise is not a fix and an assertion is not a refutation: a claim that fails the\n"
                    "filesystem check is worth LESS than no claim, because it says the finding was answered when\n"
                    "the bytes say it was not. Make the change the line describes (then it post-dates the review),\n"
                    "or write the honest release - and `CYCLE_GUARD_OFF` is never the answer.\n")
    if not newer:
        # THE RE-RUN EXEMPTION (2026-09-17) - see this function's docstring. A recipe that has already produced a
        # build log UNDER the newest prior-art review has had its direction reviewed; the next run is a repair, and
        # repairs are gated by guard_peer.py's failed-prediction rule instead.
        if latest:
            stem = os.path.splitext(os.path.basename(fp))[0]
            ran = []
            for p in glob.glob(os.path.join(BENCH, stem + "*.log")):
                if not logclass.is_build_log(p):
                    continue
                try:
                    if os.path.getmtime(p) > latest[1]:
                        ran.append(p)
                except OSError:
                    continue
            if ran:
                return None
            # THE DISPOSITION EXEMPTION (judgement decision, 2026-09-17, d1-build-plan.md §11g.3). The intended
            # path is REVIEW -> FIX -> RUN, and STATUS.md had recorded the cost of not having it: "Editing a
            # recipe re-arms guard_cycle ... every post-review fix costs another ~10-min round". A review whose
            # findings are answered BY EDITING THE RECIPE then blocked the very run it had improved - the same
            # shape as the `REFUTED:`-only hole that `FIXED:` was added for on 2026-09-16, one layer down.
            # Strictness is not lowered: the release is the SAME machine-checked `FIXED:` line the verdict gate
            # already demands - it must sit under "## What was done with it", cite a path that EXISTS, and that
            # path must have changed AFTER the review. Citing THIS recipe file is therefore a statement the
            # filesystem can verify: "the edit you are about to run is this review's disposition."
            # MOVED OUT 2026-09-18 (cycle 20 step 1): the same `fixed_claim(latest)` call now runs ABOVE, before
            # the mtime rule, so that a claim which FAILS the check refuses instead of being invisible. Reaching
            # this line therefore means the newest review makes no claim on this recipe at all.
        # PROVEN PATTERN (card chat-P1 item 2a, user 2026-09-28 "1~4번은 적용하도록"): a recipe whose mechanism - its
        # stageplan ops + create classes + the stagekit/stagexec functions it calls - already ran CLEAN in >= 2 other
        # stages (stage_prerun.proven_pattern, from stage_runs.jsonl + each run's log) asks nothing the prior-art
        # question has not answered twice. Allowed and logged; condition (a) above and the verdict gate stay as they are.
        try:
            import stage_prerun
            ok_p, stages_p, _sig = stage_prerun.proven_pattern(fp)
        except Exception:                # noqa: BLE001 - a broken reader never releases (fail closed)
            ok_p, stages_p = False, []
        if ok_p:
            _proven_log("PROVEN-PATTERN | %s | %s | no prior-art review owed: signature covered by clean runs of %s"
                        % (time.strftime("%Y-%m-%d %H:%M:%S"), rel, ", ".join(stages_p)))
            return None
        return ("BLOCKED by tools/hooks/guard_cycle.py: this RECIPE HAS NO PRIOR-ART REVIEW NEWER THAN ITSELF.\n"
                f"  recipe        : {rel}  (last changed "
                f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(rmt))})\n"
                f"  newest priorart review : "
                + (f"{_rel(latest[0])} ({time.strftime('%Y-%m-%d %H:%M', time.localtime(latest[1]))})"
                   if latest else "none archived") + "\n\n"
                "Device for the `premature-build` slug. Either no prior-art review has run for this build, or the\n"
                "recipe was edited AFTER the review that saw it AND it has never run under that review.\n"
                "(A recipe that HAS already run once under the newest prior-art review is exempt - a repair after a\n"
                "failed prediction is guard_peer.py's gate, not this one. 2026-09-17.)\n"
                "Dispatch it and let it finish (the CURRENT command form - `--recipe` became mandatory on\n"
                "2026-09-18, and without it the dispatcher REFUSES rather than leaving the launch gate inert):\n"
                "  py tools/bgrun.py --max-min 20 --log tools/bench/priorart_<slug>.log -- \\\n"
                "     py tools/prior_art_review.py --plan-file <plan> --slug <slug> --trigger cycle-start \\\n"
                "        --recipe " + rel + "\n"
                "  (launch it from PowerShell; the Bash tool returns rc 127 for this one today. A review that\n"
                "   genuinely has no recipe - a plan document - takes --no-recipe \"<reason>\" instead, and the\n"
                "   reason is written into the archived review.)\n")
    return None


def _proven_log(line):
    """One PROVEN-PATTERN line to stderr and tools/bench/jev_gate.log (resolved at call time: a self-test's BENCH)."""
    sys.stderr.write(line + "\n")
    try:
        with open(os.path.join(BENCH, "jev_gate.log"), "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


def _rel(p):
    """`os.path.relpath` that cannot raise. On Windows it throws `ValueError: path is on mount 'C:', start on
    mount 'G:'` for a path on another drive - which crashed this hook's own self-test (2026-09-17) and would
    crash the hook itself if BENCH/PEER ever pointed off the project drive. A refusal message is not worth a
    traceback."""
    try:
        return os.path.relpath(p, ROOT)
    except ValueError:
        return p


def block(msg):
    sys.stderr.write(msg)
    sys.exit(2)


def offline_only(cmd):
    """card 112-1 T6: True when EVERY segment of `cmd` that BUILD_RE matches is `stage_prerun.py --dry|--prerun`
    (stop_record.offline_checker, bgrun-wrapped or not; segments split by tools/launchunit.segments, the one shared
    splitter). False when any recipe-naming segment is anything else, or when no segment names a recipe."""
    import launchunit
    segs = [s for s in launchunit.segments(cmd) if BUILD_RE.search(s)]
    return bool(segs) and all(stop_record.offline_checker(s.strip()) for s in segs)


def main():
    if os.environ.get("CYCLE_GUARD_OFF") == "1":
        return
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    cmd = (data.get("tool_input") or {}).get("command") or ""
    if not BUILD_RE.search(cmd) or EXEMPT_RE.search(cmd):
        return

    # THE LAUNCH GATE (cycle 18, docs/cycle18-plan.md Pre-decided 2). One line, no logic duplicated: the verdict
    # gate at the bottom of this function only ever looks at the NEWEST prior-art review, so an older review's
    # standing verdict stops nothing once a newer one is archived - and an annotated review looks disposed even
    # when its findings were never answered for the recipe about to run. `tools/stop_record.py` keys the refusal
    # to the recipe's own path + hash instead, and releases only on the same FIXED:/REFUTED: lines this file
    # already validates.
    allow, why = stop_record.check_command(cmd)
    if not allow:
        block(why)

    # OFFLINE CHECKERS ARE NOT BUILDS (card 112-1 T6; docs/violation-decisions.md device-failed 2026-09-27 22:20).
    # BUILD_RE also matches `stage_prerun.py --dry tools/recipes/X.py` (the `\bpy` of `stage_prerun.py` is in command
    # position for it), so the verdict / timing / retrospective gates below refused an OFFLINE dry of an unreleased
    # recipe that the launch gate above had already classed "exempt" (card 107-1). The same shared predicate decides
    # it here: every segment that names a recipe must be an offline checker; one launch segment keeps every gate on.
    if offline_only(cmd):
        return

    due = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "violations.py"), "--due"],
                         capture_output=True, text=True, timeout=120)
    if due.returncode == 1 and due.stdout.strip():
        block("BLOCKED by tools/hooks/guard_cycle.py: a retrospective violation has reached its threshold.\n"
              f"{due.stdout}\n"
              "Build the mechanical device for it first (a hook, a reader, or a gate), then continue. "
              "CLAUDE.md: 'when a rule is broken twice, move it into a hook'.\n")

    # THE OUTCOME LAYER (user, 2026-09-15). One line, by the user's own budget for it: every 5 cycles
    # or 7 days, the project's RESULTS get reviewed, not just its process. A cycle can be run perfectly
    # and still be the wrong cycle, and the session doing the work is the last to notice.
    od = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "outcome_review.py"), "--due"],
                        capture_output=True, text=True, timeout=120)
    if od.returncode == 1:
        block("BLOCKED by tools/hooks/guard_cycle.py: the project's OUTCOMES are due for review.\n"
              f"  {od.stdout.strip()}\n\n"
              "Cycle retrospectives ask how a cycle was run; nobody has asked whether the work is reaching the\n"
              "goal in project-requirements/. Run:\n"
              "  py tools/bgrun.py --max-min 15 --log tools/bench/outcome_review.log -- py tools/outcome_review.py\n"
              "then annotate it and act on its OUTCOME-VIOLATION lines - those are answered by making the next\n"
              "cycle a DELIVERY cycle, not by building another tool.\n")

    # THE TIMING GATE (device for `premature-build`, 2026-09-16 round 3) runs BEFORE the verdict gate below:
    # a review that has not returned has no verdicts to be refuted or fixed, so the verdict gate is blind to
    # exactly the case that cost cycle 11 - a build launched while its own review was still in flight.
    msg = premature_build(cmd)
    if msg:
        block(msg)

    # THE PRIOR-ART REVIEW STOPS THE WORK (user's decision, 2026-09-15). A warning was not enough: an outcome
    # review's "do not build that reader" was overridden by my own judgement hours later. Any verdict other than
    # `novel` blocks the next build, and the ONLY release is to open the cited file and refute it IN WRITING -
    # one `REFUTED: <slug>` line per blocking slug, added to the review file itself, so the next reviewer can
    # check the refutation the same way.
    # stamp(), not getmtime: annotating a review (which every review owes) must not make an OLD one look newest,
    # and a frontmatter pass must not reorder them at all. See stamp().
    pa = sorted(glob.glob(os.path.join(PEER, "*priorart*.md")), key=stamp)
    if pa and time.time() - stamp(pa[-1]) <= MAX_AGE_S:
        try:
            with open(pa[-1], "r", encoding="utf-8", errors="replace") as f:
                body = f.read()
        except OSError:
            body = ""
        # THIS GATE HAD NEVER FIRED (found 2026-09-16). The pattern was `^PRIOR-ART:\s*([a-z-]+)\s*$` - slug at end
        # of line, nothing after it - while prior_art_review.py's own prompt demands "naming a FILE and LINE for
        # every finding", so every real verdict reads
        #     PRIOR-ART: contradicted      (A3a - NAMES.md:823 cited for a fact stated at NAMES.md:864-866)
        # and matched NOTHING. The prompt and the parser contradicted each other, so the review the user gave
        # stopping power to ("실제로 멈추는 권한을 부여하는 게 좋지 않을지", 2026-09-15) was inert from the day it
        # was built: eight unrefuted verdicts on 2026-09-16 parsed as zero. Builds had been blocked only by an
        # unrelated clock bug, i.e. by accident.
        # Two changes: allow a citation after the slug (which is the whole point of the verdict), and scan only the
        # ANSWER - the archive embeds the QUESTION too, and the question lists the legal slugs as a menu line.
        answer = body.split("\n## Answer", 1)[-1]
        slugs = [s for s in PRIOR_ART_RE.findall(answer) if s != "novel" and s in PRIOR_ART_SLUGS]
        released, bad_fixed = released_slugs(pa[-1], body)     # ONE definition, shared with tools/stop_record.py
        open_slugs = [s for s in dict.fromkeys(slugs) if s not in released]
        if open_slugs:
            rejected = "".join(f"  rejected FIXED : {s} - {why}\n" for s, why in bad_fixed)
            block("BLOCKED by tools/hooks/guard_cycle.py: the PRIOR-ART review has findings that are neither\n"
                  "refuted nor fixed.\n"
                  f"  review       : {_rel(pa[-1])}\n"
                  f"  open verdicts: {', '.join(open_slugs)}\n"
                  f"{rejected}\n"
                  "This review answers one question - has this already been done here - and its verdicts stop the\n"
                  "work, because repeating a build or a decision we already made is the cheapest waste there is.\n"
                  "There are exactly TWO releases, both written into the review file itself, both paid for with a\n"
                  "citation:\n"
                  "  1. the review is WRONG - open the FILE AND LINE it cites and show in writing that it does not\n"
                  "     cover this case:\n"
                  "         REFUTED: <slug> - <file>:<line> says X, which does not cover Y because ...\n"
                  "  2. the review is RIGHT and the work already changed - cite the change:\n"
                  "         FIXED: <slug> - <path>:<line> - <one sentence saying what changed>\n"
                  "     It releases only if (a) <path> exists under the project, (b) <path> was last changed AFTER\n"
                  "     the review (its frontmatter date, else the file's own stamp), and (c) the line sits under\n"
                  f"     '{DISPOSITION_MARK}' in the review file.\n"
                  "An assertion is not a refutation and a promise is not a fix; the citation is the currency.\n")

    # A CYCLE IS NOT ONE BUILD (fixed 2026-09-15). The original test was "any build log newer than the newest
    # retrospective => block", which re-arms on the FIRST build of a cycle and therefore permits exactly one build
    # per retrospective - cycles 1-7 each ran many. The docstring's intent is "the PREVIOUS cycle", and the only
    # mechanical way to tell previous from current is a budget: work done since the last retrospective IS the
    # current cycle until it grows past a cycle's worth, at which point the review is genuinely overdue.
    log = newest_build_log()
    retro = newest_retrospective()
    # THE BUDGET COUNTS RECIPE BUILDS, NOT EVERY LOG IN tools/bench (Pre-decided 112, 2026-09-22). On
    # 2026-09-22 09:0x this set held 16 logs whose OLDEST and NEWEST were `jev_trial.log` (a model-API trial)
    # and `selftest_guard_peer_jev.log` (a hook self-test) - neither builds anything in LabVIEW, and together
    # they set BOTH the count and the span the gate then called an overdue cycle. `is_recipe_build_log` reads
    # each log's own last `BGRUN START` COMMAND and counts it only when that command RAN a tools/recipes/*.py,
    # which is the same question `BUILD_RE` asks on the command side. `newest_build_log()` above is deliberately
    # left on `is_build_log`: it answers "is there unreviewed work at all", and guard_peer arms the
    # failed-prediction review off the same predicate - narrowing that one would disarm a mandatory rule.
    since = [p for p in glob.glob(os.path.join(BENCH, "*.log"))
             if logclass.is_recipe_build_log(p)
             and (retro is None or os.path.getmtime(p) > retro[1])
             and time.time() - os.path.getmtime(p) <= MAX_AGE_S]
    # THE CLOCK MEASURES BUILDING, NOT WAITING (user's instruction, 2026-09-16: "해당 조건은 개선할 것").
    # It used to be `now - retro`, i.e. time elapsed SINCE THE LAST REVIEW - which counts sleep, discussion, lint
    # passes and weekends as if they were a cycle's worth of work. The consequence was not theoretical: on
    # 2026-09-16 a 337-byte SELF-TEST of the bgrun runner, plus an overnight gap, tripped it and blocked the first
    # build of a fresh cycle. Generalised, ANY first build more than CYCLE_HOURS after a retrospective was refused,
    # which is the normal case for a project with overnight gaps - the gate fired hardest exactly when the least
    # work had been done.
    # The honest quantity is how long the CURRENT, UNREVIEWED cycle has been building: the span from its oldest to
    # its newest build log. Zero or one build spans nothing and is not a cycle; a genuine cycle grinding for eight
    # hours still trips, which is what the gate is for. `since` is already the unreviewed set.
    if retro is None:
        hours = 999.0
    elif len(since) >= 2:
        ts = [os.path.getmtime(p) for p in since]
        hours = (max(ts) - min(ts)) / 3600.0
    else:
        hours = 0.0
    overdue = len(since) >= CYCLE_BUILD_BUDGET or hours >= CYCLE_HOURS
    if log and (retro is None or (retro[1] < log[1] and overdue)):
        block("BLOCKED by tools/hooks/guard_cycle.py (CLAUDE.md: every cycle ends with a RETROSPECTIVE review).\n"
              f"  newest build log : {_rel(log[0])}\n"
              f"  newest retrospective : {_rel(retro[0]) if retro else 'none archived'}\n\n"
              "The previous cycle's execution has not been reviewed as a cycle - only its individual hypotheses were.\n"
              "Run:\n"
              "  py tools/bgrun.py --max-min 10 --log tools/bench/retro.log -- py tools/retrospective.py --cycle <N>\n"
              "then annotate the archived review and start the new cycle. Reading logs, writing docs, running\n"
              "tools/audit_cycle.py and dispatching peers are never blocked.\n")


if __name__ == "__main__":
    main()
