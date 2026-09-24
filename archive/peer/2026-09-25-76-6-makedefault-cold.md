# 76-6-makedefault-cold

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.3870  in 28 / out 14232 / cache-create 95566 / cache-read 1307684  (173s, 22 turn(s))
- **date:** 2026-09-25 05:31:43
- **outcome:** ANSWERED (175s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

Failed prediction, card 76-6 (LabVIEW 2026, VI Server over ActiveX from Python).

Claim under test: `tools/gscript.py` `make_default` (lines ~2985-3030) sets front-panel control values with
VirtualInstrument.SetControlValue, runs our op `OpMakeDefault_v0.vi` (VI method `Default Values:Make Current Default`,
3F3, on a VI reference opened by path), checks the op's error out (empty), then saves the VI (VirtualInstrument
SaveInstrument path), and reads every value back in memory after the save: all equal.

Prediction: after a LabVIEW restart (cold load of the saved file) every value equals what was set.
Observed (`tools/bench/selftest_make_default.log` lines 75-82, run 2): scratch VI = EMPTY_v0 copy + IMAQ Create +
IMAQ ImageToArray; controls created by `Terminal.Create Control` on 'Image Name', 'Border Size' (I32 scalar),
'Optional Rectangle' (I32 1-D array) and a free String[] 'Control Names' (made from Get Controls.vi's terminal,
then that subVI deleted). Values set: Border Size 3, Optional Rectangle [1,2,3,4], Control Names = 10044 path strings.
Cold read: Border Size 3 OK, Control Names 10044 OK, Optional Rectangle EMPTY (len 0).
Earlier (card 76-5, `tools/bench/replay_vis_76d_defaults.log`): the same function lost a String[] ['1'] and a DBL scalar
10044 but kept a 10044-element String[] - so the lost set is not simply "by type".

Already ruled out: op error out non-empty (checked, empty); in-memory values wrong after save (read back, equal);
the negative case (unknown label raises, it does).

Question: what makes one control's default not persist while others in the same VI, same call, do? Name the most likely
mechanism, one competing one, and the cheapest discriminating measurement we can run by VI Server scripting
(no GUI). Our own-tools claim involved: that SaveInstrument saves defaults set by Make Current Default on a
separately-opened reference in the same LabVIEW instance.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**The claim does not hold, and the two runs can't show where the defaults are lost.** The check that "passed" in `make_default` can never fail, and the one scalar that "persisted" tells us nothing.

## 1. Strongest reason the claim is wrong

**The check after the save reads current values, not defaults.** `_check("after save")` (`tools/gscript.py:3004-3020`) calls `GetControlValue`, which returns each control's current value. `SetControlValue` already put those values there at `gscript.py:3013`. So the check passes even if `Make Current Default` (3F3) did nothing and even if the save wrote no defaults. That "all equal" line is the only in-instance evidence for the claim, and it can't tell the two cases apart.

**Border Size 3 is IMAQ Create's own default.** NI documents the default border as 3 pixels ([IMAQ Create help](https://documentation.help/NI-Vision-LabView/IMAQ_Create.html)). `Create Control` on that terminal starts the new control at 3. Seeing 3 on the cold read therefore proves nothing about persistence.

**The real count across both runs is 1 of 5 informative values persisted:**

| run | value | kept? |
|---|---|---|
| 76-5 | String[] `['1']` | lost |
| 76-5 | String[] of 10,044 paths | **kept** |
| 76-5 | DBL 10044 | lost (read 0.0) |
| 76-6 | I32[] `[1,2,3,4]` | lost |
| 76-6 | String[] of 10,044 paths | **kept** |

Sources: `tools/bench/replay_vis_76d_defaults.log:4`, `tools/bench/selftest_make_default.log:81`.

## 2. What separates kept from lost, and competing explanations

What the data rules out as the separator:
- **Type.** In 76-5, `['1']` and the path list were both String[], built the same way (`str_array_ctl` twice, `tools/bench/diag_replay_standins.py:30`), and set in the same call. One was lost, one kept.
- **Order of setting.** The kept control was last in 76-6 and in the middle in 76-5 (`diag_replay_standins.py:84`).
- **Wiring.** The kept control was wired to Index Array in 76-5 and was free in 76-6. The lost ones were wired to a loop tunnel, Q&R `y`, and ImageToArray.

The only variable that matches all five is **data size**: the one 10,044-element value from `L.frame_paths()` was kept both times. Every small value was lost.

Two explanations fit the logs equally well:
- **H1 – the default was never set in memory for most controls.** 3F3 did not copy the values `SetControlValue` wrote into the default data. It applies to all controls on the panel ([NI: Make Current Default](https://www.ni.com/docs/en-ZW/bundle/labview-api-ref/page/properties-and-methods/vi-server/vi/makecurvaluedefault.html)). The front panel was not open at any point: `close_panel` raised "Cannot close … a closed front panel" (`selftest_make_default.log:83`). So the gap between the running values and what the panel holds is where I'd look first. I can't explain from the logs why the large array would escape this, so H1 is a hypothesis, not a diagnosis.
- **H2 – the default was set in memory, but lost when the file was saved or cold-loaded.** For example, a relink or reset on load. Nothing in either log rules this out.

A typedef reset on load is a weaker third candidate. The DBL `y` from Quotient & Remainder is not a typedef and was also lost, so it can't explain all five.

## 3. What would falsify the claim

The claim says `SaveInstrument` saves the defaults that 3F3 set. It is falsified if a value is confirmed as the in-memory default before the save and is still missing after a reload. The claim's own premise fails if the value is already missing from the in-memory defaults before the save; then the save is not at fault at all.

## 4. Cheapest test that separates H1 from H2 (VI Server only, no restart)

On a fresh scratch VI, in one LabVIEW instance:

1. Set these values, then run `make_default`:
   - Border Size **5**, not 3, so the scalar actually tests something.
   - String[] of lengths 1, 100 and 10,044.
   - I32[] of lengths 4 and 10,044.
2. **Before saving**, set every control to a sentinel value with `SetControlValue`.
3. Call ActiveX `VirtualInstrument.ReinitializeAllToDefault` ([NI VI methods (ActiveX)](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/activex/vi-p.html), [labviewwiki](https://labviewwiki.org/wiki/VI_class/Default_Values.Reinitialize_All_To_Default_method)). Then `GetControlValue` each control. This reads the defaults held in memory.
   - A value missing here means **H1**: the save is not involved.
   - All values present here means go to step 4.
4. Save, reload from disk in the same instance (the "revert" step already in `build_opmakedefault.py:8`), and read again. A value missing only now means **H2**.
5. Repeat with the front panel opened (`OpenFrontPanel`) before step 1. If small values then persist, the closed front panel was the cause.

**The size sweep also tests the size pattern directly.** If only the 10,044-element arrays persist in step 3, size (or a side effect of a large COM transfer) is the variable.

**One unverified precondition:** the project has recorded `MakeCurValsDefault` as missing from the ActiveX interface (`docs/NAMES.md:570`). `ReinitializeAllToDefault` is a separate method in NI's ActiveX listing, but nobody has called it here yet. Probe it once before relying on it; a `DISP_E_UNKNOWNNAME` error means it needs an op, like 3F3 did.

**A fix owed whatever the test shows:** the check after the save in `make_default` should read values after resetting to defaults, not current values. As written, it can't catch the failure it was added for.

Sources:
- [NI – Default Values:Make Current Default](https://www.ni.com/docs/en-ZW/bundle/labview-api-ref/page/properties-and-methods/vi-server/vi/makecurvaluedefault.html)
- [NI – Default Values:Reinitialize All To Default](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/vi/reinitializealltodefault.html)
- [NI – VI Properties and Methods (ActiveX)](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/activex/vi-p.html)
- [labviewwiki – Reinitialize All To Default method](https://labviewwiki.org/wiki/VI_class/Default_Values.Reinitialize_All_To_Default_method)
- [IMAQ Create help (default border = 3)](https://documentation.help/NI-Vision-LabView/IMAQ_Create.html)

## Sources

(extract from answer)

## What was done with it

(pasted verbatim by material session 77-1 from tools/bench/cards/disposition_76-6-makedefault.md)

Material session 76-6, 2026-09-25 05:3x. ACCEPTED as the framing: (1) the after-save `_check` in `gscript.make_default`
reads CURRENT values and cannot catch a lost default - acknowledged, the S2 PASS in `tools/bench/selftest_make_default.log`
is therefore uninformative; only S3 (cold read) counts, and it FAILED 2/3 with Border Size 3 == IMAQ Create's own default,
so the informative count is 1 persisted of 2 (10,044-element String[] kept, I32[4] lost). (2) H1 (Make Current Default
did not copy the values; front panel closed) vs H2 (lost on save/load) is NOT yet discriminated. No further LabVIEW run
in card 76-6: the self-test's failure budget of 2 is spent (run 1 our-script-bug, IMAQ Create 'Image Name' required;
run 2 this finding). The prescribed test (Border Size 5, String[]/I32[] size sweep, sentinel + ReinitializeAllToDefault
before save, then save + reload, then with the panel open; probe ReinitializeAllToDefault on ActiveX first) is handed to
the judgement session as the next card; the stand-ins were NOT rebuilt.
