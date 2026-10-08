---
card: 148-a3-3
status: current
date: 2026-10-08
---
# Brief 148-a3-3 - P4 session 7, PROVISIONAL prep beside the s06 scratch: plan, pred, recipes, dry + prerun - OFFLINE (docs/d1/ring-p4c.md PD356(f), PD358(f), PD360(d))

`labview: none`. Runs beside card 148-a2-4 (the s06 LabVIEW scratch). s07 = the v18 ops after s06's last op (s06 = v18 ops 115..135, see `tools/bench/diag_c147_a1_3_facts.md`). The s06 file does not exist as a real graph yet, so this card works on the PROVISIONAL base exactly as `brief_147-a1-2.md` did for s06 (maker `tools/bench/prep_c147_a1_2_mk.py`, and its real-graph successor `tools/bench/prep_c147_a1_3_mk.py` 8900e0df, both read-only models): base = stagesim's end of the s06 plan, X10 start = the s06 PREDICTED load (s06 scratch peak / end as predicted in `diag_c147_a1_3_facts.md`; quote the number and where it comes from).

## Do
1. Copy the maker to a card-local `tools/bench/prep_c148_a3_3_mk.py`; change only the base (s06 sim end instead of the s05 graph), start rule inputs, session and log names. Cut = longest group-respecting prefix of the remaining v18 ops whose MAIN-recipe prerun X10 <= 680.0 (the prerun's own line decides; no hand pick). Report cut, MAIN and scratch X10, margins to 680 and MEMSTOP 695, first op over 680, +-5 MB sensitivity. s07 sim end == v18 sim over the same ops (cdiff 0, else RETURN).
2. #2626 licence: say whether the cut contains any op that needs it (X11 PD352(d)); X11 must PASS (licensed or not needed). Do not extend a licence.
3. Pred EL by `tools/elrule.py` (a5ee7d5c, unchanged) from the s06 PREDICTED EL (`plan_ring_p4_s06v18_pred.json`, c4a6a35a) as start read; write `plan_ring_p4_s07v18_pred.json` following `prep_c146_a1_2_pred.py`; total and per-class.
4. New recipes `tools/recipes/stage_d1_ring_p4_s07v18.py` and `stage_d1_ring_p4_s07v18_scratch.py` = copies of the s06 pair (d947df5d / 31009bfc) with ONLY plan / pred / base / licence names and the sink-gate declaration list changed (declare sink gates only where the s07 ops need them; quote the file:line). Show the diff against the s06 pair by file:line.
5. Dry and prerun of both recipes (`--dry`, `--prerun ... --scratch-required` expected exit 3); quote each result line, counts and X10. Mark the plan files provisional (`plan.base.provisional`) as the rebase expects.
6. Protected md5 before/after (unchanged): stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun dcd45aba, the whole s06 plan/recipe tree (cfbd9823, c4a6a35a, db72d8af, d947df5d, 31009bfc), memory_model.json 88eeb037, s05 3f9ac26b, s04 95e408ff, s03 282301ca, bed 39511877.

## Never
Open LabVIEW or any `.vi`; touch `claudeDev`, `memory_model.json`, `adopted_scratch.jsonl`, `tools/bench/sim/ring_p4_s06v18/**` or any `diag_c148_a2_4*` file; edit a stage tool, hook or elrule; launch any plan; clear a refusal by editing the plan. If a stage tool must change, RETURN with the file:line and the exact refusal.

## Return (`tools/bench/diag_c148_a3_3_facts.md`, <= 40 lines)
Start rule numbers, cut, X10s, margins, licence status, pred total/per-class, recipe diffs, dry/prerun/`--scratch-required` lines, protected md5 before/after, new file md5s. `OPEN:` line.
