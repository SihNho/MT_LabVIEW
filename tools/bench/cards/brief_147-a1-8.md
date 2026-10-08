---
type: brief
status: current
date: 2026-10-08
---
# Brief 147-a1-8 - P4 session 6 RETRY scratch + adopt (docs/d1/ring-p4b.md PD355(d)(e), PD354(a))

Everything in `tools/bench/cards/brief_147-a1-4.md` applies (steps 2-6, Never, Return) with the deltas below. This is the PD355(d) retry: the judgement card is this one,
`retry_of` = `stage_d1_ring_p4_s06v18_scratch.py`; carry it as `RETRY_CARD=tools/bench/cards/task_147-a1-8.json` in the launch command (one card = one run).

## Deltas against brief 147-a1-4
1. **Recipe bytes now** (offline-verified by card 147-a1-7, prerun 16/0 both, facts `tools/bench/diag_c147_a2_1_facts.md`): build `stage_d1_ring_p4_s06v18.py` **9150f15b**,
   scratch `_scratch.py` **31009bfc**. The s06 build recipe declares ONE sink gate `[23166,'Pos within cal image']` (sink derived from the plan row, no typed uid); its gate reads
   back after op 21 that the indicator is on the net of #5058 'pos in cal image out' with one source, else ExecStop. Plan/pred/in/licence/memory_model/stagexec/gscript md5 as
   in brief 147-a1-4 (stagexec 1bab9cf9, gscript 1a80236e, stage_prerun 61d6f590).
2. **Rerun, not resume (PD355(d)):** a NEW byte copy of `claudeDev\D1_ring_p4s05_20261008_002621.vi` (3f9ac26b), ops 1..21 from the start. The earlier stopped work copy
   `D1_ring_p4s06_20261008_020717.vi` (b58046e3) is NOT resumed and NOT adopted; do not delete it in this card.
3. **Pass for the scratch:** E1 real == sim at EVERY op including op 21; the sink gate PASS with its readback (three readings) printed in the log; every other structural gate
   PASS (prim, D/TD, PB, licence, peak <= 680, MEMSTOP 695 not hit). A stop at any op other than the gate-covered sink = RETURN; no further retry.
4. **Adopt by PD354(a)** as in brief 147-a1-4 step 4; Error List recorded per class, advisory. Then ONE `load_by_vi` entry keyed by the adopted md5 (step 5); X10 and MEMSTOP
   limits and every other memory_model field unchanged (key-by-key diff).
5. The `RETRY_CAP` gate and any prior-art / review gate: pattern is PROVEN (s04, s05 passed the same shape) -> `PROVEN-PATTERN`; a false refusal goes to `tools/gate_fp.py`,
   never an env bypass.
6. If a measured fact contradicts a prediction, RETURN with facts (LabVIEW closed, files saved); do not diagnose-and-retry. LabVIEW verified gone at the end (`tasklist`).
