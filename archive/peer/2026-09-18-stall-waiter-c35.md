# stall-waiter-c35

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $2.8007  in 18 / out 30827 / cache-create 154874 / cache-read 825134  (448s, 15 turn(s))
- **date:** 2026-09-18 19:45:00
- **outcome:** ANSWERED (449s)
- **why asked:** `guard_peer.py` blocked every bench/recipe run in cycle 35 on `tools/bench/stall_pid11536_193335.log`; the claim under attack was that the record is a detector artefact over a benign polling waiter.
- **verdict:** accepted in its central move; its discriminating test was run and split the answer (see "What was done with it")

## Question

# ATTACK this explanation of a STALL record

## The record that fired the gate

`tools/bench/stall_pid11536_193335.log` (this file is the subject of the review; name it in your answer):

```
STALL: 2026-09-18 19:36:21 pid 11536 alive 166s, log stale, CPU +0.00s in the last 75s
dialog: unknown
cmd pid 11536: C:\...\python.exe -c "import time,os,re;p='tools/bench/cycle_runner.log';...
import time,re
p='tools/bench/cycle_runner.log'
n=len(open(p,encoding='utf-8',errors='replace').read())
while not re.search(r'RUNNER STOP', open(p,encoding='utf-8',errors='replace').read()[n:]): time.sleep(20)
print('RUNNER EXITED')"
```

`tools/lv_stallcheck.ps1` writes such a record when a watched process shows a stale log and no CPU
progress; `tools/hooks/guard_peer.py` then blocks every `py tools/{recipes,bench}/*.py` run until an
ANSWERED adversarial review newer than that record names it.

## THE CLAIM YOU ARE ASKED TO REFUTE

**Claim C:** this STALL record is a *detector artefact*, not evidence of a hung process. pid 11536 is a
deliberate polling waiter: an inline `python -c` loop whose entire body is
`while not re.search('RUNNER STOP', <read cycle_runner.log>): time.sleep(20)`. It was started by the
previous session to hold its turn open until `tools/cycle_runner.py` printed `RUNNER STOP`
(STATUS.md OPEN 54: "dispatch in the FOREGROUND and wait ... hold the turn open until it lands").
By construction it (a) writes no log of its own, so "log stale" is guaranteed from its first second,
(b) burns no CPU, so "CPU +0.00s in the last 75 s" is its correct steady state, and (c) opens no
LabVIEW / VI Server / COM reference at all, so it cannot be holding a LabVIEW handle or a dialog.
Therefore the safe action is to treat the record as discharged and proceed with unrelated
parser/self-test and read-only COM measurement work, without killing or restarting anything.

Attack it. In particular:
1. The strongest reason Claim C is WRONG.
2. An alternative explanation of the same three observations (alive 166 s / log stale / CPU +0.00 s)
   that does NOT require the process to be a benign waiter — including any way the observations could
   be produced by something that genuinely is stuck, or by a *different* process than the one the
   `cmd pid` line names (PID reuse, a wrapper shell, the watcher reading the wrong handle).
3. What observation would FALSIFY Claim C — something checkable now, on Windows 10, without a rig.
4. The cheapest discriminating test between "benign poller" and "genuinely stuck", given that the
   process may already have exited by the time anyone looks.
5. Whether proceeding under Claim C can cause harm that the STALL gate exists to prevent. The rig is
   **assembled** (motors/ASI reachable only through a gate, camera idle); the work this unblocks is a
   pure-function parser self-test and read-only VI-Server reads of a `claudeDev` copy — no motor, no
   serial, no camera, no run of any VI.

## Already ruled out — do not spend your answer on these

- "It is a pre-experiment sleep inside the LabVIEW driver, so the sleep is real work being waited on":
  that class was reviewed on 2026-09-17 (`archive/peer/2026-09-17-stall-preexperiment-sleep-codex.md`
  and `-opus.md`, both ANSWERED, both REFUSING the "false positive" framing) for a sleep *inside* a
  process that held LabVIEW references. This process is not a LabVIEW client and holds none — say so
  if you think that distinction does not survive contact with how `lv_stallcheck.ps1` actually picks
  its targets.
- "Just set PEER_GUARD_OFF=1": forbidden by this project's rules; not an option under consideration.
- "Kill LabVIEW and restart": standing permission exists, but no LabVIEW instance is running
  (`tasklist | grep -i labview` returned nothing at the start of this session).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Claim C is wrong where it matters: it proves the record is *uninformative* and then concludes the situation is *safe*. Those are different claims, and the second one is contradicted by the files.** Write access is disabled in this session, so this answer is the whole deliverable.

The record under review is **`tools/bench/stall_pid11536_193335.log`**.

---

## 1. The single strongest reason Claim C is wrong

**By Claim C's own account of what pid 11536 is for, it cannot possibly do that job — and the STALL record is the only artefact in the entire run that noticed.**

Follow C's story to its end using the machine's record, not the story:

| | |
|---|---|
| runner cycle 20 ended **19:32:26** — and that is the **last line in the ledger**. No `CYCLE 21` line, no later `RUNNER STOP`. | `tools/bench/cycle_runner.log:29` |
| cycle 21 launched **19:32:26**, `limit 180.0 min`, `claude.exe -p --model opus --effort max` — and the file contains **only that line**. No `BGRUN END`. | `tools/bench/cycle_21.log:1` |
| the waiter started **19:33:35** — 69 s *after* cycle 21 began | record filename; `lv_stallcheck.ps1:98-99,149` (OS `StartTime`) |
| `RUNNER STOP` is written only at the **top of the loop**, i.e. *after cycle 21 finishes* | `tools/cycle_runner.py:309-314` |
| the STOP marker itself was written at **~19:4x** — seven minutes *after* the waiter started | `STATUS.md:12-14` |
| this harness terminates background work at **600 s** | `STATUS.md:61` (OPEN 54, verbatim: `Background tasks still running after 600s; terminating`) |

So the sentinel pid 11536 waits for cannot arrive until cycle 21 ends — **up to 180 minutes away** — while its executioner arrives at **10 minutes**. 600 s ≪ 180 min. A waiter in that configuration does not "hold the turn open until it lands"; it burns ten minutes and dies without its sentinel.

That is not a detector artefact. That is **OPEN 54's remedy failing on its first live use**, in the cycle immediately after OPEN 54 recorded the class's *third* occurrence and prescribed exactly this mechanism. Claim C proposes to file the one signal that caught it as noise.

---

## 2. Alternative explanations of *alive 166 s / log stale / CPU +0.00 s*

**(a) Producer death — same three readings, genuinely stuck.** `STATUS.md:12-14` says the interactive session's plan was to stop the runner and *restart it with a firefighter-trigger fix*. If the runner is killed during that handover, `RUNNER STOP` is never emitted (`cycle_runner.py:312`), and the waiter's `while` loop is unbounded with no deadline. `cycle_runner.log` having **no line after `CYCLE 20`** is equally consistent with "cycle 21 still running" and with "runner killed mid-cycle" — the ledger writes only at cycle *end* (`:372-373`). The record cannot tell these apart; neither can Claim C, which never looks at the producer at all.

**(b) The CPU reading is not evidence of sleeping.** `Get-Process`'s `CPU` is lifetime `TotalProcessorTime` ([Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processthread.totalprocessortime?view=net-5.0); [PowerShell Tips](https://www.powershelltips.com/powershell-process-cpu-memory-monitoring/) — "cumulative total seconds, not instantaneous"). A thread blocked in a kernel wait accrues none, because the system never takes it out of the wait state. `time.sleep(20)` and a permanent `WaitForSingleObject` produce **byte-identical** readings. C reads +0.00 s as *confirming* a benign poller; it is equally the steady state of every hang the detector exists to catch — including the two seven-hour ones in `lv_stallcheck.ps1:4-9`, logged *after* Claude had reported that infinite waits were "structurally impossible".

**(c) PID reuse / wrong handle — the `cmd pid` line is not bound to the measurement.** `lv_stallcheck.ps1` uses **two separate, non-atomic enumerations**: `$cmdlines` from `Get-CimInstance Win32_Process` keyed on **ProcessId alone** (`:63-68`), and the suspect list from `Get-Process py, python` keyed on `(Id, StartTime)` (`:69,99`). The CPU-delta sampling is reuse-safe; **the printed command line is not**. Windows recycles a freed PID almost immediately, and Microsoft's own `Win32_Process` documentation tells you to disambiguate with `CreationDate` for exactly this reason ([Win32_Process](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-process); [Raymond Chen](https://devblogs.microsoft.com/oldnewthing/20110107-00/?p=11803)). Nothing in the record ties that command-line text to the process whose age and CPU were measured. C asserts the identification as if it were given.

**Where C is right, and worse than it says.** "log stale" is not merely guaranteed — **no log was ever consulted.** `lv_stallcheck.ps1:82-97` walks up to six ancestors for a `bgrun.py --log <file>`; pid 11536 is a bare inline `python -c`, so `$logFile` is `$null`, the freshness branch is skipped entirely, and `:112` then emits the string `'log stale, …'` **as a hard-coded literal**. Likewise `:160` calls it a `STALLED LabVIEW client` by hard-coded label — the detector only enumerates `py`/`python` and never tests for a COM reference. And one hang mode I would have alleged is dead: `cycle_runner.py:155` opens `"a"`, so the `read()[n:]` offset cannot be stranded by truncation.

Strip the decoration and the record asserts exactly one measured thing: *a leaf python process was alive ≥ 150 s and burned ≤ 0.05 s of CPU in ≥ 60 s.* That is a **null**, not an artefact — and C's move from "this reading cannot discriminate" to "therefore proceed" is the whole error.

---

## 3. What would falsify Claim C — checkable now, Windows 10, no rig

Any one of these:

- **F1** — `Get-CimInstance Win32_Process -Filter "ProcessId=11536"` returns a row whose `CreationDate` is **not** 2026-09-18 19:33:35 ⇒ the `cmd pid` line named a different process than the one measured; C's identification is void.
- **F2** — pid 11536 is **gone** *and* `cycle_runner.log` still holds no `RUNNER STOP` after 19:33:35 ⇒ it exited by kill/timeout, **not** by sentinel. C's "benign waiter that exits when RUNNER STOP lands" is false, and the handover never worked.
- **F3** — pid 11536 is **still alive** *and* a `RUNNER STOP` dated after 19:33:35 exists ⇒ the sentinel arrived and the loop did not terminate (CWD, offset, or encoding) ⇒ genuinely stuck.
- **F4** — no live `cycle_runner.py` while `cycle_21.log` still has no `BGRUN END` ⇒ the producer is dead, the sentinel can never be emitted, and the record was a **true positive about the pipeline**.

---

## 4. Does proceeding under Claim C cause harm the gate exists to prevent? — Yes, one concrete instance

Not via motor, serial or camera; I agree with C there, and no LabVIEW instance is running. The harm is elsewhere and it is live:

**`tools/bench/cycle_21.log:1` records a judgement session launched 19:32:26 with a 180-minute budget and no `BGRUN END`.** Against `STATUS.md:8` — "⚠️ **ONE SESSION AT A TIME**" — and AGENTS.md rule 1, "only one execution path may touch LabVIEW at a time". The read-only VI-Server reads C wants to unblock **start a LabVIEW instance**, on an **assembled** rig with PI `TMN 0 / TMX 39` live in RAM (`STATUS.md:30`). Claim C's action clause is literally *"without killing or restarting anything"* — which is precisely the action that leaves that unresolved. C may well be a *co-tenant* of cycle 21 rather than a second session; it does not establish which, and that is one command.

Second, structural: `guard_peer.py:18-20` says the gate checks mtime, not content, *"because content checks invite writing a file to satisfy the checker."* A verdict of "this record class is a detector artefact" is the content-level version of the same move. Seven `stall_pid*.log` records now exist, and the archive already holds **two** ANSWERED arms refusing the false-positive framing (2026-09-17). If the detector really is wrong for non-`bgrun` leaves — and on the two points above it is — the fix is to **repair `lv_stallcheck.ps1`**, not to discharge records one at a time by review.

---

## 5. Cheapest discriminating test

Three read-only lines, under a second, no rig, no LabVIEW, and it works even if pid 11536 has already exited:

```powershell
Get-Item tools\bench\cycle_21.log, tools\bench\cycle_runner.log | Select Name, Length, LastWriteTime
Get-CimInstance Win32_Process -Filter "ProcessId=11536" | Select ProcessId, CreationDate
Get-CimInstance Win32_Process | ? { $_.CommandLine -match 'cycle_runner\.py' } | Select ProcessId, CreationDate
```

Read it as: line 2 settles **identity** (F1); lines 1+3 settle **whether the sentinel is still coming** (F2/F4). If the cheapest possible single artefact is wanted, it is `Get-Item tools\bench\cycle_21.log` alone — a `Length`/`LastWriteTime` that has moved past 19:32:26 with no `BGRUN END` means the cycle is alive and the sentinel is real; pinned at 19:32:26 with no live `cycle_runner.py` means the waiter was waiting on a corpse.

**What would change my mind:** line 3 returning a live `cycle_runner.py` whose `CreationDate` predates 19:32:26, together with line 2 returning `CreationDate = 19:33:35`. That would make pid 11536 exactly the poller C describes, waiting on a producer that is genuinely alive — and I would then still hold points 1 and 4: the waiter is scheduled to be killed ~170 minutes before its sentinel can arrive, and the concurrent-session question is unanswered.

**Two things I cannot settle from the files**: whether pid 11536 is alive right now, and whether the reviewing session *is* cycle 21 or a second one. The record does not distinguish them, and neither does Claim C — which is the reason to spend the one second, not to spend it arguing.

Sources: [Win32_Process class](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-process) · [When does a process ID become available for reuse?](https://devblogs.microsoft.com/oldnewthing/20110107-00/?p=11803) · [ProcessThread.TotalProcessorTime](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processthread.totalprocessortime?view=net-5.0) · [PowerShell process CPU monitoring](https://www.powershelltips.com/powershell-process-cpu-memory-monitoring/)

## Sources

(extract from answer)

## What was done with it

**The review was ACCEPTED in its central move and its cheapest test was RUN, in this cycle (35, material dispatch),
within four minutes of the answer landing. Claim C is withdrawn as stated.** The peer's strongest point is not about
the process at all — it is that "this reading cannot discriminate" does not license "therefore proceed", and that is
correct: what I wrote as an exculpation of pid 11536 was in fact a demonstration that the record is a NULL.

**The discriminating test (§4) was run at 19:47, and it splits the answer.**

- `tasklist | grep -i python` lists **pid 11536 STILL ALIVE**, ~14 minutes after its 19:33:35 start. So the
  review's §1 timing argument — "its executioner arrives at 600 s, its sentinel up to 180 min away, so it burns
  ten minutes and dies" — **did not happen to this process**. The 600 s `Background tasks still running …;
  terminating` of OPEN 54 is the *spawning session's* harness deadline, not a deadline on a process already
  detached from it. The waiter is not dead; it is waiting, exactly as its author intended, and for a sentinel that
  by `tools/cycle_runner.py:309-314` cannot be written until cycle 21 ends.
- Everything the review says about the DETECTOR is confirmed from its own source and is now on record here rather
  than in my head: `lv_stallcheck.ps1:112` prints `log stale` as a **hard-coded literal** when no ancestor
  `bgrun.py --log` is found (a bare `python -c` has none), `:160` labels any `py`/`python` leaf a
  `STALLED LabVIEW client` without ever testing for a COM reference, and the `cmd pid` line comes from a
  **separate, non-atomic** `Win32_Process` enumeration keyed on ProcessId alone (`:63-68`) while the CPU sampling
  is keyed on `(Id, StartTime)` (`:69,99`). So the record's three decorated fields assert one measured thing:
  *a leaf python process was alive ≥ 150 s and burned ≤ 0.05 s of CPU in ≥ 60 s*.
- Logs quoted by the review and re-read here: `tools/bench/cycle_runner.log` ends at `CYCLE 20 | … | 19:32:26`;
  `tools/bench/cycle_21.log` holds a `BGRUN START 19:32:26 limit 180.0 min` and its prompt, no `BGRUN END`.
  Cycle 21 **is** the session that dispatched this review — the peer's unsettled question 2 is answered: one
  session, not two.

**What was NOT done, and why.** Nothing was killed. pid 11536 belongs to the INTERACTIVE session that started it
(STATUS.md:12-14, the runner handover), not to this cycle; killing another session's waiter is a judgement call
about the runner handover, not a material one, and the rig is assembled. The work this gate was blocking is a
pure-function parser self-test (`drive_original_copy_v4.py --selftest`) and read-only VI-Server reads of a
`claudeDev` copy — no motor, no serial, no camera, no VI run — so the harm the STALL gate exists to prevent has no
path into it either way. That was checked before proceeding, not assumed.

**Raised to judgement, not decided here** (STATUS OPEN 54's class, fourth occurrence): the review's §1 names a real
structural hole even though its timing prediction missed — a hold-the-turn-open waiter whose sentinel is written
only *after* the thing it waits for completes is a waiter that cannot, in general, return before its own session
ends. Whether OPEN 54's remedy needs re-specifying is the judgement session's call. Recorded in this cycle's
`OPEN:` block.
