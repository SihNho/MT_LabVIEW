---
card: 147-c3-3
status: current
date: 2026-10-08
---
# Brief 147-c3-3 - P4 session 6 SCRATCH #2 (new gate API) + adopt (docs/d1/ring-p4c.md PD357(f), ring-p4b.md PD356(e), PD354(a))

Everything in `tools/bench/cards/brief_147-a1-8.md` (and through it `brief_147-a1-4.md`: steps 2-6, Never, Return) applies, with these deltas. This is the PD356(e) retry: `retry_of` = `stage_d1_ring_p4_s06v18_scratch.py`, `retry_of_card` = 147-a1-8; carry it as `RETRY_CARD=tools/bench/cards/task_147-c3-3.json` in the launch command (one card = one run; the RETRY_CAP of 2 per cycle is already used up by 147-a1-4 and 147-a1-8, this card is the judged third).

## Re-issue (assignment round 3, after attempt 1 BLOCKED by fp-59)
Attempt 1 measured: guard_cycle owes a DIFF-ONLY prior-art review (78 lines vs `stage_d1_ring_p4_s03v18_scratch.py`) and `prior_art_review.py` was refused because the card lacked `priorart` in `flags.peers`. This card now carries `peers: [hypothesis, priorart]`. Step 1: run `prior_art_review.py` once for the scratch recipe (diff-only, as the gate asks); it is a real review, not a formality - launch only on `novel` or a valid FIXED/REFUTED release written into the review file per CLAUDE.md section 5. Pre-checks, dry and prerun already PASS (`diag_c147_c3_3_check.log` 25/0, scratch dry 1/0, prerun 16/0): do not repeat them unless a pinned md5 changed. fp-59 stays queued; no env bypass. If the review says anything other than `novel` and no release applies: RETURN with the verdict, do not launch.

## Deltas against brief 147-a1-8
1. **Recipe bytes now** (offline-verified by card 147-c3-2, facts `tools/bench/diag_c147_c3_2_facts.md`; dry + prerun 16/0 both): build `stage_d1_ring_p4_s06v18.py` **d947df5d** (calls the stagekit 06b8d844 gate API: licence `renames` + executor `bind`, PB via `pb_rename_rows`, `unlicensed == []`), scratch `_scratch.py` **31009bfc** unchanged, licence **7f70bbf9** (5 `renames` + `rename_by_uid`). stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, plan cfbd9823, pred c4a6a35a, in db72d8af, memory_model 88eeb037, stage_prerun 61d6f590 as before.
2. **Rerun from the start on a NEW byte copy** of `claudeDev\D1_ring_p4s05_20261008_002621.vi` (3f9ac26b), ops 1..21. Neither the stopped copies b58046e3 nor the previous retry's saved file is resumed or adopted. Do not delete them in this card.
3. **Pass for the scratch (PD356(e)):** SG sink gate PASS with its readback; E1 real == sim at every op; D, TD, PB and every other structural gate PASS (the D/TD/PB renames of #2626 2832/4160/4165 and #9503 9505/9508 are licensed and printed; a reused deleted wire uid is REUSE-NOTED only if the gate says so); peak <= 680, MEMSTOP 695 not hit. A stop or a gate difference = RETURN with facts, no further retry.
4. **Adopt by PD354(a)** (`adopt_scratch` by import; the CLI form is refused): `D1_ring_p4s06_<stamp>.vi`, FULL final Error List = expected file, per-class EL-ADVISORY diff explained (pred 55), fresh-instance load + graph read JSON, md5 recorded. Then ONE `load_by_vi` entry keyed by the adopted md5 with the measured load; X10 and MEMSTOP limits and every other memory_model field unchanged (key-by-key diff).
5. **Prior art / review gates:** the pattern is PROVEN (s04, s05 same shape; `PROVEN-PATTERN`). Card 147-c3-2 reports guard_cycle may still ask a DIFF-ONLY prior-art review against `stage_d1_ring_p4_s03v18.py` for the changed lines: if the launch gate asks, run it once (`prior_art_review.py`; you may write archive/peer) and launch only on `novel` or a valid FIXED/REFUTED release; a false refusal goes to `tools/gate_fp.py`, never an env bypass.
6. `tools/bench/selftest_c147_b1_2.py` P0 (pins licence 7dce79aa + recipe 9150f15b) is now stale by design: do NOT edit it (no tool edit beside a LabVIEW card); list it under `OPEN:`.
7. LabVIEW closed and verified gone at the end (`tasklist`). Handles flat. Invariants: s05 3f9ac26b, s04 95e408ff, s03 282301ca, bed 39511877 byte-identical.
