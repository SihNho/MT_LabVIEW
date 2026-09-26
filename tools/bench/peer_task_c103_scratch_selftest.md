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
