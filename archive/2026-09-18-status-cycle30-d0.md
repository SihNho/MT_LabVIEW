---
type: archive
status: archived
date: 2026-09-18
tags: [status, cycle30, d0, lock]
---

# Cycle 30 — STATUS narrative relocated verbatim (rule 4)

## §1 — the cycle-30 dispatch-2 lock line, VERBATIM (relocated 2026-09-18 17:4x by dispatch 3)

```
  prev_purpose:   # free since cycle-30 dispatch 2 (17:02-17:06, READ-ONLY, both runs ended): diag_d0_inventory.py 7 pass/1 fail (BGRUN END rc=1 after 37s — the ONE fail is the informative measurement B1, NOT a defect) + diag_d0_trace_path.py 6 pass/0 fail (BGRUN END rc=0 after 27s). ORIGINAL md5 c39f36e0675339673b707c59f0784fee IDENTICAL before and after BOTH runs; no VI run, no motor/serial/camera, no GUI click, no scratch VI. ⚠️ LabVIEW LEFT RUNNING with the full main-VI hierarchy resident; handles 0 (not running) -> 66,449 — far above the ~31,500 idle baseline, but it is a loaded 300 kB hierarchy, not measured as a leak. Previously free since cycle-24 firefighter rerun (13:36-13:44): build_opfstunnelterm_v2.py RUN 1 = 38/38 gates PASS, BGRUN END rc=0 after 431s (tools/bench/build_opfstunnelterm_v2_run1.log). Both ops SAVED to claudeDev (OpFsTunnelTerm_v0.vi 19,869 B / OpFsInnerTunnelTerm_v0.vi 19,870 B), cold-legal (B5 both 1). Handles 30,363->30,592; all three md5s identical BEFORE AND AFTER (original C39F36E0..., V6 2A78E17C..., donor 5DC45A04...); no motor/serial/camera; one scratch created and deleted.
```

## §2 — dispatch 3 (D0 v4) full gate table

Log: `tools/bench/drive_original_copy_v4.log` — 13 pass / 3 fail, `BGRUN END rc=1 after 471s`.
JSON: `tools/bench/drive_original_copy_v4.json`, click records
`tools/bench/drive_original_copy_v4_clickrecords.json`, screenshots `tools/bench/d0_shots_v4/`.

| gate | result | detail |
|---|---|---|
| 0 G0 motor gate `--session start` | PASS | exit=0; `LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0`; `REFSTATE RON=0 FRF=1 POS=0 POS_BEFORE=0 ERR=0` |
| 1 G1 md5(ORIGINAL) before | PASS | `c39f36e0675339673b707c59f0784fee` |
| 2 G2 the D0 copy exists | PASS | `claudeDev\Track_D0_copy_20260918.vi` 471,257 B, md5 `c39f36e0…` (identical to the original — it is a plain byte copy) |
| 3 G3a apartment2 attach | PASS | LabVIEW 26.3.1f1 |
| 4 G3b ORIGINAL resident READ-ONLY | PASS | ExecState=1 |
| 5 G3c copy loads, idle, unblocked | PASS | ExecState=1; `VERDICT: clear (no modal dialog)` |
| 6 G4 panel parameters RECORDED | PASS | 60 of 60 controls returned a value, 0 errors; **nothing was written** |
| 7 G5 panel geometry derived | PASS | panel rect `(-6, 51, 1930, 1107)` size `(1936, 1056)` — **identical to v3's V6 rect, delta (0,0)**; derived image_rect `(232,500,873,1013)`, picks `[(552,756),(430,640),(690,880)]`, done `(1114,915)`, bandpass_yes_offset `(146,281)` |
| 11 run1.R2 VI left idle | PASS | ExecState left 1 within RUN_SETTLE |
| 12 run1.R3 3 bead picks | PASS | all three inside the panel rect; **`Count` across the picks: `[0, 1, 1, 1]`** — only pick 1 incremented it |
| **13 run1.R4 picking loop ended** | **FAIL** | **`Count 1 -> 1 after 303s; bandpass present=False; save present=False`** |
| 20 run2 RESTART LEG | FAIL | NOT started: ExecState=2, elapsed 345s (budget 1020s) |
| 90 G23 md5(COPY) unchanged | PASS | `c39f36e0…` -> `c39f36e0…`, exists=True (never saved, never deleted) |
| 91 G24 md5(ORIGINAL) after | PASS | `c39f36e0675339673b707c59f0784fee` |
| 92 G25 post-run `TMX?` still 39 | FAIL | gate exit=3 — `'COM3' 포트에 대한 액세스가 거부되었습니다` / COM4 likewise: **the still-running VI owned the serial ports**, so the readback could not be taken at that moment. Retried after LabVIEW exited: PASS (see §3) |

## §3 — the post-run motor readback, taken after LabVIEW exited

`tools/bench/d0v4_tmx_recheck.log`, `BGRUN END rc=0 after 2s`:

```
before: POS?=1=0.00000 TMN?=1=0.00000 TMX?=1=39.00000 ERR?=0
LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0
REFSTATE RON=0 FRF=1 POS=0 POS_BEFORE=0 ERR=0
before SL: :A X=-3.847494 Y=-4.774393   SU: :A X=0.152497 Y=-0.774402
position after (must be unchanged): X=-18473 Y=-27744
SESSION START OK
```

So the RAM-only 39 mm ceiling **survived** the run that executed the original's device init, the axis is
still `FRF=1` with `POS=0`, and the ASI limits are unchanged.

## §4 — the stop measurement (the peer's discriminating test, run for the first time)

`archive/peer/2026-09-17-d0v3-stop-heuristic.md:32` specified: write both stops `False` while idle and
read back, run, then write each `True` ONCE, no re-arm, no GUI, polling both control values and
`ExecState`. That ran here, in cleanup, while the VI sat in the **picking** phase:

```
t=60.7 ExecState=2 'stop (end)'=True 'stop (end) 2'=True frame=0
cleanup: stop -> False (NOTHING IN VI SERVER STOPPED IT) one write each: not idle in 61s;
         then 30 re-arms: not idle in 60s; ExecState=2; frame=0.
cleanup: COM Abort used in cleanup; ExecState after = 1
```

Both Booleans stayed `True` — **never consumed** — with the frame counter at 0 the whole time. In the
peer's own words that is the "persistent `True` with `ExecState=2`" branch, i.e. the stop terminals are
not read in the phase the VI was in. It does not identify that phase as the picking loop on its own,
but the frame counter never having left 0 says the experiment loop was never entered.
