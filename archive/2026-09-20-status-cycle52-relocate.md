---
type: archive
status: archived
date: 2026-09-20
tags: [status, relocation, cycle52]
---

# Cycle 52's relocation — the NEXT section cycle 50 wrote, moved here VERBATIM (rule 4)

Cycle 52 accepted D1 stage S2 and rewrote `STATUS.md`'s `## NEXT`. Nothing below is rewritten; it is the previous
NEXT body, kept for the record. What superseded it: `docs/cycle27-plan.md` Pre-decided **36** (the queue donor must
be a NODE; "use a constant" and "use a front-panel control" are measured unexecutable) and **37** (S2 delivered;
`move_in` is one node per call and severs every wire; a Wire count can never detect a cut; S3 = the whole 1.5 set,
atomic).

## §1 — the NEXT section as cycle 50 left it (STATUS.md:56-65, 2026-09-20 03:2x)

🎉 **S2's LEGALITY IS SETTLED BY MEASUREMENT — cycle 49's "S2 CANNOT END LEGAL" IS FALSIFIED.** Cycle 50 ran the discriminating test on a scratch copy of the S1 artefact (`tools/bench/diag_s2_scaffold.py` → `tools/bench/diag_s2_scaffold.log`, `tools/bench/diag_s2_scaffold.json`, 13 pass / 1 fail, the FAIL being the expected reading): one new While loop on `Diagram #686` scaffolded by `OpCreateEqual_v0` (both operands from ONE scalar output) → `OpStopFromNode_v0` reads **ExecState 1** and **SAVES** — `claudeDev\DIAG_s2scaffold_030829.vi`, md5 `eddb3e15e5b0aa673fc2bf59eadd67e2`, 475,422 B, re-read in a fresh process COLD 1 / PRELOADED 1. After `move_in #48` the same copy reads **ExecState 0** and the save is refused. ORIGINAL md5 `2a78e17c449cacdaf5da389818526859` unchanged; refs 8 opened / 8 closed / 0 live; no VI was run.

🔴 **FIRST ACT — BUILD S2 AS `docs/cycle27-plan.md` Pre-decided 34 NOW DEFINES IT: three While loops on `Diagram #686`, each scaffolded, saved as `claudeDev\D1_s2_loops.vi`. NO `move_in`, NO queues, NO re-wiring.** Contract: Diagram 170 → 173 · WhileLoop 3 → 6 · SubVI 97 → 97 unchanged · Comparison +3 · all three conditional terminals wired and read back by uid. Start from `claudeDev\D1_s1_copy.vi` (md5 `3e3d23cefd3a334001aa9d6156bf1aee`), gate on it, and copy the proven shape out of `tools/bench/diag_s2_scaffold.py` — four op calls per loop, already measured. Keep the script SHORT: the 1956-line `tools/recipes/stage_d1_s2.py` is RETIRED (34(i)) and must not be re-armed, edited or reviewed again.

🔴 **THE SCAFFOLD OPERAND IS PICKED BY NAME FROM A MEASURED SCALAR, NEVER BY ORDINAL (34(c)).** The one that worked is `#8486 x+1` on `Diagram #686`, first attempt, no op error. The pre-selected `#637 'frame index'` did NOT work: `#637`'s outer feed is an UNNAMED tunnel (`out_name ''`), so a name read from a wire table is not automatically a `src_name`. Take operands from the diagram's own output-terminal census, as the diagnostic does.

🔴 **SECOND ACT — THE QUEUE `src_name` RESOLUTION TABLE (34(g)): a DOCUMENT, zero LabVIEW.** The element types ARE on file, but SIX OF EIGHT queues have no `(node, named output terminal)` that exists on this copy at the moment their `Obtain` is placed. Write that table — uid · exact terminal name · diagram · or the stage that must run first — into `docs/d1-build-plan.md` §9, and record there that `Q_focusback` is **1 DBL**, which resolves the Bool-vs-DBL contradiction against `docs/cycle15-plan.md:122`. Owed before the sentinel stages, not before S2.

🟡 **AFTER S2 THE CHAIN IS ONE NODE PER STAGE, AND MOVE + RE-WIRE IS ATOMIC** (34(e), now measured): a moved node lands unwired, so a stage that moves one must also re-wire it before it can save. Order `#48` (7 cut rows) → `#376` (12) → `#5058` (13); all 109 cut terminals are already resolved in `tools/bench/d1_rewire_sources.json`.

🔴 **EVERY ADDRESS IS A uid OR AN EXACT NAME, RE-READ IMMEDIATELY BEFORE USE (34(h)).** Address invalidation by self-mutation is the strongest rival explanation for the ten v3→v7 deaths. "Resolve every name up front" is sound for NAMES and unsound for INDICES; they are not the same instruction.

🔴 **NO INTERMEDIATE ARTEFACT IS EVER RUN** (34(f)) — a scaffolded loop runs once, a sentinel loop with no producer blocks forever. Both are legal to SAVE; neither is legal to RUN.

🔴 **No new op, no new device** (Pre-decided 2; user 2026-09-18 08:53). **The retrospective is the LAST thing a session runs**, in the background: `py tools/bgrun.py --max-min 20 --log tools/bench/retro.log -- py tools/retrospective.py --cycle <N>`. Never run one early and never pay a previous cycle's retro debt up front (OPEN 54(a)).

🟡 **Two `doc_lint` items left open deliberately**: `L6`'s 48 blank dispositions are ALL pre-2026-09-15 — the three reviews of 2026-09-20 are disposed; `L2b` `docs/NAMES.md:1022` points past the end of `docs/toolkit-capabilities.md`. Neither gates anything.

💬 **FOR THE USER — two cost facts, not faults.** (1) Judgement-session spend dominates peer/review spend about 8 : 1 and `audit_cycle`'s C4 bucket understates it roughly 7×: cycle 49's real session cost was **$61.07** (`tools/bench/cycle_runner.log:62`) against an audited $9.54. (2) Cycle 49 spent two paid prior-art rounds on a recipe this cycle retired unlaunched; the measured route that replaced it cost one $3.36 review plus a 246 s diagnostic. Only you can act on the first; the second is already closed by 34(i).

## §2 — what cycle 52 measured against it

- The FIRST ACT **ran** (cycle 51, `tools/recipes/stage_d1_s2_loops.py`) and its artefact is accepted: Pre-decided
  37(a). The run itself was killed at 03:55 by the session exit before its post-save gates — OPEN 54(b), the second
  recurrence.
- The SECOND ACT (the queue resolution table) was written by cycle 51 into `docs/d1-build-plan.md:560-616`, and
  Pre-decided 35 was added on top of it. Cycle 52 then measured that the shapes it assumed available are refused:
  Pre-decided 36(a).
- "AFTER S2 THE CHAIN IS ONE NODE PER STAGE" is **superseded by 37(g)**: `move_in` severs every wire on the moved
  node in either order, so the 1.5 node set has no smaller legal unit than itself.
