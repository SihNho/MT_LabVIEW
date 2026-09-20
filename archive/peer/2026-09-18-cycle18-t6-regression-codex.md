# cycle18-t6-regression-codex

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-18 00:29:08
- **outcome:** ANSWERED (214s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this explanation of a FAILED PREDICTION. Do not confirm it.

=== WHAT WAS PREDICTED AND WHAT HAPPENED ===

Cycle 18 built a prior-art LAUNCH GATE (tools/stop_record.py) and, as part of it, made ONE change inside
tools/hooks/guard_cycle.py: the inline `re.findall(r"^REFUTED:\s*([a-z-]+)", body, re.M)` that used to sit in
`main()`'s verdict gate was lifted into a new module-level function

    REFUTED_RE = re.compile(r"^REFUTED:\s*([a-z-]+)", re.M)
    def released_slugs(path, body):
        fixed, bad = fixed_slugs(path, body)
        return set(REFUTED_RE.findall(body)) | fixed, bad

and `main()` now calls it. `guard_cycle.py` also gained a module-level `import stop_record` and a one-line call
to `stop_record.check_command(cmd)`. `premature_build`, `fixed_citations`, `fixed_slugs`, `review_time` and
`stamp` were NOT edited.

The cycle-18 runner (tools/bench/cycle18_stopgate_driver.py, log tools/bench/cycle18_stopgate.log) then ran the
two EXISTING self-tests as regression cover, PREDICTING both would report 0 fail. Result, log line 40:

    -> FAIL  regression selftest_guard_cycle_fixed.py   premature_build (b): 5 pass / 1 fail
    PASS     regression selftest_guard_cycle_rerun.py   selftest_guard_cycle_rerun: 4 pass, 0 fail

The driver did not echo the per-case lines, so WHICH of T1..T6 failed is not in the log. The gate
tools/hooks/guard_peer.py now refuses to re-run it until this review is archived, so the claim below was reached
BY READING THE CODE, not by measuring - which is exactly why it needs attacking.

=== THE CLAIM TO ATTACK ===

"The failing case is T6 of tools/bench/selftest_guard_cycle_fixed.py, it is unreachable BY CONSTRUCTION, it has
been failing since T4-T6 were added, and it is therefore NOT a regression caused by cycle 18's refactor."

The reasoning: T6 calls `run("T6", False, fixed_line=FIXED_OK, recipe_mtime_offset=-600)` - the recipe is made
600 s OLDER than the review's frontmatter instant. In `guard_cycle.premature_build`:

    revs  = [(p, stamp(p)) for p in glob.glob(os.path.join(PEER, "*priorart*.md"))]
    newer = [p for p, t in revs if t > rmt]
    if not newer:
        ...  exemptions, then the refusal ...
    return None

With the recipe OLDER than the review, `newer` is non-empty, so the whole `if not newer:` block - including the
`FIXED:` validation the test is trying to exercise - is skipped and the function returns None = ALLOWED, while
T6 expects REFUSED. If that reading is right, the test's own premise is wrong: condition (b) means "this recipe
has no prior-art review newer than itself", and a recipe older than its review is precisely the case (b) is
supposed to allow.

=== WHAT WOULD MAKE THE CLAIM WRONG - LOOK FOR THESE ===

1. A different case fails. Walk T1..T5 yourself against the current guard_cycle.py and say which one you think
   fails and why. In particular T1 (must be ALLOWED) depends on `stamp()` returning exactly the frontmatter
   instant 2026-09-17 10:00 for a file whose mtime was `os.utime`d to the same instant, and on
   `fixed_citations` accepting a recipe whose mtime is rt+600.
2. The refactor DID change behaviour. `main()` previously computed
   `open_slugs = [s for s in slugs if s not in refuted and s not in fixed]` and now computes
   `[s for s in slugs if s not in released]` where `released = refuted | fixed`. Are those sets identical for
   every input, including the case where `fixed_slugs` returns a slug that is not in `PRIOR_ART_SLUGS`, or where
   a `REFUTED:` line appears inside the QUESTION half of an archive rather than the ANSWER half? Name a concrete
   body of text on which the two expressions differ.
3. The new module-level `import stop_record` inside guard_cycle.py changes something the self-test depends on.
   `stop_record` imports guard_cycle LAZILY (inside `_released`) to avoid a cycle. Is there an import order -
   e.g. the self-test's `sys.path.insert(0, tools/hooks)` then `import guard_cycle` - under which the lazy
   import binds a half-initialised module, or under which `stop_record`'s module-level `ROOT` computation has a
   side effect on `guard_cycle.ROOT`? The self-test monkeypatches `guard_cycle.ROOT/BENCH/PEER` to a temp tree.
4. Time-dependence. `premature_build` starts by scanning `BENCH/priorart_*.log` for a review with no
   `BGRUN END`/`BGRUN TIMEOUT` line, with `floor = max(retro_stamp, time.time() - MAX_AGE_S)`. The self-test
   points BENCH at an empty temp dir - but is there any other clock-dependent path (MAX_AGE_S, stamp()'s
   midnight fallback, DST around 2026-09-17 10:00 local) that could make this test pass on 2026-09-17 and fail
   on 2026-09-18?
5. The historical record. `archive/2026-09-17-status-d1-phase-full-narrative.md:254` says this self-test scores
   **6/6**. If T6 is unreachable by construction, that line must be either stale (written when the file had only
   T1-T3) or wrong. Check the file and say which - a claim that contradicts the project's own record needs that
   contradiction resolved, not waved away.

=== ALREADY RULED OUT ===
  * Not a LabVIEW/COM failure: nothing in this run touches LabVIEW, a motor or a .vi.
  * Not the new gate itself: tools/bench/stop_record_selftest.py reported 18 pass / 0 fail in the same log,
    including its four required cases (refuse with no release, pass on a valid FIXED:, refuse again after the
    recipe's bytes change, and fail-closed on a corrupt/deleted store).
  * Not the second self-test: selftest_guard_cycle_rerun.py scored 4 pass / 0 fail in the same run.

=== WHAT I NEED BACK ===
The strongest reason the claim is wrong; an alternative explanation for `5 pass / 1 fail`; what would falsify
each; and the CHEAPEST discriminating test that does not require re-running the blocked self-test. If you can
determine which case fails purely by reading tools/bench/selftest_guard_cycle_fixed.py and
tools/hooks/guard_cycle.py, say which, and quote the lines that decide it.



--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The claim’s weakest—and presently unjustified—part is “it has been failing since T4–T6 were added.” The contemporaneous record is not stale from a three-case version: it explicitly names T4, T5, and T6 and records T6 as refused in a 6/6 run ([narrative](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/archive/2026-09-17-status-d1-phase-full-narrative.md:254>)). The self-test itself has a September 17 09:29 timestamp, while that narrative was updated later at 10:01. Therefore the historical statement cannot stand unless the 6/6 record is proved false. The record is not merely outdated; it is either wrong, or it describes different `guard_cycle.py` behavior.

For the current source, however, a line-by-line walk identifies T6 as the sole failure:

- T1: recipe time is `rt+600`; review stamp is `rt`. No review is newer, so the FIXED exemption is examined. The cited recipe exists and is newer than `review_time=rt`, so lines 406–412 allow it. Pass.
- T2: same timing, but no citation. Lines 413–425 refuse it. Pass.
- T3: no review exists, so `newer` and `latest` are empty; lines 413–425 refuse it. Pass.
- T4: `fixed_citations()` explicitly rejects FIXED lines above the disposition heading at lines 128–131. It then refuses. Pass.
- T5: the cited file does not exist, rejected at lines 138–141. It then refuses. Pass.
- T6: the test sets the recipe to `rt-600` and expects refusal ([self-test](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/selftest_guard_cycle_fixed.py:101>)). The review stamp is `rt`, so this decides the result:

> `newer = [p for p, t in revs if t > rmt]`  
> `if not newer:`

([guard_cycle.py](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/hooks/guard_cycle.py:377>))

For T6, `newer` is nonempty. The entire refusal/exemption branch is skipped, and line 426 returns `None`, meaning allowed. That makes T6 fail exactly as suspected.

There is no credible date rollover or DST alternative. Both the recipe setup and frontmatter parser feed the identical local `2026-09-17 10:00` tuple to `time.mktime`; T6 has a ten-minute margin, not a boundary equality. Python defines `mktime()` as converting a local-time tuple, with `-1` requesting automatic DST determination ([Python `time` documentation](https://docs.python.org/3/library/time.html)). `time.time()` only filters BENCH log entries, and BENCH is empty here.

The cycle-18 release refactor is algebraically equivalent. For every slug:

```text
s not in refuted and s not in fixed
```

is exactly:

```text
s not in (refuted | fixed)
```

A FIXED slug outside `PRIOR_ART_SLUGS` cannot create a difference because `fixed_citations()` rejects it first. A `REFUTED:` line in the QUESTION cannot create a difference either: both the stated old expression and `released_slugs()` scan the complete `body`. There is no concrete body on which those two expressions differ.

The new import also does not explain this self-test. `stop_record.py` performs no top-level import of `guard_cycle`; its lazy import occurs only inside `_released()` ([stop_record.py](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/stop_record.py:240>)), which `premature_build()` never calls. `stop_record.ROOT` is a separate module variable and does not assign `guard_cycle.ROOT`. If the lazy import were eventually reached, Python would return the already registered module from `sys.modules`; modules are placed there before their bodies execute specifically to handle recursive imports ([Python import-system documentation](https://docs.python.org/3/reference/import.html)).

An alternative explanation for the same evidence is therefore historical code drift: the recorded 6/6 may have been real under the September 17 `guard_cycle.py`, while the current September 18 rewrite introduced the branch behavior now visible—even if the intended edit description says otherwise. A second alternative is that the narrative’s 6/6 was copied or asserted without preserving raw output. No original per-case log remains in the repository, so the available evidence cannot distinguish those histories.

What would falsify the present T6 diagnosis is a direct observation that, with `rmt=rt-600`, `stamp(review) <= rmt`, or that `premature_build()` returns a refusal. What would falsify the historical-regression alternative is a dated raw September 17 per-case output showing T6 already failing, or a trustworthy pre-cycle18 `guard_cycle.py` demonstrating the same path and result.

After all four attacks, I believe the narrow current-code conclusion holds: T6 is the 5/1 failure, and the stated release-set refactor cannot cause it. I do not accept the broader “has been failing since added” claim without resolving the explicit 6/6 record.

The cheapest discriminating test is a standalone two-case temporary probe—not the blocked suite—that prints only `recipe_mtime`, `stamp(review)`, `newer`, and `premature_build()` for T1 (`rt+600`) and T6 (`rt-600`). If it reports T1 allowed and T6 allowed, the current-case diagnosis is settled; then only the missing September 17 raw output or pre-cycle18 source can decide whether this is old test debt or later code drift.

## Sources

(extract from answer)

## What was done with it

**Outcome: ANSWERED. Half the claim CONFIRMED by measurement, half REFUSED and left open.**

1. **The failing case is T6 — now MEASURED, not inferred.** The review's line-by-line walk said T6 alone fails
   because `premature_build`'s `newer` list is non-empty when the recipe is older than its review, so the whole
   `if not newer:` block is skipped and the function returns `None`. Run 2 of the driver was changed to ECHO the
   per-case lines and `tools/bench/cycle18_stopgate.log` now carries them:
   `T1..T5 PASS`, `T6 FAIL expected=REFUSED got=ALLOWED`. The prediction is confirmed exactly.
2. **The refactor is cleared.** Both arms agree the cycle-18 change (lifting `REFUTED:` out of
   `guard_cycle.main()` into `released_slugs()`, plus the module-level `import stop_record`) cannot reach that
   path. `selftest_guard_cycle_rerun.py` scored 4 pass / 0 fail in the same run, and the new gate's own
   self-test scored 18 pass / 0 fail.
3. **The half this review REFUSED is recorded as OPEN, not argued away.** codex would not accept "T6 has failed
   since it was written", because `archive/2026-09-17-status-d1-phase-full-narrative.md:254` records 6/6 while
   explicitly naming T4/T5/T6, and the self-test's own stamp (09-17 09:29) predates that narrative (10:01). So
   either that record is wrong or `guard_cycle.py` drifted after it. **A material session does not decide that**
   — it is in this cycle's `OPEN:` line for the judgement session, and the self-test was NOT edited.
4. **What changed in the code because of this review**: `tools/bench/cycle18_stopgate_driver.py` now echoes the
   regression output (run 1 discarded it, which is why the answer cost a 772 s dual review to recover) and runs
   `selftest_guard_cycle_fixed.py` as a REPORTED `KNOWN` line rather than a gate, so a pre-existing defect that
   this review has already adjudicated does not re-arm `guard_peer` on the next cycle's first build.

### Cycle 19 (2026-09-18) — item 3 is CLOSED by measurement: explanation (a). codex's refutation does not hold.

The cycle-19 judgement session put the two competing explanations to the machine (one bounded read-only
dispatch, measurement only, per `docs/cycle19-plan.md`'s pre-step):

- **Nothing on disk has ever recorded T6 passing.** `tools/bench/selftest_guard_cycle_fixed.log` **does not
  exist**; no `tools/bench/*.log` line names this suite's T6 as PASS (the T6 hits there belong to
  `selftest_stamp_window`, `test_opsubvis_v1`, `test_opwiresr`).
- **The citation codex relied on is a statement of INTENT, not of output.**
  `archive/2026-09-17-status-d1-phase-full-narrative.md:254-256` reads "T6 a path last changed BEFORE the review
  → REFUSED" — the verdict each test *expects*, written in prose inside an aggregate "6/6", with no per-test
  output line and no log citation. It therefore cannot distinguish "T6 returned REFUSED" from "T6 is written to
  expect REFUSED", which is exactly the distinction the refutation needed it to carry.
- **The drift hypothesis has no evidence and cannot acquire any**: no `.bak`, no dated copy, nothing under
  `archive/`, no VCS for `tools/hooks/guard_cycle.py`.
- **The defect is an inversion, not an unexercised corner.** `guard_cycle.py:379` gates the whole refusal on
  `if not newer:`, so the presence of a review newer than the recipe *suppresses* the check. CLAUDE.md:449
  condition (b) requires the cited path to have changed **after** the review; a review newer than the recipe is
  precisely the case where a `FIXED:` line is a promise rather than a fix. The gate skips the case it exists for,
  and `selftest_guard_cycle_fixed.py:101` (recipe stamped 09:50, review 10:00, a valid `FIXED_OK` line)
  constructs exactly that case.

**Consequence for cycle 20's fix, and it widens the scope:** the review-newer-than-recipe case has never been
enforced, so D1 route-B run 3 did not evade a working gate — there was nothing there to evade. Fixing `:379` is
therefore a first enforcement, not a regression repair, and every recipe launched under that branch to date was
launched unchecked. The fix belongs in cycle 20 (`docs/cycle19-plan.md` bounded the pre-step to measurement).
No new peer dispatch was made: no new prediction failed here, and the dual review this annotates already ran.
