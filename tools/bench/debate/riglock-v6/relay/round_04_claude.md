[4라운드] Claude (01:05, 39s, $1.03)

A. 세 질문 모두 동의합니다.

**A. 상대 질문에 대한 답**
1. **동의합니다.** 두 대기자가 같은 죽은 pid 를 보고 한쪽이 새로 만든 mutex 를 다른 쪽이 지우는 경합은 실제로 있습니다. 지금 쓰는 30 s 시간 기준 삭제(`riglock.py:92-94`)에도 같은 경합이 있습니다. 첫 판은 이렇게 갑니다. 시간이 초과되면 mutex 파일의 경로와 pid 를 보여 주며 거부합니다. 삭제는 따로 둔 `break-mutex` 명령으로만 하고, 그 기록은 로그에 남깁니다. mutex 를 쥐는 구간은 몇 ms 짜리 읽기·쓰기뿐이라, 이 방식 때문에 막히는 일은 드물 것입니다.
2. **동의합니다.** 구현안은 이렇습니다.
   - take-stale 을 하면 holder 에 `recovering` 표시가 붙습니다.
   - 그동안 `permitted()` 는 거짓입니다.
   - `recovered(token, report)` 를 불러야 일반 작업이 허용되고, 이 함수가 복구 결과를 로그에 남깁니다. `release(token)` 에 결과 인자가 없다는 지적(`riglock.py:209`)도 이것으로 해결됩니다.
   - 복구가 실패하면 release 하지 않습니다.
3. **확정할 수 있습니다.** 두 항목으로 나눕니다.
   - (가) 새 `tools/rig_session.py`: 채팅·1회성 카드의 감독 프로세스.
   - (나) 작업 자식에게 토큰 전달 + guard_lean 이 riglock 쓰기 명령을 거부. `tools/hooks` 변경이므로 사용자 승인이 필요합니다.

   (가)는 카메라만 쓰는 작업에도 필요합니다. README 규칙 1 이 카메라도 잠금 대상으로 넣기 때문입니다 (`README.md:37`).

**B. 상대 주장에 대한 피드백**
- 거부 사유별 처리에 동의합니다. 살아 있는 다른 holder 는 WAIT, stale·파일 손상·모듈 오류는 StopRun, 실험 상태는 기존처럼 STOP 을 유지하고 자동 재개하지 않습니다. 지금 큐는 STATUS 가 assembled 가 아니면 WAIT 합니다 (`lean_queue.ps1:85`). 다만 실험을 알릴 때는 채팅이 STOP 파일도 같이 쓰므로, 실제 동작은 이 구분과 같습니다.
- "LabVIEW 가 없다는 것은 복구의 전제일 뿐, 닫을 권한은 아니다"에 동의합니다. 복구할 때는 확인만 하고, 닫는 것은 사용자에게 묻습니다.

**C. 내 입장에서 바뀐 것**
- mutex 를 pid 기준으로 지우자던 안을 철회합니다.
- 복구 전용 holder 와 `recovered()` 를 받아들입니다.

**정리안 (상대 확인용)**
1. riglock 수정 (`G:\Codes\rig` 만): `permitted`, 생성 시각, `recovering`/`recovered`, `break-mutex`, 한국어 상태 이름 대응, 임시 폴더 시험.
2. 워크트리 `lean_queue.ps1` + `lean_cycle_hooks.py`: 모의 큐 시험만.
3. 사용자가 상태를 말한 뒤 `--init`, 그다음 실제 큐에서 강제.
4. motor_gate 와 guard_lean 연결. motor_gate 두 사본 동기화를 결정한 뒤에 합니다.
5. `rig_session.py`.

버릴 방안은 런 전체 보유, 실제 리그 그림자, `finally` 에서의 release, 훅에만 토큰 전달, 시간 기준 mutex 삭제, "복구한 뒤 인수" 순서입니다.

**D. 상대에게 새 질문**
없음

STATE {"agreed":["queue process is holder; per-cycle acquire/release","live other holder = WAIT; stale/corrupt/module error = StopRun; experiment = STOP, no auto-resume","failed end hook keeps the lock; no release in finally","experiment mid-cycle: no LabVIEW close, no limit release, handover-incomplete reported (user approves the handling)","check = ownership; permitted(token, allowed_states) separate; queue {assembled}, motor_gate {assembled,disassembled}","pid + creation time","no mutex auto-delete; timeout refuses; explicit break-mutex logged","take-stale -> recovering; permitted false until recovered(token, report)","token to task child + guard_lean refuses riglock write subcommands (separate approval)","chat/one-off: new tools/rig_session.py supervisor inside bgrun (separate approval)","temp-dir mock only, no real-rig shadow; --init before enforce","motor_gate master->worktree sync = separate user decision","stages: 1 riglock fixes, 2 mock queue, 3 init+enforce queue, 4 motor_gate+guard_lean, 5 rig_session"],"open":[],"questions":[],"experiment":"after approval: temp RIGLOCK_DIR + lean_queue -Stub/-Root mock: live holder WAIT, stale StopRun, end-hook fail keeps lock, experiment mid-cycle, recovering blocks permitted, mutex timeout refusal","user_needed":"approve each stage 1-5 separately; motor_gate sync; mid-cycle experiment handover handling; initial rig state before stage 3","check":"Can two Windows processes both succeed with os.open(O_CREAT|O_EXCL) on the same local NTFS file (i.e., is O_EXCL create atomic on NTFS)?","done":true}
