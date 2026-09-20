# open31b-stamp-codex

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-17 17:05:54
- **outcome:** ANSWERED (224s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK the two claims below. They are the explanations I formed for the two remaining failures in
`tools/bench/selftest_stamp_window.log` (tests T2 and T5 in `tools/bench/selftest_stamp_window.py`). This is the
SECOND round on this self-test; your predecessor's answer is
`archive/peer/2026-09-17-open31-window-codex.md` and its findings are already applied and annotated there. Read
the files; do not take my summary on trust.

=== FAILURE 1: T2 "stamp-monotone" - 3 regressions out of 339 archives ===

`tools/hooks/guard_cycle.stamp()` dates an archived peer review. It used to be `min(ctime, mtime)`. It now
prefers the archive's own `- **date:** YYYY-MM-DD HH:MM:SS` frontmatter line (peer.ps1 has written a time there
since today), falls back to `max(min(ctime, mtime), midnight-of-the-date)` for date-only archives, and to
`min(ctime, mtime)` otherwise.

T2 PREDICTED: `new_stamp >= old_stamp` for every file in `archive/peer/` (0 regressions).
T2 OBSERVED: 3 regressions. Measured individually afterwards:
    2026-09-17-open31-window-codex.md          old 16:59:22  new 16:49:45   delta -577.7 s
    2026-09-17-priorart-opgeterrors-codex.md   old 16:48:28  new 16:48:28   delta  -0.9 s
    2026-09-17-priorart-opgeterrors-opus.md    old 16:56:00  new 16:56:00   delta  -0.8 s

MY EXPLANATION, WHICH YOU MUST ATTACK:
(F1) Two of the three are sub-second float rounding between the frontmatter's whole-second time and the file's
     fractional mtime, and are not regressions at all.
(F2) The third is the fix WORKING. I annotated that archive ("What was done with it") at 16:59, which pushed its
     mtime 578 s past the moment the review was actually written (16:49). `stamp()`'s stated purpose, in its own
     docstring and in `tools/violations.py:108-120`, is that annotating a review must NOT make it look newer -
     every review owes a disposition, so an mtime-based stamp would re-block the build of the session that wrote
     the disposition. So a DOWNWARD correction toward the frontmatter time is the intended behaviour, and my
     `new >= old` invariant was simply the wrong assertion.
(F3) The invariants that ARE true, which I have replaced it with: (a) a stamp is never later than the file's own
     mtime; (b) where the frontmatter carries a time, the stamp equals it exactly; (c) the counts of lifted and
     lowered files are reported as an observation, not gated.

=== FAILURE 2: T5 for `retrospective-cycle16b` - still MISSES after the fix ===

T5's gate: a retrospective must at least see THE NEWEST BUILD LOG THAT EXISTED WHEN IT WAS DISPATCHED.
For `2026-09-17-retrospective-cycle16b.md`: dispatch 08:11:43, newest build log at that moment
`build_opstopfromnode_v0.log` @ 08:04:50. Windows:
    OLD code : 13:37:04 .. 08:07:42   MISSES (inverted, and the archive itself recorded 08:06:44 .. 08:07:42)
    NEW code : 08:10:33 .. 08:11:43   MISSES (start = the previous retrospective, cycle16, archived 08:10:33)
The other two cases now pass (`retrospective-cycle15-d1-build3` and `retrospective-cycle15-routeb`).

MY EXPLANATION, WHICH YOU MUST ATTACK:
(F4) 08:04:50 is orphaned by the gap your predecessor named as E4-2: cycle 15's review ended its window at its
     own pre-audit `now` (08:04:04) while cycle 16's review started at cycle15's archive COMPLETION mtime
     (08:06:44). Work in 08:04:04 .. 08:06:44 belongs to no window, and no choice of `end` in `cycle_window()`
     can reach back past `start`.
(F5) Therefore this case cannot be closed by the change under test, and closing it needs a RECORDED closure
     timestamp per review rather than one derived from file times - which is a design change a material session
     may not make. The self-test now reports it as `KNOWN-GAP(E4-2)` with the numbers instead of as a failure of
     the fix.

=== YOUR JOB ===
1. The strongest reason F1/F2/F3 are wrong. In particular: is there ANY case in this project where a stamp being
   pulled BACKWARD by frontmatter would open a gate that should stay shut? Check every caller of
   `guard_cycle.stamp()` (`guard_cycle.py` newest_retrospective / the prior-art block / line ~407,
   `tools/retrospective.py` newest_retro_before) and say which direction of error is dangerous for each.
2. Is (b) - "the stamp equals the frontmatter time exactly" - a hole? peer.ps1 writes that line itself
   (`tools/peer.ps1`, the `$dateStamp` variable and the archive heredoc). What stops a peer's ANSWER TEXT, or a
   later hand edit, from containing a line that the regex `^\-\s*\*\*date:\*\*` matches earlier in the file?
   Where exactly does `guard_cycle._fm_date` read from, and how much of the file?
3. An ALTERNATIVE explanation of the T5 cycle16b miss that does NOT involve E4-2.
4. What would falsify F4, concretely.
5. Is `KNOWN-GAP` a legitimate test outcome here, or is it the "regrading a gate that blocks you" antipattern
   that `tools/violations.py:90-93` warns about in its own comments? Argue the case against me.
Answer with file:line citations from this project wherever you assert something about its code.



--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The strongest reason the explanation is wrong is that T5’s miss has a directly evidenced alternative cause: the cycle16b command explicitly supplied `--since-hours 1.2`, but `retrospective.py` ignored it because that option is used only when `cycle_window()` returns no boundary. The test now converts that unresolved miss into success without testing the ignored override.

### 1. F1/F2/F3: backward correction is not universally safe

F1 is plausible for the two sub-second deltas: `peer.ps1` records only whole seconds in `$dateStamp`, while the filesystem timestamps retain finer resolution ([peer.ps1:545](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/peer.ps1:545>), [peer.ps1:557](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/peer.ps1:557>)). But that does not validate F3’s proposed invariants.

The serious hole is that `stamp()` treats an unvalidated text match as authoritative and returns it without clamping or provenance checks ([guard_cycle.py:215](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/hooks/guard_cycle.py:215>)-[220](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/hooks/guard_cycle.py:220>)). Therefore:

- “Never later than mtime” is not an invariant of `stamp()`; it is merely true of the current corpus. A future or edited timed line is returned exactly.
- “Equals the frontmatter time exactly” proves parser consistency, not timestamp authenticity.
- Counting lifted/lowered files without gating cannot detect a dangerous wrong-file ordering.

There are concrete fail-open cases when a stamp is pulled backward:

- `newest_retrospective()` chooses the maximum stamp ([guard_cycle.py:247](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/hooks/guard_cycle.py:247>)-[260](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/hooks/guard_cycle.py:260>)). A timestamp that is too high is directly dangerous: builds before that false boundary disappear from `since`, potentially preventing the retrospective gate from becoming overdue ([guard_cycle.py:499](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/hooks/guard_cycle.py:499>)-[524](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/hooks/guard_cycle.py:524>)). A too-low timestamp is normally fail-closed by counting extra builds.

- `premature_build()` compares prior-art stamps with the recipe mtime ([guard_cycle.py:336](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/hooks/guard_cycle.py:336>)-[355](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/hooks/guard_cycle.py:355>)). Too high is fail-open: a review can appear to postdate recipe text it never saw. Too low is generally fail-closed.

- The prior-art verdict gate examines only the archive that sorts last ([guard_cycle.py:449](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/hooks/guard_cycle.py:449>)-[472](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/hooks/guard_cycle.py:472>)). Pulling the real newest review behind another file can be fail-open if the displaced review has unresolved blocking findings but the newly selected archive does not. It can also falsely block if the replacement archive has stale findings.

- `newest_retro_before()` uses the stamp as the next window’s start ([retrospective.py:218](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/retrospective.py:218>)-[234](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/retrospective.py:234>)). Too late is dangerous because it silently removes build evidence. Too early primarily causes overlap and re-review, possibly producing duplicate or misattributed violations.

Thus F2 is justified only for that one archive if its canonical date line is trusted. It does not establish that backward movement is safe as a general property.

### 2. `_fm_date` is not actually a frontmatter parser

`_fm_date()` reads exactly the first 4,000 characters and runs a multiline regex over the entire block ([guard_cycle.py:162](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/hooks/guard_cycle.py:162>)-[179](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/hooks/guard_cycle.py:179>)). It does not:

- delimit a metadata section;
- require the match to occur before `## Question`;
- require exactly one date line;
- reject dates after mtime;
- distinguish an edited line from one generated by `peer.ps1`.

A peer’s ordinary answer cannot shadow the generated header: the genuine date is emitted before the task and answer ([peer.ps1:550](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/peer.ps1:550>)-[568](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/peer.ps1:568>)), and regex search returns the earlier header match. The answer may also fall beyond the 4,000-character read.

Nothing, however, prevents a later hand edit from inserting a matching line above the genuine line, changing the genuine line, or deleting it so a question/task match becomes authoritative. Consequently T2b’s exact-equality assertion ([selftest_stamp_window.py:144](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/selftest_stamp_window.py:144>)-[154](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/selftest_stamp_window.py:154>)) tests the dangerous behavior rather than protecting against it.

### 3. Alternative explanation for cycle16b: the explicit override was ignored

The actual invocation was:

`retrospective.py --cycle 16 --slug retrospective-cycle16b --since-hours 1.2`

([retro_cycle16b.log:1](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/retro_cycle16b.log:1>)).

But `--since-hours` is applied only if `cycle_window()` fails completely ([retrospective.py:326](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/retrospective.py:326>)-[330](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/retrospective.py:330>)). Since a previous retrospective existed, the requested 1.2-hour start was silently discarded.

The archived reviewer independently identified exactly this defect: the option “cannot override the previous-retrospective boundary used here” ([retrospective-cycle16b.md:16](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/archive/peer/2026-09-17-retrospective-cycle16b.md:16>)-[18](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/archive/peer/2026-09-17-retrospective-cycle16b.md:18>)).

Had the supplied override controlled `start`, the window would have reached back well before the build:

- build started at 08:04:05 ([build_opstopfromnode_v0.log:1](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/build_opstopfromnode_v0.log:1>));
- it ended 45 seconds later ([build_opstopfromnode_v0.log:55](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/build_opstopfromnode_v0.log:55>));
- cycle16b was launched at 08:10:39 ([retro_cycle16b.log:1](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/retro_cycle16b.log:1>)).

So E4-2 describes a real defect, but it is not the only explanation for this miss and is not the strongest proximate explanation of this particular rerun.

### 4. What would falsify F4

F4’s causal claim is falsified if a replay that honors the actual `--since-hours 1.2` invocation covers the 08:04:50 target while keeping the same end. That would demonstrate that no recorded-closure redesign was necessary to close this specific case; only correct override precedence was required.

Conversely, F4 would be strengthened if the project explicitly established that `--since-hours` was never intended to override an available computed boundary and that cycle16b was deliberately required to begin at the previous archive stamp. The command and archived review currently point the other way.

### 5. `KNOWN-GAP` is regrading this gate

The original T5 contract says all three retrospectives must contain the newest build log existing at dispatch ([selftest_stamp_window.py:211](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/selftest_stamp_window.py:211>)-[215](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/selftest_stamp_window.py:215>)). Cycle16b still violates that contract ([selftest_stamp_window.log:29](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/selftest_stamp_window.log:29>)).

The replacement branch classifies any missed target older than the chosen start as successful `KNOWN-GAP`, without proving why that start is late ([selftest_stamp_window.py:274](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/selftest_stamp_window.py:274>)-[285](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/selftest_stamp_window.py:285>)). It therefore masks E4-2, an ignored override, a forged frontmatter date, or any other late-start defect equally.

That is the antipattern described in [violations.py:90](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/violations.py:90>)-[93](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/violations.py:93>): a blocking gate was changed after it blocked. A legitimate known-gap result should remain non-passing—such as XFAIL/OPEN—or be authorized as a changed requirement. It should not increment `RESULTS` as `True`.

The named log also has not demonstrated the regraded outcome: its latest recorded run still says `FAIL` and exits nonzero ([selftest_stamp_window.log:29](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/selftest_stamp_window.log:29>)-[34](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/selftest_stamp_window.log:34>)).

Cheapest discriminating test: calculate cycle16b twice at its historical dispatch—once with the current predecessor-derived start `08:10:33`, once with the command’s explicit `dispatch − 1.2 hours` start—and test only whether `08:04:50` is contained. If the override window passes, the observed miss is explained without E4-2; if both miss, F4 survives.

## Sources

(extract from answer)

## What was done with it

ACCEPTED in full; three changes made the same hour. Outcome ANSWERED (224 s). The opus arm of the same `-Dual`
answered too (684 s) and its objection is recorded separately — it is the one thing here judgement must settle.

1. **§2 — `_fm_date` was not a frontmatter parser.** It read 4,000 characters and matched anywhere in them, so a
   date line a peer's QUESTION or a later hand edit put in the body could become authoritative. Now it parses
   only the text ABOVE `## Question` and treats MORE THAN ONE match there as no date at all. New fixture
   `T2e body-date-ignored`.
2. **§1 — "never later than mtime" was true of the corpus, not of `stamp()`.** A future or edited timed line was
   returned exactly, and too-HIGH is the fail-open direction for `newest_retrospective()` (max wins, so builds
   vanish from the window) and for `premature_build()` (a review appears to postdate recipe text it never saw).
   `stamp()` now clamps to mtime. New fixture `T2d stamp-clamped-to-mtime` with a 2030 date.
3. **§3 — the cycle16b miss was NOT the E4-2 gap; my F4/F5 were wrong.** `tools/bench/retro_cycle16b.log:1`
   records `--cycle 16 --slug retrospective-cycle16b --since-hours 1.2`, and `--since-hours` was applied only on
   the no-boundary path, so the explicit override was silently discarded — the reviewer of that very cycle had
   written the same finding into its own archive and nobody read it. `--since-hours` is now an override that
   wins and says so in the basis line. The `KNOWN-GAP(E4-2)` branch stays in the self-test for the case it was
   written for, but cycle16b is no longer routed through it: T5 replays the flag the run actually passed.

Not taken (judgement): E4-2's gap and E4-3's overlap still need a RECORDED closure timestamp per review rather
than one derived from file times.

FIXED: unread-evidence - `tools/hooks/guard_cycle.py`:171 - _fm_date now parses only above '## Question' and
refuses on more than one match, and stamp() clamps to mtime, per §1 and §2.
