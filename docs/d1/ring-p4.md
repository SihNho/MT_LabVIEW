---
type: decision
kind: topic
status: current
date: 2026-10-02
parent: docs/d1/INDEX.md
tags: [d1, ring-buffer, p4, tracking-loop, pre-decided]
---

# Ring buffer P4 (tracking loop 1.2) — decisions from 268 on

Scope: loop 1.2's reader (`last` register, smallest `Num > last`, seqlock n1 == n2 >= 0, jump to `Latest` on an
overwrite, 1 ms own wait; PD238(e) `docs/d1-loop12-17-split-plan.md:2258`), and P5/P6 until they get their own
file. Carries from the frozen plan: size P4 with the memory formula of PD266(b) before planning (:2946); re-check
PD237(g) (`#10068`/`#29240` into 1.2, :2229) when P4 is planned.

How to add: see the 5-line note at the top of `docs/d1/INDEX.md`.

## Pre-decided

293. **(cycle 135 judgement, 2026-10-02 — after prep card 135-P1 PASS 6/0, `tools/bench/cards/result_135-P1.json`)**
     USER-RULES: U1, U9, U11, U13 (relied on: the seqlock, discard-as-gap and jump rules of `docs/ring-buffer-design.md:25-31`;
     none contradicted).
     - **(a) Sizing accepted as a measurement, not a plan:** draft `tools/bench/plan_ring_p4_draft.json` d9d66246 (never launched,
       not simulated) = 93 actions (reader R 68 + slot-value consumers C 25), X10 824.2 MB from the measured P3b-2 start 578.0;
       largest 675-MB session = 21 ops. P4 fits neither the ≤ ~40-action step (D-2026-10-01-01) nor one LabVIEW session, and after
       P3b-2 only 2 of 6 broken files remain (P4, P5). That is the user's call → **D-2026-10-02-03**. Until answered, P4 is
       planned as build steps of ≤ 40 actions, each in as many memory sessions as X10 needs; only the file COUNT is open.
     - **(b) A torn or stale frame's result has NO effect** (`ring-buffer-design.md:27-28`: "otherwise it is DISCARDED"): every
       loop-1.2 shift register written by the tracking body takes `valid ? new : old` (Select per register) and the result is
       handed to 1.7 only when valid. No private image copy is added (the design tracks `Img(i)` in place). Valid frames run the
       original nodes unchanged (U1); a discarded frame is a gap (U9, U13).
     - **(c) valid = `n1 == n2 AND n1 > last`.** `last` ≥ −1 always, so `n1 > last` implies `n1 ≥ 0`; the separate `n1 > -1` test
       (7 ops) is dropped as equivalent. On overwrite (smallest `Num > last` missing because the slot was reused) `last := Latest − 1`.
     - **(d) Reader shape = the draft's inner wait-for-new While W1, plus a stop exit:** W1 also stops on the program's stop
       (local read of the same control the other loops stop on), so a stopped camera cannot hang loop 1.2; a W1 exit without a
       new frame gives `n1 ≤ last` ⇒ invalid ⇒ rolled back by (b). Rejected: a case around the original 1.2 nodes (moves the whole
       tracking body — far more actions and memory than W1).
     - **(e) n2 is ordered after the tracking by DATA dependency on a MEASURED route** (an error or image-out wire of the last
       tracking node into the second `Num` read's path); the draft's UNMEASURED "FS input tunnel with no inner sink" is not used.
     - **(f) Facts owed before the P4 plan is finalized (cycle 136, offline):** (1) what `#2626` element|0 (← `#5119`
       BufNum − LastBufferNumber) and `#11363` (← `#11608`) feed in the ORIGINAL — saved data, display, or nothing — because a
       per-frame value computed in 1.1 that reaches saved data needs its own per-slot array (rule 1a); (2) loop 1.2's stop
       `#10171 Equal?` with x and y on the same wire (TRUE always, one iteration): which stage created it and what the original's
       tracking-loop stop is; (3) the 6 UNMEASURED routes left after (c)–(e), each with the cheapest measurement.
295. **(cycle 135 judgement, 2026-10-02 — after prep card 135-P2 PASS 4/0, `tools/bench/prep_c135_p2_facts.md`)**
     USER-RULES: U1, U9, U13 (relied on: each result carries its own frame's values, PD233(f)(1)(2); none contradicted).
     - **(a) `#5119 x-y` (BufNum − LastBufferNumber) is SAVED** (→ `#2626` element → `#376` save trace, `diag_c126_8_orig.log:5-6,32`), so
       it is a per-frame value of loop 1.1 that must travel with its frame: a FIFTH per-slot array, front-panel indicator labelled
       `BufDiff`, type = `#5119`'s output type read from the graph, created and initialised like PD240 (FS1 `#4866`), written in
       1.1's per-slot group, read in 1.2 into `#2626` element|0 (t2832). Its actions belong to P4 and count in P4's size.
     - **(b) `#11608` and `#1359` feed the Force-vs-Extension DISPLAY only** (`main_vi_nodeterms.json:12370,12685,12759`) ⇒ no per-slot
       array; they go to the display track (PD210, display loop fed by locals) after P6.
     - **(c) Loop 1.2's stop:** `#10171` (x == x, always TRUE) is the S2 scaffold that made the empty While legal
       (`stage_d1_s2_loops.log:61-69`). P4 replaces it with the program stop that W1 uses (PD293(d)); read `#10170`'s
       conditional-terminal mode first. The original stop logic is `#648 ← #11639` (`main-vi-stop-and-save.md:41-49`).
     - **(d) PD293(e) AMENDED:** `#5058` has no error out and no Image Out (`d1-loop12-17-split-plan.md:2235`), so n2's `Num` read
       sits in a one-frame Flat Sequence whose input tunnel takes a `#5058` output (the draft's route). That route is measured in
       the scratch verification of (e) before the P4 plan is finalized.
     - **(e) Before the P4 plans (next LabVIEW card, scratch only):** ONE scratch VI for Select on a Boolean array / I32 MAX
       constant / Array Max & Min / Boolean-array selector, and ONE scratch byte copy for While outer face → FS frame and FS-frame
       exit (precedent `#28302`, `diag_c126_6_cross.log:77-78`); the `Or` donor for W1's stop is found or made there.
298. **(cycle 136 judgement, 2026-10-02 — after 136-1 BLOCKED 16/1 (fp-33), prep 136-P1 FAIL 5/1, `tools/bench/prep_c136_p1_p4v2.md`)**
     USER-RULES: U1, U4, U9, U12, U13 (relied on: no-effect discard of a torn frame, control signals by local, display in its own
     loop; none contradicted).
     - **(a) Accepted as measurement:** P4 v2 `plan_ring_p4_v2.json` 0d67d704 = 159 actions / 154 ops (43 for the six rollback Selects,
       PD293(b), because no single-sink disconnect op exists); replay ok to action 63, cdiff 16; 5 build steps 33/39/39/36/12. The
       bed's MEASURED load is 600.2 MB (`diag_c136_1_graph.log:24`), not the 578.0 the step table used ⇒ the session table is
       recomputed from 600.2 and from a load-growth figure fitted to MEASURED loads, never assumed (prep's 0.719 MB/op is a model).
     - **(b) Pool crossing `p4_x_pool` (#23099 → IAI1.array in #10170's body):** the plan gets an explicit loop-input tunnel action on
       `#10170` first, as stagesim requires; the simulator is not extended for this. The tunnel route goes on the scratch list when no
       census record for "base While, input tunnel from the parent diagram" exists.
     - **(c) n2 ordering (PD295(d)):** the one-frame FS's input tunnel takes a `#5058` output and feeds ONE no-effect consumer inside
       the frame (an existing measured primitive, output left unwired) — the tunnel exists because a sink exists, which every route
       already supports; the frame still starts only after `#5058` finishes. No `border_only` address, no new route. Values unchanged (U1).
     - **(d) Values leaving loop 1.2 follow the rollback:** a value that reaches ANOTHER loop (the `autofocus reseed flag` t25557 and
       `autofocus reset count` t25573 locals read by 1.1/1.5) or saved data takes the Select output (rolled-back value), never the raw
       one — a torn frame has no effect outside 1.2 either (U9). Display-only sinks (`Pos within cal image` t3173,
       `Pos: Diffraction Pattern` t9519) stay on the raw value and move to the display loop later (U12, PD295(b)).
     - **(e) Loop stop for W1 and 1.2:** read `stop (end)`'s mechanical action first (136-3). Not a latch ⇒ W1 and 1.2 read it by local.
       A latch (no local possible) ⇒ ONE writer: the loop owning `stop (end)` (`#639`) writes a new non-latch Boolean indicator
       `StopAll` every iteration; W1 and 1.2 read it by local (U4). The other loops' scaffold stops (`#23042`, `#23035`) are NOT
       changed in P4 — they belong to the interface-contract step after P6.
     - **(f) The 700 MB stop is a measurement to re-take, not a law:** it sits 70 MB under ONE error-2 observation at ~770 MB, which
       `.claude/skills/labview-automation/references/com-driving.md:308-312` ascribes to leaked references ("low for a 64-bit
       process"). After P4 (+154 ops) the bed's own load approaches the stop, so before P4 is cut into more sessions, a scratch
       run (bed byte copy, no save, warn-only meter, repeated whole-VI reads) measures where error 2 really appears with today's
       reference-closing tools. The X10 thresholds change only by a later judgement item citing that run.
     - **(h) see PD299 for the X10 edit-model follow-up.**
     - **(g) File count:** P4 at 159 actions supersedes the 93 in D-2026-10-02-03's question; new item D-2026-10-02-04 carries the
       measured numbers. Until answered, P4 is prepared as dependency-closed ≤ 40-action steps (valid under every option).
299. **(cycle 136 judgement, 2026-10-02 — after 136-2 FAIL 3/2, `tools/bench/cards/result_136-2.json`)**
     USER-RULES: none apply (tooling; no design of the VI).
     - **(a) Accepted:** X10's edit-diagnostic branch (`stage_prerun.py:2083`, self-test `selftest_x10_c136_2` 6/0, fp-33 drained).
       The bed's MEASURED load 600.2 MB (`diag_c136_1_graph.log:24`) is entered as `load_by_vi[395118775a…]` in `memory_model.json`.
     - **(b) Reads are counted from the SOURCE, not from what the dry happens to execute:** the dry skips DRY-guarded
       `census_snapshot`/`read_terms` reads (`stagekit.py:265`), so a dry-counted R undercounts (3 vs ~50 call sites). Until the
       gate counts call sites itself (tooling carry), a card lists every whole-VI read call site of its script and X10 is judged on
       that count; scripts keep reads to the PD193(a) set (start + end of each part).
     - **(c)** `selftest_x10_c132_1` T3 fails on a deleted fixture VI (`scratch_c133_6…`, MISSING) — stale fixture, tooling carry.
     - **(d)** `While Loop.Stop If True?` (6362C01, R/W) is a community-sourced fact (labviewwiki only); it is read on the machine
       in 136-3 before any plan relies on it.
300. **(cycle 136 judgement, 2026-10-02 — after prep 136-P2 FAIL 5/1, `tools/bench/prep_c136_p2_p4v3.md`)**
     USER-RULES: U1, U9, U10 (relied on: a discarded frame has no effect; the sequential fallback exists; none contradicted).
     - **(a) Accepted as measurement:** v3 `plan_ring_p4_v3.json` d14c1bba = 163 actions / 164 ops; replay on the REAL bed graph ok to
       step 101 (cdiff 16 → 20 from the `#10068`/`#29240` move-in at 98-99), step 102 `p4_x_fd` stops on "#686 owns no terminal"
       while the real graph lists t8936 on 686 — a simulator/plan addressing question, diagnosed only if P4 keeps its shape (c).
     - **(b) `autofocus reseed flag` t25557** (from `#9647` AND, not a register): Select(valid, new, Local read of the same flag) —
       an invalid frame leaves the published value exactly as the last valid frame wrote it ("the frame did not happen"). n2's
       source `#5058` t5111 accepted (ordering only).
     - **(c) MEMORY IS THE BINDING CONSTRAINT, not the edit count:** measured load growth 0.543 MB/op (6 loads, SD 10.6) ⇒ an EMPTY
       session passes 675 after ~86 more ops; P4 = 164 ops; P5 and the display/motor tracks add more. No session-cutting makes P4
       fit under today's stop. So the NEXT LabVIEW act is PD298(f)'s error-2 re-measure (card 136-4). Then:
       error 2 not reached well above 770 with today's tools ⇒ a judgement item re-bases X10's thresholds on that run; error 2 at
       ~770 again ⇒ P4 is re-planned (judgement; candidates include building new parts in subVIs so the top VI's load does not grow
       with them, and the user's sequential fallback U10) and the user is told before more P4 build cards are written.
301. **(cycle 136 judgement, 2026-10-02 — after 136-4 PASS 13/0, `tools/bench/diag_c136_4_mem.log`; 136-3 FAIL 3/2)**
     USER-RULES: none apply (memory measurement and tooling; no VI design).
     - **(a) PD300(c)'s premise is REFUTED by measurement:** LabVIEW.exe is 64-bit (PE32+, `diag_c136_4_mem.log:18-19`); a fresh
       LabVIEW with nothing loaded holds 567.7 MB (`:114`) and the bed copy loads at 576.5 MB (`:85`) — the VI adds ~9 MB. The
       0.543 MB/op "load growth" fit was baseline noise (same file differed by 28.8 MB). Memory grows WITHIN a session (reads
       ~1.9 MB each, `:86`; edits per memory_model) and resets on restart. ⇒ P4 IS feasible as several fresh LabVIEW sessions; the
       session table uses each session's MEASURED input load (≈ 576–600), not a cumulative growth term. The PD300(c) re-plan branch
       is not taken.
     - **(b) Error 2 not reproduced:** 40 whole-VI reads, max 653.5 MB, no error, handles flat (`:82-88`). The 700 stop and X10's
       675/690 stay (no evidence above 654); raising them needs a later run that reaches ≥ 800 MB, not needed for P4.
     - **(c) 136-3's run stopped on OUR script** (a node created in a new While body not found by the per-node lookup,
       `diag_c136_3_routes.log:36-46`) ⇒ patch the lookup and rerun the same routes; no review owed for the route itself.
     - **(d) Stop-mode reads need a read-only op** (no generic property reader, `docs/cycle27-plan.md:1703`): one op reading
       `While Loop.Stop If True?` and a Boolean's `Mechanical Action`, built on the `OpLoopEndRef_v0` pattern
       (`tools/bench/build_oploopendref_v0.py:250-266`) — a tool the deliverable needs (PD298(e)).
     - **(e) stagesim step 102 (`#686 owns no terminal` while the real graph lists t8936 on 686)** is diagnosed offline next, read
       only first; a stagesim fix runs in a card with no LabVIEW card beside it.
302. **(cycle 137 judgement, 2026-10-02 — at cycle start; cards 137-1 / 137-P1 / 137-2, brief `tools/bench/cards/brief_137.md`)**
     USER-RULES: none apply (measurement, tooling and a review disposition; no VI design).
     - **(a) Cards:** 137-1 (LabVIEW, scratch) = 136-3's routes rerun with the new-While-body lookup fixed (PD301(c)); 137-P1 (offline,
       read-only) beside it; 137-2 (LabVIEW, after 137-1 returns) = the read-only stop-mode op (PD301(d)). One LabVIEW card at a time.
     - **(b) PD301(d)'s pattern path is `tools/recipes/build_oploopendref_v0.py:250-266`** (it cited `tools/bench/`, which does not exist).
       137-P1 also lists v3's unmeasured route classes against 137-1's routes, so the next scratch card closes ALL of them at once.
     - **(c) Review `archive/peer/2026-10-02-c136-3-c135e-elmismatch.md` disposed:** its mechanism correction is accepted ("missing 2" =
       loose ends 22 → 20, a real VI change — the class-level fact PD297 accepted the bed on; the bed stays, STRUCTURAL); its item-level
       one-sided-wire test runs in 137-P1 (a difference other than {4878 + one of 3268/30592/28437} reopens the bed for judgement);
       `errorlist_check.compare()` naming the missing classes is a tooling carry for a card with no LabVIEW card beside it.
303. **(cycle 137 judgement, 2026-10-02 — after 137-P1 PASS 5/0, `tools/bench/prep_c137_p1_facts.md`)**
     USER-RULES: none apply (plan addressing, session arithmetic and a structural check; no VI design).
     - **(a) Step 102 is a PLAN fault, fixed in the plan:** v3 addresses ControlTerminal t8936 as {uid 686 (its owner diagram), term 8936};
       `vigraph.node_of` (`tools/vigraph.py:57-60`) and the executor (`tools/stagexec.py:1493-1496`) both key a ControlTerminal by its OWN
       uid. Simulator and executor agree, so the tools are not changed; v4 = v3 with the 5 CT ends (v3 steps 102, 104, 115, 116, 143)
       re-addressed by own uid (card 137-P2). PD301(e)'s "stagesim fix" is not needed for this stop.
     - **(b) Session table accepted as measurement:** at the bed load 600.2 and stop 675, option 1 = 12 sessions / option 2 = 11; build
       unit U05 alone reaches 676.9 > 675 ⇒ U05 is re-cut before its launch (690 launch stop not used as a planning bound). Broken
       files: option 1 → 10 total, option 2 → 6 total (exactly the cap, P5 then needs a run first). These numbers go to D-2026-10-02-04's
       next report; the question itself is unchanged.
     - **(c) Route coverage:** 24 unmeasured route classes / 113 actions; 137-1 covers 7 actions. The remaining 17 classes (78 of the 105
       uncovered actions sit in 9 classes on base body `#23166`) are measured in ONE bed-byte-copy scratch run, one action per class, on
       the lookup 137-1 fixes — written after 137-1 returns (it reuses that script), never a P4 build card before it.
     - **(d) Review c135e §4 settled:** source-only one-sided wires P3b-1 → P3b-2 differ by {4878} only, sink-only identical, no new
       loose-end wire. The "{4878 + one of 3268/30592/28437}" clause rested on those wires being one-sided; they are two-sided in P3b-1, so
       the clause was a wrong premise, not a failed test. The falsifier that mattered (a NEW loose end) did not occur ⇒ the bed stays.
       One of the two lost `Wire has loose ends` items is not traceable by `prof()` — recorded, not chased (structural only; P6 decides).
304. **(cycle 137 judgement, 2026-10-02 — after 137-1 FAIL 3/1, `tools/bench/cards/result_137-1.json`)**
     USER-RULES: none apply (tool verification; no VI design).
     - **(a) Second failure on the SAME scripting function ⇒ scratch-VI verification, not a third route run** (CLAUDE.md "Scratch-VI
       verification before a third try"): 136-3 and 137-1 both stopped at const `#29466`, created by `const_donor` in the new While body
       `#29431`, which `node_labels` lists on NONE of the 180 Diagram indices (`diag_c137_1_routes.log:36-48`); the stale-index cause is
       refuted. Card 137-3 measures, in a new empty VI and in a bed byte copy, which read method (node_labels per index, Diagram count,
       read_terms by owner uid, Stage.address) finds a const and a primitive created in a new While body. No route card until it PASSes.
     - **(b) The route rerun and the 17-class route run (PD303(c)) both wait on (a)'s result;** the stop-mode op (137-2) runs after 137-3.
305. **(cycle 137 judgement, 2026-10-02 — after 137-P2 PASS 4/0, `tools/bench/prep_c137_p2_facts.md`)**
     USER-RULES: none apply (plan routing; values unchanged, U1 untouched).
     - **(a) v4 (`plan_ring_p4_v4.json` a30f7700) accepted:** the 5 CT ends now resolve; replay 1–101 unchanged, and step 102 stops on a
       direct `connect_term_uid` across base While `#10170`'s border (`tools/stagesim.py:1366`), a class stagesim does not model. By the
       PD298(b) precedent (explicit loop-input tunnel action on `#10170`, simulator not extended) the 3 crossings `p4_x_fd`, `p4_x_dt`,
       `p4_x_n2_out` each get an explicit tunnel action first → v5 (card 137-P3). The tunnel route is on the scratch list (PD303(c)).
306. **(cycle 137 judgement, 2026-10-02 — after 137-P3 FAIL 8/2, `tools/bench/prep_c137_p3_facts.md`)**
     USER-RULES: none apply (plan routing and step size within the user's D-2026-10-01-01 bound).
     - **(a) v5 `plan_ring_p4_v5.json` 91f6476e accepted as an intermediate:** 2 tunnels (`p4_t_fd`, `p4_t_dt`) on `#10170` + inner wires,
       pool-crossing form (v4:1069-1095); the replay passes the old stop and reaches step 103. `p4_x_n2_out` is NOT a `#10170` crossing
       (FS4 frame → body 23166) — left as is until the replay reaches it; PD305(a)'s "3 crossings" premise was wrong for it.
     - **(b) The 2 RLE actions `p4_rle_x_fd` / `p4_rle_x_dt` are DROPPED (v6):** with an explicit tunnel both wires are same-diagram, the
       PD255(b) RLE-after-crossing rule existed for `connect_term_uid`'s auto-tunnel stub (PD252(d)), and the pool form has no RLE. Whether
       a loose end still appears is read from the tunnel-route scratch run's Error List count, not assumed.
     - **(c) Step 3 = 41 actions is ACCEPTED** under the user's "≤ ~40" (D-2026-10-01-01, PD261(d)); a re-cut would add a broken file under
       the 6-file cap for one action. A step above ~42 is re-cut.
     - **(d) Next offline card:** v6 = v5 minus (b), replay to the next stop; dispatched when no LabVIEW card is live (prep budget 3/3 used).
307. **(cycle 137 judgement, 2026-10-02 — after 137-3 PASS 5/0, `tools/bench/diag_c137_3_lookup.log`; review c137-p3-mkv5-stepcount)**
     USER-RULES: none apply (tool behaviour and plan checking; no VI design).
     - **(a) MEASURED (both legs, empty VI and bed copy): a `const_donor` constant in a new While body is NOT in `Diagram.Nodes[]`**
       (`node_labels`, `Traverse Node`, hence `stagekit.address` — `stagekit.py:790,804-805`) but IS in `Traverse Constant` and in
       `read_terms` (OpAllTerms_v1) by owner uid, which also returns its terminal uid (`diag_c137_3_lookup.log:36-45`). A primitive in the
       same body is found by every method. ⇒ diagnostics look up body CONSTANTS by `read_terms` by owner uid (it yields the terminal
       uid a wire needs); route rerun = card 137-5. **Tooling carry:** `stagekit.address`/`Stage.address` cannot address a constant in a
       NEW body — before a P4 build card relies on it, an offline check names every v6 action that addresses a body constant that way.
     - **(b) A replay is not executor acceptance:** `stagexec.compile_plan` requires a tunnel's two wires right after it
       (`stagexec.py:676-685`); every plan-replay card from now also runs `compile_plan` (137-4 does it for v5 and v6).
308. **(cycle 137 judgement, 2026-10-02 — after 137-4 FAIL 5/2, `tools/bench/prep_c137_4_facts.md`)**
     USER-RULES: U1, U9 (relied on: valid frames run the original nodes unchanged; a torn frame has no effect outside 1.2; none contradicted).
     - **(a) v6 `plan_ring_p4_v6.json` 99586b73 accepted as an intermediate:** 165 actions, steps 33/35/41/36/20, replay to 163 (cdiff 23),
       `compile_plan` compiles 1–157 incl. both `#10170` tunnel groups. The placeholder `decide p4_dec_reseed` (v6:2170-2183) is NOT a
       question: PD300(b) chose option 2 — Select(valid, `#9647` out, Local read of the same flag) → t25557. v7 = that (card 137-6).
       `#10465` (the other sink of `#9647`) stays on the raw value — computation unchanged; its downstream sinks are reported as facts,
       and if they leave loop 1.2 for saved data, PD298(d) is applied by a later judgement item, not inside the card.
     - **(b) `p4_x_n2_out` (plan-made FS4 frame → body 23166, an FS EXIT) is the U6 route 137-5 measures;** stagesim models FS entry only
       (`stagesim.py:1364-1365`). The simulator gets an FS-exit row MODELLED ON U6's MEASURED census (tunnel created, name, loose end),
       in a tooling card with no LabVIEW card beside it — the next cycle's first act, after 137-5's U6 record exists.
309. **(cycle 137 judgement, 2026-10-02 — after 137-5 FAIL 3/1, `tools/bench/diag_c137_5_routes.log`; review c137-4-mkv6-step164)**
     USER-RULES: none apply (route measurement; no VI design).
     - **(a) Routes MEASURED on scratch:** A2, U1 ×3, U2, W1-Or PASS; U5 (FS entry from a plan-made While's outer face) PASS after RLE with
       the source wire re-created. **U3 FAIL** (Select.s ← `Greater?` on the Num array broken, w29730; LT.y ← KMX broken; KMX was created
       DBL, not I32 — log:75,108-110,127-129). **U6 FAIL** (FS-frame EXIT: tunnel #29822 created, exit wire 29706 broken before and after
       RLE, log:167-169). Both are measured "does not work", causes open ⇒ card 137-7 reads types, endpoints and per-combination
       Is Broken? (with an external fact question on Select's Boolean-array selector) — no redesign before those facts.
     - **(b) FS exit route (PD308(b) AMENDED):** both stagesim (refuses) and `compile_plan` (files it as a plain `connect`,
       `stagexec.py:720-721`) lack an FS-exit route; it is built in BOTH from a PASSING U6, never as a loop `tunnel` action on a Flat
       Sequence (would pass both checks on a wrong plan — review §1).
     - **(c) Carry:** steps 160/162 replay "ok" without a measurement in that enclosing structure (`FS_BORDER_SIG` ignores it) — UNMEASURED.
     - **(d) The stop-mode op (card 137-2, ready and validated) moves to cycle 138** — the 6-dispatch cap is spent on the route blockers.
310. **(cycle 137 judgement, 2026-10-02 — after 137-6 FAIL 3/1, `tools/bench/prep_c137_6_facts.md`)**
     USER-RULES: U1, U9 (relied on: original nodes unchanged on a valid frame; none contradicted).
     - **(a) v7 `plan_ring_p4_v7.json` 01ab0893 accepted as the current P4 plan:** 172 actions (steps 33/35/41/36/27), the decide replaced by
       PD300(b) option 2 (8 actions); **`compile_plan(v7)` compiles ALL actions to 160 ops** (37 in step 3). Replay stops at 159.
     - **(b) The raw re-wire `#9647` → `#10465` t10469 STAYS:** `#10465` (Case `#10445` input tunnel) has no inner sink in either frame, so
       dropping it would change no number — but keeping it keeps the original's structure (the least change, rule 1a); not re-opened.
     - **(c) Stop 159 (`#10465 owns no terminal` after `delete_wire` w25415) is a SIMULATOR defect** (the graph has 3 rows for #10465): it goes
       to the same stagesim tooling card as the FS-exit row (PD309(b)), with a self-test reproducing it, run with no LabVIEW card beside it.
311. **(cycle 137 judgement, 2026-10-02 — after 137-7 PASS 5/0, `tools/bench/diag_c137_7_types.log`; reviews c137-7-hyp-c137-5-routes, c137-7-select-boolarray-fs-exit-gemini)**
     USER-RULES: U9, U13 (relied on: the reader takes the smallest `Num > last` and verifies n1 == n2; a gap is fine). None contradicted
     — this item changes only HOW the new reader computes its own index, not the original's computation (U1 untouched).
     - **(a) MEASURED + externally confirmed: Select's `s` takes a SCALAR Boolean only.** A Boolean array on `s` breaks the wire whatever
       `t`/`f` carry (C1/C2/C3 broken, scalar control C5 unbroken, `diag_c137_7_types.log:171-189`; LabVIEW's own Error List "source 1D array
       of boolean, sink boolean", `errorlist_c137_5_routes_20261002_154406_raw.json:598-600`; NI docs via the fact peer). The P4 reader's
       "Select on a Boolean array" (U3, PD293/v7's smallest-`Num > last` group) is IMPOSSIBLE as planned.
     - **(b) REDESIGN of that group:** a For loop auto-indexing `Num` (20 elements); inside it ONE scalar `Select(Num[i] > last, Num[i], MAX)`
       with MAX = I32 2147483647 made by `const_donor` (I32 measured, `:212-216`; `const_row` on Select.f before `t` gives DBL, `:218`); the
       auto-indexed output → `Array Max & Min` (min) = the smallest `Num > last`, MAX when none — the same value the array form was
       meant to give. The For loop + auto-index tunnels are a NEW structure class on this path ⇒ prior-art review and a scratch route
       measurement before a build card; rejected: arithmetic masking (MAX − Num overflows I32 at Num = −1).
     - **(c) FS EXIT works with a typed source** (U6′: tunnel faces I32, both wires unbroken, `:290-306,317,328`); U6 failed only because its
       source `IAN.array` was unwired (void). The stagesim + stagexec FS-exit route (PD309(b)) is modelled on U6′. Carry: U6′'s new tunnel
       faces carried the label `Index of closest\ncal image slice, bead 2` (`:301-302`) — the tunnel-name gate must predict it or flag it.
     - **(d) Name fix:** Select's output terminal is `'s? t:f'` (no space, `diag_c128_2_donors.log:62`); plans saying `'s? t: f'` are wrong.
     - **(e) Next cycle, in order:** ONE offline tooling card (no LabVIEW card beside it): stagesim FS-exit row from U6′ + the `delete_wire`
       row-loss defect (PD310(c)), each with a self-test, and stagexec FS-exit route; then v8 = v7 with (b) + (d); then a scratch route run
       of (b)'s For-loop group and the 17 uncovered route classes (PD303(c)); the stop-mode op (card 137-2) when the LabVIEW slot is free.
312. **(cycle 138 judgement, 2026-10-02 — after 138-1 FAIL 5/1, 138-2 PASS 5/0, 138-3 PASS 5/0, 138-4 PASS 5/0, 138-5 PASS 5/0)**
     USER-RULES: U1, U4, U9, U13 (relied on: original nodes unchanged; the stop signal between loops is a local variable; the reader's
     smallest `Num > last` with seqlock; none contradicted).
     - **(a) Tooling accepted:** stagesim FS-exit row modelled on U6′ (`tools/stagesim.py:190,1399,1989`, self-test 14/0) and the
       `delete_wire` row-loss fix (`DROP_WHEN_UNWIRED` had `Tunnel` with no sample; now LoopTunnel only, `stagesim.py:67`); stagexec
       FS-exit route `fs_exit` (`stagexec.py:644`); c125_1 PASS 6/0; v7 replay END 172/172 (`tools/bench/prep_c138_1_facts.md`). X10 counts
       reads from the SOURCE (`stage_prerun.py:2109,2268,2309`, self-test 12/0); diag_c136_1_routes now FAILs at 806 MB as it should;
       P3b-2 a/b still PASS (`tools/bench/prep_c138_2_facts.md`). Conservative total kept as the X10 verdict; a multi-session script's total
       reads are the per-session bound until that blocks a launch. 138-1's one FAIL = two STALE self-test fixtures, red at HEAD
       (`tools/bench/prep_c138_3_facts.md`) — re-pin them on frozen copies (carry, tooling card).
     - **(b) v8 `plan_ring_p4_v8.json` 059b5296 accepted as an intermediate** (181 actions, compile 163 ops, per step ≤ 37, replay END,
       end cdiff 24 == v7's). `Greater?` stays OUTSIDE the For on the arrays: the auto-indexed mask element i equals `Num[i] > last`, the
       same value (`tools/bench/prep_c138_4_facts.md:11-13`). The 11 unclassed end-cdiff rows are carried from v7, not caused by v8.
     - **(c) MAX constant: ONE measured donor `claudeDev\DonorI32Max_v0.vi` (I32 2147483647) for BOTH KMX1 and KMX2.** The prior-art's
       const_row for KMX2 is REFUTED for this plan: const_row's type depends on wiring order (DBL measured, `diag_c137_7_types.log:218`) and the
       review itself marks the I32 outcome UNMEASURED. IndexMode: the review is RIGHT — v9 adds a recipe-level `index_mode_fix` + read-back
       gate per auto-index tunnel (PD235(c) form, `docs/d1-loop12-17-split-plan.md:2212`), since the executor sets it only under `if lost:`
       (`stagexec.py:2104-2109`).
     - **(d) `stop (end)` reads Mechanical Action 4** and every bed While loop is Stop-if-True (`tools/bench/diag_c138_5_facts.md`, op
       `OpStopModeB_v0`). 3–5 are the latch actions ⇒ PD298(e)'s LATCH branch applies: ONE writer (loop `#639`) writes a new non-latch
       Boolean indicator `StopAll` each iteration; W1 and 1.2 read it by local (U4). The latch reading of 4 is confirmed on the machine by a
       scratch Boolean set to 4 with a local variable (LabVIEW refuses a local of a latched Boolean) before v9 is launched.
     - **(e) Next:** LabVIEW card 138-6 (scratch only): DonorI32Max_v0 built + read back; the For-loop group on a scratch VI with IndexMode
       read-back and one functional run on known values; `#10465` after `delete_wire` w25415 on a bed byte copy (does LabVIEW remove the
       unwired Case tunnel? UNMEASURED, `prep_c138_1_facts.md` OPEN); latch-local test; op hygiene records into `tools/bench/op_hygiene/`.
       Beside it, offline prep 138-P1: v9 = v8 + (c) + (d) + IndexMode gates, replay + compile_plan, prior-art release lines, NAMES rows.
313. **(cycle 138 judgement, 2026-10-02 — after 138-6 FAIL 23/1 (`tools/bench/diag_c138_6_facts.md`), 138-P1 FAIL 19/1 (`tools/bench/prep_c138_p1_facts.md`); review c138-6-p1cmp-routes)**
     USER-RULES: U4, U6 (relied on: the stop signal is a local variable of a plain indicator; nothing paces acquisition; none contradicted).
     - **(a) MEASURED:** `claudeDev\DonorI32Max_v0.vi` md5 c0c8db65, constant uid **127**, I32, 2147483647, ExecState 1 ⇒ KMX1/KMX2 bind uid 127.
       Case tunnel `#10465` SURVIVES `delete_wire` w25415 with its 3 rows (as the fixed stagesim predicts); Error List 51 → 52, the new item
       unidentified (count-only read) — v7's step 159 re-wires it at once; the item is named in the next scratch read. A local variable of a
       Boolean at Mechanical Action 4 breaks the VI ("Boolean latch action is incompatible with local variables") ⇒ PD312(d)'s latch branch
       is CONFIRMED on the machine. Op hygiene records for `OpStopMode_v0`/`OpStopModeB_v0` now in `tools/bench/op_hygiene/`.
     - **(b) 138-6 step 2 (the For-loop group) stopped on OUR script:** the scratch put the group on the TOP-LEVEL diagram, where
       `create_control_nested` refuses (`gscript.py:4149`). v8 puts the For inside W1's body, so the rerun builds the scratch the same way
       (While → For inside), which is both the fix and the faithful measurement — no tool edit. `read_terms` lists no For-owned terminal
       (the `i` terminal); v8 does not use `i` (N comes from auto-indexing), so it is a fact, not a blocker.
     - **(c) 138-P1's route change is a PLAN-MAKER bug:** `prep_c138_p1_mkv9.py` copied v8's position-indexed `finalized.fs_routes` table
       unchanged after inserting an action at #4, so 3 untouched wires (`p4_w_b_out`, `p4_x_bufdiff`, `p4_x_i_rab1`) compiled to other
       routes (review c138-6-p1cmp-routes). v10 regenerates that table from the plan (never copies it); the route compare v8 → v10 must then
       show changes ONLY on added/edited actions. v9 b91cf4d7 is NOT accepted.
     - **(d) StopAll start value:** a plain indicator keeps the previous run's True at start, so W1/1.2 could stop before `#639` writes it.
       v10 initialises `StopAll` = False on FS1 frame `#4866`, outside the loops, every run — the PD240(b)(c) mechanism already used for the
       ring indicators (`docs/d1-loop12-17-split-plan.md:2287,2292`).
     - **(e) Next cycle, two cards in one message:** LabVIEW scratch = 138-6 step 2 rerun inside a While body (For + 3 auto-index tunnels with
       IndexMode read-back, scalar Select f = donor uid 127, Array Max & Min, ExecState 1, one run on known values) + a full Error List read of
       a `delete_wire` w25415 byte copy naming item 52; offline = v10 per (a)(c)(d), replay + compile_plan + route compare v8→v10, disposition
       of review c138-6-p1cmp-routes written. Then the 17-class scratch route run (PD303(c)), then P4 build sessions (D-2026-10-02-04 open).
