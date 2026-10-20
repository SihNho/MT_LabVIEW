[1라운드] Claude (01:02, 91s, $0.52)

**입장:** riglock 을 V6 에 처음 붙일 때는 **lean_queue.ps1 한 곳에, 그림자 모드(기록만 하고 막지 않음)로** 연결하자는 것입니다. motor_gate 와 가드 훅은 riglock 수정과 두 사본 정리가 끝난 뒤에 다룹니다.

**근거와 방안**
1. **holder 는 큐 프로세스로.** 큐는 런 전체 동안 살아 있고, 사이클 훅은 짧게 끝나는 자식 프로세스입니다 (`lean_queue.ps1:74`, `:93-106`). README 규칙 2 도 같은 말입니다 (`README.md:38`).
2. **토큰은 훅을 부를 때만 넘깁니다.** 인자로 주거나, 그 호출 동안만 env 에 둡니다. `$env:` 를 런 전체에 걸어 두면 `launch_lean.ps1` 의 Opus 세션까지 물려받습니다 (`:100`). 그 세션이 토큰을 쥘 이유는 없습니다.
3. **권위는 두 곳을 AND 로 봅니다.** motor_gate 는 지금 STATUS 의 `rig-state:` 를 권위로 읽습니다 (`motor_gate.py:142-160`, `:849-854`). 옮겨 가는 동안에는 STATUS 와 rig_lock.json 중 **하나라도** assembled 가 아니면 거부합니다. STOP 파일은 "사용자가 멈추라고 함"이라는 다른 신호라서 그대로 둡니다 (`lean_queue.ps1:80`, `:108`).
4. **riglock 에 요청할 수정**
   - a) **실험 상태에서 check 가 True 를 줍니다** (`riglock.py:200-206`). check 를 False 로 바꾸거나, 실험 상태를 따로 나타내는 종료 코드를 주는 방식으로 고쳐야 합니다.
   - b) **pid 만으로는 holder 를 확인하기에 부족합니다.** pid 와 함께 프로세스 생성 시각을 기록하고 맞춰 봐야 합니다.
   - c) **상태 이름이 다릅니다.** riglock 은 영어만 쓰고 (`riglock.py:37`), STATUS 는 조립/실험중을 씁니다 (`motor_gate.py:154-159`). 둘을 맞추는 대응표가 필요합니다.
5. **motor_gate 는 지금 건드리지 않습니다.** 러너가 쓰는 것은 워크트리 사본입니다 (`lean_cycle_hooks.py:33`, `:51`). master 만 고치면 러너에는 아무 효과가 없습니다. 게다가 채팅이 motor_gate 를 직접 쓸 때 (2026-10-19 회전 확인) 쓸 만큼 오래 사는 holder pid 를 아직 정하지 못했습니다.
6. **사용자가 LabVIEW 를 손으로 쓰는 경우**는 riglock 이 볼 수 없습니다. 지금과 마찬가지로 채팅이 STOP 파일을 쓰고 `set-state experiment` 를 함께 실행하는 것이 유일한 신호입니다.

**단계**
- **0단계:** 사용자가 초기 상태를 말하고 `--init` 합니다. riglock 수정 a~c 와 자체 시험을 합니다.
- **1단계 (그림자):** 큐가 런 시작에 acquire, 끝에 release 하고, check 결과는 `queue.log` 에만 남깁니다. 시험은 `-Stub`/`-Root` 모의 큐에 `RIGLOCK_DIR` 임시 폴더를 써서 합니다 (`lean_queue.ps1:28`). 되돌리기는 큐 파일 하나를 복원하면 됩니다.
- **2단계 (강제):** check 가 실패하면 StopRun 합니다. `lean_cycle_hooks` 는 토큰이 없으면 거부합니다.
- **3단계:** motor_gate 와 채팅 세션 연결 (별도 승인).

**상대에게 질문**
1. 채팅 세션이나 1회성 카드의 holder pid 로 어떤 프로세스를 쓰자는 건가요? Bash 호출은 금방 끝납니다.
2. 런 도중 실험 상태가 되면 STOP 파일만으로 충분하다고 보나요, 아니면 check 도 실패해야 한다고 보나요?
3. 리뷰·계획 단계(하드웨어 없음, 최대 약 65분) 동안에도 잠금을 계속 쥐어야 하나요?
4. 3단계 전에 master → 워크트리로 motor_gate 를 동기화(rotor envelope)하는 것을 별도 사용자 결정으로 따로 떼어야 하나요?

STATE {"agreed":[],"open":["holder for chat/one-off cards","check semantics under experiment","hold lock across review/plan","motor_gate two copies before stage 3","AND authority STATUS+riglock during transition","token passing scope (per-hook only)"],"questions":["1. 채팅·1회성 카드의 holder pid 는 어떤 프로세스?","2. 런 중 experiment 전환 시 STOP 파일로 충분한가, check 도 실패해야 하나?","3. 리뷰·계획 단계에도 잠금을 쥐는가?","4. motor_gate master→워크트리 동기화를 별도 사용자 결정으로 분리할까?"],"experiment":"mock queue (-Stub/-Root) with RIGLOCK_DIR temp dir: shadow acquire/check/release logged, no LabVIEW, no motor","user_needed":"initial rig state for --init; approval per stage (0 riglock fixes, 1 shadow in lean_queue, 2 enforce, 3 motor_gate)","check":"On Windows, does comparing a pid's process creation time (GetProcessTimes) reliably detect pid reuse?","done":false}
