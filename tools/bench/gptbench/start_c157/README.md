---
type: bench-guide
status: current
date: 2026-10-09
tags: [gptbench, comparison]
---

# GPT comparison - start point after cycle 157

User 2026-10-09: "현재싸이클만 돌리고 멈춰봐. GPT하고 한번 비교해보게" / "gpt는 내가 직접 돌릴거임". The Claude runner stopped
after cycle 157; `manifest.json` here (written automatically when the runner stopped) fixes the start point.

## What the start point is
- `manifest.json` `head`: the git commit to start from (`git worktree add <dir> <head>` gives a clean copy).
- `start_vi`: the LabVIEW file the next step builds on, with md5. A byte copy is in
  `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\bench\gpt_start\` - work on copies of it, so
  the Claude chain's own file stays untouched.
- `purpose_act` / `purpose_pass`: the next cycle's purpose as Claude's judgement session wrote it (`tools/bench/next.json`).
- Copies of STATUS.md, CLAUDE.md, next.json, the plan index and the script rules, with md5s.

## Keep the comparison fair
1. Run the GPT arm in its own worktree (e.g. `..\V6_bench\GPT`), never in this main folder; its LabVIEW outputs in their
   own folder under `claudeDev\bench\GPT\`.
2. Only one LabVIEW user at a time: the Claude runner stays stopped (STATUS STOP line) while the GPT arm runs.
3. Hardware rules are the same (rig state in STATUS.md; motors only through `tools/motor_gate.py` with limits set at
   start and released at end; LabVIEW closed at the end).
4. Count the same things for both arms (`manifest.json` `metrics`; definitions as in
   `tools/bench/livebench/report_4arms.md`): wall minutes and cost per cycle, files adopted and when, cards and passes,
   LabVIEW runs, hand-backs, purpose met, goalmap changes.
5. For the Claude side of the comparison, the chat can run the same number of cycles from this start in a worktree with
   the livebench harness (`tools/bench/livebench/`), one arm at a time.
