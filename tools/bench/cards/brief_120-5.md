# brief 120-5 — QRT-W step-split page + step A0 plan (OFFLINE PREP, PD237)

`labview: none`. Base graph = the REAL pool bed dump `tools/bench/graph_qrt_pool_20260928.json` (md5 `d265b283…`), so
A0's plan is NOT provisional. Decisions in force: `docs/d1-loop12-17-split-plan.md` PD237 (a)–(h) as amended by (j)–(m),
plus 233(g) and 236. Apply them; anything they do not settle goes to OPEN (≤ 3), it is not decided here.

## Part P — the step-split page `docs/qrtw-plan.md` (frontmatter `type: plan`, `status: draft`)
- Every QRT-W row on the pool graph, grouped into steps A0 → A → B1 → B2 → C → OV (PD237(h)); ≤ 15 rows per step
  (25 only where `stage_prerun` reports a proven pattern — say which). Rows re-derived from `tools/bench/qrtw_rows_draft.json`
  (uids re-checked by 120-1 G7: unchanged) with the PD237 carriers: `Q_work` = image refnums (pool), `Q_f1..Q_f5`,
  `Q_r0`, `Q_r1` lock-stepped; IMAQ Copy (c); buffer return by the count-1 For loop (k); Case on `Dequeue(Q_free)`
  `timed out?` in A, filled by OV (f); Q&R MOVE in B2 (g); b2_03 + t11273 together in B1 (227(d)).
- Per step: the routes it uses (existing file:line, or "120-3/120-4 route"), the saved file name
  `claudeDev\D1_qrtw_<step>_<ts>.vi`, and its gates. Every `nested`-route row carries the stray-Invoke removal and the
  node-census gate (PD237(m)). OV's rows carry `"user_decision": "D-2026-09-28-01"`.

## Part A0 — the first build step, planned to launch-ready (no launch in this card)
- Rows: 7 new `Obtain Queue` on `686` outside the loops (`Q_f1` DBL, `Q_f2` DBL, `Q_f3` I32, `Q_f4` U32,
  `Q_f5` Cluster{DBL[],DBL[]}, `Q_r0` DBL[], `Q_r1` I32; types from `tools/bench/facts_c120_types.json`), each with an
  exact-type donor constant on `686` and max size 20 (a shared I32 20 constant as in PD235(d) is fine), each
  `data_stream: true` with reason "per-frame values handed between loops, PD237(a)". Nothing else is wired in A0.
- Donor route per type: an existing route (file:line) that yields that exact type on `686`. If a type has no route,
  report it as a missing tool (name the type, the routes tried by grep), do not improvise.
- `tools/bench/plan_qrtw_a0.json` through stagesim FINAL; recipe `tools/recipes/stage_d1_qrtw_a0.py` ≤ 120 lines modelled on
  `tools/recipes/stage_d1_qrt_pool.py`, with gates: 7 Obtains present, each element type == its field's canonical type
  via `gscript.read_term_type`, max size 20, cdiff == the pool bed's 16 rows, only new objects' terminals change,
  Error List == 53 + the pinned count, handle gate per PD236(b); dry PASS; `stage_prerun --prerun` PASS; prior-art review
  dispatched and answered (`py tools/prior_art_review.py …`, peers flag `priorart`).
- The scratch run, the Error List pin and the ONE launch are a later LabVIEW card.
