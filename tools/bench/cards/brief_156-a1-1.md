---
card: 156-a1-1
status: current
date: 2026-10-09
---
# Brief 156-a1-1 - P5-2 PLAN RE-MADE on the REAL P5-1 graph 6716c499 per PD379 (a)-(e); OFFLINE, LabVIEW 0, NOT launched

Cycle 155's P5-2 plan (285cb59a, `tools/bench/diag_c155_a4_1_facts.md`) had three gaps. `docs/d1/ring-p5.md` PD379 decides them;
read PD379 (lines 166-206) and PD374(c)(d) (lines 42-54) first. This card re-makes the plan; it follows
`tools/bench/cards/brief_155-a4-1.md` (read it: it names the makers, the symbol map, the pred / licence / recipe / prior-art /
invariants steps) with ONLY the changes below. The 155 files `plan_ring_p5s02*`, `stage_d1_ring_p5s02*`, `prep_c155_a4_1_*` are the
cycle-155 record: do NOT overwrite them. New files use the prefixes `plan_ring_p5s02r_*` (all-groups and input plans),
`plan_ring_p5s02a*` (step 1), `prep_c156_a1_1_*`, `tools/recipes/stage_d1_ring_p5s02a.py` + `_scratch.py`.

## Changes against brief_155-a4-1.md
1. **Makers are CALLED, not copied** (`docs/script-writing.md` 1, 4, 6). Start from `prep_c155_a4_1_{mk,pred,licence,inv}.py`
   (166f6003 / 9c587c75 / 8a35a601 / fbcd6cb1). Where a block is identical to the 155 makers (gate(), step_facts, TIE loop, SG census,
   main_of), import it from the 155 module or from the shared module that has it; if no import is possible without editing a file
   outside your write globs, list the block in the facts file as `OPEN:` with file:line (do not paste a second copy more than the 155
   makers already hold, and say so).
2. **(a) GAP J-ge0 dropped.** No `>= 0` primitive, no `And`. `Equal?` (counter-after-increment vs the `records final` local) feeds
   loop 1.7's condition terminal directly. The loop's stop mode (stop-if-true / continue-if-true) is READ FROM THE GRAPH (the
   scaffold `#23042` 'x = y?' stop it replaces, and loop `#23041`'s condition terminal), quoted with file:line of the graph read;
   not assumed. If the read shows the opposite polarity, add the polarity-correct form and say so in `OPEN:`.
3. **(b) t3 / t4 shift registers** (`#376` 'file progress' t3 / 'file number to append out' t4). Per terminal: SR L.inner -> case
   in-tunnel -> pass wire in the TIMED-OUT frame -> case out-tunnel -> SR R.inner; `#376` t3 / t4 -> the same out-tunnel in the
   not-timed-out frame. The in-tunnel's ONE out-wire IS the pass wire (this is the form cycle 155 did not try; its in-tunnel had no
   group out-wire and stagexec refused it at `stagexec.py:857-859`). SR init = a constant equal to the terminal type's default value
   (read the type from the graph; the original calls `#376` at least once so the init never reaches a sink unless no valid frame
   exists). The sinks of `#6384` / `#2048` that took t3 / t4 in P5-1 must take the value that reaches R.inner (keep out-tunnels
   `#5204` / `#10404` re-fed from that net, or feed from R.outer: pick the form with an existing route). **Measurement for the
   result:** compile the t3 and t4 groups with the EXISTING routes and report per group OK, or GAP with the stagexec/stagesim
   file:line that refuses it. Do NOT edit stagexec / stagesim in this card. A GAP that blocks the first step is the card's result
   (status PASS with the GAP rows listed, if every other row compiled; BLOCKED with the census row if the GAP blocks everything).
4. **(c) Cut.** No group is split across steps. Each step <= 40 actions and planned MAIN <= 675 (NOT 680; `fail_above` set so a
   value above 675 fails). Plan the FIRST step in full; list the later cut points and each step's expected saved-file name
   (`D1_ring_p5s02a_<ts>.vi`, ... in-between, the LAST step `D1_ring_p5_<ts>.vi`). If step 1 is all of P5-2, say so.
5. **(d) sr_q R.outer t31246 (loop 1.2) stays unwired**; Release takes loop 1.7's refnum SR (R.outer -> Release on 686).
6. **(e) Prior-art A4** (`archive/peer/2026-10-09-priorart-priorart-c155-a4-1-p5s02.md`): cite it in the new review's task;
   the E1 graph == sim check on each `move_in` op of `#376` / `#3052` / `#3453` is a scratch-run item (next card), the pred lists
   those three ops as E1 checkpoints with step files.
7. Row content only from PD374/PD376/PD379 and uids read from the P5-1 graph; none retyped. A design question the PDs do not
   answer is an `OPEN:` line. Pass A + REALSIM replay: 0 PROVISIONAL for every compilable row. Dry + prerun PASS on final bytes;
   X10 (with the 675 limit), X17, X14, `--scratch-required` rc and `--check-launch` quoted. NOT launched; `tasklist` shows no LabVIEW
   before or after.
8. **Prior-art review** ANSWERED for the re-made plan (the gate's own waiver quoted if it grants one). Invariants md5 before = after
   (adopt `prep_c155_a4_1_inv.py` as the base; add the 155-a4-1 outputs and `docs/d1/ring-p5.md` 742e54c4).

## Pins (must not change)
stagexec 53e17623, stagesim eb99c6ba, stagekit aec03c6c, stage_prerun 9decb20f, vigraph a7eb58c7, addrcheck 207beb0d, gscript 1a80236e;
`docs/d1/ring-p5.md` 742e54c4; P5-1a / P5-1 files; stored P4 and cycle-155 plans / recipes / preds; no `tools/hooks/**` edit; no
stage-tool edit. Rule 1a: `#376` is MOVED, not changed; no per-bead computation, `#2626`, loop 1.1 or the ring touched.

## Report `tools/bench/diag_c156_a1_1_facts.md` (<= 45 lines)
Plan / pred / licence / recipe md5s; the action list with real uids; per-group route census (OK / GAP + reason, t3 and t4 groups
explicit); stop-mode read (quote); the t3/t4 sink sim result (#6384/#2048 sink -> R.inner net); cut and X10 numbers; dry / prerun /
rc / check-launch quotes; prior-art outcome; invariants; OPEN lines. Facts only.
