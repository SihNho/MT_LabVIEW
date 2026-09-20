---
type: reference
status: current
date: 2026-09-14
tags: [docs, stage2]
---

# Stage 2 — assembly step A3: wiring a scripted shift register's sides (2026-09-14 23:0x, overnight cycle 2)

Parent: [stage2-assembly-step-a.md](stage2-assembly-step-a.md). Row 37 gave `add_shift_reg()`: a register whose
**three terminals all come back unwired** — left OUTSIDE (initial value, sink), left INSIDE (source into the body),
right INSIDE (sink of the iteration's result). Stage 2 needs all three wired for each of the kernel's three feedback
registers. No op does that yet.

## Route — one method, three chains, four small ops from one parameterised recipe

`Terminal.Connect Wire` 6349C03, invoked on the **SINK**, `Wire Source` = the source (labviewwiki, adopted in step A).
Every terminal is reached by a **typed chain with no cast** (the seed problem is avoided entirely):

| terminal | chain (all typed) | already proven where |
|---|---|---|
| left OUTSIDE / left INSIDE / right INSIDE of register *i* | WhileLoop seed → `Loop.Shift Registers[]` → IA[i] → `Left Registers[]` → IA[0] → `Tunnel.Outside Terminal` 6356001 / `Inside Terminals[]` 6356000 → IA[0] | `OpShiftRegs_v1` (the donor; reader of exactly these) |
| a terminal of the *n*-th node INSIDE the loop body | the SAME WhileLoop ref → **`Loop.Diagram` 6361401** → `AbstractDiagram.Nodes[]` 6375809 → IA[n] → `Node.Terminals[]` 6359000 → IA[t] | `Loop.Diagram` = NI example short name `Diagram` (NAMES.md); the Nodes/Terminals half is `OpConnectCtl_v0`'s source chain |
| a terminal of the *n*-th node on the TOP-LEVEL diagram (initial value from a node, e.g. a pool image or loadcal output) | `VI.Block Diagram` 23C → `Nodes[]` → IA[n] → `Terminals[]` → IA[t] | `OpConnectCtl_v0` verbatim |
| a front-panel CONTROL's terminal (initial value from a control) | `VI.Front Panel` 23D → `Panel.Controls[]` 6348801 → IA[p] → `Control.Terminal` 6332006 | `OpConnectCtl_v0`'s sink chain |

Ops (each = donor `OpShiftRegs_v1` + one node chain + ONE Connect-Wire invoke; the recipe takes the variant as an
argument and builds them one after another in a single batch):

| op | `reference` (sink) | `Wire Source` | stage-2 use |
|---|---|---|---|
| `OpWireSR_LeftIn_v0` | body node terminal [n, t] | left INSIDE | left register → kernel `x,y,z array` etc. |
| `OpWireSR_RightIn_v0` | right INSIDE | body node terminal [n, t] | kernel `x,y,z array out` → right register |
| `OpWireSR_LeftOutNode_v0` | left OUTSIDE | top-level node terminal [n, t] | initial value from a node |
| `OpWireSR_LeftOutCtl_v0` | left OUTSIDE | control terminal [p] | initial value from a control |

Node/terminal **indices, never names** (row 37's duplicate-name lesson); the caller resolves indices with
`node_terms_uid` on the body diagram beforehand.

## Prediction contract (the runner stops at the first miss; nothing saved on a miss)

- Build: each op `ExecState 1` after its invoke is wired, saved; donor md5 unchanged. `Loop.Diagram` on the WhileLoop
  seed is the one UNVERIFIED property here (NAMES.md lists it from the Wiki) — the first op gates on it.
- **Functional (a register that a running VI actually carries):** scratch copy of `HARNESS_copyloop` + one scripted
  While loop (stop by control) + `IMAQ Copy` dropped in the body + one register from `add_shift_reg`:
  `LeftOutNode`: top-level `IMAQ Create`.`New Image` → left OUTSIDE; `LeftIn`: left INSIDE → `IMAQ Copy`.`Image Dst`;
  `RightIn`: `IMAQ Copy`.`Image Dst Out` → right INSIDE; `Image Src` from the second `IMAQ Create` by `wire()`
  (auto tunnel, row 36). Predict: the three register terminals report the expected wire UIDs (each equal to the UID
  on the far end), **ExecState 0 → 1**, and the VI RUNS and returns with the stop control TRUE.
  `LeftOutCtl` is verified structurally on the same scratch (a second register, its outside wired from the
  `Image Name` control — a type mismatch makes a broken wire, which is the gate: the wire must exist AND ExecState
  must stay 1 only if the types agree; the recipe predicts a broken wire here and deletes it — the op's job is the
  wire, not the type).

Level reached: the wiring ops are FUNCTIONAL (a VI with a scripted, fully wired shift register runs). Value semantics
across iterations remain for the fixture diff.
