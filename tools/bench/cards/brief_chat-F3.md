# Brief chat-F3 - real-LabVIEW test records for the scripting functions the P4 plans use (idea 2 of chat-F2)

User 2026-10-06: "1~3번 모두 적용하도록 하자" (CLI-Anything ideas) and "마저 벤치 진행하도록" (the 4-arm live bench; arms A13 /
A13K need these records). Card chat-F2 (PD339) built: tools/fncontract.py (postconditions), tools/fn_records.py + 86 test
plans in tools/bench/fn_records/ (P4 v18 routes + stagekit/stagexec calls + verbs + 5 recipe fns), an ADVISORY gate
(stage_prerun.py:4551 -> fn_gate.log; tools/bench/fn_records/gate_config.json mode advisory, auto false).

## Do
1. For every function with a test plan, run its test against REAL LabVIEW on a scratch VI (minimal VI built for the
   test, or a byte copy of a bench start file - never the bed chain, never an original), measure the declared
   postconditions, and write the result record (PASS/FAIL, date, LabVIEW version, log, source md5) through fn_records.
   Batch them: one stagekit-based runner per group of functions (<= 120 lines each), handle count flat (+-100 per 20
   calls), LabVIEW closed at the end, memory limits as in memory_model.json. Legacy scratch_verify evidence does not
   count as fresh.
2. A FAIL is a finding, not something to fix here: record it, list it with its measured numbers, and do not change the
   function (the arm runs measure the functions as they are).
3. Report coverage: functions used by the three P4 v18 plans (s04..s06) with a fresh PASS / FAIL / no record. If EVERY
   function those plans use has a fresh PASS, switch gate_config.json to refuse mode (state it); otherwise leave it
   advisory and say which functions block the switch.
4. Regenerate the capability block (tools/gen_capabilities.py) so the record status shows; doc_lint drift none.
5. Record the decision as the next PD in docs/d1/tooling.md + INDEX; commit by explicit path.

## Limits
labview build on scratch VIs only (claudeDev\fntest\ or similar, created and deleted per run), no GUI except the
existing broken-intermediate save rule if a scratch needs it, no hardware, no run of any main VI. The live bench is
idle (arms A and B done; A13/A13K start after this card). Main runner stopped. Edit tool only. Return one result/1.
