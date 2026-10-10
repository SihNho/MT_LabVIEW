---
name: establish-cheap-automation-standard-before-grinding
description: Settle on a cost-effective automation standard (and manage context/sub-sessions proactively) instead of grinding through slow screenshot-and-click GUI work
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 72babae7-a0eb-4591-80eb-3f88511dbec4
  modified: 2026-08-25T17:00:16.977Z
type: decision
status: in-force
date: 2026-08-25
source: memory/establish_cheap_automation_standard_before_grinding.md
---

# Pick the automation standard first; don't grind on screenshot-and-click

The user's standing expectation on this LabVIEW project (stated 2026-08-26, after watching a long
run of screenshot → crop → click → screenshot round-trips): **screenshot-driven GUI control is too
slow and too costly for small actions, and Claude should establish a good standard method before
proceeding rather than brute-forcing its way through.** "There are so many ways to go, and you
should find a good standard before proceeding."

Concretely, when a task can be done more than one way, evaluate the options and commit to the
cheapest reliable one *before* spending many turns. On this project the ranking that follows from
that principle is: drive LabVIEW programmatically (VI Scripting, driven in turn from outside via VI
Server / LabVIEW CLI with a **parameterised** driver VI so no re-clicking is needed per change)
first; hand-editing a driver in the GUI second; screenshot-and-click only as a genuine last resort.
A single mis-aimed click costs several round-trips, because each one needs a capture, a crop, and a
visual read — so anything requiring pixel precision on a 4-pixel target is a signal to change method,
not to try again.

The user also expects Claude to **manage its own context budget and sub-sessions**: long unbroken
runs fill the context and slow things down further, so proactively delegate separable work, keep the
project's hand-off docs current, and start fresh sessions rather than letting one session sprawl.
The user noted this is why the project's `.md` rules (`CLAUDE.md`, `STATUS.md`) were written the way
they were — cheap cold starts are the point, so use them.

A related open item the user cares about: **different models have not been benchmarked for GUI
control quality.** Do not claim they have been.
