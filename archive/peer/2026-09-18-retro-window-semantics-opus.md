# retro-window-semantics-opus

- **agent:** claude
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.7054  in 24 / out 35838 / cache-create 216415 / cache-read 1196476  (490s, 24 turn(s))
- **date:** 2026-09-18 09:08:55
- **outcome:** ANSWERED (491s)
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

## 1. The single strongest reason the claim is WRONG

**Its one actionable conclusion — (iii), "a bias that can only understate the true count" — is refuted by a measured double count in the project's own archive.** The tally over-counts, and I can show the same fault counted twice with the same evidence pointer:

```
archive/peer/2026-09-17-retrospective-cycle15.md:226
  VIOLATION: repeated-failure-class | loss_min=43 | loss_usd=14.1418 | evidence=tools/bench/build_d1_v0_run3.log:1
archive/peer/2026-09-17-retrospective-cycle15-d1-build3.md:224
  VIOLATION: repeated-failure-class | loss_min=43 | loss_usd=14.1418 | evidence=tools/bench/build_d1_v0_run3.log:1
```

Byte-identical line, same evidence `file:line`, two archives, **two counted occurrences and 86 summed minutes for one 43-minute event**. A second pair: `archive/peer/2026-09-17-retrospective-cycle16.md:200` and `archive/peer/2026-09-17-retrospective-cycle16b.md:202` both fire `repeated-failure-class` citing `tools/bench/retro_cycle16.log:2`. The direction of the bias is therefore *not* one-way, and the claim asserts a direction it did not check.

That matters because (iii) is the only part of the claim that would change anything: it is an argument that the threshold-3 device rule is being under-triggered. The measured evidence says the opposite risk is live.

---

## A. Does the code select evidence by cycle number, or only by time window?

**Only by time window. The deciding line is `tools/retrospective.py:287`:**

```python
287:    prev = newest_retro_before(now, exclude_slug=slug)
...
289:        start = prev[1]
309:    end, ebasis = now, "now, at window computation (...)"
```

`n` (from `int(cycle)` at :282) appears nowhere in the branch that runs when a previous retrospective exists. Confirmed by the machine, not by reading: `retro_cycle18.log:2` prints `window 2026-09-18 03:42:17 ..`, and `archive/peer/2026-09-18-retrospective-cycle19.md:7` carries `- **date:** 2026-09-18 03:42:17`. The start is that file's stamp, to the second.

**But "`--cycle N` is ONLY a LABEL" is overstated — N reaches evidence selection in three places you did not list, one of which you missed entirely:**

1. **`--cycle` → default slug → `exclude_slug` (`:328` → `:287` → `:223`).** `cycle_window(a.cycle, a.slug or f"retrospective-cycle{a.cycle}")` and `if exclude_slug and b.endswith(f"-{exclude_slug}.md"): continue`. This *does* move the window: run `--cycle 19` right now and the 03:42:17 boundary is skipped as its own archive, so the start falls back to `2026-09-18-retrospective-cycle17.md` (00:02:53) — a ~9 h window instead of ~5 h. On the 03:46 run it was a no-op only because no `*retrospective-cycle18.md` exists (verified: no such file in `archive/peer/`).
2. **`--cycle` is forwarded to the audit (`:350`) and `audit_cycle.py:326-328` uses it** to pick `docs/cycle<N>-plan.md` for C7 "out-of-plan files". So the 03:46 run scoped its scope-creep check against **cycle 18's plan** over a window belonging to cycles 19/20. That is attached evidence changing with N, and in the direction that manufactures false out-of-plan hits.
3. **The task text (`:374`, `:408-410`)** tells the reviewer "this cycle's own plan is `docs/cycle{N}-plan.md`" — a pointer, not a selector, but it aims the reviewer at a document that need not match the window.

**Dead code worth naming:** `retro_archive(n)` (`:195-204`) is the *only* by-cycle selector in the file and it is no longer called in production — `dispatch_time(retro_archive(n))` was removed from `end` (`:300-304`). Grep finds live references only in `tools/bench/selftest_stamp_window.py:281-283`. So the file still *contains* by-cycle selection; it just no longer runs it.

---

## B. The window rule, precisely as implemented

```
start := max{ stamp(f) : f ∈ archive/peer/*retrospective*.md,
                         "retrospective-v2-" ∉ basename(f),
                         not basename(f).endswith("-" + exclude_slug + ".md"),
                         stamp(f) < now }                            (:219-234, :287-289)
         else  mtime(docs/cycle<N>-plan.md)  if that file exists     (:293-297)
         else  no window → main() falls back to --since-hours or 20 h (:329-332)

end   := now, captured BEFORE audit_cycle, task build and peer.ps1  (:309)

override: --since-hours H ⇒ start = end − 3600·H, unconditionally   (:333-341)
```

`stamp()` is `guard_cycle.stamp` (`tools/hooks/guard_cycle.py:260-300`): frontmatter `- **date:** …HH:MM[:SS]` used exactly, else `max(min(ctime,mtime), midnight of the frontmatter date)`, else `min(ctime,mtime)`. `glob` order is irrelevant here because a maximum is taken — [glob returns results in arbitrary order by design](https://bugs.python.org/issue33275), which would have mattered had the code taken the first hit.

**When do `--cycle N` and the window disagree?** Whenever the last retrospective was not written at cycle N's start — which is most of the time here:

| condition | effect | measured instance |
|---|---|---|
| two retrospectives dispatched inside one cycle | the second sees only the gap between them | `retro_cycle18.log:2` — 4 min 33 s |
| a cycle's retrospective never archived (killed run) | that cycle's evidence is inherited by the **next** retrospective, under its label | `retro.log:51-53` and `:54-56` — two killed dispatches; the boundary stayed pinned at 00:02:53 |
| reviewing cycle N after cycle N+1's review landed | the window is the interval **after** the work | the 03:46 run |
| re-running the same slug | own archive excluded; window re-covers already-reviewed time | `newest_retro_before` docstring, `:216` |

**One genuine hole the claim misses.** `start` is the previous review's *answer* time; the previous `end` was `now` captured before its dispatch. Cycle 19: window ended **03:36:08**, archive stamped **03:42:17** — 369 s, matching `- **outcome:** ANSWERED (368s)`. That 6-minute interval falls in no window at all, once per retrospective. It is documented and unfixed at `:306-308`.

---

## C. Is (iii) right?

**The mechanism is right; the stated direction is wrong.** `violations.py:172` iterates `glob.glob(os.path.join(PEER, "*retrospective*.md"))`, so yes — a cycle whose retrospective was never archived contributes exactly zero, and two such runs exist from last night (`retro.log:51`, `retro_cycle18.log`). Your figure checks out too: I count 9 raw `wrong-ordering` lines, minus `2026-09-16-retrospective-v2-cycle13.md` (`comparison: true` at line 5, dropped by `:174`) = **8**.

But look at *which* 8: cycles 7, 8, 9, 10, 11, 12, 13 — plus cycle 19. Seven of eight come from the v1 format whose own replacement notice says it **saturated**: "cycles 11, 12 and 13 each fired ALL NINE" (`tools/retrospective.py:14-17`). And `violations.py:17-19` names a second inflation source in its own docstring: *"the count was inflated by cadence: three retrospectives ran inside five hours, on overlapping work, while the threshold was set assuming cycles spread over days."* A third: comparison archives counted until the flag was added, which "jumped `judgement-in-material` from 3 to 4 and `device-failed` reached its threshold" (`:138-145`).

So the net bias is **indeterminate, and demonstrably inflated in at least two concrete cases** (§1). A missing file subtracts one; a duplicated review adds one; a saturated format adds seven. Calling it "a bias that can only understate" is the `unreported-fact` shape — a partial account of the error quoted as its total.

**And the missing-file loss is partly self-cancelling**, which the claim does not consider: a killed retrospective writes no archive, so it consumes no boundary, and the next successful run inherits the whole span. That is exactly what happened.

---

## D. Alternative explanation, falsifier, and the cheapest test

### The alternative explanation of the same evidence

**The window was 4 min 33 s because a retrospective had been answered 4 min 33 s earlier, and 0 build logs because nothing was built in those 4 min 33 s.** Both facts follow from the operator's dispatch order alone and are independent of what `--cycle` means:

- 03:36:08 `retro_cycle19.log:1` dispatches `--cycle 19`, window `00:02:53 .. 03:36:08 (213 min)`, **17 build logs**.
- 03:42:17 that review is archived (`…cycle19.md:7`).
- 03:46:50 `--cycle 18` is dispatched into the 4½ minutes that remain.

Under this explanation the tool did precisely what `newest_retro_before`'s docstring says it does — *"EVERY retrospective closes a window, not just the previous CYCLE's… A cycle number is a label Claude chooses"* (`:210-217`). Nothing was formed under pressure; it was written down on 2026-09-17 and not read on 2026-09-18.

**Your "already ruled out" fence does not hold.** You dismissed "little work happened" on the grounds that this was "a cycle that built and released a recipe". Check the clock: `build_opfstunnelterm_v0.log:1` starts **2026-09-18 08:59:47**, five hours *after* the 03:46 review, and the prior-art release it needed (`priorart_fstunnel.log:1`, 03:04:33, ANSWERED 524 s, STOP RECORD armed at `:80`) is five *minutes before* 03:36 — inside cycle 19's window. The two nearest builds are `diag_uid_identity.log` (03:16:53) and `c20_release_probe.log` (03:33:41), both before 03:42:17 and both listed in cycle 19's attachment (`…cycle19.md:160,163`). **`0 build logs` is a true and unremarkable statement about that interval.** The anomaly you set out to explain is not an anomaly.

### Consequences (i) and (ii) are false as stated

- **(ii) "cycle 18's is not reconstructible" — refuted on the evidence.** Cycle 18's work was already reviewed, under the label "cycle 19": `…cycle19.md:161-162` attaches `cycle18_arming.log` and `cycle18_stopgate.log`, and its own verdict line cites cycle-18 evidence — `…cycle19.md:244: VIOLATION: device-failed | … | evidence=premature-build@tools/bench/cycle18_stopgate.log:102`. Windows tile the timeline; only the labels are scrambled. **The defect is misattribution, not loss.**
- **(i) "cycle 20 has no retrospective of its own" — true about filenames, misleading about coverage.** Cycle 20's early work (`c20_release_probe.log`, 03:33:41) is inside cycle 19's window and was reviewed there; everything after 03:42:17 is still claimable because the killed 03:46 run wrote no archive and so consumed no boundary.

### The fact that changes the recommendation, and that the claim missed entirely

**This project already records cycle boundaries mechanically, and `retrospective.py` does not read them.** `tools/bench/cycle_runner.log`, written by `tools/cycle_runner.py:152-160`:

```
CYCLE 2 | 2026-09-18 00:11:53 | 2026-09-18 00:59:06 | exit 0 | $18.4765 | …
CYCLE 5 | 2026-09-18 02:30:02 | 2026-09-18 03:56:02 | exit 0 | $39.8614 | …
```

Explicit start **and** end per cycle, with cost. `retrospective.py:306-308` asks for exactly this — *"need a recorded closure timestamp rather than a derived one - NOT taken here"* — while the recorded timestamp sits one directory away. This is the standard remedy for inferring run boundaries from timestamps: [carry an explicit run/correlation identifier rather than deriving membership from a time window](https://skonves.github.io/pages/correlation-ids.html).

Note also that the runner's ordinals and the project's labels are **not 1:1** — five runner cycles (23:18:33 → 03:56:02) against four labels (17, 18, 19, 20). Cycle 18 ≈ runner CYCLE 2 (00:11:53 → 00:59:06). So cycle 18's audit is reconstructible *exactly*, today: `py tools/audit_cycle.py --from <epoch 00:11:53> --to <epoch 00:59:06> --cycle 18`. The peer dispatch can only be approximated (`--since-hours`, `retrospective.py:333-341`, because `end` is always `now` and there is no `--to`) — which is itself the smallest real gap this episode exposes.

### What would falsify the claim

A `--dry-run` invocation in which the printed `window …` line **matches cycle N's own span for at least two different N at the same instant** — i.e. the window tracks the argument rather than the archive. Equivalently: any live call path reaching `retro_archive(n)`.

### The cheapest discriminating test — one command, no LabVIEW, no peer cost

```
py tools/retrospective.py --cycle 18 --dry-run | findstr /B "   window"
py tools/retrospective.py --cycle 20 --dry-run | findstr /B "   window"
py tools/retrospective.py --cycle 19 --dry-run | findstr /B "   window"
```

`--dry-run` returns before `peer.ps1` (`:419-421`), so this costs one audit subprocess and zero dollars.

- **Claim (time window only):** 18 and 20 print an *identical* window starting `03:42:17`. 19 prints a start of `00:02:53` — and that difference is `exclude_slug`, not cycle selection.
- **Alternative (cycle selects evidence):** all three differ and each matches its own cycle's span.

**The trap this test is built to expose:** comparing only `--cycle 18` against `--cycle 19` produces two different windows and would "confirm" cycle-based selection. Any run of this test must include a third N with no archive of its own (20), or it discriminates nothing. That single triple settles A and B together and quantifies the one place where the cycle number genuinely moves the window.

---

**Where I end up:** the mechanism half of your claim survives — I verified it in the code and to the second in the timestamps, and it is not a discovery, it is `newest_retro_before`'s docstring. The conclusions do not survive: (ii) is contradicted by cycle 18's own logs sitting in cycle 19's attachment, (iii) has its direction backwards against two measured double counts, and the 5-minute/0-log observation needs no explanation beyond "a review had just closed the window and nothing was built in the next four minutes". What would change my mind on (iii): a listing showing that the archives absent from `archive/peer/` outnumber the duplicate-evidence lines present in it — that is a count, and it is available from the same glob that `violations.py` already runs.

**Sources:** [glob.glob ordering is unspecified (bpo-33275)](https://bugs.python.org/issue33275) · [glob returns results in non-deterministic order (bpo-30461)](https://bugs.python.org/issue30461) · [correlation IDs vs. inferring boundaries from timestamps](https://skonves.github.io/pages/correlation-ids.html) · [correlation IDs in microservices logging](https://light-trace.robomiri.com/blog/correlation-id-logging-microservices/)

## Sources

(extract from answer)

## What was done with it

Cycle 21 step 1, the `-Dual` failed-prediction review OPEN 49 owed. Arm 2 of 2 (arm 1:
`archive/peer/2026-09-18-retro-window-semantics-codex.md`); dispatch log
`tools/bench/peer_retro_window_semantics.log`, `BGRUN END rc=0 after 621s`, `DUAL DONE: codex rc=0, opus rc=0`.

Both arms AGREE and both PARTLY REFUTE the claim, independently naming the same deciding line
(`tools/retrospective.py:287`) and the same three N-dependencies (default slug → `exclude_slug` at `:328`/`:223`;
`audit_cycle.py:325-327` C7 plan; the `:293-297` fallback). This arm adds the measured start-equals-stamp check
(`retro_cycle18.log:2` 03:42:17 == `2026-09-18-retrospective-cycle19.md:7` date), the dead-code note on
`retro_archive(n)` (`:195-204`, no live caller), the ~6-minute per-retrospective gap that falls in no window
(`:306-308`), and the `--dry-run` triple-N discriminating test at zero dollars.

No decision taken here: this material session reported the facts to the judgement session, which owns the
windowing rule, the counting-bias direction and OPEN 49's disposition. No code was changed by this review.
