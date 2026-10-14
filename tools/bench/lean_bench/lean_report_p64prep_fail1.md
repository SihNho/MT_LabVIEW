# Lean report - p64prep (2026-10-14): P6-4 preparation, read and plan only

Task `tools/bench/lean_bench/queue/running/p64prep.md`. One Opus session, lean rules (`CLAUDE.md`). **No LabVIEW, no driver,
no `motor_gate.py`, no camera, no rig.** Files written: `p64_plan.md`, this report, 7 lines appended to
`questions_for_user.md`. Nothing else edited; nothing committed. `tasklist | grep -ic labview` -> 0 at 10:07.
A = main checkout `../V6_ParallelLoop/`, B = this worktree.

## 0. Start condition and user notes
- `lean_report_p6close.md:262` RESULT `"p6close": "PASS"` -> started.
- `user_notes.md` has 3 notes: (1) no edit inside the big P6 VI, small subVI copy + callee swap; (2) v5 G0 per-leg
  session start APPROVED; (3) P6-4 PREPARATION approved, read + plan only, the bead run waits for the user at the rig.
  The task text agrees with all three; nothing contradicts. Note (1) decides the form of the two test variants in the
  plan (observer copy, 150 Hz wrapper: callee swaps only); note (2) answers section-14 item 9.
- `tools/bench/motor_session.json` exists (queue-owned); not used - this task touches no motor. STOP file absent.

## 1. What was read (key lines re-read by this session)
- B: `CLAUDE.md`; the task; `user_notes.md`; `lean_report_p6close.md` (all, section 14 = :201-237); `lean_report_latest.md`
  :1-70, :138-187; `questions_for_user.md`; `tools/bench/diag_c104_abba.py` (all); `diag_c104_leg.py` (all);
  `drive_m8.py` (all); `drive_original_copy_v5.py` (all); `motor_limits.json`; the p6close P62 leg record
  `out_p6close/legs/P62_a1/m8_v5_replay_s1.json:255-344` (panel record) and the four `m8_replay_s1.json:102` lost lines;
  `imaqdx_attributes.txt` (chunk / timestamp attributes).
- A: `docs/d1/ring-p6.md` (all), `docs/d1/ring-p6b.md` (all), `docs/d1-loop12-17-split-plan.md:865-894, 1843-1932, 2252-2291`,
  `docs/camera-acquisition-facts.md:1-100, 630-760`, `docs/m8-real-run-plan.md:290-339`, `docs/user-rules.md` (all),
  `STATUS.md:1-80`, `tools/bench/decisions_pending.json:108-122` (D-2026-09-25-05), `docs/decisions/camera_settings_in_vi_cal_out_of_scope.md`,
  `experimental_load_beads_and_frame_rate.md`, `display_policy_and_camera_panel_decisions.md`, grep of
  `docs/main-vi-subvi-identity.md` (camera open / Configure Grab call sites).

## 2. Section-14 open items -> answer or question
| # | section-14 item ("not in the files") | outcome | where |
|---|---|---|---|
| 14.2 | a live-camera run of 15c664e3 | **answered (fact):** none exists; every P6 run swapped #6810/#22692 to replay stand-ins (`lean_report_p6close.md:29-30,207`). Plan: a 60 s B smoke leg before the ABBA, stop if it fails | plan §2, §5.4 |
| 14.4 / a | the P6-4 pass criterion | **HOLD-1** (criterion proposed in PD217(f)'s GAIN form, A split-plan:1849, + functional + acceptance #1). **ASSUME-2** for the metric: lost = column-0 gaps of the tra file for both arms. Found in the files: P6's `Total Lost Frames` indicator counts camera-loop gaps only - W100 read `"0"` (`out_p6close/legs/W100_a1/m8_replay_s1.json:102`) while 1068 frames had no row (`lean_report_p6close.md:112`) - so the indicator cannot be the A-vs-B metric | plan §3.3, §9, §10 |
| 14.5 / c | how 15c664e3 runs at 150 Hz | **answered in principle:** the user chose "rate set inside the VI (copy only), later as metadata" (D-2026-09-25-05, A `decisions_pending.json:108-122`; A `docs/decisions/camera_settings_in_vi_cal_out_of_scope.md:22-25`). Form per `user_notes.md:2`: callee swap of the `IMAQdx Configure Grab` call (#13962 in S1, A `main-vi-subvi-identity.md:106`) to a small wrapper that writes + reads back `AcquisitionFrameRate` = 150 (camera ceiling 247.95 Hz, A `camera-acquisition-facts.md:29-36`; .icd reload :642-647). **HOLD-2:** apply it to the A arm (a copy of the original) too, or run 90 Hz only | plan §1, §10 |
| 14.6 / d | do the panel's magnet controls move anything during a leg | **answered: no.** v5 writes only the 3 control-flow booleans, "no panel PARAMETER" (`drive_original_copy_v5.py:278-285`), panel recorded "never set" (:596-600); `Send to Trans`, `Start Cycles`, `Send to Rot`, `HOME`, `1 L-Turn`, `1 R-Turn` False, `Trans Step`/`Rot Step` 0 before and after the p6close P62 leg (`m8_v5_replay_s1.json:264-307, 539-582`). The motion that does happen per leg (G0 reference, init PI -> 30 mm, z-stack, autofocus, G93 reference 30 -> 0) is listed with sources in plan §4 | plan §4, §7 |
| 14.7 / e | bead preparation, focus, machine vs aimed picks | **HOLD-3** (beads, focus, when; state stays 조립; magnet 0 -> 30 -> 0 mm per leg with beads OK?) and **HOLD-4** (fixed machine picks / bead-map picks from one camera snapshot, same 15 points every leg (recommended) / hand picks). Not in the files: the earlier real ABBA ran with "No beads on the rig" (A `STATUS.md:54`) and fixed-fraction machine clicks (`drive_m8.py:33-38`) | plan §2, §3.4, §10 |
| 14.8 / b | acceptance #1 on a LIVE run | **ASSUME-1**, design in plan §6: column 0 = `Num - LastBufferNumber(read once)` -> one constant per run (`lean_report_latest.md:18-29`); a separate OBS leg per rate runs a byte copy of 15c664e3 with the pick call #31710 swapped to the already-built observer `RingPickSlot_latestobs` 9504e0cf (logs Num[0..19], last, picked Num, slot, tick); offline join "picked - C == col0" for every row, in order, C = first picked Num, each pick inside the ring (the join `latest` ran on replay: 1474/1474, 0 mismatches, `lean_report_latest.md:157-159`). Extra saved: the pick log (test copy only) + the driver moving it per leg. Stated limit: slot-image pairing and TransPos/RotPos lag stay proven by the replay legs. The camera's own frame metadata was checked and is not usable from the files: `ChunkDataDecodingEnabled = False`, `ReceiveTimestampMode = 'None'`, no chunk frame-ID attribute listed (`imaqdx_attributes.txt:14-15,179`) | plan §6 |
| 14.9 | v5 G0 per-leg limit re-write + PI reference | **answered:** approved (`user_notes.md:3`; `questions_for_user.md:9`). Kept unchanged in the plan | plan §3.6 |

Plus ASSUME-3 (method inside the rules): 120 s / 15 picks / ABBA as before, smoke leg first, 150 Hz as a separate task,
the two builds and the driver copy (`p64_abba.py`, dry run) before the rig day.

## 3. The plan
**`tools/bench/lean_bench/p64_plan.md`** - sections: 0 what P6-4 is; 1 VIs (byte copies under `claudeDev\bench\lean\`;
A90 from `D1_s1_copy.vi` 3e3d23ce, B90 from 15c664e3, BOBS observer copy, 150-Hz variants by callee swap); 2 legs (90 Hz:
smoke + A B B A + OBS, ~72 min; 150 Hz: A B B A + OBS, ~60 min; two tasks); 3 driver changes, described not made
(`p64_abba.py`/`p64_leg.py` = parameterised copies of `diag_c104_abba.py`/`diag_c104_leg.py`: rate, run length, B pin,
no #8323 gates, no INDEX append, STOP/motor-session check per leg; `p64_sum.py` lost metric; bead-map picks; pick-log
move; `p64_own.py`); 4 every motor move per leg with sources; 5 stop conditions; 6 the live acceptance #1 design;
7 answers found in the files; 8 predictions per leg; 9 acceptance in final words; 10 the 7 questions; 11 order of work.

## 4. What was not done / limits
- Not checked in a VI (read-only work, no LabVIEW): whether the `Display period (ms)` label exists on the P6 panel (the plan
  makes that read recorded-only either way); the P6-lineage uid of the Configure Grab call (the plan says: locate by class +
  callee); which device carries the z-stack focus step. Each is marked in the plan.
- Predictions for B are wide because the ring VI has never run on the live camera; the A numbers come from legs without beads.
- `questions_for_user.md` lines carry "10:0x" (written 10:07).

RESULT {"p64prep": "PASS", "answered": 4, "questions": {"hold": 4, "assume": 3}, "plan": "tools/bench/lean_bench/p64_plan.md", "minutes": 9}
