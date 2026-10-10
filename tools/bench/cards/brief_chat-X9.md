# Card chat-X9 - inactive candidate: shell-write refusal for protected files, bundle-bound agreement tokens, append-only ledger, baseline list; isolated tests

User 2026-10-10: "1번 진행". Agreed by Claude and GPT in discussion structure-equal-02, round 10 (relay/round_10_claude.md,
relay/round_10_gpt.md STATE agreed; both done). Builds on card chat-X6 (tools/rules_apply.py, tools/rules_protected.json,
tools/git_precommit_rules.py, tools/bench/selftest_rules_apply.py, tools/bench/candidates/README.md).

NOTHING IS SWITCHED ON: no edit to the ACTIVE hooks (tools/hooks/**), .codex/**, .claude/**, CLAUDE.md, AGENTS.md,
docs/rules/**; no real ledger (tools/bench/rules_ledger.jsonl must not be created); no .git/hooks install. The device files
tools/rules_apply.py and tools/rules_protected.json are NOT active yet (no ledger exists), so they may be edited in place.
No LabVIEW, no hardware. Read docs/script-writing.md; new scripts carry the header block at the TOP.

## Build
1. CANDIDATE hook change under tools/bench/candidates/cand-shellguard-01/files/tools/hooks/ (copies of guardcore.py and,
   if needed, guard_bash.py + manifest.json per candidates/README.md): refuse SHELL writes to protected paths
   (tools/rules_protected.json) - redirection (> >>), Set-Content/Add-Content/Out-File/New-Item/Remove-Item/Copy-Item/
   Move-Item/Rename-Item, cp/mv/rm/tee/sed -i, git checkout/restore -- <protected>, py -c writing a protected path - for
   Claude and Codex payloads alike. The ONLY shell write allowed is `py tools/rules_apply.py apply <bundle-id>` whose
   rules_apply.py md5 equals the version named in the bundle, whose bundle exists and whose targets are its listed paths
   (GPT round 10: "명령 이름뿐 아니라 실행 버전·합의 묶음·대상·시험 결과 확인"). The user's .claude/settings.local.json: every
   agent write (Write/Edit/apply_patch/shell) refused, never in the ledger (Claude round 10).
2. tools/rules_apply.py: agreement token = "<bundle-id> 동의" where bundle-id = <change-id>@<first 8 of the staged
   manifest md5>; `check` binds the staged hash AND re-hashes right before apply; a token already in the ledger is refused
   (no reuse); the ledger is hash-chained (each line carries the previous line's sha256) and `audit` refuses a broken
   chain or an appended line whose agreement does not re-verify against the debate files.
3. tools/rules_protected.json: add .claude/agents/**, .codex/agents/** (both sides' agent definitions), the ledger file;
   settings.local.json as a separate `agent_write_denied` list (not ledger-tracked).
4. Baseline LIST (not the ledger): tools/bench/rules_baseline_20261010.json - every protected file with md5, header
   "status record only - not an approval, not an auto-restore target" (both, round 10).
5. Restore note in tools/bench/candidates/README.md: restore = a verified approved bundle, or the pre-install state (today
   .git/hooks holds only *.sample - check and quote).

## Isolated tests (tools/bench/selftest_shellguard_cand.py, labview none)
Feed REAL PreToolUse JSON (Claude and Codex formats) directly to the CANDIDATE copies (import from the candidate folder,
never the active ones), and run rules_apply on a temp fake tree + temp ledger:
- shell writes to a protected path refused (each form above, both formats); same writes to an unprotected path allowed;
- `rules_apply apply <id>` allowed only with the right rules_apply md5, an existing bundle and its own targets; refused
  with another executable path, a modified rules_apply, a target outside the bundle;
- token reuse refused; staged-vs-live hash mismatch refused; a forged ledger line (edited or appended without agreement)
  flagged by audit; settings.local.json writes refused for every tool kind;
- md5 of EVERY active hook / .codex / .claude file listed before and after the run: unchanged.
Then run the existing selftest_rules_apply.py and selftest_guardcore.py (must stay green).

Return <= 25 lines: files, test counts, before/after active-file md5 check, the .git/hooks state, and OPEN items for the
debaters before activation.
