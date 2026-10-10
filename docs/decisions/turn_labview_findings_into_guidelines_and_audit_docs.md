---
name: turn-labview-findings-into-guidelines-and-audit-docs
description: "Write up any noteworthy LabVIEW coding finding as a reusable guideline, and periodically audit the project's docs, skills and structure rather than only appending to them"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 72babae7-a0eb-4591-80eb-3f88511dbec4
  modified: 2026-08-25T17:34:22.631Z
type: decision
status: in-force
date: 2026-08-25
source: memory/turn_labview_findings_into_guidelines_and_audit_docs.md
---

# Every noteworthy LabVIEW finding becomes a guideline; audit the doc set periodically

The user extended an earlier instruction (2026-08-26). It was originally about GUI-control tips; the
general form is: **"not only for the GUI control tip itself, if there is note-worthy information when
you perform the LabVIEW coding, had better make a guide-line."** Anything learned while actually
writing LabVIEW code — dataflow rules that make a wire illegal, what a given error code really means,
which node inputs are required versus optional, how a scripting API expects to be driven — should be
captured as a durable guideline, not left inside a dated session narrative where it is effectively
lost.

The second half matters as much: **"to also enhance the performance of overall project, check the
overall guide-lines, skills, .md s or overall structures when needed."** So do not only append.
Periodically step back and audit the whole set — the project's `.md` files, any available skills, and
the overall structure — looking for documents that have drifted out of date, contradict each other,
duplicate content, or have grown so long that a cold start is expensive. This project has already
been bitten once by that: `STATUS.md` had swollen to ~274 lines while still claiming to be short,
which defeated the whole strategy of refreshing sessions often and keeping state in files.

The underlying goal is that the project gets **cheaper to work on over time**. Knowledge that stays
only in a transcript has to be re-derived by the next session; knowledge promoted into the right
guideline file compounds instead. When adding something, pick the file by audience and durability —
technique into the tool's own header or the playbook, mechanism explanations into the user's learning
document, session narrative into the worklog, and only "what is true now" into the status page.
