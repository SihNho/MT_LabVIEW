# Brief for card 110-2 (cycle 110 judgement, escalation rung 1 of card 110-1) — decisions, not yours to change

Card 110-1 (`tools/bench/cards/result_110-1.json`) FAILED 4/2 with its budget spent. Its G1 device PASSED and stays.
The plan `tools/bench/plan_l2b1.json` (md5 `cd553209…`), the split page `tools/bench/cards/split_plan_110.md` and the
recipe `tools/recipes/stage_d1_l2b1.py` (md5 `9671f90f…`) are your starting point. Brief 110-1 sections D and B still hold.

## J. Judgement on 110-1's three OPENs
1. **Indicators `#8323`/`#28786` and constants `#6404`/`#9050`/`#9906` MOVE into 1.2 in B1** — precedent PD182(a)
   (a constant whose consumers are all moved nodes moves with them) and PD182(b) (an indicator whose sole writer moves,
   with 0 Local readers, moves with it). Their wire rows join B1 **when both endpoints are node or control terminals**;
   a row with a ForLoop LoopTunnel endpoint (e.g. `29172→28786` if 29172 is a `#29874` tunnel) goes to B2. B1 stays ≤ 13 wires.
2. **No new tool in this card.** The stagexec LoopTunnel owner route and the stagesim flip_reg seeding (`#5058→#2765`)
   are B2's tools and get their own card. B1 carries none of those rows.
3. **Checkpoints = every op that creates or binds an object, DERIVED FROM THE PLAN** (not a hand-typed list), plus
   the recipe's existing ones. Fix the class: the recipe computes the checkpoint set from `plan_l2b1.json`.

## R. Order
1. The owed review for `tools/bench/plan_l2b1_dry.log` / `plan_l2b1_dry2.log` first: follow `material.md`'s JEV-LADDER
   procedure; if a hypothesis review is owed, ONE review card covering both (same script) via `peer.ps1 -ReviewCard`,
   ANSWERED and annotated before any further dry.
2. Re-finalize the plan with J1 (stagesim), fix the recipe (J3), top-level `--dry` + `--prerun` PASS with records,
   prior-art round on the changed recipe ANSWERED + annotated, `py -m pyflakes` on the recipe through the launch gate.
3. ONE launch → `claudeDev\D1_l2_b1_<ts>.vi` (gui_save; broken by design, ExecState 0 expected), end cdiff == the plan's
   open rows, input md5 unchanged, LabVIEW gone.
4. In the same card (PD223(a)): the new file's EXPLICIT expected Error List file
   `tools/bench/errorlist_expected_D1_l2_b1_<ts>.json` with a reverdict OK (0 extra, 0 missing), or the mismatch reported.
