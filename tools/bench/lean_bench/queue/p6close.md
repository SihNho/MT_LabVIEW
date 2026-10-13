# Lean task 5: close P6 - one final VI, every acceptance re-run on it, and what P6-4 (real beads) needs
One session, <= 180 min, <= $60. Real project work (chat 2026-10-13, from the plan: PD404 rows P6-2/P6-3 done by lean
tasks, P6-4 needs beads and the user's word first). Written by the chat ahead of time so the queue keeps running; the user
may delete this file from queue/ before it starts.

Read `CLAUDE.md` (the lean rules), then `lean_report_p6fix.md` and `lean_report_latest.md` (the two tasks before this one).
**Start condition:** both reports exist and their RESULT lines say `"p6fix": "PASS"` and `"latest": "PASS"`. Otherwise do
nothing in LabVIEW: write `lean_report_p6close.md` saying why and end with `RESULT {"p6close": "NOT-STARTED", ...}`.

## Do
1. Name the ONE P6 VI that carries both fixes (the `latest` result, path + md5) - read-only; make copies.
   Re-hash every input the earlier reports name; any drift is reported and stops the task.
2. Write predictions BEFORE any LabVIEW run (from the two reports' numbers).
3. Re-run, on fresh byte copies of that VI and with the routes the earlier reports used:
   P6-2 replay (normal), gap, W40, W100 - one LabVIEW run at a time, motor sessions with readback, LabVIEW gone after each.
4. Per condition, in one table: rows, own-buffer-number rows / total (acceptance #1, user 2026-10-13), X/Y/Z bit-identical
   rows vs S1, lost, damaged, strictly ordered, W100 lag, cal outside the date field, trans/rot post-init.
5. Read-only facts for P6-4 (real ABBA with beads, NOT run here - the user is asked first): which VI, which legs, how long,
   which motor moves, what the user must do at the rig. Write them as a short list for the chat to put to the user.

Do NOT build or save a new VI in this task (only byte copies for runs, under `claudeDev\bench\lean\`). Do NOT edit
`tools/hooks/**`, `tools/motor_gate.py`, `tools/bench/motor_limits.json` or `CLAUDE.md`. Do not commit.

## Report `tools/bench/lean_bench/lean_report_p6close.md`
Predictions (first), timeline, the VI (path, md5), the table vs predictions, motor readback lines, LabVIEW-gone, input md5s
start vs end, the P6-4 facts list, then
`RESULT {"p6close": "PASS|FAIL|INCOMPLETE|NOT-STARTED", "vi_md5": "...", "own_number": {...}, "minutes": N}`.
