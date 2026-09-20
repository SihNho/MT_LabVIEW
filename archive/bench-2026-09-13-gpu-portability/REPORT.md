---
type: narrative
status: historical
date: 2026-09-13
tags: [archive]
---

# GPU portability — will the CUDA tracking DLL still work if the PC changes?

**Date:** 2026-09-13 · **Duration:** ~25 min · **Rig untouched** (no LabVIEW, no instruments; the GPU only)

---

## 1. Why this test was run

The user asked directly:

> *"만약 내가 나중에 디바이스를 옮겨서 gpu 버전이 바뀐다고 해도 너가 지금 만들 커널 사용에 문제가 없을까"*

This is not a hypothetical. It is the **same premise that split the codebase in two** — *"언제든지 pc가 바뀔 여지가 있으므로
cpu only, gpu computing 두개 코드를 별도로 둘거야"* (2026-09-13). A GPU build that silently only runs on this one RTX 2060
would undermine the reason the GPU path is being maintained at all.

The question decomposes into three that can each be measured rather than argued:

1. Does the compiled DLL contain code a **different** GPU architecture can execute?
2. Which **other components** must travel with it, and do *they* have the same property?
3. If it runs, does it produce the **same numbers**? (The project's acceptance is 1e-6 px.)

## 2. Environment

| | |
|---|---|
| GPU | NVIDIA GeForce RTX 2060, **compute capability 7.5** (Turing) |
| Driver | 616.64 |
| CUDA Toolkit | 12.6.3 (`nvcc` V12.6.85) |
| `nvcc` cubin targets available | `sm_50 … sm_90` — **`sm_100`/`sm_120` cannot be built here at all** |
| DLL under test | `tools/gpu/cuda/mt_track.dll`, built by `build.bat` |
| Fixture | the recorded 5-bead dataset, chained frame-to-frame, vs the LabVIEW reference |
| Acceptance | `\|dx\|,\|dy\| < 1e-6 px`, `\|dz\| < 1e-4 µm` (z relaxed by the user 2026-09-07) |

Raw evidence: [`evidence_cuobjdump.txt`](evidence_cuobjdump.txt).

## 3. What was held fixed, what varied

**Fixed:** the DLL's source (`mt_track.cu` untouched), the fixture frames, the GPU, the driver, the toolkit, the
acceptance tolerance, the harness (`tools/gpu/test_mt2.py`).

**Varied, one at a time:**

- the compiled architecture set (`-arch=sm_75` → an explicit `-gencode` list),
- the **execution path** for the *same* binary — native SASS vs forced PTX JIT (`CUDA_FORCE_PTX_JIT=1`),
- and, as a control, the JIT cache (`CUDA_CACHE_DISABLE=1`) on its own.

The third is the point of the design: it is what turns "the forced-JIT run failed" into "**`CUDA_FORCE_PTX_JIT` caused
the failure**".

## 4. Results

| # | test | command | result | log |
|---|---|---|---|---|
| 1 | Is PTX embedded in our DLL? | `cuobjdump --list-ptx` | **`mt_track.sm_75.ptx` — yes** | evidence |
| 2 | Which cubins? | `cuobjdump --list-elf` | `sm_75` only | evidence |
| 3 | What links dynamically? | `dumpbin -dependents` | **`cufft64_11.dll`**; no `cudart` → static | evidence |
| 4 | Baseline numerics (41 frames) | `N=40 py tools/gpu/test_mt2.py` | `dx 2.37e-07` `dy 1.69e-07` px, `dz 2.66e-06` µm, 0 flips, 1.74 ms | `verify_before_rebuild.log` |
| 5 | **Forced PTX path** | `CUDA_FORCE_PTX_JIT=1 CUDA_CACHE_DISABLE=1` | **FAIL — `cufftPlan1d(...): cufft 5` = `CUFFT_INTERNAL_ERROR`** | `verify_force_ptx_jit.log` |
| 6 | **Control**: cache only | `CUDA_CACHE_DISABLE=1` alone | **PASS, numbers identical to test 4** | `verify_cache_disable_only.log` |
| 7 | Rebuild multi-arch | `build.bat` | cubins `sm_75`+`sm_86`+`sm_89`, PTX `compute_75`; 776 KB → 1.75 MB | `build_multiarch.log` |
| 8 | Post-rebuild, same 41 frames | `N=40 …` | `dx 2.37e-07` `dy 1.69e-07` px, `dz 2.66e-06` µm — **identical to every digit** | `verify_after_rebuild_n40.log` |
| 9 | Post-rebuild, 201 frames | `N=200 …` | `dx 4.31e-07` `dy 1.74e-07` px, `dz 3.83e-06` µm, 0 flips, 1.72 ms | `verify_after_rebuild.log` |

### 4.1 The headline — test 5

```
mt2_open -> False   cufftPlan1d(&c->plan_z, n, CUFFT_Z2Z, nb): cufft 5
```

`CUDA_FORCE_PTX_JIT=1` is **NVIDIA's own acceptance procedure** for "will my binary run on a GPU I do not own"
([Blackwell Compatibility Guide](https://docs.nvidia.com/cuda/blackwell-compatibility-guide/)): it forces every module
through the PTX→SASS JIT route, and a failure means some required kernel has no usable PTX.

Two things make the reading precise:

- **Our kernels are not the problem.** Execution reached `cufftPlan1d`, which is well past our own module's load. Had
  our PTX been missing or malformed, `mt2_open` would have failed earlier.
- **Attribution is isolated.** Test 6 runs the *other* environment variable alone and passes with numbers identical to
  the baseline, so the failure in test 5 is caused by `CUDA_FORCE_PTX_JIT` and by nothing else in that command line.

**Conclusion: cuFFT is the component that breaks first on a new GPU architecture — not our kernel.**

### 4.2 The rebuild is a numerical no-op, as it must be

Test 8 against test 4, same 41 fixture frames, same harness:

| | before (`-arch=sm_75`) | after (multi-arch) |
|---|---|---|
| worst \|dx\| | 2.37e-07 px | **2.37e-07 px** |
| worst \|dy\| | 1.69e-07 px | **1.69e-07 px** |
| worst \|dz\| | 2.66e-06 µm | **2.66e-06 µm** |
| flips | 0 | 0 |
| DLL-internal median | 1.74 ms | 1.66 ms |

This is the expected result — the `sm_75` cubin is compiled from the same source with the same flags — and it is worth
stating as a *verified* no-op rather than an assumed one. Test 9's slightly larger worst case is five times as many
frames sampled, not a regression; at the identical 41 frames the agreement is exact.

## 5. Two claims of mine that the measurements corrected

Recorded because both were stated to the user before being checked.

1. **"`-arch=sm_75` embeds no PTX fallback, so the DLL would fail on any other GPU."** — **Wrong.** `-arch=sm_XX` is
   documented shorthand for `--gpu-architecture=compute_XX --gpu-code=sm_XX,compute_XX`
   ([NVCC docs](https://docs.nvidia.com/cuda/cuda-compiler-driver-nvcc/index.html)); test 1 confirms the PTX is
   physically present. **The original build was never broken for forward compatibility.**
2. **"cuFFT ships no PTX — `cuobjdump --list-ptx cufft64_11.dll` finds none."** — **Not established that way.**
   cuobjdump finds exactly one `sm_52` cubin inside a 277 MB library, which should itself have been the tell that the
   tool cannot read cuFFT's kernel store; and NVIDIA documents that since CUDA 12.0 a large share of cuFFT kernels are
   **delivered as PTX and compiled at plan-initialization time**
   ([cuFFT, Plan Initialization Time](https://docs.nvidia.com/cuda/archive/12.6.3/cufft/index.html#plan-initialization-time)).
   The conclusion about cuFFT survives — but on the strength of test 5, not of a cuobjdump reading.

Both corrections came out of the adversarial peer review, which is why it was run: the first claim was a **failed
prediction** (predicted no PTX, observed PTX), and the replacement claim — "so the DLL is already portable, no rebuild
needed" — was about to drive the decision to do nothing. See
[`archive/peer/2026-09-13-gpu-portability-attack.md`](../peer/2026-09-13-gpu-portability-attack.md); the peer supplied
the `CUDA_FORCE_PTX_JIT` test that then falsified it.

## 6. Verdict per target GPU

| target | our kernel | cuFFT 12.6 | verdict |
|---|---|---|---|
| **Turing sm_75** — RTX 20xx, GTX 16xx (this machine) | native cubin | native | works |
| **Ampere sm_86** — RTX 30xx | native cubin *(added by this rebuild)* | inside 12.6's range | expected to work — re-verify numerics |
| **Ada sm_89** — RTX 40xx | native cubin *(added by this rebuild)* | inside 12.6's range | expected to work — re-verify numerics |
| **Blackwell sm_120** — RTX 50xx | PTX → driver JIT | **not supported** (test 5) | **needs cuFFT from CUDA 12.8+** |
| Pascal sm_61 and older | no — `compute_75` PTX never runs *backwards* | — | not supported |

## 7. The change made

`tools/gpu/cuda/build.bat` — `-arch=sm_75` replaced by an explicit list ([`build.bat.after`](build.bat.after)):

```
-gencode arch=compute_75,code=sm_75      Turing   (this machine)
-gencode arch=compute_86,code=sm_86      Ampere   RTX 30xx
-gencode arch=compute_89,code=sm_89      Ada      RTX 40xx
-gencode arch=compute_75,code=compute_75 PTX — everything newer, via driver JIT
```

This fixes nothing that was broken. What it buys is **native SASS for the two GPU generations this rig is most likely
to move to**, so those machines skip JIT entirely: no first-call compile latency, and no JIT-vs-SASS numerical question
on the hardware we would most plausibly land on. The deployment caveats are now comments at the top of `build.bat`, so
they are read by whoever next rebuilds rather than living only in a document.

Deployed to `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Debug\` — both `mt_track.dll` and the
legacy-named `GPU Tracking.dll`, md5 `d4c98cea80db37a8e9b9ea8402b2e84c`. The pre-change DLL is preserved as
`tools/gpu/cuda/mt_track.dll.sm75only.bak`, md5 `ab9070cc4457d11b7f2b6025641c3c70`.

## 8. Moving to a new machine — the checklist

1. **Driver ≥ R560 (Windows 560.76).** The CUDA 12.x minor-version floor of 528.33 is *not* enough for a PTX-dependent
   binary ([minor version compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html)).
2. **`cufft64_11.dll` must be present.** It is the only CUDA library that has to travel (cudart is static). The soname
   stays `_11` across all of CUDA 12.x, so a **newer** cuFFT drops in with no relinking.
3. **On an RTX 50xx box, deploy cuFFT from CUDA 12.8+**, or rebuild the DLL on that toolkit — which would also allow
   `-gencode arch=compute_120,code=sm_120` to be added.
4. **Re-run the numerical acceptance there.** cuFFT guarantees bitwise reproducibility only while *plan inputs, cuFFT
   version and GPU model all stay fixed*
   ([cuFFT Accuracy and Performance](https://docs.nvidia.com/cuda/archive/12.6.3/cufft/index.html#accuracy-and-performance));
   changing the GPU model breaks that condition by definition, and FMA contraction and reassociation are permitted and
   differ between compiler backends. **So the 1e-6 px agreement is a property of a machine, not of this DLL.** One line:

   ```
   N=200 py tools/gpu/test_mt2.py
   ```

5. **Run test 5 there first** (`CUDA_FORCE_PTX_JIT=1`). It costs one second and tells you immediately whether some
   kernel path has no PTX.

## 9. Level of verification

**Functional, on this machine** — real fixture data flowed through the rebuilt DLL and the outputs were compared with
the LabVIEW reference (tests 8, 9). The portability *verdicts* for Ampere/Ada in §6 are **not** functional: no such GPU
was available to test. They are structural (the cubins exist and the toolkit supports the architecture), which is why
§8 item 4 makes re-verification mandatory rather than advisory.

## 10. Files

| file | what it is |
|---|---|
| `evidence_cuobjdump.txt` | environment, `cuobjdump`/`dumpbin` before and after, md5s |
| `verify_before_rebuild.log` | test 4 |
| `verify_force_ptx_jit.log` | **test 5 — the headline** |
| `verify_cache_disable_only.log` | test 6, the control that isolates the cause |
| `verify_after_rebuild_n40.log` | test 8, the like-for-like comparison |
| `verify_after_rebuild.log` | test 9, 201 frames |
| `build_multiarch.log` | test 7 |
| `build.bat.after` | the changed build script, caveats included |
| `../peer/2026-09-13-gpu-portability-attack.md` | the adversarial review that supplied test 5 |
| `../../docs/gpu-portability.md` | the active, short version of this report |
