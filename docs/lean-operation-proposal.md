---
type: proposal
status: draft
date: 2026-10-13
tags: [runner, rules, lean]
---
# Switching the runner to lean operation - proposal (user 2026-10-13 "진행하도록"; NOT applied yet)

## Evidence (discussion tools/bench/debate/lean-rules-01, bench reports in tools/bench/lean_bench/)
| | current structure (cycles 170 + part of 171) | lean (one Opus session) |
|---|---|---|
| P6-2 replay acceptance | ~3 h, > $50, replay never run (6 hand-backs; a dry-checker bug held cycle 171) | 64 min, $6.64, PASS on every item |
| P6-3 gap + overload tests | not started | 102 min, $17.52, both PASS; found the col-0 one-lap lag the old acceptance missed |
| safety | - | motor sessions with readback every run, inputs md5 unchanged, LabVIEW gone, saves only under claudeDev\bench\lean |
The chat re-computed the key numbers from the raw tra files (scratch verify_p63.py): all equal to the reports.
Caveat: lean started on tools and facts the harness had built (stagekit verbs, replace_object, motor_gate, bgrun, the
replay chain, the compare, documented ring facts). The harness paid for itself while the tools were young; now its gates
cost more than they prevent.

## What lean operation keeps (enforced)
1. Motor hook + motor_gate sessions with readback (user: "모터 훅은 반드시 체크 해야돼") - `tools/hooks/guard_lean.py`.
2. Originals: no file-tool write to *.vi/.ctl/.lvlib/.lvproj; LabVIEW saves only under claudeDev (gscript refuses others).
3. LabVIEW: bgrun or <= 30 s, one client, refs closed, run-time MEMSTOP 695 MB, LabVIEW gone at the end.
4. No guard-bypass variables; secrets only in env vars; never start/stop without the user.
5. Rule 1a acceptance by recorded-frame replay at the end of a build step (not per step).
6. Two cheap habits that proved their worth in the bench: predictions written BEFORE the LabVIEW run; the chat re-checks
   the acceptance numbers from the raw output files before a result is adopted.

## What it drops (still available as tools, no longer gates)
judgement / assignment / material split, task/1 cards, first-surprise hand-backs and the 3-hand-back limit, per-card
re-hash, dry-run / pre-run / X10 prediction gates, the prior-art launch gate, mandatory peer reviews, document layering.
Self-tests, dry runs, the compare and the debate stay usable when a session decides they help.

## How it would run
- One lean session per task, launched by `launch_lean.ps1 -Task <file> -Tag <tag>` (<= 185 min, <= $60), in a worktree whose
  CLAUDE.md is the lean rules. The chat writes the task file from the plan, reviews the report, re-checks the numbers,
  merges into master and writes the next task.
- The auto-mode classifier refuses the chat starting these sessions ([Create Unsafe Agents]); today the user starts each one.
  Options: (a) keep it that way (one command per task); (b) a small supervisor the USER starts once that takes the next task
  file from a queue the chat fills - it still runs only when the user started it and stops at a STOP line.
- Master keeps the full rules until the user decides; nothing in this file is applied.

## Open for the user
1. Adopt lean operation (and which launch option, a or b)?
2. U8: under sustained overload the ring trails at the oldest slot (~19 frames) and jumps to the newest only after a
   discard (P6-3 W100: 311 single skips + 41 jumps of 19). Keep, or change to latest-wins?
3. The stage_replay_swap.py `work_dir` option stays on the lean branch (master's prior-art launch gate needs a review).
