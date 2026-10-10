---
type: decision
kind: topic
status: current
date: 2026-10-10
parent: docs/d1/INDEX.md
tags: [d1, ring-buffer, p5, step-4, pre-decided]
---

# Ring buffer P5, step 4 onward (continues `docs/d1/ring-p5b.md`)

`docs/d1/ring-p5b.md` holds PD388..PD396 and is near the 400-line cap, so the P5 decisions from PD397 go here.
How to add: see the 5-line note at the top of `docs/d1/INDEX.md`.

## Pre-decided

397. **(cycle 164 judgement, 2026-10-10 — step 3 adopted; step 4 = the rest of A53..A80 by whole groups under X10; the
     K3/K4 pass wires get the adopted pass-wire shape; PB class 3 is tightened AFTER the LabVIEW card)**
     USER-RULES: U1 (relied on: A53..A80 are `plan_ring_p5s02r_in.json`'s actions as designed in PD374/PD379(b); the only
     row change is the missing `frame` key of two pass wires, which PD379(b) already specifies), U4, U13 (unchanged); none
     contradicted.
     - **Accepted (`tools/bench/cards/assign_result_163_1.json`, PURPOSE_MET 12/12):** the in-between
       `claudeDev\D1_ring_p5s02c_20261010_125755.vi` 564d8cbe (scratch 21/0, peak 602.0 ≤ 675), graph
       `graph_ring_p5s02c_20261010_131658.json` 3d5196ab, expected Error List
       `errorlist_expected_D1_ring_p5s02c_20261010_125755.json` 26d45c71, `memory_model.json` 8fb432e4 (one `load_by_vi`
       entry for 564d8cbe), census in the pred 721b9546, K3/K4 facts `tools/bench/diag_c163_a3_1_facts.md` 568381e7. The bed
       stays s09 until P5 ends (PD379).
     - **(a) The card's OPEN items, decided.** (1) Memory model ran HIGH (start 561.9 vs 607.1, peak 602.0 vs 653.2): it errs
       on the safe side, so it is NOT re-fitted inside P5. A crash at 680 costs more than one extra step. A re-fit needs ≥ 3
       start/peak samples from the same scratch path and comes after P6. (2) The assignment session's gate edit (PB class 3,
       stagekit dd57c1ca) is ACCEPTED for steps 3 and 4: the peer found no wrong row (`archive/peer/2026-10-10-c163-a1-4-pbchain.md`).
       Its three objections are ACCEPTED as tightenings, see (e). Changing a shared gate and setting aside a review is a
       judgement call; from now on a hand-back carries it (retrospective-cycle163 finding 7). (3) Stale stagekit pins
       (`selftest_c160_delwire`, `c161_delckpt`, `c155_basecase_frame`, `prep_c163_a1_3_pred/_md5`): PD396(a)(4) applies.
       Re-pin only a suite that a gate RUNS, by name, ONCE after (e) changes stagekit again. Everything else is history.
       (4) `selftest_c156_passwire.py:27`'s stale `stagesim.py:1536` citation: history.
     - **(b) K3/K4 GAP, decided from the facts (`diag_c163_a3_1_facts.md` §1-§3).** `w_k3pass` (A69) and `w_k4pass` (A79)
       carry no `frame` key, so the sink resolves to OK's own group frame (-29, 'False') and the sim stops on the border. PD379(b)
       places the pass wire in the TIMED-OUT frame between the in-tunnel's and the out-tunnel's 'True' faces. That is the
       shape already adopted three times in this graph: `w_gpass` A33, `w_hpass` A40 and `w_c7_pass` A52, with `frame: "True"`
       on BOTH ends (wire 31722 on frame 31517). **Decision: A69 and A79 get `"frame": "True"` on both ends in
       `plan_ring_p5s02r_in.json`. No other byte changes; a JSON compare shows exactly those 4 added keys.** This adds no
       computation: the pass wire carries the register value unchanged in the frame where no element arrived, as designed.
       The `new:CQ7` / `new:CQ7.f0|f1` references bind to base case #31308 through the step-3 run's binding record. The
       frame binding ('True' → its uid) is QUOTED from that record and never inferred from placement.
     - **(c) Step 4 = `plan_ring_p5s02d.json` on the real p5s02c graph 3d5196ab, mechanical memory rule.** The remaining
       groups, in plan order: J (A53..A60, `delete_object`), K3 (A61..A69), K3f (A70), K4 (A71..A79), K4f (A80). Step 4 takes the
       longest prefix of WHOLE groups whose MAIN (X10 on `SX.checkpoint_ops` from the measured start, `load_by_vi` 564d8cbe,
       limit 675 unchanged, read-only) is ≤ 675, with rows ≤ 40 (D-2026-10-01-01). A group is never split. If J alone is
       > 675, hand back. Any groups left over become the next step, planned on step 4's real graph in the next purpose. Same
       shared mapping (stagekit, PD390(c)) and `stage_shared.py`; the recipe pair `stage_d1_ring_p5s02d{,_scratch}.py` are
       inputs on the shared gates. Every `delete_wire` is a checkpoint (PD393(a)).
     - **(d) Gates and deliverable, as PD396(d)/(e).** The PB check runs offline on the plan BEFORE anything else (the
       retrospective-cycle163 counterfactual): dry of both recipes = PASS, or PASS-UNVERIFIED with CEN2 the ONLY unverified
       gate; prerun X10/X14/X17/X8; `--check-launch`; `--scratch-required` exit quoted. Predicted step-4-end Error List from
       the expected file 26d45c71, each cleared / raised item cited to an action, the rest named UNPREDICTED. Prior-art
       review `novel` + disposition when owed (owed for the TUNNEL deletion; corrected PD399(c): `delete_object` itself passed in P4, `diag_c140_3_facts.md:14,22`). The card's `flags.peers` include
       `priorart` whenever a pass item names it (163-a2-1 lost 6 min). Then ONE scratch on a NEW byte copy of 564d8cbe;
       peak ≤ 675 and every BLOCK gate PASS. On PASS: if step 4 ends at A80 it is the P5 FINAL file `claudeDev\D1_ring_p5_<ts>.vi`,
       broken file 6 of 6, and P6 must RUN next. Otherwise it is the in-between `claudeDev\D1_ring_p5s02d_<ts>.vi` (not counted).
       Then the full Error List item by item against the prediction, a graph read, ONE `load_by_vi` entry, and the measured
       census written into the pred. A gate FAIL ends the card at that step: the copy is kept, never loaded, and the card hands
       back. If PB blocks a row in the dry, hand back with the row. Do not add a class.
     - **(e) After the LabVIEW card, tooling: PB class 3 tightened (the pbchain review's objections; stricter only).**
       (1) Provenance: a class-3 row also needs a `RECORD PB <sink>` line in the ADOPTED step's scratch log, with the same
       S1 source set. (2) Coverage per frame instead of the multiplicity count, in classes 2 and 3: every frame in the
       allowed set carries exactly one tag for the sink, and no tag sits on any other frame. (3) `chain_tunnel_case` becomes
       newest-wins, like `chain_connects`. Self-test: the stored p5s02c and p5s02d (or p5) PB inputs still RECORD every row,
       and new negative cases cover missing provenance, a missing frame and a doubled frame. A tightened rule that blocks an
       ADOPTED row is handed back with the row; the rule is never loosened to pass it. Then drain fp-86 citing the new line
       and self-test, re-pin per (a)(3), and run one fn-descriptions batch (carry).

398. **(cycle 164 judgement, hand-back round 1, 2026-10-10 — PD397(b) corrected: the K3/K4 pass wire carries `frame` on
     its DST end only; step 4 is re-planned with that shape; card 158-a3-3 retired)**
     USER-RULES: U1 (relied on: the same two wires, same faces, same frame as PD379(b); only the plan notation of the source
     end changes), U4, U13 (unchanged); none contradicted.
     - **Hand-back accepted as fact** (`tools/bench/cards/handback_164_1.json`, results `result_164-a1-1.json`,
       `result_164-a1-2.json`, `tools/bench/diag_c164_a1_2_facts.md`): with `frame: "True"` on BOTH ends, `w_k3pass` is not a
       group wire (`tools/stagexec.py:896-897`) and not a case pass wire (`tools/stagexec.py:6286-6288` refuses a src
       `frame`), so the in-tunnel IK3 has no out-wire and compile stops (`tools/stagexec.py:901`). PD397(b) copied the shape of
       the G/H/C7 pass wires, but those are standalone frame wires placed AFTER two complete tunnel groups. In K3/K4 the pass
       wire IS the in-tunnel's one out-wire. Card 156-a1-2 designed a shape for exactly these rows
       (`tools/bench/selftest_c156_passwire.py:6-10`): `frame` = the in-tunnel's body frame, on the DST end only. The source is
       the in-tunnel's inner face in that same frame, so the wire is the same one PD379(b) describes. No computation changes.
     - **(a) Decision:** in `plan_ring_p5s02r_in.json`, A69 `w_k3pass` and A79 `w_k4pass` DROP the `frame` key on `src`
       and KEEP `"frame": "True"` on `dst`. A JSON compare against the pre-164 file d84634bd shows exactly 2 added keys (the dst
       frames). Against 4c8d3645 it shows exactly 2 removed keys (the src frames). On the base graph the dst frame binds to
       base case #31308's 'True' frame #31517. That binding is QUOTED from the step-3 binding record
       (`creation_map/plan_ring_p5s02a_4284c22a_20261010_023453.jsonl:35`), never inferred.
     - **(b) The shape is accepted offline, before any group count.** Compile of K3 and K4 must treat the pass wire as the
       group's out-wire (`case_pass_wire` True) and build each group as the register-end-case-border tunnel group, as
       `selftest_c156_passwire.py` gate A predicts. If compile refuses the dst-only shape on the real p5s02c graph, hand back
       with the refusal text. No third shape is tried inside the card, and no tool is edited to accept it.
     - **(c) Step 4 is re-planned under PD397(c), unchanged:** longest prefix of whole groups J K3 K3f K4 K4f with X10 MAIN
       ≤ 675 and rows ≤ 40. The J-alone plan `plan_ring_p5s02d.json` 1152ce60 (MAIN 628.0, 8 rows) stays on file as the
       fallback. It is used only if J+K3 is over 675 or refused.
     - **(d) Card 158-a3-3 is RETIRED.** It was never dispatched: guard_assign refused it in cycle 158
       (`assign_result_158_3.json` note), and cycles 159-163 did its attribution / step-2 work. It is closed so its pin on
       `plan_ring_p5s02r_in.json` d84634bd no longer counts as an open card. It is never re-pinned or run.
     - **(e) Unchanged:** PD397(d) gates and deliverable, PD397(e) PB tightening after the LabVIEW card, fp-86, the re-pin
       rule, the fn batch. The cycle-163 retrospective disposition is already written
       (`archive/peer/2026-10-10-retrospective-cycle163.md:518`). The `retro-undisposed` line in this cycle's `gates_due` was
       read before that write.

399. **(cycle 164 judgement, hand-back round 2, 2026-10-10 — group J takes the P4 delete form; step 4 = J + K3; K3f/K4f are
     measured before they are planned)**
     USER-RULES: U1 (relied on: the same scaffold nodes are removed and the same wires remain as in PD374/PD379(b); only the
     edit form of the removal changes, as in PD321(b)/PD323(a)), U4, U13 (unchanged); none contradicted.
     - **Hand-back accepted as fact** (`tools/bench/cards/handback_164_2.json`, `assign_result_164_2.json`,
       `tools/bench/diag_c164_a2_1_facts.md`, `tools/bench/diag_c164_a2_4_facts.md`). The dst-only pass-wire shape compiles
       (PD398(b) met). The prior-art review (`archive/peer/2026-10-10-priorart-priorart-c164-a2-3-p5s02d.md`) is RIGHT on both
       counts: J deletes #23042 / #23501 with w23460 and w23519 still attached, which is not the settled P4 form, and
       PD397(d)'s "`delete_object` has no passing launch yet" was false.
     - **(a) J's delete form = PD323(a), applied to the measured wires** (`diag_c164_a2_4_facts.md` §Wires):
       w23460 runs from #23501's inner face t23505 to #23042 only, so it has no end outside the two deleted nodes. It is
       removed by `delete_wire` BEFORE the deletes. w23519 has 4 sinks and only t23514 is on #23501, so it must NOT be
       deleted (that would cut the live sinks on #23417, #23172 and #7201). After `delete_object #23501` it gets
       `wire_remove_loose_ends`. That wire keeps 3 sinks, so PD321's whole-wire 1055 hazard cannot occur. Row order in
       `plan_ring_p5s02r_in.json` group J: A53 `delete_wire` w23489, NEW `delete_wire` w23460, A54 `delete_object` #23042,
       A55 `delete_object` #23501, NEW `wire_remove_loose_ends` w23519, then A56..A60 unchanged. JSON compare against 4d93c82d:
       exactly these 2 added actions. Gates are quoted from graph 3d5196ab before use: w23460's endpoints ⊆ #23042 ∪ #23501's
       terminals, and w23519 keeps ≥ 1 sink outside both nodes. The stagesim end graph must show w23460 gone and w23519 with
       sinks {t23450, t23241, t7606} exactly. That is the peer's discriminating test. Any other result is a hand-back.
     - **(b) Step 4 = J (10 rows) + K3 (A61..A69), MAIN ≤ 675.** PD397(c)'s prefix rule is kept, with a group allowed only
       if it routes. K3f (A70) branches onto the INNER face #8776 of LoopTunnel #5204, which no tool route reaches
       (`tools/stagexec.py:1930`, `diag_c164_a2_1_facts.md:27-34`). The prefix therefore stops before K3f. K3f, K4 and K4f become
       step 5 (P5 final, broken file 6 of 6). Step 4's file is the in-between `claudeDev\D1_ring_p5s02d_<ts>.vi`, which is not
       counted. If J+K3 is over 675, step 4 = J alone. make_step_plan does not check routability
       (`prep_plan_flow_lib.py:171`); that tool fix is carried, not done here.
     - **(c) K3f/K4f: measure, do not choose a route yet.** An offline facts card reads the design of `w_k3f`/`w_k4f` in
       `plan_ring_p5s02r_in.json` and its PD374/PD379 source, what sits on t8776/t24342 in 3d5196ab (stubs w10362/w25232),
       and whether any adopted stage ever wired an inner tunnel face (log citations or "none found"). It also checks whether an
       outer-face rewrite would carry the same value into the same frame. The route is decided from these facts in the next
       purpose. An outer-face rewrite is a rule-1a question and is not assumed equivalent.
     - **(d) The PD397(e) PB tightening, the fp-86 drain, the re-pins and the fn batch move to the NEXT cycle's purpose.** This is
       the last hand-back round of cycle 164 (3 max), and the deliverable goes first. PD397(d)'s gates are unchanged. The launch
       card names `DRY-UNVERIFIED-OK: CEN2 new-object census` when the dry is PASS-UNVERIFIED with CEN2 only
       (`stage_prerun.py:3432-3456`).

400. **(cycle 165 judgement, 2026-10-10 — step 4 adopted; K3f/K4f keep their designed wire onto the base tunnels' INNER
     faces, reached by stub delete + `connect_term_uid`; step 5 = K3f K4 K4f = the P5 final file if it fits)**
     USER-RULES: U1 (relied on: A70/A80 are wired exactly as `plan_ring_p5s02r_in.json` and PD379(b) design them, source
     OK3/OK4.outer, sink the inner faces t8776/t24342 of the kept tunnels #5204/#10404; the stubs deleted first have no source
     and carry no data, as PD388/PD391(a)), U4, U13 (unchanged); none contradicted.
     - **Accepted (`tools/bench/cards/assign_result_164_3.json`, PURPOSE_MET 17/17):** the in-between
       `claudeDev\D1_ring_p5s02d_20261010_152518.vi` 6dcd5c3d (scratch 21/0, peak 652.6 ≤ 675), graph
       `graph_ring_p5s02d_20261010_154830.json` 2a5fa0c4 (w23460 absent, w23519 sinks {t23450, t23241, t7606} == the stagesim
       prediction), Error List 53 == prediction 2c1edf78 (extra 0, missing 0), `memory_model.json` ff0fabca (`load_by_vi`
       6dcd5c3d = 603.9), pred 5a7bfc81, K3f/K4f facts `tools/bench/diag_c164_a3_2_facts.md`. The note's three assumptions
       stand: (1) END1 reads an absent wire as 0 rows, which the real graph confirms; (2) the plan input renamed
       `plan_ring_p5s02d_in2.json` for gate L0 is history; (3) E5's uid-only test failed on LabVIEW's uid re-use and the
       identity check (`prep_c164_a3_7_ident.log`) is accepted for step 4. The gate itself is fixed in (d), not here.
     - **(a) K3f/K4f route = the designed form, not the outer-face rewrite.** The facts (`diag_c164_a3_2_facts.md` §2-§4):
       t8776 and t24342 each hold a one-end sink-only stub (w10362, w25232) with no source; OK3/OK4 sit on the same diagram
       23405 as the inner faces. The outer-face form would leave #5204/#10404 unfed, needs deletes the plan does not have, and
       its equality rests on an unmeasured IndexMode, so it is a rule-1a question with no answer on file. It is NOT taken.
       Design form: plan rows `delete_wire` w10362 before A70 and `delete_wire` w25232 before A80 (each a checkpoint,
       PD393(a)); then A70/A80 unchanged. JSON compare of `plan_ring_p5s02r_in.json` against its cycle-164 bytes = exactly these
       2 added actions. Gates quoted from graph 2a5fa0c4 before the edit: each stub has exactly one terminal row, that row is
       the inner face, and it is not a source.
     - **(b) The tool gap, closed narrowly (this tool work goes before the deliverable only because compile refuses A70 at
       `stagexec.py:1930`).** A dst that is the INNER face of a While/For LoopTunnel with wire 0 (seen after the stub-delete
       checkpoint) routes by `gscript.connect_term_uid` (face uid ← source terminal uid). That is the sink-side twin of
       `loop_inner_face_route` (`stagexec.py:1673-1692`), with the same owner checks, and the op PD385(a)/PD391(a) adopted.
       Every other inner face (wired, Case / Flat Sequence tunnel, owner not one While/For loop) still stops. stagesim models
       the same. Self-test on graph 2a5fa0c4: A70/A80 compile to `connect_term_uid`; the four stop cases still stop; the stored
       p5s01a/b, p5s02a-d plans compile byte-equal. A connect from a source face that is already wired (OK3.outer feeds
       w_k3r) cites its adopted precedent (`diag_c161_p5s02b_scratch.log:97`) or the card hands back with the fact.
     - **(c) Step 5 on step 4's REAL graph 2a5fa0c4, new:OK3/OK4/CQ7/SK* bound by QUOTING step 4's binding record.** Groups
       in plan order: K3f (stub delete + A70), K4 (A71..A79), K4f (stub delete + A80). Longest prefix of whole groups with X10
       MAIN ≤ 675 from `load_by_vi` 6dcd5c3d (limit unchanged, read-only), rows ≤ 40. If it reaches A80 the adopted file is the
       P5 FINAL `claudeDev\D1_ring_p5_<ts>.vi`, broken file 6 of 6, and the next purpose is P6's run. Otherwise it is the
       in-between `D1_ring_p5s02e_<ts>.vi` (not counted). Gates and deliverable as PD397(d), predicted Error List from step 4's
       53-item expected file. Prior-art review owed (a new op on a new face class); the card's `flags.peers` include `priorart`.
     - **(d) After the LabVIEW card, tooling, in this order:** PD397(e)'s PB tightening + self-test, then drain fp-86. E5 and
       the reuse detectors judge a deleted node by identity (class, owner, owner uid, position) rather than by uid alone. This
       is the `prep_c164_a3_7_ident` check moved into the shared module, with a self-test on the step-4 data (I1/I2 pass, a
       planted survivor is caught). Then drain fp-87/fp-88. Stricter only: an adopted row that a tightened rule blocks is
       handed back with the row. Re-pin the gate-run suites once, then one fn-descriptions batch. Hook entries (fp-75, fp-80,
       fp-89, …) go to the chat.
401. **(cycle 165 judgement, hand-back round 1, 2026-10-10 — the wired-source precedent for A70/A80, and the 165-1-1 tool
     change kept)**
     USER-RULES: U1 (relied on: A70/A80 stay the designed wires of PD400(a); nothing here changes what is wired), U13
     (unchanged); none contradicted.
     - **Accepted from `tools/bench/cards/result_165-1-1.json` (items 0-4 and 6 of the cycle-165 purpose):** stub gates PASS
       on 2a5fa0c4; `stagexec.loop_inner_face_sink` (`tools/stagexec.py:6345`, md5 6ea6637f) self-test 25/0
       (`selftest_c165_innerface.log:68`), the six stored plans compile and dry byte-equal, regressions green; r_in
       9dadb0c1 -> 0b895983 = exactly the 2 added `delete_wire` rows. The change was made before the precedent check (an
       order slip, recorded in `diag_c165_a1_1_facts.md` §4); it is KEPT, not reverted: it is self-tested, changes no stored
       plan, and only the scratch run below can use it.
     - **(a) PD400(b)'s cited precedent was wrong** — `diag_c161_p5s02b_scratch.log:97` connects from an UNWIRED source
       (#3934 wire 0, `prep_c165_a1_1_prec.log:9`). **The precedent in force is `diag_c127_1_fsinner.log:81-102`:** three
       `connect_term_uid` from one already-wired source #32868 each returned the existing wire 32859 (terms 3 -> 4, census
       {}, Is Broken? False, Error List unchanged). That is the behaviour A70/A80 need from the verb: a connect from a wired
       source terminal branches onto its wire. It does NOT cover the face classes (source there a Flat Sequence inner face,
       here SelectorTunnel #31803's outer terminal; sink here an unwired LoopTunnel inner face). That residue is checked by
       the step-5 scratch run itself, not by a separate scratch-VI card: the scratch-verification rule fires only after two
       stage runs fail on one function (none has), and the scratch runs on a byte copy, so a wrong prediction costs one
       returned card and nothing is adopted.
     - **(b) What the step-5 plan predicts and the scratch shows, per stub-delete + connect pair:** after `delete_wire`
       w10362 / w25232 the face has wire 0; after A70 / A80 the census is in [{}, {'Wire': 1}] (the c127 form), t8776 /
       t24342 sit on OK3's / OK4.outer's net (w31792 or the uid the run echoes), Is Broken? False, and the Error List delta
       is the plan's predicted one. Any other result = the first unexpected result: finish the step, return, no second run.
     - **(c) Stale open card 160-c3-2** (no result file, pins `tools/stagexec.py` ddf23a31 since before 165-1-1) is closed
       by writing its `result/1` with a note naming this item, so guard_write stops reporting it; no other card is touched.
402. **(cycle 165 judgement, hand-back round 2, 2026-10-10 — the base PRIME step refuses the stub-holding inner faces; it is
     the rest of PD400(b)'s tool gap, closed in the same narrow way)**
     USER-RULES: U1 (relied on: A70/A80 and the two stub deletes are unchanged; only WHEN an end is address-proved moves),
     U13 (unchanged); none contradicted.
     - **Accepted from `tools/bench/cards/result_165-2-1.json`:** purpose items 0-3 (hashes 23/0 before and after, the c127
       precedent quoted, 160-c3-2 closed), and the step-5 group facts: K3f A72-73, K4 A74-82, K4f A83-84, MAIN per prefix
       642.6 / 657.1 / 665.0, every `delete_wire` a checkpoint (`prep_c165_a2_1_mk.log:38-47`). REALSIM replayed 13/13. The
       per-step route of w_k3f / w_k4f is `connect_term_uid` (mk.log:68,75). Only the base check refused.
     - **(a) Cause, read from the code:** the PRIME pass (`tools/stagexec.py:2620-2642`) proves at base every plan end whose
       base row has a wire, through `Addr.triple`. t8776 / t24342 still hold the stubs w10362 / w25232 at base. So `_triple`
       raises at `:1934` before the plan's own `delete_wire` rows run. In a real launch the same pass raises "PRIME ... stop
       before op 1". 165-1-1's self-test checked compile and the per-step route, not PRIME. My PD400(b) asked for no more
       than that, so the gap is mine.
     - **(b) Fix (stagexec only, narrow):** PRIME skips an end only when ALL of these hold: it is a LoopTunnel InnerTerminal
       sink; its base wire uid is the `wire_uid` of a `delete_wire` op that comes EARLIER in the plan than the action using
       the end; and that op is a checkpoint. Such an end is addressed at its own step by `loop_inner_face_sink` on the
       post-delete read. The skip is logged with the end, the wire and the deleting op. Every other end is primed as before.
       Self-test on graph 2a5fa0c4: the r_in step-5 plan finalizes in SB REALSIM with route PASS and 0 UNROUTABLE; the
       real-backend (non-collect) PRIME does not raise for these two ends. These cases still refuse:
       (n1) the same connect without the `delete_wire` row; (n2) a `delete_wire` of another wire; (n3) the `delete_wire`
       placed AFTER the connect; (n4) a wired SelectorTunnel / FS inner face. The six stored plans compile and dry
       byte-equal; the c157 / c158 / c165 innerface, stagesim and stagexec self-tests stay green.
     - **(c) Then step 5 as PD400(c)/PD401(b), unchanged.** The full prefix (K3f+K4+K4f, 13 rows, MAIN 665.0) re-makes
       `plan_ring_p5s02e.json` over the 20bde81a (final False) bytes. 165-2-1's module-level import of
       `prep_c164_a3_1_mk.py` plus the inline census extension is accepted for this maker.
     - **(d)** This is the cycle's last hand-back round (3 of 3). If the fix cannot pass its self-test, or the scratch
       returns, the cycle closes on this next.json and the same purpose carries to cycle 166.
