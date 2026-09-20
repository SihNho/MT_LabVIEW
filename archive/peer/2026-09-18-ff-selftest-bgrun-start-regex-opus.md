# ff-selftest-bgrun-start-regex-opus

- **agent:** claude
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $2.3381  in 12 / out 28336 / cache-create 134775 / cache-read 458405  (383s, 11 turn(s))
- **date:** 2026-09-18 11:46:10
- **outcome:** ANSWERED (385s)
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

## Verdict first

**I could not break the mechanism, but I can break the conclusion.** Hand-tracing the fixture confirms your regex story is *sufficient*; what I am refuting is the inference it licenses — that the trigger works once this line is fixed. It does not, and the self-test is structurally incapable of showing you that.

Two of my planned attacks died on the evidence, and I'll say so rather than dress them up:

- **The fixture matches production exactly.** `bgrun.py:111` writes `f"BGRUN START {ts} limit {a.max_min} min: {' '.join(cmd)}"`, and every real log agrees (`build_d1_v0.log:1`, `build_harness_copy.log:1`). So `.*? min:` is not a fiction you invented to make the test green.
- **The fixture was not edited after the failing run.** Glob's mtime ordering puts `tools/bench/selftest_cycle_runner_ff.py` *before* `tools/bench/selftest_cycle_runner_ff.log` (and `tools/cycle_runner.py` last, i.e. the just-applied fix). The `limit 1.0 min:` text at `selftest_cycle_runner_ff.py:23` is what ran at 11:38, so the diagnosis is not retrofitted onto post-hoc text. Lazy `.*?:` does stop at the timestamp's first colon ([Python docs: "as *few* characters as possible"](https://docs.python.org/3/library/re.html)), and `RECIPE_RE`'s `^` without `re.M` anchors only at string start even under `.search()` ([same page](https://docs.python.org/3/library/re.html)), so `00:00 limit 1.0 min: py tools/...` cannot match. Mechanism confirmed.

## 1. The single strongest reason the claim is wrong

**It is scoped to a fixture that does not resemble the logs `failed_recipes()` will actually read, so a green self-test will certify a broken trigger.** The self-test writes **one fresh file with exactly one `BGRUN START`** per cycle (`selftest_cycle_runner_ff.py:22`, `build_fake_v0_run%d.log`). Real bgrun logs are **appended** (`bgrun.py:102`, `open(logp, "a")`) and routinely hold several runs:

- `build_harness_dispI.log:1,35,76` — three STARTs in one file
- `build_harness_copy.log:1,24`, `build_opaddshiftreg_v0_run2.log:1,6`
- your own `selftest_cycle_runner_ff.log:1,14` — two STARTs, two ENDs

`failed_recipes()` takes `BGRUN_START_RE.search()` (the **first** START, `cycle_runner.py:215`) and `BGRUN_FAIL_RE.search()` (the **first** failure anywhere in the file, `:216`). So a recipe whose log opens with an old `rc=1` and whose *current* run passed is counted as failed — the mtime only has to land in the window, which it does on every re-run, successful or not. Two such cycles fire a Fable firefighter at a recipe that is **passing**. That burns exactly the budget the user's ladder exists to ration.

The same fixture hides a false **negative**, from `RECIPE_RE`'s `^` anchor. Real failing recipe runs are wrapped:
- `build_d1_v0_run4.log:1` — `powershell -NoProfile … -Command py -u tools/lv_restart.py; py -u tools/recipes/build_d1_v0.py`
- `build_opaddshiftreg_v0_run2.log:1` — `cmd C:/ taskkill /F /IM LabVIEW.exe & … & py -u tools\recipes\build_opaddshiftreg_v0.py`

Both are genuine recipe failures; both are invisible to the anchored pattern. And the `(?:MATERIAL=1\s+)?` branch is dead against real logs: `.claude/agents/material.md:26-27` puts the marker on the **outer** command, which bgrun never writes, while `tools/motor_census.py:76` uses `-- env MATERIAL=1 py …`, which the anchor also rejects.

## 2. Alternative explanation of the same evidence

I checked the other five stages and could **not** construct a live alternative for this fixture — the window is safe (`t0` precedes `subprocess.run`, the stand-in writes before its 1.1 s sleep), `--bench-dir` and `FF_BENCH` are the same temp dir, and no fixture filename hits the `.log` / `cycle_|peer_|priorart_|retro` filters. So the honest alternative is not about *which* stage, it is about what a pass would prove:

**A green run after this fix is consistent with "the regex was the only fault" and equally with "the regex was one of two faults, the second sitting in a branch the fixture never exercises."** `BGRUN_START_RE` is upstream of every other stage, so fixing it unmasks nothing — a pass cannot distinguish the two. That is not idle: this file's own comments record two prior rounds diagnosed the same way and both turned out to be "necessary, not sufficient" (`selftest_cycle_runner_ff.py:24` and `:27-28`). Round three deserves less confidence than rounds one and two got.

Underneath: `FAILED-RECIPES` absent is **one bit** at the end of a six-filter pipeline (`cycle_runner.py:205-220`). You read the cause out of the source, not out of the machine. CLAUDE.md's own rule — *"the second time a class of failure is explained by inference rather than read from the machine, the next build is the READER for it"* — is now due, on its third occurrence.

## 3. What would falsify the claim

Call `failed_recipes()` on a directory holding the 11:38 fixture bytes **with the old pattern restored**. If it returns `{'build_fake_v0.py'}`, the regex was never the cause and the fix is cosmetic. Secondary falsifier: any real bgrun START line lacking ` min:` would mean the fix is to the fixture rather than to the runner — I found none, so this one is closed.

## 4. Cheapest discriminating test

One `py -c`, ~1 second, no bgrun, no 4-cycle run, no LabVIEW:

```
import re, os, tempfile, sys; sys.path.insert(0, "tools"); import cycle_runner as C
d = tempfile.mkdtemp()
open(os.path.join(d, "build_fake_v0_run1.log"), "w").write(
    "BGRUN START 2026-09-18 00:00:00 limit 1.0 min: py tools/recipes/build_fake_v0.py\nx\nBGRUN END rc=1 after 1s\n")
print("new:", C.failed_recipes(d, 0, 2e9))
C.BGRUN_START_RE = re.compile(r"^BGRUN START .*?:\s*(.*)$", re.M)
print("old:", C.failed_recipes(d, 0, 2e9))
```

`new={'build_fake_v0.py'}` and `old=set()` isolates the regex as cause and effect in one shot; anything else kills the claim. Then feed it the three real lines above (`build_d1_v0_run4.log:1`, `build_opaddshiftreg_v0_run2.log:1`, a two-START appended file) — that is the test that matters, and it is the one the self-test will never run.

**Durable version, per the "build the reader" rule:** make `failed_recipes()` emit one census line per cycle — `FAILED-RECIPES scan: N files, N in window, N parsed, N recipes` — so the fourth time this returns empty the runner log names the stage instead of costing another review. Same edit, and it retires this whole class of guess.

I still hold the claim is correct about the 11:38 failure. What would change my mind is the `old:` line above printing a non-empty set. What should change *yours* is that being correct here does not make the firefighter trigger correct.

No files written — read-only review, per the brief.

Sources:
- [re — Regular expression operations, Python docs](https://docs.python.org/3/library/re.html)
- [Greedy vs lazy regex quantifiers](https://www.toolhq.io/blog/regex-greedy-vs-lazy-quantifiers)

## Sources

(extract from answer)

## What was done with it

(Claude fills in)

ACCEPTED 2026-09-18 12:1x: regex fix kept (capture must start with the command); opus's finding applied - failed_recipes() now judges the LAST BGRUN START segment of an appended log, not the first START/first failure anywhere; codex's filename-filter alternative checked: the fixture name build_fake_v0_runN.log is not excluded. Verified by rerunning tools/bench/selftest_cycle_runner_ff.py.
