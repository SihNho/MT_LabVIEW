# cycle18-t6-regression-opus

- **agent:** claude
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $4.0548  in 24 / out 41139 / cache-create 230269 / cache-read 1354952  (554s, 21 turn(s))
- **date:** 2026-09-18 00:38:26
- **outcome:** ANSWERED (558s)
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

Write is disabled in this session, as the read-only brief requires — the review is below.

---

# The claim is wrong where it matters most: T6 **passed** on 2026-09-17, and the thing that broke it was not cycle 18

I confirm only the narrow part — T6 is the failing case — and refute the three load-bearing parts: "unreachable by construction", "failing since T4–T6 were added", and the implied disposition that the test's premise is wrong.

## 1. The single strongest reason the claim is wrong

**T6 was reachable, was reached, and passed — under seven minutes before its own threshold — and the project's 6/6 record is accurate rather than stale.**

The claim says the recipe being older than the review makes the FIXED branch unreachable "BY CONSTRUCTION". That is an *atemporal* statement about the test. But reachability here is decided by `stamp()`, and `stamp()` was rewritten on the afternoon of 2026-09-17.

The fixture pins only mtime:

```python
os.utime(p, (rt, rt))          # selftest_guard_cycle_fixed.py:65
```

On Windows `os.utime` sets atime and mtime only — it cannot set creation time — while `os.path.getctime`/`st_ctime` *is* creation time ([python docs via note.nkmk.me](https://note.nkmk.me/en/python-os-stat-file-timestamp/), [GeeksforGeeks os.utime](https://www.geeksforgeeks.org/python/python-os-utime-method/)). So the review file's ctime is **the wall clock of whoever runs the test**.

Pre-OPEN-31, `stamp()` was `min(ctime, mtime)` — `guard_cycle.py:222-223` still describes that as its whole design. T6 sets `rmt = rt-600 = 2026-09-17 09:50:00`, and the gate turns on one line:

```python
revs  = [(p, stamp(p)) for p in glob.glob(os.path.join(PEER, "*priorart*.md")))]   # guard_cycle.py:377
newer = [p for p, t in revs if t > rmt]                                            # :378
if not newer:                                                                      # :379
```

* run **before 09:50** → `stamp = min(ctime≈09:4x, 10:00) = 09:4x` → `newer` empty → block entered → `fixed_citations` rejects the backdated citation at `guard_cycle.py:147` (`fm 09:50 <= rt 10:00`) → refusal → **T6 PASS**
* run **today** → `stamp()` reads the frontmatter and returns exactly `rt` = 10:00 > 09:50 → `newer` non-empty → `premature_build` returns `None` → **T6 FAIL**

And the machine dates it. `tools/bench/build_opsentinel_ops.log:1`:

```
BGRUN START 2026-09-17 09:43:20 limit 30.0 min: py -u tools/recipes/build_opsentinel_ops.py both
```

`archive/2026-09-17-status-d1-phase-full-narrative.md:254-258` records 6/6 and says the exemption *then* "released the real case twice in this session (`build_opsentinel_ops.py`, `build_d1_v0.py`)". So the 6/6 run precedes 09:43:20 — **inside** the window where T6 passes, with under seven minutes of margin (run 3 started 09:50:24, already 24 s past the threshold).

The OPEN-31 rewrite is dated by the archives it produced: `archive/peer/2026-09-17-open31b-stamp-opus.md:105` (17:05:54) and `:29`/`:106` (16:49:45). `tools/peer.ps1:538` confirms the same round is when frontmatter gained a time. That is ~7 hours *after* the 6/6.

The internal check is exact: under this story **only T6 flips**, because T1–T5 all use `offset=+600` (`rmt` = 10:10) and `newer` is empty under both the old and the new `stamp`. 6/6 → 5 pass / 1 fail, one case. Nothing else in the file moves.

So the contradiction the brief asked me to resolve resolves *against* the claim. The claim offered "stale or wrong" as the only two branches for the 6/6 line and never considered "correct, and the gate changed underneath it".

## 2. Which case fails, by reading, with the deciding lines

T6 — confirmed independently, and T1–T5 confirmed passing:

| | `rmt` | `newer` | path taken | result |
|---|---|---|---|---|
| T1 | rt+600 | empty | `fixed_citations` → `fp in cited` → `None` (`:411-412`) | ALLOWED ✓ |
| T2 | rt+600 | empty | no FIXED line → `cited` empty → refusal (`:413`) | REFUSED ✓ |
| T3 | rt+600 | empty (`revs` empty) | `latest` None → refusal | REFUSED ✓ |
| T4 | rt+600 | empty | FIXED above the heading → `bad` (`:129-131`) | REFUSED ✓ |
| T5 | rt+600 | empty | path missing (`:139-141`) | REFUSED ✓ |
| **T6** | **rt-600** | **non-empty** | **`if not newer:` skipped → `return None` (`:426`)** | **ALLOWED ✗** |

The two lines that decide it are `selftest_guard_cycle_fixed.py:101` (`recipe_mtime_offset=-600`) and `guard_cycle.py:378-379`.

## 3. An alternative explanation of the same `5 pass / 1 fail`

**The regression is real and belongs to OPEN 31, not to cycle 18.** `stamp()` learning to read `- **date:**` collapsed an asymmetry the morning code depended on: `review_time()` read the frontmatter (`:101-109`) while `stamp()` read the filesystem (`:244`). `review_time`'s own docstring is written in the future tense — *"If peer.ps1 ever writes a time too"* (`:99`) — which dates it before peer.ps1 carried one. T6 was passing precisely because those two clocks disagreed. OPEN 31 made them agree, and the test died.

Under this alternative, cycle 18's regression cover **worked**: it is the first thing to detect a side-effect of the OPEN-31 change, and the explanation under review would dispose of it as "the test's premise is wrong" — deleting the detector. `stamp()` is read by `premature_build`, the verdict gate, `newest_retrospective()`, `retrospective.py:186,225,300`, and now by `stop_record` through `released_slugs`. If it moved one gate it may have moved others, and that question does not get asked if T6 is written off.

## 4. The brief's other four candidates — checked, and three are dead ends

**(2) The `released_slugs` refactor cannot differ.** `s not in A and s not in B` ⟺ `s not in (A|B)`, by definition of union; both read the same `body`. Neither named sub-case produces a difference: a non-`PRIOR_ART_SLUGS` slug is rejected at `:135-137` before reaching `ok`, and `slugs` at `:520` is already filtered, so a stray member of `released` can only match nothing. **There is no body of text on which the two expressions differ.**

There *is* a standing fail-open, though it is not this failure and not new: `PRIOR-ART:` slugs are read only from the answer half (`:519-520`), while `REFUTED:` is read from the whole `body` (`:179`) — the exact defect the `:518` comment says it fixed for slugs. Cycle 18 has now **exported** that asymmetry to a second gate (`stop_record.py:257`), so a line-initial `REFUTED: <slug>` anywhere in a review file now releases a launch stop record too. I found no current instance — the templates at `:536` and `stop_record.py:285` emit `<slug>` in angle brackets, which `[a-z-]+` cannot match — so this is a widened blast radius, not a live hole.

**(3) `import stop_record` is inert on this path.** `guard_cycle.py:61` inserts the *real* `ROOT/tools` at import time, before any monkeypatch; `stop_record`'s module body (`:59-74`) only computes paths and compiles regexes; it never reads or writes `guard_cycle.ROOT`; and `premature_build` never calls it — the only call site is `main()` (`:462`), which the self-test never invokes (`selftest:75` calls `premature_build` directly). The lazy import at `stop_record.py:254-256` runs at call time, never during import, so it cannot bind a half-initialised module. The driver's own probe asserted this and passed (`cycle18_stopgate_driver.py:62-72`).

**(4) Clock dependence — yes, and it is the answer.** Not `MAX_AGE_S` (no age filter is applied to `revs` at `:377-378`), not the `priorart_*.log` scan (BENCH is an empty temp dir, `selftest:51-52`), not DST (both sides derive from the same `time.mktime(..., -1)`, so any offset cancels; KST has none). The live dependence is `stamp()`'s `base = min(getctime, getmtime)` at `:244` against a fixture that pins only mtime. **T6 was always a time bomb; OPEN 31 detonated it.**

**(5) The record.** Resolved above — and one thing worth stating plainly: `grep -n "SELFTEST guard_cycle"` across the whole project returns **exactly one hit**, the `print` at `selftest_guard_cycle_fixed.py:106`. No log anywhere records this self-test's output. The 6/6 was read off a terminal, never archived, which is why the claim could treat it as soft evidence. That is a gap in the record, not grounds to assume the record is wrong.

## 5. What would falsify my account

* The probe below showing `len(newer) == 0` for T6 today → my reading of the short-circuit is wrong and the fault is inside `fixed_citations`.
* The self-test having actually been run **after 09:50** on 2026-09-17 → even the old `stamp` gives `min(10:0x, 10:00) = 10:00 > 09:50`, T6 would have failed then too, and 6/6 would be an unmeasured assertion.
* `_fm_date`/the frontmatter branch of `stamp()` turning out to predate 09:43 → the morning run could not have passed.

**Where the evidence does not settle it:** I have the session window (`narrative:240`, `retrospective-cycle15-d1-build3.md:236` — "logs written 09:3x–10:0x") and the 09:43:20 bgrun line, but the ordering "self-test ran, *then* the recipe was released" is a sentence in a narrative, not a machine record, because no log of the self-test exists. That sentence is the one inferential link in my chain, and the window it has to fit is only ~7 minutes wide. I would not call this settled beyond the probe in §6.

## 6. The cheapest discriminating test

**Zero-cost, already done:** the `grep` in §4(5) — one hit, the `print` itself. No archived measurement of this self-test has ever existed.

**Then, ~1 second and gated by nothing:** a ~10-line probe in the scratchpad, **outside** `tools/recipes/` and `tools/bench/`. `guard_cycle.BUILD_RE` requires `tools/recipes/` (`:40`) and `guard_peer.RUNS_RE` requires `tools/recipes|bench` (`guard_peer.py:45`), so a file anywhere else is touched by neither gate — no `CYCLE_GUARD_OFF`, no `PEER_GUARD_OFF`, no waiting on this review. It imports `guard_cycle`, rebuilds the same temp tree, and prints per case: `stamp(review)`, `review_time(review)`, `rmt`, `len(newer)`, and the return value.

* Predicts my account: T6 shows `stamp == review_time == rt`, `len(newer) == 1`; T1–T5 show `0`.
* **The decisive step:** stub `guard_cycle._fm_date = lambda p: (None, False)` — that is precisely the pre-OPEN-31 `stamp` — and re-run T6. If it flips to PASS, the 6/6 is vindicated and the regression is dated to OPEN 31. If it still fails, my account is wrong.

Two facts worth having on record for whoever runs this: the driver **already echoes** the per-case lines (`cycle18_stopgate_driver.py:89`, with `:85-88` noting run 1 swallowed them), so "we cannot see which case failed" expires on its own once `guard_peer`'s 6-hour `MAX_AGE_S` window (`guard_peer.py:69`) passes over `cycle18_stopgate.log`. And this review cannot lift that gate regardless — `review_quality` rejects `agent: claude` (`guard_peer.py:143-146`); only the codex arm of this dual dispatch discharges it.

## 7. What I would do with T6 — and what I would not

**Do not delete it.** Its named condition, the `fm <= rt` rejection at `guard_cycle.py:147-151`, is the entire strictness argument for `FIXED:` ("a promise is not a fix"), it is fully reachable from `main()`'s verdict gate and from `stop_record._released` where no `newer` short-circuit exists, and it currently has **no test at all**. Retarget T6 at `released_slugs`/`fixed_citations` directly, and assert on `stamp()` and `review_time()` as numbers so wall-clock creation time stops deciding the verdict.

Within `premature_build` the branch is still reachable, narrowly: entering needs `stamp = min(fm, mt) <= rmt` while rejecting needs `review_time = fm >= recipe_mtime`, so it requires `mt < fm` — an archive whose mtime precedes its own frontmatter stamp (a re-archive under NTFS tunneling, a hand-edited date, a clock step). Narrow, but "narrow" is not "by construction".

**Sources:** [os.stat / getctime on Windows](https://note.nkmk.me/en/python-os-stat-file-timestamp/) · [os.path.getctime](https://www.geeksforgeeks.org/python-os-path-getctime-method/) · [os.utime sets atime/mtime only](https://www.geeksforgeeks.org/python/python-os-utime-method/) · [ctime is not creation time off Windows](https://dev.to/nguyendhn/bty-day-5-ctime-does-not-refer-to-creation-time-2mkl)

## Sources

(extract from answer)

## What was done with it

**Outcome: ANSWERED. This is the opus arm of the dual dispatch; its companion is
`archive/peer/2026-09-18-cycle18-t6-regression-codex.md`, where the full disposition is written.**

Agreement with the codex arm on the part that mattered: **T6 is the single failing case**, and the cycle-18
refactor cannot reach the path that decides it. Run 2 of `tools/bench/cycle18_stopgate_driver.py` then MEASURED
it (`tools/bench/cycle18_stopgate.log`): `T1..T5 PASS`, `T6 FAIL expected=REFUSED got=ALLOWED`.

This arm's distinctive contribution, kept because it narrows the open question: the T6 branch is **not**
unreachable in the absolute sense the original claim asserted — entering it needs
`stamp(review) <= recipe_mtime` while rejecting the FIXED line needs `review_time >= recipe_mtime`, so it is
reachable when `mtime < frontmatter date` (an NTFS-tunneled re-archive, a hand-edited date, a clock step).
"Narrow" is not "by construction". That is recorded, not acted on: whether the 2026-09-17 6/6 record is wrong
or `guard_cycle.py` drifted after it is a judgement question and sits in this cycle's `OPEN:` line. The
self-test was NOT edited.

Cost comparison for the dual-dispatch experiment (CLAUDE.md, 2026-09-17): both arms ANSWERED, the dispatch ran
772 s wall-clock, and both reached the same verdict on the case that fails.
