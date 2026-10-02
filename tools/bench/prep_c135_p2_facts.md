# Card 135-P2 — facts owed by PD293(f), OFFLINE (no LabVIEW, no VI opened)

Sources: existing records only. "ORIGINAL" below = `Min_Track N beads V6_ParallelLoop.vi` md5 `2a78e17c…` as dumped headless in
`tools/bench/main_vi_nodeterms.json` (the S1 source; = the true original + the 2026-09-01 fixture nodes #22700/#22703/#23020/#23175,
`docs/fixture-recording.md:15-20`, `docs/d1-build-plan.md:1024-1025`).

## 1. Where #2626 element|0 (<- #5119 x-y) and #11363 (#11608 side) lead in the ORIGINAL

| value | ORIGINAL wiring | ends in | cite |
|---|---|---|---|
| `#5119 x-y` (w16483) | sinks: `#2626` 'element' (i1) and `#22703` 'input 1' | **SAVED DATA** via `#2626` | `tools/bench/diag_c126_8_orig.log:6` |
| `#2626` 'appended array' (w4517) | -> `#376` save trace.vi 'current frame data array in' | per-frame record; save trace accumulates it into `total data array` and periodically calls `save N xyz traces.vi` | `diag_c126_8_orig.log:5,32,46`; `docs/d1-build-plan.md:503` |
| `#22703` Format Into String | TIFF file-name chain = FIXTURE node, not the true original | (removed from derived VIs) | `docs/fixture-recording.md:18`; memory rule "tiff writer is a fixture insertion" |
| `#11608` Bundle 'output cluster' (w12256) | -> `#11261` Build Array 'element' (only sink) | **DISPLAY only** | `diag_c126_8_orig.log:39-40`; `main_vi_nodeterms.json:12752-12759,12693-12697` |
| `#1359` For out-tunnel i6 (w11352) = the tunnel the bed calls `#11363` (fed by Bundler `#11310`, NOT by `#11608`) | -> `#11261` 'array' | **DISPLAY only** | `main_vi_nodeterms.json:12370-12374,12681-12685`; `docs/d1-loop12-17-split-plan.md:1403-1406` |
| `#11261` 'appended array' (w10908) | -> a front-panel indicator terminal = `#8323` 'Force (pN) vs Extension (nm)'; no path to the tra/file writer, a motor call or `#5058` | display | `main_vi_nodeterms.json:12669-12673`; `docs/frame-loop-wire-graph.md:205,469`; `docs/d1-loop12-17-split-plan.md:1404-1406,1610-1611` (96-3 / 99-1 measured on the bed) |

Notes (facts, no decision):
- The card's wording "#11363 (<- #11608)" (also `prep_c135_p4_sizing.md:13`) does not match the records: `#11363` and `#11608` are the
  two SEPARATE inputs of `#11261` ('array' / 'element'); both lead only to display.
- `docs/fixture-recording.md:18` says `#5119` "feeds 'Save trace'.`frame index`"; the ORIGINAL dump contradicts it: `#376` 'frame index'
  is w3268 (the `#637` iteration value, sinks `#2136 #3191 #10068 #1114 #29240`), and w16483 has only the two sinks above
  (`diag_c126_8_orig.log:6,34`). `#5119` x-y reaches saved data only as `#2626` element|0 (i1).
- `#5119` y <- `#250` 'LastBufferNumber' (w3363, `docs/frame-loop-wire-graph.md:269`).

## 2. Loop 1.2's stop `#10171 Equal?` (x,y on one wire)

- **Created by stage S2** (`tools/recipes/stage_d1_s2.py`, log `tools/bench/stage_d1_s2_loops.log:61-69`): loop b `#10170` (body `#23166`),
  `OpCreateEqual_v0` with BOTH operands from `#8486` 'x+1' (Increment on `#686`), `OpStopFromNode_v0` onto conditional terminal
  `#23246` (wire 23310 then). Same scaffold on `#23041` -> `#23042` (`:77-80`) and on `#23032` -> `#23035` (`:49-52`).
- Why it exists: the "scaffold" pattern that made an empty new While legal (`ExecState` 1) — `docs/cycle27-plan.md:956-972`
  (34(l), `diag_s2_scaffold.log`); operand picked by name from a measured scalar (archive/2026-09-20-status-cycle52-relocate.md:22, cited
  by name only). The intended real stop ("each new loop's conditional terminal driven by its own sentinel `Equal?`", built later from
  queues/QRT) is `tools/recipes/build_d1_routeb_v7.py:131-137`; plan row **STOP** ("1.2 / 1.7 conditional terminals driven by the stop
  design ... inputs from QRT") is `docs/d1-loop12-17-split-plan.md:76`. P0 confirmed both bodies held ONLY the scaffold
  (`docs/d1-loop12-17-split-plan.md:83-85`); `:1615` "S3 loop has NO stop local (x==x scaffold)".
- **ORIGINAL tracking-loop stop:** the original has no separate tracking loop; tracking runs inside the frame loop `#637`, whose
  conditional terminal `#648` is fed by wire 3457 from `CompoundArithmetic #11639` (OR of `stop (end)` uid 7 [w6929], w12070 <- node
  #12589 t2, w10249 <- `x = y?` #10019); w3457 also drives indicator `TurnOff`. `docs/main-vi-stop-and-save.md:41-49,55-72`;
  `tools/recipes/build_d1_routeb_v7.py:136-137`. `stop (end) 2` (#19587 -> #17883) is a separate path to a case, not this terminal.
- UNMEASURED: the conditional terminal's mode (Stop if True / Continue if True) of `#10170` is not read in any record found;
  "TRUE ⇒ one iteration" assumes Stop if True. Reader: a property read of the While's conditional-terminal mode on a byte copy.

## 3. UNMEASURED routes of the draft after PD293(c)-(e) — cheapest measurement each

Draft `plan_ring_p4_draft.json` d9d66246 has 6 UNMEASURED actions (`:215-240,553-561,704-718,739-747,758-766`). (c) removes none of
them (the dropped `n1 > -1` actions `p4_gt_n1`/`p4_k_m1`/wires are PRECEDENT/MEASURED). (e) removes U4. **5 remain**:

| # | action (draft line) | what is unmeasured | closest existing record | cheapest measurement |
|---|---|---|---|---|
| U1 | `p4_sel_mask` create Select from donor #529 (`:213-228`) | the CREATE route is measured (`census_samples.json:217-226`, `diag_c128_2_donors.log:62`); unmeasured = its later use with a Boolean ARRAY `s` | scalar s only (`scratch_verify/gscript.create_primitive_nested_errsel_c128_2_20261002_001722.json`) | one scratch VI covering U1+U2+U3 together (below) |
| U2 | `p4_k_max` const 2147483647 created ON `SW1.f` (`:229-241`) | created BEFORE `t` is wired (`p4_w_num_sel` at `:543-552` comes later), so the constant's type = Select's untyped default f; it is also branched to `LT1.y` (`:583-592`) | const_on_term value pattern = P3a `p3a_wait_k` (I32 1 on a typed terminal) | same scratch VI: read the created constant's class/value after create, and after t is wired |
| U3 | `p4_w_gt_sel` Greater?(array,scalar) out -> `SW1.s` (`:553-561`) | Boolean-array into Select.s legality | none | same scratch VI: Local `Num`-typed array (or an I32 array constant) -> Greater? x, I32 -> y, out -> Select s; array -> t; U2 const -> f; out -> Array Max & Min; read connect op's `Is Broken?` per wire + Error List + ExecState. ≤120-line stagekit diagnostic, existing ops only |
| U5 | `p4_x_slot_fs` TS1.outer (already wired to IAI.index) -> IAN.index in FS4.f0 (`:739-747`) | source = a LoopTunnel OUTER face of a plan-made While; sink in a plan-made FS frame | node-terminal sources: `case_frame_to_fs_frame_branch` (`census_samples.json:500-516`, `diag_c126_4_fs.log:57`: second sink makes a NEW FS outer tunnel, source wire re-created); `loop_body_wired_src_to_fs_frame_in_case` (`:517-541`); face sources: `fs_inner_face_branch` (`:568-579`), `register_end_case_border` (`:408-440`) | scratch byte copy: While + output tunnel + FS on the parent body, connect_term_uid(IAN.index, TS1 outer face) then RLE; census + Is Broken? |
| U6 | `p4_x_n2_out` IAN.element in FS4.f0 -> EQ2.y on `#23166` (`:758-766`) | single-hop FS frame -> enclosing diagram EXIT on a plan-made FS | an FS EXIT hop WAS made by connect_term_uid in 126-6 B3: tunnel `#28302` on FS `#12938`, inner face on frame 13236 (sink), outer face on `#536` (source) — part of a multi-border crossing out of an existing FS, Is Broken? False (`diag_c126_6_cross.log:68,77-78`; `census_samples.json:542-566`) | existing record = PRECEDENT for the exit; a single-hop plan-made-FS exit needs the same scratch as U5 (add EQ2 on the body, connect_term_uid(EQ2.y, IAN.element), RLE) |
| (U4) | `p4_x_xyz_fs` ordering-only FS input (`:704-718`) | — | — | REMOVED by PD293(e) |

Routes NOT in the draft that (d)/(e) add (unclassified, no route level yet):
- (d) W1's stop exit: a Local read of the program's stop control inside `new:W1.body` + an OR into W1's conditional terminal (draft
  wires `LT1` straight to `W1.cond`, `:593-602`). No Or donor is named in the draft's create list (`:72-86`).
- (e) "an error or image-out wire of the last tracking node into the second `Num` read's path": `#5058` has NO error in/out and NO
  Image Out (outputs: `Bead is good? array out`, `x,y,z array out`, `pos in cal image out`) — `docs/d1-loop12-17-split-plan.md:2235`.
  The second read `LRN5` is a Local (no input terminal) and `IAN`'s two inputs are both used in the draft (`:729-747`), so the frame
  holding n2 has no free sink for an ordering wire as drafted. Which node is "last" and what carries the dependency is undecided.

## 4. Not readable offline (UNMEASURED, with the reader)
- Select with Boolean-array s / constant type on untyped f (U1-U3): scratch VI above.
- Plan-made While outer face -> plan-made FS frame, and plan-made FS frame -> parent exit (U5, U6): scratch byte copy above.
- `#10170` conditional-terminal mode: property read on a byte copy.
- Data types of `#2626` / `#11261` inputs: no `Terminal.Data Type` reader exists (`docs/d1-loop12-17-split-plan.md:1922`).
