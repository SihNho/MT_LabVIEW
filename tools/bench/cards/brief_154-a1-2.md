---
card: 154-a1-2
status: current
date: 2026-10-09
---
# Brief 154-a1-2 - FACT CENSUS of every consumer of the frame counter (docs/d1/ring-p5.md PD374(g)); offline, read-only, may run beside the P5-1 plan card

No LabVIEW, no VI opened (the ORIGINAL is never opened: read only STORED files), no tool/plan/doc edit except the one output file. This is facts for the later P6 plan; do not judge or recommend a design.

## Question (MEASUREMENT)
For the ORIGINAL's `#644` (loop `i` on Diagram #639; w3268) and for s09's `FrameIdx` (and its sources `#644` w29454 / FS #29411 / FrameIdx write `#6859`, display remainders `#10068` / `#29240`, any autofocus cadence counter), list EVERY consumer. Table columns:
`system (original | s09)` · `sink node (uid, class/name)` · `loop` · `what it computes` · `uses the value as a COUNTER y/n` (Q&R / every-N / modulo / equality against a count; y only if the stored graph or a cited doc line shows it) · `file:line` evidence.

## Where to read (stored files only)
`tools/bench/p5_facts.md` F4 (lines ~48-57) and its cited logs (`diag_c153_a2_6_orig_read.*`, `census2.log`, `census3.log`, `census4.log`, `facts_c120_types.json`); `docs/cycle27-plan.md` around lines 3748-3751 (the 8 sinks of w3268, NOT the whole file);
the stored S1 / original graph reads that card 153-a2-6 produced; the s09 graph `tools/bench/graph_ring_p4s09_20261009_062044.json` (22f967b5, read-only, parse with Python); `docs/NAMES.md:112` (note corrected 2026-10-09). For what a sink "computes", follow the sink node's class/name in the graph and the doc line that explains it; if neither states it, write `unmeasured` (never infer).

## Steps
1. Original: the 8 sinks of w3268 (node, loop, what, counter y/n, file:line). Quote how you confirmed the count 8.
2. s09: every consumer of `#644` i (w29454 -> its 6 sinks per p5_facts line 19), of the `FrameIdx` write (#6859) and read (#30240 / w30278), and of `#10068` / `#29240`; plus any node whose name or doc line says autofocus cadence / every-N frames. Same columns.
3. A short pairing section: original sink <-> s09 sink where the graph shows the same node (by uid or by the doc line), `unpaired` otherwise. Facts only.
4. Invariants md5 before = after: `docs/d1/ring-p5.md` 58f168cb, graph 22f967b5, s09 VI eb1d0f31 (do not open), stagekit/stagexec/stagesim/vigraph/stage_prerun/gscript pins from the task's inputs. Write nothing else.

## Report `tools/bench/frameidx_consumers.md` (the deliverable; <= 80 lines, frontmatter `type: fact`)
Tables from steps 1-3, `unmeasured` rows listed, an `OPEN:` line. Return <= 15 lines: row counts, unmeasured count, path.
