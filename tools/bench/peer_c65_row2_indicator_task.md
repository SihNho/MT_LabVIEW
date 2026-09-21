# ATTACK this route. Do not confirm it.

## The prediction that failed

A build script (`tools/bench/diag_c65_s3b_row2.py` -> `tools/bench/diag_c65_s3b_row2.log`, `BGRUN END rc=1`)
was written to finish one row of a signal-transport change inside a copy of a large LabVIEW VI. Its last step
was pre-scripted as a call to a helper, `wire_indicators(node_class='Function')` at `tools/gscript.py:1756`,
whose job is to feed an EXISTING front-panel indicator from a named source terminal of a node. The node it had
to work from is identified in this project by its object uid, `#10757`.

**The prediction: `#10757` would appear in that helper's node census, which the helper takes over the object
class `'Function'`.**

**What was measured instead:** `#10757` is an `Index Array` primitive. In the object model it lives at
`Diagram #639`, `Nodes[27]`, label `'Index Array'`, with three terminals — t0 `'array'` (wire 121),
t1 `'element'` (a SOURCE, currently BARE), t2 `'index'` (wire 10947). It is **absent from all 183 rows** of the
`'Function'` census on that VI, while the node row 1 of the same job used (`#10686`, an `And` primitive) WAS
present in that census. The helper therefore had nothing to act on and the step did not run.

**The consequence on disk:** the saved file `D1_s3b_row2_20260921_151221.vi`
(md5 `7a11818387fe44a764c2ff169b1dd6f7`) is sound in every other respect — it re-opens cold, after a full
LabVIEW restart, at execution state 1; the earlier half of the row landed (a new local variable feeds the Case
structure `#10407`'s terminal t2 through one wire, one uid at both ends) — but the pre-existing indicator
labelled `'index'` (front-panel control uid 23525) is now **fed by nothing**. The transport chain is open at
its head.

## THE ROUTE I AM ABOUT TO RUN — destroy it

> Abandon `wire_indicators` for this row entirely. Instead connect `#10757`'s terminal t1 `'element'` (the
> SOURCE) **directly** to the block-diagram terminal of the EXISTING `'index'` indicator (the SINK), using the
> project's nested-diagram connect verb `connect_nested_v1`, with both endpoints addressed on the SAME diagram
> (`Diagram #639`, traverse index 46; source node `Nodes[27]`, source terminal 1; sink node = the indicator's
> own index in that same `Nodes[]` list, sink terminal = whichever of its terminals reads back as the sink).
> Then delete, by uid, the stray broken `Invoke` node that this verb is known to leave on the diagram it worked
> on, and only then read the execution state. Expect execution state 1, and one new wire object.

The route is conditional on one measurement taken first: if the indicator's block-diagram terminal does NOT
appear as an addressable entry in `Diagram #639`'s `Nodes[]` list, the run stops and changes nothing.

## Already ruled out (do not spend your answer on these)

- "The VI is broken / the earlier half failed": the bed file opens cold at execution state 1 after a restart,
  and an ordered not-broken read on the new wire returned False (not broken). Four md5-pinned predecessor
  files are byte-unchanged.
- "Just fix the helper to census a different class": the helper also requires that **the source terminal be
  ALREADY WIRED**, because it works by BRANCHING the wire attached to that terminal. `#10757` t1 is bare, so
  the helper's documented failure mode ("an unwired source makes it extend an unrelated wire instead -> 'This
  wire connects more than one data source' and the target breaks") would apply even if the census were fixed.
- "The stray `Invoke` node is a mystery": it was measured on two independent beds — six terminals, zero wired,
  every row carrying error 1055 — and deleting it by uid restores execution state 1, stably, across re-reads.
- "Use the GUI / open the panel / allow a broken save": all forbidden here and not on the table.

## What I want back

1. The strongest reason this route is WRONG. In particular: is connecting a bare SOURCE terminal directly to
   an indicator's block-diagram terminal, with both addressed through one diagram's `Nodes[]` list, a
   different operation in LabVIEW's scripting object model from what the helper would have done — and if so,
   in what way could the difference produce a file that LOOKS sound (execution state 1, one wire, one uid at
   both ends) while the data path is not the one intended?
2. A DIFFERENT explanation of why `#10757` is absent from the `'Function'` census while `#10686` is present —
   one that, if true, would mean the route above is addressing the wrong object or the wrong terminal.
3. What single observation would falsify the route's premise.
4. The cheapest discriminating test that separates your explanation from mine — runnable, not an argument.

Be concrete about LabVIEW's scripting classes here: what class does an `Index Array` primitive belong to, what
does a front-panel indicator's block-diagram terminal belong to, and does a terminal of that kind appear in a
`Diagram.Nodes[]` traversal at all? If it does not, say what the correct addressing is.
