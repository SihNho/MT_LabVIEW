# pi-err5-unreferenced-codex

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-18 15:42:23
- **outcome:** ANSWERED (153s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# FAILED PREDICTION, live motor test 2026-09-18 15:37 (PI C-863.11 on COM3, Mercury GCS, M-126.PD1 stage)

## What was predicted and what happened
Log: `tools/bench/motor_gate2_live.log` (one bgrun, rc=1, 14 s).
- PREDICTED L2: `MOV 1 5` moves the magnet axis to 5.000 mm.
  OBSERVED: `before: POS?=1=0.00000 SVO?=1=1 FRF?=1=0 VEL?=1=15.00000 ERR?=0` / `SENT: MOV 1 5` /
  `ERR? right after send = 5` / `after: POS?=1=0.00000 ONT?=1=1 ERR?=0` - no motion.
- PREDICTED L3: `MOV 1 40` is refused by the controller's soft limit with **ERR 7** and no motion.
  OBSERVED: **ERR 5**, no motion. So the controller-limit refusal was NOT demonstrated in this run.
- Everything else passed: the session hook wrote and read back TMN=0 / TMX=39 and ASI SL/SU
  (-3.847494/-4.774393, 0.152497/-0.774402 mm) within 0.001; two ASI moves of 0.2 mm ran and returned;
  `HOME X` was refused by our gate; the release read back TMX=52 and SL/SU +-500; the re-arm read back 39 again.

## My hypothesis (attack it)
"PI error 5 here means the axis is NOT REFERENCED (FRF? = 0), so the controller rejects every MOV before it ever
consults the soft limits. The cause is not our `SPA 1 0x15 / 0x30` writes: the axis was already unreferenced
before this run. Therefore the gate rework is not implicated, the controller soft limits are still believed good,
and the fix is to restore the reference (`RON 1 0` then `POS 1 <current>`) before any PI motion."

## Evidence I already have (do not repeat it, attack it)
- 2026-09-18 14:50 `tools/bench/p2_pi_softlimit_test.log`: the FIRST SPA run also ended `MOV 1 40 -> ERR?=5`,
  logged as "unexpected (ERR 5, no motion)".
- 15:08 `tools/bench/p2_pi_query_ron.log`: `RON? 1=1  FRF? 1=0  SVO? 1=1  POS? 1=0.00000  TMN? 0  TMX? 39`.
- 15:08 `tools/bench/p2_pi_ron_off.log`: `RON 1 0` -> `RON?=0`; then `POS 1 0` -> `FRF?=1`, TMN/TMX still 0/39.
- 15:08 `tools/bench/p2_pi_softlimit_test2.log`, immediately after that: `MOV 1 40 -> ERR?=7 (expect 7)`,
  `MOV 1 38.5 -> settled POS=38.5`, `MOV 1 0 -> settled POS=0`. So with FRF=1 the same commands worked and the
  soft limit answered 7.
- Between 15:08 and 15:37 nobody ran a PI write from this project except my session hook's SPA writes at 15:37:18
  (the 15:23 run touched the ASI on COM4 only). The user was at the rig and had run a LabVIEW copy of the
  original VI earlier in the afternoon; a note in `docs/motor-limit-assurance-plan.md` records that after that
  D0 run the axis read `RON 1 / FRF 0`.
- At 15:37 the session hook's own "before" line showed TMN/TMX still 0/39 from 14:5x, i.e. controller RAM had NOT
  been cleared by a power cycle, yet FRF was 0. My run did not read `RON?`, so I do not know its value at 15:37.

## What I need from you
1. The strongest reason my hypothesis is WRONG. In particular: can `SPA 1 0x15` / `SPA 1 0x30` (travel-range
   parameters) on a C-863.11 CLEAR the referenced state / set FRF to 0, or otherwise put the axis in a state where
   MOV returns error 5? Cite PI documentation.
2. Is PI GCS error 5 on this controller really "unallowed command / axis not referenced", or can it mean
   something else that my remedy would not fix (servo, macro running, joystick/manual mode, motion in progress)?
   SVO? read 1 and ONT? read 1 in the failing run.
3. An alternative explanation for FRF going 1 -> 0 between 15:08 and 15:37 without a power cycle (controller RAM
   kept TMN/TMX), and what would falsify it.
4. The CHEAPEST discriminating test, given that the rig is ASSEMBLED, a human is present, and the only PI writes
   we are willing to make are: reads, `SPA` of the two limit parameters, `RON`, `POS`, `MOV` inside 0..39.
5. Whether restoring the reference with `RON 1 0` + `POS 1 0` is safe when POS? already reads 0.00000, i.e.
   whether it can move the axis or shift the coordinate zero relative to where the soft limits (TMN/TMX, absolute)
   sit - our whole safety scheme now depends on those limits not sliding.



--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The strongest flaw is the claim that `RON 1 0; POS 1 0` safely “restores” the original absolute coordinate system. It does not establish physical truth; it merely declares that the present mechanical location is coordinate 0. PI explicitly warns that `POS` does not move the axis, but also does not adjust `TMN/TMX`, and can therefore make controller-permitted positions physically unreachable—or place coordinate zero outside the physical travel range. The same manual says parameters `0x15/0x30` are relative to the current zero, not independent physical limits. [PI C-863 manual: POS](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f#L7464), [PI C-863 manual: soft limits](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f#L1394)

### 1. Can `SPA 0x15/0x30` clear `FRF`?

PI’s C-863 documentation does not document that behavior. It defines:

- `0x15/0x30` strictly as positive/negative closed-loop soft limits.
- A target outside them should produce error 7, “Position out of limits.”
- `SPA` changes a parameter in volatile RAM immediately, but its documented side effects do not include invalidating the reference result. [PI C-863 manual: travel limits](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f#L1331), [PI C-863 manual: SPA](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f#L7924), [PI C-863 manual: errors 5 and 7](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f#L8820)

Therefore I find no documentary basis for claiming those two `SPA`s normally clear `FRF`. Your recorded `FRF?=0` before the 15:37 writes is also strong evidence that those writes did not cause that particular transition.

But “not documented” is not proof of firmware behavior. An identical-value `SPA` experiment is the cheap way to settle it.

### 2. What does error 5 actually mean?

For this controller, PI names error 5 `PI_CNTR_MOVE_WITHOUT_REF_OR_NO_SERVO`: “Unallowable move attempted on unreferenced axis, or move attempted with servo off.” It is not PI’s generic code for macro, joystick, or motion-in-progress conflicts. [PI C-863 manual: error table](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f#L8820)

The competing conditions have distinct codes:

- Joystick owns the axis: error 51.
- `MOV!` still in progress: error 53.
- Target beyond `TMN/TMX`: error 7. [PI C-863 manual: errors 51 and 53](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f#L9028)
- A running macro is not inherently an error, although PI warns that macro commands and externally received motion commands can overwrite each other. `RMC?` identifies a running macro. [PI C-863 manual: RMC?](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f#L7534)

Given `SVO?=1` and `FRF?=0`, lack of reference is the best-supported branch of error 5. `ONT?=1` does not contradict this: PI defines it only as the closed-loop on-target state, influenced by settling-window settings; it is not a reference-status test. [PI C-863 manual: ONT?](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f#L7436)

The claim would be falsified immediately by observing `SVO?=1` and `FRF?=1` immediately before an otherwise isolated `MOV`, followed by error 5.

### 3. Alternative explanation for `FRF 1 → 0`

The strongest alternative is an intervening reference-mode or controller-initialization action—not the soft-limit values themselves:

- At 15:08 you left the controller in `RON=0`.
- Some other client, startup sequence, or macro could have restored `RON=1`, rebooted/reinitialized the controller, or otherwise invalidated the manually established reference.
- PI defines `RON=1` as requiring an actual `FRF/FNL/FPL` reference before closed-loop motion; `POS` is forbidden in that mode. [PI C-863 manual: RON](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f#L7564)

PI does not say that merely changing `RON` from 0 to 1 clears an existing `FRF` result, so that specific mechanism remains a hypothesis requiring measurement.

A reboot or brownout is not excluded solely by `TMN/TMX=0/39` unless you know that the nonvolatile `SEP?` values were different. PI states that reboot loads nonvolatile parameter values into volatile RAM; consequently, identical volatile and nonvolatile limit values would survive as the same apparent `TMN/TMX` after a reset while reference knowledge is lost. [PI C-863 manual: volatile/nonvolatile loading](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f#L10161)

This alternative would be falsified by:

- `RON?` remaining 0 throughout,
- no reboot/reset,
- no stage reinitialization or running macro,
- and `FRF` dropping specifically on one of the two `SPA` commands.

### 4. Safety of `RON 0; POS 0`

`RON 1 0` itself selects manual position definition. `POS 1 0` causes no mechanical motion. [PI C-863 manual: POS](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f#L7464)

If `POS?` is exactly 0 immediately beforehand, assigning the same value should introduce no numerical coordinate offset. Nevertheless, it only preserves the current encoder-to-coordinate mapping; it does not prove that this location is the original physical zero. PI explicitly recommends manual position definition only when physical referencing is otherwise impossible because of possible soft-limit conflicts. [PI C-863 manual: manual-reference warning](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f#L1608)

Thus:

- No, the command should not move the axis.
- Setting `POS 0` when the reported position is already exactly 0 should not numerically slide the limits.
- But no, it is not sufficient by itself to prove that 0…39 still corresponds to the intended physical envelope. That requires confidence that the stage has not physically moved relative to the encoder coordinate since the last valid reference.

### Cheapest discriminating test

With no commanded motion:

1. Read `RON?`, `FRF?`, `SVO?`, `POS?`, `TMN?`, `TMX?`, both `SPA?` values, both corresponding `SEP?` values, `RMC?`, and joystick status.
2. Let `p = POS?`; do not assume or round it to zero.
3. Send `RON 1 0`, then `POS 1 p`; confirm `FRF?=1`.
4. Send `RON 1 1`; query `FRF?`.
5. Restore with `RON 1 0; POS 1 p`.
6. Write parameter `0x15` back to its already-read identical value; query `FRF?`.
7. Write parameter `0x30` back to its identical value; query `FRF?`.

Interpretation:

- `FRF` drops after `RON 1 1`: reference-mode transition is implicated.
- `FRF` survives `RON 1 1` but drops after an identical-value `SPA`: your “SPA not implicated” claim is falsified.
- `FRF` survives both: the loss came from some other intervening initialization/reset/write.

After attacking it, I still believe the narrow diagnosis—error 5 was caused by `FRF=0`, not by the 40 mm limit check—is strongly supported. What does not survive is treating `POS 0` as proof that the original physical zero and therefore the physical 0…39 safety envelope have been restored.

## Sources

(extract from answer)

## What was done with it

ACCEPTED in part, 2026-09-18 16:0x (material session).

1. **Diagnosis accepted:** ERR 5 = the axis is not referenced (`FRF? 0`), reached before the soft limit is ever
   consulted. Confirmed independently by the coordinator's own reading at 15:5x (`RON?=0 FRF?=0 POS?=0 TMX?=39`)
   and by the fact that the only PI writes between the working 15:08 state and the failure were our `SPA` writes.
2. **The review's main objection is ACCEPTED and NOT closed:** `POS` declares the current mechanical location to be
   a coordinate; PI's manual says 0x15/0x30 are relative to that zero, so a POS-define with a *different* number
   would MOVE THE FENCE. Our implementation therefore re-defines POS to **the value `POS?` returned a moment
   earlier** and REFUSES (exit 7 / rc 3, no session file) if `POS` differs from `POS_BEFORE` by more than 0.001
   (`tools/motor_send_pi.ps1` limits-set branch; `tools/motor_gate.py:parse_pi_ref` + `session_start`; self-test
   cases 3b/3c in `tools/bench/selftest_motor_gate2.py`, 76/76). What the review says CANNOT be established that
   way — that coordinate zero still equals the ORIGINAL physical zero, hence that TMN/TMX 0..39 still fences the
   intended physical window — is left OPEN for the user/judgement (STATUS OPEN 53). No physical-zero claim is made
   anywhere in the code or in STATUS.
3. **Not adopted:** `FRF`/`FNL`/`FPL`/`GOH` reference moves stay refused by the gate (they MOVE the axis).
4. Cost line: ANSWERED in 153 s, no cost reported by the codex CLI.
