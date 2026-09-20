# c36-bgrun-finalline-selftest

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $2.7466  in 16 / out 32702 / cache-create 151366 / cache-read 735467  (460s, 19 turn(s))
- **date:** 2026-09-18 21:57:04
- **outcome:** ANSWERED (462s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim. Do not confirm it. Name the strongest reason it is wrong, an alternative explanation, what
would falsify it, and the cheapest discriminating test.

CLAIM UNDER ATTACK
`tools/bench/selftest_bgrun_final_line.log` ended `BGRUN END rc=1 after 3s` ONLY because the self-test script
`tools/bench/selftest_bgrun_final_line.py` crashed in ITS OWN `print()` — `UnicodeEncodeError: 'cp949' codec
can't encode character '—'` at line 61, while quoting the output of `tools/wait_logs.py`, whose text
contains an em-dash. The claim is that this rc=1 says NOTHING about the repair the test exists to check, and
that the repair is sound.

WHAT WAS REPAIRED THIS CYCLE (both are repairs of existing devices, not new devices)
1. `tools/bgrun.py` — its module docstring has always promised "Always ends by writing BGRUN END / BGRUN
   TIMEOUT", but the file contained no `try/finally` and no `atexit`, so any exit path other than the three
   explicit `out(...)` calls left a log whose last line was `BGRUN START` (four such logs on disk). The repair
   adds a module-level `_STATE` dict, a `_write_final()` that appends the terminal line without ever raising,
   a `try/except SystemExit/except BaseException/finally` around `main()` in `__main__`, a `_STATE["final"]`
   flag set by the three terminal `out(...)` lines so no second line is written, a `_STATE["delegated"]` flag
   set ONLY on a successful `--detach` (where the detached copy owns the log), and a non-fatal stdout echo.
2. `tools/wait_logs.py` — `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` plus a `_p()` printer
   that catches `UnicodeEncodeError` and re-encodes with `errors="replace"`.

THE OBSERVED RUN (the log under review)
  -> PASS B1 normal-exit         runner exit 0   | last: BGRUN END rc=0 after 0s
  -> PASS B2 child-rc-nonzero    runner exit 3   | last: BGRUN END rc=3 after 0s
  -> PASS B3 runner-exception    runner exit 125 | last: BGRUN END rc=125 ... (runner exception: ...subprocess.py line 971...)
  -> PASS B4 timeout             runner exit 124 | last: BGRUN TIMEOUT killed after 3s (limit 0.02 min)
  -> PASS B5 exactly-one-terminal-line   logs with a count other than 1: none
  -> PASS C0 control-cp949-raises        python -c print(em-dash) under PYTHONIOENCODING=cp949 exit 1
  Traceback ... selftest_bgrun_final_line.py line 61 in gate -> UnicodeEncodeError 'cp949' '—'
  BGRUN END rc=1 after 3s
The W1 and W2 gates (wait_logs DONE / RUNNING with an em-dash) never printed a verdict — the crash happened
inside the W1 verdict print itself. The harness was then patched (its own stdout reconfigured to utf-8 and an
ASCII fold in its `safe()` helper) and is being re-run.

ALREADY RULED OUT (do not spend the answer on these)
- "The repair did not run": B1–B4 each exercised a DIFFERENT exit path of the patched `bgrun.py` and each left a
  terminal line; B3's line exists only because of the new `finally` (Popen raises FileNotFoundError before any
  `out()` call).
- "bgrun's own inner-failure scan produced the rc=1": the child process genuinely exited 1 (SystemExit from the
  traceback); no `BGRUN INNER FAILURE` line is in the log.
- "The em-dash came from LabVIEW": no LabVIEW, no VI, no motor and no camera were touched; the em-dash is written
  by the test itself into a temporary fixture log.

QUESTIONS I MOST WANT ATTACKED
(a) Is there an exit path of `tools/bgrun.py` that STILL leaves no terminal line after this repair — e.g. a hard
    kill of the runner itself (taskkill /T on the parent), `os._exit`, a `MemoryError` inside `_write_final`, the
    log file being locked or on a full disk, or the DETACHED copy dying before it writes START?
(b) Is `_STATE["delegated"]` correct? On a successful `--detach` the parent writes NO terminal line and returns 0
    — is there a case where the detached copy then never writes one either, so the log ends at
    `BGRUN DETACH ... / BGRUN START` forever? Is the parent's silence the right choice at all?
(c) Could the new `except BaseException` swallow something that previously produced a useful non-zero exit, or
    change the exit code semantics a caller depends on (argparse `ap.error()` -> exit 2 now passes through
    `except SystemExit`)?
(d) Is the double-guard on the stdout echo (`try/except Exception` in `out()`) hiding a real failure — e.g. a
    full disk that should stop the run?


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

## 1. The strongest reason the claim is wrong

**The repair does not fix a single one of the four logs it was built for — and the machine measured that in this same cycle.**

`tools/bench/repair_c36_selftest.log:33-42` (M1, re-measured identically at `:145-154` and `:264-273`):

| log | lines | START | limit | mtime | has_END |
|---|---|---|---|---|---|
| `diag_fstunnelterm_v2_panelcost` | 48 | 13:29:13 | 12 min | **13:29:15** | False |
| `p2_open_copy` | 8 | 14:35:32 | 180 min | **14:35:35** | False |
| `prose_cycle25` | 1 | 13:56:30 | 8 min | **13:56:30** | False |
| `wait_runner_exit` | 8 | 19:33:35 | 200 min | 20:40:37 | **True** |

Read the mtimes. All three genuine cases stopped being written **0–3 seconds after START**, with their child alive and their deadline minutes-to-hours away. At that instant the runner's main thread is parked in `while not done.wait(timeout=2)` (`tools/bgrun.py:227`) — a loop that re-checks the deadline every two seconds and **cannot raise**. So:

- an exception in the runner's own code is ruled out by the timestamps (there is no raising code executing then);
- an exception in the pump thread is ruled out too — it would leave `done` unset, the main loop ticking, and `BGRUN TIMEOUT` written at `bgrun.py:246` twelve minutes later. Nothing was ever appended;
- a hung child is ruled out for the same reason: the deadline exists precisely for that and would have fired.

The only survivor is that **the runner process ceased to exist within seconds, from outside**. `try/finally` does not run on `TerminateProcess` — Windows' hard kill, and what a job object with `KILL_ON_JOB_CLOSE` does when the calling shell exits ([SuperFastPython](https://superfastpython.com/kill-a-process-in-python/), [docs.python.org/3/library/atexit](https://docs.python.org/3/library/atexit.html)). That is the exact failure `relaunch_detached()` was written for (`bgrun.py:76-89`), and M1 records `has_DETACH_line=False` for all three: none was dispatched with `--detach`.

And the fourth entry is a **false positive**: `wait_runner_exit.log:8` reads `BGRUN END rc=0 after 4022s`. It was never an END-less log — it was a 67-minute job that was still *in flight* when the census was taken. The census that sized the problem counted a running job as a lost one, which is the very confusion the terminal line exists to prevent.

So "the repair is sound" is true only in the narrow sense that it closes internal-exception paths correctly. As a repair *of the observed problem* it is aimed at a class with **zero instances in its own evidence**, and the class that produced all three real cases — the runner destroyed from outside — remains completely open. B1–B4 cannot detect this, because all four gates test paths the process takes *by itself*; the file's own comment at `bgrun.py:260-262` concedes exactly this while the docstring at `:7-12` still promises "Always".

**Secondary, and it breaks the claim's other half:** "this rc=1 says NOTHING about the repair" is false on the log's face. The traceback crashed at old line 61, inside `gate()` — and old 61 is the **PASS** branch. Three independent anchors fix the offset at exactly 11 lines (log `line 149 sys.exit(main())` → `:160`; `line 139 gate(...)` → `:150`; `line 61 print` → `:72`), matching the 9-line reconfigure block added at `selftest_bgrun_final_line.py:43-51` plus a separator plus one line in `safe()` at `:63-65`. `PASS += 1` runs before that print. So W1's `ok` (`:148-149`) evaluated **True**: `wait_logs.py` under `PYTHONIOENCODING=cp949`, on a log whose matched line carries an em-dash, exited 0, printed `DONE`, and emitted no traceback. The run is 7 passes and one harness crash, not a null result.

## 2. Alternative explanation of the same evidence

The crash is not incidental to the harness. **It is the defect under repair, reproducing one level up, inside the same run.**

`PYTHONIOENCODING` and `PYTHONUTF8` appear **nowhere** in `tools/`. Instead the identical one-line band-aid `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` is pasted into ten files: `bgrun.py:22`, `wait_logs.py:38-39`, `cycle_runner.py:46`, `doc_ingest.py:49-50`, `doc_lint.py:45`, `audit_cycle.py:59`, `mark_legacy_dispositions.py:37`, `gemini_executor.py:56`, `outcome_review.py:152`, and now `selftest_bgrun_final_line.py:49`. Cycle 36's repair #2 is instance ten of a per-file fix for a fleet-wide defect — and within the same cycle the pattern failed again in the eleventh file, which the run under review then patched the same way.

Note what repair #2 actually changed: with the reconfigure, `wait_logs` no longer dies — it *emits* the em-dash as UTF-8 (a UTF-8 target encodes it fine, so `errors="replace"` never fires) into a consumer whose stdout is cp949. The hazard moved downstream onto the first process that read it. `bgrun.py:184` already reads its children with `encoding="utf-8"` — i.e. it *assumes* every child speaks UTF-8 — but `child_env` at `bgrun.py:182` never *tells* them to. That unstated contract is the defect; `wait_logs`'s second belt, `_p()` at `wait_logs.py:44-50`, is dead code in every tested configuration (the reconfigure at `:38` means `print` never raises) and re-reads `sys.stdout.encoding` rather than the failing `e.encoding`, so in the one scenario its comment claims to cover — a stream pinned to another codec — it re-raises.

One environment key in `child_env` fixes all eleven files and every future one: `PYTHONIOENCODING=utf-8:replace` (std streams only, the narrower choice) or `PYTHONUTF8=1`, which propagates to Python children precisely because it is an environment variable ([PEP 540](https://peps.python.org/pep-0540/)).

## 3. What would falsify my position

- **On the census:** a runner killed externally, mid-run, that *does* leave a terminal line. That would mean the three logs' cause is reachable by `finally` after all and the repair does address them.
- **On the encoding:** `PYTHONIOENCODING=utf-8` in `bgrun.py:182`'s `child_env` failing to stop the harness crash — then per-file reconfigure really is the only lever and the ten copies are not a smell.
- **On W1:** old line 61 turning out to be the FAIL branch, not PASS — i.e. my 11-line offset being wrong. Check it by any anchor other than the three I used.

## 4. Cheapest discriminating test

**Two commands, ~40 seconds, no LabVIEW, no lock.**

**T1 — does the repair cover the class its census is made of?**
```
py tools/bgrun.py --max-min 60 --log tools/bench/probe_extkill.log -- py -c "import time;print('a',flush=True);time.sleep(600)"
# note the RUNNER's pid, then:  taskkill /F /PID <runner pid>       (no /T — kill the runner, not the tree)
```
My prediction: the log ends at `BGRUN START` with the deadline 60 minutes away — the same shape as `prose_cycle25` / `p2_open_copy` / `diag_fstunnelterm`. If a terminal line appears, I am wrong and the claim's "the repair is sound" survives.

**T2 — one key vs. eleven patches:**
```
py tools/bgrun.py --max-min 1 --log tools/bench/probe_emdash.log -- py -c "print('tail \u2014 here')"
```
Run as-is (predict: child dies `UnicodeEncodeError`, rc=1 — the cycle-36 crash with no self-test in the picture), then add `PYTHONIOENCODING="utf-8:replace"` to `child_env` at `bgrun.py:182` and re-run (predict: rc=0, em-dash intact in the log).

## Answers to (a)–(d)

**(a) Yes — three uncovered paths remain.**
- *External termination*, as above. Only a **sweeper** can close it: nothing the dead process runs can write the line. A ~15-line pass over `tools/bench/*.log` for `START` with no terminal line whose `START time + limit` is in the past, appending `BGRUN LOST (deadline passed, runner gone)`. That is the repair the census actually called for.
- *`p.wait()` is unbounded* (`bgrun.py:248`). The deadline loop exits the moment the pump hits EOF on `p.stdout`. A child that closes stdout without exiting — or a grandchild holding the pipe — parks the runner in `p.wait()` with **no deadline at all**. The repair does not touch this; it is a hang, not an exit path, so `finally` never gets a turn.
- *The terminal line is not guaranteed to start a line.* `out()` writes child chunks verbatim (`bgrun.py:160`); the final chunk before EOF may lack `\n`, so `bgrun.py:254` glues onto it: `no newlineBGRUN END rc=2 after 0s`. `wait_logs` uses `rx.search` and survives, but `audit_cycle.py:77`'s `FAILURE_RE` is anchored `^BGRUN END rc=(?!0\b)\d+` while `audit_cycle.py:246` uses substring `"BGRUN END" in body` — so a **failed** run reads as ended-and-clean. `_write_final` has the same defect and it matters more there, since abnormal exits are exactly when the log ends mid-line. Test: `-- py -c "import sys;sys.stdout.write('no newline');sys.exit(2)"`. Fix: check the last byte, prepend `\n`.
- Full disk / locked log: `_write_final`'s `except Exception: pass` (`:65-66`) swallows it by design. Correct as a finalizer, but it means "Always" is conditional on a writable log — say so in the docstring.

**(b) `delegated` is right in principle, with one live hole.** The parent sets it on `rc == 0`, which means only that `Popen` returned — not that the detached copy survived. `import logclass` sits at module level (`bgrun.py:30`), outside any `try`; a detached copy that fails at import writes its traceback into the log (stderr is pointed there, `:99-104`) and **no terminal line**, because `__main__`'s `try/finally` is never entered. The parent has already returned 0. Result: `BGRUN DETACH` + traceback, read as "still running" forever. The parent's silence is the right default, but the handoff should be verified: sleep ~2 s, confirm a `BGRUN START` after the DETACH line, else set `delegated=False` and let the finalizer write it.

**(c) Two small semantic changes, neither dangerous.** `KeyboardInterrupt` now exits **125** instead of the interpreter's interrupt code, and 125 is overloaded three ways (detach-failed, runner exception, interrupt) — a caller that distinguished them loses that. `sys.exit("message")` would have its message dropped (argparse is unaffected: `ap.error()` prints to stderr itself before raising `SystemExit(2)`, which passes through correctly). One new artefact: `--help` raises `SystemExit(0)` with `_STATE["log"]` still `None`, so the finalizer appends a fake `BGRUN END rc=0 ... (runner exited with no terminal line)` to **stdout**. Harmless today; a `_STATE["started"]` flag set by the START line would be the honest guard.

**(d) No — you are worried about the wrong guard.** `log.write`/`log.flush` are *outside* the `try` in `out()` (`bgrun.py:160`); only the stdout echo is swallowed. A full disk still raises and still propagates. What it propagates *into* is `except BaseException` → `_write_final` → a second failing write → `except Exception: pass`. So the silent failure lives in the finalizer, not the echo, and it is unavoidable there. The correct response is documentation, not code.

**What would change my mind:** T1 producing a terminal line after a hard kill of the runner. Short of that, the repair is a correct fix to paths that were not the cause, and the four-log census that justified it contains one job that had simply not finished yet.

**Sources:** [SuperFastPython — Kill a Process in Python](https://superfastpython.com/kill-a-process-in-python/) · [Python docs — atexit](https://docs.python.org/3/library/atexit.html) · [PEP 540 — UTF-8 Mode](https://peps.python.org/pep-0540/) · [safe-exit (Windows signal coverage)](https://pypi.org/project/safe-exit/0.1.1)

## Sources

(extract from answer)

## What was done with it

ANSWERED (opus/max, $2.7466, 462 s). ACCEPTED IN PART, and its discriminating test T1 WAS RUN the same cycle —
`tools/bench/c36_close_runner.log:15-19`, step 2. Measured: a bgrun runner killed from outside with
`taskkill /F /PID <runner>` (no `/T`), deadline 60 min away, left a 2-line log ending `a` — **no terminal line**.
The reviewer's prediction is CONFIRMED: `try/finally` does not run on `TerminateProcess`, so this repair closes
the internal-exception class (B1–B4, all four exit paths now write a terminal line, 8/8 in
`selftest_bgrun_final_line.py`) and does NOT close the class that produced the three genuine END-less logs.
Also confirmed by the same run: the reviewer's reading of the crash offset was right — W1 and W2 both PASS,
so `wait_logs.py` under `PYTHONIOENCODING=cp949` on an em-dash line exits 0 and prints DONE.
NOT acted on, referred to judgement (material sessions do not take design decisions): (a) the fleet-wide
encoding fix `PYTHONIOENCODING=utf-8:replace` in `bgrun.py`'s `child_env`, which the reviewer shows would
replace ten pasted per-file `reconfigure` calls — it changes every child process's behaviour and is outside the
brief's named repair; (b) whether the external-kill class is worth a mechanism at all (an external kill is what
`--detach` already exists for) or whether the docstring's "Always" should simply be narrowed to what the code
can guarantee; (c) the reviewer's observation that `wait_logs._p()` is dead code while the reconfigure stands.
