---
name: unattended-runs-drive-bead-picking-by-gui
description: "The user's 2026-09-17 decision — until the rig is reassembled, test runs of the assembled VI must run WITHOUT the user (overnight, dozens of repeats), so the bead-picking stage is driven by scripted mouse clicks + button + save-path entry (their option 1), not by a .cal-loading test VI (option 2, rejected); tracking errors without beads are acceptable because the purpose is device-communication and frame checks; GPU path first, CPU afterwards"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 97b1695e-68c2-4985-8cac-1ca3097b3b15
  modified: 2026-09-16T16:27:33.188Z
type: decision
status: in-force
date: 2026-09-16
source: memory/unattended_runs_drive_bead_picking_by_gui.md
---

# Until the rig is reassembled, the harness runs without me — so it clicks the beads itself

On 2026-09-17, after I asked whether the live tests could be supervised, the user said no:

> *"리그 조립 전까지는 내가 없는 환경에서 돌리기를 기대함. 애초에 트러블 슈팅이 진행된다고 하면 동일 프로세스를
> 몇십번이고 돌려야 할테니 내가 일일히 체크 하는 것은 어렵겠고 또한, 내가 실제 사용하지 않는 밤 시간동안 하네스
> 루프 돌리며 개발 하기를 기대함."*

And chose, between the two ways to get past the bead-picking loop:

> 1) 직접 마우스 움직여서 디스플레이 상에 클릭 이후 버튼 누르기 → 저장 위치 및 저장 이름 쓰기.
> 2) 테스트 코딩 용도로 전반부를 기존 .cal 데이터 불러오는 방식으로 대체하는 vi 작성 → 이후 메인 vi로 최종 수정
> **"이 방식 중 나는 1번이 더 괜찮다고 봄."**

Plus: *"Bead가 없는 상황에서 트래킹 에러가 분명히 생기겠으나, 디바이스 통신 및 프레임 체크 용도로는 무리 없을
듯"* and *"GPU 먼저 작성, 이후 CPU는 부가적으로 작성하는것."*

## What this fixes

- **Unattended is the requirement, not a convenience.** A test that needs a human at the panel is not a test
  this project can run. Design every run of the assembled VI to start, pass the picking stage, run, stop and
  restart with nobody present; the harness loop runs overnight.
- **The picking stage is driven by GUI automation** — mouse clicks on the live image display (first click =
  reference bead, later clicks = magnetic beads), the "done" button, then typing the save location and file
  name. This is the user's explicit choice, so it is an **approved GUI use** under the "GUI only where
  scripting is unreachable" rule: use `tools/lv_gui.ps1` with `-Exception Approved -Evidence "user
  2026-09-17 bead-pick option 1"`. Still verify targets by COM/screenshot as the GUI skill requires, and
  prefer setting a control by VI Server when a click is only a proxy for a control value.
- **No `.cal`-loading substitute VI.** Option 2 was rejected; the copy keeps the original's stages 0–3 as they
  are, and the calibration runs on whatever the camera sees.
- **Tracking errors without beads are expected and acceptable.** With the rig apart there are no beads; these
  runs check device communication, frame accounting, stop/restart and file writing — not tracking quality.
  Do not treat lost-bead or garbage-position output in these runs as a failure.
- **GPU tracking path first**, CPU-parallel afterwards as the additional deliverable (re-affirmed).
