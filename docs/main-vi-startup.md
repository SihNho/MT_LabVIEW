---
type: reference
status: current
date: 2026-09-14
tags: [docs, main-vi]
---

# Main VI startup — the configuration block, frame by frame

> Document 4 of the system inventory (`docs/system-inventory-plan.md`). **First pass.**
>
> Source: the complete 170-diagram sweep (`tools/bench/main_vi_netmap.json`, 2026-09-14). Node identity is
> read from **terminal signatures**, not from node labels — so every "this is X" below is an inference from
> naming convention, marked ⟨inferred⟩, unless a terminal is unique in the whole VI (see instrument-libraries.md
> for the uniqueness rule). Frame numbers are the sweep's diagram indices.

## What the sweep shows for diagrams 1–13

The VI is 57 flat-sequence frames and 76 case frames; the first thirteen diagrams are the early frames of the
outer sequence plus the cases nested in them. Read in order:

| diag | owner | nodes | terminal signatures seen | reading |
|---|---|---|---|---|
| 1 | FlatSequenceFrame | 8 | `Total Lost Frames`; `System no.` `Axes to move` `Set Focus  (0->50)`; 3× property nodes | ⟨inferred⟩ **PI motor init**, driven straight from the panel control `Set Focus (0->50)` (=51.5 today). `System no.`/`Axes to move` is the Mercury GCS library's terminal vocabulary |
| 2 | Sequence | 2 | `x = y?`; `System no.` `If no: current pos z?` `Axes to move` | ⟨inferred⟩ conditional PI move using the startup control `If no: current pos z?` (=30) — this is the "if not auto-referenced, go to the typed z" branch the panel labels describe |
| 3 | CaseStructure | 2 | `System no.` `Axes to move` `Position values` `No.of digits` | ⟨inferred⟩ PI **MOV** (absolute position) |
| 4 | CaseStructure | 1 | `System no.` `GOH axes` `All axes?` `Axis identifier?` | ⟨inferred⟩ PI **GOH** (go home) — the other arm of the same case |
| 5 | Sequence | 7 | `Axes to set` `Velocity values`; `Axes to query`; index array; **`Trans position`** | ⟨inferred⟩ PI **VEL** then a position **query**, then the result stored into the shared field `Trans position` |
| 6 | FlatSequenceFrame | 19 | `cal image array` `# slices in stack` `bandpass/forget array` `obj step between slices` | **calibration-stack preparation** (terminal names match the calibration subVIs' panes) |
| 7 | ForLoop | 6 | `Cosine bandpass` `HIGH/LOW bandpass (mode)` `Raw cal image` `forget radius` | per-slice bandpass build — the loop inside frame 6 |
| 8 | FlatSequenceFrame | 7 | **`Rot position`**; `32bit integer`→`number`; `path`/`refnum`; `string`/`path` | ⟨inferred⟩ rotor position written to the shared field, plus a file open |
| 9 | FlatSequenceFrame | 9 | `x = 0?`; `In Set Position` `Set Focus  (0->50)`; string replace | ⟨inferred⟩ focus set, again from `Set Focus (0->50)` |
| 10 | FlatSequenceFrame | 2 | **`Baud Rate (115200)` `timeout (500ms)` `VISA resource name out`**; `VISA out` | **`ASI TG-1000.lvlib:Initialize.vi` (uid 43997) then `Move Axis to Position.vi` (44036)** — MEASURED 2026-09-14 (`OpSubVIs_v1`, docs/main-vi-subvi-identity.md): the 115200 terminals are the ASI driver's own Initialize inputs, so this frame opens the **ASI stage port (COM4, alias `ASI_Piezo`)** and moves an axis. The same pair recurs on diagram 88 |
| 11 | FlatSequenceFrame | 1 | `millisecond timer value` `milliseconds to wait` | a wait |
| 12 | FlatSequenceFrame | 1 | `position [internal units]` `VISA out` | **`ASI TG-1000.lvlib:Get Current Position.vi` (uid 44196)** — measured identity; a position read over the ASI session |
| 13 | CaseStructure | 1 | `In Range?` `coerced(x)` `lower limit` | range clamp |

## What this settles

1. **The four greyed-out startup controls are all consumed here.** `Set Focus (0->50)` feeds frames 1 and 9;
   `If no: current pos z?` feeds frame 2. That is why they are greyed: they are read once, at startup, and the
   run never looks at them again. (`Autoreference? 1=Y` and `Current pos rot?` were not found by name in these
   frames — see the limits below.)
2. **The shared fields get their first values at startup**: `Trans position` in frame 5 (after a PI query),
   `Rot position` in frame 8. `Focus position` is touched only on diagram 19, later.
3. **PI motor first, then rotor, then serial config.** The ordering of the outer sequence is itself a fact
   the restructuring must preserve (rule 1a: behaviour, not just numbers).

## What this does NOT settle — and is not to be guessed

- ~~Whose port is configured at 115200 on frame 10.~~ **SETTLED 2026-09-14 by subVI identity:** the node carrying
  `Baud Rate (115200)` / `timeout (500ms)` IS `ASI TG-1000.lvlib:Initialize.vi` — the ASI stage port. (The VISA
  resource constant's literal value is still unread — `Constant.Value` remains unbuilt — but the callee decides
  the instrument; NI MAX: ASI = COM4.)
- ~~Whether `Trans position` / `Rot position` here are writes.~~ **SETTLED 2026-09-14 by `Terminal.Is Source?`
  (`OpNodeTerms_v0`, docs/main-vi-state.md): both are WRITES** — frame 5 writes `Trans position`, frame 8 writes
  `Rot position`; every global access in the main VI is a write (readers, if any, live outside this hierarchy).
- **Node identity is by naming convention.** `System no.`/`Axes to move` reads as Mercury GCS because that is
  the GCS LabVIEW library's terminal vocabulary; the authoritative confirmation is `SubVI.VI Path`, blocked by
  the class-cast problem.

## Why the panel-wiring column of document 2 still cannot be filled from this sweep

An attempt to join the 114 front-panel objects against the sweep came back **92 NOT FOUND** — which is not a
finding about the panel, it is a finding about the method. `net_map` walks `AbstractDiagram.Nodes[]`, and a
front-panel object's diagram terminal is a **`ControlTerminal`, a Terminal, not a Node** — it is simply not in
the walk. The 15 "matches" were Global and Property nodes that happen to share a label. The join is void and its
output (`tools/bench/panel_wiring.json`) is kept only as the record of a wrong method.

The correct route is `Traverse('ControlTerminal')` → `Terminal.Connected Wire` (634A000) plus the terminal's
label — a Terminal-class property read on a GObject-typed reference, which is the same cast problem again.
Every remaining gap in documents 2, 3 and 4 reduces to that one capability.
