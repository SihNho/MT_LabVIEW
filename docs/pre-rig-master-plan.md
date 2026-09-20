---
type: plan
status: current
date: 2026-09-16
tags: [master-plan, pre-rig, parallelisation, seven-loop, dry-run]
---

# Master plan — BUILD THE MAIN VI AND RUN IT, without the rig

**Rewritten 2026-09-16** after the user rejected the first version's framing, and after two peer reviews
(`archive/peer/2026-09-16-master-plan-attack.md`, `…-priorart-master-plan.md`) found most of its measurement items
already done. The user's reframing is the plan:

> *"내 생각에는 결국에 main vi 만들어서 가동 해보기는 해야함 (리그 없는 상태에서도 가동은 가능할 듯). 아마
> bead tracking은 안될테니 tracking renewal은 계속 들어가겠지 [심지어 LED 전원 꺼놓은 상태]… 그렇다고는 할지라도
> 루프는 계속 돌테니 모터 가동, 카메라 acquisition 등 정상 가동 자체는 확인 가능할듯."*

And the scope it sets:

> *"남은 진짜 부분은 루프 병렬화 및 정상 작동 여부로 보임. 1) 정상적으로 프레임 문제를 해결하는지 2) 정상 가동
> 하는지 (모터 움직임 및 읽기)."*

## What changed, and why it is better than either reviewer's version

The first plan asked *"what can we measure before the rig comes back?"* and the answer was: mostly things already
measured. The user's question is different — *"does the parallel version actually run?"* — and it can only be
answered by **building the thing and starting it.** This is also exactly what the outcome review demanded on
2026-09-15: *"the next problem is not missing tooling; it is failure to cross the boundary from replay proof to
experiment product."*

**Bead tracking will fail with no sample, and that is the expected condition, not a defect.** Codex attacked the
old plan's live test on precisely this ground — blank images drive the tracker straight into bead-loss/reseed. The
user's answer settles it: yes, and the loops keep running anyway, so motor motion, motor reading, camera
acquisition and frame accounting are all observable. **The failing half is the half we already proved on the
fixture.**

🔴 **The "free reseed stress test" was a CONTRADICTION and is withdrawn (rev4 A6).** This section claimed that with
no beads `tracking renewal` fires continuously and gives the fault injection for free — while §2C, written after
the user's decision, says the reseed term is `Auto-Reset AND (min(pos) < 0)` and that **`Auto-Reset` OFF means no
reseed fires at all**. Both cannot be true of the same batch. What is true: **the no-bead condition makes reseed
available for free, but only in a batch that turns `Auto-Reset` ON.** The first batches keep it OFF on purpose, so
they test the loops *without* reseed; the stress test is the second batch, and it costs nothing extra there
because the empty stage still supplies the fault. Do not schedule the two claims into the same run.

**Bead-tracking correctness is NOT re-opened here.** The user's own recorded data (`.cal`, `.tra`, `.tiff`)
already settles it, and the fixture run confirms it numerically for the first 10,018 frames.

---

## Phase 0 — make a run observable and repeatable  *(no LabVIEW execution)*

| # | work | detail |
|---|---|---|
| **0.1** | **Batch directory convention** — `G:\Data\Sihyeong-Developing\<YYYY-MM-DD>-<batch>\` (the user's directory; created empty 2026-09-16 12:48). One subdirectory per batch, nothing written anywhere else | the user's instruction |
| **0.2** | **What every run records — the list already exists; use it, do not re-specify it.** `stage2-plan.md:83-88` holds the **adopted** live-instrumentation minimum (requested/returned buffer numbers; gap count and size; overwrite/error count; acquisition-call duration count/p99.9/max; acquisition→dequeue and acquisition→kernel-done latency p99.9/max; `Q_img` high-water mark, enqueue timeouts, dropped frames, longest full interval; acquired/copied/enqueued/dequeued/processed/returned counts; slot-invariant violations; `Q_res` high-water mark) **with its acceptance**: zero gaps, zero drops, zero slot violations, processed = acquired. This plan adds only what that list predates — **the stop reason, the motor command/readback pairs, the reseed counter, and the full front-panel control snapshot** | a run whose settings are not recorded is not a measurement; a list that exists twice drifts |
| **0.3** | 🔴 **Fix the acceptance metric before using it.** `Images Missed = 0` is **not sufficient** under `Buffer Number Mode = Last`: `Last` re-returns the same buffer when we are faster than the camera, and `Images Missed` does not count that. Both reviewers flagged it independently, and `camera-acquisition-facts.md:79-81` already says so. The authoritative trace is **`Buffer Number Out`**, from which gaps AND duplicates are derived | the old plan's criterion was wrong |
| **0.4** | ✅ **Camera contract — DECIDED (see below): 90 Hz, `ExposureTime` ≈ 5 556 µs (half the 11.111 ms period), `ExposureAuto` OFF**, 1280×1024, offsets 0, never write `BinningHorizontal`. 🟡 **RESCOPED 2026-09-16 — the tool exists (`tools/bench/camera_contract.py`) and the write works, but a Python pre-pass CANNOT set the run's condition.** Measured in three sessions: as found `ExposureAuto = Continuous` / 1909 µs → written to `Off` / 5555 µs and read back inside the session → **a new session reads `Continuous` / 1909 µs again.** `IMAQdxOpenCamera` resets exposure exactly as it resets the ROI (`camera-acquisition-facts.md`, "exposure resets on session open too"). **So the contract moves into Phase 1.1**: the acquisition loop writes `ExposureAuto = Off` and `ExposureTime` right after `IMAQdx Open Camera`, then reads both back into the batch record. `camera_contract.py` stays as the pre-flight reader and the after-the-fact verifier (`--batch <dir>` writes before/after JSON). Measured range `ExposureTime` **10 – 11053 µs**, so half-period is legal | the dim-field hazard is removed by the operating condition — but only by the process that owns the session |
| **0.5** | 🟢 **NOT A BLOCKER WHILE THE RIG IS APART — rule 1b was rewritten 2026-09-16.** Hardware permission now follows the **rig state**, and the ASI piezo is explicitly *not* a special case: disassembled ⇒ motors, ASI and camera are all allowed. So the dry run may execute the original's startup **as it is**, which is what makes "build it and start it" reachable this window. What follows stays worth having for two reasons — it becomes a hard requirement the moment the rig is **assembled** (camera only), and a run whose side effects are unknown is not a measurement. **Startup's instrument sites, measured:** `main-vi-startup.md:33`: **startup diagram 10 calls `ASI TG-1000.lvlib:Initialize.vi` (uid 43997) then `Move Axis to Position.vi` (uid 44036)**, opening COM4 (alias **`ASI_Piezo`**) and moving an axis; **the same pair recurs on diagram 88**, and diagram 12 reads the position back (uid 44196). `t0-instrumentation-plan.md:136-138` concluded from this that running the main VI *"never runs unattended"* — written under the old rule, and **superseded for the disassembled state**: the run is still supervised in the ordinary sense, but the ASI motion is no longer a reason it cannot happen. **What the disarm list becomes:** a list to *record* now (which sites the run touched) and to *excise* the moment the rig is assembled — the ASI init/move pair on diagrams 10 and 88, the position read on 12. When that excision happens it must be shown node-level, by uid, in the build log, because `main-vi-startup.md:47` notes the outer startup ordering is itself a rule-1a fact and removing part of it is a deliberate deviation, not a silent edit. This is also where A6's finding lands: the autofocus case fires **every 25 frames (≈3.6 Hz at 90 Hz)**, so the same axis is driven again throughout the run unless the control `Fix to a Certain Pattern` (uid 10230) is TRUE. **And the ASI is not the whole list** (rev4 A1, citations opened): startup diagram 1 is **PI motor init** driven from `Set Focus (0->50)`, diagram 3 is **PI `MOV`** (absolute), diagram 4 is **PI `GOH`** (go home) and diagram 5 is **`VEL` + a position query** (`main-vi-startup.md:22-28`). ⚠️ **The rotor adds a physical hazard of its own:** the controller counter was deliberately left at **0**, so the original's Baseline-200 convention makes its **first absolute move a 200-turn trip** — `PIC 100000` first, or run only the new VI (`rotor-sign-diagnosis.md:124-127`). So the list of things a start-up touches is: **ASI init + axis move (diagrams 10, 88) · ASI position read (12) · PI init (1) · PI `MOV` (3) · PI `GOH` (4) · `VEL` + query (5) · the rotor's baseline** — and the run's log must *record* each one, because the difference between "the loops ran" and "the loops ran while the stage was homing" is the difference between a measurement and a story. Disarming becomes mandatory at assembly, not now | rule 1b (2026-09-16): permission is the rig's state, not the instrument's identity. Disassembled ⇒ all of this is allowed |

| **0.6** | **GPU clock lock — the script ALREADY EXISTS; this item is "run it and verify", not "write it"** (rev4 B1: `tools/gpu/register_gpu_clock_lock.ps1` registers the logon task; `tools/gpu/regime_test.py` / `regime_test_lock.py` are the duty-cycle pstate check, rev4 B2). Register `nvidia-smi -lgc 1365,1905` with highest privileges (it resets at reboot) and verify the pstate **under the real 90 Hz duty cycle**, not in a tight loop. `-lmc` is unsupported on this RTX 2060, so upload stays ~3× slower than tight-loop and the 1.14 ms figure is not the number to plan against (`gpu-backend.md:225-241`) | a measured ms/frame at 90 Hz replaces the tight-loop figure before 1.2 is accepted |

## Phase A — FINISH THE MAP FIRST  *(LabVIEW read-only + offline; the user's standing instruction)*

Nothing in phase 1 is ordered correctly without this, and hardware measurement before it measures the wrong things.

| # | work | needs |
|---|---|---|
| **A1** | ✅ **DONE 2026-09-16** — built and run as **`OpOwnerChain_v1`**: **20/20 gates pass**, and gate **B6 is FUNCTIONAL on the main VI**, read-only (`tools/bench/build_opownerchain_v1.log`; `docs/toolkit-capabilities.md:49` records `10407 → Diagram#639`, `1359 → Diagram#639`, `639 → WhileLoop#637`). *was: "**`OpOwnerChain_v0`** — the missing link is **structure → the diagram it sits on**, NOT node → owner (that already works; `which_loop_owns_motor.log` prints the blocker 18 times). The recipe exists, corrected, **never run**"* — **corrected 2026-09-16**, resolving `archive/ingest/2026-09-16-ingest-2026-09-16.md` PAIR 1 (line 89) and PAIR 7 (line 118): this row was the stale side | LabVIEW RO |
| **A2** | ✅ **DONE 2026-09-16** — owner semantics validated for **all six** structure classes: **54/54 gates pass / 0 fail** (`tools/bench/diag_owner_semantics.log`), with **`FlatSequence` the one exception** (owner uid 0, error 1055). Recorded in `docs/diagram-hierarchy.md`. *was: "**Validate owner semantics per structure class** before any walk. The measured fact (`NAMES.md:864-866`) is scoped to `CaseStructure` — 1 of **6** classes (3 WhileLoop, 17 ForLoop, 37 CaseStructure, 21 FlatSequence, 4 Sequence, 2 EventStructure). FlatSequence gets a round-trip check against `diagram_tree_main.json`"* — **corrected 2026-09-16**, resolving `archive/ingest/2026-09-16-ingest-2026-09-16.md` PAIR 1 (line 88) | A1 |
| **A3** | 🟡 **PARTLY DONE (cycle 13)** — **112 of 170 diagrams resolved** (100 agree / 0 disagree; `tools/bench/diagram_tree_a3.json`). What is left is exactly the **57 `FlatSequenceFrame`** diagrams, and they **are** reachable: the **`FlatSequence.Diagrams[]`** property, short-name **3578BC00**, was **measured attaching** in cycle 13 (`tools/bench/diag_flatseq_diagrams_attach.py`, END rc=0, 5/0). Walking it needs one new op VI — cycle 14 §3. *was: "**Complete the 170-diagram hierarchy** — the 41 unresolved plus every FlatSequence link, replacing position matching (the diagram was Clean-Up'd, so position means nothing)"* — **updated 2026-09-16** | A2 |
| **A4** | **The frame loop's TRUE membership** — body **and nested frames**. The body-only list already exists (`frame-loop-anatomy.md:40-55`); only the nested delta is new | A3 |
| **A5** | **The unconditional per-frame path** — what executes every iteration vs. conditionally. **This decides phase 1's loop-split order** | A4 |
| **A6** | ✅ **DONE 2026-09-16, offline, from dumps we already had.** The criterion is `AND( (frame index mod N) == 0 , NOT(x) )` on `CaseStructure #10407`, acting on the kernel's `Index of closest cal image slice, bead 2` against `# slices in stack`; it **does** transact serial when it fires. Full derivation and wire-level citations: `camera-acquisition-facts.md`, "MEASURED 2026-09-16 (master plan A6)". **The switch is `Auto-Focus` (uid 24266)** — corrected the same hour after the user pointed at the panel. Wire 3362 is the control `Fix to a Certain Pattern` (uid 10230), but **code writes that control every iteration** (Property Node #1469 ← `NOT( Auto-Focus AND NOT(reseed-And) AND (counter < Limit of Auto-Focus) )`), so setting it by hand is overwritten. Turning **`Auto-Focus` OFF** is what stops the piezo. **N is 25**, from the control **`Frame rate`** (`frame-loop-wire-graph.md:120` names the implicit link; `main-vi-panel-map.md:83` gives the value) — so the case fires **every 25 frames ≈ 3.6 times per second at 90 Hz**, each firing running `Move Axis Relative` plus a position read. ⚠️ Both of these had been recorded on 2026-09-14 and were re-measured this session; wire 3362 is likewise already at `main-vi-panel-map.md:311`. **A6 required no new measurement at all** | ✅ complete — it was already in our files |
| **A7** | **Three audits over A4's membership, not one** (widened 2026-09-16, rev5 A6 — the plan had only the first): **(a) every VISA/serial call site**, rule 1c's list, which phase 1 must empty out of the frame loop; **(b) the REENTRANCY audit**, which `t0-instrumentation-plan.md:65-70` calls *"the highest-value check in the whole plan"* — for every VI called from more than one While loop, read `Execution:Reentrancy Type` (VI property **288**, already in `docs/vi-server-ids.json`) and flag every non-reentrant one, because a shared non-reentrant subVI is **an accidental mutex**: the second caller blocks until the first returns, and if the first is inside a serial round trip the frame loop stops for exactly that long. ⚠️ **We already have one confirmed instance and had not connected it** — `main-vi-panel-map.md:558` records `ASI_adjust focus-subvi.vi` as *non-reentrant by design* and called from **both** the frame loop (43) and the display loop (99); **(c) the UI-thread census** — count the property-node `Value` accesses on the per-frame path and note which share a loop with the display, since `motion-path-audit.md:122-126` makes UI-thread serialisation, not CPU work, the leading explanation for "one loop carries too much" | A4, A6 |
| **A8** | ⚠️ **Census A — Case #10445 frames. RE-SCOPE BEFORE ATTEMPTING.** The obvious route is `OpCaseFrames_v0`, which **failed five times** and is CLAUDE.md's own example of breaking the "failure budget = 2" rule (`CLAUDE.md:212`), and the outcome review told us not to retry it. So: either read #10445 by a route that already works (A1's owner chain walked downward, or the existing wire-graph JSON), or **drop A8** and collapse the reseed `Or` conservatively. Do **not** rebuild the failed op | A1 |
| **A9** | 🟢 **ANSWERED 2026-09-16, MEASURED — and the answer is good news for this plan.** Raised at rev4 A5 and rev5 A9; scheduled and closed the same afternoon. **uid 9775 READS the camera `Height`/`Width`; it does not write them** — both wires (32937, 32938) have uid 9775 itself as their source, so both terminals are outputs (`tools/bench/diag_9775_direction.log`, 37 s, main VI md5 unchanged). **So a copy of the original does not set the acquisition geometry at start-up, and this plan's 1280×1024 budget basis is safe from this node.** The follow-on, from dumps already on disk with no LabVIEW run: **diagram 97 does write a size, and it is the front-panel display's** — panel `Height`/`Width` read back (uids 30445/30471) → bundle (30512) → **÷ 2** (constant uid 27664) → written into **`Image Area Size`** (30118) and **`Draw Area Size`** (30422). That is the rig owner's own recollection confirmed (*"카메라 프레임 읽어오기 → IMAQ 화면 사이즈 셋팅"*), and it explains why no ROI test ever saw it. Full derivation: `camera-acquisition-facts.md`, "MEASURED 2026-09-16 — uid 9775 READS the geometry". ⚠️ **Do not widen this.** The peer review (`archive/peer/2026-09-16-uid9775-read-not-write-codex.md`) confirms the narrow claim and explicitly refuses the wide one: *"'the VI does not set frame size' is not established by this evidence"* — another node could still write ROI. **Residual, and cheap when it is wanted:** the reviewer's own test, `Property Items[] → Is Write` per item across the VI's 106 Property nodes, which needs no wire walking. Also unmeasured on purpose: that the sink terminals of 32937/32938 are the same panel objects diagram 97 reads back | ✅ done — offline + one 37 s read |
| **A10** | **How a bead-free run gets INITIALISED** — raised at rev4 A7, again at rev5 A10, still unwritten. The plan answers only what happens when tracking *fails*; it never says what the loops are *started* with. The inputs are known and need naming per batch, not discovering: the kernel takes `Array of cal clusters`, `Real-space cosine window`, `Cosine bandpass for Hilbert` (`stage2-plan.md:21-23`), all built at startup from `cal image array` (`main-vi-startup.md:29-30`), and the gate is the wired control `Done Picking \nBeads?`, **uid 11819** (`main-vi-panel-map.md:359`). **Decide and record in writing: which `.cal` file a dry-run batch loads, and what satisfies the picking gate with no beads on the stage.** If the gate is never satisfied the loops never reach steady state and the whole dry run measures the wrong thing — this is a *precondition* of Phase 2, not a finding of it | offline (docs + existing dumps) |

## Phase 1 — build the runnable seven-loop main VI on the **GPU** path, in a COPY of the original

Rule 1 unchanged: the original is never touched. The in-copy migration method is **proven end to end**
(`probe_migrate_v2` 3/3, `probe_migrate_v3` 5/5, `ExecState == 1`); untested is SCALE and RUNTIME, which is what
this phase tests.

| # | loop | acceptance at this phase |
|---|---|---|
| **1.1** | **Acquisition** — `IMAQdx Get Image`, `Buffer Number Mode = Last`; no free slot ⇒ skip the read, never gate the camera; carry the buffer number with the slot. **The handoff is already designed and measured — cite it, do not re-decide it:** `frame-ownership-design.md:23-39` chose the **pre-allocated image pool + slot index** over enqueueing pixels (unbounded) or buffer numbers (re-introduces the ring-wrap race); the pool's one copy per frame is **0.12 ms**, and **ring depth absorbs jitter only — 10/50/100 buffers all failed at the same delay**, so start at **20 slots** and treat growth as a symptom, not a fix. The pool authority is a bounded **`Q_free`** with the invariant **free + queued + processing = 8** asserted in the test (`stage2-plan.md:64-67`). **And the lifecycle, not just the pool** (rev5 A4 — `frame-ownership-design.md:41-64` was the design for this loop and was uncited): the slot states are FREE → FILLING → OWNED, **two queues not one** (a `free` queue of indices and a `work` queue of filled ones, so the pool size is enforced by construction), and the invariant that actually breaks builds is **"every exit path returns the slot exactly once — normal completion, kernel error, enqueue timeout, shutdown, file-writer error"**; a slot leaked on an error path starves acquisition, one returned twice hands the same memory to two owners. `:60` is a hard constraint on 1.2 specifically — **a GPU raw pixel pointer must not outlive slot ownership and must not survive a pool reallocation**, *"the exact shape of the bug that cost the GPU v2 work a day"*. **Plus the camera contract, which lives here and nowhere else** (moved from 0.4 on measurement): write `ExposureAuto = Off` and `ExposureTime ≈ 5 556 µs` right after `IMAQdx Open Camera`, then read both back into the batch record — a session open resets them to `Continuous` / 1909 µs, so no external pre-pass can do it. ⚠️ **"Right after `IMAQdx Open Camera`" is NOT on this loop's diagram** (rev4 A5 → rev5 A9, raised twice unrefuted, answered here): in a copy of the original the session is opened in the **startup frame, diagram 87** (`stage2-plan.md:17`: `IMAQdx Open Camera` → `Configure Grab`), so the contract write belongs on **diagram 87 immediately after the open**, and the acquisition loop only re-reads it. Diagram 87 also carries A9's unresolved node — see Phase A9 | the VI compiles and the loop iterates; **the read-back in the batch record shows `Off` / ~5 555 µs**, otherwise the run was not at the decided condition; **and the slot ledger closes**: returned = taken, no slot returned twice |
| **1.2** | **Tracking — the GPU path** (user's decision 3): dequeue → **GPU kernel via our own DLL interface** (single call per frame, raw image in; designed fresh, not copied from the Saleh-lab donor) → frame-identified result. The CPU queue core's 162/162 fixture result is the **reference**, not the thing being shipped here | compiles; runs; result carries its buffer number; **x/y ≤ 1e-6 px and z ≈ 1e-4 µm against the CPU kernel**, and the tolerance is quoted with the two things it is a property of (rev3 B1 → rev4 B3 → rev5 B3, asked three times, fixed here): **the frame set is `INDEX.md:36` row 15 — 200 chained frames, 5 beads**, not the 10,043-frame fixture; and **`INDEX.md:41` row 20 — the 1e-6 px figure is a property of a MACHINE, not of the DLL** (cuFFT guarantees bitwise reproducibility only for a fixed GPU model), so it is re-run on any new box with `N=200 py tools/gpu/test_mt2.py`. Extending the comparison to all 10,043 fixture frames is a separate, cheap run and is not assumed here |
| **1.3** | **Scheduler** — cycle state machine. ⚠️ **TRANSPORT IS AN OPEN DECISION, and this row no longer pretends otherwise (corrected twice: rev5 A7, then rev5 B1 + a re-read of the cited line on 2026-09-16).** Two corrections to what this row said an hour ago. **(i) The attribution was wrong.** The previous text released the queue design by claiming locals are "the user's decision" and citing `rotor-scheduler-design.md:75`. That line was opened: `:72-73` records the user's point — *the motor loop has been parallel to acquisition since `4.4_MotorParallelLoop`, so serial cost never touches the frame budget* — and `:74-75` ("Local variables carry the targets…") is **that document's own reasoning, not a user decision**. So "a peer correction does not overrule a user decision" was applied to something the user never decided, and the 2026-09-12 peer correction (`restructure-plan-4.6.md:59-63`: four non-atomic writes let the motor loop read **a new speed with an old force**) stands on its merits. **(ii) The replacement was not buildable.** "One cluster local" was proposed without checking the fleet: a cluster local needs a typed cluster terminal exactly as a cluster queue element does, `docs/toolkit-capabilities.md:32` and `:46-49` have **no Bundle/Unbundle writer** — only readers — and `stage2-plan.md:96-103` already decided against composite elements for v0 for precisely this reason ("neither exists without a donor"). The shipped core proves the alternative works: `stage2-assembly-step-c.md:21-26`, six lock-stepped queues. **So the requirement is fixed and the transport is not:** the motor loop must never act on a half-updated target set; the two buildable routes are **(a)** lock-stepped publication consumed as a set — all four fields written by one producer in one iteration and read as a set before any of them is acted on, the proven pattern — or **(b)** a real donor cluster typedef created once as an explicit build item, after which a single cluster local or queue element becomes legal. **Pick before loop 3 is built, not now, and record the pick here**; do not build 1.3 against the sentence that happens to be in front of you | compiles; emits a command trace; **the motor never reads a half-updated target set** — the acceptance is the invariant, not the mechanism |
| **1.4** | **Motor** — reading and control out of the frame loop. ⚠️ **WITHDRAWN 2026-09-16 (rev5 A8), and it was against a standing user instruction:** an hour earlier this row said the new VI's rotor calls must be repointed to `SetCommand_signed.vi`. `rotor-sign-diagnosis.md:145-147` says the opposite in the same breath as the user's own words — *"configuration은 그대로 쓰면 되는데 왜 자꾸 바꾸려고 하는거야?"* — and `rotor-scheduler-design.md:143-148` spells out the rule: **the schedule's rotor row calls `SetCommand.vi` exactly as the existing `Send to Rot` path does**, same `Baseline Startpoint`, same `Ring`, only the commanded value coming from the schedule. Copying the working call is correct by construction and is what rule 1a requires. The signed variant stays a *separate*, hardware-verified artefact, not something this phase adopts. **What DOES belong here:** the rotor counter is at **0**, so nothing may assume the Baseline-200 coordinate (`rotor-sign-diagnosis.md:124-127`). ✅ **DECIDED by the user 2026-09-16 — `SetCommand_signed.vi`, following the hardware number with its sign** (*"로터는 본래 부호 인식이 가능했으나 랩뷰 시리얼 통신에서 부호 인식이 안되는 문제가 있었음. 이제는 해결 방법을 찾은 것 같으니 부호를 포함하여 하드웨어 숫자 그대로 따라가야함."*). The "unsigned `SetCommand.vi` unchanged" text below is superseded; the sign round-trip on the real serial link is still a disassembled-state measurement.** (was: ⚠️ OPEN (user) — `SetCommand.vi` or `SetCommand_signed.vi` in the new VI? NOT resolved here; it is rig knowledge, not a document fault.) This row says the new VI calls the original unsigned `SetCommand.vi` unchanged; `docs/questions-for-user-2026-09-14.md:35-38` records the user's 2026-09-14 decision to use the signed copy in the new VI, hardware-verified 2026-09-13 20:22/20:28. Both cannot hold. Raised by `archive/ingest/2026-09-16-ingest-2026-09-16.md` PAIR 4 (lines 103–105); **only the user decides which**, and 1.4 must not be built until they do | compiles; issues and reads back; the rotor row's call is byte-for-byte the existing path with only the value substituted |
| **1.5** | **ASI / focus** — **exclusively owns the VISA session**; reaches the frame path only through a non-blocking handoff (rule 1c). Gated to every N frames rather than every frame | no serial on the frame path |
| **1.6** | **Display / UI** — 10–20 Hz gate + `Defer Panel Updates`; **Image Display, not Picture — measured, not preferred** (`INDEX.md:43, :46`: Image Display +1.0/+6.9 ms vs Picture +2.9/+8.0) | panel updates do not enter the frame budget |
| **1.7** | **File writer** — consumes the results queue, lossless FIFO. Queue mechanics are already specified (`restructure-plan-4.6.md:65-68`: timeout −1 and the error-1122 shutdown path; `:147-167` the boundary manifest; `:161-162` latch-action controls) and the seam is checked with the existing `tools/bench/boundary_manifest.py`, not a new script | every computed result written, in order; the manifest shows no state carrier crossing the seam |
| **1.8** | **Frame accounting** — reuse `get buff image-lost frames.vi` (uid 6810), the original's own camera-buffer bookkeeping and *"the frame source"* (`frame-loop-anatomy.md:47`), rather than writing a counter. Decide **reuse or replace in writing**: it is a subVI on the frame loop's body, so keeping it also keeps its per-call cost | the `Buffer Number Out` trace and this VI's numbers agree, or the disagreement is explained |
| **1.9** | 🔴 **STOP AND SHUTDOWN — the one build item Phase 1 had no row for** (rev5 B2). `STATUS.md` says both shipped artefacts are *"replay artefacts … no stop protocol"*; a seven-loop VI that cannot be stopped cleanly is not an experiment product. Nothing here needs inventing — **the rule, the trap and the wiring primitive all exist**: stop conditions are evaluated **INSIDE** each loop, because a front-panel Boolean wired in from the top level becomes an input tunnel read **once** before the loop runs (NI's infinite-loop mistake, `stage2-plan.md:90-94`); the primitive is `OpExitWhile_v0` / `exit_while(target, stop_control, body_diagram, node_index, output_names, node_class)`, verified 5/5, ExecState 0 → 1 (`toolkit-capabilities.md:31`). **Seven loops need seven stops and one order**: `frame-ownership-design.md:68-72` — every enqueue takes a finite timeout and handles `timed out` (a bounded queue's default is −1, *wait forever*), and releasing a queue while another node waits on it raises **error 1122**, so shutdown is always **stop the users → drain → release**. ⚠️ **And the normal stop is still Abort**, which `frame-ownership-design.md:92-97` says bypasses diagram cleanup entirely — so the next start must concretely clean stale named queues, undisposed IMAQ images, an open camera session, partial file refnums, VISA sessions and an outstanding GPU DLL call. The plan already leans on Abort at `:132-134`; this row is what makes that safe | every loop stops from a Boolean read **inside** it; the VI stops with no error 1122 and no orphaned queue/image/session; an Abort followed by a fresh start runs clean |

**Ordering inside phase 1 comes from phase A5**, not from assumption. Two of the numbers already exist: motor
reading costs **2.56 ms** (`motion-path-audit.md:84-99`) and the autofocus wrapper is **called** every iteration
but **transacts only when its case fires** — its unconditional diagram is five nodes (two UI-thread `Value` reads),
with the fixed `Wait` and both VISA calls inside the case (`camera-acquisition-facts.md`, "the ASI wrapper's
unconditional diagram"; corrected there against the older "Wait + VISA every frame" reading of
`frame-loop-anatomy.md:68`). A6 measured **when** it fires: on a frame-index schedule, not rarely. Those are the frame
loop's known offenders — against the **10 ms** budget at 90 Hz (the 11.111 ms period minus the ~1 ms of jitter
margin measured in `camera-acquisition-facts.md:53`; see "The budget this sets is 10 ms" below), motor reading
alone is **26 %** of it.

**✅ The GPU interface is ALREADY BUILT, callable from LabVIEW, and benchmarked** — checked after the third
prior-art review flagged that the plan treated it as unknown risk (`gpu-backend.md:245-251`, INDEX rows 15/36/37).
`HARNESS_gpu2`, script-built: `IMAQ Create → ReadFile → GetImagePixelPtr → one CLFN `mt2_track_simple``, DBL in/out,
**no image copies**. 200 chained frames, 5 beads:

| path | ms/frame above base |
|---|---|
| sequential (the original) | 8.15 |
| CPU-parallel v3 | 2.43 |
| GPU, Saleh-lab donor node | 5.14 |
| **GPU, our own interface** | **1.14** |

Outputs match the reference at **x,y 4.9e-7 px, z 2.9e-6 µm, 0 flips, 0 good-flag mismatches** — inside the agreed
tolerance already. Everything fixed (calibration, windows, twiddles, buffers) lives on the GPU from `mt2_open`, so
per-frame traffic is one image upload, one kernel launch and 3×nb doubles back.

**So decision 3 is cheaper than it looked**: phase 1's tracking loop wraps an interface that already exists and
already meets tolerance. But two corrections from rev3, both opened and both holding:

🔴 **1.14 ms is a TIGHT-LOOP number, and 90 Hz is the duty cycle measured to destroy it** (`gpu-backend.md:225-241`).
Any idle gap ≥ 2 ms drops the RTX 2060 to **P8** (SM 360 MHz, memory 405 MHz) and every phase slows **~3.5×**; at
90 Hz the GPU is idle ~9 ms of every 11.111 ms, which is that regime exactly. The measured fix is the SM clock lock
**`nvidia-smi -lgc 1365,1905`** (admin; resets at reboot, so it is registered as a logon task) — and even then
`-lmc` is unsupported on this card, so upload stays ~3× slower than tight-loop. **Phase 0 gains one item: register
the clock lock and verify the pstate under the real duty cycle. Phase 1.2 gains a timing acceptance: measured
ms/frame at 90 Hz with the lock in place, not the tight-loop figure.** Also do not `cudaHostRegister` LabVIEW's
IMAQ buffer (`gpu-backend.md:345-349`) — relevant the moment acquisition hands pooled image refnums to this loop.

✅ **The stop path is already built** (`gpu-backend.md:332-343`, `tools/gpu/test_abort.py`) — it exists precisely
because the experiment VI is normally stopped with LabVIEW's Abort button. So "unproven inside a live loop" is now
only about the *acquisition handoff*, not about stop or error handling.

🔴 **And GPU-first changes the acceptance ladder** (rev3 A5). `restructure-plan-4.6.md:201-210` assigns
**bit-identity** to stages 0–5 and a tolerance only to stage 6, on the assumption that the CPU build ships first.
With the GPU top level built first, the shipped path is a tolerance path from stage 2 onward, and bit-identity has
no replacement named. **What replaces it:** the CPU queue core stays the reference — every GPU stage is accepted
as **x/y ≤ 1e-6 px and z ≤ 1e-4 µm against the CPU build on the same fixture frames**, and the *CPU* build, when
it follows, is still accepted bit-identically. Neither number is new; what was missing was saying which one applies
to which artefact.

## Phase 2 — the two questions that matter  *(dry run, no rig)*

> **The specification is `restructure-plan-4.6.md:201-216`, not this section.** That file's stage list already
> carries these live-stage criteria with more content (deadline misses, buffer-number gaps, p99.9 and max of the
> acquisition-call latency, per-core CPU, UI-thread time, display age, the minutes-long back-pressure test and the
> thermal/disk soak). The two tables below are **this batch's checklist**, deliberately shorter — when they differ,
> the restructure plan wins. Every run also records what 0.2 lists.

### 2A. Does it solve the frame problem correctly?

| check | criterion |
|---|---|
| frame accounting | every `Buffer Number Out` accounted for: continuous, or a gap that is explicitly counted. **Duplicates counted separately, not as successes** |
| the camera is never gated | acquisition rate is independent of how slow the consumer is made. Deliberately slow tracking and verify the camera's own cadence does not move |
| identity | pixels and buffer number change together; a result labelled N was computed from frame N's pixels. **The user's stated corruption test** |
| no loss from serial | the frame loop transacts no VISA (rule 1c), verified by instrumenting the boundary, not by reading the diagram |
| back-pressure | slow the writer and the disk for minutes; the acquisition side must degrade by skipping reads, never by blocking |
| **slot invariants** | added 2026-09-16 (rev5 A4 — 2A had no ownership check at all). **`free + queued + processing = pool size` asserted continuously** (`stage2-plan.md:64-67` asserts it at 8; 1.1 starts the pool at 20), **slot-invariant violations = 0**, and **every exit path returned its slot exactly once** (`frame-ownership-design.md:41-64`) — including the error paths, which is where a leak actually comes from. A pool that silently shrinks looks exactly like "the camera got slower" |
| **no leak over the run** | `Q_img` / `Q_res` **high-water marks** recorded and flat, not merely "no crash"; process handle count flat against the ~31,500 baseline; pipeline counts reconcile — **acquired = copied = enqueued = dequeued = processed = returned**, the full set `stage2-plan.md:83-88` adopted (0.2) rather than the shorter list this plan once carried |

### 2B. Does it run normally — motor motion and reading?

| check | criterion |
|---|---|
| motor moves | a schedule's translation commands are issued and the stage reaches the commanded positions |
| motor reads | readback matches command within the driver's tolerance; per-call cost matches the measured 2.56 ms |
| command equivalence | an existing 3-row schedule produces **identical translation commands and timings** to the original VI (restructure §5 stage 3) |
| rotor | absolute degrees, translation-then-rotation ordering; the counter is at **0**, not the old 100 000 baseline. ⚠️ **This does not weaken the row above**, which rev5 A8 read as a tension: that row's subject is the **translation** axis (PI), this one's is the **rotor** — two different controllers, so "identical translation commands" and "no absolute move assumes Baseline 200" can both hold. The rotor's own equivalence is 1.4's: the call is byte-for-byte the existing `Send to Rot` path with only the commanded value substituted |
| the loops survive | run for hours; no leak, no deadlock, no queue growth, handle count flat. **Not "with reseed firing continuously"** — the first batches hold `Auto-Reset` OFF, so no reseed fires at all (see 2C) |

### 2C. What the no-bead condition gives free — and the control settings it FORCES us to choose

With no beads `tracking renewal` **would** fire continuously, so the empty stage supplies for free the fault
injection codex said we would otherwise have to build: reseed event counts, the reset counter, the state fed into
the next kernel call, and reseed arriving while acquisition has skipped buffers. ⚠️ **But only in a batch that
turns `Auto-Reset` ON** — the decision below holds it OFF for the first batches, and with it off the reseed term
is false every iteration. The free stress test is real and it is the *second* batch, not this one.

🔴 **But "run for hours with reseed firing" is not achievable at default settings, and the plan said it was.**
Found by the third prior-art review and verified in the diagram census (`stage2-assembly-step-e.md:66`,
`GLOSSARY.md:48-54`): the lost-bead reseed has **three runtime controls**, not one.

| control | effect in a no-bead dry run |
|---|---|
| **`Auto-Reset`** (uid 17472) | **gates the reseed entirely** — *"it fires only while the user has Auto-Reset on"*. OFF ⇒ no reseed at all, and the loops simply run with garbage tracking output |
| **`Limit of Program`** (uid 9654) | the **cap on auto-resets per run**. `Equal?` against `# of Auto-Reset` — **equality, not ≥** — and on reaching it the run **stops and saves**. With no beads every frame is a loss, so the cap is reached almost immediately and **the program terminates itself** |
| **`Reset Tracking`** (uid 5605) | manual reseed, OR'd on top |

### ✅ DECIDED by the user, 2026-09-16: **`Auto-Reset` OFF**

> *"오토리셋 끄고 봐야할듯."*

The dry runs turn the lost-bead reseed **off**: that term is `Auto-Reset AND (min(pos in cal image out) < 0)`
(`stage2-assembly-step-e.md:66`), so with the control off the AND is false and the *bead-loss* arm cannot fire.
Questions 2A and 2B are then read without reseed noise on top of them — the right first experiment.

🔴 **CORRECTED 2026-09-16 (rev3 A3, citation opened and it holds): there is a SECOND arm, and `Auto-Reset` does
not gate it.** `stage2-assembly-step-e.md:36-38` records a **periodic** auto-reset term — `# of Auto-Reset`.Value
#9879, `Quotient & Remainder` #10068, `Equal?` #10019, Not/And — and `:66` scopes the `Auto-Reset` control (#9806)
to *"the lost-bead reseed"* only. `GLOSSARY.md:55` gives the period from an in-VI comment: **"~27 mins/100000"**.
The 10,043-frame fixture is ≈1.9 minutes, which is why *"it never fired on this recording"* — absence there is a
sampling artefact, not evidence.

So the earlier claim — *"`# of Auto-Reset` never increments and `Limit of Program` never trips"* — **was wrong for
a long run**, which is exactly what 2B asks for ("run for hours"). On present evidence an hours-long dry run
accumulates periodic auto-resets and can hit `Limit of Program`'s exact-equality stop-and-save on its own.

**MEASURED 2026-09-16 (`tools/bench/diag_reset_arm.log`, `OpWireSource_v5`, MAIN md5 unchanged) — and it does not
settle the question, it localises it.** The four wires the argument turns on:

| wire | source | sinks |
|---|---|---|
| **10187** the periodic modulo's remainder | `Function` #10068 (the Q&R) | **`LoopTunnel` #10177** — it *leaves* the frame loop |
| **10103** the period itself (the divisor) | **`LoopTunnel` #10114** — it *enters* from outside | #10068 |
| 9868 the reseed `And`'s other input | `Comparison` #10950 | `And` #9647, whose other input is the `Auto-Reset` control |
| 3457 the `# of Auto-Reset == Limit of Program` chain | `CompoundArithmetic` #11639 | two `Diagram`-owned terminals (panel objects) |

So the **lost-bead** arm is gated by `Auto-Reset` inside the loop (#9647), while the **periodic** arm's period comes
in through a tunnel and its remainder goes back out through another — the decision is assembled **outside diagram
43**, where the node-level dumps do not reach. That is exactly the structure→home-diagram link A1 is for. Until it
is walked, "the periodic arm is ungated" and "it is gated somewhere outside" are both live, so the plan may not
assert either. It does answer `stage2-assembly-step-e.md:75-76`'s *"remainder 10187 → (sink to find)"* as far as
the loop border: **LoopTunnel #10177**.

**What follows, and none of it is optional:**
1. **Record `Limit of Program`'s value in every batch** and treat a run that ends by itself as a *result*, not a
   crash — the stop reason is already in 0.2's record list.
2. **The first long run is instrumented for it**: `# of Auto-Reset` is logged per frame, so the period is measured
   rather than taken from a comment.
3. **This is what A8 was for.** The plan offered to "drop A8" (the #10445 census) while asserting the claim that
   census would test. Either the periodic arm's gating is read from the machine, or the claim is not made.

**What this deliberately does NOT test, recorded so it is not mistaken for coverage:**

| not exercised | where it goes |
|---|---|
| the reseed path itself, reset counters, state handed to the next kernel call | a later batch with `Auto-Reset` ON and `Limit of Program` raised |
| **`Limit of Program`'s stop-and-save**, including its exact-equality trigger | a later, deliberately short batch at the normal limit — it is reachable in seconds, so it costs nothing when we want it |
| `Reset Tracking`, the manual OR | operator-driven; test alongside the above |

### Why reseeding drops frames — ⚠️ WE DO NOT KNOW. The explanation below was built on a superseded census.

> *"이전 경험상 reseeding이 적용되면 프레임 드랍이 다소 생기는 것 같던데, 이유가 있는지."*

🔴 **RETRACTED 2026-09-16 (rev3 A4, citations opened, and it is right).** The account given here was: the reset
frame of Case #5540 holds *"one Property Node reading `Value`"* (`keystone-op-spec.md:596-600`), so a reseeding
iteration pays an extra UI-thread round trip. **Our own later census contradicts it.** CENSUS B
(`stage2-assembly-step-e.md:128-138`) measured both frames of #5540 and found **both are pure pass-throughs with
nothing computed in either**; the reseed values arrive from *outside* the loop through `FlatSequenceInnerTunnel`
2886 / 5818 — they are *"literally the loop's INITIALISERS"* (`:140-148`). If the frame computes nothing, there is
no extra UI-thread cost on a reseed iteration, and this explanation has no mechanism left.

**So the honest answer to the user's question is: not yet known.** What survives is the *shape* of the failure if
any extra cost does appear — the budget is 10 ms of an 11.111 ms period (`camera-acquisition-facts.md:53`) and the
failure is a cliff, not a slope (`:60-66`), so one slow iteration costs whole frames rather than a percentage.
What is missing is the cause, and it is **one measurement**: a reseed iteration's duration against a non-reseed
one, which the `Auto-Reset` ON batch produces. Do not re-state the retracted mechanism in a later document.

**The design consequence stands on its own** and was already the plan: carry the initialisers on a wire into
`ReseedMux.vi` rather than through a Property Node (`stage2-assembly-step-e.md:143-148`). It costs nothing and
changes no computation; it simply no longer needs a frame-drop story to justify it.

⚠️ **One thing to verify in the run rather than assume.** With no beads and no reseed, `Bead is good?` stays false
for every bead. If anything downstream is gated on bead validity — `save trace.vi` #376 writing records, the WLC
fit, the result enqueue — those paths may sit idle, and "the file writer loop ran" would be a false positive. So
the run's record must show **what each loop actually did**, not merely that it iterated: rows written, results
enqueued and dequeued, bytes on disk. If the writer turns out to be starved, inject synthetic results rather than
turning `Auto-Reset` back on, so 2A and 2B stay clean.

## Already measured — CITE, do not redo

Both reviews found the first plan re-proposing settled work. These are closed:

| item | where |
|---|---|
| `Last` vs `Next` on the real camera (74.9 vs 123.0 Hz) — **measured, not calculated** | `camera-acquisition-facts.md:64-72`, INDEX row 40 |
| motor read cost **2.56 ms** | `motion-path-audit.md:84-99, :108-114` |
| camera ceiling, exposure, headroom at 150 Hz | `camera-acquisition-facts.md:35-42` |
| rotor negative-angle hardware verification (`PIC -10` → −7.2°) | INDEX row 31 — **done with the user watching** |
| `OpCaseFrames_v0` | **already failed**; do not retry (CLAUDE.md "failure budget = 2") |
| the frame loop's six body subVIs | `frame-loop-anatomy.md:40-55` |

**The autofocus question is closed** — see A6 above; the derivation lives in `camera-acquisition-facts.md`
("MEASURED 2026-09-16 (master plan A6)") and is not repeated here.

## Genuinely deferred to reassembly

Only real experimental conditions with beads **and** the motor moving:

- bead tracking accuracy under load, and force/extension measurement;
- reseed triggered by a real bead physically coming unstuck;
- the supervised pilot the user runs to accept the whole thing.

Everything else in this plan runs dry.

## DECIDED by the user, 2026-09-16 — the three open questions are closed

### 1. Camera: 90 Hz, exposure = half the period, fixed

> *"카메라 노출은 90 Hz 조건으로 절반만큼은 노출, 나머지 절반은 대기."*

| parameter | value |
|---|---|
| frame rate | **90 Hz** — the rig's configured condition (`imaqdx_limits.py --restore`: 1280×1024, offsets 0, **90.0009 Hz**) |
| period | **11.111 ms** |
| `ExposureTime` | **≈ 5 556 µs** — half the period |
| idle | the remaining ≈ 5 556 µs |
| `ExposureAuto` | **OFF.** Fixed exposure is the point of the decision |

**This dissolves the sharpest objection either review raised.** Codex's strongest attack was that
`ExposureAuto = Continuous` (max 15 000 µs, enough to cap the camera near 66 Hz) makes a dark rig change the
achievable rate, so a dry run would "measure" that the target is unreachable and blame the software. With exposure
fixed at half the period there is no auto-exposure loop to react to a dark field — the objection is removed by the
operating condition rather than argued with. Record the frozen contract in every batch directory anyway.

**The budget this sets is 10 ms, not 11.111 ms.** Corrected after the third prior-art review: the measured table in
`camera-acquisition-facts.md:53` gives, for **90.00 Hz / 11.11 ms period**, a **budget (zero frames lost) of
10 ms**, first failing at a 12 ms delay. *"The budget is the frame period minus about 1 ms, and ~1 ms of that margin
is jitter rather than fixed cost."* Using the period as the budget — as the first draft did — spends a margin that
was measured to be necessary. **Dry-run acceptance is judged against 10 ms**; the 6.00 ms / 150 Hz figures in older
documents stay as the stretch condition and are not what these runs test.

Exposure does not consume this budget: the camera exposes on its own clock and the PC's 10 ms is what it has
between deliveries.

### 2. The MAP comes first — and it was already the user's standing instruction

> *"지도 작성이 우선되는게 맞음. 내 지시였음."*

The previous version of this plan argued hardware-first ("the motor window closes at reassembly"). That was wrong,
it contradicted a standing instruction, and codex had attacked it independently: starting hardware work before the
map is finished buys measurements of the wrong things. **Track A ordering is restored**: finish the diagram
hierarchy and the frame loop's true membership before hardware characterisation, and before phase 1 fixes the
split order. The hardware window is real but it is not a licence to measure blind.

### 3. The GPU top level is built FIRST and is the default

> *"tracking은 기본적으로 GPU 기준으로 최상위 vi 작성할 것. [이후 CPU 병렬 vi도 추후 작성 필요하기는 함]"*

Phase 1 builds the seven-loop top level around the **GPU** tracking path. The CPU-parallel top level is a later,
additional deliverable — both still ship as **two separate top-level VIs**, never one VI with a runtime switch.
This inverts how the work had been queued: `Track_v6_CPU_*` existed, so the top level was implicitly going to be
assembled around the CPU core with the GPU kernel "swapped in at stage 6". Loop 1.2 below is therefore the **GPU**
tracking loop, and its numeric acceptance is the agreed GPU tolerance (x/y ≤ 1e-6 px, z ≈ 1e-4 µm against the CPU
kernel on the recorded fixture) — not a final-stage afterthought.

**Consequence to check early, not late:** `docs/gpu-backend.md` and `docs/gpu-portability.md` describe the GPU
path, and `memory: design-gpu-interface-fresh-not-saleh` records that our DLL interface is designed from scratch
(single call per frame, raw image in). Whether that interface is actually built and callable is now on the
critical path, where it used to be at the end.
