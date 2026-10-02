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
