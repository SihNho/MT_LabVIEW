---
name: lean_operation_and_buffer_number_accuracy
description: "2026-10-13 - lean rules beat the harness (P6-2 64 min $6.6 vs ~3 h $50+ unfinished); user chose option b (a user-started queue runs lean sessions); buffer-number accuracy per row is the data-accuracy criterion, even under overload"
metadata:
  node_type: memory
  type: project
  originSessionId: b607b493-a66f-4081-b122-a7a95d2c2a67
  modified: 2026-10-13T13:13:59.932Z
---

2026-10-13, after discussion lean-rules-01 and two lean runs (P6-2 PASS 64 min $6.64; P6-3 gap+load PASS 102 min $17.52,
which also found P6's column-0 one-ring-lap lag the old acceptance missed):
- The user agreed lean operation performs better ("하네싱이 과하게 필요했지만 지금은 아닌가보네") and chose **option b**:
  the USER starts `V6_lean/tools/bench/lean_bench/lean_queue.ps1` once; the chat puts task files in its `queue/`; it stops
  on a `STOP` file there or when the main STATUS rig-state is not 조립. The chat cannot launch these sessions itself (auto-mode
  classifier: [Create Unsafe Agents]). Proposal text: docs/lean-operation-proposal.md.
- Kept as hard rules: motor hook ("모터 훅은 반드시 체크 해야돼"), originals, LabVIEW safety, rule 1a at the end; plus
  predictions before the run and the chat's own re-check of the numbers from raw files before adopting a result.
- User: "과부하가 걸리더라도 버퍼 넘버의 정확성이 데이터의 정확성을 결정하는듯" - every saved row's buffer number must be its
  own frame's (U7 time axis, U9 mismatched pair = corruption), at normal load, gapped source and overload.
- User check every 10 cycles ("4번은 10 사이클로 하자"). The auto-mode classifier refused the chat writing/starting an
  autonomous lean runner even with stop points between cycles ([Create Unsafe Agents]) - never route around it; the user
  starts the queue or changes the permission mode. Detail: docs/lean-operation-proposal.md, PD414 in docs/d1/ring-p6b.md.
- Runner shape (user 2026-10-13 late, commit 0992a11e on bench/lean-20261013): one user start = one run of <= 10 cycles
  ("한 러너에 10 사이클은 돌려"; the user checks after each run and starts the next). A failed cycle is NOT a stop: a
  read-only Claude-GPT discussion (lean_discuss.py) writes a same-tag retry task into queue/next/ ("실패한 사이클은 멈춰버리지
  말고 토론해서 방향 잡도록"); no agreed action / a user question / 3rd failure of a tag -> tag skipped, reason in
  questions_for_user.md. Motor limits SET at cycle start and RELEASED at cycle end by the queue (lean_cycle_hooks.py:
  LabVIEW closed + verified first, then --session end); a lean session may not run motor_gate --session (guard_lean).
  A failed cycle hook (motor/LabVIEW) DOES stop the run - safety, not a task failure.
- GitHub: upload once a day (scheduled task github-daily-push, tools/git_push.py) and on explicit request; never per cycle.

**Why:** the gates cost more than they prevented once the tools existed; a single session kept context and found a real defect.
**How to apply:** write lean task files, review each report, re-check the acceptance from raw files, merge to master;
when the user announces 실험중, write the queue STOP file and stop a running lean session. See [[claude_main_gpt_debate_peer_only]].
