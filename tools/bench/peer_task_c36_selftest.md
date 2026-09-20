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
