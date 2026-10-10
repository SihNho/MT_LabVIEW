---
name: close-every-reference-verified-by-handle-count
description: Closing VI Server references is mandatory in every op and every COM client, the rule must be written into the project rules, and compliance is VERIFIED by measuring LabVIEW's handle count — the user found LabVIEW sluggish and "not responding" after 30 h of scripting had leaked ~32,000 handles
metadata:
  pinned: false
type: decision
status: in-force
date: 2026-09-06
source: memory/close_every_reference_verified_by_handle_count.md
---

# Close every reference — codify it, and verify it by measurement

User, 2026-09-06, after finding LabVIEW sluggish and repeatedly "응답 없음" during manual use, and
after Claude measured the running instance at 32,480 handles (normal idle: a few thousand):
*"이후 close reference 필수로 사용하도록 하고, 규칙에 확실히 규정할 것. 그리고 해당 규칙이 반영되는지
검증. 충분히 검증 되었으면 이후 작업 시작."*

What this means in practice:
- **Every VI Server / COM reference is closed** — in op VIs (`Close Reference` on every ref an op
  opens: Open VI Reference, Traverse for GObjects arrays, Get Outputs, New VI Object, creator
  outputs) and in Python clients (release cached VI references on exit; never leave a killed or
  hung client holding references; abandoned watchdog threads still hold marshalled interfaces).
- **The rule is written where it is enforced**, not only remembered: CLAUDE.md, the skill
  reference, and a mechanical check (handle count in the health/prep step with a threshold that
  triggers a LabVIEW restart).
- **Compliance is verified by numbers**: LabVIEW's handle count before and after a batch of the
  operation types (reporter runs, open/revert cycles, process exit, a killed client). "The VI
  goes idle so LabVIEW closes refs" is a claim to test, not a reason to skip the measurement.
- Only after that verification does construction resume. The same pattern as every other rule
  the user has had to restate: a rule that lives in prose and is not measured gets bypassed.
