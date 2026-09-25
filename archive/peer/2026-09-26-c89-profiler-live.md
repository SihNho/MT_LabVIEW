# c89-profiler-live

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.3855  in 30 / out 12072 / cache-create 98292 / cache-read 1510186  (165s, 22 turn(s))
- **date:** 2026-09-26 02:41:17
- **outcome:** ANSWERED (169s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about the failed prediction in tools/bench/diag_c89_profiler_live.log (script tools/bench/diag_c89_profiler_leg.py --liveness, card tools/bench/cards/task_89-4.json Part 2 amendment A1, plan tools/bench/profiler_run_plan_89.md).

WHAT HAPPENED (log lines 8-27): the menu path Tools -> Profile -> Performance and Memory... was located by OCR on each capture and clicked; the `Profile Performance and Memory` window was listed (PF1 PASS). Inside it the OCR rows were: 'Profile Performance and Memory', ' Profile memory usage', 'Timing statistics', 'Application Instances', ' Timing details', 'Memory usage', 'Time unit', 'Size unit', 'kilobytes', 'milliseconds', 'Select Application Instances..', 'Profile Data'. Then: (a) the regexes `^Timing details` / `^Profile memory usage` did NOT match because the OCR text carries a LEADING SPACE; (b) the Time-unit regex `^(µs|us|ms|s|...)` matched 'Size unit' (the `s` alternative), so the script clicked the 'Size unit' LABEL at (803,449) - a no-op - then found no 'us' item and sent `key esc`; (c) the next `shotwin -Title 'Profile Performance and Memory'` returned nothing and the script returned False with an EMPTY locked list, so the Start button was never located and the run ended rc=1 with PF6/PF7 PASS (LabVIEW closed, copy deleted, S1 md5 unchanged).

CLAIM: the failure is ENTIRELY our script's: (1) the leading-space regexes and the wrong unit regex are OCR-handling bugs; (2) the Profile window CLOSED because the script sent Esc while that window was foreground (LabVIEW tool dialogs such as the Error List close on Esc - tools/lv_gui.ps1:729-731 says so for the Error List; `focus` also taps Esc), which is why shotwin found no window afterwards; (3) therefore the fixed script (regexes `^\s*Timing details` etc., unit located by its VALUE word 'milliseconds' then the 'microseconds' item, `activate` instead of `focus` for the Profile window, no Esc while it is foreground, an explicit log line when shotwin fails) will pass the liveness test - Start clicked, a `Stop` label visible, COM ExecState/SetControlValue round trip inside 10 s, Snapshot, Save to a typed absolute path, header containing `VI Time`.

Questions: (1) strongest reason the claim is wrong - in particular, is there another reason the window disappeared (e.g. the click on 'Size unit' opened a ring dropdown that the Esc then closed, leaving the window in place but with a changed title; or the window is a floating/tool window that lv_gui's Find does not list after it loses focus)? (2) alternative explanation; (3) what would falsify it; (4) the cheapest discriminating test. Also: in LabVIEW 2026's Profile Performance and Memory window, is `Start` a button that relabels to `Stop`; does Save open a standard Windows file dialog whose file-name field takes keyboard input; and does the window close on Esc?


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict: the claim about why the window disappeared holds up. The prediction that the fixed script will pass does not.** The run's own captures show two more defects, and one of them silently defeats amendment A3. One of the planned fixes also brings back the exact Esc failure the claim blames.

**1. The strongest reason the claim is wrong: the checkbox reader, not the regex, is the A3 failure, and the fix does not touch it.**
- `m8_shots/20260926_023542_prof_live_unit_menu.png` shows all four boxes in the Profile window **unchecked**, including "Timing statistics".
- Yet `profile_89_live_20260926_023542.json:27-28` records `chk_timing_stat_before: 0.132` → `chk_timing_stat_ok: true`. The threshold is `d_before > 0.12` (`diag_c89_profiler_leg.py:114`), so an empty enabled box read as ON and was never clicked. That 0.132 is the box border plus part of the glyph. The only 0.0 was the greyed, disabled "Memory usage" box.
- With the fixed regex, `^\s*Timing details` will now match. Its box, drawn the same way, will read about 0.13 → "on" → no click.
- **Result:** Timing statistics and Timing details both stay OFF, and every gate still passes. PF4 only checks for `VI Time`, and the capture shows the columns `VI Time / Sub VIs Time / Total Time` present with every box off. The liveness run would "pass" while A3 is not met.

**2. A defect the fix keeps, of the same kind the claim describes: `snapshot_and_save` line 169 calls `d0.focus(title)` on the Save file dialog.**
- `d0` is `drive_original_copy_v2` (v5 → v4 → v2), and its `focus` is `lv_gui focus` = Alt tap + **Esc tap** (`lv_gui.ps1:243-252`).
- Esc in a Windows common file dialog means Cancel. So the dialog is likely dismissed before `^a`, the path and `{ENTER}` are typed. Those keystrokes then land on the Profile window, where Enter may press its default button (Start/Stop or Close).
- Line 174 does the same thing again on the "stuck" path. The comment at line 154 applies to line 169 too.

**3. The alternative explanations for the missing window, tested against the machine record:**
- **"A dropdown opened, and Esc closed only the dropdown":** refuted. The capture about 1 s after the click at (803,449) shows no dropdown. That point is on the "Size unit" label, and the Size unit ring is greyed/disabled anyway.
- **"The window lost focus and lv_gui can no longer list it":** refuted. `Find` enumerates every visible top-level window of the LabVIEW process, whatever has focus (`lv_gui.ps1:219-223`). The final `dialogs` output (`profile_89_live…json:34`) lists only the Front Panel and `LabVIEW 0,0,0,0`. `…_locked.png` shows no Profile window anywhere on screen.
- **The window really closed.** The capture also shows it has a **Close** button, and Windows dialogs normally map Esc to their Close/Cancel button. So part (2) of the claim is well supported: 1.7 s between "locate us item" and RECOVERY_LOCKED fits esc + a failed `shotwin`.
- **Caveat:** the original script text was overwritten, and the run never logged the Esc or the failed `shotwin` (the fix only now adds that log line). "Esc closed it" is therefore strongly supported, not directly observed.
- NI's documentation does not say whether this window closes on Esc; I found no source either way.

**4. The fix's time-unit branch leaves a dropdown open when nothing matches.**
- If the list has no `microseconds` item (NI's docs don't list the ring's values), line 137 does nothing.
- The first click on Start is then spent closing the dropdown. PF2 would fail with a misleading cause.

**Your LabVIEW questions:**
- **Start → Stop:** NI's and third-party guides describe separate Start, Snapshot and Stop steps, with Save afterwards ([NI: Using the Profile window](https://www.ni.com/docs/en-US/bundle/labview/page/using-the-profile-performance-and-memory-window.html), [OpenStax lab](https://www.jobilize.com/course/section/profile-tool-lab-1-introduction-to-labview-by-openstax)). The capture shows only Start/Snapshot/Save/Close/Help, so Stop is the Start button's relabel. That fits, but no source I found states it outright.
- **Save:** writes a **tab-delimited text file** ([LAVA: LabVIEW Performance and Memory Management](https://lavag.org/old_files/post-705-1100237457.pdf)). Save is greyed until a Snapshot exists, as the capture shows. Whether the dialog is the native Windows one depends on LabVIEW's native-file-dialog option; I found no source for 2026.
- **Close on Esc:** not documented. The local evidence (see 3) says yes.

**What would falsify the claim:** a fixed-script run that reaches `Stop` and saves a file, but where `pJ1.png` shows no file dialog, or the saved header lacks timing-statistics columns. Either would show the run failing on the defects above rather than on the regex/Esc bugs.

**The cheapest discriminating test, offline and free:** run `box_dark` on the existing `…_chk_timing_det.png` at the fixed regex's hit. If it returns > 0.12 for a box the capture shows empty, points 1 and 2 of this reply are confirmed before any LabVIEW run. Then, before the next live run:
- replace `d0.focus` at lines 169 and 174 with `activate`;
- check each box's state by comparing it against a known-checked template, and require a visible change after every click;
- add `timing_stat` and `timing_det` ON as gates, not optional facts.

## Sources

(extract from answer)

## What was done with it

Card 89-4 (material, fable/low), 2026-09-26 02:4x. ACCEPTED, applied in `tools/bench/diag_c89_profiler_leg.py` before the
second liveness run (`tools/bench/diag_c89_profiler_live2.log`):
- §1 checkbox reader: no absolute threshold any more - a want-ON box is CLICKED and its state decided by the CHANGE of the
  interior dark fraction (rose = ON; fell = it was ON, click again and require a rise; no change = click missed -> FAIL);
  `PF8 timing_stat ON` / `PF8 timing_det ON` are GATES (A3), memory boxes are recorded and never clicked.
- §2 `d0.focus` on the Save file dialog replaced by a NegativeSearch-logged `activate` (both the typing path and the stuck path).
- §4 time-unit branch: when no `microseconds` item is found the ring is clicked AGAIN at the same point (closes the dropdown on
  its current item); no Esc is ever sent while the Profile window is foreground.
- Kept as facts: Start relabels to Stop (PF2 tests it); Save writes tab-delimited text (PF4 tests the header); close-on-Esc is
  recorded as "strongly supported, not directly observed" (this script never sends Esc to that window again).

SAME-ROW: diag_c89_profiler_live2.log (2026-09-26 02:44:32)
  This later failure of the SAME script was released without buying a new peer review: one review per row per cycle (CLAUDE.md, user 2026-09-22). The review above is the evidence; this line records which re-run was charged to it.
