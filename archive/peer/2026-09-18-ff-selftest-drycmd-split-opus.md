# ff-selftest-drycmd-split-opus

- **agent:** claude
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.0124  in 14 / out 32698 / cache-create 189724 / cache-read 503295  (422s, 13 turn(s))
- **date:** 2026-09-18 11:37:08
- **outcome:** ANSWERED (423s)
- **why asked:** failed prediction in the firefighter self-test (guard_peer)
- **verdict:** accepted - both findings applied

## Question

FAILED PREDICTION in tools/bench/selftest_cycle_runner_ff.py (log tools/bench/selftest_cycle_runner_ff.log, 11:28):
predicted the dry runner would log FAILED-RECIPES for cycles 1-2 and a FIREFIGHTER line for cycle 3; observed both
modes ended "exit 2" on cycle 1 and 2 immediately (0 s) and RUNNER STOP "exited non-zero twice".

My explanation: `tools/cycle_runner.py` splits `--dry-cmd` on whitespace (docstring line: "Whitespace-split, so it
carries no path with a space in it"), and the self-test passed `sys.executable` + an ABSOLUTE path under
`G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop\...` - which contains spaces -
so the stand-in command was mangled and py exited 2 ("can't open file"). Fix applied: pass
`py tools/bench/selftest_cycle_runner_ff.py <mode>` (relative, cwd=ROOT).

Already ruled out: the firefighter code path itself was never reached (no FAILED-RECIPES line, cycles took 0 s);
the fake-log writer needs env FF_BENCH, which the test sets.

Attack this: what else would produce exit 2 in 0 s for both modes? Would the relative-path fix still fail on
this Windows/Git-Bash setup (py launcher, cwd handling in subprocess.run with cwd=ROOT)? Name the cheapest
discriminating test. Also: is "trigger = same recipe basename with BGRUN END rc!=0 / TIMEOUT in two consecutive
cycle windows, by log mtime" a sound trigger, or can a log written by a DIAGNOSTIC (not a build) or a re-run of
an old log fire it falsely?



--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled for this role, as it should be — so here is the review itself.

---

## The claim's mechanism is proven right; its conclusion ("fix applied") is wrong

I did not have to reason about the cause. `tempfile.mkdtemp` dirs are never cleaned up, so both bench dirs from the 11:28 run still exist and hold bgrun's verbatim record of what it launched — `C:\Users\KimLab\AppData\Local\Temp\ffbench_ztxqza9q\cycle_1.log:1-3`:

```
BGRUN START 2026-09-18 11:28:28 limit 180.0 min: C:\...\Python310\python.exe G:\Codes\...\zz_LabView VI\AAA_UNIST\2. Tracking\...\selftest_cycle_runner_ff.py fail
C:\...\python.exe: can't open file 'G:\\Codes\\LabVIEW_Codes\\MinLab\\zz_LabView': [Errno 2] No such file or directory
BGRUN END rc=2 after 0s
```

`ffbench_ras7j3dn\cycle_1.log:1-3` is the same for `fail2`. The whitespace-split story is confirmed by the machine. No alternative survives for the observed exit 2, and inventing one would be a confident wrong answer.

**1. The single strongest reason the claim is wrong.** The fix is necessary and not sufficient — the self-test will fail again at cycle 2, with `rc=3` and `0/2 PASS`, and no `FIREFIGHTER` line. Stop condition 3 fires first:

- the stand-in writes only `count.txt` and `build_fake_v0_run<N>.log` (`selftest_cycle_runner_ff.py:16-25`); `STATUS.md` is written **once**, by the parent, at `:31`, and never touched again.
- `cycle_runner.py:341` increments `unchanged_streak` whenever `next_after == next_before`; `:348` stops at 2.
- the firefighter first needs `len(fail_hist) >= 2` (`:281`) — cycle 3.

Cycle 1 → streak 1, cycle 2 → streak 2 → `RUNNER STOP`. **Cycle 3 is unreachable in this harness.** Two stop conditions were armed to fire at the same cycle; the path bug masked the STATUS bug completely, which is exactly why "exit 2" in the ledger could not settle anything.

**2. Alternative explanation.** For the observed run, none — the child's log is decisive. The live alternative is the *other* producer of "exit 2 in 0 s in both modes": bgrun's own argparse. `bgrun.py:95` calls `ap.error("no command after --")`, and argparse exits **2** on usage errors. If `--dry-cmd` is ever empty, `session_cmd` returns `[]` (`cycle_runner.py:101`) and bgrun exits 2 instantly. Discriminator for next time: that leaves **no `cycle_N.log` at all** (the log opens at `bgrun.py:102`, after `:95` and after the `makedirs` at `:97`). Eliminated by reading: `--max-min 180.0` is `type=float` (`bgrun.py:86`); missing `FF_BENCH` is a `KeyError` → exit 1; `py`'s "no default Python" is 103.

**3. Will the relative path still fail here? No — machine-proven.** bgrun spawns the child with **`cwd=PROJECT` hardcoded** (`bgrun.py:112`, `PROJECT` from its own `__file__` at `:26`), so the relative path resolves against the project root whatever shell called it. Bare `py` through `shell=False` → `CreateProcessW` with `lpApplicationName=NULL`, which appends `.exe` to an extensionless first token → `C:\Windows\py.exe`; `cycle_runner.py:105`'s warning concerns **PATHEXT** (`.cmd`/`.ps1`), which is not applied, while `.exe` is. And the proof is in this very run: `tools/bench/selftest_cycle_runner_ff.log:1` is bgrun's START line for bare `py` + relative path under `cwd=PROJECT`, and it ran.

But the relative path *avoids* the landmine rather than removing it. `--dry-cmd` is `str.split()` in a project root with two spaces, and `:240` documents the hazard as though it were a spec. `nargs=argparse.REMAINDER` — which `bgrun.py:91` already uses — makes it impossible. `shlex.split` is not the fix on Windows; posix mode eats backslashes.

**4. The trigger is not sound.** Four defects, all from the code:

- **(a) fires on the normal case.** bgrun **appends** (`bgrun.py:87`, `:102`), and `failed_recipes` takes the *first* `BGRUN START` (`:210`) and the *first* fail line anywhere (`:211`), neither scoped to one run. A recipe that failed in cycle 1 and **passes** in cycle 2 into the same fixed-name log still reads as failed — the append refreshed the mtime into cycle 2's window while cycle 1's `rc=1` line is still in the file.
- **(b) mtime is not the run's time** (`:204-207`). Any touch re-dates an old failure in — an append, a non-`copy2` archive copy, an editor save. The true timestamp is already on the `BGRUN START` line (`bgrun.py:111`).
- **(c) yes, a diagnostic can fire it.** `RECIPE_RE` (`:181`) matches anywhere in the invocation string, so `py tools/diag_x.py tools/recipes/build_y.py` counts. And the exclusion list at `:200` is a **fifth private copy** of the machinery classifier, narrower than the canonical one — missing `outcome_review`, `audit_cycle`, `violations`, `doc_ingest`, `doc_lint`, `ingest_`, and spelling `priorart_` where `logclass.REVIEW_LOG_RE` spells `prior_?art` (`logclass.py:46-71`). `logclass.py:3-20` exists to stop precisely this; `bgrun.py:28` already imports it.
- **(d) false *clear*, contradicting the firefighter's own prompt.** `FF_PROMPT` (`:186-188`) accepts "a diagnosis with a discriminating test that was RUN" as success and invites running the recipe; the mechanical check (`:327`) accepts only "no failing log this cycle". A firefighter that reproduces the bug first — the obvious move — guarantees escalation, then STOP.

Two smaller ones: a **one-cycle blind spot** (after any firefighter cycle, `ff_active` is True and `ff_pending` None, so neither branch at `:279`/`:281` can fire a *new* firefighter next cycle; `ff_active` only resets at `:292`), and **restart amnesia** (`n` is recovered from the ledger at `:254`, but `fail_hist`/`ff_rung` are in-memory at `:258-259`, so a restart resets the ladder to `low` and "never a third firefighter" is not guaranteed).

**5. What would falsify me.** The re-run printing `FIREFIGHTER | ... cycle 3 runs as fable/low` and `2/2 PASS`. Then I mis-read the stop ordering and withdraw §1.

**6. Cheapest discriminating test.** Re-run the fixed self-test (~10 s, no LabVIEW, no lock) and grep three lines: `Select-String -Pattern "FAILED-RECIPES|FIREFIGHTER|RUNNER STOP|PASS" tools\bench\selftest_cycle_runner_ff.log`. Claim predicts `FIREFIGHTER ... cycle 3 runs as fable/low` and `2/2 PASS`; I predict the `FIREFIGHTER` line is absent and the stop reason is `NEXT section was byte-identical after two consecutive cycles (1 and 2)`, `0/2 PASS`. If mine holds, repair the **stand-in** (append a changing line to `$FF_BENCH\STATUS.md`'s NEXT each cycle), not the runner — stop condition 3 is correct behaviour and must not be weakened to let a test through.

One process note worth the sentence: the mechanism was inferred from a docstring (`cycle_runner.py:240`) while the child's own error message sat one directory listing away in `%TEMP%`, and that inference — right about the cause — carried a wrong conclusion about closure. The reader already exists; it is bgrun, and it had already written the file. Printing the failing `cycle_N.log` beside the runner log at `selftest_cycle_runner_ff.py:43-44` would make the next failure name itself.

**Sources:** [argparse — usage errors exit 2](https://docs.python.org/3/library/argparse.html) · [CreateProcessW — `.exe` appended when `lpApplicationName` is NULL and the token has no extension](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw)

## Sources

(extract from answer)

## What was done with it

(Claude fills in)

ACCEPTED both findings, 2026-09-18 11:5x: (1) the dry stand-in now appends to STATUS NEXT each cycle so stop condition 3 cannot pre-empt the firefighter (tools/bench/selftest_cycle_runner_ff.py); (2) RECIPE_RE in tools/cycle_runner.py now requires the recipe in COMMAND position, and the self-test writes a diagnostic log naming a recipe as an argument and asserts it is NOT counted. Whitespace-split diagnosis confirmed by both arms.
