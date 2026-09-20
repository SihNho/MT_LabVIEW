# priorart-prior-art

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $3.4739  in 26 / out 26904 / cache-create 193169 / cache-read 1739018  (356s, 22 turn(s))
- **date:** 2026-09-16
- **outcome:** ANSWERED (357s)
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
---
type: plan
status: current
date: 2026-09-16
tags: [cycle-10, plan, hardware, owner-chain]
---

# Cycle 10 plan ??the owner-chain reader, then the measurements it unlocks (including hardware)

Three user decisions on 2026-09-16 set this cycle. Two of them change direction, so this plan goes to the
prior-art review before anything is built.

## The decisions

1. **"build reader and tools first."** The fork was: build `OpOwnerChain_v0`, or honour the outcome review's
   "further readers are tooling drift" and go straight to a delivery slice. The user chose the reader.
2. **Hardware is no longer deferred.** *"You eventually need to operate the motors and machines before
   reassembling the rig. It includes the motor operation, reading, et cetera. I'll let you know when the rig is
   reassembled??Don't need to hastle around me before I tell you."* The 2026-08-27 motor ban is superseded for
   this window; rig-bound measurements move from "one later batched session" into the current queue.
3. **No serial on the frame path.** *"I don't want to have even a single frame loss coming from the motor
   communication if possible??serial communication through VISA can somehow stall the loop."* And the fact
   behind it: the sample stage drifts by itself (thermal drift, sample-holder pin), so **focus re-adjustment is
   continuous, not rare**, frequency unknown but "not trivial".

## Why the reader, stated as a defect rather than a wish

`docs/diagram-hierarchy.md` resolved **129 of 170 diagrams**; 41 failed the margin test, and several FlatSequence
matches produced a structure uid that appears on no diagram at all. The method is nearest-structure **position
matching**, and this VI was rearranged by Clean Up Diagram, so position carries no meaning ??the 21횞 margin that
justifies `gscript.loop_diagram` was measured on loops 700 px apart and does not generalise to structures tens of
pixels apart. Consequences that are currently unreliable rather than unknown:

- **which loop encloses the 11 PI motor / rotor call sites** ??the doc's own verdict is "a strong indication, not
  a conclusion", and the requirement calls motor reading a frame-rate bottleneck;
- **the unconditional per-frame path**, which the whole split order depends on;
- **the frame loop's true member list** (body + nested frames), which the reseed `Or` collapse needs.

## Steps

| # | step | level of verification |
|---|---|---|
| 1 | **`OpOwnerChain_v0`** ??UID in, owner UID + owner class out. Donor: `OpWireSource_v5` with the `Wire` cast removed; semantics already MEASURED (`docs/NAMES.md:823` ??a node's `Generic.Owner` is its frame Diagram, that Diagram's `Owner` is the structure) | structural: `ExecState == 1` + owner chain reproduced on a known case |
| 2 | **Re-walk the hierarchy with it** ??all 170 diagrams ??owning structure ??parent diagram, replacing every position-matched link; the 41 unresolved and the FlatSequence links are the acceptance set | functional: chains terminate at a top level or a known loop, 170/170 |
| 3 | **Which loop owns the 11 motor / rotor call sites** (`MOV.vi` 횞7, `VEL.vi` 횞4, `POS?`/`TMN?`/`TMX?`/`GOH`, `Magnet2Force` 횞2, Autonics `SetCommand.vi` on diagrams 32/111) | functional, offline from 2 |
| 4 | **The unconditional per-frame path** ??what executes every iteration vs. conditionally | functional, offline from 2 |
| 5 | **Every VISA/serial call site in the frame loop's true membership**, enumerated ??this is decision 3's audit, and the list is what the restructure must empty | functional, offline from 2 |

## Hardware work this cycle (new ??was deferred, now permitted)

Ordered cheapest-first, each a measurement with a number attached. The ASI **piezo** stays excluded; its detached
state is verified from the recorded rig state before anything touches that axis.

| # | measurement | why it matters now |
|---|---|---|
| H1 | **true VISA round-trip latency** on the ASI serial path, p50 and **p99** | decision 3 is about stalls, so the tail is the quantity, not the mean |
| H2 | **how often ASI focus actually fires** during a quiet period with no commanded motion | the user cannot state the rate; "not trivial" is the only bound we have |
| H3 | **per-frame cost of motor reading**, against the requirement's claim that it is a bottleneck | step 3 says which loop it is in; this says what it costs |
| H4 | **rotor negative-angle verification** of `claudeDev\SetCommand_signed.vi` (`PIC -10` ??read back ??.2째) | the last open item on the rotor sign fix; needs the motor to move, which is now allowed |

Rotor counter is at **0**, not the old 100,000-pulse baseline. Restore with `PIC 100000` before the original VI
is ever run again; the new VI does not need it.

## What this plan does NOT do

It does not build a delivery slice, and it does not touch the acquisition/tracking split. Judgement returns after
step 4 and H1?밐2, because the split order depends on their numbers. It also does not revisit the camera design
(free-running camera, `Buffer Number Mode = Last`, no eviction machinery) ??that is settled and separately owes a
peer review before construction, not before measurement.


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
  status: acquired
  owner: Claude (session 2b7a154c)
  since: 2026-09-16 (cycle 10 - build OpOwnerChain_v0, on the user's "build reader and tools first")
  purpose: >
    Build and verify OpOwnerChain_v0 (UID -> owner UID + class), then walk the motor/rotor call sites and the
    frame loop's true membership with it. Read-only against the main VI; scratch VIs under claudeDev only,
    unique name per run.
  state: >
    2026-09-16 - ACQUIRED. Earlier note, still true: a LabVIEW instance has been idle in memory since
    2026-09-15 (34,007 handles vs the ~31,500 fresh-start baseline) and holds stale scratch VIs - restart it
    before the first batch, and use a unique scratch name per run either way.
```

*(The previous block was malformed ??it carried two `status:` keys, `acquired` then `released`, so a parser could
have read either. Fixed 2026-09-16. Custody of the original VI's own hash is the user's, not tracked here.)*

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

## RIG STATE ??disassembled, and that is the WINDOW for hardware work (user, 2026-09-16)

No bead measurement is possible, so anything needing real beads still waits: live acquisition at 150 Hz with
`Images Missed` = 0, real camera jitter and buffer gaps, and reseed on a real bead loss. Fixture work is
unaffected ??the 10,043-frame recording (`archive/bench-2026-09-07-fixture/`) carries 13 real lost-bead frames,
the kernel's per-frame cost is measured on it, and the display paint cost was measured 2026-09-14.

## HARDWARE PERMISSION ??STANDING, until the user announces reassembly (2026-09-16)

*"You eventually need to operate the motors and machines before reassembling the rig. It includes the motor
operation, reading, et cetera. I'll let you know when the rig is reassembled, because it is a crucial point.
Don't need to hastle around me before I tell you."*

- **Motor operation and reading are now expected work, not deferred.** CLAUDE.md rule 1b is REVERSED for this
  window; the 2026-08-27 motor ban is superseded and must not be reinstated from an old summary.
- **Do not ask per incident or per session.** The instruction is explicit.
- **Only the user's announcement closes the window.** Never infer reassembly from silence; stop when it comes.
- Instruments: piezo stage detached 쨌 rotor free 쨌 magnet motor full travel 쨌 camera **on condition of restore**
  (`tools/bench/imaqdx_limits.py --restore`: 1280횞1024, offsets 0, 90.0009 Hz; never write `BinningHorizontal`).
  **The ASI piezo remains the one exception** ??verify it is still detached from the recorded rig state before
  driving it (a check to run, not a question to ask).
- Hardware last touched 2026-09-13 20:1x??0:22 (rotor only, user present); the rotor's counter is 0 by the new
  convention. ?좑툘 Running the ORIGINAL VI (Baseline 200) now would make its first absolute move a 200-turn travel ??
  reset with `PIC 100000` first, or use only the new VI.

**Rig-bound work is therefore NO LONGER deferred to "one later session".** What moves into the current queue:
true VISA/serial latency, how often ASI focus actually fires, the per-frame cost of motor reading, and the rotor
negative-angle verification of `SetCommand_signed.vi`.

## NO SERIAL ON THE FRAME PATH ??user's acceptance constraint (2026-09-16), CLAUDE.md rule 1c

*"I don't want to have even a single frame loss coming from the motor communication if possible??serial
communication through VISA can somehow stall the loop, and cause unwanted frame stop."* Plus the fact behind it:
the sample stage **drifts on its own** (thermal drift, sample-holder pin shifting, unknown causes), so focus
re-adjustment is **continuous, not rare** ??"not trivial", frequency unknown and to be measured.

This retires every plan that deprioritised the ASI loop because "its serial is conditional". The ASI/serial loop
must own its VISA session exclusively and reach the frame path only through a non-blocking handoff, and a
mechanism that *can* stall the frame loop is disqualified even if it usually does not.

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


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

# PRIOR-ART REVIEW — cycle 10 plan (trigger: new-op)

Nothing built, run, or locked. Every finding names a file and line.

---

## PART A — THE DIRECTION

### A1. SETTLED ALREADY — H4 (rotor negative-angle) was already performed in hardware, with the user watching

The plan's H4: *"`PIC -10` → read back → −7.2°) — the last open item on the rotor sign fix; needs the motor to move, which is now allowed."* That exact test is on record as executed and passed:

- `archive/benchmarks/INDEX.md:52` (row 31): *"**Hardware acceptance PASSED 20:22; visible −3-turn / `PAB 0` test PASSED 20:28 with the user watching** (−1080.0° tracked live, back to 0.0°) … `CLL X` zeroed the counter, **`PIC -10` moved −7.2° and the signed copy read −7.2°** while the original read +3 092 376 445.92°; `PIC 10` returned to 0."*
- `STATUS.md`, OPEN list: *"Rotor read sign — **DECIDED and DONE**: `SetCommand_signed.vi` under claudeDev, verified in hardware 2026-09-13 (INDEX row 31)."*

The plan's own STATUS says DONE while the plan says "last open item". **What this citation does not cover:** any edit to `SetCommand_signed.vi` after 2026-09-14. Show one in writing and H4 is released.

### A2. REFUTED ALREADY — step 2 generalises semantics measured for one structure class, and a peer already refused exactly that

`archive/peer/2026-09-15-cycle8-plan-rule-audit.md:124`: *"`OpOwnerChain_v0` … is donor-evidenced only for owner chains **inside a Case frame** (`docs/NAMES.md:823`), but item 2 plans to use it across all 170 diagrams' full nesting (While/For/Event/Sequence too) — untested generalization … **Test against one node under each structure type before running it project-wide.**"*

The plan's step-1 acceptance is *"owner chain reproduced on a known case"*, and the recipe's gate B6 (`tools/recipes/build_opownerchain_v0.py:36-38`) uses `CaseStructure#10407` — the one class the semantics were measured on. Step 2 then walks 170 diagrams whose unresolved population is dominated by FlatSequence (`docs/diagram-hierarchy.md:66-69`: several FlatSequence matches give a structure uid that *"appears on no diagram at all"*; *"treat every FlatSequence-owned link in the JSON as unverified"*). The acceptance set cannot detect the failure the reviewer named. Cheapest release: widen it to one node per structure class — `tools/bench/which_loop_owns_motor.log:4-22` already lists candidates of each (CaseStructure#3826, Sequence#3593, FlatSequenceFrame#43914, ForLoop#28670, WhileLoop#637).

*Not a blocking finding:* the outcome review's "further readers are tooling drift" (`archive/peer/2026-09-15-outcome-review-20260915.md:151,163,211,221`) is released in writing by the user's decision quoted at `docs/cycle10-plan.md:15`, and `archive/peer/2026-09-15-retrospective-cycle9.md:103` independently names the missing reader as a cost driver. That fork is properly closed.

### A3. CONTRADICTED — two, both load-bearing

**(a) `docs/NAMES.md:823` does not say what three documents say it says.** The plan (`docs/cycle10-plan.md:43`), `STATUS.md:386` and `docs/diagram-hierarchy.md:76-77` all cite NAMES.md:823 for the owner-chain semantics. `docs/NAMES.md:816-828` is about `Constant.Value` 634AC00 returning a void variant for numeric constants — nothing about owners. The real statement is `docs/NAMES.md:864-866`: *"**Owner chain inside a case frame:** a node's `Generic.Owner` is its frame **Diagram**; that Diagram's `Owner` is the **CaseStructure**."* Scoped to a case frame — which is A2's problem. Fix the pointer in all three files, not just the plan.

**(b) H2's premise conflicts with our own reading of the ASI focus VI.** The plan wants *"how often ASI focus actually fires during a quiet period with no commanded motion"*. Our files say it acts on operator input: `docs/camera-acquisition-facts.md:137-138` — *"its `+Inc`/`-Inc`/`Focus inc` inputs are **control references**, which is the shape of a VI that acts only when a key or button says so"*; `:169` — *"It is paid only while a focus key is held"*; `docs/frame-loop-anatomy.md:77-78` — loop C *"already owns the focus keys and the same `Focus inc reference` terminals — uid 15921 there is the same VI."* On a disassembled rig with no sample (`STATUS.md` RIG STATE: *"No bead measurement is possible"*) a key-driven VI fires zero times, and zero is not the user's "not trivial" rate. The discriminating read is offline and cheap: who drives uid 48's `Focus inc reference` on diagrams 43 and 99.

### A4. UNREAD EVIDENCE

- `docs/frame-loop-anatomy.md:40-55` — the frame loop's six subVIs with identifying terminals, the 10 `Value` property nodes, and `:33` (*"uid 5058 sits directly on diagram 43's body, not inside a case frame, so it runs unconditionally on every iteration"*). Steps 4–5 restart this from zero; the real delta is the **nested** frames only, as STATUS itself concedes.
- `tools/bench/which_loop_owns_motor.log:4-22` — step 3's instrument already ran; its output *is* the call-site table, each row resolved to its owning structure and blocked at the same one missing link.
- `archive/peer/2026-09-15-priorart-ownerchain.md` — the prior-art review of this very build, still `verdict: unverified` / `(Claude fills in)` (`archive/peer/2026-09-15-retrospective-cycle9.md:122`). Its findings *were* acted on (see B1); the record doesn't say so.

---

## PART B — THE ARTIFACT

### B1. ALREADY BUILT — the recipe exists, complete, with the last review's fixes already in it

`tools/recipes/build_opownerchain_v0.py:1-42` is the entire build — donor, both rewires, the deletions, and a six-gate contract ending in functional gate B6. It already absorbed the 2026-09-15 review: `:64-69` (*"wire 751 has THREE consumers, not two — node 163, node 1221 AND **node 482** — and `tools/bench/build_opwiresource_v5.log:35-39` records that the first v5 rewire failed for exactly this reason"*; `REWIRE_SINKS` now carries all three) and `:70-72` (the omitted seventh deletion, uid 1329). There is no `tools/bench/build_opownerchain_v0.log`, so **running** it is open; **writing** it is not. Likewise step 2's instrument (`tools/bench/build_diagram_hierarchy.py`, already run three times; its `:19` names `OpOwnerChain_v0` as its designed fallback) and step 3's (`tools/bench/which_loop_owns_motor.py`).

### B2. ALREADY FAILED — no record for this op; one adjacent trap sits on the wire it creates

`docs/NAMES.md:773-775`: *"`Generic.Owner` (6327806) returns a **Generic** reference, and wiring it into a **GObject**-class property node … is a downcast — ExecState 1 → 0."* The recipe routes `Owner` into `ClassName` (Generic-class, legal) and into the TMSC at uid 1221 (the documented remedy), so it does **not** repeat the fault — but gate B5 is the only thing between this wire and that ExecState 0, and `docs/NAMES.md:771-772` warns a uid-equality gate cannot see a broken wire. Keep B5 before the save. No slug.

### B3. HELPER EXISTS — H1 needs a flag, not an instrument

`tools/bench/serial_roundtrip_asi.ps1` already has the COM4 path, the read-only whitelist, the motion/flash blacklist and the `-IUnderstandTheRisk` gate (`:28`, `:32-34`, `:84-85`), and reports `median / min / p90 / max` per command (`:120-123`) with `-Count` (`:32`). p99 is `-Count 500` plus one percentile line at `:121`. PI side: `tools/bench/serial_roundtrip.ps1`.

### B4. ALREADY MEASURED — H1 in part, H3 in its dominant term

**H1:** `docs/camera-acquisition-facts.md:110-126` — COM4, 50 exchanges, 0 timeouts: *"median 1.128 ms min 0.960 p90 1.292 max 3.200"*, decomposed to a **measured 0.69 ms fixed overhead** + 86.8 µs/byte → *"a realistic `WHERE`-style query of ~16 bytes ≈ 2.1 ms"*; also `archive/benchmarks/INDEX.md:40`. The same file states what remains open at `:152`: *"What is still unmeasured is how often 'frequent' is, and **the true `WHERE` latency**."* Scope H1 to the real command at realistic length plus the tail.

**H3:** `docs/motion-path-audit.md:90-98` — `POS?` **2.56 ms** median (min 2.49, p95 2.63), *"1.2 ms fixed + 86.8 µs per byte"*; `:58-62` — *"one motor command costs a send plus an error query, i.e. **two** serial round trips"*; `:108-120` — *"The serial read is not slow, and it cannot be made much faster"* (floor ≈1.5 ms). And `docs/camera-acquisition-facts.md:187-188` — *"The dedicated motor loop is already separate and correct: diagram 20."* H3's remaining content is *whether a motor read sits on the frame path* — step 3's output, not a hardware run — times a number we already have.

---

## MACHINE-READABLE VERDICTS

```
PRIOR-ART: settled-already   (A1 — H4 already run: INDEX.md:52, STATUS.md OPEN list)
PRIOR-ART: refuted-already   (A2 — case-frame-only semantics generalised to 170 diagrams: cycle8-plan-rule-audit.md:124)
PRIOR-ART: contradicted      (A3a — NAMES.md:823 cited for a fact stated at NAMES.md:864-866, scoped to case frames)
PRIOR-ART: contradicted      (A3b — H2's autonomous-focus premise vs camera-acquisition-facts.md:137-138, :169)
PRIOR-ART: unread-evidence   (A4 — frame-loop-anatomy.md:40-55; which_loop_owns_motor.log:4-22; priorart-ownerchain.md)
PRIOR-ART: already-built     (B1 — build_opownerchain_v0.py:1-72; build_diagram_hierarchy.py; which_loop_owns_motor.py)
PRIOR-ART: helper-exists     (B3 — serial_roundtrip_asi.ps1:28, :32, :120-123)
PRIOR-ART: already-measured  (B4 — camera-acquisition-facts.md:110-126, :152; motion-path-audit.md:58-62, :90-98, :108-120)
```

**What survives as novel:** *running* the existing recipe (step 1); the owner-walk of the 41 unresolved diagrams and the FlatSequence links (step 2, once A2's acceptance set is widened); the nested-frame membership delta in step 5; and the true `WHERE`-length ASI latency with a real tail (H1, scoped). Steps 3 and 4 are re-runs of existing instruments over the new link; H3 is arithmetic over existing numbers plus step 3; H4 and the body-only half of step 5 are already done.

Two process notes: the `Write` tool is disabled in this session, so this review exists only in this reply — copy it to `archive/peer/` if it should be gate-visible. And no memory write was due this turn: the message set a task, it did not teach a durable preference.

## Sources

(extract from answer)

## What was done with it

**ALL EIGHT VERDICTS ACCEPTED. No `REFUTED:` line is added, because every citation checked out against the source.**
`docs/cycle10-plan.md` was rewritten rather than released — which is what the gate's own instruction says to do when
the review is right. Verified one by one, 2026-09-16:

| verdict | what I checked, and what I found |
|---|---|
| A3a `contradicted` | **The sharpest finding.** The plan cited `docs/NAMES.md:823` for owner-chain semantics. Line 823 is about `DigitalNumericConstant` property IDs. The real fact is at **:864-866**, under the heading **"Owner chain inside a case frame"**, and it says the Diagram's `Owner` is the **CaseStructure** — scoped to case frames, exactly as the reviewer said |
| A2 `refuted-already` | accepted. Generalising case-frame semantics to all 170 diagrams was already argued against in `cycle8-plan-rule-audit.md:124` |
| A4 `unread-evidence` | confirmed, and it is worse than a missed citation: **`tools/bench/which_loop_owns_motor.log` already ran the walk** and prints the real blocker 18 times — *"cannot step above this structure without the structure→home-diagram link"*. That is the **opposite direction** from the reader step 1 specifies. The plan would have built a tool for a direction that already works |
| B1 `already-built` | confirmed on disk: `tools/recipes/build_opownerchain_v0.py` (9,348 B, written and corrected, **never run**), `tools/bench/build_diagram_hierarchy.py` and `tools/bench/which_loop_owns_motor.py` (both already **run**) |
| A1 `settled-already` | confirmed, and it is a verbatim repeat: **H4 was already executed in hardware** on 2026-09-13/14 with the user watching (`archive/benchmarks/INDEX.md` row 31 — `PIC -10` → the signed copy read **−7.2°**, the `PAB 0` visible test passed 20:28). H4 is deleted from the plan |
| A3b `contradicted` | confirmed, and it invalidates H2's design. `docs/camera-acquisition-facts.md:137-138` records that uid 48's `+Inc`/`-Inc`/`Focus inc` inputs are **control references** — "the shape of a VI that acts only when a key or button says so" — and `:169` that serial is "paid only while a focus key is held". **ASI focus is operator-driven, not autonomous**, so "how often does focus fire during a quiet period with no commanded motion" has nothing to observe. Reconciled with the user's *"focus 조정은 꽤나 빈번하게 발생함"*: it is frequent because the **operator** acts frequently against a drifting stage — which can only be measured during a real experiment, i.e. after reassembly |
| B3 `helper-exists` | confirmed: `tools/bench/serial_roundtrip_asi.ps1` exists (7,822 B, 2026-09-12). H1 needs scoping, not a new tool |
| B4 `already-measured` | accepted |

**Net effect on the cycle:** of five steps and four hardware items, H4 is already done, H2 is unmeasurable in this
window, H3 is arithmetic over existing numbers, step 3 is a re-run of an existing script, and step 5's body-only
half is already written down in `frame-loop-anatomy.md:40-55`. What survives is genuinely small — see the rewritten
plan.

**This is the review's second real save.** Its first run (2026-09-15) found four defects in a pending recipe; this
one caught a misread citation that would have justified a whole cycle. Cost $3.47 / 356 s / 22 turns, recorded for
the token-budget revision the user asked for.
