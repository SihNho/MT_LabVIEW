# stall-liveness-class-c36

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.1587  in 18 / out 34537 / cache-create 177492 / cache-read 899644  (506s, 16 turn(s))
- **date:** 2026-09-18 21:12:53
- **outcome:** ANSWERED (507s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# Refute two claims about this project's stall watchdog and its background runner

Your job is to ATTACK the two claims below. Both are this session's own conclusions, formed under pressure after a
failed prediction, so treat them as hostile witnesses. Do not restate them back.

## Context (what the machinery is)

- `tools/lv_stallcheck.ps1` is a watchdog. It looks at processes descended from this project's background runner,
  and writes a record `tools/bench/stall_pid<PID>_<HHMMSS>.log` beginning `STALL: ... alive Ns, log stale, CPU
  +0.00s in the last Ms` whenever a leaf process is alive, its associated bgrun log has not grown, and the process
  burned no CPU in the sample window.
- `tools/hooks/guard_peer.py` reads those records: a `^STALL:` line is treated as a FAILED PREDICTION ("this client
  finishes"), and it BLOCKS the next recipe build until a peer review newer than that record, naming that record, is
  archived. So every false positive costs a paid review.
- `tools/bgrun.py` is the background runner. It is supposed to ALWAYS write a final `BGRUN END rc=<n> after <s>s` or
  `BGRUN TIMEOUT` line into its log, killing the process tree at a deadline.
- A standing user order forbids building any NEW process device (gate, hook, record, lock). REPAIRS of the three
  existing devices above are permitted.

## CLAIM 1 — refute it

"The repeated STALLED-LabVIEW-client false positives are NOT caused by PID/command-line mis-binding or by a missing
bgrun job log. They are caused by a legitimate bgrun job class — long waiters and holders whose log is written ONCE
at START — for which 'stale log + zero CPU' is the healthy steady state. Therefore `tools/lv_stallcheck.ps1` cannot
separate a healthy waiter from a genuinely stalled LabVIEW client using log age and CPU alone, and cycle 36's
shipped repair (identity-binding + skipping leaves with no bgrun log) does not address the class."

## CLAIM 2 — refute it

"The three bgrun logs that end without `BGRUN END|TIMEOUT` are CALLER-side, not a bgrun defect: none carries a
`BGRUN DETACH` line, so each stayed inside its caller's job object and the runner process was terminated — no code
inside bgrun can write a line after TerminateProcess."

(Context for claim 2: on Windows, this harness kills background tasks at a deadline; a `claude -p` cell that ends
its turn has its child job object terminated. bgrun writes its final line from a Python `finally` / atexit path.)

## ALREADY RULED OUT — measured THIS cycle, `tools/bench/repair_c36_selftest.log`. Do not re-propose these.

1. The cycle-35 reviewer's premise is FALSE: `stall_pid11536_193335.log:3`'s process was the bgrun CHILD of
   `wait_runner_exit.log` (START 19:33:35), so the ancestor walk DID find a job log; that job ended
   `BGRUN END rc=0 after 4022s` — the waiter finished normally, i.e. the alert was a false positive on a healthy job.
2. The cycle-35 reviewer's four falsification probes F1–F4 (`tools/bench/peer_stall_c35.log:50-53`) were RUN:
   F1 not evaluable (pid gone), F2 False (3 `RUNNER STOP` lines, last 20:40:22), F3 False (pid not alive),
   F4 False (21 live `cycle_runner` rows; `cycle_21.log` ends `BGRUN END rc=0 after 4076s`).
3. Measured side-fact: a bgrun child launched as `python.exe` directly OWNS a `conhost.exe`, and the watchdog then
   drops it as "wrapper (has a live child)" — so the watchdog is blind to any bgrun child that allocates its own
   console.

## What to return, in this order, for EACH claim separately

1. **Strongest reason the claim is WRONG** — the specific mechanism, not a caveat.
2. **An alternative explanation** of the same observations that the claim does not cover.
3. **What would FALSIFY the claim** — a concrete observable, readable from a file, a process table or a log.
4. **The CHEAPEST discriminating test** — one command or one file read, seconds not minutes, that separates the
   claim from your alternative.

## Then one further question, answered concretely

Given that NO new process device may be built, does any REPAIR of an existing device — `tools/lv_stallcheck.ps1`,
`tools/bgrun.py`, `tools/hooks/guard_peer.py` — actually fix the CLASS behind claim 1 (healthy waiters
indistinguishable from stalled clients), or does every candidate repair amount to a new device or a new heuristic
with its own false positives? Name the repair, name the signal it would read that log-age and CPU do not carry, and
name what it would still get wrong.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled for this role, so nothing was written — correct for a read-only reviewer; the review above is the deliverable.

**Summary for the manager:** claim 1's causal attribution is false (4 of 7 stall records name sweeps, drivers and a recipe build, and the three oldest came from a predicate that no longer exists), though its conclusion about the repair survives — and for a sharper reason than the claim gives: repair 2's own motivating example had a bgrun ancestor, so the repair does not touch the case its comment cites. Claim 2 is refuted outright: `tools/bgrun.py` has no `try/finally` or `atexit` anywhere, and `stall_pid20500_143532.log:1` records the supposedly-terminated tree alive 595 s after its log fell silent.

The repair that fixes the class is not in the watchdog. It is (1) a `try/finally` around `bgrun.main()` plus a non-fatal stdout echo, which makes `bgrun.py:7-10`'s promise true for the first time, and then (2) letting `guard_peer.py` retract a stall record whose named job later ends `BGRUN END rc=0` — outcome instead of snapshot. Both live in files that already exist; (2) is unsound until (1) is done.

## Sources

(extract from answer)

## What was done with it

Dispatched by the cycle-36 MATERIAL session as the mandatory failed-prediction review (CLAUDE.md §5;
`docs/cycle27-plan.md` Pre-decided 7 — SINGLE `-Agent claude -Role hypothesis` arm). Outcome **ANSWERED**, 507 s,
$3.1587 (`tools/bench/peer_stall_c36.log:2-3`).

**Verified against the machine before reporting** (a peer answer is a hypothesis): the load-bearing fact under the
claim-2 refutation is TRUE — `grep -n "finally\|atexit" tools/bgrun.py` returns **zero matches**, so the
"always ends by writing `BGRUN END|TIMEOUT`" promise at `tools/bgrun.py:7-10` has no exception-path or
process-exit mechanism behind it at all, and `tools/bench/stall_pid20500_143532.log:1` records the tree the claim
called "terminated" as **alive 595 s** after its log fell silent.

**Not decided here.** The reviewer's proposed repairs — (1) `try/finally` around `bgrun.main()` + a non-fatal
stdout echo, (2) `guard_peer.py` retracting a stall record whose named job later ends `BGRUN END rc=0` — are
repairs of existing devices, not new ones, but whether to build either is a JUDGEMENT call and was left to the
judgement session (material session, brief: "report; do not decide").

**Capture limitation to note:** the archived answer is the reviewer's FINAL message only. Its own line "Write is
disabled for this role … the review above is the deliverable" shows it intended to write the full four-part
per-claim answer (strongest counter · alternative · falsifier · cheapest discriminating test) to a file; Write is
denied for the `hypothesis` role, so those four sections exist nowhere on disk — only the summary paragraph above.
