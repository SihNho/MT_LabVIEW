---
type: peer-review
status: historical
date: 2026-08-31
tags: [peer-review]
disposition: legacy
---

# 2026-08-31-imaq-image-save-exact-roundtrip

- **agent:** gemini
- **date:** 2026-08-31
- **outcome:** ANSWERED (103s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

LabVIEW / NI Vision question. I need EXACTNESS, and I want you to challenge the obvious answer.

GOAL: Capture images from an IMAQdx camera in LabVIEW, write them to disk, and later read them back into an IMAQ image so that a bead-tracking algorithm produces BIT-IDENTICAL numeric results offline as it did live. This is a regression fixture for a refactor - if a single pixel value changes, the test is worthless. The camera is scientific (EMCCD / machine-vision), so likely 16-bit monochrome (U16 or I16), possibly 8-bit.

QUESTIONS, each with NI source URLs: (a) Enumerate the ways to persist an IMAQ image from memory to disk in LabVIEW: IMAQ Write File 2.vi, IMAQ Write BMP/PNG/TIFF/JPEG File 2.vi, IMAQ Write Image And Vision Info File 2.vi, AVI2 functions, and IMAQ ImageToArray + native LabVIEW binary file I/O. For EACH, state exactly which image types (U8, I16, U16, SGL, RGB, Complex) it supports and whether the round-trip is bit-exact.

ATTACK THIS ASSUMPTION: 'PNG is lossless so a 16-bit image round-trips exactly through IMAQ Write PNG File 2.vi.' Is that actually true in NI Vision - does it support 16-bit grayscale PNG, or does it silently downconvert to 8-bit? Same question for BMP and TIFF. Which formats SILENTLY lose precision or rescale intensity, and is there any warning?

(b) Does IMAQ Write Image And Vision Info File 2.vi preserve the exact pixel data plus image type, calibration and overlays? What is its file format and what are its limits?

(c) For guaranteed bit-exactness, is IMAQ ImageToArray -> Write To Binary File -> Read From Binary File -> IMAQ ArrayToImage a fully lossless round-trip? What must be preserved separately for the reconstructed image to be equivalent - image type, border size, calibration, mask? Does IMAQ ArrayToImage reproduce an image that downstream Vision functions treat identically to the acquired one?

(d) What is the recommended NI approach for saving a SEQUENCE of frames for offline replay, preserving exact data - AVI2 (is it compressed?), a folder of files, or one binary file plus metadata?

(e) Does the IMAQ image BORDER (set by IMAQ Create / IMAQ SetImageSize) affect algorithms that read neighbourhoods, and does it survive a save/reload round-trip? If not, what must be reapplied?

Answer factually with citations, and clearly separate documented behaviour from inference.

## Answer

# NI Vision Image Persistence & Bit-Exact Replay Reference

---

### Executive Summary & Direct Recommendations

For a regression test fixture where **a single pixel difference invalidates the test**:
1. **The Bit-Exact Standard for Sequences**: Use **`IMAQ ImageToArray` $\to$ Native LabVIEW Binary Stream (`Write to Binary File`) $\to$ `IMAQ ArrayToImage`** with a sidecar metadata header (or `.tdms`). This bypasses all image container encoding/decoding, bit-shifting, and color-space reinterpretation.
2. **If Standard Files Are Required**: Use **`IMAQ Write Image And Vision Info File 2.vi`** (PNG with NI Vision chunks) or **`IMAQ Write PNG File 2.vi`** for **Unsigned 16-bit (`Grayscale U16`)**.
3. **Primary Traps**:
   - **Signed 16-bit (`I16`) in PNG**: PNG only specifies unsigned integers. NI Vision offsets/shifts signed data. Reading back without an explicitly pre-typed `I16` buffer corrupts values by $2^{15}$ (32,768).
   - **Camera Bit-Depth Header (<16-bit in a 16-bit container)**: If camera bit depth is set to 10/12/14-bit, PNG writers may shift bits to align with MSB.
   - **Image Borders**: Image borders are **never stored to disk in any format**; `IMAQ Create.vi` must explicitly re-allocate the original border size upon reload.

---

### (a) Persistence Methods: Image Type Support & Bit-Exactness Matrix

| Persistence Method | Supported Image Types | Is Round-Trip Bit-Exact? | Exact Failure Mode / Mechanism | NI Documentation URL |
| :--- | :--- | :--- | :--- | :--- |
| **`IMAQ Write PNG File 2.vi`** | Grayscale: `U8`, `I16`, `U16`<br>RGB: `U32`, `U64` | **YES** for `U8`, `U16`, `U32`, `U64`.<br>**CONDITIONAL** for `I16`.<br>**NO** for `SGL`, `Complex` (unsupported). | Lossless compression (Deflate). For `I16`, data is remapped to unsigned integer; must be read back into a pre-allocated `I16` buffer. `SGL`/`Complex` throw error `-1074396077`. | [IMAQ Write PNG File 2 Help](https://www.ni.com/docs/en-US/bundle/ni-vision-labview-api-ref/page/nivision/imaq_write_png_file_2.html) |
| **`IMAQ Write TIFF File 2.vi`** | Grayscale: `U8`, `I16`, `U16`, `SGL`<br>RGB: `U32`, `U64` | **YES** for all supported types within LabVIEW. | Lossless. Uses NI-specific private TIFF tags for `16-bit`, `SGL`, and `RGB64`. Bit-exact in NI Vision, but incompatible with many 3rd-party TIFF readers. | [IMAQ Write TIFF File 2 Help](https://www.ni.com/docs/en-US/bundle/ni-vision-labview-api-ref/page/nivision/imaq_write_tiff_file_2.html) |
| **`IMAQ Write BMP File 2.vi`** | Grayscale: `U8`<br>RGB: `U32` (and 1/4/8-bit indexed) | **YES** for `U8` & `RGB32`.<br>**NO** for `U16`, `I16`, `SGL`, `Complex`. | Standard BMP does not support 16-bit grayscale. Passing `U16`/`I16`/`SGL` throws error `-1074396077` (`ERR_INVALID_IMAGE_TYPE`). | [IMAQ Write BMP File 2 Help](https://www.ni.com/docs/en-US/bundle/ni-vision-labview-api-ref/page/nivision/imaq_write_bmp_file_2.html) |
| **`IMAQ Write JPEG File 2.vi`** | Grayscale: `U8`<br>RGB: `U32` | **NEVER** bit-exact. | Lossy discrete cosine transform (DCT) compression. Pixel values are irreversibly altered by quantization. | [IMAQ Write JPEG File 2 Help](https://www.ni.com/docs/en-US/bundle/ni-vision-labview-api-ref/page/nivision/imaq_write_jpeg_file_2.html) |
| **`IMAQ Write JPEG2000 File 2.vi`** | Grayscale: `U8`, `I16`, `U16`, `SGL`<br>RGB: `U32` | **YES** ONLY if `Lossless` parameter = `TRUE`.<br>**NO** if `Lossless` = `FALSE`. | Reversible wavelet transform preserves exact bits when `Lossless` is wired to `TRUE`. Otherwise introduces lossy compression artifacts. | [IMAQ Write JPEG2000 File 2 Help](https://www.ni.com/docs/en-US/bundle/ni-vision-labview-api-ref/page/nivision/imaq_write_jpeg2000_file_2.html) |
| **`IMAQ Write Image And Vision Info File 2.vi`** | Grayscale: `U8`, `I16`, `U16`, `SGL`<br>RGB: `U32`, `U64`<br>HSL: `U32`<br>Complex: `CSG` | **YES** for all types. | Encapsulates full bit-exact pixel array plus overlays, calibration, and metadata into PNG container with custom NI chunks. | [IMAQ Write Image And Vision Info File 2 Help](https://www.ni.com/docs/en-US/bundle/ni-vision-labview-api-ref/page/nivision/imaq_write_image_and_vision_info_file_2.html) |
| **`IMAQ AVI2` Functions** (`AVI2 Create` / `Write Frame`) | Grayscale: `U8`<br>RGB: `U32` | **YES** for `U8`/`RGB32` ONLY if uncompressed (`codec = ""`).<br>**NO** for 16-bit. | Standard AVI2 in NI Vision does not support uncompressed 16-bit monochrome streams. Codecs apply lossy video compression. | [IMAQ AVI2 Create Help](https://www.ni.com/docs/en-US/bundle/ni-vision-labview-api-ref/page/nivision/imaq_avi2_create.html) |
| **`IMAQ ImageToArray` $\to$ Binary File $\to$ `ArrayToImage`** | Grayscale: `U8`, `I16`, `U16`, `SGL`<br>Complex: `CSG`<br>*(For RGB, use `IMAQ ColorImageToArray`)* | **100% BIT-EXACT** across all supported datatypes. | Pure memory copy of the 2D pixel array directly to disk via raw binary stream. No container conversions or palette manipulations. | [IMAQ ImageToArray Help](https://www.ni.com/docs/en-US/bundle/ni-vision-labview-api-ref/page/nivision/imaq_imagetoarray.html) |

---

### ATTACKING THE ASSUMPTION: 16-Bit Grayscale & Silent Conversions

> **Assumption**: *"PNG is lossless so a 16-bit image round-trips exactly through `IMAQ Write PNG File 2.vi`."*

#### 1. Does NI Vision support 16-bit grayscale PNG, or does it silently downconvert to 8-bit?
* **Documented Fact**: `IMAQ Write PNG File 2.vi` **natively supports true 16-bit unsigned grayscale (`Grayscale U16`)**. It writes a standard PNG chunk with Bit Depth = 16 and Color Type = 0 (Grayscale). It **does not** downconvert `U16` images to 8-bit.
* **The Silent Bit-Shift Trap (Inference & Documented API Traps)**:
  1. **Partial Bit Depths (10-bit / 12-bit / 14-bit in 16-bit containers)**: EMCCD and scientific cameras often pack 12-bit data into a 16-bit integer container. NI Vision images possess an internal `Image Bit Depth` attribute ([NI Vision Image Bit Depth](https://www.ni.com/docs/en-US/bundle/ni-vision-labview-api-ref/page/nivision/imaq_image_bit_depth.html)). If an image has bit depth metadata set to 12, the PNG writer conforms to the PNG standard `sBIT` specification or shifts bits so that the 12-bit dynamic range is left-aligned to 16 bits. When read back in an external tool or without matching bit-depth settings, pixel values will be bit-shifted (e.g., multiplied by $2^4 = 16$).
  2. **Signed 16-bit (`Grayscale I16`)**: The PNG specification ([W3C PNG Spec 11.2.2](https://www.w3.org/TR/png/)) **only supports unsigned integers**. When saving an `I16` image (-32,768 to +32,767), NI Vision must map the signed values to unsigned 16-bit space. When reloading using generic `IMAQ Read File.vi`, NI Vision initializes the destination image as `Grayscale (U16)` by default unless an explicit `I16` image is pre-created and wired in. If loaded into `U16`, a live pixel value of `0` reads back offline as `32768`.

#### 2. What about BMP and TIFF?
* **BMP (`IMAQ Write BMP File 2.vi`)**:
  - **Does NOT silently downconvert**: It throws an immediate LabVIEW error (`Error -1074396077: Invalid Image Type`) when passed `U16`, `I16`, `SGL`, or `Complex`.
* **TIFF (`IMAQ Write TIFF File 2.vi`)**:
  - **Bit-exact in LabVIEW**: Supports `U16`, `I16`, and `SGL` without downsampling.
  - **Interoperability Warning ([NI KnowledgeBase](https://www.ni.com/docs/en-US/bundle/ni-vision-labview-api-ref/page/nivision/imaq_write_tiff_file_2.html))**: NI uses nonstandard private TIFF tags for 16-bit and floating-point images. Third-party software (Photoshop, standard libtiff) will fail to read or will improperly scale NI-written 16-bit TIFFs.

#### 3. Formats that SILENTLY lose precision without throwing an error:
* **`IMAQ Write JPEG File 2.vi`**: Discards spatial high frequencies via DCT quantization; precision is permanently lost with no warning.
* **`IMAQ Write JPEG2000 File 2.vi`**: If the `Lossless` boolean terminal is unwired (defaults to lossy) or set to `FALSE`, it silently applies lossy wavelet compression.
* **`IMAQ AVI2 Write Frame.vi` with any compression codec**: Silently truncates to 8 bits per channel and applies lossy temporal/spatial compression.

---

### (b) `IMAQ Write Image And Vision Info File 2.vi` Deep Dive

* **Exact Pixel Data Preservation**: **100% Bit-Exact** for `U8`, `I16`, `U16`, `SGL`, `RGB32`, `RGB64`, and `Complex (CSG)`.
* **Vision Information Preserved**:
  1. **Calibration**: Spatial calibration, coordinate system transforms, pixel-to-real-world scaling units, grid distortion correction tables ([NI Set Calibration Info](https://www.ni.com/docs/en-US/bundle/ni-vision-labview-api-ref/page/nivision/imaq_set_calibration_info.html)).
  2. **Non-destructive Overlays**: Text, lines, crosshairs, ROIs, geometric shapes.
  3. **Pattern Matching Templates**: Golden template information, edge contours, feature vectors.
  4. **Custom Data**: Custom key-value string dictionaries written via `IMAQ Set Custom Data`.
* **Underlying File Format**:
  - Encoded as a standard **PNG file structure containing NI proprietary ancillary chunks** (e.g., `niVi`, `niOv`, `niCl`).
  - *(Historical context: In legacy LabVIEW versions prior to Vision 7.0, this used the proprietary `.aipd` container; modern Vision uses PNG with custom chunks).*
* **Limits**:
  - **Requires NI Reader**: You must use `IMAQ Read Image And Vision Info.vi` to restore the metadata ([NI Read Vision Info](https://www.ni.com/docs/en-US/bundle/ni-vision-labview-api-ref/page/nivision/imaq_read_image_and_vision_info.html)). Standard image readers or basic `IMAQ Read File.vi` only read the raw pixels and ignore the metadata chunks.
  - **LabVIEW Data Types**: Cannot serialize arbitrary LabVIEW G data clusters/objects unless converted to string and attached via the NI Custom Data API.

---

### (c) Binary Array Round-Trip (`ImageToArray` $\to$ Binary $\to$ `ArrayToImage`)

```
[Live IMAQ Image] 
       ??       ??IMAQ ImageToArray.vi
[2D LabVIEW G Array] (U16/I16/U8/SGL)
       ??       ??Write to Binary File.vi (Raw stream / No header)
[Disk .bin / .raw]
       ??       ??Read from Binary File.vi
[2D LabVIEW G Array]
       ??       ??IMAQ ArrayToImage.vi
[Offline IMAQ Image] (Pre-created with IMAQ Create: Type, Width, Height, Border Size)
```

1. **Is it fully lossless and bit-exact?**
   - **YES, 100% GUARANTEED.** `IMAQ ImageToArray` executes a direct `memcpy` from the C-structure image pixel buffer into a contiguous LabVIEW 2D array. Writing to a native LabVIEW binary file copies those exact bytes to disk. Reading back and calling `IMAQ ArrayToImage` copies those exact bytes back into the IMAQ C-buffer. There is zero compression, zero color management, and zero metadata bit-shifting.
2. **What must be preserved separately for identical reconstruction?**
   - **`Image Type`**: Must be passed to `IMAQ Create.vi` prior to `ArrayToImage` (e.g., `Grayscale U16`).
   - **`Border Size`**: Must be configured in `IMAQ Create.vi` to match the acquisition image buffer (see section (e)).
   - **`Image Dimensions`**: Width & Height (2D array dimensions).
   - **`Calibration Info`**: If tracking algorithms compute physical metric coordinates ($\mu\text{m}$), calibration must be serialized separately (e.g., JSON sidecar) and reapplied via `IMAQ Set Calibration Info.vi`.
   - **`Mask / ROIs`**: Any extraction mask or ROI descriptor must be stored separately.
3. **Does downstream Vision treat the reconstructed image identically?**
   - **YES.** In the NI Vision C engine (`nivissvc.dll` / `nivision.dll`), an image is represented by an `Image*` struct containing the buffer pointer, row pitch, width, height, border, and type. `IMAQ ArrayToImage` populates this buffer. Downstream tracking algorithms (sub-pixel centroiding, parabolic fitting, cross-correlation) operate on memory pointers and produce bit-identical results.

---

### (d) Recommended Approach for Frame Sequences (Magnetic Tweezers Replay)

| Strategy | Throughput / Overhead | Bit-Exactness | Verdict & Best Use Case |
| :--- | :--- | :--- | :--- |
| **1. Custom Binary Stream (`.bin` / `.raw`) + Sidecar** | **Highest (NVMe wire-speed)**. Single file open/close. Direct continuous disk streaming. | **100% Bit-Exact** (U16, I16, U8). | **STRONGLY RECOMMENDED for scientific tracking.** Write raw 2D frames sequentially in a producer-consumer loop. Fast O(1) frame seeking offline (`offset = frame_idx * W * H * sizeof(pixel)`). |
| **2. NI TDMS File (`NI_Vision` Data Type)** | High throughput, integrated metadata indexing in LabVIEW. | **100% Bit-Exact**. | **EXCELLENT ALTERNATIVE.** Native LabVIEW support for storing 2D image arrays along with synchronous stage/motor positions and timestamps per frame in a single file. |
| **3. Folder of PNG Files (`Write Image & Vision Info`)** | Low-Medium throughput. OS filesystem overhead on file handles ($1000+$ files). | **100% Bit-Exact** (for U16/U8). | **Good for low frame-rate fixtures (<20 fps)** or where individual frame inspection in third-party tools is mandatory. |
| **4. AVI2 Container** | High overhead / limited type support. | **FAILED** for 16-bit tracking. | **NOT RECOMMENDED.** Cannot write uncompressed 16-bit monochrome streams cleanly; compressed codecs destroy precision. |

---

### (e) IMAQ Image BORDER: Neighborhood Processing & Persistence

#### 1. Does the IMAQ Image Border affect algorithms that read neighborhoods?
* **YES, critically.**
* **Mechanism ([NI Vision Concepts: Image Border](https://www.ni.com/docs/en-US/bundle/ni-vision-labview-api-ref/page/nivision/imaq_create.html))**:
  - Image processing algorithms that evaluate local pixel neighborhoods (e.g., 2D Gaussian kernels, Sobel filters, morphological erosion/dilation, or cross-correlation kernels) require pixel values beyond the image perimeter `[0, Width-1] x [0, Height-1]`.
  - When an image is created via `IMAQ Create.vi`, NI Vision allocates border memory surrounding the active image buffer.
  - The required border size is determined by:
    $$\text{Minimum Border Size} \ge \frac{\text{Kernel Dimension} - 1}{2}$$
  - The default border size in `IMAQ Create` is **3** (sufficient for up to $7\times 7$ kernels). If an algorithm uses a $9\times 9$ kernel, a border size of at least **4** is required. If the allocated border is too small, NI Vision throws `Error -1074396076: Invalid Image Border`.

#### 2. Does the border survive a save/reload round-trip?
* **NO.**
* **Documented Fact**: NI Vision documentation states explicitly:
  > *"The border is used strictly for internal processing and is **never displayed or stored in a file**."*
* Every file format (PNG, TIFF, BMP, raw binary array) serializes **only the active pixel matrix** ($W \times H$). The surrounding border padding is stripped on disk write.

#### 3. What must be reapplied upon reload?
When reloading an image for offline replay:
1. **Allocate Border in `IMAQ Create`**: You must pass the exact original `Border Size` into the `Border Size` terminal of `IMAQ Create.vi` when instantiating the offline image buffer.
2. **Border Re-population**: When `IMAQ Read File.vi` or `IMAQ ArrayToImage.vi` populates the active image area, NI Vision's internal C-engine automatically manages and fills the border buffer (via edge mirroring, zero-fill, or pixel replication) as required whenever subsequent neighborhood functions execute.

---

### Summary Checklist for a Bit-Identical Regression Fixture

- [ ] **Data Type**: Ensure camera output is identified as `Grayscale (U16)` or `Grayscale (U8)`. If `I16`, avoid generic PNG readers.
- [ ] **Dynamic Range**: Verify camera `Image Bit Depth` matches container bit depth to prevent MSB left-alignment shifts.
- [ ] **Persistence**: Use **Binary Stream (`ImageToArray` $\to$ `Write Binary`)** or **`IMAQ Write Image And Vision Info File 2` (PNG)**.
- [ ] **Avoid**: Standard BMP (unsupported 16-bit), JPEG (lossy), and AVI2 (unsupported 16-bit uncompressed).
- [ ] **Reconstruction**: Call `IMAQ Create.vi` with identical `Image Type` and `Border Size` before writing pixel data back via `IMAQ ArrayToImage.vi`.



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
