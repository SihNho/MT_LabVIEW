---
type: narrative
status: historical
date: 2026-09-01
tags: [archive]
---

# STATUS — read this first (keep under one screen; push detail DOWN a layer, never append here)

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  owner:
  since: 2026-09-01 12:10 (fixture insertion COMPLETE and saved; next step is the USER running frames)
  purpose:
```

## Current state, one paragraph

**`PARALLEL_kernel_v3.vi` assembly is functionally complete and legal** (claudeDev, 68,138 B,
Wire 262+, ExecState 1, cold-verified): P=4 loop runs `Track 1 of N` per bead; all 9 inputs wired
(x,y,z via 3-output Decimate outside the loop; both cosine windows through NON-indexed tunnels);
all 3 outputs driven (X/Y/Z → 3-input Interleave → `x,y,z array out`; bead-good and
`Index of closest cal image slice` → indicators). The old four-fold structure remains inside as
dead code — its outputs are cut but **it still executes**, so delete/disable it before any speed
measurement. Originals untouched; the rig standardised on LabVIEW 2026 (2019 is history).

## FIXTURE BUILD COMPLETE (2026-09-01 12:08, structural level - user run pending)

All edits live in the working copy `..\Min_Track N beads V6_ParallelLoop.vi` (saved 473,317 B,
mtime 12:07:59, ExecState 1 = compiles). Inside the tracking while loop (Diagram uid 639):

- **IMAQ Write TIFF File 2** (uid 22700): `Image` <- branch of acquisition `Image Out`;
  `File Path` <- Build Path; `error in` <- branch of acquisition `error out` (orders TIFF after
  acquisition). `error out` left UNWIRED **on purpose**: an unwired error out that receives an
  error raises LabVIEW's automatic error dialog = a loud stop, acceptable for an attended fixture.
- **Format Into String** (uid 22703): `format string` <- constant `img%05d.tif` (created via the
  node's right-click *Edit Format String...* dialog); `input 1` <- branch of the frame-index
  subtract `x-y` (uid 5119, the node feeding 'Save trace'.`frame index` - so image names use THE
  value written to .tra, gaps included).
- **Strip Path** (uid 23175): `path` <- GUI branch of the file-path wire feeding
  'Save trace'.`base path/filename` -> directory = the .tra directory.
- **Build Path** (uid 23020): `base path` <- Strip Path; `name or relative path` <- Format.

**Error SERIES splice (acq->TIFF->analysis) deliberately SKIPPED**: byte-scan of BOTH sub-kernels
(`Track 1 of N bds xyz-kernel-reentrant.vi`, `Track 2 of N bds xyz-kernel-reentrant-v2.vi`) shows
the ONLY image access is `Omars IMAQ ImageToArray.vi` = read-only; no in-place modification, so
concurrent TIFF write + analysis of the same buffer is race-free. This resolves the peer review's
conditional ("critical IF analysis modifies its source in place") in the safe direction.

**NEXT (user, hardware-side):** run the working copy a few frames at a low frame rate with saving
on -> the .tra directory should fill with `imgNNNNN.tif` whose numbers match .tra frame numbers
(lost frames = gaps in both). That run is the fixture for the four-fold vs v3 numeric acceptance.

**Verification level: STRUCTURAL only** (ExecState 1 + wiring verified by count/probe/screenshot).
No data has flowed; filename<->frame alignment and TIFF pixel correctness are UNVERIFIED until the
run.

## (superseded) Waiting on: the user's FIXTURE (functional acceptance gate)

Per-frame recording at a very low frame rate, into the untouched main-VI working copy
`Min_Track N beads V6_ParallelLoop.vi` (verified 2026-09-01: mtime still 2026-08-24, never edited):
1. image per frame (TIFF or raw block), zero-padded frame number in the name;
2. that frame's trace row — ideally the KERNEL'S RAW output as an extra column (check whether
   `.tra` stores raw kernel output or exp-ref/calibrated values before trusting comparisons);
3. per-frame `Bead is good?` array; 4. `.cal` + `.tra` as usual;
5. one sidecar per session: image type (U8/U16/I16?), width, height, **border size**, cross size,
   cal file used, bead count.
Then: same inputs → four-fold vs v3, numerically identical X/Y/Z = rule-1a acceptance.

## Next actions (in order)

1. ~~Connector pane~~ **already complete**: v3 is a byte copy, so it inherited the four-fold's
   entire pane — verified 2026-08-31, pane widgets pixel-identical (pattern + per-slot type
   colours). Scripting API for future recipes recorded in the skill (Pattern 4815, Assign Control
   To Terminal, Controls[] readback).
2. ~~OpSetIndexMode~~ **BUILT & FUNCTIONALLY VERIFIED** (2026-09-01: flipping scrap-v2 tunnels
   0→11 turned the visible tunnel glyph from auto-index bracket to solid square, with the expected
   downstream type break — the op writes IndexMode for real; v2 reverted unsaved). **BUILT** (10,461 B, ExecState 1, wrapper `gscript.set_index_mode()`;
   one-time bootstrap done under the gated GUI with recorded evidence — class picker, PN placement,
   Select Class, Index Mode row, Change-All-To-Write; value + one error wire landed by script).
   Remaining fleet work, REVISED by peer attack (archive/peer/2026-09-01-...opwireref-donor-plan-attack.md
   — generic OpWireRef scored 4/10, **fused topology-specific creators 8/10**):
   (a) reporter-dump `Conditionally Connect Wire.vi`'s pane before any use (publicly undocumented);
   (b) build FUSED ops per topology (tunnel→indicator via Exit-For-Loop capture; primitive wiring
   via primitive-specific terminal properties — IndexArray exposes `Array Input Terminal` etc.);
   (c) donor with labels = discovery hints only + before/after reporter acceptance test;
   (d) wire PN `error out` → indicator in OpSetIndexMode. Then integrate into
   **`tools/recipes/build_v3.py`** to replace its GUI pauses.
3. **Functional acceptance**: user-made fixture (per-frame TIFF/raw + tra + cal), same inputs
   through four-fold and v3, numerically identical X/Y/Z. Then remove the dead structure and
   benchmark.

## The work cycle (user directive, 2026-08-31)

1) plan + **peer-review the plan** → 2) write ONE long script (all names from
[docs/NAMES.md](docs/NAMES.md)) → 3) execute as a batch → 4) read results, revise → 5) repeat.
No mid-run name discovery; no per-step verification loops.

## Where everything else lives

- [docs/NAMES.md](docs/NAMES.md) — **verified terminal/label strings** (newlines are real!). Check here BEFORE any wiring call.
- [.claude/skills/labview-automation/SKILL.md](.claude/skills/labview-automation/SKILL.md) — technique: COM traps, GUI recipes, error meanings.
- [tools/gscript.py](tools/gscript.py) — the op fleet wrappers (docstrings are contracts).
- [CLAUDE.md](CLAUDE.md) — standing rules. [ARCHITECTURE.md](ARCHITECTURE.md) — the rig.
- [archive/](archive/) — history, incl. `2026-08-31-status-full-assembly-narrative.md` (the full
  assembly log this file replaced) and `peer/` exchanges. Not read in normal work.
