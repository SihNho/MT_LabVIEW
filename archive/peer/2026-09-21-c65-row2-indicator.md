# c65-row2-indicator

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $4.3470  in 26 / out 45302 / cache-create 227699 / cache-read 1749335  (662s, 24 turn(s))
- **date:** 2026-09-21 15:38:56
- **outcome:** ANSWERED (664s)
- **why asked:** MANDATORY failed-prediction review (`guard_peer`). `tools/bench/diag_c65_s3b_row2.log`
  (`BGRUN END rc=1`) is the newest failing log: the brief pre-scripted `wire_indicators(node_class='Function')`
  to re-feed row 2's existing `'index'` indicator from `#10757` t1 `'element'`, predicting `#10757` would
  appear in the Traverse `'Function'` census. It did not — `#10757` is an `Index Array` primitive
  (`Diagram #639 Nodes[27]`), absent from all 183 `'Function'` rows — so the step did not run and
  `D1_s3b_row2_20260921_151221.vi` saved with the indicator fed by nothing. The review was asked to ATTACK the
  replacement route cycle 65 material #2 part B was about to run.
- **verdict:** REFUTED-THE-ROUTE (route not changed here — quoted to judgement under `OPEN:`; the two
  mechanical corrections were implemented in `tools/bench/diag_c65_s3b_row2b.py` before the run)

## Question

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


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled in this session (correct for a read-only reviewer), so the review is here.

# The route is refuted — and the row was already solved, six hours earlier, with the call you are abandoning

## 1. The strongest reason it is WRONG: the sink is not addressable, and the thing that *is* addressable is the wrong object

`connect_nested_v1` can address an endpoint only as `Diagram[d].Nodes[n].Terminals[t]` — that is its entire signature and it sets nothing else (`tools/recipes/build_opconnectnested_v1.py:418-431`). An indicator's block-diagram terminal is a `ControlTerminal`, and this project has already written down, twice and independently, that `Nodes[]` does not reach it:

- `docs/d1-route-b-plan.md:239` — *"`Z/dZ` uid 47, a `ControlTerminal`, which `Diagram.Nodes[]` does not list (**R3**)"*
- `tools/gscript.py:1342-1343` — *"Control/indicator terminals are class Terminal, not Node, and this cannot reach them"*
- and the run's own net walk proves it operationally: three members of net 10990, found by **two** enumerations — the two nodes from the 74 scanned on `#639`, the indicator only from the 116 **panel** rows, reported as `'where': 'panel control uid 23525', 'terminal': None` (`tools/bench/diag_c65_s3b_row2.log:121`).

So the honest outcome of the route is its own abort clause: a cycle spent rediscovering R3.

**Now the part you asked for — how it could look sound while the data path is wrong.** The entry on `Diagram #639`'s `Nodes[]` whose terminal name reads `'index'` is not the indicator. It is the **Local `#23523` at `Nodes[74]`** (`…row2.log:496-498`) — the one step [5] already wired, at that exact index. And your three acceptance criteria — ExecState 1, one new wire, one uid at both ends — **never read the front panel**. They would pass identically for a wire into the Local, into a different type-compatible node, or into another indicator's terminal, while control 23525 stays bare. The op's own readback reports the sink's uid and name only, and its own comment warns the readbacks may pre-date the wire (`build_opconnectnested_v1.py:444-451`). The single measurement that separates "the indicator is fed" from "something called index is fed" is `panel_wiring()` row 114 `wire != 0` — a reader you already have and already used at step [1] (`…row2.log:126`), and which the route omits.

## 2. A different explanation of the census miss — it is a class *name*, and your own machine logged it

`#10757` is missing from the `'Function'` census because it is not a `Function`:

- `tools/bench/cycle59_s3a_recipe.log:34` — `uid 10757 … self **'IndexArray'**#10757`
- `…:119` — `#10757 class membership [{'class': '**IndexArray**', 'index': 20, 'members': 47}]`
- `docs/NAMES.md:331` — `Function 161 · … · **IndexArray 47** · GrowableFunction 40 · CaseStructure 37`
- `#10686` is an `And`, a fixed-size primitive, and was wired as `Function[102]` (`cycle59_s3a_recipe.log:290`)

This matches NI's own account that array primitives are not plain `Function`s — DFGray (NI): *"Use GrowableFunction for the vi object class and Array Subset for the style. GrowableFunction covers a multitude of nodes"* ([NI forums](https://forums.ni.com/t5/LabVIEW/what-vi-object-class-for-Array-Subset/td-p/2765400)); on this COM path the machine's own name for it is `IndexArray`.

**So the route is not addressing the wrong object — it is drawing the wrong conclusion from the right one.** The helper was never unusable; it was passed one wrong word. The plan propagated the error: `docs/d1-build-plan.md:356` literally prescribes `node_class='Function'` for `#10757`.

## 3. The observation that falsifies the route's premise

`report_all(target,'IndexArray')` contains uid 10757 — **already observed**, at index 20 of 47 members (`cycle59_s3a_recipe.log:119`), and followed immediately by `wire_indicators(IndexArray[20], ['element'] -> ['index'], diagram_index=46)` returning an empty error, taking that same indicator from wire `0 → 10990`, ExecState 1 either side, no tunnel on `#637` (`…:126-131`). That is this row's wiring, passing, on 2026-09-21.

## 4. Cheapest discriminating test — one call on a scratch copy, no new verb

`wire_indicators(copy, node_index=<10757 in report_all(copy,'IndexArray')>, ['element'], ['index'], diagram_index=46, node_class='IndexArray')`, then read `count(Wire)` and `panel_wiring()[114]['wire']`.

- **Wire 1906 → 1907 and panel row 114 wire ≠ 0, ExecState 1** → the op is a plain Connect Wire, the "source must already be wired" clause is a false generalisation from one test where the source happened to be wired, and row 2 closes with the call the plan always specified — 1907 being exactly what gate 55(f) demanded.
- **the VI breaks** → the docstring is right, and row 2 has *no built route*. That is a finding for the user, not a cue to improvise one.

## The one thing genuinely open — and it is not what you think

Whether `wire_indicators` works on a **bare** source has never been measured here. S3a branched onto a live net (Wire delta 0, `cycle59_s3a_recipe.log:128`); row 2 needs a wire created. Your own documents contradict each other on it: `gscript.py:1765-1770` says it cannot, while `docs/d1-build-plan.md:346-357` — written the same day — plans `wire_indicators` *precisely after* `move_in` has left `#10757` unwired. And gate 55(f) predicted **+1 wire**, i.e. a fresh connect, not a branch. Two minutes settles what has now cost a cycle.

Do not look for a single-branch disconnect as an escape: there is no `Terminal.Disconnect` in `docs/vi-server-ids.json` (`tools/recipes/probe_move_into_v0.py:17-19`), and a temporary sink is permanently unauthorised (`docs/d1-route-b-plan.md:228`). Delete-and-rebuild is forced, which makes the bare-source behaviour of `wire_indicators` the critical path, not a side issue.

**What the evidence does not settle:** whether `Traverse 'Function'` excludes `IndexArray` by inheritance or by exact-class matching. `docs/NAMES.md:641` records `Function → GrowableFunction`, which would imply exact matching, but `IndexArray`'s place in the hierarchy is recorded nowhere here and NI publishes no full hierarchy. Operationally irrelevant: `IndexArray` resolves the node, `Function` does not, both measured.

**Two smaller things worth fixing regardless.** Gate `I` is meaningless — it walked "the net of wire 0", and 0 means *no wire*, so it collected eight unrelated bare terminals and called them sources (`…row2.log:332-335`). And step [7] was scheduled last, after the Local was committed, so the only step that could fail was placed where its failure leaves the deliverable open rather than where it would be caught first.

## Sources

(extract from answer)

## What was done with it

Outcome **ANSWERED** (664 s, opus/effort max, $4.3470) — a real review, so the `guard_peer` block on
`tools/bench/diag_c65_s3b_row2.log` is discharged. Disposed in full, by this material session (cycle 65
material #2), which may implement mechanical corrections but may NOT change the route.

### A. IMPLEMENTED HERE (mechanical, no route change)

1. **"Gate `I` is meaningless — it walked the net of wire 0"** (§"Two smaller things", citing
   `…row2.log:332-335`). ACCEPTED AND FIXED. `tools/bench/diag_c65_s3b_row2b.py` `reverse_census()` now
   REFUSES a census of wire uid `0`/`None` and records the refusal instead of reporting eight bare terminals
   as a net.
2. **"Your three acceptance criteria never read the front panel … the single measurement that separates 'the
   indicator is fed' from 'something called index is fed' is `panel_wiring()` row 114 `wire != 0`"** (§1).
   ACCEPTED. `diag_c65_s3b_row2b.py` already carried gates `K4` (reverse census must find exactly ONE source
   and its sink must be **panel control 23525**) and `K4c` (the indicator's own panel row must carry the new
   wire); the review confirms they are the load-bearing ones rather than `ExecState`/wire-count.
3. **"The entry on `Diagram #639`'s `Nodes[]` whose terminal name reads `'index'` is not the indicator — it is
   the Local `#23523` at `Nodes[74]`"** (§1). ACCEPTED as a real trap. The script's B1(iii) selector already
   requires `class == 'ControlTerminal'` (so the `Local` cannot be chosen) — and a new measurement was ADDED:
   gate `A4c` intersects the whole-VI `ControlTerminal` census with Diagram #639's `Nodes[]` uid list and
   reports the result, so the review's **R3** claim ("`Diagram.Nodes[]` does not list a `ControlTerminal`",
   `docs/d1-route-b-plan.md:239`, `tools/gscript.py:1342-1343`) is MEASURED on this machine rather than
   assumed in either direction. If R3 holds, B2 is not attempted and the run stops after B1 — which is exactly
   the abort clause the brief wrote.

### B. QUOTED TO JUDGEMENT, NOT ACTED ON (a ROUTE CHANGE — this session may not take it)

The review's core proposal is to abandon the direct-connect route and re-run the helper under a corrected
class name. Verbatim, its §3 and §4:

> `report_all(target,'IndexArray')` contains uid 10757 — **already observed**, at index 20 of 47 members
> (`cycle59_s3a_recipe.log:119`), and followed immediately by `wire_indicators(IndexArray[20], ['element'] ->
> ['index'], diagram_index=46)` returning an empty error, taking that same indicator from wire `0 → 10990`,
> ExecState 1 either side, no tunnel on `#637` (`…:126-131`). That is this row's wiring, passing, on
> 2026-09-21.

> `wire_indicators(copy, node_index=<10757 in report_all(copy,'IndexArray')>, ['element'], ['index'],
> diagram_index=46, node_class='IndexArray')`, then read `count(Wire)` and `panel_wiring()[114]['wire']`.

> **Wire 1906 → 1907 and panel row 114 wire ≠ 0, ExecState 1** → the op is a plain Connect Wire, the "source
> must already be wired" clause is a false generalisation from one test where the source happened to be wired,
> and row 2 closes with the call the plan always specified — 1907 being exactly what gate 55(f) demanded.
> **the VI breaks** → the docstring is right, and row 2 has *no built route*. That is a finding for the user,
> not a cue to improvise one.

And its remaining open point, also quoted rather than acted on:

> Whether `wire_indicators` works on a **bare** source has never been measured here. S3a branched onto a live
> net (Wire delta 0, `cycle59_s3a_recipe.log:128`); row 2 needs a wire created. Your own documents contradict
> each other on it: `gscript.py:1765-1770` says it cannot, while `docs/d1-build-plan.md:346-357` — written the
> same day — plans `wire_indicators` *precisely after* `move_in` has left `#10757` unwired.

> Do not look for a single-branch disconnect as an escape: there is no `Terminal.Disconnect` in
> `docs/vi-server-ids.json` … and a temporary sink is permanently unauthorised
> (`docs/d1-route-b-plan.md:228`). Delete-and-rebuild is forced, which makes the bare-source behaviour of
> `wire_indicators` the critical path, not a side issue.

> **What the evidence does not settle:** whether `Traverse 'Function'` excludes `IndexArray` by inheritance or
> by exact-class matching. … Operationally irrelevant: `IndexArray` resolves the node, `Function` does not,
> both measured.

Not acted on, and no plan document edited: the brief for this dispatch names the route (`connect_nested_v1`
plus the 55(c) purge) and forbids choosing or recommending another. The route was run as written, with its own
abort clause intact, and this block is carried to the judgement session under `OPEN:`.
