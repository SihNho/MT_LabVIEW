---
card: 150-a1-2
status: current
date: 2026-10-08
---
# Brief 150-a1-2 - STATUS.md back to about 110 lines, older text moved VERBATIM (PD364(h)); offline

Plan: `docs/d1/ring-p4c.md` PD364(h) (lines 250-252). CLAUDE.md rule 4: content is relocated, never rewritten or deleted. STATUS.md is 203 lines (md5
050f34f4) and the archive target `archive/2026-10-08-status-cycle150-relocate.md` exists with a 12-line header and no body.

## Steps
1. Copy STATUS.md to `tools/bench/diag_c150_a1_2_status_before.md` (md5 quoted). Work from this copy's line numbers.
2. **Keep byte-identical in STATUS.md:** the frontmatter; the chat's STOP lines at the top (the two `STOP - CHAT CARD chat-T6` / `STOP - RELAUNCH FOR
   PYTHON PATH` lines and the RESTARTED line); the `labview-lock` block with its `relocated_c81` key; the hardware banner and the `rig-state:` line
   (whole line incl. the HTML comment); the `## OPEN` heading and live items; the `## NEXT` PARALLELISM RULE paragraph; the `CYCLE 150 PURPOSE` and
   `OUTCOME ESCALATION (cycle 150)` paragraphs; `current-bed:` and its comment if present; the `## Where to look` section; `START HERE`.
3. **Move VERBATIM, in original order, to the end of `archive/2026-10-08-status-cycle150-relocate.md`** (append, under a heading per source section with
   the source line range): every `## NEXT` paragraph older than cycle 150 (the "(cycle 149 round 3)" down to the last cycle-142 paragraph) and every
   `(history)` line of the top banner, leaving ONE pointer line in each place: `(history) RELOCATED VERBATIM -> archive/2026-10-08-status-cycle150-relocate.md
   §<n>`. Do not touch the existing 12-line header of the archive file except to append.
4. **Verify mechanically (`tools/bench/diag_c150_a1_2_check.py`, card-local):** every moved line of the before-copy appears byte-for-byte in the
   archive; every kept line of the before-copy appears byte-for-byte in the new STATUS.md; new STATUS.md line count in 100..120; line sets
   (before) == (new STATUS lines minus pointer lines) union (archive body lines); `py tools/doc_lint.py` result quoted before/after (no NEW error).
5. OPEN items 53 and 58 are already marked closed in STATUS by the judgement; leave them as they are.

## Return conditions
A line you cannot classify as moved/kept (list it, change nothing more); the line-count target unreachable without rewriting text; doc_lint gaining an
error. The edit of STATUS.md is authorised by this card (`flags.status_edit`); no other doc is edited.

## Report (`tools/bench/diag_c150_a1_2_facts.md`, <= 25 lines)
Before/after line counts and md5, what was kept (section list), what moved (line ranges, archive sections), the check output, doc_lint before/after.
`OPEN:` line. Facts only.
