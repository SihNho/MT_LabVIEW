---
type: facts
status: current
date: 2026-10-02
tags: [card-139-4, ring-p4, v12, route-check, offline]
---
# Card 139-4 facts (offline only; LabVIEW NOT opened, no scratch run: returned at pass 2 per the card's "else return")
Maker `tools/bench/prep_c139_4_mkv12.py` -> `tools/bench/prep_c139_4_mkv12.log` (BGRUN END rc=1 after 263 s, 19 pass / 2 fail).
Outputs: `plan_ring_p4_v12.json` 831d899b, `plan_ring_p4_v12_in.json` 12791a33, `plan_ring_p4_v12_recipe_gates.json` e8f601c4.
## 1. v12 = v11 e398c447 with two edits (mkv12.log:9-12)
- KSF1 `p4_c_stopall_f`: donor DonorBoolF_v0.vi (md5 2346e9d8) uid 0 SENTINEL -> **126** (PD315(a)).
- `p4_w_last_gt` (wire_sr LeftIn SL1L.inner -> GT2.y) MOVED from #83 to #53, just before the `p4_t_last` group (now #54-56),
  so SL1L.inner is already wired when the group runs. Every other action identical, same relative order.
## 2. Replay / compile / routes (mkv12.log:376-391)
- Replay END 186 steps; per-step cdiff == v11 at every shared id (0 differ); end cdiff == v11's 24; fs_routes regenerated, ids == v11's.
- compile_plan 167 ops (== v11); route compare v11 -> v12: 0 differing ops (route of an op is unchanged by the move).
- Route check: `p4_w_last_gt` = wire_sr:LeftIn, `p4_t_last` group = **cfw** (the p4_t_n1 form), both addressed (:387-388).
  UNROUTABLE v11 {p4_t_last, _in, _out, p4_w_stop12} -> v12 {**p4_w_stop12**} (:389).
## 3. Gate failures
- FAIL :14 — the move crosses the meta step cut: p4_w_last_gt was meta step 3, p4_t_last is step 2 (step 2 +1 action, step 3 -1).
- FAIL :391 — card pass 2 (0 UNROUTABLE): `p4_w_stop12` still "ADDRESS: node #23166 not in Diagram[122] (#23166).Nodes[]" (:386).
## 4. Why p4_w_stop12 cannot take the p4_w_or_cond form without a tool edit (read, not run)
- The cond terminal t23246 of base While #10170 is a graph row owned by Diagram #23166 (owner_class 'Diagram', wire 23310;
  prep_c139_4_probe.log:5), so any connect addressing it looks for node #23166 in Diagram #23166's Nodes[] (stagexec.py:1603-1609).
- The W1 form `dst "new:W1.cond"` compiles to kind `stop` (OpStopFromNode_v0, addresses the loop by index, not the sink) ONLY when
  the head is a While THIS plan created: stagexec.py:719-720 (`created[ds] == "while"`), check_symbols :483-485, and the simulator's
  `cond_target` requires a `new:` head (stagesim.py:1364). LVBackend.stop itself takes any loop uid (stagexec.py:2852-2873).
- So a base-loop stop needs compile_plan + stagesim to accept e.g. `{uid: 10170, term: "cond"}`; the card forbids tools/*.py edits.
## 5. Not done (depend on pass 2): step-1 plan + recipe `stage_d1_ring_p4s1.py`, dry/prerun/X10, scratch run, Error List read.
Bed `D1_ring_p3b2b_20261002_130007.vi` never opened. Classes covered by a scratch: none (no run).
OPEN: p4_w_stop12 needs a base-loop `.cond` -> `stop` route in stagexec.compile_plan/check_symbols and stagesim.cond_target (a tool
card), and is the p4_w_last_gt move across the meta step 3 -> 2 cut acceptable (or should step 2/3 be re-cut)?
