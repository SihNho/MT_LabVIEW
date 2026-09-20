---
type: narrative
status: historical
date: 2026-09-15
tags: [archive, stage2]
---

# STATUS history — Stage-2 assembly cycles 1-7 (overnight 2026-09-14/15)

Moved out of STATUS.md on 2026-09-15 under rule 4 (STATUS stays one screen; narrative lives here).
Current state, open items and the next action are in STATUS.md; measured facts are in docs/ and
archive/benchmarks/INDEX.md rows 37-43; every peer exchange is in archive/peer/.

## STAGE 2 STARTED 20:4x (user: "재구성이 중요하겠는데 이거 진행하도록") — plan [docs/stage2-plan.md](docs/stage2-plan.md), reviewed

Decisions recorded: display 10 Hz default, runtime control, never at the cost of a frame (else an external viewer);
camera-settings panel at configuration = later option. **Toolkit for stage 2 — COMPLETE 22:1x (INDEX rows 32–36, all
functional):** While loop with tunnels by control name (`while_loop`), stop by control (`exit_while`), four queue nodes
(`queue_node`), empty runnable VI (`EMPTY_v0.vi`), **loops inside loops** (`loop_in('for'|'while', …)` with inputs from
a node's outputs; a top-level control wired through two borders makes one tunnel per border). Composite elements
avoided (two lock-stepped queues per direction, plan item 8).

### Assembly cycle 1 (session 6959fd57, from 22:2x) — step A: shift registers are a MISSING primitive, now being built

The build order's step 4 ("the kernel with 3 shift registers") had **no primitive behind it**: `while_loop`/`loop_in`
make input tunnels, `exit_while` makes output tunnels, `OpShiftRegs_v0/v1` only READ. Rows 32–36's claim that every
stage-2 primitive exists is wrong by this one item. Plan: [docs/stage2-assembly-step-a.md](docs/stage2-assembly-step-a.md).

- **Peer review REFUSED the first route and was right** (`archive/peer/2026-09-14-stage2-shiftreg-primitive.md`): the
  plan wanted to abuse erdosmiller `Exit While Loop.vi`'s never-exercised `Shift Registers` input, while LabVIEW's
  documented **`Loop.Add Shift Register` 6361000** sat already catalogued at `docs/NAMES.md:234`, unverified. Also
  adopted: `Terminal.Connect Wire` = invoke on the SINK, `Wire Source` = source; the three-depth-1-queue fallback is
  DEMOTED (no atomic tuple alignment, and a −1-timeout dequeue deadlocks with no recoverable state).
- **DONE, 9/9 PASS (run 3, `tools/bench/build_opaddshiftreg_v0_run3.log`, INDEX row 37): `OpAddShiftReg_v0` /
  `gscript.add_shift_reg()`.** `6361000` is **public** (attaches through the ordinary builder) and a **Loop-class
  Invoke accepts a WhileLoop reference** by inheritance. Functional on a real scripted While loop: `shift_reg_uids`
  [] → [503], `RightShiftRegister` 503 + `LeftShiftRegister` 509, **both sides unwired** (target ExecState 0 — correct
  until wired). Donor md5 unchanged, no junk, op saved.
- Two failed predictions on the way, both peer-reviewed before any repair, both my own recipe defects (neither a
  LabVIEW limit): (1) an `ExecState` gate placed before the required `Y Position` was wired, which cannot discriminate
  — the wire-UID equality on the two terminal ends can, and showed the branch had landed all along; (2) `g._lv = None`
  executed *after* a phase had cached op-VI proxies, re-Dispatching the Application underneath them → `0x800706BA`
  mid-batch. Recipe now: wire-UID gates, terminals addressed by **index + direction** (this node carries `Y Position`
  and `Add Shift Register` twice each), `g._lv = None` once at the top, `com_preflight()` (two spaced round-trips
  agreeing on an unchanged pid), and the panel closed on every exit path.
- **State right now: nothing running, nothing open dirty. LabVIEW pid 4232 (fresh, 22:36), handles ~30.6 k
  (baseline ~31.5 k).** No original or vendor VI touched; no hardware.

### Overnight cycle 2 (23:0x) — A3: the four `OpWireSR_*_v0` wiring ops. BUILT, test pending

- Plan [docs/stage2-assembly-step-a3.md](docs/stage2-assembly-step-a3.md), peer-reviewed
  (`archive/peer/2026-09-14-stage2-a3-wire-shiftreg-plan.md`: viable; adopted — verify the body-node choice by far-end
  wire UID, isolate the string-negative test with a wire-UID snapshot around Remove Bad Wires).
- **All four ops built and SAVED, ExecState 1** (`tools/bench/build_opwiresr_v0.log`): `LeftIn`, `RightIn`,
  `LeftOutNode`, `LeftOutCtl`; labels `tools/bench/opwiresr_labels.json`. **`Loop.Diagram` 6361401 on the WhileLoop
  seed is verified usable** (compiles, feeds `AbstractDiagram.Nodes[]`). Donor untouched.
- **Functional test failed twice at the same `drop_subvi` — CAUSE FOUND 23:2x, my path error:** `IMAQ Copy` is in
  `Management.llb`, not `Basics.llb` (already recorded in an older recipe header; now in NAMES.md "Vision LLB member
  locations"). The untitled modal was `OpSubVI_v1`'s automatic-error-handling dialog (error 7), which also opens the
  op's BD. My first hypothesis (watchdog false positive) was WRONG — the raw window rows logged by
  `tools/bench/test_opwiresr.py` showed a real untitled enabled window with every VI window blocked. The
  `lv_gui` hardening (a VI's own FP/BD is never a dismissible candidate) stays: it is correct regardless.
  Path fixed in the recipe; review `wiresr-test-fail2-imaqcopy-llb-path` dispatched (gate), then rerun the test.
- **QUOTA WARNING seen 23:09 in the Claude app: "주간 사용량 한도 초과 임박 — 9월 21일 (월) 07:00 재설정".** If a limit
  error arrives: STATUS resume point → scheduled task at 2026-09-21 07:02 → rerun the interrupted batch from the start.

- **A3 FUNCTIONAL, 23:18 (INDEX row 38): T1–T7 PASS** — a script-created register wired on all three sides compiles
  (ExecState 0→1) and the VI runs; every register terminal carries the far end's wire UID. **Every primitive the
  stage-2 skeleton needs now exists** (rows 32–38). Two open items under review (`wiresr-test-t8b-…`): T8b
  mis-predicted (an UNTYPED register takes the type of the first wire — the string wire was legal, nothing to remove;
  the sub-test is to be dropped, LeftOutCtl is proven by T7) and an untitled modal at 23:18:37 attributed to
  `OpFPLabels_v0`'s automatic error handling (its BD/FP windows are open) → fix = auto error handling OFF on
  `OpFPLabels_v0` and `OpSubVI_v1` (save authority: fleet ops), after the review.

- Fixes applied 23:2x: `OpSubVI_v1` automatic error handling OFF (saved, counts unchanged); `gscript.wire_sr()`
  wrapper added. `OpFPLabels_v0` deliberately NOT changed (`fp_labels` uses its error dialog as the loop terminator).

### Overnight cycle 3 (23:3x) — step B: the replay core `Track_v6_CPU_core_v0.vi` — PLANNED, under review

Plan [docs/stage2-assembly-step-b.md](docs/stage2-assembly-step-b.md): one While loop, `IMAQ ReadFile` of
`Frame Paths[i]` (auto-indexed) → `PARALLEL_kernel_v3clean` with the 3 feedback registers → `XYZ` 2-D indicator via
an auto-indexed output tunnel; acceptance = bit-identical to the 2026-09-07 reference (`ff` values, session 16:00)
for every frame BEFORE the first lost bead (~11798; the recording has 51 lost-bead rows, so the reseed Case = plan
item 3 is the next slice, not this one). **Missing primitive found and routed:** a front-panel ARRAY-OF-PATH control —
peer research (`…-stage2-replay-path-array-control-route.md`) ranked `New VI Object` ×2 (Array shell on the Panel,
Path element owned by the array) first; donor = NI's `Creating Objects\Drop Digital Numeric Inside Cluster.vi`
(copies under `claudeDev\NIScriptingExamples`). Running: donor census (`tools/bench/census_newviobject_donors.log`)
and the plan review (`stage2-step-b-replay-core-plan`). Recipe not yet written.

**Route revised twice under review (23:4x–00:0x, both archived, both adopted):** the `New VI Object` op is dead
(`style` is an unretargetable typed ring); the replay core is a **FOR loop** (N from an auto-indexed input; the
fixture's ids have 124 gaps so `Loop Counter` cannot index them); the frame path comes from a **string-array
control** (Python supplies full paths) + a one-node `StrToPath.vi` — `Format Into String` is out (every small donor
instance has 5–6 arguments; arity is not scriptable; NI error 83 at run time). Toolkit for this: `OpForLoop_v1`
(the missing `Control Terminals→Inputs` wire), the register ops rebuilt on the **ForLoop seed** (`SR_SEED=For`),
`StrToPath.vi`. One runner: `tools/recipes/cycle3_toolkit.py` → `tools/bench/cycle3_toolkit.log`.

**Cycle-3 batch run 1 (23:46): item 1 stopped on a failed prediction** — `OpForLoop_v1` built (both ends wire 389,
ExecState 1, saved) and the control tunnel exists, but IndexMode read 0. Census: `Inputs Indexing?` IS wired
(1981 both ends) → not an op defect; the test used a SCALAR Boolean, which cannot auto-index — the test was
ill-posed. Review dispatched (`opforloop-v1-fail1-indexmode-zero`); the rerun's test uses the String[] control made
by the assembly's own trick (Get Controls `Control Names` → control → cut) and adds a 3-element and an empty run.

**Cycle-3 run 2 (23:48–23:55, INDEX row 39): items 1, 2a, 2b PASS** — `OpForLoop_v1` verified with a String[]
control (IndexMode 1, ExecState 1, 3-element and empty runs: H1 confirmed, and the string-array-control trick is
functional); `OpAddShiftRegF_v0` 9/9; `OpWireSRF_*` **7/7 functional on a real For loop (1024 iterations)**.
**Item 3 `StrToPath.vi` failed:** `copy_into` → Error 1054 in `OpMoveByLabel` ("object not found") — the `prepare`
label write was silently declined because the substituted donor's panel was not open (precedent `copy_clfn2.py`
opens it). Fix in the recipe (open panel + read the label back before the move); review dispatched
(`strtopath-fail1-move-by-label-1054`).

**StrToPath run 2 (23:58): label verified on uid 194, STILL error 1054** (skill notes: 1054 = name not found,
1057 = class mismatch) — so the name lookup fails even with the label text present. Leading hypothesis now: a
built-in function's `Open VI Object Reference` name is its OWN name (`String To Path`), not its label (a CLFN's
name is its label, which is why the precedent worked). Recipe: plan A = look up `"String To Path"` with no
prepare; plan B = the `STP` route. Review dispatched (`strtopath-fail2-label-present-still-1054`).

**StrToPath run 3 (00:01): BOTH lookups fail with 1054** (`'STP'` label and `'String To Path'` name) — the label/name
route of `OpMoveByLabel` is exhausted for built-in primitives (it works for controls and for a CLFN). Plan under
review (`strtopath-fail3-move-by-index-plan`): **`OpMoveByIndex_v0`** = `OpMoveByLabel_v0` with the
`Open VI Object Reference` replaced by `Traverse for GObjects` (class control) → Index Array (index control) →
`Move.reference`; Python picks the index from `report(donor, 'Function')` so uid 194 is copied by REFERENCE, no label.
Gives `copy_by_index()` — a general primitive-copier the fleet has lacked.

Review accepted (UID guard inside the op; target rejected on mismatch). Donor censused
(`tools/bench/diag_opmovebylabel.log`). **Running 00:1x: `tools/recipes/cycle3b_toolkit.py`** = build
`OpMoveByIndex_v0` (S1–S9 gates) → `build_strtopath.py` plan C (`gscript.copy_by_index`, expect uid 194) →
`tools/bench/cycle3b_toolkit.log`.

**cycle3b run 1–2 (00:07–00:19):** `OpMoveByIndex_v0` **BUILT + SAVED 13/13** (run 1 missed only the required
`Traverse Target` ring → control, = 1 BD; reviewed). `gscript.copy_by_index()` then copied uid 194 (UID guard
passed) but the broken Target's `gui_save` failed: no Block Diagram window was open and Ctrl+S on a Front Panel
saves nothing (2026-08-30 finding) → `gui_save` now opens the BD with Ctrl+E first. Review dispatched
(`strtopath-fail4-gui-save-of-broken-target`). **State: `Test - Moving Objects Target.vi` is loaded DIRTY while
its disk bytes were restored → LabVIEW RESTART before the next batch (standing permission).**

**00:3x: `StrToPath.vi` 9/9 FUNCTIONAL** (copy-by-reference + `finish` hook + one COM save of a runnable VI —
protocol revised per review, no broken intermediate saved). **CYCLE 3 COMPLETE** — INDEX row 39 final,
toolkit-capabilities "Overnight additions" table. LabVIEW restarted 00:2x (fresh).

### Overnight cycle 4 (00:4x) — `build_track_v6_core.py`: the replay core, PLANNED, under review

Recipe `tools/recipes/build_track_v6_core.py` (phases H head / L loop / R registers / O outputs / T fixture run).
One deviation from the reviewed route, gated: `Frame Paths` reaches `StrToPath.string` through `wire_control`
(a NON-indexed tunnel, so the wire is array→scalar and broken) followed by `set_index_mode(tunnel, 1)` — predicted
to retype the inner terminal to String and make the wire legal (ExecState gate + far-end wire UID); the reviewer's
"route 3" with its own gate. Kernel controls come from a temporary top-level kernel instance (create then delete).

Reviewed twice (`…-cycle4-replay-core-recipe.md`, `…-v2.md`; both sets of hardenings applied: fatal gates,
UID-set gate for the temporary kernel, tunnel route proven on a scratch first, register indices by UID, one-to-one
output-tunnel pairing, all three outputs compared, gate sequence 1 → 2 → 200 → `--full`, Run-timeout exit).
**Run 1 (00:5x): 28/29** — scratch discriminator D PASS (the wire-then-index tunnel route is proven: inner wire ==
`StrToPath.string`, ExecState 1, runs), head, temp-kernel controls (UID-set gate), String[] control, loop, the
indexed Frame Paths tunnel all PASS; stopped at the first BORDER-CROSSING wire by a wrong gate of mine (equal uid
both ends — a border wire is two Wire objects through a tunnel, row 36). Gate corrected (both ends non-zero + a new
non-indexed tunnel outer==source/inner==sink); reviewed + strengthened (one tunnel, direction, error fields).
**Run 2 (01:0x): 31/32 — a REAL rule-1a catch:** `Array of cal clusters` crossed the border AUTO-INDEXED (LabVIEW's
default for arrays into a For loop, applied by `Wire Inputs`) — one cluster per frame would have reached the
kernel. The IndexMode-0 gate stopped it. Fix: flip such tunnels with `set_index_mode(0)` and re-gate (NAMES.md);
reviewed, fix applied.
**Run 3 (01:1x): 37/38 — ALL wiring gates PASS** (the three arrays flipped to IndexMode 0 with inner wires
preserved); stopped at `add_shift_reg` with **error 1055 in `OpAddShiftReg_v0`**: my `gscript` wrappers
(`add_shift_reg`, `wire_sr`) never selected the ForLoop-seeded F-ops by `class_name` — the WhileLoop seed cannot
cast a ForLoop ref (row 28). Wrappers fixed (op + labels chosen by class); reviewed.
**Run 4 (01:2x): 57/58 — the replay core ASSEMBLED completely** (all wires, 3 registers with UID-set gates, 3
paired output tunnels, indicators) **but ExecState 0**: something is type-broken and no gate localised it (leading
candidates: a register cross-pairing via the Panel.Controls[]-order assumption in LeftOutCtl, or a broken inner
wire after an auto-index flip). Not saved. Recipe now carries a LOCALISER (on ExecState 0: wire→terminal census,
Remove Bad Wires, report the wires that vanish). Reviewed: the cause was `IMAQ Create.Image Name` — a REQUIRED
input never wired (HARNESS_compare had it as a control).

### ★ Run 5 (01:3x): 69/69 PASS — THE STAGE-2 REPLAY CORE IS FUNCTIONAL AND NUMERICALLY EXACT (INDEX row 40)

`claudeDev\Track_v6_CPU_core_v0.vi` (saved, ExecState 1): For loop over `Frame Paths` → `StrToPath` →
`IMAQ ReadFile` → `PARALLEL_kernel_v3clean` with the three feedback registers; XYZ/GOOD/POS **bit-identical** to
the 2026-09-07 reference for 1, 2 and 200 frames; **6.1 ms/frame in-loop** (vs 18–23 ms per COM-driven frame).
Labels: `tools/bench/track_v6_core_labels.json`. **`--full` (10,043 frames) running as its own batch →
`tools/bench/build_track_v6_core_full.log`** (it rebuilds the VI, then 1/2/200/full).

**`--full` 03:0x: 72/72 PASS — 10,018 pre-loss frames of 10,043 bit-identical in ONE 192-s run; post-loss worst
1072.28@11801 = the reference driver's own plain-feedback figure** (INDEX row 40 final). Usage limit hit ~02:xx,
reset ~03:00, resumed per protocol.

### Overnight cycle 5 (03:0x) — step C: the producer/consumer core. First plan REJECTED by review, v2 written

`archive/peer/2026-09-15-stage2-step-c-queue-core-plan.md` killed the While-tracker-stops-on-timeout design (the
"8 slots > depth 7" invariant was backwards; a timeout is not end-of-stream; a While stop terminal does not
short-circuit the timed-out iteration; paired queues are not atomic; `Q_meta` never consumed). **v2
(docs/stage2-assembly-step-c.md): in replay every loop is a FOR loop over N** — ACQ / TRK / sink run in parallel
through the queues with blocking calls, no timeouts, no Cases, `Q_img` capacity 8, meta passed through to the
sink; a pool-image gate precedes assembly. Live mode (While + end-of-stream token) = step D.

v2 reviewed (`…-queue-core-plan-v2.md`): accepted with a conditional liveness claim, error-chained paired
enqueues, and the final `Q_free` == permutation {0..7} gate — all written into the plan.

**Open construction question before the recipe:** the pool array leaves its For loop through an auto-indexed
OUTPUT tunnel; `Index Array(pool, slot)` must be fed from that tunnel's OUTER terminal, which no wiring op addresses
by name. Read-only census first: does the loop NODE's `Terminals[]` list its tunnels' outer terminals (then
`connect_terminals` by index works)? Else a small `OpWireTunnelOut_v0` (tunnel chain of `OpTunnelInd_v0` +
node chain of `OpConnectCtl_v0` + Connect Wire).

Census done (03:3x): a loop node's `Terminals[]` lists all tunnel outer terminals by name → loop outputs wire by
name; no new op. **v2.1: the pool is a queue of IMAGE REFNUMS** (no slots, no Index Array) — plan updated.

Recipe `tools/recipes/build_track_v6_queue.py` written and reviewed (`…-stage2-queue-core-recipe.md`: the
teardown race fixed by a join through each queue's `queue out` passed through the loop that last uses it + a
DRAIN loop of 8; KT self-check on all three outputs; count-tunnel trick proven on a scratch first —
`test_count_tunnel.log`: 0/1/3 elements → 0/1/3 iterations, ExecState 1).
**Run 1 (03:16): died in 1 s at phase P** — `copy_by_index` raised Errno 22 on the Move-example Target file,
which LabVIEW still had LOADED since the 00:3x StrToPath copy (the "substitute under a loaded VI" hazard the
save-failure review named). Recovery: the untouched EMPTY copy of `PathToStr.vi` deleted, LabVIEW restarted;
recipe now restarts LabVIEW before any `copy_by_index` session and removes a half-built sub-VI on failure.
Reviewed: my "CopyFile2 lock" mechanism was wrong; the copies were instrumented instead.
**Run 2 (03:3x): labelled — the FIRST copy (`donor → MOVE_SRC`) fails, errno 22 winerror None (CRT-level
EINVAL), right after `close_panel()` LOADED that file on the fresh instance.** Hypothesis: a loaded VI's file is
held (mapped) → write-open fails, CRT maps it to EINVAL. Fix = the discriminating experiment: in
`copy_by_index` all byte substitutions now happen BEFORE any COM call names the files (restore is file-only, the
`revert` comes after the copies). Reviewed: reorder confirmed.
**Run 3 (03:4x–03:5x): 100/101 PASS** — `PathToStr.vi` built (copy_by_index now works with substitute-before-load),
head + KT, 7 Obtains, pool loop, ACQ loop, TRK loop with its three registers all PASS; stopped in the SINK on a
GUESSED terminal name (`'timeout'` → the real `'timeout in ms (-1)'`, error 5001). Fixed in both count tunnels;
NAMES.md gained the queue terminal names. Reviewed, fixed.

### ★ Run 4 (04:0x): 162/162 PASS — THE PRODUCER/CONSUMER CORE WORKS, NUMERICALLY EXACT (INDEX row 41)

`claudeDev\Track_v6_CPU_queue_v0.vi` (saved): pool = a queue of image refnums; ACQ / TRK (3 registers) / sink
as parallel For loops through blocking queues; drain + chained releases. XYZ/GOOD/POS bit-identical for 1, 2,
200 frames; `META[n] == Frame Paths[n]`; KT one-shot == row 0; 8/8 pool images back; releases clean; 200 frames
in 0.2 s (reads overlap the kernel; cached TIFFs). Labels `tools/bench/track_v6_queue_labels.json`.
**`--full` 04:2x: 168/168 PASS — 10,043 frames in 7.5 s (0.7 ms/frame; the For-core took 192 s with serial
TIFF reads), all 10,018 pre-loss frames exact, META aligned, pool whole (INDEX row 41 final).**

### Cycle 6 (04:2x) — step E: the reseed Case (plan item 3). PLANNED, under review

[docs/stage2-assembly-step-e.md](docs/stage2-assembly-step-e.md). Facts measured from the reference jsonl: 13
frames carry −1.0 in x,y,z, the same 13 carry −1 in `pos`, 26 carry a FALSE flag (a superset — the flag is NOT the
trigger). The original's selector is compound (`Less?` #10950 / `Or` #10247 / `And` #9647 / implicit `min value`
#17289 upstream of #5540): **E0 = read-only census of that chain** (`tools/bench/census_case5540.py`, runs after
the full batch — one COM client at a time), then a `Reseed.vi` sub-VI (detector + Boolean Case + output tunnels:
~4 new ops) inside the tracking loop; acceptance = ALL 10,043 frames exact. Review dispatched
(`stage2-step-e-reseed-case-plan`).

**E0 measured 04:3x** (`census_case5540.log`): #5540 takes the kernel's RAW outputs and feeds the right
registers — the original's Case sits exactly where `Reseed.vi` will; selector = `Or`(inner Case #10445, outside
10312); lost-bead term = `Less?`(`min value`.Value ← `Array Max & Min`(pos out), y ← outside) → `And`; periodic
term = `# of Auto-Reset` → `Equal?` / `Quotient & Remainder`. **Structural race in the original:** the `min value`
indicator is written and property-read in the same iteration with no wire — the rebuild uses the direct dataflow
(numerically identical on the fixture) and this is an OPEN item for the user (docs/questions-for-user).
Second-hop census running (`census_case5540_hop2.log`: inner Case #10445, outside feeders via tunnels, constants).

**Hop 2 measured 04:4x** (`census_case5540_hop2.log`): `And(Less?, y)` feeds the inner Case #10445's selector AND
a `Not`; #10445 outputs a Boolean into `Or.x` plus a `Value` passthrough; `Q&R(tunnel 2213 ← outer 2187,
'# FD points')` → remainder into For loop #1359; `Equal?` → `Compound Arithmetic` #11639; #5540's t1/t4 come in
through tunnels 5569/5752. **Four feeders are constants whose VALUES the fleet cannot read** (`Less?.y`, `Or.y`,
`And.y`, `Equal?.y`) — `Constant.Value` 634AC00 reader still unbuilt (needs a Constant-typed seed: an NI example
with a Constant-class property node; the 'Finding and Modifying Objects' census returned 1055 instantly —
`diag_example_load.log` running). **Step E cannot be shown computation-preserving without those values**: it
stops here for the user's answers (docs/questions-for-user-2026-09-14.md, new section) + the Constant reader.

**Seed FOUND (04:5x, `census_constant_seed.log`):** NI's `Navigating Nodes and Wires.vi` diagram 3 has
TMSC → Property `Value` (uid 284) — the Constant-class chain; `Navigating Structures.vi` has a
`CaseStructure.Selector` PN (seed for the Case work). (The first census's 1055 was a forward-slash path: NAMES.md.)
Recipe `tools/recipes/build_opconstvalue_v1.py` reviewed (`opconstvalue-v1-recipe`: STOP-as-written → gates by
added uid, wires by uid, and the class settled by TYPED oracles: StringConstant must give the VISA literal
`COM`/`ASRL`, DigitalNumericConstant non-identical numbers). Run 1 (04:00 log clock): phase D fine, then **RPC unavailable after the recipe's own LabVIEW kill** — the
stale-op-proxy class again (`gscript._cache` survived `_lv = None`). Fix: `gscript.reset()` clears both; both
recipes' fresh-instance helpers use it. Reviewed, fixed.
**Run 2 (04:03 log clock): the Property node copied by reference (new uid 324, data terminal `Value`) and the
seed control created on its `reference` — but the Target read ExecState 0, so it was not saved** (cause not yet
localised: PN class not preserved by Move? seed class conflict? a wire stub?). Recipe gained a donor-ExecState
gate and an F1 diagnostic. **Run 3 LOCALISED it: the copied example node is a WRITE property (`Value` is a
sink) → an unwired required input; donor runnable, no wire stubs, class preserved.** Fix: keep the Constant-typed
seed, delete the write node, build the READ node with `build_property('VI Server:Constant', 634AC00)` on the TMSC
output. Review `opconstvalue-fail3-copied-pn-is-a-write`: diagnosis confirmed; reviewer prefers flipping `Is Write?`
first — deviated (no PropertyItem writer in the fleet; build_property proven), annotated. **Run 4 (04:10): BUILD
PASSED — `OpConstValue_v1.vi` saved runnable (ExecState 1, labels `tools/bench/opconstvalue_labels.json`, donor
and NI example unchanged). Structural only.** The TEST phase (typed oracles on the main VI) died with 0x800706BA
right after `fresh()` (kill + 8 s + reset()) and no LabVIEW process remained (no crash entry) — failed prediction
#3 of this error class; review `opconstvalue-run4-rpc-after-restart-no-labview` dispatched (bgrun
`tools/bench/peer_rpc_run4.log`). Fix prepared: com_preflight (pid-stable double round-trip) inside `fresh()`,
traceback in the handler, `--test-only` entry (the passed build is not rerun). Review landed (H1 top; MAIN not
proven reached; run the RAW discriminator first so the preflight does not mask the cause). `diag_rpc_restart.py`
runs 2 and 3 (cold, and warm launch→use→kill→relaunch): **not reproduced** — Dispatch blocks ~14 s and returns
ready, op(OP) and report(MAIN) succeed; measured: a COM-launched LabVIEW with no panel exits when its client exits
(explains run 4's missing process). Trigger INCONCLUSIVE. Run 5 `--test-only` (04:23, 1031 s): preflight OK, all
reads ran, then a recipe print bug (`None[:20]`) lost the values — non-result. **Run 6 (04:41, 302 s): FUNCTIONAL
for strings** — all 22 top-diagram StringConstants read as typed str, incl. the independently documented
`img%05d.tif` and `Bead # %d`. Two failed predictions: the COM/ASRL oracle (the VISA literal is on sequence
frame 10; the op traverses the top diagram only — oracle replaced) and **all 12 DigitalNumericConstant reads =
`None`, no error** (Variant-of-numeric marshalling suspected). Review `opconstvalue-run6-numeric-reads-none`
answered: export the variant through Flatten To String (lossless), drop the Boolean/OpReport probes. Recipe
`tools/recipes/build_opconstvalue_v1b.py` written (creator OpBuildFlatten_v0 + branch + 2 indicators + typed decode
test); review `opconstvalue-v1b-recipe-flatten` applied (parser = hypothesis validated on StringConstant[7] first,
NUL-survival length gate, per-read UID/class identity, MAIN md5 gate). **Build v1b (04:54) PASSED and saved**
(Flatten branch on wire 598, indicators `data string` / `type string (7.x only)`); its test failed on a NEW failed
prediction: the `data string` BSTR arrives **code-page decoded (cp949)**, not byte-raw. Review
`opconstvalue-v1b-bstr-codepage` dispatched (`peer_v1b_codepage.log`); fix prepared: `mbcs` strict re-encode with
structural gates and `--test-only` (never rerun main(): it would add a second Flatten). Review verdict: the string
route can never be PROVEN lossless (a corrupted DBL is a valid DBL) → the U8/hex route is the fix. No
String-To-Byte-Array creator in the Erdos Miller library; candidate donor `vi.lib\Bit Manipulation\Bytes to
Lowercase Hex String.vi` (ASCII hex out). Censuses (05:00): hex VI = `bytes` (U8[] sink) / `hex string`; the
Unflatten creator node exposes `data includes array or string size? (T)`. Route fixed: Flatten.data string →
Unflatten(type ← U8[] control seeded from `bytes`, size?=F) → hex VI; indicators `hex string` + U8[] `value`.
Recipe `tools/recipes/build_opconstvalue_v1c.py`; review `opconstvalue-v1c-recipe-byte-route` applied (remainder
indicator, size readback, buffer-style U8, strict hex, # of Refs/range gates, md5 audit in finally, negative
control). **Build v1c (05:06) PASSED and saved; byte route FUNCTIONAL on StringConstant[7]** (hex == U8, 53 B,
remainder empty, literal present, identity OK, MAIN untouched). Only the parser's framing hypothesis A failed (by
design): measured layout = version · I32 #TDs · TDs (code carries 0x40 label flag) · **I16 index count · I16
top-level index** · data · I32 attrs. Parser corrected (review `opconstvalue-v1c-framing`: documented layout).
**Run 2 (05:11, `--test-only`): byte route FUNCTIONAL on all reads** — but every DigitalNumericConstant returns
the SAME 20-byte EMPTY variant (TD 0x0000 void, no data, no error) for six different UIDs, while the string
constant carries its value: `Constant.Value` 634AC00 supplies NOTHING for numeric constants (measured; the
earlier H3). Review `opconstvalue-numeric-void-variant`: not a design fact yet — discriminators: (1) siblings
through the unchanged op (`diag_constvalue_siblings.log`): **BooleanConstant void too (4/4), strings carry data, no
PathConstants**; (2)+(3) recipe `tools/recipes/build_opconstvaluen_v0.py` (`OpConstValueN_v0`: DigitalNumericConstant-
typed node reading Value + `Numeric Text`→`Text.Text` + `Representation`) written; pre-build review
`opconstvaluen-v0-recipe-numeric-reader` applied (three separate property nodes, text asserted non-empty only,
reporter-class gate, baseline at import, cast error 1057). Build run 1 (05:26) STOPPED at gate B: **ID 634D004
attached `RadixVis`, not `Numeric Text`** — the wiki ID table is wrong for this class (failed prediction; review
`opconstvaluen-fail1-634d004-is-radixvis`: table shifted, no blind sweep). Census of the 8 documented IDs
(`census_dnc_property_ids.log`): **`634D007` = `NumText`** (map in NAMES.md). **Build run 2 (05:41) PASSED and
saved `OpConstValueN_v0.vi`; DECISIVE: through the DigitalNumericConstant-typed node `Value` CARRIES DATA for all 6
constants (TDs 400a DBL / 4007 U32 / 4003 I32, labelled), Numeric Text = '1','0','1','0','0','1', Representation
1/6/3** — the void was the base-typed node, not LabVIEW storage. Test stopped on two of my own gates (parser
required even TD lengths — measured odd, unpadded; negative control expected 1057 — got 1055 on the typed nodes);
both fixed; review `opconstvaluen-run2-typed-node-carries-data` applied (undocumented 2026 behaviour, not a
documented rule; Representation enum 1/3/6 = DBL/I32/U32 now a cross-check gate). The four selector constants
are identified by the WIRE they feed: recipe `tools/recipes/build_opconstvaluen_v1.py` (`OpConstValueN_v1` =
v0 + `Constant.Terminal` 634AC04 → `Connected Wire` 634A000 → `UID` 632A813 — review
`opconstvaluen-v1-recipe-wire-identity` corrected the chain (Constant is not a Node) and warned that constants
outside diagram 43 report the tunnel OUTER wire; the reviewer prefers a reverse traversal from the four wires —
deferred (two more typed casts); the bounded read-only `--scan` runs first, traversal only if the inner uids do
not surface). **Build v1 run 2 (05:49): 17/17 PASS — `OpConstValueN_v1.vi` FUNCTIONAL** (value 1.0 DBL / 0 U32,
TD == Representation, fed-wire uids 5003/3152, cast negative control 1055, MAIN untouched). Run 1 stopped on a
short-name gate (`Connected Wire` → `Wire`; review `…-v1-fail1-connected-wire-short-name`). **`--scan` of all
180 numerics running** (`tools/bench/opconstvaluen_scan.log`, ≤50 min; output `opconstvaluen_scan.json`) →
**scan done (06:00, 370 s, 180/180, identity failures 0, MAIN untouched): wire 10850 ← DigitalNumericConstant
uid 10739 = I32 `0`** → the lost term is `min(pos in cal image out) < 0` (the `pos == -1` marker); written into
step-e.md. The other three (10312/9806 Boolean terminals, 10142) matched no numeric constant — failed prediction,
review `opconstvaluen-scan-three-selectors-missing` dispatched (`peer_scan_three_missing.log`). Prepared:
review answered: walk the WIRE instead of re-scanning constants. **Build `tools/recipes/build_opwiresource_v0.py`
running** (`OpWireSource_v0` = donor OpConstValue_v1 minus its value tail, + `Wire.Terms[]`→IA[0]→`Generic.Owner`
→`ClassName`/`UID`; acceptance = wire 10850 must resolve to constant uid 10739 / DigitalNumericConstant;
`build_opwiresource_v0.log`, 20 min). Run 1 (06:07): the whole chain built and wired (Terms[]→IA→Owner→ClassName
gates all PASS, indicator `Class Name 4` created), then **`create_indicator` on the `UID` terminal produced no new
indicator** — failed prediction; review `opwiresource-fail1-uid-indicator-not-created`: duplicate panel labels are
LEGAL, so a label set is not a creation oracle. Recipe now diffs panel rows by UID and gates indicator-ness +
label uniqueness (+ an 80-node walker gate). Run 2 (06:13): the ClassName indicator was created normally, and the
UID one returned **nothing at all** — no panel row, no ControlTerminal, no error (the reviewer's H6). Diagnosis
under review (`opwiresource-fail2-generic-owner-into-gobject-node`, `peer_generic_downcast.log`):
`Generic.Owner` → a **GObject**-class node is a DOWNCAST, so that wire is broken and the node unusable. Recipe now
MEASURES it (reviewer's A/B/C ExecState sequence, then deletes the node) and identifies each source by CLASS; the
object itself then comes from the cast-free fed-wire scan (`build_opconstwire_v0.py`, Wire→GObject = upcast,
confirmed type-correct). **Run 3 (06:20): downcast diagnosis CONFIRMED (ExecState 1 → 0 on that wire).** The run
then failed my own step-C gate because a BRANCH is one wire object — deleting it also cut `Owner`→`ClassName`;
repaired (delete the node, not the wire; review `opwiresource-fail3-branch-wire-is-one-object` dispatched,
review `opwiresource-fail3-branch-wire-is-one-object` confirmed it and added `Wire.Disconnect Terminal` 6370C0D as
the per-sink primitive). **Run 4 (06:25): the BUILD PASSED and `OpWireSource_v0.vi` is SAVED** (all gates, labels
`opwiresource_labels.json`), then the TEST hung on `g.report(MAIN,'Wire')` — one op run PER OBJECT on a VI with
thousands of wires — and bgrun killed it at 20 min. Fixed to `g.uids()` (report_all, one run) + a forced restart in
`--test-only`; review `opwiresource-fail4-report-per-object-on-5000-wires` also pointed at
`vi.lib\VIServer\UID to GObject Reference.vi` (present on this machine; noted in NAMES.md as the future op).
**`--test-only` (11:47): the cross-check gate CAUGHT A REAL DEFECT** — `uids()` (report_all op, 1902 wires in
3.3 s) put uid 10850 at index 742, but the op's own Traverse at index 742 reported uid 3512: **index order is
per-op**, and mixing two enumerations violates the project's own "Traverse order is not a selector" rule. Review
review `opwiresource-fail5-traverse-index-order-mismatch` (no ordering contract exists; UIDs are stable within a VI).
**`tools/recipes/build_opwiresource_v1.py` running** — the wire is addressed by UID through
`vi.lib\VIServer\UID to GObject Reference.vi` (terminals censused, readback UID + class `Wire` + error gates, handle
delta measured, no nonexistent UID ever submitted). Run 1 (11:52) censused the VI — inputs `Owning VI` / `UID`,
output `GObject` (+ `dup Owning VI`); my count-based gate was wrong and stopped the build. Names are now in
NAMES.md and the gate selects by name; review `opwiresource-v1-lookup-terminal-census` dispatched
(`peer_lookup_terminals.log`): name+direction gates, and `dup Owning VI` is a flow-through (nothing extra to
close). Run 2 (11:56): the lookup was dropped, its UID control made, the TMSC rewired to its `GObject` output and
both readback nodes branch-wired — then **ExecState 0** with no per-step measurement to localise it. Recipe now
records ExecState after EVERY mutation; review `opwiresource-v1-fail2-execstate-zero-after-readbacks` dispatched
(`peer_v1_execstate0.log`): the cause was the BRANCH again — the Index-Array wire I deleted also feeds
OpReport_v3's identity property nodes. Recipe reworked: copy a FRESH cast node in while the VI is still runnable
(broken VIs cannot be saved), wire seed + lookup into it, then delete the OLD cast node and wire the new one into
`Wire.Terms[]`; ExecState after every mutation. Run 3 (12:04) stopped inside the copy's finish hook: the Wire-typed
seed already fed the old cast, so that connection is a BRANCH — `wire_control(..., branch=True)`. No peer review
for that one: the helper's own error named the cause and the branch mechanism is already documented here; the
exception is logged as a non-result. **Run 4 (12:06): 29/29 PASS — `OpWireSource_v1.vi` FUNCTIONAL.** UID→object
lookup verified (readback UID, class `Wire`), cross-check held (wire 10850 ← `DigitalNumericConstant`), MAIN
untouched, handle delta +148 over 4 reads. **Result: 10312 (`Or.y`), 9806 (`And.y`) and 10142 (`Equal?.y`) all have
source owner class `Diagram` — the documented signature of a front-panel CONTROL TERMINAL**, so those three
selector inputs are CONTROLS, not constants. `tools/bench/census_selector_sources.py` (panel_wiring match, one op
run) is running to name them.
Broken-VI readers to build next time: `Wire.Is Broken?` 6371004, `VI.Get Errors` 452, `Wire.Get Error List` 6370C0A
(NAMES.md).
Both lessons are in NAMES.md:
wire-uid equality does not prove a wire is good, and a branch cannot be deleted separately.
`build_opconstwire_v0.py` kept unbuilt as the fallback.

**CYCLE 6 CLOSED (12:09).** Ops now in the fleet: `OpConstValue_v1` (string constants, lossless bytes),
`OpConstValueN_v0/v1` (numeric value + text + representation + fed wire), `OpWireSource_v1` (wire → source object,
addressed by UID). All four reseed selector feeders are measured and written into `docs/stage2-assembly-step-e.md`
(constant I32 0; controls `Auto-Reset`, `Reset Tracking`, `Limit of Program`); INDEX row 43; six new standing facts
in NAMES.md; the user-questions doc now asks only about `Limit of Program`'s operational meaning.

**CYCLE 7 (started 12:1x).** Design review of `Reseed.vi` dispatched (`reseed-vi-design-cycle7`,
`peer_reseed_design.log`). Already settled offline while it runs: on the reference session the two candidate
triggers — "previous x,y,z contains −1.0" (the driver's rule) and the original's own `min(pos) < 0` — fire on the
SAME 13 frames, 0 disagreements across 50,215 per-bead comparisons, so the rebuild uses the ORIGINAL's quantity and
the fixture still validates it (step-e.md).

Design review ANSWERED (`reseed-vi-design-cycle7`): **build blocked** until two read-only censuses are done —
Case #10445's frames (it may not be collapsed into an `Or` unsighted) and both frames of #5540 (the TRUE-frame
contents are still the driver's paraphrase). Design restructured accordingly: a stateless **`ReseedMux.vi` built
from two `Select` primitives** (which deletes three of the four missing ops), with the selector expression and the
`# of Auto-Reset` counter kept at loop level; the periodic term stays in the rebuild. Next step: a case-frame
reader op. Property IDs ANSWERED and written into NAMES.md (`Frames[]` 6363801, `Frame Names` 6365002 →
`FrameNames`, `Selector` 6365000, `ConditionalTunnel.Use Default if Unwired` 5D251C00 → `UseDefault`,
`Terminal.Diagram` 634A002 → `Diagram`; inner-terminal order is NOT frame order — map via the terminal's diagram).
First increment building now: **`OpWireSource_v2`** = v1 + the source object's UID (a second cast, `Generic.Owner` →
TMSC(GObject) → `UID`), because Census B starts from the two #5540 output wires 5975/5637 and needs the TUNNEL uids
(`build_opwiresource_v2.log`). **Run 1 (12:2x) STOPPED**: the seed trick needs an unwired (broken) node, a broken
VI cannot be saved, and `copy_by_index` loads the target FROM DISK — so the copy ran against the unedited file and
the added-uid filter found nothing. Plan changed rather than patched: **`OpTunnelRead_v0`** instead — retarget the
EXISTING cast to Tunnel and use only UPCASTS afterwards (`Outside Terminal` 6356001 → `Connected Wire` → `UID`;
`Inside Terminals[]` 6356000 → Index Array[index] → `Connected Wire` → `UID` and `Terminal.Diagram` 634A002 → `UID`
for the frame), so no second cast is needed at all. Review answered: the real defect was comparing uid sets across a reload, so the fix went into the TOOLKIT —
`gscript.copy_by_index` now hands its own `added` delta to the finish hook — and the recipe keeps the VI RUNNABLE at
every save boundary (the seed stays wired until the hook cuts it). **v2 run 2 (12:3x): the op BUILT and SAVED (all structural gates, ExecState clean), and its cross-check then
exposed a CONTRADICTION that matters for step E:** the wire walk says wire 10850's source is a
`DigitalNumericConstant` with uid **3628**, while the 180-object constant scan says constant **10739** (value I32 0)
feeds wire 10850 — and 3628 is not in the reporter's DigitalNumericConstant list at all. The lost-bead threshold
VALUE depends on which is right, so step E stays blocked. Review `constant-vs-wire-source-uid-contradiction`
dispatched (`peer_uid_contradiction.log`); discriminator `tools/bench/diag_source_uid_contradiction.py` written
(agreement sweep + a direct UID lookup of 3628/10739). Review answered with the hypothesis my op could not see:
**H5 — the wire may have TWO sources and therefore be broken**; "no error" proves a property read worked, not that
the diagram is sound, and `Terms[0]` is a convention with known broken-wire exceptions. Prescribed algorithm: read
EVERY terminal of the wire with `Terminal.Is Source?` 634A003 (short `IsSource`) and the reciprocal
`Connected Wire`, and require exactly one source pointing back at the wire. **`OpWireSource_v3` building now**
(`build_opwiresource_v3.log`). **Run 1 (12:4x): the op BUILT and SAVED, and the terminal walk REJECTS H5** — wire
10850 has exactly ONE source terminal (`Is Source?` TRUE, owner class `DigitalNumericConstant`, reciprocal wire
10850) and one sink (owner class `Comparison` = the `Less?` node); indices 2+ are past the end. So the wire is
sound. **Still open: WHICH constant** — the owner-UID readout printed 3628 for every index including the
out-of-range ones, so that chain is reading something constant, not the indexed terminal's owner (the owner CLASS
chain, on the same wire, varies correctly). Review `opwiresource-v3-owner-uid-constant-3628` dispatched
(`peer_owneruid_stale.log`); the recipe's prints are now ASCII-only (the cp949 console killed run 1 in its own
error handler). `OpTunnelRead_v0` stays as
the fallback; noted for it: a `Tunnel`-targeted cast cannot reach `ConditionalTunnel.Use Default if Unwired`.

**NEXT (cycle 7, in order):** (1) confirm the case/diagram/tunnel property IDs → build a read-only case-frame
reader op; (2) Census A — Case #10445's frames (labels, contents, the source of output 10573, default-if-unwired,
side effects); (3) Census B — both frames of #5540, the source cones of tunnels 5975 and 5637 only; (4) then build
the stateless `ReseedMux.vi` (two `Select` nodes) plus the loop-level selector and counter, integrate into
`Track_v6_CPU_queue_v0`, and accept on all 10,043 fixture frames exactly. Later: live-camera step D.

**NEXT:** read the result → INDEX row 41 → `--full` batch → reseed Case (plan item 3) → live-camera step D.

**NEXT:** read the result → INDEX row 40 → if the 200-frame gate passes, `--full` (10,043 frames, ~3–4 min) as its
own batch → then cycle 5 = queues + acquisition loop (plan items 1, 2, 8) → reseed Case (item 3). → cycle 4 = `build_track_v6_core.py` (head, For loop, kernel + 3
registers, `XYZ`, fixture diff with a 600-s run timeout) → cycle 5 = queues + acquisition loop (plan items 1, 2, 8)
→ reseed Case (item 3).
(`OpWireSRSrc_v0`: left INSIDE terminal as the source into a named node input; `OpWireSRSink_v0`: left OUTSIDE
terminal as the sink of the initial value), per the measured direction rule (invoke on the SINK, `Wire Source` =
source; `LeftShiftRegister` derives from `Tunnel`, so 6356001/6356000 apply). Then the assembly recipe for
`claudeDev\Track_v6_CPU.vi`
from `EMPTY_v0.vi`, following docs/stage2-plan.md "Build order" with the review's items 1–8: pool of 8 `IMAQ Create`,
`Q_free`/`Q_img`/`Q_meta`, acquisition While loop (fixture mode first: ReadFile of `img%05d.tif`), tracking While loop
with the P=4 kernel loop inside (`loop_in('for', …, parallel=4)` + `drop_subvi(PARALLEL_kernel_v3clean)` + kernel
feedback shift registers), results queues, a sink; fixture acceptance = x/y/z bit-identical to
`archive/bench-2026-09-07-fixture/`. One runner (build → structural census → fixture run → diff → INDEX row).
LabVIEW restarted 22:00; nothing is running.


### Cycle 7 note (12:5x) — the wire-source instrumentation, and a hook false positive

`OpWireSource_v4` did what the review asked and localised the contradiction in one run: the owner-UID branch was
hanging off **OpReport_v3's identity node** (which describes the TRAVERSED object, owner = a Diagram, uid 3628
invariant), not off the `Owner` node fed by the `Terms[]` element. The class chain was always correct, so the earlier
findings stand (wire 10850's source is a `DigitalNumericConstant`; wires 10312/9806/10142 are control terminals) —
only "which constant" was never actually measured. `OpWireSource_v5` rewires that branch by DATAFLOW and asserts
**reference provenance** (each node's `reference` sink wire must equal the wire intended), which is the single gate
the reviewer named for this whole class of mistake; NAMES.md carries the lesson.

Also fixed: `tools/hooks/guard_peer.py` scanned `peer_*.log` transcripts as if they were build logs, so a reviewer's
sentence ("Fail the build on inequality…") blocked the very build that review had approved. Peer logs are now
excluded — they are evidence, not the thing under test.

**13:0x — the uid contradiction is RESOLVED and step E is not blocked by it.** `OpWireSource_v5` rewired the
owner-UID branch by dataflow and its provenance gate passed (751/751), but the VI then read ExecState 0 (deleting the
old wire may have cut a second sink again, or the rewired wire is broken, or the diagram needs a recompile) — review
`opwiresource-v5-still-broken-after-rewire` dispatched. That is instrumentation polish. What is measured and stands
(written into step-e.md): wire 10850 has exactly ONE source and one sink, both reciprocal; the source's CLASS is
`DigitalNumericConstant`; and the constant-side scan — identity-gated per read, no duplicate wire claims — names
uid 10739, value **I32 0**. The lost-bead test is `min(pos in cal image out) < 0`.

**13:1x — `OpWireSource_v5`: 12/12 PASS, instrumentation CLOSED.** The unwired-sink dump found the orphan the
deleted branch had left (a `reference` sink re-fed from the same Owner output — the reviewer's H1), and with the
branch correct the wire side reports wire 10850 = source `DigitalNumericConstant` **10739** (cast-output class
agrees) and sink `Comparison` **10950** = `Less?` #10950 from the E0 census. Three independent measurements now
agree. `docs/stage2-assembly-step-e.md` records the threshold as settled (`Less?.y` = I32 0); NAMES.md documents the
op and how to drive it.

**NEXT:** Census A/B still need a TUNNEL reader — retarget a cast to `Tunnel` and read `Inside Terminals[]` 6356000
per frame (map each inner terminal to its frame with `Terminal.Diagram` 634A002, since the array order is not frame
order), starting from the tunnel uids that `OpWireSource_v5` now returns for the #5540 output wires 5975 / 5637.

**13:2x — Census B step 1 DONE, step 2 in progress.** `OpWireSource_v5` resolved Case #5540's two output wires:
5975 is driven by **SelectorTunnel 6016** and 5637 by **SelectorTunnel 5680** (both wires then feed SubVI 5058 —
the E0 census had recorded only "the right shift registers"), and it re-confirmed 10850 ← constant 10739 / sink
`Comparison` 10950. `OpTunnelRead_v0` (Tunnel-retargeted cast + `Inside Terminals[]` + `Terminal.Diagram` → frame
uid) is being built to read what each FRAME puts on those tunnels; runs 1–2 stopped on the same
deleted-branch-orphan signature (all provenance gates pass, ExecState 0), the unwired-sink dump that solved it in v5
is now in this recipe too, and the mandatory review is dispatched (`optunnelread-v0-broken-after-retarget`).

**13:5x — `OpTunnelRead_v0` BUILT (24/24 PASS) and Census B step 2 measured.** Case #5540 has exactly TWO frames
(diagrams **5582** and **5592**); tunnel 6016 (`x,y,z array`) takes inner wire 6071 in frame 5582 and 6030 in 5592,
tunnel 5680 (`Bead is good? array in`) takes 5710 and 6011 respectively — and both tunnels report the same frame
set, as they must. Fixes that got it there, all banked in NAMES.md: no `Remove Bad Wires` inside an edit window
(it ate the whole reader chain when the Index Array input was transiently unwired), delete the obsolete sink NODE
before rewiring, and the wire stub a deleted node leaves behind makes the next connection a BRANCH.
Step 3 running: resolve the four inner wires to their driving objects (`diag_case5540_frame_sources.py`).

**14:0x — Census B, steps 3-4 measured; a TOPOLOGY CORRECTION.** Both frames of Case #5540 are pure pass-throughs
(4/4 identity-checked): frame **5582** forwards the case's input tunnels fed by the **LEFT shift registers**
(1681 ← LeftShiftRegister 1142, 6041 ← LeftShiftRegister 5805 = the PREVIOUS state), frame **5592** forwards two
**LoopTunnels from outside the loop** (5746 ← LoopTunnel 5752, 5979 ← LoopTunnel 5569 = the reseed values). Both
case outputs are consumed by **SubVI 5058**. So the case selects what goes INTO its consumer — which contradicts the
E0 note that it "sits after the kernel, before the registers" and matches the fixture driver's own rule ("the next
frame's kernel INPUTS become the calibration positions"). Step 5 running (`diag_case5540_context.py`): name SubVI
5058 and resolve the two reseed values' producers. Frame POLARITY (which diagram is the TRUE case) still needs
`CaseStructure.Frame Names` 6365002 — not yet built.

**14:1x — Census B COMPLETE except frame polarity.** SubVI 5058 = `Track N beads four-fold over-kernel-v3.vi` (the
kernel), so Case #5540 selects the KERNEL'S INPUT state. The reseed frame forwards wires driven by
`FlatSequenceInnerTunnel` 2886 / 5818 — the very wires that also initialise the left shift registers 1142 / 5805,
i.e. **the loop's initialisers**: a reseed restarts the kernel from the calibration state the loop began with.
All of it is in `docs/stage2-assembly-step-e.md`. Remaining: frame POLARITY (`CaseStructure.Frame Names` 6365002 +
`Frames[]` 6363801 → an op), then Census A (Case #10445), then the design.

**14:3x — `OpCaseFrames_v0` run 1 stopped, cause identified.** The property IDs both censused cleanly
(`MultiFrameStructure.Frames[]` 6363801 → short name `Frames[]`; `CaseStructure.Frame Names` 6365002 → `FrameNames`)
and every provenance gate passed, but the op inherits a TERMINAL-reader chain from its donor and the Index Array now
carries DIAGRAM references — so those Terminal-class nodes are type-incompatible and the blind orphan repair re-fed
them with the wrong type. Repair: delete the terminal readers, wire the element straight into `GObject.UID`
(Diagram inherits GObject). Confirmation review dispatched (`opcaseframes-terminal-chain-must-go`).

**15:2x — `OpCaseFrames_v0`, runs 2-4.** Both property IDs censused (`Frames[]` 6363801 → `Frames[]`,
`Frame Names` 6365002 → `FrameNames`); the inherited TERMINAL readers were deleted (the Index Array element now
carries Diagram refs), the frame-uid node was identified BEFORE deletion (a deleted node leaves a stub wire that
hides orphans), and the last dead reader was deleted rather than propped up — all per review. Still ExecState 0,
and the cause is now diagnosed as the SAME downcast trap one level up: the seed came from the
MultiFrameStructure node, so the cast emitted MultiFrameStructure and the CaseStructure-class `Frame Names` node was
fed a parent reference. Fix applied (seed taken from the CaseStructure node; one cast drives both by upcast); review
`opcaseframes-multiframe-to-casestructure-downcast` dispatched. **Toolkit gap this keeps exposing: no broken-VI
reader.** `VI.Get Errors` 452 is the next op to build — three consecutive diagnoses were guesses that a reader would
have answered in one run.

