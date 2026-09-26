# Brief chat-N4 - model table approved by the user 2026-09-27 02:1x ("테이블대로 적용해서 차기 싸이클 부터는 변경된걸로 돌리자")

| role | before | AFTER |
|---|---|---|
| judgement session level 0 | Opus 5.5 medium/high A/B by parity | **Opus 5.5 high fixed**; `--judge-ab` default `off` (keep the flag for a later experiment; JUDGE-AB line only when on) |
| judgement ladder | 0 opus(base) -> 1 opus high -> 2 fable low -> 3 fable medium -> STOP | **0 opus high -> 1 opus MAX -> 2 fable low -> STOP** (JUDGE_RANKS = [None, (opus, max), (fable, low)]; level 2 failing again = RUNNER STOP + decisions item) |
| cycle firefighter (same recipe fails 2 cycles) | fable low cycle -> fable medium cycle -> STOP | **Opus 5.5 MAX cycle -> STOP** (FF_LADDER one rung; FF_MODEL/FF_EFFORT = claude-opus-5-5 / max; `--ff-model` default follows) |
| retrospective peer | `-Role outcome` (fable medium, thin) - $5 x 37 calls this week | **Opus 5.5 high**: dispatch `-Agent claude -Role hypothesis -Kind fact` (or, if peer.ps1 ties hypothesis to -Kind review, add the minimal branch so `-Role hypothesis -Kind fact` runs opus/high with the retrospective's own prompt, no adversarial preamble, no web needed) |
| fact / prose peer roles | fable low thin | **claude-opus-5-5 medium**, still thin (--safe-mode) |
| outcome review (every 5 cycles) | fable medium thin | unchanged |
| material / escalation | opus high; max -> fable low -> user | unchanged (card chat-N1/N3, commit b9eee14) |

Rules: edit with Edit/Write (no heredoc patches); keep every existing self-test green; the runner PROCESS now running (cycle 102) keeps its in-memory code - the chat relaunches it at the cycle boundary, so edits to cycle_runner.py are safe; peer.ps1 / retrospective.py edits apply to the next dispatch immediately (cycle 102's retrospective will already run on Opus high - that is intended).
Data behind the table: tools/bench/matbench/report_v1.md (material effort), judge A/B cycles 89-97 (high PASS 2.5 vs 2.0, $33 vs $39), archive/peer cost lines (outcome-role retrospectives $196), cycle 87 (fable/low judgement produced nothing).

## Added by the user 2026-09-27 02:2x: "도구 결함 관련하여 스크래치 vi 검증 부분도 적용"
When a stage run fails TWICE on the SAME scripting function (result cards' `first_fail` naming the same
gscript/stagekit function or op VI, `_vN` stripped), the next LabVIEW act is a SCRATCH-VI VERIFICATION of that
function, not a third stage run: a <=120-line stagekit script builds a minimal scratch VI (loop + the few nodes the
function needs), runs the function there, reads back the graph (uids, terminals, Is Broken?, ExecState) and writes
`tools/bench/scratch_verify/<function>_<ts>.json` with a RESULT line. Mechanical: `stage_prerun.check_launch` refuses a
stage launch whose last two records for that stage name the same failing function unless a scratch_verify PASS record
for that function is NEWER than the second failure. The record is keyed by function name from the stage's own
STEP-DIFF / exception line (structure: parse the recorded failure json, not free text). The judgement prompt gets one
sentence: after two failures on one function, write the scratch-verification card first.
