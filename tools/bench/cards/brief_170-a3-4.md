---
card: 170-a3-4
status: current
date: 2026-10-13
---
# Brief 170-a3-4 (assignment 170-3, the ONE retry of 170-a3-2) - give plan 170 a graph that names its callees, then build the P6 replay copy

Read first: `tools/bench/cards/brief_170-a3-2.md` (the build, UNCHANGED - every step, gate and hygiene item applies), `tools/bench/cards/result_170-a3-2.json`, `tools/bench/diag_c170_a3_2_facts.md`.

## Why 170-a3-2 returned (a fact, not a verdict)
The dry of `stage_replay_swap.py --plan 170` failed gate A2 at `tools/bench/stage_replay_swap_170_dry.log:9` ({6810: None, 22692: None}): the dry's callee census comes from the plan's `input.graph` JSON,
and `graph_ring_p6_20261012_212645.json` (fbc7b7ee) holds no SubVI names (`p6_replay_facts.md:43`). Plan 110's graph (`graph_disp_20260927.json`) had them. Nothing was built; the recipe has its `PLANS["170"]` entry (fa94e80c) and the plan exists (9ec7a13e).

## What this card adds - ONE read of the bed, then the unchanged build
1. Produce a graph JSON of the bed `claudeDev\D1_ring_p6_20261012_212645.vi` (c2d9c13c) that carries the SubVI callee names per node uid (the field the dry reads, `graph_summary.subvi_calls` or what `stage_prerun`'s dry census uses - find it by reading
   how plan 110's graph and `diag_c170_a2_3_graph.py` (which made `diag_c170_a2_3_graph_buf.json` for the buf stand-in's dry) produce it; use THAT existing graph reader, a shared function, no new reader). Read it from a BYTE COPY of the bed
   (scratch under claudeDev, deleted after; no save, no run), name the output `tools/bench/graph_ring_p6_callees_<ts>.json`, quote its md5 and the two rows (#6810 -> 'get buff image-lost frames.vi', #22692 -> 'IMAQdx Get Image.vi').
   If the read shows a different callee or a missing uid for #6810/#22692: RETURN with the facts, no swap. `graph_ring_p6_20261012_212645.json` (fbc7b7ee) is NOT edited or replaced; other plans keep their graphs.
2. Point `plan_replay_swap_170.json` `input.graph` at the new graph (plan 170 only; plans 78/95/110 byte-identical), re-run the dry. It must now pass A2; later dry gates that print PASS-UNVERIFIED are named by this card's rule
   ("DRY-UNVERIFIED-OK: ...", prefixes as the dry prints them; the launch passes `--unverified-card tools/bench/cards/task_170-a3-4.json`). Do not relabel a refused gate as a row.
3. Then exactly `brief_170-a3-2.md`: prerun (X10, `load_by_vi` c2d9c13c 603.7 stays; no memory_model edit), prior-art review (write its "What was done with it" under `archive/peer/`), the ONE launch
   `py tools/bgrun.py --material --max-min 45 --log tools/bench/launch_c170_p6swap.log -- py -u tools/recipes/stage_replay_swap.py --plan 170 --unverified-card tools/bench/cards/task_170-a3-4.json`
   (the flag goes on the bgrun command exactly as card 170-a3-1's launch did, `launch_c170_paced60.log`), gates A1-A6 and C1-C3, hygiene, facts in `tools/bench/diag_c170_a3_2_facts.md` (append, <= 40 lines).

## Not in this card
No leg, no compare, no hook/stage_prerun/STATUS/INDEX edit, no VI Run, no hardware. A new unexpected result = RETURN with the facts (this is the retry; it is spent).
