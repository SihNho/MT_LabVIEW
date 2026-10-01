# Brief 125-5 — Flat Sequence op (route a), then a scratch check of connect_term_uid's case-border stub (LabVIEW)

Decisions: `docs/d1-loop12-17-split-plan.md` Pre-decided **252(d)(e)**. Previous card `tools/bench/cards/result_125-4.json`
(`diag_c125_4fsm.log:23-54`, `diag_c125_joints.log:26,39`). Beds (P3a `4dfa44aa…`, P2b `652b1447…`) are NEVER saved over;
work on BYTE COPIES only. Scripts <= 120 lines on stagekit (the P3a-bed byte copy + plan route 125-4 used for
`diag_c125_4fsm` passes the dry gate).

## STEP 1 — new op `claudeDev\OpFsAddFrame_v0.vi` (route a, DECIDED — not the donor route)
- Input: VI path + FlatSequence uid, Reference Frame Index, After(T). It resolves uid → GObject → To More Specific Class
  (FlatSequence) → Invoke `3578B800` (Add Frame), closes every reference it opens, returns the new frame's uid and error.
- Frame-ORDER reader: `FlatSequence.Diagrams[]` (`3578BC00` per 125-4) → list of frame diagram uids, left to right. Reuse
  an existing generic property/array-of-references reader op if one already reads it; otherwise a second new op.
- Hygiene record for each NEW op: >= 2,000 consecutive calls, 0 errors, handles flat ±100,
  `tools/bench/op_hygiene/<op>.json`.
- How the FIRST frame is created is yours to measure (New VI Object for a Flat Sequence on a given diagram = 1 frame,
  per the fact answer; an existing `new_object`-type function, or `struct_copy_nested` of a 1-frame donor).
- Scratch on a P3a byte copy: Flat Sequence on case `#22694`'s FALSE frame, Add Frame twice → 3 frames; read back frame
  count, left-to-right order, per-frame diagram uid, census delta; a frame-1 constant → frame-2 primitive wire through a
  sequence tunnel (class, `Is Broken?` False), and `wire_joints` on that wire: free segment ends = 0.
- Deliver: gscript function(s), census sample, `tools/bench/scratch_verify/` record; list what the stagexec route and
  stagesim model need.

## STEP 2 — scratch-VI verification of `connect_term_uid` across a case border (measurement; runs if LabVIEW is clean)
125-4 found that P3a's row `p3a_w_cnt_in` (register LEFT inner face → node inside case `#22694`, STEPX 15) left wire
`w27378` with one dangling segment end (joint 3, LOOSE 0x100, no terminal) on the tunnel's OUTER face `#27365`.
1. Reproduce on a minimal scratch VI (While + shift register + a `case_wired` case + a node in its False frame): one
   `connect_term_uid` call register-inner → node, then `wire_joints` on the resulting outer wire. Record whether the stub
   appears (count free ends).
2. If it appears: measure ONE candidate removal on that scratch, read joints again, and `Is Broken?`. Candidates in
   order: a Wire method that cleans up / removes loose segments on THAT wire only (look it up first; a `-Kind fact` peer
   if unsure), or deleting the stub segment. Do NOT use a whole-VI "Remove Broken Wires" (it would also delete the 28
   known loose wires on the beds).
3. Report: stub yes/no, the removal that worked (method id, effect on joints / terminals / `Is Broken?`), or none.
   No change to `connect_term_uid` itself in this card; record what the change would be.

## Rules
- No stage recipe run; beds unchanged; scratch copies deleted or md5-recorded; LabVIEW closed and verified gone.
- Return at the first unexpected result in STEP 1 (finish it, close LabVIEW, record facts), then still run STEP 2 if
  LabVIEW is clean. A failing log → Jev ladder row; an owed hypothesis review is dispatched.
