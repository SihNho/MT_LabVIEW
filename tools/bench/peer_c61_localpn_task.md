# Failed prediction: a `Local`-class Property Node makes the VI illegal the instant it is created

LabVIEW 2026 (26.3.1f1), Windows 10, VI Scripting over ActiveX/COM. Everything below is a reading taken
off the machine in ONE run today (`tools/bench/diag_c61_localdir_write.log`, 38 pass / 1 fail).

## The prediction that failed

PREDICTED: after adding a `VI Server:Local` Property Node to a copy of a working op VI, wiring its
`reference` input from a `Control -> Create:Local Variable` Invoke Node's output terminal, and creating a
front-panel control on the node's `Write?` input, the VI would read `ExecState == 1` (legal) and could be saved.

OBSERVED: `ExecState` went **1 -> 0 the moment `build_property('VI Server:Local', [('6355401', True)])`
returned**, and stayed 0 through every later step. The VI was therefore never saved.

## The readings, verbatim

On a scratch duplicate of a large application VI (`Property` census 106):
- `build_property('VI Server:Local', [('6355401', True)])` -> node #23493 created, creator error column `''`,
  its i=4 row `{'i': 4, 'name': 'Write?', 'is_source': False, 'wire': 0}`. **ExecState 1 -> 0.**
  `delete_object` the node again -> **ExecState 0 -> 1**, census 106 -> 107 -> 106.
- The same with `('6355400', True)` (`CtrlName`, a SINK): **1 -> 0**, delete -> **1**.
- The same with `('6355401', False)` (`Write?`, now a SOURCE): **1 -> 0**, delete -> **1**.
- The same with `('6355400', False)` (`CtrlName`, a SOURCE): **1 -> 0**, delete -> **1**.
- CONTROL: `build_property('VI Server:VI', [('242', False)])` -> i=4 `'Def Err Handling'`, SOURCE.
  **ExecState 1 -> 1.** Delete -> 1. So the creator itself does not break VIs; the `Local` CLASS does here.

On a throwaway copy of the op VI `OpCreateLocal_v0.vi` (9,688 B, `Property` census 4, `Wire` census 9):
- `ExecState` 1 at open.
- `build_property('VI Server:Local', [('6355401', True)])` -> node #339 at Nodes[9], error column `''`,
  i=4 `{'name': 'Write?', 'is_source': False, 'wire': 0}`. **ExecState 1 -> 0.**
- `connect_terminals(sink = #339 'reference' i=0, src = Invoke #306 i=5 'Create Local' SOURCE)`:
  `wire_delta 1`, error column `''`, `Wire` 9 -> 10, new wire uid **390**, and the `reference` row afterwards
  reads `{'i': 0, 'name': 'reference', 'is_source': False, 'wire': 390}`. **ExecState 0 before and 0 after.**
- An ORDERED second pass through our `Wire.Is Broken?` (6371004) carrier on that same connection:
  **`Is Broken?` = False** on wire 390, `wire_delta 0`, op error `''`. So THAT wire is not broken.
- `create_control` on #339's `Write?` SINK -> one new ControlTerminal #496, label read back off the machine as
  `'Write?'`, plus wire #536. **ExecState 0 before and 0 after.**
- Nothing was saved; the copy was deleted; the donor is byte-unchanged.

The Invoke Node is `Control -> Create:Local Variable`, method id `6331C02`, six terminals:
`(0 reference sink, 1 reference out source, 2 error in sink, 3 error out source, 4 'Create Local' sink,
5 'Create Local' SOURCE)`. Terminal 4 was and is unwired; terminal 5 is the one we wired.

## Already ruled out (do not spend your answer here)

1. NOT the wire: `ExecState` was already 0 before any wire existed, and the wire we made reads `Is Broken? False`.
2. NOT the created control: `ExecState` was 0 before `create_control` and 0 after.
3. NOT the write/read mode and NOT the property id: all four `Local` combinations go 1 -> 0, while
   `VI Server:VI` id 242 on the same bed stays at 1; deleting the `Local` node restores 1 every time.

## What we want from you

Attack the diagnosis "a `Local`-class Property Node cannot legally exist on a diagram built this way, so this
route is blocked". In particular:

- The strongest reason that diagnosis is WRONG.
- An alternative explanation for `ExecState` 1 -> 0 that our four readings do not exclude (for example: what a
  Property Node whose class the creator wrote as a string, with an UNWIRED `reference`, actually is to
  LabVIEW's type checker; whether a `Local` refnum wire from `Create:Local Variable` is the type this node's
  `reference` expects at all, given `Is Broken?` reads False; whether `ExecState 0` here means "broken VI" or
  something weaker, and what would distinguish those).
- What observation would FALSIFY your alternative.
- The single cheapest discriminating test we could run next, using only: creating/deleting nodes, wiring
  terminals by index, reading terminal tables (`name`, `is_source`, `wire`), `Wire.Is Broken?`, `ExecState`,
  front-panel control creation, and the LabVIEW error list if you know a scripting route to it over ActiveX.

Public documentation on `Local Variable` refnum class, `Local.Write?` / `Local.Control Name` property ids
(6355401 / 6355400), and on what makes a Property Node itself break a VI, is welcome — cite it.
