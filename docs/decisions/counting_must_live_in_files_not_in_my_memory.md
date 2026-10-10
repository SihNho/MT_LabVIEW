---
name: counting-must-live-in-files-not-in-my-memory
description: "When proposing \"do X after this repeats N times\", the counter must be a file the machine reads — the user caught that a rule whose counter is my memory is not a rule at all"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 6959fd57-add7-402e-9ed9-9a94ff2b4d5f
  modified: 2026-09-15T05:02:28.655Z
type: decision
status: in-force
date: 2026-09-15
source: memory/counting_must_live_in_files_not_in_my_memory.md
---

On 2026-09-15 I proposed adding a mechanical device "when the retrospective repeatedly flags the same violation".
The user asked the one question that dismantles it:

> *"회고가 반복해서 위반을 지적하는지는 어떻게 알아? 그걸 규약에 넣어서 일정 회수 이상 반복되면 추가한다는거야?"*

The proposal was not executable. The thing that would count the repetitions was my own recollection across sessions,
and a count I keep is a count I can decline to keep. This is the same defect as promising to remember a procedural
rule instead of building the refusal — which this project had already diagnosed once.

**The correction, now built into the project:** a repetition-based rule needs three things, none of which may be me.

1. **A machine-readable record at the point of observation.** The peer's retrospective must end with
   `VIOLATION: <slug>` lines drawn from a fixed list in CLAUDE.md. Free prose cannot be counted.
2. **A counter that reads the files, not the conversation.** `tools/violations.py` greps
   `archive/peer/*retrospective*.md` and tallies slugs — and deliberately ignores the "What was done with it"
   annotation, so my own writing cannot inflate or deflate the tally.
3. **A gate that acts on the count.** `tools/hooks/guard_cycle.py` refuses the next recipe build when a slug reaches
   3, and refuses it while the previous cycle has no retrospective newer than its build logs.

**The wider lesson, which generalises past this project:** whenever I propose a rule of the form "after N times, do
Y", I must name the artefact that stores N and the code that reads it in the same breath. If I cannot, the honest
move is to build the device immediately instead of deferring it behind a count nobody keeps — as the user then
decided for the compliance audit, which had no reason to wait for evidence of repetition at all.
