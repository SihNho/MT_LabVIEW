---
name: feedback-shared-labview-checkpointing
description: "The user's LabVIEW instance is shared with real experiments and can be reclaimed at any moment — keep STATUS.md's checkpoint log current during work, not just at session end"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 52d900cc-eddf-491c-ac00-c5055911beed
  modified: 2026-08-25T10:58:15.263Z
type: decision
status: in-force
date: 2026-08-25
source: memory/feedback_shared_labview_checkpointing.md
---

The user runs real magnetic-tweezers experiments on the same machine and LabVIEW instance that
GUI-automation work in this project drives. They can and will **forcibly interrupt a Claude session
at any moment** — no warning, possibly mid-edit — to reclaim LabVIEW for an experiment. Work must be
resumable from wherever it was interrupted, potentially picked up by a different chat/session/LLM.

**Why:** stated directly by the user (2026-08-25): "그동안 실험도 동시에 진행되야" — experiments have
to run concurrently with any revision work, on the same shared resource, so they stop Claude sessions
outright to take LabVIEW back rather than waiting for a natural stopping point.

**How to apply:** during active GUI/LabVIEW work in this project, update `V6_ParallelLoop/STATUS.md`'s
checkpoint log after each real milestone — not every click, but every "something meaningfully changed
or was decided" moment (a structure placed, a wire connected, a file saved, a decision reached, an
unexpected state discovered). Each entry should let a cold read (a different session with zero prior
context) know exactly: what was just done, what LabVIEW's current window/file state is, and what the
precise next step is. Treat "the user vanishes right now" as the normal case to design around, not an
edge case to handle if there's time. See `CLAUDE.md` in the project root (written 2026-08-25
specifically to carry this rule forward) and [[project-v6-parallelization]].
