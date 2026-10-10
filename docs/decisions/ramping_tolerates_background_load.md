---
name: ramping-tolerates-background-load
description: "The user's 2026-10-07 note — ramping experiments are relatively insensitive to occasional frame loss, clamping experiments are not; offline background work may continue during ramping, but ask about pausing it during clamping"
metadata:
  node_type: memory
  pinned: false
  originSessionId: b607b493-a66f-4081-b122-a7a95d2c2a67
  modified: 2026-10-07T05:39:38.427Z
type: decision
status: in-force
date: 2026-10-07
source: memory/ramping_tolerates_background_load.md
---

On 2026-10-07, while an experiment was about to start on the lab PC and an offline (LabVIEW-free) tool-fix agent was
running, I measured the load (CPU 23 % on 12 logical cores, ~2 GB RAM for the Claude processes) and offered to pause it.
The user said to continue: "어차피 ramping이라 frame에 비교적 덜 민감함. clamping 보다야".

## How I apply it

- When the user announces an experiment and LabVIEW-free background work is running, ask which kind it is if unknown.
- Ramping: offline background work (code edits, offline self-tests, transcript reads) may continue.
- Clamping: frame timing matters more; offer to pause background work (resumable) before it starts.
- In both cases LabVIEW, camera and motors stay untouched while the rig state is 실험중 (rule 1b).
