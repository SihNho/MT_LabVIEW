# Card chat-X8 - experiment 4 of discussion structure-equal-02: a continued (forked) judgement session vs a fresh one on the SAME hand-back

User 2026-10-10: "이후 2~4번도 진행하도록" and earlier: "싸이클 끝나면 컨텍스트 아낀다고 새로 세션을 열어버리는데 … 이전에
나눴던 컨텍스트가 다 사라져서 오히려 비효율성도 늘어날 것 같음". Agreed in structure-equal-02 (round 6, both): first a
PAIR COMPARISON on the same hand-back raw material (Claude via `--fork-session`), real-cycle observation only after;
verify the installed version supports fork and that the ORIGINAL session record is preserved.

No LabVIEW, no hardware, no repo writes except this card's outputs. Read docs/script-writing.md; new scripts carry the
header block at the TOP. Model calls: claude -p only (no codex in this card).

## Cases (hand-backs with a known later outcome)
- cycle 165 hand-back 1 (tools/bench/cards/handback_165_1.json) - judged 16:31 (cycle_165_handback_1.log)
- cycle 165 hand-back 2 (handback_165_2.json) - judged 16:46
- cycle 164 hand-back 2 (handback_164_2.json) - judged 14:38
Ground truth for each: what the real hand-back judgement wrote (next.json act/note right after, from git history or the
judged log), and what the NEXT assignment round then found (did the new plan hold, or hand back again, and why).

## Method
1. For each case find (a) the session id of the cycle's PURPOSE judgement session (tools/bench/cycle_<N>.log last JSON line
   session_id) - this is the context a "continued" judge would have had; (b) the exact prompt the runner gave the real
   hand-back session (its transcript's first user message under
   C:\Users\KimLab\.claude\projects\G--Codes-LabVIEW-Codes-MinLab-zz-LabView-VI-AAA-UNIST-2--Tracking-V6-ParallelLoop\<sid>.jsonl,
   or rebuild it with the runner's own function in tools/cycle_runner.py).
2. Arm FORK: `claude -p --resume <purpose sid> --fork-session --model claude-opus-5-5 --effort high --output-format json`
   with that prompt plus one line "BENCH: do not write any file; output the next.json you would write as a JSON block".
   Arm FRESH: same prompt + same line, new session, same model/effort. Both read-only: --allowedTools Read Glob Grep,
   --disallowedTools Write Edit Bash PowerShell Agent; env BENCH_CELL=1. Each call bounded (<= 15 min).
3. Before/after each fork call: md5 + line count of the original purpose-session transcript (must be unchanged) and the new
   fork session id (must differ).
4. Score each answer blind against the ground truth (hide which arm when scoring - write both answers to files A/B with a
   random assignment, score from the files): did it reach the same decision as the real judge; did it avoid the mistake the
   NEXT round then hit; did it cite evidence (file:line). Plus cost (total_cost_usd), input/cache-read tokens, wall time.
5. Write tools/bench/forkbench/report_x8.md (table per case x arm) and the raw outputs under tools/bench/forkbench/.

Return <= 25 lines: per case x arm decision match / mistake avoided / cost / tokens / minutes, the original-record check,
and one line on what this does NOT show (n=3, one model).
