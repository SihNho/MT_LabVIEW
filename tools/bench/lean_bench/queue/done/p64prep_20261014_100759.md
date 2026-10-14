# Lean task 6: P6-4 PREPARATION - the real-bead ABBA plan, read and plan only (no LabVIEW, no motor, no rig)
One session, <= 180 min, <= $60. User 2026-10-14 05:1x "동의" to "P6-4 (실제 비드 ABBA) 준비를 시작할까요?" - the
PREPARATION is approved; the real bead run waits for the user at the rig (see `user_notes.md`).

Read `CLAUDE.md` (the lean rules), `user_notes.md`, then `lean_report_p6close.md` section 14 (the P6-4 facts and the
items marked "not in the files"), `lean_report_latest_*.md` / `lean_report_latest.md`, and the sources section 14 cites
(main checkout `../V6_ParallelLoop/`: `docs/d1/ring-p6.md`, `docs/d1/ring-p6b.md`, `docs/d1-loop12-17-split-plan.md`
around PD217/PD238, `docs/camera-acquisition-facts.md`, `docs/m8-real-run-plan.md`, `docs/user-rules.md`; this worktree:
`tools/bench/diag_c104_abba.py`, `tools/bench/drive_m8.py`, `tools/bench/drive_original_copy_v5.py`).
**Start condition:** `lean_report_p6close.md` exists and its RESULT says `"p6close": "PASS"`. Otherwise write
`lean_report_p64prep.md` saying why and end with `RESULT {"p64prep": "NOT-STARTED", ...}`.

## Do (reading and writing plain files only)
1. For EVERY item section 14 marks "not in the files", either find the answer in the files (cite file:line, re-read it
   yourself) or turn it into ONE question for the user, marked `HOLD:` (needs the user's decision or the rig) or
   `ASSUME:` (a method choice inside the rules - state the assumption you would take). At least these:
   a. the P6-4 pass criterion, written BEFORE any run (lost frames A vs B, and acceptance #1 on a live run);
   b. how acceptance #1 (every saved row's buffer number is its own frame's) can be checked on a LIVE run, where there is
      no S1 column 0 to compare with (e.g. from the camera's own frame counter / image metadata saved with the row) -
      design the check and say what extra the VI or the driver would have to save, without editing anything;
   c. how the final VI 15c664e3 would run at 150 Hz (the .icd reload resets the rate to 90 Hz on every camera open);
   d. whether the panel's magnet controls move anything during an ABBA leg;
   e. bead preparation, focus, and machine picks vs aimed picks.
2. Write the P6-4 run plan `tools/bench/lean_bench/p64_plan.md`: legs (A B B A per rate), VIs (byte copies only), driver
   and its changes if any (described, not made), durations, every motor move per leg (v5 G0 per-leg session start is
   approved; the queue's cycle hooks stay), what the user does at the rig and when, the stop conditions, the predictions
   for each leg, and the acceptance in its final words.
3. List the user questions from step 1 at the end of the plan AND append each as one line to `questions_for_user.md`.

Do NOT open LabVIEW, run any leg or driver, call `tools/motor_gate.py`, or touch the rig or camera. Do NOT edit any .vi,
`tools/hooks/**`, `tools/motor_gate.py`, `tools/bench/motor_limits.json` or `CLAUDE.md`. Write only under
`tools/bench/lean_bench/`. Do not commit.

## Report `tools/bench/lean_bench/lean_report_p64prep.md`
What was read, each section-14 open item -> answer (file:line) or question (HOLD/ASSUME), the plan's path, then
`RESULT {"p64prep": "PASS|FAIL|INCOMPLETE|NOT-STARTED", "answered": N, "questions": {"hold": N, "assume": N}, "plan": "<path>", "minutes": N}`.
PASS = every open item is answered with a citation or turned into a question, and `p64_plan.md` is complete.
