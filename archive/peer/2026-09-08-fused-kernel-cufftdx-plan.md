---
type: peer-review
status: historical
date: 2026-09-08
tags: [peer-review, kernel, plan]
disposition: legacy
---

# fused-kernel-cufftdx-plan

- **agent:** codex
- **date:** 2026-09-08
- **outcome:** ANSWERED (150s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

Review this plan critically (attack weak points, cite docs). Context: CUDA 12.6, RTX 2060 (sm_75), MSVC 2022, nvcc. Existing DLL tools/gpu/cuda/mt_track.cu tracks 5-500 beads per 1280x1024 8-bit frame: per frame 9 kernel launches + 6 cuFFT Z2Z executions (batched, sizes 120 and 119, DOUBLE precision) + 9 memcpys, ~1.5 ms for 5 beads dominated by per-call overhead (3.5x worse inside LabVIEW). Plan: fuse the whole per-bead pipeline into ONE kernel (one block per bead, 120 threads, shared memory; ~20 KB per block): read 120x120 sub-image from the frame in global memory -> cross-averaged x/y profiles (double) -> 120-point FFT -> window+square -> 3 rounds of {IFFT -> parabola peak -> phase shift} -> radial profile with bilinear binning -> mirrored 119-point profile -> 119-point FFT -> cosine band -> IFFT -> SSD fit against 60 calibration slices (each ~40 doubles) -> 5-point phase quadratic fit -> z. Using cuFFTDx (MathDx) block FFTs inside the kernel for the 120- and 119-point transforms in double precision; fall back to an in-kernel direct DFT (O(n^2), 14k multiply-adds) where cuFFTDx lacks the size. Questions: (1) Does cuFFTDx support double-precision block FFT of size 120 and size 119 (119 = 7 x 17) on sm_75 with CUDA 12.6? Which MathDx version, and is the header package on PyPI as nvidia-mathdx usable with plain nvcc (include path), or is a download from developer.nvidia.com required? Any licence constraint for redistributing a DLL built with it? (2) Register/shared-memory pressure: cuFFTDx block FFT of 120 doubles with 120 threads (or ffts_per_block / elements-per-thread choices) - realistic occupancy on sm_75 and pitfalls (block size must match FFT::block_dim; Complex type; need for __syncthreads between fused stages). (3) Is a direct O(n^2) DFT in double for n=119/120 per block competitive (~14k FMAs per thread-block, easily under 20 us) - i.e. is cuFFTDx even worth the dependency for these tiny sizes? (4) Numerical: our acceptance is 1e-6 px in x,y and 1e-4 um in z against the LabVIEW kernel; are cuFFTDx double transforms accurate to ~1e-12 like cuFFT, and does the ordering/normalisation differ from cuFFT (unnormalised inverse)? (5) Anything that makes a single 120-thread block per bead a bad idea (e.g. the SSD fit over 60 slices x 40 samples per bead is only 2400 FMAs, fine; the 3 sequential rounds are latency-bound) - would 2 beads per block or 240 threads be better on a 30-SM GPU with 5-50 beads? Give URLs.

## Answer

The plan is directionally good, but two assumptions need correction: cuFFTDx 24.08 supports FP64 size 120 on sm_75, but not size 119; and ??4k FMAs??materially understates a direct complex DFT?셲 work.

## 1. Version, size support, installation, licensing

For CUDA 12.6 + RTX 2060 + MSVC 2022, use MathDx 24.08 / cuFFTDx 1.2.1. NVIDIA identifies cuFFTDx 1.2.1 as the version shipped in `nvidia-mathdx-24.08.0`; it supports sm_75 and CUDA 12-era toolchains. MSVC support was preliminary, requiring `/Zc:__cplusplus`, with a warning about long template-mangled names. [cuFFTDx 1.2.1 release notes](https://docs.nvidia.com/cuda/cufftdx/1.2.1/release_notes.html)

- FP64 C2C size 120: supported.
- FP64 C2C size 119: not supported. The complete 1.4-era FP64 list?봶hich is broader than or comparable to 1.2.1?봠ontains 120 and 121 but not 119. Therefore do not expect 119 to compile merely because it is below the nominal maximum. [FP64 supported-size list](https://docs.nvidia.com/cuda/cufftdx/1.4.0-ea/double_c2c_sizes.html)
- Verify the exact descriptors at compile time with `cufftdx::is_supported<Description, 750>`. Support depends not just on size but also precision and `ElementsPerThread`. [cuFFTDx traits](https://docs.nvidia.com/cuda/cufftdx/api/traits.html)

The PyPI wheel is usable with plain `nvcc`; it is not a Python execution wrapper. `nvidia-mathdx==24.8.0` is a platform-independent wheel containing the MathDx distribution. Point `-I` at the installed directory containing `cufftdx.hpp`, and compile as C++17:

```text
nvcc -std=c++17 -arch=sm_75 -Xcompiler "/Zc:__cplusplus" \
     -I<...>/nvidia/mathdx/24.08/include ...
```

NVIDIA describes cuFFTDx as header-only and documents precisely this include-path workflow. A developer.nvidia.com download is therefore not technically required if the PyPI wheel supplies the same headers. [PyPI package](https://pypi.org/project/nvidia-mathdx/24.8.0/) [installation guide](https://docs.nvidia.com/cuda/cufftdx/installation.html)

For licensing, distributing a DLL that incorporates cuFFTDx device code appears explicitly permitted when the application has material additional functionality, the incorporated SDK parts are accessed only by that application, and required notices are preserved. Do not redistribute the raw SDK/header package casually, and review the exact 24.08 license bundled in the wheel before release. [NVIDIA Math Libraries SDK license](https://docs.nvidia.com/cuda/archive/12.0.0/cufftdx/license.html)

## 2. Block shape and resource pressure

Do not assume ??20 FFT points means 120 cuFFTDx threads.??In block mode the normal x dimension is:

```text
FFT::block_dim.x = FFT size / FFT::elements_per_thread
```

FP64 `ElementsPerThread` must normally be 2??6. Therefore a size-120 transform might use 60, 30, 24, 20, 15, 12, 10, or fewer FFT workers?봭ot 120. Launching an arbitrary 120-thread block is incorrect unless the selected descriptor explicitly supports a matching custom `BlockDim`; custom block dimensions were not available in cuFFTDx 1.2.1. Launch with exactly `FFT::block_dim`, or arrange the surrounding work around that dimension. [block operators](https://docs.nvidia.com/cuda/cufftdx/api/operators.html) [block-dimension trait](https://docs.nvidia.com/cuda/cufftdx/api/traits.html)

A practical pattern is:

- Launch `max(120, FFT::block_dim.x)` only if the 1.2.1 execution contract permits inactive/nonparticipating lanes?봶hich must be verified from that version?셲 example and execution method.
- Otherwise pick an FFT descriptor whose required block dimension also works for the rest of the pipeline, and have each thread process several image samples.
- Add compile-time assertions and launch from `FFT::block_dim`; do not hard-code 120.

Use `FFT::value_type`/`FFT::input_type`, not an assumed `double2` or arbitrary complex class. For FP64 C2C, the documented representation is real followed by imaginary, but the library?셲 trait type protects you against API details. [cuFFTDx value formats](https://docs.nvidia.com/cuda/cufftdx/1.2.1/api/methods.html)

Your estimated 20 KB shared memory is plausible only if the 120횞120 input remains bytes or is streamed. If expanded to double in shared memory, the subimage alone is 115,200 bytes and cannot fit on sm_75. Turing provides 64 KB shared memory per SM and 64K 32-bit registers per SM. [Turing tuning guide](https://docs.nvidia.com/cuda/archive/13.0.0/turing-tuning-guide/index.html)

At approximately 20 KB/block, shared memory alone nominally permits three blocks per SM, but registers may reduce that sharply. FP64 complex temporaries consume pairs of 32-bit registers, and cuFFTDx?셲 `ElementsPerThread` directly affects register demand. Check:

```text
nvcc --ptxas-options=-v
```

and feed the actual registers/block, shared bytes, and block dimensions into Nsight Compute?셲 occupancy calculator; NVIDIA warns that allocation granularity makes hand estimates unreliable. [CUDA Best Practices occupancy guidance](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html)

You need explicit `__syncthreads()` whenever one fused stage consumes shared-memory results written by other threads, including before reusing FFT shared storage. Do not rely on cuFFTDx?셲 internal barriers to publish your later writes: its execute methods synchronize what they need for their own shared-memory use, not arbitrary producer/consumer stages surrounding the call. [cuFFTDx execution methods](https://docs.nvidia.com/cuda/cufftdx/1.7.3/api/methods.html)

Also audit every barrier for divergent control flow: all threads in the block must reach a block barrier consistently.

## 3. Direct DFT competitiveness

??4k FMAs??is not the correct cost model. A 119-point direct complex DFT performs 119짼 = 14,161 complex multiply-accumulates. That is roughly:

- 56,644 real multiply/add or FMA-like arithmetic operations under a four-operation complex MAC model;
- plus coefficient access or `sin/cos` generation;
- plus reduction/accumulation dependencies.

Never calculate transcendental twiddles inside the inner loop. Precompute 119횞119 complex twiddles?봮r exploit recurrence/symmetry?봟ut a full FP64 table is about 226 KB and will not fit in constant memory. A smaller base-twiddle table plus recurrence is more realistic.

On a consumer Turing GPU, FP64 throughput and serial accumulator dependency are the risks. ?쏣asily under 20 쨉s??is plausible for one block but is not established from operation count, particularly when only five blocks are active. Benchmark the complete fused candidate; CUDA?셲 own documentation notes that direct DFT is \(O(N^2)\), while FFT implementations reduce the work substantially. [cuFFT accuracy and performance](https://docs.nvidia.com/cuda/cufft/index.html#accuracy-and-performance)

My recommendation:

- Use cuFFTDx for every 120-point transform.
- Implement the single 119-point pair using either a specialized mixed-radix/Rader transform or direct DFT initially.
- Benchmark direct DFT versus a hand-coded 7횞17 decomposition. Since 17 is prime, Rader or a compact direct 17-point stage is manageable.
- Do not add a global cuFFT call solely for 119 unless measurement shows the direct implementation dominates.

cuFFTDx remains worthwhile because the pipeline performs four 120-point transforms per bead and fusion avoids global-memory round trips; NVIDIA explicitly identifies this as its main advantage over host-launched cuFFT. [cuFFTDx introduction](https://docs.nvidia.com/cuda/cufftdx/introduction1.html)

## 4. Numerical equivalence

cuFFTDx FP64 means its inputs, outputs, and underlying FFT arithmetic are double precision. Both cuFFTDx and cuFFT use unnormalised transforms: forward followed by inverse yields \(N\) times the original. [cuFFTDx precision and scaling](https://docs.nvidia.com/cuda/cufftdx/api/operators.html)

However, NVIDIA does not promise ?쏿pproximately \(10^{-12}\)??agreement with cuFFT or bitwise equivalence. cuFFTDx explicitly warns that different `ElementsPerThread`, `FFTsPerBlock`, block dimensions, or GPU architectures may produce non-bit-identical results. [bit-identity warning](https://docs.nvidia.com/cuda/cufftdx/1.2.1/warnings/bit_identical.html)

The strictest risk is not raw FFT error; it is amplification through:

- parabola denominators near zero;
- phase wrapping or peak-bin tie breaking;
- bilinear radial-bin accumulation order;
- SSD slices with nearly equal scores;
- the final five-point quadratic fit.

Therefore validate final x/y/z results over the real calibration corpus, including boundary, flat-peak, and near-tie cases. Matching cuFFT normalisation and sign convention is necessary but insufficient. Your `1e-6 px` x/y tolerance may be harder than an ordinary FP64 FFT error target because reductions and peak selection can change downstream branches.

## 5. One block per bead

For 5??0 beads on 30 SMs, one block per bead gives only 5??0 blocks, so the five-bead case cannot occupy more than five SMs. That is unavoidable unless each bead is decomposed across independently schedulable blocks, which conflicts with the sequential phase-refinement pipeline.

Two beads per block is probably worse:

- five beads become three blocks instead of five;
- shared memory and registers roughly double;
- block residency falls;
- one bead can delay the other;
- synchronization becomes more complicated.

A 240-thread block for one bead only helps if it exposes genuine parallel work?봣or example two independent x/y profile FFTs concurrently or two independent direct-DFT outputs per logical lane. Adding idle or duplicative lanes does not improve latency and may increase register allocation and barrier cost.

The strongest alternative is one bead per block but process independent pairs concurrently where possible:

- x and y profile formation;
- x and y 120-point forward transforms;
- corresponding refinement paths if they are independent;
- radial/SSD work after both coordinates converge.

If cuFFTDx permits `FFTsPerBlock<2>` for the chosen FP64/120/sm_75 descriptor, this could naturally calculate x and y together. NVIDIA defines each FFT as being handled by a separate thread group in the block. [FFTsPerBlock documentation](https://docs.nvidia.com/cuda/cufftdx/api/operators.html)

Finally, attack the biggest architectural assumption first: a single launch removes CUDA launch overhead, but it does not automatically remove the reported 3.5횞 LabVIEW overhead if that overhead is DLL-call marshalling, context synchronisation, pageable copies, or a forced device synchronization. Before the rewrite, cheaply measure four timestamps separately: LabVIEW?묭LL entry, H2D, kernel/FFT region via CUDA events, and D2H/synchronization. Otherwise you may optimise 1.5 ms of GPU orchestration while retaining the dominant LabVIEW boundary cost.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
