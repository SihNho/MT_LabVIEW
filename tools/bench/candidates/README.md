---
type: guideline
status: draft
date: 2026-10-10
tags: [rules, candidates, apply-path]
---

# Candidate changes to protected files (CANDIDATE device, not active)

Card chat-X6, experiment 2 of discussion structure-equal-02 (agreed in round 6 by both sides,
`tools/bench/debate/structure-equal-02/relay/round_06_claude.md:43`, `round_06_gpt.md:24`): a change to a protected
file (the list is `tools/rules_protected.json`) is only a CANDIDATE until both debaters agree; candidates live here,
apart from the active paths; ONE apply path (`tools/rules_apply.py apply`) compares agreement + hashes + test results
right before copying, and `tools/rules_apply.py audit` finds every protected file whose hash did not come through it.

Nothing here is active yet: no git hook is installed and no hook refuses direct edits. Activation is a later joint
decision of both debaters.

## Layout

```
tools/bench/candidates/<change-id>/
    manifest.json
    files/<repo path>          full copy of the candidate version of each changed file
```

`manifest.json`:

```json
{
 "schema": "rules-candidate/1",
 "change_id": "<change-id>",
 "protected_paths": [{"path": "tools/hooks/guard_bash.py", "base_md5": "<live md5 when the candidate was made, null = new file>",
                      "cand_md5": "<md5 of files/<path>>"}],
 "agreement": {"debate": "tools/bench/debate/<topic>", "round": 4, "token": "<change-id> 동의"},
 "tests": [{"command": "py -u tools/bench/selftest_x.py", "result_line": "RESULT {...}",
            "md5s": {"tools/hooks/guard_bash.py": "<md5 of the file the test ran on>"}}]
}
```

## Commands (all end with a `RESULT {...}` line)

| command | does |
|---|---|
| `py tools/rules_apply.py stage <id> --debate <dir> --round N` | (re)writes `manifest.json` from `files/`: base_md5 from the live file, cand_md5 from the candidate, token `<id> 동의`; keeps recorded tests |
| `py tools/rules_apply.py add-test <id> --command "<cmd>" --log <log> [--md5 path=md5]` | records a test: the log's last RESULT line, md5s from its artefacts plus `--md5` |
| `py tools/rules_apply.py check <id>` | (a) both `relay/round_NN_claude.md` and `round_NN_gpt.md` carry the token in their STATE `agreed` list (exact string); (b) every live file still equals base_md5; (c) every test names every cand_md5 and has a PASS RESULT line; (d) every path is protected; candidate files match cand_md5; no unlisted file under `files/` |
| `py tools/rules_apply.py apply <id>` | check, then copy candidates over the live paths, re-hash, append one line to `tools/bench/rules_ledger.jsonl` |
| `py tools/rules_apply.py audit [--baseline [--dry]]` | hash every protected file and compare with the ledger's last md5: `VIA-APPLY`, `BASELINE`, or `OUT-OF-BAND` (mismatch, never applied, or missing). `--baseline` writes the first ledger entry from the current tree (refused when a ledger exists); `--dry` prints only |

`tools/git_precommit_rules.py` (written and tested, NOT installed) refuses a commit whose staged protected files do not
match the ledger, and a staged ledger whose hash chain is broken.

Self-test: `tools/bench/selftest_rules_apply.py` (temp fake tree only, never the real files).

## Bundle ids, tokens and the hash-chained ledger (card chat-X9, discussion structure-equal-02 round 10)

- **Bundle id** = `<change-id>@<first 8 hex of the md5 of the manifest's canonical core>`; the core is the manifest
  without its `agreement` and `bundle` blocks (paths with base/cand md5s, `rules_apply_md5`, tests). `stage` and
  `add-test` print the id; every change to the staged content gives a new id.
- **Agreement token** = `"<bundle-id> 동의"`, in the last STATE `agreed` list of BOTH relay round files. `check` and
  `apply` take the bundle id, not the change id.
- **Binding**: `check` recomputes the core hash (`bundle-hash`), requires the live `tools/rules_apply.py` md5 to equal
  `rules_apply_md5` (`rules-apply-version`), refuses a token already in the ledger (`token-unused`) and a broken
  ledger chain (`ledger-chain`). `apply` re-hashes manifest, candidates, live files and the device right before
  writing (`prehash:*`) and writes the bytes it hashed.
- **Ledger** `tools/bench/rules_ledger.jsonl` (`chain_checked` in `tools/rules_protected.json`): each line carries
  `prev` = sha256 of the previous line (genesis: 64 zeros) and, for an apply, the sha256 (CRLF folded) of the two relay
  files. `audit` flags a broken chain, a baseline after genesis, a reused token, a relay file changed since the apply,
  an apply whose token is no longer in both STATE agreed lists, an apply line whose md5s are not its bundle's
  cand_md5s, and a live ledger that does not extend the git-committed one.
- `baseline-list --out <file>` writes the STATUS RECORD (`tools/bench/rules_baseline_20261010.json`): every protected
  file with md5 plus the repo version. It is not a ledger entry, not an approval and not an auto-restore target.

## Shell-write guard (candidate `cand-shellguard-01`, NOT installed)

`files/tools/hooks/protected_write.py` (new) holds the one decision; `guard_bash.py` (Claude and Codex shell),
`guardcore.py` (Codex write/patch, R7) and `guard_card.py` (Claude Write/Edit) call it. A shell write to a protected path
or the ledger is refused unless the WHOLE command is `py tools/rules_apply.py apply <bundle-id>` and that bundle passes
`rules_apply.check` with the live device md5 it names. `.claude/settings.local.json` is refused for every agent write.
Verification level: command TEXT (structural); a program that writes a protected file from inside is invisible to
it, and the post-hoc `audit` is the backstop. The real-harness check (sentinel run in the main folder, as in card
chat-X5b) runs only after activation. Self-test: `tools/bench/selftest_shellguard_cand.py`.

## Restore

Restore means one of two things, never the baseline list:

1. **an approved bundle**: re-apply the previous verified bundle (its files are kept under `<change-id>/files/`) through
   `tools/rules_apply.py apply <bundle-id>` with a fresh agreement on a new bundle id;
2. **the pre-install state** of a device that was installed. For the git pre-commit hook, checked 2026-10-10 22:1x:
   `.git/hooks/` holds only the 14 `*.sample` files git ships (`applypatch-msg.sample` ... `update.sample`, including
   `pre-commit.sample`), no `pre-commit`, and `git config core.hooksPath` is unset. Restoring it = deleting the
   installed `.git/hooks/pre-commit` (or unsetting `core.hooksPath` if that is how it is installed). Had a
   `pre-commit` existed, its original bytes would be restored instead.
