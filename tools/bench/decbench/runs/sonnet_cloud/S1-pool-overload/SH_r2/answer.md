The POOL step is the right next act, but NEXT needs two amendments before the card starts.

**Why keep it**
- R2 is accepted as the bed, so the pool is the next unbuilt step: `STATUS.md:62-65`, PD233(i) at `docs/d1-loop12-17-split-plan.md:2160-2164`.
- The ordering follows rule 1a. R1 has a single IMAQ refnum. If it were queued, 1.1 could overwrite the buffer before 1.2 reads it, so 1.2 could track a different frame (PD233(g) O5, `split-plan:2142`).
- The design already exists. Q_free/Q_work hold IMAQ refnums with bound 20, and full Q_work means skip this read (`d1-build-plan.md:572`). The slot-pool pattern was proven offline in step C (`stage2-assembly-step-c.md:19-29`).
- The skip policy matches `decisions.md:24`, "no free slot: simply do not read this iteration", and `decisions.md:21`, "the PC is a reader, never a gate".
- A frame queue is lossless per-frame data, so CLAUDE.md 1c'' (control signals go by local variable) does not apply.
- The card's shape is sound: ≤ 15 rows, a recipe ≤ 120 lines, dry run, prerun, scratch run, then one launch (`STATUS.md:67`).
- Building a missing create route inside the card is allowed by the 2026-09-24 tools rule (`split-plan:2174`).

**Two amendments**

1. **Settle the overload policy before the card.** `decisions.md:25` says overload from acquisition to tracking is "lossy, latest-wins — discard the backlog". The pool design instead skips new reads and processes up to 20 stale frames in order.
   - The two don't conflict only if the pool's skip rule counts as the "no free slot" row (`decisions.md:24`) and the latest-wins row is read as a statement about the camera mode (`Buffer Number Mode = Last`).
   - The card should write that reading down as a one-line Pre-decided entry, not choose it silently.
   - Define "full Q_work" as Q_free empty. Q_free is the pool authority, so one dequeue on Q_free with timeout 0 gives the skip, and no separate full-test is needed. This keeps rule 1c's timeout-0 requirement on the frame path (`d1-build-plan.md:639-640`).
   - NEXT says to return O6 (timeouts) as BLOCKED to judgement. The pool needs exactly these timeouts, and §9 already settles them for the frame path. Only the error chains and the release order (O7, the STOP stage) should be BLOCKED.

2. **Plan for the donor and the missing route.**
   - PD35(a) (`cycle27-plan.md:994`) and `d1-build-plan.md:608-615` forbid using a `#637` outer terminal as the queue's element-type donor, because that is a guaranteed deadlock.
   - The donor therefore has to be the `IMAQ Create` output, placed before the loops.
   - `stagexec` has no create route for the queue ops (`qrtw-plan-draft.md:25-29`), and `const_on_term` is missing on Diagram `#686` (`:33`).
   - A quick check shows `queue_node('obtain')` exists (`gscript.py:1262`). Put its donor wiring and the 1055 limit first in the card.

**Level of verification.** The pool-only file will be structural only. It is ExecState 0 by design and never run, because 1.2 does not consume Q_work until QRT-W. The card must say so. It must not claim that skipping a read is correct.

VERDICT: keep NEXT
NEXT ACT: Run the POOL card as written, with a one-line Pre-decided entry for the pool's skip-read policy, the pre-loop IMAQ Create donor and the queue-op creation route handled first, and only the error chains and the release order sent back to judgement.