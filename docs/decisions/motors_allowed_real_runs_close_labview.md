---
name: motors-allowed-real-runs-close-labview
description: "The user's 2026-09-24 grants and rules — motor access is allowed until they say otherwise (reference + limits always verified), assembled main VIs are RUN for real as their acceptance test (recorded-frame replay only when needed), every cycle ends by closing LabVIEW so the camera stops acquiring, outcome reviews issue steering cards, and stage retries are capped with the number tuned from data"
metadata:
  node_type: memory
  pinned: true
  originSessionId: 1e5293f3-09a7-4b72-9393-fcba8dd55703
  modified: 2026-09-24T12:16:34.258Z
type: decision
status: in-force
date: 2026-09-24
source: memory/motors_allowed_real_runs_close_labview.md
---

# Motors allowed, real runs, LabVIEW closed at cycle end (user, 2026-09-24)

At the end of the structure discussion the user said:

> "당분간 내가 말하기 전까지는 모터 접속 허용함. 다만 원점 확인 및 모터 리밋, 두 가지는 꼭 확인 필요"
> "녹화프레임 재생으로는 이미 테스트 한 것 같음. 그러나 필요하다면 더 해보도록. 이제 메인 vi 조립시에는 실제 작동시켜야
> 할테니 그대로 해볼 것. 다만 사이클 종료하고서는 제대로 LabVIEW 끄는것 잊지 말것. (특히 카메라가 계속 Acquisition 하면
> 기계에 좋지 않으니)"
> "아웃컴 리뷰에 조향카드 부여하는 것 동의." · "재시도 상한도 동의함. 다만 숫자 3번이 적합한지는 모르겠으니 이후로 계속
> 데이터를 쌓아가면서 조정하도록 하자."

## How I apply it

- **Motors may be driven** (PI magnet, rotor, ASI) by the gate and by a running main VI until the user withdraws
  this, with the rig still physically assembled. Two checks are never skipped: the PI reference move with
  commanded-vs-readback verify at session start, and controller limits set at start and released at end, both
  read back. The user announces any change; I never infer one.
- **A newly assembled main VI's acceptance test is a real run** (camera, motors, bead-pick GUI automation), not only
  ExecState 1 and graph equivalence. Rule 1a is checked on numbers from that run against the original. Recorded-frame
  replay is an extra, used when a real run cannot answer the question.
- The user added the same evening: "코드 작동은 현재 테스트가 가능하나 내가 실제 채널을 현미경에 놓지 않아서 데이터는
  이상한 숫자가 나올 것." So a real run proves OPERATION (runs to stop, frames, motors, save) and garbage tracking
  values are not a failure; the rule-1a NUMBER check is done by recorded-frame replay through the original copy and
  the new VI, never by comparing live runs.
- **Every cycle ends with LabVIEW closed and verified gone** (process list), because a VI left running keeps the
  camera acquiring, which harms the hardware. This is a runner end hook, not a reminder.
- **Outcome reviews steer**: a repeated verdict yields a steering card the judgement session follows or refuses with
  cited evidence; two refusals of the same item stop the runner and put it on the user's decision list.
- **Retry cap per stage per cycle** exists (start at 2 LabVIEW runs; a third needs a judgement card); the number is
  a config value tuned from the recorded per-stage run counts, not fixed.
