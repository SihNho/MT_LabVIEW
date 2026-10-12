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

405. **(cycle 168 judgement, 2026-10-12 — after `tools/bench/cards/assign_result_167_1.json` (cards 167-a1-1..5), discussion
     c168-outcome (`tools/bench/debate/c168-outcome/summary.json`, steer_168 FOLLOWED) and retrospective-cycle167)**
     USER-RULES: U1 (relied on: the 168 card saves nothing that is adopted; the one deletion is measured on a scratch copy
     and judged here before any P6-1 launch), U12 (relied on: #11261 and the other DISP rows feed display only; their feed is
     rebuilt by the display loop fed by locals after P6, so P6-1 leaves them unfed), U4 (relied on: no control or data route
     changes), U6/U8/U9/U13 (the ring and overload path are not touched); none contradicted.
     - **(a) Accepted from 167 (items 0-10):** RBW measured on a scratch copy of 75773b0d: ExecState 0 → 0, wires 2091 → 2066
       (25 deleted = 22 termless + 2 source-only + 1 data-carrying, w25618 #11261 'appended array' → t8323 'Force (pN) vs
       Extension (nm)'), Error List 47 → 1 item "Build Array: Contains unwired or bad terminal", uid unread
       (`tools/bench/diag_c167_a1_1_facts.md:14-25`); after-RBW graph `graph_ring_p6rbw_20261012_191349.json` c5531708;
       closure table `p6_closure` (R 27, D 19, DISP 5, C 2, U 22); C-row facts `p6_crows`; replay readiness `p6_replay_ready`;
       the tooling notes. The 167-a1-1 conversion of launch gates A0/R1 into rows was NOT the card's to make (retrospective
       fault 2); its measurements stand because A0 read 0 and the wire count dropped by 25 as stated.
     - **(b) 'RBW 후 소멸' (vanished after RBW):** the 22 U rows (looseends EL[0,1,4,6,14,21,25,31..42,45,46] and twotypes
       EL[3]) are items RBW removed while deleting no data-carrying wire other than w25618 (`p6_rbw_deleted.json` 0a6c1206:
       data-carrying 1). They are re-classed D-by-measurement and need no P6-1 row. **U = 0 (PD404(b)) applies to the P6
       candidate's REMAINING Error List items and computation-diff rows only**, not to historical items RBW removed.
     - **(c) Which Build Array is left is UNMEASURED.** F1 attributes the item to #2626, but in 7815af09 every #2626 input is
       wired while #11261 'array' / 'element' have no source (`prep_c167_a1_3_explore.log:44-47,60-61`). #11261 feeds the
       Force-vs-Extension display only (`docs/d1/ring-p4.md:52`, PD295(b)). The 168 measurement: offline on c5531708, every
       BuildArray node's input wiring + #11261's output path (compute / save / control or display only); then ONE LabVIEW card
       on a fresh scratch byte copy of 75773b0d: RBW (the 167 verb) → delete #11261 (existing `delete_object` route) →
       ExecState → full Error List → graph read (`stagekit.e5_check`). Nothing adopted. ExecState 1 = STRUCTURAL only; the
       card then reports each PD404(b) save gate as a fact. ExecState 0 = the remaining Error List and graph are returned
       and no further repair is guessed inside the card.
     - **(d) P6-1 repair rows (provisional, final after (c)):** R1 = RBW (method 410, as 167); R2 = delete #11261. DISP rows
       (5: t11270, t11273, t8323, t17272, t28786) stay UNFED in P6-1 — no local now (U12, PD295(b)); the display loop feeds
       them after P6. PD404(b)'s computation-diff gate uses the FRAME-KEYED mode, with the five #376 tag-only rows (cal
       cluster path, error in, file size, selected path, total data array in) counted R by PD374(d) (they are the PB rows the
       P5 scratch recorded, `diag_c167_a1_3_facts.md:12-14`).
     - **(e) C rows t10083 (#10068 'x') and t29256 (#29240 'x'), fed by #30240 'element' (FrameIdx) instead of S1's `#644` i:**
       P6-1 keeps FrameIdx (the PD374(b) record counter); it is not rewired. Basis: in four stored A legs of the original the
       frame step was never ≤ 0 (`p6_crows.md`, "Repeated BufNum": steps_le0 0), so the original never re-processes a frame.
       FrameIdx counts processed frames from 0 while `#644` i counts 1.1 iterations from 0; they are equal only while 1.2 drops
       no frame. Their equivalence on numbers out is judged by the P6-2 numeric replay only (rule 1a), not by this argument.
     - **(f) 167's open notes:** (1) **correction:** card 110-6 ran nothing; the replay legs ran under 110-7 and DID drive the
       PI stage and the ASI through the replay copy's device init, under `motor_gate --session` (`diag_c167_a1_4_facts.md:12-14`);
       every P6-2 card states `hardware: motor_gate session` (rig 조립 only), never `none`. cal files: until the user answers
       D-2026-10-12-01/02 the criterion in force stays PD374(f) (saved files bit-identical). (2) STATUS relocation, (3) el_class
       vs `errorlist_check.class_counts`, (4) inline copies, U-row uid recovery, shared-function moves and re-pins are DEFERRED
       until after P6-1 and P6-2 (steer_168 item 6). (6) fp-98 (stage_prerun X5) and fp-99 (protocol.py:572) are non-hook
       entries; they are drained in the first tooling card after P6-2. The op label `rbw_method410` is accepted as the RBW
       op's name.
     - **(g) Launch gates a dry run can only stub** (ExecState before/after, wire-count drop, #11261 absent) are NAMED in the
       card as expected-unverified (the existing release); a material session never turns a gate into a row (rule 7).
     - **(h) Next:** cycle 169's judgement writes PD406 = the final P6-1 plan from (c)'s facts.

406. **(cycle 169 judgement, 2026-10-12 — after `tools/bench/cards/assign_result_168_1.json` (cards 168-a1-1, 168-a1-2):
     the final P6-1 plan)**
     USER-RULES: U1 (relied on: the two rows are the ones measured on a scratch byte copy of 75773b0d; the saved file is
     new, the bed and every original stay byte-unchanged), U12 (relied on: #11261 and the DISP rows feed display only and
     stay unfed until the display loop, PD405(d)), U4/U6/U8/U9/U13 (no control route, ring or overload path changes); none
     contradicted.
     - **(a) Accepted from 168 (items 0-9):** offline, of 19 BuildArray nodes only #11261 has unwired inputs and its output
       reaches only display t8323 (`tools/bench/p6_buildarray.md`). Scratch of 75773b0d: RBW (wires 2091 → 2066) then
       `Stage.delete_object("BuildArray", 11261)` → ExecState 0, 0, **1**; Error List **0 items**
       (`errorlist_D1_ring_p6rbwd_20261012_205248.json` f71773bc); graph `graph_ring_p6rbwd_20261012_205248.json` 57f33e7c
       with `e5_check` ok; save gates F-S1..F-S4 PASS; peak 611.7 MB; scratch deleted, LabVIEW gone
       (`tools/bench/diag_c168_a1_2_facts.md:11-41`). ExecState 1 is STRUCTURAL only; numbers are P6-2's.
     - **(b) F-S5 is a criterion error, not a build fault (mine: PD404(b) predates PD405(e)).** The measured frame-keyed
       cdiff has 30 rows = 27 closure R/DISP rows + t8323 (DISP, PD405(d); unfed now that its only source #11261 is gone)
       + t10083 (#10068 'x') and t29256 (#29240 'x'), the two C rows PD405(e) keeps on FrameIdx. The two "closure only" rows
       are #11261's own inputs, which no longer exist (`diag_c168_a1_2_rbwdel.log:379`). **PD404(b)'s cdiff gate is replaced:**
       the P6-1 graph's frame-keyed `computation_diff(S1, P6)` row set == the same diff on the 168 scratch graph 57f33e7c,
       row for row (30 rows; = closure R ∪ DISP ∪ C − the deleted node's inputs). Any other difference stops the save.
     - **(c) P6-1 = ONE launch, no further scratch.** 168 ran exactly P6-1's two rows on a byte copy of 75773b0d with the
       same verbs; it is accepted as P6-1's full scratch (PD404(a)). Rows: R1 = RBW (op `rbw_method410`), R2 = delete_object
       BuildArray #11261. Nothing else. If `stage_prerun --scratch-required` exits 3 or `check_launch` asks for a scratch,
       ONE scratch on a fresh byte copy precedes the launch (that is the tool's rule, not a new decision).
     - **(d) Form:** a recipe on the shared stagekit/stagexec gates with the 168 card's inputs (plan rows + uids 11261 / 2626),
       calling the shared functions (`gscript`, `Stage.delete_object`, `gscript.exec_state`, `stagekit.e5_check`, the EL read,
       `prep_c168_a1_2_lib` for mem / frame cdiff); no new inline copies. Its dry passes `--graph
       graph_ring_p5s02e_20261012_173009.json` explicitly (fp-100's form, accepted; no gate became a row); stub-only gates
       named expected-unverified (PD405(g)). Memory: prerun X10 PASS on the model as is (168 predicted 678.9 < fail_above 680,
       measured 611.7) and every measured MEM line ≤ 675; no limit changed. If build + save + post-save reads do not fit one
       session, the post-save reads run in a second session on the saved bytes.
     - **(e) Save and adopt:** the work copy is a byte copy of 75773b0d named `claudeDev\D1_ring_p6_<ts>.vi`; it is saved ONLY
       when, before save, ExecState 1, 0 Error List error items, F-S3 (#2626 inputs), F-S4 (#5204/#10404 IndexMode + outer
       type vs 7f2582ae) and (b) all PASS; otherwise it is deleted and the card returns its Error List. After save, from the
       SAVED bytes: md5; ExecState 1 on reload; full Error List read (`--role final`, 0 error items, file kept as the
       expected Error List); graph read + `e5_check` + (b) re-checked; one `load_by_vi` entry in `tools/bench/memory_model.json`.
       Then the bed moves: STATUS `current-bed:` and INDEX "Current state" → `D1_ring_p6_<ts>.vi` (RUNNABLE, not a counted
       broken file; the count stays 6 of 6).
     - **(f) Tooling after the deliverable (gate-fp DUE):** one card drains the non-hook entries fp-98 (stage_prerun X5) and
       fp-100 (stage_prerun dry graph pick: an RBW'd graph labelled with its pre-RBW md5 was taken for 75773b0d), each with a
       self-test; fp-99 only if its fix lies outside `tools/hooks/**`, else it stays for the chat with the other hook entries.
       The remaining PD405(f) tidy-ups stay deferred until after P6-2.
     - **(g) Next:** P6-2 (recorded-frame replay) is blocked by D-2026-10-12-01/02 (replay pass criterion) for its criterion
       only; cycle 170's judgement plans what of P6-2 can be built before the answer (PD405(f)(1): hardware = motor_gate session).

407. **(cycle 169 judgement, hand-back round 1, 2026-10-12 — after `tools/bench/cards/handback_169_1.json` (cards 169-a1-1
     BLOCKED, 169-a1-2 FAIL))**
     USER-RULES: none apply beyond PD406's (no design change; this item judges a returned self-check only).
     - **(a) Accepted (purpose items 0-5, 8):** the prior-art review is `novel` (`archive/peer/2026-10-12-priorart-priorart-c169-p6.md:353`).
       The ONE launch on a byte copy of 75773b0d gave ExecState 0, 0, **1**, MEM peak 610.9, Error List 0 items, and S-1..S-5 PASS,
       with S-5 at 30 vs 30 rows and both differences empty (`tools/bench/launch_c169_p6.log:27-42,360-386`). It was **SAVED** as
       `claudeDev\D1_ring_p6_20261012_212645.vi`, md5 **c2d9c13cb40c0a5cab7433896d1df157**, and 75773b0d is unchanged
       (`:376-393`). The post-save read on a byte copy gave ExecState 1, `e5_check` ok with deleted_nodes [11261], graph
       `graph_ring_p6_20261012_212645.json` fbc7b7ee, S-5 30 vs 30, and MEM after load 600.4 (`diag_c169_a1_2_post.log:27-321`).
     - **(b) The one FAIL is a script bug, not a machine fact.** The post script's own DN gate took every non-Wire object of
       7815af09 absent from 57f33e7c and got [11261, 11267, 11270, 11273]. 11267/11270/11273 are `Terminal` objects owned by
       BuildArray #11261 (`graph_ring_p5s02e_20261012_173009.json`), so they go away with the node. The correct DN set is the
       absent non-Wire objects **whose owner is not itself absent** (equivalently, absent objects of class not in {Wire,
       Terminal}); the expected result is [11261]. Patch in place (`tools/bench/diag_c169_a1_2_post.py:66-71`) and re-run the
       post-save reads; `e5_check` already used [11261] and passed, so no other gate changes.
     - **(c) `--scratch-required` exit 3 after the scratch is by design** (`stage_prerun.py:4872`, it counts OTHER clean stages).
       The scratch ran and passed, so PD406(c) was met; the brief's "exit 0 after" prediction was wrong, and that is not a fault
       of the build.
     - **(d) The docs/script-writing.md drift (0165fb24 → 3583b9f3, chat commit 02bdfa47) is accepted.** Rules 10-15 bind new or
       changed code only, so they apply to the DN patch and to no file already run.
     - **(e) Still owed from PD406(e)/(f):** the post-save run with the patched DN gate; `errorlist_check --role final` on the saved
       bytes, kept as `errorlist_expected_D1_ring_p6_20261012_212645.json`; ONE `load_by_vi` entry keyed c2d9c13c; then the bed
       move (STATUS `current-bed:` + INDEX "Current state" → `D1_ring_p6_20261012_212645.vi`, RUNNABLE, count stays 6 of 6);
       then the fp-98/fp-100 drain. A post-save FAIL on anything other than the DN gate hands back; the saved file is never
       re-saved or rebuilt in this cycle.
     - **(f) P6-2 is no longer blocked.** The user answered D-2026-10-12-01/02 on 2026-10-12 21:16 ("동의함";
       `tools/bench/decisions_pending.json:387,405`). The replay criterion is now the answered one, which amends PD374(f) and
       replaces PD405(f)(1)'s fallback. Cycle 170's judgement plans P6-2 on that criterion.
408. **(cycle 169 judgement, hand-back round 2, 2026-10-12 — after `tools/bench/cards/handback_169_2.json` (cards 169-a1-3
     FAIL, 169-a2-1 PASS, 169-a2-2 FAIL, 169-a2-3 PASS))**
     USER-RULES: none apply (judges returned facts and one gate-fp entry; no design change).
     - **(a) P6-1 is DONE and ADOPTED (purpose items 0-6 accepted).** Post-save run with the patched DN gate on a byte copy: ExecState 1,
       DN [11261], E5 ok, S-5 30 vs 30 empty, MEM peak 615.1 <= 675, c2d9c13c unchanged (`tools/bench/diag_c169_a1_3_facts.md:21-26`);
       Error List --role final 0 items, kept as `errorlist_expected_D1_ring_p6_20261012_212645.json` (`:27-30`); `load_by_vi` c2d9c13c
       = 603.7 (`:31`); bed = `D1_ring_p6_20261012_212645.vi` (STATUS `current-bed:`, INDEX). 169-a1-3's FAIL is the pin of the very
       log the card was ordered to re-run into (`diag_c169_a1_2_post.log`, old bytes kept as `_run1.log`, 7 VI pins equal) - a pin
       artefact, not a build fact; its Jev "review owed" row (jev_gate.log:7509) is answered here: no review.
     - **(b) fp-98 CLOSED as by design**, not drained: X5 must FAIL an unplanned remove_bad_wires (card 115-3, T8,
       `tools/bench/selftest_stage_prerun_c115c.py:52`); a planned RBW passes through its plan label (`rbw_method410`, 167 script
       PRERUN PASS, `tools/bench/selftest_c169_fp98_100.py:66` A1-A4). PD405(f)(6)'s label acceptance stands. fp-99, fp-100 drained.
     - **(c) Left open, after P6-2, never before it:** fp-102 (stage_prerun X10_RO_EDIT_RE matches 'delete' in any call name,
       `tools/stage_prerun.py:2192`; non-hook, a runner tooling card may fix it); selftest c106c C2/C3/C6 EXECUTOR-STOP UNROUTABLE
       (6/0 at cycle 152, broken before 2026-10-12 22:10; facts `tools/bench/diag_c169_a2_3_facts.md:18-22`); fp-101 and the hook
       entries go to the chat.
     - **(d) Next = cycle 170: P6-2** (recorded-frame replay, PD404 row P6-2) on the criterion answered in D-2026-10-12-01/02,
       base = the adopted P6 file c2d9c13c; hardware per PD405(f)(1) = motor_gate session (rig 조립 only).
