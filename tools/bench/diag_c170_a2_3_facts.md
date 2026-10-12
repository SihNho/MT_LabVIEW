---
type: facts
status: current
date: 2026-10-13
card: 170-a3-1 (retry of 170-a2-3)
---
# Cards 170-a2-3 / 170-a3-1 - paced stand-in pair (PD410(d), PD411(b)): BUILT, 31/0

## What ran (card 170-a3-1)
| step | log | result |
|---|---|---|
| re-hash of the 11 pinned inputs (offline, stagekit.md5) | `tools/bench/diag_c170_a3_1_rehash.log:3-14` | PASS 11/0, no drift |
| lever (a): edits moved onto Stage._op (`op()`, stage_replay_paced60.py:49-58); --dry | `tools/bench/diag_c170_a3_1_dry.log:35` | PASS-UNVERIFIED, same 9 labels; 4 ops recorded (:10,:11,:20,:22) |
| --prerun after (a) alone | `tools/bench/diag_c170_a3_1_prerun_a.log:48` | FAIL 14/1: X10 "opened VI load unmeasured (md5 a89dafc1... not in memory_model load_by_vi)" |
| one-open read-only load measurement (lever (b)) | `tools/bench/diag_c170_a3_1_load.log:18` | MEM after load 550.3 MB private; 11/0, scratch deleted (:27), LabVIEW gone (:34) |
| --prerun after (b) | `tools/bench/diag_c170_a3_1_prerun.log:55` | PASS 15/0 |
| prior-art review (guard_cycle asked for it) | `tools/bench/priorart_c170-paced60.log`, `archive/peer/2026-10-13-priorart-c170-paced60.md` | novel, no blocking verdict |
| build launch (--unverified-card task_170-a3-1.json) | `tools/bench/launch_c170_paced60.log:123` | PASS 31/0, rc 0 after 585 s (:124) |

## Facts
- X10 verdict, verbatim (`diag_c170_a3_1_prerun.log:51`): "PASS  X10 predicted LabVIEW private MB <= model fail_above_mb, from the compiled
  plan + checkpoint set (peak 607.0 MB)"; model: N 4 ops, R 11 reads, start 556.2 = 550.3 + op-0 5.9 (:48-49).
- memory_model.json: ONE new load_by_vi key a89dafc1db03feef7b528f0dd4fcc692 = 550.3 MB (cite `diag_c170_a3_1_load.log:18`); nothing
  else changed (git diff: 5 added lines, 0 removed); new md5 464bed2528992746d7a515e4354e45f9. No 842ecad9 entry (X10 did not need it).
- Lever (a) caveat: diag_replay_lib.copy_to is counted as ONE op although it runs junk_purge inside it; `op()` re-raises what the call raised.
- Paced buf `claudeDev\replay\replay_imaqdx_get_image_buf_paced60.vi`: md5 e40ec86722948812d155d6e4047a3ef9, 38428 B (launch log :64).
  Wait #642 copied from donor #163 (:39); const #660 = 60 on 'milliseconds to wait' (:50); only edge const -> Wait, none removed (:52);
  census Function 3->4, Constant 7->8, Wire 16->17 (:53); ExecState 1 warm (:55) and COLD (:78); cold const text '60' (:82).
- Paced get-buff `claudeDev\replay\replay_get_buff_image_paced60.vi`: md5 59ec66b61f3518b049a3c532a8e65482, 13805 B (:73).
  Callee #221 (buf) -> #226 (paced buf) only, wire-edge diff 0 over 13 edges, ES 1 warm (:67,:70); ES 1 COLD (:80); cold census == warm (:83).
- Pane per slot of both == the unpaced file's (:79,:81); VI.Name of both has no library (:78,:80).
- Inputs unchanged a89dafc1 / 842ecad9 (:84, pins :105-108); only the 2 new .vi in claudeDev\replay (:85).
- Hygiene: refs opened 16 == closed 16, live 0 (:90); all pins incl. bed, P5, P5-1, S1, S1 replay, cal, donor hold (:93-110, H3 :110);
  Moving-Objects pair restored (:114-117); LabVIEW gone (:118, and tasklist empty after the run). No original opened (preload=False).

## Files written (card 170-a3-1)
`tools/recipes/stage_replay_paced60.py` (op() wrapper, task id, launch line), `tools/bench/memory_model.json` (one key),
`tools/bench/diag_c170_a3_1_rehash.py`, `..._load.py`, logs `diag_c170_a3_1_{rehash,dry,prerun_a,load_prerun,load,prerun}.log`,
`launch_c170_paced60.log`, this file. `diag_c170_a3_1_load_prerun.log` is a FAIL of a stage_prerun pass over the read-only load diag
(no graph JSON / plan for it, :6-20); that diag needs no prerun and ran without one (its X10 was PASS 589.9, :23).
