---
type: reference
status: current
date: 2026-10-10
tags: [hooks, codex, safety]
---

# guardcore - one guard for Claude Code and Codex (card chat-X2)

User 2026-10-10 "좋음. 진행하도록", after discussion token-efficiency-01 agreed: the project must run from Claude Code OR
Codex with the SAME safety rules.

## Files

| file | role |
|---|---|
| `tools/hooks/guardcore.py` | `judge(event) -> (allow/deny, reason)`. Calls the EXISTING guards through their `main()` (shell: guard_bash, guard_peer, guard_cycle; write/edit/patch per path: guard_card; Agent/Task: guard_card + guard_session) plus R1 .vi-family write ban, R2 originals path ban, R3 runner sessions never write hook files (never_in_runner_globs + `.codex/**`, `.claude/settings*.json`), R4 no LabVIEW-scoped launch while a LabVIEW process runs, R5 unknown tool = deny, R6 unparseable patch = deny. |
| `tools/hooks/adapt_claude.py` | Claude PreToolUse JSON -> event -> exit 2 + stderr. NOT wired into `.claude/settings.json` (the chat decides the switch). |
| `tools/hooks/adapt_codex.py` | Codex PreToolUse JSON -> event -> deny JSON on stdout, exit 0. `apply_patch` body parsed into Add / Delete / Update / Update+Move (both rename paths judged). Own crash = deny. |
| `.codex/hooks.json` | PreToolUse group 1 (no matcher = every tool) runs adapt_codex.py. Group 0 (guard_bash, trusted by the user) is byte-identical. |
| `tools/bench/selftest_guardcore.py` | 31 pairs x 2 formats + parser, R4 and adapter-I/O gates. |
| `tools/bench/guardcore_fake/` | sentinel targets (write a marker only), `fake_executor.py`, `codex_live_check.py`. |

## Codex 0.162.0 hook facts

- Events: PreToolUse, PermissionRequest, PostToolUse, PreCompact, PostCompact, SessionStart, SessionEnd, UserPromptSubmit, SubagentStart, SubagentStop, Stop, Interrupt (strings in the installed `codex.exe`).
- Config: `hooks.json` or `[hooks]` in `config.toml`, user layer `~/.codex/` or project layer `<repo>/.codex/` (project layer only when the project is trusted - this one is, `~/.codex/config.toml` `[projects.'g:\...\v6_parallelloop'] trust_level = "trusted"`).
- Hook trust: every non-managed hook is hashed and SKIPPED until reviewed in the TUI (`/hooks`); the trust record is written to the USER's `~/.codex/config.toml` (`[hooks.state.'<file>:pre_tool_use:<group>:<handler>'] trusted_hash`). An edit of a handler resets it. `codex exec --dangerously-bypass-hook-trust` runs untrusted hooks for one invocation without persisting.
- stdin: `session_id, turn_id, cwd, hook_event_name, model, permission_mode, transcript_path, tool_name, tool_input, tool_use_id` (+ `agent_id, agent_type` strings present in the binary).
- Tool names: shell = `Bash` with `tool_input.command`; file edits = `apply_patch` (exact `tool_input` shape not documented; the adapter searches it for `*** Begin Patch`); MCP = `mcp__<server>__<tool>`. Matcher = regex on `tool_name`; no matcher = all tools.
- Deny: stdout `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"..."}}`, exit 0. Exit 2 + stderr is also a block in the docs, but was reported to FAIL OPEN on Windows in 0.144.x; a deny without a non-empty reason is rejected.
- Fail mode: any other non-zero exit, invalid JSON or an untrusted hook = logged and SKIPPED (fail open). Default timeout 600 s.

Sources: installed binary strings (`node_modules/@openai/codex-win32-x64/.../codex.exe`, 0.162.0); codex.danielvaughan.com 2026-05-25 "Codex CLI Hooks After GA"; Dicklesworthstone/destructive_command_guard `docs/codex-integration.md`; web summary of openai/codex issue #16732 / PR #18391 (apply_patch hooks). `developers.openai.com/codex/hooks` redirects to learn.chatgpt.com, which the permission layer refused to fetch.

## Payload cwd (scope-cwd-fix-20261012, card chat-X11)

guard_bash (scope_gate, offline_scripts_only) and R4 hand the payload's `cwd` to `tools/scope_header.py`: relative
script paths resolve against it; a folder change or an unconfirmed / outside-tools launch is never timeout-exempt; when
cwd is not the main tree only a drive-absolute path inside its `tools/` is exempt and a cell script gets the honesty
check. Record: `tools/bench/debate/scope-cwd-fix/applied_scope-cwd-fix-20261012.md`.

**OPEN (not fixed by this change, both debaters agreed to record it only, round 6):** a Codex shell call may carry its
own `workdir` argument that the hook payload does not show (hook `cwd` = the session's start folder; reported for
0.144/0.145 in openai/codex issues the debaters could not confirm, not measured on 0.162.0). A MAIN-folder Codex
session (cwd = ROOT) still gets the relative-path exemption, so its relative `py tools/...` is judged against ROOT
even if a hidden workdir points elsewhere. Unblock: measure a harmless call with a changed workdir and read its payload.

## Verification level

EXECUTOR PATH VERIFIED / OUTSIDE THE EXECUTOR ONLY SECONDARY DEFENCE. Command-string checks see text, not what a process
does; the final allowance is the executor's (bgrun deadline + `stage_prerun.check_launch`). Executor gaps (script
version outside stage scripts, card check inside bgrun, target exclusivity) are listed in `result_chat-X2.json`.
