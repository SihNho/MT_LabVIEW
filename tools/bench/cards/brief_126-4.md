# Brief 126-4 — RemoveLooseEnds op + w27378 removal; outer → Flat Sequence frame crossings (retry of 126-2)

Decisions applied (do not re-open): `docs/d1-loop12-17-split-plan.md` PD254(c)(e), PD253(d). Measurement only.

## STEP 0 — op on Wire method `6370C08` RemoveLooseEnds (measured, `diag_c126_2_op.log`)
- Fix `diag_c126_2_op.py`'s gate M1: match the method by id `6370C08` AND LabVIEW's data name (`RemoveLooseEnds`), never a
  spaced literal. Build ONE op (e.g. `claudeDev\OpWireRemoveLooseEnds_v0.vi`: uid → Wire → Invoke 6370C08, UID echo,
  every reference closed). Rename `gscript.wire_cleanup` to match the op it calls.
- Hygiene ONLY via `gscript.hygiene_run(op, workload, recycle=True)`. PD242(b) VERBATIM: "For a CREATOR the probe may
  delete each created constant+indicator after its call, or recycle the scratch VI without saving at fixed call counts,
  measuring handles at the same VI state each time." ≥ 2,000 calls, 0 errors, ±100. The workload may call the method on
  healthy wires (PD254(c)).

## STEP 1 — w27378 on a P3a BYTE COPY (never the bed)
- Before / after RemoveLooseEnds on w27378 only: `wire_joints` (joint 3 LOOSE expected before), `Is Broken?`, the wire's
  terminals (still connected to tunnel `#27344`'s outer face `#27365` and its sink?), class-count census delta, and
  `errorlist_check.py --count-only --role scratch` per-class counts (P3a pin: 55 items).

## STEP 2 — `diag_c126_2_fs.py` (prerun 14/0) on a fresh P3a byte copy, extended (≤ 120 lines)
- Keep its FS build (3 frames in `#22694`'s False frame `27219`) and its read-only tail, using the renamed op.
- ADD (PD254(e)): from an output terminal of a node on case frame `27219` (P3a's `Quotient & Remainder` remainder `i` —
  find its uid in the copy's graph), wire by `connect_term_uid` to a node input in FS frame 1, then a SECOND sink from the
  same source into a node input in FS frame 3. Read per wire: census delta, `Is Broken?`, free ends, the tunnel(s) made
  (class, uids, which frame faces), and the Error List count-only delta for the whole FS build vs the copy's start.
- If a one-terminal stub appears, read it the same way and apply RemoveLooseEnds to it.

## Always
- Close LabVIEW at the end and verify it is gone; bed md5 unchanged; scratch copies deleted.
- Return at the first unexpected result (finish the step cleanly). Facts in `result_126-4.json`; JEV row if a gate fails.
