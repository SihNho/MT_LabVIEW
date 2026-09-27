# Brief for card 110-3 (cycle 110 judgement) — continuation of 110-2 at the same rung; decisions, not yours to change

110-2 (`tools/bench/cards/result_110-2.json`) BLOCKED on my decision after dry 3 (`plan_l2b1_dry3.log:84-85`).
Briefs 110-1 (D, B) and 110-2 (J, R) still hold. Decided now:

1. **Re-cut B1: rows `rw_403_2282` (Z/dZ → Tunnel `#2276`) and `rw_9306_6142` (Correction Factor → SelectorTunnel
   `#6132`) move to B2**, with the LoopTunnel rows. B1 = 8 wires, 29 open pairs (your 110-2 fact 9). Update the split
   page's B1/B2 lines. The recipe derives rows/checkpoints/CTs from the plan, so its bytes should not change; if they
   must, say why.
2. **The lint criterion is dropped**: pyflakes is not installed (`diag_c110_pyflakes.log:3`) and installing it is a
   system change I do not authorise. Nothing replaces it in this card.
3. **Accepted for the B2 tooling card, NOT this card:** (a) the executor unions its required checkpoints itself;
   (b) stagesim finalize runs `connect_route` so an UNROUTABLE row fails at plan time; (c) the CT-source → structure
   tunnel face route; (d) the LoopTunnel owner route; (e) flip_reg seeding (`#5058→#2765`). Do not build them here.

Then: re-finalize (stagesim), top-level `--dry` + `--prerun` PASS with records, prior-art ANSWERED + annotated if the
gate asks for it, ONE launch → `claudeDev\D1_l2_b1_<ts>.vi`, and the explicit expected Error List file with a reverdict
(110-2 brief R3–R4).
