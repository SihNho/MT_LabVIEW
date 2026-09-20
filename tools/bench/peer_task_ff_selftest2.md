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
