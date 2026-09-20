---
type: narrative
status: historical
date: 2026-09-10
tags: [archive]
---

# TRACK_kernel_v1 — one tracking subVI whose setting picks CPU-parallel or GPU: build and functional verification

Date 2026-09-10 03:4x–05:1x · rig PC (LabVIEW 2026 26.3.1f1 64-bit, RTX 2060, SM clock locked 1365 MHz by the logon task) ·
fixture cal002, 5 beads, 60 slices, 1280×1024 U8 frames · reference = the LabVIEW tracking kernel's own `.tra` output on the
same frames. Zero GUI: every VI in this report was built and tested by script (tools/recipes, tools/bench).

## Why

User, 2026-09-09: *"최종적으로는 subvi를 만들어서 내가 셋팅에 따라 cpu parallel 혹은 gpu를 쓸건지 정할 수 있으면 좋겠어"*, and
*"내 생각에는 앞으로도 계속 case structure는 사용해야 할 것 같은데"*. The deliverable is therefore a subVI with the tracking
kernel's own connector pane (so it can replace the kernel at its single call site in the main VI) containing a Case Structure:
frame 0 = `PARALLEL_kernel_v3` (bit-identical to the original computation, INDEX row 12), frame 1 = `GPU_kernel_v1`
(INDEX row 16). Computation-preserving by construction — the new VI only routes the pane's controls and indicators.

## What had to be built first

1. **OpBuildCase_v1** — a Case Structure creator Python can drive. erdosmiller `Create Case Structure.vi` wants terminal
   REFNUMS for `Selector` and `Inputs`; COM cannot make refnums, so v0 raised an error-1055 dialog on every run. v1 takes
   control NAMES and resolves them inside LabVIEW (`Get Controls.vi` ×2 + Index Array). Two facts cost most of the session:
   `OpBuildIA_v0`'s Index Array arrives UNWIRED (six "which source terminal" attempts chased that; the fix is one
   wire-by-name to its `array` input), and `Frames` is a STRING ARRAY of frame names that must match the selector's frame
   count (`["0, Default","1"]` for a numeric selector; an integer or `[]` trips error 1302 inside the library, an 8 s dialog).
   Functional test (case_v1_test.log / case_v1_frames2.log): +1 case, +2 diagrams, +3 wires, ExecState 1, 0.1 s, no dialog.
2. **OpMakeDefault_v0** — VI method `Default Values:Make Current Default` (ID 3F3). The ActiveX interface has no such method
   and a `SetControlValue` on a loaded subVI does not reach its calls (the first backend-1 attempt ran the CPU frame).

## How TRACK_kernel_v1 was assembled (build_track_kernel_v1.log, 106 s)

Copy of PARALLEL_kernel_v3 (same pane) → diagram stripped → a selector control `index` (I32) made by `create_control` on a
throw-away Index Array → `build_case(selector="index", frames ["0, Default","1"])` → the two kernels dropped into the frames
→ the 10 pane controls wired into each kernel by name (`wire_control`: first frame +2 wires = tunnel + inner wire, second
frame +1 = tunnel reused) → the 3 pane indicators wired from each kernel (`wire_indicators`, same +2 / +1 pattern) →
3 nodes, 40 wires, 14 tunnels, ExecState 1, saved 17,061 B. `index` is NOT on the connector pane (no connector-pane op yet):
the backend is the control's saved default. Shipped default: **0 = CPU**.

## Functional verification (track_check2.log, 50 chained frames, HARNESS_base / par / gpuk / track, saved defaults, fresh LabVIEW per run)

| backend (default of `index`) | DLL log growth | track worst dev vs reference | track kernel ms/frame | par | gpuk |
|---|---|---|---|---|---|
| 0 (CPU frame) | +51 lines = the gpuk row's own 50 (+1 header); **track added none** | **0.00** (bit-identical, like par) | 2.25 | 2.47 | 3.50 |
| 1 (GPU frame) | **+102** = gpuk 51 + **track 51** | **2.69e-6 µm in z** = exactly gpuk's | 3.40 | 1.96 | 3.52 |

Three independent signals agree: the DLL's own per-frame log, the output deviation signature (0 vs the GPU's known
2.7e-6 z rounding), and the kernel time. Frame "0, Default" is the CPU kernel, frame "1" is the GPU kernel.

Timing caveat: this run was noisy (base sd 19–26 ms; the machine was busy), so the ms values above are functional evidence
only — the like-for-like timing rows remain INDEX rows 15–16 (CPU-par 2.4–2.7, GPU drop-in 2.65–3.19, GPU v2 1.14 ms/frame).
A quiet-machine repeat of base/par/gpuk/track is the obvious follow-up.

## A measurement lesson (track_check.log vs track_time.log)

The first check touched TRACK_kernel_v1 through VI Server (`GetVIReference` + `SetControlValue`) before timing it, and the
track row cost **11–22 ms/frame** instead of ~2. Untouched, in a fresh LabVIEW: track 1.62 vs par 2.76 ms in the same run.
The touch loads the subVI's front-panel data space and every call then refreshes it. Protocol now: configure (values →
OpMakeDefault_v0 → save), restart LabVIEW, then time. Recorded in docs/NAMES.md.

## How the user switches the backend

Open `TRACK_kernel_v1.vi` (user.lib\claudeDev), set `index` (0 = CPU-parallel, 1 = GPU), Edit ▸ Make Current Values Default,
save. By script: `gscript.make_default(TRACK, {"index": 1})`. Not yet done: putting `index` on the connector pane so the main
VI can drive it with a wire (needs a connector-pane op), and the frame-delay run in the working copy's real acquisition loop
(that VI initialises the motor and the piezo — waits for the user).

## Files

track_check.log (first check: backend switch failed, +9 ms lesson) · track_time.log (untouched timing) · track_check2.log +
track_check2_results.json (the verification above) · mt_gpu_frames_track2_*.txt (DLL per-frame log) · build_track_kernel_v1.log
· case_v1_test.log, case_v1_frames2.log (OpBuildCase_v1 contract) · recipes build_track_kernel_v1.py, build_opbuildcase_v1c.py,
build_opmakedefault.py · harness driver track_check_chain2.py · peer review archive/peer/2026-09-10-opbuildcase-v1-ia-unwired.md.
