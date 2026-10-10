---
name: display-policy-and-camera-panel-decisions
description: "User decisions 2026-09-14 - live display 10 Hz is enough but must be a runtime control; if live imaging ever costs a measurement frame, an external (non-LabVIEW) display is acceptable; a camera-settings panel at the VI's configuration stage is a later option"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 7b982769-ee4e-45be-8846-85edbec23e37
  modified: 2026-09-14T11:35:28.458Z
type: decision
status: in-force
date: 2026-09-14
source: memory/display_policy_and_camera_panel_decisions.md
---

# Live display: 10 Hz, adjustable, and never at the cost of a frame

On 2026-09-14 the user settled the display question that the measurements had left open (visible paint of the
image costs ~6.5 ms per update, so per-frame display at 150 Hz is impossible):

> "라이브 이미지는 10Hz도 충분히 좋은데, 나중에 컨트롤로 변경할 수 있으면 좋겠음. 다만, 라이브 이미징 때문에 한 프레임이라도
> 측정상 문제가 생긴다면 랩뷰가 아닌 다른 프로그램 통한 디스플레이로 보이는 것도 진지하게 생각중."

So, for the restructured VI:

- The display loop runs at **10 Hz by default**, and the rate must be a **front-panel control changeable at run time**,
  not a constant.
- The display path must be designed so it **cannot cost the acquisition/tracking path a single frame** (copy-on-demand
  into a bounded pool, `Last`-mode/lossy hand-off, its own loop). If it ever does, the user is prepared to move the
  live view to a separate non-LabVIEW program — so never argue for keeping the display inside LabVIEW at the expense of
  measurement integrity.

# Priorities after the inventory

The same message ordered the work: **do the restructuring first** ("재구성이 중요하겠는데 이거 진행하도록"), then the
remaining items. As a later, explicitly optional item ("급하진 않고 옵션"): a **camera-settings panel** (frame rate,
exposure time, and the other values NI MAX can set) that can be opened from the VI's configuration stage. Keep it in the
plan as an option, not as part of the restructuring's acceptance.
