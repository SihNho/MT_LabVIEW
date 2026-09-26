# c92-unstamped-clickprobe

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.5374  in 24 / out 12910 / cache-create 129412 / cache-read 1218836  (163s, 20 turn(s))
- **date:** 2026-09-26 08:30:54
- **outcome:** ANSWERED (167s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim (card 92-1, log tools/bench/m8_unstamped8_92.log, scripts tools/bench/diag_c92_m2.py and tools/bench/diag_c92_unstamped_leg.py):

CLAIM: The only failure in m8_unstamped8_92.log (T1 leg rc 0 FAIL on both attempts, and every gate downstream of it: T3/T5/T10/T12) is OUR OWN SCRIPT BUG in the new wrapper diag_c92_unstamped_leg.py, not a harness, LabVIEW, camera or motor fault, and the measurement is simply not yet taken.
Evidence: the leg's stderr (m8_unstamped8_92.log:7-16) ends in `ValueError: too many values to unpack (expected 2)` at diag_c92_unstamped_leg.py:50 `j, raw = real_probe(title, x, y, why)` - the wrapper was written against d0_clickprobe.clickprobe (returns `(obj, out)`, tools/bench/d0_clickprobe.py:67-86) but the name it wraps, `d4.clickprobe` = drive_original_copy_v4.clickprobe, returns the dict alone (tools/bench/drive_original_copy_v4.py:447-465). The exception fires at the FIRST pick click (drive_original_copy_v5.py:319 probe_click), after "=== D0 v5: 15 pass, 0 fail ===" i.e. after the motor-gate session, LabVIEW launch, copy load, run start and the pre-pick steps all passed; both attempts (a1 429 s, a2 425 s) died at the same line. The pre-launch reader gates R1/R2/R3 passed; T2/T4/T6/T7/T8 (LabVIEW gone before/after, camera 90 Hz before/after, md5 pins) passed on both attempts, so nothing on the machine changed. The fix (already applied): `j = real_probe(...)` and `return j`; the sequencer now also refuses to RERUN a leg that crashed before reading the tra (a crash is not a lost pick), which cost 7 min on attempt 2.

ALREADY RULED OUT: (1) a modified VI - T8 md5 pins hold for S1 (3e3d23ce...), t0, kswap, bed; (2) a stalled LabVIEW - T6 gone after both legs without taskkill; (3) a camera-rate fault - 90.0 before, 90.0009 after, restored to 90 (T7).

Questions: (a) the strongest reason the claim is wrong - could the unpack error be masking a DIFFERENT first fault (e.g. the pick click never delivered, so real_probe returned something else)? (b) an alternative explanation of the same two identical 425-429 s deaths; (c) what would falsify "script only"; (d) the cheapest discriminating test before the rerun - and whether wrapping d4.clickprobe (called from v5.probe_click at :185) can change the pick-click behaviour itself (timing between clicks, the delivered verdict), which would contaminate the very frame-loss/first-click-capture comparison this leg exists to make.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict: the crash cause is right, but the claim is wrong in two places.** The unpack error is our script bug, and it hides no earlier click fault. The claim is wrong, though, that nothing else happened on the machine, and wrong that nothing was measured.

**1. Strongest reason the claim is wrong: ruled-out item (2) is false.** LabVIEW did not exit cleanly. It was force-killed inside the leg, by v5's own cleanup, so the sequencer's taskkill never had anything left to do.
- `m8_v5_replay_s1_p8_r120.json:103`: `"waited 251s; forced kill used=True"`.
- `m8_v5_replay_s1_p8_r120.json:279-280`: the stop needed `"COM Abort (VI SERVER DID NOT STOP IT)"`, taking 95.9 s.
- The exception passed through `v5.main`'s `finally` into `cleanup()` (`drive_original_copy_v5.py:571-573`). The chain was: try the VI Server stop, give up, COM Abort, wait `EXIT_WAIT_S`=240 s (`:161`, `:641`), then `Stop-Process -Force` (`:644-648`).
- T6 in `diag_c92_m2.py:104-107` only checks whether *its own* taskkill ran, so it cannot see this.
- The `=== D0 v5: 15 pass, 0 fail ===` line does not show "the pre-pick steps passed before the crash". `report()` prints it inside the `finally`, after the crash. Its 15 steps are 11 pre-pick steps plus the 4 cleanup steps G90–G93, and "0 fail" is only because L3 onward were never recorded (json `:9-109`).

This is probably benign: the VI was sitting in the bead-picking loop, which likely does not read the stop booleans, and after an Abort the VI never runs its own shutdown. By comparison, the stamped INDEX-51 leg stopped by one VI Server write (`t0_legs/step4_20260926_071816/leg2_ctl_p8_a1/leg.json:192`). But "benign" is my inference, not a measurement. What the log does show is that each attempt ended with an abort and a hard kill, with the camera's acquisition session presumably never closed by the VI. The camera read 90.0009 Hz afterwards, so it was not visibly harmed.

**2. Alternative explanation of the two identical 425–429 s deaths.** They are not "death at a line after ~425 s". The crash came early, at the first bead click, 08:20:33 on attempt 2 (`_clicks.json:11`). Most of the remaining time was fixed cleanup timeouts: about 96 s for stop and Abort, plus 251 s waiting before the kill. Deterministic timeouts are enough to explain the equal durations. Equal durations say nothing either way about whether the machine behaved identically.

**3. Does the unpack error mask a different first fault? No.** Checked on the machine's record:
- The Python message itself narrows the return value. `None` would raise `cannot unpack non-iterable NoneType object`. A 2-key dict would unpack silently. `too many values to unpack (expected 2)` means a dict with 3 or more keys, i.e. clickprobe's JSON parsed.
- The one surviving record, attempt 2 (`m8_v5_replay_s1_p8_r120_clicks.json`), passes all four delivery checks: `setforegroundwindow.ret` true (:48), `fg_after_sfw_is_target` (:55), `wfp_press_xy.root_is_target` (:74), `fg_at_buttondown_is_target` (:91). By `d4.delivered` (`drive_original_copy_v4.py:467-474`), the first pick was delivered.
- Attempt 1's record was overwritten, because both attempts share the same `PROBE_JSON` path (`drive_m8.py:81`). For attempt 1, only the identical error text supports "dict returned". Its delivery verdict is not recoverable.

**4. What would falsify "script only".** Any one of these, on the fixed rerun:
- a pick click whose `delivered()` is false;
- `cleanup_stop` or a forced kill appearing even though the experiment loop was reached (L7/L9/L11 pass);
- G93 TMX ≠ 39;
- a new exception anywhere past L3.

**5. "The measurement is not yet taken" is also partly wrong.** The first-click capture read the leg exists for was already recorded, for attempt 2's first click. `hwndCapture` was 24840136 (non-zero) at `gti_before_focus` and `gti_before_click` (`_clicks.json:42`, `:82`), and 0 after the click (`:99`). So the unstamped copy also shows a non-zero capture window before the first pick. That should be reported, not thrown away with the failed run. Frame loss was not measured.

**6. Can the wrapper change the clicks it is measuring? Very unlikely.**
- `probe_with_class` only runs after `real_probe` returns, so it cannot touch that click's before/at-click state.
- Its extra work is 3 × (`IsWindow`, `GetClassNameW`, `GetWindowTextW`, `GetWindowThreadProcessId`) plus one print: sub-millisecond next to `PICK_SETTLE`.
- `GetWindowTextW` on a window owned by another process reads the caption directly, with no `WM_GETTEXT`, so it cannot block on a busy LabVIEW (https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowtextw, Remarks).
- The patch reaches every click path: v5 calls `d4.clickprobe` through the module attribute (`v5.py:185`), and `gated_click_hwnd` looks up the module global (`v4.py:486`).
- One caveat about meaning: `capture_win` is read *after* the click, when capture is already 0. The class/title it reports describes the window at read time, not at click time. If `alive` is false, or if handle 24840136 has been reused, that attribution is wrong.

**7. Cheapest discriminating test (no LabVIEW).** Run the fixed wrapper once with its `d4.clickprobe` stubbed to return the saved attempt-2 `json` dict. Confirm that:
- `probe_with_class` returns that same dict;
- `d4.delivered(j)` still gives all four true;
- `FACTS["clicks"][0]["gti_before_click"]["hwndCapture"] == 24840136`.

This proves the fix changes the plumbing and not the verdict. It is effectively what the `--dry` path should have caught: `diag_c92_m2.py:93-94` bypasses the wrapper entirely, which is why a dry run passed and the real run did not. Then on the rerun, add one assertion to the prediction contract: `cleanup_stop` absent, or G92 forced-kill false, whenever L11 is reached. That separates "a crash left the VI in the picking loop" (expected Abort and kill) from "LabVIEW does not stop by the VI's own control on the unstamped copy" (a real fault).

**Minor:** `diag_c92_unstamped_leg.py:68-69` reads the shared `m8_replay_s1_p8_r120.json` without checking that it is fresh, and that file currently holds the cycle-91 data. It is safe today only because `drive_m8.main` always writes the file when it returns. Checking `m8["run_dir"]`'s timestamp against the leg's start time would close the gap.

**What would change my mind to "script only, clean":** on the fixed rerun, an experiment-loop leg that stops through VI Server (`mechanism` starting with `VI SERVER`), with `forced kill used=False` and TMX 39.

## Sources

(extract from answer)

## What was done with it

Card 92-1 material session (fable/low), 2026-09-26 08:3x. Jev ladder: `new-problem p=0.750` -> review owed (old path), this
review bought.
- §1 ACCEPTED as a fact: "LabVIEW gone after" was v5's own forced kill (`m8_v5_replay_s1_p8_r120.json:103`), not a clean
  exit; the sequencer's T6 cannot see that. My ruled-out item (2) is withdrawn. The rerun's M4 (`mechanism` starts
  `VI SERVER`) is the gate that separates a crash-left-in-picking-loop from a real stop fault, as §7 asks.
- §3 ACCEPTED: the unpack error masks no earlier click fault (the error text implies a parsed dict; attempt 2's record
  passes all four delivery checks).
- §5 ACCEPTED and REPORTED: attempt 2's first pick click on the UNSTAMPED copy had hwndCapture 24840136 (non-zero) at
  `gti_before_focus` and `gti_before_click`, 0 after the click (`m8_v5_replay_s1_p8_r120_clicks.json:42,82,99`) - kept as
  a fact in result_92-1.json. Its window CLASS was not read (the wrapper died before its read).
- §6 caveat ACCEPTED as a limit of the read: `capture_win` is read AFTER `real_probe` returns (~0.6 s after the click); the
  class/title describe the window at read time and `alive` is recorded; a dead or reused handle is reported as such.
- §7 test (stub run) NOT run - the fix is the one-line unpack (`j = real_probe(...)`), and the rerun itself is the test;
  the 'Minor' freshness check IS applied (`diag_c92_unstamped_leg.py`: the shared m8 json is used only when its mtime is
  after the leg start). The sequencer also no longer reruns a leg that crashed before reading the tra.
- Not applied (judgement): the review's note that `--dry` bypasses the wrapper (`diag_c92_m2.py:93-94`) - a dry-run
  design change for the harness.

SAME-ROW: m8_unstamped8_92b.log (2026-09-26 08:52:27)
  This later failure of the SAME script was released without buying a new peer review: one review per row per cycle (CLAUDE.md, user 2026-09-22). The review above is the evidence; this line records which re-run was charged to it.
