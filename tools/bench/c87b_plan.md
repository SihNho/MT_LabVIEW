# Cycle 87, dispatch 2 — RE-RUN M3a-3b Row D CLEAN from the same bed, with two changes

`tools/recipes/stage_d1_m3a3_rowD.py` ALREADY RAN ONCE, at 2026-09-22 15:36:12
(`tools/bench/build_d1_m3a3b_rowD.log`, 20 gates pass / 1 fail, `BGRUN END rc=1 after 148s`), and it
LANDED an artefact: `claudeDev\D1_s3b_m3a3b_rowD_20260922_153612.vi`, md5
`c9d38bb194013ac7b916d073466078c7`, 307,093 B, saved through the approved broken-intermediate
`gui_save` route. That artefact is KEPT on disk. Its prior-art review is
`archive/peer/2026-09-22-priorart-c87-rowd-stagekit.md` (4 slugs, all accepted and fixed before the
run). This review is about the TWO EDITS made to that recipe afterwards, and about re-running it.

## Why re-run at all
The mandatory failed-prediction review of the D7 gate,
`archive/peer/2026-09-22-c87-rowd-d7-termcount.md`, §5, says the SAVED artefact carries an unpurged
junk `Invoke` node from the D5 ordered-second-pass connect — `Node` census 635 -> 636
(`build_d1_m3a3b_rowD.log:86` vs `:201`), `Diagram #686`'s `nodes_on_diagram` 27 -> 28 — and calls it
a defect, not cosmetic: "Repair before this file is used as a bed." Judgement ACCEPTED that. The
15:36:12 file stays on disk and is superseded, not deleted.

⚠️ **CORRECTED 2026-09-22 16:1x, after this review answered** (prior-art
`archive/peer/2026-09-22-priorart-c87b-rowd-clean.md` A3, ACCEPTED). Two sentences that stood here
are withdrawn:
* *"Every remaining address on this build is an INDEX TRIPLE into `Diagram #686`.`Nodes[]`, so a
  spare node on that diagram shifts addresses"* — **REFUTED by this build's own log**: the junk node
  is appended at the TAIL (`nodes_index 27` of 28, `build_d1_m3a3b_rowD.log:99`), `#637` still
  resolved at `Nodes[4]` with uid echo 637 at 28 nodes (`:137-138`), and `Diagram[19].Nodes[21]`
  echoed `23032 -> MATCH` at 27 nodes (`:22`). The purge is still right, for §5's *other* two
  reasons: an unwired-`reference` `Invoke` is a broken node that pins `ExecState` 0, and it is an
  object the original never had (rule 1a).
* *"The re-run produces a clean bed"* — **CONTRADICTED**: the bed ITSELF already carries one
  inherited unpurged second-pass `Invoke` (`Node` 634 cold -> 635 saved,
  `build_d1_m3a3_run2.log:33` vs `:187`/`:195`; `Diagram #686` 26 -> 27), because Row C's idempotent
  second pass skipped its purge at `build_d1_m3a3.py:1432`. `junk_purge` deletes only nodes new
  since the last `node_mark` (`stagekit.py:460-474`), so this run cannot remove it. D8 therefore
  claims only that **THIS RUN adds none**. For judgement: that inherited node may block M4's COLD
  `ExecState` 1 target from inside the bed.

## EDIT 1 — the junk purge runs TWICE
The first `junk_purge` stays exactly where it was (after the first connect). A SECOND
`s.junk_purge("rowD SECOND PASS", hints=[d_idx])` is added immediately after
`s.expect_is_broken_false("D5", connect, wire_uid=wire)`, because that ordered second pass issues a
real connect and the `OpConnect*` family is MEASURED to mint 1.00 stray `Invoke` per call
(`build_opfsinnertunnelconnect_v0.purge_junk`, the c82 measurement). A new gate **D8** asserts the
final `Node` census equals the BEFORE census — both values printed by `s.census(...)`.

## EDIT 2 — D7 becomes a SET DIFFERENCE, not a count
The old D7 compared `(total, wired)` tuples of `WhileLoop #637`'s 60-row terminal table before and
after; it failed `before (60, 48) after (60, 47)`. The c87 review's finding, accepted: the `total`
half is a constant that could not have moved, so relaxing D7 to the total-only form "makes D7 green
by construction on every future row". Its own remedy is to assert the PREDICTED SET DIFFERENCE.
D7 now keys BOTH tables on `(i, name, is_source, build_d1_m3a1.term_state(t))` and passes only when
the symmetric difference is exactly `{(10, 'Outgoing Handle', True, 'WIRED'), (10, 'Outgoing
Handle', True, 'BARE')}` with ZERO `UNREAD` rows on either side. t10 is the OLD source `#4334`'s
outer terminal detaching, which is Row D's purpose.

The review's own FREE offline discriminating test was run FIRST, on the 15:36:12 tables, and
returns exactly that: 2 elements in the symmetric difference, both t10, 0 UNREAD on each side,
WIRED 48 -> 47, BARE 12 -> 13.

## Everything else is unchanged
Same bed `claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e0b6b193a158c9221474c68e3`, opened
only as a COPY, md5-pinned at both ends, never opened for execution, never run. No Remove Bad Wires
anywhere (plan 111a). No new op, no new device, no motor, no ASI, no camera. The artefact is BROKEN
BY DESIGN (`ExecState` 0) and is saved through the user-approved broken-intermediate `gui_save`
route. The recipe is 116 lines on `tools/stagekit.py`.

## What I am asking
Has any of this already been done, measured, settled or refuted in this project's own files — in
particular: (a) has a second junk purge after the ordered second pass already been built or
measured somewhere; (b) does a set-difference terminal gate already exist in the fleet; (c) is
there an existing helper for keying terminal tables that I should be calling instead of writing the
two-line comprehension; (d) is re-running this stage on the same bed already settled one way or the
other anywhere?
