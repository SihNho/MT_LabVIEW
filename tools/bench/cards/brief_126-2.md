# Brief 126-2 — one-wire cleanup on w27378 (PD253(d)), and the Flat Sequence scratch's one-terminal wire

Decisions applied (do not re-open): `docs/d1-loop12-17-split-plan.md` PD253(d) — measure the REMOVAL on the real wire;
never a whole-VI "Remove Broken Wires" (it would delete the 28 known loose wires too). Measurement only; no prediction
decides an action inside this card.

## STEP 0 — the Wire cleanup method
- Find the Wire class method that cleans up ONE wire ("Clean Up Wire" in the LabVIEW scripting class reference; its id is
  not measured). Measure its id from LabVIEW's own class data the way `FS_METHODS` was measured (`diag_c125_4fsm.py`), not
  from a peer answer alone.
- If no existing op invokes a Wire method by uid, build one NEW op (`claudeDev\OpWireInvoke_v0.vi` or similar: uid → Wire
  → Invoke <id>, UID echo as in `OpFsAddFrame_v0`, every reference closed). Its hygiene check goes ONLY through
  `gscript.hygiene_run(op, workload, recycle=True)` (`tools/gscript.py:360`) — PD242(b) VERBATIM: "For a CREATOR the probe
  may delete each created constant+indicator after its call, or recycle the scratch VI without saving at fixed call
  counts, measuring handles at the same VI state each time." ≥ 2,000 calls, 0 errors, ±100.

## STEP 1 — w27378 on a P3a BYTE COPY (never the bed `D1_ring_p3a_20261001_180540.vi`)
- Before: `wire_joints` on w27378 (joint 3 LOOSE expected, `diag_c125_joints.log:26,39`), `Is Broken?`, Error List
  `errorlist_check.py --count-only --role scratch` per-class counts.
- Apply the cleanup method to w27378 only. After: the same three reads, plus the wire's terminals (source `#27365`'s
  tunnel and its sink still connected?) and the class-count census delta. Report the numbers; P3a's pin is 55 items.

## STEP 2 — the one-terminal wire left by a cross-frame `connect_term_uid` inside a Flat Sequence
- Re-run `tools/bench/diag_c125_5_fsscr.py` (md5 `fd2d339f…`, 15/0 in card 126-1) on a fresh P3a byte copy, but keep the
  copy open for reads before it is deleted (a read-only addition after its last gate, ≤ 120 lines total).
- Card 126-1 found wire `#32592` (1 joint, 1 terminal: tunnel `#32584`'s outer face on case frame `27219`) and a second
  FlatSequenceInnerTunnel `#32599` with no wire (`diag_c125_5_fsscr.log:57,59-60`; uids will differ on a rerun — find them
  the same way). Read: their `Is Broken?`, the Error List per-class counts (count-only) vs the copy's starting counts, and
  the cleanup method's effect on that wire (same three reads after).

## Always
- Close LabVIEW at the end and verify it is gone; bed md5 unchanged; scratch copies deleted.
- Return at the first unexpected result (finish the step cleanly). Facts in `result_126-2.json`.
