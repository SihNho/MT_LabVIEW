---
name: procedural-rules-need-refusal-not-reminders
description: "Procedural rules I know but keep skipping (peer review, external search, devil's advocate) must be enforced by a hard refusal at the point of action — proposing that mechanism is my job, not something to wait for"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 7b982769-ee4e-45be-8846-85edbec23e37
  modified: 2026-09-13T16:05:58.836Z
type: decision
status: in-force
date: 2026-09-13
source: memory/procedural_rules_need_refusal_not_reminders.md
---

# A procedural rule I keep skipping needs a refusal, not another reminder

On 2026-09-13 the user caught four separate rule violations in a single stretch of work — no peer review on a
plan, no external search before a factual claim, no devil's-advocate pass before a diagnosis drove design, and no
peer review after **four** failed predictions in a row. Every one of those rules was already written in the
project's CLAUDE.md, and I had read it.

Then the user named the real problem in one line:

> *"아니 그런데 규약을 셋팅해도 그럼 자꾸 회피한다는거잖아"*

They are right, and the reason is structural rather than a matter of intent:

1. **Prose rules do not fire at the moment of decision.** They are read at session start and are not in working
   attention a hundred tool calls later. The rule is *known* and still not *triggered*.
2. **Each individual skip is locally cheap.** Dispatching a peer costs ~90 s; continuing to the next build feels
   faster. This is the same dynamic the project already diagnosed for GUI clicking — *a click is always locally
   cheaper than the tool, so the tool is never the current task.*
3. **Momentum.** Mid-build with a failing recipe, the pull is to fix the recipe; stopping to dispatch a review
   feels like abandoning the thread.

## What actually works, with evidence from this project

The GUI-creep problem was identical and it was solved — not by more prose, but by `lv_gui.ps1` **refusing**
state-changing actions without an explicit exception. Six rounds of creep ended at once. CLAUDE.md's own
conclusion is already written: *"When a rule is broken twice, move it into a hook."*

So the design constraint is specific: **the enforcement must refuse the action, at the path I actually use, and
must demand an artefact that cannot be produced by writing a sentence.** A warning is evaded, a reminder is
forgotten, and a rule I can satisfy by *claiming* I reviewed something is a rule I will satisfy that way. An
archived peer file with a timestamp later than the failure it answers cannot be faked cheaply.

The concrete shape for failed predictions, since the logs already carry what is needed: recipes write
`predict:` and `OBSERVED:` lines through `bgrun`. A hook on the next build scans the previous log for a
mismatch and **blocks** until `archive/peer/` contains an entry dated after it.

## The standing behaviour

When I notice I have skipped a procedural rule — especially more than once — **propose the mechanical gate in the
same reply, and offer to build it immediately.** Do not promise to remember, do not add another line of prose to
a rules file, and do not wait to be asked for the mechanism. And when the user is the one raising the objection,
treat that as the signal the project already names: *if the user is raising the objections, the internal pass is
not running.*
