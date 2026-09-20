ATTACK this claim. Do not confirm it. Give the strongest reason it is WRONG, an alternative
explanation, what would falsify it, and the cheapest discriminating test.

CONTEXT (project root: "G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop";
you may read files there read-only). NO hardware is involved: this is a pure string parser.

WHAT WAS CHANGED, and why (STATUS.md OPEN 55):
`tmx_from()` in `tools/bench/drive_original_copy_v4.py` reports the PI controller's TMX (upper travel
limit) after an unattended LabVIEW run, and `tools/bench/drive_original_copy_v5.py:659` gate 93
PASSES when it equals 39.0. The old code, when the sender's `before:` line carried no `TMX?=` token,
fell through to the sender's `LIMITS` line - which in `limits-set` mode `tools/motor_send_pi.ps1`
prints AFTER the `SPA 1 0x15 <hi>` write (:58/:78). So the gate could read back the value it had
just written and PASS without ever seeing what the controller held after the run. Measured on the
UNPATCHED code, `tools/bench/tmx_fallthrough_before.log:4` (got 39.0 off the LIMITS line) and :10
(got 12.0, the wrong number).

The patch: (1) `tools/motor_send_pi.ps1:52` now also emits `PRELIMITS TMN=<n> TMX=<n>`, normalised by
that script's own `Num` parser, BEFORE the SPA write; (2) `tmx_from` reads it with an anchored regex;
(3) `tmx_from` returns `(None, <that before: line>)` when a `before:` line exists but has no `TMX?=`
token, instead of falling through to LIMITS; (4) `tools/motor_gate.py:281` `parse_pi_limits` was
anchored to `(?m)^LIMITS` because `PRELIMITS TMN=0 TMX=39` CONTAINS the substring the unanchored
regex searched for, and is printed first.

THE FAILED PREDICTION I want attacked:
I predicted 15 pass / 0 fail. The run was 14 pass / 1 fail (`tools/bench/tmx_selftest.log:36`, the
run that starts at :26):
  FAIL | no TMX anywhere | got=None line='before: POS?=1=0.00000 ERR?=0' (want None)
      text='before: POS?=1=0.00000 ERR?=0'
(That case asserts BOTH the value and a substring of the reported line; its expected substring was
"no TMX line".)

MY EXPLANATION (the claim to attack):
"This FAIL is a STALE ASSERTION in a pre-existing test case, not a defect in the new parser. The case
checks two things: the VALUE (None) and the LINE the value came from. The value is unchanged and
still correct - None. Only the reported LINE changed, and it changed BY DESIGN and FOR THE BETTER:
the old code walked past the `before:` line into the LIMITS fallback, found nothing there either, and
returned the placeholder '(no TMX line in the gate's output)'; the new code stops at the `before:`
line and names it, which is precisely the fall-through that was being removed. So the right action is
to update that case's expected line to the `before:` line and add a separate case for 'no `before:`
line at all', which still returns the placeholder. No further change to `tmx_from` is needed."

ALREADY RULED OUT (do not spend the answer on these):
- The new fall-through case itself: `FALL-THROUGH: before: without TMX?= never reads LIMITS` PASSED
  (`tmx_selftest.log:37`), and the SAME fixture returned 39.0 against the unpatched parser
  (`tmx_fallthrough_before.log:4`), so the case is demonstrably discriminating.
- The anchoring: the two `PRELIMITS anchored ...` cases and `PRELIMITS with an empty field` all
  PASSED (`tmx_selftest.log:39-41`).
- `_last_field_float` on `<cmd>=<axis>=<value>`: PASSED (`:27`), unchanged by this patch.

QUESTIONS I MOST WANT ATTACKED:
1. Is "only the reported line changed" actually TRUE of every consumer, or am I asserting it from the
   self-test alone? Who reads the second element of `tmx_from`'s tuple, and can any of them behave
   differently now? (`drive_original_copy_v5.py:656-662` is the one I know about.)
2. Is updating a failing assertion to match new behaviour distinguishable, HERE, from the classic
   fault of editing the test until it goes green? What evidence in these files makes the difference,
   and what would it take for my move to be the bad kind?
3. The residual I did NOT close: when a transcript has NO `PRELIMITS` and NO `before:` line but DOES
   have a `LIMITS` line, `tmx_from` still answers from `LIMITS` - which in a `limits-set` transcript
   is post-write. Is that residual reachable in practice given `tools/motor_gate.py:368-370` always
   calls the sender in `limits-set` mode for `--session start`, and is leaving it open defensible, or
   is it the same false green wearing a different hat?
4. Anchoring `parse_pi_limits` to `(?m)^LIMITS`: does that break any real sender transcript - e.g. a
   line that is not flush-left because of how `tools/motor_gate.py:369` re-emits the text
   (`out(text.strip())`), or a `\r\n` transcript?
