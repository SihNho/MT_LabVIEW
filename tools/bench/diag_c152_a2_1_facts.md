---
type: facts
status: current
date: 2026-10-09
card: 152-a2-1
---
# Card 152-a2-1 facts: stagesim takes fs_owner_read (PD368(c)); FS #29721 resolved to Diagram #23166 on the derived graph; OFFLINE
- Edit: `tools/stagesim.py` `fs_measured_state` only (after `fs_parent`, +46/-2 lines); md5 748bbf30 -> **c24bd39aaca3801d232c54ae2c10d520**. Valid read = class exactly `Diagram`, uid != 0, cite echo `["FlatSequence", fs]`; no faces -> fs_parent; faces must be ONE outer diagram == read; anything else -> pop from fs_parent (UNMEASURED). Returns an extra `fs_owner_read` status dict ONLY when the key is present. `_diag_chain` / `base_state` untouched.
- Identity (graphs without the key): `diag_c152_a2_1_ident_after.log` 4/0 - fs_measured_state + base_state byte-identical to the before-dump for 44858dbf and 71935a84 (`_ident_before.log`, md5s 54b9e804 / 72d8241e / 281611f6).
- New `selftest_c152_fsowner.py` 15/0 (`selftest_c152_fsowner.log`): R1 derived 29721 -> ['Diagram', 23166], fs_unmeasured [2499, 14682, 43914]; R2 faced FS #681 read != faces #536 -> UNMEASURED; R3 TopLevelDiagram / R4 uid 0 / R5a-d echo missing, uid 29722, class Diagram, no cite -> UNMEASURED; R6 agreeing read resolved; R7 derived minus keys == original == before-dump; R8 original [2499, 14682, 29721, 43914]; R11 non-FS uid IGNORED; R12 faced FS #681 + TopLevelDiagram read -> UNMEASURED (literal rule).
- `_diag_chain` from frame #29869: derived = [29869, 23166, 686, 536] (R9); original graph raises "frame #29869 belongs to FS #29721 whose diagram is UNMEASURED" (R10).
## Baseline vs after (same counts)
| test | before | after |
|---|---|---|
| selftest_c134_4_owners | 7/0 (`_base_owners.log:11`) | 7/0 (`_after_owners.log`) |
| selftest_c134_1_fsmap | 6/0 | 6/0 |
| selftest_c134_2_gates | 11/0 | 11/0 |
| selftest_c134_1_dry | NOT RUN: card labview none, header `labview: read` (refused; gate-fp **fp-71** logged) | NOT RUN |
| selftest_c134_2_regress (as is) | killed at my 5-min cap after 11/17 children, 9 PASS / 2 FAIL (`_base_regress.log:3-17`); it launched the read-header children c134_1_dry (10/1, T2a recipe md5 0d1f0c15 != bb5ba064) and c128 itself | not re-run (it launches read-header children) |
| copy `diag_c152_a2_1_regress.py` (skips non-none headers: dry, c128, graphload, c125_1) | 11/2 (`_regress_before.log`) | 11/2, child by child identical (`_regress_after.log`); stagesim selftest 105/0 both |
- The 2 regress FAILs are pre-existing and unchanged: selftest_c133_6_fr `KeyError: 'fs_frames'`; selftest_stage_prerun_c106e 14/1 "E1 Part-B prerun, no meter record".
## Inventory: `diag_c152_a2_1_inv_before.log` 24/0, `_inv_after.log` 24/0 - only stagesim.py differs (stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun c739eb86, vigraph 13be0847, s08 f99e8414, graph 44858dbf, derived e26b4d90, s07 71935a84, all card inputs unchanged; no scratch). No LabVIEW, no hooks edit.
OPEN: PD368(c) literal: a FACED FS whose read is not exactly 'Diagram' becomes UNMEASURED (R12; a1-1's control FS #681 read 'TopLevelDiagram' #536) - keep, or accept TopLevelDiagram for the top-level uid? The 20-read OpOwnerChain_v1 hygiene run owed by the a1-1 review is still not done.
