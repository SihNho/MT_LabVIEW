ATTACK this claim about the failed stage run `tools/bench/fgate_97_stage.log` (recipe `tools/recipes/stage_d1_fgate.py`, card 97-5).

CLAIM: the run's F5a / F5c / F6a failures (Invoke count 1 -> 2; cdiff "added" lists an extra `(10261, 'Invoke')`; ExecState 0 warm, so nothing was saved) have ONE cause: `s.connect_from_wire(...)` (recipe line ~61) is not wrapped by the recipe's `op()` helper, so no `junk_purge` runs after it, and the stray Invoke node that the OpConnect* family mints on every call (stagekit.py `junk_purge` docstring: "1.00 stray Invoke per call") stays on Diagram #639 with its `reference` input unwired, which breaks the VI. The fix is one call, `s.junk_purge("connect_from_wire")`, after that gate; everything else in the build is correct.

Evidence in the log:
- `connect_from_wire node census: 628 rows` (log:207) and `wire_control node census: 629 rows` (log:210): +1 node between them and no purge line; every other connect op in the run prints a `CENSUS DIFF ... Invoke` and a `purge delete` line (log:220-268).
- `CENSUS before ... 'Invoke': 1 ... after ... 'Invoke': 2` (log:378); `CDIFF rows 0; added [(10261, 'Invoke'), (10280, 'Function'), (22968, 'Function'), (23136, 'ControlTerminal')]`.
- F3b/F3c/F3d/F4 A/F4 B (edge tables equal, 16 and 3 edges)/F4c/F4d all PASS; only F5a, F5c, F6a fail.
- uid 10261 was earlier an IndexArray (deleted) and then a purged junk Invoke (log:189-199); LabVIEW reuses uids.

Already ruled out: memory (peak 622 MB < MEMSTOP 700, no error 2); the donor unload (it failed with LabVIEW 0x47D and changed nothing, and it touches only the donor file).

Questions: what else could make ExecState 0 here (e.g. the Case B ' False ' frame leaving #8323's BuildArray input/outputs unwired, a case-A output tunnel, the non-indexed #1359 input tunnel, the moved `Exp Baseline` terminal #8476, the Q&R/Eq0 types with an I32 control vs `i`)? What cheap read in the next run would tell the junk-Invoke cause apart from those, BEFORE the save gate?
