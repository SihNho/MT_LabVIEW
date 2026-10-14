# Lean report - fr90 retry 1 (2026-10-15): frame-rate ABBA at 90 Hz, Auto-Reset OFF in every leg copy (fixed 15 picks)

Task `tools/bench/lean_bench/queue/running/fr90.md` (retry 1 of 1, the LAST try for the tag). One Opus session, lean rules (`CLAUDE.md`).
Started 04:38.

## 1. Predictions (written 04:43, BEFORE the S0 leg; no leg had started in this session)
| item | S0 (B90r, 60 s) | A legs (A90r, 120 s) | B legs (B90r, 120 s) | OBS (BOBS90r, 120 s) |
|---|---|---|---|---|
| `# of Auto-Reset` at the end (after the stop) | **0** | **0** | **0** | **0** |
| fps = frame-counter delta / run_s | 90 +- 1 | 90 +- 1 | 90 +- 1 | 90 +- 1 |
| picks registered, from the tra file `(cols - 3) / 3` | 15 | 15 | 15 | 15 |
| lost = column-0 gaps of the tra file | 0 - 50 | **0 - 3,000 per leg (central ~1,000)** | **0 - 50 per leg (central < 20)** | not judged |
| display box / locator | fr90 fallback (live field bright, as run 1 attempt 2), box (233,503,873,1015), C2 PASS | same | same | same |
| LabVIEW gone after, G93 TMX 39 | yes | yes | yes | yes |
- Basis for `# of Auto-Reset` = 0: the lost-bead reseed arm is `Auto-Reset AND (min(pos) < 0)`
  (`../V6_ParallelLoop/docs/pre-rig-master-plan.md:195-200`), so with the control False it cannot fire. The periodic arm is not
  gated by `Auto-Reset`, but its period (~27 min / 100,000 frames) is far beyond 120 s (~10,800 frames). A non-zero count = that
  leg is INVALID (not used).
- A legs: with no beads and no reseed, the A VI still runs its full tracking + Force-plot path per frame; the earlier A indicator
  values (3,359 / 5,860, Auto-Reset state unknown) included any reseed cost. Central guess ~1,000, wide range.
- **GAIN rule** (`p64_plan.md` 9.1: both B legs below the lower A leg by >= 25 % of the A mean): **predicted MET, confidence ~55 %**.
  The main risk: with the reseed gone, A may lose very few frames; if the lower A leg is below ~50, the rule cannot be met
  (a NO-DIFFERENCE result, reported with its numbers).
- **OBS own check:** wrapper file `getbuff_first.txt` exactly 1 line; R - S = 0; own check PASS `{0: rows}` (`p64_own.py`).
  Confidence ~70 % (never run live; replay only).
- md5 of every pinned file unchanged start -> end (8 / 8); each leg's G0 exit 0, G93 TMX? 39.

## 0. Start condition, user notes
- `lean_report_p64ready.md:122` RESULT `"p64ready": "PASS"`; `tools/bench/motor_session.json` present; `tasklist | grep -ic labview`
  -> 0 (04:39); `tools/bench/lean_bench/STOP` absent (only the archived `STOP_run1_*` / `STOP_run3_*`); `fr90_md5.py` 04:39:
  **PINS ALL MATCH (8 / 8)**. `claudeDev\bench\lean\obs\` empty (Glob: no files) - checklist step 7 not needed. **Met** -> started.
- `user_notes.md`: no conflict with the task. Fixed 15 picks, no beads, no pull test, no Jev work (note 12, "the program first");
  no VI built or edited (note 1 not touched); v5 G0's per-leg session start kept (note 3).

## 2. The leg copies (kept from run 1, not rebuilt; quoted from `lean_report_fr90_fail1.md` section 2)
All under `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\bench\lean\`. "The one change in each: the panel
DEFAULT of the control `Auto-Reset` (uid 17472) True -> False, by `gscript.make_default` ... Nothing on any diagram was touched."
| id | file | source (md5) | md5 of the copy | cold diff vs the unchanged byte copy (run 1) |
|---|---|---|---|---|
| A90r | `D1_s1_fr90A_20261015_034347.vi` | `claudeDev\D1_s1_copy.vi` 3e3d23ce | **7ca7d861557fcb331387b8df72a9a975** | values: only `{Auto-Reset: True -> False}` of 114; rows 114; callees 97; edges 2216; props equal; ExecState 1 |
| B90r | `D1_ring_fr90B_20261015_034347.vi` | `bench\lean\D1_ring_p6latest_20261014_010104.vi` 15c664e3 | **b96b91e2f93989f915ff9a19f40ca965** | only `{Auto-Reset}` of 126; rows 126; callees 101; edges 2431; props equal; ExecState 1 |
| BOBS90r | `D1_ring_fr90Bobs_20261015_034347.vi` | `bench\lean\D1_ring_p64Bobs_20261014_114246.vi` 257fb852 | **71ed7b871228660941d24b3c91715df7** | only `{Auto-Reset}` of 126; rows 126; callees 101; edges 2431; props equal; ExecState 1 |
All three md5 matched their pins at the start of this session (section 0).

## 3. C1 / C2 / C4 (offline, before any leg)
Only fr90_* files changed: `fr90_abba.py` (C1), `fr90_locate.py` (C2), `fr90_leg.py` (doc line only), new `fr90_c2_check.py`.
`p64_abba.py`, `p64_leg.py`, `drive_original_copy_v5.py`, `d0_locate.py` not edited.
- **C1 output path check** (`fr90_abba.py`): p64_abba's `start_checks` (called before EVERY leg by `run_leg`, and per slot in the
  dry) is wrapped: first the leg's out-root and its run folder (`M8_RUN_ROOT`, else `<out-root>\run`) must be absolute (drive +
  root) and their real path (`os.path.realpath`, `normcase`) must lie strictly under `<V6_lean>\tools\bench\lean_bench\out_p64\`;
  otherwise a `GATE C1 ... FAIL` line is printed and the reason joins the leg's refusals -> the leg is REFUSED, the leg script
  (and so LabVIEW) is not started. Self-test `fr90_abba.py --c1-selftest` (`out_p64/fr90/r1_c1_selftest.log`): **7 / 7 PASS** -
  refused: the run-1 attempt-2 relative path `tools/bench/lean_bench/out_p64/fr90/s0_a2` ("is not absolute"), an absolute path in
  `out_latest2`, out_p64 itself, `out_p64\..\out_latest2` (escapes via `..`), `C:\Temp\out_p64\fr90`; accepted: the intended
  `...\out_p64\fr90r1\s0` and the same upper-cased.
- **C2 display box check** (`fr90_locate.py`): whichever locator gave the box (original `d0_locate`, or the run-1 camera-shaped
  fallback), it is handed to v5 only if every side is within +-5 px of the recorded rect (232,500)-(873,1013); otherwise (or if
  nothing is found) the locator returns None, and v5 returns before any pick (`drive_original_copy_v5.py:348-349`) -> leg FAIL.
  The box, the locator name and the check are printed (`[fr90 locate] ...`, into `leg_child.log` and v5 L2's detail).
  `fr90_c2_check.py` (`out_p64/fr90/r1_c2_offline.log`):
  | capture | locator | box | side offsets | C2 |
  |---|---|---|---|---|
  | run-1 attempt 1 `m8_shots/20261015_040648_v5_run1_before_picks.png` | fr90 fallback (original: band (678,585,873,587) too small; grey ceiling 160) | (233,503,873,1015) 641x513 | [1, 3, 0, 2] | PASS |
  | run-1 attempt 2 `20261015_041525_..._before_picks.png` | fr90 fallback (same) | (233,503,873,1015) | [1, 3, 0, 2] | PASS |
  | 2026-10-14 replay captures, all 13 (`20261014_000335` ... `20261014_043654`) | original (mid-grey band) | (233,503,873,1015) | [1, 3, 0, 2] | PASS |
  Synthetic boxes: exact rect, all sides +5, all sides -5 -> accepted; left +6, bottom -6, shifted 40 px, the run-1 band
  (678,585,873,587), nothing found -> refused. **C2 SYNTH PASS (8 / 8).**
- **C4 dry** (`out_p64/fr90/r1_dry_abbao.log`, 04:41): `fr90_abba.py --order ABBAO` with the exact live arguments, out-root
  `G:\...\V6_lean\tools\bench\lean_bench\out_p64\fr90r1\abbao` (absolute), no `--live`: for each of slots 1-5 `GATE C1 out-root`
  and `GATE C1 run folder` PASS, then `A 7ca7d861 / B b96b91e2 / B b96b91e2 / A 7ca7d861 / O 71ed7b87 md5 == pin -> would start`;
  RESULT PASS 5 / 0. Nothing launched.

## 4. Smoke S0 (B90r, 60 s) - run ONCE: **PASS**
`out_p64/fr90/r1_s0.log` (04:41:50-04:52:32, `BGRUN END rc=0 after 642s`), leg folder `out_p64/fr90r1/s0/legs/leg1_B_a1/`.
Command: `py tools/bgrun.py --material --max-min 25 --log tools/bench/lean_bench/out_p64/fr90/r1_s0.log -- py -u
tools/bench/lean_bench/fr90_abba.py --b-src "...\bench\lean\D1_ring_fr90B_20261015_034347.vi" --b-md5 b96b91e2f93989f915ff9a19f40ca965
--hz 90 --run-s 60 --order B --out-root "G:\...\V6_lean\tools\bench\lean_bench\out_p64\fr90r1\s0" --live`
| item | result |
|---|---|
| C1 out-root / run folder | PASS / PASS (absolute, under out_p64) |
| VISA precheck Rotor / ASRL5 | 0x00000000 both |
| G0 motor session start (v5, approved) | PASS exit 0; TMN 0 / TMX 39; RON 1 FRF 1 POS 0 POS_BEFORE 0 travelled 0 |
| display box + locator (v5 L2, `leg_child.log:175-176`) | **fr90 fallback** (original: band (677,585,873,587) too small); box (233,503,873,1015) 641x513; offsets [1,3,0,2]; **C2 PASS** |
| L3 picks / Done / bandpass | 15 panels answered (`bandpass_answered` 15); v5 L8 (3-panel contract) FAIL by design, excluded (plan 5.4) |
| L9 save dialog | PASS, absolute path typed: `...\out_p64\fr90r1\s0\run\replay_s1_20261015_044152\cal001` |
| cal / tra files (L13) | `cal001` 857,377 B, `tra001-000` 2,179,666 B, both under out_p64 |
| rows / lost (column-0 gaps) | **5,675 rows, lost 5** (steps {1: 5672, 2: 1, 5: 1}); column 0 strictly increasing; cols 3 + 3x15 |
| picks registered (tra) | **15** (`picks_clicked` 31 is all clicks, not used) |
| fps (frame counter over the 60 s window) | 22125 .. 27372 = 5,247 frames -> **87.45 Hz** (T5 within 15 %: PASS) |
| `Total Lost Frames` indicator | 17 (recorded only; P6 counts camera-loop gaps) |
| `# of Auto-Reset` before / after the stop | **0 / 0**, `Auto-Reset` false both (`leg_child.log:298,310`); gate L8 PASS |
| L12 stop | VI Server stop worked, idle after 1.0 s |
| p64_leg gates L-1, L0-L8 | **all PASS** (10 / 10); sequencer gates Q, T6, P2, T1, L, T5, T12 all PASS (7 / 0) |
| G92 / G93 | LabVIEW gone (waited 255 s, forced kill, as every earlier leg); TMX? 39, POS_BEFORE 30 -> reference move back to 0 (travelled 30.000: the VI's start-up move to 30 mm, accepted by the task) |
| md5 B90r after | b96b91e2 unchanged (P2 PASS) |

## 5. ABBAO (120 s per leg, the same fixed 15 picks) - **all 5 legs PASS, 37 / 0 gates**
`out_p64/fr90/r1_abbao.log` (04:52:4x-05:51, `BGRUN END rc=0 after 3505s`), summary `out_p64/fr90r1/abbao/p64_abba.json`
(md5 6ffdc6ab7e2bb38109a41174d4d17f36). Command as the C4 dry plus `--live` (out-root `G:\...\out_p64\fr90r1\abbao`). Every leg's
out path is `out_p64\fr90r1\abbao\legs\leg<N>_<arm>_a1\` and its run folder `out_p64\fr90r1\abbao\run\replay_s1_<time>\` (cal001 +
tra001-000). Before every leg: C1 out-root / run folder PASS, STOP / session / rig / pin / LabVIEW / VISA clear (gate Q PASS).
| leg | VI | run folder | rows (tra) | **lost, column-0 gaps** | col-0 steps | fps (frame counter / 120 s) | `Total Lost Frames` | `# of Auto-Reset` before / after stop | picks registered (tra) | display box / locator | G0 / G93 | LabVIEW gone |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 A | A90r | `replay_s1_20261015_045250` | 10,909 | **224** | {1: 10799, 3: 107, 4: 1, 8: 1} | 22073..32743 -> **88.92** | 236 (after stop) | 0 / **0** | **15** | (233,503,873,1015), fallback, C2 PASS | exit 0 / TMX 39 | yes (T6) |
| 2 B | B90r | `replay_s1_20261015_050432` | 11,077 | **17** | - | 22056..32718 -> **88.85** | 16 | 0 / **0** | **15** | same, C2 PASS | exit 0 / TMX 39 | yes |
| 3 B | B90r | `replay_s1_20261015_051612` | 11,097 | **4** | - | 22047..32716 -> **88.91** | 15 | 0 / **0** | **15** | same, C2 PASS | exit 0 / TMX 39 | yes |
| 4 A | A90r | `replay_s1_20261015_052753` | 10,613 | **522** | - | 22112..32782 -> **88.92** | 532 (534 after stop) | 0 / **0** | **15** | same, C2 PASS | exit 0 / TMX 39 | yes |
| 5 OBS | BOBS90r | `replay_s1_20261015_053936` | 11,081 | 15 (not judged) | - | 21789..32454 -> **88.88** | 15 | 0 / **0** | **15** | same, C2 PASS | exit 0 / TMX 39 | yes |
- Every leg: p64_leg L-1, L0-L8 all PASS (column 0 strictly increasing, cols 3 + 3x15, 0 TIFFs, 15 bandpass panels answered ==
  15 registered, TMX 39 after), T1 rc 0, T5 fps within 15 %, T6 LabVIEW gone (waited 255 s then forced kill, as every earlier leg),
  P2 md5 unchanged, T12 registered 15 with no rerun. `Auto-Reset` read `false` before and after every stop. **No leg is INVALID.**
- In every leg the original locator found only a thin band and the fr90 fallback gave (233,503,873,1015), offsets [1,3,0,2], C2 PASS.
- Every leg's G93: POS_BEFORE 30 -> reference move to 0 (travelled 30.000): the VI's own start-up move to 30 mm, as accepted by the task.

### 5.1 GAIN verdict (`p64_plan.md` 9.1; `p64_sum.abba_summary`, the same column-0 rule for A and B)
A = 224 / 522 (mean 373), B = 17 / 4. Limit = min(A) - 0.25 x mean(A) = 224 - 93.25 = **130.75**. Both B legs (17, 4) are below it:
**GAIN MET.** The larger B leg (17) is 7.6 % of the lower A leg. Section 9.2 (functional, every B leg) also holds: all leg gates,
15 == 15, column 0 strictly increasing, stopped by its own stop control (v5 L12 VI Server, idle after 1 s), LabVIEW gone, md5 unchanged.
9.5 safety: every G0 exit 0, every G93 TMX 39, no refusal routed around.

### 5.2 OBS leg own-number check (`p64_own.py`, `legs/leg5_O_a1/p64_own.json`) - **PASS**
- The wrapper file `getbuff_first.txt` held **exactly 1 line** (md5 01011c2f...) and was moved into the leg folder with the pick log
  (11,082 lines, md5 948faaf5...), both md5 equal after the move, sources gone (gate O PASS). `bench\lean\obs\` is empty again.
- S = 21347 (logged start value), R = 21359, **R - S = 12**; step 2: 11,081 rows vs 11,082 picks, `col0 + S - picked` = **{0: 11081}**
  (every row equals its own pick's buffer number, in order, no fitted constant); 1 trailing pick (32455) without a row, counted;
  step 3: col0[0] = 12 >= R - S = 12 PASS; step 4: lag at the pick {0: 11082}, share 1.0 PASS; end lag 2. Verdict **PASS**.
- So acceptance #1's **live half (number consistency, plan 9.3)** is shown at 90 Hz on a live camera: every saved row's buffer
  number is its own frame's pick. The other half (image pairing + X/Y/Z bit-identical) still rests on the replay (plan 9.4).

### 5.3 Compared with the earlier ABBA (89 Hz; A 3359 / B 16 / B 12 / A 5860 - those are `Total Lost Frames` indicator values, Auto-Reset state unknown) - facts only
| | earlier (indicator) | now, indicator | now, column-0 gaps |
|---|---|---|---|
| A legs | 3,359 / 5,860 | 236 / 532 | 224 / 522 |
| B legs | 16 / 12 | 16 / 15 | 17 / 4 |
With Auto-Reset OFF the A arm's loss is 11-14x lower than the earlier A values; the B arm is about the same. The earlier B legs
were a different VI (the display-loop VI, plan 8.1), so the B row is not a like-for-like comparison. This fits the user's caution
(the reseed costs frames) but this task did not run an Auto-Reset ON leg, so it does not measure that cost directly.
- Plan 8.1's inference "A indicator ~= A column-0 gaps within 1 %": 236 vs 224 (5.1 %) and 532 vs 522 (1.9 %) - **outside 1 %**
  (the indicator is read over the 120 s window of the frame counter, the tra rows cover the whole loop; reported, not explained further).

## 6. Predictions vs results
| prediction | result |
|---|---|
| `# of Auto-Reset` 0 at every end | **held** (S0 + 5 legs, 0 / 0) |
| fps 90 +- 1 | **missed slightly**: 87.45 (S0, 60 s window) and 88.85-88.92 (120 s legs); all within T5's 15 % |
| picks registered 15 (tra) | **held** in all 6 legs |
| S0 lost 0-50 | held: 5 |
| A lost 0-3,000, central ~1,000 | held in range (224 / 522), below the central guess |
| B lost 0-50, central < 20 | held (17 / 4) |
| GAIN met, ~55 % | **met** (limit 130.75; B 17 / 4) |
| OBS: 1 line, R - S = 0, own PASS `{0: rows}` | 1 line and own PASS `{0: 11081}` held; **R - S = 12, not 0** (the first saved row is col0 12 = R - S, so step 3 still passes) |
| display box via fallback (233,503,873,1015), C2 PASS | held in all 6 legs |
| md5 8 / 8 unchanged; G0 exit 0 / G93 TMX 39 | held |

## 7. Motors, LabVIEW, md5
- Queue's session start for this cycle, `motor_session_start_fr90_20261015_043830.log`, last lines:
  - `LIMITS SL X=-3.847494 Y=-4.774393 SU X=0.152497 Y=-0.774402`
  - `position after (must be unchanged): X=-52899 Y=-41518`
  - `RESULT: controller limits set (mode limits-set)`
  - `ASI : ASI controller limits match the file (SL {'X': -3.8475, 'Y': -4.7744} / SU {'X': 0.1525, 'Y': -0.7744} mm, tol 0.001) (sender code=0)`
  - `SESSION START OK -> ...\tools\bench\motor_session.json`
  - `RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}`
- Per leg (v5 G0 = the approved per-leg session start; G93 = post-run readback): 6 / 6 G0 `exit=0; LIMITS TMN=0 TMX=39`,
  RON 1 FRF 1, POS 0 (or -5E-05 / -0.0001); 6 / 6 G93 `TMX?=39.0`, POS_BEFORE 30 -> POS 0. This session ran no `motor_gate` verb itself.
- LabVIEW: gone after every leg (T6 / G92); `tasklist | grep -ic labview` -> **0** at the end (05:52).
- md5 start (04:39) vs end (05:52), `fr90_md5.py`: **PINS ALL MATCH 8 / 8** both times (S1 copy 3e3d23ce, final VI 15c664e3, BOBS90
  257fb852, A90r 7ca7d861, B90r b96b91e2, BOBS90r 71ed7b87, original main VI 2a78e17c, moved pick log 9a6cc2e3).

## 8. Notes, safety, files
- S0 ran once and passed; no leg was re-run (C3 not triggered). No hook refusal was routed around. One guard refusal: a foreground
  offline C2 check with a 120 s timeout -> `BLOCKED by guard_lean ... timeout <= 30 s`; re-run with 30 s. A few compound / inline
  shell commands needed approval (non-interactive -> not run); re-done as single commands, the dry via bgrun, the log waits via the
  new read-only `fr90_wait.py`. No guard variable set.
- Not edited: `p64_abba.py`, `p64_leg.py`, `drive_original_copy_v5.py`, `d0_locate.py`, `tools/hooks/**`, `motor_gate.py`,
  `motor_limits.json`, `CLAUDE.md`, any .vi. No VI built or edited.
- Changed: `fr90_abba.py` (C1), `fr90_locate.py` (C2), `fr90_leg.py` (doc only). New: `fr90_c2_check.py`, `fr90_wait.py`,
  `out_p64/fr90/r1_*.log`, `out_p64/fr90r1/` (s0, abbao), this report. Moved by p64_abba after the OBS leg (never deleted):
  `bench\lean\obs\getbuff_first.txt` and `out_latest2\picklog_w100.txt` -> `out_p64\fr90r1\abbao\legs\leg5_O_a1\`. Nothing committed.
- The user's data folder `G:\Data\Seungjae Ko\Periodic\20261014 Random\5pM` was not opened; every save path in this run was typed
  absolute under out_p64 (v5 L9 detail). Its unchanged state is not claimed (ASSUME, task).
- user_notes vs task: no conflict.
- Minutes: 04:38 -> 05:54 = 76.

RESULT {"fr90": "PASS", "lost": {"A": [224, 522], "B": [17, 4], "S0": 5, "OBS": 15, "metric": "column-0 gaps"}, "auto_reset": {"S0": 0, "leg1_A": 0, "leg2_B": 0, "leg3_B": 0, "leg4_A": 0, "leg5_OBS": 0}, "gain": "MET (limit 130.75; B 17, 4 < 130.75)", "fps": {"S0": 87.45, "A": [88.92, 88.92], "B": [88.85, 88.91], "OBS": 88.88}, "picks_registered_tra": 15, "own_check": "PASS {0: 11081}, R-S 12", "md5_equal": true, "labview_gone": true, "minutes": 76}
