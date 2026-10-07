ATTACK this claim about a failed check in an OFFLINE prep script (no LabVIEW): `tools/bench/prep_c145_2_fix.py`, log
`tools/bench/prep_c145_2_fix.log` (BGRUN END rc=1, 16 pass / 1 fail).

What the script does: card 145-a1-2 step 2. It edits ONLY the SQ1 row (`p4_s2_seqcheck`, SubVI RingSeqCheck_v0.vi) of
`tools/bench/plan_ring_p4_s04v18.json` (old md5 9ff46b0e, byte copy kept as `tools/bench/prep_c145_2_plan_9ff46b0e.json`): its
terminal list goes from 8 named rows to the MEASURED 12 rows (8 named + 4 '' sinks t0,t4,t5,t6, in t-index order, read from
`tools/bench/diag_c144_p4s04v18_scratch.log:231-242`). Then it re-simulates the plan with `tools/stagesim.py` `simulate()` on the
unchanged base and compares the new `finalized` block with the old one.

Observed: every comparison PASSES (FINAL, end_cdiff_rows, open_rows, fs_routes, route_check rows, fs_border_gate) except gate A:
"addr_pos == old except SQ1 rows". The SQ1 rows themselves came out exactly as predicted (last index 2 -> 9, n1 index 0 -> 11 == the
measured t-index). Some NON-SQ1 addr_pos row differs; the log does not print which.

CLAIM (the explanation to attack): the failure is in MY CHECK, not in the plan or the simulator. stagesim allocates symbolic negative
uids sequentially per created node AND per terminal; SQ1 is node -38 with 8 terminal ids (-39..-46), so the next object is -47 (the
pred's `errorlist.fixed.detail_end` has local -47 'Latest' = p4_lr_latest, created right after SQ1, `tools/bench/plan_ring_p4_s04v18_pred.json`).
With 12 terminals every symbolic id allocated after SQ1 shifts by -4, so the `owner` field of later addr_pos rows (TL1 -54, TN1 -63 in
the old plan, `tools/bench/plan_ring_p4_s04v18.json` finalized.addr_pos) changes; their index/class/name/addr do not. The plan is
rebased (no negative uid in actions), so the shift touches only sim-internal ids; the pred is regenerated from the new step files.

Planned next act: rerun the script with the check narrowed to (addr, source, index, class, name) for non-SQ1 rows plus an explicit
owner-shift check (every changed owner = old - 4 and old <= -47), and print the differing rows.

Questions: Is the sequential-allocation explanation wrong or incomplete (could the difference be a real change of routing or of a
terminal binding)? What would falsify it? Does an id shift of later symbolic objects endanger anything downstream (stagexec binding
of created objects by symbolic id, the recipe's checkpoint/bind map, the creation map, the Error List predictor's new_items keyed by
negative uid, `stage_prerun --prerun`)? Name the cheapest discriminating test.
