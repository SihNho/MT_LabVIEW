---
type: decision
kind: topic
status: current
date: 2026-10-19
parent: docs/d1/INDEX.md
tags: [d1, layout, block-diagram, clean-up, coordinates, readability]
---

# Block-diagram layout of the product VI (from PD421)

Discussion: `tools/bench/debate/bd-layout/` (Google Doc 18oHlPS0AZo1T2c0AGZx-_e46r5knxj6vi_sKGOeTkxo, 5 rounds, converged).
User words: `V6_lean/tools/bench/lean_bench/user_notes.md` (2026-10-19 lines).

## Pre-decided

421. **(chat ingest, 2026-10-19 - lean runs 16-18, tasks bdtidy, bdtidy retry 1, discussion bd-layout)**
     - **(a) Problem (user):** "코드 위치가 너무 사방팔방임" - layout only, never the maths; structures too big; others cannot
       read the code. P6L (54f7cd2f) loop Bounds pass +-32767 (#10170 36528 wide); the user's own whole-diagram Clean Up
       froze LabVIEW (~556 MB) - "나도 clean-up diagram 해봤거든? 그런데 안되더라고".
     - **(b) Clean Up routes measured (scratch only; `lean_report_bdtidy_fail1.md`, `lean_report_bdtidy.md` PASS):** Clean Up
       Diagram 6D17C801 on an inner diagram = error 1071; a selection rectangle inside a structure selects 0 objects ->
       whole-diagram Clean Up; a selected TOP-LEVEL structure is re-laid with its whole nested tree (FS 906x2447 -> 589x160)
       and pushes its neighbours. Shrink Wrap Structures 6375403 shrank nothing in 4 calls (only grows an undersized
       structure), not recursive. Bounds is read-only on every structure class; GObject.Move does not grow a structure;
       FlatSequence.Size Frame 3578B804 grows a frame. Wire edges, node census, tunnel and wire uids unchanged in every call.
       No route found that tidies ONE nested structure.
     - **(c) The coordinate limit hurts edits:** P6R (PD422(d)) moved 5 nodes at y = 32710 and LabVIEW re-placed 25
       objects beyond +-32767 on save.
     - **(d) DECIDED (user "둘 다 동의함" after bd-layout, 2026-10-19):** layout by **direct coordinates** - sizes inner ->
       outer, positions outer -> inner, every move read back. Whole-diagram Clean Up, selection Clean Up and Shrink Wrap are
       out of the recommended route; splitting loop bodies into subVIs is out of this scope (later, separately).
       Order: scratch checks (shrink routes per class, coordinate frame of nested Position, save + reopen) -> ONE
       out-of-range object recovered on a P6L byte copy P6C (anything outside the pre-declared allow-list moving = stop) ->
       smallest structure first, then wider -> before / after images (readability) -> replay X/Y/Z bit-identical + one
       150 Hz leg. The first-recovery gate (target moved, nothing else) is separate from the final gate (all contents
       inside their structure, all coordinates within +-30000); no widening of an allow-list after results.
     - **(e) GUI resize allowed (user):** only when no scripting route is found, only the SIZE of While / For / Case / Flat
       Sequence structures, only on our scratch VIs and the P6L byte copy, through `tools/lv_gui.ps1` with a recorded
       `-Exception` (routes tried) and `-Evidence` (Bounds before / after + image). "Not found in this search" is reported,
       never "impossible".
     - **(f) Future builds (user: "이번에 정리해도 새로 만들때 또 온갖 이상한 곳에 만들 수 있잖아"):** one zone per top-level
       loop (camera, 1.1, 1.2, display, 1.7, motor / UI); new code only inside its loop's zone, never at an arbitrary
       absolute coordinate; every build runs the layout gate after save + reopen (nodes inside their structure's content
       area, tunnels on its border, wires and labels checked separately, coordinates within +-30000). Zone coordinates:
       `bdcoord_layout_plan.md` from lean run 18.
     - **(g) Records:** discussions that ran while the Google login had expired (45 local `doc.md`) were copied to Google
       Docs by `tools/debate_backfill.py` (links in each folder's `gdoc_url.txt`; re-run uploads only new ones).
