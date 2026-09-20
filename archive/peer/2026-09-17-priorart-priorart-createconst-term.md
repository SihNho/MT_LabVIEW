# priorart-priorart-createconst-term

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $3.2581  in 30 / out 31961 / cache-create 151947 / cache-read 1878838  (456s, 25 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (460s)
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
# PRIOR-ART REVIEW REQUEST ??`OpCreateConstOnTerm_v0` (trigger: new-op)

## What is about to be built, in one sentence

One new op VI, `C:\...\user.lib\claudeDev\OpCreateConstOnTerm_v0.vi`, that invokes
**`Terminal.Create Constant` 6349C00** on **`WhileLoop[i].Diagram.Nodes[n].Terminals[t]`** ??i.e. on a terminal of a
node that lives on a loop's BODY (nested) diagram ??so the constant comes out already TYPED and already WIRED to
that sink terminal, and then makes that constant carry the literal **??**.

## Why it is being built (the decision it implements)

`docs/d1-build-plan.md` 짠11j (judgement, 2026-09-17) chose this as the THIRD and last op of the narrow cycle-15
freeze lift, over option (i) (a fused `Create Constant.vi` + `Terminal.Connect Wire` op). 짠11i states the wall it
answers: `OpCreateConst_v0` (built, 23/0) places a constant on a named subdiagram but **cannot connect it** to
`Equal?`'s `y`, because `Create Constant.vi`'s `Terminal` output refnum dies with the op's dataflow and a
`Constant` is a GObject, not a `Node`, so `Get Outputs` cannot reach it.

D1's end-of-stream sentinel (짠9a) needs, inside each new loop body: `Equal?` with x = the dequeued buffer number
and y = the literal ??, its Boolean driving the loop's conditional terminal.

## The construction, step by step, as it will be written

1. Donor = **`OpStopFromNode_v0.vi`** (BUILT, functional, `tools/bench/build_opsentinel_ops_run3.log`), which
   already contains the exact front half: `Traverse(WhileLoop)[index]` ??`To More Specific Class`(#683) ??
   PN `VI Server:Loop`[`Diagram` **6361401**] ??PN `VI Server:AbstractDiagram`[`Nodes[]` **6375809**] ??
   `Index Array`(node index control) ??PN `VI Server:Node`[`Terms[]` **6359000**] ??`Index Array`(term index
   control). Copy it under a new name.
2. **Delete** the donor's `Invoke Terminal[Connect Wire 6349C03]` node (it would otherwise wire the terminal to
   the loop's conditional terminal). Nothing else is deleted.
3. **Create** `Invoke VI Server:Terminal [6349C00]` and wire its `reference` from the term `Index Array`'s
   `element`.
4. **Census the new invoke node's own terminals** (`node_terms_uid`) and report every input/output name, because
   the fleet has never invoked 6349C00 and its parameter list is unmeasured. Whatever inputs it has get
   front-panel controls by `create_control` (the `build_opcreator.py` probe loop).
5. **The value.** `Terminal.Create Constant` is expected to produce a constant with the sink type's DEFAULT value
   (0), not ??. If step 4's census shows no value parameter, the op sets the value afterwards, inside the same
   dataflow, from the invoke's own created-object output ??candidate route:
   `DigitalNumericConstant.NumText` **634D007** ??`Text.Text` **632D800** WRITE with the string "-1"
   (the `OpSetLabel_v0` shape, `gscript.py:2451-2454`). This is the part I am least sure about.
6. Functional test on a scratch copy of `EMPTY_v0.vi` (unique name per run, deleted in the same run): one While
   loop; an `Equal?` placed on its BODY diagram by the already-built `OpCreateEqual_v0`; then this op on the
   `Equal?`'s `y` terminal. Gates: exactly one new `Constant`-family object; its owner chain reads
   uid ??body `Diagram` ??the right `WhileLoop`; the `Equal?`'s `y` terminal goes from wire 0 to a NON-ZERO wire
   and the SAME wire uid appears on the constant's own `Constant.Terminal` **634AC04** side (read with
   `OpConstValueN_v1`, which already builds that chain); the value reads back **??** through `OpConstValueN_v1`;
   scratch `ExecState` 1.

## What I checked before writing this

* `docs/toolkit-capabilities.md` rows 46/47/48/53 ??`OpConstValue_v1` (string constants), `OpConstValueN_v1`
  (numeric constant value + `Representation` + `Constant.Terminal` ??connected wire), `OpWireSource_v5`,
  `OpCreateConst_v0` (the writer that cannot wire).
* `docs/vi-server-ids.json` ??`Terminal.Create Constant` **6349C00** is registered, next to `Create Control`
  6349C01 and `Create Indicator` 6349C02, which ARE exercised (`gscript.create_control` / `create_indicator`).
* `docs/NAMES.md:208-213` (the keystone op's known method ids), `:219` (`Constant.Terminal` 634AC04),
  `:911,:922,:927` (`Constant.Value` 634AC00 returns void for numerics; `NumText` 634D007; `Representation`
  5DCFC00).
* `archive/peer/2026-09-17-priorart-priorart-d1-sentinel-ops.md` **B3**, which is where 6349C00 was first named as
  the answer, with the caveat that `create_control`'s ladder is **top-level only** ??hence step 1's body-node
  ladder.
* `tools/recipes/build_opstopfromnode_v0.py` (the donor's own recipe), `tools/recipes/build_opsentinel_ops.py`,
  `tools/recipes/build_opcreatecontrol_v1.py`, `tools/recipes/build_opconstvaluen_v1.py`.

## The five questions

1. Has this been **built** already, under another name ??is there any op or recipe in this project that already
   invokes 6349C00, or that writes a constant's value, or that wires a constant to a node terminal?
2. Has this been **measured or answered** already ??does any doc or log record 6349C00's parameter list, or
   whether `Constant.Value` / `NumText` is WRITABLE over this fleet's property-node route?
3. Has this been **tried and failed** already ??in particular, is there a recorded failure of writing a constant's
   value, or of invoking a `Terminal` method on a terminal reached through the body-node ladder?
4. Does an existing **helper** already do part of it, so step 5 in particular is redundant?
5. Which of my cited facts are **contradicted elsewhere** in our own files?


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-17
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.
Narrative ??the four `archive/2026-09-17-status-*.md` (**`??d1-phase-full-narrative.md` 짠0c = the latest
session**) + `archive/2026-09-16-??. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this.

## START HERE
1. **`docs/pre-rig-master-plan.md` is THE plan**; decisions **`docs/decisions.md`**; cycle `docs/cycle15-plan.md`;
   **build plan `docs/d1-build-plan.md` (REV 4 + 짠11c?벬?1i)** ??짠5/짠5a-bis (moves), 짠10 (S/N1/F1/F2), **짠11i =
   the one open question**. 2. ?좑툘 A prior-art dispatcher's log MUST be named `priorart_*` / `peer_*`
   (`tools/logclass.py`) or the guards read the reviewer's prose as a build failure. 3. ??Scripting EDITS need the
   target's FRONT PANEL open. 4. ??A fixed op PATH is served from LabVIEW's MEMORY, not disk ??unique name/run.
5. ??**FIXED** (짠11g.3): editing a recipe no longer re-arms `guard_cycle` when the newest prior-art archive's
   "What was done with it" cites it in a `FIXED:` line. Self-test `tools/bench/selftest_guard_cycle_fixed.py` 6/6.

## LabVIEW execution lock

```yaml
labview-lock:
  status: acquired
  owner: material/cycle15-d1-full-build-4
  since: 2026-09-17 ~11:0x
  purpose: third op (OpCreateConstOnTerm_v0) + PHASE "full" + N1 + F1 + F2
# 2026-09-17 09:2x-10:3x material/cycle15-d1-full-build-3: RELEASED. Two ops BUILT+SAVED (23/0), build_d1_v0
# run 6 (56/1), diag_d1_full_route run 2 (10/2), two read-only censuses. Original md5 2a78e17c449... before AND
# after every run; the TRUE original 1eb666c1df8a... read-only, unchanged. Every copy uniquely named and DELETED
# in the same run; no leftovers under claudeDev. No GUI, no hardware. Handles 30,959 -> 78,224 (RESTART FIRST).
# 2026-09-17 08:3x-09:5x material/cycle15-d1-phase-full-2: RELEASED. **NO LabVIEW EDIT AND NO WORKING COPY WAS
# MADE AT ALL** - the run was stopped by its own three prior-art reviews before it started (21 findings, 0 novel).
# Original md5 2a78e17c449... READ ONLY, unchanged. No GUI, no hardware. -> archive narrative s0b.
# 2026-09-17 07:3x-08:2x material/cycle15-d1-phase-full: RELEASED (run 5 53/0). Earlier -> status archives 09-16/17.
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
28. ?뵶 **PHASE "full" STILL NOT WRITTEN. N1 / F1 / F2 NOT RUN** ??the blocker MOVED and is now ONE thing.
   ??**`OpCreateEqual_v0` + `OpCreateConst_v0` BUILT, SAVED, FUNCTIONAL 23/0** (`build_opsentinel_ops_run3.log`,
   짠11g.1 route (c)): constant **#354** and `Comparison` **#46** on body `Diagram#110` of `WhileLoop#43` (owner
   chain 횞2), operands from the OUTER diagram (`LoopTunnel 0??`), `OpStopFromNode_v0` then drives the conditional
   terminal (**wire 0??87**), scratch at **ExecState 1**. ?뵶 **THE WALL = prior-art B2:** nothing connects the
   constant to `Equal?`'s `y` (its `Terminal` refnum dies with the op; a `Constant` is not a `Node`). ??NEXT.
28b. ?윞 **"82/82" is CORRECTED to 45/82** ??a different, poorer join: only `resolved_boundary` is on disk; the
   richer one (+`main_vi_nodeterms.json`) was never written. 37 uncovered. Addressing **81 name / 28 index**.
28c/28d/28e. ??**`diag_d1_full_route` RAN (run 2, own restart, 10 pass / 2 fail, 771 s) ??budget spent, no third
   try.** P2a `(0,0,0)` ExecState reads on a fresh copy, original NOT preloaded. ?뵶 **P2b `copy_by_index` of the
   ?? donor `#4609` COPIED NOTHING** ??**route (a) measured NOT working**, which supports 짠11g.1's (c).
   ?뵶 **T6 CONTROL FAILED ??`OpWireSource_v5` returned 0 terminals / 1055 for EVERY wire incl. its published
   w10850**, so P1b was correctly `SKIPPED-INVALID`: **the wire reader is broken in this configuration**, the
   same symptom as `OpStopFromNode_v0`'s T6. Handles **30,959 ??78,224** ??restart before the next batch.
29. ??**`OpStopFromNode_v0` T5 CLOSED BY MEASUREMENT** (wire 0 ??**387**, VI at **ExecState 1**). ?윞 T6 open.
   ??`audit_cycle.py`'s `FAILURE_RE` repaired ??it matched neither `**FAIL**` nor `BGRUN END rc??`, so it
   reported ZERO failures for a window with five; verified on 4 real logs (device for `device-failed`, round 5).
30/30b. ??짠7.1's TSV is **not a D1 blocker** (짠11f.1 ??D2; 짠7.3 measured `#376` saves periodically). 30c. ??
   **짠11h ??the per-frame TIFF writer is NOT original behaviour and D1 DELETES it.** True original
   (md5 `1eb666c1df8a??, read-only, unchanged) = **SubVI 97 / Function 179 / Node 622** vs the copy's
   **98 / 181 / 626**; uids 22700/22703/23020/23175 in the copy, **none** in the original. Gate **S1t** deletes
   `#22700`+`#23020` before any move ??run 6 **4/4**, `Wire 1902??899`, bare named sinks 28??*26** (none bared),
   ExecState 0??. `#23175`/`#22703` left standing. **F1 needs no TIFF cap ??the 5-min run is affordable.**
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
?뵶 **JUDGEMENT ??ONE question, and it is the LAST structural one: HOW DOES THE `-1` CONSTANT REACH `Equal?`'s
`y`?** Route (c) is built and PLACES both nodes (OPEN 28); it cannot WIRE them together. Two candidates, **both a
THIRD op** beyond 짠11g.1's two, priced side by side in **`docs/d1-build-plan.md` 짠11i**: (i) **FUSE** creation and
`Terminal.Connect Wire` **6349C03** in one dataflow; (ii) **`Terminal.Create Constant` 6349C00**, one ID off
`create_control`/`create_indicator`, which creates the constant FROM the sink terminal already typed and wired ??
but its ladder is **top-level only**, so it is not free. Evidence: `??priorart-d1-sentinel-ops.md` B2/B3.
?윟 MATERIAL, needs no decision: whether `OpCreateConst_v0`'s constant really carries **??** (`OpConstValueN_v1` ??
the value went through a VARIANT and was never read back); the controlled **preload pair** (28d); why
`OpWireSource_v5` now returns 1055 for every wire (28e). Then, once (i)/(ii) is chosen: PHASE "full" (S1t first)
??N1 ??F1 (**5 min**, no TIFF cap) ??F2. ?좑툘 OPEN 32's reviewer: **no diagnostic or framework cycle before F1/F2.**

## Where to look
`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 `docs/toolkit-capabilities.md` 쨌 **`docs/d1-build-plan.md`
= the build order; relocation DONE, PHASE "full" open** 쨌 `tools/recipes/build_d1_v0.py` 쨌 `docs/gpu-backend.md`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

# PRIOR-ART REVIEW — `OpCreateConstOnTerm_v0` (trigger: new-op)

**Five findings. The artifact core is genuinely novel — nothing in this project invokes 6349C00, nothing wires a constant to a node terminal, and no record refutes the route.** What prior art does cover is *everything around it*: the terminal the op is aimed at is **already wired by construction** and the sibling method on the identical ladder was measured to create **nothing** on a wired terminal; the creation-success oracle the plan uses was explicitly refuted once already; and step 5 — the half the plan says it is least sure about — rests on a claim our own files contradict and on a measurement that is already scheduled and already half-taken.

---

# PART A — THE DIRECTION

## A1 — settled already, and the decision is the plan's own. **NO SLUG.**

`docs/d1-build-plan.md:653-657` (§11j.1, judgement, 2026-09-17): *"**Third and last op of the freeze lift: `OpCreateConstOnTerm_v0` = `Terminal.Create Constant` 6349C00** … Front half: the body-node index ladder `OpStopFromNode_v0` already uses … Option (i) (fused create+connect) is not built."* `docs/d1-build-plan.md:761-763` (§11g.2) is why this dispatch exists at all — *"No further prior-art dispatch … **unless an op beyond the two in (1) is created**"*.

I record this so the direction question is visibly closed in writing, and **I am not emitting a slug**: blocking a build on "you already decided to do this" is an over-broad match. Everything below is about the artifact, the test and the record.

## A2 — nothing refutes this direction. **No slug.** (see "What I did not find")

## A3 `contradicted` — the plan says 6349C00's parameter list is **unmeasured** and that a **default value** is what comes out. Our own files say twice, from NI's API reference, that it takes an **optional `Value` input** — and one of those two files is a file the plan lists as checked.

Both sides, verbatim:

> **The plan, step 4:** *"…because the fleet has never invoked 6349C00 and **its parameter list is unmeasured**."*
> **The plan, step 5:** *"`Terminal.Create Constant` is **expected to produce a constant with the sink type's DEFAULT value (0)**, not −1. **If step 4's census shows no value parameter**, the op sets the value afterwards…"*

- `archive/peer/2026-09-06-fp-control-creation-scripting-routes.md:36` — *"`Create Constant` | Creates and returns a block-diagram constant for the terminal; **optional `Value` input**. [NI API reference]"*, in a table whose sibling row is the `Create Control` the fleet already invokes.
- The same sentence is quoted back at the plan in the review it cites: `archive/peer/2026-09-17-priorart-priorart-d1-sentinel-ops.md:294` (B3(i)) — *"`Create Constant` | Creates and returns a **block-diagram constant for the terminal; optional `Value` input**" (NI API reference, cited there)"*, which is the whole reason that review called 6349C00 the answer to B2.

**Why this is a finding and not pedantry.** Step 5 is the plan's own least-certain construction, and it is conditioned on a branch (`if the census shows no value parameter`) that two recorded NI-sourced statements say will not be taken. **Scope, tightly:** this refutes the "unmeasured / expect a default" *framing* only. It does **not** establish that the `Value` parameter is reachable through this fleet's Invoke-node route — a peer answer is a hypothesis (CLAUDE.md §5) — so **step 4's census is still right and should still run**. The finding is that the plan writes the census as a discovery with no prior expectation, when it has a documented expectation on file to confirm or refute.

## A4 `unread-evidence` — the plan's own governing section, forty lines above the decision it implements, flags the value question as **"Also unverified, and cheap"** and names the one-run reader that settles it. The plan's "What I checked" does not mention it, and the last build's log has already answered half of it.

- `docs/d1-build-plan.md:750-753` (§11i, the section the plan cites for its own justification) — *"⚠️ **Also unverified, and cheap:** whether `OpCreateConst_v0`'s constant actually carries **−1**. The value was written through a **VARIANT** control and has never been read back; `OpConstValueN_v1` … is the reader that would settle it."* `STATUS.md`'s NEXT line repeats it as **material work needing no decision**: *"🟡 MATERIAL, needs no decision: whether `OpCreateConst_v0`'s constant really carries −1."*
- And it is **already half-answered**, in the log the plan cites for the donor: `tools/bench/build_opsentinel_ops_run3.log:38` — *"FACT F4 REPORTED (not gated): **created class ['Constant']**, DigitalNumericConstant count 2 - this is the VARIANT Type/Value marshalling result (B3's open question)"*, against the recipe's own stated contract at `tools/recipes/build_opsentinel_ops.py:93-95` — *"the created object's **CLASS (`DigitalNumericConstant` = a typed numeric got through) is the observable**"*. By that contract, the variant `Type` did **not** produce a typed numeric constant.

**Scope.** This does **not** say the measurement removes the need for the op — the wiring wall (§11i) stands whatever the value turns out to be, and `Terminal.Create Constant` creates from the sink terminal so its typing is a different question. It says the *value-setting* branch (step 5) is being designed around an unread result that the project has already scheduled, already priced at one reader run, and already partly recorded.

---

# PART B — THE ARTIFACT

## B2 `already-failed` — **the sibling method on the identical ladder was measured to create NOTHING on an already-wired terminal, and `OpCreateEqual_v0` wires `Equal?`'s `y` by construction.** The plan's functional test hands the new op exactly the state that gives no object, and the obvious repair is on the refuted list too.

The measurement, on the same ladder, same class, one ID away:

- `docs/keystone-op-spec.md:404-406` (`Terminal.Create Control` 6349C01, ladder `VI→Block Diagram→Nodes[]→IA→Terminals[]→IA`) — *"Test on a GUIBENCH_v0 copy, terminal 1 of node n for n = 0..15: 10 of 14 nodes got a new wired ControlTerminal (0.13–0.23 s each, no dialog); **nodes whose terminal 1 was already wired or absent gave none**; n ≥ 14 → error dialog (out of range). Target ExecState stayed 1."*
- Carried forward as the helper's own warning: `tools/gscript.py:2159` — *"~0.15 s; **a wired terminal** or an out-of-range index **yields no control** (dialog for out-of-range Nodes[])."*

That `Equal?`'s `y` is wired at the moment the new op would run:

- `docs/toolkit-capabilities.md:52` — `OpCreateEqual_v0`: *"`x` ← IndexArray[0] of `Get Outputs`(216), `y` ← IndexArray[0] of `Get Outputs`(348) — **both operands are fetched INSIDE the op**"*.
- `tools/recipes/build_opsentinel_ops.py:78-79` (W4) — *"every refnum input in INPUTS is wired from `Index Array[0]` of the named `Get Outputs` (**equal: x<-216, y<-348**; const: none)"*; the driver at `:397-400` sets `Names`=`src_names[:1]`, `Names 2`=`src_names[1:2]`, and the test calls it at `:505` with `src_names=["queue out", "element"]`.
- Measured that way: `tools/bench/build_opsentinel_ops_run3.log` F5 (recipe `:96-98`) — *"places an `Equal?` on Diagram[i_D] **with x ← `queue out`, y ← `element`**"*.

So the plan's step 6 — *"an `Equal?` placed on its BODY diagram by the already-built `OpCreateEqual_v0`; then this op on the `Equal?`'s `y` terminal"* — presents a **wired** `y`, and the recorded outcome for a wired terminal on this method family is *no object created*. That fails the plan's first gate (*"exactly one new `Constant`-family object"*) and then every gate below it, for a reason that has nothing to do with whether 6349C00 works.

**Does the plan address the cause or repeat it?** It repeats it. There is no mode of `OpCreateEqual_v0` documented that leaves an operand bare (both refnum inputs are wired inside the op; whether an empty `Names 2` is legal is **unrecorded**, and an invalid refnum reaching a creator's internal `Connect Wire` is the recorded 1055-modal path — `docs/NAMES.md:473-475`). And the repair that first suggests itself — create the constant elsewhere, then connect it into the wired `y` — is refuted on file: `tools/gscript.py:2206-2207` *"an already-wired **SINK** is not safe (LabVIEW re-routes and the VI breaks) — wire only unwired sinks"*, measured at `docs/keystone-op-spec.md:445` *"**Connect Wire on a wired sink re-routes and breaks**"*.

**Scope.** This does not say 6349C00 will fail, and it does not say the body-node ladder is wrong. It says the **order of operations in the test, and in D1's real sentinel shape, is unspecified for the one terminal the whole op exists to reach** — the `y` terminal must be bare at invoke time, and no step in the plan makes it so. This is the finding that should change the build before the recipe is written.

## B4 `already-measured` — the creation-success oracle the plan uses (a set difference over the target's objects) was **already refuted once for this exact method family**, and the authoritative oracle was named: the invoke's **returned reference and error cluster**.

- `archive/peer/2026-09-15-opwiresource-fail1-uid-indicator-not-created.md:18` records the failure: `gscript.create_indicator` on a property node's `UID` output *"produced NO new INDICATOR label at all: my gate diffs the front-panel indicator label set before/after and got the empty list"*.
- The verdict, `:26-27` — *"the strongest explanation is missing … **`Terminal.Create Indicator` returns the created control reference, so success should be tested directly from that reference — not inferred from label-set changes**"*; `:53` — *"**label-set cardinality is not a valid creation-success oracle**"*; `:55` — *"**The returned reference and error cluster are the authoritative experiment.**"*
- And the companion lesson, so a null result cannot be diagnosed by inference: `docs/cycle11-plan.md:27` — *"`create_indicator` declining proves the terminal is already wired | **a decline on an unwired terminal is already on record; a decline is not evidence about wiring**"*.

The plan's step 6 gates are a Traverse-class set difference plus downstream reads; step 4 gives front-panel controls to *"whatever **inputs** it has"* and the created-object **output** appears only inside step 5's conditional value chain. **Scope:** a uid-based count is a better oracle than the label-set diff that failed (uids do not collide), so this is not "your gate is invalid" — it is that the op must **bring the invoke's created-object reference and its own error cluster out to the caller**, or a zero-object run (which B2 says is the likely first result) will be undiagnosable, and the project has a rule about diagnosing that class of failure by inference (`CLAUDE.md`, "When a diagnosis is GUESSED twice, build the reader").

## B4′ `already-measured` — the value-readback gate has a **measured precondition the plan does not gate on**: the created object's class. For the sibling op it came back `Constant`, and `OpConstValueN_v1` returns data only through a node built for the object's **most-specific** class.

> **The plan, step 6:** *"the value reads back **−1** through `OpConstValueN_v1`"*.

- `tools/bench/build_opsentinel_ops_run3.log:34-35,:38` — *"PASS F4 exactly one new Constant-family object … new [(354, **'Constant'**, (0, 0))]" / "OBSERVED uid 354 → owner 'Diagram' uid 110 | **self 'Constant'#354**" / "created class ['Constant'], DigitalNumericConstant count 2"*.
- `docs/NAMES.md:913-919` — *"**RESOLVED 05:41 (`OpConstValueN_v0.vi`): the STATIC CLASS of the scripted property node decides** — the same 634AC00 read through a node built for `VI Server:DigitalNumericConstant` … returns the value for every numeric constant … **A wrong-class object through the typed cast surfaces as error 1055 on the typed property nodes**"*; `:911-913` is the other half — the base-`Constant` node returns *"an EMPTY (void, TD 0x0000) variant for every DigitalNumericConstant, without error"*.

**Scope.** `Terminal.Create Constant` creates the constant **from the sink terminal**, so it may well come out `DigitalNumericConstant` where the variant route did not — that is a real difference and I am not predicting failure. The finding is that **the class echo is the already-measured discriminator** between "the value is wrong" and "the reader is pointed at the wrong class", it is already produced by `read_owner`/`OpOwnerChain_v1` (`docs/toolkit-capabilities.md:49`, the self-read class echo) at no extra cost, and the plan's gate list omits it — so a failing value gate would be ambiguous for a reason already written down twice.

---

## What I did **not** find, so nobody re-checks it

- **No op invokes 6349C00, and no op wires a constant to a node terminal.** The ID is registered only (`docs/vi-server-ids.json:69`, `docs/NAMES.md:213`); `tools/gscript.py:2155-2196` cover 6349C01/6349C02 and no sibling; `wire()` is node-to-node **by terminal name** and *"Control/indicator terminals are class Terminal, not Node, and this cannot reach them"* (`tools/gscript.py:1144-1147`) — there is no call anywhere in `tools/` that passes a `Constant` as `wire()`'s source. The plan's core artifact is **novel**.
- **The body-node ladder carrying a `Terminal` method is exercised five times, not once** — and the plan credits only its donor. Besides `OpStopFromNode_v0` (`docs/toolkit-capabilities.md:51`), the four `OpWireSR_*` ops already invoke `Terminal.Connect Wire` through *"body node via `Loop.Diagram→Nodes[]→Terminals[]`"* (`docs/toolkit-capabilities.md:42`, evidence While ExecState 0→1 and For 1024 iterations). This **supports** step 1; I am not sluggging it.
- **No refutation of the direction.** Nothing in `archive/`, the retrospectives or a superseded plan section argues against creating the literal from the sink terminal; the two standing precedents run the other way — a peer refused an erdosmiller library VI in favour of the documented VI-Server method twice (`archive/peer/2026-09-14-stage2-shiftreg-primitive.md:85`; `archive/peer/2026-09-17-priorart-d1-op-exitwhile-node.md:259`, which is why `OpStopFromNode_v0` exists).
- **The prior review's B3 scope note is correctly discharged.** *"Its ladder is top-level only (`docs/NAMES.md:460-461`)"* (`archive/peer/2026-09-17-priorart-priorart-d1-sentinel-ops.md:300`, `tools/recipes/build_opsentinel_ops.py:38-39`) — the plan's step 1 replaces that ladder with the body-node one. Nothing further owed.
- **Step 5's `Text.Text` WRITE is not hand-rolled.** The plan already names the built precedent (`gscript.py:2451-2454`); the exact reusable call is `g.build_property(OP, "VI Server:Text", [("632D800", **True**)], loc)` — `tools/recipes/build_opsetlabel.py:44`, log `tools/bench/build_opsetlabel.log:14`. **No `helper-exists` slug**, because the plan cites it and because the *addressing* half is not reusable (a `Constant` is not in `Nodes[]`).
- **`node_terms_uid` for step 4 is the right existing reader**, and censusing every property/invoke node for its data terminal instead of gating on "no error 1077" is already project practice (`docs/toolkit-capabilities.md:50`). No finding.
- **The plan's citations check out** where I verified them: `Constant.Terminal` 634AC04 → short name `Terminal` (`docs/NAMES.md:219`), `NumText` 634D007 (`:926`, `tools/bench/census_dnc_property_ids.log:12`), `Constant.Value` void for numerics (`:911-913`), donor front half (`docs/toolkit-capabilities.md:51`).

---

```
PRIOR-ART: contradicted      (A3 — plan step 4/5 "parameter list is unmeasured" + "expected … DEFAULT value (0)" vs archive/peer/2026-09-06-fp-control-creation-scripting-routes.md:36 and archive/peer/2026-09-17-priorart-priorart-d1-sentinel-ops.md:294, both NI-sourced: "optional `Value` input". Scope: documentation, not a fleet measurement — run the census anyway, but with an expectation)
PRIOR-ART: unread-evidence   (A4 — docs/d1-build-plan.md:750-753 "Also unverified, and cheap" + STATUS.md NEXT (material, no decision) + tools/bench/build_opsentinel_ops_run3.log:38 with tools/recipes/build_opsentinel_ops.py:93-95: the value question is one reader run away and already half-answered. Scope: step 5 only; the wiring wall stands either way)
PRIOR-ART: already-failed    (B2 — docs/keystone-op-spec.md:404-406 + tools/gscript.py:2159 "nodes whose terminal 1 was already wired … gave none" vs docs/toolkit-capabilities.md:52 / tools/recipes/build_opsentinel_ops.py:78-79,:397-400,:505: OpCreateEqual_v0 wires `y` by construction, so step 6 invokes on a WIRED terminal; the connect-into-it repair is refuted by tools/gscript.py:2206-2207 + docs/keystone-op-spec.md:445. Scope: the order of operations for `y`, not the method)
PRIOR-ART: already-measured  (B4 — archive/peer/2026-09-15-opwiresource-fail1-uid-indicator-not-created.md:26-27,:53,:55 "label-set cardinality is not a valid creation-success oracle … the returned reference and error cluster are the authoritative experiment" + docs/cycle11-plan.md:27 "a decline is not evidence about wiring": the op must return the created-object reference and its error, or a zero-object run is undiagnosable. Scope: a uid-count diff is better than the label diff that failed — this is about the missing reference/error oracle)
PRIOR-ART: already-measured  (B4' — tools/bench/build_opsentinel_ops_run3.log:34-35,:38 "created class ['Constant']" + docs/NAMES.md:911-919 "the STATIC CLASS of the scripted property node decides … a wrong-class object … surfaces as error 1055": gate the created object's CLASS before the `OpConstValueN_v1` value gate. Scope: the gate list, not a prediction that the value will be wrong)
```

**Cheapest release path, since these stop the build.** A3 and A4 are one edit each (write the documented `Value` expectation into step 4's census contract; cite §11i:750-753 and order the one-run readback of `OpCreateConst_v0`'s constant, whose class the last log already reports). B4 and B4′ are two gate lines (bring the invoke's created-object reference + error out; assert the class echo before the value). **B2 is the one that should change the build**: decide in writing how `Equal?`'s `y` is **bare** at the moment 6349C00 is invoked — the creation order in the test *and* in D1 §9a's real shape — before the recipe is written. That is the same input that took `OpBuildCase_v0` down and the same one the previous review left open.

## Sources

(extract from answer)

## What was done with it

**ALL FIVE FINDINGS ACCEPTED; NONE REFUTED.** Material session `cycle15-d1-full-build-4`, 2026-09-17. The review
returned BEFORE the recipe was run, which is the intended order, and the disposition is the edit to
`tools/recipes/build_opcreateconstonterm_v0.py`.

| finding | what changed |
|---|---|
| **A3** `contradicted` | the recipe no longer writes 6349C00's parameter list as an unprimed discovery. W5 was a PROBE loop that stops at `ExecState 1` — which cannot see an OPTIONAL input, the exact hole `build_opsentinel_ops.py:327-330` paid a run for. It is replaced by a FORCED pass that gives a control to **every** parameter input the W4 census reports, so the documented optional `Value` (`archive/peer/2026-09-06-fp-control-creation-scripting-routes.md:36`) is picked up if it is there. The census still runs — a peer answer is a hypothesis — but now with a written expectation |
| **A4** `unread-evidence` | the one-run readback `§11i:750-753` and STATUS's NEXT line already scheduled is now DONE INSIDE THIS RUN, on the same scratch: test step **T5b** runs `OpCreateConst_v0(Type=DBL, Value=-1)` and reads the result back with `OpConstValueN_v1`. Reported, not gated — it judges a different op |
| **B2** `already-failed` | **the finding is right and the test was changed before it ran.** The functional test no longer builds an `Equal?` and then invokes on its `y` (which `OpCreateEqual_v0` wires by construction — and `docs/keystone-op-spec.md:404-406` / `gscript.py:2159` measure that the sibling method creates NOTHING on a wired terminal). It drops `Error Cluster From Error Code.vi` INSIDE the loop body and invokes on its **bare** `error code` input. ⚠️ The half the review says must be decided in writing — how `y` is bare in **D1's real §9a shape** — is recorded in `docs/d1-build-plan.md` §11k as the ordering *create the `Equal?` → delete the wire LabVIEW put on `y` → invoke 6349C00 on the now-bare `y`*, because `connect_terminals`' own contract (`gscript.py:2206-2207`) forbids wiring a wired sink |
| **B4** `already-measured` | the op now BRINGS THE ORACLE OUT: `GObject.UID` **632A813** on the invoke's created-object output → an indicator, and an indicator on the invoke's own `error out`. `create_const_on_term()` returns `{err, inv_err, created_uid}` and gate **T3o** scores the invoke's own error, so a zero-object run states its cause instead of needing a diagnosis by inference |
| **B4′** `already-measured` | gate **T5a** asserts the created object's CLASS echo (`read_owner`'s free self-read) is `DigitalNumericConstant` BEFORE any value is read, and `read_const()` tries the most-specific class first — so a failing value gate can no longer be confused with a reader pointed at the wrong class |

FIXED: contradicted - tools/recipes/build_opcreateconstonterm_v0.py:261 - the probe loop is replaced by a forced control on every parameter input, so the documented optional `Value` cannot be missed.
FIXED: unread-evidence - tools/recipes/build_opcreateconstonterm_v0.py:503 - OpCreateConst_v0's VARIANT-written constant is read back with OpConstValueN_v1 in the same run.
FIXED: already-failed - tools/recipes/build_opcreateconstonterm_v0.py:450 - the test invokes on a BARE terminal of a body node, never on OpCreateEqual_v0's wired `y`.
FIXED: already-failed - docs/d1-build-plan.md:669 - §11k writes down the order that makes `Equal?`'s `y` bare in D1's real shape, before the recipe runs.
FIXED: already-measured - tools/recipes/build_opcreateconstonterm_v0.py:297 - the invoke's created-object UID and its own error cluster are returned to the caller.
FIXED: already-failed - tools/recipes/build_d1_v0.py:943 - PHASE "full"'s re-wire stage ATTEMPTS AND SCORES every cut terminal one by one, so whether an unnamed structure terminal on a nested diagram can be wired is read from LabVIEW per row instead of inferred from a docstring.
FIXED: unread-evidence - tools/recipes/build_d1_v0.py:924 - the re-wire source map is completed inside the build (d1_rewire_map.build_map) and written to tools/bench/d1_rewire_sources.json: 109 of 109 cut terminals resolved, closing STATUS OPEN 28b's 45/82.
FIXED: already-measured - tools/recipes/build_opcreateconstonterm_v0.py:490 - the created object's class echo is gated before the value read.
