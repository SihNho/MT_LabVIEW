# Brief chat-F2 - per-function postconditions, per-function test records, capability docs generated from code

User 2026-10-06: "그러면 1~3번 모두 적용할 가치가 있겠다. 적용하도록 하자" - three ideas taken from CLI-Anything
(analysis: docs/chat-handoff.md 2026-10-06; repo HKUDS/CLI-Anything HARNESS.md, unrealinsights README :345-360,
macrocli MACROCLI.md :76-113, nsight HARNESS.md :75-77). Purpose (user 2026-10-04): catch errors at the START.

## 1. One standard result + declared postconditions per scripting function (tools/gscript.py, stagekit, stagexec)
Every LabVIEW-touching function returns/raises one standard outcome: ok | no_output | failed | timed_out (with reason).
Each function DECLARES its postconditions in one table (not prose): e.g. delete_object "objects removed == 1",
terminal lookup "matches == 1", create "new objects == expected class/count", wire "one new wire, both ends bound".
A shared checker runs them on every call and fails at that call with the measured numbers (delete_object already has
one - generalise it, do not duplicate). Functions whose postcondition cannot be measured cheaply say so explicitly
(`postcondition: none - <reason>`), never silently. Do not change what any function DOES (rule 1a spirit: behaviour of
working tools stays); only add checks and the standard outcome.

## 2. Test plan first, then a real-LabVIEW record per function; scripts use only recorded functions
- A machine-readable registry (e.g. tools/bench/fn_records/<function>.json): test plan (inputs, predicted
  postconditions) written BEFORE the test; result record (PASS/FAIL, date, LabVIEW version, log path, md5 of the function
  source at test time).
- A record goes stale when the function's source md5 changes.
- stage_prerun / guard_bash: a stage script that calls a function with no fresh PASS record -> ADVISORY (logged) in this
  card; switch to refusing only after card chat-F3 has run the records for the functions the current plans use. State
  the switch condition in code/config.
- Write the test plans for the functions used by the P4 v18 plans and stagekit/stagexec paths now (offline); the real
  LabVIEW runs are card chat-F3, not this card. Fold in existing evidence where a scratch_verify PASS already exists.

## 3. Capability docs generated from code
A generator that emits the function table (name, args, outcome/postconditions, record status, source file:line) into a
GENERATED block of docs/toolkit-capabilities.md (and the terminal-name part of docs/NAMES.md only if it is derivable
from code/records - otherwise leave NAMES.md alone and say so). Human-written prose outside the block stays untouched,
and existing file:line citations into these docs must stay valid (append the block at the END of the file, as chat-E3
did with headers). doc_lint: report code-vs-doc drift (function in code missing from the block, block entry whose
function is gone, stale record) every cycle.

## Do
Self-tests for each part (a double delete caught at the call; lookup matching 2 caught; standard outcome on timeout;
stale record after source change; advisory gate line; generator idempotent; drift report). Existing self-tests green or
explained. Offline only - no LabVIEW in this card. Headers per PD338 on new files. Record the decision as the next PD in
docs/d1/tooling.md + INDEX. Do NOT edit CLAUDE.md (the chat does). Commit your files by explicit path. Edit tool only.
Return one result/1 JSON object.
