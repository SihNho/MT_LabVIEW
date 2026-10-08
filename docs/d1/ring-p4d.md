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

370. **(cycle 153 judgement, 2026-10-09 — after `tools/bench/cards/assign_result_152_2.json` PURPOSE_MET, facts
     `tools/bench/diag_c152_b3_1_facts.md`, retrospective `archive/peer/2026-10-09-retrospective-cycle152.md:601`)**
     USER-RULES: U1 (relied on: only facts are read and two tools are changed. No v18 action, no computation and no bed byte
     changes), U4 (relied on: the 1.2 → 1.7 results path is a DATA stream, so a lossless queue is allowed there; control
     signals stay locals), U6/U8/U9 (relied on: nothing here touches acquisition or the ring); none contradicted.
     - **(a) Accepted: P4 ENDS with `claudeDev\D1_ring_p4s09_20261009_060515.vi` eb1d0f31** (scratch 20/0, E1 6 ops real == sim
       incl. op 187 'min slot' / op 189; D/TD/PB pass; adopt 3/0), **counted broken file 5 of 6.** The same md5 appears in the
       graph read `graph_ring_p4s09_20261009_062044.json` 22f967b5 and in the Error List expected file
       `errorlist_expected_D1_ring_p4s09_20261009_060515.json` 5146f980, which has 45 items. s08 had 46. The one item dropped is
       Index Array #29879 'unwired', which op 187 closed by wiring. |Δ| = 1 and no class is unseen, so it passes on substance
       (PD354(a)); the RULE-SAME-ROW discharge was formal only. b2-1's two recipe gate changes are accepted:
       FR `(on or NC == 0)` and licence R "zero allowed". s09 creates no object, so for s09 they are equivalent to the old
       criteria. Metered start 561.9 vs pred 595.0 (−33.1; s08 +21.4) is recorded as data. Recalibration stays deferred and
       MEMSTOP stays the hard stop. "carry as the default EL pred" is NOT decided: carry gave 47 vs 46 measured on s08 and 45 vs
       45 measured on s09. P5's EL pred reports both totals and neither gates. **This judgement moves STATUS `current-bed:` to
       s09.**
     - **(b) P5 is the LAST broken file the cap allows (6 of 6), so P6 must RUN next.** P5 = loop 1.2's results reach loop 1.7
       (the file writer `#376` in `#23041`'s body, L7-1b/L7-R) through a lossless FIFO (PD238(d)). A torn or stale frame is
       not handed to 1.7 (PD293(a)), and the values that leave 1.2 are the rolled-back ones (PD298(c)). P5 is ONE counted file;
       in-between files are allowed and not counted (D-2026-10-02-02/-04). CLAUDE.md "Big or blocked work" item 4 applies: no
       P5 build until judgement has written the P5 design, its step list and its saved-file list in a new topic file
       `docs/d1/ring-p5.md`. This cycle measures the facts that design needs (f). The design is the next judgement's.
     - **(c) Device (violation-decisions 2026-10-09 07:0x):** `stagesim` collect-all replay. On an UNMEASURED refusal it puts in
       the plan's own predicted value, flags the step PROVISIONAL with the refusal text, continues, and lists every refusal. It is
       never a dry, prerun or launch PASS. Self-test on the s08 END graph, with #29721's owner unmeasured and the naming table
       without row 152-b1-2 (a temp copy): BOTH refusals must be listed (op 185 owner, op 187 naming). The existing stagesim
       self-tests stay green, and the default (non-collect-all) path keeps refusing the same way. `stagesim.py` md5 changes
       (authorised); every other stage-tool pin stays, except `vigraph.py` by (d).
     - **(d) Gate-fp: fp-70 and fp-72 are drained in this purpose, after (f) and (c).**
       - fp-70: `vigraph.computation_diff` keys rows by terminal name. Key them by position (owner, index, class), the same way
         chat-T6 keys D/TD/PB. Rename-only rows must stop reading as lost+new. Re-score the stored end reads of s06..s09 and
         S1-vs-s09: every result stays the same except rows that were rename-only.
       - fp-72: the `card_clock` CITE regex matched 'min' inside a quoted terminal name.
       fp-62..69 and fp-71 stay with the chat (hooks / hook-side scope check, user 2026-10-08).
     - **(e) Rule:** a card that changes the pass criterion of a recipe gate is HANDED BACK to judgement before the launch that
       uses it. The assignment session does not settle it (retrospective-cycle152 finding 7).
     - **(f) The P5 fact census, offline, from files on disk.** Main sources: the s09 graph 22f967b5, its Error List expected
       file 5146f980, the S1 graph/wiki and the L7-1b/L7-R logs. ONE read-only LabVIEW read of a claudeDev copy is allowed only
       for a fact that is absent on disk, and it is named in the facts file. Never the original. Each fact is quoted with
       file:line:
       - **F1.** `#376`'s input terminals in S1: for each, its source node/terminal/wire uid and the data type. For each input,
         where that source is in s09 (loop 1.1 / 1.2 / 1.7 / top level / gone) and whether the input is wired in s09. This
         covers at least w4517 'current frame data array in' from #2626, w3268 'frame index' and w1397.
       - **F2.** The s09 Error List: each of the 45 items mapped to its object, and which of them are 1.7's open rows.
       - **F3.** Loop 1.7 `#23041` in s09: its body, shift registers, stop source, wait/timing, and every node it runs per
         iteration.
       - **F4.** The ORIGINAL's call of `#376`: inside which case/structure, under which condition (save on/off, every frame or
         every N), its order relative to the tracking kernel, and what 'frame index' is (loop i, BufNum or another counter).
         This is the rule-1a reference for what one queue element must carry.
       - **F5.** Loop 1.2 in s09: the valid-frame boolean (RingSeqCheck's n1==n2 AND n1>last) and the rolled-back Select
         outputs. Their uids and terminals, i.e. where an enqueue gated on a valid frame could attach.
       - **F6.** How loops 1.2 and 1.7 stop in s09 (StopAll local, `stop (end)` latch) and their order at shutdown.
       - **F7.** Queue tooling: which ops/routes/donors created and removed the pool queues (Obtain / Enqueue / Dequeue / Release,
         element-type constant). Their hygiene records, and whether `protocol.py requires` finds each.
       - **F8.** The s09 load (596.7) and the X10 headroom for a P5 session.
       Output: `tools/bench/p5_facts.md` (≤ 100 lines) + `tools/bench/p5_facts.json`. Facts only. No design, no option table, no
       plan file.

371. **(cycle 153 judgement, hand-back round 1, 2026-10-09 — `tools/bench/cards/handback_153_1.json`,
     `assign_result_153_1.json`: 13 of 15 met; F2 per-item uids and fp-70 unmet)**
     USER-RULES: U1 (relied on: fp-70 changes how a difference is REPORTED, never which slots differ; no bed byte, no
     computation changes), U4 (relied on: the queue hygiene run is for the 1.2 → 1.7 DATA stream); none contradicted.
     - **(a) F2 accepted at CLASS level.** The 45 items map by class (1 BuildArray #2626 · 1 type · 22 not-connected = the
       22 termless wires · 21 loose ends) and none is placed in 1.7 by its class's graph location. Per-item uids are
       UNMEASURED: no `Selection List[]` reader exists, and it is NOT built now. P5's own scratch run does the full Error List
       read against the simulator's prediction, and that read is the per-item measurement. `p5_facts.md` F2 must say
       "class level; per-item uids unmeasured" in those words.
     - **(b) fp-70: the position-keyed `computation_diff` (candidate `diag_c153_b2_1_vigraph_poskey.txt` a7eb58c7) is
       ADOPTED as a recipe gate-criterion change, decided here under PD370(e).** The reporting rule: one row per changed
       input slot (owner, index, class), holding both the old and the new name/source. A slot whose source is unchanged
       produces no row, even if it was renamed. s06's #2626: slot 4 was rename-only and gives no row. Slots 1-3 had real
       source changes, the rolled-back values PD298(c) designed, and they stay flagged as 3 changed rows instead of 3
       lost+new pairs. The set of flagged (owner, slot) positions is the same, so this is equivalent for the gate's
       substance. **This is proved mechanically, not asserted.** A converter in the self-tests maps stored name-keyed
       rows to position rows: a lost+new pair at the same (owner, index, class) becomes one changed row, and a pair with
       equal sources becomes nothing. `selftest_t6_poskey` must then give 43/0 and `selftest_c147_b1_2` 19/1 (only its
       pre-existing P0 pin FAIL) against the CONVERTED stored preds. The stored pred files stay byte-unchanged. After
       that, `vigraph.py` takes the candidate's bytes (new md5 authorised), `selftest_c153_compdiff_poskey` 8/0, and
       fp-70 is drained.
     - **(c) The source of 'frame index' is MEASURED in the ORIGINAL before any doc is corrected.** F4 reads #637 i
       (S1 graph, `cycle27-plan.md:3748-3751`). `docs/NAMES.md:112` and `docs/fixture-recording.md:18` ("verified by
       probe") say #5119 x-y. The uid of `#376`.'frame index''s source wire is read in the original from an on-disk
       original read; if none exists, ONE read-only LabVIEW read of a claudeDev COPY of the original is allowed.
       Original == S1 ⇒ correct the two doc lines with a dated, cited note. Original ≠ S1 ⇒ STOP and hand back: that is
       a rule-1a question about S1 and everything built on it, and only judgement decides it.
     - **(d) Queue op hygiene now, before P5's design needs it** (CLAUDE.md "Big or blocked work" item 5). Each of the 4
       `OpQueue*_v0` ops gets 20 consecutive calls through `gscript.hygiene_run` on a fresh scratch VI under claudeDev,
       with the handle count flat (±100) and a record written to `tools/bench/op_hygiene/`. The scratch VI is deleted
       and LabVIEW is verified gone afterwards. This card never runs at the same time as the `vigraph.py`-writing card
       (wrong-ordering device, 133-4).
     - **(e) 153-b1-1's isolation question is accepted:** the before/after suite counts matched and the default
       (non-collect-all) path refuses exactly as before. stagesim stays at 78b8d5a1.
     - **(f) Not in this purpose:** `docs/d1/ring-p5.md` (the next judgement writes it from `p5_facts.md`), any P5 build,
       fp-62..69 / fp-71 (chat), and a `Selection List[]` reader.

372. **(cycle 153 judgement, hand-back round 2, 2026-10-09 — `tools/bench/cards/handback_153_2.json`,
     `assign_result_153_2.json`: trigger a, card 153-a2-6 FAILed its own gates R3/R4/R5/H)**
     USER-RULES: U1 (relied on: the F4 reference is read from the ORIGINAL's current bytes and matches S1 uid-for-uid, so
     nothing built on S1 changes); none contradicted.
     - **(a) 153-a2-6 measurement ACCEPTED: the original == S1.** `#376`.'frame index' (term 5763) ← w3268 ← term #644 on
       Diagram #639 (owner WhileLoop) = loop i (`diag_c153_a2_6_orig_read.log:11,13`). S1 has the same uids and the same 8
       sinks (`D1_s1_copy.json:35865-35870,36385-36392`). #5119 x-y feeds only #2626 'element' (`:20`). The four gate FAILs
       are defects in the script's predictions, not facts about the VI. R3/R4: `read_terms` returns the #644 row twice, and
       S1's json has the same duplicate at :36395, so the set of distinct rows has ONE source. R5: the census set was
       node-terminals only, while the observed set also has 3 tunnels. H: the handle count FELL by 6552 after the load.
       Rule 2 guards against growth, and a fall is not a leak. Jev class `our-script-bug`; no rerun is owed. Card 153-a2-7
       (NAMES.md:112, fixture-recording.md:18, p5_facts F4: a dated, cited correction) runs as written.
     - **(b) The original's md5 changed (c39f36e0 → 2f048e3a, mtime 2026-10-07 15:48, BDHb bytes differ, same size).
       There is no re-baseline and no user question.** The user owns the original's state (custody rule 2026-08-28). The
       rule-1a reference that matters here was read on the CURRENT bytes and matches. Review disposition:
       `archive/peer/2026-10-09-c153-a2-6-origmd5.md`.
     - **(c) 153-a2-5's open_rows assumption ACCEPTED.** A (node, name) open row is dropped when the conversion removed its
       pair entirely (here only (2626, 'array')). That is PD371(b)'s rename-only rule applied to the plan side: no row for
       the pred, so no open row for the plan. Card 153-a2-4 is re-issued against a2-5's wrapper `diag_c153_a2_5_run.py`.
     - **(d) The REAL scoring path must accept a stored name-keyed plan after `vigraph.py` is adopted. This is measured,
       not assumed.** a2-5 converted the plans' open_rows only in temp copies. After adoption, the PB check is run through
       its real entry point on the stored s06 plan + pred (cfbd9823 / c1bd6b3e), with no temp conversion, and the result is
       quoted. Pre-decided, judged equivalent under (c) and PD371(b): if it does not pass, `convert_open_rows` goes into that
       real path in ONE place. New md5s are authorised for `vigraph.py` and for the one file that calls the PB check.
       t6_poskey 43/0, c147_b1_2 19/1 (P0 only) and compdiff_poskey 8/0 are re-run on the final bytes. No other pinned tool
       changes; if a second tool would have to change, the card hands back.
     - **(e) Order.** a2-7 (docs, offline) → a2-2 (OpQueue*_v0 hygiene, LabVIEW, alone) → a2-4 (vigraph + (d), offline,
       never beside a2-2) → drain fp-70.
