# Brief for card 110-1 (cycle 110 judgement) — decisions already taken, not yours to change

## D. Decided design for L2-B (docs/d1-loop12-17-split-plan.md PD223(b), PD163/164/166/175/182(c))
1. Destination: body `#23166` of WhileLoop `#10170` (= loop 1.2, PD163).
2. All 8 group-B nodes (`#1359 #2222 #2626 #6104 #8885 #9833 #11261 #29874`) and the 4 control terminals
   (`Z/dZ` #47, `Correction Factor` #9289, `Force smoothing` #28148, `Extension median` #28996) go to 1.2.
   Interior objects of the structures (e.g. `Exp Baseline` #8476) move with their structure.
3. The 2 group-B-only shift-register pairs on `#637` (`#9018/#9025` ring, `#29505/#29512`) are RE-CREATED on
   `#10170`, each new LEFT fed from the same source as in S1 (PD164 pattern, RULE-CHAIN-S1). The old pairs stay on
   `#637` until L2-R.
4. Pre-loop inputs (SR inits `#8953`/`#28124`, `#27605`, `#5426`, `#5556`) enter 1.2 by NEW input tunnels on `#10170`
   off the same outer feed (PD166 rule rows).
5. Per-frame DATA crossings from 1.1 (facts T3: `#10068`, `#30117`, `#5119`, `#4580`, `#11608`, `#29240`) and the
   out-crossing `#2626 -> #376` (w4517) are OPEN rows owed to QRT — never made in B1..B3 (PD182(c), PD175).
   If you find a crossing that is a control/trigger signal (CLAUDE.md 1c''), REPORT it as an OPEN; do not make it.

## B. B1 content and order
B1 = the moves (D2) + the SR pairs (D3) + re-wire batch 1, ≤ 13 rows, in this order: B-internal rows cut by the
moves → `#5058 'x,y,z array out'` → `#2222`/`#2626` (w505, both ends in 1.2) → SR re-feeds → pre-loop tunnels.
Rows that do not fit go to B2/B3 (≤ 13 each); list them on the split page.

## M. Measurement asked (not an action)
- The Property Value nodes `#30117` / `#4580`: target control uid + label, read on a SCRATCH copy of the bed.
- The X10 memory-margin prediction for B1 (pre-run). If X10 fails, return BLOCKED with the numbers — do not re-cut.

## G. The owed launch-gate device (docs/violation-decisions.md:1541-1556)
`stage_prerun.launched_py`: `py -m <module> …` launches the module; later paths are arguments. `guard_bash`
`prerun_gate` strips lint segments like the stop_record path. Self-test the 3 cases at `:1552-1554`; the existing
stage_prerun / guard_bash self-tests must show 0 regressions.
