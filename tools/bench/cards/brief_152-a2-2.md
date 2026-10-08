---
card: 152-a2-2
status: current
date: 2026-10-09
---
# Brief 152-a2-2 - P4 session 9 MADE (not run) on the REAL s08 graph + the measured FS owner read; OFFLINE (docs/d1/ring-p4d.md PD368(d)(e), PD365(d), PD366)

Why: card 151-a3-2 RETURNED at brief step 3 (the simulator refused v18 op 185, FS #29721 unmeasured). Card 152-a1-1 measured the owner (Diagram #23166, echo 29721) and wrote the derived graph
`tools/bench/graph_ring_p4s08_20261009_033522_fsowner.json` e26b4d90; card 152-a2-1 taught `stagesim.py` (now c24bd39a) to use it (`diag_c152_a2_1_facts.md`: `_diag_chain(#29869)` = [29869, 23166, 686, 536] on the derived graph).
This card is `brief_151-a3-2.md` again with the changes below. Read that brief first, then `diag_c151_a3_2_facts.md` (what the maker already did: cut = whole remainder = v18 actions 197..202 = ops 185..190, START 595.0, X10 MAIN 638.4, margin 41.6).

## Changes against brief_151-a3-2.md
1. **Copies:** `prep_c151_a3_2_mk.py` (+ `_probe.py`, `_check.py`) -> `prep_c152_a2_2_*`; the pred / licence / check of `prep_c150_a3_6_*` -> `prep_c152_a2_2_*` (names, pins, paths only; say which lines changed).
   The REALSIM base graph becomes the DERIVED file e26b4d90 (the only graph path that changes). Graph 44858dbf is not rewritten and not edited.
2. **Discriminator FIRST (PD368(d), before the maker writes a plan):** quote (i) the measured diagram of FS #29721 = Diagram #23166 (`diag_c152_a1_1_owner.log:25`), and (ii) the diagram the v18 plan's own create action for that Flat Sequence targeted, after rebind
   (find the create action / the s0x creation map entry for the FS and its target diagram uid; if the target is a symbolic id, resolve it through the creation map and the rebase table, quoting each hop). Equal => go on. Different, or (ii) cannot be resolved from files => **RETURN** with both values; s09 is not made.
3. **Cut:** as before - whole remainder if X10 <= 680 (margin 41.6 expected); quote START, margins and the +13.6 / +21.4 MB sensitivities as numbers only (PD367(c): no start-term recalibration).
4. **Rebase** onto the real s08 graph (`stage_prerun --rebase`, the s07 form `prep_c150_a3_6_rebase.log`) -> `tools/bench/plan_ring_p4_s09v18.json`. The simulator must now accept ops 185..190. If it still refuses one: RETURN with the refusal verbatim (file:line), the op, the rows of FS #29721. No `stagesim.py` or any other stage-tool edit.
5. **Pred (V18E-R', PD366(c))** with EL base = s08's **46**; `elrule.predict` WITH carry {4538, 29843, 29879, 30002, 2626}: first run it for the s08 plan and quote whether it gives 46 (quoted, not a gate, PD354(a)); pass the carry in the s09 pred if it reproduces 46, else pass none and quote both totals.
6. **Recipes** `tools/recipes/stage_d1_ring_p4_s09v18.py` + `_scratch.py` (copies of the s08 pair, names/pins only); sink gate per `wire_indicators` census row read by script (zero allowed); licence by script (PD365(d)); X11 `--buildarray-check`; dry + prerun on FINAL bytes of plan + both recipes;
   `--scratch-required` rc and `--check-launch` of the scratch recipe quoted. NOT launched.
7. **Invariants md5 before = after:** stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun c739eb86, vigraph 13be0847, **stagesim c24bd39a (new pin)**, errorlist_check 2b466a89, s08 VI f99e8414, graph 44858dbf, derived e26b4d90, s07 graph 71935a84,
   s08 plan/pred/licence/recipes (c328fdaf, cf2eccbf, 6b978d9e, ca5a5478, 7cab5049), memory_model a28b6dd7, `selftest_c152_fsowner.py` 64918ff7. No LabVIEW process before or after. No file under tools/hooks edited.
   A gate that refuses your OWN prep command text is a false positive: `py tools/gate_fp.py log` and go on, or name it in OPEN; never an env bypass.

## Report `tools/bench/diag_c152_a2_2_facts.md` (<= 45 lines)
Discriminator (both values, every hop); cut + margins + sensitivities; rebase rc + simulator outcome on 185..190; pred checks + carry measurement; licence entries; sink-gate census; X11; dry / prerun / scratch-required / check-launch numbers; invariants; `OPEN:` line. Facts only; a result-dependent action is not yours (RETURN with the facts).
