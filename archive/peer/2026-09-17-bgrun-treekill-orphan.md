# bgrun-treekill-orphan

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-17
- **outcome:** ANSWERED (89s)
- **why asked:** failed prediction — bgrun's docstring says the deadline "KILLS THE WHOLE TREE", and
  `tools/bench/detach_canary.log` showed an orphaned grandchild heart-beating past `BGRUN TIMEOUT`.
- **verdict:** adopted — its logging defect is FIXED and its discriminating test (e) was RUN; the test
  **confirmed** our explanation and **rejected** its own alternative.

## Question

A PREDICTION OF OURS FAILED and I want the explanation attacked, not confirmed. Read tools/bgrun.py and tools/bench/detach_canary.log in this repo. PREDICTION: bgrun's deadline handler 'KILLS THE WHOLE TREE' (its own docstring, line 6) so nothing it launched can outlive the BGRUN TIMEOUT line. OBSERVATION: in detach_canary.log the runner launched A; A launched B; B launched grandchild C with DETACHED_PROCESS and exited immediately; at the deadline taskkill /F /T reported rc=0 and killed three processes, the runner wrote 'BGRUN TIMEOUT killed after 13s' at 01:41:51 - and C went on writing heartbeat lines at 01:41:57, 01:42:05, 01:42:13 until I killed it by hand. MY EXPLANATION, which is what you must attack: taskkill /T walks the live parent-child ancestry at kill time, B had already exited, so C was reparented/orphaned and was never in the set; therefore the 'whole tree' guarantee has always been conditional on no intermediate process exiting, and --detach did not cause it. Give me (a) the strongest reason that explanation is WRONG or incomplete - e.g. is DETACHED_PROCESS itself, rather than B's exit, what removed C from the walk; could taskkill have skipped C for a different reason (timing, access rights, a session/elevation boundary); does rc=0 mean anything at all here; (b) an alternative explanation of the same log; (c) the observation that would falsify my explanation; (d) whether assigning every launched process to a runner-owned Job Object with JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE actually closes this hole on Windows 10 given that the runner may ITSELF have been created with CREATE_BREAKAWAY_FROM_JOB, and what such a job would break for a workload that legitimately spawns LabVIEW.exe and expects it to survive - name the concrete failure; (e) the cheapest test that separates (a) from my explanation.

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The single strongest flaw is evidentiary: the log cannot show why C was omitted. `bgrun.py` discards `stderr` whenever `stdout` is nonempty, truncates the selected stream to 160 characters, checks only root PID 2644 afterward, and then writes “killed” unconditionally. Thus “C was unreachable because B exited” is not established by this run.

### (a) Strongest attack

“C was reparented” is an unsupported mechanism. Windows exposes a process’s `th32ParentProcessID` as “the identifier of the process that created this process”; Microsoft does not document Unix-style reparenting or explain how `taskkill` reconstructs trees after a creator exits. [`taskkill /T` is documented only as ending the target and child processes it started](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/taskkill); its traversal algorithm and snapshot timing are unspecified. The Toolhelp definition preserves creator identity, not a guaranteed live-parent relationship: [PROCESSENTRY32](https://learn.microsoft.com/en-us/windows/win32/api/tlhelp32/ns-tlhelp32-processentry32).

`DETACHED_PROCESS` by itself is not a credible cause: Microsoft defines it solely as preventing a console process from inheriting its parent’s console. It does not sever parentage or job membership. `CREATE_BREAKAWAY_FROM_JOB` is the distinct job-related flag. [Microsoft’s process-creation flags](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags).

`rc=0` proves only that `taskkill.exe` returned zero. Microsoft’s `taskkill` documentation gives no contract that zero means every discovered descendant was terminated. Here it is especially weak because [bgrun.py](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bgrun.py>) hides possible mixed-success diagnostics:

```python
(k.stdout or k.stderr)[:160]
```

If successes were on stdout and a C-specific error was on stderr, stderr vanished. Even stdout itself was truncated. The follow-up `tasklist` queried only PID 2644, never C.

### (b) Alternative explanation

`taskkill` may have discovered C but failed to open or terminate it because of a token, DACL, protection, or elevation difference; termination requires `PROCESS_TERMINATE`, and access is checked against the process security descriptor. [Process security and access rights](https://learn.microsoft.com/en-us/windows/win32/procthread/process-security-and-access-rights), [TerminateProcess](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-terminateprocess).

The current logging could suppress that error while retaining `rc=0` from successful termination of the other processes. That alternative is less likely if C was an ordinary same-token Python child, but this log does not exclude it. A snapshot/race bug inside `taskkill` is another possibility, but its implementation is undocumented.

### (c) Falsifying observation

Your explanation is falsified if:

- B is positively observed alive when `taskkill` begins and remains alive during enumeration;
- C’s PID and creation time prove it is the same process B created;
- C is shown as B’s child immediately before the call;
- yet C survives `/F /T`.

That would remove the missing-live-intermediate condition. Survival would then implicate access, traversal behavior, or another boundary. Conversely, DETACHED C dying while B remains alive would strongly reject “DETACHED_PROCESS alone removes it.”

### (d) Job Object fix and its concrete failure

Yes—with implementation qualifications—a runner-owned Job Object using `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` closes this particular ancestry hole on Windows 10. Job membership persists independently of whether an intermediate parent exits, children inherit membership by default, and closing the last job handle kills associated processes. Windows 8 and later support nested jobs. [Microsoft Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects).

The runner having itself escaped its caller’s job using `CREATE_BREAKAWAY_FROM_JOB` does not prevent it from creating a new job and assigning its launched root to that job. Indeed, escaping the outer job can make ownership cleaner. However:

- Create the workload suspended, assign it to the job, then resume it; otherwise it can spawn C before assignment.
- Do not enable `BREAKAWAY_OK` or `SILENT_BREAKAWAY_OK`, or descendants can escape.
- Keep the job handle non-inheritable, or an inheriting descendant can keep the “last handle” open.
- Check every job API result. `AssignProcessToJobObject` can fail for incompatible nesting/UI restrictions, and Microsoft says preventing breakaway can cause software that expects to create its own job to fail its own `AssignProcessToJobObject` call. [AssignProcessToJobObject](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject).

The concrete LabVIEW failure is not subtle: if a newly spawned `LabVIEW.exe` is in the runner’s kill-on-close job but is legitimately intended to remain running after the command finishes, closing the runner’s last job handle terminates `LabVIEW.exe`. Its UI, in-memory state, and subsequent automation endpoint disappear. If LabVIEW or a helper expects to establish an incompatible job of its own, that assignment can instead fail.

After attacking it, I still regard your live-intermediate hypothesis as the leading explanation—but “reparented” is not demonstrated, and the log cannot distinguish lost reachability from a hidden partial kill failure. Full stderr plus an explicit C liveness check would change that.

### (e) Cheapest discriminating test

Repeat the same canary with exactly one change: after spawning detached C, make B sleep past the deadline. Log full, separate `taskkill` stdout and stderr and check C’s exact PID afterward. If C dies, B’s early exit caused the hole; if C survives while B is demonstrably alive, your explanation is falsified.

## Sources

(extract from answer)

## What was done with it

**Its logging complaint was right and is fixed; its discriminating test was run and it went against it.**

1. **`(k.stdout or k.stderr)[:160]` hides a mixed-success kill** — accepted and FIXED in `tools/bgrun.py`:
   the deadline branch now writes `BGRUN KILL taskkill rc=… still_listed=…`, then **`BGRUN KILL stdout:`** and
   **`BGRUN KILL stderr:`** as two separate lines at 600 chars each. Its point that `rc=0` alone certifies nothing
   stands, and the `still_listed=` re-query was already added from the previous review.
2. **Its test (e) — "make B sleep past the deadline instead of exiting" — was RUN**:
   `tools/bench/detach_canary_balive.log`, identical canary with `canary_b_alive.py`.
   `BGRUN KILL stdout` names **`PID 5728인 프로세스(PID 23852인 자식 프로세스)가 종료되었습니다`**, i.e. the
   DETACHED grandchild C (5728) was killed **as a child of the still-live B (23852)**; `stderr` was empty;
   `heartbeat2.txt` stops at `beat=5, 01:45:19` and the TIMEOUT line is 01:45:22 — **no beat after the kill**.
   So: `taskkill /F /T` DOES reach a `DETACHED_PROCESS` grandchild while its parent is alive. That
   **rejects its own alternative** ("DETACHED_PROCESS itself removes C from the walk", and the access/DACL
   theory — same token, same result, opposite outcome) and **confirms** the live-intermediate explanation:
   the only difference between the two runs is whether B had exited.
3. **Reservation kept, not argued away**: it is right that "reparenting" is not a documented Windows mechanism
   and that the logs cannot show `taskkill`'s traversal. The claim recorded in STATUS is therefore the measured
   one — *the deadline kill misses a descendant whose intermediate parent has exited* — not a mechanism.
4. **(d) the Job Object fix is NOT built.** Its answer is the reason to leave it to judgement, not a licence to
   build: the concrete failure it names is ours — a `LabVIEW.exe` spawned inside a `KILL_ON_JOB_CLOSE` job dies
   when the runner's last handle closes, and this project's whole automation model is a LabVIEW that OUTLIVES the
   runner. Its implementation conditions (create suspended → assign → resume; no `BREAKAWAY_OK`; non-inheritable
   handle; check every job API result) are recorded here for whoever takes that decision.
