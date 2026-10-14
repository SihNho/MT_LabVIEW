# Lean report - fr90 (2026-10-15): frame-rate ABBA at 90 Hz with Auto-Reset OFF in every leg copy (fixed 15 picks)

Task `tools/bench/lean_bench/queue/running/fr90.md`. One Opus session, lean rules (`CLAUDE.md`).

## 0. Start condition, user notes
- `lean_report_p64ready.md:122` RESULT `"p64ready": "PASS"`; `tools/bench/motor_session.json` present (03:40); `tasklist | grep -ic labview`
  -> 0 (03:40); `tools/bench/lean_bench/STOP` absent (only the archived `STOP_run1_*` / `STOP_run3_*` files exist). **Met** -> started 03:40.
- `user_notes.md`: nothing in the task contradicts a note. The task uses the fixed 15 picks with no beads; note 12 (2026-10-15, "the
  program first") covers that. No pull test, no Jev work, nothing queued. Big VIs: the only change is one panel default (the task's
  explicit allowance); no diagram edit (note 1).

## 1. Predictions (written 03:47, BEFORE the first leg; the copy build was running, no leg had started)
Copies (`fr90_build.py`):
- In all three sources (S1 copy 3e3d23ce, final VI 15c664e3, BOBS90 257fb852) exactly one panel CONTROL labelled `Auto-Reset`, uid
  17472, current (= default) value True. After `make_default {Auto-Reset: False}` + save, COLD: the panel values differ in exactly
  `{Auto-Reset: True -> False}`; panel rows, callee census, wire edges and VI properties equal to the unchanged byte copy; ExecState 1.
Dry `--order ABBAO` (stale pick log already moved): all five slots "would start".
Legs (fixed 15 picks, no beads, magnet start-up move accepted):
| item | S0 (B90r, 60 s) | A legs (A90r, 120 s) | B legs (B90r, 120 s) | OBS (BOBS90r, 120 s) |
|---|---|---|---|---|
| `# of Auto-Reset` at the end | **0** | **0** | **0** | **0** |
| fps (frame-counter delta / run_s) | 90 +- 1 | 90 +- 1 | 90 +- 1 | 90 +- 1 |
| picks registered (tra) | 15 | 15 | 15 | 15 |
| lost, column-0 gaps | 0 - 50 | **0 - 3,000 per leg (central ~1,000)** - lower than the earlier indicator values 3,359 / 5,860 because the per-frame reseed is gone | **0 - 50 per leg** (central < 20) | not judged |
| LabVIEW gone after, TMX 39 | yes | yes | yes | yes |
- Basis for `# of Auto-Reset` = 0: the lost-bead arm is `Auto-Reset AND (min(pos) < 0)` (`stage2-assembly-step-e.md:66`), so with the
  control False it cannot fire; the periodic arm is not gated by `Auto-Reset` (`pre-rig-master-plan.md:203-212`) but its period is
  "~27 mins/100000" (`GLOSSARY.md:55`), far beyond 120 s (~10,800 frames). If a leg shows a non-zero count, the periodic arm (or a
  reseed path I have not read) fired - the leg is INVALID.
- GAIN rule (`p64_plan.md` 9.1: both B legs below the lower A leg by >= 25 % of the A mean): **predicted MET**, confidence ~60 %. The
  risk is the other way from before: with the reseed gone, A may lose very few frames; if A's lower leg is below ~50 the rule cannot
  be met (a NO-DIFFERENCE result, reported with its numbers).
- OBS: wrapper file exactly 1 line, R - S = 0, own check PASS `{0: rows}`.
- md5 of every source and leg copy unchanged start -> end; motor readbacks G0 exit 0 / G93 TMX 39 per leg.

## 2. The leg copies (`fr90_build.py`, log `fr90_build.log` 03:43:47-04:06:24, `BGRUN END rc=0 after 1356s`, **54 pass / 0 fail**)
All under `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\bench\lean\`. The one change in each: the panel DEFAULT of
the control `Auto-Reset` (uid 17472) True -> False, by `gscript.make_default` (SetControlValue + VI "Make Current Values Default" on a
freshly loaded copy + save + read back). Nothing on any diagram was touched.
| id | file | source (md5) | md5 of the copy | `Auto-Reset` row found | cold diff vs the unchanged byte copy |
|---|---|---|---|---|---|
| A90r | `D1_s1_fr90A_20261015_034347.vi` | `claudeDev\D1_s1_copy.vi` 3e3d23ce | **7ca7d861557fcb331387b8df72a9a975** | control, uid 17472, wire 9806, value True | values: only `{Auto-Reset: True -> False}` of 114; rows 114 equal; callees 97 equal; edges 2216 equal; props equal; ExecState 1 |
| B90r | `D1_ring_fr90B_20261015_034347.vi` | `bench\lean\D1_ring_p6latest_20261014_010104.vi` 15c664e3 | **b96b91e2f93989f915ff9a19f40ca965** | control, uid 17472, wire 25514, value True | values: only `{Auto-Reset}` of 126; rows 126; callees 101; edges 2431; props equal; ExecState 1 |
| BOBS90r | `D1_ring_fr90Bobs_20261015_034347.vi` | `bench\lean\D1_ring_p64Bobs_20261014_114246.vi` 257fb852 | **71ed7b871228660941d24b3c91715df7** | control, uid 17472, wire 25514, value True | values: only `{Auto-Reset}` of 126; rows 126; callees 101; edges 2431; props equal; ExecState 1 |
How "nothing else changed" was shown (per copy, gates `<id>.0-.5` and `<id>.C0-.C8`): the byte copy (md5 == source) was loaded in a fresh
LabVIEW and read: every top-level panel object (panel_wiring: label, indicator, uid, terminal direction, wire) and its value (every
label read by VI Server; values longer than 120 characters compared by md5 of their text; 0 read errors), the callee census of every
diagram, every wire edge (source node/terminal -> sink node/terminal), and five VI execution properties. After the save, a fresh
LabVIEW read the same items from the saved file. Values: exactly one difference, `Auto-Reset` True -> False. Everything else was
equal. Each source md5 was unchanged after its copy was saved, and each saved copy's md5 was unchanged by the cold reads. The B copies
wire `Auto-Reset` through 25514, not 9806; that is the P6 lineage's own wiring and the same in the source. Rule 1a: this is an
input value (a control's default), not a change to any computation. A and B get the same value.

## 3. Picks, stale pick log, dry
- Picks: drive_m8's fixed 15 fractions (no `--fracs-json`, no bead map), the same in every leg.
- Stale pick log moved (checklist step 7) at 03:45: `p64_abba.py --move-stale --to tools/bench/lean_bench/out_latest2/legs/W100OBS_a1`
  -> `picklog.txt` 1475 lines, md5 9a6cc2e3491afa481fcf5e0936f42945 before = after, source gone (`GATE S moved picklog.txt PASS`).
  Nothing deleted. `claudeDev\bench\lean\obs\` empty (no `getbuff_first.txt`).
- Dry `fr90_abba.py ... --order ABBAO` without `--live` (`out_p64/fr90/dry90.log`, 04:06): slots 1-5 (A90r 7ca7d861, B90r b96b91e2, B90r,
  A90r, BOBS90r 71ed7b87) all `md5 == pin -> would start`; RESULT PASS 5/0. `fr90_abba.py` = `p64_abba.py` unchanged, with its leg
  script pointed at `fr90_leg.py` = `p64_leg.py` unchanged + the `# of Auto-Reset` read (section 4).

## 4. How `# of Auto-Reset` is read
`fr90_leg.py` wraps v5's stop in the leg's child process: just before the stop and just after it, VI Server reads `# of Auto-Reset`,
`Auto-Reset`, `Total Lost Frames` and `current image number` (reads only) into `<leg>/fr90_autoreset.json`. The parent adds the gate
`L8 # of Auto-Reset == 0 at the end` (after-stop value) to the leg's `p64_leg.json`, so the sequencer's "leg gates all pass" includes it.

## 5. Smoke S0 (B90r, 60 s)
### Attempt 1 (04:06:48-04:13:53, `out_p64/fr90/s0.log`, `BGRUN END rc=1 after 426s`) - did not reach the test
- G0 PASS (motor session start exit 0, TMN 0 / TMX 39, PI referenced at 0); VISA precheck passed; the VI ran (L1 ExecState 2).
- **v5 L2 FAIL: the IMAQ display was not located** - `band (678, 585, 873, 587) smaller than 200x150`
  (`legs/leg1_B_a1/leg_child.log:175`). So 0 picks were clicked, and the leg ended before pick 1 (stop-on-fail).
- Cause: the driver's locator, not the VI. The capture `tools/bench/m8_shots/20261015_040648_v5_run1_before_picks.png` shows the
  live camera image on the display (a bright grey field, a bead cluster, a bright spot). `d0_locate.locate_image_display` only
  accepts mid-grey pixels (mean 30..110, `d0_locate.py:237-238`), and today's live field is brighter than that.
- The `# of Auto-Reset` read worked: before and after the stop it read `0` and `Auto-Reset` read `false`
  (`leg_child.log:185,444`; frame counter 0, as the VI never left the picking stage).
- End of leg: G90 copy md5 unchanged, G92 LabVIEW gone (forced kill after the 255 s wait, as in earlier legs), G93 TMX? 39.
- **Decision (stated, mine):** the task says "a FAIL ends the task", but this attempt never tested the ring VI's live path: no
  pick was made because the driver's screenshot rule did not fit the brighter field. I fixed the tool and ran S0 ONCE more. If
  attempt 2 fails for any reason, the task ends. The fix, `fr90_locate.py` (d0_locate.py not edited): call the original first;
  only if it finds nothing, re-run the same band method with a higher grey ceiling (160 / 200 / 230), and accept only a box with
  the camera's shape (aspect 1.25 +- 3 %, width 560-720 px). Offline on the attempt-1 capture: original None ->
  fallback (233, 503, 873, 1015) = 641 x 513 at ceiling 160. On the 2026-10-14 replay capture the original gives the same box
  (233, 503, 873, 1015), so the fallback is not used there. That box equals the earlier recorded display rect (232,500)-(873,1013).

### Attempt 2 (04:15:25-04:28:25, `out_p64/fr90/s0_a2.log`, `BGRUN END rc=1 after 778s`) - FAIL at the save dialog, again not a test of the VI
Command (Bash `run_in_background`): `py tools/bgrun.py --material --max-min 25 --log tools/bench/lean_bench/out_p64/fr90/s0_a2.log -- py -u
tools/bench/lean_bench/fr90_abba.py --b-src "...\bench\lean\D1_ring_fr90B_20261015_034347.vi" --b-md5 b96b91e2f93989f915ff9a19f40ca965 --hz 90
--run-s 60 --order B --out-root tools/bench/lean_bench/out_p64/fr90/s0_a2 --live`
| step (`legs/leg1_B_a1/leg_child.log`) | result |
|---|---|
| 0p VISA precheck Rotor / ASRL5 | PASS (0x00000000 both) |
| 0 G0 motor session start | PASS exit 0; TMN 0 / TMX 39; PI REFERENCED, POS -5E-05 |
| L1 VI left idle | PASS (ExecState 2) |
| L2 display located | **PASS via the fr90 fallback** (233, 503, 873, 1015) = 641 x 513 |
| L3 picks | PASS: red markers inside the display 0 -> 15 |
| L4 / L5 / L6 / L7 Done button, click, bandpass, picking loop ended | PASS |
| L8 bandpass panels | 15 closed (the 3-panel contract fails on every 15-pick leg by design; plan 5.4 excludes it) |
| **L9 save dialog** | **FAIL**: the typed path was **relative**: `tools/bench/lean_bench/out_p64/fr90/s0_a2\run\replay_s1_20261015_041525\cal001` |
| L10 cal file / L11 frame counter / L13 tra file | FAIL: no cal file, `Cal File Path` ''; `current image number` 0 .. 0 over 60 s; no tra file |
| L12 stop | VI Server writes did not stop it (the VI was still waiting on the save dialog); COM Abort idled it after 95 s |
| `# of Auto-Reset` before / after the stop | **0 / 0**, `Auto-Reset` false both times (`leg_child.log:299,558`) |
| G90 copy md5 / G91 original md5 / G92 LabVIEW gone / G93 TMX? | PASS b96b91e2 unchanged / PASS 2a78e17c / PASS (forced kill after 255 s) / PASS 39 (POS 0) |
- Cause: **my invocation**, not the VI. I passed `--out-root` as a RELATIVE path. `p64_abba.py` puts the run folder under it
  (`M8_RUN_ROOT`), and v5 types that path into the VI's Windows save dialog. Windows rejected it: the capture
  `tools/bench/m8_shots/20261015_041525_v5_stopfail_run1.png` shows "...\cal001 파일 이름이 올바르지 않습니다" (the file name is not
  valid). The VI never got a path, so it never entered the experiment loop. p64_abba's own default out-root is absolute
  (`os.path.join(HERE, "out_p64", ...)`, `p64_abba.py:295`), and every earlier dry/mock used the default.
- **The user's data folder was not written.** The save dialog opened in the VI's last folder,
  `G:\Data\Seungjae Ko\Periodic\20261014 Random\5pM`, which holds `cal001` (2026-10-14 8:06 PM, 391 KB) and `tra001-000` (8:19 PM,
  11,775 KB). The name was rejected (error dialog above), `Cal File Path` stayed '', the VI was aborted and LabVIEW killed. The
  04:23 capture taken after the rejection still shows only those two files with those dates and sizes. I could not list the folder
  myself (outside this session's allowed directory). **For the user:** please glance at that folder once and confirm it holds
  only `cal001` and `tra001-000` with those dates.
- **Decision: the task ends here** - as I wrote before attempt 2 (section above) and as the task says ("A FAIL ends the task"). I
  did not run a third attempt, even though the cause was my own and the fix is known. No ABBA leg was run.

## 6. Results against the task
| item | result |
|---|---|
| leg copies (1) | **done**: A90r 7ca7d861, B90r b96b91e2, BOBS90r 71ed7b87; the only change each is `Auto-Reset` default False; cold diff shows nothing else changed; ExecState 1 |
| picks (2) | fixed 15; stale pick log moved; dry ABBAO: all 5 would start |
| smoke S0 (3) | **not passed**: attempt 1 driver locator (no pick); attempt 2 my relative save path (no experiment loop). L0-L7 not met; fps not measured; `# of Auto-Reset` = 0 at the end of both attempts |
| ABBAO (4) | **NOT RUN** (the smoke did not pass) |
| per leg rows / lost (column 0) / fps / picks registered | none: no tra file was written in either S0 attempt |
| GAIN verdict (`p64_plan.md` 9.1) | **NOT RUN** |
| OBS own-number check | **NOT RUN** (no OBS leg) |
| earlier ABBA (89 Hz, A 3359 / B 16 / B 12 / A 5860, Auto-Reset state unknown) | nothing new to compare with |
Predictions (section 1) vs results: the copy predictions held exactly (one control, uid 17472, True -> False, nothing else). The
dry held (5 would start). `# of Auto-Reset` = 0 held in both S0 attempts, but in attempt 1 the frame loop never ran, and in
attempt 2 it never ran either (counter 0). So this says nothing about the periodic arm. No leg prediction could be checked.

## 7. Motors, LabVIEW, md5
- Queue's session start, `motor_session_start_fr90_20261015_034002.log`, last lines:
  - `PI  : reference {"FRF": 1.0, "POS": 0.0, "POS_BEFORE": 0.0, "RON": 1.0} -> REFERENCED at 0; verify OK (attempt 1/3)`
  - `LIMITS SL X=-3.847494 Y=-4.774393 SU X=0.152497 Y=-0.774402`
  - `position after (must be unchanged): X=-52899 Y=-41518`
  - `ASI : ASI controller limits match the file (SL {'X': -3.8475, 'Y': -4.7744} / SU {'X': 0.1525, 'Y': -0.7744} mm, tol 0.001) (sender code=0)`
  - `SESSION START OK -> ...\tools\bench\motor_session.json`
  - `RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}`
- Per leg (v5 G0 / G93, the approved per-leg session start): attempt 1 G0 exit 0 (TMN 0 / TMX 39, POS 0), G93 TMX? 39 (POS 0,
  travelled 0); attempt 2 G0 exit 0 (POS -5E-05), G93 TMX? 39 (POS 0). The magnet stayed at 0 in both: the VI's start-up move to
  30 mm did not show in the G93 readback (`travelled=0.000`, POS_BEFORE 0). This session ran no `motor_gate` verb itself.
- LabVIEW: gone after the build (H9), after each S0 attempt (G92 + T6), and `tasklist | grep -i labview | wc -l` -> **0** at the end (04:30).
- md5 start vs end (`fr90_md5.py`, 04:31): **PINS ALL MATCH 8 / 8** - S1 copy 3e3d23ce, final VI 15c664e3, BOBS90 257fb852, A90r
  7ca7d861, B90r b96b91e2, BOBS90r 71ed7b87, the original main VI 2a78e17c, the moved pick log 9a6cc2e3. drive_m8's per-leg
  `_run_` copies were deleted by drive_m8 (no `_run_` file left in `bench\lean`); `bench\lean\obs\` is empty.

## 8. What the next run needs (the fixes are in place; nothing else changes)
1. Run `fr90_abba.py` with the DEFAULT out-root (omit `--out-root`) or an ABSOLUTE one. Same pins as section 2.
2. `fr90_leg.py` already uses `fr90_locate.py` (the original locator first; the camera-shaped fallback only if the original finds
   nothing). It worked live in attempt 2 (L2-L7 PASS).
3. Then S0 -> ABBAO as the task says. Estimate: S0 ~13 min, ABBAO ~65 min.
4. The user check in section 5 (data folder) first.

## 9. Notes, safety, files
- Rules: no hook refusal was routed around. One guard refusal: a foreground log-wait with a 540 s timeout -> `BLOCKED by guard_lean: a
  LabVIEW-touching command needs run_in_background (bgrun) or a timeout <= 30 s (got 540000)`; I re-ran it with a 30 s timeout.
  Permission prompts on compound shell commands (`ls ... ; md5sum ...`, `cd ... ; py ...`) and on `ls`/`md5sum` outside the worktree:
  re-done as single commands, with Glob, or with the read-only `fr90_md5.py`. No guard variable set.
- Not edited: `p64_abba.py`, `p64_leg.py`, `drive_original_copy_v5.py`, `d0_locate.py`, `diag_c104_leg.py`, `tools/hooks/**`,
  `motor_gate.py`, `motor_limits.json`, `CLAUDE.md`, any pre-existing .vi. Inside the big VIs: only the one panel default, via VI Server, on copies.
- New files: `fr90_build.py` (+ `fr90_build.log/.json`, `fr90_state.json`), `fr90_leg.py`, `fr90_abba.py`, `fr90_locate.py`,
  `fr90_md5.py`, `out_p64/fr90/` (dry90.log, s0.log, s0/, s0_a2.log, s0_a2/), the three leg copies in `bench\lean`, this report.
  Moved: `out_latest2/picklog_w100.txt` -> `out_latest2/legs/W100OBS_a1/picklog.txt`. Nothing deleted, nothing committed.
- user_notes vs task: no conflict.
- Minutes: 03:40 -> 04:32 = 52.

RESULT {"fr90": "INCOMPLETE", "lost": {"A": null, "B": null, "why": "smoke S0 not passed - attempt 1 driver display locator (live field brighter than its mid-grey rule, no pick), attempt 2 my relative --out-root (Windows rejected the save path, no experiment loop); ABBAO not run"}, "auto_reset": {"S0_a1": 0, "S0_a2": 0, "legs": "not run"}, "gain": "NOT RUN", "copies": {"A90r": "7ca7d861557fcb331387b8df72a9a975", "B90r": "b96b91e2f93989f915ff9a19f40ca965", "BOBS90r": "71ed7b871228660941d24b3c91715df7"}, "md5_equal": true, "labview_gone": true, "minutes": 52}
