# Brief chat-E3 - catch errors at the START: declared-scope headers + write-time and launch-time checks

User 2026-10-04: "훅 작동을 위해서는 프론트매터에 특정 플래그를 달도록 강제해야겠음" ... "이번 훅을 넣는 가장 큰 이유는 초장에
에러 발생을 극소화하여 시간 낭비를 최소화하는게 목적임" ... "에러 잡는 훅도 만들어줘".
Measured basis (cycles 142-143): ~75-80 of 175 min went to failed cards; ~36 min were LabVIEW scripting-function defects
(not catchable early); the other ~44 min were catchable within seconds of writing/launching: prose-field format/length
(143-5), release-line format (143-1), a stale copy of a pair another card had changed (143-P1), a data-shape crash at
import (142-4 run 1), plan addresses vs real graph (143-3/4, now S1 addrcheck), and hooks blocking good commands by text
pattern (fp-36..39 in tools/bench/gate_fp_queue.jsonl).

## 1. Declared scope header in every script (tools/**/*.py, tools/**/*.ps1)
```
# ---
# labview: none        # none | read | build
# hardware: none       # none | camera | motor
# ---
```
Same words as task/1 flags. Migration: add headers to existing scripts automatically from static imports/calls; anything
not clearly none/read gets `build` (= today's strictness, nothing is loosened).

## 2. Check at WRITE time (new PostToolUse hook on Write|Edit for tools/** scripts and plan/card JSON; result goes back to
the writing agent in the same turn, seconds)
header present and valid; py_compile / PowerShell parse; HONESTY: a `labview: none` script that imports gscript/COM/
LabVIEW-run modules or calls them is refused; JSON files: schema + machine-field length via S1's protocol.machine_view
(prose fields never gated); referenced path+md5 in cards/briefs still match.

## 3. Check at LAUNCH time (guard_bash and guard_peer read the header instead of text patterns)
declared scope <= the card's flags, else refuse; header missing -> refuse; dry run + prerun (+ S1 addrcheck) records newer
than the script and plan; failing logs end with a RESULT line carrying card id + labview flag, and guard_peer attributes a
failing log only to ITS card (fixes fp-36); stage_prerun --scratch-required and stagexec adopt are declared offline
(fp-37, fp-39); `git add` of a recipe path is not a launch (fp-38).

## 4. Prep on a not-yet-built base reports WAITING, not FAIL
A prep card whose dry run fails only on unbound objects of the provisional base (e.g. 143-P1 "E1 BASE unbound") returns
status WAITING (result/1 enum) - not counted as a failure, owes no review, blocks nothing.

## 5. Prior-art review only on what changed for repeated session scripts
For a session script of the same pattern as the last APPROVED one: text diff vs that script; parameter-only lines (plan
path, file names, memory numbers) -> no review; other changed lines -> review those lines only. Plan: op kinds already
executed successfully in earlier sessions are skipped; only new op kinds go to the review.

## Do
Implement in tools/hooks/ (guard_bash, guard_peer, guard_cycle, new write-time hook), .claude/settings.json (register the
PostToolUse hook; keep every existing hook), tools/protocol.py (WAITING), stage_prerun/stagexec as needed, the header
migration over tools/. Self-tests: each fp-36..39 as a regression case; honesty refusal; missing header refusal; WAITING
path; prior-art diff path; replay the 142-143 failure records and report which would now be caught at write or launch
time and how many minutes that is. Existing hook/stage self-tests green or explained. Do NOT edit cycle_runner.py,
guard_session.py or .claude/agents/** (parallel card chat-A1 owns them) or CLAUDE.md (the chat does). Commit only your own
files by explicit path. Edit tool only (the header migration may use a .py script you write to a file and run). Offline,
no LabVIEW. Record the decision as the next PD in docs/d1/tooling.md + INDEX. Return one result/1 JSON object.
