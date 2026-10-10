---
name: scratch-instances-are-free-to-kill
description: Experimental/scratch LabVIEW instances and VIs may be closed and deleted freely without asking
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 1ffa4eb9-19ac-4240-b7d7-6ef33fffb8c1
  modified: 2026-08-28T13:31:05.603Z
type: decision
status: in-force
date: 2026-08-28
source: memory/scratch_instances_are_free_to_kill.md
---

# Scratch instances and VIs may be killed freely — no need to ask

On 2026-08-28, after Claude reported that several editor windows for already-deleted scratch VIs
were cluttering LabVIEW and asked whether to restart the shared instance, the user answered:
*"실험용 인스턴스는 얼마든지 자유롭게 끄고 지우고 하고"* — experimental instances may be closed and
deleted freely.

So housekeeping of throwaway artefacts is Claude's own call: closing scratch VI windows, deleting
scratch build targets, and restarting a LabVIEW instance that holds only scratch state need no
permission. Everything that matters is on disk anyway, because the fleet's rule is to save after
every verified edit.

This does **not** loosen the two rules it sits next to. Original `.vi` files are still never
modified or saved, and the instance must still not be reclaimed while the user is running a real
experiment — the standing protocol is that work starts and stops on the user's explicit word, and
that has not changed. What changed is only that *cleanup of Claude's own leftovers* no longer needs
a confirmation round-trip.
