---
type: peer-review
status: historical
date: 2026-09-16
tags: [peer-review, archive, labview]
disposition: legacy
legacy_note: closed as legacy 2026-09-25 by card chat-L1 (cutoff 2026-09-22; user 2026-09-25 lint order before runner resume)
---

# priorart-master-plan-rev4

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $5.6428  in 66 / out 40092 / cache-create 200014 / cache-read 5280033  (570s, 48 turn(s))
- **date:** 2026-09-16
- **outcome:** ANSWERED (574s)
- **why asked:** the build gate was closed and rev3's 18 findings had just been accepted into the plan; rev4 asked
  whether the *corrected* plan still repeats work. **It does, and the two most valuable hits are about this very
  session's work:** (a) the autofocus interval N was already named in our files — `frame-loop-wire-graph.md:120`
  reads `#30146 Property 'Frame rate'.Value (implicit)` and `main-vi-panel-map.md:83` gives its value **25** — so
  the number I had queued an op build for was on disk; (b) `archive/peer/2026-09-14-implicit-property-node-linked-object.md`
  had already answered the implicit-property-node question (ID `Linked Control` 636F806, and `OpNodeLabels_v0`
  built and verified 88/88 on this VI), which means **two codex dispatches I made today were re-asks** of an
  archived question — the one thing `CLAUDE.md`'s archiving rule names explicitly. A third (the property-ID fact
  query) was killed mid-flight once rev4 landed. Also accepted: wire 3362 was already at `main-vi-panel-map.md:311`;
  the GPU clock-lock script already exists (`tools/gpu/register_gpu_clock_lock.ps1`); the plan contradicted itself
  about the "free reseed stress test" versus `Auto-Reset` OFF; and startup's disarm list is longer than the ASI —
  PI `MOV`/`GOH`/`VEL` plus the rotor's 200-turn baseline trip. All folded into the plan, `STATUS.md` and
  `docs/camera-acquisition-facts.md` the same hour.
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

**Free bonus:** with no beads ??even with the LED off ??`tracking renewal` (re-initialise and re-track when a bead
leaves the tracking z range) fires continuously. That is a **free, continuous reseed stress test**, which is the
fault injection codex said we would otherwise have to build.

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
| **0.5** | ?뵶 **THE BLOCKER, named at last: startup DRIVES THE FORBIDDEN AXIS.** Not "contains motor initialisation paths" ??`main-vi-startup.md:33` measured it: **startup diagram 10 calls `ASI TG-1000.lvlib:Initialize.vi` (uid 43997) then `Move Axis to Position.vi` (uid 44036)**, opening COM4 (alias **`ASI_Piezo`**) and moving an axis; **the same pair recurs on diagram 88**, and diagram 12 reads the position back (uid 44196). `t0-instrumentation-plan.md:136-138` already concluded from this that running the main VI *"never runs unattended"*. So a copy of the original cannot simply be started. **Before any dry run the copy must have these three call sites disarmed** (the ASI init/move pair on diagrams 10 and 88, and the position read on 12), the disarming must be *shown* ??node-level, by uid, in the build log ??and `main-vi-startup.md:47` notes the outer startup ordering is itself a rule-1a fact, so the excision is recorded as a deliberate deviation, not a silent edit. This is also where master plan A6's finding lands: the autofocus case fires on a frame-index schedule, so **the same axis is driven again during the run** unless the boolean on wire 3362 blocks it | rule 1b: the ASI piezo is the one instrument that can physically break the rig. A "dry run" that starts the original's startup sequence is not dry |

| **0.6** | **GPU clock lock, because the default backend is scheduled into the duty cycle measured to cost 3.5횞.** Register `nvidia-smi -lgc 1365,1905` as a logon task with highest privileges (it resets at reboot) and verify the pstate **under the real 90 Hz duty cycle**, not in a tight loop. `-lmc` is unsupported on this RTX 2060, so upload stays ~3횞 slower than tight-loop and the 1.14 ms figure is not the number to plan against (`gpu-backend.md:225-241`) | a measured ms/frame at 90 Hz replaces the tight-loop figure before 1.2 is accepted |

## Phase A ??FINISH THE MAP FIRST  *(LabVIEW read-only + offline; the user's standing instruction)*

Nothing in phase 1 is ordered correctly without this, and hardware measurement before it measures the wrong things.

| # | work | needs |
|---|---|---|
| **A1** | **`OpOwnerChain_v0`** ??the missing link is **structure ??the diagram it sits on**, NOT node ??owner (that already works; `which_loop_owns_motor.log` prints the blocker 18 times). The recipe exists, corrected, **never run** | LabVIEW RO |
| **A2** | **Validate owner semantics per structure class** before any walk. The measured fact (`NAMES.md:864-866`) is scoped to `CaseStructure` ??1 of **6** classes (3 WhileLoop, 17 ForLoop, 37 CaseStructure, 21 FlatSequence, 4 Sequence, 2 EventStructure). FlatSequence gets a round-trip check against `diagram_tree_main.json` | A1 |
| **A3** | **Complete the 170-diagram hierarchy** ??the 41 unresolved plus every FlatSequence link, replacing position matching (the diagram was Clean-Up'd, so position means nothing) | A2 |
| **A4** | **The frame loop's TRUE membership** ??body **and nested frames**. The body-only list already exists (`frame-loop-anatomy.md:40-55`); only the nested delta is new | A3 |
| **A5** | **The unconditional per-frame path** ??what executes every iteration vs. conditionally. **This decides phase 1's loop-split order** | A4 |
| **A6** | ??**DONE 2026-09-16, offline, from dumps we already had.** The criterion is `AND( (frame index mod N) == 0 , NOT(x) )` on `CaseStructure #10407`, acting on the kernel's `Index of closest cal image slice, bead 2` against `# slices in stack`; it **does** transact serial when it fires. Full derivation and wire-level citations: `camera-acquisition-facts.md`, "MEASURED 2026-09-16 (master plan A6)". **Open remainder, 2 names:** the control behind Property Node `#30146` (the interval N) and the boolean on **wire 3362** ??both loop-border objects, so they come with A1's owner chain, not another offline pass. The second one decides whether a dry run auto-disarms the ASI axis, which makes it 0.5's dependency | ??+ 1 LabVIEW read |
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
| **1.4** | **Motor** ??reading and control out of the frame loop | compiles; issues and reads back |
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
2. **Run the prior-art review of the plan, because the build gate is closed on purpose:**
   ```
   py tools/bgrun.py --max-min 25 --log tools/bench/priorart_master_plan_rev3.log -- py tools/prior_art_review.py --plan-file docs/pre-rig-master-plan.md --slug master-plan-rev3 --trigger cycle-start
   ```
   The plan changed after the last review, so its verdicts are unrefuted and `guard_cycle` blocks every recipe
   build. **The release is a fresh review returning `novel`, not a `REFUTED:` line** ??nothing has been refuted;
   the plan was corrected instead. Diagnostics, docs and peer dispatch are never blocked.
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

1. ?윞 **Autofocus decision path ??FOUND (A6, 2026-09-16), two names still open.** It is **periodic and
   code-driven**, in the MAIN VI: `CaseStructure #10407` on diagram 43 fires on `AND( (frame index mod N) == 0 ,
   NOT(x) )` and acts on the kernel's `Index of closest cal image slice, bead 2` against `# slices in stack`; when
   it fires it **does** transact serial (`ASI TG-1000.lvlib:Move Axis Relative.vi` on diagram 73, plus the subVI's
   two VISA calls and its fixed `Wait`). Read offline from dumps we already had ??full derivation in
   `docs/camera-acquisition-facts.md` ("MEASURED 2026-09-16 (master plan A6)"). **Still unnamed:** the control
   feeding Property Node `#30146` (the interval N) and the boolean on **wire 3362** ??both are loop-border objects,
   so they are resolved by A1's owner chain, not by another offline pass. ?좑툘 Until wire 3362 is named we cannot say
   whether a dry run auto-disarms the **forbidden** ASI focus axis; that is now master plan 0.5's concrete target.
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

No prior-art-free direction here: **10 findings, zero `novel`** — and the two most expensive ones concern work the live session is doing *right now*, which our own files already answered.

First, credit where due: rev3's A2–A7, A9 and B2–B5 are all discharged in this revision (clock lock added as 0.6, periodic auto-reset arm corrected, reseed mechanism retracted, bit-identity replacement named, A6 done, 1.7 cites the queue mechanics and `boundary_manifest.py`, 1.8 decides reuse-or-replace, 0.4 rescoped on measurement). rev3's A1 is discharged **only for the ASI half**, and rev3's B1 is unchanged.

---

# PART A — THE DIRECTION

## A1 `unread-evidence` — 0.5 disarms one instrument out of three that the same startup drives

0.5 quotes `t0-instrumentation-plan.md:136-138` — but that sentence reads *"its initialisation frame, which contains **the PI motor's `GOH` (go home)** and the ASI stage's `MOVE AXIS TO POS`"*. The plan keeps the ASI half and drops the PI half. The measured startup is broader still:

- `docs/main-vi-startup.md:24` diagram 1 = *"PI motor init, driven straight from the panel control `Set Focus (0->50)` (=51.5 today)"*; `:26` diagram 3 = *"PI **MOV** (absolute position)"*; `:27` diagram 4 = *"PI **GOH** (go home)"*; `:28` diagram 5 = *"PI **VEL** then a position query"*.
- `docs/rotor-sign-diagnosis.md:124-126` — *"**The controller counter was left at 0** … the original main VI (Baseline 200) would now command its first absolute move as a **200-turn trip**, so either restore the old coordinate (`PIC 100000`…) before running the original again, or run only the new VI."* Same fact at `docs/instrument-libraries.md:324-325` and `STATUS.md:61-62`.
- `docs/rotor-sign-diagnosis.md:127` — *"**Remaining: repoint the NEW main VI's rotor calls to `SetCommand_signed.vi` (stage 2).**"* That build task appears nowhere in Phase 1's list (1.1–1.8), yet 2B's rotor row (`pre-rig-master-plan.md:165`) accepts *"absolute degrees … the counter is at 0"* — which is true only of a VI carrying the signed repoint.

A copy of the original started today issues PI MOV/GOH from a panel control and, on its first absolute rotor move, a 200-turn trip. Motors are permitted (rule 1b), so this is not forbidden — it is **unnamed**, and 0.5 is the section whose whole job is naming it.

## A2 `already-measured` — the interval N behind Property Node #30146 is `Frame rate` = 25, read from the machine on 2026-09-14

This is the fact the LabVIEW lock is currently held for (`STATUS.md:38-42`, *"resolve wire 3362 / 31234 / 3268 and Property Node #30146"*), and which `docs/camera-acquisition-facts.md:266-268` calls *"Still open: N … pending the peer answer on whether an implicit property node's linked object is readable at all in LabVIEW 2026."*

It is not open, and that peer answer arrived two days ago:

- `tools/bench/main_vi_node_labels.json:2979-2983` — `"30146": { "diagram": 43, "label": "Frame rate", "is_panel_label": true }`.
- `docs/frame-loop-wire-graph.md:120` — *"#30146 Property `Frame rate`.Value (implicit)"*, with provenance at `:10-13` (`OpNodeLabels_v0`, `Node.Label` read headless; *"An implicit property node's name is the panel object it is bound to"*).
- `archive/benchmarks/INDEX.md:48` (row 27) — *"**88/88 implicit nodes returned a non-empty label that is a panel label** (45 distinct objects, 40 READ / 48 WRITE)"*.
- `archive/peer/2026-09-14-implicit-property-node-linked-object.md:13` asks exactly *"which scripting property names the bound control, and is it reachable cast-free"*; `:26-27` answers (`Linked Control` 636F806 needs a cast; `Node.Label → Text.Text` does not); `:40-43` records that the reader was built and confirmed on the machine.
- `docs/main-vi-panel-map.md:83` — `Frame rate` is CTL uid 98, **value 25**; `:469` — diagram 43, node 30146, **READ**.

So **N = 25**: the autofocus case fires every 25 frames ≈ **3.6 times a second at 90 Hz**. That number belongs in 1.5's gating and in A7's serial audit today, and it removes a LabVIEW read from the critical path.

## A3 `contradicted` — the candidate list for #30146 is refuted by our own wire graph

`docs/camera-acquisition-facts.md:219-220`: *"which control feeds Property Node **#30146** (the interval N — **panel candidates are `Limit of Auto-Focus` #48 and `Focus Deviation from the Center` #33**)"*, carried forward verbatim into `pre-rig-master-plan.md:69` and `STATUS.md:189`.

Against `docs/frame-loop-wire-graph.md:120` above. Neither candidate is right, and the same file's own line `:262-264` already warns *"do not assume `Auto-Focus` turns autofocus off."*

## A4 `already-measured` — wire 3362 was re-derived from LabVIEW today; it was on disk on 2026-09-14

`docs/camera-acquisition-facts.md:242-245` (added during this review) names it from `panel_wiring(MAIN)`, *"114 rows"*, run 2026-09-16. That is the **same 114-row census** already written up as `docs/main-vi-panel-map.md:261-263` (*"Wiring column — measured 2026-09-14 with `OpPanelWiring_v0` (`Control.Terminal` → `Terminal.Connected Wire`)"*, source `tools/bench/main_vi_panel_wiring.json`), whose row `:311` reads:

| # | label | type | terminal wired | wire uid | control uid |
|---|---|---|---|---|---|
| 31 | `Fix to a Certain Pattern` | CTL | YES | **3362** | **10230** |

Corroborated at `docs/frame-loop-wire-graph.md:458` (3362 listed among control-terminal-sourced wires) and `:56` (`#1469 Property 'Fix to a Certain Pattern'.Value` on the same loop). `camera-acquisition-facts.md:233-235` even prescribes the route — *"the label comes from `panel_wiring`, not from the signature"* — while the answer that census produced was already in a doc. The conclusion is right; the LabVIEW session that produced it was avoidable.

## A5 `unread-evidence` — the copy configures the camera itself, on a diagram the plan never names

0.4/1.1 freeze the run at 1280×1024 / 90 Hz and put the exposure write *"right after `IMAQdx Open Camera`"*. In a copy of the original that is **diagram 87, the startup frame** (`docs/stage2-plan.md:17` — *"Camera session opened in the startup frames (diagram 87: `IMAQdx Open Camera` → `Configure Grab`)"*), not the acquisition loop — and that same frame holds:

- `docs/camera-acquisition-facts.md:382-384` — *"uid **9775** is the **IMAQdx property node**"* with terminals `Height`, `Width`; `:414-417` — it belongs to camera **initialisation**;
- `:428-430` — *"**Still open, and it is the whole question: is uid 9775 reading or writing?** … a *write* means the VI sets it and the value on the wire is the answer"*;
- `:338-351` — the 640×512 observation is recorded as **one unexplained observation**, four hypotheses falsified;
- `:353-355` — *"its front-panel **indicators** `Width` and `Height` hold **640** and **512** … that run ended with the camera at 640 × 512"*; same at `archive/benchmarks/INDEX.md:40`.

If uid 9775 writes, the dry run's condition is set by the copy, not by the contract — and every budget number in Phase 2 is against the wrong frame size.

## A6 `contradicted` — the plan's headline promises the stress test its own decision removes

- `pre-rig-master-plan.md:37-39` — *"**Free bonus** … `tracking renewal` … fires continuously. That is a **free, continuous reseed stress test**"*; `:166` (2B) — *"run for hours **with reseed firing continuously**"*; `:170-172` (2C) — *"the run exercises reseed for free: **reseed event counts, the reset counter**, the state fed into the next kernel call"*.
- Against `:188-190` — with `Auto-Reset` OFF *"the **bead-loss arm cannot fire**"* — and `:213-215`, under **"What this deliberately does NOT test"**: *"the reseed path itself, reset counters, state handed to the next kernel call"*.

Both halves are in one document 130 lines apart, and the claim has already propagated to `STATUS.md:147`. What survives the OFF decision is only the **periodic** arm (`:192-201`), which is not a reseed stress test.

## A7 `unread-evidence` — how the tracking loop gets initialised with no beads was raised by codex and answered only for the tracking half

`archive/peer/2026-09-16-master-plan-attack.md:73` — *"The tracking loop requires **valid initial bead coordinates, calibration clusters, good flags, and reseed state**, as shown in stage2-plan.md:17"*; `:85` — *"E2 needs either a representative sample or **an explicit hybrid test mode that injects fixture tracking inputs** while exercising live acquisition."*

The plan (`:31-35`) answers the *tracking-fails* half and never the *initialisation* half:
- `docs/stage2-plan.md:21-23` — the kernel takes `Array of cal clusters`, `Real-space cosine window`, `Cosine bandpass for Hilbert`, built at startup (`main-vi-startup.md:29-30`, diagrams 6–7, from `cal image array`);
- `docs/main-vi-panel-map.md:359` — `Done Picking \nBeads?` is a **wired control** (uid 11819).

Which `.cal` a bead-free batch loads, and what satisfies the picking gate, is unwritten — and `:241-246`'s false-positive warning covers only the writer, not this.

---

# PART B — THE ARTIFACTS

**B1 `already-built`** — 0.6 proposes to *"Register `nvidia-smi -lgc 1365,1905` as a logon task with highest privileges"*. It exists: `tools/gpu/register_gpu_clock_lock.ps1:3-6` — `New-ScheduledTaskAction -Execute nvidia-smi.exe -Argument "-lgc 1365,1905"`, `-AtLogOn`, `-RunLevel Highest`, task name *"GPU clock lock (LabVIEW tracking)"*. `docs/gpu-backend.md:239` already prescribed it. What is genuinely unknown is whether it was ever **run** on this box — a `Get-ScheduledTask` check, not a build.

**B2 `helper-exists`** — 0.6's *"verify the pstate under the real 90 Hz duty cycle"* has its harness: `tools/gpu/regime_test.py` is the nvidia-smi pstate/SM/mem sampler behind the table at `gpu-backend.md:227-234`, and `tools/gpu/regime_test_lock.py:22` already runs `regime("15 ms gaps under clock lock", 0.015, 0)`. Change the gap to 0.0111; do not write a third script.

**B3 `already-measured` (repeat of rev3 B1, unchanged)** — 1.2's acceptance still says *"against the CPU kernel **on the fixture**"* (`:82`) with no frame count and no machine caveat. `docs/gpu-backend.md:245-251` is **200 chained frames**; `archive/benchmarks/INDEX.md:41` (row 20) adds the constraint that must travel with the number: *"**the 1e-6 px acceptance is a property of a MACHINE, not of this DLL** — cuFFT guarantees bitwise reproducibility only for a fixed GPU model, so it must be re-run on any new box (`N=200 py tools/gpu/test_mt2.py`)"*. `INDEX.md:37` (row 16) also records `GPU_kernel_v1` already wearing the kernel's own connector pane.

---

## Where I found NO prior art

Loops 1.1, 1.3, 1.4, 1.5, 1.7, 1.8 as artefacts; Phase A2–A5 and A7; 0.1's batch directory and 0.2's record list; the frame-identity corruption test; "the camera is never gated" verified at the boundary; and the user's four decisions (90 Hz · map-first · GPU-first · `Auto-Reset` OFF), which are theirs to make.

```
PRIOR-ART: unread-evidence   (A1 — main-vi-startup.md:24, :26-28 PI MOV/GOH at startup; t0-instrumentation-plan.md:136-138 names GOH too; rotor-sign-diagnosis.md:124-127 200-turn trip + "repoint to SetCommand_signed.vi" never in Phase 1)
PRIOR-ART: already-measured  (A2 — N = `Frame rate` = 25: main_vi_node_labels.json:2979-2983; frame-loop-wire-graph.md:120; INDEX.md:48; main-vi-panel-map.md:83, :469)
PRIOR-ART: unread-evidence   (A2 — archive/peer/2026-09-14-implicit-property-node-linked-object.md:13, :26-27, :40-43 answers the "pending peer question" at camera-acquisition-facts.md:266-268)
PRIOR-ART: contradicted      (A3 — camera-acquisition-facts.md:219-220 candidates #48/#33 vs frame-loop-wire-graph.md:120; carried into pre-rig-master-plan.md:69 and STATUS.md:189)
PRIOR-ART: already-measured  (A4 — wire 3362 = `Fix to a Certain Pattern` uid 10230, main-vi-panel-map.md:311, census of 2026-09-14 at :261-263)
PRIOR-ART: unread-evidence   (A5 — diagram 87 / uid 9775 read-or-write OPEN and the 640x512 unexplained: camera-acquisition-facts.md:382-384, :414-417, :428-430, :338-351, :353-355; INDEX.md:40; stage2-plan.md:17)
PRIOR-ART: contradicted      (A6 — "free continuous reseed stress test" pre-rig-master-plan.md:37-39, :166, :170-172 vs :188-190, :213-215; propagated to STATUS.md:147)
PRIOR-ART: unread-evidence   (A7 — no-bead initialisation: master-plan-attack.md:73, :85; stage2-plan.md:21-23; main-vi-startup.md:29-30; main-vi-panel-map.md:359)
PRIOR-ART: already-built     (B1 — tools/gpu/register_gpu_clock_lock.ps1:3-6 is 0.6's logon task; gpu-backend.md:239)
PRIOR-ART: helper-exists     (B2 — tools/gpu/regime_test.py, regime_test_lock.py:22 for the duty-cycle pstate check)
PRIOR-ART: already-measured  (B3 — 1.2's tolerance: gpu-backend.md:245-251 = 200 frames; INDEX.md:41 machine caveat; INDEX.md:37)
```

**Cheapest way to act, if the citations hold when opened:** (1) close `N = Frame rate = 25` from `main_vi_node_labels.json` and release the lock — nothing in A6's remainder needs LabVIEW; (2) extend 0.5 to name the PI MOV/GOH sites and the rotor repoint, or state in writing why they are safe; (3) add diagram 87 / uid 9775 to Phase A before the camera contract is called frozen; (4) delete the "free reseed stress test" sentence from the plan and STATUS, or reinstate the arm that would make it true; (5) say which fixture run 1.2's tolerance means, and carry INDEX row 20's machine caveat with it; (6) check for the scheduled task instead of building it.

I took no lock, opened no `.vi`, built nothing and ran nothing. One note on method: `docs/camera-acquisition-facts.md` changed under me mid-review (the `Fix to a Certain Pattern` section at :242-264 appeared between two reads), consistent with the live session holding the lock — findings A2/A4 are written against the file as it stands now.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
