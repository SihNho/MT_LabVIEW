---
type: bench
status: current
date: 2026-10-10
tags: [bench, reviews]
---
# Experiment 3 (discussion structure-equal-02): single hypothesis review vs independent-first-round discussion

Card chat-X7 (tools/bench/cards/task_chat-X7.json, result_chat-X7.json). Written by the chat from the card's hand-back:
the Claude Code harness refuses report-file writes by sub-agents (fp-96). Raw files under tools/bench/reviewbench/
(case_1-3.md, truth_1-3.md added only after scoring, score_x7.py, scores_x7.json, mapping_x7.json, blind/, disc_1-3/,
armA_*.log, armB_*.log, score_x7.log) and archive/peer/2026-10-10-reviewbench-1..3.md.

Cases: 1 = cycle 164 hand-back 1 (K3/K4 pass wires do not compile), 2 = cycle 164 hand-back 2 (prior art: J delete
form), 3 = cycle 165 hand-back 2 (route check refuses inner faces). Arm A = `peer.ps1 -Agent claude -Role hypothesis`
(one answer). Arm B = debate_gdoc rounds, local doc, round 1 independent (Claude + GPT), <= 4 rounds, auto-end. Same
question to both. Blind scoring by a fresh read-only Claude scorer; GPT scorer for case 1 only.

Scores: cause named / discriminating test matches the truth / wrong claims / actionable in one card.

| case | arm A single | arm B discussion |
|---|---|---|
| 1 | yes / yes / 0 / yes - 1 round, $1.03, 2.4 min | yes / yes / 0 / yes - 4 rounds, $3.43, 5.9 min |
| 2 | partial / partial / 0 / yes - $1.14, 3.0 min | partial / partial / 0 / yes - 3 rounds, $2.16, 6.8 min |
| 3 | yes / partial / 0 / yes - $0.87, 2.7 min | yes / **yes** / 0 / yes - 4 rounds, $2.75, 7.4 min |
| total | $3.04, 8.1 min | $8.34 Claude (2.7x) + GPT + Gemini checks, 20.1 min (2.5x) |

- All three discussions converged. B also ran 1/2/2 Gemini checks (cost not recorded); GPT token counts not recorded
  (tools/debate_relay.py:129-136 keeps only the codex session id).
- GPT scorer on case 1 agreed with the Claude scorer (both arms yes/yes/0/yes); 140,825 input tokens (109,696 cached),
  814 output. Its file checks did not run: guardcore denied `mcp__node_repl__js` (21:22:45) - the agreed fail-closed rule.
- **Where B was better - case 3 only:** B proposed the narrow conditional PRIME skip with negative cases, which is the
  test that later decided it; A's exemption was broader and its test ran in memory only.
- Case 2: both avoided deleting w23519; neither wrote the new J order; both proposed a LabVIEW scratch run where the truth
  used an offline end-graph check.

## Limits
- n=3, one run per arm per case; the hand-back text already names much of the cause in cases 1 and 3.
- The scorer is Claude (same family as A and half of B); blinding partial (B answers Korean summaries, A English prose).
- Leak possible: in case 2 B's Claude opened a later pred file and said so (disc_2/relay/round_03_claude.md:13); arm A's
  file reads were not recorded. Case 3 used reconstructed code (src/stagexec_case3.py.txt, md5 ec4f38e5, not the pinned
  6ea6637f).

## Reading
One better discriminating test in three, at 2.7x Claude cost (plus GPT and Gemini) and 2.5x time. Not a case for moving
EVERY hypothesis review into a discussion; open whether a narrower trigger (e.g. a repeated failure class, or a review
whose first answer proposes a LabVIEW run) earns the cost.
