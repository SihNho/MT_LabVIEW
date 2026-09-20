# priorart-priorart-d1-sentinel-ops

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.1930  in 46 / out 29927 / cache-create 177530 / cache-read 3338670  (427s, 42 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (431s)
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
# PLAN UNDER REVIEW ??two new ops for D1's sentinel tests (cycle 15, 2026-09-17)

## What I am about to build, and why

`docs/d1-build-plan.md` 짠9a says each of D1's three new While loops (1.2 TRACKING, 1.5 FOCUS, 1.7 WRITER) exits on
an **end-of-stream sentinel** that arrives on a queue it already consumes: buffer number **??** on `Q_meta` /
`Q_rmeta` / `Q_focus`, an **empty array** on `Q_res` / `Q_good`. To test a sentinel INSIDE a loop body I need, on
that body diagram, two things the fleet cannot place there today:

1. a **comparison primitive** (`Equal?`) whose output drives the loop's conditional terminal, and
2. the **literal** it compares against (a numeric constant `-1`, and a Boolean constant where one is needed).

짠11g.1 (judgement, 2026-09-17) chose **route (c)**: wrap the erdosmiller LV-Scripting creators
`Create Equal.vi` and `Create Constant.vi` (both present, listed today in
`C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting\`) in the **`queue_node`
pattern** ??`tools/gscript.py:928-934`, the wrapper shape that already placed `Create Obtain Queue` /
`Enqueue Element` / `Dequeue Element` / `Release Queue` on arbitrary diagrams (4 ops, core 162/162). The cycle-15
op freeze (`docs/cycle15-plan.md:104`) is lifted for **exactly these two ops** and nothing else.

Proposed artefacts:
* `OpCreateEqual_v0.vi` ??places one `Equal?` Comparison node on a NAMED subdiagram (`Diagram` Traverse index),
  same input shape as `OpQueue*_v0`: `vi path` 쨌 `Class Name`/`index`/`Names` (the source node whose output
  terminal seeds it) 쨌 `Class Name 2`/`index 2` = `Diagram`/<body index> 쨌 `location`.
* `OpCreateConst_v0.vi` ??places one numeric or Boolean **constant** with a GIVEN VALUE on a named subdiagram.
* Python wrappers in `tools/gscript.py` alongside `queue_node`, plus rows in `docs/toolkit-capabilities.md`.

Acceptance for each: build, then a FUNCTIONAL test on a scratch copy ??the node appears on the named subdiagram
(owner chain uid ??body Diagram ??the right WhileLoop) and a trivially wired case reaches `ExecState 1`.

## The facts I am relying on, with citations, so each can be attacked

* `tools/gscript.py:928-934` ??`queue_node` "places one primitive on any diagram" via a `Diagram` Traverse index.
* `archive/bench-2026-09-14-stage2-toolkit/probe_queue_vis.log:9-10` ??the erdosmiller creators were censused.
* `docs/toolkit-capabilities.md` rows 24-35, 41-44 ??the queue / loop / exit_while / shift-register ops.
* `.claude/skills/labview-automation/references/vi-scripting.md:308` ??`New VI Object` cannot create most node
  types (error 1054); NI's advice is to copy from a donor. That is why a library creator is preferred here.
* `docs/d1-build-plan.md` 짠11d row 3 ??"the literals come from donor constants in the original
  (`opconstvaluen_scan.json`: 0횞69, 1횞36, 20횞2, ??횞1, 25횞1) via `copy_by_index` + `move_in`" ??the route 짠11g.1
  did NOT choose.

## The five questions

1. Has either op been **built** already, under another name? (I know of `OpConstValue*`, `build_case`,
   `OpBuildIA`, `copy_by_index` ??I believe none of them PLACES a new primitive or constant on a named
   subdiagram, but that belief is exactly what I want attacked.)
2. Has the route been **measured or answered** already in a doc or a log?
3. Has it been **tried and failed** already ??is there a recorded failure of wrapping `Create Constant.vi` or
   `Create Equal.vi`, or of setting a created constant's VALUE by script?
4. Does an existing **helper** already do it, so this code is redundant?
5. Which of my cited facts are **contradicted elsewhere** in our own files?

Answer for BOTH ops separately where the answer differs ??`Create Constant.vi` (does anything in the fleet set a
constant's value after creating it?) is the one I am least sure about.


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-17
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.
Narrative ??`archive/2026-09-16-status-cycles-11-13-narrative.md` + the four `archive/2026-09-17-status-*.md`
(**`??d1-phase-full-narrative.md`** 짠0b = this session). ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this.

## START HERE
1. **`docs/pre-rig-master-plan.md` is THE plan**; decisions **`docs/decisions.md`**; cycle `docs/cycle15-plan.md`;
   **build plan `docs/d1-build-plan.md` (REV 4 + 짠11c/짠11e/짠11f)** ??짠5/짠5a-bis (moves), 짠10 (S/N1/F1/F2).
2. ?좑툘 A prior-art dispatcher's log MUST be named `priorart_*` / `peer_*` (`tools/logclass.py`) or the guards read
   the reviewer's prose as a build failure. 3. ??Scripting EDITS need the target's FRONT PANEL open. 4. ??A fixed
   op PATH is served from LabVIEW's MEMORY, not disk ??unique working-copy filename per run.
5. ?좑툘 **Editing a recipe re-arms `guard_cycle`**: it compares the recipe's mtime to the newest prior-art review, so
   every post-review fix costs another ~10-min round. Batch corrections into ONE edit before dispatching.

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  owner:
  since:
  purpose:
# 2026-09-17 08:3x-09:5x material/cycle15-d1-phase-full-2: RELEASED. **NO LabVIEW EDIT AND NO WORKING COPY WAS
# MADE AT ALL** - the run was stopped by its own three prior-art reviews before it started (21 findings, 0 novel).
# Original md5 2a78e17c449... READ ONLY, unchanged. No GUI, no hardware. -> archive narrative s0b.
# 2026-09-17 07:3x-08:2x material/cycle15-d1-phase-full: RELEASED. `build_d1_v0.py` run 5 PHASE "relocate" (53/0),
# `build_opstopfromnode_v0.py` x3, four read-only censuses; every copy uniquely named, created and DELETED in the
# same run; md5 before AND after; handles 31,002 -> 33,225. Earlier holders -> the status archives of 09-16/17.
```
**Never assume an instance exited**: `tasklist | grep -i labview`. Fresh ??1,500 handles; unique scratch name/run.

## HARDWARE ??permission follows the RIG STATE. Current: **遺꾪빐 / DISASSEMBLED ??everything allowed**
**遺꾪빐 ??WE ARE HERE** = motors ??ASI ??camera ??쨌 議곕┰ = ??????쨌 ?ㅽ뿕以?= ?????? ?좑툘 The ASI carve-out is
**RETIRED** (rule 1b); **only the user announces a state change**. Rotor counter **0** 쨌 magnet full travel 쨌
camera 1280횞1024, offsets 0, 90.0009 Hz, never write `BinningHorizontal`; **a session open RESETS ROI *and*
exposure** ??the acquisition loop applies `tools/bench/camera_contract.py`. **No beads while disassembled.**

## Where things stand
**Stage 1 CLOSED**. **Stage 2 IN PROGRESS**: `Track_v6_CPU_core_v0.vi` 69/69 쨌 `??queue_v0.vi` 162/162 ??**say it
exactly:** bit-identical for the **first 10,018 frames only**, both **replay** artefacts (recorded TIFFs, `FOR`
loops, no acquisition, no stop). **THE GAP:** 169 ops, 118 recipes, 226 peers ??**zero runnable experimental VIs**.

## OPEN ??one line each; long forms in `archive/2026-09-17-status-cycle15-narrative.md`
1??, 5, 9??2, 18 ??**all in archive 짠9**: PERIODIC auto-reset ungated 쨌 autofocus CLOSED (25 frames ??3.6 Hz) 쨌
   27 undisposed peer archives 쨌 startup drives instruments 쨌 A2 54/54, A3 112/170 쨌 doc lint 2/4/3 쨌 **TIFF
   1.3 MB/frame, ??22 MB/s ??bound it or the disk fills**. 13/14/15b/17b: ??stop measured (`#637` term
   **648 ??w3457 ??#11639**) 쨌 ?뵶 `bgrun --detach` misses an orphaned grandchild 쨌 ?뵶 v3's R11 scored the *restart*.
16. ?뵶 **GPU whole-fixture divergence OUTSIDE `decisions.md:38` ??JUDGEMENT** (`gpu_n1_deltas.json`): beads 0??
   **0 exceedances over all 10,043**; **only bead 4** ??10 x, 9 y, 1 flip, n_valid 10,029. ??짠4.
19/25/26. ??**PLAN = REV 4 + 짠11c/짠11d/짠11e**; TRANSPORT = **queues only**, sentinels stop 1.2/1.5/1.7,
   `#12589`/`#642` stay on 1.1. 20??3 ??CLOSED ??0 slugs awaiting a response.

27. ??**D1 RELOCATION MEASURED** ??run 5 (53/0, 43 s): `WhileLoop 3??`, `Diagram 170??73`, 1.2=#1133/1170,
   1.5=#1134/1194, 1.7=#1135/1215; all 23 moves; 8 SRs; ControlTerminal 114 intact; collateral 0, d19 clean;
   S4b terms 1183/1204/1225 wire 0. **Re-wire list = `tools/bench/build_d1_v0.json`, 109 terminals / 24 uids.**
   Long form ??`archive/2026-09-17-status-d1-phase-full-narrative.md` 짠0.
28. ?뵶 **PHASE "full" NOT WRITTEN. N1 / F1 / F2 NOT RUN.** The sentinel test needs a comparison primitive +
   literals **inside** each loop body. **THREE prior-art rounds, 21 findings, 0 novel, all accepted and disposed**
   (`??priorart-d1-full-route{,-rev2,-rev3}.md`) ??what is left is a **DECISION, not a measurement**.
   ?좑툘 Two inherited premises **withdrawn**: an NI-example `copy_*` donor is **not** a recorded crash (vi.lib only,
   `keystone-op-spec.md:136-143`; worked twice, `build_opconstvalue_v1.log:21-25`), and **짠11f.2 never names
   `copy_by_index`** ??it orders `OpConstValue`/`build_case` first, now **discharged in writing**. ??NEXT.
28b. ??**RE-WIRE SOURCE MAP COMPLETE ??82/82, NO LabVIEW RUN NEEDED** (81 offline join + w3268 already measured,
   `diag_autofocus_border.log:19-26` = **driven by `Diagram` 639**) ??the "`#376 frame index` = the loop's
   iteration terminal `i`" rule-1a hazard is **REFUTED**. Node 41 쨌 LoopTunnel 15 쨌 LeftSR 10 쨌 CtlTerm 6 쨌
   NumConst 5. Remainders: one `panel_wiring` read for w3268's driver; `max_terms=8` for its sinks.
28c/28d. ??**109 cut terminals ARE addressable: 81 by name, 28 by INDEX** (the record stores `term_index` +
   `is_source`; `wire_sr` / `OpStopFromNode_v0` address body `Terminals[index]`) ??"19 unreachable" **withdrawn**.
   ?윞 Fresh-copy ExecState: the discriminator is **PRELOAD**, never varied in a controlled pair (3?? split);
   `d1-build-plan.md:203` + `build_d1_v0.py:419` still say "headlessly" ??**withdrawn**, needs a plan edit.
28e. ?뵶 **`copy_by_index` MUST start on a FRESH LabVIEW instance** (recorded **Errno 22**); its gate reads
   `exec_state(**MOVE_DST**)`, not the target. `diag_d1_full_route.py` is CORRECTED, now refuses P2 without
   `FRESH_INSTANCE_DONE`, and was **not run** for exactly this reason. ??archive 짠0b.
29. ??**`OpStopFromNode_v0.vi` BUILT + SAVED, 20/2**; the write is MEASURED (cond. terminal 119, wire 0 ??**147**,
   same uid on the body node's Boolean output). **T5 CLOSED ON THE RECORD, no run needed** ??`NAMES.md:788` "never
   gate on ExecState while a required input is unwired"; the donor's `path` IS required, so run 3's 0???? said
   nothing about the op. T6's answer is published (`toolkit-capabilities.md:48`); it survives as a **control** only.
30/30b. ?뵶 **STREAMING TSV (짠7.1) NOT BUILT** (review stopped it, 8 findings). ??`#376 save trace.vi` = **7 nodes,
   NO file I/O**; it accumulates and calls `save N xyz traces.vi` **periodically** from a Case. ??plan 짠7.3/짠11.9.
31. ?뵶 **RETROSPECTIVE WINDOWS BROKEN ??`repeated-failure-class` 횞2 (threshold 3).** `retrospective.py` takes the
   cycle start from the PREVIOUS retrospective's timestamp, so cycles 15/16 reviewed <1-min windows with **zero
   builds**; `--since-hours` does NOT override it (`tools/retrospective.py:282-286`). Fix: make it override, or use
   the oldest unreviewed build log. Also **no `docs/cycle16-plan.md`** ??the scope check cannot run.

## NEXT
?뵶 **JUDGEMENT ??ONE question now blocks PHASE "full", and it is a ROUTE CHOICE, not a measurement.**
짠11f.2's "`OpConstValue`/`build_case` **first**" is **discharged in writing** (both are readers / a top-level Case
creator ??they cannot produce a node), so its **"additive builds"** fallback is reached. Which one:
 (a) `copy_by_index` + `move_in` ??NOT an additive build, so not covered by 짠11f.2 as written; needs a fresh
     instance; NI-example donors are now known-good, so the donor need not be the working copy;
 (b) `Constant.Terminal` **634AC04** + `Terminal.Connect Wire` **6349C03** ??a copied constant feeding a copied
     primitive's required input, **creating no panel object**; additive on a proven front half;
 (c) wrap erdosmiller `Create Equal.vi` / `Create Constant.vi` in the **`queue_node` pattern**
     (`gscript.py:928-934`, "places one primitive on any diagram", 162/162); already censused
     (`archive/bench-2026-09-14-stage2-toolkit/probe_queue_vis.log:9-10`).
 (b)/(c) are new/additive ops and `cycle15-plan.md:104`'s freeze governs ??**only judgement may lift it.** Behind:
 짠7.1's TSV route (OPEN 30); OPEN 16 the GPU tail; F1 60 s (??.3 GB) vs 5 min.
?윟 MATERIAL, needs no decision: the controlled **preload pair** for 28d (one line); w3268's driver via one
`panel_wiring` read + `max_terms=8` for its sinks (28b). Then, once (a)/(b)/(c) is chosen: PHASE "full" against
`tools/bench/build_d1_v0.json` (**109 terminals ??81 by name, 28 by index**) ??N1 ??F1 ??F2.

## Where to look
`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 `docs/toolkit-capabilities.md` 쨌 **`docs/d1-build-plan.md`
= the build order; relocation DONE, PHASE "full" open** 쨌 `tools/recipes/build_d1_v0.py` 쨌 `docs/gpu-backend.md`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

# PRIOR-ART REVIEW — `OpCreateEqual_v0` / `OpCreateConst_v0` (trigger: new-op)

**Seven findings, none of them "you may not do this".** Two are about the *artifacts* (a generic wrapper-builder for exactly this job already exists and has been run three times; one of those runs blocked for the reason `Create Equal.vi`'s inputs will reproduce), two are about cheaper already-built halves the plan does not price, and three are about the record. `Create Constant.vi` — the half the plan says it is least sure about — is the half with the most prior art.

---

# PART A — THE DIRECTION

## A1 — decided, and the decision is the plan's own. **No slug.**

`docs/d1-build-plan.md:645-650` (§11g.1, judgement, 2026-09-17) already chose route (c) by name and lifted `docs/cycle15-plan.md:104`'s freeze "for **exactly these two ops**", and `:651-653` (§11g.2) says no further prior-art dispatch is owed "unless an op beyond the two in (1) is created". The plan cites this itself. I record it so the judgement session knows the *direction* question is closed in writing and that everything below is about the artifacts and the record — **I am not emitting a slug for A1**, because blocking a build on "you already decided to do this" is an over-broad match.

## A2 `refuted-already` — the choice "erdosmiller `Create *.vi` vs. the documented VI-Server method" has been put to a peer twice here, and **both times the peer refused the library VI and named the documented method**. Neither precedent is cited.

Both sides, verbatim:

> **The plan:** "§11g.1 chose **route (c)**: wrap the erdosmiller LV-Scripting creators … (b) `Constant.Terminal` **634AC04** + `Terminal.Connect Wire` **6349C03** … is recorded as the alternative."

- `archive/peer/2026-09-14-stage2-shiftreg-primitive.md:85` — *"That is the documented creation route the plan should try first. It is substantially cleaner than using `Exit While Loop.vi` as an **undocumented side-effect generator**. I found no writable WhileLoop property or `New VI Object` style that should be preferred. **The direct Loop invoke method is the answer.**"* Disposition at `:126-129`: accepted and acted on — `docs/stage2-assembly-step-a.md` was rewritten around the direct method, `OpAddShiftReg_v0` was built on `Loop.Add Shift Register` 6361000, and *"the `Exit While Loop` side-effect route was not touched."*
- The same precedent was re-applied **~18 hours before this plan**, in this cycle: `archive/peer/2026-09-17-priorart-d1-op-exitwhile-node.md:259` cites it to refuse an erdosmiller front-half, and the outcome is written into the capability table — `docs/toolkit-capabilities.md:51`: *"Route chosen by its prior-art review, which **refused** the erdosmiller `Exit While Loop.vi` front-half swap."* `OpStopFromNode_v0`, the op this same plan depends on, exists **because** that refusal was accepted.

**Does it still apply? Partly, and I will not overstate it.** The shift-register precedent was about using a library VI for a *side effect* it does not document (`Exit While Loop.vi`'s `Shift Registers` input); `Create Equal.vi` / `Create Constant.vi` doing their documented job is a weaker case, and the `queue_node` family (`docs/toolkit-capabilities.md:32`) is itself four library creators that work. So this finding covers the **unstated precedent and the unpriced (b)** — not the conclusion. Route (b) is not a sketch: see B3, where it turns out to be one property ID away from two ops that are already built.

## A3 `contradicted` — "162/162" is the tracker VI's gate count, not the queue ops'. The wrapper shape's own evidence is **7/7**.

Both sides:

- **The plan:** "the `queue_node` pattern … the wrapper shape that already placed `Create Obtain Queue` / `Enqueue Element` / `Dequeue Element` / `Release Queue` on arbitrary diagrams (**4 ops, core 162/162**)." Repeated at `STATUS.md:99-100`.
- `STATUS.md:73` (Where things stand) — *"`Track_v6_CPU_core_v0.vi` 69/69 · `…queue_v0.vi` **162/162**"*, i.e. 162/162 is the gate count of **`Track_v6_CPU_queue_v0.vi`**, a replay tracker.
- `docs/toolkit-capabilities.md:32` — the four `OpQueue*_v0` ops' own evidence line is *"`test_opqueue.log` **7/7**: typed queue, enqueue inside a loop through auto tunnels, element 1280 dequeued in a 0.09 s run"*.

**Why it is a finding and not pedantry:** 162/162 is being used to say how hard the *wrapper shape* has been exercised, and the number belongs to a different artifact. The shape's real record is 7/7 plus whatever the tracker build exercised indirectly. **Scope:** covers the figure and the sentence that attaches it to the pattern. It does not question that the queue ops work.

## A4 `unread-evidence` — `docs/stage2-assembly-step-e.md` (status: `current`) specifies **this exact artifact under another name**, in a **different** wrapper pattern, and carries the library census the plan re-derives.

- `docs/stage2-assembly-step-e.md:213-215` — a detector *"created by wrapping erdosmiller `Create Less?.vi` / **`Create Equal.vi`** / `Create Or Array Elements.vi` as ops in the **`OpBuildIA_v0` pattern**"*; `:221-222` — *"Toolkit gaps (each = one op + one functional test, the row-32 pattern): `OpBuildLess_v0`/**`OpBuildEqual_v0`**, `OpBuildOrArray_v0`, `OpBuildCaseBool_v0` …"*.
- The same file, `:39-41`, holds the library census the plan sources from `probe_queue_vis.log`: *"**`Create Less?.vi` does not exist** in the library (Equal / Or Array / And Array / Index Array / Case (Boolean) / Exit Structure do)."*

So a current document already names the op (`OpBuildEqual_v0`), already chose a **different** template for it (`OpBuildIA_v0`, not `queue_node`), and already answers "is the creator there". The plan's question 1 lists `OpConstValue*`, `build_case`, `OpBuildIA`, `copy_by_index` — it knows the pattern but not that the op was specified against it. **Scope:** it does not say `OpBuildIA_v0` is the better template; it says the plan is choosing between two in-house templates without knowing the other one was already selected for this node.

---

# PART B — THE ARTIFACT

## B1 `already-built` — a **generic op-builder for an erdosmiller creator** exists and has been run to completion three times. The plan does not mention it.

- `tools/recipes/build_opcreator.py:1-8` — *"generic op builder for an erdosmiller node CREATOR: `Op<Name>_v0.vi` places the creator's node on a target's top-level diagram at `location (0, 0)` … copy `OpBuildIA_v0`, **swap the creator SubVI**, wire `PN VI.Block Diagram` → `Diagram in` and the location control, then **give every remaining REQUIRED input a front-panel control (probe terminals until ExecState == 1)**, purge junk Invokes, save, and **test on a scratch target**."* Usage line `:5-6` is literally `--creator "<Create X.vi>" --op Op<Name>_v0`.
- It works: `tools/bench/creators_chain.log:15-21` — `Create Flatten to String.vi` → `OpBuildFlatten_v0`, *"assembled … ExecState 1 controls [(5, 'anything')] / saved / test: new nodes on scratch: [(622, 'FlattenString', (1300, 700))]"*; `:32-38` — the same for `Create Unflatten from String.vi` → `OpBuildUnflatten_v0`.
- Driver pattern for running such an op is built too: `tools/recipes/build_opclfn.py:150` — `creator_node(OP, class, position)` *"run a creator op (`OpBuildFlatten_v0` / `OpBuildUnflatten_v0`) on OP; returns the new node's uid"*.

**Scope, tightly, because this must not cost more than it should.** `build_opcreator.py` places the node on the **top-level** diagram (`:3` and `:50`: `PN VI.Block Diagram → 'Diagram in'`), so it does **not** do the named-subdiagram placement D1 needs, and the `gscript.build_creator(...)` wrapper its docstring promises at `:7` was never written (no `def build_creator` in `tools/gscript.py`; no `tools/bench/build_op_*.log` exists). The finding is: **the two ops are a parameter change plus a diagram-addressing change to an existing, exercised recipe**, not new construction — and the plan prices them as new.

## B2 `already-failed` — the generic creator-wrapper was pointed at a creator with **refnum inputs** and every run then **blocked behind a modal dialog**. `Create Equal.vi`'s `x`/`y` are that same kind of input, and the plan sources only one of them.

- The attempt: `tools/bench/caseop_chain.py:6-7` → `build_opcreator.py --creator "Create Case Structure.vi" --op OpBuildCase_v0`. Result `tools/bench/caseop_chain.log:18-21` — *"assembled … ExecState 1 controls [(5, 'Selector'), (7, 'Inputs'), (9, 'Frames')] / saved / **test run: run blocked behind a modal dialog (dismissed by watchdog after 8s)** / test: new nodes on scratch: [(622, 'CaseStructure', …)]"*.
- The cause, written down: `docs/NAMES.md:473-475` — *"**Never SetControlValue on `Selector`.** It is a **terminal refnum**; writing 0 into it makes the creator call `Connect Wire` with an invalid reference → **error 1055 dialog** … that blocks the run"*; `:478-480` — *"The Selector error is **NOT silenced** by an error-out indicator … **Until the op can be given a real Selector terminal refnum, every case-structure creation blocks an unattended run.**"*
- That `Create Equal.vi`'s inputs are the same kind: `archive/2026-08-31-status-full-assembly-narrative.md:526-529` — *"The library's `Create *.vi` family is a refnum algebra — verified on `Create Add.vi` (`x`,`y` in as **wire-source refnums**, `x+y` out as a **terminal refnum**) and `Create Constant.vi` (`Type`/`Value` in, **`Terminal` out**)."*
- And the constraint that follows, from the same page, `:531-534`: *"refnums live only inside **one VI's dataflow**, so a chain of node creation must sit in **one fused op**, never split across COM calls. That is why `OpLoopKernel_v0` had to fuse Create For Loop → Create SubVI."*

**Does the plan address the cause or repeat it?** Half and half, and this is the finding that matters most.
- **Addressed:** choosing the `queue_node` shape is exactly the recorded fix — `tools/gscript.py:928-934` fetches the refnum *inside* the op (`Traverse src_cls[src_index] . src_name` via Get Outputs) instead of setting it over COM. For `Equal?`'s first input that is solved.
- **Repeated:** the plan builds **two separate ops** and `OpCreateConst_v0` returns nothing a second op run can use — `Create Constant.vi`'s output is `Terminal` (a refnum, `tools/bench/erdos_creators.log:41`), which dies with the op's dataflow. The plan's `OpCreateEqual_v0` input list names **one** source node (`Class Name`/`index`/`Names`); nothing in it says how the constant's terminal reaches `y`. Either the two creations fuse into one op (the `:531-534` rule), or `OpCreateEqual_v0` needs a second addressing path that finds the already-placed constant on the body diagram — and that path is not specified.

**Scope:** covers the split into two ops and the unsourced second input. It does not say the `queue_node` shape fails; it says the cause that killed `OpBuildCase_v0` is still live on the input the plan leaves unwired.

## B3 `helper-exists` — for the constant (the plan's own least-sure half) the documented method is **one property ID away from two ops that already exist**, and it removes both variant inputs from the COM boundary. Also: `Text.Text` **writing** and **named-subdiagram addressing** are each already built.

Taking the plan's three sub-questions in turn:

**(i) Creating a typed constant with a value.** `archive/peer/2026-09-06-fp-control-creation-scripting-routes.md:36` — *"`Create Constant` | Creates and returns a **block-diagram constant for the terminal; optional `Value` input**"* (NI API reference, cited there). ID catalogued at `docs/NAMES.md:213` and `docs/vi-server-ids.json:69` (`"Terminal.Create Constant": "6349C00"`). The fleet already owns **two ops on the identical ladder with the sibling IDs**: `tools/gscript.py:2155-2161` — `create_control` = `Terminal.Create Control` **6349C01**, *"OpCreateControl_v0, built by script 2026-09-06 on the ladder VI→Block Diagram→Nodes[]→IA→Terminals[]→IA"*, and `tools/gscript.py:2180-2182` — `create_indicator` = **6349C02**, *"same ladder"*. A constant creator is that op with the ID changed — and because it creates the constant **from the sink terminal**, it is **correctly typed and already wired**, so `Create Constant.vi`'s two **variant** inputs (`Type`, `Value` — `tools/bench/erdos_creators.log:40,42`, both reading `None`) never have to cross COM at all. That boundary is not hypothetical: `archive/2026-09-15-status-stage2-cycles-1-7.md:290` records numeric values coming back through it as *"`None`, no error (Variant-of-numeric marshalling suspected)"*, and `archive/2026-08-31-status-full-assembly-narrative.md:576-579` records a pywin32→LabVIEW array-of-cluster write that **LabVIEW discarded while returning `S_OK`**.

**(ii) "Does anything in the fleet set a constant's value after creating it?"** No op does — but **both halves are built and measured**. `docs/NAMES.md:924-927` — `VI Server:DigitalNumericConstant` `634D007` **NumText** (*"the `Numeric Text` reference → `Text.Text` 632D800"*), measured by attaching each. The read direction is already inside `OpConstValueN_v1` (`docs/toolkit-capabilities.md:47`). And **writing `Text.Text` is already an op**: `docs/d1-build-plan.md:96-97` — *"built a second time as `OpSetLabel_v0` (`gscript.py:2451-2454`, `Node.Label` 6359001 → `Text.Text` **write**)"*.

**(iii) Named-subdiagram addressing is not unique to `queue_node`.** `tools/gscript.py:2451-2458` — `set_node_label(target, diagram_index, node_index, text)` addresses *"`Nodes[node_index]` of Traverse `"Diagram"[diagram_index]`"* **and performs a property write**. That is the plan's required addressing and a write, in one already-built op, on the `OpNetInfo_v1` ladder.

**Scope, honestly.** `create_control` / `create_indicator` walk the **top-level** `Nodes[]` and *"cannot reach nodes inside frames — their ladder walks the TOP-LEVEL `Nodes[]` (index 1+ is out of range → an 8 s dialog per try)"* (`docs/NAMES.md:460-461`). So route (b) needs the same subdiagram work route (c) needs; it is **not free**, and I am not calling it cheaper. The finding is that the plan states (b) as a bare ID pair and never notices it is a one-ID derivative of two built ops that also dissolves the variant problem — so the two routes have never actually been priced against each other.

## B4 `already-measured` — the acceptance gate the plan proposes ("owner chain uid → body `Diagram` → the right `WhileLoop`") has already been run, with the same reader, on these three bodies.

> **The plan:** "Acceptance for each: … the node appears on the named subdiagram (owner chain uid → body Diagram → the right WhileLoop)".

- `tools/bench/build_d1_v0_run5.log:100-108` — `OpOwnerChain_v1` on three Constant-class objects placed inside the new 1.5 body: *"uid **3529** → owner 'Diagram' uid **1194** … uid 1194 → owner 'WhileLoop' uid **1134** … PASS"*, likewise `#3560` and `#3447`; `:109` — *"FACT 1.5 body Diagram#1194 now holds [10407, 25033, 48, 25048, **3529**, 25054, **3560**, 25056, **3447**, 25062]"*.
- Already recorded as prior art once: `archive/peer/2026-09-17-priorart-d1-full-route-rev2.md:422-426` — *"Run 5 **already measured** a Constant `move_in`-ed into a freshly created While body with the same reader, three times … with `ControlTerminal` still 114. The only untested variable is **provenance**."*

**Scope:** the three objects were `ControlReferenceConstant`s **relocated** into the body, not primitives freshly created there — so the *provenance* half is genuinely untested and the new ops must still be run. What is already on file is the **gate**: the owner-chain assertion and its expected uids. Write the test against `#1170`/`#1194`/`#1215` and `#1133`/`#1134`/`#1135` from `STATUS.md:79-82`; do not re-derive them.

---

## What I did **not** find, so nobody re-checks it

- **No refutation of the direction itself.** Nothing in `archive/`, the retrospectives or a superseded plan section argues that a sentinel test must not be built from a comparison primitive plus a literal inside the body.
- **The library census is right.** `Create Equal.vi` and `Create Constant.vi` both exist and are terminal-censused: `tools/bench/probe_queue_vis.log:9-10`, and `Create Constant.vi` independently at `tools/bench/erdos_creators.log:34-42`. `docs/stage2-assembly-step-e.md:39-41` confirms it from the other side (`Create Less?.vi` is the one that is absent).
- **`queue_node`'s docstring says what the plan says it says.** `tools/gscript.py:928-934`, *"Place one queue primitive on Traverse `'Diagram'[diagram_index]` of `target`"*; `.claude/skills/labview-automation/references/vi-scripting.md:308` says what the plan quotes.
- **One fact that supports the plan and is worth having in the recipe:** `OpForLoop_v0` **already calls `Create Constant.vi` three times** on its own diagram (`tools/bench/probe_opforloop.log:12-13,16`) — `Type` wired from a constant inside the op, **`Value` wire 0 (unwired)**. So the creator is exercised in this fleet, in exactly the shape that takes the *default* value. A sentinel that can be expressed with a default (`0`, `FALSE`) needs no value-setting at all; only the `−1` literal does.

---

```
PRIOR-ART: refuted-already   (A2 — archive/peer/2026-09-14-stage2-shiftreg-primitive.md:85 + :126-129, and archive/peer/2026-09-17-priorart-d1-op-exitwhile-node.md:259 / docs/toolkit-capabilities.md:51; covers the uncited precedent and the unpriced route (b), NOT the conclusion)
PRIOR-ART: contradicted      (A3 — the plan's "4 ops, core 162/162" and STATUS.md:99-100 vs STATUS.md:73 "…queue_v0.vi 162/162" and docs/toolkit-capabilities.md:32 "test_opqueue.log 7/7")
PRIOR-ART: unread-evidence   (A4 — docs/stage2-assembly-step-e.md:213-215, :221-222, :39-41 — this op specified as OpBuildEqual_v0 in the OpBuildIA_v0 pattern, plus the library census)
PRIOR-ART: already-built     (B1 — tools/recipes/build_opcreator.py:1-8 + tools/bench/creators_chain.log:15-21,32-38; generic erdosmiller-creator wrapper, run 3x. Scope: top-level diagram only; gscript.build_creator was never written)
PRIOR-ART: already-failed    (B2 — tools/bench/caseop_chain.log:20 + docs/NAMES.md:473-475,478-480; refnum input set over COM ⇒ 1055 modal on every run. queue_node fixes input #1; the constant's Terminal refnum into Equal.y is unsourced, cf. archive/2026-08-31-status-full-assembly-narrative.md:531-534 "one fused op")
PRIOR-ART: helper-exists     (B3 — archive/peer/2026-09-06-fp-control-creation-scripting-routes.md:36 + docs/vi-server-ids.json:69 + tools/gscript.py:2155-2161,:2180-2182 (6349C01/02 ladder); docs/NAMES.md:924-927 + docs/d1-build-plan.md:96-97 / tools/gscript.py:2451-2454 (Text.Text write); tools/gscript.py:2451-2458 (Diagram-index + Nodes[] addressing). Scope: docs/NAMES.md:460-461 — that ladder is top-level only)
PRIOR-ART: already-measured  (B4 — tools/bench/build_d1_v0_run5.log:100-109 + archive/peer/2026-09-17-priorart-d1-full-route-rev2.md:422-426; the owner-chain gate and its uids. Scope: relocated ControlReferenceConstants, so fresh-creation provenance is still untested)
```

**The cheapest way to release most of this:** B1/B4 are `FIXED:` lines away (derive the recipe from `build_opcreator.py`, reuse run 5's gate). A3/A4 are one edit each. **B2 is the one that should change the build**: decide, in writing, whether `Equal?`'s `y` comes from a fused single op or from a second addressing path, before the recipe is written — that is the input that took `OpBuildCase_v0` down.

## Sources

(extract from answer)

## What was done with it

**ALL SEVEN FINDINGS ACCEPTED; NONE REFUTED.** Material session `cycle15-d1-full-build-3`, 2026-09-17. The
review changed the recipe before it was written, which is the intended order, and the disposition is the edit:
`tools/recipes/build_opsentinel_ops.py` opens with a finding-by-finding block that cites every file and line
below. One finding (B2) is accepted AND left open, because closing it needs a THIRD op and that is judgement.

| finding | what changed |
|---|---|
| **B1** `already-built` | the recipe is no longer new construction: it is `build_opqueue.py`'s donor route (`OpExitLoop_v0`, whose `Diagram in` already comes from `Traverse('Diagram')[index 2]` — the named-subdiagram half `build_opcreator.py` lacks) PLUS `build_opcreator.py:59-72`'s required-input probe loop, in shape. Recorded with the reviewer's scope note (`build_opcreator.py` is top-level only; `gscript.build_creator` was never written) |
| **B2** `already-failed` | **no refnum is set over COM anywhere in this recipe.** `Create Equal.vi`'s `x`/`y` are fetched inside the op from `Get Outputs` of a Traverse-named node (`queue_node`'s fix); `Create Constant.vi` has no refnum input. 🔴 The half the review says "should change the build" — where `Equal?`'s `y` comes from — is **NOT closed here and is flagged as the session's OPEN question**: a constant is not a `Node`, so no `Get Outputs` reaches it, and the creator's `Terminal` output dies with its op's dataflow. Both candidate answers (a FUSED create-const-and-connect op, or `Constant.Terminal` 634AC04 → `Terminal.Connect Wire` 6349C03) are a **third** op, beyond the two §11g.1 authorises |
| **B3** `helper-exists` | `Terminal.Create Constant` 6349C00 recorded in the recipe as the documented alternative that would also answer B2 (it creates the constant FROM the sink terminal, typed and already wired) together with the reviewer's own scope note that its ladder is top-level only (`docs/NAMES.md:460-461`), so it is **not** cheaper. Not built (third op) |
| **B4** `already-measured` | the functional test asserts the owner chain with the SAME reader (`read_owner`/`OpOwnerChain_v1`) instead of re-deriving a gate, and records that run 5's objects were *relocated* `ControlReferenceConstant`s, so fresh-creation **provenance** is the untested variable this test buys |
| **A2** `refuted-already` | both uncited precedents (`…stage2-shiftreg-primitive.md:85`, `…priorart-d1-op-exitwhile-node.md:259`) are now cited in the recipe, with the reviewer's own scope note that they concern an UNDOCUMENTED side effect and so apply weakly here |
| **A3** `contradicted` | every "162/162" attached to the wrapper shape is corrected to the queue ops' own evidence, `test_opqueue.log` **7/7** (`docs/toolkit-capabilities.md:32`) |
| **A4** `unread-evidence` | `docs/stage2-assembly-step-e.md:221-222`'s `OpBuildEqual_v0` (the `OpBuildIA_v0` template) is recorded, with the reason the `queue_node` template is kept anyway: `OpBuildIA_v0`'s `Diagram in` is the **top-level** one, and D1 needs a named subdiagram. The requirement decides it, not preference |

**B2 also changed a SECOND file, and that is why it is cited twice.** `tools/recipes/build_d1_v0.py`'s
`--full` refusal listed the sentinel comparison and its literal as blocker (b) and plan §7.1's streaming TSV as
blocker (c). Both are now wrong: (b) is BUILT and functional 23/0, and (c) moved to D2 under §11f.1. The refusal
now names the one blocker that is actually left — **B2's own finding**, where `Equal?`'s `y` comes from — so a
future session reads the current state instead of a superseded list. (This recipe's direction has had four
prior-art rounds of its own — `…priorart-d1-build{,-rev3,-rev4,-rev4b,-rev4c}.md` — and `d1-build-plan.md`
§11g.2 says no further dispatch is owed for it; the gate fires only because a NEWER review now exists.)

FIXED: already-built - `tools/recipes/build_opsentinel_ops.py`:17 - the recipe is derived from build_opcreator.py's probe loop and build_opqueue.py's donor route, not written fresh.
FIXED: already-failed - `tools/recipes/build_d1_v0.py`:857 - the --full refusal now names B2's unsourced Equal?.y as the one remaining blocker, replacing two statements this review and §11f.1 made false.
FIXED: already-failed - `tools/recipes/build_opsentinel_ops.py`:23 - no refnum input is set over COM; the remaining half (Equal?'s y source) is flagged OPEN for judgement, not built around.
FIXED: helper-exists - `tools/recipes/build_opsentinel_ops.py`:36 - Terminal.Create Constant 6349C00 recorded as the documented alternative with its top-level-only scope note.
FIXED: already-measured - `tools/recipes/build_opsentinel_ops.py`:41 - the functional test reuses read_owner/OpOwnerChain_v1 and names provenance as the untested variable.
FIXED: refuted-already - `tools/recipes/build_opsentinel_ops.py`:44 - both uncited peer precedents are cited, with their scope.
FIXED: contradicted - `tools/recipes/build_opsentinel_ops.py`:54 - 162/162 corrected to test_opqueue.log 7/7 wherever it described the wrapper shape.
FIXED: unread-evidence - `tools/recipes/build_opsentinel_ops.py`:56 - OpBuildEqual_v0 / the OpBuildIA_v0 template recorded, with the measured reason queue_node is kept.
