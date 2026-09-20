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
