---
type: archive
status: history
date: 2026-09-17
cycle: 15
tags: [status-narrative, relocated]
relocated_from: STATUS.md
---

# STATUS narrative relocated 2026-09-17 (cycle 15) — the long forms of OPEN 13–21

Rule 4 / CLAUDE.md's 100-line threshold: STATUS.md had grown to 165 lines again after cycle 15's D1 work. The
entries below are **moved verbatim**, not rewritten. STATUS keeps a one-line pointer for each. Open this file only
when a line there is ambiguous.

## §1. OPEN 13 — the frame loop's stop (CLOSED 2026-09-17)

13. ✅ **CLOSED 2026-09-17 — the reader was BUILT and the stop is MEASURED.** `OpLoopEndRef_v0.vi`
   (`WhileLoop.Loop End Ref` **6362C00**, short name `LpEndRef`, id now verified on this machine) reads
   **#637 → conditional terminal uid 648 → wire 3457 → source `CompoundArithmetic` #11639** = `stop (end)` uid 7
   OR-ed, all inside `Diagram#639`. `stop (end) 2` #19587 → #17883 → `Tunnel#22085` of `CaseStructure#22082` is a
   SEPARATE path. 16/16, MAIN md5 unchanged (`tools/bench/build_oploopendref_v0.log`, `loopendref_637.json`);
   also #25380→25410/1737 and #15173→15276/19456. → `docs/main-vi-stop-and-save.md` §1. **This is D1's S4 gate.**

## §2. OPEN 14 — the cycle-15 prior-art review, partly disposed

14. 🔴 **The cycle-15 prior-art review is only PARTLY disposed** — A1/A2 `settled-already`, A3–A6/B2 `contradicted`,
   A7/B3 `unread-evidence` BLOCK on purpose (D1's method vs `decisions.md:19`; `SubVI.Replace` 635E001 unverified).
   **Only a judgement session may refute or fix those.** → `archive/2026-09-17-status-d0-and-gpu-narrative.md` §2.

## §3. OPEN 15 — bgrun --detach

15. ✅ **`bgrun.py --detach` BUILT and MEASURED** (deadline + END/TIMEOUT survive detachment; `BGRUN KILL` line;
   detached stdout → the log). 15b. 🔴 **its deadline kill does NOT kill an ORPHANED grandchild**
   (`detach_canary.log`) — pre-existing; the Job-Object fix is a **judgement call**.
   → `archive/2026-09-17-status-d0-and-gpu-narrative.md` §3.

## §4. OPEN 16 — the GPU divergence, localised

16. 🔢 **GPU N1, full fixture: max |Δx| 4.13e-06 px · |Δy| 3.13e-05 px · |Δz| 1.28e-05 µm · 1 flip** vs acceptance
   `decisions.md:38` (x,y ≤ 1e-6, 0 flips) ⇒ **x/y and the flip are OUTSIDE it**. **LOCALISED 2026-09-17**
   (`docs/gpu-backend.md` §2026-09-17, raw `tools/bench/gpu_n1_deltas.json`, 8/8 gates): every x/y exceedance is
   **bead 4 on 10 frames of f11805–f11823**, in the all-beads-lost tail, interleaving the 13 recorded lost rows;
   **over the first 10,018 frames max |Δx| 4.86e-07 · |Δy| 4.68e-07 · 0 exceedances**; the flip is k1679/f1937
   bead 4, one cal slice (Δz 4.7 nm); **two runs bit-identical**. 🔴 **Acceptability is a JUDGEMENT call.**

## §5. OPEN 17 / 17b — D0

17. ✅ **D0 CLOSED — the original's full unattended cycle RAN, 16 pass / 0 fail** (`drive_original_copy_v3.py`,
   HWND-gated clickprobe, `SetControlValue` stop → idle in 2 s, `tra001-000` written, md5 unchanged).
   → `archive/2026-09-17-status-d0-and-gpu-narrative.md` §5.
17b. 🔴 **v3's R11 never gated on the stop** — `rec(..., left2, ...)` (`drive_original_copy_v3.py:415-418`) scores the
   *restart*, and `reset_controls()` runs only at line 248, so "stop works only in the frame loop" is **UNPROVEN**
   (peer `…2026-09-17-d0v3-stop-heuristic.md`, ANSWERED, adopted). Next D0 step is its VI-Server-only test: stops
   `False` + readback → restart → one `True` each → poll values + `ExecState`.

## §6. OPEN 19 — D1 rev 2 and its ten prior-art findings

19. 🔴 **D1 REV 2 (`docs/d1-build-plan.md`) is written and prior-art-reviewed; the build did NOT start.**
   `archive/peer/2026-09-17-priorart-priorart-d1-build.md` — **10 findings, 0 novel, all accepted and disposed**
   (`FIXED:` ×6). The two that change the cycle: **(A1+A6)** relocating a plain primitive or a subVI call is the
   *settled* route (`decisions.md:19`, `restructure-plan-4.6.md:79-81`, and `tools/recipes/probe_relocate_route.py`
   asked this in cycle 8) — so D1's ONLY real unknown is **relocating a STRUCTURE WITH ITS CONTENTS**
   (`#5540 #2222 #12589 #10407 #1359 #29874`), whose documented route is `Make Selection` 0x6349002 →
   `Copy Selection` 0x6349003 → `AbstractDiagram.Paste` 0x6375400 (`vi-scripting.md:323-325`) and **has never been
   run here**; **(A4)** `#10407` (autofocus) is in the kernel's forward slice and **neither placement is legal** —
   tracking loop = VISA on a path whose stall makes acquisition skip reads (rule 1c / `decisions.md:30`),
   acquisition loop = its input no longer exists. 🔴 **JUDGEMENT.** Also A5 (writer must STREAM, not relocate the
   accumulator), A3 (`#11639` AND `#17883` are two nodes; `CaseStructure#22082` unplaced), A2 (row 1.7 before the
   per-frame measurement `decisions.md:46,:52`).

**All five of these were decided by the judgement session on 2026-09-17** and are written into
`docs/cycle15-plan.md:42-57` and `docs/d1-build-plan.md` REV 3 §0.

## §7. OPEN 19b — phase P, runs 1–3 (superseded by rev 7 and its own §2a table in the D1 plan)

19b. 🔴 **Phase P RAN TWICE and the QUESTION IS STILL UNANSWERED — failure budget 2 spent, handed to judgement.**
   `tools/recipes/probe_move_into_v0.py` (now REV 6) never reached P2/P3; both runs died in **phase 1**, building
   `OpMoveIn_v0`. Run 1 (`log:78-80`): `net_map` returned 4 of the U2G subVI's 12 terminals and the VI-reference
   input is named `Owning VI` — harness, fixed. Run 2 (`log`, last block): **every requested wire was made**, new
   gate **P1a** proves `Move.owner` is now carried by a wire sourced from the Diagram cast uid 683 (the run-1
   defect the review caught is really gone), the U2G chain is wired, and `OpMoveIn_v0` still reads **ExecState 0**
   after `set_auto_error_handling(False)` + `remove_bad_wires_scripted`.
   🟢 **CAUSE MEASURED, and it was the PEER's explanation, not either of mine** (`archive/peer/2026-09-17-
   moveinto-p1-execstate0.md`, codex, ANSWERED; test `tools/bench/diag_movein_p1_break.log` 5/5, 2 s, read-only):
   **wire 464 is ONE NET with one source `IndexArray#236` and THREE sinks — `Property#237`, `Property#240`,
   `Invoke#741`.** The probe deletes the whole Wire object to bare `Move.reference`, so it also bares the
   **required** `reference` inputs of #237 and #240 → no broken wire, nothing for Remove Bad Wires, ExecState 0.
   My hypothesis (A) is **FALSIFIED**: `report_all('Invoke')` is `[741]` on both donor and OpMoveIn_v0 — zero
   extra creator junk. 🔴 **JUDGEMENT: the repair** — bare only the Move's own terminal, or re-wire
   `#237.reference` / `#240.reference` from `#236` after the delete. Both change the probe's construction and its
   budget is spent. **Cost note for the retrospective: FIVE prior-art rounds** (`priorart_loopendref`, `…_rev2`,
   `moveinto_rev4/5/6`) on this one probe, ~45 min; rounds 2–4 each found a genuinely run-breaking defect
   (name-keyed terminals · a cached Traverse index · a missing Invoke purge), round 5 returned `novel`.

## §8. OPEN 20 / 21 — cycle 14's retrospective and the round-5 devices

20. 🔴 **Cycle 14's retrospective ran** (`archive/peer/2026-09-17-retrospective-cycle14.md`, ANSWERED) and left
   **two slugs DUE, which now BLOCK every recipe build**: `repeated-failure-class` 7/3 (the 2026-09-16 disposition
   gate **failed at its in-flight edge**) and `device-failed` 1/1 (the `unreported-fact` runner-exit device let
   `diag_stop_condterm_panel.log:15-18` end **rc=0 with a failed gate**). Each needs a dated `DECISION:` block in
   `docs/violation-decisions.md`. Its finding 7 also flags *judgement taken inside material sessions*.
21. ✅ **Round-5 devices BOTH BUILT 2026-09-17** (`docs/violation-decisions.md` 03:38). (a) `device-failed`:
   `tools/bgrun.py` now scans build/diagnostic logs for `^\s*(?:->\s*)?FAIL\b` and forces rc=1 —
   `tools/bench/selftest_bgrun_fail_scan.log` **7/7**, incl. the literal `diag_stop_condterm_panel.log:15-19`
   lines ending rc=1 where they used to end rc=0, a PASS-only log still rc=0, `FAILED`/`FAILURE`/`failures` not
   tripping it, and a `peer_*.log` still exempt via logclass. (b) `repeated-failure-class`: `OpLoopEndRef_v0`,
   OPEN 13 above.

## §9. OPEN 1–12, 18 — the older items STATUS still points at

1. 🟡 **PERIODIC auto-reset not gated by `Auto-Reset` at the wire level** (`ForLoop#1359`, 10 terminals, 0 panel sources); one `Value` read inside #1359 closes it. → 2026-09-16 archive, OPEN 1.
2. 🟢 **Autofocus CLOSED** — `Auto-Focus` uid 24266 stops the piezo; `CaseStructure #10407` every 25 frames ≈ 3.6 Hz.
2c. 🟢 **uid 9775 READS camera geometry** (the size written is the panel display area, not the ROI) ⇒ the 1280×1024 budget basis is safe. Residual: `Property Items[] → Is Write` over the 106 Property nodes.
3. 🟡 **Peer-archive dispositions** — 39 pre-09-15 `legacy`; **27 are real debt** (L6); L1: 64/336 docs lack frontmatter.
5. **Startup drives instruments** (ASI diagrams 10/88, PI 1/3/4/5 — `main-vi-startup.md:22-33`): fine while apart, a hard blocker at assembly; excise node-by-node (rule 1a).
6–8. ✅ RESOLVED — bgrun regex, REVIEW-log scan skip, `premature-build`/`scope-creep` devices. 4. `Global motor pos.vi` write-only; **user: keep it**.
9. 🟢 **A2 DONE** — owner semantics, six structure classes (54/54); `FlatSequence` the exception (owner uid 0, error 1055). `docs/diagram-hierarchy.md`.
10. 🟢 **A3 MEASURED for the 112 clean diagrams** (100 agree / 0 disagree); left: the 57 `FlatSequenceFrame` diagrams, reachable via `FlatSequence.Diagrams[]` **3578BC00**. 🟡 Needs ONE new op VI — judgement call.
11–12. ✅ **Retrospective v2 ADOPTED** (A–E closed, `violations.py --due` empty rc=0); **doc lint + ingest BUILT**, but
   MEASURED 2026-09-17: **2 fail / 4 warn / 3 pass** — 🔴 L4 *two* `current` cycle plans (14 + 15) and L6 27 undisposed
   reviews; the "1 fail/3 warn/5 pass" figure is stale. → archive §2.
18. 🔴 **The original saves EVERY FRAME as a 1.3 MB TIFF** (`IMAQ Write TIFF File 2` #22700, diagram 43) —
   **~118 MB/s at 90 Hz**. Any unattended overnight harness must bound this or the disk fills in minutes.

## §10 — relocated verbatim from STATUS.md, 2026-09-17 (material/cycle15-d1-build; STATUS was 135 lines)

Rule 4: nothing deleted, only moved. STATUS keeps one line and a pointer for each of these.

13. ✅ **CLOSED — the frame loop's stop is MEASURED**: `#637` conditional terminal **uid 648 ← wire 3457 ←
   `CompoundArithmetic #11639`**; `stop (end) 2` #19587 → #17883 → `Tunnel#22085` of `CaseStructure#22082` is a
   SEPARATE path. `OpLoopEndRef_v0.vi`, 16/16. → `docs/main-vi-stop-and-save.md` §1; archive §1.

19b. ✅ **PHASE P ANSWERED, 12 pass / 0 fail, 14 s** (`tools/bench/probe_move_into_v0.log`, rev 7c).
   **`GObject.Move` with a wired `owner` reparents `CaseStructure #12589` WITH ITS CONTENTS** into a new While
   loop's body on Diagram 19 — owner `Diagram#1170` → `WhileLoop#1133`, **Diagram count 171 → 171**, Node 626 →
   627, control arm `#8885` likewise. So the `Make Selection`/`Copy Selection`/`Paste` op family is **NOT needed**
   (it would also have required a GObject-ref array constructor the fleet does not have). ⚠️ **The move CUTS the
   border wires** (Wire 1902 → 1895, LoopTunnel 132 → 130), so D1 must re-wire afterwards and `ExecState` is
   meaningful only at the end. `OpMoveIn_v0.vi` is BUILT (ExecState 1, UID control `'UID 3'`). Runs 1–3 → §7.

22. ✅ **NEW — `guard_cycle.premature_build` (b) now applies only to a recipe's FIRST run after its review.** If a
   build log `tools/bench/<recipe-stem>*.log` is newer than the newest prior-art archive, a re-run is allowed; a
   failed prediction is `guard_peer`'s gate, not this one. With **no** prior-art review archived it still blocks.
   Self-test `tools/bench/selftest_guard_cycle_rerun.log` **4/4** (first-run→refused · re-run→allowed ·
   no-review→refused · regression review-newer→allowed). `_rel()` added so a cross-drive path cannot crash the hook.

23. 🟡 handle count jumped 30,849 → 51,530 in one 14 s probe run (baseline ≈31,500). **CLEARED 2026-09-17**: the
   step-0 run restarted LabVIEW at its top (51,220 → 37,290). Attribution to an operation type is still a one-run
   `tools/bench/handle_audit.py` job, not a build item.

### §10a — D1 step 0, the full result (STATUS keeps four lines; `docs/d1-build-plan.md` §0-MEASURED keeps the tables)

`tools/bench/diag_d1_step0.log` 12/12 in 35 s (LabVIEW restarted first, 51,220 → 37,290 handles; MAIN md5
`2a78e17c449cacdaf5da389818526859` before **and** after), plus `tools/bench/diag_d1_step0_reclass.log` 8/8 — an
offline re-run of the classification only, after the edge model was corrected. Raw: `tools/bench/d1_step0_census.json`.

* **81 of the 91 boundary wires of the move set resolved without a single op run**, from `g.tunnels()` (132
  LoopTunnels in 9 s), `g.shift_reg_left()` (14 registers of `#637`) and `g.panel_wiring()` (114 objects). The
  remaining 10 went to `OpWireSource_v5` and every one of them is a `DigitalNumericConstant`.
* **The first classification was wrong, and the correction is the most reusable thing step 0 produced.** A
  wire-graph-only model called `#5540` — the reseed case that feeds two of the kernel's own inputs —
  `stays-with-tunnel`, contradicting `d1-build-plan` §4/§8. Two carriers are invisible to `Nodes[]`: shift
  registers (`toolkit-capabilities.md:494`) and a front-panel round trip (`#10969` writes indicator `min value`
  #17257; the implicit property `#17289` reads it back). With both measured and in the model the answer flips to
  `{5540, 9647, 10247, 10445, 10950, 17289: moves-with-kernel; 6810: stays-with-acquisition}` and **agrees** with
  the plan (gate G9). Anyone citing `diag_d1_step0.log:129` must cite the reclass log instead.
* **Notifier payload width = 1 DBL.** `#10407` t2 `Index of closest\ncal image slice, bead 2` ← w10990 ←
  `#10757 Index Array .element` ← w121 = `#5058 pos in cal image out`. Nothing else the focus pair reads comes
  from the kernel in the same iteration.
* **All 14 shift registers of `#637` tabled with what each carries** — §8's "2 per-frame state carriers"
  undercounts: 4 belong to 1.2 (`#1147/#1142` x,y,z · `#5796/#5805` bead-good · `#119/#2972` pos-in-cal ·
  `#7311/#11001` the reseed counter), 2 to 1.5 (`#4256/#4274` position, **`#4334/#4344` the VISA session**),
  2 to 1.7 (`#15/#51` the accumulator, `#24/#1108` the error chain), 1 to 1.1 (`#1117/#5351` LastBufferNumber).
* **Reverse crossing:** `#10407` t6 `position [internal units]` w9113 → `CaseStructure #12589` → `#11639` → the
  acquisition loop's conditional terminal. The focus loop feeds the stop, and the plan gives it no transport.
