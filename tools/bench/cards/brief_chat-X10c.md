# Card chat-X10c - GPT vs Claude benchmark, third attempt: GPT launched with the user's trusted profile `matbench`

Continues chat-X10b (BLOCKED at step 0: in ..\V6_bench\gpt_cell the hook did not run - calls.jsonl empty, the main-tree
probe write RAN; ~/.codex/config.toml has no hooks.state for the cell path; the user's trust step at 12:12 produced the
profile ~/.codex/matbench.config.toml with the same hook command and a trusted_hash). Everything in brief_chat-X10.md and
brief_chat-X10b.md holds (read both, and tools/bench/cards/result_chat-X10b.json), with these changes:

1. GPT launch adds `--profile matbench` (no trust-bypass flag; never edit any ~/.codex file). Use tools/bench/matbench/
   codex_arm.py (built in X10b, selftest 8/0) - extend it, do not copy.
2. Equal conditions: guardcore -> guard_bash treated the GPT payload as a JUDGEMENT session and refused tools/bench
   scripts (x10/step0_offline.log:6), while Claude cells run under the bench-cell marker. Launch codex with the SAME env
   markers the Claude cells get (find them in matbench's Claude launch: BENCH_CELL / MATERIAL marker) and check in step 0
   whether the hook process sees them (the Codex hook payload or env) - if it cannot, report it as an unequal condition
   in the result, do not edit tools/hooks/** (chat-only).
3. STEP 0 again, live, before any task: a harmless command runs and is LOGGED in <cell>/.matbench/calls.jsonl; a write
   into the main tree is DENIED and the file does not exist; `py tools/bench/guardcore_fake/sentinel_lv.py` is denied.
   Any of these failing -> STOP BLOCKED with the evidence (no unguarded GPT task).
4. Then the benchmark as in X10/X10b (T1, T2, T3, T5, T6; Claude arm unchanged; per task the cell checkout, hooks.json
   sha256 prefix 3B8CADE3690E98E8, AGENTS.md = that commit's CLAUDE.md + material.md). Claude weekly % read by the chat:
   0 % at the start of 2026-10-12.
Return the full report as TEXT; commit under tools/bench/matbench/.
