---
type: archive
status: historical
date: 2026-09-17
tags: [status, cycle15, d1, narrative]
relocated_from: STATUS.md
---

# STATUS narrative relocated 2026-09-17 (rule 4 — STATUS reached 136 lines)

Moved **verbatim**; nothing rewritten. STATUS keeps one line and a pointer for each.

## OPEN 19 — REV 4 WRITTEN

19. ✅ **REV 4 WRITTEN** — the plan is now the build order: §11a/§11b folded in, the node-by-node move table on the
   BEFORE census keys (**21 moves + 1 delete + 1 drop**; 8 of 14 SRs; 5 of 31 ControlTerminals), F1 **60 s**, A5 →
   **D2**, #376 in 1.7, S/N1/F1/F2 with counts. Recipe `tools/recipes/build_d1_v0.py`. Rev 3's 8 findings disposed.

*(Superseded in part by §11c and by the run-4 measurement: the move table is **20** moves, not 21 — `#12589`
stays on 1.1 — and §5d's ControlTerminal count was corrected from 5 to **6**.)*

## OPEN 26 — the rev-4 prior-art review, disposed

26. ✅ **REV-4 REVIEW DISPOSED** (`archive/peer/2026-09-17-priorart-priorart-d1-build-rev4.md`, 548 s, $6.67):
   **7 findings, 0 novel, all ACCEPTED.** FIXED **A1** (false "impossible"), **A4** (measured **122 MB/s** ⇒ F1
   60 s ≈ **7.3 GB**, not 4), **B1** (the `Control Name` writer is the `OpSetIndexMode_v0` shape — one additive
   op), **B3** the costly one: **`#376`'s w3268/w5090 are shared nets whose 6 other sinks STAY on 1.1**, so moving
   it bares them silently (phase P run 2's exact death) and S3b saw only moving nodes — S3b now walks the net and
   a new **`S3b-collateral`** gate fails the build if a staying node loses a wire. ESCALATED **A2 A3 B2** → 25.

*(Run 4 measured B3's hazard and it did **not** materialise for `#376`: the census shows **0 staying nodes
bared**. `#376` is a SINK on w3268/w5090, so its move leaves the net's source and its other sinks intact. The
gate stays — it is cheap and it is the only thing that would have caught the opposite case.)*

## OPEN 19b / 19c / 24 — the three relocation facts

19b/19c/24. ✅ **THE THREE RELOCATION FACTS, measured, now in plan §2/§5**: phase P 12/0 (a `CaseStructure` moves
   **with its frames**, 171→171; `OpMoveIn_v0` UID control `'UID 3'`; the move **CUTS** border wires −7/−2, so
   ExecState is read only at the end); ctlterm 9/0 (`#642` reparents, 114→114; **31** terminals in `Diagram#639`);
   step 0 12/12 + 8/8 (payload **1 DBL**; 14 SRs tabled; a wire graph alone mislabels 6 of 7 backward-slice nodes).

*(The "171→171" here is the **post-loop-creation** count — `probe_move_into_v0.log:217` reads `Diagram 170` on
the fresh copy and `:220` creates the loop. Transcribing 171 as the BEFORE count cost run 1 of the D1 build;
peer `archive/peer/2026-09-17-d1-s1-diagram-count.md`.)*

## The four D1 relocation runs of 2026-09-17, in order

| run | log | outcome |
|---|---|---|
| 1 | `tools/bench/build_d1_v0.log` | **FAIL S1** — `Diagram 170` where the plan predicted 171; seven other classes exact. Cause measured in our own probe log; peer `d1-s1-diagram-count` ANSWERED, constant corrected. Nothing edited. |
| 2 | `tools/bench/build_d1_v0_run2.log` | S1 ✅, S2 ✅ (`WhileLoop 3→6`, `Diagram 170→173`), **FAIL S3** — `#5540` landed in `Diagram#1215`/`WhileLoop#1135` (the loop created LAST) because all three new body diagrams reported Traverse index **20** at creation. Peer `d1-s3-stale-traverse-index` ANSWERED; every index is now re-resolved from its UID immediately before use. |
| 3 | `tools/bench/build_d1_v0_run3.log` | **FAIL S1** — the "fresh copy" censused as run 2's EDITED state (`Diagram 173, Node 630, WhileLoop 6`): run 2 returned early without closing the target, so LabVIEW served a **resident** VI and the disk overwrite was invisible. Peer `d1-s1-stale-in-memory-copy` ANSWERED; fixed with a unique working-copy name per run **and** gate `S1z` (md5 the destination before LabVIEW sees it). |
| 4 | `tools/bench/build_d1_v0_run4.log` | **46 pass / 5 fail, 61 s** — the relocation itself completed. See STATUS OPEN 27 / 27b. |
