---
card: 148-a2-4
status: current
date: 2026-10-08
---
# Brief 148-a2-4 - P4 session 6 SCRATCH + adopt (docs/d1/ring-p4c.md PD358(e), PD354(a)); the first real launch with the new gate API

Everything in `tools/bench/cards/brief_147-c3-3.md` applies (and through it `brief_147-a1-8.md` and `brief_147-a1-4.md`: steps 2-6, Never, Return), with these deltas. `retry_of` = `stage_d1_ring_p4_s06v18_scratch.py`, `retry_of_card` = 147-c3-3 (that card was BLOCKED before any launch, so no LabVIEW run has yet used licence 7f70bbf9 / recipe d947df5d). If `stage_prerun` asks for a retry card, carry `RETRY_CARD=tools/bench/cards/task_148-a2-4.json` in the launch command.

## Deltas
1. **Prior art is DONE**: `archive/peer/2026-10-08-priorart-c148-s06-scratch.md` (md5 4e66245f, ANSWERED, `PRIOR-ART: novel`, card 148-a2-2). Do NOT run `prior_art_review.py` again. If the launch gate still refuses on prior art, that is a gate false positive: queue it through `tools/gate_fp.py`, no env bypass, and RETURN with the refusal text.
2. **fp-60 is fixed** (card 148-a2-1, `guard_assign.py` md5 bbaa2325, self-tests drop the env). Do not edit any tool/hook/self-test (no tool edit beside a LabVIEW card).
3. **stage_prerun.py is now dcd45aba** (cycle-148 edits, 148-a1-1), not 61d6f590 as 147-c3-3 pinned. The dry + prerun for the scratch recipe MUST be re-run once before the launch (`--dry`, `--prerun`; quote counts and X10). A difference from 147-c3-3's 1/0 and 16/0, or X10 674.2, is a RETURN with the facts, not a fix.
4. **Concurrent card**: an OFFLINE s07 prep card (labview none) may run beside you; it reads the s06 plan files provisionally. It never touches the claudeDev directory, `memory_model.json`, `adopted_scratch.jsonl`, `tools/bench/sim/ring_p4_s06v18/**` or your `diag_c148_a2_4*` files.
5. Pass, adopt, `load_by_vi`, handles, LabVIEW-gone: exactly brief 147-c3-3 deltas 2-4 and 7. ONE scratch; RETURN at the first result differing from the prediction; no second launch inside this card. The adopted file is the only thing the s07 rebase will read: finish with its path, md5, graph json path+md5, and final EL path in the facts file.
6. `selftest_c147_b1_2.py` is already re-pinned (17/0); leave it.

## Report (`tools/bench/diag_c148_a2_4_facts.md`, <= 45 lines)
Pre-launch dry/prerun counts and X10; gate outcomes per op class (SG with readback, E1 real == sim, prim, D/TD/PB, licence, peak MB); adopted file + md5 + load MB; EL diff per class; `load_by_vi` key-by-key diff; invariants (s05 3f9ac26b, s04 95e408ff, s03 282301ca, bed 39511877, stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c); handle counts; `tasklist` LabVIEW count 0 after. `OPEN:` line. Facts only.
