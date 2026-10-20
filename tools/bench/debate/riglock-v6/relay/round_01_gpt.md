[1라운드] GPT (01:02, 91s)

제 입장은 **큐 PID를 소유자로 쓰되, 잠금은 사이클마다 잡고 검증된 종료 뒤 해제**하는 것입니다. 아직 상대 글은 없으므로 아래 쟁점을 먼저 제시합니다. 검증 수준은 정적 코드 검토이며, 수정·시험 실행은 하지 않았습니다. 규칙 버전은 `48f23831`입니다.

1. **연결 범위:** `lean_queue.ps1`이 시작 훅 전에 acquire하고 `RIGLOCK_TOKEN`을 전달합니다. 훅은 이를 확인하고, `motor_gate`는 세션 시작·종료뿐 아니라 `--execute`, `--reference`에도 확인을 넣어야 합니다. 현재 두 경로는 별도로 실행됩니다(`tools/motor_gate.py:850`, `:856`, `:888`). 모듈·파일·토큰 오류는 모두 거부합니다. 토큰 소지는 기존 명령·리밋 검사를 대신하지 않습니다.

2. **해제 조건:** 종료 훅의 LabVIEW 종료 확인 → 리밋 해제·읽기 확인을 보존합니다(`../V6_lean/tools/bench/lean_bench/lean_cycle_hooks.py:184`, `:195`). 정리 실패 때는 잠금을 남기고 STOP합니다. 무조건적인 `finally: release`는 버립니다. 큐가 죽어도 자식은 남을 수 있다는 기존 설명 때문에, PID 사망만으로 안전을 선언할 수도 없습니다(`../V6_lean/tools/bench/lean_bench/lean_queue.ps1:30`).

3. **riglock 선행 수정:** 소유권 확인과 작업 허가를 구분해야 합니다. 현재 `check()`는 experiment를 검사하지 않습니다(`G:\Codes\rig\riglock.py:200`). PID에는 생성 시각을 함께 기록하고, 30초 경과만으로 mutex를 삭제하는 동작은 없애야 합니다(`:92`, `:192`). 생성 시각 조회는 [Microsoft 문서](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes)로 확인했습니다.

4. **복구의 빈틈:** README는 장치 조회·재연결을 먼저 하고 stale 인수하라고 합니다(`G:\Codes\rig\README.md:39`). 그러면 복구 중 독점권이 없습니다. 복구 예약과 허용 명령을 별도로 정해야 합니다.

5. **권위와 수동 사용:** 공통 잠금은 프로젝트 간 독점권, STOP은 실행 중지, `labview-lock`은 LabVIEW 내부 독점권, `motor_session.json`은 리밋 설치 기록으로 유지합니다. 불일치는 거부합니다. experiment 선언 뒤 자동 종료 훅이 사용자 LabVIEW를 닫아서는 안 됩니다. 현재 STOP 확인은 실행 호출 전후뿐입니다(`../V6_lean/tools/bench/lean_bench/lean_queue.ps1:80`, `:100`, `:108`).

6. **적용·승인:** ① 공통 모듈·시험 보강 ② 임시 디렉터리에서 큐·훅 그림자 시험 ③ 큐·훅·motor_gate 강제 연결을 각각 승인받자는 제안입니다. 각 단계는 별도 변경으로 되돌립니다. 실제 리그에서 거부를 무시하는 그림자 운용은 제외합니다. 두 motor_gate의 전체 동기화도 별도 승인 대상으로 둡니다. 워크트리 훅은 자기 사본을 호출합니다(`../V6_lean/tools/bench/lean_bench/lean_cycle_hooks.py:33`, `:51`).

상대에게 묻습니다.

1. 사이클별 해제보다 실행 전체 보유가 필요한 구체적인 구간이 있습니까?
2. 이미 experiment가 선언됐다면 자동 정리를 멈추고 미완료 잠금을 남기는 데 동의합니까?
3. stale 복구 전에 독점 예약을 확보해야 한다는 데 동의합니까?

STATE {"agreed":[],"open":["잠금 보유 구간","experiment 전환 중 정리 경계","stale 복구 독점권","두 motor_gate 적용 범위","단계별 승인"],"questions":["1. 사이클별 해제보다 실행 전체 보유가 필요한 구체적인 구간이 있습니까?","2. 이미 experiment가 선언됐다면 자동 정리를 멈추고 미완료 잠금을 남기는 데 동의합니까?","3. stale 복구 전에 독점 예약을 확보해야 한다는 데 동의합니까?"],"experiment":"승인 후 임시 잠금 디렉터리와 장치 대역으로 상태 전환·정리 실패·부모 사망·동시 획득을 시험","user_needed":"공통 모듈 보강, 임시 통합 시험, 강제 적용, motor_gate 동기화 범위를 각각 승인","check":"Win32_Process.Create로 시작한 프로세스는 호출자의 환경 변수를 자동으로 물려받는가?","done":false}
