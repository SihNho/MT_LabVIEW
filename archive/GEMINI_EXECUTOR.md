---
type: narrative
status: historical
date: 2026-08-26
tags: [archive]
---

# Gemini GUI Executor — setup, protocol, and the A/B test

**Status 2026-08-26:** built and smoke-tested **without an API key**. The capture → denormalise →
`lv_gui.ps1` path is verified; the protected-window refusal is verified. **The model loop has not
run yet** — it needs `GEMINI_API_KEY`, which the user must supply (Google account, AI Studio).

## The idea (user's proposal)

Split GUI automation into two roles so each model does what it is fast at:

| role | model | does |
|---|---|---|
| planner | Claude | decides *what* to do; hands over one bounded sub-task |
| executor | `gemini-3.5-flash-lite` (default), `gemini-3.7-flash` on escalation | looks at the screen, performs the next one-or-two actions |
| hands | `tools/lv_gui.ps1` | the **only** thing that touches mouse/keyboard, for both |

Gemini never drives the machine directly. Every action it proposes is translated into a
`lv_gui.ps1` call, so it inherits the mechanics that were expensive to learn: window-rect
coordinate law, focus-before-click, deterministic `probe`/`wire`.

## Setup (one-time)

1. Get a key at <https://aistudio.google.com/apikey>.
2. Set it **for the session only** — never write it into a file in this project:
   ```powershell
   $env:GEMINI_API_KEY = "..."
   ```
3. The SDK is installed already: `google-genai 2.20.0` (Python 3.10, via `py`).

## Run

Always start with `--dry-run`; it prints every action Gemini *would* take, with denormalised screen
coordinates, without touching LabVIEW.

```powershell
py tools\gemini_executor.py --window "Untitled 9 Block Diagram" `
    --task "Place a numeric constant on empty canvas to the left of the For Loop" `
    --model gemini-3.5-flash-lite --max-steps 12 --dry-run
```

Drop `--dry-run` to execute. `--escalate 6` switches to `gemini-3.7-flash` after 6 steps.
Every run writes `tools/gemini_runs/<timestamp>/actions.jsonl` plus a screenshot per step — that
is the audit trail and the data source for the A/B comparison.

## Safety gates (in the code, independent of which model runs)

- Refuses to start unless a LabVIEW window with **exactly** the given title is open.
- Refuses any window whose title matches a **protected** pattern (`Min_Track N beads 4.5`,
  `3StateClamping`, `4ParallelLoop`, …). Verified: targeting the original 4.5 VI exits with
  `REFUSED` before any capture.
- Honors Gemini's `safety_decision: require_confirmation` by **stopping** (exit 3) — it never
  auto-acknowledges.
- Keyboard is allow-listed: no `Ctrl+S`, no `Alt+F4`, no File menu. `type` refuses text containing
  control sequences.
- `--max-steps` hard cap; 3 refused actions in a row aborts.
- **Unreachable through this tool by construction:** acquisition start, magnet moves, force
  settings, data overwrite, and the ASI piezo stage. Those stay human-confirmed on the real rig.

## Why the capture is a WINDOW, not the screen

Gemini returns coordinates normalised to **0..999 over the image it was shown**. We show it one
LabVIEW window (`shotwin`, which prints the rect) and denormalise against that rect:

```
screen_x = rect.left + x/1000 * rect.width
```

Verified: on a 1000×700 window at (0,0), `norm(999,999) → screen(999,699)`. Showing the full screen
would re-create exactly the wrong-window misclicks that cost several benchmark runs, and a smaller
image is a faster round-trip.

## The A/B test (do this before adopting it)

Same ten LabVIEW tasks, on scratch VIs only, three configurations:

1. **Claude + current composite tools** ← the honest baseline (NOT raw screenshot-and-click)
2. Claude planning + Flash-Lite executing
3. `gemini-3.7-flash` alone

Compare: **total time · model wait time · click count · misclicks · human interventions.**
`actions.jsonl` records wait time per step and every action, so 2 and 3 are measured for free;
config 1 is measured from tool-call counts as in `BENCHMARK_gui_control.md`.

**Expectation, stated in advance so it can be wrong:** this project's measured bottleneck was
round-trips and coordinate-frame errors, not per-click reasoning. `probe`+`wire` took a 40-call task
to 2 calls; no model swap approaches a 20× gain. So Gemini is most likely to help on the residual
"small target not found" failures (5 px terminal stubs, top-edge terminals), and least likely to
help where the loop is waiting on LabVIEW to render. If the A/B shows otherwise, update this file.

## What would make it unnecessary

Finishing `KernelBuilder_v1.vi`. Once diagram edits are one `Run` of a scripted driver, there is no
GUI loop left to accelerate. The executor is for the residual GUI work that scripting cannot reach.

## References

- Gemini Computer Use — <https://ai.google.dev/gemini-api/docs/computer-use> (model IDs, desktop
  action set, `interactions.create`, 0..999 normalisation, `safety_decision` contract)
- `google-genai` SDK, Apache-2.0 — <https://github.com/googleapis/python-genai>
- Google's reference agent, Apache-2.0, **browser-only** — <https://github.com/google/computer-use-preview>.
  Read for the loop shape; no code copied. The desktop executor here is original.
