# Brief chat-S5 (the user calls it "S1") - stop false failures between plan and real file; protocol fields; 3-tier mismatch check

User 2026-10-03 ("좋아. 지금 수정 내용을 S1이라고 할게"), after the chat's measurement of cycles 142-143: of ~175 min,
~75-80 min went to failed cards; ~44 min of it was OUR checkers refusing good work (results 143-1, 143-3, 143-4, 143-5;
first_fail lines in tools/bench/cards/result_143-*.json), ~36 min real LabVIEW scripting defects (not in scope here).

## 1. Address terminals by position as well as name (cause of 143-4)
Plan actions may address a terminal by name only; stagesim names a Local's terminal 'value', LabVIEW names it by the
variable ('StopAll'). Add to the plan address an optional (owner uid, terminal index, terminal class) triple, written by
stagesim/compile_plan; rebase/bind resolves by name, and when the name does not bind uniquely, by the triple against the
REAL graph's terminal table. Never guess: no unique match = refuse as today.

## 2. 3-tier mismatch check before every LabVIEW launch (user approved the design)
(a) CODE first, automatic, inside stage_prerun --prerun/--rebase: every plan address against the real graph's terminal
table, every referenced input file md5, schema/length of machine fields. Output: resolved / unresolved-with-candidates.
(b) JEV only for unresolved items with a short candidate list (e.g. plan 'value' vs real 'StopAll'): one typed question
per item ("same terminal?"), confidence returned. Per the standing Jev rule: build a labelled set from cycles 130-143
first_fail lines + this cycle's cases, MEASURE accuracy, and switch it on as ADVISORY only (logged, not acting).
(c) LLM only for low-confidence items - no whole-card re-review.
And: a failed log whose ONLY failures are classified by (a) as address/format mismatches does not owe a hypothesis
review (extend the existing JEV-LADDER 'our-script-bug' discharge / gateclass soft path in guard_peer; keep STOP gates).

## 3. Predicted-vs-measured differences on a good result (cause of 143-1/143-2)
When every STOP gate passes (gateclass) and only a prediction count differs (Error List, census) by a by-design reason
the code can state (session-boundary unwired Local read / While cond, as measured in 143-2), record it to
gate_soft_log.jsonl, re-derive the prediction with the fixed rule (prep_c143_3_elrule.py, move it into a shared module)
and continue - the card is not FAIL. An unexplained difference still stops.

## 4. Protocol: machine fields vs prose fields (cause of 143-5 and the 143-1 release-line retry)
- Schemas (docs/protocol/) mark prose fields (why, note, ...). No gate or token scan reads a prose field (fix the RB
  negative-uid scan and the 400-char limit applies only where a schema says so). One shared helper, not per script.
- Prior-art / review releases become a JSON record with an enum (the verdict's own slugs), validated when written;
  keep reading the old FIXED:/REFUTED: lines for archived reviews.
- A task card or brief that names another file gives path + md5 (task/1 inputs already does); a card whose input md5
  changed before it starts is refused at bind time (cause: 143-P1 copied a pair that 143-1 had changed meanwhile).

## Do
Implement 1-4 in stage_prerun/stagesim/stagexec/gateclass/protocol/guard_peer (shared modules, no per-recipe copies),
self-tests for each, re-run the existing stage_prerun/stagexec/stagekit/gateclass/guard_peer/protocol self-tests (green
or explained). Replay check offline: run the new check on the plans/graphs of 143-3, 143-4, 143-5 and report whether each
would have resolved without a new card. Record the decision as the next PD in docs/d1/tooling.md + INDEX.

## Limits
Offline only, no LabVIEW. Runner is stopped (STATUS STOP line). Edit tool only, no py heredoc patches. git commit
allowed for touched tools/docs. Return one result/1 JSON object.
