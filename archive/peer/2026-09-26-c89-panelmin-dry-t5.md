# c89-panelmin-dry-t5

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.4588  in 26 / out 15131 / cache-create 106180 / cache-read 1372002  (176s, 21 turn(s))
- **date:** 2026-09-26 02:19:41
- **outcome:** ANSWERED (180s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about the failed prediction in tools/bench/m8_panelmin_89_dry.log (script tools/bench/drive_m8_panelmin89.py, leg wrapper tools/bench/drive_m8_panelmin89_leg.py, card tools/bench/cards/task_89-4.json).

FAILED PREDICTION: gate `T5 leg1 min@15@90Hz frames/s within 15% of 90` (and the same for leg2 ctl) FAILED in the --dry run; all other 13 gates passed (M1..M8 per leg, PM0, T1..T4, T6..T9).

CLAIM: the T5 failure is a dry-fixture artefact, not a fault of the new sequencer or of the leg wrapper. In --dry mode drive_m8.py installs m8_dry.stub (tools/bench/m8_dry.py:21-32), whose fake_leg writes a FIXED frame series `[100, 3000]` regardless of --run-s; the sequencer computes measured_hz = frames_delta / RUN_S = 2900 / 120 = 24.2 Hz, which is outside 15 % of 90 by construction. The cycle-88 sequencer drive_m8_load83_kswap88.py has the identical T5 formula (line 107) and its real legs measured 89.0 Hz (tools/bench/m8_kswap_88.json rows). The real legs of drive_m8_panelmin89.py will therefore not fail T5 for this reason, and the correct patch is to exempt T5 in DRY mode (or to scale the fixture by RUN_S), nothing in the real path.

Already ruled out: the argv plumbing (both legs reached M1..M8 PASS and PM0 PASS in dry); the backup/restore of the fixed json names (T9 PASS); the md5 pins (T8 PASS).

Questions: (1) strongest reason the claim is wrong - is there any way the REAL path of drive_m8_panelmin89_leg.py (the patched d0.answer_save_dialog / v5.stop_with_fallback, the private MinCom apartment setting VirtualInstrument.FPState) could itself lower the measured frame rate or break T5? (2) alternative explanation of the dry T5 failure; (3) what would falsify the claim; (4) cheapest discriminating test. Also flag anything in the leg wrapper that would make the L-min leg unsafe or unmeasurable (e.g. FPState enum values assumed as Standard=1 / Minimized=4, a minimized panel breaking v5's later steps L12/L13/cleanup, or lv_gui `rect` behaviour on an iconic window).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

I've finished the review. My answer is below.

**Verdict: the dry-run arithmetic in the claim is right, but the conclusion drawn from it is not.** In dry mode, 2900 frames over 120 s gives 24.2 Hz, and that is an artefact of the fixture. But T5 cannot tell whether the minimize wrapper is harmless, so "the real legs will pass T5" says nothing about whether the L-min leg is valid. The patch already in the file also removes the one thing the dry run could have checked.

## 1. Strongest reason the claim is wrong

**T5 cannot see the effect under test, so passing it tells you nothing about the real path.** In cycle 88, all three real legs read **89.0 Hz** while losing **3410, 3490 and 3776 frames** (`tools/bench/m8_kswap_88.json:53-54, 173-174, 293-294`). That is about a third of roughly 10,700 frames. `current image number` is therefore the camera's buffer counter, not the processing loop's count: it keeps rising at the camera rate however far tracking falls behind. The frames-per-second figure is `frames_delta / RUN_S` over that counter (`drive_m8.py:106-107`, `drive_m8_panelmin89.py:98`).

So if the minimize or restore wrapper, the second COM connection, or the UI-thread cost of the `FPState` writes slowed the experiment loop, T5 would still pass at about 89 Hz. The consequence shows up only in `lost_frames`, which is reported and never gated.

"The real legs will not fail T5" is probably true, but only because T5 is blind to this. It is not evidence that the wrapper leaves the experiment loop alone.

## 2. Alternative explanation of the same dry-run evidence

The same failure appears if `--run-s 120` never reaches `v5.RUN_S`. With the default 35 s, a real leg would give about 35 × 90 = 3150 frames, and 3150 / 120 = 26 Hz, which also fails T5. The "already ruled out" list cites M1..M8 and PM0, but **none of those gates depends on run_s**: M3 (≥ 2000 frames) passes at 35 s too.

Here is what actually rules this out:
- The json file the sequencer found is named `m8_s1_p15_r120_dry.json`, which only happens when drive_m8 parsed `--run-s` (`drive_m8.py:40`).
- `v5.RUN_S = RUN_S_ARG` runs unconditionally (`drive_m8.py:82`).

The dry run itself cannot show this, because `fake_leg` ignores `RUN_S` and its L11 text is hard-coded to "over 35s" (`m8_dry.py:28`). The fixture was sized for 35 s: 2900 / 35 = 82.9 Hz, which passes T5.

**The patch is already in place and is the weaker fix.** `drive_m8_panelmin89.py:108-109` now reads `DRY or …`, so T5 always passes in dry mode and can no longer catch a run_s plumbing regression. The better fix is to size the fixture from `v5.RUN_S`, for example `[100, 100 + int(90 * v5.RUN_S)]` in `m8_dry.py:29`. M3 still passes at 35 s (3150 frames). Also record `v5.RUN_S` in drive_m8's output json and divide by that value rather than by the sequencer's own constant.

## 3. What would falsify the claim

Either of these would:
- A real L-min leg whose L11 counter series is stalled or flat after the `FPState = 4` write, which the camera-counter reading says should not happen.
- A dry run with the fixture sized from `v5.RUN_S` that still gives a rate other than about 90 Hz, which would mean the rate is not coming from RUN_S at all.

## Problems in the leg wrapper that could make L-min unsafe or unmeasurable

- **The FPState enum values are correct.** NI's documentation gives 0 Invalid, 1 Standard, 2 Closed, 3 Hidden, 4 Minimized, 5 Maximized ([NI FPState (ActiveX)](https://www.ni.com/docs/en-CY/bundle/labview-api-ref/page/properties-and-methods/activex/vi/fpstate.html), [documentation.help mirror](https://documentation.help/NI-ActiveX-LabView/VI_FP_WinStateAX.html)). I could not fetch the page body; the values come from the search snippet.
- **The leg order is confounded.** L-min always runs first and L-ctl second. In cycle 88, lost frames rose with each leg (3410 → 3490 → 3776), and the two identical kswap legs differed by 80. With one leg of each type in a fixed order, "minimize reduces lost frames" cannot be separated from "later legs lose more". Use an ABBA order, or at least report the difference against the 80–370-frame spread.
- **`Total Lost Frames` is cumulative** from the start of the loop, read once at the end of L11 (`drive_original_copy_v5.py:465`). It includes the seconds before the minimize takes effect: the `open` call can take up to 60 s, plus a 1.5 s sleep. For the comparison, take lost frames as the difference across the L11 window instead.
- **The `cleanup` step calls the patched stop function again.** `cleanup()` calls `stop_with_fallback("cleanup")` by name (`drive_original_copy_v5.py:595`), which is now `restore_then_stop`. After `release`, `vi` is `None`, so the `set` raises and **PM4 is overwritten to FAIL** even when the restore before L12 succeeded. It also sends a second `release`. This happens only when L12 failed to stop the VI, but it records a failure in the wrong place.
- **PM3 passes on `None`** (`drive_m8_panelmin89_leg.py:96`). `win_rect` returns `None` whenever lv_gui throws, for example "No LabVIEW window whose title contains …" (`lv_gui.ps1:866`). So a title mismatch counts as "iconic or unlisted". A minimized window is still visible and `GetWindowRect` gives about -32000, so the ≤ -30000 test is sound. Treat `None` as FAIL unless PM2 read back 4.
- **A hung `MinCom` call leaves a COM reference open.** If `open` times out, the worker thread is still blocked inside LabVIEW holding `app`. The later `set` and `release` then queue behind it and each wait 15 s. That reference could stop LabVIEW exiting and force the kill path in G92 and M6.
- **Motor safety is not gated (in both sequencers).** The post-run `TMX? still 39` check (G93) is only listed in `v5_failing`. No T or M gate reads it, and `motor_tmx_after` is recorded but not checked. In this dry run G93 FAILED and every gate still passed. A real run where the controller limit was lost would also pass. Add a gate `motor_tmx_after == 39` whenever the run is not dry.
- **Timing is fine.** Cycle-88 legs took 418–419 s. The minimize adds at most about 65 s, well inside `LEG_MAX_MIN` of 12 minutes.

## 4. Cheapest discriminating test

This needs no LabVIEW. Change `m8_dry.fake_leg` so it writes `[100, 100 + int(90 * v5.RUN_S)]` and prints `v5.RUN_S`. Remove the `DRY or` from T5 and run `--dry` again.
- **Claim holds:** it prints `RUN_S=120.0`, and T5 PASSES at about 90 Hz.
- **Alternative holds:** it prints 35.0 or T5 still fails.

For the real-path question, which T5 cannot answer, the discriminator is in the real run's own data. Compare the L11 counter slope and the lost frames across the L11 window for L-min against L-ctl, with the leg order alternated.

**What I still hold:** the arithmetic is correct and the real legs will very probably pass T5. I do not accept that this makes T5 evidence that the leg is safe or measurable. If a real L-min leg's lost frames across L11 match L-ctl within the cycle-88 spread, the wrapper does not disturb the loop, and that would change my mind about the wrapper, not about T5.

## Sources

(extract from answer)

## What was done with it

Card 89-4 (material, fable/low), 2026-09-26 02:2x. ACCEPTED and applied, all script-level (no design change):
- `tools/bench/m8_dry.py:28-31` fixture sized from `v5.RUN_S` (`100 + int(90*RUN_S)`) and prints `DRY RUN_S=`; the `DRY or`
  exemption was REMOVED from T5 in `tools/bench/drive_m8_panelmin89.py` (the review's cheapest test, re-run dry).
- `drive_m8_panelmin89.py`: new per-leg gate `T10 motor TMX 39 after` (real runs only); leg order changed to ctl FIRST, min
  SECOND so that a collapse on the min leg cannot be cycle 88's "later legs lose more" order effect (ABBA not run: 2 legs
  per the brief; the 80-370-frame spread is reported beside the difference).
- `drive_m8_panelmin89_leg.py`: `restore_then_stop` runs once (cleanup's second call passes straight through, PM4 no longer
  overwritten); PM3 treats `None` from win_rect as FAIL unless PM2 read back 4; `Total Lost Frames` + `current image number`
  are read at the minimize point and at the restore point (`counters_at_minimize` / `counters_at_restore`) so the lost
  frames are differenced over the minimized window.
- NOT changed: FPState enum (review confirms 1 Standard / 4 Minimized); MinCom hang handling (a timed-out `open` is reported
  as PM1/PM2 FAIL and the leg's own M6 kill path covers LabVIEW exit).
