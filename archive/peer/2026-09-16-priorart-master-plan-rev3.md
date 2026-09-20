# priorart-master-plan-rev3

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.2706  in 32 / out 43609 / cache-create 210440 / cache-read 2151612  (546s, 29 turn(s))
- **date:** 2026-09-16
- **outcome:** ANSWERED (550s)
- **why asked:** (Claude fills in)
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
| **0.4** | ??**Camera contract ??DECIDED (see below): 90 Hz, `ExposureTime` ??5 556 쨉s (half the 11.111 ms period), `ExposureAuto` OFF**, 1280횞1024, offsets 0, never write `BinningHorizontal`. ?뵶 **The tool to apply it does not exist yet** ??`imaqdx_limits.py --restore` writes only `OffsetX/OffsetY/Width/Height` (`:93-96`), never exposure. A small extension must write `ExposureAuto = Off` and `ExposureTime`, then **read both back** into the batch directory | the dim-field hazard is removed by the condition, not argued away ??but only if the condition is actually applied |
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
| **A8** | ?좑툘 **Census A ??Case #10445 frames. RE-SCOPE BEFORE ATTEMPTING.** The obvious route is `OpCaseFrames_v0`, which **failed five times** and is CLAUDE.md's own example of breaking the "failure budget = 2" rule (`CLAUDE.md:212`), and the outcome review told us not to retry it. So: either read #10445 by a route that already works (A1's owner chain walked downward, or the existing wire-graph JSON), or **drop A8** and collapse the reseed `Or` conservatively. Do **not** rebuild the failed op | A1 |

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
already meets tolerance, at **1.14 ms of the 10 ms budget**. What is unproven is the interface inside a *live,
free-running* loop with stop and error handling ??not the numerics.

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

The dry runs turn the lost-bead reseed **off**. The mechanism makes this clean: the reseed term is
`Auto-Reset AND (min(pos in cal image out) < 0)`, so with the control off the AND is false and no auto-reset
fires ??which means **`# of Auto-Reset` never increments and `Limit of Program` never trips**. The run does not
self-terminate, and questions 2A (frame accounting) and 2B (motor motion and reading) are read without reseed
noise on top of them. That is the right first experiment: separate "do the loops run correctly" from "does
re-initialisation behave", rather than debugging both at once.

**What this deliberately does NOT test, recorded so it is not mistaken for coverage:**

| not exercised | where it goes |
|---|---|
| the reseed path itself, reset counters, state handed to the next kernel call | a later batch with `Auto-Reset` ON and `Limit of Program` raised |
| **`Limit of Program`'s stop-and-save**, including its exact-equality trigger | a later, deliberately short batch at the normal limit ??it is reachable in seconds, so it costs nothing when we want it |
| `Reset Tracking`, the manual OR | operator-driven; test alongside the above |

### Why reseeding drops frames ??the user's observation, and our files already explain it

> *"?댁쟾 寃쏀뿕??reseeding???곸슜?섎㈃ ?꾨젅???쒕엻???ㅼ냼 ?앷린??寃?媛숇뜕?? ?댁쑀媛 ?덈뒗吏."*

There is a mechanism, and it is an **asymmetry between the two frames of Case 5540** that our own census recorded
(`keystone-op-spec.md:596-600`):

| frame | contents |
|---|---|
| **pass-through** (diagram 81) | **no nodes at all** |
| **reset** (diagram 82) | **one Property Node reading `Value`** (uid 4401 ??wire 5888) ??the calibration bead positions |

**A `Value` property node costs a UI-thread switch** (`frame-loop-anatomy.md:65`), and the UI thread is also where
the front-panel image and graphs redraw ??*"the loops that were deliberately separated meet again there"* (`:66`).
So an ordinary iteration pays nothing for this Case, while **a reseeding iteration pays one extra UI-thread round
trip whose latency depends on how busy the UI thread happens to be** (`camera-acquisition-facts.md:205`).

Two things turn that into visible frame loss rather than a small wobble:

1. **The margin is about 1 ms.** At 90 Hz the measured budget is **10 ms of an 11.11 ms period**
   (`camera-acquisition-facts.md:53`) ??the rest is jitter allowance. A UI-thread round trip contending with a
   redraw eats it.
2. **The failure mode is a cliff, not a slope.** Overrun the budget by 0.3 ms under `Next` semantics and you lose
   *every second frame*, not 5 % (`camera-acquisition-facts.md:60-66`). One slow reseed iteration therefore costs
   whole frames.

**Design consequence for the rebuild, and it is free:** the reseed values are *the loop's own initialisers*
(`stage2-assembly-step-e.md:143`). They do not need a Property Node at all ??read the calibration positions **once**
and carry them on a wire or shift register into `ReseedMux.vi`. `frame-loop-anatomy.md:82` states the general rule:
*a Property Node write goes through the UI thread; a wire does not.* That removes the extra round trip from the
reseed path entirely, changing no computation (rule 1a: same values, same route, different scheduling).

**Confidence and what would confirm it:** the mechanism is measured (node census, UI-thread cost, budget, cliff);
what nobody has measured is **a reseed iteration's actual duration against a non-reseed one**. That is one number,
and it needs the `Auto-Reset` ON batch ??so it is a reason that batch happens, not a reason to doubt the account.

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

1. ?넅 **Where is the autofocus decision path?** **BLOCKING for the ASI split order.** The user (2026-09-16) has
   **never** adjusted ASI focus by hand in an experiment ??the joystick is separate hardware ??and **software**
   re-adjusts when the image goes off focus. Our file had inferred "operator-driven" from the subVI's inputs being
   *control references*; that is a statement about terminal type, and a `Value` property write from code arrives at
   a control reference exactly like a button press does. So an off-focus criterion and a writer exist somewhere and
   are **unidentified**. Correction recorded at `docs/camera-acquisition-facts.md` (?좑툘 block); the search is master
   plan **A6**. Manual adjustment is also possible but **the user does not know whether that path is even wired**.
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

Write is disabled in this session, so the review is delivered here in full. **14 findings, zero `novel`** — and five of them are repeats of verdicts the previous review (`archive/peer/2026-09-16-priorart-master-plan-rev2.md`) recorded as accepted, whose plan text did not change.

---

# PART A — THE DIRECTION

## A1 `settled-already` + `unread-evidence` — the dry run is already decided as *never unattended*, and the reason is the ASI axis at startup

This governs all of Phase 2 and is the costliest finding.

- `docs/t0-instrumentation-plan.md:128` — *"Step 4 — in-situ cross-check (**needs the user present; motor and piezo initialise**)"*; `:130` — *"**Non-negotiable, not optional.**"*; `:136-138` — *"**Running the main VI executes its initialisation frame, which contains the PI motor's `GOH` (go home) and the ASI stage's `MOVE AXIS TO POS`, i.e. real motion — which is why this step waits for the user and never runs unattended.**"*
- `docs/main-vi-startup.md:33` — diagram 10 = *"**`ASI TG-1000.lvlib:Initialize.vi` (uid 43997) then `Move Axis to Position.vi` (44036)** — MEASURED 2026-09-14 … this frame opens the **ASI stage port (COM4, alias `ASI_Piezo`)** and moves an axis. **The same pair recurs on diagram 88**"*; `:35` — diagram 12 = `Get Current Position.vi`.
- Plan 0.5 cites only `main-vi-startup.md:24` (PI motor init) and declares *"the ASI piezo must never be driven"* — then schedules the run that drives it, never naming the measured call site.
- `docs/main-vi-startup.md:47` — *"**PI motor first, then rotor, then serial config.** The ordering of the outer sequence is itself a fact the restructuring must preserve (rule 1a)."* So excising startup is itself a rule-1a change, not a free workaround.

**Why this is a repeat:** raised at `rev2.md:479-486` (verdicts `:595-596`); its own disposition at `rev2.md:632` says *"A1's `unread-evidence` on `main-vi-startup.md:33` … **is folded into plan item 0.5**."* Compare that review's verbatim copy of 0.5 (`rev2.md:104`) with the current 0.5 — **the sentence is unchanged.** The folding did not happen.

## A2 `contradicted` — 1.14 ms/frame is a *tight-loop* number; 90 Hz is the exact duty cycle measured to cost 3.5×

- Plan: *"at **1.14 ms of the 10 ms budget**. What is unproven is the interface inside a live, free-running loop with stop and error handling — **not the numerics**."*
- `docs/gpu-backend.md:248` — that 1.14 ms is *"**200 chained frames**"*, back-to-back.
- `docs/gpu-backend.md:232` — *"| 2, 5 or 15 ms gaps | **5.50 ms** | … **P8 360 MHz SM / 405 MHz mem** |"*
- `docs/gpu-backend.md:236-241` — *"**Any idle gap ≥ 2 ms drops the card to P8**; the memory clock falls 17× and every phase … slows ~3.5×. The NVIDIA 'prefer maximum performance' per-app profile does not apply to a CUDA-only process (verified: LabVIEW idle → P8) … **Working fix = SM clock lock (admin): `nvidia-smi -lgc 1365,1905`** … Memory clock lock (`-lmc`) is **NOT supported on the RTX 2060** … **final in-LabVIEW DLL time 2.12 ms, gpu − base 5.41 ms**."*

At 90 Hz the GPU idles ~9–10 ms of every 11.111 ms. The numerics **are** what is unproven in this regime, and no clock-lock step appears anywhere in the plan. rev2 raised this as B3 (`rev2.md:554-565`, verdict `:607`); the annotation at `rev2.md:631` absorbed it into *"good news"* and carried 1.14 ms forward without the precondition.

Adjacent, also uncarried: `gpu-backend.md:345-349` — *"**Never `cudaHostRegister` LabVIEW's IMAQ buffer**"* (32.5 ms/frame, 3 slice flips, 0.3 px deviation after frame ~50) — live the moment loop 1.1 hands pooled IMAQ refnums to 1.2.

## A3 `contradicted` — *"`Auto-Reset` OFF ⇒ `# of Auto-Reset` never increments and `Limit of Program` never trips"* has a second, ungated arm

- `docs/stage2-assembly-step-e.md:66` — `Auto-Reset` gates *"**the lost-bead reseed**"* — that arm, not the reset system.
- `docs/stage2-assembly-step-e.md:36-38` — *"**The periodic auto-reset term is bigger** than one `Or`: `# of Auto-Reset`.Value #9879, `Quotient & Remainder` #10068, `Equal?` #10019, Not/And nodes. **It never fired on this recording**, so the 10,043-frame run cannot validate it — **it gets a separate small-interval test.**"*
- `docs/GLOSSARY.md:55` — *"**# of Auto-Reset** — periodic re-homing … (program auto-ends once this counter hits its limit, per an in-VI comment: **"~27mins/100000"**)"*.
- `docs/keystone-op-spec.md:600-601` — Case 10445 is *"**a periodic auto-reset whose period never elapsed in this recording**"*.
- The increment path has never been read: `stage2-assembly-step-e.md:55` — *"`And` → 9921 (**sink to find**)"*; `:75-76` — *"remainder 10187 → (**sink to find**)"*.

The fixture is 10,043 frames ≈ **1.9 minutes** at 90 Hz — shorter than a "~27 min" period, which is why it never fired. The plan proposes **hours**, and its own A8 offers to *"**drop A8**"* — the #10445 census — discarding the measurement that would settle the claim while asserting the claim.

## A4 `contradicted` — the "why reseeding drops frames" mechanism rests on a census our own files later corrected

- Plan: *"| **pass-through** (diagram 81) | no nodes | **reset** (diagram 82) | **one Property Node reading `Value`** (uid 4401 → wire 5888)"* → *"a reseeding iteration pays **one extra UI-thread round trip**"* (cited to `keystone-op-spec.md:596-600`, read 2026-09-07).
- `docs/stage2-assembly-step-e.md:122-138` — **CENSUS B, 2026-09-15**, `OpTunnelRead_v0` 24/24 + `OpWireSource_v5` 12/12, identity-checked, main VI byte-identical: *"frames of Case #5540 | exactly TWO: diagrams **5582** and **5592**"*; both *"**pure pass-through**"*; `:134` — *"**Correction to the E0 note**"*; `:137-138` — *"**neither frame computes anything — both are pass-throughs**."*
- `:140-145` — the reseed values arrive on tunnels from outside the loop (`FlatSequenceInnerTunnel` **2886** / **5818**), not from a property read inside the frame.

The two censuses disagree on the frames' identity *and* their contents. The plan's confidence line — *"the mechanism is measured (node census, UI-thread cost, budget, cliff)"* — rests on the superseded half.

Its "free design consequence" is also **already the built design**: `stage2-assembly-step-e.md:143-148` — *"the reseed values are literally **the loop's INITIALISERS** … `ReseedMux.vi` belongs BEFORE the kernel … its `xyz0`/`good0` inputs are the same arrays that initialise the loop's state registers, **which that VI already has in hand**."*

## A5 `contradicted` — GPU-first dissolves the bit-identity acceptance assigned to stages 0–5, and no replacement is named

The user's GPU-first call is theirs and not under review; its recorded consequence is:
- `restructure-plan-4.6.md:201` — stage 2 = *"fixture output **bit-identical for the first 10,018 frames**"*;
- `:205` — stage **6** = *"GPU build: swap loop 2's kernel | x/y ≤ 1e-6 px, z ≤ 1e-4 µm"*;
- `:209-210` — *"**Stages 0–5 remain bit-identical**; only the GPU build … uses a tolerance."*

With the GPU kernel in loop 2 from the start, no assembled stage can be accepted bit-identically. The plan states no replacement reference.

## A6 `already-measured` — A6's second half is already read from the machine

- Plan A6: *"one read of `ASI_adjust focus-subvi.vi`: confirm the criterion, **and whether it transacts serial when it fires**."*
- `docs/camera-acquisition-facts.md:192-194` — `read_asi_focus.py` already read all nine diagrams: *"The two real serial VIs sit **inside** that case, on diagram 4: uid 663 = `Move Axis to Position.vi` and uid 929 = `Get Current Position.vi`. **The fixed `Wait (ms)` … is on diagram 8 … not unconditional.**"* Restated at `archive/benchmarks/INDEX.md:40`.
- Genuinely open is only the **off-focus criterion and its writer** (`camera-acquisition-facts.md:156-161`).

## A7 `contradicted` (repeat, unfixed) — the autofocus "Wait + VISA, every frame" line

Plan: *"autofocus holds the only fixed `Wait` … plus its own VISA traffic, **called every frame** (`frame-loop-anatomy.md:68, :76`)"* vs `camera-acquisition-facts.md:181-194`: unconditionally it is **five nodes — two `Value` reads, a comparison, a Case Structure, a pass-through**. The cited document is itself provisional: `frame-loop-anatomy.md:8` *"**DRAFT / PROPOSAL**"*, `:105` *"The Wait's constant … was **detected, not read**."* Identical to rev2 A5 (`rev2.md:510-515`, verdict `:602`); sentence unchanged.

## A8 `settled-already` (repeat, unfixed) — 0.2 / 2A / 2B already specified, with more content

`restructure-plan-4.6.md:212-216` — *"Each live stage records: processed-frame deadline misses, **gaps in buffer numbers**, the acquisition-call latency **distribution including p99.9 and max**, per-core CPU, **UI-thread time**, and display age. Add a **back-pressure test** … and a **soak run**."* Plan 0.2 records *"p50/p99"* and drops p99.9, max, per-core CPU, UI-thread time and display age — UI-thread time being the one quantity `camera-acquisition-facts.md:204-208` names as the mechanism behind the user's own symptom. `:201` already states 2A's criterion in the plan's own words. (rev2's cite 183-187 has moved to **212-216** since the 2026-09-16 banner.)

## A9 `unread-evidence` + `helper-exists` — queue mechanics and the boundary-manifest gate

- `restructure-plan-4.6.md:65-68` — *"a bounded LabVIEW queue's default enqueue timeout is `-1`, which **waits forever when full** … releasing a queue while another node is waiting … raises **error 1122**, so shutdown order is stop → drain → release."* Phase 2B asserts *"no deadlock, no queue growth"* with none of it.
- `:147-167` — extraction *"does **not** preserve all observable behaviour 'by construction'"*, and *"**each extraction is gated on a written BOUNDARY MANIFEST**"*; `:161-162` — *"an extracted **Event Structure** is the worst case: **latch-action Boolean terminals must be read inside the event case**."* The frame loop holds one (`frame-loop-anatomy.md:35`) and 1.6 moves the UI out. Phase 1 has no manifest step.
- The helper exists: `tools/bench/boundary_manifest.py` (`archive/peer/2026-09-15-frameloop-seam-77-crossings.md:50`) — and that same review **refuted** the "77 crossings" number (`:36`), so re-scope rather than re-derive.

---

# PART B — THE ARTIFACTS

**B1 `already-measured` (repeat, half-fixed)** — 1.2's tolerance: `gpu-backend.md:249` (200 frames, x,y 4.9e-7 px / z 2.9e-6 µm / 0 flips); `gpu-portability.md:112`; `INDEX.md:41` (row 20, 41 + 201 frames); `INDEX.md:37` (row 16 — `GPU_kernel_v1` already wears the kernel's own connector pane). Say which run 1.2 means: at 200/201 frames it is closed; across the full 10,043-frame fixture it has never been run. Carry `INDEX.md:41`'s constraint: *"the 1e-6 px acceptance is a property of a **MACHINE**, not of this DLL."*

**B2 `already-built`** — the GPU stop path. `gpu-backend.md:332-343`: built precisely because *"the experiment VI is normally stopped with LabVIEW's Abort button, so `mt2_close` never runs"*; single-context policy + keep-alive idle timeout, verified by `tools/gpu/test_abort.py` — 12 open-without-close cycles, **0 MB** drift. The plan calls "stop and error handling" unproven without citing this.

**B3 `helper-exists` (repeat, unfixed)** — `frame-loop-anatomy.md:47` uid 6810 *"camera buffer bookkeeping … it is the frame source"*; `camera-acquisition-facts.md:353-354` — `Total Lost Frames` / `Missing Frames?` / lost-frame message already driven by the `LastBufferNumber` shift register on diagrams 19 and 43. 0.2/0.3 must say reuse or replace; **replacing it is a rule-1a behaviour change.**

**B4 `already-measured` (repeat, unfixed)** — 1.6's display route: `INDEX.md:46` (row 25, Image Display +1.0/+6.9 vs Picture +2.9/+8.0), `INDEX.md:43` (row 22), and `restructure-plan-4.6.md:45` already carries loop 6 with those numbers and the 10–20 Hz gate. 1.6 restates the conclusion uncited.

**B5 `contradicted`** — `camera-acquisition-facts.md:240-251`: *"**`IMAQdxOpenCamera` hands every session a full frame**"* — close/re-open reads 1280×1024 again. The VI opens its own session after the Python session closes; exposure persistence across open is **unmeasured in either direction**. 0.4's read-back must be taken *after the VI opens the camera*, or the recorded contract is not the condition the run had.

---

## Where I found NO prior art

Loops 1.1, 1.3, 1.4, 1.5, 1.7 as artefacts; the frame-identity corruption test; "the camera is never gated" verified by instrumenting the boundary; the batch directory at `G:\Data\Sihyeong-Developing\`; A2–A5 and A7 of Phase A; and the user's four decisions (90 Hz / map-first / GPU-first / `Auto-Reset` OFF), which are user calls. The A8 re-scope correctly discharges rev2's A4.

---

```
PRIOR-ART: settled-already     (A1 — t0-instrumentation-plan.md:128, :130, :136-138 "never runs unattended")
PRIOR-ART: unread-evidence     (A1 — main-vi-startup.md:33 ASI Initialize + Move Axis to Position AT STARTUP, recurs diagram 88; :47)
PRIOR-ART: contradicted        (A2 — "1.14 ms, not the numerics" vs gpu-backend.md:232, :236-241, :248 P8 at any idle gap >= 2 ms)
PRIOR-ART: unread-evidence     (A2 — gpu-backend.md:345-349 never cudaHostRegister the IMAQ buffer)
PRIOR-ART: contradicted        (A3 — "Limit of Program never trips" vs stage2-assembly-step-e.md:36-38, :66; GLOSSARY.md:55; keystone-op-spec.md:600-601)
PRIOR-ART: contradicted        (A4 — reseed Property-Node mechanism, keystone-op-spec.md:596-600 vs CENSUS B stage2-assembly-step-e.md:128-138)
PRIOR-ART: settled-already     (A4 — "carry the initialisers on a wire" already the design, stage2-assembly-step-e.md:143-148)
PRIOR-ART: contradicted        (A5 — GPU-first vs restructure-plan-4.6.md:201, :205, :209-210 "stages 0-5 remain bit-identical")
PRIOR-ART: already-measured    (A6 — "does it transact serial when it fires", camera-acquisition-facts.md:192-194; INDEX.md:40)
PRIOR-ART: contradicted        (A7 — "Wait + VISA every frame", frame-loop-anatomy.md:68 vs camera-acquisition-facts.md:181-194; :8, :105)
PRIOR-ART: settled-already     (A8 — 0.2/2A/2B already specified with more content, restructure-plan-4.6.md:212-216, :201)
PRIOR-ART: unread-evidence     (A9 — restructure-plan-4.6.md:65-68 queue timeout -1 / error 1122; :147-167 BOUNDARY MANIFEST; :161-162 latch-action)
PRIOR-ART: helper-exists       (A9 — tools/bench/boundary_manifest.py, per archive/peer/2026-09-15-frameloop-seam-77-crossings.md:50, :36)
PRIOR-ART: already-measured    (B1 — 1.2's tolerance, gpu-backend.md:249; gpu-portability.md:112; INDEX.md:37, :41)
PRIOR-ART: already-built       (B2 — GPU abort/stop path, gpu-backend.md:332-343; tools/gpu/test_abort.py)
PRIOR-ART: helper-exists       (B3 — get buff image-lost frames.vi uid 6810, frame-loop-anatomy.md:47; camera-acquisition-facts.md:353-354)
PRIOR-ART: already-measured    (B4 — 1.6 display route, INDEX.md:43, :46; restructure-plan-4.6.md:45)
PRIOR-ART: contradicted        (B5 — camera contract vs camera-acquisition-facts.md:240-251, open resets attributes)
```

**Cheapest way to act, if the citations hold when opened:** (1) settle the startup question before anything in Phase 2 is scheduled — as written the dry run is a *supervised* step that drives the ASI axis; (2) add the `nvidia-smi -lgc` clock lock to Phase 0 and give 1.2 a timing acceptance; (3) either run #10445's census by a working route or stop claiming the run cannot self-terminate; (4) reconcile the two Case #5540 censuses before using the reseed frame-loss account; (5) say what replaces bit-identity for stages 2–5; (6) cite rather than restate for 0.2, 1.2, 1.6, and say reuse-or-replace for uid 6810.

I took no lock, built nothing, and ran nothing.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
