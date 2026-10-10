---
name: project-v6-parallelization
description: "Ground rules, Loop1/Loop2 architecture, and the two active parallelization threads (main-VI loop hunt + tracking-kernel rebuild) — see STATUS.md in the project for the live hand-off doc"
metadata: 
  node_type: memory
  type: project
  originSessionId: 52d900cc-eddf-491c-ac00-c5055911beed
  modified: 2026-08-25T04:09:46.535Z
type: decision
status: in-force
date: 2026-08-25
source: memory/project_v6_parallelization.md
---

V6 build work is governed by `Requests.md`'s ground rules and two task-spec documents in
`Project Requirements/`: `Parallelization requirement.md` (2026-08-24) and the more detailed
`Description of the project.md` (2026-08-25). All are ingested into the wiki — see `OVERVIEW.md`'s
"Experimental workflow" and "V6 goal" sections, and `VERSION_HISTORY.md`'s "V6 planning" /
"V6 investigation" entries.

**Ground rules (Requests.md):**
- Reference `Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi` read-only — never modify it directly.
- New sub-VIs go under `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev`, not in `V6_ParallelLoop/`.
- Keep a change history in `VERSION_HISTORY.md` so work is resumable across chats/sessions/LLMs.

**Baseline question — resolved:** user chose **4.5** as the reference file. A working copy exists at
`2. Tracking/Min_Track N beads V6_ParallelLoop.vi` (sibling of 4.5, same folder depth — placing it
inside `V6_ParallelLoop/` itself breaks relative-path sub-VI dependencies, confirmed the hard way).

**LabVIEW is actually installed** on this machine (`LabVIEW 2026`, plus LabVIEW CLI) — the wiki
originally assumed otherwise; that's now corrected in `ANALYSIS_METHOD.md`. It can be driven live via
screenshot + simulated mouse/keyboard (PrintWindow for window capture; Alt-key trick to force real
foreground/keyboard focus; LabVIEW context menus open on right-mouse-**down**, select by dragging to
the item and releasing there). Headless VI Scripting via LabVIEWCLI was tried and abandoned — NI's
shipped scripting examples only build brand-new blank VIs from scratch or are non-runnable teaching
diagrams; there's no way to script edits into an *existing* VI without first hand-building a custom
scripting VI in the GUI, which is the same chicken-and-egg problem.

**Current understanding of the loop structure to parallelize** (per `Description of the project.md`,
which refines the original requirement doc): the real experiment phase (workflow step 4) runs as
exactly two While Loops today —
- **Loop 1** — motor *writing* control only (already isolated, leave alone).
- **Loop 2** — everything else: motor *reading*, camera acquisition, image processing, scheduling,
  data saving, and printing to the screen.

Target architecture: **7 parallel loops total** — Loop 1 unchanged, plus 6 new loops splitting Loop 2:
Motor Reading, Camera Acquisition, Image Processing, Scheduler, Merge & Save, Screen/Display Update.

**Acquisition vs. processing split (user request, 2026-08-25):** camera acquisition and image
processing are two separate loops, not one, because the camera setup already does buffered/ring-buffer
acquisition via IMAQdx — evidenced by the existing `get buff image-lost frames.vi` sub-VI and
front-panel diagnostics `Buffer Number Mode`/`Total Lost Frames`/`Missing Frames?`. Plan: Acquisition
loop only grabs/waits for the next buffer and passes its **buffer index** (not image pixels) through a
queue; Processing loop dequeues the index, fetches that buffer's image, and runs the bandpass +
tracking kernel. Keeps the acquisition loop maximally lightweight (never the cause of lost frames) and
avoids copying full images through a queue every frame.

Introduce proper Queues for all inter-loop data — the codebase currently has **zero** Queue/Notifier/
Semaphore/Rendezvous usage anywhere; cross-loop state today goes through VI Globals like
`Global motor pos.vi`, a real race-condition risk once more parallel loops are added.

**Not yet found: the actual Loop 1/Loop 2 in the diagram.** A GUI investigation session scrolled
through the VI's entire top-level Sequence Structure (~8-9 frames) and found a `Done Picking Beads?` →
While-Loop-stop wiring, plus a `MainCycle`/`SubCycle`/`MOV.vi`/`VEL.vi` frame — but per
`Description of the project.md`, that whole Sequence Structure most likely covers workflow steps 1-3
(manual setup, bead selection, one-time per-bead radial-profile *calibration* → `.cal` file), not step
4's continuous experiment loops. **Before doing any diagram surgery, resume the search for Loop
1/Loop 2 specifically — likely located after or outside that Sequence Structure, not as one of its
frames.**

**Why this matters:** the user is directing V6 development iteratively through dropped-in requirement
docs across sessions, explicitly wants a maintained change history for continuity across different
LLMs/chats, and this is real instrument-control software (magnetic tweezers, real motors/camera) — so
confirm structural assumptions against their own descriptions rather than acting on inferred guesses,
and never actually execute/Run the real VI during scripting work (only static diagram edits; hardware
only matters once a human runs the finished result). See [[labview_vi_analysis_skill]].

**Second parallelization thread — the tracking kernel itself (2026-08-25):** separately from the
Loop1/Loop2 hunt above, the user asked to rebuild `Track N beads four-fold over-kernel-v3.vi` (the
per-bead tracking math called from within the experiment loop) to process beads in parallel. Full
current plan lives in `STATUS.md` (the "read this first" hand-off doc, now added to the wiki
specifically for cross-session continuity) and the "Kernel investigation" entry in
`VERSION_HISTORY.md`. Short version: that kernel's outer For Loop already has unwired `N`/`P`
parallel-loop terminals (parallel infrastructure present but unused); of its two reentrant sub-kernels,
`Track 1 of N bds xyz-kernel-reentrant.vi` is confirmed genuinely single-bead/independent while
`Track 2 of N bds xyz-kernel-reentrant-v2.vi` bundles two beads per call (confirmed both via
connector-pane strings and the user's own visual inspection of its diagram). **Decision: build the new
parallel kernel around Track 1 only**, one call per bead per parallel-loop iteration — not around the
existing four-fold/Track-2 pairing. Not yet built; see `STATUS.md` for exact next steps.

**Workflow note:** don't force-close and relaunch LabVIEW between inspecting different VIs — reuse the
open instance. See [[feedback_labview_session_reuse]] (corrected by the user 2026-08-25).
