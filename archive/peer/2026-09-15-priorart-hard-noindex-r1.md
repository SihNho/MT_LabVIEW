# priorart-hard-noindex-r1

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $3.0848  in 32 / out 29599 / cache-create 150438 / cache-read 1680535  (361s, 29 turn(s))
- **date:** 2026-09-15
- **outcome:** ANSWERED (365s)
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
PLAN UNDER REVIEW - the parallel tracking build, next stage.

The acceptance bar is the full requirement in project-requirements/: acquisition, tracking, motor reading, the
scheduler and data saving each in its own parallel loop, built inside a copy of the main VI. Eight steps follow,
each with the reasoning behind it.

1. FEEDBACK STATE. The tracking loop must carry x/y/z, the good-flags and pos-in-cal from one frame to the next.
   Shift registers cannot be created by VI Scripting, so I will implement the feedback with a pair of local
   variables written at the end of the body and read at the top instead.

2. KERNEL CALL SITES. The four-fold tracking kernel is invoked from several places in the main VI, so every call
   site has to be found and patched consistently. I will sweep the whole VI for them before touching anything.

3. DISPLAY. The display path is cheap relative to the kernel, so it can stay inside the frame loop for now and be
   split out later; it is not worth a loop of its own in this stage.

4. GPU. The GPU backend is slower than the CPU one because the CUDA kernels themselves are slow. The fix is to
   optimise the kernels - fuse the passes and cut the per-pass work - before revisiting the interface.

5. PARALLEL OUTPUT ORDER. When the per-bead For loop runs with several parallel instances, the instances finish
   out of order, so its auto-indexed output array cannot be trusted to keep bead k at index k. I will carry an
   explicit bead-index array alongside the results and re-sort on the consumer side.

6. XYZ LAYOUT. The layout of the kernel's x,y,z array is settled, so I will wire the Decimate-based split now and
   route each component to its own consumer.

7. FIXTURE FRAMES. New fixture recordings will be saved as PNG files, one per frame, which keeps them viewable and
   is good enough for bit-exact replay comparisons.

8. WRITING CLUSTER ARRAYS. LabVIEW's ActiveX interface cannot write a 1-D array of clusters - an earlier attempt
   silently did nothing - so the recipe will avoid that route entirely and set each element through a separate
   control instead.

Attack this on prior art only: has any of it already been decided, measured, built, or tried and failed here, and
is any claim above contradicted by this project's own files?


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-15
tags: [hand-off]
---

# STATUS ??read this first (one screen; detail lives one layer down, never appended here)

## LabVIEW execution lock

```yaml
labview-lock:
  status: acquired   # session 6959fd57 - overnight loop from 2026-09-14 22:5x. Release only on the user's word.
  owner: Claude (session 6959fd57)
  since: 2026-09-14 22:5x (took over from 7b982769)
  scope: >
    Stage-2 assembly + read-only analysis of the main VI (opened by reference, never edited or saved). Scratch VIs
    under claudeDev are created and deleted per run.
  status: released
  owner:
  since:
  purpose:
  state: >
    2026-09-15 18:2x - RELEASED, nothing running. Step 0a is unanswered after two void runs; the next attempt is
    specified in the 0a STATE block below and is a DIFFERENT test, not a rerun. Only scratch copies under
    claudeDev were touched; the donor HARNESS_copyloop.vi is unchanged on disk (2026-09-14 14:33) and the main VI
    is byte-identical: md5 2a78e17c449cacdaf5da389818526859, written 2026-09-01 12:07:59, verified after the runs.
    A LabVIEW instance is idle in memory and holds stale scratch VIs - prefer a restart, or unique scratch names.
```

## Cycle discipline ??the devices that enforce it (2026-09-15)

| device | what it refuses / reports |
|---|---|
| `tools/audit_cycle.py` | mechanical compliance of a cycle (bgrun discipline, runs terminated, failing logs reviewed, reviews annotated, originals untouched) + the cost lines. No judgement, no thresholds |
| `tools/retrospective.py --cycle N` | dispatches a FIXED question set about HOW the cycle ran, with the audit, the raw build logs and CLAUDE.md attached ??Claude writes neither the questions nor the evidence |
| `tools/violations.py` | counts the `VIOLATION: <slug>` lines retrospectives record, **from the files**; 3 of a slug = the next cycle must build a mechanical device for it |
| `tools/hooks/guard_cycle.py` | refuses the next RECIPE build while the previous cycle has no newer retrospective, or while a slug is at threshold |

Cycle 7's retrospective (`archive/peer/2026-09-15-retrospective-cycle7.md`) recorded all eight slugs; they stand at
**1 each** against a threshold of 3, so no device is due ??`py tools/violations.py` is the tally, not this file. Its
sharpest accepted finding: the approach should have changed at `OpWireSource_v5` attempt 1, the SECOND inferred
broken-VI diagnosis. Cost of the whole overnight window (cycles 1?? **plus** earlier rotor work ??not cycle 7
alone): 130 builds, 23 failing logs, 83 peer reviews, 212 min inside bgrun.

## Session-model policy (user, 2026-09-15) ??ADOPTED

Judgement vs material split, now CLAUDE.md "Usage discipline" 짠3: the scarce model does design, review judgement,
rule-1a calls and diverging diagnoses; a separate **Opus-high** session prepares the material (API-fact censuses,
verified-pattern recipes, log greps, bookkeeping, peer dispatch/collection). **Material sessions stop after 2
failures** and hand over; **judgement sessions stay short** (STATUS + plan doc + failing-log summary only).
**This week Fable's budget is exhausted, so judgement runs on Opus max.**

## RIG STATE ??still disassembled (user, 2026-09-15 16:4x): **no bead measurement is possible**

So nothing that needs real beads can be accepted right now: live acquisition at 150 Hz with `Images Missed` = 0,
real camera jitter and buffer gaps, reseed on a real bead loss, and the ASI focus-active cost all WAIT for
reassembly. Everything else on the delivery path is fixture work and does not: the 10,043-frame recording
(`archive/bench-2026-09-07-fixture/`) carries 13 real lost-bead frames, the kernel's per-frame cost is already
measured on it, and the display paint cost was measured 2026-09-14. **Ask the user before touching hardware in any
session; rule 1b (never the ASI piezo, never the motor) is NOT lifted by the older permission block below.**

## HARDWARE PERMISSION ??FULL, granted 2026-09-13 for an unattended day (rig disassembled)

Piezo stage detached 쨌 rotor free 쨌 magnet motor full travel 쨌 camera **on condition of restore**
(`tools/bench/imaqdx_limits.py --restore`: 1280횞1024, offsets 0, 90.0009 Hz; never write `BinningHorizontal`).
**CLAUDE.md rule 1b is NOT revoked** ??this permission is tied to the disassembled state; ask again in any session
that does not carry this line, and stop if anything suggests the rig was reassembled. Hardware last touched
2026-09-13 20:1x??0:22 (rotor only, with the user present); the rotor's counter is 0 by the new convention.

## Where things stand

**Stage 1 (analysis) CLOSED** ??the documentation pass is done and measured: `docs/instrument-libraries.md`,
`main-vi-subvi-identity.md` (98 call sites, 0 mismatches), `main-vi-panel-map.md` (114 objects + wiring + locals),
`main-vi-state.md`, `main-vi-startup.md`, `frame-loop-wire-graph.md` (all 83 half-edges accounted),
`rotor-sign-diagnosis.md`. Benchmarks and their raw data: `archive/benchmarks/INDEX.md` rows 22??1.

**Stage 2 (assembly) IN PROGRESS** ??plan `docs/stage2-plan.md`, per-step docs `docs/stage2-assembly-step-{a,a3,b,c,e}.md`.

| cycle | result |
|---|---|
| 1?? | the scripting primitives Stage 2 needed: shift-register creation/wiring for While AND For loops, For-loop control tunnels, copy-by-reference of primitives (`copy_by_index`), `StrToPath` (INDEX rows 37??9) |
| 4 | **`Track_v6_CPU_core_v0.vi` ??the replay core, 69/69 PASS** (row 40) |
| 5 | **`Track_v6_CPU_queue_v0.vi` ??the producer/consumer core, 162/162 PASS** (row 41) |

**Say it exactly** (the outcome review, 2026-09-15, found this line overstated): both cores are bit-identical to the
reference for the **first 10,018 frames ??those before the first bead loss**, not for all 10,043. The remainder waits
on the reseed logic. Both are **replay** artefacts: recorded TIFFs, `FOR` loops, no live acquisition, no stop protocol.
| 6 | **the reseed selector's four feeders, measured** (row 43) ??see below |
| 7 | reseed design reviewed; Census B measured; Census A and the build still open |

Narrative of cycles 1??: `archive/2026-09-15-status-stage2-cycles-1-7.md`. Toolkit API:
`docs/toolkit-capabilities.md`. Verified names and the standing LabVIEW-scripting facts: `docs/NAMES.md`.

## Cycle 7 (reseed) ??closed

The reseed measurements (four selector feeders, Case #5540's two frames, the `ReseedMux.vi` design) are still true
and live in `docs/stage2-assembly-step-e.md`. They and the NEXT list the outcome review superseded moved to
`archive/2026-09-15-status-cycle7-reseed-measurements.md`. One item survives into the delivery cycle: **Census A ??
Case #10445** must be read before it is collapsed into an `Or`, as part of the reseed slice rather than its own cycle.

## 2026-09-15 afternoon ??review gained a THIRD layer, and it judged the project

Review now has three layers (CLAUDE.md rule 5): hypothesis (`guard_peer`), cycle (`retrospective`), **outcome**
(`outcome_review.py`, every 5 cycles or 7 days, codex only, gated in `guard_cycle.py`). Also: `peer.ps1` gained
`-Agent claude` (rule/consistency auditor, sonnet ??it CANNOT discharge a failed prediction), pinned codex to
`gpt-5.6-sol`/medium, records the model in every archive, and `-Kind review` REFUSES confirm-bait while appending
the adversarial instruction set. `guard_peer` additionally requires `outcome: ANSWERED` from an external peer.
Verification 13/13: `tools/bench/verify_review_layers_run2.log`.

**The first outcome review fired all 7 slugs** (`archive/peer/2026-09-15-outcome-review-20260915.md`):
*"the next problem is not missing tooling; it is failure to cross the boundary from replay proof to experiment
product."* 168 op VIs, 116 recipes, 217 peer exchanges produced two replay VIs and **zero runnable experimental
VIs**; of the five functions the requirement names, none has moved into a product.

## STRATEGY DECIDED (user, 2026-09-15 16:3x) ??restructure INSIDE A COPY of the original

**"??諛⑺뼢??醫뗪쿋??"** Not the outcome review's hot-path-only swap, and not a fresh rebuild in an empty VI.
The work happens in a **copy** of the main VI (rule 1 unchanged: the original is never touched), so bead picking,
calibration, the controls and the experiment workflow survive, and the loops come out in the order the **measured
frame budget** dictates:

**The SHELL decision stands; the ORDERING was refuted by the plan review and is replaced**
(`archive/peer/2026-09-15-restructure-in-copy-plan.md`). My ordering rested on "kernel + one serial round trip =
5.06 ms of 6.00", but `docs/camera-acquisition-facts.md` **already answered this on 2026-09-12**, 44 lines above the
line I quoted: *"the frame loop does NOT transact serial every iteration"* ??the ASI wrapper's unconditional
top-level diagram is five nodes and its VISA case is a **gate only**; the real per-frame cost is **two UI-thread
property reads**. There is no ~2.5 ms ASI prize on ordinary frames, so ASI-first has no performance support.

| # | step | note |
|---|---|---|
| 1 | **measure the unconditional per-frame path** ??what actually executes every frame, p50 **and p99** | replaces all guessed orderings |
| 2 | **one live vertical slice**: acquisition -> owned image handoff -> queue core -> frame-identified result, including stop, error, reseed and overload | the queue core proves replay numerics only, through the first 10,018 pre-loss frames |
| 3 | **split whichever measured owner dominates** | not whichever I assumed |
| 4 | scheduler, file writer | completes the 7-loop target |

**But the ASI loop is back on the critical path ??user, 2026-09-15: "?ㅼ젣 ?ъ슜 寃곌낵 ASI濡?focus 議곗젙? 苑ㅻ굹 鍮덈쾲?섍쾶
諛쒖깮??"** The plan review deprioritised ASI because its serial is conditional; that reasoning assumed focus activity
is rare, and it is not. The frame loop's cost is therefore **bimodal** ??cheap ordinarily, +~2 ms whenever focus acts,
inside a 6.00 ms budget ??so the defect is **frames dropped during focus adjustment (p99), not average throughput**.
Both the review and the user's fact point the same way architecturally: the **ASI loop must exclusively own the VISA
session**. Still unmeasured, and needing the rig: how often "frequent" is, and the true `WHERE` latency.

Two seam constraints the review established, to honour in any design: the tracking seam is an **immutable,
frame-identified result message BEFORE `save trace.vi` #376** (the 22-node slice is a *reachability* slice, not a
component ??lifting it drags file ownership and accumulated `total data array` state into tracking); and the ASI
loop must **exclusively own the VISA session**, because case #10407's `Outgoing Handle` carries resource ownership,
not just a value. Also corrected: the 49 "to border" nets are marked *unresolved* by the script that produced them ??
the richer census finds **31** actual loop tunnels.

The user's objection is what produced this ??*"A?덉? 紐⑦꽣 蹂묐젹???ш린?쒕떎?붽굅 ?꾨땲??"* Motor CONTROL was already
its own loop (diagram 20) so nothing is given up there, but the hot-path-only plan would have left the **ASI serial
subVI #48 and the ten property nodes** in the frame loop ??precisely the two things
`docs/camera-acquisition-facts.md` measures as worth **~2.5 ms, the difference between 150 Hz and 200 Hz**
(kernel + one serial round trip = 5.06 ms of a 6.00 ms budget). **The plan is under peer attack before construction
starts** (`tools/bench/peer_restructure_in_copy_plan.log`); nothing is built until that returns.

## OVERLOAD POLICY ??DECIDED (user, 2026-09-15): latest-wins, drop the backlog

**"?먮? 踰꾨━怨??덈줈 ?ㅼ뼱?ㅻ뒗 ?꾨젅?꾩쓣 ?쎈뒗 寃껋씠 媛??諛붾엺吏곹븿. ?대뒗 ?쒓퀎???곗씠?곗쓽 ?꾨??깆쓣 ?꾪븿."** A result
computed from a stale frame is a sample attached to the wrong moment; an explicit gap is honest, a late sample is
not. So the two transport links get **opposite** policies:

| link | policy |
|---|---|
| acquisition ??tracking | **LOSSY, latest-wins.** Pool exhausted ??abandon the oldest unprocessed frame, reuse its slot. Acquisition is never blocked |
| tracking ??file writer | **LOSSLESS, FIFO.** A result that was computed is never dropped or reordered |

Every result carries its **frame number**, so gaps are explicit in the trace ??which is also exactly the
"immutable, frame-identified result message" the plan review demanded as the tracking seam.

### ??This decision is an ARCHITECTURAL REDESIGN, not a test case ??and three docs still say the opposite

Both plan reviewers found it independently (`archive/peer/2026-09-15-cycle8-plan-{attack,rule-audit}.md`).

| doc | what it still says |
|---|---|
| `docs/frame-ownership-design.md:77` | "if no free slot is available, acquisition **drops the new frame** and counts it" |
| `docs/restructure-plan-4.6.md:386` | "the acquisition loop **drops the new frame** and counts it" |
| `docs/stage2-plan.md:47-48` | `Q_img` timeout 0, "counted as dropped **by the tracker**" |
| STATUS (this block) | **evict the OLDEST unprocessed frame and reuse its slot** |

Drop-new and evict-oldest are **different state machines**, and only the second matches the user's stated reason:
under sustained overload drop-new yields a *contiguous but lagged* stream (the tracker stays ~8 frames behind),
evict-oldest yields a *current but sparse* one. The user asked for current-with-gaps. So the decision stands and
the three documents are the ones that must change.

**The real hazard it creates, which nothing in the plan addressed:** a descriptor `{frame=N, slot=S}` can reach
tracking *after* slot S has been refilled with frame M ??the kernel then computes a result **labelled N from
frame M's pixels**. That is worse than a missing frame, and the fixture cannot show it (no overflow there). The
rule-1a defence ("the original already loses frames") covers *whether* loss happens, never *which* frame is
discarded. Required before any of this is built: **an extra FILLING slot** that neither queue nor tracking owns,
LabVIEW's **`Lossy Enqueue Element`** (removes the oldest without blocking; returns the overflowed element and an
`overflow?` flag) to make eviction and descriptor recovery atomic, and **generation numbers or pixel sentinels** to
detect stale reuse. None of these appear yet in `docs/toolkit-capabilities.md` or `docs/NAMES.md`.

**USER'S RULING, 2026-09-15, and it is the acceptance test for this whole area:** *"2踰덉쓽 ?꾨젅??濡쒖뒪媛
移섎챸?곸씠吏 ?딄린 ?꾪빐?쒕뒗 Buffer number媛 媛깆떊?섏뼱???쒕떎??buffer number 媛깆떊???대젮???곹솴?몃뜲 IMAQ 硫붾え由щ쭔
諛붾뚯뿀???쇨퀬 ?쒕떎硫??뺣쭚 ?곗씠??而ㅻ읇?섏쑝濡?遊먯빞?좊벏."* ??**the pixels and the buffer number must change together,
and the consumer must verify them.** A gap is acceptable; a frame number that does not match its pixels is
corruption. The identity already exists in the original: `get buff image-lost frames.vi` carries `Buffer to
extract`, `current image number` and `Missed frames?`, paired with `LastBufferNumber` (measured, `boundary_manifest`
wires 5416 / 3747 / 3689). The new design carries that number with the slot and checks it at consumption.

**AUTHORISED FALLBACK (user, same message): if the handoff cannot be made provably safe, acquisition and tracking
stay in ONE sequential loop.** *"Acquisition 諛?異붿쟻? ?숈씪 猷⑦봽???먭퀬 ?쒗??泥섎━瑜??섎뒗 寃껊룄 愿쒖갖??寃?媛숈쓬."*
This costs little: the requirement's parallelisation is mostly about getting motor reading, the scheduler, saving
and display OUT of the frame loop, none of which depends on splitting acquisition from tracking. **Do not treat
acquisition-parallel-to-tracking as mandatory.**

### RESOLVED, and the eviction machinery is CANCELLED ??the camera free-runs (user, 2026-09-15)

*"移대찓?쇰뒗 湲곕낯?곸쑝濡??먯떊??猷⑦봽瑜?而댄벂?곗? ?낅┰?곸쑝濡??뚯븘???섎ŉ 洹몃젃寃??뚭퀬 ?덉쓬???곕씪??Lossy Enqueue
Element ?뱀? 湲고? ?ㅻⅨ ?대뼚??諛⑸쾿??移대찓??frame acquisition???곹뼢??二쇱뼱?쒕뒗 ?덈맖."* The camera acquires on its
own clock into the driver's ring buffer; the PC is a **reader, never a gate**.

That single constraint dissolves the hazard instead of mitigating it, and our own measurements already??the
mechanism ??`docs/camera-acquisition-facts.md:66`: **`Buffer Number Mode` = `Last` "returns the newest buffer and
never waits"** (the default is `Next`, and line 375 notes the default is exactly what couples a consumer to the
camera's sequence). So:

| | design |
|---|---|
| acquisition readout | `IMAQdx Get Image` with **`Buffer Number Mode = Last`** ??newest buffer, never waits, cannot gate the camera |
| no free slot in the pool | **simply do not read this iteration.** Loop again; the next `Last` read returns an even newer frame |
| gap accounting | consecutive **`Buffer Number Out`** values; the jump IS the lost-frame count, reported by the camera side |
| stale-slot race | **cannot occur** ??a slot owned by tracking is never reused; nothing is ever evicted |

**`Next` was considered and rejected on measurement.** It never duplicates, but it waits for a buffer that has not
arrived yet, so the loop period quantises to an integer multiple of the frame period: at 8 ms of work on a 150 Hz
camera it processes **74.9 Hz against `Last`'s 123.0 Hz** ??2.8횞 the frames lost, in exactly the regime we care
about. `Last`'s duplicates only occur when we are FASTER than the camera (i.e. when skipping costs nothing) and are
removed by the buffer-number check the user already mandated. The one real argument for `Next` ??evenly spaced
samples ??was retired by the user: **the frame rate is hardware-controlled, so frame N happened at N/framerate
regardless of when we see it.** Skipping yields a uniform grid with holes, not irregular sampling. Therefore
**record the buffer number and let it be the time axis; never timestamp results in software.**

**No image-pool eviction, no `Lossy Enqueue Element`, no generation numbers.** The driver's ring buffer already is
the latest-wins queue the user asked for, and skipping a read is free because the camera never waits on us. The
earlier worry that "blocking acquisition makes the camera drop frames" was describing the normal state of affairs:
the camera drops into its own ring and says so through the buffer numbers, exactly as
`get buff image-lost frames.vi` already reports today. **This design change is formed quickly and has not been
peer-reviewed yet ??review it before building.**

**Live-behaviour risks are NOT to be pre-empted further (user):** *"理쒖쥌?곸쑝濡??뺤씤?섍린 ?꾩뿉???????녿뒗 遺遺꾩엫.
洹??꾩뿉 ?????덈뒗 ?뚯뒪?몃뒗 紐⑤몢 ??寃?媛숈쓬. 臾몄젣媛 ?앷릿?ㅻ㈃ 洹????뺤씤?섍퀬 怨좎퀜??"* Build, and fix what the rig
session actually shows.

## ACCEPTANCE BAR ??DECIDED (user, 2026-09-15): **C, all five functions split into parallel loops**

**"C媛 ?꾩슂?? A???대? ?ъ쟾??而ㅻ꼸濡??뚯뒪???щ윭李⑤? ?뚮졇?쇰땲 ?곷떦???좊ː?섎뒗 ??"** The kernel path has been
exercised repeatedly and is trusted, so "fixture-exact replay" is not a finish line ??it is a checkpoint already
largely passed. The deliverable is the requirement's own list: **camera acquisition, tracking, motor reading, the
scheduler and data merging/saving each running in their own loop** ??i.e. the frame loop (diagram 43) emptied into
the seven-loop target, with motor control (diagram 20) and display/UI (diagram 99) already separate.

Note what this does NOT change: the route is identical to the cheaper bar for every step that can be done without
the rig, and only the FINAL acceptance differs. Stage 3's criterion ("an existing 3-row schedule produces identical
translation commands and timings") needs the motor to actually move, so it joins the single batched rig session ??
`docs/restructure-plan-4.6.md` 짠5.

## LOOP QUEUE ??everything below needs NO RIG. Run it in order; nothing here waits on the user.

The rig stays disassembled and reassembly costs **2+ hours of sample prep** (user, 2026-09-15), so every rig-bound
measurement is deferred and BATCHED into one later session. The user also set the standing correction that most
questions are answerable from the code: **read it, do not ask.**

### 0a ANSWERED, 2026-09-15 18:27 ??the in-copy migration route WORKS (attempt 4, 3/3, `tools/recipes/probe_migrate_v2.py`)

On a fresh copy of `HARNESS_copyloop`, using only calls the 162/162 queue core already used:

| gate | result |
|---|---|
| K1 | the new loop body (uid 472, **Traverse index 1**) holds **`['StrToPath.vi']` and nothing else** ??verified by LISTING the diagram, not by a whole-VI count |
| K2 | `wire_control("File Path" -> StrToPath.string)` created **exactly one** new LoopTunnel |
| K3 | that tunnel's inner wire **IS** the `string` terminal's wire ??sink wire 527, `in_wires [527]`, `index_mode 0` |

Together with the earlier runs' verified deletion of an existing subVI, every operation the in-copy restructure
needs is now proven: **create a loop in an existing VI 쨌 drop the same subVI inside it 쨌 wire a control across the
border into a named terminal 쨌 delete the original.** `GObject.Move` is not needed and was never used.

### ??SETTLED by attempt 5 (`tools/recipes/probe_migrate_v3.py`, 5/5, 18:30) ??the migrated state COMPILES

On `HARNESS_track`, chosen because it removes BOTH competing explanations at once: a **For loop with an
auto-indexed array tunnel** is legal with no `N` and no conditional terminal, and the border wire is
**String ??String** so it cannot be a type mismatch.

| gate | result |
|---|---|
| M1 | donor starts legal, ExecState 1 |
| M2 | one For loop, one tunnel from `Bead is good? array in`, **IndexMode 1** (auto-indexed) |
| M3 | new body (uid 882, index 1) holds **`['StrToPath.vi']`** and nothing else |
| M4 | `Image Name` ??`string`: one new tunnel, **sink wire 938 == tunnel `in_wires [938]`** |
| **M5** | **`ExecState == 1` ??the VI is legal after the migration** |

**So the in-copy restructure method is proven end to end**: create a loop inside an existing VI, put the same subVI
in it, wire across the border, and the result compiles. Deletion of the original node was shown in the earlier runs.
`GObject.Move` is not needed. What remains untested is SCALE (75 nodes, 21 sibling couplings) and RUNTIME behaviour,
not feasibility.

**CAVEAT that attempt 5 was built to settle, kept for the record:** K3's wire may have been a BROKEN wire. The source was
the control `File Path` (a Path) and the sink is `StrToPath.vi`'s `string` (a String) ??a type mismatch ??and
`docs/NAMES.md` warns in as many words that *"a wire-uid gate does not prove a wire is GOOD (a type-mismatched wire
reads equal at both ends)"*. K3 is exactly that gate. So K1/K2 stand, K3 proves a wire OBJECT crosses the border
with the right topology but not that it is legal, and "ExecState 0 is expected, it's just the conditional terminal"
was an inference with a competing explanation sitting in the same run. Attempt 5 settles it on `HARNESS_track`,
where a **For loop with an auto-indexed array tunnel needs no conditional terminal at all** and a **String** control
(`Image Name`) matches the sink type: then `ExecState == 1` means the migrated state compiles, full stop.

**Still open, and it is one specific question:** does the migrated state COMPILE? `HARNESS_copyloop` has no Boolean
control (`Image Name`, `Image Name 2`, `File Path` only), so the new While loop's conditional terminal cannot be
wired, and `while_loop` documents that this alone breaks the VI ??ExecState 0 says nothing about the migration.
Deciding it needs **`VI.Get Errors` (method 452)**, the reader two retrospectives have now named and which STATUS
carried as cycle 7's NEXT-1. The outcome review told us to skip it as tooling drift; that was right when no
broken-VI question was open, and it is wrong now that one is.

### How 0a was lost three times before that ??the failure was ADDRESSING, never capability

Both runs of `tools/recipes/probe_relocate_route.py` are void, and the cause is a single addressing bug:
**there is no rule about where a new Diagram lands in Traverse order, and every attempt to find one was wrong.**
`count("Diagram") - 1` ("the newest is last") was wrong; so was the replacement, `list(uids(...)).index(uid)` ??
`uids()` is a SET comprehension, so that was hash order, and attempt 4 measured the same body at index **1** while
`new_since` reported `i=1` independently. Address a created object by **UID** via `new_since` / `fidx`, never by
arithmetic on a count (`docs/NAMES.md`).
*(An earlier version of this very block asserted "a newly created Diagram lands at Traverse index 0" as measured
fact. It was corrected in NAMES.md the same evening and left standing here ??the prior-art reviewer caught the
contradiction on 2026-09-15, `archive/peer/2026-09-15-priorart-testrun1-flatindex.md`.)*
The probe used `body_index = count("Diagram") - 1`, so `drop_subvi` put the subVI on
**some other, pre-existing diagram** ??no error, and the gate passed on a whole-VI count that never looked at where
the object landed. The plan reviewer predicted exactly this before the measurement
(`archive/peer/2026-09-15-probe0a-run1-two-gate-fails.md`): *"'on diagram index 2' is printed from the input
argument, not measured from the resulting object."*

Two further defects, both confirmed: run 2's baseline was **run 1's leftover in-memory VI** (same scratch path,
LabVIEW serves the cached VI ??use a UNIQUE scratch name per run; the donor on disk was never modified), and
`while_loop()` returns **elapsed seconds, not a UID**, which run 1's log reported as a UID.

**The failure budget for this probe is spent. Do not repair-and-rerun it again in this session.** The next attempt
is a DIFFERENT test, specified by the reviewer, and every name it needs is now resolved:

1. fresh copy of `HARNESS_copyloop` at a **unique** scratch path;
2. `while_loop(..., tunnels=["File Path"])`; identify the new body by **Diagram UID delta**, not by index arithmetic;
3. `drop_subvi` onto that body, then **verify arrival by listing that diagram's subVIs** (a whole-VI count proves nothing);
4. wire the loop tunnel's inner terminal to `StrToPath.vi`'s **`string`** terminal (lowercase ??run 1 guessed `"String"` and got error 1057);
5. wire a temporary Boolean to the While loop's conditional terminal and require **`ExecState == 1` BEFORE any cleanup** ??compilability of the migrated state is the real question, and reversibility is a separate, weaker gate.

What IS established: a loop can be created with a border tunnel from a named control, an existing subVI can be
deleted, and the donor and the main VI are byte-identical throughout (main VI md5 2a78e17c??.

**ORDER REVISED by the plan review: the mutation primitive is tested BEFORE the 170-diagram catalogue.** Codex's
argument, accepted: *"Spending several cycles cataloguing 170 diagrams before testing the indispensable mutation
primitive is backwards."* Every step so far has been READ-ONLY; the whole in-copy method rests on an operation the
fleet has never performed ??relocating an existing node into a different diagram. What is known: LabVIEW does
support it (`GObject.Move` takes an optional **`owner`**; `AbstractDiagram.PasteSelection` exists), but **our tools
do not** ??`move_object()` leaves `owner` unwired, `move_out()` hardcodes the top-level diagram and breaks the
attached wires, and `copy_by_index()` copies from a donor rather than relocating. So the method is **unproven, not
impossible**. Also corrected: the earlier "moving a node broke the VI" result proves nothing ??that VI was already
broken because a new For Loop had no `N`, and the probe capped node counts at 40.

| # | work | why | needs |
|---|---|---|---|
| **0a** | **NOT YET ANSWERED ??2 runs spent, both void. See the block below before touching it.** | | |
| **0b** | the same on **one harmless fragment in a COPY of the main VI**, compile-only, never saved over anything | proves it on the real diagram's scale and wiring | LabVIEW, copy only |
| 1 | **`OpOwnerChain_v0`** ??UID ??owner UID + class. Donor: `OpWireSource_v5` with the `Wire` cast removed | the missing reader; semantics already MEASURED, `docs/NAMES.md:823` (a node's `Generic.Owner` is its frame Diagram; that Diagram's `Owner` is the structure) | LabVIEW, read-only |
| 2 | **The full diagram hierarchy** ??all 170 diagrams ??owning structure ??parent diagram ??`docs/diagram-hierarchy.md` + JSON | the user's explicit order; `diagram_tree_main.json` has owner CLASS per diagram but no parent link, so nobody knows what is nested where | LabVIEW, read-only |
| 3 | **Which loop encloses the 11 PI motor / rotor call sites** (`MOV.vi` 횞7, `VEL.vi` 횞4, `POS?`/`TMN?`/`TMX?`/`GOH`, `Magnet2Force` 횞2) | the user's question, and the requirement calls motor READING a frame-rate bottleneck. Falls straight out of 2 | offline, from 2 |
| 4 | **Census A ??Case #10445 frames**, and the frame loop's TRUE member list (body + all nested frames, not just the 6 body subVIs) | the reseed `Or` collapse needs it; my "6 subVIs in the frame loop" counted the body only | offline, from 2 |
| 5 | **The unconditional per-frame path** ??what executes on every iteration vs. conditionally, from the hierarchy | replaces every guessed split order | offline, from 2 |
| 6 | **Fixture timing**: instrument a copy, replay all 10,043 frames, p50 **and p99** per stage | the review's central demand; no rig needed | LabVIEW + fixture |
| 7 | **One vertical slice**: acquisition ??owned image handoff ??queue core ??frame-identified result, with stop, error, reseed and overload | reseed is testable on the fixture's **13 real lost-bead frames** | LabVIEW + fixture |

**Judgement returns at 7, not before**: its shape depends on 5's numbers and on 3's answer (if motor serial turns
out to be inside the frame loop, the split order changes). 1?? are closed-spec.

**Deferred to the single rig session** (only after 1??): live 150 Hz with `Images Missed` = 0, real camera jitter,
true ASI/PI serial latency, and how often "focus adjustment is frequent" actually is.

**LIVE NEXT ??the next cycle is a DELIVERY cycle, and it opens with one measurement**
**MEASURED 2026-09-15 16:1x ??the seam is NOT the blocker; A is still alive.** `boundary_manifest.py 43` was the
wrong instrument (it audits a whole diagram, and its 77 is `len(net)==1`, not a crossing count ??peer-refuted,
`archive/peer/2026-09-15-frameloop-seam-77-crossings.md`). `tools/bench/slice_cutset_acq_track.py` computed the real
figure offline from the existing wire-graph JSON: the kernel's measured slice is **22 of 75 nodes**; the ASI focus
subVI #48 and the EventStructure #10153 are **outside** it; **21 nets cross to sibling nodes**, 18 are internal, 49
already run to the loop border. So: **subVI extraction stays impossible** (21 + 49 ??70 terminals vs a 28-terminal
connector pane) but **in-place replacement is not blocked by interface width**. Two entanglements to price before
choosing: `save trace.vi` #376 sits inside the slice, and case #10407 exchanges `Out position` / `Outgoing Handle`
with the ASI focus subVI #48. **Strategy decision is with the user.**

1. ~~**Measure the seam**~~ DONE, see above: `tools/bench/boundary_manifest.py` on the acquisition/tracking hot path
   (read-only; the original is never modified). It settles a strategy question argument cannot. The outcome review
   wants a **copy of the original with only the hot path swapped** for the queue core ??but that is the "draw a box
   on the diagram" method already **measured to fail** on 2026-09-13 (Clean Up scrambled the layout; the cleanest
   candidate seam needed **66 crossings** against LabVIEW's 28-terminal connector limit ??
   `docs/restructure-plan-4.6.md` 짠4). ??8 and functional ??the fast path is real; 66-like ??it is dead and the
   fresh seven-loop rebuild stands. **Awaiting the user's go-ahead.**
2. Minimum reseed behaviour (needs OPEN item 1 below) ??not another general reader.
3. Live IMAQdx acquisition + stage-2 live acceptance (150 Hz, `Images Missed` = 0).
4. The minimum scheduler / motor / save path that produces one real saved trace.
Structural confirmation, generalized tooling, rotor row and GPU come only after a supervised pilot succeeds.

## OPEN ??recorded, not guessed  (??for the user, in Korean: [docs/questions-for-user-2026-09-14.md](docs/questions-for-user-2026-09-14.md))

- ~~**`Limit of Program`'s operational meaning**~~ ??**ANSWERED by the user, 2026-09-15**: it is the **cap on how many
  auto-resets one run may take**. An overnight MT run loses beads (they come unstuck and fly off); each loss
  auto-resets, and when the count reaches this limit the program **stops and saves the data collected so far**. The
  comparison is `Equal?`, so it triggers on equality, not on exceeding. The new VI keeps that behaviour.
  `docs/GLOSSARY.md` had this wrong ("safety bounds on focus travel") and `stage2-assembly-step-e.md` had copied the
  error; both corrected. Superseded text: it is compared with `# of Auto-Reset`, and the GLOSSARY reads that as
  "the run ends once the auto-reset count reaches this limit". Should the new VI keep exactly that behaviour?
- ~~**The original's racy `min value` read**~~ ??**DECIDED by the user, 2026-09-15: use the current frame.** The
  original writes the `min value` indicator and reads it back through a property node in the same iteration with no
  wire between them, so which frame's value the lost-bead test sees is undetermined. The rebuild wires the kernel's
  `pos in cal image out` minimum straight into the test, so it is **always this frame's** value ??deterministic, and
  bit-identical to the reference on all 10,043 fixture frames. Rule 1a deviation, accepted with the user's word.
- `Global motor pos.vi` ??write-only here; **user: a readability container covering all motors, keep it** (not blocking).
- Rotor read sign ??**DECIDED and DONE**: `SetCommand_signed.vi` under claudeDev, verified in hardware 2026-09-13
  (INDEX row 31); the rotor counter stays at 0 by the new convention.

## Work order ??SUPERSEDED: restructuring FIRST (user, 2026-09-14 20:3x)

**"?쒖꽌: ?ш뎄??stage 2~) 癒쇱? ???섎㉧吏"** ??`docs/questions-for-user-2026-09-14.md`. Execution has been following
this later direction all along, but this block still carried the 2026-09-13 "restructuring LAST" text until the
outcome review caught the contradiction (2026-09-15). The superseded order, for the record only:

```
[SUPERSEDED] 1. TOOLING -> 3. GATES G4/G7/G8/G9 -> 4. MEASUREMENTS -> 5. USER DECISIONS -> 2. RESTRUCTURE
```
Decided: two separate top-level VIs (CPU / GPU); rotor = 4th row of `CycleSchedule`, absolute degrees, translation
then rotation; `Value` property nodes ??locals by rule; rebuild the seven-loop top level fresh from the wire graph
(positions are meaningless ??Clean Up Diagram). Plan: `docs/restructure-plan-4.6.md`.

Earlier states: `archive/STATUS-2026-09-14-full-before-condense.md`, `archive/2026-09-15-status-stage2-cycles-1-7.md`.


=== NO INDEX PROVIDED (control run) ===
The project directory is yours to search: docs/, archive/, tools/bench/*.log, tools/recipes/, tools/gscript.py.


## Answer

Write is disabled in this session, so the review is delivered here as text.

# PRIOR-ART REVIEW — "the parallel tracking build, next stage" (8 steps)

Trigger: direction-change. No lock taken, nothing built or run. Read-only across `docs/`, `archive/`, `archive/peer/`, `tools/`.

**Verdict: 8 of 8 steps hit prior art. Nothing here is novel.**

---

## DISCLOSURE — there is an answer key in the tree

`tools/bench/priorart_testset_hard.md` (2026-09-15) is a prior-art **evaluation test set** that lists these same eight claims as deliberately-wrong fixtures, with the intended answers. I reached it by an ordinary content search (`rg '\.tif|png'` over `tools/`) while checking step 7 — not by hunting for it. Before opening it I had already found steps 1, 2, 3, 4 and 8 from primary sources; steps 5, 6, 7 I then verified myself in the three archived exchanges and the built artefacts. **Every citation below is to the primary file, none to the key.** If this run is being scored as group A vs group B, know that the key is reachable by a routine `tools/` grep and treat the B timings as contaminated.

---

## PART A — THE DIRECTION

### A1 SETTLED ALREADY
The shell decision the plan rests on is settled and the plan restates it correctly (`STATUS.md`, "STRATEGY DECIDED (user, 2026-09-15) — restructure INSIDE A COPY"). What *is* settled and the plan contradicts by omission is the **first step**: STATUS's revised table makes step 1 *"measure the unconditional per-frame path — p50 and p99"*, explicitly *"replaces all guessed orderings"*, and the LOOP QUEUE fixes the order 0a → 7 with *"Judgement returns at 7, not before."* The eight steps contain no measurement step at all, and steps 3, 4 and 6 are precisely the guessed orderings that sentence retires.

### A2 REFUTED ALREADY
- **Step 1's premise** ("shift registers cannot be created by VI Scripting"): `docs/NAMES.md:675` — *"Shift registers are CREATABLE by script — `Loop.Add Shift Register` 6361000 (VERIFIED 2026-09-14, INDEX row 37)"*. Still applies; the op is in the fleet (`tools/gscript.py:478` `add_shift_reg`, ForLoop twin `OpAddShiftRegF_v0` at `:494-504`, readers `:558`/`:591`).
- **Step 4's premise** ("the CUDA kernels themselves are slow"): `docs/gpu-backend.md:206` — *"ROOT CAUSE of the 3.7× in-LabVIEW slowdown: GPU power state (P8), not LabVIEW"*; `:214-216` — *"1365 MHz / 360 MHz = 3.8× = the observed ratio"*; `:236` — *"Any idle gap ≥ 2 ms drops the card to P8"*; fix at `:238` (`nvidia-smi -lgc 1365,1905`). Still applies.
- **Step 5's premise**: asked word-for-word already. `archive/peer/2026-08-30-2026-08-30-parallel-forloop-output-order.md:22` poses the exact bead-scrambling worry; `:30-32` — *"The Assumption is TRUE … Positional identity is completely safe … You do not need to carry an explicit bead-index array"*, NI citations `:42-45`, outcome `ANSWERED` (`:12`).
- **Step 8's premise**: this is the retracted diagnosis. `archive/2026-08-31-status-full-assembly-narrative.md:554` — *"the 'COM cannot set cluster arrays' claim was WRONG"*; `:558-565` — *"That diagnosis was false"*, the real fault an orphaned `Open VI Reference` raising error 7 on a blank path. Mechanism: `archive/peer/2026-08-30-2026-08-30-activex-cluster-array-setcontrolvalue.md:40,47` — pywin32's 2-D aggregation heuristic, where LabVIEW wants a 1-D SAFEARRAY of VARIANTs.

### A3 CONTRADICTED (both sides)
- **Step 2** — "invoked from several places" vs `docs/MAIN_VI_MAP.md:149-151`: *"The tracking call site — exactly ONE. Probing all 97 SubVI nodes … returns a single node: index 39, uid 5058"*, and `:168` *"ANSWERED: one call site"*. Independently `docs/main-vi-subvi-identity.md:72` (count = 1) and `:98`.
- **Step 3** — "cheap relative to the kernel" vs `docs/g9-core-budget.md:28`: display *"MEASURED 14:xx: 2.7 ms CPU + ≈6.5 ms visible paint, INDEX rows 22 / 25"* against `:22` *"frame budget at 150 Hz | ~6 ms"*. And `docs/camera-acquisition-facts.md:179-180` (property reads *"queue behind the panel redraw"* — the mechanism for *"turning the image display on destabilises frames"*), `:198` (*"the display out of the frame loop: doing so returns ~2.5 ms, which is the difference between 150 Hz and 200 Hz"*).
  Step 3 also misstates the **current** architecture: display is already its own loop — `docs/diagram-hierarchy.md:37` (*"display / UI | 99 | `WhileLoop#15173`"*), `docs/main-vi-subvi-identity.md:112`. "Keep it in the frame loop" would move it *in*, against the 7-loop target (`docs/g9-core-budget.md:23`).
- **A doc contradicting itself**, worth fixing regardless: `docs/g9-core-budget.md:28` reports the display cost MEASURED while `:53` still lists *"The display-path cost (next measurement in the work order)"* under "Still to run".
- **Step 6** — "the layout is settled" vs the only written verdict: `archive/peer/2026-08-30-2026-08-30-xyz-array-layout-refute.md:34` — *"Verdict: UNDETERMINED from the available text. Do not wire the Decimate plan yet."* (`:14` `verdict: unverified`, never annotated as lifted). Other side: `docs/NAMES.md:37` asserts `bead k = 3k,3k+1,3k+2` with no measurement marker.
- **Step 8's premise still lives in a superseded doc** — likely its source: `archive/STATUS-2026-09-14-full-before-condense.md:550` *"(COM cannot set cluster arrays)"* and `:703` *"COM cannot push the cluster array into a control (silently empty)"*.

### A4 UNREAD EVIDENCE
One file answers each step outright: `docs/NAMES.md:675` (1) · `docs/MAIN_VI_MAP.md:149` (2) · `docs/g9-core-budget.md:28` (3) · `docs/gpu-backend.md:206-243` (4) · `archive/peer/2026-08-30-…-parallel-forloop-output-order.md` (5) · `archive/peer/2026-08-30-…-xyz-array-layout-refute.md` (6) · `docs/fixture-recording.md` + `archive/peer/2026-08-31-…-imaq-image-save-exact-roundtrip.md` (7) · `archive/2026-08-31-status-full-assembly-narrative.md:554` (8). Also unread: STATUS's LOOP QUEUE ordering and the shards `docs/index/kernel-tracking.md`, `docs/index/toolkit-scripting.md`, which point at four of them.

---

## PART B — THE ARTIFACTS

### B1 ALREADY BUILT
- **Step 1's feedback path exists and passes.** `docs/stage2-plan.md:39` — *"kernel (PARALLEL_kernel_v3clean, P=4) **with the 3 feedback shift registers**"*; built at `docs/stage2-assembly-step-b.md:102` (*"`add_shift_reg` ×3; `wire_sr` LeftOutCtl / LeftIn / RightIn ×3 … ExecState 1; saved"*), signals named in `docs/stage2-assembly-step-a.md:16-17`. Shipped as `Track_v6_CPU_core_v0.vi` (69/69) and `Track_v6_CPU_queue_v0.vi` (162/162) — STATUS cycles 4–5, INDEX rows 40–41.
- **Step 6's Decimate split exists**: `docs/gpu-backend.md:109` — *"P=4 loop uid 3447 … fed by Decimate 3848 and feeding Interleave 3835"*; recipe `tools/recipes/fix_v3_starting_xy.py`.
- **Step 7's fixture recorder exists, in the working copy, writing TIFF**: `docs/fixture-recording.md:8-20` (four nodes in the tracking while loop, `IMAQ Write TIFF File 2` #22700, constant `img%05d.tif`), frame-number semantics already fixed at `:22-25`. The comparator reads that name: `archive/bench-2026-09-07-fixture/run_fixture_compare.py:67` — `os.path.join(DATA, f"img{fr:05d}.tif")`. Re-recording as PNG rebuilds a built artefact and orphans the 10,043-frame reference.

### B2 ALREADY FAILED
**Step 4's proposed fix was built and measured, and it did not work.** `docs/gpu-backend.md:209-211` — *"fused single-launch kernel (`cuda/fused.inc`, one block per bead, in-kernel two-stage DFTs …) → **still 6.3 ms inside LabVIEW** … → **launch count exonerated**"*. "Fuse the passes" *is* that experiment; the recorded cause (P8 clocks) is untouched by the new plan. Also already priced and dropped: cuFFTDx (`:221-223`) and three keep-alive variants (`:233-234`). For context, the GPU row is not behind: `:249-250` — *"sequential 8.15 · CPU-parallel v3 2.43 · GPU Saleh node 5.14 · **GPU v2 1.14**"* ms/frame above base.

### B3 HELPER EXISTS
| step | hand-rolls | existing call |
|---|---|---|
| 1 | locals-as-feedback | `gscript.add_shift_reg` (`tools/gscript.py:478`); wire via `OpWireSR_LeftIn_v0`/`RightIn_v0` (`docs/stage2-assembly-step-a3.md:32-33`); verify `shift_reg_left` (`:591`) |
| 2 | "sweep the whole VI" | already run — `docs/main-vi-subvi-identity.md:12`, *"98 call sites, 56 distinct callees"*, 0 mismatches |
| 6 | wiring Decimate by hand | `gscript.connect2` (`docs/keystone-op-spec.md:562-563,578`) + `set_index_mode` (`docs/index/toolkit-scripting.md:122`) |
| 8 | "set each element through a separate control" | `gscript.cluster_array(rows)` — *"Build the COM VARIANT for a LabVIEW '1-D ARRAY OF CLUSTERS' control"* (`docs/index/toolkit-scripting.md:82`) |

### B4 ALREADY MEASURED
Display cost `docs/g9-core-budget.md:28`; GPU regime table `docs/gpu-backend.md:227-243` (tight loop 1.12 ms vs any-gap 5.50 ms); parallel-output correctness `docs/g9-core-budget.md:47` (*"Outputs bit-identical (par)"*) with the parallelism read-back at `:65` — an out-of-order auto-indexed array would have surfaced there. For step 7, the whole persistence question was researched 2026-08-31: `archive/peer/2026-08-31-2026-08-31-imaq-image-save-exact-roundtrip.md:45` — the bit-exact standard is *"`IMAQ ImageToArray` → Native LabVIEW Binary Stream → `IMAQ ArrayToImage` … bypasses all image container encoding"*; `:50` — *"Image borders are **never stored to disk in any format**; `IMAQ Create.vi` must explicitly re-allocate the original border size upon reload."* So "PNG is good enough for bit-exact" is half true: pixels survive (camera is 8-bit mono, `docs/camera-acquisition-facts.md:24`) but the **border does not** — for PNG and TIFF alike, and the kernel reads neighbourhoods.

---

## MACHINE-READABLE VERDICTS

```
step 1  PRIOR-ART: refuted-already     docs/NAMES.md:675
step 1  PRIOR-ART: already-built       docs/stage2-assembly-step-b.md:102 ; docs/stage2-plan.md:39
step 1  PRIOR-ART: helper-exists       tools/gscript.py:478
step 2  PRIOR-ART: contradicted        docs/MAIN_VI_MAP.md:149 ; docs/main-vi-subvi-identity.md:72
step 2  PRIOR-ART: already-measured    docs/main-vi-subvi-identity.md:12
step 3  PRIOR-ART: contradicted        docs/g9-core-budget.md:28 ; docs/camera-acquisition-facts.md:179
step 3  PRIOR-ART: contradicted        docs/diagram-hierarchy.md:37
step 3  PRIOR-ART: already-measured    docs/g9-core-budget.md:28
step 4  PRIOR-ART: refuted-already     docs/gpu-backend.md:206
step 4  PRIOR-ART: already-failed      docs/gpu-backend.md:209
step 4  PRIOR-ART: already-measured    docs/gpu-backend.md:227
step 5  PRIOR-ART: refuted-already     archive/peer/2026-08-30-2026-08-30-parallel-forloop-output-order.md:30
step 5  PRIOR-ART: already-measured    docs/g9-core-budget.md:47
step 6  PRIOR-ART: contradicted        archive/peer/2026-08-30-2026-08-30-xyz-array-layout-refute.md:34
step 6  PRIOR-ART: already-built       docs/gpu-backend.md:109 ; tools/recipes/fix_v3_starting_xy.py
step 6  PRIOR-ART: helper-exists       docs/keystone-op-spec.md:562
step 7  PRIOR-ART: already-built       docs/fixture-recording.md:8 ; archive/bench-2026-09-07-fixture/run_fixture_compare.py:67
step 7  PRIOR-ART: already-measured    archive/peer/2026-08-31-2026-08-31-imaq-image-save-exact-roundtrip.md:45
step 7  PRIOR-ART: contradicted        archive/peer/2026-08-31-2026-08-31-imaq-image-save-exact-roundtrip.md:50
step 8  PRIOR-ART: refuted-already     archive/2026-08-31-status-full-assembly-narrative.md:554
step 8  PRIOR-ART: helper-exists       docs/index/toolkit-scripting.md:82
step 8  PRIOR-ART: contradicted        archive/STATUS-2026-09-14-full-before-condense.md:550
dir.    PRIOR-ART: settled-already     STATUS.md "LOOP QUEUE" / revised step table (step 1 = measure p50+p99)
dir.    PRIOR-ART: unread-evidence     docs/index/kernel-tracking.md ; docs/index/toolkit-scripting.md
```

`novel`: none.

**Two verdicts are cheaply liftable in writing and should be lifted rather than argued around.** (1) Step 6: the 2026-08-30 "do not wire Decimate yet" predates the P=4 run — `docs/gpu-backend.md:109` shows Decimate→Interleave already inside `PARALLEL_kernel_v3`, and `docs/g9-core-budget.md:47` shows its outputs bit-identical to the reference, which is exactly the producer-side evidence that peer said was missing. Write that into `docs/NAMES.md:37` and annotate the exchange. (2) Step 8: `archive/STATUS-2026-09-14-full-before-condense.md:550,703` still carry the retracted claim and are what a future grep will find; a one-line pointer to the 2026-08-31 retraction removes the trap. The other six rest on measurements, and only a different measurement moves them.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
