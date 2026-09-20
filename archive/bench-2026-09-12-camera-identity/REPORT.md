---
type: narrative
status: historical
date: 2026-09-12
tags: [archive]
---

# Camera identity, frame-rate ceiling, and the "first run halves the image" fault

**Date:** 2026-09-12 · **Rig:** magnetic tweezers, UNIST · **Hardware state:** rig disassembled, motors detached,
camera connected. Operating all four instruments was cleared by the user for this state
(*"ASI stage, PI stage, rotor, camera 모두 작동해도 괜찮아"*); this work touched the camera only.

## 1. What the test was

Three questions had been blocking the acquisition work, and none of them could be answered because the camera's
IMAQdx name was unknown:

1. **What is the camera actually set to?** The rig runs 2×2 binning, normally 90 Hz. Nothing else was verified.
2. **Is 150 Hz physically reachable?** The user wants 150 Hz or higher. The sensor's published figure is 62 fps at
   full resolution, which left open the possibility that the target was unreachable and the goal itself had to move —
   a much more important answer than any software optimisation.
3. **Why does the first run halve the image?** User report: *"코드 처음 가동하면 카메라 사이즈가 절반으로 줄어버리더라"*,
   *"두 번 작동하면 사이즈 원상복구되"*, *"property node로 입력되는 상수값이거든, 그래서 그런지 이미지 값도 작게 보여"*.
   The severity split mattered: a **ROI** clamp shrinks the field of view and leaves calibration intact, whereas a
   **binning** change doubles nanometres-per-pixel and makes every distance from a halved run wrong by 2×.

## 2. Why the method changed — and the 40 minutes that bought the lesson

The first plan was to drive NI's shipped example `Acquire Every Image.vi` over COM. It failed three times, always the
same way: the example's `Camera Name` is an **IMAQdx Session control that reads back as the tuple `('', 0)`**, not a
string. `('', 0)` is *truthy* in Python, so a guard written as `if not cam:` passed, the name was never written, and the
example ran with no camera — which opens a **modal dialog** that blocks every subsequent COM call until LabVIEW is
killed. `tools/bench/camera_dump.py` died at the 1202 s watchdog behind exactly that dialog.

The fix was to stop going through LabVIEW. **The C API has no front panel, so it has no dialog.**
`tools/bench/imaqdx_ctypes.py` and `tools/bench/imaqdx_limits.py` call `niimaqdx.dll` directly with ctypes: enumerate,
open, read attributes and attribute *ranges*, close. Total runtime under two seconds, no dialogs, no LabVIEW.

The first thing it returned was the answer to the blocker: **the camera is `cam1`, not `cam0`.** Every earlier attempt
had guessed `cam0`.

## 3. Environment

| | |
|---|---|
| driver | NI-IMAQdx, `C:\Windows\System32\niimaqdx.dll`, called from 64-bit Python via ctypes |
| camera | JAI Corporation **SP-5000M-USB**, serial `000014FB0067A270`, SuperSpeed (USB 3.0) |
| LabVIEW | not involved in the measurement (deliberately) |
| method | read-only for §4; §6 writes only `Width`/`Height`/`OffsetX`/`OffsetY`, never binning |

## 4. Results — the camera as found

| attribute | value |
|---|---|
| `SensorWidth` × `SensorHeight` | 2560 × 2048 |
| `WidthMax` / `HeightMax` | 2560 / 2048 — **unbinned units**, unlike `Width`/`Height` |
| `BinningHorizontal` / `BinningVertical` | **2 / 2** (`JaiBinningGainEnable` False) |
| `Width` × `Height` | 1280 × 1024 after a fresh open (640 × 512 on the first probe — see §6) |
| `OffsetX` / `OffsetY` | 0 / 0 |
| `PixelFormat` | 8 Bit Monochrome |
| `PayloadSize` | 1 310 720 B full frame, 327 680 B halved |
| `AcquisitionFrameRate` | 90.0009 Hz (`AcquisitionFrameRateRaw` 11 111 = frame **period in µs**) |
| `ExposureTime` / `ExposureMode` / `ExposureAuto` | 1909 µs / Timed / **Continuous** |
| `AcquisitionMode` / `TriggerMode` | Continuous / Off — free-running |
| `AutoShutterControlExposureMax` | 15 000 µs |

Full dump: [`imaqdx_attributes.txt`](imaqdx_attributes.txt) (198 attributes at Advanced visibility).

## 5. Results — the ceiling: **247.95 Hz**, so 150 Hz is reachable

Read as attribute *ranges*, not inferred:

```
Width  range (min 8, max 1280, increment 8)
Height range (min 8, max 1024, increment 2)
AcquisitionFrameRateRaw (period us)  min 4033  max 8000000
   => ceiling 1e6 / 4033 = 247.95 Hz          floor 0.125 Hz
AcquisitionFrameRate  min 0.125  max 247.9544
```

**The wanted 150 Hz has 65 % headroom in the camera.** The published "62 fps" figure is the full-resolution number and
does not apply at 2×2 binning. The goal does not have to move; what 150 Hz costs is a per-frame budget of **6.67 ms**
for everything the computer does, and **4.03 ms** at the ceiling.

**One caveat.** `ExposureAuto` is **Continuous** and `AutoShutterControlExposureMax` is 15 000 µs. Exposure sits at
1909 µs today, which fits inside even the 4033 µs ceiling period — but if the field dims, auto-exposure will walk
exposure up and the achievable rate falls with it; at the 15 ms cap the camera alone would be limited to ~66 Hz. A rate
target is only meaningful with exposure bounded.

## 5b. Results — the per-frame budget, and what it has to pay for

`tools/bench/camera_budget_sweep.py` runs NI's `Acquire Every Image` experiment through the C API: a ring of buffers,
fetch the **next** buffer in sequence, burn a settable delay pretending to process it, count the gaps in the returned
buffer numbers. No LabVIEW, so no LabVIEW overhead is folded into the answer — this is the floor. 1280 × 1024, 2 × 2
binning, 10 buffers, 4 s per point.

| camera set to | frame period | **budget (zero frames lost)** | first failing delay |
|---|---|---|---|
| 90.00 Hz | 11.11 ms | **10 ms** | 12 ms → 45.0 Hz processed, 179 missed |
| 149.99 Hz | 6.67 ms | **6 ms** | 7 ms → 75.0 Hz processed, 299 missed |
| 200.00 Hz | 5.00 ms | **3 ms** | 4 ms → 1 missed in 798 (marginal); 5 ms → 100.1 Hz |
| 246.97 Hz | 4.05 ms | **3 ms** | 4 ms → 123.9 Hz processed, 487 missed |

**Budget ≈ frame period − 1 ms**, and the failure is a **cliff, not a slope**: every failing row processes at exactly
half the acquired rate (150 → 75, 200 → 100, 90 → 45) while `acquired` never falls. Overrunning by 0.3 ms costs every
second frame, not 5 % of frames.

**Acquisition itself costs 0.12 ms/frame** — median 122.6 µs, p90 149 µs, p99 206 µs, max 218 µs over 300 calls that
each returned a *new* buffer number (`tools/bench/camera_copy_cost.py`). That is 10.70 GB/s for the 1.31 MB payload, a
believable memcpy rate, and **2 % of the 150 Hz budget**. It is paid in every possible architecture, so no loop
restructuring can win it back and none needs to. The measurement exists because the `Last`-mode delay-0 row *appears*
to give 42 µs/call — 31 GB/s, far too fast — and timing only the calls that actually advanced the buffer number shows
why: the 42 µs calls copied nothing, returning the same newest buffer repeatedly.

**At 150 Hz the 6.00 ms budget must cover:** the CPU-parallel tracking kernel at 2.43–2.87 ms (INDEX rows 15–18) **plus
a single PI serial round trip at 2.56 ms** (`tools/bench/serial_roundtrip.ps1`) = **5.06 ms**, leaving under 1 ms for
the display, file writes and front-panel updates — and MOV/VEL do *two* round trips. One serial read costs as much
budget as the whole tracking kernel. That is the quantitative case for taking the serial read and the display off the
frame loop: it returns ~2.5 ms, the difference between 150 Hz and 200 Hz.

**`Last` instead of `Next` turns the cliff into a slope.** At 150 Hz, 8 ms of work per frame gives 74.9 Hz processed on
`Next` but **123.0 Hz on `Last`**, with `acquired` steady at 149.5 in every row — a slow consumer on `Last` never makes
the camera wait, it skips. So a display loop on `Last` cannot drag acquisition down; the only remaining question for
the live view is CPU and UI-thread contention, not frame blocking.

**Ring depth is not a lever.** 10 / 50 / 100 buffers all pass at 6 ms and collapse at 7 ms. Expected: a consumer
permanently slower than the camera cannot be rescued by a deeper ring, and this sweep applies a *constant* delay, so it
tests exactly the steady-state case where depth provably cannot help. Depth remains cheap insurance against occasional
long frames (100 × 1.31 MB = 131 MB of 64 GB) — it just does not move the budget.

## 6. Results — the halving fault

**The first probe found the camera at 640 × 512 with binning still 2 × 2 and both offsets 0.** Two consequences, one of
them reassuring:

- **Calibration is safe.** Binning was unchanged, so nanometres-per-pixel was unchanged. The halved frame is a smaller
  *field of view*, not coarser pixels, and distances measured during a halved run are not wrong. The worse of the two
  hypotheses is dead.
- **Offsets were zero**, which falsifies the GenICam clamping hypothesis (`Width ≤ MaxWidth − OffsetX`) that was the
  leading explanation going in.

A second open minutes later read 1280 × 1024, so `tools/bench/imaqdx_reset_test.py` tested the transition directly:

| phase | observation |
|---|---|
| 1. open, read as found | 1280 × 1024, PayloadSize 1 310 720 |
| 2. write `Width`=640, `Height`=512 (binning untouched) | **rc = 0, silently accepted** → 640 × 512, PayloadSize 327 680 |
| 3. close, re-open, read | **1280 × 1024** |
| 4. restore | left at 1280 × 1024 |

**`IMAQdxOpenCamera` resets the ROI.** So the user's "the second run restores it" is the *driver*, not the second run:
every run is handed a full frame, and the halving is something the first run does after opening. The camera accepts a
half-size ROI **with no error at all**, which is why the fault never surfaced as one.

That leaves a sharp constraint: *if the VI wrote a fixed constant, the second run would halve it too.* So either the
written value is not a fixed constant, or the write happens only on the first run — an uninitialised shift register or
feedback node, a `First Call?`, or a control the first run changes.

### One observation four hypotheses have failed to explain — recorded, not papered over

The first probe of the day opened a **fresh** session and read 640 × 512. Everything measured since says that should be
impossible:

| hypothesis | how it died |
|---|---|
| GenICam clamping — a leftover `OffsetX` forces `Width` down | both offsets read 0 |
| write order — set `Width`, then set binning, camera divides it | `Binning` appears nowhere in the main VI's file |
| the camera persists the ROI between sessions | `imaqdx_reset_test.py`: set 640 → close → open reads 1280 |
| a killed client leaves the ROI behind | `imaqdx_dirty_exit.py`: set 640 → `os._exit()` → next open reads 1280 |

No fifth story is offered. This is logged as an open observation; it blocks nothing, because the severity question is
already settled (a ROI, not binning — calibration safe).

**Independent corroboration that the main VI is involved:** its front-panel *indicators* `Width` and `Height` hold
**640** and **512** (`tools/bench/main_vi_camera_values.py`, VI not running). Those are values the last real run
displayed, so that run ended with the camera halved — the user's report, recorded inside the VI.

### The main VI's camera-related front panel

| object | kind | value |
|---|---|---|
| `Width` / `Height` | **indicator** | **640 / 512** |
| `Total Lost Frames` / `Missing Frames?` | indicator | 0 / False |
| `Lost Frame Message` | indicator | "Your acquisition lost frames. See the 'lost frames' display…" |
| `pixel distance (nm)` | control | 84.0 |
| `Cross length (pixels)` | control | 120.0 |
| `Frame rate` | control | 25 |
| `CamSessionOut` | indicator | `('', 0)` |

Two consequences. First, `Width`/`Height` being **indicators** explains the `Width&2`/`Height&2` strings — the panel
already owns those labels, so a property node's same-named terminals take the disambiguated form. Second, it weakens
the assumption that the property node *writes*: a node feeding these indicators would be a **read**. Direction is what
the diagram scan is walking the VI to establish.

The frame-loss instrumentation the user remembered is real and already built: `Total Lost Frames`, `Missing Frames?`
and a message, driven by the `LastBufferNumber` shift register visible on diagrams 19 and 43.

### The configuration step is diagram 87 — found by exhaustive search, not by luck

Walking 170 diagrams was never going to finish (net_map costs ~8 s per node). The method that worked, and which is
reusable for any "where is node X in the main VI" question:

1. **one Traverse pass per class** gives every Property node's UID (106 of them);
2. cross-reference Step 0's `diagram_tree_main.json` (diagram → node UIDs) to **place** each one — 107 s total, with
   **0 nodes unplaced**, so the coverage is provably complete;
3. walk only the 38 diagrams that actually hold a property node, ordered cheapest-first by node count.

Result — **exactly one node in the whole VI touches camera geometry**:

| diagram | uid | terminals, in order |
|---|---|---|
| 87 | 13962 | `error out`, `Session Out` |
| 87 | 33151 | `error out`, `Session Out` |
| **87** | **9775** | `IMAQdx Session`, `IMAQdx Session`, `error in (no error)`, `error out`, **`Height`, `Width`** |

uid 9775 is the IMAQdx property node, and its terminal order **`Height` then `Width`** matches the order the strings
appear in the VI file (`Height&2` before `Width&2`). Two independent methods — an offline byte scan and a COM diagram
read — agree, which is what the byte evidence needed after the peer review correctly refused to accept string
adjacency as proof that the node existed.

**Still open: read or write.** Terminal names cannot say; the wires can. `tools/bench/read_diagram87.py` re-reads the
diagram keeping the nets, so whatever shares a wire with `Height`/`Width` identifies the direction — a constant means
write (and its value is the answer), an indicator means read (and the VI never sets the ROI), no wire means the
terminals do nothing at all.

### Offline evidence from the VI file (no LabVIEW)

`tools/bench/vi_strings_camera.py` inflates the VI's zlib streams:

- the main VI references exactly **six** IMAQdx VIs — Open Camera, Configure Grab, Get Image, Grab, Stop Acquisition,
  Close Camera — and **none of them sets an attribute**;
- **`Binning` appears nowhere in the file**, killing the write-order hypothesis (write Width, then set binning, camera
  divides the width);
- `Width`, `Height`, `Width&2`, `Height&2` are present, alongside front-panel numerics stored as `DigNum (strict)` read
  through `Value` property nodes.

## 7. Peer review (a failed prediction triggered it)

Two predictions failed in sequence — GenICam clamping (falsified by zero offsets) and the binning write order
(falsified by the absent `Binning` string) — so a peer was dispatched **to attack**, not to confirm:
[`archive/peer/2026-09-12-camera-halving-attack.md`](../peer/2026-09-12-camera-halving-attack.md).

It was **right** on one point and the finding is adopted: *string adjacency is not diagram connectivity*. `Width&2`
sitting near the literal `IMAQdx` does **not** prove an IMAQdx property node — `Width`/`Height` are properties of panes,
bounds and Image Display controls too, and LabVIEW appends `&2` to any duplicated object name. That inference is
downgraded to a hint pending the COM diagram scan.

Its strongest alternative — the acquired frame is full and only the *display* is halved by an Image Display zoom — is
**ruled out by `PayloadSize`**: at 640 × 512 the driver reported 327 680 bytes instead of 1 310 720, and a zoomed
display cannot change the payload. The ROI really was half.

## 8. Non-results, logged

- `tools/bench/camera_dump.py`, 2026-09-12: killed by the watchdog at 1202 s behind a modal dialog caused by the empty
  camera name. No data.
- `tools/bench/camera_ceiling.py`, two attempts before the name was known: same failure mode. No data. The guard bug
  (`if not cam:` against a truthy `('', 0)`) is now fixed and the harness refuses to start rather than open a dialog.
- `tools/bench/camera_config_scan.py` first launch: classified nodes by traversing the VI once per class — 13
  whole-hierarchy traversals — and produced its first line only after ~13 minutes. Stopped and relaunched without the
  classification pass; the JSON checkpoint let it resume rather than restart. LabVIEW handle count after the kill:
  34 833 against the ~31 500 fresh-start baseline, consistent with the main VI's hierarchy being loaded.

## 9. What changed because of this

- Camera name `cam1` is now a verified constant in `tools/bench/camera_ceiling.py`, which also verifies the write and
  aborts rather than opening a dialog.
- The 150 Hz target is **confirmed feasible** and the per-frame budget it implies (6.67 ms) is now a number the
  loop-multiplication design can be held against.
- The halving is **not a calibration risk**, which downgrades its urgency relative to the frame-rate work.
- Facts folded into [`docs/camera-acquisition-facts.md`](../../docs/camera-acquisition-facts.md).

## 10. Scripts

| file | what it does |
|---|---|
| `tools/bench/imaqdx_ctypes.py` | enumerate cameras; dump all attributes at three visibility levels |
| `tools/bench/imaqdx_limits.py` | read attribute *ranges* (the ceiling); optional `--restore` to full frame |
| `tools/bench/imaqdx_reset_test.py` | the open/close ROI-reset experiment (§6) |
| `tools/bench/vi_strings_camera.py` | offline zlib string scan of the .vi — IMAQdx VI references and attribute names |
| `tools/bench/camera_config_scan.py` | headless COM scan of the main VI's diagrams for the camera nodes |
