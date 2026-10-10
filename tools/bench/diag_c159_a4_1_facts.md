---
type: facts
status: current
date: 2026-10-10
card: 159-a4-1
---
# Card 159-a4-1 facts: dry repair PD387(e) + fp-77; offline only, no LabVIEW, no hook edit, vigraph/errorlist_check/addrcheck untouched
## Edits (pre-edit pins stage_prerun 9decb20f, stagekit 07f9e35f -> 9ea1bdeb / 9cd8822e)
- stage_prerun.py:946-981 (new) DRY_UNV_RE / dry_unverified_labels / merge_unverified; tap (was :935-956) also keeps gate lines; :1074-1075 final
  `unverified` = gate-downgraded + every UNVERIFIED-DRY / UNVERIFIED / UNPREDICTED gate line (repair 1).
- stage_prerun.py:816-822 (in gate, was :813) a result gate (PB, D, TD, CEN2; DRY_RESULT_GATES :952) TRUE on stub input -> UNVERIFIED-DRY, counted.
- stage_prerun.py:672-675 PURE_MODS + addrcheck: wrapped, addrcheck.pos_table was a STUB, so D/TD/PB position keys were stub data in every dry
  (diag_c159_a4_1_taint.log:81-93, 13 sites; pre-edit dry D read "pairs 0 == sim's 0", diag_c159_a4_1_pre_dry.log:82). After: D 21 == 21, lost 12 == 12
  (diag_c159_a4_1_taint2.log), 0 taint sites.
- stage_prerun.py:1030-1049 tracer: lines of tools/recipes/*.py run by a scratch pair (`return R.body(s)`) are statements too (was one statement: D/TD/PB tainted).
- stage_prerun.py:3235 + 3249-3277 fp-77: offline_override_delegations (cause: was :3179-3183, any ast.Call named in MODIFY_VERBS counted).
- stagekit.py:307-343 census_gate(..., unpredicted=None): SimCensus pair compared in a dry; `unpredicted` -> UNPREDICTED (repair 2).
- stagekit.py:2244-2286 (new) SimCensus, sim_census_snapshot (objs + terminal classes + wire uids + diagrams), census_unpredicted_reason.
- stagekit.py:2414-2427 gate_cen2: dry -> c0/c1 = sim census of step_00 / simulated end; partial or UNPREDICTED census -> UNPREDICTED (repair 3); :2509-2510 cg_print passes kw.
## Self-test tools/bench/selftest_c159_a4_1.py -> selftest_c159_a4_1_final.log RESULT PASS 13/0 (rc 0, 402 s)
- A1/A2 stored c158 dry / scratch-dry logs: labels [CEN2 (:70 / :82), PB (:73 / :88)] = 2; stored final line says `unverified 1`.
- D1 c158 pred (6 classes of dry.log:70, census_overall UNPREDICTED): CEN2 UNPREDICTED, counted; PASS-UNVERIFIED; PB now PASS on the sim end.
- D2 fixture pred = p5s02a's own simulated census, census_overall PASS: CEN2/PB/D/TD PASS, DRY PASS, unverified 0 (no stored RingSession plan has
  sim census == declared: diag_c159_a4_1_probe2.log:66-71; sim == declared for non-RingSession p3b2a/p3b2b/p4_s05v18, :18-23,:42-44).
- D3 recipe as stored (pred ed84b5fd MEASURED-SCRATCH): dry FAIL, CEN2 Wire sim 11 vs declared (measured) 12, all else equal; unverified 0.
- D4 scratch pair as stored: D/TD/PB PASS, CEN2 FAIL (same Wire 11/12). E1 PB TRUE on stub -> UNVERIFIED-DRY counted; F1-F6 fp-77 PASS.
- G1 stored stageplans via stagexec.compile_plan (stagexec 7a712ccb unchanged = compile code identical): 120 ok, 8 raise ExecStop (p3a_in, p4_v2..v6), digest f561095c.
## Suites before -> after (same command, logs diag_c159_a4_1_pre_* / _final_*)
- selftest_t7_ring 35/0 -> 35/0; selftest_c158_gates386 16/0 -> 16/0.
- selftest_c158_runcheck 10/0 -> 9/1 and selftest_c158_wire0face 24/0 -> 23/1: the ONLY new fail is each one's "P pins unchanged"
  (stage_prerun 9decb20f pinned; an output of this card). Every functional gate unchanged.
- selftest_stagekit, selftest_c134_1_dry: NOT RUN - guard_bash refused (card labview none, their headers say labview read); logged fp-80.
## fp-77: DRAINED (gate_fp_queue.jsonl, fixed tools/stage_prerun.py:3261, selftest selftest_c159_a4_1, note with cause). VI_MOD_EXEMPT_PATHS pins
  are of selftest_stagekit.py / selftest_fn_f2.py (stage_prerun.py:3216-3219), unchanged bytes -> no re-pin.
## Dry before -> after: p5s02a PASS unverified 0 (pre_dry.log:93, CEN2 UNVERIFIED-DRY at :83 uncounted) -> FAIL CEN2 Wire 11 vs 12 (final D3);
  scratch pair PASS unverified 0 (pre_scrdry.log:113, :98 uncounted) -> FAIL, same (final D4).
OPEN: p5s02a's dry now FAILS CEN2 (sim Wire 11, measured 12; LabVIEW re-creates one wire the sim does not) - accept as the device working, or
  record MEASURED-vs-sim census differences as UNVERIFIED-DRY instead?
OPEN: dry records written before this repair (DRY_RULE 2, stage_prerun.py:3434) still satisfy check_launch - bump DRY_RULE to force re-dries?
OPEN: run selftest_stagekit / selftest_c134_1_dry (fp-80) under a labview read card to complete the suite comparison.
