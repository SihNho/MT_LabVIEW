---
type: decision
kind: topic
status: current
date: 2026-10-10
parent: docs/d1/INDEX.md
tags: [d1, ring-buffer, p5, step-2, pre-decided]
---

# Ring buffer P5, step 2 onward (continues `docs/d1/ring-p5.md`)

`docs/d1/ring-p5.md` holds the P5 design and PD374..PD387; it reached the 400-line cap, so later P5 decisions go here.
How to add: see the 5-line note at the top of `docs/d1/INDEX.md`.

## Pre-decided

388. **(cycle 159 judgement, hand-back 1, 2026-10-10 — the one UNATTRIBUTED item is a plan omission; 94ffff94 is the base)**
     USER-RULES: U1 (relied on: the termless segment w10394 has no terminal, so it carries no data; `#376 'saved file
     refnum'` is fed by A13's new wire 11774 — deleting the segment changes no data flow), U4, U13 (unchanged); none
     contradicted.
     - **Accepted (round 1, `tools/bench/cards/assign_result_159_1.json`):** graph read of 94ffff94
       (`graph_ring_p5s02a_20261010_032547.json`, load_by_vi 593.8, pins unchanged); the attribution
       `tools/bench/attrib_c159_p5s02a.md` (8/8 new-class items to A24..A80, net +3 explained); the PD387(e) dry repair
       (self-test 13/0, `diag_c159_a4_1_facts.md`; the stub `addrcheck.pos_table` finding means every earlier dry's D/TD/PB
       was computed on stub data); fp-77 drained; the side-item causes; 60 fn descriptions.
     - **(a) w10394 = plan omission, not a leftover for the user** (steer 5 checked first: a plan error). A13 re-made
       `#3052 'File # Saved' 3060 → #376 5772` as wire 11774 on frame 31506; the old segment stayed with no terminal
       (`attrib_c159_p5s02a.md:41-43`). Step 2's FIRST action is `delete_wire 10394` (stagekit/stagesim/stagexec
       `delete_wire`, existing verb). With it PD387(d) (`ring-p5.md:365-368`) holds: 94ffff94 IS the step-2 base; its
       expected Error List cites that action for the not-connected item; the failed copy 152721 cac5236b + its resume
       record are deleted.
     - **(b) p5s02a dry FAIL CEN2 (sim Wire 11, measured 12) = the repaired device working.** p5s02a is not relaunched,
       so its record stays FAIL as history. Measurement owed (offline): the uid and endpoints of the wire LabVIEW has and
       the sim does not, by diffing the p5s02a simulated end with the real 94ffff94 graph. Working hypothesis: it is the
       A13 remnant w10394 (a re-made pair whose old wire was split by a move leaves a termless segment, which stagesim
       does not model). Not the remnant ⇒ hand back. Step 2's sim starts from the real graph (rebase), so the remnant is in
       its base and its delete is simulated.
     - **(c) Stub-carrying connects in step 2** (A28, A35, A32, A39 onto a terminal that already carries a stub;
       `attrib_c159_p5s02a.md:54-55`): the step-2 plan and prediction assume MERGE (one ok wire per pair, the 24360/24367
       precedent) and NAME the assumption per action; the next cycle's ONE scratch measures it. No extra read now.
     - **(d) `DRY_RULE` bumped** (`stage_prerun.py:3434`) so dry records written before the PD387(e) repair no longer
       satisfy `check_launch`; self-test shows a pre-bump record refused.
     - **(e) Memory:** `START_ASSUMED` 603.4 stays (measured 593.8 is below it, the assumption is the conservative side);
       no other `memory_model.json` change.
     - **(f) Suites:** after the last `stage_prerun.py` edit of the round, re-pin the "P pins unchanged" pin of
       `selftest_c158_runcheck` / `selftest_c158_wire0face` to the new md5 (the change is PD387(e)/(d)); run
       `selftest_stagekit` and `selftest_c134_1_dry` under a card whose `labview` flag matches their header (`read`) —
       that is the equivalent form the gate accepts (fp-80 stays with the chat). Counts must equal their last passing logs.
       Tooling, after the step-2 plan items.
     - **(g) The 8 stored plans that raise ExecStop** (p3a_in, p4_v2..v6) are pre-existing: stagexec 7a712ccb unchanged
       and the plans are superseded. Recorded, no action.
     - **(h) PD387(f) (`ring-p5.md:376-381`) unchanged otherwise:** split check on the real graph, `plan_ring_p5s02b.json`
       (+ the delete of (a)) and the recipe pair on the shared RingSession gates, dry `unverified 0`, prerun PASS,
       predicted step-2-end Error List, prior-art review answered + disposition, NOT launched in cycle 159.

389. **(cycle 159 judgement, hand-back 2, 2026-10-10 — the CEN2 12th wire is a wire-UID difference, not a wiring difference)**
     USER-RULES: U1 (relied on: a wire is data flow between two terminals; the same two ends under another uid is the
     same data flow, and a source-only stub with no sink carries no data), U4, U13 (unchanged); none contradicted.
     - **Accepted (round 2, `tools/bench/cards/assign_result_159_2.json`):** PD388(a) expected Error List
       `errorlist_expected_D1_ring_p5s02a_20261010_023239.json` (56 rows, unattributed 0) and the delete of 152721 + its
       resume record; PD388(d) `DRY_RULE` 2 → 3 (stage_prerun 7605116f, self-test 12/0); PD388(b) measured
       (`tools/bench/diag_c159_cen2_wire.md`).
     - **(a) PD388(b)'s hypothesis is refuted, and the hand-back's finding is NOT a fault in 94ffff94.** Within CEN2's scope
       the real and simulated end have the SAME wire ends; they differ only in uids: LabVIEW deleted 24153 and made 31587 for
       A22's pair where the sim joined onto 24153 (+1), and 24330 sits on different pairs (swap, net 0)
       (`diag_c159_cen2_wire.md:16-24`). Outside the scope, the sim keeps a source-only stub 24091 that LabVIEW removed
       (`:25-28`) — no data (U1). 94ffff94 stays the step-2 base (PD388(a) unchanged); p5s02a is NOT relaunched, its
       adopted recipes stay history, step 2 uses the new `p5s02b` recipes.
     - **(b) CEN2 is judged by wire ENDS, not by uid counts, for the Wire class** (`stagekit.py:2414` `gate_cen2`): a new
       wire = a (source terminal key, sink terminal key, frame) pair not present at c0, keyed like TD's position key
       (base uid / created-object class); the sim side from its terminal rows, the real side from the run's terminal rows
       (`real_end_rows`, `stagekit.py:2436`). Equal end-pair sets PASS and the uid counts are printed as a `UID-REUSE` fact;
       other classes keep the uid census. Self-test on the p5s02a data: the end-pair CEN2 PASSES 94ffff94's graph vs the
       p5s02a sim end, the old uid CEN2 still reads 11/12, and a copy with one real pair removed FAILS. A source-only stub
       in the sim that the real graph lacks is RECORDED, not counted (PD386(b) precedent). Tooling — after the step-2 plan
       items; then the p5s02b dry + prerun are re-run so their records sit on the final stagekit/stage_prerun bytes.
     - **(c) No stagesim change for uid re-use or stub dropping now:** both are invisible to data flow; step 2's
       prediction names, for each MERGE action of PD388(c), the uid it expects AND that the gate judges it by ends.
     - **(d) Predicted step-2-end Error List counts the items step-2 actions RAISE, not only the base items they clear**
       (round 2's 51/45 counted removal only); each raised item named with its action, or the prediction says
       `UNPREDICTED: <action>` for it — the scratch next cycle measures those.
     - **(e) `selftest_c134_2_gates` D2** (`selftest_c134_2_gates.py:91-93`) is re-pinned to `dry_rule` 3 with the other
       suite re-pins of PD388(f).
     - **(f) gates_due:** `retro-undisposed` cycle 158 — its `## What was done with it` has text
       (`archive/peer/2026-10-10-retrospective-cycle158.md:517`); the assignment session checks it with the shared parser
       and writes the disposition only if the parser still reads it as the placeholder. `gate-fp` (14 open) and
       `violations device-failed`: no runner card this round (deliverable first; hook fps stay with the chat).

390. **(cycle 160 judgement, 2026-10-10 — cycle 159 closed at hand-back 3; steer `debate:c160-stuck` FOLLOWED)**
     USER-RULES: U1 (relied on: w10394 has no terminal, so deleting it changes no data flow; a branch that deletes ONLY
     a termless Wire cannot touch a wire that carries data), U4, U13 (unchanged); none contradicted.
     - **Accepted (cycle 159 round 3, `tools/bench/cards/assign_result_159_3.json`):** the split check
       (`tools/bench/diag_c159_c1_1_facts.md:11-16`: no group crosses A60/A61, but delete + A24..A60 = MAIN 694.4 > 675);
       CEN2 by wire ends (stagekit ac3a8f57, self-test 8/0, `diag_c159_f1_2_vipins.log`); the runcheck / wire0face /
       c134_2 re-pins; retro-undisposed 158 = parser reads real text; pins unchanged. `plan_ring_p5s02b.json` caef7e1c
       (final False) is the input for (c), not a result.
     - **(a) PD388(a)'s "existing verb" premise was wrong** (`stagesim.py:1424-1426`, `stagexec.py:2843-2851` resolve a
       delete by terminal rows). Decision: `stagesim.op_delete_wire` and stagexec's `delete_wire` compile get ONE new
       branch, taken only when the uid is in the current object list as class `Wire` with 0 terminal rows; the live delete
       is the existing `stagekit.delete_wire` uid path (`stagekit.py:687`). An "already gone" allow is never counted as a
       successful delete. `remove_bad_wires` is NOT used (it removes every broken wire, not one uid). No separate LabVIEW
       delete experiment: step 2's scratch, first action, measures the object gone and every other pair kept.
     - **(b) Branch self-test on the saved 94ffff94 graph** (`graph_ring_p5s02a_20261010_032547.json`): delete w10394
       succeeds and every other terminal row and (source, sink, frame) pair is unchanged; an absent uid, a non-Wire uid and
       a Wire with terminal rows are refused or keep the old path. Then re-run `selftest_c159_cen2_ends` and the runcheck /
       wire0face pins on the new stagesim/stagexec bytes; CEN2 is not rebuilt.
     - **(c) Step 2 = `delete_wire 10394` + A24..A40 (groups F3 G H, 18 actions, MAIN 654.6 at START_ASSUMED 603.4,
       `prep_c159_c1_1_mk_run2.log:72`).** Verified here: the probe without the delete replays clean (all 26 end rows tied,
       `diag_c159_c1_1_facts.md:27`), so the delete is the only blocked action. The step-1 symbol / frame-name mapping
       (`tools/bench/prep_c159_c1_1_lib.py`, self-test 3/0) moves into stagekit as a shared function BEFORE the plan is
       re-made with it (`docs/script-writing.md`); `--rebase`'s missing frame-name map is recorded, not built.
     - **(d) Remainder A41..A80 (40 actions: I J K3 K3f K4 K4f) is split now, offline**, by group, each step on a NEW
       LabVIEW instance from START_ASSUMED 603.4, each step MAIN ≤ 675, no group split; a facts table names each step's
       groups, actions, planned MAIN and saved in-between file name. In-between session files do not count toward the cap
       (D-2026-10-02-02, deleted once P5 is accepted); the P5 final file is the counted 6th, and P6 RUNS after it. No
       step-3+ plan is made in this cycle.
     - **(e) If GPT's alternative is needed:** if the branch cannot pass (b), the purpose hands back (trigger a). It does
       NOT silently fall back to "w10394 stays an expected not-connected item, deleted in step 3".
     - **(f) Not launched in cycle 160** (discussion order): branch + self-test → pins → mapping into stagekit → p5s02b
       plan → recipe pair dry/prerun on the final bytes → predicted step-2-end Error List (cleared AND raised items) →
       prior-art review + disposition. Cycle 161's first act is the ONE step-2 scratch on a byte copy of 94ffff94.
     - **(g) Tooling after the plan items:** `selftest_c134_1_dry` 9/2 — find the commit in 421d6108..a9d0da22 that drops
       the four `2626|Terminal|array|0-3` PB rows (name the commit and its message); re-pin its pred ONLY if that commit is
       the intended chat-T7 PB-by-position change, else record it OPEN for the next judgement; the T2a header-only pin is
       re-pinned. The three stale pins (`selftest_c156_passwire.py:161`, `selftest_c155_basecase_frame.py:206`,
       `selftest_c156_b2_2_invcheck.py:101`) are re-pinned and run. Then one fn-descriptions batch.
     - **(h) gates_due gate-fp (15 open):** every open entry (fp-62..69, 71, 74, 75, 78..81) is a `guard_*` hook gate ⇒ no
       runner card; the chat drains them (user 2026-10-08).

391. **(cycle 160 judgement, hand-back 1, 2026-10-10 — routes 4/7 of p5s02b: delete the sink-only stubs, then route the
     BASE register face like a plan-made one)**
     USER-RULES: U1 (relied on: w24264 / w24300 have a sink row and no source row, so they carry no data; deleting them and
     wiring `#376 'error out'` to the same RSR inner faces gives the data flow the plan already chose for A32/A39), U4, U13
     (unchanged); none contradicted.
     - **Accepted (round 1, `tools/bench/cards/assign_result_160_1.json`):** the termless delete branch (stagesim a3261b56,
       stagexec c4a6e0b6, self-test `selftest_c160_delwire.log` 12/0); cen2_ends 8/0, runcheck 10/0, wire0face 24/0 on
       those bytes; the mapping block in stagekit (1441bb4c, `stagekit.py:2733-2869`, `selftest_c160_stagemap` 5/0);
       passwire 20/0, basecase_frame 21/0; the c134_1_dry bisect (`tools/bench/diag_c160_f1_1_facts.md`); the split table
       (`tools/bench/diag_c160_g1_1_facts.md`: p5s02c = A41..A60, groups I J, MAIN 670.7); fn descriptions 245 → 304.
     - **(a) Routes 4/7 = option a2 + b1 of `tools/bench/diag_c160_b2_1_facts.md:28-32`.** In the plan, `delete_wire 24264`
       comes before A32's connect and `delete_wire 24300` before A39's; the sinks t24139 (RSR #24083) / t24235 (RSR #24150)
       are then unwired, which is the geometry of the plan-made-register precedent (`diag_c154_p5s01a_scratch.log:229`,
       `diag_c155_p5s01b_scratch.log:137`, LabVIEW diff 0). b2 (a new `Addr._triple` route) and c (new registers) are not
       used.
     - **(b) The delete branch of PD390(a) is widened from "0 terminal rows" to "a Wire with NO SOURCE terminal row"** (0
       rows, or sink rows only). A Wire with a source row still takes the old path or is refused, so the branch cannot
       touch a wire that carries data. The delwire self-test gains: w24264 and w24300 deleted on the 94ffff94 graph,
       t24139 / t24235 unwired afterwards, every other row and (source, sink, frame) pair unchanged; w10394 still deleted;
       the source-only stub w24285 and a wire with both ends refused or on the old path.
     - **(c) Router b1:** stagexec's compile (and stagesim's, if it shares it) treats a dict end that is the InnerTerminal
       of a BASE-graph RightShiftRegister / LeftShiftRegister like a plan-made `srR` / `srL` symbol at
       `stagexec.py:866-868`, so it compiles to `connect_term_uid` register_end_case_border. Self-test: routes 4/7 on the
       94ffff94 graph pass the route check; the stored `plan_ring_p5s01a.json` / `plan_ring_p5s01b.json` compile to the same
       op lists as before the edit; a dict end that is not a register face compiles as before. The stale
       `stagexec.py:32` docstring is corrected in the same edit. The `--rebase` frame-name gap stays recorded, not built.
     - **(d) MERGE (PD388(c)) stays only for A28 / A35** (LSR source stubs w24285 / w24312, route `cfw`). For A32 / A39 it
       is REPLACED by delete + fresh connect. The plan and prediction say this per action. The new wire uids for A32/A39 are
       not predicted (CEN2 judges by ends, PD389(b)). The dry "already wired" check (`stage_prerun.py:4109-4110`) is met
       because the delete comes first in the sim order. That check is not changed.
     - **(e) New structure class** (a base register through `connect_term_uid`, a sink-only delete) ⇒ the prior-art review
       is owed and step 2's scratch is NOT skipped (`stage_prerun --scratch-required` should exit 3; quote it).
     - **(f) Step 2 = `delete_wire 10394` + A24..A40 + the two stub deletes (20 actions)**; planned MAIN re-checked ≤ 675.
       Still not launched in cycle 160 (PD390(f)). Cycle 161's first act stays the ONE step-2 scratch on a byte copy of
       94ffff94.
     - **(g) Tooling, after the plan items:** `selftest_c134_1_dry`: the PB change is PD370(b)'s adopted position PB
       (commit 18c241ec, card 153-b2-1, `ring-p4d.md:172-183`), and PD370(b) keeps stored preds byte-unchanged with a
       converter in the self-test. So: apply that converter to this self-test's stored pred rows and open pairs (no pred or
       plan file re-pinned), re-pin T2a to 0d1f0c15, and have T2 count unverified items by PD387(e)'s rule
       (`stage_prerun.py:1074-1075`). The target is 11/0, or each remaining FAIL is named. `selftest_c156_b2_2_invcheck`:
       suite :83 reads the expected `ring-p5.md` md5 from disk at run time, which is the same check with no stale pin.
       The :91 full-md5 edit is accepted as a tool pin. The target is 20/0. Closed cards that pin old md5s are history,
       with no action.
     - **(h) Recorded OPEN for the step-3/4 plan, not now:** K3 / K4 are GAP because `w_k3pass` / `w_k4pass` cross a
       border with no tunnel or register action (`diag_c160_g1_1_facts.md:31-33`). K4's census text says "action 69"
       where A79 is meant. gate-fp: unchanged (hooks → chat).

392. **(cycle 160 judgement, hand-back 2, 2026-10-10 — the refusal was a wording false positive; the dry may end with ONE
     unverified gate, CEN2)**
     USER-RULES: U1 (relied on: no action, plan or end graph changes; the census is measured by the scratch, not guessed),
     U4, U13 (unchanged); none contradicted.
     - **Accepted (round 2, `tools/bench/cards/assign_result_160_2.json`):** PD391(b)(c) branch and router with self-tests
       (`diag_c160_a2_1_facts.md`, `diag_c160_f3_2_facts.md`); `plan_ring_p5s02b.json` f4520b10 FINAL on 94ffff94, 20
       actions, MAIN 657.4 ≤ 675 (`diag_c160_b3_1_facts.md`); pred 48b50b29, licence f61a2514, predicted step-2-end Error
       List 79ec3207 (cleared 5, raised 0, UNPREDICTED 2 = A32 w_gr / A39 w_hr, total 51; `diag_c160_c3_1_facts.md:13-21`);
       prior-art `novel` + disposition (`diag_c160_d4_1_facts.md`); c134_1_dry 11/0, invcheck 20/0; stagekit L0 predicate
       `<stem>_in<N>` (0b5bb678, `selftest_c160_l0stem` 14/0, five suites re-pinned and equal, `diag_c160_e5_1_facts.md`).
       The stricter predicate (a prefix before `<stem>_in` refused) is accepted. `plan_ring_p5s02r_all`'s G/H rows going
       UNROUTABLE is accepted: p5s02b supersedes them for step 2.
     - **(a) guard_assign's refusal of card 160-c3-2 is a false positive** (fp-83): the card only RUNS prerun's X10 check
       (MAIN ≤ 675) and changes no memory limit. The purpose now names X10 as a read-only check with the limit unchanged;
       the card's pass text is reworded so no "edit" word sits near X10.
     - **(b) The p5s02b dry is accepted at `PASS-UNVERIFIED` with EXACTLY ONE unverified gate = CEN2, reason census
       UNPREDICTED** (20/20 rows without a sample, `stagekit.py:2494-2496`). Precedent: PD261(c) / PD292(c) (the census
       prediction is not a launch precondition; the scratch MEASURES it), PD247(e) (`CENSUS-UNPREDICTED` ⇒
       `--scratch-required` exit 3). No census sample is added and no gate loosened to reach 0. Any OTHER unverified gate,
       or a FAIL, is handed back. If prerun or `--check-launch` refuses on the PASS-UNVERIFIED dry, the refusing line is
       quoted and handed back (no tool edit).
     - **(c) The step-2 scratch in cycle 161 records the measured census** of its session into the p5s02b pred (a script
       citing the scratch's graph reads, as PD292(a)), so the real launch's CEN2 gates on a measured set.
     - **(d) VI md5s:** where `md5sum` on `claudeDev` is refused by the permission layer, the hashes come from a
       `tools/bench` script (hashlib) — the check is owed, not skipped.
     - **(e) Recorded OPEN, after step 2 (script-writing rule):** the copied blocks — licence rename table
       (`prep_c156_a1_1_licence.py:49-60`), pred E1 checkpoint table (`prep_c156_a1_1_pred.py:79-82`), stub-delete
       insertion (`selftest_c160_regface.py:70-79`) — move into a shared module by one tooling card before step 3's maker.
       Cycle 161's first act is still the ONE step-2 scratch on a byte copy of 94ffff94.

393. **(cycle 161 judgement, 2026-10-10 08:4x — the step-2 dry stop is a REAL executor gap: every `delete_wire` becomes a
     required checkpoint, then the ONE step-2 scratch)**
     USER-RULES: U1 (relied on: no action, wire or end graph changes; only WHEN the executor reads changes), U4, U13
     (unchanged); none contradicted.
     - **Judged (`tools/bench/cards/assign_result_160_3.json`):** c3-3's re-pin is accepted (pred 48b50b29, licence
       f61a2514, EL 79ec3207 byte-identical; L0 PASS; four VIs hashed equal, `diag_c160_c3_3_facts.md:8-27`). The dry
       FAIL (`prep_c160_c3_3_dry.log:54`) is NOT a dry artefact. Between checkpoints the executor reuses its last real
       read (`tools/stagexec.py:2196-2198`). Ops 4 and 8 (`delete_wire dw_go` / `dw_ho`) are not checkpoints
       (`:2674-2687`), so ops 5 and 9 (`connect_term_uid`) still see w24264 / w24300 on their sinks. `connect_term_uid`
       is not in `RETRY_KINDS`, so it never gets the one fresh read. A live launch would stop at the same place
       (retrospective-cycle160 :439-442). fp-84 is therefore a real defect, not a false positive.
     - **(a) Decision: every `delete_wire` op is a REQUIRED checkpoint**, the same as add_sr / tunnel / the last op /
       a move_in run's closing op. The executor's checkpoint-set validator refuses a set without one (`ExecStop
       CHECKPOINT before op 1`). The p5s02b checkpoint set gains ops 4 and 8. Not chosen: adding `connect_term_uid` to
       `RETRY_KINDS`. A retry fixes a stale read only after it has failed; the checkpoint makes the read fresh by
       construction, and it costs 2 reads (~2 × 2.53 MB, `prep_c160_b3_1_mk.log:104-106`). Self-test: (1) a p5s02b set
       without op 4 (or op 8) is refused; (2) the stored p5s01a / p5s01b / p5s02a plans' checkpoint sets still validate
       unchanged, or each newly refused one is named; (3) the p5s02b dry with the new set gets past ops 5 and 9. No hook
       file is touched.
     - **(b) What changes in the files:** only the p5s02b checkpoint set (pred E1 checkpoint table, recipe pair, and
       whatever the licence/EL makers derive from them). Each md5 change is named with its cause. The plan's 20 actions,
       the end graph and the predicted Error List items are unchanged. If anything else moves, hand back.
     - **(c) Gates before launch, as PD392(b):** dry of both recipes = `PASS-UNVERIFIED` with CEN2 (census UNPREDICTED)
       as the ONLY unverified gate; prerun (X10 read-only MAIN ≤ 675 with the two extra reads, limit unchanged; X14,
       X17, X8); `--check-launch`; `--scratch-required` exit 3 (new structure class, PD391(e)). Any other result is
       handed back.
     - **(d) Deliverable = ONE step-2 scratch** on a NEW byte copy of 94ffff94 through `stage_d1_ring_p5s02b_scratch.py`.
       On all-gates PASS: adopt the in-between `claudeDev\D1_ring_p5s02b_<ts>.vi` (not counted toward the 6,
       D-2026-10-02-02) with a full Error List compared item by item with 79ec3207 (51 total; the 2 UNPREDICTED are A32
       w_gr / A39 w_hr), a graph read, `load_by_vi`, and the measured census recorded into the p5s02b pred (PD392(c)). A
       gate FAIL ends the card at that step: the work copy is kept and never loaded, and the card hands back.
     - **(e) Tooling, AFTER the LabVIEW card:** PD392(e)'s shared module (licence rename table, pred E1 checkpoint table,
       stub-delete insertion → one shared module, callers rewritten to call it), with ONE pin sweep over every pin of the
       tools to be edited, run BEFORE the edit (retrospective-cycle160 finding 1). Then drain fp-82 (fixed by stagekit
       0b5bb678, `selftest_c160_l0stem` 14/0) and fp-84 (real defect, fixed by (a)) with `tools/gate_fp.py drain`. fp-75,
       fp-80, fp-81 and fp-83 are hook gates and go to the chat.
     - **(f) Cycles 159 and 160 both ended at the hand-back limit, but on different mechanisms** (159: the simulator could
       not look up a wire with no terminals; 160: the executor's stale read after a delete). So the "same failure two
       cycles running" stop does not apply.
394. **(cycle 161 judgement, hand-back 1, 2026-10-10 — PB's 5 extra #376 rows are p5s02a's case move, inherited from the
     base: PB must know the moves of the steps already adopted)**
     USER-RULES: U1 (relied on: the rows are licensed only when their source terminal uids equal S1's and the frame is the
     one an adopted earlier step's plan put the node in; nothing reaching `#376` changes), U13 (unchanged); none contradicted.
     - **Judged (`tools/bench/cards/handback_161_1.json`, `assign_result_161_1.json`):** accepted: 161-a1-1/a1-2 (the
       `delete_wire` checkpoint validator, self-test `selftest_c161_delckpt` 11/0; s4 24/0 after calling
       `SX.checkpoint_ops`, invcheck 20/0, c157 13/0 after the stagesim re-pin, `diag_c161_a1_2_facts.md`); 161-b1-1's
       re-made checkpoint set (pred 48b50b29 → 18729409, cause = checkpoint set only; plan f4520b10, licence f61a2514, EL
       79ec3207 unchanged); 161-b1-2's measurement (`diag_c161_b1_2_facts.md`). The assignment session's reading that op 1
       (`delete_wire 10394`) is a checkpoint too is CORRECT — PD393(a) says every `delete_wire`; so 3 extra reads, not 2.
     - **Diagnosis (measured, `diag_c161_b1_2_facts.md` §2-§3):** PB's frame-keyed cdiff has 31 rows, the pred's non-frame
       cdiff 26; the difference is exactly 5 sinks on `#376` (cal cluster path, error in, file size, selected path, total
       data array in), present at step 0 of p5s02b (base 94ffff94) and unchanged by every action. Their sources are S1's
       terminals, now tagged `@<tunnel>/f0`: p5s02a created a CaseStructure and moved them into it (PD386(a), the c158 rows
       "moved sources sit in the planned case frame"). `case_move_frames` (`tools/stagekit.py:1942-1958`) reads only the
       CURRENT plan's `move_in` into cases the SAME plan creates, so p5s02b's `move_frames` is `{}` and PB cannot record a
       move that an earlier, adopted step made. **The defect is in PB's licence source, not in the pred or in `open_rows`:**
       those rows are not open computation differences (making them `open_rows` would mislabel them), and the pred's
       non-frame cdiff is right not to carry them.
     - **(a) Decision: PB's allowed frames = this plan's `case_move_frames` ∪ the case-move frames INHERITED from the adopted
       chain** (the plans whose artefact is in the base's ancestry: p5s01a, p5s01b, p5s02a), each earlier plan's symbolic
       frame mapped to its real frame uid through THAT step's recorded run bindings (its adopt / resume record), never by
       looking at where the node sits now. An inherited row is RECORDED only if all hold: (i) the same sink's bound row
       is present identically in the frame-keyed PB of the BASE graph (step 0) and of the end; (ii) source terminal uids
       equal S1's; (iii) every tag's frame uid is an inherited frame of the sink's or source's node. Anything else BLOCKS as
       before. One shared function in stagekit (callers call it, `docs/script-writing.md`); self-test: (1) the p5s02b sim
       end → the 5 rows RECORDED, PB ok with `pairs_extra_left` [] (the other gates unchanged); (2) a synthetic row with a
       changed source uid, or a tag naming a frame no adopted plan made, still BLOCKS; (3) the stored p5s01a / p5s01b /
       p5s02a PB results reproduce unchanged. If an earlier step's bindings are not on disk, or any of the 5 rows is not
       matched by an inherited frame, hand back — do not widen the rule further.
     - **(b) X10 is measured on the REAL checkpoint set (read-only, limit 675 unchanged):** the pred's MAIN peak is
       recomputed with the set from `SX.checkpoint_ops` (ops 1, 4, 8 included) instead of the hand-coded `BIND|{0,n}` in
       `prep_c156_a1_1_lib.py:98` (call the shared function, as 161-a1-2 did in s4). New pred md5 named. MAIN > 675 is a
       hand-back.
     - **(c) Then PD393(c)-(e) unchanged:** dry of both recipes (CEN2 the only unverified gate), prerun, `--check-launch`,
       `--scratch-required` exit 3, ONE step-2 scratch on a NEW byte copy of 94ffff94, adopt + full Error List vs 79ec3207 +
       graph read + `load_by_vi` + census into the pred; tooling after the LabVIEW card.
     - **(d) Ordering:** (a) and (b) are tooling before the deliverable only because the dry refuses the launch without
       them (deliverable-first rule's exception).

395. **(cycle 161 judgement, hand-back 2, 2026-10-10 — 3 of the 5 rows are wired BY p5s02b into the inherited case: PB gets
     a second licence class; the f1 route of two of them is PD374(d)'s designed pass-through)**
     USER-RULES: U1 (relied on: every licensed row reaches `#376` from S1's source terminals only; the timed-out frame passes
     the register values unchanged, PD374(d)), U4, U13 (unchanged); none contradicted.
     - **Judged (`tools/bench/cards/handback_161_2.json`, `result_161-a2-1.json`, `tools/bench/diag_c161_a2_1_facts.md`):**
       the measurement is accepted, including its correction of `diag_c161_b1_2_facts.md`, which PD394's diagnosis relied on
       (my error, not the card's). The binding records are on disk (`adopted_scratch.jsonl:9-11`), and the inherited frames
       are {376, 3052, 3453: [31506]}, from p5s02a only (`diag_c161_a2_1_facts.md:11-17`). `cal cluster path` and
       `file size` meet PD394(a) as written (`:21-22`). `selected path`, `error in` and `total data array in` are unwired at
       step 0 and wired by THIS plan through its own new CQ7 tunnels (actions #4 `w_in3_376`, #7 `w_g376`, #15 `w_h376`,
       `:23-28`).
     - **(a) Rule-1a answer to the card's second OPEN: yes, already decided.** `error in` / `total data array in` reach their
       S1 sources once through f0 (31506, where `#376` runs) and once through f1 (31517, the timed-out frame). That is
       PD374(d) (`ring-p5.md:48-53`): `#376`'s registers t0 → RSR #24083 and t1 → RSR #24150 pass their values through the
       timed-out frame, so what leaves 1.7 is the last real `#376` call, as in the original. Numeric acceptance stays P6
       (PD374(f)). The doubled uids are one per CQ7 frame. They are not a second data source.
     - **(b) PB licence class 2, "plan-wired into an inherited case".** It sits beside PD394(a)'s class 1 (inherited row),
       in the same shared stagekit function. A row is RECORDED only if all of these hold:
       (i) at step 0 the sink is unwired (base `after` []) and at the end it is wired by a connect action of this plan; the
       record names the action;
       (ii) the SET of source terminal uids equals S1's. The multiplicity of each uid is 1, or exactly the frame count of
       the case in (iii) when (iv) applies;
       (iii) every tag is (a tunnel this plan creates, a frame uid of a case an adopted plan created). The case's frames
       come from that step's binding record (p5s02a `STEPX 09 create c_case7`, `diag_c158_p5s02a_scratch.log:161`), never
       from where nodes sit now;
       (iv) a tag on a frame OTHER than the sink node's inherited frame is allowed only for the sinks PD374(d) names as
       pass-through registers (`#376` t0 error, t1 total data array).
       Anything else BLOCKS as before. Class 1 is unchanged.
     - **(c) Self-test (replaces PD394(a)'s):** (1) the p5s02b sim end → all 5 rows RECORDED (2 as class 1, 3 as class 2,
       action named), PB ok, `pairs_extra_left` [], the other gates unchanged. (2) Synthetic rows still BLOCK: a changed
       source uid; a tag on a frame of a case no adopted plan made; an f1 tag on a sink outside (iv); a class-2 row with no
       connect action; a uid multiplicity other than 1 or the frame count. (3) The stored p5s01a / p5s01b / p5s02a PB results
       reproduce unchanged. If a row still does not match, or a step's frames are not in its binding record, hand back.
     - **(d) Unchanged:** PD394(b) (pred MAIN on `SX.checkpoint_ops`, X10 read-only, limit 675) runs in the same round. It
       does not depend on PB. Then PD393(c)-(e) as PD394(c). Tooling still comes first only because the dry refuses the
       launch without it (PD394(d)).

396. **(cycle 163 judgement, 2026-10-10 — step 2 adopted; step 3 = p5s02c (groups I J, or I alone by memory), made on the
     REAL p5s02b graph and scratched in the same purpose)**
     USER-RULES: U1 (relied on: A41..A60 are the actions of `plan_ring_p5s02r_in.json` as designed in PD374; no action, wire or
     source changes, only which LabVIEW session carries them), U4, U13 (unchanged); none contradicted.
     - **Accepted (`tools/bench/cards/assign_result_162_1.json`, PURPOSE_MET 11/11):** the adopted in-between
       `claudeDev\D1_ring_p5s02b_20261010_105511.vi` f9ae7751 (scratch 20/0, peak 657.1 ≤ 675), graph
       `graph_ring_p5s02b_20261010_111905.json` 431cfd83, expected Error List
       `errorlist_expected_D1_ring_p5s02b_20261010_105511.json` (53 = the pred's alternative_total; the extra 2 are loose
       ends), `memory_model.json` def9e640 (`load_by_vi` f9ae7751 = 601.2 only), census in the pred (4cef0a8c), fp-82/84/85
       drained, `tools/stage_shared.py` b688edd4 (PD392(e)/PD393(e) done). The bed stays s09 until P5 ends (PD379).
     - **(a) The card's OPEN items, decided:** (1) scratch start 615.4 vs model 599.7: the PEAK matched X10 within 0.9, and
       X10 is the gate ⇒ the model stands, nothing re-fitted. (2) The 2 extra loose ends and the MERGE wires that took new
       uids: CEN2 and EL are judged by ends and by class (PD389(b)); the 53-item list is the expected file of record. (3) The
       launch log keeping the c161-named constant: history. (4) `selftest_c159_a4_1.py:300` and the 7 old check scripts that
       pin pre-rewrite md5s of the 13 historical prep scripts: KEEP the rewrite (`docs/script-writing.md`); closed cards'
       scripts that pin old md5s are history, no action (PD391(g)) — unless a suite that a gate RUNS includes one, then that
       one is re-pinned, named. (5) fp-75/80/81/83 and every other open entry are hook gates ⇒ the chat (gates_due gate-fp
       DUE, no runner card).
     - **(b) Step 3 = `plan_ring_p5s02c.json`, made on the real p5s02b graph 431cfd83** with the shared mapping function
       (stagekit, PD390(c)) and `stage_shared.py`. The recipe pair `stage_d1_ring_p5s02c{,_scratch}.py` are inputs on the
       shared gates (no copied blocks). Every `delete_wire` is a checkpoint (PD393(a)); PB knows the inherited case moves and
       the plan-wired-into-inherited-case class (PD394(a)/PD395(b)).
     - **(c) Memory rule, mechanical, no hand-back:** MAIN = X10 on `SX.checkpoint_ops` from the measured start
       (`load_by_vi` f9ae7751 601.2), limit 675 unchanged, read-only. If I + J (A41..A60) ≤ 675 ⇒ one step. Otherwise step 3 =
       group I alone (A41..A52, fresh 654.6 at 603.4 in `diag_c160_g1_1_facts.md`), and J becomes p5s02d, planned in the
       next purpose on step 3's real graph. A group is never split. If I alone > 675, hand back.
     - **(d) Gates before the scratch, as PD392(b)/PD393(c):** dry of both recipes = PASS, or PASS-UNVERIFIED with CEN2
       (census UNPREDICTED) the ONLY unverified gate; prerun X10/X14/X17/X8; `--check-launch`; `--scratch-required` exit
       quoted (group J's `delete_object` is a new op kind for P5: exit 3 and the prior-art review are expected; exit 0
       means no scratch is skipped anyway: D-2026-10-01-01 keeps a full scratch before every ring step). Predicted step-3-end
       Error List from the 53-item expected file, each cleared / raised item cited to an action, the rest UNPREDICTED and
       named. Any other result hands back.
     - **(e) Deliverable = ONE step-3 scratch on a NEW byte copy of f9ae7751.** On all-gates PASS, peak ≤ 675: adopt
       `claudeDev\D1_ring_p5s02c_<ts>.vi` (in-between, not counted), full Error List item by item against the prediction,
       graph read, ONE `load_by_vi` entry in `memory_model.json` (all other keys equal by JSON compare), measured census
       into the p5s02c pred. A gate FAIL ends the card at that step: the copy is kept, never loaded, and the card hands back.
     - **(f) After the LabVIEW card, offline, facts only:** the K3/K4 GAP (PD391(h)). For `w_k3pass` / `w_k4pass`: which
       diagram (frame) each end resolves to (-30 / -29), which tunnel or register the PD379(b) pass wire is meant to run
       between, which existing route would carry it, and whether the census text's "action 69" for K4 is a stale label for
       A79. No plan and no decision; the next judgement decides the step-4 plan. Then one fn-descriptions batch (carry).
