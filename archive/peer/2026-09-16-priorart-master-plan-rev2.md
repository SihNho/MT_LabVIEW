# priorart-master-plan-rev2

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $3.8909  in 28 / out 30811 / cache-create 202569 / cache-read 2189616  (415s, 24 turn(s))
- **date:** 2026-09-16
- **outcome:** ANSWERED (419s)
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
| **0.4** | ??**Camera contract ??DECIDED (see below): 90 Hz, `ExposureTime` ??5 556 쨉s (half the 11.111 ms period), `ExposureAuto` OFF**, 1280횞1024, offsets 0, never write `BinningHorizontal`. Apply it with `imaqdx_limits.py --restore` plus the fixed exposure, and write the read-back contract into every batch directory | the dim-field hazard is removed by the condition, not argued away |
| **0.5** | **Startup/shutdown side-effect audit.** The original's startup contains motor initialisation and focus-setting paths (`main-vi-startup.md:24`). "All loops running" is unsafe until startup is explicitly separated from steady operation ??this is the one real hazard in a dry run | rule 1b: the ASI piezo must never be driven |

## Phase A ??FINISH THE MAP FIRST  *(LabVIEW read-only + offline; the user's standing instruction)*

Nothing in phase 1 is ordered correctly without this, and hardware measurement before it measures the wrong things.

| # | work | needs |
|---|---|---|
| **A1** | **`OpOwnerChain_v0`** ??the missing link is **structure ??the diagram it sits on**, NOT node ??owner (that already works; `which_loop_owns_motor.log` prints the blocker 18 times). The recipe exists, corrected, **never run** | LabVIEW RO |
| **A2** | **Validate owner semantics per structure class** before any walk. The measured fact (`NAMES.md:864-866`) is scoped to `CaseStructure` ??1 of **6** classes (3 WhileLoop, 17 ForLoop, 37 CaseStructure, 21 FlatSequence, 4 Sequence, 2 EventStructure). FlatSequence gets a round-trip check against `diagram_tree_main.json` | A1 |
| **A3** | **Complete the 170-diagram hierarchy** ??the 41 unresolved plus every FlatSequence link, replacing position matching (the diagram was Clean-Up'd, so position means nothing) | A2 |
| **A4** | **The frame loop's TRUE membership** ??body **and nested frames**. The body-only list already exists (`frame-loop-anatomy.md:40-55`); only the nested delta is new | A3 |
| **A5** | **The unconditional per-frame path** ??what executes every iteration vs. conditionally. **This decides phase 1's loop-split order** | A4 |
| **A6** | **Close the autofocus question** ??*not* blocked on A3, and nearly answered already: `keystone-op-spec.md:594` names the trigger (*"the autofocus Case 10407 driven by bead 2's cal-slice index"* ??code-driven, as the user stated), and `main-vi-panel-map.md:132-141` lists the autofocus state objects separate from the three manual buttons. What remains is **one read of `ASI_adjust focus-subvi.vi`**: confirm the criterion, and whether it transacts serial when it fires | files + 1 VI read |
| **A7** | **Every VISA/serial call site inside A4's membership** ??rule 1c's audit; this list is what phase 1 must empty out of the frame loop | A4, A6 |
| **A8** | **Census A ??Case #10445 frames**, before the reseed `Or` collapse | LabVIEW RO |

## Phase 1 ??build the runnable seven-loop main VI on the **GPU** path, in a COPY of the original

Rule 1 unchanged: the original is never touched. The in-copy migration method is **proven end to end**
(`probe_migrate_v2` 3/3, `probe_migrate_v3` 5/5, `ExecState == 1`); untested is SCALE and RUNTIME, which is what
this phase tests.

| # | loop | acceptance at this phase |
|---|---|---|
| **1.1** | **Acquisition** ??`IMAQdx Get Image`, `Buffer Number Mode = Last`; no free slot ??skip the read, never gate the camera; carry the buffer number with the slot | the VI compiles and the loop iterates |
| **1.2** | **Tracking ??the GPU path** (user's decision 3): dequeue ??**GPU kernel via our own DLL interface** (single call per frame, raw image in; designed fresh, not copied from the Saleh-lab donor) ??frame-identified result. The CPU queue core's 162/162 fixture result is the **reference**, not the thing being shipped here | compiles; runs; result carries its buffer number; **x/y ??1e-6 px and z ??1e-4 쨉m against the CPU kernel on the fixture** |
| **1.3** | **Scheduler** ??cycle state machine; commands travel as **one versioned cluster through a single-owner queue**, never as four separate locals (peer-corrected 2026-09-12: non-atomic writes let the motor read a new speed with an old force) | compiles; emits a command trace |
| **1.4** | **Motor** ??reading and control out of the frame loop | compiles; issues and reads back |
| **1.5** | **ASI / focus** ??**exclusively owns the VISA session**; reaches the frame path only through a non-blocking handoff (rule 1c). Gated to every N frames rather than every frame | no serial on the frame path |
| **1.6** | **Display / UI** ??10??0 Hz gate + `Defer Panel Updates`; Image Display route, not Picture | panel updates do not enter the frame budget |
| **1.7** | **File writer** ??consumes the results queue, lossless FIFO | every computed result written, in order |

**Ordering inside phase 1 comes from phase A5**, not from assumption. Two of the numbers already exist: motor
reading costs **2.56 ms** (`motion-path-audit.md:84-99`) and autofocus holds the only fixed `Wait` on the motion
path plus its own VISA traffic, called **every frame** (`frame-loop-anatomy.md:68, :76`). Those are the frame
loop's known offenders ??against an **11.111 ms** budget at 90 Hz, motor reading alone is 23 % of it.

**The GPU interface is now on the critical path.** It used to be "stage 6, swap the kernel in". Check early whether
the DLL interface described in `docs/gpu-backend.md` / `docs/gpu-portability.md` is actually built and callable
from LabVIEW; if it is not, that is phase 1's first task, not a discovery made halfway through.

## Phase 2 ??the two questions that matter  *(dry run, no rig)*

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

### 2C. What the no-bead condition gives us for free

`tracking renewal` fires continuously, so the run is a **sustained reseed stress test**: reseed event counts, the
reset counter, the state fed into the next kernel call, `Limit of Program`'s stop-and-save at the cap, and reseed
arriving while acquisition has skipped buffers. Codex listed these as scenarios needing deliberate fault
injection; the empty stage injects them for free.

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

**And the autofocus question is nearly closed from files we already hold.** `keystone-op-spec.md:594` records the
trigger inside diagram 43: *"the autofocus **Case 10407 driven by bead 2's cal-slice index**"* ??code-driven,
exactly as the user said, and named. `main-vi-panel-map.md:132-141` lists the autofocus state objects that are
**separate** from the three manual buttons (`Auto-Focus` #38, `Focus Deviation from the Center` #33,
`Limit of Auto-Focus` #48). What remains is one read of `ASI_adjust focus-subvi.vi` to confirm the criterion and
whether it transacts serial when it fires. **This is no longer a stop-the-line item.**

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

**Note the budget this sets:** at 90 Hz the per-frame budget is **11.111 ms**, not the 6.00 ms that earlier
documents assume from a 150 Hz target. Dry-run acceptance is judged against 11.111 ms; the 150 Hz figures stay as
the stretch condition and are not what these runs test.

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

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  owner:
  since: 2026-09-16 12:2x
  purpose:
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
| **camera** | **90 Hz; exposure ??5 556 쨉s = half the 11.111 ms period; `ExposureAuto` OFF.** This dissolves codex's sharpest objection (auto-exposure in a dark field caps the camera near 66 Hz) by the operating condition rather than by argument. **The dry-run frame budget is 11.111 ms, not 6.00 ms** |
| **order** | **the MAP comes first** ??*"??吏?쒖???"* The rewrite had argued hardware-first because the motor window closes; that contradicted a standing instruction and codex attacked it independently. Phase A is restored ahead of building |
| **backend** | **the GPU top level is built FIRST and is the default**; the CPU-parallel top level follows. Both still ship as two separate VIs. The GPU DLL interface moves onto the critical path from "stage 6" |

## Cycle 10 ??REVISED, and now track A of the master plan

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

1. ?넅 **Where is the autofocus decision path?** **BLOCKING for the ASI split order.** The user (2026-09-16) has
   **never** adjusted ASI focus by hand in an experiment ??the joystick is separate hardware ??and **software**
   re-adjusts when the image goes off focus. Our file had inferred "operator-driven" from the subVI's inputs being
   *control references*; that is a statement about terminal type, and a `Value` property write from code arrives at
   a control reference exactly like a button press does. So an off-focus criterion and a writer exist somewhere and
   are **unidentified**. Correction recorded at `docs/camera-acquisition-facts.md` (?좑툘 block); the search is master
   plan **A6**. Manual adjustment is also possible but **the user does not know whether that path is even wired**.
2. **`docs/restructure-plan-4.6.md` 짠4 and 짠5 still need revision** ??짠4's construction method says "build the top
   level fresh" where the decision is **in a copy of the original**, and 짠5's stage-2 acceptance says all fixture
   frames where the truth is the **first 10,018**. 짠3 was corrected in the 2026-09-16 lint (`Next` ??`Last`,
   software timestamp removed). Queued behind the master plan's approval.
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

Prior-art review complete. **Zero `novel` — 12 findings, each with a file and line.** The rewrite fixed what the last two reviews caught; what it now does is (a) put an *already-built, already-benchmarked* artefact on its critical path as an open risk, (b) reinstate one item its own predecessor marked `already-failed`, and (c) restate a measured budget as the frame period.

---

# PART A — THE DIRECTION

## A1. "Does it run dry?" is already answered as **never unattended, user present** — and the reason is the ASI stage

This is the costliest finding, because it governs all of Phase 2.

`docs/t0-instrumentation-plan.md:128` — *"**Step 4 — in-situ cross-check (needs the user present; motor and piezo initialise)**"*, and `:136-138`: *"Running the main VI executes its initialisation frame, which contains the PI motor's `GOH` (go home) and the ASI stage's `MOVE AXIS TO POS`, i.e. real motion — **which is why this step waits for the user and never runs unattended**."* `:130` calls it *"Non-negotiable, not optional."*

The plan's 0.5 cites `main-vi-startup.md:24` (diagram 1, PI motor init) and frames the hazard as *"motor initialisation and focus-setting paths"*. The same document names the sharper one two rows down — `main-vi-startup.md:33`: diagram 10 = *"**`ASI TG-1000.lvlib:Initialize.vi` (uid 43997) then `Move Axis to Position.vi` (44036)** — MEASURED 2026-09-14"*, and `:35` diagram 12 = `Get Current Position.vi`. A copy of the original that keeps its startup **drives the ASI axis on every run**, which is the one instrument the plan itself declares must never move (`pre-rig-master-plan.md:59`, 0.5's own note).

Two consequences the plan does not carry:

- `main-vi-startup.md:47` — *"**PI motor first, then rotor, then serial config.** The ordering of the outer sequence is itself a fact the restructuring must preserve (rule 1a: behaviour, not just numbers)."* So excising startup is not a free workaround.
- The plan states rule 1b as *"the ASI piezo must never be driven"*, while `CLAUDE.md` §1b now reads *"Confirm the detached state from the recorded rig state before driving it; that is a check to run, not a question to ask."* The plan is stricter than the rule it cites, and still schedules the run that violates its own stricter form.

## A2. Phase 0.2 and 2A's back-pressure/soak were specified on 2026-09-12 — and the plan's version has lost content

`docs/restructure-plan-4.6.md:183-187`: *"**Acceptance must measure more than a rate.** … Each live stage records: processed-frame deadline misses, **gaps in buffer numbers**, the acquisition-call latency **distribution including p99.9 and max**, per-core CPU, UI-thread time, and display age. Add a **back-pressure test** — deliberately slow tracking and disk writing for minutes, not an 8 ms injection — and a soak run long enough to expose thermal throttling and disk stalls."*

Plan 0.2 presents its list as *"decided before the first run"*; 2A's back-pressure row and 2B's soak row are that paragraph. The plan's list **drops p99.9 and max, per-core CPU, UI-thread time and display age** — and UI-thread time is the one `camera-acquisition-facts.md:206-208` identifies as the mechanism behind the user's own symptom. The archive convention for what a run records is also already fixed (`archive/benchmarks/INDEX.md:27-29`).

## A3. The 11.111 ms budget contradicts the measurement the plan cites elsewhere

- Plan, decision 1 and Phase 1 ordering: *"at 90 Hz the per-frame budget is **11.111 ms**, not the 6.00 ms… motor reading alone is 23 % of it."*
- `docs/camera-acquisition-facts.md:53`: | 90.00 Hz | 11.11 ms | **budget (zero frames lost) 10 ms** | 12 ms → 45.0 Hz processed, 179 missed |, and `:58` — *"So **the budget is the frame period minus about 1 ms**."* `archive/benchmarks/INDEX.md:40` states it again: *"budget ~= frame period - 1 ms -> 90 Hz **10 ms**"*.

The plan substitutes the period for the budget, which is the exact substitution that file was written to prevent. The error is 11 % of the whole budget, and 2.56 ms is **25.6 %** of 10 ms, not 23 %.

## A4. A8 is scheduled in Phase A and forbidden 50 lines later in the same document

- Phase A, A8: *"**Census A — Case #10445 frames**, before the reseed `Or` collapse | LabVIEW RO"*.
- The same plan, "Already measured — CITE, do not redo" (`docs/pre-rig-master-plan.md:135`): *"`OpCaseFrames_v0` | **already failed**; do not retry (CLAUDE.md 'failure budget = 2')"*.

Census A means reading a CaseStructure's frames, which is what `OpCaseFrames_v0` is (`docs/stage2-assembly-step-e.md:216` — `Frames[]` 6363801 + `Frame Names` 6365002; `CLAUDE.md:212` — *"failed five times"*; cause recorded at `archive/2026-09-15-status-cycle7-reseed-measurements.md:43-44`). The plan schedules the need, forbids the only route, and names no alternative. The need itself is real (`stage2-assembly-step-e.md:180`) — it is the **route** that is closed.

Worse, this was already found. `archive/peer/2026-09-16-priorart-master-plan.md:464` returned `already-failed (B1 — OpCaseFrames_v0)`, and `:490` dispositioned it as *"overtaken by the rewrite — the items they cite (… `OpCaseFrames_v0` …) are **no longer proposed work**"*. Old Track A's A8 (`:96`) survived into the new Phase A verbatim. The disposition is factually wrong, and the same is true of the ordering verdict A6, whose target — an eight-item Track A ahead of the first delivery slice — is unchanged.

## A5. The autofocus cost claim cites the superseded half of our own record

- Plan, Phase 1 ordering: *"autofocus holds the only fixed `Wait` on the motion path plus its own VISA traffic, called **every frame** (`frame-loop-anatomy.md:68, :76`)."*
- `docs/camera-acquisition-facts.md:181-194` (a direct read of the subVI, 2026-09-12): the unconditional top-level diagram holds **five nodes** — two `Value` property nodes, a comparison, a Case Structure and a pass-through; *"The two real serial VIs sit **inside** that case, on diagram 4… **The fixed `Wait (ms)` the motion audit found is on diagram 8, also inside a nested frame — not unconditional.**"*

Both sides are ours. What is unconditional per frame is two UI-thread property reads, not a Wait plus VISA. (The user's 2026-09-15/16 corrections change the *frequency and trigger* of the expensive branch — `:169-179`, `:140-165` — not its conditionality.)

## A6. 0.4 cites a tool that cannot apply the camera contract the decision rests on

Plan 0.4: *"Apply it with `imaqdx_limits.py --restore` plus the fixed exposure."*

`tools/bench/imaqdx_limits.py:93-96` writes exactly four attributes — `OffsetX`, `OffsetY`, `Width`, `Height`. The string `Exposure` does not occur anywhere in the file; frame rate is **read only** (`:58-67`), and its docstring `:12-16` scopes the writes to the ROI and says *"Binning is never touched."* The 90.0009 Hz figure is the camera's as-found value (`camera-acquisition-facts.md:25`), not something `--restore` sets.

Also unresolved by the plan: `camera-acquisition-facts.md:240-251` measured that **`IMAQdxOpenCamera` resets the ROI on every open** — *"3. close, re-open, read | **1280 × 1024** again"* — so a contract written by a separate Python session is not established to survive LabVIEW opening the camera; for `ExposureTime`/`ExposureAuto` persistence is unmeasured in either direction.

This repeats a finding already sustained against the previous draft: `archive/peer/2026-09-16-master-plan-attack.md:79` and `:192` — *"C1 is not implementable with the cited tool"* (`serial_roundtrip_asi.ps1:50`, `$SAFE = @('/')`).

## A7. Unread evidence

- **`docs/cycle10-plan.md:63-70`** — revised the same day, after all eight prior-art verdicts were accepted. It is a **five**-step list: A8 is gone, step 3 is recorded as *"a RE-RUN, not a measurement"* (`:112-115`, the script already resolved 18 of 19 call sites), and `:118-120` says *"**Step 5's body-only half is already written down**… Do not re-derive the body list."* Phase A reinstates eight items and carries none of these qualifications, while STATUS calls cycle 10 "track A of the master plan".
- **`docs/restructure-plan-4.6.md:48-68`** — the inter-loop transport table and the queue mechanics Phase 2's *"no deadlock, no queue growth"* rests on: a bounded queue's default enqueue timeout is `-1` and **waits forever when full**; releasing a queue with a waiter raises **error 1122**; shutdown order is stop → drain → release. Phase 1 restates the seven loops without any of it.

---

# PART B — THE ARTIFACTS

## B1. The GPU interface is built, callable from LabVIEW, and benchmarked — it is not a critical-path unknown

Plan: *"Whether that interface is actually built and callable is now on the critical path"* / *"if it is not, that is phase 1's first task."* It is:

- `docs/gpu-backend.md:245-251` — *"**HARNESS_gpu2** (script-built: IMAQ Create → ReadFile → GetImagePixelPtr → one CLFN `mt2_track_simple`, DBL in/out, no image copies) vs HARNESS_base, 200 chained frames, 5 beads: **1.14 ms/frame**… outputs == reference (x,y 4.9e-7 px, z 2.9e-6 µm, 0 flips, 0 good mismatches)."*
- `archive/benchmarks/INDEX.md:36` (row 15), evidence `archive/bench-2026-09-09-gpu2-in-labview/REPORT.md`.
- `archive/benchmarks/INDEX.md:37` (row 16) — **`GPU_kernel_v1`**, the GPU backend **as a drop-in kernel carrying the tracking kernel's own connector pane**, 3 repeats × 200 frames.
- `docs/t0-instrumentation-plan.md:165` — *"`GPU_kernel_v1` **already takes the raw IMAQ pixel pointer** and skips `Omars IMAQ ImageToArray` entirely."*
- The build path is a one-call wrapper: `gpu-backend.md:330` — `gscript.build_clfn(target, location, dll, fn, flat_hex)`.

Loop 1.2's description — *"single call per frame, raw image in; designed fresh, not copied from the Saleh-lab donor"* — is a description of the accepted design that was already implemented (`gpu-backend.md:253-265`, the `mt2_*` C API).

## B2. 1.2's numeric acceptance is already met and recorded three times

x/y ≤ 1e-6 px, z ≤ 1e-4 µm against the CPU kernel: `gpu-backend.md:249` (200 chained frames), `docs/gpu-portability.md:87` (201 frames — dx 4.31e-07, dy 1.74e-07 px, dz 3.83e-06 µm, 0 flips), `archive/benchmarks/INDEX.md:41` (row 20, 41 frames identical to every digit before and after the multi-arch rebuild). `gpu-portability.md:112` states the standing tolerance in the same words the plan uses.

What is **not** on record is that tolerance across the full 10,043-frame fixture. If that is what 1.2 means, it must say so; as written it re-runs a closed test — the same shape as the E4 verdict at `archive/peer/2026-09-16-priorart-master-plan.md:437`.

## B3. Making the GPU the default at 90 Hz has a measured precondition the plan omits

`docs/gpu-backend.md:225-241`, measured with `tools/gpu/regime_test.py`:

| regime | DLL t | sampled state |
|---|---|---|
| tight loop | 1.12 ms | P2 1905 MHz SM |
| **2, 5 or 15 ms gaps** | **5.50 ms** | **P8 360 MHz SM / 405 MHz mem** |

*"**Any idle gap ≥ 2 ms drops the card to P8**; the memory clock falls 17× and every phase … slows ~3.5×. The NVIDIA 'prefer maximum performance' per-app profile does not apply to a CUDA-only process (verified: LabVIEW idle → P8). … **Working fix = SM clock lock (admin): `nvidia-smi -lgc 1365,1905`** (resets at reboot; register as a logon task with highest privileges for the rig)"* — and keep-alive v2/v3 both failed (`:233-234`).

At 90 Hz the GPU is idle ~9.5 ms of every 11.111 ms. Phase 1.2 and Phase 2 contain no timing acceptance and no clock-lock step, so the default backend is scheduled into exactly the duty cycle already measured to cost it 3.5×. Related and also unmentioned: `gpu-backend.md:345-349`, *"**Never `cudaHostRegister` LabVIEW's IMAQ buffer**"* — relevant the moment acquisition hands pooled image refnums to the GPU loop.

## B4. The buffer accounting of 0.2/0.3 partly exists inside the VI being copied

`docs/frame-loop-anatomy.md:47` — uid 6810, *"camera buffer bookkeeping … **yes** — it is the frame source"* (`get buff image-lost frames.vi`, MAIN_VI_MAP §3b). It is driven by the `LastBufferNumber` shift register on diagrams 19 and 43 (`camera-acquisition-facts.md:354`; `keystone-op-spec.md:594`, *"current image number / LastBufferNumber logic"*) and already feeds panel objects `Total Lost Frames`, `Missing Frames?`, `Lost Frame Message` (`camera-acquisition-facts.md:282-285`). The plan must say whether it reuses or replaces this — replacing it is a rule-1a behaviour change, not instrumentation.

## B5. 2B and 2C cannot both be true: the reseed path is gated, and the cap stops the program

- 2B: *"**run for hours with reseed firing continuously**; no leak, no deadlock, no queue growth."*
- 2C: *"`Limit of Program`'s stop-and-save at the cap"* listed as an observable of the same run.

`docs/GLOSSARY.md:48-54`: *"**the maximum number of auto-resets allowed in one run** … Each loss triggers an auto-reset; when the reset count reaches this limit the program **stops and saves the data collected so far**, rather than grinding on with no beads. Measured in the diagram: `Equal?` compares it with `# of Auto-Reset` — the test is **equality**, not 'greater than'."* And `docs/stage2-assembly-step-e.md:66`: wire 9806 ← control **`Auto-Reset`** — *"gates the lost-bead reseed - **it fires only while the user has Auto-Reset on**"*.

So with a bead-free field: `Auto-Reset` ON ⇒ the counter reaches the limit almost at once and the program terminates — there are no hours; `Auto-Reset` OFF ⇒ no reseed fires and the "free stress test" does not exist. Either the limit is raised (a control value that must be recorded as part of 0.2's snapshot, not assumed) or 2B's soak and 2C's stress test are separate runs.

One more scope correction on 2C: the periodic auto-reset arm is Case 10445, and `keystone-op-spec.md:600-601` records it as *"a periodic auto-reset **whose period never elapsed in this recording**"*. The empty stage injects the **loss** arm, not codex's full scenario list.

## B6. 1.6's display decision is already measured and already written into the architecture

`archive/benchmarks/INDEX.md:46` (row 25) — Image Display +1.0 ms closed / +6.9 ms visible vs Picture 2.9 / 8.0, ≈1.9 ms CPU saved; row 22 (`:43`) — construction ≈2.7 ms + Picture paint ≈6.5 ms visible. `docs/restructure-plan-4.6.md:45` already carries loop 6 with those numbers and the 10–20 Hz gate. 1.6 restates the conclusion with no citation; cite it rather than re-deriving it.

---

## Where I found NO prior art — these are clear

Building the seven-loop top level **inside a copy** at scale (the method is proven at `probe_migrate_v2` 3/3 / `v3` 5/5, the scale is not); loops 1.1, 1.3, 1.4, 1.5, 1.7 as artefacts; the frame-identity corruption test; "the camera is never gated" verified by instrumenting the boundary; A2–A5 and A7 of Phase A; the batch-directory convention at `G:\Data\Sihyeong-Developing\`; and the user's three decisions themselves (90 Hz / map-first / GPU-first), which are user calls and not mine to review.

---

```
PRIOR-ART: settled-already     (A1 — t0-instrumentation-plan.md:128, :136-138 "never runs unattended"; main-vi-startup.md:33, :47)
PRIOR-ART: unread-evidence     (A1 — main-vi-startup.md:33 ASI Initialize + Move Axis to Position at startup, cited only at :24)
PRIOR-ART: settled-already     (A2 — restructure-plan-4.6.md:183-187 is Phase 0.2 + 2A + 2B, with more content)
PRIOR-ART: contradicted        (A3 — plan's 11.111 ms budget vs camera-acquisition-facts.md:53, :58; INDEX.md:40)
PRIOR-ART: contradicted        (A4 — Phase A "A8 Census A" vs pre-rig-master-plan.md:135 "do not retry")
PRIOR-ART: already-failed      (A4 — OpCaseFrames_v0, CLAUDE.md:212; 2026-09-15-status-cycle7-reseed-measurements.md:43-44)
PRIOR-ART: refuted-already     (A4 — outcome-review-20260915.md:151, :225; disposition at priorart-master-plan.md:490 is wrong)
PRIOR-ART: contradicted        (A5 — frame-loop-anatomy.md:68 vs camera-acquisition-facts.md:181-194)
PRIOR-ART: contradicted        (A6 — 0.4 cites imaqdx_limits.py for exposure; imaqdx_limits.py:93-96 writes ROI only)
PRIOR-ART: unread-evidence     (A7 — cycle10-plan.md:63-70, :112-120; restructure-plan-4.6.md:48-68)
PRIOR-ART: already-built       (B1 — gpu-backend.md:245-251; INDEX.md:36, :37; t0-instrumentation-plan.md:165)
PRIOR-ART: already-measured    (B2 — gpu-backend.md:249; gpu-portability.md:87, :112; INDEX.md:41)
PRIOR-ART: already-measured    (B3 — gpu-backend.md:225-241, P8 at any idle gap ≥ 2 ms; clock lock required)
PRIOR-ART: helper-exists       (B4 — get buff image-lost frames.vi uid 6810, frame-loop-anatomy.md:47; camera-acquisition-facts.md:354)
PRIOR-ART: contradicted        (B5 — 2B "hours of continuous reseed" vs GLOSSARY.md:48-54 and stage2-assembly-step-e.md:66)
PRIOR-ART: already-measured    (B6 — INDEX.md:43, :46; restructure-plan-4.6.md:45)
```

The cheapest way to act on this, if the citations hold when opened: **delete the GPU-interface risk item and replace loop 1.2 with "drop in `GPU_kernel_v1`, add the `nvidia-smi -lgc` logon task, and state whether the tolerance run is the 10,043-frame fixture"** (B1–B3 collapse into one line); **move A8 out of Phase A until a route exists** (A4); and **decide Phase 2's startup question before anything else** — under `t0-instrumentation-plan.md:128-138` the dry run as written is a supervised step that drives the ASI axis, which is the one thing the plan says it will never do.

## Sources

(extract from answer)

## What was done with it

**Five findings verified against the sources and acted on; the rest recorded.** This is the third prior-art review
of this plan ($3.89, 415 s, 24 turns) and it still found two of my own errors, one self-contradiction, and one
piece of good news the plan was treating as risk.

| verdict | verified? | what changed |
|---|---|---|
| **A3** `contradicted` — the plan's **11.111 ms** budget | ✅ **sustained** | `camera-acquisition-facts.md:53` measures, for 90.00 Hz / 11.11 ms period, a **budget of 10 ms**, first failing at 12 ms: *"the budget is the frame period minus about 1 ms, and ~1 ms of that margin is jitter."* I had used the **period** as the budget and spent a margin measured to be necessary. **Corrected to 10 ms** |
| **A6** `contradicted` — 0.4 cites `imaqdx_limits.py` for exposure | ✅ **sustained** | `imaqdx_limits.py:93-96` writes only `OffsetX/OffsetY/Width/Height`. It **cannot** set exposure, so the user's decided camera contract had no tool to apply it. 0.4 now says the extension must be written and both values read back |
| **B5** `contradicted` — "hours of continuous reseed" | ✅ **sustained, and it corrects the run design** | `stage2-assembly-step-e.md:66`: the reseed is gated by control **`Auto-Reset`** (*"it fires only while the user has Auto-Reset on"*) and capped by **`Limit of Program`**, which on **equality** makes the run **stop and save**. With no beads the cap is reached almost at once, so a default-settings dry run **terminates itself in seconds**. 2C now enumerates three deliberate configurations and sends the choice to the user |
| **A4** `contradicted` + `already-failed` | ✅ **sustained — my own plan contradicted itself** | A8 proposed Census A while the same document's own table says `OpCaseFrames_v0` already failed and must not be retried (`CLAUDE.md:212` is the "failure budget = 2" example). A8 is re-scoped: read #10445 by a route that works, or drop it. Do not rebuild the failed op |
| **B1** `already-built` + **B2/B3** `already-measured` | ✅ **sustained — and it is good news** | `gpu-backend.md:245-251`: our own GPU interface is **built, callable from LabVIEW through one CLFN (`mt2_track_simple`), and measured at 1.14 ms/frame** with outputs at x,y 4.9e-7 px / z 2.9e-6 µm / 0 flips — already inside the agreed tolerance. The plan had put "is the DLL even callable?" on the critical path; it is answered. Decision 3 (GPU top level first) is therefore much cheaper than it looked |
| **A1, A2, A5, A7, B4, B6** | recorded | Mostly "this content already exists elsewhere" (`restructure-plan-4.6.md:183-187`, `cycle10-plan.md:63-70`, `get buff image-lost frames.vi` as the gap-accounting helper). Acted on by citing rather than duplicating; **A1's `unread-evidence` on `main-vi-startup.md:33` (ASI Initialize + Move Axis to Position AT STARTUP) is folded into plan item 0.5**, which is the one real hazard in a dry run given rule 1b |

**No `REFUTED:` line.** Nothing was refuted — the plan changed, which is the gate's own instruction. One correction
to my previous annotation, which this review flagged: the disposition I wrote at
`2026-09-16-priorart-master-plan.md:490` treated Census A as live work; it is not, per A4 above.

**Review spend on this plan: ≈ $12.1 across three prior-art runs plus one codex attack.** Each earned it — a
misread citation worth a cycle, four items of already-done work, and now a wrong frame budget, a missing tool, a
self-terminating run design and a de-risked GPU decision.
