---
name: split-big-steps-and-save-intermediates
description: "The user's 2026-09-19 project-wide rule — large chunks of work, and any step that becomes a bottleneck, are split into finer steps that each SAVE an intermediate artefact (a VI on disk, a file the user can open); a one-shot script that keeps everything in memory until the end is not acceptable"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: b5d0cc76-fda8-4724-8899-5a019fc98595
  modified: 2026-09-19T08:21:01.090Z
type: decision
status: in-force
date: 2026-09-19
source: memory/split_big_steps_and_save_intermediates.md
---

# Big or blocked work is split into steps that save their intermediate results

On 2026-09-19 the user found that ten overnight attempts at the D1 loop-restructure had left **nothing to look
at**: a 2,800-line script edited a copy of the VI entirely in LabVIEW memory, died at the same re-wiring stage every
time, and the "preserved" copies on disk were byte-identical to the untouched original. Their ruling, meant for the
whole project, not just this step:

> *"앞으로도 프로젝트 방향성에 관해서 큰 덩어리의 프로젝트는, 혹은 병목이 생긴 부분에서는, 세부적으로 쪼개서
> 중간과정 저장하며 진행하는 방식으로 규칙 수정 필요할듯."*
> *"일일히 배선 하나하나 별도 스크립트를 쓰는 건 낭비가 맞지만, 필요할 때에는 프로젝트 스텝을 더 세분화하여
> 쪼개는 필요도 있겠어."*

They also named what is still ahead after the parallelisation — EMCCD connection and sync, display improvement,
and more — so this is the working style for the rest of the project.

## How I apply it

- **A step is not done until it has left a file.** Every build stage saves its intermediate VI (or data file)
  under `claudeDev`, records its hash, and the next stage starts from that file — in a fresh LabVIEW instance when
  the stage touches VI Scripting. The user must always have something to open and check.
- **Default granularity is moderate**, not one script per wire: one saved artefact per natural stage (copy →
  structures → moves → re-wiring in batches of 10–15 rows → census → save). Splitting further is done only when
  a stage becomes a bottleneck.
- **Re-splitting is triggered, not felt**: the same stage failing twice at the same place, or a stage that ends
  without a saved artefact, means the next cycle's first act is a decomposition of that stage into smaller saved
  steps — never another full-length retry under a new file name.
- The decision of *how* to split belongs to the judgement session (a design decision), but the *trigger* is
  mechanical so no one has to notice it.
