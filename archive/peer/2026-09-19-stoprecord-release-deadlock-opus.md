# stoprecord-release-deadlock-opus

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.2492  in 26 / out 32375 / cache-create 173566 / cache-read 1314316  (461s, 23 turn(s))
- **date:** 2026-09-19 01:29:57
- **outcome:** ANSWERED (462s)
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

Write is disabled for this role (read-only peer), so the review is here rather than in a file. Nothing was run, opened, edited, or locked.

---

# Failed-prediction review — "a fresh record over the edited bytes did not release run 6"

## The specific question, one sentence

Exit (c) is the workflow this gate actually *has* — a path-keyed store can only spell "new bytes, reviewed" as a new key, and the project has done exactly this three times (`tools/recipes/build_opfstunnelterm_v1.py:12-18`, `…_v2.py:20-26`, `tools/recipes/build_d1_routeb_v2.py:185-194`) — **but v2 is the first path in this project's history that would be renamed while carrying an UNRELEASED record**, so it is the designed workflow *only if* record B's four findings are disposed on `build_d1_routeb_v2.py` before the bytes move, and laundering if they are not.

## 1. Strongest reason the claim is WRONG

**Its evidence is wrong in the one field its diagnosis turns on.** The brief states record A has `reviewed_sha256 = 76e1252e…`. The store says:

- `tools/bench/stop_records.json:96` — `"reviewed_sha256": "e4fc5bb197efcffa440e18f2dafda4df0bee1a0d54937e51567425d23419e81e"`
- `tools/bench/stop_records.json:92` — `"released": {"sha256": "76e1252e3de3…"}`

Different hashes. The run-5 review read `e4fc5bb1`; the gate released `76e1252e`. The six patches in between are documented in the recipe itself (`build_d1_routeb_v2.py:203-205`, "RUN 5, SECOND PATCH … Six further changes, all in THIS file").

So the state is **not** "reviewed, released, then edited." It is: `_check` stamped as *released* whatever sat on disk at first launch — `tools/stop_record.py:319-321` writes `{"sha256": cur}` with no comparison to `reviewed_sha256`. Record A's `released` records **who launched first**, not what was reviewed. The claim treats that stamp as authoritative and builds its whole story on it; the story's *prediction* is right by luck, which is why the error survived.

Stated fairly so this isn't overclaimed: `FIXED:` *requires* the cited file to have changed after the review (`guard_cycle.py:113`), so stamp ≠ reviewed is unavoidable by construction. The defect is narrower and real — the stamp blesses **every** post-review edit, not only the ones a `FIXED:` line cites. Record A's stamp covers six changes; its release line names one (`stop_records.json:91`).

Two further corrections:

- **"even a plain `grep <path>`" is true only of shell commands.** `guard_bash.py:208` returns 0 unless `tool_name` is `Bash`/`PowerShell`. This review read the recipe, the store and both reviews with no refusal. "You can't even look at it" is false — and that is what makes §6 executable.
- **`--recipe` is not "mechanically unusable"** (`STATUS.md:24`). `_check` refuses only when a *standing record's* path meets a token (`stop_record.py:306-307`). A v3 has no record, so `prior_art_review.py --recipe …_v3.py` runs. STATUS generalises a measurement taken on a stopped path.

## 2. Alternative explanation of the same evidence

**The gate is path-keyed, not content-keyed.** `stop_record.py:313` hashes `record["recipe_path"]` — the record's own path — never the file the command names. Under this reading the refusal is not a trap; it is the store saying the only thing it can say: *this key's content is not the content I released.* A new key is then not an escape from review, it **is** the release, spelled the only way the store can spell it — honest or dishonest according to whether the new key gets its own answered review, which record B already is, one path early.

This also explains the history without bad faith: the three prior renames each escaped a *stale hash* on an already-RELEASED record (`stop_records.json:18-22`, `:35-39`, `:70-74` — all released, none with a sibling open record). None stepped over an open verdict. Record B is the first.

The two readings are separated by one number: `released.sha256 == reviewed_sha256`? It is not.

## 3. What I could not find — plainly

**There is no in-code route that releases the edited bytes without a store edit or a rename.** Exhaustively:

- `_check` refuses on the **first** matching record and returns before `save_records` (`:325`, `:332`); record B is never reached. Reordering the store fails too — every matching record must pass, and A's sha test still fails.
- Only `write_stop_record` clears `released`, and its update branch **preserves** it (`:227-234`); that branch needs disk hash `== e4fc5bb1`, i.e. a revert, and even then the stamp survives.
- `_released()` runs before the sha test, so no seventh `FIXED:` line matters — ruled-out item 1 is correct. I confirmed `_released(A)` passes: all six slugs have valid release lines at `archive/peer/2026-09-18-priorart-d1-routeb-run5.md:362-367`.
- `CYCLE_GUARD_OFF` doesn't reach it (`guard_bash.py:167-168`), and the second call site `guard_cycle.py:551` shares the function.

The claim's **mechanism** holds. Its **diagnosis** and **exit list** do not.

## 4. Falsifier

Falsified if `check_command("<launch naming build_d1_routeb_v2.py>")` returns **ALLOW** after run6.md gets valid release lines for B's four slugs, with no store edit, revert or rename. My prediction: REFUSE, with A's *"RELEASED for different bytes"* naming `76e1252e` / `5620e626` (`:325-331`). My own framing is falsified the other way: a *"neither refuted nor fixed"* refusal (`:311-312`) would mean `_released(A)` fails and the trap is in the review file, not the stamp.

## 5. Cheapest discriminating test (~2 min, no LabVIEW, no lock)

Copy `tools/bench/c20_release_probe.py` / `c22_v1_gate_probe.py`. Note `c22_v1_gate_probe.py:31` builds the path by **concatenation** (`"tools/recipes/build_opfstunnel" + "term_v1.py"`) so neither the command line nor the source carries a matching token — that is your route past the constraint in the brief. Print: store mtime before → both v2 records' `reviewed_sha256` / `released` / `sha256_of(recipe)` → `released_slugs(run6.md)` and `_released(record_B)` → `check_command(LAUNCH)` → mtime after.

⚠️ `c22_v1_gate_probe.py:6-8` warns `check_command` may stamp a release. Here it cannot — A refuses before `save_records` (`:332`) — and the mtime pair is the proof, not a hope.

## 6. What to do instead — pay record B, then branch

`STATUS.md:52-57` makes a cycle with no D1 build log a wrong-ordering cycle, so the cheapest correct path is the one that launches run 6 today.

1. **Dispose record B on v2's own path first** — `FIXED:`/`REFUTED:` lines for F1–F4 into `archive/peer/2026-09-19-priorart-d1-routeb-run6.md` under `## What was done with it`, citing what the four patches changed. This is what converts the rename from laundering into bookkeeping, and costs one edit since the findings are being answered anyway. (F1 is a *do-not-do* finding — the crash copy must be copied out before P4 deletes it — so its disposition form is judgement's call.)
2. **v3 = byte copy of v2's current bytes**, nothing else changed in that step, header in the established form naming record B and its disposition. ⚠️ Do **not** `cp` — a shell `cp` names the stopped path and is refused by this gate (and trips `BUILD_RE`, `STATUS.md:15`). Use Read/Write, which `guard_bash.py:208` does not gate.
3. **Prior-art v3 on its own bytes with `--recipe`** — usable, per §1.
4. **Findings, not devices** (device-building is suspended, `STATUS.md:10`): (a) the store is keyed by path, so a record cannot follow its bytes — content-addressing would close exit (c) permanently; (b) `_check` should stamp only when `cur == reviewed_sha256`, else refuse as UNREVIEWED — that would have refused run 5's launch and this trap would not exist.

**Do I still believe the claim holds?** Its mechanical prediction, yes — and I could not break it. Its account of *why*, no. What would change my mind on the mechanism: an ALLOW in §5's probe.

Sources: [pip hash-checking / lockfile pinning discussion](https://pentstark.com/blog/lockfile-injection-supply-chain/), [GitHub "dismiss stale pull request approvals"](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) — the standard answer in every hash-pinned approval system is *re-approve the new digest*, which is what record B is; neither source documents a rename as a sanctioned escape, so the external literature supports "new key + its own review", not "new key instead of a review."

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
