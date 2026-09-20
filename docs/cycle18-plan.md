---
type: plan
status: done
date: 2026-09-18
cycle: 18
kind: device
tags: [plan, device, prior-art, gate, motor-limit]
supersedes: []
decided_by: cycle-17 judgement session, on `py tools/violations.py` reporting device-failed DUE (threshold 1)
---

# Cycle 18 — close the `device-failed` hole: bind a recipe LAUNCH to its prior-art verdict

## Why this cycle is not check A

The user's standing P1 order is to build `docs/motor-limit-assurance-plan.md` in its §D order, one step per
cycle, and cycle 17 closed step 1 (the census). Step 2 is check A. **Cycle 18 spends its step on a process
device instead, and the user can overrule that by editing STATUS `## NEXT`.**

The reason is mechanical, not a preference. Cycle 17's retrospective returned
`VIOLATION: device-failed | loss_min=23 | loss_usd=4.8500`, and `py tools/violations.py` reports

```
device-failed   4   23(4)   ...2026-09-18-retrospective-cycle17.md   <== DUE, no decision on file
threshold 3 (device-failed: 1); 1 slug(s) awaiting a response
```

`device-failed` carries **threshold 1** — CLAUDE.md: "a device that let its own fault through is broken, not
unlucky" — and **only the user may lower that threshold.** The rule is "at threshold, the next cycle must build
the mechanical device for it first."

There is a second, better reason, and it is why this is not a detour: **the device needed here is the same
mechanism §D's check C needs** — a record file keyed to a path + hash, and a launcher that refuses to run without
a matching record. Building it against recipes first is a rehearsal of check C on a target where a mistake costs
nothing, instead of on the one where a mistake moves a motor.

## What actually failed (the report's evidence, not a paraphrase)

The prior-art review fired on route-B run 3, correctly said the recipe "was NOT executed" because it could not
pass its own gate, and was marked disposed. **Six seconds later the recipe ran anyway**, with the flagged
branches disabled while its success gate still required them; it failed as predicted and its failed-prediction
review then cost a further 781 s and $4.85.

So the hole is precise: **the device verifies that a review happened and was disposed; nothing binds the recipe's
LAUNCH to that review's verdict.** `FIXED:` / `REFUTED:` release lines already exist and their conditions are
already machine-checked — but no gate requires a launch to be covered by one.

## Pre-decided (apply, cite the number, do not re-ask)

1. **Build the device, do not write a refusal.** A `DECISION: no-device` block for `device-failed` is not
   available this cycle; the judgement session considered and rejected it, because the evidence is a concrete
   unfixed defect with a measured cost.
2. **Shape of the device: a STOP RECORD + a LAUNCH GATE.** A prior-art review whose verdict is anything other
   than `novel` writes a stop record keyed to the recipe's **path + file hash**. `guard_bash` / `guard_cycle`
   refuses to launch that recipe while the stop record stands. Re-saving the recipe changes the hash and does
   **not** clear the record — a changed hash means "unreviewed", not "released".
3. **The only releases are the two that already exist**, with their existing machine-checked conditions:
   `FIXED: <slug> - <path>:<line> - <sentence>` and `REFUTED: <slug> - <file>:<line> says X, which …`. Do not
   invent a third release. `CYCLE_GUARD_OFF` is never the answer.
4. **Prove it on a deliberately blocked recipe before trusting it** — the same requirement as the motor plan's
   §D.4. Build a scratch recipe, plant a standing stop record, and require the launch to be REFUSED; then plant
   a valid `FIXED:` release and require it to PASS; then change the scratch recipe's bytes and require it to be
   REFUSED again. A gate that passes only its happy path is not accepted. Scratch artefacts are created and
   deleted in the same operation.
5. **`docs/violation-decisions.md` is written LAST, by the cycle that has the device running**, citing it. A
   block written before the device exists would discharge the slug on a promise; CLAUDE.md is explicit that a
   promise is not a fix. Cycle 17 deliberately did not write one.
6. **Rig state is 조립 and P1's hardware rule is unchanged: no motor moves, no motor port opened for writing,
   `motor_gate.py --execute` is not to be called.** Nothing in this cycle needs hardware at all.
7. **Every runner cycle gets a `docs/cycle<N>-plan.md`** with a `## Pre-decided` section. Cycle 17's audit could
   not check scope (C7) because no cycle-17 plan existed — the runner's cycles had never had one. The closing
   session of each cycle writes the next cycle's plan file.

## Done means

- The gate exists, is registered, and its self-test covers refuse / release / hash-change-refuses (item 4).
- `py tools/violations.py` no longer reports `device-failed` as DUE, because the device is built **and** the
  `DECISION: device` block cites it (item 5).
- `py tools/doc_lint.py` shows no new FAIL. (L6 — 39 undisposed archived reviews, STATUS OPEN 42 — is
  pre-existing and is not this cycle's job.)

## Then, and only then

Cycle 19 returns to the user's P1 order at **`docs/motor-limit-assurance-plan.md` §A, check A**, with the
cycle-17 decisions already recorded in `docs/motor-call-site-census.md`: the three kinds
(`COMMAND` / `QUERY` / `CONFIGURE`), `ASSUMED_MOTION` replacing `UNKNOWN`, and **check A carries all 43 in-scope
sites — no demotion pass.** Check A's own output is the recorded measurement that demotes the eight vi.lib
GUI/error sites, for free.
