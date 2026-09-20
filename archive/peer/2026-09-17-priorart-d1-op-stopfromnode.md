# priorart-d1-op-stopfromnode

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.3335  in 42 / out 36391 / cache-create 180428 / cache-read 3191691  (494s, 36 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (498s)
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
NEW OP, REVISED AFTER ITS OWN FIRST PRIOR-ART REVIEW: `OpStopFromNode_v0.vi` ??wire a While loop's
CONDITIONAL TERMINAL from a terminal of a node INSIDE ITS OWN BODY, by the DIRECT typed-reference route.
Recipe: tools/recipes/build_opstopfromnode_v0.py

WHY: docs/d1-build-plan.md 짠11c/짠9a stops D1's three new loops (1.2 / 1.5 / 1.7) on END-OF-STREAM SENTINELS ??
each loop's stop is a Boolean produced inside its own body, never a panel read (짠4's read-once rule).
짠11e.2 (judgement session, 2026-09-17) lifted the cycle-15 op freeze NARROWLY for this one op.

WHAT CHANGED SINCE THE FIRST REVIEW, AND WHY ??attack this, it is the load-bearing part.
The first dispatch (archive/peer/2026-09-17-priorart-d1-op-exitwhile-node.md, slug d1-op-exitwhile-node,
5 findings, 0 novel) proposed a FRONT-HALF SWAP on `OpExitWhile_v0` (delete `Get Controls.vi`, feed the stop
`Index Array` from a third `Get Outputs.vi`). Two of its verdicts changed the design and I accepted both:
 - B1 `helper-exists`: the erdosmiller `Exit While Loop.vi` `Stop Condition` is not the only route.
   `WhileLoop.Loop End Ref` 6362C00 already hands back a `Terminal` (docs/NAMES.md:246-249, VERIFIED on the
   machine by `OpLoopEndRef_v0`, 16/0), and `Terminal.Connect Wire` 6349C03 on a sink is built four times over
   (tools/recipes/build_opwiresr_v0.py:4). The review's own line: the last time this project chose between a
   library-VI side effect and a direct typed-reference method, the review refused the library VI.
 - A3 `contradicted`: the build was authorised as *additive* while the proposal deleted a subVI and a wire.
So the DONOR IS NOW `OpLoopEndRef_v0.vi`, and the build is additive in the literal sense: nothing is deleted.

THE MEASURED DONOR (tools/bench/diag_loopendref_front.log, read-only, 2026-09-17):
  `To More Specific Class` #683 `specific class reference` (w366) = the WhileLoop-typed reference
    -> Property #657, data terminal `LpEndRef` (w775) = THE CONDITIONAL TERMINAL
    -> #738 `UID`, #743 `IsSource`, #745 `Wire`  (the existing read path, left untouched)

WHAT IS ADDED (every piece copied from tools/recipes/build_opwiresr_v0.py, which built this exact chain
four times):
  #683 `specific class reference` --branch--> PN Loop[`Diagram` 6361401] -> PN AbstractDiagram[`Nodes[]`
  6375809] -> IndexArray(`index node`) -> PN Node[`Terms[]` 6359000] -> IndexArray(`index term`)
  Invoke Terminal[`Connect Wire` 6349C03]: `reference` <- #657 `LpEndRef` (BRANCH, so the read path keeps its
  wire); `Wire Source` <- IndexArray(term) `element`.
  Two new controls (`index`/`index 2`-style, labels read back from the machine, never assumed) and one error
  indicator. `OpExitWhile_v0` is NOT replaced ??it remains the right op for a panel-control stop.

ACCEPTANCE, and the level of verification I claim (I do NOT claim a run):
  W-gates: counts only ever increase (gated), every wire verified by the SAME wire uid on BOTH ends,
  ExecState 1 before the save; nothing saved if not.
  T-gates on a scratch (EMPTY_v0 copy + While loop + `Is Path and Not Empty.vi` in the body, created and
  deleted in the same run): the conditional terminal's wire goes 0 -> non-zero on the SAME terminal uid;
  that wire uid equals the wire on the body node's Boolean output; ExecState 1.
  T6 DISCRIMINATOR: the same node's `error out` CLUSTER onto a SECOND loop's conditional terminal must DROP
  ExecState to 0 ??a no-op would leave it at 1.
  I do NOT run the scratch: `Is Path and Not Empty.vi` with an unwired `path` returns FALSE, so the loop would
  spin forever, and `create_control` reaches TOP-LEVEL nodes only (tools/gscript.py:2155), so no control can be
  attached to a terminal inside a loop body. Execution behaviour is deferred to D1's F2 gate.

ASK: has THIS route ??Loop End Ref + Terminal.Connect Wire to write a conditional terminal ??already been
built, attempted, failed, or measured here under any name? Does an existing op or gscript helper already write
a conditional terminal from a node terminal? Is `Loop.Diagram` 6361401 recorded as verified or as a failure?
Does any archived exchange or superseded plan refute branching `LpEndRef` into a Connect Wire `reference`?
Is the T6 discriminator already recorded as invalid (e.g. a cluster onto a Boolean sink being accepted)?


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
  status: acquired
  owner: material/cycle15-d1-phase-full
  since: 2026-09-17 07:4x
  purpose: D1 PHASE "full" - the two narrowly-unfrozen ops (stop front-half swap, streaming-write donor)
           then the full build. Scratch copies under claudeDev only; original md5 asserted before AND after.
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

Prior-art review complete — read-only: no lock, no build, no edit, no `.vi` opened, no hardware. (Write/ExitPlanMode are not in this session's tool set; the review is this reply.)

**5 findings, 0 `novel`.** The artifact is genuinely unbuilt and the direct route is not refuted anywhere. But two cited facts are stale in our own files, two construction helpers already exist with safeguards the copy drops, and the T6 discriminator measures something measured twice — with a type LabVIEW accepts.

---

# PART A — THE DIRECTION

## A1 — cleared (so the next round does not re-litigate it)

The direction is settled **in favour** and the op is already on the schedule: `docs/d1-build-plan.md:655-657` (§11e.2) lifts the freeze narrowly for D1's stop op; `STATUS.md:104-110` (OPEN 29) records the design replacement to `OpStopFromNode_v0.vi` on the `OpLoopEndRef_v0` donor; `STATUS.md:128-130` schedules "finish `OpStopFromNode_v0`" as the next material step. Both halves of the route are individually verified — `docs/NAMES.md:246-249` (`Loop End Ref` 6362C00 → a `Terminal`, ✅ 2026-09-17) and `tools/recipes/build_opwiresr_v0.py:4` (Connect Wire on the sink).

## A2 — no refutation found

Nothing in `archive/peer/`, the retrospectives or a superseded plan section argues against writing a conditional terminal with `Terminal.Connect Wire`, and **nothing refutes branching `LpEndRef` into the invoke's `reference`**. The recorded semantics *permit* it: `docs/NAMES.md:231-232` — "A wired source is branched; a wired **sink** is re-routed (breaks the VI) — wire unwired sinks only." Both W7 branches are source-side on the op's own diagram, and the target sink is measured **unwired** (`tools/bench/build_d1_v0_run4.log:243-245`: terms 1183 / 1204 / 1225, wire 0). A non-node-terminal sink is already proven working: `OpWireSR_RightIn_v0`'s Connect Wire sink is a shift-register *inside* terminal (`tools/recipes/build_opwiresr_v0.py:259`), `tools/bench/test_opwiresr.log:38` T4 PASS.

## A3-i `contradicted` — the sentence that authorises this build names a different op, and that sentence is the live subject of STATUS's open question 2

> **The recipe** (`tools/recipes/build_opstopfromnode_v0.py:8-9`): "§11e.2 lifted the cycle-15 op freeze narrowly for this one op."

- `docs/d1-build-plan.md:655-657` (§11e.2): "only ops this plan names as D1 parts — **the stop front-half swap on `OpExitWhile_v0`** (rev4c B1) and a streaming-write donor for §7.1". Repeated verbatim at `:703-705` (§11d item 8).
- The freeze itself: `docs/cycle15-plan.md:104` — "No new general-purpose op VIs …".
- The wording is not dormant: `STATUS.md:125-126` makes "**Does the narrow unfreeze (§11e.2) cover …**" one of the three open judgement questions. A sentence whose scope is currently being adjudicated cannot also be quoted as covering an op it does not name.

**Scope, tightly.** This covers the *authorising sentence*, not the substance — `STATUS.md:104-110` and `:128` record and schedule this exact op, so the intent is plainly there. Repair is one sentence in §11e.2 naming `OpStopFromNode_v0` and its `OpLoopEndRef_v0` donor. It does **not** say the op is unauthorised and does not touch §11c/§9a's sentinel direction.

*(Mechanics, not a finding: the STATUS.md pasted into this brief is one revision behind disk — the disk copy already carries 27b-corrected, 27c, 29, 30. Re-read STATUS from disk before quoting it.)*

## A3-ii `contradicted` — `Loop.Diagram` 6361401 is UNVERIFIED in the names file and MEASURED-PASS in the log; "built this exact chain four times" is twice

Direct answer to the ask: **verified on the machine, never a failure — but the document still says otherwise.**

- `docs/NAMES.md:241-242`: "Loop / ForLoop property IDs (LabVIEW Wiki, 2026-09-14; **not yet verified on this machine** — no Loop-typed ref yet): `Loop` class 16405: … **`Diagram` 6361401** …"
- `tools/bench/build_opwiresr_v0.log:25-29` and `:69-73` — gate **B0** "PN_D Loop[Diagram] 6361401 (UNVERIFIED property - the gate)" → "PN_D data terminal: **'Diagram'**" → "'specific class reference' -> 'reference': wire 366 / 366 OK", with `tools/recipes/build_opwiresr_v0.py:234-235` stopping the build if ExecState ≠ 1. It did not stop. `docs/toolkit-capabilities.md:42` ships the chain in four ops.
- Same paragraph, half-updated: `docs/NAMES.md:246-249` marks `WhileLoop.Loop End Ref` "✅ VERIFIED ON THE MACHINE 2026-09-17".

And the count: the **Loop[Diagram] → Nodes[] → Terms[]** chain is built **twice** — `tools/recipes/build_opwiresr_v0.py:227-236` gates it on `variant in ("LeftIn", "RightIn")`; `LeftOutNode` uses `VI.Block Diagram` (`:238-239`), `LeftOutCtl` uses `Panel.Controls[]` (`:241-245`). What is built four times is the Connect Wire invoke (`:255-263`).

**Scope:** the stale verification line and the count. **Not** the chain's validity — that is proven, twice, by log.

## A4 — no unread governing document

`docs/stage2-plan.md:90-94` (read-once rule) is honoured by the sentinel design; `docs/NAMES.md:264-266` independently records the `create_control` top-level-only limit the recipe cites to `tools/gscript.py:2155`; the duplicate-terminal-name trap is honoured by keying on `(name, is_source)` (`build_opstopfromnode_v0.py:114-118`).

---

# PART B — THE ARTIFACT

## B1 — cleared: the op does not exist and nothing else can do it

- The only writer of a conditional terminal is `OpExitWhile_v0`, **by panel-control name** — `docs/toolkit-capabilities.md:31`.
- `connect_terminals` / `connect2` cannot reach it: both address `Nodes[n].Terminals[t]` (`tools/gscript.py:2202-2208`, `:2428`), and the conditional terminal is in **no** node's `Terminals[]` — `tools/recipes/build_oploopendref_v0.py:33-35`.
- No such op on disk (claudeDev `Op*Wire*` listing; the only bench file for this slug is this review's own dispatch log). **No `already-built`, no `already-failed`** — the OpExitWhile variant was deleted unrun (`STATUS.md:107-109`).

## B2 `helper-exists` — `loop_end_ref()` already exists, and the copy drops exactly the safeguards its docstring exists to carry

- `tools/recipes/build_d1_v0.py:710-743` — `loop_end_ref(target, loop_index)`, docstring: "…**every output is POISONED before the run**, and **the four per-property error columns are read**, because 'no error out' is not a verdict that a property resolved (`toolkit-capabilities.md:234-238`)."
- The copy at `tools/recipes/build_opstopfromnode_v0.py:289-307` poisons only `CondTermUID`/`CondWireUID`/`LoopUID` — **not `IsSource`** — and reads **none** of `LoopEndRefErr`/`IsSourceErr`/`ConnWireErr`/`WireUIDErr`. Gates **T3, T3b, T4** (`:367-375`) are scored entirely on that unguarded read: a property that silently failed to resolve returns a defaulted `0`, read as "not wired yet".

**Scope:** the driver function only. Import it (`from build_d1_v0 import loop_end_ref`) or copy it whole.

## B3 `helper-exists` — the censusing property-node and indicator helpers exist, were imported by *this very donor* on a prior-art disposition, and are hand-rolled here without their assertions

- `tools/recipes/build_opcaseframes_v0.py:48-59` `prop_node()` creates the node **and censuses its single data SOURCE terminal**; `:62-71` `add_indicator()` asserts one new panel object, that it **is** an indicator, and that its label is **unique**.
- The donor recipe imports both and says why: `tools/recipes/build_oploopendref_v0.py:39-41` ("IMPORTED and called, not re-written" — prior-art B3-ii), `:122`, `:240-246`; the rule at `:69-75` (L3): "each … is CREATED **and its DATA TERMINAL is censused** … 'No error 1077' is explicitly NOT the verdict."
- The measurement behind it: `docs/toolkit-capabilities.md:234-238` — a **valid id on the wrong class** creates a property node with **no data terminal and no error at all**.
- The new recipe: `pn()` (`build_opstopfromnode_v0.py:158-160`) returns a uid with no census, gate **W2** (`:218`) asserts only `bool(d)`, data terminals come from the **index-4 convention** (`:137-139`), and the indicator block (`:245-255`) takes `new[0]` with no uniqueness assertion. It matters *here specifically*: W2 puts `Diagram` **6361401 on class `VI Server:Loop`** while the wire arrives from a **WhileLoop**-typed reference — the exact "is this property on this class?" question the census rule was written for. A miss surfaces as `StopIteration` inside `connect()`, not as a gate.

**Scope:** `pn()`, `data_name()`, the indicator block. Not `walk`/`term`/`connect`/`idx` (normal per-recipe duplication).

## B4 `already-measured` — T6 measures semantics already measured twice, and the type it picks is one LabVIEW accepts on a conditional terminal

The question T6 asks — "does a type-mismatched Connect Wire sink break the VI, so the op is not a no-op?" — is written down:

- `tools/gscript.py:2206-2207` (OpConnect_v0, 2026-09-06): "…**Type mismatches make a broken wire.**"
- `tools/recipes/build_opwiresr_v0.py:32-33` predicted it and `tools/bench/test_opwiresr.log:51-53` measured it: a **String** control terminal onto an image-typed register terminal → "left outside wire 192, ExecState 0", **T7 PASS / T8 PASS**.

**And the chosen mismatch is not a mismatch.** `build_opstopfromnode_v0.py:54-55, 380-418` wires the node's `error out` **cluster** onto a second loop's conditional terminal and requires ExecState 1 → 0. LabVIEW accepts an error cluster there — only the `status` field passes, and the shortcut items become *Stop if Error / Continue While Error* ([LabVIEW Wiki, While loop](https://labviewwiki.org/wiki/While_loop), the same wiki this project took 6362C00 from, `docs/NAMES.md:241`). Predicted outcome **1 → 1**, T6 FAILs, and a working op is blocked by its own gate — the class this cycle has already paid for (`STATUS.md:92-95`, 27b "THE FIVE FAILS ARE MY GATES, NOT THE MACHINE").

Either repair suffices: (a) pick a source that is genuinely neither Boolean nor error cluster — the T2 census at `:339-341` already lists the node's outputs; or (b) make it **positive**: `OpWireSource_v5` (12/12, `docs/toolkit-capabilities.md:48`) resolves the new wire's source terminal, so assert it is the body node's Boolean output. (b) also proves direction, which T4's uid equality does not.

One more measured fact assumed the other way: `:384-385` says "Remove Bad Wires then restores it, so the scratch is left clean". The only measurement says otherwise — `tools/bench/test_opwiresr.log:54`, **T8b FAIL, `gone=set()` expected `{192}`**, and `:56` "after Remove Bad Wires: ExecState 0". Harmless (the scratch is deleted at `:433`), but the comment should not outlive the measurement.

**Scope:** T6's novelty, its mismatching type, and that comment. **Not** T3/T3b/T4/T5, and no claim that the op writes nothing.

---

```
PRIOR-ART: contradicted     (A3-i  — docs/d1-build-plan.md:655-657,:703-705 + docs/cycle15-plan.md:104 + STATUS.md:125-126 vs tools/recipes/build_opstopfromnode_v0.py:8-9 — covers the authorising SENTENCE naming OpExitWhile_v0, not the op's substance, which STATUS.md:104-110,:128 already records and schedules)
PRIOR-ART: contradicted     (A3-ii — docs/NAMES.md:241-242 vs tools/bench/build_opwiresr_v0.log:25-29,:69-73 + tools/recipes/build_opwiresr_v0.py:234-235 + docs/toolkit-capabilities.md:42; and "four times" vs build_opwiresr_v0.py:227-245 where the chain is built TWICE — covers the stale verification line and the count, NOT the chain's validity, which is proven by log)
PRIOR-ART: helper-exists    (B2    — tools/recipes/build_d1_v0.py:710-743 vs tools/recipes/build_opstopfromnode_v0.py:289-307 — covers the loop_end_ref driver: the copy omits the IsSource poison and all four per-property error columns that T3/T3b/T4 depend on; does NOT question the op design)
PRIOR-ART: helper-exists    (B3    — tools/recipes/build_opcaseframes_v0.py:48-71 + tools/recipes/build_oploopendref_v0.py:39-41,:69-75,:122,:240-246 + docs/toolkit-capabilities.md:234-238 vs build_opstopfromnode_v0.py:137-139,:158-160,:218,:245-255 — covers pn()/data_name()/the indicator block; does NOT cover walk/term/connect/idx)
PRIOR-ART: already-measured (B4    — tools/gscript.py:2206-2207 + tools/recipes/build_opwiresr_v0.py:32-33 + tools/bench/test_opwiresr.log:51-54,:56 + labviewwiki While loop vs build_opstopfromnode_v0.py:54-55,:380-418,:384-385 — covers T6's novelty, its choice of the error cluster as the mismatch, and the Remove-Bad-Wires comment; does NOT cover T3/T3b/T4/T5)
```

**The two that change what happens next.** **B4** — T6 will almost certainly read 1 → 1 and fail a working op; switch to a real mismatch or to the positive `OpWireSource_v5` check before the run. **B2** — import `build_d1_v0.loop_end_ref`, or T3/T4 are scored on reads nobody checked.

**Checked and cleared:** the op is genuinely unbuilt; no archived exchange refutes the direct route or the `LpEndRef` branch; a non-node-terminal Connect Wire sink is already measured working (`test_opwiresr.log:38`); the three target conditional terminals are measured unwired (`build_d1_v0_run4.log:243-245`); the "no run" justification is independently recorded at `docs/NAMES.md:264-266`.

Sources: [LabVIEW Wiki — While loop](https://labviewwiki.org/wiki/While_loop)

## Sources

(extract from answer)

## What was done with it (material session, 2026-09-17 08:0x — cycle 15, D1 phase full)

**All five findings ACCEPTED. 0 novel. No citation refuted.** Four repairs landed in
`tools/recipes/build_opstopfromnode_v0.py` **before it was run**; the fifth is escalated because it is an
authorisation, not code. A1/A2/B1 cleared the route itself ("the op is genuinely unbuilt; no archived exchange
refutes the direct route or the `LpEndRef` branch"), which is what made the build worth finishing.

| # | verdict | disposition |
|---|---|---|
| **A3-i** | `contradicted` | **ACCEPTED, ESCALATED — not patched.** §11e.2's authorising sentence names *"the stop front-half swap on `OpExitWhile_v0`"*, and this op is not that: same duty, same narrow scope, different donor — chosen **because this review's own predecessor (B1) told me to**. A material session does not re-word an authorisation, so it is flagged in `STATUS.md` and in the recipe header, and the substance is left for judgement to ratify. |
| **A3-ii** | `contradicted` | **ACCEPTED — both counts corrected in the header.** The body-node chain is built **twice**, not four times (`build_opwiresr_v0.py:227-245`). And `Loop.Diagram` **6361401** is *"listed from the Wiki, UNVERIFIED"* in `docs/NAMES.md:241-242` while `tools/bench/build_opwiresr_v0.log:25-29,:69-73` records it as **measured PASS** — so it is verified **by log, not by the names file**, and the header now says so. (The stale line in `NAMES.md` is a doc defect this session did not own; recorded here so the next reader does not re-derive it.) |
| **B2** | `helper-exists` | **ACCEPTED — the driver is now IMPORTED**: `from build_d1_v0 import loop_end_ref`. The hand-rolled copy poisoned only three outputs (not `IsSource`) and read **none** of the four per-property error columns — and T3/T3b/T4 are scored on exactly that read, so a silently unresolved property would have read as "not wired yet". |
| **B3** | `helper-exists` | **ACCEPTED — the assertions were taken verbatim.** `build_opcaseframes_v0.prop_node()`/`add_indicator()` bind their target through a module-global `OP` and are not importable here, so their *assertions* are: `pn()` now censuses the node it creates, `data_name()` **asserts exactly one data SOURCE terminal** instead of using the index-4 convention, and the indicator block asserts one new, uniquely-labelled INDICATOR. This matters precisely where the review said it does — `Diagram` 6361401 is put on class `VI Server:Loop` while the reference arrives from a `WhileLoop`, and `toolkit-capabilities.md:234-238` measured that a valid id on the wrong class yields a node with **no data terminal and no error at all**. That now raises at W2 instead of surfacing as a `StopIteration` inside `connect()`. |
| **B4** | `already-measured` | **ACCEPTED — the gate was replaced, not softened.** The first T6 wired the node's `error out` **cluster** onto a second loop's conditional terminal and demanded ExecState 1 → 0. LabVIEW **accepts** an error cluster there (Stop if Error / Continue While Error), so the prediction was 1 → 1: a working op failed by its own gate, the same class as this cycle's five gate-spec failures (STATUS 27b). Repair **(b)** is used, which is stronger than the original: `OpWireSource_v5` (12/12) resolves the new wire's own source terminal, and T6 now asserts **exactly one source, owned by the body node** — proving DIRECTION, which T4's uid equality does not. The "Remove Bad Wires restores it" comment is gone with the gate that needed it (`test_opwiresr.log:54,:56` measured the opposite). |

**What was run under this disposition:** `tools/recipes/build_opstopfromnode_v0.py` (build + the T-gates), then
`tools/recipes/build_d1_v0.py` PHASE "relocate" with the five re-specified gates and the 23-object move table.

FIXED: contradicted - tools/recipes/build_opstopfromnode_v0.py:30 - the header now says the body-node chain is built TWICE (not four times) and that `Loop.Diagram` 6361401 is verified by `build_opwiresr_v0.log:25-29,:69-73`, NOT by `docs/NAMES.md:241-242`, which still calls it UNVERIFIED; A3-i's authorisation wording is escalated to judgement at :42 and in STATUS, not patched.
FIXED: helper-exists - tools/recipes/build_opstopfromnode_v0.py:97 - `loop_end_ref` is now IMPORTED from `build_d1_v0` (poisons every output incl. `IsSource`, reads all four per-property error columns) instead of hand-copied, and at :170 `data_name()` asserts exactly ONE data SOURCE terminal in place of the index-4 convention, with the indicator block asserting one new uniquely-labelled INDICATOR.
FIXED: already-measured - tools/recipes/build_opstopfromnode_v0.py:469 - T6 no longer wires an `error out` CLUSTER as a "mismatch" (LabVIEW accepts an error cluster on a conditional terminal, so it would have read 1 -> 1 and failed a working op); it is now the POSITIVE `OpWireSource_v5` check asserting exactly one source terminal owned by the body node, which also proves direction.
