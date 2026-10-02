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
