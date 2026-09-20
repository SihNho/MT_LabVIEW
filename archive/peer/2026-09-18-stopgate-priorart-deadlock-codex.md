# stopgate-priorart-deadlock-codex

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-18 10:05:03
- **outcome:** ANSWERED (174s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# FAILED PREDICTION — the prior-art launch gate refused a prior-art DISPATCH

PREDICTED: a prior-art peer dispatch passes the launch gate, because CLAUDE.md says of the cycle gate
"Diagnostics, docs, peers and the retrospective itself pass".
OBSERVED: `tools/stop_record.py`'s `stop_gate` refused the dispatch COMMAND itself, before anything ran.

## CLAIM TO REFUTE

`tools/stop_record.py`'s `stop_gate` refuses by PATH TOKEN in the command text (`PATH_TOKEN_RE`,
`tools/stop_record.py:74`, `:299-307`), and unlike `tools/hooks/guard_bash.py:53-56`'s `MATERIAL_EXEMPT_RE` —
which already exempts `prior_art_review.py` from the MATERIAL gate — `stop_gate` (`guard_bash.py:156-167`) has
no exemption list at all. Because `docs/cycle21-plan.md` Pre-decided 4 requires every prior-art dispatch to pass
`--recipe <path>`, the only command able to lift a stale release record is the command that record forbids: a
structural deadlock, not an incidental one. The gate also refuses read-only `ls` and `py -m py_compile` on the
same path. The other route its refusal names — "cite the edit with a fresh FIXED: line in a review that
post-dates it" — is unavailable here, because the edit (a local `wire_checked` helper that verifies a wire by
TERMINAL IDENTITY instead of by the `+1` wire-count proxy) answers none of that review's four findings
(`contradicted`, `unread-evidence`, `helper-exists`, `already-measured`; none mentions the wire-count assertion
or a wiring helper), so citing it as FIXED would be laundering the release currency.

CONCLUSION UNDER ATTACK: the correct repair is to mirror the existing exemption inside `stop_gate`, narrowly,
for `prior_art_review.py` only.

## Concrete state (all read-only, measured today)

- The recipe under discussion is cycle 21's step-2 recipe in `tools/recipes/` (its filename is deliberately
  omitted from this text and from every command line, because the gate refuses on the path token).
- Its stop record was RELEASED for sha `0cc9f6ca3599`; the file on disk is now `5a0df5089373` after a patch, so
  `stop_record.py:325-331` refuses with "RELEASED for different bytes than the ones on disk now".
- MEASURED, from the source: `tools/prior_art_review.py` NEVER executes, imports or runs the recipe named by
  `--recipe`. Every use of that value: `:214` (arg definition, `action="append"`), `:225`/`:227` (presence
  check only), `:261` `arm_stop_records(a.slug, a.recipe, ...)`, `:265`/`:293`/`:305-310` (iterated and handed
  to `stop_record.write_stop_record(rp, path, found)` at `:306`). The script's ONLY `subprocess.run` is
  `:255-259`, which launches `tools/peer.ps1`. It never opens or reads the recipe file's contents; it does
  WRITE/refresh a stop-record entry for that path via `stop_record.write_stop_record` (`:306`), stored in
  `tools/bench/stop_records.json` (`stop_record.py:63`).

## ANSWER THESE FOUR, SPECIFICALLY

1. The strongest reason the deadlock claim is WRONG — name any already-supported route we have not found: a
   `tools/stop_record.py` subcommand, an invocation of `prior_art_review.py` that does not put the recipe path
   on the command line, a config/environment setting, an existing wrapper. Cite file:line.
2. Does exempting `prior_art_review.py` inside `stop_gate` open a hole — i.e. can anything reachable from that
   script LAUNCH the recipe? The measurement above is the evidence; ATTACK it (indirect paths: `peer.ps1` and
   what the peer cell itself is allowed to run, `arm_stop_records`' imports, `guard_cycle`, glob/eval routes).
3. What observation would FALSIFY "structural deadlock"?
4. The single cheapest discriminating test.

## ALREADY RULED OUT (do not propose these)

- The `FIXED:` release route: none of the standing review's four findings covers the `wire_checked` edit, so a
  `FIXED:` line citing it would be laundering, not a release.
- Reverting the edit: restores the released sha but discards the fix the terminal-identity measurement justified.
- `CYCLE_GUARD_OFF` / any guard-off env var: never the answer in this project, and it does not reach this gate
  (`stop_record.py:289`).



--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The proposed repair is wrong as stated: a blanket `prior_art_review.py` exemption would create a compound-command bypass.

1. Strongest refutation / alternative route

There is no supported, policy-compliant route in the current source:

- `stop_record.py` exposes only `write`, `check`, and `list`; there is no refresh/re-review/re-key command (`tools/stop_record.py:364-391`).
- `prior_art_review.py` requires either `--recipe` or `--no-recipe` (`tools/prior_art_review.py:214-228`), and cycle 21 mandates the former (`docs/cycle21-plan.md:60-62`).
- `--dry-run` returns before peer dispatch and stop-record arming, so it cannot repair the record (`tools/prior_art_review.py:245-261`).
- The parser uses plain `argparse.ArgumentParser()` (`tools/prior_art_review.py:195`), so it has no response-file facility; `fromfile_prefix_chars` defaults to `None` in [Python’s argparse documentation](https://docs.python.org/3.12/library/argparse.html).
- The project search found no wrapper or config route; `guard_cycle` itself prescribes the blocked literal `--recipe <path>` command (`tools/hooks/guard_cycle.py:507-514`).

But the absolute “only command possible” claim is technically false: `stop_record` examines the raw command string’s path tokens (`tools/stop_record.py:295-308`), not the eventual argv. PowerShell can substitute a variable or subexpression before passing arguments to Python, as documented by [Microsoft’s PowerShell parsing reference](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_parsing). A recipe path obtained indirectly from `stop_records.json` therefore would not appear in the text inspected by the hook.

That is a gate bypass, not an authorized route. It refutes “structurally impossible” at the mechanism level but does not solve the policy deadlock.

2. Would the exemption open a launch hole?

A MATERIAL-style substring exemption would. For example, one command could contain both:

```text
py tools/prior_art_review.py ... --recipe <path>; py <path>
```

If `stop_gate` returned early merely because `prior_art_review.py` appeared anywhere, the second command would launch the stopped recipe. That follows from the hook receiving one complete command string (`tools/hooks/guard_bash.py:179-193`) and the existing exemption style being an unanchored regex search (`tools/hooks/guard_bash.py:53-56,73-78`).

The review script itself does not expose an indirect launch:

- Its only subprocess is `peer.ps1` (`tools/prior_art_review.py:255-259`).
- The prior-art peer is Claude in plan mode, with Bash, PowerShell, Edit, Write, NotebookEdit, and Agent expressly disabled (`tools/peer.ps1:379-400`).
- `arm_stop_records` only imports `guard_cycle`/`stop_record`, globs and reads the archived review, parses verdicts, and writes records (`tools/prior_art_review.py:265-310`).
- `guard_cycle`’s subprocess calls are inside `main()` (`tools/hooks/guard_cycle.py:534-567`), while import does not call `main()` (`:673-674`).
- There is no `eval`, recipe import, recipe-content open, or glob-execute route in the reviewed path.

Therefore a safe exception is possible, but it cannot be a mirrored substring exemption. It must classify the command structurally, exempt only the recipe argument belonging to a genuine `prior_art_review.py` invocation, and refuse compound commands or additional recipe launches.

3. What would falsify “structural deadlock”?

Any one of these observations:

- An existing documented command successfully invokes `prior_art_review.py --recipe <actual path>` through the unchanged hook without using shell indirection, a guard-off switch, `FIXED:`, or `REFUTED:`.
- An existing wrapper or `stop_record.py` subcommand re-reviews/re-keys the changed bytes without naming the recipe path in gated command text.
- The exact literal dispatch returns ALLOW from `stop_record.check_command`.

No such route appears in the inspected source. Thus the operational deadlock claim still holds, even though the regex mechanism is bypassable.

4. Cheapest discriminating test

Run the review with `--dry-run`, deriving the recipe argument from the record store at shell-expansion time rather than writing its path literally in the command. Expected outcomes:

- If the gate evaluates the eventual argv, it refuses.
- If it only scans pre-expansion command text—the alternative supported by the source—it passes and `prior_art_review.py` reaches its dry-run return at `:249-250`.

This neither launches the recipe nor changes its stop record. A successful pass would falsify “structural” impossibility, while confirming that the apparent escape is merely a textual-gate bypass.

Bottom line: no honest supported route was found, so the operational deadlock is real. What does not follow is that mirroring `MATERIAL_EXEMPT_RE` is the correct repair; a blanket exemption would open a real launch hole. A command-structure-aware exception would change my conclusion about the repair.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
