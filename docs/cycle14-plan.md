---
type: plan
status: superseded
superseded_by: docs/cycle15-plan.md
date: 2026-09-16
cycle: 14
tags: [cycle-plan, diagram-hierarchy, A3, A4, flatsequence]
---

# Cycle 14 — build `OpFlatSeqDiagrams_v0`, finish A3 (170/170), then A4

`docs/pre-rig-master-plan.md:66-72`. **A3** ends this cycle at 170 of 170 diagrams; **A4** — *"the frame loop's
TRUE membership — body AND nested frames; the body-only list exists in `frame-loop-anatomy.md:40-55`; only the
nested delta is new"* — is the deliverable.

## 🔴 GATE STATE BEFORE ANY OF THIS RUNS

`py tools/violations.py --due` (2026-09-16, `tools/bench/retro_cycle13.log`) reports **`judgement-in-material` at
3 occurrences — cycles 11, 12, 13 — with no decision on file**. CLAUDE.md: *"At 3 of the same slug the next cycle
must build the mechanical device for it first"*, and `tools/hooks/guard_cycle.py` enforces it against RECIPE
builds. **So §3 below (the op build) and everything downstream of it cannot start** until a judgement session
writes a dated `DECISION: device` / `DECISION: no-device` block into `docs/violation-decisions.md`. Choosing which
is judgement work; the material session does not take it. §1 and §2 (retrospective, this plan, the prior-art
review) run regardless — the gate exempts diagnostics, docs, peers and the retrospective itself.

## The judgement calls that opened this cycle, already taken (do not re-open)

1. **Build ONE new op, `OpFlatSeqDiagrams_v0`** — `FlatSequence` → `Diagrams[]` **3578BC00** → per element
   `GObject.UID` **632A813**, array out. No `Owner`, no tunnels. The ids are MEASURED, not guessed
   (`tools/bench/flatseq_diagrams_attach.json`: data terminal `Diagrams[]`, `attached: true`;
   `docs/NAMES.md:581-597`).
2. **Resolve the 57 `FlatSequenceFrame` diagrams with it, then do A4.** `ClassSpecifierConstant.AllTypes[]` is
   **not** built (codex: it only confirms the class tree, and access no longer depends on it).
3. **OPEN 1 gets its last read** — `node_labels` + node classes on `ForLoop #1359`'s inner diagram.

## §1 — cycle-13 retrospective (DONE, gate)

`tools/bench/retro_cycle13.log`, one bgrun, 217 s. `audit_cycle --cycle 13` + `retrospective --cycle 13` (codex,
ANSWERED 215 s) → `archive/peer/2026-09-16-retrospective-cycle13.md`, **six slugs, every citation re-checked, all
disposed in that file's "What was done with it"**. Outcome: the DUE block above.

## §2 — this plan + the prior-art review (trigger `new-op`, slug `priorart-cycle14-flatseq-a4`)

## §3 — `OpFlatSeqDiagrams_v0` — BLOCKED by the gate above; the design, with the prior art that fixes it

### What already exists, checked before a line was written (CLAUDE.md, "before creating any new op")

`grep "^def " tools/gscript.py`, `ls tools/recipes` (78 recipes), `docs/toolkit-capabilities.md:40-52`. **No
existing op returns a FlatSequence's frame diagrams**, and the two the brief nominated as donors do **not** have
the ladder the brief describes:

| candidate | its real front end | disqualified because |
|---|---|---|
| `OpOwnerChain_v1.vi` (17 151 B) | `UID to GObject Reference.vi` → `Generic.Owner` → cast(GObject) → `UID` (`docs/toolkit-capabilities.md:48`) | addressed by **UID**, not by Traverse+index; and its cast is seeded for `GObject` |
| `OpNodeTerms_v0.vi` (16 014 B) | `VI.Block Diagram` → `Diagram.Nodes[]` → IndexArray → `Node.Terminals[]` → For loop (`build_opnodeterms_v0.py:9-14`) | **no Traverse at all**; index is (diagram, node) |
| **`OpReport_v3.vi` (10 235 B)** | Open VI Reference → Traverse(`Class Name`, `index`) → IndexArray → `GObject` Property (`gscript.py:261-283`) | *is* the stated ladder and is the smallest — but has **no cast**, see below |
| **`OpSubVIs_v1.vi`** | Traverse(`Class Name`, `index`) → IndexArray → **To More Specific Class** → `AbstractDiagram.SubVIs[]` → **For loop** → `SubVI[VIName,VIPath,UID]` → **3 auto-indexed array indicators** (`build_opsubvis_v0.py:50-56`, steps 3-12) | **nothing** — this is the whole shape of the wanted op |

### The constraint that picks the donor, and it is not size

erdosmiller's `Traverse for GObjects.vi` returns refs typed **`GObject`**; `Diagrams[]` lives on
**`FlatSequence`**. A GObject wire into a FlatSequence-typed Property Node is a type conflict, so a
**`To More Specific Class`** node is mandatory — and **a TMSC node cannot be dropped by script**, because its
`target class` needs a class-specifier constant and *that* constant has no scripted creator
(`build_oploopcast_v0.py:4-8`), which is also `SKILL.md`'s rule-0 exception #1.
⚠️ **Do not over-read that citation** (corrected here 2026-09-16 after re-opening it):
`docs/toolkit-capabilities.md:63` is headed **"~~The one missing seed~~ SOLVED 2026-09-14 — the typed-control
seed"**, and `:78` marks the old framing superseded. What is still impossible is *creating the class-specifier
constant*; what is solved is *retargeting an existing TMSC* by feeding its `target class` refnum input from a
typed control. **Therefore the donor must already contain a TMSC**, and retargeting it is a solved operation.
`OpReport_v3` has none; `OpSubVIs_v1` does. Donor =
**`OpSubVIs_v1.vi`**, and the build is a re-type of four objects rather than a construction.

Node counts are asserted as **gate 0** (`report_all` on each candidate) rather than argued from file size.

### The one genuinely new step: a **FlatSequence-typed seed** for the TMSC

`build_oploopcast_v0.py:4-8` establishes the mechanism: TMSC's `target class` is a **refnum INPUT**, so any refnum
control of the wanted class seeds it, and `test_oploopcast.log` T3 measured that a seed casts **only** its own
class (a ForLoop seed on a WhileLoop ref → error 1055 downstream). OpLoopCast got its seed by creating a real For
loop on a scratch VI and `create_control`-ing the typed terminal, then `copy_into`.

**And the mechanism is already written down as general** (`docs/toolkit-capabilities.md:65-67`, found on the
re-read above): *"A refnum CONTROL of the wanted class is made by `Terminal.Create Control` on the `reference`
INPUT of a property node already configured to that class."* The documented recipe gets that property node out of
an NI example VI; here we can build one directly.

**So the cheap route, still a PREDICTION this build tests rather than a measured fact:** `build_property(OP,
'VI Server:FlatSequence', [('3578BC00', False)])` is **measured** to create a FlatSequence Property Node with no
flat sequence anywhere on the VI (`tools/bench/flatseq_diagrams_attach.json`, `new_property_uids: [43]`, on a
scratch copy of `EMPTY_v0.vi`). Its unwired `reference` terminal is therefore FlatSequence-typed, so
`create_control` on that terminal should yield the seed **on the op itself** — no scratch VI, no `copy_into`.
If that fails, the fallback is the measured OpLoopCast route with a real flat sequence on a scratch VI.

### Build steps (one recipe, `tools/recipes/build_opflatseqdiagrams_v0.py`, one `MATERIAL=1` bgrun)

| # | step | prediction |
|---|---|---|
| 0 | `report_all` node counts of `OpReport_v3` / `OpNodeTerms_v0` / `OpOwnerChain_v1` / `OpSubVIs_v1`; donor md5 | donor untouched; counts recorded, not assumed |
| 1 | copy `OpSubVIs_v1.vi` → `OpFlatSeqDiagrams_v0.vi`, `open_panel` (edits are silently declined otherwise — `STATUS.md` item 3) | ExecState 1 |
| 2 | `net_map` diagram 0: find the TMSC (`target class` + `specific class reference`), its seed wire, the `SubVIs[]` Property Node, and the body's `SubVI` Property Node | all four found by terminal name, never by position |
| 3 | build the FlatSequence seed control; delete the old TMSC `target class` wire; wire the seed in | Wire −1 then +1; ExecState 1 |
| 4 | delete the `SubVIs[]` PN; `build_property('VI Server:FlatSequence', [Diagrams[] 3578BC00])`; wire TMSC out → its `reference` | Property net 0; data terminal is `Diagrams[]` |
| 5 | delete the body `SubVI` PN; `build_property('VI Server:GObject', [UID 632A813])` inside the body; wire `Diagrams[]` → its `reference` (crosses the loop) | LoopTunnel +1, ExecState 1 |
| 6 | the 3 old output tunnels/indicators → 1: `exit_loop(['UID'])`, `set_index_mode(1)`, `tunnel_indicator` | one new ARRAY indicator (ControlTerminal **and** Wire — a ControlTerminal alone is dangling, `gscript.py:1704`) |
| 7 | `set_auto_error_handling(False)`; ExecState 1 → `save()`; label map → `tools/bench/opflatseqdiagrams_labels.json` | never save at ExecState 0 |

**Functional gate (this is what makes it verified, not structural):**
- **F1** — on the MAIN VI, read-only: run the op over all **21** `FlatSequence` traverse indices
  (uids in `tools/bench/owner_semantics.json → class_census.FlatSequence`) and take the union of returned diagram
  uids. **Predict: the union is exactly the 57 `FlatSequenceFrame`-owned diagram uids** from
  `report_all(MAIN,'Diagram')` — no more, no fewer.
- **F2** — **113 ∈ that union** (the diagram A2 reproduced the 1055 on) and **686 ∈ that union** (the diagram the
  frame loop `WhileLoop#637` sits on).
  ⚠️ The brief asked for "the FlatSequence uid from `owner_semantics.json` whose frame is diagram 113". **That
  datum does not exist**: `owner_semantics.json → classes.FlatSequence.instances[0]` records `owner_uid: 0` and
  `error 1055` — the uid is precisely what could not be read. F1/F2 are the constructible form of the same test.
- **F3** — the op echoes each FlatSequence's own UID, so traverse index → uid is read, not assumed
  (`archive/peer/2026-09-15-opwiresource-fail5-traverse-index-order-mismatch.md`).
- **F4** — main VI md5 `2a78e17c449cacdaf5da389818526859` before AND after.

**Failure budget = 2.** Two failed builds ⇒ stop, write both logs' failing lines and the two competing
explanations, hand back.

## §4 — finish A3: 170 of 170

Run the op on all 21 FlatSequence uids; produce `frame diagram → FlatSequence → parent diagram` rows (the parent
diagram of a FlatSequence is `OpOwnerChain_v1` on the FlatSequence uid — the five-clean-class hop, measured 63/63
in cycle 13). Diff against `tools/bench/diagram_tree_main.json`; write the completed 170-row hierarchy to
`tools/bench/diagram_tree_a3.json` (**v2**, keeping `part_a` verbatim) and a new dated section in
`docs/diagram-hierarchy.md`. **Report resolved-count out of 170 and every disagreement individually.**

## §5 — OPEN 1, the last read

`node_labels` **and** node classes (via `report_all`) on `ForLoop #1359`'s inner diagram. **The index is already
on disk — do not re-derive it:** `tools/bench/diagram_tree_a3.json → part_a.table` holds
`diagram_uid 7911 · diagram_index 74 · structure_uid 1359 · parent_diagram_uid 639`, and `node_labels` takes the
**traverse index**, so the call is `g.node_labels(MAIN, 74)`. (Frame-loop body for comparison: uid 639 = index 43,
parent 686.) Report every node whose label or class suggests a panel read —
`Property`, `Local`, `ControlTerminal` — and whether any is `Auto-Reset`. The wire-level answer is already in
`STATUS.md` OPEN 1 (wire 9806 is **not** among #1359's ten terminal wires, zero panel-control sources); this read
closes the remaining route, a property read *inside* the loop. **Facts only** — the verdict is judgement.

## §6 — A4: the frame loop's TRUE membership

The body-only list is `docs/frame-loop-anatomy.md:40-55` (6 subVIs — uids 6810, 22700, 5058, 48, 1114, 376 — plus
10 `Value` Property Nodes). **Only the nested delta is new.**

1. From the completed 170-row hierarchy, transitively close "diagrams whose parent chain reaches **Diagram 639** /
   `WhileLoop 637`", to any depth, each with its owning structure's class and uid.
2. For that set: the union of `g.subvis(diagram)` call sites (**0 junk** — `OpSubVIs_v1` is creator-free,
   `tools/bench/test_opsubvis_v1.log` T0) and of VISA-touching nodes, diffed against the body-only list.
3. Output a table — *diagram · structure · subVI/VISA nodes added* — into `docs/frame-loop-anatomy.md` as a new
   dated section. **Facts only; interpretation under `OPEN:`.**

⚠️ Note for §6, already measured and easy to forget: `Diagram 639`'s own parent is `Diagram 686`, whose owner
class is **`FlatSequenceFrame`** — so the frame loop itself sits inside a flat-sequence frame, and §4 is a
precondition of §6 in fact and not only on the dependency chart.

## Scope, lock, hygiene

Main VI **read-only**, md5 asserted before and after every run; the `STATUS.md` lock block held across each run;
one scratch VI per run with a unique name, created and deleted in the same run; every VI Server reference closed;
`MATERIAL=1 py tools/bgrun.py --max-min N --log …` for everything.

## Files this cycle expects to touch

`docs/cycle14-plan.md` · `docs/violation-decisions.md` (judgement) · `tools/recipes/build_opflatseqdiagrams_v0.py` ·
`tools/bench/build_opflatseqdiagrams_v0.log` · `tools/bench/opflatseqdiagrams_labels.json` ·
`tools/bench/retro_cycle13.log` · `tools/bench/retro_cycle13_runner.py` · `tools/bench/diag_a3_complete.py` ·
`tools/bench/diag_a3_complete.log` · `tools/bench/diagram_tree_a3.json` · `tools/bench/frame_loop_a4.json` ·
`docs/diagram-hierarchy.md` · `docs/frame-loop-anatomy.md` · `docs/toolkit-capabilities.md` · `docs/NAMES.md` ·
`STATUS.md` · `archive/peer/` (this cycle's reviews).

## Out of scope, deliberately

`ClassSpecifierConstant.AllTypes[]` is not built. `OpCaseFrames_v0` is not retried
(`pre-rig-master-plan.md:286`). `OpOwnerChain_v1` is not modified. No hardware, no GUI action, no A5/A7.
