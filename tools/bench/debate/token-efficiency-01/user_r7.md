(사용자 구상, 채팅에서 2026-10-10 17:xx — 이번 라운드부터 토론의 중심 주제)

"앞으로 구독을 어떻게 하는게 좋을지 고심임. 경우에 따라서는 클로드 기본 모델로 낮추고 지피티를 메인으로 사용하는 것도 고려중임. 그러니 어떤 모델이 메인으로 프로젝트를 이어갈지도 알 수 없는 상황. 현재로서는 클로드 세션을 열어서 프로젝트 진행을 맡기고 있는데, 개정 후에는 클로드가 되었든 아니면 지피티가 되었든 어떤 세션에서건 동일한 프로젝트를 진행할 수 있었으면 좋겠음." → "이 부분을 어떻게 구성할지 디스커션 이어서"

사용자 조건 (같은 대화):
- 내렸다가 다시 올리는 구독 변경은 효용이 없음: 지난달 Max 5x → 20x 업그레이드 때 차감이 거의 없어 한 달에 50만원 넘게 냄. 한 달 단위로 유지할 조합을 정해야 함.
- 가격(검색, 세금 제외): Claude Max 5x $100 / 20x $200; ChatGPT Plus $20, Pro $100(Codex Plus의 5배) / $200(20배; 9-10 이후 신규 가입 중단이라는 출처 1곳, 상충). 부가세 10%, 1 USD ≈ 1,380~1,430원.
- 현재: Max 20x(주간 77%, 이번 주는 거의 다 씀) + ChatGPT Plus.

채팅(Claude)이 정리한 '지금 Claude에만 묶인 것' 표 — 출발 자료로만, 원문 확인할 것:
1. 규칙: CLAUDE.md (Codex는 AGENTS.md를 읽는데 지금 AGENTS.md는 동료 리뷰어용 안내) → 공통 규칙 원본 하나 + 두 파일은 가리키기만?
2. 기억: ~/.claude/projects/.../memory/ (사용자 결정 ~90개, 저장소 밖, Claude 전용) → 저장소 안 docs/decisions/ + 색인?
3. 안전 규칙: Claude Code 훅 tools/hooks/*.py (.claude/settings.json; guard_bash LabVIEW 시간 제한·실행 전 점검, guard_write 헤더, guard_peer, guard_session, answer_first, report_gate, .vi 쓰기 금지) → GPT 세션에선 작동 안 함 → 실행 스크립트 자체가 거부하도록(도구 안으로)? Codex의 sandbox/approval/명령 규칙이 무엇을 대신할 수 있는지는 미확인(check 대상).
4. 보고: Claude 앱 예약 작업 runner-cycle-report + report_gate 훅 → 러너가 쓰는 보고 파일을 어느 세션이든 첫 턴에 읽기?
5. 러너 세션: cycle_runner.py 의 claude -p + .claude/agents/*.md → 실행기 백엔드 선택(Claude/Codex); tools/debate_relay.py 가 이미 양쪽을 부름.
6. 기술 문서: .claude/skills/labview-automation → docs/ 로?
7. 이미 공통: STATUS.md, tools/bench/next.json, 카드 JSON, docs/, stagekit 등 Python 게이트(cycle_runner, guard_assign, stage_prerun, bgrun, motor_gate).

토론에서 정해 줄 것: 목표 구조(어느 세션에서 열어도 같은 상태로 시작·같은 안전 규칙), 옮기는 순서와 각 단계의 판별 시험(예: 같은 카드를 Claude 세션과 Codex 세션에서 돌려 같은 게이트에 막히는지), 안전 규칙 이전에서 빠지면 안 되는 것(원본 보호 규칙 1, 모터 규칙 1b, LabVIEW 시간 제한), 그리고 이 구조가 10월 16일 구독 결정에 주는 영향(이전 기간 동안 어떤 조합이 안전한가).
