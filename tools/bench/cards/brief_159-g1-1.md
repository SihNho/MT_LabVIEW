---
card: 159-g1-1
status: current
date: 2026-10-10
---
# Brief 159-g1-1 (assignment 159-3) - OFFLINE: is the cycle-158 retrospective still `retro-undisposed`? (PD389(f))

Offline, no LabVIEW, no hardware, no tools edit. `archive/peer/2026-10-10-retrospective-cycle158.md:517` already carries text under
`## What was done with it`. Measure whether the gate's own shared parser still reads that section as the placeholder:
1. Find the shared function the `retro-undisposed` gate uses (grep `retro-undisposed` / `undisposed` under `tools/`, `tools/hooks/` read-only; it is
   the gate-due source for `assign_159_3.json`). Call that function on the cycle-158 file; do not re-implement the parse. Quote function, file:line, result.
2. Write into `tools/bench/diag_c159_g1_1_facts.md` (<= 15 lines): the parser's verdict (placeholder or real text), the section's line range, and the
   gate's current state for cycle 158 (does the gate still list it as due?).
3. Only if the parser's verdict is "placeholder": write a disposition under `## What was done with it` in the cycle-158 retrospective that states, from the
   files (`docs/d1/ring-p5b.md` PD388/PD389, round-1/2 results `tools/bench/cards/assign_result_159_1.json`, `assign_result_159_2.json`), which findings were
   acted on and which were not. Re-run the parser after; quote the new verdict. If the verdict is "real text", write nothing and say so.
Rule 1/1a/U-rules untouched; nothing else in `archive/` or `docs/` is modified.
