---
name: tools-allowed-when-cycle-judges-them-necessary
description: "The user's 2026-09-24 decision lifting the 2026-09-18 \"no more devices\" order — a cycle's judgement session may build a tool (op VI, script verb, reader) when it judges the tool necessary, because the ban kept leaving holes that cost whole cycles"
metadata:
  node_type: memory
  pinned: true
  originSessionId: 1e5293f3-09a7-4b72-9393-fcba8dd55703
  modified: 2026-09-23T18:09:46.504Z
type: decision
status: in-force
date: 2026-09-23
source: memory/tools_allowed_when_cycle_judges_them_necessary.md
---

# The judgement session may build the tools it judges necessary (2026-09-24)

On 2026-09-18 the user stopped tool/device building ("장치는 더 만들지 말고 계속 진행") because the project was
building machinery instead of delivering. On 2026-09-24, after cycle 68 lost about 25 minutes because two scripting
verbs were missing (wiring to a loop's `i` terminal, creating `Not Equal?`/`Select`) and the session had to
redesign the stage to route around them, the user lifted the ban:

> "음... 새로운 도구 만드는 걸 내가 막아뒀는데, 보니까 계속 구멍이 생기는 것 같아. 루프 판단에 따라 필요한 도구는
> 만드는 걸 허용할게"

## How I apply it

- A cycle's JUDGEMENT session decides whether a missing tool is needed; if yes, the tool is built (by a material
  session) in that cycle, before or alongside the deliverable, instead of designing around the hole.
- "Necessary" means the tool unblocks the current stage or will be needed again by the same class of work (loop
  terminals recur in every loop split). A tool for a one-off is still not built; the session says why it chose a
  workaround.
- Every tool still follows the existing rules: peer-reviewed plan, ≤120-line stage files on `stagekit`, reference
  hygiene proven by handle count, measured on a labelled case before it acts.
- The 2026-09-18 order is no longer cited as a reason to skip a tool. The retrospective slug threshold ("at 3 of the
  same slug build the device") is treated as resumed under the same words; if the user meant only scripting tools,
  they overturn that one sentence.
- Deliverable-first ordering (2026-09-18) still holds: a tool is built because the deliverable needs it, not
  instead of the deliverable.
