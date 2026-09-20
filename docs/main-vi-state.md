---
type: reference
status: current
date: 2026-09-14
tags: [docs, main-vi]
---

# Shared state between loops — what actually crosses

> Document 3 of the system inventory (`docs/system-inventory-plan.md`).
>
> **Status: the shared-state surface is complete and small. The writer/reader map is NOT.** Each row says how it
> was obtained; the missing column is named explicitly at the end rather than left as an impression of
> completeness.

## The inter-loop contract is three numbers

`Global motor pos.vi` — the VI Global named in ARCHITECTURE.md §5 as the cross-loop shared state, and the one the
main VI references **9 times**. Read from its own front panel (`Panel.Controls[]`, 2026-09-14, read-only):

| # | field | type | default | the instrument behind it |
|---|---|---|---|---|
| 0 | `Trans position` | DBL | 0.0 | ASI TG-1000 translation stage (COM4, alias `ASI_Piezo`) |
| 1 | `Rot position` | DBL | 0.0 | Autonics rotor (COM5, alias `Rotor`) |
| 2 | `Focus position` | DBL | 0.0 | PI M-126.PD1 magnet / Z motor (COM3, alias `PI`) |

**Three fields, three instruments, one scalar each.** That is the entire surface, and it is far smaller than the
restructuring plan's discussion of it implied.

Why that is good news for the restructuring: the "one writer per field" contract has **three obligations**, not a
sprawling set. Each field is a plain DBL, so there is no partial-update hazard *within* a field — the hazard is
entirely about *which loop* assigns it. (Contrast the scheduler command, where peer review found that separate
local variables for a multi-field command are not atomic and the fix was one versioned cluster through a
single-owner queue. A single DBL has no such problem.)

## Where each field is touched — located 2026-09-14

From the complete 170-diagram sweep (`tools/bench/main_vi_netmap.json`). Every access below is **wired**:

| field | diagrams | count |
|---|---|---|
| `Trans position` | **5** (Sequence), **19**, **83** | 3 |
| `Rot position` | **8**, **19**, **83** | 3 |
| `Focus position` | **19** | **1 — unique in the whole VI** |

Two things stand out and both matter for the restructuring.

**`Focus position` has exactly ONE access site.** This is the field that earlier design work nearly gave a second
writer, and today it has a single touch point — the cheapest possible starting position for the one-writer
contract, and the one most easily lost by accident.

**Diagram 19 touches all three fields**, and diagram 83 touches two. So the accesses are not scattered evenly;
there is a concentration that is very likely the "publish the current positions" step. Whether diagram 19 *writes*
and the others *read* is the next question, and it is not answered by presence.

**Direction — MEASURED 2026-09-14 12:1x–12:2x (`tools/bench/globals_direction_main.log`,
`main_vi_globals_direction.json`), all seven sites: `Terminal.Is Source?` of each global node's single data terminal
via `OpNodeTerms_v0` (`gscript.node_terms`). Semantics verified the same day on primitives and on a POSITIVE
CONTROL with real globals (NI's Network Streams example: two WRITE + one READ `Host Stop` nodes told apart,
`global_read_control3.log`).**

| field | WRITE sites (diagram) | READ sites |
|---|---|---|
| `Trans position` | 5, 19, 83 | none |
| `Rot position` | 8, 19, 83 | none |
| `Focus position` | 19 | none |

**Every access in the main VI is a WRITE.** The main VI never reads its own globals through a global node. The
motor-loop subVI `Motor control v5_No Recording.vi` (18 diagrams walked, `global_read_control2.log`) contains **no
global node at all**, and the 2026-09-13 whole-tree byte scan found no other accessor in this hierarchy — so, at the
level of what has been measured, **`Global motor pos.vi` is write-only in this hierarchy**: nothing here consumes it.
(Inference, one step beyond the measurements: it is either read by a *different* top-level VI the user runs
alongside, or it is a legacy carrier. The user holds that knowledge — ask, do not guess.) For the restructuring this
means the "one writer" contract is about not *adding* readers/writers carelessly; today there are three writers of
`Trans`/`Rot` and one of `Focus`, and no reader.

(The earlier plan to read `Global.VI Name` 6354800 through a cast is no longer needed for direction; field identity
is the terminal name, measured to equal the field on all seven sites and on the example globals.)

**And direction cannot be guessed from the diagram either**, because 133 of 170 diagrams are case or sequence
frames: an access inside a case runs only in that case. A field written in two mutually exclusive frames has one
effective writer; a field written in two frames that always both run has two. The contract has to be stated per
*frame*, not per diagram.

Node identity per diagram is now measured too — [docs/main-vi-subvi-identity.md](main-vi-subvi-identity.md)
(98 call sites, 56 callees, `OpSubVIs_v1`); the private-member route described in `docs/toolkit-capabilities.md`
was never needed for it.

**One known risk, carried forward rather than re-derived:** `Focus position` nearly gained a **second writer**
during earlier design work. That is exactly the failure the contract exists to prevent, and it is the field to
check first when the writer map becomes readable.

## Other shared-state carriers, and their status

The restructuring plan's boundary audit (2026-09-13, diagrams 160–163) reported every state-carrier class
**CLEAN** for that region — no locals, globals, sequence locals or feedback nodes crossing. That is a
region-specific result, not a whole-VI one.

Whole-VI counts are cheap now that `report_all` exists (1.7 s for 626 nodes) but were **not** run for the state
classes in this pass, because the counts alone would not say who writes what — the same missing column. Running
them is the first thing to do once node identity is readable:

```
report_all(MAIN, "Local")        report_all(MAIN, "Global")
report_all(MAIN, "SequenceLocal")  report_all(MAIN, "FeedbackNode")
```

## Why the shape of the main VI matters here

From the same session (`report_all(MAIN, "Diagram")`, 170 diagrams):

```
CaseStructure 76 · FlatSequenceFrame 57 · ForLoop 17 · Sequence 11 · EventStructure 5 · WhileLoop 3 · top level 1
```

**133 of 170 diagrams are case frames or sequence frames.** So a write to a global is very often *inside a case*,
and "who writes this field" will frequently have the answer "this loop, but only in these frames". The writer map
therefore has to record the **frame**, not just the loop — otherwise two writers that can never run in the same
condition would look like a violation, and two that always do would look like one writer.

That is a real trap for the one-writer contract, and it is worth stating before the map is built rather than
discovering it halfway through.

## Per-frame state (the frame loop's shift registers) — measured 2026-09-14 15:4x

The frame loop (WhileLoop uid 637, diagram 43) carries **14 shift registers**, none stacked, 13 initialised from
diagram 19 (`x,y,z array out`, `position [internal units]`, `VISA out`, `total data array out`, `error out`,
`LastBufferNumber`, `pos in cal image out`, `Bead is good? array out`, `F-x out` (uninitialised), `Value` ×2,
`System no.`, two unnamed). Who initialises, reads and writes each one, with wire UIDs: the two measured sections at
the end of docs/frame-loop-wire-graph.md (`OpShiftRegs_v0/v1`, INDEX row 29). Four final values leave the loop
(`position` → `Global motor pos.vi`, `total data array out` → Array Subset, `error out` → `save N xyz traces.vi`, `VISA out`).

## `Global motor pos.vi` — the user's reading (2026-09-14 20:0x)

User: *"User defined라면 아마 전체 모터 컨트롤을 싱글 vi로 처리해 가독성 향상시키려고 넣은 것 같아. … 모든 모터를 아우른다고
봐야지."* Consistent with the measurement: it is the lab's own VI Global holding the three motor positions
(Trans / Rot / Focus), written by the seven motor paths, no logic, no hardware access, no reader in this hierarchy.
Restructuring rule: keep it and keep writing it (it is the natural cross-loop shared state, ARCHITECTURE §5); label
it write-only unless a reader outside this hierarchy turns up. Not a decision the user needs to make now.
