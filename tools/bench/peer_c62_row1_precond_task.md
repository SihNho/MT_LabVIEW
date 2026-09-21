# THE FAILED PREDICTION

**Predicted** (our plan document, Pre-decided 53(d), written by the judgement session): S3b's per-row
operation would execute as *delete the whole `Wire` object → **`create_indicator` on the now-bare SOURCE
terminal** → create a Local Variable in READ mode bound to that new indicator → wire the Local's source into
the freed Case-Structure sink*, and would leave a saved VI at `ExecState` 1.

**Observed** (`tools/bench/diag_c62_s3b_rows.log`, 15 pass / 5 fail, `BGRUN END rc=1 after 131s`): the second
step has no address. Our `create_indicator(target, node_index, terminal_index)` wrapper drives an op whose
ladder is `VI → Block Diagram → Nodes[] → Terminals[] → Terminal.Create Indicator (6349C02)`, so `node_index`
indexes the **top-level** block diagram's `Nodes[]`. Measured on the bed:

- the source is `#10686` (`'And'`), owner `Diagram #639`, **Nodes[25] of traverse diagram 46**, terminal 0
  `'x .and. y?'` (`is_source` True), carrying wire 10799 before the delete (log :99).
- the **top-level** diagram (`#536`, traverse index 0) — `node_labels` lists **0 nodes** (log :101). Not "the
  source is missing from it": the top-level `Nodes[]` of this VI is EMPTY, everything living inside a flat
  sequence frame. So no top-level index exists for anything.
- Three independent throwaway scratches, each after deleting wire 10799 (which bares `#10407` t0, `#10686` t0
  and the panel indicator's terminal, `ExecState` 1 → 0):
  - `connect_ctl(panel_index=115, node_index=25, terminal_index=0)` → **error 1055 … Method Name: Connect
    Wire**, no wire (log :30-31).
  - `create_indicator(node_index=25, terminal_index=0)` → a **modal dialog**, dismissed by the watchdog after
    8 s; `ControlTerminal` census 116 → 116, nothing created (log :52-54).
  - `wire_indicators(node_index=102 (Traverse "Function"), src_terms=['x .and. y?'],
    indicator_names=['Automatic Error Handling'], diagram_index=46, node_class='Function')` → the wrapper
    RAISED *"target BROKEN after wiring"*, **but the machine shows a wire WAS made**: `#10686` t0 went
    0 → **23499** and the old indicator's panel row went 0 → **23499** (log :76-84). `ExecState` stayed 0 —
    and at that moment the Case Structure's selector `#10407` t0 was still bare, which on its own breaks the
    VI.

So the stage stopped before the delete on the real bed: nothing saved, the copy removed, four md5 pins
unchanged, refs 23/23/0-live.

# WHAT WE ALREADY RULED OUT — do not repeat these

- **Our own toolkit has no branch-removal verb** (census of all 165 defs). Deleting the whole `Wire` bares
  all three terminals; measured twice in an earlier cycle and three more times here.
- A separate API-fact search says LabVIEW 2018+ has **`Wire.Disconnect Terminal`, method ID 6370C0D**
  (`archive/peer/2026-09-21-c62-branch-disconnect.md`). We have NOT built or tested it; treat it as unverified.
- `move_in` (top-level → nested) is a proven verb here for `ControlTerminal`s; `OpConnectNested_v1` wires
  `(diagram, node, terminal)` → `(diagram, node, terminal)` pairs and scored 9/9 on real rows; a
  `ControlTerminal` is **not** a member of `Diagram.Nodes[]`, so those two verbs cannot address a panel
  object's terminal.
- A top-level node wired into a node inside the While Loop would create a border tunnel, which our rules
  forbid for this step (a while-loop output tunnel delivers one value at loop end).

# WHAT TO ATTACK

You are asked to **refute**, not to agree. Specifically:

1. Is our conclusion — "`create_indicator` cannot be used on a source that lives on a nested diagram, so
   53(d)'s route is unexecutable as written" — actually wrong? What is the strongest reason it is wrong?
2. Give an ALTERNATIVE EXPLANATION of the three observations above (e.g. the empty top-level `Nodes[]`
   reading is itself an artefact of how we address diagrams; the 1055 means something else; the modal dialog
   hid a different fault).
3. What single observation would FALSIFY our conclusion?
4. Name the CHEAPEST DISCRIMINATING TEST we can run next, on a throwaway copy, with the verbs we already
   have. In particular: is the `wire_indicators` result (a real wire 23499 from the bare source to the OLD
   indicator, with `ExecState` 0 explained by the still-bare Case selector) evidence that the OLD indicator
   can simply be re-connected — and how would we separate "the wire is good, the VI is broken only because
   the selector is bare" from "wire_indicators made a bad wire"?

Do not propose changing our plan; propose measurements.
