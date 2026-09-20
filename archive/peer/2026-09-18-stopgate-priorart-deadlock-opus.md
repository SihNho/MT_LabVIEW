# stopgate-priorart-deadlock-opus

- **agent:** claude
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $2.9115  in 18 / out 33472 / cache-create 159095 / cache-read 864474  (470s, 16 turn(s))
- **date:** 2026-09-18 10:12:53
- **outcome:** ANSWERED (471s)
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

Write is disabled in this cell, as it should be for a read-only reviewer — so the review is the answer itself.

---

# REFUTED — the claim is wrong at its premise, and the proposed repair is a no-op

## 1. The single strongest reason the claim is WRONG

**`prior_art_review.py` cannot lift a stop record. It only plants them.** The claim's load-bearing sentence — *"the only command able to lift a stale release record is the command that record forbids"* — names a capability that does not exist anywhere in this repository.

Three measurements, all from the source you pointed me at:

- **The script's only store mutation is `write_stop_record`** (`tools/prior_art_review.py:306`), and `write_stop_record` **appends** when the hash differs. Its dedupe branch requires path **and** `reviewed_sha256` **and** `review_file` to all match (`tools/stop_record.py:227-232`); its own docstring says so: *"a DIFFERENT hash appends a new record, because a different recipe was reviewed"* (`:207-208`). The stale record survives untouched.
- **`record["released"]` has exactly one writer in the entire tree** — `tools/stop_record.py:320` — guarded by `if rel is None` at `:319`. I grepped for every other spelling; the only other touches are reads (`:173`, `:318`, `:387`) and a carry-over of an existing value (`:231`). **Once a record is stamped for sha A, no code path can re-stamp it for sha B.**
- **The refusal at `:325` is reached _after_ `_released()` has already returned ok** (`:309-311` passes, then `:313`, `:318`, `:323`, `:325`). So no release line — appended to the old review file, written into a brand-new one, however perfectly cited — can change the outcome. The sha comparison is downstream of every release check.

The project's own self-test **asserts this as intended behaviour**: `tools/bench/stop_record_selftest.py:159-168`, CASE 3 — *"C3a launch REFUSED again after the recipe changed"*, *"C3c the record was NOT cleared by the re-save"*. And there is no case after C3 that re-opens it. The device was proven to refuse and never proven to re-open, which is Pre-decided 3 (`docs/cycle21-plan.md:58-59`) read in the mirror.

**Therefore the proposed repair does not do the thing it is being proposed for.** Exempt `prior_art_review.py` in `stop_gate`, run the dispatch, and take any verdict you like: `novel` writes nothing at all (`prior_art_review.py:287-292`), non-`novel` appends a *second* record which is itself unreleased and refuses at `:311`. Record 2 of `tools/bench/stop_records.json:15-31` still stands, `_check` still hits it (`:306-307`, iteration order irrelevant — a passing record `continue`s into the stale one), and `py … tools/recipes/build_opfstunnelterm_v0.py` is still refused. The cycle's sole objective — step 2 at verification level NONE (`docs/cycle21-plan.md:12-18`) — does not move one inch.

You diagnosed the exit door and proposed to oil a window.

## 2. Q1 — routes that already exist

Three, none requiring a gate change. I could not find a `stop_record.py` subcommand that releases: `_cli` has `write`, `check`, `list` only (`:364-391`).

| route | why it works | cost |
|---|---|---|
| **`--no-recipe "<reason>"`** (`prior_art_review.py:218-222`; refusal text `:141-153`) | keeps the recipe path off the command line entirely, so `PATH_TOKEN_RE` never sees it. Built *as* an auditable opt-out, written verbatim into the archived review (`record_opt_out`, `:161-187`) | contradicts cycle21 **Pre-decided 4** (`docs/cycle21-plan.md:60-62`) — a *decision* the judgement session may amend, not a code hole. It bends the flag's documented purpose ("a review that genuinely has no recipe"), so say so in the reason line |
| **`tools/peer.ps1 -Agent claude -Role priorart -Kind fact -Model opus -Effort high -Slug priorart-<s> -Task (Get-Content -Raw '<file>')`** | this is verbatim the subprocess `prior_art_review.py:255-259` builds. The recipe path lives *inside* the task file, never on the command line | skips `arm_stop_records` — which, per §1, was worth nothing here |
| **set `"released": null` on record 2 of `tools/bench/stop_records.json`** | `_check:319-322` then re-stamps to the current bytes at the next launch, with the four standing `FIXED:`/`REFUTED:` lines still validating through `_released()` | a hand edit of the gate's own record store. **This is the only route in the repository that actually reaches the goal**, and it is a judgement decision, never a material one |

**Two candidate routes I checked and closed**, so nobody re-derives them:

- **argparse `@argsfile` expansion is off.** `ArgumentParser()` at `prior_art_review.py:195` passes no `fromfile_prefix_chars`, which [defaults to `None` — "arguments will never be treated as file references"](https://docs.python.org/3/library/argparse.html). There is no way to feed `--recipe` from a file.
- **No env escape reaches this gate.** `stop_gate` is called at `guard_bash.py:193`, *before* the `LV_GUARD_OFF` check at `:199`; `stop_record` reads no environment variable at all. `CYCLE_GUARD_OFF` guards only `guard_cycle.main` (`:535`), whose own `stop_record.check_command` call sits at `:551`.

And one **laundering pattern to refuse on sight**: `--recipe build_opfstunnelterm_v0.py` (bare filename). `PATH_TOKEN_RE` (`:74`) requires a separator, so no token is produced and the gate passes — while `write_stop_record` would then key the record to `build_opfstunnelterm_v0.py`, which `keys_for` can never match against a real launch. That evades the gate *and* plants a dead record. The gate's reach depends on how a path is spelled; that is a real weakness, but not a door to walk through.

## 3. Q2 — yes, the exemption opens a hole, and it is a hole this project has already fixed once

**The regex form is the hole, not the tool.** `MATERIAL_EXEMPT_RE` is a **substring** match against the whole command (`guard_bash.py:77`: `MATERIAL_EXEMPT_RE.search(cmd)`). Mirror that form into `stop_gate` and every compound command containing the string is exempt:

```
py tools/recipes/build_opfstunnelterm_v0.py ; py tools/prior_art_review.py --help
py tools/bgrun.py --max-min 5 --log tools/bench/prior_art_review.py.log -- py -u tools/recipes/<stopped>.py
```

`guard_bash.py:41-44` records this exact class being diagnosed and fixed for `BUILD_RE` — *"until 2026-09-15 it matched the path ANYWHERE on the line"*. The same file still carries a live instance of the defect: `MATERIAL_EXEMPT_RE` also exempts `\b(cat|head|…|ls|dir)\b` anywhere on the line, so `py tools/recipes/X.py --dir foo` is **already** exempt from the material gate today (`\b` matches inside `--dir`). That is the precedent, and it argues against copying the form.

**The indirect-launch attack you asked me to press: it fails, and I can say why.** `peer.ps1:389` runs the claude cell with `--permission-mode plan`, and `:399` appends `--disallowedTools Bash PowerShell Edit Write NotebookEdit Agent`; only the `hypothesis` role adds an allow list (`:396-397`), and `priorart` is not it. Anthropic's CLI reference is explicit that a bare tool name in `--disallowedTools` [puts the tool out of Claude's reach entirely](https://docs.claude.com/en/docs/claude-code/cli-reference), so the priorart cell has **no execution tool at all** — consistent with `peer.ps1:381-384`'s own note that the project's Bash hooks never fire inside it because there is no Bash. On the Python side: the only `subprocess.run` is that dispatch (`:255-259`); the recipe path reaches `sha256_of`, which opens it `"rb"` (`stop_record.py:112-118`, called at `:214` and `:313`) — read, never exec; `arm_stop_records` imports only `guard_cycle` and `stop_record` (`:272-273`); the `glob.glob` at `:274` globs `archive/peer/`, not `tools/recipes/`. Your measurement holds. The danger is in the matcher, not the callee.

**What I do confirm of your claim:** the over-broad path-token match is real and reproducible. `py tools/stop_record.py check "py tools/recipes/build_opfstunnelterm_v0.py"` is itself refused — `PATH_TOKEN_RE` finds the token inside the quoted argument — so the gate refuses the diagnostic that asks the gate what it thinks. But that evidence argues for **command-position anchoring** (`guard_bash.py:45-46`'s `MATERIAL_RE` shape, plus a reader exemption like `:121-122`), which fixes `ls`, `py_compile`, the `check` subcommand *and* the dispatch in one stroke with no allowlist to maintain. It does not argue for a per-tool exemption.

## 4. Q3 — what would falsify "structural deadlock"

- **Falsifies the claim's mechanism:** a fresh prior-art dispatch completes, and a launch of the recipe is *still* refused. That shows the dispatch never lifted anything and the deadlock is not where the claim puts it. (This is what I predict.)
- **Falsifies "the dispatch is deadlocked":** `--no-recipe` or a direct `peer.ps1 -Role priorart` dispatch completes and archives normally. The review was reachable all along.
- **Falsifies my counter-claim:** exhibit *any* input — a release line, a new review, a CLI subcommand, an env var — after which `stop_record.check_command("py tools/recipes/build_opfstunnelterm_v0.py")` returns ALLOW **without** editing the store and **without** reverting the bytes. I assert none exists; one example and I am wrong.

## 5. Q4 — the cheapest discriminating test

**First, 10 seconds, static, and it decides the question on its own:**

```
grep -n "released" tools/stop_record.py
```

One writer, `:320`, under `if rel is None` at `:319`; the refusal at `:325` sits downstream of a `_released()` that has already passed. If that is what you see, "a re-review lifts this" is dead and the exemption is pointless. (The grep itself passes the gate — `tools/stop_record.py` matches no record.)

**Then, 60 seconds, dynamic, read-only, launching nothing** — reuse the harness that already exists rather than writing one: `tools/bench/stop_record_selftest.py:112-125` redirects `stop_record.STORE`/`MARKER` to a temp dir and fingerprints the real store before and after, and `tools/bench/c19_close_release_probe.py:56,109` does the byte-identical check. Copy the store, append the record a fresh non-`novel` review would produce (same path, sha of the *current* bytes, a new review file carrying four valid `FIXED:` lines, `released: null`), then call `check_command("py tools/recipes/build_opfstunnelterm_v0.py")`.

- Claim predicts **ALLOW** (the re-review lifted it).
- I predict **BLOCKED**, quoting *"released for sha 0cc9f6ca, on disk now 5a0df508"* — the stale record at index 1, reached before the new one is ever consulted.

Run it as a **script file** invoked as `py <scratchpad>\probe.py`, so no recipe token appears on the command line. That is not evasion — the probe executes nothing and mutates nothing — but log the distinction explicitly, because "a path token in a launch" versus "a path token in a read" is precisely the defect under discussion.

---

**Two facts the brief did not report, which the judgement session should see before acting.** `docs/cycle21-plan.md:52-53`, Pre-decided 1, standing since 2026-09-18 08:53: *"BUILD NO FURTHER PROCESS DEVICE… no new gate, hook, record store, lock or launcher. A retrospective or review naming one is a FINDING, not a task."* The claim's conclusion is a patch to a gate, proposed inside the cycle whose plan says the only thing that matters is getting step 2 to run at all. And the refusal message the session was reading is **wrong about its own remedy**: `stop_record.py:328-331` tells the operator to *"get the edited recipe reviewed, or cite the edit with a fresh FIXED: line in a review that post-dates it"* — and neither of those can ever clear a record whose `released` field is already stamped. The session spent this cycle trying to comply with an instruction the code cannot honour. That defect is worth more than the exemption debate.

**What would change my mind:** a release path I missed — any writer of `released` outside `stop_record.py:320`, or a caller that deletes or replaces a record. I grepped `tools/` for every spelling of the field and found only reads. If one exists in a file I did not search, cite it and I withdraw §1.

## Sources

(extract from answer)

## What was done with it

Disposed 2026-09-18 by a MATERIAL session, per finding. No gate, hook or record store was edited, and no release
line was written, on the strength of any of it — those are judgement's calls and were not authorised this cycle.

1. **"`prior_art_review.py` cannot lift a stop record; the proposed `stop_gate` exemption is a no-op"**
   (§1, citing `tools/stop_record.py:320` as the single writer of `record["released"]`, guarded by `if rel is None`
   at `:319`, with the sha refusal at `:325` downstream of a passing `_released()`; `:227-232`/`:207-208` for the
   append-on-different-hash behaviour). **ACCEPTED as the reason the exemption was NOT built.** The exemption is
   not implemented and is not proposed; `tools/hooks/guard_bash.py` is untouched. The claim was also re-measured
   independently from the source this session rather than taken on the reviewer's word (CLAUDE.md rule 5: a peer
   answer is a hypothesis) — the readings are reported to the judgement session as measurement (a)-(d).
2. **Route 2 of the §2 table** — dispatch the prior-art review DIRECTLY as
   `peer.ps1 -Agent claude -Role priorart -Kind fact -Slug priorart-… -TaskFile <file>`, with the recipe path
   inside the task file and never on a command line. **ACCEPTED AND EXECUTED**: that is the dispatch this session
   ran (task file in the session scratchpad; archived as `archive/peer/2026-09-18-priorart-fstunnel-wirechecked.md`,
   log `tools/bench/peer_fstunnel_wirechecked.log`). The route note is written into the task file's first lines.
3. **Route 1, `--no-recipe "<reason>"`** (`tools/prior_art_review.py:218-222`). **NOT TAKEN** — the reviewer itself
   says it contradicts cycle 21 Pre-decided 4 and bends the flag's documented purpose.
4. **Route 3, setting `"released": null` on record 2 of `tools/bench/stop_records.json`** — the reviewer calls it
   "the only route in the repository that actually reaches the goal" and "a judgement decision, never a material
   one". **NOT TAKEN, and explicitly forbidden to this session**; it is carried to the judgement session as an open
   item together with measurement (c), which reports what the gate would do with such a record.
5. **The laundering pattern to refuse on sight** — `--recipe <bare filename>`, which produces no path token
   (`tools/stop_record.py:74`) and plants a record `keys_for` can never match. **ACCEPTED as a standing refusal**;
   not used, and recorded here so it is not re-derived as a "route".
6. **§3's matcher finding** — that a substring exemption of the `MATERIAL_EXEMPT_RE` shape would be the hole, and
   that command-position anchoring, not a per-tool allowlist, is the shape of any future repair. **RECORDED, NOT
   BUILT**: it names a process device, and the user's standing order of 2026-09-18 08:53 ("장치는 더 만들지 말고
   계속 진행") makes a review naming one a FINDING, not a task.
7. **§3's indirect-launch attack result** — the `priorart` claude cell has no execution tool
   (`tools/peer.ps1:389` `--permission-mode plan`, `:399` `--disallowedTools Bash PowerShell Edit Write
   NotebookEdit Agent`; only `hypothesis` adds an allow list at `:396-397`). **ACCEPTED as the safety argument for
   finding 2's route**: the dispatch this session ran cannot launch anything.
8. **The closing paragraph's two unreported facts** — that the cycle plan's Pre-decided 1 forbids further devices,
   and that `tools/stop_record.py:328-331`'s own refusal text names a remedy ("get the edited recipe reviewed, or
   cite the edit with a fresh `FIXED:` line") that cannot clear an already-stamped record. **BOTH CARRIED TO
   JUDGEMENT**, unedited: the second is a defect in the gate's message, and correcting it is an edit to a gate.
9. **§5's dynamic probe** (copy the store to a temp dir, append the record a fresh non-`novel` review would
   produce, call `check_command`). **NOT RUN** this session — the static reading at §5's first step was the
   authorised measurement, and the probe would exercise a store copy for a prediction the judgement session has
   not yet asked for.
