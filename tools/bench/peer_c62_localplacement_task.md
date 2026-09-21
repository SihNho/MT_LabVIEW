# Failed prediction: a Local Variable created by `VI.Create:Local Variable` lands on the TOP-LEVEL diagram, and wiring it into a sink inside a While loop left the VI broken

## The prediction (written before the run, `tools/bench/diag_c62_s3b_build.py` docstring, step 3)

> `connect_nested_v1(Local SOURCE -> #10407 tN SINK)` — **`ExecState` 1 EXPECTED here**; a bare source terminal
> and a bare indicator are both legal, so once the Case selector's sink is fed the VI is legal again, and that
> is the row's guaranteed saved artefact.

## What was observed (`tools/bench/diag_c62_s3b_build.log`, `BGRUN END rc=1 after 104s`, 20 pass / 5 fail)

The target is a copy of `claudeDev\D1_s3a_focus_ind.vi` (a working copy of a large acquisition VI; the ORIGINAL
is never touched). All numbers below are read off the machine in that run.

1. cold open `ExecState` **1**; `#637` (WhileLoop) **59 terminals / 48 wired**; `ControlTerminal` census **116**.
2. `delete_object(target,'Wire', idx of uid 10799)` → `gone [10799]`, `ExecState` **1 → 0**. That one Wire object
   was a three-terminal net: `#10407` **t0** (Case-structure SELECTOR, name `''`, sink) · `#10686` **t0**
   `'x .and. y?'` (`And`, SOURCE) · front-panel indicator control **23555** `'Automatic Error Handling'` (sink).
   All three are now bare.
3. `OpCreateLocalRead_v0.vi` with `Write?` = False, bound to front-panel row 115 (`'Automatic Error Handling'`,
   indicator): error cluster `(False, 0, '')`, `Local` census **8 → 9**, new Local **#23507**. Read back with
   `node_terms`: **ONE** terminal, NAME `'Automatic Error Handling'` (hex
   `4175746f6d61746963204572726f722048616e646c696e67`), `is_source` **True = READ** — the rule-1a gate PASSED.
4. 🔴 **THE LOCAL'S OWNER, READ OFF THE MACHINE: `TopLevelDiagram` #536, diagram index 0, `Nodes[0]`.** The sink
   `#10407` is `Nodes[24]` of `Diagram #639`, traverse index 46, and `#639` is owned by `WhileLoop #637`.
5. `connect_nested_v1(target, sink_diag=46, sink_node=24, sink_term=0, src_diag=0, src_node=0, src_term=0)`
   (drives `OpConnectNested_v1.vi`, `Terminal.Connect Wire` 6349C03 with two independent diagram ladders):
   **`wire_delta` 3, op error column `''`**, i.e. the write reported success and made THREE wire segments —
   LabVIEW created the border tunnels itself, as this op's own documentation says it does.
6. Readbacks: `#10407` t0 `wire 0 → 23508`, all four error columns 0. Local #23507 t0 `wire 0 → 23601`,
   all four error columns 0. **The two uids differ** — expected for a cross-boundary wire in several segments,
   so this is not by itself evidence of failure.
7. 🔴 **`ExecState` = 0 at the save decision, so nothing was saved and the working copy was removed.**
   `ExecState` timeline for the row: `1` (cold open) → `0` (after the wire delete) → `0` (after the Local was
   created, unwired) → **`0` (after the connect)**.
8. At the stop: `#10686` t0 `'x .and. y?'` wire **0** (`wire_err` 1055 = bare); panel control 23555 wire **0**
   (`wire_err` 1055 = bare); `#10407` t0 wire **23508**.

No `Wire.Is Broken?` was read at any point (it is measured to perturb `ExecState` in this project, so the ordered
pass is only ever run after a save; the row never reached a save).

## Already ruled out

- **Not the binding**: the Local's own terminal reads back with the exact label it was created from and
  `is_source` True (READ), which is the direction the sink requires.
- **Not a silent decline of the write**: `wire_delta` 3, op error `''`, and both ends report non-zero wires
  with zero error columns.
- **Not "the differing wire uids mean the wire is wrong"**: `OpConnectNested_v1`'s own record says a
  cross-boundary connection is several segments and the sink and source uids differ.
- **Not a perturbing read**: no `Is Broken?` call happened anywhere in this run before the reading.

## The claim you are asked to REFUTE

**CLAIM:** the `ExecState` 0 after step 5 is caused by the two OTHER terminals that the same Wire delete left
bare — the source `#10686` t0 `'x .and. y?'` and the front-panel indicator control 23555 — and NOT by anything
about the Local, the cross-diagram connection or the tunnels LabVIEW created; i.e. the sequence would read
`ExecState` 1 if the indicator were re-fed before the state is sampled.

Give the strongest reason this claim is WRONG. In particular:

- In LabVIEW, is an **unwired front-panel indicator terminal** on a block diagram a broken-VI condition, or a
  legal one? Is an **unwired output terminal of a primitive** (`And`'s `x .and. y?`) a broken-VI condition?
- Does wiring a **Local Variable that sits on the top-level block diagram** into a terminal **inside a While
  loop** through automatically created tunnels produce a legal VI at all, or does that construction itself have
  a defect (for example: a tunnel on a loop border whose other side is unwired, or a Local read that LabVIEW
  refuses to route across a structure border)?
- Is there an alternative explanation that fits ALL eight observations above better?

Name what would FALSIFY your explanation, and name the CHEAPEST discriminating test — one that can be run
read-only or on a throwaway scratch copy, with the verbs this project already has:
`delete_object`, `connect_nested_v1` (`OpConnectNested_v1.vi`), `wire_indicators` (`OpWireInd_v0.vi`, branches an
EXISTING indicator onto the wire already attached to a source terminal), `OpCreateLocalRead_v0.vi`,
`node_terms_uid`, `node_labels`, `panel_wiring`, `report_all`, `count`, `exec_state`.
There is no verb in this fleet that deletes ONE BRANCH of a Wire object, and `create_indicator` /
`connect_ctl` are both measured out on this VI (they address the TOP-LEVEL `Nodes[]`, which is empty here).
