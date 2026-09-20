# priorart-master-plan

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.7071  in 50 / out 36465 / cache-create 196589 / cache-read 3658640  (489s, 33 turn(s))
- **date:** 2026-09-16
- **outcome:** ANSWERED (494s)
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
tags: [master-plan, pre-rig, parallelisation, seven-loop]
---

# Master plan ??EVERYTHING achievable before the rig is reassembled

**User's instruction, 2026-09-16:** *"?ъ씠??10 怨꾪쉷? ?됲뻾猷⑦봽 以鍮꾩옉?낅쭔 ?덈뒗 寃?媛숈??? ?닿? 紐낆떆?섍린
?꾧퉴吏??rig 議곕┰ 吏곸쟾源뚯? ?????덈뒗 紐⑤뱺 ?뚮옖???꾩슂?? ?꾩껜 ?뚮옖 諛??몃? ?뚮옖 ?ㅼ떆 以鍮꾪븷 寃?"*

Cycle 10's plan was preparation only. This replaces its **scope** (its technical content survives as track A) and
holds **until the user announces reassembly** ??the same announcement that closes the hardware-permission window.

## The reframing that changes the schedule

"Needs the rig" had been one undifferentiated category, and it was wrong. Three different physical dependencies
were being treated as one:

| dependency | available now? | consequence |
|---|---|---|
| **beads in a mounted flow channel** | ??no | genuinely blocked ??real tracking, real bead loss, force measurement |
| **motors and serial** (magnet, rotor, ASI comms) | ??**yes, and only now** | the user reversed the motor ban *for this window*. Reassembly CLOSES it |
| **the camera** | ??yes | acquisition performance does not depend on what is in the image. **No beads needed** |

So the priority rule for this plan: **track C (hardware) outranks track D (building) wherever they compete**,
because D can be done at any time and C cannot. Live acquisition acceptance ??the test that turns a replay artefact
into something runnable ??was parked as "needs the rig" and does not.

---

## Track A ??Finish the map  *(LabVIEW read-only + offline; no hardware)*

The original's diagram is only 129/170 resolved, and the unresolved part is exactly what the split order depends on.

| # | work | needs | produces |
|---|---|---|---|
| **A1** | **`OpOwnerChain_v0`** ??the missing link is **structure ??the diagram it sits on**, NOT node ??owner (that already works). `tools/recipes/build_opownerchain_v0.py` exists, corrected, **never run** | LabVIEW RO | the reader |
| **A2** | **Validate owner semantics per structure class before any walk.** The measured fact (`NAMES.md:864-866`) is scoped to `CaseStructure` ??1 of the main VI's **6** classes (3 WhileLoop, 17 ForLoop, 37 CaseStructure, 21 FlatSequence, 4 Sequence, 2 EventStructure). Ground truth we hold: `WhileLoop#637`?뭗iagram 43, `ForLoop#1359`, `CaseStructure#10407`. FlatSequence gets a **round-trip** check against `diagram_tree_main.json` | LabVIEW RO | the acceptance set |
| **A3** | **Complete the 170-diagram hierarchy** ??the 41 unresolved plus every FlatSequence link, replacing position matching (the diagram was Clean-Up'd, so position means nothing) | A1, A2 | `docs/diagram-hierarchy.md` at 170/170 |
| **A4** | **The frame loop's TRUE membership** ??body **and all nested frames**. The body-only list is already written (`frame-loop-anatomy.md:40-55`, 6 subVIs incl. ASI #48); only the nested delta is new | A3 | the member list |
| **A5** | **The unconditional per-frame path** ??what executes every iteration vs. conditionally. **This is the number the whole split order rests on** | A4 | the split order input |
| **A6** | ?넅 **Find the autofocus decision path.** The user has never adjusted focus by hand; **software** re-adjusts on off-focus. So something computes "off focus" and writes `+Inc`/`-Inc`/`Focus inc`. Find every writer (Value property writes, locals, subVI calls) and the criterion that gates them | A3 | which loop ASI belongs in |
| **A7** | **Every VISA/serial call site inside A4's membership**, enumerated ??this is CLAUDE.md rule 1c's audit, and the list is what the restructure must empty | A4, A6 | the eviction list |
| **A8** | **Census A ??Case #10445 frames**, before the reseed `Or` collapse | LabVIEW RO | reseed input |

**A6 is new and it is a stop-the-line item.** Until the autofocus path is identified we do not know how often the
expensive ASI branch fires, what triggers it, or which loop owns it ??and CLAUDE.md rule 1c says a mechanism that
*can* stall the frame loop is disqualified even if it usually does not.

## Track B ??Price the frame budget  *(fixture, no hardware)*

| # | work | needs | produces |
|---|---|---|---|
| **B1** | **Instrument a copy, replay all 10,043 fixture frames, p50 AND p99 per stage.** An average hides the cliff; the defect is frames dropped in the tail | A5 | the per-stage budget |
| **B2** | **Which owner dominates** the 6.00 ms budget ??measured, not assumed | B1 | restructure step 3's target |

## Track C ??The hardware window  *(motors 쨌 serial 쨌 camera. NO beads. CLOSES AT REASSEMBLY)*

?좑툘 **The ASI piezo stays excluded** (CLAUDE.md rule 1b) ??verify it is still detached before anything touches that
axis. C1 is comms only, no motion on that stage.

| # | work | needs | why it cannot wait |
|---|---|---|---|
| **C1** | **True ASI VISA round-trip latency, p50 and p99**, at the real `WHERE` command length. `tools/bench/serial_roundtrip_asi.ps1` already exists ??scope it, do not rebuild it | serial | rule 1c is about stalls, so the **tail** is the quantity |
| **C2** | **Per-frame cost of motor reading** against the requirement's claim that it is a bottleneck | A7 + motor | the requirement names this explicitly |
| **C3** | ?넅 **Live camera acquisition at 150 Hz: `Images Missed` = 0, buffer-number continuity, acquisition-call latency incl. p99.9 and max.** **Needs no beads** ??only the camera | camera | this is the test that makes anything *runnable*; it was wrongly deferred |
| **C4** | ?넅 **`Last` vs `Next` measured on the real camera**, not modelled. The 74.9 Hz vs 123.0 Hz figure behind the design decision is a calculation | camera | the design rests on it |
| **C5** | **Scheduler ??motor command timing**: an existing 3-row schedule produces identical translation commands **and timings** (restructure 짠5 stage 3's acceptance) | motor | needs the motor to actually move ??available now |
| **C6** | ?넅 **Observe the autofocus path actually firing**, once A6 says what triggers it ??read-only observation, no piezo motion | A6 | turns A6's static answer into a rate |

## Track D ??Build the seven loops **inside a copy of the original**

Rule 1 unchanged: the original is never touched. The in-copy migration method is **proven end to end**
(`probe_migrate_v2` 3/3, `probe_migrate_v3` 5/5, `ExecState == 1`). Untested is SCALE and RUNTIME, not feasibility.

| # | loop / step | needs | acceptance |
|---|---|---|---|
| **D1** | **One vertical slice**: acquisition ??owned image handoff ??queue core ??frame-identified result, with stop, error and overload. `Buffer Number Mode = Last`; no free slot ??skip the read; buffer number is the time axis | A5, B2 | fixture bit-identical + C3 live |
| **D2** | **Reseed slice** ??`ReseedMux.vi` + loop-level selector, integrated into `Track_v6_CPU_queue_v0` | A8 | **all 10,043** frames bit-identical (today: first 10,018) |
| **D3** | **Split whichever owner B2 says dominates** | B2 | fixture bit-identical |
| **D4** | **Scheduler loop** ??cycle state machine; commands travel as **one versioned cluster through a single-owner queue**, never as separate locals (peer-corrected 2026-09-12: four non-atomic writes let the motor read a new speed with an old force) | A3 | C5 |
| **D5** | **Motor loop** ??motor READING out of the frame loop | A7, C2 | fixture + C5 |
| **D6** | **File writer loop** ??consumes the results queue, lossless FIFO | D1 | no result dropped or reordered |
| **D7** | **Display / UI loop** ??10??0 Hz gate + `Defer Panel Updates`; Image Display route, not Picture (measured: saves ??.9 ms CPU per shown frame) | ??| C3 still passes with the display visible |
| **D8** | **ASI / focus loop** ??**exclusively owns the VISA session** (case #10407's `Outgoing Handle` carries resource ownership, not a value), reaching the frame path only through a non-blocking handoff | A6, A7, C1 | rule 1c: the frame loop transacts no serial |

## Track E ??Acceptance reachable without beads

| # | test | level |
|---|---|---|
| **E1** | all 10,043 fixture frames bit-identical through the restructured VI | functional, numeric |
| **E2** | live acquisition (C3) still clean with every loop running and the panel visible | functional, live |
| **E3** | 3-row schedule ??identical translation commands and timings (C5) | functional, hardware |
| **E4** | three-way benchmark ??original 쨌 CPU-parallel 쨌 GPU ??on the fixture, no motor | functional, numeric |
| **E5** | back-pressure + soak: deliberately slow tracking and disk for minutes, not an 8 ms injection | functional, live |

## Track F ??What genuinely waits for reassembly  *(and nothing else does)*

Only these, and each names the missing physical thing:

- real bead **tracking** end to end ??needs beads in a mounted channel;
- **reseed on a real bead loss** ??needs a bead that actually comes unstuck (the fixture's 13 recorded loss frames
  cover the logic, not the live path);
- **force / extension** measurement ??needs beads and field;
- the **supervised pilot experiment** the user runs to accept the whole thing.

---

## Ordering

1. **A1 ??A2 ??A3** unblocks almost everything; nothing else can be correctly ordered without it.
2. **C1, C3, C4 start immediately and in parallel** ??they depend on no analysis and their window closes.
3. **A6 before any decision about the ASI loop.** It is a blocking question, not a measurement detail.
4. A4/A5 ??B1/B2 ??D3. Judgement returns at D1, when B2's numbers exist.
5. D2 can proceed in parallel with the D4?밆8 splits once A8 lands.
6. Track F is scheduled with the user, after E1?밇3 pass.

## What this plan does NOT decide

It does not fix `docs/restructure-plan-4.6.md` 짠4 (whose construction method still says "build the top level fresh"
instead of the decided in-copy method) or 짠5's stage-2 acceptance (which says all frames where the truth is the
first 10,018). Those are edits to an existing document and are queued behind this plan's approval.


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

## NEXT ??cycle 10 has been REVISED; it is much smaller than it was

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

1. **`guard_cycle`'s cycle clock is wrong and blocks the first build of every cycle.** `overdue = len(since) >= 10
   or hours >= 8.0`, where `hours` counts time **since the last retrospective**, not time spent building. One
   337-byte device self-test plus an overnight gap trips it. Proposed fix: measure the span of *unreviewed build
   logs* instead. **Not applied ??the session it blocks must not widen it** (`rule-evaded`). Needs the user.
2. **`frontmatter.py` can silently open that gate**: `guard_cycle.newest_retrospective()` picks by **mtime**, and a
   bulk frontmatter pass rewrites every peer file's mtime. `audit_cycle` already learned this and uses filename
   dates; `guard_cycle` did not. 19 reviews still lack frontmatter and annotation (audit A4) ??**do not run the
   bulk pass until the gate reads dates**.
3. **`docs/restructure-plan-4.6.md` 짠3 still specifies `Next` and a software `timestamp`** in the acquisition loop,
   and 짠4's construction method is "build the top level fresh" ??both superseded above. Corrected in the 2026-09-16
   lint pass? 짠3 yes; **짠4 and the 짠5 stage-2 acceptance still need revision.**
4. `Global motor pos.vi` ??write-only here; **user: a readability container covering all motors, keep it** (not
   blocking).

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

Prior-art review complete. **Zero `novel`** — 13 findings, every one with a file and line. The plan's technical content is largely right; what it repeatedly does is schedule work our own files already did, and one of its stated motivations is factually false.

---

# PART A — THE DIRECTION

## A1. C4's stated reason is false: `Last` vs `Next` was MEASURED on this camera, not calculated

`docs/pre-rig-master-plan.md:69` — *"`Last` vs `Next` measured on the real camera, not modelled. The 74.9 Hz vs 123.0 Hz figure behind the design decision is a calculation"*.

It is not a calculation. `docs/camera-acquisition-facts.md:64-72`: *"The same sweep at 150 Hz with `Buffer Number Mode` = `Last`… | 8 ms | **74.9 Hz** | **123.0 Hz** |"*, from `tools/bench/camera_budget_sweep.py` on the real JAI SP-5000M-USB via `niimaqdx.dll` (`:44-49`). Same numbers at `archive/bench-2026-09-12-camera-identity/REPORT.md:122-123`, and `archive/benchmarks/INDEX.md:40` (row 19). The only thing not measured is the same comparison through **LabVIEW's** `IMAQdx Get Image` rather than the C API. As written, C4 is a re-run of a closed measurement.

## A2. C3's acceptance metric contradicts the settled design

C3 (`:68`) makes **`Images Missed` = 0** the criterion. The settled readout is `Buffer Number Mode = Last` (STATUS.md, "camera readout"). `docs/camera-acquisition-facts.md:79-81`: *"`Images Missed` is meaningless in `Last` mode for the same reason — a skipped buffer there is intentional, not lost work."* NI's own `Acquire Most Recent Image` has no such indicator at all (`:439-440`). The phrase is inherited verbatim from the pre-`Last` deferral lists (`archive/peer/2026-09-16-priorart-prior-art.md:519`, `:541`) and predates the 2026-09-15 decision. The buffer-number continuity C3 also lists is the correct metric; the `Images Missed` half must go.

## A3. Our own camera file contradicts itself about `Camera Name` — and C3/C4 must pick a route across that contradiction

- `docs/camera-acquisition-facts.md:13-15`: *"the examples' `Camera Name` is an IMAQdx Session control that reads back as `('', 0)` and could not be set from Python, and an empty name opens a dialog that blocks every later COM call until LabVIEW is killed."*
- `docs/camera-acquisition-facts.md:429` (same file, 416 lines later): *"**`Camera Name` is a plain string control.** The one unknown in driving a harness over COM… simply does not arise."*

Both cannot be true of the same VI. This is the "summary line contradicts its own section" case, and it sits directly under C3/C4's feet.

## A4. C2 is already measured, and the plan escalates it above what its own predecessor said

C2 (`:67`) lists `needs: A7 + motor`. `docs/motion-path-audit.md:84-99` measured it on the real PI C-863.11 Mercury over COM3: `POS?` median **2.56 ms** (min 2.49, p95 2.63, max 2.64, 30 samples; one 11.67 ms outlier in 150), model **1.2 ms fixed + 86.8 µs/byte**, four reply lengths agreeing to 0.2 ms. `:108-114`: *"The serial read is not slow, and it cannot be made much faster."* MOV/VEL costing two round trips is at `:58-62`.

`docs/cycle10-plan.md:80` already disposed of this: H3 is *"largely arithmetic over numbers we already have (`docs/motion-path-audit.md:58-62, :90-98, :108-120`)"*. The open quantity is the per-frame **rate** of reads, which A7 yields offline. Nothing on record asks for a new round-trip measurement.

## A5. A6 is not new, and most of it is answered in a document the plan never cites

This is the costliest finding, because A6 is declared *"a stop-the-line item"* (`:48`) that blocks the ASI split order, and it is listed as needing A3 — the 170-diagram walk.

`docs/main-vi-panel-map.md:538-559`, **measured 2026-09-14** (`report_all(main,"Node")`, 626 nodes, 21 `ControlReferenceConstant` nodes), already answers A6's search:

| diagram | the three focus buttons go to |
|---|---|
| 16 (startup) | `check N bead pos v3-kimlab.vi` (`-Inc/+Inc/Focus inc reference`) |
| 43 (frame loop) | `ASI_adjust focus-subvi.vi` |
| 99 (display loop) | `ASI_adjust focus-subvi.vi`, second call site |

And two of A6's three search categories are closed with a **negative** answer: `docs/main-vi-panel-map.md:618` lists `Focus Step (F1)`, `+ Inc (PgUp)`, `- Inc (PgDn)` among *"bare-terminal objects still without a `Value` node"*; `:282-284` shows no wired terminal; `:418` shows no local either. So there are no `Value` property writes and no locals to find.

Further, the criterion A6 says is unidentified has a recorded candidate: `docs/keystone-op-spec.md:594` — *"the autofocus **Case 10407** driven by **bead 2's cal-slice index**"* — corroborated by `tools/bench/which_loop_owns_motor.log:13` (`diagram 73 … ASI move → CaseStructure#10407`). The panel also carries wired controls `Auto-Focus` (#38) and `Limit of Auto-Focus` (#48) (`main-vi-panel-map.md:318`, `:328`).

**Consequence for the ordering:** A6 does **not** need A3. The call sites are already localized, and `tools/bench/read_asi_focus.py` already reads that subVI's nine diagrams (`camera-acquisition-facts.md:181-194`). The stop-the-line item can be closed from existing files plus one subVI read — which also means C6 and D8 are not behind the hierarchy walk.

## A6. The ordering is the one the outcome review refuted, and it has grown since

`archive/peer/2026-09-15-outcome-review-20260915.md:163`: *"the current `NEXT` starts with another reader Op, frame-polarity tooling, and a structural census before live camera work. **That is backwards for outcome risk.**"* Its prescribed order (`:165-173`): reseed → live acquisition → minimum scheduler/motor/save → *then* structural confirmation. `:225` puts *"additional measurement campaigns not tied to the live acceptance or saved output"* under **Abandon**. It fired `scope-inflation` and `tooling-over-delivery` (`:230`, `:234`).

The plan's Ordering §1 and §4 put A1–A3 first and return judgement at D1 behind A5 and B2 — ten analysis/measurement items before the first delivery slice, sixteen before the seven loops.

**What does NOT refute the plan, stated plainly so this verdict is not read as wider than it is:** the user overrode the review's *hot-path-only* recommendation (STATUS.md: acceptance bar **C**, restructure inside a copy), and on 2026-09-16 explicitly chose the reader over a delivery slice (`docs/cycle10-plan.md:15-16`). A1 is authorised. What was authorised was **one** reader; Track A is now eight items, Track B two, Track C six. CLAUDE.md:5 (rule 5): *"An `OUTCOME-VIOLATION` is NOT answered by building a device… the next cycle becomes a **delivery** cycle, and on repetition the work stops for a re-plan with the user."*

## A7. Unread evidence

- `docs/main-vi-panel-map.md` — the obvious document for A6, cited nowhere in the plan.
- `docs/motion-path-audit.md` — the obvious document for C2/A7, cited nowhere.
- `archive/peer/2026-09-15-outcome-review-20260915.md:151` — under *"Do not build"*: *"the currently planned `VI.Get Errors` reader **and `OpCaseFrames_v0` structural confirmation**"* — A8's dependency.

---

# PART B — THE ARTIFACTS

## B1. A8 depends on an op that failed five times; the plan says only "LabVIEW RO"

`CLAUDE.md:212`: *"`OpCaseFrames_v0` looked closed-spec and **failed five times** — grinding is more expensive than the judgement it avoids."* Recorded cause: `archive/2026-09-15-status-cycle7-reseed-measurements.md:43-44` — *"two property nodes created before either was wired, so the VI was broken at gate A; the recipe now builds one node at a time."* Method and property IDs: `docs/stage2-assembly-step-e.md:216` (`Frames[]` 6363801, `Frame Names` 6365002). A8 (`:46`) carries none of this, and the failure budget rule (CLAUDE.md, MATERIAL sessions, budget = 2) applies to it directly.

Census A itself is genuinely still required — `docs/stage2-assembly-step-e.md:180`: *"Case #10445 may not be collapsed into an `Or` until its frames are read"*. It is the **route** that is already-failed, not the need.

## B2. B2's question already has a measured answer

`docs/camera-acquisition-facts.md:92-101` is the per-stage budget table: budget 6.00 ms; acquisition 0.12 ms (2 %); CPU kernel 2.43–2.87 ms (~42 %); one serial round trip 2.56 ms (~43 %). Display was added since: `archive/benchmarks/INDEX.md:43` (row 22) — construction ≈2.7 ms CPU + Picture paint ≈6.5 ms visible, *"the visible route (8.1 ms) exceeds the 6 ms/frame budget at 150 Hz by itself"*; `:46` (row 25) — Image Display +1.0 closed / +6.9 visible, ≈1.9 ms CPU saved (the number D7 cites, correctly).

So "which owner dominates" is answered: display, then serial, then kernel. What B1/B2 genuinely add is the **p99, in situ, inside the original's frame loop** — which `docs/frame-loop-anatomy.md:98-104` already frames as open (*"Which case frames are actually taken each iteration… the 75-node figure is an upper bound"*). Worded as *"measured, not assumed"*, B2 reads as a first measurement and will re-derive four numbers we hold.

## B3. C3's numbers, in the exact hardware state the plan treats as its discovery

`archive/bench-2026-09-12-camera-identity/REPORT.md:10-12`: *"**Hardware state:** rig disassembled, motors detached, camera connected. Operating all four instruments was cleared by the user for this state."* The reframing "camera needs no beads" was not only true then — it was exercised then.

- 150 Hz with zero frames lost: `REPORT.md:101` — 149.99 Hz, frame period 6.67 ms, **budget 6 ms at zero loss**; 7 ms → 75.0 Hz, 299 missed.
- Acquisition-call latency incl. p99 **and max**: `REPORT.md:109` — median 122.6 µs, p90 149, **p99 206, max 218** over 300 calls.

Genuinely new in C3: **p99.9**, and the same figures through LabVIEW with every loop running — which the plan already carries separately as **E2**. As written, C3 and E2 overlap.

## B4. The camera helpers exist and are named for C1 but not for C3/C4

`tools/bench/camera_budget_sweep.py`, `tools/bench/imaqdx_limits.py` (with `--restore`, the standing camera obligation — `archive/STATUS-2026-09-14-full-before-condense.md:53-58`), `tools/bench/imaqdx_ctypes.py`. C1 says *"already exists — scope it, do not rebuild it"*; C3/C4 say nothing equivalent and imply new construction.

## B5. C1's residual is real but smaller than stated, and the safety gate is unmentioned

`docs/camera-acquisition-facts.md:110-126`: ASI measured 2026-09-12 on COM4, 50 exchanges, 0 timeouts — median 1.128 ms, min 0.960, **p90 1.292, max 3.200**; fixed overhead **0.69 ms measured**, and a ~16-byte `WHERE`-style query **~2.1 ms ≈ 35 % of the budget** (*"the 16-byte estimate is an estimate; the 0.69 ms is measured"*). So the gap is p99 at the real command length, not p50 — the plan asks for both. Command safety lives in `archive/peer/2026-09-12-asi-tiger-readonly-commands.md`; the script ships with a blacklist, an **empty-by-default whitelist** and an `-IUnderstandTheRisk` gate (`camera-acquisition-facts.md:128-131`), so `WHERE` must be cleared against that exchange and whitelisted before C1 runs. The plan does not say so.

## B6. E4's three-way benchmark is on record at kernel level

`archive/benchmarks/INDEX.md:36` (row 15): *"Three-way final: seq 8.15 · CPU-par 2.43 · GPU v2 1.14"*; row 16 the drop-in comparison at 5 beads; row 24 the five-core repeat. E4's wording (*"original · CPU-parallel · GPU — on the fixture, no motor"*) is that sentence. If E4 means the **VI-level** comparison it must say so, or it re-runs a closed test.

## B7. D2's reseed rule is already derived and validated to 10,043 frames

`docs/keystone-op-spec.md:604-608`: the driver rule (`run_fixture_compare.py --reseed=main`) — *"if the previous frame's kernel output contains −1, feed x,y,z := cal positions and good := all TRUE… else plain feedback"* — and *"Full rerun with `--reseed=main`: **10,043/10,043 identical, worst dev vs .tra 0.00000**"*. The four selector feeders and the peer-reviewed two-`Select` design are in `archive/2026-09-15-status-cycle7-reseed-measurements.md:17-26`. D2's remaining work is the LabVIEW-side `ReseedMux.vi`, not the rule.

## B8. "An existing 3-row schedule" has no recorded content, and its consumer is not located

C5/E3 accept against *"an existing 3-row schedule"*. `docs/restructure-plan-4.6.md:359`: *"`CycleSchedule` reads back as `((0.0,), (0.0,), (0.0,))`, i.e. **one column**"* — three rows of zero. And `archive/peer/2026-09-15-outcome-review-20260915.md:187`: *"The exact scheduler consumer is an engineering unknown… stages 3–4 remain blocked behind locating or reconstructing it."* C5, E3 and D4 all sit on that unlocated consumer.

---

## Where I found NO prior art — these are clear

A1 (no structure→home-diagram reader exists; `gscript.py:847 loop_diagram()` is the position matcher A3 correctly retires, and `tools/bench/which_loop_owns_motor.log:4-14` prints the blocker 18 times), A2, A3, A4's nested-frame delta, A5, A7, B1's p99, D1, D3, D5, D6, D7, D8, E1, E2, E5 and Track F. Track D's preamble is accurate: `probe_migrate_v2` 3/3 and `probe_migrate_v3` 5/5 with `ExecState == 1` are at `archive/peer/2026-09-16-priorart-prior-art.md:412-443`. D7's ≈1.9 ms is correctly sourced to INDEX row 25.

---

```
PRIOR-ART: contradicted          (A1 — C4 "is a calculation" vs camera-acquisition-facts.md:64-72)
PRIOR-ART: already-measured      (A1 — Last/Next 74.9 vs 123.0, REPORT.md:122-123, INDEX.md:40)
PRIOR-ART: contradicted          (A2 — C3's "Images Missed = 0" vs camera-acquisition-facts.md:79-81)
PRIOR-ART: contradicted          (A3 — camera-acquisition-facts.md:13-15 vs :429 on `Camera Name`)
PRIOR-ART: already-failed        (A3 — NI example over COM failed 3×, REPORT.md:30-34)
PRIOR-ART: already-measured      (A4 — motor read 2.56 ms, motion-path-audit.md:84-99, :108-114)
PRIOR-ART: unread-evidence       (A5 — main-vi-panel-map.md:538-559, :618; keystone-op-spec.md:594)
PRIOR-ART: refuted-already       (A6 — outcome-review-20260915.md:163, :165-173, :225)
PRIOR-ART: already-failed        (B1 — OpCaseFrames_v0, CLAUDE.md:212; outcome-review:151)
PRIOR-ART: already-measured      (B2 — camera-acquisition-facts.md:92-101; INDEX.md:43, :46)
PRIOR-ART: already-measured      (B3 — REPORT.md:101, :109, :10-12)
PRIOR-ART: helper-exists         (B4/B5 — camera_budget_sweep.py, imaqdx_limits.py --restore, serial_roundtrip_asi.ps1)
PRIOR-ART: already-measured      (B6/B7 — INDEX.md:36; keystone-op-spec.md:604-608)
PRIOR-ART: contradicted          (B8 — restructure-plan-4.6.md:359; outcome-review:187)
```

The cheapest way to act on this, if the findings hold when the citations are opened: **A6 comes out of Track A and closes this week from `main-vi-panel-map.md` plus one read of `ASI_adjust focus-subvi.vi`** — it is not blocked on A3, and that removes the plan's own stop-the-line item from the critical path.

## Sources

(extract from answer)

## What was done with it

**The plan this reviewed no longer exists.** `docs/pre-rig-master-plan.md` was rewritten on 2026-09-16 after the
user rejected its framing outright, so most verdicts were overtaken rather than argued with — but three of them
changed the rewrite, and one was independently confirmed by the other reviewer the same hour.

| verdict | disposition |
|---|---|
| **A1** `contradicted` + `already-measured` — C4 called `Last`/`Next` "modelled" when `camera-acquisition-facts.md:64-72` holds a real sweep table | **ACCEPTED**, and codex found it independently. C4 is deleted; the numbers are cited, not re-measured |
| **A2** `contradicted` — C3's `Images Missed = 0` vs `camera-acquisition-facts.md:79-81` | **ACCEPTED** and promoted to plan item 0.3. Under `Last` the same buffer can repeat, which `Images Missed` does not count, so the authoritative trace is **`Buffer Number Out`** with duplicates AND gaps. Both reviewers flagged this |
| **A4** `already-measured` — motor read cost is **2.56 ms**, `motion-path-audit.md:84-99` | **ACCEPTED.** The old C2 was a re-measurement. It now appears only as a budget fact: 2.56 ms of an 11.111 ms frame at 90 Hz |
| **A5** `unread-evidence` — `main-vi-panel-map.md:538-559, :618; keystone-op-spec.md:594` | **ACCEPTED, and it closes the plan's own stop-the-line item.** `keystone-op-spec.md:594` names the autofocus trigger inside diagram 43: *"the autofocus **Case 10407 driven by bead 2's cal-slice index**"* — code-driven, exactly as the user stated, and already written down. A6 drops from "find an unknown control loop" to one read of `ASI_adjust focus-subvi.vi` |
| **A3, A6, B1, B2, B3, B6, B7, B8** | overtaken by the rewrite — the items they cite (a `Camera Name` read, an NI COM example, `OpCaseFrames_v0`, camera budget sweeps, exposure facts) are no longer proposed work. Recorded, not actioned |
| **B4/B5** `helper-exists` | **ACCEPTED**: `camera_budget_sweep.py`, `imaqdx_limits.py --restore`, `serial_roundtrip_asi.ps1` all exist. Note the last one is armed with `$SAFE = @('/')` only and **explicitly refuses `WHERE`** — so any ASI latency item needs an archived external confirmation first, not "scoping" |

**No `REFUTED:` line is added.** Nothing here was refuted; the plan changed instead, which is what the gate's own
instruction says to do. The release is therefore a **fresh prior-art review of the rewritten plan**, whose
direction is materially different (GPU top level first, build-and-run rather than measure).

Cost recorded for the user's token-budget revision: **$4.7071**, 489 s, 33 turns, cache-read 3.66 M. Together with
`2026-09-16-master-plan-attack.md` (codex) and `2026-09-16-priorart-prior-art.md` ($3.47), review spend on this
plan is **≈ $8.2 plus the codex call**. Both prior-art runs earned it: the first caught a misread citation that
would have justified a whole cycle, this one caught four items of already-done work and handed back the autofocus
answer.
