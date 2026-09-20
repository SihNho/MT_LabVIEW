---
type: reference
status: current
date: 2026-09-13
tags: [docs, gpu]
---

# Will the GPU kernel still work if the PC / GPU changes?

> User's question, 2026-09-13: *"만약 내가 나중에 디바이스를 옮겨서 gpu 버전이 바뀐다고 해도 너가 지금 만들 커널 사용에
> 문제가 없을까"* — which is the same standing reason the codebase was split in two: *"언제든지 pc가 바뀔 여지가 있으므로"*.
>
> **Short answer: our own kernel is portable. cuFFT is not, and cuFFT is the part that breaks first.**
> Measured on this machine, not inferred.

## What was measured

Machine: RTX 2060 (compute capability **7.5**), driver **616.64**, CUDA Toolkit **12.6.3**, `nvcc` emits cubins for
`sm_50 … sm_90` only.

| # | test | command | result |
|---|---|---|---|
| 1 | is PTX in our DLL? | `cuobjdump --list-ptx mt_track.dll` | **`mt_track.sm_75.ptx` — yes** |
| 2 | which cubins? | `cuobjdump --list-elf mt_track.dll` | `sm_75` only |
| 3 | what is dynamically linked? | `dumpbin -dependents mt_track.dll` | **`cufft64_11.dll`**; no `cudart` → cudart is static |
| 4 | baseline numerics | `N=40 py tools/gpu/test_mt2.py` | worst `dx 2.37e-07` `dy 1.69e-07` px, `dz 2.66e-06` µm — **passes** |
| 5 | **forced PTX path** | `CUDA_FORCE_PTX_JIT=1 CUDA_CACHE_DISABLE=1 …` | **FAILS: `cufftPlan1d(...): cufft 5` (`CUFFT_INTERNAL_ERROR`)** |
| 6 | isolate the variable | `CUDA_CACHE_DISABLE=1` alone | **passes, byte-identical numbers** → test 5's failure is caused by `CUDA_FORCE_PTX_JIT`, nothing else |

Test 5 is NVIDIA's own acceptance procedure for "will this run on a GPU I do not have yet"
([Blackwell Compatibility Guide](https://docs.nvidia.com/cuda/blackwell-compatibility-guide/)): force every module through
the PTX-JIT path, and a failure means some required kernel has no usable PTX. Test 6 makes the attribution airtight.

Note that in test 5 **our kernels loaded fine** — execution reached `cufftPlan1d`, which is well past our own module's
load. The missing PTX is cuFFT's, not ours.

## Two prior claims of mine that the measurements corrected

1. **"`-arch=sm_75` embeds no PTX fallback."** *Wrong.* `-arch=sm_XX` is documented shorthand for
   `--gpu-architecture=compute_XX --gpu-code=sm_XX,compute_XX`
   ([NVCC docs](https://docs.nvidia.com/cuda/cuda-compiler-driver-nvcc/index.html)), and test 1 confirms the PTX is
   physically present. The original build was never broken for forward compatibility.
2. **"cuFFT ships no PTX, because `cuobjdump --list-ptx cufft64_11.dll` found none."** *Not established that way.*
   cuobjdump finds only one `sm_52` cubin in a 277 MB library, so it plainly cannot read cuFFT's kernel store; and NVIDIA
   states that since CUDA 12.0 a large share of cuFFT kernels are **delivered as PTX and compiled at plan-initialization
   time** ([cuFFT, Plan Initialization Time](https://docs.nvidia.com/cuda/archive/12.6.3/cufft/index.html#plan-initialization-time)).
   The conclusion survives, but it rests on test 5, not on cuobjdump.

## What this means per target GPU

| target | our kernel | cuFFT 12.6 | verdict |
|---|---|---|---|
| **Turing sm_75** (RTX 20xx, GTX 16xx) — this machine | native cubin | native | works |
| **Ampere sm_86** (RTX 30xx) | native cubin *(after the rebuild below)* | within 12.6's supported range | expected to work — **re-verify numerics** |
| **Ada sm_89** (RTX 40xx) | native cubin *(after the rebuild below)* | within 12.6's supported range | expected to work — **re-verify numerics** |
| **Blackwell sm_120** (RTX 50xx) | PTX → driver JIT | **not supported by cuFFT 12.6** | **needs cuFFT from CUDA 12.8+** |
| Pascal sm_61 and older | no — `compute_75` PTX never runs *backwards* | — | not supported |

cuFFT did not advertise Blackwell support until the CUDA 12.9 release notes, which matches test 5.

## The build change made

`tools/gpu/cuda/build.bat`, 2026-09-13 — `-arch=sm_75` replaced with an explicit list:

```
-gencode arch=compute_75,code=sm_75      Turing   (this machine)
-gencode arch=compute_86,code=sm_86      Ampere   RTX 30xx
-gencode arch=compute_89,code=sm_89      Ada      RTX 40xx
-gencode arch=compute_75,code=compute_75 PTX, everything newer, via driver JIT
```

This does **not** fix anything that was broken — the PTX was already there. What it buys is **native SASS for the two
GPU generations this rig is most likely to move to**, so those machines skip JIT entirely: no first-call compile
latency, and no JIT-vs-SASS numerical question on the exact hardware we would most likely land on.

**Built and verified 2026-09-13.** `cuobjdump` on the rebuilt DLL: cubins `sm_75`, `sm_86`, `sm_89` + `mt_track.sm_75.ptx`.
Size 776 KB → 1.75 MB. The rebuild is a numerical **no-op** on this machine, as it must be — same 41 fixture frames,
same DLL, before and after:

| | before (sm_75 only) | after (multi-arch) |
|---|---|---|
| worst \|dx\| | 2.37e-07 px | **2.37e-07 px** |
| worst \|dy\| | 1.69e-07 px | **1.69e-07 px** |
| worst \|dz\| | 2.66e-06 µm | **2.66e-06 µm** |
| DLL-internal median | 1.74 ms | 1.66 ms |

Extended run on the new DLL, 201 frames: `dx 4.31e-07`, `dy 1.74e-07` px, `dz 3.83e-06` µm, 0 flips, median 1.72 ms —
all inside tolerance. (The larger worst-case is simply more frames sampled, not a regression: at the identical 41
frames the numbers match to every digit.)

## Moving to a new machine — the checklist

1. **Driver ≥ R560 (Windows 560.76).** The CUDA 12.x minor-version floor of 528.33 is *not* enough for a
   PTX-dependent binary; NVIDIA says PTX-requiring applications must upgrade the driver
   ([minor version compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html)).
2. **`cufft64_11.dll` must be present.** It is a dynamic dependency; cudart is static, so it is the only CUDA library
   that has to travel. The soname stays `_11` across all of CUDA 12.x, so a **newer** cuFFT drops in without relinking —
   which is exactly the Blackwell fix.
3. **On a Blackwell (RTX 50xx) box: deploy cuFFT from CUDA 12.8 or newer**, or rebuild the whole DLL on that toolkit
   (which would also let `-gencode arch=compute_120,code=sm_120` be added).
4. **Re-run the numerical acceptance on the new machine.** This is not optional paperwork: cuFFT guarantees bitwise
   reproducibility only while *plan inputs, cuFFT version and GPU model all stay fixed*
   ([cuFFT Accuracy and Performance](https://docs.nvidia.com/cuda/archive/12.6.3/cufft/index.html#accuracy-and-performance)),
   and changing the GPU model breaks that condition by definition. FMA contraction and reassociation are permitted and
   differ between compiler backends. **So the 1e-6 px agreement is a property of a machine, not a property of this DLL.**
   The command is one line:

   ```
   N=200 py tools/gpu/test_mt2.py
   ```

   Acceptance is the project's standing tolerance: `|dx|,|dy| < 1e-6 px`, `|dz| < 1e-4 µm`.
5. **Before trusting a machine you cannot test on, run test 5 there** (`CUDA_FORCE_PTX_JIT=1`). It is the cheapest way
   to learn that a kernel path has no PTX, and it takes one second.

## Files

- `tools/gpu/cuda/build.bat` — the gencode list and the deployment caveats, in comments at the top.
- `tools/gpu/cuda/mt_track.dll.sm75only.bak` — the pre-change DLL, md5 `ab9070cc4457d11b7f2b6025641c3c70`.
- `tools/gpu/verify_before_rebuild.log`, `verify_force_ptx_jit.log`, `verify_cache_disable_only.log` — tests 4, 5, 6.
- `archive/peer/2026-09-13-gpu-portability-attack.md` — the adversarial peer review that supplied the
  `CUDA_FORCE_PTX_JIT` test and corrected the cuFFT reasoning.
- **`archive/bench-2026-09-13-gpu-portability/REPORT.md` — the full report** (INDEX row 20): protocol, what was held
  fixed vs varied, all nine tests with their logs, the two claims of mine the measurements corrected, and the level of
  verification (functional on this machine; the Ampere/Ada verdicts are structural, since no such GPU was available).
