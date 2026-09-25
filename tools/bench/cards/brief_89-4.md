# Brief 89-4 (cycle 89 judgement): display lever first, then the profiler legs

Decisions on result 89-3 (PASS; plan `tools/bench/profiler_run_plan_89.md`, review
`archive/peer/2026-09-26-c89-profiler-plan-hyp.md`):
- **ACCEPTED: the review's cheaper discriminating leg runs FIRST** (plan §6 A2). No VI is edited and nothing is
  built. The only question is whether the front panel drawing is the per-frame lever.
- **ACCEPTED: amendments A1 and A3** for the profiler legs. A1 is an idle GUI+COM liveness test (30 s, no leg). A3 is
  Timing details ON, time unit µs, Snapshot+Save at L10 AND after L12, then the difference; the 8-pick leg goes first.
  Apply them in the plan file before its legs. Also accepted: inline top-level code is ONE row. That is reported as it
  is, not treated as a failure.
- **Deferred:** the CLFN/C-DLL stamp route (open 3 of 89-3). It is not built in this cycle.

## Part 1: panel legs (real hardware, rig 조립, 2026-09-24 motor grant; VI = unmodified `D1_s1_copy.vi`)
The `drive_m8_load83.py` pattern, 120 s, 90 Hz, 15 picks:
- **L-min:** after bead picking and the done button (i.e. when the experiment loop starts), MINIMIZE the front panel
  through COM (FPState or the equivalent scripted property; no click). Keep it minimized until the leg's timed stop,
  then restore it for the stop/save steps if the driver needs that.
- **L-ctl:** the same leg with the panel left as the driver leaves it. This is the same-session control.
- Per leg: Total Lost Frames, frames acquired, actual rate. LabVIEW gone after each leg.
- If the scripted minimize is unreachable, record it with evidence, skip L-min, and continue to Part 2. Do not
  substitute a GUI click that is not in a reviewed plan.

## Part 2: profiler legs, per `profiler_run_plan_89.md` with A1 and A3 applied
Run the liveness test A1 first. Then the 8-pick leg, then the 15-pick leg, on unmodified `D1_s1_copy.vi`. Each GUI act
goes through `lv_gui.ps1 -Exception NegativeSearch -Evidence tools/bench/diag_c89_profiler_search.md`, as capture → locate
→ act → capture → confirm. A failed prediction triggers RECOVERY_LOCKED (CLAUDE.md §3): diagnostics only, then stop
and report.

## Output
`tools/bench/t0_insitu_89.json` holds:
- the L-min and L-ctl lost frames;
- per profiler leg, the profile table: per subVI VI time, # runs and average in µs, with the L10→L12 difference;
- lost frames per profiler leg.

Report the 15−8 difference per group as measured numbers. Do not recommend a design.

## Close
The md5s of `D1_s1_copy.vi`, the kswap VI and the L2-A1 bed are unchanged, and LabVIEW is gone.
