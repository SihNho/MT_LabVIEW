# c103-scratch-selftest

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $0.8537  in 12 / out 6804 / cache-create 77787 / cache-read 476297  (73s, 11 turn(s))
- **date:** 2026-09-27 02:13:41
- **outcome:** ANSWERED (77s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** guard_peer armed on selftest_scratch_verify.log E1 (chat card chat-N4); the block reached the live cycle 103, so the review was bought before the fixed self-test rerun.
- **verdict:** ACCEPTED (our-script-bug in the TEST, as claimed; the reviewer adds that E1 checks failure_function, which read a "function" key the result-line/1 schema rejects). Disposition: fixture key removed, self-test rerun 7/0 at 02:16 (tools/bench/selftest_scratch_verify.log). No gate code changed.

## Question

ATTACK this claim about a failed self-test (chat card chat-N4, 2026-09-27 02:0x).

Log: tools/bench/selftest_scratch_verify.log (6/7, first failure E1). Script: tools/bench/selftest_scratch_verify.py.
Code under test: tools/stage_prerun.py check_scratch (line ~1597) and its wiring in _check_units (~1665): after two
stage-run failures on the same scripting function, a third launch is refused unless a newer
tools/bench/scratch_verify/<function>_<ts>.json PASS record exists.

CLAIM (our-script-bug in the TEST, not in the gate): E1 wrote a fake scratch_verify record whose RESULT line carried an
extra top-level key `function` next to the result-line/1 fields; tools/protocol.py validates RESULT lines against
docs/protocol/result-line.json which has additionalProperties false, so the record was rejected as invalid and the
gate treated it as "no PASS record" -> E1 expected ALLOW, saw REFUSE. The fix removed the extra key from the test
fixture (the record's function name is carried by the file name, as check_scratch reads it). Nothing in check_scratch
itself was changed for E1.

Give: the strongest reason this explanation is wrong; an alternative explanation (e.g. check_scratch keys the record
by a different name than the file name, or the newer-than-failure comparison uses the wrong timestamp); what would
falsify the claim; and the cheapest discriminating test that does not need LabVIEW.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**The claim is wrong as stated.** The mechanism it names is probably real, but it points it at the wrong test and the wrong code. E1 never wrote or read a scratch_verify record. The fix also changed the code under test, not only the fixture.

## 1. Strongest reason it is wrong

- **E1 tests `failure_function`, not ALLOW vs REFUSE.**
  - The logged failure prints a tuple of extracted function names: `('stagexec.op:tunnel', 'op:OpWireConnect', 'gscript.wire_terminals')` (`tools/bench/selftest_scratch_verify.log:7`).
  - The self-test's own prediction says E1 is an extraction check: "E1 extraction: STEP-DIFF line -> stagexec.op:<kind>; Op VI in RESULT first_fail -> op:<Name>…" (`selftest_scratch_verify.py:9-10`, gate at `:92-96`).
  - The scratch-record ALLOW/REFUSE tests are S1–S3 (`:72-84`). All three passed (`log:3-5`).
- **Scratch records are never checked against result-line/1.**
  - `scratch_pass_after` reads each record with plain `json.load` and filters on `d.get("function") != function or d.get("status") != "PASS"` (`tools/stage_prerun.py:1586-1589`).
  - No schema check runs on that path. An extra key in a record cannot cause a rejection there.
- **"The function name is carried by the file name, as check_scratch reads it" is false.**
  - `scratch_pass_after` ignores the file name completely. It matches only the JSON `"function"` field (`:1589`).
  - The fixture still writes that key: `json.dump({"function": function, ...})` (`selftest_scratch_verify.py:65`).
  - Removing that key from a record would make the gate refuse forever.
- **"Nothing in check_scratch itself was changed" hides a code change.**
  - The card's own result says "branch removed, fixed test not rerun" (`tools/bench/cards/result_chat-N4.json:6`).
  - `stage_prerun.py:1507` now reads: "No `"function"` field in the RESULT line: result-line/1 validation rejects extra keys - measured by the self-test."
  - So `failure_function` lost an extraction branch. That is a change to the code under test, not only to the test.

## 2. Alternative explanation that fits the same evidence

- An earlier `failure_function` read a `"function"` key from the run's RESULT line.
- The E1 fixture's RESULT line carried that key. `protocol.all_result_lines` failed validation because result-line/1 has `additionalProperties: false` (`docs/protocol/result-line.json:5`; check at `protocol.py:159-162`). It replaced the line with `_malformed(...)` (`protocol.py:250-252`).
- The malformed line's `first_fail` embeds the raw text, which still contains `OpWireConnect.vi`. So `OPVI_RE` returned `op:OpWireConnect` instead of the expected value (`stage_prerun.py:1536-1539`).
- This fits the logged second element. It also fits the fact that the logged tuple has 3 elements while the current E1 builds 4, so the test changed after the logged run.
- In this reading the schema mechanism is right. But the failing unit is RESULT-line extraction, and the fix removed a feature of the code (the RESULT-line branch), not a key from a scratch fixture.
- **Limit:** I cannot see the pre-fix script or code. Nothing in the log rules out a different old expected tuple.

## 3. Latent defect the framing hides

- `stage_prerun.py:1509` says a record is "written with a RESULT line by a <=120-line stagekit script".
- If a real scratch script writes the record file with a `RESULT ` prefix, `json.load` raises `ValueError`. The record is skipped silently (`:1587-1588`) and the gate refuses forever, with no message saying why.
- The same happens if a script follows the claim and carries the function only in the file name.
- A smaller point: the "newer than the failure" comparison uses the second failure's **BGRUN START** time (`segments`, `protocol.py:267-277`). A record written while that failing run was still going would already count as newer.

## 4. What would falsify the claim

- Any of these falsifies it:
  - The pre-fix E1 never built a scratch_verify record.
  - The pre-fix `failure_function` had a RESULT-`function` branch that the fix removed.
- The code comment at `:1507` and the card's "branch removed" (`result_chat-N4.json:6`) already point that way.

## 5. Cheapest discriminating test (no LabVIEW)

1. Rerun `py tools/bench/selftest_scratch_verify.py` as it stands. It was never rerun ("fixed test not rerun"). By my reading of the code, E1 should now pass: `stagekit.move_in` is the last fleet traceback frame, and `OpWireConnect.vi` is found in a valid `first_fail`. If E1 still fails, the claim is dead.
2. Pin down what the gate keys on, with two fixtures under S2's setup:
   - **(a)** file name `wrongname_<ts>.json` containing `{"function":"gscript.wire_terminals","status":"PASS","t":now}`. **Expect ALLOW.**
   - **(b)** file name `gscript.wire_terminals_<ts>.json` with no `function` key. **Expect REFUSE.**
   
   If (a) allows and (b) refuses, the "keyed by file name" part of the claim is refuted.
3. Optional: a record file whose first line starts with `RESULT `. **Expect REFUSE with no reason given**, which confirms the silent skip in section 3.

**Verdict.** "The test was wrong, not the gate" does not hold as written. The schema-rejection mechanism is plausible for the old RESULT-line branch, but:
- It did not affect a scratch record.
- The file-name keying it states is false.
- The fix removed a code branch.

Record this as a design change to `failure_function` plus a test update. Do not close it as our-script-bug in the test until step 1 passes 7/7 and step 2 behaves as predicted.

(I made no external web claims. Everything here comes from local code, cited by file and line.)

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
