ATTACK this claim about a FAILED PREDICTION in `tools/bench/tmx_selftest.log` (this project's motor-limit
parser self-test, run as `py -u tools/bench/drive_original_copy_v4.py --selftest`).

## The observation (machine record, `tools/bench/tmx_selftest.log:26-43`, BGRUN END rc=1 after 0s)

The newest self-test block reports **14 pass / 1 fail**. The one failing row is:

```
  FAIL | no TMX anywhere  | got=None line='before: POS?=1=0.00000 ERR?=0' (want None)  text='before: POS?=1=0.00000 ERR?=0'
```

Two earlier blocks in the same file: 18:16:30 = 8 pass / 1 fail (rc=1), 18:25:57 = 10 pass / 0 fail (rc=0).
The case named `no TMX anywhere` PASSED in the 18:25 block with
`got=None line="(no TMX line in the gate's output)"`, and the 18:45 block changed that case's INPUT to
`before: POS?=1=0.00000 ERR?=0` — a `before:` line that carries no `TMX?=` token.

The function under test is `tmx_from` / `_last_field_float` in `tools/bench/drive_original_copy_v4.py`
(~line 234-270). The change being made in that file is STATUS.md OPEN 55: emit a normalised
`PRELIMITS TMN=<n> TMX=<n>` line from `tools/motor_send_pi.ps1:52` and make `tmx_from` return `(None, s)`
when a `before:` line exists but carries no `TMX?=` token, so the parser can no longer fall through to the
post-write `LIMITS` line and report back the value it just wrote (a silent false green on an ASSEMBLED rig).

## The claim to attack

> The failing row is a **self-test EXPECTATION defect, not a parser defect**: the row prints
> `got=None ... (want None)`, i.e. the returned VALUE already equals what the test wants, so the FAIL can
> only come from the assertion ALSO comparing the second element of `tmx_from`'s `(value, line)` tuple —
> the case was renamed/repurposed from "no TMX line at all" (where the second element is the
> `(no TMX line in the gate's output)` placeholder) to "a `before:` line with no `TMX?=`" (where the new
> fall-through branch returns the `before:` line itself), and the expected `line` string was not updated
> with it. Therefore the new refusing behaviour is correct and only the test's expectation is stale.

## What I want from you

1. The strongest reason this claim is WRONG.
2. An alternative explanation of a `FAIL` row that prints `got=None ... (want None)` — including
   explanations in which the PARSER is at fault (e.g. the fall-through returns the wrong `s`, or the
   `(None, s)` contract is inconsistent between the `before:`-present and `before:`-absent branches, or the
   new anchored `PRELIMITS` regex shadows the case).
3. What would FALSIFY the claim.
4. The CHEAPEST discriminating test that separates "stale test expectation" from "parser returns the wrong
   second element", using only this repository (no rig, no motors, no LabVIEW).

## Already ruled out (do not re-propose)

- Not a rig/hardware fault: `--selftest` runs pure string parsing, no serial port is opened (BGRUN END after 0 s).
- Not a flaky/timing fault: the block completes in 0 s and the three blocks are deterministic.
- Not a regression in the other 14 rows: every other case, including the two new `PRELIMITS` anchoring cases
  and the `FALL-THROUGH: before: without TMX?= never reads LIMITS` case, passes in the same block.

## Context you should know

This failure was produced by a PARALLEL material dispatch that is editing
`tools/bench/drive_original_copy_v4.py` right now; I am a different dispatch, blocked by
`tools/hooks/guard_peer.py` behind it. So judge the log, not my access to the author's intent.
