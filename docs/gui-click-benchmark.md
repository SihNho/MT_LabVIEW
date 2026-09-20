---
type: reference
status: current
date: 2026-09-04
tags: [docs, benchmark, gui]
---

# GUI click optimization — benchmark design (2026-09-04, user directive: clicking first)

Goal: make LabVIEW GUI clicking **fast, exact and cheap**, then build the toolkit with it. So the
first benchmark compares **clicking methods**, not models. Models come later, on the winner.

## Baseline (this session, Claude-reads-screenshot method)

178 gated actions; median 18 s between consecutive actions (mean 30 s); 3.4 screenshots per
action; failure modes: focus Alt-tap → menu mode (fixed in lv_gui 2026-09-04), submenus opening
only on real cursor motion, wrong palette row, foreground stolen by another app, COM/GUI
contention hangs, Quick Drop broken.

## Methods under test

| id | how the click coordinate is obtained | Claude reads images? |
|---|---|---|
| M1 baseline | full screenshot → Claude reads → computes → `lv_gui click` | yes, every step |
| M2 grounder | `uitars_grounder.py` ("where is X") → coordinate → click | no (UI-TARS does) |
| M3 data | COM `report()` diagram position + viewport offset → coordinate → click | no |
| M4 macro | M3 wrapped as single verbs (`place`, `pick_method`, `change_to_write`, `create_control`, `menu`) with COM self-verification | no |

M3 needs the viewport offset. Two routes, both to be measured: (a) one-time anchor via Find-jump
(known node → its screen position from one screenshot), (b) an op that reads/writes the VI
property `Block Diagram Window:Origin` (not on COM; needs a VI-class Property Node inside an
op — the first tool the optimized clicker builds). With (b) the offset is pure data:
`screen = client_origin + (diagram_pos − BD_origin)`.

## Micro-ops (each COM-verifiable, each reset by `gscript.revert(target)` for identical trials)

| id | action | verification | accuracy metric |
|---|---|---|---|
| U1 move | drag a named node by (+100,+50) | `report()` position delta | px error |
| U2 place | palette → primitive at target diagram coords | new uid appears; `report()` position | px error |
| U3 wire | terminal→terminal GUI wire (or terminal→existing wire branch) | Wire count / ExecState | — |
| U4 menu | Property Node item → *Change To Write* | ExecState 1→0 (required input appears) | — |
| U5 pick | Invoke Node method field → *Create Indicator* | run op → target ControlTerminal +1 | — |

Target: a scratch copy in claudeDev with a known layout (`FPTARGET_v0.vi` family); 3 trials per
(method × micro-op); LabVIEW restarted between METHODS, `revert` between TRIALS.

## Metrics per trial (recorded to `tools/bench/gui_results.jsonl`)

wall seconds · gated actions · screenshots taken · screenshots **read by Claude** · retries ·
verified success · px error (U1/U2) · parent tokens for the trial (from the transcript usage
records). Lead with **seconds and Claude-read screenshots per verified success**.

## Fixes applied before measuring (no judgement needed)

- `lv_gui focus` now taps Esc after the Alt tap (menu-mode bug).
- Rule: submenus are opened by a hover sweep (`move` steps), never by arrow keys.
- Rule: click the Method/Property FIELD to open choosers; the right-click Select-Method submenu
  is unreliable.
- Layout discipline for every GUI session: BD window maximized, Context Help closed unless
  reading it, no other app window over the diagram (the Claude desktop window stole foreground
  twice today).

## Exit criterion

The winning method becomes the only clicker; its verbs go into `lv_gui.ps1`/`gscript.py` with
COM verification built in. Then the toolkit ops (keystone first) are built with it, and the
model/effort benchmark (`tools/bench/RUNBOOK.md`) runs on top.


## RESULT 1 — offline grounding bench (2026-09-04, 19 targets, "would the click land" rule)

| grounder | hit | median px | s/query | tokens/query | notes |
|---|---|---|---|---|---|
| Sonnet 5 | 19/19 | 1.0 | 3.7 (batched) | ~5.7k marginal; **~68k fixed per fresh subagent** | answers in full-res image coords |
| Opus 5 | 19/19 | 1.0 | 4.4 (batched) | ~5.3k marginal | menu answers at text centre (x offset, still in row) |
| GPT via `codex exec -i` | 17/19 | 2.0 | 5.9 | ~6k (subscription) | missed 2 diagram nodes (18 px, 44 px); 100% on menu/palette/dialog |
| UI-TARS-1.5-7B (2-pass) | 16/19 | 3.2 | 22.5 | 0 | missed a dialog text box (146 px) and 2 nodes (417 px, 15 px) |
| Haiku 4.5 | 0/19 raw, 10/19 calibrated | 298 / 13 | 4.4 | ~4k | answers in a ~0.76x downscaled space; unfit even after calibration |

Ground truth: click points verified this session (menu/palette/dialog) + COM positions (nodes);
x-slack per kind (menu 80, dialog 30, palette 18). NOT covered yet: 5 px terminals (need live
LabVIEW + probe truth).

**Decisions taken from it**
1. Executor vision = **Sonnet 5**, in a long-lived executor session (one spawn per batch, many
   reads inside) — a fresh spawn costs ~60k tokens before the first image.
2. UI-TARS stays installed for zero-cost offline/bulk pointing only; 6x slower and misses ~16%.
3. GPT (codex) is the cheap single-shot fallback when no executor session is open (no fixed
   cost, 6 s), not for diagram nodes.
4. Haiku is out for any pixel work.
5. Diagram objects should not be grounded by vision at all — M3 arithmetic from COM
   positions; vision is for menus/palettes/dialogs, where every grounder except Haiku is ~100%.

### UI-TARS timing addendum (2026-09-04)
- The 22.5 s/query in RESULT 1 was cold-start + contention (bench ran concurrently with codex
  and three Claude subagents; first query paid a ~30 s 6 GB load). **Warm, sequential, default
  settings: 4.7 s/query**, same 84% hit rate. Warm two-pass compute is ~2.3 s + ~1.6 s.
- `ollama ps` shows the model split 33-37% CPU / 63-67% GPU on the 6 GB RTX 2060: weights
  (Q4_K_M + vision projector, ~6 GB) do not fit. Fitting it fully needs a smaller quant
  (Q3_K_M/IQ4_XS, a ~4 GB download) - not attempted.
- Per-request `num_ctx` experiments FAILED: 2048 rejects 1920x1080 images (HTTP 400);
  4096 + keep_alive -1 made queries ~180 s each (cause undiagnosed, 35 min lost). Reverted to
  defaults. Lesson: benchmark one variable at a time and stop after the first bad number.
- Verdict unchanged: Sonnet 5 (19/19, ~4 s/query in-batch) beats UI-TARS (16/19, 4.7 s) on
  precision at similar speed; UI-TARS's only edge is zero token cost.


## RESULT 2 — live click bench, M3 arithmetic vs Sonnet vision (2026-09-04, GUIBENCH_v0.vi)

| method | op | pass | median s | actions | screenshots read | px |
|---|---|---|---|---|---|---|
| M3 (COM coords + calibrated offset) | U1 move | 2/3 after header-grab fix (0/3 with centre grab) | 2.0 | 1 | 0 | 0.0 |
| M3 | U2 place (palette) | 3/3 | 8.5 | 5 | 0 | 6.1 |
| M3 | U4 menu (Change To Write) | 3/3 | 3.4 | 2 | 0 | — |
| Sonnet vision (executor subagent) | U1 move | 3/3 | 9.7 (57 first) | 1 | 1–2 | 0.0 |
| Sonnet vision | U2 place | 3/3 | 23.9 (44 first) | 5 | 2–3 | 6.1 |
| Sonnet vision | U4 menu | 3/3 | 10.5 (29 first) | 2 | 1–3 | — |

Sonnet executor session total: 157k tokens, 79 tool uses, 569 s for 9 trials (~17.5k tokens and
~63 s per trial including reverts/verification). M3 total tokens: 0 (script), one calibration
screenshot for the whole session.

Findings
- **M3 is 3–5x faster and costs nothing**, with identical accuracy where both hit (U2 lands on
  the same pixel, 6 px from the intended centre because the palette drops the icon centred).
- M3's only failures were tooling, not coordinates: dragging an Invoke Node by its centre opens
  the method chooser (grab the header row); the first mouse-down after window activation can be
  swallowed (a pre-click on empty canvas, added to prep()).
- Vision's cost is round trips: every trial re-reads the screen (1–3 shots), and the first trial
  of each op pays orientation (29–57 s). It is the right fallback for menus/dialogs whose
  geometry is unknown, not the default.
- Menu geometry is stable relative to the click point (Change To Write at (+68,+187)); palette
  geometry is stable for a given right-click point. Both can be tables, not vision.

Decisions
1. Clicker = **M3 verbs** in `lv_gui.ps1`/`gscript.py`: `place(kind, at)`, `move(uid, dx, dy)`,
   `menu(uid, item)`, `pick_method/property(uid, name)`, `create_control(uid, terminal)` —
   coordinates from `report()` + one calibration per window rect, COM verification built in.
2. Vision (Sonnet, in the long-lived executor session) only when a menu/dialog/palette item is
   not in the offset table; the executor then records the offset so it is arithmetic next time.
3. Next: build the keystone op with these verbs (zero manual clicks expected), then the model
   benchmark on top.
