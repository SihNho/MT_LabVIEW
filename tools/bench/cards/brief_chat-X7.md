# Card chat-X7 - experiment 3 of discussion structure-equal-02: single-shot hypothesis review vs (independent first round + discussion) on the SAME failure

User 2026-10-10: "이후 2~4번도 진행하도록"; idea 2: "피어리뷰를 … 코멘트 한 번 씩만 받고 있는 것 같은데, 이거를 … 에이전트 토론에
같이 통합시키는 편이 오히려 좋지 않을까?" Agreed in structure-equal-02 (round 6, both): only the HYPOTHESIS review moves to
a discussion (independent first round, then discussion); measure it first on the same raw failures - quality, time, cost.
Claude and GPT have EQUAL weight (user). No LabVIEW, no hardware. Read docs/script-writing.md; new scripts carry the
header block at the TOP. Codex runs with `-s danger-full-access` (docs/decisions/codex_sessions_run_full_access.md); the
trusted project hooks guard it.

## Cases (failures whose real cause is known from what fixed them later)
1. cycle 164 hand-back 1 (tools/bench/cards/handback_164_1.json): K3/K4 pass wires do not compile (stagexec.py:901).
2. cycle 164 hand-back 2 (handback_164_2.json): prior art says group J must use the P4 delete form (PD321(b)/PD323).
3. cycle 165 hand-back 2 (handback_165_2.json): route check refuses connects onto inner faces t8776/t24342.
For each, build ONE raw-material file tools/bench/reviewbench/case_<n>.md from the machine record only: the hand-back
json, the failing log's first failing lines (file:line), the card and plan paths - NOT the later judgement or fix (the
reviewers must not see the answer). Ground truth file tools/bench/reviewbench/truth_<n>.md: what the next judgement
decided and which later card PASSED, with paths - written for the scorer only.

## Arms
A. SINGLE: the current reviewer, `powershell -File tools/peer.ps1 -Agent claude -Role hypothesis -Slug reviewbench-<n> -TaskFile <case file>`
   (one answer; record cost/time from its archive cost line).
B. DISCUSSION: `py tools/debate_gdoc.py run --mode rounds --doc local --no-login --auto-end --max-rounds 4 --summary <file>
   --topic <case file> --dir tools/bench/reviewbench/disc_<n>/relay` (round 1 independent and simultaneous, Claude + GPT;
   ends at convergence or 4 rounds). Run under bgrun with a deadline. Record rounds, Claude cost, minutes; GPT has no
   cost line - record its token counts if the codex json gives them.
Both arms get the same question text: "What is the most likely cause of this failure, what is the strongest alternative,
and what is the cheapest test that tells them apart?"

## Scoring (blind)
Write each arm's final answer (A: the review answer; B: the discussion summary's agreed items + experiment) to files
X/Y with a random mapping recorded separately. One fresh `claude -p` scorer (opus-5-5, effort high, read-only, BENCH_CELL=1)
gets the truth file and X/Y and scores: cause named (yes/partial/no), discriminating test matches what later decided it
(yes/partial/no), wrong factual claims (count, with file:line check), actionable in one card (yes/no). Then un-blind.

Write tools/bench/reviewbench/report_x7.md: per case x arm scores, cost, minutes, rounds; what this does not show (n=3,
the scorer is a Claude model - note it, and if cheap also run the scorer once as GPT via codex exec for case 1 only).
Return <= 25 lines.
