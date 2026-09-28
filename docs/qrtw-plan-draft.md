---
type: plan
status: draft
date: 2026-09-28 11:10
card: 117-4
provisional_base: tools/bench/graph_l2r1_saved_20260928.json md5 e429f7ad7b2eebdaabaf0db1a462f10e (L2-R1 saved, D1_l2_r1_20260928_055441.vi md5 f465196b…)
rows: tools/bench/qrtw_rows_draft.json
tags: [d1, qrt, qrtw, draft]
---

# QRT-W — DRAFT row table and tool inventory (offline, card 117-4)

**Not a plan in force.** Written offline on the L2-R1 graph because L2-R2 is not saved; R2 deletes only the 13
consumer-less tunnels on `#637` (split plan 228(g)) and touches none of these rows (233(d)). Every uid must be re-read
on the R2 graph (`stage_prerun --rebase`) before use. Decided inputs: split plan **233(f)** (`docs/d1-loop12-17-split-plan.md:2132-2137`)
and **227(d)** (`:1999-2002`). Every other choice is listed under OPEN; none is taken here.

Measured by `tools/bench/diag_c117d_rows.py` → `tools/bench/diag_c117d_rows.log` (read-only; RESULT FAIL 25/4 — the 4
failing gates are the script's own contract: it gated `#644` and the three WhileLoops, which own no terminal rows in this
graph; the data lines are unaffected) and by greps of the graph file (lines quoted below).

## T1 — tool inventory

| thing | existing route (file:line) | stagexec plan route | verdict |
|---|---|---|---|
| Obtain Queue | `gscript.queue_node('obtain')` `tools/gscript.py:1262` → `OpQueueObtain_v0.vi` (claudeDev) | none — `CREATE_ROUTES` `tools/stagexec.py:198-208`, `create_route` `:276-304` | **MISSING in stagexec**; element-type donor must be a NODE with a named output (`docs/cycle27-plan.md:1037-1046`, 36(a)), never a `#637` outer terminal (`docs/d1-build-plan.md:608-615`, 35(a)) — no node on `#686` outputs a Q_work/Q_res cluster → **donor MISSING** |
| Enqueue Element | `queue_node('enqueue')` `gscript.py:1262` (`_QUEUE_OPS` `:1257`) | none | **MISSING in stagexec** |
| Dequeue Element | `queue_node('dequeue')` same | none | **MISSING in stagexec** |
| Release Queue | `queue_node('release')` same | none | **MISSING in stagexec** (and belongs to STOP, OPEN O7) |
| Bundle | no creator op; `stagekit.copy_in` `tools/stagekit.py:807` (route `copy_in`, `stagexec.py:206,298-299`; precondition work == `MOVE_DST`, `stagexec.py:253-254`) from a base Bundler | `copy_in` | 2-input: **exists** (`#11310` in 1.2, `#11608` in 1.1). 5/6-input: no base Bundler has that size (`#27660` 7, `#13793` 4, others 2 — graph grep); **resize MISSING** (no def matching resize/grow in gscript/stagekit/stagexec) |
| Unbundle | `copy_in` of `#11576` (Unbundler, 2 outputs, 1.1; graph term rows 11582/11585/11588) | `copy_in` | exists; output count adapting to the wired cluster is **INFERRED, unmeasured** |
| Quotient & Remainder | `copy_in` of `#10068`/`#29240`, or `stagekit.move_in` `stagekit.py:595` of the nodes themselves | `copy_in` / move row | exists. `create_primitive_nested` `gscript.py:4224` has donors for `Max & Min` and `Wait (ms)` only (`tools/bench/facts_c100_oplabels.json:257-273`) → primitive route **MISSING** for Q&R, Bundle, Unbundle, queue ops |
| constant on a body-node terminal (timeouts) | `const_on_term` `stagexec.py:207` → `stagekit.const_row` `stagekit.py:861` (OpCreateConstOnTerm_v0) | `const_on_term` | exists inside a WhileLoop body; **MISSING on Diagram `#686`** (1055 on a Diagram container, `cycle27-plan.md:1042-1044`) |
| wiring (all W rows) | `stagexec.connect_route` `stagexec.py:750`, created-node binding `bind_new` `:543` | `op:wire` | exists; proven (below) |

## T2 — payloads under 233(f)

**Q_work** (1.1 body 639 → 1.2 body 23166), one element per `#637` iteration:

| field | source (uid / term uid / name) | S1 wire | sinks in 1.2 | note |
|---|---|---|---|---|
| F0 image | `#6810` t6865 `Image Out` | w3040 | `#5058` t5089 `Image In` | IMAQ refnum (`d1-build-plan.md:572`); w3040 has no sink left in R1 (`diag_c117d_rows.log:16`) |
| F1 trans_pos | `#30117` t30145 `Value` | w30592 | `#2626` t4160 (S1 element\|1); `#9503` outer t9508 → `#28083` `Magnet position` | branch — w30592 still feeds `#20497` in 1.1 (`log:32`) |
| F2 rot_pos | `#4580` t4728 `Value` | w4878 | `#2626` t4165 (S1 element\|2) | no other sink in R1 (`log:39`) |
| F3 frame_i | `#637` i = term 644 (owner Diagram 639) | w3268 | Q&R ×2 `x`; Q_res R1 | 233(f)(2)/(3) |
| F4 x_minus_y | `#5119` t6323 `x-y` | w16483 | `#2626` t2832 (S1 element\|0) | **not in the card's list**; 233(f)'s rule covers it (a saved-row column). OPEN O4 |
| F5 wlc_cluster | `#11608` t11614 `output cluster` | w12256 | `#11261` t11273 `element` | 233(f) text: it meets `#11363`'s 1.2 data in Build Array `#11261`; `facts_c117_qrt.json:147` proposed a local. OPEN O3 |

Element→terminal mapping for `#2626` is from S1: t2832 ← `#5119`, t4160 ← `#30117`, t4165 ← `#4580`
(`tools/bench/diag_c117b_qrt.json:469-631`); R1 names all four inputs `array` (`diag_c117d_rows.log:79-82`).

**Q_res** (1.2 body 23166 → 1.7 body 23405): R0 = `#2626` t2813 `appended array` → `#376` t5754; R1 = F3 → `#376` t5763
`frame index` (`log:78,90,92`).

Rows: 14 create + 31 wire = **45** (`qrtw_rows_draft.json` `rows`). If all land, 12 of the 16 cdiff rows close by wire; the
4 `2626|array|0..3` rows are the rename artefact and have no row of their own.

## T3 — b2_03 with t11273 (227(d))

- b2_03 = **W17**: `#11363` outer t11369 → `#11261` t11270 `array` (1.2 → 1.2).
- t11273 = **W16**: fed by pair `(11261,'element')`, source `#11608` t11614 in 1.1 (S1 w12256), carried as **Q_work F5**
  if O3 = queue; otherwise by a latest-value local. Both rows sit in step **B1** (227(d): both inputs in one stage).
- Owed before B1 launches (`:2001`): the M1–M4 reads of card 113-3 on a byte copy. `#2626` shows the same symptom (all four
  inputs named `array` in R1) and should be read in the same pass (OPEN O9).
- The Q&R divisors are panel controls on `#686`: `# FD points` t8936 (w9000) and `# DT points` t28844 (w29006); in S1 they
  enter `#637` by tunnels `#10114` / `#29415` (graph term rows 10116/10119, 29417/29421).

## T4 — steps and proven_pattern

| step | rows | create | wire | proven today | budget |
|---|---:|---:|---:|---|---:|
| A — Q_work producer (686 + 639) | 13 | 5 | 8 | no | 15 |
| B1 — Q_work consumer + b2_03/t11273 (23166) | 11 | 2 | 9 | no | 15 |
| B2 — display remainders (23166) | 8 | 2 | 6 | no | 15 |
| C — Q_res (686 + 23166 + 23405) | 13 | 5 | 8 | no | 15 |

**Why none is proven:** no clean past stage run has an `op:create` in its pattern (`diag_c117d_rows.log:365-415`;
disp's clean runs have pattern `None`, `:393,396`, so they do not count). **Alternative split:** creates first (14 rows,
not proven), then the 31 wires in two wire-only steps; a wire-only recipe whose calls are a subset of
`stage_d1_l2b2a_r2` / `stage_d1_l2b2b_r2`'s pattern (`log:408,412`) is proven (≥ 2 other stages) → budget 25 each. A
move-in variant of O8 is covered only if its call set ⊆ `stage_d1_k_r2` and `stage_d1_l2b1_c110d` (`log:368,404`).

## T5 — OPEN (full list; judgement decides)

- **O5 (first) Image refnum without a pool.** F0 is an IMAQ image refnum. The designed carrier was `Q_free`/`Q_work`, a
  20-slot pool (`d1-build-plan.md:572`, `stage2-assembly-step-c.md:19-29`); R1 has no pool — `#6810` takes `Image In` from
  one tunnel (`#1666`, w1651, `log:15`). Queueing that one refnum lets 1.1 overwrite the buffer before 1.2 reads it, so
  1.2 could track a later frame than F1–F5 describe (a rule-1a question). Pool stage first, or another carrier? Bound 20
  and "full ⇒ skip this read" (`:572`) depend on the answer.
- **O1 Element shape.** 233(f) says "in the same queue element"; `d1-build-plan.md:567` says "no composite elements",
  lock-stepped queues, error-chained. Which one stands for Q_work/Q_res?
- **O2 Obtain donors.** A cluster donor must be a node on `#686` with a named output (36(a)); none exists. Build one
  (it must then be fully wired, 36(b) `cycle27-plan.md:1047-1049`), or a new obtain route?
- **O3** `#11608` → t11273: Q_work F5 (233(f) text) or a latest-value local (PD210, display-only sink)?
- **O4** `#5119 x-y` in Q_work (not in the card's list; needed for the saved row per 233(f)).
- **O6** Enqueue/Dequeue timeouts and `timed out?` handling; where the queue error chains go (RULE-CHAIN-S1 has no queue).
- **O7** Release order and the stop sentinel (STOP stage, split plan `:76`; `NAMES.md:912-913`: never run a `Dequeue(-1)`
  whose producer may produce nothing).
- **O8** Q&R in 1.2: copy `#10068`/`#29240`, or move them (their outputs have no other consumer in R1, `log:50,56`).
- **O9** `#2626`'s four inputs read `array` in R1 — same Concatenate Inputs question as `#11261`; include in M1–M4.
- **O10** `d1-build-plan.md:574,308` name Q_res/Q_good/Q_rmeta for `#376`; R1's `#376` has only two open inputs
  (`log:90,92`). Is §9's trio superseded by Q_res {row, i}?
- **O11** Bundle resize (5/6 inputs) is a missing tool (tools allowed since 2026-09-24): build it, or nest 2/4-input copies?
