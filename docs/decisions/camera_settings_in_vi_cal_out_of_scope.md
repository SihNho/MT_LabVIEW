---
name: camera-settings-in-vi-cal-out-of-scope
description: "The user's 2026-09-25 decisions — camera settings (frame rate, ROI, …) belong INSIDE the new VI's panel, not in NI MAX, and should be saved as metadata with the data; the bead-profile calibration (.cal) FOR-loop stage stays as in the original because frame rate is irrelevant there (only no dropped frame matters); the user cannot judge a file they do not know, so a supervised run request must come with a plain-language description"
metadata:
  node_type: memory
  pinned: false
  originSessionId: 1e5293f3-09a7-4b72-9393-fcba8dd55703
  modified: 2026-09-25T10:05:38.247Z
type: decision
status: in-force
date: 2026-09-25
source: memory/camera_settings_in_vi_cal_out_of_scope.md
---

# Camera settings live in the VI; the calibration stage is out of scope (user, 2026-09-25)

Answers to the decisions cycles 82/83 raised:

- **Calibration stage:** "비드 프로파일 보정은 실험 루프와는 별개로 이전 for 루프에서 실행하잖아. 이 단계에서는 프레임
  레이트가 그렇게 중요하지 않음. 프레임 놓치지만 않으면 무관 (프레임 불안정성도 큰 상관 없음)". So the .cal stage is
  not part of the parallelisation; keep it as the original has it; the only acceptance is that it drops no frame.
- **150 Hz / camera settings:** the user chose adding the settings inside the new VI (copy only): "추후 LabVIEW 상에서
  프레임 레이트 및 기타 셋팅을 잡는 것에 흥미가 있음 (NI MAX 활용은 … 다른 유저가 사용하면 실수하기 쉬울 것 같음. 그리고
  나중에 데이터에 메타데이터로 같이 저장하면 더 좋을 것 같음)". A rate set from outside is undone when the VI opens the
  camera, so the setting must be applied by the VI's own camera setup, and recorded into the saved data's metadata.
- **Supervised run of D1_s3_loop15.vi:** "내가 지금 연구실에 없어서 확인 불가능. 그리고 어떤 코드인지 모름" — never ask
  the user to run a file without first explaining, in plain words, what the file is and how it differs from the
  original; and they may be away from the lab.

## How I apply it

- Goal map R8 (camera settings in the VI + metadata) and R9 (calibration stage unchanged, no dropped frame).
- Requests that need the user at the rig are queued in decisions_pending with a description attached, not
  repeated.
