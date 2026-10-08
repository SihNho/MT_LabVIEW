ATTACK this claim about the failed prediction in tools/bench/diag_c151_a1_1_inv_before.log (script tools/bench/diag_c151_a1_1_inv.py, card 151-a1-1).

Observation: the before-invariant gate `md5 stagekit.py == 06b8d844` FAILED; measured 604529e8e9b68b9c4b370b8f3d5c5ee5. All 33 other pins passed
(stagexec 1bab9cf9, gscript, elrule, stage_prerun c739eb86, vigraph, stagesim, s07/s06/bed VIs, every card input incl. the s08 recipes ca5a5478 / 7cab5049).

Claim: the failure is a STALE PIN, not a corrupted or unexpected tool. The pin 06b8d844 was copied into tools/bench/cards/brief_151-a1-1.md step 8
from brief_150-a3-2.md; card chat-T6 (commit 771a39a1, merged 9dbd384b 2026-10-09 02:42) then rewrote tools/stagekit.py (git diff 07202624..HEAD:
273 lines; term_identity_356 / wire_keys_356 / rename_check removed, term_identity_pos / wire_ends_pos added: result gates D / TD / PB keyed by
terminal POSITION instead of name). `git status` shows stagekit.py clean, i.e. 604529e8 == HEAD. Consequence: the s08 scratch
(tools/recipes/stage_d1_ring_p4_s08v18_scratch.py, which imports tools/recipes/stage_d1_ring_p4_s08v18.py:161,175 calling
K.term_identity_gates and K.pb_rename_rows) would be the FIRST LabVIEW scratch whose D/TD/PB gates run on the post-T6 code; the offline prep
of 150-a3-6 (prerun 16/0, `tools/bench/diag_c150_a3_6_facts.md`) ran before the merge.

Questions: what is the strongest reason this claim is wrong (e.g. a different, unintended edit inside the 604529e8 bytes; the merge result
differing from the T6 worktree that was tested, cf. tools/bench/cards/result_chat-T6v.json)? What would falsify it, and what is the cheapest
offline discriminating test before any LabVIEW launch (e.g. `git diff 771a39a1 9dbd384b -- tools/stagekit.py`, the scratch recipe's --dry and
--prerun on the current bytes)? Is there any reason the s08 D/TD/PB verdicts on post-T6 code are not comparable with s07's?
