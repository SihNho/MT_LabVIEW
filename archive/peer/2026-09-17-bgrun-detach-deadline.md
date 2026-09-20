# bgrun-detach-deadline

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-17
- **outcome:** ANSWERED (139s)
- **why asked:** cycle 15 deliverable 1 — `bgrun.py --detach`. `guard_peer.py` blocked the next build on
  `tools/bench/detach_timeout_test.log` (a *deliberate* TIMEOUT test, but the gate is mechanical and correct to
  fire), and the claim "detached, with every guarantee intact" was about to be written into STATUS.
- **verdict:** adopted — two of its findings were real defects and are FIXED in `tools/bgrun.py`; its
  decisive test was RUN and it falsified part of the claim.

## Question

ATTACK this claim about tools/bgrun.py in this repo (read the file). CLAIM: the new --detach mode makes an unattended background run survive its caller's exit WITHOUT weakening any guarantee. Mechanism: when --detach is passed and BGRUN_DETACHED is unset, bgrun re-execs itself via subprocess.Popen with creationflags DETACHED_PROCESS|CREATE_NEW_PROCESS_GROUP|CREATE_BREAKAWAY_FROM_JOB (falling back to the same flags minus CREATE_BREAKAWAY_FROM_JOB on OSError), stdio to DEVNULL, and returns 0 immediately; the second copy does all the real work. Evidence offered: tools/bench/detach_test.log - a 40 s child launched from a shell that exited at once still produced 'BGRUN END rc=0 after 40s'; and tools/bench/detach_timeout_test.log - with --max-min 0.15 the same child produced 'BGRUN TIMEOUT killed after 10s (limit 0.15 min)', i.e. the deadline kill and the final log line still fire in the detached copy. Find the strongest reason this is WRONG or incomplete on Windows 10. Specifically: (1) can the taskkill /F /T tree kill still reach every descendant once the runner has broken away from the parent job object, or can a grandchild that creates its own job survive - how would that be detected; (2) is CREATE_BREAKAWAY_FROM_JOB silently ignored rather than raising OSError when the job lacks JOB_OBJECT_LIMIT_BREAKAWAY_OK, so that the fallback branch is dead code and the claimed breakaway never happened even though Popen reported success; (3) does DETACHED_PROCESS with DEVNULL stdio lose any failure mode that the old inherited-console runner reported, e.g. a child that writes to the console directly rather than to the pipe, or a Python crash traceback; (4) does detach_timeout_test.log actually prove the deadline kill killed the whole tree, or only that the runner printed the TIMEOUT line. Name an alternative explanation for each log line and give the cheapest discriminating test for each.

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The claim is wrong because `bgrun.py` reports successful killing without verifying that anything was killed. At [tools/bgrun.py:132](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bgrun.py:132>) it discards `taskkill`’s return code and captured diagnostics; at the next line it unconditionally writes `BGRUN TIMEOUT killed`. Python’s `subprocess.run()` does not raise on a nonzero exit unless `check=True` is used. [Python documentation](https://docs.python.org/3.10/library/subprocess.html)

### 1. The process-tree guarantee is unproved

Microsoft documents `/T` only as ending the named process and “child processes started by it”; it does not promise job-object-grade containment under races, orphaning, brokered launches, or changing topology. [Microsoft `taskkill` documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/taskkill)

A grandchild merely assigning itself to a nested job does not automatically escape: on Windows 10, a nested job remains a subset of its parent job, and terminating an ancestor job terminates child jobs too. [Microsoft nested-jobs documentation](https://learn.microsoft.com/en-us/windows/win32/procthread/nested-jobs) But `bgrun` never creates such an enclosing job. It relies on an after-the-fact `/T` traversal. A descendant can therefore escape the claimed guarantee if it becomes unreachable through the process ancestry being traversed—for example, after an intermediate process exits—or if another process/service brokers its creation.

The documented kernel mechanism for reliably destroying children and grandchildren is to put them in a runner-owned job with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`. [Microsoft’s Raymond Chen example](https://devblogs.microsoft.com/oldnewthing/20131209-00/?p=2433)

**Alternative explanation of the timeout log:** `taskkill` failed, killed only `p.pid`, or missed an orphaned/brokered descendant; the runner printed “killed” anyway.

**Falsifying observation:** any recorded descendant PID is still alive or continues writing a heartbeat after the `TIMEOUT` line.

**Cheapest test:** make the test command spawn a long-lived canary grandchild, record its PID, let the intermediate launcher exit, and have the canary append to a separate file after the timeout. Also log `taskkill.returncode`, `stdout`, and `stderr`, then query that exact PID.

### 2. Breakaway success is not established

The “silent ignore under a non-breakaway job” theory is probably wrong for a simple single job. Microsoft says the containing job must set `JOB_OBJECT_LIMIT_BREAKAWAY_OK`; otherwise the breakaway request is not permitted. [Microsoft process-creation flags](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags) `CreateProcess` failure surfaces through `Popen` as an `OSError`, so the fallback branch is plausible rather than dead.

But the fallback destroys the advertised guarantee: after an `OSError`, [tools/bgrun.py:56](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bgrun.py:56>) retries without `CREATE_BREAKAWAY_FROM_JOB`, returns 0, and leaves the new runner in the caller’s job. A kill-on-close caller can then kill it.

There are two further alternative explanations for `mode=breakaway`:

- The launcher was not in any job, so Microsoft says the flag had no effect.
- In a nested-job chain, breakaway can stop at a non-permitting ancestor; Microsoft explicitly documents partial escape through the chain. [Microsoft nested-jobs documentation](https://learn.microsoft.com/en-us/windows/win32/procthread/nested-jobs)

Thus successful `Popen` does not by itself prove escape from every kill-on-close job that matters.

**Falsifying observation:** the detached PID remains associated with the caller’s relevant job, or dies when that job’s final handle closes.

**Cheapest test:** launch it from a small controlled harness whose job has `KILL_ON_JOB_CLOSE`, test once with and once without `BREAKAWAY_OK`, close the job handle, and check the detached PID. Query job membership before closure with `IsProcessInJob`, the API Microsoft identifies for this purpose. [Microsoft job-object documentation](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)

### 3. Detachment loses runner-level diagnostics

The actual workload still has `stderr=STDOUT` and `stdout=PIPE`, so an ordinary Python traceback from that workload should reach the log. A child’s direct console output was already unreliable because the workload is launched with `CREATE_NO_WINDOW`; that is not a new detach regression. Microsoft distinguishes redirected standard handles from direct console handles such as `CONOUT$`. [Microsoft console-handle documentation](https://learn.microsoft.com/en-us/windows/console/console-handles)

What is newly lost is the detached runner’s own stderr. Its three standard streams are sent to `DEVNULL` at [tools/bgrun.py:58](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bgrun.py:58>). `DEVNULL` explicitly discards that stream. [Python documentation](https://docs.python.org/3.10/library/subprocess.html) Therefore an exception while opening the log, starting the real command, importing modules, or otherwise executing the second copy can disappear after the first copy has already returned 0. Also, Win32 process creation returns before initialization completes, so a PID alone does not prove successful initialization. [Microsoft `CreateProcess` documentation](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessa)

**Alternative explanation of `BGRUN DETACH pid=…`:** only process creation succeeded; the second Python process could fail before writing `START` or a terminal line.

**Falsifying observation:** a deliberate second-copy startup failure produces neither a log diagnostic nor an inherited-console traceback after the outer invocation returned 0.

**Cheapest test:** detach with an intentionally invalid/unwritable log target or nonexistent workload executable and check whether a durable error plus terminal line appears.

### 4. What the two logs actually prove

- `BGRUN DETACH … mode=breakaway` proves that `Popen` accepted the flags in that particular environment—not that there was a job to escape, nor that all nested jobs were escaped.
- `BGRUN END rc=0 after 40s` proves that one simple child completed and the detached runner remained alive for 40 seconds. An equally compatible explanation is that the caller had no kill-on-close job, or that some other handle kept its job alive.
- `BGRUN TIMEOUT killed…` proves only that the deadline branch ran and printed its unconditional line. It proves neither `taskkill` success nor descendant absence.
- Neither test contained a grandchild, so neither tests the advertised whole-tree guarantee.

The cheapest decisive test is the timeout-canary test: record a grandchild PID, arrange for its intermediate parent to exit, let `bgrun` time out, and check both that exact PID and a delayed heartbeat file after `BGRUN TIMEOUT`. One surviving heartbeat falsifies “kills the whole tree” immediately.

## Sources

(extract from answer)

## What was done with it

**Three of its four points were acted on the same hour; the fourth was measured and the review WON.**

1. **"`taskkill`'s result is discarded, so `BGRUN TIMEOUT killed` is written unconditionally"** — accepted; it was
   the strongest point and simply true (`subprocess.run` without `check=True`). `tools/bgrun.py` now captures
   `taskkill`'s returncode and output, re-queries the PID with `tasklist /FI "PID eq N"`, and writes a
   **`BGRUN KILL taskkill rc=… pid=… still_listed=… out=…`** line before the TIMEOUT line. A failed kill and a
   successful one no longer produce the identical log.
2. **"the detached copy's own stderr goes to DEVNULL, so a pre-START failure vanishes after the caller returned 0"**
   — accepted. `relaunch_detached` now points the detached copy's stdout+stderr at **the log file** instead of
   DEVNULL, and `out()` stops echoing in that copy so lines are not doubled. A traceback from the second copy now
   lands in the log an unattended run is actually read from.
3. **The decisive test it named ("timeout-canary: record a grandchild PID, let its intermediate parent exit, check
   for a heartbeat after the TIMEOUT line") was RUN, and it FALSIFIED the whole-tree claim.**
   `tools/bench/detach_canary.log`: runner → A → B → grandchild C (DETACHED_PROCESS), B exits at once.
   `BGRUN KILL taskkill rc=0 … still_listed=False` killed three processes and `BGRUN TIMEOUT killed after 13s` was
   written at 01:41:51 — and **C kept writing heartbeats at 01:41:57 / 01:42:05 / 01:42:13** until killed by hand.
   So "kills the whole tree" (bgrun's own docstring) is conditional on no intermediate process exiting. This is a
   **pre-existing** property of `taskkill /T`, not something `--detach` introduced, and it is now measured instead
   of assumed. Follow-up review of that failed prediction: `archive/peer/2026-09-17-bgrun-treekill-orphan.md`.
   The job-object fix the review recommends is **NOT built here**: it changes the runner's process model, it
   interacts with `CREATE_BREAKAWAY_FROM_JOB`, and it would kill a LabVIEW.exe that a workload legitimately expects
   to survive — a judgement call, left OPEN.
4. **"`mode=breakaway` proves only that `Popen` accepted the flags, not that there was a job to escape"** —
   accepted as a limit on the evidence, not repaired. STATUS now claims only what the two logs show: the caller
   returned immediately and the child ran to its END/TIMEOUT line. The mode is printed on the DETACH line so a
   `mode=detached` (breakaway refused ⇒ still inside the caller's job) can be read rather than assumed.
