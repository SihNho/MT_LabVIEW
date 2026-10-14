---
name: lean_operation_and_buffer_number_accuracy
description: "2026-10-13 - lean rules beat the harness (P6-2 64 min $6.6 vs ~3 h $50+ unfinished); user chose option b (a user-started queue runs lean sessions); buffer-number accuracy per row is the data-accuracy criterion, even under overload"
metadata:
  node_type: memory
  type: project
  originSessionId: b607b493-a66f-4081-b122-a7a95d2c2a67
  modified: 2026-10-14T17:17:00.631Z
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
  ("한 러너에 10 사이클은 돌려"; the user checks after each run and starts the next). Each cycle = EXECUTE (lean session)
  -> REVIEW (read-only Claude-GPT discussion re-computes the acceptance from raw files, VERDICT PASS/FAIL) -> PLAN (one
  read+Write session writes the next task into queue/next/) - user "실행 에이전트 --> 리뷰 에이전트 (토론) --> 플랜",
  lean_review.py, lean commit 06af8d7f. A failed cycle is NOT a stop ("실패한 사이클은 멈춰버리지 말고 토론해서 방향
  잡도록"): same-tag retry, max 2 failures per tag; what needs the user -> questions_for_user.md.
  The user corrected the chat: unattended loops ran fine before (old runner, ~170 cycles; its 10-12 restart was not
  refused) - so do not blame "unattended" for the classifier refusals; the lean design had less structure and fewer hooks. Motor limits SET at cycle start and RELEASED at cycle end by the queue (lean_cycle_hooks.py:
  LabVIEW closed + verified first, then --session end); a lean session may not run motor_gate --session (guard_lean).
  A failed cycle hook (motor/LabVIEW) DOES stop the run - safety, not a task failure.
- Run 1 (2026-10-13 22:22 -> 10-14 05:00, 5 cycles, user "한 5 사이클정도 돌려보고 평가 토론"): p6fix, latest (x3), p6close
  all ended PASS; final P6 VI claudeDev\bench\lean\D1_ring_p6latest_20261014_010104.vi 15c664e3. The review overturned one
  self-reported PASS (per-pick lag was inferred, not measured). Evaluation discussion: keep execute -> review -> plan.
  User 2026-10-14 05:1x "동의" to all three: (1) v5 G0's per-leg motor_gate --session start + PI reference is ALLOWED;
  (2) P6-4 PREPARATION starts (read + plan; the bead run still waits for the user at the rig); (3) the evaluation's
  runner changes applied (lean 68cdcd79: no verdict twice -> HOLD, never PASS-UNREVIEWED; cycles counted by REVIEW
  lines; HOLD:/ASSUME: questions; mock queue 14/0). Keep the regular human check until a real run shows the auto-STOP
  working (evaluation condition). The chat's own tail -F monitor had broken the queue's logging in run 1.
- P6-4 (2026-10-14 10:4x, user "전부 동의함"): all questions of V6_lean/tools/bench/lean_bench/p64_plan.md section 10
  agreed as written (ABBA A-B-B-A at 90/150 Hz, B both legs >= 25 % of A's mean below the lower A leg + 15 picks;
  150 Hz by a rate wrapper on copies of A and B; bead map from a snapshot checked by the user; live check = buffer-number
  consistency, image/number pairing rests on the replay evidence). Sample = non-paramagnetic polystyrene REFERENCE beads
  ("아무리 당겨도 로스는 없을 것"); the user prepares them and SAYS WHEN - no bead/rig-day task before that.
  Preparation tasks p64p1 (BOBS90 observer copy), p64p2 (150 Hz copies + 30 s camera-only check), p64p3 (drivers, dry) queued.
- 2026-10-14/15 answers: sample R for now; no minimum bead count (repeat clicks on real beads allowed); evaluation changes
  1-6 applied (lean 581c127f). Bead-selection automation by Jev/Laya (criteria: pulled? rotation radius, circular
  rotation trace, pulled as much as expected - computed from tracking data, so text-only Jev can judge) is DEFERRED
  until the coding is done (user 2026-10-15 "당장은 프로그램이잖아. 나중에 코딩 마치면 그 때 Jev 통한 자동화 생각해보면
  되지"); no pull tests now.
- GitHub repo github.com/SihNho/MT_LabVIEW is PUBLIC on purpose (user 2026-10-15 "퍼블릭으로 둘거임") - do not ask
  again; keep the secret-shape scan before every push. gh CLI installed 2026-10-15 (C:\Program Files\GitHub CLI\gh.exe),
  logged in as SihNho via the user's own `gh auth login` (keyring, https).
- Branch policy (user 2026-10-15 "현재 진행코드를 항상 마스터로 두고, 브랜치가 생길 경우 이전 기록을 브랜치에"): the
  current code lives on master; an old state goes to a branch (archive/full-harness-20261015 = master before the lean
  merge 48f23831). The lean worktree's branch bench/lean-20261013 differs from master only by its session rules
  (CLAUDE.md / AGENTS.md / .claude/settings.json, kept per branch by .gitattributes merge=ours + `git config
  merge.ours.driver true`); merge lean -> master after each run (and master -> lean only while no run is going).
- GitHub: upload once a day (scheduled task github-daily-push, tools/git_push.py) and on explicit request; never per cycle.

**Why:** the gates cost more than they prevented once the tools existed; a single session kept context and found a real defect.
**How to apply:** write lean task files, review each report, re-check the acceptance from raw files, merge to master;
when the user announces 실험중, write the queue STOP file and stop a running lean session. See [[claude_main_gpt_debate_peer_only]].
