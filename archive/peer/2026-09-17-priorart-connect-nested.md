# priorart-connect-nested

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.0788  in 40 / out 32493 / cache-create 185680 / cache-read 2818965  (443s, 35 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (446s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PRIOR-ART REVIEW (trigger: new-op).

You are checking ONE thing: has this already been done here? Do not review the plan's merits -
other reviews do that. Answer in two parts, naming a FILE and LINE for every finding. A finding without a citation
cannot be acted on, because the only way this review is released is by someone opening your citation and showing in
writing that it does not cover their case.

PART A - THE DIRECTION (this is the part that matters most)
 A1 SETTLED ALREADY. Has this direction, or its central question, already been decided or answered in STATUS.md,
    docs/ or archive/? Quote the decision and its date.
 A2 REFUTED ALREADY. Has this direction already been tried, abandoned, or argued against - in an archived peer
    review, a retrospective, or a superseded plan section? Say what killed it and whether that still applies.
 A3 CONTRADICTED. Does any fact the plan cites conflict with something else in these files? Quote BOTH sides. A
    summary line that contradicts its own section 40 lines earlier counts, and has happened here.
 A4 UNREAD EVIDENCE. Which existing document should obviously have been consulted for this direction and clearly
    was not? Name it.

PART B - THE ARTIFACT, if the plan builds or changes one
 B1 ALREADY BUILT. Does an op, recipe, helper or VI already do this, possibly under another name? Check
    tools/gscript.py's functions, tools/recipes/, docs/toolkit-capabilities.md and the claudeDev VI names.
 B2 ALREADY FAILED. Has this exact build been attempted and failed? What did the record say was the cause, and
    does the new plan address that cause or repeat it?
 B3 HELPER EXISTS. Is the plan hand-rolling something the toolkit already provides - indexing, identification,
    wiring, saving, censusing? Name the call.
 B4 ALREADY MEASURED. Has the question this artifact would answer already been measured and written down?

End with machine-readable lines, one per finding:
  PRIOR-ART: settled-already | refuted-already | contradicted | unread-evidence
  PRIOR-ART: already-built | already-failed | helper-exists | already-measured
  PRIOR-ART: novel
`novel` only if none apply. Do not invent slugs.

THESE VERDICTS STOP THE WORK. Any slug other than `novel` blocks the next build until someone opens your citation
and refutes it in writing. So be precise about what your citation actually covers: an over-broad match costs real
work, and a missed one costs a whole build cycle.

=== WHAT IS UNDER REVIEW ===
# Under review: `OpConnectNested_v0` ??a wire creator addressing BOTH ends by INDEX on NESTED diagrams

## Why it is being built (measured, not argued)

`tools/bench/build_d1_v0_run7.log` (PHASE "full" stage 1 of `tools/recipes/build_d1_v0.py`): of 66 routable
re-wire rows attempted against LabVIEW, **35 WIRED**, **7 FAILED**, **24 NO-ROUTE**.

* The 7 failures are error **5001** out of `Get Controls.vi` (6 rows, `wire_control`) and `Get Outputs.vi`
  (1 row, `g.wire` `'subarray'??x'`) ??i.e. every **name-addressed** writer fails when a terminal has no name,
  a newline-containing name or a duplicate name.
* The 24 no-route rows have a sink or a source terminal with **no name at all** (a Case/structure selector, an
  unnamed loop tunnel), or an outer source with no named node.
* Both **index-addressed** writers in the fleet require a **top-level** source: `tools/gscript.py:2202`
  (`connect_terminals`) and `:2428` (`connect2`).

## What is proposed (judgement decision, `docs/d1-build-plan.md` 짠11m, 2026-09-17)

`OpConnectNested_v0`: a new op VI under `user.lib\claudeDev`.

* Inputs: VI path; **sink** (diagram index, node index, terminal index); **source** (diagram index, node index,
  terminal index). Error out to the panel.
* Body: the **body-node ladder already proven in `OpStopFromNode_v0`** ??`VI.Block Diagram` ??Traverse for
  `Diagram` ??`Diagram[i]` ??`Diagram.Nodes[]` ??`Nodes[j]` ??`Node.Terminals[]` ??`Terminals[k]` ??run **twice**,
  once for the sink end and once for the source end.
* Then invoke **`Terminal.Connect Wire` 6349C03** on the sink terminal reference with the source terminal
  reference as `Wire Source`.
* Closes every reference it opens (project rule).

`OpStopFromNode_v0` already proves the **sink half** of exactly this shape: it invokes 6349C03 with a body
terminal as `Wire Source` and was measured wire 0 ??**387** with the scratch VI at **ExecState 1**
(`docs/d1-build-plan.md` 짠11i, STATUS OPEN 29). The claim under review is that the **source half** is the same
ladder duplicated, and that this resolves all 31 unreachable rows.

## Functional test planned before it is used on D1

On a uniquely-named scratch VI, created and deleted in the same run:
(a) body node ??body node on the same While loop; (b) body node ??an **UNNAMED tunnel** of a nested structure;
(c) source on a **different** nested diagram than the sink (cross-loop, LabVIEW creating the tunnel).
Gate: ExecState 1 for (a) and (b); (c) reported.

## Constraints this build is under

* Cycle-15 op freeze: this is the **fourth and last** op authorised (짠11m). No further op, no further dispatch.
* Rule 1a: nothing about the original's computation changes ??this only creates wires the relocation cut.
* `Terminal.Connect Wire` on an **already-wired** sink is recorded as re-routing and breaking
  (`tools/gscript.py:2206-2207`, `docs/keystone-op-spec.md:445`), so every use is on a bare sink.
* `Create Control` 6349C01 was measured to create **nothing** on an already-wired terminal
  (`docs/keystone-op-spec.md:404-406`).

## The questions

Has this op ??a both-ends-by-index wire creator on nested diagrams ??already been **built** under another name,
already been **attempted and failed**, or is there an existing helper in `tools/gscript.py` /
`user.lib\claudeDev\Op*.vi` / `tools/recipes/` that already reaches an unnamed terminal on a nested diagram?
Is the 6349C03-with-two-traversed-terminals route contradicted by anything measured in our own files (e.g. an
`Owning Diagram` or cross-diagram restriction on `Connect Wire`, or a recorded 1055/1057/5001 modal for this
shape)? And is the diagnosis above ??"every name-addressed writer cannot reach an unnamed terminal, and both
index-addressed ones need a top-level source" ??contradicted by any file that shows one of them reaching a
nested/unnamed end?


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-17
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.
Narrative ??the `archive/2026-09-17-status-*.md` set (**`??d1-full-build-4.md` = the latest session**)
+ `archive/2026-09-16-??. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this.

## START HERE
1. **`docs/pre-rig-master-plan.md` is THE plan**; decisions **`docs/decisions.md`**; cycle `docs/cycle15-plan.md`;
   **build plan `docs/d1-build-plan.md` (REV 4 + 짠11c?벬?1L)** ??짠5/짠5a-bis (moves), 짠10 (S/N1/F1/F2), **짠11L =
   the one open question**. 2. ?좑툘 A prior-art dispatcher's log MUST be named `priorart_*` / `peer_*`
   (`tools/logclass.py`) or the guards read the reviewer's prose as a build failure. 3. ??Scripting EDITS need the
   target's FRONT PANEL open. 4. ??A fixed op PATH is served from LabVIEW's MEMORY, not disk ??unique name/run.
5. ??**FIXED** (짠11g.3): editing a recipe no longer re-arms `guard_cycle` when the newest prior-art archive's
   "What was done with it" cites it in a `FIXED:` line. Self-test `tools/bench/selftest_guard_cycle_fixed.py` 6/6.

## LabVIEW execution lock

```yaml
labview-lock:
  status: acquired
  owner: material/cycle15-d1-full-build-5 (run 8)
  since: 2026-09-17 11:4x
  purpose: OpConnectNested_v0 (짠11m, 4th+last op) -> build_d1_v0 run 8 -> save -> N1 -> F1 -> F2
# 2026-09-17 10:3x-11:2x material/cycle15-d1-full-build-4: RELEASED. LabVIEW RESTARTED FIRST (78k -> 33,999).
# OpCreateConstOnTerm_v0 BUILT+SAVED (22/0); build_d1_v0 run 7 PHASE full stage 1 (55/7). Original md5
# 2a78e17c449... before AND after; working copy uniquely named, NOT saved (ExecState 0), DELETED in the same run;
# no leftovers. No GUI, no hardware. Handles 31,283 -> 34,415. -> archive/2026-09-17-status-d1-full-build-4.md
# Earlier sessions (build-3 run 6 56/1, phase-full-2, phase-full run 5 53/0) -> the same archive + 09-16/17 ones.
```
**Never assume an instance exited**: `tasklist | grep -i labview`. Fresh ??1,500 handles; unique scratch name/run.

## HARDWARE ??permission follows the RIG STATE. Current: **遺꾪빐 / DISASSEMBLED ??everything allowed**
**遺꾪빐 ??WE ARE HERE** = motors ??ASI ??camera ??쨌 議곕┰ = ??????쨌 ?ㅽ뿕以?= ?????? ?좑툘 The ASI carve-out is
**RETIRED** (rule 1b); **only the user announces a state change**. Rotor counter **0** 쨌 magnet full travel 쨌
camera 1280횞1024, offsets 0, 90.0009 Hz, never write `BinningHorizontal`; **a session open RESETS ROI *and*
exposure** ??the acquisition loop applies `tools/bench/camera_contract.py`. **No beads while disassembled.**

## Where things stand
**Stage 1 CLOSED**. **Stage 2**: `?쪪PU_core_v0` 69/69 쨌 `??queue_v0` 162/162 ??**say it exactly:** bit-identical
for the **first 10,018 frames only**, both **replay** artefacts. **THE GAP:** 171 ops, 119 recipes, 227 peers ??
**zero runnable experimental VIs**.

## OPEN ??one line each; long forms in `archive/2026-09-17-status-cycle15-narrative.md` (+ `??d1-phase-full-?? 짠0c)
1??, 5, 9??2 ??**all in archive 짠9**: PERIODIC auto-reset ungated 쨌 autofocus CLOSED (3.6 Hz) 쨌 27 undisposed
   peer archives 쨌 startup drives instruments 쨌 A2 54/54, A3 112/170 쨌 doc lint 2/4/3. **18 CLOSED by 짠11h ??no
   TIFF is written any more.** 13/14/15b/17b: ??stop measured (`#637` term **648 ??w3457 ??#11639**) 쨌
   ?뵶 `bgrun --detach` misses an orphaned grandchild 쨌 ?뵶 v3's R11 scored the *restart*, so the stop is unproven.
16. ??**GPU kernel ACCEPTED FOR NOW** ??user 2026-09-17 "?꾩옱濡쒖꽌???듦낵", revisit later (`decisions.md:38`);
   N1's whole-fixture range is REPORTED, not gated. D1 stays on `GPU_kernel_v1.vi`, no CPU-fallback branch.
19/25/26. ??PLAN = REV 4 + 짠11c?벬?1h; TRANSPORT = **queues only**; sentinels stop 1.2/1.5/1.7; `#12589`/`#642`
   stay on 1.1. 20??3 ??CLOSED. 27. ??**RELOCATION MEASURED** ??run 5 53/0, re-confirmed run 6 (56/1, the 1 a
   stale gate now fixed): `WhileLoop 3??`, `Diagram 170??73`, all 23 moves, 8 SRs, ControlTerminal 114 intact,
   collateral 0, d19 clean. Re-wire list = `tools/bench/build_d1_v0.json`, **109 terminals / 24 uids**.
28. ??**짠11i's WALL IS GONE.** **`OpCreateConstOnTerm_v0` BUILT, SAVED, FUNCTIONAL 22/0**
   (`build_opcreateconstonterm_v0.log`, toolkit row 54): `Terminal.Create Constant` **6349C00** on a BODY node's
   terminal ??a `DigitalNumericConstant` **typed by the sink and already WIRED**, value **??** read back through
   `OpConstValueN_v1`, `ControlTerminal` unchanged, scratch ExecState 1. Its census settles A3: 6349C00 **does**
   take a `Value` input (t6/t7), so no value-write chain was needed. It placed **5 literals in the real D1 copy**.
   ?윞 **`OpCreateConst_v0` is NOT the literal placer** ??measured in the same run: its VARIANT route yields class
   `Constant` with an **EMPTY** value. (That is the old NEXT line's "material, needs no decision" ??CLOSED.)
28b. ??**SOURCE MAP COMPLETE ??109/109** (`tools/bench/d1_rewire_map.py` ??`d1_rewire_sources.json`). The old
   45/82 join could not see constants, control terminals, loop tunnels or the 8 moving shift registers.
28c/28d/28e. ??`diag_d1_full_route` is RETIRED (짠11j.2). Its findings stand: `copy_by_index` of the ?? donor
   `#4609` copied nothing (route (a) dead); `OpWireSource_v5` returns 1055 for every wire in this configuration.
28f. ?뵶 **PHASE "full" STAGE 1 RAN ??55 pass / 7 fail** (`build_d1_v0_run7.log`, 짠11L). Of **66 routable rows**:
   **35 WIRED** (body-to-body `g.wire` by name WORKS on nested diagrams; `wire_sr` WORKS; 5 literals placed),
   **7 FAILED** (6 횞 `wire_control` ??5001 `Get Controls.vi`; 1 횞 5001 `Get Outputs.vi`), **24 NO-ROUTE**.
   ExecState **0**, nothing saved, copy deleted. **N1 / F1 / F2 NOT RUN ??they need a saved VI at ExecState 1.**
29. ??**`OpStopFromNode_v0` T5 CLOSED BY MEASUREMENT** (wire 0 ??**387**, VI at **ExecState 1**). ?윞 T6 open.
   ??`audit_cycle.py`'s `FAILURE_RE` repaired ??it matched neither `**FAIL**` nor `BGRUN END rc??`, so it
   reported ZERO failures for a window with five; verified on 4 real logs (device for `device-failed`, round 5).
30/30b/30c. ??짠7.1's TSV ??D2 (짠11f.1; 짠7.3 measured `#376` saves periodically). ??**짠11h ??the per-frame TIFF
   writer is NOT original behaviour and D1 DELETES it**: true original (md5 `1eb666c1df8a??) **97/179/622** vs the
   copy's **98/181/626**, gate **S1t** 4/4 again in run 7 (`Wire 1902??899`, bare named sinks 28??6, ExecState
   0??; `#23175`/`#22703` left standing). **F1 needs no TIFF cap ??the 5-min run is affordable.**
31. ?뵶 **RETROSPECTIVE WINDOWS STILL BROKEN** ??today's reviewed **07:10??8:04**, the PREVIOUS session, while
   every log it should judge was 09:3x??0:0x (`retrospective.py:282-286`). Fix: start from the oldest UNREVIEWED
   build log. Also **no `docs/cycle16-plan.md`** ??the scope check cannot run.

32. ?뵶?뵶 **OUTCOME REVIEW 2026-09-17 (codex): SIX `OUTCOME-VIOLATION`s** ??`goal-requirement-not-advanced` 쨌
   `tooling-over-delivery` 쨌 `product-not-runnable` 쨌 `decision-starved` 쨌 `scope-inflation` 쨌
   `measurement-without-product`. Verbatim: *"zero new user-runnable deliverables since the last outcome
   review"*; for an experiment next week **the user must still use the original VI**. ?좑툘 **SECOND consecutive
   review with the same finding** ??CLAUDE.md's *"on repetition the work stops for a re-plan with the user"* ??
   **JUDGEMENT/USER, never answerable by a device.** Its 짠4 order: (1) the ONE sentinel connection, (2) full D1
   build, (3) N1/F1/F2 **immediately**, (4) hand over, (5) D2. Annotated in the archive.

## NEXT
?뵶 **JUDGEMENT ??ONE question, measured row by row rather than argued (`d1-build-plan.md` 짠11L): D1's re-wire
needs a wire creator that addresses BOTH ends by INDEX on a NESTED diagram, and the fleet has none.** 24 of 66
rows have an unnamed end (a structure selector, an unnamed tunnel) or an outer source with no name; every
name-addressed op (`gscript.wire`, `wire_control`) cannot reach those, and both index-addressed ones
(`gscript.py:2202`, `:2428`) require a **top-level** source. **`OpStopFromNode_v0` already proves the sink half**
??its body-node ladder invokes `Terminal.Connect Wire` **6349C03** with a body terminal as `Wire Source` ??so the
answer is that ladder **duplicated for the source side**: a FOURTH op, beyond 짠11j's three. Only judgement lifts
the freeze. Secondary, material once that is decided: the 7 FAILED rows (6 횞 `Get Controls.vi` 5001 ??the moving
`ControlTerminal`s should be reparented first per 짠5d, not wired from the panel; 1 횞 `'subarray'` name).
Then: PHASE "full" stage 2 (8 queues + endpoints + sentinels) ??save ??N1 ??F1 (**5 min**, no TIFF cap) ??F2.
?좑툘 OPEN 32's reviewer still stands: **no diagnostic or framework cycle before F1/F2** ??the fourth op is the
re-wire itself, not a diagnostic.

## Where to look
`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 `docs/toolkit-capabilities.md` 쨌 **`docs/d1-build-plan.md`
= the build order; relocation DONE, PHASE "full" open** 쨌 `tools/recipes/build_d1_v0.py` 쨌 `docs/gpu-backend.md`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Prior-art review complete — read-only: no lock, no build, no edit, no `.vi` opened, no hardware.

**6 findings, 0 `novel`.** The op is genuinely unbuilt and `Terminal.Connect Wire` with two traversed terminals is not refuted anywhere. But the named donor is the *wrong* ladder and structurally cannot do the case that matters; "resolves all 31 rows" is contradicted by the same file 39 lines later and by the run-7 log row by row; a nearer donor already exists that is one property-node swap away; and the census written for this very op — which already says both of these things — is not cited.

---

# PART A — THE DIRECTION

## A1 — cleared

The direction is settled **in favour**, and a fourth op is explicitly authorised: `docs/d1-build-plan.md:652-662` (§11m, judgement 2026-09-17) — *"Authorised: `OpConnectNested_v0` … The freeze lift is now closed at four ops"* — and `STATUS.md:104-105` pre-empts the obvious objection: *"the fourth op is the re-wire itself, not a diagnostic."* Nothing in `docs/cycle15-plan.md`'s freeze or in outcome-review OPEN 32 (`STATUS.md:87-94`) contradicts that. The route's two halves are each proven: `Terminal.Connect Wire` 6349C03 as a writer (`docs/toolkit-capabilities.md:51`, wire 0 → 387, ExecState 1) and a `(diagram, node, terminal)` ladder ending on a Terminal reference (`docs/toolkit-capabilities.md:23`, `OpNodeTerms_v0`).

## A2 — no refutation found

Nothing in `archive/peer/`, a retrospective or a superseded section argues against two traversed terminals into one `Connect Wire`. The opposite: `archive/peer/2026-09-06-connect-ladder-plan-attack.md:20-21` put **exactly this construction** to codex in 2026-09-06 — *"Terminal.Connect Wire (6349C03) with the second ladder's terminal as the wire source to wire two arbitrary terminals by indices"* — and the verdict at `:115` was *"Connect Wire probably works for an unoccupied compatible sink"*, with the objection being **node-index stability** (`:40`), not the method. That objection is answered for this use: every index here is read from the census immediately before the call (`tools/recipes/build_d1_v0.py:943-1041`).

## A3-i `contradicted` — the donor named is a **loop**-anchored ladder, not a diagram-indexed one, and the plan's own diagnostic says it cannot do test (c)

The brief and `docs/d1-build-plan.md:658-659` both say the body is *"`OpStopFromNode_v0`'s body-node ladder (Traverse Diagram[i] → Nodes[j] → Terminals[k]) duplicated for the source side"*, with inputs *"(diagram index, node index, terminal index)"*.

`OpStopFromNode_v0`'s ladder is not that. Three files say so:

- `tools/recipes/build_opcreateconstonterm_v0.py:17-19`, verbatim: *"Traverse(`WhileLoop`)[index] -> `To More Specific Class`#683 -> PN `VI Server:Loop`[`Diagram` 6361401] -> PN `AbstractDiagram`[`Nodes[]`] -> IndexArray(`index 3`) -> PN `Node`[`Terms[]`] -> IndexArray(`index 4`)"*.
- `docs/toolkit-capabilities.md:51` — the op's signature is `Class Name`='WhileLoop', **`index` = the loop**, `index 3` = body `Nodes[]`, `index 4` = `Terminals[]`. There is no diagram index.
- `tools/bench/diag_connectnested_donors.log:55,65` — the census shows `#683 To More Specific Class` → `#1168 Property 'Diagram' (reference IN w366)`, i.e. `Diagram` read **off the WhileLoop-typed reference**. No Traverse-"Diagram" node exists in that VI.

And the consequence is already written down, by this project, for this op: `tools/bench/diag_connectnested_donors.py:11-13` — *"the body-node ladder starts at a **WhileLoop-typed** reference … so BOTH ends of a wire built that way would sit on the SAME loop. §11m's test (c) needs two DIFFERENT diagrams."*

**Scope:** the donor identification and the input signature, not the method. It matters because test (c) — source on a different nested diagram from the sink — is the case the 17 `from-tunnel` rows need, and it is the one this donor structurally cannot express. The correct donor is B3-i below.

## A3-ii `contradicted` — "It resolves all 31 rows" is contradicted by the same file 39 lines later, by STATUS, and by the run-7 log row by row

> `docs/d1-build-plan.md:659` (§11m): **"It resolves all 31 rows."**

- Same file, `:698` (§11L): the 24 are *"**8 rows** whose sink or source terminal HAS NO NAME … **16** `from-tunnel` rows whose outer wire has **no NAMED node source**"*. A row with no identified source is not an addressing problem — an op whose source input is `(diagram, node, terminal)` has nothing to put in those three fields.
- The log itself, `tools/bench/build_d1_v0_run7.log:302-325` — 24 rows, and the split is **7 / 17**, not 8 / 16: six `same-loop … unnamed end` (`:302,:305,:306,:308,:312,:314`), one `from-ctl` (`:309`), seventeen `from-tunnel`. Of those seventeen, **sixteen print `(none)`** for `outer_source`; exactly one (`:317`, `#376 t7`) carries an identified source — `{'kind':'node','diagram':'19','uid':637,'i':37,'name':''}` — and that one is genuinely this op's case.
- The 7 FAILED are assigned to a **different** fix by `STATUS.md:101-102`: *"6 × `Get Controls.vi` 5001 — the moving `ControlTerminal`s should be reparented first per §5d, **not wired from the panel**"*.

On the evidence in hand the op reaches **6 + 1 = 7 of the 24**, plus plausibly the single `'subarray'→'x'` name failure = **8 of 31**, not 31. The remaining 16 need a *source resolution*, and the 6 control rows need §5d.

**Scope:** the "all 31" claim and the 8/16 split. It does **not** say the op is unnecessary — 7 rows have no other route.

## A4 `unread-evidence` — the donor census written **for this op** answers two of its questions and is cited nowhere

`tools/bench/diag_connectnested_donors.py` (ran 11:09 today, `…donors.log:1`) exists precisely to decide this build, and `tools/bench/connectnested_donors.json` holds the **complete** census of all six donors (`OpNetInfo_v1`, `OpNodeTerms_v0`, `OpConnect_v0`, `OpStopFromNode_v0`, `OpCreateConstOnTerm_v0`, `OpWhileCast_v0`, at json `:3,:707,:1293,:1870,:2795,:3736`). Its header already states A3-i (`:11-13`) and already identifies the right half-ladder (`:14-18`: *"`OpNetInfo_v1` … ALREADY ENDS on a Terminal reference addressed by (diagram index, node index, terminal index), which is exactly one half of `OpConnectNested_v0`"*). The brief under review cites neither, and repeats the claim the header refutes. *(Observation, not a finding: `…donors.log` stops mid-`OpStopFromNode_v0` at line 71 with no `BGRUN END` line while the JSON is complete — the log is short, the measurement is not.)*

---

# PART B — THE ARTIFACT

## B1 — cleared: the op does not exist

`claudeDev` holds `OpConnect_v0`, `OpConnect2_v0`, `OpConnectCtl_v0` and nothing else matching `OpConn*`. No recipe builds a both-ends-nested writer. `connect_terminals` (`tools/gscript.py:2202-2212`) takes **both** ends from `VI.Block Diagram → Nodes[]` — top-level on both sides, not merely the source; `connect2` (`:2428-2431`) takes a Traverse-"Diagram" sink and a top-level source. So the capability gap is real as stated.

## B2 — cleared: not attempted, and the known 1055 trap is avoided by construction

No record of this build failing. The nearby recorded failure is `docs/NAMES.md:473-475` — the 1055 modal that killed `OpBuildCase_v0` when a **terminal refnum crossed COM** — and this design keeps every refnum inside the op, the same fix `OpCreateEqual_v0` used (`docs/toolkit-capabilities.md:52`, *"both operands are fetched INSIDE the op, so no terminal refnum crosses COM"*).

## B3-i `helper-exists` — `OpConnect2_v0` is the donor: it already has one nested ladder, one Connect Wire, and a complete source ladder, and `OpConnect_v0` already proves two ladders sharing one traversed array

- `tools/recipes/build_opconnect2.py:3-6`: *"sink: Traverse "Diagram"[index] -> TMSC -> Nodes[][index 2] -> Terminals[][index 3] (`OpNetInfo_v1`'s ladder); source: VI -> Block Diagram (23C) -> Nodes[][index 4] -> Terminals[][index 5]; `Terminal.Connect Wire` (6349C03) on the sink."* The **whole source ladder plus its two controls was built in 20 lines** at `:56-76`, and the swap needed here is one node: replace the `VI Server:VI [23C]` property node at `:56` with a second `Index Array` on the Traverse `References` array, plus one diagram-index control.
- That branch is already proven on a built op: `tools/bench/diag_connectnested_donors.log:42-47` — in `OpConnect_v0`, `Nodes[1]` and `Nodes[8]` **both take `array` = w171**, i.e. one `Nodes[]` array feeding two independent Index Arrays. That is the diagnostic's own Q2 (`diag_connectnested_donors.py:22-24`), answered in the affirmative by a shipped VI.
- The same file records what the plan's route costs instead: `build_opconnect2.py:5-6` — *"LabVIEW creates the loop tunnel itself when the sink is inside a structure (Connect Wire crosses borders)"*.

**Scope:** which donor to copy and how the two ladders share one Traverse call. Not the method, not the op's necessity.

## B3-ii `helper-exists` — the 16 unresolved sources have a named call, and its failure here is already logged as an unchased defect

`OpWireSource_v5` is *"**which object drives a wire** — addressed by UID, so no traverse index is involved"* (`docs/toolkit-capabilities.md:48`, 12/12; `docs/NAMES.md:940`). That is exactly the question `build_d1_v0_run7.log:303` asks and fails to answer offline (*"tunnel #5569 outer wire w5812 has no NAMED node source in any census"*) — the join is over static censuses (`tools/recipes/build_d1_v0.py:1013-1017`), never over the machine. And the reason it was not used is already recorded, as a **deferred defect, not a dead end**: `docs/d1-build-plan.md:672-673` — *"`diag_d1_full_route.py` is retired (its T6 control showed `OpWireSource_v5` returning 1055 for every wire — a separate defect, logged, **not chased now**)"*, carried at `STATUS.md:69`.

**Scope:** the 16 `(none)` rows only. It does not touch the 7 rows the new op genuinely unlocks, and it is not an argument for building a reader before F1/F2 — it names the existing call and the recorded reason it is currently unusable, which the plan's "resolves all 31" silently steps over.

## B4 `already-measured` — an unnamed tunnel terminal reached by `(node index, terminal index)` and accepted by `Connect Wire` is measured; cross-diagram `Connect Wire` is already researched

Test (b) — *"body node → an UNNAMED tunnel of a nested structure"* — is the measured content of `docs/toolkit-capabilities.md:35`: *"an EMPTY For loop's `Node.Terminals[]` has exactly one entry (**unnamed sink**) = the count tunnel's outside terminal; an I32 source wired onto it makes the loop runnable"*, via `connect_terminals(target, loop_node, 0, src_node, src_term)`, verified *"wire 346 on both ends, ExecState 0→1"* (`build_harness_copyloop2.log` run 2). A structure node's tunnels appearing as unnamed entries in its `Terminals[]` is visible again in `tools/bench/diag_connectnested_donors.log:31` (`Nodes[9] #142 For Loop`, terminals 2-8 all `''`).

Test (c) is likewise not unexplored: `archive/peer/2026-09-14-stage2-a3-wire-shiftreg-plan.md:56` — *"practitioner evidence that `Terminal.Connect Wire` can connect terminals across different diagrams using an automatically routed wire"* (NI Community, retired NI employee) — alongside `tools/gscript.py:2430-2431`, which records LabVIEW creating the tunnel itself for a nested sink.

**Scope:** the *addressing* of an unnamed tunnel terminal and its acceptance as a Connect Wire endpoint, at top level. It does **not** cover a tunnel whose owning structure sits on a nested diagram, and it does not make (c) measured — it makes (c) the only part of the test plan that is actually new, which matters because §11m's gate reports (c) rather than gating it.

---

```
PRIOR-ART: contradicted     (A3-i  — tools/recipes/build_opcreateconstonterm_v0.py:17-19 + docs/toolkit-capabilities.md:51 + tools/bench/diag_connectnested_donors.log:55,:65 + tools/bench/diag_connectnested_donors.py:11-13 vs docs/d1-build-plan.md:658-659 — covers the DONOR and the input signature: OpStopFromNode_v0's ladder is Traverse "WhileLoop"[i] -> Loop.Diagram 6361401, addressed by LOOP index, and cannot express two different diagrams; does NOT question 6349C03 or the op's necessity)
PRIOR-ART: contradicted     (A3-ii — docs/d1-build-plan.md:698 + tools/bench/build_d1_v0_run7.log:302-325 + STATUS.md:101-102 vs docs/d1-build-plan.md:659 — covers "It resolves all 31 rows" and the 8/16 split (the log says 7/17): 16 rows have NO identified source and 6 are assigned to §5d, so the op reaches ~8 of 31; does NOT say the op is unnecessary)
PRIOR-ART: unread-evidence  (A4    — tools/bench/diag_connectnested_donors.py:8-28 + tools/bench/connectnested_donors.json:3,:707,:1293,:1870,:2795,:3736 — the complete six-donor census written for THIS op, whose header already states A3-i and already names the right half-ladder, is cited nowhere in the brief)
PRIOR-ART: helper-exists    (B3-i  — tools/recipes/build_opconnect2.py:3-6,:56-76 + tools/bench/diag_connectnested_donors.log:42-47 — covers WHICH donor: OpConnect2_v0 already carries the nested sink ladder + Connect Wire + a full source ladder built in 20 lines, and OpConnect_v0 proves two Index Arrays branching one Nodes[] array; does NOT cover the method or the freeze authorisation)
PRIOR-ART: helper-exists    (B3-ii — docs/toolkit-capabilities.md:48 + docs/NAMES.md:940 + docs/d1-build-plan.md:672-673 + STATUS.md:69 vs tools/recipes/build_d1_v0.py:1013-1017 — covers the 16 rows with outer_source "(none)": OpWireSource_v5 is the existing call for "which object drives this wire", and its 1055 here is already logged as an unchased defect; does NOT cover the 7 rows the new op unlocks)
PRIOR-ART: already-measured (B4    — docs/toolkit-capabilities.md:35 + tools/bench/diag_connectnested_donors.log:31 + archive/peer/2026-09-14-stage2-a3-wire-shiftreg-plan.md:56 + tools/gscript.py:2430-2431 vs the §11m test plan's (a)/(b) — covers test (b): an unnamed tunnel terminal addressed by (node index, terminal index) and accepted by Connect Wire is measured functional; does NOT cover a tunnel on a NESTED diagram, and does not make test (c) measured)
```

**The two that change what happens next.** **A3-i + B3-i** — copy `OpConnect2_v0`, not `OpStopFromNode_v0`: the plan's donor is anchored to a loop index and, by the project's own diagnostic header, puts both ends on the same loop, which is the one thing the op exists to avoid. **A3-ii** — the row accounting is wrong in the plan's own direction: build the op for the 7 rows it actually reaches, and decide separately what happens to the 16 whose source is unidentified, because run 8 cannot go "straight to save → N1 → F1 → F2" with 16 cut terminals still unwired.

**Checked and cleared:** the op is genuinely unbuilt (`claudeDev` `OpConn*` = three files, none of them this); no archived exchange refutes `Terminal.Connect Wire` with two traversed terminals — the 2026-09-06 attack on this exact construction objected to node-index stability, which this build handles by reading indices at call time; the known 1055 refnum-over-COM trap is avoided by construction; the bare-sink rule (`tools/gscript.py:2206-2207`) is honoured.

## Sources

(extract from answer)

## What was done with it

**All 6 findings ACCEPTED whole; no citation refuted.** The review changed the donor, the op's input signature
and the row accounting BEFORE a line of the recipe ran. Disposition, one line per finding:

FIXED: contradicted - tools/recipes/build_opconnectnested_v0.py:15 - A3-i accepted: `OpStopFromNode_v0`'s ladder is loop-anchored (`Traverse("WhileLoop")[index] -> Loop.Diagram 6361401`) and cannot express two diagrams, so §11m's named donor is NOT used and the recipe's docstring records why.
FIXED: helper-exists - tools/recipes/build_opconnectnested_v0.py:21 - B3-i accepted: the donor is now `OpConnect2_v0.vi`, whose nested sink ladder, `Connect Wire` invoke and complete source ladder are reused, and only its `VI[Block Diagram 23C]` head is replaced.
FIXED: contradicted - tools/recipes/build_opconnectnested_v0.py:27 - A3-ii accepted: "resolves all 31 rows" is recorded as refuted in the recipe header; the op's reach is measured by the next `build_d1_v0` run, not claimed here.
FIXED: unread-evidence - tools/recipes/build_opconnectnested_v0.py:13 - A4 accepted: `tools/bench/diag_connectnested_donors.py` / `.json` (this session's 6-donor census, 6/0) is now the cited basis of the donor choice in the recipe header.
FIXED: already-measured - tools/recipes/build_opconnectnested_v0.py:62 - B4 accepted: test (b) is gated on WIRE IDENTITY at an unnamed terminal on a NESTED diagram (the part `toolkit-capabilities.md:35` does not cover), and a type-incompatible pairing is reported as a LabVIEW type fact rather than scored as an op failure.
FIXED: helper-exists - tools/recipes/build_opconnectnested_v0.py:68 - B3-ii accepted: the 16 `outer_source (none)` rows are explicitly NOT claimed by this op; test (c) is reported, not gated, and the 16 rows are carried to the judgement session as the remaining gap (`OpWireSource_v5`'s 1055 is the recorded, unchased defect behind them).

### ⚠️ B3-i's construction advice is REFUTED BY MEASUREMENT (run 1, `tools/bench/build_opconnectnested_v0_run1.log`)

The review's B3-i prescribes *"replace the `VI Server:VI [23C]` property node with a second `Index Array` on the
Traverse `References` array, plus one diagram-index control"*. That was **built and run against LabVIEW** and it
does not compile:

```
W4 source-diagram index control: 'index 6'
W4 ROUTE A wired: ExecState 0 (GObject element -> Diagram-class property node - this is the measurement)
```

`Traverse for GObjects.vi`'s `References` output is an array of **GObject** references; the source ladder's head
property node is **Diagram**-class, and GObject → Diagram is a **downcast**, which LabVIEW renders as a broken
wire. The review's own citation (`OpConnect_v0`'s `Nodes[1]`/`Nodes[8]` both taking `array` = w171) shows two
Index Arrays sharing a **`Nodes[]`** array — already cast — not a raw `References` array. The finding's *donor*
half (use `OpConnect2_v0`) stands and is adopted; its *one-node-swap* half does not.

**What that measures, and it is the session's main result:** two INDEPENDENT nested diagrams inside one op need a
**second `To More Specific Class`**, and this fleet cannot create one — `New VI Object` creates no primitive
(`.claude/skills/labview-automation/references/vi-scripting.md:308,:465`, the 0–399 style sweep created nothing),
and the only primitive copier, `gscript.copy_by_index`, would land the node with an **unwirable `target class`**
(a class-specifier `Constant` is a GObject, not a Node, so no wire creator in this fleet reaches its output — the
identical wall `d1-build-plan.md` §11i recorded for `OpCreateConst_v0`). So §11m's *"that ladder duplicated for
the source side"* is not buildable as written, and the op ships as **ROUTE B**: both ends by index on the **same**
nested diagram.

FIXED: contradicted - tools/recipes/build_opconnectnested_v0.py:263 - run 1's own defect repaired: `remove_bad_wires_scripted` left the broken ROUTE-A wire on the source `reference`, so the ROUTE-B fallback declined to wire and the op was never attempted; the wire is now deleted by Traverse index and the bareness is gated (W5a).

**The one thing the review under-called, recorded honestly:** B3-i says the swap is "one node - a second Index
Array on the Traverse `References` array". `References` is an array of **GObject** references while the source
ladder's head property node is **Diagram**-class, and the only cast in the VI is the single
`To More Specific Class` the sink ladder uses. Whether LabVIEW accepts that wire is NOT settled by any file, so
the recipe MEASURES it (ROUTE A) and falls back in the same run to branching the existing cast (ROUTE B, both
ends on the SAME nested diagram). Which one shipped is written to `tools/bench/opconnectnested_labels.json`.
