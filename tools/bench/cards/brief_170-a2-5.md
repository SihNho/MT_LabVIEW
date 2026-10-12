---
card: 170-a2-5
status: current
date: 2026-10-13
---
# Brief 170-a2-5 (assignment 170-2, the ONE retry of 170-a2-3) - build the paced stand-in pair: release the two launch gates the sanctioned way

Read first: `tools/bench/cards/brief_170-a2-3.md` (the build, UNCHANGED), `tools/bench/cards/result_170-a2-3.json` (BLOCKED), `tools/bench/diag_c170_a2_3_facts.md`.
What happened: the recipe `tools/recipes/stage_replay_paced60.py` (9a465ed7) and its plan/graph exist and the dry ran (PASS-UNVERIFIED, 9 stub-only gates). No paced file was built. Two launch gates refused:
1. `check_launch` PD287(a): the stub-only gates must be NAMED in the bound card. This card names them in `rules` ("DRY-UNVERIFIED-OK: A1; A2; A3; A4; B1; G2; C1; C2") and the launch passes
   `--unverified-card tools/bench/cards/task_170-a2-5.json` (precedent: `task_169-a1-1.json`, `task_169-a1-2.json:95`). Use the label prefixes the dry printed (`diag_c170_a2_3_dry.log:122`); do not relabel a refused gate as a row.
2. Prerun X10 UNMEASURED (`diag_c170_a2_3_prerun.log:44`): the recipe edits through direct `gscript` calls (`create_const_loop_term`, `save`), so X10 has no plan to model. DO NOT edit `stage_prerun.py` or any hook.
   The levers that exist and are allowed here, in this order, stop at the first that makes `py tools/stage_prerun.py --prerun tools/recipes/stage_replay_paced60.py` PASS on the model AS IS:
   (a) route the edits through the machinery X10 models (`stage_prerun.py:68-75`: `Stage._op` ops counted in the dry trace + `load_by_vi[input md5]`), which is what `stage_d1_m4b.py`'s `from_decision` rows do;
   (b) if the model lacks the opened VI's load, ONE `load_by_vi` entry in `tools/bench/memory_model.json` for the md5 it names, from a MEASURED MEM-after-load line (the precedent: `task_169-a1-1.json` rule "ONE load_by_vi entry only"; `memory_model.json:38-`). Measure it by the build's own first read or a one-open read-only session, say which; touch nothing else in the model; quote its new md5.
   If neither makes X10 PASS: RETURN BLOCKED with the verdict text. No model limit edit, no gate-to-row change, no bypass variable.
The build itself, gates and hygiene are exactly `brief_170-a2-3.md` steps 1-6 (ExecState 1 warm AND cold for both files, census checks, inputs a89dafc1 / 842ecad9 unchanged, refs balanced, `tasklist` shows no LabVIEW, 8 pinned VIs unchanged).

## Not in this card
No P6 replay copy, no plan literal, no leg, no compare, no hook/stage-tool/plan/STATUS edit. A new unexpected result = RETURN with the facts (the retry is spent).
