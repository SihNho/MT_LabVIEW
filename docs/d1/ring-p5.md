---
type: decision
kind: topic
status: current
date: 2026-10-09
parent: docs/d1/INDEX.md
tags: [d1, ring-buffer, p5, results-queue, file-writer, pre-decided]
---

# Ring buffer P5 — results 1.2 → 1.7 (lossless FIFO into the file writer `#376`)

The design, step list and saved-file list CLAUDE.md "Big or blocked work" item 4 requires before any P5 build
(PD370(b), `docs/d1/ring-p4d.md:121-126`). Facts used: `tools/bench/p5_facts.md` (F1..F8, card 153-a1-1, F4 corrected by
153-a2-7). P5 is the 6th and LAST broken file the cap allows (5 of 6 used); P6 must RUN after it.

How to add: see the 5-line note at the top of `docs/d1/INDEX.md`.

## Pre-decided

374. **(cycle 154 judgement, 2026-10-09 — the P5 design, from `p5_facts.md` F1..F8 and PD370(b))**
     USER-RULES: U1 (relied on: `#376` receives the same element `#2626` computes and the same frame-index invariant as in
     the original, see (b); no per-bead maths changes), U4 (relied on: the queue carries the 1.2 → 1.7 DATA stream only;
     1.7's termination is a published counter read by a local, no edge detection — CLAUDE.md 1c''), U6/U8/U13 (relied on:
     loop 1.1 and the ring are not touched; only valid frames, already chosen latest-wins by P4, are handed on); none
     contradicted.
     - **(a) Data path.** One queue, element type = 1-D array of DBL (the type of `#2626` 'appended array' t2813, F1 t5),
       max size unwired (unbounded = lossless). [AMENDED by PD376(a): Obtain on 686, not `#4866`.] Obtain on FS1 frame `#4866` — the SAME frame as P2b's initialisers, so the
       refnum leaves that frame only after the initial writes in (c) are done. Enqueue in loop 1.2's body (Diagram #23166)
       inside a NEW Case on the valid-frame boolean (RingSeqCheck #29724 'valid' t29900, w30457's 8th sink): True frame =
       Enqueue(`#2626` t2813) + record counter +1; False frame = pass-through. Torn/stale frames never reach 1.7 (PD293(a)).
       Dequeue in loop 1.7 (`#23041`, body #23405) with timeout 100 ms. Release Queue on 686 AFTER 1.7 exits (refnum from
       1.7's output tunnel). Error terminals of the four queue nodes stay unwired (no error is possible by construction:
       the refnum exists before both loops start and is released after both end).
     - **(b) 'frame index' into `#376` = 1.7's RECORD COUNTER, not the per-slot `FrameIdx` — AMENDS PD233(f)(2) for t7
       only.** In the original `#376` is called once per `#637` iteration with no case, so its 'frame index' (`#637` i)
       always equals the number of earlier `#376` calls (F4); inside save trace.vi that value is a ROW COUNTER — Q&R by
       'file size' picks the row and `remainder == file size − 1` writes the file (F4, `save trace.json:816-1066`); it is not
       written as data. `FrameIdx` holds loop 1.1's `i`, which also counts 1.1's duplicate-skip iterations (Wait 1 ms,
       PD238(i)), so consecutive valid frames get non-consecutive values — fed to `#376` it would skip rows and miss file
       writes. A 1.7 shift register (I32, init 0), read on its LEFT side into `#376` t7 and incremented only in the frame
       where an element was dequeued, keeps the original invariant exactly. The row's own content is unchanged (`#2626`).
     - **(c) Termination by a published counter (U4, CLAUDE.md 1c'').** New I32 indicator `records final (1.2 to 1.7)`,
       initial value −1 written on `#4866` every run (PD240(b) pattern). Loop 1.2 keeps an enqueue-count shift register
       (I32, init 0, +1 in the True frame of (a)); after 1.2 exits, its final value is written to `records final` by a
       LOCAL on 686, ordered by the data dependency on 1.2's exit. Loop 1.7 stops when `records final` ≥ 0 AND its record
       counter (after this iteration) == `records final`. Every element is processed before 1.7 stops, whichever loop
       finishes first; no queue status read, no boolean edge, no ordering race.
     - **(d) 1.7 body.** A NEW Case on Dequeue's 'timed out?': the not-timed-out frame holds `#376` (MOVED in), its
       `#3052` refnum constant and the indicator `#3453` 'file progress'; t5 ← the dequeued element, t7 ← (b)'s counter.
       `#376`'s existing shift registers (t0 error → RSR #24083, t1 total data array → RSR #24150) and TWO NEW shift
       registers for t3 / t4 (today straight to out-tunnels #5204 / #10404) pass their values through the timed-out frame,
       so the values that leave 1.7 for `#6384` / `#2048` are those of the LAST real `#376` call, as in the original. The
       scaffold stop (`#23042` 'x = y?', in-tunnel `#23501` and its wires; NOT `#8486`) is removed and replaced by (c).
       In-tunnels #24357 / #24361 / #25223 keep their sources.
     - **(e) Steps and saved files** (≤ 40 actions each, FULL scratch run on a byte copy before each, PD261(d)/D-2026-10-01-01;
       in-between files are not counted, D-2026-10-02-02/-04):

       | step | content | base | saved file |
       |---|---|---|---|
       | P5-1 | (a) Obtain + element constant on `#4866` [686 per PD376(a); cut into P5-1a / P5-1b, PD378]; refnum into 1.2; Case on 'valid' + Enqueue; (c) indicator + init −1, 1.2 count SR, local write after 1.2 | s09 eb1d0f31 | `claudeDev\D1_ring_p5s01_<ts>.vi` (in-between) |
       | P5-2 | refnum into 1.7; Dequeue; (d) Case, move `#376`/`#3052`/`#3453`, counter SR, 2 new SRs; (c) stop; scaffold removed; Release after 1.7 | real P5-1 graph | `claudeDev\D1_ring_p5_<ts>.vi` = counted 6 of 6 |

       If the plan maker cuts a step above 40 actions or above X10 680, the cut point is the plan maker's, inside the
       same order, and each extra cut is one more in-between file. P5-2's stagexec route for Release Queue does not
       exist (F7: routes obtain/enqueue/dequeue only); it is a tool the cycle builds (`stagexec` + `stagesim`, self-tested)
       before P5-2 is planned.
     - **(f) Predictions per step:** graph == sim (E1) for every op; D / TD / PB on position keys (T6) against preds made
       under `vigraph.py` a7eb58c7 (PD373(e)); Error List recorded per class with both elrule totals (carry and no-carry),
       neither gating (PD370(a)); X10 ≤ 680, MEMSTOP 695 unchanged. Structural only. Rule-1a acceptance is P6: recorded-frame
       replay, X/Y/Z AND the saved files bit-identical with the original (PD238(f)).

375. **(cycle 154 judgement, hand-back 1, 2026-10-09 — how the queue nodes are PLACED; amends PD374(a)(e) tooling only)**
     USER-RULES: U4 (relied on, unchanged from PD374: the queue carries the 1.2 → 1.7 DATA stream only); none contradicted —
     this item changes which tool places the nodes, not what the VI computes or how loops talk.
     - **Fact (card 154-a1-1, `tools/bench/diag_c154_a1_1_facts.md`):** the `queue` route (`gscript.queue_node`) always wires
       its `src`, and `src` must be a Node on the same diagram or reach a LOOP body by the creator's auto tunnel
       (`stagexec.py:3085-3089`, `:3538-3541`; `stagesim.py:2318-2342`). So it cannot put Enqueue inside a new Case frame, and
       it cannot type Obtain from a constant. No queue donor existed.
     - **(a) Decision: route (a), a DONOR, not a queue-route variant.** Build `claudeDev\DonorQueue_v0.vi` by script (a fresh
       scratch VI, never an original), holding one each of Obtain Queue, Enqueue Element, Dequeue Element, Release Queue and
       one 1-D DBL array constant; the cycle-153 hygiene-checked ops `OpQueue*_v0` may build it. Read back and record every
       node's uid, class and terminal names. All four P5 queue nodes are then created UNWIRED by the existing `primitive`
       route (`gscript.create_primitive_nested`, `gscript.py:4790`: donor copy at any nesting depth, `donor={donor, uid}`),
       and wired by existing wire / case-tunnel / FS routes. Obtain is typed by a NEW 1-D DBL constant (from that donor or
       DonorRingConst_v0 uid 101) wired to 'element data type'; `#25632`'s TransPos net is not touched.
       Why: the `primitive` route is proven (P3a/P3b), it places nodes inside Case frames, and one donor covers Release too.
       A queue-route variant would mean new op-VI versions and a new route in both stagexec and stagesim.
     - **(b) PD374(e)'s "Release route" tool build is DROPPED;** Release Queue comes from the donor by the same route.
     - **(c) Route census first (offline):** before the P5-1 plan, every P5-1 create and wire gets its existing stagexec route
       and stagesim support named. A wire or create with no route (e.g. a tunnel inner face or a constant as a wire source) is
       a hand-back, not a tool edit inside the card. stagexec / stagesim may change only to register the four queue
       primitive classes and their terminal model for the `primitive` route (no new route). Queue primitives created by
       `primitive` are a NEW structure class, so P5-1 owes the prior-art review (no proven-pattern skip).
     - **(g) Carried to P6, measured offline before P6 is planned (not a P5 blocker):** every other consumer of `#644` i in
       the original (w3268's 8 sinks) and of `FrameIdx` in s09 (`#10068` / `#29240` display remainders, PD237(g), and any
       autofocus cadence counter), each with: what it computes, its loop, and whether it uses the value as a COUNTER
       (Q&R / every-N). The same duplicate-skip argument as (b) may apply to them; judgement decides after the facts.

376. **(cycle 154 judgement, hand-back 2, 2026-10-09 — how the queue REFNUM reaches Enqueue; amends PD374(a) placement only)**
     USER-RULES: U1 (relied on: same queue, same element, same valid-frame Case; the refnum value never changes, so where it is
     obtained and whether it rides a tunnel or a shift register computes nothing different), U4 (relied on: the queue is still
     the DATA stream only; the local in (c) carries a reference written once before both loops start, read by the loops — no
     control signal by queue, no edge); none contradicted.
     - **Accepted:** card 154-a2-2 (`claudeDev\DonorQueue_v0.vi` 81dba822, `tools/bench/donor_queue_v0.json`: Obtain #108,
       Enqueue #44, Dequeue #45, Release #46, const #52) = PD375(a) met. Census 154-a2-3 (`tools/bench/p5_route_census.md`):
       17 rows OK, rows 9-10 GAP: no route crosses base-FS frame #4866 → frame 686, and no route goes loop-tunnel inner face
       → case tunnel (`stagexec.py:766-787`, `stagesim.py:2150-2152`). The only proven tunnel → case-tunnel route starts at a
       plan-made SHIFT-REGISTER inner face (R1/R2, the same route as the census's count SR, rows 14-15).
     - **(a) Form S (first choice): Obtain + its element-type constant on 686 (frame 8, the frame that holds loops 1.2 and 1.7),
       refnum into 1.2 on a NEW plan-made shift register of `#10170`.** Obtain 'queue out' → SR left outer (same diagram 686);
       L.inner → case tunnel in (R1) → Enqueue 'queue'; Enqueue 'queue out' → case tunnel out → R.inner (R2); False frame
       passes the refnum through (row-16 route). R.outer is left for P5-2 / Release. The `records final` indicator and its −1
       initialiser STAY on `#4866`: frame 7 finishes before frame 8 starts, so −1 is still written before either loop runs,
       which is all PD374(c) needed `#4866` for. Tooling cost: none — every link is an existing route.
     - **(b) Form L (only if the census shows ANY form-S row as GAP):** Obtain stays on `#4866`; a NEW refnum indicator
       `queue (1.2 to 1.7)` born on Obtain 'queue out' (row-5 route, born_on); inside 1.2's new True frame a `local_read` of
       it (`stagexec.py:243`, `:3015`) → Enqueue 'queue'. Enqueue 'queue out' left unwired. Rule: census S and L in ONE card;
       S if every S row is OK, else L if every L row is OK, else hand back. No tool is written for either.
     - **(c) X17 registration:** add the four DonorQueue_v0 entries (uids 108/44/45/46 → Obtain Queue / Enqueue Element /
       Dequeue Element / Release Queue, class "Function", md5 81dba822, cite `donor_queue_v0.json`) to `PRIM_DONORS`
       (`stage_prerun.py:2802`), self-tested, that change only. stagexec / stagesim stay unchanged (the `primitive` route
       reads no class table, census row 20 / facts "Registration").
     - **(d) P5-2's refnum rows (1.7 Dequeue, Release after 1.7) are censused in the same card, report-only:** their GAPs do not
       block P5-1; they return to judgement with the P5-2 plan. Preferred P5-2 form mirrors (a): a second branch of Obtain's
       refnum on 686 into a 1.7 shift register, Dequeue on its L.inner in the body, its R.outer → Release on 686 (row-18 route).
     - **(e) Carried, not this purpose:** census row 9 Vb crashed stagesim with a TypeError at `stagesim.py:1783` (a base FS
       frame has no `diagrams` entry) instead of refusing with a SimError — a tool defect for a later tooling card.

378. **(cycle 155 judgement, 2026-10-09 — after hand-back 154_3: P5-1a adopted, P5-1b refused at compile)**
     USER-RULES: U1 (relied on: no change to what the VI computes — the P5-1b rows are PD374/PD376 unchanged; only how the
     stage tools ADDRESS a frame changes), U4 (relied on, unchanged: queue = data stream only); none contradicted.
     - **Accepted (cycle 154 round 3):** form S (PD376(a)); X17 entries for DonorQueue_v0; P5-1 cut by X10 into P5-1a (actions
       1..20) and P5-1b (21..32). P5-1a scratch 23/0, adopted `claudeDev\D1_ring_p5s01a_20261009_101219.vi` md5 2482fe7b, Error
       List 47 (pred 48; the −1 is elrule over-counting an optional unwired Obtain sink, `archive/peer/2026-10-09-c154-a3-3b-el47.md`
       :55-59, non-gating), graph `graph_ring_p5s01a_20261009_103621.json` bd67a511, load 602.6. It is an in-between file
       (D-2026-10-02-02): not counted toward the 6.
     - **Fact (card 154-a4-1, `tools/bench/diag_c154_a4_1_facts.md`):** P5-1b's two False-frame pass-through wires (actions 21
       `w_false_pass`, 32 `w_q_false`) name frames of Case #30726, which P5-1a created and which is a BASE case in P5-1b.
       `stagexec.case_frame_op` (`stagexec.py:613-615`) and `stagesim.resolve_addr` (`stagesim.py:797-800`) give frame names
       only to a case created by the same plan; and the SR-face → case-tunnel route (`connect_term_uid` register_end_case_border,
       R1/R2) falls back to a plain `tunnel` on a base case (`stagexec.py:781`), which is not the measured route.
     - **(a) Decision: a narrow TOOL fix, not a re-cut and not a design change.** A re-cut would discard the adopted P5-1a and
       still needs X10 room for the whole case group in one step; a design change (dropping `t_qo`) would still leave the
       base-case tunnel route unmeasured. The same need returns in P5-2 (if X10 cuts it) and in every later track that edits a
       case already in the file, so the tool is necessary (CLAUDE.md, tool lift 2026-09-24). The fix: a `CaseStructure` that is
       in the REAL base graph is treated like a plan-made case for (1) `frame` addressing by MEASURED diagram uid,
       `frame: "#<diagram uid>"` (as FS faces already are, `stagexec.py:661-662`), and (2) the choice of the
       `connect_term_uid` register_end_case_border / `case_frame_wire` variants. The frame index is the position of that
       diagram uid in the graph's frame list for the case; the card cites the measurement that this order is LabVIEW's frame
       index (P5-1a: Enqueue planned on 'True' = index 1 landed on #30922, the 2nd entry of [30914, 30922]; plus one more case
       if the graph has one with known frame content). Frame NAMES for base cases are not inferred. Only
       `stagexec.py` and `stagesim.py` change; a new self-test + their existing self-tests pass; regression = P5-1a's
       plan (`plan_ring_p5s01a.json`) recompiles to the same ops as before.
     - **(b) This tool card goes BEFORE the P5-1b plan** because the P5-1b plan cannot compile without it (deliverable-first
       exception: the gate refuses the deliverable itself). Then P5-1b = actions 21..32 of `plan_ring_p5s01.json` ed6ceb9e,
       symbols mapped to real uids by `tools/bench/prep_c154_a4_1_mk.py` e65b41d3 (MAP PASS, log:7-15), frame wires addressed
       `#30914` (Case #30726's False frame: Enqueue sits on #30922), on graph bd67a511. P5-1b owes a prior-art review (base-case
       addressing is new). ONE scratch on a byte copy of P5-1a → adopt `claudeDev\D1_ring_p5s01_<ts>.vi` (still an in-between
       file). Predicted Error List change vs P5-1a: 'Tunnel: Missing assignment to tunnel' −1 and the Enqueue 'queue' unwired
       item −1 (both closed by P5-1b's wires); per-class with both elrule totals, non-gating.
     - **(c) Then the P5-2 plan** on the REAL P5-1 graph, per PD374(d) + PD376(d) (Dequeue + Release from DonorQueue_v0 by the
       `primitive` route), not launched; any route GAP comes back with its census row.
     - **(d) Carried:** elrule over-counts optional unwired primitive sinks and has no tunnel class (`elrule.py:153-158`) —
       tooling, after the deliverable, non-gating. Hook entries fp-74 (guard_bash) and fp-75 (guard_cycle) are the chat's.

379. **(cycle 156 judgement, 2026-10-09 — cycle 155 accepted; the three P5-2 GAP rows and the cut decided)**
     USER-RULES: U1 (relied on: `#376`'s inputs and the values that leave 1.7 for `#6384` / `#2048` are those of the original —
     (b) keeps the last real call's t3/t4; (a) changes only the new stop scaffolding, not any original computation), U4 (relied
     on, unchanged: the stop is a published counter read by a local; no queue status, no edge); none contradicted.
     - **Accepted (cycle 155, `tools/bench/cards/assign_result_155_1.json`):** the base-case frame tool fix (stagexec 53e17623,
       stagesim eb99c6ba, `selftest_c155_basecase_frame.py`); P5-1b scratch 20/0; adopted `claudeDev\D1_ring_p5s01_20261009_124542.vi`
       md5 7f2582ae (a byte copy of the p5s01b scratch output: `adopt_scratch` cannot rename, `stagexec.py:4114-4119` — accepted),
       Error List 45 (expected `errorlist_expected_D1_ring_p5s01_20261009_124542.json` ffc4cf66), graph
       `graph_ring_p5s01_20261009_125622.json` 6716c499, `load_by_vi` entry written. In-between file, not counted. The bed stays
       s09 until P5 ends. The P5-2 plan 285cb59a (`tools/bench/diag_c155_a4_1_facts.md`) is NOT launched; it is re-made per (a)–(d).
     - **(a) GAP J-ge0 — DROP the `≥ 0` test and its And.** 1.7's record counter is an I32 initialised 0 and only ever incremented
       by 1, so it is ≥ 0 at every check; `counter == records final` is therefore already false while `records final` = −1 and
       already implies `records final` ≥ 0. Equal? feeds 1.7's condition terminal directly (same stop mode as the scaffold it
       replaces; the card reads that mode, it is not assumed). Same stop instants as PD374(c) in every case, including
       `records final` = 0. No Greater-Or-Equal donor is built.
     - **(b) GAP K3/K4 — the two new SRs for `#376` t3 / t4 are kept (PD374(d)).** Why they are needed: 1.7 can stop on a
       TIMED-OUT iteration (all elements processed before `records final` is published), so a plain out-tunnel would carry the
       timed-out frame's value, not the last real call's. Shape per terminal: SR L.inner → case in-tunnel → pass wire in the
       timed-out frame → case out-tunnel → SR R.inner; `#376` t3/t4 → the same out-tunnel in the not-timed-out frame. The
       in-tunnel's one out-wire IS the pass wire. Invariant the sim must show: the sinks of `#6384` / `#2048` that took t3/t4 in
       P5-1 take the value that reaches R.inner (keep out-tunnels `#5204` / `#10404`, re-fed from that net, or feed from R.outer —
       either form, the same value; the plan maker picks the one with existing routes). SR init = a constant equal to the
       terminal type's default value (so a rerun without reopening the VI carries nothing over; the original always calls
       `#376` at least once, so the init never reaches a sink unless no valid frame exists). If the stage tools cannot express
       an in-tunnel whose only use is a pass wire in another frame (the refusal at `stagexec.py:857-859`), a narrow fix is
       authorised in `stagexec.py` / `stagesim.py` only, with a new self-test, the existing self-tests, and P5-1a / P5-1b plans
       recompiling to the same ops.
     - **(c) Cut.** Groups are never split across steps (155-a4-1's step 1 split G). Each step's planned MAIN ≤ 675 (5 MB under
       the X10 limit, which itself stays 680; retrospective-cycle155 finding 3). Each step ≤ 40 actions. Every step but the
       last is an in-between file named `claudeDev\D1_ring_p5s02<letter>_<ts>.vi` (not counted); the LAST step is the counted
       6 of 6, `claudeDev\D1_ring_p5_<ts>.vi`, and P6 must RUN after it.
     - **(d) sr_q R.outer (t31246, loop 1.2) stays unwired.** Release takes 1.7's refnum SR (PD376(d)). Release cannot race an
       Enqueue: 1.7 stops only after `records final` is published, which happens after 1.2 exits.
     - **(e) Prior-art A4 (`archive/peer/2026-10-09-priorart-priorart-c155-a4-1-p5s02.md`):** cycles 97/98 left case-frame moves
       termless with loose ends; the scratch's E1 graph == sim check is quoted for each `move_in` op of `#376` / `#3052` /
       `#3453`. A3 (wording of census row 10) needs no action.
     - **(f) fp-73 CLOSED as moot** (`gate_fp.py close`): the candidate fix declassified 64 real discard-only files and broke
       `selftest_guard_bash_jev` C11 (12/0 → 11/1, `tools/bench/diag_c155_a5_1_facts.md`), and the diagnostic that raised it no
       longer imports stagekit. Every other open gate-fp entry is a hook gate (the chat's).
     - **(g) Device (retrospective-cycle155 `device-failed`, `docs/violation-decisions.md` 2026-10-09 13:55):** `tools/violations.py`
       DEC_RE reads `HH:Mx` as `HH:M9`, self-tested; offline, after the LabVIEW card.
380. **(cycle 156 judgement, hand-back 1, 2026-10-09 — the P5-2 step-1 scratch stopped at op 16; measure before fixing)**
     USER-RULES: U1 (relied on: this item changes no computation — it orders a diagnosis); none contradicted.
     - **Accepted (round 1, `tools/bench/cards/assign_result_156_1.json`):** plan `plan_ring_p5s02a.json` 4284c22a re-made per
       PD379(a)–(d); the K3/K4 pass-wire fix stagexec 25a1494c (`selftest_c156_passwire.py` 20/0). The ONE scratch (156-a2-2) ran
       ops 1–15 with E1 diff 0 and stopped IN op 16: `#24360 is an INNER face of LoopTunnel #24357`
       (`tools/bench/diag_c156_p5s02a_scratch.log:254-255`). Nothing adopted; LabVIEW gone.
     - **(a) No fix is chosen yet.** Two explanations are open (hypothesis review
       `archive/peer/2026-10-09-c156-a2-2-p5s02a-innerface.md`): (E-A) the executor has no inner-face route; (E-B) the sim keeps
       wire 24330 on `#24360` after `mv_376` as "ambiguous", the route check chose `cfw`, LabVIEW dropped the wire. The next act
       is the OFFLINE measurement card `tools/bench/cards/task_156-a3-1.json` (brief d551f7e7) as written; the fix (route both
       outcomes, per-terminal outcome record, re-route from the outer face, the checkpoint list) is decided by judgement on its report.
     - **(b) PD379(e) is unmet** (move_in ops 10–12 were not E1 checkpoints, scratch log:49,55). The next scratch does not
       launch until the plan or the fix makes every `move_in` op of `#376` / `#3052` / `#3453` an E1 checkpoint.
     - **(c) Re-splitting:** a second stop at op 16/17 (same place) ⇒ a decomposition plan for P5-2 step 1 before any further
       scratch (CLAUDE.md "Big or blocked work" item 3); no full-length retry under a new name.
     - **(d) The failed work copy** `claudeDev\D1_ring_p5s02a_20261009_152721.vi` cac5236b and its resume record are kept as
       evidence, never loaded, run or resumed (its live state after `mv_376` is the question); not counted; deleted when P5-2
       step 1 is adopted.
     - **(e) The per-card invariant helper** (5th copy, `tools/bench/diag_c156_a2_1_inv.py`) is extracted into ONE shared module
       under `tools/` (not `tools/hooks/`, not stagekit) per `docs/script-writing.md`, self-tested by reproducing an existing
       inv log; offline, does not gate the deliverable.
381. **(cycle 157 judgement, 2026-10-09 — after `assign_result_156_2.json` / card 156-a3-1: the op-16 fix chosen)**
     USER-RULES: U1 (relied on: ops 16/17 still wire the same source face to the same `#376` input, only the route that finds the
     face changes; the checkpoints and outcome lines read, they compute nothing), U4 (relied on, unchanged); none contradicted.
     - **Accepted (cycle 156 round 2):** facts `tools/bench/diag_c156_a3_1_facts.md`; `tools/invcheck.py` (self-test 20/0); fp-73
       closed; `violations.py` reads `HH:Mx` (7/0); `docs/fn_descriptions.json` 3 → 62.
     - **(a) Working cause = E-B.** The op-16 stop text comes out of `connect_route` only when `#24360` has wire 0 (route.log:12), and
       op 16 used op 15's fresh checkpoint read (facts M2). So after `mv_376` LabVIEW had no wire on `#24360`. Op 17 (`#24367`) is
       the same case. No live read proves it (M2), so the fix in (b) must work whether the wire is there or not, and (c) measures it.
     - **(b) Fix: route both outcomes (stagexec / stagesim / addrcheck only, narrow).** When a plan wire's source is the INNER face of
       a LoopTunnel on a While or For loop and the face is unwired in the read, take its diagram from the graph (tunnel → owner
       loop → that loop's one body diagram) and choose the route the wired case chooses (`cfw`, same dst). Loops only: an inner face
       of a Case or FS tunnel still stops. Self-test: the M1 cases. With wire 0, op 16 and op 17 give `cfw` with the same dst as
       wired. The existing self-tests pass. `plan_ring_p5s01a` / `p5s01b` / `p5s02a` compile to the same ops as before.
     - **(c) Outcome record (measure, do not model).** After every `move_in` op the executor prints one `FATE` line per wire the sim
       marked ambiguous at that step: wire uid or 0 on the source term AND on the moved sink term, taken from that op's checkpoint
       read. This is the first record of a LoopTunnel-source only-sink move (facts M5: no precedent). Tightening `opmodels/move_in.json`
       from it is a later card. If the moved sink term (e.g. 5760) still has a wire when its connect op runs, return at that op.
     - **(d) Checkpoints (PD379(e), PD380(b)): a shared rule, not a recipe attribute.** `stagekit.RingSession` adds every op of kind
       `move_in` to `CHECKPOINTS` (stagekit.py:1927-1929); recipes stay inputs only (PD377). Self-test: `p5s02a` checkpoints = the old
       list plus 10, 11, 12. X10 is re-run with the extra reads. If planned MAIN goes over 675, the plan maker re-cuts per PD379(c).
       A cut that would split a group is handed back.
     - **(e) Then the deliverable:** dry + prerun of `plan_ring_p5s02a.json` (4284c22a unless (d) re-cuts it) on the new tool bytes.
       If the dry again shows PB PASS-UNVERIFIED, the scratch card carries `DRY-UNVERIFIED-OK` naming PB (fp-76 was this card
       omission, not a gate fault; close fp-76 as "gate correct"). Run ONE scratch on a NEW byte copy of P5-1 7f2582ae. It must show
       E1 diff 0 at every checkpoint and FATE lines for ops 10-12. Then adopt `claudeDev\D1_ring_p5s02a_<ts>.vi` (in-between, not
       counted) with a full Error List read, a graph read and `load_by_vi`. Then make the step-2 plan on that real graph (dry +
       prerun + prior-art), not launched. After step 1 is adopted, delete `D1_ring_p5s02a_20261009_152721.vi` cac5236b and its resume
       record (PD380(d)).
     - **(f) A second stop at op 16/17 means PD380(c):** no retry in the card; hand back for a decomposition plan.
     - **(g) gate-fp DUE:** every open entry (fp-62..69, 71, 74, 75) is a hook gate, so the chat drains them. No runner card does.
384. **(cycle 158 judgement, 2026-10-09 — cycle 157 (stopped mid-cycle by the chat) judged; steer_158 followed)**
     USER-RULES: U1 (relied on: ops 16/17 still join the same source face to the same `#376` input; only how the act finds the
     source changes; checkpoints read, they compute nothing), U4 (unchanged); none contradicted.
     - **Accepted (cycle 157 cards):** 157-a1-1 route fix + FATE lines + checkpoint rule (stagexec 69b1a301, stagekit 0d8f6d25,
       `selftest_c157_innerface.py`, all 200 stored plans compile equal); 157-a1-2 re-pins (20/0, 21/0) and dry/prerun facts;
       157-a1-3 fn descriptions 62 → 119; 157-a1-4 cut facts and fp-76 closed.
     - **(a) The wire-0 LIVE act is not `cfw`** (157-a1-1 open 1: `_cfw(0, …)` at `stagexec.py:3135` cannot work — there is no wire
       to branch). PD381(b) is amended: when the read shows the LoopTunnel inner face unwired, the act is the term-to-term
       `connect_nested_v1` route (`stagexec.py:3137-3142`) with src = that face's triple on the owner loop's body diagram; when it
       is wired, `cfw` as before. Same dst both ways. Self-test both outcomes on ops 16/17 through the act path (sim backend);
       Case/FS inner faces still stop.
     - **(b) Checkpoint rule, amended (PD381(d), memory):** every-`move_in` checkpoints put planned MAIN at 679.7 (> 675), and no
       group-end cut fits (20: 675.8, 26: 683.6; `diag_c157_a1_4_facts.md`). Rule now: the LAST op of each maximal run of
       consecutive `move_in` ops is a checkpoint; the FATE lines of every `move_in` in the run come from that read, compared with
       the checkpoint before the run. p5s02a = (0,1,3,6,8,9,12,15,16,17), model MAIN 674.7 (157-a1-4 line 14). The plan
       4284c22a is kept, not re-cut. A moved node's E1 check is per run, not per op (localisation lost, detection kept; ops 10–12
       move three different nodes). The Executor REFUSES before op 1 a checkpoint set missing a run-closing op (not FATE-UNREAD).
     - **(c) Then the deliverable, as PD381(e)** with the empty disposition of the c156-a1-1 prior-art review filled first (it
       blocks the next prior-art dispatch). If planned MAIN is still > 675 after (b), hand back; do not re-cut in the card.
     - **(d) Steer `debate:plan-overall-02` FOLLOWED** (PD383): P5 → P6 unchanged; PB PASS-UNVERIFIED is a representation
       difference, so it is RECORDED via `DRY-UNVERIFIED-OK`, not blocking; the FATE lines are the post-run read of what LabVIEW
       decided. The GATE MUTATION TABLE runs as ONE small offline card beside or after the LabVIEW card, never before it: on the
       stored graph `graph_ring_p5s01_20261009_125622.json` 6716c499, a fixed mutation list (wire dropped, wire re-sourced, node
       moved to another diagram, tunnel renamed with owner/connectivity unchanged, uid renumbered with connectivity unchanged,
       constant value changed) is scored against the existing gates (computation_diff, D/TD/PB, E1, invcheck); each mutation is
       classed invariant (computation / save / safety) or representation; rows where an invariant mutation passes every gate, or
       a representation mutation blocks, are listed. No gate is edited in this cycle; the gate changes are judged from the table.
       P6 carries the two separate tests (frame-number gap; execution order with a test delay in 1.2: 0 normal-load loss, exact
       overload loss count, 0 damaged rows; a discard never seen = 'not verified'); the new-skeleton comparison is after P6.
385. **(cycle 158 judgement, hand-back 1, 2026-10-10 — PD384(a)'s address does not exist; the route is chosen)**
     USER-RULES: U1 (relied on: ops 16/17 still join the same source face to the same `#376` input; only the op that makes the
     join changes), U4 (unchanged); none contradicted.
     - **Accepted (round 1, `tools/bench/cards/assign_result_158_1.json`):** 158-a1-2 PD384(b) run-closing checkpoints (stagexec
       df82d75e, `selftest_c158_runcheck` 10/0, 200 stored plans compile equal, Executor refusal self-tested); 158-a1-3 prior-art
       disposition filled, dry + prerun PASS with planned MAIN 674.7 (valid for THOSE stagexec bytes only). 158-a1-1 FAIL accepted
       as a correct return: a LoopTunnel inner face (`#24360`, `#24367`) is listed in no `Diagram.Nodes[]` row
       (`tools/bench/prep_c158_a1_1_probe.log:3-8`), so `connect_nested_v1` (Nodes[]-indexed) cannot take it as a source.
     - **(a) PD384(a) amended — the wire-0 act is `gscript.connect_term_uid(target, sink_uid, src_uid)`** (OpConnectTermUid_v0,
       `tools/gscript.py:5141-5163`: `Terminal.Connect Wire` by terminal uid, any owner, any diagram; already a stagexec route,
       `tools/stagexec.py:293-330`). src = the inner face's term uid, dst = the same `#376` input term uid the wired case uses,
       both from that op's checkpoint read (op 15 for ops 16/17). Wired face → `cfw` as before. Case/FS inner faces still stop.
       No new op VI, no `Tunnel.Inside Terminals[]` route (the M3a-3 dead-end note, `tools/recipes/build_d1_m3a3.py:123-127`,
       concerns FS tunnels and stays closed).
     - **(b) Census:** the nearest measured variant is R1 (a register INNER face → a node in a case frame = ONE SelectorTunnel,
       `ROUTE_CENSUS['connect_term_uid']['register_end_case_border']`). The fix adds a named variant for a LoopTunnel inner face
       whose predicted delta is taken from where the dst actually sits on the sim graph (case frame → R1's delta; same diagram →
       one Wire); it is a PREDICTION, marked unmeasured, and the scratch's census of ops 16/17 is the measurement — a mismatch is
       a return at that op, never a retry in the card.
     - **(c) Self-test (sim backend, act path):** ops 16/17 with the face wired → `cfw`; with wire 0 → `connect_term_uid` with the
       face uid as src and the same dst uid; a Case and an FS inner face with wire 0 still stop; all stored plans compile equal;
       158-a1-2's `selftest_c158_runcheck` and the suite counts unchanged.
     - **(d) Then PD384(c) unchanged:** dry + prerun on the new bytes (MAIN > 675 ⇒ hand back, no re-cut), ONE scratch on a NEW
       byte copy of P5-1 7f2582ae, adopt, step-2 plan not launched; PD381(f) holds (second stop at op 16/17 ⇒ hand back).
     - **(e) Prior-art:** `connect_term_uid` is a proven op, but a LoopTunnel inner face as its source is a new use; the plan's
       prior-art review (PD384(c)) covers it — no separate review.
386. **(cycle 158 judgement, hand-back 2, 2026-10-10 — the scratch built the planned graph; four gates failed on convention)**
     USER-RULES: U1 (relied on: every `#376` input keeps its S1 source terminal — 3391 'cal cluster path', 1766 'file size' —
     and the moved sources sit in the planned case frame; nothing here changes what reaches `#376`), U13 (unchanged); none
     contradicted. Applies steer `debate:plan-overall-02` items 4/10: BLOCK = computation / save / safety invariant, RECORD =
     representation.
     - **Accepted (round 2, `tools/bench/cards/assign_result_158_2.json`):** 158-a2-1 (stagexec 7a712ccb, `selftest_c158_wire0face`
       24/0, stored plans equal); dry + prerun PASS on those bytes, planned MAIN 674.7; the scratch ran all 17 ops, E1 diff 0 at
       every checkpoint, ops 16/17 took `connect_term_uid` (`diag_c158_a2_2_facts.md:18-21`); 158-a2-4 mutation table, 158-a2-5
       66 descriptions. The 158-a2-3 offline recount (`diag_c158_a2_3_facts.md`) is accepted as the reading of the failure:
       real end == sim end in topology except wire 24091's source-only stub, and real PB == sim-with-real-uids PB.
     - **(a) PB, move into a case CREATED by this stage:** the frame tag is compared by the BOUND frame uid, never by the
       ordinal (`vigraph.py:322` ranks by uid, so negative sim uids reverse it — the f1/f0 flip is that artefact, :126-128).
       Contract: real PB == sim-end PB re-keyed with the run's bindings (frame-keyed) — any difference BLOCKS. A row of
       PB(S1, real) whose only difference from S1 is the tag `@<tunnel>/f<k>` is RECORDED (not blocking) iff its source
       terminal uid equals S1's and the tunnel's bound frame is the plan's frame for that move; any other extra/missing row
       BLOCKS. Same rule for every later step that moves a source into a case it created.
     - **(b) D / TD are judged pair-keyed** (`stagekit.wire_ends_pos` (source, sink) pairs, sim owners via the bindings):
       new / lost pairs real == sim, else BLOCK. Half wires with no sink (source-only stubs) are dropped on both sides and
       RECORDED — a wire with no sink carries nothing (wire 24091: sim keeps the stub, LabVIEW deletes it). The simulator's
       stub-keeping is logged as a model gap (FINDING, no build now).
     - **(c) CEN2:** the pred's `census_overall` becomes `MEASURED-SCRATCH` = the c158-a2-2 run's census
       (`diag_c156_p5s02a_scratch.log:553-555`, the precedent `tools/bench/diag_c148_a2_4_census.py:52`); the retry's census
       must EQUAL it, else BLOCK. The FATE of ops 16/17 gets a per-op class census line (PD385(b) measurement, owed).
     - **(d) Mutation-table check of (a)/(b):** after the gate change, re-score the 158-a2-4 table
       (`tools/bench/mutation_table_p5.json`): every row classed `invariant` that blocked before still blocks; rows that now
       record are only representation rows. A newly passing invariant row = no launch, hand back.
     - **(e) The retry:** the scratch recipe writes its OWN log (`tools/bench/diag_c158_p5s02a_scratch.log`; the fixed c156
       LOG constant made METER read the whole file). Second run of the stage this cycle = a `retry_of` card
       (`stage_d1_ring_p5s02a_scratch.py`, RETRY_CARD). Then PD381(e) as written: adopt, Error List, graph json, load_by_vi,
       step-2 plan (not launched), delete failed copy 152721 cac5236b + its resume record. A FAIL on any BLOCK gate = hand back,
       no third run.
     - **(f) Tooling after the deliverable:** stale `stagekit.op:*` rows in fn_records (gen_capabilities --check DRIFT).
387. **(cycle 159 judgement 03:2x, 2026-10-10 — cycle 158 hand-back 3 judged; steer `debate:c159-stuck` FOLLOWED)**
     USER-RULES: U1 (relied on: 94ffff94 becomes the base only when every new Error List item is a connection a later P5-2
     action re-feeds; a leftover no action re-feeds would change what reaches `#376` and goes to the user), U4, U13
     (unchanged); none contradicted.
     - **Accepted (round 3, `tools/bench/cards/assign_result_158_3.json`):** 158-a3-1's PD386 gate rework (no invariant row
       weakened); the ONE retry scratch PASS 23/0 and the adoption of `claudeDev\D1_ring_p5s02a_20261010_023239.vi` 94ffff94
       as an in-between file — NOT yet the step-2 base; review `archive/peer/2026-10-10-c158-a3-2b-el56.md` as the reading of
       the Error List: the 11 extras are a NET count and are not attributed.
     - **(a) No re-run, no rebuild** (steer 1): the step-1 scratch is not re-run, 94ffff94 is not rebuilt, and no expected
       Error List is written from the 56 observed items as a block.
     - **(b) First act = the graph read** of 94ffff94 with the prepared read-only `tools/bench/diag_c158_a3_2b_graph.py`
       (plan 91fcfbec, prerun 15/0) + `load_by_vi` (prepared memload) in the same LabVIEW session; bed md5 unchanged after.
       It is PD381(e)'s graph item.
     - **(c) Offline attribution** (steer 3-4): recompute `allterms.join_wires`/`severed` from the new graph's stored
       terminals/objs, diff with P5-1's `graph_ring_p5s01_20261009_125622.json` 6716c499, and list per Error List class
       (no-source, LoopTunnel undirected, While-input-to-SubVI, not-connected, loose ends) the new and the resolved items.
       Each of the 8 items of the three NEW classes gets one row: connection (source uid + terminal, every sink, frame) →
       the `plan_ring_p5s02r_in.json` (d84634bd) A24..A80 action that re-feeds it. The net +3 of the two old classes is
       explained by listed new/resolved pairs. A fragment whose dropped end the graph does not show is UNATTRIBUTED (a
       narrow reporter read may fill it; screenshots are support only).
     - **(d) Acceptance rule:** every row attributed and the net explained ⇒ 94ffff94 IS the step-2 base; its expected
       Error List is written item by item from (c) (each item cites the action that clears it); the failed copy 152721
       cac5236b and its resume record are deleted. Any UNATTRIBUTED row ⇒ hand back with the table (a plan error is checked
       first); only a confirmed leftover that no later action re-feeds goes to the user (U1, steer 5).
     - **(e) Device for retrospective-cycle158 `device-failed`** (`docs/violation-decisions.md` 2026-10-10 03:2x), offline in
       `stage_prerun`/`stagekit` (never hooks), after the LabVIEW card and before step 2's dry: (1) the dry's final
       `unverified N` counts every gate line it printed `UNVERIFIED-DRY`; (2) a census declaration that does not cover every
       op of the plan, or a pred whose `census_overall` is `UNPREDICTED`, is UNPREDICTED — never a partial PASS; (3) the dry
       runs the recipe's own PB, D, TD and CEN2 against the simulated end. Self-test: the stored c158-a2-2 inputs (census
       declared for the Case op only, PB on stub input) make the dry report CEN2 and PB unverified or FAIL; all stored plans
       compile equal; suite counts unchanged.
     - **(f) Step-2 split** (steer 7, PD379(c)): step 2 = A24..A60 (F3..J, 37 actions), step 3 = A61..A80 (K3/K4, 20),
       kept iff on the real 94ffff94 graph no group crosses the A60/A61 boundary and step 2's planned MAIN ≤ 675; else cut at
       the last whole-group boundary that fits. Step 2 = `tools/bench/plan_ring_p5s02b.json` + recipe pair
       `tools/recipes/stage_d1_ring_p5s02b{,_scratch}.py` (the p5s02a pair's inputs on the shared stagekit `RingSession`
       gates, `docs/script-writing.md`), on the real graph: dry `unverified 0` under (e), prerun PASS, a predicted step-2-end
       Error List built from (c), prior-art review. NOT launched in cycle 159; the next cycle runs its ONE scratch.
     - **(g) Side items, after the above** (steer 6, GPT's form): the `diag_c158_a2_3_probe` result_line TypeError and the
       `diag_c158_a3_2_pascope` 'no scope' are recorded as diagnostics with their cause line, not logged to gate_fp without
       false-positive evidence; fp-77 (`stage_prerun.is_vi_modifying`, not a hook) is drained; hook entries stay with the
       chat; one batch of ~60 fn descriptions last.
PD388 onward: `docs/d1/ring-p5b.md`.
