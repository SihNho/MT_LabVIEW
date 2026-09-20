# stall-waitlogs-c37

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.1519  in 20 / out 35493 / cache-create 170098 / cache-read 1033623  (484s, 22 turn(s))
- **date:** 2026-09-18 23:50:12
- **outcome:** ANSWERED (485s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim. It is the explanation this project formed for a recurring-error record, and the record is
now gating a build, so if the explanation is wrong the gate is protecting something real.

## The claim under attack

`tools/bench/stall_pid18476_232310.log` is a FALSE POSITIVE of the stall watchdog, of the same class as the
cycle-35 record: the "stalled" process was the session's OWN waiter, `tools/wait_logs.py --seconds 1020`, whose
entire job is to sleep until another bgrun log reaches its terminal line. Zero CPU and a job log untouched for
175 s are that waiter working correctly, not a stall. Therefore nothing about the LabVIEW build path is
implicated, and the next D1 build (`tools/recipes/build_d1_routeb_v2.py`, route B run 5) may launch.

## The machine record, verbatim

* `tools/bench/stall_pid18476_232310.log:1`
  `STALL: 2026-09-18 23:26:05 pid 18476 alive 175s, job log tools/bench/wait_priorart_run5.log last written 175s,
  CPU +0.00s in the last 65s`
* same file, line 2: `dialog: no modal dialog - LabVIEW busy or two clients contending`
* same file, line 3: `cmd pid 18476 (started 20260918232310): ...python.exe -u tools/wait_logs.py --seconds 1020
  tools/bench/priorart_routeb_run5.log`
* the watched job finished successfully and so did the waiter:
  `tools/bench/wait_priorart_run5.log` last three lines —
  `DONE priorart_routeb_run5.log | BGRUN END rc=0 after 420s` / `WAITED 1/1 logs terminal` /
  `BGRUN END rc=0 after 331s`.
* the job being waited on, `tools/bench/priorart_routeb_run5.log`, ended `BGRUN END rc=0 after 420s`.

## Already ruled out (do not spend your answer here)

1. "LabVIEW was hung": no LabVIEW work was running in that window at all — the dispatch was a prior-art peer
   review (a `claude -p` cell), and the watchdog's own line 2 says no modal dialog was found.
2. "The waiter never terminated": it did, `BGRUN END rc=0 after 331s`, inside its own deadline.
3. "The watchdog has no identity binding": cycle 36 already bound `lv_stallcheck.ps1` to `(pid, CreationDate)`
   and made it skip leaves with no bgrun log (`tools/bench/repair_c36_selftest.log`, 5/0) — and it STILL fired
   here, so that repair is not the answer.

## What I want from you

1. The strongest reason the claim is WRONG — in particular, any reading under which a zero-CPU
   `wait_logs.py` with a 175 s-old job log is a REAL failure signal that should stop the next build.
2. An alternative explanation of the same three log lines.
3. What would falsify the "false positive" claim, stated as an observation someone could make.
4. The cheapest discriminating test between your alternative and the claim.
5. Separately: is a watchdog that fires on a process whose ONLY function is to sleep a defect in the watchdog's
   liveness predicate, and if so, what is the minimal predicate that keeps its real coverage (a dead or wedged
   LabVIEW client) while not firing on a waiter? Answer only from what the record above supports.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled for this role — correct for a read-only reviewer — so the review below is the deliverable in full. (`archive/peer/2026-09-18-stall-liveness-class-c36.md:117-120` records that only a reviewer's final message is captured, so nothing here is deferred to a file.)

---

# The claim's narrow factual core survives. Its inference and its conclusion do not.

## 1. Strongest reason the claim is WRONG

**It is not a diagnosis. It is the third purchase of a diagnosis this project already owns, and the record it excuses is the receipt for a repair that was specified, unblocked, and then not built.**

`archive/peer/2026-09-18-stall-liveness-class-c36.md` — ANSWERED 21:12:53, **$3.1587, 507 s**, i.e. **2 h 14 min before** the record under attack — already returned every part of the present claim and went further:

- `:92` — *"repair 2's own motivating example had a bgrun ancestor, so the repair does not touch the case its comment cites."* That is the claim's item 3 ("that repair is not the answer"), already paid for, with the mechanism attached instead of a shrug.
- `:94` — the fix *"is not in the watchdog"*: (1) a `try/finally` around `bgrun.main()`, then (2) **"letting `guard_peer.py` retract a stall record whose named job later ends `BGRUN END rc=0` — outcome instead of snapshot."**
- `:112-115` — both left undecided, handed to the judgement session.

Repair (1) **was built**: `tools/bgrun.py:11` (*"'Always' has had a MECHANISM only since 2026-09-18"*), `:259-275`. So the c36 reviewer's stated precondition — *"(2) is unsound until (1) is done"* — was already satisfied by 23:26. Repair (2) was the one thing missing, and it is exactly what makes this record vanish at zero cost:

| record | job log it names | that log's terminal line | retraction rule (2) |
|---|---|---|---|
| `stall_pid18476_232310.log` (23:26) | `wait_priorart_run5.log` | `BGRUN END rc=0 after 331s` (`:4`) | **retracted automatically** |
| `stall_pid11424_221324.log` (22:26) | `build_d1_routeb_v1_run4.log` | `BGRUN END rc=1 after 1713s` (`:354`) | **stands — correctly** |

The rule discriminates perfectly on the only two records the repaired predicate has ever produced. The claim asks to spend a fourth review excusing one instance of a class whose mechanical retraction was designed, priced, unblocked and shelved — and whose next occurrence is scheduled by the next long `bgrun` wait. **"Run 5 may launch" *is* the failed prediction repeating**: cycle 36 also concluded the class was handled, and 2 h 14 min later it was not. CLAUDE.md's own `repeated-failure-class` rule and "the second time a class of failure is explained by inference rather than read from the machine, the next build is the READER" both point at the repair, not the build.

### "Same class as the cycle-35 record" is false as stated

- **The measurements are not the same measurement.** `stall_pid11536_193335.log:1` says `log stale` — the hard-coded literal that `lv_stallcheck.ps1:142-144` admits *"asserted a log check that had never run"* — and `:3` carries no `(started …)` binding. `stall_pid18476_232310.log:1` carries a *measured* age and a bound command line. "Same class" here compares a number to a literal.
- **The cycle-35 premise was already refuted:** `…c36.md:53-55` — pid 11536 *was* the bgrun child of `wait_runner_exit.log` (START 19:33:35, ends `BGRUN END rc=0 after 4022s`), *"so the ancestor walk DID find a job log."* Cycle 36's repair 2 targeted a condition the cycle-35 case does not satisfy.
- **Census.** Of 9 `stall_pid*.log` records, 3 (2026-09-14) use a retired lifetime-CPU predicate, and the newest — `stall_pid11424_221324.log:3`, `python.exe -u tools/recipes/build_d1_routeb_v1.py` — is a **real recipe client on the D1 route-B path**, one hour earlier, with the identical `CPU +0.00s` signature. Waiters are the minority, not the class.

### The one reading under which it IS a real failure signal

`tools/wait_logs.py:3-8`: the waiter exists because `material.md`'s prescribed shell-loop wait is **denied by the permission layer**, and `Monitor` is denied too. So at 23:23:10 the session spent a **second bgrun slot and an 18-minute deadline** on a process whose entire output echoes a line already in another file — the shape CLAUDE.md §3 forbids ("one batch = one runner = one notification"). The predicate "a leaf under bgrun, alive, silent, burning nothing" is a *correct* detector of that. Wrong is the label ("STALLED LabVIEW client") and the consequence (block the build), not the detection.

And the limit, stated plainly: **at 23:26:05 a healthy waiter and a wedged waiter are identical in every quantity the watchdog reads.** The fact that settles it — `BGRUN END rc=0 after 331s` — did not exist yet. "This was a false positive" is a retrospective reading of information unavailable at the moment of the alert.

## 2. Alternative explanations of the same three lines

**A — `CPU +0.00s` is not evidence of anything, so it cannot be evidence *for* the claim.** `wait_logs.py:80-94` polls at 1 Hz: ~65 sub-millisecond bursts in the window. Windows charges process CPU at the ~15.625 ms tick quantum, and `GetProcessTimes` returns 0 for short executions — "short bursts of execution may not register within the timer tick interval". Expected charge ≈ 0.02 s, **below `$IdleCpuDelta = 0.05`** (`lv_stallcheck.ps1:31`). A waiter polling correctly and a waiter dead in a blocking read produce the *same* `+0.00`. The claim reads that number as corroboration; it corroborates neither story.

**B — the cause is the permission configuration, not the watchdog and not LabVIEW.** The waiter process exists only because two sanctioned ways to wait are denied (`wait_logs.py:3-8`). Lift the denial and the process — and every record of this shape — disappears. Same three lines, different cause, and neither a watchdog repair nor a peer review touches it.

## 3. What would falsify the "false positive" claim

- **F-a.** A `stall_pid*.log` naming a `wait_logs.py` leaf whose named job log never reaches a terminal line, or ends `BGRUN TIMEOUT`.
- **F-b.** A flagged waiter whose **watched** log was *also* stale at the stall instant — sleeping on a job already dead; that alert is a true positive about the watched job. Today's record cannot be checked for this: it names the waiter's own log and never the log being waited on — itself a defect in the record.
- **F-c.** Evidence that pid 11536 had **no** bgrun ancestor. Already resolved against the claim (`…c36.md:53-55`).

## 4. Cheapest discriminating test

**One pass over the 9 existing records — seconds, no LabVIEW, no build, no dispatch:** for each `stall_pid*.log`, resolve the job log it names and read that log's terminal line. Three buckets: `BGRUN END rc=0` (retractable by outcome), `rc≠0`/`TIMEOUT` (true positive), no terminal line (unresolved). That table separates the claim ("waiters are always bucket 1") from Alternative A ("the CPU term carries no information, so bucket membership is uncorrelated with it") — and it *is* the input the deferred `guard_peer.py` retraction needs. Cheaper than the review it replaces, and it yields a rule instead of an excuse.

Narrower, ~70 s, if only Alternative A matters: run `wait_logs.py --seconds 70` under bgrun on a log that never goes terminal and read `(Get-Process -Id <pid>).CPU` twice, 65 s apart. `+0.00` while the loop demonstrably iterates proves the watchdog's second conjunct is uninformative for python leaves.

## 5. Is the liveness predicate defective — and the minimal repair

**Yes, but not for "it fires on a process whose only job is to sleep."** Three defects, two of which the file states about itself:

1. **It reads liveness from the wrong file.** `lv_stallcheck.ps1:132` binds progress to the ancestor's `bgrun --log`. For a client that is where progress appears; for a waiter it is where progress *never* appears (`wait_logs.py:96-103` prints only after the loop). The live file — the watched log — sits on the leaf's own bound command line and is printed on line 3 of the record. The watchdog had the live file's name in hand and measured the dead one.
2. **Snapshot where the question is an outcome** (`…c36.md:94`).
3. **It never tests whether the leaf can reach LabVIEW at all** — `lv_stallcheck.ps1:138-139`, its own words. And `guard_bash.py:198`'s `LABVIEW_RE` cannot be borrowed for this: it matches *any* `py tools/*.py`, `wait_logs.py` included.

**Minimal predicate, as a repair of an existing device** (no new device — CLAUDE.md / STATUS.md line 10, *"장치는 더 만들지 말고 계속 진행"*): add one clause to the freshness skip at `lv_stallcheck.ps1:150-153` — *flag only if **every** log path on the leaf's own bound command line is also stale beyond `$LogFreshSeconds`, not just the ancestor's `bgrun --log`* — then finish repair (2) so the record is provisional.

Coverage is preserved, checkably: `stall_pid11424_221324.log:3` names no other log on its command line, so the clause is vacuous for it and the real build client is still flagged exactly as today. A waiter is skipped while the log it watches grows. A waiter sleeping on a genuinely dead job still fires, because then both logs are stale. One clause, reading a string the record already prints. **What it would still get wrong:** a client that hangs while an unrelated log on its command line keeps growing, and any client whose work is invisible to both log-age and tick-quantised CPU.

## What I concede, and what would change my mind

Conceded: pid 18476 was the waiter, it terminated normally, no LabVIEW work was in flight, and this record does not implicate the D1 build path. What does not follow is "therefore run 5 may launch."

**Changed by:** the 9-record table coming back with `wait_logs.py`-class leaves in the "no terminal line" bucket — making waiters a genuine failure class rather than a labelling problem — or a decision record showing repair (2) was considered *after* `bgrun.py`'s `try/finally` landed and rejected on stated grounds, in which case the claim is deliberate policy rather than omission.

**Sources:** [GetProcessTimes — MS Learn](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes) · [TotalProcessorTime / clock-tick interval — MS Q&A](https://learn.microsoft.com/en-us/answers/questions/1183193/totalprocessortime-differs-between-windows-10-and) · [Process.TotalProcessorTime — MS Learn](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.process.totalprocessortime?view=net-7.0)

**Local:** `tools/bench/stall_pid18476_232310.log`, `…/stall_pid11424_221324.log`, `…/stall_pid11536_193335.log`, `…/wait_priorart_run5.log:4`, `…/build_d1_routeb_v1_run4.log:354`, `tools/wait_logs.py:3-8,80-103`, `tools/lv_stallcheck.ps1:31,132,138-144,150-153`, `tools/bgrun.py:11,259-275`, `tools/hooks/guard_bash.py:198`, `tools/hooks/guard_peer.py:73,85-117`, `archive/peer/2026-09-18-stall-liveness-class-c36.md:53-55,92-94,112-115`.

## Sources

(extract from answer)

## What was done with it

Dispatched by the cycle-37 MATERIAL session because `guard_peer` held the D1 run-5 build on
`tools/bench/stall_pid18476_232310.log`. Outcome ANSWERED (485 s, $3.1519, `tools/bench/peer_stall_waitlogs_c37.log`),
so the gate lifted and **run 5 launched at 23:56** (`tools/bench/build_d1_routeb_v2_run5.log`, `BGRUN END rc=1 after
1668s`).

MATERIAL disposition — what is RECORDED, not decided here (the repair is a judgement call):

- The arm the peer attacks is **conceded in one direction**: at 23:26:05 every quantity the watchdog reads was
  identical for a healthy and a wedged waiter (`:106`), so the record was not *wrong when written*; "false
  positive" is a reading taken after `BGRUN END rc=0 after 331s` existed.
- Its named defects are about `lv_stallcheck.ps1`, not about the waiter: liveness is read from the ANCESTOR's
  `bgrun --log` (`:1`) while the live file — the watched log — is on the leaf's own command line and is already
  printed on line 3 of every record; the record is a SNAPSHOT where the question is an OUTCOME (`:2`); and the
  leaf is never tested for being able to reach LabVIEW at all (`:3`).
- Proposed minimal repair, a REPAIR OF AN EXISTING DEVICE (no new device, per the user's 2026-09-18 08:53 order):
  one clause at `tools/lv_stallcheck.ps1:150-153` — flag only if EVERY log path on the leaf's own bound command
  line is stale beyond `$LogFreshSeconds`. **NOT BUILT in this session** (the brief authorised the run, not a
  watchdog change); carried to judgement.
- ⚠️ Observed the same night: a THIRD record of this class, `tools/bench/stall_pid3792_235020.log:1`, fired at
  00:00:36 on run 5's OWN build client (pid 3792, 357 s of log silence during a long `report_all` pass) while that
  client was alive and still working — the coverage case the clause above deliberately keeps firing.

(Claude fills in)
