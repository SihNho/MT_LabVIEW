**No, NEXT should change.** The pool card would have to settle questions the files leave open, and NEXT tells the card not to settle them.

1. **The overload policy contradicts the decision it should follow.** NEXT copies "full `Q_work` ⇒ skip this read" from `docs/d1-build-plan.md:572`. But `docs/decisions.md:24` says the acquisition → tracking overload policy is **"lossy, latest-wins — discard the backlog, take the newest frame. A stale sample corrupts the time series."** With skip-when-full, tracking loop 1.2 keeps working through a backlog of up to 20 old frames while new frames are dropped. That is the stale case `decisions.md:24` rules out. `decisions.md:21` also bans pool eviction, so the decision table needs reconciling first. A skip branch is also a designed frame-loss mechanism, which runs against the user's "not a single frame loss" constraint (CLAUDE.md 1c).

2. **Rule 1a is not settled.** The 233(g) pool rationale (`docs/d1-loop12-17-split-plan.md:2142`) only covers buffer overwrite. The draft that raised O5 also said "1.2 could track a later frame … Bound 20 and 'full ⇒ skip this read' depend on the answer" (`docs/qrtw-plan-draft.md:88-89`). The cross-loop feedback doubt (reseed `#5540→#5058`, O2, `split-plan:2186-2190`) also gets worse with a 20-deep lag. CLAUDE.md 1a says that when a step cannot be shown to preserve computation, the cycle stops and asks the user.

3. **The cited design does not cover a live pool.** `docs/stage2-assembly-step-c.md` is a REPLAY design with "no stop logic, no timeouts" (`:17`). It says live mode is where "an end-of-stream token and a timeout-gated Case are unavoidable; none of that is built here" (`:43-44`). A live skip branch needs O6 (timeouts, `timed out?` handling) and O7 (releasing 20 images and the queues). NEXT tells the card to return BLOCKED on exactly those two (`STATUS.md:68`; `split-plan:2175`). So the card is predictably going to block.

4. **The tools are not there.** The tool inventory lists Obtain, Enqueue, Dequeue and Release as missing in stagexec, the cluster element-type donor as missing, and constants on `#686` as missing (`docs/qrtw-plan-draft.md:26-29,35`). `d1-build-plan.md:614` adds: "until that lands, no queue stage is written." That measurement was only answered "as far as" the fleet could take it (`docs/cycle27-plan.md:1033-1035`).

**What the next cycle should do instead.** Run a short judgement act that writes one Pre-decided item for the live pool:
- **Overload policy:** skip-when-full or latest-wins/drain, reconciled with `decisions.md:20-24`.
- **O6:** timeout 0 on every frame-path operation (`d1-build-plan.md:639-640`), plus the error chains.
- **O7:** release order and the stop sentinel.

It should also measure offline whether 1.2's per-frame time at 15 beads is ever slower than the camera's 90 Hz, using existing data such as `tools/bench/disp_110_abba.json`. If neither policy can be shown to preserve computation, the question goes to the user through `decisions_pending.json`.

Following rule 2c, work that does not depend on that answer goes beside it as an offline prep card: building the stagexec queue create routes and the IMAQ Create route. The pool build follows once the item exists.

VERDICT: change NEXT
NEXT ACT: Run a judgement act that reconciles the pool's "full Q_work ⇒ skip this read" rule with decisions.md:24 (latest-wins) and rule 1a, decides O6/O7 for the live pool, and sends it to the user if it cannot be shown to preserve computation, while an offline card builds the missing queue and IMAQ Create routes.