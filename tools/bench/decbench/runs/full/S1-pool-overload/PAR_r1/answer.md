**Change NEXT.** A pool stage should still be the next build: one shared IMAQ refnum would let loop 1.1 overwrite the image before 1.2 reads it (`docs/d1-loop12-17-split-plan.md:2142`). But the overload rule the card is told to build is keyed on the wrong queue, and the correct rule needs a timeout choice that the card must hand back as BLOCKED.

**What survives checking**

1. **"Full Q_work ⇒ skip" can never fire.**
   - §9 gives Q_work the same bound as the pool, 20 (`docs/d1-build-plan.md:572`).
   - With free/work queues, "there is no way to have more frames in flight than slots" (`docs/frame-ownership-design.md:74-76`).
   - The proven core showed the same thing: the producer never finds the work queue full (`docs/stage2-assembly-step-c.md:33-35`).
   - The settled trigger is the other queue: "no free slot — simply do not read this iteration" (`docs/decisions.md:24`), and acquisition "does not wait" (`docs/frame-ownership-design.md:65`).
   - A literal §9 build gives a dead skip branch. It also leaves a Q_free dequeue that can block 1.1, which breaks "reader, never a gate" (`docs/decisions.md:21`).
2. **The fix touches O6, which is still open.** Timeouts and error chains are listed as OPEN (`d1-loop12-17-split-plan.md:2147-2148`), and the card must return BLOCKED on them (`:2175`). The replay core had no timeouts at all; a timeout-gated Case was deferred to live mode (`stage2-assembly-step-c.md:36,44-45`). So as briefed, the card either stops BLOCKED or re-writes §9 itself, which is a judgement call made inside a material session.
3. **Two slot counts are on record.** `decisions.md:22` says "start at 20 slots" and also "free + queued + processing = 8". The card's slot-count gate needs one number. §9 and PD233 both say 20.

**What does not survive**

- **Draining Q_work to the newest frame to get "latest-wins at the tracker" (Analyst 3; Analyst 2's item 3).** The files already settled this:
  - Eviction was cancelled.
  - A full pool means "skip this read — the driver's ring IS the latest-wins queue" (`docs/stage2-plan.md:50-52`; `docs/frame-ownership-design.md:89-94`).
  - "No pool eviction" is a settled decision that is not to be reopened without the user (`docs/decisions.md:8,21`).
  - The design point is a consumer faster than the camera, so the queue absorbs jitter, not a sustained deficit (`frame-ownership-design.md:87-88`).
  
  The next cycle should not reopen this. If anyone wants to, it goes to the user as a question.
- **The missing element-type source (Analyst 1).** It is real (`d1-build-plan.md:599-600`), but it does not block the card: the card is explicitly allowed to build the IMAQ Create/queue creation route itself (`d1-loop12-17-split-plan.md:2174`). The donor constraint PD35(a) (`d1-build-plan.md:608-615`) is a design rule the card follows, not a reason to change NEXT.

**What the next cycle should do instead**

A short offline judgement step, with no LabVIEW, that writes a Pre-decided entry covering:

- **Skip trigger:** "Q_free dequeue with timeout 0 timed out ⇒ do not call Get Image this iteration". Gaps are counted from the jump in buffer number (`decisions.md:24`).
- **Q_work enqueue:** a finite timeout. On `timed out`, the slot goes back to Q_free (`stage2-plan.md:66`).
- **Error chaining:** only as much of O6 as the pool needs.
- **Slot count:** 20, as the one invariant; `decisions.md:22` is annotated to match.
- **§9 fix:** row `d1-build-plan.md:572` is patched to say the above.

The same cycle then dispatches the POOL material card unchanged in every other respect: ≤15 rows, ONE launch, saved `D1_qrt_pool_<ts>.vi`. None of this touches the saved R2 working VI (`STATUS.md:64-66`).

VERDICT: change NEXT
NEXT ACT: The judgement session first writes a Pre-decided entry that moves the pool's skip trigger to "Q_free dequeue timeout 0 timed out ⇒ skip the read", fixes the Q_work enqueue timeout, the slot-return path and the 20-slot invariant, and patches `d1-build-plan.md:572` to match; then it dispatches the POOL build card on that spec in the same cycle.