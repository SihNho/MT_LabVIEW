---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, plan]
---

# copyloop-forloop-tunnels-plan

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (64s)
- **why asked:** plan review before building HARNESS_copyloop (steady-state IMAQ Copy cell); the unverified mechanism was Create For Loop Control Names
- **verdict:** unverified

## Question

PLAN REVIEW (attack; brief). GOAL: the steady-state IMAQ Copy cost cell the earlier review asked for (archive/peer/2026-09-14-imaq-copy-handoff-plan.md): N repeated A->B copies inside ONE Run, per-copy cost = (T(N) - T(0)) / N, timed from Python. THE UNVERIFIED MECHANISM: our scripted For loop has no way to wire N (New VI Object cannot make numeric constants for N; Terminal.Create Control on the loop's N terminal produced dangling objects on 2026-09-06). Plan: give the loop an AUTO-INDEXED input from an existing front-panel ARRAY control instead - N = the array's row count, set from Python per run (rows = an N x 1 U8 2D array; 0 rows = the loop runs 0 times = the baseline T(0)). Construction on a copy of HARNESS_copy1 (IMAQ Create A -> ReadFile -> Create B -> IMAQ Copy A->B, all wired): (1) obtain a 2D U8 array control by dropping Flatten Pixmap.vi, create_control on its '8-bit pixmap' input, then deleting the Flatten node (the control stays, unwired); (2) gscript.for_loop(target, location, tunnels=['8-bit pixmap'], indexing=[True]) = erdosmiller Create For Loop.vi with 'Control Names' = the control's label and 'Inputs Indexing?' = TRUE - it should create the loop with an auto-indexed input tunnel wired from that control's terminal (never used with names in this project - the unknown); (3) drop a second IMAQ Copy INSIDE the loop body (drop_subvi with the body diagram index), wire ReadFile 'Image Out' -> inner Copy 'Image Src' and Create B 'New Image' -> inner 'Image Dst' with branch=True (both sources are already wired; wire() across a loop boundary auto-creates plain tunnels, proven for unwired sources); (4) the outer IMAQ Copy stays as the untimed warm copy that sizes B before the loop (dataflow: it must run BEFORE the loop - how to force that without a sequence structure? wire the outer Copy's 'Image Dst Out' into the loop instead of Create B's New Image - then the loop depends on the outer copy having run; agree?); (5) auto error handling off; ExecState 1 -> save. RUN: rows = 0 (T0), 50, 200; report (T(N)-T0)/N per frame image, closed panel, 200 timed Runs each. ATTACK: (a) does Create For Loop.vi with Control Names create the tunnel from the CONTROL TERMINAL (the control is on the panel but its terminal is unwired) and set indexing from 'Inputs Indexing?' - or does it require the control to be wired to something first (its documented contract)?; (b) will LabVIEW run an auto-indexed loop over a 2D array by ROWS (N = rows) and does a 0-row array give 0 iterations cleanly (no error)?; (c) is the inner copy's dependency on the outer copy's 'Image Dst Out' enough to guarantee ordering, and does branching Image Out to the inner Copy create a race with the outer Copy (both read A; reads are fine)?; (d) anything about running a 200-iteration copy of 1.3 MB inside a COM-invoked Run that would distort (buffer reuse makes the copy a no-op? NI: IMAQ Copy copies every time?). One paragraph.

## Answer

The plan is sound except for step (2), which remains the single go/no-go uncertainty: the public erdosmiller documentation points users to its examples but does not document whether `Control Names` discovers and wires an otherwise-unwired front-panel terminal, so first build only the empty loop and require reporter evidence of one indexed tunnel plus `ExecState == 1`; do not proceed on a clean return alone ([upstream repository](https://github.com/erdosmiller/lv-scripting)). A 2D array auto-indexes by its outer dimension?봢ach iteration receives one row?봞nd an empty outer dimension should execute zero iterations without error; NI confirms that an indexed input determines the For Loop count, while its array explanation identifies rows as the outer-loop elements ([NI auto-indexing](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG), [NI arrays](https://www.ni.com/en/support/documentation/supplemental/08/labview-arrays-and-clusters-explained.html)); nevertheless, round-trip the Python values because COM may not preserve an intended `0횞1` shape distinctly from an empty array. Wiring outer Copy?셲 `Image Dst Out` as the loop?셲 B input is sufficient to order outer Copy before the loop under LabVIEW dataflow ([NI dataflow](https://www.ni.com/docs/en-GB/bundle/labview/page/block-diagram-data-flow.html)); branching A to both copies is safe because both only read A, while the ordered B reference prevents concurrent writes?봟ut IMAQ image wires are mutable buffer references, so this explicit dependency is essential ([NI IMAQ ordering](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P8khSAC)). Buffer reuse removes repeated allocation, not the copy operation: NI describes destination resizing/reuse and copying source image content to the destination ([IMAQ manual](https://download.ni.com/support/manuals/322917a.pdf), [IMAQ reference](https://docs-be.ni.com/bundle/322567a/raw/resource/enus/322567a.pdf)). Finally, randomize/interleave `N=0,50,200` runs and demand linearity of `T(N)-T(0)`; otherwise cache warming, drift, or COM/run overhead has contaminated the inferred per-copy cost.

## Sources

(extract from answer)

## What was done with it

Followed the go/no-go gate exactly (tools/recipes/build_harness_copyloop.py step 3a): the empty loop was built first and the reporter showed ForLoop 1, LoopTunnel 0, control unwired, ExecState 0 -> gate FAIL, nothing saved. The peer's caution was right: a clean return proved nothing. Verdict: correct; the ordering advice (outer Copy Image Dst Out feeds the loop) is kept in build_harness_copyloop2.py.
