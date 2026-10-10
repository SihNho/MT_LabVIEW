# diag_c160_h1_1 facts (card 160-h1-1, offline, no LabVIEW, no .py edited)
- Entries: git HEAD 119 / card-pinned input 245 / after 304 (+59). md5 before bf3224bd5ff6b3bd8d57f0c71f1b5864 (== card pin) / after 30db045d4a3bb4e21d929d25bd3396e8.
- Added by module: stage_prerun 28 (all remaining), diag_replay_lib 12 (all), lv_errorlist 12 (all), guard_session 7 (all). Each read from the function's code.
- Round-160 additions (stagekit made_symbols / used_symbols / map_symbols / map_frames / apply_map / bound_from_cmap, stagesim.termless_wire) are NOT undocumented: stagekit, stagesim, stagexec, addrcheck, vigraph have 0 rows in the list (diag_c160_h1_1_list.log TOTALS) - they carry docstrings.
- Candidates: tools/bench/diag_c158_a2_5_list.py (gen_capabilities.described_rows) -> diag_c160_h1_1_list.log (stage toolchain), diag_c160_h1_1_list2.log (other shared tools).
- Check tools/bench/diag_c160_h1_1_check.py -> diag_c160_h1_1_check.log: 9/0. C0 pre-edit bytes rebuilt by cutting the appended block == pin bf3224bd; no pinned or HEAD entry changed/removed; 59 added; L12 stale_descriptions() = []; every new key 'side file'; longest 289 chars; stagekit 1441bb4c, stagesim a3261b56, stagexec c4a6e0b6, stage_prerun 7605116f unchanged.
- gen_capabilities --summary (diag_c160_h1_1_gen.log): "rewrote | fn-table 152 rows; fn-list 198 files, 2567 functions, 304 from the side file, 882 undocumented" (list before: 941).
- Tracked file rewritten: docs/toolkit-capabilities.md 1192694b5dbc6113fa6809aa32589bda -> ae0c5aa1297f7f041dd4f6c910c66ba8. capabilities_regen.log/.out, capabilities_shared.json md5 unchanged (diag_c160_h1_1_hash_before.log vs _after.log).
- doc_lint (diag_c160_h1_1_doclint.log:25): L12 WARN only "stale 5" stagekit.op fn-table records (pre-existing, same as c159), no stale-description part -> L12 clean for the new keys. rc=1 from pre-existing FAILs L2 (docs/d1/ring-p4.md:131), L6, L8, L10.
- New file: tools/bench/diag_c160_h1_1_check.py (same gates as diag_c159_a5_1_check.py, whose pin and first key are hard-wired, + tool md5 gate). tools/hooks untouched (guard_session described in the json only).

Samples (description <- code):
1. stage_prerun.stage_key <- tools/stage_prerun.py:3459-3460 `return re.sub(r"_v\d+(?=\.py$)", "", os.path.basename(script).lower())`.
2. diag_replay_lib.edges <- tools/bench/diag_replay_lib.py:169-176 wires grouped by wire_uid; `set((own(a), a["term_name"], own(b), b["term_name"]) ... if a["is_source"] ... if not b["is_source"])`, own = remap.get.
3. guard_session.session_id <- tools/hooks/guard_session.py:138-143 data session_id, else env CLAUDE_SESSION_ID, else "unknown"; `SAFE_RE.sub("_", sid)[:80]` (SAFE_RE = [^A-Za-z0-9._-], :78).

OPEN: not described this card (budget ~60): fntest_lib 12, lvclick 10, motor_gate 9, debate_relay 8, guard_assign 8, opmodels_lib 3, then the build_*/diag_* scripts (882 left). None skipped for unclear behaviour.
