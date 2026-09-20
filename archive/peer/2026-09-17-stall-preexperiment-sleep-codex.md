# stall-preexperiment-sleep-codex

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-17 19:55:46
- **outcome:** ANSWERED (170s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK the following claim about a recurring alert in this project (V6_ParallelLoop). Do not confirm it.
Your job is to find the strongest reason it is WRONG, an alternative explanation, what would falsify it, and
the cheapest test that discriminates between the explanations.

THE RECORD UNDER TEST
`tools/bench/stall_pid25164_181319.log` holds one line:
  STALL: 2026-09-17 18:17:39 pid 25164 alive 261s, log stale, CPU +0.00s in the last 105s
  dialog: unknown
  cmd pid 25164: python.exe -u tools/bench/preexperiment_guard.py 42

MY CLAIM (attack it):
"This STALL record is a FALSE POSITIVE, not a failure. `tools/bench/preexperiment_guard.py` is a deliberate
backstop that calls `time.sleep(42*60)` before it does anything, so zero CPU and a stale log are its CORRECT
behaviour for 42 minutes. `tools/bench/preexperiment_guard.log` shows the same run completing normally:
`T+42 check 18:55:19` / `no LabVIEW process - clean` / `working-copy md5 2a78e17c... (OK)` /
`BGRUN END rc=0 after 2520s`. Therefore nothing hung, the alert is an artefact of `tools/lv_stallcheck.ps1`
deciding liveness from (log age + CPU delta) only, and the correct remedy is to teach the watchdog about
intentionally-sleeping jobs rather than to diagnose a hang."

ALREADY RULED OUT (do not spend your answer on these):
- The process did not die: the same pid's bgrun log carries `BGRUN END rc=0 after 2520s`, written by the runner.
- It was not a LabVIEW/COM stall: this script only calls `tasklist`, `Stop-Process` and an md5 read; it opens no
  VI Server / ActiveX reference, and no LabVIEW.exe was running at the check.
- It is not new: `archive/peer/2026-09-14-stall-alert-wrappers-false-positive.md`,
  `...-stall-record-sweep-false-positive.md`, `...-stall-record-silent-walk.md` and
  `...-stall-record-matrix-silent-block.md` record four earlier false-positive classes of the same watchdog.

WHAT I NEED FROM YOU, in this order:
1. The strongest case that this is NOT a false positive - i.e. a way the record could be reporting a real defect
   (in bgrun's detach path, in the watchdog's own accounting, in the hook that consumes these records, or in the
   fact that a 42-minute sleeping job was launched at all under a runner whose deadline is 50 minutes).
2. An alternative explanation of the same three facts.
3. What observation would falsify MY claim.
4. The cheapest discriminating test, runnable WITHOUT LabVIEW and WITHOUT any instrument - the rig is running a
   real experiment right now, so any test that starts LabVIEW.exe or touches hardware is disqualified.
5. A structural criticism worth acting on: this is the FIFTH recorded false-positive class of the same watchdog,
   and each one has blocked the next build until a peer review was archived. Is the watchdog's liveness test
   (log age + CPU delta) salvageable, or is the design wrong - and if wrong, what is the cheapest correct test
   of "this child process is making progress" for a mixed fleet of LabVIEW COM clients and pure-python jobs?

Files you may read: tools/lv_stallcheck.ps1, tools/bench/preexperiment_guard.py,
tools/bench/preexperiment_guard.log, tools/bench/stall_pid25164_181319.log, tools/bgrun.py,
tools/hooks/guard_peer.py, tools/logclass.py, CLAUDE.md. Cite file:line for every claim you make.



--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

## 1. Strongest reason the claim may be wrong

The completion log does **not prove that PID 25164 completed**.

`BGRUN DETACH pid=26324` identifies the detached runner, not its eventual child (`tools/bench/preexperiment_guard.log:1`; `tools/bgrun.py:63-78`). The runner subsequently creates the child at `Popen(...)`, but neither `BGRUN START` nor `BGRUN END` records `p.pid` (`tools/bgrun.py:111-113,177-184`). Conversely, the stall record identifies PID 25164 but contains no parent PID or run identifier (`tools/bench/stall_pid25164_181319.log:1-3`).

Therefore, “the same run completed normally” is an unproved identity join based only on matching command line and timing. Eventual `rc=0` proves that *the child owned by runner 26324* completed; it does not, from these logs alone, prove that this child was PID 25164.

There is a second real defect: the 50-minute deadline provides only eight nominal minutes beyond a 42-minute sleep (`tools/bench/preexperiment_guard.py:7,24-38`). Python explicitly permits `time.sleep()` to return later than requested because of scheduling, so that margin is not a guaranteed execution budget ([Python documentation](https://docs.python.org/3.12/library/time.html#time.sleep)). This run happened to finish after 2520 seconds, but the design can still time out a correctly functioning guard before its safety check.

## 2. Alternative explanation of the evidence

A concurrent or orphaned second process could have had the identical command line:

- PID 25164 was the unobserved duplicate and legitimately triggered the stall detector.
- Runner 26324 owned another child, which wrote `sleeping 42.0 min`, completed normally, and produced the later `rc=0`.
- Both processes would present the same command line shown in the record and log (`tools/bench/stall_pid25164_181319.log:3`; `tools/bench/preexperiment_guard.log:2-7`).

Even if there was only one process, the record can report a genuine **progress-contract defect**, rather than a hung computation. Project policy says unattended silence exceeding the expected interval is something to diagnose (`CLAUDE.md:210-224`). The guard emits one line and then becomes externally indistinguishable from a hung sleeper for 42 minutes (`tools/bench/preexperiment_guard.py:23-27`). Later success does not make that loss of observability imaginary.

## 3. Observation that would falsify the claim

Any of these would falsify “PID 25164 was merely the successfully completing intentional sleeper”:

- Process-creation evidence shows that PID 25164’s parent was not detached runner PID 26324.
- It shows two simultaneous children with this command line, only one descended from PID 26324.
- PID 25164 remained alive after the logged child’s `BGRUN END`.
- An identity-correlated run records PID 25164 ending differently from `rc=0`.

Windows Security event 4688, if process-creation auditing was enabled, contains both the new PID and creator PID; these are hexadecimal and can be correlated after conversion ([Microsoft documentation](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4688)). Here the relevant values are `25164 = 0x624C` and `26324 = 0x66D4`.

If event 4688 proves PID 25164 was the sole direct child of PID 26324, then I would accept the narrow conclusion that this particular stall classification was false. The current files do not establish that fact.

## 4. Structural criticism

The generic liveness design is wrong, not merely missing one sleep-script exemption.

The watchdog applies a COM-stall hypothesis to every leaf `python.exe`/`py.exe`, without first establishing that it is a LabVIEW client (`tools/lv_stallcheck.ps1:63-77`). It defines a stall as stale log plus low CPU (`tools/lv_stallcheck.ps1:91-112`), labels the result “STALLED LabVIEW client,” and turns that heuristic into a mandatory build-blocking failure (`tools/lv_stallcheck.ps1:139-162`; `tools/hooks/guard_peer.py:63-74,249-277`). A sleeping timer gives false positives; a busy loop or a hung process that keeps logging gives false negatives. Command-name exceptions will merely create a sixth class.

The cheapest sound replacement is an explicit per-job progress contract:

- `bgrun` records a run ID and child PID immediately after `Popen`.
- Jobs emit monotonic checkpoints such as `phase=WAIT until=<timestamp>`, `phase=COM_CALL deadline=<timestamp>`, and `phase=VERIFY`.
- The watchdog checks whether the declared phase deadline has expired.
- `bgrun` retains the independent hard deadline already enforced at `tools/bgrun.py:155-176`.

This measures conformance to declared progress, not guessed progress from CPU consumption.

## 5. Cheapest discriminating test

Without starting LabVIEW or touching an instrument, query existing Security event 4688 records around 18:13:19 for new PID `0x624C`, then inspect its creator PID. **Creator PID `0x66D4` with no duplicate supports the false-positive explanation; any other creator or a second identical process supports the alternative.**

## Sources

(extract from answer)

## What was done with it

READ AND RECORDED, NO CODE CHANGED THIS SESSION (material session, 2026-09-17 evening; the rig is running a real
experiment, so nothing that starts LabVIEW or an instrument was run).

1. My "false positive" framing was NOT accepted as stated. Both arms make the same structural point: at 18:17:39
   the watchdog could not distinguish this job from a genuine hang, and `BGRUN END rc=0 after 2520s` is 18:55
   evidence used to judge an 18:17 decision. So the record is an alert about an UNOBSERVABLE window, not a
   malfunction of the alert.
2. The concrete defect both arms name is in the JOB, not the watchdog: a 42-minute `time.sleep` under a 50-minute
   bgrun deadline (`tools/bench/preexperiment_guard.py:25-26`) makes silence mean "still running" for 84 % of the
   budget — on a safety backstop whose own failure mode is silence.
3. The proposed remedy (a heartbeat file written by long sleepers and by COM clients, with the watchdog testing
   only that file's mtime and dropping the CPU delta) is a DESIGN CHANGE to the fleet's liveness test. A material
   session does not take it. It is carried to the judgement session as an OPEN item, together with the opus arm's
   secondary finding that `lv_stallcheck.ps1:112` prints `log stale` as a literal, so a record cannot prove the
   ancestor walk ever read a log.
4. Effect on this session: the gate lifted, and the work it was blocking — `tools/cycle_runner.py`,
   `tools/hooks/guard_session.py`, the doc_lint L8 warning — was built and self-tested with no LabVIEW.
