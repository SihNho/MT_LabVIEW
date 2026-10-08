---
type: archive
status: frozen
date: 2026-10-08
tags: [decisions-pending, verbatim, relocation]
---

# decisions_pending.json — answered items' long fields, VERBATIM (relocated 2026-10-08 by the cycle-150 judgement session)

Why: `docs/protocol/decisions-pending.json` limits `question` to 300, `answer` to 300, `recommendation` to 200 and each
option to 80 characters. Four ANSWERED items written before those limits were checked broke them, so
`py tools/protocol.py validate tools/bench/decisions_pending.json` failed and `tools/hooks/guard_write.py` refused the
file when cycle 150 appended D-2026-10-08-01. The fields below are the original text, unchanged; the live file now holds
a shorter text with a pointer here. Ids, status, answers' meaning and answered_at are unchanged. Nothing was deleted
(CLAUDE.md rule 4: moved, not rewritten).

## D-2026-09-28-01 (asked 2026-09-28T11:55 by chat; answered)

question:
"The next build step (PD233(k)) adds the frame pool between the camera loop 1.1 and tracking loop 1.2: 20 image slots, and when all 20 are waiting, 1.1 skips reading the NEWEST camera frame. So under sustained overload tracking works through older queued frames (up to 20 behind, ~0.2 s at 90 Hz) and the newest frames are the ones lost. Your 2026-09-15 rule (docs/decisions.md:25) says the opposite: discard the backlog and take the newest frame. Every frame keeps its own buffer number, so timing labels stay correct either way; what differs is which frames are lost and how far tracking lags. Which do you want?"

options[0]:
"latest-wins as decided on 09-15: when tracking falls behind, it drops the queued older frames and takes the newest (the pool stage is changed to do that)"

options[1]:
"keep the planned pool: skip the newest read when 20 are waiting (lag up to 20 frames, oldest kept)"

blocks (the schema allows milestone ids only; "R4" was dropped from the live file):
["M4", "R4"]

answer:
"ALREADY DECIDED by the user 2026-09-15 (memory prefer_the_freshest_frame_over_a_complete_backlog; docs/decisions.md:25), re-confirmed 2026-09-28 15:3x (\"위에 프레임 관련해서는 내가 말한 내용이 있음 ... 우선순위가 있는데\"). Priority: (1) NO CORRUPTION - image memory and its buffer number change together and the consumer verifies them; a pixel/number mismatch is data corruption. (2) LATEST-WINS - discard the queued backlog, read the newest frame (time-series rigor); a gap recorded by the buffer number is fine. (3) FALLBACK - if 1 and 2 cannot be made provably safe, acquisition and tracking may stay in ONE sequential loop. So the planned full=>skip-newest branch is WRONG and must become latest-wins with the buffer-number check, or the fallback."

## D-2026-10-01-01 (asked 2026-10-01T14:40 by cycle 123; answered)

options[0]:
"keep 6 unrun files; allow up to ~40 rows per build step for these steps, each with a full test-copy run before the real build"

options[1]:
"keep 15-25 rows per step; raise the unrun-file limit to 9 (the first full run comes about 3 build steps later)"

recommendation:
"the first option: the first end-to-end run (the reason for your limit) comes sooner, and recent steps passed first time after their test-copy run (P2a 27/0, P2b 41/0). The camera-loop control part (~24 rows) goes ahead under either answer."

## D-2026-10-02-03 (asked 2026-10-02T13:30 by cycle 135; answered)

options[2]:
"keep 6 and 40: first make the current file runnable and run it (several extra cycles)"

## D-2026-10-02-04 (asked 2026-10-02T15:00 by cycle 136; answered)

options[1]:
"keep 6: P4 is one step (one file), built over several LabVIEW sessions whose in-between files are deleted"

options[2]:
"keep 6 and 40: first make the current file runnable and run it (several extra cycles)"
