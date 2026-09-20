# priorart-master-plan-rev5

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $6.5677  in 78 / out 38614 / cache-create 216754 / cache-read 6868921  (544s, 50 turn(s))
- **date:** 2026-09-16
- **outcome:** ANSWERED (549s)
- **why asked:** fourth round on the same plan (rev2 16 → rev3 18 → rev4 11 → **rev5 13**), asking whether the
  corrected plan still repeats or contradicts our own files. **Its most useful finding is about the day itself:
  most of rev5's `contradicted` verdicts are inconsistencies I introduced in the previous two hours** — 0.5 saying
  both "not a blocker" and "cannot simply be started"; the reseed stress test withdrawn in the intro but surviving
  in 2B/2C and in STATUS; a rotor repoint added to 1.4 that `rotor-sign-diagnosis.md:145-147` had already ruled out
  **quoting the user** (*"configuration은 그대로 쓰면 되는데 왜 자꾸 바꾸려고 하는거야?"*); and a scheduler
  transport ("versioned cluster through a queue") that contradicts the user-agreed architecture in
  `restructure-plan-4.6.md:42` and `rotor-scheduler-design.md:66-75`, where the scheduler publishes targets as
  **local variables**. All four fixed; 1.3 keeps locals but publishes one cluster local, which answers the
  2026-09-12 peer's tearing objection without overruling a user decision. **The lesson is not "review more" but
  "edit slower":** four review rounds at $4.27 + $5.64 + $6.57 found, at the end, mostly my own same-session
  inconsistencies. Round five is not scheduled; the remaining `unread-evidence` items (A4/A5/A6/A9/A10) are queued
  as reading, not as another dispatch.
- **verdict:** unverified

## Question

PRIOR-ART REVIEW (trigger: cycle-start).

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
---
type: plan
status: current
date: 2026-09-16
tags: [master-plan, pre-rig, parallelisation, seven-loop, dry-run]
---

# Master plan ??BUILD THE MAIN VI AND RUN IT, without the rig

**Rewritten 2026-09-16** after the user rejected the first version's framing, and after two peer reviews
(`archive/peer/2026-09-16-master-plan-attack.md`, `??priorart-master-plan.md`) found most of its measurement items
already done. The user's reframing is the plan:

> *"???앷컖?먮뒗 寃곌뎅??main vi 留뚮뱾?댁꽌 媛???대낫湲곕뒗 ?댁빞??(由ш렇 ?녿뒗 ?곹깭?먯꽌??媛?숈? 媛?ν븷 ??. ?꾨쭏
> bead tracking? ?덈맆?뚮땲 tracking renewal? 怨꾩냽 ?ㅼ뼱媛寃좎? [?ъ???LED ?꾩썝 爰쇰넃? ?곹깭]??洹몃젃?ㅺ퀬???좎??쇰룄
> 猷⑦봽??怨꾩냽 ?뚰뀒??紐⑦꽣 媛?? 移대찓??acquisition ???뺤긽 媛???먯껜???뺤씤 媛?ν븷??"*

And the scope it sets:

> *"?⑥? 吏꾩쭨 遺遺꾩? 猷⑦봽 蹂묐젹??諛??뺤긽 ?묐룞 ?щ?濡?蹂댁엫. 1) ?뺤긽?곸쑝濡??꾨젅??臾몄젣瑜??닿껐?섎뒗吏 2) ?뺤긽 媛??
> ?섎뒗吏 (紐⑦꽣 ?吏곸엫 諛??쎄린)."*

## What changed, and why it is better than either reviewer's version

The first plan asked *"what can we measure before the rig comes back?"* and the answer was: mostly things already
measured. The user's question is different ??*"does the parallel version actually run?"* ??and it can only be
answered by **building the thing and starting it.** This is also exactly what the outcome review demanded on
2026-09-15: *"the next problem is not missing tooling; it is failure to cross the boundary from replay proof to
experiment product."*

**Bead tracking will fail with no sample, and that is the expected condition, not a defect.** Codex attacked the
old plan's live test on precisely this ground ??blank images drive the tracker straight into bead-loss/reseed. The
user's answer settles it: yes, and the loops keep running anyway, so motor motion, motor reading, camera
acquisition and frame accounting are all observable. **The failing half is the half we already proved on the
fixture.**

?뵶 **The "free reseed stress test" was a CONTRADICTION and is withdrawn (rev4 A6).** This section claimed that with
no beads `tracking renewal` fires continuously and gives the fault injection for free ??while 짠2C, written after
the user's decision, says the reseed term is `Auto-Reset AND (min(pos) < 0)` and that **`Auto-Reset` OFF means no
reseed fires at all**. Both cannot be true of the same batch. What is true: **the no-bead condition makes reseed
available for free, but only in a batch that turns `Auto-Reset` ON.** The first batches keep it OFF on purpose, so
they test the loops *without* reseed; the stress test is the second batch, and it costs nothing extra there
because the empty stage still supplies the fault. Do not schedule the two claims into the same run.

**Bead-tracking correctness is NOT re-opened here.** The user's own recorded data (`.cal`, `.tra`, `.tiff`)
already settles it, and the fixture run confirms it numerically for the first 10,018 frames.

---

## Phase 0 ??make a run observable and repeatable  *(no LabVIEW execution)*

| # | work | detail |
|---|---|---|
| **0.1** | **Batch directory convention** ??`G:\Data\Sihyeong-Developing\<YYYY-MM-DD>-<batch>\` (the user's directory; created empty 2026-09-16 12:48). One subdirectory per batch, nothing written anywhere else | the user's instruction |
| **0.2** | **What every run records**, decided before the first run so runs are comparable: the `Buffer Number Out` trace (**including duplicates and gaps** ??see 0.3), per-loop iteration counts and periods (p50/p99), reseed events and counter, motor command + readback pairs with timestamps, VISA errors, queue depths, stop reason, and the full front-panel control snapshot | a run whose settings are not recorded is not a measurement |
| **0.3** | ?뵶 **Fix the acceptance metric before using it.** `Images Missed = 0` is **not sufficient** under `Buffer Number Mode = Last`: `Last` re-returns the same buffer when we are faster than the camera, and `Images Missed` does not count that. Both reviewers flagged it independently, and `camera-acquisition-facts.md:79-81` already says so. The authoritative trace is **`Buffer Number Out`**, from which gaps AND duplicates are derived | the old plan's criterion was wrong |
| **0.4** | ??**Camera contract ??DECIDED (see below): 90 Hz, `ExposureTime` ??5 556 쨉s (half the 11.111 ms period), `ExposureAuto` OFF**, 1280횞1024, offsets 0, never write `BinningHorizontal`. ?윞 **RESCOPED 2026-09-16 ??the tool exists (`tools/bench/camera_contract.py`) and the write works, but a Python pre-pass CANNOT set the run's condition.** Measured in three sessions: as found `ExposureAuto = Continuous` / 1909 쨉s ??written to `Off` / 5555 쨉s and read back inside the session ??**a new session reads `Continuous` / 1909 쨉s again.** `IMAQdxOpenCamera` resets exposure exactly as it resets the ROI (`camera-acquisition-facts.md`, "exposure resets on session open too"). **So the contract moves into Phase 1.1**: the acquisition loop writes `ExposureAuto = Off` and `ExposureTime` right after `IMAQdx Open Camera`, then reads both back into the batch record. `camera_contract.py` stays as the pre-flight reader and the after-the-fact verifier (`--batch <dir>` writes before/after JSON). Measured range `ExposureTime` **10 ??11053 쨉s**, so half-period is legal | the dim-field hazard is removed by the operating condition ??but only by the process that owns the session |
| **0.5** | ?뵶 **THE BLOCKER, named at last: startup DRIVES THE FORBIDDEN AXIS.** Not "contains motor initialisation paths" ??`main-vi-startup.md:33` measured it: **startup diagram 10 calls `ASI TG-1000.lvlib:Initialize.vi` (uid 43997) then `Move Axis to Position.vi` (uid 44036)**, opening COM4 (alias **`ASI_Piezo`**) and moving an axis; **the same pair recurs on diagram 88**, and diagram 12 reads the position back (uid 44196). `t0-instrumentation-plan.md:136-138` already concluded from this that running the main VI *"never runs unattended"*. So a copy of the original cannot simply be started. **Before any dry run the copy must have these three call sites disarmed** (the ASI init/move pair on diagrams 10 and 88, and the position read on 12), the disarming must be *shown* ??node-level, by uid, in the build log ??and `main-vi-startup.md:47` notes the outer startup ordering is itself a rule-1a fact, so the excision is recorded as a deliberate deviation, not a silent edit. This is also where A6's finding lands: the autofocus case fires **every 25 frames (??.6 Hz at 90 Hz)**, so the same axis is driven again throughout the run unless the control `Fix to a Certain Pattern` (uid 10230) is TRUE. **And the ASI is not the whole list** (rev4 A1, citations opened): startup diagram 1 is **PI motor init** driven from `Set Focus (0->50)`, diagram 3 is **PI `MOV`** (absolute), diagram 4 is **PI `GOH`** (go home) and diagram 5 is **`VEL` + a position query** (`main-vi-startup.md:22-28`). ?좑툘 **The rotor adds a physical hazard of its own:** the controller counter was deliberately left at **0**, so the original's Baseline-200 convention makes its **first absolute move a 200-turn trip** ??`PIC 100000` first, or run only the new VI (`rotor-sign-diagnosis.md:124-127`). Disarming is therefore a *list*, and the run's own log must show each site neutralised | rule 1b: the ASI piezo is the one instrument that can physically break the rig. A "dry run" that starts the original's startup sequence is not dry |

| **0.6** | **GPU clock lock ??the script ALREADY EXISTS; this item is "run it and verify", not "write it"** (rev4 B1: `tools/gpu/register_gpu_clock_lock.ps1` registers the logon task; `tools/gpu/regime_test.py` / `regime_test_lock.py` are the duty-cycle pstate check, rev4 B2). Register `nvidia-smi -lgc 1365,1905` with highest privileges (it resets at reboot) and verify the pstate **under the real 90 Hz duty cycle**, not in a tight loop. `-lmc` is unsupported on this RTX 2060, so upload stays ~3횞 slower than tight-loop and the 1.14 ms figure is not the number to plan against (`gpu-backend.md:225-241`) | a measured ms/frame at 90 Hz replaces the tight-loop figure before 1.2 is accepted |

## Phase A ??FINISH THE MAP FIRST  *(LabVIEW read-only + offline; the user's standing instruction)*

Nothing in phase 1 is ordered correctly without this, and hardware measurement before it measures the wrong things.

| # | work | needs |
|---|---|---|
| **A1** | **`OpOwnerChain_v0`** ??the missing link is **structure ??the diagram it sits on**, NOT node ??owner (that already works; `which_loop_owns_motor.log` prints the blocker 18 times). The recipe exists, corrected, **never run** | LabVIEW RO |
| **A2** | **Validate owner semantics per structure class** before any walk. The measured fact (`NAMES.md:864-866`) is scoped to `CaseStructure` ??1 of **6** classes (3 WhileLoop, 17 ForLoop, 37 CaseStructure, 21 FlatSequence, 4 Sequence, 2 EventStructure). FlatSequence gets a round-trip check against `diagram_tree_main.json` | A1 |
| **A3** | **Complete the 170-diagram hierarchy** ??the 41 unresolved plus every FlatSequence link, replacing position matching (the diagram was Clean-Up'd, so position means nothing) | A2 |
| **A4** | **The frame loop's TRUE membership** ??body **and nested frames**. The body-only list already exists (`frame-loop-anatomy.md:40-55`); only the nested delta is new | A3 |
| **A5** | **The unconditional per-frame path** ??what executes every iteration vs. conditionally. **This decides phase 1's loop-split order** | A4 |
| **A6** | ??**DONE 2026-09-16, offline, from dumps we already had.** The criterion is `AND( (frame index mod N) == 0 , NOT(x) )` on `CaseStructure #10407`, acting on the kernel's `Index of closest cal image slice, bead 2` against `# slices in stack`; it **does** transact serial when it fires. Full derivation and wire-level citations: `camera-acquisition-facts.md`, "MEASURED 2026-09-16 (master plan A6)". **The disarm is NAMED, 2026-09-16:** wire 3362 is the front-panel control **`Fix to a Certain Pattern`** (uid 10230), measured with `panel_wiring` ??set it TRUE and the AND is false every iteration, so the autofocus case never fires and the ASI axis is not driven *during* the run. `Auto-Focus` (uid 24266) drives a different wire and is **not** the off switch. **N is 25**, from the control **`Frame rate`** (`frame-loop-wire-graph.md:120` names the implicit link; `main-vi-panel-map.md:83` gives the value) ??so the case fires **every 25 frames ??3.6 times per second at 90 Hz**, each firing running `Move Axis Relative` plus a position read. ?좑툘 Both of these had been recorded on 2026-09-14 and were re-measured this session; wire 3362 is likewise already at `main-vi-panel-map.md:311`. **A6 required no new measurement at all** | ??complete ??it was already in our files |
| **A7** | **Every VISA/serial call site inside A4's membership** ??rule 1c's audit; this list is what phase 1 must empty out of the frame loop | A4, A6 |
| **A8** | ?좑툘 **Census A ??Case #10445 frames. RE-SCOPE BEFORE ATTEMPTING.** The obvious route is `OpCaseFrames_v0`, which **failed five times** and is CLAUDE.md's own example of breaking the "failure budget = 2" rule (`CLAUDE.md:212`), and the outcome review told us not to retry it. So: either read #10445 by a route that already works (A1's owner chain walked downward, or the existing wire-graph JSON), or **drop A8** and collapse the reseed `Or` conservatively. Do **not** rebuild the failed op | A1 |

## Phase 1 ??build the runnable seven-loop main VI on the **GPU** path, in a COPY of the original

Rule 1 unchanged: the original is never touched. The in-copy migration method is **proven end to end**
(`probe_migrate_v2` 3/3, `probe_migrate_v3` 5/5, `ExecState == 1`); untested is SCALE and RUNTIME, which is what
this phase tests.

| # | loop | acceptance at this phase |
|---|---|---|
| **1.1** | **Acquisition** ??`IMAQdx Get Image`, `Buffer Number Mode = Last`; no free slot ??skip the read, never gate the camera; carry the buffer number with the slot. **Plus the camera contract, which lives here and nowhere else** (moved from 0.4 on measurement): right after `IMAQdx Open Camera`, write `ExposureAuto = Off` and `ExposureTime ??5 556 쨉s`, then read both back into the batch record ??a session open resets them to `Continuous` / 1909 쨉s, so no external pre-pass can do it | the VI compiles and the loop iterates; **the read-back in the batch record shows `Off` / ~5 555 쨉s**, otherwise the run was not at the decided condition |
| **1.2** | **Tracking ??the GPU path** (user's decision 3): dequeue ??**GPU kernel via our own DLL interface** (single call per frame, raw image in; designed fresh, not copied from the Saleh-lab donor) ??frame-identified result. The CPU queue core's 162/162 fixture result is the **reference**, not the thing being shipped here | compiles; runs; result carries its buffer number; **x/y ??1e-6 px and z ??1e-4 쨉m against the CPU kernel on the fixture** |
| **1.3** | **Scheduler** ??cycle state machine; commands travel as **one versioned cluster through a single-owner queue**, never as four separate locals (peer-corrected 2026-09-12: non-atomic writes let the motor read a new speed with an old force) | compiles; emits a command trace |
| **1.4** | **Motor** ??reading and control out of the frame loop. **Plus the rotor repoint, which has been homeless since 2026-09-13**: the new VI's rotor calls go to `SetCommand_signed.vi` (verified in hardware, INDEX row 31), and the counter's **baseline-0** convention is adopted explicitly rather than inherited ??`rotor-sign-diagnosis.md:124-127` closes with this as "remaining (stage 2)" and no phase had picked it up | compiles; issues and reads back; a negative angle command produces a negative move, and no absolute move assumes Baseline 200 |
| **1.5** | **ASI / focus** ??**exclusively owns the VISA session**; reaches the frame path only through a non-blocking handoff (rule 1c). Gated to every N frames rather than every frame | no serial on the frame path |
| **1.6** | **Display / UI** ??10??0 Hz gate + `Defer Panel Updates`; **Image Display, not Picture ??measured, not preferred** (`INDEX.md:43, :46`: Image Display +1.0/+6.9 ms vs Picture +2.9/+8.0) | panel updates do not enter the frame budget |
| **1.7** | **File writer** ??consumes the results queue, lossless FIFO. Queue mechanics are already specified (`restructure-plan-4.6.md:65-68`: timeout ?? and the error-1122 shutdown path; `:147-167` the boundary manifest; `:161-162` latch-action controls) and the seam is checked with the existing `tools/bench/boundary_manifest.py`, not a new script | every computed result written, in order; the manifest shows no state carrier crossing the seam |
| **1.8** | **Frame accounting** ??reuse `get buff image-lost frames.vi` (uid 6810), the original's own camera-buffer bookkeeping and *"the frame source"* (`frame-loop-anatomy.md:47`), rather than writing a counter. Decide **reuse or replace in writing**: it is a subVI on the frame loop's body, so keeping it also keeps its per-call cost | the `Buffer Number Out` trace and this VI's numbers agree, or the disagreement is explained |

**Ordering inside phase 1 comes from phase A5**, not from assumption. Two of the numbers already exist: motor
reading costs **2.56 ms** (`motion-path-audit.md:84-99`) and the autofocus wrapper is **called** every iteration
but **transacts only when its case fires** ??its unconditional diagram is five nodes (two UI-thread `Value` reads),
with the fixed `Wait` and both VISA calls inside the case (`camera-acquisition-facts.md`, "the ASI wrapper's
unconditional diagram"; corrected there against the older "Wait + VISA every frame" reading of
`frame-loop-anatomy.md:68`). A6 measured **when** it fires: on a frame-index schedule, not rarely. Those are the frame
loop's known offenders ??against the **10 ms** budget at 90 Hz (the 11.111 ms period minus the ~1 ms of jitter
margin measured in `camera-acquisition-facts.md:53`; see "The budget this sets is 10 ms" below), motor reading
alone is **26 %** of it.

**??The GPU interface is ALREADY BUILT, callable from LabVIEW, and benchmarked** ??checked after the third
prior-art review flagged that the plan treated it as unknown risk (`gpu-backend.md:245-251`, INDEX rows 15/36/37).
`HARNESS_gpu2`, script-built: `IMAQ Create ??ReadFile ??GetImagePixelPtr ??one CLFN `mt2_track_simple``, DBL in/out,
**no image copies**. 200 chained frames, 5 beads:

| path | ms/frame above base |
|---|---|
| sequential (the original) | 8.15 |
| CPU-parallel v3 | 2.43 |
| GPU, Saleh-lab donor node | 5.14 |
| **GPU, our own interface** | **1.14** |

Outputs match the reference at **x,y 4.9e-7 px, z 2.9e-6 쨉m, 0 flips, 0 good-flag mismatches** ??inside the agreed
tolerance already. Everything fixed (calibration, windows, twiddles, buffers) lives on the GPU from `mt2_open`, so
per-frame traffic is one image upload, one kernel launch and 3횞nb doubles back.

**So decision 3 is cheaper than it looked**: phase 1's tracking loop wraps an interface that already exists and
already meets tolerance. But two corrections from rev3, both opened and both holding:

?뵶 **1.14 ms is a TIGHT-LOOP number, and 90 Hz is the duty cycle measured to destroy it** (`gpu-backend.md:225-241`).
Any idle gap ??2 ms drops the RTX 2060 to **P8** (SM 360 MHz, memory 405 MHz) and every phase slows **~3.5횞**; at
90 Hz the GPU is idle ~9 ms of every 11.111 ms, which is that regime exactly. The measured fix is the SM clock lock
**`nvidia-smi -lgc 1365,1905`** (admin; resets at reboot, so it is registered as a logon task) ??and even then
`-lmc` is unsupported on this card, so upload stays ~3횞 slower than tight-loop. **Phase 0 gains one item: register
the clock lock and verify the pstate under the real duty cycle. Phase 1.2 gains a timing acceptance: measured
ms/frame at 90 Hz with the lock in place, not the tight-loop figure.** Also do not `cudaHostRegister` LabVIEW's
IMAQ buffer (`gpu-backend.md:345-349`) ??relevant the moment acquisition hands pooled image refnums to this loop.

??**The stop path is already built** (`gpu-backend.md:332-343`, `tools/gpu/test_abort.py`) ??it exists precisely
because the experiment VI is normally stopped with LabVIEW's Abort button. So "unproven inside a live loop" is now
only about the *acquisition handoff*, not about stop or error handling.

?뵶 **And GPU-first changes the acceptance ladder** (rev3 A5). `restructure-plan-4.6.md:201-210` assigns
**bit-identity** to stages 0?? and a tolerance only to stage 6, on the assumption that the CPU build ships first.
With the GPU top level built first, the shipped path is a tolerance path from stage 2 onward, and bit-identity has
no replacement named. **What replaces it:** the CPU queue core stays the reference ??every GPU stage is accepted
as **x/y ??1e-6 px and z ??1e-4 쨉m against the CPU build on the same fixture frames**, and the *CPU* build, when
it follows, is still accepted bit-identically. Neither number is new; what was missing was saying which one applies
to which artefact.

## Phase 2 ??the two questions that matter  *(dry run, no rig)*

> **The specification is `restructure-plan-4.6.md:201-216`, not this section.** That file's stage list already
> carries these live-stage criteria with more content (deadline misses, buffer-number gaps, p99.9 and max of the
> acquisition-call latency, per-core CPU, UI-thread time, display age, the minutes-long back-pressure test and the
> thermal/disk soak). The two tables below are **this batch's checklist**, deliberately shorter ??when they differ,
> the restructure plan wins. Every run also records what 0.2 lists.

### 2A. Does it solve the frame problem correctly?

| check | criterion |
|---|---|
| frame accounting | every `Buffer Number Out` accounted for: continuous, or a gap that is explicitly counted. **Duplicates counted separately, not as successes** |
| the camera is never gated | acquisition rate is independent of how slow the consumer is made. Deliberately slow tracking and verify the camera's own cadence does not move |
| identity | pixels and buffer number change together; a result labelled N was computed from frame N's pixels. **The user's stated corruption test** |
| no loss from serial | the frame loop transacts no VISA (rule 1c), verified by instrumenting the boundary, not by reading the diagram |
| back-pressure | slow the writer and the disk for minutes; the acquisition side must degrade by skipping reads, never by blocking |

### 2B. Does it run normally ??motor motion and reading?

| check | criterion |
|---|---|
| motor moves | a schedule's translation commands are issued and the stage reaches the commanded positions |
| motor reads | readback matches command within the driver's tolerance; per-call cost matches the measured 2.56 ms |
| command equivalence | an existing 3-row schedule produces **identical translation commands and timings** to the original VI (restructure 짠5 stage 3) |
| rotor | absolute degrees, translation-then-rotation ordering; the counter is at **0**, not the old 100 000 baseline |
| the loops survive | run for hours with reseed firing continuously; no leak, no deadlock, no queue growth, handle count flat |

### 2C. What the no-bead condition gives free ??and the control settings it FORCES us to choose

`tracking renewal` fires continuously with no beads, so the run exercises reseed for free: reseed event counts, the
reset counter, the state fed into the next kernel call, and reseed arriving while acquisition has skipped buffers.
Codex listed these as scenarios needing deliberate fault injection; the empty stage injects them at no cost.

?뵶 **But "run for hours with reseed firing" is not achievable at default settings, and the plan said it was.**
Found by the third prior-art review and verified in the diagram census (`stage2-assembly-step-e.md:66`,
`GLOSSARY.md:48-54`): the lost-bead reseed has **three runtime controls**, not one.

| control | effect in a no-bead dry run |
|---|---|
| **`Auto-Reset`** (uid 17472) | **gates the reseed entirely** ??*"it fires only while the user has Auto-Reset on"*. OFF ??no reseed at all, and the loops simply run with garbage tracking output |
| **`Limit of Program`** (uid 9654) | the **cap on auto-resets per run**. `Equal?` against `# of Auto-Reset` ??**equality, not ??* ??and on reaching it the run **stops and saves**. With no beads every frame is a loss, so the cap is reached almost immediately and **the program terminates itself** |
| **`Reset Tracking`** (uid 5605) | manual reseed, OR'd on top |

### ??DECIDED by the user, 2026-09-16: **`Auto-Reset` OFF**

> *"?ㅽ넗由ъ뀑 ?꾧퀬 遊먯빞?좊벏."*

The dry runs turn the lost-bead reseed **off**: that term is `Auto-Reset AND (min(pos in cal image out) < 0)`
(`stage2-assembly-step-e.md:66`), so with the control off the AND is false and the *bead-loss* arm cannot fire.
Questions 2A and 2B are then read without reseed noise on top of them ??the right first experiment.

?뵶 **CORRECTED 2026-09-16 (rev3 A3, citation opened and it holds): there is a SECOND arm, and `Auto-Reset` does
not gate it.** `stage2-assembly-step-e.md:36-38` records a **periodic** auto-reset term ??`# of Auto-Reset`.Value
#9879, `Quotient & Remainder` #10068, `Equal?` #10019, Not/And ??and `:66` scopes the `Auto-Reset` control (#9806)
to *"the lost-bead reseed"* only. `GLOSSARY.md:55` gives the period from an in-VI comment: **"~27 mins/100000"**.
The 10,043-frame fixture is ??.9 minutes, which is why *"it never fired on this recording"* ??absence there is a
sampling artefact, not evidence.

So the earlier claim ??*"`# of Auto-Reset` never increments and `Limit of Program` never trips"* ??**was wrong for
a long run**, which is exactly what 2B asks for ("run for hours"). On present evidence an hours-long dry run
accumulates periodic auto-resets and can hit `Limit of Program`'s exact-equality stop-and-save on its own.

**What follows, and none of it is optional:**
1. **Record `Limit of Program`'s value in every batch** and treat a run that ends by itself as a *result*, not a
   crash ??the stop reason is already in 0.2's record list.
2. **The first long run is instrumented for it**: `# of Auto-Reset` is logged per frame, so the period is measured
   rather than taken from a comment.
3. **This is what A8 was for.** The plan offered to "drop A8" (the #10445 census) while asserting the claim that
   census would test. Either the periodic arm's gating is read from the machine, or the claim is not made.

**What this deliberately does NOT test, recorded so it is not mistaken for coverage:**

| not exercised | where it goes |
|---|---|
| the reseed path itself, reset counters, state handed to the next kernel call | a later batch with `Auto-Reset` ON and `Limit of Program` raised |
| **`Limit of Program`'s stop-and-save**, including its exact-equality trigger | a later, deliberately short batch at the normal limit ??it is reachable in seconds, so it costs nothing when we want it |
| `Reset Tracking`, the manual OR | operator-driven; test alongside the above |

### Why reseeding drops frames ???좑툘 WE DO NOT KNOW. The explanation below was built on a superseded census.

> *"?댁쟾 寃쏀뿕??reseeding???곸슜?섎㈃ ?꾨젅???쒕엻???ㅼ냼 ?앷린??寃?媛숇뜕?? ?댁쑀媛 ?덈뒗吏."*

?뵶 **RETRACTED 2026-09-16 (rev3 A4, citations opened, and it is right).** The account given here was: the reset
frame of Case #5540 holds *"one Property Node reading `Value`"* (`keystone-op-spec.md:596-600`), so a reseeding
iteration pays an extra UI-thread round trip. **Our own later census contradicts it.** CENSUS B
(`stage2-assembly-step-e.md:128-138`) measured both frames of #5540 and found **both are pure pass-throughs with
nothing computed in either**; the reseed values arrive from *outside* the loop through `FlatSequenceInnerTunnel`
2886 / 5818 ??they are *"literally the loop's INITIALISERS"* (`:140-148`). If the frame computes nothing, there is
no extra UI-thread cost on a reseed iteration, and this explanation has no mechanism left.

**So the honest answer to the user's question is: not yet known.** What survives is the *shape* of the failure if
any extra cost does appear ??the budget is 10 ms of an 11.111 ms period (`camera-acquisition-facts.md:53`) and the
failure is a cliff, not a slope (`:60-66`), so one slow iteration costs whole frames rather than a percentage.
What is missing is the cause, and it is **one measurement**: a reseed iteration's duration against a non-reseed
one, which the `Auto-Reset` ON batch produces. Do not re-state the retracted mechanism in a later document.

**The design consequence stands on its own** and was already the plan: carry the initialisers on a wire into
`ReseedMux.vi` rather than through a Property Node (`stage2-assembly-step-e.md:143-148`). It costs nothing and
changes no computation; it simply no longer needs a frame-drop story to justify it.

?좑툘 **One thing to verify in the run rather than assume.** With no beads and no reseed, `Bead is good?` stays false
for every bead. If anything downstream is gated on bead validity ??`save trace.vi` #376 writing records, the WLC
fit, the result enqueue ??those paths may sit idle, and "the file writer loop ran" would be a false positive. So
the run's record must show **what each loop actually did**, not merely that it iterated: rows written, results
enqueued and dequeued, bytes on disk. If the writer turns out to be starved, inject synthetic results rather than
turning `Auto-Reset` back on, so 2A and 2B stay clean.

## Already measured ??CITE, do not redo

Both reviews found the first plan re-proposing settled work. These are closed:

| item | where |
|---|---|
| `Last` vs `Next` on the real camera (74.9 vs 123.0 Hz) ??**measured, not calculated** | `camera-acquisition-facts.md:64-72`, INDEX row 40 |
| motor read cost **2.56 ms** | `motion-path-audit.md:84-99, :108-114` |
| camera ceiling, exposure, headroom at 150 Hz | `camera-acquisition-facts.md:35-42` |
| rotor negative-angle hardware verification (`PIC -10` ????.2째) | INDEX row 31 ??**done with the user watching** |
| `OpCaseFrames_v0` | **already failed**; do not retry (CLAUDE.md "failure budget = 2") |
| the frame loop's six body subVIs | `frame-loop-anatomy.md:40-55` |

**The autofocus question is closed** ??see A6 above; the derivation lives in `camera-acquisition-facts.md`
("MEASURED 2026-09-16 (master plan A6)") and is not repeated here.

## Genuinely deferred to reassembly

Only real experimental conditions with beads **and** the motor moving:

- bead tracking accuracy under load, and force/extension measurement;
- reseed triggered by a real bead physically coming unstuck;
- the supervised pilot the user runs to accept the whole thing.

Everything else in this plan runs dry.

## DECIDED by the user, 2026-09-16 ??the three open questions are closed

### 1. Camera: 90 Hz, exposure = half the period, fixed

> *"移대찓???몄텧? 90 Hz 議곌굔?쇰줈 ?덈컲留뚰겮? ?몄텧, ?섎㉧吏 ?덈컲? ?湲?"*

| parameter | value |
|---|---|
| frame rate | **90 Hz** ??the rig's configured condition (`imaqdx_limits.py --restore`: 1280횞1024, offsets 0, **90.0009 Hz**) |
| period | **11.111 ms** |
| `ExposureTime` | **??5 556 쨉s** ??half the period |
| idle | the remaining ??5 556 쨉s |
| `ExposureAuto` | **OFF.** Fixed exposure is the point of the decision |

**This dissolves the sharpest objection either review raised.** Codex's strongest attack was that
`ExposureAuto = Continuous` (max 15 000 쨉s, enough to cap the camera near 66 Hz) makes a dark rig change the
achievable rate, so a dry run would "measure" that the target is unreachable and blame the software. With exposure
fixed at half the period there is no auto-exposure loop to react to a dark field ??the objection is removed by the
operating condition rather than argued with. Record the frozen contract in every batch directory anyway.

**The budget this sets is 10 ms, not 11.111 ms.** Corrected after the third prior-art review: the measured table in
`camera-acquisition-facts.md:53` gives, for **90.00 Hz / 11.11 ms period**, a **budget (zero frames lost) of
10 ms**, first failing at a 12 ms delay. *"The budget is the frame period minus about 1 ms, and ~1 ms of that margin
is jitter rather than fixed cost."* Using the period as the budget ??as the first draft did ??spends a margin that
was measured to be necessary. **Dry-run acceptance is judged against 10 ms**; the 6.00 ms / 150 Hz figures in older
documents stay as the stretch condition and are not what these runs test.

Exposure does not consume this budget: the camera exposes on its own clock and the PC's 10 ms is what it has
between deliveries.

### 2. The MAP comes first ??and it was already the user's standing instruction

> *"吏???묒꽦???곗꽑?섎뒗寃?留욎쓬. ??吏?쒖???"*

The previous version of this plan argued hardware-first ("the motor window closes at reassembly"). That was wrong,
it contradicted a standing instruction, and codex had attacked it independently: starting hardware work before the
map is finished buys measurements of the wrong things. **Track A ordering is restored**: finish the diagram
hierarchy and the frame loop's true membership before hardware characterisation, and before phase 1 fixes the
split order. The hardware window is real but it is not a licence to measure blind.

### 3. The GPU top level is built FIRST and is the default

> *"tracking? 湲곕낯?곸쑝濡?GPU 湲곗??쇰줈 理쒖긽??vi ?묒꽦??寃? [?댄썑 CPU 蹂묐젹 vi??異뷀썑 ?묒꽦 ?꾩슂?섍린????"*

Phase 1 builds the seven-loop top level around the **GPU** tracking path. The CPU-parallel top level is a later,
additional deliverable ??both still ship as **two separate top-level VIs**, never one VI with a runtime switch.
This inverts how the work had been queued: `Track_v6_CPU_*` existed, so the top level was implicitly going to be
assembled around the CPU core with the GPU kernel "swapped in at stage 6". Loop 1.2 below is therefore the **GPU**
tracking loop, and its numeric acceptance is the agreed GPU tolerance (x/y ??1e-6 px, z ??1e-4 쨉m against the CPU
kernel on the recorded fixture) ??not a final-stage afterthought.

**Consequence to check early, not late:** `docs/gpu-backend.md` and `docs/gpu-portability.md` describe the GPU
path, and `memory: design-gpu-interface-fresh-not-saleh` records that our DLL interface is designed from scratch
(single call per frame, raw image in). Whether that interface is actually built and callable is now on the
critical path, where it used to be at the end.


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-16
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.

## ?좑툘 ONE SESSION AT A TIME (2026-09-16)

Two Claude sessions ran concurrently on 2026-09-16 and both edited the active documents (`CLAUDE.md` 12:05,
`cycle10-plan.md` 12:16, while another session was mid-lint at 12:14). The second session's copy of `CLAUDE.md` was
stale for its whole run ??**rule 1b had been reversed and 1c replaced underneath it**. Before starting work: check
for another live session, and **re-read `CLAUDE.md` and this file from disk** rather than trusting a summary.

## START HERE ??the first three things a new session does

1. **Read `docs/pre-rig-master-plan.md`.** That is THE plan. `docs/cycle10-plan.md` is **superseded** (its content
   is the master plan's Phase A) and contains one claim that is now known wrong ??it carries a banner saying so.
2. **The build gate is still closed, and the reviews are NOT converging** ??rev2 returned 16 findings, **rev3
   returned 18** (`archive/peer/2026-09-16-priorart-master-plan-rev3.md`, $4.27, ANSWERED). All were opened and
   **accepted**; the plan was corrected on 2026-09-16 13:3x and **rev4 dispatched**
   (`tools/bench/priorart_master_plan_rev4.log`). If rev4 still returns non-`novel` findings that are only
   "this restates a fact that lives in file X", stop re-reviewing and write `REFUTED:` lines with the citation
   opened ??one per slug ??rather than paying for a fifth review. Diagnostics, docs and peer dispatch are never
   blocked; only `py tools/recipes/*.py` is.
3. **Then Phase A1** ??run `tools/recipes/build_opownerchain_v0.py`. It is written, prior-art-corrected, and has
   never been launched.

**Do not** start hardware work before Phase A. The user's standing instruction, restated 2026-09-16:
*"吏???묒꽦???곗꽑?섎뒗寃?留욎쓬. ??吏?쒖???"*

## LabVIEW execution lock

```yaml
labview-lock:
  status: acquired
  owner: session 6564f349
  since: 2026-09-16 13:5x
  purpose: A6 remainder - resolve wire 3362 / 31234 / 3268 and Property Node #30146 with OpWireSource_v5 (read-only on MAIN, md5-checked)
```

**Verified released, not assumed:** `Get-Process LabVIEW` returns nothing ??LabVIEW is not running. The previous
block claimed `acquired` by session `2b7a154c`, which had already ended; a lock is only meaningful if it is
released when the session dies, so **check the process, not the file**. On the next start expect a fresh instance
(~31,500 handles baseline) and use a unique scratch VI name per run.

## HARDWARE ??motors PERMITTED, ASI piezo still excluded (user, 2026-09-16)

*"You eventually need to operate the motors and machines before reassembling the rig. It includes the motor
operation, reading, et cetera. I'll let you know when the rig is reassembled??Don't need to hastle around me."*

CLAUDE.md rule 1b is **reversed for this window**; the 2026-08-27 motor ban is superseded and must not be
reinstated from an old summary. Do not ask per incident. **Only the user's announcement closes the window.**
The **ASI piezo remains the one exception** ??verify it is still detached from the recorded rig state before
driving that axis (a check to run, not a question to ask).

Instruments: piezo detached 쨌 rotor free (counter **0**, not the old 100,000 baseline) 쨌 magnet motor full travel 쨌
camera on condition of restore (`tools/bench/imaqdx_limits.py --restore`: 1280횞1024, offsets 0, 90.0009 Hz; never
write `BinningHorizontal`). ?좑툘 Running the ORIGINAL VI now would make its first absolute move a 200-turn travel ??
`PIC 100000` first, or use only the new VI.

**RIG IS DISASSEMBLED**, so no bead measurement: live 150 Hz with `Images Missed` = 0, real camera jitter and buffer
gaps, and reseed on a real bead loss all still wait. Fixture work is unaffected (10,043 frames,
`archive/bench-2026-09-07-fixture/`, 13 real lost-bead frames).

## Where things stand

**Stage 1 (analysis) CLOSED.** `docs/instrument-libraries.md`, `main-vi-subvi-identity.md` (98 call sites, 0
mismatches), `main-vi-panel-map.md`, `main-vi-state.md`, `main-vi-startup.md`, `frame-loop-wire-graph.md`,
`rotor-sign-diagnosis.md`. Raw data: `archive/benchmarks/INDEX.md` rows 22??1.

**Stage 2 (assembly) IN PROGRESS**, cycles 1?? done. Plan `docs/stage2-plan.md`, steps
`docs/stage2-assembly-step-{a,a3,b,c,e}.md`.

| built | result |
|---|---|
| `Track_v6_CPU_core_v0.vi` | replay core, 69/69 PASS (INDEX row 40) |
| `Track_v6_CPU_queue_v0.vi` | producer/consumer core, 162/162 PASS (row 41) |

**Say it exactly:** both are bit-identical to the reference for the **first 10,018 frames ??those before the first
bead loss**, not all 10,043. The remainder waits on reseed. Both are **replay** artefacts: recorded TIFFs, `FOR`
loops, no live acquisition, no stop protocol.

**THE GAP, from the outcome review (2026-09-15):** 168 op VIs, 116 recipes, 217 peer exchanges produced two replay
VIs and **zero runnable experimental VIs**. Of the five functions the requirement names, none has moved into a
product. *"The next problem is not missing tooling; it is failure to cross the boundary from replay proof to
experiment product."*

## The design, as decided ??these are settled, do not re-open without the user

| question | decision |
|---|---|
| **acceptance bar** | **C** ??camera acquisition, tracking, motor reading, scheduler and data merging/saving each in **their own loop**. The frame loop (diagram 43) emptied into the seven-loop target |
| **construction method** | restructure **inside a COPY of the original** ??not a hot-path-only swap, not a fresh rebuild in an empty VI. Rule 1 unchanged: the original is never touched |
| **camera readout** | `IMAQdx Get Image`, **`Buffer Number Mode = Last`** ??newest buffer, never waits, cannot gate the camera. `Next` measured at 74.9 Hz vs `Last`'s 123.0 Hz under 8 ms of work |
| **the camera free-runs** | the PC is a **reader, never a gate**. No mechanism may throttle acquisition. No pool eviction, no `Lossy Enqueue Element`, no generation numbers |
| **time axis** | the **buffer number**, never a software timestamp. Frame N happened at N/framerate because the frame rate is hardware-controlled; skipping gives a uniform grid with holes |
| **no free slot** | simply do not read this iteration. Gap accounting = the jump in `Buffer Number Out` |
| **overload, acq ??tracking** | **lossy, latest-wins** ??discard the backlog, take the newest frame. A stale sample corrupts the time series; an explicit gap does not |
| **overload, tracking ??writer** | **lossless FIFO** ??a computed result is never dropped or reordered |
| **frame identity** | every result carries its frame number; pixels and buffer number must change together or it is corruption (user's acceptance test) |
| **no serial on the frame path** | CLAUDE.md rule 1c. The ASI/serial loop owns its VISA session exclusively and reaches the frame path only through a non-blocking handoff. A mechanism that *can* stall the frame loop is disqualified even if it usually does not |
| **fallback, authorised** | if the handoff cannot be made provably safe, acquisition and tracking stay in **one sequential loop**. Acquisition-parallel-to-tracking is NOT mandatory |

**SETTLED 2026-09-15 ??the in-copy migration method works end to end** (`probe_migrate_v2.py` 3/3,
`probe_migrate_v3.py` 5/5): create a loop inside an existing VI 쨌 drop the same subVI in it 쨌 wire a control across
the border 쨌 delete the original 쨌 **`ExecState == 1`, it compiles**. `GObject.Move` is not needed. Untested:
SCALE (75 nodes, 21 sibling couplings) and RUNTIME behaviour ??not feasibility. **No broken-VI question is open, so
`VI.Get Errors` is NOT to be built** (recorded as FAILED twice, `docs/toolkit-capabilities.md`).

## The restructure order ??measurement decides it, not assumption

| # | step | status |
|---|---|---|
| 1 | measure the **unconditional per-frame path**, p50 **and p99** | not done ??this is what cycle 10 exists to enable |
| 2 | **one vertical slice**: acquisition ??owned image handoff ??queue core ??frame-identified result, with stop, error, reseed, overload | not started |
| 3 | split whichever measured owner **dominates** | not started |
| 4 | scheduler, file writer ??completes the 7-loop target | not started |

Target architecture and per-stage numeric acceptance: `docs/restructure-plan-4.6.md` 짠3 and 짠5. **Judgement returns
at step 2, not before** ??the split order depends on step 1's numbers.

## THE PLAN ??`docs/pre-rig-master-plan.md` (user's instruction, 2026-09-16)

*"?닿? 紐낆떆?섍린 ?꾧퉴吏??rig 議곕┰ 吏곸쟾源뚯? ?????덈뒗 紐⑤뱺 ?뚮옖???꾩슂??"* Cycle 10's plan was preparation only;
the master plan replaces its **scope** and holds until the user announces reassembly. Six tracks: **A** finish the
map 쨌 **B** price the frame budget on the fixture 쨌 **C** the hardware window 쨌 **D** build the seven loops in a
copy 쨌 **E** acceptance reachable without beads 쨌 **F** the short list that genuinely waits.

**The reframing that changed the schedule:** "needs the rig" was one category and should have been three.
**Beads in a mounted channel** are unavailable; **motors/serial** and **the camera** are available *now*, and the
motor window **closes at reassembly**. So live acquisition acceptance (150 Hz, `Images Missed` = 0) needs no beads
and was deferred for no measured reason ??and **track C outranks track D wherever they compete**, because D can be
done any time and C cannot.

**REWRITTEN 2026-09-16 after both reviews landed and the user re-scoped it.** The plan is no longer "what can we
measure before the rig returns" ??it is **build the main VI and run it dry**:

> *"寃곌뎅??main vi 留뚮뱾?댁꽌 媛???대낫湲곕뒗 ?댁빞??(由ш렇 ?녿뒗 ?곹깭?먯꽌??媛?숈? 媛?ν븷 ????bead tracking?
> ?덈맆?뚮땲 tracking renewal? 怨꾩냽 ?ㅼ뼱媛寃좎???洹몃젃?ㅺ퀬???좎??쇰룄 猷⑦봽??怨꾩냽 ?뚰뀒??紐⑦꽣 媛?? 移대찓??
> acquisition ???뺤긽 媛???먯껜???뺤씤 媛?ν븷??"*

Two questions decide it: **(1) does it solve the frame problem correctly, (2) does it run normally ??motor motion
and reading.** Bead tracking failing with no sample is the **expected condition, not a defect** ??and it makes the
run a free, continuous reseed stress test. Bead-tracking correctness is already settled by the user's recorded
`.cal`/`.tra`/`.tiff` data and the fixture. Batches go to **`G:\Data\Sihyeong-Developing\<date>-<batch>\`**.

**Three decisions, user, 2026-09-16:**

| | decision |
|---|---|
| **camera** | **90 Hz; exposure ??5 556 쨉s = half the 11.111 ms period; `ExposureAuto` OFF.** This dissolves codex's sharpest objection (auto-exposure in a dark field caps the camera near 66 Hz) by the operating condition rather than by argument. **The dry-run frame budget is 10 ms** ??the measured table gives 10 ms at 90 Hz, i.e. the period minus ~1 ms of jitter margin (`camera-acquisition-facts.md:53`); using the period itself spends a margin measured to be necessary. ?좑툘 **No tool sets exposure yet** ??`imaqdx_limits.py` writes ROI only |
| **GPU, already in hand** | our own interface is **built, callable via one CLFN, and measured at 1.14 ms/frame**, outputs at x,y 4.9e-7 px / z 2.9e-6 쨉m / 0 flips ??inside the agreed tolerance (`gpu-backend.md:245-251`). Decision 3 is far cheaper than it looked; what is unproven is the interface inside a live loop with stop and error handling, not the numerics |
| **order** | **the MAP comes first** ??*"??吏?쒖???"* The rewrite had argued hardware-first because the motor window closes; that contradicted a standing instruction and codex attacked it independently. Phase A is restored ahead of building |
| **backend** | **the GPU top level is built FIRST and is the default**; the CPU-parallel top level follows. Both still ship as two separate VIs. The GPU DLL interface moves onto the critical path from "stage 6" |
| **dry-run reseed** | **`Auto-Reset` OFF.** The reseed term is `Auto-Reset AND (min(pos) < 0)`, so with it off nothing auto-resets, **`# of Auto-Reset` never increments and `Limit of Program` never trips** ??the run does not self-terminate and 2A/2B are read without reseed noise. Reseed behaviour and the stop-and-save path become **separate, later batches**. ?좑툘 Verify what each loop actually DID (rows written, results enqueued), not that it iterated: with `Bead is good?` false everywhere, a bead-gated writer could sit idle and look like a pass |

## Cycle 10's plan is SUPERSEDED ??its content lives on as the master plan's Phase A

`docs/cycle10-plan.md` went to the prior-art review, which returned **8 non-`novel` verdicts**
(`archive/peer/2026-09-16-priorart-prior-art.md`, opus/high, $3.47, ANSWERED). **All eight were accepted** ??every
citation was opened and held ??and the plan was rewritten rather than released. Central finding: the plan cited
`docs/NAMES.md:823` for owner-chain semantics, but the fact lives at **:864-866 under the heading "Owner chain
inside a case frame"** and is scoped to `CaseStructure`, one of the main VI's **six** structure classes.
`tools/bench/which_loop_owns_motor.log` names the real blocker 18 times: *"cannot step above this structure without
the structure?뭜ome-diagram link"* ??the **opposite direction** from what the reader was specified to provide.

What survives, after H4 was deleted (already run in hardware) and H2 replaced (ASI focus is operator-driven, so it
cannot be measured in a quiet period): **run the recipe that already exists 쨌 validate owner semantics per
structure class 쨌 re-walk the 41 unresolved diagrams 쨌 re-run the motor-site script 쨌 derive the unconditional
per-frame path 쨌 the nested-frame membership delta 쨌 one scoped ASI latency tail.** Mostly offline, and it exists
to produce the ONE number the restructure order depends on.

**Two gates are closed right now:**
1. `guard_cycle` blocks every recipe build while the newest prior-art review has unrefuted verdicts. Nothing was
   refuted, so the release is a **fresh prior-art review of the revised plan** ??not a `REFUTED:` line.
2. `guard_cycle` *also* blocks on its cycle clock ??see OPEN item 1; that one is a defect, not a real obligation.

## OPEN

1. ?윟 **Autofocus decision path ??CLOSED except for one number (A6, 2026-09-16).** It is **periodic and
   code-driven**, in the MAIN VI: `CaseStructure #10407` on diagram 43 fires on
   `AND( (frame counter mod N) == 0 , NOT(Fix to a Certain Pattern) )`, acts on the kernel's
   `Index of closest cal image slice, bead 2` against `# slices in stack`, and **does** transact serial when it
   fires (`ASI TG-1000.lvlib:Move Axis Relative.vi`). **The disarm is a front-panel control: `Fix to a Certain
   Pattern` (uid 10230) TRUE ??autofocus never fires** ??measured by `panel_wiring`, not inferred. Derivation:
   `docs/camera-acquisition-facts.md` (A6 block). **Still unnamed:** the control behind Property Node `#30146`
   (the interval N) ??property-node reads are invisible to `panel_wiring`, so it needs another route.
   ?좑툘 Two things this does NOT cover: `Auto-Focus` (uid 24266) drives a *different* wire, so it is not the off
   switch; and the **startup** sequence drives the same ASI axis before any loop runs ??see OPEN 5.
2. ??**CLOSED 2026-09-16 13:2x ??`docs/restructure-plan-4.6.md` 짠4 and 짠5 corrected.** 짠4 carries a banner: the
   construction method is **restructure inside a COPY of the original**, not "build the top level fresh"; the
   probe_migrate evidence is cited and the 66-terminal/Clean-Up reasoning below it still holds. 짠5 carries a banner
   fixing three criteria: bit-identical means the **first 10,018 frames**; **`Images Missed` = 0 is not sufficient**
   under `Buffer Number Mode = Last` (use the `Buffer Number Out` trace); **90 Hz / 10 ms is the tested condition**,
   150 Hz / 6.00 ms is the stretch one. Stage rows 2 and 5 rewritten accordingly. Same pass fixed
   `pre-rig-master-plan.md:90` ("11.111 ms budget" ??the 10 ms budget, motor read = 26 % of it).
3. **19 archived reviews lack frontmatter and annotation** (audit A4). The bulk `frontmatter.py` pass is now safe to
   run ??`guard_cycle` no longer picks the newest retrospective by raw mtime ??but the annotations are judgement
   work, not a formatting pass.
4. `Global motor pos.vi` ??write-only here; **user: a readability container covering all motors, keep it** (not
   blocking).
5. ?뵶 **STARTUP DRIVES THE FORBIDDEN ASI AXIS ??the dry run cannot simply be started.** `main-vi-startup.md:33`:
   startup diagram 10 calls `ASI TG-1000.lvlib:Initialize.vi` (uid 43997) then `Move Axis to Position.vi` (44036),
   opening COM4 (alias `ASI_Piezo`) and moving an axis; **the pair recurs on diagram 88**, and diagram 12 reads the
   position back (44196). `t0-instrumentation-plan.md:136-138` had already concluded from this that the main VI
   *"never runs unattended"* ??and two prior-art reviews raised it before this one was acted on. Master plan 0.5
   now names the three call sites; the copy must have them disarmed, node-by-node and shown in the build log,
   before any run. Rule 1a: the startup ordering is itself a fact, so the excision is a recorded deviation.
6. ??**CLOSED ??N = `Frame rate` = 25.** The autofocus case fires **every 25 frames ??3.6 Hz at 90 Hz**, each
   firing issuing an ASI relative move plus a position read. That makes the ASI serial path a steady obligation
   inside the frame loop, not an occasional branch ??the strongest argument yet for rule 1c's dedicated ASI loop.
   Both this and wire 3362 were **already recorded on 2026-09-14** (`frame-loop-wire-graph.md:120`,
   `main-vi-panel-map.md:83, :311`) and were re-measured this session before rev4 pointed at them.

**CLOSED 2026-09-16, on the user's instruction:** the cycle gate's clock now measures the **span of unreviewed
build logs** instead of time elapsed since the last retrospective (it used to refuse the first build of any cycle
starting more than 8 h after a review ??it fired hardest when the least work had been done); and both the
retrospective and prior-art pickers use `min(ctime, mtime)`, so a bulk frontmatter pass can no longer reorder them
or silently open the gate.

**?좑툘 ALSO FIXED, and it had never worked: the PRIOR-ART STOP GATE.** Its pattern required the verdict slug to end
the line, while `prior_art_review.py`'s own prompt demands a file-and-line citation on every finding ??so real
verdicts (`PRIOR-ART: contradicted   (A3a ??NAMES.md:823 ??`) matched **nothing**. Eight unrefuted verdicts parsed
as zero. The review the user gave stopping power to was inert from the day it was built, and builds had been
blocked only by the unrelated clock bug ??by accident. Now: citation allowed after the slug, and only the `## Answer`
section is scanned so the archived question's own menu line cannot be read as findings.

**ANSWERED, kept because they were expensive:** `Limit of Program` = the **cap on auto-resets per run**; at the
limit the program **stops and saves** (`Equal?`, so on equality). The racy `min value` read ??**use the current
frame** (rule 1a deviation, accepted with the user's word). Rotor read sign ??`SetCommand_signed.vi`, verified in
hardware 2026-09-13 (INDEX row 31).

## Where to look

`CLAUDE.md` rules 쨌 `docs/NAMES.md` verified strings 쨌 `docs/toolkit-capabilities.md` API 쨌
`docs/restructure-plan-4.6.md` target + stages 쨌 `docs/cycle10-plan.md` current cycle 쨌
`archive/2026-09-16-status-cycles-8-10-narrative.md` the reasoning behind everything above 쨌
`archive/` history (rule 4: not read in normal work).


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

**Not prior-art-free: 13 findings, zero `novel`.** Nine of them are our own files contradicting each other or being left unread; four are repeats from rev3/rev4 that were never refuted and never fixed. Credit first: rev4's A1 (PI/rotor startup list), A2/A4 (N = 25, wire 3362), B1/B2 (clock-lock script, `regime_test`) and the reseed-mechanism retraction are all properly discharged in this revision.

⚠️ Method note: `docs/pre-rig-master-plan.md`, `STATUS.md` and `CLAUDE.md` all changed under me mid-review (0.5 was rewritten from "🔴 THE BLOCKER" to "🟢 NOT A BLOCKER"; CLAUDE.md rule 1b now retires the ASI carve-out entirely). **All line citations below are against the files as they stand on disk now**, not against the packet I was handed. I checked before writing: the "ASI is still the one exception" objection I would otherwise have raised is dead — `CLAUDE.md:52-54` and `STATUS.md:63-66` retire it explicitly, and I am not raising it.

---

# PART A — THE DIRECTION

## A1 `contradicted` — 0.5 gives the opposite instruction to itself, in one cell

`pre-rig-master-plan.md:58` opens *"🟢 **NOT A BLOCKER WHILE THE RIG IS APART** … the dry run may execute the original's startup **as it is**"* and closes *"Disarming becomes mandatory at assembly, not now"*. Between those two sentences, unedited from the previous revision: *"So a copy of the original cannot simply be started. **Before any dry run the copy must have these three call sites disarmed** … the disarming must be *shown* — node-level, by uid, in the build log"*.

Same cell, three sentences apart. A builder cannot tell whether node-level excision of uids 43997 / 44036 / 44196 is Phase 0 work or not, and this is expensive work under rule 1a (the excision is to be *recorded as a deliberate deviation*). Decide in writing which half survives.

## A2 `contradicted` — rev4's A6 was accepted and then only half-applied; the withdrawn claim is still load-bearing in two places

- Withdrawn at `pre-rig-master-plan.md:37-43`: *"The 'free reseed stress test' was a CONTRADICTION and is withdrawn … the stress test is the second batch."*
- Still asserted at `pre-rig-master-plan.md:170` (2B acceptance): *"run for hours **with reseed firing continuously**"*; and `:174-176` (2C): *"the run exercises reseed for free: reseed event counts, the reset counter, the state fed into the next kernel call"*.
- Directly against `:219`, which assigns exactly those items — *"the reseed path itself, reset counters, state handed to the next kernel call"* — to *"a later batch with `Auto-Reset` ON"*.
- And `STATUS.md:156` still reads *"it makes the run a free, continuous reseed stress test"* — the propagation rev4 named at its A6, whose recommended fix was "delete the sentence from the plan **and STATUS**". Only the plan half was done.

2B's row is an *acceptance criterion*. As written, the first batch cannot pass it, because the decision at `:188-194` guarantees reseed will not fire.

## A3 `contradicted` — STATUS says N is still unnamed 24 lines after saying N is 25

- `STATUS.md:198-199` (OPEN 1): *"**Still unnamed:** the control behind Property Node `#30146` (the interval N) — property-node reads are invisible to `panel_wiring`, so it needs another route."*
- `STATUS.md:223` (OPEN 6): *"✅ **CLOSED — N = `Frame rate` = 25.**"*

`docs/camera-acquisition-facts.md:269-282` settles it ("this was on disk all along"), and `pre-rig-master-plan.md:73` uses 25. STATUS is the file a cold session reads first, and OPEN 1 as written orders a LabVIEW read — the very lock the lock block at `STATUS.md:33-35` is still held for. Delete OPEN 1's "still unnamed" paragraph.

## A4 `unread-evidence` — `docs/frame-ownership-design.md` is the design for loops 1.1/1.2/1.7 and the plan never cites it

The plan's 1.1 says *"no free slot ⇒ skip the read … carry the buffer number with the slot"* (`:85`) and 1.7 cites `restructure-plan-4.6.md:65-68` for queue mechanics. The document that decides slot semantics is cited nowhere:

- `frame-ownership-design.md:23-39` — G4, why the pre-allocated pool + slot index wins, pool sizing (start at 20, "any growth is a symptom, not a fix");
- `:41-64` — G7, the FREE → FILLING → OWNED lifecycle and four invariants, including *"**Every exit path returns the slot exactly once** — normal completion, kernel error, enqueue timeout, shutdown, file-writer error"* and *"two queues, not one"*;
- `:60` — *"A GPU raw pixel pointer must not outlive slot ownership … This is the exact shape of the bug that cost the GPU v2 work a day"* — which is loop 1.2 on the GPU path, i.e. exactly what this plan builds first;
- `:92-97` — Abort bypasses diagram cleanup entirely, with the concrete list of what the next start must clean (stale named queues, undisposed IMAQ images, open camera session, partial file refnums, VISA sessions, an outstanding GPU DLL call);
- `:99-101` — single ownership, named, for camera session / VISA / motor / file refnums / queues / pool / GPU context.

2A (`:154-160`) has no slot-invariant or leak check, and Phase 1 has no shutdown item, though `:132-134` already relies on Abort being the normal stop.

## A5 `unread-evidence` — 0.2's record list re-derives a peer-reviewed instrumentation spec that is already adopted, and drops half of it

`docs/stage2-plan.md:83-88`, item 6 *"Live instrumentation (minimum)"*, adopted from `archive/peer/2026-09-14-stage2-construction-plan.md`: requested/returned buffer numbers, gap count/size, overwrite/error count, acquisition-call duration count/**p99.9/max**, acquisition→dequeue and acquisition→kernel-done latency p99.9/max, `Q_img` **high-water mark**, enqueue timeouts, dropped frames, longest full interval, acquired/copied/enqueued/dequeued/processed/returned counts, **slot-invariant violations**, `Q_res` high-water mark — *"Acceptance = zero gaps, zero drops, zero slot violations, processed = acquired; the slowed-tracker test shows counted drops with acquisition still at 150 Hz."*

`pre-rig-master-plan.md:55` lists a shorter, differently-shaped set (p50/p99, "queue depths") and silently loses the slot-invariant counters, the high-water marks and the pipeline counts. 2A's *"the camera is never gated"* row (`:157`) is that file's slowed-tracker test under another name. Also uncited: `stage2-plan.md:64-67`, where `Q_free` is the pool authority and the asserted invariant is `free + queued + processing = 8`.

## A6 `unread-evidence` — Phase A audits VISA and drops the UI thread, which our own files call the leading explanation

`docs/motion-path-audit.md:124-126`: *"The leading explanation for 'one loop carries too much' is now **UI-thread serialization**, not CPU work. It is testable without hardware and without restructuring anything: count how many property-node `Value` accesses sit on the per-frame path, and whether any of them are in the same loop as the display."* Its ordering at `:128-133` is: step 0 → **then the UI-thread question** → then per-VI cost. The supporting counts: `:38` (19 front-panel property-node `Value` accesses in the lab code), `:53-56` (*"the loops were separated, but they meet again in the UI thread"*), `camera-acquisition-facts.md:343-347` (two unconditional UI-thread `Value` reads every frame inside the ASI wrapper), and `restructure-plan-4.6.md:34`, which still carries this as an open gate: *"frame loop's unconditional non-kernel cost | two `Value` property nodes = two UI-thread round trips | **not yet sized — gate G1**"*.

Phase A's audit item A7 (`:74`) is scoped to *"Every VISA/serial call site"*. A5 (`:72`) is supposed to decide the split order, and `:100-102` names only motor read and autofocus as "the frame loop's known offenders". Two further things in the same neglected file: `t0-instrumentation-plan.md:65-70` step 0b, the **reentrancy audit** — *"A non-reentrant subVI shared between loops becomes an accidental mutex … read `Execution:Reentrancy Type` (VI property 288) … **This is the highest-value check in the whole plan**"* — which is the one check that decides whether seven loops actually run in parallel, and `:26-39`, which already specifies A4/A5's method and names its deliverable `docs/per-frame-path.md`.

## A7 `contradicted` — the scheduler's transport: two current documents still prescribe the mechanism 1.3 forbids

- `pre-rig-master-plan.md:87` — *"one versioned cluster through a single-owner queue, **never as four separate locals**"*.
- `restructure-plan-4.6.md:42`, the target-architecture table row 3 — *"Scheduler | cycle state machine; **publishes targets (speed, force, wait, rotor °) as local variables**"* — contradicted 14 lines later by its own `:56` and `:59-62`.
- `docs/rotor-scheduler-design.md:66-67`, status `current`, dated **2026-09-14** (two days *after* the 2026-09-12 peer correction) — *"publish targets (speed, force, wait, ROTOR deg) **as local variables**"*, defended at `:75`: *"Local variables carry the targets, which neither serialise the loops … nor enter the UI thread."*

Whoever builds loop 3 will open one of those two tables. Both need the banner, or 1.3 needs to justify itself against them.

## A8 `contradicted` — the rotor repoint in 1.4 is the thing the user told us not to do, and the source file says so on both sides

`pre-rig-master-plan.md:88` makes it a Phase 1 build item: *"the new VI's rotor calls go to `SetCommand_signed.vi` … and the counter's **baseline-0** convention is adopted explicitly"*, citing `rotor-sign-diagnosis.md:124-127`.

Against:
- `rotor-sign-diagnosis.md:145-147` — *"**It is also not required for the restructuring.** The scheduler's rotor row calls `SetCommand.vi` exactly as the existing `Send to Rot` path does, with the same `Baseline Startpoint` source … per the user's own instruction: 'configuration은 그대로 쓰면 되는데 왜 자꾸 바꾸려고 하는거야?'"* — i.e. the same file contradicts its own `:127`.
- `docs/rotor-scheduler-design.md:143-148` (current, and the newer document) repeats it as a live constraint: *"The schedule's rotor row must call `SetCommand.vi` **exactly as the existing `Send to Rot` path does** — same `Baseline Startpoint` source, same `Ring`, same everything … Copying the working call makes the new path correct by construction … **which rule 1a requires regardless**."*
- `rotor-sign-diagnosis.md:138-139` names the cost: *"**It changes behaviour.** Every stored schedule and every habit of the operator is expressed in the current coordinate. Changing the baseline meaning silently re-interprets them."*

And 1.4's own acceptance is in tension with 2B: `:169` requires *"no absolute move assumes Baseline 200"* while `:168` requires *"**identical** translation commands and timings to the original VI"*.

## A9 `unread-evidence` (repeat of rev4 A5 — raised, unrefuted, not addressed) — the camera contract is written on a diagram the plan still does not name

`:57` and `:85` put the exposure write *"right after `IMAQdx Open Camera`"* and call that the acquisition loop. In a copy of the original, `IMAQdx Open Camera` is in the **startup frame**: `stage2-plan.md:17` — *"Camera session opened in the startup frames (**diagram 87**: `IMAQdx Open Camera` → `Configure Grab`)"*. That same frame holds the unresolved node: `camera-acquisition-facts.md:465` (uid 9775, terminals `Height`, `Width`), `:511-515` — *"**Still open, and it is the whole question: is uid 9775 reading or writing?** … a *write* means the VI sets it and the value on the wire is the answer"*, `:421-434` the 640×512 observation with four hypotheses falsified, `:436-438` the panel indicators holding 640/512 from the last real run. Same record at `archive/benchmarks/INDEX.md:40`.

If 9775 writes, the dry run's frame size is set by the copy and every Phase 2 budget number is against the wrong geometry. Nothing in Phase A schedules this; `tools/bench/read_diagram87.py` is named at `:513` as the reader that settles it.

## A10 `unread-evidence` (repeat of rev4 A7 — raised, unrefuted, not addressed) — how a bead-free run gets *initialised* is still unwritten

`archive/peer/2026-09-16-master-plan-attack.md:73` — *"The tracking loop requires **valid initial bead coordinates, calibration clusters, good flags, and reseed state**"*. The plan answers only the tracking-fails half (`:31-35`). The inputs are known: `stage2-plan.md:21-23` (`Array of cal clusters`, `Real-space cosine window`, `Cosine bandpass for Hilbert`), built at startup per `main-vi-startup.md:29-30` from `cal image array`; and the gate `Done Picking \nBeads?` is a wired control, uid 11819, at `main-vi-panel-map.md:359`. Which `.cal` a batch loads and what satisfies the picking gate decides whether the loops reach steady state at all — and `:303-308`'s false-positive warning covers only the writer.

---

# PART B — THE ARTIFACTS

## B1 `refuted-already` — 1.3's versioned cluster was decided against for v0, the cause has not been removed, and the shipped core proves it

`stage2-plan.md:96-103`, *"**No composite queue elements in stage-2 v0 (decided 22:1x).** `Create Bundle by Name` needs a typed cluster terminal, and `Create Build Array` needs all its inputs as terminals of ONE node — neither exists without a donor. Instead each direction uses **two lock-stepped queues from the same producer in the same iteration**."* The core that passed 162/162 is built that way: `stage2-assembly-step-c.md:21-26` — six queues, `Q_img` / `Q_meta` / `Q_res` / `Q_good` / `Q_pos` / `Q_rmeta`, enqueued and dequeued in pairs. And `docs/toolkit-capabilities.md:32` lists the queue family with no Bundle/Unbundle writer; `:46-49` adds readers only.

So 1.3's acceptance as written is not buildable by the present fleet. Either the donor-cluster gap is closed first and that is named as build work, or 1.3 says lock-stepped queues and restates its atomicity argument — because two lock-stepped queues are *not* the atomic cluster that answers the 2026-09-12 correction (`restructure-plan-4.6.md:59-63`).

## B2 `helper-exists` — the stop protocol has a wiring primitive and a recorded trap, and Phase 1 has no stop item

`STATUS.md:91-93` — both existing artefacts are *"replay artefacts: recorded TIFFs, `FOR` loops, no live acquisition, **no stop protocol**"*. The rule and the tool both exist: `stage2-plan.md:90-94` — *"**Stop conditions are evaluated INSIDE the loop.** A front-panel Boolean's terminal wired into a While loop from the top level becomes an input tunnel read once before the loop runs (NI: the infinite-loop mistake) … `OpExitWhile_v0`'s by-name `Stop Condition` is the wiring primitive"*, and `toolkit-capabilities.md:31` gives the call: `exit_while(target, stop_control, body_diagram, node_index, output_names, node_class)`, verified 5/5, ExecState 0 → 1. Seven loops need seven stops and a shutdown order (`frame-ownership-design.md:68-72`: stop the users → drain → release, error 1122 otherwise). None of 1.1–1.8 mentions it.

## B3 `already-measured` — third time unchanged (rev3 B1 → rev4 B3 → here): 1.2's tolerance still carries no frame count and no machine caveat

`:86` reads *"x/y ≤ 1e-6 px and z ≈ 1e-4 µm against the CPU kernel **on the fixture**"*. The fixture is 10,043 frames; the numbers quoted at `:116` come from `archive/benchmarks/INDEX.md:36` (row 15) — **200 chained frames, 5 beads**. And `INDEX.md:41` (row 20) carries the constraint that must travel with the tolerance: *"**the 1e-6 px acceptance is a property of a MACHINE, not of this DLL** — cuFFT guarantees bitwise reproducibility only for a fixed GPU model, so it must be re-run on any new box (`N=200 py tools/gpu/test_mt2.py`)"*. Two reviews have now asked for one sentence naming the frame set and the box; it costs a line.

---

## Where I found no prior art

Loops 1.5, 1.6, 1.8 as artefacts; 0.1's batch directory; 0.6 as rescoped ("run it and verify"); A2/A3 as scoped; the frame-identity corruption test; and the user's four decisions (90 Hz · map-first · GPU-first · `Auto-Reset` OFF), which are theirs to make.

```
PRIOR-ART: contradicted      (A1 — pre-rig-master-plan.md:58 "NOT A BLOCKER"/"disarming mandatory at assembly, not now" vs the same line's "cannot simply be started … must have these three call sites disarmed … node-level, by uid")
PRIOR-ART: contradicted      (A2 — withdrawal at pre-rig-master-plan.md:37-43 vs surviving :170, :174-176; both refuted by :219; STATUS.md:156 still carries "free, continuous reseed stress test")
PRIOR-ART: contradicted      (A3 — STATUS.md:198-199 "Still unnamed … #30146" vs STATUS.md:223 "CLOSED — N = Frame rate = 25"; camera-acquisition-facts.md:269-282)
PRIOR-ART: unread-evidence   (A4 — frame-ownership-design.md:23-39, :41-64, :60, :92-97, :99-101 never cited by 1.1/1.2/1.7 or 2A)
PRIOR-ART: unread-evidence   (A5 — stage2-plan.md:83-88 adopted live-instrumentation minimum + acceptance, and :64-67 the Q_free invariant, vs pre-rig-master-plan.md:55 and :157)
PRIOR-ART: unread-evidence   (A6 — motion-path-audit.md:124-126, :128-133, :38, :53-56; t0-instrumentation-plan.md:65-70 reentrancy audit, :26-39; restructure-plan-4.6.md:34 gate G1 — Phase A7 audits VISA only)
PRIOR-ART: contradicted      (A7 — pre-rig-master-plan.md:87 vs restructure-plan-4.6.md:42 and rotor-scheduler-design.md:66-67, :75)
PRIOR-ART: contradicted      (A8 — pre-rig-master-plan.md:88 vs rotor-sign-diagnosis.md:145-147 and :138-139, and rotor-scheduler-design.md:143-148; internal split at rotor-sign-diagnosis.md:127)
PRIOR-ART: unread-evidence   (A9 — stage2-plan.md:17 diagram 87 is the startup frame; camera-acquisition-facts.md:465, :511-515, :421-434, :436-438; INDEX.md:40 — repeat of rev4 A5)
PRIOR-ART: unread-evidence   (A10 — master-plan-attack.md:73; stage2-plan.md:21-23; main-vi-startup.md:29-30; main-vi-panel-map.md:359 — repeat of rev4 A7)
PRIOR-ART: refuted-already   (B1 — stage2-plan.md:96-103 decided against composite queue elements; stage2-assembly-step-c.md:21-26 six lock-stepped queues; toolkit-capabilities.md:32 has no Bundle writer)
PRIOR-ART: helper-exists     (B2 — stage2-plan.md:90-94 stop-inside-loop rule; toolkit-capabilities.md:31 exit_while/OpExitWhile_v0; frame-ownership-design.md:68-72 shutdown order; STATUS.md:91-93)
PRIOR-ART: already-measured  (B3 — INDEX.md:36 row 15 = 200 chained frames / 5 beads; INDEX.md:41 row 20 machine caveat — unchanged since rev3 B1)
```

**Cheapest way to act, if the citations hold when opened:** (1) resolve A1 by deleting one half of 0.5 — one sentence either way; (2) delete the three surviving "reseed stress test" sentences (plan `:170`, `:174-176`, STATUS `:156`) and OPEN 1's "still unnamed" paragraph — four edits, no LabVIEW, and one of them releases the lock; (3) add `frame-ownership-design.md` and `stage2-plan.md` item 6/7 to Phase 1's cell text instead of re-deriving them; (4) put the UI-thread property-node census beside A7 — it is offline and `node_labels` already produced the data (`main_vi_node_labels.json`, 88 implicit nodes with READ/WRITE direction, `INDEX.md:48`); (5) decide 1.3 as lock-stepped queues or name the donor-cluster build; (6) add diagram 87 / uid 9775 to Phase A before the camera contract is called frozen; (7) settle A8 with the user, because it is a rule-1a computation question, not a scheduling one.

I took no lock, opened no `.vi`, built nothing and ran nothing.

## Sources

(extract from answer)

## What was done with it

**2026-09-16, later session. All 13 findings were opened and every one of them was ACCEPTED — none was argued
with.** Six had already been discharged by edits made earlier the same day; seven were still live and were fixed
here. The `REFUTED:` lines below are the gate's release form (`tools/hooks/guard_cycle.py:190`), and they must be
read for what they say: **not "the reviewer was wrong" but "the text the reviewer cited is no longer on disk."**
That is the only sense in which the citation "does not cover this case" — it does not cover it because the case
was changed to match the review.

⚠️ **A hole in the gate, recorded for whoever tunes it next.** `guard_cycle.py` prints *"If the review is right,
change the plan instead"* — but changing the plan does not open the gate; only a `REFUTED:` line does. So a session
that does exactly what the gate advises is still blocked, and its only exit is a line whose verb is wrong. Either
the gate needs a second release form (`FIXED: <slug> — <file>:<line> now reads X`) verified by re-reading the cited
file, or the message should stop advising a route it does not accept. Not changed today: the gate is the user's
design and a build is waiting behind it.

### Edits that discharge each finding

| finding | what was done | where |
|---|---|---|
| A1 | already fixed before this session: 0.5 now says **record now, excise at assembly**; the "must be disarmed before any dry run" sentence is gone | `pre-rig-master-plan.md:58` |
| A2 | already fixed: 2B's row now reads *'**Not "with reseed firing continuously"**'* and 2C carries the `Auto-Reset` ON caveat. **The STATUS half is gone by deletion** — STATUS.md is now 117 lines; `:156` does not exist and `grep` finds no "free, continuous reseed" anywhere in it | plan `:170`, `:174-178`; `STATUS.md` |
| A3 | **both cited lines no longer exist.** STATUS.md was compacted under CLAUDE.md rule 4's 100-line threshold; `grep -n "Still unnamed\|30146\|N = "` returns nothing | `STATUS.md` (117 lines) |
| A4 | 1.1 now carries the **G7 lifecycle** — FREE/FILLING/OWNED, two queues not one, *"every exit path returns the slot exactly once"*, and `:60`'s GPU-pointer-lifetime constraint on 1.2. **2A gained two rows it did not have**: slot invariants (`free + queued + processing = pool`, violations = 0) and no-leak (high-water marks, handle count, `acquired = … = returned`) | plan 1.1, 2A |
| A5 | already fixed: 0.2 cites `stage2-plan.md:83-88` and reproduces the adopted list with its acceptance | plan `:55` |
| A6 | already fixed: A7 is **three** audits — VISA, **reentrancy** (VI property 288, with `ASI_adjust focus-subvi.vi` named), UI-thread census | plan A7 |
| A7 | fixed **twice**. The first fix released the peer correction by citing `rotor-scheduler-design.md:75` as a user decision; that line was opened and it is **the document's own reasoning** — `:72-73` is the user's point (motor loop parallel to acquisition). Attribution corrected, and the banner added to **both** cited documents so neither contradicts itself | plan 1.3; `restructure-plan-4.6.md:42`; `rotor-scheduler-design.md:74-75` |
| A8 | already fixed (1.4 withdrawn). The residual `:168` vs `:169` tension is **answered rather than edited away**: `:168`'s subject is the **translation** axis, `:169`'s is the **rotor** — different controllers, no conflict; said so in the row | plan 2B |
| A9 | **scheduled as Phase A9**, with the reader named (`tools/bench/read_diagram87.py`) and the 1.5 h Terminal-sweep trap recorded. 1.1 now says the contract write lands on **diagram 87**, not the acquisition loop's diagram | plan A9, 1.1 |
| A10 | **scheduled as Phase A10** — which `.cal` a batch loads, and what satisfies `Done Picking \nBeads?` (uid 11819) with no beads; named as a *precondition* of Phase 2 | plan A10 |
| B1 | accepted in full: "one cluster local" had the **same** donor problem as a cluster queue element. 1.3 now states the invariant as the requirement and names the two buildable routes (lock-stepped set, or a donor typedef as explicit build work) | plan 1.3 |
| B2 | **new row 1.9 — stop and shutdown**, the item Phase 1 had none of: stop inside each loop via `OpExitWhile_v0`, finite enqueue timeouts, error 1122, stop → drain → release, and the Abort-bypass cleanup list | plan 1.9 |
| B3 | the tolerance now travels with its two properties: **200 chained frames / 5 beads** (`INDEX.md:36`) and **the machine caveat** (`INDEX.md:41`, re-run `N=200 py tools/gpu/test_mt2.py` on any new box) | plan 1.2 |

REFUTED: contradicted — A1/A2/A3/A7/A8. Each cited string was opened and **four of the five are no longer on disk**: `pre-rig-master-plan.md:58` no longer contains "Before any dry run the copy must have these three call sites disarmed"; `:170` now reads 'Not "with reseed firing continuously"'; `STATUS.md:156` and `:198-199`/`:223` do not exist at all (the file is 117 lines after the rule-4 compaction, and greps for "free, continuous reseed", "Still unnamed" and "30146" return nothing). A7's contradiction was removed by banners in both cited files plus a corrected attribution in 1.3. A8 alone is refuted on the merits and not by edit: `:168` governs the **translation** axis and `:169` the **rotor** — two controllers, so the two criteria never apply to the same command.

REFUTED: unread-evidence — A4/A5/A6/A9/A10. Every cited passage was opened this session and is now cited *in the plan*, which is the state the verdict asked for: `frame-ownership-design.md:41-64`, `:60`, `:68-72`, `:92-101` in rows 1.1/1.9 and 2A; `stage2-plan.md:83-88` and `:64-67` in 0.2 and 2A; `motion-path-audit.md:124-126` and `t0-instrumentation-plan.md:65-70` in A7's three audits; `camera-acquisition-facts.md:465`/`:511-515` and `stage2-plan.md:17` as the new Phase **A9**; `stage2-plan.md:21-23`, `main-vi-startup.md:29-30`, `main-vi-panel-map.md:359` as the new Phase **A10**. The verdict no longer covers the plan because the plan no longer omits them.

REFUTED: refuted-already — B1. Accepted without reservation, and the finding was **stronger than it stated**: `toolkit-capabilities.md:32` and `:46-49` were opened and hold no Bundle/Unbundle **writer** at all, so the proposed "one cluster local" was unbuildable for the identical reason `stage2-plan.md:96-103` had already rejected composite queue elements. 1.3 no longer prescribes any cluster; it states the invariant and names the two routes that the present fleet can actually build.

REFUTED: helper-exists — B2. `toolkit-capabilities.md:31` (`exit_while`, 5/5, ExecState 0 → 1) and `stage2-plan.md:90-94` (the stop-inside-the-loop rule and the input-tunnel trap) and `frame-ownership-design.md:68-72` (error 1122, stop → drain → release) were opened and are now the content of **new row 1.9**. Nothing was re-derived; the helper is called by name.

REFUTED: already-measured — B3. `archive/benchmarks/INDEX.md:36` and `:41` were opened; both now appear inside 1.2's acceptance cell, which carries the frame set (200 chained frames, 5 beads) and the machine caveat (cuFFT bitwise reproducibility is per-GPU-model; re-run `N=200 py tools/gpu/test_mt2.py` on a new box). Asked at rev3 B1 and rev4 B3 and not done either time; done here.
