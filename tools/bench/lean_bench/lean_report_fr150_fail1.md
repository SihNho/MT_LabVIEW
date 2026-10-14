# Lean report - fr150 (2026-10-15): frame-rate ABBA at 150 Hz, Auto-Reset OFF in every leg copy (fixed 15 picks, no beads)

Task `tools/bench/lean_bench/queue/running/fr150.md`. One Opus session, lean rules (`CLAUDE.md`). Started 05:59.

## 1. Predictions (written 06:08, BEFORE the copy build and before any LabVIEW run)
| item | S0 (B150r, 60 s) | A legs (A150r, 120 s) | B legs (B150r, 120 s) | OBS (BOBS150r, 120 s) |
|---|---|---|---|---|
| `# of Auto-Reset` at the end (after the stop) | **0** | **0** | **0** | **0** |
| rate line (`obs\configgrab_rate150.txt`) | exactly 1 line `150 150 1909 0 <tick>` | same | same | same |
| fps = frame-counter delta / run_s | 148 +- 3 | 148 +- 3 | 148 +- 3 | 148 +- 3 |
| picks registered, from the tra file | 15 | 15 | 15 | 15 |
| lost = column-0 gaps of the tra file | 0 - 100 | **300 - 9,000 per leg (central ~2,500, i.e. ~14 % of ~18,000)** | **0 - 300 per leg (central < 60)** | not judged |
| column-0 steps | {1: most, 2: a few} | {1: most; 2 and 3 frequent; a tail of larger steps} | {1: ~all, 2: a few} | - |
| display box / locator | fr90 fallback, box (233,503,873,1015), C2 PASS | same | same | same |
| LabVIEW gone after, G0 exit 0, G93 TMX 39 | yes | yes | yes | yes |
- **Basis.** There is no earlier 150 Hz measurement (`p64_plan.md:264`; that plan's 55-75 % estimate for A was made from A's row
  rate WITH the reseed). At 90 Hz with Auto-Reset OFF (fr90, `lean_report_fr90.md:104-107`) A lost 224 / 522 of ~10,900 (2-5 %),
  mostly as steps of 3 ({1: 10799, 3: 107, ...}), i.e. A keeps up on average but stalls ~20-30 ms now and then. At 150 Hz the
  budget per frame drops from 11.1 ms to 6.67 ms, so every stall costs more frames (steps of 4-5) and A's average per-frame work
  (tracking + Force plot, unmeasured) may no longer fit -> wide range, central ~14 %. B (ring + parallel loop) lost 17 / 4 at 90 Hz;
  its frame path is lighter, so it should still keep up at 150 Hz; central < 60.
- fps: fr90 read ~1.2 % under the set rate (88.9 for 90) with the same window rule, so ~148; the p64p2 30 s harness gave 149.947
  by buffer numbers. Rows per leg ~18,000 minus the loss.
- `# of Auto-Reset` = 0: the reseed arm is `Auto-Reset AND (min(pos) < 0)` (`../V6_ParallelLoop/docs/pre-rig-master-plan.md:195-200`);
  with the control False it cannot fire; the periodic arm (~100,000 frames) is beyond 120 s x 150 = 18,000 frames.
- **GAIN rule** (both B legs below the lower A leg by >= 25 % of the A mean): **predicted MET, confidence ~70 %** (higher than at
  90 Hz: the tighter budget should widen the A-B gap; the risk stays a small A loss, as the low A leg 224 at 90 Hz).
- **OBS own check:** `getbuff_first.txt` exactly 1 line; R - S small and positive (fr90 gave 12; at 150 Hz maybe ~12-25);
  `col0 + S - picked` = {0: rows} -> PASS, confidence ~70 %.
- Copies: exactly one control `Auto-Reset`, uid 17472, default True in each 150 Hz source; cold diff only
  `{Auto-Reset: True -> False}`; rows / callees / edges / props equal (A 114 rows / 2216 edges, B and BOBS 126 rows / 2431 edges,
  as in fr90 and p64p2); the wrapper at #23006 / #31524 / #31381; BOBS150r calls GetBuffFirst #4092; ExecState 1.
- R1 / R2 self-test PASS; C1 / C2 PASS; dry ABBAO: all five slots `md5 == pin -> would start`.
- md5 of every input unchanged start -> end.

## 0. Start condition, user notes, motor session start
- `lean_report_fr90.md:184` RESULT `"fr90": "PASS"`; `tools/bench/motor_session.json` present (Glob, 06:01); `tasklist | grep -ic labview`
  -> 0 (06:01); `tools/bench/lean_bench/STOP` absent (Glob); `fr150_md5.py start` (06:01:34, `out_p64/fr150/md5_start.log` / `.json`):
  **PINS ALL MATCH (10 / 10)** - A150 65b409a8, B150 d3953cd6, BOBS150 35e7e973, wrapper 1419d4c6, GetBuffFirst 4cd87cb4, `.icd`
  2ea8512c, A90r 7ca7d861, B90r b96b91e2, BOBS90r 71ed7b87, original main VI 2a78e17c. `claudeDev\bench\lean\obs\` holds neither
  `getbuff_first.txt` nor `configgrab_rate150.txt`, and the BOBS150 pick-log default path `out_latest2\picklog_w100.txt` does not
  exist (fr90 moved it) - nothing to move (checklist step 7 not needed). **Met** -> started.
- `user_notes.md`: no conflict with the task (fixed 15 picks, no beads / pull test / Jev - note 12; no edit inside a big VI - note 1,
  only the panel default; v5 G0's per-leg session start kept - note 3).
- Queue's session start for this cycle, `motor_session_start_fr150_20261015_060004.log` (read only), last lines:
  - `PI  : reference {"FRF": 1.0, "POS": 0.0, "POS_BEFORE": 0.0, "RON": 1.0} -> REFERENCED at 0; verify OK (attempt 1/3)`
  - `LIMITS SL X=-3.847494 Y=-4.774393 SU X=0.152497 Y=-0.774402`
  - `position after (must be unchanged): X=-52899 Y=-41518`
  - `RESULT: controller limits set (mode limits-set)`
  - `ASI : ASI controller limits match the file (SL {'X': -3.8475, 'Y': -4.7744} / SU {'X': 0.1525, 'Y': -0.7744} mm, tol 0.001) (sender code=0)`
  - `SESSION START OK -> ...\tools\bench\motor_session.json`
  - `RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}`

## 2. The three leg copies (`fr150_build.py`, log `fr150_build.log` 06:02:5x-06:24, `BGRUN END rc=0 after 1279s`, **64 pass / 0 fail**)
`fr150_build.py` = `fr90_build.py` (not edited) with its SRC table changed to the three 150 Hz sources. Beyond the SRC table I
changed only what had to change so that fr90's files are neither reused nor written: the state file (`fr150_state.json`; fr90's
state would have skipped the build and reused fr90's timestamp), the json / work-file / task names, the tag names; and I ADDED
gates C9a-d (the task's call-site checks) and the wrapper / GetBuffFirst md5 pins of the run. Method unchanged: byte copy ->
`gscript.make_default {Auto-Reset: False}` on the copy -> save -> fresh LabVIEW -> cold reads vs the unchanged byte copy.
All under `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\bench\lean\`:
| id | file | source (md5) | md5 of the copy | `Auto-Reset` row | cold diff vs the unchanged byte copy |
|---|---|---|---|---|---|
| A150r | `D1_s1_fr150A_20261015_060254.vi` | A150 65b409a8 | **74c2a9048b96b2836b7119dc9f22a2e2** | control, uid 17472, wire 9806, True | values only `{Auto-Reset: True -> False}`; rows 114 equal; callees 97 equal; edges 2216 equal; props equal; ExecState 1; wrapper the callee at exactly #23006; no vi.lib Configure Grab call |
| B150r | `D1_ring_fr150B_20261015_060254.vi` | B150 d3953cd6 | **ee4a61c87fca753ab61f263aba77bba2** | control, uid 17472, wire 25514, True | only `{Auto-Reset}`; rows 126; callees 101; edges 2431; props equal; ExecState 1; wrapper at exactly #31524; no Configure Grab |
| BOBS150r | `D1_ring_fr150Bobs_20261015_060254.vi` | BOBS150 35e7e973 | **0efd7a746a5089de716ebfe3e023fd95** | control, uid 17472, wire 25514, True | only `{Auto-Reset}`; rows 126; callees 101; edges 2431; props equal; ExecState 1; wrapper at exactly #31381; GetBuffFirst at #4092 |
Each source md5 unchanged after its copy's save (`.5`, `.C8`); each copy's md5 unchanged by the cold reads (`.C7`); wrapper 1419d4c6
and GetBuffFirst 4cd87cb4 unchanged (`.C9d`, H3 every pin still holds); H5 refs opened 40 == closed 40; H6 no file left / removed
(the scratch work copy removed by the stage); H9 LabVIEW gone. No save prompt naming a source or the wrapper was answered with Save.

## 3. R1 / R2 self-test, C1 / C2, dry
- `fr150_abba.py` = `fr90_abba.py` imported unchanged (C1 + leg script `fr90_leg.py`, which carries the `# of Auto-Reset` read and
  the C2 display-box check) + R1 (added to p64_abba's leg-start refusals, before every leg and in the dry) + R2 (hooked into
  p64_abba's `keep_leg_files` step, which `run_leg` calls right after T6 LabVIEW gone and P2, before it reads `p64_leg.json`: the
  rate file is moved into the leg folder, `<leg>\fr150_rate.json` written, and the rate gate added to the leg's `p64_leg.json`
  gates so "L leg gates all pass" includes it).
- **Self-test** `fr150_abba.py --r-selftest` (`out_p64/fr150/r_selftest.log`, TEMP stand-in obs dir; the real obs dir untouched):
  R1 absent -> may start; R1 stale file -> REFUSED; R1 through `p64_abba.start_checks` (+C1) -> only the R1 reason; R2 good line
  `150 150 1909 0` -> gate PASS, moved, md5 equal, source gone; R2 two lines / readback 90.0009 / readback 150.2 / code
  -1074360311 / file missing -> gate FAIL (leg INVALID); every move kept md5 and removed the source; real obs dir unchanged.
  **R SELFTEST PASS (15 / 15 cases)**; then fr90_abba's C1 self-test **7 / 7 PASS** (unchanged).
- C2 unchanged from fr90 (`fr90_locate.py`, box within +-5 px of (232,500)-(873,1013), else no pick); it is checked live per leg.
- **Dry** (`out_p64/fr150/dry_abbao.log`, 06:24:23, `BGRUN END rc=0 after 2s`): `fr150_abba.py` with the exact live arguments
  (A150r / B150r / BOBS150r with the md5s above, `--hz 150 --run-s 120 --order ABBAO --out-root
  G:\...\V6_lean\tools\bench\lean_bench\out_p64\fr150\abbao`), no `--live`: every slot `GATE C1 out-root` PASS, `GATE C1 run folder`
  PASS, `GATE R1 ... absent` PASS, then `A 74c2a904 / B ee4a61c8 / B ee4a61c8 / A 74c2a904 / O 0efd7a74 md5 == pin -> would start`;
  RESULT PASS 5 / 0. Nothing launched.

## 4. Smoke S0 (B150r, 60 s, 150 Hz) - run ONCE: **PASS**
`out_p64/fr150/s0.log` (06:24:32-06:35:10, `BGRUN END rc=0 after 638s`), leg folder `out_p64/fr150/s0/legs/leg1_B_a1/`, summary
`out_p64/fr150/s0/p64_abba.json` (md5 f3cb71c6...). Command: `py tools/bgrun.py --material --max-min 25 --log
tools/bench/lean_bench/out_p64/fr150/s0.log -- py -u tools/bench/lean_bench/fr150_abba.py --b-src "...\bench\lean\D1_ring_fr150B_20261015_060254.vi"
--b-md5 ee4a61c87fca753ab61f263aba77bba2 --hz 150 --run-s 60 --order B --out-root "G:\...\V6_lean\tools\bench\lean_bench\out_p64\fr150\s0" --live`
| item | result |
|---|---|
| C1 out-root / run folder; R1 | PASS / PASS; R1 PASS (no stale rate file) |
| VISA precheck Rotor / ASRL5 | 0x00000000 both |
| G0 motor session start (v5, approved) | PASS exit 0; TMN 0 / TMX 39; RON 1 FRF 1 POS -5E-05 POS_BEFORE 0 travelled 0 |
| display box + locator (`leg_child.log:175-176`) | fr90 fallback (original: band (658,585,873,587) too small); box (233,503,873,1015) 641x513; offsets [1,3,0,2]; **C2 PASS** |
| cal / tra files | `run\replay_s1_20261015_062434\cal001` 857,377 B, `tra001-000` 2,375,121 B, both under out_p64 |
| rows / **lost (column-0 gaps)** | **6,184 rows, lost 3,273** (34.6 % of 9,457 frames spanned); column 0 strictly increasing; cols 3 + 3x15 |
| **column-0 steps** | **{1: 2984, 2: 3131, 3: 65, 4: 1, 5: 1, 6: 1}** - about half the rows skip one frame |
| picks registered (tra) | **15** (`picks_clicked` 31 = all clicks, not used) |
| fps (frame counter over the 60 s window) | 8,735 frames -> **145.58 Hz** (T5 within 15 %: PASS) |
| `Total Lost Frames` indicator | 26 (camera-loop gaps only, recorded) |
| `# of Auto-Reset` before / after the stop | **0 / 0**, `Auto-Reset` false both (`leg_child.log:298,310`); L8 PASS |
| **rate line** (R2) | exactly 1 line `150 150 1909 0 38229903` -> readback 150, exposure 1909 us, code 0; moved into the leg folder, md5 cdb9fb64 before = after; **PASS** |
| p64_leg gates L-1, L0-L8 + R2 | all PASS (11 / 11); sequencer Q, T6, P2, T1, L, T5, T12 PASS (7 / 0) |
| G93 / LabVIEW | TMX? 39, POS_BEFORE 30 -> reference move to 0 (the VI's start-up move to 30 mm, accepted); LabVIEW gone (T6) |
**S0 passed every criterion of task step 5**, so ABBAO was started. The loss (3,273) is far above my prediction (0-100) - a result,
not a pass criterion of S0: at 150 Hz the B arm's saving loop keeps only about two of every three frames (steps of 2 dominate).

## 5. ABBAO (150 Hz, 120 s per leg, the same fixed 15 picks) - **all 5 legs ran, every leg valid, 37 / 0 gates**
`out_p64/fr150/abbao.log` (06:35:2x-07:33, `BGRUN END rc=0 after 3485s`), summary `out_p64/fr150/abbao/p64_abba.json` (md5
015683f4ee024b55b763ced4dbdf3850), per-leg extract `out_p64/fr150/legsum_abbao.txt` (read-only `fr150_legsum.py`). Command = the dry's
plus `--live`. Leg folders `out_p64\fr150\abbao\legs\leg<N>_<arm>_a1\`, run folders `out_p64\fr150\abbao\run\replay_s1_<time>\` (cal001 +
tra001-000). Before every leg: C1 out-root / run folder PASS, R1 PASS, STOP / session / rig / pin / LabVIEW / VISA clear (gate Q).
| leg | VI | run folder | rows (tra) | **lost, column-0 gaps** | **column-0 steps** | fps (frame counter / 120 s) | `Total Lost Frames` (after stop) | `# of Auto-Reset` before / after | picks (tra) | rate line (R2) | G0 / G93 | LabVIEW gone |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 A | A150r | `replay_s1_20261015_063532` | 12,372 | **6,182** (33.3 %) | {1: 9375, 3: 2828, 4: 156, 5: 7, 6: 4, 11: 1} | 17,782 -> **148.18** | 6,202 | 0 / **0** | **15** | 1 line `150 150 1909 0 38887333`, PASS | exit 0 TMX 39 / TMX? 39 | yes (T6) |
| 2 B | B150r | `replay_s1_20261015_064709` | 12,969 | **5,536** (29.9 %) | {1: 7576, 2: 5253, 3: 137, 4: 1, 7: 1} | 17,784 -> **148.20** | 26 | 0 / **0** | **15** | 1 line `150 150 1909 0 39585518`, PASS | same | yes |
| 3 B | B150r | `replay_s1_20261015_065846` | 12,966 | **5,534** (29.9 %) | {1: 7573, 2: 5254, 3: 137, 7: 1} | 17,779 -> **148.16** | 27 | 0 / **0** | **15** | 1 line `150 150 1909 0 40281900`, PASS | same | yes |
| 4 A | A150r | `replay_s1_20261015_071022` | 12,990 | **5,565** (30.0 %) | {1: 10279, 3: 2571, 4: 135, 5: 3, 7: 1} | 17,786 -> **148.22** | 5,586 | 0 / **0** | **15** | 1 line `150 150 1909 0 40977516`, PASS | same | yes |
| 5 OBS | BOBS150r | `replay_s1_20261015_072159` | 12,321 | 6,172 (33.4 %, not judged) | {1: 6371, 2: 5744, 3: 192, 4: 11, 6: 1, 7: 1} | 17,771 -> **148.09** | 27 | 0 / **0** | **15** | 1 line `150 150 1909 0 41674779`, PASS | same | yes |
- Every leg: p64_leg L-1, L0-L8 and the R2 rate gate all PASS (11 / 11; column 0 strictly increasing, cols 3 + 3x15, 0 TIFFs,
  15 bandpass panels == 15 registered, TMX 39 after), T1 rc 0, T5 within 15 % of 150, T6 LabVIEW gone, P2 md5 unchanged, T12
  registered 15 with no rerun. `Auto-Reset` read false before and after every stop. **No leg is INVALID** (no leg was refused,
  none re-run).
- Display box in every leg: fr90 fallback, (233,503,873,1015), offsets [1,3,0,2], **C2 PASS**.
- Rate files: each leg's `obs\configgrab_rate150.txt` moved into its own leg folder (md5 before = after: 7a18f9e4, f223710c,
  c08fd1d0, 69a1068c, e9a67c41), `obs\` empty again before the next leg (R1 PASS each time).
- Every G0: `exit=0; LIMITS TMN=0 TMX=39`; every G93: `TMX?=39.0`, POS_BEFORE 30 -> reference move to 0 (the VI's start-up move to
  30 mm, accepted by the task).
- `p64_sum` counts the tra rows over the whole loop (not just the 120 s counter window): spanned frames A 18,554 / 18,555, B 18,505 /
  18,500, OBS 18,493.

### 5.1 GAIN verdict (`p64_plan.md` 9.1; `p64_sum.abba_summary`, the same column-0 rule for A and B): **NOT MET (no difference)**
A = 6,182 / 5,565 (mean 5,873.5), B = 5,536 / 5,534. Limit = min(A) - 0.25 x mean(A) = 5,565 - 1,468.4 = **4,096.6**. Both B legs are
above it: **GAIN NOT MET**. The B legs are below the lower A leg by only 29 / 31 frames (0.5 %); in share of frames both arms lose
~30 % (A 30.0-33.3 %, B 29.9 %). This is a NO-DIFFERENCE result at 150 Hz, reported with its numbers and not re-run (`p64_plan.md:294`).
Section 9.2 (functional, every B leg) holds: all leg gates, 15 == 15, column 0 strictly increasing, stopped by its own stop control,
LabVIEW gone, md5 unchanged. 9.5 safety: every G0 exit 0, every G93 TMX 39, no refusal routed around.
- **Step distributions (review :14), facts only:** A is mostly steps of 3 (2,828 / 2,571, plus 4-11), i.e. A runs at full rate for a
  while and then misses two frames at once; B (and OBS) are steps of 1 and 2 in near-equal numbers (7,576 / 5,253), i.e. B keeps
  roughly two of every three frames all the time. B's `Total Lost Frames` (camera-loop gaps) stays at 26-27, so B's camera loop
  keeps up at 150 Hz and the frames are lost between the ring and the saved rows; A's indicator equals its column-0 gaps (6,202 vs
  6,182; 5,586 vs 5,565 - within 0.4 %, so plan 8.1's "A indicator ~= A column-0 gaps within 1 %" holds at 150 Hz).

### 5.2 OBS leg own-number check (`p64_own.py`, `legs/leg5_O_a1/p64_own.json`) - **PASS**
- `getbuff_first.txt` held **exactly 1 line** (md5 7e761f5d...) and was moved with the pick log (12,322 lines, md5 f12fb544...) into
  the leg folder, md5 equal after the move, sources gone (gate O PASS); `obs\` and the pick-log default path are empty again.
- S = 35322 (logged start value), R = 35343, **R - S = 21**; step 2: 12,321 rows vs 12,322 picks, `col0 + S - picked` = **{0: 12321}**
  (every row equals its own pick's buffer number, one-to-one, in order, no fitted constant); 1 trailing pick (53837) without a row,
  counted; step 3: col0[0] = 21 >= R - S = 21 PASS; step 4: lag at the pick {0: 12322}, share 1.0 PASS; end lag 2. Verdict **PASS**.
- So acceptance #1's **live half (number consistency, plan 9.3) is shown at 150 Hz** on a live camera, with ~33 % of frames not
  saved: every saved row's buffer number is its own frame's pick. The other half (image pairing + X/Y/Z bit-identical) still rests
  on the replay (plan 9.4).

### 5.3 Compared with fr90 (90 Hz, the same rules, Auto-Reset OFF) - facts only
| | fr90 (90 Hz) | fr150 (150 Hz) |
|---|---|---|
| A lost (column 0) | 224 / 522 | 6,182 / 5,565 |
| A steps | {1: 10799, 3: 107, 4: 1, 8: 1} (leg 1) | {1: 9375, 3: 2828, ...} / {1: 10279, 3: 2571, ...} |
| B lost (column 0) | 17 / 4 | 5,536 / 5,534 |
| B `Total Lost Frames` | 16 / 15 | 26 / 27 |
| fps | ~88.9 | ~148.2 |
| GAIN | MET (limit 130.75) | NOT MET (limit 4,096.6) |
| OBS own check | PASS {0: 11081}, R - S 12 | PASS {0: 12321}, R - S 21 |
At 90 Hz B kept nearly every frame; at 150 Hz both arms keep ~70 % and B's advantage disappears. Why the B arm's saving path tops out
near ~100 rows/s at 150 Hz (12,966 rows / ~123 s) is not measured by this task.

## 6. Predictions vs results
| prediction (section 1) | result |
|---|---|
| `# of Auto-Reset` 0 at every end | **held** (S0 + 5 legs, 0 / 0) |
| rate line exactly 1, `150 150 1909 0` | **held** in all 6 legs |
| fps 148 +- 3 | **held** for the 120 s legs (148.09-148.22); S0 145.58 (60 s window) just outside +- 3, within T5 |
| picks registered 15 (tra) | **held** in all 6 legs |
| S0 lost 0-100 | **missed**: 3,273 |
| A lost 300-9,000, central ~2,500 | in range (6,182 / 5,565), above the central guess |
| B lost 0-300, central < 60 | **missed badly**: 5,536 / 5,534 |
| A steps {1, 2-3, tail}; B {1: ~all, 2: a few} | A as predicted (steps of 3 dominate the misses); **B missed**: steps of 2 are ~40 % of B's rows |
| GAIN met, ~70 % | **NOT MET** (no difference) |
| OBS: 1 line, R - S ~12-25, own PASS `{0: rows}` | **held**: 1 line, R - S 21, `{0: 12321}` |
| C2 via fallback (233,503,873,1015) | **held** in all 6 legs |
| copies: only Auto-Reset, rows / edges / call sites as listed; R1/R2, C1, dry | **held** exactly |
| md5 unchanged | **held** (section 7) |
My basis for B (the ring + parallel loop "keeps up") was wrong at 150 Hz: B's camera loop keeps up (indicator 26-27) but its saved rows do not.

## 7. Motors, LabVIEW, md5
- Queue's session start: section 0 (`motor_session_start_fr150_20261015_060004.log`). Per leg (v5 G0, the approved per-leg session
  start; G93 post-run readback): 6 / 6 G0 `exit=0; LIMITS TMN=0 TMX=39`; 6 / 6 G93 `TMX?=39.0`, POS_BEFORE 30 -> POS 0 / -5E-05.
  This session ran no `motor_gate` verb itself.
- LabVIEW: gone after the build (H9), after S0 and every leg (T6); `tasklist | grep -ic labview` -> **0** at the end (07:33).
- md5 (`fr150_md5.py`): start `out_p64/fr150/md5_start.log` (06:01:34) **PINS ALL MATCH 10 / 10**; end `out_p64/fr150/md5_end.log`
  (07:33:46) **PINS ALL MATCH 13 / 13** (the 10 inputs + A150r 74c2a904, B150r ee4a61c8, BOBS150r 0efd7a74), **DIFF start vs end EQUAL
  10 / 10**; `obs\getbuff_first.txt`, `obs\configgrab_rate150.txt` and the pick-log default path absent at start and end.

## 8. Notes, safety, files
- Approval prompts (not approved; re-done as single commands or with Glob / Grep, never another route to the same effect):
  first message verbatim: `This Bash command contains multiple operations. The following part requires approval: grep -ic labview;
  ls tools/bench/motor_session.json; ls tools/bench/lean_bench/STOP 2>&1; ls -t tools/bench/lean_bench/motor_session_start_fr150_* ;
  ls "/c/Program Files/National Instruments/LabVIEW 2026/user.lib/claudeDev/bench/lean/obs/"`; later `Contains simple_expansion`
  (a `; echo rc=$?` line; the self-test was re-run plainly and then via bgrun with a log), a `| sed -n` line (re-done with Grep on a
  written summary), and a `py -c` one-off (`This command requires approval`; re-done with Grep). **Hook refusals: none.** No guard
  variable set.
- Not edited: `fr90_*` files, `p64_abba.py`, `p64_leg.py`, `p64_own.py`, `p64_sum.py`, `drive_original_copy_v5.py`, `d0_locate.py`,
  `tools/hooks/**`, `motor_gate.py`, `motor_limits.json`, `CLAUDE.md`, the `.icd`, any pre-existing .vi. Saved VIs: only the three
  Auto-Reset copies; nothing inside any diagram edited; wrapper, A150 / B150 / BOBS150 and the fr90 copies byte-identical (section 7).
- New: `fr150_md5.py`, `fr150_build.py` (+ `fr150_build.log/.json`, `fr150_state.json`), `fr150_abba.py`, `fr150_legsum.py`
  (read-only extract), `out_p64/fr150/` (md5_start/end .json/.log, r_selftest.log, dry_abbao.log, s0.log, s0/, abbao.log, abbao/,
  legsum_abbao.txt), this report. Moved (never deleted): every leg's `obs\configgrab_rate150.txt` -> its leg folder; after the OBS leg
  `obs\getbuff_first.txt` and `out_latest2\picklog_w100.txt` -> `out_p64\fr150\abbao\legs\leg5_O_a1\`. Only TEMP self-test stand-ins
  were removed. Nothing committed; nothing queued (no p64run90 / p64run150).
- user_notes vs task: no conflict. Every save path was typed absolute under out_p64 (C1).
- Minutes: 05:59 -> 07:37 = 98.

## 9. Verdict
**fr150: PASS** by the task's PASS list - three copies with only the `Auto-Reset` default changed (cold diff), S0 passed, ABBAO's five
legs all ran and every leg is valid with all gates PASS, the OBS own check PASS `{0: 12321}` (acceptance #1's live half shown at
150 Hz), md5 equal, LabVIEW gone. **The measured result is a NO-DIFFERENCE at 150 Hz:** GAIN NOT MET - A lost 6,182 / 5,565 and B
5,536 / 5,534 (both ~30 % of frames). The B arm's camera loop keeps up (26-27 camera gaps) but its saved rows skip every other frame
about 40 % of the time; at 90 Hz the same copies gave A 224 / 522 vs B 17 / 4.

RESULT {"fr150": "PASS", "lost": {"A": [6182, 5565], "B": [5536, 5534], "S0": 3273, "OBS": 6172, "metric": "column-0 gaps"}, "steps": {"S0": {"1": 2984, "2": 3131, "3": 65, "4": 1, "5": 1, "6": 1}, "leg1_A": {"1": 9375, "3": 2828, "4": 156, "5": 7, "6": 4, "11": 1}, "leg2_B": {"1": 7576, "2": 5253, "3": 137, "4": 1, "7": 1}, "leg3_B": {"1": 7573, "2": 5254, "3": 137, "7": 1}, "leg4_A": {"1": 10279, "3": 2571, "4": 135, "5": 3, "7": 1}, "leg5_OBS": {"1": 6371, "2": 5744, "3": 192, "4": 11, "6": 1, "7": 1}}, "auto_reset": {"S0": 0, "leg1_A": 0, "leg2_B": 0, "leg3_B": 0, "leg4_A": 0, "leg5_OBS": 0}, "rate_lines": {"S0": "150 150 1909 0", "leg1_A": "150 150 1909 0", "leg2_B": "150 150 1909 0", "leg3_B": "150 150 1909 0", "leg4_A": "150 150 1909 0", "leg5_OBS": "150 150 1909 0"}, "fps": {"S0": 145.58, "A": [148.18, 148.22], "B": [148.2, 148.16], "OBS": 148.09}, "gain": "NOT MET - no difference (limit 4096.6; B 5536, 5534 > limit; B below the lower A by 29 / 31 frames)", "own_check": "PASS {0: 12321}, R-S 21", "md5_equal": true, "labview_gone": true, "minutes": 98}
