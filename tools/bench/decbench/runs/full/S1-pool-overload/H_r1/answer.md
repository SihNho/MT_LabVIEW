**No, change NEXT.** A pool is still needed, but the overload rule NEXT would build into it goes against a decision already recorded in the project.

**What NEXT tells the card to build**
- NEXT asks one material card to build the pool "Q_free / Q_work lock-stepped, bound 20, full ⇒ skip the read" (`STATUS.md:65-66`), copying `d1-build-plan.md:572` exactly. PD233(k) says the same (`docs/d1-loop12-17-split-plan.md:2171-2172`).
- PD233(g) O5 only decided that the pool comes before QRT-W (`:2142`). It carried "bound 20, full ⇒ skip" along without checking it. The QRT-W draft had already said that these two values "depend on the answer" (`docs/qrtw-plan-draft.md:88-89`).
- The card may only return BLOCKED for choices "the files do not settle" (`STATUS.md:68`). The files do settle this one, but they contradict each other, so the card would just build the §9 row.

**What was decided about overload**
- Camera → tracking overload is "**lossy, latest-wins** — discard the backlog, take the newest frame. A stale sample corrupts the time series; an explicit gap does not" (`docs/decisions.md:25`).
- `frame-ownership-design.md:89-91` rejects drop-new by name: "drop-new leaves the tracker *contiguous but lagged*, which is the one thing a time series must not be."
- Ring depth is meant to "absorb jitter only" (`decisions.md:22`). That line gives a pool invariant of **8**, while §9 gives a bound of **20**. The two numbers were never reconciled.

**Why this matters now**
- A 20-deep Q_work where a full queue skips the new read *is* drop-new. Once tracking falls behind, Q_work stays full and 1.2 keeps tracking frames about 20 behind (about 220 ms at 90 Hz). Every new frame is the one that gets thrown away.
- The original VI reads `Buffer Number Mode = Last` and tracks each frame straight away (`decisions.md:20`), so it never tracks an old frame. Adding lag it never had is a behaviour change that should be checked against rule 1a, not simply built.
- This is not a hypothetical overload. The ABBA at 15 beads lost 3,359 frames on the original copy (`STATUS.md:18`). The rule is written for exactly that condition.
- The autofocus loop runs on 1.2's reference-bead z (CLAUDE.md 1c''). A 20-frame backlog puts that delay into the focus feedback.
- Putting this right after the build would mean redoing a saved step. PD233(g) had already left O6 and O7 open for this same stage (`:2148-2149`). The overload row belongs with them.

**What the next cycle should do**
A short judgement step, before any build card, that:
1. Rewrites the §9 Q_work row so it satisfies latest-wins without breaking `decisions.md:21` (no eviction by the producer, no Lossy Enqueue, the camera never throttled). Two candidates:
   - a small Q_work bound (1–2);
   - or 1.2 dequeues everything waiting, tracks only the newest frame, returns the skipped slots to Q_free, and records each gap as a jump in the buffer number (`decisions.md:23-24`).
2. Settles the slot count (8 or 20).
3. Decides O6 (timeouts) and O7 (release order and stop) in the same pass.
4. If it cannot be shown that dropping backlog frames the original never had is computation-preserving, puts that question to the user in `decisions_pending.json` (CLAUDE.md 1a: "stop and ask").

Then the unchanged POOL card builds the corrected row.

VERDICT: change NEXT
NEXT ACT: Before the POOL build card runs, a judgement step replaces §9's "bound 20, full Q_work ⇒ skip this read" with a latest-wins rule that matches decisions.md:25 and frame-ownership-design.md:89-94, settles the pool depth and O6/O7, and sends any rule-1a doubt to the user.