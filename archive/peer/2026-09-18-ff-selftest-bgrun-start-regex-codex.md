---
type: peer-review
status: historical
date: 2026-09-18
tags: [peer-review, archive, labview]
disposition: legacy
legacy_note: closed as legacy 2026-09-25 by card chat-L1 (cutoff 2026-09-22; user 2026-09-25 lint order before runner resume)
---

# ff-selftest-bgrun-start-regex-codex

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-18 11:39:45
- **outcome:** ANSWERED (47s)
- **why asked:** second failed prediction in the firefighter self-test (guard_peer)
- **verdict:** accepted - applied

## Question

SECOND FAILED PREDICTION in tools/bench/selftest_cycle_runner_ff.py (log tools/bench/selftest_cycle_runner_ff.log,
11:38 run): after the whitespace-split fix the dry runner ran 4 cycles (exit 0, "--cycles 4 exhausted") but logged
NO "FAILED-RECIPES" and NO "FIREFIGHTER" line, in both modes.

My explanation: cycle_runner.py's BGRUN_START_RE was `^BGRUN START .*?:\s*(.*)$` - the lazy `.*?:` stops at the
FIRST colon, which is inside the timestamp `2026-09-18 00:00:00`, so the captured "command" began with
`00:00 limit 1.0 min: py tools/recipes/...`; the newly anchored command-position RECIPE_RE (`^\s*(MATERIAL=1 )?py
...tools/recipes/<name>.py`) then cannot match, so failed_recipes() returns an empty set every cycle and the trigger
never arms. Fix applied: BGRUN_START_RE = `^BGRUN START .*? min:\s*(.*)$` (bgrun writes `limit <N> min: <cmd>`).

Already ruled out: the fake logs ARE written (the stand-in ran 4 times, count.txt reached 4); log mtimes fall in
the cycle window (each cycle takes >1 s because the stand-in sleeps 1.1 s).

Attack this: is there another reason failed_recipes() would return empty (mtime window edges: t0 is taken BEFORE
subprocess.run and the window end AFTER - can a log written 1.1 s into the cycle fall outside? os.listdir on a
temp dir; the `.log` filter; the startswith(("cycle_","peer_","priorart_","retro")) exclusion)? What would falsify
the regex explanation? Cheapest discriminating test.



--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The strongest reason your claim is wrong as stated is that it assigns causality before proving the fake logs survive the filename filters. A newly written `.log` named `cycle_*`, `peer_*`, `priorart_*`, or `retro*` is unconditionally excluded; its existence and in-window mtime therefore prove nothing about whether `BGRUN_START_RE` was reached.

Alternative explanation: the self-test’s fake-log basename hits that exclusion—or its suffix differs in case from exact `.log`. Either produces four successful cycles with no `FAILED-RECIPES` or `FIREFIGHTER`.

The mtime-edge theory is weak. If `t0` is recorded before `subprocess.run()` and the end time afterward, a file modified 1.1 seconds during a synchronous child normally lies inside the window; `subprocess.run()` waits for process completion [Python documentation](https://docs.python.org/3/library/subprocess.html#subprocess.run). Exceptions would require preserved/backdated metadata or a detached writer.

Your regex mechanics are nevertheless correct conditionally: `.*?` takes the earliest colon that permits the remainder to match, so the old expression captures from the timestamp’s first colon [Python `re` documentation](https://docs.python.org/3/library/re.html#regular-expression-syntax).

What would falsify the regex explanation: demonstrate that the relevant log is rejected before line parsing, or show that `failed_recipes()` receives no `BGRUN START` line. Conversely, an admitted candidate whose old capture is `00:00 ...` and whose fixed capture is `py tools/recipes/...` strongly confirms it.

Cheapest discriminating test: in one failing dry cycle, print only three values—candidate basename, its accept/reject reason, and `repr(BGRUN_START_RE.match(line).group(1))`. If the file is excluded, the filename-filter alternative wins; if admitted and the capture begins `00:00`, the regex explanation wins. Given an admitted file and the supplied line format, I believe your regex explanation holds; evidence that the file never reaches the parser would change my mind.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)

ACCEPTED 2026-09-18 12:1x: regex fix kept (capture must start with the command); opus's finding applied - failed_recipes() now judges the LAST BGRUN START segment of an appended log, not the first START/first failure anywhere; codex's filename-filter alternative checked: the fixture name build_fake_v0_runN.log is not excluded. Verified by rerunning tools/bench/selftest_cycle_runner_ff.py.
