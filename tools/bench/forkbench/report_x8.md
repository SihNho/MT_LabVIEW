---
type: bench
status: current
date: 2026-10-10
tags: [bench, sessions]
---
# Experiment 4 (discussion structure-equal-02): forked judgement session vs fresh session on the same hand-back

Card chat-X8 (tools/bench/cards/task_chat-X8.json, result_chat-X8.json). Written by the chat from the card's hand-back
text: the Claude Code harness refuses report-file writes by sub-agents (fp-96). Raw files committed in 2d5463ba under
tools/bench/forkbench/ (forkbench_x8.py, rows_x8.json, rec_*.json, answer_*.md, score_*.json, key_x8.json, run_x8.log).

## Setup
Claude Code 2.1.281. Prompt = the real hand-back session's first user message + "BENCH: do not write any file; output
the next.json you would write". Both arms Opus 5.5 high, read-only (--tools Read,Glob,Grep), --strict-mcp-config,
BENCH_CELL=1. FORK = `--resume <purpose-session id> --fork-session`; FRESH = new session. Blind A/B (random key
key_x8.json), one `claude -p --safe-mode --tools ""` scorer per case.

| case | arm | decision match | next-round mistake avoided | usd | cache-read / create | min | tool calls |
|---|---|---|---|---|---|---|---|
| 165_1 | fork | yes | no | 3.40 | 476k / 161k | 0.8 | 4 |
| 165_1 | fresh | partial | yes* | 0.55 | 237k / 44k | 1.4 | 14 |
| 165_2 | fork | yes | no | 3.52 | 804k / 166k | 0.9 | 9 |
| 165_2 | fresh | yes | no | 0.73 | 375k / 61k | 1.7 | 15 |
| 164_2 | fork | yes | yes (n/a, plan held) | 4.11 | 861k / 187k | 1.1 | 10 |
| 164_2 | fresh | yes | yes (n/a, plan held) | 0.78 | 294k / 68k | 1.9 | 15 |

Real hand-back judges: $1.69 / $1.94 / $1.82, 2.7-3.0 min, with full tools. Total bench cost $13.47.
Original record: all three forks left the purpose transcript byte-identical (d4f28ef8 124 lines x2, 005e4e6a 172 lines);
fork session ids new (ee854af9, 993cd5a1, dc143cca).

## What it shows
- **Cost: the fork cost 5-6x more** - the purpose session's prompt cache had expired (forks ran 4-7 h later), so
  160-187k tokens were written to cache again. A fork is cheap only inside the cache lifetime (1 h).
- **Speed: the fork was faster** (0.8-1.1 vs 1.4-1.9 min) with fewer tool calls (4-10 vs 14-15) - it already knew the
  purpose and did not re-read it.
- **Quality: no separation** on decision match or mistake avoided; both arms missed case 165_2 (Error List 47 vs 49).

## Confounds - why this is not a verdict
- **Future leak, both arms.** The repo could not be rolled back (cycles 160-164 committed together at 17:33, b68dacbe).
  Fresh arms read today's next.json, stagexec.py and ring-p5c.md; the 165_1 fresh "yes"* names the PD402 fix, so it most
  likely came from reading the future. `--resume` attached an edited_text_file snippet of today's next.json to every
  fork (noticed by the 165_1 fork, answer_165_1_fork.md:62).
- n=3 hand-backs from one purpose (D1 ring P5), one model/effort, one Claude scorer.
- Arms were read-only; the real judges could run checks.
- Cold cache = the fork's worst case; the fork held only the purpose session, not the earlier hand-back judgement.

## Next if repeated
Measure forward, not backward: in live cycles, at a hand-back, run both arms at that moment (cache warm, no future to
leak) and score after the next round shows the truth.
