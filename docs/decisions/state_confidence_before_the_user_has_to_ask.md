---
name: state-confidence-before-the-user-has-to-ask
description: "Label every claim's confidence and its evidence when first stated — the user's complaint is not that I am wrong, it is that my story keeps changing because I report intermediate steps as findings"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 7b982769-ee4e-45be-8846-85edbec23e37
  modified: 2026-09-13T22:03:12.018Z
type: decision
status: in-force
date: 2026-09-13
source: memory/state_confidence_before_the_user_has_to_ask.md
---

# Say how sure you are the FIRST time, not after being challenged

On 2026-09-13/14 the user asked, flatly: *"말이 왜 또 바뀌는거야"* — why does your story keep changing again?

It was a fair count. In one night I asserted and then withdrew:

- `Baseline Startpoint` "is" the rotor's zero (the premise it rested on was falsified by one search);
- the VI's four port strings "are" per-room configuration pairs (they were stale ring labels from another machine);
- `Configure.vi` / `SetCommand.vi` belong to the ASI and PI libraries (both are Autonics — `instr.lib` said so);
- a private method ID "sprays ~67 nodes" (a total object count misread as a delta);
- "private members cannot be attached by script" — **three times**, every one void because the *reader* had
  failed, not the attempt;
- "everything is blocked on reading node labels" (nothing was blocked; terminal names already identify a subVI,
  a trick I was using elsewhere in the same session).

## The defect is not being wrong. It is claiming more confidence than the evidence carries.

Retracting when challenged is correct and I did it each time. But the retraction is only necessary because the
first statement was made at full confidence. What was actually happening was **narrating intermediate steps as
findings**: a probe result is not a finding until its control passes and a competing explanation has been ruled
out; a string extracted from a binary is a hint, not a fact; a peer's hypothesis is a hypothesis even when it is
well argued and well cited.

The cost lands on the user. They cannot tell which sentences to build on, so they have to challenge everything —
and when they do, the claim collapses, which teaches them to trust none of it.

## What to do instead

1. **Every claim carries its evidence and its level, in the same sentence it is first made.** Measured on the
   machine / stated by the user / read from vendor documentation / inferred — and inferred is said out loud.
   "The terminal is named `Baseline Startpoint` and its default is 200.0" is a measurement. "So it is the zero"
   is an inference and must be written as one.
2. **A probe without a passing control concludes nothing.** Say "inconclusive" and leave it inconclusive. Three
   times in one night the honest answer was "my reader failed", and three times the first draft said something
   much stronger.
3. **Prefer "I do not know yet" to a confident wrong answer**, especially when the user is relying on the
   project to hold knowledge they no longer remember. A hedge costs one sentence; a retraction costs their trust
   in everything nearby.
4. **A change of plan is a plan, and plans get peer-reviewed.** I launched a 74-minute sweep on a fresh idea
   without review. The failed-prediction gate did not catch it, because nothing had *failed* — I had simply
   changed direction, which is exactly when a fresh idea is least examined.
