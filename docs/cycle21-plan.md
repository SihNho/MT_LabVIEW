---
type: plan
status: superseded
date: 2026-09-18
cycle: 21
kind: build
tags: [plan, tunnel-reader, motor-limit, P1, no-devices]
supersedes: [docs/cycle20-plan.md]
decided_by: cycle-21 judgement session, applying STATUS `## NEXT` and the user's 2026-09-18 08:53 decision
---

# Cycle 21 — run the step that is already written, released and never run

This plan adds no scope. It restates STATUS `## NEXT`'s "IF the user says continue" paragraph, which is what the
user authorised at 08:53 (*"장치는 더 민들지 말고 계속 진행"*). Cycle 20 wrote, prior-art-released and
launch-gate-cleared `tools/recipes/build_opfstunnelterm_v0.py` and then never ran it, because the
`wrong-ordering` 8/3 round-3 gate stopped the cycle. That gate is released. **Verification level of step 2 is
still NONE**, and nothing else in this cycle matters until that changes.

## Step 1 — discharge the review OPEN 49 owes

The failed prediction is on record and its mandatory `-Dual` review was never dispatched (the session gate closed
cycle 20 first). The claim to be refuted, not confirmed: *`tools/retrospective.py --cycle N` does not select
cycle N's logs — `--cycle N` is only a label and the window is the interval since the previous retrospective
run, so cycle 20 has no retrospective of its own and `violations.py` counts only the retrospective files that
happen to exist.*

Done when: both arms are archived under `archive/peer/` with a classified outcome, and the windowing rule is
stated from the code (`tools/retrospective.py:<line>`), not from inference.

## Step 2 — LAUNCH `tools/recipes/build_opfstunnelterm_v0.py` and prove its three done-whens

Unchanged from `docs/cycle20-plan.md:45-48`, because the recipe is unchanged:

1. the op returns, for a real tunnel uid on a real VI, the terminal reference **and its owner** — a live read on
   an instance, which is the whole point of the op (attaching a property id to a class is not a read);
2. the known-good fixture resolves **through the new op**: `LoopTunnel #28343 → Max Trans Pos.vi · Magnet
   position output` (`docs/frame-loop-wire-graph.md:264`) — last time it resolved only through the OLD ops;
3. the d10 uid-44036 walk advances past the flat-sequence border that stopped it in cycle 19, crossing ≥1 FSIT,
   with the hop count recorded;

plus Pre-decided 3 below: the op is shown to REFUSE two deliberately bad inputs, not only to pass on good ones.

## Step 3 — only if steps 1–2 close: check A, `docs/motor-limit-assurance-plan.md` §A.1

In §A.1's own order — the ORIGINAL's read-only node/terminal sweep, forward reachability from the three coerce
nodes, the control **Data-Entry ranges**, the three comparator mutation negatives. §A.1 is SETTLED: do not
redesign it and do not re-open its prior-art release.

## Pre-decided (apply, cite the number, do not re-ask)

1. **BUILD NO FURTHER PROCESS DEVICE.** User, 2026-09-18 08:53, standing until they say otherwise: no new gate,
   hook, record store, lock or launcher. A retrospective or review naming one is a FINDING, not a task.
   `docs/violation-decisions.md` round-3 block `DECISION: no-device`.
2. **Hardware — P1 is stricter than the rig state and P1 wins.** `rig-state: 조립`. **No motor moves and no motor
   port opened for writing**; `motor_gate.py --execute` is not called at all. LabVIEW and camera allowed.
   Originals are read-only: md5 before AND after every run, never save, Don't Save on every prompt.
3. **A gate or op that passes only its happy path is not accepted.** Anything that can refuse is proven to refuse
   on deliberately bad input.
4. **Every prior-art dispatch passes `--recipe <path>`**; a non-`novel` verdict arms the launch gate until a
   valid `FIXED:`/`REFUTED:` line stands. Writing that release line is the judgement session's call, never the
   material session's. `CYCLE_GUARD_OFF` is never the answer.
5. **Do not re-run a peer question already in `archive/peer/`** — check there first (rule 5's exception to rule 4).
6. **`-Dual` is for FAILED-PREDICTION reviews only** (`CLAUDE.md:554`) — never `-Kind fact`, prose or ingest.

## Done means

- Both arms of step 1's review archived and classified.
- Step 2's op has read a live instance; the fixture resolves through the new op; the d10 hop count is recorded;
  the two bad-input refusals are shown. **Verification level stated explicitly** (structural vs functional).
- `py tools/doc_lint.py` shows no NEW fail (L6's undisposed archived reviews are pre-existing — STATUS OPEN 42).

## Standing above this cycle

**OPEN 32 — the second consecutive outcome review returned six `OUTCOME-VIOLATION`s.** THE GAP is unchanged:
174 ops, 123 recipes, 235+ peers, zero runnable experimental VIs. It is not answerable by a device and not by
this plan; it is what the user is owed when the P1 sequence reaches them.
