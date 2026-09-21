ATTACK this claim. I want it REFUTED, not confirmed. If it survives, say exactly which part survives and why.

## THE CLAIM I FORMED (attack it)

`tools/bench/c62f_astcheck.log` ends `=== ASTCHECK FAILED; failing: 7 move_in is neither imported nor called`
(`FAIL  7 move_in is neither imported nor called  called=True imported=True`), 11 of 12 checks passing.

My explanation: **check 7 in `tools/bench/c60c_astcheck.py` encodes a constraint from CYCLE 60's brief, which
forbade `move_in`; the current cycle-62 brief and `docs/cycle27-plan.md` Pre-decided 53(d⁗) explicitly ORDER
`move_in` as the one new step in the row sequence, so this FAIL is a STALE GATE, not a defect in
`tools/bench/diag_c62_s3b_movein.py`, and launching that diagnostic despite it is applying the plan rather
than evading a gate.**

## THE EVIDENCE (read these yourself; do not take my word)

- `tools/bench/c60c_astcheck.py` — the gate. Its docstring line 14 and its `gate("7 move_in is neither
  imported nor called", ...)` around line 99. Note the file's own header says it is a static gate on
  `tools/bench/diag_s3b_l0_localname_v2.py`, a cycle-60 diagnostic; the target is `sys.argv[1]`.
- `tools/bench/c62f_astcheck.log` — the failing run (12 check lines).
- `docs/cycle27-plan.md` Pre-decided 53(d⁗) (search for `d⁗` or `move_in`) — the cycle-62 judgement decision:
  *"the row sequence gains one step — `move_in` the new Local onto `Diagram #639` BEFORE connecting"*, taken
  after `tools/bench/diag_c62_s3b_build.log` measured the Local landing on `TopLevelDiagram #536` and the
  connect building a cross-diagram TUNNELLED path (wire_delta 3, two different wire uids at the two ends).
- `tools/bench/diag_c62_s3b_movein.py` — the diagnostic about to run. It imports `move_in` from
  `tools/recipes/build_d1_v0.py:318` and calls it once, at its step 3.
- `CLAUDE.md` — the project's rules, including "GUI only where scripting is VERIFIED unreachable", the
  gate/threshold discipline, and the standing rule that `CYCLE_GUARD_OFF`/gate evasion is never the answer.

## SPECIFIC LINES OF ATTACK I WANT YOU TO TRY

1. **Is this actually gate laundering?** A session that hits a red gate and declares it "stale" is the exact
   pattern this project's rules exist to stop. Give me the strongest version of the argument that I am
   rationalising, and name what evidence would distinguish "stale gate" from "evaded gate".
2. **Is check 7 really cycle-60-specific?** Search the repo for why it was added. If there is a SAFETY reason
   for it that outlives cycle 60 — e.g. `move_in` is known to corrupt something, leaves residue, or was
   banned for a measured reason rather than a brief-scoped one — that kills my claim outright. In particular
   look at `tools/bench/diag_s58_boolwire.py` (which calls `move_in` and documents a junk-`Invoke` residue as
   PREDICTED RISK (i)) and anything in `docs/` or `archive/peer/` about `move_in`.
3. **Is the right move to run a DIFFERENT gate instead?** Argue for/against: (a) run the diagnostic with the
   failing check reported as-is, (b) write a cycle-62 gate file that keeps checks 1-6/8/9 and inverts 7,
   (c) do not run at all. Note that the cycle-62 brief forbids new tools/recipes and forbids editing
   `tools/gscript.py`; say whether a new *astcheck* file falls inside or outside that prohibition.
4. **What else did the 11 PASSing checks fail to cover** that matters for a script that calls `move_in` on a
   `Local` (not a `ControlTerminal`, which is the only class `move_in` has been measured on here)?

## ALREADY RULED OUT (do not spend the answer on these)

- A typo/parse error in the diagnostic: check 1 passes, 1,063 lines, 42 gate sites.
- A missing gscript verb or a bad import: checks 4, 4b and 5 all pass, `move_in` resolves in `build_d1_v0`.
- `gui_save` / `remove_bad_wires*` / `allow_broken=True`: checks 2 and 3 pass, all absent.
- Setting `PEER_GUARD_OFF` or `CYCLE_GUARD_OFF`: never an option in this project.

## OUTPUT

Start with one of: `The claim is REFUTED` / `The claim SURVIVES` / `The claim SURVIVES IN PART`. Then: the
strongest reason it is wrong; an alternative explanation for the FAIL; what would falsify my claim; and the
CHEAPEST discriminating test. No confirmation, no summary of what I already said.
