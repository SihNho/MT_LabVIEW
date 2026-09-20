---
type: peer-review
status: historical
date: 2026-08-30
tags: [peer-review]
disposition: legacy
---

# 2026-08-30-vilib-vision-detection-failed-prediction

- **agent:** gemini
- **date:** 2026-08-30
- **outcome:** ANSWERED (109s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

Attack my diagnosis - I predicted something and the opposite happened. Tell me what I got wrong.

MY CLAIM (now contradicted): 'LabVIEW 2026 on this machine has no NI Vision installed, so a VI hierarchy that calls IMAQ/IMAQdx VIs cannot load in it.' My evidence was a filesystem check: under C:\\Program Files\\National Instruments\\LabVIEW 2026\\vi.lib there is no directory named vision, and a recursive search found no IMAQdx.llb, Image Controls.llb or Basics.llb. Under LabVIEW 2019 vi.lib all of those exist.

WHAT ACTUALLY HAPPENED: the user reports the experiment VI hierarchy opens and works fine in LabVIEW 2026.

QUESTIONS - cite NI documentation: (a) Where do NI Vision Development Module and NI Vision Acquisition Software (IMAQdx) actually install their LabVIEW support VIs in RECENT LabVIEW versions? Has NI moved them out of <LabVIEW>\\vi.lib into a shared/versionless location, an NI Package Manager managed folder, or somewhere resolved by a search path rather than a literal directory? (b) How does LabVIEW resolve the symbolic path <vilib>, and can vi.lib content be aggregated from more than one physical location - e.g. via labview.ini search paths, links, or a per-package overlay? (c) Are IMAQ/IMAQdx palette VIs in current versions delivered as .llb archives at all, or have they been unpacked into plain folders / .lvlib libraries, which would make a search for IMAQdx.llb miss them even when Vision IS installed? (d) A VI saved in an older LabVIEW references a subVI by a path inside an .llb that no longer exists in the newer install - what does LabVIEW do? Does it silently resolve to the relocated VI of the same name, and is there a documented mechanism (aliases, .lvlib mapping, vi.lib alias files) that makes that transparent? (e) What is the RELIABLE way to determine whether Vision/IMAQdx support is installed for a specific LabVIEW version - an NI Package Manager query, a registry key, an ini entry - rather than guessing from directory names?

ALREADY RULED OUT: it is not a bitness issue (both LabVIEW installs are 64-bit); the NI-IMAQdx driver IS installed system-wide at C:\\Program Files (x86)\\National Instruments\\NI-IMAQdx; PI's Mercury GCS LabVIEW driver LLBs exist under BOTH LabVIEW 2019 and 2026 instr.lib.

Be adversarial: my directory-existence test was probably invalid. Explain exactly why.

## Answer

### Why Your Diagnosis Failed

Your filesystem check assumed that LabVIEW 2026 still stores add-on and driver VIs inside the version-specific installation folder (`<LabVIEW 2026>\vi.lib`). That architectural assumption became obsolete in **LabVIEW 2022 Q3** with the introduction of the version-independent **`LVAddons`** system.

In modern LabVIEW installations (2022 Q3 through 2026+), drivers and toolkits like **NI-IMAQdx (VAS)** and the **NI Vision Development Module (VDM)** are installed once into `C:\Program Files\NI\LVAddons\` and virtually merged into `<vilib>` at runtime. Your check looked in `C:\Program Files\National Instruments\LabVIEW 2026\vi.lib` (which is empty of these drivers) while LabVIEW 2026 was seamlessly loading them from `C:\Program Files\NI\LVAddons\`.

---

### Answers to Your Questions

#### (a) Where do NI Vision / IMAQdx actually install their support VIs in recent LabVIEW versions?
Starting with LabVIEW 2022 Q3, NI moved add-on and driver LabVIEW support VIs out of the version-specific `<LabVIEW>\vi.lib` directories and into a shared, version-independent directory managed by NI Package Manager (NIPM):
- **Default Path (Windows 64-bit):** `C:\Program Files\NI\LVAddons\`
- **NI-IMAQdx location:** `C:\Program Files\NI\LVAddons\niimaqdx\1\vi.lib\vision\driver\IMAQdx.llb`
- **VDM location:** `C:\Program Files\NI\LVAddons\nivision\1\vi.lib\vision\...`

Each add-on directory contains a version folder (e.g., `1`) with a required `lvaddoninfo.json` descriptor defining the add-on name, API version, and supported LabVIEW range.

* **Documentation:** [Installing Add-ons to the Version-Independent LVAddons Directory](https://www.ni.com/docs/en-US/bundle/labview/page/installing-add-ons-to-lvaddons.html)

---

#### (b) How does LabVIEW resolve `<vilib>`, and can `vi.lib` be aggregated from multiple physical locations?
Yes. `<vilib>` is a dynamic **symbolic path** (pseudopath). 
1. At startup, LabVIEW discovers all valid add-ons in `C:\Program Files\NI\LVAddons\` by reading each package's `lvaddoninfo.json`.
2. LabVIEW creates a **virtual overlay**, aggregating the physical version directory (`C:\Program Files\National Instruments\LabVIEW 2026\vi.lib`) with every matching `vi.lib` subtree under `LVAddons`.
3. When a VI references `<vilib>:\vision\driver\IMAQdx.llb\IMAQdx Open Camera.vi`, LabVIEW resolves `<vilib>` against both the base `vi.lib` and the active `LVAddons` trees.
4. Source VIs in `LVAddons` are compiled on first load and stored in the version-specific compiled object cache (`Separation of Compiled Code`).

* **Documentation:** [Symbolic Paths in LabVIEW](https://www.ni.com/docs/en-US/bundle/labview/page/symbolic-paths.html)

---

#### (c) Are IMAQ/IMAQdx palette VIs delivered as `.llb` archives, or unpacked into folders / `.lvlib`?
- **NI-IMAQdx:** Still delivered as an LLB (`IMAQdx.llb`), but located inside `C:\Program Files\NI\LVAddons\niimaqdx\1\vi.lib\vision\driver\IMAQdx.llb`.
- **Vision Development Module (VDM):** Uses a mix. Core low-level and high-level palette items retain their legacy LLB containers (e.g., `Image Controls.llb`, `Basics.llb`, `nivision.llb`), while newer toolkits use plain directory hierarchies and `.lvlib` namespaces.
- Your search for `IMAQdx.llb` failed purely due to search scope (searching `<LabVIEW 2026>\vi.lib` instead of `C:\Program Files\NI\LVAddons\`).

---

#### (d) What does LabVIEW do when loading a VI referencing a subVI in an older/relocated path?
When loading a VI saved in an older version:
1. **Symbolic Resolution:** The subVI reference is stored using symbolic tokens (e.g., `<vilib>:\...`). Because `<vilib>` aggregates `LVAddons`, references like `<vilib>\vision\driver\IMAQdx.llb\IMAQdx Snap2.vi` match immediately without triggering a missing VI error.
2. **Fallback Search Heuristic:** If a path has changed (e.g., LLB unpacked into a folder or renamed), LabVIEW searches by VI name across:
   - Already loaded memory.
   - The caller VI's directory / project root.
   - The LabVIEW VI Search Paths (including `<vilib>` and `<instrlib>`).
3. If found under `<vilib>`, LabVIEW automatically links to the resolved VI in memory and prompts to save changes on exit (or marks the VI dirty).

* **Documentation:** [How LabVIEW Resolves SubVIs](https://www.ni.com/docs/en-US/bundle/labview/page/how-labview-resolves-subvis.html)

---

#### (e) Reliable ways to determine whether Vision / IMAQdx support is installed

##### 1. NI Package Manager CLI (`nipkg.exe`) ??*Recommended & Deterministic*
Run from PowerShell or Command Prompt (read-only, does not touch LabVIEW or hardware):
```powershell
& "C:\Program Files\National Instruments\NI Package Manager\nipkg.exe" list-installed | Select-String -Pattern "imaq|vision"
```
Look for packages such as:
- `ni-imaqdx` / `ni-imaqdx-labview-support`
- `ni-vision-development-module` / `ni-vision-development-module-labview-support`

* **Documentation:** [NI Package Manager Command-Line Interface](https://www.ni.com/docs/en-US/bundle/package-manager/page/nipkg-command-line-interface.html)

##### 2. Check the `LVAddons` directory directly
```powershell
Get-ChildItem "C:\Program Files\NI\LVAddons" -Directory
Get-ChildItem "C:\Program Files\NI\LVAddons" -Filter "IMAQdx.llb" -Recurse
```
Inspect `C:\Program Files\NI\LVAddons\niimaqdx\1\lvaddoninfo.json` to verify `MinimumSupportedLVVersion` and compatibility.

##### 3. Windows Registry Keys
Check under `HKLM\SOFTWARE\National Instruments`:
- `HKLM:\SOFTWARE\National Instruments\NI-IMAQdx`
- `HKLM:\SOFTWARE\National Instruments\Vision Development Module`
- `HKLM:\SOFTWARE\National Instruments\LabVIEW Add-ons`



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
