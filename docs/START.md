---
type: procedure
status: current
date: 2026-10-10
tags: [start, rules, sessions, codex]
---

# START - how any session picks up this project

For EVERY session: Claude Code or Codex, the interactive chat or a runner session (judgement, assignment, material,
peer). Agreed in the Claude-GPT discussion token-efficiency-01 and approved by the user on 2026-10-10 ("좋음.
진행하도록", card chat-X1): rules, decisions and state live in this repository, not in one tool's private memory.
`CLAUDE.md` and `AGENTS.md` hold the same short core; this file is the reading order behind it.

## 1. Read, in this order (stop as soon as your role has what it needs)

| # | what | where | why |
|---|---|---|---|
| 1 | the core prohibitions | `CLAUDE.md` = `AGENTS.md` (loaded automatically) | never-do list |
| 2 | rules version | `git log -1 --format="%h %cs" -- docs/rules` | say which rules you worked under in your result |
| 3 | the rules for your work | `docs/rules/` topic files: `originals.md`, `hardware.md`, `interaction.md`, `labview-execution.md`, `runner.md`, `reviews.md`, `docs.md` | full wording / quotes: the frozen `docs/rules/CLAUDE-full-2026-10-10.md` (old `CLAUDE.md:N` = its line N); map: `docs/rules/coverage.md` |
| 4 | the user's decisions | `docs/decisions/INDEX.md` (one file per decision, verbatim) | a later decision wins; superseded ones are listed separately |
| 5 | state, lock, rig, OPEN, NEXT | `STATUS.md` | read first among the state files, always |
| 6 | the current purpose / next act | `tools/bench/next.json`; plan of record `docs/d1/INDEX.md` | what the next cycle does |
| 7 | open cards and unfinished work | `tools/bench/cards/active.json` (bound cards), `tools/bench/cards/task_*.json` without a matching `result_*.json`, `STATUS.md` OPEN | do not start what is already running |
| 8 | the latest report | `tools/bench/heartbeat_latest.md`, the newest file under `tools/bench/reports/` (when present) | what the user was last told |
| 9 | questions waiting for the user | `tools/bench/decisions_pending.json` | never decide these yourself |
| 10 | LabVIEW technique (before ANY LabVIEW work) | `docs/labview/SKILL.md` + `docs/labview/references/` | Claude: skill `labview-automation` points there |
| 11 | how to write a script | `docs/script-writing.md` | shared functions, never copies |

## 2. Who owns execution right now - check before acting

- **Is the runner running?** `tasklist | grep -i "python\|claude"` and the tail of `tools/bench/runner_supervisor.log` /
  `tools/bench/cycle_runner.log` (`RUNNER STOP` / `CYCLE ... END` lines).
- **STOP lines** at the top of `STATUS.md`: the newest non-`(history)` STOP line is in force until the user says start.
  Only the user starts or stops work; silence is not authorization.
- **`labview-lock`** block in `STATUS.md` (acquired / released, owner, since, purpose) and
  `tasklist | grep -i labview`: one LabVIEW client at a time; a card that does not use LabVIEW may run beside ONE that
  does.
- **Rig state** (hardware banner in `STATUS.md`): disassembled / assembled / experiment running decides motor and
  camera access (`docs/rules/hardware.md`). Only the user announces a change.

## 3. What each role may do

| role | may | may not |
|---|---|---|
| **chat** (interactive, talks with the user) | answer first (rule 2b); report from STATUS / retrospectives / reports; redirect the runner by editing STATUS NEXT/STOP; write and dispatch chat cards; drain hook false positives between runs | run a cycle itself; start or stop the runner without the user's word |
| **judgement** (runner, one per cycle) | read STATUS + the plan; write the purpose (`next.json` act + pass); judge hand-backs; decide designs, rule-1a calls, review acceptance; write `## NEXT` before the retrospective | run `tools/recipes/*.py` / `tools/bench/*.py`; read whole logs; dispatch build cards in the purpose flow |
| **assignment** (runner) | issue `task/1` cards for the purpose, retry, escalate, run the pipeline; end when every pass item has evidence | change the purpose; continue past a `guard_assign` hand-back |
| **material** (card) | the card's work within its `flags`; bind first, `requires` second; return one `result/1` | decide what a measurement means; route around a refusal; edit `tools/hooks/**` in a runner card |
| **peer** (via `tools/peer.ps1`) | read and answer, per `docs/peer-brief.md` | run, open or modify anything |
| **Codex session** (for now, per the discussion) | READ-ONLY analysis of the repo; propose cards (a `task/1` JSON draft or a written proposal) for the chat to review and dispatch | edit files, run scripts, touch LabVIEW or hardware, commit |

## 4. When you finish

Leave a file: a result card, a log with its `RESULT {...}` line, or a document - the next session starts from what is
on disk, never from your memory. Keep `STATUS.md` true during the work if your card may edit it; otherwise report the
change you would make. A rule or decision that changed goes into `docs/rules/` or `docs/decisions/` (new file), never
only into a tool's private memory.
