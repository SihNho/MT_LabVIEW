# c100-5-retrycap-detach

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.1357  in 20 / out 7979 / cache-create 94764 / cache-read 976236  (90s, 16 turn(s))
- **date:** 2026-09-26 21:51:14
- **outcome:** ANSWERED (93s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about a failed self-test (card 100-5; logs tools/bench/selftest_stage_prerun_c100-5.log and tools/bench/selftest_stage_prerun_c100.log).

FACT: `py -u tools/bench/selftest_stage_prerun_stageplan.py` passed 12/0 at 21:35 today (selftest_stage_prerun_c100.log, launched as `py tools/bgrun.py --max-min 6 --log ... -- py -u tools/bench/selftest_stage_prerun_stageplan.py`, foreground). At 21:48 the same self-test gave 11/1 (selftest_stage_prerun_c100-5.log); the only failing row is its sub-test `EX selftest_retry_cap.py`: 7 pass / 1 fail, first_fail "C4 started run +1 (rc=0, counted 1, by/cycle/card on the line)". So rc == 0 and len(counted) == 1 held; the failing conjunct is `c[0]["card"] is None` or `"BGRUN STAGE-RUN recorded" in outp` (tools/bench/selftest_retry_cap.py:112-116).

CLAIM: this is an ENVIRONMENT artefact of how I launched it, not a code regression: I launched the 21:48 run with `py tools/bgrun.py --material --detach ...`. bgrun's detached copy runs with env BGRUN_DETACHED=1 (tools/bgrun.py:40, 96), that env is inherited by every grandchild, and the NESTED bgrun that selftest_retry_cap.py starts (selftest_retry_cap.py:101-105, subprocess.run capturing stdout) then sees BGRUN_DETACHED=1 and does not echo its lines to stdout (tools/bgrun.py:183-185 `echo = os.environ.get(DETACH_ENV) != "1"`), so `BGRUN STAGE-RUN recorded` is missing from `outp` and C4 fails although the record was written (counted 1). The files changed between 21:35 and 21:48 (docs/protocol/stageplan.json replaced by a widening-only schema; tools/bench/sim/disp/*; tools/gscript.py / tools/stagekit.py by a parallel card) do not touch bgrun.py, stage_prerun.record_started or selftest_retry_cap.py.

Give: the strongest reason this claim is wrong; an alternative explanation (e.g. c[0]["card"] not None because of an active task card, tools/bench/cards/active.json, or a concurrent run); what would falsify it; the cheapest discriminating test (my plan: rerun the same self-test with a FOREGROUND bgrun, no --detach, and expect 12/0; and/or rerun with --detach and expect the same 11/1).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**I could not refute the claim.** The C4 failure is almost certainly caused by how the 21:48 run was launched (with `--detach`), not by a code change. The code and the logs pin every part of the failing check except the missing stdout line, and the environment variable explains that line exactly.

**1. Strongest reason it could be wrong.** No passing run has ever been launched through `--detach`. Every earlier passing log starts with `BGRUN START`, not `BGRUN DETACH`: `selftest_stage_prerun_c100.log:1`, `selftest_stage_prerun_stageplan.log:1,73`, `selftest_stage_prerun_stageplan_95.log:1`, `prerun_fix95_selftests_{before,after}.log:1` and `selftest_retry_cap.log:1,19`. So "a detached launch gives 11/1" rests on one observation plus reading the code, not on a comparison. That weakens the evidence but does not contradict the claim.

**2. Alternative explanations, and why they fail.**
- **`c[0]["card"]` is not None:** ruled out.
  - The real `stage_runs.jsonl` has 0 lines mentioning `selftest_dummy`, so the seeded temp file holds none.
  - When C4 records its run, `check_cap` finds 0 earlier runs, which is below the cap of 2, so it returns card id None (`tools/stage_prerun.py:1450-1452`, used by `record_started` at `:1482`).
  - Neither `active.json` nor any concurrent card is read on this path. `cycle_key` is also bypassed, because the test sets `STAGE_RUNS_CYCLE` (`selftest_retry_cap.py:34`, `stage_prerun.py:1397`).
- **Concurrent run or failed record:** ruled out.
  - `STAGE_RUNS` points at a per-process temp directory (`selftest_retry_cap.py:30-33`), so no other process shares the file.
  - A count of 1 with 0 seeded lines means `record_started` returned a record. So `bgrun.py:237` did call `out("BGRUN STAGE-RUN recorded …")`.
- **The line was produced but not captured:** only two ways.
  - (a) The echo was off, which is `bgrun.py:185`: `echo = os.environ.get("BGRUN_DETACHED") != "1"`.
  - (b) The echo was on but `sys.stdout.write` raised and was silently swallowed (`bgrun.py:196-199`). This is unlikely: the line is plain ASCII, stdout was reconfigured to UTF-8 (`:26`), and the same line is echoed in foreground runs.
- **The variable does reach the nested bgrun.**
  - The detached copy sets it (`bgrun.py:96`), and its PID 24720 matches the `BGRUN PID` line (`c100-5.log:1,3`).
  - Every subprocess in the chain inherits the parent's environment: `bgrun.py:226` copies `os.environ`, and `selftest_stage_prerun_stageplan.py:62` and `selftest_retry_cap.py:104` pass no `env`. The Python docs say a child inherits the parent's environment unless `env` is given (https://docs.python.org/3/library/subprocess.html).
  - The nested bgrun gets no `--detach`, so it runs inline with the echo off. C3, C5 and C6 do not look at `outp`, which is why C4 is the only failure. That matches the observed 7/1.

**3. What would falsify it:**
- a `--detach` rerun that passes C4;
- a foreground rerun that still fails C4;
- or the C4 detail list showing a `STAGE-RUN` line. The EX summary line cuts the output short, so the 21:48 log does not show that detail.

**4. Cheapest test.** Run `selftest_retry_cap.py` on its own, not the whole stageplan wrapper. Each run takes about 10 s and touches no LabVIEW:
- **(a)** `py tools/bgrun.py --max-min 3 --log tools/bench/st_rc_fg.log -- py -u tools/bench/selftest_retry_cap.py` should give 8/0.
- **(b)** The same command with `--detach` and a different log should give 7/1, failing C4 with detail `[]`.

If (b) gives 8/0, the claim is false. If (a) gives 7/1, it is a real regression. Your planned two-way rerun is correct; running the file alone is cheaper, and its log shows the C4 detail directly.

**A real defect this exposes** (not a regression): C4, and any self-test that reads a nested bgrun's stdout, cannot pass when launched detached. Two ways to fix it:
- in `selftest_retry_cap.bgrun()`, pass `env={k: v for k, v in os.environ.items() if k != "BGRUN_DETACHED"}`;
- or have C4 read the nested log file `TMP/run.log` instead of stdout.

Until one is done, never launch this self-test through `--detach`.

I could not archive this verdict: file writing is disabled in this session.

## Sources

(extract from answer)

## What was done with it

Card 100-5 (material). The claim survived the attack and the discriminating test confirmed it: the review's test (a),
`selftest_retry_cap.py` alone under a FOREGROUND bgrun, gave 8/0 with C4's `BGRUN STAGE-RUN recorded ... card=None`
line present (tools/bench/diag_c100_retrycap_fg.log); the full `selftest_stage_prerun_stageplan.py` under a foreground
bgrun gave 12/0 (tools/bench/selftest_stage_prerun_c100-5b.log). Not a regression: the 11/1 of
selftest_stage_prerun_c100-5.log came from launching it with `--detach` (BGRUN_DETACHED=1 inherited by the nested
bgrun turns its stdout echo off, tools/bgrun.py:185). Test (b) (detached rerun) was not spent. The self-test defect the
review names (C4 cannot pass under a detached launcher; fix = strip BGRUN_DETACHED in selftest_retry_cap.bgrun(), or
read TMP/run.log) is NOT fixed here - selftest_retry_cap.py is outside card 100-5's write flags; reported to the
caller as an OPEN item. Until then this self-test is launched in the foreground only.
