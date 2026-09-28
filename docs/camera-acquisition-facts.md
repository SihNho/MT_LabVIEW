---
type: reference
status: current
date: 2026-09-12
tags: [docs, camera]
---

# The camera path: verified connector panes, and what they mean for frame loss

## The camera itself, measured (2026-09-12, `niimaqdx.dll` via ctypes — no LabVIEW)

`tools/bench/imaqdx_ctypes.py` and `tools/bench/imaqdx_limits.py` talk to the driver directly. This was the route
taken after three attempts to drive NI's example VIs over COM each ended in a modal dialog: the examples' `Camera Name`
is an IMAQdx Session control that reads back as `('', 0)` and could not be set from Python, and an empty name opens a
dialog that blocks every later COM call until LabVIEW is killed. The C API has no front panel, so it has no dialog.

| | value |
|---|---|
| **IMAQdx name** | **`cam1`** — *not* `cam0`. This single wrong guess is what blocked both earlier harness runs. |
| identity | JAI Corporation **SP-5000M-USB**, serial `000014FB0067A270`, SuperSpeed (USB 3.0) |
| sensor | `SensorWidth` 2560 × `SensorHeight` 2048; `WidthMax`/`HeightMax` report the same, i.e. **unbinned units** |
| binning | `BinningHorizontal` = `BinningVertical` = **2**, `JaiBinningGainEnable` False |
| frame | `Width` × `Height` = **1280 × 1024** immediately after a fresh open; `OffsetX` = `OffsetY` = **0** |
| pixel | `PixelFormat` = 8 Bit Monochrome; `PayloadSize` = 1 310 720 B at full frame (327 680 B when halved) |
| rate | `AcquisitionFrameRate` 90.0009 Hz; `AcquisitionFrameRateRaw` 11 111 = the frame **period in µs** |
| exposure | `ExposureTime` 1909 µs, `ExposureMode` Timed, **`ExposureAuto` Continuous** |
| trigger | `AcquisitionMode` Continuous, `TriggerMode` Off — free-running |

### The ceiling: **247.95 Hz**, so 150 Hz is reachable

Read as an attribute RANGE, not a guess: `AcquisitionFrameRateRaw` has minimum **4033 µs**, and 1 / 4033 µs =
**247.95 Hz**; `AcquisitionFrameRate` itself reports max 247.9544. That is at the full 1280 × 1024 binned frame, and
`Width`'s legal range is (8, 1280, step 8) with `Height` (8, 1024, step 2) — so the camera is not being asked for
anything unusual.

The wanted 150 Hz therefore has **65 % headroom in the camera**, and the goal does not have to move. What 150 Hz costs
is a per-frame budget of **6.67 ms** for everything the computer does; at the 247.95 Hz ceiling it is 4.03 ms.

One caveat that is easy to miss: `ExposureAuto` is **Continuous**. Exposure sits at 1909 µs today, which fits inside
even the 4033 µs ceiling period, but auto-exposure raises it when the field dims and the achievable rate falls with it.
A rate target is only safe with exposure bounded — `AutoShutterControlExposureMax` is currently 15 000 µs, which alone
would cap the camera near 66 Hz.

### The per-frame budget, measured (`tools/bench/camera_budget_sweep.py`, 2026-09-12)

The sweep does exactly what NI's `Acquire Every Image.vi` does — configure a ring of 10 buffers, fetch the **next**
buffer in sequence, then burn a settable delay pretending to process it — but through the C API, so no LabVIEW overhead
is folded into the answer. What comes out is the floor no software change can get under. 1280 × 1024, 2 × 2 binning,
4 s per point.

| camera set to | frame period | **budget (zero frames lost)** | first failing delay |
|---|---|---|---|
| 90.00 Hz | 11.11 ms | **10 ms** | 12 ms → 45.0 Hz processed, 179 missed |
| 149.99 Hz | 6.67 ms | **6 ms** | 7 ms → 75.0 Hz processed, 299 missed |
| 200.00 Hz | 5.00 ms | **3 ms** | 4 ms → 1 missed in 798 (marginal); 5 ms → 100.1 Hz |
| 246.97 Hz | 4.05 ms | **3 ms** | 4 ms → 123.9 Hz processed, 487 missed |

So **the budget is the frame period minus about 1 ms**, and ~1 ms of that margin is jitter rather than fixed cost.

**The failure mode is a cliff, not a slope.** Every failing row processes at *exactly half* the acquired rate — 150 → 75,
200 → 100, 90 → 45 — while `acquired` never falls. Overrun the budget by 0.3 ms and you do not lose 5 % of frames, you
lose every second frame. With `Next` semantics there is no graceful degradation to trade against.

### `Last` instead of `Next`: the cliff becomes a slope

The same sweep at 150 Hz with `Buffer Number Mode` = `Last`, which returns the newest buffer and never waits:

| delay | `Next` processed | `Last` processed |
|---|---|---|
| 6 ms | 149.7 Hz | 163.2 Hz |
| 8 ms | **74.9 Hz** | **123.0 Hz** |
| 10 ms | 74.9 Hz | 98.7 Hz |

`acquired` stays at 149.5 Hz in every `Last` row: a slow consumer on `Last` **never makes the camera wait**, it just
skips. At 8 ms of work per frame that is 123 Hz of updates instead of 75. This is the measurement behind restoring the
live view — a display loop on `Last` cannot drag the acquisition down, so the question is only whether it competes for
CPU and the UI thread, not whether it blocks frames.

(At delay 0 the `Last` row reads 23 795 "frames/s": with nothing to wait for it re-reads the same newest buffer
thousands of times. `Images Missed` is meaningless in `Last` mode for the same reason — a skipped buffer there is
intentional, not lost work.)

### Ring depth does not buy throughput

At 150 Hz with 10 vs 50 buffers the cliff does not move: 6 ms passes and 7 ms collapses to 75 Hz in both. That is the
expected result and worth stating so nobody spends effort on it — **a consumer that is permanently slower than the
camera cannot be rescued by a deeper ring**; depth only absorbs *jitter*, and this sweep applies a constant delay, so
it deliberately tests the steady-state case where depth provably cannot help. Depth is still nearly free (100 buffers
× 1.31 MB = 131 MB against 64 GB), so it remains the right insurance against occasional long frames — it is simply not
a lever on the budget.

### What that budget has to pay for, at 150 Hz

| item | measured cost | share of the 6.00 ms | source |
|---|---|---|---|
| **budget at 150 Hz** | **6.00 ms** | — | this sweep |
| acquisition itself: 1.31 MB out of the ring | **0.12 ms** (median 122.6 µs, p99 206 µs, 10.70 GB/s) | 2 % | `tools/bench/camera_copy_cost.py` |
| tracking kernel, CPU-parallel | 2.43 – 2.87 ms | ~42 % | INDEX rows 15–18 |
| tracking kernel, GPU v2 | 1.14 ms above base | ~19 % | INDEX row 15 |
| **one serial round trip — PI motor, measured** | **2.56 ms** | **~43 %** | `tools/bench/serial_roundtrip.ps1` (1.2 ms fixed + 86.8 µs/byte) |
| display via ImageToArray → Flatten Pixmap | not yet measured, known slow | — | `docs/frame-loop-anatomy.md` |

**Two caveats keep this from being a settled number, and both matter.**

*Which port.* The 2.56 ms is the **PI motor** (COM3, GCS queries). The subVI on the frame loop is the **ASI** path on
COM4, and ASI is not the same animal: `Send Serial Command.vi` serialises the port with a named semaphore and does a
**VISA Read by byte count** rather than by termination character, so a short reply blocks until the VISA timeout
(default 5000 ms per `Mercury_comm.vi`'s help).

**ASI measured 2026-09-12** (`tools/bench/serial_roundtrip_asi.ps1`, COM4, 50 exchanges, 0 timeouts):

```
/  (STATUS)   median 1.128 ms   min 0.960   p90 1.292   max 3.200   reply 'N'
```

`/` was the command chosen because its reply is **fixed length** — one character plus CR LF — which is the one shape
that cannot trip the driver's read-by-byte-count. It is therefore a *small* exchange, and the raw 1.128 ms must not be
copied into the budget table as "the ASI round trip". Decompose it instead: `/` + CR is 2 bytes out and `N` + CR + LF
is 3 bytes back, and at 115200 8N1 a byte is 86.8 µs, so 5 bytes is 0.434 ms of wire time. That leaves

**fixed overhead ≈ 1.128 − 0.434 = 0.69 ms** (controller turnaround + FIFO + driver),

and a realistic `WHERE`-style position query of ~16 bytes total costs **0.69 + 1.39 ≈ 2.1 ms** — smaller than PI's
2.56 ms but the same order, i.e. **~35 % of the 6.00 ms budget** when it is paid. The number is now this port's own
measured overhead plus a measured wire model, not another instrument's figure. (The 16-byte estimate is an estimate;
the 0.69 ms is measured.)

Command safety was settled before anything was transmitted: `archive/peer/2026-09-12-asi-tiger-readonly-commands.md`
confirms `/` as query-only and lists the motion/homing/flash commands to blacklist — including `SAVEPOS`/`SP`, whose
bare form halts the axes, writes to flash and leaves the controller unresponsive until a power cycle. The script ships
with that blacklist, an empty-by-default whitelist, and a second `-IUnderstandTheRisk` gate.

*How often.* What is certain from `tools/bench/loop_contents.json` is that `ASI_adjust focus-subvi.vi` (uid 48 —
`VISA resource name`, `In position`, `Out position`, `Focus inc reference`) sits **directly on diagram 43's body**, so
it is *called* every iteration, and that a second VISA path sits inside Case Structure uid 10407, which is conditional.
What is **not** established is whether uid 48 *transacts* on every call: the audit found it holds a fixed `Wait (ms)`
inside a case frame (diagram 8) plus five or more property-node `Value` accesses, and its `+Inc`/`-Inc`/`Focus inc`
inputs are **control references**, which is the shape of a VI that acts only when a key or button says so.

> ## ⚠️ USER CORRECTION, 2026-09-16 — focus is SOFTWARE-driven, and "control reference ⇒ operator-driven" was wrong
>
> *"나는 실제 실험 중 ASI를 매뉴얼하게 조작한 적이 없음 (조이스틱 하드웨어는 제외). 소프트웨어적으로
> off-focus 되었을때 포커스 재조종 들어간 것. 그러나 컨트롤 조정이 가능한 것 또한 사실이긴 함. 다만, 이 부분
> 배선이 잘 되어 있는지는 모르겠음."*
>
> The user has **never** adjusted ASI focus by hand during an experiment — the joystick is separate hardware and
> does not go through this VI. When the image goes off-focus, **the software re-adjusts it.** Manual adjustment
> through the controls is *possible*, but whether that path is even wired correctly is unknown to the user.
>
> **What this kills:** the inference that a control-reference input means the VI "acts only when a key says so".
> That is a statement about the *terminal type*, and terminal type cannot distinguish a human pressing a button
> from a `Value` property write issued by code — both arrive at a control reference. Two sessions and one peer
> review reasoned from the structure to the driver and got it backwards. (The prior-art review's A3b verdict was
> right that the premise was unverified; its conclusion, "operator-driven", was the same mistake with the opposite
> sign. `docs/cycle10-plan.md`'s H2 replacement inherited it.)
>
> **What this opens, and it is now a blocking question for the split order:** there is an autofocus decision path
> — something computes "we are off focus" and issues a correction — and **we have not identified it.** Until it is
> found we do not know which loop it belongs in, how often it fires, or whether it transacts serial when it does.
> This is offline work: find every writer of those control references (`Value` property writes, locals, subVI
> calls), and the off-focus criterion that gates them.
>
> **Still true and unaffected:** the *cost* measurements below (the ASI wrapper's unconditional diagram is five
> nodes; the VISA case is a gate; the per-frame cost on ordinary iterations is two UI-thread property reads). What
> changes is the assumed **frequency and trigger** of the expensive branch, not the price of either branch.

### MEASURED 2026-09-16 (master plan A6) — the autofocus decision path, found in our own dumps

Read **offline**, from `tools/bench/frame_loop_graph_43.json`, `main_netmap_diag43.json`, `frame_loop_state.json`
and `asi_focus_anatomy.json`. No LabVIEW was started; the data had been captured in earlier cycles and not yet
walked. (Which is itself the finding the prior-art review keeps making: the answer was already on disk.)

**The decision lives in the MAIN VI, not in the subVI.** `CaseStructure #10407` on diagram 43 is the autofocus
case, and its terminals are, verbatim from the netmap:

| terminal | name | wire |
|---|---|---|
| t0 (selector) | — | 10799 |
| t1 | `# slices in stack` | 9635 |
| t2 | **`Index of closest\ncal image slice, bead 2`** | 10990 |
| t3 | `Outgoing Handle` | 11232 |
| t4 | `VISA out` | 7337 |
| t5 | `Out position` | 7388 |
| t6 | `position [internal units]` | 9113 |

**The criterion is an AND of two conditions**, and neither is an operator action:

```
#10407 fires  ⇐  10686 `x .and. y?`
                   x ← 3057 `x = 0?`   ← 2136 `x-y*floor(x/y)` (Quotient & Remainder)
                                          x ← wire 3268 = the FRAME INDEX
                                              (the same wire feeds save trace.vi #376 t7 "frame index"
                                               and WLC function sub.vi #1114 t0 "index i")
                                          y ← wire 31234 ← Property Node #30146 `Value`  ⟵ still unnamed
                   y ← 10825 `.not. x?` ← wire 3362, which crosses the frame loop's border
                                          (frame_loop_state.json: "one-sided", inner_feeds_body)  ⟵ still unnamed
```

So autofocus is **periodic and code-driven**: *every N-th frame, unless a boolean says otherwise*, where N is read
from a front-panel control by a property node. The value it acts on is the tracking kernel's own output —
`pos in cal image out` (wire 121) indexed by `Index Array #10757` to **bead 2** — compared against
`# slices in stack`. That is exactly the user's description ("소프트웨어적으로 off-focus 되었을때 포커스 재조종
들어간 것"), now with the mechanism attached: off-focus means *bead 2 has drifted through the calibration stack*.

**And yes, it transacts serial when it fires.** Two independent records:
- inside `#10407`, **diagram 73** calls `ASI TG-1000.lvlib:Move Axis Relative.vi` (`diagram-hierarchy.md:46`);
- inside the subVI, `asi_focus_anatomy.json` shows `CaseStructure uid 587` holding two VISA subVIs
  (uid 663 `VISA out`; uid 929 `VISA out` + `position [internal units]`) on diagram 4, and the fixed `Wait`
  (uid 1179) on diagram 8. The subVI's top level is only two control-reference `Value` reads and the case.

**Consequence for the split order:** the ASI path fires on a *frame-index schedule*, not on a rare exception, so
its cost is incurred on a predictable subset of frames — which is the worst shape for a p99 budget and the
strongest argument yet for rule 1c's dedicated ASI loop. It also means the dry run will exercise it: with no beads,
`Index of closest cal image slice, bead 2` is garbage, so **every N-th frame will command an ASI move** unless the
boolean on wire 3362 blocks it. ⚠️ Written when the ASI was carved out of every hardware permission; **rule 1b was
rewritten on 2026-09-16** so that permission follows the rig state and the piezo is treated like any other motor —
allowed while disassembled, forbidden once assembled. The mechanism below is therefore a *batch setting* now and an
interlock later.

**Two names still missing, and they need one LabVIEW read** (both are border objects the offline dumps do not
resolve): which control feeds Property Node **#30146** (the interval N — panel candidates are `Limit of
Auto-Focus` #48 and `Focus Deviation from the Center` #33), and what boolean arrives on **wire 3362**. Until the
second one is named we cannot say whether a dry run auto-disarms itself.

#### Read from the machine, 2026-09-16 (`tools/bench/diag_autofocus_border.log`, `OpWireSource_v5`, MAIN md5 unchanged)

| wire | source | sinks |
|---|---|---|
| **3362** (the `NOT`'s input) | **`Diagram` 639** | `Function` 10825 only |
| **3268** (the modulo's dividend) | **`Diagram` 639** | `Function` **2136** (autofocus modulo) · `SelectorTunnel` 3045 · `LoopTunnel` 2213 · `Function` **10068** · `SubVI` **1114** t0 `index i` |
| 31234 | `Property` **30146** | `Function` 2136 (`y`, the divisor) |

Two things follow, and one of them was not being looked for:

1. **A source terminal owned by a `Diagram` is the control-terminal signature** — that is how INDEX row 43
   identified `Auto-Reset`, `Reset Tracking` and `Limit of Program`, *"confirmed by `panel_wiring`"*. A constant on
   the same diagram looks identical, so the label comes from `panel_wiring`, not from the signature.
2. 🔴 **The autofocus schedule and the PERIODIC AUTO-RESET share one counter.** `Function #10068` is the
   `Quotient & Remainder` that `stage2-assembly-step-e.md:36` names as part of the periodic auto-reset term — and
   it reads the same wire 3268 as the autofocus modulo #2136. So the two periodic behaviours are two divisors on
   one frame counter. This is independent corroboration of the master plan's A3 correction: the periodic
   auto-reset is real, it is driven by frame count, and ~~it is not gated by the `Auto-Reset` control~~.
   🔴 **THAT LAST CLAUSE IS WITHDRAWN, 2026-09-16 (cycle 13; prior-art `A3-ii`).** It contradicted
   `docs/pre-rig-master-plan.md:224-227`, which says in terms that *"the plan may not assert either"* while the
   chain is unwalked — and both documents were current on the same day. The two claims this file may still make
   are the measured ones: the periodic auto-reset **exists** and is **driven by frame count**. Whether
   `Auto-Reset` gates it is **open and under measurement** — `docs/cycle13-plan.md` §3d resolves the driving node
   of every input wire of `ForLoop#1359` and tests whether the control's wire **9806**
   (`docs/main-vi-panel-map.md:317`, uid 17472) reaches it. Do not re-assert either side from this paragraph.

#### ✅ NAMED 2026-09-16 — the boolean is the front-panel control **`Fix to a Certain Pattern`** (uid 10230)

`panel_wiring(MAIN)` (`tools/bench/diag_autofocus_panel.log`, 114 rows, MAIN md5 unchanged) resolves wire 3362 to
a **control terminal**, and the control's label is `Fix to a Certain Pattern`. So the criterion reads, in full:

```
autofocus (#10407, which moves the ASI focus axis)  fires when
      (frame counter mod N) == 0        N ← Property Node #30146 `Value`  (control still unnamed)
  AND  NOT( Fix to a Certain Pattern )  ← front-panel control uid 10230
```

🔴 **CORRECTED within the hour — `Fix to a Certain Pattern` is NOT an operator switch. Code writes it every
iteration.** The user said so from memory of their own panel (*"auto-reset을 활성화시키면 tracking reseeding,
auto-focus는 piezo 움직임 조절"*), the trace confirms it, and the earlier paragraph below — "set it TRUE to disarm
autofocus" — **would not have worked**: the next iteration overwrites it. The real switch is **`Auto-Focus`**.

```
enable  =  NOT( reseed-And #9921 )  AND  Auto-Focus (#24266, wire 7527)
                                    AND  ( #10445's counter  <  Limit of Auto-Focus (#10173, wire 11527) )
                                                                        [Compound Arithmetic #10886 → wire 6525]
Fix to a Certain Pattern  ←  NOT(enable)      [ NOT #10285 → wire 3461 → Property Node #1469, an implicit WRITE ]
#10407 fires  ⇐  (frame counter mod 25 == 0)  AND  NOT(Fix to a Certain Pattern)   ≡  every 25 frames AND enable
```

Read entirely offline from `tools/bench/main_netmap_diag43.json`; the write target is named in our own
`frame-loop-wire-graph.md:56` — *"#1469 Property `Fix to a Certain Pattern`.Value (implicit)"*.

**Three things fall out of this, and two of them were open questions elsewhere:**

1. **The control the case reads is a code-written flag**, which is the cleanest possible demonstration of the
   user's 2026-09-16 correction: a `Value` property write arrives at a control exactly like a button press, so
   "it is a control, therefore an operator drives it" is never a valid inference.
2. **Autofocus is suppressed while the reseed fires.** Wire 9921 — the reseed `And` that
   `stage2-assembly-step-e.md:55` recorded as *"→ 9921 (sink to find)"*, unanswered — goes to three places: the
   periodic auto-reset Case `#10445`'s selector, a further `And` #9647, and (negated) this enable. **That "sink to
   find" is now found.**
3. **`Limit of Auto-Focus` caps it against a counter coming out of `#10445`**, so the focus system and the
   auto-reset system share state rather than merely coexisting.

**To stop the piezo moving in a dry run, turn `Auto-Focus` OFF** — writing the pattern flag is pointless.

~~**This is the in-run disarm the dry run needs.** With `Fix to a Certain Pattern` **TRUE**, the AND is false every
iteration and the autofocus case never fires~~ (superseded by the block above; kept so the reasoning is traceable) — so the forbidden ASI axis is not driven *during* the run. It does
nothing about the startup sequence, which drives the same axis before any loop iterates (`main-vi-startup.md:33`);
that is master plan 0.5. **Note (2026-09-16 rule change):** driving the ASI is *permitted* while the rig is
disassembled — permission follows the rig state and the piezo is no longer carved out — so this control is now a
**measurement choice** (do I want focus corrections inside this batch?) rather than a safety interlock. It becomes
an interlock again once the rig is assembled.

⚠️ **The control's NAME is measured; its intended MEANING is the user's to confirm.** "Fix to a certain pattern"
reads as *hold the field fixed instead of chasing focus*, which matches the wiring, but a label is not a
specification and this one gates the instrument that can break the rig.

**Not the same control:** `Auto-Focus` (uid 24266) drives wire **7527**, not this selector, and
`Limit of Auto-Focus` (uid 10173) drives wire 11527. Neither reaches #10407's selector, so whatever they gate is
elsewhere — do not assume `Auto-Focus` turns autofocus off.

#### ✅ N = the front-panel control **`Frame rate`**, and its value is **25** — and this was on disk all along

`frame-loop-wire-graph.md:120` already reads, verbatim: **`#30146 Property 'Frame rate'.Value (implicit)`** — the
bound control, by name, for the very node whose link I spent this session trying to resolve. It is there because
`OpNodeLabels_v0` was built on 2026-09-14 for exactly this and verified **88/88** on this VI
(`archive/peer/2026-09-14-implicit-property-node-linked-object.md`, whose annotation records
`Linked Control` = ID **636F806** and the cast-free `Node.Label → Text.Text` route it settled on).
`main-vi-panel-map.md:83` gives the value: `| 98 | Frame rate | CTL | value 25 |`.

**So the criterion, complete and measured:**

```
autofocus #10407 fires when   (frame counter mod 25) == 0   AND   NOT( Fix to a Certain Pattern )
```

🔴 **That is roughly every 0.28 s at 90 Hz — about 3.6 times a second**, and each firing runs
`ASI TG-1000.lvlib:Move Axis Relative.vi` plus the wrapper's position read and fixed `Wait`. The ASI serial path
is therefore not an occasional branch at all; it is a steady 3.6 Hz obligation sitting inside the frame loop. This
is the measured form of the user's *"focus 조정은 꽤나 빈번하게 발생함"*, and it is the strongest single argument
for rule 1c's dedicated ASI loop. (What the case does *inside* — whether it always commands a move or only when
the deviation exceeds a threshold — is not established here and should not be assumed.)

**Two things I got wrong on the way, kept because they are the expensive kind.** The candidates I named for N
(`Limit of Auto-Focus` #48, `Focus Deviation from the Center` #33) were guesses and both are wrong. And the
elimination shortcut — "only 8 of 60 controls have a bare terminal, so N is one of them" — is invalid: the first
three of those eight (`Focus Step (F1)`, `+ Inc`, `- Inc`) are the **control references** handed to
`ASI_adjust focus-subvi.vi` (`main-vi-panel-map.md:549`), and a control that *is* wired elsewhere can still be
read by a property node, so the list was never exhaustive. `Frame rate` is wired elsewhere and would never have
appeared in it.

#### The unpredicted failure in run 1, and what it turned out to be

`report_all(MAIN, "PropertyNode")` raised **error 1092** inside `Traverse for GObjects`. A 2×2 grid settled it in
20 seconds: the legal VI Server class name is **`Property`** and `PropertyNode` does not exist in the hierarchy —
full account and the citation in `docs/NAMES.md`, "The two failure codes are different". The same file had said
`Property` since 2026-09-12.

### ANSWERED: the frame loop does NOT transact serial every iteration (2026-09-12)

> **USER CORRECTION, 2026-09-15: "실제 사용 결과 ASI로 focus 조정은 꽤나 빈번하게 발생함."** Focus adjustment is
> FREQUENT during a real run. That does not change the measurement below — the transaction is still conditional —
> but it destroys the inference built on top of it. A 2026-09-15 plan review argued that because the serial is
> conditional, moving ASI out of the frame loop wins nothing and can be deprioritised; that argument silently
> assumed focus activity is rare. It is not. So the frame loop's cost is **bimodal**: cheap on ordinary frames,
> and +~2 ms (the peer's own 2.1–2.56 ms range, itself an estimate from a short exchange, not a measured `WHERE`)
> on every frame where focus acts — inside a 6.00 ms budget. The consequence is **dropped frames during focus
> adjustment**, i.e. a p99 / tail-latency defect, not an average-throughput one. Giving the ASI its own loop is
> therefore justified, and the review's own architectural advice agreed: the ASI loop should **exclusively own the
> VISA session**. What is still unmeasured is how often "frequent" is, and the true `WHERE` latency — both need the
> rig, which is disassembled as of 2026-09-15.

`tools/bench/read_asi_focus.py` read the subVI's nine diagrams on a copy. Its **top-level diagram — the part that runs
unconditionally on every frame — holds five nodes**:

| uid | what it is | per-frame cost |
|---|---|---|
| 46 | Property Node `Value` on a control reference | **a UI-thread round trip** |
| 108 | Property Node `Value` on a control reference | **a UI-thread round trip** |
| 272 | a comparison (`result`, `value`, `value`) | negligible |
| 587 | **Case Structure**, tunnels carrying `VISA resource name` / `VISA out` / `In position` | gate only |
| 443 | reference pass-through | negligible |

The two real serial VIs sit **inside** that case, on diagram 4: uid 663 (`VISA out`) = `Move Axis to Position.vi` and
uid 929 (`position [internal units]`, `VISA out`) = `Get Current Position.vi`. The fixed `Wait (ms)` the motion audit
found is on diagram 8, also inside a nested frame — not unconditional.

**So serial does not block 150 Hz.** It is paid only while a focus key is held, and then it is paid as a cliff: one
overrunning iteration loses a whole frame, not a fraction of one, which is the shape of the intermittent instability
rather than a constant slowdown.

*(A caveat about the script's own output, because read literally it says the opposite: its verdict line reports
"diagram 0 … 1 VISA node". That node is uid 587, the **Case Structure**, flagged because its tunnels carry the VISA
wire. A structure passing a refnum through is not a transaction. The keyword filter cannot tell those apart.)*

**What IS paid every frame is two `Value` property nodes**, and a `Value` property node **always executes in the UI
thread**. That is two thread switches per frame whose latency depends on how busy the UI thread is — which is a direct
mechanism for the user's observation that turning the image display on destabilises frames: the frame loop's property
reads queue behind the panel redraw. The motion audit's conclusion about the motor loop — *the loops were separated,
but they meet again in the UI thread* — turns out to hold for the frame loop too.

**Open, and blocked on a missing tool rather than on knowledge:** the `Wait (ms)` constant inside that VI has never been
read, and no op in the fleet reads a diagram constant's value. That is a tool gap to close, not an impossibility;
whether VI Scripting exposes a constant's value at all is being checked externally before anything is built.

The dedicated motor loop is *already* separate and correct: diagram 20 holds one `Motor control v5` call with
`Rot VISA in/out`, which is what the `4.4_MotorParallelLoop` version introduced.

**Acquisition is not the problem: it costs 2 % of the budget and is paid in every possible design**, so no restructuring
can win it back and none needs to. That measurement also corrects a tempting wrong number — the `Last`-mode delay-0 row
appears to show 42 µs per call, which would be 31 GB/s; timing only the calls that returned a **new** buffer number
gives 122.6 µs and 10.70 GB/s, a real memcpy rate. The 42 µs calls had copied nothing.

Kernel + a single serial round trip is **5.06 ms of the 6.00 ms**, leaving under 1 ms for the display, the file writes,
the front-panel updates and everything else — and MOV/VEL do *two* round trips, not one. That is the quantitative form
of the user's own observation that too much is crammed into one loop, and it is the case for moving the serial read and
the display out of the frame loop: doing so returns ~2.5 ms, which is the difference between 150 Hz and 200 Hz.

### The "first run halves the image" report is NOT the camera persisting a bad state

The first probe found the camera at **640 × 512** — exactly half of 1280 × 1024 — with **binning still 2 × 2 and both
offsets 0**. Two consequences:

1. **Calibration is safe.** Binning was unchanged, so nm-per-pixel was unchanged. The halved frame is a smaller field
   of view, not coarser pixels, and the distances measured during a halved run are not wrong.
   (This kills the worse of the two hypotheses: a binning change would have doubled nm-per-pixel.)
2. **The offsets were zero**, which falsifies the GenICam clamping hypothesis (`Width` ≤ `MaxWidth − OffsetX`) that
   was the leading explanation before the measurement.

A second open, minutes later and with nothing else touching the rig, read **1280 × 1024**.

### Open/close resets the ROI — measured, not inferred (`tools/bench/imaqdx_reset_test.py`)

| phase | result |
|---|---|
| 1. open, read as found | 1280 × 1024, PayloadSize 1 310 720 |
| 2. write `Width`=640, `Height`=512 (binning untouched) | **rc = 0, silently accepted** → 640 × 512, PayloadSize 327 680 |
| 3. close, re-open, read | **1280 × 1024** again |
| 4. left at the full binned frame | 1280 × 1024 |

### MEASURED 2026-09-16 — **exposure resets on session open too, and that kills the Python-pre-pass idea**

The same test, run on the exposure attributes with `tools/bench/camera_contract.py` (three consecutive sessions):

| phase | `ExposureAuto` | `ExposureTime` |
|---|---|---|
| 1. open, read as found | **Continuous** | 1909 µs |
| 2. same session: write `Off`, write 5555.5 | **Off** (read back) | **5555 µs** (read back; the camera quantises to 1 µs) |
| 3. close, open a NEW session, read | **Continuous** again | **1909 µs** again |

So exposure behaves exactly like the ROI: **`IMAQdxOpenCamera` hands every session the camera's own defaults**, and a
setting written by one process is gone the moment that process closes. Phase 0.4 of the master plan had assumed a
Python pre-pass could set the operating condition for a later LabVIEW run; it cannot. **Whoever owns the acquisition
session must write the contract after opening it** — i.e. the acquisition loop, right after `IMAQdx Open Camera`,
followed by a read-back into the batch record. `camera_contract.py` keeps its value as the *reader* and as the
pre-flight check, not as the applier. (The prior-art review rev3 raised this as B5 from the ROI table below; the
exposure half was unmeasured in either direction until this run.)

**It also answers a question nobody had asked plainly: every run starts at `ExposureAuto = Continuous`.** Line 26 of
this file recorded that as the camera's state; the reset behaviour makes it the state at the *start of every run*
unless the VI writes it. Nothing in `docs/main-vi-startup.md` shows the main VI touching an exposure attribute — so
on present evidence the original experiments run with auto-exposure, and the achievable frame rate has been a
function of how bright the field was. ⚠️ Not proven: "no mention in our startup map" is weaker than "the VI does not
do it", and the check belongs with the next main-VI read.

So `IMAQdxOpenCamera` hands every session a full frame. **The user's "second run restores it" is the driver, not the
second run** — every run starts from 1280 × 1024, and the halving is something the first run does *after* opening.
The camera accepts a half-size ROI **with rc = 0 and no error**, which is why nothing ever surfaced a fault.

That creates the constraint worth holding on to: *if the VI wrote a fixed constant, the second run would halve it too.*
So either the written value is **not** a fixed constant, or **the write happens only on the first run** — an
uninitialised shift register or feedback node, a `First Call?`, or a control whose value the first run changes.

### An observation that four hypotheses have now failed to explain

The very first probe of the day opened a **fresh** session and read 640 × 512. Every test since says that should be
impossible. Falsified, in order:

| hypothesis | how it died |
|---|---|
| GenICam clamping — a leftover `OffsetX` forces `Width` down | both offsets read 0 |
| write order — set `Width`, then set binning, camera divides | the string `Binning` appears nowhere in the main VI |
| the camera persists the ROI between sessions | `imaqdx_reset_test.py`: set 640 → close → open reads 1280 |
| a client that is killed leaves the ROI behind | `imaqdx_dirty_exit.py`: set 640 → `os._exit()` → next open reads 1280 |

Rather than invent a fifth story, this is recorded as **one unexplained observation**. It does not block anything: the
severity question is already settled (ROI, not binning; calibration safe).

What *is* solid corroboration that the main VI is involved: its front-panel **indicators** `Width` and `Height` hold
**640** and **512** (`tools/bench/main_vi_camera_values.py`). Those are displayed values left by the last real run, so
that run ended with the camera at 640 × 512 — the user's report, recorded inside the VI itself.

### MEASURED 2026-09-16 — **uid 9775 READS the geometry, and the size the VI WRITES is the front-panel display's**

Two questions closed in one afternoon, one by an op we already had and one from a dump already on disk. The second
began with the user saying, from memory: *"프로퍼티 노드로 아마 카메라 프레임 읽어오기 → 이후 프로퍼티 노드로
IMAQ 화면 사이즈 셋팅하는 걸로 기억함."* Both halves are now measured, and both are right.

**Half 1 — uid 9775 is a READ** (`tools/bench/diag_9775_direction.log`, main VI md5 unchanged, 37 s). `:511-515`
asked *"is uid 9775 reading or writing?"*. `OpWireSource_v5` on the two wires answers it without geometry and
without a traverse index:

| wire | source terminal | sink |
|---|---|---|
| 32937 `Height` | **`Property` uid 9775 itself** (`Is Source? = TRUE`) | one `Diagram`-owned terminal, uid 13236 |
| 32938 `Width` | **`Property` uid 9775 itself** | the same |

A terminal that drives its wire is an OUTPUT, so both property items are reads. ⚠️ **Note how long the wrong tool
kept this open:** `whats_next_to_9775.py` sorted objects by POSITION around the node and reported "three numeric
constants to its LEFT ⇒ write". That method is invalid on this VI — the diagram was Clean Up'd, so position carries
no functional meaning — and it kept the question open across two prior-art reviews. The right op existed the whole
time.

**Half 2 — the write is on diagram 97, and it is the front-panel image display, not the camera.** Entirely from
`tools/bench/main_vi_nodeterms.json` and `main_vi_netmap.json`, no LabVIEW run:

```
 [diagram 87]  9775 reads camera Height/Width ──► panel Height / Width
 [diagram 97]  30445 `Height`.Value ──┐
               30471 `Width`.Value  ──┴─► 30512 bundle ─► 11120 divide ─► wire 28798
                                                   ÷ wire 28487 = constant uid 27664, value **2**
               wire 28798 ──► 30118 `Image Area Size`   (INPUT ⇒ WRITE)
                         └──► 30422 `Draw Area Size`    (INPUT ⇒ WRITE)
```

`30118` also carries `ZoomInteger`, `Visible`, `Container Bounds`; `30422` carries `ZoomFactor`, `Visible`. The
divisor is read from the numeric-constant census already on disk (`opconstvaluen_scan.json`, 180 constants, each
with the wire it drives) — **uid 27664 = 2**, so the display area is set to **half the camera geometry**: 640 × 512
against a 1280 × 1024 camera.

**What this does and does not settle.**

- ✅ **The camera ROI is not written on this path.** The startup frame asks the camera its size; it does not set it.
  So a copy of the original does not change the acquisition geometry at start-up, and the master plan's
  1280 × 1024 budget basis is safe from *this* node.
- ✅ **The user's memory is confirmed** — read the camera frame size with a property node, then set an IMAQ size
  with a property node. The size being set is the **display area**, which is why it never showed up in any ROI test.
- ❌ **It does NOT explain the unexplained observation above.** A fresh session reading 640 × 512 is still
  unexplained; the display-size write cannot reach the camera. The two 640 × 512 figures have different causes and
  must not be conflated: one is the camera's reported ROI, the other is a display area *derived* from it by ÷2.
- ⚠️ **Not measured, and not to be asserted:** that the `Diagram`-owned sink terminals of wires 32937/32938 are the
  same panel objects as diagram 97's `Height`/`Width` property nodes. The names match and the chain only makes
  sense that way, but the terminal identities were not read. Cheapest check if it ever matters: the sink terminals'
  runtime class (`ControlTerminal`) and their `Terminal.Object` UID.
- ⚠️ **"The VI does not set the frame size" is NOT established**, and was nearly written into the plan. The peer
  review (`archive/peer/2026-09-16-uid9775-read-not-write-codex.md`) made exactly this distinction: the narrow claim
  about uid 9775 is supported, the VI-wide claim is not, because another node elsewhere could still write ROI. What
  was found on diagram 97 is a *display* write, so the VI-wide question remains open — and the cheapest definitive
  test the reviewer named is `Property Items[] → Is Write` per item, which needs no wire walking at all.

### What the front panel holds (read 2026-09-12, VI not running)

| object | kind | value |
|---|---|---|
| `Width` / `Height` | **indicator** | **640 / 512** |
| `Total Lost Frames` | indicator | 0 |
| `Missing Frames?` | indicator | False |
| `Lost Frame Message` | indicator | "Your acquisition lost frames. See the 'lost frames' display…" |
| `pixel distance (nm)` | control | 84.0 |
| `Cross length (pixels)` | control | 120.0 |
| `Frame rate` | control | 25 |
| `CamSessionOut` | indicator | `('', 0)` — the IMAQdx Session, empty while stopped |

`Width`/`Height` being **indicators** also explains the `Width&2` / `Height&2` strings in the file: the panel already
uses those two labels, so a property node's same-named terminals take the disambiguated form. It also weakens the
assumption that the property node *writes* — a node feeding these indicators would be a **read**.

### FOUND: the configuration step is diagram 87 (2026-09-12)

The targeted walk located it. **Diagram 87** carries three camera nodes, and one is the node the whole question turns on:

| uid | terminals, in order |
|---|---|
| 13962 | `error out`, `Session Out` |
| 33151 | `error out`, `Session Out` |
| **9775** | `IMAQdx Session`, `IMAQdx Session`, `error in (no error)`, `error out`, **`Height`, `Width`** |

uid 9775 is the **IMAQdx property node**, and its terminal order is **`Height` then `Width`** — which is exactly the
order the two strings appear in the VI file (`Height&2` before `Width&2`). The offline byte scan and the COM read now
agree independently, which is what the byte evidence needed: a peer review had correctly said string adjacency alone
could not establish that this node existed.

The search that found it was exhaustive rather than lucky, so the negative results are load-bearing too: all **106**
Property nodes in the VI were placed on a diagram (0 unplaced), and every diagram holding one was walked. The only
remaining blind spot is that diagrams 43 and 99 were read with `max_terms=20`, which truncates any node with more
terminals than that — `tools/bench/reread_loops_wide.py` closes it if needed.

Both geometry terminals ARE wired — `Height` to wire 32937, `Width` to wire 32938 — but each net came back with only
its own terminal on it. That is not a contradiction: `net_map` and the Step-0 diagram tree are both built from the same
`Nodes[]` walk (diagram 87's tree entry lists exactly the 14 nodes net_map found), and **front-panel terminals and
constants are not Nodes**, so the far end of each wire is simply invisible to that enumeration. Reaching it needs a
Traverse by class instead — `tools/bench/whats_next_to_9775.py`, which places every Constant near uid 9775's position
(-15780, 1017). The VI holds 301 Constants and **5763 Terminals**; at roughly a second per object the Terminal sweep
is an hour and a half, so it is deliberately skipped and the Constant sweep is run first.

**The proximity sweep narrowed it but did not settle it, and it is worth being explicit about that.** 61 objects lie
within 700 units of uid 9775. The three nearest are all numeric constants to its **left** — uid 13245 at (−131, −101),
and **uid 13598 and uid 13540**, two `DigitalNumericConstant`s at (−252, −33) and (−250, −37), i.e. essentially stacked
at the same x with a few units between them and within ~35 units of the node's own y. A pair of numeric constants
stacked immediately left of the node is exactly the shape of two values feeding `Height` and `Width`, and it matches
the user's own description — *"property node로 입력되는 상수값이거든"*, a constant fed **into** the property node.

But 61 objects in the box is not a wiring proof, and the nearest hit is not an answer. The decisive test is to read
those constants' **values**: (512, 640) would mean the VI writes the halved geometry; (1024, 1280) would mean it writes
the full frame and the halving comes from somewhere else. Either way the answer does not depend on tracing the wire.
That is what `tools/recipes/build_opconstvalue.py` is for.

**A fourth, independent line now points the same way.** [MAIN_VI_MAP.md](MAIN_VI_MAP.md) §3b, written from a visual
walk of the diagram on 2026-08-30 and long before any of this, describes the far-left initialisation frame as holding
*"`Initialize camera` (IMAQdx, `Grayscale (U8)`, **Height/Width**)"*. Diagram 87 is that frame. So the property node
belongs to camera **initialisation**, which is a step that configures rather than reports. Converging evidence, in
order of independence:

1. the user's own account — *"property node로 입력되는 상수값이거든"*, a constant fed **into** the node;
2. a visual diagram walk recorded eighteen days earlier listing Height/Width under *Initialize camera*;
3. two numeric constants stacked immediately to the node's left;
4. terminal order `Height` then `Width` matching the file's `Height&2` before `Width&2`.

That is strong convergence, and it is still **not** the wiring proof — which is exactly why the constants' values, not
more inference, are the next step.

**Still open, and it is the whole question: is uid 9775 reading or writing?** Terminal names cannot say. A *read*
explains the front-panel `Width`/`Height` indicators and would mean the VI never sets the ROI; a *write* means the VI
sets it and the value on the wire is the answer. `tools/bench/read_diagram87.py` re-reads the diagram keeping the
**nets**, so every terminal sharing a wire with `Height` or `Width` is listed — a constant or control on that net means
write, an indicator means read, and no wire at all means the terminals do nothing.

Note the frame-loss instrumentation the user remembered is real and already present: `Total Lost Frames`,
`Missing Frames?` and a lost-frame message, driven by the `LastBufferNumber` shift register seen on diagrams 19 and 43.

### What the offline byte scan established, and what it did NOT

`tools/bench/vi_strings_camera.py` reads the VI's zlib streams with no LabVIEW at all. Solid findings:

- the main VI references exactly **six** IMAQdx VIs — Open Camera, Configure Grab, Get Image, Grab, Stop Acquisition,
  Close Camera — and **none of them sets an attribute**;
- **the string `Binning` does not appear anywhere in the file**, so the main VI never writes binning. This is what kills
  the write-order hypothesis (write Width, then set binning, camera divides the width);
- the literal strings `Width`, `Height`, `Width&2`, `Height&2` are present, as are front-panel numerics stored as
  `DigNum (strict)` and read through `Value` property nodes.

A peer review (codex, `archive/peer/2026-09-12-camera-halving-attack.md`) was asked to attack this and was right on one
point: **string adjacency is not diagram connectivity**. `Width&2` sitting near the literal `IMAQdx` does not prove an
IMAQdx property node — `Width`/`Height` are also properties of panes, bounds and Image Display controls, and LabVIEW
appends `&2` to any duplicated object name. That inference is downgraded to a hint pending the COM scan.

The peer's strongest alternative — that the acquired frame is full and only the *display* is halved by an Image Display
zoom — is **ruled out by `PayloadSize`**: at 640 × 512 the driver reported 327 680 bytes rather than 1 310 720. A zoomed
display cannot change the payload. The ROI really was half.

Read 2026-09-12 from `C:\Program Files\NI\LVAddons\niimaqdx\1\vi.lib\vision\driver\IMAQdx.llb`
(`tools/bench/inspect_imaqdx.log`). Read-only: no camera was opened and nothing was acquired.

Hardware in place: **NI-IMAQdx USB3 Vision Device, VID_14FB (JAI) PID_1006** — the SP-5000M-USB, e2v Lince5M CMOS,
2560×2048, 5 µm pixels, global shutter, 62 fps at full resolution, USB3 Vision. Run today at **2×2 binning**, normally
**90 Hz**, with **150 Hz or higher wanted**. ~~No `.icd` file exists, so the attributes are set in code.~~ **CORRECTED
2026-09-25 (review `archive/peer/2026-09-25-hyp-camrate83.md`, measured by `tools/bench/diag_camrate_persist83.log`): the
camera file EXISTS — `C:\Users\Public\Documents\National Instruments\NI-IMAQdx\Data\JAI Corporation SP-5000M-USB
(#000014FB0067A270).icd` — and EVERY `IMAQdxOpenCamera` (C API or the VI) reloads it, so a rate written in one session
(150 Hz) reads 90.0009 Hz again after any close + reopen. A different rate needs the VI's own session to set it, or the
`.icd` changed (the user's decision, D-2026-09-25-05).** The camera's
onboard frame memory is not stated in any public JAI datasheet found, and was not assumed.

## Connector panes (exact, for building against)

| VI | controls | indicators |
|---|---|---|
| Open Camera | `Session In`, `Camera Control Mode`, `error in` | `Session Out`, `error out` |
| Configure Grab | `Session In`, **`Number of Buffers`**, `error in` | `Session Out`, `error out` |
| Configure Acquisition | `Session In`, `Continuous?`, **`Number of Buffers`**, `error in` | `Session Out`, `error out` |
| Get Image | `Session In`, `Image In`, `Buffer Number In`, **`Buffer Number Mode (Next)`**, `error in` | `Session Out`, `Image Out`, `Buffer Number Out`, `error out` |
| Get Image2 | the same plus `Timeout (ms)` | the same |
| Grab | `Session In`, `Image In`, **`Wait for Next Buffer? (Yes)`**, `error in` | `Image Out`, `Session Out`, `Buffer Number Out`, `error out` |
| Stop Acquisition / Close Camera | `Session In`, `error in` | `Session Out`, `error out` |
| Calculate Frames per Second | `Session In`, `Buffer Number`, `Reset Counters`, `Frames per Second Update Interval (ms)`, **`Minimum Display Update Interval (ms)`**, `error in (no error)` | **`Acquired Frames per Second`**, **`Processed Frames per Second`**, **`Images Behind`**, **`Images Missed`**, **`Update Display`**, `Session Out`, `error out` |
| Get Buffer Difference | `Previous Buffer Number`, `Current BufferNumber` | `Buffer Difference` |
| Enumerate Attributes | `Session In`, `Root`, `Visibility`, `error in` | `Attribute Information Array`, `Session Out`, `error out` |
| Enumerate Cameras | `Connected Only? (Yes)`, `error in` | `Camera Information Array`, `error out` |

## Two findings that matter more than the pane list

**1. The default couples the display to the camera's sequence.** `Get Image` has `Buffer Number Mode (Next)` and `Grab`
has `Wait for Next Buffer? (Yes)`. The parenthesised word is the DEFAULT, so **leaving the terminal unwired makes the
call wait for the next buffer in order**. A display loop wired that way must keep up with the camera; when drawing is
slow it falls behind, the ring overwrites unread buffers, and frames are lost. `Last` returns the newest buffer without
waiting, which lets a display run at its own slow rate and skip everything in between — it decouples rather than merely
throttles. Whether the main VI wires this terminal is the single cheapest thing left to check.

**2. NI already ships the instrument this project was about to build.**
`IMAQdx Calculate Frames per Second` reports `Acquired Frames per Second` against `Processed Frames per Second`, plus
`Images Behind` and `Images Missed`. That is exactly the user's own model of the failure — *the camera loop runs on its
own and frames are lost when the computer cannot keep up* — rendered as four numbers. It also carries
`Minimum Display Update Interval (ms)` in and `Update Display` out, i.e. the display-rate gate is a built-in feature
rather than something to hand-roll.

## NI's examples already are the experiment (read 2026-09-12)

Building a harness node by node was the wrong plan. `C:\Program Files\NI\LVAddons\niimaqdx\1\examples\Vision
Acquisition\NI-IMAQdx\` ships VIs that match the open questions almost exactly.

| example | nodes | controls | indicators |
|---|---|---|---|
| Basic Acquisition\\**Acquire Every Image** | 17 | `Camera Name`, `Number of Images`, **`Simulated Processing Delay (ms)`**, `Overwrite Mode`, `Percent of Images Reserved by Driver`, `Stop` | `Acquired Frame Rate`, `Processing Frame Rate`, `Images Behind`, `Images Missed`, `Buffer Number`, `Image` |
| Basic Acquisition\\**Acquire Most Recent Image** | 12 | `Camera Name`, `Stop` | `Acquisition Frame Rate`, `Buffer Number`, `Image` |
| Design Patterns\\Parallel Processing | 51, 4 While loops | `Camera Name`, `Number of Images`, 3 × `Processing Delay (s)` | `Images Processed`, `Images Behind`, `Images Missed`, `Current Buffer Number` |

Three things fall out:

**`Camera Name` is a plain string control.** The one unknown in driving a harness over COM — whether an IMAQdx Session
refnum can be set from Python — simply does not arise.

**`Simulated Processing Delay (ms)` turns the whole question into one sweep.** Set it to 0 and the VI reports the
camera's ceiling at the current 2×2 binning. Set it to 2.5 ms and it stands in for the tracking kernel; 7 ms for kernel
plus the estimated `t0`. Sweeping it while watching `Images Missed` answers the question this project actually cares
about — **how large a per-frame processing budget can the rig afford before it starts losing frames** — without touching
the main VI at all, so none of its complexity can confound the result.

**`Acquire Most Recent Image` has no `Images Missed` indicator at all.** With `Last` semantics the concept does not
apply: the loop never falls behind because it never queues. The contrast between the two panels is itself the argument
for decoupling the display.

## Consequence for the measurement plan

[t0-instrumentation-plan.md](t0-instrumentation-plan.md) Step 3 gets much cheaper: a harness that opens the camera,
configures a grab and loops `Get Image` + `Calculate Frames per Second` reports the acquisition ceiling and the
keep-up margin directly, with no hand-written timing code.

The order to run, all without the main VI so its complexity cannot confound the result:

1. **Ceiling.** Acquire with no tracking and no display; read `Acquired Frames per Second`. At 2×2 binning the sensor's
   62 fps full-frame figure suggests the ceiling may sit below the wanted 150 Hz, in which case no software change can
   reach the target and the goal itself has to move. Bandwidth is not the limit: 1280×1024 at 8 bit and 150 fps is
   196 MB/s, comfortable for USB3.
2. **Acquisition cost alone.** `Processed` against `Acquired`, and `Images Behind`, give term A of the A+B+W budget.
3. **The display question, isolated.** Add the display to the same harness and compare `Buffer Number Mode` = `Next`
   against `Last`, with and without a display-rate gate. If `Last` plus a gate holds `Images Missed` at zero, the live
   view can be restored as it stands; if frames still drop, the cost is CPU and UI-thread contention and an external
   viewer is justified rather than merely attractive.
4. **Ring depth.** `Number of Buffers` is the jitter margin. 100 buffers of 1.3 MB is 130 MB against 64 GB of RAM, so
   depth is nearly free; what the main VI currently requests should be read and compared.

## MEASURED 2026-09-28 (card 121-1, ring-buffer P1) — all five buffer-number modes, C API, no LabVIEW

Script `tools/bench/p1_bufmode_121.py`, log `tools/bench/p1_bufmode_121.log` (`BGRUN END rc=0 after 144s`, gates 51/0),
raw rows `tools/bench/p1_bufmode_121.json`. 10 ring buffers, 1280×1024, contract applied after open (ExposureAuto Off,
ExposureTime 5555 µs read back), 4 s per cell after 5 discarded frames. "Delay" is a WAIT (`time.sleep`, 1 ms timer
period), i.e. a LabVIEW `Wait (ms)`, not busy processing. `BufferNumber` mode asked for `previous + 1`.

**Modes defined by the installed header**: `C:\Program Files (x86)\National Instruments\NI-IMAQdx\include\NIIMAQdx.h:178-185`
(NI-IMAQdx 26.3) — `Next` 0, `Last` 1, `BufferNumber` 2, `Every` 3, `LastNew` 4 (+ `Guard`). The claim in
`archive/peer/2026-09-25-m8b-replay-prep-75-fact.md:58` that the public header lists only three is true of an old
third-party copy, not of this install. NI's meaning of each value is quoted from the NI pages cited at `:54`/`:58` of that
archived fact search (web tools were not available to this card, so no fresh fetch).

| mode | 90 Hz, delay 0: calls/s · median GetImageData · CPU | 150 Hz, delay 0 | delay 1 ms (90 / 150) calls/s | delay 15 ms (90 / 150) delivered/s · gaps/skipped |
|---|---|---|---|---|
| `Next` | 90.0 · 11.11 ms · 1.2 % | 149.9 · 6.67 ms · 2.3 % | 89.9 / 149.9 | **45.0 / 49.9** (exactly ½ and ⅓) · 179/179, 199/398 |
| `Last` | **25 112 · 0.038 ms · 100 %** (100 088 duplicates; distinct 90.0/s) | 25 203 · 0.038 ms · 100 % | 595 / 585 (duplicates 2 022 / 1 739) | 64.5 / 64.7 · 101/101, 258/339 |
| `BufferNumber` | 90.0 · 11.11 ms · 1.2 % | 149.9 · 6.67 ms · 2.7 % | 90.0 / 149.9 | 64.4 / 64.4 · 20/100, 64/337 |
| `Every` | 90.0 · 11.11 ms · 0.4 % | 149.9 · 6.67 ms · 2.3 % | 89.9 / 149.9 | 64.2 / 64.6 · 20/100, 64/336 |
| `LastNew` | 90.0 · 11.11 ms · 0.4 % | 149.9 · 6.67 ms · 5.5 % | 89.9 / 149.9 | 64.2 / 64.5 · 101/101, 257/339 |

- **Every mode except `Last` blocks inside `GetImageData` until a buffer it has not returned exists** (median = the frame
  period at delay 0; ≈ period − 1 ms at delay 1), so those loops run at exactly the camera rate with 0 duplicates, 0 gaps.
- **`Last` never waits**: at delay 0 it re-reads the newest buffer 25 000×/s and holds one core at 100 % (process CPU
  / wall = 1.004); a 1 ms wait cuts that to ~590 calls/s and <1 % CPU with no lost distinct buffers.
- When the consumer is slower than the camera (15 ms wait), **no mode returned an rc error**; the camera rate stayed within
  0.3 % of the set rate in every cell. `Next` fell to exactly ½ (90 Hz) / ⅓ (150 Hz) of the camera; `BufferNumber`
  (asked for prev+1) and `Every` jumped forward in steps of ~5 buffers (20 gaps / 100 skipped at 90 Hz) and delivered
  the same 64 Hz as `Last`/`LastNew`, which skip one buffer at a time. `BufferNumber` therefore returned a buffer other
  than the one requested without an error — the returned number must be read, not assumed.
- 150 Hz was reachable under the contract exposure (5555 µs < 6667 µs period); set 149.993 Hz, measured 149.7–149.9.
- Cleanup: rate restored to 90.0009 Hz, session closed rc 0, a fresh open/close afterwards rc 0/0 at 1280×1024, 90.0009 Hz.
