---
type: reference
status: current
date: 2026-08-26
tags: [docs]
---

# UI-TARS local grounder — setup, calibration, and what it is for

**Status 2026-08-26:** installed, running fully locally on the RTX 2060, coordinate contract
**calibrated empirically**. No subscription, no API key, no data leaves the machine.

## What it is

`tools/uitars_grounder.py` answers one question: **"where on this LabVIEW window is X?"** — and
returns a screen coordinate ready for `lv_gui.ps1`. It is deliberately *not* an autonomous agent:
Claude keeps all judgement; the grounder replaces only the crop-and-squint step that has been the
residual failure mode (5 px terminal stubs, top-edge terminals).

| role | who |
|---|---|
| planner | Claude — decides what to click |
| grounder | **UI-TARS-1.5-7B** (Q4_K_M, local via Ollama) — finds it |
| hands | `lv_gui.ps1` — the only thing that touches the mouse |

Why this model: ScreenSpot-Pro (GUI grounding) **61.6** vs OpenAI CUA **23.4**; Apache-2.0;
Qwen2.5-VL based; a Korean setup guide the user supplied independently recommends exactly this
planner/executor split with action allow-listing ([R14] in `REFERENCES.md`).

## Install (done)

- **Ollama 0.32.15** via winget (MIT).
- Weights: `mradermacher/UI-TARS-1.5-7B-GGUF` — `Q4_K_M` (4.7 GB) **plus** `mmproj-Q8_0` (0.8 GB).
  **The community Ollama tags `0000/ui-tars-1.5-7b*` are text-only (no projector) — do not use.**
- Imported with a two-`FROM` Modelfile (`models_import\Modelfile`). Ollama issue #17491 reported this
  hanging; on 0.32.15 it completed cleanly. `ollama show` confirms `vision` + `clip` projector.
- Official parser: `pip install ui-tars` (ByteDance).

## THE COORDINATE CONTRACT — read this before trusting any output

UI-TARS outputs **absolute pixel coordinates in the space of the image the model saw**. Two things
were verified the hard way:

1. **Ollama does NOT apply Qwen's published `smart_resize`.** It enforces its own pixel budget and
   **upscales small windows** — a 1000×700 capture was fed to the model as ~1087×761. Dividing by
   Qwen's formula left a systematic **+8–10 % bias (55–62 px)**. At 1400×900 the scale was ~1.0 and
   the bias vanished, which is what exposed it.
2. **The fix is self-calibrating:** Ollama returns `prompt_eval_count` on every call; subtract the
   text prompt's tokens (measured once, cached) to get **image tokens**; `seen_pixels = tokens × 28²`,
   aspect preserved. Map with `screen = rect.left + model_x × rect.w / seen_w`. No constants to
   guess, and it survives Ollama changing its preprocessing.

Calibration (`--calibrate` draws magenta markers at known positions and asks the model to find them):

| window | before fix | after fix |
|---|---|---|
| 1000×700 | 60 px mean, all +biased | **1–4 px** on 2/3 targets; one 31 px model miss |
| 1400×900 | 20 px | (scale ≈1, unaffected) |

Inference: **~1.6 s** per query once loaded (first call ~16 s).

## THE KEY RESULT — small targets need a ZOOM pass (now the default)

Real LabVIEW targets on a 1000×700 window, single pass at 1×:

| target | truth (probe) | UI-TARS 1× | error |
|---|---|---|---|
| For Loop `N` terminal (5 px) | (127,118) | (55,161) | ~60 px — **miss** |
| numeric constant `3` | (~87,118) | (55,227) | ~110 px — miss |
| Edit menu | (~58,41) | (88,40) | ~30 px |
| For Loop centre | — | (161,201) | plausible |

Same `N` terminal on a **3× crop** of the loop region: **(127,121) vs truth (127,118) → (0,+3) px.**

So small-target failure is a **resolution** problem, not a model problem. `uitars_grounder.py` now
does this automatically (`--zoom`, default ON): coarse pass on the whole window → crop a 300 px box
around the guess → upscale 3× → re-ground → map back. Cost ≈ 2 queries, ~8 s once the model is warm.

**Validated two-stage results** (same window, same three targets):

| target | truth | two-stage | error |
|---|---|---|---|
| `N` terminal (5 px) | (127,118) | **(124,119)** | 3 px ✔ |
| Run arrow | (~70,66) | **(71,66)** | 1 px ✔ |
| numeric constant `3` | (~87,118) | (67,119) | ~20 px x (hit its left edge), 1 px y |

Two of three at terminal-grade precision; the third is on the object but not centred. Still **verify
with `probe` before any wire that matters** — the grounder finds the object, `probe` finds the pixel.

## Usage

```powershell
$env:PATH = "$env:LOCALAPPDATA\Programs\Ollama;" + $env:PATH     # once per session
py tools\uitars_grounder.py --window "Untitled 9 Block Diagram" --target "the N terminal of the For Loop"
py tools\uitars_grounder.py --window "..." --target "..." --click     # ground AND click via lv_gui.ps1
py tools\uitars_grounder.py --window "..." --calibrate               # re-verify the contract
```

Always capture **one window** (`shotwin`); never the full screen — the protected-window refusal and
the wrong-window guarantee both depend on it.

## Honest limits

- Grounding is probabilistic. One of three synthetic markers was missed by 31 px even after the
  mapping fix. **Verify with `probe` before wiring anything that matters**; treat the grounder as a
  fast first guess that usually removes the crop-and-squint loop, not as ground truth.
- 6 GB VRAM forces Q4_K_M. Q8 would need CPU offload (64 GB RAM makes that possible but slow).
- Single monitor only (the model, and the setup guide, both assume it).

## References

[R11] UI-TARS · [R12] GGUF+mmproj · [R13] Ollama · [R14] setup guide — see `REFERENCES.md`.
