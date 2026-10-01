---
type: decision
kind: topic
status: current
date: 2026-10-02
parent: docs/d1/INDEX.md
tags: [d1, ring-buffer, p3b, pre-decided]
---

# Ring buffer P3b (P3b-1 / P3b-2) — decisions from 268 on

Scope: the slot writes of loop 1.1 (IMAQ Copy + error guard, per-slot `TransPos`/`RotPos`/`FrameIdx`, `Num(i)`,
`Latest`), split into P3b-1 and P3b-2 by predicted memory. Everything decided up to 267 is in the frozen
`docs/d1-loop12-17-split-plan.md` (PD258–267 at :2749–2973); its in-force lines are in `docs/d1/INDEX.md`.

How to add: see the 5-line note at the top of `docs/d1/INDEX.md` (next number = 1 + the highest `NNN.` in
`docs/d1/*.md`, never below 268; a `USER-RULES:` line in every item; one line added to the index).

## Pre-decided

269. **(cycle 130 judgement, 2026-10-02 — after 130-5 FAIL 3/1, `plan_ring_p3b_split_c130_5.log`, `diag_c130_5_frames.log`)**
     USER-RULES: U1, U9 (relied on: the FINAL graph is unchanged — split end == unsplit 70, 10244 objects / 5933
     terminals / 1974 wires; only the cut point between two never-run intermediates moves; none contradicted).
     - **(a) Memory cut ACCEPTED:** P3b-1 = N 31, BIND 18, R 20, predicted 663.4 MB; P3b-2 = N 39, BIND 14, R 16,
       664.3 MB (both ≤ 675, X10 model PD268(a)). Split self-test 12/0. The cut moves FS frame f0's `Num(i)=-1` group
       (9 rows) into P3b-2; only 4 cuts were valid and the 2 under 675 both do that (next best keeping f0: 687.1).
     - **(b) An EMPTY f0 after P3b-1 is accepted** (f0 0 / f1 16 / f2 18 terminals in the simulated end state). P3b-1 is
       broken by design and never run; PD238(c)'s order (−1 → copy → values → BufNum → Latest) holds in the FINAL graph,
       which P3b-2 completes. PD261(d)'s "IMAQ Copy + guard together" holds (both in P3b-1).
     - **(c) P3b-1's FS/FU recipe gates compare each frame's terminal count with the simulator's predicted end state**
       (from the finalized plan/pred, never typed) instead of "every frame holds rows" (`stage_d1_ring_p3b1.py:51-52,66`);
       docstring `:1-11` updated to the new cut. Same change for P3b-2's gates when it is rebased.
     - **(d)** Broken-file count unchanged: P3b-1 = 3, P3b-2 = 4 of 6.
