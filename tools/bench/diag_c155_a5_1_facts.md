---
card: 155-a5-1
status: current
date: 2026-10-09
---
# 155-a5-1 facts - fp-73 fix tried, RETURNED FAIL at step 4 (a self-test count got worse); stage_prerun.py reverted

1. Preferred form measured UNSAFE as-is: census before (`prep_c155_a5_1_census_before.log`) = 2057 files, 192 VI-modifying,
   160 call discard_work, **67 discard-only** - incl. the real ring stages `tools/recipes/stage_d1_ring_p5s01b.py`,
   `stage_d1_ring_p5s02.py`, `stage_template_ring.py` (their edits go through `RingSession.executor/run`, tools/stagekit.py:1968/1989).
2. Candidate tried (tools/stage_prerun.py:3137-3184): MODIFY_VERBS += "executor"; new `NON_MODIFYING_ALONE = {"discard_work"}`;
   `vi_modifying_calls` returns [] when `calls <= NON_MODIFYING_ALONE`. `executor(` is called only by those 3 recipes (grep).
3. Census after (`prep_c155_a5_1_census_after.log`): 128 modifying, discard-only 0. Class changed for exactly the 64 non-ring
   discard-only files; the 3 ring recipes stay True (verb list gains "executor" - my diff script flagged that as OTHER-CHANGE,
   `prep_c155_a5_1_census_diff.log`, a list change not a class change). No file became newly classified.
4. New self-test `selftest_c155_gatefp73.py` on the candidate: 10/0 (`selftest_c155_gatefp73.log`).
5. Existing self-tests, clean before (9decb20f) -> after (candidate):
   c103d_hooks 17/0 -> 17/0 · c121_3_gatefp 30/0 -> 30/0 · prerun_diag 9/0 -> 9/0 ·
   fn_f2 35/1 (P7b doc drift, PRE-EXISTING) -> 36/0 · **guard_bash_jev 12/0 -> 11/1 (WORSE)**.
6. The worse gate: `selftest_guard_bash_jev.py:92,223-229` C11 uses `tools/bench/diag_c88_brokenwires.py` as "the old
   VI-modifying fixture" and asserts its launch is still refused (code 2); with the candidate it is allowed (code 0).
   That file's only MODIFY_VERBS hit is discard_work, but it edits a SCRATCH copy through gscript directly:
   `g.remove_bad_wires_scripted(` at diag_c88_brokenwires.py:92 (on `s.scratch(` :90).
7. Declassified set also holds other gscript-direct scratch editors, e.g. diag_c89_wirebirth.py:77/82 (`g.connect_terminals`,
   `g.connect_ctl`). The fp-73 diag itself (`diag_c153_a2_2_queue_hygiene.py`) no longer imports stagekit (False before and after).
8. Per the brief's return rule the candidate was REVERTED by Edit: tools/stage_prerun.py md5 = 9decb20f (unchanged), so no
   pin went stale. Pins verified unchanged: stagexec 53e17623, stagesim eb99c6ba, stagekit aec03c6c, vigraph a7eb58c7,
   addrcheck 207beb0d, gscript 1a80236e. Pre-existing stale pins (guard_write): open cards 149-a3-4 (dcd45aba), 150-a2-6 (c739eb86).
9. Not done (stopped at the first worse count): step 5 s02/s01b re-check (stage_prerun bytes unchanged, so 155-a4-1/155-a3-1
   results stand), step 6 fp-73 drain (left open).

OPEN: is a discard-only script that edits a scratch copy through gscript directly (diag_c88_brokenwires:92) meant to be
gated? If no -> re-run this candidate with C11 re-pointed to a fixture that calls a real MODIFY_VERB (selftest edit, outside
this card's write flags); if yes -> fp-73 needs a narrower rule (the hygiene diag also imports gscript, :21, so "no gscript
import" would not separate them), or fp-73 is closed as moot (the diag no longer imports stagekit).
