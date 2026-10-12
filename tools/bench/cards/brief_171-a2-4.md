---
card: 171-a2-4
status: current
date: 2026-10-13
---
# Brief 171-a2-4 (assignment 171-2) - re-issue of 171-a2-3 (BLOCKED, not failed): prior-art review of the patch, drain fp-103, queue c130_5 T3

Do exactly `tools/bench/cards/brief_171-a2-3.md` (steps 1-2 and its hygiene), with these changes:
- Why it is re-issued: 171-a2-3 returned BLOCKED because guard_peer refused the prior-art review while `archive/peer/2026-10-13-priorart-c170-paced60.md` had an empty "What was done with it".
  That paragraph is now written (by the assignment session); the c170 review is disposed. Its facts: `tools/bench/diag_c171_a2_3_facts.md`.
- Facts file is `tools/bench/diag_c171_a2_4_facts.md` (not a2_3). Result file `tools/bench/cards/result_171-a2-4.json`.
- Do NOT edit the c170 review file again. If guard_peer refuses for another reason, return BLOCKED with the exact message and do not look for a way round it.
- fp-105 (logged by 171-a2-3) and fp-104 are hook gates: untouched. fp-102 untouched.
- Disposition of the NEW review (`archive/peer/2026-10-13-priorart-c171-taint.md`): fill "What was done with it" yourself, factually, so the next review is not blocked either.
- stage_prerun.py stays af6937e8 (byte-identical).
