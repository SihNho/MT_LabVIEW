No, not as written. The pool's overload rule contradicts a settled user decision, so the next cycle should settle the rule first and build afterwards.

**What NEXT prescribes.** One build step: a 20-slot image pool with the queues Q_free and Q_work, where a full Q_work means "skip this read" (`STATUS.md:65-68`, `docs/d1-loop12-17-split-plan.md:2171-2175`). Both copy the rule from `docs/d1-build-plan.md:572`.

**Why it is the wrong next act**

1. **It breaks the user's overload decision.** When tracking falls behind the camera, the settled rule is to throw away the waiting frames and take the newest one. The reason given is that a stale sample corrupts the time series and a gap does not (`docs/decisions.md:25`). That table "must not be re-opened without the user" (`docs/decisions.md:8`).
   - A 20-deep first-in-first-out queue that skips new reads when full does the opposite: it keeps up to 20 old frames and drops the newest.
   - The design doc records that the user rejected exactly this ("drop-new"), because it leaves the tracker "contiguous but lagged" (`docs/frame-ownership-design.md:89-91`).
   - Under sustained overload, every tracked frame would sit about 20 tracking periods behind the camera.
   - The later argument that "the driver's ring IS the latest-wins queue" (`docs/stage2-plan.md:50-52`) only holds if nothing queues up after the camera driver. A 20-deep Q_work is a second backlog in front of the tracker.
2. **This load is real.** At 15 beads the original copy lost 3,359 and 5,860 frames in its two runs (`STATUS.md:18`). So the overload branch will run in practice.
3. **The source documents disagree with each other, and nobody has resolved it:**
   - Pool size: 20 slots (`docs/decisions.md:22`, `docs/d1-build-plan.md:572`) versus an invariant of 8 (the same `decisions.md:22`, `docs/stage2-plan.md:67`, `docs/stage2-assembly-step-c.md:19-20`).
   - Which frame gets read: always the newest (`Buffer Number Mode = Last`, `docs/decisions.md:20`) versus the original's "last buffer number + 1" (`docs/stage2-plan.md:68-70`). The second is a rule-1a question: the original's computation must not change.
4. **The draft already flagged this.** It says the 20-slot bound and "full ⇒ skip" depend on the answer to its open question O5 (`docs/qrtw-plan-draft.md:88-89`). Judgement answered O5 only with "pool first" and copied `:572` unchanged (`docs/d1-loop12-17-split-plan.md:2142`).
5. **The build step would probably stop anyway.** Queue timeouts (O6) are still open (`:2148`), and the build instruction says any unsettled choice returns BLOCKED (`:2175`). The "full ⇒ skip" branch is exactly a timeout-and-return-the-slot choice. That spends a LabVIEW build step to rediscover the gap.

**What the next cycle should do instead**

- **Short judgement act first.** Write a Pre-decided entry for the pool that matches `docs/decisions.md:20-25`. One way that fits the rules: the tracking loop (1.2) empties Q_work, tracks only the newest slot, and returns the older ones to Q_free. That discards the backlog without the forbidden lossy enqueue or pool eviction (`docs/decisions.md:21`).
  - The same entry fixes the pool size (20 or 8), the read mode against rule 1a, and O6 for the camera-loop side. `docs/d1-build-plan.md:640` already gives timeout 0 there.
- **Ask the user if needed.** If any of this departs from `docs/decisions.md`, it goes into `decisions_pending.json` for the user.
- **Meanwhile, do the policy-independent work.** The missing creation routes for `IMAQ Create` and the queues (`docs/qrtw-plan-draft.md` T1) do not depend on the answer.
- **Then run the POOL build step** on that settled specification.

VERDICT: change NEXT
NEXT ACT: Add a Pre-decided entry that makes the pool follow the user's newest-frame-wins rule (`docs/decisions.md:25`) and settles pool size, read mode and camera-side timeouts (asking the user where it departs from `docs/decisions.md`), build the policy-independent creation routes meanwhile, then run the POOL build step on that entry.