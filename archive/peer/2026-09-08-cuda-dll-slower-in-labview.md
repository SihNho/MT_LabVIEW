---
type: peer-review
status: historical
date: 2026-09-08
tags: [peer-review]
---

# cuda-dll-slower-in-labview

- **agent:** codex
- **date:** 2026-09-08
- **outcome:** ANSWERED (125s)
- **why asked:** failed prediction — the DLL's own timer reads 1.5 ms from Python but 5.4 ms inside LabVIEW (200-frame medians); mandatory devil's-advocate review before explaining it.
- **verdict:** being tested on the machine: phase split (chain 11) shows upload 0.34→1.58 ms, kernels 0.96→3.40 ms, readback 0.11→0.18 ms — every CUDA call uniformly ~3.5-4.5× slower, i.e. host-side latency; chain 12 adds cudaEvent GPU time (e=) and UI-thread detection (ui=) to discriminate the peer's #1 (UI thread) from #2 (GPU timeline).

## Question

Devil's-advocate + search. Windows 10, LabVIEW 2026 64-bit, RTX 2060 (driver 616.64, CUDA 12.6 runtime, cuFFT). A CUDA DLL (about 100 small kernel launches + 2 cuFFT batched plans + one 1.3 MB pageable host-to-device cudaMemcpy + a few small device-to-host copies, synchronous, default stream) is called once per frame. Measured with QueryPerformanceCounter INSIDE the DLL around the whole track call: from a Python ctypes loop it takes 1.5-1.7 ms per call (also with 5-20 ms sleeps between calls, so GPU clock ramp-down is ruled out). Called from a LabVIEW Call Library Function Node (node copied from a 2013 demo VI; thread setting unknown - could be 'Run in UI thread' or 'Run in any thread'; the VI is started via VI Server from a Python COM client each frame), the SAME internal timer reads 5.4 ms median over 200 calls (3.5x slower), outputs identical. Question 1: what mechanisms could make the same CUDA work run 3.5x slower when the caller is LabVIEW? Consider: CLFN 'Run in UI thread' vs any-thread (does the UI thread's message pumping or priority affect CUDA driver calls?), CUDA context/thread affinity when LabVIEW's execution system calls from different pooled threads each time (primary context per-thread state, cudaSetDevice cost), WDDM GPU scheduling and LabVIEW's own GPU/Direct2D use for panel drawing (front panel might be open), pageable memcpy from LabVIEW-allocated handles vs numpy memory (alignment, large-page), power/priority differences (Python process foreground?), Windows timer resolution (LabVIEW sets 1 ms timeBeginPeriod?) affecting cudaDeviceSynchronize spin/yield behaviour (cudaDeviceScheduleAuto/Yield/BlockingSync!). Question 2: rank these by likelihood and give the cheapest discriminating test for each that a script can run (e.g. cudaSetDeviceFlags(cudaDeviceScheduleSpin) in the DLL, pinned host buffer, cudaEvent timing of GPU-only time vs wall time, closing the front panel, reading the CLFN thread setting via VI Scripting CallLibrary.'Any Thread?' 636D403). Cite NVIDIA docs / NI docs / forum evidence with URLs.

## Answer

The strongest discriminator is to split the 5.4 ms into GPU timeline versus host-side submission/wait time. My leading hypothesis is not ?쏞UDA computes differently under LabVIEW,??but that the LabVIEW process/thread is delayed while submitting or synchronizing?봫ost plausibly by UI-thread contention, WDDM/display contention, or CUDA?셲 host-wait policy.

## Likelihood ranking

| Rank | Mechanism | Assessment | Cheapest decisive test |
|---|---|---|---|
| 1 | CLFN running in LabVIEW?셲 UI thread | High | Read `CallLibrary.'Any Thread?'` (`636D403`) through the existing reporter/VI-Scripting path; then compare an otherwise identical copy configured ?쏳un in any thread.??|
| 2 | Host-side launch/synchronization latency under WDDM, possibly amplified by display/UI activity | High?뱈edium | Add CUDA events around the stream workload and return both GPU-event time and QPC wall time. Repeat with the front panel closed/minimized and display updates disabled. |
| 3 | CUDA synchronization scheduling policy: Auto/Yield/Blocking versus Spin | Medium | Set `cudaDeviceScheduleSpin` once, before CUDA initialization, and compare QPC minus CUDA-event time. Also report the effective flags with `cudaGetDeviceFlags`. |
| 4 | Different pageable-source behavior or hidden LabVIEW data copying | Medium?뱇ow | Copy the incoming 1.3 MB immediately into a persistent `cudaHostAlloc` buffer, outside the timed region if testing the CUDA path, then use that pinned buffer for H?묭. Separately time the CPU staging copy and H?묭 copy. |
| 5 | Calls arriving on different LabVIEW execution threads | Low?뱈edium | Log Windows thread ID, `cudaGetDevice`, `cuCtxGetCurrent`, and first-call-on-this-thread status on every invocation. Force the calling VI to one execution system/thread and compare. |
| 6 | Competing CUDA contexts or another CUDA consumer in the LabVIEW process | Low, unless another plugin uses CUDA | Log the current `CUcontext`; query primary-context state; capture Nsight Systems or ETW once if permitted. Search the LabVIEW process for other CUDA-using modules. |
| 7 | Foreground-process priority or CPU affinity differences | Low | Match process priority/affinity between Python and LabVIEW, then repeat. Log thread priority inside the DLL. |
| 8 | Windows timer resolution / `timeBeginPeriod` | Very low as a direct explanation | QPC is already independent of timer tick resolution. Still compare Spin and BlockingSync; do not treat a `timeBeginPeriod` change itself as proof. |
| 9 | Ordinary pointer alignment or ?쐋arge pages??| Very low | Benchmark exactly the received pointer versus a deliberately aligned pageable buffer and a pinned buffer. Large pages are not the relevant control for PCIe DMA. |

## Why the UI-thread hypothesis is plausible?봟ut not sufficient by itself

NI says a CLFN not declared thread-safe runs in the LabVIEW UI thread, and that configuring a thread-safe call as reentrant/?쏳un in any thread??can improve performance. The UI thread is shared with front-panel work and other UI-related operations. [NI: Access DLLs or Shared Libraries](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YGZjCAO&l=en-US), [NI: CLFN slowing an application](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA0VU000000A0bR0AS&l=en-US)

However, because QPC starts **inside** the DLL, merely waiting to enter the UI thread is excluded. UI-thread execution explains the 5.4 ms only if that thread is preempted or participates in UI/message work while the DLL is submitting/waiting, or if its scheduling behavior changes CUDA synchronization latency. NI forum reports support extra jitter and thread-switch effects, but they do not establish a 3.5횞 CUDA slowdown inside the native call. [NI forum discussion](https://forums.ni.com/t5/LabVIEW/DLL-execution-time/td-p/2739350)

Also, a synchronous DLL call does not normally ?쐏ump LabVIEW messages from inside CUDA.??The better hypothesis is CPU scheduling/contention, not reentrant execution of LabVIEW UI work within `cudaDeviceSynchronize`.

So the first cheap test is:

1. Read the CLFN setting via the existing non-executing reporter.
2. If it is UI-thread, create/test a manager-controlled ?쏿ny thread??variant only if the DLL is thread-safe.
3. Log `GetCurrentThreadId()` inside the DLL.

If ?쏿ny thread??immediately restores ~1.6 ms, the mechanism is established operationally, though CUDA-event timing is still useful to determine whether the saved time was submission or synchronization.

## CUDA context/thread affinity is probably not the main cause

CUDA?셲 runtime primary context is one per device per process and is shared by runtime users. When a host thread has no current explicit context, the runtime selects and makes the device?셲 primary context current as needed. `cudaSetDevice()` makes that primary context current to the calling host thread. [NVIDIA Runtime API: primary contexts](https://docs.nvidia.com/cuda/cuda-runtime-api/group__CUDART__DRIVER.html)

Therefore, changing LabVIEW worker threads does **not normally create a fresh CUDA context per call**. It may require thread-local current-context setup on a thread?셲 first CUDA use, but a stable 5.4 ms median across 200 calls is difficult to explain that way unless LabVIEW continually uses many new threads, the DLL explicitly creates contexts, or it resets the device/context. NVIDIA explicitly warns that multiple contexts per device add context-switching costs and substantially degrade performance. [NVIDIA driver/runtime context comparison](https://docs.nvidia.com/cuda/cuda-driver-api/driver-vs-runtime-api.html)

Cheap instrumentation per call:

```text
GetCurrentThreadId()
cudaGetDevice()
cuCtxGetCurrent()
cudaGetDeviceFlags()
```

Also record whether that thread ID has been observed previously. Interpret results as follows:

- Changing thread ID, same non-null context, no first-use-only penalty: thread migration is exonerated.
- Slow only on each thread?셲 first call: thread-local CUDA initialization is implicated.
- Different `CUcontext` handles: investigate explicit context creation immediately.
- Null context on entry followed by slowdown: time `cudaSetDevice(0)` separately, once per newly observed thread.

Do not call `cudaDeviceReset()` between frames; NVIDIA says it deinitializes the primary context and the next qualifying CUDA call must initialize it again. [NVIDIA Runtime API](https://docs.nvidia.com/cuda/cuda-runtime-api/group__CUDART__DRIVER.html)

## WDDM and front-panel rendering

The RTX 2060 is a display-class GeForce device and therefore normally uses WDDM rather than TCC. NVIDIA documents that TCC reduces kernel-launch latency and that ordinary display devices use WDDM; GeForce devices generally cannot switch to TCC. [NVIDIA Windows installation guide](https://docs.nvidia.com/cuda/archive/11.5.1/cuda-installation-guide-microsoft-windows/index.html)

With roughly 100 small launches, a few tens of microseconds of extra host/driver delay per launch is enough to produce several milliseconds. LabVIEW does not inherently make WDDM slower, but an open, frequently redrawn front panel can generate graphics work in the same process and on the same display GPU. That could introduce GPU scheduling gaps or CPU contention in the LabVIEW UI thread.

Cheap test matrix:

- front panel open and updating;
- front panel open but all graph/image updates disabled;
- front panel closed;
- LabVIEW window minimized;
- monitor/display attached to another GPU, if already available.

The conclusive observation is CUDA-event time:

- **CUDA event ??.5 ms, QPC ??.4 ms:** delay is host submission, synchronization wake-up, or CPU preemption.
- **CUDA event ??.4 ms:** the GPU timeline itself is delayed?봚DDM contention, other GPU work, or changed GPU clocks/work scheduling.
- **CUDA event intermediate:** both mechanisms contribute.

CUDA events timestamp work on the GPU clock and are OS-timer independent. NVIDIA recommends them for GPU execution timing. [NVIDIA CUDA Best Practices: GPU timers](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html?highlight=bank)

Place events in the same stream immediately before the first GPU operation and after the last GPU operation. Do not include CPU preprocessing. Because everything is in the default stream, this should give a meaningful GPU timeline, assuming the DLL and cuFFT plans really use that same stream.

## Spin/Yield/BlockingSync could readily account for host-wall differences

NVIDIA defines:

- `cudaDeviceScheduleSpin`: actively spin while waiting, reducing latency at the cost of CPU resources.
- `cudaDeviceScheduleYield`: yield the host thread while waiting, potentially increasing latency.
- `cudaDeviceScheduleBlockingSync`: wait on a synchronization primitive.
- `cudaDeviceScheduleAuto`: choose behavior heuristically.

These flags govern how the host thread interacts with the OS scheduler while waiting for GPU results. [NVIDIA primary-context scheduling flags](https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__PRIMARY__CTX.html)

This is unusually relevant because your workload synchronizes every ~1.5 ms. A yielding or blocking LabVIEW UI thread can incur millisecond-scale wake-up latency that a spinning Python thread avoids.

Test at process/DLL initialization, before creating plans or doing other CUDA work:

```cpp
cudaSetDeviceFlags(cudaDeviceScheduleSpin);
cudaSetDevice(0);
```

Then report the actual flags and repeat with `Yield` and `BlockingSync`. Do this in separate fresh processes where possible so initialization history cannot contaminate the comparison.

Devil?셲 advocate: both executables should normally start with `Auto`, so caller identity alone should not change the flag. A large result from forcing Spin would show that host wake-up policy matters, but not necessarily that Python and LabVIEW originally had different flags. Record the effective flags in both processes.

`timeBeginPeriod(1)` is unlikely to directly affect QPC or GPU execution. It might indirectly affect scheduler wake-up behavior under a blocking/yielding policy, but CUDA?셲 documented scheduling flag is the cleaner experimental control. CUDA-event timing is explicitly independent of OS timer resolution. [NVIDIA CUDA Best Practices](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html?highlight=bank)

## Pageable LabVIEW memory

Pinned host memory can provide higher transfer bandwidth, and NVIDIA provides `cudaHostAlloc` and `cudaHostRegister` for this purpose. Registration itself is heavyweight and should not be performed every frame. [NVIDIA pinned-memory guidance](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html?highlight=bank)

Still, 1.3 MB alone is unlikely to explain an additional 3.8 ms unless:

- the LabVIEW pointer causes expensive pageable staging;
- the DLL or CLFN configuration triggers an extra copy;
- the source pages are cold or repeatedly faulted;
- LabVIEW is relocating/copying a handle-backed array;
- Python is actually providing pinned or otherwise better-resident storage.

Plain NumPy allocations are generally pageable unless explicitly registered, so ?쏯umPy versus LabVIEW??is not automatically ?쐏inned versus pageable.??Treat that as an inference to verify experimentally, not an assumption.

Best test:

1. Allocate one persistent pinned staging buffer with `cudaHostAlloc`.
2. CPU-copy the supplied input into it.
3. Time the CPU copy separately.
4. Time the pinned H?묭 copy separately.
5. Compare against direct H?묭 from the supplied pointer.
6. Do the identical staging experiment in both Python and LabVIEW.

If direct LabVIEW input is slow but pinned staging normalizes the total, memory provenance matters. If the H?묭 CUDA-event interval is already similar in both callers, it does not.

Ordinary alignment is unlikely to add several milliseconds for a 1.3 MB synchronous transfer. Page-locked status and hidden copies are much more meaningful than large-page backing.

## Recommended experiment order

1. Read `Any Thread?` and log thread ID/context/device/flags.
2. Add CUDA-event timing and per-phase QPC timing:
   - input preparation;
   - H?묭;
   - kernel launches/cuFFT;
   - D?묱;
   - final synchronization.
3. Close the front panel or suppress all display updates.
4. Compare Spin, Yield, and BlockingSync in fresh processes.
5. Try persistent pinned staging.
6. Only then investigate affinity, foreground priority, timer resolution, and pointer alignment.

My predicted outcomes are: GPU-event time remains near 1.5?? ms while the missing ~3?? ms appears in a host synchronization or launch interval; changing the CLFN away from the UI thread and/or forcing Spin substantially removes it. If instead CUDA events themselves report ~5 ms, focus on WDDM/display contention and per-launch gaps, ideally with a short Nsight Systems trace.

## Sources

(extract from answer)

## What was done with it

Instrumented the DLL exactly as advised (QPC per phase, cudaEvent around the GPU section, GetCurrentThreadId vs the LabVIEW window thread); results in archive/bench-2026-09-07-gpu-reference/REPORT.md addendum (row 3).
