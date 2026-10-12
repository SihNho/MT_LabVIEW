# diag_c171_a2_2 facts (card 171-a2-2, assignment 171-2, 2026-10-13) - offline, no LabVIEW (tasklist 0 before/after)
## Step 1 - patch re-applied with the Edit tool (5 edits = the 4 hunks of diag_c171_a1_2_patch.diff)
stage_prerun.py db81a1d3 -> af6937e84fbe857e571f19bb55301465; `git diff --stat`: 1 file changed, 136 insertions(+) (= patch +136/-0).
guard_write warned per edit: open card 170-a2-5 pins stage_prerun.py at db81a1d3 (stale pin, not this card's to re-pin).
## Step 2 - checks, one at a time
a `diag_c171_a2_2_dry170.log:10` UNVERIFIED  A2 p6 BEFORE: #6810 calls get buff image-lost frames.vi, #22692 calls IMAQdx Get Image.vi  (dry: stub input)
  `:28` === DRY PASS-UNVERIFIED ... first_fail=None coverage 65/69 lines, first mutation g.replace_object, unverified 7; no FAIL line; `:30` BGRUN END rc=0
b `diag_c171_a2_2_st134.log:15` RESULT PASS 11/0 (= selftest_c134_1_dry_c160_f3_1.log:15); `:16` END rc=0 140 s
c `diag_c171_a2_2_taint.log:19` RESULT PASS 9/0; `:20` END rc=0
d `diag_c171_a2_2_c130_5.log:4` T1 SKIPPED, `:6` T2 PASS, `:8` T3 FAIL at GATE PB frame-keyed cdiff(S1, real end) == the P2b bed's 16 rows
  and the plan's 11 open (node, term) pairs (FATAL, before save), `:9` T4 PASS, `:10` totals 2/1.
  SAME TEXT: `diff` vs diag_c171_a2_1_c130_5_unpatched.log - lines 3-9 identical; only BGRUN START/PID (1-2) and the RESULT card id (10) differ.
## Step 3 - state
prerun_records.jsonl:1204 (newest plan-170 record, 2026-10-13 02:09:29, this card's dry a): status PASS-UNVERIFIED, unverified 7, plan_replay_swap_170 01c21526.
Plan 170 md5 01c215260c268e8a8990984139c4cfef unchanged. Recipe: sha256 5ae90c59 in records :1203 and :1204 (same as before this card);
  its md5 could not be printed: guard_bash prior-art gate refused a read-only md5sum naming the recipe (logged fp-104, tools/stop_record.py:768).
No hook edited, no .vi written, no STATUS/INDEX/plan edit.
