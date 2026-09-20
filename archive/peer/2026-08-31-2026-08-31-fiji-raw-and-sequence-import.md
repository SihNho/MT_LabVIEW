---
type: peer-review
status: historical
date: 2026-08-31
tags: [peer-review]
disposition: legacy
---

# 2026-08-31-fiji-raw-and-sequence-import

- **agent:** gemini
- **date:** 2026-08-31
- **outcome:** ANSWERED (188s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

Short factual question about ImageJ/Fiji, with source URLs. Do not pad the answer.

(a) File > Import > Raw... in ImageJ/Fiji: list every parameter the dialog takes (image type options, width, height, offset to first image, number of images, gap between images, white-is-zero, little-endian byte order, open all files in folder). Which image types are supported - specifically 16-bit unsigned and 16-bit SIGNED? How does ImageJ handle SIGNED 16-bit data, given that its 16-bit type is unsigned - is there a documented offset applied, and what must a user do to read signed data correctly?

(b) File > Import > Image Sequence...: does it open a numbered folder of single-image TIFFs directly as a stack WITHOUT converting or duplicating the files? What are its options (starting index, count, step, file name filter, sort numerically), and does it sort numerically or lexically - i.e. is zero-padding of filenames required?

(c) Can Fiji save an opened stack as a single multi-page TIFF, and is that save bit-exact for 16-bit data?

(d) Byte order: ImageJ's raw import default - is it big-endian unless 'little-endian' is ticked? LabVIEW's binary file write defaults to BIG-endian, so I want to confirm the pairing is correct with the checkbox left unticked.

Context so you answer the right question: I am building a regression fixture of scientific camera frames written from LabVIEW as a raw binary sequence, to be inspected in Fiji and replayed numerically. Bit-exactness matters; a silent offset or byte-swap would ruin it.

## Answer

### (a) `File > Import > Raw...`

**Source URLs:**
- [ImageJ User Guide ??Raw Import](https://imagej.nih.gov/ij/docs/guide/146-17.html#toc-Subsection-17.6)
- [`ImportDialog.java` Source](https://github.com/imagej/ImageJ/blob/master/ij/io/ImportDialog.java)
- [`ImageReader.java` Source](https://github.com/imagej/ImageJ/blob/master/ij/io/ImageReader.java#L110-L156)
- [`FileOpener.java` Source](https://github.com/imagej/ImageJ/blob/master/ij/io/FileOpener.java)

#### 1. Parameters in the Dialog
The `Import > Raw...` dialog (`ij.io.ImportDialog`) exposes the following fields:
- **Image type:** Dropdown list (see supported types below).
- **Width:** Image width in pixels (integer, default `512`).
- **Height:** Image height in pixels (integer, default `512`).
- **Offset to first image:** Header offset in bytes (integer, default `0`).
- **Number of images:** Total slices/frames to import (integer, default `1`).
- **Gap between images:** Byte padding between consecutive frame buffers (integer, default `0`).
- **White is zero:** Checkbox (inverts display LUT; default `false`).
- **Little-endian byte order:** Checkbox (default `false` $\rightarrow$ big-endian).
- **Open all files in folder:** Checkbox (imports all files matching layout; default `false`).
- **Use virtual stack:** Checkbox (streams slices on demand from disk; default `false`).

#### 2. Supported Image Types
The 14 supported image types in `ImportDialog.java` are:
- `8-bit`
- `16-bit Signed`
- `16-bit Unsigned`
- `32-bit Signed`
- `32-bit Unsigned`
- `32-bit Real`
- `64-bit Real`
- `24-bit RGB`
- `24-bit RGB Planar`
- `24-bit BGR`
- `24-bit Integer`
- `32-bit ARGB`
- `32-bit ABGR`
- `1-bit Bitmap`

#### 3. Handling of 16-bit Signed vs Unsigned Data
- **Offset applied:** ImageJ's internal 16-bit buffer (`ShortProcessor`) is strictly an unsigned 16-bit array ($0 \dots 65,535$). When **"16-bit Signed"** is chosen, `ImageReader.java` adds a fixed offset of **$+32,768$** to every pixel value (`pixels[i] = (short)(raw_val + 32768)`).
- **Display vs Raw Values:** ImageJ attaches a linear density calibration function (`y = 1.0 * x - 32768.0`) via `FileOpener.setCalibration()`. The status bar / pixel readout displays signed numbers ($-32,768 \dots +32,767$), but the underlying pixel buffer in memory is shifted by $+32,768$.
- **Required User Action:**
  - For standard scientific camera data (unsigned ADC values $0 \dots 2^{16}-1$), select **`16-bit Unsigned`**. This preserves bit-exact pixel values without offset.
  - If your raw stream truly contains signed two's-complement 16-bit integers and you extract the raw memory buffer (`short[]`) in code, you must subtract $32,768$ (or cast `(short)(val - 32768)`) to recover original values.

---

### (b) `File > Import > Image Sequence...`

**Source URLs:**
- [ImageJ User Guide ??Image Sequence](https://imagej.nih.gov/ij/docs/guide/146-17.html#toc-Subsection-17.2)
- [`FolderOpener.java` Source](https://github.com/imagej/ImageJ/blob/master/ij/plugin/FolderOpener.java)
- [`StringSorter.java` Source](https://github.com/imagej/ImageJ/blob/master/ij/util/StringSorter.java)

#### 1. In-Place Operation & File Modification
- **No conversion or file duplication occurs.** ImageJ opens the folder into a memory stack (`ImageStack`) or a disk-backed virtual stack (`VirtualStack`). The source single-image TIFF files on disk remain completely unmodified.

#### 2. Dialog Options
- **Directory:** Folder path (displayed).
- **Type / Bit Depth:** Dropdown (`default`, `16-bit`, `32-bit`, `RGB`).
- **Count:** Number of images to import.
- **Starting image:** 1-based start index.
- **Step:** Increment between images (e.g., `1` for all, `2` for every second).
- **Scale images (%):** Resize scaling factor (default `100%`).
- **File name contains:** Text/regex filter string.
- **Sort names numerically:** Checkbox (default `true`).
- **Use virtual stack:** Checkbox (default `false`).

#### 3. Sorting & Zero-Padding Requirement
- When **"Sort names numerically"** is ticked (the default), ImageJ uses `StringSorter.sortNumerically()`, which parses embedded digits within file basenames and performs natural sorting (`frame_1.tif`, `frame_2.tif`, `frame_10.tif`). **Zero-padding is not required.**
- If "Sort names numerically" is unticked, it uses standard ASCII lexicographical sorting (`frame_1.tif`, `frame_10.tif`, `frame_2.tif`), where zero-padding (e.g. `frame_0001.tif`) is required.

---

### (c) Saving Stack as Multi-Page TIFF & Bit-Exactness

**Source URLs:**
- [`FileSaver.java` Source](https://github.com/imagej/ImageJ/blob/master/ij/io/FileSaver.java)
- [`TiffEncoder.java` Source](https://github.com/imagej/ImageJ/blob/master/ij/io/TiffEncoder.java)

- **Yes.** Selecting `File > Save As > Tiff...` on an open stack saves all slices into a single multi-page TIFF file.
- **Bit-Exactness:** **Yes.** For 16-bit stacks, `TiffEncoder` dumps the raw `short[]` memory arrays directly into TIFF strips without lossy compression, downsampling, or quantization.

---

### (d) Byte Order Matching (LabVIEW $\leftrightarrow$ ImageJ)

**Source URLs:**
- [NI LabVIEW `Write to Binary File` Function Reference](https://www.ni.com/docs/en-US/bundle/labview/page/glang/write_to_binary_file.html)
- [`ImportDialog.java` Byte Order Flag](https://github.com/imagej/ImageJ/blob/master/ij/io/ImportDialog.java#L47)

- **ImageJ Default:** **Big-Endian** (Motorola byte order). The checkbox in the Raw Import dialog is `"Little-endian byte order"`, and its default state is **unticked** (`false`).
- **LabVIEW Default:** **Big-Endian** (`byte order = 0: network/big-endian`).
- **Confirmation:** Leaving **"Little-endian byte order" unticked** in Fiji/ImageJ is the **exact, matching pairing** for LabVIEW binary files written with default settings.



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
