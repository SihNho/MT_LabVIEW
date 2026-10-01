# Brief 131-1 — measure the Flat Sequence tunnel-naming rule (offline), PD270(b)

Decision in force: `docs/d1/tooling.md:39-55` (PD270). Read it; it is the whole reason for this card.

## Part A — the crossing table (measurement, no code change)
One row per tunnel-creating crossing ever RUN in LabVIEW and recorded on disk. At least:
- B1, A_bn (the cases PD265(a) was built from: `cross.log` / `fs.log`, see `docs/d1-loop12-17-split-plan.md:2916` only);
- 129-4 scratch pin2 op 33 (`current image number`) and every row of that run that came out `''`;
- 130-6 scratch pin3 ops 1–26 (`tools/bench/stage_d1_ring_p3b1_scratch_pin3.log`; op 26 = `Image Out`, `:370`).
Columns: run/op · source node class + uid · source TERMINAL name (label/caption as LabVIEW reports it) · existing tunnel
names already on the source net at that moment · border kind (FS outer, case, loop, multi-border) · resulting tunnel name.
Every cell cites `file:line` (log or graph read). A value not on disk is written `unknown` — never inferred.
Write it as `tools/bench/fs_tunnel_naming_table.json` (+ a short .md render).

## Part B — the rule
Rewrite `tools/stagesim.py`'s naming of a crossing-created tunnel so it explains EVERY row; the self-test is the table
itself (`tools/bench/selftest_stagesim_tunnel_naming.py`, one case per row, all pass). Existing stagesim self-tests stay
green. If no single rule explains every row: STOP at that point, return the table and the rows that conflict (status
FAIL, OPEN line) — do not invent a name-insensitive binder; that is judgement's call.

## Part C — only if B passes
Re-simulate and re-finalize P3b-1 and P3b-2 (split end graph == unsplit 70 reference, PD268(c)/PD269(a));
P3b-1 recipe + scratch helper `--dry` (31/31) and `--prerun` PASS; X10 peak printed; `--scratch-required` exit code.
New plan/pred md5s in the result. Rerun `tools/bench/c125_1_offline_measure.py` if stagexec.py or stagekit.py changed.

## Rules
Offline only (labview none). Do not edit `tools/stage_prerun.py`, `tools/hooks/*` (card 131-2 is live on those).
Return at the first unexpected result. result/1 in `tools/bench/cards/result_131-1.json`.
