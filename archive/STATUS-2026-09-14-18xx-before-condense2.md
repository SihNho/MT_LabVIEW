---
type: narrative
status: historical
date: 2026-09-14
tags: [archive]
---

# STATUS — read this first (one screen; detail lives one layer down, never appended here)

## LabVIEW execution lock

```yaml
labview-lock:
  status: acquired
  owner: Claude (session 7b982769) - AUTONOMOUS ALL-DAY LOOP, user unreachable 2026-09-14
  since: 2026-09-14 ~09:xx (quota pause 11:5x-12:0x, resumed)
  loop: >
    User: "하네스 구성해서 피어 리뷰를 통해서 오늘 쭉 루프를 돌려줘". Each cycle = peer-review the plan -> build with a
    control -> functional test -> document -> STATUS. Hard limits: zero GUI, zero edits to originals/vendor VIs,
    zero hardware. A blocked item is recorded as OPEN and the loop moves on; it never guesses to keep moving.
  scope: >
    System inventory + stage-1 analysis. READ-ONLY against the main VI (opened by reference only, never edited or
    saved - and a reference-only target never receives the walker's junk, measured). Scratch VIs under claudeDev are
    created and deleted per run. LabVIEW pid 1728 (restarted 10:52 by bench_prep).
```

## HARDWARE PERMISSION — FULL, RE-GRANTED 2026-09-13 for an unattended day (rig disassembled)

User, twice: *"프레임 지연 측정 해도 되도록 모터 다 분해해 뒀으니까 모터 사용하는 부분도 얼마든지 가동 가능. 현재 모터 가동범위에서는
하드웨어적으로 충돌 없음."* Piezo stage detached on the desk · rotor free to rotate · magnet motor full travel · camera
**on condition of restore** (`tools/bench/imaqdx_limits.py --restore`: 1280×1024, offsets 0, 90.0009 Hz; never write
`BinningHorizontal`). **CLAUDE.md rule 1b is NOT revoked** — this permission is tied to the disassembled state; ask again
in any session that does not carry this line, and stop if anything suggests the rig was reassembled. Nothing today
touched hardware.

## Where things stand (2026-09-14 14:0x) — the documentation pass the user ordered is DONE, measured

| document | state |
|---|---|
| [docs/instrument-libraries.md](docs/instrument-libraries.md) | done — ports from NI-VISA, drivers from `instr.lib` |
| [docs/main-vi-subvi-identity.md](docs/main-vi-subvi-identity.md) | **new** — 98 call sites, 56 callees, all 170 diagrams, 0 mismatches |
| [docs/main-vi-panel-map.md](docs/main-vi-panel-map.md) | 114 objects + **wiring column** (10 bare terminals) + **locals / `Value` PN census** |
| [docs/main-vi-state.md](docs/main-vi-state.md) | 3 globals, **direction measured: all 7 sites WRITE**, no reader in this hierarchy → ask the user |
| [docs/main-vi-startup.md](docs/main-vi-startup.md) | frames 1–13; frame 10 = ASI Initialize (COM4), frame 12 = ASI Get Position |
| [docs/frame-loop-wire-graph.md](docs/frame-loop-wire-graph.md) | **new, stage 1** — kernel feeders/consumers, loop border named (25 in / 6 out) |
| [docs/rotor-sign-diagnosis.md](docs/rotor-sign-diagnosis.md) | diagnosis only; the fix is a behaviour change → user |

Tools that made it possible (all functionally verified, API in [docs/toolkit-capabilities.md](docs/toolkit-capabilities.md)
top section): `subvis`, `panel_wiring`, `node_terms`, `tunnels` — cast-free array readers; `net_map` now purges its
own junk and prints progress. Data: `tools/bench/main_vi_{subvis,panel_wiring,nodeterms,tunnels,globals_direction}.json`.
Process rules added today (user: 스톨도 피어리뷰 필수, 규율에 적용): stall hook → `STALL:` record → `guard_peer` blocks the
next build until a review NAMES the failure (created after it: creation time, not mtime); gate also fires on `FAIL`
rows; net_map purge O(J²) bug fixed. **Stall detector after 4 false positives / 0 true stalls (all reviewed):** the
lifetime-CPU predicate is gone — a stall = leaf alive ∧ job log stale ≥ 90 s ∧ CPU delta ≤ 0.05 s over ≥ 60 s; long
silent phases print progress lines (net_map per node, purge per 20, bench blocks per sample).

## OPEN — recorded, not guessed  (→ for the user, in Korean: [docs/questions-for-user-2026-09-14.md](docs/questions-for-user-2026-09-14.md))

- **Shift registers** of the frame loop (54 unresolved half-edges = the per-frame state carriers): ~~needs a cast~~
  **CAST SOLVED 15:1x without GUI (INDEX row 28):** `loop_cast(main, 1, 'WhileLoop')` returns the frame loop's
  **14 shift-register UIDs**; `OpShiftRegs_v0` (15:3x, `test_opshiftregs.log`) reads each one: they are the 14
  **RIGHT** registers, named by their inside terminal (`x,y,z array out`, `position [internal units]`, `VISA out`,
  `total data array out`, `error out`, `LastBufferNumber`, `pos in cal image out`, `Bead is good? array out`,
  `F-x out`, `Value` ×2, `System no.`, 2 unnamed) with their body-side feed wires; 4 final values leave the loop.
  **CLOSED 15:4x (INDEX row 29):** `OpShiftRegs_v1` (8/8) adds the LEFT side — every register has exactly one left
  (no stacking), 13 of 14 initialised from diagram 19, each left's inside terminal is the body's source. Both measured
  sections are in docs/frame-loop-wire-graph.md (the name-pairing heuristic is superseded); summary in
  docs/main-vi-state.md. **Stage-1 wire graph closed 15:5x:** all 83 one-sided wires of the body are accounted for
  (29 frame-loop tunnels, 22 shift registers, 7 nested-structure tunnels, 17 panel terminals — measured; 8 constants
  by elimination). **18:1x `OpLoopCast_v1` (INDEX row 30, 7/7):** no loop of the original runs parallel (0/17; one
  stores a dormant P=12); `PARALLEL_kernel_v3` reads enabled/P=4, so the CPU-parallel benchmarks stand. Nothing is running.
- ~~9 bare-terminal panel objects unattributed~~ **ATTRIBUTED 14:5x** (offline, from the sweep + a node-class census):
  the main VI has 21 `ControlReferenceConstant` nodes — single-terminal source nodes named after their panel object —
  and 9 of the 10 bare-terminal objects are reached through them (explicit property nodes / event registrations;
  docs/main-vi-panel-map.md, "Control references" section). ~~Only `Rot \nSpeed` … candidate legacy leftover~~
  **CLOSED 14:5x (INDEX row 27):** `OpNodeLabels_v0` (`Node.Label` = an implicit node's header, cast-free) attributed
  **88/88 implicit `Value` nodes** to 45 panel objects; `Rot \nSpeed` is READ twice (diagrams 32/111, next to the
  rotor `SetCommand.vi` calls) → **not legacy**; nothing on the panel is unattributed. Question 2 for the user withdrawn.
- ~~IMAQ Image Display route unmeasured~~ **MEASURED 14:1x (INDEX row 25)** after building `OpConnectCtl_v0`
  (`gscript.connect_ctl`: Terminal.Connect Wire on a panel object's own terminal — the fleet's first way to wire a
  Vision control): Image Display terminal **+1.0 ms closed / +6.9 ms visible** vs Picture route 2.9 / 8.0 → use the
  Image Display inside the decimated display loop; the visible paint (~7 ms) is the cost either way.
- `Global motor pos.vi` has **no reader** in this hierarchy (write-only): read elsewhere or legacy? **User decides.**
- Rotor zero meaning; rotor read parse (unsigned) fix — **user decisions.**
- ~~Handle count grows ~+0.9 per `Open VI Reference` on the main VI~~ **CLOSED 14:2x by the peer's matrix**
  (`tools/bench/handle_growth_matrix.log`): `report_all` +1.0/run and `subvis` (6 element refs/run) +0.96/run are the
  same, `node_terms` −1.0/run, a small VI 0.0; the first block's +2.5k was the main VI loading and returned after
  30 s idle. Churn, not a per-op leak; the day's ~5,000 op runs left 34.1k vs the 31.5k fresh baseline (loaded VIs
  included). Keep the per-op 20-run rule and `bench_prep`'s restart-above-limit.
- `Constant.Value` (VISA literal on frame 10) unbuilt (needs a Constant-typed ref = the cast seed). ~~`Cal Zero`
  legacy status~~ in use: indicator wired + 2 implicit `Value` reads (diagrams 21, 100; panel-map last section).

## Work order (user, 2026-09-13) — restructuring LAST

```
1. TOOLING  done  ->  3. GATES G4/G7/G8/G9  ->  4. MEASUREMENTS array-crossing · display path  ->  5. USER DECISIONS
                                                                       ->  2. RESTRUCTURE stages 0-6 (stage 1 first pass done)
```
Decided by the user: two separate top-level VIs (CPU / GPU); rotor = 4th row of `CycleSchedule`, absolute degrees,
translation then rotation; `Value` property nodes → locals by rule; rebuild the seven-loop top level fresh from the
wire graph (positions are meaningless: Clean Up Diagram). Plan: [docs/restructure-plan-4.6.md](docs/restructure-plan-4.6.md).

**Work-order measurements DONE today** (all functional on the fixture; reports in `archive/bench-2026-09-14-*/`, catalog
`archive/benchmarks/INDEX.md` rows 22–27):

| gate / question | result | row |
|---|---|---|
| display path (Picture route) | construction 2.7 ms CPU/frame; **visible paint ≈6.5 ms** → decimated `Last`-mode display loop | 22 |
| IMAQ Image Display route | +1.0 ms closed / +6.9 ms visible (vs Picture 2.9 / 8.0) → use it in the display loop | 25 |
| G4 image copy | cold `IMAQ Copy` 0.4 ms (= allocation), **steady state 0.05 ms** (linearity at N 1024/1280 PASS) → pool + copy-on-demand | 23, 26 |
| G9 kernel core budget | par kernel +0.3 % with one physical core removed (A-B-A affinity) → PASS; loop-level G9 waits for stage 2 | 24 |
| implicit `Value` nodes | `Node.Label` reader: **88/88 attributed**, `Rot \nSpeed` in use | 27 |

Tool gains (NAMES.md / toolkit-capabilities.md): a For loop's N wired by script (`connect_terminals` onto the loop
node's single unnamed sink); `node_labels` = cast-free node identity (bound control / VI file / primitive type).
Remaining before stage 2: **user decisions** (rotor zero; rotor sign fix; who reads `Global motor pos`) and the cast
seed (one GUI act, a session with the user). **Loop status 14:5x: everything unattended-doable is measured; LabVIEW
stays reserved by this session.**
**15:0x — GUI-free cast seed, in progress:** codex confirmed (NI doc) that TMSC `target class` accepts ANY wire of
the target type, so a ForLoop-typed refnum control is a seed. Attempt 1 (`build_oploopcast_v0.log`) stopped: erdosmiller
`Create For Loop.vi` has no ForLoop-typed output (recorded). Attempt 2 under review (`peer_loopcast_seed2.log`): take
the seed from NI's example `VI Scripting with Structures - For Loop.vi` (scratch copy) via Create Control + `copy_into`.
**15:1x — THE SEED WORKS (functional, `test_oploopcast.log` 9/12):** `OpLoopCast_v0` (seed = a ForLoop refnum control
made by Create Control on a ForLoop property node's `reference` input in a scratch copy of NI's Structures example,
moved by `copy_into`) recovers HARNESS_copyloop's N wire 346 and resolves all 17 ForLoops of the main VI (N wires,
`Loop.Shift Registers[]` counts). The 3 FAILs were one fact (the frame loop is a **WhileLoop**; a ForLoop seed cannot
cast it) → `OpWhileCast_v0` built and **13/13 PASS** (frame loop: 14 shift registers). **The 'one GUI act' deferred
item is closed without GUI** (toolkit-capabilities.md seed section; INDEX row 28). Nothing is running.

History of this day and every earlier state: `archive/STATUS-2026-09-14-full-before-condense.md` (unread by default).
