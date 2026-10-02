I checked NEXT against the plan, the decisions file and the project rules. My answer is no: the POOL card as written should not be launched next.

**What NEXT prescribes.** One material card builds the POOL stage on the R2 bed: `Q_free`/`Q_work` locked to step with each other, bound 20, and "full ⇒ skip the read". Any design choice the files do not settle (O6 timeouts, O7 release/stop) goes back to judgement as BLOCKED (STATUS.md:65-68; docs/d1-loop12-17-split-plan.md:2171-2175).

**Why it is the wrong next act.**

1. **The overload policy contradicts the decisions it claims to come from.**
   - §9 says "full `Q_work` ⇒ skip this read" (docs/d1-build-plan.md:572).
   - The decisions file says the camera-to-tracking overload is "**lossy, latest-wins** — discard the backlog, take the newest frame. A stale sample corrupts the time series" (docs/decisions.md:25).
   - The original reads the newest buffer (`Buffer Number Mode = Last`, decisions.md:20) and tracks it in the same iteration.
   - A 20-deep FIFO that skips when full does the opposite: under load, tracking works through frames up to 20 old and the newest frames are dropped.
   - The sources also disagree on size and type. decisions.md:22 gives 20 slots but an invariant of "= 8". The proven core used an 8-slot integer index queue (docs/stage2-assembly-step-c.md:19-23). §9 calls for a queue of image refnums instead (d1-build-plan.md:572).

2. **This is a question about computation, not only scheduling (rule 1a).**
   - Which frames receive X/Y/Z under overload, and how many frames of lag the per-frame feedback paths get, changes the output. The cross-loop lag doubt is already recorded for the reseed feedback (`#5540→#5058`) at split-plan:2186-2190; the 25-frame focus feedback (d1-build-plan.md:575-576) is another such path.
   - CLAUDE.md 1a says that when a step cannot be shown computation-preserving, stop and ask the user. 233(g) O5 decided "pool first" (split-plan:2142) but never examined the overload policy that came with it.

3. **The card is predictably BLOCKED.**
   - "Full ⇒ skip" can only be built as an enqueue/dequeue with timeout 0 plus a `timed out?` branch. That is O6, which the card itself must return to judgement (split-plan:2175; docs/qrtw-plan-draft.md:96).
   - On top of that, the stage executor has no create route for Obtain, Enqueue, Dequeue or Release (qrtw-plan-draft.md T1). The queue type source must be a real node, and none exists yet for an image pool (docs/cycle27-plan.md:1033-1046; d1-build-plan.md:599-600, state **B**).
   - A LabVIEW card that will stop at its own O6 gate wastes a launch.

**What the next cycle should do instead**

- **Judgement act first.** Reconcile d1-build-plan.md:572 with decisions.md:21-25, then decide in one written item:
  - the overload policy: latest-wins versus FIFO with skip;
  - the slot count and the slot type (integer index or refnum);
  - O6, the timeouts and `timed out?` handling that follow from that policy;
  - a rule-1a statement of which frames get tracked under overload, compared with the original.
  
  Whether X/Y/Z can be dropped or tracked late is the user's data-quality call. Put it in `decisions_pending.json` instead of deciding it inside a card.
- **Beside it, an offline prep card** (no LabVIEW) for the parts that do not depend on the answer: the Obtain/Enqueue/Dequeue/Release create routes in the stage executor, plus a type-donor node for the pool, built against R2.
- **Then the POOL build**, with a gate that checks the chosen overload behaviour, written down before the build.

VERDICT: change NEXT
NEXT ACT: Run a judgement card that reconciles the pool's "full Q_work ⇒ skip this read" with decisions.md:25's latest-wins rule, fixes slot count/type and O6 timeouts with a rule-1a statement (and puts the frame-drop choice to the user), while an offline card builds the missing queue create routes; build POOL only after that.