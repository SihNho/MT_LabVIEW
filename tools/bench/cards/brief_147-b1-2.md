---
card: 147-b1-2
status: current
date: 2026-10-08
---
# Brief 147-b1-2 - stagekit D / TD / PB gate fix (PD356(b)), ALONE, offline

Offline only. No LabVIEW, camera or motor. This card edits `tools/stagekit.py` (the cycle purpose authorises exactly that file plus its self-tests) and runs ALONE. `tools/stagexec.py` (1bab9cf9), `tools/gscript.py` (1a80236e), `tools/elrule.py` (a5ee7d5c) are NOT edited. No plan, pred, licence, recipe or memory_model.json edit (the next card handles licence + recipes).

## Why (measured by card 147-b1-1, `tools/bench/diag_c147_b1_1_facts.md`)
Retry scratch 147-a1-8 built the right graph; D/TD/PB failed on KEYS only: TD keys a terminal by (uid, owner, NAME) (`tools/stagekit.py:1355-1357`), so the renames 'array'->'element' (#2626: 2832/4160/4165) and 'Value'->'' (#9503: 9505/9508) count as lost; PB's key `node|class|name|ordinal` (`vigraph.py:244-245,371-372`) ranks the renamed uids into other ordinals (that is the 4th missing row, `array|0`); D's `wire_keys` (:1360-1371) counts wire uid 23807 as 'kept' although the sim deleted that wire and LabVIEW re-used the uid on the same source with fewer sinks (`diag_c147_b1_1_rescore2.log:18-23`). The offline re-score with the rules below gives ALL PASS under the 5-rename licence (:30).

## The rules to implement (PD356(b)) - in stagekit only, behaviour for runs WITHOUT the new inputs must stay byte-for-byte what it is today
1. **TD / PB rename rule.** Identity = (uid, owner). A name change on a uid passes ONLY if the stage's licence lists that uid under a new key `renames` (list of `{"node", "term_uids", "from", "to"}` or the shape you find least invasive next to the existing `rename_by_uid`; read `tools/stage_prerun.py:1261-1278` `pb_licences` and the l2b1 precedent `tools/recipes/stage_d1_l2b1.py:75-76` before choosing). An unlisted rename FAILS. Today's licence format (no `renames` key) must give today's verdicts.
2. **D reuse rule (REUSE-NOTED).** A plan-deleted wire uid that is present at the end is counted REUSE-NOTED (not lost-and-new, and not 'kept' either) only if (a) its SOURCES and SINKS in the real end equal a wire of the simulated end state and (b) every sink the simulator removed from the base wire is gone from the real wire. Reused uid with any other sink set FAILS.
3. The gate functions stay pure (no LabVIEW); callers get the new optional inputs by keyword with a default that reproduces today's behaviour. Find where `term_identity_gates` / `d4_pb` / PB are called for the s06 recipe pair and report each call site (`file:line`) and what the recipe must pass for the NEXT card to wire it - do NOT edit the recipes here.

## Self-tests (extend `tools/bench/selftest_stagekit.py` or add `tools/bench/selftest_c147_b1_2.py`; quote the rc)
- (T1) the stored 147-a1-8 rows (`tools/bench/diag_c147_p4s06v18_scratch.json`, stage rows as `tools/bench/diag_c147_b1_1_rescore.py` loads them) with the 5-rename licence: D, TD, PB all PASS.
- (T2) same rows, a licence that lists only 2832/4160/4165: TD FAILS naming 9505/9508 (unlisted rename).
- (T3) a synthetic copy of the rows in which wire 23807 keeps a sink the simulator removed (e.g. 9519): D FAILS.
- (T4) a synthetic copy in which a licensed uid also changes OWNER: FAILS (the licence covers names only).
- (T5) the previous verdicts of s03 / s04 / s05 unchanged: re-score their stored end reads (find the scratch json/log of the adopted s03 282301ca, s04 95e408ff, s05 3f9ac26b; list the files you used) before and after your edit and show identical verdicts. If a stored read for one of them cannot be found, say which and run the stagekit self-test suite instead.
- (T6) the existing stagekit self-tests (`tools/bench/selftest_stagekit.py` and any that import the edited functions: grep for them) still pass with the same pass counts as before the edit (record the counts BEFORE editing).

## Report (`tools/bench/diag_c147_b1_2_facts.md`, <= 40 lines)
New md5 of `tools/stagekit.py`; diff summary by `file:line`; the call sites and the licence shape chosen; each self-test with rc and counts before/after; md5 of stagexec/gscript/elrule/plan/pred/licence/recipes/memory_model after (must equal inputs); `OPEN:` line for anything unsettled. A gate false positive goes to `tools/bench/gate_fp_queue.jsonl` through `tools/gate_fp.py`, never an env bypass.
