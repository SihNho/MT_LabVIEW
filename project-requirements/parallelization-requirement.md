---
type: decision
status: current
date: 2026-08-24
tags: [requirements, user-source]
---

To maximize the CPU loading, and to minimize the frame dragging, parallelization on the existing version code is necessary.

1. The while loop part that comes after 'Done Picking 
Beads?' (which records the bead radial profile by multiple for loop) needs to be parallelized in multiple parallel while loops.
2. The target while loop performs multiple functions at a time
	1. Motor control (Only this part has been parallelized)
	2. Motor reading (One of the bottle neck of the frame rate)
	3. Camera acquisition
	4. Scheduler for motor control plan
	5. Merging and saving data
3. LLM should split the functions above, and make them run in parallel.