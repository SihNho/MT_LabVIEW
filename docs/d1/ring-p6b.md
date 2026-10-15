---
type: decision
kind: topic
status: current
date: 2026-10-13
parent: docs/d1/INDEX.md
tags: [d1, ring-buffer, p6, replay, dry-taint, fp-103, pre-decided]
---

# Ring buffer P6 — continued (`docs/d1/ring-p6.md` is near the 400-line cap; PD412 and earlier live there)

413. **(cycle 171 judgement, 2026-10-13 — `handback_171_1.json`, trigger a: 171-a1-2, the one retry of PD412's fix, FAILed
     `selftest_dry_c130_5` T3, cause not diagnosed)**
     USER-RULES: U1 (relied on: a dry-checker change touches no VI and no computation); none contradicted.
     - **(a) PD412(b) is NARROWED to the value criterion of patch af6937e8 (`diag_c171_a1_2_patch.diff`, f8f1fd95).** The
       literal rule ("every name bound in a stub-touching statement is tainted") contradicts card 134-1 T1: its FR gate reads
       `real` = 5911 simulated rows bound by `x.run()`, which touches Fakes inside the simulator, and T1 must FAIL at FR
       (`diag_c171_a1_1_facts.md:10-12`). The bound VALUE separates the two cases: a name is tainted when its value is a
       Fake, holds a Fake, is an EMPTY container, or is unbound. Scalars from a stub stay clean; that is the checker's
       behaviour BEFORE this fix (status quo, not a new hole). Evidence the patch met PD412(c)(1)-(2): plan 170 A2
       UNVERIFIED, dry ends PASS-UNVERIFIED, unverified 7 (`diag_c171_a1_2_dry170.log:10,28`); c134_1 11/0 = record.
     - **(b) PD412(c)(3) is met in substance:** with the patch, plans 78 and 110 give their stored verdicts again (same
       labels), and the unpatched db81a1d3 does NOT (FAIL A2), so fp-103 already broke them. Plan 95 has no graph (same
       before and after); the ring recipe p5s02c gives PASS before and after (stored FAIL PB is older than the recipe's
       last change). These are facts, not failures (`diag_c171_a1_1_facts.md:26-30`).
     - **(c) c130_5 T3 is decided by ONE measurement:** run `selftest_dry_c130_5.py` on the UNPATCHED db81a1d3 first. Its
       stored records (cycles 134, 152) are older than the PB-criterion change of PD370(b) (cycle 153, `ring-p5b.md:165`),
       so the FAIL may well predate the patch. Rule set now: if the unpatched run FAILs T3 at the same GATE PB, the
       patch is not the cause → re-apply af6937e8, record the T3 FAIL as a stale self-test fact (gate-fp entry, fixed
       after P6-2, not in this purpose). If the unpatched run PASSes T3, the patch causes it → the card returns and hands
       back; no third version of the patch is tried in this cycle.
     - **(d) Brief step 0 label swap accepted:** a89dafc1 = `replay_imaqdx_get_image_buf.vi`, 842ecad9 =
       `replay_get_buff_image.vi` (`ring-p6.md:313-315`), not drift.
     - **(e) Then PD412(c)-(d) unchanged:** prior-art review on the patch (peers priorart), drain fp-103 naming
       `selftest_c171_a1_1_taint.py` + c134_1; then P6 replay copy → S1 leg → P6 leg → compare with D = 20 → fp-102 last.

414. **(chat, 2026-10-13 — lean-rules bench and two lean tasks; cycle 171 stopped mid-cycle for the bench; PD413 not run)**
     USER-RULES: U1 (relied on: no per-bead maths changed; test copies only change timing / the frame source), U7 + U9 (the
     col-0 finding CONTRADICTS them in P6 as built - see (c)), U8 + U13 (P6 as built does not do latest-wins - see (d)), U2
     (motor sessions with readback on every run); the user's new statement "과부하가 걸리더라도 버퍼 넘버의 정확성이 데이터의
     정확성을 결정하는듯" (2026-10-13) is added as an acceptance in (c).
     - **(a) P6-2 replay, by a lean session** (branch bench/lean-20261013, report `tools/bench/lean_bench/lean_report.md`, 64 min,
       $6.64): P6 replay copy `claudeDev\bench\lean\D1_ring_p6_replay_20261013_135743.vi` 09a23608 (plan 170's two swaps, gates
       19/0); S1 leg 6321 rows lost 0, P6 leg 2538 rows; X/Y/Z bit-identical 2538/2538, DISTINCT 2538/2538 (D = 20), cal 0 bytes
       outside the date field, trans/rot 2437/2437 post-init; inputs md5 18/18 unchanged. Re-checked by the chat from the raw
       tra files. **PD409(b) items PASS - but column 0 was excluded, and (c) shows it is wrong.**
     - **(b) P6-3, by a lean session** (`lean_report_p63.md`, 102 min, $17.52; predictions written before the runs): T-gap (a
       get-buff wrapper that adds 1 to the buffer number: every frame skips one number) P6 2537/2537 rows bit-identical, 0 lost,
       0 damaged; the original (S1 copy with the same wrapper) does the same, same Total Lost Frames formula. T-load (a copy of
       RingSeqCheck_v0 with a Wait (ms) swapped into loop 1.2): W40 2540/2540, 0 lost; W100 1431 rows, 0 damaged, strictly
       ordered, 1090 lost = 311 x 1 + 41 x 19 (counted from X/Y/Z and from column 0 alike); the discard path fired 41 times.
       Copying a node INTO the P6 VI re-sourced calibration wires and broke it (ExecState 0); a callee swap of a small subVI copy
       does not. All numbers re-computed by the chat (scratch verify_p63.py): equal.
     - **(c) DEFECT - column 0 is one ring lap old.** In loop 1.2 the `FrameIdx` local read (#30239 → IndexArray #30240, wire
       30267) has no input wire: not ordered after the pick, outside the n1 → track → n2 seqlock. When 1.2 keeps up, every row
       stores the buffer number of frame k-20 (P6-2 2518/2518 rows with index >= 20, W40 2520/2520; first 20 rows -1); the
       original stores the row's own number. Under U7 (the buffer number is the time axis) and U9 (a mismatched pair is
       corruption) every such row is corrupt. TransPos/RotPos very likely share the read form (P6-2 B4) - the replay data cannot
       show it (init trans differs between any two runs). **Acceptance from now on: every saved row's buffer number (and each
       per-slot value written with it) is its own frame's, at normal load, gapped source and overload.** Task: lean task p6fix
       (`V6_lean/tools/bench/lean_bench/task_p6fix.md`, queued).
     - **(d) Overload as built is not latest-wins.** Under W100 1.2 trails at the oldest slot (~19 frames), skips single frames
       uncounted, and jumps to the newest only after a seqlock discard. U8/U13 say drop the backlog, take the newest. User
       2026-10-13 "수정하고 다음 작업 시작": fix it after p6fix (lean task `task_latest.md`, queued; starts only if p6fix PASSes).
     - **(e) Operation:** lean rules adopted by the user (discussion lean-rules-01; `docs/lean-operation-proposal.md`; decision
       `docs/decisions/lean_operation_and_buffer_number_accuracy.md`). The chat cannot start or write an autonomous lean runner
       (auto-mode classifier [Create Unsafe Agents], also with stop points between cycles); the user starts
       `V6_lean/tools/bench/lean_bench/lean_queue.ps1` or changes the permission mode. User check every 10 cycles (2026-10-13).
     - **(f) Next:** p6fix → latest-wins → P6-2 re-accepted with column 0 included → P6-3 re-run → P6-4 (beads; user first).

415. **(chat ingest, 2026-10-15 — lean runs 1-5 on branch bench/lean-20261013, merged to master; reports in
     `tools/bench/lean_bench/`, each re-checked by a Claude-GPT review from the raw files)**
     USER-RULES: U1 (every fix changes order / which frame is picked, never per-bead maths; edits only by callee swap of a
     small subVI copy - user note 2026-10-13 "큰 VI 안을 직접 고치지 말 것"), U7/U9 (acceptance #1 below), U8/U13 (latest-wins).
     - **(a) P6 is functionally DONE.** p6fix: column 0 = the row's own buffer number in every condition (P6-2 2537/2537,
       gap 2537/2537, W40 2540/2540, W100 1432/1432; X/Y/Z 9046 rows bit-identical - the review corrected the report's 10046).
       latest (3 tries): pick = newest valid slot (RingPickSlot callee swap only), W100 lag at the pick 0 on 1475/1475 picks,
       1-2 frames to the next pick. Final VI `claudeDev\bench\lean\D1_ring_p6latest_20261014_010104.vi` **15c664e3**;
       p6close re-ran P6-2 / gap / W40 / W100 on it: own number and X/Y/Z on every row (2540 / 2539 / 2538 / 1472).
     - **(b) P6-4 preparation done** (`p64_plan.md`, all section-10 questions agreed by the user 2026-10-14 "전부 동의함"):
       BOBS90 257fb852, 150 Hz rate wrapper + A150 / B150 / BOBS150 (readback 150, 149.947 fps, 0 gaps; fresh open returns to
       90.0009 Hz), ABBA drivers with a strict own-number check (p64p3, 25/0). Sample R (reference beads) "for now"; no minimum
       bead count (repeat clicks on real beads allowed). The real-bead run waits for the user (reference beads not stuck well).
     - **(c) Frame rate, Auto-Reset OFF in every leg copy** (user 2026-10-15: bead renewal costs frames; decision 2026-09-16
       "오토리셋 끄고 봐야할듯"; the saved default of `Auto-Reset` was TRUE in all sources), fixed 15 picks, no beads:
       **90 Hz (fr90)**: lost A 224 / 522, B 17 / 4, fps ~88.9, GAIN met; the earlier 3359 / 5860 for A was reseed load.
       **150 Hz (fr150)**: lost A 6182 / 5565, B 5536 / 5534, GAIN NOT met; B's camera loop keeps up (`Total Lost Frames`
       26 / 27) but only ~2 of 3 frames are saved. Own-number check PASS at both rates (11081 / 12321 rows). → PD416.
     - **(d) Sample / later:** bead-selection automation by Jev / Laya (pulled?, rotation radius, circular trace, expected
       extension - all from tracking data, so text-only Jev can judge) is DEFERRED until the coding is done (user 2026-10-15).
