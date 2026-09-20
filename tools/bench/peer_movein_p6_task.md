# Failed prediction P6 — where node `#48` lives, and the three framings built on top of it

This is a LabVIEW VI Scripting project. We are restructuring a copy of a large tracking VI by moving
groups of block-diagram nodes into newly created While loops. All addressing is by object uid.

## THE FAILED PREDICTION

Gate **P6** in the diagnostic `tools/bench/diag_movein_set.py` asserted that node **`#48`**
(`-Inc reference`, the call to `ASI_adjust focus-subvi.vi`) is owned by **`Diagram #686`**.

## THE OBSERVATION

The machine reported **`#48`** and **`#3529`** (`- Inc (PgDn)`, a `ControlReferenceConstant`) both on
**`Diagram #639`**, which is the BODY of **`WhileLoop #637`** — the frame acquisition loop, one nesting
level deeper than `#686`.

Evidence line: `tools/bench/diag_movein_set.log:57` —
`  **FAIL**  P6 #48 is on Diagram #639 with 7 wired terminals; #3529 t0 '- Inc (PgDn)' carries wire 4833  sink owner 639 wired 7; src rows [(0, '- Inc (PgDn)', 4833)]`

## ALREADY RULED OUT — do not re-litigate these three

1. **A stale or index-based address.** The owner was read **by uid** through the `owner_of` op, not by an
   array index into any `Nodes[]` list.
2. **A transcription slip in the report.** `#639` reads identically in the before-census and the
   after-census of the same run.
3. **`#639` and `#686` being one diagram under two uids.** The census lists them as distinct `Diagram`
   objects with different `Nodes[]` sets.

## WHAT YOU ARE ASKED TO ATTACK — the framings, not the measurement

The measurement above is settled. What follows is reasoning built on top of it, and it is what should be
taken apart.

**(1) The dismissal.** The project first recorded P6 as "a mere drafting error with no consequence" and
ruled no review was owed. That reasoning has since been struck out. Argue the case that the mis-prediction
was NOT harmless — that believing `#48` sat on `#686` has consequences still embedded in the plan that
followed.

**(2) The node-set claim (plan item 37(g)).** The plan asserts that ALL 7 of `#48`'s cut wire rows are
**internal to the "1.5 FOCUS" node set** — that set being `#3529`, `#3560`, `#3447`, `CaseStructure
#10407`, and two shift-register pairs, `#4334/#4344` (VISA) and `#4256/#4274` (position) — and that
**none** of `#48`'s sources stays behind on `#686`. Cited to `docs/d1-build-plan.md:250, :306, :330-332,
:340, :359-360`. If that claim is wrong, the next build stage (S3) moves a set whose wires cannot be
restored, and the stage cannot be saved (a broken VI is refused by our save path). Attack the claim;
the cited lines are readable in the project directory.

**(3) The destination claim (plan item 37(h)).** The plan asserts that newly created loop `a` =
`WhileLoop #23032` (body `Diagram #23058`), which is owned by `Diagram #686`, is a legal destination for a
node set that currently lives one level DEEPER — inside `WhileLoop #637`'s body `Diagram #639`. The
supporting `move_in` measurements were taken moving nodes from `#639` into `#23058`. The question to
attack: is moving OUT of one loop's body and INTO a sibling loop's body on the outer diagram the same
operation those measurements exercised, or does that framing hide a difference (tunnels, nesting depth,
data-flow legality) that the measurements never touched?

## MEASURED FACTS YOU MAY USE

- `move_in` takes ONE node per call and SEVERS every wire on the moved node, in either order. Measured on
  the pair `#3529 → #48` (wire 4833): after moving the source, `#3529` went 1 wired terminal → 0; after
  moving the sink, `#48` went 7 → 0; the wire object 4833 remained in the whole-VI `Wire` list with 0
  terminals.
- The whole-VI `Wire` count never changed (1905 → 1905 → 1905) across both moves, so a wire census cannot
  detect a cut. Every re-wiring gate therefore counts WIRED TERMINALS.
- After the moves the VI read `ExecState` 0 and the save was refused, so that attempt left no artefact.
- `#3529` is a `ControlReferenceConstant`, not a function node.

## WHAT THE ANSWER MUST CONTAIN

- The strongest reason the S3 shape (move the whole 1.5 FOCUS set into `#23032`'s body and re-wire, one
  script, one save) is wrong.
- An alternative explanation for how the P6 mis-prediction arose, other than "someone typed the wrong uid".
- What observation would falsify that alternative.
- The cheapest discriminating test.

## HARD CONSTRAINT ON ANY TEST YOU PROPOSE

**No new op may be built.** (Project rule, standing user order of 2026-09-18.) Any proposed test must be
expressible with the existing op fleet: uid-addressed owner reads, node/terminal censuses, wire-source
reads, `move_in`, loop creation, `ExecState` reads, and file-level md5/size probes. A test that requires a
new reader — for example anything needing `Terminal.DataType` — is out of scope and should be named as such
rather than proposed.
