---
name: experimental-load-beads-and-frame-rate
description: "The user's 2026-09-25 statement of the real experimental load — typically 8 beads, sometimes 15; frame loss already occurs intermittently at 90 Hz and grows at 150 Hz; they want the maximum frame rate possible, and the SP-5000M camera can go faster with a reduced ROI — so benchmarks must use this load, not 1–6 beads for 35 s"
metadata:
  node_type: memory
  pinned: false
  originSessionId: 1e5293f3-09a7-4b72-9393-fcba8dd55703
  modified: 2026-09-25T00:34:59.603Z
type: decision
status: in-force
date: 2026-09-25
source: memory/experimental_load_beads_and_frame_rate.md
---

# Experimental load: 8 beads (up to 15) at the maximum frame rate (user, 2026-09-25)

Cycle 77 measured real runs at 1/3/6 beads for 35 s and found only 2–11 lost frames of ~3,075 in both the original
and the split VI, and asked the user what a real experiment looks like. The answer:

> "보통 8개, 그러나 경우에 따라서는 15개도 봄. 그리고 무엇보다 현재 90Hz에서도 간간히 프레임 로스가 나오는데 150Hz로
> 처리할 경우 프레임 로스가 더 크게 잡힘. 가능하다면 최대의 프레임으로 실험하길 원함. 특히 sp-5000M의 경우 ROI를
> 축소하면 프레임 레이트 더 올릴 수도 있음"

## How I apply it

- A frame-loss benchmark that shows "no gain" at 1–6 beads for 35 s says nothing; the comparison that matters is
  8 and 15 beads, at 90 Hz and 150 Hz, runs of minutes, and at the highest rate a reduced SP-5000M ROI allows.
- The target is not "90 Hz without loss" but the maximum sustainable frame rate at 8–15 beads; the seven-loop split
  is judged by how far it raises that ceiling (goal map R4 / M10).
- ROI reduction is a legitimate lever the user wants used, not a test artefact.
