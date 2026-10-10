---
name: consider-gemini-vision-executor-for-gui-loop
description: "The user wants Gemini wired into the terminal as a low-latency GUI executor (Claude plans, Gemini clicks); the bridge is built as tools/gemini_executor.py and needs a GEMINI_API_KEY the user supplies"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 72babae7-a0eb-4591-80eb-3f88511dbec4
  modified: 2026-08-26T05:35:20.411Z
type: decision
status: in-force
date: 2026-08-26
source: memory/consider_gemini_vision_executor_for_gui_loop.md
---

# Gemini as the GUI "executor", Claude as the planner — built, key pending

On 2026-08-26 the user relayed a proposal and then confirmed it: *"I need to connect Gemini with the
terminal too."* Keep Claude for planning and LabVIEW code judgement; hand **screen recognition and the
next one-or-two GUI actions** to a low-latency vision model — `gemini-3.5-flash-lite` by default,
escalating to `gemini-3.7-flash` when recognition falls short. Google documents both as computer-use
models supporting desktop screenshots and coordinate-based mouse control
(<https://ai.google.dev/gemini-api/docs/computer-use>).

**What now exists:** `tools/gemini_executor.py` in the V6 project, documented in
`GEMINI_EXECUTOR.md`. Design decisions that matter for anyone extending it:

- Gemini never touches the machine directly; every proposed action is translated into a
  `tools/lv_gui.ps1` call, so it inherits the window-rect coordinate law and the deterministic
  `probe`/`wire` mechanics rather than re-learning them.
- Gemini's coordinates are **normalised 0..999 over the image it was shown**, so the executor
  captures **one LabVIEW window** (`shotwin`, which prints the rect) and denormalises against that
  rect — never the full screen, which would recreate the wrong-window misclicks seen in benchmarks.
- Hard safety gates independent of model: refuses protected window titles (the original VIs),
  stops on Gemini's `safety_decision: require_confirmation` rather than auto-acknowledging, allow-lists
  keys (no Ctrl+S, no Alt+F4, no File menu), caps steps, logs every action.
- Smoke-tested **without a key**: capture → denormalise verified, protected-window refusal verified.
  The model loop has **not** run — it needs `GEMINI_API_KEY`, which only the user can supply and
  which must be set per session, never written into the project.

**The user's boundary, which stands regardless of model:** acquisition start on the real MT rig,
magnet moves, force settings, and data overwrites remain human-confirmed; first comparisons run on
scratch/offline VIs only.

**The user's validation plan:** an A/B on the same ten LabVIEW tasks — (1) current Claude,
(2) Claude planning + Flash-Lite executing, (3) 3.7 Flash alone — comparing total time, model wait,
click count, misclicks, human interventions. Make (1) **Claude + the existing composite tools**, not
raw screenshot-and-click: this project's measured bottleneck was round-trips, and `probe`+`wire` cut a
40-call task to 2, so a Gemini executor should be judged against that, and is most likely to earn its
place on the residual "small target not found" failures.
