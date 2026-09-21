# ATTACK this claim — two gates failed in `tools/bench/diag_c64_connect_v2.log` and I say both are bugs in my own harness, not in the route

## The claim you must try to REFUTE

> "Run 1 of `tools/bench/diag_c64_connect_v2.py` (log `tools/bench/diag_c64_connect_v2.log`, `BGRUN END rc=1
> after 74s`) failed exactly two gates, and BOTH are defects in the diagnostic harness itself, not evidence
> against the build route or against anything the run measured. (1) `P_c the census finds at least one node
> carrying a terminal named 'Is Broken?'` failed with `0 found` because I matched the PANEL INDICATOR's label
> `Is Broken?`, while the property ITEM's short name ON THE NODE is `Broken?` — the census printed in the same
> log shows node `#242 Property Node` with terminals `(4,'UID','SRC',660)` and `(5,'Broken?','SRC',676)`.
> (2) `C_1b no existing def was removed, and exactly connect_nested_v2 was added` failed listing EVERY def in
> the file as 'added', because `git show HEAD:tools/gscript.py` returned empty output, so the HEAD def-set was
> empty and the set difference was the whole file; the additivity fact was nonetheless measured correctly by
> the sibling gate `C_1`, which passed with `git diff --numstat` = `56 added / 0 deleted`. Therefore the fix is
> (a) accept the spellings `Broken?` / `Is Broken?` / `IsBroken`, (b) use a cwd-relative pathspec
> `git show HEAD:./tools/gscript.py`, and (c) nothing else about the run's design needs to change."

## What the run was doing, so you can attack the premise and not only the conclusion

The task (judgement's decision, `docs/cycle27-plan.md` Pre-decided 53(d⁷)) is to build
`claudeDev\OpConnectNested_v2.vi` ADDITIVELY on the byte-unchanged donor `claudeDev\OpConnectNested_v1.vi`
(md5 `b7a1bb56…`) with the embedded `Wire.Is Broken?` (property id 6371004) readback REMOVED, then run a
PAIRED v2-vs-v1 idempotent-connect test on two scratch duplicates of `claudeDev\D1_s3a_focus_ind.vi` in ONE
LabVIEW session. Background: `docs/NAMES.md:912-929` records that reading `Is Broken?` perturbs the target's
`ExecState`; cycle 62 measured `ExecState` 1 → 0 after an idempotent connect that created no wire at all.

Run 1 reached the census and stopped at the fatal `P_c`. The census it printed (top-level diagram of the
byte-copy of the donor, 21 nodes / 38 wires / 7 Property / 1 Invoke / 20 ControlTerminal) shows the readback
chain to be:

- `#241 Property Node`: `(0,'reference',snk,572) (1,'reference out',SRC,0) (2,'error in (no error)',snk,0)
  (3,'error out',SRC,630) (4,'Name',SRC,609) (5,'Wire',SRC,620)`
- `#242 Property Node`: `(0,'reference',snk,620) (1,'reference out',SRC,0) (2,'error in (no error)',snk,630)
  (3,'error out',SRC,739) (4,'UID',SRC,660) (5,'Broken?',SRC,676)`
- `#399 Clear Errors.vi`: `(4,'error in (no error)',snk,739)`
- `#757 Invoke Node` (`Terminal.Connect Wire`): `(0,'reference',snk,572) … (6,'Wire Source',snk,969)
  (3,'error out',SRC,1027)`

So wire **w572** carries the sink-terminal reference to BOTH `#241.reference` AND the Invoke `#757.reference`.

My plan for run 2, which you should also attack: delete ONLY `#242` — its wires **w620, w630, w660, w676,
w739 first, by uid, then the node by uid** — under a safety rule fixed before the run (a wire is deletable
only if every terminal on it is on a doomed node, or is a SOURCE that stays, or is a ControlTerminal SINK
that stays, or is an ERROR-IN sink on a node that stays), and then RE-WIRE `#241`'s `error out` (t3) straight
into `#399 Clear Errors.vi`'s `error in (no error)` (t4) with `connect_terminals`, so the error chain
survives. `#241` is KEPT because the same rule refuses w572 (the Invoke still needs it), which means v2 still
performs the `Terminal.Wire` and `Terminal.Name` reads — only the `Wire.UID` + `Wire.Broken?` reads go.
Then `ExecState`, `save` (which refuses a broken VI), restart, cold reopen, and the paired test.

## Already ruled out (do not spend your answer on these)

1. "Use `remove_bad_wires` / `remove_bad_wires_scripted` / `gui_save` / `allow_broken=True`" — all forbidden
   by the brief and blocked by a static gate; not on the table.
2. "Delete `#241` as well by deleting w572" — that wire feeds the Invoke that does the actual work.
3. "Edit the static gate, or set `CYCLE_GUARD_OFF` / `PEER_GUARD_OFF`" — never.
4. "Do not build v2 at all" — the route is judgement's decision, taken above my level this cycle.

## What I want from you

1. The STRONGEST reason the claim is WRONG — in particular, is there any reading of run 1's two failures under
   which something REAL (not a harness bug) was caught, and I would be papering over it by widening a string
   match and fixing a git pathspec?
2. Attack the run-2 plan structurally: after `#242` and its five wires are gone and `#241.error out` is wired
   into `#399.error in`, what is the strongest reason `ExecState` will NOT be 1 at the save point, or will not
   be 1 on a COLD reopen? Name the failure mode, not a feeling.
3. Is deleting `#242` alone actually sufficient to remove the `Wire.Is Broken?` READ, given that `#241` stays
   and still evaluates `Terminal.Wire`? If `#241` staying could itself perturb `ExecState`, say what evidence
   would show that and what the cheapest test is that needs NO new op and NO save.
4. A THIRD explanation of run 1's `P_c` failure beyond "wrong string" and "the reader is not there", which my
   run-2 design would NOT distinguish.
5. What would FALSIFY the claim, and the cheapest discriminating test I could add to the SAME diagnostic.

Answer against the files in this project directory; you may read them. Do not ask me to confirm anything.
