# stall-preexperiment-sleep-opus

- **agent:** claude
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.2598  in 18 / out 32596 / cache-create 199499 / cache-read 758708  (448s, 26 turn(s))
- **date:** 2026-09-17 20:03:18
- **outcome:** ANSWERED (452s)
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

Write is disabled (correct — this is a read-only peer session per AGENTS.md rule 2), so the review is the answer itself.

---

# The claim is half right and its conclusion is wrong

I concede the guard did not hang — `tools/bench/preexperiment_guard.log:7` settles that. But **"false positive", the count of five, and the proposed remedy are each refuted by this project's own records.**

## 1. Strongest reason the claim is WRONG

**The predicate that fired has a confirmed TRUE POSITIVE from the same day, 6½ hours earlier — and the claim counts it as one of the five false ones.**

The five records split into two predicates, visible in their own text:

| record | text | predicate |
|---|---|---|
| `tools/bench/stall_pid9272_105613.log:1` | `CPU 0.41s lifetime` | old |
| `tools/bench/stall_pid6164_121247.log:1` | `CPU 0.36s lifetime` | old |
| `tools/bench/stall_pid1720_141314.log:1` | `CPU 0.41s lifetime` | old |
| `tools/bench/stall_pid2832_112502.log:1` | `log stale, CPU +0.00s in the last 655s` | **current** |
| `tools/bench/stall_pid25164_181319.log:1` | `log stale, CPU +0.00s in the last 105s` | **current** |

All four archived reviews you cite are dated `2026-09-14` and attack the **old lifetime-CPU** predicate — which was deleted for exactly that reason (`tools/lv_stallcheck.ps1:103-106`). None of them touches the predicate that wrote record 5.

Record 4 — the *only* other firing of the current predicate — was a **real hang**:

- `tools/bench/build_opconnectnested_v0.log:67` — `BGRUN START 2026-09-17 11:25:02 limit 30.0 min`
- `tools/bench/stall_pid2832_112502.log:1` — `STALL: … 11:46:49 … alive 1,307s … CPU +0.00s in the last 655s`
- `tools/bench/build_opconnectnested_v0.log:130` — `COM Run did not return within 120s …`
- `tools/bench/build_opconnectnested_v0.log:134` — `BGRUN TIMEOUT killed after 1801s`
- expected runtime, same recipe: `tools/bench/build_opconnectnested_v0_run1.log:66` — `BGRUN END rc=1 after 22s`

A 22-second recipe sat 30 minutes and was tree-killed. **The watchdog named it at 11:46:49; bgrun's deadline caught it at 11:55:03 — the watchdog was 8 min 14 s earlier.** Its review (`archive/peer/2026-09-17-connectnested-stall.md:3,8` — codex, `ANSWERED`) records no false-positive finding.

The current predicate is therefore **1 true / 1 disputed, not 0/5.** "Fifth false-positive class" is a factual error, and it is the premise your whole structural argument rests on.

**Second reason:** "false positive" misstates what the alert asserts. Per its own header (`tools/lv_stallcheck.ps1:13-18`) it reports *"this looks blocked — diagnose it"*, not *"this will never finish"*. At 18:17:39, pid 25164 was from outside **bit-identical to record 4's genuine hang**. You are refuting an 18:17 decision with 18:55 evidence. And `tools/bgrun.py:7-10` states the contract the job broke: *"silence can never mean 'still running' for longer than the limit."* A 42-minute `time.sleep` under a 50-minute limit (`tools/bench/preexperiment_guard.py:7,25-26`) makes silence mean "still running" for 84 % of the budget — on a **safety backstop for a real experiment whose failure mode is silent**. Had it died at 18:20, that stall record was the only artefact in the system that would have noticed.

## 2. Alternative explanations

**A (primary).** No watchdog defect at all. Facts 1–2 are *the job's* doing: `preexperiment_guard.py:25-26` prints once then emits nothing for 42 min, so the log-freshness skip at `lv_stallcheck.ps1:91-97` had nothing to work with. Fact 3 did not exist at decision time. The record correctly reports a deliberately unobservable window in a safety-critical backstop.

**B (secondary, real).** `log stale` at `lv_stallcheck.ps1:112` is a **literal inside the format string**, not conditioned on the ancestor walk having found or read a log. Any leaf with no bgrun ancestor in 6 hops — not run under bgrun, a recycled parent PID, a walk broken by the `--detach` re-exec (`bgrun.py:36-81`) — is reported as "log stale" when no log was consulted. Here the walk probably worked (last write 18:13:19, checked 18:17:39 → 260 s > `$LogFreshSeconds`=90), but **the record cannot prove it**, and that wording is what makes record 5 look like a log-freshness failure.

## 3. What falsifies the claim

Your claim needs the signature to lack discriminating power. **Falsifier: the same signature on a job that did not complete.** It already exists — `stall_pid2832_112502.log:1` + `build_opconnectnested_v0.log:134`. Found without running anything.

**Falsifier for MY position:** if a job that *does* heartbeat is still flagged, the fix cannot live in the job and the watchdog has a genuine accounting defect.

## 4. Cheapest discriminating test — ~6 min, pure python, no LabVIEW, no instrument

```
py tools/bgrun.py --detach --max-min 6 --log tools/bench/probe_hb_silent.log -- py -u -c "import time; time.sleep(300)"
py tools/bgrun.py --detach --max-min 6 --log tools/bench/probe_hb_beat.log   -- py -u -c "import time
for i in range(10): print('hb',i,flush=True); time.sleep(30)"
```

Then invoke `tools/lv_stallcheck.ps1` at T+0, 70, 140, 210, 280 s — it needs a baseline sample ≥ `$DeltaWindowSeconds`=60 (`:32,:106`) and `$StallSeconds`=150 of age (`:25`).

| outcome | reading |
|---|---|
| silent flagged, heartbeat **not** | log-freshness works → defect is in the job; fix = 3 lines in `preexperiment_guard.py`; your remedy is unnecessary **(my prediction)** |
| **both** flagged | ancestor walk inert for `--detach`ed jobs → alternative B, a real watchdog defect |
| neither | predicate doesn't fire on detached jobs at all → re-open the diagnosis of record 5 |

Honest cost: the silent probe writes a `stall_pid*.log` that arms `guard_peer.py:67`. Run it inside one bgrun that moves any record it creates into `archive/` naming this probe — don't hide it.

## 5. Structural criticism

**Salvageable, but the architecture is inverted — and your remedy is the worst option available.**

*It adds exemption #6.* Five exist: `BENCH_CELL` (`:43`), `matrix_run` by name (`:73`), non-leaf (`:77`), log-fresh<90 s (`:91-97`), lifetime-CPU dropped (`:103-113`). #2 is a permanent blind spot — a genuinely hung matrix driver is now undetectable forever. "Teach it about intentionally-sleeping jobs" asks the observer to see *intent*; every implementation is an allowlist, an opt-out env var, or a declared-duration file, all of which move trust into the job while leaving detection in the observer.

*The mechanism already exists, unused.* `lv_stallcheck.ps1:80` already says **"Progress, not CPU, is the signal"** and `:91-97` already skips any job whose bgrun log is fresh. One `print(..., flush=True)` per minute in the sleep loop and record 5 never happens — **with no watchdog change at all.**

*Two defects worth fixing regardless:*
- **CPU delta cannot do its assigned job.** Windows CPU accounting is quantized (~15.6 ms) and a thread blocked in a COM/RPC call accrues *zero* CPU by definition — so it cannot distinguish "blocked" from "sleeping", the exact discrimination asked of it.
- **Its sampling rate is the session's tool-call rate.** It is a PostToolUse hook (`.claude/settings.json:38-47`), and because `continue` at `:95` precedes the sampling at `:101`, flagging needs two invocations spanning ≥60 s of continuous silence. **During an unattended overnight run with no Bash calls it never executes** — structurally blind exactly where CLAUDE.md §1c' requires unattended operation.

*The correct design — liveness asserted, not inferred.* systemd settled this: `WatchdogSec` requires the process to send `sd_notify("WATCHDOG=1")`, because a process can be running and wholly unresponsive and the supervisor cannot infer liveness from observing that it exists. Cheapest version here, since `bgrun` already owns the process, the deadline and the log:

1. `bgrun` sets `BGRUN_HEARTBEAT=<log>.hb`; `tools/heartbeat.py:tick()` is 3 lines that touch it.
2. COM clients tick around every `Run`/`Invoke` (one central call site already exists); long sleepers tick in their sleep loop — `preexperiment_guard.py` becomes `for _ in range(int(minutes)): time.sleep(60); tick()`.
3. `lv_stallcheck.ps1` tests **only** that file's mtime. Drop CPU delta. A job with no `.hb` is *unmonitorable* — a configuration finding, different record, no `guard_peer` arm.

Test of whether that design is right: **record 4 still fires** (last tick precedes the COM call that never returned, `build_opconnectnested_v0.log:130`) and **record 5 does not.** One change, both cases correct, zero exemptions.

*The economics run the other way.* A false stall costs one review (~$1.86, CLAUDE.md's dual self-test cost line). The missed real stall of 2026-08-28/29 cost **7 hours** — which is why this file exists (`lv_stallcheck.ps1:4-9`). ~200 false positives buy one such loss. Tuning this detector toward silence is backwards; make the fleet observable instead.

**What would change my mind:** the "both flagged" branch of the test in §4. If a heartbeating detached job is still flagged, alternative B is the explanation, the fix is in the watchdog, and my §5 ordering is wrong.

Sources: [sd_notify](https://www.freedesktop.org/software/systemd/man/latest/sd_notify.html) · [sd_watchdog_enabled](https://www.freedesktop.org/software/systemd/man/latest/sd_watchdog_enabled.html) · [GetProcessTimes](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes) · [sdlogwatchdog](https://github.com/detecttechnologies/sdlogwatchdog)

## Sources

(extract from answer)

## What was done with it

READ AND RECORDED, NO CODE CHANGED THIS SESSION — same disposition as the codex arm
(`archive/peer/2026-09-17-stall-preexperiment-sleep-codex.md`), which this arm largely agrees with.

Kept for judgement, verbatim from §1/§2/§5 of the answer:
- the claim was refuted at its premise: an 18:17 decision cannot be judged with 18:55 evidence, and one of the
  five "false positives" was a confirmed TRUE positive earlier the same day;
- `log stale` at `tools/lv_stallcheck.ps1:112` is a literal in the format string, so a record cannot prove the
  ancestor walk found or read a log — a real, separate defect;
- the proposed heartbeat design (bgrun exports `BGRUN_HEARTBEAT`, long sleepers and COM clients tick it, the
  watchdog tests only that mtime and drops the CPU delta) is a fleet-wide design change and therefore a
  judgement call, not a material one. It is on STATUS's OPEN list, not built.

No `FIXED:`/`REFUTED:` line is claimed here: nothing in the watchdog changed, and a promise is not a fix.
