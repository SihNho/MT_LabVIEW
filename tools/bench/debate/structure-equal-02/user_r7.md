(채팅, 2026-10-10 21:4x) 합의한 실험 1~5 결과 — 사용자 지시("이후 2~4번도 진행하도록")로 채팅이 카드로 실행. 원문을 볼 것.

1. guardcore-fix 회귀 + 실제 Codex 실측: tools/bench/cards/result_chat-X4.json (훅 시험 40/41, 실패 1건 c155는 무관), result_chat-X5.json (workspace-write 샌드박스: 금지 8/8 거부, 허용 3건은 Codex 샌드박스 오류 "setup refresh had errors"), result_chat-X5b.json (사용자 운영 규칙대로 -s danger-full-access: 15/0 — 금지 8/8 거부, 허용 3/3 실행). Codex 실제 입력 형태: Bash·apply_patch 모두 tool_input {command}. 새 사용자 결정: docs/decisions/codex_sessions_run_full_access.md (이 PC에서 Codex 샌드박스가 실패하므로 Codex는 항상 전체 접근, 신뢰된 프로젝트 훅이 안전 장치; peer.ps1의 codex 리뷰어는 아직 read-only — 공동 결정 안건).
2. 반영 통로 후보 (켜지 않음): tools/rules_apply.py, tools/rules_protected.json, tools/git_precommit_rules.py, tools/bench/candidates/README.md; 시험 tools/bench/selftest_rules_apply.py 17/0 (임시 복사본); 실제 저장소 모의 감사 보호 파일 49개. result_chat-X6.json.
3. 단발 가설 리뷰 vs 독립 1라운드 + 토론: tools/bench/reviewbench/report_x7.md — 3건 중 1건(사례 3)에서만 토론 쪽이 더 나은 판별 시험; 비용 Claude 2.7배 + GPT·Gemini, 시간 2.5배; 한계 n=3, Claude 채점자, 부분 맹검, 누설 가능.
4. 이어 가기(--fork-session) vs 새 세션: tools/bench/forkbench/report_x8.md — 판단 질 차이 없음(n=3), 이어 가기 비용 5~6배(캐시 식음, 4~7시간 뒤), 더 빠름(0.8~1.1 vs 1.4~1.9분); 저장소를 되돌릴 수 없어 미래 정보 누설 오염; 원본 기록 보존 확인.

이번 라운드부터 결정할 것 (두 쪽 동등, 각 항목 동의/반대/수정을 STATE에):
A. 반영 통로 켜기: (a) git_precommit_rules.py를 .git/hooks/pre-commit으로 설치할지 (b) guardcore에 "보호 파일은 rules_apply 밖에서 직접 쓰기 거부" 규칙을 넣을지 (c) 지금 트리로 첫 기록부(기준선)를 쓸지 (d) 보호 범위: .claude/agents/**, .claude/settings.local.json(사용자 개인 파일), 기록부 자체(추가만 허용 검사 필요) (e) .codex/agents/*.toml 21개가 정책인지 벤치 설정인지.
B. 실험 3 결과로 가설 리뷰 통합 범위를 다시 정할지 (전부 토론 / 좁은 조건만 / 단발 유지).
C. 실험 4 결과로 긴 사이클 방향을 다시 정할지 — 오염 없는 다음 측정(러너 재개 시 실제 넘김 순간에 두 방식을 동시에, 캐시가 살아 있을 때)을 할지.
D. peer.ps1 codex 리뷰어의 read-only 약속을 바꿀지 (이 PC에서 Codex 샌드박스는 실패함).
각 결정이 바꾸는 파일과, 켜는 순서·되돌리는 방법을 함께 적을 것. 켜는 일 자체는 합의 뒤 사용자 확인을 거쳐 채팅이 한다.
