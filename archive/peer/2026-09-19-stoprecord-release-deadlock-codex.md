# stoprecord-release-deadlock-codex

- **agent:** codex
- **role:** (n/a)
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-19 01:22:14
- **outcome:** ANSWERED (140s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# FAILED PREDICTION — a fresh prior-art record over the edited bytes did NOT release the launch

NOTE ON ROUTE (so no command you suggest is refused before it runs): this task travels as a FILE, because
`tools/stop_record.py`'s launch gate refuses any COMMAND TEXT containing a path token that matches a stopped
recipe. Do not propose remedies that require typing that path on a command line.

PREDICTED (by the judgement session, cycle 38): running a NEW prior-art review over the EDITED recipe bytes,
and planting a fresh stop record for those bytes, would release the launch of build run 6.
OBSERVED: it did not. The launch is still refused, by the OLD record, which is already stamped `released` for
the PRE-EDIT bytes.

## CLAIM TO REFUTE (verbatim)

"`tools/stop_record.py::_check():318-331` compares the OLD record's already-stamped `released.sha256` against
the on-disk sha AFTER `_released()` has run, so once a recipe has been released and then edited, no `FIXED:` /
`REFUTED:` line in any newer review can ever release it again; the only exits are (a) revert the file to the
released bytes, (b) hand-edit the record, or (c) launch under a NEW recipe path that has no stop record — and
the gate additionally refuses `py tools/stop_record.py write --recipe <path>` and even a plain `grep <path>`,
because it matches on any command text containing the recipe path."

## THE SPECIFIC QUESTION

Is exit (c) — carrying the corrected bytes into a NEW recipe file (v2 -> v3) and launching that — the workflow
this gate was DESIGNED for (the project's own history is that v0 -> v1 -> v2 were each a NEW FILE, each getting
its own prior-art review and its own record), or is it exactly the laundering the gate exists to stop (a path
rename that erases a standing stop record's reach without answering its findings)?

Answer that in one sentence, then give your single strongest reason the CLAIM ABOVE IS WRONG.

## MEASURED STATE (all read-only, today)

- Recipe under discussion: the cycle-38 D1 route-B build recipe under `tools/recipes/` (filename deliberately
  omitted from this text — the gate matches path tokens).
- Its sha256 when the run-5 prior-art review saw it: `9ff90ded8f01…` for v1, `76e1252e3de3…` for v2 at release.
- Four cycle-38 patches then edited it; sha on disk now `5620e626a95d…`.
- Record A (old): `reviewed_sha256 = 76e1252e3de3…`, `review_file = archive/peer/2026-09-18-priorart-d1-routeb-run5.md`,
  `released = {"sha256": "76e1252e3de3…", …}` (stamped at run 5's launch).
- Record B (new, planted this cycle): same `recipe_path`, `reviewed_sha256 = 5620e626a95d…`,
  `review_file = archive/peer/2026-09-19-priorart-d1-routeb-run6.md`, verdict 4 findings, `released = null`.
- `_check()` iterates ALL records whose `keys_for(recipe_path)` meet a path token in the command; record A
  reaches `:323-331` and returns False before record B is ever considered.

## ALREADY RULED OUT (do not re-propose these three)

1. A seventh `FIXED:` line in the run-5 review — refused: `_released()` passes, then `:323` compares the
   ALREADY-STAMPED release sha to the disk sha, so release lines are never re-read for a stamped record.
2. `CYCLE_GUARD_OFF` — does not reach this gate (`tools/stop_record.py:289`).
3. Re-running prior art over the edited bytes — DONE; record B's `released` is null and record A still refuses.

Also already reviewed, for context, NOT to be repeated: `archive/peer/2026-09-18-stopgate-priorart-deadlock-{codex,opus}.md`
(the deadlock on the DISPATCH command; its route 4, hand-editing `released` to null, was left to judgement).

## WHAT TO ATTACK

- Find a route in the repository's own code that releases the edited bytes WITHOUT hand-editing the store and
  WITHOUT renaming the recipe. If one exists, cite file:line and the exact command or edit.
- If exit (c) is laundering, say what the project should do instead, given that the four findings of the NEW
  review are all being answered by code changes in this same cycle.
- Name what observation would falsify your answer, and the cheapest test that discriminates it.



--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Exit (c) is the project’s intended versioned-recipe workflow when the new file’s exact bytes receive their own review and stop record; renaming without that review would be laundering.

The strongest reason the claim is wrong is its assertion that (a)–(c) are the only exits: the code plainly intended a fresh same-path review to work—its refusal instructs “Get the edited recipe reviewed” ([stop_record.py:329](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/stop_record.py:329>)), and `write_stop_record()` deliberately appends a record for a different hash ([stop_record.py:203](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/stop_record.py:203>)). `_check()` simply lacks the corresponding supersession rule.

The appropriate fourth exit is to fix `_check()`, not hand-edit its data. Change the loop at line 306 to track the record index, and before the mismatch refusal at line 325 defer a released obsolete record when a later record exists for the same normalized path:

```python
for i, record in enumerate(records):
    ...
    if rel.get("sha256") == cur:
        continue
    later_same_path = any(
        _rel(r.get("recipe_path")) == _rel(record.get("recipe_path"))
        for r in records[i + 1:]
    )
    if later_same_path:
        continue
    return False, _refusal(...)
```

Record B would then be evaluated normally: it blocks until all four findings have valid `FIXED:`/`REFUTED:` dispositions, after which lines 319–321 stamp the corrected bytes. Unreleased older findings are not bypassed; only an already-released obsolete record is superseded.

The alternative explanation of today’s evidence is therefore an implementation omission: Record A short-circuits before the deliberately supported later record can govern. The plan requires edits not to clear a record ([cycle18-plan.md:53](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/cycle18-plan.md:53>)), but it never says an older released record permanently poisons that pathname. Project history explicitly describes the new-filename maneuver as intentional ([build_d1_routeb_v2.py:185](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_d1_routeb_v2.py:185>)).

What would falsify this answer is a binding plan clause or acceptance test requiring predecessor records to follow renamed/versioned successors as one recipe family. No such aliasing exists in `keys_for()` or the six documented acceptance cases.

After attacking it, I believe the claim’s mechanical diagnosis of the current unpatched `_check()` holds, but its exhaustive “only exits” conclusion does not. The cheapest discriminating test is an isolated temporary-store unit case: old released record, later same-path record with valid dispositions, edited bytes—current code must refuse on the old record, while the supersession edit must evaluate and release through the later one.

## Sources

(extract from answer)

## What was done with it

ACCEPTED AND APPLIED, cycle-44 judgement session, 2026-09-19. The fault is real and measured twice — cycles 42 and 43 each needed a filename rename to relaunch a recipe whose bug fix judgement had already released — and the cycle-43 retrospective scored it `device-failed` (threshold 1): a gate that refuses the legitimate path while a rename walks straight past it is broken, not strict. The patch is accepted as written because it narrows nothing the gate exists for: an undisposed older record still blocks, and the later record still blocks until its own findings carry valid FIXED:/REFUTED: lines. Its `unverified` verdict is answered by the review's own cheapest test, run as a three-case unit test before the patch is trusted — (1) old released record + later same-path record fully disposed + edited bytes: unpatched REFUSES, patched RELEASES; (2) later record present but NOT disposed: patched MUST STILL REFUSE; (3) no later record for that path + edited bytes: patched MUST STILL REFUSE. Cases 2 and 3 are the over-release guards and are judgement's addition, not the review's. This is a REPAIR of an existing device; the user's standing 2026-09-18 08:53 'no more devices' order is read as governing NEW machinery, and that reading is flagged to the user in STATUS NEXT for the second cycle running.
