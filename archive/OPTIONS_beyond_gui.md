---
type: narrative
status: historical
date: 2026-08-26
tags: [archive, gui]
---

# Options beyond GUI automation — what is possible, what is already done, what to avoid

**Context (user, 2026-08-26):** if the new grounder pipeline is not fast/accurate enough, could we
(a) export LabVIEW code as a script and edit it as text, (b) write a DLL and call it from LabVIEW,
or (c) extract LabVIEW's core built-in functions as DLLs? Answered from what is actually on this
machine, not from memory.

## First: what the kernel's hot path really is

Byte-level dependency scan of `Track 1 of N bds xyz-kernel-reentrant.vi` and its helpers:

```
Track 1 of N bds xyz-kernel-reentrant.vi
 ├─ rect coord from center.vi                      (ROI crop)
 ├─ Omars IMAQ ImageToArray.vi                     (IMAQ image -> 2D array)   ← NI Vision
 ├─ tracking-prep avgx,y profiles.vi
 ├─ tracking-average x,y in cross.vi
 ├─ tracking-find avg profile center.vi
 ├─ tracking-calculate radial profile-openv2.vi
 ├─ Tracking-prep I of r.vi
 │    └─ Real FFT.vi / FFT.vi / Inverse FFT.vi  →  NI_AALPro.lvlib  →  **lvanlys.dll**
 ├─ Tracking-fit prepped I of r to cal.vi
 ├─ tracking-calculate phase in neighborhood.vi
 └─ tracking- quadratic fit to phase nghbrd.vi
```

**The numerically heavy parts — FFTs — already run in a native DLL: `lvanlys.dll`** (LabVIEW's
Advanced Analysis Library, backed by Intel MKL; both present under `Program Files\National
Instruments\`). Image access goes through NI Vision (IMAQ), also native. The G code around them is
glue: ROI cropping, profile averaging, phase calculation, quadratic fitting. That reshapes all three
of the user's options.

## (c) "Extract LabVIEW's core functions as DLLs" — not needed, and not permitted

- **Not needed:** the core numerics are *already* native (`lvanlys.dll`, MKL, NI Vision). There is
  nothing to extract; LabVIEW is already calling compiled code for the FFTs.
- **Not permitted:** `lvanlys.dll` is proprietary NI software under the LabVIEW EULA. Reverse
  engineering or redistributing it is a licence violation. Calling it *from within LabVIEW* is what
  it is for; pulling it out is not. Do not pursue this.
- If native FFT is wanted **outside** LabVIEW, use a free library (FFTW — GPL, or KissFFT — BSD, or
  NumPy/SciPy) rather than NI's.

## (b) "Write a DLL and call it from LabVIEW" — possible, standard, and the right long-term move

This is the **Call Library Function Node** (CLFN) — an official, documented, supported mechanism.
LabVIEW ships the headers for it (`cintools\extcode.h`, `fundtypes.h`, `ILVDataInterface.h` are on
this machine). A C/C++/Rust function exported from a DLL can take a 2D image array plus calibration
data and return x, y, z per bead. Inside the DLL you own the threading — an OpenMP `parallel for`
over beads, or one thread per bead — with no LabVIEW loop, no shift registers, no `P` terminal.

Why it is attractive *for this specific kernel*:
- The per-bead work is **embarrassingly parallel** (each bead crops its own ROI; no shared state).
- The G glue between the FFTs is exactly the kind of code that is faster and clearer in C.
- It side-steps the entire "make LabVIEW's loop parallel" problem that the project has been fighting.

Costs, stated honestly:
- **No C compiler is installed on this machine** (no `cl`, `gcc`, `clang`; no Visual Studio). Building
  a DLL means installing one — MSVC Build Tools or MinGW-w64. That is a system change to request.
- Data marshalling must be exact: LabVIEW 2D arrays arrive as a handle or as a flat row-major
  buffer with dims, depending on the CLFN configuration. Getting this wrong crashes LabVIEW — on a
  machine that runs live experiments. Develop and test on a copy, never on the rig's live VI.
- Debugging a DLL from inside LabVIEW is harder than debugging G.
- **The algorithm must be re-implemented and validated bit-for-bit against the existing kernel**
  (radial profile, phase neighbourhood, quadratic fit). That is real scientific-software work, and
  the validation is the expensive part, not the C.

**Recommended shape if pursued:** write the DLL in **Rust** or C with **no LabVIEW-specific types**
at the boundary — plain `float*` + dimensions in, `float*` out — so it is testable from Python with
the same arrays before it ever touches LabVIEW. Call it from a *new* wrapper VI in `claudeDev`.

## (a) "Export LabVIEW code as a script and edit it as text" — partially exists, with a big caveat

A `.vi` is a compiled binary; **there is no official text form of a block diagram.** Three things
approximate it:

| route | what it gives | status here |
|---|---|---|
| **VI Scripting** (what we have) | programmatic *editing* of the diagram, not a text dump | **working**; `KernelBuilder_v1.vi` in progress |
| **Zuehlke labview-mcp** read path | VI → "AIXML" text via LabVIEW 2026's private `lvai` gRPC | machine qualifies (26.3 Q3); **not tried**; edit path reported broken by its author; undocumented API, no stability promise |
| **VI Snippet PNG** | a PNG carrying the binary diagram — movable, not human-editable | compiles on 2026; **not functionally tested** |

So "edit the code as text" in the ordinary sense is **not available**. What *is* available is
"edit the code as a program" (VI Scripting), which is what the driver does. The AIXML read path is
worth one bounded experiment purely to *read* wiring as text — that would help comprehension a lot —
but building an edit workflow on it is unwise.

## (1) Benchmark the new pipeline — yes, and here is the design

The existing `BENCHMARK_gui_control.md` measured *models*. The new question is *pipelines*. Same
three-step task (place For Loop, place constant, wire to `N`) on scratch VIs, five configurations:

| # | configuration | what it isolates |
|---|---|---|
| A | Claude + composite tools (`probe`/`wire`) | current baseline — **31 calls / SUCCESS** already measured (Opus) |
| B | Claude + UI-TARS grounder (`--zoom`) for every "find X" | does local grounding cut round-trips? |
| C | Claude + UI-TARS 1× only | is the zoom pass earning its 6 s? |
| D | Claude + Gemini executor (needs `GEMINI_API_KEY`) | hosted vision vs local |
| E | **VI Scripting driver, one Run** | the ceiling: what "no GUI at all" costs |

Metrics per run, all already logged by the tools: **tool calls · wall-clock · model wait (s) ·
misclicks (probe-verified) · human interventions**. Predictions on file so they can be wrong:
E ≪ B < A; C ≈ A (1× misses small targets); D unknown.

**Do not run this during the experiment.** Every config drives LabVIEW; one path at a time.

## Bottom line

| option | verdict |
|---|---|
| (c) extract NI's DLLs | **No** — already native, and a licence violation |
| (b) own DLL via CLFN | **Yes, and probably the best long-term answer** for the kernel; needs a compiler installed and rigorous validation against the existing algorithm |
| (a) text export | **Not really** — VI Scripting is the real "edit as program" path; AIXML worth one read-only experiment |
| (1) benchmark | **Yes** — design above; run after the experiment |

The DLL route is the one that genuinely removes the problem instead of automating around it.
