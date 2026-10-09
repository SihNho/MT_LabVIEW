---
type: decision
kind: topic
status: current
date: 2026-10-08
parent: docs/d1/INDEX.md
tags: [d1, tooling, gates, stagekit, terminal-identity, pre-decided]
---

# Result gates D / TD / PB key terminals by POSITION

Opened by card chat-T6 because `docs/d1/tooling.md` is at its 400-line cap. Numbered PD366: the highest PD in the main tree's
`docs/d1/*.md` was PD365 when this was written (2026-10-08, `ring-p4c.md` PD365 = cycle 150's name-free `rebind` key, the same
rename problem on the PLAN side); code cites this file, not the number.

## Pre-decided

366. **(card chat-T6, user 2026-10-08: "두 가지 모두 적용하자"; "단자 네이밍은 몇 차례나 이야기했던 것 같은데, 왜 아직도 수정이 안되는거임?")**
     S1 (PD337, `tooling.md`) moved PLAN ADDRESSING to (owner, terminal index, terminal class); the post-run RESULT gates of
     `tools/stagekit.py` stayed on names and wire uids, so LabVIEW's own renames on wiring (#2626 'array'->'element',
     #9503 'Value'->'') and its re-issue of a deleted wire uid (23807) failed a correct build (cycle 147, `result_147-a1-8.json`)
     and a per-batch renames LICENCE (PD356(b), PD357) had to whitelist them.
     - **(a) Terminal = POSITION KEY** (node, index among the node's rows in READ order, term class, direction):
       `addrcheck.pos_table`, the same index as `addrcheck.triple` (node = `vigraph.node_of`, rows de-duplicated first-wins).
       The name is a report column only (`renames`, INFO).
     - **(b) Wire = its two ends' position keys** (frozenset of sources, frozenset of sinks), never its uid; a deleted wire uid
       present again at the end is INFO (`reuse_noted`); `reuse_bad` is always empty.
     - **(c) TD** (`stagekit.term_identity_gates` -> `term_identity_pos`): lost (base keys absent from real, plus a deleted key
       real holds under another term uid) == gone (base keys absent from the sim end); no `moved` (a kept key whose term uid
       changed - an index or class swap at one node); no `unwired`. **D**: lost wires == the sim's (sets, base space), new wires
       whose every end is on a kept base node == the sim's (sets), and |new| == |sim new|.
     - **(d) Created objects are compared by COUNT, not position:** the simulator's terminal order for a created object is not
       LabVIEW's (s03 Replace Array Subset #29396 'index' vs 'new element/subarray', s04 Wait #11081 in/out reversed: 4/15,
       2/13, 1/8, 2/4 created objects per batch, `tools/bench/selftest_t6_poskey.log` FACT lines) - `stagekit.kept_nodes`.
       Making the simulator emit LabVIEW's order is a separate change (not in this card).
     - **(e) PB** (`stagekit.pb_rename_rows`): every real row on a kept base node whose position key the sim end has gets the
       sim end's name before `vigraph.build4`; wires are untouched, so a wiring change still shows in the cdiff. `unlicensed`
       is always []. Created objects keep their real names (NG checks them).
     - **(f) Licences:** `licence_renames` still parses a pb-licence/1 `renames` list; the gates only echo it
       (`licence_renames_listed`). No new licence needs a `renames` field. The name-keyed code is kept as
       `stagekit.term_identity_names` for comparison only.
     - **(g) Measured, offline** (`tools/bench/selftest_t6_poskey.py`, 43/0, log beside it): per-node read order base vs real
       end identical in ring P4 batches s03/s04/s05/s06 (0 nodes differ); all five stored end reads (s06 twice: 147-a1-8 and the
       147-c3 rerun) PASS TD / D / PB with NO licence, and the 147-a1-8 read that FAILED on names still fails under
       `term_identity_names`; drop / unwire / source change / index swap / class change / a new wire's source change at equal
       counts / `selftest_c147_b1_2`'s T3 and T4 scenarios each FAIL; renaming every terminal or renumbering every wire uid
       still PASSES; `selftest_td_key_c141_3`'s 141-2 uid-re-use case re-asked (K2-K7) as there. The 147-a1-8 end read is kept
       as `tools/bench/fixtures/t6_s06_a1_8_end.json` (git 07202624 blob e364374c). Regressions: `tools/bench/selftest_t6_regress.py`.
     - **(i) Old tests rewritten to these semantics** (card chat-T6 follow-up): `selftest_c147_b1_2.py` - RETIRED assertions
       T0 "default == pre-edit code", T0b "pb_rename_rows(.., None) untouched", T2 "TD FAILS naming 9505/9508", T3
       "reuse_bad == [23807]", T4b "TD FAILS on an unlicensed name"; their scenarios now assert name = INFO, re-use = INFO, loss /
       owner change / kept removed sink = FAIL, plus T1n (no licence). `selftest_td_key_c141_3.py` - RETIRED `recycled == [28004,
       28979]` (T2) and `xu in recycled` (T4); T1-T7 kept on position keys; it imports stagekit inside main() and now declares
       `labview: none`, like `selftest_c147_b1_2.py`. Pins in both match raw OR LF-content md5 (a CRLF worktree checkout).
     - **(h) Recipes need no edit:** the s06 recipe's calls (`term_identity_gates(..., renames=REN, bind=...)`,
       `pb_rename_rows(BASE, L, real, REN)`, `unlic == []`) keep their signatures and output keys; their gate TEXT still says
       "wire uid + source identity" / "licensed" - wording only, the key is the position.

377. **(card chat-T7, user 2026-10-09: "보통 같은 함수가 계속 반복되면 복사 붙여넣기 대신 공통 함수로 만들고 호출하지 않아?" ·
     "지금것도 당연히 공용함수로 빼야하고 추가로 다른 작업을 할 때도 스크립트 제대로 작성하도록"; rules `docs/script-writing.md`)**
     USER-RULES: U1 (relied on: only how the PB gate KEYS its comparison changes - no bed byte, plan action or computation changes;
     the recipes' other gates are moved, not altered); none contradicted.
     Ring recipes are INPUTS + CALLS; their logic lives once in `tools/stagekit.py` (block "RING RECIPES AS CALLS", appended at its end
     so earlier `stagekit.py:N` citations stay valid); PB compares by POSITION; gate-fp fp-70 drained.
     - **(a) Census** of logic repeated in the ring recipes (files that carry it / the P5-1a copy's lines): PB inline cdiff + name
       compare 21 files (`stage_d1_ring_p5s01a.py:174-182`) · L0 plan/pred/md5 gate 21 (`:126-129`) · HB/PS/save/record tail 21 (`:183-191`)
       · checkpoints from BIND ops 17 (`:38-39`) · FR frames gate 16 (`:153-159`) · D/TD on `term_identity_gates` 10 (`:160-172`) ·
       ExecStop resume + stop report 9 (`:142-149`) · SGBackend 5 (`:82-87`) · sg_read 5 (`:90-117`) · _sg_spec + census rows 4
       (`:51-78`); in the `_scratch` pairs: snap_keep/cg_print CENSUS-ALL 13 (`stage_d1_ring_p5s01a_scratch.py:41-65`) · x10() 13
       (`:68-77`) · MEM/MEML/IN/GONE tail + sum json 13 (`:171-190`) · elcls/el_advisory/el_selftest + argv modes 5 (`:87-167`).
       s07..s09 / p5s01a mains differ from each other only in file names (diffs s06→s07: sink gates generalised; s08→s09: FR `on or
       NC == 0`).
     - **(b) Extracted (stagekit):** `pos_slot_table` / `pos_name_free` / `pos_slots` / `pos_convert` / `pos_convert_open_rows` (the
       153-a2-3 converter, PD373(d): its ONE library home is stagekit, the owner of the result gates - `selftest_c153_poskey_convert.py`
       keeps its old names as aliases) · `s1_frame_graph` · `pred_end_graph` · `pb_check` · `sink_gate_spec` · `sink_gate_read` ·
       `sink_gate_backend_class` · `RingSession` (gate_l0, census_snapshot, executor = SG + backend + Executor + L1, run = E1 /
       ExecStop, gates_ng_fr_d, gate_cen2, gate_td, gate_pb, finish) · `pred_x10` · `census_all_install` · `el_norm_ocr` / `el_class` /
       `el_advisory` / `el_advisory_print` / `el_advisory_selftest` / `scratch_offline_modes` · `scratch_tail` · `jload` · `pure`.
       Behaviour = the P5-1a recipe line for line, EXCEPT PB. The two `census_snapshot` call sites stay in the recipe source because
       `stage_prerun` X10 counts whole-VI reads from the recipe source (`stage_prerun.py:2191`).
     - **(c) PB by POSITION:** `pb_check(S1, real end, pred graph, pred rows, open rows)` converts the pred rows on S1 and the PRED'S OWN
       graph (the plan's simulated end, `pred_end_graph`) - never on the real end, which erases a pred row the build failed to make
       (`selftest_t7_ring.py` M2: converted on the real end it PASSES, on the pred graph it FAILS) - and compares SLOT sets
       (owner, index, class); open pairs through `pos_convert_open_rows`; sink names are report columns. Natively position-keyed preds
       (P5 on, PD373(e)) pass through unchanged (Q gates: the converted pred == cdiff(S1, sim end) under vigraph a7eb58c7 in all 9 cases).
     - **(d) Measured offline** (`tools/bench/selftest_t7_ring.py` 35/0): pb_check PASSES with NO licence on the stored end reads of
       P4 s03, s04, s05, s06 (147-a1-8 and 147-c3), s07, s08, s09 and P5-1a (s06: the pred's 18 stored rows = 14 slots); the old name
       compare FAILS on s06 (14 vs 18); a pred row dropped / the plan predicting a rewire the build did not make / a kept computation
       sink rewired / an open pair dropped / an unlicensed rename each FAIL; every terminal renamed still PASSES; `sink_gate_read`
       reproduces both recorded s07 PASS details character for character; `el_advisory` reproduces `diag_c149_a1_2_eladv.log:3`.
       fp-70 per PD373(d), run DIRECTLY: `selftest_t6_poskey` 43/0 (was 38/5), `selftest_c147_b1_2` 19/1 (P0 pin only, was 17/3),
       `selftest_c153_compdiff_poskey` 8/0, `selftest_c153_poskey_convert` 10/0 (now testing the library functions).
     - **(e) Recipes:** the copy-made recipes that RAN (P4 s01..s09, P5-1a, + scratch pairs) stay as the record (PD373(c)); no unrun
       ring recipe existed (P5-1b stopped at its plan, `handback_154_3.json`). The pattern for the next batch is the TEMPLATE pair
       `tools/recipes/stage_template_ring.py` + `_scratch.py` (inputs = P5-1a's as the worked example; a real launch of the template
       itself is refused). Its `stage_prerun --dry` / `--prerun` == P5-1a's: DRY PASS, PRERUN 16/0, the same 36 gate lines except the
       PB label, X10 677.3 MB (source 2 reads) / scratch 672.2 MB (`tools/bench/diag_t7_prerun2_*.log` vs `diag_t7_prerun_*.log`).
       A new batch writes `stage_d1_ring_<batch>.py` with its own INPUTS block and the same calls; its pattern signature differs from
       the copy-made recipes (`stage_prerun.pattern_signature`), so its first launch is not on a PROVEN pattern.
     - **(f) Function list (user "전부 적용"):** `tools/gen_capabilities.py` writes a second generated block in
       `docs/toolkit-capabilities.md` - every public function of every SHARED tools file (import graph); `tools/hooks/guard_write.py`
       re-runs it detached on a write to a shared file (lock + re-run flag); `tools/cycle_runner.py` `capabilities_hook` runs it before
       the cycle-end git commit (`CAPABILITIES | ...` line). Self-test `tools/bench/selftest_t7_capabilities.py`.
