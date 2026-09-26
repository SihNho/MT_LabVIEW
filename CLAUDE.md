---
type: rules
status: current
date: 2026-09-15
tags: [rules]
---

# Standing rules — read before doing anything

## 1. Never modify an original file. Ever.

Applies to **every** pre-existing `.vi` this project touches: the reference VI
`Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi`, everything in `zz_LabView VI\background
VIs\`, and any original opened for inspection. **Copies are always fine** — new/derived work goes in
`C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev`, never saved over an
original, never into this project folder.

A `*` in a LabVIEW title bar does **not** mean the disk file changed — only an explicit Save does.
If an original ends up dirty: close **without saving**, verify the on-disk checksum, continue.
Answer **Don't Save** to every save prompt naming an original (merely *opening* a hierarchy in a
newer LabVIEW relinks subVIs, dirties them, and one "Save" on exit rewrites the whole hierarchy in
the newer format — irreversibly). After any session that opened originals, audit saved-version
bytes offline: `19 00 80 00` = LV2019, `26 00 80 00` = LV2026.

## 1a. Never change the original's COMPUTATION — this is a behaviour-preserving refactor

**User, 2026-08-30: "원본의 연산방법 자체를 바꾸면 안돼. 이건 꼭 명심하고."** Only *scheduling* may
change (shift registers → auto-indexed tunnels, parallel instances). The per-bead maths, the
parameters that reach it, and the numbers that come out must be identical.

- A change of decomposition can be a change of computation — any kernel substitution must be
  justified as equivalent or checked numerically, never assumed.
- Parameters must arrive by the same route with the same values; falling back to a default is a
  computation change in disguise. Whole-array parameters must cross loop borders **non-indexed**.
- **Acceptance is numeric**: same inputs → same X/Y/Z through old and new paths. `ExecState == 1`
  says nothing about equivalence.
- When a step cannot be shown computation-preserving, **stop and ask the user**.

## 1b. Hardware permission is a function of the RIG STATE — and the ASI is not a special case

**RE-ISSUED 2026-09-16 by the user**, replacing every earlier hardware rule:
*"모터 접근 및 카메라 접근을 '리그 분해 / 리그 조립 / 실험중' 상태에 따라 다르게 두는게 맞는듯. 리그 분해 →
모든 모터 및 카메라 접근 허용. 리그 조립 → 카메라 접근만 허용. 실험중 → 모든 모터 및 카메라 접근 불가.
이는 Piezo stage인 ASI 컨트롤러를 포함하는 내용 (ASI와 다른 모터를 구분하여 권한 두지 말것)."*

| rig state | motors (PI translation · rotor · magnet) | **ASI piezo stage** | camera |
|---|---|---|---|
| **분해 — disassembled** | ✅ allowed | ✅ **allowed, exactly like any other motor** | ✅ allowed |
| **조립 — assembled** | ⚠️ **ONLY through `tools/motor_gate.py`, inside the safe-motion envelope** | ⚠️ same gateway, same envelope | ✅ allowed |
| **실험중 — experiment running** | ❌ | ❌ | ❌ |

- **The 조립 row was ❌ ❌ until the user amended it on 2026-09-17 evening** (*"조립 상태에서도 이 범위 안이면 모터
  허용함"*, after *"실험 1차로 끝났는데, 리그는 유지되는 중"*). The later statement NARROWS rather than widens: motors
  and the ASI are reachable while assembled **only** through the single gateway `tools/motor_gate.py` and only
  inside the safe-motion envelope (PI magnet 0–39 mm · ASI x/y inside the `SL`/`SU` limits the user set AT THE RIG on
  2026-09-18 15:2x — live position **±2 mm**, never homed · ASI z free). ⚠️ **The numbers live in `STATUS.md`'s
  hardware banner and in `tools/bench/motor_limits.json`; never restate them here.** This line said "≤ ~1 mm from the
  anchor" until 2026-09-19, when `doc_ingest` measured it against the banner's absolute `SL`/`SU` values (a 4.0 mm-wide
  window in each axis) and the cycle-41 judgement session resolved it the same way rule 1b was resolved on 2026-09-18:
  the later user statement wins and STATUS was the one that was right,
  **conditional on that envelope being really enforced as refusing code**. The envelope says what is SAFE, not when
  motors are allowed; the rig state still decides that. Numbers and the gate's live-move evidence:
  `STATUS.md` hardware banner. Resolved 2026-09-18 by the cycle-18 judgement session after `doc_ingest` reported
  this row contradicting STATUS.md — later user statement wins, and STATUS was the one that was right.
- **Never give the ASI its own rule again.** The old carve-out ("the one instrument that can physically break the
  rig", the 2026-09-13 permission conditioned on the piezo being *detached*) is **retired**. Permission is decided
  by the rig's state, not by the instrument's identity — when the rig is apart there is nothing to collide with.
- **CONTROLLER LIMITS ARE SET AT EVERY CYCLE START AND RELEASED AT EVERY CYCLE END, BY THE RUNNER, EACH VERIFIED BY READBACK** (user, 2026-09-23: "훅으로 묶어서 매 사이클마다 시작할때는 묶고, 종료시에는 풀고. 그 다음 각 싸이클 시작 및 종료 시점마다 제대로 리밋 셋팅 되어있는지 확인하도록"). `cycle_runner.py` `motor_limits_hook` runs `motor_gate.py --session start` before and `--session end` after every cycle; a start that does not verify stops the runner before the cycle, an end that does not verify stops it after and writes STATUS. In 실험중/unknown state nothing is sent and the skip is logged. **SESSION START = A REAL REFERENCE MOVE FIRST, THEN A COMMANDED-vs-READBACK CHECK, RETRIED UP TO 3× (user, 2026-09-23 after the near-miss: "반드시 싸이클 시작할 때는 PI 모터 원점 복귀 반드시 시킨 후에 실제 좌표와 아웃풋 좌표 비교하는거 반드시 만들어" · "원점 복귀하여 복원 시키고 사이클 시작한다 … 여러 차례 복원 시도해도 문제가 생긴다면 그 때는 사이클 종료"):** `motor_send_pi.ps1` limits-set now sends `SVO 1 1`, `RON 1 1`, `FNL 1` (0 = negative limit switch), requires `FRF? 1` and `POS 0`, then moves 2 mm and back and compares readback to the command within 0.05 mm; `motor_gate.session_start` retries the whole PI step `REF_ATTEMPTS`=3 times and refuses only after all fail, which is when the runner does not start the cycle. The old "reference restore" (`RON 1 0` + `POS 1 <current>`) is GONE: after a controller power-cycle the counter reads 0 wherever the stage physically is, and declaring that zero drove the magnet into the hard limit on 2026-09-23 (`tools/bench/pi_testmove_20260923e.log`, ERR 216). Why: `--session start` was run once on 2026-09-18 and `--session end` never, so the limits sat on the controllers for five days and had to be released by hand before an experiment (`tools/bench/motor_session_end_20260923.log`).
- **MOTOR GRANT 2026-09-24 (user: "당분간 내가 말하기 전까지는 모터 접속 허용함. 다만 원점 확인 및 모터 리밋, 두 가지는 꼭 확인 필요"):** while it stands, motors may be driven by the gate and by a RUNNING MAIN VI with the rig assembled — a newly assembled main VI's acceptance test IS a real run ("이제 메인 vi 조립시에는 실제 작동시켜야 할테니 그대로 해볼 것"); recorded-frame replay is used only when a real run cannot answer. The two checks are never skipped (session-start reference + verify, limits set/released with readback). **EVERY CYCLE ENDS WITH LabVIEW CLOSED AND VERIFIED GONE** ("사이클 종료하고서는 제대로 LabVIEW 끄는것 잊지 말것, 특히 카메라가 계속 Acquisition 하면 기계에 좋지 않으니") — `cycle_runner.py` end hook, mechanical. The grant ends only when the user says so.
- **Only the user announces a state change**, and the announcement is the boundary. Never infer a transition from
  silence, from a quiet period, or from how long a session has run.
- **Do not ask per incident** inside a state the user has already declared (*"Don't need to hastle around me
  before I tell you."*). Re-requesting permission each session is the error.
- While **disassembled**, hardware measurement is expected work — true VISA/serial latency, the per-frame cost of
  motor reading, the rotor negative-angle check on `SetCommand_signed.vi`. It is cheapest now and expensive after
  reassembly, so it is not deferred to "a supervised session".
- **The rotor is SIGNED — the new VI uses `SetCommand_signed.vi` and follows the hardware number, sign included**
  (user, 2026-09-16: *"로터는 본래 부호 인식이 가능했으나 랩뷰 시리얼 통신에서 부호 인식이 안되는 문제가 있었음.
  이제는 해결 방법을 찾은 것 같으니 부호를 포함하여 하드웨어 숫자 그대로 따라가야함."*). The unsigned
  `SetCommand.vi` was a workaround for a serial-path defect, not the rotor's nature. "해결 방법을 찾은 것 **같으니**"
  — the sign round-trip on the real link is still to be measured while disassembled, not assumed.
- Superseded and not to be reinstated from an old summary: the 2026-08-27 blanket motor ban
  (*"우선 모터 가동은 절대 하지 않는 선에서 계속 처리해"*) and the piezo-detached condition.

The realistic hazard remains a VI run as a side effect: LabVIEW's broken-arrow and Run buttons are the same
pixels — check the arrow state or use menus before clicking that toolbar region on any VI that can reach an
instrument.

## 1c. No serial on the frame path — the user's data-quality constraint (2026-09-16)

*"I don't want to have even a single frame loss coming from the motor communication if possible. And it is so
clear that serial communication through VISA can somehow stall the loop, and cause unwanted frame stop."* And the
fact behind it: the sample stage **drifts on its own** (thermal drift, the sample-holder pin shifting, causes the
user cannot name), so **focus re-adjustment is continuous, not rare** — "I can't tell how frequent it is, but it
is not trivial."

So the constraint is structural, not statistical: **no VISA/serial call may sit anywhere on the frame acquisition
path.** A mechanism that *can* stall the frame loop is disqualified even if it usually does not. Serial lives in
its own loop, owns its VISA session exclusively, and reaches the frame path only through a non-blocking handoff.
Any argument of the form "the serial branch is conditional, so it is cheap on average" is refuted at the premise.

## 1c''. Loop-to-loop CONTROL signals travel by LOCAL VARIABLE (latest value), never by queue; the focus loop runs on its own clock (user, 2026-09-25)

*"큐를 넣어버린다면 두 루프 사이에 상관관계가 생겨버린다 … 그런 리스크를 감당할 필요가 있는지 모르겠음. 그냥 Boolean 값 및
타겟 값을 local variable로 전달하는게 더 좋지 않을지? ASI autofocus 루프는 애초에 frame acquisition 루프와 동시에 돌
필요가 없을듯."* A queue couples producer and consumer (backlog, timeouts, shutdown order); a local variable does not —
the writer never waits and the reader sees the latest value. So: **control / trigger signals between loops (focus
requests, setpoints, enable flags, counters) are locals; queues are for lossless DATA streams only** (the file writer's
results FIFO, master plan 1.7). **Never detect an EDGE on a polled boolean** (that is what produced STATUS OPEN 58's
three autofocus limits); publish a value the reader can compare (a counter, a position).

**Autofocus — the user's account (2026-09-25) and what the code MEASURES:** the user remembers a distance-threshold
trigger on the **first-clicked reference bead**; the offline read of Case `#10407` (`docs/autofocus-case-10407.md`,
card chat-F1) shows NO threshold: every firing (every 25 frames, `camera-acquisition-facts.md:255-270`) moves the axis
by `clamp(idx_bead0 − slices/2 + 'Focus Deviation from the Center', ±0.2)` — a proportional correction with an
additive setpoint OFFSET, on bead index 0; `Focus Step (F1)` is not read there; the `In Range?` node is unwired.
**Rule 1a decides: the redesign copies the CODE, not the memory.** A threshold trigger would be a new feature and
needs the user's separate decision. The user does not run with `Frame rate` = 1. DESIGN IN FORCE for the focus loop
(after M3, `docs/connectivity-map-plan.md` Pre-decided 190 — renumbered 2026-09-25 from 148, which clashed with `d1-loop12-17-split-plan.md`): frame loop publishes the reference bead's z and the
auto-reset counter as locals; the focus loop runs on its own time cadence, reads them, applies the original's
correction arithmetic (offset, clamp ±0.2, bead index 0) under `Auto-Focus` / `Limit of Auto-Focus`, and moves — no
schedule boolean in the frame loop, no edge detection, no queue. Scheduling changes; the arithmetic does not (rule 1a).
Mechanical: `tools/stage_prerun.py` refuses a stage plan that creates a queue primitive for a control signal or
wires a boolean into a shift-register edge detector across loops (`control_path_lint`).

## 1c'. Test runs are UNATTENDED until the rig is reassembled — the harness clicks the beads itself (user, 2026-09-17)

The main VI runs as: panel parameters → device configure → **a while loop that waits for mouse clicks on the live
image (first = reference bead, rest = magnetic beads)** → **a button** that ends it and runs bead-profile
calibration → the experiment loop. Nobody present ⇒ it stalls in the picking loop. The user's requirement:
*"리그 조립 전까지는 내가 없는 환경에서 돌리기를 기대함 … 몇십번이고 돌려야 할테니 … 밤 시간동안 하네스 루프
돌리며 개발 하기를 기대함."* Their choice of mechanism, **option 1**: *"직접 마우스 움직여서 디스플레이 상에 클릭
이후 버튼 누르기 → 저장 위치 및 저장 이름 쓰기"* — i.e. scripted GUI clicks on the image display, the done
button, and the save-path entry, through `tools/lv_gui.ps1` with `-Exception Approved -Evidence "user 2026-09-17
bead-pick option 1"`. A `.cal`-loading substitute VI (option 2) was **rejected**. *"Bead가 없는 상황에서 트래킹
에러가 분명히 생기겠으나, 디바이스 통신 및 프레임 체크 용도로는 무리 없을 듯"* — garbage tracking output in a
no-bead run is not a failure. **GPU path first; CPU afterwards** (re-affirmed the same day).

## 1d. The main VI is in scope — read-only, and read it when meaning requires it

(User, 2026-08-30: examine the main VI when the situation calls for it; effort belongs on
*semantic* analysis.) Never modify, never save; prefer **headless COM reads** over editor windows.
**Read nested structures properly** — a flat strings dump once made calibration-cluster *fields*
look like ignorable stray controls.

## 2. LabVIEW is shared with real experiments — be interruptible at any point

The user may forcibly stop a session at any moment to reclaim LabVIEW. Keep `STATUS.md`'s state
current **during** work — after each real milestone, not just at session end. Treat "the user might
vanish right now" as the normal case.

### 2b. The user's messages during work are interrupts — answer first, then continue

(User, 2026-08-27; re-issued 2026-08-28 after a compaction let it fade; re-issued 2026-09-04
"전체 세션을 돌더라도 항상 응답 즉각적으로 할 수 있게 규칙 잡지 않았었나?".) A user message that
arrives mid-turn is answered in the **very next reply, first line, before any tool call** — a
progress line ("지금 ~ 확인 중") is not an answer, and a yes/no question gets its yes/no in the first
sentence, explanation after. Stop or redirect the running work if that is what the message implies.
Background anything slow; prefer short checkable steps to long chains. Re-read this whenever the
session is summarized.

## 2c. Once a cycle is turning, RUN IT TO THE END — do not pause it to ask (user, 2026-09-16)

*"한 번 루프 돌기 시작했을 때, 꼭 필요하지 않다면 중간에 멈추지 않고 끝까지 루프 계속 진행했으면 좋겠음.
규약에도 갱신하면 좋을듯."* Said after a session stopped mid-cycle to put a genuine question to the user — a gate
was blocking the build over a date-comparison bug — while other work in the same cycle was still runnable.

**The default is: finish the cycle, then report once.** When something is uncertain mid-cycle: (1) do every part
that does not depend on the answer, all of it; (2) for the part that does, **write the assumption down, proceed
under it**, and flag it in the closing report so the user overturns one thing rather than unblocks ten; (3) stop
only when proceeding under *any* assumption would be unsafe, destructive, or would make the work useless if wrong.

This is about **where the waiting happens**. A question asked mid-cycle makes the user the scheduler; the same
question in the closing report lets them answer whenever, with the finished work already in front of them. It does
not weaken 2b — their messages arriving mid-work are still answered in the very next reply, first line. Claude
stays responsive to the user; the user does not become responsible for keeping the cycle moving.

## 3. Autonomous progress protocol

**Start/stop is explicit, never inferred** — the user says start ("지금 진행해") and stop ("멈춰");
silence is NOT authorization. Maintain the lock block in `STATUS.md` (acquired ↔ released) so any
future session can tell at a glance whether LabVIEW is safe to touch:

```yaml
labview-lock:
  status: released   # acquired | released
  owner:
  since:
  purpose:
```

- **GUI only where scripting is VERIFIED unreachable** (user, 2026-08-31: "GUI 활용은 script로
  도달 불가능한 경우에만"). **Mechanically enforced**: `lv_gui.ps1` refuses state-changing actions
  (click/rclick/dclick/drag/wire/keys) without `-Exception VerifiedImpossible|NegativeSearch|Approved`
  plus `-Evidence <record>`, and logs every authorized one to `tools/gui_actions.log`. The
  verified-impossible list (skill; currently 2 entries) names operation CLASSES — each concrete use
  must also show no scriptable alternative construction exists. Cost/time is never a reason. Known
  laundering patterns to refuse in review: a too-narrow "negative search", "only opening it to
  look", and plan clauses like "via GUI if needed" (every GUI act must be individually enumerated
  in the peer-reviewed plan). One execution path at a time.
- **Failed batch ⇒ RECOVERY_LOCKED** (peer-reviewed design, 2026-08-31,
  `archive/peer/...gui-rule-hole-analysis-review.md`): when a scripted batch hits an unpredicted
  result, state-changing GUI is OFF; only diagnostics (screenshots, window lists, reporter reads,
  Esc) are allowed. Produce a recovery packet (prediction, observation, evidence, competing
  explanation, cheapest discriminating test), get a **successful** peer review (a timeout/quota
  failure is not a review), then resume as a NEW batch — never by continuing the failed one
  interactively. Recipes must state their prediction contracts (expected counts/states/tolerances)
  before execution so "failed prediction" is machine-checkable.
- **Save authority**: files under `user.lib\claudeDev` may be saved autonomously. Never originals.
- **Restart authority** (user, 2026-08-29: "재시작 항상 오케이"): restart/kill LabVIEW when it is
  the right fix, no per-incident approval; save valuables to disk first.

### Reference hygiene — close every reference, and PROVE it by handle count (user, 2026-09-06)

("이후 close reference 필수로 사용하도록 하고, 규칙에 확실히 규정할 것. 그리고 해당 규칙이 반영되는지
검증." — after LabVIEW turned sluggish/'응답 없음' at 32,480 handles following ~30 h of scripting.)

1. **Every VI Server reference is closed by whoever opened it**: op VIs wire `Close Reference`
   on every ref they create (Open VI Reference, Traverse arrays, Get Outputs, New VI Object,
   creator outputs); Python releases cached VI references on exit and never abandons a COM call
   (a killed or hung client keeps its references alive inside LabVIEW).
2. **Measured, not assumed**: `tools/bench/handle_audit.py` attributes handle growth to operation
   types; `bench_prep.py` reads LabVIEW's handle count before every batch and restarts the
   instance above `HANDLE_LIMIT` (mechanical, standing restart permission). A new op is accepted
   only if 20 runs leave the handle count flat (±100). **Baseline: this LabVIEW 2026 install holds
   ~31,500 handles one minute after a fresh start** (measured 2026-09-06 04:16) — the first
   "32,480 = leak" diagnosis was WRONG; judge growth relative to that baseline, never the absolute
   number. Responsiveness itself is measured directly with `lv_gui.ps1 -Action ping`
   (SendMessageTimeout latency per window: the metric behind '응답 없음').
3. Any batch that must kill a client (deadline) is followed by a handle read; a jump is logged as
   a non-result and the instance restarted before the next batch.

### Usage-limit protocol (user, 2026-09-04)

("만약 중간에 이용한도가 꽉 차면 (95% 초과할 것 같으면) 리뉴얼 시점보다 2분 이후로 일정 예약
걸어두고 하던 작업 이어가도록. 벤치 중간에 멈췄다면 해당 벤치는 다시 돌리도록.")

1. **Detect.** Before each long unit of work (a benchmark cell, a batch build) check the usage
   readout if one is available; a usage/rate-limit error is the reactive trigger. Never assume the
   quota is fine because nothing complained.
2. **Schedule, don't wait.** At ~95 % or on a limit error, read the renewal time from the limit
   message and schedule a wake-up at **renewal + 2 min** (session wake-up for ≤ 1 h, a scheduled
   task otherwise). Write the resume point to `STATUS.md` first. Do not end the turn with "resume
   me later" — the schedule is the resume.
3. **Rerun, don't resume.** A benchmark cell or build interrupted mid-run is invalid: after the
   wake-up it is rerun **from the beginning** and the partial attempt is logged as a non-result
   (which cell, when, why). Half-run numbers never enter a results table.
4. **Never wait on a user turn** for something a script can do (registering definitions, restarting
   a tool, re-queuing a cell). If a route needs the user, say that in one sentence and build the
   scripted route.

### Reports reach the user THROUGH THE CLAUDE SESSION — the user is remote (user, 2026-09-25)

*"보통은 내가 원격으로 러너 확인 및 지침을 줌. 그러니 클로드 세션으로 확인 필요함. 훅 경로 변경하도록."* A Windows toast,
a local file or a session-only timer (CronCreate, ScheduleWakeup — both failed silently, 09-23 and 09-25) is not a
report. Path in force: (1) `cycle_runner.py` writes `HEARTBEAT` at every cycle end and at RUNNER STOP
(`tools/bench/heartbeat_latest.md`, mechanical, no model); (2) the app-level scheduled task `runner-cycle-report`
(`~/.claude/scheduled-tasks/runner-cycle-report/SKILL.md`, every 30 min, survives session changes, runs while the app
is open) turns new events into a Korean report (`tools/bench/reports/`), acks `report_gate`, and its completion
notifies the main chat session, which relays the report verbatim and calls `PushNotification` (phone when mobile
push is on); (3) `tools/hooks/report_gate.py` still blocks the chat's turn on unreported events when the user speaks
first. Open user decisions (`tools/bench/decisions_pending.json`) are part of every report.

### Unattended runs: silence is not progress (2026-09-05) — now mechanical

A log monitor only reports what a live process writes. Two mechanisms replace attention:
(1) `tools/hooks/guard_bash.py` refuses any backgrounded LabVIEW command unless it runs through
`py tools/bgrun.py --max-min N --log <file> -- <cmd>`, which kills the process tree at the deadline
and always writes a final `BGRUN END|TIMEOUT` line; (2) gscript's `_run/_invoke` watchdog caps
Run/Invoke calls; an attempt to route GetVIReference/SetControlValue through the same thread
(`tools/gscript.py.guarded_attempt_20260905`) itself blocked in cross-apartment marshalling and was
rolled back — the PROCESS-level deadline of bgrun is the guarantee, not per-call guards. (User, 2026-09-05: "Timeout 검사에서 우회된 내용이 있는 것 같은데 규칙 개선
필요할듯", after a background job hung 3 h 48 min.) Original prose rule kept below for the why.

A log monitor only reports what a live process writes; a driver that dies writes nothing, and the
session sat 2.5 h believing a benchmark was running. While anything unattended runs, schedule a
heartbeat (ScheduleWakeup / cron, ≤ 30 min) that checks the process list AND the log's age, and
treat "no new line for longer than one cell" as a failure to diagnose, not as waiting.

### Usage discipline — fewer turns, one cycle per session (user, 2026-09-14: "턴수 줄이는것 해보고 주기적 컨텍스트 정리도 적용해보자")

The user found Fable usage burning "말도 안되게 빠른" after a 13-hour session. The burn is **turns × context**: every
background notification is a full turn over the whole conversation. Standing rules:

1. **One LabVIEW batch = one runner = one notification.** Chain build → test → archive/INDEX bookkeeping into a single
   Python runner under one `bgrun` (as `build_opqueue_all.py` does); never a build turn, then a test turn, then a doc
   turn. Dispatch the mandatory peer review AND prepare the fix in the same turn; read logs with a targeted grep, not
   whole files; never re-read what is already in context.
2. **Session = one cycle.** Start a session by reading STATUS.md and the cycle's plan document only; end it by writing
   STATUS's "Next" line and stop. Do not carry a second cycle in the same session — start a fresh one (the layered docs
   exist for exactly this cold start; a fresh session beats compacting a long one).
   **ENFORCED BY A RUNNER — user decision 2026-09-17 ("2번으로 가자. Opus max"), after a 15-hour session:** cycles are
   not started by a person and not continued in a chat. `tools/cycle_runner.py` loops: spawn a fresh `claude -p`
   judgement session (**Opus, effort max** — not Fable; **AMENDED 2026-09-23 by the user: `claude-opus-5-5` pinned by id at effort HIGH** — the Artificial Analysis index shows high→max = +4 points at 3.3× cost (news.hada.io/topic?id=34142); hypothesis reviews max→high, priorart 5.5/medium, material 5.5/medium, log-reader 5.5/low — **re-set 14:xx to the table the user approved ("오케이 테이블대로 반영하자") after the measured fact that Opus 5.5's effort scale differs: its medium scores as Opus 5's max on the Artificial Analysis index and is its default (platform.claude.com/docs/en/build-with-claude/effort); judgement = medium**; the alias `opus` resolved to `claude-opus-5` and is no longer used, so a later alias change cannot silently move the comparison baseline; needs Claude Code ≥ 2.1.280) that reads STATUS.md + the current plan only, runs ONE cycle
   (delegate → decide → retrospective → STATUS NEXT), exits; the runner checks the exit and NEXT and spawns the next.
   Runner stop conditions: a `STOP` marker in STATUS.md (written by the user), the same failure two cycles running,
   the usage-limit rule (renewal + 2 min). `tools/hooks/guard_session.py` (PreToolUse Agent) refuses material
   dispatches after the retrospective has run in that session and above 8 dispatches per session. **The interactive
   chat is for talking with the user only** — it answers from STATUS and the latest retrospective and redirects the
   runner by editing STATUS NEXT/STOP; it never runs a cycle itself. Every cycle plan carries a `## Pre-decided`
   section (decisions material sessions apply without asking; `doc_lint` warns when it is missing).
   **FIREFIGHTER cycles (user, 2026-09-18: "기존 구조로 처리가 잘 안되는 부분은 Fable, low로 소방수 파견" · "단순히
   판단만으로는 부족" · "트리거링 걸리면 발동하도록" · "Low로 첫번, 그 다음 middle로. 그래도 안되면 나한테 판단
   요청").** The runner itself decides, from bgrun logs, never a session or a person: when the SAME recipe
   (`tools/recipes/<name>.py`, in command position) ends `BGRUN END rc≠0` / `TIMEOUT` in TWO CONSECUTIVE cycles,
   — **or the SAME MISTAKE under another name** (user, 2026-09-18: "동일 실수 반복하는 것도 판단 조건에 들어가야"):
   the same first failing GATE line (uids stripped) in two consecutive cycles even if the recipe was renamed
   v1 → v2, or a retrospective archived in the cycle carrying `VIOLATION: repeated-failure-class` —
   the NEXT cycle runs as a whole cycle on **fable / low** (so it can execute, not only advise; it may patch and
   run the recipe itself with `MATERIAL=1`). If the same recipe fails again → the next cycle is **fable / medium**;
   if it fails a third time → `RUNNER STOP`, the user's judgement is requested; there is never a third
   firefighter. Every other rule (1, 1a, 1b, no new process device, peer review, retrospective) holds inside a
   firefighter cycle. The user may also order one directly (`--firefighter <recipe>`, first cycle only, as on
   2026-09-18 12:59). Self-test: `tools/bench/selftest_cycle_runner_ff.py` (2/2).
   **A DEADLINE ENDS THE RUNNER BETWEEN CYCLES, NEVER MID-CYCLE (user, 2026-09-21: "그냥 셧다운 하지 말고 진행 작업들 마무리하고 종료하는 방향으로. 그래야 다음 싸이클에 정상적으로 작동하지").** `cycle_runner.py --budget-min` (default 480) is checked only between cycles; the cycle in progress always finishes (retrospective landed, NEXT written, git committed). The `bgrun --max-min` around the runner is the LAST RESORT and is set well above budget + the longest cycle (≈3 h), e.g. `--max-min 720`. A hard kill mid-cycle left a failing log with no review and deadlocked the next launch on 2026-09-21.
   **`## NEXT` IS WRITTEN BEFORE THE RETROSPECTIVE IS LAUNCHED — MECHANICAL (user, 2026-09-21: "NEXT 작성하도록 훅에 강제할 필요성 있을듯").** The runner snapshots the NEXT section's md5 before spawning a session (`tools/bench/next_snapshot.md5`); `guard_bash.py next_gate()` refuses `retrospective.py` while NEXT still hashes the same. Sessions 58/64/65/66 exited waiting on their retrospective with NEXT unwritten, and the chat rewrote it four times.
3. **Split sessions by JUDGEMENT vs MATERIAL — ADOPTED 2026-09-15** (user, after comparing token costs directly:
   *"정말 필수적으로 고차원적인 판단이 필요한 경우에만 Fable 사용하고 Fable이 판단할 재료들은 opus 혹은 하위 모델로
   세션을 잡는게 거의 필수처럼 보이는데?"* — Opus at high effort is far cheaper than Fable at low). Note this INVERTS
   the direction sketched here earlier: the scarce model is spent ONLY on judgement, and Opus is the
   **material-preparation** tier, not a lower one — that is where most wall-clock time goes.
   - **MATERIAL** (its own session, Opus high by default): measuring API facts (property short-name censuses, class
     hierarchy, a VI's terminal names), writing/running recipes that follow an already-verified pattern, log greps,
     INDEX/NAMES/STATUS bookkeeping, dispatching peer reviews and collecting their answers, and extracting the bare
     facts from a failed run (which gate, which values).
   - **JUDGEMENT** (the scarce model; Opus max while the Fable budget is out): design decisions, what to accept from a
     review, rule-1a calls, diagnosis when hypotheses genuinely diverge, and designing the discriminating experiment.
   - **Failure budget = 2.** A material session that fails twice STOPS, writes the logs and state down, and hands the
     problem to a judgement session. (`OpCaseFrames_v0` looked closed-spec and failed five times — grinding is more
     expensive than the judgement it avoids.)
   - **Judgement sessions stay SHORT**: STATUS.md, the relevant plan document, and a summary of the failing log —
     nothing else. A judgement session at 78 % of its context window defeats the whole point.
   - **RE-ISSUED 2026-09-16, after the subscription was upgraded — the upgrade does NOT relax this:** *"Fable의
     사용량을 최대한 줄이고, 필요하다면 하부 세션을 늘려서라도 opus 비중을 높이는 게 좋음."* Minimise Fable
     unconditionally; **spawn more Opus sub-sessions rather than do material work in a Fable session.** The moment
     a judgement session is about to write a recipe, read a long log or patch a wrapper, hand off. (Trigger: on
     2026-09-16 one Fable session did an entire cycle — recipes, log reads, a 26-wrapper patch — in one context.)
   - **The hand-off is mechanical — two agent definitions (user, 2026-09-16 "에이전트 정의 먼저"):**
     `.claude/agents/material.md` (Opus high: writes/runs recipes and diagnostics, patches tools, dispatches
     peers, keeps STATUS; returns a ≤30-line fact summary; failure budget 2) and `.claude/agents/log-reader.md`
     (Opus low, read-only: which gate, which values, which line; ≤25 lines). **A judgement session spawns these
     via the Agent tool and never runs `tools/recipes/*.py` or `tools/bench/*.py` itself, never reads a whole
     log itself.** The judgement session's turns are three kinds only: read STATUS + plan, decide, delegate.
   - **A delegation brief states the MEASUREMENT, never the result-dependent ACTION** (2026-09-16, after the
     user asked whether a judgement session fed ≤30-line summaries can still judge). Writing "if A2 removes 1
     do X, else do Y" into a material brief is not delegation — it moves the decision into the session that
     is not supposed to make it, before the evidence exists. The material session measures, returns FACTS and
     an `OPEN:` line, and stops; the judgement session decides and delegates again. One extra sub-session is
     the intended cost. The retrospective asks, per cycle, whether any decision was taken inside a material
     session that belonged to judgement — slug `judgement-in-material`, counted by `violations.py` like the
     others. The judgement session may always ask `log-reader` for more; ≤30 lines is a default, not a cap.
   - **Reports the user reads are WRITTEN BY CODEX, not by Claude** (user, 2026-09-16: *"보고는 검수를 받는게
     아니라 그냥 chatgpt cli에 의존하는게 좋을 것 같은데? 그냥 클로드와 코덱스는 문체가 달라."*). For any
     paragraph-length report, summary or decision request, Claude hands `.claude/agents/reporter.md` a **fact
     list** (numbers, paths, gate outcomes, the question) and shows that text as-is (`peer.ps1 -Kind prose`,
     archived under `archive/prose/`, invisible to every gate). ⚠️ **From 2026-09-18 the writer is `claude
     -Role prose` = fable/low with a THIN prompt (`--safe-mode`), not codex** (§5, "Codex's roles move to Claude
     sub-sessions"): the rule exists so the report is not in this session's sentence shapes, and a cell that never
     loads this project's rules or context is not this session. Codex stays at `-Agent codex -Kind prose`.
     **The dispatch is run by the judgement session
     itself, in the FOREGROUND, not by a sub-agent** (2026-09-17, user: "어떻게 하면 같은 일을 막을 수 있을까"):
     twice a `reporter` sub-agent backgrounded the call and returned, and its exit killed the child before codex
     had written a line. The relay is one file write and one ~60 s wait; `guard_bash.py` allows exactly that
     shape (`-Kind prose` under bgrun, foreground timeout ≤ 6 min), and it costs no sub-agent tokens. Claude still writes one-line answers (rule 2b),
     short status lines and questions of a sentence or two. A proofreading variant was tried first and
     rejected the same day — rewriting Claude's sentences keeps Claude's sentence shapes.

### MODEL LADDERS, decided by the runner from files (user, 2026-09-26)

*"지금 3일 안에 사용량 다 써야하는데, 당분간 Fable 5.1 low 사용빈도를 높여보는 건"* · *"판정 세션은 필요에 따라서 medium
상위 혹은 fable로 교체하는 것도 생각해보는게 어떨지"*. Two ladders, both mechanical (`tools/cycle_runner.py`), nobody
"feels" a level:
- **Material sessions:** default **`claude-opus-5-5` HIGH** (user "승인" 2026-09-26 13:0x, on the replay bench
  `tools/bench/matbench/report_v1.md`: 5 replayed cards x 2, low 5 / medium 7 / high 8 / max 9 of 10 at $8 / $11 / $15 /
  $33 and 1.1 / 2.0 / 2.6 / 7.6 min; effort changed the score only on the uid-precision check (high, max) and on "report
  the missing verb" (max only)). Intra-cycle escalation rungs: Opus max -> Fable low -> `decisions_pending`. The
  "Fable low until Monday" trial (cycles 89-91) was ended early by the user: 3x cost, no more deliveries, same failure
  classes; a live-cycle cost comparison is context only, the replay bench decides (user: "재료 세션이 사실 판단 및 생성까지
  관여하잖아 … 적절한 테스트가 필요").
- **Judgement sessions:** level 0 `claude-opus-5-5` medium → 1 Opus high → 2 Fable low → 3 Fable medium → RUNNER STOP
  + decision item. Up one level when the last cycle left `next.json` UNCHANGED or its retrospective named a
  judgement fault (`inference-over-measurement`, `wrong-ordering`, `judgement-in-material`); back to 0 after a cycle
  that delivers. The recipe firefighter (fable/low on a repeated recipe failure) stays; the two never stack above
  Fable medium. The level and its reason are a `JUDGE-LADDER` runner-log line and a field of the cycle card.
- **Judgement effort A/B until Monday** (user, 2026-09-26: *"Opus 5.5도 기본을 medium이 좋을지 high가 좋을지도 판단
  필요"*): no cycle so far ran judgement at high, so there is no basis to choose; `cycle_runner --judge-ab` alternates
  level-0 effort by cycle parity (odd medium, even high, `JUDGE-AB` log line, `effort` in the cycle card; a triggered
  ladder level overrides it) until 2026-09-28 07:00, and the Monday comparison (minutes, cost, deliveries, judgement
  slugs, unchanged-NEXT count) sets the default. External prior: Artificial Analysis index Opus 5.5 medium 51 / high
  54 at $1.34 / $1.82 per task.

### INTRA-CYCLE ESCALATION — a card that runs out of budget goes to Opus max, then Fable low, then to the user (user, 2026-09-25; rungs re-set 2026-09-26 on matbench v1)

*"한 싸이클 내부에서도 특정 프로세스가 과하게 오래 걸리거나 반복적으로 실패할 경우 Fable 5.1 낮음 (그래도 안된다면 Fable
5.1 중간) 높여보는 것이 유효할지"* — asked while cycle 85 spent 105 min building two missing verbs on Opus. The
cycle-level firefighter (fable/low after two failing cycles) already exists; this is the same ladder inside a cycle,
per card. Trigger: a `task/1` card returns FAIL with its failure budget spent, or exceeds `budget.minutes`. Rung 1:
re-issue the card (`escalation: 1`, `retry_of_card`) to `.claude/agents/material-opus-max.md`; rung 2: `escalation:
2` to `material-fable-low.md`; then `decisions_pending.json` and stop. (Rungs were Fable low -> Fable medium until
2026-09-26; re-set by the user on matbench v1: max alone reported the missing verb, Fable low 5/5 at half of max's
minutes, Fable medium no gain over low.) Two rungs per card, same flags, rules and
peers; the result card carries `escalation`, so Opus-vs-Fable outcomes accumulate as data. Evidence so far: cycles
71/72 (fable/low) delivered L7-1b after two Opus failures. This does not relax the standing rule to minimise Fable —
it bounds it to a card that Opus has already failed twice.

### Every cycle ends with a RETROSPECTIVE — the peer loop cannot criticise judgement otherwise (user, 2026-09-15)

(User: *"피어 리뷰를 통해 판단 및 실행 구조에 대한 비평은 할 수 없는 것 같아."*) The hypothesis-level reviews all
pass and the cycle still goes badly, because a peer only ever sees a framing Claude wrote about a failure Claude
chose. Nobody asks whether the question was worth asking, whether twenty failures were one failure, or whether a
tool should have come first. So the cycle itself is reviewed, from the machine's record rather than from Claude's
summary:

1. `py tools/audit_cycle.py` — mechanical compliance, no judgement: bgrun discipline, every run terminated, every
   failing log followed by an archived review, every review annotated, the originals untouched, GUI actions
   recorded — plus the cost lines (builds, failures, wall-clock) the retrospective argues about.
2. `py tools/retrospective.py --cycle N` — **v2, ADOPTED 2026-09-16** (v1 frozen at `tools/retrospective_v1.py`,
   kept runnable for the comparison only; measurement in `tools/bench/retro_v2_comparison.md`). It dispatches a
   FIXED question set (repeated failure · missing tool · inference over measurement · rule compliance · ordering ·
   what was not reported · judgement inside a material session) plus a DEVICE EFFECT question built mechanically
   from `docs/violation-decisions.md`, with the audit output, the cycle's build logs and CLAUDE.md attached.
   Claude does not write the questions and does not choose the evidence. v1 SATURATED — cycles 11/12/13 fired 9/9/6
   slugs; v2 fired 2/2/1 with three different top faults.
3. **v2's output contract:** the peer names the **ONE most costly structural fault** (at most two), everything else
   is prose FINDINGS with no slug, `VIOLATION: none` is a legitimate and expected answer, and each named fault
   carries `loss_min`, `loss_usd` (or `?`) and a clock counterfactual:
   `VIOLATION: <slug> | loss_min=<n> | loss_usd=<n or ?> | evidence=<file:line>`. Slugs come from the known list
   (`repeated-failure-class`, `tool-not-built`, `inference-over-measurement`, `rule-evaded`, `wrong-ordering`,
   `unreported-fact`, `scope-creep`, `premature-build`, `judgement-in-material`, `device-failed` — the last two
   added 2026-09-16; `device-failed` has **threshold 1**, because a device that let its own fault through is broken,
   not unlucky). `py tools/violations.py` parses both v2's form and v1's bare `VIOLATION: <slug>` and counts them
   **across retrospectives, from the files**
   — because "add a device when it repeats" is worthless if Claude is the one counting (the user's question:
   *"회고가 반복해서 위반을 지적하는지는 어떻게 알아?"*). **At 3 of the same slug the next cycle must build the
   mechanical device for it first.** Only the user may lower that threshold. ✅ **THE 2026-09-18 NO-NEW-DEVICE ORDER IS LIFTED (user, 2026-09-24 03:1x: "새로운 도구 만드는 걸 내가 막아뒀는데, 보니까 계속 구멍이 생기는 것 같아. 루프 판단에 따라 필요한 도구는 만드는 걸 허용할게") — after cycle 68 lost ~25 min to two missing scripting verbs (wiring to a loop's `i` terminal; no creator for `Not Equal?`/`Select`) and routed around them. A cycle's JUDGEMENT session decides a tool is necessary (it unblocks the stage, or the same class of work will need it again) and a material session builds it in that cycle, under every existing rule (peer-reviewed plan, stagekit, handle-count hygiene, measured before it acts). Deliverable-first ordering still holds: the tool is built because the deliverable needs it. The threshold below resumes with the same words; the suspension text is kept for history.** ⚠️ **(HISTORY) SUSPENDED since 2026-09-18
   08:53** by the user's standing order (*"장치는 더 민들지 말고 계속 진행"*, **user, 2026-09-18 08:53** — cited by
   DATE, never by a STATUS line number, which every relocation moves): while it
   stands, a slug reaching 3 is recorded as a FINDING in `docs/violation-decisions.md` and the next cycle builds
   NO device; the threshold resumes the moment the user lifts the order. **EXCEPTION (user, 2026-09-22: "Jev 건은 예외로 추가하도록 하고"): devices that put TypeSafe's Jev (a typed-decision model, `docs/jev-integration-plan.md`) behind an EXISTING decision point — the firefighter trigger, the failed-prediction review gate, log classification, plan checks — are allowed under the no-new-device order, each one MEASURED on a labelled set before it is switched on and introduced as an ADVISORY signal first.** Jev scripts (`tools/jev*.py`, `tools/bench/jev_*.py`) are EXEMPT from the failed-prediction and material gates (user, 2026-09-22 "Jev는 면제") — they touch no LabVIEW. Thresholds in force: review discharge p≥0.80 (active), firefighter veto p≤0.30 (active), triage/NEXT/prior-art advisory only. **SECOND WAVE APPROVED (user, 2026-09-22 17:3x: "훌륭하네. 이거 다 적용해보자") — `docs/jev-integration-plan.md` '2차 후보' 1~7, all of them, including the RULE CHANGE in #1: a failed prediction goes first to the JEV REVIEW LADDER (3-way: our-script-bug / already-reviewed-class / new-problem); only `new-problem` (or no key / unknown band) owes the Opus `hypothesis` review; the other two pass with a logged `JEV-LADDER` line and a citation. Each insertion is measured on a labelled set before it acts; #4 (per-command drift) and #7 (Pre-decided contradictions) are advisory; #6 (5-sample consensus) is the default for every gate call.** **ONE REVIEW PER ROW PER CYCLE (user, 2026-09-22 18:xx "전부 적용해보자", after the measured cost: reviews were 30 % of cycle time, 8 in one cycle, mostly a chain of failures on ONE stage row): a failed prediction on the SAME script (basename with `_vN` stripped) that already has an ANSWERED adversary review archived within the last 6 h is DISCHARGED by that review — `guard_peer` cites it (`RULE-SAME-ROW`), no second review is bought. A different script, or a review older than 6 h, still owes its own review. Also: the Jev drift advisory (#4) judges against the WHOLE `## NEXT`, not only its first act; the 10 Pre-decided contradiction suspects from #7 are checked and annotated, not left as a list.** **Second exception (user, 2026-09-22 "좋아. 다음 사이클에 추가하도록"): the stage-script library `tools/stagekit.py` (Pre-decided 93) — the repeated skeleton of stage/diagnostic scripts as one verified module, so a stage file is inputs only.** **BUILT 2026-09-22 16:0x (725 lines, self-test 32/0, a 595-line probe re-cut in 120 lines matched 13/13). From now on every new stage or diagnostic is a ≤120-line file on `tools/stagekit.py`; a free-standing multi-hundred-line script is the pattern the user rejected.** Resolved 2026-09-18 by the cycle-26
   judgement session after `doc_ingest` reported this line contradicting STATUS — the later user statement wins.
4. `tools/hooks/guard_cycle.py` refuses the next RECIPE build while the previous cycle's logs have no newer
   retrospective, or while a slug is at threshold. Diagnostics, docs, peers and the retrospective itself pass.

### When a diagnosis is GUESSED twice, build the reader (2026-09-15)

The sibling of "when a rule is broken twice, move it into a hook". On 2026-09-15 three consecutive `ExecState 0`
failures were diagnosed by inference — branch wire, downcast, transient Remove Bad Wires — each costing a peer review
and a rebuild, because the fleet has no way to ask LabVIEW *why* a VI is broken. Each was 3 minutes of measurement
dressed as 20 minutes of reasoning. **Rule: the second time a class of failure is explained by inference rather than
read from the machine, the next build is the READER for it, not another attempt at the thing that failed.** Readers
identified this way: **`Wire.Is Broken?` 6371004 IS BUILT** and measured (`docs/NAMES.md:902-911`, 2026-09-17) — but ONLY inside the connect ops, there is no stand-alone read-only `Wire.Is Broken?` op (STATUS 2026-09-25, `docs/NAMES.md:1081-1089`); use the connect ops' read-back instead of inferring why a wire is bad; `VI.Get Errors` (method 452) is still unbuilt and is probably unreachable over our COM path (absent from the exported `VirtualInstrument` ActiveX interface — `archive/peer/2026-09-18-fstunnel-v1-b4-execstate0-codex.md`), so it is off the critical path. Corrected 2026-09-18 by the cycle-22 judgement session after a `-Dual` review found this line stale.

### Stages are SIMULATED and PRE-RUN OFFLINE before LabVIEW touches them (user, 2026-09-24)

*"미리 사전계획 해서 옮길 vi들 미리 정리하고 만들 struct 미리 계산한 다음 그 결과 어떻게 될지 미리 예측 … Sequential하게
각 단계들을 시뮬레이션 하여 temporary 파일로 저장한 후에 각 사이클의 finalized 플랜을 두는게 맞는듯."* Said after the
loop-1.7 split failed 6 of 9 LabVIEW runs (≈49 min of LabVIEW, several times that in diagnosis) on problems that were
all knowable offline. Eight decisions; design and build order in `docs/stage-simulator-plan.md`:

1. every stage script is DRY-RUN first (COM stubbed); 2. an OFFLINE PRE-RUN (every row decided, every terminal
addressable from the graph — unwired ones by owner node → terminal list → uid echo, rows == plan rows);
3. error-cluster and accumulator chains are copied from S1 (`RULE-CHAIN-S1`), never asked of Jev; 4. a failed run
invalidates the pre-run records; 5. every cycle starts by reading the bed's LabVIEW Error List through the GUI,
each item double-clicked to its location (*"GUI로 에러 내용 확인하고 각 에러 더블클릭하면 에러 위치로 이동해서
보여주거든"*); 6. a move's cut set and reconnect table are computed from the graph before the move and checked after;
7. the whole stage is simulated action by action (temporary graph per step, symbolic ids bound by a before/after
terminal-table diff) and finalized at `computation_diff` 0, then executed once with a per-step comparison;
8. row content comes ONLY from the finalized plan file — a recipe never re-types a uid or terminal name.
**Python computes, Jev picks per-row mechanisms, the LLM designs and takes low-confidence rows.** 1/2/4/7 are
enforced by the launch gate in `tools/hooks/guard_bash.py`, 5 by `cycle_runner.py`'s `errorlist_hook`, 3/6/7/8 by
stagekit gates; this section records only the why.

### Big or blocked work is SPLIT into steps that each SAVE an intermediate artefact (user, 2026-09-19)

*"앞으로도 프로젝트 방향성에 관해서 큰 덩어리의 프로젝트는, 혹은 병목이 생긴 부분에서는, 세부적으로 쪼개서 중간과정
저장하며 진행하는 방식으로 규칙 수정 필요할듯."* — said after ten overnight route-B attempts (v3→v7, 5 cycles, ≈$166)
edited a VI copy entirely in LabVIEW memory, died at the same re-wiring stage every time, and left **no file to look
at** (the "preserved" crash copies were byte-identical to the untouched original). Applies to everything still ahead
(EMCCD connection/sync, display, …), not only D1.

1. **A step is not done until it has left a file.** Every build stage saves its intermediate VI/data under `claudeDev`,
   records its md5, and the next stage starts FROM THAT FILE — in a fresh LabVIEW instance when the stage uses VI
   Scripting. The user must always have something to open.
2. **Default granularity = one saved artefact per natural stage** (copy → structures → moves → re-wiring in batches of
   10–15 rows → census → final save). Not one script per wire (*"일일히 배선 하나하나 별도 스크립트를 쓰는 건 낭비"*).
3. **Re-splitting is triggered, not felt** (user: the decision is the judgement session's, the trigger is the
   machine's): the same stage failing twice at the same place, or a stage that ends without a saved artefact ⇒ the
   next cycle's FIRST act is a **decomposition plan** for that stage (one page: sub-steps, each's saved file name and
   pass criterion), prior-art-reviewed once, then executed step by step by material sessions. A full-length retry under
   a new file name (`_v8`) is forbidden. `cycle_runner.py` counts renamed recipes as the same recipe.
4. A new large stage (e.g. EMCCD sync) starts with its step list and saved-file list written into the plan; no build
   before that list exists.
6. **A BROKEN INTERMEDIATE MAY BE SAVED BY GUI Ctrl+S (user, 2026-09-22: "저장 허용함.").** A `claudeDev` stage artefact that is broken BY DESIGN (its missing rows belong to the next stage, `ExecState` 0) is saved through `gui_save` (block-diagram window fronted and click-probed, Ctrl+S, mtime verified) with `-Exception Approved -Evidence "user 2026-09-22 broken-intermediate save"`, because COM `SaveInstrument` hangs on a broken VI — the scripted route is verified unreachable for this class. Such a file is NEVER run and never cold-loaded headless. Not for originals (rule 1) and not for the final deliverable, which must reach `ExecState` 1 and save by script.
5. **Reference hygiene is a precondition, not an afterthought**: an op that traverses without `Close Reference` is
   repaired before it is used in a staged build (20 consecutive calls in one script, handle count flat ±100).

### The work cycle (user, 2026-08-31)

1) **Plan, and peer-review the plan**; 2) write the WHOLE build as **one long script file**
(Python/bash — e.g. `tools/recipes/*.py`), every name resolved from `docs/NAMES.md` at planning
time; 3) execute the file as a batch; 4) read the results report, revise; 5) repeat. No mid-run
name discovery; no per-step verification round-trips. Target: replay speed, discovery paid up
front.

### Tooling

**Hooks (mechanical rules, 2026-09-04)** in `.claude/settings.json`: `tools/hooks/answer_first.py`
(UserPromptSubmit) re-injects rule 2b on every user message; `tools/hooks/guard_bash.py`
(PreToolUse Bash|PowerShell) blocks any LabVIEW-touching command run in the foreground without a
timeout ≤ 30 s — background it instead. Prose rules fade after compaction; code rules do not
(the GUI gate in lv_gui.ps1 ended six rounds of GUI-creep). When a rule is broken twice, move it
into a hook. Hook commands use forward-slash paths (backslashes are escape-interpreted). **Project hooks also run
inside every `claude -p` cell spawned from this directory** — a hook that gives advice ("stalled client,
stop the task") will be acted on by that cell; gate such hooks on an env var the spawner sets
(`BENCH_CELL`), as lv_stallcheck.ps1 now does.

**Patch files with the Edit/Write tools, never with a `py - <<'EOF'` heredoc** (2026-09-09: three heredoc patches
in one session died on `\U`/`\N` escapes or literal NUL bytes, and because the launch line followed on a new line
the chain ran UNPATCHED each time — 20 min lost per round). A heredoc is fine for read-only one-liners only.

All screenshot/window/mouse/keyboard/checksum operations go through
[tools/lv_gui.ps1](tools/lv_gui.ps1) — never inline `Add-Type`. `.claude/settings.json`
pre-approves it **only** in the exact form `& .\tools\lv_gui.ps1 -Action ...` from the project root
— a `cd`, a variable, or an absolute path breaks the allowlist and stalls unattended work. The same
settings **deny** Edit/Write on `*.vi`, `*.ctl`, `*.lvlib`, `*.lvproj` (compiled binaries; every
legitimate change happens inside LabVIEW) — defense-in-depth for rule 1.

## 4. Documentation is layered: short top index, topic files below, archive unread

(User, 2026-08-27 + 2026-08-31 "계층화".) **Active docs** state what is true now, in as little text
as a cold start needs: `STATUS.md` stays under one screen and only points; verified facts go to
topic files (`docs/`, skill `references/`); narrative goes to [archive/](archive/) — nothing is
deleted, only moved. **Do not read `archive/` in normal work**; open a specific file only when the
active docs are ambiguous, and say why. When any working doc needs scrolling to find the current
state, push content down a layer immediately, not at the next cleanup. Scratch artefacts
(throwaway VIs, build targets) are created and deleted in the same operation.

**Concrete threshold (2026-09-15, after STATUS.md reached 651 lines):** STATUS.md over ~100 lines means the cycle
narrative has crept back in — move it to `archive/<date>-status-<topic>.md` and leave lock, hardware permission,
current state, OPEN items and NEXT. The narrative is never rewritten, only relocated.

### Documents are LINTED by code and INGESTED by a model every cycle (user, 2026-09-16)

*"특정 주기마다 .md 파일들 ingest 및 lint 하는 규약 필요해보임"* — after STATUS reached 526 lines, CLAUDE.md carried a
stale slug list and two docs described one wire two ways. Cadence is **per cycle / per run, never weekly**
(*"주 단위보다는 싸이클 단위 혹은 실제 실행 단위가 적절해보임"*). "Ingest" means **a model reads and refreshes
state** — NOT an index; the index was measured and rejected (`tools/bench/priorart_scores.md`).

| layer | what | model | when |
|---|---|---|---|
| **lint** | `tools/doc_lint.py` — frontmatter valid; every cited path / `file:line` exists; STATUS ≤ ~100 lines; one `status: current` plan; `supersedes:` targets not still current; review dispositions not placeholders; unmarked decision sentences (warn) | none (a `.py`) | every cycle close, run by `audit_cycle` |
| **ingest — changed docs** | `tools/doc_ingest.py --cycle N` — the claude peer as rule/consistency auditor (`peer.ps1 -Role ingest`, archived to `archive/ingest/`, invisible to every gate) over the cycle's changed files (audit C7 list): contradictions between them and with the active docs | **Sonnet** | every cycle close |
| **ingest — all active docs** | `tools/doc_ingest.py --full --model opus` — same audit over all of `docs/` + STATUS + CLAUDE.md | **Opus** | every 5 cycles (same rhythm as the outcome review) |
| **resolving** which document is right | — | judgement session | when the ingest reports a contradiction |

## 5. Peer agents (Codex, Gemini) — Claude manages, they only advise

Read-only research sub-agents; their brief is [AGENTS.md](AGENTS.md). **Dispatch only through
[`tools/peer.ps1`](tools/peer.ps1)** (`-Agent codex|gemini|claude [-Kind review|fact] -Slug <name>
-Task "..."` — nothing else validates). It enforces read-only, bounds every call with a timeout, classifies the outcome, and
archives the exchange. Screenshots and reporter text may be attached; **never `.vi` files**. Attach
a ~3-line "already ruled out" block for diagnostic questions; none for pure API facts. **A peer
answer is a hypothesis** — confirm against the machine or the vendor's own files; two models
agreeing is not confirmation. Call them *before building something expensive* and whenever a
diagnosis is about to drive real work; dispatch needs no approval and has no call limit. On quota
exhaustion stop calling that agent for the session — degrade to working without it, never to
waiting.

### Review has THREE layers, and only the third asks whether the work was worth doing (2026-09-15)

| layer | asks | fires | enforced by |
|---|---|---|---|
| hypothesis | is this diagnosis right? | every failed prediction | `guard_peer.py` |
| cycle | was this cycle run well? | end of every cycle | `guard_cycle.py` + `retrospective.py` |
| **outcome** | **did any of it move the deliverable?** | **every 5 cycles or 7 days** | `guard_cycle.py` + `outcome_review.py` |

The first two both ask HOW; a cycle can be run impeccably and still be the wrong cycle (user,
2026-09-15: "주기적으로 프로젝트의 성과를 판단하는 피어도 필요하지 않을까"). The outcome layer asks
against `project-requirements/`: what can the user RUN today that they could not before; which
numbered requirement has not moved since the project began; is the cost-to-product ratio defensible;
if the user had to run an experiment next week, would they use the original VI or anything we built.
Its reviewer was **codex, never claude** — "was this worth doing" is the question a reviewer sharing our priors is
worst at. ⚠️ **CHANGED 2026-09-18, a TRIAL (see "Codex's roles move to Claude sub-sessions" below): the reviewer is
`peer.ps1 -Agent claude -Role outcome` = FABLE / medium, run `--safe-mode` so the cell never loads CLAUDE.md,
STATUS.md's framing or the plan documents into its system prompt.** The original objection is answered by the THIN
PROMPT rather than by the vendor — what made codex right here was not sharing our priors, and a cell that reads
only `project-requirements/` and the counted output does not share them either. `-Agent codex -Kind fact` is one
flag away if the trial fails. **Fired three times (2026-09-15, 2026-09-16, 2026-09-18: zero runnable experimental VIs every time); the
user re-planned to DELIVERY-FIRST on 2026-09-16 ("A로 진행하자") — `docs/cycle15-plan.md` — with the boundary
*"여기는 중간 과정일 뿐 결국에는 최종 스텝으로 나가야함"*: delivery is ordering, the seven-loop restructure is
still the goal.** **An `OUTCOME-VIOLATION` is NOT answered by building a device** (that is the
process rule, and answering goal drift with another tool is how the drift happened): the next cycle
becomes a **delivery** cycle, and on repetition the work stops for a re-plan with the user. **AMENDED by the user 2026-09-23 ("83번으로 가자", resolving Pre-decided 44 vs 83): once the user has ANSWERED a repeated outcome verdict (as on 2026-09-20, "계속"), a further repetition of the SAME verdict does NOT stop the runner — the session marks the escalation in STATUS and the interactive chat reports it; the work stops only when the verdict's CONTENT changes (a new violation line, or a requirement moving backwards).** Keep the
layer to one script, one dispatch and one gate line — the user's explicit budget for it. **STEERING CARD (user, 2026-09-24: "아웃컴 리뷰에 조향카드 부여하는 것 동의"):** a repeated outcome verdict now also emits a `steer/1` card (the next cycle's required act, tied to `docs/goalmap.json` ids); the judgement session FOLLOWS it or REFUSES it with cited evidence in `next.json`; two refusals of the same item stop the runner and put it on `tools/bench/decisions_pending.json`. **RETRY CAP (user, same day: "재시도 상한도 동의함. 다만 숫자 … 데이터를 쌓아가면서 조정"):** one stage's LabVIEW runs per cycle are capped (`tools/stage_prerun.py` `RETRY_CAP`, start 2); a further run needs a judgement card; per-stage run counts are recorded so the number is tuned from data.

**The fourth layer — PRIOR ART ("has this already been done here?", `prior_art_review.py`, gated by the same
`guard_cycle.py`) — stops the work on any verdict other than `novel`, and there are exactly TWO releases, each
written into the review file itself and each paid for with a citation:**

| release | means | conditions (all machine-checked) |
|---|---|---|
| `REFUTED: <slug> - <file>:<line> says X, which does not cover Y because …` | the review is **wrong** | open the cited file and show in writing that it does not cover this case. Not "I think otherwise" |
| `FIXED: <slug> - <path>:<line> - <one sentence saying what changed>` | the review is **right and the work already changed** | (a) `<path>` exists under the project, (b) it was last changed **after** the review (its frontmatter date; the file's own stamp if it carries none), (c) the line sits under `## What was done with it` in the review file |

`FIXED:` was added 2026-09-16 (tested: valid releases; nonexistent path does not; older-than-the-review path does
not). Until then the gate's own refusal said "if the review is right, change the plan instead" while accepting only
the branch where the review is WRONG — so a round whose findings were all correct and all acted on could not
release the build it had just improved. An assertion is not a refutation and **a promise is not a fix**; the
citation is the currency, and `CYCLE_GUARD_OFF` is never the answer.

**The peer must be asked to REFUTE — now mechanical.** `peer.ps1 -Kind review` (the default) REFUSES
a task carrying confirm-bait ("please confirm", "sanity check", "do you agree", "확인 부탁") and
APPENDS the adversarial instruction set (strongest reason it is wrong · an alternative explanation ·
what would falsify it · the cheapest discriminating test). `-Kind fact` exempts a pure API-fact
question. Cycle 7's retrospective found prompts saying "BRIEF CONFIRM"; a rule about how a question
is *phrased* belongs in the dispatcher, not in good intentions.

**The claude peer cannot discharge a failed prediction.** It is the rule/consistency auditor, so
`guard_peer.py` requires the lifting exchange to come from codex or gemini **and** to have ended
`ANSWERED` — a TIMEOUT/QUOTA/ERROR exchange is exactly what this file calls "told you nothing", and
the gate used to accept one.

### External search is MANDATORY — the ladder only decides who runs it

(User, three times, finally: "멀티 에이전트 활용을 하던 아니면 너 혼자 답변을 하던 외부 검색 세션을
필수로 넣도록".) Every factual question about a tool, API, error or capability gets an external
search — by a peer or by Claude, never skipped. The error being stamped out is **false confidence
from local evidence**: absence in what you happen to be looking at is not evidence of absence.
**Trigger sentence:** the moment you are about to write "X is not possible", "our tools cannot
reach that", or "so we fall back to GUI clicking" — stop and search. Claims about *our own tools*
are factual claims, the ones you are most likely to be wrong about.

### A FAILED PREDICTION triggers mandatory peer review — all three parts

(User, 2026-08-30: "가설을 세워서 결과와 맞지 않으면 피어리뷰 과정을 필수로 넣자. 내가 말한 피어리뷰는
멀티에이전트 검색 및 감시, 더해서 advocate 과정이야".) **A recurring error alert is a failed prediction too**
(user, 2026-09-14, on the repeated "STALLED LabVIEW client" hook messages: "이런 에러들도 반복되는 것 같으니
피어리뷰 반드시 필요하겠어. 규율에 적용하도록") — mechanically: `tools/lv_stallcheck.ps1` writes
`tools/bench/stall_pid<N>.log` (`STALL:` line) and `tools/hooks/guard_peer.py` blocks the next build until
a peer review newer than that record is archived. When any other error class shows up a second time, give
it the same treatment in the same session: a record the gate can see, not a sentence here. **The gate reads build
logs only — `tools/bench/peer_*.log` transcripts are excluded** (2026-09-15: a reviewer's own sentence, "Fail the
build on inequality…", blocked the very build that review had approved; review logs are evidence, never the thing
under test). The moment you predicted X and observed
not-X, the explanation you form is a fresh hypothesis built under pressure. Peer review then means
**all three together**: (1) multi-agent search asked to *attack* the claim; (2) **monitoring** —
watch the dispatch and classify its outcome; a call that failed, timed out or hit quota told you
*nothing* (an `-Agent agy` ValidateSet typo once died instantly and would have passed for a
completed review); (3) the devil's-advocate pass below. **Your own successful discriminating test
does not discharge this** — it confirms the experiment you thought to run; the peer's job is to
attack the framing.

### The devil's-advocate pass — search catches ignorance; this catches false knowledge

(User, 2026-08-29: "외부 검색만이 아니라 자체적으로 devil's advocate이 필요하겠는데".) Before a
diagnosis or plan drives real work — and at every "X is impossible", before expensive construction,
before destructive steps — argue against it. Two requirements keep it from being theatre: **it must
end in a discriminating test** (name an alternative cause, name what would falsify the hypothesis,
run the cheapest separator — comparing options is not a test); and **a peer used as adversary must
be asked to refute, not confirm**. Health check: if the user is the one raising the objections, the
internal pass is not running.

### Name the level of verification — structural is not functional

(User, 2026-08-29: "데이터 넣어보지 않았는데 어떻게 확인한 거야?") **Structural** = the artefact is
well-formed and legal (object counts, owners, `ExecState == 1` — the compiler's verdict, nothing
more). **Functional** = the right numbers when real data flows through. A build that has never been
run is not verified, however many counts agree. State the level explicitly in STATUS and in every
summary.

### The research ladder — one rung at a time, and it always has a bottom

| | reads files | reads the web | model |
|---|---|---|---|
| **codex** | ✅ project dir, read-only sandbox | ✅ | `gpt-5.6-sol` / medium, pinned in peer.ps1 (user, 2026-09-15). **Still selectable, no longer any default — weekly quota 9 % on 2026-09-18** |
| **agy (gemini)** | ❌ | ✅ | RETIRED from every default/fallback 2026-09-22 (user: roles delegated to claude; headless permission auto-deny). Explicit `-Agent gemini` only |
| **claude** | ✅ project dir (the thin roles: only what they choose to read), plan mode + acting tools denied | per role | **`-Role` decides**: `audit` sonnet · `ingest` sonnet · `priorart` claude-opus-5-5/medium · `hypothesis` claude-opus-5-5/high +web (user table 2026-09-23; was opus/high · opus/max) · `fact` **fable/low +web, thin** · `outcome` **fable/medium +web, thin** · `prose` **fable/low, thin** |

The claude peer was added 2026-09-15 on the user's direction ("claude 하위 세션도 peer review에 참여
시키는게 좋겠어") so the review structure survives an external quota outage. It is the one peer that
spends the SAME subscription as the main session. **THIN** = dispatched with `--safe-mode`, so the cell skips
CLAUDE.md, skills, plugins, hooks and MCP; that fixed context load, not the model, was the ~$1.5–3 a peer call
cost. Web is now per role, not banned outright — `hypothesis`, `fact` and `outcome` have `WebSearch`/`WebFetch`;
`audit`, `ingest`, `priorart` and `prose` still have none.

One peer per question (the others only to cross-check an answer about to drive expensive construction).
Fallback order from 2026-09-22 (user: "Gemini 역할도 claude에게 위임" — agy auto-denies its `command` permission headless, so it is dead in unattended runs): **claude → Claude's own research session**; gemini stays selectable by an explicit `-Agent gemini` only, with codex reachable by an
explicit `-Agent codex` while its quota lasts. If every peer is exhausted, Claude still runs the external research
itself — "no peer available" never means going straight to experimenting. Waiting for a quota to renew is never
the right move.

### Codex's roles move to Claude sub-sessions — TRIAL, user's decision 2026-09-18

> *"Codex 잔여량이 생각보다 얼마 남지 않음. 주간 한도 9% 남았음. 아무래도 Codex가 수행중인 역할을 fable로
> 구동하는게 어떨까 싶음."* … *"우선은 지금 말한 방법으로 몇 번 돌려보자"*

A trial, not a settled rule: run it a few times, then decide. What changed, all inside `peer.ps1`'s role table:

| dispatch | before | from 2026-09-18 |
|---|---|---|
| `-Kind fact`, no `-Agent` | codex by hand | **claude `-Role fact`** — fable/low, thin, web |
| `-Kind prose`, no `-Agent` | codex (`reporter`) | **claude `-Role prose`** — fable/low, thin |
| `outcome_review.py` | `-Agent codex` | **claude `-Role outcome`** — fable/medium, thin, web |
| failed prediction | `-Dual` (codex **and** opus/max) | **`-Agent claude -Role hypothesis` SINGLE arm**; `-Dual` stays available |
| `prior_art_review.py`, `doc_ingest.py`, `retrospective.py` | unchanged | unchanged |

**D3 is amended**: `guard_peer.py` now accepts an ANSWERED `claude` exchange whose `role:` is `hypothesis`
(opus / effort max) as discharging a failed prediction, alongside codex and gemini. Every other claude role still
cannot — it is the rule/consistency audit, not a framing adversary. Check a routing change without spending a
call: `tools/peer.ps1 -Kind fact -Slug x -Task "..." -DryRun` prints agent, role, model, effort, tools and the
archive path and dispatches nothing.

### Hypothesis reviews are being moved to an Opus/max Claude peer — measured first (user, 2026-09-17)

GPT usage was higher than the user expected (*"GPT 사용량이 생각보다 적지 않은데"*). Decision: try the failed-
prediction (hypothesis) review on a Claude sub-session under **codex's exact constraints** (read-only, adversarial
preamble, timeout, archive, gates) with **Opus at effort MAX** (*"opus는 high 보다 더 높게 잡아도 문제 없을 것
같은데"*) and **web search enabled** for that role. Not Fable (cost rule). codex stays for the OUTCOME review and
as the second opinion when a Claude review passes a claim about our own tools. **The next five failed predictions
go to BOTH; D3 ("a claude peer cannot discharge a failed prediction") is amended only after that comparison.**
Implementation: `peer.ps1` role `hypothesis` (opus/max, WebSearch allowed) + a dual-dispatch switch; the archive's
cost lines are the comparison data.

✅ **BUILT AND SELF-TESTED 2026-09-17** (`tools/bench/peer_dual_selftest.log`, `BGRUN END rc=0 after 100s`):
`tools/peer.ps1 -Agent claude -Role hypothesis` = **opus / effort max** with `--allowedTools WebSearch WebFetch
Read Glob Grep` (the only claude role with the web; every other one keeps rule 5's "claude peer has no web"), and
**`-Dual`** re-invokes the script twice on one `-TaskFile`, archiving `<date>-<slug>-codex.md` and
`<date>-<slug>-opus.md`. Both arms ANSWERED on the self-test; the cost lines are
`codex 26 s` (no cost line — the CLI reports none) vs **`opus $1.8621, in 10 / out 4,581 / cache-create 158,866 /
cache-read 258,782, 70 s, 11 turns`**. ⚠️ `-Dual` exits with **codex's** return code.
✅ **SUPERSEDED 2026-09-18 by the trial above**: the comparison stopped early because codex's weekly quota reached
9 %. **D3 IS AMENDED** — `guard_peer.py` accepts `-Agent claude -Role hypothesis` (ANSWERED, opus/max) on its own,
so a failed-prediction review is now a **SINGLE claude arm**, not `-Dual`. `-Dual` remains available and is the
right call when a claim about our OWN tools needs a second opinion that does not share our priors.

### Archiving peer exchanges — and the one exception to rule 4

Every exchange goes to `archive/peer/YYYY-MM-DD-<slug>.md` (question, answer, source URLs);
conclusions that changed direction get copied into an active doc. **Exception:** check
`archive/peer/` for the same question before re-asking — re-asking wastes quota the session may
need later.

## Where to actually look

- [STATUS.md](STATUS.md) — lock, current state, next actions. Read first, always. One screen.
- [docs/NAMES.md](docs/NAMES.md) — verified terminal/label strings (newlines are real). Check
  before every wiring call.
- `.claude/skills/labview-automation/` — ALL LabVIEW technique (SKILL.md index + 4 references).
  Invoke the skill before any LabVIEW work.
- [ARCHITECTURE.md](ARCHITECTURE.md) — the rig. [Requests.md](Requests.md) — the user's ground
  rules verbatim. [AGENTS.md](AGENTS.md) — the peers' brief; keep it short and true.
- [archive/](archive/) — history; see rule 4.
