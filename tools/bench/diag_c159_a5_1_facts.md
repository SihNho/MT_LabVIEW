# diag_c159_a5_1 facts (card 159-a5-1, offline, no LabVIEW, no existing .py edited)
- Entries: git HEAD 119 / card-pinned input 185 / after 245 (+60). md5 before c54377eabbdbb8afa79e4e4c1ec42206 (== card pin) / after bf3224bd5ff6b3bd8d57f0c71f1b5864.
- Added by module: stagexec 32 (every remaining undocumented one), protocol 14 (all), scope_header 8 (all), jev_gate 3 (all), run_mode 3 (all). None for stagekit / stage_prerun (card 159-a4-1 edits them).
- Candidates: tools/bench/diag_c158_a2_5_list.py (gen_capabilities.described_rows) -> diag_c159_a5_1_list.log (stagesim / addrcheck / vigraph: 0 left), diag_c159_a5_1_list2.log (other shared tools).
- Check tools/bench/diag_c159_a5_1_check.py -> diag_c159_a5_1_check.log: 9/0. C0 pre-edit bytes rebuilt by cutting the appended block == pin c54377ea; no pinned or HEAD entry changed/removed; 60 added; L12 stale_descriptions() = []; every new key shows as 'side file'; longest 276 chars.
- gen_capabilities --summary (diag_c159_a5_1_gen.log): "rewrote | fn-table 152 rows; fn-list 196 files, 2543 functions, 245 from the side file, 933 undocumented" (was 993).
- Tracked file rewritten: docs/toolkit-capabilities.md fb76516bf1f730a397b3dcd040d2b4ef -> 3b0e0f7b75bb7761fd5c2ed9892dfedf. tools/bench/capabilities_regen.log/.out, capabilities_shared.json md5 unchanged (diag_c159_a5_1_hash_before.log vs _after.log).
- doc_lint (diag_c159_a5_1_doclint.log:22): L12 WARN only "stale 5" stagekit.op fn-table records (pre-existing, same as c158), no stale-description part -> L12 clean for the new keys. rc=1 from pre-existing FAILs L2 (docs/d1/ring-p4.md:131, docs/d1/ring-p5.md:378), L6, L8, L10.
- New files: tools/bench/diag_c159_a5_1_check.py (same gates as diag_c158_a2_5_check.py, which is hard-wired to git HEAD, plus the pinned-bytes baseline), tools/bench/diag_c159_a5_1_hash.py (md5 + git status of the files the tools rewrite).

Samples (description <- code):
1. stagexec.Addr.track_new <- tools/stagexec.py:1759-1770 difflib opcodes; `elif tag != "equal": raise ExecStop`; `if len(src) != 1 or len(snk) != 1: raise`; `return {"r_outer_idx": src[0], "l_outer_idx": snk[0]}`.
2. protocol.make_result <- tools/protocol.py:303-306 `st = status or ("PASS" if (n_fail == 0 and not first_fail) else "FAIL")`; first_fail `[:200]`; returns the result-line/1 dict.
3. run_mode.effective <- tools/run_mode.py:37-48 disabled -> "performance"; unreadable mode file or age > stale_min -> "economy"; else `pct <= threshold_pct`.

OPEN: not described this card (budget ~60): stage_prerun 28 (card rule), lv_errorlist 12, diag_replay_lib 12, fntest_lib 12, lvclick 10, motor_gate 9, debate_relay 8, guard_assign 8, guard_session 7, opmodels_lib 3, then the build_*/diag_* scripts (diag_c159_a5_1_list.log TOTALS, 933 left).
