---
type: plan
status: proposed
date: 2026-09-18
kind: build
tags: [motor, safety, envelope, coerce, assembled-rig]
---

# Motor-limit assurance for VIs WE build — the plan for its own session

**Why this exists.** On 2026-09-17 the user confirmed by live test that commands sent from OUTSIDE LabVIEW are
bounded (`tools/motor_gate.py`: PI 30/35 moved, 40 refused; ASI ±0.4 mm moved, ±2 mm refused — STATUS.md
HARDWARE). Then: *"그렇다면 LabVIEW 코딩에서 상한 하한 관련 실수가 없는지도 확신이 필요함."* The gate cannot see a
move made INSIDE a VI. The user approved all of the below (*"1~3번 모두 필요한 내용이고, 추가 고정제한도 있으면
좋음"*) and asked that it run in **a separate session** (*"이를 위한 별도의 세션이 있는것이 좋지 않을까?"*).

## The envelope (user, 2026-09-17 — memory `motor_safe_motion_envelope.md`)
ASI up/down: no limit · ASI x/y: never home/origin, ≤ 1.0 mm from the anchor (`tools/bench/motor_anchor.json`) ·
PI magnet: 0–39 mm (`Max Trans Pos` = 40.94, applied in the original by a **coerce**; the controller's own `TMX?`
is **52**, measured — it protects nothing). Rotor: no envelope declared yet.

## Pre-decided (apply, cite the number, do not re-ask)
1. **Build all three checks**: (A) wiring check, (B) fake-motor run, (C) run gate.
2. **The extra fixed clamp IS approved** — a user-granted, narrow exception to rule 1a: directly in front of the
   motor-moving subVIs in OUR VIs, clamp PI targets to 0–39 and refuse ASI home/origin. Inside the envelope the
   output must be bit-identical to the original; it may differ ONLY for values outside it. It goes into copies
   under `user.lib\claudeDev`, never into an original (rule 1).
3. The original's own coerce stays exactly as it is (40.94). The 0–39 clamp is an ADDITION, not a replacement.
4. Rig state is 조립; motors are allowed only inside the envelope. Nothing in this plan needs a motor to move:
   A is offline, B uses stubs that open no port.
5. `drive_original_copy.py` stays blocked by `guard_bash.py` until C exists; C replaces the blanket block.

## A — wiring check (static, LabVIEW not run)
For EVERY motion call site in the built VI (`MOV.vi` ×7, `VEL.vi` ×4, `GOH`, ASI `Move Axis to Position.vi` incl.
the startup move on diagram 10 — `docs/main-vi-startup.md:33`, rotor `SetCommand*`; census first, do not trust
these counts), trace the position input BACKWARDS to its sources and compare with the same trace in the original:
same coerce node on the path, its upper-limit input fed from the same `Max Trans Pos` source, no path that reaches
the subVI without passing the coerce, no limit input left unwired/defaulted. Output: one row per call site,
PASS/FAIL, machine-readable. Any difference from the original = FAIL.
**Also report, as facts for judgement: call sites where the ORIGINAL has no limit at all** (the known candidate is
the startup ASI move) — that is where pre-decided 2 matters most.

## A.1 — HOW check A is measured (method, redesigned 2026-09-18; §A above is unchanged)

`archive/peer/2026-09-18-priorart-check-a-wiring.md` stopped the first design with `unread-evidence` /
`contradicted` / `helper-exists` / `already-measured` ×2. Every load-bearing citation was opened and verified
verbatim; all four findings are correct. This section is the method that replaces the design they stopped — it
changes HOW §A is measured, not WHAT §A requires. Cycle-19 judgement session.

1. **Forward from the limits, not backward from 43 sites.** The whole main VI holds exactly three
   `In Range and Coerce` nodes — d13 uid 790, d73 uid 25455, d88 uid 41725 (`docs/NAMES.md:319`; label scan of
   all 170 diagrams; `Array Max & Min` d43 uid 10969 is the frame loop's bead minimum, not a limit). So **at most
   3 of the 43 in-scope sites can be `COERCE_ON_PATH`**, and the candidate set is enumerable in one op run
   instead of 43 independent backward walks. Reachability is then tested from those 3 nodes outwards.
2. **No limit lives in a callee — measured, so check A never descends into a motion subVI to find one.**
   `tools/bench/probe_motion_limit_labels.py` (2026-09-18): `MOV.vi`, `VEL.vi`, `GOH.vi`, ASI
   `Move Axis to Position.vi`, ASI `Move Axis Relative.vi`, Autonics `SetCommand.vi`,
   `Motor control v5_No Recording.vi`, `ASI_adjust focus-subvi.vi` — **zero** limiting constructs each.
   `Max Trans Pos.vi` has **no nodes at all**: it returns a constant, so the coerce is always in the caller.
3. **The flat-sequence border IS crossable — the old blocker was misdiagnosed.** `already-measured` rested on the
   continuation rule terminating on 32 of the 43 sites (`docs/d1-build-plan.md:791-797`, re-measured 2026-09-20, was `:733-739`). Measured this cycle
   (`tools/bench/probe_flatseq_walk_run2.log`, `tools/bench/probe_flatseq_outer.log`): the barrier is
   `Diagram[d].Nodes[]` **addressing**, not LabVIEW — the tunnels are Traverse-visible (518 `FlatSequenceInnerTunnel`,
   58 `FlatSequenceOuterTunnel`) and UID-addressable, and expose `OuterTerminal` / `InnerTerminal` / `Frame`
   (3195B800/1/2) and `LeftTerm` / `RightTerm` / `LeftFrame` / `RightFrame` (1C3A9000-3). Check A therefore does
   **not** inherit the terminating rule; it needs one new primitive, the **UID-addressed tunnel reader**
   (`UID → TMSC(FlatSequence*Tunnel) → Outer/Inner terminal`), which is built and proven on a live instance
   BEFORE check A runs. Attaching an id to a class is not yet a live read on an instance.
4. **Consume the caches; sweep only what has none.** `tools/bench/main_vi_nodeterms.json` (170 diagrams / 626
   nodes / 3,328 terminals) and `tools/bench/diagram_tree_main.json` already hold steps 2–3 for the V6 copy;
   validate by md5 (`2a78e17c449cacdaf5da389818526859`), do not re-run `node_labels` per diagram.
5. **Reuse the two helpers instead of hand-rolling the join:** `tools/bench/diag_tunnelsource_onehop.py` (the
   cross-border hop, already built and run) and `tools/bench/wiregraph_frame_loop.py` (offline wire-uid join +
   backward slice, no LabVIEW run). LabVIEW is touched once per BORDER, not once per wire. The resolved hop
   `LoopTunnel #28343 → Max Trans Pos.vi · Magnet position output` (`docs/frame-loop-wire-graph.md:264`) is the
   walker's known-good fixture, not something to re-derive.
6. **`net_map()` stays unused, for the reason that survives.** "It pours junk into an original" is **withdrawn**
   (`docs/NAMES.md:332-339`, `docs/toolkit-capabilities.md:76-77`: a reference-only read never receives junk).
   The surviving reasons are that its purge has no positive evidence of deleting
   (`archive/2026-09-16-status-gate-a1-delete-regression.md:143-144`) and cost — 0.8 s/node vs ≈8 s/node.
7. **A limit need not be a node — and a node-only scan would report the original UNBOUNDED when it is not.**
   A LabVIEW numeric control's **Data Entry range** coerces out-of-range values and appears in no `Nodes[]` list.
   Check A must therefore also read the data-entry limits of every control feeding an in-scope site before any
   site is classified `ORIGINAL_UNBOUNDED`. Not yet measured; it is a required input to that classification.
8. **Baseline = the 3StateClamping ORIGINAL** (`tools/bench/motor_census_3state-ORIGINAL.json`, md5
   `c39f36e0675339673b707c59f0784fee`), which the 43 site identities are keyed to. The V6 working copy is not
   pristine — Claude inserted a per-frame TIFF writer into it on 2026-09-01, and its census reports 98 sites to
   the original's 97 — so a baseline drawn from V6 begs §A's question. V6 stays the development fixture (it has
   the cache); the ORIGINAL needs its own read-only node/terminal sweep (~11 min), and the ORIGINAL-vs-V6 row
   diff is itself a recorded finding.
9. **Default-deny is unchanged**: a site whose trace cannot be completed is `UNTRACED` — in scope, never dropped,
   never counted PASS, with the missing primitive named. The three comparator mutation negatives (coerce deleted,
   limit wire cut, second un-coerced path) are untouched by this redesign and remain required.

## B — fake-motor run (functional)
A copy in which each motion subVI is replaced by a stub with the identical connector pane that opens no port and
appends (call site, command, value) to a log. Drive the panel with deliberately out-of-range inputs (magnet 45,
−3, 40.95, NaN; large ASI steps; home button) and in-range ones. Prediction contract, stated before the run:
every logged PI target ∈ [0, 39]; no ASI home/origin command logged; in-range inputs produce values identical to
the original copy run through the same stubs. Level of verification: FUNCTIONAL for the limit path only.

## C — run gate
A record file written only by A+B passing for a given VI (path + file hash). The run scripts refuse to run a VI on
an assembled rig without a matching record; a changed hash invalidates it. Self-test without hardware, like
`tools/bench/selftest_motor_gate.py`.

## D — the checker is a SEPARATE sub-session, and the builder cannot certify itself (user, 2026-09-17: "그 구성으로 적용")
The user: *"main vi 혹은 모터 가동하는 vi를 만들었을 때, 모터 리밋이 정상적으로 걸리는지를 체크하는 하위 세션이
꼭 필요"*. Approved design, all four parts:
1. **Agent `.claude/agents/motor-limit-checker.md`** (written 2026-09-17; Opus high). Input = one VI path, never
   the builder's explanation. It runs A and B and returns a per-call-site table. It never builds or edits a VI.
2. **Mechanical trigger.** "Can reach a motor" = the VI's hierarchy calls at least one motion subVI (decided by the
   census tool, not by a person). Such a VI needs a pass record carrying its **file hash**; C refuses to run it on
   an assembled rig without one; any re-save changes the hash and voids the record.
3. **The builder cannot write the record.** Only the check tool writes it; a hook refuses any other write to the
   record path (Edit/Write/shell redirect alike). Without this, 1 and 2 still leave self-certification open.
4. **The check tools are proven on BROKEN VIs first.** Build deliberately faulty scratch VIs — coerce removed,
   upper-limit wire cut, limit defaulted to 0, a second un-coerced path to `MOV.vi`, an ASI home call — and
   require every one to FAIL. A checker that misses one is not used. (Same class of hole as 2026-09-17's gate
   self-test, which never loaded the real anchor file and so missed the BOM bug.) Scratch VIs are created and
   deleted in the same operation.
**Build order:** census → A → B → broken-VI proof (4) → C + record hook (2, 3) → first real use of the agent (1).

## P2 live findings (user present, 2026-09-18 14:4x, D0 plain copy `Track_D0_copy_20260918.vi` running)
- **The original's magnet limit is NOT a coerce in front of the motor command — it is the panel control's
  Data-Entry range** (user, watching the rig: *"컨트롤 패널에 상한 하한이 잡혀 있어서, 값이 갱신될 때 상한 하한으로
  들어감. 모터 입력값 앞에서 코어스 잡혀있지는 않은듯"*). Input 45 via `Trans Step (mm)` + `Send to Trans` stopped
  at **40.84** (not the documented 40.94 — the control's own max; the 0.1 mm gap is unexplained). Input −50 → the
  control itself became **0** and `Trans Pos` 0: so `Trans Step (mm)` is an ABSOLUTE target despite its name, with
  Data-Entry range **0 … 40.84**; both bounds live in the control, nothing in front of `MOV`.
- Consequence: a Data-Entry range coerces only values typed on the panel. Values written by **VI Server**, local
  variables or wires are NOT coerced — exactly how the unattended harness sets panel values. So §A.1 item 7 is
  confirmed as the real limit mechanism, and **pre-decided 2 (the fixed clamp in front of the motor subVIs) is
  mandatory, not optional**, for every VI we run unattended.
- Startup: the copy loaded without a "Find the VI" dialog only with the original preloaded read-only
  (`tools/bench/p2_open_copy.py`); md5 of the original identical before and after.
- **CONTROLLER-SIDE SOFT LIMITS WORK ON THE C-863.11 — MEASURED 14:5x** (`tools/bench/p2_pi_softlimit_test.log`,
  `…_test2.log`; search `archive/peer/2026-09-18-pi-c863-soft-limits.md`): `SPA 1 0x15 39.0` + `SPA 1 0x30 0.0` →
  `TMX?`=39, `TMN?`=0; **`MOV 1 40` → ERR 7, no motion; `MOV 1 38.5` moved; `MOV 1 0` back.** RAM only (lost at
  controller power-cycle; `WPA 100 1 0x15` / `… 0x30` would persist — NOT done). Side finding: after the user's
  D0 run + stop, the axis read `RON 1 / FRF 0` (all moves ERR 5); the original's own mode (Autoreference?=0) is
  `RON 1 0` + `POS 1 <z>`, restored by `tools/bench/p2_pi_ron_off.ps1` — no reference move needed. OPEN: does the
  original's startup init reload stage parameters and overwrite 0x15/0x30? Read `TMX?` after the next D0 run.
- **ASI**: `SL`/`SU` (mm) are controller-side limits, stop motion at the boundary (also HOME and joystick),
  persist across power cycles automatically, and follow the coordinate zero (`archive/peer/2026-09-18-asi-soft-limits-sl-su.md`).
  Axis-direction caveat: read current `SL?`/`SU?` before setting.
- **User's design (14:5x–15:1x): a session-start hook SETS the controller limits and verifies them; a session-end
  hook RELEASES them** (PI back to 0–52, ASI back to ±500); the gateway refuses to transmit while the readback
  differs. Abnormal exit leaves limits in place (the safe direction).
- **ASI LIMITS WRITTEN 15:1x, user-ordered ±2 mm around the live position** (`tools/bench/p2_asi_set_limits.log`):
  `SL X=-3.8475 Y=-4.7744`, `SU X=0.1525 Y=-0.7744` (readback ≈ ±0.5 µm rounding); position unchanged; persistent
  in the ASI controller. Undo: `SL X=-500 Y=-500`, `SU X=500 Y=500`. SL/SU are ABSOLUTE coordinates.

## Deferred to the FINAL LabVIEW code (user, 2026-09-18 19:0x)
- After the D0 v5 run the magnet sat at 30 mm (the original's startup `If no: current pos z?` = 30). The user:
  *"0으로 되돌릴 필요는 현재 없음. 가동 범위 안에서만 움직이면됨. 나중에 LabVIEW 코드 최종화할 때 이야기할 부분인 것
  같음. (시작시 PI 모터 0으로 복귀)"* — so: no return-to-0 now; **"PI motor returns to 0 at startup" is a design
  item for the final VI (D1/D2 finalisation), to be discussed with the user then**, not a harness step.

## Open for judgement (not for a material session to decide)
- Where exactly the fixed clamp sits when a motion subVI is called from several loops (one wrapper VI vs per site).
- What to do with a call site where the original itself is unbounded.
- The rotor's envelope (user has not given one; `motor_gate.py` refuses all rotor motion meanwhile).
- The ASI distance test is radial (hypot ≤ 1 mm); the user was asked whether per-axis ±1 mm was meant — unanswered.
