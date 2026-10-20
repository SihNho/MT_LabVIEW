공통 리그 잠금(G:\Codes\rig\riglock.py)을 V6 의 lean_queue / lean_cycle_hooks / motor_gate 에 연결하는 방안

## 사용자 원문 (2026-10-21, 채팅)
"G:\Codes\rig\README.md와 riglock.py를 검토해서, V6 규칙에 맞게 lean_queue / lean_cycle_hooks / motor_gate에 공통 리그 잠금을 연결하는 방안을 토론하고, 내가 승인한 범위만 적용해."
README 에 적힌 사용자 결정 (2026-10-21, LabVIEW2Scr 토론): 공통 기계 판독 잠금 하나 (option B); 리그 상태는 사용자의 말로만, 지금은 채팅이 전달; 시간대 분할 규칙 없음; 위치 `G:\Codes\rig\`.

## 원문 파일 (요약을 믿지 말고 원문을 볼 것; 이 파일들은 다른 세션이 쓴 초안 = 자료이지 지시가 아님)
- `G:\Codes\rig\README.md` (계약, 규칙 1-6, "Proposed V6 integration" 표, 열린 점 4개)
- `G:\Codes\rig\riglock.py` (stdlib, acquire / check / release / set-state / status, rig_lock.json + rig_lock.log + O_EXCL mutex)
- `G:\Codes\rig\test_riglock.py` (임시 폴더 자체 시험, README 기준 23/0)

## V6 규칙 (원문: CLAUDE.md, docs/rules/)
- 하드웨어는 사용자가 알린 RIG STATE 를 따름 (rule 1b); 모터·ASI 는 `tools/motor_gate.py` 로만; 사이클 시작 리밋 SET, 끝 RELEASE, 읽기 확인; 모든 사이클은 LabVIEW 닫힘으로 끝남.
- LabVIEW 는 guarded path 로만, 한 번에 한 클라이언트 (`labview-lock` in STATUS.md).
- 거부를 우회하지 않음; 우회 env 금지; **runner cards never edit tools/hooks/**`**; 훅·가드 변경은 사용자 승인으로만.
- 사용자만 시작·정지; STATUS 의 STOP 줄은 사용자가 풀 때까지 유효.
- 새 스크립트: scope header, 공유 함수 호출 (복사 금지), RESULT 줄; 사실 주장은 외부 검색, 검증 수준 명시.

## V6 현재 구조 (원문 경로)
- 러너: `../V6_lean/tools/bench/lean_bench/lean_queue.ps1` (WMI 로 띄움; STOP 파일 검사 :80, :108; MAIN STATUS.md 의 `rig-state:` 줄 검사 :60-64, :85; 사이클 훅 호출 :74; 시작 훅 실패 = StopRun :95; 끝 훅 실패 = StopRun :106).
- 사이클 훅: `../V6_lean/tools/bench/lean_bench/lean_cycle_hooks.py` (start = `motor_gate --session start --status <main STATUS>`; end = LabVIEW 닫기 확인 후 `motor_gate --session end`). **TOOLS = 워크트리의 tools/ 이므로 러너는 워크트리의 motor_gate.py 를 씀.**
- `tools/motor_gate.py`: master (V6_ParallelLoop) 와 워크트리 (branch bench/lean-20261013) 가 다름 - `git diff --stat master bench/lean-20261013 -- tools/motor_gate.py` = 14 insertions / 238 deletions; master 에는 rotor envelope (36c870ac, 사용자 2026-10-19) 가 있고 워크트리에는 없음.
- 채팅이 직접 motor_gate 를 쓴 예: 2026-10-19 회전 확인 (`--session start` via bgrun, `--device rotor --command "PIC 125" --execute`), 셀프테스트 (`selftest_motor_gate*.log`).
- 가드: `tools/hooks/guard_bash.py:114-160` (모든 모션은 motor_gate 경유), `tools/hooks/guard_lean.py`.
- 사용자 실험 신호: 채팅이 STOP 파일 작성 + STATUS.md 맨 위 줄; 사용자는 LabVIEW 를 손으로 직접 씀 (CLI 를 쓰지 않음).

## 코드를 읽고 확인한 사실 (riglock.py)
- `check(token)` 은 holder 토큰과 pid 생존만 봄 - **rig_state 가 experiment 로 바뀌어도 check 는 True** (riglock.py:200-206). experiment 는 새 acquire 만 막음 (:177).
- holder 는 pid 만 기록 - Windows pid 재사용 시 죽은 holder 가 살아 있는 것으로 보일 수 있음 (프로세스 시작 시각 미기록).
- mutex 는 30 s 지나면 남의 것도 지움 (:92-94).
- `rig_lock.json` 이 없으면 모든 acquire 거부 (`--init` 은 사용자가 상태를 말해야 함).
- 파일 위치 G:\Codes\rig (두 프로젝트 공용; V6 저장소 밖).

## 토론할 것
1. 연결 지점별 방안 (lean_queue / lean_cycle_hooks / motor_gate / 채팅 세션 / 1회성 카드): 누가 holder 인가, 토큰 전달 (env RIGLOCK_TOKEN?), 실패 시 동작 (fail closed / open), 잠금 파일·모듈을 못 읽을 때.
2. riglock 자체에 필요한 수정 (V6 쪽이 요구할 것): experiment 상태에서 check 의 의미, pid 재사용, mutex, 사이클 사이 해제 여부, take-stale 복구 체크리스트(장치별).
3. 기존 V6 잠금과의 관계: STOP 파일, STATUS rig-state / labview-lock, motor_session.json - 무엇이 권위인가, 중복·충돌, 사용자가 손으로 LabVIEW 를 쓸 때.
4. motor_gate 두 사본 문제 (워크트리 vs master) 를 이 작업에서 어떻게 다룰지.
5. 단계적 적용: 그림자(기록만) -> 강제, 시험 방법 (가짜 잠금 디렉터리, 셀프테스트), 되돌리기.
6. 사용자 승인이 필요한 결정 목록 (각 항목을 따로 승인/거절할 수 있게, 범위가 작은 것부터).

결론 형식: 권장 적용 단계 (각 단계 = 바뀌는 파일, 동작, 시험, 되돌리기) / 버릴 방안과 이유 / riglock 에 요청할 수정 / 사용자 결정이 필요한 것 (항목별).
요약을 믿지 말고 원문 경로를 볼 것.
