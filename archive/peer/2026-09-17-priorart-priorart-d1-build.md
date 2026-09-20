# priorart-priorart-d1-build

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.9996  in 56 / out 34796 / cache-create 212752 / cache-read 4003863  (484s, 39 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (487s)
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
date: 2026-09-17
cycle: 15
kind: build
tags: [d1, delivery, seven-loop, acquisition, tracking, writer, stop]
parent: docs/cycle15-plan.md
spec_rows: [pre-rig-master-plan.md 1.1, 1.2, 1.7, 1.8, 1.9]
---

# D1 build plan ??the first slice of the seven-loop VI, inside a COPY of the original

One page, node-by-node, written **before** the build (CLAUDE.md work cycle step 1). Target
`C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Track_v6_D1_GPU.vi` = a fresh copy of
`Min_Track N beads V6_ParallelLoop.vi` (md5 `2a78e17c449cacdaf5da389818526859`, verified before and after every
run; the original is never opened for writing ??rule 1).

**Tracker (assumption handed down by the judgement session, not re-decided here):** `GPU_kernel_v1.vi`. Its
connector pane is the seam's pane minus the GPU-only extras (`tools/bench/gpu_kernel_v1_fp.json`;
`docs/gpu-backend.md:13`). If overturned, one subVI path changes and nothing else.

## 0. What is already built, and is therefore NOT re-derived here (prior-art, checked first)

| need | what already exists | where |
|---|---|---|
| the seam's 16 terminals, every wire, every other end | **measured** | `docs/main-vi-stop-and-save.md` 짠4 |
| the stop control wiring (`stop (end)` uid 7, `stop (end) 2` uid 19587, both read INSIDE Diagram#639) | measured | same file 짠1 |
| `save N xyz traces.vi` #6384 sits on diagram 19 AFTER the loop, 7 of 8 inputs off #637's tunnels | measured | same file 짠2 |
| shutdown frame (diagram 83: IMAQdx Stop/Close, ASI Close, IMAQ Dispose) | measured | same file 짠3 |
| the kernel's forward slice = **14 nodes**, backward slice = 7 | measured | `docs/frame-loop-wire-graph.md:43-45` |
| producer/consumer core with 6 lock-stepped queues + pool, numerically accepted | **built** (`Track_v6_CPU_core_queue_v0.vi`, 162/162) | `docs/stage2-assembly-step-c.md` |
| queue ops (`obtain/enqueue/dequeue/release`), `while_loop`, `loop_in`, `exit_while`, `add_shift_reg`, `wire_sr`, `drop_subvi`, `delete_object`, `remove_bad_wires_scripted` | built + functionally verified | `docs/toolkit-capabilities.md:24-35, 41-44` |
| in-copy migration (create a loop inside an existing VI 쨌 drop a subVI in its body 쨌 wire a control across the border 쨌 ExecState 1) | **proven 3/3 and 5/5** | `tools/recipes/probe_migrate_v2.py`, `probe_migrate_v3.py` |
| unattended drive of the original copy through stages 0?? (picks, 3횞 bandpass Yes, save dialog, run, stop, restart) | **built, 16 pass / 0 fail** | `tools/bench/drive_original_copy_v3.py` |
| camera contract writer (`ExposureAuto=Off`, `ExposureTime??556 쨉s`, read-back) | built | `tools/bench/camera_contract.py` |
| frame accounting subVI `get buff image-lost frames.vi` #6810 | the original's own | `docs/frame-loop-anatomy.md:47` |

## 1. The seam, and the one operation D1 needs that has never been exercised

`WhileLoop #637` owns `Diagram 43` (75 nodes, 14 shift registers). D1 must end with **three** loops where there
is one. The tracker `#5058` is deleted and `GPU_kernel_v1.vi` is dropped into the new TRACKING loop ??that part
is exactly `probe_migrate_v3`. **What is new is that the kernel's FORWARD SLICE must travel with it.**

`frame-loop-wire-graph.md:45` ??the 14 nodes downstream of `#5058`:

```
#376 save trace.vi 쨌 #1359 ForLoop 쨌 #2222 CaseStructure 쨌 #2626 Build Array 쨌 #6104 Index Array 쨌
#8885 Multiply 쨌 #9833 Index Array 쨌 #10407 CaseStructure (autofocus) 쨌 #10757 Index Array 쨌
#10969 Array Max & Min 쨌 #11261 Build Array 쨌 #11639 Compound Arithmetic (the stop OR) 쨌
#12589 CaseStructure 쨌 #29874 ForLoop
```

Plus the backward slice's `#5540 CaseStructure` (the reseed case, feeds tracker t0 and t7) and the two per-frame
state carriers `LeftShiftRegister#2972` / `RightShiftRegister#5796`.

So D1's assignment is:

| loop | keeps / receives | how |
|---|---|---|
| **1.1 ACQUISITION** = the existing `WhileLoop #637` | `#6810 get buff image-lost frames.vi` (the frame source, row 1.8 ??**REUSED, not replaced**; decision recorded in 짠4), `#22700 IMAQ Write TIFF File 2` (**unconditional, exactly as the original has it**), the camera reads, the stop terminals | nodes stay where they are; only additions |
| **1.2 TRACKING** = a NEW While loop on **Diagram 19** (the flat-sequence frame that owns #637, so it is a sibling loop) | `GPU_kernel_v1.vi` (new call), `#5540`, `#2222`, `#2626`, `#10757`, `#10969`, `#6104`, `#8885`, `#9833`, `#11261`, `#12589`, `#1359`, `#29874`, the two shift registers | kernel = `drop_subvi`; **the 13 existing nodes must be REPARENTED from Diagram 43 into the new body diagram** |
| **1.7 WRITER** = a NEW While loop on Diagram 19 | `#376 save trace.vi` and its three shift registers (`total data array`, `file number to append`, `file progress`) | reparented likewise |
| **1.9 STOP** | `#11639` (the OR node both stop Booleans feed) is itself in the forward slice; each of the three loops gets its own in-loop Boolean read via `exit_while` / `OpExitWhile_v0` | |
| **D2, not D1** | `#48 ASI_adjust focus-subvi.vi` and `#10407` (autofocus) ??but `#10407` is IN the forward slice, so D1 must place it somewhere | **see the OPEN item below** |

**The unexercised operation, named plainly.** `gscript.move_out()` (`OpMoveOut_v0`) proves `GObject.Move` with an
`owner` input reparents a node **from a nested diagram to the VI's top-level diagram**. Nothing in
`docs/toolkit-capabilities.md` records a move **INTO an arbitrary diagram**, and nothing records moving a
**Structure with its contents**. `restructure-plan-4.6.md:141` calls a node-by-node move "large and risky", and
`toolkit-capabilities.md:373` says "'move a node' was never needed" ??for the op fleet's own build, which had no
existing code to relocate. D1 does.

**Therefore the build's first phase is a PROBE, not construction** (CLAUDE.md: "the second time a class of failure
is explained by inference rather than read from the machine, the next build is the READER for it"). The probe is
`tools/recipes/probe_move_into_v0.py`: on a scratch copy of the original it builds `OpMoveIn_v0` (the `move_out`
op with its `owner` taken from `Diagram`[index] instead of `VI.Block Diagram`) and asks four questions. Its
answers decide whether phases 2?? below can run at all.

## 2. Queues, names and types (from the proven core, not invented)

`stage2-assembly-step-c.md:21-26` ??**no composite elements**; each direction is lock-stepped queues from one
producer in one iteration, error-chained so a partial pair cannot be published.

| queue | element | type source | bound | who obtains |
|---|---|---|---|---|
| `Q_free` | IMAQ image refnum | `IMAQ Create.New Image` sample | 20 | stage-0 (pool loop), seeded at creation |
| `Q_work` | IMAQ image refnum | same | 20 | stage-0 |
| `Q_meta` | buffer number, DBL | `#6810 current image number` | unbounded | stage-0 |
| `Q_res` | `x,y,z array out`, DBL[] | the kernel's own output | unbounded (lossless FIFO, row 1.7) | stage-0 |
| `Q_good` | `Bead is good? array out`, Bool[] | kernel output | unbounded | stage-0 |
| `Q_rmeta` | buffer number, DBL | same sample | unbounded | stage-0 |

Pool = **20 slots** (`decisions.md:22`, `frame-ownership-design.md:49-51` ??depth absorbs jitter only).
Every enqueue takes a **finite** timeout and its `timed out?` is read (`frame-ownership-design.md:80-83`); a full
`Q_work` means **skip this read** and return the slot to `Q_free` in the same iteration (`decisions.md:24`), which
is the one and only place a slot can be returned twice ??gated by the ledger in 짠5.
Shutdown order is **stop the users ??drain ??release**, so no `error 1122`.

## 3. Camera contract (row 1.1, and it lives on diagram 87 only)

`ExposureAuto = Off` and `ExposureTime ??5556 쨉s` are written on **diagram 87 immediately after
`IMAQdx Open Camera`**, then read back into the batch record. A session open resets them, so no external pre-pass
can do it (`decisions.md:37`). `Buffer Number Mode = Last` on `IMAQdx Get Image`.

## 4. Frame accounting ??the written decision row 1.8 demands

**REUSE `get buff image-lost frames.vi` #6810.** It is the frame source itself (`frame-loop-anatomy.md:47`); it
already produces `Missed frames?` and `current image number`, and `current image number` is the buffer number that
becomes `Q_meta`/`Q_rmeta`. Replacing it would change the computation on the acquisition path (rule 1a) for no
gain. Its per-call cost stays on the acquisition loop, which is where the original paid it. Reconciliation gate:
the writer's recorded buffer-number series must be a strictly increasing subsequence of the acquisition loop's,
and `Total Lost Frames` must equal the number of skipped buffer numbers.

## 5. Prediction contract

**Phase P ??the probe (decides everything after it).** `tools/recipes/probe_move_into_v0.py`, scratch copy only:
* **P1** `OpMoveIn_v0` builds and is `ExecState 1`.
* **P2** a plain node (`#8885 Multiply`) moves from `Diagram 43` into a new While loop's body diagram on
  `Diagram 19`: its `Generic.Owner` chain reads `<new body> ??<new WhileLoop>` afterwards (`OpOwnerChain_v1`).
* **P3** a **Structure** (`#12589 CaseStructure`) moves the same way **and its contents move with it** ??the
  owner chain of one node inside #12589 still terminates at #12589 after the move.
* **P4** after `remove_bad_wires_scripted`, the copy is `ExecState 0` (expected ??wires were cut) and no node is
  lost: the total `Node` count is unchanged.
  *Any of P2/P3 failing = D1 as specified is not buildable with today's fleet; the run stops and reports.*

**Phase S ??structural, only if P passes.** S1 pool + 6 queues obtained, `ExecState 1`; S2 three loops exist with
`#637` still the acquisition loop; S3 the kernel call has all 16 seam inputs wired from the SAME sources and
values as `#5058` had, whole-array parameters crossing the loop border **non-indexed** (`IndexMode 0`, read back
with `tunnels()`); S4 every loop's conditional terminal is driven by a Boolean read **inside** it; S5 saved and
re-opened at `ExecState 1`; S6 original md5 unchanged.

**Phase N1 ??numeric, rule 1a.** Offline replay of the 10,043-frame fixture through D1's tracking+writer path (or,
if D1 cannot be fed TIFFs without changing its acquisition loop, through the kernel harness ??the run says which
it used) against the CPU reference: **first 10,018 frames within `decisions.md:38`** (x,y ??1e-6 px, z ??1e-4 쨉m,
0 flips).

**Phase F1 ??live, 20 s.** Driven by `drive_original_copy_v3.py`'s method (3 picks, bandpass Yes 횞3, save dialog
into the run folder). Recorded: frames acquired / tracked / written, results file grows **during** the run,
`Q_work`/`Q_res` high-water marks, slot ledger (**returned == taken**, no slot returned twice), LabVIEW handle
count before/after (flat 짹100), every TIFF counted and deleted.

**Phase F2 ??stop/restart.** `stop (end)` set `True` by `SetControlValue`; all three loops exit; **no error 1122**;
trace/results files closed and re-openable; restart 15 s; stop; close without saving; scratch copy deleted.

## 6. OPEN ??what this plan cannot decide, and does not pretend to

1. **`#10407` (autofocus) is in the kernel's forward slice.** Row 1.5 (ASI/focus) is D2, so D1 has no focus loop
   ??yet the autofocus case consumes the kernel's `Index of closest cal image slice, bead 2` and transacts VISA
   when it fires (`pre-rig-master-plan.md` A6). Leaving it on the ACQUISITION loop violates rule 1c (serial on the
   frame path); moving it to the TRACKING loop puts serial on the tracking path and is a D2 decision taken early.
   **This is a judgement call and the build does not take it**: the recipe places `#10407` with the rest of the
   forward slice on the TRACKING loop, records that it did, and flags it.
2. **`#11639` (the stop OR) is in the forward slice too** ??the same node both stop Booleans feed. D1 keeps a copy
   of the stop read on each loop via `exit_while`; whether the original's OR-of-three condition is reproduced
   per-loop or once-and-broadcast is recorded, not decided.
3. **`save N xyz traces.vi` #6384 after the loop** takes 7 inputs off `#637`'s output tunnels. If `save trace.vi`
   #376 moves to the WRITER loop, those tunnels move with it and #6384 must be re-fed from the writer loop's
   tunnels. The run measures whether it still receives what it needs; if not, the plan's answer is that the
   writer loop's per-frame streaming write is the D1 product and the `.tra` format preservation is a D2 item.


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-17
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.

Narrative relocated **verbatim** (rule 4): cycle 11??3 ??`archive/2026-09-16-status-cycles-11-13-narrative.md`;
D0 (15??8), the GPU numbers, the lock history and the long OPEN forms ??**`archive/2026-09-17-status-d0-and-gpu-narrative.md`** (STATUS was 268 lines). Open one only when a line here is ambiguous.
?좑툘 **ONE SESSION AT A TIME** (two ran concurrently on 2026-09-16) ??**re-read `CLAUDE.md` and this from disk**.

## START HERE

1. **`docs/pre-rig-master-plan.md` is THE plan** (`cycle10-plan.md` superseded = its Phase A); settled decisions
   **`docs/decisions.md`**; current cycle plan `docs/cycle14-plan.md`.
2. ??**Prior-art gate live, hole fixed** ??`guard_cycle.py` accepts `REFUTED:` and `FIXED: <slug> - <path>:<line> - <what>`.
3. ??**Retrospectives 10??3 done/disposed**; `retrospective.py` **v2** fixes slug saturation (`tools/bench/retro_v2_comparison.md`).
4. ??**Scripting EDITS are silently declined until the target's FRONT PANEL has been opened** (not "diagram loaded" ??refuted); fixed by `ensure_loaded()` in `tools/gscript.py`, 26 mutating wrappers.

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  owner:
  since:
  purpose:
# 2026-09-17 material/gpu-n1-localise: NO LabVIEW touched (DLL + recorded files only, ctypes; no COM anywhere in
# the import chain) - gates G0a/G0b assert tasklist shows no LabVIEW.exe at start and at end.
# Holder history (cycle15 D0 v1/v2/v3, md5s, scratch copies created+deleted, TIFFs written+deleted, GUI action
# counts): archive/2026-09-17-status-d0-and-gpu-narrative.md 짠1. Earlier: the 2026-09-16 narrative archive.
```
**Never assume an instance exited** (pid 14352 did not): `tasklist | grep -i labview`, kill strays. Fresh instances
??1,500 handles; unique scratch VI name per run, deleted in the same run.

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
**Stage 1 (analysis) CLOSED** ??the seven `docs/main-vi-*` / `instrument-libraries` / `frame-loop-wire-graph` /
`rotor-sign-diagnosis` files; raw `archive/benchmarks/INDEX.md` 22??1.
**Stage 2 (assembly) IN PROGRESS** (`docs/stage2-plan.md`): `Track_v6_CPU_core_v0.vi` 69/69 쨌 `??queue_v0.vi`
162/162. **Say it exactly:** bit-identical to the reference for the **first 10,018 frames only** (before the first
bead loss), and both are **replay** artefacts ??recorded TIFFs, `FOR` loops, no acquisition, no stop protocol.
**THE GAP (outcome review):** 168 op VIs, 116 recipes, 217 peer exchanges ??two replay VIs, **zero runnable
experimental VIs**.

## OPEN ??one line each; the long form is in the narrative archives

1. ?윞 **PERIODIC auto-reset not gated by `Auto-Reset` at the wire level** (`ForLoop#1359`, 10 terminals, 0 panel sources); one `Value` read inside #1359 closes it. ??2026-09-16 archive, OPEN 1.
2. ?윟 **Autofocus CLOSED** ??`Auto-Focus` uid 24266 stops the piezo; `CaseStructure #10407` every 25 frames ??3.6 Hz.
2c. ?윟 **uid 9775 READS camera geometry** (the size written is the panel display area, not the ROI) ??the 1280횞1024 budget basis is safe. Residual: `Property Items[] ??Is Write` over the 106 Property nodes.
3. ?윞 **Peer-archive dispositions** ??39 pre-09-15 `legacy`; **27 are real debt** (L6); L1: 64/336 docs lack frontmatter.
5. **Startup drives instruments** (ASI diagrams 10/88, PI 1/3/4/5 ??`main-vi-startup.md:22-33`): fine while apart, a hard blocker at assembly; excise node-by-node (rule 1a).
6??. ??RESOLVED ??bgrun regex, REVIEW-log scan skip, `premature-build`/`scope-creep` devices. 4. `Global motor pos.vi` write-only; **user: keep it**.
9. ?윟 **A2 DONE** ??owner semantics, six structure classes (54/54); `FlatSequence` the exception (owner uid 0, error 1055). `docs/diagram-hierarchy.md`.
10. ?윟 **A3 MEASURED for the 112 clean diagrams** (100 agree / 0 disagree); left: the 57 `FlatSequenceFrame` diagrams, reachable via `FlatSequence.Diagrams[]` **3578BC00**. ?윞 Needs ONE new op VI ??judgement call.
11??2. ??**Retrospective v2 ADOPTED** (A?밇 closed, `violations.py --due` empty rc=0); **doc lint + ingest BUILT**, but
   MEASURED 2026-09-17: **2 fail / 4 warn / 3 pass** ???뵶 L4 *two* `current` cycle plans (14 + 15) and L6 27 undisposed
   reviews; the "1 fail/3 warn/5 pass" figure is stale. ??archive 짠2.
13. ?윟 **Cycle 15 step 1(b)(c) MEASURED ??`docs/main-vi-stop-and-save.md`.** ?윞 Left: which `Diagram#639` sink of wire
   3457 is `WhileLoop#637`'s cond terminal ??**guessed twice ??build the READER** (recursive `ControlTerminal`
   census, then `WhileLoop.Loop End Ref` 0x06362C00). ??archive 짠2.
14. ?뵶 **The cycle-15 prior-art review is only PARTLY disposed** ??A1/A2 `settled-already`, A3?밃6/B2 `contradicted`,
   A7/B3 `unread-evidence` BLOCK on purpose (D1's method vs `decisions.md:19`; `SubVI.Replace` 635E001 unverified).
   **Only a judgement session may refute or fix those.** ??archive 짠2.
15. ??**`bgrun.py --detach` BUILT and MEASURED** (deadline + END/TIMEOUT survive detachment; `BGRUN KILL` line;
   detached stdout ??the log). 15b. ?뵶 **its deadline kill does NOT kill an ORPHANED grandchild**
   (`detach_canary.log`) ??pre-existing; the Job-Object fix is a **judgement call**. ??archive 짠3.
16. ?뵢 **GPU N1, full fixture: max |?x| 4.13e-06 px 쨌 |?y| 3.13e-05 px 쨌 |?z| 1.28e-05 쨉m 쨌 1 flip** vs acceptance
   `decisions.md:38` (x,y ??1e-6, 0 flips) ??**x/y and the flip are OUTSIDE it**. **LOCALISED 2026-09-17**
   (`docs/gpu-backend.md` 짠2026-09-17, raw `tools/bench/gpu_n1_deltas.json`, 8/8 gates): every x/y exceedance is
   **bead 4 on 10 frames of f11805?밼11823**, in the all-beads-lost tail, interleaving the 13 recorded lost rows;
   **over the first 10,018 frames max |?x| 4.86e-07 쨌 |?y| 4.68e-07 쨌 0 exceedances**; the flip is k1679/f1937
   bead 4, one cal slice (?z 4.7 nm); **two runs bit-identical**. ?뵶 **Acceptability is a JUDGEMENT call.**
17. ??**D0 CLOSED ??the original's full unattended cycle RAN, 16 pass / 0 fail** (`drive_original_copy_v3.py`,
   HWND-gated clickprobe, `SetControlValue` stop ??idle in 2 s, `tra001-000` written, md5 unchanged). ??archive 짠5.
17b. ?뵶 **v3's R11 never gated on the stop** ??`rec(..., left2, ...)` (`drive_original_copy_v3.py:415-418`) scores the
   *restart*, and `reset_controls()` runs only at line 248, so "stop works only in the frame loop" is **UNPROVEN**
   (peer `??026-09-17-d0v3-stop-heuristic.md`, ANSWERED, adopted). Next D0 step is its VI-Server-only test: stops
   `False` + readback ??restart ??one `True` each ??poll values + `ExecState`.
18. ?뵶 **The original saves EVERY FRAME as a 1.3 MB TIFF** (`IMAQ Write TIFF File 2` #22700, diagram 43) ??
   **~118 MB/s at 90 Hz**. Any unattended overnight harness must bound this or the disk fills in minutes.

## NEXT

?윟 **Slug block cleared** (`violations.py --due` empty, rc=0); the **OUTCOME REVIEW is RUN and disposed**
(`archive/peer/2026-09-16-outcome-review-20260916.md`, ANSWERED, **7 OUTCOME-VIOLATION slugs**).
?뵶 **JUDGEMENT NEEDED before the next recipe build:** CLAUDE.md turns that into a **delivery** cycle, contradicting
`docs/cycle14-plan.md` (짠3 `Diagrams[]` op, 짠4 A3 ??170/170, 짠5 OPEN 1's read, 짠6 A4). Queued second: **is item
16's GPU divergence acceptable**, on the 2026-09-17 localisation.

## Where to look

`CLAUDE.md` rules 쨌 **`docs/decisions.md`** settled 쨌 `docs/NAMES.md` strings 쨌 `docs/toolkit-capabilities.md` API 쨌
`docs/restructure-plan-4.6.md` target 쨌 `docs/pre-rig-master-plan.md` the plan 쨌 `docs/diagram-hierarchy.md` A2/A3 쨌
`docs/gpu-backend.md` GPU 쨌 narrative: the 2026-09-17 and 2026-09-16 status archives 쨌 `archive/` history (rule 4).


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Prior-art review complete — read-only, no lock taken, nothing built or run. **10 findings, zero `novel`.** The two that matter most are A1 and A4: the plan's central new operation is the one the project already tested a route *around* and recorded as unnecessary, and its provisional placement of `#10407` breaks a settled rule rather than an open question.

---

# PART A — THE DIRECTION

## A1 `settled-already` — "relocate existing nodes into the new loop" is the route this project already examined and set aside; the settled method is create-loop → drop → wire → delete

`docs/d1-build-plan.md:62` — *"the 13 existing nodes must be **REPARENTED** from Diagram 43 into the new body diagram"*; `:67-72` presents this as *"the one operation D1 needs that has never been exercised"*.

It was not only exercised in thought — a recipe was written for exactly this question, on exactly this VI, and it deliberately excluded the operation the plan now makes mandatory:

- `tools/recipes/probe_relocate_route.py:1-2` — *"step 0a of the delivery cycle: **can work be moved from one loop to another INSIDE ONE VI**, using only operations the fleet has already proven?"*
- `:10-15` — *"**WHAT IT DOES NOT TEST, deliberately.** `GObject.Move` with an `owner` input — relocating an existing node into another diagram — is NOT used… This probe therefore tests the route we would actually take: CREATE the destination loop, DROP the same subVI into it, WIRE across the border, DELETE the original. **If that works, relocation is unnecessary** and the method stands on primitives with a track record."*

That route then became the project's settled construction method, twice in `status: current` documents:

- `docs/decisions.md:19` — *"restructure **inside a COPY of the original**… **Method proven end to end** (`probe_migrate_v2` 3/3, `probe_migrate_v3` 5/5, `ExecState == 1`); **untested is SCALE and RUNTIME, not feasibility**."* STATUS names this file as *"Settled decisions that must not be re-opened"*.
- `docs/restructure-plan-4.6.md:79-81` — *"create a loop inside an existing VI · drop the same subVI in it · wire a control across the loop border · delete the original node · `ExecState == 1`, it compiles. **`GObject.Move` is not needed.**"*
- `docs/toolkit-capabilities.md:386-388` — the measured mechanics of that route: the loop body is just the new diagram index, `drop_subvi(..., body_index, ...)` places nodes **directly inside** it, and **`wire()` across a loop boundary AUTO-CREATES the tunnel**.

**Scope of this citation, stated precisely so it can be released.** The settled route covers a node that the fleet can *build fresh* inside the destination: a subVI call (`#376`, and the kernel itself, which `:42-43` already routes this way) and a primitive (`#8885`, `#2626`, `#6104`, `#9833`, `#10757`, `#10969`, `#11261`, `#11639`). It does **not** cover relocating a **Structure with its contents** — `#5540`, `#2222`, `#12589`, `#10407`, `#1359`, `#29874` — because building a Case structure's frames fresh is `OpCaseFrames_v0`, which `docs/pre-rig-master-plan.md:75` records as having *"**failed five times**"* and which the outcome review told us not to retry.

So A1 blocks the general claim at `:67-72` and blocks P2 (`#8885 Multiply`, a plain primitive — the settled route already covers it). It does **not** block P3.

## A2 `contradicted` — two current documents disagree about whether the loop split may be chosen before the per-frame measurement, and the plan cites neither

- **against**: `docs/decisions.md:46` — step 1 is *"measure the **unconditional per-frame path**, p50 **and p99**"*, marked *"not done"*; `:48` step 3 is *"split whichever measured owner **dominates**"*; `:52` — *"**Judgement returns at step 2, not before** — the split order depends on step 1's numbers."* `docs/pre-rig-master-plan.md:97` — *"**Ordering inside phase 1 comes from phase A5**, not from assumption"*, and A5 is *"not done"* (`:72`).
- **for**: `docs/cycle15-plan.md:28-30` — the user-approved D1 is rows 1.1 + 1.2 + 1.7 + 1.8 + 1.9, i.e. the writer loop is in D1 by approval.

The acquisition→tracking split is `decisions.md:47` step 2 and is sanctioned. The **third (WRITER) loop** is step 3/4 work placed before step 1's measurement. Both sides are `status: current`; the plan reconciles them nowhere.

## A3 `contradicted` — `#11639` is **not** the node both stop Booleans feed

`docs/d1-build-plan.md:50` — *"`#11639 Compound Arithmetic (**the stop OR**)"*; `:64` — *"`#11639` (**the OR node both stop Booleans feed**)"*.

`docs/main-vi-stop-and-save.md:46`, the file the plan cites as its stop source (`:28`):

| | `stop (end)` | `stop (end) 2` |
|---|---|---|
| its only wire sink | `CompoundArithmetic`**#11639** term 2 | `CompoundArithmetic`**#17883** term 1 |

Two different nodes, on the same diagram (`:49`). `#17883` appears nowhere in the plan, and `#17883`'s result (wire 15229) goes to `Tunnel#22085` of `CaseStructure#22082` (`:48`) — a fourth structure the assignment table at `:59-65` never places. The stop row `:64` is built on a false premise.

## A4 `settled-already` — putting `#10407` on the TRACKING loop is forbidden by a settled rule, not an open question

`docs/d1-build-plan.md:148-152` calls this *"a judgement call and the build does not take it"*, then takes it: *"the recipe places `#10407` with the rest of the forward slice on the TRACKING loop"*.

The rule already decided:

- `docs/decisions.md:30` — *"**no serial on the frame path** — CLAUDE.md rule 1c. The ASI/serial loop **owns its VISA session exclusively** and reaches the frame path only through a non-blocking handoff. **A mechanism that *can* stall the frame loop is disqualified even if it usually does not.**"*
- `docs/pre-rig-master-plan.md:91` (row 1.5) — same, acceptance *"no serial on the frame path"*.
- `archive/prose/2026-09-17-d1-d2-explained-r2.md:53` — the D2 description the user approved: *"ASI 초점 루프 — VISA 세션을 **독점** 소유… 수용: **프레임 루프에 VISA 호출 0**."*

A VISA stall in the tracking loop fills `Q_work`, and `:96` then makes acquisition *"skip this read"* — i.e. frames lost to motor communication, the exact outcome rule 1c exists to forbid. "Record it and flag it" is not available for a settled prohibition; the buildable options are: leave `#10407` where it is until D2, or cut it out of D1 with its removal shown node-level in the build log (`pre-rig-master-plan.md:58`).

## A5 `contradicted` — the WRITER loop as specified reproduces the original's save-at-the-end, which is what row 1.7 exists to replace, and the plan's own F1 gate asks for the opposite

`docs/d1-build-plan.md:63` gives the writer loop exactly *"`#376 save trace.vi` and its three shift registers (`total data array`, `file number to append`, `file progress`)"* — the accumulator. `:139` then requires *"results file **grows during** the run"*.

- `archive/prose/2026-09-17-d1-d2-explained-r2.md:86` describes the original: *"실행 중에는 파일이 없고, 중간에 죽으면 데이터도 없다"* — the file only exists after `#6384` runs at `:114`'s *"저장 루프는… 원본처럼 끝에 한 번 저장하지 않고 **실행 중 계속** 파일에 쓴다"*.
- `docs/pre-rig-master-plan.md:93` (row 1.7) — acceptance *"**every computed result written, in order**"*.

Relocating the accumulator does not produce a streaming write. `:157-160` (OPEN 3) notices the `#6384` side of this and defers the `.tra` format to D2, but never reconciles `:63` with `:139`.

## A6 `unread-evidence` — the documented route for relocating a *connected fragment*, researched twice and written into our own skill reference, is uncited, and it answers P3 directly

`docs/d1-build-plan.md:68-69` — *"Nothing in `docs/toolkit-capabilities.md` records a move **INTO an arbitrary diagram**, and nothing records moving a **Structure with its contents**."* Three files on disk speak to exactly this:

- `.claude/skills/labview-automation/references/vi-scripting.md:323-325` — *"For a **wired fragment** rather than one object, the equivalents are `TopLevelDiagram.Make Selection` → `Copy Selection` → destination `AbstractDiagram.Paste(position)` (**paste onto the actual subdiagram reference, not the top level**), or `Move Selected Objects`."*
- `archive/peer/2026-09-13-scripted-diagram-selection.md:143` — *"A recent NI forum example confirms that copying a selection and pasting into a diagram in another VI works, **including contents of a structure frame**"* (with URL). That is P3's question, already answered for the copy/paste route. `:166-172` gives the exact chain and IDs (`Make Selection` `0x6349002`, `Copy Selection` `0x6349003`, `AbstractDiagram.Paste` `0x6375400`, verify with `Selection List[]` `0x6349400`).
- `archive/peer/2026-08-28-copy-nodes-between-vis.md:55` — *"copying them one at a time **is not equivalent** to copying the selected code fragment: wires and relationships need to be part of the same operation"*; `:86` — *"Pasting to the top-level diagram when the intended destination is a case frame creates a 'floating' object rather than an object owned by that frame"*, i.e. the `AbstractDiagram` owner requirement the plan's `OpMoveIn_v0` is rediscovering.

And the same exchange denies the plan's stated premise at `:67-68`: `archive/peer/2026-09-13-scripted-diagram-selection.md:162` — *"`GObject.Move` (`0x632A400`) is **not** a cross-VI reparenting method. It changes the position of an object within its existing owner."* Our own `tools/gscript.py:2469-2472` (`move_out` moves a node to the VI's top-level diagram) contradicts that as written for the within-VI case. Both sides are in our files and neither is cited; whichever is right, the plan is building on an unreconciled pair.

Also uncited and directly on point: `tools/recipes/probe_relocate_route.py` (A1), which is not in the `§0` "what already exists" table at `:25-37`.

---

# PART B — THE ARTIFACT

## B1 `already-built` — a probe for "can work move from one loop to another inside one VI" exists and has been run

`docs/d1-build-plan.md:74-78` proposes `tools/recipes/probe_move_into_v0.py`. `tools/recipes/probe_relocate_route.py` is that probe, with its own prediction contract (`:17-25`) and a recorded run: `tools/bench/probe_relocate_route.log:21` — *"5 pass, 2 fail"*, both failures documented at `probe_relocate_route.py:27-36` as **defects in the probe, not the toolkit**, and superseded by `probe_migrate_v2`/`v3` (3/3, 5/5).

**Scope:** this covers the *question* Phase P asks and the probe harness/scratch-copy pattern. It does **not** cover `OpMoveIn_v0` itself, which does not exist anywhere in `tools/gscript.py` (`move_out` `:2469`, `move_object` `:2094`, `move_by_label` `:1364`, `copy_by_index` `:1290-1338` — none takes a destination-diagram owner).

## B2 `already-failed` — addressing objects by Traverse index across a sequence of mutations

`docs/d1-build-plan.md:76-77` builds `OpMoveIn_v0` with *"its `owner` taken from `Diagram`[**index**]"*, and `move_out`'s signature is index-based throughout (`tools/gscript.py:2469` — `move_out(target, diagram_index, node_index, position)`). Thirteen moves, each adding and removing diagrams and nodes, all keyed on indices.

- `archive/peer/2026-09-15-opwiresource-fail5-traverse-index-order-mismatch.md:26` — *"There is no documented ordering contract for `Traverse for GObjects.vi`"*; `:29` — *"**Do not assume a cached index remains stable across executions, reloads, edits, or sessions.** If index selection remains anywhere, retain the **UID identity gate** on every read."*
- `tools/gscript.py:833-836` — *"**Use this, NOT position matching**, to identify what a mutating Op just created… which is exactly how a wrong object gets reported as the result of a successful build."*
- `tools/prior_art_review.py:6` records this as the project's canonical repeat: *"step 0a derived a Traverse index by hand THREE times"*.

The plan never says how a node's index is re-resolved after each move. The recorded remedy (`new_since` / uid gating, the `fidx(uid, cls)` pattern in `tools/recipes/build_track_v6_queue.py:45`) is not named.

## B3 `already-measured` — Phase N1's kernel-harness branch was measured on 2026-09-17, twice, bit-identically

`docs/d1-build-plan.md:133-136` — *"or… through the kernel harness — the run says which it used) against the CPU reference: **first 10,018 frames** within `decisions.md:38`"*.

`docs/gpu-backend.md:371` — *"**2026-09-17 MEASURED** — WHERE the full-fixture GPU/CPU divergence lives"*; `:400` — for **k < 10018**: max |Δx| **4.857e-07 px**, max |Δy| **4.677e-07 px**, |Δz| 1.279e-05 µm, **0 exceedances**; `:377` records the run reproducing the earlier one exactly. STATUS OPEN 16 carries the same numbers and adds *"two runs bit-identical"*.

What is **not** measured and stays novel: the same comparison through **D1's own tracking+writer path** (`:133`), i.e. the in-situ run. If the recipe takes the harness branch it re-runs a settled measurement; if it takes the in-VI branch it is new.

## B4 `unread-evidence` — gate S4 has no reader, and STATUS records building that reader as the mandated next step

`docs/d1-build-plan.md:130` — *"S4 **every loop's conditional terminal is driven by a Boolean read inside it**"*, stated as a read-back gate.

- `docs/main-vi-stop-and-save.md:58-59` — *"**no reader for the While loop's conditional terminal exists in this toolkit**"*; `:164-165` lists it under "What this file does NOT establish", naming `WhileLoop.Loop End Ref` **0x06362C00**; `:72-74` — *"Both are new ops and are NOT built in this cycle."*
- `STATUS.md` OPEN 13 — *"which `Diagram#639` sink of wire 3457 is `WhileLoop#637`'s cond terminal — **guessed twice → build the READER**"*, which is CLAUDE.md's own trigger rule.

For the two new loops `exit_while` writes the terminal and `ExecState` is the evidence (`toolkit-capabilities.md:31`, 5/5); for `#637`, the loop S2 keeps as the acquisition loop, S4 is currently unmeasurable and would be a third guess.

---

## Where I found NO prior art

- **Moving a Structure with its contents inside one VI (P3), by `GObject.Move` with an owner** — never attempted here. `docs/toolkit-capabilities.md:362-368` records a positional `move_object` into a For Loop's area, and `:390-392` **retracts** the conclusion drawn from it (*"The earlier probe blamed `move_object` for breaking the VI. It did not"*), so nothing on disk says either way. This is the genuinely open half of A1.
- **Three loops inside a copy of the original, wired through the six-queue core** — no record of any attempt at that scale; `decisions.md:19` calls scale *"untested"*, which is a statement that it has not been done.
- **The §4 frame-accounting reconciliation gate** (`:111-113`, buffer-number series as a strictly increasing subsequence) — no equivalent gate exists in `tools/bench/` or `archive/benchmarks/INDEX.md`.
- **A live 20 s run of a restructured copy** — `drive_original_copy_v3.py` drove the **unmodified** copy only.

---

```
PRIOR-ART: settled-already    (A1 — tools/recipes/probe_relocate_route.py:10-15; docs/decisions.md:19; docs/restructure-plan-4.6.md:79-81; docs/toolkit-capabilities.md:386-388 — covers plain nodes and subVI calls, NOT structures with contents)
PRIOR-ART: contradicted       (A2 — docs/decisions.md:46,:48,:52 and docs/pre-rig-master-plan.md:97,:72 vs docs/cycle15-plan.md:28-30)
PRIOR-ART: contradicted       (A3 — d1-build-plan.md:50,:64 "the node both stop Booleans feed" vs docs/main-vi-stop-and-save.md:46,:48 — #11639 and #17883 are two nodes)
PRIOR-ART: settled-already    (A4 — d1-build-plan.md:152 places #10407 on the TRACKING loop vs docs/decisions.md:30, docs/pre-rig-master-plan.md:91, archive/prose/2026-09-17-d1-d2-explained-r2.md:53)
PRIOR-ART: contradicted       (A5 — d1-build-plan.md:63 reparents the accumulator vs :139 "grows during the run", docs/pre-rig-master-plan.md:93, archive/prose/2026-09-17-d1-d2-explained-r2.md:86,:114)
PRIOR-ART: unread-evidence    (A6 — .claude/skills/labview-automation/references/vi-scripting.md:323-325; archive/peer/2026-09-13-scripted-diagram-selection.md:143,:162,:166-172; archive/peer/2026-08-28-copy-nodes-between-vis.md:55,:86)
PRIOR-ART: already-built      (B1 — tools/recipes/probe_relocate_route.py:1-25 + tools/bench/probe_relocate_route.log:21 — the probe, not OpMoveIn_v0)
PRIOR-ART: already-failed     (B2 — archive/peer/2026-09-15-opwiresource-fail5-traverse-index-order-mismatch.md:29; tools/gscript.py:833-836; tools/prior_art_review.py:6)
PRIOR-ART: already-measured   (B3 — docs/gpu-backend.md:371,:400 — the kernel-harness branch of Phase N1 only)
PRIOR-ART: unread-evidence    (B4 — docs/main-vi-stop-and-save.md:58-59,:72-74,:164-165; STATUS.md OPEN 13)
```

One note for whoever disposes of this: `archive/peer/2026-09-16-priorart-priorart-cycle15-d1.md:374-385` is still only partly released, and STATUS OPEN 14 says only a judgement session may touch its A1–A7/B2/B3 lines. A4/A6 above are new and independent of those; A1 supersedes the earlier A1 (the hot-path-swap objection is genuinely fixed by `docs/cycle15-plan.md:22-30`) and replaces it with an objection to the *method*, not the scope.

## Sources

(extract from answer)

## What was done with it

**All ten findings accepted. `docs/d1-build-plan.md` was rewritten as REV 2 before any build ran** (material
session, cycle 15 "D1 build", 2026-09-17 ~03:5x). Nothing was refuted: every citation opened, and every one of
them said what the review said it said. The two that changed the cycle's direction are A1+A6 (the relocation
route is settled for plain nodes and subVI calls, so D1's only real unknown is **structures with contents**, and
the documented route for those is `Make Selection`/`Copy Selection`/`AbstractDiagram.Paste`, which our own skill
reference has carried since 2026-09-13 and which has never been run) and A4 (`#10407` on the tracking loop is
forbidden by `decisions.md:30`, not merely uncertain — it became OPEN 1 and the build does not touch it).

Per finding, where it landed:

| finding | what changed |
|---|---|
| A1 | §1 now splits the forward slice into *settled* (subVI + primitive, create→drop→wire→delete) and *open* (six structures); `probe_relocate_route.py` added to §0 |
| A2 | OPEN 2 — the conflict is recorded; `cycle15-plan.md` (user-approved, newer) is taken as governing, which is stated rather than assumed |
| A3 | §2 row 1.9 now names **both** `#11639` and `#17883`, and `CaseStructure#22082` / `Tunnel#22085` |
| A4 | OPEN 1 — neither placement of `#10407` is legal; the judgement session decides; Phase P does not touch it |
| A5 | §2 row 1.7 is a **streaming per-frame write**, not the relocated accumulator |
| A6 | §0 and §1 cite `vi-scripting.md:323-325` and both peer archives, including the `GObject.Move` cross-VI/within-VI contradiction, and Phase P is reframed as *measure the cheap route first, with a control* |
| B1 | the new probe cites `probe_relocate_route.py` as prior art and keeps only the part it does not cover |
| B2 | §1 adds the UID-addressing / index-re-resolution rule with its citation |
| B3 | Phase N1 no longer re-runs the harness branch; only the in-VI comparison is claimed as new |
| B4 | S4 is **not claimed for `#637`** — no reader exists; `ExecState` evidences the two new loops only |

**The artefact these findings produced**, written after the table above and reviewed against it line by line:
`tools/recipes/probe_move_into_v0.py` REV 2 — its docstring opens by citing `probe_relocate_route.py:10-15`
(B1), states that the settled route covers primitives and subVI calls and that only structures-with-contents are
open (A1), names the `Make Selection`/`Copy Selection`/`AbstractDiagram.Paste` chain with its IDs as the
alternative and the reason it is not tried first (A6), makes `#8885` an explicit CONTROL arm whose failure
invalidates the run, and re-resolves every Traverse index from a UID before each mutation (B2). It does not
touch `#10407` (A4) and builds no writer (A5).

FIXED: settled-already - docs/d1-build-plan.md:56 - the forward slice is split into the settled route (subVI/primitive) and the one genuinely open case (structures with contents), with the settled route cited.
FIXED: contradicted - docs/d1-build-plan.md:92 - row 1.9 now names both stop nodes (#11639 and #17883) and CaseStructure#22082, and the writer row 1.7 is a streaming write instead of the relocated accumulator.
FIXED: unread-evidence - docs/d1-build-plan.md:40 - the Make Selection/Copy Selection/AbstractDiagram.Paste route and the GObject.Move cross-VI contradiction are cited, and S4 is no longer claimed for #637.
FIXED: already-built - docs/d1-build-plan.md:39 - probe_relocate_route.py and its log are listed as prior art and the new probe keeps only the part they do not cover.
FIXED: already-failed - docs/d1-build-plan.md:81 - every object is addressed by UID and every Traverse index is re-resolved after each mutation, citing the fail5 exchange.
FIXED: already-measured - docs/d1-build-plan.md:141 - Phase N1 records the harness numbers as already measured and claims only the in-VI comparison as new.
