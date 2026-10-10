---
card: 158-a3-2b
status: current
date: 2026-10-10
---
# Brief 158-a3-2b (assignment 158-3) - re-issue of 158-a3-2 with the prior-art peer allowed

Card 158-a3-2 stopped BLOCKED before any LabVIEW use: the edited scratch recipe (64b4f18b) owes a prior-art review (guard_cycle) and the card's `peers`
lacked `priorart`. This card is the SAME work with `peers` = hypothesis + priorart. Read `tools/bench/cards/brief_158-a3-2.md` (all of it, it is the
brief) and `tools/bench/diag_c158_a3_2_facts.md` (the pre-checks 158-a3-2 already ran: dry, prerun, check_launch ALLOW, invariants before; re-run them
on unchanged bytes if cheap, they are not edits).

## Delta
0. **FIRST ACT: the prior-art review of the edited scratch recipe.** The plan text is ready: `tools/bench/diag_c158_a3_2_priorart_plan.md`. Dispatch
   `prior_art_review.py` once (slug `c158-a3-2-p5s02a-retry`) the way earlier cycles did (`archive/peer/2026-10-09-priorart-priorart-c156-a1-1-p5s02a.md`
   shows the form). Verdict `novel` = continue. Any other verdict stops the launch: act on it only through the two releases in CLAUDE.md section 5
   (`REFUTED:` with a file:line citation, or `FIXED:`), otherwise RETURN with the verdict. The recipe is NOT to be edited again in this card.
1. Everything else exactly as brief_158-a3-2 items 1-8 (one scratch, no second run on a BLOCK FAIL, adopt, delete the failed copy only after adoption,
   step-2 plan offline with its own dry + prerun + prior-art, not launched). The step-2 plan's prior-art review is the same dispatch kind; a PROVEN
   pattern is exempt (quote `PROVEN-PATTERN` if the log says so).
2. Facts go to `tools/bench/diag_c158_a3_2b_facts.md` (<= 45 lines); helper scripts `diag_c158_a3_2b_*` (or reuse the `diag_c158_a3_2_*` ones by call).
