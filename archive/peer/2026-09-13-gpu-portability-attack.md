---
type: peer-review
status: historical
date: 2026-09-13
tags: [peer-review, gpu]
---

# gpu-portability-attack

- **agent:** codex
- **date:** 2026-09-13
- **outcome:** ANSWERED (107s)
- **why asked:** a FAILED PREDICTION. I told the user `-arch=sm_75` embeds no PTX fallback; `cuobjdump --list-ptx` on
  the real DLL then showed PTX present. CLAUDE.md makes peer review mandatory at that point, and the replacement claim
  ("so the DLL is already portable, no rebuild needed") was about to drive a decision.
- **verdict:** DECISIVE — it supplied the acceptance test that overturned the replacement claim

## Question

ATTACK this claim, do not confirm it. CLAIM: our CUDA DLL (mt_track.dll, nvcc -O2 -arch=sm_75, CUDA Toolkit 12.6.3, dynamically linked to cufft64_11.dll, cudart static) runs unchanged on a DIFFERENT machine with a NEWER NVIDIA GPU (Ampere sm_86, Ada sm_89, Blackwell sm_120), because the fatbinary carries compute_75 PTX that the driver JIT-compiles. ALREADY RULED OUT locally: kernel PTX presence VERIFIED by cuobjdump --list-ptx on the real DLL; cudart absent from dumpbin -dependents so it is static; the -arch shorthand equivalence confirmed in NVIDIA nvcc docs; and cuobjdump --list-ptx on cufft64_11.dll reports NO PTX AT ALL. FIND REASONS THIS FAILS: (a) does cuFFT 12.6, shipping only cubins, work on Blackwell sm_120 at all, or does cufftPlanMany/cufftExecZ2Z return an error on an arch with no cubin? Is there any cuFFT-internal JIT or nvJitLink path? (b) minimum NVIDIA driver version for CUDA 12.6 PTX JIT, and how CUDA 12 minor-version compatibility interacts. (c) can JIT from PTX change DOUBLE-PRECISION numerical results versus the sm_75 cubin? We require 1e-6 px agreement. (d) first-call JIT compile latency and whether the compute cache is per-user/per-driver-version. Cite NVIDIA doc URLs.

## Answer

The claim is unsafe, especially for Blackwell. Your own kernels are forward-compatible through `compute_75` PTX, but that does not prove that the complete DLL?봧ncluding cuFFT 12.6.3?봶ill execute unchanged or reproduce tracking coordinates within \(10^{-6}\) px.

### (a) cuFFT is the main Blackwell risk

The premise that cuFFT 12.6 ?쐓hips only cubins??is contradicted by NVIDIA?셲 cuFFT 12.6.3 documentation. NVIDIA says that since CUDA 12.0, a larger portion of cuFFT kernels is delivered as PTX and compiled by the driver during plan initialization. Therefore, `cuobjdump --list-ptx cufft64_11.dll` is not a reliable inventory of every internally packaged or dynamically selected cuFFT kernel. [NVIDIA cuFFT 12.6.3, Plan Initialization Time](https://docs.nvidia.com/cuda/archive/12.6.3/cufft/index.html#plan-initialization-time)

That internal PTX is probably what gives ordinary cuFFT plans a chance of working on Blackwell. But NVIDIA did not advertise explicit Blackwell support in cuFFT until CUDA 12.9 release notes. That is a serious qualification against treating cuFFT 12.6 as supported on `sm_120`, even if it happens to run by JIT. [CUDA 12.9 release notes, cuFFT ?쏛dded support for NVIDIA Blackwell??(https://docs.nvidia.com/cuda/archive/12.9.2/cuda-toolkit-release-notes/index.html)

For your specific calls:

- `cufftPlanMany` may fail during library initialization, kernel-module loading, plan generation, or JIT. Possible documented results include `CUFFT_SETUP_FAILED`, `CUFFT_INTERNAL_ERROR`, and allocation/size errors. [cuFFT return codes and plan APIs](https://docs.nvidia.com/cuda/archive/12.6.3/cufft/index.html#cufftresult)
- `cufftExecZ2Z` may subsequently return `CUFFT_EXEC_FAILED`, `CUFFT_INTERNAL_ERROR`, or `CUFFT_SETUP_FAILED`. [cuFFT execution API](https://docs.nvidia.com/cuda/archive/12.6.3/cufft/index.html#cufftexecc2c-and-cufftexecz2z)
- Absence of a compatible cubin does not necessarily mean immediate failure because cuFFT documents ordinary driver PTX JIT. Conversely, the fact that some cuFFT kernels contain internal PTX does not establish that every kernel selected for every `cufftPlanMany` geometry has a Blackwell-compatible route. [cuFFT plan initialization](https://docs.nvidia.com/cuda/archive/12.6.3/cufft/index.html#plan-initialization-time)

cuFFT also has a separate nvJitLink path for LTO kernels and callbacks. CUDA 12.6 cuFFT requires nvJitLink from CUDA 12.x with minor version at least 12.6, and it loads nvJitLink dynamically. NVIDIA says runtime-link failure falls back to offline-compiled kernels. On an architecture for which those fallback cubins are unusable, that fallback cannot be assumed to rescue execution. [cuFFT LTO/nvJitLink requirements](https://docs.nvidia.com/cuda/archive/12.6.3/cufft/index.html#link-time-optimized-kernels)

For plain Z2Z without callbacks, the documented ordinary cuFFT PTX/driver-JIT path is more relevant than nvJitLink. There is nevertheless no NVIDIA statement in the 12.6 release notes guaranteeing cuFFT 12.6 operation on `sm_120`.

NVIDIA?셲 Blackwell guide gives the decisive acceptance test: install a Blackwell-capable driver, set `CUDA_FORCE_PTX_JIT=1`, and exercise the whole application. It says failure under that setting means some required kernel lacks usable PTX. Testing only `mt_track.dll`?셲 fatbinary is insufficient because the process also loads cuFFT. [NVIDIA Blackwell Compatibility Guide](https://docs.nvidia.com/cuda/blackwell-compatibility-guide/#verifying-blackwell-compatibility-for-existing-applications)

### (b) Driver requirements are stricter than ?쏞UDA 12.x compatible??
There are two different driver thresholds:

- CUDA 12.x minor-version compatibility floor: Linux `525.60.13`, Windows `528.33`.
- Driver corresponding to CUDA 12.6 GA: Linux `560.28.03`, Windows `560.76`; later 12.6 updates specify slightly newer R560 versions. [CUDA 12.6 release notes](https://docs.nvidia.com/cuda/archive/12.6.3/cuda-toolkit-release-notes/)

The lower CUDA-12 compatibility floor is not sufficient for your PTX-dependent binary. NVIDIA explicitly warns that applications requiring PTX can fail on older drivers under minor-version compatibility and says such applications must upgrade the driver. Minor compatibility provides only a limited feature set; it is not a promise that an older R525/R528 driver can understand PTX produced by CUDA 12.6. [CUDA Minor Version Compatibility caveats](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html#application-considerations-for-minor-version-compatibility)

Accordingly:

- For Ampere/Ada, require at least the CUDA 12.6 corresponding driver?봕560, specifically at least `560.28.03` Linux or `560.76` Windows?봱ather than relying on the CUDA-12 family floor. [CUDA 12.6 release notes](https://docs.nvidia.com/cuda/archive/12.6.0/cuda-toolkit-release-notes/index.html)
- For Blackwell, the GPU itself requires a later Blackwell-capable driver. NVIDIA lists B200 at R570 `>=570.133.20` and RTX PRO Blackwell at R575 `>=575.51.03`; the exact minimum depends on the actual Blackwell product. [NVIDIA MIG deployment requirements](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/deployment-considerations.html)

A sufficiently new Blackwell driver should understand older `compute_75` PTX, but that establishes only the driver-JIT route for kernels whose PTX is actually available. NVIDIA?셲 compatibility guide says PTX may be compiled for later architectures, including Blackwell, but requires every needed kernel path to contain PTX. [Blackwell Compatibility Guide](https://docs.nvidia.com/cuda/blackwell-compatibility-guide/)

### (c) \(10^{-6}\) px numerical agreement is not guaranteed

PTX JIT can change double-precision results relative to the precompiled `sm_75` cubin. Both may be IEEE-754-conforming while differing in low bits because the driver JIT is a different compiler backend targeting a different architecture. Floating-point contraction and reassociation are permitted by default; FMA uses one rounding rather than separate multiply and add operations, and operation ordering affects results. [CUDA floating-point rules](https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/mathematical-functions.html#cuda-and-ieee-754-compliance), [CUDA Best Practices: floating-point accuracy](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/#floating-point-math-is-not-associative)

cuFFT provides an even more direct warning: it promises bitwise reproducibility only when the plan inputs, cuFFT version, and GPU model remain constant. You are changing the GPU model, so NVIDIA?셲 reproducibility condition is explicitly not met. cuFFT also says FFT relative error grows approximately with \(\log_2 N\). [cuFFT Accuracy and Performance](https://docs.nvidia.com/cuda/archive/12.6.3/cufft/index.html#accuracy-and-performance)

Consequently, neither double precision nor identical source/PTX implies \(10^{-6}\)-pixel coordinate agreement. Small FFT/kernel differences can propagate through peak selection, interpolation, division, thresholds, or iterative fitting. The tolerance must be validated end-to-end using representative and adversarial frames; it cannot be established from CUDA compatibility documentation.

### (d) Startup latency and cache behavior

NVIDIA states that PTX JIT increases application/module load time. For cuFFT, compilation occurs during the first plan initialization for the selected transform, with cost dependent on transform size and host-CPU speed. cuFFT LTO finalization can add hundreds of milliseconds. [cuFFT plan initialization](https://docs.nvidia.com/cuda/archive/12.6.3/cufft/index.html#plan-initialization-time), [cuFFT LTO kernels](https://docs.nvidia.com/cuda/archive/12.6.3/cufft/index.html#link-time-optimized-kernels)

The driver compute cache is effectively per user by default because it resides at:

- Windows: `%APPDATA%\NVIDIA\ComputeCache`
- Linux: `~/.nv/ComputeCache`

It is bounded, entries can be evicted, binaries larger than the configured limit are not cached, and `CUDA_CACHE_DISABLE=1` forces recompilation. [CUDA JIT-cache environment variables](https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/environment-variables.html#jit-compilation)

NVIDIA also states that upgrading the device driver invalidates the compute cache so the new driver?셲 JIT compiler can regenerate code. Thus a first run by another Windows account, after a driver update, following eviction, or with caching disabled can incur the compilation cost again. [CUDA Programming Guide, JIT Compilation](https://docs.nvidia.com/cuda/cuda-programming-guide/01-introduction/cuda-platform.html#just-in-time-compilation)

### Bottom line

- **Ampere/Ada:** likely executable with a sufficiently new driver, but not proven numerically equivalent.
- **Blackwell `sm_120`:** your own `compute_75` PTX is necessary but not sufficient. cuFFT 12.6 contains internal JIT machinery despite the `cuobjdump` result, yet explicit Blackwell support arrived later and the exact Z2Z plan path is not guaranteed by the 12.6 documentation.
- **The claim ?쐒uns unchanged??fails as a qualification statement** until the complete deployed DLL set is tested on each target GPU/driver, including cold-cache initialization, checked `cufftResult` values, forced-PTX execution, and the full \(10^{-6}\)-px regression corpus.

## Sources

(extract from answer)

## What was done with it

The peer's most valuable contribution was **naming NVIDIA's own acceptance test**, `CUDA_FORCE_PTX_JIT=1`, which
reproduces "will this run on a GPU I do not own" on the GPU I *do* own. Run here, it **falsified the claim**:

```
mt2_open -> False   cufftPlan1d(&c->plan_z, n, CUFFT_Z2Z, nb): cufft 5      (CUFFT_INTERNAL_ERROR)
```

Attribution was isolated with a second run — `CUDA_CACHE_DISABLE=1` alone passes with byte-identical numbers — so the
failure is caused by `CUDA_FORCE_PTX_JIT` and nothing else. Our own kernels loaded fine: execution reached the cuFFT
plan call, well past our module's load. **cuFFT, not our kernel, is what blocks a new-architecture GPU.**

It also corrected a second claim of mine. I had inferred "cuFFT ships no PTX" from `cuobjdump --list-ptx cufft64_11.dll`
returning nothing; the peer showed that is not a valid inventory — NVIDIA documents that since CUDA 12.0 much of cuFFT
arrives as PTX compiled at plan-initialization time. The conclusion survives, but now on the strength of the forced-JIT
test rather than on a cuobjdump reading. (cuobjdump finds exactly one `sm_52` cubin in a 277 MB library, which should
have been the tell.)

Two further points went straight into the deployment checklist: the driver floor for a PTX-dependent CUDA 12.6 binary is
**R560 (Windows 560.76)**, not the 528.33 CUDA-12 minor-version floor; and cuFFT guarantees bitwise reproducibility only
while the GPU model is fixed, so the project's 1e-6 px acceptance must be **re-run** on any new machine rather than
inherited.

Written up in [docs/gpu-portability.md](../../docs/gpu-portability.md). The build was changed to emit native cubins for
`sm_75/86/89` plus `compute_75` PTX, verified numerically identical to the digit on the 41-frame fixture, and deployed to
`claudeDev\Debug\`. The caveats live in comments at the top of `tools/gpu/cuda/build.bat`.
