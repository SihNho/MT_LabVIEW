---
type: decision
kind: topic
status: current
date: 2026-10-02
parent: docs/d1/INDEX.md
tags: [d1, ring-buffer, p4, tracking-loop, pre-decided]
---

# Ring buffer P4 (tracking loop 1.2), part b — decisions from 323 on

Continues `docs/d1/ring-p4.md` (frozen 2026-10-02 at 429 lines; PD293–PD322 there stay in force as listed in
`docs/d1/INDEX.md`). Same scope: loop 1.2's reader, and P5/P6 until they get their own file.

How to add: see the 5-line note at the top of `docs/d1/INDEX.md`.

## Pre-decided

323. **(cycle 141 judgement, 2026-10-02 — after PD322, 140-5 PASS (`tools/bench/diag_c140_5_facts.md`), steer_140)**
     USER-RULES: U1 (relied on: the repair brings the slot write back to the design's fixed 20-slot write; the per-bead maths is
     untouched), U13 (relied on: 20 slots, slot = counter mod 20 — an array that grows breaks it); none contradicted.
     - **(a) Repair form per bed node** (`#27928`, `#28916`, `#29048`, `#29265`, `#29316`, in that order): record the node's 4 terminal
       endpoints from the bed graph; `delete_wire` every wire whose endpoints other than the node are none (the node's output wire, and an
       input wire whose only sink is the node — PD321's 1055 hazard); `delete_object` the node; `wire_remove_loose_ends` only on a wire that
       still has another sink (e.g. index wire w28367, shared by `#29048/#29265/#29316`); create from `claudeDev\DonorRAS1D_v0.vi` uid 175
       in the node's own frame; `connect_term_uid` the 4 terminals BY NAME (array, index, new element/subarray, output array —
       `diag_c140_5_facts.md:22-24`). Everything from the graph, nothing re-typed (Stages rule 8).
     - **(b) Prim gate (PD322(d)) has two halves, both FAIL:** run-time — every created node's read-back label/class equals the action's
       declared prim; offline (prerun) — a donor create's donor label equals the declared prim (`$work` donors from
       `main_vi_node_labels.json`). The offline half would have stopped `#29157` in cycle 131 before any LabVIEW run.
     - **(c) X10 is NOT recalibrated this cycle.** One point says it over-predicts (140-3: 615.5 measured vs 673.4), but P3b launches matched
       within 0.4 MB (680.4 / 680.8, PD274). The conservative model costs at most an extra session; the launch is additionally gated on the
       scratch's MEASURED peak ≤ 675 (PD321(c)). Recalibrate when ≥ 3 P4 sessions have measured peaks.
     - **(d) Cycle-141 order:** card 141-1 ALONE (it edits stage tools; pairing rule PD281(a)); then the LabVIEW card = session 1 of v16
       per PD320(e) — ONE scratch on a bed byte copy, launch only if every gate PASSes (prim gate included), Error List count == prediction
       (PD322(e) per-node rule) and scratch peak ≤ 675 — beside an offline prep card for session 2 (provisional on stagesim's end graph of
       session 1, `--rebase` after the launch).
     - **(e) Acceptance level of the repair:** structural now (prim gate + terminal types read back equal to the old node's); functional only
       at P6's recorded-frame replay (arrays stay length 20, X/Y/Z bit-identical, PD238(f)). The bed is broken by design, so nothing earlier
       can run it.
     - **(f) steer_140 FOLLOWED:** the cycle's LabVIEW act is a P4 build session saving an in-between file of the deliverable (M3); every
       user question is answered (`decisions_pending.json`: none open).
324. **(cycle 141 judgement, 2026-10-02 — after 141-1 PASS 6/0 (`tools/bench/prep_c141_1_facts.md`))**
     USER-RULES: U1 (relied on: the end graph and computation_diff are identical to PD323(a)'s; only the edit order changes); none contradicted.
     - **(a) ACCEPTED: v16 `plan_ring_p4_v16.json` 36981c83** (50 repair actions + v15's 185; replay END, end cdiff == v15's 24, 217 ops),
       prim gate run-time (`stagexec.py:435-461`) + offline X17 (`stage_prerun.py:2528-2606`), self-tests 13/0, X10-provisional 4/0.
     - **(b) RATIFIED: CREATE-FIRST repair order** (create RAS from uid 175, branch the 3 inputs from their existing nets, delete the old
       output wire + old node, RLE the 3 old inputs — each still has the new RAS as sink, so PD321's whole-wire hazard cannot occur —
       then wire the output). PD323(a)'s delete-first order is unroutable: a deleted node's FS-tunnel-face endpoints vanish from
       `Diagram.Nodes[]` (`prep_c141_1_mkv16.log:11-13`). A branch from an FS tunnel face is UNMEASURED: session 1's scratch is its test.
     - **(c) `p4_eq_seq` donor (X17 refusal, session 5):** `$work` #10171 is deleted by `p4_do_10171`; replace it by an `Equal?` node of
       the bed graph that v16 never deletes, preferring one whose x/y are I32; ops 1..24 must stay unchanged (s01 stays valid) → v17.
     - **(d) Session 1 = `plan_ring_p4_s01.json` f4831031** (24 actions: #27928, #28916 repaired, #29048 created + 3 branches), X10 669.3
       scratch / 674.4 launch, Error List predicted 51. Card 141-2 = PD320(e) with PD323(d)'s gates; beside it prep 141-P1 (v17 + s02).
325. **(cycle 141 judgement, 2026-10-02 — after 141-2 FAIL 24/1 (`tools/bench/diag_c141_2_facts.md`), review
     `archive/peer/2026-10-02-c141-2-scratch-td.md`, 141-P1 PASS 29/0 (`tools/bench/prep_c141_p1_facts.md`))**
     USER-RULES: U1 (relied on: no edit changes; only a gate's terminal key and the census prediction change); none contradicted.
     - **(a) MEASURED in the scratch:** ops real == sim (24), PB cdiff == pred, prim gate 3/3 'Replace Array Subset', peak 601.4 MB. The one
       FAIL is gate TD: lost base terminals 6 vs plan deletes 8, the two "survivors" 28004 / 28979 are terminals of the NEW nodes
       (`diag_c141_p4s01_scratch.log:167,267,280`). Hypothesis (review, supported in substance): LabVIEW re-uses a deleted object's uid in
       the same session; a raw-uid key cannot tell old from new. First session that deletes and creates nodes on the same frames.
     - **(b) DECISION — fix the KEY, not the plan:** TD / unwired / D compare terminals by (uid, owner uid, name), wherever they are computed
       (stagekit first, so every later session gets it), with a self-test built from 141-2's log case; preceded by an OFFLINE owner check
       from the logs that 28004/28979 belonged to deleted nodes in the base graph and to #6942/#6805 in the scratch (else return).
     - **(c) Census:** the scratch's measured census (GrowableFunction +1, Terminal +4, …) is written into `plan_ring_p4_s01_pred.json` by
       script citing the log line (PD264(c) precedent), so CEN2 is predicted at the launch.
     - **(d) Retry = card 141-3** (retry_of_card 141-2): fix + self-test, re-dry/prerun, ONE scratch rerun (2nd of the cycle, within the cap),
       then the gated launch exactly as PD323(d). X10 over-predicted again (669.3 vs 601.4; 2nd point after 140-3) — still not recalibrated
       (PD323(c) needs 3).
     - **(e) 141-P1 ACCEPTED:** v17 e19d7e14 (`p4_eq_seq` donor #10019, Equal? is polymorphic and adapts to I32 on wiring; the session-5
       scratch + prim gate measure it); s02 5e483ea6 = v17 ops 25..54 provisional. Its X10 675.0 is at the limit: after `--rebase` the cut is
       recomputed from session 1's MEASURED load (PD320(d)) and stands only if X10 ≤ 675.
326. **(cycle 141 judgement, 2026-10-02 — after 141-3 PASS 6/0 (`tools/bench/diag_c141_3_facts.md`))**
     USER-RULES: U1, U13 (relied on: session 1's edits are the planned ones, read back; none contradicted).
     - **(a) P4 SESSION 1 DELIVERED (in-between file, not counted toward the 6-file cap, user D-02/D-04):**
       `claudeDev\D1_ring_p4s01_20261002_232547.vi` md5 `dc61e193e0376ce760f88fdfcda7087b`; scratch 23/0 and launch 23/0 (same uids), prim
       gate PASS on every created node, full Error List 51 = expected (0 extra / 0 missing), peak 605.0 MB; graph
       `tools/bench/graph_ring_p4s01_20261002_234419.json` (load 596.5 MB, after full read 607.3). Bed slot writes `#27928`, `#28916` are now
       Replace Array Subset (`#6942`, `#6805`); `#29048`'s new RAS is created and branched, its swap finishes in session 2. STRUCTURAL only.
       The bed key does NOT move (P4 is one counted file at its end); session 2 starts from this file.
     - **(b) ACCEPTED:** `stagekit.term_identity_gates` (TD / unwired / D by (uid, owner, name), self-test 9/0); the first read of a NEW file
       dry/preruns with `--graph <its input's graph>` as stand-in (no graph exists for its md5 yet) — standing form.
     - **(c) X10 still NOT recalibrated:** the three over-prediction points (−58, −68, −64 MB) all come from session 1 (two plan versions), and
       P3b launches matched within 0.4 MB — the cause is unmeasured. Session 2 uses start = 596.5 (measured load, PD320(d)); recalibrate after
       session 2 gives a second session's point.
     - **(d) Carry, not ahead of the build:** stagexec's binding (`stagexec.py:946-950`) compares raw `term_uid` sets; uid re-use inside one
       bind op would make a new terminal look old. A failure there is LOUD (binding finds no new terminal) and the scratch returns before any
       launch — so it is fixed when hit, not pre-emptively (deliverable first, steer_140).
     - **(e) Cycle 142 FIRST act = P4 session 2 build card** (LabVIEW, alone): `stage_prerun.py --rebase plan_ring_p4_s02.json --graph
       graph_ring_p4s01_20261002_234419.json`, cut re-checked at start 596.5 (≤ 675, else re-cut by PD320(c) before the scratch), dry/prerun,
       ONE scratch on a byte copy of the session-1 file, gated launch (all PASS + EL == pred + peak ≤ 675) saving `D1_ring_p4s02_*.vi`, load +
       graph read. Beside it: offline prep of session 3 (provisional on stagesim's end of s02).
