# pi-err5-unreferenced-opus

- **agent:** claude
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.8839  in 26 / out 37198 / cache-create 206881 / cache-read 1243353  (567s, 26 turn(s))
- **date:** 2026-09-18 15:51:51
- **outcome:** ANSWERED (568s)
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

Write is disabled for this role (correct — I'm read-only), so the review is the answer itself.

---

# Failed-prediction review — PI C-863.11 ERR 5, 2026-09-18 15:37

**Verdict, split:** the *diagnosis* (error 5 = unreferenced axis) is probably right. The two things hanging off it — **"not our SPA writes"** and **"the fix is `RON 1 0` + `POS 1 <current>`"** — do not survive, and those are the parts that decide what happens to the safety gate.

## 1. The strongest reason the claim is WRONG

**The run never read `FRF?` before its own SPA writes. The measurement order destroyed the evidence that would have exonerated SPA.**

- `tools/bench/motor_gate2_live.log:3-18` — L1 `--session start` writes `SPA 1 0x15` / `0x30` **first** (`ERR? after SPA = 0`, line 5). Its `before:` line (4) reads `POS? TMN? TMX? ERR?` — **no `FRF?`, no `RON?`**. Confirmed in code: the limits-set path in `tools/motor_send_pi.ps1:47-62` never queries them.
- `motor_gate2_live.log:25` — the **first and only** `FRF?` of the run is inside L2 at 15:37:18, *after* those writes (`motor_send_pi.ps1:73` is the sole line that reads it).
- The 14:50 corroboration is worse: `tools/bench/p2_pi_softlimit_test.log:14` shows its `BEFORE` reads came back as **help-text fragments** (`POS?=y status TMN?=ion>} Set Closed-Loop Acceleration …`), and line 13 says `HLP has SPA: False`. That channel was **desynchronised** — an `ERR?=5` read on it is not a reliable code for the `MOV` before it. Down-weight, don't discard.

Both ERR-5 events happened after SPA writes; neither has a pre-SPA FRF reading. The one run that produced the expected ERR 7 (`p2_pi_softlimit_test2.log:6-10`, 15:08:41) is the one in that window that **wrote no SPA at all**. The brief treats SPA's innocence as established; the data are 2-for-2 the other way. And its exclusion clause — *"nobody ran a PI write **from this project**"* — excludes exactly the actor most likely responsible.

## 2. Alternative explanations

**(a) The reference was re-armed, not lost.** At 15:08:39 we deliberately left `RON?=0` (`p2_pi_ron_off.log:3`). The documented post-D0 signature is **`RON 1 / FRF 0`** (`docs/motor-limit-assurance-plan.md:141`) — *something sets RON back to 1*, which invalidates a POS-declared reference by construction, with no power cycle and no effect on TMN/TMX. Exactly your signature. The same line records the original VI's own mode as `RON 1 0` + `POS 1 <z>`, so its PI init manipulates RON. **You never read `RON?` at 15:37.**

**(b) The servo was cycled.** delmic/odemis `pigcs.py` states in `_stopServo()` that **"Referencing is lost"** when the servo goes off. A VI shutdown, stop button, following error or MikroMove disconnect does it — again leaving RAM intact.

**(c) Our SPA writes.** Still live, per §1. I found **no PI document asserting or denying** that SPA of 0x15/0x30 clears the reference; absence in what I could reach is not evidence of absence. Measure it, don't argue it.

## 3. What would FALSIFY the claim

**`RON?` reading 1 right now.** Our last write left it 0. If it reads 1, the axis was *actively re-armed* between 15:08:41 and 15:37 — the causal story is wrong even though the ERR-5 reading is right. Conversely, **`FRF?` dropping 1→0 across a no-op SPA write** falsifies the gate's exculpation outright.

## 4. Cheapest discriminating test

Two steps, inside your approved write set, **no motion, ~10 s.**

**Step 1 (pure read).** One port open: `RON? 1 · FRF? 1 · SVO? 1 · POS? 1 · TMN? 1 · TMX? 1 · ERR?`
`RON?=1` → alternative (a); SPA exonerated. `RON?=0` → nothing external touched reference mode, so **SPA/servo are the only candidates left** — the thing the brief assumed without testing.

**Step 2 (only if SPA survives step 1).** Restore (`RON 1 0`, `POS 1 0`), verify `FRF?=1`, then write **the two values already in force** — `SPA 1 0x15 39`, `SPA 1 0x30 0`, a genuine no-op — and re-read `FRF?`. If it goes 1→0, the session-start hook **disarms the axis every time it arms the fence**. Read `ERR?` after *each* command so a desynchronised channel can't be mistaken for a result again.

## Your five questions

**Q1 — Can SPA clear FRF?** Unknown; **the evidence does not distinguish it**. No vendor doc I could reach settles it either way; odemis has no such comment (weak evidence). What I can say: your own points correlate ERR 5 with SPA 2-for-2, ERR 7 with no-SPA 1-for-1, and the breaking measurement was never taken.

**Q2 — Is error 5 really "unreferenced"?** Documented text has exactly two branches: *"Unallowable move attempted on unreferenced axis, **or move attempted with servo off**"* (`PI_CNTR_MOVE_WITHOUT_REF_OR_NO_SERVO` = 5). `SVO?=1` favours the first. Caveats: `SVO?` was read ~1 s before the `MOV`, so a transient servo drop isn't excluded; I found no source giving this firmware a third meaning. One confirmation you didn't use: **L2's target was 5 mm, well inside 0–39, and was still refused with 5** (`motor_gate2_live.log:21,27`) — so the refusal is definitely not limit-related, and the reference check precedes the limit check.

**Q3 — FRF 1→0 without a power cycle?** §2(a) RON re-armed, or §2(b) servo cycled. Both preserve TMN/TMX. Falsified by §3.

**Q5 — Is `RON 1 0` + `POS 1 0` safe?** *Physically, right now,* yes — neither command moves the axis, and there's a clean custody chain (driven to 38.5 and back to 0 while referenced at 15:08:41, `p2_pi_softlimit_test2.log:8-9`; every `MOV` since refused). **But your stated reason is not a reason** — `POS?` reading 0 is the number under suspicion, not evidence for it. Three things follow that the brief doesn't say:

1. **`POS` doesn't restore a reference, it fakes one.** odemis documents it exactly: setting position with RON disabled *"causes the axis to report as referenced (via FRF?) despite not being truly referenced."* Afterwards `FRF?=1` is a value you told the controller.
2. **It is the operation your own gate refuses on principle.** `tools/motor_gate.py:68` — *"A zero shift MOVES THE FENCE"*; `motor_gate.py:86-88` lists `POS` as *"would SHIFT the coordinate zero under the absolute [limits] … do not change it"*; L7 refused ASI `HOME` for that very reason (`motor_gate2_live.log:89`). **The remedy is the PI equivalent of the ASI `HOME` the gate forbids.** `POS 1 <current>` can never *correct* a coordinate error — only **ratify** one, sliding the physical fence by exactly that error. It is safe this time by custody, and won't be the time it's needed: the next reference loss will follow a D0 run that *did* move the magnet.
3. **The ERR-5 state is the fail-safe one.** `RON=1, FRF=0` refuses every absolute move. Setting `RON=0` trades that for convenience — thereafter a lost reference is silent. The fence itself still works in RON-0 (`p2_pi_ron_off.log:3` → `p2_pi_softlimit_test2.log:6-7` gave ERR 7); only its *zero* becomes yours to get wrong. Make restoring the reference an explicit logged operator step with position from an independent source, not something the session hook does by itself.

## Three things in the record the framing walked past

**D1 — the gate reports a REFUSED command as a successful move.** `tools/motor_send_pi.ps1:93` decides success on **position alone** (`|final-target| < 0.01 → exit 0`); `$err` is captured at line 76 and **never used in the verdict**. So L4's `MOV 1 0` — rejected, `ERR? = 5` — exited 0, printed *"RESULT: reached 0"*, scored **PASS**, and entered the audit log as `rc=0 … RESULT: reached 0` (`motor_gate2_live.log:55-60,130`). Any command whose target equals the current position passes without executing, writing a **false position belief** into a system whose every mechanism is denominated in position. Fail unless `ERR?` after send is 0.

**D2 — the gate reads the datum that predicts refusal and transmits anyway.** `motor_send_pi.ps1:73` prints `FRF?`/`SVO?`, line 74 transmits unconditionally; only TMN/TMX gate the send (69-72). And the permission text asserts a mechanism it hadn't verified in the axis's actual state — *"a target outside them answers ERR 7 and does not move"* (`motor_gate2_live.log:21,35`) — while the axis was in a state that answers 5.

**F1 — flagged, not alarming: the fence's UNIT is unverified.** You name the stage **M-126.PD1**, travel range **25 mm**. Yet `TMX?` natively reads **52** (`docs/motor-limit-assurance-plan.md:19-20`) and the axis *settled* at `POS=38.5` with `ERR?=0` (`p2_pi_softlimit_test2.log:8`) — 38.5 units of real encoder travel on a nominally 25 mm stage. At least one of {stage identity, `motor_gate.py:31`'s *"PI native unit = mm (M-126.PD1)"*, the 52 mm native range} is wrong. Probably benign operationally — 0–39 shares units with the panel's own 0…40.84 (`motor-limit-assurance-plan.md:130`), so the fence is strictly tighter — but it matters the moment anyone reasons about **physical** clearance from "39". `SPA? 1 0xE` plus the stage assignment would settle it.

## What would change my mind

If step 1 returns `RON?=0` **and** step 2 shows `FRF?` surviving a no-op SPA, the hypothesis is right on every count except its evidence, and (b) a servo cycle by the D0 VI is what's left. I'd still hold D1, D2 and the Q5 objection — none of them depend on the cause.

Sources: [PI GCS error codes (`picontrollererrors.h`)](https://www.slac.stanford.edu/grp/lcls/controls/global/doc/epics-modules/R3.15.5-1.0/motor/R6.10.1-1.0.1/motorApp/PIGCS2Src/picontrollererrors.h) · [spec `pi_gcs` help — error 5 text, RON 0 + POS](https://certif.com/spec_help/pi_gcs.html) · [delmic/odemis `pigcs.py`](https://github.com/delmic/odemis/blob/master/src/odemis/driver/pigcs.py) · [C-863 manual MS205E](https://www.le.infn.it/~chiodini/allow_listing/pi/Manuals/C-863_UserManual_MS205E200.pdf) (text not extractable — certificate error; the SPA/reference question is **not** settled from vendor docs) · [PI M-126 datasheet](https://www.pi-usa.us/fileadmin/user_upload/pi_us/files/product_datasheets/M126_Precision_Positioning_Stage.pdf)

## Sources

(extract from answer)

## What was done with it

ACCEPTED in part, 2026-09-18 16:0x (material session). This arm found a defect in our own code that the codex arm
did not, and that defect had already produced a FALSE PASS in the run under discussion.

1. **D1 ACCEPTED AND FIXED:** `tools/motor_send_pi.ps1` decided success on position alone, so L4's `MOV 1 0` —
   rejected with ERR 5 while the axis already sat at 0 — printed "RESULT: reached 0", exited 0 and scored PASS in
   `tools/bench/motor_gate2_live.log`. The sender now requires `ERR?` right after the send to be `0` **and** the
   position to match, else `RESULT: REJECTED BY THE CONTROLLER ... exit 9`. **Consequence for the record: L4 of the
   15:37 run was NOT a successful move — no PI motion happened at all in that run.**
2. **"Not our SPA writes" WITHDRAWN.** The coordinator's 15:5x reading (`RON?=0 FRF?=0` after nothing but our two
   `SPA` pairs since the axis was referenced at 15:08) is consistent with this arm's position, so the gate now
   treats "SPA leaves the axis unreferenced" as the working assumption and the session-start hook repairs it in
   the same port open (`RON 1 0` + `POS 1 <the number POS? just returned>`), verifying `FRF?=1` and that `POS` did
   not change; it refuses the whole session otherwise. Self-test cases 3b/3c, 76/76.
3. **The zero-vs-physical-truth objection is ACCEPTED and left OPEN** (same as the codex arm): our limits are
   absolute in CONTROLLER coordinates, and nothing we can read proves those still coincide with the original
   physical zero. STATUS OPEN 53; no code or document claims otherwise.
4. **Not adopted:** any reference move (`FRF`/`FNL`/`FPL`/`GOH`) — they move the axis and stay refused.
5. **Not verified yet:** the fixed hook could NOT be re-run live — the two re-run attempts were refused by the
   session's permission classifier (Modify Shared Resources), so the discriminating test this arm asked for is
   still outstanding. Cost line: $3.8839, 568 s, 26 turns.
