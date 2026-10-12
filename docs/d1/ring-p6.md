---
type: decision
kind: topic
status: current
date: 2026-10-12
parent: docs/d1/INDEX.md
tags: [d1, ring-buffer, p6, first-run, replay, pre-decided]
---

# Ring buffer P6 — the first RUN of the chain (after P5, `docs/d1/ring-p5c.md`)

P5 ended in cycle 166 (PD403): the bed is `claudeDev\D1_ring_p5_20261010_172913.vi` 75773b0d, broken file 6 of 6, Error
List 47. No further COUNTED broken file may be saved. P6 makes the chain RUN and proves rule 1a numerically (PD238(f)).
Facts used: `tools/bench/p6_facts.md` (e0f93a45) + `.json` (707bc678), card 166-a1-5. How to add: see the 5-line note at
the top of `docs/d1/INDEX.md`.

## Pre-decided

404. **(cycle 167 judgement, 2026-10-12 — P5 close-out accepted; the P6 outline; P6-0 = closure census + ONE
     Remove-Bad-Wires measurement on a scratch copy, before any P6 build)**
     USER-RULES: U1 (relied on: P6-0 edits and saves nothing that is adopted; every row P6-1 may touch is first classed
     against S1, and a row with no designed replacement is a stop for judgement, never a fix inside a card), U4 (relied
     on: a cross-loop row is classed by the design that carries it — local for control, the PD374 queue for the 1.2 → 1.7
     data stream), U6/U8/U9/U13 (relied on: the ring and the overload path are read as built, F4; nothing changes them),
     U12 (relied on: a pure-display row is classed DISP; its feed belongs to the display loop after P6, `ring-p4.md:53`);
     none contradicted.
     - **Accepted from `tools/bench/cards/assign_result_166_1.json` (items 0-14, cards 166-a1-1..6):** the close-out graph
       read (`graph_ring_p5s02e_20261012_173009.json` 7815af09); the rule-1a tunnel check PASS 21/0 — #5204 / #10404
       IndexMode 0 and outer type I32, equal in 75773b0d and P5-1 7f2582ae (`tools/bench/diag_c166_a1_1_facts.md:24-25`),
       so no P6 pre-run item comes from it; `load_by_vi` 647.8 (memory_model d12bcd3b); measured census in the pred
       (1cba18c2); expected Error List c94be128 (47 items); the bed move; the EL device on `stagekit.el_advisory`; the
       predictor replay (47, missing 0, extra 0); PB tightening + fp-86; E5 by node identity + fp-87/88; the P6 fact census.
       **P5 is closed.**
     - **The eight notes of that result, judged:** (1) the same bytes loaded at 647.8 (graph read) and 599.4 MB (tunnel
       read): the model keeps 647.8 as the X10 start, it errs safe (as PD397); the cause is not chased now. (2) the inline
       copies of the elcls and JSON-rewrite helpers (`diag_c166_a1_2_facts.md:25`, `diag_c166_a1_1_facts.md:38`) move into
       the shared module in the first tooling card after the LabVIEW card (`docs/script-writing.md`). (3) the PB count kept
       as a guard beside coverage: accepted, stricter only. (4) E5: the 15 stored inline copies stay as history; every NEW
       graph-read diagnostic calls `stagekit.e5_check`. (5) p5s02d's dry rc 1 is history; that stored plan is never launched
       again. (6) the drifted pins (`selftest_c165_innerface.py:250`, `selftest_c165_prime.py:117`, c147_b1_2 P0) are
       re-pinned in that tooling card. (7) STATUS.md: the `## NEXT` history lines older than cycle 164 are relocated
       VERBATIM to an archive file by that card. (8) noted, no act.
     - **gate-fp DUE (cycle card):** all 25 open entries (fp-62 .. fp-97) are hook gates (`guard_bash`, `guard_write`,
       `guard_peer`, `guard_assign`, `guard_cycle`, `guard_card`) or the harness (fp-96). None may be drained by a runner
       card (user 2026-10-08); they go to the chat.
     - **(a) P6 in parts, each its own purpose:**

       | part | content | file |
       |---|---|---|
       | P6-0 | closure census (offline) + ONE Remove-Bad-Wires measurement on a scratch byte copy of 75773b0d | nothing adopted |
       | P6-1 | the repair rows judged from P6-0; FULL scratch on a byte copy of 75773b0d, then ONE launch; save gates (b) | `claudeDev\D1_ring_p6_<ts>.vi`, saved ONLY with ExecState 1 (not a broken file) |
       | P6-2 | recorded-frame replay = rule-1a acceptance (PD238(f), PD374(f)): S1 replay copy vs P6 replay copy on the same recorded frames, X/Y/Z bit-identical over the common rows AND the saved files bit-identical | replay copies only |
       | P6-3 | the two steer_158 tests (PD384(d)): frame-number gap; execution order with a test delay in 1.2 (0 normal-load loss, the exact overload loss count, 0 damaged rows; a discard never seen = "not verified") | test copies only |
       | P6-4 | real ABBA at 90 / 150 Hz on the camera (PD238(f)); needs beads on the rig, so the user is asked before it is planned | — |

       After P6: the interface-contract step (STATUS parallelism rule). No other track is designed before it.
     - **(b) P6-1 save gates, fixed now so P6-0 measures what they need:** ExecState 1 (`gscript.exec_state`); an Error
       List with 0 error items (warnings recorded); `vigraph.computation_diff(S1, P6 graph)` rows == the closure table's R
       and DISP rows exactly (no D row carries data, no U row exists); #2626's inputs read 'element' ×3 + 'array'
       (PD366(d)); #5204 / #10404 IndexMode and outer type unchanged. A P6-1 scratch that does not reach ExecState 1 is NOT
       saved; it returns with its Error List. Whether DISP rows may stay unfed in P6-1 or get a local now is decided from
       P6-0's DISP count.
     - **(c) Closure classes, one per row, assigned by CITATION only (a row with no citation is U):** R = the sink's new
       source is a designed replacement (ring slot read, queue element, record counter PD374(b), a local — cite the PD);
       DISP = a pure-display indicator (U12, PD210); D = carries no data: a termless wire, or a loose-end branch whose sinks
       are fed elsewhere; C = a consumer of `#644` i or of FrameIdx (F2, PD374(g)); U = none of these. The census proposes
       no fix; U and C rows are judged by the next judgement under rule 1a.
     - **(d) P6-0 LabVIEW measurement, ONE card, deliverable first:** a fresh byte copy of 75773b0d under claudeDev
       (scratch name, never adopted) → ExecState → VI-level Remove Bad Wires by the EXISTING verb
       (`gscript.remove_bad_wires`, `tools/gscript.py:1987`, or the stagexec `rbw` route; `protocol.py requires` first) →
       ExecState → full Error List read → graph read (calling `stagekit.e5_check`). Deleted wires = the graph before
       (7815af09) minus the graph after, each with its ends before and tagged data-carrying (a source AND a sink terminal)
       or not. Stated prediction: RBW deletes the 22 termless wires of F1 and some loose-end wires; how many data-carrying
       wires it deletes and ExecState after are UNPREDICTED (the facts this card exists for). X10 ≤ 675 from 647.8 per
       LabVIEW session; if the reads do not fit one session, the RBW'd copy is saved under its scratch name, read in a
       second session and deleted at card end. Bed and the six kept P5 inputs hash unchanged; LabVIEW closed, verified gone.
     - **(e) P6-0 closure table, offline, a NEW file pair `p6_closure` (.md + .json) in tools/bench:** rows = the union of the 47 Error List
       items (F1), the declared `open_rows` of `plan_ring_p5s02e.json` (fd23974e; the lists at :12 and :319) and
       `vigraph.computation_diff(S1, 7815af09)`; the set equality of the last two is quoted (differences listed). Per row:
       sink (owner uid, terminal uid + name, loop), S1 source, P5-final source, class (c) + its citation, and after (d) the
       RBW-deleted wire it maps to (or none) and whether its Error List item is gone after RBW.
     - **(f) C rows measured (PD374(g)), offline:** for each F2 consumer (#1114, #2136, #29411, #12045, #3162, #1628,
       #30240 → #29240 / #10068): its owner chain in the P5 final and in S1; whether it runs on every 1.1 iteration or only
       in the new-frame case; the uid of the P3a new-frame counter terminal (PD246(c)) on its diagram; and whether the
       original ever repeats a BufNum on consecutive iterations, from a stored record (PD238(i) P1 measurement, ABBA leg
       records — cited; none stored = "unread"). No fix.
     - **(g) P6-2 readiness facts, offline:** the m8 replay chain (`tools/recipes/stage_replay_swap.py`,
       `tools/bench/drive_m8_replay_110.py`, `tools/bench/m8b_replay_compare.py`; F5): which call sites it swaps (uid in
       S1) and whether each exists in 7815af09; how card 110-6 kept its legs off the motors (hardware none); which saved
       files it compared; what is missing to point it at a ring file. Facts only; no tool built.
     - **(h) Order:** (d) first; (e)-(g) offline beside or after it; then the tooling notes (2), (6), (7). Nothing in
       `tools/hooks/**`. The next judgement writes PD405 = the P6-1 repair rows from (d)-(f).
