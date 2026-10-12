---
card: 170-a2-3
status: current
date: 2026-10-13
---
# Brief 170-a2-3 (assignment 170-2) - PD410(d): build the paced stand-in pair under claudeDev\replay

Plan: `docs/d1/ring-p6.md` PD410(d) (lines 310-320). Why: unpaced, the P6 loop 1.1 would lap loop 1.2 on the replay stand-in; a 60 ms pace per fetched frame
(S1 took 29.4 ms per frame, `tools/bench/p6_replay_facts.md:131`) lets 1.2 read every frame. Pacing adds time only: no pixel, no computation changes.
LabVIEW build, no VI Run, no hardware. Originals: the two inputs below are claudeDev replay tools (not originals); they stay unchanged, the paced files are NEW files.

## Build (two new files, same folder `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\replay\`)
1. `replay_imaqdx_get_image_buf_paced60.vi` = a BYTE COPY of `replay_imaqdx_get_image_buf.vi` (md5 a89dafc1...) plus ONE `Wait (ms)` node whose input is a
   diagram constant 60 (U32, typed by the sink), with NO data wire to or from anything else (it runs beside the rest, so the call lasts >= 60 ms).
   Route (prior art, read it first): `stage_d1_m4b.py` / `decision_m4b.json` (Wait (ms) + constant row via `stagekit.from_decision`, `create_const_on_term`),
   the donor `OpWaitDonor_v0` (`facts_c100_oplabels.json` OpPrimCopyNested_v0 donors "Wait (ms)"), `stage_d1_ring_p3a.py`. Use a shared route; do NOT hand-write a new op.
2. `replay_get_buff_image_paced60.vi` = a BYTE COPY of `replay_get_buff_image.vi` (842ecad9...) whose inner call of `replay_imaqdx_get_image_buf.vi` is swapped to the paced
   file by `gscript.replace_object` (the verb `stage_replay_standins.py` section [G] used: census of callees before and after, wire-edge diff 0 after the uid remap, only that node changed).
3. Gates (each a real gate, stop at the first unexpected result): the input md5s equal before and after; paced buf ExecState 1 warm and COLD (fresh LabVIEW); census shows the
   Wait node and constant 60 present and no wire from/to the Wait node; paced get-buff ExecState 1 warm and COLD; its callee census = the 842ecad9 census with ONLY the buf callee replaced by the paced file;
   VI.Name of both has no library. Record md5 and size of both new files.
4. The recipe is a new `tools/recipes/stage_replay_paced60.py` (scope header `# labview: build` / `# hardware: none`, `RESULT {...}` line), under `bgrun --material`, calling shared functions
   (`docs/script-writing.md`; follow `stage_replay_standins.py` for the Stage/pins/close pattern). The recipe edit needs `flags.peers ["priorart"]` only if the card flags say so; this card has none: if
   guard_cycle refuses the recipe, RETURN BLOCKED with the text (no bypass).
5. Hygiene: no original opened; VI Server refs balanced (counter); `tasklist` shows no LabVIEW at the end; the 8 pinned VIs rehashed unchanged; only the 2 new .vi plus diag/recipe files written.
6. Facts `tools/bench/diag_c170_a2_3_facts.md` (<= 40 lines, every number with a file:line).

## Not in this card
No P6 replay copy, no plan literal, no leg, no compare, no hook/plan/STATUS edit. Failure = RETURN with the facts.
