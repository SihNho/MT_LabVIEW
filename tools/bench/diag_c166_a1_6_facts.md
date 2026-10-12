---
type: facts
status: current
date: 2026-10-12
card: 166-a1-6
---
# 166-a1-6 facts (offline, no LabVIEW): E5 + reuse detectors by node identity, stricter only; fp-87 / fp-88 drained
## Change (tools/stagekit.py 93299121 -> b40155ed)
- NEW block NODE IDENTITY at the end of the file: `node_ident` (:3102) and `ident_matches` (:3120) = prep_c164_a3_7_ident.py ident()/matches() moved unchanged (tunnel owner via stagexec.tunnel_owner, else frame_diagram of its rows). The prep script is not edited (stored record).
- NEW `deleted_nodes_by_ident` (:3131): PRESENT if an object of the base identity exists under ANY uid (survivors), or the uid is still an object of the SAME class; `uid_reused` (INFO) only when the uid now holds another class; a uid not in base keeps the uid rule.
- NEW `e5_check(edits, after, base=None)` (:3160): the inline `e5` of the graph diags as one call; old keys + ok, uid_reused, survivors, rule. base None = old uid rule.
- NEW `row_uid_reused(base, real)` (:3184): uids in both row tables whose roles differ (node: owner class; term: term class, owner uid, owner class). INFO only.
- term_identity_pos returns `uid_reused` (:1522, same line); RingSession.gate_td prints `RECORD TD uid ... re-used` per entry (:2736-2737, +2 lines after :2735). td_ok / d_ok / reuse_noted / recycled code unchanged.
- Docstrings of the five new functions and term_identity_pos name selftest_c166_ident.py; docs/fn_descriptions.json unchanged (no docstring-less old function touched).
- Inline E5 copies NOT rewritten (stored records; future graph diags call e5_check): diag_c141_3_graph.py:59, diag_c143_1 .. diag_c165_a3_4 _graph.py:63-70 (e.g. diag_c164_a3_5_graph.py:65).
## Self-test tools/bench/selftest_c166_ident.py -> selftest_c166_ident.log:105 RESULT PASS 29/0 (run 2)
- Run 1 :52 FAIL 28/1 = own N4 mutation (moved term kept owner_class 'Comparison', so #12169 also gained a role); fixed in the test (:70).
- P1 :57 node_ident #23042 ('Comparison','Diagram',23405,(15713,30518)), #23501 ('LoopTunnel','WhileLoop',23041,(15675,11867)) == prep_c164_a3_7_ident.log IDENT lines.
- I1 :59 #23501 identity GONE, uid_reused -> ('ParameterTerminal','Comparison',(),(5478,11923)); I2 :60 #23042 identity GONE.
- P2 :63 e5_check(base) ok, deleted_nodes_present []; P3 :64 without base = stored E5 FAIL [23501] (diag_c164_a3_5_graph.log:305).
- P4 :66 row_uid_reused(p5s02c, p5s02d) = 2 entries: 23481 term of #23042 -> term of #12170; 23501 node LoopTunnel -> term of #12170 (:65); term_identity_pairs carries the same list.
- N1 :67 planted survivor of #23501 under uid 99923501 -> present [23501], ok False; N2 :68 same for #23042; N3 :69 same uid + same class elsewhere -> present; N4 :70 rename -> no entry, owner move -> 1 entry.
- S :71-101 old rule recomputed == stored E5 line in all 15 pairs (diag_c143_1 .. diag_c165_a3_4, base = previous step's graph); diag_c141_3 not scored (no stored base graph read, :71).
- S2 :102 no stored PASS becomes BLOCK (no RETURN row). S3 :103 the only BLOCK -> PASS is diag_c164_a3_5 uid 23501 (class LoopTunnel -> ParameterTerminal) = fp-87 itself.
## Stored plans: compile + dry (all stagekit edits of assignment 166-1)
- Command: `py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c166_a1_6_dry.log -- py -u tools/bench/diag_c166_a1_6_dry.py all` (calls diag_c166_a1_4_dry.run_one / norm).
- Old = pre-assignment stagekit dd57c1ca (diag_c166_a1_4_stagekit_pre.txt), new = b40155ed: diag_c166_a1_6_dry.log:11 RESULT PASS 8/0; :4-10 p5s01a, p5s01b, p5s02a-e equal after timestamp cut, no RECORD TD uid line.
- p5s02d dry rc 1 under both (CEN2 vs plan_ring_p5s02d_pred.json census, :9) - pre-existing, unchanged, not fixed.
- Card 166-a1-3 edited errorlist_check.py / elpredict.py only; neither is imported by stagekit, stage_prerun, stagexec, stagesim or the p5 recipes (grep).
## Regressions (stagekit b40155ed)
- t6_poskey 43/0, c158_gates386 16/0, td_key_c141_3 9/0, c159_cen2_ends 8/0, t7_ring 35/0, c166_pbtight 26/0, c161_pbinherit 10/0, c163_pbchain 10/0 (diag_c166_a1_6_reg_*.log).
- selftest_c147_b1_2 19/1 (diag_c166_a1_6_reg_c147.log:3): only P0 pins fail - stagexec 1d5309f4 vs 1bab9cf9, memory_model.json, plan_ring_p4_s06v18_pred.json; none touched here (pre-existing drift).
## Pins that drift (not re-pinned)
- stagekit pin dd57c1ca: selftest_c165_innerface.py:250, selftest_c165_prime.py:117-118 (drifting since 166-a1-4). No file pins 93299121.
## fp-87 / fp-88
- fp-87 drained: `gate_fp.py drain --id fp-87 --fixed tools/stagekit.py:3131 --selftest tools/bench/selftest_c166_ident.py` -> DRAINED.
- fp-88 drained: `... --id fp-88 --fixed tools/stagekit.py:3184 --selftest tools/bench/selftest_c166_ident.py` -> DRAINED.
## Checks
- diag_c166_a1_6_hash_before.log / _after.log PASS 8/0: 4 card inputs equal (stagekit excluded), 7 VIs 75773b0d 7f2582ae eb1d0f31 94ffff94 f9ae7751 564d8cbe 6dcd5c3d unchanged; no LabVIEW process (tasklist).
- tools/lint.py --files shared total 0 (diag_c166_a1_6_lint.log). No hooks / STATUS / INDEX / plan / PB / EL edit.
