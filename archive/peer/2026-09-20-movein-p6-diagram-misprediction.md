# movein-p6-diagram-misprediction

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $2.9725  in 26 / out 31578 / cache-create 131825 / cache-read 1554860  (434s, 23 turn(s))
- **date:** 2026-09-20 05:54:51
- **outcome:** ANSWERED (438s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

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


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

## 1. The single strongest reason the claim is wrong

**S3 as specified cannot reach `ExecState 1`, therefore cannot save, therefore leaves no artefact — because the 1.5 FOCUS set is not closed, and the project's own wire map says so in three places that 37(g) never consulted.**

37(g) tests closure on `#48`'s rows. `#48`'s 7 rows *do* close — I checked every one (`tools/bench/d1_rewire_sources.json:1920-2083`: t0←`#3529`, t1←`#3560`, t2←`#3447`, t3←SR `4334/4344` left-in, t4←SR `4256/4274` left-in, t5→`#10407` t5, t6→`#10407` t3). But closure of a *set* is over **every member's** rows, and `#10407` is a member:

| row | wire | other end | the map's own label |
|---|---|---|---|
| `#10407` **t0 — the case selector** (`"name": ""`) | 10799 | `#10686 'x .and. y?'`, diagram 43 | `"action": "cross-loop:1.2->1.5"` — `:1748-1773` |
| `#10407` t2 `Index of closest cal image slice, bead 2` | 10990 | `#10757 'element'`, diagram 43 | `"action": "cross-loop:1.2->1.5"` — `:1793-1818` |
| `#10407` t6 `position [internal units]` | 9113 | also `#12589` t1, which **stays on 1.1** | `:1892-1917`; `docs/d1-build-plan.md:307` |

`#10686` and `#10757` go to **1.2 — a loop that does not exist in S3**. So after S3's moves they are still inside `WhileLoop #637`, and three restorations must cross two loop borders. In LabVIEW that is not a wire: data passes out of a loop only *after the loop terminates*, which is why NI tells you to use a queue or notifier between parallel loops ([Transferring Data between Two Loops Running in Parallel](https://www.ni.com/docs/en-US/bundle/labview/page/transferring-data-between-two-loops-running-in-parallel.html), [Transfer Data Between Loops](https://www.ni.com/documentation/en/labview/latest/g-prog/transfer-data-loops/)). And the plan's intended mechanism for exactly these rows *is* a queue (`Q_focus` at `docs/d1-build-plan.md:250`, `Q_focusback` at `:307`) — which is **measured unavailable**: `queue_node('obtain')` refuses a diagram constant, a scalar ControlTerminal and a cluster ControlTerminal (error 1057), `OpCreateConstOnTerm_v0` is loop-body-only (error 1055), and Pre-decided 36 schedules the donor census **behind S3** (`STATUS.md:62`).

So the specification is circular on its face: *37(g)* says move the set **and re-wire it**; *36* says the only mechanism that can re-wire it waits until after. An unwired case selector is an unconditional broken-VI condition, so `ExecState 1` before the save is unreachable — and 37(g)'s own argument that "the stage is atomic because the machine makes it so" then guarantees the outcome: **no file**. That is the v3→v7 death for the fourth time, under a rule (CLAUDE.md, 2026-09-19) written to stop it. The batches of 10–15 rows are cosmetic: `ExecState` 0 + `allow_broken` False means no batch can leave an artefact (measured, `tools/bench/diag_movein_set.log:105-109`).

The one construction that *would* pass both stated criteria — tunnel out of `#637`, wire on `#686`, tunnel into `#23032` — restores the wired-terminal counts, compiles, and **changes the computation** (autofocus runs once after acquisition ends instead of per frame). Rule 1a is violated by the artefact that passes the gate. That is the real hazard in the pass criteria, not their strictness.

## 2. The dismissal was not harmless — the mis-prediction survives inside 37(g)

Believing `#48` sat on `#686` does not merely misname a diagram; it **changes which closure question gets asked**. On `#686`, the new loops' own parent, "does a source stay on `#686`?" is the right test and plain wires restore everything. On `#639` the right test is "does a source stay inside `WhileLoop #637`?" — and it does, three times over. 37(g)'s sentence *"**none** of its sources stays on `#686`"* is only *coherent* under the refuted origin; it is the old frame, sitting one line below the correction that retired it (`37(f)`, `STATUS.md:59`). None of its five citations (`d1-build-plan.md:250, :306, :330-332, :340, :359-360`) asserts closure — and `:250`, read whole, says the loop is *"woken by the 1-element `Q_focus`"*, i.e. the cited line **contradicts** the wire-it-up shape built on top of it.

A second consequence survives at one hop: `#48` t3's VISA session arrives from `LeftShiftRegister #4344`, whose *outside* terminal carries wire **4185 from a source on `#686`**, and whose right partner `#4334` sends wire **7506 out to `#686`** (`tools/bench/main_vi_shiftregs_v1.json:115-146`). So sources do stay on `#686`. And shift registers are not moved by the plan at all — `docs/d1-build-plan.md:365` and `docs/toolkit-capabilities.md:53-54` say they are **created** with `add_shift_reg`/`wire_sr`. Four of the nine "members" of the set that "moves" are objects with a different construction verb and a different wiring contract.

## 3. The destination claim — I concede the half you expected me to attack, and move the objection

Moving out of `#639` into `#23058` **is** what the measurements exercised (`diag_movein_set.log:61-98`; cycle 50's scaffold did the same, `STATUS.md:27`), and a CaseStructure has been measured to move **with its frame diagrams intact**, 12/0 (`docs/d1-build-plan.md:148, :188`). Nesting depth is not the hidden difference.

The hidden difference is that **both measured moves were of objects that own no diagram** — a `ControlReferenceConstant` and a `SubVI` — while `move_in`'s destination is addressed **by index**, not by uid: `move_in(target, uid, dest_diagram_index, position)` (`build_d1_v0.py:318`; `log:62, :82` — "Diagram #23058 **[index 22]**"). Index drift is already on the record: `#639` was the plan's `diagram_43` at step 0 (`d1-build-plan.md:279, :283`) and reads **index 46** after S2 (`log:41`). Relocating a structure relocates its frame diagrams inside that array. If it renumbers, every later `dest_diagram_index` in a one-script S3 is wrong — and the op **cannot tell you**: its echoed UID is not the moved object (both calls echoed 23035, loop a's scaffold Comparison). This is the mechanism `STATUS.md:63` already names as the strongest rival explanation for the ten v3→v7 deaths, and it is untested for diagram-owning objects. NI documents only `position` and `owner` for `GObject.Move` and says nothing about wires, structures or traversal order ([LabVIEW Wiki](https://labviewwiki.org/wiki/GObject_class/Move_method)) — so the vendor will not settle this either.

## 4. Alternative explanation of P6, other than a mistyped uid

**The plan gives the origin as an index and the destination as a uid, and the destination's uid is the only uid in the neighbourhood.** §5a's heading is *"Diagram 43 — the frame loop body"* (`:283`) — index, no uid anywhere. §3's 1.5 row is *"a NEW While loop on `Diagram #686`"* (`:250`) — uid, destination. The gate's constant is literally named `SIBLING_DIAG_UID = 686` (`tools/bench/diag_movein_set.py:94`), i.e. *"the diagram beside the new loops"*, and is then asserted as the **subject's owner** (`:294-297`). One symbol, two roles. That is a document defect reproduced by a script, not a keystroke — and it matters because S3 will resolve nine addresses from the same table, whose origin key `diagram_43` S2 already invalidated.

**What would falsify that alternative:** find `#639` named as the 1.5 set's origin anywhere in §3/§5a/§6 (the document was unambiguous, so the slip was local), or find `686` used in a destination role elsewhere in `diag_movein_set.py` with `639` used as the origin (the constant carried one role and P6 was a one-off). I find neither — `SIBLING_DIAG_UID` appears only at `:296` — but I did not grep every document, and that is a real limit on this claim.

## 5. Cheapest discriminating test

**T0 — free, no LabVIEW, decides the closure claim before any build.** Re-read `tools/bench/d1_rewire_sources.json` rows `uid: 10407` at `:1748`, `:1793`, `:1892` and count `"action": "cross-loop:*"` among the 1.5 members. 37(g) predicts 0; I predict 3. This file was on disk when 37(g) was written and the claim was checked against plan prose instead. If it reads 3, S3 is dead at zero cost and the next act is the decomposition the re-split trigger already demanded (`STATUS.md:23`) — with the honest choice made explicit: pull `#10686`/`#10757` in too, or defer 1.5 until a queue donor exists, or define an S3 with a zero-deficit set. The set choice, not the machine, is what makes the stage atomic.

**T1 — one ~100 s scratch run, existing ops only, no save** (same shape as the 101 s run already done), on a dated copy of `D1_s2_loops.vi`: (a) read the Diagram traverse array, record the indices of `#23058` and `#639`; (b) `move_in(#10407 → #23058)`; (c) **re-read both indices**; (d) `owner_of(#10407)` by uid + `Diagram` class count; (e) `move_in(#4344)` (a `LeftShiftRegister`) then `owner_of(#4344)`. Step (c) settles the one thing the two measured moves could not — whether a diagram-owning move moves the index space the op addresses by. Step (e) settles whether two of the nine members are movable at all. No save is attempted (it would be refused), so the scratch stays byte-identical.

**Out of scope, named:** anything requiring `Terminal.DataType` (the queue-donor typing question) is a new reader and forbidden (Pre-decided 2; `STATUS.md:62`), and `VI.Get Errors` 452 is unbuilt and likely unreachable over COM — which is exactly why every test above is an ownership/index read rather than an error read.

**Where the evidence does not settle it:** these logs cannot distinguish "the P6 uid was mistyped" from "the P6 uid was inherited from the destination column" — only §4's observations separate them. And they cannot tell you whether a tunnel-mediated restoration would read `ExecState` 1. It probably would. That is the danger in the pass criteria, not the reassurance.

**Sources:** [Transferring Data between Two Loops Running in Parallel (NI)](https://www.ni.com/docs/en-US/bundle/labview/page/transferring-data-between-two-loops-running-in-parallel.html) · [Transfer Data Between Loops (NI)](https://www.ni.com/documentation/en/labview/latest/g-prog/transfer-data-loops/) · [GObject class/Move method (LabVIEW Wiki)](https://labviewwiki.org/wiki/GObject_class/Move_method) · [GObject Move (ni.com API ref)](https://www.ni.com/docs/en-NR/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/move.html) (page served no method text on fetch — the Wiki is the usable citation).

## Sources

(extract from answer)

## What was done with it

**ACCEPTED IN PART — cycle 53 judgement session, 2026-09-20.** This discharges the mandatory
failed-prediction review that `docs/cycle27-plan.md` Pre-decided 37(f) declared owed. Four findings
adopted, one rejected as unsupported, one corrected by measurement.

**ADOPTED.**
1. **The mechanism of the P6 mis-prediction.** `docs/d1-build-plan.md:283` names the origin as an
   *index* ("Diagram 43") while `:250` names the destination as a *uid* (`#686`); the gate constant
   `SIBLING_DIAG_UID = 686` (`tools/bench/diag_movein_set.py:94`) was then asserted as the subject's
   owner at `:294-297`. "A document defect reproduced by a script, not a keystroke" is right, and it
   is 34(h)'s own lesson arriving a second time.
2. 🔴 **The finding that outweighs the rest: `move_in` addresses its DESTINATION by traverse INDEX,
   not by uid** — `move_in(target, uid, dest_diagram_index, position)`, `tools/recipes/build_d1_v0.py:318`.
   Relocating a structure relocates its frame diagrams inside that array, so in a multi-move script
   every later `dest_diagram_index` may be silently wrong **and the op cannot report it**. This is
   34(h)'s address-invalidation hypothesis — the leading explanation for the ten v3→v7 deaths —
   located in an op signature for the first time. The review's T1 was run this cycle as
   `tools/bench/diag_destidx_drift.py`.
3. **Shift registers are CREATED on the new loop, not moved.** `add_shift_reg`/`wire_sr`,
   `docs/d1-build-plan.md:402-403` ("Both SR pairs are re-created on the new loop") — verified
   independently this cycle, not taken on the review's word. Four of the nine "members" of the set
   that "moves" therefore have a different construction verb and a different wiring contract.
4. 🔴 **The rule-1a trap, which is the single most valuable line in this review.** The one
   construction that would satisfy every stated acceptance criterion — tunnel out of `#637`, wire on
   `#686`, tunnel into `#23032` — restores the wired-terminal counts, compiles to `ExecState` 1, and
   **changes the computation**: autofocus would run once after acquisition ends instead of once per
   frame. A green build would have shipped a behaviour change. Banned by name in Pre-decided 38.

~~**REJECTED — unsupported by the files it cites.** The claim that 37(g)'s *"none of its sources stays
on `#686`"* is false because `#48` t3's VISA session comes from a source on `#686` via `#4334/#4344`.
Measured against `tools/bench/main_vi_shiftregs_v1.json:113-146`, `diagram19.json:151-160` and the
netmap: wires **4185** and **7506** appear on `#686` **only as `#637`'s own outer terminals t11/t10**,
and no other node terminal on `#686` carries either — so the *source object* is unreadable from these
files and the claim is not established. Across all 17 cut rows the measured count of sources on
`#686` is **0** (`tools/bench/c53_row_class.json`). 37(g)'s sentence stands as far as the row table
can speak; the reviewer read a wire's presence as a source's presence.~~

🔴 **THAT REJECTION IS WITHDRAWN THE SAME DAY — I refuted a correct reviewer with a broken
instrument.** `archive/peer/2026-09-20-c53-netmap-terms-truncation.md` measured that `net_map` builds
its `nets` table inside a loop capped at `max_terms=40` with an `empties >= 3` early stop
(`tools/gscript.py:2549`, `:2557-2560`, `:2570-2572`), so **the netmap's `wires` table is truncated**
— Diagram 19 is missing all of `#637`'s i40–i58 wire ends (9051, 9000, 9649, 11253, 16421, 29006,
29122, 28392, 29081, 29106, 32583, 32344), which are *the border wires of the loop being rebuilt*.
The sentence above is a **negative** claim ("no other node terminal on `#686` carries either wire")
drawn straight off that table, and a truncated census cannot support one.

**STATUS OF THE CLAIM: UNRESOLVED, not rejected and not accepted.** The reviewer's finding is neither
proven nor refuted; it must be re-derived from `main_vi_nodeterms.json`, which is complete, before
anything is built on it. The count "sources on `#686` = 0" is marked UNSOUND in Pre-decided 38(b).
The strike-through keeps the withdrawn reasoning readable, per this project's convention.

**CORRECTED BY MEASUREMENT.** The review predicted **3** `cross-loop` rows among the 1.5 members
(`tools/bench/d1_rewire_sources.json:1748`, `:1793`, `:1892`). The measured number is **2** — `:1748`
(`#10407` t0 ← `#10686`) and `:1793` (`#10407` t2 ← `#10757 'element'`), both far ends planned for
row 1.2. `:1892` is **not** a cross-loop row: `#10407` t6 `position [internal units]` is a **source**
whose action label reads verbatim `to-sr`, far end `#12589` t1, which §11c
(`docs/d1-build-plan.md:398`) keeps on row 1.1. It is a real and unnamed gap — §6 gives it no
construction verb — but it is not the thing the review called it. Pre-decided 37(g)'s own prediction
of **0** cross-loop rows is likewise wrong; nobody on the record had this number right.

**DISPOSITION.** The review's verdict — that S3 as specified by 37(g) ends at `ExecState` 0 with no
saved artefact — is upheld on independent grounds (the recipe's own contract predicted the same, and
the prior-art review reached it from a third direction). `tools/recipes/stage_d1_s3_focus.py` was
**not launched**. S3 is withdrawn and re-cut as **Pre-decided 38**.
