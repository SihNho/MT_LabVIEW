# retro-window-semantics-codex

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-18 09:00:44
- **outcome:** ANSWERED (129s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK the claim below. It is a FAILED PREDICTION from cycle 20 of this project: a retrospective was
dispatched believing `--cycle N` selects cycle N's own evidence, and the window it printed covered 5 minutes
and zero build logs. The explanation formed afterwards, under pressure, is what you must try to DESTROY.
Read the files yourself in the project directory; do not take my quotes on trust.

=== THE CLAIM YOU MUST REFUTE ===

"`tools/retrospective.py --cycle N` does not select cycle N's own logs. `--cycle N` is only a LABEL: the review
window is the interval since the previous retrospective run. Evidence: a run at 03:46 on 2026-09-18 printed
`window ... 03:42:17 .. 03:46:50 (5 min); 0 build logs`. If that is right, (i) cycle 20 has no retrospective of
its own, (ii) cycle 18's is not reconstructible, and (iii) `tools/violations.py`'s count of 8 `wrong-ordering`
occurrences counts only the retrospective files that happen to EXIST - a bias that can only understate the true
count."

=== EVIDENCE (verify each against the files) ===

1. `tools/retrospective.py:256` `def cycle_window(cycle, slug=None):` - the cycle number is parsed at :279-282
   (`n = int(cycle)`), then:
     :285  `prev = newest_retro_before(now, exclude_slug=slug)`
     :286-289  `if prev: start = prev[1]` with basis text "the LAST retrospective written before this one"
     :290-296  else-branch: `cur = os.path.join(ROOT, "docs", f"cycle{n}-plan.md")` ... `start = os.getmtime(cur)`
     :308  `end, ebasis = now, "now, at window computation ..."`
   So `n` appears to be used ONLY in the no-previous-retrospective fallback path and in output labels.
2. `tools/retrospective.py:208-236` `newest_retro_before(now, exclude_slug)` globs
   `archive/peer/*retrospective*.md`, skips `retrospective-v2-*`, and takes the newest by `guard_cycle.stamp()`.
   Its own docstring (:210-215) says "EVERY retrospective closes a window, not just the previous CYCLE's ... A
   cycle number is a label Claude chooses".
3. The observed run: `tools/bench/retro_cycle18.log:1-2`
     `BGRUN START 2026-09-18 03:46:50 limit 10.0 min: py tools/retrospective.py --cycle 18`
     `   window 2026-09-18 03:42:17 .. 2026-09-18 03:46:50 (5 min); 0 build logs, 2 machinery logs, 11 devices`
   That log has NO `BGRUN END` line - the run was KILLED, so it is a NON-RESULT, not a completed review.
4. `tools/violations.py:163-192` `scan()` iterates `sorted(glob.glob(os.path.join(PEER, "*retrospective*.md")))`.

=== ALREADY RULED OUT (do not spend your answer here) ===
- "The window was short because little work happened": `0 build logs` in a cycle that built and released a recipe
  is the anomaly being explained, not the explanation.
- "`--since-hours` would have fixed it": the run did not pass it; the question is what `--cycle` alone does.
- "The archives' timestamps are unreliable (NTFS tunneling)": already reviewed separately in
  `archive/peer/2026-09-17-open31-window-codex.md`; assume `stamp()` behaves as documented there.

=== WHAT YOUR ANSWER MUST CONTAIN ===
A. Does the code select evidence BY CYCLE NUMBER anywhere, or only by TIME WINDOW? Name the DECIDING line as
   `tools/retrospective.py:<line>` and quote it. If the cycle number does influence selection anywhere I have
   missed (audit_cycle invocation, log listing, task text, slug defaulting, the `--slug` / `exclude_slug`
   interaction), say exactly where and what it changes.
B. State the window rule PRECISELY as the code implements it, including the fallback and the `exclude_slug`
   effect, and say under what conditions `--cycle N` and the window disagree about which work is reviewed.
C. Is (iii) right - does `violations.py` count only retrospective FILES present in `archive/peer/`, so a cycle
   whose retrospective was never archived contributes zero? Say whether that biases the count UP, DOWN, or
   neither, and why.
D. The strongest reason the claim is WRONG or overstated; an alternative explanation of the 5-minute / 0-log
   window; what observation would falsify the claim; and the single cheapest discriminating test.



--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The strongest defect is that “`--cycle N` is only a label” is literally false. `N` determines the default slug, and that slug determines which archived retrospective is excluded from boundary selection. Changing `N` can therefore change the evidence window. The narrower conclusion—that logs are primarily selected by time, not by a stored cycle identifier—is correct.

## A. Does `N` select evidence?

The normal deciding line is [tools/retrospective.py:287](</G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/retrospective.py:287>):

> `prev = newest_retro_before(now, exclude_slug=slug)`

Then line 289 sets `start = prev[1]`. Build logs are selected solely by mtime at lines 364–368:

> `if start <= mt <= end:`

But `N` is not merely decorative:

- At [line 328](</G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/retrospective.py:328>), it creates the default exclusion slug:

  > `cycle_window(a.cycle, a.slug or f"retrospective-cycle{a.cycle}")`

- At [line 223](</G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/retrospective.py:223>), an existing archive with that slug is omitted:

  > `if exclude_slug and b.endswith(f"-{exclude_slug}.md"): continue`

  Thus `--cycle 18` excludes an earlier default cycle-18 archive, while `--cycle 20` excludes cycle 20’s. If either is otherwise the newest retrospective, changing `N` changes the start time and hence the selected logs. An explicit `--slug` replaces this `N`-dependent exclusion.

- If no prior retrospective remains, `N` selects `docs/cycle<N>-plan.md` as the fallback boundary at lines 293–297.
- `N` is passed to `audit_cycle.py` at lines 349–351. It does not change the audit’s log window, but it selects the plan used for the C7 out-of-plan comparison at [tools/audit_cycle.py:325–327](</G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/audit_cycle.py:325>).
- It also changes the task label, referenced plan, default archive slug and scratch filename at retrospective lines 374, 409, 412–413.

So: primary build/audit-log membership is time-window based, but `N` can indirectly alter that window through `exclude_slug`, and directly changes the C7 plan comparison.

## B. The exact window rule

Without `--since-hours`:

1. Capture `now`.
2. Scan `archive/peer/*retrospective*.md`.
3. Ignore:

   - `retrospective-v2-*`;
   - files whose basename ends in `-{exclude_slug}.md`;
   - files whose `guard_cycle.stamp()` is zero or not strictly before `now`.

4. Choose the remaining file with the greatest stamp.
5. If found: `start = that stamp`.
6. Otherwise: `start = mtime(docs/cycle<N>-plan.md)`.
7. If neither exists, `cycle_window()` fails and `main()` uses 20 hours by default, or the supplied `--since-hours`.
8. `end = now` unconditionally at [tools/retrospective.py:309](</G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/retrospective.py:309>).
9. An explicit `--since-hours H` overrides a valid start with `end - H*3600`.

The label and reviewed work disagree whenever retrospective cadence differs from cycle cadence: multiple reviews occur within one cycle, a later-numbered cycle is reviewed before an older-numbered rerun, a cycle begins before its predecessor’s retrospective closes, or the default/custom slug exclusion removes the otherwise-latest boundary.

The observed run is especially weak evidence for claims (i) and (ii). [retro_cycle19.log:1–4](</G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/retro_cycle19.log:1>) shows a successful cycle-19 retrospective immediately beforehand, and line 54 has `BGRUN END rc=0 after 370s`. The 03:46 run therefore opened after a fresh closure near 03:42. It was not a historical cycle-18 retrieval operation.

Moreover, cycle 19’s own output says its window already included “66 minutes of next-cycle work” ([line 6](</G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/retro_cycle19.log:6>)). Consequently:

- “Cycle 20 has no archive named cycle 20” may be true.
- “Cycle 20’s work received no retrospective coverage” does not follow; some was reviewed under the cycle-19 label.
- “Cycle 18 is not reconstructible” also does not follow. The command cannot retrieve it automatically, but reconstructibility depends on whether its actual boundary timestamps and logs survive.

## C. The violations count

Yes. [tools/violations.py:172](</G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/violations.py:172>) scans only existing `archive/peer/*retrospective*.md` files, excluding archives marked as comparisons. A never-archived review contributes zero parser hits.

But “a bias that can only understate” is false. The bias direction is neither:

- A missing review might have emitted `wrong-ordering`, `none`, or another slug. Its absent verdict cannot automatically be treated as a hidden occurrence.
- Ordinary overlapping or relabelled retrospectives can count the same work more than once. The file itself acknowledges that three retrospectives over overlapping work inflated counts at [lines 17–19](</G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/violations.py:17>).
- `scan()` appends one hit for every matching line and does not deduplicate either by cycle or filename. Duplicate same-slug verdict lines in one archive would count multiple times.

The number 8 is accurately “eight parsed verdict lines in the eligible files,” not an unbiased count of cycles or underlying wrong-ordering events.

## D. Refutation and discriminating evidence

The strongest refutation is the `N → default slug → exclusion filter → boundary` path. That disproves the absolute “only a label” formulation.

An alternative explanation of the five-minute/zero-build output is straightforward: a completed retrospective had just closed a window near 03:42, and between that closure and 03:46 only review machinery logs existed. Retrospective logs are explicitly classified as machinery by [tools/logclass.py:45–52](</G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/logclass.py:45>). Zero build logs therefore does not demonstrate that historical cycle-18 evidence vanished; it demonstrates that the invocation opened a new forward interval after the latest eligible closure.

The claim would be falsified most directly by showing that, with the same frozen `now` and archive set, changing only `N` changes the computed `start`. That will happen when one default slug excludes the otherwise-newest retrospective. Conversely, if identical explicit nonmatching `--slug` values always yield identical windows for different existing cycle numbers, that confirms the narrower time-window model.

The cheapest discriminating test is a read-only unit probe with frozen time: call `cycle_window(18, "nonexistent-probe")` and `cycle_window(20, "nonexistent-probe")`, then repeat using each default slug. Identical results in the first pair but different results in the second isolate the slug-exclusion effect and disprove “`N` is only a label” without dispatching any peer or touching LabVIEW.

## Sources

(extract from answer)

## What was done with it

Cycle 21 step 1, the `-Dual` failed-prediction review OPEN 49 owed. Arm 1 of 2 (arm 2:
`archive/peer/2026-09-18-retro-window-semantics-opus.md`); dispatch log
`tools/bench/peer_retro_window_semantics.log`, `BGRUN END rc=0 after 621s`, `DUAL DONE: codex rc=0, opus rc=0`.

Both arms AGREE on the mechanism and both PARTLY REFUTE the claim. Agreed: evidence membership is by time window
(`tools/retrospective.py:287` `prev = newest_retro_before(now, exclude_slug=slug)`, `:289` `start = prev[1]`,
`:309` `end = now`; build logs filtered at `:364-368` `if start <= mt <= end`), and `violations.py:172` counts
only the retrospective files that exist. Refuted: "`--cycle N` is ONLY a label" — N reaches the window through
the default slug `retrospective-cycle<N>` fed to `exclude_slug` (`:328` → `:223`), selects the C7 plan in
`audit_cycle.py:325-327`, and is the fallback boundary at `:293-297`. Refuted: "a bias that can only understate"
— both arms call the direction indeterminate (missing reviews subtract, overlapping/relabelled reviews and the
saturated v1 format add; `violations.py:17-19`).

No decision taken here: this material session reported the facts to the judgement session, which owns what to do
about the windowing rule, the counting bias and OPEN 49's disposition. No code was changed by this review.
