---
name: uitars-local-grounder-chosen
description: "The user chose UI-TARS-1.5-7B (local, free, via Ollama) as the GUI grounding model over Gemini; it is installed, calibrated, and works on LabVIEW terminals only with a two-stage zoom pass"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 72babae7-a0eb-4591-80eb-3f88511dbec4
  modified: 2026-08-28T13:45:42.457Z
type: decision
status: in-force
date: 2026-08-28
source: memory/uitars_local_grounder_chosen.md
---

# UI-TARS is the chosen GUI grounder — local, free, and it works with a zoom pass

On 2026-08-26 the user weighed Gemini (subscription they hold), Google's Antigravity IDE, and
UI-TARS, and decided: *"UI-TARS 적용해보자. 구독 필요없이 완전 로컬로 작용 가능한 것 같은데"* — try
UI-TARS, since it runs fully locally with no subscription. That preference for a **free, local,
GUI-specialised** model over a hosted general one is the standing choice; the Gemini executor
remains built but idle pending an API key the user has not provided.

What now exists on the rig: **UI-TARS-1.5-7B** (Apache-2.0, Qwen2.5-VL based) at Q4_K_M with its
`mmproj` vision projector, served by **Ollama 0.32.15** on the RTX 2060 (6 GB), wrapped by
`tools/uitars_grounder.py` in the V6 project. It answers "where is X on this LabVIEW window?" with a
screen coordinate for `lv_gui.ps1`; Claude keeps all judgement, and the grounder only replaces the
crop-and-squint step. Roughly 8 s per query once warm.

Three things were learned the hard way and should not be re-learned:

1. **The community Ollama tags for this model are text-only** — no vision projector, useless for
   GUI. The working source was the `mradermacher/UI-TARS-1.5-7B-GGUF` repo, which ships `mmproj`
   files; a two-`FROM` Modelfile imported cleanly on Ollama 0.32.15.
2. **Ollama does not apply Qwen's published `smart_resize`; it upscales small windows.** A 1000×700
   capture was fed to the model as ~1087×761, producing a systematic +8–10 % coordinate bias. The
   fix is self-calibrating: derive the seen dimensions from Ollama's image-token count
   (`tokens × 28²` pixels, aspect preserved) on every call.
3. **Small targets need a two-stage zoom.** A single 1× pass missed a 5 px For Loop `N` terminal by
   ~60 px; re-grounding on a 3× crop around the coarse guess landed within 3 px (and the Run arrow
   within 1 px). Zoom is the default in the grounder.

Treat the grounder as a fast first guess that finds the object; confirm the exact pixel with the
colour `probe` before wiring anything that matters. A user-supplied Korean setup guide
(simsimit00.tistory.com/582) independently recommends this planner/executor split with allow-listed
actions and single-monitor operation.
