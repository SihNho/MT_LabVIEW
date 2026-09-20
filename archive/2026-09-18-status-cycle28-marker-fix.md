---
type: archive
status: archived
date: 2026-09-18
tags: [status-relocation, cycle28]
---

# STATUS narrative relocated at the cycle-28 close (verbatim, rule 4 — STATUS was 117 lines)

## §1 — the "Side item" paragraph from `## NEXT`, now DONE (STATUS OPEN 52, closed 16:26)

> **Side item (needs no LabVIEW, no user answer):** repair
> `tools/audit_cycle.py`'s cost window — clip each run by its own `BGRUN START`/`END` timestamps instead of counting
> a whole log whose mtime lands in the window (cycle 26's retrospective: 23:23 + $13.7777 imported from
> `tools/bench/cycle_12.log:1`; `VIOLATION: device-failed`, 3rd occurrence, threshold 1). This is a REPAIR of an
> existing device, not a new one — the 08:53 no-device order does not cover it. Add the self-test line asserting a
> pre-window run is excluded. Until it lands, no `audit_cycle` cost number is quotable.

Outcome: `tools/bench/selftest_audit_cost_window.log` — `SELFTEST 7 pass / 0 fail`, `BGRUN END rc=0 after 0s`
(T6 on the real `cycle_12.log`: OLD whole-file 19 min 59 s / $13.7777 → NEW 0 runs / $0.0000). `audit_cycle`
imports cleanly, so its import-time `_self_test()` passes and `retrospective.py` / `guard_cycle` are unbroken.

## §2 — the cycle-26 bookkeeping paragraph from `## NEXT`

> **Cycle 26 did this, do not redo it:** the `STOP`, codex's re-plan text, the retrospective
> (`archive/peer/2026-09-18-retrospective-cycle26.md`, annotated) and `doc_ingest --cycle 26` (3 contradictions, all
> resolved). `_v2` needs **no** stop_record release. ⚠️ **Cycle 25 has NO retrospective**; cycle 26's run covers it.
> Relocated verbatim narrative (`_v1.py`-bricking route · cycle-22's settled points · THE RUNNER'S ORDERS · P1/P2/P3)
> + cycle-26's own facts → `archive/2026-09-18-status-cycle26-stop.md`. ⚠️ P1's "no motor moves, no port opened" is
> SPENT: the user ordered P2 and the live run of 15:37 opened both ports (HARDWARE banner above).

## §3 — cycle 28's own facts (the material-marker deadlock, dispatch 3)

- The `--material` FLAG form **executes**: the first material recipe run since the deadlock began
  (`py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_audit_cost_window.log -- py -u
  tools/bench/selftest_audit_cost_window.py`, permitted, rc=0).
- The cycle-28 repair had been **incomplete**: `guard_bash.py`'s background gate matched
  `bgrun\.py\s+--max-min\s+\d` — `--max-min` had to be the FIRST argument — so the newly mandated form was
  refused by the same hook that mandates it, with the text *"a backgrounded LabVIEW command must run through
  `py tools/bgrun.py --max-min <N> --log <file> -- <command>`"*. Repaired with one shared
  `BGRUN_RE = r"bgrun\.py\s+(?:-\S+\s+)*--max-min\s+\d"` (`tools/hooks/guard_bash.py:187-195`, used at `:234`
  and `:244`); `--max-min <digit>` still required, deadline guarantee unchanged.
- Mandatory hypothesis peer review of the deadlock: `archive/peer/2026-09-18-permission-material-deadlock.md`
  (claude / opus / effort max, `OUTCOME: ANSWERED (402s)`), disposed under "What was done with it" — partial
  refutation accepted: our `ls -la …` vs `MATERIAL=1 ls -d tools` pair demonstrates the READ-ONLY CLASSIFIER,
  not the `Bash(py tools/*)` allow rule, so the allow-rule mechanism rests on the documentation sentence alone.
- Still carrying the dead prefix, left to judgement: `.claude/agents/material.md:26-27` (the material agent's
  own system prompt mandates `MATERIAL=1` as the ONLY form) and `tools/cycle_runner.py:183-194`
  (`RECIPE_RE`, and the instruction text handed to every cycle).
