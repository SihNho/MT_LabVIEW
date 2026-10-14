# Lean task: P6-4 day, step 1 - snapshot -> bead map at 90 Hz (camera only; nothing moves; LabVIEW stays closed)
One session, <= 30 min, <= $10. HELD in `hold/` - the chat moves it into `queue/` ONLY when the user is at the rig and says
the sample is in and focused ("준비됨"). User 2026-10-15: the beads already in the channel (magnetic beads left from the
experiment) may be used; P6-4 is a code check, not measurement automation.

Read `CLAUDE.md`, `user_notes.md`, `p64_rigday_checklist.md` (sections A-B), `lean_report_p64p3.md` (the bead-map picker).
**Start condition:** `lean_report_p64ready.md` RESULT says `"p64ready": "PASS"`; no LabVIEW process (`tasklist`); no STOP.
Otherwise write `lean_report_p64snap90.md` saying why and end with `RESULT {"p64snap90": "NOT-STARTED", ...}`.

## Do (checklist steps 3-4 only)
1. `p64_beadmap.py snap` twice ~5 s apart -> `out_p64/snap_90_1.tif`, `out_p64/snap_90_2.tif` (camera only, LabVIEW closed).
2. `p64_beadmap.py find` -> `out_p64/beadmap_90.json` + `out_p64/beadmap_90.png`. Report N (single, round, isolated,
   non-drifting beads); picks = the N best (max 15), then make up 15: by REPEATING clicks on real beads (user 2026-10-14 "같은
   비드에 여러번 클릭해도 되긴 하니") if the picker supports it, else the fixed empty-field fill - say which.
3. Do NOT run any leg, any VI, `--live`, or `--move-stale`. Do NOT touch a motor. LabVIEW count 0 at the start and the end.

## Report `tools/bench/lean_bench/lean_report_p64snap90.md`
N, the 15 picks (fractions, bead or fill/repeat), the PNG path, then
`RESULT {"p64snap90": "PASS|FAIL|NOT-STARTED", "n_beads": N, "png": "out_p64/beadmap_90.png", "minutes": N}`.
The chat shows the PNG to the user; `p64run90` waits for the user's OK on it.
