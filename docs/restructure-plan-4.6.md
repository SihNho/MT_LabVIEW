---
type: reference
status: current
date: 2026-09-14
tags: [docs, plan]
---

# Plan: restructure into `4.6 cpu parallel` and `4.6 gpu parallel`

> **PLAN ONLY — nothing built.** Written 2026-09-12. Requires peer review before construction (CLAUDE.md work cycle
> step 1). The original VI keeps running experiments throughout, which is why this can be done properly rather than
> quickly (user, 2026-09-12: *"실험이야 원본 vi로 하면 되는 일이고 재구성해서 넣자"*).

## 1. Goal

Two top-level VIs — a CPU-parallel build and a GPU build — that reach **150 Hz** acquisition with no frame loss, where
the current code manages 90 Hz with the live image display disconnected because it destabilised frames.

The two files differ in **exactly one loop**. Everything else is shared subVIs.

## 2. The facts this plan rests on (all measured 2026-09-12)

| fact | value | why it matters |
|---|---|---|
| camera ceiling | **247.95 Hz** at 1280×1024, 2×2 binning | 150 Hz is not a camera problem; 65 % headroom |
| per-frame budget | **frame period − ~1 ms** → **6.00 ms at 150 Hz**, 3 ms at 200 Hz | the number everything is held against |
| failure mode | **a cliff** — overrun by 0.3 ms and processed rate halves exactly | no graceful degradation to trade against |
| acquisition cost | **0.12 ms** (2 % of budget) | paid in every design; not worth optimising |
| CPU-parallel kernel | 2.43–2.87 ms (~42 %) | fits 150 Hz, tight at 200 Hz |
| GPU kernel | 1.14 ms above base (~19 %) | the reason the GPU build exists |
| `Last` vs `Next` | 8 ms work/frame → 74.9 Hz on Next, **123.0 Hz on Last**, `acquired` steady | a display loop on `Last` cannot block acquisition |
| ring depth | 10 / 50 / 100 identical | **not a lever**; absorbs jitter only |
| ASI serial | fixed overhead **0.69 ms**, a `WHERE`-class query ≈ 2.1 ms | paid only while a focus key is held |
| frame loop's unconditional non-kernel cost | **two `Value` property nodes** = two UI-thread round trips | **not yet sized — gate G1 below** |

## 3. Target architecture — 7 loops

| # | loop | contents | differs CPU/GPU? |
|---|---|---|---|
| 1 | **Acquisition** | `IMAQdx Get Image` **(`Buffer Number Mode = Last`)** → image-pool slot → enqueue `{slot, buffer#}`; gaps ARE the jump in `Buffer Number Out`. **No free slot ⇒ skip this read**, never block the camera | no |
| 2 | **Tracking** | dequeue → **tracking kernel** → x/y/z → enqueue results, return slot | **YES — the only one** |
| 3 | **Scheduler** | cycle state machine; publishes targets (speed, force, wait, **rotor °**) — ⚠️ **"as local variables" was this row's original text and it contradicts this same file 14 lines below**: `:56` says *"one versioned command cluster through a single-owner queue — **NOT separate local variables**"*, and `:59-63` is the 2026-09-12 peer correction that four non-atomic writes let the motor loop read a new speed with an old force. **The requirement is the invariant (no half-updated target set), and the transport is an open decision** — see `pre-rig-master-plan.md` row 1.3, which records why a cluster is not buildable by the present fleet without a donor typedef. Do not build loop 3 from this cell alone | no |
| 4 | **Motor** | reads targets; translation → poll arrival → rotor absolute (`MovePos`) → confirm → start wait | no |
| 5 | **Stage / focus (ASI)** | ASI serial, autofocus, focus keys — event-driven | no |
| 6 | **Display / UI** | Event Structure; `Last`-mode image; indicator updates behind a 10–20 Hz gate + `Defer Panel Updates`. **Measured 2026-09-14** (`archive/bench-2026-09-14-display-path`): the current route costs ≈2.7 ms CPU to build the picture plus **≈6.5 ms to paint it while the panel is visible** — above the whole 6 ms frame budget, so the gate is not optional. **Image Display route measured the same day (INDEX row 25): +1.0 ms closed / +6.9 ms visible vs Picture 2.9 / 8.0 — use the Image Display in the decimated loop (saves ≈1.9 ms CPU per shown frame), the paint itself stays ~7 ms** | no |
| 7 | **File writer** | consumes the results queue | no |

**Inter-loop transport.** No data wires between loops — a wire between two loops makes them sequential (user's
standing correction). Queues carry the lossless paths, local variables the latest-value paths:

| path | mechanism | why |
|---|---|---|
| 1 → 2 | **bounded queue** | lossless **and order-preserving** — the tracking sequence must not be reordered |
| 2 → 7 | queue | lossless |
| 2 → 6 | local variable / 1-element queue | lossy by design; the display only needs the newest |
| 3 → 4 | **one versioned command cluster through a single-owner queue** | **NOT separate local variables — see below** |
| state/config | local variables | never the UI thread |

**Correction after peer review (2026-09-12).** The first draft published the scheduler's targets as separate local
variables (speed, force, wait, rotor). That is a real defect, not a style question: the four writes are not atomic, so
the motor loop can read a **new speed with an old force**. Multi-field commands travel as **one immutable cluster with
a sequence number and timestamp**, through a queue with a single owning consumer. Local variables remain fine for
genuinely single-field latest-value state.

**Queue mechanics that must be specified, not assumed.** A bounded LabVIEW queue's default enqueue timeout is `-1`,
which **waits forever when full** — "bounded" does not imply "drops". Every enqueue uses a finite or zero timeout and
handles the `timed out` output explicitly. Releasing a queue while another node is waiting on it invalidates the refnum
and raises **error 1122**, so shutdown order is: stop the users, drain, *then* release.

## 4. Construction method — REWRITTEN 2026-09-13 after the method was tested and failed

> ### ⚠️ CORRECTED 2026-09-16 — "build the top level fresh" is superseded by "restructure inside a COPY"
>
> The user decided (2026-09-15) that the seven-loop restructuring happens **inside a copy of the original VI**, not
> in an empty one: the copy already holds the 98 calls, the panel, the state carriers and the wiring, so authoring a
> new top level would mean re-deriving all of it. Rule 1 is unchanged — the original itself is never opened for
> writing; the work happens in a copy under `user.lib\claudeDev`.
>
> **The method is proven end to end, not assumed** (`probe_migrate_v2.py` 3/3, `probe_migrate_v3.py` 5/5, recorded in
> `pre-rig-master-plan.md:73-75`): create a loop inside an existing VI · drop the same subVI in it · wire a control
> across the loop border · delete the original node · `ExecState == 1`, it compiles. `GObject.Move` is not needed.
> What is untested is **scale** (75 nodes, 21 sibling couplings) and **runtime behaviour** — not feasibility.
>
> Everything below this banner still holds and is why the copy route is the right one: extraction by drawing a box
> around a region is dead (the diagram was Cleaned Up; the first candidate seam needed 66 connector terminals), the
> 98 existing subVIs are kept unchanged, and **interface width is the design rule** for any new seam.

> **The "extract, then assemble" method below does not work on this VI. Two findings killed it, in this order.**
>
> **(a) The diagram was Cleaned Up, so position carries no meaning.** The user ran LabVIEW's *Clean Up Diagram* during
> an earlier version bump: *"기능과는 무관하게 싹 다 섞여버렸어."* Clean Up re-lays the diagram out algorithmically —
> it moves nodes without rewiring them — so code that does one job is now scattered and interleaved with unrelated
> code. **A subVI seam cannot be chosen by drawing a box around a region**, because any box cuts through several
> features at once. (Three searches earlier the same day leaned on proximity and had to be discarded; this is why.)
>
> **(b) Measured: the first candidate seam needs 66 connector terminals.** `tools/bench/boundary_manifest.py` on
> diagrams 160–163 (bead selection / cross-hair drawing — the cleanest-looking seam in the VI, already containing two
> calls to the same drawing subVI) reports:
>
> | check | result |
> |---|---|
> | Local / Global / Property / Invoke / FeedbackNode / EventStructure inside the seam | **all CLEAN — 0** |
> | subVI calls inside | 6 |
> | **wires crossing the boundary** | **66** |
>
> A LabVIEW connector pane holds at most 28 terminals. The crossing wires are individual scalars — `x`, `y`, `array`,
> `element`, `new element/subarray` — not a functional interface. **The state-carrier hazards the peer review warned
> about were absent; the seam failed on interface width instead**, which no one had predicted.
>
> Trying further seams would not help: the cause is not seam selection but the scrambled layout, so any box drawn on
> this diagram will look similar.

### The method that replaces it: rebuild the top level, reuse the subVIs

The main VI already makes **98 subVI calls** — the tracking kernel, `Motor control v5`, `ASI_adjust focus-subvi`, the
cross-drawing VI, the PI and IMAQdx drivers. Those are real, tested, functional units and they are **kept unchanged**.
What is scrambled is the glue between them, and glue is what gets rewritten.

So: **derive the behaviour, then build the seven-loop top level fresh**, calling the existing subVIs. Nothing is
"moved"; the new top level is authored, and the old one is the specification.

**Two measurements make this affordable, and they are why this is a rewrite rather than a defeat:**

- **A subVI call costs ~100 ns** (`docs/subvi-call-cost-plan.md`). At a 6.00 ms budget, 100 calls cost 0.01 ms — so the
  new code may be divided as finely as clarity wants. NI's own help text claiming "tens of microseconds" is 600× off
  and unsourced; had it been believed, this design would have been built around a cost that does not exist.
- **Grouping is recoverable from the graph.** Clean Up moved positions but not wires, so functional grouping still
  exists in the topology — reachability from an anchor (e.g. the tracking kernel call), connected components, and which
  wires cross which structure. `net_map` already returns exactly this data.

**Interface width becomes the design rule.** The 66-terminal failure is the lesson: each new subVI must expose a
*narrow, meaningful* interface — a cluster of related values, a refnum, a queue — not every scalar its internals touch.
Where 66 wires cross, the right answer is a different decomposition, not a wider pane.

**And it satisfies a goal that was previously implicit.** Restoring readable structure is, in the user's words, one of
the main reasons this project exists. A seven-loop top level whose loops are named functional units *is* that
restoration; a faster but still unreadable diagram would only be half the job.

## 4b. The original extract-then-assemble method (superseded — kept for the reasoning)

Moving 75 nodes between diagrams by script is large and risky. The cheaper and safer route, which also happens to be
exactly what the two-codebase requirement needs:

1. **Extract** each functional region of the current main VI into a **subVI** — scheduler, motor, ASI/focus, display,
   file writer. A well-chosen boundary keeps the *wired* dataflow intact, which a node-by-node move does not.

> **Peer review refuted the stronger claim this plan originally made.** Extraction does **not** preserve all observable
> behaviour "by construction". LabVIEW's Create SubVI only creates terminals for the selected *wires*; everything that
> crosses a boundary by another route changes character or ordering:
>
> - a **local variable** belongs to a front-panel object in one VI — after extraction it is either a new subVI control
>   or a control reference passed in, and those are different mechanisms;
> - a **control reference** passed into the subVI still does reference-based UI work; extraction has not turned it into
>   dataflow;
> - **error-cluster ordering** exists only along the chain actually wired, so splitting one chain into loop-local
>   chains removes ordering that was previously guaranteed;
> - a **non-reentrant** extracted subVI serialises concurrent callers; making it reentrant instead duplicates its
>   internal state — both are behaviour changes;
> - **uninitialised shift registers, feedback nodes, `First Call?`, static VI references and event registrations**
>   carry state across a boundary and must be inventoried;
> - an extracted **Event Structure** is the worst case: **latch-action Boolean terminals must be read inside the event
>   case** or their mechanical action never resets.
>
> **Therefore each extraction is gated on a written BOUNDARY MANIFEST** listing every wire, local/global, property and
> invoke node, reference, error edge, stateful node and front-panel terminal that crosses the proposed seam. A
> bit-identical fixture result is necessary but **not sufficient** — the fixture replays recorded images and proves
> numerical regression only; it cannot exercise live buffer ownership, scheduling, or races.
2. The main diagram then collapses to a skeleton small enough to **assemble by script**: seven loops, each calling
   subVIs, plus the queues.
3. The extracted subVIs **are** the shared assets — the CPU and GPU builds call the same files, so a later fix is made
   once. Duplication exists only at the top level.

## 5. Stages, each with a numeric acceptance test

Structural checks (`ExecState == 1`, object counts) prove nothing about behaviour. Every stage below is accepted on
**numbers**, against the existing 10,043-frame fixture (`archive/bench-2026-09-07-fixture/`).

> ### ⚠️ CORRECTED 2026-09-16 — three acceptance criteria below were stated wrongly
>
> 1. **"Bit-identical on the fixture" means the first 10,018 frames**, not all 10,043. Both replay builds
>    (`Track_v6_CPU_core_v0`, `Track_v6_CPU_queue_v0`) match the reference exactly up to the **first bead loss**;
>    the remaining 25 frames depend on reseed behaviour that is not yet built. Say the number, not "the fixture".
> 2. **`Images Missed = 0` is NOT a sufficient live criterion** under the decided `Buffer Number Mode = Last`:
>    `Last` re-returns the same buffer when the PC is faster than the camera, and `Images Missed` does not count
>    that duplicate. The authoritative record is the **`Buffer Number Out` trace**, from which both gaps and
>    duplicates are derived (`pre-rig-master-plan.md` Phase 0.3; `camera-acquisition-facts.md:79-81`).
> 3. **150 Hz / 6.00 ms is the stretch condition, not what the coming runs test.** The decided operating point is
>    **90 Hz, exposure ≈ 5 556 µs, `ExposureAuto` OFF, and a 10 ms budget** (the period minus ~1 ms of measured
>    jitter margin). Dry-run acceptance is judged against 10 ms.

> **Stages 1 and 2 were rewritten on 2026-09-13** when extraction was ruled out (§4). Stage 1 is no longer "extract the
> shared subVIs" — it is "derive the behaviour of each functional unit from the existing diagram", which produces a
> specification rather than a VI. The acceptance test changes accordingly: a derivation cannot be diffed on the
> fixture, so it is accepted by **review against the source diagram**, and the first numeric checkpoint moves to
> stage 2.

| stage | work | acceptance |
|---|---|---|
| **0** | re-capture the baseline: current VI's x/y/z on the fixture | the reference every later stage is diffed against |
| **1** | **derive**, per functional unit, what it consumes/produces and which existing subVIs it calls — from the graph, not from positions | reviewed against the source diagram; every existing subVI accounted for, every inter-unit value named |
| **2** | acquisition + tracking loops + queue | fixture output bit-identical **for the first 10,018 frames** (those before the first bead loss); **plus** a live run at **90 Hz** whose `Buffer Number Out` trace shows no unexplained gap and no duplicate |
| **3** | scheduler and motor loops split out | an existing 3-row schedule produces **identical translation commands and timings** |
| **4** | rotor row added (4th row, absolute degrees, `MovePos`) | a 3-row schedule still behaves identically (backward compatibility); a 4-row schedule moves translation → then rotor |
| **5** | display + file-writer loops | live view reconnected at **90 Hz** with the `Buffer Number Out` trace unchanged from stage 2 (150 Hz stays the stretch condition) |
| **6** | GPU build: swap loop 2's kernel | x/y ≤ 1e-6 px and z ≤ 1e-4 µm against the CPU build, 0 flips |

**On stage 6's tolerances.** Peer review flagged these as contradicting "the numbers must not change". They do not: the
GPU tolerance was **approved by the user in advance** as the acceptance criterion for the GPU backend (x/y 1e-6 px;
for z the user accepted ~1e-4 µm — *"결과에 크게 지장 없다"*). Stages 0–5 remain **bit-identical**; only the GPU build,
which the user knowingly accepted as a numerically-equivalent-not-identical path, uses a tolerance.

**Acceptance must measure more than a rate.** An average Hz hides the cliff, and the acquired-rate counter alone does
not prove non-interference. Each live stage records: processed-frame deadline misses, **gaps in buffer numbers**,
the acquisition-call latency **distribution including p99.9 and max**, per-core CPU, UI-thread time, and display age.
Add a **back-pressure test** — deliberately slow tracking and disk writing for minutes, not an 8 ms injection — and a
soak run long enough to expose thermal throttling and disk stalls.

## 6. Gates — things that must be settled before or during, not assumed

**G1 — CLOSED 2026-09-13, by decision rather than by measurement (user's call).** The cost of a `Value` property node
in this loop was never measured, and it no longer gates anything: **converting a `Value` property node to a local
variable cannot lose**, whatever the number turns out to be. A local variable does not enter the UI thread; a property
node always does. Knowing the magnitude would only have set the *priority*, not the direction.

So the conversion is adopted as an unconditional **design rule for stage 1**: inside the frame path, front-panel access
uses local variables, never `Value` property nodes. The measurement is not abandoned, it is **moved to where it is
cheap** — once stage 1's subVIs exist, timing them is incidental rather than a build of its own.

*Why it was not measured now.* The attempt is recorded because the obstacle will recur:
`build_property(target, 'VI Server:Control', [('633200D', False)], pos)` creates a Property node but **the property
does not attach** — no `Value` terminal, wrong position, and the object count jumps from 8 to 224. The call's shape
matches calls that do work (`('23E', False)` with `VI Server:VI`), so the format is not the problem; the ID does not
resolve for that class. Identical symptom to `VI.Get Errors` 0x452, which is already on the backlog for the same
reason. **Being listed in `docs/vi-server-ids.json` is not evidence that an ID works** — most were transcribed from
labviewwiki in one pass and only a few have ever been exercised. The scratch VI was deleted and the donor verified
untouched (ExecState 1, counts unchanged).

**Measured 2026-09-14 (INDEX rows 27, 29):** the 88 implicit `Value` nodes bind to 45 panel objects (table at the end of
docs/main-vi-panel-map.md — the list the "→ locals by rule" conversion works from), and the frame loop's 14 shift
registers are fully named with their initialisers, readers and writers (docs/frame-loop-wire-graph.md, measured
sections) — the state that stage 1's rebuild must carry across the loop border.
If a `Value` property node is ever needed by script, the route is **copy it from a donor** — the main VI alone holds
106 Property nodes — not another attempt at the ID.

**G2 — can a subVI be extracted by script? ANSWERED 2026-09-12: yes, but it is the wrong primary tool.**

*The API exists and is reachable here.* `AbstractDiagram.SubVI From Selection`, method ID **6375405** (`0x6147ED`),
owning class **16503**, scope **PRIVATE**; inputs `Clean Up Wires`, `SubVI`, `Add To Project`,
`Apply 'Create SubVI' Plugin`; returns a reference to the new VI. It needs three private-scripting ini tokens —
`SuperPrivateScriptingFeatureVisible`, `SuperPrivateSpecialStuff`, `SuperSecretPrivateSpecialStuff` — and **all three
are already set in this install** (added during the CLFN work on 2026-09-09; backup at
`archive/LabVIEW.ini.bak-2026-09-09-1300`). Source: `archive/peer/2026-09-12-scripted-subvi-extraction.md`.

*Two things it is NOT.* erdosmiller's `Create SubVI.vi` is **not** an extractor — its pane is
`VI Reference`/`Inputs`/`Input Names`/`Output Names` and it calls only `Get Outputs.vi` and `Wire Inputs.vi`, with no
trace of `SubVI From Selection`, `AbstractDiagram` or `6147ED` in the file. It *places a call to an existing VI*, which
`gscript.drop_subvi` already does. And the `resource\plugins\CreateSubVI` hook is post-processing for a VI that has
already been created, not the extraction primitive.

*Why it is demoted from the primary strategy.* Native extraction converts a **local variable that falls inside the
selection into a control reference plus a `Value` property node in the child.* That is precisely the cost this whole
restructuring exists to remove: a `Value` property node always runs in the UI thread, and the frame loop's only
unconditional non-kernel cost today is two of them. **Extraction would manufacture the very thing we are eliminating.**
Two further hazards: a **latch-action Boolean** read through a `Value` property node never resets mechanically, so
Event-Structure regions must not be auto-extracted; and NI's **CAR 571520** records Create SubVI breaking unrelated
wires when a polymorphic VI selector is inside the selection.

**Decision, revised 2026-09-13 after the capability inventory.** The first version of this decision said extraction
would be secondary and the rest built "from public scripting primitives". **That fallback does not exist.** Checking
stage 1's requirements against `docs/toolkit-capabilities.md`: creating a VI, building a connector pane, creating
controls on node terminals, placing a subVI call, wiring and deleting are all available — but **nothing in the fleet
moves a multi-node region into another VI**. `copy_into` moves ONE object, and it must carry a label; the main VI's
nodes mostly have none. Relocating a 20-node region one node at a time, re-creating every wire by hand, would take on
manually every boundary hazard the peer review listed. So the "public primitives" route was an assumption, not a plan.

**Native extraction is therefore the primary route after all** — but the objection to it is narrower than it first
looked, and that is what makes this workable. Re-reading the peer's own wording: a local variable **inside** the
selection becomes a control reference plus a `Value` property node, whereas a local that stays **outside**, with only
its wire crossing, arrives as an ordinary connector terminal carrying plain data. The hazard is therefore a property of
**where the seam is drawn**, not of extraction itself.

So the method is: **choose seams that leave locals, Event Structures and polymorphic selectors outside the selection**,
and prove it per seam with the boundary manifest before cutting. The manifest stops being paperwork and becomes the
thing that decides where the cut goes.

First concrete step: pick ONE candidate seam, build its manifest, extract on a **copy**, and check the fixture output
bit-for-bit. One seam de-risks the whole plan far more cheaply than arguing about the method.

### The state-carrier map (measured 2026-09-13) — and it is good news

Every `Local`, `Global` and `SequenceLocal` in the main VI was located by the UID-lookup method, in 25 seconds.

| diagram | Local | Global | what it means for a seam here |
|---|---|---|---|
| **43 — the FRAME LOOP** | **0** | **0** | **no extraction hazard at all** in the region we touch most |
| **19 — parent of the parallel loops** | 0 | **3** (uids 7202, 6951, 6409, stacked 26 px apart) | this is where the loops exchange state; a design item of its own |
| 99 — display loop | 1 (uid 16942) | 0 | draw the seam outside it |
| 83 | 3 | 2 | the densest state region; avoid cutting through it |
| 1, 17, 73, 167 | 1 each | — | scattered, each trivially avoidable |

Totals: **8 locals, 7 globals, 0 feedback nodes** in a 170-diagram VI. That is small enough to route seams around
individually, which is what turns the peer's objection from a blocker into a constraint.

**`FeedbackNode` count is 0**, removing one category of hidden state entirely.

**Not established:** the 7 `SequenceLocal` objects all reported `uid 0` and could not be placed. A sequence local
belongs to its structure and appears to carry no GObject UID. This is an unknown, not an absence — a seam crossing a
Flat Sequence must still be checked by reading that structure.

### The inter-loop state contract, read 2026-09-13

The globals are all fields of **one VI global, `Global motor pos.vi`** — the file `docs/motion-path-audit.md` already
flags as a pure VI Global with no block diagram, i.e. a race carrier with no hidden mutex, to which **no new writer may
be added**. Three distinct fields appear, at seven sites inside the main VI:

| field | diagram | direction | other end of the wire |
|---|---|---|---|
| `Trans position` | 5 (init, Sequence) | written | `element` / a `Value` |
| | 19 (parent) | read | motor node uid 25380 `tran pos` |
| | 83 | read | indicator `Trans Pos (mm)` |
| | 83 (uid 3166) | — | unwired |
| `Rot position` | 8 (init) | written | wire present, no second terminal on this diagram |
| | 19 (parent) | read | motor node uid 25380 `rot pos` |
| `Focus position` | 19 (parent) | **written** | frame-loop node uid 637 `position [internal units]` |

The shape is legible: **initialisation writes, the parent diagram hands the value to the loops, and diagram 83 reads it
for display.** `Focus position` runs the other way — the frame loop writes it, which is the autofocus result leaving
the loop.

**Scope check done — and it comes back clean.** A VI global is reachable from *any* VI, so "no other writer in the main
VI" would not have been evidence of anything. An offline byte scan of the entire `zz_LabView VI` tree (no LabVIEW
needed) found every file that references `Global motor pos.vi`: they are **all other generations of the main program** —
copies under `old\`, `DY\`, `Four-Fold Tracking in Room 5\`, `zz_NJH_test\`, plus the global VI itself. **Not one subVI
in our hierarchy touches it** — not `Motor control v5`, not `ASI_adjust focus-subvi`, not the tracking kernel, not the
PI driver VIs.

So each field currently has **exactly one writer, inside the main VI**. The race the motion audit warned about is a
*latent* hazard, not a present one.

**Design consequence.** Because each field already has a single writer, the globals may stay as they are — the
restructuring does not have to replace them, and replacing working state plumbing during a timing rewrite would add
risk for no measured gain. The constraint is simply that **the single-writer property must survive the split**:

| field | writer today | writer after the split | note |
|---|---|---|---|
| `Trans position` | initialisation | initialisation | readers: motor loop, display |
| `Rot position` | initialisation | initialisation | reader: motor loop |
| `Focus position` | **the frame loop** | **the ASI/focus loop (5)** | it must MOVE, not be written from both |

`Focus position` is the one that actually changes hands: the frame loop writes it today, and autofocus is moving to its
own loop, so the write moves with it. Two loops writing that field would create exactly the race the motion audit
warned about — and it would be a race we introduced.

Add to each stage's acceptance: **no field of `Global motor pos.vi` gains a second writing loop.** That is checkable by
the same Traverse used here, so it costs nothing to verify.

**G3 — the schedule consumer has not been located.** The place that splits a schedule entry into speed/force/wait is
the only work site for the rotor row. Stages 3 and 4 depend on it.

**PARTIALLY CLOSED 2026-09-13.** The one fact stages 3 and 4 actually need is settled; the exact node is deferred to
stage 4, when the frame loop will be far smaller and the search far cheaper.

**Settled: the cycle-execution logic lives inside the frame loop.** Diagram bounding boxes computed from all 626 node
positions place the `SubCycle` terminal (3160, 987) and the `Start Cycles` terminal (6054, 1258) inside
**diagram 43, x[2730..6298] y[942..2704]** — the frame loop — and inside its parent 19, which contains it. So moving
the scheduler into its own loop (loop 3) is a genuine *move*, measured rather than assumed.

**Located but not pinpointed: the table-editing region.** `CycleSchedule` (−10604, 1049), `NumCol` (−6265, 963) and
`Mag Position` (−8545, 887) fall in **no** diagram's box. The band they sit in is a continuous strip of diagrams
145→167 running x ≈ −10600 to −4600, just outside the display loop (diagram 99, x[−14685..−11563]). Their containing
diagram is therefore one of the 46 that hold no placed node, or the top-level diagram 0 (1 uid, no box). Narrowing
further was stopped deliberately: it is needed only for stage 4's rotor row, and after stage 1 the search space will be
a fraction of its current size.

**Four search methods were tried; the three failures are recorded in `docs/toolkit-capabilities.md` because each one
mapped a real limit of the tooling** — Index Array density (found the bead table instead), front-panel UID lookup in
the diagram tree (different object kinds), terminal-name matching via net_map (ControlTerminals are not Nodes), and
finally bounding boxes from `report("Node")`, which worked for the two terminals that matter.

*Search attempt 1 (2026-09-12) failed, and the negative result is useful.* Diagrams 160–165 were ranked as candidates
by Index Array density (8, 6, 4, 2 nodes) — but reading them shows **bead selection and cross-hair drawing**, not the
scheduler: the nodes carry `starting x 1/y 1`, `starting x 2/y 2`, `cross size`, `picture in`, `Picture out`,
`cosine window for hilbert`, and diagrams 161/162 each hold the same cross-drawing subVI (uids 24170, 24656). Index
Array density picked the largest 2-D array user in the VI, which is the bead coordinate table, not the schedule.

Two things follow. First, that cluster is a clean **extraction boundary for the display loop (6)** — the cross-drawing
subVI is already a subVI, so the region has an obvious seam. Second, the next search must use a different key:
`CycleSchedule` reads back as `((0.0,), (0.0,), (0.0,))`, i.e. **one column**, so it is likely indexed in 1-D, and the
scheduler is better found through the indicators it drives — `SubCycle`, `Total cycle #`, `Cycle Start Time`,
`Estimated end time (min)`, `Mag Arr`, `Force Arr`.

**G4 — image handoff between loops.** IMAQ images are references, not values: enqueueing one lets the camera overwrite
it before the consumer reads it (this exact class of bug cost the GPU v2 work a day — 32 ms/frame with stale-frame
errors). The plan assumes a **pre-allocated image pool + slot index + return path**, which bounds memory and costs the
one copy, measured at **≈ 0.05 ms** in steady state. Confirm the GPU path can still take a raw pixel pointer from a pool image.
**Measured 2026-09-14** (`archive/bench-2026-09-14-image-copy`): a reference-safe `IMAQ Copy` of a 1280×1024 U8 frame
costs **≤ 0.4 ms** cold (the destination's first allocation) and **≈ 0.05 ms in steady state** (1024 copies inside
one Run, INDEX row 26 — so a pre-allocated pool makes per-frame copying ≈ 8 ms/s at 150 Hz), `IMAQ ImageToArray` 0.55–0.6 ms — so
copy-on-demand at selection time (display: newest frame at 10–20 Hz; writer: every saved frame) is affordable, and a
bare ring reference must never reach a consumer that can stall (NI: copy, then release the ring reference).

**Which number is the copy, reconciled 2026-09-16** (`archive/ingest/2026-09-16-ingest-2026-09-16.md` PAIR 6,
lines 113–115, against `frame-ownership-design.md:34-35`). All three are measured; they measure different things:
**≈ 0.05 ms · 2026-09-14 · steady-state `IMAQ Copy` — REPRESENTATIVE** (`archive/benchmarks/INDEX.md:47` row 26);
**≤ 0.4 ms · 2026-09-14 · the cold first copy**, destination allocation included, an upper bound (`INDEX.md:44`
row 23); **0.12 ms · 2026-09-12 · acquisition itself**, median 122.6 µs/frame (`INDEX.md:40` row 19) — which is
what line 28's "acquisition cost" row above means, and is **not** the pool copy. `frame-ownership-design.md` had
quoted the 0.12 ms figure under the copy's name and has been corrected.

**G5 — abort safety.** Queues, image pools and VISA references survive a LabVIEW Abort. The GPU DLL already solves this
by having the next start clean up whatever the previous run left; the same discipline is needed here.

**G6 — overload contract.** 150 Hz × 1.31 MB = 196 MB/s. An unbounded queue grows silently until it fails.

Peer review pointed out that the first draft asked for four things that **cannot all hold at once** — bounded memory,
a lossless tracking path, a non-blocking acquisition loop, and tolerance of a consumer that is slower than the camera.
Under sustained overload only three outcomes exist: block the producer (which recreates the cliff), drop the new frame,
or recycle an old slot (risking use-after-recycle). The contract is therefore stated explicitly rather than wished away:

- **Design point:** the consumer is *faster* than the camera — 2.6 ms of work against a 6.00 ms budget — so the queue
  exists to absorb **jitter**, not a deficit. Under the designed load the path is lossless and nothing is dropped.
> **SUPERSEDED TWICE — do not build the safety valve below (lint, 2026-09-16).** The overload policy is
> **latest-wins** (user, 2026-09-15), not drop-new; and the pool/eviction machinery was then cancelled outright
> because the camera free-runs — the readout is `IMAQdx Get Image` with **`Buffer Number Mode = Last`**, and a
> full pool just means *skip this read*. Gap accounting is the jump in `Buffer Number Out`, reported by the camera
> side. See STATUS.md, "OVERLOAD POLICY" and "the camera free-runs". Superseded text kept below.

- **Safety valve:** if the queue is nevertheless full, the acquisition loop **drops the new frame and counts it**
  (finite enqueue timeout, never `-1`), feeding the existing `Total Lost Frames` / `Missing Frames?` indicators. It
  never blocks.
- **A drop is a failure report, not a normal mode.** Acceptance is therefore "zero drops under the designed load", and
  any drop at all is a defect to investigate — which resolves the contradiction between G6 and stage 2's criterion.

**G7 — the tracking-path ownership state machine (new, from peer review).** A pool + index is a sound ownership
pattern, but the index is not what makes it safe; the lifecycle is. Required invariants: acquisition obtains a **free**
slot first; exactly one owner touches a slot at a time; **every** exit path — kernel error, enqueue timeout, shutdown,
file-writer error — returns or retires the slot **exactly once**; images are disposed only after every possible user
has stopped; and a GPU raw pixel pointer must not outlive slot ownership or survive a reallocation.

**G8 — coordinated fault and shutdown (new).** Ordinary stop: send a typed stop message, drain or deliberately discard,
return slots, *then* release refnums (releasing while a node waits raises error 1122). Consumer failure needs a reverse
fault path that stops acquisition, or the producer fills the pool forever. A hard **Abort** bypasses diagram cleanup
entirely, so "the next start cleans up" must be specified concretely for VISA sessions, open files, camera acquisition,
partial records, and an outstanding GPU DLL call — not left as a slogan.

**G9 — core budget, not loop count (new).** Seven loops is not self-evidently right; the tracking kernel is itself a
parallel For Loop with several instances, and oversubscription shows up as context switching, cache eviction and
acquisition jitter rather than as a clean error. Benchmark the architecture at the normal core count **and with one
fewer core**, and account for parallel-For workers plus IMAQdx and GPU driver threads. Also: a non-reentrant shared
subVI serialises nominally independent loops — decide reentrancy per extracted subVI deliberately.

## 7. What is explicitly out of scope

- Changing the per-bead maths, the parameters that reach it, or the numbers that come out. Only scheduling changes.
- Parallel tracking instances. They would break frame ordering, which is a computation change.
- Ring-depth tuning (measured: not a lever).
- An external display program. Only justified if stage 5 shows the cost is CPU/GDI-bound, and that is not yet known.

## 7b. What the peer review changed (2026-09-12)

Full exchange: `archive/peer/2026-09-12-restructure-plan-4.6-attack.md`. It was asked to attack, and it landed.

**Adopted — these were real defects in the first draft:**

1. **Separate local variables for the scheduler's command are not atomic.** The motor loop could read a new speed with
   an old force. Fixed: one versioned command cluster through a single-owner queue. This was a bug that would have
   shipped.
2. **"Extraction preserves dataflow by construction" was overclaimed.** Replaced with a required boundary manifest and
   the specific hazards (locals, control references, error ordering, reentrancy, latch-action Booleans, stateful nodes).
3. **A bounded queue does not imply dropping** — the default enqueue timeout is `-1`, i.e. wait forever. Every enqueue
   now specifies a finite timeout and handles `timed out`.
4. **Error 1122** on releasing a queue with a waiter: shutdown order is stop → drain → release.
5. **The overload contract was self-contradictory** (G6 dropped frames while stage 2 demanded none). Now stated as a
   design point plus a safety valve, with a drop treated as a defect.
6. **"`Last` cannot block acquisition" was too strong.** One workload's acquired counter is not proof of
   non-interference; CPU/memory-bandwidth, UI-thread, and driver-lock paths remain. Claim weakened, acceptance widened.
7. **Loop count is the wrong metric.** Added the core-budget gate G9, including a run with one fewer core.
8. **The fixture proves numerical regression only** — not ownership, scheduling or races. Stated in §4.

**Not adopted, with reasons:**

- *"Stage 6's GPU tolerance contradicts the no-change rule."* It does not: the user approved that tolerance in advance
  as the GPU acceptance criterion. Stages 0–5 stay bit-identical.
- *"The rotor change should be a separate change set."* It already is — stage 4, after the restructuring stages, with
  its own backward-compatibility test. The user chose this order deliberately.

**Deferred but recorded:** end-to-end timestamping from exposure to file commit; per-record provenance (calibration ID,
kernel version, schedule version, gap records); version-pinning the shared subVIs so a later edit cannot silently
change both builds; file-writer capacity and disk-full policy; startup recovery from a previous abort.

## 8. Open question for the user

**Where is rotor zero?** The sign carries direction, so a schedule value of −7200 means "20 turns negative from zero".
Zero at experiment start makes a schedule reproducible across runs; zero after manual alignment on a bead matches the
actual experimental workflow but needs a "set zero here" control. This is an experimental-procedure decision.
