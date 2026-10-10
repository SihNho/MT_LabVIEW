Agreed conclusions:
- K3f/K4f: STUB (occupied sink) and inner-face ADDRESS are two separate blockers; prefix rule ignored routability
- P4 1055 came from the later RLE op, not delete_object; prior-art 'settled-already' mismatched the failing op
- w23519 whole delete_wire is harmful and withdrawn
- dry PASS and sim RLE give no independent evidence (stagexec.py:4249-4250, stagesim.py:2249-2265)
- D-gate compares pairs and cannot see a loose stub (prep_c164_a2_3_dry.log:58); EL count is the observer
- minimal discriminator = original A53->A54->A55 only, reading w23460 presence, w23519 sinks + broken state, EL loose-end count after A54 and A55
- w23519 전체 삭제는 부적절
- K3f/K4f의 STUB와 ADDRESS는 별개 차단 사유
- P4의 1055는 J에 없는 후속 RLE에서 발생
- 부분 도착점 삭제 뒤 빈 가지가 남는지가 J의 핵심 실측 항목
- 오류 예측은 A54/A55를 이미 UNPREDICTED로 표시

Proposed discriminating test:
- on a new byte copy (user-approved): run original A53->A54->A55 only; after A54 and A55 read w23460 presence, w23519 sinks and broken state, Error List 'Wire has loose ends' count
- 새 복사본에서 원래 A53→A54→A55만 실행하고 정리 전에 두 배선의 존재·broken 상태와 w23519의 나머지 세 연결을 단계별 확인

Still open:
- #23501 삭제 뒤 w23519의 실제 broken 상태와 세 연결 보존 여부는 실측 필요