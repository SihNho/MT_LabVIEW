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

**USER DECISIONS 2026-10-03 (chat, recorded verbatim; the next judgement agent numbers them as the next PD and plans by them):**
- **P4 FROM HERE ON IS BUILT WITH SUBVIs** ("P4부터 그렇개 진행하자", after "Subvi해도 local variable을 직접 노드에 꽂아주면
  되는거 아님?"). The caller (loop 1.2 in the bed) keeps the LOCAL reads/writes and their seqlock ORDER (n1 = Num(i) read →
  track → n2 = Num(i) read; Latest/`last` handling; StopAll); the pure computation becomes small subVIs built and verified
  in their OWN small VI files under claudeDev (inputs → outputs, no locals, no refs): e.g. slot selection (smallest
  Num > last, jump to newest on overwrite) and the overwrite check + rollback Selects (the 43-action block). The bed then
  only gets the subVI nodes + the local reads/writes + their wires. Each subVI is RUN on known values (functional) before it
  is dropped into the bed. P2/P3 (camera side) and the saved P4 session-1 file `D1_ring_p4s01_20261002_232547.vi` (the
  RAS repair) are kept as they are. This supersedes (e) above (session 2 of the per-node plan v17): re-plan P4 around
  the subVIs first.
- Process (cards chat-S2/S3/S4): STOP vs LOG gate table `tools/gateclass.py`; memory limits 680 MB predicted / 695 MB
  MEMSTOP (LabVIEW error 2 measured at 704.8 MB); tunnel OBJECT count differences stay STOP; tunnel face-row-only step
  diffs are LOG; adopt a fully passing scratch file as the stage result (no re-run on the bed); per-node reads instead of
  per-BIND whole-VI reads; resume from the stop point within a cycle.

330. **(cycle 142 judgement, 2026-10-03 — the user's 2026-10-03 subVI decision above; after 142-1 FAIL 9/1
     (`tools/bench/diag_c142_1_facts.md`), 142-P1 FAIL 17/1 (`tools/bench/prep_c142_p1_facts.md`, table
     `tools/bench/prep_c142_p1_subvi_table.md`))**
     USER-RULES: U1 (relied on: a subVI holds exactly the plan's primitives and wires, checked by running it against a Python
     reference of the same plan group; X/Y/Z equivalence still only at P6), U4 (relied on: locals stay in the caller; a subVI
     has no locals, refs or registers), U9/U13 (relied on: seqlock order n1 → track → n2 stays in the bed, untouched); none
     contradicted.
     - **(a) The P4 subVI list = TWO subVIs.** v17's 185 non-repair actions hold 6 pure groups (55 actions); only two are
       more than one node: **S1 `RingPickSlot_v0.vi`** = G2 minus `p4_or_w1` (Greater?, For + Select + I32-MAX, Array Max &
       Min, Less?; in `Num`, `last`; out `min Num`, `min slot`, `found`) — the `Or` with the `StopAll` local is W1's stop and
       stays in the bed; **S2 `RingSeqCheck_v0.vi`** = G5's scalar core (`p4_eq_seq`, `p4_gt_n1`, `p4_and`, `p4_dec`,
       `p4_sel_last`, `p4_sel_disc`, `p4_inc_disc` and their inner wires; in n1, n2, last, Latest, discard count; out valid,
       next last, next discard count). Exact terminals are read from v17's wires by the build card, never re-typed.
     - **(b) The seven rollback Selects (`p4_rb*`) and the single Index Arrays (G7–G10) stay bed primitives:** each is one
       node, their types differ per register (arrays/clusters of the original, unstated in plan and graph), and a typed
       subVI per register would add a file and a connector pane for zero removed nodes.
     - **(c) Each subVI is accepted FUNCTIONALLY in its own file:** built from `EMPTY_v0.vi`, ExecState 1, run on fixed
       vectors whose expected outputs come from a Python reference of the plan group, re-run from the saved file in a fresh
       instance (brief `tools/bench/cards/brief_142-1.md`). Only then is it dropped into the bed (`drop_subvi`).
     - **(d) The remaining slot-write repair (v17 #25..#50, 26 actions) is one bed session** `plan_ring_p4_rasrest.json`
       4ad2d288, unchanged by the subVIs. Its `--rebase` onto the s01 graph is refused by the binder's raw-uid key (s01's
       re-used terminal uids 28004/28979, PD325(a)): fix the REBIND key to (uid, owner, name) as PD325(b) did for TD, with a
       self-test from this case — a stage-tool card, run ALONE (PD281(a)). Not planning rasrest on the real graph by hand.
     - **(e) 142-1's failure = our script** (strict per-delete count after a For delete); retry 142-2 checks the scaffold
       cleanup by one end census. Then v18 = v17 with S1/S2 groups replaced by two subVI nodes + boundary wires (prep card).
331. **(cycle 142 judgement, 2026-10-03 — after 142-3 PASS 87/0 (`tools/bench/diag_c142_3_facts.md`), 142-4 PASS 121/0
     (`tools/bench/diag_c142_4_facts.md`), 142-P2 PASS 13/0 (`tools/bench/prep_c142_p2_facts.md`))**
     USER-RULES: U1 (relied on: each subVI's outputs equal a Python reference DERIVED FROM v17's wires on 7 vectors; v18's end
     cdiff == v17's), U4, U9/U13 (relied on: locals and seqlock order untouched in the bed); none contradicted.
     - **(a) BOTH P4 subVIs DELIVERED, FUNCTIONAL in their own files:** `claudeDev\RingPickSlot_v0.vi` md5 `6fcf153f…`
       (pane 11 Num / 10 last → 3 min Num / 2 min slot / 1 found) and `claudeDev\RingSeqCheck_v0.vi` md5 `0295a8d3…`
       (pane 11 n1 / 10 n2 / 9 last / 8 Latest / 7 discards → 3 next last / 2 next discards / 1 valid; valid = n1==n2 AND
       n1>last, next last = valid ? n1 : Latest−1, next discards = valid ? discards : discards+1 — v17's arithmetic). Each ran
       7/7 vectors == reference and 2 vectors again from the saved file in a fresh instance. They are not broken
       intermediates (ExecState 1) and do not count toward the 6-file cap.
     - **(b) ACCEPTED: plan v18 `plan_ring_p4_v18.json` 2ea6cafa** (202 actions, 190 ops; PS1 op 79, SQ1 op 88; replay END;
       end cdiff == v17's 24 rows). S2's provisional names equal the measured pane (142-4 log:199) — the provisional mark is
       discharged; v18 needs no re-make for names.
     - **(c) X10 cut limit = `memory_model.json` (680, PD328)**, which supersedes PD326(e)'s 675; the launch MEMSTOP stays 695.
       Loading a subVI file at drop is UNMODELLED: the scratch run's measured peak is the check (PD323(c) precedent).
     - **(d) Rebind key fix now, ALONE (PD330(d)):** card 142-5 (offline, edits stage tools) — rebind compares terminals by
       (uid, owner, name), self-test from 142-P1's refusal, `c125_1_offline_measure.py` rerun (PD252(a)); then session 2 of
       v18 = ops 25..(cut at 680) rebased on `graph_ring_p4s01_20261002_234419.json`, dry + prerun + X10 + EL prediction +
       recipe pair. `plan_ring_p4_rasrest.json` is superseded by that session (same 26 repair actions at its head).
     - **(e) Open notes kept as notes:** `gscript.for_loop` leaves 3 junk constants per call — per-caller delete stays (no
       shared-tool change now; documented `docs/toolkit-capabilities.md:60`); gate-fp fp-36 (guard_peer lacks the reverse of
       RULE-OFFLINE-CARD) is queued.
332. **(cycle 142 judgement, 2026-10-03 — after 142-5 PASS (`tools/bench/prep_c142_5_facts.md`))**
     USER-RULES: U1 (relied on: session 2's 34 actions are v18's, unchanged; only the binder's key changed); none contradicted.
     - **(a) ACCEPTED:** rebind key (uid, owner, name) (`tools/stage_prerun.py:3456-3471,3492-3493`, self-test
       `selftest_rebind_c142_5.py` 1/3 before → 4/0 after; old rebind/rebase/c125_1 green). Cause MEASURED: 28004/28979 were
       `output array` of deleted #27928/#28916, re-issued to new #6942/#6805.
     - **(b) ACCEPTED: P4 session 2 = `plan_ring_p4_s02v18.json` e941ebbf** = v18 ops 25..58 (34 actions: the 26 remaining
       slot-write repair actions + the first reader actions), rebased on the s01 graph, dry PASS, prerun 16/0, X10 678.5 ≤ 680
       at 596.5. `plan_ring_p4_s02.json` (v17) and `plan_ring_p4_rasrest.json` are SUPERSEDED — never launch them.
     - **(c) Census:** derived {} (all 34 census-unpredicted) ⇒ `--scratch-required` exit 3: the scratch run is required and
       its MEASURED census becomes the launch prediction (PD261(c)/PD325(c) precedent). Error List predicted 51, alternative 52
       (#23166 newly unwired) — the scratch decides which; a third value is a return.
     - **(d) The prior-art review of `stage_d1_ring_p4_s02v18.py` is owed before its scratch** (not a proven pattern: the
       repair has one clean launch). Cycle 143's LabVIEW card dispatches it first (peers `priorart`), then the scratch on a
       byte copy of `D1_ring_p4s01_20261002_232547.vi`; when the scratch passes every gate it is ADOPTED as session 2's file
       (PD329(a)) — no second run on the s01 file; full Error List, load + graph read in a fresh instance.
333. **(cycle 143 judgement, 2026-10-03 — after 143-1 FAIL 3/1 (`tools/bench/diag_c143_1_facts.md`), 143-2 PASS 5/0
     (`tools/bench/diag_c143_2_facts.md`, review `archive/peer/2026-10-03-c143-2-el53.md` verdict supported), 143-P1/P2)**
     USER-RULES: U1 (relied on: the s02 file's 34 actions are v18's, real == sim, no computation change; only the Error
     List PREDICTOR was wrong); none contradicted.
     - **(a) ADOPTED: `claudeDev\D1_ring_p4s02_20261003_110001.vi` md5 `84cac487…` = P4 session 2's file (PD329(a))**, Error
       List **53** = the by-design session-boundary state, MEASURED by uid: the 1.2 While `#10170` conditional terminal
       (`#23246`, its scaffold wire w23310 deleted by plan) and the StopAll READ Local `#6902` (output unwired) are both open
       in the s02v18 simulated end and both wired by s03's first action `p4_w_stop12`. Graph `graph_ring_p4s02_20261003_112505.json`
       eda9db40, load 596.0 MB. In-between file, not counted (D-2026-10-02-02/-04).
     - **(b) The EL predictor is fixed BEFORE s03's scratch** (`prep_c142_5_pred.py:65-87`, same in `prep_c143_p1_pred.py`):
       a created node with an unwired OUTPUT (source-only Local) and a base loop whose cond wire the plan deletes count as
       CERTAIN items, and an item that disappears is debited; re-deriving s02 must give 53. Otherwise s03's check (54 on a
       51 base) could pass by cancellation.
     - **(c) Session 3 = `plan_ring_p4_s03v18.json`** (v18 ops 59..78, 20 actions; recipes ported, 143-P2): `--rebase` onto
       the s02 graph, X10 at the measured 596.0 (provisional margin was 3.1 MB at 596.5), dry + prerun, EL prediction from
       the fixed predictor; then ONE scratch on a byte copy of the s02 file and adoption on full PASS (PD329(a)).
334. **(cycle 143 judgement, 2026-10-03 — after 143-3 FAIL 13/1 (`tools/bench/prep_c143_3_facts.md`))**
     USER-RULES: U1 (relied on: a binder/guard change alters no plan action; s03's 20 actions stay v18's); none contradicted.
     - **(a) DONE by 143-3:** s02 ADOPTED (`adopted_scratch.jsonl`, `adopt_scratch` by import — the CLI form was refused
       under `labview: none`, gate-fp fp-39); expected EL file 53 (compare extra [] missing []); EL rule
       `tools/bench/prep_c143_3_elrule.py` (self-test `selftest_elpred.py` 7/0: s02 → 53, s01 → 51).
     - **(b) The `--rebase` refusal is a misapplied guard, not a plan defect.** `stagexec.uid_reuse` (`stagexec.py:942-962`)
       is written for TWO CONSECUTIVE reads around ONE op; `--rebase` (`stage_prerun.py:3453-3455`) feeds it the s01 base vs
       the real s02 graph, 34 ops apart, across planned deletes — where LabVIEW re-issuing a freed uid is EXPECTED (NI; uid
       23276 = deleted Comparison #10171's term → new Local #6899's `StopAll` sink, s02 scratch log :391 recycled_uids).
       Same class as PD325(b) (TD) and PD332(a) (rebind): a raw-uid key across a delete boundary. Rule: in `--rebase`
       a re-issued uid is FATAL only when the plan being rebased names that uid (actions or bindings); otherwise it is
       logged `REUSE-NOTED` and binding goes by (uid, owner, name). Execution-time use of `uid_reuse` is UNCHANGED.
     - **(c) Close the class, not the instance:** the tooling card lists EVERY cross-graph comparison in stagexec /
       stage_prerun / stagekit that keys terminals or owners by raw uid (file:line, which graphs it compares, whether a
       delete can lie between them), fixes those on the rebase/rebind path by the same rule, and reports the rest
       without changing them. Self-test from this case + the 28004/28979 case; `c125_1_offline_measure.py` rerun (PD252(a)).
       Stage-tool card, ALONE (PD281(a)). Then s03's rebase → X10 at 596.0 → pred → dry/prerun → scratch-required.
335. **(cycle 143 judgement, 2026-10-03 — after 143-4 FAIL 5/1 (`tools/bench/prep_c143_4_facts.md`))**
     USER-RULES: U1 (relied on: only the terminal ADDRESS of s03's actions changes, to the measured name; no action is
     added, removed or rewired); none contradicted.
     - **(a) ACCEPTED: PD334's rebase fix** (`stage_prerun.py` 03cdd8c6: rebase passes the plan's named uids; a named re-issue
       refuses, an unnamed one logs REUSE-NOTED; census 19 sites, 4 rebase-path sites fixed; self-test
       `selftest_rebase_uidreuse_c143_4.py` U2–U6 PASS; old rebind/rebase self-tests + c125_1 green; stagexec unchanged).
     - **(b) The s03 plan's address is corrected to the MEASURED name**, not aliased in the binder: `p4_w_stop12`'s source
       `{uid -20, term 'value'}` → `term 'StopAll'` (provisional base row -21 and the real s02 graph both name the Local's
       terminal `StopAll`; `stagesim.py:735-736`'s `value` alias is a simulator convenience the binder does not share).
       Every other s03 action that addresses a Local terminal by `value` is corrected the same way, by a script that reads
       the name from the base rows (never typed). U1 then must PASS; dry and prerun confirm the executor resolves it.
336. **(cycle 143 judgement, 2026-10-03 — after 143-5 FAIL 2/2 (our pred script tokenised `why` text), 143-6 PASS 8/0
     (`tools/bench/prep_c143_6_facts.md`))**
     USER-RULES: U1 (relied on: s03 = v18 ops 59..78 unchanged except PD335(b)'s measured address); none contradicted.
     - **(a) P4 SESSION 3 LAUNCH-READY:** plan `plan_ring_p4_s03v18.json` da66a030 (rebased on the s02 graph eda9db40, final,
       20 uids bound, REUSE-NOTED 23276), pred `plan_ring_p4_s03v18_pred.json` 7fab8cf0: X10 676.4 ≤ 680 at the measured
       596.0, **Error List predicted 56** (53 − 2 closed by `p4_w_stop12` + 5 new, uncertain []); recipes
       `stage_d1_ring_p4_s03v18.py` d420f951 / `_scratch.py` 573b8537 dry PASS, prerun 16/0 each; `--scratch-required` exit 3
       (census unpredicted) ⇒ ONE scratch on a byte copy of `D1_ring_p4s02_20261003_110001.vi` (84cac487), measured census
       into the pred, ADOPT on full PASS (PD329(a)) + full EL + fresh-instance load + graph read. Prior-art: NOVEL for both
       s03 recipes (`archive/peer/2026-10-03-priorart-c143-p2-p4s03v18.md`).
     - **(b) The 3.6 MB X10 margin is accepted:** X10 ran 58.2 MB above s02's measured peak (678.5 vs 620.3) and MEMSTOP 695
       guards the run. `new:LRB1.value` / `new:LWB1.value` on CREATED Locals resolve in the sim only (`stagesim.py:735`);
       the scratch is the measurement — a refusal there is a return, and the fix is PD335(b)'s measured-name rule.
     - **(c) EL predictor rule in force: `tools/bench/prep_c143_3_elrule.py`** (unwired outputs of created nodes, plan-cut
       loop conds certain; closed items debited) — every later P4 session's pred uses it.
350. **(cycle 145 judgement, 2026-10-07 — after cycle 144 PURPOSE_MET (`tools/bench/cards/assign_result_144_2.json`))**
     USER-RULES: U1 (relied on: s04 = v18 ops 79..97 as rebased, no action changed by this item); none contradicted.
     - **(a) ACCEPTED: P4 session 3 ADOPTED** — `claudeDev\D1_ring_p4s03_20261007_202957.vi` 282301ca, EL 55 == pred
       (expected `errorlist_expected_D1_ring_p4s03_20261007_202957.json` 2b8f9f25), fresh load 598.5 MB, graph
       `graph_ring_p4s03_20261007_205535.json` 5638469b (`tools/bench/diag_c144_2_facts.md`). In-between file, not counted.
     - **(b) s04's X10 margin −0.1 MB (680.1 vs 680 at 598.5, `prep_c144_a2_2_facts.md:23`) is ACCEPTED without a re-cut.**
       X10 has not under-predicted a measured P4 peak (s02 678.5 vs 620.3, s03 676.4 vs 673.7); the run is a SCRATCH on a
       byte copy, so the recipe's runtime stop at 680 MB (`MEM_STOP_MB`, unchanged) is the guard: a stop there is a RETURN,
       and the pre-decided fix is the re-cut to ops 79..96 (op 97 → s05, EL re-derived by PD349). No memory-model change.
     - **(c) `diag_c144_2_el.log` rc=1 is a comparison against the SUPERSEDED s02 expected file**; the same Error List
       compared with the s03 expected file is extra 0 / missing 0 (`diag_c144_2_elexp.log`). If a gate holds s04 on it,
       follow that gate's own route (Jev ladder NEXT-ACTION, else one hypothesis review citing elexp.log) — never a bypass.
     - **(d) W1 While #16483 carries the uid of the wire s03 cut (w16483)**: s05+ plans key it by (uid, class); the s04
       rebase already bound it by the creation map (row-less, no REUSE-NOTED).
     - **(e) Cycle 145 = ONE s04 scratch → adopt on full PASS (PD329(a)) + beside it the s05 prep** (v18 ops 98.., provisional
       on stagesim's end of s04, made like `tools/bench/prep_c144_p1_mk.py`, recipes copied from the s04v18 pair).
351. **(cycle 145 judgement, hand-back 1, 2026-10-07 — after 145-a1-1 FAIL (SQ1 row provisional), 145-a1-2 FAIL 3/1
     (`tools/bench/diag_c145_2_facts.md`, `tools/bench/diag_c145_2_elfacts.log`))**
     USER-RULES: U1 (relied on: s04 = v18 ops 79..97, only SQ1's terminal LIST corrected to its measured pane; no action
     added, removed or rewired); none contradicted.
     - **(a) ACCEPTED: the SQ1 row fix** (plan 9ff46b0e → f349c39a, 12 measured rows in t-order from the 145-a1-1 read; re-sim
       FINAL, end cdiff / open rows / fs_routes unchanged; sim ids after SQ1 shift −4). Review `c145-1-sq1-bind`: the missing
       prerun check (a `subvi_path` create's terminals vs its measured pane) is tool debt, built only if a third subVI drop
       is planned with an unread pane.
     - **(b) Error List 58 vs pred 60 is EXPLAINED, not a third unexplained value — s04 scratch 95e408ff is ADOPTED.** Per
       class against the s03 expected file (55): While cond −1 and local 29720 −1 closed as predicted; locals +2 (−51, −32)
       as predicted; Index Array +3 = the three created Index Arrays (−53, −34, −26) as predicted; the only predicted items
       NOT read are the two SubVI drops PS1 (−1) and SQ1 (−38) — no "required input" item appears for either. E1 real == sim
       at all 19 ops and 24/0 gates are the structural verdict; the Error List is a cross-check and it differs only there.
       Working cause: LabVIEW lists an unwired SubVI input only when the pane terminal is **Required** (the s03 item
       `TrackNbeads… required input imageIn is not wired` is such a case); our two subVIs' inputs are presumably
       Recommended. This cause is MEASURED in the adoption card (pane requiredness of `RingPickSlot_v0.vi` /
       `RingSeqCheck_v0.vi`); if any of their unwired inputs reads Required, the explanation fails → return.
     - **(c) EL rule fix (`tools/elrule.py`, PD349):** a SubVI create contributes one item per unwired input whose pane
       terminal is MEASURED Required (read from the subVI, never assumed); self-test re-derives s01/s02/s03/s04 =
       51/53/55/58. Stage-tool edit ⇒ its own card, never beside a LabVIEW card (PD281(a)).
     - **(d) s05 prep is re-made**, not patched: its provisional base was stagesim's end of 9ff46b0e (ids now −4); after s04
       is adopted, s05 = v18 ops 98..124 is cut on the REAL s04 graph (rebase), X10 at the MEASURED s04 load, EL by (c),
       dry + prerun + `--scratch-required`. **No s05 launch in cycle 145**: X11 (Build Array #2626 inputs wired by
       `p4_w_tp_row`/`p4_w_rp_row` while (2626, array) is an open row whose licence names only `plan_l2b1.json`) is a
       judgement item; the card reports where v18 closes (2626, array) and which session wires it.
     - **(e) Housekeeping:** the stopped work copy `claudeDev\D1_ring_p4s04_20261007_212230.vi` (abb76d41) is superseded —
       delete it with its resume record after the adoption; 95e408ff is the adopted file's source.
352. **(cycle 146 judgement, 2026-10-07 — after cycle 145 PURPOSE_MET (`tools/bench/cards/assign_result_145_2.json`); facts
     `tools/bench/diag_c145_a2_6_facts.md`, `tools/bench/diag_c145_a2_x_facts.md`; review `archive/peer/2026-10-07-c145-s05-x10.md`)**
     USER-RULES: U1 (relied on: only the session CUT and an addressing licence change; every v18 action, its sources and sinks
     stay as accepted in PD331(b), end cdiff == v17); none contradicted.
     - **(a) ACCEPTED: cycle 145.** s04 ADOPTED (`D1_ring_p4s04_20261007_215031.vi` 95e408ff, EL 58, fresh load 605.4 MB, graph
       `graph_ring_p4s04_20261007_223245.json`); the two subVIs' inputs measured Recommended, none Required ⇒ PD351(b)'s cause holds;
       `tools/elrule.py` SubVI = Required inputs only, self-test 21/0 (51/53/55/58). s05 rebased (0efd8737, pred 55) — NOT launchable as cut.
     - **(b) ONE X10 start rule: the gate tool's own `x10_start` (`tools/stage_prerun.py:2043-2052`, `memory_model.json:69`) =
       MEASURED fresh load + the op-0 read.** It is the code in force, and s03's metered start (600.7 vs 596.0 load, +4.7) agrees with it
       within 1.2 MB; the prediction scripts' "start = fresh load" was our inconsistency. s04's metered start 35 MB BELOW its load only
       makes this rule conservative. So: record 95e408ff's measured load 605.4 in `memory_model.json` `load_by_vi` (a record, no
       parameter or limit changes — fail_above 680 and MEMSTOP 695 stay), and the prerun's own X10 and the pred then use one start.
       s05 is RE-CUT: the longest prefix of v18 ops 98.. that splits no 'of' group and has X10 ≤ 680 at that start (review: about
       op 116); the rest moves to s06. The review's load-only scratch is NOT run: neither of its outcomes changes this cut. The s05
       scratch's metered start and peak are recorded as calibration data.
     - **(c) X10 recalibration (PD322(c)'s "≥ 3 measured P4 sessions" is met) is DEFERRED, not skipped:** 4 of 5 points over-predict by
       58–68 MB but s03 by only 2.8, and the spread comes from the START term (s04: −35 MB vs its load), not from the per-op growth.
       A fit that never under-predicts is held at s03, so it would gain almost nothing. Recalibrate when two metered starts under rule
       (b) exist (s05 + s06); then fit the start term, not the growth term.
     - **(d) X11 on #2626 gets a uid-keyed LICENCE, not a plan change.** The rows that wire #2626 inputs (`p4_w_tp_row` t4160,
       `p4_w_rp_row` t4165; later `p4_w_bd_row` t2832, `p4_rbB_sel_t4168` t4168) are accepted v18 actions (PD331(b)); X11 protects
       NAME-keyed addressing from a sibling rename, and every one of these rows and the later rebase/rebind key the open sibling by
       term uid. The session plan that carries ops 118/119 gets `tools/bench/plan_ring_p4_<session>_licence.json` (`pb-licence/1`,
       `plan` = that session plan, `rename_by_uid` node 2626, term_uids = its still-open #2626 input uids; `require`: "every listed
       uid is an input of #2626 in the real end read with the same uid, unwired unless this session wires it, else the licence is
       void"; `decided_by` = this item). The scratch's end read records #2626's terminal names and types (facts, not a gate), so a
       rename shows up as data; a changed uid voids the licence ⇒ RETURN. Same rule for whichever later session carries ops 132/150.
     - **(e) gate-fp drain (DUE, 8 open) = ONE tooling card, ALONE, FIRST:** fp-43/45/47/48/49/50 are one class — `guard_write.py:84`
       reports a card's own authorised edit of a file it both pins and lists in `flags.write` as a stale copy; fp-44 (Jev ladder
       `new-problem` on an offline json helper) and fp-46 (a pred log's report-only rc=1 X10 line counted as a failing run) are
       `guard_peer`. Fixes in `tools/hooks/guard_write.py` / `tools/hooks/guard_peer.py` are authorised by the cycle-146 purpose.
     - **(f) Cycle-146 order:** (e) alone → s05 re-cut + pred + dry/prerun (X11 PASS or licensed by (d)) → ONE s05 scratch on a byte copy
       of 95e408ff, ADOPT on full PASS (PD329(a)) + full EL + fresh load + graph read; beside the scratch the s06 prep (provisional on
       stagesim's end of s05). Housekeeping: copy `tools/bench/build_opwiringrules_v0_hygiene.json` into `tools/bench/op_hygiene/`.
353. **(cycle 146 judgement, hand-back round 1, 2026-10-08 — `tools/bench/cards/handback_146_1.json`, facts
     `tools/bench/diag_c146_a1_4_facts.md`, `tools/bench/diag_c146_a1_5_facts.md`, review `archive/peer/2026-10-08-c146-a1-4-el55.md`)**
     USER-RULES: U1 (relied on: no v18 action, source or sink changes; the s05 bytes are adopted as built; only a PREDICTOR and a
     maker self-check change); none contradicted.
     - **(a) ACCEPTED from round 1:** gate-fp fp-43..50 drained (146-a1-1); 605.4 in `load_by_vi`, one X10 start rule, s05 re-cut to
       v18 ops 98..114 (X10 674.9), dry + prerun PASS (146-a1-3); OpWiringRules hygiene record copied. 146-a1-2 FAIL is superseded.
     - **(b) The s05 scratch is a STRUCTURAL PASS and its Error List miss is OUR PREDICTOR (as PD351(b)):** 22/0 gates, E1 real == sim at
       all 17 ops, D new 11 == 11 / lost 1 == 1, PB 11 open pairs; peak 607.7 MB. EL 55 vs pred 57 = 2 items the predictor kept open
       although s05 rows close them: `elrule.session_prediction` calls `predict` with no `carry` (`tools/elrule.py:217-225`), so base
       input items closed in this session (#5058 'Image In' by `p4_w_img_trk`; #29843 by `p4_t_slot_out`/`p4_w_pool_in`) are not
       subtracted. The per-class read agrees: SubVI 'Image In' −1 and Index Array 3 vs 4; SR and Local are as predicted.
     - **(c) Fix the predictor FIRST, ALONE (stage-tool edit, PD281(a)):** `session_prediction` passes the base's still-open input items
       as `carry` (or the equivalent subtraction); self-test re-derives s01..s04 = 51/53/55/58 UNCHANGED and s05 = 55 with
       **per-class counts equal to the read file** `errorlist_D1_ring_p4s05_20261008_002621_20261008_003324.json` (06a59001). A total
       match with a per-class mismatch is NOT a pass — that is the guard against fitting the predictor to the answer.
     - **(d) ADOPT the existing s05 work copy, no second run (PD329(a)):** `claudeDev\D1_ring_p4s05_20261008_002621.vi`, md5 3f9ac26b
       verified unchanged → `D1_ring_p4s05_*.vi` (the prepared `diag_c146_a1_4_adopt.py` / `_mkgraph.py` / `_graph.py` / `_t2626.py`).
       The full final-role EL read of those same bytes (55) is the expected file; fresh-instance load + graph read; the measured load
       goes into `memory_model.json` `load_by_vi` (a record; limits unchanged). The metered start 577.8 / peak 607.7 are the
       first calibration point of PD352(c).
     - **(e) s06 maker kind gate: `branch` → `connect` is ALLOWED when the source symbol was created in an EARLIER session** (v18 op 116
       `p4_w_idx_frameidx`, src `new:TS1.outer` = s05 uid). The compiled kind follows the source form (`stagexec.py:808-813`): a
       symbol from this plan is `branch`, an existing uid is `connect`; it is the exact pair of the already-allowed `wire_sr` → `connect`,
       and both make the same wire net. The computation check stays the maker's end comparison (s06 sim end == v18's end over the same ops)
       and the scratch's E1. Connect from an already-wired existing source is the route every base-sourced connect since P3 has used.
       Fix the gate in the maker script (prep file), not in `stagexec`.
     - **(f) Then s06 = v18 ops 115.. re-made on the REAL s05 graph:** rebase, X10 start by PD352(b) at s05's MEASURED load (the
       provisional 623.5 is void), cut = longest group-respecting prefix with X10 ≤ 680, #2626 licence per PD352(d) (t4160 op 118 and
       t4165 op 119 fall in s06), EL by the fixed rule (c), dry + prerun both recipes, `--scratch-required`; then ONE s06 scratch on a
       byte copy of the adopted s05 → adopt on full PASS + full EL == pred PER CLASS + fresh load + graph read. A miss = RETURN.
     - ⚠️ (c) and the "EL == pred PER CLASS" clause of (f) are SUPERSEDED by PD354 (cycle 147).
354. **(cycle 147 judgement, 2026-10-08 01:16 — `tools/bench/cards/assign_result_146_3.json`, facts
     `tools/bench/diag_c146_a2_1_facts.md`, retrospective `archive/peer/2026-10-08-retrospective-cycle146.md:460-517`)**
     USER-RULES: U1 (relied on: the computation check is the scratch's real == sim graph comparison, unchanged; nothing about
     the v18 actions changes); none contradicted.
     - **(a) The Error List is a RECORDED CROSS-CHECK, no longer an adoption gate** (violation decision 2026-10-08 01:16). A
       scratch whose structural gates all PASS (E1 real == sim at every op, D new/lost, PB, prim, term identity, peak ≤ limit) is
       adopted; its full final EL read is the expected file; the per-class difference against the elrule prediction goes into the
       result card with one line of explanation. RETURN only when a class appears that is in neither the start read nor the
       prediction, or the total differs by more than 3. Four sessions (s02..s05) were held back by predictor gaps, none by a build
       fault — the EL items are unwired inputs of a broken-by-design in-between file, not the computation check.
     - **(b) elrule is NOT patched this cycle.** 146-a3-1's options V1/V3/VX are declined: the exact SubVI class needs #5058's
       identity and pane requiredness, i.e. a reader that binds an EL item to its node (the retrospective's missing tool, :489-492);
       that reader is wanted only if EL differences start to cost again. `tools/elrule.py` a5ee7d5c stays.
     - **(c) Order of cycle 147:** (1) ADOPT s05 3f9ac26b (PD353(d), unchanged) — FIRST, it never depended on elrule; its measured
       load is written into `memory_model.json` `load_by_vi` (that one entry; every limit unchanged). Beside it, offline: the s06
       maker kind gate (PD353(e)). (2) s06 on the real s05 graph (PD353(f), pred by the CURRENT elrule, scratch EL step made
       advisory per (a)). (3) ONE s06 scratch → adopt by (a). (4) Offline, any time: the runner's `retro-undisposed` gates_due
       entry (violation decision 2026-10-08 01:16).
355. **(cycle 147 hand-back 1 judgement, 2026-10-08 — `tools/bench/cards/handback_147_1.json`, facts
     `tools/bench/diag_c147_a1_4_facts.md`, review `archive/peer/2026-10-08-c147-a1-4-re1.md` (ANSWERED, disposed))**
     USER-RULES: none apply (a scratch-tool gate declaration; the v18 actions and the computation check are unchanged).
     - **(a) Cause accepted from the review, read from the code:** `gscript.wire_indicators` raises AFTER the wire is made whenever
       the target's ExecState != 1 (`tools/gscript.py:2148-2155`); every P4 bed is ExecState 0 by design, so on op 21 (`p4_rbA_re1`,
       #5058 'pos in cal image out' → indicator 'Pos within cal image') the raise says nothing about the wire. The device for exactly
       this is the recipe-owned SINK GATE (`tools/stagexec.py:2734-2758`, card 80-3): an op error passes only through a named gate that
       reads that exact sink. The s06 plan declared none (scratch log :310).
     - **(b) Fix = declare ONE sink gate in the s06 scratch recipe (and the s06 build recipe, same bytes of the declaration)** for
       the sink key as the run reports it, `[23166, 'Pos within cal image']`. The gate PASSes only when, read back from LabVIEW after op
       21, that indicator terminal is on the same wire net as #5058 'pos in cal image out' and the indicator terminal has exactly one
       source; anything else = ExecStop. No other sink is declared. `stagexec.py` and `gscript.py` are NOT edited (the device exists).
       E1 (real == sim at op 21) still has to pass on top of the gate.
     - **(c) Re-cutting s06 to end before `p4_rbA_re1` is declined:** the op still has to run in s07 on the same kind of bed and would
       hit the same raise.
     - **(d) Rerun, not resume:** ONE retry scratch (RETRY_CARD, `retry_of` the s06 scratch recipe) on a NEW byte copy of the adopted
       s05 `claudeDev\D1_ring_p4s05_20261008_002621.vi` (3f9ac26b), ops 1..21 from the start (443 s last time), so E1 covers every op
       on one file. The stopped work copy `D1_ring_p4s06_20261008_020717.vi` (b58046e3) is not resumed and not adopted; it may be
       deleted after the retry is adopted. A stop at any op other than this gate-covered sink = RETURN, no further retry this cycle.
     - **(e) Adopt by PD354(a)** (structural gates + EL recorded per class); then `memory_model.json` `load_by_vi` gets the s06
       measured load (that entry only; X10 / MEMSTOP limits unchanged). Calibration note kept: metered start 570.2 vs assumed 612.6,
       peak 618.7 vs X10 674.2 (the X10 start term is conservative by ~42 MB; not acted on this cycle).
356. **(cycle 147 hand-back judgement, 2026-10-08 — `tools/bench/cards/handback_147_1.json`, facts `tools/bench/diag_c147_a1_8_facts.md`,
     review `archive/peer/2026-10-08-c147-a1-8-re1.md` ANSWERED)** USER-RULES: U1 (relied on: wiring/edges must equal the sim; a
     name change is tolerated only where listed, and the S1 names must be back at the first ExecState-1 file); none contradicted.
     - **(a) Accepted from the review:** the retry's end wiring == the sim's end (t5171 → t10975 + t3173 on one wire); SG and E1 PASS
       at every op. D/TD/PB fail on their KEYS, not on the graph: TD/PB key by (uid, owner, NAME) (`tools/stagekit.py:1355-1357`) and
       ops 3/4/5/18 renamed #2626 2832/4160/4165 'array'→'element' and #9503 9505/9508 'Value'→'' (same uids, owners, wires); D keys
       by (wire uid, source) (`:1360-1371`), so w23807 reused on the same source t5171 reads as "kept" (15/16, 7/8).
     - **(b) Fix the GATES (stagekit, shared), not the plan:** a name change passes TD/PB ONLY when the session's licence file lists it
       exactly (`renames`: uid, owner, from, to), uid/owner/class are unchanged and the terminal's edges equal the sim's; any other
       rename still FAILs. D: a wire uid that a plan `delete_wire` removed and that is present at the end counts as lost + new
       (`REUSE-NOTED`) only when its end source+sink set equals a sim-created wire's AND the base sinks the sim takes off that net are
       absent from it; else FAIL. TD's "unwired" must read by (uid, owner), not by the old name. Self-tests: the 147-a1-8 end rows PASS;
       an unlisted rename FAILs; a reused uid with a different sink set FAILs; the stored s03/s04/s05 scratch verdicts are unchanged.
       Run ALONE (stage-tool edit), BEFORE any LabVIEW card.
     - **(c) Re-score first, offline:** D/TD/PB re-scored on `tools/bench/diag_c147_p4s06v18_scratch.json` with (b)'s rules must all
       PASS, PB's "4 missing for 3 renamed" must be explained from the code, and w23807's base sinks vs end sinks must be quoted (that
       settles "deleted + reused" vs "never deleted" without LabVIEW). Any remaining FAIL = a real graph difference ⇒ return.
     - **(d) The s06 licence gains the 5 measured renames;** the rename is a broken-intermediate type-propagation transient
       (`stagekit.py:1399-1404`, precedent `tools/bench/diag_c126_8_orig.py:79`), so **the first ExecState-1 file (P6) must read #2626's
       inputs back as 'array'** — a P6 gate, recorded here so it is not lost.
     - **(e) Then ONE more s06 scratch** (new RETRY_CARD, `retry_of` the s06 scratch recipe; the cycle's two runs are spent) on a NEW
       byte copy of 3f9ac26b, ops 1..21, no resume → adopt by PD354(a)/PD355(e). A stop on anything else = return, no further run.
