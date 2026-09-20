---
type: plan
status: superseded
superseded_by: docs/cycle14-plan.md
date: 2026-09-16
cycle: 13
tags: [cycle-plan, diagram-hierarchy, A3]
---

# Cycle 13 — A3: complete the 170-diagram hierarchy from the machine, replacing position matching

`docs/pre-rig-master-plan.md:66-72`, row **A3**: *"Complete the 170-diagram hierarchy — the 41 unresolved plus
every FlatSequence link, replacing position matching (the diagram was Clean-Up'd, so position means nothing)."*
A3's dependency A2 is **DONE** (`docs/diagram-hierarchy.md`, "A2 — OWNER SEMANTICS PER STRUCTURE CLASS";
`tools/bench/owner_semantics.json`; 54 gates pass / 0 fail).

## The judgement calls that opened this cycle, already taken (do not re-open)

The three calls A2 left under `STATUS.md` OPEN 9 were answered by the judgement session before this cycle started:

1. **A3 proceeds now, on the five clean classes, with `OpOwnerChain_v1` unchanged.** A2 measured that
   WhileLoop · ForLoop · CaseStructure · Sequence · EventStructure all return a non-zero owner uid AND complete the
   structure → parent-diagram hop, with no error (`owner_semantics.json`, 14/14 rows).
2. **FlatSequence is handled TOP-DOWN, by measurement** — asking the machine whether anything we already own
   returns a flat sequence's frames' diagram uids. It is **not** handled by modifying `OpOwnerChain_v1`, and
   **`ClassSpecifierConstant.AllTypes[]` is NOT built in this cycle** (`docs/NAMES.md:611-622`; it stays under
   OPEN — it answers "is `FlatSequenceFrame` outside the `GObject` subtree?", which is a *why*, not the *link*
   A3 needs).
3. **STATUS OPEN 1's next read is the inputs of `ForLoop 1359`** — A2 measured `LoopTunnel #10177 → ForLoop#1359`
   and `ForLoop#1359 → Diagram#639`, so the modulo remainder crosses into a For loop that sits on the frame loop's
   own diagram. What drives 1359's other input tunnels has never been read.

## Scope — ONE diagnostic, read-only on the main VI, no op built or modified

`tools/bench/diag_hierarchy_a3.py`, one `MATERIAL=1` bgrun, main VI md5 `2a78e17c449cacdaf5da389818526859`
asserted **before and after**, lock block in `STATUS.md` held across the run. Every name resolved from
`docs/NAMES.md` and `docs/toolkit-capabilities.md` at planning time. **Nothing in `user.lib\claudeDev` is saved
except a scratch VI created and deleted in the same run (3b).**

### 3a — the full hierarchy for the five clean classes

`g.report_all(MAIN,'Diagram')` returns all **170** diagram uids with their owner **class** in ONE op run
(`gscript.py:294`; the prior-art review of cycle 12 established this as the helper, deleting 18 op runs from A2).
For every diagram whose owner class is **not** `FlatSequenceFrame` and not `''` (the top-level diagram),
`OpOwnerChain_v1` runs twice: diagram → structure uid, structure → parent diagram uid. The structure → parent hop
is memoised per structure uid, so the cost is ~112 + ~63 op runs, not 224.

Output: a machine table `diagram_uid → structure_uid → parent_diagram_uid` written to
`tools/bench/diagram_tree_a3.json`, plus a **diff against `tools/bench/diagram_tree_main.json` and
`tools/bench/diagram_hierarchy.json`** — the position-matched tree A3 exists to replace: agree / disagree /
newly-resolved counts, with **every disagreement listed individually**.

**Prediction: 0 disagreements**, from A2's 14/14. A disagreement is a failed prediction and owes a peer review.

> **REVISED 2026-09-16 after the prior-art review**
> (`archive/peer/2026-09-16-priorart-priorart-cycle13-a3.md`, claude/opus, ANSWERED 591 s, $5.1239, 44 turns).
> **Ten verdicts, all accepted, none argued.** What changed, with the reviewer's citations:
> **A3-i** `errCO` is NOT the cast's error — `build_opwiresource_v4.py:108-115` shows it is the `error out` of a
> `Generic.ClassName` Property Node hanging off the cast's *output*, and the cast (`To More Specific Class`, a
> Function) has **no error indicator in the op at all**, so 3c cannot separate "the cast generated it" from "a
> downstream node did". **A3-iv** error 1077 was only ever measured from a *bogus* id
> (`toolkit-capabilities.md:226`); a valid id on the wrong class has silently produced a node with no data
> terminal (`:131`), so the attach verdict is the **data-terminal-name census**. **B2** the `Frames[]` route *is*
> `OpCaseFrames_v0`, and the attach **passed** in all five failed runs — the failures were downstream. **B3a**
> `tools/bench/main_vi_nodeterms.json` already holds ForLoop #1359's ten terminals (diagram `"43"`, node 16), so
> 3d's ~40-run ownership walk is a file lookup plus one `node_terms_uid` read. **B3b** `diagram_tree_main.json`'s
> per-diagram `uids` lists make structure → home diagram a file lookup for catalogued structures. **B4a**
> `Frames[]` **6363801** on `VI Server:MultiFrameStructure` attaches and censuses as data terminal `Frames[]` —
> five recorded times, `build_opcaseframes_v0.log:9-11,36-38,61-63,90-92,120-122`. **B4b** `errO` was already read
> and merged into `errs`, so the new fact is *which* indicator carries the 1055, with `errG` the competing
> candidate. **A4** `docs/main-vi-panel-map.md:317` pins `Auto-Reset` (uid 17472) to **wire 9806**, and
> `docs/frame-loop-wire-graph.md:440` records #1359 t1 (wire 9097) as fed by `#8953 Initialize Array`.
> **A3-ii / A3-iii** two active docs contradict the measurement and are annotated in this cycle.

### 3b — FlatSequence, top-down, and the branch has an explicit STOP

The 57 `FlatSequenceFrame`-owned diagrams cannot be walked upward: A2 measured owner uid **0**, `error 1055` and
an empty cast echo, twice, on two different diagrams (113 and 686). So the question is asked from the structure
end instead, on **3** of the 21 `FlatSequence` uids: does any reader or VI-Server property we **already own**
return that structure's frames' **diagram uids**?

The reader that plausibly answers it **already exists and is not the failed route**: `OpTunnelRead_v0.vi`
(`docs/toolkit-capabilities.md:50`, 24/24 verified) takes a tunnel uid and an inner-terminal index and returns
that terminal's **frame DIAGRAM uid** via `Terminal.Diagram` **634A002**. So the run probes which traverse class
string reaches a structure tunnel (`Tunnel` · `SequenceTunnel` · `FlatSequenceTunnel` · `Structure` ·
`MultiFrameStructure` — 109 = unknown name, 1092 = not in the GObject hierarchy, `docs/NAMES.md:566-580`), then
drives `read_inner` on the FlatSequence-owned ones. Coverage reached is **reported, not claimed**: the sweep is
bounded by a 300 s budget.

**The `Frames[]` half is now one attach census, not a route.** Prior-art B2: the `Frames[]` route *is*
`OpCaseFrames_v0`, which failed five times — and the **attach passed in every one of them**; the failures were
downstream (an inherited terminal-reader chain, then a downcast trap). Prior-art B4a: `6363801` on
`VI Server:MultiFrameStructure` is measured attaching, with data terminal `Frames[]`, five times at
`tools/bench/build_opcaseframes_v0.log:9-11,36-38,61-63,90-92,120-122`. So exactly **one** uncovered fact is
bought here — does `6363801` attach to `VI Server:FlatSequence` — on a scratch copy, and **the verdict is the
data-terminal-name census, not the absence of error 1077** (prior-art A3-iv: the measured 1077 came from a bogus
id, `toolkit-capabilities.md:226`, while a *valid* id on the wrong class has silently created a node with no data
terminal, `:131`). This is the check `build_opcaseframes_v0.py:49-58` already uses.

**STOP condition, written in advance:** if no existing reader returns the uids and getting them would require a
**new op VI**, the branch stops there, the candidate property IDs go under `OPEN:`, and nothing is built.
`OpCaseFrames_v0` is not retried (`pre-rig-master-plan.md:286`).

### 3c — where the 1055 comes from: DE-MERGE every error indicator (one read)

⚠️ **Rewritten after prior-art A3-i and B4b, and the original framing was wrong twice over.** `errCO`
(`"error out 10"`) is **not** the cast's own error — `build_opwiresource_v4.py:108-115` builds it as the
`error out` of a `Generic.ClassName` **Property Node hanging off the cast's OUTPUT**, and the cast itself
(`To More Specific Class`, a Function) has no error indicator anywhere in the op. And `errO` is **not** a new
read: `build_opownerchain_v1.py:268-269` already merges `errL/errT/errO/errU/errG` into `errs`, which A2 measured
as carrying the 1055 (`diag_owner_semantics.log:96-98`).

So the read is: on one `FlatSequenceFrame` diagram (113) and one clean control (639), report **all eight**
indicators separately — `errL`, `errT`, `errO`, `errU`, `errG`, `errS`, `errWU`, `errCO`. The only new
information is **which** of them carries the 1055; `errG` (the UID Property Node, also downstream of the cast) is
the competing candidate and the one codex's mechanism predicts
(`archive/peer/2026-09-16-ownerchain-flatseqframe-1055-r2.md:74` — the cast yields `Not A Refnum` and the
*downstream* UID node emits the 1055). **This run cannot separate "the cast generated it" from "a downstream node
generated it", and must not be written as if it could.** Facts only.

### 3d — STATUS OPEN 1: the inputs of `ForLoop 1359`

`ForLoop#1359` sits on `Diagram#639` (the frame loop's own diagram) and receives the PERIODIC modulo remainder
through input `LoopTunnel #10177`.

⚠️ **Rewritten after prior-art B3a and A4 — the ~40-run ownership walk is gone.**
`tools/bench/main_vi_nodeterms.json` **already holds ForLoop #1359's ten terminals** under diagram `"43"`,
node 16, each with `is_source` and its wire uid. So membership is a file lookup confirmed by **one**
`g.node_terms_uid(MAIN, 43, 16)` read (identity-proving: it returns the node's own uid), and the count/`N`
terminal question is answered in the same rows — a For loop's `N` is a terminal of the **ForLoop node**, which
`g.tunnels()` structurally cannot see. Then `OpWireSource_v5` resolves the driving node of each **input** wire,
named through `node_labels` on diagram 639 and `panel_wiring` (wire → control label).

The `Auto-Reset` question becomes a **membership test on a number already on disk**: `docs/main-vi-panel-map.md:317`
pins `Auto-Reset` (uid 17472) to **wire 9806**, so the run asks whether 9806 is among #1359's terminal wires and
whether it appears as a source of any of them. `docs/frame-loop-wire-graph.md:440` likewise already records #1359
t1 (wire 9097) as fed by `#8953 Initialize Array` through left shift register 9018 — that is a cross-check, not a
rediscovery. Both files were uncited in the first draft of this plan (prior-art A4), and `docs/NAMES.md:848-851`
makes reading the panel map mandatory before building a reader for the main VI.

**Facts only — what it means for "is the PERIODIC auto-reset gated by `Auto-Reset`?" goes under `OPEN:` for
judgement.**

## Gates this cycle passes through first

1. Cycle-12 **retrospective** (`tools/audit_cycle.py --cycle 12` + `tools/retrospective.py --cycle 12`), every
   `VIOLATION:` line disposed, `py tools/violations.py --due` clean. If a slug is DUE, the device for it is the
   next cycle's first work and A3 does not run.
2. **Prior-art review**, trigger `cycle-start`, slug `priorart-cycle13-a3`, released only by `REFUTED:` or
   `FIXED:` lines with citations (`CLAUDE.md`, "Review has THREE layers").

## Files this cycle expects to touch

`docs/cycle13-plan.md` · `tools/bench/diag_hierarchy_a3.py` · `tools/bench/diagram_tree_a3.json` ·
`tools/bench/diag_hierarchy_a3.log` · `tools/bench/retro_cycle12.log` · `docs/diagram-hierarchy.md` ·
`docs/NAMES.md` · `STATUS.md` · `archive/peer/` (this cycle's reviews) ·
and the three documents the prior-art review found contradicting the measurement or carrying a stale claim:
`docs/stage2-assembly-step-e.md` (A3-iii) · `docs/camera-acquisition-facts.md` (A3-ii) ·
`docs/toolkit-capabilities.md` (A3-iv, the 1077 caveat).

## Out of scope, deliberately

No op VI is built, modified or saved. `ClassSpecifierConstant.AllTypes[]` is not built. `OpCaseFrames_v0` is not
retried. A4 (the frame loop's true membership) waits for A3's table. No hardware, no GUI action.
