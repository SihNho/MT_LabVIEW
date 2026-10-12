훅 수정 동의 요청 - 상대 경로 스크립트를 명령 실행 폴더 기준으로 판정 (scope-cwd-fix-20261012)

## 사용자 원문 (2026-10-12)
"동의 받고 고쳐. 만약 벤치 해서 GPT를 갈아탈 동인이 약하다면 이후로는 GPT 무시할 수 있겠지만 우선은 조심할것"
→ 이 한 가지 변경에 대해 Claude와 GPT 두 쪽의 동의를 받은 뒤에만 채팅이 고친다. 두 쪽은 동등하다. 이 문서에는 채팅의 수정안과 측정 사실만 있다; 더 나은 안이 있으면 내도 된다.

## 배경 (원문을 볼 것)
- GPT 대 Claude 벤치(카드 chat-X10d, tools/bench/cards/result_chat-X10d.json, 로그 tools/bench/matbench/x10/x10d_step0_live.log:6-9): GPT 칸(..\V6_bench\gpt_cell, Codex --profile matbench, 신뢰된 훅 tools/bench/matbench/codex_cell_hook.py → cell_guard + adapt_codex/guardcore)에서 `py tools/bench/matbench_out/x10d_offline_ok.py`(머리 표시 labview none, hardware none)가 guard_bash 2b "Got timeout=None"으로 거부됨.
- 원인: tools/scope_header.py:421-423 `_abs()`가 상대 경로를 항상 본 폴더 ROOT 기준으로 바꿈 → 칸에만 있는 스크립트는 :510 `in_tools`/`isfile`에서 건너뜀 → tools/hooks/guard_bash.py offline_scripts_only()(:436-449)가 False → 2b가 시간 제한을 요구 → Codex 입력에는 시간 제한 칸이 없음(x10d_env_probe_raw.jsonl: tool_input={command}).
- Claude 칸은 훅 설정이 칸 폴더를 가리키도록 바뀌어(tools/bench/matbench/matbench.py:184-188) 이 차이가 없다. 즉 지금 GPT 칸은 자기가 만든 오프라인 스크립트를 못 돌리는 불평등 조건.
- 이미 동작하는 다른 보호: cell_guard(tools/bench/matbench/cell_guard.py BAN_CMD/BAN_SRC — 실행되는 .py 원문에 gscript/stagekit/stagexec/win32com/comtypes import가 있으면 거부, LabVIEW·GUI·장비·동료·git 변경 금지, 칸 밖 쓰기 금지), 모터 게이트와 실행 전 점검(벤치 표시로 꺼지지 않음, guard_bash.py:146,:174).

## 채팅의 수정안
1. tools/scope_header.py: `launch_scope(cmd, extra=(), cwd=None)` — 상대 경로는 cwd(훅 입력의 "cwd")가 주어지면 그 폴더 기준으로, 없으면 지금처럼 ROOT 기준. `in_tools`도 같은 기준 폴더의 tools/ 아래인지로 판정. cwd가 프로젝트처럼 보이지 않으면(그 아래 tools/가 없으면) 스크립트를 못 찾아 건너뜀 → 지금과 같은 보수적 경로(시간 제한 요구).
2. tools/hooks/guard_bash.py: offline_scripts_only()와 scope_gate()가 훅 입력의 cwd를 launch_scope에 넘김.
3. 효과: 본 폴더 세션(cwd = 본 폴더)은 동작 변화 없음. 칸 안의 "labview none + hardware none" 스크립트는 시간 제한 없이 통과. LabVIEW 스크립트는 여전히 시간 제한 또는 bgrun 필요. 머리 표시가 거짓인 스크립트는 scope_header의 기존 검사 + cell_guard BAN_SRC가 막음.
4. 시험: 기존 훅 시험 41개, selftest_guardcore, selftest_guard_bash_codex에 cwd 경우 추가(칸 cwd + 칸 전용 none 스크립트 → 허용; 칸 cwd + LabVIEW 머리 스크립트 → 거부; cwd 없음 → 지금과 동일; 거짓 머리 → 거부), 그리고 GPT 칸 시작 전 확인(step 0) 재실행.

## 결론 형식
동의하면 STATE agreed에 정확히 "scope-cwd-fix-20261012 동의". 반대나 조건이 있으면 open에 이유와 함께. 적용은 두 쪽 동의 뒤 채팅이 하고, 회귀 시험 결과와 해시를 토론 폴더에 기록한다.
