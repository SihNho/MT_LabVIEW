---
name: deliverable-build-goes-first-in-a-cycle
description: "The user's 2026-09-18 ordering rule — a cycle's FIRST act is the deliverable build dispatch, and machinery repairs, watchdog reviews, audit fixes and doc relocation all wait until after it has RUN"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 3c595a56-57b6-4661-bbcf-6a8030686415
  modified: 2026-09-18T14:11:59.420Z
type: decision
status: in-force
date: 2026-09-18
source: memory/deliverable_build_goes_first_in_a_cycle.md
---

# The build dispatch goes first in a cycle; process work waits until after it has run

On 2026-09-18, after watching a plain copy of the original VI run its experiment loop unattended (their words:
*"상당히 고무적인데 지금은 뭘 하고있는거임?"* — "this is quite encouraging, but what are you doing right now?"),
the user wrote a standing ordering rule into the project's STATUS file:

> TWO CYCLES SINCE D0 HAVE NOT TOUCHED D1. The next cycle's FIRST ACT is a D1 BUILD dispatch. **NO machinery
> repairs, NO watchdog reviews, NO audit fixes, NO doc relocation before that dispatch has RUN**; those go AFTER
> the D1 dispatch returns, or into the retrospective as findings. **A cycle that ends without a D1 build log is a
> wrong-ordering cycle by definition.**

## What it actually forbids

It is an ordering rule, not a licence to skip process work. Repairs, reviews, audits and documentation hygiene all
still happen — they happen *after* the deliverable's build has produced a log, or they are recorded as findings in
the retrospective. The last clause is a definition, so it applies to every future cycle and needs no restating:
a cycle with no build log for the current deliverable has mis-ordered itself, whatever else it accomplished.

## Why I needed telling

The cycle in which this landed opened by spending its first two dispatches on exactly the work the rule names —
two device repairs that the *previous* cycle's NEXT section had put first — and only reached the build afterwards.
The build did eventually run, but the cycle's own retrospective independently scored it
`VIOLATION: wrong-ordering | loss_min=41 | loss_usd=2.7466`. The failure mode is subtle and worth naming: each
individual piece of process work was justified in writing, gated, peer-reviewed and green. Legitimacy of the parts
is not the test. The test is whether the deliverable moved.

Two practical consequences:

- **A stale NEXT section is not authority against the user.** The previous cycle's plan said "repairs first"; the
  user's later instruction reverses it, and the later statement wins. Read STATUS fresh at the start of every
  cycle, because the interactive chat window edits it to redirect the runner mid-flight.
- **Gate-clearing work counts as process work.** Prior-art releases, violation dispositions and retrospective debts
  feel like part of the build because they block it, but they are the thing the rule is aimed at. Where such a gate
  genuinely blocks the first dispatch, clear it in the *same* dispatch as the build rather than as a cycle of its own.
