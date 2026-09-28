# Card 117-2: QRT facts per open pair at L2-R1's end (offline, structural; no LabVIEW)

Data: `tools/bench/facts_c117_qrt.json`. Measured by `tools/bench/diag_c117b_qrt.py` → `diag_c117b_qrt.log` (15/0,
rc=0) + `diag_c117b_qrt.json` on `graph_l2r1_saved_20260928.json` (md5 `e429f7ad`) vs S1 (`D1_s1_copy`).

**Q1:** cdiff(S1, R1 saved) = 16 sink keys == `plan_l2r1.json:191-208`, 11 (node, term) pairs (`log:10-12`). The 16/11
count is not in `facts_c114e_inventory.json`. It is in `plan_l2b3.json:179-196` and `result_114-2.json:18`. Of the 11
pairs, 9 are loop-to-loop. `(2626,'array')` is a naming artefact: S1's x,y,z edge (t4168) is WIRED in R1, keyed
`array|3`, w25283, same loop (`diag_c117b_qrt.json:399-446`). `(11261,'array')` is a 1.2→1.2 plain wire (b2_03).

| pair | S1 wire | source (loop now) | sink loop | consumer | proposal (judgement decides) |
|---|---|---|---|---|---|
| #376 `current frame data array in` t5754 | w4517 | #2626 `appended array` (1.2) | 1.7 | file writer | queue (saved row) |
| #376 `frame index` t5763 | w3268 | #644 = #637 `i` (1.1) | 1.7 | file writer | queue (saved column, paired with row 1) |
| #2626 `array` ×4 | w505 | #5058 `x,y,z array out` (1.2) | 1.2 | writer | none: edge present, rename artefact |
| #2626 `element` ×3 | w16483 / w30592 / w4878 | #5119 `x-y`, #30117 `Trans Pos (mm)`, #4580 `Rot pos (deg)` (1.1) | 1.2 | writer | queue (saved columns) |
| #5058 `Image In` t5089 | w3040 | #6810 `Image Out` (1.1) | 1.2 | kernel | queue (Q_work, d1-build-plan.md:572) |
| #8634 `index (col)` t9196 | w10187→#10177→w10166 | #10068 Q&R remainder (1.1) | 1.2 | display #8323 | queue or recompute in 1.2 |
| #11261 `array` t11270 | w11352 | #11310 Bundle via #11363 (1.2) | 1.2 | display #8323 | none: plain wire (b2_03) |
| #11261 `element` t11273 | w12256 | #11608 Bundle (1.1) | 1.2 | display #8323 | local admissible (display only) |
| #28083 `Magnet position` t28095 | w30592→#9503→w28684 | #30117 Property Value (1.1) | 1.2 | display #8323 | local / same queue element as #2626 |
| #29625 `index (col)` t29643 | w29787→#29777→w29766 | #29240 Q&R remainder (1.1) | 1.2 | display #28786 | queue or recompute in 1.2 |
| #29973 `element` t29989 | same w29766 | #29240 (1.1) | 1.2 | display #28786 | one carrier with #29625 |

**Q3 (measured):** No data type is recorded. The graph rows have no type field (`log:5,9`). The only typed item is the
design table's IMAQ refnum for Image In (`d1-build-plan.md:572`). Every 1.1 source sits directly on body 639 with no
case frame, so it runs on every #637 iteration (`log:14-34`). #637 is the frame loop (`d1-build-plan.md:594`). The sinks
that use every value are #376 (the file writer) and #2626, which feeds #376 only (`diag_c117b_qrt.json:460,690,1118`).
#8634, #11261, #28083, #29625 and #29973 feed only the two indicators #8323 and #28786 (`facts_c108c_groupB.md:15-17`).
PD210 (split plan `:1572-1576`) lets #8323 show the latest value.

**Q4:** PD175 `:431-434` (t5/t7). PD177(e) `:508-509` (Image In). PD177(f) `:510-512`: w3040 also fed the deleted TIFF
writer. 227(d) `:1999-2001` (b2_03 with t11273). D5 `brief_110-1.md:13-15` and `plan_l2r1.json:117-171` (each row's
`why`). R8 `d1-route-b-plan.md:360-366` (#10068/#29240). `cycle27-plan.md:930-933` says a resolution table is owed and
names no queue. Of §9's eight queues, only Q_work and Q_res/Q_good/Q_rmeta reach these pairs (`d1-build-plan.md:570-579`).

**OPEN:** (1) #10068/#29240 are frame-counter remainders that index the same frame's data. CLAUDE.md 1c'' lists counters
as local-carried. Which carrier do they get: a queue, a local, or a recompute in 1.2 (R8)? (2) #30117/#4580 are panel
Property reads that feed the saved row. Should the value read in 1.1 be carried, or re-read in 1.2? A re-read changes
the sampling time (rule 1a). (3) #376's two inputs start in different loops (1.2 and 1.1). How is the pairing kept?
