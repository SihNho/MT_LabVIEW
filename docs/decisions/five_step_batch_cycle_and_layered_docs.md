---
name: five-step-batch-cycle-and-layered-docs
description: "The user's standing work cycle: peer-review the plan, write ONE long script, execute it as a batch, read results, revise — and keep the .md docs layered so nothing is missed and only the needed layer is read"
metadata:
    pinned: true
type: decision
status: in-force
date: 2026-08-31
source: memory/five_step_batch_cycle_and_layered_docs.md
---

# Work in planned batches, not verified single steps — and layer the docs

On 2026-08-31, after watching an assembly session crawl through step-by-step GUI/COM work, the user
prescribed the work cycle explicitly:

1. **피어리뷰 및 계획 먼저** — plan first, and peer-review the plan itself (dispatch a peer to
   attack it) before any construction.
2. **스크립팅으로 길게 작성** — write the WHOLE build as one long script. Every name, position and
   argument is resolved at planning time, not discovered mid-run.
3. **스크립팅 실행해서 연속으로 VI 실행** — execute the script as a batch, ops chained
   continuously.
4. **결과 판독 및 리비전** — read the results (counts, ExecState, screenshots) afterwards and
   revise.
5. Repeat from 1 as needed.

The failure mode this replaces: interleaving discovery, editing and verification one step at a
time, paying a round trip per step, hitting unknown terminal names mid-build, and stalling on each
one. Discovery belongs in steps 1–2 (against the name registry and docs); execution should be a
replay that approaches one VI per minute. Verification consolidates into step 4 instead of
bracketing every edit.

## The documentation half of the instruction

The user also diagnosed why things were being missed: *".md파일이 너무 길어지다보니 너가 자꾸
놓치는게 아닌가"* — the working docs (STATUS.md near 100 KB) had grown past what a session actually
re-reads, so recorded contracts were being rediscovered the hard way. Standing instruction:
**계층화** — keep the docs layered so nothing is lost AND only the needed layer is read:

- A **short top index** (STATUS.md: lock, current state, next actions, pointers — readable in one
  screen) that a cold session always reads in full.
- **Topic files one level down** (a verified-name registry, build recipes, technique references)
  that are opened only when that topic is being worked.
- **Narrative to the archive** as before — never appended to the working layer.

When a working doc starts needing scrolling to find the current state, that is the signal to push
content down a layer, immediately, not at the next cleanup.
