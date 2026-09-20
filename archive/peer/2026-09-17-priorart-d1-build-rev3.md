# priorart-d1-build-rev3

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.5639  in 36 / out 36615 / cache-create 210961 / cache-read 3077509  (498s, 28 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (502s)
- **why asked:** cycle 15 step 1 — the mandatory prior-art review of `docs/d1-build-plan.md` REV 3 before the D1
  build recipe is written (trigger `new-op`; STATUS OPEN 19 said it was not yet dispatched).
- **verdict:** 8 findings, 0 novel — **2 FIXED** (A1, A2, folded into the plan's new §0-MEASURED), **6 ACCEPTED
  and escalated to judgement** (A3, A4, A5, B1, B2, B3); none refuted. **The build was stopped by it.**

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
date: 2026-09-17
cycle: 15
kind: build
tags: [d1, delivery, seven-loop, acquisition, tracking, writer, stop, autofocus]
parent: docs/cycle15-plan.md
spec_rows: [pre-rig-master-plan.md 1.1, 1.2, 1.5, 1.7, 1.8, 1.9]
reviewed_by: archive/peer/2026-09-17-priorart-priorart-d1-build.md
supersedes: []
measured_in: [tools/bench/build_oploopendref_v0.log, tools/bench/loopendref_637.json, tools/bench/diag_stop_save_seam.log, tools/bench/probe_move_into_v0.log, tools/bench/diag_movein_p1_break.log, tools/bench/gpu_kernel_v1_fp.json, tools/bench/gpu_n1_deltas.json]
---

# D1 build plan ??the first slice of the seven-loop VI, inside a COPY of the original

**REV 3, 2026-09-17.** Rev 2 left three decisions open and one route unmeasured. The judgement session has now
taken all five D1 spec decisions (`docs/cycle15-plan.md:42-57`), the stop is **measured** rather than inferred,
and phase P has run. Every section below says which of those it consumes. **This document is not a build order
yet** ??it is what the judgement session reads before authorising one; its prior-art review is deliberately NOT
dispatched from here.

Target `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Track_v6_D1_GPU.vi` = a fresh copy of
`Min_Track N beads V6_ParallelLoop.vi` (md5 `2a78e17c449cacdaf5da389818526859`, asserted before **and** after every
run; the original is never opened for writing ??rule 1).

## 0. The five D1 spec decisions this rev is built on

Taken by the judgement session on 2026-09-17 after `archive/peer/2026-09-17-priorart-priorart-d1-build.md`
(10 findings, 0 novel). Quoted here so no section re-argues them:

| # | decision | consumed in |
|---|---|---|
| 1 | **`#10407` (autofocus, VISA) gets its own loop in D1** ??a minimal row 1.5: the case and its VISA session alone in a loop, woken every 25 frames by a **latest-result (lossy, non-blocking) notifier** from the tracking loop; its other inputs by the same route and values as today | 짠5 |
| 2 | **Writer = stream AND accumulate** ??the 1.7 loop writes each result as it arrives *and* accumulates the arrays; at stop it calls the original `save N xyz traces.vi` #6384 with them, so the `.tra` format stays byte-compatible | 짠6 |
| 3 | **Stop = two nodes and a fourth structure** ??`stop (end)` #7 ??`CompoundArithmetic` #11639, and `stop (end) 2` #19587 ??`#17883` ??`Tunnel #22085` of `CaseStructure #22082`; the plan places #22082 explicitly | 짠3 |
| 4 | **Structures in the kernel's forward slice** (`#5540 #2222 #12589 #1359 #29874 #10407`) move by the documented **Make Selection ??Copy Selection ??Paste onto the subdiagram** route, which has never been run ??so it is **probed first**, never inside the D1 build | 짠2 |
| 5 | **Precondition readers/devices** ??`OpLoopEndRef_v0` (how #637 actually stops, D1's S4 gate) and bgrun's `-> FAIL` scan | 짠3, 짠8 |

?좑툘 **Decision 4 is OVERTAKEN BY ITS OWN PROBE, in the cheap direction.** It named `Make Selection ??Copy Selection
??Paste` as the route for structures and required a probe first. The probe ran (짠2b, 12/0) and the *cheaper*
route ??`GObject.Move` with a wired `owner`, via the new `OpMoveIn_v0.vi` ??**relocates `CaseStructure #12589`
with its frame diagrams intact**. So the selection/paste op family is **not built**, and D1's structures move with
`OpMoveIn_v0`. Everything else in decision 4 stands, including "never probed inside the D1 build".

## 1. What is already built or measured, and is therefore NOT re-derived here

| need | what exists | where |
|---|---|---|
| the seam's 16 terminals, every wire, every other end | measured | `docs/main-vi-stop-and-save.md` 짠4 |
| **the frame loop's conditional terminal and what drives it** | **MEASURED 2026-09-17** (not inferred) | same file 짠1; `tools/bench/loopendref_637.json` |
| `save N xyz traces.vi` #6384 on diagram 19 after the loop, 7 of 8 inputs off #637's tunnels | measured | same file 짠2 |
| shutdown frame (diagram 83): IMAQdx Stop/Close, `ASI TG-1000 Close.vi` #29815 (all terminals bare), IMAQ Dispose | measured | same file 짠3 |
| kernel forward slice = 14 nodes, backward slice = 7 | measured | `docs/frame-loop-wire-graph.md:43-45` |
| producer/consumer core, 6 lock-stepped queues + pool, 162/162 | built | `docs/stage2-assembly-step-c.md` |
| queue / loop / exit_while / shift-register / drop_subvi / delete ops | built, functionally verified | `docs/toolkit-capabilities.md:24-35, 41-44` |
| **relocating a plain primitive or a subVI call** ??create it fresh in the destination loop, wire across the border, delete the original | **SETTLED; `GObject.Move` declared unnecessary** | `docs/decisions.md:19`, `docs/restructure-plan-4.6.md:79-81`, `tools/recipes/probe_relocate_route.py:10-15` |
| GPU vs CPU on the fixture, kernel harness | **MEASURED twice, bit-identical**; k < 10018 ??max \|?x\| 4.857e-07 px, \|?y\| 4.677e-07 px, \|?z\| 1.279e-05 쨉m, **0 exceedances** | `docs/gpu-backend.md` 짠2026-09-17; `tools/bench/gpu_n1_deltas.json` |
| unattended drive of a copy through stages 0??, run, stop, restart | built, 16/16 | `tools/bench/drive_original_copy_v3.py` |
| camera contract writer | built | `tools/bench/camera_contract.py` |
| frame accounting subVI `get buff image-lost frames.vi` #6810 | the original's own | `docs/frame-loop-anatomy.md:47` |
| identify what a mutating op created ??by uid, never a cached Traverse index | recorded remedy | `tools/gscript.py:833-836`; `archive/peer/2026-09-15-opwiresource-fail5-traverse-index-order-mismatch.md:29` |

## 2. Phase P ??the relocation route, and what it actually measured

Rev 2 named this D1's one real unknown: relocating **a structure with its contents**. Phase P
(`tools/recipes/probe_move_into_v0.py`) measures the cheap route ??`GObject.Move` with a wired `owner` ??with a
plain primitive (`#8885 Multiply`) as the control arm and `CaseStructure #12589` as the question.

### 2a. What phase P cost, and the two defects it found in itself

Three runs, all stopped in **phase 1** (building the op `OpMoveIn_v0` from `OpMoveOut_v0`), each for a cause that
was then **measured rather than argued**:

| run | stopped at | cause, as measured |
|---|---|---|
| 1 (04:2x) | P1 | `net_map` returned 4 of `UID to GObject Reference.vi`'s 12 terminals, and the VI-reference input is named `Owning VI` (`tools/bench/diag_u2g_terminals.log`, 5/5). Harness. |
| 2 (04:55) | P1, `ExecState 0` | **wire 464 is ONE net**: source `IndexArray #236`, sinks `Property #237`, `Property #240`, `Invoke #741`. Deleting the Wire object to bare `Move.reference` also bares the **required** `reference` of #237 and #240 ??no broken wire, nothing for Remove Bad Wires, ExecState pinned at 0 (`tools/bench/diag_movein_p1_break.log`, 5/5; peer `archive/peer/2026-09-17-moveinto-p1-execstate0.md`, whose THIRD explanation was the right one). |
| 3 (05:15, rev 7) | P1b | The "fresh donor copy" was **the previous run's artefact**: the same LabVIEW process still held `OpMoveIn_v0.vi` in memory with run 2's unsaved edits, so `GetVIReference(path)` served the cached object and the disk overwrite was invisible. Remedy: a **uniquely named working copy per run** plus gate **P1z**, which proves the copy is the donor (ExecState 1, 15 nodes, no `UID to GObject Reference.vi`) before anything is edited. |

**The repair that is in the file now** (judgement decision A, 2026-09-17): the net is deleted and
`#237.reference` / `#240.reference` are **immediately re-wired from `IndexArray #236`**, gated by **P1b**. The
decision's literal wording was *"do not delete wire 464"*, and that is not simultaneously realisable with feeding
`Move.reference` from the UID-addressed GObject: a sink takes exactly one source and **there is no
`Terminal.Disconnect` in `docs/vi-server-ids.json`** (it carries `Terminal.Connect Wire` 6349C03 and only
`ConnectorPane.Disconnect Terminal` 239A8002 / `Disconnect All Terminals` 239A8003, which act on the connector
pane, not on a diagram wire). The end state for #237/#240 is identical either way. **Flagged for the judgement
session.**

### 2b. ??RESULT ??MEASURED 2026-09-17 05:22, **12 pass / 0 fail, 14 s** (`tools/bench/probe_move_into_v0.log`)

**`GObject.Move` with a wired `owner` reparents a STRUCTURE WITH ITS CONTENTS inside one VI.** D1's only real
unknown is closed, and it is closed by the *cheap* route ??the new op family of 짠2c is **not needed**.

| gate | result |
|---|---|
| **P0a / P0b** | original md5 `2a78e17c449cacdaf5da389818526859` before **and** after |
| **P1z** | working copy is the donor: ExecState 1, Node 15, subVIs = Clear Errors / Create Invoke Node / Traverse for GObjects, **no U2G** |
| **P1b** | `#237.reference` and `#240.reference` both on **wire 456**, one shared net, sourced at `IndexArray #236` |
| **P1a** | `Move.owner` carried by wire 645 whose source is the Diagram cast **#683** (not `VI.Block Diagram`) |
| **P1** | `OpMoveIn_v0.vi` **ExecState 1** ??the op is built and saved (UID control label `'UID 3'`) |
| **P2a** | a While loop created on `Diagram #686` (Traverse index **19**, the holder of `#637`): **+1 diagram, +1 while loop** ??`WhileLoop #1133`, body `Diagram #1170` at index 20 |
| **P2 (control)** | `#8885 Multiply` ??owner `Diagram #1170` ??owner `WhileLoop #1133` |
| **P2b** | `Diagram[20]` (uid 1170) holds `[8885, 1134]` ??the destination index still names the right diagram |
| **P3 (the question)** | **`CaseStructure #12589` ??owner `Diagram #1170`, and the VI's total `Diagram` count is UNCHANGED, 171 ??171** ??no frame diagram destroyed or orphaned, i.e. the case's contents came with it |
| **P4a / P4** | 2 junk Invokes (`1145`, `1134`) purged; `Node` 626 ??**627** (= +1, the new While loop); `ExecState 0` afterwards, **expected** (wires were cut) |
| **census** | `Wire` 1902 ??**1895** (??), `LoopTunnel` 132 ??**130** (??); the new body `Diagram #1170` holds `[8885, 12589]` |
| **P5** | scratch copy deleted in the same run; the per-run working copy retired to `OpMoveIn_v0.vi` and deleted |

**Read the census honestly.** The move **cuts** the wires that crossed the old border (?? wires, ?? loop tunnels)
rather than re-routing them through new tunnels. So a relocation is *not* a complete operation: **D1 must re-wire
every cut connection afterwards**, and 짠8's per-terminal table is the list of what to re-wire. `ExecState 0` after
the moves is the expected state, not a defect ??but it means **a D1 build cannot use `ExecState` as a progress
signal between moves**, only at the end.

Two facts recorded that are not gates:

* the scratch copy of the original reads **`ExecState 0`** when opened headlessly (before any edit). Nothing here
  depends on it, but an S-phase gate must not assume a fresh copy starts at 1.
* **handle count 30,849 ??51,530 in 14 s** (baseline ??31,500). That is a ~20,700 jump for two `move_in` runs plus
  the reads ??well past anything measured before. Per CLAUDE.md's reference-hygiene rule this is a **measured
  growth to attribute, not an absolute number to panic about**; `bench_prep`'s `HANDLE_LIMIT` restart applies
  before the next batch. ?윞 Attribution is a one-run `handle_audit.py` job, not a build item.

### 2c. If the `GObject.Move` route does not answer it

The documented alternative is `TopLevelDiagram.Make Selection` **0x6349002** ??`Copy Selection` **0x6349003** ??
destination `AbstractDiagram.Paste` **0x6375400**, verified with `Selection List[]` **0x6349400**
(`.claude/skills/labview-automation/references/vi-scripting.md:323-325`;
`archive/peer/2026-09-13-scripted-diagram-selection.md:143,:162,:166-172`, whose forum citation says explicitly
*"including contents of a structure frame"*; `archive/peer/2026-08-28-copy-nodes-between-vis.md:86` adds the trap
that pasting to the top level when a frame was meant produces a floating object).

**It is not a drop-in, and this is measured, not estimated.** `Make Selection` takes `Objects[]` ??an **array of
GObject references** ??and the fleet has no way to build one inside an op VI: `grep "^def " tools/gscript.py` has
`build_invoke` / `build_property` / `build_index_array` but **no Build Array creator**, `create_control` would make
an array-of-refnum control whose value cannot be set from an out-of-process COM client, and a scalar
`GObject` wired into an array terminal is a type mismatch. So this route is **three new Invoke ops plus a missing
primitive constructor** ??exactly what `docs/cycle15-plan.md:54-55` and rev 2 짠1 call *"a new op family and its own
cycle"*. **Choosing it is a judgement call, not a fallback this plan takes on its own.**

## 3. The stop, now measured ??row 1.9

??**`WhileLoop #637`'s conditional terminal is uid 648**, a SINK, carrying **wire 3457**, whose single source is
`CompoundArithmetic` **#11639** ??all inside `Diagram #639`. Read by `OpLoopEndRef_v0.vi`
(`WhileLoop.Loop End Ref` **6362C00**, data-terminal short name **`LpEndRef`**, id verified on this machine),
16 pass / 0 fail (`tools/bench/build_oploopendref_v0.log`, raw `tools/bench/loopendref_637.json`). The same run
read #25380 ??25410 / wire 1737 and #15173 ??15276 / wire 19456.

So the stop is **two paths, not one** (spec decision 3):

| path | wiring (measured) | where it goes in D1 |
|---|---|---|
| **A** | panel `stop (end)` **#7** ??terminal wire 6929 ??`CompoundArithmetic` **#11639** t2 (OR-ed with wire 12070 ??#12589 t2 and wire 10249 ??`x = y?` #10019) ??**wire 3457** ??**#637's conditional terminal uid 648**, and also ??panel indicator `TurnOff` #24423 | stays the ACQUISITION loop's stop; each new loop reads the same Boolean **inside itself** via `exit_while` |
| **B** | panel `stop (end) 2` **#19587** ??terminal wire 15230 ??`CompoundArithmetic` **#17883** t1 (with wire 18092 ??`.not. x?` #17837 and wire 18056 ??`x = y?` #22284) ??**wire 15229** ??`Tunnel` **#22085** of **`CaseStructure #22082`** | **#22082 is a fourth structure and D1 places it explicitly**: it stays on the acquisition loop with path B intact, because nothing in the kernel's forward slice feeds it |

**Rule (NI's infinite-loop mistake, `stage2-plan.md:90-94`):** a front-panel Boolean wired in from the top level
becomes an input tunnel read **once**. Every new loop therefore reads its stop from a terminal **inside** its own
body, built by `exit_while` / `OpExitWhile_v0` (verified 5/5, ExecState 0 ??1, `toolkit-capabilities.md:31`).
Shutdown order is **stop the users ??drain ??release**, so no error 1122
(`frame-ownership-design.md:68-72`).

## 4. Loop assignment

| loop | keeps / receives |
|---|---|
| **1.1 ACQUISITION** = the existing `WhileLoop #637` | `#6810 get buff image-lost frames.vi` (row 1.8 ??REUSED, 짠7), `#22700 IMAQ Write TIFF File 2` **unconditional, exactly as the original has it**, the camera reads, both stop terminals, `CaseStructure #22082` |
| **1.2 TRACKING** = a NEW While loop on **Diagram 19** | `GPU_kernel_v1.vi`, the reseed case `#5540`, the two per-frame state carriers (`LeftShiftRegister #2972`, `RightShiftRegister #5796`), and the forward-slice nodes that are neither autofocus nor writer |
| **1.5 FOCUS** = a NEW While loop on Diagram 19 | `CaseStructure #10407` with `#48 ASI_adjust focus-subvi.vi` and its VISA session, woken by a latest-result notifier ??짠5 |
| **1.7 WRITER** = a NEW While loop on Diagram 19 | streaming per-frame write **and** array accumulation; at stop, the original `#6384 save N xyz traces.vi` ??짠6 |
| **1.9 STOP** | paths A and B of 짠3; each of the three new loops stops from a Boolean read inside it |

## 5. Row 1.5 ??the autofocus loop (spec decision 1)

Rev 2 left this open (`#10407` is in the kernel's forward slice and **neither** placement was legal: on the
tracking loop a VISA stall fills `Q_work` and acquisition then skips reads ??rule 1c / `decisions.md:30`; on the
acquisition loop its input no longer exists). The decision is a **third** placement:

* **`CaseStructure #10407` and `#48 ASI_adjust focus-subvi.vi` move to their own While loop**, which is the only
  owner of the ASI VISA session. Nothing on the frame path can block on it ??rule 1c is satisfied **by
  construction**, not by being fast enough.
* **Wake-up = a latest-result notifier**, written by the tracking loop and read with a **finite timeout** in the
  focus loop. A Notifier is lossy-by-nature (a new value overwrites an unread one), which is exactly the
  "prefer the freshest" semantics the user set for overload; `Send Notification` never blocks, so the tracking loop
  cannot be held up by a focus loop that is mid-VISA.
* **Cadence unchanged:** the original fires on a frame-index schedule, measured at every **25 frames ??3.6 Hz**
  (STATUS OPEN 2). D1 keeps that schedule and evaluates it in the TRACKING loop (where the frame counter is), not
  in the focus loop.
* **Rule 1a:** the case's own inputs ??`Index of closest cal image slice, bead 2` and the panel values it reads ??
  arrive by the same route and with the same values as today; only *when the case is evaluated* changes, and that
  is scheduling, which rule 1a permits.
* ?좑툘 **OPEN (judgement, small):** the notifier carries the one slice index the case consumes. If the case reads
  more than that one per-frame value, the notifier's payload becomes a cluster and the fleet has **no
  Bundle/Unbundle writer** (`toolkit-capabilities.md:32,:46-49`) ??in which case the payload must be a DBL array,
  or a second notifier. `tools/bench/case5540_frame_sources.json` has the analogous census for #5540; the
  equivalent for #10407 is **not measured** and is a one-run diagnostic, not a build item.

## 6. Row 1.7 ??the writer loop, streaming AND accumulating (spec decision 2)

The conflict rev 2 recorded (`pre-rig-master-plan.md:93` wants every result written in order; the user wants a
file that grows during the run; `#6384` wants seven whole arrays at the end) is resolved by doing **both**:

1. **Stream.** The writer dequeues `Q_res` / `Q_good` / `Q_rmeta` (lossless FIFO, `decisions.md:24`) and appends
   one line per result to an open file refnum. That is the user's requirement verbatim: *"???猷⑦봽???먮낯泥섎읆 ?앹뿉
   ??踰???ν븯吏 ?딄퀬 ?ㅽ뻾 以?怨꾩냽 ?뚯씪???대떎"* (`archive/prose/2026-09-17-d1-d2-explained-r2.md:114`).
2. **Accumulate.** The same loop builds the arrays in shift registers ??the same values, in the same order, that
   `#376 save trace.vi`'s accumulators hold in the original.
3. **At stop**, after the drain, it calls **`save N xyz traces.vi` #6384 unchanged** with those arrays, so the
   `.tra` file is byte-compatible with the original's output. #6384's eight inputs and their present sources are
   measured in `main-vi-stop-and-save.md` 짠2; seven come off `#637`'s output tunnels and the eighth is an
   `Array Subset` (#2048) of `total data array out`. In D1 those seven come from the writer loop's own shift
   registers instead ??**same values, different carrier**, which is scheduling.
4. **Consequence to state plainly:** D1 produces **two** artefacts per run ??the streamed file and the `.tra` ??and
   the N1 gate is checked against the `.tra`, because that is what the original writes.

## 7. Row 1.8 ??frame accounting

**REUSE `get buff image-lost frames.vi` #6810**, decided in writing. It is the frame source itself, already
produces `Missed frames?` and `current image number`, and that number is the buffer number carried in
`Q_meta`/`Q_rmeta`. Replacing it would change computation on the acquisition path for no gain.
**Reconciliation gate (new ??no equivalent exists in `tools/bench/` or `archive/benchmarks/INDEX.md`):** the
writer's buffer-number series is a strictly increasing subsequence of the acquisition loop's, and
`Total Lost Frames` equals the count of skipped buffer numbers.

## 8. The seam, node by node

`subvis(MAIN, 43)` returns six calls; **`#5058 Track N beads four-fold over-kernel-v3.vi` is the seam**. Its 16
terminals with the object on the other end (`docs/main-vi-stop-and-save.md` 짠4, `census` + `measured`):

| t | terminal | dir | wire | other end | D1 route |
|---:|---|---|---:|---|---|
| 0 | `Bead is good? array in` | IN | 5637 | ??`CaseStructure #5540` t2 | #5540 moves to 1.2 with the kernel (structure ??짠2) |
| 1 | `Image In` | IN | 3040 | ??`#6810 Image Out`; also ??`#22700` t11 | **crosses the loop border**: the pool slot's image, out of `Q_work` |
| 2 | `cross size` | IN | 373 | ??`LoopTunnel #2580` | loop-invariant ??a tunnel on the 1.2 loop, non-indexed |
| 3 | `Bead is good? array out` | OUT | 5859 | ??`RightShiftRegister #5796` | the SR moves to 1.2 |
| 4 | `x,y,z array out` | OUT | 505 | ??`#2222` t2, `#2626` t4 | 1.2 ??`Q_res` |
| 5, 6, 10 | *(unnamed)* | IN | 0 | bare | stay bare |
| 7 | `x,y,z array` | IN | 5975 | ??`#5540` t6 | with #5540 |
| 8 | `pos in cal image out` | OUT | 121 | ??`#10757` t0, `#10969` t0 | 1.2; the slice index also feeds the 1.5 notifier (짠5) |
| 9 | `# of bead 4 packs` | IN | 42 | ??`LoopTunnel #2396` | loop-invariant ??tunnel |
| 11 | `4 pack remainder` | IN | 3512 | ??`LoopTunnel #4432` | loop-invariant ??tunnel |
| 12 | `Array of cal clusters` | IN | 3646 | ??`LoopTunnel #3656` | loop-invariant ??tunnel, **non-indexed** (`IndexMode 0`) |
| 13 | `pos in cal image in` | IN | 7429 | ??`LeftShiftRegister #2972` | the SR moves to 1.2 |
| 14 | `Real-space cosine window` | IN | 3912 | ??`LoopTunnel #3920` | loop-invariant ??tunnel, non-indexed |
| 15 | `Cosine bandpass\nfor Hilbert ` | IN | 4027 | ??`LoopTunnel #4031` | loop-invariant ??tunnel, non-indexed |

**Shape:** 6 loop-invariant inputs through LoopTunnels, 2 per-frame state carriers (SRs #2972 / #5796), 2 inputs
from the reseed case #5540, the image straight from #6810, and three outputs (wires 505, 121, 5859).

### 8a. `GPU_kernel_v1.vi`'s six EXTRA pane inputs, and where each value comes from

The GPU kernel shares the CPU kernel's pane for the 13 named terminals above (`docs/gpu-backend.md:13`) and adds
six of its own (`tools/bench/gpu_kernel_v1_fp.json`; built by `tools/recipes/build_gpu_kernel.py:12-13,:111,:137`).
**None of them exists on `#5058`, so none of them has a rule-1a source ??each must be supplied as a diagram
constant with the value the measured harness used:**

| extra input | what it is | value in D1 | why that value |
|---|---|---|---|
| `Function` | the **`IMAQ GetImagePixelPtr` node's own `Function` input**, promoted to the pane because it is a REQUIRED input (`build_gpu_kernel.py:111`) | the node's default, wired as a constant | not a DLL parameter at all; it belongs to the IMAQ node inside the kernel |
| `cal_path` | path of the `.cal` file for `mt2_open` | **empty** | empty ??the DLL falls back to `MT_GPU_CAL` / `mt_track_cal.txt` (`build_gpu_kernel.py:12`) ??the configuration every measured GPU run used |
| `nb` | bead count for `mt2_track` | **0** | 0 ??the DLL uses the calibration's bead count; the array handle also carries the length (`gpu-backend.md:359`) |
| `status` | `char*` status buffer | **empty** | with `status_len` 0 the DLL writes nothing |
| `status_len` | length of that buffer | **0** | as above |
| `flags` | `mt2_open` flags; bit0 = keep-alive | **0** | the value under which the 8/8 fixture comparison was measured |

?좑툘 **Rule-1a statement, so it is not smuggled:** the 13 shared terminals are wired from the same sources with the
same values as `#5058` had ??that is the equivalence D1 claims. The six extras are **new inputs on a new callee**;
their acceptance is **numeric** (gate N1), not structural, and the numbers already exist for the kernel harness:
over the first 10,018 frames max \|?x\| 4.857e-07 px, \|?y\| 4.677e-07 px, \|?z\| 1.279e-05 쨉m, **0 exceedances**
(`gpu-backend.md` 짠2026-09-17). ?뵶 The **whole-fixture** figures are outside `decisions.md:38` (bead 4, 10 frames
of f11805?밼11823, in the all-beads-lost tail, plus one z flip at k1679) and whether that is acceptable is **STATUS
OPEN 16 ??a judgement call this plan does not take**.

## 9. Queues, names and types (from the proven core, not invented)

`stage2-assembly-step-c.md:21-26` ??**no composite elements**; each direction is lock-stepped queues written by one
producer in one iteration, error-chained so a partial set cannot be published.

| queue | element | type source | bound | overload policy |
|---|---|---|---|---|
| `Q_free` / `Q_work` | IMAQ image refnum + slot index | `IMAQ Create.New Image` sample | **20** (`decisions.md:22`) | full `Q_work` ??skip this read, return the slot in the same iteration |
| `Q_meta` | buffer number, DBL | `#6810 current image number` | unbounded | ??|
| `Q_res` / `Q_good` / `Q_rmeta` | DBL[] / Bool[] / DBL | the kernel's own outputs | unbounded | **lossless FIFO** (`decisions.md:24`) |
| `N_focus` (notifier) | DBL (slice index) | `#5058` t8 | n/a | **latest wins, non-blocking** (짠5) |

Every enqueue takes a **finite** timeout and its `timed out?` is read (`frame-ownership-design.md:80-83`).
**Slot ledger:** every exit path returns the slot exactly once ??normal completion, kernel error, enqueue timeout,
shutdown, writer error.

## 10. Prediction contract

**Phase P ??the probe** (`tools/recipes/probe_move_into_v0.py`; scratch copy only) ??짠2:
* **P0** original md5 `2a78e17c449cacdaf5da389818526859` before AND after.
* **P1z** the working copy is a fresh copy of `OpMoveOut_v0` (ExecState 1, 15 nodes, no U2G) ??rev 7b.
* **P1b** the old reference net's collateral sinks `#237.reference` / `#240.reference` are wired again from `#236`.
* **P1** `OpMoveIn_v0.vi` reads `ExecState 1`.
* **P2 (CONTROL)** `#8885 Multiply` reparents into a new While loop's body ??`OpOwnerChain_v1` reads
  `8885 ??<body Diagram> ??<new WhileLoop>`. A failure here makes the run **INVALID**; conclude nothing.
  ??all of P0?밣5 PASSED on 2026-09-17 ??see 짠2b for the values.
* **P3 (THE QUESTION)** `#12589 CaseStructure` reparents AND its frame diagrams come with it: owner is the new body
  diagram and the VI's total `Diagram` count is unchanged.
* **P4** total `Node` count = before + 1 (the new While loop). `ExecState 0` afterwards is **expected**.
  Census reported: `Wire` and `LoopTunnel` counts before/after, and the body diagram's contents.
  (There is **no per-wire `Wire.Is Broken?` reader** on this fleet ??6371004 is still unbuilt ??so "tunnels vs
  broken" is stated at the level that is readable.)
* **P5** scratch deleted in the same run; handle count before and after.

**Phase S ??structural**, only after phase P is answered:
* **S1** pool + 6 queues + 1 notifier, `ExecState 1`.
* **S2** four loops where there was one; `#637` is still the acquisition loop and still owns `#6810`, `#22700` and
  `CaseStructure #22082`.
* **S3** the kernel call's 13 shared seam inputs come from the **same sources and values** as `#5058` had; whole
  arrays cross the border **non-indexed** (`IndexMode 0`, read back with `tunnels()`); the six GPU extras are
  constants with the 짠8a values.
* **S4** each of the three NEW loops' conditional terminals is written by `exit_while`; **for `#637` the reader now
  exists** ??`OpLoopEndRef_v0` must still read terminal **648 ??wire 3457 ??`#11639`** after the build (this is the
  gate spec decision 5 was built for; rev 2 could not claim it).
* **S5** saved and re-opened at `ExecState 1`. **S6** original md5 unchanged.

**Phase N1 ??numeric, rule 1a.** The kernel-harness branch is already measured and is not re-run. N1 adds the
**in-VI** comparison: the fixture replayed through D1's tracking + writer path, `.tra` against the original's, first
10,018 frames within `decisions.md:38`.

**Phase F1 ??live, ??20 s** (camera only; rig disassembled, no beads ??tracking errors without beads are expected
and are not a failure). Recorded: frames acquired / tracked / written; the streamed file **grows during** the run;
`Q_work`/`Q_res` high-water marks; slot ledger (returned == taken); handle count flat; every TIFF counted and
deleted ???좑툘 `#22700` writes a **1.3 MB TIFF per frame ??118 MB/s at 90 Hz** (STATUS OPEN 18), so F1 must bound
the run or the disk fills in minutes.

**Phase F2 ??stop/restart.** `stop (end)` by `SetControlValue`; all four loops exit; no error 1122; the `.tra` is
written and re-openable; restart 15 s; stop; close without saving; scratch deleted.
?좑툘 **F2 inherits STATUS OPEN 17b**: `drive_original_copy_v3.py`'s R11 scored the *restart*, not the stop, so
"the stop works only in the frame loop" is **unproven** ??F2 must gate on the stop itself (stops `False` +
readback ??run ??one `True` each ??poll values + `ExecState`).

## 11a. DECIDED (judgement session, 2026-09-17) ??answers to 짠11

1. **GPU divergence:** D1 proceeds under the written assumption that it is acceptable (tail-only + one 1-slice
   flip; first 10,018 frames inside tolerance, the same statement made for the CPU replay artefacts). Flagged to
   the user; if overturned, only the kernel subVI is swapped.
2. **Re-wiring list is MEASURED, not static.** 짠8 is the *expected* set. The recipe takes a `node_terms` census
   of every node that will move BEFORE the move, moves, takes it again, and the set of terminals that went
   wired?뭕are is the authoritative re-wire list; gate: that set ??짠8's crossings and every member is re-wired
   (tunnel or queue) before ExecState is read. **Step 0 of the build is the backward-slice census** (the 7 nodes
   of `frame-loop-wire-graph.md:43`): each is classified moves-with-kernel / stays-with-a-tunnel before anything
   moves.
3. **Notifier payload:** step 0 also measures what `#10407` reads per frame from the kernel's outputs. One value
   ??a DBL notifier; more ??a DBL-array notifier (no cluster ??the fleet has no Bundle writer). Same route, same
   values (rule 1a).
4. **Streamed file format is ours:** TSV, one header line, one line per result:
   `buffer_no  t_ms  x_0 y_0 z_0 good_0 ??x_{N-1} y_{N-1} z_{N-1} good_{N-1}`. The `.tra` from `#6384` stays the
   rule-1a artefact; N1 is judged on the `.tra`.
5. **Accepted as recorded**: row 1.7 is built here because `cycle15-plan.md` (user-approved) governs.
6. **Phase P decision A** (do not delete wire 464) could not be realised literally ??no `Terminal.Disconnect`
   exists; the implemented delete-and-rewire reaches the same end state for #237/#240 and is **confirmed**.

## 11. OPEN ??what this plan still does not decide (answered in 11a)

1. ?뵶 **Is the GPU's whole-fixture divergence acceptable?** (STATUS OPEN 16.) N1's tail frames are outside
   `decisions.md:38`. D1 cannot claim rule-1a equivalence over the whole fixture until this is answered.
2. ??**CLOSED by phase P** ??the structure arm PASSED, so the `Make Selection`/`Paste` family (짠2c) is not
   needed and must not be built. What replaces it as a build question: **the move CUTS the border wires**
   (?? wires, ?? tunnels), so D1's build order is *move, then re-wire every cut connection from 짠8's table*, and
   `ExecState` is only meaningful at the end. ?윞 Judgement: is that re-wiring list complete at 짠8, or does the
   backward slice (7 nodes, `frame-loop-wire-graph.md:43`) add rows?
3. ?윞 **The `#10407` notifier payload** ??one DBL or more (짠5). One diagnostic run answers it; it is not a build
   item.
4. ?윞 **Two output artefacts** (짠6.4): is the streamed file's format the user's to specify, or is it ours?
5. ?윞 **Row 1.7 is step 3/4 work placed before step 1's measurement** (`decisions.md:46,:52`;
   `pre-rig-master-plan.md:97`). The user-approved `cycle15-plan.md:28-30` governs; the conflict is recorded, not
   silently resolved.


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-17
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.

Narrative relocated **verbatim** (rule 4): cycle 11??3 ??`archive/2026-09-16-status-cycles-11-13-narrative.md`;
D0 + GPU + lock history ??`archive/2026-09-17-status-d0-and-gpu-narrative.md`; **cycle 15's OPEN 1??1 long forms ??
`archive/2026-09-17-status-cycle15-narrative.md`** (STATUS was 165 lines). Open one only when a line here is
ambiguous. ?좑툘 **ONE SESSION AT A TIME** ??**re-read `CLAUDE.md` and this from disk.**

## START HERE

1. **`docs/pre-rig-master-plan.md` is THE plan**; settled decisions **`docs/decisions.md`**; current cycle plan
   `docs/cycle15-plan.md`; **the build plan under review is `docs/d1-build-plan.md` REV 3**.
2. ??Prior-art gate live (`REFUTED:` / `FIXED:`); **`premature_build` (b) now exempts a RE-RUN** ??see OPEN 22.
3. ??Retrospectives 10??4 done; `retrospective.py` **v2**.
4. ??**Scripting EDITS are silently declined until the target's FRONT PANEL has been opened** ??`ensure_loaded()`.
5. ??**A fixed op PATH is served from LabVIEW's memory, not from disk** ??use a unique working-copy filename per
   run (peer `2026-09-17-moveinto-stale-in-memory-vi.md`, adopted).

## LabVIEW execution lock

```yaml
labview-lock:
  status: acquired
  owner: material/cycle15-d1-build
  since: 2026-09-17 (D1 STEP 0)
  purpose: read-only step-0 census on the ORIGINAL (tunnels / shift regs / panel / OpWireSource_v5); LabVIEW
           restarted first (OPEN 23, 51,530 handles). No writes, no GUI, no hardware.
# 2026-09-17 05:1x-05:3x material/cycle15-movein-rev3: RELEASED. probe_move_into_v0 rev 7c 12 pass / 0 fail; one
# peer (moveinto-stale-in-memory-vi, ANSWERED, disposed). Original md5 2a78e17c449... asserted before AND after;
# scratch SCRATCH_d1move_* and OpMoveIn_v0_<epoch>.vi created+deleted in the same run; OpMoveIn_v0.vi kept as the
# finished op. No GUI, no hardware. ?좑툘 HANDLES 30,849 -> 51,530 in 14 s ??restart before the next batch (OPEN 23).
# Earlier holders and their md5/scratch records: the two 2026-09-17 archives, then the 2026-09-16 one.
```
**Never assume an instance exited**: `tasklist | grep -i labview`, kill strays. Fresh instances ??1,500 handles;
unique scratch VI name per run, deleted in the same run.

## HARDWARE ??permission follows the RIG STATE. Current state: **遺꾪빐 / DISASSEMBLED ??everything allowed**

| rig state | motors (PI 쨌 rotor 쨌 magnet) | **ASI piezo** | camera |
|---|---|---|---|
| **遺꾪빐 ??disassembled ??WE ARE HERE** | ??| ??| ??|
| 議곕┰ ??assembled | ??| ??| ??|
| ?ㅽ뿕以???experiment running | ??| ??| ??|

?좑툘 **The ASI carve-out is RETIRED** (rule 1b). **Only the user announces a state change**; never infer one, never
ask per incident inside a declared state. Instruments: rotor counter **0** 쨌 magnet full travel 쨌 camera 1280횞1024,
offsets 0, 90.0009 Hz, never write `BinningHorizontal`; **a session open RESETS ROI *and* exposure**, so the
acquisition loop applies the contract itself (`tools/bench/camera_contract.py`). **No beads while disassembled**;
fixture work unaffected (10,043 frames, `archive/bench-2026-09-07-fixture/`).

## Where things stand

**Stage 1 (analysis) CLOSED** ??the seven `docs/main-vi-*` files; raw `archive/benchmarks/INDEX.md` 22??1.
**Stage 2 (assembly) IN PROGRESS**: `Track_v6_CPU_core_v0.vi` 69/69 쨌 `??queue_v0.vi` 162/162. **Say it exactly:**
bit-identical to the reference for the **first 10,018 frames only**, and both are **replay** artefacts (recorded
TIFFs, `FOR` loops, no acquisition, no stop protocol). **THE GAP (outcome review):** 168 op VIs, 116 recipes, 218
peer exchanges ??two replay VIs, **zero runnable experimental VIs**; cycle 15 is meant to end that.

## OPEN ??one line each; long forms in `archive/2026-09-17-status-cycle15-narrative.md`

1??, 5, 9??2, 18 ??**all in archive 짠9**: PERIODIC auto-reset ungated (`ForLoop#1359`) 쨌 autofocus CLOSED
   (`#10407` every 25 frames ??3.6 Hz) 쨌 27 undisposed peer archives 쨌 startup drives instruments (blocker at
   assembly) 쨌 A2 54/54, A3 112/170 (the 57 `FlatSequenceFrame` diagrams need ONE new op) 쨌 doc lint 2/4/3 쨌
   **the original writes a 1.3 MB TIFF per frame, ~118 MB/s at 90 Hz ??bound it or the disk fills in minutes**.
13. ??**CLOSED ??the frame loop's stop is MEASURED**: `#637` conditional terminal **uid 648 ??wire 3457 ??
   `CompoundArithmetic #11639`**; `stop (end) 2` #19587 ??#17883 ??`Tunnel#22085` of `CaseStructure#22082` is a
   SEPARATE path. `OpLoopEndRef_v0.vi`, 16/16. ??`docs/main-vi-stop-and-save.md` 짠1; archive 짠1.
14. ?뵶 The cycle-15 prior-art review is only PARTLY disposed ??A7/B3 block on purpose. **Judgement only.** ??짠2.
15. ??`bgrun.py --detach` built. 15b. ?뵶 its deadline kill misses an ORPHANED grandchild ??judgement. ??짠3.
16. ?뵶 **GPU whole-fixture divergence is OUTSIDE `decisions.md:38`** (bead 4, 10 frames of the all-beads-lost tail;
   1 flip at k1679). First 10,018 frames: **0 exceedances**. **Acceptability is a JUDGEMENT call.** ??짠4.
17. ??D0 CLOSED, 16/0. 17b. ?뵶 v3's R11 scored the *restart*, not the stop ??"stop works" is UNPROVEN. ??짠5.
19. ??**D1 REV 3 IS WRITTEN** (`docs/d1-build-plan.md`): the five spec decisions, the measured stop, phase P's
   result, `GPU_kernel_v1`'s six extra pane inputs and their values, the stream+accumulate writer, the minimal 1.5
   focus loop, node-by-node at the seam, and gates S1?밪6 / N1 / F1 / F2. ?뵶 **Its prior-art review is NOT
   dispatched and the build has NOT started ??judgement reads rev 3 first.** Its rev-2 findings ??짠6.
19b. ??**PHASE P ANSWERED, 12 pass / 0 fail, 14 s** (`tools/bench/probe_move_into_v0.log`, rev 7c).
   **`GObject.Move` with a wired `owner` reparents `CaseStructure #12589` WITH ITS CONTENTS** into a new While
   loop's body on Diagram 19 ??owner `Diagram#1170` ??`WhileLoop#1133`, **Diagram count 171 ??171**, Node 626 ??
   627, control arm `#8885` likewise. So the `Make Selection`/`Copy Selection`/`Paste` op family is **NOT needed**
   (it would also have required a GObject-ref array constructor the fleet does not have). ?좑툘 **The move CUTS the
   border wires** (Wire 1902 ??1895, LoopTunnel 132 ??130), so D1 must re-wire afterwards and `ExecState` is
   meaningful only at the end. `OpMoveIn_v0.vi` is BUILT (ExecState 1, UID control `'UID 3'`). Runs 1?? ??짠7.
20/21. ?뵶 Cycle 14's retrospective left two slugs DUE; ??both round-5 devices built. ??짠8.
22. ??**NEW ??`guard_cycle.premature_build` (b) now applies only to a recipe's FIRST run after its review.** If a
   build log `tools/bench/<recipe-stem>*.log` is newer than the newest prior-art archive, a re-run is allowed; a
   failed prediction is `guard_peer`'s gate, not this one. With **no** prior-art review archived it still blocks.
   Self-test `tools/bench/selftest_guard_cycle_rerun.log` **4/4** (first-run?뭨efused 쨌 re-run?뭓llowed 쨌
   no-review?뭨efused 쨌 regression review-newer?뭓llowed). `_rel()` added so a cross-drive path cannot crash the hook.
23. ?윞 **NEW ??handle count jumped 30,849 ??51,530 in one 14 s probe run** (baseline ??1,500). Restart LabVIEW
   before the next batch; attribution is a one-run `tools/bench/handle_audit.py` job, not a build item.

## NEXT

?뵶 **JUDGEMENT, in order:** (1) **read `docs/d1-build-plan.md` REV 3** and decide its five OPEN items ??chiefly
**#1 the GPU divergence (OPEN 16)** and **#2 the re-wiring list after a move**; (2) the two DUE slugs of OPEN 20
(`py tools/violations.py --due`); (3) authorise the build order, which is when the plan's prior-art review is
dispatched. ?윟 Then MATERIAL: the D1 build recipe ??one script, S1?밪6 ??N1 ??F1 ??F2, on a copy in claudeDev.

## Where to look

`CLAUDE.md` rules 쨌 **`docs/decisions.md`** settled 쨌 `docs/NAMES.md` strings 쨌 `docs/toolkit-capabilities.md` API 쨌
`docs/d1-build-plan.md` **the build under review** 쨌 `docs/restructure-plan-4.6.md` target 쨌
`docs/pre-rig-master-plan.md` the plan 쨌 `docs/diagram-hierarchy.md` A2/A3 쨌 `docs/gpu-backend.md` GPU 쨌
narrative: the three status archives 쨌 `archive/` history (rule 4).


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Prior-art review complete — read-only, no lock taken, nothing built or run. **8 findings, zero `novel`.** The single most costly one is A1/A2: a 12/12 diagnostic run (`tools/bench/diag_d1_step0.log`, 2026-09-17 05:35) already measured two of the plan's five OPEN items and produced a third fact — a **reverse crossing out of the new 1.5 loop** — that no section of REV 3 has a route for. The plan's `measured_in:` frontmatter does not list that log.

---

# PART A — THE DIRECTION

## A1 `already-measured` — the notifier payload width and the backward-slice classification are already measured; the plan defers both to "step 0 of the build"

`docs/d1-build-plan.md:196` — *"the equivalent for `#10407` is **not measured** and is a one-run diagnostic, not a build item"*; `:347` — *"step 0 also measures what `#10407` reads per frame"*; `:344` — *"**Step 0 of the build is the backward-slice census** (the 7 nodes of `frame-loop-wire-graph.md:43`)"*; `:366` (OPEN 3) — *"One diagnostic run answers it"*.

That run happened, 12/12 gates, 35 s, MAIN md5 unchanged:

- `tools/bench/diag_d1_step0.log:143` — *"FACT **NOTIFIER PAYLOAD WIDTH (measured) = 1 value(s)**: [(10407, 2, 'Index of closest\ncal image slice, bead 2')]"*. So §5's ⚠️ branch (cluster → no Bundle writer → DBL array or a second notifier) is closed: one DBL.
- `:129` (gate G8) — all seven backward-slice nodes already carry exactly one classification: `{5540: stays-with-tunnel, 6810: stays-with-acquisition, 9647/10247/10445/10950/17289: stays-with-tunnel}`, each with its reason printed at `:79-128`.
- `:146` — the BEFORE census is on disk: `tools/bench/d1_step0_census.json` (47 nodes on d43, 5 on d19), which is exactly the artefact `:343-344` says the recipe must take *before* the move.

**Scope:** this does not touch the *design* decisions of §5 or §11a; it says the three measurements they are waiting on are done, and a build that re-runs them repeats a 35 s run whose output is already in `tools/bench/`.

## A2 `unread-evidence` — the same log records a REVERSE crossing out of the new focus loop, and 91 boundary wires where §8 tables 16

`docs/d1-build-plan.md:169` sends `CaseStructure #10407` to the new 1.5 loop and `:165-167` sends `CaseStructure #12589` to 1.2. `:182-185` designs **one** direction of traffic (tracking → focus, latest-result notifier).

- `tools/bench/diag_d1_step0.log:145` — *"FACT **REVERSE CROSSING**: `#10407` t6 'position [internal units]' **w9113** → `#12589` 'Case Structure' 'position [internal units]' (a value the 1.5 loop produces that a node outside it consumes)"*. §8's per-terminal table (`:230-247`) has no row for wire 9113 — it tables `#5058`'s 16 terminals only — and §9's queue/notifier table (`:277-285`) carries nothing in that direction. As written, D1 splits a per-frame data dependency with no transport.
- `:8` — *"FACT **91 boundary wires** on the move set (one census end only)"*, of which `:18` says 81 resolve to tunnels/SRs/panel and 10 do not. The plan's OPEN 2 (`:362-365`) asks precisely *"is that re-wiring list complete at §8, or does the backward slice add rows?"* — the count exists.
- `:141-142` — `#48` t3 `VISA resource name` ← `LeftShiftRegister #4344` and t4 `In position` ← `LeftShiftRegister #4274`. §5's *"its other inputs by the same route and values as today"* (`:34`) is, for these two, a shift register of the loop the case is being moved **out of**.

**Scope:** covers §5's handoff design and §8's table only. It does not claim the notifier is wrong; it claims the plan is missing the return path and the measured size of the re-wiring job.

## A3 `contradicted` — F1's floor is 20 s here and 5 minutes in the user-approved gate

- `docs/d1-build-plan.md:324` — *"**Phase F1 — live, ≥ 20 s**"*.
- `docs/cycle15-plan.md:77` (the `decided_by: user 2026-09-16` acceptance table) — *"D1 runs live on the camera at 90 Hz with no beads … **for ≥ 5 min**, produces a data file through the original's writer, and the file reopens"*.
- `archive/prose/2026-09-17-d1-d2-explained-r2.md:136`, the text the user approved — *"F1 **카메라 라이브 5분** + 파일 생성·재열기"*.

A run gated at 20 s satisfies the plan's prediction contract and fails the cycle's. The plan supplies the reason for the tension at `:326-328` (`#22700` ≈ 118 MB/s ⇒ ~35 GB over five minutes) and reconciles it nowhere — no section says the 5-minute gate is amended, or how F1 reaches it with the TIFF write unconditional. Both documents are `status: current`.

## A4 `settled-already` — F1's "Recorded:" list re-specifies an adopted instrumentation minimum, against a rule written to stop exactly that

`docs/d1-build-plan.md:325-326` records six items (frames acquired/tracked/written, file grows, `Q_work`/`Q_res` high-water, slot ledger, handles, TIFFs); `:221` calls the reconciliation gate *"(new — no equivalent exists in `tools/bench/` or `archive/benchmarks/INDEX.md`)"*.

- `docs/pre-rig-master-plan.md:55` (item 0.2) — *"**What every run records — the list already exists; use it, do not re-specify it.** `stage2-plan.md:83-88` holds the **adopted** live-instrumentation minimum … **with its acceptance** … a run whose settings are not recorded is not a measurement; **a list that exists twice drifts**."* The same row adds the four items that list predates: *the stop reason, the motor command/readback pairs, the reseed counter, and the full front-panel control snapshot.*
- `docs/stage2-plan.md:83-88` is that list — requested/returned buffer numbers, gap count/size, overwrite/error count, acquisition-call duration p99.9/max, acquisition→dequeue and acquisition→kernel-done latency, enqueue timeouts, longest full interval, acquired/copied/enqueued/dequeued/processed/returned counts, slot-invariant violations — *"Acceptance = zero gaps, zero drops, zero slot violations, processed = acquired"*. That acceptance **is** §7's reconciliation gate in specification form; `pre-rig-master-plan.md:159-165` (2A) states it again as run criteria.

**Scope:** the *implementation* of a buffer-number reconciliation check may well be new; the **specification and its acceptance are adopted**, so §7 and F1 must cite them rather than write a shorter list beside them.

## A5 `contradicted` — "the only owner of the ASI VISA session" is false as measured, and the session it isolates has no close

`docs/d1-build-plan.md:179-181` — *"`CaseStructure #10407` and `#48 ASI_adjust focus-subvi.vi` move to their own While loop, **which is the only owner of the ASI VISA session**. Nothing on the frame path can block on it — rule 1c is satisfied **by construction**"*.

- `docs/main-vi-panel-map.md:550` — *"| 99 (display loop) | … | `ASI_adjust focus-subvi.vi` (**second call site**) |"*; `:558` — *"`ASI_adjust focus-subvi.vi` — **non-reentrant by design** — is called from **both the frame loop (43) and the display loop (99)** with the same three button references."* Moving uid 48 relocates one of two call sites; the other keeps calling the same non-reentrant VI.
- `docs/pre-rig-master-plan.md:74` (A7b) names this VI as the project's one confirmed instance of the hazard: a shared non-reentrant subVI is *"**an accidental mutex**: the second caller blocks until the first returns, and if the first is inside a serial round trip the frame loop stops for exactly that long"*.
- The exclusivity requirement itself is settled and has a recorded reason the plan does not carry: `archive/2026-09-16-status-cycles-8-10-narrative.md:182-183` — *"the ASI loop must **exclusively own the VISA session**, because case `#10407`'s **`Outgoing Handle` carries resource ownership, not just a value**."*
- And the shutdown: `docs/main-vi-stop-and-save.md:136` — `ASI TG-1000.lvlib:Close.vi` #29815 has *"every terminal **bare** (wire 0) — no error chain, no VISA wire on this diagram"*; `:143-145` — *"**No VISA Close node is on diagram 83**"*. `archive/prose/2026-09-17-d1-d2-explained-r2.md:178` states the consequence the user was shown: *"원본에 VISA Close가 없고 ASI Close가 미배선이므로 **1.9에서 새로 넣어야 한다**"*. `docs/d1-build-plan.md:330-331` (F2) gates on error 1122 and the `.tra`, not on the VISA/ASI close of the loop D1 newly makes the session's owner.

**Scope:** blocks the exclusivity claim and the words *"by construction"*, plus F2's shutdown coverage. It does **not** block giving row 1.5 its own loop — that is settled at `docs/pre-rig-master-plan.md:91`.

---

# PART B — THE ARTIFACT

## B1 `unread-evidence` — the notifier is a transport the fleet cannot build, chosen without the check that row 1.3 exists to force

`docs/d1-build-plan.md:34`, `:169`, `:182-185`, `:284` make the wake-up a LabVIEW **Notifier** (`N_focus`, latest-wins, non-blocking).

- `tools/gscript.py:923-924` — `_QUEUE_OPS = {"obtain": …, "enqueue": …, "dequeue": …, "release": …}`, four erdosmiller **queue** creators; `:928` `queue_node()` is the only primitive-placing wrapper of that kind, and the word *notifier* appears nowhere in `gscript.py` or in `tools/recipes/`. `docs/toolkit-capabilities.md:32` lists the same four and nothing else.
- `docs/toolkit-capabilities.md:549-553` is the rule this file was written to enforce: *"Before a plan depends on a capability, it must name **where that capability was last exercised**. If the answer is 'it is in the list' … the plan has an untested assumption in it and should say so out loud — as a gate, with a cheap test scheduled before the work that depends on it."* §5 and §9 name no exercise.
- `docs/pre-rig-master-plan.md:89` (row 1.3) records this exact mistake being made and caught: *"**(ii) The replacement was not buildable.** 'One cluster local' was proposed **without checking the fleet** … So the requirement is fixed and the transport is not … **Pick before loop 3 is built, not now, and record the pick here**; do not build 1.3 against the sentence that happens to be in front of you."* The plan cites `toolkit-capabilities.md:32,:46-49` at `:193-194` for the *cluster* half of that lesson and not the transport half.
- There is no donor to copy one from: `ARCHITECTURE.md:60` — *"**No LabVIEW Queue, Notifier, Semaphore, or Rendezvous primitives appear anywhere** in the decompiled text of 4.4/4.5/4.6"*, and `copy_into` / `copy_by_index` need a labelled donor object (`docs/toolkit-capabilities.md:122`).
- Building the three notifier ops collides with `docs/cycle15-plan.md:104` — *"**No new general-purpose op VIs**, no hierarchy completion beyond what D1 needs"* — the freeze the outcome review imposed for the duration of this build.

**Scope:** the *requirement* (lossy, non-blocking, latest-wins, no serial on the frame path) is settled and not challenged. What has no prior art is the **mechanism**: a notifier has never been created by this fleet, and the two buildable alternatives already named for the identical problem are lock-stepped publication (`docs/stage2-assembly-step-c.md:21-26`, 162/162) and a donor typedef built as an explicit item.

## B2 `contradicted` — "those seven come from the writer loop's own shift registers" is not what `#6384`'s inputs were measured to be

`docs/d1-build-plan.md:210-212` — *"seven come off `#637`'s output tunnels and the eighth is an `Array Subset` (#2048) … In D1 those seven come from **the writer loop's own shift registers** instead — **same values, different carrier**, which is scheduling."*

`docs/main-vi-stop-and-save.md:115-121`, the measurement the same paragraph cites:

| `#6384` input | measured source |
|---|---|
| t5 `desired # data points` | `#637` **outer terminal 14** — also feeds `dimension size` of `#781` (Initialize Array, outside the loop) |
| t6 `cal cluster path` | `#637` **outer terminal 23** |
| t11 `base path/filename` | `#637` **outer terminal 17** |
| t7 `actual # data points` | `#637` t19 **`file progress`** |
| t10 `file # to append` | `#637` t18 **`file number to append out`** |

The first three are loop-invariant values passing *through* the loop, not accumulated per-frame state — a writer-loop shift register is not the same carrier, it is a different source. The next two are **outputs of `#376 save trace.vi`**, not of any register: `docs/frame-loop-wire-graph.md:168` (wire 5274, *source only*, `#376` t3 `file progress`) and `:166` (wire 5056, *source only*, `#376` t4 `file number to append out`). Reproducing them means reproducing `#376`'s computation, which CLAUDE.md rule 1a calls a change of decomposition requiring justification or a numeric check.

And the plan does not say what becomes of `#376`: REV 2 gave the writer loop *"`#376 save trace.vi` and its three shift registers"* (`archive/peer/2026-09-17-priorart-priorart-d1-build.md:113`); REV 3's §4 writer row (`docs/d1-build-plan.md:171`) drops it and no later section places it, while `docs/main-vi-stop-and-save.md:151` still lists it as one of diagram 43's six subVI calls and `:125` as `#6384`'s in-loop partner through wire 541.

## B3 `unread-evidence` — F1's pass criterion "the streamed file grows during the run" has a recorded no-bead failure mode, with a prescribed remedy, neither of them cited

`docs/d1-build-plan.md:325` records *"the streamed file **grows during** the run"* as an F1 result, under the no-bead condition stated in the same paragraph.

`docs/pre-rig-master-plan.md:269-274` — *"⚠️ **One thing to verify in the run rather than assume.** With no beads and no reseed, `Bead is good?` stays false for every bead. If anything downstream is gated on bead validity — **`save trace.vi` #376 writing records**, the WLC fit, **the result enqueue** — those paths may sit idle, and **'the file writer loop ran' would be a false positive**. So the run's record must show **what each loop actually did** … rows written, results enqueued and dequeued, bytes on disk. **If the writer turns out to be starved, inject synthetic results** rather than turning `Auto-Reset` back on."*

The condition that makes this live is already decided for these runs: `docs/pre-rig-master-plan.md:195-200` — *"**✅ DECIDED by the user, 2026-09-16: `Auto-Reset` OFF**"*. So under D1's own F1 conditions the gate can read empty for a reason that is not a defect, and it can read non-empty without proving anything about ordering — and the remedy has been chosen in advance.

---

## Where I found NO prior art

- **Move-then-rewire as a build ORDER** (`docs/d1-build-plan.md:339-345`): that `GObject.Move` cuts border wires (Wire 1902→1895, LoopTunnel 132→130) is new to `tools/bench/probe_move_into_v0.log`, and no earlier document prescribes a re-wire pass after a relocation.
- **`OpMoveIn_v0.vi`** — built and gated this cycle; nothing earlier reparents a structure with its contents. The 2026-09-13 exchange said the opposite (`archive/peer/2026-09-13-scripted-diagram-selection.md:162`) and was refuted by measurement, which is recorded.
- **The TSV streamed format** (`docs/d1-build-plan.md:349-351`) — no format is decided anywhere for row 1.7; `pre-rig-master-plan.md:93` gives only the acceptance.
- **Four loops inside a copy of the original at this scale** — `docs/decisions.md:19` calls scale *"untested"*, which is a statement that it has not been done.

---

```
PRIOR-ART: already-measured   (A1 — tools/bench/diag_d1_step0.log:143 notifier width = 1, :129 the 7-node backward-slice classification, :146 d1_step0_census.json vs docs/d1-build-plan.md:196,:344,:347,:366)
PRIOR-ART: unread-evidence    (A2 — tools/bench/diag_d1_step0.log:145 reverse crossing w9113 #10407 t6 -> #12589, :8 91 boundary wires, :141-142 #48's VISA-name shift register, vs docs/d1-build-plan.md:182-185,:230-247)
PRIOR-ART: contradicted       (A3 — docs/d1-build-plan.md:324 "F1 >= 20 s" vs docs/cycle15-plan.md:77 ">= 5 min" and archive/prose/2026-09-17-d1-d2-explained-r2.md:136)
PRIOR-ART: settled-already    (A4 — docs/pre-rig-master-plan.md:55 "the list already exists; use it, do not re-specify it" + docs/stage2-plan.md:83-88 vs docs/d1-build-plan.md:221,:325-326)
PRIOR-ART: contradicted       (A5 — docs/main-vi-panel-map.md:550,:558 second non-reentrant call site on diagram 99, docs/pre-rig-master-plan.md:74, archive/2026-09-16-status-cycles-8-10-narrative.md:182-183, docs/main-vi-stop-and-save.md:136,:143-145, archive/prose/2026-09-17-d1-d2-explained-r2.md:178 vs docs/d1-build-plan.md:179-181,:330-331)
PRIOR-ART: unread-evidence    (B1 — tools/gscript.py:923-924,:928; docs/toolkit-capabilities.md:32,:549-553; docs/pre-rig-master-plan.md:89; ARCHITECTURE.md:60; docs/cycle15-plan.md:104 vs docs/d1-build-plan.md:34,:182-185,:284)
PRIOR-ART: contradicted       (B2 — docs/main-vi-stop-and-save.md:115-121,:125,:151 and docs/frame-loop-wire-graph.md:166,:168 vs docs/d1-build-plan.md:210-212,:171)
PRIOR-ART: unread-evidence    (B3 — docs/pre-rig-master-plan.md:269-274,:195-200 vs docs/d1-build-plan.md:325)
```

One note for whoever disposes of this: A1 and A2 are cheap to clear — the log is 35 s old work already on disk, so the disposition is "cite it and fold its three facts into §5, §8 and §11a", not a new run. B1 is the one that can change the cycle's shape: if the notifier stays, an op family has to be built inside a freeze that forbids it, so the decision belongs to a judgement session, not to the build recipe.

## Sources

(extract from answer)

## What was done with it

Disposed 2026-09-17 by the MATERIAL session `cycle15-d1-build`. **8 findings: 2 FIXED in the plan, 6 ACCEPTED as
facts whose consequent decision is JUDGEMENT and is therefore escalated, not taken here** (CLAUDE.md §3 — a
material session does not take design decisions, rule-1a calls, or "what to accept from a review"). **No finding
is refuted.** The plan file edited is `docs/d1-build-plan.md`; the new section is **§0-MEASURED** (§0a–§0d).

**FIXED:** `A1` `already-measured`. Correct, and the run is this session's own: `tools/bench/diag_d1_step0.log`
(12/12, 35 s) plus the offline re-classification `tools/bench/diag_d1_step0_reclass.log` (8/8). Folded into the
plan as **§0-MEASURED §0a/§0b/§0c**, with `tools/bench/d1_step0_census.json` named as the BEFORE census §11a.2
diffs against. Notifier payload width = **1 DBL**, so §5's cluster branch is closed in writing.
⚠️ **One correction to the finding itself, and it matters.** A1 quotes `diag_d1_step0.log:129`, where six of the
seven backward-slice nodes read `stays-with-tunnel`. **That classification was wrong and has been withdrawn.** It
came from a wire-graph-only edge model, and on this diagram the data does not travel only on wires: the kernel's
outputs re-enter through **shift registers** (not in `Nodes[]`, `toolkit-capabilities.md:494`) and the reseed
selector runs **through a front-panel indicator** (`#10969` writes `min value` #17257; the implicit property
`#17289` reads it back). With both carriers measured and in the model, the answer is
`{5540, 9647, 10247, 10445, 10950, 17289: moves-with-kernel; 6810: stays-with-acquisition}` — which **agrees**
with `docs/d1-build-plan.md` §4/§8 (gate **G9**). Anyone citing `:129` must cite `diag_d1_step0_reclass.log`
instead.

**FIXED:** `A2` `unread-evidence`. Accepted in full and made worse by re-measurement, so it is recorded rather
than argued: §0-MEASURED **§0b** tables the reverse crossing `#10407` t6 → w9113 → `#12589` → `#11639` (the
acquisition loop's stop) and states plainly that §3/§4 give it no transport; **§0c** tables **all 14 shift
registers** with what each carries, which shows §8's "2 per-frame state carriers" undercounts — the build must
create **4 registers on 1.2, 2 on 1.5 (including the one carrying the VISA session), 2 on 1.7**; the 91 boundary
wires are resolved (81 by tunnel/SR/panel censuses, 10 by `OpWireSource_v5`, all `DigitalNumericConstant`).

**ACCEPTED → JUDGEMENT:** `A3` `contradicted` (F1 ≥ 20 s here vs ≥ 5 min in the user-approved
`cycle15-plan.md:77`). Both documents are `status: current` and the 5-minute figure is the **user's**; reconciling
them is not a material call, and it interacts with the ~118 MB/s TIFF write. Escalated.

**ACCEPTED → JUDGEMENT:** `A4` `settled-already` (F1's "Recorded:" list re-specifies the adopted
`stage2-plan.md:83-88` minimum). The citation is exact. Rewriting §7/F1 to cite the adopted list instead of a
shorter one beside it is a plan edit whose content is a specification choice; escalated with the citation.

**ACCEPTED → JUDGEMENT:** `A5` `contradicted` — the strongest finding, and it invalidates a claim the plan makes
"by construction". `#48 ASI_adjust focus-subvi.vi` has a **second call site on diagram 99**
(`main-vi-panel-map.md:550,:558`) and is **non-reentrant**, so moving uid 48 does not make the new 1.5 loop the
only owner of the VISA session; and no `VISA Close` exists (`main-vi-stop-and-save.md:136,:143-145`), which F2
does not gate. Whether D1 proceeds, and under what wording, is judgement. **Not measured here and not assumed
away.**

**ACCEPTED → JUDGEMENT:** `B1` `unread-evidence` — the reviewer's own "this is the one that can change the
cycle's shape", and this session agrees. The fleet has **four queue creators and no notifier anything**
(`gscript.py:923-928`); building the notifier ops collides with the cycle-15 freeze (`cycle15-plan.md:104`). The
requirement (lossy, non-blocking, latest-wins, no serial on the frame path) is settled; the **mechanism** is not,
and picking it is exactly the decision `pre-rig-master-plan.md:89` says to record rather than assume. Escalated.

**ACCEPTED → JUDGEMENT:** `B2` `contradicted`. The citation holds: three of `#6384`'s inputs are loop-invariant
values passing *through* `#637`'s tunnels and two are **`#376 save trace.vi`'s own outputs**, so "the writer
loop's own shift registers" is a different source, not a different carrier — and §4 places `#376` nowhere.
§0-MEASURED §0c records which registers are the writer's (`#15/#51` accumulator, `#24/#1108` error chain), which
is the measured half; where `#376` goes is a rule-1a decomposition call. Escalated.

**ACCEPTED → JUDGEMENT:** `B3` `unread-evidence` (with no beads the writer may be starved, so "the file grows" is
not a valid F1 gate; `pre-rig-master-plan.md:269-274` prescribes injecting synthetic results). Accepted; F1's
gate needs rewriting, which is a plan edit with an acceptance consequence. Escalated.

**Net effect on this session:** the D1 build recipe was **NOT written and NOT run**. Three of the six escalated
findings (A5, B1, B2) change what the build would construct, so writing it now would be building against a plan
the review has already stopped. Step 0 (the census this review's A1/A2 point at) is complete and is the material
this hand-off exists to give the judgement session.
