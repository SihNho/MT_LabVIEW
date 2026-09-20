# priorart-d1-full-route-rev2

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $7.0852  in 86 / out 50227 / cache-create 220434 / cache-read 7249532  (662s, 55 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (666s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PRIOR-ART REVIEW (trigger: direction-change).

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
# Plan under review ??`tools/recipes/diag_d1_full_route.py` REV 2 (cycle 15, D1 PHASE "full")

## This is a REVISION. Its first prior-art review already landed and is fully disposed

`archive/peer/2026-09-17-priorart-d1-full-route.md` ??ANSWERED, 6 findings, 0 novel, **all six accepted, none
refuted**; the disposition is written in that file's "What was done with it". Please do **not** re-litigate those
six. What they changed:

* **A3-i** killed my claim that `wire()` is the only nested-diagram writer and is name-addressed ??withdrawn;
  `wire_sr` (`gscript.py:523-528`) and `OpStopFromNode_v0` (`toolkit-capabilities.md:51`) address a **body**
  node's `Terminals[index]` by INDEX.
* **B3** killed my "19 unreachable terminals" ??`build_d1_v0.json` already stores `term_index` and `is_source`.
  The old R2 gate is deleted; the recipe now only *reports* the addressing mode (81 by name / 28 by index).
* **B4** killed the old R3 (an unnamed terminal has been wired by index twice) and T5sep (it re-derives
  `NAMES.md:788`). T6sep survives **as a control only**, which B4's own scope note releases.
* **A1** killed my new join ??the recipe now JOINS the existing `d1_step0_census.json.resolved_boundary` to the
  82-wire cut set and calls `OpWireSource_v5` only for what that does not cover.
* **A3-ii** killed "PHASE 'full' is not executable as written" and pointed at the **recorded** blocker instead.

## What REV 2 actually runs, and the one question I need reviewed

The recorded blocker is `archive/2026-09-17-status-d1-phase-full-narrative.md:141-147` = STATUS OPEN 28: the
end-of-stream sentinel test needs a **comparison primitive and literals INSIDE each new loop body**, and the one
untried route that touches no original and no vi.lib donor is **`copy_by_index` with the D1 working copy as BOTH
donor and target, followed by `move_in`**. `docs/d1-build-plan.md` 짠11f.2 authorises exactly this.

REV 2's P2 tests it on a uniquely named working copy of the original, deleted in the same run:

* **P2a** open the copy's panel and report `ExecState`. `copy_by_index` refuses to save a Target that is not
  ExecState 1 (`gscript.py:1351-1354`), and `d1-build-plan.md` 짠2b records a fresh copy reading **0** headlessly.
  Whether an OPEN panel gives 1 is, as far as I can find, unmeasured ??and it decides whether this route exists.
* **P2b** `copy_by_index(donor=copy, 'DigitalNumericConstant', idx(4609), target=copy, expect_uid=4609)` ??the
  **?? sentinel literal**, the half with no required inputs. Predict: one new GObject, count 180 ??181, and
  **no** new panel object.
* **P2c** one While loop on `Diagram#686` + `move_in` of the copied literal into its body; owner chain
  `uid ??body Diagram ??that WhileLoop`; `ControlTerminal` still 114, `Local` still 8.
* **P2d** the COMPARISON half is **deliberately not attempted**, and the reason is written down before the run:
  a comparison primitive has two REQUIRED inputs; `copy_by_index` will not save a broken Target; and the only
  fleet feeders at top level are `create_control` (adds a PANEL CONTROL, breaking the plan's own "ControlTerminal
  still 114", `d1-build-plan.md` 짠10 S3c/S4s) or another **top-level** node's output ??and a Constant is not a
  `Nodes[]` member (`toolkit-capabilities.md:494`). I treat the way out as a DESIGN call and report it as OPEN.

Because each `copy_by_index` **overwrites its `target` file from `MOVE_DST`** (`gscript.py:1360`), every stage
continues on a fresh filename and the previous one is never opened again (the recorded stale-in-memory-VI class).
`restore_move_fixtures()` runs in the `finally`.

## The questions

1. Has **`copy_by_index` with donor == target** been tried here before ??on the main VI or anything else ??and
   what happened? Is there a recorded reason it cannot work (the Move-example fixture path, the UID guard, the
   ExecState-1-before-save rule)?
2. Has the **ExecState of an open-panel fresh copy of the main VI** already been measured? 짠2b records 0
   headlessly; is the open-panel number written down anywhere?
3. Has a **diagram constant been copied and then `move_in`-ed into a loop body** before ??is P2b/P2c already done
   under another name?
4. Is my P2d stop correct, or does the record already contain a way to make a copied comparison primitive
   runnable **without** creating a panel object (a `finish` hook pattern, a donor that arrives pre-wired,
   `build_case`, `OpConstValue*`, copying a whole Case frame, anything)?
5. Which of REV 2's cited facts are contradicted elsewhere in our own files?


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-17
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.
Narrative relocated **verbatim** (rule 4) to `archive/2026-09-16-status-cycles-11-13-narrative.md` + the four
`archive/2026-09-17-status-*.md` (**`??d1-phase-full-narrative.md`** = this session).
?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this from disk.

## START HERE
1. **`docs/pre-rig-master-plan.md` is THE plan**; settled decisions **`docs/decisions.md`**; cycle plan
   `docs/cycle15-plan.md`; **build plan `docs/d1-build-plan.md` (REV 4 + 짠11c/짠11d/짠11e)** ??짠5 + 짠5a-bis (moves),
   짠10 (S/N1/F1/F2). Recipe: `tools/recipes/build_d1_v0.py`.
2. ?좑툘 A prior-art dispatcher's log MUST be named `priorart_*` / `peer_*` (`tools/logclass.py`) or the guards read
   the reviewer's prose as a build failure ??it blocked this session, the 6th of its recorded class.
3. ??**Scripting EDITS are silently declined until the target's FRONT PANEL has been opened** ??`ensure_loaded()`.
4. ??**A fixed op PATH is served from LabVIEW's memory, not from disk** ??unique working-copy filename per run.

## LabVIEW execution lock

```yaml
labview-lock:
  status: acquired
  owner: material/cycle15-d1-phase-full-2
  since: 2026-09-17
  purpose: diag_d1_full_route.py - the PHASE "full" route measurement (re-wire source map, wire() addressability
    with a control, OpStopFromNode T5/T6 separators). Read-only on the original; one uniquely named working copy,
    created and DELETED in the run.
# 2026-09-17 07:3x-08:2x material/cycle15-d1-phase-full: RELEASED. `build_d1_v0.py` run 5 PHASE "relocate"
# (53/0), `build_opstopfromnode_v0.py` x3, and four read-only censuses. Every scratch/working copy uniquely
# named, created and DELETED in the same run. Original md5 2a78e17c449... before AND after run 5;
# `save trace.vi` md5 9d126b32e6de... before AND after. No original edited, no GUI, no hardware.
# Handles 31,002 -> 33,225 (baseline ~31,500).
# Earlier holders (all RELEASED, all md5-clean, none touched an original; run-4 handles 30,682 -> 38,336 after a
# restart) -> the status archives of 2026-09-16/17.
```
**Never assume an instance exited**: `tasklist | grep -i labview`, kill strays. Fresh instances ??1,500 handles;
unique scratch VI name per run, deleted in the same run.

## HARDWARE ??permission follows the RIG STATE. Current state: **遺꾪빐 / DISASSEMBLED ??everything allowed**

| rig state | motors (PI 쨌 rotor 쨌 magnet) | **ASI piezo** | camera |
|---|---|---|---|
| **遺꾪빐 ??disassembled ??WE ARE HERE** | ??| ??| ??|
| 議곕┰ ??assembled | ??| ??| ??|
| ?ㅽ뿕以???experiment running | ??| ??| ??|

?좑툘 **The ASI carve-out is RETIRED** (rule 1b). **Only the user announces a state change.** Instruments: rotor
counter **0** 쨌 magnet full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz, never write `BinningHorizontal`;
**a session open RESETS ROI *and* exposure** ??the acquisition loop applies `tools/bench/camera_contract.py`.
**No beads while disassembled**; fixture work unaffected.

## Where things stand
**Stage 1 CLOSED** (the seven `docs/main-vi-*`). **Stage 2 IN PROGRESS**: `Track_v6_CPU_core_v0.vi` 69/69 쨌
`??queue_v0.vi` 162/162 ??**say it exactly:** bit-identical for the **first 10,018 frames only**, both **replay**
artefacts (recorded TIFFs, `FOR` loops, no acquisition, no stop). **THE GAP:** 169 ops, 118 recipes, 223 peers ??
**zero runnable experimental VIs**.

## OPEN ??one line each; long forms in `archive/2026-09-17-status-cycle15-narrative.md`
1??, 5, 9??2, 18 ??**all in archive 짠9**: PERIODIC auto-reset ungated 쨌 autofocus CLOSED (25 frames ??3.6 Hz) 쨌
   27 undisposed peer archives 쨌 startup drives instruments 쨌 A2 54/54, A3 112/170 쨌 doc lint 2/4/3 쨌 **TIFF
   1.3 MB/frame, ??22 MB/s measured ??bound it or the disk fills**.
13/14/15b/17b. ??stop measured (`#637` term **648 ??w3457 ??#11639**; `stop (end) 2` separate) 쨌 ?뵶 cycle-15
   prior-art partly disposed 쨌 ?뵶 `bgrun --detach` misses an orphaned grandchild 쨌 ?뵶 v3's R11 scored the *restart*.
16. ?뵶 **GPU whole-fixture divergence OUTSIDE `decisions.md:38` ??JUDGEMENT** (`gpu_n1_deltas.json`): beads 0??
   **0 exceedances over all 10,043**; **only bead 4** ??10 x, 9 y, 1 flip, n_valid 10,029. ??짠4.
19/25/26. ??**PLAN = REV 4 + 짠11c/짠11d/짠11e**; TRANSPORT = **queues only**, sentinels stop 1.2/1.5/1.7,
   `#12589`/`#642` stay on 1.1; **six prior-art reviews disposed, 0 novel**. 19b/19c/24 in plan 짠2/짠5.
20??3. ??CLOSED ??0 slugs awaiting a response; `premature_build` (b) exempts a RE-RUN; handles clear on a restart.

27. ??**D1 RELOCATION MEASURED** ??run 4 (46/5) then **run 5 (53/0)**: S1 **Diagram 170** 쨌 S2 `WhileLoop 3??`,
   `Diagram 170??73`, 1.2=#1133/1170, 1.5=#1134/1194, 1.7=#1135/1215 쨌 S2c the six stayers on `Diagram#639` 쨌
   8 SRs 쨌 ControlTerminal 114 intact. **Re-wire list = `tools/bench/build_d1_v0.json`.**
27b/27c. ??**RUN 5: 53 PASS / 0 FAIL, 43 s** (`build_d1_v0_run5.log`; copy created+deleted in the run, not saved,
   md5 before AND after, handles 31,002??3,225). The five gate specs are fixed (S3b-collateral excludes the
   **deleted** `#5058`, whose 13 cut terminals ARE 짠8's crossings ??the dropped GPU kernel **reused uid 5058**;
   S3d SKIPPED-PHASE; S4b 횞3 per 짠11e.4 ??terms **1183/1204/1225, wire 0**, 1055 reported not gated). **All 23
   moves pass**, incl. 짠11e.3's `#3529`/`#3560`/`#3447` ??`Diagram#1194`??WhileLoop#1134` = **1.5**.
   **Re-wire list is now 109 terminals over 24 uids** (was 106/21); collateral 0, d19 clean, no SR changed.
28. ?뵶 **PHASE "full" STILL NOT WRITTEN. N1 / F1 / F2 NOT RUN ??nothing to report on them.** 짠11e.2's two ops do
   **not** cover the sentinel test: it needs a comparison primitive + literals **inside** each loop body, and
   `copy_*` from vi.lib/NI examples is a **recorded crash**. Untried route touching no original: `copy_by_index`
   with the D1 **working copy as both donor and target** + `move_in`. ??narrative 짠5.
29. ?윞 **`OpStopFromNode_v0.vi` BUILT + SAVED, 20/2** (`build_opstopfromnode_v0_run3.log`); route chosen by its own
   prior-art review (B1: `Loop End Ref` **6362C00** returns a `Terminal`, `Terminal.Connect Wire` **6349C03** is
   built ??erdosmiller not needed; A3: "additive" is gated by W8b). ??**The write is MEASURED**: cond. terminal
   **119, wire 0 ??147**, the SAME uid on the body node's Boolean output, op `error out` empty. ?뵶 **T5** ExecState
   0???? and **T6** `OpWireSource_v5` returned no terminals for w147 ??budget spent, 2 explanations each in
   narrative 짠3b. **Not closed.**
30. ?뵶 **STREAMING TSV (짠7.1) NOT BUILT ??its review stopped it** (8 findings, 0 novel): A3 kills the
   copy-from-NI-example route I had just measured; B1 leaves `drop_subvi` of a **one-call** vi.lib file VI (4/4
   present); B2 withdraws "D1 cannot build this"; A4 finds **no gate** for Abort/disk-full. ??plan 짠11.9.
30b. ??**A5's premise MEASURED** (`diag_savetrace_376.log` 4/0, md5 unchanged): `#376 save trace.vi` has **7 nodes
   and NO file I/O** ??it accumulates and calls `save N xyz traces.vi` **periodically** from a Case. ??plan 짠7.3.
31. ?뵶 **RETROSPECTIVE WINDOWS BROKEN ??`repeated-failure-class` 횞2 today (threshold 3).** `retrospective.py` takes
   the cycle start from the PREVIOUS retrospective's timestamp, so cycles 15 and 16 each reviewed a <1-min window
   with **zero builds**; `--since-hours` does NOT override it (`tools/retrospective.py:282-286`). Fix: make it
   override, or use the oldest unreviewed build log (`guard_cycle.py:427-436`). Also **no `docs/cycle16-plan.md`**
   ??the scope check cannot run. Disposed in `??retrospective-cycle16.md` / `??cycle16b.md`.

## NEXT
?뵶 **JUDGEMENT ??three questions** (all of the relocation is measured and depends on none of them):
1. **Is 짠7.1's TSV still wanted, and on which route?** 짠7.3 shows `#376` does not stream, so the requirement
   survives ??but the copy route is refuted, `drop_subvi` one-call is unmeasured, 짠10 has no Abort/disk-full gate.
2. **Does 짠11e.2's narrow unfreeze cover the sentinel test's comparison primitive and literals inside a loop
   body?** PHASE "full" cannot be written without them. (OPEN 28)
3. Behind them: OPEN 16 the GPU tail (only bead 4); F1 60 s (**??.3 GB**) vs the user's 5 min (**??5 GB**).
?윟 MATERIAL: close `OpStopFromNode_v0`'s T5/T6 (narrative 짠3b names the two separators, one run each) ??
PHASE "full" against `tools/bench/build_d1_v0.json` (**109 terminals**) ??N1 ??F1 ??F2.

## Where to look
`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 `docs/toolkit-capabilities.md` 쨌 **`docs/d1-build-plan.md`
= the build order; relocation DONE, PHASE "full" open** 쨌 `tools/recipes/build_d1_v0.py` 쨌 `docs/gpu-backend.md` 쨌
`docs/pre-rig-master-plan.md` 쨌 the status archives.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Write is disabled here, so the review is delivered as text. No lock taken, nothing built, edited or run.

---

# PRIOR-ART REVIEW — `tools/recipes/diag_d1_full_route.py` REV 2 (cycle 15, D1 PHASE "full")

The six findings of `archive/peer/2026-09-17-priorart-d1-full-route.md` are not re-litigated.

**8 findings, 0 novel.**

---

## PART A — THE DIRECTION

### A1 `already-measured` — P2a's number is in the record TWICE, and the two records disagree

The recipe makes P2a the pivot: *"Which number an OPEN panel gives is unmeasured, and it decides whether this route exists at all"* (`tools/recipes/diag_d1_full_route.py:76-78`, repeated verbatim in the FACT line at `:308-310`).

It is measured, twice, on a fresh byte-copy of this same original, on the same day:

- **1.** `tools/bench/drive_original_copy_v3.log:9-12` — copy at `claudeDev\D0_MAINCOPY_20260917_024503.vi`; `#3 open` = `GetVIReference` (`tools/bench/drive_original_copy_v2.py:208-210`), `#4 panel (False,)` = `OpenFrontPanel(False, 1)` (`:211-213`), `#5 state` = `int(vi.ExecState)` (`:214-215`) → **`STEP 2 R1 copy loads, idle  COM  PASS ExecState=1`**, at 02:45. `:8` also records the **original itself** resident at `ExecState=1`.
- **0.** `tools/bench/build_d1_v0_run5.log:13-16` — copy at `claudeDev\Track_v6_D1_GPU_081752.vi`; `tools/recipes/build_d1_v0.py:413` opens the panel (`g.open_panel(TARGET)`) and `:419` reads `g.exec_state(TARGET)` → **0**, at 08:17 the same morning.

So the precondition `copy_by_index` needs (`tools/gscript.py:1351-1354`) has already been observed **holding** once and **failing** once, and P2a as written reproduces one of the two without telling you which variable produced it.

**Scope.** Covers P2a as a *new* measurement and its framing as the deciding unknown. It does **not** cover measuring the **discriminator** between the two records — the ~1.3 s gap between panel-open and read in v3 versus the immediate read in `build_d1_v0`, the `GetVIReference` that preceded the panel in v3, warm versus cold instance. That is genuinely unmeasured, it is one line of code, and it is the measurement this run should buy.

### A2 `contradicted` — "a scratch copy reads 0 **headlessly**" describes a measurement whose panel was open

- Plan side: `docs/d1-build-plan.md:203` — *"a scratch copy of the original reads **`ExecState 0`** when opened **headlessly**, before any edit"*; repeated at `tools/recipes/build_d1_v0.py:419` and `tools/bench/build_d1_v0_run5.log:16`, and inherited by `diag_d1_full_route.py:76-78`.
- Machine side: the panel **was** open. `tools/recipes/build_d1_v0.py:413` is `g.open_panel(TARGET)`, and `open_panel` is `OpenFrontPanel` (`tools/gscript.py:1047,:1059`); the read at `:419` is six lines later. Against `drive_original_copy_v3.log:12` (**ExecState=1** after the same call) the word "headlessly" is doing load-bearing work it cannot carry.

**Scope.** Covers the "headlessly" qualifier in `d1-build-plan.md:203` and every sentence resting on it. It does **not** claim the number 0 was misread, nor that 1 is the right answer.

### A3 `contradicted` — "an NI example as a `copy_*` donor is a recorded crash" is not what the record says

- Recipe: `diag_d1_full_route.py:36-37` — *"`copy_*` from vi.lib / an NI example is a recorded LabVIEW crash"*, which is what removes every donor except the working copy itself.
- The record names **vi.lib**, not NI examples: `docs/keystone-op-spec.md:136-143` — *"substituting **`Create Property Node.vi`**'s bytes into the Move example's source file and running OpMoveByLabel **CRASHED LabVIEW** … **Rule: copy_into only from claudeDev donors we built ourselves; never from vi.lib.**"* `Create Property Node.vi` is a vi.lib\Erdos Miller file (`tools/bench/erdos_creators.log:2,:19`).
- An **NI example** donor is recorded WORKING, twice, through `copy_by_index` itself: `tools/recipes/build_opconstvalue_v1.py:39` (`EX = claudeDev\NIScriptingExamples\Finding and Modifying Objects\Navigating Nodes and Wires.vi`), used at `:169` (Property) and `:199` (Function) — `tools/bench/build_opconstvalue_v1.log:21-25,:45-49`, all PASS.

**Scope.** Covers the premise that excludes NI-example donors and therefore the claim that donor==target is forced. It does **not** dispute the vi.lib prohibition, and does **not** assert the main VI is a safe donor.

### A4 `contradicted` — §11f.2 authorises the GOAL and prescribes a DIFFERENT ORDER; it never names this route

- Recipe: `diag_d1_full_route.py:41-42` — *"`docs/d1-build-plan.md` s11f.2 **AUTHORISES exactly this**"*.
- §11f.2, verbatim: `docs/d1-build-plan.md:652-654` — *"**Authorised for PHASE 'full'** (narrow, D1 parts only): the sentinel comparison primitive and the literals it needs inside the loop bodies — **`OpConstValue`/`build_case` first**, additive builds only where those cannot produce the node."*

It authorises the **objective**, names two tools to try **first**, and permits **additive builds** as the fallback. `copy_by_index` is neither of the named two nor an additive build, and "donor == target" appears nowhere in it.

**Scope.** Covers the authorisation claim at `:41-42`. It does **not** dispute that the objective is authorised, and does **not** assert `OpConstValue`/`build_case` can produce the node — `OpConstValue_v1`/`OpConstValueN_v1` are READERS (`docs/toolkit-capabilities.md:46-47`) and `build_case` is top-level with a front-panel selector (`tools/gscript.py:2616-2625`), so §11f.2's "first" clause may well be discharged on inspection. That discharge has to be written down, not skipped.

### A5 `refuted-already` — `restore_move_fixtures()` in a `finally` is the exact defect this project fixed on 2026-09-15

- Recipe: `diag_d1_full_route.py:452-456` calls `g.restore_move_fixtures()` inside `main`'s `finally`.
- The helper forbids it: `tools/gscript.py:1268-1272` — *"ONLY when nothing of theirs is loaded (call it at the START of a copy, **never in a finally while a VI may still be in memory**: peer `archive/peer/2026-09-15-strtopath-fail4-gui-save-of-broken-target.md` — restoring the disk under a loaded, dirty VI creates the changed-on-disk split-brain that needs a LabVIEW restart)."*
- The exchange: that file's `:75` — *"On failure: do **not** restore disk bytes in `finally`"*; `:81` — *"The current unconditional disk restore in `finally` should be treated as the **primary protocol defect**."* Disposition `:118-122`: adopted in full, LabVIEW restarted, `copy_by_index` rewritten.
- **The failure path is live here.** `tools/gscript.py:1351-1354` raises *before* `close_panel(MOVE_DST)` at `:1357`, and `:1292-1293` says on failure *"nothing is restored … the next call's restore (with nothing loaded, or after a restart) cleans up"*. Given A1, the P2b raise is a realistic branch — and on it the recipe restores fixture bytes under a still-loaded, dirty `MOVE_DST` holding the main VI's contents.

**Scope.** Covers the `finally` placement at `:452-456`. It does **not** object to the sanctioned start-of-copy call.

---

## PART B — THE ARTIFACT

### B1 `already-measured` — P2c is run 5's S3, passed three times six hours earlier

P2c predicts *"owner chain uid → body Diagram → that WhileLoop, and NO new panel object (ControlTerminal 114, Local 8)"* for a **Constant** `move_in`-ed into a freshly created While body (`diag_d1_full_route.py:82-85,:393-399`).

`tools/bench/build_d1_v0_run5.log:100-108` records exactly that, three times, with the same reader:

```
OBSERVED uid 3529 -> owner 'Diagram' uid 1194 | self 'ControlReferenceConstant'#3529 …
PASS  S3 #3529 -> 1.5  owner Diagram#1194 …; owner(owner) WhileLoop#1134 …
```

…and `#3560`, `#3447` identically; `:109` lists the body's contents. The no-panel-object half is S3c in the same run — `ControlTerminal` still 114 (`archive/2026-09-17-status-d1-phase-full-narrative.md:132`). Why a Constant is reachable was written up the same day: `:31-35`.

**Scope.** Covers *"a diagram Constant can be `move_in`-ed into a new While body, owner chain verified, no panel object"*. It does **not** cover a **freshly copied** constant as the subject — provenance is the one untested variable — so P2c is legitimate only as the second half of P2b's outcome, never as a question of its own.

### B2 `unread-evidence` — "donor == target" is the recipe's own addition; the recorded route does not need it

- Recipe: `:37-38` and `:74` — *"The one route that touches no original and no vi.lib donor is `copy_by_index` with the D1 working copy as BOTH donor and target"*.
- The sibling recipe wrote this route down first, without that requirement: `tools/recipes/build_d1_v0.py:43-47` — *"a route exists with BUILT ops: the original itself carries donor constants of exactly the needed values … so `copy_by_index` … + `move_in` (12/0) places them with no new op. **MEASURED, UNWRITTEN — see CONST_DONORS below.**"* — and `:237` `CONST_DONORS = {0: 3130, 1: 3683, 20: 451, -1: 4609, 25: 25175}`, already emitted in run 5's JSON (`:900`).
- A **second, separately named copy of the original** is an ordinary claudeDev donor (copies are always permitted, CLAUDE.md rule 1), keeps `copy_by_index` in its recorded shape, and clears its only same-file guard trivially (`tools/gscript.py:1313-1314` refuses identical *paths*).
- Also on record about this call inside one VI: `tools/recipes/probe_move_into_v0.py:88-90` — *"`copy_by_index()` … copies an object into a target's TOP-LEVEL diagram … it cannot place into a nested diagram and **cannot relocate inside one VI. Not a route.**"*

**Scope.** Covers the claim that donor==target is *the* route and its framing as the untried novelty. It does **not** claim donor==target fails; and `probe_move_into_v0.py:88-90` is about **relocating**, not duplicating (`duplicate=True`, `tools/gscript.py:1330`), so it is a caution, not a refutation.

### B3 `unread-evidence` — P2d's "only fleet feeders" list omits three things already in our own files

`diag_d1_full_route.py:405-410` concludes the comparison half stops because *"the only fleet feeders at top level are `create_control` … or another TOP-LEVEL node's output, and a Constant is not a `Nodes[]` member"*. Three omissions:

1. **`Constant.Terminal` 634AC04** — *"a base-`Constant` property and therefore applies to every actual Constant descendant"* (`archive/peer/2026-09-15-opconstvaluen-scan-three-selectors-missing.md:74-76`), already read inside a built op (`docs/toolkit-capabilities.md:47`), whose partner `Terminal.Connect Wire` **6349C03** is already a WRITER inside a built op (`docs/toolkit-capabilities.md:51`, `OpStopFromNode_v0`). A copied constant feeding a copied primitive's required input creates **no panel object** — precisely the additive build §11f.2 permits once `OpConstValue`/`build_case` are shown not to produce the node.
2. **The erdosmiller creators, already censused terminal by terminal.** `archive/bench-2026-09-14-stage2-toolkit/probe_queue_vis.log:10` — `Create Equal.vi: … 'Diagram in' … 'x' … 'x = y?' … 'y' … 'Compare Aggregates?'`; `:9` — `Create Constant.vi: … 'Diagram in' … 'Type' … 'Terminal' … 'Value'`. The pattern that turns such a creator into an op placing a node **on any diagram by Traverse index, with an input already wired**, is `queue_node` (`tools/gscript.py:928-934`; `docs/toolkit-capabilities.md:32`, *"places one queue primitive on any diagram"*, exercised 162/162) — built from the same `Create *.vi` family in the same folder.
3. **The sibling recipe already states this design question and its status**: `tools/recipes/build_d1_v0.py:40-47` and `:844-847` — *"`create_control` adds a PANEL CONTROL and contradicts the plan's own 'ControlTerminal still 114', while `Terminal.Create Constant` 6349C00 is catalogued only and an op for it is frozen by `cycle15-plan.md:104`"*. P2d reports this as a fresh OPEN; it is a restatement.

**One consequence inside P2d itself.** `traverse_index`'s candidate classes (`:246-247`) are `DigitalNumericConstant, Function, CaseStructure, SubVI, IndexArray, ForLoop, Node`, and the class our files record for the `x=y?`/`x<y?` primitives is **`Comparison`** (`docs/toolkit-capabilities.md:48`, *"sink `Comparison` 10950"*). If `Function` does not subsume it, P2d's FACT line reports `None[None]` for `Equal?` #10019 and the "design call" is reported off a lookup failure rather than the arithmetic the docstring promises.

**Scope.** Covers the enumeration at `:405-410` and the candidate list at `:246-247`. It does **not** claim (1) or (2) is a built placer today — both are new/additive builds and the general-purpose freeze (`docs/cycle15-plan.md:104`, `build_d1_v0.py:42-43`) still governs. Routes to price, not builds to start.

---

## The five questions, answered

1. **`copy_by_index` with donor == target: never tried here, and the record does not require it.** Every recorded call is donor ≠ target (`build_opconstvalue_v1.py:169,:199`, `build_opwiresource_v1.py:177`, `build_opwiresource_v2.py:144`, `build_strtopath.py:113`, `build_track_v6_queue.py:136`). The recorded route needs only a donor that *contains* the constants (`build_d1_v0.py:43-47,:237`). Two recorded reasons it can still fail, neither about the donor: the ExecState-1-before-save rule (`gscript.py:1351-1354`) against A1's split record, and the fixture protocol (A5). One recorded caution about this call inside one VI: `probe_move_into_v0.py:88-90`.
2. **Yes — recorded twice, in disagreement.** `drive_original_copy_v3.log:9-12` = **1** (panel opened, then read); `build_d1_v0_run5.log:13-16` = **0** (panel opened at `build_d1_v0.py:413`, read at `:419`). `d1-build-plan.md:203`'s "headlessly" is false of the measurement it describes.
3. **Yes for the `move_in` half — run 5, S3, three times** (`build_d1_v0_run5.log:100-109`). The copy half is done elsewhere but never on a constant, and the *composition* is untried, so P2b is the only part of P2 that asks something new.
4. **Your P2d stop is over-stated.** The record contains a way to feed a copied primitive with no panel object: `Constant.Terminal` 634AC04 + `Terminal.Connect Wire` 6349C03, both inside built ops (`toolkit-capabilities.md:47,:51`); and `Create Equal.vi` / `Create Constant.vi` are censused (`probe_queue_vis.log:9-10`) with `queue_node` as the proven placement pattern (`toolkit-capabilities.md:32`). Neither is built today, so the *stop* may still be right — but state it as "frozen, and here are the two priced routes", not "no feeder exists".
5. **Contradicted cited facts:** the NI-example crash claim (A3), the §11f.2 authorisation (A4), the "unmeasured open-panel ExecState" (A1) and the "headlessly" qualifier it inherits (A2). Correctly cited and untouched: `gscript.py:1351-1354`, `gscript.py:1360`, `toolkit-capabilities.md:494`, `toolkit-capabilities.md:213` (the control rule), `CONST_DONORS[-1] = 4609`, and the stale-in-memory-VI class behind the per-stage filenames.

---

```
PRIOR-ART: already-measured  (A1 — tools/bench/drive_original_copy_v3.log:8-12 + tools/bench/drive_original_copy_v2.py:114,:208-215 + tools/bench/build_d1_v0_run5.log:13-16 + tools/recipes/build_d1_v0.py:413,:419 vs tools/recipes/diag_d1_full_route.py:76-78,:308-310 — covers P2a as a new measurement and as "the deciding unknown"; does NOT cover measuring the discriminator between the recorded 0 and 1)
PRIOR-ART: contradicted      (A2 — docs/d1-build-plan.md:203 + tools/recipes/build_d1_v0.py:413 + tools/gscript.py:1047,:1059 vs tools/bench/drive_original_copy_v3.log:12 — covers the word "headlessly" and every claim resting on it; does NOT claim either number was misread)
PRIOR-ART: contradicted      (A3 — docs/keystone-op-spec.md:136-143 + tools/bench/erdos_creators.log:2,:19 + tools/recipes/build_opconstvalue_v1.py:39,:169,:199 + tools/bench/build_opconstvalue_v1.log:21-25,:45-49 vs tools/recipes/diag_d1_full_route.py:36-37 — covers "an NI example is a recorded crash" and the donor exclusion built on it; does NOT dispute the vi.lib prohibition)
PRIOR-ART: contradicted      (A4 — docs/d1-build-plan.md:652-654 vs tools/recipes/diag_d1_full_route.py:41-42 — covers "s11f.2 AUTHORISES exactly this"; does NOT dispute that the objective is authorised, nor assert OpConstValue/build_case can produce the node)
PRIOR-ART: refuted-already   (A5 — tools/gscript.py:1268-1272,:1292-1293,:1351-1357 + archive/peer/2026-09-15-strtopath-fail4-gui-save-of-broken-target.md:75,:81,:118-122 vs tools/recipes/diag_d1_full_route.py:452-456 — covers restore_move_fixtures() in a finally; does NOT object to the start-of-copy call)
PRIOR-ART: already-measured  (B1 — tools/bench/build_d1_v0_run5.log:100-109 + archive/2026-09-17-status-d1-phase-full-narrative.md:31-35,:132 vs tools/recipes/diag_d1_full_route.py:82-85,:393-399 — covers "a Constant move_in-ed into a new While body, owner chain, no panel object"; does NOT cover a freshly COPIED constant as the subject)
PRIOR-ART: unread-evidence   (B2 — tools/recipes/build_d1_v0.py:43-47,:237,:900 + tools/gscript.py:1313-1314,:1330 + tools/recipes/probe_move_into_v0.py:88-90 vs tools/recipes/diag_d1_full_route.py:37-38,:74 — covers "donor == target is the one route"; does NOT claim donor == target fails, and probe_move_into_v0.py:88-90 is cited for RELOCATION, not duplication)
PRIOR-ART: unread-evidence   (B3 — docs/toolkit-capabilities.md:32,:47,:48,:51 + archive/peer/2026-09-15-opconstvaluen-scan-three-selectors-missing.md:74-76 + archive/bench-2026-09-14-stage2-toolkit/probe_queue_vis.log:9-10 + tools/gscript.py:928-934 + tools/recipes/build_d1_v0.py:40-47,:844-847 vs tools/recipes/diag_d1_full_route.py:405-410,:246-247 — covers P2d's "only fleet feeders" enumeration and the Comparison-class omission; does NOT claim any of these is a built placer today, and the general-purpose freeze still governs)
```

**The one that changes what happens next: A1 + A2.** P2a is the gate the whole P2 run hangs on, and our own files already answer it — with two different numbers taken five and a half hours apart on the same day. Re-running P2a as specified buys one more sample of a bimodal measurement. What is actually unmeasured is the **variable** separating `drive_original_copy_v3.log:12` from `build_d1_v0_run5.log:16`, and that is a one-line change to P2a: read `exec_state` immediately after `open_panel`, then again after a short settle, and record both. If the second read is 1, `copy_by_index`'s precondition holds, A5's failure branch never fires, and P2b/P2c become the cheap run they were meant to be.

## Sources

(extract from answer)

## What was done with it

**ALL EIGHT FINDINGS ACCEPTED. NONE REFUTED.** No citation was opened and shown not to cover its case. Disposed
2026-09-17 09:1x by the material session that dispatched it. Between them these findings dismantle the premise
that made `donor == target` look forced, and convert P2a from a yes/no precondition into the one measurement
worth buying.

**FIXED: A5 `refuted-already` — `restore_move_fixtures()` in a `finally`. Removed.** This is the one finding with
a live safety consequence: `tools/gscript.py:1268-1272` forbids it in terms
(*"never in a finally while a VI may still be in memory"*), the protocol defect was already adopted and fixed on
2026-09-15 (`archive/peer/2026-09-15-strtopath-fail4-gui-save-of-broken-target.md:75,:81,:118-122`), and — given
A1 — the raise at `gscript.py:1351-1354` is a realistic branch that would have left my `finally` restoring fixture
bytes under a still-loaded, dirty `MOVE_DST` holding the main VI's contents. `copy_by_index` already restores at
the START of every call (`:1320`), which is the sanctioned placement; the recipe now relies on that and restores
nothing itself.

**FIXED: A1 + A2 `already-measured` / `contradicted` — P2a rewritten as the DISCRIMINATOR.** The number is in the
record twice and the records disagree on a byte-copy of this same original on the same morning: **1** in
`tools/bench/drive_original_copy_v3.log:9-12` (`GetVIReference` → `OpenFrontPanel(False,1)` → ~1.3 s → `ExecState`)
and **0** in `tools/bench/build_d1_v0_run5.log:13-16` (`g.open_panel` then `g.exec_state` six lines later). And
A2 is right that the word carrying the difference cannot carry it: `docs/d1-build-plan.md:203` says *"reads
ExecState 0 when opened **headlessly**"*, but `build_d1_v0.py:413` **had the panel open** (`open_panel` =
`OpenFrontPanel`, `gscript.py:1047,:1059`). So "headlessly" is withdrawn as the explanation. P2a now reads
`ExecState` at **three points on one copy** — after `GetVIReference`, immediately after `OpenFrontPanel(False)`,
and after a settle — which is A1's own "one line of code … the measurement this run should buy".
⚠️ `docs/d1-build-plan.md:203` and `build_d1_v0.py:419` still carry the withdrawn word; correcting a plan section
is not a material session's call, so it is raised under OPEN rather than edited.

**FIXED: A3 `contradicted` — "an NI example donor is a recorded crash". Withdrawn.** The recorded prohibition is
**vi.lib**, not NI examples: `docs/keystone-op-spec.md:136-143` (*"never from vi.lib"*, about
`Create Property Node.vi`, an Erdos Miller file — `tools/bench/erdos_creators.log:2,:19`). An NI-example donor is
recorded **working twice through `copy_by_index` itself** (`tools/recipes/build_opconstvalue_v1.py:39,:169,:199`;
`tools/bench/build_opconstvalue_v1.log:21-25,:45-49`, all PASS). I inherited this sentence from the narrative and
repeated it without opening the citation — the exact failure class the fourth review exists to catch.

**FIXED: A4 `contradicted` — "§11f.2 authorises exactly this". Withdrawn, and the "first" clause is now
DISCHARGED IN WRITING** (the review's own requirement: *"That discharge has to be written down, not skipped"*).
§11f.2 verbatim (`docs/d1-build-plan.md:652-654`) authorises the **objective** and orders
*"`OpConstValue`/`build_case` **first**, additive builds only where those cannot produce the node."* Discharge:
`OpConstValue_v1` and `OpConstValueN_v1` are **READERS** — `docs/toolkit-capabilities.md:46-47` describes both as
reading `Constant.Value` 634AC00, neither creates a node; `build_case` creates a **Case structure on the
top-level diagram from a front-panel selector by name** (`tools/gscript.py:2616-2625`), not a comparison
primitive and not a diagram constant inside a loop body. Neither named tool can produce either node, so §11f.2's
fallback clause is reached on the record. **Which fallback to take remains a judgement call** — §11f.2 permits
"additive builds", and `copy_by_index` is not one; this run therefore treats the copy route as a **measurement**,
not as a build commitment, and the choice is raised under OPEN.

**FIXED: B2 `unread-evidence` — `donor == target` dropped.** A second, separately named copy of the original is an
ordinary claudeDev donor (copies are always permitted, CLAUDE.md rule 1), keeps `copy_by_index` in its recorded
shape, and clears its only same-file guard trivially (`gscript.py:1313-1314` refuses identical **paths**). The
recipe now uses `..._donor.vi` → `..._a.vi`. Noted and carried, not refuted:
`tools/recipes/probe_move_into_v0.py:88-90` — `copy_by_index` *"cannot relocate inside one VI. Not a route."* —
which is about **relocating**, while this call duplicates (`duplicate=True`, `gscript.py:1330`); it is a caution,
and `move_in` does the nested placement afterwards.

**FIXED: B1 `already-measured` — P2c demoted to the second half of P2b.** Run 5 already measured a Constant
`move_in`-ed into a freshly created While body with the same reader, three times
(`tools/bench/build_d1_v0_run5.log:100-109`: `#3529`/`#3560`/`#3447` → `Diagram#1194` → `WhileLoop#1134`), with
`ControlTerminal` still 114. The only untested variable is **provenance** — a *freshly copied* constant — so P2c
is no longer asked as a question of its own and its gate says so.

**FIXED: B3 `unread-evidence` — the candidate class list and the "only feeders" enumeration.**
`traverse_index`'s candidates now include **`Comparison`**, the class our own files record for `x=y?`/`x<y?`
(`docs/toolkit-capabilities.md:48`, *"sink `Comparison` 10950"*) — without it P2d would have reported
`None[None]` for `Equal?` #10019 and called a lookup failure a design finding. P2d's enumeration is rewritten as
a **restatement** of `build_d1_v0.py:40-47,:844-847`, not a fresh discovery, and the two omitted routes are
recorded as **routes to price, not builds to start** (both are new/additive ops and
`docs/cycle15-plan.md:104`'s general-purpose freeze still governs): **(1)** `Constant.Terminal` **634AC04** +
`Terminal.Connect Wire` **6349C03** — a copied constant feeding a copied primitive's required input, creating
**no panel object**; **(2)** the erdosmiller `Create Equal.vi` / `Create Constant.vi` creators, already censused
terminal by terminal (`archive/bench-2026-09-14-stage2-toolkit/probe_queue_vis.log:9-10`), wrapped by the
`queue_node` pattern (`gscript.py:928-934`) that already places a primitive **on any diagram by Traverse index
with an input already wired**, 162/162.

**Net effect on the run:** P2 stops being "does the forced route work" and becomes three measurements that are
genuinely unrecorded — the ExecState discriminator (A1), whether a **copied** constant survives `move_in` into a
loop body (B1's provenance gap), and whether `copy_by_index` accepts a **second copy of the main VI** as donor
(B2). Everything else the review showed was already on file.

(Claude fills in)
