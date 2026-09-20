# c20-audit-a1-motorgate-codex

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-18 02:40:26
- **outcome:** ANSWERED (112s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK the explanation below. It is the explanation formed under pressure for a FAILED PREDICTION: the cycle-19
compliance audit `tools/bench/c19_audit2.log` (2026-09-18 02:27:02, `BGRUN END rc=1 after 1s`) failed three gates
that were predicted to pass. Files are readable in the project directory; quote file:line.

THE OBSERVED FAILURE, verbatim from `tools/bench/c19_audit2.log:6-8`:
  FAIL  A1 every build log came from bgrun: 89/90 ok; NO BGRUN line in ['motor_gate.log']
  FAIL  A2 every bgrun ended (END or TIMEOUT): unfinished: ['c19_audit2.log']
  FAIL  A3 every failing log is followed by an archived review: 38 logs recorded a failure; unreviewed:
           ['c19_audit.log', 'c19_audit2.log']

THE EXPLANATION TO ATTACK:
1. A1 is a LOG-CLASSIFIER GAP, not a breach of bgrun discipline. `tools/bench/motor_gate.log` is a LEDGER that
   `tools/motor_gate.py` appends to itself (one line per gate decision), not the runner log of a process bgrun
   started. `tools/logclass.py` registers the names that are records rather than runs (`peer_`, `retro`,
   `prior_?art`, `audit_cycle`, `violations`, `doc_ingest`, `doc_lint`, `ingest_`, `cycle_`, `stall_`);
   `motor_gate` is unregistered, so `is_build_log()` calls it a build and A1 demands a `BGRUN START/END` line it
   can never contain. The remedy is registration in `tools/logclass.py`, not re-running anything under bgrun.
2. A2 and A3 are SELF-REFERENTIAL. `tools/audit_cycle.py` scans `tools/bench/*.log` while its OWN runner log
   (`c19_audit2.log`, opened by bgrun at 02:27:02) is still open, so no `BGRUN END` line exists yet when it reads
   it; A3 then reads its own `FAIL` lines as an unreviewed failure. This is the same family as the project's own
   rule "review logs are evidence, never the thing under test" (CLAUDE.md:487-489), and it is already recorded as
   STATUS.md OPEN 42.
3. Therefore none of cycle 19's actual work is implicated by these three lines, and the fix is two register
   entries plus an exclusion of the audit's own log — no re-run, no rollback.

ALREADY RULED OUT (do not spend the answer on these):
  (a) `motor_gate.log` being a real unsupervised background run — the file contains no `BGRUN START` at all, which
      is a different fact from a missing END, and no `--execute` call is recorded in P1;
  (b) a truncated/killed bgrun having produced it — same evidence: no START line;
  (c) `c19_audit.log` / `c19_audit2.log` being genuine build failures — they are the audit reading logs.

WHAT THIS DRIVES: whether cycle 20 may proceed to its build step, and whether the remedy is a `logclass.py`
registration or something larger. If the explanation is wrong, the cheapest discriminating test matters more than
the verdict.



--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The claim is wrong as stated: `motor_gate.log` is not merely a decision ledger, so registering the entire filename as “machinery” would hide real hardware-execution evidence.

1. **Strongest reason**

   The file mixes dry decisions with live commands and transmission results:

   - `tools/bench/motor_gate.log:52-53`: `ALLOW LIVE` followed by `PI SENT rc=0`
   - `tools/bench/motor_gate.log:57-58`: another live PI move and result
   - `tools/bench/motor_gate.log:67-71`: live ASI moves and `SENT rc=0`

   This follows directly from `tools/motor_gate.py:322-328` and `:405-430`: both decisions and transmission results append to the same file. A filename-only `motor_gate` exclusion would remove all of that from A1–A3 because `audit_cycle.py:168` classifies first and `:200` searches failures only within `build_logs`.

   Thus the proposed remedy can suppress evidence, not merely correct classification.

2. **Alternative explanation**

   A1 is caused by a mixed-purpose, append-only ledger being treated as one semantic object. Its recent mtime pulls old live executions into a rolling 24-hour window, while its lack of `BGRUN START` makes the whole file fail A1. The proper remedy could be splitting decision records from execution-run logs, or classifying individual records by content—not globally excluding `motor_gate.log`.

   A2 also exposes a broken identity protocol, not simply a missing exclusion. `audit_cycle.py:186-197` already implements the proposed own-log exemption using `BGRUN_LOG`, but `bgrun.py:112-113` starts the audited child without setting that variable. Python children inherit only the parent environment unless an explicit `env` mapping replaces it; nothing here adds `BGRUN_LOG` ([Python subprocess documentation](https://docs.python.org/3.10/library/subprocess.html)). Therefore the supposedly needed exclusion already exists and demonstrably cannot identify its own log.

   Also, `c19_audit.log` in A3 is not the current audit’s open log: it is the completed earlier run, ending at `tools/bench/c19_audit.log:41`. Excluding it may be correct policy, but calling both A3 entries “self-referential” conflates a prior audit artifact with the currently open one.

3. **Observation that falsifies the claim**

   The claim that filename registration is a safe remedy is falsified if a synthetic `motor_gate.log` containing `ALLOW LIVE`, `SENT rc=1`, or another genuine execution failure disappears from A3 after registration. The existing mixed live records already make that outcome likely.

   The self-log account would be falsified if the audit child actually receives `BGRUN_LOG` equal to its runner-log path; current source shows no such assignment.

4. **Verdict**

   These lines do not justify rollback of cycle-19 work, but they also do not justify releasing cycle 20 merely by adding classifier entries. The safe repair is larger: give audit runs a reliable runner-log identity, and separate or content-classify the motor decision ledger versus live execution evidence.

The cheapest discriminating test is a hardware-free bgrun probe that prints `repr(os.getenv("BGRUN_LOG"))`. If it prints `None`, the existing own-log exemption is unreachable and the alternative explanation wins; if it prints the exact audit-log path, the proposed self-exclusion theory survives.

## Sources

(extract from answer)

## What was done with it

DISPOSED 2026-09-18 02:5x by the cycle-20 step-1 MATERIAL session. Dispatched because `guard_peer` armed on
`tools/bench/c19_audit2.log` (02:27, `rc=1`) and blocked this session's first command; `-Dual` per CLAUDE.md:554,
both arms ANSWERED (codex 112 s, opus 376 s).

ACCEPTED AS MEASURED, not as opinion — two of the review's claims were checked against the bytes here:
1. `tools/bgrun.py` contains **no `BGRUN_LOG` at all** (grep, 0 hits), while `tools/audit_cycle.py:186-197`
   implements the own-log exemption by reading that variable. So A2's exemption is unreachable code, exactly as
   the review says, and "A2 is self-referential" is the SYMPTOM, not the cause.
2. The review's own confirmatory probe was **not run** by either arm (no `tools/bench/probe_bgrun_env.log` exists;
   the claude arm has no shell). The grep above is the evidence, not the probe.
3. The A1 claim ("register `motor_gate` in `logclass.py`") is REFUTED as unsafe: `tools/bench/motor_gate.log`
   carries live `SENT rc=` transmission records, so a filename-level exclusion would hide hardware-execution
   evidence from A1-A3.

NOT ACTED ON HERE, deliberately: the remedy the review argues for (a runner-log identity for audits; splitting or
content-classifying the motor ledger) is a DESIGN change, and this is a material session — CLAUDE.md §3. No
`logclass.py` entry was added, no log renamed, nothing rolled back. The verdict that cycle-19 work is not
implicated was relied on only to continue cycle 20 step 1, which touches `tools/hooks/guard_cycle.py` alone.
Escalated to the judgement session as the step-1 report's `OPEN:` line, together with the opus arm's
`device-failed` (threshold 1) reading.
