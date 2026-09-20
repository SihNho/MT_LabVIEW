# priorart-testrun1-flatindex

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $2.9149  in 22 / out 18416 / cache-create 170953 / cache-read 1489746  (228s, 18 turn(s))
- **date:** 2026-09-15
- **outcome:** ANSWERED (231s)
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
PLAN UNDER REVIEW - the next cycle of the V6 parallelisation project.

CONTEXT. The acceptance bar is the full requirement in project-requirements/: camera acquisition, tracking, motor
reading, the scheduler and data merging/saving each running in its own parallel loop. The work happens inside a
COPY of the main VI, never the original.

WHAT I INTEND TO DO, and the reasoning behind each step:

1. ORDERING. Take the ASI serial read out of the frame loop FIRST, before anything else. The justification is in
   docs/camera-acquisition-facts.md, which states that kernel plus one serial round trip is 5.06 ms of the 6.00 ms
   budget and that moving the serial read and the display out returns about 2.5 ms - the difference between 150 Hz
   and 200 Hz. That is the largest single win available, so it goes first.

2. THE CENTRAL RISK. Everything downstream depends on an operation the fleet has never performed: relocating an
   existing node from the frame loop into a new loop inside the same VI. Before anything else is built I will
   establish whether LabVIEW VI Scripting can move a node to a different diagram, since if it cannot, the whole
   in-copy method collapses.

3. A NEW READER. Build `VI.Get Errors` (method 452) as an op: a VI path in, the compiler's error list out. Three
   consecutive ExecState-0 diagnoses were settled by inference when this reader would have answered them in one
   run, so it is the highest-value tool to add.

4. A REWIRE. Derive `OpOwnerChain_v0` from `OpWireSource_v5` by pointing the owner chain at a UID-addressed object
   instead of an indexed wire terminal. Concretely: rewire the reference of node uid 163 (Property `ClassName`) and
   node uid 1221 (To More Specific Class -> GObject) so that both read the `Owner` output of node uid 241 instead
   of wire 751, then delete the Wire-specific front section. Those are the two consumers of wire 751.

5. ADDRESSING. Where a recipe needs the Traverse index of a diagram or loop it just created, compute it directly -
   take `count("Diagram") - 1` for the newest diagram, since a newly created object is appended last.

Attack this plan on prior art only: has any of it already been decided, measured, built, tried and failed, or is
any cited fact contradicted elsewhere in this project's own files?


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
**a newly created Diagram lands at Traverse index 0, not at the end** (measured, `tools/bench/census_0a_names.log`;
written up in `docs/NAMES.md`). The probe used `body_index = count("Diagram") - 1`, so `drop_subvi` put the subVI on
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


=== PRIOR-ART INDEX (generated by tools/build_prior_art_index.py) ===
Each line states a conclusion, not just a topic. It is a POINTER, never the evidence: open any
file whose line looks relevant and cite it by line number.

# Prior-art index ??what this project already decided, measured, built and failed at

Generated by `tools/build_prior_art_index.py`. Each line states a CONCLUSION, not just a topic, so a reviewer can decide from here whether opening the file is worth it. Open the file for anything that looks relevant ??the line is a pointer, never the evidence.


## Archived peer exchanges ??slug 쨌 outcome 쨌 verdict

- `2026-08-28-agy-permissions-schema` [ERROR] ??adopted
- `2026-08-28-auto-error-handling-scripting` [ANSWERED] ??rejected
- `2026-08-28-auto-error-handling-scripting2` [ANSWERED] ??adopted
- `2026-08-28-containment-proof` [ANSWERED] ??adopted
- `2026-08-28-delete-unwire-undo-agy` [ANSWERED] ??adopted
- `2026-08-28-delete-unwire-undo` [QUOTA] ??adopted
- `2026-08-28-perm-allowlist-test` [ERROR] ??rejected
- `2026-08-28-perm-allowlist-test2` [ERROR] ??rejected
- `2026-08-28-perm-allowlist-test3` [ERROR] ??rejected
- `2026-08-28-perm-allowlist-test4` [ERROR] ??rejected
- `2026-08-28-perm-allowlist-test5` [ERROR] ??rejected
- `2026-08-28-perm-allowlist-test6` [ERROR] ??rejected
- `2026-08-28-perm-allowlist-test7` [ERROR] ??rejected
- `2026-08-28-perm-verify-after-install` [ERROR] ??rejected
- `2026-08-28-perm-verify-user-write` [ANSWERED] ??adopted
- `2026-08-28-quota-probe` [ANSWERED] ??adopted
- `2026-08-28-wire-indicators-api` [ANSWERED] ??adopted
- `2026-08-28-wire-silent-fail` [ANSWERED] ??adopted
- `2026-08-28-wrapper-smoke-codex` [ANSWERED] ??adopted (correct answer confirmed the brief loads and read-only holds)
- `2026-08-28-wrapper-smoke-test` [ANSWERED] ??adopted (correct answer confirmed the brief loads and read-only holds)
- `2026-09-05-com-run-hang-after-killed-client` [ANSWERED] ??accepted as 'unproven' ??the killed-client mechanism has no documentary support; 180 s is gscript's own watchdog, not a LabVIEW timeout; hidden modal 
- `2026-09-05-keystone-build-plan-attack` [ANSWERED] ??accepted: (1) the created node's class follows the referenced OBJECT (Term ref -> Term node; only a Control refnum gives Ctl) so 'node class as a stri
- `2026-09-05-m3-clicker-spec-attack` [ANSWERED] ??accepted in substance: single-point offset is not a transform (zoom/scroll/DPI) -> two-object calibration + Ctrl+0; extent probing dropped (GObject.Bo
- `2026-09-06-fp-control-creation-scripting-routes` [ANSWERED] ??actionable: Terminal.Create Control (input terminals), Constant.Change to Control, Control.Indicator (R/W), VI.Create from Data Type (variant -> Panel
- `2026-09-06-invoke-class-name-string-format` [ANSWERED] ??accepted (consistent with the creator's diagram: Class Name -> Method Class Name verbatim; Set Method with AllowAlternateNames=F): use 'VI Server:<Cla
- `2026-09-08-clfn-cluster-spin` [ANSWERED] ??H1 REFUTED by the machine (09:0x): the saved HARNESS_gpu.vi carries the cluster wire (CLFN t32 <- loader 'Array of cal clusters', wire 4329) and loads
- `2026-09-08-clfn-scripting-config` [ANSWERED] ??HYPOTHESIS, not yet verified on the machine (LabVIEW Wiki class dump): VI Server class CallLibrary (Generic>GObject>Node>GrowableFunction>CallLibrary)
- `2026-09-08-cuda-dll-slower-in-labview` [ANSWERED] ??being tested on the machine: phase split (chain 11) shows upload 0.34??.58 ms, kernels 0.96??.40 ms, readback 0.11??.18 ms ??every CUDA call uniformly
- `2026-09-08-vi-error-list-by-script` [ANSWERED] ??HYPOTHESIS (LabVIEW Wiki + NI forum): VI method 'Get Errors' 0x452 (private scope; SuperSecretPrivateSpecialStuff=True may be needed; outputs Errors, 
- `2026-09-09-clfn-build-op-plan` [ANSWERED] ??Approach endorsed; adopted the validation ladder: round-trip byte equality, read-back after Set, Prototype, Parameter Terminals count/types, save/relo
- `2026-09-09-clfn-create-and-configure` [ANSWERED] ??Creation by New VI Object (style 'Call Library Function Node', class CallLibrary) and the CallLibrary properties are confirmed; Parameter Info enum co
- `2026-09-10-opbuildcase-v1-ia-unwired` [ANSWERED] ??diagnosis CONFIRMED by the machine before the answer arrived ??wiring GC1.`Control Terminals` ??IndexArray.`array` by name (+1 wire, so `array` IS the
- `2026-09-13-gpu-portability-attack` [ANSWERED] ??DECISIVE ??it supplied the acceptance test that overturned the replacement claim
- `2026-09-14-autonomous-loop-plan` [ANSWERED] ??ACTED ON. Node.Label rejected as identity (correct: identity came from AbstractDiagram.SubVIs[] -> SubVI.VI Name, docs/main-vi-subvi-identity.md); the
- `2026-09-14-builder-leaves-artifact` [ANSWERED] ??RESOLVED by measurement the same morning (probe_builder_artifact.log): the artefact was the WALKER's junk Invokes (spec s33), not the builder's; net_m
- `2026-09-14-cast-route-research` [ANSWERED] ??ClassSpecifierConstant.Set Type 566EF800 / Class Name 566EFC02 exist, but a typed reference to the constant needs one seed cast -> ONE manually prepar
- `2026-09-14-castfree-ladders-execstate0` [ANSWERED] ??RESOLVED: the ExecState 0 was the walker's junk on the open target, not the ladder; with the self-purging walker both ladders compile (probe_castfree5
- `2026-09-14-castfree-ladders-fail1` [ANSWERED] ??superseded - see castfree-ladders-execstate0 and probe_castfree5.log (both ladders compile).
- `2026-09-14-castfree-reader-nondeterministic` [ANSWERED] ??RESOLVED: fresh nodes sat behind the walker's own junk Invokes in Nodes[]; purge fixed it (net_map, 2026-09-14).
- `2026-09-14-copy-harness-build-run1` [ANSWERED] ??explanation accepted (VDM Management.llb); rebuilt in the same session; cold first-copy cost measured (INDEX row 23).
- `2026-09-14-dispI-controlterminal-route` [ANSWERED] ??peer: no - a ControlTerminal is a Terminal, not a Node; Terminal.Connect Wire on the control's terminal is the clean route. Built as OpConnectCtl_v0 t
- `2026-09-14-dispI-wire-indicators-5001` [ANSWERED] ??probe (a) run: 'File Type out' -> 'Image' also 5001 -> H1 confirmed (the library's indicator lookup does not see a Vision Image Display); resolved by 
- `2026-09-14-display-bench-results` [ANSWERED] ??ACTED ON, and the peer's key cell decided it: disp4 (Draw with the indicator removed) ??construction +1.6 ms, Picture indicator write/paint **+6.5 ms 
- `2026-09-14-display-harness-build-run2` [ANSWERED] ??explanation accepted; fixes applied (exact 'Image Pixels (U8)', node_terms for terminal reads, save only when every step succeeded); run 3 built all f
- `2026-09-14-display-path-harness-plan` [ANSWERED] ??ACTED ON: two named conditions (panel closed = construction cost; panel open = representative, coalescing stated); `IMAQdx Get Image` removed from the
- `2026-09-14-g9-five-core-plan` [ANSWERED] ??ACTED ON: topology read from GetLogicalProcessorInformation (siblings (0,1)..(10,11) -> mask 0x3FF), A-B-A, gate > +10 % on the par kernel median; res
- `2026-09-14-image-display-harness-plan` [ANSWERED] ??ACTED ON: alternating frames kept; closed/open/closed2 conditions; the 'Synchronous Display on' cell is NOT built (no scripted route to the indicator 
- `2026-09-14-imaq-copy-handoff-plan` [ANSWERED] ??ACTED ON. (1) the per-Run harness (HARNESS_copy0/1) is kept but LABELLED "cold first-copy cost (includes B's first 1.3 MB allocation)"; a steady-state
- `2026-09-14-netmap-sweep-plan` [ANSWERED] ??see 'What was done with it' / STATUS.md 2026-09-14
- `2026-09-14-nodeterms-full-sweep-plan` [ANSWERED] ??ACTED ON: (a)/(c) node_terms now returns the node's own UID (the donor's node-UID reader survives in the op); the sweep verifies uid == Step-0 tree pe
- `2026-09-14-nodeterms-step3-wire-pn-name` [ANSWERED] ??explanation accepted; run 2 matched 'Broken?' and built cleanly (Property 5->7 after -2/+4, IndexArray 3->2, uid 240 untouched, ExecState 1 throughout
- `2026-09-14-opbuildpn-v1-fail1` [ANSWERED] ??fixed (Nodes[] index of the creator); OpBuildPN_v1 built and in use.
- `2026-09-14-opbuildpn-v1-fail2` [ANSWERED] ??fixed (Create Indicator on the source terminal 15, not the sink 10); OpBuildPN_v1 built and in use.
- `2026-09-14-opbuildpn-v1-plan` [ANSWERED] ??see 'What was done with it' / STATUS.md 2026-09-14
- `2026-09-14-opconnectctl-v0-plan` [ANSWERED] ??ACTED ON: verification order (invoke error -> display terminal wire present and ImageToArray wire intact -> ExecState 1 -> nothing else) implemented i
- `2026-09-14-opnodeterms-v0-plan` [ANSWERED] ??ACTED ON. (s4, strongest) each property on its OWN node with its own error chain: PN_N[Name] ??PN_S[Is Source?] ??PN_C[Connected Wire] ??PN_W[UID] cha
- `2026-09-14-oppanelwiring-v0-plan` [ANSWERED] ??ACTED ON. Taken: (s2) `Control.Terminal` moved to its OWN property node (PN1b) fed from PN1's `reference out`, so a failing Terminal row cannot defaul
- `2026-09-14-opreportnodes-execstate0` [ANSWERED] ??see 'What was done with it' / STATUS.md 2026-09-14
- `2026-09-14-opsubvis-v0-plan` [ANSWERED] ??ACTED ON before the build ran. Taken: (b) net_map check that the inner SubVI node carries exactly VIName/VIPath/UID before wiring the loop; (d) the Su
- `2026-09-14-opsubvis-v1-donor-netinfo` [ANSWERED] ??diagnosis CONFIRMED as leading; acted on. (1) No cast-free route to a nested Diagram-typed ref exists (peer search + NI docs) ??keep the Traverse?묲A?뭈
- `2026-09-14-optunnels-v0-plan` [ANSWERED] ??ACTED ON: IDs taken (Inside Terminals[] 6356000, Outside Terminal 6356001 = 'Outer Term' on this machine, IndexMode 6356C00, GObject.UID 632A813); per
- `2026-09-14-panelwiring-step6-execstate0` [ANSWERED] ??explanation accepted (recipe order: PN1b's required `reference` unwired before the check); fix = create PN1b after step 6; rebuilt as run 2.
- `2026-09-14-panelwiring-test-oracle` [ANSWERED] ??ORACLE error confirmed (term_err=0 + wire_err=1055 on every zero row = valid terminal, no wire; the donor OpNodeInfo_v0 really has six bare controls).
- `2026-09-14-private-method-attach` [ANSWERED] ??see 'What was done with it' / STATUS.md 2026-09-14
- `2026-09-14-rotor-baseline-zero` [ANSWERED] ??see 'What was done with it' / STATUS.md 2026-09-14
- `2026-09-14-stage2-shiftreg-primitive` [ANSWERED] ??**ACCEPTED and acted on.** The reviewer refused the plan and named a documented creation API,
- `2026-09-14-stale-nodes-snapshot` [ANSWERED] ??RESOLVED: same cause as castfree-reader-nondeterministic (walker junk); superseded.
- `2026-09-14-stall-alert-wrappers-false-positive` [ANSWERED] ??ACTED ON - three real defects found (see below); the wrapper reading of the alert stands but was made subordinate to a progress measure
- `2026-09-14-stall-record-silent-walk` [ANSWERED] ??explanation accepted; fix accepted (per-node progress line = real progress; purge loop now prints every 20 deletions; 90-s window kept fixed). Remaini
- `2026-09-14-stall-record-sweep-false-positive` [ANSWERED] ??diagnosis CONFIRMED (a COM client idles in LabVIEW's Run call; lifetime CPU is not a stall signature); design accepted with fixes: `$procs` IS populat
- `2026-09-14-walker-aborts-at-empty-node` [ANSWERED] ??superseded by the junk-Invoke finding (the walker's own junk, purged since).
- `2026-09-14-walker-zero-junk-anomaly` [ANSWERED] ??peer favours an in-memory aliasing of the loaded OpNetInfo instance (H2/H1), not a counting failure; decisive test = LabVIEW restart + one walk on a s
- `2026-09-14-wiregraph-frame-loop-plan` [ANSWERED] ??see 'What was done with it' / STATUS.md 2026-09-14
- `2026-09-15-frameloop-seam-77-crossings` [ANSWERED] ??REFUTED, and the refutation was right on both counts ??confirmed by measurement the same hour
- `2026-09-15-outcome-review-20260915` [ANSWERED] ??ACCEPTED; all 7 slugs fired. Two factual corrections were checked against the files and applied to
- `2026-09-15-peerps1-bomless-cp949-parse` [ANSWERED] ??PARTIALLY REFUTED, and accepted. The broad diagnosis (BOM-less UTF-8 decoded through the legacy ANSI
- `2026-09-15-restructure-in-copy-plan` [ANSWERED] ??PREMISE REFUTED, plan revised; the copied-original SHELL survives, the ORDERING does not. Verified
- `2026-09-15-retrospective-cycle8` [ANSWERED] ??ACCEPTED, with one observation corrected. Its sharpest finding is right: the approach should have

**Not annotated (148) ??slug only; open one if its name looks relevant:**
  2026-08-28-copy-nodes-between-vis, 2026-08-28-exit-for-loop-usage, 2026-08-29-decimate-resize, 2026-08-29-perm-scope-test, 2026-08-29-perm-scope-test2, 2026-08-30-2026-08-30-activex-cluster-array-setcontrolvalue, 2026-08-30-2026-08-30-parallel-forloop-output-order, 2026-08-30-2026-08-30-save-for-previous-version-range, 2026-08-30-2026-08-30-vilib-vision-detection-failed-prediction, 2026-08-30-2026-08-30-xyz-array-layout-refute, 2026-08-31-2026-08-31-classspecifierconstant-scriptable, 2026-08-31-2026-08-31-connector-pane-scripting-and-plan-review, 2026-08-31-2026-08-31-connector-pane-scripting-api, 2026-08-31-2026-08-31-createpropnode-reference-wiring, 2026-08-31-2026-08-31-fiji-raw-and-sequence-import, 2026-08-31-2026-08-31-gui-rule-hole-analysis-review, 2026-08-31-2026-08-31-imaq-image-save-exact-roundtrip, 2026-09-01-2026-09-01-fixturewrite-plan-attack, 2026-09-01-2026-09-01-opwireref-donor-plan-attack, 2026-09-01-loop-vs-graph-parallelism-labview, 2026-09-01-quickdrop-empty-cache-sendkeys, 2026-09-01-ringconstant-scripting-props, 2026-09-04-fp-object-creation-scripting, 2026-09-04-uitars-latest-version-vs-claude, 2026-09-06-connect-ladder-plan-attack, 2026-09-06-vi-block-diagram-property-id, 2026-09-06-vi-server-property-unique-ids, 2026-09-07-com-run-hang-opbuildpn-copy, 2026-09-07-tmsc-class-bootstrap-attack, 2026-09-08-fused-kernel-cufftdx-plan, 2026-09-09-clfn-create-crash-empty-paraminfo, 2026-09-09-clfn-scripted-node-broken-with-arguments, 2026-09-10-track-gpu-frame-1ms, 2026-09-12-asi-tiger-readonly-commands, 2026-09-12-camera-halving-attack, 2026-09-12-read-constant-value-scripting, 2026-09-12-restructure-plan-4.6-attack, 2026-09-12-scripted-subvi-extraction, 2026-09-13-astra-wiring-recovery-review, 2026-09-13-astra-wiring-recovery, 2026-09-13-scripted-diagram-selection, 2026-09-13-subvi-call-cost, 2026-09-13-tunnel-array-indicator, 2026-09-14-addshiftreg-fail1-branch-or-decline, 2026-09-14-addshiftreg-run2-rpc-unavailable, 2026-09-14-autonics-pmc-serial-command-vocabulary, 2026-09-14-autonics-pmc-serial-position-reply-format, 2026-09-14-copyloop-forloop-tunnels-plan, 2026-09-14-copyloop-gate-controlnames-fail, 2026-09-14-copyloop-linearity-plan, 2026-09-14-copyloop2-forloop-terminals-unnamed, 2026-09-14-hex-string-to-number-signed-default, 2026-09-14-implicit-property-node-linked-object, 2026-09-14-loopcast-seed-from-ni-example, 2026-09-14-loopcast-typed-terminal-seed-plan, 2026-09-14-loopcast-whileloop-seed-failed-prediction, 2026-09-14-nested-structure-creators-plan, 2026-09-14-opexitwhile-fail1-duplicate-terminal-names, 2026-09-14-opforloop-v1-fail1-indexmode-zero, 2026-09-14-oploopcast-v1-parallelism-plan, 2026-09-14-oploopcast-v1-t1-harness-par-no-loop, 2026-09-14-opnodelabels-v0-plan, 2026-09-14-opqueue-fail1-duplicate-error-out, 2026-09-14-opqueue-test-run-hang, 2026-09-14-opshiftregs-v0-elements-are-right-registers, 2026-09-14-opshiftregs-v0-fail1-loop-body-index, 2026-09-14-opshiftregs-v0-plan, 2026-09-14-opshiftregs-v1-fail1-wrong-index-array, 2026-09-14-rotor-first-read-timeout, 2026-09-14-rotor-negative-coordinate-test-plan, 2026-09-14-setcommand-signed-copy-plan, 2026-09-14-setcommand-signed-fail1-nodes-index-scope, 2026-09-14-setcommand-signed-fail2-test-injection, 2026-09-14-setcommand-signed-fail3-openpanel-hang, 2026-09-14-setcommand-signed-fail4-openpanel-after-restart, 2026-09-14-setcommand-signed-wirecontrol-plus2, 2026-09-14-stage2-a3-wire-shiftreg-plan, 2026-09-14-stage2-construction-plan, 2026-09-14-stage2-replay-path-array-control-route, 2026-09-14-stage2-step-b-replay-core-plan, 2026-09-14-stage2-step-b-revised-forloop-route, 2026-09-14-stage2-step-b-strtopath-simplification, 2026-09-14-stall-record-matrix-silent-block, 2026-09-14-strtopath-fail1-move-by-label-1054, 2026-09-14-wiresr-test-fail1-watchdog-modal, 2026-09-14-wiresr-test-fail2-imaqcopy-llb-path, 2026-09-14-wiresr-test-t8b-untyped-register-and-fplabels-dialog, 2026-09-15-case-frame-reader-property-ids, 2026-09-15-constant-vs-wire-source-uid-contradiction, 2026-09-15-core-fail1-border-wire-gate, 2026-09-15-core-fail2-array-tunnel-autoindexed, 2026-09-15-core-fail3-wrapper-used-while-seed, 2026-09-15-core-fail4-assembled-but-broken, 2026-09-15-cycle8-plan-attack, 2026-09-15-cycle8-plan-rule-audit, 2026-09-15-movebyindex-fail1-execstate0, 2026-09-15-opcaseframes-identify-before-delete, 2026-09-15-opcaseframes-last-orphan-node-1329, 2026-09-15-opcaseframes-multiframe-to-casestructure-downcast, 2026-09-15-opcaseframes-terminal-chain-must-go, 2026-09-15-opconstvalue-fail1-stale-op-cache, 2026-09-15-opconstvalue-fail2-broken-after-seed, 2026-09-15-opconstvalue-fail3-copied-pn-is-a-write, 2026-09-15-opconstvalue-numeric-void-variant, 2026-09-15-opconstvalue-run4-rpc-after-restart-no-labview, 2026-09-15-opconstvalue-run6-numeric-reads-none, 2026-09-15-opconstvalue-v1-recipe, 2026-09-15-opconstvalue-v1b-bstr-codepage, 2026-09-15-opconstvalue-v1b-recipe-flatten, 2026-09-15-opconstvalue-v1c-framing, 2026-09-15-opconstvalue-v1c-recipe-byte-route, 2026-09-15-opconstvaluen-fail1-634d004-is-radixvis, 2026-09-15-opconstvaluen-run2-typed-node-carries-data, 2026-09-15-opconstvaluen-scan-three-selectors-missing, 2026-09-15-opconstvaluen-v0-recipe-numeric-reader, 2026-09-15-opconstvaluen-v1-fail1-connected-wire-short-name, 2026-09-15-opconstvaluen-v1-recipe-wire-identity, 2026-09-15-optunnelread-removebadwires-ate-the-chain, 2026-09-15-optunnelread-v0-broken-after-retarget, 2026-09-15-opwiresource-fail1-uid-indicator-not-created, 2026-09-15-opwiresource-fail2-generic-owner-into-gobject-node, 2026-09-15-opwiresource-fail3-branch-wire-is-one-object, 2026-09-15-opwiresource-fail4-report-per-object-on-5000-wires, 2026-09-15-opwiresource-fail5-traverse-index-order-mismatch, 2026-09-15-opwiresource-v1-fail2-execstate-zero-after-readbacks, 2026-09-15-opwiresource-v1-lookup-terminal-census, 2026-09-15-opwiresource-v2-fail1-and-tunnelread-plan, 2026-09-15-opwiresource-v3-owner-uid-constant-3628, 2026-09-15-opwiresource-v4-wrong-owner-node-localised, 2026-09-15-opwiresource-v5-still-broken-after-rewire, 2026-09-15-priorart-ownerchain, 2026-09-15-probe0a-run1-two-gate-fails, 2026-09-15-queue-fail1-errno22-move-target-loaded, 2026-09-15-queue-fail2-errno22-copy-after-load, 2026-09-15-queue-fail3-guessed-timeout-name, 2026-09-15-reseed-vi-design-cycle7, 2026-09-15-retrospective-cycle7, 2026-09-15-retrospective-cycle9, 2026-09-15-stage2-cycle4-replay-core-recipe-v2, 2026-09-15-stage2-cycle4-replay-core-recipe, 2026-09-15-stage2-queue-core-recipe, 2026-09-15-stage2-step-c-queue-core-plan-v2, 2026-09-15-stage2-step-c-queue-core-plan, 2026-09-15-stage2-step-e-reseed-case-plan, 2026-09-15-strtopath-fail2-label-present-still-1054, 2026-09-15-strtopath-fail3-move-by-index-plan, 2026-09-15-strtopath-fail4-gui-save-of-broken-target, README

## Benchmarks (archive/benchmarks/INDEX.md) ??the question each row answered

- row 1 (2026-08-26) ??**Model quality at LabVIEW GUI control.** Same 3-step task (place For Loop, place numeric constant, wire it to `N`) by mouse/keyboard only, 40-tool-call cap, each model on its own blank VI. Which model finishes?
- row 2 (2026-08-26) ??**GUI-automation pipeline configurations.** Same wiring task through different pipelines (Claude-direct with probe = ceiling, grounder-assisted, 1x-pass accuracy vs probe ground truth).
- row 3 (2026-08-26) ??**UI-TARS-1.5-7B coordinate calibration.** Does the local grounder's coordinate contract hold on this Ollama build? Synthetic markers at known positions; zoom pass on a 5 px terminal.
- row 4 (2026-08-26) ??**Gemini GUI executor A/B (planned).** Claude plans, Gemini executes clicks; window-only capture, allow-listed actions.
- row 5 (2026-09-04) ??**Offline grounding: which pointer finds LabVIEW targets?** 19 targets (nodes, palette, menu, dialog) on 12 saved screenshots, same question to every model; ground truth = COM positions or verified clicks; hit = "would t
- row 6 (2026-09-04) ??**Live click: coordinates from data vs vision.** Three GUI micro-ops (drag node, palette place, context-menu item) on `GUIBENCH_v0.vi`, 3 trials each, revert between trials; M3 = COM position + one calibrated window offs
- row 7 (2026-09-04) ??**Where did session time go?** Transcript decomposition since 09-01: tool wait vs model latency, by tool type and by trigger (screenshot read, COM result).
- row 8 (2026-09-04) ??**UI-TARS speed-up attempt (failed).** Per-request `num_ctx`/`keep_alive` to fit the model on the 6 GB GPU.
- row 9 (2026-09-04 ??05) ??**GUI-executor model 횞 effort matrix (DONE).** Same vision-executor task (EXECUTOR_TASK.md: U1 move, U2 palette place, U4 context menu, U5 dialog; 3 trials each) run by one `claude -p` cell per (model, effort); pass/fail
- row 10 (2026-09-05) ??**M3v1 clicker toolkit verification.** The four vision micro-ops (move, palette place, context menu, dialog) done by `tools/lvclick.py`: coordinates from COM positions + a two-object-calibrated viewport offset, geometry 
- row 11 (2026-09-06) ??**Do our LabVIEW operations leak handles?** (user saw LabVIEW sluggish / '?묐떟 ?놁쓬'; the running instance had 32,480 handles) Six phases on a fresh instance: 20 reporter runs, a child process with clean exit, 10 open/revert
- row 12 (2026-09-07) ??Fixture acceptance of PARALLEL_kernel_v3 vs four-fold vs recorded .tra (10,043 frames)
- row 13 (2026-09-07) ??../bench-2026-09-07-gpu-reference/REPORT.md
- row 14 (2026-09-08) ??GPU DLL called from LabVIEW (row 3 of the three-way comparison): HARNESS_gpu vs HARNESS_base, 200 chained frames, 5 beads
- row 15 (2026-09-09) ??GPU DLL through OUR interface v2 (one CLFN on the raw IMAQ pixel pointer, built by script): HARNESS_gpu2 vs HARNESS_base, 200 chained frames, 5 beads
- row 16 (2026-09-09) ??GPU backend as a DROP-IN tracking kernel (GPU_kernel_v1, the kernel's own connector pane) vs PARALLEL_kernel_v3 in identical harnesses, 3 repeats x 200 chained frames, 5 beads
- row 17 (2026-09-10) ??TRACK_kernel_v1 ??ONE tracking subVI (kernel's own pane) with a Case Structure choosing CPU-parallel (frame 0) or GPU (frame 1) by the saved default of control `index`; built by script (OpBuildCase_v1 + OpMakeDefault_v0 
- row 18 (2026-09-10) ??**What the backend switch costs.** TRACK_kernel_v1 against the bare kernels in identical harnesses, 3 repeats 횞 2 backends 횞 200 chained frames, fresh LabVIEW per repeat, OS file cache warmed, contaminants logged
- row 19 (2026-09-12) ??**Camera identity, frame-rate ceiling, and the "first run halves the image" fault.** Driver called directly from Python via ctypes (`niimaqdx.dll`) after three attempts to drive NI's example VIs over COM each died behind
- row 20 (2026-09-13) ??**Will the GPU kernel still work if the PC / GPU changes?** (user: *"留뚯빟 ?닿? ?섏쨷???붾컮?댁뒪瑜???꺼??gpu 踰꾩쟾??諛붾먮떎怨??대룄 ?덇? 吏湲?留뚮뱾 而ㅻ꼸 ?ъ슜??臾몄젣媛 ?놁쓣源?* ??the same premise that split the codebase in two). Three questions measured rather than 
- row 21 (2026-09-13) ??**Does an array-returning reporter actually fix the O(n짼) toolkit bottleneck?** `report()` runs its op once per object, and ~990 ms of every run is the FIXED `Open VI Reference` cost on the 473 KB main VI ??so a 626-node
- row 22 (2026-09-14) ??**What does the main VI's image display route cost per frame, and where?** (work-order measurement 4; diagram 99's `IMAQ ImageToArray` ??`Flatten Pixmap.vi` ??`Draw Flattened Pixmap.vi` ??Picture indicator, called 'the s
- row 23 (2026-09-14) ??**What does a reference-safe image copy cost per frame?** (restructure gate G4 ??an IMAQ image handed to a slow consumer must be COPIED, because the ring buffer reuses the pixels behind a reference; NI: copy the acquisit
- row 24 (2026-09-14) ??**G9 core budget: does the tracking kernel slow down with one physical core fewer?** (restructure gate G9 asks for the normal core count AND one fewer). The accepted three-way method (`run_timing.py`: HARNESS_base / par 
- row 25 (2026-09-14) ??**Is NI's IMAQ Image Display control cheaper than the Picture route?** (the alternative row 22 left unmeasured). HARNESS_dispI = disp1's chain (Create ??ReadFile ??ImageToArray) + the image reference wired straight into 
- row 26 (2026-09-14) ??**What does IMAQ Copy cost in steady state, without the first allocation?** (row 23 gave only the cold upper bound; the cell was OPEN because no scripted For loop had an N). HARNESS_copyloop = copy1 + `IMAQ GetImageSize`
- row 27 (2026-09-14) ??**Which panel object does each of the main VI's 88 IMPLICIT `Value` property nodes touch?** (the last unreadable link in the panel map; the authoritative `Property.Linked Control` needs a typed reference no cast can give
- row 28 (2026-09-14) ??**Can the toolkit cast a generic GObject reference to a chosen class WITHOUT the one GUI act?** (the 'missing seed' that blocked shift registers, Loop Count, parallel instances, Linked Control). Claim researched and conf
- row 29 (2026-09-14) ??**What are the frame loop's per-frame state carriers (shift registers), exactly ??who initialises each, who reads it, who writes it?** (the 54 unresolved half-edges of docs/frame-loop-wire-graph.md; until now a name-pair
- row 30 (2026-09-14) ??**Does any loop of the original main VI already run parallel iterations, and did our scripted P=4 kernel loop really enable parallelism?** `OpLoopCast_v1` = the ForLoop cast + `Is Parallelism Enabled?` 6362004 + `Number 
- row 31 (2026-09-14) ??**Signed rotor position read** (user decision 18:3x: fix the read sign so the rotor zero can follow the hardware setup). The lab's Autonics driver `SetCommand.vi` parses the 8-hex-digit reply (`POS hhhhhhhh[CR]`, 32-bit 
- row 32 (2026-09-14) ??**Stage-2 toolkit gap 1: can the fleet create a While loop, with input tunnels by control name?** `OpWhileLoop_v0` = OpForLoop_v0 with erdosmiller `Create While Loop.vi` swapped in by script and ??the finding ??`Get Cont
- row 33 (2026-09-14) ??**Stage-2 toolkit gap 2: can a scripted While loop be made runnable and stoppable by a front-panel control?** `OpExitWhile_v0` = OpExitLoop_v0 with erdosmiller `Exit While Loop.vi` swapped in and its `Stop Condition` fed
- row 34 (2026-09-14) ??**Stage-2 toolkit gap 3: can the fleet build a working producer/consumer queue by script?** Four ops (`OpQueueObtain/Enqueue/Dequeue/Release_v0`, all from the OpExitLoop_v0 donor with erdosmiller `Create Obtain Queue / E
- row 35 (2026-09-14) ??**Stage-2 toolkit gap 4: an empty, runnable VI to author the new top level in.** `EMPTY_v0.vi` = HARNESS_copy0 stripped by script (3 subVIs + RBW, 3 controls, 2 orphan constants)
- row 36 (2026-09-14) ??**Can the fleet create loops INSIDE loops (the kernel's P=4 For loop inside the tracking While loop)?** `OpForLoopIn_v0` / `OpWhileLoopIn_v0` from the OpExitLoop_v0 donor: `Diagram in` from Traverse `Diagram`[index], inp
- row 37 (2026-09-14) ??**Stage-2 assembly step A: can the fleet CREATE a shift register?** (the kernel's x,y,z / good-flags / pos-in-cal feedback ??the one build-order line with no primitive behind it; rows 32??6's "every primitive exists" was
- row 38 (2026-09-14) ??**Stage-2 step A3: can the fleet WIRE a script-created shift register's three sides?** Four ops from one recipe (`OpWireSR_LeftIn/RightIn/LeftOutNode/LeftOutCtl_v0` = `OpWhileCast_v0` + a typed register chain `Loop.Shift
- row 39 (2026-09-14/15) ??**Stage-2 step B toolkit (overnight cycle 3): For-loop control tunnels, and the register ops on a FOR loop.** (1) `OpForLoop_v1` = `OpForLoop_v0` + the never-made wire `Get Controls.'Control Terminals' ??Create For Loop.
- row 40 (2026-09-15) ??**STAGE-2 REPLAY CORE: `Track_v6_CPU_core_v0.vi` ??does a script-built For loop with `PARALLEL_kernel_v3clean` and three shift-register feedbacks reproduce the original kernel path bit-for-bit on the fixture?** (docs/sta
- row 41 (2026-09-15) ??**STAGE-2 PRODUCER/CONSUMER CORE: `Track_v6_CPU_queue_v0.vi` ??the kernel path of row 40 moved into the pool-queue structure (plan items 1, 2, 4, 8), replay mode.** Pool = a queue of IMAGE REFNUMS (8 `IMAQ Create` in a F
- row 42 (2026-09-15) ??**`OpConstValue_v1.vi` ??can a diagram CONSTANT's value be read by script (`Constant.Value` 634AC00) and delivered to Python losslessly?** Build: Constant-typed seed control from NI's `Navigating Nodes and Wires.vi` PN 2
- row 43 (2026-09-15) ??**Reading a diagram's DATA by script: numeric constants, and which object feeds a wire ??the four reseed selector feeders of Case #5540.** `OpConstValueN_v0/v1` (value through a `DigitalNumericConstant`-typed `Constant.V

## Active documents

- `docs/GLOSSARY.md` ??Glossary
- `docs/MAIN_VI_MAP.md` ??Main VI map ??call graph, structure, and what it means
- `docs/NAMES.md` ??Verified name registry ??the exact strings the scripting APIs accept
- `docs/PRIOR-ART-INDEX.md` ??Prior-art index ??what this project already decided, measured, built and failed at
- `docs/REFERENCES.md` ??REFERENCES ??third-party code used, and what derives from it
- `docs/UITARS_GROUNDER.md` ??UI-TARS local grounder ??setup, calibration, and what it is for
- `docs/astra-gui-benchmark-2026-09-13.md` ??Astra GUI benchmark ??infrastructure failure, no performance result
- `docs/benchmark-report-2026-09-04.md` ??LabVIEW GUI ?먮룞??踰ㅼ튂留덊겕 蹂닿퀬????2026-09-04
- `docs/camera-acquisition-facts.md` ??The camera path: verified connector panes, and what they mean for frame loss
- `docs/diagram-hierarchy.md` ??The main VI's diagram hierarchy ??what is nested inside what
- `docs/fixture-recording.md` ??Fixture recording ??what was inserted into the working copy (2026-09-01)
- `docs/frame-loop-anatomy.md` ??The three While loops: what each one does, and where the frame budget goes
- `docs/frame-loop-wire-graph.md` ??Frame loop (diagram 43) ??functional units from the wire graph (measured 2026-09-14, offline)
- `docs/frame-ownership-design.md` ??Frame ownership, faults and shutdown ??gates G4, G7, G8
- `docs/g9-core-budget.md` ??G9 ??core budget (facts as of 2026-09-14; kernel-level gate PASSED 14:2x ??INDEX row 24; loop-level waits for stage 2)
- `docs/gpu-backend.md` ??GPU/CUDA backend ??plan, environment, findings (started 2026-09-07)
- `docs/gpu-portability.md` ??Will the GPU kernel still work if the PC / GPU changes?
- `docs/gui-click-benchmark.md` ??GUI click optimization ??benchmark design (2026-09-04, user directive: clicking first)
- `docs/instrument-libraries.md` ??Instrument libraries of the main VI ??what drives what
- `docs/keystone-op-spec.md` ??Keystone op spec ??`OpBuildNode_v0.vi` (2026-09-04, awaiting start signal)
- `docs/m3-clicker-spec.md` ??M3 clicker ??coordinates from data, verbs with self-verification (spec, 2026-09-05)
- `docs/main-vi-panel-map.md` ??Main VI front panel ??every object, by role
- `docs/main-vi-startup.md` ??Main VI startup ??the configuration block, frame by frame
- `docs/main-vi-state.md` ??Shared state between loops ??what actually crosses
- `docs/main-vi-subvi-identity.md` ??Main VI ??subVI identity per call site (measured 2026-09-14)
- `docs/motion-path-audit.md` ??Audit of the motor / stage serial path ??what is actually on it
- `docs/parallel-strategy.md` ??Parallelization strategy: loop-level now, graph-level only on evidence (2026-09-01)
- `docs/questions-for-user-2026-09-14.md` ???ъ슜??寃곗젙???꾩슂????ぉ ??2026-09-14 ?먯쑉 猷⑦봽 寃곌낵
- `docs/restructure-plan-4.6.md` ??Plan: restructure into `4.6 cpu parallel` and `4.6 gpu parallel`
- `docs/rotor-scheduler-design.md` ??Adding the rotor to the experiment scheduler
- `docs/rotor-sign-diagnosis.md` ??Why the rotor needs a baseline: the read-back parses as UNSIGNED
- `docs/stage2-assembly-step-a.md` ??Stage 2 ??assembly step A: the missing primitive (shift registers) + the first skeleton
- `docs/stage2-assembly-step-a3.md` ??Stage 2 ??assembly step A3: wiring a scripted shift register's sides (2026-09-14 23:0x, overnight cycle 2)
- `docs/stage2-assembly-step-b.md` ??Stage 2 ??assembly step B: the replay core `Track_v6_CPU_core_v0.vi` (overnight cycle 3, 2026-09-14 23:4x)
- `docs/stage2-assembly-step-c.md` ??Stage 2 ??assembly step C (v2): the producer/consumer core in REPLAY (overnight cycle 5, 2026-09-15 03:0x)
- `docs/stage2-assembly-step-e.md` ??Stage 2 ??step E: the reseed Case (plan item 3) ??overnight cycle 6, 2026-09-15 04:2x
- `docs/stage2-plan.md` ??Stage 2 ??acquisition + tracking loops + queue (construction plan, 2026-09-14 20:5x)
- `docs/subvi-call-cost-plan.md` ??What does a subVI call cost? ??ANSWERED: about 100 ns, i.e. free
- `docs/system-inventory-plan.md` ??System inventory ??understand and document BEFORE building
- `docs/t0-instrumentation-plan.md` ??Plan: attribute `t0`, the fixed per-frame cost ??design only, nothing executed
- `docs/toolkit-capabilities.md` ??What the op fleet can actually do

## Toolkit ??gscript.py functions (this is where 'a helper already exists' lives)

- `lv()` ??
- `op(path)` ??A cached VI reference. Op VIs are non-reentrant, so one reference each is correct."""
- `reset()` ??Forget the Application AND every cached op-VI proxy. Call after LabVIEW is killed/restarted mid-script:
- `_lv_gui(*args)` ??Invoke lv_gui.ps1 (no COM - safe from any thread)."""
- `cluster_array(rows)` ??Build the COM VARIANT for a LabVIEW '1-D ARRAY OF CLUSTERS' control.
- `_invoke(vi, method, *args, **kw)` ??Call any COM method under the SAME watchdog + hard cap as _run().
- `_run(vi, poll_s=6.0, hard_timeout_s=180.0)` ??Run the VI over COM under a watchdog AND an absolute time cap.
- `_err(vi, name="error out")` ??
- `report(target, cls)` ??Every object of `cls` on target's block diagram, as dicts with class/uid/pos/owner."""
- `report_all(target, cls)` ??Every object of `cls` on target's block diagram in ONE op run - the array-returning form of report().
- `subvis(target, diagram_index, purge=False, strict=True, **controls)` ??Every subVI call on ONE diagram of `target`, as [{uid, name, path}] in one op run - the cast-free identity
- `node_labels(target, diagram_index, strict=True, **controls)` ??The LABEL TEXT of every node on one diagram of `target`, as [{uid, label}] in one op run - cast-free
- `loop_cast(target, index, class_name="ForLoop")` ??A ForLoop-TYPED look at the `index`-th loop of `target` (Traverse class `class_name`, 'ForLoop' or
- `add_shift_reg(target, loop_index, y_position=120, class_name="WhileLoop")` ??CREATE a shift register on the loop_index-th loop of Traverse class `class_name`, returning the new
- `wire_sr(variant, target, loop_index, reg_index, node_index=None, ter)` ??Wire ONE side of the reg_index-th shift register of the loop_index-th `class_name` loop (OpWireSR_*_v0,
- `shift_reg(target, loop_index, reg_index, class_name="WhileLoop")` ??The reg_index-th element of Loop.Shift Registers[] of the loop_index-th loop of Traverse class `class_name`
- `shift_reg_left(target, loop_index, reg_index, left_index=0, class_name="Whi)` ??OpShiftRegs_v1: everything shift_reg() returns for the reg_index-th RIGHT register PLUS its LEFT side:
- `panel_wiring(target)` ??Every TOP-LEVEL front-panel object of `target` with its diagram terminal's wiring, in one op run:
- `node_terms(target, diagram_index, node_index)` ??Every terminal of Nodes[node_index] on the `diagram_index`-th Diagram of `target`, in ONE op run:
- `node_terms_uid(target, diagram_index, node_index)` ??(node_uid, rows) - node_terms plus the node's own UID even when it has no terminals (0 = index out of range)."""
- `tunnels(target, index)` ??The `index`-th LoopTunnel of `target` (Traverse 'LoopTunnel' order - an access index, not an identity):
- `connect_ctl(target, panel_index, node_index, terminal_index)` ??Wire Nodes[node_index].Terminals[terminal_index] (a SOURCE) into the terminal of front-panel object
- `count(target, cls)` ??
- `uids(target, cls)` ??
- `new_since(target, cls, before)` ??The objects of `cls` that appeared since the `before` uid set.
- `loop_diagram(target, loop_pos, min_margin=4.0)` ??The body Diagram of the For Loop at `loop_pos`, selected deterministically.
- `find_at(target, cls, pos, tol=40)` ??Index of the `cls` object nearest `pos` - the deterministic selector.
- `queue_node(kind, target, src_cls, src_index, src_name, diagram_index, l)` ??Place one queue primitive on Traverse 'Diagram'[diagram_index] of `target` (erdosmiller Create Obtain Queue /
- `drop_subvi(target, subvi_path, diagram_index, location)` ??Place `subvi_path` on the target's `diagram_index`-th Diagram. Get the index from find_at."""
- `open_panel(target, activate=False)` ??Open the target's front panel - REQUIRED before wire() AND before drop_subvi().
- `close_panel(target)` ??Close the target's front panel. SAVE FIRST: closing the panel of a modified VI
- `wire(target, src_cls, src_i, src_term, dst_cls, dst_i, dst_term, )` ??Node-to-node wire by terminal name. Call open_panel(target) first, and save
- `revert(target)` ??Discard a VI's in-memory changes by reloading from disk (VI method Revert)."""
- `copy_into(donor, label, target, prepare=None)` ??Copy the object labeled `label` from `donor` INTO `target`.
- `restore_move_fixtures()` ??Put the two Move-example files back to their pristine bytes - ONLY when nothing of theirs is loaded (call it
- `copy_by_index(donor, cls, index, target, expect_uid=None, finish=None)` ??Copy the `index`-th object of Traverse class `cls` (report() order) from `donor` INTO `target` BY REFERENCE ??
- `move_by_label(donor, label, harvest_to=None)` ??Copy the GObject labeled `label` out of `donor` via OpMoveByLabel_v0.
- `ensure_move_files_pristine()` ??Restore the Move example's Test-Source if a previous run left a donor in it.
- `remove_bad_wires(target)` ??Edit > Remove Broken Wires on `target` (the Ctrl+B cleanup).
- `delete_by_label(target, label, allow_broken=False)` ??Delete the object labeled `label` from `target` (Generic:Delete).
- `exit_loop(target, node_index, output_names, diagram_index, node_class=)` ??Create AUTO-INDEXED output tunnels for `output_names` of a node inside a loop.
- `wire_indicators(target, node_index, src_terms, indicator_names,
            )` ??Branch a node's output terminals onto EXISTING front-panel indicators by label.
- `loop_kernel(target, location, control_names, kernel_path, input_names, p)` ??ONE call: parallel For Loop + kernel subVI inside + named tunnel wiring.
- `set_index_mode(target, tunnel_index, mode)` ??Write a LoopTunnel's IndexMode in `target` (0 = regular/non-indexed, 1 = auto-indexed).
- `tunnel_indicator(target, tunnel_index)` ??Create a front-panel INDICATOR wired to LoopTunnel[tunnel_index] of `target`, typed by LabVIEW.
- `wire_control(target, control_names, dst_cls, dst_i, dst_terms, branch=Fal)` ??Wire FRONT-PANEL CONTROLS to a node's named inputs - the one thing OpWire_v1
- `exec_state(target)` ??
- `gui_save(target)` ??Save a BROKEN VI by focusing its window and sending Ctrl+S.
- `save(target, allow_broken=False)` ??Persist the in-memory edits. Guarded to claudeDev + explicit allowlist: an
- `main()` ??
- `build_invoke(target, cls, method_id, location, diagram_index=0)` ??Create an Invoke Node on `target`'s diagram: class `cls` ("VI Server:Terminal", "VI Server:VI",
- `build_property(target, cls, props, location, diagram_index=0)` ??Create a Property Node on `target`'s diagram: class `cls` ("VI Server:GObject", ...),
- `delete_object(target, cls, index, verify=True)` ??Delete the `index`-th object of Traverse class `cls` on `target` (Generic.Delete over a
- `move_object(target, cls, index, position)` ??Move the `index`-th object of class `cls` (Traverse order, same as report()) on `target` to the
- `build_index_array(target, location, source_terminal_index=0)` ??Place an Index Array primitive on `target`'s top-level block diagram at `location` (erdosmiller
- `node_rank(target, uid)` ??WRONG in general ??kept as a warning. Nodes[] is CREATION order; uid rank matched it on GUIBENCH_v0 only
- `create_control(target, node_index, terminal_index)` ??Create a front-panel control wired to terminal `terminal_index` (Node.Terminals[] order = the Context
- `create_indicator(target, node_index, terminal_index)` ??Indicator wired to terminal `terminal_index` of Nodes[node_index] (Terminal.Create Indicator 6349C02 ??
- `connect_terminals(target, sink_node, sink_term, src_node, src_term)` ??Wire Nodes[src_node].Terminals[src_term] (source) into Nodes[sink_node].Terminals[sink_term] (sink) on
- `fp_labels(target, max_n=200)` ??[(index, label, is_indicator)] for every front-panel object of `target` in tabbing order
- `node_info(target, max_n=400)` ??[(Nodes[] index, style name, label text)] for the top-level block-diagram nodes of `target` in
- `remove_bad_wires_scripted(target)` ??LabVIEW's Ctrl+B by script: VI.'Block Diagram:Remove Bad Wires' (410) on `target` (OpRemoveBadWires_v0,
- `net_map(target, diagram_index=0, max_nodes=200, max_terms=40)` ??Connectivity of one diagram of `target` (Traverse "Diagram" index; 0 = top level), read headlessly with
- `print_net_map(nodes, nets)` ??
- `set_auto_error_handling(target, enabled)` ??Write VI.'Automatic Error Handling' (242) of `target` ??OpSetAutoErr_v0 (2026-09-07). FALSE silences the
- `connect2(target, diagram_index, sink_node, sink_term, src_node, src_t)` ??Wire top-level Nodes[src_node].Terminals[src_term] into Nodes[sink_node].Terminals[sink_term] of ANY diagram
- `set_node_label(target, diagram_index, node_index, text)` ??Write the label of Nodes[node_index] of Traverse "Diagram"[diagram_index] on `target` (OpSetLabel_v0, built by
- `move_out(target, diagram_index, node_index, position)` ??Move Nodes[node_index] of Traverse "Diagram"[diagram_index] to the TOP-LEVEL diagram of `target` at `position`
- `build_clfn(target, location, dll, fn, flat_hex, calling_convention=0, r)` ??Place a CLFN on `target` calling `fn` of `dll` with the parameter list `flat_hex` (flattened Parameter Info array,
- `conpane(target, max_terminals=32)` ??The connector pane of `target` as {terminal index: control label}, with None for a FREE terminal (OpConPane_v0,
- `conpane_assign(target, control_label, terminal_index)` ??Assign the front-panel control `control_label` of `target` to connector-pane terminal `terminal_index`
- `make_default(target, values=None)` ??Set `values` ({control label: value}) on `target` through VI Server, then make ALL current front-panel values the

## Recipes ??what each build script did

- `build_empty_vi.py` ??build_empty_vi.py - EMPTY_v0.vi: an empty, runnable top-level VI to author the stage-2 VI in (docs/stage2-plan.md,
- `build_gpu_kernel.py` ??build_gpu_kernel.py - GPU_kernel_v1.vi: the GPU backend as a DROP-IN for the tracking kernel ??same connector pane as
- `build_harness_compare.py` ??build_harness_compare.py ??HARNESS_compare.vi: one frame through BOTH tracking kernels on identical inputs.
- `build_harness_copy.py` ??build_harness_copy.py - HARNESS_copy{0,1}.vi: the per-frame cost of a reference-safe image copy (IMAQ Copy).
- `build_harness_copyloop.py` ??build_harness_copyloop.py - HARNESS_copyloop.vi: N repeated IMAQ Copy A->B inside ONE Run (steady-state copy cost).
- `build_harness_copyloop2.py` ??build_harness_copyloop2.py - HARNESS_copyloop.vi, N-source variant: the loop count comes from IMAQ GetImageSize
- `build_harness_dispI.py` ??build_harness_dispI.py - HARNESS_dispI.vi: the IMAQ Image Display route (image reference wired straight into the
- `build_harness_display.py` ??build_harness_display.py - HARNESS_disp{0..3}.vi: the main VI's display route on the recorded fixture, stage by stage.
- `build_harness_gpu.py` ??build_harness_gpu.py - HARNESS_gpu.vi: the GPU kernel (CUDA DLL through the Call Library Function Node copied from the
- `build_harness_gpu2.py` ??build_harness_gpu2.py - HARNESS_gpu2.vi: OUR GPU interface (user 2026-09-09: not the Saleh node) - one CLFN per frame,
- `build_harness_loadcal.py` ??build_harness_loadcal.py ??HARNESS_loadcal.vi: the lab's `Load and prep N cal images.vi` with its File Dialog
- `build_harness_variant.py` ??build_harness_variant.py - HARNESS_<name>.vi for the three-way timing benchmark, built from scratch like
- `build_keystone.py` ??build_keystone.py ??build OpBuildPN_v0.vi (docs/keystone-op-spec.md, Build plan v2) in one batch.
- `build_keystone_invoke.py` ??build_keystone_invoke.py ??OpBuildInvoke_v0.vi: create an INVOKE NODE on a target diagram, class =
- `build_opaddshiftreg_v0.py` ??build_opaddshiftreg_v0.py - OpAddShiftReg_v0.vi: CREATE a shift register on a While loop by script.
- `build_opbuildba.py` ??build_opbuildba.py - OpBuildBA_v0.vi: place a Build Array primitive (default: ONE input, not concatenating) on a target's
- `build_opbuildcase_v1.py` ??build_opbuildcase_v1.py - OpBuildCase_v1.vi: a Case Structure that Python can actually drive.
- `build_opbuildcase_v1b.py` ??build_opbuildcase_v1b.py - stage 2 of OpBuildCase_v1: feed the creator's REFNUM inputs from control NAMES.
- `build_opbuildcase_v1c.py` ??build_opbuildcase_v1c.py - stage 2 of OpBuildCase_v1, on a SCRATCH COPY, copied back only if it ends runnable.
- `build_opbuildia.py` ??build_opbuildia.py ??OpBuildIA_v0.vi: place an Index Array primitive on a target's top-level diagram,
- `build_opbuildpn_v1.py` ??build_opbuildpn_v1.py - OpBuildPN_v1: the property-node builder that can no longer fail silently.
- `build_opcaseframes_v0.py` ??build_opcaseframes_v0.py - OpCaseFrames_v0.vi: a case structure's FRAME NAMES and its frame diagrams, by UID.
- `build_opclfn.py` ??build_opclfn.py - OpCLFNBuild_v0.vi: create and configure a Call Library Function Node on a target VI entirely by script,
- `build_opclfnparams.py` ??build_opclfnparams.py - OpCLFNParams_v0.vi: read AND set the import wizard's `Parameter Info` functional global
- `build_opclfnpre.py` ??build_opclfnpre.py - OpCLFNPre_v0.vi: sets the import wizard's FUNCTIONAL GLOBALS that NI's Call Library Node\\Method\\Create.vi
- `build_opconnect.py` ??build_opconnect.py ??OpConnect_v0.vi: wire terminal tb of node nb (source) into terminal ta of node na (sink)
- `build_opconnect2.py` ??build_opconnect2.py ??OpConnect2_v0.vi: wire a TOP-LEVEL source terminal into a sink terminal that lives in ANY
- `build_opconnect_gateway_attempt.py` ??build_opconnect.py ??OpConnect_v0.vi: wire any two terminals of a target VI by Traverse index
- `build_opconnectctl_v0.py` ??build_opconnectctl_v0.py - OpConnectCtl_v0.vi: wire a NODE's terminal to a FRONT-PANEL object's terminal by script.
- `build_opconpane.py` ??build_opconpane.py - OpConPane_v0.vi: READ a VI's connector pane by script.
- `build_opconpaneassign.py` ??build_opconpaneassign.py - OpConPaneAssign_v0.vi: put a front-panel control ON the connector pane, by script.
- `build_opconstvalue.py` ??build_opconstvalue.py - OpConstValue_v0.vi: READ the VALUE of a diagram constant by script.
- `build_opconstvalue_v1.py` ??build_opconstvalue_v1.py - OpConstValue_v1.vi: READ a diagram constant's VALUE by script (Constant.Value 634AC00),
- `build_opconstvalue_v1b.py` ??build_opconstvalue_v1b.py - augment the saved OpConstValue_v1.vi (run 4 build, run 6 functional for strings) so a
- `build_opconstvalue_v1c.py` ??build_opconstvalue_v1c.py - lossless byte readback for OpConstValue_v1.vi. The v1b `data string` BSTR arrives
- `build_opconstvaluen_v0.py` ??build_opconstvaluen_v0.py - OpConstValueN_v0.vi: the NUMERIC-constant reader (discriminators 2 + 3 of
- `build_opconstvaluen_v1.py` ??build_opconstvaluen_v1.py - OpConstValueN_v1.vi = OpConstValueN_v0 (numeric constant reader, run 2 functional:
- `build_opconstwire_v0.py` ??build_opconstwire_v0.py - OpConstWire_v0.vi: for ANY constant class, the wire it feeds. The numeric-typed reader
- `build_opcreatecontrol.py` ??build_opcreatecontrol.py ??OpCreateControl_v0.vi: create a front-panel control wired to terminal t of node n
- `build_opcreatecontrol_v1.py` ??build_opcreatecontrol_v1.py ??OpCreateControl_v1.vi = OpCreateControl_v0 + the created control's LABEL reported
- `build_opcreateindicator.py` ??build_opcreateindicator.py ??OpCreateIndicator_v0.vi: create a front-panel INDICATOR wired to terminal t of
- `build_opcreator.py` ??build_opcreator.py - generic op builder for an erdosmiller node CREATOR: Op<Name>_v0.vi places the creator's node on a
- `build_opctrlvalue.py` ??build_opctrlvalue.py - OpCtrlValue_v0.vi: read a front-panel control's VALUE through a Control reference.
- `build_opexitwhile.py` ??build_opexitwhile.py - OpExitWhile_v0.vi: OpExitLoop_v0 with erdosmiller 'Exit While Loop.vi' in place of
- `build_opforloop_v1.py` ??build_opforloop_v1.py - OpForLoop_v1.vi = OpForLoop_v0 + the ONE wire it always lacked:
- `build_opfplabels.py` ??build_opfplabels.py ??OpFPLabels_v0.vi: report the LABEL and control/indicator flag of front-panel object
- `build_opgeterrors.py` ??build_opgeterrors.py - OpGetErrors_v0.vi: read a VI's ERROR LIST by script (VI method `Get Errors`, ID 0x452, private scope;
- `build_oploopcast_v0.py` ??build_oploopcast_v0.py - OpLoopCast_v0.vi: a ForLoop-TYPED reference to the `index`-th For loop of a VI, cast-free,
- `build_oploopcast_v1.py` ??build_oploopcast_v1.py - OpLoopCast_v1.vi = OpLoopCast_v0 + ForLoop 'Is Parallelism Enabled?' 6362004 and 'Number of
- `build_oploopin.py` ??build_oploopin.py <for|while> - OpForLoopIn_v0 / OpWhileLoopIn_v0: create a For / While loop on ANY diagram of the
- `build_opmakedefault.py` ??build_opmakedefault.py - OpMakeDefault_v0.vi: VI method `Default Values:Make Current Default` (ID 3F3, labviewwiki VI class,
- `build_opmove.py` ??build_opmove.py ??OpMove_v0.vi: move any block-diagram object to an absolute position (GObject.Move,
- `build_opmovebyindex.py` ??build_opmovebyindex.py - OpMoveByIndex_v0.vi: copy ANY GObject from the (byte-substituted) Move-example Source
- `build_opmoveout.py` ??build_opmoveout.py - OpMoveOut_v0.vi: move Nodes[index 2] of Traverse "Diagram"[index] of a target VI to the TOP-LEVEL
- `build_opnetinfo.py` ??build_opnetinfo.py ??OpNetInfo_v1.vi: headless connectivity reader. Inputs: `index` (Traverse "Diagram" index
- `build_opnodeinfo.py` ??build_opfplabels.py ??OpNodeInfo_v0.vi: report the LABEL text and Style code of block-diagram node
- `build_opnodelabels_v0.py` ??build_opnodelabels_v0.py - OpNodeLabels_v0.vi: the LABEL TEXT of every node on ONE diagram, as arrays, cast-free.
- `build_opnodeterms_v0.py` ??build_opnodeterms_v0.py - OpNodeTerms_v0.vi: every terminal of ONE node (diagram `index`, Nodes[] `index 2`) as
- `build_opownerchain_v0.py` ??build_opownerchain_v0.py - OpOwnerChain_v0.vi: a UID in, its OWNER's class and UID out.
- `build_oppanelwiring_v0.py` ??build_oppanelwiring_v0.py - OpPanelWiring_v0.vi: every top-level front-panel object of a VI, with its diagram
- `build_opqueue.py` ??build_opqueue.py <obtain|enqueue|dequeue|release> - OpQueueObtain_v0 / OpQueueEnqueue_v0 / OpQueueDequeue_v0 /
- `build_opqueue_all.py` ??build_opqueue_all.py - run build_opqueue.py for obtain, enqueue, dequeue, release in sequence; stop at the first
- `build_opremovebadwires.py` ??build_opremovebadwires.py ??OpRemoveBadWires_v0.vi: LabVIEW's own Ctrl+B for a target VI, headless:
- `build_opreportall.py` ??build_opreportall.py - OpReportAll_v0.vi: return EVERY object of a class in ONE run, as arrays.
- `build_opreportall_v1.py` ??build_opreportall_v1.py - OpReportAll_v0.vi: report EVERY object of a class in ONE run, as ARRAYS.
- `build_opreportnodes.py` ??build_opreportnodes.py - OpReportNodes_v0.vi: every node of ONE diagram, WITH ITS NAME, as arrays.
- `build_opreportsubvi.py` ??build_opreportsubvi.py - OpReportSubVI_v0.vi: every SubVI call site WITH ITS NAME, as arrays.
- `build_opsetautoerr.py` ??build_opsetautoerr.py ??OpSetAutoErr_v0.vi: write VI.'Automatic Error Handling' (ID 242, R/W) of a target VI from a
- `build_opsetlabel.py` ??build_opsetlabel.py - OpSetLabel_v0.vi: WRITE the label of Nodes[index 2] of Traverse "Diagram"[index] of a target VI
- `build_opshiftregs_v0.py` ??build_opshiftregs_v0.py - OpShiftRegs_v0.vi: the `index 2`-th shift register of the `index`-th loop (Traverse
- `build_opshiftregs_v1.py` ??build_opshiftregs_v1.py - OpShiftRegs_v1.vi = OpShiftRegs_v0 + the LEFT side of the `index 2`-th right register:
- `build_opsubvis_v0.py` ??build_opsubvis_v0.py - OpSubVIs_v0.vi: every subVI call on ONE diagram, as arrays, in ONE run - cast-free.
- `build_optunnelind.py` ??build_optunnelind.py - OpTunnelInd_v0.vi: create a correctly-typed INDICATOR wired to a loop TUNNEL.
- `build_optunnelread_v0.py` ??build_optunnelread_v0.py - OpTunnelRead_v0.vi: the INNER terminals of a case/loop tunnel, per frame.
- `build_optunnels_v0.py` ??build_optunnels_v0.py - OpTunnels_v0.vi: the `index`-th LoopTunnel of a VI - its own UID, IndexMode, the OUTER
- `build_opwhileloop.py` ??build_opwhileloop.py - OpWhileLoop_v0.vi: OpForLoop_v0 with erdosmiller 'Create While Loop.vi' in place of
- `build_opwiresource_v0.py` ??build_opwiresource_v0.py - OpWireSource_v0.vi: name the SOURCE object of a wire, by wire index. This replaces the
- `build_opwiresource_v1.py` ??build_opwiresource_v1.py - OpWireSource_v1.vi: the source object of a wire addressed BY UID, not by traverse index.
- `build_opwiresource_v2.py` ??build_opwiresource_v2.py - OpWireSource_v2.vi = v1 plus the SOURCE OBJECT'S UID.
- `build_opwiresource_v3.py` ??build_opwiresource_v3.py - OpWireSource_v3.vi = v2 plus the ability to inspect EVERY terminal of a wire.
- `build_opwiresource_v4.py` ??build_opwiresource_v4.py - OpWireSource_v4.vi = v3 plus proof that the owner-UID branch reads what it claims.
- `build_opwiresource_v5.py` ??build_opwiresource_v5.py - OpWireSource_v5.vi = v4 with the owner-UID branch REWIRED to the right Owner node,
- `build_opwiresr_v0.py` ??build_opwiresr_v0.py - the four OpWireSR_*_v0 ops (docs/stage2-assembly-step-a3.md) + their functional test.
- `build_rawcmd.py` ??build_rawcmd.py - RAWCMD_rotor.vi: a copy of the Autonics driver's Configure.vi (VISA Open -> VISA Write of an init
- `build_setcommand_signed.py` ??build_setcommand_signed.py - SetCommand_signed.vi: the lab's Autonics rotor driver with a SIGNED position read.
- `build_strtopath.py` ??build_strtopath.py - StrToPath.vi: one `String To Path` primitive with a string control and a path indicator on the
- `build_track_kernel_v1.py` ??build_track_kernel_v1.py - TRACK_kernel_v1.vi: ONE kernel subVI with a `backend` selector (0 = CPU-parallel, 1 = GPU).
- `build_track_v6_core.py` ??build_track_v6_core.py - Track_v6_CPU_core_v0.vi: the stage-2 REPLAY CORE (docs/stage2-assembly-step-b.md,
- `build_track_v6_queue.py` ??build_track_v6_queue.py - Track_v6_CPU_queue_v0.vi: step C v2.1 (docs/stage2-assembly-step-c.md) - the kernel path
- `build_v3.py` ??build_v3.py - the FULL, replayable build of PARALLEL_kernel_v3.vi from a clean four-fold copy.
- `cycle3_toolkit.py` ??cycle3_toolkit.py - ONE runner for the three stage-2 step-B toolkit items (docs/stage2-assembly-step-b.md, revised
- `cycle3b_toolkit.py` ??cycle3b_toolkit.py - ONE runner: OpMoveByIndex_v0 (the primitive copier) then StrToPath.vi (its functional test =
- `derive_harness_disp4.py` ??derive_harness_disp4.py - HARNESS_disp4.vi = disp3 with the Picture indicator removed (Draw output unwired).
- `finish_gpu_kernel.py` ??finish_gpu_kernel.py - finish GPU_kernel_v1.vi from the checkpoint (GPU_kernel_v1_partial.vi: every input wired, ExecState 1).
- `fix_fleet_auto_error.py` ??fix_fleet_auto_error.py - turn AUTOMATIC ERROR HANDLING OFF on fleet ops that still have it (and save them).
- `fix_opreportall_errors.py` ??fix_opreportall_errors.py - stop OpReportAll_v0 popping a modal dialog, and find out what really errors.
- `fix_v3_starting_xy.py` ??fix_v3_starting_xy.py - wire Decimate outputs 1/2 into the P=4 loop's kernel 'starting x 1'/'starting y 1' on a COPY of
- `inspect_setindexmode.py` ??inspect_setindexmode.py - read OpSetIndexMode_v0's skeleton, so the tunnel-indicator op can be built from it.
- `keystone_discovery.py` ??keystone_discovery.py ??discovery for docs/keystone-op-spec.md "Build plan v2", on a scratch copy.
- `patch_opbuildcase.py` ??patch_opbuildcase.py - OpBuildCase_v0 pops an error dialog on every run: erdosmiller `Create Case Structure.vi` always tries
- `probe_allow_private.py` ??probe_allow_private.py - is `Set Method (Allow Private)` itself attachable by our builder?
- `probe_allow_private2.py` ??probe_allow_private2.py - fix the probe first, then answer the private-member question.
- `probe_allow_private3.py` ??probe_allow_private3.py - the creator SPRAYS ~67 nodes on a private ID. Is one of them correct?
- `probe_arrayout.py` ??probe_arrayout.py - HOW does an AUTO-INDEXED OUTPUT tunnel + ARRAY indicator get built by script?
- `probe_arrayout2.py` ??probe_arrayout2.py - the corrected follow-up to probe_arrayout.py.
- `probe_attach_reader.py` ??probe_attach_reader.py - make "did the property attach?" a DETERMINISTIC read before asking anything else.
- `probe_attach_reader2.py` ??probe_attach_reader2.py - does the walker ABORT at the first empty node? Swap the creation order and see.
- `probe_builder_artifact.py` ??probe_builder_artifact.py - what does ONE build_property call leave on the target, and does v0 do it too?
- `probe_castfree_ladders.py` ??probe_castfree_ladders.py - cycle 1 of the autonomous loop: do the peer's cast-free ladders compile?
- `probe_castfree_ladders2.py` ??probe_castfree_ladders2.py - cycle 1b: same two ladders, with the branch bug removed and the attach read first.
- `probe_castfree_ladders3.py` ??probe_castfree_ladders3.py - cycle 2: compile the two cast-free ladders, now that attach is deterministic.
- `probe_castfree_ladders4.py` ??probe_castfree_ladders4.py - node fault or wire fault? ExecState at every step, on both ladders.
- `probe_castfree_ladders5.py` ??probe_castfree_ladders5.py - cycle 2 retry of the two cast-free ladders with a walker that cleans up after itself.
- `probe_migrate_compiles.py` ??probe_migrate_compiles.py - step 0a, attempt 3, and a DIFFERENT test from the two void ones.
- `probe_migrate_v2.py` ??probe_migrate_v2.py - step 0a attempt 4, built on the calls the queue core actually used.
- `probe_migrate_v3.py` ??probe_migrate_v3.py - step 0a attempt 5: does the MIGRATED state actually compile?
- `probe_relocate_route.py` ??probe_relocate_route.py - step 0a of the delivery cycle: can work be moved from one loop to another
- `probe_stale_nodes.py` ??probe_stale_nodes.py - what makes a freshly created node VISIBLE to the Nodes[] walker?
- `probe_walk_raw.py` ??probe_walk_raw.py - what does the node walker's op RETURN at each index past the donor's nodes?
- `test_opreportall.py` ??test_opreportall.py - ACCEPTANCE for OpReportAll_v0: same answers as report(), and how much faster?
- `test_optunnelind.py` ??test_optunnelind.py - does OpTunnelInd_v0 actually produce an ARRAY indicator? FUNCTIONAL test.

## Recent bench logs (last 3 days; older ones exist ??search them if needed)

- `probe_claude_json_usage2.log` ??BGRUN END rc=0 after 7s
- `probe_claude_json_usage.log` ??BGRUN END rc=1 after 0s
- `retro_cycle9.log` ??BGRUN END rc=0 after 255s
- `priorart_ownerchain.log` ??BGRUN END rc=0 after 245s
- `census_opwiresource_v5.log` ??BGRUN END rc=0 after 6s
- `which_loop_owns_motor.log` ??BGRUN END rc=0 after 7s
- `build_diagram_hierarchy_run3.log` ??BGRUN END rc=0 after 8s
- `build_diagram_hierarchy_run2.log` ??BGRUN END rc=1 after 6s
- `build_diagram_hierarchy.log` ??BGRUN END rc=1 after 7s
- `probe_migrate_v3.log` ??BGRUN END rc=0 after 2s
- `census_boolean_controls.log` ??BGRUN END rc=0 after 2s
- `probe_migrate_v2.log` ??BGRUN END rc=0 after 1s
- `probe_migrate_compiles.log` ??BGRUN END rc=1 after 12s
- `census_0a_names.log` ??BGRUN END rc=0 after 3s
- `probe_relocate_route_run2.log` ??BGRUN END rc=0 after 168s
- `probe_relocate_route.log` ??BGRUN END rc=1 after 1s
- `retro_cycle8_run2.log` ??BGRUN END rc=0 after 262s
- `retro_cycle8.log` ??BGRUN END rc=1 after 209s
- `peer_cycle8_plan.log` ??BGRUN END rc=0 after 639s
- `peer_restructure_in_copy_plan.log` ??BGRUN END rc=0 after 173s
- `peer_frameloop_seam.log` ??BGRUN END rc=0 after 194s
- `boundary_manifest_frameloop.log` ??BGRUN END rc=0 after 827s
- `verify_review_layers_run2.log` ??BGRUN END rc=0 after 493s
- `verify_review_layers.log` ??BGRUN END rc=1 after 1s
- `peer_claude_test.log` ??BGRUN END rc=0 after 27s
- `peer_modelrec_test.log` ??BGRUN END rc=0 after 10s
- `retro_cycle7.log` ??BGRUN END rc=0 after 166s
- `build_opcaseframes_v0.log` ??BGRUN END rc=1 after 52s
- `peer_caseframes_downcast.log` ??BGRUN END rc=0 after 68s
- `peer_caseframes_orphan1329.log` ??BGRUN END rc=0 after 21s
- `peer_caseframes_stub.log` ??BGRUN END rc=0 after 22s
- `peer_caseframes_terminalchain.log` ??BGRUN END rc=0 after 46s
- `diag_case5540_context.log` ??BGRUN END rc=0 after 38s
- `diag_case5540_inputs.log` ??BGRUN END rc=0 after 42s
- `diag_case5540_frame_sources.log` ??BGRUN END rc=0 after 43s
- `build_optunnelread_v0.log` ??BGRUN END rc=0 after 80s
- `peer_removebadwires_window.log` ??BGRUN END rc=0 after 85s
- `peer_tunnelread_broken.log` ??BGRUN END rc=0 after 51s
- `diag_case5540_tunnels.log` ??BGRUN END rc=0 after 39s
- `build_opwiresource_v5.log` ??BGRUN END rc=0 after 48s
- `peer_v5_execstate.log` ??BGRUN END rc=0 after 63s
- `peer_wrong_owner_node.log` ??BGRUN END rc=0 after 41s
- `build_opwiresource_v4.log` ??BGRUN END rc=1 after 56s
- `peer_owneruid_stale.log` ??BGRUN END rc=0 after 95s
- `build_opwiresource_v3.log` ??BGRUN END rc=1 after 72s
- `peer_uid_contradiction.log` ??BGRUN END rc=0 after 96s
- `build_opwiresource_v2.log` ??BGRUN END rc=1 after 126s
- `peer_tunnelread_plan.log` ??BGRUN END rc=0 after 91s
- `peer_case_reader_ids.log` ??BGRUN END rc=0 after 107s
- `peer_reseed_design.log` ??BGRUN END rc=0 after 127s
- `census_selector_sources.log` ??BGRUN END rc=0 after 29s
- `build_opwiresource_v1.log` ??BGRUN END rc=0 after 86s
- `peer_v1_execstate0.log` ??BGRUN END rc=0 after 94s
- `peer_lookup_terminals.log` ??BGRUN END rc=0 after 57s
- `peer_traverse_order.log` ??BGRUN END rc=0 after 95s
- `build_opwiresource_v0.log` ??BGRUN END rc=1 after 40s
- `peer_report_on_wires.log` ??BGRUN END rc=0 after 61s
- `peer_branch_wire_delete.log` ??BGRUN END rc=0 after 56s
- `peer_generic_downcast.log` ??BGRUN END rc=0 after 75s
- `peer_uid_indicator.log` ??BGRUN END rc=0 after 72s
- `peer_scan_three_missing.log` ??BGRUN END rc=0 after 108s
- `opconstvaluen_scan.log` ??BGRUN END rc=1 after 370s
- `build_opconstvaluen_v1.log` ??BGRUN END rc=0 after 324s
- `peer_opconstvaluen_v1_fail1.log` ??BGRUN END rc=0 after 41s
- `peer_opconstvaluen_v1_recipe.log` ??BGRUN END rc=0 after 74s
- `peer_opconstvaluen_run2.log` ??BGRUN END rc=0 after 111s
- `build_opconstvaluen_v0.log` ??BGRUN END rc=1 after 357s
- `census_dnc_property_ids.log` ??BGRUN END rc=0 after 54s
- `peer_numtext_id.log` ??BGRUN END rc=0 after 93s
- `peer_opconstvaluen_recipe.log` ??BGRUN END rc=0 after 78s
- `diag_constvalue_siblings.log` ??BGRUN END rc=0 after 262s
- `peer_numeric_void.log` ??BGRUN END rc=0 after 98s
- `build_opconstvalue_v1c.log` ??BGRUN END rc=1 after 219s
- `peer_v1c_framing.log` ??BGRUN END rc=0 after 93s
- `peer_v1c_recipe.log` ??BGRUN END rc=0 after 100s
- `census_unflatten_terms.log` ??BGRUN END rc=0 after 7s
- `census_hexstring_vi.log` ??BGRUN END rc=1 after 7s
- `peer_v1b_codepage.log` ??BGRUN END rc=0 after 83s
- `build_opconstvalue_v1b.log` ??BGRUN END rc=1 after 66s
- `peer_v1b_recipe.log` ??BGRUN END rc=0 after 62s
- `peer_numeric_none.log` ??BGRUN END rc=0 after 57s
- `build_opconstvalue_v1.log` ??BGRUN END rc=1 after 302s
- `diag_rpc_restart.log` ??BGRUN END rc=0 after 121s
- `peer_rpc_run4.log` ??BGRUN END rc=0 after 76s
- `peer_cv3.log` ??BGRUN END rc=0 after 33s
- `peer_cv2.log` ??BGRUN END rc=0 after 48s
- `peer_rpc2.log` ??BGRUN END rc=0 after 57s
- `peer_constvalue.log` ??BGRUN END rc=0 after 83s
- `census_constant_seed.log` ??BGRUN END rc=0 after 11s
- `diag_example_load.log` ??BGRUN END rc=0 after 1s
- `census_case5540_hop2.log` ??BGRUN END rc=0 after 215s
- `census_case5540.log` ??BGRUN END rc=0 after 80s
- `build_track_v6_queue_full.log` ??BGRUN END rc=0 after 360s
- `peer_stepe.log` ??BGRUN END rc=0 after 112s
- `build_track_v6_queue.log` ??BGRUN END rc=0 after 352s
- `peer_5001.log` ??BGRUN END rc=0 after 58s
- `peer_errno22b.log` ??BGRUN END rc=0 after 65s
- `peer_errno22.log` ??BGRUN END rc=0 after 43s
- `test_count_tunnel.log` ??BGRUN END rc=0 after 36s
- `peer_queue_recipe.log` ??BGRUN END rc=0 after 115s
- `census_loop_node_terms.log` ??BGRUN END rc=0 after 4s
- `peer_stepc2.log` ??BGRUN END rc=0 after 113s
- `build_track_v6_core_full.log` ??BGRUN END rc=0 after 397s
- `peer_stepc.log` ??BGRUN END rc=0 after 143s
- `build_track_v6_core.log` ??BGRUN END rc=0 after 206s
- `peer_core_es0.log` ??BGRUN END rc=0 after 105s
- `peer_core_1055.log` ??BGRUN END rc=0 after 56s
- `peer_core_idx.log` ??BGRUN END rc=0 after 47s
- `peer_core_l4.log` ??BGRUN END rc=0 after 67s
- `peer_core2.log` ??BGRUN END rc=0 after 149s
- `peer_core.log` ??BGRUN END rc=0 after 161s
- `build_strtopath.log` ??BGRUN END rc=0 after 324s
- `peer_guisave.log` ??BGRUN END rc=0 after 83s
- `cycle3b_toolkit.log` ??BGRUN END rc=2 after 458s
- `peer_movebyindex_es0.log` ??BGRUN END rc=0 after 77s
- `diag_opmovebylabel.log` ??BGRUN END rc=0 after 2s
- `peer_movebyindex.log` ??BGRUN END rc=0 after 89s
- `peer_strtopath_1054b.log` ??BGRUN END rc=0 after 69s
- `peer_strtopath_1054.log` ??BGRUN END rc=0 after 65s
- `cycle3_toolkit.log` ??BGRUN END rc=2 after 441s
- `peer_forv1.log` ??BGRUN END rc=0 after 61s
- `diag_opforloop_v1.log` ??BGRUN END rc=0 after 1s
- `peer_stepb3.log` ??BGRUN END rc=0 after 61s
- `census_fis_donors.log` ??BGRUN END rc=0 after 15s
- `peer_stepb2.log` ??BGRUN END rc=0 after 132s
- `census_savetraces_terms.log` ??BGRUN END rc=0 after 9s
- `census_path_donors.log` ??BGRUN END rc=0 after 49s
- `peer_stepb.log` ??BGRUN END rc=0 after 133s
- `census_newviobject_donors.log` ??BGRUN END rc=0 after 28s
- `peer_patharray.log` ??BGRUN END rc=0 after 117s
- `fix_fleet_auto_error.log` ??BGRUN END rc=0 after 1s
- `peer_wiresr_t8b.log` ??BGRUN END rc=0 after 64s
- `test_opwiresr.log` ??BGRUN END rc=1 after 13s
- `peer_wiresr_path.log` ??BGRUN END rc=0 after 125s
- `peer_wiresr_modal.log` ??BGRUN END rc=0 after 73s
- `build_opwiresr_v0.log` ??BGRUN END rc=1 after 329s
- `peer_a3.log` ??BGRUN END rc=0 after 122s
- `build_opaddshiftreg_v0_run3.log` ??BGRUN END rc=0 after 66s
- `peer_addsr_rpc.log` ??BGRUN END rc=0 after 111s
- `build_opaddshiftreg_v0_run2.log` ??BGRUN END rc=1 after 34s
- `diag_addsr_fail1.log` ??BGRUN END rc=0 after 0s
- `peer_addsr_fail1.log` ??BGRUN END rc=0 after 91s
- `build_opaddshiftreg_v0.log` ??BGRUN END rc=1 after 3s
- `peer_stage2_shiftreg.log` ??BGRUN END rc=0 after 145s
- `test_oploopin.log` ??BGRUN END rc=0 after 2s
- `build_oploopin.log` ??BGRUN END rc=0 after 46s
- `peer_nested_creators_plan.log` ??BGRUN END rc=0 after 59s
- `build_empty_vi.log` ??BGRUN END rc=0 after 10s
- `probe_harness_base.log` ??BGRUN END rc=0 after 21s
- `test_opqueue.log` ??BGRUN END rc=0 after 41s
- `lv_restart_2100.log` ??BGRUN END rc=0 after 71s
- `peer_opqueue_run_hang.log` ??BGRUN END rc=0 after 80s
- `build_opqueue.log` ??BGRUN END rc=0 after 117s
- `peer_opqueue_fail1.log` ??BGRUN END rc=0 after 44s
- `probe_queue_vis.log` ??BGRUN END rc=0 after 3s
- `test_opexitwhile.log` ??BGRUN END rc=0 after 13s
- `build_opexitwhile.log` ??BGRUN END rc=0 after 21s
- `peer_exitwhile_fail1.log` ??BGRUN END rc=0 after 101s
- `test_opwhileloop.log` ??BGRUN END rc=0 after 2s
- `build_opwhileloop.log` ??BGRUN END rc=0 after 3s
- `peer_stage2_plan.log` ??BGRUN END rc=0 after 123s
- `probe_opexitloop.log` ??BGRUN END rc=0 after 11s
- `probe_opforloop.log` ??BGRUN END rc=0 after 11s
- `hw_rotor_visible.log` ??BGRUN END rc=0 after 10s
- `hw_rotor_signed_test.log` ??BGRUN END rc=0 after 4s
- `peer_rotor_negative_plan.log` ??BGRUN END rc=0 after 73s
- `build_rawcmd.log` ??BGRUN END rc=0 after 18s
- `peer_rotor_read_timeout.log` ??BGRUN END rc=0 after 72s
- `peer_autonics_commands.log` ??BGRUN END rc=0 after 120s
- `hw_rotor_read.log` ??BGRUN END rc=0 after 3s
- `probe_autonics_configure.log` ??BGRUN END rc=0 after 18s
- `test_setcommand_signed.log` ??BGRUN END rc=0 after 0s
- `peer_setcommand_fail5.log` ??BGRUN END rc=0 after 37s
- `build_setcommand_signed.log` ??BGRUN END rc=0 after 82s
- `lv_restart_1952.log` ??BGRUN END rc=0 after 66s
- `peer_setcommand_fail4.log` ??BGRUN END rc=0 after 56s
- `lv_restart_1940.log` ??BGRUN END rc=0 after 74s
- `peer_setcommand_fail3.log` ??BGRUN END rc=0 after 24s
- `peer_setcommand_fail2.log` ??BGRUN END rc=0 after 33s
- `peer_setcommand_fail1.log` ??BGRUN END rc=0 after 21s
- `peer_setcommand_signed_plan.log` ??BGRUN END rc=0 after 65s
- `peer_autonics_protocol.log` ??BGRUN END rc=0 after 58s
- `probe_setcommand3.log` ??BGRUN END rc=0 after 0s
- `peer_hexstring_signed.log` ??BGRUN END rc=0 after 56s
- `probe_setcommand2.log` ??BGRUN END rc=0 after 1s
- `probe_setcommand.log` ??BGRUN END rc=0 after 13s
- `test_oploopcast_v1.log` ??BGRUN END rc=0 after 63s
- `peer_loopcast_v1_t1.log` ??BGRUN END rc=0 after 37s
- `build_oploopcast_v1.log` ??BGRUN END rc=0 after 79s
- `peer_loopcast_v1_plan.log` ??BGRUN END rc=0 after 50s
- `test_opshiftregs_v1.log` ??BGRUN END rc=0 after 57s
- `build_opshiftregs_v1.log` ??BGRUN END rc=0 after 260s
- `peer_shiftregs_v1_fail1.log` ??BGRUN END rc=0 after 18s
- `peer_shiftregs_right.log` ??BGRUN END rc=0 after 85s
- `test_opshiftregs.log` ??BGRUN END rc=1 after 58s
- `build_opshiftregs_v0.log` ??BGRUN END rc=0 after 252s
- `peer_shiftregs_fail1.log` ??BGRUN END rc=0 after 50s
- `peer_shiftregs_plan.log` ??BGRUN END rc=0 after 82s
- `test_oploopcast.log` ??BGRUN END rc=0 after 65s
- `build_opwhilecast_v0.log` ??BGRUN END rc=0 after 99s
- `peer_loopcast_whileloop.log` ??BGRUN END rc=0 after 67s
- `build_oploopcast_v0.log` ??BGRUN END rc=0 after 156s
- `probe_example_forloop.log` ??BGRUN END rc=0 after 9s
- `peer_loopcast_seed2.log` ??BGRUN END rc=0 after 63s
- `peer_loopcast_seed_plan.log` ??BGRUN END rc=0 after 51s
- `test_opnodelabels.log` ??BGRUN END rc=0 after 211s
- `build_opnodelabels_v0.log` ??BGRUN END rc=0 after 71s
- `peer_opnodelabels_plan.log` ??BGRUN END rc=0 after 35s
- `peer_implicit_pn_linked_object.log` ??BGRUN END rc=0 after 50s
- `run_copyloop_bench.log` ??BGRUN END rc=0 after 18s
- `peer_copyloop_linearity.log` ??BGRUN END rc=0 after 37s
- `build_harness_copyloopX.log` ??BGRUN END rc=0 after 5s
- `build_harness_copyloop2.log` ??BGRUN END rc=0 after 5s
- `peer_copyloop2_terminals.log` ??BGRUN END rc=0 after 80s
- `peer_copyloop_gate.log` ??BGRUN END rc=0 after 21s
- `build_harness_copyloop.log` ??BGRUN END rc=4 after 53s
- `peer_copyloop_plan.log` ??BGRUN END rc=0 after 65s
- `peer_stall_matrix.log` ??BGRUN END rc=0 after 25s
- `handle_growth_matrix.log` ??BGRUN END rc=0 after 456s
- `stall_pid1720_141314.log` ??
- `run_dispI_bench.log` ??BGRUN END rc=0 after 24s
- `build_harness_dispI.log` ??BGRUN END rc=0 after 87s
- `build_opconnectctl_v0.log` ??BGRUN END rc=0 after 57s
- `peer_opconnectctl_plan.log` ??BGRUN END rc=0 after 50s
- `peer_dispI_route2.log` ??BGRUN END rc=0 after 33s
- `peer_dispI_5001.log` ??BGRUN END rc=0 after 10s
- `peer_dispI_plan.log` ??BGRUN END rc=0 after 48s
- `g9_affinity_run.log` ??BGRUN END rc=0 after 19s
- `peer_g9_plan.log` ??BGRUN END rc=0 after 34s
- `run_copy_bench.log` ??BGRUN END rc=0 after 5s
- `build_harness_copy.log` ??BGRUN END rc=0 after 55s
- `peer_copy_build_run1.log` ??BGRUN END rc=0 after 33s
- `peer_imaqcopy_plan.log` ??BGRUN END rc=0 after 55s
- `run_display_bench.log` ??BGRUN END rc=0 after 27s
- `derive_harness_disp4.log` ??BGRUN END rc=0 after 26s
- `peer_display_results.log` ??BGRUN END rc=0 after 32s
- `build_harness_display.log` ??BGRUN END rc=0 after 58s
- `peer_display_build_run2.log` ??BGRUN END rc=0 after 29s
- `peer_display_path_plan.log` ??BGRUN END rc=0 after 84s
- `peer_cast_route.log` ??BGRUN END rc=0 after 93s
- `test_optunnels.log` ??BGRUN END rc=0 after 173s
- `build_optunnels_v0.log` ??BGRUN END rc=0 after 228s
- `peer_optunnels_plan.log` ??BGRUN END rc=0 after 138s
- `peer_wiregraph_plan.log` ??BGRUN END rc=0 after 73s
- `patch_nodeterms_classes.log` ??BGRUN END rc=0 after 4s
- `sweep_nodeterms_main.log` ??BGRUN END rc=3 after 667s
- `global_read_control3.log` ??BGRUN END rc=0 after 319s
- `peer_nodeterms_sweep_plan.log` ??BGRUN END rc=0 after 55s
- `global_read_control2.log` ??BGRUN END rc=3 after 42s
- `walk_junk_probe.log` ??BGRUN END rc=0 after 6s
- `global_read_control.log` ??BGRUN END rc=3 after 4s
- `peer_stall_silent_walk.log` ??BGRUN END rc=0 after 23s
- `globals_direction_main.log` ??BGRUN END rc=0 after 385s
- `stall_pid6164_121247.log` ??
- `peer_walker_zero_junk.log` ??BGRUN END rc=0 after 71s
- `test_opnodeterms.log` ??BGRUN END rc=0 after 208s
- `build_opnodeterms_v0.log` ??BGRUN END rc=0 after 142s
- `peer_nodeterms_step3.log` ??BGRUN END rc=0 after 19s
- `peer_opnodeterms_plan.log` ??BGRUN END rc=0 after 63s
- `test_oppanelwiring.log` ??BGRUN END rc=0 after 58s
- `peer_panelwiring_oracle.log` ??BGRUN END rc=0 after 41s
- `build_oppanelwiring_v0.log` ??BGRUN END rc=0 after 131s
- `peer_panelwiring_step6.log` ??BGRUN END rc=0 after 16s
- `build_oppanelwiring_v0_run1.log` ??BGRUN END rc=3 after 6s
- `peer_stall_sweep.log` ??BGRUN END rc=0 after 76s
- `peer_oppanelwiring_plan.log` ??BGRUN END rc=0 after 176s
- `sweep_subvis_main.log` ??BGRUN END rc=0 after 168s
- `stall_pid9272_105613.log` ??
- `test_opsubvis_v1.log` ??BGRUN END rc=0 after 140s
- `prep_restart_1052.log` ??BGRUN END rc=0 after 62s
- `build_opsubvis_v1.log` ??BGRUN END rc=0 after 118s
- `peer_opsubvis_v1_plan.log` ??BGRUN END rc=0 after 103s
- `test_opsubvis.log` ??BGRUN END rc=3 after 80s
- `build_opsubvis_v0.log` ??BGRUN END rc=0 after 89s
- `peer_opsubvis_plan.log` ??BGRUN END rc=0 after 129s
- `probe_castfree5.log` ??BGRUN END rc=3 after 77s
- `stall_selftest.log` ??BGRUN END rc=4294967295 after 130s
- `peer_stall_wrappers.log` ??BGRUN END rc=0 after 130s
- `probe_attach_reader2c.log` ??
- `revert_main_after_sweep.log` ??BGRUN END rc=1 after 0s
- `probe_builder_artifact.log` ??BGRUN END rc=0 after 261s
- `peer_artifact.log` ??BGRUN END rc=0 after 69s
- `probe_castfree4.log` ??BGRUN END rc=0 after 10s
- `peer_castfree3.log` ??BGRUN END rc=0 after 111s
- `probe_castfree3.log` ??BGRUN END rc=3 after 7s
- `build_opbuildpn_v1c.log` ??BGRUN END rc=0 after 103s
- `peer_buildpn_v1_fail2.log` ??BGRUN END rc=0 after 60s
- `build_opbuildpn_v1b.log` ??BGRUN END rc=3 after 59s
- `probe_stale_nodes.log` ??BGRUN END rc=0 after 10s
- `peer_stale_nodes.log` ??BGRUN END rc=0 after 38s
- `probe_walk_raw.log` ??BGRUN END rc=0 after 3s
- `peer_buildpn_v1_fail1.log` ??BGRUN END rc=0 after 32s
- `probe_attach_reader2b.log` ??BGRUN END rc=0 after 5s
- `build_opbuildpn_v1.log` ??BGRUN END rc=3 after 56s
- `probe_attach_reader2.log` ??BGRUN END rc=0 after 5s
- `peer_buildpn_v1.log` ??BGRUN END rc=0 after 69s
- `peer_walker_abort.log` ??BGRUN END rc=0 after 68s
- `read_opbuildpn_panel.log` ??BGRUN END rc=0 after 12s
- `probe_attach_reader.log` ??BGRUN END rc=2 after 35s
- `peer_castfree2.log` ??BGRUN END rc=0 after 65s
- `probe_castfree2.log` ??BGRUN END rc=3 after 13s
- `peer_castfree1.log` ??BGRUN END rc=0 after 66s
- `probe_castfree.log` ??BGRUN END rc=3 after 12s
- `peer_loop_plan.log` ??BGRUN END rc=0 after 92s
- `sweep_netmap_main.log` ??BGRUN END rc=0 after 5487s
- `peer_netmap_plan.log` ??BGRUN END rc=0 after 89s
- `probe_allow_private3.log` ??BGRUN END rc=0 after 29s
- `probe_allow_private2.log` ??BGRUN END rc=0 after 32s
- `probe_allow_private.log` ??BGRUN END rc=0 after 26s
- `erdos_creators.log` ??BGRUN END rc=0 after 26s
- `erdos_invoke_terms.log` ??BGRUN END rc=0 after 26s
- `shared_state.log` ??BGRUN END rc=0 after 9s
- `peer_private_method.log` ??BGRUN END rc=0 after 125s
- `build_opgeterrors.log` ??BGRUN END rc=5 after 151s
- `diff_wiring.log` ??BGRUN END rc=0 after 9s
- `peer_opreportnodes.log` ??BGRUN END rc=0 after 74s
- `probe_netmap_labels.log` ??BGRUN END rc=0 after 312s
- `setcommand_diagram.log` ??BGRUN END rc=0 after 6s
- `autonics_driver.log` ??BGRUN END rc=0 after 26s
- `autonics_configure.log` ??BGRUN END rc=1 after 0s
- `peer_rotor_zero.log` ??BGRUN END rc=0 after 91s
- `autonics_defaults.log` ??BGRUN END rc=0 after 0s
- `autonics_fp.log` ??BGRUN END rc=0 after 9s
- `netmap_label_probe.log` ??BGRUN END rc=0 after 1s
- `imaqdx_state_20260914.log` ??BGRUN END rc=0 after 10s
- `imaqdx_recheck_20260914.log` ??=== visibility Simple: 80 attributes; the relevant ones ===
- `build_opreportnodes2.log` ??BGRUN END rc=5 after 50s
- `build_opreportnodes.log` ??BGRUN END rc=5 after 54s
- `inspect_opnodeinfo.log` ??BGRUN END rc=0 after 3s
- `nodeinfo_probe.log` ??BGRUN END rc=0 after 10s
- `build_opreportsubvi2.log` ??BGRUN END rc=4 after 4s
- `build_opreportsubvi.log` ??BGRUN END rc=4 after 4s
- `visa_aliases.log` ??BGRUN END rc=0 after 1s
- `vi_string_context.log` ??BGRUN END rc=0 after 0s
- `vi_inventory.log` ??
- `close_main_fp.log` ??BGRUN END rc=0 after 0s
- `open_main_fp.log` ??BGRUN END rc=0 after 1s
- `find_rotor_controls.log` ??BGRUN END rc=0 after 120s
- `vi_strings_rotor.log` ??BGRUN END rc=0 after 0s
- `fix_opreportall_errors.log` ??BGRUN END rc=0 after 3s
- `test_opreportall.log` ??BGRUN END rc=2 after 770s
- `build_opreportall_v2.log` ??BGRUN END rc=0 after 74s
- `build_opreportall_v1.log` ??BGRUN END rc=4 after 6s
- `build_opreportnodes3.log` ??BGRUN END rc=5 after 60s
- `test_optunnelind.log` ??BGRUN END rc=0 after 21s
- `build_optunnelind2.log` ??BGRUN END rc=0 after 2s
- `build_optunnelind.log` ??BGRUN END rc=4 after 4s
- `inspect_setindexmode.log` ??BGRUN END rc=0 after 19s
- `peer_tunnel_indicator.log` ??BGRUN END rc=0 after 74s
- `probe_arrayout3.log` ??BGRUN END rc=0 after 8s
- `probe_arrayout2.log` ??BGRUN END rc=0 after 10s
- `probe_arrayout.log` ??BGRUN END rc=0 after 6s
- `peer_gpu_portability.log` ??BGRUN END rc=0 after 108s
- `kernel_parallelism.log` ??BGRUN END rc=0 after 95s
- `opreportall_output.log` ??BGRUN END rc=0 after 10s
- `lv_restart3.log` ??BGRUN END rc=0 after 65s
- `build_opreportall3.log` ??BGRUN END rc=0 after 8s
- `build_opreportall2.log` ??
- `verify_donor_intact.log` ??BGRUN END rc=0 after 3s
- `cleanup_reportall.log` ??BGRUN END rc=0 after 66s
- `opreportall_step3c.log` ??
- `build_opreportall.log` ??BGRUN END rc=0 after 2s
- `probe_tunnel_wire.log` ??BGRUN END rc=0 after 2s
- `probe_tunnel_first.log` ??BGRUN END rc=0 after 2s
- `final_fleet_check.log` ??BGRUN END rc=0 after 11s
- `probe_reparent.log` ??BGRUN END rc=0 after 24s
- `traverse_vs_read.log` ??BGRUN END rc=0 after 29s
- `inspect_opreport_copy.log` ??BGRUN END rc=0 after 11s
- `diag_fplabels.log` ??BGRUN END rc=0 after 14s
- `fleet_after_restart2.log` ??BGRUN END rc=0 after 28s
- `lv_restart_unstick.log` ??BGRUN END rc=0 after 74s
- `fleet_after_restart.log` ??BGRUN END rc=0 after 15s
- `find_array_donor.log` ??BGRUN END rc=0 after 109s
- `unstick_fplabels.log` ??BGRUN END rc=0 after 1s
- `fleet_recheck.log` ??BGRUN END rc=0 after 3s
- `clfn_pane.log` ??BGRUN END rc=0 after 0s
- `op_latency.log` ??BGRUN END rc=0 after 22s
- `peer_selection.log` ??BGRUN END rc=0 after 130s
- `astra_gui_verify.log` ??BGRUN END rc=0 after 0s
- `astra_diagnose.log` ??BGRUN END rc=0 after 1s
- `astra_wiring.log` ??BGRUN END rc=1 after 3s
- `astra_probe.log` ??BGRUN END rc=0 after 9s
- `peer_subvi_cost.log` ??BGRUN END rc=0 after 134s
- `boundary_manifest.log` ??BGRUN END rc=0 after 741s
- `subvi_settings2.log` ??BGRUN END rc=0 after 4s
- `subvi_settings.log` ??BGRUN END rc=0 after 1s
- `node_boxes.log` ??BGRUN END rc=0 after 618s
- `find_scheduler3.log` ??BGRUN END rc=0 after 217s
- `find_sched_bypos.log` ??BGRUN END rc=0 after 282s
- `ct_positions.log` ??BGRUN END rc=0 after 230s
- `find_scheduler2.log` ??BGRUN END rc=0 after 228s
- `global_contract.log` ??BGRUN END rc=0 after 359s
- `read_globals19.log` ??BGRUN END rc=0 after 162s
- `locate_state_carriers.log` ??BGRUN END rc=0 after 25s
- `probe_local_class.log` ??BGRUN END rc=0 after 14s
- `cleanup_ctrlvalue.log` ??BGRUN END rc=0 after 1s
- `build_opctrlvalue2.log` ??BGRUN END rc=1 after 12s
- `build_opctrlvalue.log` ??BGRUN END rc=0 after 3s
- `peer_g2.log` ??BGRUN END rc=0 after 155s
- `g2_createsubvi.log` ??BGRUN END rc=0 after 18s

## VIs built under claudeDev

  ASTRA_GUIBENCH_20260913.vi, ASTRA_WIRING_20260913_v1.vi, BenchE_Example8_ForLoops.vi, CAMBENCH_every_image.vi, CAMDUMP_attributes.vi, CAMDUMP_enumerate.vi, DONOR_Ex1_GetControlsWireIndicators.vi, DONOR_Ex3_PrimitiveFunctions.vi, DONOR_arrayops.vi, DONOR_clfn.vi, EMPTY_v0.vi, Ex5_SubVIs_COPY.vi, Ex6_WhileLoops_COPY.vi, FPTARGET_v0.vi, GPU_clfn_target.vi, GPU_kernel_base.vi, GPU_kernel_probe.vi, GPU_kernel_v1.vi, GUIBENCH_v0.vi, HARNESS_Tracking-fit prepped I of r to cal.vi, HARNESS_Tracking-prep I of r.vi, HARNESS_base.vi, HARNESS_compare.vi, HARNESS_copy0.vi, HARNESS_copy1.vi, HARNESS_copyloop.vi, HARNESS_copyloop0.vi, HARNESS_copyloopX.vi, HARNESS_copyloopX0.vi, HARNESS_disp0.vi, HARNESS_disp1.vi, HARNESS_disp2.vi, HARNESS_disp3.vi, HARNESS_disp4.vi, HARNESS_dispI.vi, HARNESS_gpu.vi, HARNESS_gpu2.vi, HARNESS_gpuk.vi, HARNESS_loadcal.vi, HARNESS_par.vi, HARNESS_seq.vi, HARNESS_track.vi, HARNESS_tracking- quadratic fit to phase nghbrd.vi, HARNESS_tracking-calculate phase in neighborhood.vi, HARNESS_tracking-calculate radial profile-openv2.vi, KERNEL_asm.vi, KERNEL_asm2.vi, KERNEL_build_A.vi, KernelBuilder_v1.vi, KernelBuilder_v1_testbench_BACKUP.vi, OP_test1.vi, OpAddShiftRegF_v0.vi, OpAddShiftReg_v0.vi, OpBuildBA_v0.vi, OpBuildCase_v0.vi, OpBuildCase_v1.vi, OpBuildFlatten_v0.vi, OpBuildIA_v0.vi, OpBuildInvoke_v0.vi, OpBuildPN_v0.vi, OpBuildPN_v1.vi, OpBuildUnflatten_v0.vi, OpCLFNBuild_v0.vi, OpCLFNParams_v0.vi, OpCLFNPre_v0.vi, OpCaseFrames_v0.vi, OpConPaneAssign_v0.vi, OpConPane_v0.vi, OpConnect2_v0.vi, OpConnectCtl_v0.vi, OpConnect_v0.vi, OpConstValueN_v0.vi, OpConstValueN_v1.vi, OpConstValue_v1.vi, OpCreateControl_v0.vi, OpCreateControl_v1.vi, OpCreateIndicator_v0.vi, OpCreatePropNode_v0.vi, OpDeleteByLabel_v0.vi, OpDelete_v0.vi, OpExitLoop_v0.vi, OpExitWhile_v0.vi, OpFPLabels_v0.vi, OpFP_v0.vi, OpForLoopIn_v0.vi, OpForLoop_v0.vi, OpForLoop_v1.vi, OpLoopCast_v0.vi, OpLoopCast_v1.vi, OpLoopKernel_v0.vi, OpMakeDefault_v0.vi, OpMoveByIndex_v0.vi, OpMoveByLabel_v0.vi, OpMoveOut_v0.vi, OpMove_v0.vi, OpNetInfo_v0.vi, OpNetInfo_v1.vi, OpNodeInfo_v0.vi, OpNodeLabels_v0.vi, OpNodeTerms_v0.vi, OpNode_v0.vi, OpPanelWiring_v0.vi, OpQueueDequeue_v0.vi, OpQueueEnqueue_v0.vi, OpQueueObtain_v0.vi, OpQueueRelease_v0.vi, OpRemoveBadWires_v0.vi, OpReportAll_v0.vi, OpReport_v0.vi, OpReport_v1.vi, OpReport_v2.vi, OpReport_v3.vi, OpSetAutoErr_v0.vi, OpSetIndexMode_v0.vi, OpSetLabel_v0.vi, OpSetName_v0.vi, OpShiftRegs_v0.vi, OpShiftRegs_v1.vi, OpSubVI_v0.vi, OpSubVI_v1.vi, OpSubVIs_v0.vi, OpSubVIs_v1.vi, OpTunnelInd_v0.vi, OpTunnelRead_v0.vi, OpTunnels_v0.vi, OpWhileCast_v0.vi, OpWhileLoopIn_v0.vi, OpWhileLoop_v0.vi, OpWireCtl_v0.vi, OpWireInd_v0.vi, OpWireSRF_LeftIn_v0.vi, OpWireSRF_LeftOutCtl_v0.vi, OpWireSRF_LeftOutNode_v0.vi, OpWireSRF_RightIn_v0.vi, OpWireSR_LeftIn_v0.vi, OpWireSR_LeftOutCtl_v0.vi, OpWireSR_LeftOutNode_v0.vi, OpWireSR_RightIn_v0.vi, OpWireSource_v0.vi, OpWireSource_v1.vi, OpWireSource_v2.vi, OpWireSource_v3.vi, OpWireSource_v4.vi, OpWireSource_v5.vi, OpWire_v0.vi, OpWire_v1.vi, PARALLEL_build_testA.vi, PARALLEL_kernel_v2.vi, PARALLEL_kernel_v3.vi, PARALLEL_kernel_v3_withdead.vi, PARALLEL_kernel_v3clean.vi, PARALLEL_kernel_v3fix.vi, PARALLEL_smoke.vi, PathToStr.vi, RAWCMD_rotor.vi, READONLY_fourfold_COPY.vi, ScriptDriver_DropForLoop.vi, ScriptTest_Driver.vi, ScriptTest_Target.vi, SetCommand_orig_TEST.vi, SetCommand_signed.vi, SetCommand_signed_TEST.vi, StrToPath.vi, TRACK_kernel_v1.vi, Track N beads PARALLEL over-kernel v1.vi, Track N beads PARALLEL over-kernel v2_KERNEL.vi, Track_v6_CPU_core_v0.vi, Track_v6_CPU_queue_v0.vi



## Answer

Write is disabled in this session (correct for a read-only reviewer), so the review is below.

# PRIOR-ART REVIEW ??delivery-cycle plan (trigger: direction-change)

**Four of the five steps are prior art. Nothing here is `novel`.** A same-day prior-art review of steps 3 and 4 already exists and already returned these verdicts: `archive/peer/2026-09-15-priorart-ownerchain.md:129-131`.

---

## PART A ??THE DIRECTION

### A1 SETTLED ALREADY ??step 2 ("the central risk") closed ~2 h before this plan was written

The plan: *"everything downstream depends on an operation the fleet has never performed??before anything else is built I will establish whether VI Scripting can move a node to a different diagram."*

- `tools/bench/probe_migrate_v3.log:12` ??`PASS M5 THE MIGRATED STATE COMPILES (ExecState == 1)`, 5/5 in 2 s, at 18:30 today.
- `STATUS.md:283` ??*"SETTLED by attempt 5 (`tools/recipes/probe_migrate_v3.py`, 5/5, 18:30) ??the migrated state COMPILES"*, and the same block: *"`GObject.Move` is not needed and was never used."*

What remains open is **scale and runtime** (75 nodes, 21 sibling couplings) ??`STATUS.md:283-297` says so explicitly. Re-establishing feasibility re-runs a settled test.

### A1b SETTLED ALREADY ??the ordering decision already exists, and it is "measure first"

`STATUS.md:124` ??*"The SHELL decision stands; the **ORDERING was refuted** by the plan review and is replaced"*; `STATUS.md:133` replaces it with *"measure the unconditional per-frame path ??p50 **and p99** | replaces all guessed orderings"*, queued again at `STATUS.md:362`. Step 1 is the superseded ordering restated.

### A2 REFUTED ALREADY ??the ~2.5 ms ASI justification, refuted the same day

`archive/peer/2026-09-15-restructure-in-copy-plan.md:11-16`:
> *"The 5.06 ms 'kernel + one serial round trip' is **not** the ordinary-frame cost??So 'move ASI out to win ~2.5 ms per frame' is **void**, and ASI-first ordering has no performance support."*  ??and line 93: *"replace 'kernel, then ASI, then display' with 'measure unconditional latency??"*

**Does it still apply? The refuted half does.** `docs/camera-acquisition-facts.md:142-152` (the user's correction) restores ASI to the critical path ??but on **p99 / frames-dropped-during-focus** grounds, *"not an average-throughput one"* (line 148-149). The plan cites the throughput number ("the difference between 150 Hz and 200 Hz"), which is precisely the half that stayed dead. ASI-owns-its-loop survives; *"largest single win, so it goes first"* does not.

### A3 CONTRADICTED ??the plan's central number contradicts its own source file, 55 lines apart

Both sides, same file `docs/camera-acquisition-facts.md`:

| line | text |
|---|---|
| 140 | **"ANSWERED: the frame loop does NOT transact serial every iteration (2026-09-12)"** |
| 155-167 | the unconditional top-level diagram **"holds five nodes"**; the real serial VIs "sit **inside** that case, on diagram 4 ??not unconditional" |
| 169 | **"So serial does not block 150 Hz."** |
| 195-198 | *"Kernel + a single serial round trip is **5.06 ms of the 6.00 ms** ??doing so returns ~2.5 ms, which is the difference between 150 Hz and 200 Hz"* ??**the passage the plan quotes** |

And `:177-181` names what *is* paid every frame: **two `Value` property nodes = two UI-thread round trips** ??a different quantity and a different fix from the one step 1 performs.

### A3b CONTRADICTED ??"the two consumers of wire 751" is false in our own census

`tools/bench/census_opwiresource_v5.log` ??**three**, not two:
```
161:  t0 'reference'  wire 751   (node 4, uid 482 ??Property Node)
183:  t0 'reference'  wire 751   (uid 163)
221:  t3 'reference'  wire 751   (uid 1221)
181:  t4 'Owner'      wire 751   (uid 157 ??the source the plan deletes)
```

### A3c CONTRADICTED ??STATUS still carries the index rule NAMES.md retracted, and step 5 rests on that class of rule

| file | text |
|---|---|
| `STATUS.md:321` | *"a newly created Diagram lands at **Traverse index 0**, not at the end (measured)"* |
| `docs/NAMES.md:518-522` | *"**That was wrong** ??it was the hash order of a set??attempt 4 measured the same body (uid 472) at **Traverse index 1**??**there is no rule about where a new diagram lands, and looking for one is the error.**"* |

Step 5 proposes a different rule (`count("Diagram") - 1`) for the same job.

### A4 UNREAD EVIDENCE

1. `archive/peer/2026-09-15-priorart-ownerchain.md` ??reviews steps 3 and 4, verdicts at 129-131; its 짠3 (lines 111-117) is the exact defect this plan re-introduces.
2. `tools/recipes/build_opownerchain_v0.py:64-69` ??**already fixed**: *"THE THIRD CONSUMER??wire 751 has THREE consumers, not two ??node 163, node 1221 AND node 482 ??and `build_opwiresource_v5.log:35-39` records that the first v5 rewire failed for exactly this reason."*
3. `docs/NAMES.md:509-532` ??the write-up of the three lost 0a runs and the helpers step 5 should use.

---

## PART B ??THE ARTIFACTS

### B1 ALREADY BUILT ??step 4's recipe exists, and the plan's wording regresses it

`tools/recipes/build_opownerchain_v0.py`: donor at line 54, uid table 57-62, prediction contract B1-B6 at 30-38, three-consumer fix at 64-69 (`REWIRE_SINKS` line 69 lists all three). **Never run** ??no `build_opownerchain_v0.log` exists ??so the *build* is open, the *design* is not. Rewriting it from the plan's two-consumer description undoes the correction. Step 3's recipe also exists: `tools/recipes/build_opgeterrors.py`.

### B2 ALREADY FAILED ??`VI.Get Errors` (452), twice, cause recorded, cause unaddressed

`tools/bench/build_opgeterrors.log`:
```
 1: BGRUN START 2026-09-09 12:45:12 ??build_opgeterrors.py
 7: assembled: ExecState 0 outputs ['reference out', 'error out 2']   8: STOP: not saved   9: rc=5
10: BGRUN START 2026-09-14 01:34:19 ??build_opgeterrors.py
16: assembled: ExecState 0 outputs ['reference out', 'error out 2']  17: STOP: not saved  18: rc=5
```
Cause: `docs/toolkit-capabilities.md:147` (*"no `Errors`, no `Details`"*), `:149` (*"the **member selection** is silently refused"*), `:184-186` (the three private ini tokens *"were already True throughout ??they were never the missing piece"*), `:244` (logged as standing failure).

**Releasable, and here is exactly how.** `docs/toolkit-capabilities.md:170-179` names two routes the failures did **not** cover: (a) *"`ID String = "Get Errors"` with `Allow Alternate Names? = TRUE` ??that separates an ID-format problem from access filtering"*; (b) *"`Create from Reference` ??a donor VI plus a scripted copy is a real route"*. A plan naming (a) or (b) escapes this citation. "Build method 452 as an op" does not.

### B2b ALREADY FAILED ??the step-4 rewire's failure mode, with its fix, on record

`tools/bench/build_opwiresource_v5.log:35-38`:
```
35: DIAG unwired sinks after the rewire: [??(482,'Property Node','reference') ??
37: DIAG re-fed node 482 (Property Node) 'reference' from the Owner output
38: ExecState per step: [('copy of v4',1), ('wrong Owner wire removed',0), ('owner-uid branch rewired',0), ('orphaned references re-fed',1)]
```
Deleting the Wire-specific front section removes node 157, wire 751's **source**; 482 is orphaned ??ExecState 0.

### B3 HELPER EXISTS ??step 5 hand-rolls what `new_since()` returns

`docs/NAMES.md:526-528` ??*"`gscript.new_since(target, cls, before_uid_set)` ??each carries its real Traverse index `i` **and** its uid. Its own docstring says it: 'Use this, **NOT** position matching, to identify what a mutating Op just created.'"* Plus `loop_diagram()` (`:529-531`) and *"verify arrival by **listing** that diagram's contents (`subvis`), never by a whole-VI count"* (`:532`). `probe_migrate_v3.log:5` did exactly this ??*"body uid 882 at Traverse index 1"*. `count("Diagram")-1` is the named cause of the two void runs (`docs/NAMES.md:515`, `STATUS.md:322`).

### B4 ALREADY MEASURED ??step 4's acceptance oracle is written down

`archive/peer/2026-09-15-priorart-ownerchain.md:105-107` ??`docs/diagram-hierarchy.md:46` (10407 on diagram 43), `docs/keystone-op-spec.md:593` (diagram 43 = uid 639), `tools/bench/diagram_tree_main.json:370,397`. The recipe already encodes it at `build_opownerchain_v0.py:36-38`.

---

```
PRIOR-ART: settled-already      (step 2 ??probe_migrate_v3.log:12, STATUS.md:283)
PRIOR-ART: settled-already      (step 1 ordering ??STATUS.md:124,133)
PRIOR-ART: refuted-already      (step 1 ASI-first ??restructure-in-copy-plan.md:11-16,93)
PRIOR-ART: contradicted         (camera-acquisition-facts.md:140,169 vs :195-198)
PRIOR-ART: contradicted         (wire 751 consumers ??census_opwiresource_v5.log:161,183,221)
PRIOR-ART: contradicted         (STATUS.md:321 vs docs/NAMES.md:518-522)
PRIOR-ART: unread-evidence      (priorart-ownerchain.md; build_opownerchain_v0.py:64-69)
PRIOR-ART: already-built        (tools/recipes/build_opownerchain_v0.py ??written, corrected, unrun)
PRIOR-ART: already-failed       (VI.Get Errors 452 ??build_opgeterrors.log:1-18; toolkit-capabilities.md:147,244)
PRIOR-ART: already-failed       (orphaned node 482 ??build_opwiresource_v5.log:35-39)
PRIOR-ART: helper-exists        (new_since / loop_diagram / subvis ??docs/NAMES.md:526-532)
PRIOR-ART: already-measured     (owner oracle 10407 ??Diagram 639 ??priorart-ownerchain.md:105-107)
```

The only genuinely open work in this plan is step 4's **execution** (the recipe exists and has never been run) and step 3 **if** rewritten onto one of the two untried routes at `docs/toolkit-capabilities.md:170-179`.

I took no lock, opened no `.vi`, and changed nothing.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
