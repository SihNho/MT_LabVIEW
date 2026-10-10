---
card: 158-a2-2
status: current
date: 2026-10-10
---
# Brief 158-a2-2 (assignment 158-2) - P5-2 STEP-1 SCRATCH, second launch, with the wire-0 loop-face act; adopt as `D1_ring_p5s02a_<ts>.vi`; the ONE LabVIEW card

This is `tools/bench/cards/brief_156-a2-1.md` again (read it, and through it brief_155-a3-1 / 155-a3-2 / 154-a3-3 / 3b: launch, adopt,
final Error List, graph read, `load_by_vi`, invariants, LabVIEW-gone) with ONLY the deltas below. The first launch (card 156-a2-1)
stopped at ops 16/17 because the loop inner face (`#24360`, `#24367`) is in no `Nodes[]` row; card 158-a2-1 (PASS) changed
`tools/stagexec.py` so an UNWIRED While/For LoopTunnel inner face is joined by ONE `gscript.connect_term_uid` (src = face terminal uid,
sink = the same `#376` input terminal uid the wired case uses), a wired face stays `cfw`. Read `tools/bench/diag_c158_a2_1_facts.md`
and `tools/bench/diag_c158_a1_3_facts.md` first (dry/prerun records are valid only for the stagexec bytes they were run on).
Helper scripts to copy: `tools/bench/diag_c155_a3_1_{inv,peek}.py` and `diag_c155_a3_2_{adopt,elexp,mkgraph,graph,memload,nodes,inv}.py`
(-> `diag_c158_a2_2_*`; names, ids, pins, paths ONLY; say which lines changed). Call shared functions, do not paste a block you can
import (`docs/script-writing.md`); a block you must copy is an `OPEN:` line with file:line.

## Pins (md5 in the task; a mismatch is a RETURN)
stagexec **7a712ccb** (changed by 158-a2-1), stagekit 0d8f6d25, stagesim eb99c6ba, addrcheck 207beb0d, stage_prerun 9decb20f,
gscript 1a80236e, vigraph a7eb58c7; plan `plan_ring_p5s02a.json` 4284c22a, pred 31d8e9be, licence e8fd6a98, MAIN recipe b52b9ff5,
scratch recipe 71c3aed4; adopted P5-1 `claudeDev\D1_ring_p5s01_20261009_124542.vi` 7f2582ae (never edited; the scratch runs on a NEW
byte copy), graph 6716c499, memory_model c87d170a, `docs/d1/ring-p5.md` 59a0c310.

## Deltas against brief_156-a2-1
1. **Pre-checks on the NEW stagexec bytes, FIRST.** Re-run dry (expect PASS, PASS-UNVERIFIED PB), prerun (expect PASS, X10 planned MAIN
   <= 675; round-1 value was 674.7), `--scratch-required` and `--check-launch`, and quote the lines. The earlier dry/prerun records belong
   to stagexec df82d75e and are stale for 7a712ccb: re-running dry + prerun on the unchanged recipes is not an edit. **If planned MAIN
   is above 675: RETURN with the numbers, no re-cut of the plan, no launch.**
2. **The launch gate** needs the card's rules text `DRY-UNVERIFIED-OK: PB frame-keyed cdiff` (it is in this task's rules) and the
   argument `--unverified-card tools/bench/cards/task_158-a2-2.json`. A gate refusing your own command text is a false positive:
   `py tools/gate_fp.py log`, no env bypass; RETURN with the refusal text.
3. **ONE scratch** under `bgrun --material` on a NEW byte copy of 7f2582ae, ops 1..17. E1 real == sim at every checkpoint
   (0,1,3,6,8,9,12,15,16,17); diff must be 0. Quote **the FATE lines of the move_in run (ops 10-12)**: E1 for mv_376 op 10, mv_3052 op 11,
   mv_3453 op 12.
4. **Ops 16/17 (the new act).** Quote which act each op took (wired face -> `cfw`; unwired -> `connect_term_uid`, the face uid and the dst
   uid it used) and the MEASURED census delta of each op against the PREDICTED variant `loop_inner_face_wire0` (R1 delta
   `register_end_case_border` = SelectorTunnel 1, OuterTerminal 1, InnerTerminal 2, Wire 2 when the dst sits in a Case frame). A census
   that differs from the prediction is a RETURN with both values (the variant is marked unmeasured). **A SECOND stop at op 16 or 17 is a
   RETURN with the facts and NO retry in this card** - the assignment session hands the stop back to judgement.
5. **Adopt** (structural PASS only), final Error List, fresh-instance load + graph json + md5, `load_by_vi` entry (only that entry of
   `memory_model.json`; key-by-key diff quoted), invariants md5 before = after, handles, LabVIEW closed AND verified gone: exactly as in
   brief_156-a2-1 items 3-7. The graph is the base of the step-2 plan: quote the rows brief_156-a2-1 item 5 lists.
6. **After adoption only: delete the failed copy** `claudeDev\D1_ring_p5s02a_20261009_152721.vi` (md5 cac5236b - verify the md5 first)
   and its resume record (find it with a grep for `152721` under `tools/bench/`; quote the path). Do NOT delete before the adopted file
   is accepted. Do not delete anything else.
7. **Quote md5 of s09 eb1d0f31, P5-1a 2482fe7b and P5-1 7f2582ae before and after.** No `tools/hooks` edit, no recipe / plan / pred /
   licence / stage-tool edit, no original opened, no motor or camera. Concurrent cards: none.

## Report `tools/bench/diag_c158_a2_2_facts.md` (<= 45 lines)
Pre-check numbers; gate outcomes per op class; E1 per checkpoint and for the three move_in ops; the act and measured vs predicted
census of ops 16/17; metered start/peak vs 597.5 / planned; adopted file + md5 + load MB; EL total + per-class; graph json + md5 + the
quoted rows; `load_by_vi` diff; invariants; handles; failed copy + resume record deleted; LabVIEW gone. `OPEN:` line. Facts only.
Dispatch a hypothesis peer only if a gate FAILS.
