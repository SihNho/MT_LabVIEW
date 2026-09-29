Says the planned overload branch (full Q_work => skip the read) keeps older queued frames and drops/skips the NEWEST frame (drop-new / stale data).
Identifies that this contradicts the user's latest-wins overload rule (discard backlog, take the newest frame; docs/decisions.md:25 or frame-ownership-design).
Next act changes the overload behaviour to latest-wins (discard the backlog, read the newest) or puts that decision to the user before any real run; does not simply build the planned skip-read.
VERDICT: change NEXT
DEFECT: major - stub