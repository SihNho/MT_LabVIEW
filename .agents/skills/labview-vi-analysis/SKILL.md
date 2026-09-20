---
name: labview-vi-analysis
description: Reverse-engineers compiled LabVIEW .vi files in this project (Kim Lab magnetic tweezers "2. Tracking" / "AAA_UNIST" control software) by extracting and diffing the text embedded in the binary. NOTE: LabVIEW 2026 IS installed on this machine and VI Scripting works, so this byte-level technique is the FALLBACK for fast offline diffing, not the primary method - open or script the VI for ground truth whenever wiring or logic matters. Use this whenever the user asks to read, open, inspect, summarize, explain, or "analyze" any .vi file in this project; whenever they ask what changed, what's new, or what's different between two VI versions (e.g. "what did 4.6 change", "diff 4.5 vs 4.6", "why is this called 3StateClamping/4ParallelLoop/MagnetOrder"); whenever they ask about this project's architecture, subsystems, sub-VI dependencies, hardware, or version history; and whenever they ask to update, extend, regenerate, or check the project wiki under V6_ParallelLoop/. Also trigger on bare mentions of a .vi filename with a question attached, even without the word "analyze".
---

# LabVIEW .vi Analysis — Kim Lab Tracking Project

## Read this first — the premise changed (updated 2026-08-26)

**LabVIEW 2026 IS installed on this machine** and **VI Scripting is enabled and proven working** — a
driver VI has programmatically created objects, including a For Loop, on another VI's block diagram.
This skill was originally written assuming no LabVIEW was available; that assumption is **wrong** and
has been since 2026-08-24.

So the ordering is now:

1. **Ground truth: open the VI, or script it.** For anything about *wiring, logic, control flow or
   structure*, open the file in LabVIEW (on a COPY — never modify an original, see `AGENTS.md`) or use
   VI Scripting to interrogate it programmatically. The byte technique below CANNOT recover wiring.
2. **This skill's byte extraction is still genuinely useful** for what it is good at: fast offline
   diffing between two saved `.vi` files, recovering control labels / comments / ring-item lists
   without launching anything, and working while LabVIEW is busy or reserved by the user's experiment.
   It is also the only option if a future session has no GUI access.

A worked example of its continuing value: dumping the ring constants out of NI's `Adding Objects.vi`
listed every object class `New VI Object` can create, before that VI was ever opened.

Before touching LabVIEW at all, read `AGENTS.md` (hard rules), `STATUS.md` (current state and the
`labview-lock`), and invoke the `labview-automation` skill (how to edit a VI with code, and how to
hit a GUI target without wasting round-trips).

**Script location:** byte-identical copies live at `.Codex/skills/labview-vi-analysis/scripts/`
(canonical, self-contained with this skill) and at `V6_ParallelLoop/tools/` (referenced by
`ANALYSIS_METHOD.md`). Change one, change the other, or they silently drift.

## Why this skill exists

A `.vi` file is LabVIEW's compiled `RSRC` binary container, with no built-in plain-text export.

The project wiki at `V6_ParallelLoop/` (README.md, ARCHITECTURE.md, docs/GLOSSARY.md;
older analyses in archive/) already documents the results of applying this technique through
version 4.6. Read that first — the answer to "what does X control do" or "what changed in version Y"
may already be there. Only re-run the scripts when the wiki doesn't cover it, or when analyzing a file
newer than what the wiki reflects.

## Windows/Python gotcha — read this before running anything

On this machine, `python3` and `python` invoked through the Bash tool intermittently resolve to a
broken Windows Store alias stub — it exits with code 49 and prints just `Python`, doing nothing
useful. **Use the PowerShell tool with the `py` launcher instead** — it reliably reaches the real
Python 3.10 interpreter:

```powershell
py "scripts\extract_strings.py" "<path to .vi>" "out_raw.txt"
```

If you're in an environment where `python3` works fine via Bash, that's also fine — just verify the
first call actually produced output before trusting it silently.

## Workflow

### 1. Reading/summarizing a single .vi file

```powershell
py "scripts\extract_strings.py"  "<file>.vi" "raw_strings.txt"       # dependency paths only (fast)
py "scripts\decompress_vi.py"    "<file>.vi" "decompressed.txt"      # + control labels, comments, event cases
```

Grep `decompressed.txt` for the sub-VI dependency block (lines ending in `.vi`/`.ctl`/`.lvlib`) to map
which subsystems the file touches (camera/`IMAQdx`, stage/`ASI TG-1000`, motor/`MOV`,`POS?`,`SetCommand`,
tracking/`bandpass`,`calibration`, force/`Magnet2Force`,`WLC`, cycling/`CycleSchedule`,`Mag Arr`,
`Force Arr`). See `V6_ParallelLoop/ARCHITECTURE.md` for the full subsystem map already built from this
project's files — a new version almost always reuses the same sub-VI vocabulary.

### 2. Diffing two versions to find out what changed

This is the highest-signal operation available. Compiled-code noise differs everywhere between any
two builds, but the small number of genuinely new/removed *readable* strings (multi-word, mostly
letters — `diff_vi.py` already filters for this) reliably point at what changed functionally.

```powershell
py "scripts\diff_vi.py" "<old version>.vi" "<new version>.vi" "diff_out.txt"
```

Read both the "only in NEW" and "only in OLD" sections — a renamed control shows up as one string in
each. Ignore short/symbol-heavy garbage lines that slip through the filter; focus on lines that read
as real words or phrases.

**Pick the right baseline.** This project has branching version names (e.g. `4.4_EMCCD` is a separate
camera-support branch, not a strict ancestor of `4.5`/`4.6` — diffing against the wrong branch
attributes unrelated differences to the wrong feature). Check `V6_ParallelLoop/VERSION_HISTORY.md` for
the already-worked-out branch relationships before picking which file to diff against.

### 3. Re-verify before trusting a stale read

VI files in this project get resaved during active work. If a file's `LastWriteTime` is newer than the
last time it was analyzed (check `VERSION_HISTORY.md` for the timestamp recorded there, or just
`Get-ChildItem` it), re-run the extraction — don't repeat old conclusions as current fact. This bit the
first pass on `4.5_3StateClamping.vi`, which changed size mid-session.

## Known limitations — always disclose these when reporting findings

- **No wiring/case logic.** This recovers text, not the diagram. Statements about exact algorithm
  behavior, specific numeric setpoints, or control-flow order are inference from control/variable
  naming, not verified from the block diagram. Say so.
- **Decompressed streams mix real text with code noise.** The heuristic filter (letters-heavy,
  multi-word) in `diff_vi.py` cuts most of it, but isn't perfect — sanity-check anything surprising.
- **Branch vs. lineage ambiguity.** Version names in this project don't always form a strict line of
  descent (see `4.4_EMCCD` above). Don't assume the file with the next-highest version number is the
  direct parent without checking.
- **A real LabVIEW installation IS available (2026-08-26) - prefer it whenever wiring or logic
  matters.** VI Analyzer, `File > Create VI Documentation`, and especially **VI Scripting** (proven
  working; see `LEARNING.md` and the `labview-automation` skill) give ground truth this method cannot reach.

## Keeping the wiki in sync

If this skill's workflow turns up something new (a new control, a changed subsystem, a new version
diffed) that isn't already reflected in `V6_ParallelLoop/`, update the wiki as part of finishing the
task rather than leaving the finding only in the conversation:

- New/renamed controls or terms → add a line to `docs/GLOSSARY.md`
- New sub-VI dependencies or a structural change (e.g. new parallel loop, new subsystem) → `ARCHITECTURE.md`
- A new version analyzed, or a diff run against an existing version → add a dated entry to `VERSION_HISTORY.md`, following the existing format (file/date/size table row, then a prose section citing the specific evidence strings found)

Keep entries evidence-based, in the same terse, cited style as the existing wiki — state what string(s)
were found, not just a conclusion, so a future reader (human or LLM) can verify it without re-running
the scripts.

## Example

**User:** "what changed between 4.6 and the new V6 file I just saved?"

1. Confirm both files exist and check `V6_ParallelLoop/VERSION_HISTORY.md` for whether 4.6 has already
   been diffed against anything relevant.
2. Run `diff_vi.py` old=4.6, new=the new V6 file.
3. Read the output, separate real findings from noise, cross-reference control names against
   `docs/GLOSSARY.md`/`ARCHITECTURE.md` to describe *what* changed in domain terms, not just *that* a string
   changed.
4. Report findings to the user with the limitations caveat, and append a dated section to
   `VERSION_HISTORY.md`.
