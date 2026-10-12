# Card chat-X11 - implement scope-cwd-fix-20261012 EXACTLY as both sides agreed (chat card: tools/hooks edits allowed)

User 2026-10-12: "동의 받고 고쳐 ... 우선은 조심할것". Both debaters wrote "scope-cwd-fix-20261012 동의" in STATE.agreed,
round 6 of tools/bench/debate/scope-cwd-fix/relay (round_06_claude.md, round_06_gpt.md - READ BOTH in full and the
topic tools/bench/debate/scope-cwd-fix/topic_in.md). Implement the AGREED scope, not the topic's first proposal:

1. Pass the hook payload's `cwd` through: path extraction (tools/scope_header.py launches/_seg_launches/_abs), nested
   PowerShell -Command, the bgrun child, in_tools, and guardcore's R4 (tools/hooks/guardcore.py:183); guard_bash
   offline_scripts_only() and scope_gate() hand it on. No cwd in the payload = today's behaviour exactly.
2. When the normalized cwd != ROOT (the main tree), ONLY a script given as an ABSOLUTE path including the drive, inside
   that cwd's tools/, may be exempt from the 2b timeout rule (also as a bgrun child or inside nested PowerShell). A
   relative path there is NOT exempt; the refusal text then (and only then) tells the caller to use the absolute
   path inside its folder.
3. A cell file that is executed gets the header honesty check (scope_header's existing checks); a failure is a
   scope_gate refusal.
4. No timeout exemption anywhere (main tree included) when the command mixes an unconfirmed tools/ launch, changes
   folder (cd / Set-Location / pushd / Push-Location), or launches a script outside the cwd's tools/.
5. Compatibility: cwd = ROOT single ordinary command (e.g. `py tools/debate_gdoc.py say --dir ... "x"`) keeps today's
   verdict - a representative test.
6. Not in scope, record only: the main-folder Codex hidden-workdir question (write one line in docs/guardcore.md as an
   open item).

Tests: extend tools/bench/selftest_guard_bash_codex.py (and/or a new tools/bench/selftest_scope_cwd.py) with every case
above: cwd=ROOT say passes; folder change / unconfirmed mix not exempt; cwd!=ROOT relative path not exempt (with the
absolute-path hint); cwd!=ROOT absolute path inside its tools/ with a true none header exempt; outside its tools/ and a
false header refused; no-cwd payload unchanged. Then run ALL hook self-tests (selftest_*guard*/*gate*/*protocol*/*card*/
*hook*/*scope*), selftest_guardcore, selftest_guard_bash_codex. selftest_c155_gatefp73 failed before (stage_prerun) -
report, do not diagnose. Read docs/script-writing.md; Edit/Write tools only (no heredoc patches - rule 10).

Record tools/bench/debate/scope-cwd-fix/applied_scope-cwd-fix-20261012.md: agreement lines, changed files with md5 at test
time, test results; verify md5 unchanged at commit. Commit. Return <= 25 lines as text.
