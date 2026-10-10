---
card: 158-a3-1
status: current
date: 2026-10-10
---
# Brief 158-a3-1 (assignment 158-3) - OFFLINE: PD386(a)(b)(c)(d) gate change for a move into a stage-created case, pred census, scratch log name, mutation re-score

No LabVIEW, no hook edit, no plan / licence / P5-file edit, no original opened. Read first: `CLAUDE.md` rule 1a, `docs/script-writing.md`
(calls, no pasted copies; a docstring names its self-test), `docs/d1/ring-p5.md` item 386 (all of it, lines ~313-350) and 384/385 only where 386
cites them, then `tools/bench/diag_c158_a2_3_facts.md` (the offline recount of the failed scratch: it is the measurement behind every
decision below) and `diag_c158_a2_3_measure.py` (it already calls D / TD / PB / cdiff by CALL on the real and the sim end - reuse its calls).
Rule 1a: only how the gates JUDGE a result changes; no VI content, no computation, no op of the plan.

Base pins (task inputs): stagekit 0d8f6d25, stagexec 7a712ccb, stagesim eb99c6ba, vigraph a7eb58c7, stage_prerun 9decb20f, addrcheck 207beb0d,
gscript 1a80236e; plan 4284c22a (unchanged), pred 31d8e9be, licence e8fd6a98, recipes b52b9ff5 / 71c3aed4, table 2d9fd051, graph 6716c499.
`stage_prerun.py`, `addrcheck.py`, `gscript.py`, `tools/hooks/**`, the plan, the licence: read-only for this card.

## What to change (the four failed gates of scratch 158-a2-2; real == sim topology was shown, the gates judged convention)
**(a) PB, a move into a case CREATED by this stage** (`stagekit.pb_check` at stagekit.py:1806 and the frame tag code it uses, vigraph.py:287-291,
:322, :812-836). Contract (386(a)): the frame tag `@<tunnel>/f<k>` is compared by the BOUND frame uid, never by the ordinal (the ordinal ranks by
uid, so negative simulated uids reverse it: f1/f0 flip, facts :16). Real PB == sim-end PB re-keyed with the run's bindings (frame-keyed); ANY
difference BLOCKS. A PB(S1, real) row whose only difference from S1 is the tag is RECORDED (not blocking) iff (i) its source terminal uid equals
S1's and (ii) the tunnel's bound frame is the PLAN's frame for that move; every other extra / missing row BLOCKS. Same rule for every later step
that moves a source into a case it created. Where the bindings come from: the run's `bound {...}` line (scratch log format, facts :10) - find the
existing carrier in stagexec/stagekit and CALL it.
**(b) D and TD pair-keyed** (`stagekit.term_identity_gates` stagekit.py:1376 with `wire_ends_pos` :1439): (source, sink) pairs by position
(owner, index, class), simulated owners mapped through the bindings. New and lost pairs real == sim, else BLOCK. A wire with NO sink (a source-only
stub) is dropped on BOTH sides and RECORDED with its wire uid / source - wire 24091 is the known case (sim keeps the stub, LabVIEW deletes it). The
simulator's stub keeping is logged as a model gap in the facts file (FINDING; no simulator edit in this card).
**(c) CEN2.** `plan_ring_p5s02a_pred.json`: `census_overall` becomes `MEASURED-SCRATCH` = the 158-a2-2 run's census (`diag_c156_p5s02a_scratch.log:553-555`:
InnerTerminal 10, Wire 12, OuterTerminal 6, Diagram 2, CaseStructure 1, Tunnel 1 in the pred's classes, all classes :554-555), following the
precedent `tools/bench/diag_c148_a2_4_census.py:52`. The retry's census must EQUAL it, else BLOCK. Read `census_gate`/`gate_cen2`
(stagekit.py:307, :2028) and say in the facts file how an EMPTY declared set vs `MEASURED-SCRATCH` is read (facts :35). The scratch recipe also
prints a per-op CLASS census line for ops 16 and 17 (the PD385(b) measurement owed) - add it to the recipe's printing only (no act change).
**(d) Scratch log name.** `tools/recipes/stage_d1_ring_p5s02a_scratch.py` writes to its OWN log `tools/bench/diag_c158_p5s02a_scratch.log` (the
fixed c156 LOG constant made METER read the whole file); the second run of the stage this cycle is a `retry_of` card - read how RETRY_CARD is
carried in the recipe and in `docs/d1/ring-p5.md:343-346` and make the recipe accept it as written. Edit names/constants/printing only.

## Measure, in this order (FACTS)
1. BEFORE any edit: store the op lists of every stored plan and the suite counts (reuse `tools/bench/prep_c158_a2_1_regress.py` by CALL, new
   prefix `prep_c158_a3_1_*`; record the two known failing suites as found: case_frame_c124 28/1, t6_regress 9/2).
2. After the edits: the same; every stored plan compiles to the SAME ops; counts unchanged except md5 strings you re-pin
   (`selftest_c155_basecase_frame.py`, `selftest_c156_passwire.py`, `selftest_c157_innerface.py`, `selftest_c158_runcheck.py`,
   `selftest_c158_wire0face.py` - the md5 strings only). `selftest_c158_wire0face` and `selftest_c158_runcheck` counts must be unchanged.
3. New `tools/bench/selftest_c158_gates386.py` on the RECORDED c158-a2-2 data (`diag_c158_a2_3_measure.json` real/sim end rows, bindings from
   the log, graph 6716c499): PB, D, TD give PASS-with-RECORD (the two #376 tag rows, wire 24091); and these still BLOCK: (i) a re-sourced `#376`
   input (same sink, another source terminal), (ii) a tag on a frame that is NOT the plan's frame, (iii) a source-terminal uid different from S1's
   under the same tag, (iv) a lost / new pair on real that sim does not have, (v) a sink-bearing wire dropped on one side only, (vi) a census that
   differs from `MEASURED-SCRATCH` by one class count.
4. Mutation re-score (386(d)): re-run the 158-a2-4 mutation table (`diag_c158_a2_4_mut.py` 461d4f3a, by CALL; write the re-scored table to NEW
   files `tools/bench/mutation_table_p5_rescore.md/.json`, and leave `mutation_table_p5.*` untouched). Report, per row classed `invariant` that
   blocked before, whether it still blocks. A newly PASSING invariant row = STOP and RETURN with the row ids (hand back, no further work). Rows
   that now record must be representation rows only (M3t / M5 are the expected movers; M6 is the known gap and unchanged).
5. Dry + prerun of `plan_ring_p5s02a.json` on the NEW bytes, both MAIN and scratch recipes (same commands as `diag_c158_a2_2_dry.log` /
   `_prerun.log` / `_scr_*`; new log prefix `diag_c158_a3_1_`): dry PASS, prerun PASS, X10 planned MAIN <= 675. Above 675 = RETURN with the number,
   no plan re-cut. Also run `--scratch-required` and `--check-launch` the way `diag_c158_a2_2_checklaunch.py` does and quote the outcome (the
   launch card for the retry carries `retry_of`; say what the launch gate needs on the command line / in the card rules).
6. Report the new md5 of every file you changed; stage_prerun, addrcheck, gscript, stagesim (unless named below), hooks, plan, licence, graph,
   mutation_table_p5.* unchanged. If a fix needs a stagesim edit, RETURN with file:line and the exact change (stagesim is in the write list only for
   a binding / rekey helper, not for the model gap).

Facts file `tools/bench/diag_c158_a3_1_facts.md` (<= 45 lines, facts only, an `OPEN:` line per unresolved thing, before/after lines as file:line).
Return the standard <= 30-line summary. Failure budget 2. A gate refusing your own command text is a false positive: `py tools/gate_fp.py log`,
no env bypass, no hook edit.
