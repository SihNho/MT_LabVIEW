# priorart-fstunnel-wirechecked

- **agent:** claude
- **model:** opus (effort high; peer.ps1 default for role priorart)
- **kind:** fact
- **cost:** $3.3253  in 28 / out 17578 / cache-create 217305 / cache-read 1425418  (237s, 24 turn(s))
- **date:** 2026-09-18 10:21:55
- **outcome:** ANSWERED (239s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ROUTE NOTE, SAID OPENLY: this prior-art review is dispatched directly through `tools/peer.ps1` instead of
through `tools/prior_art_review.py --recipe <path>`, because the launch gate (`tools/stop_record.py`) refuses any
command whose RAW TEXT contains the recipe's path, and `prior_art_review.py` requires that path on its command
line. The refusal message itself asks for exactly this: "Get the edited recipe reviewed." So the recipe's path is
named only inside this task file, never on a command line. This is a read-only review that every gate in this
project is documented to permit; NO launch, build or run follows from it, and no release line will be written on
the strength of it. That is judgement's call, in a later session.

=== THE QUESTION ===
Has the change made to `tools/recipes/build_opfstunnelterm_v0.py` in cycle 21 already been done, measured or
refuted in this project's own files?

Answer the standard prior-art question set (A1 settled-already / A2 refuted-already / A3 contradicted /
A4 unread-evidence / B1 already-built / B2 already-failed / B3 helper-exists / B4 already-measured), and in
particular:

 (1) Name, with file:line, ANY existing helper, op, recipe, doc or archived review in this project that already
     does WIRE VERIFICATION BY TERMINAL IDENTITY (i.e. reads a terminal's `.wire` property before and/or after a
     wire call and compares the two endpoints), under any name.
 (2) Name, with file:line, anything in this project that ALREADY RECORDS this branch / false-negative behaviour of
     `gscript.wire`'s wire-count assertion - an earlier measurement, an earlier peer exchange, a doc line, a
     retrospective, a code comment.
 (3) Say whether the SIX call sites' derived `branch=` conditions contradict anything already measured or written
     down in these files (for instance a recorded case where a source terminal owned a wire but the connection
     still had to be made non-branching, or vice versa).

=== THE CHANGE UNDER REVIEW ===
A LOCAL helper `wire_checked(...)` was added to the recipe at lines 284-320, and the recipe's six wire calls now
go through it, at lines 431, 438, 441, 444, 449, 452. `tools/gscript.py` is NOT modified.

What the helper does, per call:
  1. reads the SOURCE terminal's `.wire` BEFORE the call (`src_before`);
  2. calls `g.wire(..., branch=(src_before != 0))` - i.e. branch exactly when the source already owns a wire,
     which is the condition `gscript.wire`'s own error text names;
  3. reads `.wire` on BOTH terminals AFTER the call and raises unless they are EQUAL and NON-ZERO.
Its docstring states the intent: terminal identity is the direct reading, and it also catches what `branch=True`
alone would silently pass - a DECLINED connection (dst still 0) and a wire landing on the WRONG endpoint.

The six call sites and their tags:
  :431 `[kind] TMSC->PN_A`      Function TMSC `<T_CAST_OUT>` -> Property PN_A `reference`
  :438 `[kind] TMSC->PN_B`      Function TMSC `<T_CAST_OUT>` -> Property PN_B `reference`
  :441 `[kind] <short_a>->UID`  Property PN_A `<short_a>`    -> Property PN_A_UID `reference`
  :444 `[kind] <short_b>->UID`  Property PN_B `<short_b>`    -> Property PN_B_UID `reference`
  :449 `[kind] <short_b>->ConnWire` Property PN_B `<short_b>` -> Property PN_B_CW `reference`
  :452 `[kind] ConnWire->UID`   Property PN_B_CW `Wire`      -> Property PN_B_CWU `reference`

What it replaces: reliance on `gscript.wire`'s `+1` wire-count assertion, `tools/gscript.py:1325-1333`:
    after = count(target, "Wire"); crossings = max(0, count(target,"LoopTunnel") - tun_before)
    lo, hi = before + 1, before + 1 + crossings
    if not branch and not (lo <= after <= hi): raise RuntimeError(... "re-call with branch=True")

The measurement that motivated it, made this cycle and recorded in
`tools/bench/diag_fstunnel_wire_semantics.json`: the TMSC (`specific class reference`) output ALREADY owned a
residual SOURCE-ONLY stub wire #384; after `wire(..., branch=True)` the Wire count went 40 -> 40 (no new Wire
object) while BOTH terminals afterwards read wire #384, and PN_A's `wire_err` went 1055 -> 0. So the connection
SUCCEEDED and the count test reported it as a failure. The recipe had failed twice at its line :392 -> that
assertion (`tools/bench/` build logs of 2026-09-18 08:59 and 09:0x, both rc=1).

=== ALREADY RULED OUT (do not spend the review re-deriving these; attack them if they are wrong) ===
 * `tools/gscript.py` is DELIBERATELY untouched: ~140 call sites depend on its current contract and the `+1`
   assertion is a real net elsewhere. Hence a helper LOCAL to the recipe.
 * The residual source-only stub wire is DELIBERATELY not deleted: branching onto it is the intended topology.
 * Passing `branch=True` unconditionally was rejected because it asserts nothing - `gscript.wire` performs no
   post-check at all in the branch case.

=== OUTPUT CONTRACT ===
Cite a FILE and LINE for every finding; a finding with no citation cannot be acted on. End with machine-readable
lines, one per finding, from this list only:
  PRIOR-ART: settled-already | refuted-already | contradicted | unread-evidence
  PRIOR-ART: already-built | already-failed | helper-exists | already-measured
  PRIOR-ART: novel
`novel` only if none apply. Do not invent slugs. Read `archive/` - that is your job in this role.


## Answer

**Verdict: NOT novel.** Verification by terminal identity is this project's *documented standing rule*, already implemented six times under the name `connect()`, and the false-negative branch of the count assertion is written in a comment **inside that very assertion**.

---

## (1) The helper already exists — six recipes, same function

| file:line | what it is |
|---|---|
| `tools/recipes/build_opstopfromnode_v0.py:180-193` | `connect(src_uid, src_name, dst_uid, dst_name, branch=False, tag="")` — *"Wire by name, verified by the SAME wire uid on BOTH ends - never by a count, never by ExecState (docs/toolkit-capabilities.md row 37)."* Body = `wire_checked` steps 2–3 exactly: call `g.wire`, re-walk, read the source-side and sink-side `.wire`, `ok = bool(a) and a == b`, raise on mismatch. |
| `tools/recipes/build_opconnectnested_v1.py:196-209` | same function; docstring says *"build_opconnectnested_v0.connect verbatim"* |
| `tools/recipes/build_opconnectnested_v0.py:158` | the original |
| `tools/recipes/build_opwiresr_v0.py:155-166` | same, *"row 37: never by count, never by ExecState"* |
| `tools/recipes/build_opmovebyindex.py:81-87` | same, reported through `check()` |
| `tools/recipes/build_opcreateconstonterm_v0.py:160` | same signature |
| `tools/recipes/build_opaddshiftreg_v0.py:201-212` | the first one — the A1b gate *is* wire-uid equality |
| `tools/recipes/build_track_v6_core.py:111-139` | `wire_sub(...)` — the **strictly more general** version: same diagram ⇒ uid equality; across a border ⇒ one new `LoopTunnel`, `out_wire == source`, `in_wires == [sink]`, `IndexMode 0`, clean error fields |

And the recipe under review **already used the pattern itself** before the change — `tools/recipes/build_opfstunnelterm_v0.py:462-467`, gate `B4b`.

## (2) The behaviour is already on record — code, docs, and an archived review

- `tools/gscript.py:1327-1329`, the comment inside the assertion the recipe died on: *"A BRANCH from an already-wired source does NOT add a Wire object (the wire owns all its sinks), so this check misreads a successful branch as a decline. For branches pass branch=True and verify by effect."*
- `docs/NAMES.md:785-788` — logged 2026-09-14 as one of *"two COM/recipe traps … both of which cost a batch"*, with the remedy stated: *"Verify a branch by reading the **wire UID on both terminal ends** (`node_terms`): a real branch shares the existing Wire object, so the two UIDs are equal."*
- `archive/peer/2026-09-14-addshiftreg-fail1-branch-or-decline.md:66-83` (codex refuting "unchanged count = branch succeeded") and `:129-154` — *"equality of the two terminal-reported wire UIDs is the discriminator that raw wire count lacks"*; `:176-195` records it measured and adopted.
- `docs/toolkit-capabilities.md:138`; earlier firings of the same false negative in `archive/bench-2026-09-14-stage2-toolkit/build_opexitwhile.log:23` and `archive/bench-2026-09-14-rotor-sign/build_setcommand_signed.log:151,165`.

The cycle-21 measurement (`tools/bench/diag_fstunnel_wire_semantics.json`) re-derived on hardware what is printed two lines above the raise.

## (3) Two limits already measured that the change does not carry

**(3a) uid equality does not prove the wire is GOOD.** `docs/NAMES.md:861-867` (measured 2026-09-15, `tools/bench/build_opwiresource_v0.log`): *"LabVIEW joins type-incompatible terminals and draws a broken wire, whose uid still reads identically at both ends. Gate `exec_state == 1` after any wire whose types are not obviously compatible."* The measured case is a **property-node `reference` downcast** — the shape of call sites `:441`, `:444`, `:452`. Corroborated by `archive/2026-09-16-status-cycles-8-10-narrative.md:146` and `.claude/skills/labview-automation/references/gui-recipes.md:283-290` (the 3/3 "branch breaks the diagram" cases were **all TYPE mismatches**). The recipe's `B4`/`B5` ExecState gates (`:76-77`, `:464-467`) are the net that catches this — but the docstring at `:290-291` enumerates only *declined* and *wrong endpoint* and records no false positive.

**(3b) the unconditional equal-and-non-zero test is documented-wrong across a border — scope only.** `docs/NAMES.md:822-823`: *"A border-crossing wire is TWO Wire objects through a tunnel (uids differ at the two ends — never gate a cross-border wire on uid equality…)"*; `archive/2026-09-17-status-d1-route-a-run9.md:15`; concrete cost at `tools/recipes/build_track_v6_core.py:112-116` (*"'New Image' -> 'Image' read 531/506 and my equal-uid gate stopped the build"*). `gscript.wire`'s count test tolerates crossings (`tools/gscript.py:1322-1324`); `wire_checked` does not, so it is **strictly narrower** than what it replaces. **It does not hit the six call sites** — all read through `sweep(op)`, diagram 0 only (`build_opfstunnelterm_v0.py:358-359`), every node created on diagram 0 (`:406, :436, :439, :442, :447, :450`).

## The one ingredient with no prior instance: `branch=(src_before != 0)`

Every existing helper takes `branch` as a caller argument (`build_opstopfromnode_v0.py:180`, `build_opconnectnested_v1.py:196`, `build_opwiresr_v0.py:155`, `build_opmovebyindex.py:81`, `build_opcreateconstonterm_v0.py:160`, `build_track_v6_core.py:111`). **Nothing contradicts the derivation:** `branch` never reaches LabVIEW — `gscript.wire` sets no control from it (`tools/gscript.py:1310-1318`); it only guards the count assertion at `:1325`. So deriving it changes which assertion runs, nothing about the edit. No file records a case where a wired source had to be connected non-branching, or the converse, because the flag has no such meaning in this codebase. The one recorded asymmetry runs the other way — `tools/gscript.py:1296-1306`, LabVIEW may MERGE a crossing segment (+1 where +2 was expected), which is why the bound is a range — and it argues *for* the identity test.

---

PRIOR-ART: helper-exists
PRIOR-ART: already-built
PRIOR-ART: settled-already
PRIOR-ART: already-measured
PRIOR-ART: unread-evidence
PRIOR-ART: contradicted

*(Note: the `Write` tool is disabled in this session, so this review exists only as this answer — nothing was written to disk, no lock taken, nothing built or run.)*

## Sources

(extract from answer)

## What was done with it

All six findings were acted on in `tools/recipes/build_opfstunnelterm_v1.py` (the `_v0` bytes this review read are
superseded and unlaunchable — `_v0`'s stop record is released for a different sha, see that file's header):

FIXED: contradicted - tools/recipes/build_opfstunnelterm_v1.py:308 - the helper now records that equal wire uids do not prove a GOOD wire (docs/NAMES.md:861-867) nor hold across a structure border (docs/NAMES.md:822-823), and adds a per-site ExecState-worsening check so a broken downcast is attributed to its own wire site; the recipe's B4/B5 ExecState gates remain the net.
FIXED: unread-evidence - tools/recipes/build_opfstunnelterm_v1.py:297 - the helper cites tools/gscript.py:1327-1329 and docs/NAMES.md:785-788 as its authority and does what they prescribe, passing branch=True and verifying by effect.
FIXED: settled-already - tools/recipes/build_opfstunnelterm_v1.py:297 - branch is derived from the 2026-09-14 measurement cited in that docstring instead of being re-derived in this recipe.
FIXED: already-measured - tools/recipes/build_opfstunnelterm_v1.py:297 - the same docstring cites archive/peer/2026-09-14-addshiftreg-fail1-branch-or-decline.md as the measurement, so nothing here is re-measured.
REFUTED: helper-exists - tools/recipes/build_opstopfromnode_v0.py:180 says connect() is a module-level def inside a recipe whose module body builds its own op VI, which does not cover reuse from another recipe because importing it would execute that build; a local per-recipe helper is the pattern being followed, and it is attributed in the docstring.
REFUTED: already-built - tools/recipes/build_opstopfromnode_v0.py:189 verifies both-ends-equal-and-non-zero only, which does not cover this case because no existing instance derives branch from the source terminal's own wire or attributes a break to its wire site; the delta is named in the docstring.
