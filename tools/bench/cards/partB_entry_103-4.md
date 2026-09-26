---
title: display-stage Part-B entry (card 103-4) - stagexec from_step + stage_d1_disp.py --from-step
date: 2026-09-27
card: task_103-4.json
source: tools/bench/cards/split_plan_103.md row B (amended: Part A = ops 1-33, Part B = ops 34-47)
status: plan
---
# Part-B entry — what changed and why (one page)

**Deliverable path.** Part A (card 103-3) saved `claudeDev\D1_s1_dispA_20260927_024535.vi` (ops 1–33 of `tools/bench/sim/disp/plan_disp.json`,
broken by design) and its binding `tools/bench/stage_d1_dispA.json` (`partA.bind` obj/term/diag, plan md5 c7d80fc9…, stop_after 33).
Part B (next cycle, fresh LabVIEW) must continue from that file WITHOUT re-executing ops 1–33.

**Edits (no new op, no LabVIEW op VI, gscript / stagekit.copy_in untouched):**
1. `tools/stagexec.py`: `load_binding` (plan md5 must match, stop_after == from_step, refuses a Part A that created shift
   registers), `bind_state` (sim step state -> real uids through the binding; unbound created uid -> stop), `Executor(from_step=k,
   binding=…)`: entry read compared with simulated step k through the binding (WARN-class tolerated in record mode), value gates of
   ops ≤ k re-read (read-only `read_bool_const`), parity + PRIME on the bound step-k state for ends of ops > k, ops k+1.. only;
   `dry_run(from_step, binding)` runs the Part-B dry on the bound state. Self-test 91/0 incl. T41/T42 negatives.
2. `tools/recipes/stage_d1_disp.py`: `--from-step N --base <dispA file>`: B0 binding gate, input = the dispA file (md5 from its JSON),
   W0 pre-existing wires = S1's (plan base graph, 1899 == Part A's measured W0), B1 entry gate; end gates E1/W1/E2/E3/PS unchanged.
3. `tools/bench/sim/disp/graph_dispA_step33.json`: SIMULATED offline stand-in graph for the dispA md5 (step 39 bound), used by the dry
   run only.

**Known risk (from split_plan_103.md risk 1):** Part B must open a file saved broken; the plan forbids cold-loading it headless
(recompile spin). The Part-B run loads it through `stagekit.Stage.start` -> `gscript.ensure_loaded` in a fresh LabVIEW.
