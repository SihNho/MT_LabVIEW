---
type: reference
status: current
date: 2026-09-14
tags: [docs, main-vi]
---

# Main VI front panel — every object, by role

> Document 2 of the system inventory (`docs/system-inventory-plan.md`).
>
> **Source: the running VI itself.** Read through `Panel.Controls[]` (6348801) → `Control.Label` → `Text.Text`
> and `Control.Indicator` (6332007), i.e. LabVIEW's own object list — not a byte scan, not a screenshot.
> `tools/bench/find_rotor_controls.py`, 2026-09-14, 114 objects in 120 s.
>
> **Wiring column added 2026-09-14** (section at the end, measured by `OpPanelWiring_v0`): 104 of the 114 objects
> have a wired diagram terminal; **10 have a bare terminal** (`Focus Step (F1)`, `+ Inc (PgUp)`, `- Inc (PgDn)`,
> `File # Saved`, `continue tracking`, `Image`, `Send`, `Rot step (turns)`, `Stop Trans`, `Rot \nSpeed`). A bare
> terminal means "not used *via its terminal*" — the main VI also reaches objects through local variables and
> `Value` property nodes, which that read does not see — so the "unused legacy" verdict the user warned about
> still needs the property-node / local-variable census (next pass). *Presence here is still not evidence of use.*

**114 objects: 60 controls, 54 indicators.** The CTL/IND split is itself informative and is used below — several
things that read like settings turn out to be read-backs, and vice versa.

## The startup configuration cluster

Four controls, greyed out on the panel, sitting together top-right. This is what the user meant by
*"프로그램 맨 시작부분에 분명 position을 입력해뒀을거임"* — the operator tells the program where things are
before a run.

| # | label | type | value seen 2026-09-14 |
|---|---|---|---|
| 43 | `Autoreference? 1=Y` | CTL | 0 |
| 44 | `If no: current pos z?` | CTL | 30 |
| **45** | **`Current pos rot?`** | **CTL** | **0** |
| 46 | `Set Focus  (0->50)` | CTL | 51.5 |

`Current pos rot?` being a **control** matters: the rotor's absolute position is *told to* the program, not read
from the device. That is the shape a software zero-offset would take. Whether this control is what
`Rot pos (deg)` is measured against is a wiring question, not yet answered.

## Rotor

| # | label | type | note |
|---|---|---|---|
| 16 | `Rot step (turns)` | CTL | |
| 18 | `Rot pos (deg)` | IND | the displayed position — a read-back, so something computes it |
| **40** | **`Auto-reset zero`** | **CTL** | **exists, but was NOT visible on the panel** — hidden or outside the window |
| 45 | `Current pos rot?` | CTL | see above |
| 70 / 71 | `1 L-Turn` / `1 R-Turn` | CTL | the manual relative buttons |
| 72 | `Rot Step (deg) ` | CTL | note the trailing space in the label |
| 73 | `Rot \nSpeed` | CTL | the label contains a real newline |
| 74 | `Send to Rot` | CTL | |
| 100 | `RotationVISA` | IND | the rotor's own VISA session — a third session, separate from stage and motor |
| 104 | `TurnOff` | IND | |

`Auto-reset zero` is the one object this inventory found that a screenshot could not: it is a real control at tab
index 40, and hunting for it visually failed. That is the argument for this document existing.

## Magnet motor — and the `Cal Zero` naming trap

| # | label | type |
|---|---|---|
| 75 | `- Cal Zero` | CTL |
| 76 | `+ Cal Zero` | CTL |
| 89 | `Cal Zero` | **IND** |

The CTL/IND split confirms the user's account exactly (ARCHITECTURE.md §3): `+`/`-` are **buttons**, and plain
`Cal Zero` is a **display** of the magnet-motor position — `Cal Zero` = position 0, `+ Cal Zero` = a position
between 36 and 38. `- Cal Zero` is legacy and believed unused; that remains to be shown by wire topology before
anything is removed.

Nothing here is a calibration or rotor zero, which is what the name suggests and what I initially mis-read.

## Camera and image

| # | label | type | note |
|---|---|---|---|
| 12 | `Image` | IND | |
| 34 | `Width` | **IND** | |
| 35 | `Height` | **IND** | |
| 98 | `Frame rate` | **CTL** | value 25 |
| 101 | `IMAQimage` | IND | |
| 102 | `CamSessionOut` | IND | |
| 103 | `current image number` | IND | |
| 62 | `pixel distance (nm)` | CTL | 84 |
| 63 | `Cross length (pixels)` | CTL | 120 |

**`Width` and `Height` are INDICATORS.** This settles a question that a screenshot alone made confusing: the panel
showed `640 × 512` while the camera, read directly through the driver the same night, was at **1280 × 1024,
binning 2×2, 90.00 Hz**. There is no contradiction — the panel is showing what the *last run* ended with, not what
the code will set. It also matches the 2026-09-12 finding that `IMAQdxOpenCamera` resets the ROI, so every run
begins full-frame.

**Open, and not to be guessed:** `Frame rate` is a CONTROL holding **25**, while the camera runs at **90 Hz**. So
either it is not the camera's rate (a display or logging rate, say), or it is not wired to the camera at all. The
byte scan offers no way to tell these apart, and neither does the panel. Marked open.

## Cycling / scheduler

| # | label | type |
|---|---|---|
| 105 | `CycleSchedule` | CTL |
| 107 | `NumCol` | CTL |
| 106 | `Mag Position` | IND |
| 52 | `SubCycle` | IND |
| 53 | `Set # of Cycles` | CTL |
| 54 | `Start Cycles` | CTL |
| 50 | `Start Moving?` | IND |
| 51 | `Reached clamp` | IND |
| 55 / 56 / 57 / 59 | `Initial Time at Start` / `Estimated end time (min)` / `Time span after start (min)` / `Cycle Start Time` | IND |
| 99 | `Total cycle #` | IND |
| 58 | `Switch` | CTL |

This is where the rotor row will be added (`docs/rotor-scheduler-design.md`).

## Translation stage

| # | label | type |
|---|---|---|
| 22 | `Trans Speed (mm/s)` | CTL |
| 77 | `Trans Step (mm)` | CTL |
| 78 | `Send to Trans` | CTL |
| 23 | `Stop Trans` | CTL |
| 17 | `HOME` | CTL |
| 15 | `Send` | CTL |
| 87 | `Trans Pos (mm)` | IND |
| 19 | `Max Trans Pos` | IND |
| 88 | `Max Travel Limit` | IND |

## Focus / autofocus

| # | label | type |
|---|---|---|
| 2 | `Focus Step (F1)` | CTL |
| 3 / 4 | `+ Inc (PgUp)` / `- Inc (PgDn)` | CTL |
| 33 | `Focus Deviation from the Center` | CTL |
| 67 | `Focus Pos (Start)` | CTL |
| 38 | `Auto-Focus` | CTL |
| 48 | `Limit of Auto-Focus` | CTL |
| 32 | `Focus Pos (Track)` | IND |
| 82 | `Focus Pos (Cal)` | IND |

## Calibration stack

| # | label | type |
|---|---|---|
| 64 | `z step (um)` | CTL |
| 65 | `# to avg per image` | CTL |
| 66 | `# images in stack` | CTL |
| 31 | `Fix to a Certain Pattern` | CTL |
| 79 | `Done Picking \nBeads?` | CTL |
| 10 | `Pos within cal image` | IND |
| 30 | `Pos: Diffraction Pattern` | IND |
| 84 | `Intensity vs Radius` | IND |
| 90 | `Cal File Path` | IND |
| 14 | `exp/ref \narray` | IND |

## Force / physics

| # | label | type |
|---|---|---|
| 26 / 27 | `Lc` / `Lp` | CTL |
| 28 / 29 | `Baseline` / `Exp Baseline` | CTL |
| 60 / 61 | `+ -> Lc` / `x -> Lc` | CTL |
| 25 | `# FD points` | CTL |
| 97 | `# DT points` | CTL |
| 94 | `Force\nsmoothing\nhalf-width` | CTL |
| 95 | `Extension\nmedian filter\nhalf-width` | CTL |
| 21 | `Correction Factor` | CTL |
| 20 | `Z/dZ` | CTL |
| 24 | `Force (pN) vs Extension (nm) ` | IND |
| 96 | `Extension (nm) vs Time (Frame #)` | IND |

## Run control, files, errors

| # | label | type |
|---|---|---|
| 0 / 49 | `stop (end)` / `stop (end) 2` | CTL |
| 11 | `continue tracking` | CTL |
| 13 | `Reset Tracking` | CTL |
| 37 | `Auto-Reset` | CTL |
| 47 | `Limit of Program` | CTL |
| 42 | `# of Points` | CTL |
| 92 | `Count` | CTL |
| 93 | `Mp measure freq` | CTL |
| 1 | `Total Lost Frames` | IND |
| 9 | `Missing Frames?` | IND |
| 41 | `Lost Frame Message` | IND |
| 39 | `# of Auto-Reset` | IND |
| 5 / 7 / 8 | `File Size` / `File # Saved` / `file progress` | IND |
| 91 | `Track File Path` | IND |
| 6 | `error out 2` | IND |

## Objects with generic names — the legacy-leftover candidates

| # | label | type |
|---|---|---|
| 108 | `x < y?` | IND |
| 109 | `Target` | IND |
| 110 | `Value` | IND |
| 111 | `abs(x)` | IND |
| 112 | `Value 2` | IND |
| 113 | `Value 3` | IND |
| 36 | `min value` | IND |
| 85 | `size(s)` | IND |
| 86 | `output cluster` | IND |
| 68 / 69 | `color table string` / `Color table` | IND |
| 80 | `Bead Pos` | IND |
| 81 | `Waveform Graph` | IND |
| 83 | `Picture` | IND |

`x < y?`, `abs(x)`, `Target`, `Value`, `Value 2`, `Value 3` are LabVIEW's **default names for primitive outputs**
— the names you get when an indicator is created straight off a comparison or an arithmetic node and never
renamed. Together with their position at the very end of the tab order (108–113, i.e. added last), they are the
strongest candidates for the leftovers the user described.

**They are candidates, not conclusions.** A default name proves only that nobody renamed it; it says nothing
about whether a wire reaches it. Rule 1a forbids changing behaviour, so each one must be shown unreachable by
wire topology before the restructuring drops it.

## Notable label hazards, for anyone writing code against these names

Three labels contain characters that break naive name matching, and the fleet's wiring ops match by exact string:

- `Rot Step (deg) ` — **trailing space**
- `Rot \nSpeed`, `Done Picking \nBeads?`, `Force\nsmoothing\nhalf-width`, `Extension\nmedian filter\nhalf-width`,
  `exp/ref \narray` — **real newlines inside the label**
- `Force (pN) vs Extension (nm) ` — **trailing space**

These are the same class of trap already recorded in `docs/NAMES.md`: a label that *renders* on two lines may
contain a genuine newline, and a name-based API fails on it silently-ish.

## The wiring column — attempted 2026-09-14, and why it is still empty

A join of these 114 objects against the complete diagram sweep returned **92 "not found"**. That is a verdict on
the method, not on the panel: the sweep walks `AbstractDiagram.Nodes[]`, and a front-panel object's terminal is a
**`ControlTerminal` — a Terminal, not a Node** — so it never appears. The 15 apparent matches were Global and
Property nodes sharing a label. The join is void (`tools/bench/panel_wiring.json` is kept only as the record).

The valid route is `Traverse('ControlTerminal')` → `Terminal.Connected Wire` (634A000) with the terminal's
label — a Terminal-class property read on a GObject-typed reference, i.e. the class-cast problem that also blocks
node identity and global read/write direction. **One capability, three gaps.** Details in
`docs/toolkit-capabilities.md`.

What the sweep *did* give this document: the startup frames consume `Set Focus (0->50)` (43→frames 1, 9) and
`If no: current pos z?` (44→frame 2) — see `docs/main-vi-startup.md`. Those two are therefore **live**, by
measurement. Nothing else in this document has that status yet.

## Next pass

1. **Which terminal does each object reach, and is it wired?** This is the column that turns a list into a map,
   and it is what separates live settings from leftovers. Blocked as above.
2. **Where is `Auto-reset zero` on the panel** — position and visibility, so it can be shown to the user.
3. **Is `Frame rate` (25) connected to the camera at all?**
4. **What does `Current pos rot?` feed?** — the likely rotor zero.

<!-- wiring-section:begin -->

## Wiring column — measured 2026-09-14 with `OpPanelWiring_v0` (`Control.Terminal` → `Terminal.Connected Wire`)

Source `tools/bench/main_vi_panel_wiring.json` (114 rows, one op run, `test_oppanelwiring.py` T3). **Semantics:** *terminal wired = YES* means the object's block-diagram terminal carries a wire; *NO* means the terminal is bare. A bare terminal does **not** prove the object is unused — the main VI reads and writes objects through local variables and `Value` property nodes (106 property nodes), which this read does not see. So NO = "not used via its terminal"; "unused" needs the property-node/local census (next pass). `Is Source?` agreed with CTL/IND on every row (controls' terminals are sources, indicators' are sinks).

**10 objects have a bare terminal:**

- CTL `'Focus Step (F1)'` (uid 87)
- CTL `'+ Inc (PgUp)'` (uid 159)
- CTL `'- Inc (PgDn)'` (uid 174)
- IND `'File # Saved'` (uid 6)
- CTL `'continue tracking'` (uid 41)
- IND `'Image'` (uid 31543)
- CTL `'Send'` (uid 5700)
- CTL `'Rot step (turns)'` (uid 5789)
- CTL `'Stop Trans'` (uid 7715)
- CTL `'Rot \nSpeed'` (uid 11595)

| # | label | type | terminal wired | wire uid | control uid |
|---:|---|---|---|---:|---:|
| 0 | `stop (end)` | CTL | YES | 6929 | 7 |
| 1 | `Total Lost Frames` | IND | YES | 27824 | 421 |
| 2 | `Focus Step (F1)` | CTL | **NO** |  | 87 |
| 3 | `+ Inc (PgUp)` | CTL | **NO** |  | 159 |
| 4 | `- Inc (PgDn)` | CTL | **NO** |  | 174 |
| 5 | `File Size` | IND | YES | 3266 | 3229 |
| 6 | `error out 2` | IND | YES | 4800 | 4977 |
| 7 | `File # Saved` | IND | **NO** |  | 6 |
| 8 | `file progress` | IND | YES | 5274 | 1877 |
| 9 | `Missing Frames?` | IND | YES | 3689 | 1819 |
| 10 | `Pos within cal image` | IND | YES | 121 | 49 |
| 11 | `continue tracking` | CTL | **NO** |  | 41 |
| 12 | `Image` | IND | **NO** |  | 31543 |
| 13 | `Reset Tracking` | CTL | YES | 10312 | 5605 |
| 14 | `exp/ref \narray` | IND | YES | 2332 | 4983 |
| 15 | `Send` | CTL | **NO** |  | 5700 |
| 16 | `Rot step (turns)` | CTL | **NO** |  | 5789 |
| 17 | `HOME` | CTL | YES | 24619 | 5951 |
| 18 | `Rot pos (deg)` | IND | YES | 7152 | 6349 |
| 19 | `Max Trans Pos` | IND | YES | 31920 | 6184 |
| 20 | `Z/dZ` | CTL | YES | 730 | 47 |
| 21 | `Correction Factor` | CTL | YES | 6096 | 9289 |
| 22 | `Trans Speed (mm/s)` | CTL | YES | 14421 | 7449 |
| 23 | `Stop Trans` | CTL | **NO** |  | 7715 |
| 24 | `Force (pN) vs Extension (nm) ` | IND | YES | 10908 | 8038 |
| 25 | `# FD points` | CTL | YES | 9000 | 8918 |
| 26 | `Lc` | CTL | YES | 16585 | 19716 |
| 27 | `Lp` | CTL | YES | 5959 | 19743 |
| 28 | `Baseline` | CTL | YES | 8254 | 19758 |
| 29 | `Exp Baseline` | CTL | YES | 7931 | 8455 |
| 30 | `Pos: Diffraction Pattern` | IND | YES | 121 | 9402 |
| 31 | `Fix to a Certain Pattern` | CTL | YES | 3362 | 10230 |
| 32 | `Focus Pos (Track)` | IND | YES | 5773 | 9238 |
| 33 | `Focus Deviation from the Center` | CTL | YES | 9797 | 9391 |
| 34 | `Width` | IND | YES | 32938 | 9686 |
| 35 | `Height` | IND | YES | 32937 | 10168 |
| 36 | `min value` | IND | YES | 17287 | 17257 |
| 37 | `Auto-Reset` | CTL | YES | 9806 | 17472 |
| 38 | `Auto-Focus` | CTL | YES | 7527 | 24266 |
| 39 | `# of Auto-Reset` | IND | YES | 10205 | 9768 |
| 40 | `Auto-reset zero` | CTL | YES | 11253 | 10208 |
| 41 | `Lost Frame Message` | IND | YES | 11520 | 11486 |
| 42 | `# of Points` | CTL | YES | 1150 | 10008 |
| 43 | `Autoreference? 1=Y` | CTL | YES | 4981 | 10485 |
| 44 | `If no: current pos z?` | CTL | YES | 4892 | 10647 |
| 45 | `Current pos rot?` | CTL | YES | 7559 | 10821 |
| 46 | `Set Focus  (0->50)` | CTL | YES | 6119 | 11009 |
| 47 | `Limit of Program` | CTL | YES | 10142 | 9654 |
| 48 | `Limit of Auto-Focus` | CTL | YES | 11527 | 10173 |
| 49 | `stop (end) 2` | CTL | YES | 15230 | 19587 |
| 50 | `Start Moving?` | IND | YES | 10820 | 341 |
| 51 | `Reached clamp` | IND | YES | 10819 | 9535 |
| 52 | `SubCycle` | IND | YES | 16421 | 24868 |
| 53 | `Set # of Cycles` | CTL | YES | 15283 | 9871 |
| 54 | `Start Cycles` | CTL | YES | 15302 | 9897 |
| 55 | `Initial Time at Start` | IND | YES | 21918 | 10053 |
| 56 | `Estimated end time (min)` | IND | YES | 17447 | 10768 |
| 57 | `Time span after start (min)` | IND | YES | 17688 | 10932 |
| 58 | `Switch` | CTL | YES | 19078 | 18980 |
| 59 | `Cycle Start Time` | IND | YES | 18828 | 19515 |
| 60 | `+ -> Lc` | CTL | YES | 12383 | 12353 |
| 61 | `x -> Lc` | CTL | YES | 11178 | 11136 |
| 62 | `pixel distance (nm)` | CTL | YES | 13111 | 11169 |
| 63 | `Cross length (pixels)` | CTL | YES | 13114 | 11200 |
| 64 | `z step (um)` | CTL | YES | 13117 | 11218 |
| 65 | `# to avg per image` | CTL | YES | 13120 | 11252 |
| 66 | `# images in stack` | CTL | YES | 13123 | 11288 |
| 67 | `Focus Pos (Start)` | CTL | YES | 42795 | 11344 |
| 68 | `color table string` | IND | YES | 14726 | 11414 |
| 69 | `Color table` | IND | YES | 14729 | 11450 |
| 70 | `1 L-Turn` | CTL | YES | 19293 | 11516 |
| 71 | `1 R-Turn` | CTL | YES | 19296 | 11534 |
| 72 | `Rot Step (deg) ` | CTL | YES | 34401 | 11552 |
| 73 | `Rot \nSpeed` | CTL | **NO** |  | 11595 |
| 74 | `Send to Rot` | CTL | YES | 19302 | 11627 |
| 75 | `- Cal Zero` | CTL | YES | 19323 | 11698 |
| 76 | `+ Cal Zero` | CTL | YES | 19327 | 11735 |
| 77 | `Trans Step (mm)` | CTL | YES | 17274 | 11788 |
| 78 | `Send to Trans` | CTL | YES | 19311 | 11804 |
| 79 | `Done Picking \nBeads?` | CTL | YES | 19456 | 11819 |
| 80 | `Bead Pos` | IND | YES | 15789 | 11831 |
| 81 | `Waveform Graph` | IND | YES | 25559 | 11889 |
| 82 | `Focus Pos (Cal)` | IND | YES | 22269 | 12216 |
| 83 | `Picture` | IND | YES | 25108 | 12270 |
| 84 | `Intensity vs Radius` | IND | YES | 25117 | 12286 |
| 85 | `size(s)` | IND | YES | 26074 | 12563 |
| 86 | `output cluster` | IND | YES | 26668 | 12644 |
| 87 | `Trans Pos (mm)` | IND | YES | 31134 | 6125 |
| 88 | `Max Travel Limit` | IND | YES | 33805 | 33150 |
| 89 | `Cal Zero` | IND | YES | 23207 | 31945 |
| 90 | `Cal File Path` | IND | YES | 3769 | 27930 |
| 91 | `Track File Path` | IND | YES | 5303 | 28450 |
| 92 | `Count` | CTL | YES | 30530 | 28051 |
| 93 | `Mp measure freq` | CTL | YES | 31575 | 23942 |
| 94 | `Force\nsmoothing\nhalf-width` | CTL | YES | 31059 | 28148 |
| 95 | `Extension\nmedian filter\nhalf-width` | CTL | YES | 31166 | 28996 |
| 96 | `Extension (nm) vs Time (Frame #)` | IND | YES | 32890 | 28532 |
| 97 | `# DT points` | CTL | YES | 29006 | 28827 |
| 98 | `Frame rate` | CTL | YES | 28882 | 28821 |
| 99 | `Total cycle #` | IND | YES | 31687 | 30309 |
| 100 | `RotationVISA` | IND | YES | 26006 | 25917 |
| 101 | `IMAQimage` | IND | YES | 26665 | 34963 |
| 102 | `CamSessionOut` | IND | YES | 26656 | 28859 |
| 103 | `current image number` | IND | YES | 3747 | 34200 |
| 104 | `TurnOff` | IND | YES | 3457 | 24423 |
| 105 | `CycleSchedule` | CTL | YES | 31742 | 26557 |
| 106 | `Mag Position` | IND | YES | 30272 | 29308 |
| 107 | `NumCol` | CTL | YES | 32901 | 29660 |
| 108 | `x < y?` | IND | YES | 22045 | 9077 |
| 109 | `Target` | IND | YES | 6492 | 4825 |
| 110 | `Value` | IND | YES | 22072 | 25243 |
| 111 | `abs(x)` | IND | YES | 22054 | 38 |
| 112 | `Value 2` | IND | YES | 31717 | 23298 |
| 113 | `Value 3` | IND | YES | 29233 | 22378 |

_Generated 2026-09-14 11:12 by tools/bench/write_panel_wiring_section.py._

<!-- wiring-section:end -->

<!-- locals-section:begin -->

## Local variables and `Value` property nodes — measured 2026-09-14 (`OpNodeTerms_v0` sweep of all 635 nodes)

Source `tools/bench/main_vi_nodeterms.json` (626 nodes, 3328 terminals, 11 mismatches vs the Step-0 cache, node identity verified per node by UID). Class census by Traverse: `Local` 8, `Global` 7, `Property` 106, `Invoke` 1.

**Local variables.** A local-variable node's single terminal is NAMED after its control — an observed rule (it held on every local below and on all seven globals, whose terminal carries the field name), not an NI contract. `Is Source?` TRUE = the local is READ, FALSE = WRITTEN.

| local uid | diagram | owner | control (terminal name) | direction | on panel map | terminal bare? |
|---:|---:|---|---|---|---|---|
| 2991 | 1 | FlatSequenceFrame | `Total Lost Frames` | WRITE | yes |  |
| 4277 | 17 | FlatSequenceFrame | `File # Saved` | WRITE | yes | **bare** |
| 11574 | 73 | CaseStructure | `Focus Pos (Track)` | WRITE | yes |  |
| 3160 | 83 | FlatSequenceFrame | `Rot pos (deg)` | READ | yes |  |
| 3097 | 83 | FlatSequenceFrame | `Trans Pos (mm)` | READ | yes |  |
| 2143 | 83 | FlatSequenceFrame | `Total Lost Frames` | WRITE | yes |  |
| 16942 | 99 | WhileLoop | `Picture` | WRITE | yes |  |
| 25805 | 167 | FlatSequenceFrame | `Color table` | READ | yes |  |

Bare-terminal objects reached through a local: `File # Saved`. Bare-terminal objects with NO local either: `+ Inc (PgUp)`, `- Inc (PgDn)`, `Focus Step (F1)`, `Image`, `Rot 
Speed`, `Rot step (turns)`, `Send`, `Stop Trans`, `continue tracking` — these can still be reached by an implicit `Value` property node (below), a control reference, or an event registration, none of which names its object in a terminal. **Resolved 14:5x (last section of this file):** `Rot \nSpeed`, `Send` and `continue tracking` ARE reached by implicit `Value` nodes; the rest by control references (see "Control references").

**`Value` property nodes:** 106 nodes carry a `Value` row, 88 of them implicit (unwired `reference` = bound to a panel object; **identity measured 14:5x by `OpNodeLabels_v0` — see the last section**). Direction of the `Value` row: READ 47 / WRITE 78. Every `Value` row runs in the UI thread (the cost the restructuring converts to locals by rule).

| diagram | owner | uid | implicit | Value rows |
|---:|---|---:|---|---|
| 1 | FlatSequenceFrame | 10399 | yes | WRITE |
| 1 | FlatSequenceFrame | 10793 | yes | WRITE |
| 1 | FlatSequenceFrame | 12476 | yes | WRITE |
| 5 | Sequence | 31228 | yes | WRITE |
| 5 | Sequence | 29447 | yes | READ |
| 9 | FlatSequenceFrame | 8498 | yes | WRITE |
| 9 | FlatSequenceFrame | 32823 | yes | READ |
| 16 | FlatSequenceFrame | 35917 | yes | READ |
| 16 | FlatSequenceFrame | 35869 | yes | READ |
| 17 | FlatSequenceFrame | 8184 | yes | WRITE |
| 18 | FlatSequenceFrame | 10894 | yes | WRITE |
| 18 | FlatSequenceFrame | 8603 | yes | WRITE |
| 18 | FlatSequenceFrame | 24144 | yes | READ |
| 19 | FlatSequenceFrame | 637 | wired ref | WRITE, WRITE, READ, WRITE, WRITE, READ, WRITE |
| 19 | FlatSequenceFrame | 25380 | wired ref | WRITE, READ |
| 20 | WhileLoop | 6440 | yes | READ |
| 20 | WhileLoop | 25116 | yes | READ |
| 20 | WhileLoop | 22 | yes | READ |
| 21 | FlatSequenceFrame | 25810 | wired ref | WRITE |
| 21 | FlatSequenceFrame | 26991 | wired ref | WRITE |
| 21 | FlatSequenceFrame | 27364 | wired ref | WRITE |
| 21 | FlatSequenceFrame | 27905 | wired ref | WRITE |
| 21 | FlatSequenceFrame | 28631 | yes | READ |
| 21 | FlatSequenceFrame | 28677 | yes | READ |
| 21 | FlatSequenceFrame | 28796 | yes | READ |
| 21 | FlatSequenceFrame | 28853 | yes | READ |
| 21 | FlatSequenceFrame | 28939 | yes | READ |
| 21 | FlatSequenceFrame | 28991 | yes | READ |
| 25 | FlatSequenceFrame | 28484 | yes | WRITE |
| 29 | FlatSequenceFrame | 27777 | yes | WRITE |
| 32 | FlatSequenceFrame | 27113 | yes | READ |
| 32 | FlatSequenceFrame | 27139 | yes | READ |
| 33 | FlatSequenceFrame | 27292 | yes | WRITE |
| 33 | FlatSequenceFrame | 27317 | yes | WRITE |
| 37 | FlatSequenceFrame | 26912 | yes | WRITE |
| 41 | FlatSequenceFrame | 26341 | yes | WRITE |
| 43 | WhileLoop | 1359 | wired ref | WRITE |
| 43 | WhileLoop | 10445 | wired ref | WRITE, READ |
| 43 | WhileLoop | 17289 | yes | READ |
| 43 | WhileLoop | 9879 | yes | READ |
| 43 | WhileLoop | 1469 | yes | WRITE |
| 43 | WhileLoop | 20474 | wired ref | WRITE, WRITE, WRITE |
| 43 | WhileLoop | 22261 | yes | READ |
| 43 | WhileLoop | 17780 | yes | READ |
| 43 | WhileLoop | 30146 | yes | READ |
| 43 | WhileLoop | 29617 | wired ref | READ, WRITE, WRITE, READ, WRITE |
| 43 | WhileLoop | 30117 | yes | READ |
| 43 | WhileLoop | 4580 | yes | READ |
| 43 | WhileLoop | 10153 | wired ref | WRITE, WRITE |
| 43 | WhileLoop | 2457 | wired ref | WRITE, WRITE |
| 43 | WhileLoop | 22560 | yes | READ |
| 43 | WhileLoop | 22542 | yes | READ |
| 46 | EventStructure | 22858 | yes | WRITE |
| 47 | EventStructure | 4810 | wired ref | WRITE |
| 47 | EventStructure | 30783 | yes | WRITE |
| 47 | EventStructure | 3973 | yes | READ |
| 47 | EventStructure | 22347 | yes | WRITE |
| 53 | FlatSequenceFrame | 16367 | yes | READ |
| 53 | FlatSequenceFrame | 10824 | yes | WRITE |
| 55 | CaseStructure | 11611 | yes | READ |
| 56 | CaseStructure | 8718 | yes | READ |
| 57 | CaseStructure | 19200 | yes | WRITE |
| 59 | CaseStructure | 22168 | yes | WRITE |
| 59 | CaseStructure | 22213 | yes | WRITE |
| 59 | CaseStructure | 11139 | yes | WRITE |
| 59 | CaseStructure | 28073 | yes | WRITE |
| 61 | CaseStructure | 20548 | wired ref | WRITE, WRITE, WRITE |
| 61 | CaseStructure | 21986 | yes | READ |
| 61 | CaseStructure | 2320 | yes | READ |
| 61 | CaseStructure | 21600 | wired ref | WRITE |
| 61 | CaseStructure | 21936 | yes | READ |
| 64 | CaseStructure | 21676 | yes | READ |
| 66 | CaseStructure | 21770 | yes | WRITE |
| 66 | CaseStructure | 21793 | yes | WRITE |
| 67 | CaseStructure | 21892 | yes | WRITE |
| 69 | CaseStructure | 20859 | yes | WRITE |
| 69 | CaseStructure | 21023 | yes | WRITE |
| 70 | CaseStructure | 9907 | yes | READ |
| 82 | CaseStructure | 4401 | yes | WRITE |
| 84 | CaseStructure | 12284 | yes | WRITE |
| 86 | FlatSequenceFrame | 32191 | yes | WRITE |
| 87 | FlatSequenceFrame | 13366 | yes | WRITE |
| 87 | FlatSequenceFrame | 27926 | yes | WRITE |
| 97 | FlatSequenceFrame | 30445 | yes | READ |
| 97 | FlatSequenceFrame | 30471 | yes | READ |
| 97 | FlatSequenceFrame | 30512 | wired ref | WRITE, WRITE |
| 99 | WhileLoop | 1565 | yes | WRITE |
| 100 | FlatSequenceFrame | 17410 | wired ref | WRITE |
| 100 | FlatSequenceFrame | 4276 | yes | READ |
| 104 | FlatSequenceFrame | 19243 | yes | WRITE |
| 108 | FlatSequenceFrame | 18934 | yes | WRITE |
| 111 | FlatSequenceFrame | 30933 | yes | READ |
| 112 | FlatSequenceFrame | 18593 | yes | WRITE |
| 112 | FlatSequenceFrame | 18622 | yes | WRITE |
| 116 | FlatSequenceFrame | 42899 | yes | WRITE |
| 122 | FlatSequenceFrame | 17995 | yes | WRITE |
| 126 | FlatSequenceFrame | 17680 | yes | WRITE |
| 129 | FlatSequenceFrame | 7462 | yes | READ |
| 130 | FlatSequenceFrame | 17330 | yes | WRITE |
| 130 | FlatSequenceFrame | 17358 | yes | WRITE |
| 144 | CaseStructure | 30688 | yes | WRITE |
| 146 | FlatSequenceFrame | 20054 | yes | WRITE |
| 148 | FlatSequenceFrame | 25524 | yes | WRITE |
| 149 | ForLoop | 21590 | wired ref | READ |
| 153 | Sequence | 22351 | yes | READ |
| 157 | Sequence | 27951 | yes | WRITE |

Globals: the seven sites of `Global motor pos.vi` reappear with the same direction as `globals_direction_main` (all agree).

_Generated 2026-09-14 12:46 by tools/bench/analyse_nodeterms_main.py._

<!-- locals-section:end -->

## Control references — how the "bare-terminal" objects are actually used (measured 2026-09-14 14:5x)

A node-class census (`report_all(main, "Node")`, 626 nodes) shows **21 `ControlReferenceConstant` nodes**: single-terminal
source nodes named after their panel object, invisible to the terminal-wiring read because the object's own terminal
stays bare. Every one of them feeds a **subVI's reference input** — the subVIs drive the main panel through
references (property nodes inside them run on the UI thread: the `Value` nodes found in `ASI_adjust focus-subvi.vi`).

| diagram | panel object (bare?) | reference goes to |
|---:|---|---|
| 16 (startup frame) | `- Inc (PgDn)`, `+ Inc (PgUp)`, `Focus Step (F1)`, `continue tracking`, `Image` — all bare | `check N bead pos v3-kimlab.vi` (`-Inc/+Inc/Focus inc reference`, `Continue tracking`, `Image reference`) |
| 20 (motor loop) | `Trans Pos (mm)`, **`Send`**, `Rot pos (deg)`, `HOME`, `Send to Trans`, **`Rot step (turns)`**, `Trans Step (mm)`, `Trans Speed (mm/s)`, **`Stop Trans`** | `Motor control v5_No Recording.vi` (`tran/rot display ref`, `send to rot/trans ref`, `Home ref`, `change of … value ref`, `Stop one-way`) |
| 43 (frame loop) | **`File # Saved`**; `Focus Step (F1)`, `- Inc`, `+ Inc` | `save trace.vi` (`saved file refnum`); `ASI_adjust focus-subvi.vi` (`Focus inc / -Inc / +Inc reference`) |
| 99 (display loop) | `- Inc`, `+ Inc`, `Focus Step (F1)` | `ASI_adjust focus-subvi.vi` (second call site) |

So **9 of the 10 bare-terminal objects are in use** through references (and `File # Saved` also through a local).
**`Rot \nSpeed` (#73) is the only panel object with no terminal wire, no local and no control reference** — but it is
**NOT legacy (measured 14:5x, last section):** two implicit `Value` READs, on diagrams 32 and 111 (Flat-Sequence frames
that also hold `Rot Step (deg)` reads and `SetCommand.vi` calls — the Autonics rotor driver), i.e. it is the speed sent
to the rotor with every rotation command. Nothing on the panel is unattributed any more. Two design facts for the restructuring: the motor loop subVI and the
focus subVI *write the main panel through references* (UI-thread work inside subVIs, see docs/restructure-plan-4.6.md
stage 1), and `ASI_adjust focus-subvi.vi` — non-reentrant by design — is called from both the frame loop (43) and the
display loop (99) with the same three button references.

## Implicit `Value` property nodes → panel objects — MEASURED 2026-09-14 (`OpNodeLabels_v0`, 88/88)

Source `tools/bench/main_vi_node_labels.json` (`test_opnodelabels.py` T3: every one of the 88 implicit `Value` nodes returned a non-empty label that is a panel label; direction from the `Value` terminal's `Is Source?` in the terminal sweep). An implicit property node's header is its `Node.Label` (peer + LabVIEW Wiki), read headless with the panel closed — the never-displayed caveat did not bite. **This closes the 'bound object not readable' gap.**

| panel object | kind | terminal wired | implicit `Value` READ | WRITE | diagrams |
|---|---|---|---:|---:|---|
| `CycleSchedule` | control | yes | 2 | 2 | 43, 46, 47 |
| `Focus Pos (Cal)` | indicator | yes | 1 | 3 | 87, 146, 148, 153 |
| `Reached clamp` | indicator | yes | 2 | 2 | 61, 66, 67 |
| `Start Moving?` | indicator | yes | 1 | 3 | 59, 61, 66, 69 |
| `# of Auto-Reset` | indicator | yes | 2 | 1 | 1, 43, 70 |
| `+ Cal Zero` | control | yes | 1 | 2 | 21, 41, 126 |
| `- Cal Zero` | control | yes | 1 | 2 | 21, 37, 122 |
| `1 L-Turn` | control | yes | 1 | 2 | 21, 25, 104 |
| `1 R-Turn` | control | yes | 1 | 2 | 21, 29, 108 |
| `Rot Step (deg) ` | control | yes | 1 | 2 | 32, 33, 112 |
| `Send to Rot` | control | yes | 1 | 2 | 21, 33, 112 |
| `Start Cycles` | control | yes | 1 | 2 | 18, 43, 59 |
| `SubCycle` | indicator | yes | 1 | 2 | 43, 59, 69 |
| `Cal Zero` | indicator | yes | 2 | 0 | 21, 100 |
| `Count` | control | yes | 0 | 2 | 86, 144 |
| `Lc` | control | yes | 1 | 1 | 53, 55 |
| `Lost Frame Message` | indicator | yes | 0 | 2 | 1, 84 |
| `Mag Position` | indicator | yes | 2 | 0 | 18, 43 |
| `Rot 
Speed` | control | **no** | 2 | 0 | 32, 111 |
| `Rot pos (deg)` | indicator | yes | 1 | 1 | 43, 116 |
| `Send to Trans` | control | yes | 1 | 1 | 20, 130 |
| `Switch` | control | yes | 0 | 2 | 57, 59 |
| `Trans Pos (mm)` | indicator | yes | 1 | 1 | 5, 43 |
| `Trans Speed (mm/s)` | control | yes | 2 | 0 | 5, 129 |
| `TurnOff` | indicator | yes | 1 | 1 | 18, 20 |
| `continue tracking` | control | **no** | 0 | 2 | 9, 17 |
| `Auto-reset zero` | control | yes | 0 | 1 | 1 |
| `CamSessionOut` | indicator | yes | 1 | 0 | 16 |
| `Cycle Start Time` | indicator | yes | 1 | 0 | 56 |
| `Exp Baseline` | control | yes | 1 | 0 | 53 |
| `Fix to a Certain Pattern` | control | yes | 0 | 1 | 43 |
| `Focus Pos (Start)` | control | yes | 0 | 1 | 87 |
| `Focus Pos (Track)` | indicator | yes | 0 | 1 | 99 |
| `Frame rate` | control | yes | 1 | 0 | 43 |
| `Height` | indicator | yes | 1 | 0 | 97 |
| `IMAQimage` | indicator | yes | 1 | 0 | 16 |
| `Initial Time at Start` | indicator | yes | 1 | 0 | 64 |
| `Missing Frames?` | indicator | yes | 0 | 1 | 157 |
| `NumCol` | control | yes | 0 | 1 | 47 |
| `Reset Tracking` | control | yes | 0 | 1 | 82 |
| `RotationVISA` | indicator | yes | 1 | 0 | 9 |
| `Send` | control | **no** | 1 | 0 | 20 |
| `Trans Step (mm)` | control | yes | 0 | 1 | 130 |
| `Width` | indicator | yes | 1 | 0 | 97 |
| `min value` | indicator | yes | 1 | 0 | 43 |

45 distinct panel objects are reached by implicit `Value` nodes (40 READ / 48 WRITE rows).

**Bare-terminal objects now attributed through an implicit `Value` node:** `continue tracking`, `Send`, `Rot 
Speed`.  
**Bare-terminal objects still without a `Value` node** (control reference / event registration / legacy): `Focus Step (F1)`, `+ Inc (PgUp)`, `- Inc (PgDn)`, `File # Saved`, `Image`, `Rot step (turns)`, `Stop Trans`.
