---
type: decision
kind: topic
status: current
date: 2026-10-09
parent: docs/d1/INDEX.md
tags: [d1, ring-buffer, p4, tracking-loop, pre-decided]
---

# Ring buffer P4 (tracking loop 1.2), part d — decisions from 368 on

Continues `docs/d1/ring-p4c.md` (392 lines when this file was opened, near the 400-line cap; PD357–PD367 there stay in
force as listed in `docs/d1/INDEX.md`). Same scope: loop 1.2's reader, and P5/P6 until they get their own file.

How to add: see the 5-line note at the top of `docs/d1/INDEX.md`.

## Pre-decided

368. **(cycle 152 judgement, 2026-10-09 — after `tools/bench/cards/assign_result_151_3.json` HANDBACK (purpose RETURN line),
     facts `tools/bench/diag_c151_a1_1_facts.md`, `prep_c151_a3_2_mk.log:35`, `stagesim.py:1802-1807`)**
     USER-RULES: U1 (relied on: only an owner FACT is read and recorded; no v18 action, source or sink changes); none
     contradicted.
     - **(a) Accepted: P4 SESSION 8 ADOPTED** `claudeDev\D1_ring_p4s08_20261009_031503.vi` f99e8414 (scratch 22/0, E1 19 ops
       real == sim incl. action 19 `p4_w_n2_arr`, D / TD / PB on T6 position keys PASS), EL 46 (expected c19cde96; pred 48 —
       the 2 extra closures are Select #4538 and IndexArray #29879, which `elrule.predict` missed because it got no `carry`;
       review `archive/peer/2026-10-09-c151-a3-1-el46.md` ANSWERED, outcome holds), graph `graph_ring_p4s08_20261009_033522.json`
       44858dbf, load 589.1 MB in `memory_model.json`. In-between file, not counted. v18 ops 1..184 built; ops 185..190 remain
       (v18 = 202 actions = 190 ops). s07 T6 re-score PASS 8/0; fp-61 drained (5/0).
     - **(b) The hand-back is a missing MEASUREMENT, not a simulator defect.** FS #29721 has one frame (#29869) and 0 border
       tunnels (its 7 rows are IndexArray #29879 / #30002 and Local #30016, wired only to each other, `facts.md:39-42`), so
       PD289(f)'s only FS → diagram link (border outer faces) does not exist, and the rule correctly marks it UNMEASURED. Same
       case as PD289(c): "the card RETURNS (a one-read reader fix is then the next card, LabVIEW)". No `stagesim` workaround
       that guesses the diagram.
     - **(c) THIRD measured owner link: FS → diagram by `OpOwnerChain_v1`** (gscript `owner_of`, strict uid echo) read on a
       FRESH load of the file the graph was read from (s08 f99e8414, read-only, nothing saved). Rule: used ONLY for an FS with
       no border outer face; where border faces exist too they must agree with the read, else UNMEASURED (unchanged); the read
       must return owner class `Diagram` with a non-zero uid and echo the FS uid, else UNMEASURED. It is recorded in a graph JSON
       key `fs_owner_read` = `{fs uid: ["Diagram", uid]}` with the read log cited; the original graph file 44858dbf is not
       rewritten (a derived file by script, or the graph reader extended — the material session chooses). `stagesim`'s
       `fs_measured_state` path (`stagesim.py:343-354`) takes it into `fs_parent`. Carried maps, the creation map and the
       simulator are still NOT owner sources (PD289(c)). Self-test: `selftest_c134_4_owners` still 7/0, plus new cases (no-border
       FS resolved by the read; read disagrees with faces → UNMEASURED; read class not `Diagram` / uid 0 / echo mismatch →
       UNMEASURED). `stagesim.py` md5 changes by this item (authorised); every other stage-tool pin stays.
     - **(d) Discriminator before s09 is made:** the measured diagram of #29721 is compared with the diagram the v18 plan's
       own create action for that Flat Sequence targeted (after rebind). Different ⇒ RETURN with both values; s09 is not made.
     - **(e) s09 = ops 185..190, the remainder, the LAST P4 session,** made on the real s08 graph plus (c), start = measured
       s08 load 589.1 (`prep_c151_a3_2_mk.log:35`: MAIN 638.4, margin 41.6 to 680; cut by PD320(e) only if X10 > 680), licence
       PD365(d), V18E-R′ (PD366(c)). Its EL pred uses `elrule.predict` WITH `carry`; first check offline that carry
       {4538, 29843, 29879, 30002, 2626} reproduces s08's 46 — quoted, not a gate (PD354(a)). Dry + prerun PASS,
       `--scratch-required` rc quoted. Then ONE s09 scratch on a NEW byte copy of s08 f99e8414 → adopt on structural PASS
       (PD354(a) routes) → full Error List expected file + graph read + `load_by_vi` entry. That file is the END OF P4 = counted
       broken file 5 of 6 (D-2026-10-02-03). STATUS `current-bed:` is moved by the next judgement, not by the card.
     - **(f) Gate-fp DUE (9 open), no runner tooling card this cycle:** fp-62..69 are hook gates ⇒ the chat drains them (user
       2026-10-08); fp-70 (`vigraph.computation_diff` name keys) belongs to chat-T6's scope (PD366(h)) and was held until P4's
       last session is adopted (PD367(f)) ⇒ once s09 is adopted it is free for the chat or the P5 cycle's tooling card.
     - **(g) Carries, not in this purpose:** the s08 recipe's `--el-advisory` and its `gate_fp.py log` were refused by the
       adopted-scratch launch gate (a hook false positive → the chat); metered start +21.4 MB over pred is the second data point
       (recalibration still deferred, MEMSTOP is the hard stop); `comtypes`/`rapidocr` live only in the Claude app's MSIX user
       site (the runner's PYTHONPATH covers it; the chat owns the install question).

369. **(cycle 152 judgement, hand-back round 1, 2026-10-09 — after `tools/bench/cards/handback_152_1.json`, facts
     `tools/bench/diag_c152_a1_1_facts.md`, `tools/bench/diag_c152_a2_2_facts.md`, refusal `stagesim.py:1892`)**
     USER-RULES: U1 (relied on: only a LabVIEW naming FACT is measured and recorded; no v18 action, source, sink or
     arithmetic changes); none contradicted.
     - **(a) Accepted: PD368(c)/(d) met.** FS #29721 → `Diagram` #23166, echo 29721 (`diag_c152_a1_1_owner.log:25,29`);
       derived graph `graph_ring_p4s08_20261009_033522_fsowner.json` e26b4d90 (44858dbf not rewritten); stagesim c24bd39a with
       `fs_owner_read` (self-test 15/0, owners 7/0); discriminator EQUAL 23166 == 23166 (`prep_c152_a2_2_probe.log:13-22`).
       The read's control FS #681 returned `TopLevelDiagram` #536 (uid agrees, class string differs): a KNOWN class-name case
       (`gscript.py:4864-4867`, review `archive/peer/2026-10-09-c152-a1-1-owner-ctl.md`), not a defect in the #29721 read,
       which returned `Diagram` exactly as PD368(c) requires. PD368(c)'s rule is unchanged: `fs_owner_read` stays restricted
       to class `Diagram`; a top-level FS is not in scope.
     - **(b) Accepted: the maker's (c4)** (provisional base = END8 + the measured owner, only `fs_unmeasured` and
       `owners['29721']` differ, `base_provisional_fsowner.json` fd84b364). It carries the same measured fact PD368(c) records,
       because the rebase's `carry_fs` carries only negative-uid owners (`stage_prerun.py:4215-4217`). REALSIM on the derived
       real graph gives the same result, and that is the run that counts.
     - **(c) The new hand-back is again a missing MEASUREMENT.** Op 187 `p4_x_slot_fs` wires LoopTunnel #30179's outer face
       'min slot' (already on net w30166, on diagram #23166) to #29879.index inside FS #29721's single frame. That FS has 0
       border tunnels, so LabVIEW creates one FS border tunnel. The name its faces take from a LoopTunnel source has never
       been recorded. `fs_tunnel_naming_table.json` has no LoopTunnel-source row, and `stagesim.py:1882-1883` lists only
       SubVI/Property/Local/Diagram (named) and Function/BuildArray (''). Refusing it is correct (card 131-1). No route-around
       that changes v18 op 187, and no guessed name.
     - **(d) Measure it with ONE scratch-VI crossing** (stagekit, ≤ 120 lines, a NEW minimal scratch VI that is never a
       claudeDev deliverable, created and deleted in the run, LabVIEW only, no instrument). The case mirrors op 187:
       - the source is an output LoopTunnel on a loop of #30179's owner class;
       - its outer face is named by the same kind of inner source as #30179's (read off the s08 graph);
       - the outer face is already wired to one other sink;
       - the sink is IndexArray.index inside a 1-frame FS with 0 border tunnels, on the same diagram as the outer face.

       Read back every face name of the created FS tunnel and of the other tunnels on that net, before and after (strict uid
       echo). An offline census of existing crossings with a LoopTunnel source in the recorded graphs may add support. It does
       not replace the scratch read: an existing tunnel's name reflects its creation history.
     - **(e) Record → simulator:** one new row in `fs_tunnel_naming_table.json` citing the scratch log line; `stagesim`'s
       naming rule extended for the LoopTunnel source class exactly as measured (named like a SubVI, or '' like a Function, or
       a scope rule if the faces differ). `stagesim.py` md5 changes by this item (authorised). Self-tests: `selftest_stagesim_tunnel_naming`
       (new row included), `selftest_c152_fsowner` 15/0, `selftest_c134_4_owners` 7/0, all PASS. Every other stage-tool pin
       stays. If the measurement shows the crossing renames the source net's existing tunnels, record that too, not just the
       new tunnel.
     - **(f) Then PD368(e) unchanged:** s09 = ops 185..190 (the run also simulates op 189 for the first time), ONE scratch on
       a NEW byte copy of s08 f99e8414, adopt = END OF P4 (counted 5 of 6).
     - **(g) Carries, not in this purpose:** a warm 20-read handle-hygiene run of `OpOwnerChain_v1` (+102 over 4 reads
       including the first op-VI load, `diag_c152_a1_1_owner.log:36`, review above; the op is not called by s09) and a
       nested-parent control read. Both are owed before `OpOwnerChain_v1` is used again in a staged build (CLAUDE.md
       reference-hygiene rule 5). fp-71/fp-72 are queued for the chat.
