# Failed prediction P6d (cycle 68, tools/bench/q_m4_iterlocal.log) - attack the explanation

Context: LabVIEW 2026 VI Scripting over COM, on a dated scratch copy of a VI whose ExecState is 1 on open.
Steps (all by scripted op VIs, never run the target VI):
1. `OpCreateLocalRead_v0` with Write?=True creates a WRITE Local for indicator 'current image number' on the
   top-level diagram -> ExecState 0 (an unwired write Local; expected).
2. `OpMoveIn_v0` moves the Local into a While-loop body diagram (#639). Node census 633 -> 634 across the
   move (one extra node appears).
3. `OpConnectFromWire_v0` branches wire 3268 (source = the loop's iteration terminal #644) onto the Local's
   input. Op errors empty, `Wire.Is Broken?` False, wire delta 0. Node census rises by one again.
Prediction P6d: ExecState 1 after step 3. Observed run 1: ExecState 0 (`q_m4_iterlocal.log:78`).

Run 2 (`tools/bench/q_m4_iterlocal_run2.log`), identical steps plus a purge after step 2 and after step 3 that
deletes any NEW node with ZERO wired terminals (the fleet's documented 'stray Invoke' each OpMoveIn/OpConnect*
call mints, `tools/stagekit.py:513-524`): each purge deleted exactly one 6-terminal, 0-wired node (census
634 -> 633, `run2.log:52-55`, `:103-106`); ExecState after the final purge = 1 (`run2.log:107`); Remove Bad Wires
on the result removed 0 wires, ExecState 1 (`:114`). Control arm: an unwired READ Local on the same indicator ->
ExecState 0 (`:120`).

Our explanation: run 1's ExecState 0 was caused by the unpurged stray Invoke node(s) minted by the op calls
(an unwired Invoke method node with a required refnum input breaks the VI), i.e. a defect of our script's
omitted cleanup, not of the wiring. The next build (a boolean shift register + Not + And + Wait on the same
body, via move_in/connect ops) relies on "purge after every move_in/connect => ExecState reflects only the
intended edit".

Already ruled out: the connect itself (Is Broken? False, RBW removes 0, ExecState 1 once the strays are gone).
