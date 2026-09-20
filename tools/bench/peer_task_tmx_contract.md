# ATTACK this claim — `tmx_from`'s fall-through contract and which half of the self-test is stale

Repo-relative files you may read: `tools/bench/drive_original_copy_v4.py` (`tmx_from` at :280, `selftest_tmx`
at :318), `tools/motor_send_pi.ps1` (:52 `PRELIMITS`, :58/:78 `LIMITS`), `tools/bench/tmx_selftest.log`,
`tools/bench/tmx_fallthrough_before.log`, `archive/peer/2026-09-18-tmx-lastfield-parse.md`.

## THE CLAIM TO REFUTE

> When `parse_motor` finds a `before:` line carrying no `TMX?=` token, `(None, <that line>)` is the correct
> return for `tmx_from`, and the self-test case asserting the old placeholder string
> `"(no TMX line in the gate's output)"` is the stale half. The alternative the old code took — falling
> through to the `LIMITS` line — reports back the value the gate itself just wrote, i.e. a silent false green
> on a motor-limit check on an ASSEMBLED rig.

## THE FAILURE ON RECORD

`tools/bench/tmx_selftest.log:36` (run of 18:45:48, `BGRUN END rc=1`, `SELFTEST tmx_from: 14 pass / 1 fail`):

```
FAIL | no TMX anywhere | got=None line='before: POS?=1=0.00000 ERR?=0' (want None)  text='before: POS?=1=0.00000 ERR?=0'
```

The returned VALUE (`None`) matches. Only the assertion on the REPORTED LINE fails: the case still expects the
substring `"no TMX line"`, i.e. the placeholder the old fall-through produced.

## WHAT IS ALREADY RULED OUT (do not spend the answer on these)

- Not a `_last_field_float` bug: the per-axis form `TMX?=1=39.00000` parses correctly — `tmx_selftest.log:27` passes.
- Not a `PRELIMITS` regex problem: all four anchored-regex cases pass (`tmx_selftest.log:38-41`).
- Not a rig/hardware question: this dispatch touched no motor, no VISA, no LabVIEW; it is pure-function self-test.

## WHAT TO ANSWER

1. The strongest reason the claim is WRONG — including any case where returning `(None, <before: line>)` is worse
   than returning the `LIMITS` value, or where the placeholder line is the more honest report.
2. An alternative explanation for that FAIL line other than "the expectation is stale".
3. What observation would FALSIFY the claim.
4. The cheapest discriminating test, runnable without hardware.
5. Specifically: is the residual documented at `drive_original_copy_v4.py:295-299` — `LIMITS` may still answer
   when a transcript has NEITHER `PRELIMITS` NOR any `before:` line — itself a route to the same false green?
