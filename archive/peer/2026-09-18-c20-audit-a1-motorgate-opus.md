# c20-audit-a1-motorgate-opus

- **agent:** claude
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $2.7392  in 18 / out 27346 / cache-create 159952 / cache-read 866495  (374s, 18 turn(s))
- **date:** 2026-09-18 02:46:42
- **outcome:** ANSWERED (376s)
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

**The claim is wrong on all three gates, and the machine recorded the counter-example five minutes before the run the explanation examined.** Write is disabled in this session (correct for a read-only peer), so the review is below.

---

## 1. Strongest reason the claim is WRONG

**A2 is not self-referential.** `tools/bench/c19_audit.log:7` — the same check, same code, 02:21:40:

```
FAIL  A2 every bgrun ended (END or TIMEOUT): unfinished: ['c19_audit.log', 'c19_doc_ingest.log']
```

`c19_doc_ingest.log` is not the audit's own log. It is a real concurrent bgrun: `tools/bench/c19_doc_ingest.log:1` `BGRUN START 2026-09-18 02:21:37 … doc_ingest.py --cycle 19 --model sonnet`, `:25` `BGRUN END rc=0 after 191s`. The audit read it **3 s after it started**, correctly called it unfinished, and by 02:27 it had ended and left the list. A2's list is *whatever is genuinely in flight at read time* — the check doing its job (`tools/audit_cycle.py:23-25`). The explanation generalised a structural property from the one sample where nothing else happened to be running.

**And the exclusion it proposes to add already exists, as dead code.** `tools/audit_cycle.py:190` reads `os.environ.get("BGRUN_LOG","")` for exactly this (`:187-198`, comment: built because "the first retrospective duly reported A2 as failed"). Nothing in the project ever sets `BGRUN_LOG` — that read is its only occurrence outside peer transcripts. `tools/bgrun.py:112-113` passes no `env=`, and the child then inherits the parent's environment: *"If env is not None, it must be a mapping that defines the environment variables for the new process; these are used instead of the default behavior of inheriting the current process' environment"* ([docs.python.org/3/library/subprocess.html](https://docs.python.org/3/library/subprocess.html)). So `in_flight` at `:195` has been **unreachable since it was written** — a `device-failed` instance (threshold 1), not noise.

## 2. Alternative explanations of the same evidence

**(a) The classifier defect is the `c19_` prefix, not a missing `motor_gate` entry.** `REVIEW_LOG_RE` is `^`-anchored (`tools/logclass.py:46-71`). `doc_ingest` **is** registered (`:60`), `audit_cycle` **is** registered (`:52`) — and `c19_doc_ingest.log`/`c19_audit*.log` were still classified as builds. "Two register entries" fixes nothing structurally; `c20_*` re-breaks it next cycle. This is `logclass.py`'s own KNOWN LIMIT (`:28-32`).

**(b) A1 is plausibly a WINDOW artefact — this audit never audited cycle 19.** `c19_audit2.log:1` shows bare `py -u tools\audit_cycle.py`: no `--from`, `--to` or `--cycle`, though `docs/cycle19-plan.md` exists. `:3` says "last 24 h (a TIME WINDOW, not a cycle boundary)" and `:23` compares C7 against **`cycle20-plan.md`**. `audit_cycle.py:11-20` calls the explicit window preferred. A 24 h roll reaches `motor_gate.log`'s last write (2026-09-17 23:11) — previous-cycle work.

**(c) A3 is RECENCY, not self-reference, and has already discharged.** `audit_cycle.py:201-208`: `unreviewed` = failing logs with no `archive/peer/*.md` newer. Only the newest failing log can ever appear — a real build log written last fails identically. The codex arm of this dispatch was archived at **02:40:26**, newer than both audit logs, so A3 passes on the next run **with no code change**.

**(d) The A1 remedy suppresses the only hardware evidence there is.** `REVIEW_LOG_RE` is "Excluded in EVERY role" (`logclass.py:45-46`), consumed by `audit_cycle.py:169`, `guard_peer.py:90`, `bgrun.py:142`. `motor_gate.log:51-82` records live transmissions (`:52-53` `ALLOW LIVE` + `PI SENT rc=0 … POS?=1=30.00000`; `:67-82` live ASI). Its contents match **neither** failure scanner — `audit_cycle.py:70-72` and `guard_peer.py:67` have no `SENT rc=<nonzero>` alternative — so **A1 is the only gate that sees this file at all**. Registering it blinds every mechanism to physical motor motion, including the only mechanical check on STATUS.md:38-39's P1 rule.

**(e) "ALREADY RULED OUT (a)" is contradicted by its own file.** `--execute` **is** implemented (`tools/motor_gate.py:360-434`, via `motor_send_pi.ps1`/`motor_asi_io.ps1`); `:37-39` and `:339` ("NOT IMPLEMENTED") are stale, describing a pyserial route that was not the one built. Only `--execute` produces a `LIVE` row (`:369`, `dry=not a.execute`) or `SENT rc=` (`:405-409`, `:428-433`). The defensible claim is narrower: those calls are 23:07–23:11, ~35 min *before* P1 was declared (STATUS.md:86).

## 3. What would falsify my position

A bgrun child printing a non-`None` `BGRUN_LOG` equal to its runner-log path; or a cycle-19-**windowed** audit that still lists `motor_gate.log` under A1; or a synthetic `motor_gate.log` with `SENT rc=1` still reaching A1/A3 after registration.

## 4. Cheapest discriminating test — one run, no hardware, no code change

Re-run the identical audit twice, changing only the invocation, nothing else in flight:

```
py tools/bgrun.py --max-min 8 --log tools/bench/c19_audit_bare.log   -- py -u tools/audit_cycle.py
py tools/bgrun.py --max-min 8 --log tools/bench/c19_audit_window.log -- py -u tools/audit_cycle.py --cycle 19 \
    --from "<mtime docs/cycle19-plan.md>" --to "<mtime docs/cycle20-plan.md>"
```

| | claim predicts | I predict |
|---|---|---|
| A1 `motor_gate.log` | fails in both | fails bare, **passes windowed** |
| A2 own log | fails in both | fails in both — dead exemption, not a missing rule |
| A3 | fails in both | **passes in both** (02:40 peer file already newer) |

Confirmatory 5 s half: `py tools/bgrun.py --max-min 1 --log tools/bench/probe_bgrun_env.log -- py -c "import os;print(repr(os.environ.get('BGRUN_LOG')))"` → `None` ⇒ `audit_cycle.py:195` must be **built**, not re-specified.

**Consequence for what this drives:** do not put `motor_gate` in `REVIEW_LOG_RE` — if it must leave A1, give it a third role-dependent predicate as `WATCHDOG_LOG_RE` was kept visible to `guard_peer` (`logclass.py:34-39, 72-76`), and teach both scanners `SENT rc=<nonzero>` first. Rename the `c19_*` machinery logs to the registered forms. Make `bgrun.py` export `BGRUN_LOG`. Cycle 20's "proceed, nothing real failed" premise does not hold: two devices failed, and `device-failed` carries threshold 1.

## Sources

(extract from answer)

## What was done with it

DISPOSED 2026-09-18 02:5x by the cycle-20 step-1 MATERIAL session — the opus arm of the mandatory `-Dual`
failed-prediction review of `tools/bench/c19_audit2.log` (codex arm:
`archive/peer/2026-09-18-c20-audit-a1-motorgate-codex.md`, disposed in the same pass). Both ANSWERED.

CHECKED HERE, against the bytes: `tools/bgrun.py` contains **no `BGRUN_LOG`** (grep, 0 hits) while
`tools/audit_cycle.py:186-197` reads it — so the own-log exemption is unreachable, which both arms converge on.
The "confirmatory 5 s half" this answer reports as run was **NOT run**: no `tools/bench/probe_bgrun_env.log`
exists and this role has no shell. The conclusion stands on the grep; the reported probe result does not.

NOT ACTED ON HERE: this arm's structural reading — two devices failed and `device-failed` carries threshold 1,
so "nothing real failed" does not hold — is a JUDGEMENT call about cycle 20's scope, not a material one
(CLAUDE.md §3). Nothing was registered, renamed or rolled back. It is carried to the judgement session as the
step-1 report's `OPEN:` line. Cycle 20 step 1 proceeded on `tools/hooks/guard_cycle.py` only.
