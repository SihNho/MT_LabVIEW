---
name: delivery-cycles-are-a-means-to-the-final-step
description: "After two outcome reviews found zero runnable experimental VIs, the user chose delivery-first (2026-09-16, option A — smallest runnable VI: original copy + stop/shutdown + file writing) but said plainly that this is an intermediate step and the final seven-loop restructure remains the goal"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 97b1695e-68c2-4985-8cac-1ca3097b3b15
  modified: 2026-09-16T12:53:01.503Z
type: decision
status: in-force
date: 2026-09-16
source: memory/delivery_cycles_are_a_means_to_the_final_step.md
---

# Deliver something runnable first — and remember it is a step, not the destination

Two outcome reviews in a row (2026-09-15, 2026-09-16) found the same thing: many tools, many reviews, **zero
runnable experimental VIs**; the user would still run the original VI next week. Per the rule the user set on
2026-09-15, a repeated outcome violation stops the work for a re-plan. On 2026-09-16 the user chose:

> **"A로 진행하자."** — a delivery cycle: the smallest runnable VI from what is already known. The candidate
> named in the re-plan: a copy of the original with the frame loop left as-is and **stop/shutdown + actual file
> writing** added first (the outcome reviewer's own ordering). Phase A's remaining analysis (A4–A7) only as the
> running VI turns out to need it.

And, in the same message, the boundary of that choice:

> *"동의. 다만 여기는 중간 과정일 뿐 결국에는 최종 스텝으로 나가야함."*

So delivery-first is **ordering**, not a change of goal. The final step — the seven-loop restructuring, GPU
tracking path as the default top level, CPU-parallel as the second deliverable, computation preserved
bit-for-bit — is still where this ends. A delivery cycle that quietly becomes the new destination is the same
drift the outcome review exists to catch, from the other side.

## How I should behave

- Each delivery cycle names, in its plan, which final-step requirement it advances and what it leaves.
- Do not let "make the original usable sooner" reorder the maths — rule 1a and the "build it right" memory still
  hold; what changes is only which runnable thing exists first.
- When a delivery cycle's product runs, the next question is "what does the final step need next", not "what
  else can be delivered".
