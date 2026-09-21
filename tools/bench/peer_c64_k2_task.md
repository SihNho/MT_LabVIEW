# ATTACK this claim. Do not confirm it.

## The record

A build script, `tools/bench/diag_c64_s3b_row1.py`, ran to completion and wrote
`tools/bench/diag_c64_s3b_row1.log`: 51 checks passed, one failed. The failing check is `K2`, a census read
on the finished file after LabVIEW was restarted and the file re-opened cold.

Expected: `Node 631, Wire 1905, ControlTerminal 116, Local 9`.
Measured: `Node 631, Wire 1906, ControlTerminal 116, Local 9`.

Only the wire count differs, by exactly one.

What the run did, in order, to a copy of an existing VI:

1. deleted one whole wire object (wire census 1905 -> 1904)
2. created one local-variable object bound to an existing front-panel indicator
3. relocated that local onto the nested diagram where its destination lives
4. joined the local's source terminal to the freed destination terminal. Check `E` recorded
   `wire_delta == 1`, wire census `1904 -> 1905`, and check `E2` recorded ONE wire uid (23502) present at
   BOTH ends
5. deleted the stray object the joining operation leaves behind, by uid
6. saved an intermediate file, then called a helper whose job is to feed that SAME already-existing indicator
   from a second source terminal, then saved the final file

Step 6's helper is `wire_indicators` at `tools/gscript.py:1756`. **Its own docstring, at
`tools/gscript.py:1771-1772`, states: "NO new Wire object is created (a branch joins an existing wire), so a
wire-count check cannot verify success."** The expectation in check `K2` was written from that sentence.

After step 6 the source terminal carried wire uid 23526 (check `H`), and a reverse census of everything
touching wire 23526 (check `I`) found EXACTLY ONE source — the intended source terminal, named `x .and. y?` —
and exactly one sink: the intended panel control, uid 23555.

The same docstring, at `tools/gscript.py:1765-1769`, warns of a specific failure: "Each source terminal MUST
ALREADY BE WIRED: WI branches the indicator onto the wire attached to the source terminal. An UNWIRED source
makes it extend an unrelated wire instead -> 'This wire connects more than one data source' and the target
breaks."

The finished file opens cold at execution state 1 (check `K`), and a later ordered read of the new
destination wire reports it not broken (check `L`).

## THE CLAIM YOU MUST TRY TO DESTROY

"`K2` failed because the EXPECTATION was mis-written, not because anything is wrong with the artefact.
`wire_indicators` created one new wire object here rather than branching an existing one; the documented
'no new Wire object' sentence is what is wrong. The count 1906 = 1905 - 1 (deleted) + 1 (the join) + 1 (the
indicator feed) is the correct number, and the file is sound."

## Already ruled out (do not spend your answer on these)

- "The file is broken" as a blanket claim: it opens cold at execution state 1 after a full restart, and the
  four md5-pinned originals are byte-unchanged.
- "The extra wire is the deleted one coming back": the deleted wire's uid is 10799; the two wires involved
  after the edits are 23502 and 23526, both newly minted.
- "A reference leak or a stray object": references opened 23, closed 23, live 0; the one stray object the
  joining operation left was located, its full terminal table read, and it was deleted by uid.

## What I want back

1. The strongest reason the claim is WRONG — in particular, any reading in which a wire count of 1906 is
   evidence that the indicator was fed by EXTENDING AN UNRELATED WIRE (the documented failure) rather than by
   a legitimate new connection.
2. A DIFFERENT explanation of the same +1 that I have not considered.
3. What observation would falsify the claim.
4. The cheapest discriminating test that separates your explanation from mine — runnable, not an argument.

Be concrete about what "branch" means in LabVIEW's scripting object model: does joining a terminal that is
already wired add a Wire object or not, and can a single logical net be represented by more than one Wire
object? If the answer is that a net of one source and one sink should be exactly one Wire object, say what
the second one is.
