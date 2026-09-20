---
type: peer-review
status: historical
date: 2026-09-12
tags: [peer-review, camera]
disposition: legacy
---

# camera-halving-attack

- **agent:** codex
- **date:** 2026-09-12
- **outcome:** ANSWERED (61s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK MY DIAGNOSIS. Do not confirm it. Find the explanation I am missing.

SETUP: LabVIEW magnetic-tweezers rig. Camera = JAI SP-5000M-USB (e2v Lince5M, 2560x2048, 8-bit mono, USB3 Vision), driven by NI-IMAQdx, IMAQdx name "cam1". Run at 2x2 binning, so the full binned frame is 1280x1024.

USER SYMPTOM (verbatim): "코드 처음 가동하면 카메라 사이즈가 절반으로 줄어버리더라" (first run of the code halves the camera size), "두 번 작동하면 사이즈 원상복구되" (running it a second time restores it), "property node로 입력되는 상수값이거든, 그래서 그런지 이미지 값도 작게 보여" (it is a constant fed into a property node, and the image looks small too).

WHAT I MEASURED TODAY (ctypes against niimaqdx.dll, no LabVIEW):
1. First open of cam1: Width=640, Height=512, BinningHorizontal=2, BinningVertical=2, OffsetX=0, OffsetY=0, PixelFormat 8-bit mono, PayloadSize=327680, AcquisitionFrameRate=90.0009.
2. A second open minutes later, nothing else touching the rig: Width=1280, Height=1024, same binning, offsets still 0.
3. Attribute ranges at 1280x1024: Width (min 8, max 1280, inc 8), Height (min 8, max 1024, inc 2), AcquisitionFrameRateRaw (frame period in us) min 4033 => ceiling 247.95 Hz. WidthMax/HeightMax report 2560/2048, i.e. UNBINNED units, while Width/Height are in BINNED units.

WHAT I FOUND IN THE MAIN VI (offline byte scan of the .vi, zlib streams):
4. The main VI references exactly six IMAQdx VIs: Open Camera, Configure Grab, Get Image, Grab, Stop Acquisition, Close Camera. NO IMAQdx Set Attribute VI, no IMAQdx Property Node helper VIs.
5. No GenICam attribute path strings ("CameraAttributes::...") anywhere in the file.
6. The literal strings "Width", "Height", "Width&2", "Height&2" DO appear; "Width&2"/"Height&2" sit immediately before the literal "IMAQdx" in the same stream, which I read as an IMAQdx property node with Width and Height terminals. Separately there are front-panel numeric controls labelled Width and Height (stored as "DigNum (strict)") read via Value property nodes.
7. The string "Binning" does not appear ANYWHERE in the main VI file.

HYPOTHESES I HAVE ALREADY KILLED:
- H1 GenICam clamping (Width <= MaxWidth - OffsetX with a leftover non-zero offset): FALSIFIED, both offsets are 0.
- H2 write-order bug (write Width while binning is 1, then set binning 2, camera divides width): FALSIFIED, the main VI never writes binning at all.
- H3 the camera persists the halved state across sessions: FALSIFIED, a fresh IMAQdxOpenCamera already reads back the full 1280x1024.

QUESTIONS, and please answer them by attacking rather than agreeing:
A. Given observation 6+7, what mechanism makes an IMAQdx property node write of Width/Height produce exactly HALF the expected size on the first run and the correct size on the second? Consider specifically: unit confusion between binned and unbinned coordinates in the IMAQdx property node; the order Width-then-Height vs Height-then-Width; whether writing Width/Height while an acquisition is configured (IMAQdx Configure Grab already called) behaves differently from writing before; and whether IMAQdx caches/needs a re-read after a write.
B. Is my inference in 6 sound, that "Width&2"/"Height&2" before the literal "IMAQdx" means an IMAQdx property node? What ELSE in LabVIEW produces those exact strings? Note the VI also contains an IMAQ Image Display / Vision acquisition typedef (NI_Vision_Acquisition_Software.lvlib was also in the strings).
C. Is there a completely different reading of the symptom I am not entertaining - e.g. the IMAQ IMAGE buffer (not the camera) being the thing that is half size, or an IMAQ Image Display control zoom/scale factor, or the display being half while the acquired frame is full?
D. What is the single cheapest DISCRIMINATING test that separates your best alternative from mine? I can read the camera live through the C API and I can read the block diagram headlessly over COM.

Cite NI documentation or forum sources with URLs where you can. Be concrete and short.

## Answer

Your diagnosis lacks evidence that those strings belong to an IMAQdx node. The strongest alternative is that `Width`/`Height` act on the image display?봮r are ordinary duplicated object names?봶hile the camera dimensions and display state are being conflated.

### A. No credible IMAQdx ?쐄irst write divides by binning, second write fixes it??mechanism

The proposed mechanisms do not fit documented IMAQdx behavior:

- IMAQdx Width and Height represent the camera ROI attributes. Their units and permitted increments come from the camera?셲 GenICam implementation; IMAQdx does not document a first-call conversion between unbinned and binned coordinates. [NI ROI documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAfjSAG&l=en-US)
- With zero offsets, Width-then-Height versus Height-then-Width should not produce a stable factor-of-two transition. Ordering matters when another constraint?봢specially offsets?봳emporarily makes a requested ROI invalid, not merely because both dimensions are written. [NI discussion showing ROI ordering with offsets](https://forums.ni.com/t5/LabVIEW/Error-1074360302-When-Setting-the-OffsetX-in-IMAQdx-Property/td-p/4153736)
- `IMAQdx Configure Grab.vi` starts acquisition. NI explicitly says Width and Height generally cannot be changed while acquiring; a post-Configure write should produce an error, not silently apply half-sized values and repair them on the next run. [NI attribute-setting documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YI5lCAG&l=en-US)
- NI says changing ROI requires reconfiguring/restarting acquisition. There is no documented ?쐗rite, then re-read to commit or double the value??protocol. [NI ROI documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAfjSAG&l=en-US)

Therefore, if an actual IMAQdx property node writes `640횞512`, the most ordinary explanation is simply that its inputs are `640` and `512`?봯ossibly stale/default front-panel values. If it executes after Configure Grab, inspect the error wire: an unwired or cleared error could make the alleged write a no-op.

The exact first/second-run pattern points more strongly to LabVIEW state:

1. Width/Height controls initially contain `640/512`.
2. First run reads those values somewhere.
3. The controls or indicators are subsequently updated to `1280/1024`.
4. Second run therefore behaves differently.

That is a dataflow/local-variable/control-state hypothesis, not an IMAQdx cache hypothesis.

### B. The byte-string inference is not sound

`Width&2`, `Height&2`, followed nearby by `IMAQdx` is insufficient to identify a node or even establish semantic adjacency. Compressed VI streams contain object names, type information, library names and resources; physical string proximity is not equivalent to diagram connectivity.

In particular:

- Width and Height are common properties of front-panel controls, panes, bounds and image-display objects.
- LabVIEW appends numeric suffixes when copied objects would otherwise have duplicate names. [LabVIEW copying-object documentation](https://rajsite.github.io/unofficial-lvdocs/lvhowto/Copying_and_Pasting_Object.html)
- An IMAQ Image Display has its own runtime property nodes and view/zoom state. [NI Vision manual](https://download.ni.com/support/manuals/371007a.pdf)
- `NI_Vision_Acquisition_Software.lvlib` can appear because the VI contains an image-display/acquisition typedef; it does not prove the adjacent Width strings are IMAQdx acquisition properties.
- Conversely, absence of `IMAQdx Set Attribute.vi` does **not** exclude an IMAQdx property node: NI documents the property node as a separate way to access attributes. [NI attribute-setting documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YI5lCAG&l=en-US)

You need reporter output giving the node?셲 class, selected property paths, read/write direction, reference-terminal source, and wires. String scanning cannot establish those facts.

### C. The display is the strongest missing alternative

?쏷he image looks small??does not establish a smaller acquired frame. The Image Display control independently supports zooming and reports both image size and zoom factor. [NI Image Display documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YI6eCAG&l=en-US)

A full `1280횞1024` image displayed at `0.5횞` looks exactly like a `640횞512` image at `1횞`. Image Display zoom can be set through a property node, including fractional factors and fit-to-window behavior. [NI zoom discussion](https://forums.ni.com/t5/Machine-Vision/Zooming-images-zoom-to-fit-width-property/m-p/4338723)

A permanently half-sized IMAQ destination buffer is less likely. Acquisition functions normally size/configure their buffers from the acquisition configuration rather than treating the visual control size as the camera ROI. [NI memory-allocation explanation](https://www.ni.com/en/support/documentation/supplemental/18/ni-imaq-memory-allocation.html)

So rank the alternatives:

1. Image Display bounds/zoom or front-panel control state.
2. Stale `640/512` control values feeding a genuine IMAQdx node before acquisition.
3. A property write after Configure Grab that errors and is ignored.
4. An undocumented binning-unit/cache toggle?봪east supported.

### D. Cheapest discriminating test

Immediately after the ?쐆alf-size??first run, open `cam1` through the C API and read:

- Width
- Height
- PayloadSize

Interpretation:

- `640`, `512`, `327680`: the camera ROI really was changed.
- `1280`, `1024`, `1310720`: the camera is full-frame; the halving is downstream?봡isplay zoom/bounds, an extracted/resampled image, or mistaken Width/Height indicators.

Then use the COM reporter only to identify the suspect property node?셲 owner class and read/write direction. Do not spend time testing write order or cache behavior until that report proves it is an `IMAQdx` property node.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
