**No, not as written.** The pool itself is needed: if 1.1 queued its single IMAQ image reference, it could overwrite the frame before 1.2 reads it (`docs/d1-loop12-17-split-plan.md:2142`, `docs/frame-ownership-design.md:25`). The problem is the overload rule NEXT tells the build to lock in (`STATUS.md:66`, `docs/d1-loop12-17-split-plan.md:2172`).

1. **It goes against a settled user decision.** For acquisition → tracking, `docs/decisions.md:25` says "lossy, latest-wins: discard the backlog, take the newest frame". The user chose that over drop-new, which "leaves the tracker contiguous but lagged" (`docs/frame-ownership-design.md:89-91`). A 20-slot first-in-first-out queue (`docs/stage2-assembly-step-c.md:39`) that skips the *new* read when full keeps up to 20 stale frames and tracks the oldest first. That keeps the backlog instead of discarding it. Settled decisions are not re-opened without the user (`docs/decisions.md:8`).

2. **The docs' own reconciliation doesn't fit this VI.** "Skipping a read = latest-wins" depends on `Buffer Number Mode = Last` (`docs/frame-ownership-design.md:92-94`, `docs/stage2-plan.md:50-52`). The current working VI instead reuses `get buff image-lost frames.vi` #6810 (`docs/d1-build-plan.md:515-517`), which asks for `LastBufferNumber + 1` on every iteration (`docs/m8-real-run-plan.md:205`, `docs/stage2-plan.md:19-20`). After a skip it asks for the next buffer in order, not the newest one, and the plan required its overwrite behaviour to be measured first (`docs/stage2-plan.md:70-71`). The saved frame index is also `#637 i` (`docs/d1-loop12-17-split-plan.md:2137`), which would also count skipped iterations. Under overload, the saved numbers could differ from the original's. The rule for that case is to stop and ask the user (`CLAUDE.md:37`).

3. **The trigger as written can never fire.** The pool has 20 slots and `Q_work` holds 20, so `Q_work` cannot be full while 1.1 holds a slot (the same count rule as `docs/stage2-assembly-step-c.md:33-35`). Overload actually shows up as an empty `Q_free`, and §9 doesn't say what happens then (`docs/d1-build-plan.md:572`).

**What the next cycle should do instead:** put the overload behaviour on the user's decision list:
- **Option (a):** latest-wins on the tracking side. 1.2 empties `Q_work`, tracks the newest slot and returns the older slots to `Q_free`. Nothing is evicted and nothing uses a lossy enqueue, so `docs/decisions.md:21` still holds.
- **Option (b):** keep drop-new as a jitter buffer and formally re-open `docs/decisions.md:25`.

The same question should also settle which buffer #6810 asks for after a skip.

Meanwhile, following `CLAUDE.md:169`, one material session builds and checks on a scratch VI the parts every option needs: the missing Obtain/Enqueue/Dequeue/Release queue routes and the IMAQ Create route (`docs/qrtw-plan-draft.md:26-29`). The POOL build runs only after the user answers.

VERDICT: change NEXT
NEXT ACT: Add the pool's overload behaviour (20-slot queue plus "skip this read", against the settled latest-wins rule and #6810's in-order buffer requests) to the user's decision list, and meanwhile have one material session build and scratch-test the queue and IMAQ Create routes, running the POOL build only after the answer.