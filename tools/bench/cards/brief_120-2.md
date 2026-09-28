# brief 120-2 — FS-crossing measurement + terminal data-type reader (PD237(k))

Two independent parts. Scratch VIs only; the bed is only ever byte-copied. PD237(j)/(k) in
`docs/d1-loop12-17-split-plan.md` give the why.

## Part F — FS crossing (MEASURE ONLY; the route choice is judgement's)
Facts: the pool's Obtains sit on FS2 frame `13236` (frame 2 of 10); loops 1.1/1.2 sit on `686` = FS1 frame 9 of 10;
path `13236 → 8 FSIT → FS2 outer → #536 → FS1 outer → 8 FSIT → loop tunnel` (`tools/bench/facts_c120_qrtw.json:303-352,749-834`).
No measured route creates FS tunnels (`tools/bench/opmodels/connect_from_wire.json:14-31` made a LoopTunnel only).

- **F1** Build a ≤ 120-line stagekit scratch VI with the same NESTING (source node in frame 2 of flat sequence A; sink
  inside a While loop in frame 9 of flat sequence B; both sequences in one frame of an outer structure like `#536`;
  frame counts may be smaller if the pattern is kept: source frame not the last, sink frame not the first).
- **F2** Wire source → sink with the EXISTING connect route (`stagexec.connect_route` / the ops it uses; no new op).
  Record: the call's error, which tunnel objects appeared (class, uid, owner), the chain read back from the graph
  (every hop), `Wire.Is Broken?` on each segment, and whether the source and sink ends are the requested terminals.
- **F3** If F2 fails, record the error and stop Part F. Do NOT try alternatives (named obtain, manual tunnel creation):
  that choice is judgement's.
- **F4** Write the record under `tools/bench/scratch_verify/` (PASS or FAIL with the facts) and add the observed
  behaviour as samples to a new `tools/bench/opmodels/connect_across_fs.json` (same format as `connect_from_wire.json`).

## Part T — terminal data-type reader (a TOOL, 2026-09-24 tools rule)
- **T1** A read-only op VI in `claudeDev` (name `OpTermDataType_v0.vi`, no "Op" name for anything that is not an op)
  that returns a terminal's data type as a comparable value (flattened type descriptor string, or the type's class +
  representation + for clusters the element list). `NAMES.md:470-484` names the property-id lead given by 120-1.
- **T2** Hygiene: 20 calls with handles flat ±100, and a record under `tools/bench/op_hygiene/` so `gscript.op()` admits it
  (`gscript.py:299`). A gscript wrapper `read_term_type(target, term_uid)`.
- **T3** Measure on a byte copy of the bed: the six field source terminals (`#30117` Value, `#4580` Value, `#637` i t644,
  `#5119` x-y t6323, `#11608` output cluster t11614, `#2626` appended array t2813) and the pool's Obtain `#23105`
  element type input; plus two known controls (an I32 and a DBL terminal of your choice with the type cited) to show
  the reader distinguishes them. Types into `tools/bench/facts_c120_types.json`.
