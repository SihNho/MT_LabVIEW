ATTACK this claim. I want it REFUTED, not confirmed. If it survives, say exactly which part survives.

## THE FAILED PREDICTION

`tools/bench/diag_c62_s3b_movein.log` — `BGRUN END rc=1 after 178s`, GATES 30 pass / 4 fail. The gate that
failed first and matters is `B1_f ExecState == 1 after the connect  0`.

The cycle's plan (`docs/cycle27-plan.md` Pre-decided 53(d⁗)) predicted that the previous dispatch's
`ExecState` 0 was caused by PLACEMENT — the new Local landing on `TopLevelDiagram #536` so the connect built a
cross-diagram TUNNELLED path (`wire_delta` 3, two different wire uids) — and that moving the Local onto
`Diagram #639` first would make `ExecState` read 1. **The placement was fixed and the VI is still broken.**

## WHAT THE MACHINE SAID THIS TIME (all from `tools/bench/diag_c62_s3b_movein.log`)

- `:19` cold open of the bed `D1_s3a_focus_ind.vi` (md5 `eef91c1d…`): `ExecState` **1**.
- `:38` after `delete_object(Wire[uid 10799])` (`gone [10799]`): **0** (expected).
- `:43` after `OpCreateLocalRead_v0.vi(Write?=False)` created Local **#23507**, `Local` census 8 → 9: **0**.
- `:51-:62` `move_in(#23507 → Diagram #639, traverse index 46 re-read live, position (120,4000))` returned
  3447, error `''`; it left ONE junk `Invoke` #9317, purged. **PLACEMENT: `TopLevelDiagram`#536 diagram 0
  `Nodes[0]` → `Diagram`#639 diagram 46 `Nodes[73]`.** Rule-1a readback AFTER the move: ONE terminal, NAME
  `'Automatic Error Handling'`, `is_source` **True** (= READ); `Local` census still 9. `ExecState` **0**.
- `:66-:76` `connect_nested_v1(target, sink_diag=46, sink_node=24, sink_term=0, src_diag=46, src_node=73,
  src_term=0)` → **`wire_delta` 1** (not 3), op error `''`. `#10407` t0 now reads
  `{'i':0,'name':'','is_source':False,'wire':23508,'errs':[0,0,0,0]}` and Local #23507 t0 reads
  `{'i':0,'name':'Automatic Error Handling','is_source':True,'wire':23508,'errs':[0,0,0,0]}` — **ONE wire uid
  23508 at BOTH ends, all four error columns 0 at both ends.**
- `:79-:81` `#637` (WhileLoop) census IMMEDIATELY after the connect: **59 terminals / 48 wired = the
  baseline**, i.e. no tunnel and no border object was created. `ControlTerminal` census 116 → 116.
- `:82` `ExecState` after the connect: **0**.
- `:67` the op's own embedded readback printed `op readback {'UID': 10407, 'Name': '', 'UID 2': 0,
  'Is Broken?': False}` — note **`UID 2` is 0**, so that `Is Broken?` reading is not on wire 23508.
- `:88` the save was attempted unconditionally and `gscript.save` raised
  `RuntimeError: refusing to save a BROKEN VI - SaveInstrument blocks forever on one`, so the file on disk is
  byte-identical to the bed (md5 `eef91c1d…`) and carries none of the edits. No artefact exists.

## THE CLAIM I AM FORMING (attack it)

**The remaining cause is the now-SOURCELESS indicator: wire 10799's net had three terminals — `#10407` t0
(the Case SELECTOR, sink), `#10686` t0 `'x .and. y?'` (source) and panel indicator 23555 `'Automatic Error
Handling'` (sink). Deleting the wire bared all three. Step 4 re-fed only the selector, from a Local that READS
23555, and 23555 itself now has no writer — so the diagram contains a Local read whose control is never
written, and THAT is what holds `ExecState` at 0 until step 6 re-feeds the indicator. The brief's own order
(Local first, indicator last) therefore cannot reach a legal state at step 4 at all, and the step-4
`ExecState == 1` precondition for step 6 is unsatisfiable by construction.**

## THINGS TO TRY TO BREAK IT

1. Is a Local READ of an indicator that has no writer actually a broken-VI condition in LabVIEW, or is it
   legal? Search NI/LabVIEW Wiki. If legal, my claim dies and you must offer the real cause.
2. `archive/peer/2026-09-21-c62-localplacement.md` established that a BARE terminal does not break this VI
   (it opens at `ExecState` 1 with eleven bare terminals on `#637` alone) and that what the delete broke was an
   unwired REQUIRED INPUT — the Case selector. That required input is now fed, with clean error columns. So
   what is left? Name it.
3. Could the Case structure's selector now be TYPE-incompatible — e.g. its cases are not Boolean, or the
   Local's datatype is not what `'x .and. y?'` delivered — even though all four error columns read 0 and
   `wire_delta` is 1? What reading would show that, given `docs/NAMES.md:902-918` says `Wire.Is Broken?`
   PERTURBS `ExecState` and this project therefore runs it only last?
4. Could `ExecState` simply be STALE — a reading LabVIEW has not recomputed — as
   `archive/peer/2026-09-21-c62-localplacement.md` suggested ("save unconditionally and judge by the COLD
   reopen")? Note the practical trap: `gscript.save` (`tools/gscript.py:2071-2074`) REFUSES at `ExecState` 0
   and its only broken-VI path is `gui_save`, a GUI action this project's rules ban here — so "judge by the
   cold reopen" is unreachable while the live reading is 0. If staleness is your explanation, name a reading
   that settles it WITHOUT a save and WITHOUT a GUI click.
5. Did `move_in` itself damage something? It returned 3447 and left one junk `Invoke` (#9317) which was
   purged by uid. `tools/recipes/build_d1_routeb_v0.py:48-55` reports that after a `GObject.Move` every
   terminal of a moved STRUCTURE reads `is_source` FALSE — here the Local read `is_source` True after the
   move, so that effect did not appear. Is there another residue a `Local` move leaves?

## ALREADY RULED OUT (do not spend the answer on these)

- Tunnelling / cross-diagram wiring: `wire_delta` 1, one wire uid at both ends, `#637` at 59/48.
- A wrong or stale diagram index: `diag_index(#639)` is re-read off the machine before the move, before the
  connect and before `wire_indicators` (the previous review's §4.1 repair).
- A wrong Local direction: read back twice, before and after the move, as NAME `'Automatic Error Handling'`,
  `is_source` True (= READ).
- The Local being duplicated by the move: `Local` census 9 before and after.
- A missing or ambiguous indicator: control uid 23555, label read off the machine, exactly one panel row.

## OUTPUT

Start with one of `The claim is REFUTED` / `The claim SURVIVES` / `The claim SURVIVES IN PART`. Then the
strongest reason it is wrong, an alternative explanation, the observation that would falsify it, and the
CHEAPEST discriminating test that needs no save and no GUI action.
