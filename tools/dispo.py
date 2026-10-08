# ---
# labview: none
# hardware: none
# ---
"""Find the DISPOSITION section ('## What was done with it') of an archived peer review (card 150-a3-3, docs/d1/ring-p4c.md
PD365(f)). Stdlib only; imported by tools/violations.py, tools/cycle_runner.py (retro_undisposed) and tools/audit_cycle.py
(A4, A9). Not a hook.

Why: those sites cut the review at the FIRST substring occurrence of the heading. A review whose ANSWER quotes the heading
inline (archive/peer/2026-10-08-retrospective-cycle149.md:98, :147, :370; retrospective-cycle148.md:98, :147) was cut at the
quote, so the answer was truncated and the answer text was read as the disposition. The heading is a line that is exactly
the heading at column 0 (trailing blanks allowed); an inline quote is not a heading. With several such lines (card 150-a3-4)
the LAST one whose section carries non-placeholder text wins, else the last one.

Contract (kept so outputs on files with ONE column-0 heading are byte-identical to the old code):
  find_disposition(body) -> (answer, disposition_text | None)
      answer = body[:i], disposition_text = body[i + len(DISPOSITION_H):] (the text right after the heading characters, as
      `body.split(H, 1)[1]` gave), i = heading_index(body); no heading -> (body, None).
  heading_index(body) -> i or -1 (the `body.find(H)` replacement).
  disposition_len(body) -> length of the disposition with the '(Claude fills in)' placeholder lines removed and stripped
      (cycle_runner.py retro_undisposed / guard_peer.py:852), or None when there is no heading.
Prior art (grep before writing): no shared helper existed; guard_peer.py:834-855 and cycle_runner.py:997-1022 each carry a
copy of the first-occurrence test; tools/hooks/** is never edited by a runner card, so guard_peer keeps its copy (logged
with gate_fp.py).
"""
import re

DISPOSITION_H = "## What was done with it"
HEADING_RE = re.compile(r"^## What was done with it[ \t\r]*$", re.M)
PLACEHOLDER_RE = re.compile(r"^\s*\(?\s*claude fills in\s*\)?\s*$", re.I | re.M)      # = cycle_runner.py:998, guard_peer.py:835


SECTION_END_RE = re.compile(r"^## ", re.M)       # a section ends at the next column-0 level-2 heading (or EOF)


def heading_index(body):
    """Start index of the disposition heading, else -1 (card 150-a3-4)."""
    # Rule: the LAST column-0 heading whose section (to the next column-0 '## ' or EOF) is non-empty once the
    # '(Claude fills in)' placeholder is stripped; if every such section is empty/placeholder, the LAST heading.
    heads = list(HEADING_RE.finditer(body))
    if not heads:
        return -1
    for m in reversed(heads):
        nxt = SECTION_END_RE.search(body, m.end())
        section = body[m.end():nxt.start() if nxt else len(body)]
        if PLACEHOLDER_RE.sub("", section).strip():
            return m.start()
    return heads[-1].start()


def find_disposition(body):
    """(answer, disposition_text) split at the last line-anchored heading; (body, None) when there is none."""
    i = heading_index(body)
    if i < 0:
        return body, None
    return body[:i], body[i + len(DISPOSITION_H):]


def disposition_len(body):
    """Characters left in the disposition after placeholder lines are removed and the rest stripped; None = no heading."""
    tail = find_disposition(body)[1]
    if tail is None:
        return None
    return len(PLACEHOLDER_RE.sub("", tail).strip())
