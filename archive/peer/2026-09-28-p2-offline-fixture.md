# p2-offline-fixture

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.2931  in 18 / out 9257 / cache-create 116663 / cache-read 872826  (105s, 16 turn(s))
- **date:** 2026-09-28 18:19:52
- **outcome:** ANSWERED (109s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about a failed self-test.

Failing log: tools/bench/p2run_selftest_guard_cycle_offline.log (lines 5-6), script tools/bench/selftest_guard_cycle_offline.py.
Failure: cases O3/O4 expect guard_cycle to REFUSE a launch of stage_d1_l2b2a because its prior-art verdict is unreleased; the launch is now ALLOWED (rc 0).

Claim (card chat-P2's material session): this is a STALE FIXTURE, pre-existing drift, not caused by chat-P2's edits. The fixture reads the LIVE archive state of 2026-09-27; the prior-art review archive/peer/2026-09-27-priorart-c111e-l2b2a.md was later released by FIXED: lines (:543-547), so the guard correctly allows the launch today. chat-P2 (commit 99e99f8) only added a slug `user-rule-contradicted` and refusal text to tools/hooks/guard_cycle.py; an earlier O3 PASS (selftest_guard_cycle_offline_p1after.log:3) passed for an unrelated reason (a retrospective-threshold block).

Attack it: is there a reading in which chat-P2's guard_cycle.py change (or its prior_art_review.py / stage_prerun.py changes: new_structure_classes, proven_pattern) makes guard_cycle allow a launch it should refuse? Name the file:line, the alternative explanation, what would falsify the stale-fixture claim, and the cheapest discriminating test (e.g. run the self-test against a fabricated unreleased review).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**I could not refute the claim.** chat-P2's edits did not cause O3/O4 to allow the launch. The self-test has depended on live state since the evening of 2026-09-27. The claim does get the releasing mechanism wrong, and it understates the damage: the test has been reporting PASS without testing what it says it tests.

**1. What the claim gets wrong: c111e is not the review that releases the launch today.**
- In the launch gate, the c111e record is released only for one version of the recipe file, sha `a78d3c14…` (`tools/bench/stop_records.json:1411-1414`, stamped 2026-09-27T14:38:09Z).
- A later record for the same recipe carries its own release, for sha `876bb078…` (`stop_records.json:1427-1438`, review `archive/peer/2026-09-28-priorart-c112d-l2b2a.md`).
- Under the gate's supersession rule, c111e is skipped once a later record exists for that path (`tools/stop_record.py:684-685`, `:733-735`). The c112d record is the one that decides.
- So if the recipe's bytes on disk were anything other than `876bb…`, the launch would be refused as "released for different bytes", however valid c111e's FIXED lines at `:543-547` are.
- guard_cycle's own verdict check only reads the newest prior-art review (`tools/hooks/guard_cycle.py:669-690`), which today is `2026-09-28-priorart-c119-qrt-pool.md` (novel). c111e never reaches that check.

**2. The other explanation, and why the evidence rules it out.**
- For chat-P2's code to be the cause, the new `new_structure_classes` call (`guard_cycle.py:543`) or the proven-pattern release (`:533-539`) would have to let the launch through.
- The logged stderr rules out both. The proven-pattern release always writes a `PROVEN-PATTERN` line to stderr (`:569-571`), and O3/O4 logged `(0, [])` (`p2run_selftest_guard_cycle_offline.log:5-6`).
- `new_structure_classes` only runs on the refusal path. It sits inside `except Exception`, and a crash would exit with rc 1, not 0.
- Adding `user-rule-contradicted` to the slug list (`:71-75`) can only block more. It releases something only when a FIXED line uses that slug, and none of the l2b2a reviews do.

**3. The earlier passes support the claim, and they expose the real defect.**
- The launch gate runs before the retrospective-threshold check (`guard_cycle.py:621` before `:633`).
- `selftest_guard_cycle_offline_p1before.log:3`, taken before chat-P1 or chat-P2 existed, was refused by the threshold check. That means the launch gate was already allowing the launch at that point.
- The only run where O3 passed for the stated reason is the original, at 2026-09-27 22:26 (`selftest_guard_cycle_offline.log:5`). The release was stamped 1 h 12 min later, at 23:38 local time.
- Since then O3/O4 have passed twice for the wrong reason. This is a self-test that never builds its own test state, not just drift. It cannot tell a working launch gate from one that allows everything.

**What would show the claim wrong:** the launch gate refusing the launch at chat-P2's parent commit 53916a1 but allowing it at 99e99f8. Or any stderr, or rc ≠ 0, from the proven-pattern or new-structure code on this command.

**Cheapest test that tells the two apart** (read-only, no LabVIEW):
1. `py tools/stop_record.py check py -u tools/recipes/stage_d1_l2b2a.py` should print `ALLOW`.
2. `git diff 53916a1 99e99f8 --stat -- tools/stop_record.py` should show nothing changed.
3. Run the recipe file's sha256. It should equal `876bb078…`.

If all three hold, chat-P2 is cleared. The fix is to make O3/O4 build their own state: copy `stop_records.json` into a scratch folder, add an unreleased record for a scratch recipe, point `stop_record.STORE` at the copy, and run the check in-process. Only then does the test show the launch gate refusing an unreleased launch.

What would change my mind: step 1 printing a refusal, or steps 2 or 3 failing.

## Sources

(extract from answer)

## What was done with it

- ACCEPTED (chat, 2026-09-28 18:1x). The reviewer's three discriminating checks were run read-only and all hold:
  (1) `py tools/stop_record.py check "py -u tools/recipes/stage_d1_l2b2a.py"` → `ALLOW`; (2) `git diff 53916a1 99e99f8
  --stat -- tools/stop_record.py` → empty; (3) sha256 of `tools/recipes/stage_d1_l2b2a.py` = `876bb078…`. chat-P2 is
  cleared; the failure is the self-test's dependence on live state (it never builds its own unreleased record).
- Correction taken: the releasing record is c112d (sha 876bb078…), not c111e's FIXED lines.
- The fixture fix follows the reviewer's recipe (scratch copy of stop_records.json + an unreleased record for a scratch
  recipe, in-process check) and is Part 1.2 of card chat-P3 (`tools/bench/cards/brief_chat-P3.md`), the runner's first act.
