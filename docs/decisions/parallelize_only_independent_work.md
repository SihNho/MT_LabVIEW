---
name: parallelize-only-independent-work
description: "The user's 2026-09-28 rule for parallel sessions — only run work in parallel when its result cannot be changed by the work in progress; tracks that take the current build's outcome as input wait, and are parallelised only after an interface contract fixes that input"
metadata:
  node_type: memory
  pinned: false
  originSessionId: a5bcbf27-1eb1-4a4c-b234-98f27fbcff51
  modified: 2026-09-28T10:38:48.646Z
type: decision
status: in-force
date: 2026-09-28
source: memory/parallelize_only_independent_work.md
---

# Parallel only what the running work cannot change (user, 2026-09-28)

The user offered to run many sessions in parallel ("여러 세션을 병렬로 돌려도 무관하겠는데"). I proposed designing the
display, motor, scheduler, focus and GPU tracks beside the ring-buffer build. The user pointed at the flaw: "한 싸이클을
마쳤을 때 다음 싸이클에 변동이 생기는 일이라고 하면, 병렬이 안되는 거잖아". Every one of those tracks takes the ring
buffer's final shape as input, so designing them early is building on a guess — the same failure as the pool direction.

## How I apply it

- Before proposing parallel work, list for each task what it takes as input; if that input is produced by work still
  running, it is not parallel. Say so rather than proposing it.
- Safe parallel work: facts from files that never change (the original VI), tool/test debt, the next step's prep.
- To unlock real parallelism, first freeze the shared interface (a contract of what each loop publishes and reads),
  checked against the user's rules; only then design the dependent tracks side by side.
- Parallel sessions communicate through files, not conversation: each proposes into a shared change ledger, a script
  checks conflicts, a combined offline simulation verifies the plans compose — and the JUDGEMENT session alone
  reconciles and finalises ("결국 계획을 조율하고 확정하는건 판단 세션이 진행해야함", user 2026-09-28).
