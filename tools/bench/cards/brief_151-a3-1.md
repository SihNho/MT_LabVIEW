---
card: 151-a3-1
status: current
date: 2026-10-09
---
# Brief 151-a3-1 - RE-ISSUE of card 151-a1-1 (P4 session 8 SCRATCH + adopt) with the stale pin corrected (PD367(h)); the ONE LabVIEW card of this round

Card 151-a1-1 (`retry_of_card`) stopped before any LabVIEW work: its brief step 8 pinned stagekit 06b8d844 (pre chat-T6 merge 9dbd384b); the file is 604529e8.
The whole of `tools/bench/cards/brief_151-a1-1.md` applies UNCHANGED (read it, and through it brief_150-a3-2 / 148-a2-4 / 147-c3-3 / 149-a3-1 / 147-a1-8 / 147-a1-4),
with exactly these deltas. That brief file is NOT edited (the old card and `diag_c151_a1_1_inv.py` pin its md5).

## Deltas over brief_151-a1-1.md
1. **Step 8 invariants, re-pinned:** stagekit **604529e8** (not 06b8d844), plus **addrcheck 207beb0d** (`tools/addrcheck.py`) before = after. Every other pin in step 8 stands
   (stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun c739eb86, vigraph 13be0847, stagesim 748bbf30, s07 b3f86b32, s06 569ffbf5, bed 39511877, graph 71935a84,
   s08 plan/pred/licence/recipes). `tools/bench/diag_c151_a1_1_inv.py` already carries the stagekit 604529e8 pin (line 24; md5 ffbc0579) and reads the OLD card
   `task_151-a1-1.json` for its input pins: run it as is (`before` / `after`) with its existing log names. Add the addrcheck 207beb0d check to your facts (one md5 line before and after; do not edit the inv script).
2. **Concerning the stale pin only:** any other measured md5 that differs from a pin is still a RETURN with the facts; do not re-pin anything else yourself.
3. **Output names:** keep the `diag_c151_a1_1_*` file names named in brief_151-a1-1.md (facts, adopt, elexp, mkgraph, graph copies) so the already-prepared inv script and write globs match; the facts file is `tools/bench/diag_c151_a1_1_facts.md`.
4. **Prior review** `archive/peer/2026-10-09-c151-a1-1-stalepin.md` (the review of the stale pin) is disposed by PD367(h); nothing further owed from it. No new peer unless a gate FAILS in the launch (failed-prediction rule).
5. Everything else - one scratch, RETURN at the first result differing from the prediction, adopt by import, EL expected file, fresh load + graph with FS #29721 frame/border rows, ONE `load_by_vi` entry, LabVIEW closed and VERIFIED gone - exactly as in brief_151-a1-1.md.
