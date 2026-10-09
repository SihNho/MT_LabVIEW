---
card: 156-a2-2
status: current
date: 2026-10-09
---
# Brief 156-a2-2 - RETRY of 156-a2-1: the same ONE P5-2 step-1 scratch + adopt; the launch gate's PASS-UNVERIFIED naming is now in the card

`tools/bench/cards/brief_156-a2-1.md` is the brief, unchanged: read it first, and `tools/bench/diag_c156_a2_1_facts.md` (the pre-checks
that card already ran: dry 1/0 PASS-UNVERIFIED PB, prerun 16/0 X10 672.1 / Executor 667.0, `--scratch-required` rc 3; no LabVIEW was started,
no byte copy exists). Card 156-a2-1 returned BLOCKED at the launch: `stage_prerun.py:4888-4895` (card 134-1 PD287(a)) refuses a scratch whose
newest dry is PASS-UNVERIFIED unless the bound card names each unverified gate and the command carries `--unverified-card`. The unverified
gate is PB (`PB frame-keyed cdiff(S1, real end) by POSITION ...`): a dry runs on a stub input, so PB can only be evaluated on real data, and
the scratch run itself evaluates it. The brief expected this (brief_156-a2-1.md:16).

## What changes
1. This card's `rules` carries `DRY-UNVERIFIED-OK: PB frame-keyed cdiff`. The scratch launch command carries
   `--unverified-card tools/bench/cards/task_156-a2-2.json` (the `bgrun ... -- py -u tools/recipes/stage_d1_ring_p5s02a_scratch.py` line,
   flag placed per `stage_prerun.py:3339` UNVERIFIED_CARD_RE and the recipe's own argument handling; if the recipe does not accept it,
   put it where `check_launch` reads the command text and say where). Quote the gate's ALLOW line for the full launch command text before
   launching (the bare CLI `--check-launch <path>` is vacuous: `stage_prerun.py:4821-4824` - check the whole command).
2. Everything else is brief_156-a2-1 item for item: the pre-checks re-quoted (no re-run needed unless a md5 or record moved; re-run dry +
   prerun if the gate says stale), ONE scratch, E1 for the three move_in ops, adopt by import, final Error List, graph read, `load_by_vi`,
   invariants, LabVIEW gone. PB must PASS on the real data in the scratch run; a PB failure there is the RETURN condition of the brief.
3. The previous card's helper `diag_c156_a2_1_inv.py` (ab4ff13c) is the inv helper: reuse it by import / call (fp: it is the 4th per-card
   copy of the 155/154 helper; the extraction to a shared module is an `OPEN:` line, not in this card's scope).
4. The gate refusal of fp-76 is already logged in `tools/bench/gate_fp_queue.jsonl`; do not log it again. If the gate refuses the corrected
   command for a NEW reason, log it with `py tools/gate_fp.py log`, no env bypass, RETURN with the text.

## Report `tools/bench/diag_c156_a2_2_facts.md` (<= 45 lines)
As brief_156-a2-1's report list, plus the quoted ALLOW line for the full launch command. Facts only. `OPEN:` line.
