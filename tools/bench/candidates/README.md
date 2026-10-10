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
match the ledger.

Self-test: `tools/bench/selftest_rules_apply.py` (temp fake tree only, never the real files).
