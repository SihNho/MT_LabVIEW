---
name: recurring-errors-become-peer-review-triggers
description: "Any error class that repeats (e.g. \"STALLED LabVIEW client\" alerts) must be made a mandatory peer-review trigger and written into the rules mechanically, not just handled case by case"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 7b982769-ee4e-45be-8846-85edbec23e37
  modified: 2026-09-14T01:23:36.099Z
type: decision
status: in-force
date: 2026-09-14
source: memory/recurring_errors_become_peer_review_triggers.md
---

# A repeating error class becomes a mandatory peer-review trigger, encoded in the rules

On 2026-09-14, while an autonomous loop was running, the session's stall-detector hook reported
"STALLED LabVIEW client(s) ... Do not wait: diagnose now and stop the task" for the third or fourth
time that week. The user's reaction was not "fix this stall" but a standing instruction:

> "이런 에러들도 반복되는 것 같으니 피어리뷰 반드시 필요하겠어. 규율에 적용하도록"

That is: when the same kind of error keeps coming back, it is evidence that the current explanation
of it is wrong or incomplete, so every recurrence must go through the full peer-review protocol
(multi-agent attack, monitored dispatch, devil's-advocate pass) — and the requirement must be put
into the project's rules, not remembered per incident.

## How to apply it

- Treat a recurring error alert exactly like a failed prediction under CLAUDE.md: the implicit
  prediction "this client finishes" or "this build compiles" did not hold. Do not diagnose it alone
  and move on, even when the local cause looks obvious (a false positive in the detector, a slow
  purge loop). The user's point is that "obvious" local causes are what let the class recur.
- Encode the trigger mechanically, the way the project encodes every rule that was broken twice:
  the detector writes a record file that the build gate (`tools/hooks/guard_peer.py`) treats as a
  failing log, so the next build stays blocked until a peer review newer than the record is
  archived under `archive/peer/`. A prose sentence in CLAUDE.md alone is not what the user asked for.
- Generalise: whenever an error message or alert appears for the second time in a session or across
  sessions, ask "is this class already a peer-review trigger in the hooks?" and if not, make it one
  in the same session, then say so to the user.

The user's reason, stated repeatedly across this project, is that prose rules get skipped under
pressure ("규약을 셋팅해도 그럼 자꾸 회피한다는거잖아"), so only a mechanism that refuses the next step
counts as applying a rule.
