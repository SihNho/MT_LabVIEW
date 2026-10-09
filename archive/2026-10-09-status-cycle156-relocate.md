---
type: archive
date: 2026-10-09
source: STATUS.md ## NEXT, line 64 before cycle 156
---
# STATUS relocation, cycle 156 judgement (rule 4, verbatim)

## §1 Cycle 155 purpose line

🟢🟢 **CYCLE 155 PURPOSE (judgement 2026-10-09; `tools/bench/next.json`; `docs/d1/ring-p5.md` PD378):** cycle 154 built and ADOPTED P5-1a = `claudeDev\D1_ring_p5s01a_20261009_101219.vi` md5 2482fe7b. The scratch passed 23/0. Error List 47 (the predicted 48 was one too high because elrule over-counts an optional unwired Obtain input; this does not gate). Graph `tools/bench/graph_ring_p5s01a_20261009_103621.json` bd67a511, load 602.6 MB. It is an in-between file, so it does not count toward the 6 broken files. The bed stays s09. The P5-1b plan (actions 21..32) was refused at compile: its two False-frame pass-through wires name frames of Case #30726, and the stage tools give frame names only to a case made in the same plan (`stagexec.py:613-615`, `stagesim.py:797-800`, `tools/bench/diag_c154_a4_1_facts.md`). **Decision: a narrow tool fix**, because P5-2 and every later track will also edit cases that already exist in the file. With the fix, a case in the real base graph is addressed by its measured frame uid, `#<uid>`, and uses the R1/R2 / case_frame_wire routes. Only `stagexec.py` and `stagesim.py` change. They get a new self-test, and P5-1a's plan must recompile to the same ops. **First act = that tool card (it goes first only because the P5-1b plan cannot compile without it) → P5-1b plan (frame wires on `#30914`) + prior-art review → ONE scratch on a byte copy of P5-1a → adopt `D1_ring_p5s01_*.vi` → P5-2 plan on the real P5-1 graph (not launched).** Then fp-73. Hook entries fp-74 and fp-75 are left for the chat.
