---
name: main-vi-run-sequence-needs-bead-clicks
description: "The user's description (2026-09-17) of how the main VI actually runs — panel parameters, configure, a bead-picking WHILE loop that waits for mouse clicks on the camera image, a button that ends it and runs bead-profile (PSF-like) calibration, then the experiment loop — so an unattended test run stalls in the first loop unless beads are clicked and the button pressed"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 97b1695e-68c2-4985-8cac-1ca3097b3b15
  modified: 2026-09-16T16:02:47.092Z
type: decision
status: in-force
date: 2026-09-16
source: memory/main_vi_run_sequence_needs_bead_clicks.md
---

# The main VI cannot get to its experiment loop without mouse clicks and a button press

The user laid out the run sequence on 2026-09-17, in their words:

> 우선 시작 전에 프론트 패널의 파라미터들을 조정함 (Bead ROI 사이즈, bead calibration 관련 파라미터 등).
> 1) 연결 디바이스 컨피규어 및 기타 셋팅
> 2) while loop를 돌며 프론트패널 카메라 화면에서 내가 실험할 비드를 클릭하여 고름. [1: ref bead, else: magnetic bead]
> 3) 특정 버튼을 누르면 while loop 종료, 및 bead profile calibration. [유사 psf 추출]
> 4) 이후 while loop 재진입. 이 루프가 실험 루프임.
>
> 이 과정을 따라가다 보면 필연적으로 마우스 클릭이 필요함. 클릭이 없을 시 첫 번째 루프에서 멈춰버림.
> 만약 메인 vi 조립을 마치고 테스트 런을 돌려본다고 하면 타겟 비드 위에 클릭하고 버튼을 눌러줘야 함.

So the VI has **two while loops in sequence**, not one:

| stage | what happens | how it advances |
|---|---|---|
| 0 | front-panel parameters set by hand (bead ROI size, calibration parameters) | — |
| 1 | configure the connected devices, other setup | runs through |
| 2 | **bead-picking loop**: the live camera image is on the panel; the user clicks the beads to use — the **first click is the reference bead, every later click a magnetic bead** | **waits for mouse clicks** |
| 3 | a button ends loop 2 and runs **bead-profile calibration** (a PSF-like extraction per bead) | **waits for the button** |
| 4 | the **experiment loop** — the frame loop this project restructures (diagram 43) | runs until stopped |

## What follows for any assembled copy of the VI

- A test run that nobody is sitting at **stalls in loop 2**. "ExecState 1 and it runs" says nothing until beads
  have been picked and the button pressed.
- The calibration in step 3 needs **real beads in the image**. With the rig disassembled there are none, so a live
  no-bead run can only proceed if the calibration is *loaded* from a saved result or the picks are injected —
  the "bead-free initialisation" question already on the plan (Phase A10; `Done Picking Beads?` uid 11819;
  `Array of cal clusters`).
- Driving the picks by GUI clicks is the last resort (rule: GUI only where scripting is verified unreachable);
  the first question is which controls the clicks and the button land in, so `SetControlValue` can supply them.

This is the user's direct account of the instrument's workflow and overrides any inference about it from the
diagram.
