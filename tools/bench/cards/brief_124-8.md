# Brief for card 124-8 — retry of 124-7: declare measured terminal classes in the P3a plan, then scratch + ONE launch (cycle 124)

`tools/bench/cards/result_124-7.json` (FAIL 10/2): the scratch run of P3a stopped at op 1 (`create p3a_wait`, `Wait (ms)` from
`OpWaitDonor_v0` uid 163 → Function `#26747`) on a BINDING key: the simulator keyed its terminals `('Terminal', …)`, LabVIEW's
real table says `ParameterTerminal` (`tools/bench/stage_d1_ring_p3a_scratch_pin.log:65-71`). Cause on the plan side:
`plan_ring_p3a.json:28-37` declares `p3a_wait`'s terminals without `term_class`, and `stagesim.py:1317` defaults an undeclared
class to `Terminal`. Everything was clean afterwards (bed unchanged, scratch deleted, LabVIEW gone). Jev: `new-problem p=0.664` →
hypothesis review owed.

## Decision (judgement, cycle 124)
**Fix the PLAN, not the simulator default.** Every node the P3a plan CREATES (`Wait (ms)`, `Equal?`, `Increment`,
`Quotient & Remainder`, constants, the case) gets an explicit `term_class` on every terminal it declares, taken from a MEASURED
terminal table — this scratch log (`:65-67`), `tools/bench/diag_c124_p3a_scratch.log` (124-5's real `Equal?` / `Increment` /
`Quotient & Remainder` / case), or `tools/bench/diag_c123_routes.log:55,76` — each cited in the plan generator
(`tools/bench/plan_ring_p3a_make_v3.py` or its successor). If a created node's class is not measured anywhere, that is the first
unexpected result: return. `stagesim.py` is not edited (other plans rely on its default).

## Steps
0. The owed hypothesis review: `-Agent claude -Role hypothesis`, naming `stage_d1_ring_p3a_scratch_pin.log`, ATTACKING the claim
   above (cause = undeclared `term_class` on created-node terminals; fix = declare measured classes). ANSWERED before step 3.
   If it refutes the claim, return with its answer.
1. Regenerate the plan (`plan_ring_p3a.json`) with the classes; the predictions do not change (a class key changes no census).
   Simulate: FINAL, route check PASS.
2. Dry + prerun of `tools/recipes/stage_d1_ring_p3a.py` again (a failed run invalidated the records); `--scratch-required`.
3. Then `brief_124-7.md` steps 1–4 unchanged: scratch run via `tools/bench/stage_d1_ring_p3a_scratch.py` (census sample, MODEL
   lines corrected only), scratch Error List pin with `tools/bench/stage_d1_ring_p3a_el.py`, ONE launch →
   `claudeDev\D1_ring_p3a_<ts>.vi`, final Error List full read == pin, expected file reverdicts OK, LabVIEW gone.
The recipe file is edited ONLY if it pins the plan's md5 (then that one constant). Return at the first unexpected result.
