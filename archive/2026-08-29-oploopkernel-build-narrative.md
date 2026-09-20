---
type: narrative
status: historical
date: 2026-08-29
tags: [archive, kernel]
---

# OpLoopKernel_v0 — build narrative, 2026-08-29 night

Moved out of `STATUS.md` item 4 during the 2026-08-30 ingest/lint. The *conclusions* live in
STATUS (fleet table + item 4); this is the story, including the wrong turns, which is why it is
here and not there.

## How it was built (~90% scripted)

Skeleton: a copy of `OpForLoop_v0` — which is itself an adapted `Example 8 - For Loops.vi`, and
therefore **already carried idle `Input Names` / `Output Names` controls**, a lucky break that
removed two donor-copies from the plan.

Steps, in order:
1. `copy_into` the `vi path 2` control from `OpSubVI_v1` (donor-copy protocol).
2. Quick-Drop an `Open VI Reference` primitive — menu route (View ▸ Quick Drop, type the name,
   Enter, then click the canvas). Its `vi path` input row was found by hover-tooltip after one
   mis-wire landed on `options` (a `file path`→`long` type clash, cleaned with
   `remove_bad_wires`).
3. `drop_subvi` `Create SubVI.vi`.
4. Scripted wires: `CFL.Diagram out → CS.Diagram in`, `CFL.Inputs → CS.Inputs`,
   `OpenRef.vi reference → CS.VI Reference`.
5. GUI wires (`lv_gui.ps1 -Action wire`, rows confirmed by tooltip before each):
   `vi path 2 → OpenRef.vi path`, `Input Names → CS[5]`, `Output Names → CS[9]`.
6. Error chain rethreaded `CFL → CS → Close Reference → error out indicator`: the old
   `CFL.errout → indicator` wire was GUI-selected and deleted, then the new chain wired by script.

`CS.location` was deliberately left unwired — the kernel's position inside the loop subdiagram is
cosmetic and the run arrow did not object.

## The wrong turn: "structure ✓, wiring ✗"

The first smoke tests produced a loop, a kernel inside it (owner=Diagram) and "+1 Tunnel per
Control Name" — but **zero wires**. Fault-injection narrowed it:

- a bogus **output** name raised 5001, proving the Output-Names path reached Create SubVI and that
  the two GUI wires were not swapped;
- a bogus **input** name produced silence, proving CS's input-pairing loop ran zero times, i.e.
  **`Create For Loop`'s `Inputs` OUTPUT was arriving empty** despite the wire existing.

Two hypotheses were tested and both failed to explain it (`Inputs Indexing? = [False]`, and
control-name/indexing permutations). The root cause inside the vendor VI was never pinned.

**The load-bearing discovery came from a control run with zero control names, which still produced
"+1 Tunnel".** That is when it became clear the counter had been lying all along: a For Loop's
**`N` terminal reports as class `Tunnel`** (and `P` adds another when parallelism is configured).
Checking `PARALLEL_build_testA.vi` — the file this project had been calling "the P=4 evidence" —
confirmed it has N/P terminals and **no data tunnels at all**. `OpForLoop_v0`'s tunnel-creation had
therefore been a **silent no-op since the day it was written**, and every "tunnel +1" count in
earlier status notes was really the N terminal.

## The fix: bypass, don't debug

Rather than keep chasing the vendor VI's empty `Inputs` output, the op now wires `Get Controls`'
control terminals **straight into `Create SubVI.Inputs`**. Because the sink is inside the loop and
the source outside it, **LabVIEW auto-creates the tunnel on the border crossing** — auto-indexed
for array sources, plain for scalars, which is exactly the semantics the parallel kernel needs.

Consequence: the op's `Inputs Indexing?` control is now **dead** (index modes follow LabVIEW's
wiring defaults). The flat `x,y,z array` therefore still needs explicit treatment, since a naive
auto-index would hand each iteration one scalar.

## The VI-Server wedge (same session)

After one of the failed runs, every COM `Run` blocked ≥180 s while property reads answered
instantly, menus worked, no modal dialog existed on repeated `-Action dialogs` scans, and `Abort`
on every candidate VI returned 0x3E8 "not in a state compatible". The working hypothesis was that
two `Revert` calls, timed out and killed earlier, still occupied the serialized VI-Server/UI-thread
queue (NI forums: ActiveX runs through the UI thread; abandoned requests can hang it).

A LabVIEW restart cleared it completely (COM answering in ~5 s afterwards, cold load included).
The user granted standing restart permission at that point.

**Two earlier notes were corrected by the restart:** `Revert` does **not** hang on broken dirty VIs
(0.1 s on a healthy server — the earlier hangs were the wedge itself, misattributed), and the
project's "never restart LabVIEW because COM hangs; it is always a hidden dialog" rule turned out
to have a real exception.

## GUI lesson banked

A single click selects one wire **segment**, and Delete removes only that segment — leaving broken
remnants while the **Wire count stays unchanged** and the VI silently breaks. This bit twice in one
session (the op's `Diagram out` wire was destroyed by mistake both times; `revert` recovered it
both times). The reliable sequence is: click → screenshot-verify the marching ants → Delete →
`remove_bad_wires` → re-check counts and ExecState.
