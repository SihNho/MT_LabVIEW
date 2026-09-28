---
type: reference
status: current
date: 2026-09-28
tags: [user-rules, design-check, prior-art, card-chat-P2]
---
# The user's standing DESIGN rules — every new design is checked against this list before it is built

Card chat-P2 item 1 (user 2026-09-28 17:xx, "그렇게 1~4번 적용하여 수정하면 되겠음"). The largest single loss in cycles
84–120 was not a bad build but a design direction (the image pool with `Q_free`/`Q_work` queues, PD233–237) that
contradicted rules the user had already given; nobody compared the plan with them before building. This file is that
comparison's input. Every row is the user's own words, dated, with where it was recorded.

How it is used (mechanical):
- `tools/prior_art_review.py` attaches this file to EVERY prior-art dispatch and asks one fixed question: *does this
  plan contradict any rule in user-rules.md? Name the rule and the plan line.* A contradiction is the verdict
  `PRIOR-ART: user-rule-contradicted` — a non-`novel` verdict, released only by the usual `REFUTED:` / `FIXED:` lines.
- A judgement session that writes a new Pre-decided DESIGN item reads this file first and puts a `USER-RULES:` line in
  the item (the rule ids it relies on, or `USER-RULES: none apply`); `tools/doc_lint.py` L9 warns when a Pre-decided
  item numbered 238 or later lacks one.
- A row is added only from a user statement (quote + date + source). A row is never re-worded; a later user statement
  that changes a rule is a NEW row that names the row it supersedes.

| id | rule (one line) | the user's words (verbatim) | date | source |
|---|---|---|---|---|
| U1 | The original's computation (per-bead maths, its parameters, its numbers) never changes; only scheduling may. | "원본의 연산방법 자체를 바꾸면 안돼. 이건 꼭 명심하고." · "이미지를 분석해서 수치화하는 모델과 그 연산 방법 및 결과가 바뀌면 안된다는 말이지." | 2026-08-30 | CLAUDE.md:25-37 (rule 1a); memory preserve_the_original_computation.md |
| U2 | Hardware access follows the rig state (disassembled / assembled / experiment running); the ASI is a motor like any other. | "모터 접근 및 카메라 접근을 '리그 분해 / 리그 조립 / 실험중' 상태에 따라 다르게 두는게 맞는듯. … 이는 Piezo stage인 ASI 컨트롤러를 포함하는 내용 (ASI와 다른 모터를 구분하여 권한 두지 말것)." | 2026-09-16 | CLAUDE.md:39-44 (rule 1b) |
| U3 | No VISA/serial call anywhere on the frame acquisition path; serial lives in its own loop with a non-blocking handoff. | "I don't want to have even a single frame loss coming from the motor communication if possible. And it is so clear that serial communication through VISA can somehow stall the loop, and cause unwanted frame stop." | 2026-09-16 | CLAUDE.md:89-100 (rule 1c); memory no_serial_on_the_frame_path.md |
| U4 | Loop-to-loop CONTROL signals go by local variable (latest value), never by queue; queues only for lossless data streams. | "큐를 넣어버린다면 두 루프 사이에 상관관계가 생겨버린다는 것 같은데, 그런 리스크를 감당할 필요가 있는지 모르겠음. 그냥 Boolean 값 및 타겟 값을 local variable로 전달하는게 더 좋지 않을지?" | 2026-09-25 | CLAUDE.md:102-124 (rule 1c''); memory locals_not_queues_focus_loop_own_clock.md |
| U5 | The ASI autofocus loop runs on its own clock, not in step with frame acquisition. | "ASI autofocus 루프는 애초에 frame acquisition 루프와 동시에 돌 필요가 없을듯." | 2026-09-25 | CLAUDE.md:102-124 (rule 1c''); memory locals_not_queues_focus_loop_own_clock.md |
| U6 | The camera free-runs; nothing we build may throttle, block or pace acquisition (the PC is a reader, never a gate). | "카메라는 기본적으로 자신의 루프를 컴퓨터와 독립적으로 돌아야 하며 그렇게 돌고 있음. 컴퓨터를 통한 카메라 프레임 컨트롤을 신뢰할 수 없기 때문임. 따라서 Lossy Enqueue Element 혹은 기타 다른 어떠한 방법도 카메라 frame acquisition에 영향을 주어서는 안됨." | 2026-09-15 | docs/decisions.md:21; memory camera_free_runs_never_gate_it.md |
| U7 | The buffer number is the time axis (frame N happened at N/framerate); never a software timestamp. | "시간 간격은 컴퓨터 루프와는 별개로 프레임이 같다면 동일함. 카메라 루프의 acquisition 정보에 frame rate을 별도의 하드웨어로 통제하기 때문. 그러니 데이터 전달에서 생기는 시간 불균일은 크게 중요하지 않음." | 2026-09-15 | docs/decisions.md:24; memory camera_free_runs_never_gate_it.md |
| U8 | Overload, acquisition → tracking: discard the backlog and take the newest frame (latest-wins). | "큐를 버리고 새로 들어오는 프레임을 읽는 것이 가장 바람직함. 이는 시계열 데이터의 엄밀성을 위함." | 2026-09-15 | docs/decisions.md:25; memory prefer_the_freshest_frame_over_a_complete_backlog.md |
| U9 | No corruption: image memory and its buffer number change together and the consumer verifies them; a gap is fine, a mismatched pair is corruption. | "만약 buffer number 갱신이 어려운 상황인데 IMAQ 메모리만 바뀌었다 라고 한다면 정말 데이터 커럽션으로 봐야할듯." | 2026-09-15 | docs/decisions.md:27; memory prefer_the_freshest_frame_over_a_complete_backlog.md |
| U10 | Authorised fallback: acquisition and tracking may stay in ONE sequential loop if the handoff cannot be made provably safe. | "2번이 문제가 된다면 Acquisition 및 추적은 동일 루프에 두고 시퀀셜 처리를 하는 것도 괜찮을 것 같음." | 2026-09-15 | docs/decisions.md:31; memory prefer_the_freshest_frame_over_a_complete_backlog.md |
| U11 | Frame rules have a PRIORITY ORDER: (1) no corruption, (2) latest-wins, (3) the sequential fallback. Search these rows before asking the user a frame question. | "위에 프레임 관련해서는 내가 말한 내용이 있음. 다시 찾아봐. 우선순위가 있는데" | 2026-09-28 | memory prefer_the_freshest_frame_over_a_complete_backlog.md |
| U12 | Pure-display indicators (plots) are drawn by a SEPARATE display loop on its own clock, fed by local variables; never an every-N-frames gate inside the frame loop. | "그래프 플롯 기능을 혹시 별도 루프로 두는 것은 어떤지? 로컬 변수에 데이터들은 다 입력하고 데이터 플롯은 별도 루프로" → "이대로 진행" | 2026-09-26 | memory display_in_separate_loop_fed_by_locals.md; docs/d1-loop12-17-split-plan.md Pre-decided 210 |
| U13 | Frame handoff 1.1 → 1.2 is a RING BUFFER of 20 IMAQ slots (slot = camera loop counter mod 20), seqlock per slot, no `Q_free`/`Q_work` queues; on overwrite jump to the newest slot; slot numbers come from the camera loop. Supersedes the pool-queue design (PD233–237) and cancels the "option C" rollback. | "1번 지적은 훌륭한 부분 / 2번 … 특정 프레임은 놓쳐버릴 수도 있으니까 / 3번 … 버퍼로 20 프레임이 있어도 문제가 생긴다면 최신 칸으로 움직이는게 맞음 / 4번 … 칸 번호는 카메라 루프를 쓸 수밖에 없지 않나?" | 2026-09-28 16:3x | docs/ring-buffer-design.md:10-38 |

## Reading the rows together (what a reviewer checks first)

- A **queue** between two of our loops is allowed only for a lossless DATA stream (tracking → file writer). A queue that
  carries a control signal (U4) or sits at the acquisition boundary (U6, U13) contradicts the rules.
- Anything whose failure mode is "the camera loop waits" contradicts U6; anything that can put serial on the frame path
  contradicts U3; anything that changes a per-bead number contradicts U1.
- A frame-handling design must say how it meets U9 (pair verified), then U8 (latest-wins), then U13 (ring + seqlock) —
  in that order (U11).
