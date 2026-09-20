r"""violations.py - count the VIOLATION slugs that retrospectives recorded. The counting is the point.

Claude proposed "add a mechanical device when a violation repeats" and the user asked the right question: how would
you know it repeated? (2026-09-15: "회고가 반복해서 위반을 지적하는지는 어떻게 알아?") If the counter is Claude's
memory, it counts to whatever is convenient. So the count lives in the files: each retrospective ends with
`VIOLATION: <slug>` lines, and this reads them.

  py tools/violations.py            # table of slug -> count, with the retrospectives that named each
  py tools/violations.py --due      # exit 1 and list slugs at/over the threshold (used by the cycle gate)

THRESHOLD 3: at the third occurrence of the same slug the next cycle owes a RESPONSE - and from 2026-09-16
(user's decision, option C) that response may be EITHER a mechanical device OR a written refusal to build one.

Why the second door exists. Six slugs hit 3 at once on 2026-09-15, and building six devices would itself have been
the `tooling-over-delivery` the outcome review had just flagged. Worse, two of the six (`repeated-failure-class`,
`wrong-ordering`) are answered by rules that already exist - "stop at the second failure", "resolve names before
you build" - so a device there would only add a rule to the pile. And the count was inflated by cadence: three
retrospectives ran inside five hours, on overlapping work, while the threshold was set assuming cycles spread over
days.

What keeps this from being an escape hatch: the refusal is an ARTEFACT, not a sentence in a reply. It goes in
`docs/violation-decisions.md` as a dated block naming the slug, and it must be NEWER than the retrospective that
carried the slug to threshold - so every fresh occurrence reopens the question. The gate reads the file; Claude
still does not do the counting.

  py tools/violations.py            # table of slug -> count, with the retrospectives that named each
  py tools/violations.py --due      # exit 1 and list slugs at/over threshold with NO device and NO decision

TWO ARCHIVE FORMATS, BOTH COUNTED (2026-09-16, retrospective v2). v1 archives end `VIOLATION: <slug>`; v2 archives
end `VIOLATION: <slug> | loss_min=<n> | loss_usd=<n or ?> | evidence=<file:line>`. The loss fields are summed and
printed as their own column, because seven cycles of pure counts could not tell a 90-second annoyance from a
five-hour detour - and the "3 occurrences -> build a device" rule was being driven by exactly that blind count.
A '-' in the loss column means UNMEASURED (a v1 archive), never zero.

PER-SLUG THRESHOLDS. Default 3, unchanged. `device-failed` is 1 - see THRESHOLDS below.
"""
import argparse
import collections
import glob
import os
import re
import sys

try:                                     # slug tables reach a peer through the gate's stderr; see audit_cycle.py
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
PEER = os.path.join(os.path.dirname(HERE), "archive", "peer")
THRESHOLD = 3
# TWO FORMS, BOTH COUNTED (2026-09-16, retrospective v2 proposal 1).
#   v1:  VIOLATION: <slug>
#   v2:  VIOLATION: <slug> | loss_min=<n> | loss_usd=<n or ?> | evidence=<file:line>
# The seven historical archives (cycles 7-13) carry the bare form and must keep counting - the whole point of a
# tally that lives in files is that it survives a change of format. The pipe tail is optional and its fields are
# read where present, so a v2 reviewer that omits them still records an occurrence.
SLUG_RE = re.compile(r"^VIOLATION:\s*([a-z0-9-]+)\s*(\|.*)?$", re.M)
LOSS_MIN_RE = re.compile(r"loss_min\s*=\s*([0-9]+(?:\.[0-9]+)?)", re.I)
LOSS_USD_RE = re.compile(r"loss_usd\s*=\s*\$?([0-9]+(?:\.[0-9]+)?)", re.I)
# `judgement-in-material` added 2026-09-16 (CLAUDE.md, "A delegation brief states the MEASUREMENT, never the
# result-dependent ACTION"): a brief that pre-scripts "if A then do X, else Y" moves the decision into the session
# that is not supposed to make it. Same THRESHOLD as the rest; its first countable cycle is 11.
# `device-failed` added 2026-09-16 with retrospective v2's DEVICE EFFECT question: the fault a device was built to
# stop happened anyway inside the cycle window.
KNOWN = {"repeated-failure-class", "tool-not-built", "inference-over-measurement", "rule-evaded",
         "wrong-ordering", "unreported-fact", "scope-creep", "premature-build", "judgement-in-material",
         "device-failed", "none"}

# PER-SLUG THRESHOLDS. The default stays 3 - proposal 3 (re-tuning the threshold against measured loss) is
# DEFERRED by the user until the v1/v2 comparison exists, so nothing else moves here.
# `device-failed` is 1 by construction, not by exception: the threshold exists to distinguish a one-off from a
# pattern, and a mechanical device that let its own fault through is not a one-off - it is a broken instrument,
# and every measurement taken through it since is suspect. Waiting for two more occurrences to say so is the same
# patience that let five slugs fire in 7 of 7 cycles before anyone noticed the counter had saturated.
THRESHOLDS = {"device-failed": 1}


def threshold(slug):
    return THRESHOLDS.get(slug, THRESHOLD)


DECISIONS = os.path.join(os.path.dirname(HERE), "docs", "violation-decisions.md")
# ORDERING, NOT A COOLING-OFF DAY (fixed 2026-09-16 on the user's instruction, "타임스탬프 비교로 고친다").
# Both stamps used to be bare dates and the test was `decision > retrospective` as STRINGS, so a decision written
# the same day as the retrospective that raised the slug could NEVER discharge it - "2026-09-16" > "2026-09-16" is
# false. Six slugs at threshold were unanswerable for a calendar day because of it. The file's stated intent is
# that "a fresh occurrence reopens the question", i.e. ORDER; date-only stamps cannot represent order inside a day.
# A decision heading may now carry an optional `HH:MM` and is compared as a timestamp. A retrospective's own stamp
# comes from its filename date plus the FILE's mtime time-of-day, which is when it was actually archived - so a
# same-day decision discharges if and only if it was written AFTER the review landed.
# (Found while the gate was blocking this session's own build. Not self-authorised: the block was reported and
# stood until the user decided - regrading a gate that blocks you is the `rule-evaded` slug itself.)
DEC_RE = re.compile(r"^##\s*([a-z0-9-]+)\s*[-—]\s*(\d{4}-\d{2}-\d{2})(?:[ T]+(\d{2}:\d{2}))?", re.M)


def _stamp(date, hhmm):
    """(date, time) as one comparable string. A bare date sorts BEFORE any timed entry on that date, which keeps
    the old strictly-after-the-day behaviour for undated-time blocks and is the conservative direction."""
    return f"{date} {hhmm or '00:00'}"


def _retro_date(name):
    m = re.match(r"(\d{4}-\d{2}-\d{2})", os.path.basename(name))
    return m.group(1) if m else ""


def _retro_stamp(name):
    """The retrospective's stamp, from its FILENAME date only - deliberately NOT its mtime.

    Every review owes a disposition, and writing one touches the file; an mtime-based stamp would therefore make a
    review look newer than the decision it provoked, and annotating diligently would re-block the build. That is
    the same trap `guard_cycle.stamp()` documents ("annotating a review must not make an OLD one look newest").

    So the rule is: a decision block that carries a TIME asserts it was written after the review landed that day,
    and discharges a same-day slug. A decision with only a date still has to be on a strictly later day, which is
    the old behaviour and the conservative default.
    """
    return _stamp(_retro_date(name), None) if _retro_date(name) else ""


def decisions():
    """slug -> the date of its most recent decision block. A decision older than the retrospective that raised the
    slug to threshold does not count: a fresh occurrence reopens the question."""
    out = {}
    try:
        with open(DECISIONS, encoding="utf-8", errors="replace") as f:
            body = f.read()
    except OSError:
        return out
    for slug, date, hhmm in DEC_RE.findall(body):
        st = _stamp(date, hhmm)
        if st > out.get(slug, ""):
            out[slug] = st
    return out


# A COMPARISON RUN IS NOT AN OCCURRENCE (decided 2026-09-16, OPEN-B of tools/bench/retro_v2_comparison.md).
# The v1-vs-v2 measurement re-reviewed cycles 11, 12 and 13 under the new format. Those archives are real reviews
# of real cycles - but the cycles were ALREADY counted once under v1, so letting them into the tally counts the
# same three cycles twice, and that is exactly what happened: `judgement-in-material` jumped from 3 to 4 and
# `device-failed` reached its threshold of 1 on a retroactive re-reading of cycles that had already closed.
# FLAG-BASED, NEVER NAME-BASED. The obvious cheap fix was to skip anything matching `*-v2-*`; it was rejected
# because a rename silently re-enters the tally and nobody would see it, and because the next comparison will not
# be called "v2". The archive says what it is in its own frontmatter, and this reads that.
COMPARISON_RE = re.compile(r"^comparison:\s*(true|yes)\s*$", re.M | re.I)


def is_comparison(body):
    """True if the archive's YAML frontmatter carries `comparison: true`.

    Scoped to the frontmatter block deliberately: the word could appear anywhere in a 20 KB review answer, and a
    reviewer's sentence must never be able to remove a cycle from the tally (the same rule that keeps peer_*.log
    transcripts out of guard_peer's evidence - "a reviewer's own sentence is evidence, never the thing under test").
    """
    head = body.lstrip("﻿")
    if not head.startswith("---"):
        return False
    end = head.find("\n---", 3)
    return bool(COMPARISON_RE.search(head[:end if end > 0 else 400]))


def scan():
    """(hits, loss) - slug -> the retrospectives that named it, and slug -> (loss_min, loss_usd, n_with_a_figure).

    The loss columns exist because a count alone cannot rank: a 90-second annoyance and a five-hour detour emitted
    the same line for seven cycles. Only v2 archives carry the figures, so the sums are over a subset and are
    labelled as such wherever they are printed - a partial sum quoted as a total is the `unreported-fact` slug.
    """
    hits = collections.defaultdict(list)
    loss = collections.defaultdict(lambda: [0.0, 0.0, 0])
    for p in sorted(glob.glob(os.path.join(PEER, "*retrospective*.md"))):
        body = open(p, encoding="utf-8", errors="replace").read()
        if is_comparison(body):
            continue                     # a retroactive re-review of an already-counted cycle; see is_comparison()
        # only the peer's own answer counts; a slug quoted in the annotation must not inflate the tally
        answer = body.split("## What was done with it")[0]
        for slug, tail in SLUG_RE.findall(answer):
            if slug == "none":
                continue
            hits[slug].append(os.path.basename(p))
            if tail:
                m = LOSS_MIN_RE.search(tail)
                u = LOSS_USD_RE.search(tail)
                if m:
                    loss[slug][0] += float(m.group(1))
                    loss[slug][2] += 1
                if u:
                    loss[slug][1] += float(u.group(1))
    return hits, loss


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--due", action="store_true")
    a = ap.parse_args()
    hits, loss = scan()
    unknown = [s for s in hits if s not in KNOWN]
    due = {s: v for s, v in hits.items() if len(v) >= threshold(s)}
    # A slug at threshold is discharged by a dated decision block that is NEWER than the newest retrospective that
    # named it. `DECISION: device` and `DECISION: no-device` both count - what matters is that the question was
    # answered in a file, and that a fresh occurrence reopens it.
    dec = decisions()
    for s in list(due):
        newest_retro = max((_retro_stamp(r) for r in due[s]), default="")
        if dec.get(s, "") > newest_retro:
            del due[s]
    if a.due:
        for s, v in sorted(due.items(), key=lambda kv: -len(kv[1])):
            lm, lu, n = loss[s]
            extra = (f" [reported loss: {lm:.0f} min"
                     + (f", ${lu:.2f}" if lu else "") + f", from {n} of {len(v)} occurrence(s)]") if n else ""
            print(f"DUE {s}: {len(v)} occurrences (threshold {threshold(s)}) -> {', '.join(v)}{extra}")
            if s == "device-failed":
                print("    THRESHOLD 1: a device that let its own fault through is broken, not unlucky. Fix or "
                      "withdraw the device named in the evidence field before the next build.")
            print("    Answer it in docs/violation-decisions.md: a dated block with `DECISION: device` or "
                  "`DECISION: no-device` and the reason. Dated AFTER the retrospective above.")
        if unknown:
            print(f"NOTE slugs outside the known list (add them to CLAUDE.md or map them): {unknown}")
        return 1 if due else 0
    if not hits:
        print("no VIOLATION lines recorded yet (no retrospective has run, or none found a structural fault)")
        return 0
    # THE TABLE MUST AGREE WITH THE GATE (lint, 2026-09-16). Until now `mark` was computed from the raw count while
    # the summary line below was computed from `due` (post-discharge), so the same run printed six `<== DUE` flags
    # and then "0 slug(s) due" - a reader had to know which half to believe. The discharge is the interesting state,
    # so name it and date it.
    # THE LOSS COLUMN (2026-09-16, retrospective v2). Only v2 archives carry `loss_min=`, so the column is blank
    # for the cycle 7-13 rows and that is the honest rendering: a count of nine and a cost of nothing is exactly
    # what the old format produced.
    print(f"\n{'slug':<28} {'count':>5} {'loss_min':>9}   retrospectives")
    for s, v in sorted(hits.items(), key=lambda kv: (-loss[s][0], -len(kv[1]))):
        if s in due:
            mark = "  <== DUE, no decision on file"
        elif len(v) >= threshold(s):
            mark = f"  (answered {dec.get(s, '?')} in docs/violation-decisions.md)"
        else:
            mark = ""
        lm, lu, n = loss[s]
        col = (f"{lm:.0f}({n})" if n else "-")
        print(f"{s:<28} {len(v):>5} {col:>9}   {', '.join(v)}{mark}")
    tot_min = sum(l[0] for l in loss.values())
    tot_usd = sum(l[1] for l in loss.values())
    tot_n = sum(l[2] for l in loss.values())
    print(f"\nthreshold {THRESHOLD} (device-failed: {threshold('device-failed')}); {len(due)} slug(s) awaiting a "
          f"response (a mechanical device OR a dated written refusal - user's option C, 2026-09-16)")
    print(f"loss_min column: 'x(n)' = x minutes reported across n of that slug's occurrences; v1 archives carry no "
          f"figure at all, so '-' means UNMEASURED, not zero.")
    print(f"reported loss across all slugs: {tot_min:.0f} min"
          + (f", ${tot_usd:.2f}" if tot_usd else "") + f", from {tot_n} violation line(s) that carried one\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
