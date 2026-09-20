---
type: reference
status: current
date: 2026-09-03
tags: [docs, fixture]
---

# Fixture recording — what was inserted into the working copy (2026-09-01)

Target: `..\Min_Track N beads V6_ParallelLoop.vi` (the user-authorized working copy; the original
`Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi` is untouched). Saved 473,317 B, mtime
2026-09-01 12:07:59, ExecState 1 (compiles). All four nodes sit inside the tracking while loop
(Diagram uid 639).

| node (uid) | inputs | outputs |
|---|---|---|
| IMAQ Write TIFF File 2 (22700) | `Image` <- branch of acquisition `Image Out`; `File Path` <- Build Path; `error in (no error)` <- branch of acquisition `error out` (forces TIFF after acquisition) | `error out` UNWIRED on purpose: an unwired error out that receives an error raises LabVIEW's automatic error dialog = loud stop, acceptable for an attended fixture |
| Format Into String (22703, class FormatScanString) | `format string` <- constant `img%05d.tif` (made with the node's right-click *Edit Format String...* dialog); `input 1` <- branch of the frame-index subtract `x-y` (uid 5119, the node that feeds 'Save trace'.`frame index`) | `resulting string` -> Build Path |
| Strip Path (23175) | `path` <- GUI branch of the file-path wire feeding 'Save trace'.`base path/filename` | `stripped path` -> Build Path (= the .tra directory) |
| Build Path (23020) | `base path`, `name or relative path` | `appended path` -> TIFF `File Path` |

Frame-number semantics (user, 2026-09-01): the .tra frame number is `current image number - first
image number`; camera buffer numbers keep incrementing through dropped frames, so lost frames show
as gaps. The image filename branches the SAME subtract output, so `imgNNNNN.tif` <-> .tra row
alignment is definitional, gaps included.

## Decisions and their evidence

- **Error SERIES splice (acq -> TIFF -> analysis) skipped.** Byte-scan of both sub-kernels
  (`Track 1 of N bds xyz-kernel-reentrant.vi`, `Track 2 of N bds xyz-kernel-reentrant-v2.vi`) shows
  the only image access is `Omars IMAQ ImageToArray.vi` (read-only). No in-place modification, so
  concurrent TIFF write and analysis of the same buffer are race-free; the next acquisition cannot
  start before the iteration completes (dataflow). This resolves the peer review's conditional
  (archive/peer/2026-09-01-...fixturewrite-plan-attack.md: "critical IF analysis modifies its
  source in place") in the safe direction.
- TIFF compression: CORRECTION 2026-09-03 — the pane DOES have a `TIFF Options`[9] input
  (and an `Image Out (duplicate)`[3] passthrough); both left unwired, so compression = NI
  default (none). Color Palette unwired (grayscale). Wire an explicit options constant later if
  a reader needs a guaranteed layout.
- `%05d` is a minimum width: frame >= 100000 gets 6 digits.

## Verification level: STRUCTURAL only

ExecState 1; every wire confirmed by wire-count (+1) or by the loud-5001 name probe; branches
confirmed by screenshot. No data has flowed. Functional acceptance = the user's run: a few frames
at low frame rate with saving on -> the .tra directory must fill with `imgNNNNN.tif` whose numbers
match .tra frame numbers. That dataset is the input for the four-fold vs v3 numeric acceptance
(rule 1a). Still to check on that data: whether `.tra` stores raw kernel output or calibrated
values; image type/size/border/cross size/cal file/bead count for the offline harness.

## How it was built (recipes now in the skill)

TIFF writer via `gscript.drop_subvi` (LLB member path has NO `.vi` extension); the three
primitives via the right-click Functions palette (Quick Drop is broken in this install, peer
reviewed); node-to-node wires via `gscript.wire` (branch=True added); the Strip Path input via a
reverse-direction GUI branch (start on the terminal, end on the existing wire); the format
constant via *Edit Format String...*. `Track File Path` is invisible to erdosmiller Get Controls
from all 170 diagrams (non-pane control), hence the GUI branch.
