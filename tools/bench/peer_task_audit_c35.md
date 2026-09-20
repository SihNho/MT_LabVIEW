# ATTACK this reading of `tools/bench/audit_c35.log`

## What happened

Cycle 35 repaired `tools/audit_cycle.py` check C7 (it built the plan filename from the cycle number,
`docs/cycle<N>-plan.md`, which went dead when this project moved to ONE plan spanning cycles 27+; it now reads the
plan whose frontmatter says `status: current`, via `doc_lint.current_plans()`). To verify the repair I ran the
audit: `py tools/bgrun.py --material --max-min 10 --log tools/bench/audit_c35.log -- py -u tools/audit_cycle.py`.

C7 printed, for the first time in many cycles, a real answer (`audit_c35.log:23`):
`C7 files modified in the window but NOT named in docs/cycle27-plan.md [frontmatter status: current]: 138 - …`

The run ended `BGRUN END rc=1 after 1s`, because the audit exits non-zero when any A-check fails
(`audit_c35.log:39`): `AUDIT VIOLATIONS: A1 …, A2 …, A3 …, A4 …`. The four failing lines, verbatim:

```
FAIL  A1 every build log came from bgrun: 88/89 ok; NO BGRUN line in ['motor_gate.log']
FAIL  A2 every bgrun ended (END or TIMEOUT): unfinished: ['audit_c35.log',
      'diag_fstunnelterm_v2_panelcost.log', 'p2_open_copy.log', 'prose_cycle25.log', 'wait_runner_exit.log']
FAIL  A3 every failing log is followed by an archived review: 26 logs recorded a failure;
      unreviewed: ['audit_c35.log']
FAIL  A4 every archived review says what was done with it: 99/121 annotated; blank: [6 named files]…
PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c…, mtime 2026-09-01 12:07
```

`tools/hooks/guard_peer.py` then blocked the next bench run on `audit_c35.log` as a FAILED PREDICTION.

## THE CLAIM YOU ARE ASKED TO REFUTE

**Claim D:** none of those four failures is evidence about the C7 repair or about the work the gate is now
blocking, and in particular:

1. **A2 and A3 are SELF-REFERENTIAL.** `audit_c35.log` is named by A2 as "unfinished" and by A3 as "unreviewed"
   because the audit reads the directory of bench logs *including the log it is at that moment writing* — at the
   instant A2/A3 ran, its own `BGRUN END` line had not been written yet, and no review of a log that does not yet
   exist can exist. This project already recorded that self-reference (STATUS.md OPEN 42: "`audit_cycle` A2/A3
   SELF-REFERENTIAL, not fixed").
2. **A1 and A4 are PRE-EXISTING and untouched by this cycle.** `motor_gate.log` (A1) and the six blank review
   dispositions (A4) were all written in earlier cycles; A4's blank list is STATUS.md OPEN 42's "39 undisposed
   reviews" and `doc_lint` L6's standing warning. Nothing cycle 35 did created or worsened them.
3. **Therefore the safe action is to proceed** with the one remaining task: a READ-ONLY VI-Server measurement
   (`tools/bench/diag_count_indicator.py`) of what the `Count` indicator is wired to, on a `claudeDev` COPY —
   no motor, no serial, no camera, no VI is run, no file is written except a JSON of the readings, and the
   ORIGINAL's md5 is checked before and after.

Attack it:

1. The strongest reason Claim D is WRONG — including any way the four failures could be *caused by* the C7 edit
   or by the `doc_lint.current_plans()` helper added in the same cycle.
2. An ALTERNATIVE explanation of the same log, especially of A2's other four entries
   (`diag_fstunnelterm_v2_panelcost.log`, `p2_open_copy.log`, `prose_cycle25.log`, `wait_runner_exit.log`) —
   are those also benign, or is one of them a live process that should stop something?
3. What observation would FALSIFY Claim D.
4. The cheapest discriminating test, runnable now, that separates "self-reference + pre-existing debt" from
   "the C7 edit broke something".
5. Whether the specific next action — that read-only measurement — can cause any harm the STALL/prediction gate
   exists to prevent. The rig is **assembled**: motors and the ASI are reachable only through `tools/motor_gate.py`
   and this script never imports it.

## Already ruled out — do not spend your answer on these

- "Set `PEER_GUARD_OFF=1`" / "`CYCLE_GUARD_OFF`": forbidden by this project's rules, not under consideration.
- "Fix A1–A4 first": A4's remedy (disposing 22 old reviews) and A1's (`motor_gate.log`'s missing BGRUN line) are
  open items owned by judgement (STATUS.md OPEN 42), and this is a material session with no authority to decide
  them. Say so if you think that ordering is itself the error.
- "The audit should not exit 1 on pre-existing debt": possibly true, but changing the audit's exit code is a
  device change, and this project is under a standing user order to build no further process devices
  (STATUS.md line 10, `docs/cycle27-plan.md` Pre-decided 2).
