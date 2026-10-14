# Review of p6fix (2026-10-14 00:49)

- session's own result: PASS
- review verdict: PASS
- cycle counts as: PASS
- discussion: ok, rounds 4, ended converged, doc https://docs.google.com/document/d/1pu_i7qDZFKwY9v7gVZWQu8ixTjK8leB4P6T4RhXPqyg/edit?usp=drivesdk
- summary: `tools/bench/debate/c0-lean-p6fix-review/summary.json`

## agreed
- VERDICT: PASS
- 원본 재계산 X/Y/Z 합계는 9046/9046 (P62 2537, GAP 2537, W40 2540, W100 1432)이고 보고서의 10046/10046 은 오기. 행 단위 자기 번호, cal(날짜 필드 밖 동일), trans/rot 초기화 뒤 값, 모터 리밋 읽기 값, LabVIEW 종료, 입력 md5 24/24 모두 통과
- 방법 이탈(큰 P6 VI 내부 편집, 빌드 5 는 23:19 시작)은 사실로 기록하되, 검증된 D1_ring_p6fix_20261013_231910.vi(3e847397)는 그대로 둠
- 다음: 큐의 latest 다음 p6close 순서 유지. latest.md 3단계는 큰 P6 VI 내부 편집 금지, ring subVI 사본 + callee swap 만 허용으로 고쳐 씀. RingPickSlot #29719 와 RingSeqCheck #29724 를 구분하고, Num 스냅샷에서 최신 유효 슬롯을 고르는 방식을 먼저 검토 (Latest Local #30001 은 읽는 순서가 보장되지 않음). seqlock 과 손상 행 폐기는 유지
- 레그 도구 G0(drive_original_copy_v5.py:549-561, 실패 시 VI 시작 거부)은 제거하지 않음. 기준점 이동을 포함한 모터 절차 변경은 사용자 결정 뒤에 하고, 그때까지 latest 작업에서 모터 도구는 고치지 않음
- 실제 비드 P6-4 는 사용자 승인 후
- 원본 재계산 X/Y/Z 합계는 9046/9046; 보고서의 10046/10046은 정정 대상
- 큰 P6 VI 내부 편집은 방법 이탈로 기록하되 검증된 p6fix는 다시 만들지 않음
- 다음 큐 순서는 latest 후 p6close; 기준 VI는 D1_ring_p6fix_20261013_231910.vi, MD5 3e847397eb120860adb2e868792345f7
- latest는 작은 subVI 사본과 callee swap만 사용; RingPickSlot의 Num 스냅샷에서 최신 유효 슬롯 선택을 먼저 검토하고 seqlock과 손상 행 폐기를 유지
- G0 변경은 latest와 분리하고 사용자 결정 전까지 코드를 유지; 반복 리밋 설정과 기준점 이동은 보고서에 명시
- 실제 비드 P6-4는 사용자 승인 후

## open
- G0의 레그별 리밋 재설정·PI 기준점 이동을 계속 허용할지는 사용자 결정

## experiment

## user_needed
- 현재 레그 도구 G0 은 레그마다 리밋을 다시 설정하고 PI 기준점 이동을 합니다. 이것을 큐 소유 규칙의 예외로 계속 허용할까요, 아니면 안전 확인은 유지하면서 기준점 이동이 없는 확인 방식으로 바꿀까요?
- 현재 G0의 레그별 리밋 재설정·PI 기준점 이동을 계속 허용할까요, 아니면 안전 확인을 유지하면서 기준점 이동 없는 확인 방식으로 바꾸도록 할까요?

