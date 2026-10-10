---
name: no-serial-on-the-frame-path
description: "The user's hard constraint (2026-09-16) — not one frame may be lost to motor/serial communication, because VISA can stall a loop; and stage drift makes focus correction continuous, not occasional"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 2b7a154c-b779-4f1a-8095-9dd814570b41
  modified: 2026-09-16T03:04:43.833Z
type: decision
status: in-force
date: 2026-09-16
source: memory/no_serial_on_the_frame_path.md
---

# Not a single frame lost to motor communication. Serial never touches the frame path.

The user stated this on 2026-09-16, in two parts that belong together.

## 1. Focus correction is continuous, not an occasional event

> *"ASI responds when needed only, of course. But as with my experience during the experimentation, the focus
> re-adjustment is not so seldom. Just without existence of motor moving, due to various factors (thermal drift,
> sample holder pin might be somehow shifting slightly, or for some other reasons that I don't know) the sample
> stage itself drifts. I can't tell how frequent it is, but it is not trivial. It needs continuous adjustment."*

The sample stage drifts **on its own**, with nothing commanded to move — thermal drift, the sample-holder pin
shifting, and causes the user cannot name. So the ASI focus path is exercised throughout a run. Any analysis that
treats the ASI serial round trip as a rare branch whose cost can be amortised away is wrong at the premise, and I
have made that mistake: a plan review once deprioritised the ASI loop precisely because "its serial is
conditional".

**How frequent is unknown and must be measured, not guessed.** "Not trivial" is the user's own bound.

## 2. The constraint that follows, and it is an acceptance criterion

> *"Regardless of how frequent it is, I don't want to have even a single frame loss coming from the motor
> communication if possible. And it is so clear that serial communication through VISA can somehow stall the loop,
> and cause unwanted frame stop. This will hurt the frame consistency and might disturb the quality of my data."*

So the design rule is absolute in shape, not statistical: **no VISA/serial call may sit anywhere on the frame
acquisition path.** It is not "keep the serial cost small" or "serial is fine because it is usually skipped" — a
stall is a data-quality defect, and a mechanism that *can* stall the frame loop is disqualified even if it usually
does not. Serial lives in its own loop, which owns its VISA session exclusively, and communicates with the frame
path only through a non-blocking handoff.

This is the same shape as the camera rule the user set the day before (the camera free-runs; nothing we build may
gate acquisition). Both say: the acquisition path is sacred, and every other loop must be unable to hold it up —
by construction, not by being fast enough in testing.

## Why the user cares, in their terms

Frame consistency is what makes the time series trustworthy. A stalled loop does not merely cost throughput; it
puts a hole in the record at a moment chosen by a serial device rather than by the experiment.
