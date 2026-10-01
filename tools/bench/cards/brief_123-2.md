# Brief for card 123-2 — OFFLINE prep of ring P3 (cycle 123 judgement, 2026-10-01)

P3 = the camera-loop rows of the ring buffer. Design of record: `docs/ring-buffer-design.md` as amended by
`docs/d1-loop12-17-split-plan.md` Pre-decided **238(b)(c)(d)(i)**, **241(d)**, **242(c)**. In short, loop 1.1, per NEW
BufNum only: `Num(i) = -1` → `IMAQ Copy` (Src = `#6810` Image Out `t6865`, Dst = pool image `i`) → per-slot values at `i`
(`#30117` trans pos, `#4580` rot pos, `#637` frame index) → `Num(i) = BufNum` → `Latest = BufNum`; `i` = the camera loop's
own count of NEW frames mod 20; a duplicate BufNum is skipped before any slot is touched; loop 1.1 gets `Wait (ms)` = 1
with no data dependency on the frame path; order by data dependency (error chain / sequence), never by timing. The 20
pool refnums leave For `#23093` through a NEW indexing output tunnel and route `nested` into loop 1.1.

This card runs beside card 123-1 (the P2b launch, LabVIEW). It touches no LabVIEW.

## STEP 1 — facts from files only → `tools/bench/facts_c123_p3.json`
- (a) Image Type: the source of the Image Type input of `IMAQ Create #20436` and of the `IMAQ Create` inside For
  `#23093` — uid, class, and whether it is the same object or wire. A value only if a file records it (cite file:line).
  (Card 123-1 reads the values in LabVIEW; this step records what the graph files already say.)
- (b) For `#23093`: its tunnels today, and which verb/op would create a NEW indexing output tunnel for the 20 pool refnums
  and route it into loop 1.1; what `tools/bench/opmodels/` records about the tunnel's indexing mode.
- (c) Loop 1.1's diagram uid, and every terminal P3 binds to, found in the P2b sim END graph
  (`tools/bench/sim/ring_p2b/step_10_create.json`, confirm against `summary.json` that it is the final step):
  `#6810` BufNum (w3747), Image Out (t6865), error out (w653); `#30117` Value; `#4580` Value; `#637` i; the five P2b
  indicators by label. Each with file:line. Start from `facts_c122_p3.json` / `facts_c122_p3_rows.md`; do not re-derive
  what they already state.

## STEP 2 — routes
`py tools/protocol.py requires` (write a scratch card for it if needed) on every op / verb / route P3 needs: shift
register, case structure, flat sequence, local variable bound to an indicator by label (read and write), `IMAQ Copy`,
`Index Array`, `Replace Array Subset`, a comparison node, `Increment`, `Quotient & Remainder`, `Wait (ms)`, numeric
constants, the For exit tunnel. Each PRESENT (file:line) or MISSING.

## STEP 3 — `tools/bench/ring_p3_steps.md` (one page)
P3's sub-steps: rows per step (≤ 15; ≤ 25 only where `stage_prerun --prerun` X14 reports the pattern proven), the saved
file name and the pass criterion of each. **Cap:** CLAUDE.md "AT MOST 6 CONSECUTIVE BROKEN INTERMEDIATES" — P2b is 1 of 6
and P6 must be the first run, so P3 takes AT MOST 2 steps (P4 and P5 need the rest).
Every choice NOT fixed by PD238/240–242 is an `ASSUMPTION:` line with its alternatives — at least:
- how the order `Num(i) = -1` → copy + per-slot values → `Num(i) = BufNum` → `Latest` is enforced;
- a shift-register master copy in loop 1.1 vs. a local-variable read-modify-write for the per-slot arrays;
- where the duplicate-BufNum register and the new-frame counter live, and their initial values.
These are for the judgement session. Do not decide them; proceed under the assumption you mark.

## STEP 4 — P3a plan and recipe (only if STEP 2 found every route P3a needs)
- `tools/bench/plan_ring_p3a.json` on the PROVISIONAL base: `base` = `{path: <P2b sim end graph>, md5, "provisional": true,
  "sim_of": {"plan": "tools/bench/plan_ring_p2b.json", "md5": "ce18e794994b94b251d76cb2c828ef7b"}}`; stagesim FINAL.
- `tools/recipes/stage_d1_ring_p3a.py` ≤ 120 lines on stagekit. dry + prerun PASS.
- The census prediction file says, per create class, whether the number comes from a MEASURED opmodel sample (cite it)
  or is NOT measured. Never present a hand-typed number as measured (cycle-123 decision,
  `docs/violation-decisions.md`, inference-over-measurement 2026-10-01 13:56).

## STEP 5 — prior-art
Prior-art review of the P3a recipe (`prior_art_review.py`); record the verdict and any release in the review file.

## Stop rule
A MISSING route that P3a needs ends the card after STEP 3; the missing list is the result.

## Rules
- No LabVIEW, no GUI, no hardware. A fact that contradicts PD238/240–242 is returned as OPEN.
- Do not edit gate or build code (`tools/stage_prerun.py`, `tools/stagekit.py`, `tools/stagexec.py`, `tools/stagesim.py`,
  `tools/gscript.py`, `tools/hooks/**`) while card 123-1 is live. A gate that refuses wrongly is logged with
  `py tools/gate_fp.py log ...`.
- STEPS 1–3 before any dry/prerun run. A provisional plan is never launched.
- Return at the first unexpected result.
