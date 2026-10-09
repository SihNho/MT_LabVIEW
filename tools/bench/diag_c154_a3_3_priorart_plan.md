---
card: 154-a3-3
status: current
date: 2026-10-09
---
# Prior-art re-review (DIFF-ONLY in content) of tools/recipes/stage_d1_ring_p5s01a.py after a two-string fix

`tools/priorart_diff.py` finds no approved sibling for this recipe (pattern key unique), so the tool demands a full
review; the substance under review is ONLY the two lines below. The previous review of this same recipe answered
`PRIOR-ART: novel` (`archive/peer/2026-10-09-priorart-priorart-c154-a3-2b-p5s01a.md:300`) and its Note 2 asked for
exactly this change (the result label copied from the P4 recipe would mislabel the step).

Changed lines (card 154-a3-3, brief step 1, names only; nothing else in the file changed, plan/pred/licence unchanged):
- `tools/recipes/stage_d1_ring_p5s01a.py:173`
  - old: `s.es("after all rows (ExecState 0 expected: session 8's in-between file is broken by design)")`
  - new: `s.es("after all rows (ExecState 0 expected: P5-1a's in-between file is broken by design)")`
- `tools/recipes/stage_d1_ring_p5s01a.py:191`
  - old: `"level": "STRUCTURAL, in-between file of P4 (v18 session 8), broken by design, never run"`
  - new: `"level": "STRUCTURAL, in-between file of P5 (P5-1a), broken by design, never run"`

Both strings are a log label and a result-record label; neither reaches LabVIEW, a gate, or a computation.
Question: is there anything in these two changed lines that already exists, was refuted, or conflicts with a user
rule? The rest of the recipe and the plan were reviewed `novel` in the review cited above and are context only.
