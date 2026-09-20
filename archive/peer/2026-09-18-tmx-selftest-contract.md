# tmx-selftest-contract

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.0428  in 26 / out 26225 / cache-create 159975 / cache-read 1285901  (378s, 24 turn(s))
- **date:** 2026-09-18 19:03:08
- **outcome:** ANSWERED (380s)
- **why asked:** `tmx_from`'s precedence rules 3/4 were patched on an assembled rig's motor-limit path; the self-test's contract (16/0) and the docstring at `drive_original_copy_v4.py:295-299` disagreed about which half was stale.
- **verdict:** CONFIRMED by our own measurement — see "What was done with it".

## Question

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


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled for this role, as the peer brief requires — so the review is this answer.

# The claim defends a contract that its own producer refutes

## 1. The single strongest reason the claim is WRONG

**A `before:` line is not a limits-set marker — `--mode send` prints one too, and it never carries `TMX?=`.**

`tools/motor_send_pi.ps1:111` (send path): `before: POS?={0}  SVO?={1}  FRF?={2}  VEL?={3}  ERR?={4}` — **no `TMX?=` token**. Consequences, all from the same file:

- Rule 3 (`drive_original_copy_v4.py:286-294`, implemented at `:308-310`) is the rule that fires on **send-mode** transcripts.
- Rule 4 (`:295-296`) states its own justification as *"a `--mode send` transcript, where `LIMITS` is printed before any transmit"*. Rule 3 always preempts it. **Rule 4 is unreachable for the exact transcript class it was written for.**
- The `LIMITS` line rule 3 suppresses there (`motor_send_pi.ps1:103-105`) is the one `LIMITS` in this system that is genuinely **pre-write, pre-transmit, same-port-open** — send mode writes nothing before it. It is the correct answer to "what did the controller hold when the gate arrived", and the new rule discards it.
- Conversely, the *post-write* `LIMITS` the patch exists to block (`:73`, `:93`) appears only in limits-set/-release transcripts — where `:58`'s format string **unconditionally emits a literal `TMX?=`** token (empty string if the reply was unreadable, which `_last_field_float` turns into `(None, that line)` at rule 2). **Rule 3 can never fire there.**

So the headline rule cannot fire where the hazard lives, and does fire where it is wrong. Both halves of the self-test are downstream of a precedence rationale that misdescribes the sender; "which half is stale" is the wrong question.

Rule 3 is also dead code for the only two production callers — both run `motor_gate.py --session start` (`drive_original_copy_v4.py:1004-1006`, `diag_d0_pickloop_liveness.py:432-433`), which reaches PI only as `pi_call("limits-set", …)` (`motor_gate.py:375`, `:358-359`).

## 2. Alternative explanation of the same FAIL line

Not "the expectation is stale" — **the implementation and its fixture were edited out of step inside one un-reviewed patch.** `tmx_selftest.log:36` prints the label `no TMX anywhere`; the source at `:373` now reads `no TMX anywhere (reports the before: line it read)`. Different strings, and `%-40s` would have printed the longer one in full. So the file was edited after the only run on record, and **`--selftest` has not been re-run since** (the log holds exactly three runs: 18:16:30, 18:25:57, 18:45:48). The claim is an unrun prediction about a file that has already falsified one — the charge `archive/peer/2026-09-18-tmx-lastfield-parse.md:87,100` made two hours earlier.

Second alternative: **that case never tested the contract at all.** Its fixture has no `LIMITS` line, so it cannot distinguish fall-through from no-fall-through in either direction. It snapshots wording. The five hand-written cases carry the discrimination; this one is a tautology whichever way it is set.

## 3. Where `(None, before)` is worse, and the placeholder more honest

- The tuple is documented as *"(value_or_None, **the line it came from**)"* (`:281`). On a None return no line produced the value. `TMX?=None from 'before: POS?=1=0.00000 ERR?=0'` (`:1013`) reads as *the controller answered nothing* — a comms failure. The real condition rule 3 is built for is *the sender's `TMX?=` label drifted*, and the placeholder said that loudly. The change trades a format-drift alarm for a plausible-looking quote.
- Two other cases (`:341`, `:378`) still assert the placeholder, so the function's report format becomes **case-dependent** with no consumer told.
- Honest limit: this is cosmetic in practice. **Nothing parses the second element.** It is interpolated into human-readable detail strings only (`:1013`, `diag…:436`); the gate is `tmx == 39.0` (`:1012`), value-only, and `None` fails it — a false *red*, the safe direction. **The measurement does not distinguish the two candidate reports on any machine-checkable ground.** Meanwhile the send-mode suppression above is a real functional regression, and it is untested.

## 4. What would FALSIFY my refutation

`tools/motor_send_pi.ps1:111` not existing, or its `before:` line carrying a `TMX?=` token. Then rule 4 is reachable and rule 3 is harmless. Also falsifying: a send-mode transcript fed to `tmx_from` returning `39.0`.

## 5. Cheapest discriminating test — one fixture, no hardware

Add the real send-mode transcript to `selftest_tmx()` and run `py tools/bench/drive_original_copy_v4.py --selftest`:

```python
("send-mode transcript: the PRE-write LIMITS must still answer",
 "LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0\n"
 "before: POS?=1=30.00000  SVO?=1  FRF?=1  VEL?=1.0  ERR?=0",
 39.0, "LIMITS"),
```

`got=39.0` refutes me. `got=None` proves rule 4 is dead code and the docstring's rationale false. Either way the run also closes the unrun-prediction gap from §2 — that is why it is the cheapest test: it settles two questions in one execution and touches no motor, no VISA, no LabVIEW.

## Your Q5 — is the documented residual a route to the same false green?

**No — and that is worse news than yes.** `:297-299` describes a transcript with neither `PRELIMITS` nor any `before:` line. **Every mode of this sender prints a `before:` line** (`:58` for limits-set/-release, `:111` for send), so the residual as written is unreachable. It documents a scenario that cannot happen while the reachable ones are undocumented:

- **First/last asymmetry.** `prelimits_from` (`:269-277`) keeps the **LAST** matching `PRELIMITS`; the `before:` scan (`:304-307`) returns the **FIRST** match. A transcript containing two PI invocations (a retry, or a future `--session start` that calls limits-set twice) reports the second invocation's "pre-write" value — which is post-**first**-write. Same false-green class, arriving through the line the patch declared authoritative. No case covers it.
- **Whitespace tokenisation**, still untouched from the previous review (`archive/peer/2026-09-18-tmx-lastfield-parse.md:122`): an internal space makes the matched token `TMX?=1`, last field `1.0` — a silent wrong number, not None. Harmless against `tmx == 39.0`, live against any future `tmx <= 39` comparison.
- Checked and clear: `motor_asi_io.ps1:61` prints `before SL: …`, which fails `startswith("before:")`, so no cross-controller collision; `LIMITS SL X=…` fails `startswith("LIMITS TMN=")` (`:232`).

**The structural fix is neither branch of the disputed case.** The driver knows which mode it invoked (`motor_gate.py:358-359,375`); pre-/post-write is a property of the **mode**, not of which lines appeared. And the driver should not consult `LIMITS` at all — `motor_gate.py:377-378` already verifies it, so the driver's only distinct use of that line is the one use that must not happen. If the string must stay, `"(no TMX?= token in: %s)" % before[-1]` satisfies both halves and ends the dispute.

**What would change my mind:** the send-mode fixture above returning `39.0`, or evidence that `tmx_from` is contractually limits-set-only (no such contract is stated at `:280-299`, and nothing stops `diag_d0_pickloop_liveness.py:433` being pointed at a send transcript).

External checks: `TMX?` is *Get Maximum Commandable Position* and parameter `0x15` is *Maximum Travel In Positive Direction*, the positive soft limit — so a post-`SPA` `LIMITS` really is a different measurement from a pre-`SPA` `before:`, and the hazard the claim names is genuine. I could not extract the `<AxisID>=<value>` reply grammar from the Mercury command manual (the PDF did not parse); the nearest sourced confirmation of that reply shape is the `1 0X40=125` example on the spec help page, which is weaker evidence than `motor_send_pi.ps1:74`'s live readback check passing on 2026-09-18 (`STATUS.md:53,113`).

Sources: [C-863 Mercury Controller User Manual MS205E](https://www.le.infn.it/~chiodini/allow_listing/pi/Manuals/C-863_UserManual_MS205E200.pdf) · [Mercury GCS Commands MS163E102](https://twiki.cern.ch/twiki/pub/ILCBDSColl/Phase2Preparations/Mercury_GCS_Commands_MS163E102.pdf) · [CSS spec help: pi_gcs](https://certif.com/spec_help/pi_gcs.html) · [PI E-871 user manual (parameter 0x15)](https://www.manualslib.com/manual/1523161/Pi-E-871-1a1n.html)

## Sources

(extract from answer)

## What was done with it

ACCEPTED AS A HYPOTHESIS, NOT AS GROUNDS TO PATCH (cycle-34 judgement session). No motor-limit parser was
changed this cycle. Cycle-34 material dispatch C then RAN THE PEER'S OWN CHEAPEST DISCRIMINATING TEST (§5,
this file's `:102-113`), which nobody had run.

1. **Premise verified independently.** `tools/motor_send_pi.ps1:58` (limits-set) emits a literal `TMX?=`;
   `:111` (send) emits `before: POS?=…  SVO?=…  FRF?=…  VEL?=…  ERR?=…` with no `TMX?=` token. Two
   `before:` emitters, exactly as the peer says.
2. **The test was run** with a throwaway script (`tools/bench/tmx_sendmode_probe.py`, created and deleted
   in the same operation; the logs are the record — `tools/bench/tmx_sendmode_probe.log` run 1, 2 pass /
   1 fail, and `tools/bench/tmx_sendmode_probe2.log` run 2, **4 pass / 0 fail, `BGRUN END rc=0`**; run 1's
   single red was the dispatch's own mis-specified control gate, not a parser fault). Verbatim results:

   ```
   RESULT a | value=None | line='before: POS?=1=30.00000  SVO?=1  FRF?=1  VEL?=1.0  ERR?=0'   (send mode)
   RESULT b | value=39.0 | line='PRELIMITS TMN=0 TMX=39'                      (limits-set, full)
   RESULT c | value=39.0 | line='PRELIMITS TMN=0 TMX=39'                      (send + PRELIMITS)
   RESULT d | value=39.0 | line='before: POS?=1=30.00000 TMN?=1=0.00000 TMX?=1=39.00000 ERR?=0'
   ```

   By the reviewer's own criterion at `:113`, `got=None` on (a) **CONFIRMS the refutation**: rule 3
   pre-empts rule 4, so rule 4 is dead code for the send-mode transcript class its docstring was written
   for.
3. **Scope measured, and it bounds the damage.** Every production call site of `tmx_from` / `parse_motor`
   (`drive_original_copy_v4.py:1006`, `:848`, `:1007`; `drive_original_copy_v5.py:656`, `:501`, `:657`;
   `diag_d0_pickloop_liveness.py:433`, `:210`) is fed by `motor_gate()` = `motor_gate.py --session start`
   = `pi_call("limits-set", …)` (`tools/motor_gate.py:375`) ONLY. The fleet's two PI `--execute` users
   (`tools/bench/motor_gate2_live.py`, `tools/bench/asi_xy_check.py:20-21`) call neither parser. So the
   regression is **theoretical and latent**, and if a send transcript ever reaches it the answer `None`
   fails the value-only gate `tmx == 39.0` (`v4:1012`) — a false RED, the safe direction.
4. **Still open for judgement, recorded in `STATUS.md` OPEN 55:** make the precedence mode-aware (the
   driver knows the mode it invoked), or stop consulting `LIMITS` in `tmx_from` altogether since
   `motor_gate.py:377-378` already verifies it. Not a material session's call — it changes what a
   motor-limit gate accepts on an ASSEMBLED rig.
