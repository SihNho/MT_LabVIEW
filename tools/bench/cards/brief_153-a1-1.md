---
card: 153-a1-1
status: current
date: 2026-10-09
---
# Brief 153-a1-1 - P5 FACT CENSUS F1..F8 (docs/d1/ring-p4d.md PD370(f)); facts only, offline

Read `docs/d1/ring-p4d.md` lines 105-161 (PD370, parts (a) and (f)) first. This card measures; it does NOT design. No design text, no option table,
no `docs/d1/ring-p5.md`, no plan file, no P5 build, no tool edit. The next judgement session writes the P5 design from your facts.

## What to produce
`tools/bench/p5_facts.md` (<= 100 lines) and `tools/bench/p5_facts.json`. Every fact carries `file:line` (or json path / uid) evidence.
A fact that is not on disk is written as `UNMEASURED: <what> - <cheapest way to read it>`, never guessed.

## The eight facts (copy the wording of PD370(f) F1..F8 exactly as the headings)
- F1: each input terminal of the file writer `#376` in S1: source node / terminal / wire uid, data type; then where that source sits in s09 (loop 1.1 / 1.2 / 1.7 / top level / gone) and whether the input is wired in s09. At least w4517 'current frame data array in' (from #2626), w3268 'frame index', w1397.
- F2: the 45 items of the s09 Error List (expected file 5146f980), each mapped to an object uid; mark which are loop 1.7's open rows.
- F3: loop 1.7 `#23041` in s09: body, shift registers, stop source, wait/timing, every node it runs per iteration.
- F4: the ORIGINAL's call of `#376` (read the on-disk S1 graph / original reads; the original VI is never opened for editing): inside which case/structure, under which condition (save on/off, every frame or every N), order relative to the tracking kernel, and what 'frame index' is (loop i, BufNum or another counter).
- F5: loop 1.2 in s09: the valid-frame boolean (RingSeqCheck n1==n2 AND n1>last) and the rolled-back Select outputs: uids and terminals.
- F6: how loops 1.2 and 1.7 stop in s09 (StopAll local, `stop (end)` latch) and their shutdown order.
- F7: the ops / routes / donors that created and removed the pool queues (Obtain / Enqueue / Dequeue / Release, element-type constant), their hygiene records, and the result of `py tools/protocol.py requires` for each.
- F8: the s09 load (596.7) and the X10 headroom for a P5 session, QUOTED from `tools/bench/memory_model.json` (do not recompute).

## Sources
s09 graph `tools/bench/graph_ring_p4s09_20261009_062044.json` 22f967b5; Error List expected `tools/bench/errorlist_expected_D1_ring_p4s09_20261009_060515.json` 5146f980;
the S1 graph / wiki files and the L7-1b / L7-R logs and facts (`tools/bench/c73_l7r_facts.*`, `decision_l7_1b_*.json`, `dev_prerun_stage_d1_l7_*.log`); the pool-queue stage logs/recipes (grep `Obtain Queue` in `tools/recipes/`, `docs/NAMES.md:909-920`); `docs/d1/ring-p4d.md`.
Use `py` scripts that READ json. Put scripts and logs under `tools/bench/diag_c153_a1_1*`; each new script <= 120 lines.

## LabVIEW
Prefer none. At most ONE read-only LabVIEW read, of a claudeDev COPY, only for a fact absent on disk; name it in `p5_facts.md` (which fact, which file, md5 before/after).
If used: background it under `py tools/bgrun.py --max-min 20 --log <file> -- <cmd>`, close every reference, then verify LabVIEW is gone (`tasklist | grep -i labview` -> 0). Never open or save an original; never save the bed.

## Invariants (md5 before and after, quote them)
stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun c739eb86, stagesim 128bacfb, vigraph 13be0847, s09 `claudeDev\D1_ring_p4s09_20261009_060515.vi` eb1d0f31, graph 22f967b5, Error List 5146f980, memory_model 6f2b5687.

## Return (<= 30 lines)
Per pass item: met / not met + path. List every UNMEASURED fact. An `OPEN:` line for anything that needs judgement. Failure budget 2; a failure that repeats stops the card with the facts.
