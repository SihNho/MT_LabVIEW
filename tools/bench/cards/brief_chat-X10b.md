# Card chat-X10b - GPT vs Claude benchmark, retry with the FIXED trusted GPT cell

Continues card chat-X10 (BLOCKED: a GPT cell in a %TEMP% worktree has untrusted hooks = unguarded; the trust bypass was
refused). User 2026-10-11/12: "그냥 agent를 수정하는게 맞는거 아님?" -> "진행해" -> "훅 설정 했음" (the user trusted the cell's
hook with /hooks in Codex). Everything in tools/bench/cards/brief_chat-X10.md still holds (read it); this brief changes
only the GPT arm's place and start instruction. No LabVIEW, no hardware, offline tasks only (T1, T2, T3, T5, T6; T4 dropped).

## The fixed GPT cell
- Folder: G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_bench\gpt_cell (a git worktree).
- Its .codex/hooks.json is byte-identical to now: sha256 prefix 3B8CADE3690E98E8. It calls the MAIN tree's
  tools/bench/matbench/codex_cell_hook.py = cell_guard --codex (the replay card's rules, the same as the Claude cells) and
  then tools/hooks/adapt_codex.py (guardcore); fail closed. NEVER change that file's bytes (the trust is tied to it) -
  after each per-task checkout (`git -C <cell> checkout -f --detach <task base commit>` and `git -C <cell> clean -fdx -e
  .codex -e .matbench`) rewrite .codex/hooks.json with exactly these bytes and check the sha256 prefix before launching.
- Per task, BEFORE launching GPT: write <cell>/AGENTS.md = that base commit's CLAUDE.md + a separator + that commit's
  .claude/agents/material.md (what the Claude cell gets). Codex reads AGENTS.md itself; the task prompt carries no
  role override. The main tree's AGENTS.md is never touched.
- GPT launch: `node <codex.js> exec --json --skip-git-repo-check -m gpt-6.1-sol -c model_reasoning_effort="high"
  -s danger-full-access -C <cell> -` (no trust bypass flag). Tasks run one after another in this single cell.

## Step 0 - prove the hook really runs in the cell (before any task)
1. Offline: feed codex_cell_hook.py fake Codex payloads (cwd = the cell): a read -> allowed; an apply_patch adding a file
   inside the cell -> allowed; an apply_patch writing into the MAIN tree -> denied; `py tools/bench/guardcore_fake/
   sentinel_lv.py` -> denied; an unknown tool -> denied. Quote outputs.
2. Live: one short codex exec in the cell asking it to (a) run a harmless command and (b) write a file into the main
   tree's tools/bench/matbench/ (must be denied). Show <cell>/.matbench/calls.jsonl got lines for both calls and that
   the main-tree file does not exist. If calls.jsonl stays empty, the hook did NOT run (trust not effective) - STOP,
   report BLOCKED with the evidence; do not run tasks unguarded.

## Measure (as brief_chat-X10.md) and report
Per task x arm (x2 if time): blind score (matbench key, A/B mapping recorded), minutes, retries / refused calls (from
calls.jsonl for both arms), tokens, Claude USD, GPT rate_limits used_percent first/last (codex json token_count events
or ~/.codex/sessions rollout files). The chat reads the Claude weekly % before (0 % at 2026-10-12 07:xx, just reset) and
after. Return the full report as TEXT (sub-agents cannot write report files); commit driver changes, raw outputs and
logs under tools/bench/matbench/.
