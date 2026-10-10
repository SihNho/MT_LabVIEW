---
name: user-owns-the-original-vi-state
description: "The user manages the original VI's own state, paths and baselines - do not track, re-baseline, or raise it"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 1ffa4eb9-19ac-4240-b7d7-6ef33fffb8c1
  modified: 2026-08-28T13:12:40.904Z
type: decision
status: in-force
date: 2026-08-28
source: memory/user_owns_the_original_vi_state.md
---

# The original VI's state is the user's to manage, not Claude's

The project's standing rule has always been that original `.vi` files are never modified. On
2026-08-28 the user extended that into a division of responsibility, after Claude repeatedly
surfaced that the reference VI's on-disk hash had changed (it was the user's own Save All) and
asked whether to re-baseline it: *"원본은 내가 알아서 셋팅할테니 패스나 다른것 건들지 말고"* — I
will set up the original myself, so do not touch its path or anything else about it.

So the behaviour is: **do not track the original's checksum, do not propose a new baseline, do not
ask what to do about a changed timestamp, and do not touch its path or surrounding files.** A
detected change in an original is not a finding to report and not a decision to escalate; it is
simply the user working on their own file. This removes a recurring item that had been sitting in
the project's status document awaiting a decision that was never Claude's to ask for.

The prohibition on *modifying* originals is unchanged and absolute — this is narrower and about
custody: Claude does not manage the original's state at all, in either direction.
