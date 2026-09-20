# Files and formats (LabVIEW Automation skill)

Reading .vi offline, LVAddons/<vilib> overlay, saved-version audit, IMAQ image persistence.


## Reading a `.vi` without opening LabVIEW

Most content is zlib-compressed inside the binary. Inflating those streams recovers control labels,
comments, and **ring/enum item lists** — but never wiring. Useful for fast offline diffing between two
saved versions, and for enumerating what a ring constant can contain. Compiled machine code in the
same streams produces convincing ASCII noise, so treat any single string as a hint, not proof.


## Driver/toolkit VIs are NOT under `<LabVIEW>\vi.lib` any more — `LVAddons` and the `<vilib>` overlay

Since **LabVIEW 2022 Q3**, NI installs drivers and toolkits (Vision/IMAQdx, DAQmx, VISA, …) into a
**version-independent** tree rather than into each LabVIEW installation:

```
C:\Program Files\NI\LVAddons\<package>\<n>\vi.lib\...
C:\Program Files\NI\LVAddons\niimaqdx\1\vi.lib\vision\driver\IMAQdx.llb
```

`<vilib>` is a **virtual overlay**, not a directory. At startup LabVIEW reads each add-on's
`lvaddoninfo.json` and aggregates its `vi.lib` subtree with the LabVIEW installation's own, so
`<vilib>:\vision\driver\IMAQdx.llb\IMAQdx Open Camera.vi` resolves even when nothing of the sort
exists beneath `LabVIEW 2026\`.

**Consequence: "the directory isn't there, so the driver isn't installed" is an invalid test** — and
it produced a confidently wrong diagnosis on 2026-08-30 (that an experiment hierarchy could not load
in 2026 for want of Vision; it loaded and ran fine). Test it deterministically instead:

```powershell
& "C:\Program Files\National Instruments\NI Package Manager\nipkg.exe" list-installed | Select-String "imaq|vision"
```

or list `C:\Program Files\NI\LVAddons` and read the package's `lvaddoninfo.json` for its supported
LabVIEW range.

### Relinking marks VIs dirty — this is how a hierarchy gets silently upgraded

When a stored subVI path no longer matches (an LLB relocated, unpacked, or renamed — exactly what
`LVAddons` does to older references), LabVIEW searches by VI name across memory, the caller's
directory and the search paths. On finding it, **LabVIEW relinks in memory and marks the caller
dirty, so it prompts to save on exit.**

So *opening* an old hierarchy in a newer LabVIEW can leave every VI in it dirty, and one "Save"
answered on the way out rewrites the whole hierarchy in the newer format — which older LabVIEW can
then never open. No one has to decide to save for this to happen. **When opening any hierarchy that
must keep working in an older LabVIEW, expect the save prompt and answer No**, and audit the saved
versions afterwards (`19 00 80 00` vs `26 00 80 00`, see above).


## Persisting IMAQ images so an algorithm gives bit-identical results offline

Building an offline regression fixture from camera images: a single changed pixel invalidates a
numeric comparison, so the format choice is not cosmetic.

**Use `IMAQ ImageToArray` → `Write to Binary File` → `Read from Binary File` → `IMAQ ArrayToImage`.**
`ImageToArray` is a memcpy of the pixel buffer, so the round trip is bit-exact for every grayscale
type (U8, I16, U16, SGL, CSG) with no codec, palette or colour management in the path. For a
sequence, write frames back-to-back in one file and seek with
`offset = frame × W × H × bytes_per_pixel`. **TDMS** is an equally exact alternative and lets
per-frame metadata (stage position, timestamp) live in the same file.
`IMAQ Write Image And Vision Info File 2.vi` is also bit-exact for all types and additionally keeps
calibration and overlays (PNG container with NI-private chunks; needs
`IMAQ Read Image And Vision Info.vi` to restore the metadata).

**Format traps, verified against NI's docs (2026-08-31 peer research, archived):**

| format | 16-bit | trap |
|---|---|---|
| PNG | U8/U16 fine | **I16 is remapped to unsigned.** Read back into a default U16 image and every pixel is off by 32768 — silently. Pre-create an I16 image. |
| TIFF | U8/I16/U16/SGL fine | NI-private tags; third-party readers mis-scale or fail. |
| BMP | U8 only | **Errors** (`-1074396077`), does not silently downconvert. |
| JPEG | U8 only | Always lossy, no warning. |
| JPEG2000 | all | Lossy unless `Lossless` is explicitly TRUE — the default is not safe. |
| AVI2 | U8/RGB32 only | Cannot stream uncompressed 16-bit mono; codecs truncate to 8 bits. |

**The one that bites even when the bits are perfect: the image BORDER is never written to any
file.** Neighbourhood operators (Gaussian, Sobel, morphology, correlation) read outside the active
`W × H` region, and that padding exists only in memory. When reconstructing, pass the **same
`Border Size` to `IMAQ Create`** as the acquisition buffer used — the default is 3, enough for a 7×7
kernel; too small raises `-1074396076` or changes behaviour. Also re-apply calibration and masks
separately if the algorithm works in physical units.

**A fixture is not just images.** Capture every other input the algorithm consumes in the same
frame, or the comparison has nothing to hold constant.

