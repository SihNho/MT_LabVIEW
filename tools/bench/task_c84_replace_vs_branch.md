ATTACK the claim below. It is about to drive a real build against a real VI, so the job is to find the
reason it is WRONG, not to improve it.

## The failing record

`tools/bench/diag_c83_connect2x2_r2.log` (rc=1, 27 pass / 14 fail, 151 s) and its script
`tools/bench/diag_c83_connect2x2_r2.py`. The first failing line the gate names is:

    **FAIL**  R0 the border terminal's own `Wire` property read returned NO error  wire_err 1055

and every cell that DELETED wire 7506 first returned
`error 1055: Invoke Node ... | Method Name: Connect Wire` together with
`error 1055: To More Specific Class in UID to GObject Reference.vi`.

## The machine facts, all from that log (cite them back if you dispute them)

* `:56`, `:66` — cells R0 / R0b: wire 7506 ALIVE, the Invoke on the terminal named by the INDEX TRIPLE
  (`WhileLoop #23032`, `Nodes[21]`, `Terminals[1]`, owner `RightShiftRegister #23868`), the
  `FlatSequenceInnerTunnel #7468` `LeftTerm` `#7488` handed in as `Wire Source`. Result:
  `term_uid=7488 uid_back=7468`, NO error, `UID 2 = 7506`, the border terminal went `0 -> 7506`,
  `wire_delta 0`, `is_broken True`. Poison ON and poison OFF were identical.
* `:77`, `:89`, `:101`, `:113` — cells R1 / R2 / R3 / R4: wire 7506 DELETED first. All four return
  `error 1055` at the Invoke AND at `To More Specific Class in UID to GObject Reference.vi`,
  `term_uid=0 uid_back=0`, `UID 2 = 0`, border wire stays 0, `wire_delta 0`, one junk `Invoke` minted.
  R3/R4 are the SWAPPED op (`:36-46`: nets `w572 #239.'element'` and `w1337 #183.'LeftTerm'` exchanged
  onto the Invoke, the two other consumers re-branched, Remove Bad Wires removed 0, ExecState 1).
* `:54`, `:64`, `:75`, `:87`, `:99`, `:111` — in EVERY cell the border terminal's own `Wire` property
  read carries `wire_err: 1055` while that terminal is BARE, and 0 once it is wired.
* Earlier, `tools/bench/build_harness_copyloop2.log:31-40` records `Terminal.Connect Wire` 6349C03
  CREATING a wire between two BARE terminals (wire census 9 -> 10, both ends on wire 346,
  `ExecState` 0 -> 1).
* `tools/gscript.py:2521-2523` states: "an already-wired source is BRANCHED ... an already-wired SINK is
  not safe (LabVIEW re-routes and the VI breaks) — wire only unwired sinks."

## THE CLAIM UNDER ATTACK

1. Delete-then-connect is dead for this sink: deleting wire 7506 makes `FlatSequenceInnerTunnel #7468`
   itself unresolvable, so no configuration that deletes first can work.
2. Every connect-with-the-wire-ALIVE cell ever run put the Invoke on the SOURCE terminal, which is why it
   BRANCHED (net 7506 ending with three source terminals) instead of replacing.
3. Therefore the configuration NEVER RUN — the Invoke sitting on the SINK terminal (the FSIT `LeftTerm`
   `#7488`, which is `is_source=False`) with wire 7506 LEFT ALIVE, the loop border terminal handed in as
   `Wire Source` — will REPLACE the existing wire, because in LabVIEW's editor wiring a new source onto an
   input that is already wired replaces the wire that was there.
4. The border row's `wire_err: 1055` on a BARE terminal means `wire: 0` there is the error path's DEFAULT,
   so that column is a refusal rather than a measurement, and the FSIT's own faces (read through
   `OpFsInnerTunnelTerm_v0`) must be used instead.

## What to do with it

State the STRONGEST reason claim 3 is wrong. Name an ALTERNATIVE explanation of the R0/R0b branch that does
not predict a replacement in the swapped-with-wire-alive cell. Say what OBSERVATION would falsify claim 3
before anything is saved. Name the CHEAPEST discriminating test. Specific questions worth your search:

* Does `Terminal.Connect Wire` (method id 6349C03) REPLACE the existing wire on an already-wired sink
  terminal, REFUSE, BRANCH, or leave the VI broken? Is there NI or community documentation of its behaviour
  on a wired input? Is `Auto Route?` relevant to any of those outcomes?
* Does `tools/gscript.py:2521-2523` ("an already-wired SINK is not safe — LabVIEW re-routes and the VI
  breaks") refute claim 3 outright, and if so what evidence stands behind that line?
* If the method DOES replace, what happens to the OTHER end of the displaced wire — the old source
  `RightShiftRegister #4334` — does LabVIEW delete the old wire, leave a broken stub, or re-route it? A
  broken stub would raise the diagram-wide broken-wire count, which is the gate this build is about to use.
* Is `is_source=False` on `#7488` actually the right way to decide which side is the SINK for this method,
  given that a `FlatSequenceInnerTunnel`'s left terminal sits on the OUTER diagram?

You have read-only access to the project directory and the web. Cite `file:line` or a URL for every factual
claim. "Cannot tell from here" is an acceptable answer for any sub-question; say so rather than guessing.
