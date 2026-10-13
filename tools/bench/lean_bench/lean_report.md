# Lean-bench report — P6-2 (recorded-frame replay, rule 1a for P6), 2026-10-13

One Opus session. Started 13:54:36 (`start.txt`); report written about 14:58, so roughly 64 min. About $6 spent.

## Verdict
On the same recorded frames, P6 and S1 give **bit-identical X/Y/Z on every one of the 2538 compared rows**. DISTINCT passes
on all 2538 rows at D = 20. trans/rot are bit-identical on all 2437 rows after device init. The .cal files differ only
inside the date/time field. The init rows are finite and inside the PI range. Every task item PASSes.

There is one extra compare item, B4 ("init first+last value equal S1's"). It comes from the judgement text PD409(b) and is
**not** in the task list. B4 FAILs on row 0's trans value. The details and why it is not a rule-1a fail are below.

## Timeline (clock time)
| time | step |
|---|---|
| 13:54:36 | start; read CLAUDE.md, task.md, ring-p6.md PD409-412, p6_replay_facts.md, next.json, recipe, driver, compare |
| 13:56 | input md5 snapshot `md5_start.json` (18 files) |
| 13:56-13:57 | tool edits (listed below) |
| 13:57:19 | `motor_gate.py --session start`: OK (`motor_session_start_0.log`) |
| 13:57:42 - 14:06:06 | build: `stage_replay_swap.py --plan lean` gave **19 pass / 0 fail** (`build_lean.log`) |
| 13:57:52 | `drive_m8_replay_p6.py --selftest` 7/0 after my edits |
| 14:06:16 | chain run 1 launched with a RELATIVE `--out-root`; I stopped it within about 30 s (reason below). No leg had started and no LabVIEW was running. Left an empty `out_20261013/` |
| 14:06:50 - 14:27:12 | chain run 2 (`legs_run2.log`, `out_20261013b/`): S1 attempt 1 FAIL at v5 L4, attempt 2 FAIL at T2 (two different causes, below). Motor end readback OK; LabVIEW gone |
| 14:27:48 - 14:27:58 | chain run 3 (`legs_run3.log`): crashed in 1 s on my own syntax error. Motor start and end both OK; LabVIEW never opened |
| 14:28:30 - 14:52:23 | **chain run 4** (`legs_run4.log`, `out_20261013d/`): S1 leg then P6 leg, then the compare. 17 gates / 0 fail |
| 14:53:00 | final `motor_gate.py --session end`: OK (`motor_session_end_final.log`) |
| 14:53 | md5 end snapshot: **EQUAL 18/18** with the start; `tasklist` shows 0 LabVIEW processes |

## Build (task step 1)
- A byte copy of `claudeDev\D1_ring_p6_20261012_212645.vi` (c2d9c13c) with plan 170's two swaps:
  - #6810 → `replay\replay_get_buff_image_paced60.vi` (59ec66b6)
  - #22692 → `replay\replay_get_image_cal.vi` (afce0d04)
- Saved **only** at `claudeDev\bench\lean\D1_ring_p6_replay_20261013_135743.vi`, **md5 09a23608c223a9a31ea6ca3638c1241c**. That md5 was read again at the end and is the same.
- Gates:
  - A1: copy md5 equals the source.
  - A2: before the swap, #6810 calls `get buff image-lost frames.vi` and #22692 calls `IMAQdx Get Image.vi`. ExecState 1.
  - A3: both `replace_object` calls returned no error; new uids 31533 and 6829.
  - A4: the callee diff is exactly the two swaps.
  - A5: wire edges 2426 before and 2426 after, diff 0.
  - A6: ExecState 1 warm.
  - Cold check: C1 ExecState 1, C2 cold census equals warm, C3 md5 unchanged by the cold load.
  - Hygiene: H5 VI-Server refs opened 8 / closed 8 / live 0. H2 and H3: input and all pins unchanged. H9: LabVIEW gone.
- The ring subVIs (`claudeDev\RingPickSlot_v0.vi`, `RingSeqCheck_v0.vi`) loaded from the new folder. ExecState was 1 right after the open.

## Legs (task step 3), run 4, output under `tools/bench/lean_bench/out_20261013d/`
Frames came from `G:\m8_replay_frames`. Its `frames_manifest.json` md5 is f9032ae5, the same as F-facts. The pinned text
manifest `tools/bench/p6_replay_frames_manifest.txt` has md5 9055d98a in the main checkout and 73877ae0 in this worktree.
That is a line-ending copy of the same text, and it was unchanged start to end.

| leg | src (md5) | run_s | tra rows ('actual data points') | Total Lost Frames | frame-counter delta | picks | LabVIEW gone |
|---|---|---|---|---|---|---|---|
| S1 | `replay\D1_s1_replay_20260925_075422.vi` (126f8497) | 120 | **6321** | **0** | 5962 | 15 | yes |
| P6 | `bench\lean\D1_ring_p6_replay_20261013_135743.vi` (09a23608) | 150 | **2538** (>= 1500) | 0 | 2460 | 15 | yes |

v5 reports `run1.L8` as failing on both legs. L8 is v5's "== 3 panels" contract, which does not apply when N = 15. The
110-7 leg A failed it the same way (`t0_legs/c110f.../A_S1replay_a1/leg.json:453`). drive_m8 gates M1-M8 PASS on both legs.

Files each leg wrote (name, size, md5):
- S1 run dir `run/replay_s1_20261013_142928/`:
  - `cal001` 857377 B 08fbaff8cf13155210f6fddd0ae1f009
  - `tra001-000` 2427726 B b3c7fcb2020abb4195d28ce2bedfb1a3
- P6 run dir `run/replay_s1_20261013_144109/`:
  - `cal001` 857377 B 5e81876c543570b41c2e16d0c0df99dc
  - `tra001-000` 975054 B 072e1488226ab82cca20abcb2fea36da
- S1 leg dir `legs/S1_a1/`:
  - `leg.json` d7b63ed1
  - `clicks.json` 38101b39
  - `m8_replay_s1.json` 718e303a
  - `m8_v5_replay_s1.json` e8678ef5
  - `m8_v5_replay_s1_clicks.json` 38101b39
- P6 leg dir `legs/P6_a1/`:
  - `leg.json` 28d33ce0
  - `clicks.json` 432c2558
  - `m8_replay_s1.json` cb4b54ae
  - `m8_v5_replay_s1.json` 1c4a6b04
  - `m8_v5_replay_s1_clicks.json` 432c2558
- `m8json/` holds the same m8 jsons under their `_p15_r120` / `_p15_r150` names.
- Chain records: `drive_m8_replay_p6.json` 86abeab5713e74294994c655d5a6a19d; compare `m8b_replay_p6.json` 6fc795ac882533f278ce4b42c20b93bc.
- Screenshots: `tools/bench/m8_shots/20261013_14*`. The run copies (`*_run_<ts>.vi`) were deleted by drive_m8 (M8 PASS); no new one is left in claudeDev.

## Compare (task step 5): S1 lost 0, so it ran. D = 20 (U13, `ring-p4b.md:21`). A = S1, B = P6.
| item | number | result |
|---|---|---|
| tra both parse | dims [6321, 48] / [2538, 48] | PASS |
| **DISTINCT** (S1 row i differs from each of rows i+1..i+20) | 2538 / 2538 pass, 0 fail | **PASS** |
| **MATCH** X/Y/Z bit-identical per common row (B1) | 2538 common rows, 0 not identical; first miss: none; drop signature: none | **PASS** |
| finite cells compared per bead | beads 1-14: 7614 each (= 3 × 2538); bead 15: 2538. NaN cells A 5076 = B 5076, all in bead 15 (2 of its 3 cells per row, on both legs) | fact |
| **cal outside the date/time field** (B2) | walk consumed 857377/857377 on both; field at offset 857264, length 41 on both; 4 bytes differ, **0 outside the field** (text `오후 2:33:18` vs `오후 2:44:59`) | **PASS** |
| **trans/rot post-init** (B3) | init boundary row 101 (last S1 change at row 100); 2437 stationary rows, **0 differ** | **PASS** |
| **init inside motor_limits.json ranges** (B6) | 101 init rows of P6: trans in [0.0, 30.00555] inside PI 0..39, 0 non-finite, 0 outside; rot 0 non-finite (rotor: finite only). ASI has no tra column, so it is not evaluated | **PASS** |
| **every other leg file**, run dir (B5) | `cal001` and `tra001-000` present in both and both differ: cal only inside the field (B2); tra differs because P6 has fewer rows and column 0 is time | **PASS** |
| **every other leg file**, leg dirs (B7) | 5 files, present in both, all differ (driver records with timestamps and click coordinates; not computation outputs) | **PASS** |
| extra, not a task item: B4 init first+last equal S1 | rows finite, last row equal (30.0, 139407.84) on both; **first row differs: S1 (21.6852, 0.0) vs P6 (0.0, 0.0)** | FAIL (fact) |

What B4 means: trans in column 1 is the PI stage position read back from hardware. In S1, the first tra row was written
while the device-init move toward 30 mm was already under way (21.6852 mm). In P6 it was written before the move started
(0.0 mm). The answered criterion D-2026-10-12-01/02 (`decisions_pending.json:387,406`) asks for trans/rot to be "identical
after device init", with a "per-frame stored check during init". That is met (B3, B6). Matching init start values comes only
from PD409(b)'s wording. I report it as a fact. I did not re-run anything for it.

## What failed and how I fixed it
1. **The recipe saved only to `claudeDev\replay\`.** I added an optional plan key `work_dir` to `tools/recipes/stage_replay_swap.py`,
   plus a new plan `tools/bench/plans/plan_replay_swap_lean.json` with plan 170's swaps, md5s and pins and `work_dir: bench\lean`.
2. **Leg outputs were hard-wired to `tools/bench/m8_out` and `tools/bench`.** I added:
   - env `M8_RUN_ROOT` in `drive_m8.py` for the run dir;
   - `--out-root` and `--swap-json` in `drive_m8_replay_p6.py`, which set `M8_RUN_ROOT` / `M8_OUT_DIR` and the P6 md5 pin source;
   - in `m8_legs.keep_leg_files` and `diag_c104_leg.py:176,210`, reads from `M8_OUT_DIR` when it is set.
   The driver self-test is still 7/0.
3. **Run 1: I passed a relative `--out-root`.** v5 types the run dir into LabVIEW's save dialog, so I stopped the run within
   about 30 s, before any leg. motor_gate's own output from that run was not captured, so I cannot say whether its start
   finished. The next start (run 2) completed with a full readback.
4. **Run 2, S1 attempt 1: v5 L4 "Done Picking Yes button not located".** The cause: `tools/bench/ref_done_yes_button.png`
   (`d0_locate.REF_DONE`) is untracked and exists only in the main checkout. Without it the template score was None and no
   candidate could win. The harness blocked a copy from the main checkout, and I did not work around that. Instead I cut a
   46×29 patch (the stored reference's size) from this run's own screenshot `m8_shots/20261013_140748_v5_run1_before_done.png`,
   at the box d0_locate's shape test had found ((1091,900)-(1136,928), caption 25×12), using
   `lean_bench/make_ref_done.py`. Checked offline with `lean_bench/diag_done.py`: winner (1113,914), score 0.00, next-best 28.35,
   so it passes the 50 % ratio test.
5. **Run 2, S1 attempt 2: drive_m8 passed 8/8, but leg.json had run_dir null, so T2 failed.** The cause was my item 2:
   `diag_c104_leg.py` still read drive_m8's json from `tools/bench`. I fixed lines 176 and 210. That attempt's data is kept,
   unused, in `out_20261013b/` (S1 lost 0, 4571 tra points).
6. **Run 3: my edit to line 176 put a comment in the middle of an expression, so it crashed (SyntaxError).** I fixed it and
   compile-checked all four edited scripts. Run 4 then passed 17/0.

## Motor sessions (readback lines quoted)
- **Session start 13:57:19** (`motor_session_start_0.log`):
  `LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0` · `PI  : PI controller limits match the file (TMN 0.0000 / TMX 39.0000, tol 0.001)` ·
  `PI  : reference {"FRF": 1.0, "POS": 0.0, "POS_BEFORE": 0.0, "RON": 1.0} -> REFERENCED at 0; verify OK (attempt 1/3)` ·
  `LIMITS SL X=-3.847494 Y=-4.774393 SU X=0.152497 Y=-0.774402` ·
  `ASI : ASI controller limits match the file (SL {'X': -3.8475, 'Y': -4.7744} / SU {'X': 0.1525, 'Y': -0.7744} mm, tol 0.001)` · `SESSION START OK`
- **Each leg in run 4 had its own start and end** (`legs_run4.log:6-23, 48-58` for S1; `:64-81, 106-116` for P6). Same start
  lines as above. Each end read: `LIMITS TMN=0 TMX=52 SPA15=52 SPA30=0`, `PI  : ... (TMN 0.0000 / TMX 52.0000, tol 0.001)`,
  `LIMITS SL X=-500 Y=-500 SU X=500 Y=500`, `ASI : ... (SL {'X': -500.0, 'Y': -500.0} / SU {'X': 500.0, 'Y': 500.0} mm, tol 0.001)`,
  `SESSION END OK - controller limits released`. Gates MS/ME for S1 and P6: PASS.
- **Final session end 14:53:00** (`motor_session_end_final.log`):
  `LIMITS TMN=0 TMX=52 SPA15=52 SPA30=0` · `PI  : PI controller limits match the file (TMN 0.0000 / TMX 52.0000, tol 0.001) (sender code=0)` ·
  `LIMITS SL X=-500 Y=-500 SU X=500 Y=500` · `position after (must be unchanged): X=4559 Y=-37898` ·
  `ASI : ASI controller limits match the file (SL {'X': -500.0, 'Y': -500.0} / SU {'X': 500.0, 'Y': 500.0} mm, tol 0.001) (sender code=0)` ·
  `SESSION END OK - controller limits released ... motor_session.json deleted`
- Every motion went through `tools/motor_gate.py`, or through v5's own call to it inside the leg.

## LabVIEW gone
- `tasklist | grep -ic labview` gave `0` at 14:53, after the final session end.
- It was also verified gone after the build (H9) and after each leg (T3 S1, T3 P6, H at the end of the chain).

## Input md5s, start vs end (`md5_start.json` / `md5_end.json`): EQUAL 18/18
| file | md5 |
|---|---|
| D1_ring_p6_20261012_212645.vi | c2d9c13cb40c0a5cab7433896d1df157 |
| D1_ring_p5_20261010_172913.vi | 75773b0ded2a08586bb1a542ddda5af6 |
| D1_ring_p5s01_20261009_124542.vi | 7f2582ae54dc5bc42c3df0bdf3c72d2e |
| D1_s1_copy.vi | 3e3d23cefd3a334001aa9d6156bf1aee |
| RingPickSlot_v0.vi / RingSeqCheck_v0.vi | 6fcf153f7b8fecda727f5dcf944faab9 / 0295a8d349a3b61151cd87797119b9b1 |
| replay\D1_s1_replay_20260925_075422.vi | 126f84975fca9f6124432a7e4decd0c8 |
| replay\replay_get_buff_image.vi | 842ecad9a6674a5060ebb3d5522751a9 |
| replay\replay_get_image_cal.vi | afce0d04346fc58234d28bcc0fc42e55 |
| replay\replay_imaqdx_get_image_buf.vi | a89dafc1db03feef7b528f0dd4fcc692 |
| replay\replay_imaqdx_get_image_buf_paced60.vi | e40ec86722948812d155d6e4047a3ef9 |
| replay\replay_get_buff_image_paced60.vi | 59ec66b61f3518b049a3c532a8e65482 |
| original `Min_Track N beads V6_ParallelLoop.vi` | 2a78e17c449cacdaf5da389818526859 |
| G:\m8_replay_frames\frames_manifest.json | f9032ae5510e96126d9f53fc92f69cfe |
| p6_replay_frames_manifest.txt (worktree copy) | 73877ae04bd5386cac8b6aeed2d9716d |
| motor_limits.json / motor_gate.py | 65e9efae189ff0a911c9b109b19d0e69 / 0f06dd0dc937bf2959a336fb0ea23c7d |
| plans/plan_replay_swap_170.json | f3175f66039bf30a9c671caeac48582a |

No original was opened or saved. The only LabVIEW save was the replay copy under `claudeDev\bench\lean\`. No hooks file,
`motor_gate.py`, `motor_limits.json` or `CLAUDE.md` was edited.

RESULT {"p6_2": "PASS", "items": {"DISTINCT": "PASS 2538/2538 (D=20)", "MATCH": "PASS 2538 rows, 0 differ, no drop signature", "cal_outside_datetime_field": "PASS 0 bytes", "transrot_post_init": "PASS 2437 rows, 0 differ", "init_in_motor_limits_rotor_finite": "PASS 101 rows", "every_other_leg_file": "PASS (run dir 2/2, leg dirs 5/5 present in both)", "extra_B4_init_first_equal_S1": "FAIL row0 trans 21.6852 vs 0.0 (hardware readback timing; not a task item)", "S1_lost": 0, "P6_tra_rows": 2538, "build_gates": "19/0", "inputs_md5_equal": "18/18"}, "minutes": 64}
