# Card chat-X6 - experiment 2 of discussion structure-equal-02: ONE apply path with agreement/hash/test check + audit, built as a CANDIDATE

User 2026-10-10: "이후 2~4번도 진행하도록". Agreed in structure-equal-02 (relay/round_06_*.md STATE agreed, both sides):
- joint-agreement scope: rules (docs/rules/**), CLAUDE.md, AGENTS.md, both harnesses' hooks and settings (tools/hooks/**,
  .codex/**, .claude/settings.json), the protected list itself, the check and apply devices;
- a new policy is only a CANDIDATE until both agree; candidates live apart from the active paths;
- ONE apply path compares agreement + hashes + test results right before applying, refuses other writes, and an audit
  afterwards finds hash mismatches; reports separate "came through the verified apply path" from "found afterwards".
- the user may put one specific change to both sides; both agreeing = apply before the discussion ends (first case:
  tools/bench/debate/structure-equal-02/applied_guardcore-fix-20261010.md).

THIS CARD BUILDS THE DEVICE AS A CANDIDATE AND PROVES IT ON A SANDBOX COPY. It does NOT activate anything: it does not
install a git hook in .git/, does not change tools/hooks/**, .codex/**, .claude/**, CLAUDE.md, AGENTS.md or docs/rules/**.
Activation is a later joint decision of both debaters. No LabVIEW, no hardware. Read docs/script-writing.md; new tools/
scripts carry the header block at the TOP.

## Build (all new files)
1. tools/bench/candidates/README.md: the staging layout - tools/bench/candidates/<change-id>/files/<repo path> (full candidate
   copies) + manifest.json {change_id, protected_paths:[{path, base_md5, cand_md5}], agreement:{debate, round, token
   "<change-id> 동의"}, tests:[{command, result_line, md5s}]}.
2. tools/rules_apply.py (labview none): `check <id>` - (a) both relay/round_NN_claude.md and round_NN_gpt.md of the named
   debate carry the token in their STATE agreed list (parse the STATE json, exact string); (b) every live file's md5 equals
   base_md5 (no drift since the candidate was made); (c) every test entry names the cand md5s and has a PASS RESULT line;
   (d) every changed path is in the protected list. `apply <id>` - check, then copy the candidates over the live paths,
   re-hash, append one line to tools/bench/rules_ledger.jsonl {id, time, paths+md5, agreement, tests}. `audit` - hash every
   protected path (glob list in ONE place, tools/rules_protected.json) and compare with the ledger's last applied md5;
   print OUT-OF-BAND for each mismatch or each protected file never applied (baseline mode `audit --baseline` writes the
   first ledger entry from the current tree, marked baseline). Every command ends with a RESULT line.
3. tools/rules_protected.json: the protected globs above (+ tools/rules_apply.py and tools/rules_protected.json themselves).
   OPEN for the chat: whether .claude/agents/** and .claude/settings.local.json (the user's own) belong in it - list, do not decide.
4. A candidate pre-commit check tools/git_precommit_rules.py (labview none) that refuses a commit whose staged protected
   files do not match the ledger - written and tested, NOT installed.
5. tools/bench/selftest_rules_apply.py: on a temp copy of a small fake tree (never the real files): apply with matching
   agreement/hashes/tests -> applied + ledger line; refused when one side's token is missing, when GPT wrote it in `open`
   instead of `agreed`, when a live file drifted, when a test md5 differs from the candidate, when a path is not
   protected; audit flags an out-of-band edit; the precommit check refuses a mismatching staged file and passes a
   matching one. Also run `rules_apply.py audit --baseline` against the REAL tree in dry form (print only, no ledger
   write) and quote how many protected files it found.

Return <= 25 lines: files, self-test counts, the dry baseline count, and OPEN: what the debaters must decide to activate
(git hook install, guardcore rule refusing direct edits to protected paths, the open list items).
