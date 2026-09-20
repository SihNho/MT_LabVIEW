---
type: narrative
status: historical
date: 2026-09-13
tags: [archive]
---

# The array-returning reporter — 646 s → 1.7 s on the main VI

**Date:** 2026-09-13, ~22:40–23:30 · **Rig untouched** (LabVIEW only; no instruments)

---

## 1. The problem

The toolkit's diagram reader was **O(n²)**, and the cause was not where it was assumed to be. Measured earlier
the same day:

```
one bare op run, SMALL target VI     10.4 ms
one bare op run, the MAIN VI        960.8 ms      <- 92x, scales with TARGET size
SetControlValue / GetControlValue     0.07 ms     <- COM is irrelevant
```

~990 ms of every run is the **fixed** cost of `Open VI Reference` on a 473 KB VI with 98 subVI call sites.
`report()` calls the op **once per object**, so a 626-node sweep paid it 626 times: 601 s predicted, 618 s
measured. Varying the traversed class by 720× moved the time only 23 %, so the traversal itself is a thin layer
on top of that fixed cost.

The restructuring reads far more diagram than that, which is why the work order puts tooling first.

## 2. What was blocking the fix, and why the recorded blocker was wrong

The fix is obvious — loop **inside** LabVIEW and return arrays — and had been blocked on one thing: the
auto-indexed output tunnels needed **array indicators**, because a COM caller reads results with
`GetControlValue(label)`. STATUS.md recorded the blocker as:

> no donor exists ... front-panel object creation is the fleet's weak spot

**That was wrong, and it had been wrong for a week.** No donor was ever needed: an indicator created *from a
tunnel* is typed by LabVIEW, so the array comes for free. What was actually missing was one hop in the scripting
path, which nobody had looked for.

## 3. Measurements

### 3.1 Why `create_indicator` could not do it (probe, two rounds)

`OpCreateIndicator_v0` addresses `VI → Block Diagram → Nodes[] → Terminals[]`. Swept over a For Loop's
`Terminals[0..13]` **after** an auto-indexed output tunnel existed:

| terminal | ControlTerminal | Wire | verdict |
|---|---|---|---|
| 0–7 | **+1** | **+0** | **dangling** — a front-panel object appears but nothing is wired |
| 8–13 | +0 | +0 | nothing |

Zero wired hits. The scoring rule matters and was set before the run: *a real hit is ControlTerminal +1 **AND**
Wire +1*. `create_indicator` never fails loudly — it creates *something* either way — so counting front-panel
objects alone would have reported eight successes.

The first round of this probe was **malformed** and is recorded as such: it swept the loop's terminals *before*
any output tunnel existed, so it could only ever miss. Re-asked in the right order, it gave the table above.

Peer review then explained it exactly: `ForLoop.Terminals[]` are the loop's own infrastructure terminals, and
**a Tunnel is a GObject, not a Terminal**, so it inherits no Terminal methods. The documented route adds one hop:

```
Structure.Tunnels[]        6360801       (or Traverse('LoopTunnel', i), which the fleet already had)
  -> Tunnel.'Outer Term'   6356001       <- THE MISSING HOP
  -> Terminal.'Create Indicator' 6349C02
```

### 3.2 `OpTunnelInd_v0` — built, then verified functionally

Built from `OpSetIndexMode_v0`, whose front half (`Traverse('LoopTunnel', index) → IndexArray → To More Specific
Class`) was already proven. Structural result: ExecState 1, Invoke 1, Wire 12.

The functional test is the one that counts, because **ExecState says nothing about a datatype**. On a
never-run VI the COM defaults discriminate cleanly:

| tunnel | result | indicator value | verdict |
|---|---|---|---|
| 0 (the loop's INPUT tunnel) | indicator created, **Wire +0** | — | dangling, correctly refused by the wrapper |
| **1 (the auto-indexed OUTPUT tunnel)** | indicator created, **Wire +1** | **`()`** | **an empty ARRAY** — not `(0, 0)` |

### 3.3 `OpReportAll_v0` — correctness and speed

Built on `OpReport_v3`, which already emits the whole `References` array and then throws it away through an Index
Array. Delete that, put the property reads inside a For Loop, auto-index four results out:

```
GObject.Position 632A800 · GObject.UID 632A813 · Generic.Class Name 6327803 · Generic.Owner 6327806
```
(one GObject-class property node carries all four, since GObject inherits Generic; a second node reads the
owner's class name). All IDs from `docs/vi-server-ids.json` — none guessed.

**Acceptance: same answers AND faster.** Both paths timed end to end from Python, warm. "IDENTICAL" means every
row's `uid`, `class`, `pos` and `owner` match **in order** — order was compared deliberately, because a
same-set/different-order result would corrupt every index-based lookup downstream and silently.

| target | class | n | `report_all` | `report` | speed-up | correctness |
|---|---|---:|---:|---:|---:|---|
| small | Node | 14 | 0.05 s | 0.15 s | 3.0× | IDENTICAL |
| small | Wire | 28 | 0.05 s | 0.31 s | 5.9× | IDENTICAL |
| small | ControlTerminal | 8 | 0.05 s | 0.09 s | 2.0× | IDENTICAL |
| small | Diagram | 1 | 0.13 s | — | — | IDENTICAL *(after the fix in §4)* |
| **main** | **Property** | **106** | **1.15 s** | **108.13 s** | **93.8×** | **IDENTICAL** |
| **main** | **Node** | **626** | **1.70 s** | **646.50 s** | **379.8×** | **IDENTICAL** |

The 646.50 s confirms the 618 s baseline and the 601 s prediction. `report_all` is essentially **flat in n** —
0.05 s at 14 objects, 1.70 s at 626 — because the fixed cost is paid once.

## 4. One real defect, found by the test and not by inspection

On class `Diagram` the op raised a **modal dialog**:

```
Error 1055 occurred at Property Node in OpReportAll_v0.vi
LabVIEW: (Hex 0x41F) Object reference is invalid.
```

The error is 1055 — an **invalid reference** — not 1057/1058, which is what "this class has no such property"
would look like. The invalid reference is the **top-level diagram's `Owner`**: it is the one object in a
traversal with nothing above it. Confirmed by the data, not by argument: `report()` returns `owner = ''` for that
row too, and the rows match.

The dialog itself was **my defect**: both property nodes inside the loop had an unwired `error out`, so LabVIEW's
automatic error handling turned a harmless error into an 8-second block. Classes that never error (Node, Wire,
Property) hid it completely. Fixed with `set_auto_error_handling(False)` — the standing fleet treatment for an op
whose property nodes error by design (`OpNetInfo_v1`, `OpFPLabels_v0`, `OpTunnelInd_v0` all carry it).

Silencing an error is only legitimate if the results are still right, so it was re-verified rather than assumed:

```
Diagram   report_all (3, 'TopLevelDiagram', (0, 75), '')
          report     (3, 'TopLevelDiagram', (0, 75), '')      -> IDENTICAL, no dialog
Node      14 rows, IDENTICAL, no dialog
```

## 5. Three terminal names cost three build cycles

Every one was guessed from documentation instead of read off the machine, and every one failed the same way —
`error 5001: Get Outputs.vi`, which means **the name does not exist** (an existing-but-illegal name is declined
*silently* instead).

| guessed | actual |
|---|---|
| `specific class reference out` | **`specific class reference`** |
| `Outside Terminal` | **`Outer Term`** |
| `Class Name` | **`ClassName`** |

The last is the sharpest: in the *same VI*, `Traverse for GObjects.vi` really does have a `Class Name` input
**with** a space, while the `Generic.Class Name` property's terminal has none. Neither spelling can be inferred
from the other.

**The rule that came out of it**, now in `docs/NAMES.md`: after creating a node and before wiring it, run
`net_map(target, diagram, ...)` — it prints every node's full terminal list, costs one call, and replaces a
whole build cycle.

## 6. A tool bug fixed on the way

`gscript.wire()`'s success check was wrong for **boundary crossings**. Wiring into a loop creates a tunnel *and*
splits the connection into two wire objects, so a single successful crossing reports `+2`, not `+1`. The flat
`+1` check raised on three consecutive probe runs whose wires had actually succeeded. It now expects
`1 + tunnels created`, checked exactly — not loosened.

## 7. Level of verification

**Functional.** Real traversals on a real 473 KB VI, results compared row-for-row with the existing path, and the
datatype of the new indicators read back over COM. Not merely `ExecState == 1`.

Known limitation, stated rather than left implicit: `report_all` returns the four fields `report()` returns.
Any caller needing something else still needs the per-object op.

## 8. Files

| file | what it is |
|---|---|
| `probe_arrayout2.log` | the malformed first probe + the three answers it did give |
| `probe_arrayout3.log` | the corrected sweep — 0 wired hits, the negative result |
| `build_optunnelind2.log` | `OpTunnelInd_v0` assembled |
| `test_optunnelind.log` | **the `()` datatype proof** |
| `build_opreportall_v2.log` | `OpReportAll_v0` assembled, 12 steps, label map |
| `test_opreportall.log` | **the 380× table** |
| `fix_opreportall_errors.log` | the 1055 dialog fix and its re-verification |
| `opreportall_labels.json` | indicator label → field, read from the machine at build time |
| `*.py` | the recipes, replayable |
