---
card: 154-a1-1
status: current
date: 2026-10-09
---
# Brief 154-a1-1 - P5-1 PLAN (loop 1.2 side) made on the REAL s09 graph; dry + prerun; NOT launched (docs/d1/ring-p5.md PD374(a)(c)(e)(f)); offline

Offline: no LabVIEW, camera or motor; NO `--launch`; no stage-tool, hook or elrule edit; the pinned tools stay byte-identical. Design is fixed by `docs/d1/ring-p5.md` PD374 - read it and `tools/bench/p5_facts.md` (F1..F8) only.
The routes exist - copy them, change names/bases only: `tools/bench/cards/brief_150-a3-5.md` (maker -> rebase -> X10 -> pred -> recipes -> licence -> dry + prerun), `brief_151-a1-1.md` (what the scratch later needs), the s09 pair
`tools/recipes/stage_d1_ring_p4_s09v18.py` + `_scratch.py` (recipe form), `tools/bench/plan_ring_p4_s09v18*.json` if present (plan/pred/licence form), `tools/bench/diag_c149_a1_2_elrun.py`.
Queue routes: stagexec route 'queue' obtain/enqueue/dequeue (`stagexec.py:252-257`, `gscript.queue_node` `gscript.py:1480`); the pool plan `tools/bench/plan_qrt_pool.json` and recipe `tools/recipes/stage_d1_qrt_pool.py` are the donor for the Obtain/Enqueue rows.

## Facts this card starts from (do not re-measure)
Bed = s09 `claudeDev\D1_ring_p4s09_20261009_060515.vi` md5 eb1d0f3107bbba49c9ae67a47c0ee50f (never opened for edit), graph `tools/bench/graph_ring_p4s09_20261009_062044.json` 22f967b5, load_by_vi 596.7 MB, X10 = start (load + op-0 read 5.9) + formula, fail 680, MEMSTOP 695 (`p5_facts.md` F8).

## What to do
1. **Read the targets from the REAL s09 graph, quote each with its uid/index/class:** FS1 frame `#4866` (P2b's initialiser frame); `#2626` and its output t2813 'appended array' (type DBL 1-D); RingSeqCheck `#29724` output t29900 'valid' and its sinks (w30457 incl. the 8th sink); loop 1.2's body Diagram `#23166`;
   the loop 1.2 exit side and the `686` diagram where the final local write goes; `#23041` (loop 1.7) is NOT touched in P5-1. If any target is missing or differs from PD374(a), RETURN with the rows (do not decide).
2. **Plan P5-1** (`tools/bench/plan_ring_p5s01.json`, sim in `tools/bench/sim/ring_p5s01/`), exactly PD374(a)(c) 1.2 side and nothing from the 1.7 side: Obtain Queue on `#4866` with element type DBL 1-D (constant/array of DBL) and max size unwired; new I32 indicator `records final (1.2 to 1.7)` with initial value -1 written on `#4866` (P2b / PD240(b) initialiser pattern);
   refnum into loop 1.2 by a tunnel; NEW Case structure in loop 1.2's body selected by `valid` t29900 - True frame = Enqueue(`#2626` t2813 -> element) + enqueue-count +1; False frame = pass-through; an I32 shift register (init 0) for the count; after loop 1.2 exits, ONE local write of the count's final value to `records final` on `686`, ordered by data dependency on 1.2's exit.
   Release Queue and all 1.7-side work are NOT in P5-1. Queue error terminals stay unwired (PD374(a)). <= 40 actions, no `of` pair split; if the whole plan is above 40 actions or MAIN X10 above 680, cut inside the same order (PD374(e)) and say where.
3. **Rebase** onto the real s09 graph (`py tools/stage_prerun.py --rebase <plan> --graph tools/bench/graph_ring_p4s09_20261009_062044.json`; bgrun if the hook asks). **stagesim replay** (`stagesim.py` read-only): quote PROVISIONAL steps (pass needs 0) and every refusal verbatim with file:line. A route or op kind that does not exist (e.g. Case-structure creation inside a loop body, shift-register creation, local write) is a RETURN with the facts, not a tool edit.
4. **X10** at the measured start (`stage_prerun.x10_start` of the s09 md5): range, count, X10 vs 680 / 695 margins.
5. **Pred under `vigraph.py` a7eb58c7** (no conversion; position-key rows), recipes `tools/recipes/stage_d1_ring_p5s01.py` + `_scratch.py` from the s09 pair (base/start/cut/pred/names only, no new op kind beyond the plan's), licence from the rebased plan by script (copy the s09 licence script), a sink gate per `wire_indicators` census row read by script (zero is a valid answer if stated), X11 (`--buildarray-check`) quoted.
   Expected Error List recorded later at the scratch; here only state the elrule prediction if the pred form asks for one.
6. **Dry + prerun PASS** on the final bytes of both recipes and the plan; `--scratch-required` rc quoted; X10 lines for MAIN and scratch; PROVEN-PATTERN or prior-art situation stated (do NOT run a prior-art review here - the launch card decides). A gate false positive: `py tools/gate_fp.py log`, no env bypass.
7. **Invariants** md5 before = after: stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun c739eb86, stagesim 78b8d5a1, vigraph a7eb58c7, s09 eb1d0f31, graph 22f967b5, EL expected 5146f980, memory_model 6f2b5687, ring-p5.md 58f168cb, every stored P4 recipe/plan/pred (never launched), `tools/hooks/**`. No LabVIEW process at the end (`tasklist`).

## Return conditions
A target differing from PD374(a); a missing route/op kind; a rebase / replay refusal; a prerun gate failing twice at the same place; a protected md5 moved; MAIN X10 > 680 for the shortest meaningful prefix.

## Report `tools/bench/diag_c154_a1_1_facts.md` (<= 45 lines)
Targets read (uid/class/index, file:line); action list and count; rebase output; replay PROVISIONAL count; X10 numbers; pred form; X11; sink-gate rows; licence summary; dry/prerun/scratch-required rc; files created; invariants. `OPEN:` line. Facts only; a result-dependent action is not yours (RETURN with the facts).
