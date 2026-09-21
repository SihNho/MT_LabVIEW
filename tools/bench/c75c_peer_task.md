# ATTACK this claim — stage M3a-3 run 2, the Row D deferral

You are the adversary. Do not confirm anything. Find the strongest reason the claim below is WRONG, give an
alternative explanation for the same observation, say what would falsify each, and name the CHEAPEST
discriminating test that could be run read-only against the LabVIEW machine.

## Context (only what is needed; no VI files are attached and none may be requested)

A LabVIEW block diagram is being restructured stage by stage. Stage M3a-3 had TWO rows to re-source:

* **Row C** — a `Global` node `#7202` (`Global motor pos.vi`), terminal 0 `'Focus position'`, was fed from an
  OLD loop's `RightShiftRegister #4256` OUTER terminal (wire 4859). It had to be re-sourced onto the NEW loop's
  `RightShiftRegister #23895` OUTER terminal.
* **Row D** — a `FlatSequenceInnerTunnel #7468`, today fed by wire **7506** whose source is the OLD
  `RightShiftRegister #4334` OUTER terminal, had to be re-sourced onto the NEW `RightShiftRegister #23868`.

Both sinks were ALREADY WIRED, so each row is a delete-and-rebuild, not a branch.

Run 1 deleted a wire and then the rebuild raised (`OpConnectNested_v2.vi` was not on disk), leaving the Global's
terminal 0 BARE — a dropped consumer. That artefact was rejected.

Run 2 (`tools/bench/build_d1_m3a3_run2.log`, recipe `tools/recipes/build_d1_m3a3.py`, static-checked by
`tools/bench/c60c_astcheck.py`) wrote Row C only and reports 26 gates pass / 2 fail. Its first failing line is:

    FAIL  P0 ROW D's SINK RESOLVED - wire 7506 appears EXACTLY ONCE on FlatSequence #681's terminal table
          (the PREDICTION, written before the read)   FAILED PREDICTION - FlatSequence #681 did not resolve

## THE CLAIM TO ATTACK

> Because wire 7506 did not resolve to exactly one terminal on `FlatSequence #681`'s terminal table, the sink
> address for Row D was unknown, so DEFERRING Row D (writing nothing, deleting nothing, leaving wire 7506 and
> `FlatSequenceInnerTunnel #7468`'s old source intact) was the correct handling; the resulting file
> `D1_s3b_m3a3_20260922_081056.vi` is therefore a sound bed for the next stage, and the two FAIL lines are a
> pre-decided deferral rather than a defect.

## Attack it on at least these axes

1. **Is "did not resolve" even the right reading of the observation?** A `FlatSequenceInnerTunnel` is owned by a
   frame, not by the sequence node; a tunnel's OUTER terminal may not appear on the structure node's
   `Terminals[]` table at all, or may appear more than once (one row per frame). If so, the prediction was
   mis-written and the gate measured the wrong table — which makes "the sink is unresolvable" a false
   conclusion drawn from a true reading.
2. **Can a deferral be SILENTLY DESTRUCTIVE?** Row C's delete-and-rebuild ran in the same script and the same
   LabVIEW session. Name every mechanism by which writing Row C could disturb wire 7506, tunnel `#7468`, or the
   old register `#4334` — border-tunnel creation, terminal-index drift across a structure border, an implicit
   Remove Bad Wires, a register OUTER terminal changing identity — such that "we wrote nothing for Row D" is
   true of the script and false of the file.
3. **Is the artefact a sound bed?** The file is broken by design (`ExecState` 0) and is never run. What could be
   wrong with it that NO count, NO `ExecState` read and NO source-terminal walk would show?
4. **The independent check now being written** re-reads, on a scratch copy and anchored at UIDs only:
   the one source terminal on the Global's net; whether `#4256`'s OUTER is bare; whether wire 7506 still carries
   `#7468` as a sink with `#4334` OUTER as its source; whether the two earlier M3a-2 rows are untouched; whether
   `#23868` is still bare. **Name what that check would MISS**, and the one extra read-only measurement that
   would catch it.
