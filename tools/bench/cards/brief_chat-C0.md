# Brief chat-C0 - roll back to option C (user 2026-09-28 16:0x: "C로 진행하자. 진행 방향이 잘못되었네. 롤백하고 다시 C로 진행")

Option C = camera acquisition and tracking stay in ONE loop (the frame loop `#637`), reading the newest camera buffer
every iteration (Buffer Number Mode = Last, the original's way; the user's 2026-09-15 fallback). NO image pool, NO
frame queue between acquisition and tracking. Motor reading, scheduler, file saving, display still leave the frame
loop. Control signals between loops by LOCAL variables; lossless result data to the file writer may use a queue.

Read-only analysis (2026-09-28, chat) found, with evidence:
- Stage K moved the tracking kernel `#5058` into loop 1.2 `#10170` (split-plan :69, :482, PD156 :235); L2-A/B moved its
  data slices; L2-R retired carriers; POOL/QRT exist only because `Image In` crosses 1.1 -> 1.2. ALL of K, L2-A1..R2,
  POOL, QRT-W prep are incompatible with C.
- Last C-compatible bed: `claudeDev\D1_s4_loop17.vi` (md5 4b621946..., goalmap M2). Its 1.2 `#10170` is an empty
  skeleton. Gap: file-writer inputs w4517 (`#2626` -> `#376` 'current frame data array in') and w3268 (frame index)
  are open (split-plan :75, PD164 :268-270), so it writes 0 tra rows (goalmap.json:177, tools/bench/m8_run1.json).
- Reusable: loop 1.5 (focus, local-based), loop 1.7 (writer), the display-loop branch `D1_s1_disp_20260927_041648.vi`
  (accepted: lost 16/12 vs 3,359/5,860; replay bit-identical), kswap branch for M9, all tooling.

## Do (docs/state only; NO LabVIEW; do not edit CLAUDE.md)
1. STATUS.md: `current-bed: D1_s4_loop17.vi` (verify its md5 from the file); replace the QRT/pool first act with the C
   plan below; mark the pool/QRT/L2 lines as (history, superseded by C 2026-09-28). Keep STATUS's STOP line.
2. tools/bench/next.json: act = C2 then C1 (below); advances ["M8","R2.5","R4"]; validate with protocol.py.
3. docs/d1-loop12-17-split-plan.md: a new Pre-decided item 238 "OPTION C (user 2026-09-28)" stating the rollback, the
   superseded items (K rows :69, L2 rows :70-75, :41, PD151, PD156, PD157, PD164's "future 1.2" clause only, PD177-179,
   PD221(e), PD223(b), PD225-231, PD233(f)(1)/(g), PD233(k), PD234-237; PD224(f) becomes "now, onto S4"), and the C
   build order. Add "(superseded by PD238)" markers at those items; never rewrite their text.
4. docs/goalmap.json: M3 superseded (reason); M4 re-titled "Loop 1.1 = acquisition + tracking, newest buffer each
   iteration, no image handoff", done_when "frame loop holds no VISA/display/file/scheduler work; replay X/Y/Z
   identical"; R2.3 note (user accepted acq+tracking in one loop); `current` text; M2 note (writer inputs open).
5. Mark superseded (one line at the top, text untouched): docs/d1-build-plan.md §9 pool/queues (:160, :271, :309, :407,
   :527, :572-578, :599-600, :651-652), docs/decisions.md:22 (keep :20 Last), docs/pre-rig-master-plan.md :87-88,:164,
   docs/frame-ownership-design.md:32, docs/parallel-strategy.md:34, docs/qrtw-plan-draft.md.
6. decisions_pending.json: add ONE open item (plain words, options, recommendation) for C3: motor positions Trans Pos
   `#30117` / Rot pos `#4580` are read in the frame loop today, so each saved row carries the position at that frame.
   Moving motor reading to its own loop and passing the latest value by a local changes WHEN the saved position was
   sampled (rule 1a vs R2.2). Options: (a) keep these two reads in the frame loop only if they are not serial/VISA
   calls (check: they are `.Value` reads - say whether they cost frame time); (b) motor loop + local, accept the
   sampling change and record the motor-loop timestamp; (c) other. Recommendation from the facts you find.

## C build order (for next.json / PD238)
C2 DISP-D1: port plan_disp.json T2 (9 interior nodes of `#1359` + `#11261` -> `#8323`) from the S1 branch onto S4
  (PD224(f), PD210(a)); `#2626` stays in the frame loop. Largest measured gain.
C1 writer results queue 1.1 -> 1.7 carrying w4517 + w3268 in one element; 1.7 stops on the stop local and drains.
  Acceptance: tra rows written, replay X/Y/Z bit-identical to S1.
C3 motor reading out (after the user answers the new decision). C4 scheduler loop in the empty `#10170` (locals).
C5 M11 focus redesign. C6 stop/shutdown. C7 real ABBA vs D1_s1_copy at 15 beads/90 Hz + replay. Then M9, M10.

Return result/1: files changed, doc_lint status, next.json valid, the decision item id. One git commit.
