---
type: narrative
status: historical
date: 2026-08-26
tags: [archive]
---

# How this wiki was built (and how to update it)

> **Status 2026-08-26:** this byte-level technique is now the **fallback**, not the primary method.
> LabVIEW 2026 is installed and **VI Scripting is proven working**, so open/script the VI for ground
> truth whenever wiring or logic matters - this technique can never recover wiring. It remains the
> best option for fast offline diffing and for reading ring/enum item lists. The packaged version
> lives in the `labview-vi-analysis` skill; `tools/*.py` here are byte-identical mirrors of
> `.claude/skills/labview-vi-analysis/scripts/*.py` - change both or they drift.

## Why this approach was needed

A `.vi` file is LabVIEW's compiled binary format (`RSRC` container), and no official text export was
used — everything in this wiki was reconstructed by reading the raw bytes of the `.vi` files with
Python. This technique was originally written assuming no LabVIEW installation existed on this
machine; that assumption was **wrong** and corrected 2026-08-24 — LabVIEW 2026 is actually installed
(`C:\Program Files\National Instruments\LabVIEW 2026\LabVIEW.exe`), along with LabVIEW CLI. A live
GUI-automation session (screenshot + simulated mouse/keyboard, driving the real editor) was used
successfully that day to inspect the actual block diagram — see VERSION_HISTORY.md's "V6
investigation" entry for what that found and the technique (PrintWindow capture, the Alt-key
foreground-lock workaround, right-click-down-then-drag-release for context menus). The byte-level
technique below is still useful for quick diffing between saved `.vi` files without opening LabVIEW at
all, and remains the fallback if a future session has no GUI access.

## The technique

1. **Raw string extraction** (`tools/extract_strings.py`) — pulls printable ASCII runs directly
   from the file. This alone only recovers dependency paths (sub-VI names, `.ctl`/`.lvlib`
   references) because front-panel/block-diagram content is zlib-compressed inside the file.
2. **Decompression** (`tools/decompress_vi.py`) — scans the whole file for zlib stream headers
   (`0x78 0x01/0x5E/0x9C/0xDA`), inflates every candidate, and extracts printable strings from the
   decompressed output. This recovers front-panel control labels, string constants, comments, and
   event-structure case names. It does **not** recover the actual wiring/diagram logic — LabVIEW
   also embeds compiled x86-64 machine code in these streams for fast loading, which shows up as
   printable-looking noise (register mnemonics, junk ASCII runs) mixed in with the real text. There
   is no way to distinguish "real UI text" from "code noise" perfectly; a rough heuristic (contains
   spaces, mostly letters) was used when comparing versions.
3. **Diffing two versions** (`tools/diff_vi.py`) — runs both extractions on two files and reports
   strings unique to each side. This is the single most useful technique here: it cuts through the
   noise because compiled-code noise differs almost everywhere between any two builds, but it's the
   handful of genuinely new/removed *readable* strings (multi-word, mostly letters) that tell you
   what actually changed functionally.

## Limitations — be explicit about these when using this wiki

- **No wiring/case logic.** We know controls exist (e.g. `CycleSchedule`) and that an event case
  fires on their value change, but not what the case actually *does*. Anything about exact
  algorithm behavior, specific numeric setpoints, or control-flow order is inference from naming,
  not verified from the diagram.
- **Diffs need the right baseline.** Comparing the wrong pair of versions attributes unrelated
  branch differences (e.g. EMCCD camera controls) to the wrong feature. Always check which branch
  you're actually diffing against — see VERSION_HISTORY.md for the branch relationships already
  worked out.
- **Files can change between reads.** `4.5_3StateClamping.vi` changed size mid-session while this
  wiki was being written. Re-run the tools before trusting stale conclusions if a file's mtime is
  newer than this wiki's.

## Regenerating / extending this wiki

```powershell
# from this folder (V6_ParallelLoop)
$DIR = "G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking"

# dump raw + decompressed strings for one VI
py tools\extract_strings.py "$DIR\Min_Track N beads 4.6_KimLabMTroom_4ParallelLoop.vi" out_raw.txt
py tools\decompress_vi.py  "$DIR\Min_Track N beads 4.6_KimLabMTroom_4ParallelLoop.vi" out_decompressed.txt

# diff two versions to see what changed
py tools\diff_vi.py "$DIR\Min_Track N beads 4.6_KimLabMTroom_4ParallelLoop.vi" "$DIR\<new V6 file>.vi" diff_out.txt
```

Then grep `diff_out.txt` for readable multi-word strings (lines matching something like
`[a-z] [a-zA-Z]+ [a-z]`) to filter out compiled-code noise, and fold anything meaningful into
`VERSION_HISTORY.md` and `GLOSSARY.md`.

If a real LabVIEW installation is available in a future session, prefer more authoritative options
over this technique: VI Analyzer, `File > Create VI Documentation` (HTML/RTF export with front
panel + diagram images), or VI Scripting via a LabVIEW instance — any of these would give ground
truth this wiki can't reach.
