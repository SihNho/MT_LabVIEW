# Card chat-X2 - common guard code + Codex adapter, tested on fake targets (user 2026-10-10 "좋음. 진행하도록")

Runs in the MAIN tree after the runner stopped (cycle 165 finished, STATUS STOP line in force). This chat card MAY edit
tools/hooks/** (the runner-card ban does not apply to chat cards; the chat tells the user, who approved this plan after
being told hooks are tested with fake targets and the rig needs no disassembly). Read docs/script-writing.md first; new
tools/ files carry the header block at the TOP (# --- / # labview: none / # hardware: none / # ---). NEVER start LabVIEW,
never open a real serial/COM port, never call a real motor script: every forbidden-command test targets a FAKE
(nonexistent port such as COM99, or a sentinel script that only writes a marker file under tools/bench/guardcore_fake/).
Card chat-X1 runs at the same time and owns CLAUDE.md, AGENTS.md, docs/rules, docs/decisions, docs/START.md - do not
edit those.

## Why
Discussion token-efficiency-01 converged (tools/bench/debate/token-efficiency-01/relay/round_16_claude.md +
round_16_gpt.md, STATE agreed): the project must run from Claude Code OR Codex sessions with the SAME safety rules.
Agreed design: one common judgement code + per-backend adapters; Codex `apply_patch` is caught by a Write|Edit-type
matcher but its patch body must be converted to the file-check form, and BOTH old and new paths of
modify/delete/rename are checked; the .vi/.ctl/.lvlib/.lvproj write ban moves from .claude/settings.json permissions
into the hook code; the final allowance is the common executor's check (script version, card, target, timeout) and
inline-string checks are secondary; the report states the level "executor path verified / outside the executor only
secondary defence". Runner cards never edit hook files - this must cover the Codex hook files too (keep them under
tools/hooks/ so never_in_runner_globs in tools/bench/assign/assign_config.json covers them; verify).

## Steps
1. FACTS FIRST (external search mandatory; cite sources): Codex CLI hooks in the installed 0.162.0 (package under
   C:\Users\KimLab\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\npm\node_modules\@openai\codex - read its
   docs/changelog/schema) and developers.openai.com/codex: a PreToolUse-type hook? configured where (user
   ~/.codex/config.toml vs project .codex/)? stdin JSON fields, tool names (shell / exec_command / apply_patch / others),
   matcher syntax, deny response format and exit codes, fail-open vs fail-closed on hook error. If no blocking hook
   exists, say so and list what Codex offers instead (sandbox modes, approval policy, exec policy rules); do not invent.
2. Read the Claude hooks (.claude/settings.json hooks; tools/hooks/guard_bash.py, guard_write.py, guard_peer.py,
   guard_session.py, guard_cycle.py, guard_card.py and the deny rules at .claude/settings.json:27-35). Build
   tools/hooks/guardcore.py: normalized event {backend, tool_kind: shell|write|edit|patch|agent|read|other, command,
   paths (old and new), content, cwd, env flags} and judge(event) -> (allow|deny, reason) calling the EXISTING decision
   functions of the guards (refactor minimally into importable functions if needed) plus the .vi-family write ban.
   Unknown tool names: deny (fail closed) unless on an explicit read-only allow list. Adapters tools/hooks/adapt_claude.py
   (Claude PreToolUse JSON in/out) and tools/hooks/adapt_codex.py (Codex hook JSON in/out; apply_patch body -> per-file
   old/new paths + new content). Claude's live behaviour must NOT change: keep .claude/settings.json pointing at the
   current hook scripts unless the adapter is proven identical by step 3; keep the settings deny rules as an extra layer.
3. TESTS tools/bench/selftest_guardcore.py (labview none): fixture bundle of forbidden AND allowed (positive control)
   cases, each in BOTH Claude and Codex formats: bare LabVIEW command without bgrun/timeout, motor script called directly
   instead of tools/motor_gate.py, inline COM/SerialPort in a command, a second concurrent LabVIEW launch,
   Write/Edit/apply_patch (add, modify, delete, rename) touching a .vi or an originals path, edits to tools/hooks/** under
   a runner-card env flag, unknown tool name; plus ordinary allowed reads/edits/commands. Assert identical verdicts
   across formats, every forbidden case denied, every positive control allowed. Run the existing hook self-tests (find
   them: tools/bench/selftest_*) to show no regression.
4. FAKE EXECUTOR: show the common executor path (tools/bgrun.py and the launch gates in guard_bash / stage_prerun
   check_launch) refuses: bypass (a recipe without bgrun), inline COM, a run left past its timeout, a concurrent run -
   sentinel targets only. Record which of the four executor checks (script version, card, target, timeout) exist today
   and which are missing; do NOT build a new executor in this card, list the gap.
5. INSTALLED-VERSION CHECK: if Codex has a blocking hook and it can be configured at PROJECT level, configure it in the
   repo (inside tools/hooks/ or the project .codex/ dir), then run one real `codex exec` (node <codex.js> exec --json
   --skip-git-repo-check -m gpt-6.1-sol -s danger-full-access -C <project root> -, codex.js under the MSIX npm path above,
   0.162.0) asking it to run each forbidden sentinel command and one allowed command; quote the denials and show the
   sentinel markers were NOT created and the allowed one ran. Timeout every call (<= 5 min). If only the user-level
   ~/.codex/config.toml works, STOP before changing it and report - the user's global Codex config is not ours to change.
   Commit.

Return <= 30 lines: commit hash, Codex hook facts with sources, files created/changed, test counts (cases x formats,
pass/fail), regression result, real-Codex check result (or why not run), executor-check gap list, the verification-level
sentence, OPEN: what the chat must decide (e.g. switch Claude's settings to the adapter; user-level Codex config).
