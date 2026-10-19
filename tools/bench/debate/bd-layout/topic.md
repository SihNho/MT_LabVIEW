P6L 블록 다이어그램 배치 정리 - 다른 사람이 읽을 수 있게 만드는 방법

## 사용자 원문 (2026-10-19, 채팅)
- "코드를 살펴보니 사방 팔방으로 뻗쳐있는걸 확인함. 코드 정리한번 해볼래?"
- "기능을 말하는게 아니라 코드 위치가 너무 사방팔방임."
- 방법 B 선택: 구조별 Clean Up, 가장 안쪽부터, 그 다음 최상위 루프를 정해진 순서로 배치. "B가 좋겠음"
- "그리고 플랫 시퀀스, 루프, 등등 크기가 너무 커" / "사실 'Clean-up diagram' 하면 그걸 자동으로 줄여주기는 함"
- "사실은 나도 clean-up diagram 해봤거든? 그런데 안되더라고. 너가 하면 다를까 했음."
- "그렇다면 방법이 뭘까? 이 방식이라면 다른 사람은 너 코드를 전혀 읽을 수 없으므(로)"
- "음.... clean-up 말고 좌표 재지정은 안됨?"
- "이거 토론 해봐. 어떻게 해결할지"

## 지켜야 할 규칙 (CLAUDE.md 원문 요지 - 원문은 CLAUDE.md, docs/rules/)
- 원본 파일 수정 금지; 파생 작업은 `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev` 에만 (rule 1).
- 원본의 계산을 바꾸지 않는다; 판정은 숫자 (같은 입력 -> 같은 X/Y/Z; replay bit-identical + 150 Hz leg) (rule 1a).
- 루프 사이 제어 신호는 LOCAL VARIABLE, 큐 금지 (rule 1c'').
- .vi 파일을 파일로 편집 금지; LabVIEW 는 guarded path(bgrun, timeout) 로만; 빌드 단계 메모리 상한 MEMSTOP 695 MB.

## 측정된 사실 (원문 경로 - 요약을 믿지 말고 원문을 볼 것)
- 대상: P6L = `claudeDev\bench\lean\D1_ring_fxdP6L_20261016_115105.vi` md5 54f7cd2f27175b3aa993a2e7630cff40 (제품 후보, 150 Hz PASS).
  루프 Bounds 가 ±32767 을 넘음 (#10170 폭 36528). 사용자가 `_Copy.vi` 에서 전체 Clean Up 을 시도하자 LabVIEW 가 ~556 MB 에서 멈춤.
- 원본 hierarchy: 170 diagrams (`docs/motor-call-site-census.md`).
- 1차 탐색 보고서: `../V6_lean/tools/bench/lean_bench/lean_report_bdtidy_fail1.md` - 내부 다이어그램에 Clean Up = error 1071; 선택 후 Clean Up 은 최상위 구조만.
- 2차 탐색 보고서 (PASS): `../V6_lean/tools/bench/lean_bench/lean_report_bdtidy.md` - 핵심:
  - 구조물 확대: `FlatSequence.Size Frame` (3578B804) 로 가능; GObject.Move 로 노드 이동 시 구조물 자동 확장 없음; 모든 구조 클래스에서 Bounds 는 read-only.
  - Shrink Wrap Structures (6375403): 4 회 호출 모두 아무것도 줄이지 않음; 최상위에서 내용이 밖으로 나간 루프를 키우고 이웃을 784 px 밀어냄; 재귀 아님.
  - 영역 선택 Clean Up: 중첩 구조 둘레 사각형 = 0 객체 선택 -> 전체 Clean Up. 최상위 루프 선택 -> 그 루프의 중첩 트리 전체를 재배치·축소 (FS 906x2447 -> 589x160), 이웃을 밀어냄.
  - 모든 호출에서 wire-edge set, node census, tunnel uid, wire uid 변화 없음.
- 회전 위치 수정 사본 P6R 보고서: `../V6_lean/tools/bench/lean_bench/lean_report_rotpos_fail1.md` - 9 개 subVI 교체만 했는데 y = 32710 (좌표 한계) 의 노드 5 개가 16 px 이동, 저장 시 ±32767 밖의 객체 25 개를 LabVIEW 가 재배치 (게이트 G7 FAIL). 좌표 한계가 이미 편집을 방해하고 있음.
- 검증된 scripting 메서드/속성 목록: `docs/vi-server-ids.json`, `docs/toolkit-capabilities.md`. 스킬 `labview-automation`.

## 토론할 것
1. 사용자가 원하는 결과(사방에 퍼진 코드를 모으고, 너무 큰 구조물을 줄이고, 다른 사람이 읽을 수 있게)를 얻는 현실적인 방법은?
   (예: 좌표 재지정 - 노드/구조물 위치를 스크립트로 직접 지정하고 구조물 크기를 맞추기; 최상위 단위 Clean Up 을 단계적으로; 루프 본문을 subVI 로 분리;
   그 밖의 방법) - 각 방법이 LabVIEW 2026 scripting 으로 실제로 가능한지, 무엇이 아직 미검증인지, 계산 불변(rule 1a)과 local-variable 규칙과의 관계.
2. 사용자의 Clean Up 이 왜 실패(멈춤)했는지에 대한 가설과 확인 방법.
3. 위험: 메모리(695 MB), 좌표 한계, 선 재배치, 성능(150 Hz), 검증 게이트.
4. 첫 실험 하나 (작은 scratch VI 에서 무엇을 확인할지) 와 그 다음 P6L 사본 적용 순서.

결론 형식: 권장 방법 / 버릴 방법과 이유 / 판별 실험 (무엇을 측정해 무엇이면 진행) / 사용자 결정이 필요한 것.
요약을 믿지 말고 원문 경로를 볼 것.
