(채팅, 2026-10-10 22:xx) 사용자가 1번(켜지 않는 후보 카드)을 지시했고, 결과를 보고 활성화 안건 상정에 "동의". 결과 원문: tools/bench/cards/result_chat-X9.json, 커밋 87e48c28.

카드 chat-X9 결과 (켠 것 없음):
- 후보 tools/bench/candidates/cand-shellguard-01/ (manifest.json; files/tools/hooks/protected_write.py:417 shell_decision, :385 apply_exception, :553 agent_write_decision; 호출 지점 guard_bash.py:649, guardcore.py:165 R7, guard_card.py:145 — 모두 후보 복사본).
- selftest_shellguard_cand 93/0 (tools/bench/selftest_shellguard_cand.log:402): 거부 형태 41 x 경로 3(Claude, Codex→guard_bash, Codex→guardcore), 허용 15 x 3, 반영 예외 A1-A12, 토큰 T1-T3, 기록부 L1-L7, settings.local W1, 활성 파일 무변경 M1.
- tools/rules_apply.py: bundle id = <change-id>@<core md5 앞 8자>, 토큰 "<bundle-id> 동의", 실행 파일 md5 = 묶음이 지정한 것, 토큰 재사용 거부, 반영 직전 재해시(:384), 기록부 sha256 사슬 감사(:449; 토론 기록 해시는 CRLF 보정).
- tools/rules_protected.json: .claude/agents/**, .codex/agents/**, 기록부(사슬 검사), agent_write_denied [.claude/settings.local.json].
- 기준선 목록 tools/bench/rules_baseline_20261010.json: 보호 파일 75개 md5, "현황 기록, 승인·복원 대상 아님".
- 활성 훅 md5 무변경, 기록부 없음, .git/hooks는 *.sample 14개뿐(core.hooksPath 없음). 기존 시험 selftest_rules_apply 17/0, selftest_guardcore 111/0.
- 묶음 cand-shellguard-01@23fd5380 준비됨: rules_apply check 29/2 — 실패 2개는 두 쪽 동의 토큰이 아직 없어서(예상대로).

결정할 것 (두 쪽 동등; 동의하면 STATE agreed에 정확히 "cand-shellguard-01@23fd5380 동의"):
1. 이 묶음을 켤지. 켜는 순서와 되돌리는 방법을 함께. 켜기 전 필요한 것: 후보 파일 줄바꿈 고정(.gitattributes eol=lf — autocrlf 체크아웃이 md5를 바꿈), 첫 기록부(기준선 genesis)를 누가 어떤 경로로 쓰는지(켜진 뒤에는 셸 거부가 `audit --baseline`도 막음).
2. 글자 검사가 놓치는 경로: 스크립트 내부 쓰기, git pull/merge/rebase/cherry-pick/revert/apply/am, git checkout <branch>, 이어 붙인 경로, 보호되지 않은 relay 파일 — 사후 감사만으로 충분한지.
3. 직접 쓰기 거부(Claude Write/Edit, Codex apply_patch로 보호 파일을 고치는 것; settings.local.json 제외)는 아직 허용 — 다음 카드로 둘지. 파서가 깨질 때 쓰기 모양 명령만 거부하는 현재 동작을 받아들일지.
켜는 일 자체는 합의 뒤 사용자 확인을 거쳐 채팅이 rules_apply로 한다. 묶음을 다시 만들면 번호가 바뀐다.
