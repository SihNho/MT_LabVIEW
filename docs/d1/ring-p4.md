---
type: decision
kind: topic
status: current
date: 2026-10-02
parent: docs/d1/INDEX.md
tags: [d1, ring-buffer, p4, tracking-loop, pre-decided]
---

# Ring buffer P4 (tracking loop 1.2) — decisions from 268 on

Scope: loop 1.2's reader (`last` register, smallest `Num > last`, seqlock n1 == n2 >= 0, jump to `Latest` on an
overwrite, 1 ms own wait; PD238(e) `docs/d1-loop12-17-split-plan.md:2258`), and P5/P6 until they get their own
file. Carries from the frozen plan: size P4 with the memory formula of PD266(b) before planning (:2946); re-check
PD237(g) (`#10068`/`#29240` into 1.2, :2229) when P4 is planned.

How to add: see the 5-line note at the top of `docs/d1/INDEX.md`.

## Pre-decided

(none yet — the first P4 decision written here takes the next free number, 268 or above)
