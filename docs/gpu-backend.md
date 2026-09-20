---
type: reference
status: current
date: 2026-09-09
tags: [docs, gpu]
---

# GPU/CUDA backend — plan, environment, findings (started 2026-09-07)

User request: reproduce the bead-tracking kernel on the GPU (CUDA). Acceptance: |dx|,|dy| < 1e-6 px, |dz| < 1e-6 um
per bead per frame against the CPU kernel on the fixture (tools/bench/fixture_compare_results.jsonl, 10,043 frames,
verified == .tra to 0.0). The algorithm steps, constants and array sizes stay those of the VIs (rule 1a); only the
executor changes. CPU (PARALLEL_kernel_v3) and GPU backends are kept side by side with the same connector pane.

## Steps
1. **Spec extraction (in progress).** Wiring of every diagram of the analysis VIs and the calibration loader VIs, read
   headlessly from claudeDev\SPEC copies (`tools/bench/spec_read.py`, `spec_read_more.py`, results
   `spec_wiring.json` / `spec_wiring_more.json`; inventories `spec_inventory*.json`). Constants are not readable by the
   current ops (Constant.Value 634AC00 needs a Constant-typed ref) — settled by FP defaults, the C port, and numeric
   sweeps against the reference.
2. **NumPy float64 reference** (`tools/gpu/ref_numpy.py`, one function per VI) matched to the reference on all frames.
3. **CUDA port**: CuPy prototype (float64, cuFFT) → C++/CUDA DLL with a LabVIEW-friendly ABI (handles as in the Saleh
   code's datatypes.h) once the toolkit is installed.
4. **LabVIEW wrapper subVI** (Call Library Function Node, same pane as the kernel) added to HARNESS_compare as a
   third kernel; tolerance check + timing on the fixture.
5. Main-VI copy swap (script), user's live run.

## Environment (2026-09-07 20:1x)
| item | value |
|---|---|
| GPU | GeForce RTX 2060, 6144 MiB |
| driver | 457.51 (2020-11; supports CUDA <= 11.1) — **update to 616.64 pending the user's UAC click** |
| CUDA toolkit / nvcc | not installed |
| CuPy | not installed; NumPy 1.26.4, Python 3.10 |
| OS | Windows 10 Home 19045; shell is NOT elevated |

Driver 616.64 WHQL (2026-09-03, 984 MB, RTX 20-series + Windows 10 supported, Authenticode = NVIDIA Corporation) is at
`C:\Users\KimLab\Downloads\nvidia_616.64\`; `tools\gpu\install_nvidia_driver.ps1` installs it silently (display driver
only, no reboot) and needs one UAC approval. Two unattended attempts timed out (UAC auto-cancels after ~2 min).
Note: Parsec host runs on this PC — a remote viewer loses the picture for a few seconds during the install.

## Finding: the Saleh-lab C/CUDA port of these very subVIs is on disk
`zz_LabView VI\GPU Track Algo (Saleh Lab)\` — "GPU Tracking Demo" (2013). Attribution: code by Shawn Tabrizi, advised
by Bob Lansdorp, Omar A. Saleh lab, UC Santa Barbara; BSD 2-clause (BSDlicense.txt in the folder); paper: Lansdorp,
Tabrizi, Dittmore, Saleh, "A high-speed magnetic tweezer beyond 10,000 frames per second", Rev. Sci. Instrum. 84,
044301 (2013), https://pubs.aip.org/aip/rsi/article-abstract/84/4/044301/358204 ; public repo
https://github.com/shawntabrizi/GPU-Accelerated-Magnetic-Tweezer-Tracking-CUDA . The `CPU Tracking\*.h` files are a
function-per-subVI port (avgxycross ↔ tracking-average x,y in cross, prepavgprofile ↔ tracking-prep avgx,y profiles,
findavgprofilecenter(+finddelta, quadfit) ↔ tracking-find avg profile center (+ fit parabola), calculateradialprofile,
prepradinprof ↔ Tracking-prep I of r, fitpreptocal, phaseinnbhd, quadfitphase) written "to match the results of the
subVI". The GPU version is float32 and changes the algorithm (integer start positions, Croquette's discretization
fix run twice, no bandpass in XY) — **not** usable as-is under rule 1a. Use: reading aid + ABI/handle layout example.
Known C-vs-VI differences already seen in the wiring: the VI's XY find-center takes the 'cosine window for hilbert'
input (the C port skipped it: "RESULTS INDICATE NOT NEEDED"); the VI uses General Polynomial Fit (not a closed-form
normal-equation solve); rounding of the arm start ('To Long Integer' = round-half-even vs C truncation) — all settled
numerically against the reference.

## Wiring-read facts so far (2026-09-07 20:4x, from spec_wiring.json)
- fit parabola: n = '# of points for parabola' (default 5); start = argmax − floor(n/2) (Array Max&Min first max);
  X = start+i, Y = subset; General Polynomial Fit order 2; output = −b/(2a) in array-index units.
- prep avg profiles: base = (Σ profile[i] + Σ profile[cross − i]) / (2·N) for i = 0..N−1 (the "last" points are
  indexed cross − i, so i = 0 reads index `cross` = out of range = 0 — a quirk to be confirmed numerically, then kept);
  prepped = (profile − base) × real-space cosine window.
- prep I(r): mirrored = reverse(profile with element `index` deleted) ++ profile (length 2·half − 1 = 119); FFT-type
  subVI → × cosine bandpass (complex) → inverse subVI; corkscrew = subarray from index (A + B − 1) to the end (the
  right half, r increasing, no conjugation); prepped I(r) = Re(corkscrew).
- phase in neighborhood: 5 slices from index − 2; weight = |c_live| × amp_cal; θ = arg(c_live / c_cal);
  phase_i = Σ wθ / Σ w. quadratic fit to phase: General Polynomial Fit (order 2) of offset(phase), evaluated at 0,
  added to the index.

## 2026-09-07 21:0x — NumPy reference status
- Kernel inputs captured over COM (`tools/bench/capture_harness_inputs.py` → `tools/gpu/harness_inputs.npz`): the array
  of cal clusters IS readable by GetControlValue (7-tuple per bead; complex arrays arrive as (re, im) pairs); the two
  cosine windows come from running the SPEC copy of `make both cosine bandpass.vi` (cross length 120). Cluster facts:
  forget radius 23 (bead 1) / 18 (beads 2-5) = the third value of the per-bead triplet in cal002's tail; z step is a
  SGL 0.1 (0.10000000149…); cosband has 120 elements (multiplied element-wise with the 119-long spectrum → LabVIEW
  truncates to 119); ampl/cork/real are 60 × (60 − forget).
- **XY matches to 5e-8 px** on frame 4, all beads (ref_numpy `Params(orient="xy")`): the sub-image array is the
  transpose of image[y][x] (rows = x) — the average VI's "along x" profile is the per-row mean, and the VI's index
  arithmetic (rows ← x centre) only works with that layout. The 3-frame Croquette shift (magnitude of the IFFT, Rotate
  by half, parabola −b/2a, phase ramp on the squared+windowed spectrum) is confirmed by the match; the C port's
  "real part" and "no window" variants are NOT what the VI does.
- Z still off (index right for 3/5 beads, z index off by 1.5 slices) → black-box per-VI comparison running
  (`tools/bench/blackbox_z.py`).

## 2026-09-07 21:3x — NumPy reference matches (frame 4: |dx|,|dy| 5e-8 px, |dz| 2.5e-6 um); full-fixture check running
How the last two Z discrepancies were found — by script-built **subVI harnesses** (`tools/bench/subvi_harness.py`:
FPTARGET base + drop_subvi + create_control/create_indicator on every terminal; Create Control on an OUTPUT terminal
yields an UNWIRED control, detected by the wire count and replaced by an indicator; reentrant subVIs cannot be Run over
COM — error 6535 / a 60 s hang — but a harness that calls them can):
- `tracking- quadratic fit to phase nghbrd.vi`: the General Polynomial Fit is **weighted, Weight = [2, 4, 5, 4, 2]**
  (identified from 10 designed inputs, residual 1.5e-9; an unweighted fit was 1e-3..1e-2 slices off). Y = offsets
  −2..2, X = phases, order 2, P(0) added to the index.
- `tracking-calculate radial profile-openv2.vi`: the profile is **single precision** (every LabVIEW value is exactly
  representable in float32; delta-image probes match double-precision accumulation to 1e-8, the const-100 image shows
  SGL rounding at 1e-7 relative). The rounding order is not emulated (user 2026-09-07: "z 축에서 1e-4 차이는
  괜찮아") — NumPy accumulates in double and rounds the output to float32.
- COM cannot set a complex-array control (pairs, VARIANT forms, numpy: all leave it empty) → the prep-I(r) and phase
  harnesses could not be driven directly; not needed after the two fixes above.
Kernel-input facts used by the reference (all from `harness_inputs.npz`): cross 120, h = I32(0.6·cross) = 72
(sub-image 144×144 from rect [x−h, y−h, x+h, y+h]), arm = 10, n_end = I32(cross/4) = 30 with the `cross − i`
out-of-range quirk, parabola 5 points, the sub-image is image[y][x] (standard), starting x/y are I32 (round half even).
Runner: `tools/gpu/check_all.py` (state fed back as the LabVIEW harness did; TOL 1e-6 px / 1e-4 um).

## 2026-09-08 00:4x — three-way timing benchmark (user's framing: sequential VI / CPU-parallel VI / GPU DLL, in LabVIEW)
PARALLEL_kernel_v3 structure (headless read, `tools/bench/v3_structure.json`): top level = the ORIGINAL four-fold code
(For Loop uid 248 over 4-packs with two 2-bead kernels `Track 2 beads` per iteration, diagram 6; Case Structure uid 107
= the 0/1/2/3-bead remainder cases, diagrams 2-5, four more kernels) whose outputs are dangling, plus the script-built
P=4 loop uid 3447 (one 1-bead reentrant kernel, diagram 1) fed by Decimate 3848 and feeding Interleave 3835 → the
connector pane. The dead code still executed, so timing v3 as-is would have counted sequential + parallel.
`tools/bench/timing_chain.py` deletes 248 + 107 on a copy (6 SubVIs gone, ExecState 1), swaps it into
PARALLEL_kernel_v3.vi (backup PARALLEL_kernel_v3_withdead.vi), builds HARNESS_base/seq/par (HARNESS_compare minus
kernels) and runs `run_timing.py`: kernel time = harness median − base median (COM Run + IMAQ ReadFile + windows cancel).
Toolchain for the GPU DLL: installers downloaded + signature-checked (driver 616.64, VS Build Tools 2022, CUDA 12.6.3);
`tools/gpu/install_gpu_toolchain.ps1` needs one UAC click at the PC (two unattended attempts timed out). DLL source:
`tools/gpu/cuda/mt_track.cu` (fused kernels; C API mt_gpu_init / set_bead / set_bounds / track / free).
Bead-good bounds: only the upper z bound is evidenced by the recording (index 59 → bad; z_hi_margin 3 assumed, z_lo 2 and
the x/y bounds = h assumed) — to be pinned by probing the kernel harness before the DLL is trusted for the good flag.

## 2026-09-08 09:1x — GPU harness in LabVIEW: what stalled, what works

- **HARNESS_gpu.vi** (script-built, `tools/recipes/build_harness_gpu.py`): loader + IMAQ Create/ReadFile + make both cosine
  bandpass + ImageToArray → the donor CLFN (uid 2471, path in = "Debug\GPU Tracking.dll" relative to the VI). Controls/labels
  in `tools/bench/harness_gpu_labels.json`. The loader's own `file (use dialog)` control must be primed (run HARNESS_loadcal
  with the cal path first — the harness does not wire it; error 1430 otherwise).
- **Stall, reproduced twice:** `gscript.connect_terminals` (OpConnect_v0 = Terminal.Connect Wire) INTO the CLFN returns, then
  LabVIEW spins one core and the next VI Server call never returns (08:43 array-of-clusters into t32; 09:06 DBL array into
  t28). Peer review (codex, archive/peer/2026-09-08-clfn-cluster-spin.md): no NI evidence for a compile hang on nested-handle
  adapt-to-type parameters; and the machine refuted it too — the saved VI carries the cluster wire and runs in 28 ms. The
  erdosmiller name route (`gscript.wire(..., "CallLibrary", 0, "Y Output")`) wired the same node instantly at build time.
- **DLL entries:** the donor's decorated export now resolves to `GPUTracking_auto`: cluster route (`GPUTracking_lv`, LabVIEW
  handle layout, pack 8) when a non-empty 'Array Cal Cluster' is wired, else `GPUTracking_file` (`cuda/cal_file.inc`: reads
  the .cal itself, host double DFT; == LabVIEW's clusters ≤ 6.7e-7, z effect 4.7e-9 µm on 300 bead-frames; path arrives in
  the C-string parameter). C-string contract (from the peer review): the DLL writes ≤ 59 bytes + NUL; callers pass ≥ 60 bytes
  (the timing script passes 64 spaces; a path is ≥ 83); bytes are the system code page.
- First LabVIEW call of the deployed DLL (09:04): reached the DLL, cluster route selected (n=5), rejected with
  `size mismatch ... yout=0` because the Hilbert-window wire (W → 'Y Output') was missing from the saved file.

## 2026-09-08 09:5x — the CLFN's parameter types are FIXED (donor signature); DLL adapted, harness untouched

Wires into 'Y Output' (1-D DBL win_h) and 'Z Output' (bool good flags) were removed as bad wires three times, even with the
placeholder indicators deleted. COM round-trip proves the types are the donor's: 'X Array 3' returns 708.4→708 (I32 1-D),
'X Output' accepts ((1.5,2.5,0.0),) (2-D DBL), 'Y Array' 3.7→4 (I32) — exactly the decorated export
`?GPUTracking@@YAHHHHHHPAPAUArray1dInt@@0HHPAPAUImage@@PAPAUArray2d@@22PAPAUArrayCluster@@PAPAUBoolArray@@PADPAPAUArray1d@@@Z`
(X/Y Array I32[], Image, X/Y/Z Output 2-D DBL, cluster array, bool array, char*, DBL[]). The CLFN configuration is not
reachable by VI Scripting, so the DLL took the donor's types instead (final contract, `mt_track.cu` + `cal_file.inc`):

| CLFN parameter | type (fixed) | use |
|---|---|---|
| X Array | I32[] | unused (placeholder control 'X Array 3') |
| Y Array | I32[nb] | 'pos in cal image' in / out ('Y Array' / 'Y Array 2') |
| Cross Size | I32 | cross (loader 'cross size') |
| Array of Images | U8 2-D | image (Omars IMAQ ImageToArray) |
| X Output | DBL 2-D, rows·cols = 3 nb | **x,y,z in / out** ('X Output' / 'X Output 2') |
| Y Output, Z Output | DBL 2-D | unused (empty placeholders) |
| Array Cal Cluster | cluster array | calibration (loader); empty ⇒ file route via Error Message |
| Bead Is Good Array | bool[nb] | good flags in / out ('Bead Is Good Array' / '… 2') |
| Error Message | C string ≥ 60 B | status out (file route: cal path in) |
| Test Array | DBL[cross] | win_rs (make both cosine bandpass 'Real-space cosine window') |

win_h has no parameter left, so the DLL computes it: `0.5(1−cos(2π(i+half)/(2·half)))` for i ≤ half, 0 beyond (the VI's
LOW=−half..HIGH=half clip — the first, unclipped attempt was 0.19 px off; the clip found by comparing with the captured array).
Verified: max |Δwindow| 8.5e-8 vs LabVIEW's array; effect on the reference kernel over 400 bead-frames |dx| 3.0e-9 px,
|dy| 4.9e-9 px, |dz| 6.7e-8 µm. Fake-handle test (`tools/gpu/test_dll_lv2.py`): all four entries == LabVIEW frame 4 to
2.5e-6 µm; 41-frame chained sweep |dx| 2.4e-7 px, |dz| 2.7e-6 µm, 0 index flips, 1.58 ms/frame. The timing script converts
'x,y,z array' to the 2-D control when `harness_gpu_labels.json` has `xyz_2d`.

## 2026-09-08 10:0x — handle layout READ FROM BYTES (tools/gpu/cuda/dump.inc → %TEMP%\mt_track_dump.bin → decode_dump.py)

Two more wrong guesses (error 1097 = the DLL crashed on a bad pointer) ended by dumping what LabVIEW actually passes, guarded
by IsBadReadPtr. Verified layout (LabVIEW 2026 64-bit, CLFN "Array Handle" parameters):

| parameter | handle payload |
|---|---|
| X Array (I32 1-D) | `{I32 n; I32 d[n]}` (data at +4) |
| Test Array (SGL 1-D) | `{I32 n; SGL d[n]}` (data at +4; win_rs[0]=0 so the pad question was settled by d[1]) |
| X Output (SGL 2-D) | `{I32 rows; I32 cols; SGL d[]}` |
| Bead Is Good (bool 1-D) | `{I32 n; U8 d[n]}`, TRUE arrives as 0xFF when set over COM |
| Array of Images (U8 2-D) | `{I32 rows; I32 cols; U8 d[]}` — arrived **0×0**: Omars IMAQ ImageToArray (itself a CLFN with a `subRegion` input) returns an empty array for the default 'Optional Rectangle'; fixed by a control on that terminal set to (0,0,1280,1024) |
| Array Cal Cluster | header `{I32 n; pad}`; element **56 B** = `{I32 forget; pad; DBL z step; H cosband; H ampl; H cork; H real; I32 # slices; pad}` |
| cosband | DBL 1-D `{I32 n; pad; DBL d[]}` (data at +8) |
| ampl, real | DBL 2-D `{I32 rows; I32 cols; DBL d[]}` |
| cork | CDB 2-D `{I32 rows; I32 cols; (DBL re, DBL im)[]}` |

So the calibration is DOUBLE precision in this VI (the Saleh C header's `float zstep` / float arrays described their 2013
32-bit build, not the donor VI's wire types); only X/Y/Z Output and Test Array are SGL. The DLL's structs (`mt_track.cu`) now
match this table; `tools/gpu/test_dll_lv3.py` builds fake handles with exactly this layout (frame 4 == LabVIEW to 2.5e-6 µm).
Rule for next time: **dump first, guess never** — the dump costs one call.

## 2026-09-08 11:2x — ROW 3 DONE (archive/bench-2026-09-08-gpu-in-labview/REPORT.md)

HARNESS_gpu runs the DLL inside LabVIEW; 200 chained frames match the reference (x,y 1e-6 px, z 2.9e-6 µm). Kernel time
≈ 9.5 ms/frame (gpu − base; 6.8–10.5 across runs), the DLL itself 5.2–5.4 ms inside LabVIEW vs 1.4–1.7 ms from Python — all
phases uniformly ~3.5× slower and the cudaEvent GPU time 3.3 vs 0.9 ms. Ruled out: GPU clock ramp-down (Python with 5–20 ms
gaps: 1.66 ms), the CLFN's UI-thread execution (ui=1; a DLL-owned worker thread changed nothing). Open: a per-launch host delay inside the LabVIEW process — CPU thread
contention, priority, or per-process GPU scheduling; NOT LabVIEW drawing on the GPU (panels are CPU/GDI-rendered; user's
correction 2026-09-08). At 5 beads the CPU-parallel VI (2.43 ms) stays the fastest.
Image path: ImageToArray (rectangle control) → OpBuildBA_v0-placed Build Array (2-D→3-D) → CLFN; big-array placeholder
indicator wires removed (−1.7 ms). DLL status string carries `t= u= k= d= e= ui=` diagnostics (run_timing.py collects them).
Next for a competitive GPU row: fewer launches (the frame is ~25 GPU API calls: 9 kernels, 6 cuFFT execs, 9 memcpys; fuse the per-bead pipeline into one kernel with in-kernel FFTs → 1 launch + 2 memcpys). Use **cuFFTDx** (NVIDIA MathDx, header-only
device-side FFT made for exactly this; MathDx 25.12 supports CUDA 12/13; sizes 2–64 all + specific larger sizes, float ≤ 32768):
120 = 2³·3·5 is standard, 119 = 7·17 must be checked with cufftDeviceCheckDescription — fall back to an in-kernel 119-point DFT
(≈14k multiply-adds) if unsupported. Sources: https://docs.nvidia.com/cuda/cufftdx/index.html , https://developer.nvidia.com/cufftdx-downloads, pinned/zero-copy image, CLFN 'Any Thread?' via the CallLibrary
property (636D403), and the per-launch-delay experiments (one-launch micro-benchmark in both processes, worker thread priority, Python with busy threads).

## 2026-09-08 12:0x — ROOT CAUSE of the 3.7× in-LabVIEW slowdown: GPU power state (P8), not LabVIEW

Discriminating chain (all measured, archive/bench-2026-09-08-gpu-in-labview/):
- fused single-launch kernel (`cuda/fused.inc`, one block per bead, in-kernel two-stage DFTs 120 = 10×12, 119 = 7×17;
  |fused − classic| 2.3e-13, LabVIEW reference unchanged) → still 6.3 ms inside LabVIEW, GPU-event 4.4 ms vs 1.1 offline →
  launch count exonerated;
- CPU probe inside the DLL (2 M-iteration FP64 loop): 6.11 ms in LabVIEW = 6.19 ms in Python → host thread at full speed;
  priority class / affinity identical (Normal, all cores); nvidia-smi: LabVIEW holds only a compute context (no graphics);
- **nvidia-smi sampling during a low-duty loop (15 ms gaps) from Python: P8 / 360 MHz dominant, and the same DLL takes 5.5 ms
  (GPU event 3.4) — identical to the LabVIEW numbers.** 1365 MHz / 360 MHz = 3.8× = the observed ratio. The GPU's clock governor
  keeps the card in P8 when ~1 ms of work arrives every ~15 ms; earlier Python "gap" tests were too short after tight loops.
- Fix options: (a) NVIDIA Control Panel → Manage 3D settings → Program Settings → LabVIEW.exe → Power management mode =
  "Prefer maximum performance" (persistent, per app) or the global setting; (b) `nvidia-smi -lgc 1365,1365` (admin, resets on
  reboot); (c) DLL keep-alive spin kernel (`mt_gpu_keepalive`, opt-in via MT_GPU_KEEPALIVE=1) — NOT recommended: cudaMalloc/
  cudaFree and (observed) the work stream can wait on it; left opt-in only.
- cuFFTDx: evaluated and dropped for now (MathDx 25.6 needs CUDA ≥ 12.8 + CUTLASS, preliminary MSVC, FP64 size 119 unsupported;
  peer review archive/peer/2026-09-08-fused-kernel-cufftdx-plan.md). The two-stage in-kernel DFT reaches cuFFT's GPU time
  (event 0.89 ms both) at 5 beads.

## 2026-09-09 — the limiter is the GPU MEMORY clock at any idle gap; keep-alive attempts failed; clock lock required

`tools/gpu/regime_test.py` (Python, DLL-internal timers + nvidia-smi 200 ms sampling of pstate / SM / mem clocks / PCIe):

| regime | DLL t | upload | GPU event | sampled state |
|---|---|---|---|---|
| tight loop | 1.12 ms | 0.33 | 0.64 | P2 1905 MHz SM / 6801 MHz mem |
| 2, 5 or 15 ms gaps | 5.50 ms | 1.71 | 3.40 | **P8 360 MHz SM / 405 MHz mem** |
| 15 ms gaps + keep-alive v2 (0.3 ms compute kernel per ms) | 4.7–4.9 | 1.1 | 3.4 | SM sometimes P2, mem stays 405 → no gain |
| 15 ms gaps + keep-alive v3 (+8 MB D2D copy per ms) | 6.6 | 2.8 | 3.4 | P8, and it steals bandwidth |

Any idle gap ≥ 2 ms drops the card to P8; the memory clock falls 17× and every phase (upload, image reads, kernels) slows
~3.5×. The NVIDIA "prefer maximum performance" per-app profile does not apply to a CUDA-only process (verified: LabVIEW idle →
P8). An infinite spin kernel (v1) stalled the work stream under WDDM. **Working fix = SM clock lock (admin): `nvidia-smi -lgc
1365,1905`** (resets at reboot; register as a logon task with highest privileges for the rig). Memory clock lock (`-lmc`) is
NOT supported on the RTX 2060 (verified 2026-09-09), so the upload stays ~3× slower than in a tight loop; final in-LabVIEW
DLL time 2.12 ms, gpu − base 5.41 ms. Keep-alive stays opt-in only.
Chain 17 (DLL 1.73 ms inside LabVIEW) happened while another workload kept the clocks up — the same 1.1–1.7 ms is what the
lock should give in LabVIEW; chain 18 without it: 5.13 ms.

## 2026-09-09 13:3x — ROW 3 with OUR interface: **1.14 ms/frame** (archive/bench-2026-09-09-gpu2-in-labview/REPORT.md, INDEX row 15)

HARNESS_gpu2 (script-built: IMAQ Create → ReadFile → GetImagePixelPtr → one CLFN `mt2_track_simple`, DBL in/out, no image copies)
vs HARNESS_base, 200 chained frames, 5 beads: gpu2 5.70 − base 4.56 = **1.14 ms/frame** (DLL-internal 1.62 = upload 0.38 + kernel
1.11 + sync); outputs == reference (x,y 4.9e-7 px, z 2.9e-6 µm, 0 flips, 0 good mismatches). Three-way FINAL (ms/frame above base):
sequential 8.15 · CPU-parallel v3 2.43 · GPU Saleh node 5.14 · **GPU v2 1.14**. Per-frame traffic is now the image upload, one
kernel launch and 3×nb doubles back; everything fixed (calibration, windows, twiddles, buffers) lives on the GPU from `mt2_open`.

## 2026-09-09 — GPU interface v2: OUR design (user: "Saleh꺼 따라하지 마 … 최적으로 짜보자고")

Goals: one DLL call per frame, zero LabVIEW-side image copies, DBL in/out, persistent context, clocks handled inside the DLL.

**C API (`mt2_*`, all exported, C calling convention, 64-bit):**

| function | parameters | notes |
|---|---|---|
| `int64 mt2_open(const char* cal_path, int cross, int flags, char* status, int status_len)` | returns a context handle (0 on error) | loads the .cal, builds calibration + windows on the GPU, allocates all buffers once; `flags` bit0 = keep-alive on |
| `int mt2_set_image(int64 ctx, uint64 pixel_ptr, int line_width, int width, int height)` | IMAQ buffer pointer + stride | registers the buffer (cudaHostRegister → pinned DMA) the first time; no copy in LabVIEW |
| `int mt2_track(int64 ctx, int nb, const double* xyz_in, const uint8* good_in, double* xyz_out, int32* idx_out, uint8* good_out, char* status, int status_len)` | one launch per frame (fused kernel) | xyz arrays are DBL[3 nb] (Array Data Pointer); x,y in are the previous frame's DBL results, rounded inside exactly as the kernel VI does (round-half-even) |
| `int mt2_close(int64 ctx)` | frees everything, stops keep-alive | |
| `const char* mt2_last_error()` | | |

**LabVIEW side (one new subVI, script-built, CLFN configured by script):** `IMAQ GetImagePixelPtr.vi` → pixel pointer (U64) +
line width → `mt2_set_image`; `mt2_track` with the kernel VI's own connector types (x,y,z DBL array in/out, good flags,
cal index). No ImageToArray, no Build Array, no SGL encoding. Calibration path from the loader's file path (or clusters later).

**CLFN configuration by script:** NI's own import-wizard library `resource\importtools\sharedlib\VI\Block Diagram\Call
Library Node\Call Library Node.lvlib` (Method/Create.vi, Attribute/Parameter Info.vi, Function Name.vi, Library Path.vi,
Calling Convention.vi, Reentrant.vi, Parameter Terminals.vi) wraps the CallLibrary scripting properties (636D400/401/402/403/409).
Peer (codex): creation also possible with New VI Object style "Call Library Function Node" + class CallLibrary; Parameter Info
enum encodings are undocumented → learn them from NI's library / by reading an existing node, never guess.

### Plan: scripted CLFN configuration (2026-09-09 02:0x)

Facts (machine): COM cannot set an array-of-clusters control even with scalar fields (Parameter Info.vi probe: stays empty);
NI's `Parameter Info.vi` cluster (strings recovered from the VI): `Parameter Name` (string), `Num Dimensions` (I32),
`Parameter Type` (ring: Numeric, Array, String, Waveform, Digital Waveform, Digital Table, ActiveX, Any, Instance Data Pointer,
Void), `Numeric Type` (numeric code, values unknown), `Param Passing` (By Value, Pointer To Value), `Array Passing` (Array Data
Pointer, Array Handle, Array Handle Pointer), `String Passing` (C String Pointer, Pascal String Pointer, String Handle, String
Handle Pointer), `Adapt Format`, `ActiveX Types` (ActiveX Variant Pointer, IDispatch* Pointer, IUnknown* Pointer),
`Const (unused)` (bool), `Minimum Size` (I32). Enum numeric values = ring order (to be verified with the Prototype method).

Op design `OpCLFNBuild_v0` (one op, typed refnums only, no TMSC): Open VI Ref → PN VI.Block Diagram → NI `Method/Create.vi`
(diagram, position) → `Library Path.vi` / `Function Name.vi` / `Calling Convention.vi` / `Reentrant.vi` (set, from string/ring
controls) → `Parameter Info.vi` (get) → Flatten To String → indicator `flat params out` (layout sample) AND Unflatten From String
(binary string control `flat params`, type = the read-back array) → `Parameter Info.vi` (set) → `Parameter Terminals.vi` →
`Terms[]` count indicator. Python composes the flattened bytes (LabVIEW flatten: big-endian, I32 array count, per element:
I32-prefixed string, I32, enums as U16/U32 per the sample, U8 bool, I32). `Numeric Type` codes and the enum values are
confirmed by reading the `Prototype` method (636D000) string after each set.
Creators to wrap (erdosmiller): `Create Flatten to String.vi`, `Create Unflatten from String.vi` (recipe pattern = build_opbuildba.py).

**Result 2026-09-09 11:5x — NI `Create.vi` KILLS LabVIEW when the `Parameter Info` global is EMPTY** (ACCESS_VIOLATION read at 0,
LabVIEW.exe+0x578A41, GDI frames on the stack; minidumps d8556cd8 / 70426c46; variants: 4 globals / +Function Dec / +empty Parameter Info /
kernel32+GetTickCount all crash in 0.3 s, Path-only (error 1077 before the node is configured) survives; our DLL never loaded). Peer
(codex, archive/peer/2026-09-09-clfn-create-crash-empty-paraminfo.md): element 0 of Parameter Info is the RETURN-VALUE record, a CLFN
always has one; NI forum 4147512 documents a return-name blanking / node-width bug when Parameter Info is rewritten. With the global
filled first (OpCLFNParams_v0, below) Create.vi succeeds and the fresh node reports our 15 records — hypothesis confirmed.

**`Parameter Info` element layout (decoded from the FGV's 7.x type string, tools/bench/paraminfo_td.json; flattened = big-endian):**

| # | field | flattened |
|---|---|---|
| 1 | Parameter Name | I32 length + bytes |
| 2 | Num Dimensions | I32 (LabVIEW reports 1 for scalars) |
| 3 | Parameter Type | U16 enum: Numeric 0, Array 1, String 2, Waveform 3, Digital Waveform 4, Digital Table 5, ActiveX 6, Any 7, Instance Data Pointer 8, Void 9 |
| 4 | Numeric Type | U16 enum: I8 0, I16 1, I32 2, I64 3, U8 4, U16 5, U32 6, U64 7, SGL 8, DBL 9, PTR INT 10, PTR UINT 11 |
| 5 | Param Passing | U16: By Value 0, Pointer To Value 1 |
| 6 | Array Passing | U16: Array Data Pointer 0, Array Handle 1, Array Handle Pointer 2 |
| 7 | String Passing | U16: C String Pointer 0, Pascal String Pointer 1, String Handle 2, String Handle Pointer 3 |
| 8 | Adapt Format | U16: By Value 0, Pointer To Value 1 |
| 9 | ActiveX Types | U16: ActiveX Variant Pointer 0, IDispatch* Pointer 1, IUnknown* Pointer 2 |
| 10 | Const (unused) | U8 bool |
| 11 | Minimum Size | **string** (I32 length + bytes; "" = none) |

Array = I32 count + records (27 B each with empty strings). Composer: `tools/gpu/clfn_params.py --compose <hex>` (PARAMS = return
value + the 14 `mt2_track_simple` arguments). **OpCLFNParams_v0** (tools/recipes/build_opclfnparams.py): FGV Get → Flatten
(`data string`, `type string (7.x only)` — populated without any convert flag) | Unflatten(`binary string`, type = Get output) →
FGV Set (`operation` 1). Read-back of the 523-byte array is byte-identical. Chain: `clfn_sample.py --params <hex> [--flat <hex>]`.

**A scripted CLFN on `GPU Tracking.dll` is BROKEN (ExecState 0) — the SPACE in the file name** (probe tools/bench/clfn_break_probe.py,
2026-09-09 12:1x, fresh FPTARGET copies, node alone on the diagram): kernel32/GetTickCount fine; our DLL at `...\Debug\GPU Tracking.dll`
broken with every parameter list and every export; the same bytes as `...\Debug\mt_track.dll` (same Program Files directory) fine; a
dependency-free `ver sion.dll` at a spaced path fine; ours (+cufft beside) at `Temp\mt spaced dir\GPU Tracking.dll` broken. Also found on
the way: the deployed DLL (01:22) predated mt2.inc (no `mt2_*` exports) — `tools/bench/gpu2_chain.py` now deploys
tools/gpu/cuda/mt_track.dll to BOTH names (`mt_track.dll` for our interface, `GPU Tracking.dll` for the Saleh-node harness).
`gscript.build_clfn(target, location, dll, fn, flat_hex)` is the one-call wrapper (Params → Pre → Build, junk Invoke purged).

**Abort-safety (2026-09-09 14:0x — user: the experiment VI is normally stopped with LabVIEW's Abort button, so `mt2_close` never
runs).** LabVIEW's Abort stops the VI, not the process: the CLFN call always returns (~2 ms), the DLL stays loaded and the GPU
context survives, so nothing is left half-written. Two nets were added for what Abort does skip:

- **Single-context policy** — `mt2_open` closes any context this DLL still holds before creating a new one (`g_mt2_live`;
  `mt2_close` also clears the one-node entry's cache). The rig runs one tracking loop, so nothing legitimate is ever closed.
- **Keep-alive idle timeout** — the keep-alive thread parks itself when no track call has arrived for `mt_gpu_keepalive_idle(ms)`
  (default 2000) and wakes on the next call; `mt_gpu_keepalive_state()` reports 0 off / 1 running / 2 parked. An aborted run can no
  longer leave the GPU busy-looped at +7 W.

Verified `tools/gpu/test_abort.py` (log tools/bench/test_abort.log): 12 open-without-close cycles → GPU memory drift **0 MB**, every
run reproduces the reference; keep-alive state 1 → 2 (2.5 s idle) → 1 (next track).

**Never `cudaHostRegister` LabVIEW's IMAQ buffer** (HARNESS_gpu2 run 1, 13:2x: 32.5 ms/frame LabVIEW-side vs 1.7 ms DLL, plus 3 slice
flips and a 0.3 px deviation after frame ~50 while offline runs were exact): IMAQ frees/re-allocates the image buffer, so a pinned
mapping goes stale at the same address and every address change costs an unregister+register of the whole frame. v2 now copies the
strided rows into a DLL-owned pinned staging buffer (`cudaMallocHost`, ~0.4 ms upload for 1280×1024) — offline 61 frames 2e-7 px,
0 flips after the change.

**A LabVIEW BOOLEAN array needs an "Adapt to Type" parameter — no explicit CLFN type takes one** (2026-09-09, building the
drop-in GPU kernel whose pane carries `Bead is good? array in` as a Boolean array). The Numeric Type ring has no Boolean, and a
Boolean-array wire into an Array/U8 parameter is created and then **deleted by Remove Bad Wires**, leaving a required argument
unwired and the VI broken — which looks like a mysterious "broken before I did anything" state. Measured in isolation
(`tools/bench/bool_wire_probe.py`, log bool_wire_probe.log): DBL→DBL wires 0→1→1 (kept), BOOL→U8 wires 1→2→**1** (removed),
I32→I32 1→2→2 (kept). Fix: Parameter Type **`Any`** (= the dialog's "Adapt to Type") with Adapt Format **By Value**
(= "Handles by Value") — the DLL then receives a LabVIEW array HANDLE, and a Boolean array's payload is one byte per element,
so `(*h)->d` is exactly the `uint8*` the rest of the code wants (`mt2_track_simple_b` in mt2.inc, composer `PARAMS_B` /
`paraminfo_mt2_b.hex`). The handle also carries the length, so `nb` needs no Array Size node.

**A scripted CLFN's ARGUMENT inputs act as REQUIRED until wired** (probes M01-M14/N1-N4 + tools/bench/clfn_wire_probe.py, 13:0x):
return-only node runnable; return + any one argument → ExecState 0 with no attribute error; a control wired to the argument's
INPUT terminal (t6 of the 2-record node) turns ExecState to 1 (peer ranking archive/peer/2026-09-09-clfn-scripted-node-broken-with-arguments.md:
terminal datatype committed only through wiring / the dialog's OK). Consequence for recipes: wire EVERY argument input (control or
wire) before judging ExecState, and never use an absolute ExecState guard while inputs are still unwired.
Then `HARNESS_gpu2` = loader path + IMAQ Create/ReadFile + `IMAQ GetImagePixelPtr` + ONE CLFN `mt2_track_simple(cal_path, ptr,
line_width_bytes, width, height, nb, xyz_in, good_in, xyz_out, idx_out, good_out, status, len)` (the DLL opens/caches the
context by cal path) — no ImageToArray, no Build Array, DBL in/out. Terminals wired by name (`g.wire`, never connect_terminals
into a CLFN).

## 2026-09-17 MEASURED — WHERE the full-fixture GPU/CPU divergence lives (localisation only; no interpretation)

`tools/bench/gpu_n1_deltas.py` (log `tools/bench/gpu_n1_deltas.log`, **8/8 gates pass**, `BGRUN END rc=0 after
121s`), raw per-frame deltas `tools/bench/gpu_n1_deltas.json` (3.66 MB, 10 043 rows). **No LabVIEW is involved**:
ctypes → `tools/gpu/cuda/mt_track.dll` + the recorded fixture + `tools/bench/fixture_compare_results.jsonl`
(the CPU-kernel reference, `== .tra` to 0.0); gates G0a/G0b assert no `LabVIEW.exe` at start or end.
The run reproduces `gpu_n1_full_fixture.log` exactly (gate G2: 4.13e-06 / 3.13e-05 / 1.28e-05 px·px·µm, 1 flip),
so this is the SAME comparison, only with every frame kept. Seeding is unchanged from `test_mt2.py`: frame *k* is
seeded from the **CPU reference** of frame *k−1* (cal xy after a lost bead), so **deltas do not accumulate**.
Tolerances: 1e-6 px for x,y (`decisions.md:38`); 1e-4 µm for z (user, 2026-09-07).

### Per bead, per axis — max |Δ|, first exceedance, how many frames exceed

`k` = row index 0…10042; `f` = the recorded TIFF frame number. Maxima below EXCLUDE the one flipped bead-frame
(as `test_mt2.py`'s `worst` does) and the frames where the reference marks the bead lost.

| bead | max\|Δx\| (px) | max\|Δy\| (px) | max\|Δz\| (µm) | frames exceeding x / y / z | first exceedance |
|---|---|---|---|---|---|
| 0 | 1.803e-07 @k3641 (f4243) | 1.870e-07 @k5333 (f6255) | 4.347e-06 @k1965 (f2272) | 0 / 0 / 0 | — |
| 1 | 4.857e-07 @k98 (f106) | 2.066e-07 @k2820 (f3257) | 6.787e-06 @k5243 (f6131) | 0 / 0 / 0 | — |
| 2 | 3.237e-07 @k685 (f742) | 8.989e-08 @k1046 (f1179) | **1.279e-05 @k3281 (f3801)** | 0 / 0 / 0 | — |
| 3 | 1.177e-07 @k742 (f799) | 1.632e-07 @k660 (f715) | 3.788e-06 @k8350 (f9863) | 0 / 0 / 0 | — |
| **4** | **4.131e-06 @k10029 (f11811)** | **3.135e-05 @k10025 (f11807)** | 3.832e-06 @k250 (f265) | **10 / 9 / 0** | **k10023 (f11805)** |

**The whole x/y acceptance failure is bead 4, in the last 25 rows of the recording.** Split at the first bead
loss (k10018 = f11797, the boundary STATUS's "Say it exactly" already uses):

| window | max\|Δx\| | max\|Δy\| | max\|Δz\| | frames exceeding |
|---|---|---|---|---|
| **k < 10018** (the first 10 018 frames) | **4.857e-07** (bead 1) | **4.677e-07** (bead 4) | 1.279e-05 µm (bead 2) | **0** |
| k ≥ 10018 (f11798–f11824) | 4.131e-06 (bead 4) | 3.135e-05 (bead 4) | 3.430e-06 µm (bead 2) | 10 |

In the k ≥ 10018 window beads 0–3 stay ≤ 2.598e-07 px (x) and ≤ 8.888e-08 px (y).

### The one flip — k1679, f1937, bead 4, and it is NOT in the loss region

One calibration slice apart (`zstep` 0.1 µm): CPU index 26, GPU index 25, **CPU z 2.547769 µm vs GPU z 2.543102 µm,
Δz −4.667e-03 µm (−4.7 nm)**. The ±3 neighbours agree to ≤ 1e-6 with identical indices:

| k | f | CPU z (µm) / idx | GPU z (µm) / idx |
|---|---|---|---|
| 1676 | 1934 | 2.560960 / 26 | 2.560960 / 26 |
| 1677 | 1935 | 2.574721 / 26 | 2.574721 / 26 |
| 1678 | 1936 | 2.577262 / 26 | 2.577262 / 26 |
| **1679** | **1937** | **2.547769 / 26** | **2.543102 / 25** |
| 1680 | 1938 | 2.540745 / 25 | 2.540745 / 25 |
| 1681 | 1939 | 2.560959 / 26 | 2.560960 / 26 |
| 1682 | 1940 | 2.565392 / 26 | 2.565393 / 26 |

CPU z falls 2.5773 → 2.5478 → 2.5407 across k1678–k1680, i.e. the CPU itself changes index 26 → 25 at k1680; the
GPU changes it one frame earlier. No other flip exists in 10 043 × 5 bead-frames.

### Clustering — one bead, one region, alternating rows; and the lost-bead frames

- **10 frames exceed any axis; every one of them is bead 4** (`beads_involved: [4]`), and all lie in
  **k10023…k10041 = f11805…f11823**. Every "run" has length 1: the exceedances sit on the **odd** rows
  f11805, 11807, 11809, 11811, 11813, 11815, 11817, 11819, 11821, 11823.
- The **13 recorded lost-bead rows** (measured here, matching `archive/bench-2026-09-07-fixture/REPORT.md:49-51`)
  are the **even** ones: f11798, 11800, 11804, 11806, 11808, 11810, 11812, 11814, 11816, 11818, 11820, 11822,
  11824. **`exceed_k_in_lost_rows` is EMPTY** — no exceedance lands on a row the recording marks lost; they
  **interleave** with them, one frame off, exactly the alternation the fixture REPORT describes.
- Against frame 10 018: **all 10 exceedances have k ≥ 10018** (`exceed_k_ge_first_lost = exceed_k_ge_10018 = 10`),
  i.e. all of them are after the first bead loss, inside the 11797–11824 end-of-recording stretch where the
  REPORT says all five beads are lost simultaneously. **Scattered within that stretch, absent everywhere else.**
- The flip (k1679) is 8 364 rows before that stretch and is unrelated to it.

### Run-to-run reproducibility on this card — BIT-IDENTICAL

Two full identical passes in the same process (RTX 2060, P0, SM 1365 MHz, mem 7000 MHz; clock lock registered):
**0 of 150 645 output doubles differ, max|A−B| = 0.000e+00**, and the `idx` and `good` arrays are equal as well
(gate G4). DLL-internal median 1.62 ms in both passes. **The divergence is deterministic, not run noise.**

OPEN (judgement, deliberately not answered here): whether this is acceptable against `decisions.md:38`, and what
causes bead 4's behaviour in the all-beads-lost tail and the single early flip.
