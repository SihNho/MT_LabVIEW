---
name: finish-the-cycle-without-stopping
description: "Once a work cycle has started, run it to the end — the user does not want it paused mid-way to ask them something unless stopping is genuinely necessary"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 97b1695e-68c2-4985-8cac-1ca3097b3b15
  modified: 2026-09-16T06:11:33.104Z
type: decision
status: in-force
date: 2026-09-16
source: memory/finish_the_cycle_without_stopping.md
---

# Once the loop is turning, keep it turning

On 2026-09-16 the user interrupted a session to say:

> *"한 번 루프 돌기 시작했을 때, 꼭 필요하지 않다면 중간에 멈추지 않고 끝까지 루프 계속 진행했으면 좋겠음.
> 규약에도 갱신하면 좋을듯."*

("Once a loop has started running, unless it is really necessary, I would like the loop to keep going to the end
without stopping in the middle. Worth updating the rules too.")

## What triggered it

I had stopped mid-cycle and put a question to them with `AskUserQuestion`. The question was real — a gate was
blocking the build because of a date-comparison bug, and fixing a gate that blocks me is the kind of thing that
normally needs their sign-off — but stopping was still the wrong default. There was other work in the cycle I could
have carried on with, and the pause put the cycle in their lap instead of mine.

## What this changes

**The default is to carry the cycle to its end and report once**, not to pause at each decision point. When
something is uncertain mid-cycle:

1. Do every part that does not depend on the answer — the whole of it, not the easy half.
2. For the part that does depend on it, state the assumption in writing, proceed under it, and flag it in the final
   report so the user can overturn one thing rather than unblock ten.
3. Only actually stop when proceeding under *any* assumption would be unsafe, destructive, or would make the work
   useless if the assumption turns out wrong.

This is a matter of **where the waiting happens**. A question asked mid-cycle makes the user the scheduler; a
question asked in the closing report lets them answer when they get to it, with the finished work already in front
of them. It sits alongside the project's standing rule that their messages arriving mid-work are interrupts to be
answered immediately (CLAUDE.md 2b) — I stay responsive to *them*, but I do not hand *them* the job of keeping the
cycle moving.

It also lines up with the project's own cost discipline: one cycle per session, one runner per batch, one
notification. A cycle broken into "ask, wait, resume" is several sessions' worth of context for one session's work.
