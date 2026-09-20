# priorart-d1-op-exitwhile-node

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $5.0480  in 42 / out 37132 / cache-create 276723 / cache-read 2704572  (518s, 34 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (522s)
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
NEW OP PROPOSED: `OpExitWhileNode_v0.vi` ??wire a While loop's CONDITIONAL TERMINAL from a Boolean
terminal of a NODE INSIDE THE LOOP BODY (not from a front-panel control chosen by name).

WHY NOW: docs/d1-build-plan.md 짠11c/짠9a stops the three new D1 loops (1.2 tracking, 1.5 focus,
1.7 writer) on END-OF-STREAM SENTINELS: each loop dequeues its queue, compares the dequeued value to
the sentinel (-1 / empty array), and the comparison's Boolean output drives that loop's conditional
terminal. docs/d1-build-plan.md 짠11e.2 (judgement session, 2026-09-17) lifted the cycle-15 op freeze
NARROWLY for exactly this op.

WHAT EXISTS AND WHAT I INTEND TO REUSE (stated so you can attack it):
 - `OpExitWhile_v0` (docs/toolkit-capabilities.md:31, test_opexitwhile.log 5/5) already wires a While
   loop's conditional terminal; its front half is "VI.Block Diagram -> Get Controls(Control Names) ->
   Index Array[0] -> `Exit While Loop.vi` `Stop Condition`"
   (archive/bench-2026-09-14-stage2-toolkit/build_opexitwhile.py:2-3).
 - archive/peer/2026-09-17-priorart-priorart-d1-build-rev4c.md B1 verdict `helper-exists` says the
   change is a FRONT-HALF SWAP, the swap this fleet built four times (OpWireSR_* family:
   "body node via Loop.Diagram -> Nodes[] -> Terminals[]"; OpTunnelInd_v0 from OpSetIndexMode_v0;
   OpLoopEndRef_v0 from OpWhileCast_v0).
 - `OpLoopEndRef_v0` (16/0) READS a conditional terminal; it does not write one.
 - docs/NAMES.md:751-752 ??`Exit While Loop.vi` pane: 9 `Stop Condition` is a TERMINAL REFNUM input.

PLANNED BUILD (additive, nothing deleted from the template):
 copy OpExitWhile_v0 -> OpExitWhileNode_v0; delete the `Get Controls` + `Index Array`(control-name)
 front half; replace it with the OpWireSR_* body-node addressing chain ??WhileLoop-typed seed
 (OpWhileCast_v0) -> `Loop.Diagram` -> `Nodes[]` -> Index Array(node index) -> `Node.Terminals[]` ->
 Index Array(term index) -> `Exit While Loop.vi` `Stop Condition`; inputs `vi path`, `index`
 (WhileLoop Traverse index), `node index`, `term index`. Functional test on a scratch VI: a While loop
 whose body holds a comparison node, ExecState 0 -> 1, the VI runs and stops.

ASK: has this op (or this exact front-half swap) already been built, attempted, failed, or measured
here under any name? Is there a helper in tools/gscript.py that already writes a conditional terminal
from a body node? Does any archived exchange or superseded plan already settle or refute this route?


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-17
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.
Narrative relocated **verbatim** (rule 4) to `archive/2026-09-16-status-cycles-11-13-narrative.md`,
`??2026-09-17-status-d0-and-gpu-narrative.md`, `??cycle15-narrative.md`, **`??d1-rev4-narrative.md`** (the four
D1 runs). ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this from disk.

## START HERE
1. **`docs/pre-rig-master-plan.md` is THE plan**; settled decisions **`docs/decisions.md`**; cycle plan
   `docs/cycle15-plan.md`; **the build plan is `docs/d1-build-plan.md` REV 4 ??read 짠0-BLOCKER first**, then 짠5
   (the node-by-node move table) and 짠10 (the S/N1/F1/F2 contract). Recipe: `tools/recipes/build_d1_v0.py`.
2. ??Prior-art gate live (`REFUTED:`/`FIXED:`); `premature_build` (b) exempts a RE-RUN (22). Retrospectives 10??4.
3. ??**Scripting EDITS are silently declined until the target's FRONT PANEL has been opened** ??`ensure_loaded()`.
4. ??**A fixed op PATH is served from LabVIEW's memory, not from disk** ??unique working-copy filename per run.

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  owner:
  since:
  purpose:
# 2026-09-17 06:5x-07:2x material/cycle15-d1-build-rev4b: RELEASED. FOUR runs of build_d1_v0.py PHASE "relocate"
# on uniquely-named COPIES under claudeDev; md5 2a78e17c449... asserted before AND after every run; the run-4
# copy was created and DELETED in the same run. No edit to any original, no GUI, no hardware.
# Handles 30,682 -> 38,336 (LabVIEW restarted at the start of run 4; it had reached 54,726).
# Earlier holders (all RELEASED, all md5-clean, none touched an original) -> the status archives of 2026-09-16/17.
```
**Never assume an instance exited**: `tasklist | grep -i labview`, kill strays. Fresh instances ??1,500 handles;
unique scratch VI name per run, deleted in the same run.

## HARDWARE ??permission follows the RIG STATE. Current state: **遺꾪빐 / DISASSEMBLED ??everything allowed**

| rig state | motors (PI 쨌 rotor 쨌 magnet) | **ASI piezo** | camera |
|---|---|---|---|
| **遺꾪빐 ??disassembled ??WE ARE HERE** | ??| ??| ??|
| 議곕┰ ??assembled | ??| ??| ??|
| ?ㅽ뿕以???experiment running | ??| ??| ??|

?좑툘 **The ASI carve-out is RETIRED** (rule 1b). **Only the user announces a state change**; never infer one, never
ask per incident. Instruments: rotor counter **0** 쨌 magnet full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz,
never write `BinningHorizontal`; **a session open RESETS ROI *and* exposure** ??the acquisition loop applies the
contract itself (`tools/bench/camera_contract.py`). **No beads while disassembled**; fixture work unaffected
(10,043 frames, `archive/bench-2026-09-07-fixture/`).

## Where things stand
**Stage 1 (analysis) CLOSED** ??the seven `docs/main-vi-*` files; raw `archive/benchmarks/INDEX.md` 22??1.
**Stage 2 (assembly) IN PROGRESS**: `Track_v6_CPU_core_v0.vi` 69/69 쨌 `??queue_v0.vi` 162/162 ??**say it exactly:**
bit-identical for the **first 10,018 frames only**, and both are **replay** artefacts (recorded TIFFs, `FOR` loops,
no acquisition, no stop). **THE GAP:** 168 ops, 116 recipes, 220 peers ??**zero runnable experimental VIs**.

## OPEN ??one line each; long forms in `archive/2026-09-17-status-cycle15-narrative.md`
1??, 5, 9??2, 18 ??**all in archive 짠9**: PERIODIC auto-reset ungated 쨌 autofocus CLOSED (every 25 frames ??3.6 Hz)
   쨌 27 undisposed peer archives 쨌 startup drives instruments (blocker at assembly) 쨌 A2 54/54, A3 112/170 쨌 doc
   lint 2/4/3 쨌 **TIFF 1.3 MB/frame ??MEASURED ??22 MB/s (2041 files / 2.68 GB in ~20 s) ??bound it or the disk fills**.
13. ??**STOP MEASURED**: `#637` cond. term **648 ??w3457 ??`#11639`**; `stop (end) 2` SEPARATE. ??archive 짠1, 짠10.
14. ?뵶 cycle-15 prior-art only PARTLY disposed (A7/B3 = judgement) ??짠2. 15. ??`bgrun --detach`; 15b. ?뵶 its kill
   misses an ORPHANED grandchild ??짠3. 17. ??D0 16/0; 17b. ?뵶 v3's R11 scored the *restart* ??"stop works" UNPROVEN.
16. ?뵶 **GPU whole-fixture divergence OUTSIDE `decisions.md:38` ??JUDGEMENT.** Now exact (`gpu_n1_deltas.json`):
   beads 0?? **0 exceedances over all 10,043**; **only bead 4** ??10 x, 9 y, 1 flip, n_valid 10,029. ??짠4.
   20/21. ??**CLOSED** ??`py tools/violations.py`: **0 slugs awaiting a response**; devices built. ??짠8.
19. ??**REV 4 WRITTEN**, now **REV 4 + 짠11c + 짠11d**: the move table is **20** moves (not 21) and 짠5d's terminal
   count is **6** (not 5). ??`archive/2026-09-17-status-d1-rev4-narrative.md`.
25. ??**TRANSPORT DECIDED ??짠11c, QUEUES ONLY, folded into rev 4's body** (짠0-BLOCKER/짠11.1/짠11.3 resolved;
   짠3 짠4 짠5a 짠5d 짠6 짠9+짠9a 짠10 rewritten): 1-elem DBL `Q_focus` (1.2 enqueues on the 25-frame tick, timeout 0);
   1-elem `Q_focusback` (1.5 writes, 1.1 polls timeout 0) and **`#12589` STAYS on 1.1**, so w12070/w6929 are
   never cut; **end-of-stream sentinels** stop 1.2/1.5/1.7 (`Q_meta`/`Q_rmeta`/`Q_focus` = **??**,
   `Q_res`/`Q_good` = **empty array**; the writer must not write the sentinel row), so **`ControlTerminal #642`
   stays in 1.1 and no `Local` is needed**. Move table is now **20 moves** (17/2/1) + 1 delete + 1 drop.
26. ??**THREE PRIOR-ART REVIEWS DISPOSED, 19 findings, 0 novel, all accepted** ??rev4 (7), **rev4b (6)**,
   **rev4c (6)**; plus **FOUR hypothesis peers** this session, all ANSWERED. rev4b's B3 hazard was then
   **measured and did not materialise** (0 staying nodes bared). ??archive narrative + plan 짠11d.
19b/19c/24. ??**THE THREE RELOCATION FACTS** (phase P 12/0 쨌 ctlterm 9/0 쨌 step 0 12/12 + 8/8), in plan 짠2/짠5.
   ?좑툘 its "171??71" is the POST-loop-creation count ??transcribing it as the BEFORE count cost run 1. ??archive.
22. ??`premature_build` (b) exempts a RE-RUN (4/4). 23. ??handles CLEARED by a restart (51,220 ??37,290).

27. ??**D1 RELOCATION MEASURED ??`build_d1_v0_run4.log`, 46 pass / 5 fail, 61 s** (PHASE "relocate": structure
   only, nothing re-wired, **not saved**, copy created+deleted in the same run; md5 before AND after). S1 census
   **Diagram 170** (not 171) 쨌 S2 `WhileLoop 3??`, `Diagram 170??73`; 1.2=#1133/1170, 1.5=#1134/1194,
   1.7=#1135/1215 쨌 S2c `#6810 #22700 #22082 #12589 #11639 #642` all still `Diagram#639` 쨌 **all 20 moves pass**
   (17/2/1) 쨌 **S3b cut = 106 terminals over 21 uids**, ??짠8's 13 crossings, **0 staying node bared**, d19 clean,
   **no shift register changed** 쨌 8 SRs created. **The re-wire list is `tools/bench/build_d1_v0.json`.**
   Runs 1?? and their three ANSWERED peers ??`archive/2026-09-17-status-d1-rev4-narrative.md`.
27b. ?뵶 **THE FIVE FAILS ARE MY GATES, NOT THE MACHINE.** S3b-collateral's 13 "bared" terminals are all on uid
   **5058**, the uid the drop returned for the NEW GPU kernel after the old `#5058` was deleted. ?좑툘 **uid reuse is
   the leading explanation, NOT measured** ??peer `d1-s3b-uid-reuse-after-delete` showed the evidence is circular
   (both reads resolve *through* 5058); the two-read test that would settle it is in that file. S3d (6 seam tunnels)
   and S4b횞3 are PHASE-"full" gates left armed: S4b actually **succeeded as a measurement** ??the three new
   loops' conditional terminals are **1183 / 1204 / 1225, all unwired** ??and only failed because I required an
   empty error column where an unwired terminal legitimately reports **1055**.
28. ?뵶 **PHASE "full" IS NOT WRITTEN**; its three blockers are the three NEXT questions below. **N1 / F1 / F2 are
   unreachable until D1 exists ??not run, nothing to report.**

## NEXT
?뵶 **JUDGEMENT ??three questions, in this order** (the relocation is measured and does not depend on them):
1. **`Q_focus` is drop-NEW** ??a skipping `Enqueue` on a full 1-element queue keeps the OLDER slice index, while
   `decisions.md:25`/`frame-ownership-design.md:89-93` decided **latest-wins, "not drop-new"** and
   `decisions.md:21` excludes `Lossy Enqueue`. 짠11c's "freshest wins" is false as written; the queue carries
   **data** ??**rule 1a**. (plan 짠11.7)
2. **Lift the cycle-15 op freeze for D1?** PHASE "full" needs 1?? **additive** ops (plan 짠11.8).
3. **Do `#3447/#3529/#3560` (control refs feeding `#48`) get move-table rows?** (plan 짠11.6)
Behind them: OPEN 16 the GPU tail (only bead 4); F1 60 s (**??.3 GB**) vs the user's 5 min (**??5 GB**).
?윟 Then MATERIAL: write PHASE "full" in `build_d1_v0.py` against the measured re-wire list
(`tools/bench/build_d1_v0.json`, 106 terminals), re-arm S3d/S4b, exclude the deleted uid from S3b ??N1 ??F1 ??F2.

## Where to look
`CLAUDE.md` 쨌 **`docs/decisions.md`** settled 쨌 `docs/NAMES.md` strings 쨌 `docs/toolkit-capabilities.md` API 쨌
**`docs/d1-build-plan.md` REV 4 + 짠11c/짠11d = the build order; relocation DONE, PHASE "full" open** 쨌
`tools/recipes/build_d1_v0.py` 쨌 `docs/restructure-plan-4.6.md` 쨌 `docs/pre-rig-master-plan.md` 쨌
`docs/diagram-hierarchy.md` 쨌 `docs/gpu-backend.md` 쨌 the four status archives (rule 4).


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Prior-art review complete — read-only: no lock, no build, no edit, no `.vi` opened. **5 findings, zero `novel`.** The artifact itself is not built anywhere (I checked five places), but three of its stated premises and two of its construction steps are already answered in our own current files.

---

# PART A — THE DIRECTION

## A1 — cleared, stated so the next round does not re-litigate it

The *direction* (sentinel-driven stops for 1.2/1.5/1.7) is settled **in favour**, and the op is authorised:
- `docs/d1-build-plan.md:658-662` (§11c) and `:246`, `:379` — the three new loops stop on end-of-stream sentinels; nothing reads `stop (end)` but `#11639`.
- `docs/d1-build-plan.md:636` (§11e.2) — "the cycle-15 op freeze is lifted **narrowly**: only ops this plan names as D1 parts — **the stop front-half swap on `OpExitWhile_v0`** (rev4c B1) … each an **additive** build on a proven template."

So rev4c's A2 (`settled-already`, the freeze) **does not block this**. That authorisation is the source of finding A3.

## A2 — no refutation found, with one precedent that bears on the *route*, not the direction

Nothing in `archive/peer/`, the retrospectives or a superseded plan section argues against driving a conditional terminal from a body node. The one adjacent, disposed precedent is cited under B1 — the last time a plan routed a **loop-structure mutation** through erdosmiller `Exit While Loop.vi`, the review refused it.

## A3 `contradicted` — the build calls itself "additive, nothing deleted from the template" and then deletes two nodes; the authorisation it inherits was granted for an additive build

Both sides:

> **The proposal:** "PLANNED BUILD (**additive, nothing deleted from the template**): … **delete** the `Get Controls` + `Index Array`(control-name) front half".

- `docs/d1-build-plan.md:636` — the freeze is lifted for builds that are "**each an additive build on a proven template**". The lift's own wording is the condition.
- `tools/recipes/build_oploopendref_v0.py:26-27` — this project's operative definition: "IT IS THE DONOR, and the build below is **purely ADDITIVE — nothing in it is deleted, so the donor's measured behaviour cannot regress**." Same phrasing in `docs/toolkit-capabilities.md:50` ("Additive build on OpWhileCast_v0 (nothing deleted)").
- The failure class deletion carries here, measured this cycle: `docs/d1-build-plan.md:176` and `:443` — "**wire 464 is ONE net** whose collateral sinks `#237`/`#240` were **bared** by the delete, **pinning ExecState at 0**", with `:444-446`'s note that it produced "**no broken wire and nothing for Remove Bad Wires** — a silent bare terminal". `ExecState 0 → 1` is exactly the gate that shape defeats, and it is the only structural gate the proposal names.

**Honest scope, so this does not cost more work than it should.** Front-half *removal* has succeeded here: `docs/toolkit-capabilities.md:49` — `OpOwnerChain_v1` is "`OpWireSource_v5` with the `Wire` cast and the whole `Wire.Terms[]` front section **removed**", 20 gates pass (`tools/bench/build_opownerchain_v1.log`). So the finding is **not** "deletion is unsafe". It covers (a) the word *additive* and the authorisation at `:636` that rests on it, and (b) the absence of a bared-terminal gate where the precedent carried 20. The cheap repair is available and smaller than the plan's: in `OpExitWhile_v0` the only wire that must change is `IndexArray.element → Exit While Loop.'Stop Condition'` (`archive/bench-2026-09-14-stage2-toolkit/build_opexitwhile.py:136`) — delete **that one wire**, leave `Get Controls` and `Index Array` in place with unwired outputs, and the build is additive in this project's own sense. It does **not** say the op is unnecessary or the direction wrong.

## A4 `unread-evidence` — `docs/stage2-plan.md` item 7 is the document that governs exactly this, and it records that the 5/5 "runs and stops" is a ONE-ITERATION stop

The proposal's whole evidence base for the back half is `docs/toolkit-capabilities.md:31` ("`test_opexitwhile.log` 5/5: ExecState 0 → 1, **the VI runs and stops**"), and its functional test repeats that sentence ("ExecState 0 → 1, the VI runs and stops").

- `docs/stage2-plan.md:90-94` — item 7, uncited by the proposal: "**Stop conditions are evaluated INSIDE the loop.** A front-panel Boolean's terminal wired into a While loop from the top level becomes an input tunnel **read once** before the loop runs (NI: the infinite-loop mistake) … (`OpExitWhile_v0`'s by-name `Stop Condition` is the wiring primitive; **the test uses a control already TRUE, so it terminates after one iteration by design**)."
- The test confirms it: `tools/bench/test_opexitwhile.py:8` ("run the scratch over COM **with the control TRUE**"), `:50` and `:56` (`SetControlValue(STOP, True)` before `g._run`).
- And the recorded provenance of item 7: `archive/peer/2026-09-14-opexitwhile-fail1-duplicate-terminal-names.md:37` — "**if the Boolean terminal remains outside the While Loop, its value is read before loop execution** … The terminal must be inside the loop", disposition at `:47` ("The 'terminal must be inside the loop' warning went into `docs/stage2-plan.md` item 7").

**Consequence for the test, which is why this is a finding and not a footnote:** a scratch VI whose body comparison is constant will stop after one iteration whether or not the terminal is evaluated per-iteration — the same non-discriminating result the 5/5 already has. The test must make the body comparison **change value across iterations** (e.g. the loop's own `Loop Counter` 6361400 compared to a constant — the route `archive/peer/2026-09-14-stage2-step-b-replay-core-plan.md:210` already records as proven) and assert the iteration count, not merely that `_run` returned. **Scope:** covers the proposal's evidence base and its stated acceptance test. It does not question `OpExitWhile_v0`'s 5/5 for what that test actually measured.

---

# PART B — THE ARTIFACT

## B1 `helper-exists` — the DIRECT route writes a conditional terminal with no library VI and nothing deleted: both halves are built and machine-verified, and the plan considers neither

- `docs/NAMES.md:246-249` — "`WhileLoop`: `Loop End Ref` **6362C00 — ✅ VERIFIED ON THE MACHINE 2026-09-17**, data-terminal short name **`LpEndRef`**, **returns a `Terminal` reference** that `Terminal.Is Source?` 634A003 and `Terminal.Connected Wire` 634A000 **accept without a cast**." The conditional terminal is an ordinary `Terminal` object in hand, not an opaque loop property.
- The write method on exactly that class is this fleet's wiring primitive, built four times: `tools/gscript.py:529` — "**`Terminal.Connect Wire` is invoked on the SINK**"; `tools/recipes/build_opwiresr_v0.py:4` — "`Terminal.Connect Wire` 6349C03 (invoked on the SINK, 'Wire Source' = the source)"; `tools/recipes/build_opconnect2.py:5-6` — "Connect Wire **crosses borders**" when the sink is inside a structure. Direction independently sourced: `archive/peer/2026-09-14-stage2-shiftreg-primitive.md:62-67` (labviewwiki, `6349C03`).
- External corroboration already in our files, on this exact operation: `archive/peer/2026-09-14-opexitwhile-fail1-duplicate-terminal-names.md:35` — "VI Scripting connects terminal objects using the terminal `Connect Wire` method", citing the NI thread *"Wiring the conditional terminal of a while loop created by [scripting]"*.
- **The disposed precedent that makes this a prior-art finding rather than a preference.** `archive/peer/2026-09-14-stage2-shiftreg-primitive.md:13-19` — asked because "the plan proposed to use erdosmiller `Exit While Loop.vi`'s never-exercised `Shift Registers` input"; verdict "**ACCEPTED and acted on. The reviewer refused the plan and named a documented creation API**"; `:85` — going through the library VI is using it "as an **undocumented side-effect generator**", and the direct invoke on the typed reference "is the answer"; disposition `:126-129` — the doc was rewritten around the direct method and "**the `Exit While Loop` side-effect route was not touched**". `tools/gscript.py:486-487` carries that history in the code.

**Scope, tightly.** This covers the proposal's premise that the erdosmiller `Stop Condition` input is *the* route (a premise that dates from `archive/bench-2026-09-14-stage2-toolkit/build_opexitwhile.py:4-5`, "the loop node's `Terminals[]` is empty … **so the library's Stop Condition is the route**" — written **before** `Loop End Ref` was verified on this machine, three days later). It does **not** claim any op already writes a conditional terminal — none does, and `docs/toolkit-capabilities.md:50` is right that `OpLoopEndRef_v0` only reads. It does **not** decide which route is cheaper: the erdosmiller route is proven end-to-end, the direct route has an unmeasured step (`Connect Wire` onto a conditional-terminal sink). It says the alternative is **built, measured and unpriced in the plan**, and that the last comparable choice went the other way.

## B2 `helper-exists` — the op already holds the loop body's diagram reference, and `Diagram → Nodes[] → Terminals[]` is already built; the `OpWhileCast_v0` + `Loop.Diagram` hop is a third addressing space for something the op has in hand

- `OpExitWhile_v0` already takes the body diagram by Traverse index and casts it: `archive/bench-2026-09-14-stage2-toolkit/build_opexitwhile.py:8` — "`Diagram in` ← TMSC 788 (**`Class Name 2` / `index 2` = the loop body**)"; the wrapper sets it at `tools/gscript.py:913` (`"Class Name 2", "Diagram"`; `"index 2", diagram_index`). `Exit While Loop.vi`'s `Diagram in` is terminal 0 and required (`docs/NAMES.md:751-752`), so that reference **cannot be removed** — the new front half would run beside it.
- The node/terminal walk from a **Diagram** reference is already an op: `docs/toolkit-capabilities.md:23` — `OpNodeTerms_v0` / `node_terms(target, diagram, node)`, "every terminal of ONE node … and the node's own UID", `test_opnodeterms.log` all PASS; and `tools/gscript.py:2202-2208` / `tools/recipes/build_opconnect2.py:2` — `OpConnect_v0`/`OpConnect2` address `Nodes[node].Terminals[term]` "**on any diagram of the target (top level or a loop's), by indices**".
- Branching an existing reference into a new chain is this op's own idiom: `archive/bench-2026-09-14-stage2-toolkit/build_opexitwhile.py:119` (`branch=True` off `Open VI Reference.'vi reference'`).
- The proposal's own input list (`vi path`, `index`, `node index`, `term index`) has **no diagram input**, while the node it keeps requires one — so the WhileLoop-typed seed is not replacing `Class Name 2`/`index 2`, it is a second path to the same diagram. Note also `docs/NAMES.md:241-244`: the `Loop` class ids, `Diagram` 6361401 included, are catalogued as "**not yet verified on this machine**" (the chain *is* exercised inside `OpWireSR_*`, `docs/toolkit-capabilities.md:42` — so this is a redundancy point, not an impossibility one).

**Scope:** covers importing an `OpWhileCast_v0` seed and a `Loop.Diagram` hop into this op, and the proposal's stated input list. It does **not** cover the body-node `Nodes[]→Terminals[]` addressing itself, which the proposal is right to reuse.

## B3 `already-measured` — the acceptance instrument and the three target terminals are already measured, and the gate is already written

The proposal's verification is "ExecState 0 → 1, the VI runs and stops". The stronger, already-built readback is in the same plan:

- `docs/d1-build-plan.md:572` — gate **S4**: "each of the three NEW loops' conditional terminals is **written and driven by its own sentinel test**, **read back by `OpLoopEndRef_v0`**: a non-zero `CondWireUID` on each of 1.2 / 1.5 / 1.7", plus `#637` unchanged at "terminal **648 ← wire 3457 ← `#11639`**".
- The three terminals are **already identified**: `tools/bench/build_d1_v0_run4.log:243-245` — "term **1183** … wire 0", "term **1204** … wire 0", "term **1225** … wire 0" for 1.2 / 1.5 / 1.7. So the new op's functional test has a named before/after oracle without discovering anything.
- And the gate's known trap is already corrected: `docs/d1-build-plan.md:621` (§11e.4) — "an unwired conditional terminal **legitimately reports 1055** on its wire read; the gate compares the terminal uid and `wire == 0`, **not an empty error column**" (this is what made run 4's S4b×3 report FAIL while succeeding as a measurement).

**Scope:** covers the op's acceptance criterion — the readback exists, is 16/0 (`tools/bench/build_oploopendref_v0.log`), and its gate wording is settled. It does **not** claim the op's own behaviour has been measured, and it does not replace A4's per-iteration requirement (a non-zero `CondWireUID` proves the wire, not the dynamics).

---

## Checked and cleared — so the next round does not re-derive it

1. **No `OpExitWhileNode`-equivalent exists under any name.** Project-wide greps for `OpExitWhile*`, `Stop Condition`, `conditional terminal`, `ExitWhileNode` return: the built op + its wrapper (`tools/gscript.py:889`), the reader (`OpLoopEndRef_v0`), the creators, and prose. `archive/benchmarks/INDEX.md` row 33 is the by-name op only. **The artifact is genuinely unbuilt.**
2. **`OpExitWhile_v0`'s recorded failure is addressed by inheritance, not repeated.** Run 1 died on name-keyed terminals collapsing the duplicate `Outputs`/`Shift Registers` pairs and on wire `0` matching as a connection (`archive/peer/2026-09-14-opexitwhile-fail1-duplicate-terminal-names.md:24-29`); the fix is inside the saved op (`archive/bench-2026-09-14-stage2-toolkit/build_opexitwhile.py:90-94`). Copying the fixed op inherits it. **No `already-failed` slug.**
3. **The sentinel encoding, the literals route and the Case are not reopened** — `docs/d1-build-plan.md:540-554`, and rev4c's B2/B3 (`gscript.py:2616`, `opconstvaluen_scan.json`) already disposed of them.
4. **One recorded design rule the new op's property/invoke chain is subject to, not a finding:** `docs/toolkit-capabilities.md:50,:53-55` — one property per node with its own error chain, census the data terminal, "never gated on 'no error 1077'"; `tools/recipes/build_oploopendref_v0.py:60` records `OpCaseFrames_v0`'s five failures in exactly the shape that skips it.

---

```
PRIOR-ART: contradicted     (A3 — docs/d1-build-plan.md:636 + tools/recipes/build_oploopendref_v0.py:26-27 + docs/toolkit-capabilities.md:50 + docs/d1-build-plan.md:176,:443-446 vs the proposal's "additive, nothing deleted" / "delete the Get Controls + Index Array front half" — covers the word "additive", the authorisation resting on it, and the missing bared-terminal gate; does NOT say front-half deletion is unsafe, cf. toolkit-capabilities.md:49)
PRIOR-ART: unread-evidence  (A4 — docs/stage2-plan.md:90-94 + tools/bench/test_opexitwhile.py:8,:50,:56 + archive/peer/2026-09-14-opexitwhile-fail1-duplicate-terminal-names.md:37,:47 vs the proposal's citation of docs/toolkit-capabilities.md:31 and its "the VI runs and stops" test — covers the evidence base and the acceptance test's shape, not OpExitWhile_v0's 5/5)
PRIOR-ART: helper-exists    (B1 — docs/NAMES.md:246-249 + tools/gscript.py:529 + tools/recipes/build_opwiresr_v0.py:4 + tools/recipes/build_opconnect2.py:5-6 + archive/peer/2026-09-14-stage2-shiftreg-primitive.md:13-19,:85,:126-129 vs archive/bench-2026-09-14-stage2-toolkit/build_opexitwhile.py:4-5 — covers the premise that the erdosmiller Stop Condition is THE route and the unpriced direct route; does NOT claim any op writes a conditional terminal today, and takes no position on which route is cheaper)
PRIOR-ART: helper-exists    (B2 — archive/bench-2026-09-14-stage2-toolkit/build_opexitwhile.py:8,:119 + tools/gscript.py:913 + docs/toolkit-capabilities.md:23 + tools/gscript.py:2202-2208 + tools/recipes/build_opconnect2.py:2 vs the proposal's OpWhileCast_v0 -> Loop.Diagram chain and its four-input list — covers importing a seed and a Loop.Diagram hop for a diagram the op already holds; does NOT cover the body-node Nodes[]->Terminals[] addressing itself)
PRIOR-ART: already-measured (B3 — docs/d1-build-plan.md:572,:621 + tools/bench/build_d1_v0_run4.log:243-245 + tools/bench/build_oploopendref_v0.log — covers the op's acceptance instrument and the three target terminal uids; does NOT claim the new op's behaviour has been measured, and does not discharge A4)
```

**The two that change what happens next.** **A3** — the build is authorised as *additive*; make it additive by deleting only the one wire into `Stop Condition` (`build_opexitwhile.py:136`), or drop the word and carry a bared-terminal census the way `OpOwnerChain_v1` carried 20 gates. **B1** — before writing the recipe, price the direct route: `WhileLoop.Loop End Ref` 6362C00 already hands back a `Terminal` (`docs/NAMES.md:247-248`) and `Terminal.Connect Wire` on a sink is built four times over; the last time this project chose between a library-VI side effect and a direct typed-reference method, the review refused the library VI and the direct method is what shipped.

Two mechanics notes for the dispatching session: this review exists only in this reply — it needs archiving under `archive/peer/` to be gate-visible; and `ExitPlanMode` is not in this session's tool set (nothing to implement in any case — the brief is read-only).

## Sources

(extract from answer)

## What was done with it (material session, 2026-09-17 07:5x — cycle 15, D1 phase full)

**All five findings ACCEPTED. 0 novel. No citation refuted. The review CHANGED THE DESIGN before a line of the
op was built**, which is what it exists for: the proposal was a front-half swap on `OpExitWhile_v0`, and what is
being built instead is `OpStopFromNode_v0.vi`, an **additive** build on `OpLoopEndRef_v0.vi`.

| # | verdict | disposition |
|---|---|---|
| **A1** | cleared | Noted, no action. The direction (a body-node stop) is not settled elsewhere. |
| **A2** | no refutation | Noted, no action, with the route precedent folded into B1's disposition. |
| **A3** | `contradicted` | **ACCEPTED — the design was replaced rather than re-worded.** The proposal called itself "additive, nothing deleted" while deleting `Get Controls.vi` and a wire, and §11e.2's authorisation was granted for an *additive* build. The new route deletes **nothing**: `tools/recipes/build_opstopfromnode_v0.py` gate **W8b** asserts that no class lost a member (`all(c1[k] >= c0[k])`) across the whole build, so "additive" is now machine-checked rather than claimed. |
| **A4** | `unread-evidence` | **ACCEPTED — the acceptance test's shape was rewritten.** The "the VI runs and stops" line is not reused: the recipe states its level of verification explicitly (STRUCTURAL + WIRE-IDENTITY + a TYPE discriminator, **not** a run) and says why a run is not attempted — `Is Path and Not Empty.vi` with an unwired `path` returns FALSE, so the scratch loop would spin, and `create_control` reaches TOP-LEVEL nodes only (`tools/gscript.py:2155`), so no control can be attached to a terminal inside a loop body. Execution behaviour is deferred to D1's F2 gate (all loops exit). The duplicate-terminal-name trap (`archive/peer/2026-09-14-opexitwhile-fail1-duplicate-terminal-names.md`) is honoured: every terminal is keyed by `(name, is_source)`, never by name alone. |
| **B1** | `helper-exists` | **ACCEPTED — this is the finding that replaced the route.** `WhileLoop.Loop End Ref` 6362C00 hands back a `Terminal` (`docs/NAMES.md:246-249`, verified on the machine by `OpLoopEndRef_v0`, 16/0) and `Terminal.Connect Wire` 6349C03 on a sink is built four times over (`tools/recipes/build_opwiresr_v0.py:4`). The erdosmiller `Exit While Loop.vi` is dropped from the new op entirely. `OpExitWhile_v0` is **not** replaced — it stays the right op for a panel-control stop. |
| **B2** | `helper-exists` | **ACCEPTED.** The body-node addressing is not invented: the chain `TMSC --branch--> PN Loop[Diagram 6361401] -> PN AbstractDiagram[Nodes[] 6375809] -> IndexArray -> PN Node[Terms[] 6359000] -> IndexArray` is lifted verbatim from `build_opwiresr_v0.py:228-249`, and it branches off the **same** typed reference the donor already holds (`#683 specific class reference`), so no seed is imported and no second addressing space is created. |
| **B3** | `already-measured` | **ACCEPTED.** The acceptance instrument is `OpLoopEndRef_v0` itself (16/0), and the three D1 target terminals are already measured — **1183 / 1204 / 1225**, all wire 0 (`tools/bench/build_d1_v0_run4.log:243-245`). The same run's S4b gate has been re-specified this session per plan §11e.4 (compare terminal uid and `wire == 0`; an unwired terminal's 1055 is expected and is reported, never gated). |

**The two that changed what happens next**, both taken: the direct route (B1) and literal additivity (A3).
**What was run under this disposition:** the read-only census `tools/bench/diag_loopendref_front.log` (the donor's
internals: `#683` typed reference, `#657` data terminal `LpEndRef`, the three read property nodes) and then
`tools/recipes/build_opstopfromnode_v0.py`. `tools/recipes/build_opexitwhilenode_v0.py`, written from the
proposal before this review returned, was **deleted unrun**.
