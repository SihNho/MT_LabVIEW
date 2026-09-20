---
type: narrative
status: historical
date: 2026-09-05
tags: [archive]
---

# M3 clicker — coordinates from data, verbs with self-verification (spec, 2026-09-05)

Purpose: the GUI-click layer of the lab toolkit. Every click target is computed from COM data
(object positions from `gscript.report`) plus one calibrated viewport offset; vision (an
opus-low executor cell) is the fallback for what data cannot give. Each verb verifies its own
effect over COM and returns a structured result. No screenshots on the happy path.

Module: `tools/lvclick.py` (Python API) — built on `tools/gscript.py` (COM) and `tools/lv_gui.ps1`
(input + window queries). Benchmark ancestor: `tools/bench/gui_bench.py` (M3, 2026-09-04).

## 1. Viewport model

- A block-diagram window with rect (L, T, R, B) at scroll origin (0,0) maps diagram (x, y) to
  screen (x + L + DX, y + T + DY). Measured on LabVIEW 2026 / 1920x1080 / default toolbar:
  DX = 11, DY = 37 (window rect (0,4)-(1400,904) gave screen = diagram + (11,41)).
- `calibrate(bd_title)` reads the rect (`lv_gui -Action shotwin` prints it) and returns
  `Viewport(L, T, DX, DY)`. It **validates** by probing pixels at a known object's computed
  position (`probe_box`) — a node body is never canvas-white — and refuses to hand out a
  viewport that fails the probe (scrolled window, other DPI, hidden toolbar).
- Scroll is not modelled: verbs require scroll origin (0,0); `calibrate` detects a scrolled
  window by the probe failing and reports it.

## 2. Node geometry

`report(target, cls)` gives top-left positions only. `node_box(vp, uid)` finds the extent by
pixel probing rightwards and downwards from the top-left until canvas colour returns (lv_gui
`probe` scans a 1-px line and reports colour runs). Header-row grab point = (x + w/2, y + 8):
grabbing the centre of an Invoke/Property node opens its method chooser instead of dragging.

## 3. Verbs (all return dict: ok, what was measured, px_error where applicable)

| verb | acts | verifies |
|---|---|---|
| `move_node(target, uid, dx, dy)` | drag header row by (dx, dy) | report(): position delta within 6 px |
| `place_from_palette(target, item, x, y)` | right-click canvas at a registered point; walk the registered palette geometry; click at (x, y) | exactly one new object of the item's class within 12 px (uid diff, not position matching) |
| `node_menu(target, uid, row, item, verify)` | right-click row centre; click item at registered offset | caller-supplied verifier (default: ExecState change) |
| `dialog_button(title, button)` | click a registered button offset inside the dialog rect | window list before/after |
| `focus_bd(title)` | focus + one canvas click (absorbs the swallowed first mouse-down; clears menu mode) | window in front |

Every state-changing action goes through `lv_gui -Exception Approved -Evidence <who/when>` and is
logged in `tools/gui_actions.log` (unchanged gate).

## 4. Registries (data, not code) — `docs/gui-geometry.json`

- `palette`: for a right-click point P, item path → list of screen offsets relative to P
  (measured: P=(1150,500): Array (+160,−265) clicked twice, Index Array (+369,−200)).
- `menus`: (node class, row) → item → offset from the right-click point
  (measured: Property node 'Position' row → "Change To Write" (+68,+187)).
- `dialogs`: title → button → offset from the dialog rect's top-left
  (measured: Find → Cancel (+484,+466) at rect (474,250)).
Unknown entries make the verb return `{"ok": False, "reason": "no geometry for ..."}` — the
caller escalates to the vision executor and, on success, records the measured offset back into
the registry (the registry grows by use).

## 5. Verification plan (batch, GUIBENCH_v0.vi, revert before each trial)

3 trials per verb: move_node (Invoke uid 538, +100,+50), place_from_palette ("Array/Index Array"
at (1100,600)), node_menu (PN uid 610 row 0 "Change To Write"), dialog_button ("Find", "Cancel"
after Ctrl+F). Acceptance: ≥ 8/9 for the three M3-benchmarked verbs (bench: 8/9 → after the
pre-click fix 9/9), 3/3 dialog. Same JSON line format as gui_results.jsonl, method "M3v1".

## 6. Known limits

- One viewport offset per window layout; a moved/resized/scrolled BD needs re-calibration.
- Palette/menu offsets are layout facts of LabVIEW 2026 at this DPI; other machines must
  re-measure (the registry file is per-machine).
- Objects inside structures report positions in a shifted space (see gscript.new_since) —
  verbs take a `diagram_index` and refuse nested owners until measured.

## 7. After peer review (codex, 2026-09-05, archive/peer/2026-09-05-m3-clicker-spec-attack.md)

Accepted and applied:
- **Viewport = two-object calibration.** `calibrate` reads two registered objects' COM positions
  and their probed screen positions; scale must be exactly 1 and both offsets equal, else refuse
  (catches zoom, scroll, DPI, hidden toolbar). Send Ctrl+0 (actual size) is NOT automated —
  a scaled diagram is reported, not corrected.
- **No extent probing.** `GObject.Bounds` exists (read-only, remote) but OpReport_v3 does not
  export it; until the reporter is extended, per-class sizes live in the registry and the grab
  point is validated by the header colour at that pixel (Invoke/Property headers are distinct
  solid colours), not by scanning to canvas.
- **Palette offsets are relative to the detected popup rect** (`lv_gui -Action toplevel` lists
  the LabVIEW process's visible top-level windows with class and rect; the palette is the new
  untitled one). Edge flipping and pinned palettes change the rect, not the item offsets inside
  it. Placement by scripting (New VI Object / donor copy — the keystone op) is the primary path;
  this verb is the fallback.
- **Menu verbs are registered triples** (node class, item, verifier). No generic "ExecState
  changed" verifier: `Change To Write` on a read-only Property row is verified by ExecState 1→0
  because that is its known effect on that row; other items need their own verifier.
- **Dialog buttons**: the dialog rect's SIZE must match the registered size (±3 px) before the
  click; a resized/rewrapped dialog refuses and escalates.
Rejected for now (recorded): reading menu text/accessible IDs (needs UI Automation; queued),
per-state drag exemplars (vision fallback covers unknown classes).

## 8. Verification notes (2026-09-05)

- First batch: calibrate failed because `open_panel` raised the FRONT PANEL over the diagram and
  the probe read panel grey → calibrate now focuses the BD and requires it to be the top window.
- Second batch: COM Run hang in calibrate → discriminating test H5: `OpenFrontPanel(activate)` +
  lv_gui focus (Alt tap) ⇒ next COM Run blocks until a canvas click (4/4 predictions). Batch and
  verify_op now open the panel only when it is not already open.
