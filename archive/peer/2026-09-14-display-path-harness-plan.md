---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, plan]
---

# display-path-harness-plan

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (83s)
- **why asked:** plan review before building the display-path measurement harness (work-order item 4).
- **verdict:** ACTED ON: two named conditions (panel closed = construction cost; panel open = representative, coalescing stated); `IMAQdx Get Image` removed from the measured chain (file replaces acquisition); the IMAQ Image Display control declared NOT measured (no donor control); fixture asserted 1280x1024 8-bit via PIL before timing; timing by the accepted pattern (one Run per frame, perf_counter, base-subtracted) instead of Tick Count; frames alternate so the image changes every run. Recipe tools/recipes/build_harness_display.py, runner tools/bench/run_display_bench.py.

## Question

PLAN REVIEW (attack; be concrete; cite NI docs for the VIs). GOAL (work order item 4, 'display path cost'): measure, inside LabVIEW on the recorded fixture (no camera, no hardware), the per-frame cost of the main VI's display route on diagram 99: IMAQdx Get Image -> IMAQ ImageToArray -> Flatten Pixmap.vi -> Draw Flattened Pixmap.vi (docs: 'the slowest documented path'), for a 1280x1024 U8 image, against the 6 ms/frame budget at 150 Hz. Also measure the cheaper alternatives NI documents for showing an IMAQ image so the restructuring can pick: (a) the IMAQ Image Display control (WindDraw-free, in-process) fed directly with the image reference (zero copy), (b) IMAQ ImageToArray only (the copy cost alone), (c) Flatten Pixmap only. HARNESS BY SCRIPT (our fleet: drop_subvi of vi.lib VIs by path, build_property/build_invoke, wire by terminal name, create_indicator, for_loop, tunnel indicators; verified pattern = tools/recipes/build_harness_gpu2.py which built IMAQ Create -> IMAQ ReadFile -> GetImagePixelPtr -> CLFN with 14 controls and timed 200 frames): HARNESS_display_v0.vi = IMAQ Create + IMAQ ReadFile(fixture PNG/TIFF path control) once, then a For loop N=200 with Tick Count (ms) before/after each stage, stages selectable by a control (0 = ImageToArray only, 1 = + Flatten Pixmap, 2 = + Draw Flattened Pixmap into a Picture indicator, 3 = Image Display control write via its Value property?), outputs: ms/frame per stage (median over 200), array indicators for the raw per-frame times. Run headless via COM (Run + read indicators), 3 repeats, machine quiet (clock-lock P0 as in earlier benches). ATTACK: (1) is 'Draw Flattened Pixmap' into a Picture indicator measurable without the front panel being visible/updated - does a Picture indicator's update run on the UI thread only when the panel is open, so a headless Run understates the real cost; conversely does opening the panel (FP visible) make the measurement representative of the running experiment (the user's actual mode)? (2) the IMAQ Image Display control route: can our fleet create such a control by script (create_control on a terminal typed IMAQ image? New VI Object with a .ctl path from vi.lib?) - if not, what is measurable without it? (3) fixture: the recorded frames are in which format (the earlier gpu harness read a file via IMAQ ReadFile - reuse) - any risk the on-disk image is not 1280x1024 U8 (state the check). (4) timing method: Tick Count (ms) resolution is 1 ms against a ~1-3 ms effect - propose the right primitive (High Resolution Relative Seconds.vi in vi.lib\Utility? or 'Get Date/Time in Seconds'?) and whether our fleet can drop it (a vi.lib VI = drop_subvi OK). (5) what in this plan would silently measure the wrong thing (e.g. constant folding, the loop's own overhead, the image never changing so LabVIEW skips redraws?) and the cheapest control for each (e.g. alternate two different images).

## Answer

Verdict: revise the harness before building it. As written, it will likely under-measure display cost, cannot measure `IMAQdx Get Image` from a recorded file, and does not test the recommended Image Display route equivalently.

1. Front-panel rendering: headless is not representative

`Draw Flattened Pixmap.vi` produces LabVIEW picture data; writing that data to a Picture indicator is a separate front-panel update. NI says front panels update asynchronously by default, so completion of the terminal write does not prove that the pixels were rendered before the ?쏿fter??timestamp. Enabling Synchronous Display forces each value to update immediately, but intentionally prioritizes rendering over execution. [NI: How to Force Update a LabVIEW Front Panel](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000g0R1SAI&l=en-US)

Therefore run two explicitly named conditions:

- `compute-only`: panel closed; consume the picture string without a display terminal.
- `representative-visible`: front panel open, normal size and position, Picture indicator visible and unobscured, with the same Synchronous Display setting as the main experiment.
- Optional diagnostic: visible plus Synchronous Display enabled. This is the defensible ?쐃very frame was actually presented??upper-bound test.

Do not call the headless result ?쐂isplay cost.??Call it `ImageToArray + Flatten + Draw picture construction cost`. NI describes `Draw Flattened Pixmap.vi` as generating picture data that can be wired to a Picture indicator; that documentation does not promise that the indicator has painted before the subVI returns. [NI: Flatten/Unflatten Pixmap purpose](https://digital.ni.com/public.nsf/allkb/390B634D95072A4586256EF6004B75C6)

Opening the panel is necessary but insufficient: asynchronous coalescing can still skip intermediate paints. Test both the main VI?셲 actual asynchronous configuration and a synchronous diagnostic.

2. The Image Display comparison must use a terminal, not Value

NI?셲 documented normal route is to wire an IMAQ image directly to the Image Display terminal. [NI Vision manual, ?쏛n Image Wired into the Image Display Control Terminal??(https://download.ni.com/support/manuals/371007a.pdf) The control displays the image buffer referenced by the IMAQ image value; outside Snapshot mode it reflects the buffer currently wired to it. [NI: Programmatically Clear an Image Display Control](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019MA0SAM)

A `Value` property write is a different and slower operation:

- It introduces a UI-thread property-node call.
- NI says Value property nodes must update the panel item every time and are slower than terminals because of reference dereferencing. [NI: terminal/local/Value-property differences](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019LXrSAM)
- It is documented as the workaround for updating a caller?셲 Image Display from a subVI, not as the ordinary direct-display path. [NI: Updating a Main VI Image Display From a SubVI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019M2pSAE&l=en-US)

Recommendation:

- Primary alternative: a real Image Display terminal inside the loop, wired directly.
- Secondary, separately labelled measurement: `Image Display.Value property`, only if the intended architecture actually crosses a subVI boundary that requires it.
- Do not describe either route as ?쐚ero copy??without a measurement or more precise NI documentation. NI confirms that the IMAQ wire is a reference to a preallocated image buffer, but that does not prove the display backend performs no internal conversion/upload. [NI: IMAQ images are buffer references](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P8khSAC)

Fleet feasibility: `create_control` on an IMAQ image terminal will likely create the ordinary IMAQ image-reference control, not an Image Display object. The safest construction route is a tiny donor VI containing one Image Display control, copied into the harness. If no donor/copy operation is available, the fleet can still measure:

- `ImageToArray`
- `ImageToArray + Flatten Pixmap`
- `ImageToArray + Flatten Pixmap + Draw Flattened Pixmap`
- Picture-terminal update

But it cannot honestly claim to have measured the native Image Display alternative. NI identifies Image Display as a distinct Vision-installed front-panel control. [NI: IMAQ Image Display Control](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YI6eCAG&l=en-US)

3. The fixture cannot exercise `IMAQdx Get Image`

`IMAQ ReadFile` replaces acquisition; it does not emulate or time `IMAQdx Get Image`. Thus the recorded-fixture harness can measure only the downstream route:

`preloaded IMAQ buffer ??ImageToArray ??Flatten ??Draw ??indicator`

Report acquisition separately from the existing camera benchmark, or remove `IMAQdx Get Image` from this work item?셲 measured-chain label. Adding `IMAQ ReadFile` inside the timed loop would instead measure disk decoding and filesystem/cache behavior?봞lso the wrong thing.

After the one-time read, assert before timing:

- width = 1280;
- height = 1024;
- image type = U8;
- row stride if any pointer-based interpretation is involved;
- the decoded fixture is lossless and has expected checksum/min/max or selected pixel values.

PNG and TIFF are acceptable for U8, but the assertion must be made on the resulting IMAQ buffer, not inferred from the filename extension.

4. Replace Tick Count; do not use Get Date/Time

NI says `Tick Count (ms)` has only 1 ms precision and recommends `High Resolution Relative Seconds.vi` for higher-resolution measurements. `Get Date/Time in Seconds` uses the operating-system clock and is not the better benchmark primitive. [NI: Benchmarking LabVIEW Code](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P839SAC&l=en-US)

Use:

`<vilib>:\Utility\High Resolution Relative Seconds.vi`

It is a vi.lib subVI, so `drop_subvi` is the appropriate fleet route. The known physical path is `vi.lib\Utility\High Resolution Relative Seconds.vi`; verify its installed path before specifying the build.

Still measure timer overhead:

- back-to-back timer calls, 200??0,000 iterations;
- same loop/tunnel/array instrumentation as the real stage;
- report the raw baseline and baseline-adjusted results.

For sub-millisecond stages, prefer total batch duration divided by N over a median of individually timed calls. Individual samples are valuable for jitter, but Windows scheduling and timer-call overhead can dominate them.

5. Silent wrong-measurement risks and cheap controls

| Risk | Cheapest effective control |
|---|---|
| Asynchronous indicator update occurs after the timestamp | Visible-panel run plus Synchronous Display diagnostic |
| Panel closed causes paint work to be omitted/coalesced | Report closed and visible runs separately |
| Same IMAQ reference and unchanged buffer suppress redraw | Preload two distinct same-size U8 buffers and alternate references A/B |
| Image Display sees the same reference while its contents change out of dataflow order | Use two buffers and explicit error/data dependency; never modify the buffer being displayed |
| Constant fixture lets compiler move pure work outside the loop | Feed alternating buffers through an auto-indexed input or shift-register selection and make each iteration?셲 output observably consumed |
| Compiler eliminates an unused result | Accumulate a cheap checksum/length from the output and expose it after the loop |
| Picture strings grow cumulatively | Wire an empty picture input to `Draw Flattened Pixmap` every iteration unless diagram 99 intentionally accumulates commands |
| Cumulative modes cannot isolate stage cost reliably | Build isolated cases with identical timer and loop scaffolding; use subtraction only as a cross-check |
| First call pays allocation/load/cache costs | Run untimed warm-up iterations, then measure; preserve first-call data separately |
| Auto-indexing output arrays allocate or resize during timing | Preallocate fixed-size timing arrays or include identical collection overhead in the empty baseline |
| `N=200` at full-rate visible rendering queues work after the loop | Also measure end-to-end wall time through a forced final update; inspect whether 200 distinct frames were actually presented |
| Median hides missed 6.67 ms deadlines | Report median, p95, p99, maximum, and count over 6.0 ms and 6.667 ms |
| P0/clock lock changes the production environment | Record it in results and include one ordinary-clock confirmation run |
| Scaling/zoom changes renderer cost | Match the main VI control bounds, zoom mode, interpolation, ROI/tools visibility, and monitor/DPI |
| COM indicator reads add time | Read outputs only after the VI finishes, as proposed |
| File decode accidentally included | `IMAQ ReadFile` strictly outside all timed loops |
| ?쏤latten only??accidentally includes ImageToArray | Keep a precomputed compatible pixmap input for an actual Flatten-only case; otherwise label it cumulative |

One nomenclature correction: I could verify that NI documents Picture/Intensity Graph as routes that require extracting the pixel array, while the native Image Display accepts the IMAQ image directly. [NI: Display Images with NI Vision](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019M7zSAE&l=en-US) I did not find an NI source declaring the conversion/flatten/draw chain ?쐔he slowest documented path.??Unless that exact source is already recorded, label it ?쐔he current multi-conversion Picture path,??not an NI-documented superlative.

Recommended harness outputs:

- isolated compute time for each stage;
- visible asynchronous terminal-write throughput;
- visible synchronous-render upper bound;
- native Image Display direct-terminal result, only after obtaining a typed donor;
- raw high-resolution samples plus median/p95/p99/max;
- deadline-miss counts at 6.0 ms and 6.667 ms;
- fixture dimensions/type validation and output checksum;
- empty-loop/timer baseline;
- three warmed repeats with first-call behavior retained separately.

This separates conversion cost, picture construction, update enqueueing, and forced presentation?봳he four quantities the current single mode-0?? harness would conflate.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
