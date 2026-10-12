---
type: facts
status: current
date: 2026-10-12
card: 167-a1-1
---
# Card 167-a1-1 - P6-0 (d): ONE Remove Bad Wires on a scratch byte copy of 75773b0d (facts only, nothing adopted)

Log `tools/bench/diag_c167_a1_1_rbw.log` (L), RESULT PASS 18/0 (L:380-382), BGRUN END rc=0 after 206 s (L:384).
- Hashes before: 13 card inputs + 7 VIs (75773b0d 7f2582ae eb1d0f31 94ffff94 f9ae7751 564d8cbe 6dcd5c3d) equal - `diag_c167_a1_1_hash_before.log` 8/0; after: same 8/0 - `diag_c167_a1_1_hash_after.log`.
- `protocol.py requires` PASS 2/0 (`tools/bench/cards/requires_167-a1-1.json`).
- Verb: `gscript.remove_bad_wires_scripted` (VI method 410) through `stagekit.Stage.broken_wire_count(allow_mutation=True)` inside `Stage._op` (op label `rbw_method410`, L:30-31). The GUI-menu `gscript.remove_bad_wires` was NOT used.
- Scratch: `claudeDev\scratch_c167_a1_1_rbw_20261012_191349.vi`, byte-identical to the bed (K3, L:21); never saved; deleted (H4, L:367); files left on disk [] (H6, L:375-376).
- ExecState BEFORE RBW: 0 (L:27). ExecState AFTER RBW: 0 (L:33).
- Wire objects: 2091 -> 2066 = 25 removed (L:30).
- Deleted wires (`tools/bench/p6_rbw_deleted.json` counts): 25 = 22 termless + 2 source-only + 1 src+sink; data-carrying 1, not data-carrying 24; new wire uids 0.
- The 22 termless F1 uids: 22 deleted, 0 kept (p6_rbw_deleted.json `termless22`; W22 gate L:319; diff P1 gate `diag_c167_a1_1_diff.log`).
- Source-only deleted: 10103 (#10114 LoopTunnel t10116 '# FD points'), 12256 (#11608 Bundler t11614 'output cluster') (p6_rbw_deleted.md:25,31).
- Data-carrying deleted: 25618 = #11261 BuildArray t11267 'appended array' (source) -> #23166 Diagram t8323 'Force (pN) vs Extension (nm) ' (sink) (p6_rbw_deleted.md:35).
- Error List of the RBW'd copy, read in the LIVE session (no save needed: lv_errorlist reads the in-memory VI): 1 item, window N 1 (L:342,350).
  - item 0: "Build Array 'Build Array': Contains unwired or bad terminal" | "One or more required inputs to this function are not wired or are wired incorrectly..." (L:345,351). uid unread (errorlist uid_route: none).
  - per-class (errorlist_check.class_counts): {'buildarraybuildarraycontainsunwiredorbadterminal': 1}.
  - file `tools/bench/errorlist_D1_ring_p6rbw_20261012_191349.json` md5 507ed14d2f3cc6d73f9bdf6bc310e944 (+ `_raw.json` e33b689cd47080d661a571511f6bc9c6).
  - before RBW: 47 items {unwiredinput 1, twotypes 1, looseends 23, notconnected 22} (p6_facts.md:14).
- Graph after: `tools/bench/graph_ring_p6rbw_20261012_191349.json` md5 c55317089900b64f83f863fc381ed73c: 6224 rows, 10834 objs, 2066 Wire objs, 25 loops, 23 FS (L:322); G1, FS1 PASS (L:320-321).
- e5_check line (L:318): `E5 stagekit.e5_check(edits={deleted_wires: 22 termless F1}, after, base 7815af09): ok True deleted_wires_present [] deleted_nodes_present [] uid_reused 0 rule identity (class, owner class, owner uid, pos)`.
  - NOTE: e5_check judges wire presence by terminal rows only (stagekit.py:3167), so it cannot see a termless wire; the Wire-object gate W22 (L:319) is the check that does.
- MEM (private): after_load 599.0, after_rbw 599.3, after_graph_read 610.5, after_errorlist 585.0; PEAK 610.5 <= 675 (L:24,36,316,355,358-359). X10 model prediction was 677.5 (stage_prerun --prerun).
- Hygiene: refs opened 8 / closed 8 / live 0 (H5, L:364-365); handles 45642 -> 43091 during work, 33969 at exit (L:357,377); input md5 unchanged (H2, L:368); pins hold (H3, L:374); LabVIEW gone at exit (L:383) and `tasklist` shows none; no original opened (K2 hashes it only, L:14).
- close_panel at hygiene raised 0x47D "front panel already closed" (L:363) - non-gating; ref counter balanced.
- Shared code: graph-read calls extracted once into `tools/bench/prep_c167_a1_1_graphlib.py` (self-test 2/0, `prep_c167_a1_1_graphlib_selftest.log`); the 15 inline copies diag_c141_3..diag_c165_a3_4 _graph.py left as record.
- Gate false positive logged: fp-98 (stage_prerun X5 counts any op verb containing 'wire' as a wire-making op, so an RBW op label failed X5).
- Launch-gate adaptation: A0 (ExecState before) and R1 (wire count drop) are ROWS, not gates, because the dry run can only stub them (L:28,35).
