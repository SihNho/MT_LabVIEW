# priorart-d1-full-route-rev3

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $5.1799  in 58 / out 36408 / cache-create 191918 / cache-read 4700423  (507s, 44 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (510s)
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
# Plan under review ??`tools/recipes/diag_d1_full_route.py` REV 3 (cycle 15, D1)

## Two prior-art reviews already landed on this file and BOTH are fully disposed

* `archive/peer/2026-09-17-priorart-d1-full-route.md` ??6 findings, 0 novel, **all accepted**, disposition
  written in its "What was done with it".
* `archive/peer/2026-09-17-priorart-d1-full-route-rev2.md` ??8 findings, 0 novel, **all accepted**, disposition
  written there too.

Please do **not** re-litigate those 14. REV 3 is what is left after applying them, and it is deliberately small.

## What REV 3 runs

**P1 (offline, no LabVIEW).** Joins the EXISTING `d1_step0_census.json.resolved_boundary` to the 82 cut wires of
`build_d1_v0.json` (rev1 A1 killed my new join). Reports coverage and the addressing mode of all 109 cut
terminals by name vs index (rev1 B3: the record already stores `term_index` and `is_source`).

**P1b + T6.** `OpWireSource_v5` on only the wires P1 does not cover ??measured offline as exactly **w3268** ??
with `wire_source(copy, 10850)` as the **control** (`toolkit-capabilities.md:48`, released by rev1 B4's scope
note and required by `toolkit-capabilities.md:213`). If w3268's owner is `WhileLoop #637`, its source is the
frame loop's iteration terminal `i`, which is a rule-1a fact about moving `#376` to 1.7 ??reported, not decided.

**P2a ??the discriminator (rev2 A1's own "the measurement this run should buy").** `copy_by_index` requires its
Target at `ExecState 1` (`gscript.py:1351-1354`), and our record holds **both** numbers for a byte-copy of this
original on the same morning: **1** (`drive_original_copy_v3.log:9-12`) and **0** (`build_d1_v0_run5.log:13-16`).
Rev2 A2 withdrew the word meant to explain it ("headlessly" ??that run had the panel open). So one copy is read
at three points: after `GetVIReference`, immediately after `OpenFrontPanel(False)`, and after a 2 s settle.

**P2b/P2c.** `copy_by_index` of the **?? donor constant #4609** from a **second, separately named copy** of the
original (rev2 B2 ??donor==target dropped), then `move_in` into a new While body on `Diagram#686`. Rev2 B1 says
the owner-chain half is already measured for constants the VI already owned, so the gate is explicitly about the
one untested variable: **provenance** (a freshly copied constant).

**P2d is not attempted**, and REV 3 states it as a restatement of `build_d1_v0.py:40-47,:844-847` rather than a
discovery, carrying rev2 B3's two added routes as "routes to price, not builds to start".

Corrections already applied from rev2: no `restore_move_fixtures()` in a `finally` (A5 ??`gscript.py:1268-1272`
forbids it); `Comparison` added to the traverse-class candidates (B3); "NI example donor is a recorded crash"
withdrawn (A3 ??the prohibition is vi.lib only); "짠11f.2 authorises exactly this" withdrawn and 짠11f.2's
"`OpConstValue`/`build_case` **first**" clause **discharged in writing** (A4): both `OpConstValue_v1` and
`OpConstValueN_v1` are READERS (`toolkit-capabilities.md:46-47`) and `build_case` creates a top-level Case from a
front-panel selector (`gscript.py:2616-2625`), so neither can produce a comparison primitive or a diagram
constant inside a loop body.

## The questions

1. Is the **ExecState discriminator** (P2a) already measured ??is there a record of what makes a fresh copy of
   this VI read 1 rather than 0 after `OpenFrontPanel(False)`?
2. Has `copy_by_index` been run with **a copy of the main VI as the donor** before, and what happened? (Rev2 B2
   proposed this; I want to know if it was ever exercised, not just proposed.)
3. Is my written discharge of 짠11f.2's "first" clause correct ??can `OpConstValue*` or `build_case` in fact
   produce a node, contrary to `toolkit-capabilities.md:46-47` and `gscript.py:2616-2625`?
4. Is w3268's source already recorded anywhere (is it the frame loop's `i` terminal)?
5. Which of REV 3's cited facts are contradicted elsewhere in our own files?


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
27b/27c. ??**RUN 5: 53/0, 43 s**; all 23 moves; re-wire list **109 terminals / 24 uids**; collateral 0, d19 clean,
   no SR changed; S4b terms 1183/1204/1225 wire 0. Long form ??`archive/2026-09-17-status-d1-phase-full-narrative.md` 짠0.
28. ?뵶 **PHASE "full" STILL NOT WRITTEN. N1 / F1 / F2 NOT RUN ??nothing to report on them.** 짠11e.2's two ops do
   **not** cover the sentinel test: it needs a comparison primitive + literals **inside** each loop body, and
   `copy_*` from vi.lib/NI examples is a **recorded crash**. Untried route touching no original: `copy_by_index`
   with the D1 **working copy as both donor and target** + `move_in`. ??narrative 짠5.
29. ??**`OpStopFromNode_v0.vi` BUILT + SAVED, 20/2**; the write is MEASURED (cond. terminal 119, wire 0 ??**147**,
   same uid on the body node's Boolean output). **T5 CLOSED ON THE RECORD, no run needed** ??`NAMES.md:788` "never
   gate on ExecState while a required input is unwired"; the donor's `path` IS required, so run 3's 0???? said
   nothing about the op. T6's answer is published (`toolkit-capabilities.md:48`); it survives as a **control** only.
30. ?뵶 **STREAMING TSV (짠7.1) NOT BUILT ??its review stopped it** (8 findings, 0 novel). ??plan 짠11.9, archive 짠0.
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

Write is disabled here, so the review is delivered as text. No lock taken, nothing built, edited or run. The 14 findings of `2026-09-17-priorart-d1-full-route.md` and `…-rev2.md` are not re-litigated.

---

# PRIOR-ART REVIEW — `tools/recipes/diag_d1_full_route.py` REV 3 (cycle 15, D1 PHASE "full")

**6 findings, 0 novel.** Four of them land on P1b and P2a — the two halves REV 3 kept as "genuinely unrecorded".

---

## PART A — THE DIRECTION

### A1 `already-measured` — P1b's whole subject, w3268, was resolved from the machine on 2026-09-16 with the same op

REV 3 keeps P1b as the one reader call the stored resolution does not cover, predicting w3268 and citing the rev1 disposition (`tools/recipes/diag_d1_full_route.py:85-89`). That call has already been made, on the original itself, read-only, md5 unchanged:

- `tools/bench/diag_autofocus_border.py:50-54` lists `(3268, "the modulo's dividend - assumed to be the frame index")` among the three wires; `:48` imports `read_terminal` from `build_opwiresource_v5` — **the same `OpWireSource_v5`** the recipe's `wire_source()` drives (`diag_d1_full_route.py:237-272`).
- `tools/bench/diag_autofocus_border.log:19-26` — six terminals read, ending
  `RESULT wire 3268 driven by ('Diagram', 639); sinks [('Function', 2136), ('SelectorTunnel', 3045), ('LoopTunnel', 2213), ('Function', 10068), ('SubVI', 1114)]; 1 source terminal(s) of 6 read`.
- Published: `docs/camera-acquisition-facts.md:225-230`, under the heading *"Read from the machine, 2026-09-16 (`tools/bench/diag_autofocus_border.log`, `OpWireSource_v5`, MAIN md5 unchanged)"*.

**Scope.** Covers `wire_source(copy, 3268)` as a measurement of **the source**. It does **not** cover the sink list: `diag_autofocus_border.py:62` is `for i in range(6)`, so terminals 6+ were never read, while `docs/frame-loop-wire-graph.md:151` names six sinks for this wire. Re-running with `max_terms=8` to **complete the sink enumeration** is legitimate and this finding releases on that; re-running to learn the source is not.

### A2 `contradicted` — P1b's predicted content is the opposite of what the machine returned, including the rule-1a clause

- Plan: `diag_d1_full_route.py:86-89` — *"Predicted content: w3268 (six sinks … and **no source among nodes, tunnels, registers, constants or panel terminals**). **If its owner is `WhileLoop #637`, the source is the frame loop's ITERATION terminal `i`**, and that is a rule-1a FACT about moving `#376` to 1.7."*
- Machine: `tools/bench/diag_autofocus_border.log:20` — `wire 3268 Terms[0] source=True owner 'Diagram' uid 639`. The owner is **`Diagram` 639**, the frame loop's body diagram, not `WhileLoop #637`, and a source terminal exists.
- What a `Diagram`-owned source terminal means here is already written down: `docs/camera-acquisition-facts.md:235-237` — *"**A source terminal owned by a `Diagram` is the control-terminal signature** … A constant on the same diagram looks identical, so the label comes from `panel_wiring`, not from the signature."* That is precisely the two categories `:86-89` says the source is **not** in.

So the conditional the plan carries forward as a rule-1a fact — `#376`'s `i` — is refuted on the record before the run starts.

**Scope.** Covers `:86-89`'s prediction and its rule-1a conditional. It does **not** decide *which* diagram-owned object drives w3268; `camera-acquisition-facts.md:237` says that needs a `panel_wiring` label, and that read is untaken.

### A3 `contradicted` — P2a's citation does not say what P2a reads. `gscript.py:1351` reads `MOVE_DST`, not the target

- Plan: `diag_d1_full_route.py:94-97` and the FACT line at `:359-363` — *"The precondition `copy_by_index` needs (`gscript.py:1351-1354`: **the Target must be ExecState 1**)"*, and the code then reads `ExecState` of **`T0`** at three points (`:344-358`).
- Machine: `tools/gscript.py:1351` is `es = exec_state(MOVE_DST)`. `MOVE_DST` is the fixed NI Move-example fixture `…\claudeDev\NIScriptingExamples\Moving Objects\Test - Moving Objects Target.vi` (`tools/gscript.py:55`), onto which the target's *bytes* are copied at `:1321` (`_copy("target -> MOVE_DST", target, MOVE_DST)`) and reverted at `:1322-1326`. The gate fires **after** the Move and after the `finish` hook (`:1339-1354`), and the result is copied back to `target` only at `:1360`.

The number P2a collects is therefore the ExecState of a *different file*, at a *different path*, at a *different point in the protocol*, from the one the gate reads. Every recorded caller gates its own op instead, before the call (`build_opconstvalue_v1.py:166`, `build_opwiresource_v1.py:176`, `build_opwiresource_v2.py:143`).

**Scope.** Covers the mapping of `gscript.py:1351-1354` onto `T0`'s own path in `:94-97`/`:359-363`. It does **not** claim the fixture will read a different number than `T0` would — that is unmeasured, and reading `exec_state(MOVE_DST)` is the read that matches the citation.

### A4 `unread-evidence` — the discriminator candidate is in the record **three times**, one line above the plan's own citation

The plan cites `drive_original_copy_v3.log:9-12` for the **1** (`:97-98`). The decisive line is `:7-8`, immediately before the range it quotes:

```
[  13.3s]   com.deq  #2 preload ('…\Min_Track N beads V6_ParallelLoop.vi',)
[  14.6s] STEP 1b original resident (read-only) COM  PASS original resident (ExecState=1)
```

`preload` is `app.GetVIReference(<the ORIGINAL>)` (`tools/bench/drive_original_copy_v2.py:205-207`, dispatched at `:739-740`) — i.e. **the whole original hierarchy is made resident before the copy is opened** at `:743-745`. The record then splits cleanly:

| ExecState of a fresh claudeDev byte-copy | original preloaded first? | evidence |
|---|---|---|
| **1** | yes | `drive_original_copy_v3.log:7-12` · `drive_original_copy_v2.log:8-13` · `d0_clickprobe.log:7-12` |
| **0** | no | `build_d1_v0_run5.log:13-16` · `build_d1_v0_run4.log:18` · `probe_move_into_v0.log:217` |

Three and three, on the same original, same claudeDev destination, all within one day. The elapsed gap between panel-open and read is ~1.3–1.4 s in **all three** of the "1" runs, so time is fully confounded with preload. P2a varies **only** elapsed time on one copy (`:349-358`, a 2 s settle) and never preload — so it cannot separate the two, and on a run with no preload it is predicted by six data points to print `0, 0, 0`.

**Scope.** Covers P2a's claim to be *the* discriminator (`:94-102`). It does **not** assert preload is the cause — it has never been varied in a controlled pair, and doing that (one copy read with the original resident, one without, same instance) is one line and is the measurement still worth buying.

### A5 `contradicted` — the P2 banner still announces the design rev2 B2 removed

- `diag_d1_full_route.py:335` — `print("\n=== P2: `copy_by_index` with donor == target, then `move_in` …")`.
- The same file, `:47-49` and `:155-159`, `:406`: donor == target is **dropped**; the donor is `TDONOR`, a separately named second copy.

The banner is what lands in `tools/bench/diag_d1_full_route.log`, which is what the retrospective, `audit_cycle` and the next session read. A one-line edit releases it.

**Scope.** Covers the string at `:335` only. Nothing else in the file still carries donor == target.

---

## PART B — THE ARTIFACT

### B1 `already-failed` — a `copy_by_index` session that does not start on a FRESH LabVIEW instance is a recorded Errno 22 failure, and the recipe does not restart

- `tools/recipes/build_track_v6_queue.py:105-109`, `fresh_labview()`: *"Run 1 (03:16): **`copy_by_index` died with Errno 22 on the Move-example Target while LabVIEW still had that VI LOADED** from the 00:3x StrToPath copy — the substitution protocol must never overwrite a loaded VI's file (peer …-strtopath-fail4 / …-queue-fail1-errno22). **A `copy_by_index` session therefore starts on a FRESH instance** (standing restart permission)."* It kills LabVIEW at `:111-114` and is called at `:121`, immediately before the copy at `:136`.
- The helper states the same rule about itself: `tools/gscript.py:1304-1307` — *"substitute the bytes FIRST, on an instance where nothing of theirs is loaded (**the caller restarts LabVIEW before a `copy_by_index` session**)"*, and `:1309-1319` exists only to attribute that Errno 22.
- `build_opconstvalue_v1.py:197` calls `fresh()` before its second `copy_by_index` at `:199`.
- `diag_d1_full_route.py` calls `copy_by_index` at `:410` with no restart anywhere in the file; `g._lv = None` at `:481` clears only the Python COM handle, not LabVIEW's loaded VIs, and the run is dispatched into the long-lived instance the lock currently names.

**Scope.** Covers the missing fresh-instance step before `:410`. It does **not** claim the fixtures are loaded right now — that is exactly what the recorded protocol refuses to depend on.

### B2 `unread-evidence` — "provenance is the only untested variable" omits that BOTH files are relocated to the fixture paths, and the hierarchy hazard is already on file

`:107-110` names provenance as the one untested variable, inheriting rev2 B1. But the protocol does not copy an object *from* `TDONOR` *into* `T0` in place: `tools/gscript.py:1321` byte-copies **both** onto `Test - Moving Objects Source.vi` / `…Target.vi` and `:1322-1326` `revert()`s them **there**, under `claudeDev\NIScriptingExamples\Moving Objects\` (`gscript.py:53-55`). Two ~473 kB copies of the main VI (`drive_original_copy_v2.log:3`) are then loaded from a directory that is not their hierarchy's.

Every donor on record is small and self-contained — NI example (`build_opconstvalue_v1.py:39`), `OpReport_v3`/`OpWireSource_v5` lineage (`build_opwiresource_v1.py:177`, `build_opwiresource_v2.py:144`), `save N xyz traces.vi` (`build_strtopath.py:31`, `build_track_v6_queue.py:38`). **None is the main VI**, so REV 3's question 2 is correctly identified as unasked — but the variable it introduces is not provenance alone. The hazard class is recorded: `archive/peer/2026-09-14-setcommand-signed-fail4-openpanel-after-restart.md:38-39` — *"moving only a caller changes relative dependency resolution; NI explicitly recommends copying the hierarchy"*.

**Scope.** Covers the "only untested variable is PROVENANCE" framing at `:107-110`. It does **not** predict the copy fails, and it does not touch P2c's owner-chain half.

---

## The five questions, answered

1. **The ExecState "discriminator" is not measured, but it is also not what P2a measures (A3), and the candidate variable is already in the record six times (A4).** No file says what makes a fresh copy read 1 rather than 0. What the files do say is that all three recorded **1**s follow a `preload` of the original and all three recorded **0**s do not. P2a as written varies neither that nor the file the gate actually reads.
2. **`copy_by_index` has never been run with a copy of the main VI as donor** — every recorded donor is a small op VI or `save N xyz traces.vi` (citations in B2). The thing the record does add is that the *target* is relocated to the fixture path too, and that a session without a fresh instance is a recorded Errno 22 (B1).
3. **Your §11f.2 discharge is correct, and I could not break it.** `docs/toolkit-capabilities.md:46-47` describes `OpConstValue_v1` and `OpConstValueN_v1` purely as readers of `Constant.Value` 634AC00 (the `Constant.Terminal` 634AC04 hop in `:47` is read-only, to report the wire a constant drives); `tools/gscript.py:2616-2625` places a Case Structure **on `target`'s top-level diagram** from a front-panel selector by label, with a contract of *"+1 CaseStructure, +2 Diagrams, +1 wire per name"* and no constant and no primitive. `gscript.py`'s full public surface contains no constant creator. Neither named tool can produce the node; the fallback clause is reached.
4. **Yes — `docs/camera-acquisition-facts.md:230` / `tools/bench/diag_autofocus_border.log:20-26`: w3268 is driven by `Diagram` 639, not by `WhileLoop #637`'s `i`** (A1, A2). The only part of P1b still worth a call is the sink list beyond terminal index 5.
5. **Contradicted cited facts:** `gscript.py:1351-1354` as "the Target must be ExecState 1" (A3), P1b's predicted w3268 content and its rule-1a conditional (A2), and the P2 banner (A5). **Correctly cited and untouched:** `gscript.py:1313-1314` (identical *paths*), `gscript.py:1360`, `gscript.py:1268-1272` and the absent `finally` restore, `docs/toolkit-capabilities.md:213` releasing T6 as a control, `docs/toolkit-capabilities.md:46-47`, `:48`, `:51`, `:494`, `gscript.py:2616-2625`, `cycle15-plan.md:104`'s freeze, `build_d1_v0.py:40-47,:844-847` as the restatement source, `Comparison` in the candidate list, and `BEFORE_COUNTS` against `build_d1_v0_run5.log:14`.

One non-blocking note, no slug: `move_in()` at `:202-218` is now the **third** verbatim copy of `probe_move_ctlterm_v0.py:160-178` (the second is in `build_d1_v0.py`), and `gscript.py` has no `move_in`. It is honestly cited, so it is not a finding — but the toolkit gap behind three copies is real.

---

```
PRIOR-ART: already-measured  (A1 — tools/bench/diag_autofocus_border.log:19-26 + tools/bench/diag_autofocus_border.py:48,:50-54,:59-62 + docs/camera-acquisition-facts.md:225-230 vs tools/recipes/diag_d1_full_route.py:85-89,:383-391 — covers wire_source(copy,3268) as a SOURCE measurement; does NOT cover sink terminals beyond index 5, which diag_autofocus_border.py:62 never read)
PRIOR-ART: contradicted      (A2 — tools/bench/diag_autofocus_border.log:20 + docs/camera-acquisition-facts.md:230,:235-237 + docs/frame-loop-wire-graph.md:151,:455 vs tools/recipes/diag_d1_full_route.py:86-89 — covers "no source among nodes, tunnels, registers, constants or panel terminals" and the "owner is WhileLoop #637 -> iteration terminal i" rule-1a conditional; does NOT decide which diagram-owned object drives w3268)
PRIOR-ART: contradicted      (A3 — tools/gscript.py:55,:1321,:1322-1326,:1339-1354,:1360 + tools/recipes/build_opconstvalue_v1.py:166 + tools/recipes/build_opwiresource_v2.py:143 vs tools/recipes/diag_d1_full_route.py:94-97,:344-358,:359-363 — covers mapping the gscript.py:1351-1354 gate onto T0's own path; does NOT claim MOVE_DST reads a different number than T0)
PRIOR-ART: unread-evidence   (A4 — tools/bench/drive_original_copy_v3.log:7-8 + tools/bench/drive_original_copy_v2.py:205-207,:739-745 + tools/bench/drive_original_copy_v2.log:8-13 + tools/bench/d0_clickprobe.log:7-12 + tools/bench/build_d1_v0_run4.log:18 + tools/bench/probe_move_into_v0.log:217 vs tools/recipes/diag_d1_full_route.py:94-102 — covers P2a's claim to BE the discriminator; does NOT assert preload is proven causal, since it has never been varied in a controlled pair)
PRIOR-ART: contradicted      (A5 — tools/recipes/diag_d1_full_route.py:335 vs :47-49,:155-159,:406 — covers the P2 banner string that still announces donor == target; nothing else in the file carries it)
PRIOR-ART: already-failed    (B1 — tools/recipes/build_track_v6_queue.py:105-115,:121,:136 + tools/gscript.py:1304-1307,:1309-1319 + tools/recipes/build_opconstvalue_v1.py:197,:199 vs tools/recipes/diag_d1_full_route.py:410,:481 — covers the missing fresh-LabVIEW step before a copy_by_index session; does NOT claim the Move fixtures are loaded right now)
PRIOR-ART: unread-evidence   (B2 — tools/gscript.py:53-55,:1321,:1322-1326 + tools/recipes/build_opconstvalue_v1.py:39 + tools/recipes/build_opwiresource_v1.py:177 + tools/recipes/build_strtopath.py:31 + tools/recipes/build_track_v6_queue.py:38 + tools/bench/drive_original_copy_v2.log:3 + archive/peer/2026-09-14-setcommand-signed-fail4-openpanel-after-restart.md:38-39 vs tools/recipes/diag_d1_full_route.py:107-110 — covers "provenance is the only untested variable"; does NOT predict the copy fails, and does not touch P2c's owner-chain half)
```

**The one that changes what happens next: A4 with A3.** P2 is the run REV 3 exists for, and its gate is a number read from the wrong file (A3) by a procedure that cannot move the variable the record actually differs on (A4). The cheap fix keeps the run and costs nothing extra: start the session on a fresh instance (B1), read `exec_state` on a copy **without** preloading the original, then `GetVIReference` the original and read the same copy again — that is the controlled pair — and have `copy_by_index` report `exec_state(MOVE_DST)` at `gscript.py:1351` when it raises. P1b, meanwhile, should shrink to "complete the sink list past terminal 5", because its source answer has been on file since 2026-09-16.

## Sources

(extract from answer)

## What was done with it

**ALL SEVEN FINDINGS ACCEPTED. NONE REFUTED.** Disposed 2026-09-17 09:4x. This was the THIRD prior-art round on
one diagnostic — 21 findings across the three, **0 novel in any of them** — and that count is itself the finding
that ends the run: every question this recipe was built to ask was already answered in our own files, and what is
left is a decision, not a measurement. The recipe is left CORRECTED for the next session; it is **not run**, and
why is stated under OPEN.

**FIXED: A1 + A2 `already-measured` / `contradicted` — P1b is DELETED, and its prediction was backwards.** w3268
was resolved from the machine on 2026-09-16 with the same op, on the original, read-only, md5 unchanged
(`tools/bench/diag_autofocus_border.log:19-26`, published at `docs/camera-acquisition-facts.md:225-230`):

```
wire 3268 Terms[0] source=True owner 'Diagram' uid 639
RESULT wire 3268 driven by ('Diagram', 639); sinks [('Function', 2136), ('SelectorTunnel', 3045),
       ('LoopTunnel', 2213), ('Function', 10068), ('SubVI', 1114)]
```

So the one wire my offline join could not source **has a recorded source**, and with it the re-wire source map
is complete at **82/82** (81 offline + this) with no LabVIEW run at all. My predicted content was the opposite of
the record on both halves: there IS a source terminal, and its owner is **`Diagram` 639**, not `WhileLoop #637`.
**The rule-1a conditional I carried forward is therefore REFUTED before it was ever tested** — `#376`'s
`frame index` is not the frame loop's iteration terminal `i`, so the "1.7's own `i` counts writer iterations"
hazard I raised does not arise from this wire. What a `Diagram`-owned source terminal means is also already
written: `docs/camera-acquisition-facts.md:235-237` — *"A source terminal owned by a `Diagram` is the
control-terminal signature … A constant on the same diagram looks identical, so the label comes from
`panel_wiring`, not from the signature."* **Which** diagram-owned object drives w3268 is still open and needs a
`panel_wiring` label read; A1's scope note also releases a re-run at `max_terms=8` to complete the sink
enumeration (`diag_autofocus_border.py:62` read only `range(6)`, while `frame-loop-wire-graph.md:151` names six
sinks). Both are recorded as the cheap remainder, not done here.

**FIXED: A3 `contradicted` — P2a read the wrong file.** `tools/gscript.py:1351` is `es = exec_state(MOVE_DST)`,
and `MOVE_DST` is the fixed NI Move-example fixture (`gscript.py:55`) onto which the target's *bytes* are copied
at `:1321`; the gate fires after the Move and after the `finish` hook. My P2a read `ExecState` of **`T0`**, a
different file at a different path at a different point in the protocol, while citing that line. Every recorded
caller gates its **own op** before the call instead (`build_opconstvalue_v1.py:166`,
`build_opwiresource_v2.py:143`). The citation is removed from the recipe.

**FIXED: A4 `unread-evidence` — the discriminator is PRELOAD, and my P2a could not have found it.** The decisive
line is one above the range I quoted: `drive_original_copy_v3.log:7` — `#2 preload ('…Min_Track N beads
V6_ParallelLoop.vi',)`, i.e. `GetVIReference` on the **original hierarchy** before the copy is opened
(`drive_original_copy_v2.py:205-207,:739-745`). The record then splits 3–3 with no exceptions:

| ExecState of a fresh claudeDev byte-copy | original preloaded? | evidence |
|---|---|---|
| **1** | yes | `drive_original_copy_v3.log:7-12` · `drive_original_copy_v2.log:8-13` · `d0_clickprobe.log:7-12` |
| **0** | no | `build_d1_v0_run5.log:13-16` · `build_d1_v0_run4.log:18` · `probe_move_into_v0.log:217` |

The ~1.3–1.4 s panel-open-to-read gap is present in **all three** of the "1" runs, so elapsed time is fully
confounded with preload — and P2a varied only elapsed time (a 2 s settle) on one copy, so six data points predict
it would have printed `0, 0, 0` and taught nothing. The controlled pair (one copy read with the original
resident, one without, same instance) is one line and is the measurement still worth buying; it is written into
the recipe as P2a but **not run**, because B1 below makes the run itself unsafe as the file stands.

**FIXED: B1 `already-failed` — the recipe would have hit a RECORDED Errno 22.** `build_track_v6_queue.py:105-109`:
*"Run 1 (03:16): `copy_by_index` died with **Errno 22** on the Move-example Target while LabVIEW still had that
VI LOADED … a `copy_by_index` session therefore starts on a FRESH instance"*, and the helper says the same about
itself (`gscript.py:1304-1307`). My file called `copy_by_index` with **no restart anywhere**, into the long-lived
instance the lock names; `g._lv = None` clears the Python COM handle, not LabVIEW's loaded VIs. This is the
single reason the file is not run today even though the gate would currently pass: running it would spend a
failure-budget slot on a defect already in the record.

**FIXED: A5 `contradicted` — the P2 banner still printed "donor == target"**, which rev2 B2 had removed
everywhere else. That string is what lands in the log the retrospective and the next session read. Corrected.

**ACCEPTED, recorded: B2 `unread-evidence`.** "Provenance is the only untested variable" also omits that BOTH
files are byte-copied onto the fixture paths under `claudeDev\NIScriptingExamples\Moving Objects\` and
`revert()`ed there — two ~473 kB copies of the main VI loaded from a directory that is not their hierarchy's.
Noted in the recipe beside P2b/P2c as a second untested variable, not resolved.

(Claude fills in)
