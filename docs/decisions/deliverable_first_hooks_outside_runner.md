---
name: deliverable-first-hooks-outside-runner
description: "The user's 2026-10-08 decisions — a runner cycle runs its LabVIEW deliverable card before any tooling card, and no runner card may edit tools/hooks/** (the chat drains hook false positives between runs and tells the user)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: b607b493-a66f-4081-b122-a7a95d2c2a67
  modified: 2026-10-08T11:22:46.755Z
type: decision
status: in-force
date: 2026-10-08
source: memory/deliverable_first_hooks_outside_runner.md
---

After cycles 147–149 spent about $130 for one adopted file, mostly on gate clean-up (gate false-positive drains, suite
re-runs, hook edits needing hand-backs), I proposed three changes. The user approved two ("두 가지 모두 적용하자") and
questioned the third ("훅 수정 권한이면 조금 위험하지는 않을지?"), which I withdrew.

- Deliverable first: the LabVIEW build/scratch/adopt card goes before gate-fp drains and regression proofs, unless that
  very gate refuses the deliverable's launch. Encoded in tools/bench/assign/purpose_addendum.md, assign_prompt.md,
  tools/cycle_prompt.md, CLAUDE.md §3.
- Hooks are never changed inside a runner cycle, even if the purpose names them: guard_assign `never_in_runner_globs`.
  The chat drains hook false positives between runs and reports what changed.
- The user was annoyed that terminal-NAME keys survived after repeated discussion: S1 fixed plan addressing only and
  I scoped it too narrowly; result gates D/TD/PB still used names (card chat-T6 moves them to position keys).

**Why:** hooks are the mechanical form of the user's rules (originals, motors, timeouts, reviews); a session that can
edit its own guard can weaken them. Tooling work had started to crowd out deliverables.

**How to apply:** when a rule change is agreed, apply it to EVERY place the same key or check is used, not only the
path that just failed — check gates and checkers too. Related: [[guards_exist_to_catch_errors_early]],
[[purpose_cycles_assignment_session]], [[deliverable_build_goes_first_in_a_cycle]].
