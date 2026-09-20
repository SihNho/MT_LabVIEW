---
type: peer-review
status: historical
date: 2026-08-30
tags: [peer-review]
disposition: legacy
---

# 2026-08-30-save-for-previous-version-range

- **agent:** gemini
- **date:** 2026-08-30
- **outcome:** ANSWERED (133s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

Factual LabVIEW question - I need accurate, cited answers, and I need you to challenge my assumptions.

SITUATION: A lab has LabVIEW 2019 (runs the real experiments) and LabVIEW 2026 (used for VI-scripting/harness work) on one Windows machine. 34 VIs of an experiment hierarchy - including the top-level VI and about 30 subVIs - have been re-saved by LabVIEW 2026 and now cannot be opened in LabVIEW 2019. Verified offline: the VI files' version dword changed from 19 00 80 00 to 26 00 80 00.

QUESTIONS, each with an NI source URL: (a) 'File > Save for Previous Version...' in a recent LabVIEW: HOW FAR BACK can it save? Is there a fixed limit (e.g. only N previous versions, or only back to a specific release), and specifically can LabVIEW 2025/2026 save directly to LabVIEW 2019 format, or must it be stepped down through intermediate versions on other installations? (b) Does 'Save for Previous Version' operate on the ENTIRE VI HIERARCHY (all subVIs) or only the single VI? What is the correct procedure to downgrade a whole hierarchy including subVIs in a shared directory? (c) What is LOST or changed when saving to a previous version - features unavailable in the target version, compiled code, VI properties, malleable VIs, maps/sets, etc.? Is any silent behavioural change possible? (d) If the hierarchy references vi.lib VIs, does Save for Previous Version relink them to the OLD version's vi.lib, or will the downgraded VIs still point at 2026 vi.lib paths and fail in 2019? (e) SEPARATE OBSERVATION TO EXPLAIN: the user reports that files saved as .llb (LabVIEW VI Library) in LabVIEW 2019 appear to be read as .dll by LabVIEW 2026. Is there a known behaviour, bug, or path-resolution issue where LabVIEW treats an .llb as a shared library, or where an error message about a .dll appears when an .llb dependency cannot be resolved? What actually causes that?

Do not speculate without saying so. Mark clearly which answers are documented and which are inference.

## Answer

Here are the factual, cited answers to each question.

---

### (a) "Save for Previous Version" Range and 2026 $\rightarrow$ 2019 Feasibility

#### Direct Answer
* **Can LabVIEW 2025/2026 save directly to LabVIEW 2019?** **YES.** LabVIEW 2025 and 2026 can save directly to LabVIEW 2019 in a single step. You do **not** need to step down through intermediate versions.
* **How far back can it save?** In LabVIEW 2024/2025/2026, the **LabVIEW Version** drop-down menu in the *Save for Previous Version* dialog natively lists target versions going back to **LabVIEW 2017** (and in standard releases, back to **LabVIEW 8.0**). Starting in LabVIEW 2024 Q3, LabVIEW also provides an explicit project-level "Editor Save Version" supporting formats back to **2019**.

#### Reasoning & Documentation
* In the LabVIEW development environment, `File > Save for Previous Version...` opens a dialog containing a dropdown menu of major LabVIEW versions.
* NI's file-format serialization engine translates the in-memory object hierarchy into the binary tag structure of the chosen target version. Stepped conversion is only necessary when converting code to versions older than the minimum entry in the dropdown (e.g. pre-8.0).
* **Sources**:
  * NI Documentation: [Saving for a Previous Version](https://www.ni.com/docs/en-US/bundle/labview/page/saving-for-a-previous-version.html)
  * NI Documentation: [Save for Previous Version Dialog Box](https://www.ni.com/docs/en-US/bundle/labview/page/save-for-previous-version-dialog-box.html)
  * NI KnowledgeBase: [How to Save LabVIEW Files for a Previous Version](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P6hMSAS)

---

### (b) Hierarchy vs. Single VI Scope & Recommended Procedure

#### Direct Answer
* **Scope**: `File > Save for Previous Version` **operates on the entire VI hierarchy** (the open top-level VI, all referenced static subVIs, custom type definitions, and controls). It does **not** save only the single top-level VI.
* When saving, LabVIEW requires you to choose a **new destination directory** to avoid overwriting current files and replicates the relative directory structure of the hierarchy inside that destination directory.

#### Correct Procedure for a Hierarchy
1. **Ensure Clean Load**: Open the top-level VI (or `.lvproj` Project file) in LabVIEW 2026. Ensure all subVIs load without unresolved search prompts.
2. **Execute Save**:
   * If using a Project: In the *Project Explorer* window, select `File > Save for Previous Version...`
   * If using a standalone VI: With the top-level VI active, select `File > Save for Previous Version...`
3. **Configure Dialog**:
   * Select **LabVIEW 2019** in the version dropdown.
   * Choose an empty target folder (e.g. `C:\downgraded_2019\`).
   * Click **Save**.
4. **Review Warnings**: If any nodes are incompatible, the **Save for Previous Warning List** dialog will pop up listing affected objects.
5. **Preserve SubVI Relative Paths**: LabVIEW writes all caller and subVI files into the target folder, maintaining their relative directory hierarchy so that cross-directory linking remains intact when opened in LabVIEW 2019.

#### Sources
* NI Documentation: [Save for Previous Version Dialog Box](https://www.ni.com/docs/en-US/bundle/labview/page/save-for-previous-version-dialog-box.html)
* NI KnowledgeBase: [Saving a LabVIEW Project for a Previous Version](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P83fSAC)

---

### (c) What is Lost/Changed and Potential Silent Behavioral Changes

#### Direct Answer
* **Compiled Code**: Compiled machine code is stripped from the saved VIs. LabVIEW 2019 will recompile the hierarchy automatically upon load.
* **Unsupported Features**: Any feature or function introduced in LabVIEW 2020 through 2026 cannot be converted. LabVIEW replaces unsupported block diagram nodes with an **unsupported/broken node placeholder (question mark icon)** and breaks the run arrow.
* **Feature Breakdown for LabVIEW 2019 Target**:
  * *Malleable VIs (`.vim`)*: Introduced in LabVIEW 2017 $\rightarrow$ **Supported in 2019**.
  * *Maps and Sets*: Introduced in LabVIEW 2019 $\rightarrow$ **Supported in 2019** (except nodes/methods added in 2020+).
  * *LabVIEW OOP Interfaces*: Introduced in LabVIEW 2020 $\rightarrow$ **NOT supported in 2019** (classes using interfaces will lose interface inheritance).
  * *Execution / Structure features*: Features added after 2019 (e.g. new JSON / string functions or palette additions) become broken nodes.

#### Silent Behavioral Changes vs. Explicit Breaks
* **Documented Rule**: NI's downgrade engine does not silently change algorithm math or logic?봧t breaks the VI if a node/feature is missing.
* **Potential Risks / Edge Cases (Inference & Documented Caveats)**:
  1. *Dynamic VI Server Property/Invoke Nodes*: If a property/method string introduced after 2019 is invoked dynamically, it may fail at runtime rather than at compile time.
  2. *vi.lib Implementation Differences*: The downgraded code will execute against LabVIEW 2019's `vi.lib` implementation, which may contain older bug fixes/behaviors than 2026's `vi.lib`.
  3. *Polymorphic VI Resolution*: If custom polymorphic VIs had instances added in 2026 that use newer data types, the selector might fall back to an unexpected instance if types were altered.

#### Sources
* NI Documentation: [LabVIEW Features and Changes by Version](https://www.ni.com/docs/en-US/bundle/labview/page/labview-features.html)
* NI Documentation: [Save for Previous Warning List Dialog Box](https://www.ni.com/docs/en-US/bundle/labview/page/save-for-previous-warning-list-dialog-box.html)
* NI KnowledgeBase: [Incompatibilities When Saving for Previous Version](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000x2bECAQ)

---

### (d) `vi.lib` Relinking Behavior

#### Direct Answer
* Downgraded VIs **will automatically link to LabVIEW 2019's `vi.lib`** and will **NOT** point to or pull from LabVIEW 2026's `vi.lib`.

#### Reasoning & Documentation
* LabVIEW does not store hardcoded absolute filesystem paths for standard library components. It stores **symbolic paths** (e.g., `<vilib>`, `<instrlib>`, `<userlib>`).
* During *Save for Previous Version*, LabVIEW explicitly excludes files located in `vi.lib` from being copied to the destination folder.
* When the downgraded VIs are opened in LabVIEW 2019, LabVIEW resolves `<vilib>` relative to the LabVIEW 2019 installation directory (`C:\Program Files (x86)\National Instruments\LabVIEW 2019\vi.lib` or 64-bit equivalent).
* **Caveat**: If a VI in the hierarchy referenced a `vi.lib` VI that was first introduced in LabVIEW 2020??026, LabVIEW 2019 will prompt that the VI is missing because it does not exist in the 2019 `vi.lib` directory.

#### Sources
* NI Documentation: [Symbolic Paths in LabVIEW](https://www.ni.com/docs/en-US/bundle/labview/page/symbolic-paths.html)
* NI KnowledgeBase: [Why Are vi.lib VIs Not Copied During Save for Previous?](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019YcASAU)

---

### (e) Why .llb Files Appear to be Read as .dll in LabVIEW 2026

#### Root Cause Analysis *(Distinguishing Documented Facts vs. Inferred Causes)*

1. **Documented Fact**: A `.llb` (LabVIEW VI Library archive) and a `.dll` (Windows Dynamic Link Library binary) are fundamentally different file types. LabVIEW's core loader never aliases `.llb` as a `.dll`.
2. **Most Probable Cause ??Call Library Function Node (CLFN) & Bitness/Search Path Failure** *(Inferred based on standard LabVIEW architecture & documented CLFN behavior)*:
   * VIs inside hardware-interfacing LLBs (cameras, piezo controllers, motion stages) typically call C-DLLs via **Call Library Function Nodes (CLFN)**.
   * If LabVIEW 2019 is **32-bit** and LabVIEW 2026 is **64-bit** (a very common configuration):
     * LabVIEW 2026 attempts to load the external DLL referenced by the VI inside the LLB.
     * Loading a 32-bit DLL in a 64-bit LabVIEW environment fails with an OS/LabVIEW dialog: *"The file specified is not a valid Dynamic Link Library"* or *"Library not found or failed to load"*.
     * When opening the `.llb`, the user sees an error modal specifically naming a `.dll`, giving the impression that the LLB itself is being processed as a DLL.
3. **Secondary Cause ??Path Resolution Inside LLB Containers** *(Documented LabVIEW path behavior)*:
   * In LabVIEW, paths inside an LLB are structured as `C:\path\library.llb\my_subvi.vi`.
   * If a subVI inside the LLB programmatically builds a path to a companion `.dll` using `Current VI's Path -> Strip Path -> Append 'driver.dll'`, `Strip Path` returns `C:\path\library.llb` (treating the LLB as a folder).
   * When this path is passed to Windows `LoadLibrary`, Windows fails because it cannot traverse inside a `.llb` archive to find the `.dll`.
4. **Packed Project Library (`.lvlibp`) Terminology Confusion** *(Documented)*:
   * A Packed Project Library (`.lvlibp`) is compiled into a single file with DLL-like characteristics. If an error log mentions missing packed libraries or shared library linkage, this can be confused with legacy `.llb` files.

#### How the Manager Can Cheaply Verify This
* Check the bitness of both installations:
  * LabVIEW 2019: Check if installed in `C:\Program Files (x86)\...` (32-bit).
  * LabVIEW 2026: Check if installed in `C:\Program Files\...` (64-bit).
* Check the reporter text / block diagrams of VIs inside the `.llb` for any `Call Library Function Node` referencing external `.dll` files.

#### Sources
* NI KnowledgeBase: [LabVIEW 32-bit vs 64-bit and DLL Loading Compatibility](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019LSPSA2)
* NI Documentation: [Configuring the Call Library Function Node](https://www.ni.com/docs/en-US/bundle/labview/page/call-library-function.html)
* NI Discussion Forums: [Current VI's Path inside LLB returns path with LLB name](https://forums.ni.com/t5/LabVIEW/Current-VI-s-Path-inside-LLB-returns-path-with-LLB-name/td-p/1182740)



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
