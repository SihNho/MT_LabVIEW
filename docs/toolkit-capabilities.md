---
type: reference
status: current
date: 2026-09-18
tags: [docs, vi-scripting]
---

# What the op fleet can actually do

> Written 2026-09-13 after two capability assumptions failed in one session — erdosmiller's `Create SubVI.vi` turned
> out not to be an extractor, and `Control.Value` would not attach to a scripted Property node. Both were assumed from
> a *name in a list*. This file exists so plans are built on what has been **exercised**, not on what is catalogued.
>
> **The distinction this file enforces:** an entry in `docs/vi-server-ids.json`, or a VI in `vi.lib`, is a *candidate*.
> Only use counts as evidence.

## Array-returning READERS built 2026-09-14 — the cast-free fleet (all functionally verified)

| Python API (`tools/gscript.py`) | op VI | one run returns | verified by | cost on the main VI |
|---|---|---|---|---|
| `subvis(target, diagram)` | `OpSubVIs_v1` | every subVI call on ONE diagram: `[{uid, name, path}]` (`AbstractDiagram.SubVIs[]` → `SubVI.VI Name/VI Path/UID`) | `tools/bench/test_opsubvis_v1.log` 14/14; sweep `main_vi_subvis.json` 98 sites, 0 mismatches | ~1.2 s |
| `panel_wiring(target)` | `OpPanelWiring_v0` | every top-level panel object: label, indicator flag, control UID, terminal `Is Source?`, connected-wire UID (0 = bare) + error columns | `test_oppanelwiring.log` 11/11 (constructed orphan = exactly +1) | ~0.8 s |
| `node_terms(target, diagram, node)` / `node_terms_uid` | `OpNodeTerms_v0` | every terminal of ONE node: name, `Is Source?`, wire UID + per-property error columns, and the node's own UID | `test_opnodeterms.log` all PASS (exact per-index tuples vs the walker; direction on primitives and on NI's example globals) | ~0.8 s/node (walker: ~8 s/node) |
| **`node_terms_uids(target, diagram, node)`** → `(node_uid, rows)` (card 112-2 D2, 2026-09-27) | `OpNodeTermsUid_v0` (md5 `fc21b17a…`; byte copy of `OpNodeTerms_v0` + ONE `GObject.UID` 632A813 property node on PN_C's `reference out` inside the For loop → auto-indexed `Array 8` = TermUID, `Array 9` = its error; labels `tools/bench/diag_c112b_opnodetermsuid_labels.json`) | `node_terms` rows PLUS each `Terminals[]` entry's OWN terminal uid — the reader behind `stagexec.Addr._by_uid` (a BARE face on an owner's `Terminals[]` is found by uid echo, never by name/position). Measured: a ForLoop's `Terminals[]` list its LoopTunnels' OUTER faces (8/8 by uid on `OpNodeTerms_v0`'s loop #142) | `tools/bench/diag_c112b_opuid.log` 14/0: 83/83 entries on every node of the donor match `OpAllTerms_v1` (direction + wire) and the old columns == `OpNodeTerms_v0`; 20 calls handles 31191 → 31191 | ~0.8 s/node |
| `tunnels(target, index)` | `OpTunnels_v0` | the index-th `LoopTunnel`: tunnel UID, IndexMode, outer terminal (name / source? / wire), inner terminals as arrays | `test_optunnels.log` all PASS; 132 tunnels censused | ~1.3 s |
| `connect_ctl(target, panel_i, node_i, term_i)` (WRITER) | `OpConnectCtl_v0` | wires Nodes[node_i].Terminals[term_i] into the terminal of Panel.Controls[panel_i] (Terminal.Connect Wire on the control's own terminal) — works on a Vision IMAQ Image Display, which erdosmiller's Wire Indicators cannot see | `build_harness_dispI.log` run 4: wire created, existing branch kept, ExecState 1 | 8 s (open target) |
| `node_labels(target, diagram)` | `OpNodeLabels_v0` | the label text of every node on one diagram (`Diagram.Nodes[]` → loop → `Node.Label` 6359001 → `Text.Text`) + UID: implicit property node → its bound panel object's name; subVI → file name; primitive → type name. Cast-free identity that `net_map` never had | `test_opnodelabels.log` 7/7: 88/88 implicit `Value` nodes of the main VI labelled with a panel label, handles flat | ~1.0 s/diagram on the main VI |
| `loop_cast(target, index, class_name='ForLoop'|'WhileLoop')` (+ `parallel_enabled`, `static_instances` for For loops via `OpLoopCast_v1`) | `OpLoopCast_v1` / `OpWhileCast_v0` | a TYPED look at the index-th loop: loop UID, the N wire's UID (For loops), `Loop.Shift Registers[]` element UIDs. **The first cast-free TYPED cast**: the TMSC's target class is a refnum CONTROL of that class (seed section below) | `test_oploopcast.log` 13/13: N wire 346 on HARNESS_copyloop, 17/17 For loops and 3/3 While loops of the main VI, frame loop = 14 shift registers, handles flat | ~1.0 s/loop on the main VI |
| `shift_reg(target, loop_i, reg_i, 'WhileLoop')` | `OpShiftRegs_v0` | the reg_i-th element of `Loop.Shift Registers[]` (= the RIGHT register): class name, outside terminal (final value: name / source? / wire), inside terminals (body feed) | `test_opshiftregs.log`: 14/14 registers of the frame loop, no errors, handles flat | ~1 s/register |
| `shift_reg_left(target, loop_i, reg_i, left_i, 'WhileLoop')` | `OpShiftRegs_v1` | v0 + `RightShiftRegister.Left Registers[]`: every left's UID, and the left_i-th left's class, outside terminal (initial value; wire 0 = uninitialised) and inside terminal (the body's source) | `test_opshiftregs_v1.log` 8/8: 14 lefts, all `LeftShiftRegister`, 13 initialised | ~1 s/register |
| `while_loop(target, location, tunnels=[labels], indexing=[...])` (WRITER) | `OpWhileLoop_v0` | a While loop on the top-level diagram with input tunnels from EXISTING controls by name (the creator's `Inputs` fed from `Get Controls`, which OpForLoop_v0 lacked). Conditional terminal left unwired → wire a stop via the next op | `test_opwhileloop.log` 5/5 | 0.06 s |
| `exit_while(target, stop_control, body_diagram, node_index, output_names, node_class)` (WRITER) | `OpExitWhile_v0` | wires a While loop's conditional terminal from the Boolean control named `stop_control` (Get Controls → Index Array → Exit While Loop `Stop Condition`) and creates output tunnels for named outputs of a node inside the body | `test_opexitwhile.log` 5/5: ExecState 0 → 1, the VI runs and stops | 0.04 s |
| `queue_node(kind, target, src_cls, src_i, src_name, diagram, location)` kind ∈ obtain/enqueue/dequeue/release (WRITER) | `OpQueueObtain/Enqueue/Dequeue/Release_v0` | places one queue primitive on any diagram, its refnum input taken from a named OUTPUT terminal of an existing node (Obtain: the terminal whose type the queue takes); the element of an Enqueue is wired afterwards with `wire(…,'element')`; timeouts via `create_control` on the created node | `test_opqueue.log` 7/7: typed queue, enqueue inside a loop through auto tunnels, element 1280 dequeued in a 0.09 s run | ~0.2 s/node |
| `EMPTY_v0.vi` (an empty runnable top-level VI; copy it to start a new VI) | recipe `build_empty_vi.py` | HARNESS_copy0 stripped of subVIs, controls, constants by class deletion; ExecState 1, runs | `build_empty_vi.log` | — |
| `loop_in('for'|'while', target, diagram, location, src_cls, src_i, [names], [indexing], parallel)` (WRITER) | `OpForLoopIn_v0` / `OpWhileLoopIn_v0` | a loop on ANY diagram (Traverse index), input tunnels from a node's named outputs, static parallel instances — the nesting the stage-2 kernel loop needs | `test_oploopin.log` 6/6 (nested For and While; a control wired through two borders → one tunnel per border). ⚠️ PRECONDITION (2026-09-26, `archive/peer/2026-09-26-c97-loopin1055.md`): an object must exist at `Traverse(src_cls)[src_index]` (default `SubVI`[0]); on a VI with no SubVI both recorded calls raised `1055 To More Specific Class` (`build_opstopfromnode_v0.log:51-53`, `diag_c97_tools_t124b.log:14`). Which of the op's two casts raised is UNMEASURED (review Arm A) | 0.1 s |
| **wiring a For loop's N by script** = `connect_terminals(target, loop_node, 0, src_node, src_term)` | existing `OpConnect` route | an EMPTY For loop's `Node.Terminals[]` has exactly one entry (unnamed sink) = the count tunnel's outside terminal; an I32 source wired onto it makes the loop runnable. Verify by the same wire uid on both terminals (`node_terms`) + ExecState 1. `Create For Loop`'s Control Names does NOT wire an existing control (measured) | `build_harness_copyloop2.log` run 2 (wire 346 on both ends, ExecState 0→1); functional in `run_copyloop_bench.log` | 0.1 s |
| **`replace_object(target, uid, new_path)`** (WRITER, callee swap; card 75-4, 2026-09-25) | `OpReplaceGObj_v0` (md5 `a3723240…`; donor OpOwnerChain_v1 + Invoke `GObject.Replace` 632A402 (Path) → `GObject.UID` 632A813 → Close Reference on the returned ref; built by `tools/bench/diag_swap_build.py`, labels `tools/bench/swap_verb_75_oplabels.json`) | swaps the VI a subVI node calls, IN PLACE. MEASURED on a scratch of `D1_s1_copy.vi`, #6810 → byte copy under a new name: **node uid CHANGES** (6810 → 23006; returned as `new_uid`), every wire kept (name-keyed edge diff with the node remapped = ∅; raw term uids 16 renewed), callee census diff = that node only, ExecState 1. `computation_diff(S1, swapped)` = **9 rows**, all from the uid change (cdiff keys nodes by uid, `tools/vigraph.py:205`). `SubVI.Replace` 635E001 NOT needed/not tried | `tools/bench/swap_verb_75.log` 13/0; build `swap_verb_75_build.log` 8/0 (cold ExecState 1) ; 20 back-and-forth swaps clean, handles range 38 | ~1 s |
| **`connect_ctl_ind(target, sink_panel_index, src_panel_index)`** (WRITER, control → indicator; card 76-4, 2026-09-25) | `OpConnectCtlInd_v0` (md5 `e59d103f…`) = `OpConnectCtl_v0` with its `Nodes[]→Terms[]` source ladder DELETED and replaced by a second `Panel.Controls[]` → Index Array (`index 5`) → `Control.Terminal` 6332006 feeding `Wire Source`; sink index = `index`; error = `error out 2`; **3 Close Reference** (sink Terminal, source Terminal after the invoke's error, vi reference). Labels `tools/bench/replay_vis_76_ctlind_labels.json`; built by `tools/bench/diag_replay_skeleton.py` | wires a front-panel CONTROL's terminal straight into an INDICATOR's terminal on the top-level diagram — the pass-through (Session/error/Buffer Number In→Out) no earlier verb could make | `tools/bench/replay_vis_76c_skeleton.log` 16/0: ES 1 COLD; on a scratch Session/error/BN In→Out same wire uid both ends, ES 1; 20 delete+reconnect calls, handles 31,113–31,119 | ~0.1 s |
| **`wire_const(target, src_cls, src_i, dst_cls, dst_i, dst_term_index)`** (WRITER, bare diagram-CONSTANT source; card 85-1, 2026-09-25, Pre-decided 188(c)) | `claudeDev\ops\OpConstWire_v1.vi` (md5 `c978863c…`) = `OpWire_v1` with Get Outputs #216 / Wire Inputs #262 deleted: SOURCE Traverse(`Class Name`)[`index`] → TMSC #683 retargeted by a Constant-typed seed (`reference`) → `Constant.Terminal` 634AC04 → `Wire Source`; SINK Traverse(`Class Name 2`)[`index 2`] → TMSC #788 (Node) → `Node.Terminals[]` 6359000 → Index Array[`index 3`] → `Terminal.Connect Wire` 6349C03; error = `error out 2`. Labels `tools/bench/constsrc_l2a1_85_opcw_labels.json`; recipe `tools/recipes/build_opconstwire_v1.py`; stagexec route `'const'` | wires a constant that is NOT in `Diagram.Nodes[]` (reached by its class traverse) into a node's sink terminal by Terminals[] index. A non-Constant source is refused by the cast (1057), nothing wired | `tools/bench/constsrc_l2a1_85_build.log` 31/0: separator 5001 (source cast was the 82-3 1057), ES 1 cold, 20 negative calls 1057 / Wire+Invoke unchanged / handles 42,413→42,445; functional at op 35/36: `tools/bench/constsrc_l2a1_85.log` | ~0.1 s |
| **Unowned IMAQdx-Get-Image pane base** `claudeDev\replay\replay_imaqdx_pane_base.vi` (md5 `65e999d9…`) | `EMPTY_v0` copy (12 free slots) + `drop_subvi(IMAQdx Get Image.vi)` + `create_control`/`create_indicator` on each of its 9 terminals + delete the node + `ConnectorPane.Assign` per slot | a VI with IMAQdx Get Image.vi's connector pane and NO library owner (VI.Name `replay_imaqdx_pane_base.vi`) — the byte-copy route keeps the lvlib claim (`replay_vis_76_measure.log:33,38`) | same log: per-slot label+direction == vi.lib; ES 1 COLD; `replace_object` of get-buff `#529` by it keeps all 9 terminal wires and ES 1 | — |

### 2026-09-17 — `tools/motor_census.py`, the motion CALL-SITE reader (composed of ops, not a new op)

| what | fact |
|---|---|
| what it answers | every motion call site reachable from a given VI: owning VI · diagram index · owning structure class + uid · callee name/path · call-site uid · which rule matched · PI/ASI/rotor |
| the PRIMARY rule | **reachability to a serial WRITE**, measured. The name list (`MOV/VEL/GOH/Move Axis to Position/SetCommand*`) is a CROSS-CHECK only; a reachable VI that is not on it is reported `UNCLASSIFIED`, a name-list VI that is not reachable is `NAME_ONLY` |
| how a VISA Write is identified | **by its LABEL, never by class.** The node's VI Scripting class is the generic `Function` (`tools/bench/visa_class_probe.log:14`), so `report_all(vi,'Function')` cannot single it out; `node_labels()` reads `\|VISA Write\|` (`visa_class_probe.log:23-40`, 5 of them in `SetCommand.vi`) |
| ⛔ the offline route is REFUTED | a `.vi`'s raw bytes **and every zlib blob in it** contain no "VISA Write" string, not even in `SetCommand.vi` which holds five. Only the VISA *terminal* names survive. Do not try a byte-scan again |
| ⛔ `VI.Callees` is the WRONG call-graph source here | it exists and returns, but returns **NAMES** (plus `.ctl` typedefs), and `GetVIReference` on a bare name does not resolve → `count(Diagram)` dies with error 1445/7. It broke run 1 of the census (72 of 126 VIs errored). Use `subvis(vi, d)` per diagram, which returns the real `VI Path` |
| structure path | the nearest-structure match of `tools/bench/build_diagram_hierarchy.py` (body diagram at `struct_pos + (10,22)`, runner-up ≥ 3× farther) reused unchanged |
| it is a READER | opens VIs by reference, traverses, changes nothing; lives in `tools/`, not `tools/recipes/`, so `guard_cycle.BUILD_RE` does not gate it |

### Overnight 2026-09-14/15 additions (INDEX rows 37–39; all functionally verified)

| Python API | op | what it does | evidence |
|---|---|---|---|
| `add_shift_reg(target, loop_i, y, 'WhileLoop'|'ForLoop')` | `OpAddShiftReg_v0` / `OpAddShiftRegF_v0` | CREATES a shift register (`Loop.Add Shift Register` 6361000, public) on the typed seed of either loop class; both sides come back unwired | rows 37, 39 |
| `wire_sr(variant, target, loop_i, reg_i, node_index, term_index / ctl_index, class_name)` | `OpWireSR_*` / `OpWireSRF_*` (`LeftIn`, `RightIn`, `LeftOutNode`, `LeftOutCtl`) | wires ONE side of a register with `Terminal.Connect Wire` on the sink: body node via `Loop.Diagram→Nodes[]→Terminals[]`, top-level node via `VI.Block Diagram`, control via `Panel.Controls[]` — indices, never names | row 38 (While: ExecState 0→1, runs), row 39 (For: 1024 iterations) |
| `for_loop(target, loc, tunnels=[labels], indexing=[...])` | `OpForLoop_v1` | For loop with input tunnels from EXISTING controls, auto-indexed when asked (an ARRAY control; a scalar silently stays regular); an indexed input alone sets N. ⚠️ **JUNK, MEASURED 2026-10-03 (card 142-3): every call also leaves 3 UNWIRED constants on the TOP-LEVEL diagram** — 1 DigitalNumericConstant at (-10,-8) + 2 ArrayConstants at (0,0), each owning one element (numeric / Boolean) = 5 `Constant` traverse entries (the op's erdosmiller `Create Constant.vi` calls; v0 structure `probe_opforloop.log:8-16`). Delete the 3 top-level ones after the call (elements go with their array), gate them unwired first; the For's own N stays unwired | row 39; junk: `build_ringpickslot_v2.log:21,57-62` |
| `copy_by_index(donor, cls, index, target, expect_uid, finish)` | `OpMoveByIndex_v0` | copies ANY object — built-in primitives included — from a donor by Traverse class+index with a UID guard; `finish(dst)` makes the loaded Target runnable before the single COM save | row 39 (`StrToPath.vi`) |
| `StrToPath.vi` (sub-VI: `string` → `path`) | — | the replay loop's per-frame path conversion (no `Format Into String`: copied instances keep their donor's argument count) | row 39, 3 round-trips exact |
| `OpConstValue_v1.vi` (`vi path`, `Class Name`, `index`, size?=F → `Value` variant, `hex string`, U8 `value`, `rest`, plus `UID`/`Class Name 2`/`# of Refs`) | `Constant.Value` 634AC00 read + `Flatten To String` + `Unflatten From String`(U8[]) + `Bytes to Lowercase Hex String.vi` | reads a diagram constant's value as lossless bytes (`decode_flat` in `build_opconstvalue_v1b.py`); **STRING constants only** — a numeric constant needs the subclass-typed reader below | row 42: 22 StringConstants of the main VI typed, `img%05d.tif`/`Bead # %d` match docs |
| `OpConstValueN_v1.vi` (`vi path`, `Class Name`, `index`, size?=F → value bytes, `Text`, `Representation`, the fed wire's `UID`, plus identity) | `Constant.Value` 634AC00 on a **`DigitalNumericConstant`-typed** node + `NumText` 634D007 → `Text.Text` + `Representation` 5DCFC00 + `Constant.Terminal` 634AC04 → `Connected Wire` → `UID` | a NUMERIC constant's value AND the wire it drives. The base-`Constant` node returns a void variant for numeric and Boolean constants — build the Value node for the object's **most-specific class** | row 43: 180 numerics scanned, identity-gated, TD always matches `Representation` |
| `OpWireSource_v5.vi` (`vi path`, wire `UID`, `term index` → per terminal: `Is Source?`, reciprocal wire, owner class + owner `UID`, cast-output class) | `UID to GObject Reference.vi` → cast(`Wire`) → `Wire.Terms[]` → Index Array → `Is Source?` 634A003 / `Connected Wire` 634A000 / `Generic.Owner` 6327806 → `ClassName` + cast(GObject) → `UID` | **which object drives a wire** — addressed by UID, so no traverse index is involved. Walk `term index` until error 1055; require exactly one terminal with `Is Source?` TRUE whose reciprocal wire is the wire asked about | row 43: wire 10850 → constant 10739 / sink `Comparison` 10950, 12/12. ✅ **RE-MEASURED 2026-09-17 and the op is NOT defective** (`tools/bench/diag_tunnelsource_onehop.log` G2, first try): the recorded "0 rows, error 1055 for all 38 wires" (`diag_d1_full_route.json:49-52`, STATUS OPEN 28c) was the CALLER — `diag_d1_full_route.py:265-273` / `build_opstopfromnode_v0.py:368-376` set `Class Name`+`index` (a Traverse index) and **never `UID 2`**, while this op is UID-addressed. With `UID 2` set it answers; with it 0 the cast has no object and index 0 is already past the end. ⚠️ `build_opwiresource_v5.read_terminal` hard-codes the ORIGINAL as `vi path` — pass the target explicitly |
| `OpOwnerChain_v1.vi` (`vi path`, any object `UID` → `Owner` class + owner `UID`, plus the self-read `UID`/class echo) | `UID to GObject Reference.vi` → `Generic.Owner` 6327806 → `ClassName` + cast(GObject) → `UID`, i.e. `OpWireSource_v5` with the `Wire` cast and the whole `Wire.Terms[]` front section removed | **any object → the object that OWNS it**, so a node resolves to its home diagram and a diagram to its structure. Built 2026-09-16 by `tools/recipes/build_opownerchain_v1.py` (20 gates pass, `tools/bench/build_opownerchain_v1.log`) | FUNCTIONAL on the main VI, read-only: `10407 → Diagram#639`, `1359 → Diagram#639`, `639 → WhileLoop#637` (B6). ⚠️ **MEASURED LIMIT 2026-09-16** (`tools/bench/diag_ownerchain_hop.log`): when the owner's class is **`FlatSequenceFrame`** the ClassName comes back but the **UID does not** — `owner_uid 0`, `error 1055: Property Node`, and the cast-class echo is **empty** where a `Diagram` owner echoes `'Diagram'`. So an owner chain **terminates silently at a flat-sequence frame**. Cause under peer review, slug `ownerchain-flatseqframe-1055` |
| `OpLoopEndRef_v0.vi` (`vi path`, `Class Name`='WhileLoop', `index` → `CondTermUID`, `IsSource`, `CondWireUID` + 4 error columns, and the donor's `LoopUID`/`ShiftRegUIDs`) | `OpWhileCast_v0`'s WhileLoop-typed TMSC → `WhileLoop.Loop End Ref` **6362C00** (data terminal `LpEndRef`) → `GObject.UID` 632A813 / `Terminal.Is Source?` 634A003 / `Terminal.Connected Wire` 634A000 → `GObject.UID` | **a While loop's CONDITIONAL TERMINAL** — the thing no node's `Terminals[]` can reach, and the reason two inference attempts at "how does #637 stop" were refuted. Additive build on OpWhileCast_v0 (nothing deleted); every property node **censused for its data terminal**, never gated on "no error 1077" (§ the `Control.Value` trap below). Built 2026-09-17, `tools/recipes/build_oploopendref_v0.py` | FUNCTIONAL on the main VI, read-only, 16/16 (`tools/bench/build_oploopendref_v0.log`, md5 unchanged): all **3** While loops resolved — #637 → term 648 / wire **3457** → `CompoundArithmetic` #11639; #25380 → 25410 / 1737; #15173 → 15276 / 19456 | ~1 s/loop |
| **`OpStopFromNode_v0.vi`** (`vi path`, `Class Name`='WhileLoop', `index` = the loop, **`index 3`** = body `Nodes[]` index, **`index 4`** = that node's `Terminals[]` index → the op's own `error out 7`) — **WRITER** | `OpLoopEndRef_v0`'s WhileLoop-typed TMSC → `WhileLoop.Loop End Ref` **6362C00** (`LpEndRef`) **branched** into `Terminal.Connect Wire` **6349C03** as the SINK; the SOURCE comes off the same TMSC through `Loop.Diagram` **6361401** → `AbstractDiagram.Nodes[]` **6375809** → IndexArray → `Node.Terms[]` **6359000** → IndexArray | **wires a While loop's stop from a terminal of a node INSIDE ITS OWN BODY** — what D1's end-of-stream sentinels need, and what `exit_while`/`OpExitWhile_v0` cannot do (that one takes a front-panel Boolean BY NAME). **ADDITIVE build on `OpLoopEndRef_v0`, gated: no class lost a member** (Node 14→20, Property 8→11, Wire 25→33, ControlTerminal 20→23, Invoke 0→1, IndexArray 1→3). Route chosen by its prior-art review, which refused the erdosmiller `Exit While Loop.vi` front-half swap (`archive/peer/2026-09-17-priorart-d1-op-exitwhile-node.md` B1). Built 2026-09-17, `tools/recipes/build_opstopfromnode_v0.py` | **20 pass / 2 fail** (`tools/bench/build_opstopfromnode_v0_run3.log`). ✅ **The write itself is MEASURED**: on a scratch While loop the conditional terminal went **term 119, wire 0 → wire 147**, and w147 is the **same uid on the body node's Boolean output** (`Is Path and Not Empty?`), op `error out` empty. ✅ **T5 CLOSED BY MEASUREMENT 2026-09-17** (`tools/bench/build_opsentinel_ops_run3.log`, gate F5c/F6): driven from a freshly created `Equal?` inside the body, the conditional terminal went **term 119, wire 0 → 387** and the scratch then read **ExecState 1** — the op produces a RUNNABLE VI. Run 3's `0 → 0 → 0` was `docs/NAMES.md:788` (the donor `Is Path and Not Empty.vi`'s required `path` was unwired), not a defect in this op. ✅ **T6 CLOSED 2026-09-17 — it was the CALLER, the same defect as row `OpWireSource_v5` above.** `build_opstopfromnode_v0_run3.log:56` reads `**FAIL** T6 DISCRIMINATOR … sources [] (want exactly one, owner #44)`; `tools/recipes/build_opstopfromnode_v0.py:373-376` sets `vi path`, `Class Name`, `index` and `term_index` and **never `UID 2`**, while `OpWireSource_v5` is UID-addressed — with `UID 2` unset the cast has no object and index 0 is already past the end. Same sentence, same line numbers, as the `OpWireSource_v5` row records for `diag_d1_full_route.py:265-273`. So the front half has **no open defect**; raised by `archive/peer/2026-09-17-priorart-priorart-connectfromwire.md` B2 (`already-failed`) | ~0.2 s |
| **`OpCreateEqual_v0.vi`** (`vi path`, `Class Name`/`index`/`Names`=[x source terminal], `Class Name 2`='Diagram'/`index 2`= the BODY diagram, `Names 2`=[y source terminal], `location (0, 0)`) — **WRITER** | erdosmiller **`Create Equal.vi`** wrapped in the `queue_node` shape on donor `OpExitLoop_v0`: `Diagram in` ← `Traverse('Diagram')[index 2]` cast, `x` ← IndexArray[0] of `Get Outputs`(216), `y` ← IndexArray[0] of `Get Outputs`(348) — **both operands are fetched INSIDE the op, so no terminal refnum crosses COM** (the fix for `docs/NAMES.md:473-475`, the 1055 modal that killed `OpBuildCase_v0`) | **places one `Equal?` Comparison node on a NAMED SUBDIAGRAM** with both operands wired from output terminals of one existing node — D1 §9a's end-of-stream sentinel test. Operands may sit on an outer diagram: LabVIEW makes the tunnels (measured `LoopTunnel 0 → 2`). §11g.1 lifted the cycle-15 freeze for exactly this op; built 2026-09-17 by `tools/recipes/build_opsentinel_ops.py` after `archive/peer/2026-09-17-priorart-priorart-d1-sentinel-ops.md` (7 findings, all accepted) | **FUNCTIONAL, 23/0** (`tools/bench/build_opsentinel_ops_run3.log`): on a scratch `EMPTY_v0` copy — new `Comparison` #46, owner chain **#46 → Diagram#110 → WhileLoop#43**, its Boolean output then drives the loop's conditional terminal through `OpStopFromNode_v0` (term 119, wire 0 → **387**) and the scratch reads **ExecState 1** | ~0.3 s |
| **`OpCreateConst_v0.vi`** (`vi path`, `Class Name 2`='Diagram'/`index 2`= the BODY diagram, `location (0, 0)`, **`Type`** and **`Value`** = VARIANT controls) — **WRITER** | erdosmiller **`Create Constant.vi`**, same donor and same `Diagram in` chain. It has **no refnum input at all**; `Type` (the constant's data type) and `Value` are VARIANTs, and both got front-panel controls — `Value` only because the build FORCES one: the probe loop stops at `ExecState 1` and `Value` is optional, so run 1 produced an op that could create only a DEFAULT-valued constant (measured, `build_opsentinel_ops.log`) | **places one numeric/Boolean CONSTANT on a NAMED SUBDIAGRAM** — the literal D1's sentinel compares against (−1). ⚠️ **Its `Terminal` output is NOT returned to the caller** (a refnum dies with the op's dataflow), so the constant is placed **unwired**; connecting it to another node's input needs a route this op does not have — see the OPEN item below the table | **FUNCTIONAL, 23/0** (same log): new `Constant` **#354** on the body diagram, owner chain **#354 → Diagram#110 → WhileLoop#43**, op `error out` empty, `Type`/`Value` variants accepted over COM without error. 🔴 **NOT verified: the constant's VALUE.** The created object reports class `Constant`, and nothing read its bytes back — `OpConstValueN_v1` (row above) is the reader that would | ~0.3 s |
| **`OpCreateConstOnTerm_v0.vi`** (`vi path`, `Class Name`='WhileLoop'/`index` = the loop, **`index 3`** = body `Nodes[]` index, **`index 4`** = that node's `Terminals[]` index, **`Value`** = the literal → **`UID 4`** = the created object's uid, **`error out 8`** = the invoke's own error) — **WRITER** | **`Terminal.Create Constant` 6349C00**, invoked on `WhileLoop[i].Diagram.Nodes[n].Terminals[t]`. Donor = `OpStopFromNode_v0` with its `Connect Wire` invoke replaced: the body-node ladder (`Loop.Diagram` 6361401 → `AbstractDiagram.Nodes[]` 6375809 → IA → `Node.Terms[]` 6359000 → IA) is kept verbatim. **MEASURED terminal census** (never done before): `reference`(0) · `reference out`(1) · `error in`(2) · `error out`(3) · `Create Constant` IN/OUT(4,5) · **`Value` IN/OUT(6,7)** — so the NI-documented optional `Value` input is real | **the literal, TYPED BY THE SINK and ALREADY WIRED, on a NESTED diagram.** This is the op that ends §11i's wall: no "create then connect" step exists, so the dead-refnum problem never arises. It creates NO panel object (`ControlTerminal` unchanged) | **FUNCTIONAL, 22/0** (`tools/bench/build_opcreateconstonterm_v0.log`): on a loop-body node's bare `error code`, one new **`DigitalNumericConstant` #159**, owner chain **#159 → Diagram#110 → WhileLoop#43**, terminal wire **0 → 176**, value read back **`-1`, Representation 3** through `OpConstValueN_v1`, scratch **ExecState 1**. ⚠️ Same run MEASURED the contrast: `OpCreateConst_v0`'s VARIANT route produced class **`Constant`** with an **EMPTY** value — it does **not** carry −1 (STATUS's material question, closed) | ~1 s |
| **`gscript.create_const_loop_term(target, kind, index, value, term_index=0)`** → `OpCreateConstTop_v0.vi` (`kind='for_n'`: top-level `Nodes[index].Terminals[term_index]`; `vi path`, `Names`/`Names 2`=[], `Class Name`/`Class Name 2`='', `index`, `index 2`, `Value`) / `OpCreateConstLoopEnd_v0.vi` (`kind='while_cond'`: `vi path`, `Class Name`='WhileLoop', `index` = Traverse index of the loop, `Value`; `index 3`/`index 4` are ignored) — **WRITER**, labels in `tools/bench/opcreateconst_loopterm_labels.json` | A = `OpCreateIndicator_v0` with invoke 6349C02 swapped for **`Terminal.Create Constant` 6349C00** + `Value` control + `GObject.UID` 632A813 and error indicators. B = `OpCreateConstOnTerm_v0` with the invoke's `reference` fed from **`WhileLoop.Loop End Ref` 6362C00** (`LpEndRef`, as a branch) instead of the body-node terminal | **a diagram constant, typed by the sink and already wired, on a LOOP-OWNED terminal**: For N (top-level For loop, N = `Terminals[0]`, `docs/NAMES.md:313`) and a While loop's conditional terminal at any nesting depth. A body-node terminal stays `OpCreateConstOnTerm_v0` | **WARM ONLY, 2026-09-25, task 77-2** (`tools/bench/const_loopterm_77.log:23-24`): For N → one new **`DigitalNumericConstant` #237** on the top-level diagram, N wire 0 → **250**, invoke error `''`; While conditional → one new **`BooleanConstant` #243** in the loop body, `OpLoopEndRef_v0` reads cond term #119 wire **260**, invoke error `''`. ✅ **COLD, 2026-09-25, task 77-3** (`tools/bench/const_loopterm_77c.log:8-14`): after scripted save + LabVIEW restart ExecState 1; For N constant text `1` on N wire 250; control body constant (OpCreateConstOnTerm_v0) text `-7`; cond still `BooleanConstant` #243 on cond wire 260 (value True not read); 20 calls handles 31113 → 31119, refs 8/8 closed. No reader exists for a `BooleanConstant`'s value (`docs/NAMES.md:1149`) | ~1 s |
| **`OpConnectNested_v0.vi`** (`vi path`, `Class Name`='Diagram'/**`index`** = the diagram, **`index 2`/`index 3`** = SINK `Nodes[]`/`Terminals[]`, **`index 4`/`index 5`** = SOURCE `Nodes[]`/`Terminals[]` — both ends on THAT diagram) — **WRITER** | `Terminal.Connect Wire` **6349C03**. Donor = **`OpConnect2_v0`** (chosen by `archive/peer/2026-09-17-priorart-connect-nested.md` B3-i over §11m's named `OpStopFromNode_v0`, which is **loop**-anchored and cannot express a diagram index): its nested SINK ladder `Traverse('Diagram')[index] → To More Specific Class → Nodes[] → IA → Terms[] → IA` is kept, its source head `VI[Block Diagram 23C]` is **deleted**, and the same TMSC's `specific class reference` is **branched** into the source `Nodes[]` node | **wires two terminals addressed purely by INDEX on a NESTED diagram** — the only route to a terminal with **no name**, which `gscript.wire` / `wire_control` (name-addressed, 5001 from `Get Controls.vi`/`Get Outputs.vi`), `connect_terminals` (both ends TOP-LEVEL) and `connect2` (top-level SOURCE) all miss. Built 2026-09-17, `tools/recipes/build_opconnectnested_v0.py` | **BUILT + WIRE-IDENTITY VERIFIED, NOT ExecState-verified — say it exactly.** Build 10/1 (`tools/bench/build_opconnectnested_v0.log`, ExecState 1, saved, 14 234 B); test 7/1 (`tools/bench/test_opconnectnested_v0.log`): body→body on a nested diagram **wire 0 → 206, same uid on both ends**, and an **UNNAMED** terminal of a body node reached by index, also w206 (a BRANCH, so `wire delta 0` is expected). 🔴 The scratch read **ExecState 0** — the test paired `error out` into a `path` input and a fresh While loop's unwired conditional terminal is a broken VI by itself (`build_opstopfromnode_v0.py:438-441`), so the ExecState gate was invalid; peer `connectnested-t2b` | ~0.2 s |
| ✅ **`OpConnectNested_v1.vi`** (`vi path`, `Class Name`='Diagram'; SINK = **`index`**/`index 2`/`index 3` = diagram/`Nodes[]`/`Terminals[]`; SOURCE = **`index 6`**/`index 4`/`index 5` — **a DIFFERENT diagram**) — **WRITER** | `Terminal.Connect Wire` **6349C03** with **TWO** independent `Traverse('Diagram')[i] → To More Specific Class → AbstractDiagram.Nodes[] → IA → Node.Terms[] → IA` ladders. Built **additively on `OpConnectNested_v0`**: the single TMSC's output net is deleted, a **TYPED SEED** refnum control is made by `Terminal.Create Control` **on the source `Nodes[]` node's own `reference`** (so its class is that node's by construction, never a typed string), a **second `To More Specific Class`** is brought in with `copy_by_index` from the NI example `Navigating Nodes and Wires.vi` (`Function[6]`, uid 99 — the route `build_opconstvalue_v1.py` proved), and a second `Index Array` on the same Traverse `References` array carries the source-diagram index | **wires two terminals by INDEX on two DIFFERENT nested diagrams.** LabVIEW creates the border tunnels itself (`LoopTunnel 0 → 2`, wire delta 3), so the sink and source wire uids **differ** — a cross-boundary wire is several segments. Built 2026-09-17, `tools/recipes/build_opconnectnested_v1.py` (run 1 died on a Python `TypeError` in the recipe's own hook; run 2 **31 pass / 1 fail**, the one failure a test-harness stale diagram index) | ✅ **FUNCTIONAL, WARM AND COLD — `tools/bench/test_opconnectnested_v1_cold.log`, 7 pass / 0 fail** in a RESTARTED LabVIEW: cold `ExecState 1`, 14 666 B, two casts, `index 6` present; body(A) `error out` → body(B) `error in (no error)` across diagrams, op error `''`, sink w268, and the wire **SURVIVES `remove_bad_wires_scripted`** — 🔴 **THIS SENTENCE IS WRONG ABOUT ITS OWN IMPLEMENTATION, corrected 2026-09-17** (`docs/d1-build-plan.md` §11u.1, `archive/peer/2026-09-17-rbw-deleted-wires-run9.md`, codex ANSWERED, accepted in full): the "survives RBW" check at `tools/recipes/build_d1_v0.py:1118-1121` IS uid equality — it compares two `Terminal.Connected Wire` 634A000 reads, and `Terminal.Connect Wire` 6349C03 returns nothing, so it measures object identity, not survival. **Do not cite RBW-survival as evidence a wire is good.** Use `ExecState 1` on an otherwise-runnable scratch; the sound reader, `Wire.Is Broken?` **6371004** + `Wire.Terminals[]` 6371003 from a HELD terminal reference, is **NOT BUILT** (`NAMES.md:861-863`) 🔴 **CORRECTED 2026-09-23 — this "NOT BUILT" is STALE, and it is the third copy of a sentence already corrected once on 2026-09-18 at `docs/d1-route-b-plan.md:340-345`.** `docs/NAMES.md:992` records *"`Wire.Is Broken?` 6371004 IS BUILT AND MEASURED, 2026-09-17 — and it never needed a new op"*. The true distinction, which every copy of this sentence has lost: what is built reads **ONE** wire and only **AFTER** a `Terminal.Connect Wire` write (the readback embedded in the connect ops, `docs/NAMES.md:1003-1017`), so it cannot be used read-only and it perturbs the target. **A write-free, whole-VI, per-wire `Is Broken?` census is what is absent** — conceded as genuinely unbuilt by `archive/peer/2026-09-23-priorart-allwires.md` A3, which is also where this correction was raised. Cite the distinction, never the bare "not built"; and an **UNNAMED** For-loop count terminal on diagram P wired from a source on diagram Q, wire **0 → 414**, op error `''`. ✅ **NOW MEASURED IN THE REAL VI** (`tools/bench/build_d1_v0_run9.log`, §11s.2): 8 wires made on the D1 working copy — 7 same-diagram body wires and 1 cross-diagram `D[19] → D[24]` — of which **5 SURVIVED `remove_bad_wires_scripted`** and 3 were deleted by it (`#1359` t4, `#1359` t9, `#29874` t4; two are branches of one `#8885 x*y` net, wire 26189). It moved the re-wire from 35 to **42 of 66**. ✅ **REVISED 2026-09-17: "3 were deleted" is not what was measured.** One of the three (`#1359` t4) ended with a **non-zero** wire (`26189 -> 26412`, `build_d1_v0_run9.log:269`) and was counted as deleted only because the uid changed. The honest statement is **at most 2 of 8 became null and 1 of 8 changed wire identity**; terminal-INDEX drift across tunnel creation is a live, unmeasured alternative (§11u.1) | ~0.2 s |
| 🔴 **SUPERSEDED BY THE ROW ABOVE — the v0 limit was ONE diagram index, not two.** `docs/d1-build-plan.md` §11m specifies "both ends by index on **nested diagrams**", i.e. sink and source on DIFFERENT nested diagrams. That is **not buildable by this fleet** | Two independent nested diagrams need a **second `To More Specific Class`**. Run 1 built the alternative the prior-art review prescribed — a second `Index Array` on `Traverse for GObjects.vi`'s `References` array feeding the source `Nodes[]` node — and **measured ExecState 0**: `References` is an array of **GObject** refs, the property node is **Diagram**-class, and GObject→Diagram is a downcast | So the op ships with the source constrained to the sink's diagram. ⚠️ **"A second TMSC has no creator" is WITHDRAWN 2026-09-17** (prior-art review `archive/peer/2026-09-17-priorart-connectnested-v1.md`, A3-i `contradicted` + B3-i `helper-exists`). Three refutations, all from our own files: (1) `:72` of this file — *"`target class` accepts **any wire of the target type**"* — so it never has to be a class-specifier `Constant`; (2) `tools/recipes/build_opconstvalue_v1.py:165-199` **copied** a TMSC with `copy_by_index` and fed `target class` from a `create_control` seed (`OpConstValue_v1.vi`, 13,499 B, on disk); (3) **`OpExitLoop_v0.vi`, `OpWire_v1.vi` and `OpWireSource_v5.vi` each already carry TWO independent `Traverse → IA → TMSC` ladders** (`tools/bench/probe_opexitloop.log:12-18`: #683 and #788, the latter Diagram-typed, each with its own `Class Name`/`index` pair) — the 6-donor census that concluded otherwise (`diag_connectnested_donors.log`) censused none of those three. What run 1 actually measured is narrower and stands: an **ungated** `GObject` element wired straight into a `Diagram`-class property node is a downcast and reads ExecState 0 | `tools/bench/build_opconnectnested_v0_run1.log` (`W4 ROUTE A wired: ExecState 0`); consequence for D1's 17 `from-tunnel` rows is STATUS OPEN |
| ✅ **`OpConnectFromWire_v0.vi`** (`vi path`, `Class Name`='Diagram'; SINK = **`index`**/`index 2`/`index 3` = diagram/`Nodes[]`/`Terminals[]`; SOURCE = **`UID 3`** = an existing WIRE's uid + **`index 7`** = which terminal on that wire → `UID 2`, `Is Broken?`, `Name`, `error out 2`/`error out 3`) — **WRITER** | `Terminal.Connect Wire` **6349C03** whose `Wire Source` is a terminal taken from `Wire.Terms[]` **6371003**, not from `Nodes[]`. Built ADDITIVELY on `OpConnectNested_v1` (nothing deleted but ONE wire): `UID to GObject Reference.vi` (`vi.lib\VIServer\`) → a THIRD `To More Specific Class` (`copy_by_index` from the NI example, uid 99) fed by a **Wire-typed seed** made with `create_control` on a `"VI Server:Wire"` property node's own `reference` → `Wire.Terms[]` → Index Array → `Wire Source`. The old `Nodes[]`-based source ladder is left in place and DEAD (its `error out`s are unwired, so it cannot poison the Invoke; `index 4/5/6` may stay 0) | **the only writer whose SOURCE need not be a node** — what the 16 `FlatSequenceInnerTunnel` / `LeftShiftRegister` from-tunnel rows need (`d1_tunnel_sources.json`, `d1-build-plan.md` §11t). ✅ It also carries the project's first ORDERED `Wire.Is Broken?` **6371004** readout: the donor already had the reader (#241→#242) but its `error in` was unwired, so it ran before the write and always printed `UID 2: 0` — gate W7b branches the Invoke's own `error out` into it | **BUILT + SAVED 2026-09-17, 16,524 B, ExecState 1; `tools/recipes/build_opconnectfromwire_v0.py`, run 2 42 pass / 1 fail** (`tools/bench/build_opconnectfromwire_v0_run2.log`). ✅ **T1 FUNCTIONAL**: on a scratch, branched an OUTER-diagram wire's source terminal into a node inside a NEW While loop body — op error `''`, sink wire **0 → 229**, **`Is Broken? FALSE`**, `LoopTunnel 0 → 1` (LabVIEW made the border tunnel itself). ✅ **T2a**: on a copy of the real VI it ACCEPTED a source terminal owned by `FlatSequenceInnerTunnel` **#5818** (wire w5812) and created a wire, op error `''`, sink **0 → 1231** — the capability §11s.1 said did not exist. 🔴 **T2c2 FAILED: that wire reads `Is Broken? TRUE`**, and w1231 has **TWO** terminals reporting `Is Source? TRUE` (`SelectorTunnel` #5680, `LoopTunnel` #2497). The sink terminal the op resolved is named **`Bead is good? array out`** — an OUTPUT tunnel — because terminal index 1 came from a census of the RESTRUCTURED copy and was applied to an UNRESTRUCTURED one. Reading under peer review, slug `cfw-t2c2-broken-wire`; **not** diagnosed here | ~0.3 s |
| 🎉 **`OpCreateLocalRead_v0.vi`** (`vi path`, the panel control to bind to, **`Write?`** = Boolean → a new `Local` **in the mode asked for**) — **WRITER** | Built **ADDITIVELY on `OpCreateLocal_v0`** (donor md5 `58275b21…` byte-unchanged — `docs/cycle27-plan.md` Pre-decided 51(h)): the donor's `Create:Local Variable` **6331C02** Invoke is kept whole, and its **`i=5 'Create Local'` SOURCE** — the created object's own reference — feeds a **write-mode `'VI Server:Local'` property node** carrying `Local.Write?` **6355401** (short name `Write?`, Boolean, terminal i=4 = SINK in write mode, SOURCE in read mode), whose value comes from a front-panel Boolean made by `create_control` on that SINK (`ControlTerminal` #434, label `'Write?'` read off the machine). 🎉 **NO `To More Specific Class` anywhere**: the Invoke's own output is already `Local`-class, ordered `Is Broken?` **False** on the reference wire (#339 `reference` ← #306 i=5, wire 390) | **creates a Local Variable ALREADY IN READ MODE** — the one thing S3b needs and this fleet could not do. A Local is born WRITE (`is_source` False), while `#10407` t0/t2 are SINKs fed from SOURCEs, so their replacements must READ (Pre-decided **52(a)**, measured off `c53_row_class.json` + the rewire JSON + `main_vi_nodeterms.json`, all three agreeing). Built 2026-09-21 by `tools/bench/diag_c61_localdir_write2.py`, after the same cycle repaired `build_property`'s **mode-blind post-condition** — it asserted write items against `Outputs`, where an input can never appear, and refused the known-good 6355400 identically (`tools/gscript.py`, +37/−2, 5/5 self-test + the `VI Server:VI` 242 regression unchanged) | **BUILT + SAVED + FUNCTIONALLY EXERCISED 2026-09-21**, md5 `f695d97a36ae127cd2dd3ca6b1fc1089`, 10,192 B, LV2026 `26 00 80 00`: `ExecState` **1 at the save and 1 COLD** in a freshly restarted LabVIEW (`tools/bench/diag_c61_localdir_write2.log`, **38 pass / 0 fail**). On a scratch of `D1_s3a_focus_ind.vi`: `Write?`=False → Local **#23507** bound to **`'index'`** (hex `696e646578`), **`is_source` True = READ**; `Write?`=True → **#23508**, `'index'`, **False = WRITE** — the Boolean steers the mode; both error clusters `(False, 0, '')`, census 8→9→10, refs 26/26/**0 live**, four md5 pins PASS before and after. ⚠️ The `Write?` wire itself has **no `Is Broken?` route** here (its source is a panel object; the reader addresses sources as `Nodes[]` positions) — `ExecState` 1 COLD covers every wire in the VI and is the stronger statement, **52(g)**: no reader is built | ~0.05 s/call (20 calls in 0.9 s) |
| **`gscript.create_indicator_nested(target, node_uid, terminal_index)`** → `OpCreateIndicatorNested_v0.vi` / **`gscript.create_control_nested(target, node_uid, terminal_index, value=None)`** → `OpCreateControlNested_v0.vi` (`vi path`, `Class Name`='Node', `index` = Traverse('Node') index of the uid, `index 3` = Terminals[] index, control op also `Value`; out `UID` = created object, `error out 2`, `UID 2` = node echo, `error out 3`; labels `tools/bench/facts_c100_oplabels.json`) — **WRITER**, card 100-2 | c97 typed-seed route on an `OpSetIndexMode_v0` copy: Traverse → IA → TMSC (Node seed) → `Node.Terms[]` 6359000 → IA → Invoke `Terminal.Create Indicator` 6349C02 / `Create Control` 6349C01 → `GObject.UID`. Invoke census: t4/t5 = the method's own return pair (a control on t4 raised a modal dialog, `diag_c100_verbs_build.log:43`); 6349C01 also has a real optional **`Value`** t6/t7 (`archive/peer/2026-09-26-c100-verbs-build.md`) | **indicator/control on a terminal of a node on ANY diagram, addressed by the node's UID**, born on the node's own diagram and wired (the top-level `create_indicator`/`create_control` reach `VI → Block Diagram → Nodes[]` only) | built, saved, **ExecState 1 COLD** both (`tools/bench/diag_c100_verbs_build2.log:32-33,61-64`; md5 `0e5a4739…` / `ead0d743…`). ✅ indicator FUNCTIONAL on a scratch of S1: `#11608` t0 (`output cluster`, wired w12256) inside Diagram #639 → new terminal #23261 owned by Diagram #639, panel object #23006 `output cluster 2` on w12256 (a BRANCH of an existing wire), echo 11608, error `''` (`:75-79`). ✅ **card 100-4 (`diag_c100_verbs_build3.log` / `_build4.log`):** the control verb is FUNCTIONAL on Wait (ms) `#44143` t1 in Diagram #44125 (new control wired, `value=100` read back 100; 19 more calls, handles 54,831→54,823). ⚠️ **MEASURED: `Create Control` on an ALREADY-WIRED sink does NOT fail — it makes a DANGLING control (terminal wire 0, error `''`, `_build3.log:45`)**, so `create_control_nested` now READS the sink first (`gscript._node_term_row`) and a wired sink / an output → `ValueError` before any edit (`_build4.log:53`); both verbs append `NOT WIRED (dangling)` to `err` when the new object has no wire. ✅ **TUNNEL / TERMINAL OWNER (PD213(b)), Python only:** `create_indicator_nested(target, <LoopTunnel uid>, None|'outer')` or `(target, <outer-face terminal uid>, None)` routes to **`OpTunnelInd_v0`** (Tunnel.Outside Terminal 6356001 → Create Indicator; FUNCTIONAL since 2026-09-13) with the `Traverse('LoopTunnel')` index resolved from the uid and ECHOED by `OpTunnels_v0` first; the face is proven OUTER by its wire (allterms row vs `tunnels().out_wire`). On S1: `#9234` (outer face of `#9227`, For #1359) → panel object `Array` on **w9215** (a branch), echo 9227, terminal owned by Diagram #639; alias `(9227,'outer')` the same; inner face `#9230`, `'inner'`, a wire uid → `ValueError`, nothing created; 20 calls handles 54,746→54,742 (`_build3.log:23-38`). Only LoopTunnel faces are routed (no inner face, no Selector/FlatSequence tunnel) | — |
| **`gscript.create_indicator_nested(target, <SelectorTunnel outer-face terminal uid or SelectorTunnel uid>, None\|'outer')`** — card 108-4 (PD222(b)), Python only, **no new op** | `_selector_outer_face`: allterms row → owner chain (`build_d1_v0.owner_of`) tunnel → **CaseStructure** → Diagram, `Traverse('Diagram')` index, `OpNodeTerms_v0` on the case (uid echo) → the ONE `Terms[]` entry that is a SOURCE on the face's wire (a wire has one source) → `_create_on_node_term("OpCreateIndicatorNested_v0", case, k)`; effect check = exactly one new panel object on the face's wire (a BRANCH). `OpTunnelInd_v0` is not used: its cast is LoopTunnel-typed (`tools/recipes/build_optunnelind.py:119`) | an indicator on a **case-structure OUTPUT tunnel's OUTER face** (L2-A3 row 2, `#11336 t11346`). Inner face, unwired or sink outer face, non-CaseStructure owner, no unique `Terms[]` entry → `ValueError` before any edit. LoopTunnel faces and int indices keep their routes (checked first) | **BUILT + SCRATCH-VERIFIED 2026-09-27, 24/0** (`tools/bench/diag_c108d_selind2.log`; record `tools/bench/scratch_verify/gscript.create_indicator_nested_20260927_141618.json`): byte copy of `TRACK_kernel_v1.vi`, outer face #488 of SelectorTunnel #430 → case #154 `Terms[11]` → indicator `pos in cal image out 2` on w408 (branch, Wire 40→40, ControlTerminal 14→15), face still the only source, ExecState 1; alias (#430, None) the same; inner face #434 and input-tunnel face #449 → `ValueError`, nothing created; 20 more calls handles 35,998→35,995; refs 7/7. A stagekit scratch script needs a graph JSON (`--graph`) and a decision-row plan to pass dry/prerun (`archive/peer/2026-09-27-c108d-selind-dry.md`). ⚠️ `stagexec` still routes indicator creation on LoopTunnel faces only (`tools/stagexec.py:306-318`, `:1793-1802`, `:2086-2092`) | — |
| **`gscript.set_visible(target, uid, visible)`** → `OpVisibleSet_v0.vi` (`vi path`, `index` = Panel.Controls[] index resolved from the panel_wiring uid, `Visible` → `Visible 2` read back, `UID`, `error out 2`) — **WRITER** | OpLabelSet_v0 route on an `OpFPLabels_v0` copy: `Control.Visible` **6332000** WRITE on the Control PN's `reference out`, then `Control[Visible 6332000, UID 632A813]` READ chained by reference + error. The id was MEASURED by attaching `VI Server:Control` candidates (first try: `6332000` → output `Visible`, `diag_c100_verbs_build.log:126`) | hides/shows a top-level front-panel object and reads it back in the same run; a uid that is no panel row → `ValueError` before the run | built, saved, **ExecState 1 COLD** md5 `54051663…` (`diag_c100_verbs_build.log:129-130,141`). ✅ **FUNCTIONAL (card 100-4, `diag_c100_verbs_build3.log:40-42`)**: on panel object #23006 of a scratch of S1, False/True/False written and read back, echo 23006, error `''`; a non-panel uid refused; 20 alternating calls all read back, handles 54,762→54,761 | — |
| **`gscript.read_bool_const(target, uid)`** → `OpConstValueB_v0.vi` (`vi path`, `Class Name`='BooleanConstant', `index`; out `Value` (variant → Python bool over COM), `error out 2`, `UID` echo, `error out 3`) — READER | c97 typed-seed route: TMSC with a **`VI Server:BooleanConstant`** seed → `Constant.Value` 634AC00 (the base class returns void for Booleans, `docs/NAMES.md` constant-class note) | the value of a Boolean diagram constant | ✅ **FUNCTIONAL** (`diag_c100_verbs_build2.log:65,70-73`): cold ES 1, md5 `2a540847…`; on a byte-identical scratch of S1 **`#25261` = `False`**, echo 25261, error `''`; a non-BooleanConstant uid refused; 20 calls same value, handles 54508 → 54509 | — |
| **`gscript.create_local_write(target, panel_index, dest_diagram_uid=None, position)`** + **`stagekit.create_local_write(label, panel_index=None, dest_diagram_uid=None, position)`** — WRITER, no new op | `OpCreateLocalRead_v0` (row above) with `Write?` = True → Local uid by set difference → `build_d1_v0.move_in` into the nested diagram (destination resolved BEFORE the create) → owner + terminal direction read back | a WRITE local on a nested diagram (the display loop's `Force (pN) vs Extension (nm)` write) | ✅ **`gscript.create_local_write` FUNCTIONAL (card 100-4, `diag_c100_verbs_build3.log:74-98`)**: bound to `Force (pN) vs Extension (nm) ` (one panel row), Local #28649 in Diagram #44125, `is_source [False]` (WRITE), error `''`; a non-Diagram destination (`#44143`) → `ValueError` before creating (Local count 8 unchanged); 20 calls all placed, handles 54,910→54,909. 🟡 the `stagekit` wrapper itself was NOT LabVIEW-run: a harness that imports `stagekit` and calls `delete_object`/`save` is gated as a STAGE by `guard_bash` (`stage_prerun.is_vi_modifying`, card chat-N1); its only extra logic is the exact-label → panel index lookup, reproduced in the harness. ✅ **`gscript.create_local_read(target, panel_index)` (cycle 102) = the same op with `Write?`=False, is_source `[True]`; `stagekit.create_local_read` now binds to IT (the old binding drove `OpCreateLocal_v0`, a write-mode local, `stage_d1_disp_r6.log:544,595`); FUNCTIONAL in `stage_d1_disp_r7.log` ops 26–30 (five read locals, diff 0) and the tunnels wired from them at ops 31–37** | — |
| **`gscript.create_primitive_nested(target, diagram_uid, prim_name, pos) -> uid`** → **`OpPrimCopyNested_v0.vi`** (md5 `89e45459…`, 13,427 B; `vi path`, `Class Name`='Diagram', `index` = Traverse('Diagram') index, **`vi path 2`** = the DONOR file, `UID` = donor object uid, `position`, `Duplicate? (F)` = True → `UID 2` donor echo, `UID 3` diagram echo, `error out 4` = the Move's error; labels + donor registry `tools/bench/facts_c100_oplabels.json` key `OpPrimCopyNested_v0`) — **WRITER**, card 100-4, V6 | built on an `OpSetIndexMode_v0` copy, which carries TWO `Open VI Reference`s (`inspect_setindexmode.log`: #43 ← `vi path`, #316 ← `vi path 2`, an orphan): c97 retarget with a `VI Server:Diagram` seed (TMSC #683 → PN `UID`), **`GObject.Move` 632A400** (census: reference, error in, `Move` return pair t4/t5, `position`, `owner`, `duplicate`) with `owner` ← the Diagram cast and `reference` ← `UID to GObject Reference.vi` whose `Owning VI` ← OVR #316. A Move whose owner is in ANOTHER VI duplicates (`archive/peer/2026-08-28-copy-nodes-between-vis.md:31-44`) | **places a PRIMITIVE by DONOR COPY on ANY diagram of an arbitrary loaded target** — not bound to the Moving-Objects fixture (which `stagekit.copy_in` needs, and which the display stage uses for the base). Donor registry: `Max & Min` = uid 43 (class `Comparison`) of **`claudeDev\OpPrimDonor_v0.vi`** = a byte copy (md5 `6e958063…`) of NI `examples\Comparison\Max and Min.vi`, which holds SIX `Max & Min` nodes (lowest uid taken). Verb post-conditions: op error `''`, both echoes, exactly one new Node, owner = Diagram #diagram_uid; unknown primitive / non-Diagram → `ValueError` before any edit | ✅ **FUNCTIONAL (`diag_c100_verbs_build4.log`, 27/0)**: build ES 1 and COLD ES 1; on a scratch of S1, `Max & Min` #2146 born in Diagram #639 (label read back), negatives refused with Node count unchanged, 20 more calls 20 distinct nodes, handles 54,650→54,650. The copy is UNWIRED (the scratch reads ExecState 0 until its inputs are wired) | ~1-2 s |
| `OpTunnelRead_v0.vi` (`vi path`, tunnel `UID`, `term index` → inner wire, frame diagram `UID`, owner) | cast(`Tunnel`) → `Inside Terminals[]` 6356000 → Index Array → `Connected Wire`, `Terminal.Diagram` 634A002 → `UID` | **what each FRAME puts on a structure tunnel.** The inner-terminal array order is not documented as frame order — map each terminal to its frame via `Terminal.Diagram` | row 43: both #5540 output tunnels, 24/24 |
| ✅ **`OpAllTerms_v0.vi` — BUILT, SAVED AND FUNCTIONALLY TESTED 2026-09-23** (`vi path`, `Class Name` = the Traverse class → six auto-indexed arrays: `Array 2` term_uid · `Array 5` term_name · `Array 6` is_source · `Array 7` wire_uid · `Array 8` owner_uid · `Array 4` owner_class, map in `tools/bench/opallterms_labels.json`) | `Open VI Reference` → `Traverse for GObjects` → For loop → **PN1 `VI Server:GObject`[Position · UID 632A813 · ClassName · Owner 6327806]** (cast-free: Traverse yields GObject) → **TMSC1** → `VI Server:Terminal`[Name 634A004 · Is Source? 634A003] → `VI Server:Terminal`[Connected Wire 634A000] → `VI Server:GObject`[UID] (a Wire IS a GObject, no cast); and **PN2 `VI Server:Generic`[ClassName] → TMSC2 → `VI Server:GObject`[UID]** for `owner_uid`. ONE CONCERN PER NODE (`:74`). Both `To More Specific Class` nodes were placed by **GUI Quick Drop** — the only operation on this route with no scripted creator — and their `target class` seeds by `create_control` on a THROWAWAY root-diagram property node (`create_control` cannot reach a loop body, `docs/NAMES.md`) | **the whole-VI terminal table in ONE op run** — `docs/connectivity-map-plan.md` step 1, and the join half of the connectivity map (`tools/allterms.py`). Replaces ~508 s of `node_terms` sweeping | **14,600 B, md5 `484853aad3a9c2819d7fd36028491a81`, `ExecState` 1 COLD** (`tools/bench/allterms_s3.log` run 2, **39 pass / 1 fail**). ✅ On the bed: **5,811 rows**, the four known endpoints EXACT (`w1731` src `LeftShiftRegister#4344` · `w3947` src `#4274` · `w9635` src `LoopTunnel#9641` · `w7337` sink `RightShiftRegister#4334`), **5/5** random wires agree with `OpWireSource_v5`, **0 rows with `owner_uid` 0** (the retarget review's predicted silent-default defect did NOT occur — the one-concern-per-node split is why), handles **45,738–45,751 over 20 calls**. ✅ **ALL THREE 2026-09-23 MISSES WERE RULED ON BY JUDGEMENT AND THE RULINGS ARE NOW MEASURED** (`tools/bench/diag_wiki_probe.log`, 12 pass / 0 fail): (1) **the wire-join criterion is `1,913 termed + termless by SET DIFFERENCE against report_all('Wire')` = 1,920**, implemented as `allterms.all_wire_uids()` + `join_wires(rows, uids)` — on the bed it returns 1920 uids in **3.09 s**, 1913 termed / 7 termless, and `severed()` == `[1731,1893,2819,3947,4833,7337,7388,9635,11232,23502,23540]` EXACTLY, so the op meets the plan's "11 broken wires" criterion after all; (2) **warm 10–12 s passes the ≤ 15 s criterion** — the 24.2 s cold figure is the LOAD; (3) **+0.7 MB/call is ACCEPTED, re-measure at 100 calls** (14.69 MB over 20). 🟡 The original three-miss text, kept because it is the measurement: **cold 24.22 s vs warm 9.73–11.9 s** against a ≤15 s criterion set from a Traverse-only measurement; the join returns **1,913 wires, not 1,920**, because the **7** wires `diag_c90_endpoints.log` measured with an EMPTY `Wire.Terms[]` have NO terminal and are invisible to a TERMINAL-centric join (1920−7=1913 exactly), so only the **4** one-terminal wires show as severed — `[1731, 3947, 7337, 9635]`, three missing a sink and one missing a source; and **private bytes +14.69 MB over 20 calls** vs ≤5 MB, with **no `Close Reference` creator in the fleet** to fix it. All three are judgement's to rule on | cold 24.2 s · warm ~10.5 s |
| 🟡 *(superseded by the row above)* **`OpAllTerms_v0.vi` — S1 DELIVERED, S2 HAS NO ARTEFACT** (`claudeDev\OpAllTerms_v0_s1.vi`, md5 `ca44b62fbe428282719e4733e2cea785`, 12,512 B, `ExecState` **1** warm and after the scripted save) | S1 = `OpReportAll_v0.vi` unchanged (md5 `ffcec2c7…`): `Open VI Reference` → `Traverse for GObjects` (`Class Name` is a CALL-TIME control) → For loop with the AUTO-INDEXED input tunnel → `VI Server:GObject`[Position · UID 632A813 · ClassName 6327803 · Owner 6327806] → `VI Server:Generic`[ClassName] → 4 auto-indexed output tunnels (`Array`…`Array 4`). ⚠️ The brief's "empty body + a tunnel" is NOT CONSTRUCTIBLE — `for_loop` (`gscript.py:1250`) makes an EMPTY loop and the tunnel exists only because a body node is WIRED from `References`. Those two nodes carry **term_uid and owner_class WITH NO CAST**, because Traverse yields GObject | **the missing columns are exactly the Terminal-class ones** (`Name` 634A004 · `Is Source?` 634A003 · `Connected Wire` 634A000) plus `owner_uid`, and each needs a `To More Specific Class` INSIDE the body. 🟢 **The TMSC can be BORN there by GUI Quick Drop — measured, keyboard only, twice** (`docs/NAMES.md` §"ONE `VI Server:Terminal` property node…", 2026-09-23 correction): `Ctrl+Space` → the window titled `Quick Drop` → type the name → Enter → the node appears AT THE MOUSE. So `move_in` (the F-side route Pre-decided 139 forbids) is no longer the only way in | Geometry: ForLoop uid **113** (1400,900), box ≈1530×1210; body Diagram index **1** uid **272**. 🔴 TWO open laws, both measured: a REAL mouse click must land before the next COM call (else `report_all` hangs 180 s — `tools/bench/allterms_s2.log` run 1), and even after that click the dropped node was NOT in `Traverse('Function')` although a TMSC's class IS `Function` (`tools/bench/allterms_tmscclass.log`, 4/0). Review owed | `tools/bench/allterms_s1.log` 13 pass / 1 fail (the fail is the script's own slice) · `allterms_s2.log` run 1 11/1, run 2 9/4 |

Design rules that came out of the day (each was a failed prediction first): **one property per node** with its own
error chain (a failing row silently defaults the rows below it on the same node); **match terminal names the walk
printed, never a guessed variant** (`Broken?`, not `IsBroken`); **the donor decides the index space** (OpNodeInfo_v0's
`index` is a node index, OpNetInfo_v1's is a diagram index); **junk Invokes land only on an open target** (a
reference-only read never receives them — `walk_junk_probe.log`), and the junk-dropping creator can be deleted from a
copy (OpSubVIs_v1 / OpNodeTerms_v0 are creator-free). Traverse classes that work: `Global`, `Local`, `LoopTunnel`,
`Property`, `Invoke`, `SubVI`, `Diagram`, `Wire`… (`GlobalVariable`, `LocalVariable` → error). ~~What still needs a
cast and has no donor: shift registers, an implicit property node's linked object, `Constant.Value`.~~ **Closed the
same evening:** shift registers via the typed-control seed (`loop_cast` → `shift_reg` / `shift_reg_left`), the implicit
node's object via `Node.Label` (`node_labels`); only `Constant.Value` remains (low value; the seed trick applies).

### ~~The one missing seed~~ SOLVED 2026-09-14 15:1x without GUI — the typed-control seed (INDEX row 28)

`To More Specific Class`'s `target class` accepts **any wire of the target type** (NI doc, confirmed by codex), not
only a class-specifier constant. A refnum CONTROL of the wanted class is made by `Terminal.Create Control` on the
`reference` INPUT of a property node already configured to that class; NI ships such nodes in
`examples\Application Control\VI Scripting\Structures\VI Scripting with Structures - <For|While> Loop.vi` (one class
constant → several property nodes). Recipe `tools/recipes/build_oploopcast_v0.py [ForLoop|WhileLoop]`: scratch copy
of the example → delete the constant's wire → `create_control(scratch, node, 0)` (label `reference`) → delete the
other property nodes (a broken VI cannot be COM-saved) → `copy_into(scratch, 'reference', op)` → delete the op's
constant wire → `wire_control(['reference'] → TMSC 'target class')`. A seed casts exactly its class (a ForLoop seed on
a WhileLoop ref errors 1055 downstream; a Loop-class seed would need a Loop-typed input — circular), so one op per
concrete class. The same trick yields any class an NI example or library VI exposes on a property-node input
(Property → `Linked Control`, Constant → `Value`, LeftShiftRegister …) — check the example folder first. The section
below is kept as the record of the GUI route that is no longer needed.

### (superseded) The one missing seed: a retargetable cast (researched 2026-09-14, `archive/peer/2026-09-14-cast-route-research.md`)

Everything still blocked (shift registers, `Loop.Shift Registers[]`, ForLoop parallel instances, `Structure.Tunnels[]`,
implicit property-node linkage, `Constant.Value`) needs a `To More Specific Class` whose target class we can choose.
The class-specifier constant IS scriptable: class `ClassSpecifierConstant`, property **`Class Name` 566EFC02 (r/w)**,
method **`Set Type` 566EF800**, `All Types[]` 566EFC05 (the exact class-name vocabulary). So a copy of any donor can
be retargeted **by string** — once we hold a *typed* reference to its constant. That typed reference needs a cast
itself (circular); `New VI Object` has no documented style for a TMSC or a class-specifier constant; `Open VI Object
Reference` also takes a typed class input. **The circle is broken by ONE manually prepared donor**, prepared once:

1. copy `OpSetIndexMode_v0.vi` → `OpRetarget_v0.vi` (script);
2. **GUI, one act**: right-click its class-specifier constant → *Select VI Server Class* → `Generic ▸ GObject ▸ Constant ▸
   RefNumConstant ▸ ClassSpecifierConstant` (the constant that feeds the TMSC);
3. script: `build_invoke(OpRetarget, "VI Server:ClassSpecifierConstant", "566EF800")` on the TMSC output, a string
   control on its type-name input, `create_indicator` on `Class Name` (566EFC02) for read-back; save.
Afterwards every reader is a copy of a donor + `retarget(copy, class_name)` — no further GUI, ever. Not done today
(unattended: the exception mechanism in CLAUDE.md §3 requires the peer-reviewed enumeration and `lv_gui.ps1
-Exception VerifiedImpossible -Evidence` — this section is that evidence; the act is deferred to a session where the
user is reachable).

## The three tiers

**Tier 1 — exercised repeatedly, trust it.** These ran many times during the 2026-09-12/13 main-VI analysis alone.

| capability | function | evidence |
|---|---|---|
| traverse a class, get uid/pos/owner | `report`, `count`, `uids` | 106 Property nodes + 47 IndexArray + 37 CaseStructure mapped; `Terminal` 5763, `GObject` 10030 |
| per-diagram connectivity with terminal names | `net_map` | ~90 diagrams of the main VI, plus donors and subVIs |
| front-panel labels and values | `fp_labels` + `GetControlValue` | 114 objects of the main VI, 10 of OpReport_v3 |
| top-level node list with labels | `node_info` | donors; **top-level diagram only** |
| open / close / revert / save | `open_panel`, `close_panel`, `revert`, `save` | daily; `revert` recovered a broken op this session |
| object counts and broken state | `exec_state` | fleet health sweep, 42 ops |
| delete an object by class+index | `delete_object` | two deletions landed exactly as predicted |
| clean up orphaned wires | **`remove_bad_wires_scripted`** | VI method `410`, no window needed — **use this one** |

**Tier 2 — works, with a recorded caveat that must be respected.**

| capability | function | the caveat |
|---|---|---|
| wire node→node by terminal name | `wire` | target's panel must be OPEN or the edit is declined **silently**; a found-but-illegal name is also declined silently; branching from an already-wired source needs `branch=True` |
| place a subVI call | `drop_subvi` | panel open first, same rule |
| create a Property node | `build_property` | **only with an ID that actually resolves for that class** — see Tier 3 |
| create an Invoke node | `build_invoke` | same; a wrong/private method yields a node with no method terminals |
| copy a primitive from a donor | `copy_into` / `move_by_label` | the object needs a LABEL in the donor; substitution protocol restores the Move example files afterwards |
| parallel For Loop + kernel + tunnels | `loop_kernel` | supersedes `build_kernel`, whose `tunnel`/`indexing` args are **inert** |
| Case Structure | `build_case` | `Frames` is a string ARRAY of frame names; wrong length → error 1302 behind an 8 s modal |
| connector pane read/write | `conpane`, `conpane_assign` | panel must be open; re-read to prove the assignment landed |
| make current values default | `make_default` | inflates the target's call time by ~9 ms until LabVIEW restarts — configure, restart, *then* time |

**Tier 3 — tried and failed, or never exercised. Do not plan on these without testing first.**

| thing | status |
|---|---|
| `Control.Value` (`633200D`) on a scripted Property node | **FAILED 2026-09-12** — node created, property did not attach: no `Value` terminal, wrong position, Node count 8 → 224. Same call shape as IDs that work. **CAUSE FOUND 2026-09-14 — see below; this is fixable, not a limit** |

## PRIVATE members need the "Allow Private" setters — the builder calls the ordinary ones (2026-09-14)

> **SUPERSEDED the same day (14:xx).** The failures this section reasons about (`OpReportNodes_v0` ×3, the ladders
> reading ExecState 0, "invisible" fresh nodes) were caused by the walker's junk Invokes on an OPEN target
> (`probe_builder_artifact.log`, `walk_junk_probe.log`), not by private members. Every document gap was closed cast-free
> (top section). Kept as history; do not build on it.

**This explains every "the node was created but the member did not attach" failure this project has recorded**, and
it means the scripted route was never closed.

Failures with an identical signature, now unified:

| attempt | date | symptom |
|---|---|---|
| `Control.Value` (`633200D`) on a Property node | 2026-09-12 | node created, **no `Value` terminal** |
| `VI:Get Errors` (`452`) on an Invoke node | 2026-09-09 **and** 2026-09-14 | node created with only `reference out` / `error out` — **no `Errors`, no `Details`** |

In both cases the creation succeeds and the *member selection* is silently refused, leaving a generic
unconfigured node. Public members (`Block Diagram:Remove Bad Wires` 410, `Terminal.Create Indicator` 6349C02)
attach through the very same call and work.

**A HYPOTHESIS FROM PEER REVIEW — three probes have failed to confirm it. Do not treat it as the cause yet.**
(`archive/peer/2026-09-14-private-method-attach.md`.) LabVIEW does expose *separate scripting methods* for
attaching private members, and the fleet's keystone builders plausibly call the ordinary ones — but every attempt
to verify this on the machine has foundered on the reader, not on the answer. See "What three probes actually
showed" below before acting on any of it.

| what to call instead | ID |
|---|---|
| `Invoke.Set Method (Allow Private)` | **6370003** |
| `Property.Set Properties[] (Allow Private)` | **636F406** |
| `PropertyItem.Set Property (Allow Private)` | **6DE8D802** |

Three more points from the same review, all of which change how the fix must be written:

1. **Order matters.** Set `Invoke Node Class Name` (6370402) / `Property Node Class Name` (636F804) **first**,
   then call the Allow-Private setter, then read back `Method` and the terminal arrays to confirm. Setting a
   member before its class is not a valid test of the API.
2. **The setter takes an ID *String*, not a number.** With `Allow Alternate Names? = FALSE` it wants the Unique
   ID string exactly as `All Supported Methods` returns it. A cheap discriminating test is `ID String =
   "Get Errors"` with `Allow Alternate Names? = TRUE` — that separates an ID-format problem from access filtering.
3. **No special VI-reference option is needed.** The private bypass belongs to the *node's setter*, not to how
   the target VI was opened. And three references must not be confused: the VI being edited, the new node, and
   the runtime reference eventually wired into it.

**Fallback if the setter is broken in LabVIEW 2026:** `Create from Reference` makes a perfect scripted copy of an
existing object, and an NI thread specifically about `Get Errors` reports *"If I copy it, it works fine"* — so a
donor VI plus a scripted copy is a real route, not a GUI one.

### Why this matters more than one op

`VI:Get Errors` is the capability that ends **blind debugging**. Three consecutive builds of `OpReportNodes_v0`
failed at `ExecState == 0` with no way to ask LabVIEW *what* was broken; each round was a guess. The INI tokens
(`SuperPrivateScriptingFeatureVisible`, `SuperPrivateSpecialStuff`, `SuperSecretPrivateSpecialStuff`) were
already True throughout — they were never the missing piece.

### What three probes actually showed — and why the question is still OPEN

`tools/recipes/probe_allow_private{,2,3}.py`, 2026-09-14. Each run carried a **control**: the known-good public
method `Terminal.Create Indicator` (6349C02), attempted on the same scratch VI by the same code path.

| run | control | `Set Method (Allow Private)` 6370003 | what it really established |
|---|---|---|---|
| 1 | **FAILED** — "node not found" | "node not found" | **nothing.** The reader was broken; the run's own printed verdict ("BRANCH B, private is unreachable") was void |
| 2 | **passed** — terminals `Create Indicator` | "object exists, reader cannot see it" | reader fixed; but `max_nodes=80` was *below* the object count, so a correct node could have been hidden |
| 3 | **passed** | **1 object created, 0 readable** | the node exists per `report_all` and `net_map` cannot read its terminals |

**The honest verdict is INCONCLUSIVE**, and each run's first draft of that verdict was wrong in a different way:

- run 1 concluded "private is unreachable" from a broken reader;
- run 2 concluded the same from an undersized read window;
- run 2's summary also reported a **spray of ~67 nodes per call**, which run 3 did not reproduce — that figure
  came from misreading a *total* object count as a *delta*, and it is withdrawn.

So the only thing established is about **our reader**: `net_map` / `OpNetInfo_v1` cannot return the terminals of
a node the creator left unconfigured. Whether the private method attaches is **not known**, and neither
"BRANCH A" nor "BRANCH B" may be recorded.

**The control is the reason any of this is trustworthy.** Without it, run 1 would have written "private members
are GUI-only" into this document as a permanent limitation. Every probe of a suspected capability limit gets one
from now on: attempt the *known-good* case through the identical code path, and if it fails, print INVALID and
conclude nothing.

**RESOLVED 2026-09-14 (day loop, cycle 1) — and the resolution overturns the table above.** The three probes
were void for a reason found in code: `net_map` / `OpNetInfo_v1` **does not see nodes created by another op in
the same session** (five refresh attempts, none worked; `tools/bench/probe_stale_nodes.log`), so "no
method-specific terminals" was "the walker never listed the node". The fix was to stop verifying attachment
through the walker and to read the **creator's own error** instead — `OpBuildPN_v1`
(`tools/recipes/build_opbuildpn_v1.py`, `tools/bench/build_opbuildpn_v1c.log`):

| case through v1 | creator error | Outputs | verdict |
|---|---|---|---|
| control `GObject.Position` 632A800 | none | 1 | attached |
| deliberately bogus id `FFFFFFF` | **1077** from `Set Properties[]` | 0 | rejected, loudly |
| `Control.Terminal` 6332006 | none | 1 | **ATTACHED** |
| `AbstractDiagram.SubVIs[]` 6375802 | none | 1 | **ATTACHED** |

So the two cast-free ladders the plan review proposed are open: `Panel.Controls[]` → `Control.Terminal` →
Terminal-class reads (panel wiring, `Is Source?` direction), and `Block Diagram` → `SubVIs[]` → `SubVI.VI Name`
(identity). `build_property()` now drives v1 and **raises** on a creator error or a count mismatch — a
rows-less node can no longer masquerade as success.
⚠️ **But "no 1077" is NOT a verdict that a property attached** (prior-art `A3-iv`, 2026-09-16): the 1077 above
came from a **deliberately bogus** id, while `Control.Value` **633200D** — a *valid* id on the wrong class —
created a node with **no `Value` terminal and no error at all** (`:131` in this file). The robust check is the
**data-terminal-name census** on the created node (`build_opcaseframes_v0.py:49-58`: exactly one data SOURCE
terminal, and its name printed, never guessed). Any "does property X exist on class Y?" test must use that. Whether `Control.Value` 633200D and `VI:Get Errors` 452
were walker artefacts or genuine 1077s is now a one-call question each (an `OpBuildInvoke_v1` with the same
exposure is needed for the Invoke case).

Detail worth keeping: the erdosmiller creator's connector pane has **two terminals named `error out`** —
index 10 is a **sink** (an indicator on it breaks the caller), index 15 is the real output. Names do not carry
direction; `Terminal.Is Source?` (634A003) does.

**And it was the peer gate that produced this.** I was about to write "private methods are GUI-only" into this
document as a permanent limitation; `tools/hooks/guard_peer.py` blocked the next command until the failure was
reviewed, and the review returned a specific, cited fix. The gate's first two firings both caught a real
unreviewed failure.
| `VI.Get Errors` (`0x452`) | **FAILED 2026-09-09** — Invoke node created with only reference/error terminals, with and without the private ini tokens |
| `AbstractDiagram.SubVI From Selection` (`6147ED`, private) | **not attempted.** Reachable in principle (the three private tokens are set in this install) but demoted: native extraction turns a local inside the selection into a control reference + `Value` property node, i.e. it *manufactures* the UI-thread access this project is removing |
| erdosmiller `Create SubVI.vi` | **NOT an extractor.** Pane is `VI Reference`/`Inputs`/`Output Names`; calls only `Get Outputs.vi` and `Wire Inputs.vi`. It places a call to an existing VI — `drop_subvi` already does that |
| creating front-panel objects from nothing | ✅ **BUILT AND MEASURED — no new op needed** (cycles 56–58, 2026-09-20/21). `create_control`/`create_indicator` still work only **from a node terminal**, so the route is: put a carrier node on the `VI → Block Diagram` head with `build_index_array` (`gscript.py:2322`) or `build_property` (`:2194`, `diagram_index` = the live `diag_index(#536)`) → `create_indicator` on one of its terminals → delete the carrier (`delete_object`, `:2240`) → `move_in` the orphaned `ControlTerminal` onto the nested diagram (`build_d1_v0.py:318`). **Two grains decide the outcome, and they pull against each other:** a **SINK** carrier terminal creates **NO wire** but hands the indicator the SINK's own type (Index Array `index` → NUMERIC — that is why 47(d)'s numeric leg came out numeric); a **SOURCE** carrier terminal gives the right type but `create_indicator` is born **wired to the carrier** (whole-VI `Wire` 1905 → 1906), and that wire must be deleted FIRST — `delete_object(target,'Wire',<traverse idx>,verify=True)`, the uid resolved to its index over `report_all(target,'Wire')` because there is **no by-uid form** — or the carrier delete leaves it dangling and the VI sits at `ExecState` **0** with nothing saveable. Artefacts, all `ExecState` 1 at their save point, LV2026: `claudeDev\D1_s3a_boolcarrier_b1_20260921_010034.vi` md5 `7237b2c1…` · `…_b2_20260921_010034.vi` `14805014…` · `…_b3_20260921_010034.vi` `dc14dd00…`. `New VI Object` with a control style from the ring is still never built and is no longer on the path |
| several created `ControlTerminal`s coexisting and relocating in ONE run | ✅ **MEASURED** — `tools/bench/diag_queue_donor2.log:41-55`: two free-standing terminals created and relocated in a single run on this VI, `#23124` (`'index'`, scalar) and `#23493` (the error cluster), each *"is BORN owned by `'TopLevelDiagram'` #536"* (`:44`, `:51`) and each *"`move_in(…)`: returned 8486, **error None**; owner AFTER `'Diagram'` #686"* (`:46`, `:53`). ⚠️ **Scope, so this is not read wider than it is:** donor2 used `create_control` into `#686` and **never wired** either terminal — TWO `wire_indicators` calls against one VI, selecting by two distinct labels, remains **unmeasured** (the labels must differ; read both off the machine and check for a newline and for a duplicate of an existing panel label) |
| re-pointing an existing Property node's property | no op. `build_property` creates; it does not edit. The route is delete + build + rewire |
| reading a diagram constant's value | no op. `Constant.Value` = `634AC00` is registered but **unexercised**; recipe drafted at `tools/recipes/build_opconstvalue.py`, blocked on a `To More Specific Class` donor that was *assumed* to exist and does not |
| `ArraySubset`, `ReplaceArraySubset` as traverse classes | **not class names** — error 109. `IndexArray` is one |
| a WHOLE-VI terminal reader (`OpAllTerms_v0`: one call → term_uid / name / is_source / wire_uid / owner) | 🔴 **NOT BUILT, and all four construction routes are now MEASURED, 2026-09-23.** The reader needs a `To More Specific Class` **inside a loop body**, because `Traverse for GObjects` yields **GObject** refs while `Name` 634A004 / `Is Source?` 634A003 / `Connected Wire` 634A000 are Terminal-class. ONE VARIABLE, on ONE copy: the same `Traverse.References` wire → a `VI Server:GObject` node in the body reads `ExecState` **1**, → a `VI Server:Terminal` node reads **0** (`tools/bench/diag_allterms_donor.log:33` vs `tools/bench/diag_allterms_cast.log:42`) — so the border tunnel is NOT the confound and the node's CLASS is. Routes: **(a) a donor that already owns a TMSC in a loop body — NONE EXISTS**, censused over all **26** op VIs that carry both a Function node and a loop, 54 loop-body diagrams, **0 hits** (`diag_allterms_donor.log:136` + `tools/bench/diag_allterms_donor2.log:150-153`; run 1's 16 unwalked VIs were re-walked on scratch copies after its 6503s proved to be an identity collision with the LIVE op files, 16/16 ExecState 1, 20/20 diagrams walked). **(b) `loop_in` around an existing TMSC — NO**: it creates an EMPTY loop (`gscript.py:1195-1200`). **(c) `copy_by_index` onto a nested body diagram — NO**: the signature has no destination-diagram parameter at all (`gscript.py:1519`); it lands on the Target's TOP-LEVEL diagram. **(S) the cast on a one-row subVI's ROOT diagram, called from inside the loop** (`drop_subvi` any diagram + `conpane_assign` 239A8000 + `exit_loop`, whose `node_class` already defaults to `"SubVI"`) — all helpers exist, and re-targeting `OpLoopCast_v0`'s TMSC #683 to `Terminal` wires up cleanly (seed `'reference 2'` → `target class`, `specific class reference` w348 → the Terminal node's `reference`, Wire 8→9→10, both op errors `''`) but the scratch reads **ExecState 0** (`tools/bench/diag_allterms_retarget2.log:98,114`). That 0 is **not attributed**. 🔴 **The "empty For loop `#331`" explanation first written here is WITHDRAWN the same day** — `archive/peer/2026-09-23-allterms-retarget-es0.md` (claude/hypothesis opus max, ANSWERED 702 s, disposition written) refuted it from our own record: the identical five-step construction run for class `Local` on 2026-09-21 read `1 → 0 → **1** → 0 → 0` (`docs/cycle27-plan.md:2220-2222`), and wreckage cannot let a VI read 1 mid-sequence; `#331` is a PRE-EXISTING loop in a VI that opened at ExecState 1, so emptying it does not unwire N, and `build_opreportall_v1.py:134` is about a FRESHLY CREATED loop. ⚠️ Nor is "both wires landed" evidence: that gate is a wire COUNT, and `:70`'s T2c2 measured a wire that counted +1 with op error `''` and read `Is Broken? TRUE`. The live hypothesis is the SEED's class, plus an unidentified eighth root node `#187`; the prescribed test is five `s.es()` readings inside the existing 77-s file. ⚠️ **AND THE 5-PROPERTY NODE IS ITSELF A DEFECT**: `Name, IsSource, ConnectedWire, UID, Owner` on ONE node breaks `:74`'s rule — an unwired terminal errors at `Connected Wire` and returns **UID and Owner as 0**, on the majority of terminals; `owner_uid` additionally needs a second cast and returns 0 / error 1055 on a `FlatSequenceFrame` owner (`:61`). One property per node, own error chain |

### Traverse class names, tested on the main VI (2026-09-13)

Guessing a class name costs an error 109 and a round trip, so the tested set is recorded here. Counts are the main VI's.

**Valid:** `Local` (8), `Global` (7), `SequenceLocal` (7), `FeedbackNode` (0), `ControlTerminal` (114), `Terminal`
(5763), `SubVI` (98), `Property` (106), `Constant` (301), `IndexArray` (47), `CaseStructure` (37), `Invoke` (1),
`Node`, `Wire`, `Diagram`, `WhileLoop`, `ForLoop`, `Sequence`, `FlatSequenceFrame`, `EventStructure`,
`DigitalNumericConstant` (180), `NumericConstant` (207), `StringConstant` (22), `GObject` (10030).

**Invalid (error 109):** `LocalVariable`, `Variable`, `GlobalVariable`, `PropertyNode`, `SharedVariable`,
`ArraySubset`, `ReplaceArraySubset`. The pattern: LabVIEW's scripting names are usually the **short** form
(`Local`, not `LocalVariable`; `Property`, not `PropertyNode`).

## Some fleet functions CLICK — check before using one in a headless batch (2026-09-13, cost three stalls)

`remove_bad_wires()` reads like a scripting call. It is not: it **drives the menu bar** — moves the window to a known
geometry, then clicks `Edit ▸ Remove Broken Wires`. With no block-diagram window open the clicks land on nothing and
the call burns the full 180 s watchdog. It did that three times in one session before the cause was read out of its own
docstring.

**`remove_bad_wires_scripted()` has existed since 2026-09-07** and calls the VI method
`Block Diagram:Remove Bad Wires` (**410**) directly — no window, no coordinates, no stall. The recipes were simply
still calling the older GUI version.

**The general hazard:** the project's rule is "GUI only where scripting is verified unreachable", but that rule cannot
fire when **the GUI is hidden inside a helper whose name sounds scripted**. Before putting any fleet function in an
unattended batch, check whether its docstring mentions windows, coordinates, `_lv_gui`, or a menu. Known clickers today:
`remove_bad_wires`, `gui_save`.

## GUI error-list reader — `tools/lv_errorlist.py` (2026-09-23, connectivity-map-plan STEP 2)

| what | measured |
|---|---|
| **purpose** | the errors of a BROKEN VI, read from LabVIEW's own Error List (Ctrl+L, keyboard; the arrow/Run toolbar is never clicked). `read(vi_path, out_json)` → `{items:[{index,vi,object,reason,raw,detail}], n_reported, gui_acts, …}` → `tools/bench/errorlist_<vi>_<date>.json` |
| **accessibility: NO** | the Error List (`LVDChild`, title `Error list`) is **fully owner-drawn** — **0** win32 child windows, a **7**-element UIA tree holding only title-bar chrome, **1** MSAA object (the window). 0 rows by either route. `tools/bench/errorlist_test.log` |
| **what WORKS** | capture → locate-on-capture → OCR. The panels are located by colour, never by remembered offsets: dialog grey `#F0F0F0` vs panel (grey fraction is exactly 1.0 outside a panel and 0.0 inside), selection blue `#0078E5`. Row pitch = the highlight's own height (16 px) |
| **the count** | the window's own `"N errors and warnings"` label reads reliably: **14** on the Row-D bed `D1_s3b_m3a3b_rowD_20260922_161040.vi` (= 3 junk `Invoke Node` errors + the 11 severed wires) and **11** on `D1_s3b_m3a_BROKEN_20260922_005732.vi` |
| **OCR engine** | `rapidocr-onnxruntime` (pip, PP-OCR English) — verbatim on every row. `winsdk` Windows.Media.Ocr is installed but the only recognizer language on this machine is **ko**, which mangles Latin (3/41, 37/39, 56/60, 0/25 characters right per row); it is kept only as a no-model-files fallback and says so |
| ✅ **DELIVERED** | `item_count == N` on both VIs — **14/14** on the bed (**11 of them name a wire**, matching the 11 severed uids) and **11/11** on `D1_s3b_m3a_BROKEN_20260922_005732.vi`; every row and every Details text verbatim in the JSON. 86 s / 64 s per VI; 73 / 58 GUI acts, 34-of-35 and 27-of-28 confirmations. Each item carries `row_index` (counting category rows), `rect` and `screen_rect` |
| **stepping** | the highlight is walked one row at a time, its rectangle derived from the highlight's own position and height on the live capture; `{DOWN}` is tried first and **measured not to move it** (`step_mode: "click"` — the dialog's focused control is not the list), so each row is selected by a located click and confirmed on the next capture. At the bottom of the band the list is mouse-wheeled and the scroll distance is measured, not assumed (2 scrolls on the bed, 1 on the second VI) |
| 🆕 **`-Action activate`** | **`-Action focus` AND `-Action clickprobe` DISMISS ANY ESC-CLOSING DIALOG**: `[LVGui]::Focus` (`tools/lv_gui.ps1:243`) and `[LVGui]::ClickProbe` (`tools/lv_gui.ps1:372`) both send **VK_ESCAPE** after activating. Measured twice on the Error List — after either call, `rect`/`shotwin` report "No LabVIEW window whose title contains 'Error list'". **`-Action activate`** (`[LVGui]::Activate`) is that activation minus the Alt tap and minus the Esc: AttachThreadInput + SetForegroundWindow, returning one JSON line with the measured `fg_after` and `ok`. Same gate, same log. Self-test: `activate` then `rect` on the same title — `ok:true`, window still alive |
| **OCR caveat, handled** | a **highlighted** (white-on-blue) row loses its word spaces (`"Thiswireisnotconnectedtoanything"`); the same row drawn unselected reads verbatim. `refine_rows()` re-reads every row from the capture one step later (or earlier) and accepts the replacement only when the two readings agree on alphanumerics — 10/10 and 8/8 rows refined, none left unrefined. It is OFFLINE (captures only, no LabVIEW) and runs at the end of `read()` |

## ✅ `OpAllTerms_v1.vi` — the SEVEN-column terminal reader (2026-09-23, built from the same `_s2` artefact)

| what | measured |
|---|---|
| **delivered** | `claudeDev\OpAllTerms_v1.vi`, md5 `457a8d732a0e219e9aeddbeafbb38c1d`, **15,052 B**, `ExecState` **1** cold. Build `tools/bench/allterms_v1.log` **45 pass / 1 fail** (the fail is H6's expectation list, which did not name the deliverable the run deliberately also wrote — the same bookkeeping row S3 failed). `OpAllTerms_v0.vi` is UNTOUCHED and stays the default reader |
| **the seventh column** | `frame_diagram` = `Terminal.Diagram` **634A002** → that diagram's `UID`. Indicator `Array 9`; the whole map in `tools/bench/opallterms_v1_labels.json`, READ off the machine at build time |
| **why a rebuild and not an edit of v0** | `Terminal.Diagram` is a Terminal property, so it needs **NO new `To More Specific Class`** — but it cannot "sit on the existing Terminal property node A", because adding a property to a property node is **growing a node's terminal count**, one of the exactly two operations with no scripting path at all. So the column is two NEW nodes: `D` `VI Server:Terminal[Diagram]` ← `B.'reference out'` (CHAINED, not branched — a branch adds no Wire object and the gate counts wires) and `DU` `VI Server:GObject[UID]` ← `D.'Diagram'` (a Diagram IS a GObject, so no cast), plus a fifth auto-indexed tunnel. `D`'s output terminal name `'Diagram'` was READ off the machine, not guessed |
| ✅ **FUNCTIONAL, 7 pass / 0 fail** (`tools/bench/allterms_v1_check.log`) | on the D1 bed: **5,811 rows in 13.0 s**; v1's six columns are **IDENTICAL to v0's row for row** (0 differing term_uid); **`frame_diagram` is non-zero on all 1,036 inner/frame rows**; **173 distinct values, all 173 real `Diagram` objects on the bed, 0 stray**; the join is unchanged (1,913 + 7 = 1,920, severed == the 11). Bed, ORIGINAL and v0 byte-unchanged |
| 🟢 **OPEN B IS ANSWERED** | `docs/connectivity-map-plan.md` OPEN B asked where a case/sequence inner terminal's FRAME identity comes from. It comes from this column: the row's `owner_uid` is the TUNNEL, and `frame_diagram` is the frame's own Diagram uid. `tools/allterms.py` picks the label file from the OP's name, so `read_terms(vi, op=OP_ALLTERMS_V1)` returns the seventh column with no other change |
| **the wiki is still on v0** | `tools/wiki_build.py --op v1` switches it; that costs a FULL re-read of every VI (≈14 min for 96), so it is a flag, never a default |

## subVI WIKI — `tools/wiki_build.py` + `tools/vigraph.py` (2026-09-23, connectivity-map-plan STEP 3)

| what | measured |
|---|---|
| **purpose** | one md5-gated JSON per VI — `docs/wiki/subvi/<key>.json` + `docs/wiki/index.json`. Per VI: `file/md5/bytes`, `connector_pane[{index,label,direction,type}]` + `connector_pane_source`, the full terminal table (each row tagged with its LEAF class), the wire join, `graph_summary` (objects/nodes/wires/terminals/diagrams/loops/cases/sequences/locals/globals/`subvi_calls[{node_uid,subvi_name,diagram,path}]`/class census/edge method), `io_paths` (conpane output → the conpane inputs that reach it), `summary` **left empty on purpose** (the one-sentence LLM line is a separate pass, Pre-decided 140), `call_sites_in_main` from `tools/bench/main_vi_subvis.json` |
| ✅ **DELIVERED** | **96 VIs, 851 s, 0 unread, 12.8 MB**; PASS gates **8/0** (`tools/bench/wiki_gate.log`): re-run with nothing changed reads **0**, a touched md5 re-reads **exactly 1**, every copy still byte-identical to its ORIGINAL. Per-VI: min 0.12 s, median 0.91 s, max 214.7 s. LabVIEW handles **33,966 → 34,652** across the whole session (~300 op runs) |
| **the coverage set is 94, not 93** | `background VIs` holds a subfolder, `Tracking kernel (xy_profile)`, with two more VIs — and **both repeat a top-level name** (`Find xy center with sock corr.vi`, `Track xy and profile.vi`), so a basename key would silently merge four VIs into two. The wiki key is the path relative to the copy folder with `\` → `__` |
| **⚠️ one copy had DRIFTED** | `background VIs_COPY\Track N beads one-fold over-kernel-v3.vi` was **17,633 B / 2026-08-26** against the original's **13,377 B / 2010-09-07** — an earlier session let LabVIEW re-save the copy. The ORIGINAL was untouched. The copy was refreshed from it (the drifted one kept in the session scratchpad), and **all 94 are now byte-identical**, which the gate G4b re-checks every run |
| **CONNECTOR-PANE route, and why this one** | `connector_pane_source: "call-node-terminals"` — each subVI is DROPPED ONCE on a dated scratch copy of `claudeDev\EMPTY_v0.vi` (chunks of 12, each scratch deleted) and the CALL NODE's own terminals, read by the same `Traverse('Terminal')`, ARE the connector pane. Verified against the front panel: 4 == 4 and 5 == 5 on the probe VIs. **The call node exposes every slot of the pane PATTERN**, an unassigned slot coming back with an EMPTY name (`Find brightest peak.vi`: 12 slots, 2 real) — blanks are dropped and counted in `connector_pane_unassigned_slots`. `index` is TRAVERSE order, not the pattern's index, and `type` is `""`: no data-type and no conpane-index property is reachable on this route, and **no `VI.Connector Pane` / `ConPane.Connections[]` reader exists in this fleet**. The two TOP-LEVEL targets (main VI S1 copy, the bed) are called nowhere, so they fall back to `"fp-control-terminals"` |
| **the graph model, READ not inferred** (`tools/bench/diag_wiki_probe2.log`) | `Traverse('Terminal')` is INCLUSIVE of its subclasses — 21 rows = `Terminal` 5 + `ParameterTerminal` 8 + `ControlTerminal` 4 + `OverridableParameterTerminal` 4 — and the LEAF class comes only from a `report_all('GObject')` join on `term_uid`. A **front-panel terminal is `ControlTerminal` and its OWNER is the TopLevelDiagram**, so `vigraph` keys those on `term_uid` or every one of them collapses into one node. A **loop tunnel is ONE object** (`LoopTunnel` #311 owns both `OuterTerminal` #310 and `InnerTerminal` #313), so wires + node pass-through already cross a loop border exactly; a **flat-sequence tunnel is not** (outer and inner are separate objects, 116 vs 1,036 on the bed). `GObject.Position` is **(LEFT, TOP)** |
| **`tools/vigraph.py` is an OVER-approximation, deliberately** | edges: wire (exact) · node pass-through (all inputs → all outputs) · shift register right→left and flat-sequence outer↔inner **paired by equal TOP** (a heuristic; the pair counts are reported per VI in `edge_method`, and step 4 replaces them with `Shift Registers[]` / `Inner Terminals[]`) · locals and globals by name within one VI. NOT modelled: case-frame selection, sequence ORDER, read-before-write on a shift register. Safe for "which inputs CAN reach this output"; **not** safe for a rule-1a diff, which is step 4's job |

## ✅ `tools/vigraph.py` STEP 4 — the FULL graph, the diff, and `computation_diff` (2026-09-23)

| what | measured |
|---|---|
| **API** | `build4(terms, objs, loops, labels)` → a TERMINAL-level graph (`out`/`in`/`edges`/`flags`/`method`); `reach4` · `sources_of(…, collapse=True)` · `path` · `terminals` · `wire_terminals` · `diff(A,B)` · `effective_sources` · `computation_diff(A,B)`. The step-3 walker (`build`/`io_paths`/`fp_terminals`, which `wiki_build.py` calls) is UNCHANGED; `reach()` dispatches on the graph shape |
| **keys** | a terminal is `"<owner uid>|<leaf class>|<name>|<ordinal>"` — Pre-decided 137, never a wire uid. Edge kinds: `wire` (exact) · `thru` (a node's sinks → its sources: EXACT for a one-object tunnel, over-approximate for a function — **excluded from `diff`**, being derived) · `sr` · `fs` · `local`/`global` |
| ✅ **gate 9 / 0** | `tools/bench/diag_vigraph_check.py` → `tools/bench/vigraph_check.log` (`BGRUN END rc=0 after 1s`). S1 1,750 nodes / 5,748 terminals / 8,305 edges; bed 1,773 / 5,811 / 8,375. **build 0.07 s, diff 0.02 s, computation_diff 0.66 s** (criterion < 5 s) |
| **shift registers are now EXACT** | each register is assigned to its loop by the v1 column `frame_diagram` of its INNER terminal (10 distinct body diagrams on S1; the frame loop's body #639 holds 14 pairs) and paired right↔left by equal TOP inside that loop. VALIDATED against `Loop.Shift Registers[]` read per loop (`tools/bench/graph_loops_*.json`): 36/36 on S1 and 38/38 on the bed, **equal sets, no loop split across body diagrams**, 0 unpaired. The step-3 whole-VI equal-TOP heuristic over-paired (36 rights → 38 pairs) |
| ⚠️ **flat-sequence tunnels — MEASURED, and not as step 3 assumed** | an FS tunnel's terminals have leaf class **`Terminal`**, not Outer/InnerTerminal; **one FS object carries terminals on SEVERAL frames** (outer #14430 on {13236, 14435}; inner #14007 on {13236, 14037, 14435}); and only **22 of 114** wired outer terminals share a wire with an inner object, so a wire alone does not join them. ~~Rule: same TOP + a COMMON frame (23 of 58 paired)~~ — **REPLACED 2026-09-23 by step 4b, MEASURED** (`tools/bench/diag_fstunnel_pairs.log` 14/0, 172 s): the existing uid readers `OpFsTunnelTerm_v0` (FSOT `OuterTerminal`/`InnerTerminal`) and `OpFsInnerTunnelTerm_v0` (FSIT `LeftTerm`/`RightTerm`) read **58/58 FSOT and 518/518 FSIT, every face clean**; cross-class = error 1055 both ways. Model: an **FSOT is ONE object owning both faces** (== the traverse's rows, 58/58); a **physical inner tunnel is TWO FSIT uids reporting the same two faces swapped** (259 pairs, faces on different frames 518/518), and the traverse files all 4 rows of a pair under ONE uid — 2 faces + **2 non-face terminals** (mostly on the TopLevelDiagram) wired only to each other. The wiki now carries `fs_tunnel_pairs` (S1 + bed, `tools/wiki_build.py --refresh`, terminals byte-equal to before), and `vigraph.build4` makes ONE exact `fs` edge per physical tunnel (sink face → source face, info `faces:<uid>`): **317 edges, 0 unpaired**, FSIT `thru` suppressed; heuristic kept as fallback when the key is absent. Gate `diag_vigraph_check.py` **14/0**; diff(S1,bed) 16/43/9 = step 4's 15/42/9 + one −/+ `fs` pair on FSIT **#7468** (Row D: faces `VISA out` → `Outgoing Handle`). ⚠️ The old limit's "reachability incomplete" was overstated: the `thru` edges already crossed (R1/R2 reach with thru on the heuristic graph); what 4b adds is EXACT, diff-visible FS edges |
| **the relay ASSUMPTION A caught** | `computation_diff` first reported ONE row (#9703's `x` unsourced). The cause was a missing relay, not a computation change: M3a wires a value to an INDICATOR and reads it back through a `Local`. Two rules were added — indicator(sink) → every same-named Local read, and `transparent()`, which walks through a front-panel terminal only when something writes it. After that, **`computation_diff(S1, bed)` = 0 rows**: every M3a substitution keeps each computation input's effective source identical |
| **the 11 severed wires, one by one** | 4 are HALF in the bed (1731, 3947, 7337, 9635 — e.g. w1731 S1 `#4344 'VISA out'` → `#48 'VISA resource name'`, bed source only); 5 are complete in S1 and **termless** in the bed (1893, 2819, 4833, 7388, 11232, all into `#48 ASI_adjust focus-subvi`); 2 (23502, 23540) carry no terminal in either — junk wire objects born in M3a. A terminal-centric reader can only ever see the first group as "severed", which is the step-1 scope call, not a defect |
| **path answers the doc could not give** | `path(#4334 → #48 'VISA resource name')` = `#4334 'VISA out'` →(sr)→ `#4344 'VISA out'` → `#48` — the `VISA out` state carrier of `docs/frame-loop-wire-graph.md`; and `#5058 'cross size'`, listed there as "(boundary: tunnel / shift register)", resolves to `#2580 InnerTerminal` and, collapsed, to `#28147 'x+1'` |

## NEVER point an op at another op VI — it wedges the fleet (2026-09-13, hit twice)

An op is a VI that is *running* while it works. LabVIEW refuses to inspect or edit a VI that is in a run state, so the
moment the fleet is turned on itself it jams:

| what was done | result |
|---|---|
| `net_map(OpFPLabels_v0, 0)` | the target came back **ExecState 0** (broken) — a `revert()` fixed it, disk bytes unchanged |
| `fp_labels()` over the whole `Op*.vi` folder | **error 6500** *"The VI is not in a state compatible with this operation"* on every op, and `OpFPLabels_v0` was left stuck at **ExecState 2 (running)** — which then broke every later call that uses it |

Neither is damage — the on-disk md5 never changed in either case — but **they need different fixes, and the second
one lies about its state:**

| symptom | recovery |
|---|---|
| target reads **ExecState 0** (broken) | **`revert()`** reloads it from disk and it works again |
| the op itself reads **ExecState 1**, yet every call through it returns 6500 | **`revert()` is refused too** — error 6573, *"this property is writable only when the VI is not running"* — so LabVIEW still holds a run reservation that `ExecState` does not report. **Restart LabVIEW.** |

The second is the nastier one: **the status says healthy while the tool is unusable**, so reading ExecState and
concluding "fine" sends you looking in the wrong place. Judge an op by whether a call through it succeeds, not by its
reported state.

**Rule: to inspect an op VI, copy it to a scratch file first and inspect the copy.** A copy is not running, so it
answers normally. This is the same pattern already used for originals, and it costs one `shutil.copyfile`.

## THE bottleneck, measured 2026-09-13: every op run re-traverses the whole target

This is the single most important performance fact about the fleet, and it was not what anyone assumed.

```
one bare op run, SMALL target VI      10.4 ms   (min 9.4, max 15.3)
one bare op run, the MAIN VI         960.8 ms   (min 946.7, max 3017.8)   <- 92x
SetControlValue                       0.069 ms
GetControlValue                       0.062 ms
```

**COM is not the cost.** Set/Get are 70 µs — utterly negligible. The cost is the op *run*, and **it scales with the
size of the target VI**: the same op, the same call, is 92× slower against the main VI than against a small one.

**And it is not the traverse either** — that was the next guess, and it is wrong too. Varying the traversed class by a
factor of 720 changes the time by 23 %:

```
repeat the same index            992 ms
walk different indices           998 ms
class Local      (8 objects)     991 ms
class Terminal   (5763 objects) 1222 ms      <- 720x the objects, +23% time
```

So **~990 ms of every call is FIXED**, and the traversal rides on top of it. The fixed part is opening the target: each
op run does its own `Open VI Reference` on a 473 KB VI with 98 subVI call sites. A small target costs 10.4 ms through
the identical code path.

**That sharpens the fix.** The thing to eliminate is **the number of runs**, not the traversal:

| approach | 626 nodes | difficulty |
|---|---|---|
| cache the VI reference inside the op | 990 ms + 626 × 10 ms ≈ **10×** | needs a shift register (state) in the op |
| **return ARRAYS — one run** | 1 × 990 ms ≈ **600×** | For Loop + auto-indexed output tunnel |
| narrow the traversed class | 23 % | free, already done |

Array return wins by two orders of magnitude, and for a reason worth remembering: the win comes from **paying the
990 ms opening cost once** rather than from touching fewer objects.

### First attempt at building it — where it stopped (2026-09-13)

`OpReport_v3` is small and its shape is right for the change: 5 nodes — `Open VI Reference` → `Traverse` (which
**already produces the whole `References` array** and `# of Refs`) → `Index Array` (which throws all but one away) →
two Property nodes reading `Position` / `ClassName` / `UID` / `Owner`. Wrapping the two Property nodes in a For Loop
fed by `References` would turn one run into the whole answer.

Two obstacles, in order:

1. **`for_loop(tunnels=…)` takes FRONT-PANEL CONTROL NAMES**, not wires. The array to feed in is the `Traverse` node's
   `References` output, which has no control name — so the loop cannot be created with its input tunnel already wired.
   The alternative is: place an empty loop, move the nodes inside, then wire.
2. **Moving a node into the loop breaks the VI.** A probe on a scratch copy placed an empty For Loop (`ForLoop 0→1`,
   `Diagram 1→2` — that part works), then `move_object`'d a Property node into the loop's area: **ExecState went
   1 → 0.** Consistent with LabVIEW reparenting the node while its wires stay outside with no tunnel to cross — but the
   probe's own verification line never printed, so *reparenting is inferred, not proven*. (The probe also used
   `max_nodes=40`, which capped both diagrams at 40 and made the before/after node counts useless — a flaw in the
   probe, not in the tool.)

`exit_loop()` does create auto-indexed **output** tunnels, but its contract restricts `output_names` to terminals on a
node's **connector pane**, so it does not apply to a Property node's outputs.

### RESOLVED the same day — the build route is clear, and "move a node" was never needed

Two probes on scratch copies settled it, and both earlier obstacles dissolved:

```
start                       ForLoop=0 LoopTunnel=0 Wire=17 Property=2 ExecState=1
empty for_loop              ForLoop=1 LoopTunnel=0 Wire=17 Property=2 ExecState=0
build_property INSIDE loop  ForLoop=1 LoopTunnel=0 Wire=17 Property=3 ExecState=0
wire() across the boundary  ForLoop=1 LoopTunnel=1 Wire=18 Property=3 ExecState=1
```

| finding | consequence |
|---|---|
| the loop body is just **diagram index 1** (`diagrams: [(0,''), (1,'ForLoop')]`) | `build_property(..., diagram_index=1)` and `drop_subvi(..., body_index, ...)` place nodes **directly inside** the loop |
| **`wire()` across a loop boundary AUTO-CREATES the tunnel** (`LoopTunnel 0→1`) | no separate tunnel-creation API is needed; `for_loop(tunnels=…)`'s control-name-only limitation stops mattering |
| the tunnel also **restored ExecState 1** | the auto-indexed array supplies `N`, which is why the loop was broken until then |

**A wrong inference is corrected here too.** The earlier probe blamed `move_object` for breaking the VI. It did not:
**ExecState was already 0 immediately after `for_loop`**, because an empty For Loop has no `N`. A broken VI mid-assembly
is the *expected* state, not a failure — the first probe simply never sampled between the steps.

**Build order (the user corrected this — tunnels before nodes):**

1. create the empty For Loop — ExecState drops to 0, which is normal
2. **wire the array into the loop** — the tunnel appears and `N` is resolved
3. build the Property nodes inside the body and wire them to the tunnel's inner end
4. auto-indexed output tunnels → indicators
5. delete the old `Index Array` and the old Property nodes

Doing nodes first leaves the VI broken across more steps, which is exactly what made the first probe misdiagnose
itself. Every operation in that list is now a verified one.

### Build attempted 2026-09-13 — the structure WORKS; one piece is left

Running that order end to end took **8 seconds** (the two earlier attempts burned 20-minute timeouts on the GUI
`remove_bad_wires`). Steps 1-6 each hit their prediction exactly:

```
1 delete old Index Array   IndexArray 1->0, ExecState 0
2 remove_bad_wires_SCRIPTED            Wire 17->14
3 delete the 2 old Property nodes      Property 2->0, Wire->7, ExecState 1
4 empty For Loop                       ExecState 0   (expected: no N yet)
5 loop body = diagram index 1
6 Property built INSIDE the body       Property 0->1
7 wire References across the boundary  LoopTunnel 0->1, ExecState 0->1   <- the array supplies N
```

**State after step 7: `LoopTunnel=1, Property=1, ExecState=1`** — a For Loop auto-indexing the `References` array into
a Property node inside its body, and the VI runnable. **The structure this whole optimisation depends on is
buildable by script.**

Two notes on the "failures" reported by the guards:

- step 7 raised *"wire count 7->9, expected +1"* — but it had **succeeded**. Crossing a loop boundary creates
  **two** wire segments (outside the tunnel and inside it) plus the tunnel. `wire()`'s +1 check does not know about
  tunnels; treat a +2 with a new `LoopTunnel` as success.
- step 8 (`wire_indicators`) raised error 5001 because it wants **connector-pane** names and `Position` is a property
  item; wiring to the `ControlTerminal` directly was then tried and also refused.

**What is actually left, and it is a type problem not a wiring problem:** an auto-indexed output tunnel emits an
**array**, and the donor's `Position` indicator is a **scalar**. The output side needs **array-typed indicators**, which
is the fleet's known weak spot (no op creates a free-standing front-panel object; `create_indicator` only works from a
node terminal). That is the single remaining task for `OpReportAll_v0`.

### ⚖️ S0 CLOSED, 2026-09-19 — the traverse ops are ACCEPTED WITHOUT a `Close Reference`, on measurement

`OpReport_v3.vi`, `OpReportAll_v0.vi` and `OpWireSource_v5.vi` carry a traverse and **no `Close Reference`**
(`docs/REFERENCES.md` §4a). Stage **S0** of the D1 build existed to repair that. Three measured arms closed it
instead, and **no repair was built — no `_vN` op file was created and all three op VIs are byte-identical to what
they were** (`0743701a249b6ac20a5dab9ee676c09c` / `ffcec2c75e92dcad514299ba20e66054` /
`5dc45a04ea5d809f5ca57e9309ed59c5`, gated before and after each run):

| arm | 20 calls of | handles (from call 1) | private bytes | `error 2`? | evidence |
|---|---|---|---|---|---|
| traverse-only | `report_all(Diagram)` (170 matched/call) | +9 | **−0.1 MB** | none | `tools/bench/s0_hygiene_probe_run2.log:121-123` |
| traverse + mutate | `count(Node)` → `report_all(Diagram)` → `OpWireSource_v5` → `build_property` | −19 | **+34.6 MB** | none | `tools/bench/s0b_refleak_profile.log:61-64`; `…profile.json` md5 `b3ddf21fc39735e329c61477dbcac03e` |
| mutate-only | the same loop, three explicit traverse legs removed, `build_property` kept | −12 | **+34.5 MB** | none | `tools/bench/s0b_mutonly_profile.log:61-65`, `:68-71`; `s0b_mutonly_profile.json` md5 `6917c1cba61a403561de55a5ac0f5071` |

Mutate-only and traverse+mutate differ by **0.1 MB**, so the +34.6 MB is the VI growing by 20 Property nodes
(626 → 645 ≈ 1.7 MB each), **not** a traverse leak; traverse-only is flat across 3,400 matched objects. Against the
one S0 criterion (`docs/cycle27-plan.md:453-457` — G-A no `error 2` · G-B handles ±100 from call 1 · G-C private
drift ≤ 5 MB) the ops **pass on traverse-attributable drift**, so `docs/cycle27-plan.md` Pre-decided 25(iv)+27+28
accept them as they are with the measurement as the record. **S0 is closed; S1 is next.**

Three cautions this measurement does NOT license:
- The third arm is not traverse-free — `build_property` calls `report_all(Property)` twice internally
  (`tools/gscript.py:2196`, `:2225`, `:1017-1021`) in **both** arms, which is why they cancel.
- It says nothing about `error 2`'s cause, which returns to OPEN (`docs/cycle27-plan.md` Pre-decided 21(b) as
  amended). "The ops do not leak measurably" is not "the ops cannot exhaust anything": the kernel handle count is
  blind to VI Server refnums (`tools/gscript.py:227-228`), which is why G-C exists beside G-B.
- Building the repair anyway stays legitimate as **rule compliance** (Pre-decided 21(c)); what the measurement
  removes is the claim that it fixes anything.
⚠️ **Flagged to the user**: reading CLAUDE.md's hygiene rule as satisfied by its own stated measurement is the
judgement session's call (Pre-decided 28), and only the user may overturn it.

Because `report()` and friends call the op **once per object**, and each run re-traverses the entire VI, the fleet's
traversal is **O(n²)**:

| sweep | arithmetic | measured |
|---|---|---|
| `report("Node")`, 626 objects | 626 × 0.96 s | **618 s** |
| `report("ControlTerminal")`, 114 | 114 × 0.96 s | 230 s (incl. fp_labels) |
| `net_map` of one 75-node diagram | nodes × terminals × 0.96 s | 741 s for four diagrams |

The arithmetic matches the measurements, so the model is right.

### The fix, and why it is worth doing before the restructuring

An op that **loops inside LabVIEW and returns ARRAYS** turns O(n²) into O(n): one traverse, one run, one round trip.

| sweep | now | batched |
|---|---|---|
| all 626 nodes | 601 s | ~1 s |
| all 114 control terminals | 110 s | ~1 s |
| one diagram's connectivity | minutes | ~1 s |

That is **hundreds of times**, not the ten-fold that was hoped for — and it is more fundamental than the UID-lookup
trick invented earlier the same day, which reduced the *number* of traversals (170 diagrams → 38) without touching the
cost of one. The restructuring needs far more diagram reading than today's session did, so this is paid back
immediately.

*Two corrections recorded with it, because both were beliefs taken from documentation rather than measurement:*
`net_map`'s docstring warns of "one 8 s dialog per node" — **that is stale**; `OpNetInfo_v1` already runs with
automatic error handling off and returns `UID 0` past the end instead of opening a dialog. And the batching idea was
first justified as "fewer round trips"; round trips are 0.07 ms and were never the problem.

## Cost notes that shape plans

- `report()` costs roughly **one second per object**. `Terminal` (5763) is ~90 minutes; `GObject` (10030) longer. Pick a
  narrow class or reach the objects another way.
- `net_map()` costs roughly **8 s per node** (one op run per terminal, with an 8 s dialog per node). Diagram 43 alone
  (75 nodes) is ~10 minutes. **Walking all 170 diagrams does not finish inside any sane deadline** — this is why the
  UID-lookup method below exists.
- **Finding a node without walking diagrams:** one `report()` per class gives every uid; cross-reference
  `tools/bench/diagram_tree_main.json` (diagram → node uids, from Step 0) to place each one; then `net_map` only the
  diagrams that actually hold one. 106 Property nodes were placed in **107 seconds** this way, versus a diagram walk
  that could not finish. `camera_config_scan.py` takes an explicit comma-separated diagram list for exactly this.

### The blind spot in BOTH diagram readers — it has now cost three attempts

> **SUPERSEDED 2026-09-14:** `node_terms` (OpNodeTerms_v0) reads every terminal of every `Nodes[]` node with direction
> and wire; `tunnels` reads the loop tunnels; the node-class census (`report_all(vi, "Node")` → `class`) names
> `ControlReferenceConstant`, `Local`, `Global` … — the "invisible object kinds" below were never invisible to the
> array readers, only to the per-terminal walker's end-of-list heuristics.

`net_map` and the Step-0 diagram tree are built from the same **`Nodes[]`** walk. Diagram 87's tree entry lists exactly
the 14 nodes net_map found, which is the tell. So these object kinds are **invisible to both**:

| invisible to `Nodes[]` | how to reach it instead |
|---|---|
| **Constants** (301 in the main VI) | `report("Constant")` etc. — placement only by POSITION, not by the tree |
| **ControlTerminal** — a front-panel object's terminal on the diagram (114) | same; `where.get(uid)` returns `None` for every one of them |
| Sequence locals (7) | all report `uid 0`; not placeable at all by current means |
| **`FlatSequence` — the whole CLASS** (MEASURED 2026-09-22, `tools/bench/diag_c77_rowd_addr.log`) | `report_all(target, "FlatSequence")` (21 rows on the main VI, with an `owner` column); for its inner tunnels, `OpFsInnerTunnelTerm_v0` **by uid** (`Left Terminal` 1C3A9000 / `Right Terminal` 1C3A9001) |

🔴 **`find_node` returns `found None` for a `FlatSequence`, and the miss tracks the CLASS — never the owner.**
Measured on **all three** of the VI's addressed flat sequences: `#43914` (nested), `#12938` (top-level) and
`#681` (top-level), each over 173/173 diagrams with 0 scan errors, in a sweep that **did** enumerate a
`WhileLoop` on the same diagram — so the reader was working. Two consequences, both binding:

1. **A FlatSequence is never to be addressed through `Nodes[]`**, and **a `Nodes[]` miss on one is never to be
   diagnosed as an ownership problem** — that diagnosis was offered three times before it was measured.
2. **`diag_index(#681)` raises `ValueError: 681 is not in list`, so that call is NOT a membership test** and
   must not be used as one; the exception says the uid is absent from the Diagram census, which is true of every
   node that is not a diagram.

Carried by `docs/cycle27-plan.md` Pre-decided 110. The class reason (`FlatSequence` is a direct child of
`GObject`, never of `Node`) and the dead-end property ids are in `docs/NAMES.md`.

Three separate attempts this session tripped on it: the camera property node's wires appeared to touch nothing (their
far ends were constants/terminals), and two scheduler hunts cross-referenced UIDs that the tree could never contain.

**A caveat on what that fact covers — I over-generalised it once already.** A **VI Global** does surface its own name
as a terminal name (`node[5] uid 6951 ['Rot position']` on diagram 19). I assumed a **front-panel ControlTerminal**
would behave the same and built a whole search on it; net_mapping eleven candidate diagrams for `CycleSchedule`,
`NumCol`, `SubCycle` and friends returned **zero** hits. Globals are Nodes; ControlTerminals are not, which is what the
table above already said. Two different object kinds, one wrong generalisation.

So: to find where a front-panel control is *used*, neither the diagram tree nor `net_map` will name it. What does work
is `report("ControlTerminal")` for the terminal's **position**, then reading the diagram that owns that region — with
the standing warning that nested diagrams do not share a coordinate space, so position gives *candidates*, not an
answer.

Also measured: `fp_labels` returns 114 objects and `report("ControlTerminal")` returns 114 — every front-panel object
has exactly one diagram terminal in this VI.

## EVERY scripting EDIT needs the target's FRONT PANEL open — and "loading the diagram" is NOT a substitute

MEASURED 2026-09-16, `tools/bench/diag_load_vs_editmode.log` (`rc=0 after 112s`), one fresh copy of
`OpFPLabels_v0.vi` per arm, identical raw op (`Traverse 'Property' → Index Array → Generic.Delete 6327400`),
index 0:

| done first | result |
|---|---|
| nothing | `4 → 4` nothing removed, `error out (False,0,'')` |
| **`VI.Block Diagram` (23C) read — the property labviewwiki marks "Loads the block diagram into memory: Yes", no window** | **`4 → 4` nothing removed** |
| `OpenFrontPanel(activate=False)` | `4 → 3`, removed uid 115 |
| 23C-loaded, panel-less, **`GObject.Move`** instead of Delete | `(853,300) → (853,300)` did not move |

Two consequences for anyone writing a new op or recipe:

1. **Call `gscript.ensure_loaded(target)` (or `open_panel`) before any edit** — every mutating wrapper already
   does. Reading the documented load primitive instead does NOT work, so do not "optimise away the window".
2. **The decline is general, not delete-specific.** Delete and Move behave identically, which is why the rule is
   stated over EDITS rather than over one method. Readers are unaffected: `report`/`report_all`/`node_terms`/
   `panel_wiring` counted the target's 4 Property objects correctly in the arms where no edit could land.

**Why the panel works is NOT known** — say "edits need the panel", never "edits need edit mode". Codex
(`archive/peer/2026-09-16-load-vs-editmode-23c-r2.md`): the 23C read ran in a separate op VI that then returned,
and NI closes a top-level VI's references when it goes idle, so that arm may have had no diagram in memory by the
time the delete ran. Deciding it needs one op VI that reads 23C, reads `Metrics:Block Diagram Loaded` (292) and
deletes, with the diagram ref held live by data dependency and no window opened.

**Two failed attempts at a standalone flag reader — read this before building a third** (`tools/bench/
diag_bdloaded_reader.log`, `diag_load_vs_editmode.log`). `build_property('VI Server:VI', [('291',False),
('292',False)])` DOES attach (terminals `PanelLoaded`, `DiagramLoaded`; indicator labels `Metrics:Front Panel
Loaded` / `Metrics:Block Diagram Loaded`), and after that build the donor copy is still `ExecState 1`. The failure
is the WIRE: `connect2` branching `Open VI Reference.vi reference` into that node's `reference` leaves a wire
(uid 467) and `ExecState 0`, and `remove_bad_wires` does not clear it. A wire-count delta of 0 is normal for a
branch and is not the fault.

### `gscript.save()` DOES reach COM `SaveInstrument` on a COPY of the main VI — MEASURED 2026-09-19, the first such save in this project

`tools/recipes/stage_d1_s1.py` phase A (`tools/bench/stage_d1_s1.log:14-18`): with the ORIGINAL held resident
READ-ONLY (`GetVIReference(…, False, 0)`) in the same instance, `g.save()` on an **UNEDITED** byte copy under
`claudeDev` returned 475,141 in **0.28 s, no exception** — and the bytes moved: md5
`2a78e17c449cacdaf5da389818526859` → `e0112963cc1b9e3be29d2bb053ba9029`, **473,317 → 475,141 B (+1,824)**,
saved-version bytes `26 00 80 00` at offset 36 UNCHANGED, the ORIGINAL byte-identical afterwards (`:85`).
The route is the one `docs/cycle27-plan.md` Pre-decided 29 (`:595`) mandates for a stage artefact — save ONLY under preload.
⚠️ **What the save WROTE is an OPEN question, not a capability.** The saved copy then reads `ExecState`
**cold 1 / preloaded 1** where a pristine byte copy reads **cold 0 / preloaded 1** (`:36`, `:57`, `:68`, `:79`;
four separate LabVIEW pids). Its nine pinned structural counts are IDENTICAL to the ORIGINAL's
(`tools/bench/s1_savedcopy_census.log`, 7/0, delta 0 on Diagram/Node/Wire/LoopTunnel/ControlTerminal/WhileLoop/
Local/SubVI/Function), so whatever moved is not object count. Review: `archive/peer/2026-09-19-s1-saved-copy-cold-execstate.md`.

## Harness frictions measured in cycle 22 (2026-09-18) — recorded, NOT remedied (Pre-decided 1: no new devices)

- **`tools/stop_record.py` has no `supersede` / `clear` / `re-point` verb, and `_check:325` refuses on the FIRST
  matching record** — so once a recipe's release is stamped, those exact bytes are the only ones that path can ever
  launch, and `PATH_TOKEN_RE` then refuses even `grep`, `cp`, `certutil` and `py -m py_compile` naming that file.
  The cycle-22 route around this was **not** a gate edit: the patched recipe became `_v1` with its own record
  planted by `stop_record.py write` against the review that read those bytes (`tools/bench/stop_records.json`
  record 3), following the existing `_v0`/`_v1` recipe convention.
- **The permission allowlist has `Bash(py tools/*)` but no `Bash(MATERIAL=1 py tools/*)`, and the PowerShell tool
  refuses `$env:MATERIAL='1'`** — so a non-interactive material session cannot use the documented env-prefix form.
  The marker was declared as a **trailing token** instead, which `guard_bash.MARKER_RE` accepts. Remedy is one
  allowlist entry, deliberately NOT made this cycle.
- **Cosmetic:** `tools/recipes/build_opfstunnelterm_v1.py` still writes its result JSON to
  `tools/bench/opfstunnelterm_v0.json`. It will mislead a later reader; fix it with the next recipe change.

## ⚠️ The DONOR `OpWireSource_v5.vi` SHIPS **NO** ORPHAN WIRES — 894/1356 are PANEL-TO-NODE wires that the recipe's OWN node deletes orphan, and ONE `Remove Bad Wires` at B4 repairs them (2026-09-18)

**This section said the opposite until 2026-09-18 and the machine refuted it.** The wire-side read
(`tools/bench/diag_fstunnel_wireterms_panel_run2.log:36-51`, run 2 = 12/12 gates, rc=0) dumped each wire's own
`Wire.Terms[]` instead of the node-only `OpNodeTerms.wire` column, and both wires turned out fully connected:

- On a **fresh** copy of the donor the orphan set is **EMPTY** — measured twice, once per op, by gate **A0a** of
  the build itself (`tools/bench/build_opfstunnelterm_v2_run1.log:45,97`: *"actual orphan set []; 42 wires;
  ExecState 1"* for FSOT and FSIT), and earlier at `build_opfstunnelterm_v1.py:403`
  (`tools/bench/diag_fstunnel_orphan_timeline.log`, T1/T2 PASS). Each of the two wires has **TWO real
  terminals, one of them a FRONT-PANEL object**:
  - **#894** runs from block-diagram node **#145 `Property Node`, terminal `error out` index 3 (SOURCE)** to the
    panel **INDICATOR `error out 3`, uid 825** (`…wireterms_panel_run2.log:36-41`).
  - **#1356** runs from the panel **CONTROL `index 2`, uid 1334 (SOURCE)** to block-diagram node **#151
    `Index Array`, terminal `index` index 2 (SINK)** (`…wireterms_panel_run2.log:44-50`).
  The panel end has owner `TopLevelDiagram` #3, which is what a front-panel `ControlTerminal` reports
  (`docs/NAMES.md:885`) — so a node-only sweep sees one terminal, calls the other end missing, and reports an
  orphan that is not one.
- **The `[894, 1356]` set is made by the recipe, not shipped by the donor.** It first appears at `_v1.py:442`,
  the first checkpoint AFTER `_v1.py:426-434` deletes nodes #145 and #151 — the very nodes holding those wires'
  diagram ends. `ExecState` goes 1 → 0 at the same point and stays 0 through all six wire sites to B4. Gate
  **A0h/A0a** reads the same thing straight off the machine at B4 on both ops —
  `tools/bench/build_opfstunnelterm_v2_run1.log:81,133`: *"actual orphan set [894, 1356]; 43 wires; ExecState 0"*.
  The pair is therefore a **B4-state measurement that was read as a donor property**. The "the donor ships with
  orphan wires" explanation is **REFUTED and stays refuted**.
- **ONE `Remove Bad Wires` at B4 repairs it, and it costs no terminal.** Gate **A0h** (the `_v2` delta, one RBW
  call at B4 and nowhere else — gate A0f) removes exactly `[894, 1356]`, adds none, drops the wire count by 2 and
  leaves the **terminal count unchanged at 133**, and `ExecState` moves **0 → 1** — reproduced on both ops
  (`tools/bench/build_opfstunnelterm_v2_run1.log:83-85,135-137`; the same Twin-A result earlier in
  `tools/bench/diag_fstunnel_preclean_twins.log`). What the repair does cost is a *wire*, not a terminal: by the
  terminal lists above the indicator `error out 3` (#825) and the control `index 2` (#1334) are left unwired.
- ⚠️ **Line anchors in this section were WRONG when first written (2026-09-18 12:1x) and were corrected the same
  hour** after the prior-art review caught them (`archive/peer/2026-09-18-priorart-fstunnel-v2-preclean.md`,
  finding B4b). A citation is the currency of this project's gates — re-read the log line, do not count offsets
  from a paged `sed` window.

**So a `ExecState 0` on a VI copied from this donor is not automatically the recipe's own wiring.** Check the
orphan pair first. `tools/recipes/build_opfstunnelterm_v2.py` (gates A0a–A0h) is the one place that removes them,
and only after asserting the measured set. ✅ **RUN, and it passed:** run 1 on 2026-09-18 =
**38/38 gates PASS, rc=0** (`tools/bench/build_opfstunnelterm_v2_run1.log`), building `OpFsTunnelTerm_v0.vi` and
`OpFsInnerTunnelTerm_v0.vi` cold-legal in `user.lib\claudeDev`.

## `tools/stagekit.py` — THE STAGE-SCRIPT SKELETON AS A LIBRARY (built 2026-09-22, Pre-decided 103) — ⚠️ HISTORY since 2026-10-09 (card chat-T7): this hand-written section is stale; the CURRENT function list is the generated fn-list block at the end of this file (section `tools/stagekit.py`, `py tools/gen_capabilities.py`), ring recipes as calls: `docs/d1/result-gates.md` PD377

A stage file declares its INPUT, its ROWS and its CRITERIA; the skeleton is no longer retyped. **It builds no
LabVIEW op VI** — every verb is a thin wrapper over one that already exists on disk, lifted from the scripts that
passed (`build_opfsinnertunnelconnect_v0.py` · `diag_c83_connect2x2_r2.py` · `build_d1_m3a3b_d3.py` ·
`stage_d1_s1.py` / `stage_d1_s2_loops.py` / `build_d1_m3a1.py` · `gscript.py`).

| surface | what it is |
|---|---|
| `Stage(input_vi, md5, name, fresh=True, pins=…, deadline_min=…, preload=True)` + `.start()` | pins the ORIGINAL (`2a78e17c…`) and the INPUT **fatally**, takes the claudeDev listing FIRST, restarts LabVIEW, Preloads the ORIGINAL read-only, makes the dated WORK copy, opens it |
| `.gate(label, ok, detail, fatal=)` · `.fact()` · `.row(label, observed, expected)` · `.summary()` | the documented rows `  PASS  ` / `  FAIL  ` / `  FACT  ` (never `**FAIL**`) and `=== GATES: n pass / m fail`. `.row()` is the NON-gate record: it prints an outcome without arming `guard_peer.FAILURE_RE`, which is how a re-cut reproduces a recorded FAIL without blocking the next build |
| `.es(tag)` · `.census(classes=…)` · `.count()` · `.uid_index()` · `.wired_terminals(uid)` · `.net_sources(wire_uid)` · `.broken_wire_count(...)` | readings. `net_sources` is the owner-identity walk (`OpWireSource_v5`, WIRE-addressed); `broken_wire_count` **REFUSES the stage target** unless `allow_mutation=True` — it runs Remove Bad Wires, which deletes |
| `.scratch(suffix)` · `.drop_scratch(p)` · `.discard_work()` | dated scratch copies, deleted in the same run; `discard_work()` marks a diagnostic's work copy as leaving no artefact |
| `.delete_wire` · `.delete_object` · `.move_in` · `.connect` · `.connect_from_wire` · `.fs_inner_tunnel_connect` (v1) · `.fs_inner_tunnel_read` · `.wire_indicators` · `.add_shift_reg` · `.wire_sr` · `.create_local_read` · `.junk_purge()` | the verbs. Each records the op's error column into the JSON and marks a Node census so `junk_purge()` (the measured 1.00 stray `Invoke` per connect call) can diff against it |
| `.expect_is_broken_false(label, reconnect, wire_uid=)` | **42(b)**: the acceptance is asserted on a SEPARATE idempotent re-connect — `wire_delta` 0 **and** `Wire.Is Broken?` 6371004 False — never in the pass that made the connection |
| `.save(broken_ok=False)` | `save_route()` picks: ExecState 1 → scripted `SaveInstrument`; 0 + `broken_ok` → the APPROVED broken-intermediate `gui_save` (CLAUDE.md split-rule 6, evidence *"user 2026-09-22 broken-intermediate save"*); 0 without it → REFUSE. Records md5/size/version bytes; the COLD re-read runs only when ExecState was 1 |
| `.close(expect_files=)` · `K.run(fn, stage)` | refs opened == closed, scratches deleted, the INPUT's md5 unchanged, every pin re-checked, files-left-on-disk, handles, JSON; `run()` guarantees the hygiene tail even on a `Stop` |

**Acceptance, measured:** `tools/bench/selftest_stagekit.py` **32 pass / 0 fail** (no LabVIEW: row format, summary
counting, the md5 pin's fatal refusal, the save-route table, the mutating-reader refusal, an AST check that no
message is built with `%`, and `case_g_constants` — every shipped constant resolves and the ORIGINAL is one
object). Re-cut: `tools/bench/diag_c83_connect2x2_kit.py` — **120 lines against run 2's 595** — reproduces
`diag_c83_connect2x2_r2.log`'s cells R0/R0b/R1 **13 labels for 13**, 28 gates pass / 0 fail, `BGRUN END rc=0 after
119s` (`tools/bench/diag_c83_connect2x2_kit.log`). ⚠️ **Its first run exposed a real library
defect in one second**: `stagekit` had RESTATED the ORIGINAL's path instead of importing
`diag_s2_scaffold.ORIGINAL` (`:81-82`) and restated it wrong, so gate K2 pinned a file that is not there. Fixed;
the lesson is the one this file already encodes — an identity restated in a second place is an untested assumption.

## Connectivity-map STEP 5 — per-item Jev menus over the wiki graph (built 2026-09-23, no LabVIEW)

| surface | what it is | measured |
|---|---|---|
| `tools/jev_candidates.py` `load(key)` · `candidates(G, intent)` · `scope()` · `map_key()` | PYTHON ONLY: every legal (source, sink) terminal pair for an intent `{src, dst, hints, replace}`; filters = direction, sink free (wire 0 or a no-source half-wire, or `replace`), not two frames of one case; columns = scope (same/nested/cousins/unknown + borders), type (wiki `type` is always "" → unknown), cycle (reach4 over-approx). Ends: uid, `{"structure": uid}` (HEURISTIC tunnel group), `{"subvi": name}`. Diagram tree from single-object tunnels (115 parent edges on the bed) | bed load 0.13 s; the 11 M3a-4 intents: 10 give 0 pairs with `replace=False`, w7337 gives 1 |
| `tools/jev_pairs.py` `ask_pair` / `ask_op` / `ask_risk` / `decide()` / `write_record()` | PAIR noul per candidate, code takes the best (act ≥ threshold AND < 2 above 0.70, else `llm`); OP choice ≤ 3 from `OP_MENU` by row classes (CT sink → `wire_indicators`; FSIT sink → `fs_inner_tunnel_connect`; shift register end → `wire_sr`; always `connect_nested`, `connect_from_wire`); RISK noul over vigraph effective sources (proceed only at p ≤ threshold). Thresholds read from `tools/bench/jev_menu_thresholds.json` | PAIR 0.898 / Brier 0.075, acts ≥ 0.70 · OP 0.55 flag only · RISK 0.571 flag only (`tools/bench/jev_menus_step5.log`) |
| `tools/jev_chain.py` `build_chain()` · `true_next()` · `direct_successors()` | layer 1: "is subVI X the next link after Y toward Z?" one candidate at a time over the subVIs of the Y diagram's scope; ground truth `true_next` from the graph (direct subVI successor that reaches Z) | CHAIN 0.807 / Brier 0.128, recall 2/13 |
| `tools/bench/decision_<stage>.json` | the record step 6 reads: intents, every candidate (keys = node uid + terminal name), per row `pair_p, op, op_p, risk_p, action (wire/llm/skip), decided_by (jev/python), evidence`, `jev_calls`, cost | `decision_m3a4.json`: 10 skip / 1 llm / 0 wire, 15 calls, 8.5 s |

## ✅ CallLibrary (CLFN) property READER + WRITER — `OpCLFNThread_v0` / `OpCLFNThreadSet_v0` (2026-09-26, cards 92-1 / 92-2)

| op | what | measured |
|---|---|---|
| `claudeDev\OpCLFNThread_v0.vi` md5 `a7308101…` (labels `tools/bench/opclfnthread_labels.json`) | READ `Any Thread?` 636D403, `Library Path` 636D400, `Calling Convention` 636D402 of `Traverse('CallLibrary', index)` + a `GObject.UID` echo. Built by the typed-control-seed route from donor `OpSetIndexMode_v0` (`tools/bench/diag_c92_clfn_thread.py`) | self-test 9/0 incl. cold ES 1; 12/12 uid echo on t0 (`diag_c92_clfn_thread_r2.log`) |
| `claudeDev\OpCLFNThreadSet_v0.vi` md5 `d084d43d…` (labels `tools/bench/opclfnthreadset_labels.json`, value control `Any Thread? 2`) | WRITE 636D403 (a write PN branched off the TMSC output; its `error out` feeds the read PN's `error in`, so the SAME run reads the value back after the write). Built in `tools/bench/diag_c92b_anythread.py` | negative case index 12 → `error 1055`; toggle False→True read back; 20 calls handles flat (54,510 → 54,510); 12/12 on the copy, re-read by the separate reader warm and cold (`diag_c92b_anythread.log` 23/0) |

**Fact behind it:** `gscript.build_clfn(reentrant=True)` goes to NI's import-wizard `Reentrant` global and leaves 636D403
**False** (UI thread) on every node it creates (`tools/bench/t0_clfn_thread_92.json`); a CLFN meant to run in any thread
must be SET afterwards with `OpCLFNThreadSet_v0`. Not yet wrapped in `gscript.py` (use `run_op` in `diag_c92b_anythread.py`).

## ✅ ForLoop parallelism WRITER — `OpForLoopParSet_v0` / `gscript.loop_par_set` (2026-09-26, card 95-4)

| op | what | measured |
|---|---|---|
| `claudeDev\OpForLoopParSet_v0.vi` md5 `868e1f42…` 15,390 B (labels `claudeDev\OpForLoopParSet_v0_labels.json`; value control `Is Parallelism Enabled?`) | WRITE ForLoop `Is Parallelism Enabled?` 6362004 on `Traverse(Class Name, index)` of `vi path` (donor `OpLoopCast_v0`: ForLoop-typed TMSC #683), then READ 6362004 + `Number of Static Parallel Instances` 6362005 through the write PN's `reference out`; write `error out` → read `error in`, so the read runs strictly after the write. P is NEVER written. Built by `tools/bench/diag_c95_opbuild.py` (plan `tools/bench/par1359_95_opplan.json`, dry+prerun PASS on `tools/bench/graph_oploopcast_v0_c95.json`) | build 31/0, ES 1 warm and COLD (`tools/bench/diag_c95_opbuild.log`); self-test 18/0 on a byte copy of `HARNESS_copyloop.vi` (`tools/bench/selftest_opforlooppar_v0.log`): set True → op True + separate reader `OpLoopCast_v1` True, set False → False/False, `WhileLoop[0]` and `Diagram[0]` → `error 1055` (refused, loop unchanged), 20 calls handles 34,235 → 34,229 after 20 s idle |

`gscript.loop_par_set(target, index, enable, class_name='ForLoop')` → `{loop_uid, parallel_enabled, static_instances, err}`;
the edit is IN MEMORY on `target` (the caller saves or discards). ⚠️ Enabling by this property on a loop never configured
in the dialog leaves `static_instances` **0** (harness #239: ES stays 1) — what LabVIEW compiles for P = 0 is NOT measured.

## ✅ Card 97-3 — the display-gate tools T1–T5 (2026-09-26, `docs/d1-loop12-17-split-plan.md` Pre-decided 206(d))

All in `tools/gscript.py` section "CARD 97-3". Ops built by `tools/bench/diag_c97_tools_opbuild.py` (typed-control-seed
route of `diag_c92_clfn_thread.py`, **18/0, cold ExecState 1**, `tools/bench/diag_c97_tools_opbuild.log`); label map
`tools/bench/diag_c97_tools_oplabels.json`. Self-test `tools/bench/selftest_c97_tools.py` on a NEVER-SAVED scratch of
`D1_s1_copy.vi` (For #1359 body 7911 in While #637 body 639): **33 pass / 1 fail** (`tools/bench/selftest_c97_tools.log`,
line refs `:n` below; the fail = cold first-load handles, closed by `tools/bench/diag_c97_tools_handles.log` 13/0). Level:
STRUCTURAL (the scratch was never run).

| tool | Python API | op / route | measured |
|---|---|---|---|
| T1 nested case | `case_in(target, diagram_uid, location, selector_label, frame_names=("0, Default","1"), position=None)` → `{case, owner_class, owner, names, frames, err}` | composition: `build_case`'s body on the top level (selector = a TOP-LEVEL panel control by label; one-run `uids()` snapshots instead of per-object `report()`, ~40 s/call on the main VI) → `OpMoveIn_v0` into Diagram #uid (severs the selector wire) → `OpOwnerChain_v1` → `case_frames` | case #22989 owned by 7911, #9083 by 639, 2 frames each owned by the case (`:11-27`); NEG unknown diagram → `ValueError` before any edit (`:30`); 20 calls handles 51,560 → 51,555 (`:51`) |
| T1 reader | `case_frames(target, case_uid)` → `{echo, names, frames, err}` | NEW `claudeDev\OpCaseFrames_v1.vi` md5 `5770209c…`: Traverse(`Class Name`,`index`) → TMSC(CaseStructure seed) → `Frame Names` 6365002 → `Frames[]` 6363801 → IA[`index 3`] → `GObject.UID`; uid echo `UID 2` | names come back PADDED: `' 0, Default '`,`' 1 '`; after a Boolean is wired into the selector `' False '`,`' True '` with the SAME frame uids in the same order — frame "0, Default" → False, "1" → True (`:17`, `:28`) |
| T2 node set → case frame, wires kept | `move_into_frame(target, frame_uid, members, spot)` → `{edges_before, edges_after, missing, extra, new_tunnels, census_*, ops, owners_after}` | composition, per edge class: node→node `connect_nested_v1` · const→node `wire_const` · ctl→node `wire_control` (label, frame diagram) · node→indicator `wire_ctlsink` · loop-tunnel OUTER→node `wire_tunouter` · loop-tunnel INNER→node `connect_from_wire` on the original wire · 2nd sink of a crossed source branches from the new inner wire (one tunnel per source) · node→loop-tunnel INNER = `connect_from_wire` INVERTED. Members are moved ONE AT A TIME and re-wired at once; junk Invokes purged | PD206(b) set, 10 objects, 16 edges: table (src term uid → sink term uid, new tunnels collapsed) EQUAL, census: only SelectorTunnel +4 (`:70-119`); NEG member on another diagram → `ValueError`, Wire count unchanged (`:124`). handles **+113** over this ONE COLD invocation (the only FAIL, `:120`) = FIRST-LOAD cost of the op VIs, measured by the review's test (`archive/peer/2026-09-26-c97-t2handles.md` §4, `tools/bench/diag_c97_tools_handles.log` 13/0): first calls +73 (T3 cold) / +18 / +14 / +74, then T2 WARM **−13** with the table equal again; 20 idempotent `OpConnectNested_v1` **+1**, 20 `OpConnectFromWire_v0` **−1**, 5 `OpAllTerms_v0` **−4**. ⚠️ private bytes still climb ~0.5–0.75 MB per connect call (585.8 → 595.5 → 610.4 MB) — error 2 hit at ~695 MB in cycle 85 |
| T3 control / indicator terminal | same `move_into_frame` (a member uid may be a `ControlTerminal`) | allterms reports a panel terminal with owner class `Diagram` and term uid == the object uid | ctl #8476 `Exp Baseline` → #8764 `y` re-made by `wire_control` (`:85`); case B: #11261 + indicator #8323, 3 edges equal, +2 tunnels, handles +36 (`:133-147`); NEG (`:151`) |
| T2' post-move gate (card 98-2, PD207(c)) — **SUPERSEDED by T2'' (card 98-3): the termless-by-uid delete and `_keep_orphans` are gone** | `move_into_frame(..., expect_broken=False, _keep_orphans=0)` adds `{exec_state, orphans_deleted, orphans_kept, orphan_owners, termless_before, termless_left, termless_total, wires_gone_unexpectedly}`; raises `MoveIntoFrameBroken` (`.result` = the dict). Reader `wire_health(target, rows=None)` → `{wires, wired, termless, exec_state}` | after the moves: every wire present WITH a terminal before the move, termless now (`all_wire_uids` − wired uids of `read_terms`) and owned (`owner_of`) by the case's diagram or the frame is deleted BY UID (`delete_object('Wire', live index)`, as `del_wire`); never a whole-VI Remove Bad Wires. Raises on ExecState ≠ 1 or a termless wire left unless `expect_broken=True`; a declined delete or any other wire gone ALWAYS raises. `_keep_orphans` = self-test negative case only | why: `diag_c98_fgate.log:364-480` (9 severed old wires = the whole ExecState 0). Self-test `tools/bench/selftest_c98_stage.log`: on case A deleted exactly the 8 orphans of 98-1 (all on Diagram 7911), 0 termless left, edges 16 = 16 (`:302-312`) — but ExecState stayed **0** after A + UseDefault (`:321`): termless-orphan deletion is NOT sufficient; suspected loose ends on surviving wires (`archive/peer/2026-09-26-c98-selftest-f4e.md`). NOT accepted; negative case not reached |
| T2'' precondition + Remove Bad Wires gate (card 98-3, PD208(c)) | `move_into_frame(target, frame_uid, members, spot, log=None, expect_broken=False, _skip_rbw=False)`; post step also callable alone: `move_into_frame_finish(target, frame_uid, r, log=None, expect_broken=False, _skip_rbw=False)` (r = a `MoveIntoFrameBroken.result`, which keeps the private pre-move keys until a call succeeds). Result adds `{exec_state_before, rbw_ran, rbw, rbw_removed, rbw_new_uid_removed, rbw_appeared, wires_before_rbw, wires_after_rbw, lost_edges, lost_nonmember_since_move, nonmember_edges_before, missing/extra (post-RBW; pre-RBW kept as missing_pre_rbw/extra_pre_rbw), termless_before, termless_left, termless_total, exec_state, expect_broken}` | (1) `exec_state` read BEFORE ANY EDIT, ≠ 1 → `MoveIntoFrameRefused` (a `ValueError`); (2) move + re-wire unchanged (T2); (3) whole-VI `read_terms` + `all_wire_uids`, then **VI-level** `remove_bad_wires_scripted` (VI method 410, `OpRemoveBadWires_v0`) — LabVIEW has NO per-diagram Remove Bad Wires (`archive/peer/2026-09-26-c98-rbw-scope.md` §1: AbstractDiagram's only wire method is `Remove Wire Loose Ends` 6375409; Diagram's none), and the precondition makes VI scope = "the move's own breaks" — then read again. HARD raise (even with `expect_broken`): a removed uid not present before the move · any (src term → sink term) pair lost across RBW · any pair with no member endpoint that existed before the move gone · a wire appeared · moved-edge table ≠ before · a termless wire left. SOFT: ExecState ≠ 1 after (waived by `expect_broken=True`). `_skip_rbw` = self-test negative case only | `tools/bench/selftest_c98_rbw.log` (48/2, stage path on a never-saved S1 scratch): NEG `_skip_rbw` → raised, 8 termless left (`:355-358`); PRECONDITION on that ExecState-0 state → `MoveIntoFrameRefused`, Wire 1915→1915, Node 628→628 (`:359`); finish → RBW removed exactly the 8 pre-existing termless wires [7931 9407 15847 24106 28139 28443 28509 33062], 1915→1907, 0 pairs lost (0 of 2212 non-member), edges 16 = 16 (`:360-370`). ⚠️ **ExecState stayed 0 after A + RBW + UseDefault (`:383`, F4e FAIL) — the same as the uid delete (98-2), so in-memory RBW does NOT make the post-A state executable. The gates are measured; the verb is NOT accepted as the stage fix.** 20-call handle test not reached (stopped at F4e) |
| T4 label writer | `set_control_label(target, panel_index, text)` → `{text_back, err}` (`panel_index` = `panel_wiring` row); default: `set_default_in_memory(target, label, value, probe)` | NEW `claudeDev\OpLabelSet_v0.vi` md5 `985f71bb…` = `OpFPLabels_v0` + `Text.Text` 632D800 WRITE on a branch of `Control.Label`, then a READ chained by reference+error. Default = `OpMakeDefault_v0` (ALL controls) + ActiveX `ReinitializeAllToDefault`, NOTHING saved | 20 writes read back, handles 51,749 → 51,767 (`:159-160`); `Force graph: update every N frames` read back by the op AND `panel_wiring` (`:161`); NEG index past the end → `error 1055`, no label changed (`:162`); default 9 read back after a reinit (5 in between) (`:163`) |
| T5 use-default setter | `tunnel_use_default(target, tunnel_uid, value, cls="SelectorTunnel")` / `tunnel_use_default_at(target, cls, index, value)` → `{echo, before, after, err, uid_err}` | NEW `claudeDev\OpTunnelUseDefault_v0.vi` md5 `d823b5ef…`: TMSC(ConditionalTunnel seed) → READ 5D251C00 → WRITE → READ, ordered by reference+error; uid echo | 20 alternating writes read back, `before` == previous `after`, on S1 output tunnel #1034, restored; handles 51,726 → 51,725 (`:153-154`); case A's 4 new tunnels → True (`:156`); NEG LoopTunnel → `error 1055` (`:157`) |

Measured on the way (each first-time): a wire whose every sink was on the moved node SURVIVES the move as a stub and
still sources `connect_from_wire` (w31128 → #29009 `right rank`, `:93`); `Terminal.Connect Wire` invoked on a node's
OUTPUT with `Wire Source` = a loop tunnel's INNER sink terminal on the stub makes the out-crossing (w11374, `:114`); a
moved case node's `Terminals[]` = `[(0, 'index', sink, 0)]` — the selector terminal carries the NAME of the control that
fed it (`:15`). The route that 97-2 planned for T1 (`loop_in` fixture) needs an existing source object:
`archive/peer/2026-09-26-c97-loopin1055.md`.

## ✅ Card 106-3 — offline stage checks, pure Python (2026-09-27, PD216(g) / PD217(d); no LabVIEW)

- **`stagesim.cdiff_inputs(plan, st)`**: the FINALIZE cdiff graph of a plan whose context names the S1 wiki (`s1_key` /
  `fs_pairs_wiki`) is built with `JC.node_labels_default()` + the wiki `fs_tunnel_pairs` — the E3 inputs
  (`stagexec.e3_graph`); the ops keep their inputs, so step states are unchanged. Finalize also accepts the PD217(c)
  CLASSED rule (`stagesim.open_rows_classed`: end rows == class 1-3 rows, class-4 sources == S1's). Re-sim of
  `plan_disp.json`: end rows 6 == the class 1-3 rows, step 0 has 0 rows (was 15), 58/58 step states identical
  (`tools/bench/diag_c106c_resim.log`, `tools/bench/sim/c106c_resim_summary.json`).
- **`stage_prerun` X9** — every dispatched op whose verb holds a precondition on the work file
  (`stagexec.ROUTE_PRECONDITIONS`, `precondition_failures`: `copy_in` needs work == `gscript.MOVE_DST`) is checked against
  the Stage the dry run built. **X10** — predicted private-MB peak from the RECORDED per-op meter of an earlier run of the
  same recipe (`stagexec.meter_rows_from_log`, `mem_predict`; same mode first, else a fresh-start record shifted) must be
  < `MEM_STOP_MB`; no covering record = UNMEASURED (reported, passes). Self-test `tools/bench/selftest_stage_prerun_c106c.py`.
  **Card 106-5 (PD219(c)):** X10 fails at a predicted checkpoint **>= 690 MB** (`stage_prerun.X10_FAIL_MB`; 690.0 fails,
  689.9 passes); UNMEASURED prints `X10 WARN unmeasured` and puts it in the RESULT line's `first_fail` of a PASS
  (`result_first`; result-line/1 has no other text field). Without `--graph` the dry takes the recipe's **plan base graph**
  (`plan_base_graphs` -> `find_graph(md5, plan_graphs)`, pinned by the plan's `base.md5`; `plan_disp` -> `par1359_95_graph.json`).
  `launched_py` splits on newlines (after joining `\`/backtick continuations); `launched_plan_runs` does not yet.
  Self-test `tools/bench/selftest_stage_prerun_c106e.py`.
- **Recipe helpers in `stagexec`** (moved from `tools/recipes/stage_d1_disp.py`, now 90 lines): `DryPlanBE`, `w0_wires`,
  `report_stop`, `log_step_diffs`, `b1_gate`, `part_a_gates`, `w1_rbw`, `e3_gate`, `kill_labview_at_exit`.

## The rule this file encodes

Before a plan depends on a capability, it must name **where that capability was last exercised**. If the answer is
"it is in the list" or "the library ships a VI called that", the plan has an untested assumption in it and should say
so out loud — as a gate, with a cheap test scheduled before the work that depends on it.

<!-- GENERATED fn-table BEGIN (tools/gen_capabilities.py - do not edit by hand; regenerate) -->

## Scripting functions - generated from code (card chat-F2)

Outcome of every call: `ok | no_output | failed | timed_out` (tools/fncontract.py). Contract column = the declared postconditions `[measure, on_fail]` or `none - <reason>`. Record = tools/bench/fn_records/ (fresh-pass only while the function's source md5 equals the record's). 152 rows; records: fresh-fail 3, fresh-pass 59, none 66, planned 24.

| function | arguments | outcome contract | record | source |
|---|---|---|---|---|
| `gscript.add_shift_reg` | target, loop_index, y_position=120, class_name='WhileLoop' | new_register == 1 [result, raise] | fresh-pass | tools/gscript.py:940 |
| `gscript.build_case` | target, location, selector_name, input_names=(), frame_names=('0, Default', '1') | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:3498 |
| `gscript.build_clfn` | target, location, dll, fn, flat_hex, calling_convention=0, reentrant=True | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:3317 |
| `gscript.build_index_array` | target, location, source_terminal_index=0 | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:2892 |
| `gscript.build_invoke` | target, cls, method_id, location, diagram_index=0 | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:2692 |
| `gscript.build_kernel` | target, loop_at=(4000, 300), parallel=4, tunnel='Array of cal clusters', bead_vi='Track 1 of N bds xyz-kernel-reentra... | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:2615 |
| `gscript.build_property` | target, cls, props, location, diagram_index=0 | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:2727 |
| `gscript.case_frame_wire` | target, case_uid, frame_index, src, dst | new_wire == 1 [result, raise] | planned | tools/gscript.py:5187 |
| `gscript.case_frames` | target, case_uid | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | none | tools/gscript.py:3666 |
| `gscript.case_in` | target, diagram_uid, location, selector_label, frame_names=('0, Default', '1'), position=None | new_objects == 1 [existing-raise, existing] | planned | tools/gscript.py:3695 |
| `gscript.case_inner_face` | target, tunnel_uid, frame_index | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | none | tools/gscript.py:5166 |
| `gscript.case_wired` | target, diagram_uid, src_node_uid, src_term, pos=(40, 40), donor=None | new_objects == 1, selector_wired == 1 [existing-raise, existing] | planned | tools/gscript.py:5078 |
| `gscript.close_panel` | target | none - session / editor state (panel, load, save, revert); no countable diagram effect | fresh-fail | tools/gscript.py:1615 |
| `gscript.connect2` | target, diagram_index, sink_node, sink_term, src_node, src_term | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:3254 |
| `gscript.connect_ctl` | target, panel_index, node_index, terminal_index | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:1312 |
| `gscript.connect_ctl_ind` | target, sink_panel_index, src_panel_index | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:1338 |
| `gscript.connect_term_uid` | target, sink_uid, src_uid | new_wire == 1 [result, raise] | fresh-pass | tools/gscript.py:5141 |
| `gscript.connect_terminals` | target, sink_node, sink_term, src_node, src_term | new_wires >= 1 [result, record] | planned | tools/gscript.py:3028 |
| `gscript.conpane` | target, max_terminals=32 | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | none | tools/gscript.py:3365 |
| `gscript.conpane_assign` | target, control_label, terminal_index | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:3422 |
| `gscript.const_class_index` | target, uid | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | none | tools/gscript.py:4520 |
| `gscript.const_indicator_on_diagram` | target, diagram_uid, donor, label, pos=(40, 40) | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:4571 |
| `gscript.copy_by_index` | donor, cls, index, target, expect_uid=None, finish=None | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:1837 |
| `gscript.copy_into` | donor, label, target, prepare=None | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:1757 |
| `gscript.count` | target, cls | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | fresh-pass | tools/gscript.py:1363 |
| `gscript.create_const_loop_term` | target, kind, index, value=None, term_index=0 | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:2983 |
| `gscript.create_control` | target, node_index, terminal_index | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:2930 |
| `gscript.create_control_nested` | target, node_uid, terminal_index, value=None | op_err == 0 [result, record] | none | tools/gscript.py:4349 |
| `gscript.create_indicator` | target, node_index, terminal_index | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:2958 |
| `gscript.create_indicator_nested` | target, node_uid, terminal_index | op_err == 0 [result, record] | fresh-pass | tools/gscript.py:4166 |
| `gscript.create_indicator_on_const` | target, const_uid, label=None | op_err == 0 [result, record] | fresh-pass | tools/gscript.py:4529 |
| `gscript.create_local_read` | target, panel_index, dest_diagram_uid=None, position=(40, 40) | new_locals == 1, op_err == 0 [result, record] | fresh-pass | tools/gscript.py:4707 |
| `gscript.create_local_write` | target, panel_index, dest_diagram_uid=None, position=(40, 40) | new_locals == 1, op_err == 0 [result, record] | fresh-pass | tools/gscript.py:4715 |
| `gscript.create_primitive_nested` | target, diagram_uid, prim_name, pos, donor=None | new_objects == 1 [existing-raise, existing] | fresh-pass | tools/gscript.py:4790 |
| `gscript.delete_by_label` | target, label, allow_broken=False | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:2023 |
| `gscript.delete_object` | target, cls, index, verify=True | removed == 1 [inline, raise] | fresh-pass | tools/gscript.py:2808 |
| `gscript.drop_subvi` | target, subvi_path, diagram_index, location | none at this level - returns only the run time; the new SubVI is measured by the caller (stagexec create 'subvi': SubVI uid diff == 1) | fresh-pass | tools/gscript.py:1583 |
| `gscript.ensure_loaded` | target | none - session / editor state (panel, load, save, revert); no countable diagram effect | fresh-pass | tools/gscript.py:1626 |
| `gscript.ensure_move_files_pristine` |  | none - session / editor state (panel, load, save, revert); no countable diagram effect | none | tools/gscript.py:1965 |
| `gscript.exec_state` | target | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | fresh-pass | tools/gscript.py:2457 |
| `gscript.exit_loop` | target, node_index, output_names, diagram_index, node_class='SubVI' | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:2079 |
| `gscript.exit_while` | target, stop_control, diagram_index, node_index=0, output_names=(), node_class='SubVI', shift_names=() | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:1441 |
| `gscript.find_at` | target, cls, pos, tol=40 | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | none | tools/gscript.py:1419 |
| `gscript.for_loop` | target, location, tunnels=(), indexing=(), parallel=0 | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:1568 |
| `gscript.fp_labels` | target, max_n=200 | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | none | tools/gscript.py:3058 |
| `gscript.fs_add_frame` | target, fs_uid, ref_index, after=True | new_frames == 1 [existing-raise, existing] | planned | tools/gscript.py:4933 |
| `gscript.fs_frames` | target, fs_uid, max_frames=200 | echo == fs_uid [existing-raise, existing] | fresh-pass | tools/gscript.py:4910 |
| `gscript.gui_save` | target | none - session / editor state (panel, load, save, revert); no countable diagram effect | none | tools/gscript.py:2470 |
| `gscript.hygiene_run` | op_path, workload, source, total=2000, per_round=100, recycle=True, check=None, warm=None, card='', log='', workload_... | none - session / editor state (panel, load, save, revert); no countable diagram effect | none | tools/gscript.py:366 |
| `gscript.loop_cast` | target, index, class_name='ForLoop' | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | none | tools/gscript.py:869 |
| `gscript.loop_diagram` | target, loop_pos, min_margin=4.0 | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | none | tools/gscript.py:1400 |
| `gscript.loop_face_index` | target, diagram_uid, loop_uid, face_uid | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | none | tools/gscript.py:2362 |
| `gscript.loop_in` | kind, target, diagram_index, location, src_cls=None, src_index=0, src_names=(), indexing=(), parallel=0 | new_loops == 1 [result, raise]; PRE src_present == 1 (measured when the call raised) | fresh-pass | tools/gscript.py:1513 |
| `gscript.loop_kernel` | target, location, control_names, kernel_path, input_names, parallel=4 | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:2162 |
| `gscript.loop_par_set` | target, index, enable, class_name='ForLoop' | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:912 |
| `gscript.main` |  | none - session / editor state (panel, load, save, revert); no countable diagram effect | none | tools/gscript.py:2664 |
| `gscript.make_default` | target, values=None | none - session / editor state (panel, load, save, revert); no countable diagram effect | none | tools/gscript.py:3456 |
| `gscript.move_by_label` | donor, label, harvest_to=None | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:1919 |
| `gscript.move_into_frame` | target, frame_uid, members, spot=(0, 0), log=None, expect_broken=False, _skip_rbw=False | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:3846 |
| `gscript.move_into_frame_finish` | target, frame_uid, r, log=None, expect_broken=False, _skip_rbw=False | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:3877 |
| `gscript.move_object` | target, cls, index, position | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:2869 |
| `gscript.move_out` | target, diagram_index, node_index, position | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:3295 |
| `gscript.net_map` | target, diagram_index=0, max_nodes=200, max_terms=40 | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | none | tools/gscript.py:3123 |
| `gscript.new_since` | target, cls, before | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | none | tools/gscript.py:1382 |
| `gscript.node_info` | target, max_n=400 | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | none | tools/gscript.py:3080 |
| `gscript.node_labels` | target, diagram_index, strict=True, **controls | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | fresh-pass | tools/gscript.py:830 |
| `gscript.node_rank` | target, uid | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | none | tools/gscript.py:2922 |
| `gscript.node_terms` | target, diagram_index, node_index | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | fresh-pass | tools/gscript.py:1153 |
| `gscript.node_terms_uid` | target, diagram_index, node_index | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | fresh-pass | tools/gscript.py:1208 |
| `gscript.node_terms_uids` | target, diagram_index, node_index | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | none | tools/gscript.py:1229 |
| `gscript.open_panel` | target, activate=False | none - session / editor state (panel, load, save, revert); no countable diagram effect | none | tools/gscript.py:1599 |
| `gscript.panel_wiring` | target | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | fresh-pass | tools/gscript.py:1109 |
| `gscript.queue_node` | kind, target, src_cls, src_index, src_name, diagram_index, location, element_name=None | new_functions >= 1 [result, record] | planned | tools/gscript.py:1480 |
| `gscript.read_bool_const` | target, uid | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | planned | tools/gscript.py:4391 |
| `gscript.read_const_value` | target, uid | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | none | tools/gscript.py:4417 |
| `gscript.read_term_type` | target, term_uid, index=None | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | none | tools/gscript.py:4646 |
| `gscript.remove_bad_wires` | target | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:1987 |
| `gscript.remove_bad_wires_scripted` | target | none - the number of bad wires is not known in advance; returns the Wire count and ExecState for the caller | planned | tools/gscript.py:3104 |
| `gscript.replace_object` | target, uid, new_path | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:3396 |
| `gscript.report` | target, cls | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | none | tools/gscript.py:698 |
| `gscript.report_all` | target, cls | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | fresh-pass | tools/gscript.py:731 |
| `gscript.revert` | target | none - session / editor state (panel, load, save, revert); no countable diagram effect | none | tools/gscript.py:1751 |
| `gscript.save` | target, allow_broken=False | saved == 1 [existing-raise, existing] | fresh-pass | tools/gscript.py:2595 |
| `gscript.set_auto_error_handling` | target, enabled | none - session / editor state (panel, load, save, revert); no countable diagram effect | none | tools/gscript.py:3238 |
| `gscript.set_control_label` | target, panel_index, text | label_back_ok == 1, op_err == 0 [result, record] | fresh-pass | tools/gscript.py:3758 |
| `gscript.set_default_in_memory` | target, label, value, probe_value | none - the function itself re-reads the value after reinit and returns it; the caller compares it with the plan default | planned | tools/gscript.py:3775 |
| `gscript.set_index_mode` | target, tunnel_index, mode | mode_back == mode [caller, caller] | planned | tools/gscript.py:2213 |
| `gscript.set_node_label` | target, diagram_index, node_index, text | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:3277 |
| `gscript.set_visible` | target, uid, visible | none - returns the op's read-back dict; Visible is a display property the step diff does not model | fresh-pass | tools/gscript.py:4365 |
| `gscript.shift_reg` | target, loop_index, reg_index, class_name='WhileLoop' | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | fresh-pass | tools/gscript.py:1036 |
| `gscript.shift_reg_left` | target, loop_index, reg_index, left_index=0, class_name='WhileLoop' | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | fresh-pass | tools/gscript.py:1069 |
| `gscript.sr_init_const` | target, loop_uid, face_uid, diagram_uid, donor, pos=(40, 40), loop_cls='WhileLoop' | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:2377 |
| `gscript.struct_copy_nested` | target, diagram_uid, cls, donor, pos=(40, 40) | new_objects == 1 [existing-raise, existing] | fresh-pass | tools/gscript.py:5016 |
| `gscript.subvis` | target, diagram_index, purge=False, strict=True, **controls | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | none | tools/gscript.py:768 |
| `gscript.term_index` | target, diagram_uid, node_uid, name, is_source | matches == 1, node_echo == node_uid [inline, raise] | none | tools/gscript.py:4999 |
| `gscript.tunnel_indicator` | target, tunnel_index | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:2240 |
| `gscript.tunnel_use_default` | target, tunnel_uid, value, cls='SelectorTunnel' | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:3749 |
| `gscript.tunnel_use_default_at` | target, cls, index, value | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:3733 |
| `gscript.tunnels` | target, index | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | planned | tools/gscript.py:1270 |
| `gscript.uids` | target, cls | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | fresh-pass | tools/gscript.py:1375 |
| `gscript.vi_ref` | target | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | none | tools/gscript.py:473 |
| `gscript.while_loop` | target, location, tunnels=(), indexing=() | none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists it as unrecorded) | none | tools/gscript.py:1549 |
| `gscript.wire` | target, src_cls, src_i, src_term, dst_cls, dst_i, dst_term, branch=False | new_wires >= 1 [existing-raise, existing] | none | tools/gscript.py:1698 |
| `gscript.wire_const` | target, src_cls, src_i, dst_cls, dst_i, dst_term_index, labels=None | new_wires == 1, op_err == 0 [result, record] | planned | tools/gscript.py:2340 |
| `gscript.wire_const_sr` | target, const_cls, const_i, loop_cls, loop_i, face_index, labels=None | new_wires == 1, op_err == 0 [result, record] | fresh-pass | tools/gscript.py:2351 |
| `gscript.wire_control` | target, control_names, dst_cls, dst_i, dst_terms, branch=False, src_diagram_index=0 | new_wires >= 1 [existing-raise, existing] | fresh-pass | tools/gscript.py:2286 |
| `gscript.wire_ctlsink` | target, ct_i, src_cls, src_i, src_term_index, labels=None | new_wires == 1, op_err == 0 [result, record] | fresh-pass | tools/gscript.py:2408 |
| `gscript.wire_health` | target, rows=None | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | fresh-pass | tools/gscript.py:3835 |
| `gscript.wire_indicators` | target, node_index, src_terms, indicator_names, diagram_index=0, node_class='SubVI' | none at this level - the op's err column is returned; stagexec's indicator route stops on it or defers it to a declared sink gate | fresh-fail | tools/gscript.py:2114 |
| `gscript.wire_joints` | target, wire_uid, index=None | none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the caller's census / step diff judges it) | none | tools/gscript.py:4679 |
| `gscript.wire_remove_loose_ends` | target, wire_uid, index=None | echo == wire_uid, broken_after == 0, op_err == 0 [result, record] | fresh-pass | tools/gscript.py:4980 |
| `gscript.wire_sr` | variant, target, loop_index, reg_index, node_index=None, term_index=None, ctl_index=None, class_name='WhileLoop' | none at this level - returns nothing; the wire is measured by the caller's census (stagekit wire_sr / stagexec step diff) | fresh-pass | tools/gscript.py:990 |
| `gscript.wire_tunouter` | target, tun_cls, tun_i, dst_cls, dst_i, dst_term_index, labels=None | new_wires == 1, op_err == 0 [result, record] | planned | tools/gscript.py:2418 |
| `recipes.build_d1_v0.move_in` | target, uid, dest_diagram_index, position | recipe function - outcome via the Stage._op verb that calls it | fresh-pass | tools/recipes/build_d1_v0.py:318 |
| `recipes.build_opconnectfromwire_v0.connect_from_wire` | target, wire_uid, term_index, sink_diag, sink_node, sink_term, labels | recipe function - outcome via the Stage._op verb that calls it | fresh-pass | tools/recipes/build_opconnectfromwire_v0.py:381 |
| `recipes.build_opconnectnested_v1.connect_nested_v1` | target, sink_diag, sink_node, sink_term, src_diag, src_node, src_term, labels | recipe function - outcome via the Stage._op verb that calls it | fresh-pass | tools/recipes/build_opconnectnested_v1.py:418 |
| `recipes.build_opfsinnertunnelconnect_v0.del_node` | target, cls, uid, tag='' | recipe function - outcome via the Stage._op verb that calls it | fresh-pass | tools/recipes/build_opfsinnertunnelconnect_v0.py:346 |
| `recipes.build_opfsinnertunnelconnect_v0.del_wire` | target, wire_uid, tag='' | recipe function - outcome via the Stage._op verb that calls it | fresh-pass | tools/recipes/build_opfsinnertunnelconnect_v0.py:336 |
| `stagekit.op:add_shift_reg` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.add_shift_reg) | fresh-pass | tools/stagekit.py:767 |
| `stagekit.op:case_frame_wire` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.case_frame_wire) | planned | tools/stagexec.py:3263 |
| `stagekit.op:case_in` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.case_in) | planned | tools/stagexec.py:2996 |
| `stagekit.op:case_wired` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.case_wired) | planned | tools/stagexec.py:2996 |
| `stagekit.op:connect` | (Stage._op verb) | none - gscript.connect_nested_v2 raises at entry (its op VI was never built); the live route is op:connect_nested_v1 | planned | tools/stagekit.py:704 |
| `stagekit.op:connect_from_wire` | (Stage._op verb) | none at this level - recipes.build_opconnectfromwire_v0.connect_from_wire returns its readout; LVBackend._cfw stops on its err / wire delta | fresh-pass | tools/stagekit.py:711 |
| `stagekit.op:connect_nested_v1` | (Stage._op verb) | none at this level - recipes.build_opconnectnested_v1.connect_nested_v1 returns (wire delta, ExecState, err); LVBackend.connect stops on err | fresh-pass | tools/stagekit.py:1086 |
| `stagekit.op:connect_term_uid` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.connect_term_uid) | fresh-pass | tools/stagexec.py:3289 |
| `stagekit.op:connect_terminals` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.connect_terminals) | planned | tools/stagekit.py:1086 |
| `stagekit.op:copy_in` | (Stage._op verb) | none at this level - the copied object is bound by stagexec's next read (bind_new) | planned | tools/stagekit.py:910 |
| `stagekit.op:create_const_on_term` | (Stage._op verb) | none at this level - OpCreateConstOnTerm_v0's readout; bound by the next read | fresh-pass | tools/stagekit.py:964 |
| `stagekit.op:create_local_read` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.create_local_read) | fresh-pass | tools/stagekit.py:779 |
| `stagekit.op:create_local_write` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.create_local_write) | fresh-pass | tools/stagekit.py:802 |
| `stagekit.op:create_primitive_nested` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.create_primitive_nested) | fresh-pass | tools/stagexec.py:2996 |
| `stagekit.op:delete_object` | (Stage._op verb) | removed == 1 [inline, raise] | fresh-pass | tools/stagekit.py:685 |
| `stagekit.op:delete_wire` | (Stage._op verb) | found == 1 [inline, raise] | fresh-pass | tools/stagekit.py:672 |
| `stagekit.op:drop_subvi` | (Stage._op verb) | none at this level - stagexec create 'subvi' measures the SubVI uid diff | fresh-pass | tools/stagexec.py:2996 |
| `stagekit.op:fs_add_frame` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.fs_add_frame) | planned | tools/stagexec.py:2996 |
| `stagekit.op:indicator_nested` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.create_indicator_nested) | fresh-pass | tools/stagexec.py:2996 |
| `stagekit.op:indicator_on_const` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.create_indicator_on_const) | fresh-pass | tools/stagexec.py:2996 |
| `stagekit.op:loop_in` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.loop_in) | fresh-pass | tools/stagexec.py:2996 |
| `stagekit.op:move_in` | (Stage._op verb) | none at this level - recipes.build_d1_v0.move_in; the new owner is read by stagexec's step diff | fresh-pass | tools/stagekit.py:698 |
| `stagekit.op:queue_node` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.queue_node) | planned | tools/stagexec.py:2996 |
| `stagekit.op:set_index_mode` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.set_index_mode) | planned | tools/stagexec.py:3330 |
| `stagekit.op:stop_from_node` | (Stage._op verb) | none - OpStopFromNode_v0's error string is returned; the step diff checks the new wire | fresh-pass | tools/stagexec.py:3212 |
| `stagekit.op:struct_copy_nested` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.struct_copy_nested) | fresh-pass | tools/stagexec.py:2996 |
| `stagekit.op:wire_const` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.wire_const) | planned | tools/stagexec.py:2863 |
| `stagekit.op:wire_const_sr` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.wire_const_sr) | fresh-pass | tools/stagexec.py:2863 |
| `stagekit.op:wire_control` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.wire_control) | fresh-pass | tools/stagexec.py:2863 |
| `stagekit.op:wire_ctlsink` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.wire_ctlsink) | fresh-pass | tools/stagexec.py:2863 |
| `stagekit.op:wire_indicators` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.wire_indicators) | fresh-fail | tools/stagekit.py:758 |
| `stagekit.op:wire_remove_loose_ends` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.wire_remove_loose_ends) | fresh-pass | tools/stagexec.py:3313 |
| `stagekit.op:wire_sr` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.wire_sr) | fresh-pass | tools/stagekit.py:773 |
| `stagekit.op:wire_tunouter` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.wire_tunouter) | planned | tools/stagexec.py:2863 |

<!-- GENERATED fn-table END -->

<!-- GENERATED fn-list BEGIN (tools/gen_capabilities.py - every public function of every SHARED tools file, by import graph; do not edit by hand) -->

## Every public function of the shared tools files - generated from code (card chat-T7)

A file is SHARED when at least one OTHER file under tools/ imports it (import graph, measured at generation; cache tools/bench/capabilities_shared.json). Look here before writing any logic (docs/script-writing.md rule 8). 185 files, 2432 functions, 1155 without a docstring. Regenerated at every cycle end and when a shared file is written.

| file | kind | imported by | functions | no docstring |
|---|---|---|---|---|
| [`tools/addrcheck.py`](#tools-addrcheck-py) | shared module | 12 | 17 | 1 |
| [`tools/allterms.py`](#tools-allterms-py) | shared module | 71 | 5 | 1 |
| [`tools/audit_cycle.py`](#tools-audit-cycle-py) | shared module | 8 | 15 | 3 |
| [`tools/bgrun.py`](#tools-bgrun-py) | shared module | 1 | 4 | 1 |
| [`tools/bgrun_reap.py`](#tools-bgrun-reap-py) | shared module | 3 | 5 | 2 |
| [`tools/card_clock.py`](#tools-card-clock-py) | shared module | 3 | 4 | 3 |
| [`tools/census_predict.py`](#tools-census-predict-py) | shared module | 40 | 7 | 4 |
| [`tools/cycle_runner.py`](#tools-cycle-runner-py) | shared module | 14 | 51 | 19 |
| [`tools/dispo.py`](#tools-dispo-py) | shared module | 3 | 3 | 0 |
| [`tools/doc_lint.py`](#tools-doc-lint-py) | shared module | 7 | 24 | 14 |
| [`tools/elrule.py`](#tools-elrule-py) | shared module | 23 | 10 | 1 |
| [`tools/errorlist_check.py`](#tools-errorlist-check-py) | shared module | 65 | 24 | 10 |
| [`tools/fn_records.py`](#tools-fn-records-py) | shared module | 5 | 19 | 9 |
| [`tools/fncontract.py`](#tools-fncontract-py) | shared module | 6 | 20 | 3 |
| [`tools/gate_fp.py`](#tools-gate-fp-py) | shared module | 8 | 10 | 3 |
| [`tools/gateclass.py`](#tools-gateclass-py) | shared module | 13 | 14 | 3 |
| [`tools/gen_capabilities.py`](#tools-gen-capabilities-py) | shared module | 3 | 17 | 0 |
| [`tools/gscript.py`](#tools-gscript-py) | shared module | 653 | 135 | 9 |
| [`tools/hash_probe.py`](#tools-hash-probe-py) | shared module | 64 | 2 | 2 |
| [`tools/jev.py`](#tools-jev-py) | shared module | 33 | 10 | 2 |
| [`tools/jev_candidates.py`](#tools-jev-candidates-py) | shared module | 106 | 15 | 3 |
| [`tools/jev_chain.py`](#tools-jev-chain-py) | shared module | 1 | 8 | 5 |
| [`tools/jev_contradict.py`](#tools-jev-contradict-py) | shared module | 3 | 4 | 1 |
| [`tools/jev_device_value.py`](#tools-jev-device-value-py) | shared module | 2 | 4 | 4 |
| [`tools/jev_drift.py`](#tools-jev-drift-py) | shared module | 4 | 6 | 0 |
| [`tools/jev_gaterow.py`](#tools-jev-gaterow-py) | shared module | 10 | 3 | 1 |
| [`tools/jev_pairs.py`](#tools-jev-pairs-py) | shared module | 7 | 14 | 8 |
| [`tools/jev_preflight.py`](#tools-jev-preflight-py) | shared module | 3 | 5 | 1 |
| [`tools/jev_rowcheck.py`](#tools-jev-rowcheck-py) | shared module | 3 | 8 | 1 |
| [`tools/launchunit.py`](#tools-launchunit-py) | shared module | 7 | 10 | 0 |
| [`tools/logclass.py`](#tools-logclass-py) | shared module | 17 | 9 | 0 |
| [`tools/lv_errorlist.py`](#tools-lv-errorlist-py) | shared module | 5 | 25 | 12 |
| [`tools/lvclick.py`](#tools-lvclick-py) | shared module | 4 | 18 | 10 |
| [`tools/motor_gate.py`](#tools-motor-gate-py) | shared module | 3 | 21 | 9 |
| [`tools/outcome_review.py`](#tools-outcome-review-py) | shared module | 2 | 6 | 3 |
| [`tools/prior_art_review.py`](#tools-prior-art-review-py) | shared module | 2 | 7 | 2 |
| [`tools/priorart_diff.py`](#tools-priorart-diff-py) | shared module | 5 | 8 | 5 |
| [`tools/protocol.py`](#tools-protocol-py) | shared module | 578 | 60 | 14 |
| [`tools/retro_due.py`](#tools-retro-due-py) | shared module | 2 | 6 | 2 |
| [`tools/retrospective.py`](#tools-retrospective-py) | shared module | 2 | 8 | 2 |
| [`tools/run_mode.py`](#tools-run-mode-py) | shared module | 1 | 3 | 3 |
| [`tools/scope_header.py`](#tools-scope-header-py) | shared module | 13 | 21 | 8 |
| [`tools/stage_prerun.py`](#tools-stage-prerun-py) | shared module | 174 | 124 | 29 |
| [`tools/stagekit.py`](#tools-stagekit-py) | shared module | 264 | 113 | 10 |
| [`tools/stagesim.py`](#tools-stagesim-py) | shared module | 166 | 64 | 25 |
| [`tools/stagexec.py`](#tools-stagexec-py) | shared module | 311 | 169 | 61 |
| [`tools/stop_record.py`](#tools-stop-record-py) | shared module | 26 | 19 | 2 |
| [`tools/vigraph.py`](#tools-vigraph-py) | shared module | 159 | 22 | 4 |
| [`tools/violations.py`](#tools-violations-py) | shared module | 1 | 5 | 2 |
| [`tools/wiki_build.py`](#tools-wiki-build-py) | shared module | 84 | 11 | 5 |
| [`tools/bench/bench_prep.py`](#tools-bench-bench-prep-py) | shared file in the bench folder (move to tools/ later) | 293 | 5 | 4 |
| [`tools/bench/build_opstopmode_v0.py`](#tools-bench-build-opstopmode-v0-py) | shared file in the bench folder (move to tools/ later) | 2 | 24 | 23 |
| [`tools/bench/build_ringpickslot_v2.py`](#tools-bench-build-ringpickslot-v2-py) | shared file in the bench folder (move to tools/ later) | 1 | 13 | 13 |
| [`tools/bench/c131_2_reach.py`](#tools-bench-c131-2-reach-py) | shared file in the bench folder (move to tools/ later) | 2 | 1 | 0 |
| [`tools/bench/c60c_astcheck.py`](#tools-bench-c60c-astcheck-py) | shared file in the bench folder (move to tools/ later) | 2 | 5 | 3 |
| [`tools/bench/c90c_rows.py`](#tools-bench-c90c-rows-py) | shared file in the bench folder (move to tools/ later) | 2 | 7 | 1 |
| [`tools/bench/c90d_border.py`](#tools-bench-c90d-border-py) | shared file in the bench folder (move to tools/ later) | 1 | 3 | 0 |
| [`tools/bench/c90d_reads.py`](#tools-bench-c90d-reads-py) | shared file in the bench folder (move to tools/ later) | 3 | 5 | 2 |
| [`tools/bench/c90d_table.py`](#tools-bench-c90d-table-py) | shared file in the bench folder (move to tools/ later) | 1 | 1 | 1 |
| [`tools/bench/camera_contract.py`](#tools-bench-camera-contract-py) | shared file in the bench folder (move to tools/ later) | 1 | 8 | 5 |
| [`tools/bench/d0_locate.py`](#tools-bench-d0-locate-py) | shared file in the bench folder (move to tools/ later) | 1 | 11 | 6 |
| [`tools/bench/d1_rewire_map.py`](#tools-bench-d1-rewire-map-py) | shared file in the bench folder (move to tools/ later) | 9 | 3 | 2 |
| [`tools/bench/diag_c100_verbs_build.py`](#tools-bench-diag-c100-verbs-build-py) | shared file in the bench folder (move to tools/ later) | 4 | 32 | 27 |
| [`tools/bench/diag_c108c_graph.py`](#tools-bench-diag-c108c-graph-py) | shared file in the bench folder (move to tools/ later) | 1 | 13 | 9 |
| [`tools/bench/diag_c115d_sel.py`](#tools-bench-diag-c115d-sel-py) | shared file in the bench folder (move to tools/ later) | 1 | 5 | 3 |
| [`tools/bench/diag_c118_p0.py`](#tools-bench-diag-c118-p0-py) | shared file in the bench folder (move to tools/ later) | 2 | 5 | 5 |
| [`tools/bench/diag_c138_6_run.py`](#tools-bench-diag-c138-6-run-py) | shared file in the bench folder (move to tools/ later) | 6 | 11 | 11 |
| [`tools/bench/diag_c153_b2_1_rescore.py`](#tools-bench-diag-c153-b2-1-rescore-py) | shared file in the bench folder (move to tools/ later) | 1 | 4 | 4 |
| [`tools/bench/diag_c61_localdir_write2.py`](#tools-bench-diag-c61-localdir-write2-py) | shared file in the bench folder (move to tools/ later) | 1 | 23 | 17 |
| [`tools/bench/diag_c81_uidref.py`](#tools-bench-diag-c81-uidref-py) | shared file in the bench folder (move to tools/ later) | 1 | 18 | 16 |
| [`tools/bench/diag_c83_connect2x2.py`](#tools-bench-diag-c83-connect2x2-py) | shared file in the bench folder (move to tools/ later) | 2 | 26 | 19 |
| [`tools/bench/diag_c83_connect2x2_r2.py`](#tools-bench-diag-c83-connect2x2-r2-py) | shared file in the bench folder (move to tools/ later) | 1 | 16 | 15 |
| [`tools/bench/diag_c91_step4_stats.py`](#tools-bench-diag-c91-step4-stats-py) | shared file in the bench folder (move to tools/ later) | 6 | 4 | 3 |
| [`tools/bench/diag_c94_sites.py`](#tools-bench-diag-c94-sites-py) | shared file in the bench folder (move to tools/ later) | 1 | 3 | 3 |
| [`tools/bench/diag_d1_execstate_preload.py`](#tools-bench-diag-d1-execstate-preload-py) | shared file in the bench folder (move to tools/ later) | 7 | 8 | 6 |
| [`tools/bench/diag_donor_census.py`](#tools-bench-diag-donor-census-py) | shared file in the bench folder (move to tools/ later) | 1 | 7 | 7 |
| [`tools/bench/diag_fstunnel_preclean_twins.py`](#tools-bench-diag-fstunnel-preclean-twins-py) | shared file in the bench folder (move to tools/ later) | 3 | 15 | 11 |
| [`tools/bench/diag_fstunnel_rbwvictims.py`](#tools-bench-diag-fstunnel-rbwvictims-py) | shared file in the bench folder (move to tools/ later) | 1 | 19 | 14 |
| [`tools/bench/diag_movein_p1_break.py`](#tools-bench-diag-movein-p1-break-py) | shared file in the bench folder (move to tools/ later) | 3 | 4 | 3 |
| [`tools/bench/diag_movein_set.py`](#tools-bench-diag-movein-set-py) | shared file in the bench folder (move to tools/ later) | 1 | 10 | 8 |
| [`tools/bench/diag_queue_donor.py`](#tools-bench-diag-queue-donor-py) | shared file in the bench folder (move to tools/ later) | 1 | 8 | 7 |
| [`tools/bench/diag_queue_donor2.py`](#tools-bench-diag-queue-donor2-py) | shared file in the bench folder (move to tools/ later) | 3 | 13 | 8 |
| [`tools/bench/diag_replay_gbtest.py`](#tools-bench-diag-replay-gbtest-py) | shared file in the bench folder (move to tools/ later) | 1 | 6 | 6 |
| [`tools/bench/diag_replay_lib.py`](#tools-bench-diag-replay-lib-py) | shared file in the bench folder (move to tools/ later) | 9 | 19 | 12 |
| [`tools/bench/diag_s2_scaffold.py`](#tools-bench-diag-s2-scaffold-py) | shared file in the bench folder (move to tools/ later) | 75 | 15 | 10 |
| [`tools/bench/diag_s3b_l0_localname_v2.py`](#tools-bench-diag-s3b-l0-localname-v2-py) | shared file in the bench folder (move to tools/ later) | 1 | 23 | 15 |
| [`tools/bench/diag_tunnelsource_onehop.py`](#tools-bench-diag-tunnelsource-onehop-py) | shared file in the bench folder (move to tools/ later) | 5 | 12 | 7 |
| [`tools/bench/diag_vigraph_check.py`](#tools-bench-diag-vigraph-check-py) | shared file in the bench folder (move to tools/ later) | 1 | 8 | 5 |
| [`tools/bench/drive_legguard.py`](#tools-bench-drive-legguard-py) | shared file in the bench folder (move to tools/ later) | 6 | 14 | 6 |
| [`tools/bench/drive_m8.py`](#tools-bench-drive-m8-py) | shared file in the bench folder (move to tools/ later) | 14 | 5 | 5 |
| [`tools/bench/drive_original_copy_v2.py`](#tools-bench-drive-original-copy-v2-py) | shared file in the bench folder (move to tools/ later) | 4 | 32 | 27 |
| [`tools/bench/drive_original_copy_v4.py`](#tools-bench-drive-original-copy-v4-py) | shared file in the bench folder (move to tools/ later) | 3 | 19 | 6 |
| [`tools/bench/drive_original_copy_v5.py`](#tools-bench-drive-original-copy-v5-py) | shared file in the bench folder (move to tools/ later) | 15 | 11 | 8 |
| [`tools/bench/fntest_lib.py`](#tools-bench-fntest-lib-py) | shared file in the bench folder (move to tools/ later) | 2 | 24 | 12 |
| [`tools/bench/ground_bench.py`](#tools-bench-ground-bench-py) | shared file in the bench folder (move to tools/ later) | 1 | 10 | 10 |
| [`tools/bench/imaqdx_limits.py`](#tools-bench-imaqdx-limits-py) | shared file in the bench folder (move to tools/ later) | 14 | 5 | 4 |
| [`tools/bench/jev_device_value_labels.py`](#tools-bench-jev-device-value-labels-py) | shared file in the bench folder (move to tools/ later) | 1 | 2 | 2 |
| [`tools/bench/jev_discharge_trial.py`](#tools-bench-jev-discharge-trial-py) | shared file in the bench folder (move to tools/ later) | 2 | 4 | 4 |
| [`tools/bench/jev_gate.py`](#tools-bench-jev-gate-py) | shared file in the bench folder (move to tools/ later) | 16 | 20 | 3 |
| [`tools/bench/jev_gaterow_q.py`](#tools-bench-jev-gaterow-q-py) | shared file in the bench folder (move to tools/ later) | 3 | 2 | 0 |
| [`tools/bench/jev_next_q.py`](#tools-bench-jev-next-q-py) | shared file in the bench folder (move to tools/ later) | 3 | 0 | 0 |
| [`tools/bench/jev_priorart_trial.py`](#tools-bench-jev-priorart-trial-py) | shared file in the bench folder (move to tools/ later) | 1 | 1 | 1 |
| [`tools/bench/jev_triage_q.py`](#tools-bench-jev-triage-q-py) | shared file in the bench folder (move to tools/ later) | 2 | 0 | 0 |
| [`tools/bench/jev_wave2a_trials.py`](#tools-bench-jev-wave2a-trials-py) | shared file in the bench folder (move to tools/ later) | 1 | 8 | 7 |
| [`tools/bench/k_contract_79.py`](#tools-bench-k-contract-79-py) | shared file in the bench folder (move to tools/ later) | 36 | 2 | 2 |
| [`tools/bench/launch_p3b2_c135.py`](#tools-bench-launch-p3b2-c135-py) | shared file in the bench folder (move to tools/ later) | 4 | 14 | 12 |
| [`tools/bench/launch_p3b2_c135_graph.py`](#tools-bench-launch-p3b2-c135-graph-py) | shared file in the bench folder (move to tools/ later) | 1 | 1 | 1 |
| [`tools/bench/launch_p3b2_resume_c135_compare.py`](#tools-bench-launch-p3b2-resume-c135-compare-py) | shared file in the bench folder (move to tools/ later) | 3 | 3 | 1 |
| [`tools/bench/m8_dry.py`](#tools-bench-m8-dry-py) | shared file in the bench folder (move to tools/ later) | 5 | 3 | 3 |
| [`tools/bench/m8b_replay_compare.py`](#tools-bench-m8b-replay-compare-py) | shared file in the bench folder (move to tools/ later) | 1 | 3 | 3 |
| [`tools/bench/opmodels_lib.py`](#tools-bench-opmodels-lib-py) | shared file in the bench folder (move to tools/ later) | 3 | 6 | 3 |
| [`tools/bench/prep_c143_3_elrule.py`](#tools-bench-prep-c143-3-elrule-py) | shared file in the bench folder (move to tools/ later) | 11 | 0 | 0 |
| [`tools/bench/s1_subvi_paths.py`](#tools-bench-s1-subvi-paths-py) | shared file in the bench folder (move to tools/ later) | 2 | 7 | 6 |
| [`tools/bench/selftest_c153_poskey_convert.py`](#tools-bench-selftest-c153-poskey-convert-py) | shared file in the bench folder (move to tools/ later) | 3 | 6 | 0 |
| [`tools/bench/selftest_guard_peer_jev.py`](#tools-bench-selftest-guard-peer-jev-py) | shared file in the bench folder (move to tools/ later) | 1 | 5 | 3 |
| [`tools/bench/selftest_guard_peer_ladder.py`](#tools-bench-selftest-guard-peer-ladder-py) | shared file in the bench folder (move to tools/ later) | 1 | 6 | 4 |
| [`tools/bench/selftest_stoprecord_supersession.py`](#tools-bench-selftest-stoprecord-supersession-py) | shared file in the bench folder (move to tools/ later) | 1 | 9 | 4 |
| [`tools/bench/selftest_t6_poskey.py`](#tools-bench-selftest-t6-poskey-py) | shared file in the bench folder (move to tools/ later) | 4 | 8 | 5 |
| [`tools/bench/spec_read.py`](#tools-bench-spec-read-py) | shared file in the bench folder (move to tools/ later) | 1 | 3 | 3 |
| [`tools/bench/subvi_harness.py`](#tools-bench-subvi-harness-py) | shared file in the bench folder (move to tools/ later) | 6 | 2 | 2 |
| [`tools/bench/t2_rsrc_blockdiff.py`](#tools-bench-t2-rsrc-blockdiff-py) | shared file in the bench folder (move to tools/ later) | 2 | 7 | 4 |
| [`tools/bench/verify_d1_s2.py`](#tools-bench-verify-d1-s2-py) | shared file in the bench folder (move to tools/ later) | 1 | 9 | 6 |
| [`tools/recipes/build_d1_m3a1.py`](#tools-recipes-build-d1-m3a1-py) | recipe imported by another file | 25 | 46 | 23 |
| [`tools/recipes/build_d1_m3a3b_d3.py`](#tools-recipes-build-d1-m3a3b-d3-py) | recipe imported by another file | 4 | 21 | 17 |
| [`tools/recipes/build_d1_v0.py`](#tools-recipes-build-d1-v0-py) | recipe imported by another file | 176 | 24 | 16 |
| [`tools/recipes/build_opcaseframes_v0.py`](#tools-recipes-build-opcaseframes-v0-py) | recipe imported by another file | 1 | 5 | 4 |
| [`tools/recipes/build_opconnectfromwire_v0.py`](#tools-recipes-build-opconnectfromwire-v0-py) | recipe imported by another file | 54 | 12 | 10 |
| [`tools/recipes/build_opconnectnested_v1.py`](#tools-recipes-build-opconnectnested-v1-py) | recipe imported by another file | 72 | 16 | 12 |
| [`tools/recipes/build_opconstvalue_v1.py`](#tools-recipes-build-opconstvalue-v1-py) | recipe imported by another file | 59 | 6 | 5 |
| [`tools/recipes/build_opconstvalue_v1b.py`](#tools-recipes-build-opconstvalue-v1b-py) | recipe imported by another file | 5 | 3 | 2 |
| [`tools/recipes/build_opconstvalue_v1c.py`](#tools-recipes-build-opconstvalue-v1c-py) | recipe imported by another file | 4 | 4 | 3 |
| [`tools/recipes/build_opconstvaluen_v0.py`](#tools-recipes-build-opconstvaluen-v0-py) | recipe imported by another file | 1 | 4 | 4 |
| [`tools/recipes/build_opcreateconstonterm_v0.py`](#tools-recipes-build-opcreateconstonterm-v0-py) | recipe imported by another file | 23 | 15 | 12 |
| [`tools/recipes/build_opfsinnertunnelconnect_v0.py`](#tools-recipes-build-opfsinnertunnelconnect-v0-py) | recipe imported by another file | 16 | 24 | 18 |
| [`tools/recipes/build_opfstunnelterm_v0.py`](#tools-recipes-build-opfstunnelterm-v0-py) | recipe imported by another file | 1 | 25 | 17 |
| [`tools/recipes/build_opfstunnelterm_v1.py`](#tools-recipes-build-opfstunnelterm-v1-py) | recipe imported by another file | 6 | 25 | 17 |
| [`tools/recipes/build_opfstunnelterm_v2.py`](#tools-recipes-build-opfstunnelterm-v2-py) | recipe imported by another file | 6 | 28 | 17 |
| [`tools/recipes/build_opownerchain_v1.py`](#tools-recipes-build-opownerchain-v1-py) | recipe imported by another file | 11 | 10 | 7 |
| [`tools/recipes/build_opsentinel_ops.py`](#tools-recipes-build-opsentinel-ops-py) | recipe imported by another file | 13 | 8 | 6 |
| [`tools/recipes/build_opstopfromnode_v0.py`](#tools-recipes-build-opstopfromnode-v0-py) | recipe imported by another file | 22 | 17 | 12 |
| [`tools/recipes/build_optunnelread_v0.py`](#tools-recipes-build-optunnelread-v0-py) | recipe imported by another file | 2 | 6 | 6 |
| [`tools/recipes/build_opwiresource_v0.py`](#tools-recipes-build-opwiresource-v0-py) | recipe imported by another file | 1 | 7 | 7 |
| [`tools/recipes/build_opwiresource_v1.py`](#tools-recipes-build-opwiresource-v1-py) | recipe imported by another file | 1 | 6 | 6 |
| [`tools/recipes/build_opwiresource_v2.py`](#tools-recipes-build-opwiresource-v2-py) | recipe imported by another file | 2 | 5 | 5 |
| [`tools/recipes/build_opwiresource_v3.py`](#tools-recipes-build-opwiresource-v3-py) | recipe imported by another file | 1 | 5 | 5 |
| [`tools/recipes/build_opwiresource_v4.py`](#tools-recipes-build-opwiresource-v4-py) | recipe imported by another file | 1 | 5 | 5 |
| [`tools/recipes/build_opwiresource_v5.py`](#tools-recipes-build-opwiresource-v5-py) | recipe imported by another file | 18 | 5 | 5 |
| [`tools/recipes/build_opwiresr_v0.py`](#tools-recipes-build-opwiresr-v0-py) | recipe imported by another file | 1 | 20 | 16 |
| [`tools/recipes/build_track_v6_core.py`](#tools-recipes-build-track-v6-core-py) | recipe imported by another file | 37 | 15 | 12 |
| [`tools/recipes/stage_d1_fgate.py`](#tools-recipes-stage-d1-fgate-py) | recipe imported by another file | 3 | 3 | 3 |
| [`tools/recipes/stage_d1_l2r1.py`](#tools-recipes-stage-d1-l2r1-py) | recipe imported by another file | 1 | 2 | 2 |
| [`tools/recipes/stage_d1_l2r2.py`](#tools-recipes-stage-d1-l2r2-py) | recipe imported by another file | 2 | 2 | 2 |
| [`tools/recipes/stage_d1_l7_r.py`](#tools-recipes-stage-d1-l7-r-py) | recipe imported by another file | 1 | 7 | 5 |
| [`tools/recipes/stage_d1_qrt_pool.py`](#tools-recipes-stage-d1-qrt-pool-py) | recipe imported by another file | 1 | 1 | 1 |
| [`tools/recipes/stage_d1_ring_p2a.py`](#tools-recipes-stage-d1-ring-p2a-py) | recipe imported by another file | 1 | 1 | 1 |
| [`tools/recipes/stage_d1_ring_p2b.py`](#tools-recipes-stage-d1-ring-p2b-py) | recipe imported by another file | 1 | 2 | 2 |
| [`tools/recipes/stage_d1_ring_p3a.py`](#tools-recipes-stage-d1-ring-p3a-py) | recipe imported by another file | 1 | 1 | 1 |
| [`tools/recipes/stage_d1_ring_p3b1.py`](#tools-recipes-stage-d1-ring-p3b1-py) | recipe imported by another file | 1 | 1 | 1 |
| [`tools/recipes/stage_d1_ring_p3b2a.py`](#tools-recipes-stage-d1-ring-p3b2a-py) | recipe imported by another file | 2 | 1 | 1 |
| [`tools/recipes/stage_d1_ring_p3b2b.py`](#tools-recipes-stage-d1-ring-p3b2b-py) | recipe imported by another file | 2 | 1 | 1 |
| [`tools/recipes/stage_d1_ring_p4_rasrest.py`](#tools-recipes-stage-d1-ring-p4-rasrest-py) | recipe imported by another file | 1 | 1 | 1 |
| [`tools/recipes/stage_d1_ring_p4_s01.py`](#tools-recipes-stage-d1-ring-p4-s01-py) | recipe imported by another file | 1 | 1 | 1 |
| [`tools/recipes/stage_d1_ring_p4_s02.py`](#tools-recipes-stage-d1-ring-p4-s02-py) | recipe imported by another file | 1 | 1 | 1 |
| [`tools/recipes/stage_d1_ring_p4_s02v18.py`](#tools-recipes-stage-d1-ring-p4-s02v18-py) | recipe imported by another file | 1 | 1 | 1 |
| [`tools/recipes/stage_d1_ring_p4_s03v18.py`](#tools-recipes-stage-d1-ring-p4-s03v18-py) | recipe imported by another file | 1 | 1 | 1 |
| [`tools/recipes/stage_d1_ring_p4_s04v18.py`](#tools-recipes-stage-d1-ring-p4-s04v18-py) | recipe imported by another file | 1 | 1 | 1 |
| [`tools/recipes/stage_d1_ring_p4_s05v18.py`](#tools-recipes-stage-d1-ring-p4-s05v18-py) | recipe imported by another file | 1 | 1 | 1 |
| [`tools/recipes/stage_d1_ring_p4_s06v18.py`](#tools-recipes-stage-d1-ring-p4-s06v18-py) | recipe imported by another file | 2 | 4 | 2 |
| [`tools/recipes/stage_d1_ring_p4_s06v18_scratch.py`](#tools-recipes-stage-d1-ring-p4-s06v18-scratch-py) | recipe imported by another file | 1 | 9 | 5 |
| [`tools/recipes/stage_d1_ring_p4_s07v18.py`](#tools-recipes-stage-d1-ring-p4-s07v18-py) | recipe imported by another file | 1 | 4 | 2 |
| [`tools/recipes/stage_d1_ring_p4_s08v18.py`](#tools-recipes-stage-d1-ring-p4-s08v18-py) | recipe imported by another file | 1 | 4 | 2 |
| [`tools/recipes/stage_d1_ring_p4_s09v18.py`](#tools-recipes-stage-d1-ring-p4-s09v18-py) | recipe imported by another file | 1 | 4 | 2 |
| [`tools/recipes/stage_d1_ring_p4s1.py`](#tools-recipes-stage-d1-ring-p4s1-py) | recipe imported by another file | 1 | 1 | 1 |
| [`tools/recipes/stage_d1_ring_p5s01a.py`](#tools-recipes-stage-d1-ring-p5s01a-py) | recipe imported by another file | 1 | 4 | 2 |
| [`tools/recipes/stage_d1_s1.py`](#tools-recipes-stage-d1-s1-py) | recipe imported by another file | 4 | 19 | 4 |
| [`tools/recipes/stage_d1_s3_focus.py`](#tools-recipes-stage-d1-s3-focus-py) | recipe imported by another file | 1 | 22 | 15 |
| [`tools/recipes/stage_template_ring.py`](#tools-recipes-stage-template-ring-py) | recipe imported by another file | 1 | 1 | 1 |
| [`tools/hooks/guard_assign.py`](#tools-hooks-guard-assign-py) | hook - reference | 4 | 17 | 8 |
| [`tools/hooks/guard_bash.py`](#tools-hooks-guard-bash-py) | hook - reference | 13 | 12 | 0 |
| [`tools/hooks/guard_card.py`](#tools-hooks-guard-card-py) | hook - reference | 4 | 4 | 2 |
| [`tools/hooks/guard_cycle.py`](#tools-hooks-guard-cycle-py) | hook - reference | 24 | 14 | 3 |
| [`tools/hooks/guard_peer.py`](#tools-hooks-guard-peer-py) | hook - reference | 25 | 27 | 4 |
| [`tools/hooks/guard_session.py`](#tools-hooks-guard-session-py) | hook - reference | 6 | 18 | 7 |
| [`tools/hooks/guard_write.py`](#tools-hooks-guard-write-py) | hook - reference | 4 | 8 | 4 |
| [`tools/hooks/report_gate.py`](#tools-hooks-report-gate-py) | hook - reference | 2 | 8 | 5 |

### tools/addrcheck.py

shared module; imported by 12 file(s): `tools/bench/diag_c151_a1_1_fs.py`, `tools/bench/diag_c152_b3_1_fs.py`, `tools/bench/diag_c154_a3_3_nodes.py`, `tools/bench/jev_addr_measure_s5.py`, `tools/bench/prep_c150_a2_4_stage_prerun_before.py`, `tools/bench/selftest_s5.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `addr_key` | a | The canonical text of one plan address (dict or '<uid>.<term>' string) - the key stagesim's addr_pos records use. | - | 44 |
| `owner_rows` | rows, owner | The owner's terminal rows in READ order, one per term uid (a multi-frame tunnel lists a uid once). | - | 51 |
| `triple` | rows, term_uid | {owner, index, class, source, name} of one terminal row, index = position among its owner's rows (read order). | - | 61 |
| `pos_table` | rows | card chat-T6 (docs/d1/result-gates.md): {term uid: POSITION KEY (node, index, term class, is_source)} over one terminal table - the | selftest_t6_poskey.py | 72 |
| `resolve` | rows, owner, name, want_source=None, pos=None, owner_class=None | (row / None, how, candidates). Tier (a) on ONE address against ONE terminal table. 'pos' = the recorded triple | - | 97 |
| `real_match` | sim_rows, st, real_rows, rt, rn_owner | Tier (a) on the REAL side of a rebind: does real row 'rt' on real owner 'rn_owner' sit at the SAME position as | - | 139 |
| `real_face` | sim_rows, st, real_rows, rn_owner, face, want_source, rt, mode | (ok, why). A plan address named 'inner'/'outer' binds on the real side only when ALL hold: the sim row 'st' is of | - | 171 |
| `obj_class` | doc, uid | The class of object 'uid' in a graph doc's 'objs' (None when absent). | - | 194 |
| `cond_sinks` | doc, rows, loop | (body diagrams, sink rows) of While 'loop': stagesim.cond_row's filter (body Diagram = 'owners' entry owned by the | - | 199 |
| `cond_bind` | addr, sim_doc, sim_rows, sim_loop, real_doc, real_rows, real_loop, M | (real sink uid / None, why). The PD316 base-loop form {'uid': <While>, 'term': 'cond'} (stagexec.base_cond: exactly | - | 213 |
| `jev_same` | planned, candidate, n=1, timeout=25 | (p, verdict, err) - one typed question. Never raises; no key -> (None, 'unknown', 'no key'). | - | 252 |
| `measure` | path=LABELLED, out=MEASURE, n=1, log=print | Run tier (b) on the labelled set; write {accuracy, n, rows, switched_on} to MEASURE. Accuracy counts an 'unknown' | - | 265 |
| `jev_switched_on` | path=MEASURE | (no docstring) | - | 289 |
| `advise` | items, log=print, n=1 | Tiers (b) and (c) over unresolved items [{planned, candidates:[...]}]: Jev advisory per candidate when switched on | - | 298 |
| `plan_ends` | plan | [(action n, action id, field, address)] for every address field of every action. | - | 327 |
| `split_addr` | v | (owner uid int / None, term name / None, term_uid / None) - None owner for a symbolic new:... address. | - | 337 |
| `check_plan` | plan, rows, addr_pos=None | Tier (a) over every NUMERIC-owner address of a plan against ONE terminal table (the plan's base graph). Symbolic | - | 349 |

### tools/allterms.py

shared module; imported by 71 file(s): `tools/bench/allterms_s4.py`, `tools/bench/allterms_v1_check.py`, `tools/bench/diag_c100_6_maxmin.py`, `tools/bench/diag_c103_wait_donor.py`, `tools/bench/diag_c111_b1_errorlist.py`, `tools/bench/diag_c112b_opuid.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `read_terms` | target, op=OP_ALLTERMS | Every terminal of 'target''s block diagram in ONE op run. Returns (rows, seconds). | - | 68 |
| `all_wire_uids` | target | Every Wire object's uid on 'target''s diagram, in ONE 'report_all' run. Returns (uids, seconds). | - | 94 |
| `join_wires` | rows, wire_uids=None | One row per wire, joined from the terminal table by wire_uid. Pure; no LabVIEW. | - | 106 |
| `severed` | wires | Wires missing a side - the shape the D1 bed's 11 broken wires are expected to show. | - | 145 |
| `main` | argv=None | (no docstring) | - | 150 |

### tools/audit_cycle.py

shared module; imported by 8 file(s): `tools/bench/jev_wave4_selftest.py`, `tools/bench/selftest_audit_a9_witness.py`, `tools/bench/selftest_audit_c4c_split.py`, `tools/bench/selftest_audit_c7.py`, `tools/bench/selftest_audit_cost_window.py`, `tools/bench/selftest_bgrun_reap.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `seg_failures` | seg | Failure count of ONE run segment (starts at its BGRUN START line): legacy findall count before the switch, | - | 118 |
| `log_failed` | body | A3's question for a whole log: did ANY run in it fail (legacy rule for pre-switch runs). | - | 128 |
| `window_runs` | body, cutoff, until | The parts of a bgrun log that belong to THIS window: one segment per 'BGRUN START' stamped inside it. | - | 139 |
| `cost_split` | machinery_logs, cutoff, until | Wall-clock and dollars of the MACHINERY logs, split into REVIEW spend and JUDGEMENT-SESSION spend. | - | 165 |
| `drop_jev_ledgers` | paths, bench=None | (kept, dropped): the Jev ledgers directly in 'bench' (default BENCH, resolved at call time) are dropped. | - | 234 |
| `a1_bypass` | build_logs | A1's reading: basenames of build logs carrying no 'BGRUN START' line. | - | 245 |
| `a3_unreviewed` | build_logs, reviews_glob=None | A3's reading: (failing, unreviewed) - a failing log with no archived review newer than it. | - | 250 |
| `a2_state` | body | A2's reading of one log body (card 92-4): "" (no bgrun run at all), "ended" (END or TIMEOUT present), | - | 259 |
| `a9_named_files` | lines, root, code_names | Project-relative code files a disposition names: 'tools/x/y.py' as written, or a bare 'y.py' that resolves to | - | 288 |
| `a9_unlanded` | root=None, peer_glob=A9_GLOB, code_override=None, detail=None | (absent: [review stem], n_candidates). 'code_override' {project-relative path: text} replaces a code file's | - | 307 |
| `say` | check, ok, detail | (no docstring) | - | 358 |
| `read` | p | (no docstring) | - | 364 |
| `parse_ts` | s | Epoch seconds, or 'YYYY-MM-DD[ HH:MM[:SS]]' in local time. Returns None for an empty value. | - | 372 |
| `c7_plan` | root=None, next_path=None | Which plan document C7 measures scope against. Returns (path or None, basis string). | selftest_audit_c7.py | 490 |
| `main` |  | (no docstring) | - | 534 |

### tools/bgrun.py

shared module; imported by 1 file(s): `tools/bench/replay_c6_protocol.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `relaunch_detached` | logp | Re-exec THIS runner so it survives its caller's exit (cycle 15 deliverable 1). | - | 80 |
| `is_jev_command` | cmd | True when the script this command runs (its FIRST '.py' token) is a Jev script. Never the log name. | - | 131 |
| `is_scoped_script` | cmd | True when the script this command runs (its FIRST '.py' token) is a tools/recipes or tools/bench script and | - | 140 |
| `main` |  | (no docstring) | - | 147 |

### tools/bgrun_reap.py

shared module; imported by 3 file(s): `tools/bench/selftest_bgrun_reap.py`, `tools/bgrun.py`, `tools/cycle_runner.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `live_pids` |  | Set of running pids from ONE tasklist call; None when tasklist itself failed (then nothing is reaped). | - | 46 |
| `classify` | text | (state, pid) of the LAST run segment: 'none' (no START), 'ended' (terminal line present), | - | 59 |
| `killed_line` | pid, who | (no docstring) | - | 86 |
| `reap` | bench=BENCH, exclude=(), who='bgrun_reap', max_age_days=MAX_AGE_DAYS, dry_run=False, pids=None | Mark every dead-runner log under 'bench'. Returns {"marked": [(path, pid)], "open_live": [(path, pid)], | - | 91 |
| `main` |  | (no docstring) | - | 142 |

### tools/card_clock.py

shared module; imported by 3 file(s): `tools/bench/selftest_c153_cardclock_quoted.py`, `tools/bench/selftest_card_clock.py`, `tools/protocol.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `cite_text` | res | first_fail + blocked_by's strings, each with its quoted spans blanked (fp-72). | - | 41 |
| `find_bind` | log, cid | (no docstring) | - | 47 |
| `clock` | result_path, log, cards | (no docstring) | - | 59 |
| `main` | argv=None | (no docstring) | - | 93 |

### tools/census_predict.py

shared module; imported by 40 file(s): `tools/bench/diag_c133_1_pred_p3b2.py`, `tools/bench/diag_c133_5_pred_p3b2b.py`, `tools/bench/diag_c134_1_finalize_b.py`, `tools/bench/plan_ring_p3b_split.py`, `tools/bench/plan_ring_p3b_split_p3b2.py`, `tools/bench/prep_c139_5_mkv13.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `md5_of` | p | (no docstring) | - | 39 |
| `resolve_row` | a, by_as, samples, canon_by_donor | -> (op_key, variant_name or None, delta dict or None, why). | - | 72 |
| `predict` | plan, pred, samples | (no docstring) | - | 121 |
| `result_line` | rep, artefacts | (no docstring) | - | 171 |
| `check_cites` | cites, root=ROOT | Every cite {file, line, expect}: 'expect' must be a substring of that 1-based line. -> list of problems ([] = all hold). | - | 193 |
| `record_sample` | samples_p, op, variant, delta, cites, why='', plan_match=None, route=None, match=None, n=1 | Card 123-7 (PD247(e)): record a scratch run's MEASURED class census as a sample. Refuses (ValueError, nothing written) | - | 210 |
| `main` | argv | (no docstring) | - | 240 |

### tools/cycle_runner.py

shared module; imported by 14 file(s): `tools/bench/selftest_bgrun_reap.py`, `tools/bench/selftest_c108e_tools.py`, `tools/bench/selftest_chat_p1.py`, `tools/bench/selftest_cycle_runner.py`, `tools/bench/selftest_cycle_runner_ladder.py`, `tools/bench/selftest_cycle_runner_retro.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `spawn_env` | extra=None | (no docstring) | - | 108 |
| `read` | p | (no docstring) | - | 117 |
| `stop_marker` | status_text | The user's handle on the loop. 'STOP' at the start of a line in the head of the file, or a STOP heading. | - | 125 |
| `next_section` | status_text | (no docstring) | - | 135 |
| `next_last_line` | status_text | (no docstring) | - | 140 |
| `session_cmd` | a, prompt, model=None, effort=None | The command bgrun will run: one headless judgement session, or the dry-run stand-in. | - | 145 |
| `result_json` | log_text | The '--output-format json' envelope out of a bgrun log, or None. | - | 157 |
| `limit_wait_s` | log_text, now=None | Seconds to sleep for a usage limit (renewal + 2 min), or None when this is not a limit message. | - | 173 |
| `log_line` | path, text | (no docstring) | - | 199 |
| `last_cycle_number` | runner_log | (no docstring) | - | 209 |
| `judge_ab_effort` | n, mode, now=None | (effort / None, why). mode on/off/auto; auto = on before JUDGE_AB_UNTIL. | - | 275 |
| `judge_choice` | level, ff_recipe, ff_rung, base_model, base_effort | (rank, model, effort): the higher of the judgement-ladder level and the firefighter rung, capped at JUDGE_TOP. | - | 284 |
| `judge_ladder_step` | level, next_moved, slugs, delivered | -> (new_level, reason, stop). Pure; the caller persists and logs. | - | 296 |
| `retro_files_in_window` | peer_dir, t_start, t_end | card chat-P1 2b: the retrospective archives CREATED inside the window (same stamp rule as retro_slugs_in_window). | - | 314 |
| `retro_slugs_in_window` | peer_dir, t_start, t_end | VIOLATION slugs from retrospective files CREATED inside the cycle window (creation time, as failed_recipes). | - | 332 |
| `goalmap_done` | path | (no docstring) | - | 352 |
| `delivered_in_window` | cards_dir, t_start, t_end, done_before, goalmap_path | '' or a short description: a PASS result/1 card with artefacts written in the window, or a milestone newly done. | - | 360 |
| `judge_state_load` | bench | (no docstring) | - | 385 |
| `judge_state_save` | bench, level, reason, n | (no docstring) | - | 393 |
| `add_judge_decision` | n, reason, blocks, path | One open decisions-pending/1 item for a judgement ladder exhausted at its top rung. (id, None) / (None, why). | - | 402 |
| `command_identity` | cmd | The SCRIPT identity of a bgrun command: every '.py' path in it, basename, '_vN' stripped, lower-cased, joined | - | 424 |
| `newest_run_passed` | bench, identity, since_mtime, skip_names=() | True when the NEWEST bgrun run of 'identity' (any log in bench with mtime >= since_mtime, by START time then | - | 435 |
| `failed_recipes` | bench, t_start, t_end | Recipe basenames whose bgrun log (mtime inside [t_start, t_end]) ended rc!=0 or TIMEOUT - unless the NEWEST | - | 468 |
| `git_commit_cycle` | n, runner_log | Commit everything the cycle left in the tree (2026-09-24: cycles 68/69 ended with 129 uncommitted files; | - | 560 |
| `capabilities_hook` | n, runner_log, doc=None, timeout=300, gen=None | Card chat-T7 item 6(c) (user 2026-10-09 "전부 적용"): at every cycle end, BEFORE the git commit, regenerate the function table + | selftest_t7_capabilities.py | 576 |
| `land_retrospective` | bench, runner_log | A retrospective the session started but did not finish is RE-RUN by the runner, synchronously. | - | 603 |
| `retro_fallback` | n, t_start, a, bench, runner_log | card chat-P1 item 2b (user 2026-09-28): the session runs its retrospective only when tools/retro_due.py says it | - | 636 |
| `motor_limits_hook` | phase, n, a, bench, runner_log, status_text | User, 2026-09-23 ("훅으로 묶어서 매 사이클마다 시작할때는 묶고, 종료시에는 풀고. 그 다음 각 싸이클 시작 및 종료 | - | 678 |
| `labview_close_hook` | n, a, bench, runner_log, status_text | User 2026-09-24 ("사이클 종료하고서는 제대로 LabVIEW 끄는것 잊지 말것, 특히 카메라가 계속 Acquisition 하면 기계에 | - | 769 |
| `bgrun_reap_hook` | n, bench, runner_log | Card 92-4 (retrospective-cycle90 'device-failed', threshold 1): at every cycle end, close the record of any | - | 808 |
| `errorlist_hook` | n, a, bench, runner_log, status_text | User decision 5, 2026-09-24 ("사이클 시작하기 전에 LabVIEW 컴파일 에러 창은 반드시 확인해야할듯"): before every | - | 828 |
| `gates_due` | bench, peer_dir, next_card | [{gate, due, detail}] - every guard_cycle 'due' check, measured at cycle start. 'due' None = the check errored. | - | 979 |
| `retro_undisposed` | peer_dir | Path of the newest archived retrospective whose disposition is missing, empty or still the placeholder, else None | - | 1028 |
| `retro_undisposed_item` | n, peer_dir, runner_log | The 'retro-undisposed' gates_due item ({gate, due: True, detail}) when retro_undisposed() names a file, else None; | - | 1052 |
| `gates_due_hook` | n, a, bench, runner_log | Cycle start: gates_due(), then a DUE outcome review is RUN before the session spawns (not in dry runs unless the | - | 1071 |
| `write_cycle_card` | bench, n, status_text, model, effort, ff_recipe, motor_verdict, a, errorlist=None, steer=None, note=None, gates=None | C1: '<bench>/cards/cycle_<n>.json', validated against docs/protocol/cycle.json. Returns (path, None) or | - | 1114 |
| `next_json_reading` | bench | (md5 / 'absent', card / None, why / None) of '<bench>/next.json' - the ONE reading the runner uses. | - | 1164 |
| `note_in_status` | status_path, reason | APPEND a stop notice; never rewrite STATUS.md - it is the user's file and the next session's cold start. | - | 1169 |
| `Heartbeat` | (class) | (no docstring) | - | 1189 |
| `Heartbeat.begin` | n | (no docstring) | - | 1197 |
| `Heartbeat.cycle_end` | n, rc, cost | (no docstring) | - | 1200 |
| `Heartbeat.emit` | kind | (no docstring) | - | 1265 |
| `Heartbeat.final` |  | (no docstring) | - | 1325 |
| `run_session` | a, cmd, log, env, n, status_path, runner_log, tag | ONE session under bgrun, with the usage-limit / API-5xx rerun rule (CLAUDE.md usage-limit protocol: rerun, don't | - | 1339 |
| `newest_assign_result` | cards_dir | (no docstring) | - | 1410 |
| `purpose_from_next` | card | (no docstring) | - | 1415 |
| `write_assign_card` | cards_dir, n, k, purpose, next_md5, cfg, state_path, result_path, handback_in | (no docstring) | - | 1423 |
| `write_handback` | cards_dir, n, k, trigger, detail, st_path, result_path, next_md5, usd, minutes | (no docstring) | - | 1439 |
| `assign_cmd` | a, cfg, prompt | The assignment session's command (the bgrun-wrapped part), or None = skip (a dry run without a stand-in). | - | 1456 |
| `assignment_rounds` | a, n, bench, runner_log, status_path, judge_prompt, model, effort, judge_rc, next_md5_cycle_start | The purpose flow after the cycle's first judgement session. -> {'outcome', 'rounds', 'cost'}. Never raises into | - | 1465 |
| `main` |  | (no docstring) | - | 1581 |

### tools/dispo.py

shared module; imported by 3 file(s): `tools/audit_cycle.py`, `tools/bench/selftest_c150_a3_3.py`, `tools/cycle_runner.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `heading_index` | body | Start index of the disposition heading, else -1 (card 150-a3-4). | - | 36 |
| `find_disposition` | body | (answer, disposition_text) split at the last line-anchored heading; (body, None) when there is none. | - | 51 |
| `disposition_len` | body | Characters left in the disposition after placeholder lines are removed and the rest stripped; None = no heading. | - | 59 |

### tools/doc_lint.py

shared module; imported by 7 file(s): `tools/audit_cycle.py`, `tools/bench/selftest_audit_c7.py`, `tools/bench/selftest_c116a_landed.py`, `tools/bench/selftest_chat_p2.py`, `tools/bench/selftest_doc_lint_d1.py`, `tools/bench/selftest_fn_f2.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `say` | level, check, detail | (no docstring) | - | 73 |
| `read` | p | (no docstring) | - | 77 |
| `active_docs` |  | The ACTIVE set: docs/*.md, the index directories ('docs/d1/*.md', card chat-D1 2026-10-02) and the two root | - | 85 |
| `rel` | p | (no docstring) | - | 98 |
| `frontmatter` | body | The YAML block as a flat dict, or None. Deliberately not a YAML parser: these blocks are machine-written by | - | 107 |
| `check_frontmatter` |  | (no docstring) | - | 121 |
| `citation_candidates` | body | (path, lineno_or_None, line_number_in_the_document) for every span that is plausibly a project path. | - | 149 |
| `check_citations` |  | (no docstring) | - | 191 |
| `check_status_length` |  | (no docstring) | - | 233 |
| `current_plans` | docs=None | Every 'docs/cycle*-plan.md' (or 'docs/<dir>/INDEX.md') whose frontmatter says 'status: current', as ABSOLUTE paths. | - | 244 |
| `check_one_current_plan` |  | (no docstring) | - | 265 |
| `check_predecided` |  | L8: the CURRENT cycle plan carries a '## Pre-decided' section (CLAUDE.md section 3 item 2, 2026-09-17). | - | 278 |
| `check_supersedes` |  | (no docstring) | - | 299 |
| `check_dispositions` |  | 'disposition: legacy' in the frontmatter is EXCLUDED, and the exclusion is the point. | - | 321 |
| `check_marked_decisions` |  | (no docstring) | - | 359 |
| `check_decision_headers` | path=None | (no docstring) | - | 385 |
| `predecided_items` | body | [(number, first_line_no, text)] for every numbered item inside a 'Pre-decided' section of one document. | - | 424 |
| `check_user_rules_lines` | paths=None | (no docstring) | - | 452 |
| `is_frozen` | p | (no docstring) | - | 481 |
| `check_line_cap` | paths=None, names=None | L10 (card chat-D1): an active doc under docs/ that is not frozen/superseded stays <= DOC_MAX_LINES lines. | - | 485 |
| `check_frozen_footer` | paths=None | L11 (card chat-D1): a 'status: frozen' doc carries its FROZEN footer, which names the index to read instead. | - | 520 |
| `check_fn_drift` | doc=None | L12 (card chat-F2, user 2026-10-06): CODE-vs-DOC drift of the generated scripting-function table in | - | 532 |
| `run` | skip_dispositions=False | (no docstring) | - | 552 |
| `main` |  | (no docstring) | - | 573 |

### tools/elrule.py

shared module; imported by 23 file(s): `tools/bench/diag_c149_a1_2_eladv.py`, `tools/bench/diag_c150_a3_2_elexp.py`, `tools/bench/diag_c151_a1_1_elexp.py`, `tools/bench/diag_c152_b3_1_elexp.py`, `tools/bench/diag_c154_a3_3_elexp.py`, `tools/bench/prep_c143_3_elrule.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `load_requiredness` | path=None | The measured SubVI requiredness table ({'vis': {file name: {'terminals': [...]}}}); an unreadable file gives an EMPTY | - | 54 |
| `subvis_from_plan` | plan, *states | {uid: VI file name} for every SubVI the plan creates ('create' action, class SubVI, 'subvi_path'), bound through the | - | 63 |
| `subvi_rules` | rs, vi, table | ([rule or None per row of rs], how) - the measured pane rule of each terminal row of one SubVI node. | - | 78 |
| `owners_map` | *states | {body_uid: loop_uid} for every Diagram owned by a WhileLoop, merged over the given states/graphs' 'owners' maps. | - | 94 |
| `items` | state, bodies, created=(), subvis=None, table=None | (set of item keys, detail dict) for one state (sim step state or graph json: both carry 'terminals' rows). | - | 107 |
| `unwired_inputs` | state | (no docstring) | - | 162 |
| `predict` | st0, last, base_total, created, carry=(), extra_owner_states=(), subvis=None, table=None | The fixed EL prediction of one session: st0 = its base state (step_00), last = its simulated end, created = uids of the | - | 170 |
| `item_class` | text | 'local' / 'cond' / 'sr' / None for one Error List item text (raw + detail). | - | 201 |
| `session_prediction` | plan, base_total | The fixed-rule prediction of the session a finalized stageplan describes (its first/last step files), or None. | - | 217 |
| `by_design_verdict` | extra, missing, measured_total, base_total, plan=None, prediction=None | ('log'/'stop', rule, detail) - see the module docstring. 'extra'/'missing' = item texts from errorlist_check.compare; | - | 228 |

### tools/errorlist_check.py

shared module; imported by 65 file(s): `tools/bench/c109_errorlist_reverdict.py`, `tools/bench/c87_errorlist_reverdict.py`, `tools/bench/c88_reverdict.py`, `tools/bench/diag_c109c_errorlist.py`, `tools/bench/diag_c110_errorlist.py`, `tools/bench/diag_c110d_elcounts.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `md5` | p | (no docstring) | - | 57 |
| `not_ready` | e | (no docstring) | - | 95 |
| `labview_up` | R | Start (COM Dispatch launches it) / reach LabVIEW, then wait until two handle readings 5 s apart differ by | - | 100 |
| `vi_ready` | target, R | Poll a counted GetVIReference (+ ExecState) on 'target' until it answers, up to VI_READY_S; only the | - | 138 |
| `current_bed` | status_path | 'current-bed: <file.vi>' in STATUS wins; else the NEWEST-on-disk claudeDev D1_*.vi that STATUS names. | - | 159 |
| `current_bed_text` | txt, claudedev=None | current_bed() on STATUS text (pure; cycle_runner holds the text already). | - | 164 |
| `find_reusable` | bed, bed_md5, bench=None | (main_json, raw_json, None) for the newest qualifying read of 'bed' at 'bed_md5', else (None, None, reason). | - | 183 |
| `reverdict` | bed, main_json, raw_json, bench=None, out_dir=None, expected_path=None | Offline verdict of a saved read with the CURRENT checker. Writes errorlist_<stem>_<ts>_reuse.json; returns | - | 215 |
| `windows_named` | sub | (no docstring) | - | 248 |
| `open_diagram` | scratch, R | (no docstring) | - | 252 |
| `make_on_item` | scratch, R | (no docstring) | - | 272 |
| `count_zero` | R | A runnable VI has no highlighted row, so lv_errorlist never reads N: OCR the last dialog capture whole. | - | 302 |
| `norm` | s | (no docstring) | - | 315 |
| `ocr_fold` | k | (no docstring) | - | 325 |
| `norm_ocr` | s | (no docstring) | - | 331 |
| `plan_for_bed` | bed, bench=None | stage_d1_<s>.json whose 'work' is this bed -> the stageplan plan_<s>*.json carrying open_rows. | - | 350 |
| `derive_expected` | plan | (no docstring) | - | 377 |
| `compare` | items, expected, derived=() | Explicit expected entries (file) are REQUIRED; plan-derived licences are not. Returns extra raws, missing | - | 415 |
| `license_headers` | items | Mark 'licensed_by = 'header-of <n>'' on qualifying empty-raw rows; return their positions in 'items'. | - | 448 |
| `class_counts` | items, ocr=False | {norm(raw): n} over the read items - the per-class counts a count-only read is judged by. card 127-2: ocr=True | - | 471 |
| `count_only_differs` | items, n_reported, expected, derived | (differs: bool, why: str) - a count-only read is accepted only when it matches the expectation exactly. | - | 481 |
| `read_mode` | count_only, role | 'count' only for a scratch copy; the final saved file is always 'full'. | - | 495 |
| `by_design` | R, expected, plan, record=True | card chat-S5 (PD337(c), the user's "S1" item 3): a MISMATCH whose only difference is extra session-boundary items | - | 500 |
| `main` |  | (no docstring) | - | 519 |

### tools/fn_records.py

shared module; imported by 5 file(s): `tools/bench/fntest_lib.py`, `tools/bench/prep_c150_a2_4_stage_prerun_before.py`, `tools/bench/selftest_fn_f2.py`, `tools/gen_capabilities.py`, `tools/stage_prerun.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `rel` | p | (no docstring) | - | 125 |
| `locate` | fn | (file, [def qualnames], first line) of a registry function name, or (None, [], None). | - | 166 |
| `source_md5` | fn | md5 of the function's own source text (ast.get_source_segment of each def, joined) - None when not found. | - | 196 |
| `reg_path` | fn, reg_dir=None | (no docstring) | - | 216 |
| `load` | fn, reg_dir=None | (no docstring) | - | 220 |
| `write_record` | rec, reg_dir=None | (no docstring) | - | 228 |
| `status` | fn, reg_dir=None, md5_now=None | 'fresh-pass' / 'fresh-fail' / 'stale' / 'planned' / 'none' (+ the record looked at). | - | 237 |
| `add_record` | fn, st, log, labview='LabVIEW 2026', card='', reg_dir=None, md5_now=None | Append ONE result record (card chat-F3 calls this after the real run). Refuses without a plan (plan first). | - | 252 |
| `plan_set` |  | The functions whose test plans this card writes: everything the P4 v18 plans route through, the base reads of a | - | 267 |
| `predicted` | fn | (no docstring) | - | 323 |
| `legacy_for` | fn | scratch_verify records whose 'function' names this function (no src md5 -> evidence only, never fresh). | - | 333 |
| `make_plan` | fn, card='chat-F2', now=None | (no docstring) | - | 351 |
| `write_plans` | reg_dir=None, card='chat-F2' | Write (or refresh the plan of) every function in plan_set(). Existing 'records' are KEPT. | - | 375 |
| `routes_of_plan` | path | (no docstring) | - | 393 |
| `functions_for_unit` | unit | Sorted function names a stage script / stageplan JSON uses (see module docstring). | - | 408 |
| `load_config` | path=None | (no docstring) | - | 434 |
| `switch_condition` | cfg=None, reg_dir=None | (met, missing) - every function of the plans in switch.required_from has a fresh PASS record. | - | 442 |
| `launch_gate` | unit, cfg_path=None, reg_dir=None, log_path=None, now=None | (allow, line). ADVISORY in this card: logs, allows. Refuses only when mode == 'refuse', or switch.auto and the | - | 452 |
| `main` | argv=None | (no docstring) | - | 484 |

### tools/fncontract.py

shared module; imported by 6 file(s): `tools/bench/fntest_lib.py`, `tools/bench/selftest_fn_f2.py`, `tools/fn_records.py`, `tools/gen_capabilities.py`, `tools/gscript.py`, `tools/stagekit.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `PostconditionFailed` | (class) | A declared postcondition did not hold at the call. '.outcome' = the standard outcome dict. | - | 68 |
| `PostconditionValueError` | (class) | The same, for a function whose pre-existing check raised ValueError (term_index): callers that catch ValueError | - | 76 |
| `PreconditionFailed` | (class) | card chat-F3b: a DECLARED precondition (PRE) did not hold when the call failed. A RuntimeError, so every caller that | - | 85 |
| `outcome` | status, fn, reason='', measured=None, expected=None | (no docstring) | - | 94 |
| `classify_exception` | e | timed_out for the watchdog / poison family, else failed (an exception that already carries an outcome keeps it). | - | 101 |
| `outcome_of_exception` | e, fn=None | The standard outcome of an exception: its own '.outcome' when it has one, else a classified new one. | - | 111 |
| `outcome_of_text` | err_text, fn=None | For callers that only kept the error STRING (stagekit.Stage.safe): classify from the text. | - | 119 |
| `mark` |  | (no docstring) | - | 145 |
| `since` | m | (no docstring) | - | 149 |
| `worst` | ocs, fn=None | The most severe outcome in a list (ok when empty). | - | 153 |
| `evaluate` | fn, measured, post=None | (status, violations, expected) for 'measured' against the table's postconditions of 'fn' (or 'post'). | - | 171 |
| `check` | fn, msg='', raise_=None, exc=None, **measured | Evaluate 'fn''s declared postconditions on 'measured'; record the outcome; RAISE at this call when one fails and | - | 189 |
| `precondition_error` | fn, exc, ns, a, k | card chat-F3b: 'fn''s declared precondition measured after the call raised 'exc' -> a PreconditionFailed (its | - | 282 |
| `contract` | fn, f, ns=None | Wrap 'f' (the function the TABLE row 'fn' describes) so every call ends in ONE standard outcome. 'ns' = the module's | - | 302 |
| `install` | namespace, prefix | Wrap every function of module 'prefix' that the TABLE names, inside 'namespace' (the module's globals()). | - | 346 |
| `functions` | path=GSCRIPT, src=None | {name: ast.FunctionDef} of the module's TOP-LEVEL functions. | - | 376 |
| `lv_touching` | path=GSCRIPT, src=None | Public top-level functions whose call graph reaches lv/op/_run/_invoke/_err/_lv_gui or a COM method (closure). | - | 382 |
| `op_verbs` | paths=(STAGEKIT, STAGEXEC) | Every literal verb passed to 'Stage._op("<verb>", ...)' in stagekit/stagexec. | - | 405 |
| `coverage` |  | {'missing': [...], 'orphan': [...], 'no_reason': [...]} - every LabVIEW-touching public gscript function and every | - | 413 |
| `describe` | fn | One line for the generated capability table: the outcome contract of 'fn'. | - | 597 |

### tools/gate_fp.py

shared module; imported by 8 file(s): `tools/bench/diag_c146_a1_1_repro.py`, `tools/bench/selftest_c125_1.py`, `tools/bench/selftest_c131_2_tools.py`, `tools/bench/selftest_c133_1_gatefp_close.py`, `tools/bench/selftest_chat_p1.py`, `tools/bench/selftest_guard_peer_c146.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `is_checker_gate` | gate | (no docstring) | - | 60 |
| `read_queue` | path=None | (no docstring) | - | 64 |
| `log_fp` | gate, cmd, why, card, line='', log=None, path=None, cycle=None | (entry, created: bool) or raises ValueError on missing evidence. | - | 97 |
| `drain` | fp_id, fixed, selftest, path=None | (entry, None) or (None, why). | - | 126 |
| `close` | fp_id, reason, path=None | card 133-1 (PD276(d), PD282(b)): close an OPEN entry that is NOT a false positive (the refusal was CORRECT, or the | - | 150 |
| `note` | fp_id, text, path=None | card 131-2: attach a NOTE to an entry (why it stays open, who owns it). (entry, None) or (None, why). Status is | - | 172 |
| `blocking_ids` | cards_dir=None | fp ids named by a result/1 card's blocked_by.device == 'gate-fp:<id>'. | - | 187 |
| `due` | path=None, cards_dir=None, cycle=None | (due: bool, detail) - the runner's gates_due item 'gate-fp'. | - | 209 |
| `discharge_for_log` | log_path, first_line, path=None, cycle=None, record=True | (entry, None) when an OPEN checker entry names this failing log and may discharge it this cycle, else | - | 241 |
| `main` | argv=None | (no docstring) | - | 269 |

### tools/gateclass.py

shared module; imported by 13 file(s): `tools/bench/prep_c150_a2_4_stage_prerun_before.py`, `tools/bench/s2_replay.py`, `tools/bench/selftest_gateclass_s2.py`, `tools/bench/selftest_gateclass_s3.py`, `tools/bench/selftest_s5.py`, `tools/bench/selftest_t3.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `is_tunnel_class` | cls | (no docstring) | - | 63 |
| `tolerance` | predicted | max(5, 25 % of /predicted delta/), rounded up. | - | 90 |
| `is_semantic` | cls | (no docstring) | - | 95 |
| `count_verdict` | cls, measured, predicted | ('ok'/'log'/'stop', rule text) for ONE class count. | - | 99 |
| `census_verdict` | measured, declared | {'verdict': ok/log/stop, 'rows': [{class, measured, predicted, verdict, rule}]} over every class of either side. | - | 112 |
| `gate_kind` | label | (no docstring) | - | 125 |
| `classify_gate` | label, detail=None, kind=None | {'verdict': 'stop'/'log', 'kind', 'rule', 'rows'} for a FAILED gate. Never 'ok': the caller already saw ok=False; | - | 174 |
| `soft_record` | gate, cls, expected, measured, rule, script=None, path=None | Append ONE JSON line: {ts, cycle, card, script, gate, expected, measured, class, rule}. Never raises. | - | 219 |
| `record_classified` | label, c, detail=None, script=None, path=None | One soft line per non-equal class row (census/rows), or one line for a name/arith/fixture gate. | - | 232 |
| `classify_line` | line | 'log' / 'stop' for one printed '  FAIL  <label>  <detail>' line (stagekit's format); anything else -> 'stop'. | - | 258 |
| `soft_only` | segment, results | True when a failed run's ONLY failures are LOG-only gate lines: no hard marker (exception, timeout, STOP at gate, ...), | - | 272 |
| `address_only` | segment, results | True when every failing RESULT line's first_fail, and every printed FAIL / GATE FAIL line, is an address/format | - | 297 |
| `errorlist_verdict` | extra, missing, predicted_loose=0 | Error List per-class exactness is STOP for every class EXCEPT loose ends. extra/missing = item texts. | - | 317 |
| `step_face_rows_verdict` | d, sim_rows, real_rows | card chat-S3 (PD328(c), user 2026-10-03 "터널 단자행만 다를 경우 기록하자"): verdict on ONE E1 per-step diff | - | 335 |

### tools/gen_capabilities.py

shared module; imported by 3 file(s): `tools/bench/selftest_fn_f2.py`, `tools/bench/selftest_t7_capabilities.py`, `tools/doc_lint.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `rows` | reg_dir=None | [(name, args, contract, record, source)] sorted by name. | - | 72 |
| `render` | reg_dir=None | The fn-table block text (markers included) from fncontract.TABLE + fn_records. Returns a str. Self-test: selftest_fn_f2.py. | selftest_fn_f2.py | 94 |
| `split` | text | (before, block, after) - block None when the markers are absent. | - | 112 |
| `write` | doc=DOC, reg_dir=None, with_list=True, root=None | Rewrite the generated fn-table block (and, card chat-T7, the fn-list block after it - with_list) in 'doc'; returns True when | selftest_fn_f2.py | 126 |
| `imported_names` | text | Top-level module names a source text imports (static and importlib / __import__ / K.mod string forms). | - | 180 |
| `shared_files` | root=None | {rel path of a SHARED file: sorted [rel paths of the OTHER files that import it]} - the import graph over every .py under | selftest_t7_capabilities.py | 195 |
| `module_functions` | path | [(name, args, first docstring line, self-test named in the docstring, line)] of a file's public top-level functions and the | - | 233 |
| `list_rows` | root=None | [(rel path, location note, importers, [module_functions rows])] for every shared file, tools/ first then bench / recipes / | - | 253 |
| `write_shared_cache` | paths, cache=None | Write {schema capabilities-shared/1, files: [...]} to the cache guard_write reads (only when its content changes). | - | 266 |
| `render_list` | root=None | The fn-list block text (markers included): a module table of contents, then one section per shared file. | - | 281 |
| `split_list` | text | (before, list block, after) - block None when the list markers are absent. | - | 309 |
| `put_list` | text, block | 'text' with its fn-list block replaced by 'block' (appended at the end the first time). | - | 323 |
| `hook_run` | doc=DOC, state_dir=None, root=None | '--hook-run': the lock is ALREADY held by the hook that started this process. Regenerate; while the re-run flag exists, clear | - | 337 |
| `summary_line` | root=None | 'fn-table N rows; fn-list F files, M functions, U undocumented' - the counts cycle_runner's CAPABILITIES line logs. | - | 375 |
| `drift` | doc=DOC, reg_dir=None, with_list=True | {'block': bool, 'missing': [...], 'gone': [...], 'stale': [...], 'record_changed': [...], 'moved': [...], | - | 392 |
| `drift_line` | d | One printable line from a drift() dict ('' = no drift; doc_lint L12 prints it). Self-test: selftest_fn_f2.py. | selftest_fn_f2.py | 413 |
| `main` | argv=None | CLI: rewrite both generated blocks (default), --check (drift, exit 1 on drift), --summary (rewrite + the counts line | selftest_t7_capabilities.py | 428 |

### tools/gscript.py

shared module; imported by 653 file(s): `tools/allterms.py`, `tools/bench/allterms_s1.py`, `tools/bench/allterms_s2.py`, `tools/bench/allterms_s3.py`, `tools/bench/allterms_s4.py`, `tools/bench/allterms_tmscclass.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `COMPoisoned` | (class) | A previous COM call hit its hard timeout and is STILL OUTSTANDING inside LabVIEW. | - | 115 |
| `poisoned` |  | The poison record (dict) or None. Read-only; never touches COM. | - | 125 |
| `clear_poison` |  | Forget the poison WITHOUT restarting LabVIEW. Only correct when the abandoned call is known to | - | 130 |
| `lv` |  | (no docstring) | - | 220 |
| `OpHygieneRefused` | (class) | A NEW op VI (file newer than OP_HYGIENE_SINCE) has no PASS op-hygiene record matching its md5. | - | 241 |
| `hygiene_probe` | op_path | THE ONLY EXEMPTION from the op-hygiene gate: inside this block 'op(op_path)' is admitted without a record, so | - | 246 |
| `op_hygiene_record_path` | path | (no docstring) | - | 258 |
| `op_hygiene_check` | path | None if 'path' may be opened as an op VI; else the refusal text. Pure file reads, no COM. | - | 262 |
| `op` | path | A cached VI reference. Op VIs are non-reentrant, so one reference each is correct. | - | 305 |
| `lv_counts` |  | {handles, private, gdi, user} of the LabVIEW process (first instance), Nones when it is not running. | - | 329 |
| `hygiene_run` | op_path, workload, source, total=2000, per_round=100, recycle=True, check=None, warm=None, card='', log='', workload_... | THE op-hygiene measurement: 'total' calls of 'workload(copy)' (ONE op call on an open copy; returns ''/None when good, else an | - | 366 |
| `shutil_copy` | src, dst | (no docstring) | - | 436 |
| `ref_counts` |  | {opened, closed, live, cached_op_vis} - VI Server references opened by THIS process through this | - | 462 |
| `vi_ref` | target | A SHORT-LIVED, COUNTED VI reference to 'target', released when the block exits. | - | 473 |
| `reset` |  | Forget the Application AND every cached op-VI proxy. Call after LabVIEW is killed/restarted mid-script: | - | 491 |
| `cluster_array` | rows | Build the COM VARIANT for a LabVIEW '1-D ARRAY OF CLUSTERS' control. | - | 523 |
| `report` | target, cls | Every object of 'cls' on target's block diagram, as dicts with class/uid/pos/owner. | - | 698 |
| `report_all` | target, cls | Every object of 'cls' on target's block diagram in ONE op run - the array-returning form of report(). | - | 731 |
| `subvis` | target, diagram_index, purge=False, strict=True, **controls | Every subVI call on ONE diagram of 'target', as [{uid, name, path}] in one op run - the cast-free identity | - | 768 |
| `node_labels` | target, diagram_index, strict=True, **controls | The LABEL TEXT of every node on one diagram of 'target', as [{uid, label}] in one op run - cast-free | - | 830 |
| `loop_cast` | target, index, class_name='ForLoop' | A ForLoop-TYPED look at the 'index'-th loop of 'target' (Traverse class 'class_name', 'ForLoop' or | - | 869 |
| `loop_par_set` | target, index, enable, class_name='ForLoop' | WRITE ForLoop 'Is Parallelism Enabled?' (6362004) on the 'index'-th loop of Traverse class 'class_name' of | selftest_opforlooppar_v0.py | 912 |
| `add_shift_reg` | target, loop_index, y_position=120, class_name='WhileLoop' | CREATE a shift register on the loop_index-th loop of Traverse class 'class_name', returning the new | - | 940 |
| `wire_sr` | variant, target, loop_index, reg_index, node_index=None, term_index=None, ctl_index=None, class_name='WhileLoop' | Wire ONE side of the reg_index-th shift register of the loop_index-th 'class_name' loop (OpWireSR_*_v0, | - | 990 |
| `shift_reg` | target, loop_index, reg_index, class_name='WhileLoop' | The reg_index-th element of Loop.Shift Registers[] of the loop_index-th loop of Traverse class 'class_name' | - | 1036 |
| `shift_reg_left` | target, loop_index, reg_index, left_index=0, class_name='WhileLoop' | OpShiftRegs_v1: everything shift_reg() returns for the reg_index-th RIGHT register PLUS its LEFT side: | - | 1069 |
| `panel_wiring` | target | Every TOP-LEVEL front-panel object of 'target' with its diagram terminal's wiring, in one op run: | - | 1109 |
| `node_terms` | target, diagram_index, node_index | Every terminal of Nodes[node_index] on the 'diagram_index'-th Diagram of 'target', in ONE op run: | - | 1153 |
| `node_terms_uid` | target, diagram_index, node_index | (node_uid, rows) - node_terms plus the node's own UID even when it has no terminals (0 = index out of range). | - | 1208 |
| `node_terms_uids` | target, diagram_index, node_index | (node_uid, rows): node_terms' rows of Nodes[node_index] on Diagram[diagram_index] PLUS 'uid' = each Terminals[] | - | 1229 |
| `tunnels` | target, index | The 'index'-th LoopTunnel of 'target' (Traverse 'LoopTunnel' order - an access index, not an identity): | - | 1270 |
| `connect_ctl` | target, panel_index, node_index, terminal_index | Wire Nodes[node_index].Terminals[terminal_index] (a SOURCE) into the terminal of front-panel object | - | 1312 |
| `connect_ctl_ind` | target, sink_panel_index, src_panel_index | Wire the terminal of front-panel object Panel.Controls[src_panel_index] (a CONTROL, the source) into the terminal | - | 1338 |
| `count` | target, cls | (no docstring) | - | 1363 |
| `uids` | target, cls | (no docstring) | - | 1375 |
| `new_since` | target, cls, before | The objects of 'cls' that appeared since the 'before' uid set. | - | 1382 |
| `loop_diagram` | target, loop_pos, min_margin=4.0 | The body Diagram of the For Loop at 'loop_pos', selected deterministically. | - | 1400 |
| `find_at` | target, cls, pos, tol=40 | Index of the 'cls' object nearest 'pos' - the deterministic selector. | - | 1419 |
| `exit_while` | target, stop_control, diagram_index, node_index=0, output_names=(), node_class='SubVI', shift_names=() | Finish a scripted While loop: wire its conditional terminal from the front-panel Boolean control labelled | - | 1441 |
| `queue_node` | kind, target, src_cls, src_index, src_name, diagram_index, location, element_name=None | Place one queue primitive on Traverse 'Diagram'[diagram_index] of 'target' (erdosmiller Create Obtain Queue / | - | 1480 |
| `loop_in` | kind, target, diagram_index, location, src_cls=None, src_index=0, src_names=(), indexing=(), parallel=0 | Create a For ('for') or While ('while') loop on Traverse 'Diagram'[diagram_index] of 'target' (OpForLoopIn_v0 / | - | 1513 |
| `while_loop` | target, location, tunnels=(), indexing=() | Create a While loop on 'target''s top-level diagram at 'location' (erdosmiller Create While Loop.vi through | - | 1549 |
| `for_loop` | target, location, tunnels=(), indexing=(), parallel=0 | (no docstring) | - | 1568 |
| `drop_subvi` | target, subvi_path, diagram_index, location | Place 'subvi_path' on the target's 'diagram_index'-th Diagram. Get the index from find_at. | - | 1583 |
| `open_panel` | target, activate=False | Open the target's front panel - REQUIRED before wire() AND before drop_subvi(). | - | 1599 |
| `close_panel` | target | Close the target's front panel. SAVE FIRST: closing the panel of a modified VI | - | 1615 |
| `ensure_loaded` | target | Put 'target' into the state in which scripting EDITS actually land, before every edit. Idempotent, once | - | 1626 |
| `wire` | target, src_cls, src_i, src_term, dst_cls, dst_i, dst_term, branch=False | Node-to-node wire by terminal name. Call open_panel(target) first, and save | - | 1698 |
| `revert` | target | Discard a VI's in-memory changes by reloading from disk (VI method Revert). | - | 1751 |
| `copy_into` | donor, label, target, prepare=None | Copy the object labeled 'label' from 'donor' INTO 'target'. | - | 1757 |
| `restore_move_fixtures` |  | Put the two Move-example files back to their pristine bytes - ONLY when nothing of theirs is loaded (call it | - | 1823 |
| `copy_by_index` | donor, cls, index, target, expect_uid=None, finish=None | Copy the 'index'-th object of Traverse class 'cls' (report() order) from 'donor' INTO 'target' BY REFERENCE — | - | 1837 |
| `move_by_label` | donor, label, harvest_to=None | Copy the GObject labeled 'label' out of 'donor' via OpMoveByLabel_v0. | - | 1919 |
| `ensure_move_files_pristine` |  | Restore the Move example's Test-Source if a previous run left a donor in it. | - | 1965 |
| `remove_bad_wires` | target | Edit > Remove Broken Wires on 'target' (the Ctrl+B cleanup). | - | 1987 |
| `delete_by_label` | target, label, allow_broken=False | Delete the object labeled 'label' from 'target' (Generic:Delete). | - | 2023 |
| `exit_loop` | target, node_index, output_names, diagram_index, node_class='SubVI' | Create AUTO-INDEXED output tunnels for 'output_names' of a node inside a loop. | - | 2079 |
| `wire_indicators` | target, node_index, src_terms, indicator_names, diagram_index=0, node_class='SubVI' | Branch a node's output terminals onto EXISTING front-panel indicators by label. | - | 2114 |
| `loop_kernel` | target, location, control_names, kernel_path, input_names, parallel=4 | ONE call: parallel For Loop + kernel subVI inside + named tunnel wiring. | - | 2162 |
| `set_index_mode` | target, tunnel_index, mode | Write a LoopTunnel's IndexMode in 'target' (0 = regular/non-indexed, 1 = auto-indexed). | - | 2213 |
| `tunnel_indicator` | target, tunnel_index | Create a front-panel INDICATOR wired to LoopTunnel[tunnel_index] of 'target', typed by LabVIEW. | - | 2240 |
| `wire_control` | target, control_names, dst_cls, dst_i, dst_terms, branch=False, src_diagram_index=0 | Wire FRONT-PANEL CONTROLS to a node's named inputs - the one thing OpWire_v1 | - | 2286 |
| `wire_const` | target, src_cls, src_i, dst_cls, dst_i, dst_term_index, labels=None | A BARE DIAGRAM CONSTANT as the SOURCE of a new wire (card 85-1, Pre-decided 188(c)). | - | 2340 |
| `wire_const_sr` | target, const_cls, const_i, loop_cls, loop_i, face_index, labels=None | Card 123-3 S2 (PD246(e)): SHIFT-REGISTER INITIALISATION - a bare diagram constant -> the LEFT register's OUTER face. | - | 2351 |
| `loop_face_index` | target, diagram_uid, loop_uid, face_uid | The Terminals[] index of terminal #face_uid on loop #loop_uid (a node of Diagram #diagram_uid), by UID ECHO through | - | 2362 |
| `sr_init_const` | target, loop_uid, face_uid, diagram_uid, donor, pos=(40, 40), loop_cls='WhileLoop' | Card 123-3 S2 (PD246(c) A3 / (e)): INITIALISE a shift register from a VALUED constant on the loop's OWNER diagram. | - | 2377 |
| `wire_ctlsink` | target, ct_i, src_cls, src_i, src_term_index, labels=None | PD191(a): a FRONT-PANEL TERMINAL as the SINK (Connect Wire invoked on it), a bare node terminal as the source. | - | 2408 |
| `wire_tunouter` | target, tun_cls, tun_i, dst_cls, dst_i, dst_term_index, labels=None | PD191(b): a structure TUNNEL's OUTER face as the source, addressed by the TUNNEL (never by its owner's Terminals[]). | - | 2418 |
| `exec_state` | target | (no docstring) | - | 2457 |
| `gui_save` | target | Save a BROKEN VI by focusing its window and sending Ctrl+S. | - | 2470 |
| `save` | target, allow_broken=False | Persist the in-memory edits. Guarded to claudeDev + explicit allowlist: an | - | 2595 |
| `build_kernel` | target, loop_at=(4000, 300), parallel=4, tunnel='Array of cal clusters', bead_vi='Track 1 of N bds xyz-kernel-reentra... | SUPERSEDED by loop_kernel(). Places an UNWIRED loop + kernel; kept for regression. | - | 2615 |
| `main` |  | (no docstring) | - | 2664 |
| `build_invoke` | target, cls, method_id, location, diagram_index=0 | Create an Invoke Node on 'target''s diagram: class 'cls' ("VI Server:Terminal", "VI Server:VI", | - | 2692 |
| `build_property` | target, cls, props, location, diagram_index=0 | Create a Property Node on 'target''s diagram: class 'cls' ("VI Server:GObject", ...), | - | 2727 |
| `delete_object` | target, cls, index, verify=True | Delete the 'index'-th object of Traverse class 'cls' on 'target' (Generic.Delete over a | - | 2808 |
| `move_object` | target, cls, index, position | Move the 'index'-th object of class 'cls' (Traverse order, same as report()) on 'target' to the | - | 2869 |
| `build_index_array` | target, location, source_terminal_index=0 | Place an Index Array primitive on 'target''s top-level block diagram at 'location' (erdosmiller | - | 2892 |
| `node_rank` | target, uid | WRONG in general — kept as a warning. Nodes[] is CREATION order; uid rank matched it on GUIBENCH_v0 only | - | 2922 |
| `create_control` | target, node_index, terminal_index | Create a front-panel control wired to terminal 'terminal_index' (Node.Terminals[] order = the Context | - | 2930 |
| `create_indicator` | target, node_index, terminal_index | Indicator wired to terminal 'terminal_index' of Nodes[node_index] (Terminal.Create Indicator 6349C02 — | - | 2958 |
| `create_const_loop_term` | target, kind, index, value=None, term_index=0 | A DIAGRAM CONSTANT, typed by the sink and already wired, on a LOOP-OWNED terminal (task 77-2, 2026-09-25). | - | 2983 |
| `connect_terminals` | target, sink_node, sink_term, src_node, src_term | Wire Nodes[src_node].Terminals[src_term] (source) into Nodes[sink_node].Terminals[sink_term] (sink) on | - | 3028 |
| `fp_labels` | target, max_n=200 | [(index, label, is_indicator)] for every front-panel object of 'target' in tabbing order | - | 3058 |
| `node_info` | target, max_n=400 | [(Nodes[] index, style name, label text)] for the top-level block-diagram nodes of 'target' in | - | 3080 |
| `remove_bad_wires_scripted` | target | LabVIEW's Ctrl+B by script: VI.'Block Diagram:Remove Bad Wires' (410) on 'target' (OpRemoveBadWires_v0, | - | 3104 |
| `net_map` | target, diagram_index=0, max_nodes=200, max_terms=40 | Connectivity of one diagram of 'target' (Traverse "Diagram" index; 0 = top level), read headlessly with | - | 3123 |
| `print_net_map` | nodes, nets | (no docstring) | - | 3227 |
| `set_auto_error_handling` | target, enabled | Write VI.'Automatic Error Handling' (242) of 'target' — OpSetAutoErr_v0 (2026-09-07). FALSE silences the | - | 3238 |
| `connect2` | target, diagram_index, sink_node, sink_term, src_node, src_term | Wire top-level Nodes[src_node].Terminals[src_term] into Nodes[sink_node].Terminals[sink_term] of ANY diagram | - | 3254 |
| `set_node_label` | target, diagram_index, node_index, text | Write the label of Nodes[node_index] of Traverse "Diagram"[diagram_index] on 'target' (OpSetLabel_v0, built by | - | 3277 |
| `move_out` | target, diagram_index, node_index, position | Move Nodes[node_index] of Traverse "Diagram"[diagram_index] to the TOP-LEVEL diagram of 'target' at 'position' | - | 3295 |
| `build_clfn` | target, location, dll, fn, flat_hex, calling_convention=0, reentrant=True | Place a CLFN on 'target' calling 'fn' of 'dll' with the parameter list 'flat_hex' (flattened Parameter Info array, | - | 3317 |
| `conpane` | target, max_terminals=32 | The connector pane of 'target' as {terminal index: control label}, with None for a FREE terminal (OpConPane_v0, | - | 3365 |
| `replace_object` | target, uid, new_path | Swap the object 'uid' on 'target''s diagram for the subVI (or control) at 'new_path', in place - the callee-swap | - | 3396 |
| `conpane_assign` | target, control_label, terminal_index | Assign the front-panel control 'control_label' of 'target' to connector-pane terminal 'terminal_index' | - | 3422 |
| `make_default` | target, values=None | Set 'values' ({control label: value}) on 'target' through VI Server, then make ALL current front-panel values the | - | 3456 |
| `build_case` | target, location, selector_name, input_names=(), frame_names=('0, Default', '1') | Place a Case Structure on 'target''s top-level diagram (erdosmiller 'Create Case Structure.vi' via OpBuildCase_v1, | - | 3498 |
| `connect_nested_v2` | target, sink_diag, sink_node, sink_term, src_diag, src_node, src_term, labels=None | Wire Diagram[src_diag].Nodes[src_node].Terminals[src_term] (SOURCE) into | - | 3531 |
| `case_frames` | target, case_uid | T1 READER (OpCaseFrames_v1): CaseStructure #case_uid -> {'echo', 'names' (Frame Names 6365002, frame order), | - | 3666 |
| `case_in` | target, diagram_uid, location, selector_label, frame_names=('0, Default', '1'), position=None | T1: a Case Structure OWNED BY a nested diagram (a For/While body), addressed by the diagram's UID. | - | 3695 |
| `tunnel_use_default_at` | target, cls, index, value | T5 by Traverse (cls, index): OpTunnelUseDefault_v0 casts to ConditionalTunnel, READS 5D251C00, WRITES 'value', | - | 3733 |
| `tunnel_use_default` | target, tunnel_uid, value, cls='SelectorTunnel' | T5: set 'Use Default if Unwired' (ConditionalTunnel 5D251C00, NAMES.md:1036) on case tunnel #tunnel_uid and read | - | 3749 |
| `set_control_label` | target, panel_index, text | T4: write the LABEL of front-panel object Panel.Controls[panel_index] (= panel_wiring row order) through | - | 3758 |
| `set_default_in_memory` | target, label, value, probe_value | T4 default: SetControlValue(label, value) -> OpMakeDefault_v0 (VI 'Make Current Values Default' 3F3, ALL controls) | - | 3775 |
| `c97_collapsed` | rows, tunnel_uids | {(source term uid, sink term uid)} with each tunnel in 'tunnel_uids' collapsed to a pass-through. | - | 3803 |
| `MoveIntoFrameBroken` | (class) | move_into_frame's post-edit gate refused (card 98-2 PD207(c); card 98-3 PD208(c)); '.result' holds the full | - | 3815 |
| `MoveIntoFrameRefused` | (class) | PD208(c)(1) PRECONDITION (card 98-3): ExecState was not 1 BEFORE the move, so the verb refused BEFORE ANY EDIT - | - | 3824 |
| `wire_health` | target, rows=None | READER (card 98-2): {wires, wired, termless, exec_state} of 'target'. termless = Wire objects that carry NO terminal | - | 3835 |
| `move_into_frame` | target, frame_uid, members, spot=(0, 0), log=None, expect_broken=False, _skip_rbw=False | PD208(c) (card 98-3; AMENDS card 98-2's PD207(c) termless-only deletion, which left ExecState 0 after move A - | selftest_c98_stage | 3846 |
| `move_into_frame_finish` | target, frame_uid, r, log=None, expect_broken=False, _skip_rbw=False | PD208(c)(2)-(4), the post-move step of move_into_frame (see its docstring). 'r' = _move_into_frame's result, or | - | 3877 |
| `create_indicator_nested` | target, node_uid, terminal_index | V1: an INDICATOR wired to Terminals[terminal_index] of node #node_uid on ANY diagram (Terminal.Create Indicator | - | 4166 |
| `create_control_nested` | target, node_uid, terminal_index, value=None | V2: a CONTROL wired to Terminals[terminal_index] of node #node_uid on ANY diagram (Terminal.Create Control | - | 4349 |
| `set_visible` | target, uid, visible | V3: write Control.Visible of front-panel object #uid (a panel_wiring row uid) and READ IT BACK in the same op | - | 4365 |
| `read_bool_const` | target, uid | V4: the value of BooleanConstant #uid (Constant.Value 634AC00 on a BooleanConstant-TYPED node - the base class | - | 4391 |
| `read_const_value` | target, uid | Card 118-4 R1 (PD234(j)(1)): READ-ONLY value + type of diagram constant #uid, class found by traverse membership. | - | 4417 |
| `const_class_index` | target, uid | (class, Traverse index) of constant #uid: the first CONST_IND_CLASSES listing that holds it, else ValueError. | - | 4520 |
| `create_indicator_on_const` | target, const_uid, label=None | card 122-3: a NEW indicator wired to the output terminal of diagram constant #const_uid (any diagram) through | - | 4529 |
| `const_indicator_on_diagram` | target, diagram_uid, donor, label, pos=(40, 40) | card 122-3 ROUTE (PD241(a)): a VALUED constant on Diagram #diagram_uid (any nesting depth; a flat-sequence frame | - | 4571 |
| `parse_type_descriptors` | b | The TYPE half of a flattened LabVIEW variant (layout measured, docs/NAMES.md:1153-1155): U32 version, I32 nTDs, | - | 4591 |
| `read_term_type` | target, term_uid, index=None | Card 120-2 T2 (PD237(k)): READ-ONLY data type of terminal #term_uid (any GObject of class Terminal, e.g. a node's pin, | - | 4646 |
| `wire_joints` | target, wire_uid, index=None | Card 117-1 S0a: 'Wire.Joints[]' 6371005 of Wire #wire_uid through OpWireJoints_v1 (md5 29dcb59f...; built by | - | 4679 |
| `create_local_read` | target, panel_index, dest_diagram_uid=None, position=(40, 40) | Cycle 102 (stage_d1_disp_r6.log:544,572,595): the READ twin of create_local_write - OpCreateLocalRead_v0 with | - | 4707 |
| `create_local_write` | target, panel_index, dest_diagram_uid=None, position=(40, 40) | V5 core: a Local Variable in WRITE mode bound to Panel.Controls[panel_index] (OpCreateLocalRead_v0 with | - | 4715 |
| `create_primitive_nested` | target, diagram_uid, prim_name, pos, donor=None | V6 (card 100-4, PD213(b)): place primitive 'prim_name' on Diagram #diagram_uid of 'target' (ANY nesting depth) | - | 4790 |
| `fs_donor` |  | {'donor': claudeDev\DonorFs_v0.vi, 'uid': its FS uid} for struct_copy_nested (a 1-frame, EMPTY Flat Sequence). | - | 4904 |
| `fs_frames` | target, fs_uid, max_frames=200 | OpFsDiagrams_v0: the frame Diagram uids of Flat Sequence #fs_uid, LEFT TO RIGHT (Diagrams[] index k = 0, 1, ... until the | - | 4910 |
| `fs_add_frame` | target, fs_uid, ref_index, after=True | OpFsAddFrame_v0: FlatSequence.Add Frame 3578B800 on Flat Sequence #fs_uid ('Reference Frame Index' = ref_index, 'After(T)'); the | - | 4933 |
| `wire_remove_loose_ends` | target, wire_uid, index=None | 'Wire.RemoveLooseEnds' (6370C08) on Wire #wire_uid of 'target' through OpWireRemoveLooseEnds_v0. 'index' = the | - | 4980 |
| `term_index` | target, diagram_uid, node_uid, name, is_source | Card 123-7 (PD248(b)): (diagram index, node index, terminal index, row) of the ONE terminal named 'name' with direction | - | 4999 |
| `struct_copy_nested` | target, diagram_uid, cls, donor, pos=(40, 40) | Copy structure 'donor['uid']' (class 'cls') of the claudeDev file 'donor['donor']' onto Diagram #diagram_uid of 'target' | - | 5016 |
| `case_wired` | target, diagram_uid, src_node_uid, src_term, pos=(40, 40), donor=None | Card 123-5 S1: a Case structure on Diagram #diagram_uid whose SELECTOR is wired from output terminal 'src_term' (name) | - | 5078 |
| `connect_term_uid` | target, sink_uid, src_uid | OpConnectTermUid_v0: Terminal.Connect Wire on terminal #sink_uid with Wire Source = terminal #src_uid (any owner, any | - | 5141 |
| `case_inner_face` | target, tunnel_uid, frame_index | The inner terminal of tunnel #tunnel_uid in frame 'frame_index' of its case (case_frames' Frames[] order; a boolean | - | 5166 |
| `case_frame_wire` | target, case_uid, frame_index, src, dst | A wire on frame 'frame_index' of case #case_uid. 'src' / 'dst' = {"tunnel": uid} (that tunnel's inner face in this | - | 5187 |

### tools/hash_probe.py

shared module; imported by 64 file(s): `tools/bench/c52_astcheck.py`, `tools/bench/diag_c60_castseed_probe.py`, `tools/bench/diag_c60_n4_localbinding.py`, `tools/bench/diag_c61_localdir.py`, `tools/bench/diag_c61_localdir_write.py`, `tools/bench/diag_c61_localdir_write2.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `probe` | path | (no docstring) | - | 19 |
| `main` |  | (no docstring) | - | 36 |

### tools/jev.py

shared module; imported by 33 file(s): `tools/addrcheck.py`, `tools/audit_cycle.py`, `tools/bench/diag_c106d_jevrc2.py`, `tools/bench/jev_discharge_trial.py`, `tools/bench/jev_gate.py`, `tools/bench/jev_ladder_c89.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `get_key` |  | (no docstring) | - | 33 |
| `ask` | state, questions, purpose='unspecified', timeout=60, retries=3 | POST one request. Returns (response_dict, None) or (None, error_string). Never raises. | - | 64 |
| `samples` | default=SAMPLES_DEFAULT | How many times one question is asked before its answer is used. 'JEV_SAMPLES' overrides (1..25). | - | 104 |
| `ask_n` | state, questions, n=None, purpose='unspecified', timeout=60, retries=3 | CONSENSUS: ask ONE question 'n' times (sequentially, each with ask()'s own retries) and average. | - | 115 |
| `noul` | resp, name=None | The yes-probability of a noul answer (by question name when given), or None. | - | 179 |
| `choice` | resp, name | (chosen option, probabilities dict) of a choice answer, or (None, None). | - | 199 |
| `verdict` | p | 'yes' / 'no' / 'unknown' from a probability, using the project's unknown band. | - | 208 |
| `normalise` | s | (no docstring) | - | 229 |
| `summarise_failure` | logpath, run_index=-1 | Compact failure summary of ONE bgrun log's LAST run: script, how it ended, first FAIL line + context (or | - | 237 |
| `same_failure_class` | summary_a, summary_b, purpose='same-failure-class', n=None | Probability that two failure summaries are the same failure class (measured 92.5 % / Brier 0.059 on the | - | 305 |

### tools/jev_candidates.py

shared module; imported by 106 file(s): `tools/bench/c73_l7r_live.py`, `tools/bench/cdiff_blindspot_74.py`, `tools/bench/cdiff_frame_80_probe.py`, `tools/bench/ct23541_facts_80.py`, `tools/bench/dedupe_check_s2b.py`, `tools/bench/diag_c104_e3.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `node_labels_default` |  | (no docstring) | - | 63 |
| `load` | key, fs=True | The step-4 graph of one wiki VI, built exactly as tools/bench/diag_vigraph_check.py builds it | - | 73 |
| `from_parts` | rec, objs, loops, labels, fs_pairs, key | The same graph from parts already in memory (a LIVE read of a scratch VI: 'rec' needs 'terminals' and, | - | 87 |
| `diagram_tree` | G | {parent: {child: parent}, exclusive: {frame: frozenset(sibling frames of the same case)}}. | - | 102 |
| `scope` | G, da, db | (relation, borders) between two diagrams. borders = structure borders a wire would cross. | - | 133 |
| `structure_terminals` | G, struct_uid | HEURISTIC: the border-tunnel group of a structure = tunnels sharing inner frames, the group chosen by a | - | 157 |
| `resolve` | G, end | An intent end -> ([node uids], method). | - | 180 |
| `sink_state` | G, r | (no docstring) | - | 194 |
| `cut_input_tunnel` | G, node | FACT RULE (judgement 2026-09-23 16:xx, measured by bench 5b B run 2): a Selector/Loop tunnel whose OUTER | - | 206 |
| `term_row` | G, key | (no docstring) | - | 223 |
| `candidates` | G, intent | Every legal pair for ONE intent row. Returns {intent, resolved, pairs:[...], excluded:{reason: n}}. | - | 236 |
| `map_key` | G, key_other, G_other | The key in G of a terminal named by 'key_other' in another graph (Pre-decided 137: node uid + terminal | - | 272 |
| `s1_chains` | S1, node_uid | RULE-CHAIN-S1 (CLAUDE.md §3 "Stages are SIMULATED", decision 3; docs/stage-simulator-plan.md "Decide per row"): | - | 288 |
| `chain_terminals` | S1, node_uids | {(uid, term)} every terminal a RULE-CHAIN-S1 chain of these nodes owns - the node's out/in ends and the | - | 327 |
| `rule_chain_s1` | S1, node_uid, new_sr | The chain rows for 'node_uid' moved into a new loop whose new register pairs are 'new_sr' | - | 340 |

### tools/jev_chain.py

shared module; imported by 1 file(s): `tools/bench/jev_menus_step5.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `subvi_nodes_in_scope` | G, root_diagram | SubVI call nodes whose terminals sit on 'root_diagram' or on any diagram below it in the tree. | - | 47 |
| `direct_successors` | G, y | SubVI nodes reached from y's outputs without passing THROUGH another subVI node. | - | 57 |
| `reaches` | G, a, b | (no docstring) | - | 75 |
| `true_next` | G, y, z, x | (no docstring) | - | 79 |
| `subvi_line` | G, u | (no docstring) | - | 83 |
| `ask_link` | G, y, z, x, n=None | (no docstring) | - | 91 |
| `build_chain` | G, y, z, root_diagram, max_steps=8, n=None, th=None | Follow Jev one step at a time. Returns {steps:[{at, scored, chosen, action}], reached, jev_calls}. | - | 96 |
| `scope_counts` | G, root | (no docstring) | - | 124 |

### tools/jev_contradict.py

shared module; imported by 3 file(s): `tools/audit_cycle.py`, `tools/bench/jev_wave2b_trials.py`, `tools/bench/jev_wave4_selftest.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `parse_items` | path=PLAN | [{'id','title','body','text'}] - every top-level numbered item in the document, in order. | - | 72 |
| `build_pairs` | items, per_item=8, min_shared=2, cap=400, df_frac=0.15 | [(score, i, j)] with j < i: the most-overlapping earlier item for each item, capped and sorted. | - | 106 |
| `ask_pair` | a_text, b_text, samples=3, timeout=25, retries=0, purpose='contradict' | (mean p, [samples], err). 3-sample consensus by default (second-wave #6). | - | 129 |
| `main` | argv=None | (no docstring) | - | 158 |

### tools/jev_device_value.py

shared module; imported by 2 file(s): `tools/bench/jev_device_value_labels.py`, `tools/bench/selftest_jev_device_value.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `corpus` | since=None | (no docstring) | - | 39 |
| `classify` | device, items, n=None, workers=4, ask=None | (no docstring) | - | 70 |
| `totals` | rows | (no docstring) | - | 81 |
| `main` | argv=None | (no docstring) | - | 93 |

### tools/jev_drift.py

shared module; imported by 4 file(s): `tools/bench/jev_wave2b_trials.py`, `tools/bench/jev_wave3a_trials.py`, `tools/bench/selftest_guard_bash_jev.py`, `tools/hooks/guard_bash.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `next_block` | status_path=STATUS, maxchars=NEXT_MAX, text=None | THE WHOLE '## NEXT' section of STATUS.md, blank lines dropped, bullets kept IN ORDER, truncated to | - | 107 |
| `first_act` | status_path=STATUS, maxchars=FIRST_ACT_MAX, text=None | SUPERSEDED IN THE LIVE PATH 2026-09-22 by next_block(); KEPT because tools/bench/jev_wave2b_trials.py is | - | 128 |
| `recent_commands` | n=5, marker_log=MARKER_LOG | The last n commands this project's material-marker recorded, oldest first. [] on any failure. | - | 158 |
| `is_run_command` | cmd | True when the command RUNS something (bgrun / a recipe or bench script / a peer dispatch). | - | 172 |
| `judge` | cmd, act=None, recent=None, timeout=20, retries=0, purpose='drift', n=None | (p, what, err). p is the CONSENSUS mean probability that the command advances something the cycle's | - | 215 |
| `advisory` | cmd, sid='0', write_log=True | The hook entry point. Returns the advisory line (also written to stderr and jev_gate.log) or None. | - | 249 |

### tools/jev_gaterow.py

shared module; imported by 10 file(s): `tools/bench/jev_gate.py`, `tools/bench/jev_ladder_c89.py`, `tools/bench/jev_ladder_c89b.py`, `tools/bench/jev_ladder_c90.py`, `tools/bench/jev_ladder_remeasure.py`, `tools/bench/jev_wave2a_trials.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `classify` | state, purpose='gaterow', n=None, timeout=60, retries=3 | (class, mean probability, spread) for ONE row's state. Never raises. | - | 37 |
| `main` | argv | (no docstring) | - | 49 |
| `verdicts_for` | logpath, run_index=-1, max_rows=5, n=2, timeout=25, retries=1 | The gate-row verdicts of one run as a compact text block, for the review ladder's state. Never raises. | - | 91 |

### tools/jev_pairs.py

shared module; imported by 7 file(s): `tools/bench/jev_l7_1_offline.py`, `tools/bench/jev_menus_step5.py`, `tools/jev_chain.py`, `tools/recipes/stage_d1_l7_1.py`, `tools/recipes/stage_d1_l7_1b.py`, `tools/recipes/stage_d1_l7_r.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `thresholds` |  | (no docstring) | - | 46 |
| `subvi_record` | name | The wiki JSON of a subVI by its call-node name ('X.vi'), or None when it is not in the wiki. | - | 69 |
| `wiki_line` | t | ONE line for one terminal row (jev_candidates.term_row): node, class, subVI name + the matching | - | 83 |
| `pair_state` | intent_line, c | (no docstring) | - | 121 |
| `ask_pair` | intent_line, c, n=None | (no docstring) | - | 130 |
| `op_options` | c | <= 3 exclusive options, chosen by the row's CLASSES only (a hard fact, not a ranking). | - | 163 |
| `op_rule` | c, top_diagram=None | PRE-DECIDED 143 as code: the writer op chosen by the row's CLASSES; (op, variant, why) or (None, None, why) | - | 181 |
| `op_question` | opts | (no docstring) | - | 223 |
| `op_state` | c | (no docstring) | - | 233 |
| `ask_op` | c, n=None | (no docstring) | - | 241 |
| `ask_risk` | change_line, evidence, n=None | (no docstring) | - | 269 |
| `risk_evidence` | G_orig, G_new, c, orig_sink_key=None | Code-computed rule-1a evidence for wiring candidate c in G_new: the effective computation sources of the | - | 275 |
| `decide` | intent_line, cand, G_orig=None, G_new=None, orig_sink_key=None, n=None, th=None, by_rule=False, risk_gates=True, top_... | Run PAIR over every candidate, then OP and RISK on the chosen one. Returns one decision dict. | - | 289 |
| `write_record` | stage, bed_md5, intents, cands, decisions, t0, extra=None | (no docstring) | - | 370 |

### tools/jev_preflight.py

shared module; imported by 3 file(s): `tools/bench/jev_wave2b_trials.py`, `tools/bench/selftest_guard_bash_jev.py`, `tools/hooks/guard_bash.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `static_checks` | path | The five checks. Returns (dict of results, list of one-line findings). Never raises. | - | 155 |
| `classify` | path, timeout=25, retries=0, purpose='preflight' | (cls, p, findings, res, err). ONE Jev choice over the head + the static findings. | - | 228 |
| `line_for` | path, timeout=25 | The one-line advisory, or None. Never raises. | - | 250 |
| `advisory` | script_path, write_log=True | The hook entry point: print and log one line for a recipe/stage launch. Returns the line or None. | - | 263 |
| `main` | argv=None | (no docstring) | - | 281 |

### tools/jev_rowcheck.py

shared module; imported by 3 file(s): `tools/bench/jev_wave2b_trials.py`, `tools/bench/jev_wave4_selftest.py`, `tools/stagekit.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `load_tables` | sources=SOURCES, nodeterms=NODETERMS | (rows, by_uid) - the 109 cut-terminal rows and a uid -> list-of-measured-entries index. | - | 79 |
| `row_text` | row | One readable line for a planned row. | - | 114 |
| `entries_for` | row, by_uid, limit=12 | (measured source entries, measured sink entries) - only the rows mentioning that uid. | - | 122 |
| `check_row` | row, by_uid, timeout=25, retries=0, purpose='rowcheck' | (p, verdict, err). verdict is 'ok' / 'suspect' / 'unknown' by the project's band. | - | 130 |
| `normalise_row` | row | Either accepted schema -> the schema 'check_row' reads (shape A), or None when neither fits. | - | 185 |
| `check_rows` | rows, by_uid=None, limit=None, budget_s=60.0, timeout=20, retries=0, purpose='rowcheck-stage' | Judge an IN-MEMORY row list. Returns [{i,label,verdict,p,err,text}]. Never raises, never blocks. | - | 206 |
| `stage_lines` | rows, stage_name, by_uid=None, limit=None, budget_s=60.0, write_log=True | The stagekit entry point: one 'JEV-ROWCHECK / <stage> / <row> / <class> p=<p>' line per row. | - | 252 |
| `main` | argv=None | (no docstring) | - | 285 |

### tools/launchunit.py

shared module; imported by 7 file(s): `tools/bench/prep_c150_a2_4_stage_prerun_before.py`, `tools/bench/selftest_c111c_launchunit.py`, `tools/hooks/guard_bash.py`, `tools/hooks/guard_card.py`, `tools/hooks/guard_cycle.py`, `tools/stage_prerun.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `segments` | cmd | The command split into shell segments (&& // ; / newline), a line continuation (bash '\', PowerShell backtick) | - | 38 |
| `norm` | p, root=None | A path token -> normcase absolute path (relative ones against root). | - | 52 |
| `module_file` | mod, root=None | The project file '-m <mod>' would run from the project root, or None (a/b -> a/b.py / a/b/__main__.py / | - | 57 |
| `units` | cmd, root=None | Every python unit of the command: dicts {kind: 'script'/'module'/'module_arg', path, module, seg}. | - | 69 |
| `arg_is_launch` | mod, root=None | True unless '-m <mod>' only READS its arguments: mod in READONLY_MODULES and not a project-file shadow. | - | 114 |
| `launched_py` | cmd, root=None | Every script path the command RUNS: 'py X.py' (past interpreter flags, also after bgrun's '--'), a '-m' module | - | 119 |
| `module_arg_counts` | cmd, root=None | Counter {norm(path): n} of the .py tokens that are only ARGUMENTS of a read-only '-m' module. | - | 127 |
| `drop_module_args` | cmd, paths, root=None | The card-flag filter (guard_card): 'paths' = one entry per place another detector saw a launched .py. An entry | - | 133 |
| `cd_only_to_root` | cmd, root=None | True when every 'cd' segment of the command targets the project root (or there is none). | - | 155 |
| `module_arg_segment` | seg, whole_cmd='', root=None | stop_record's read-only credit for ONE segment: it is exactly 'py[thon][N.N][.exe] [flags] -m <module> args' | - | 167 |

### tools/logclass.py

shared module; imported by 17 file(s): `tools/audit_cycle.py`, `tools/bench/diag_c131_2_offline.py`, `tools/bench/diag_c78_rowd_writer.py`, `tools/bench/diag_d0_gate_probe.py`, `tools/bench/jev_discharge_trial.py`, `tools/bench/jev_trial.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `command_kind` | cmd | "review" / "jev" / "build" / "" for a bgrun command string (see the block comment above). | - | 116 |
| `log_kind` | path | The log's class from its OWN last BGRUN START command: "review" / "jev" / "build" / "" (use the filename). | - | 141 |
| `is_review_log` | path | Written by the review machinery. Excluded from build accounting AND from failure scanning. | - | 146 |
| `is_build_log` | path | Records an attempt to build or measure the artefact - the thing a cycle is made of. | selftest_logclass_recipebuild | 153 |
| `last_bgrun_command` | path | The command string of the log's LAST 'BGRUN START' line, or "" when the file has none. | - | 178 |
| `is_recipe_build_log` | path | True only when this log's OWN last run INVOKED a 'tools/recipes/*.py' file. | selftest_guard_peer_jev | 191 |
| `command_program` | cmd | The PROGRAM a bgrun command line invokes - lower-cased basename, "" for an empty command. | - | 234 |
| `is_judgement_session_log` | path | True when this log records a whole JUDGEMENT SESSION spawned by 'tools/cycle_runner.py'. | - | 248 |
| `split` | paths | (build_logs, machinery_logs) for cycle accounting - watchdog records group with the machinery. | - | 268 |

### tools/lv_errorlist.py

shared module; imported by 5 file(s): `tools/bench/diag_c100_verbs_build.py`, `tools/bench/diag_c89_profiler_leg.py`, `tools/bench/diag_errorlist_v0.py`, `tools/errorlist_check.py`, `tools/recipes/stage_d1_m3a4.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `lv_pid` |  | (no docstring) | - | 87 |
| `top_windows` | pid=None | [(hwnd, title, class, (l,t,r,b))] for every visible top-level window (of 'pid' if given). | - | 106 |
| `child_windows` | hwnd | Win32 CHILD hwnds - the measurement of whether the dialog is owner-drawn (no children). | - | 127 |
| `UIA` | (class) | (no docstring) | - | 147 |
| `UIA.from_hwnd` | hwnd | (no docstring) | - | 156 |
| `UIA.focused` |  | (no docstring) | - | 159 |
| `UIA.value` | el | (no docstring) | - | 172 |
| `UIA.text` | el | (no docstring) | - | 179 |
| `UIA.legacy` | el | (no docstring) | - | 186 |
| `UIA.selected` | el | (no docstring) | - | 199 |
| `UIA.select` | el | (no docstring) | - | 206 |
| `UIA.set_focus` | el | (no docstring) | - | 213 |
| `UIA.node` | el | One element as a plain dict - everything we can read about it. | - | 220 |
| `UIA.tree` | el, depth=0, maxdepth=14, out=None, path='0' | Full RawView tree as a flat list of dicts with a path - scroll cannot hide a row. | - | 237 |
| `msaa_rows` | hwnd, max_children=400 | [{childid, name, value, role, role_name, state, rect}] for hwnd's client object. [] if none. | - | 269 |
| `shot` | tag, acts | Full-screen capture. Read-only, needs no gate. Returns (path, md5). | - | 334 |
| `ensure_foreground` | wtitle, hwnd, acts, tag | The dialog must BE the foreground before any keystroke; SendKeys goes to whatever is. | - | 387 |
| `send_keys` | key, acts, tag, wait_ms=900 | (no docstring) | - | 409 |
| `ocr_engine` |  | (callable, name). RapidOCR if installed, else Windows.Media.Ocr, else (None, 'unavailable'). | - | 430 |
| `ocr_lines` | img, scale=3, invert=False, pad=10 | [(text, conf, y0, y1, x0)] in the ORIGINAL image's coordinates. [] when no engine. | - | 479 |
| `layout` | img | LOCATE the dialog's parts ON THE CAPTURE (never from remembered offsets). | - | 511 |
| `read_by_capture` | R, wtitle, acts, log, max_steps=None, hwnd=None, on_item=None | METHOD B. Walk the list one row at a time; each step: capture -> LOCATE the highlighted row by | - | 585 |
| `read` | vi_path, out_json=None, maxdepth=14, dump_tree=True, log=print, on_item=None, max_steps=None | Open the Error List for 'vi_path' (already in memory), read every item, close it. | - | 798 |
| `refine_rows` | R, log=print | Re-read each row from the capture in which it is NOT highlighted. OFFLINE - no LabVIEW. | - | 1088 |
| `main` |  | (no docstring) | - | 1163 |

### tools/lvclick.py

shared module; imported by 4 file(s): `tools/bench/m3v1_verify.py`, `tools/recipes/build_keystone.py`, `tools/recipes/build_keystone_invoke.py`, `tools/recipes/keystone_discovery.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `geom` |  | (no docstring) | - | 33 |
| `save_geom` | d | (no docstring) | - | 37 |
| `lv` | *args, timeout=60 | (no docstring) | - | 43 |
| `act` | action, **kw | Gated input action (click/rclick/drag/keys) — always logged by lv_gui. | - | 53 |
| `windows` |  | (no docstring) | - | 63 |
| `toplevel` |  | [(enabled, hwnd, (l,t,r,b), title)] for every visible window of the LabVIEW process — | - | 67 |
| `rect` | title | (no docstring) | - | 79 |
| `probe_runs` | x, y, x2=None, y2=None | [(start, end, 'RRGGBB'), ...] along a row (x..x2 at y) or a column (y..y2 at x). | - | 86 |
| `dominant_rgb` | runs | (no docstring) | - | 97 |
| `Viewport` | (class) | (no docstring) | - | 106 |
| `Viewport.s` | x, y | diagram -> screen | - | 110 |
| `node_pos` | target, uid, cls | (no docstring) | - | 118 |
| `calibrate` | target, title=None | Viewport from the BD window rect + registered (dx, dy), VERIFIED on two registered | - | 136 |
| `focus_bd` | vp | Focus + one click on registered empty canvas: clears menu mode and absorbs the swallowed | - | 165 |
| `move_node` | vp, target, uid, cls, dx, dy, tol=6 | (no docstring) | - | 179 |
| `place_from_palette` | vp, target, item, cls, x, y, tol=12 | (no docstring) | - | 203 |
| `node_menu` | vp, target, uid, cls, row, item | Right-click a node's item row, click a REGISTERED menu item, run its registered verifier. | - | 246 |
| `dialog_button` | title, button, open_with=None, bd=None, wait_ms=1500 | Optionally open a dialog with a key combo on the BD, then click a registered button inside | - | 270 |

### tools/motor_gate.py

shared module; imported by 3 file(s): `tools/bench/selftest_motor_fail_exit.py`, `tools/bench/selftest_motor_gate2.py`, `tools/cycle_runner.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `Decision` | (class) | (no docstring) | - | 98 |
| `rig_state` | status_text | 'disassembled' / 'assembled' / 'experiment' / 'unknown'. | - | 109 |
| `read_status` | path=None | (no docstring) | - | 130 |
| `load_limits` | path=None | The user-editable limit file. Returns None if missing/unreadable -> everything is refused. | - | 138 |
| `session_info` | path=None | (no docstring) | - | 156 |
| `decide_asi` | cmd, args, raw | (no docstring) | - | 193 |
| `decide_pi` | cmd, args, raw | (no docstring) | - | 222 |
| `decide_rotor` | cmd, args, raw | (no docstring) | - | 241 |
| `decide` | device, command, state=None | The whole command-class decision, with no I/O to a port. 'state' is injected so the self-test can run every | - | 253 |
| `parse_pi_limits` | text | 'LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0' -> dict, or None.  This is the POST-WRITE readback. | selftest_motor_gate2.py | 282 |
| `parse_pi_ref` | text | 'REFSTATE RON=0 FRF=1 POS=0.00000 POS_BEFORE=0.00000 ERR=0' -> dict, or None. | - | 306 |
| `parse_asi_limits` | text | 'LIMITS SL X=-3.847494 Y=-4.774393 SU X=0.152497 Y=-0.774402' -> dict, or None. | - | 322 |
| `check_pi_readback` | rb, lo, hi, tol=DEFAULT_TOL | (ok, message). rb = parse_pi_limits() output. Every readback field present must match. | - | 332 |
| `check_asi_readback` | rb, sl, su, tol=DEFAULT_TOL | (no docstring) | - | 345 |
| `session_start` | limits, pi_call=None, asi_call=None, session_path=None, out=print | Write the file's limits into BOTH controllers and verify by readback. rc 0 = both verified, else 3. | - | 374 |
| `session_end` | limits, pi_call=None, asi_call=None, session_path=None, out=print | Release the controller limits (PI lo..release_hi, ASI +-release) and delete the session file. | - | 429 |
| `log` | device, command, d, dry | (no docstring) | - | 458 |
| `transmit` | device, command, d, limits | Send ONE decided motion command. The SENDER re-reads the controller limits inside the same port open, | - | 476 |
| `main` | argv=None | (no docstring) | - | 535 |
| `fail_line` | rc | One 'FAIL:' line for a non-zero exit (cycle 69, device-failed repair). pi_testmove_20260923e.log:23/34 held a | - | 616 |
| `result_line` | rc | C6 (docs/session-protocol.md, user-approved 2026-09-24): the gate's verdict as its LAST line. bgrun's body scan | - | 625 |

### tools/outcome_review.py

shared module; imported by 2 file(s): `tools/bench/selftest_item34.py`, `tools/cycle_runner.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `reviews_since_last` |  | (n_retrospectives_since, days_since, last_path_or_None) - the cadence, read from the files. | - | 95 |
| `is_due` |  | (no docstring) | - | 106 |
| `evidence` |  | (no docstring) | - | 117 |
| `last_two_reviews` |  | (latest, previous) archived outcome reviews by mtime, either None. | - | 151 |
| `steer_after_review` | write=True, cards_dir=None | STEERING CARD (user 2026-09-24, "아웃컴 리뷰에 조향카드 부여하는 것 동의"): when the newest review repeats a verdict | - | 157 |
| `main` |  | (no docstring) | - | 176 |

### tools/prior_art_review.py

shared module; imported by 2 file(s): `tools/bench/selftest_chat_p2.py`, `tools/bench/stop_record_selftest.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `inventory` | use_index=False | NO INDEX. This is the measured configuration, not an omission. | - | 82 |
| `record_opt_out` | review_path, reason | Write a '--no-recipe' reason into the archived review file. Returns True if it landed. | - | 168 |
| `jev_advisory` | slug, plan | One 'JEV-PRIORART-DUP' line when an archived prior-art review already answers this step. Never raises, | - | 204 |
| `user_rules_block` | path=None | (no docstring) | - | 239 |
| `build_task` | plan, trigger='new-op', use_index=False, status_path=None, rules_path=None | The full task text a prior-art dispatch sends (split out of main() by card chat-P2 so a self-test can check it | - | 250 |
| `main` |  | (no docstring) | - | 265 |
| `arm_stop_records` | slug, recipes, opt_out='' | Plant a stop record for each '--recipe' if this review's verdicts are not all 'novel'. | - | 359 |

### tools/priorart_diff.py

shared module; imported by 5 file(s): `tools/bench/diag_c147_c3_3_proven.py`, `tools/bench/diag_c148_a2_2_gate.py`, `tools/bench/selftest_c_e3.py`, `tools/hooks/guard_cycle.py`, `tools/prior_art_review.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `pattern_key` | path | (no docstring) | - | 38 |
| `norm_line` | s | (no docstring) | - | 42 |
| `approved` | path, records=None | True when a stop record for 'path' is released or novel for the bytes on disk now. | - | 59 |
| `sibling` | recipe, records=None | (no docstring) | - | 74 |
| `diff_lines` | old, new | (parameter_only_count, [(new line no, old text, new text)] substantive). | - | 90 |
| `scope` | recipe, records=None, new_classes=None | (no docstring) | - | 114 |
| `task_text` | sc | The narrowed review subject for prior_art_review.py --diff-from. | - | 130 |
| `main` | argv=None | (no docstring) | - | 142 |

### tools/protocol.py

shared module; imported by 578 file(s): `tools/audit_cycle.py`, `tools/bench/build_op_const_loopterm_77.py`, `tools/bench/build_op_termtype.py`, `tools/bench/build_opstopmode_v0.py`, `tools/bench/build_opwiringrules_v0.py`, `tools/bench/c109_errorlist_reverdict.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `schema_path` | schema_name | 'task/1' -> docs/protocol/task.json ; a later 'task/2' -> docs/protocol/task.v2.json. | - | 80 |
| `load_schema` | schema_name | (no docstring) | - | 92 |
| `goal_ids` | path=GOALMAP | The ids a card may cite (requirements + milestones), or None when the goal map is absent/unreadable. | - | 173 |
| `machine_view` | doc, schema_name=None | A deep copy of 'doc' without the fields its schema marks "x-prose": true. schema_name: 'stageplan' or | - | 211 |
| `prose_fields` | schema_name | Dotted paths of every x-prose field of a schema (definitions included) - for the self-test and the docs. | - | 225 |
| `validate_obj` | obj, goal_ids=None | (True, 'OK <schema>') or (False, '<one-line reason>'). 'goal_ids': when given, every advances/unblocks/blocks | - | 247 |
| `load_card` | path, goal_ids=None | (no docstring) | - | 272 |
| `result_line` | d | The one-line text form. Validated; ASCII-escaped so a cp949 console can always print it. | - | 285 |
| `make_result` | n_pass, n_fail, first_fail=None, artefacts=(), status=None | (no docstring) | - | 302 |
| `all_result_lines` | text | (no docstring) | - | 314 |
| `parse_result_line` | text | The LAST 'RESULT {...}' line of 'text' as a dict, or None when there is none. A malformed one is a FAIL. | - | 329 |
| `result_failed` | d | A RESULT line fails unless its status is PASS or SKIP AND gates.fail == 0. SKIP (card 108-5, review | - | 335 |
| `stop_kind_of` | exc_or_text | 'memstop' / 'execstop' / 'exception' for an exception object (by class name) or its text. | - | 358 |
| `stop_line` | kind, message, **extra | The one-line STOP text: 'STOP {json}' (ASCII-escaped, like result_line). kind in STOP_KINDS. | - | 369 |
| `all_stop_lines` | text | Every 'STOP {json}' line of 'text' as a dict (file order). A STOP line that is not valid stop-line/1 JSON still | - | 382 |
| `segments` | text | [(start_epoch_or_None, command_line, segment_text)] - one per 'BGRUN START', in file order. | - | 398 |
| `last_segment` | text | (no docstring) | - | 412 |
| `run_verdict` | segment | C6 verdict of ONE run. failed = any RESULT line fails, or the process ended rc!=0, or TIMEOUT. | - | 417 |
| `is_legacy` | start_ts, mtime=None | (no docstring) | - | 438 |
| `log_verdict` | text, legacy_re=None, mtime=None | Verdict of the LAST run in a (possibly appended) log. Pre-switch runs without a RESULT line keep the caller's | - | 443 |
| `first_fail_signature` | segment, legacy_re=None, start_ts=None | For cycle_runner's SAME-MISTAKE trigger: the raw first-failure text of ONE run segment, or None. | - | 463 |
| `stagekit_result_from_gates` | segment | REPLAY ONLY: what stagekit's RESULT line would have been, from its '=== GATES: n pass / m fail' line. | - | 479 |
| `offline_selftest` | path, cmd | True when 'path' (a launched script) is an OFFLINE_SELFTESTS entry and every command-position occurrence of it in | - | 535 |
| `lv_script` | path, cmd, src=None | The check_command / soft-alert notion of a LabVIEW-touching launched script: a recipe, or a script whose code | - | 557 |
| `path_in_globs` | path, globs | (no docstring) | - | 608 |
| `file_lock` | (class) | card chat-P1 item 1(a)/(b): a cross-process lock FILE around a read-modify-write (os.open O_CREAT/O_EXCL, retry | - | 621 |
| `write_release` | review, kind, slug, cite_path, cite_line, what, now=None | card chat-S5 (PD337(d)): write ONE release/1 record + its legacy line into a review file, VALIDATED FIRST. | - | 699 |
| `read_releases` | body | [release/1 dict] from the 'RELEASE {...}' lines of a review body (old reviews: [] - their FIXED:/REFUTED: lines | - | 743 |
| `input_md5_changes` | card | card chat-S5 (PD337(e)): ['<path>: card <md5> != disk <md5>' / '<path>: missing'] for every task/1 input that names | - | 757 |
| `bind` | agent_id, agent_type, card_path, goals='default' | Record the binding. Returns (ok, message). The card must be a VALID task/1. | - | 781 |
| `binding` | agent_id | (no docstring) | - | 814 |
| `code_only` | src | The source with COMMENTS and DOCSTRINGS (any bare string statement) blanked, so the flag detectors see calls, | - | 829 |
| `peer_role_of` | cmd | The review role a command dispatches, or None. peer.ps1: -Role wins, else -Kind (fact/prose), else a | - | 887 |
| `src_features` | src | {'save','gui','run'} for ONE script's source, from its CALLS (judgement 2026-09-24, card chat-B4): a string | - | 922 |
| `requires_path` | card_id, cards_dir=None | (no docstring) | - | 977 |
| `check_requires` | card | {ok, missing, found} for the card's 'requires' (OFFLINE: file system + JSON, never LabVIEW). | - | 1046 |
| `requires_refusal` | card, cmd, scripts | None, or why a bgrun / LabVIEW launch is refused under a card that declares 'requires' (argv + card). | - | 1055 |
| `soft_alert_refusal` | card, cmd, scripts, srcs=None, now=None | None, or the refusal for a NEW bgrun launch of a recipe/diagnostic under a card bound > SOFT_ALERT_MIN ago. | - | 1121 |
| `check_command` | card, cmd | None = allowed, else the refusal reason. The card's flags applied to ONE Bash/PowerShell command. | - | 1139 |
| `check_write` | card, file_path | None = allowed, else the refusal reason, for Edit / Write / NotebookEdit on 'file_path'. | - | 1207 |
| `hook_decision` | payload | The PreToolUse decision for ONE tool call. Returns (allow: bool, message: str/None). | - | 1229 |
| `record_launch` | card_id, cmd | Append one ledger row per '--log' of a bgrun command run under 'card_id'. Returns the rows written. | - | 1281 |
| `card_owns_log` | card_id, log_path | True when the ledger says 'card_id' launched 'log_path' (by basename) - or when the ledger cannot be read | - | 1294 |
| `log_owner` | log_path, text=None, max_age_s=None | card chat-E3 (fp-36): the card that launched 'log_path''s LAST run - the 'card' field of its last RESULT line | - | 1315 |
| `launch_card_env` | log_path | {CARD_ID, CARD_LABVIEW} for a bgrun child, from the ledger row the PreToolUse hook wrote for this --log (the | - | 1354 |
| `review_card` | role, rid, claim, predicted='', observed='', ruled_out=(), attachments=(), note='' | Build + validate a review/1 card; returns the dict. 'attachments' = paths (md5 filled in when the file exists). | - | 1383 |
| `write_review_card` | d | (no docstring) | - | 1401 |
| `render_review` | card | The review/1 card as the text block peer.ps1 puts in front of the task, plus the verdict/1 contract. | - | 1409 |
| `verdict_contract` | card | (no docstring) | - | 1425 |
| `parse_verdict` | text, want_id=None | (dict, None) for the LAST valid 'VERDICT {...}' line of the answer, else (None, reason). | - | 1436 |
| `next_state` | path=NEXT_JSON | (md5_of_bytes / 'absent', card / None, reason / None) - the runner's and next_gate's single reading. | - | 1459 |
| `open_decisions` | path=DECISIONS | (no docstring) | - | 1470 |
| `outcome_slugs` | md_text | The OUTCOME-VIOLATION slugs of an archived outcome review's ANSWER (after '## Answer', before '## What was | - | 1498 |
| `current_cycle` | cards_dir=CARDS_DIR | The highest n of 'cycle_<n>.json' in the cards dir (0 when none). | - | 1509 |
| `steer_for` | latest, previous, cycle, goalmap_path=GOALMAP | (steer/1 card / None, why). A card only when a slug appears in BOTH reviews (a REPEATED verdict). | - | 1522 |
| `write_steer` | card, cards_dir=CARDS_DIR | (no docstring) | - | 1550 |
| `active_steer` | cards_dir=CARDS_DIR, state_path=STEER_STATE | (path, card) of the newest VALID steer card that is not closed (followed / stopped) in the state file, or | - | 1574 |
| `steer_after_cycle` | steer_path, steer_card, next_card, n, state_path=STEER_STATE | Read the judgement's answer (next/1 'steer') to the steer carried in cycle n. Returns (action, detail): | - | 1598 |
| `add_steer_decision` | steer_card, n, refusals, path=DECISIONS | Append ONE open decisions-pending/1 item for a steer refused twice; validate the whole file before writing. | - | 1628 |
| `main` | argv=None | (no docstring) | - | 1788 |

### tools/retro_due.py

shared module; imported by 2 file(s): `tools/bench/selftest_chat_p1.py`, `tools/cycle_runner.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `newest_answered_retro` | peer_dir=None | (path, stamp) / None - guard_cycle.newest_retrospective with its PEER pointed at peer_dir. | - | 47 |
| `cycle_cards` | cards_dir | (no docstring) | - | 59 |
| `delivered` | cycle, cards_dir | [result ids] of PASS result/1 cards written since cycle_<cycle>.json with a claudeDev .vi artefact. | - | 72 |
| `near_threshold` |  | [(slug, fresh occurrences, threshold)] - slugs one occurrence below their threshold (threshold >= 2), counting | - | 100 |
| `check` | cycle, cards_dir=None, peer_dir=None, violations=True | (due: bool, reasons: [str], facts: dict). | - | 120 |
| `main` | argv=None | (no docstring) | - | 153 |

### tools/retrospective.py

shared module; imported by 2 file(s): `tools/bench/selftest_stamp_window.py`, `tools/doc_ingest.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `current_plan_rel` |  | Project-relative path of the ONE cycle plan whose frontmatter says 'status: current', or None. | - | 66 |
| `parse_devices` | path | Every 'DECISION: device' block in docs/violation-decisions.md -> (slug, stamp, one-line device). | - | 168 |
| `retro_archive` | n | The archive of cycle <n>'s OWN retrospective, or None. | - | 216 |
| `newest_retro_before` | now, exclude_slug=None | (path, mtime) of the newest retrospective archived strictly BEFORE 'now', or None. | - | 228 |
| `dispatch_time` | path | When a retrospective was DISPATCHED = its archive's mtime minus the elapsed seconds peer.ps1 recorded. | - | 258 |
| `cycle_window` | cycle, slug=None | (start, end, basis) - the cycle's real boundary. | - | 279 |
| `fmt` | t | (no docstring) | - | 338 |
| `main` |  | (no docstring) | - | 342 |

### tools/run_mode.py

shared module; imported by 1 file(s): `tools/hooks/guard_session.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `config` |  | (no docstring) | - | 27 |
| `effective` | now=None | (no docstring) | - | 35 |
| `write` | weekly_pct | (no docstring) | - | 51 |

### tools/scope_header.py

shared module; imported by 13 file(s): `tools/bench/diag_c146_a1_1_repro.py`, `tools/bench/diag_c148_a1_1_before.py`, `tools/bench/diag_c148_a1_1_runall.py`, `tools/bench/prep_c150_a2_4_stage_prerun_before.py`, `tools/bench/scope_honesty_census.py`, `tools/bench/selftest_c_e3.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `parse_bytes` | b | (header dict / None, error / None). Error = the block exists but is invalid; (None, None) = no block. | - | 101 |
| `read` | path | (no docstring) | - | 129 |
| `canonical_bytes` | b | The bytes without the header block - exactly the file before the migration added it (see module doc). | - | 137 |
| `canonical_sha256` | path | (no docstring) | - | 158 |
| `canonical_md5` | path | (no docstring) | - | 162 |
| `render` | labview, hardware, offline_args=(), evidence=None, nl='\n' | (no docstring) | - | 166 |
| `append_block` | b, block_text | The file bytes with the block appended so that canonical_bytes() gives 'b' back exactly. | - | 176 |
| `honesty` | path, h, src=None | Problems with a DECLARED header against the code (an empty list = honest). Only 'labview: none' (and | - | 264 |
| `compile_error` | path, src=None | None, or the syntax/parse error text. .py: compile() in memory; .ps1: the PowerShell parser (one process). | - | 342 |
| `infer` | path, src=None | The migration's scope for an existing script. labview: none when nothing in its import closure reaches LabVIEW | - | 368 |
| `in_tools` | p | (no docstring) | - | 426 |
| `launches` | cmd | [(script abs path, argv tokens after it)] for every script RUN by 'cmd': a .py in command position of a | - | 449 |
| `effective` | h, argv | (labview, hardware) for ONE run: offline-args present in its argv -> ('none', 'none'). | - | 494 |
| `launch_scope` | cmd, extra=() | [(path, labview, hardware, problem/None)] for every tools/ script 'cmd' runs. problem: missing/invalid header, | - | 501 |
| `check_launch` | flags, cmd, extra=() | None, or the refusal: a run whose declared scope exceeds the card's flags, a header missing/invalid, a compile | - | 543 |
| `offline_run` | cmd | True when 'cmd' runs at least one tools/ script and EVERY tools/ script it runs is effectively labview none | - | 562 |
| `all_scripts` |  | (no docstring) | - | 579 |
| `tracked_scripts` |  | git-tracked tools scripts only: an untracked file belongs to a card still writing it (chat-A1 runs beside | - | 611 |
| `migrate` | apply=False, paths=None | (no docstring) | - | 620 |
| `rescope` | apply=False | fp-40: re-infer every MIGRATION-written header (a tail block with no offline-args/evidence, not KNOWN, not | - | 647 |
| `main` | argv=None | (no docstring) | - | 680 |

### tools/stage_prerun.py

shared module; imported by 174 file(s): `tools/bench/c88_reverdict.py`, `tools/bench/diag_c101b_syntax.py`, `tools/bench/diag_c103d_jevfix.py`, `tools/bench/diag_c103d_launch.py`, `tools/bench/diag_c104_launch.py`, `tools/bench/diag_c104d_launch.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `sha256` | path | (no docstring) | - | 138 |
| `md5` | path | (no docstring) | - | 151 |
| `rel` | p | (no docstring) | - | 158 |
| `GraphShapeError` | (class) | A graph JSON that is not the terminal-list shape OfflineGraph reads. | - | 177 |
| `graph_shape_error` | d | None when 'd' is the terminal-list graph ({md5, terminals:[...], objs:[...]} with the row fields the readers | - | 181 |
| `plan_base_graphs` | recipe | card 106-5 (PD219(c)): [(path, md5 pin or None)] of the base graph every plan the recipe names records | - | 204 |
| `find_graph` | input_md5, plan_graphs=() | The terminal-list graph (graph_shape_error None; card 95-1) whose top-level 'md5' is 'input_md5': | - | 226 |
| `OfflineGraph` | (class) | The readers stagekit addresses with, answered from one graph JSON ({vi, md5, terminals, objs}). Any other | - | 277 |
| `OfflineGraph.G` |  | (no docstring) | - | 303 |
| `OfflineGraph.report_all` | _t, cls | (no docstring) | - | 310 |
| `OfflineGraph.uids` | _t, cls | (no docstring) | - | 317 |
| `OfflineGraph.count` | _t, cls | (no docstring) | - | 320 |
| `OfflineGraph.nodes_in` | di | Nodes whose terminals sit on diagram 'di', plus EVERY structure (a structure's own diagram is not in the | - | 323 |
| `OfflineGraph.node_labels` | _t, di, *a, **k | (no docstring) | - | 331 |
| `OfflineGraph.term_rows` | uid | (rows, how). A structure's terminal list = the OUTER terminals of its border tunnels (jev_candidates | - | 334 |
| `OfflineGraph.node_terms_uid` | _t, di, ni | (no docstring) | - | 345 |
| `OfflineGraph.read_terms` | *_a, **_k | (no docstring) | - | 354 |
| `OfflineGraph.read_live` | _path, fs_pairs=None, fs_uids=None | (no docstring) | - | 357 |
| `DryState` | (class) | (no docstring) | - | 369 |
| `Fake` | (class) | The permissive stand-in for anything the stub cannot know. Every use is counted (taint). | - | 400 |
| `provisional_dry_graph` | recipe | card 132-1 (gate-fp fp-21, PD275(e)): (path / None, error / None). A recipe whose plan base is PROVISIONAL (base = | - | 514 |
| `waiting_reason` | recipe, tr | card chat-E3 (brief item 4): the WAITING text when a dry on a PROVISIONAL base (provisional_dry_graph) failed ONLY | - | 548 |
| `waiting_prerun` | pr | True when every FAILING prerun gate is one that follows from a WAITING dry (X1 dry, X5 executed-ops cascade, X10 | - | 577 |
| `dry_read_only` | recipe | (no docstring) | - | 592 |
| `fake_gscript` |  | A module named 'gscript': gscript.py's TOP-LEVEL constant assignments evaluated one by one (os / str only), | - | 630 |
| `fake_com` |  | (no docstring) | - | 660 |
| `wrap_module` | mod | Every function DEFINED in 'mod' -> a stub (a LabVIEW-touching fleet module loaded through K.mod). | - | 675 |
| `install` | graph_override=None | (no docstring) | - | 693 |
| `patch_stagekit` |  | (no docstring) | - | 748 |
| `dry` | recipe, graph=None | Run in THIS process (the caller is a fresh process: '--dry' / '--prerun'). Returns the trace dict. | - | 965 |
| `plan_files` | recipe | (plan paths, every .json the recipe names). A plan = a named .json with a 'decisions' list of id+action rows, | - | 1039 |
| `stageplan_check` | path | (ok, detail, plan/None, compiled ops/None) for a stageplan/1 a recipe names (card 79-6). ok only when | - | 1081 |
| `control_path_lint` | plan, base=None | List of refusals (empty = the plan passes). 'base' = (cls, terms) for tests; else read from plan['base']. | - | 1168 |
| `pb_licences` | plan_path, bench=None | {node uid: licence file} from every pb-licence/1 file under tools/bench whose 'plan' names plan_path. | - | 1279 |
| `buildarray_open_sibling` | plan, base=None, licences=None | -> [{row, node, wired, open, licensed}] : every 'wire' action whose dst is an INPUT of a Build Array node while | - | 1300 |
| `recreated_wire_refs` | plan, base=None | -> (recreated, flags). recreated = [{wire, row, idx}]: every 'wire' action whose dst is a face of a tunnel an | - | 1360 |
| `replay_sample` | model_path, sample, models | -> (outcome, mismatches, detail): outcome 'PASS' / 'FAIL' / 'ERROR'; mismatches [(field, measured, simulated)]. | - | 1505 |
| `stagesim_tun1` |  | (no docstring) | - | 1625 |
| `replay_delete_sample` | model_path, sample, models, disable=() | -> (outcome, mismatches, detail) for one delete_object / delete_wire / remove_bad_wires sample (card 115-2 R0). | - | 1634 |
| `opmodel_conformance` | ops=None, model_dir=None, disable=(), log=None | X13 core. ops = the stageplan ops to check (None = every model file in model_dir). disable: ('cfw_border_rule',) | - | 1664 |
| `plan_ops` | plan | (no docstring) | - | 1714 |
| `x13_gate` | plans | (ok, detail, warns) over stageplan/1 dicts: the union of their ops, one conformance run. | - | 1718 |
| `addr_offline` | OG, end, is_source | None if addressable offline, else the reason. Unwired terminals: owner node -> terminal list -> uid echo. | - | 1795 |
| `lint` | recipe, OG | (no docstring) | - | 1824 |
| `recipe_dispatches_rows` | recipe | card 110-7 (F1, decided by judgement): True when the recipe's AST CALLS stagekit.run_rows / from_decision (as an | - | 1845 |
| `verb_preconditions` | plans, sps, work, move_dst, stop_after=None, from_step=None, rows_dispatched=True | X9 (retrospective-cycle102 'wrong-ordering'): every op / row the run DISPATCHES whose verb holds a precondition on | - | 1863 |
| `meter_records` | recipe, log_dir=None | X10's evidence: every run log of THIS recipe that carries a recorded per-op meter (stagexec.Meter's METER lines), | - | 1897 |
| `mem_margin` | recipe, stop_after=None, from_step=None, log_dir=None, records=None, margin_mb=None | X10 (retrospective-cycle103 'inference-over-measurement'; PD216(f): 103-2 r1 crossed MEMSTOP 700 at 703.8 MB): the | - | 1933 |
| `X10Probe` | (class) | card 130-1: raised by the Executor capture in probe mode (D.x10_probe) - not an Exception, so stagekit.run's | - | 1969 |
| `load_memory_model` | path=None | (no docstring) | - | 1974 |
| `x10_capture_executors` |  | card 130-1: wrap stagexec.Executor.__init__ for the dry run - record plan path, compiled op kinds, checkpoints, | - | 1982 |
| `executor_stops` | executors | card 130-5 (PD268(b)): one FAIL text per Executor whose run() ended before its window's last op, or that was built | - | 2045 |
| `x10_start` | vi_md5, model=None | card 133-3 (PD283(b)(e)): (start_mb, cite) of a run whose INPUT VI has a measured load: load_by_vi[md5] + op0_read_mb | - | 2061 |
| `x10_plan_start` | plan_path, model=None | card 133-3: the measured start of the Executor run of 'plan_path': its (finalized) base graph's 'md5' = the input | - | 2073 |
| `x10_base_provisional` | plan_path | card 141-1: True when the plan's top-level base is provisional (a simulated graph, no measured VI load). | - | 2087 |
| `x10_model_peak` | kinds, checkpoints, stop_after=None, from_step=None, model=None, start_mb=None, partial=None | card 130-1 (PD267(b)): the predicted private-MB peak of ONE Executor run. N = ops dispatched (from_step+1 .. | - | 2096 |
| `x10_readonly` | recipe, trace | card 132-4 (PD277(a)): (ok, detail). ok True iff the dry trace shows no Executor, no Stage._op, no mutating stub | - | 2136 |
| `x10_source_reads` | recipe, names=X10_SRC_READS | card 138-2 (PD299(b)): the recipe's whole-VI reads counted from its SOURCE. Returns {"reads": n / None (None = some | - | 2206 |
| `x10_reads_line` | src, dry_n=None | card 138-2: one printable line - source count (+ sites), dry count, unbounded sites. | - | 2341 |
| `x10_edit` | recipe, trace, model | card 136-2 (fp-33): (run dict / None, why / None). why None = not an edit trace (no ops: the caller's text stands). | - | 2350 |
| `fntest_release` | path | card chat-F3 (fp-42): (declared, ok, why list). declared False = no FNTEST literal (the caller's rules stand). | - | 2415 |
| `x10_probe_release` | recipe, trace | card chat-M2 (fp-35): (declared, ok, detail). declared False = no X10_PROBE literal (the caller's rules stand). | - | 2485 |
| `x10_gate` | recipe, executors, stop_after=None, from_step=None, model=None, trace=None | card 130-1 (PD267(b)): (ok, detail dict). ok False = a predicted peak > fail_above_mb, or UNMEASURED (no Executor | - | 2548 |
| `x10_probe` | recipe, graph=None | card 130-1 self-test helper: dry-run the recipe only up to its first Executor (probe) and return the records. | - | 2626 |
| `x5_count` | verbs, rows, spc, stop_after=None, from_step=None | X5 (moved out of prerun unchanged, card 115-3 F1): (ok, detail). Wire-making verbs the dry run executed == | - | 2642 |
| `census_check` | plan_path, pred_path=None, samples_path=None | -> None (no prediction file beside the plan) or {'plan', 'pred', 'overall', 'fails': [(cls, derived, declared)], | - | 2690 |
| `census_gate` | plan_paths, pred_override=None, samples_path=None, out=print | (ok, detail, lines). ok False only on a derived != declared class (CENSUS FAIL). Prints one line per plan: | - | 2709 |
| `census_unpredicted` | recipe | card 123-7: the stageplans a recipe names whose census is CENSUS-UNPREDICTED (for --scratch-required). | - | 2738 |
| `x16_in_scope` | a | True for a create action with a declared 'terminals' list that is not a const_donor constant nor a Local. | - | 2769 |
| `termclass_undeclared` | plan | X16 core: [{action, terminal}] for every in-scope create action's declared 'terminals' entry with no term_class. | - | 2775 |
| `x16_gate` | plans | (ok, detail) of X16 over loaded stageplan dicts. | - | 2787 |
| `prim_donor_labels` | path=None | {uid: label} of the original main VI (main_vi_node_labels.json: 'diagrams' lists + 'explicit' / 'implicit' maps). | - | 2817 |
| `prim_donor_check` | plan, labels=None, registry=None, base_uids=None | X17 core: [{action, why}] for every create action with a non-const_donor 'prim' whose donor label is not the prim, is | - | 2832 |
| `x17_gate` | plans, labels=None | (ok, detail) of X17 (card 141-1) over loaded stageplan dicts. | - | 2876 |
| `prerun` | recipe, graph=None, stop_after=None, from_step=None | card 103-2 (PD216(b)): stop_after=k (the recipe's own '--stop-after k', PART-A mode) makes X5 expect only the | - | 2888 |
| `x14_advisory` | recipe, n_rows, log=None | card chat-P1 item 4 (user 2026-09-28; docs/d1-loop12-17-split-plan.md Pre-decided 'rows per step'): rows per | - | 3078 |
| `result_first` | first, warn | card 106-5 (PD219(c)): the RESULT line's first_fail carrying the X10 WARN (result-line/1 has no other free-text | - | 3094 |
| `plan_md5s` | recipe | (no docstring) | - | 3107 |
| `write_record` | kind, recipe, status, first_fail, extra=None | (no docstring) | - | 3114 |
| `launched_stage_scripts` | cmd | argv only: every 'tools/recipes/stage_*.py' a command RUNS - a python token followed (past flags) by that | - | 3125 |
| `vi_modifying_calls` | path | [] or the sorted MODIFY_VERBS names the file calls, when it imports stagekit (ast; never text search). | - | 3161 |
| `is_vi_modifying` | path | card chat-N1 (2): True iff the .py imports stagekit AND calls a name in MODIFY_VERBS. | - | 3187 |
| `launched_vi_modifying` | cmd | argv only: launched .py scripts that are NOT tools/recipes/stage_*.py but is_vi_modifying() -> gated alike. | - | 3192 |
| `launched_py` | cmd | argv only: every script path a python token RUNS (past interpreter flags), directly or after bgrun's '--'. | - | 3198 |
| `launched_plan_runs` | cmd | argv only (card chat-S3): every 'tools/stagexec.py run <plan.json>' a command RUNS -> [(stagexec path, plan | - | 3215 |
| `plan_record` | kind, plan, status, first_fail, extra=None | A dry/prerun record for a stagexec PLAN: script = tools/stagexec.py (its sha256), plan_md5s = {plan: md5}. | - | 3239 |
| `is_stageplan` | path | (no docstring) | - | 3252 |
| `read_records` |  | (no docstring) | - | 3259 |
| `is_prerun_segment` | start_line | True when this bgrun START line runs tools/stage_prerun.py itself (a dry/prerun/check, never a stage run). | - | 3286 |
| `last_failed_run_after` | script, t_min | Newest failing bgrun run of 'script' in a log modified after t_min (protocol.run_verdict). | - | 3292 |
| `unverified_card_names` | cmd | ([label prefixes], why/None) from the task/1 card named by '--unverified-card <path>' in the command. | - | 3343 |
| `stage_key` | script | (no docstring) | - | 3363 |
| `cycle_key` | now=None | 'cycle <n>' from the newest tools/bench/cards/cycle_<n>.json written in the last CYCLE_FRESH_S, else | - | 3367 |
| `read_stage_runs` |  | (no docstring) | - | 3387 |
| `retry_card` | cmd, key, used | (card id, None) when the command carries a valid judgement card for ONE more run of 'key', else (None, why). | - | 3401 |
| `offline_run_of` | cmd, s | card 148-a1-1 (fp-52, fp-58): True when 'cmd' runs script 's' in a mode its OWN scope header declares offline | - | 3420 |
| `check_cap` | cmd, s, runs, ck | (allow, why, card id/None) for ONE stage script against RETRY_CAP in cycle 'ck'. | - | 3436 |
| `pattern_signature` | recipe | sorted list - see the block comment. [] when the recipe cannot be read. | - | 3508 |
| `proven_pattern` | recipe, runs=None, recs=None | (proven: bool, stages: [stage keys whose clean run covers this signature], signature: [..]). | - | 3545 |
| `new_structure_classes` | recipe, runs=None, recs=None, sig=None | card chat-P2 item 1 (user 2026-09-28): the STRUCTURE elements of this recipe's signature ('op:<kind>' and | - | 3566 |
| `provisional_plans` | s, plan=None | [(plan path, sim_of)] for every stageplan this unit would run whose base is provisional. | - | 3615 |
| `plan_named_uids` | plan | Every positive int the plan's actions, open rows or bindings name (stagexec._ints_in over those keys) - the uids a | - | 3645 |
| `address_report` | plan, log=print, advise=True | card chat-S5 (PD337(a)): tier (a) over a stageplan against its base graph's terminal table (finalized.base, else base) | - | 3656 |
| `negative_uids_left` | plan | card chat-S5 (PD337(d)): every negative uid still in a plan's MACHINE fields - the "no negative uid left" check of a | - | 3676 |
| `read_creation_map` | path | (header, {"obj"/"diag"/"term": {sim id: entry}}, steps {k: diff n}) of ONE creation-map/1 file (stagexec | - | 3711 |
| `load_creation_map` | sim_of, graph_doc, explicit=None, cmap_dir=None, log=print | (map / None, why, meta) - the creation map of the run that SAVED stage N's artefact (the real graph). 'explicit' = a | - | 3737 |
| `rebind` | before, prov, real, prov_doc=None, real_doc=None, before_doc=None, info=None, named=None, cmap=None | (M: {negative uid -> real uid} / None, why). See the block comment, step 2. | - | 3776 |
| `carry_fs` | prov_doc, real_doc, before_doc, M, info=None | card 132-6 (PD279(b), docs/d1/ring-p3b.md:95-100): (augmented real doc / None, why). The provisional base (stagesim's | - | 4158 |
| `rebase` | plan_path, graph_path, log=print, simulate=True, out_root=None, model_dir=None, creation_map=None, cmap_dir=None | (ok, detail) - see the block comment. Writes the rebased plan to plan_path only when every check passes. | - | 4257 |
| `record_stage_run` | s, ck, card_id, cmd, by=COUNTED_BY, extra=None | (no docstring) | - | 4486 |
| `record_started` | cmdline, log=None, pid=None | Called by tools/bgrun.py right after its child STARTED (Popen returned). Appends one COUNTED line per stage | - | 4495 |
| `unit_key` | path | Stage key of a script OR a stagexec plan: basename, lower case, '_vN' stripped (stage_key for .py). | - | 4541 |
| `failure_function` | seg | The scripting function a failed run died in, from that run's own segment (see the block comment), or None. | - | 4546 |
| `stage_run_segments` | key, now=None | [(start_ts, failed, function)] of every bgrun run of stage 'key' in LOG_DIR within SCRATCH_WINDOW_S, oldest | - | 4564 |
| `scratch_pass_after` | function, t_after | Newest scratch_verify PASS record for 'function' newer than t_after: its path, or None. | - | 4595 |
| `fn_record_gate` | unit | card chat-F2 (user 2026-10-06): (allow, why) from tools/fn_records.launch_gate - every function the unit uses | - | 4618 |
| `check_scratch` | unit, now=None | (allow, why) - refuse a stage run whose last two runs failed on the same function with no newer scratch PASS. | - | 4638 |
| `function_of_text` | text | The scripting function a first_fail / fact string names: '<module>.<fn>' / 'stagexec.op:<kind>' / 'op:<OpName>'. | - | 4672 |
| `escalation_route` | card, cards_dir=None, now=None | ('scratch-verify', function, evidence) or ('escalate', None, why) for an ESCALATION card ('retry_of_card' set). | - | 4709 |
| `scratch_requirement` | recipe, runs=None, recs=None, now=None | (required: bool, why: str, proven_stages: [..]) - see the block comment. | - | 4761 |
| `scratch_skip_log` | line | (no docstring) | - | 4792 |
| `adopted_record` | script, pm | card chat-S4 A: stagexec.adopted_launch over ADOPT_LOG (None when nothing is adopted or stagexec cannot load). | - | 4804 |
| `check_launch` | cmd | (allow, why). Refuses a stage-recipe launch without a dry PASS and a prerun PASS for its CURRENT sha256 and | - | 4815 |
| `main` | argv=None | (no docstring) | - | 4935 |

### tools/stagekit.py

shared module; imported by 264 file(s): `tools/bench/allterms_s1.py`, `tools/bench/allterms_s2.py`, `tools/bench/allterms_s3.py`, `tools/bench/allterms_s4.py`, `tools/bench/allterms_v1.py`, `tools/bench/build_kswap_88.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `Stop` | (class) | A FATAL gate. The stage stops; 'close()' still runs the hygiene tail. | - | 104 |
| `md5` | path | build_opfsinnertunnelconnect_v0.py:227 verbatim. | - | 186 |
| `version_bytes` | path, n=1 << 16 | '19 00 80 00' = LV2019, '26 00 80 00' = LV2026 (CLAUDE.md rule 1) - diag_s2_scaffold.py:133-140. | - | 195 |
| `private_bytes` |  | LabVIEW's private bytes - the COMPANION of the handle count, which is blind to VI Server refnums | - | 203 |
| `mod` | name | Lazy import of a heavy fleet module, so a no-LabVIEW self-test can import stagekit. | - | 218 |
| `Stage` | (class) | One build/diagnostic stage: pin, copy, edit, gate, save, clean up, report. | - | 229 |
| `Stage.head` | text | (no docstring) | - | 264 |
| `Stage.gate` | label, ok, detail='', fatal=False, kind=None | (no docstring) | - | 267 |
| `Stage.fact` | line | (no docstring) | - | 287 |
| `Stage.row` | label, observed, expected=None | A NON-GATE record. Deliberately NOT at the start of the line, so a row reporting an expected | - | 292 |
| `Stage.census_snapshot` | target=None | {uid: class} of every GObject of 'target' (default the work copy) - ONE report_all run. {} in a dry run. | - | 301 |
| `Stage.census_gate` | label, before, after, declared | Compare the measured NEW-object census (after - before, by class) with 'declared' {class: n} (e.g. the plan's | - | 307 |
| `Stage.safe` | label, fn, default=None | (no docstring) | - | 336 |
| `Stage.left_s` |  | (no docstring) | - | 345 |
| `Stage.dump` |  | (no docstring) | - | 348 |
| `Stage.summary` |  | (no docstring) | - | 357 |
| `Stage.file_facts` | tag, path | (no docstring) | - | 371 |
| `Stage.pin_check` | when | Every md5 pin, reported one per line. Returns True iff all hold. | - | 382 |
| `Stage.restart` |  | Standing restart authority (CLAUDE.md 3). diag_s2_scaffold.fresh:155. | - | 394 |
| `Stage.start` |  | FILES ONLY -> restart -> Preload the ORIGINAL read-only -> the dated WORK copy -> open it. | - | 407 |
| `Stage.es` | tag, target=None | One ExecState reading, appended to the timeline. RECORDED; a criterion only where a gate says | - | 463 |
| `Stage.count` | cls, target=None | (no docstring) | - | 473 |
| `Stage.census` | classes=CENSUS_CLASSES, tag='', target=None | A class census by NAME, never by index - the numbers a stage's counts gate on. | - | 476 |
| `Stage.uid_index` | cls, uid, target=None | The traverse index of 'uid' RE-READ at the call site - never cached across a mutation (34(h)). | - | 488 |
| `Stage.wired_terminals` | uid, hints=(), target=None, tag='' | Every terminal row of node #uid with its wire - 'build_d1_m3a1.node_view':572, which finds the | - | 493 |
| `Stage.net_sources` | wire_uid, n=8, target=None, tag='' | THE OWNER-IDENTITY READING (build_d1_m3a3b_d3.py:589-600). 'OpWireSource_v5' is WIRE-addressed - | - | 503 |
| `Stage.broken_wire_count` | target=None, allow_mutation=False, tag='' | THE DIAGRAM-WIDE BROKEN-WIRE COUNT (build_d1_m3a3b_d3.bad_wire_count:265). ⚠️ IT MUTATES - | - | 528 |
| `Stage.scratch` | suffix, source=None | A dated scratch COPY (unique per run, deleted by 'close()') - the only surface a mutating | - | 545 |
| `Stage.drop_scratch` | path, tag='H4' | Close and DELETE one scratch now (a diagnostic that runs several cells must not hold them all | - | 559 |
| `Stage.discard_work` |  | THIS STAGE SAVES NOTHING: the dated work copy is treated as a scratch, so 'close()' deletes it | - | 577 |
| `Stage.plan_rows` | rows, tag='' | DECLARE this stage's planned re-wiring rows: (source uid/terminal) -> (sink uid/terminal). | - | 587 |
| `Stage.node_mark` | tag='' | The Node census BEFORE a mutation - 'junk_purge()' diffs against the last mark. | - | 652 |
| `Stage.junk_purge` | tag='', hints=() | THE MEASURED PURGE (build_opfsinnertunnelconnect_v0.purge_junk:288): the OpConnect* family mints | - | 659 |
| `Stage.delete_wire` | wire_uid, tag='' | build_opfsinnertunnelconnect_v0.del_wire:336 - by uid, via the LIVE traverse order. | - | 672 |
| `Stage.delete_object` | cls, uid, tag='' | build_opfsinnertunnelconnect_v0.del_node:346 - uid -> live index -> 'g.delete_object'. | - | 685 |
| `Stage.move_in` | uid, dest_diagram_index, position | build_d1_v0.move_in:318 - move an object INTO a nested diagram by uid. | - | 698 |
| `Stage.connect` | sink_diag, sink_node, sink_term, src_diag, src_node, src_term, labels=None | gscript.connect_nested_v2:2965 = 'OpConnectNested_v2' - the nested-diagram writer. | - | 704 |
| `Stage.connect_from_wire` | sink_diag, sink_node, sink_term, wire_uid, wire_term_index, labels=None | 'OpConnectFromWire_v0' - the only writer whose SOURCE need not be a node | - | 711 |
| `Stage.fs_inner_tunnel_connect` | fsit_uid, sink_diag, sink_node, sink_term, auto_route=None, target=None, op=None | 'OpFsInnerTunnelConnect_v1' (build_d1_m3a3b_d3.fsit_call:279, the POISONED caller of Pre-decided | - | 724 |
| `Stage.fs_inner_tunnel_read` | fsit_uid, target=None, tag='' | 'OpFsInnerTunnelTerm_v0' - the FSIT's two faces, read-only (build_d1_m3a3b_d3.fsit_read:342). | - | 751 |
| `Stage.wire_indicators` | node_index, src_terms, indicator_names, diagram_index=0, node_class='SubVI' | gscript.wire_indicators:1786 - branch a node's outputs onto front-panel indicators. | - | 758 |
| `Stage.add_shift_reg` | loop_index, y_position=120, class_name='WhileLoop' | gscript.add_shift_reg:687. | - | 767 |
| `Stage.wire_sr` | variant, loop_index, reg_index, **kw | gscript.wire_sr:737. | - | 773 |
| `Stage.create_local_read` | label, panel_index=None, tag='' | The BUILT local-variable creator. Its measured implementation lives in the diagnostics that | - | 779 |
| `Stage.create_local_write` | label, panel_index=None, dest_diagram_uid=None, position=(40, 40), tag='' | The WRITE twin of create_local_read (card 100-2 V5): 'gscript.create_local_write' = OpCreateLocalRead_v0 | - | 802 |
| `Stage.expect_is_broken_false` | label, reconnect, wire_uid=None | 42(b): THE ORDERED SECOND PASS. The acceptance is asserted on a SEPARATE, idempotent re-connect, | - | 817 |
| `Stage.address` | end, is_source, objs=None | A terminal named by (node uid, terminal name, frame diagram uid) -> the LIVE index triple | - | 844 |
| `Stage.resolve` | v | '$name' / '$name.key' -> self.sym; '$wire_of:<uid>:<term i>' -> that terminal's LIVE wire uid (read now, | - | 893 |
| `Stage.copy_in` | cls, uid, dest_diagram_uid, position, tag='' | COPY a primitive that already exists on the donor into Diagram #dest by 'OpMoveByIndex_v0' (the op of | - | 910 |
| `Stage.add_sr_row` | ex, tag='' | 'add_shift_reg' on the loop named by uid, then the register PAIR read back by index: {right, left, k, | - | 944 |
| `Stage.const_row` | ex, tag='' | 'OpCreateConstOnTerm_v0' ('build_opcreateconstonterm_v0.create_const_on_term':364): a constant TYPED BY | - | 964 |
| `Stage.cfw_second_pass` | src_uid, dst | 42(b)'s ordered idempotent second pass through 'OpConnectFromWire_v0', usable for ANY new wire whose sink | - | 979 |
| `Stage.live_graph` | path, retired_rights=(), extra_rights=None | The step-4 graph of a LIVE file (stage_d1_m3a4.py:104-110's recipe): wiki_build.read_live + the bed's | - | 997 |
| `Stage.rule_check` | d | PRE-DECIDED 143: the op the row names must be the op 'jev_pairs.op_rule' names for its classes, unless | - | 1013 |
| `Stage.from_decision` | record, tag='fd' | PLAN STEP 6 / Pre-decided 142-143: execute a decision record (tools/jev_pairs.write_record shape). | - | 1025 |
| `Stage.save_route` | exec_state, broken_ok | WHICH SAVE ROUTE, as a pure function so it is self-testable without LabVIEW. | - | 1178 |
| `Stage.save` | broken_ok=False, cold_check=True | ONE save of the work copy, by the route 'save_route' picks. Records md5, size and version bytes; | - | 1189 |
| `Stage.close` | expect_files=None | HYGIENE: panels closed, refs opened == closed, scratches deleted, the input's md5 unchanged, | - | 1228 |
| `fixtures_check` | bad_md5s=(), before_listing=None | REVIEW c68-h6 (archive/peer/2026-09-24-c68-h6-fixture-listing.md §1/§4, accepted): after a run that swapped | - | 1282 |
| `match_term_uid` | term_uid, all_rows, node_rows, is_source | Pre-decided 173 (cycle 71): a terminal addressed by its TERMINAL UID after its first resolution, because a | - | 1304 |
| `uid_edges` | G, kinds=('wire', 'fs') | A graph's edges keyed by TERMINAL UID, not by name (review archive/peer/2026-09-24-c68-m4a-p6b-rename.md §4, | - | 1327 |
| `term_key` | r | A terminal row's identity: (term uid, owner uid, term name). | - | 1357 |
| `wire_keys` | rows | {(wire uid, frozenset of its SOURCE rows' term_key)} over the wired rows. A recycled wire uid on a new source is a | - | 1362 |
| `term_identity_gates` | base, sim, real, renames=None, bind=None | TD / unwired / D of a stage's end (base = graph rows before, sim = the simulated end rows, real = the read-back end | - | 1376 |
| `term_identity_names` | base, sim, real | card 141-3 (PD325(b)) as it stood until card chat-T6 - identity (term uid, owner uid, NAME), wires (wire uid, source | - | 1386 |
| `wire_ends_pos` | rows, ob=None, tb=None | {wire uid: (frozenset of source position keys, frozenset of sink position keys)} - a wire as its two ends. | - | 1439 |
| `kept_nodes` | B, gone=() | The BASE nodes that keep at least one base position key (not all in 'gone'). Only these nodes' positions are compared | selftest_t6_poskey | 1449 |
| `term_identity_pos` | base, sim, real, bind=None, renames=None | TD / unwired / D on position keys (block comment above). Returns the keys term_identity_gates always returned - | - | 1464 |
| `licence_renames` | lic | {(term uid, owner uid): (from, to)} from a pb-licence/1 dict's 'renames' list ([{node, term_uids, from?, to?}]); | - | 1510 |
| `pb_rename_rows` | base, sim, real, renames=None, bind=None | (rows, restored, unlicensed) for PB's build4 - card chat-T6 (docs/d1/result-gates.md): every real row on a KEPT BASE node (kept_nodes) | - | 1523 |
| `d4_load` | path | The D4 JSON ({s1: {path, md5}, scope_nodes}) plus 'scope' (set), 's1_md5_got' and 'names' = {node: {name: | - | 1555 |
| `d4_ok` | node, name, d4 | D4's one test: the node is in scope and S1's graph has a terminal of that name on it. | - | 1573 |
| `d4_e1` | diffs, info, d4 | (ok, accepted, bad) over [(checkpoint k, stagexec.compare dict)]; 'info' = {term uid: (owner uid, name)}. | - | 1578 |
| `d4_pb` | got, want, real_end, sim_end, d4 | (ok, closed, grown, bad) at PB. got / want = sets of (node, sink name) of cdiff(S1, real end) / the plan's | - | 1603 |
| `d4_form` | real_end, d4 | FACTS ONLY: {scope node: 'equal to S1' / 'real-only {..} S1-only {..}'} comparing the real end's name counts on | - | 1627 |
| `fixture_listing` |  | (no docstring) | - | 1645 |
| `unload_donor` | path=None | Card 97-5 (judgement c97): after the copy_in calls, drop the donor (default 'g.MOVE_SRC') from LabVIEW's memory | - | 1649 |
| `run` | fn, stage | The standard main(): run 'fn(stage)', never let an exception skip the hygiene tail. | - | 1674 |
| `jload` | *parts | json.load of os.path.join(*parts) (utf-8) - the recipes' 'J' helper. Returns the parsed object. | - | 1705 |
| `pure` | name | A NO-LabVIEW module (stagexec, stagesim, vigraph, jev_candidates, elrule) imported DIRECTLY, as the recipes import it - not | - | 1711 |
| `pos_slot_table` | G | {term key: (node, index in the node's READ order, term class, is_source)} of a vigraph graph - the same key as | selftest_c153_poskey_convert.py | 1724 |
| `pos_name_free` | P, s | One effective source ('<key>' or '<key>@<tunnel>/f<n>+...') -> (its position in table P, frame tag); an unknown key | selftest_c153_poskey_convert.py | 1737 |
| `pos_slots` | G, nodes, V=None | {sink key: ((node, index, class), frozenset of name-free effective sources)} for the input terminals of 'nodes' in | selftest_c153_poskey_convert.py | 1748 |
| `pos_convert` | rows, SA, SB | Name-keyed cdiff sink strings -> POSITION rows [{sink, slot, name_a, name_b, before, after[, passthrough]}], sorted by | selftest_c153_poskey_convert.py | 1759 |
| `pos_convert_open_rows` | plan_open_rows, old_rows, new_rows | A plan's open_rows [{node, term}] with every row dropped whose (node, name) pair the old -> new row conversion removed | selftest_c153_poskey_convert.py | 1782 |
| `s1_frame_graph` | labels=None | S1's FRAME-KEYED vigraph graph (the wiki S1 terminals + the newest graph_objs_s1 / graph_loops_s1 reads), as every ring | selftest_t7_ring.py | 1790 |
| `pred_end_graph` | L, labels, fs_pairs | The FRAME-KEYED vigraph graph of a plan's simulated end state L (its terminals, objs, loops) - the graph a pred's cdiff rows | selftest_t7_ring.py | 1799 |
| `pb_check` | S1f, G1, Gpred, pred_rows, open_rows, unlicensed=(), V=None | PB by POSITION (card chat-T7, fp-70): cdiff(S1f, G1 = the REAL end) (vigraph.computation_diff_frame) against the pred's cdiff | selftest_t7_ring | 1806 |
| `sink_gate_spec` | e, actions, base, sim_end | One sink-gate census row (prep_*_session.json 'sink_gate_census', needs_sink_gate) -> its declared sink gate spec | selftest_t7_ring.py | 1836 |
| `sink_gate_read` | e, d, x, rows, n_actions | (ok, detail) for the deferred op error on sink d['sink'] (stage_d1_ring_p5s01a.py:90-117 sg_read, unchanged): (a) the indicator | selftest_t7_ring.py | 1861 |
| `sink_gate_backend_class` |  | stagexec.LVBackend subclass that KEEPS its last whole-VI read in 'last_terms' (no extra read; LVBackend.read is called exactly | - | 1893 |
| `RingSession` | (class) | The inputs of one ring stage session and the gates its body runs - stage_d1_ring_p5s01a.py:31-191 as calls. A recipe builds | selftest_t7_ring.py | 1908 |
| `RingSession.stem` |  | The plan file's name without .json (gate labels name it). Returns a str. | - | 1939 |
| `RingSession.sink_read` | e, d | (ok, detail) of sink_gate_read on this session's executor and last read; (True, 'dry') in a dry run. | - | 1943 |
| `RingSession.census_snapshot` | s | {uid: class} of s.census_snapshot() kept to the pred's census classes (the recipes' 'snap'). ONE whole-VI read. | - | 1949 |
| `RingSession.handles` |  | LabVIEW's handle count now (bench_prep.labview_handles); None in a dry run is the caller's business. | - | 1953 |
| `RingSession.gate_l0` | s | L0 (FATAL): plan final + open_rows_match + plan_in == <plan>_in; base graph md5 == pred == file; bed md5 == pred; plan end | - | 1957 |
| `RingSession.executor` | s | SG (FATAL: one declared sink gate per census row) -> the backend (stagexec.DryPlanBE in a dry run, else the SGBackend | - | 1968 |
| `RingSession.run` | s | Run the executor: E1 (every checkpoint's real graph == its simulated step). On stagexec.ExecStop: save ops 1..k-1 for a | - | 1989 |
| `RingSession.gates_ng_fr_d` | s, real | NG (crossing ops' new tunnel names == the simulator's), FR (FATAL: created objects on the sim end's frames; real frames == | - | 2006 |
| `RingSession.gate_cen2` | s, c0, c1 | CEN2: the new-object census between snapshots c0 and c1 == the pred's census. Returns s.census_gate's delta. | - | 2028 |
| `RingSession.gate_td` | s, real | TD: every base terminal the sim keeps wired is still wired; identities lost == the plan's deletes (position key). Records | - | 2032 |
| `RingSession.gate_pb` | s, real | PB (FATAL, before save): pb_check(S1, real end) - by POSITION (fp-70). The real end's rows get the sim end's names on kept | - | 2043 |
| `RingSession.finish` | s, h0, rk, dc, key, level, save=True | PH / HB (handles open -> save <= +700, PD236(b)), the rule-6 GUI save (broken by design), PS (saved, md5 differs, input | - | 2058 |
| `pred_x10` | pred_path, plan_path | The X10 prediction of a plan: its pred file's memory_pred.peak_mb, ONLY when pred.plan.md5 == md5(plan) (the scratch | selftest_t7_ring.py | 2078 |
| `census_all_install` | stage_cls=None | Wrap Stage.census_snapshot / census_gate (once) so every snapshot is kept and every census gate also prints the CENSUS-ALL | selftest_t7_ring.py | 2094 |
| `el_norm_ocr` | s | An Error List text -> lower-case alphanumerics with the OCR aliases applied (== errorlist_check.norm). Returns a str. | - | 2131 |
| `el_class` | it | One Error List item {raw, detail} -> its class: elrule.item_class's local / cond / sr, else input, else | selftest_t7_ring.py | 2140 |
| `el_advisory` | items, pred_path, plan_path, pred=None | (rc, report) for one Error List read (its items) against the pred's errorlist.per_class (PD354(a), ADVISORY): rc 1 only for | selftest_t7_ring.py | 2152 |
| `el_advisory_print` | rc, rep | Print the one EL-ADVISORY line of an el_advisory result. | - | 2175 |
| `el_advisory_selftest` | pred_path, plan_path | Four synthetic Error List reads built from the pred's predicted per-class counts (offline, the scratch recipes' | - | 2182 |
| `scratch_offline_modes` | argv, pred_path, plan_path | The scratch recipes' two OFFLINE modes, before any K.Stage: '--el-advisory-selftest' -> el_advisory_selftest's rc; | - | 2210 |
| `scratch_tail` | st, rc, gone, key, tag, log, base_vi, base_md5, pred_path, plan_path, card, sum_json, fail_mb, launch_mb=680.0 | After K.run of a scratch: peak private MB from the log's METER lines vs the pinned X10 (pred_x10), and the gates MEM (peak <= | - | 2222 |

### tools/stagesim.py

shared module; imported by 166 file(s): `tools/bench/dedupe_check_s2b.py`, `tools/bench/diag_c100_6_parity.py`, `tools/bench/diag_c100_6_resim.py`, `tools/bench/diag_c100_6_resim2.py`, `tools/bench/diag_c100_disp_sim.py`, `tools/bench/diag_c100_plan.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `SimError` | (class) | An action that cannot be applied: an unaddressable/ambiguous terminal, an occupied sink, a cross-diagram | - | 210 |
| `md5_file` | path | (no docstring) | - | 215 |
| `load_models` | model_dir=OPMODEL_DIR | (no docstring) | - | 240 |
| `model_for` | op, models | (params, source string, evidence, gaps) for one op. | - | 254 |
| `cfw_border_rule` | data | card 114-3 C1/C2 (review archive/peer/2026-09-28-c114b-l2b3d.md s1): 'recreate' when the MEASURED connect_from_wire | - | 276 |
| `plan_tunnel_face` | st, row | True when 'row' is a face of a tunnel an earlier 'tunnel' action of THIS plan made (a symbolic LoopTunnel/Tunnel, | - | 298 |
| `base_state` | graph, context=None | (no docstring) | - | 307 |
| `fs_measured_state` | graph | card 134-1 (PD287(b)): the Flat Sequence map of a REAL graph from what its reader MEASURED - graph['fs_measured'] = | - | 374 |
| `fs_border_gate` | graph, uses | card 134-2 (PD288(b)): gate B SCOPED, never relaxed. Every FlatSequenceOuterTunnel of a measured graph that | - | 496 |
| `completeness_gate` | g, uses=None, st=None | card 135-2 (docs/violation-decisions.md 2026-10-02 12:2x, device (1); selftest_c134_4_owners O1-O3 made a gate): a | selftest_c134_4_owners | 516 |
| `WriteGuard` | (class) | card 135-2 (docs/violation-decisions.md 2026-10-02 12:2x, device (2); PD279(c) extended to finalize and to the step | - | 564 |
| `WriteGuard.unchanged` |  | (no docstring) | - | 584 |
| `WriteGuard.restore` |  | (no docstring) | - | 587 |
| `new_uid` | st | (no docstring) | - | 608 |
| `node_rows` | st, uid | (no docstring) | - | 613 |
| `wire_rows` | st, w | (no docstring) | - | 617 |
| `has_source` | st, w | (no docstring) | - | 621 |
| `obj_class` | st, uid | (no docstring) | - | 625 |
| `resolve_uid` | st, ref | (no docstring) | - | 635 |
| `resolve_diag` | st, ref | A diagram field (dest_diagram / diagram / body / parent) -> a diagram uid. An int is a base diagram; the string | - | 648 |
| `parse_addr` | a | (no docstring) | - | 669 |
| `case_frame_of` | st, frame_diag | card 124-2 (PD249(d)): (case uid, frame index, frame name) of 'frame_diag' when it is a frame of a case THIS plan | - | 681 |
| `fs_of` | st, frame_diag | card 126-3: (FS uid, frame index left to right) when 'frame_diag' is a frame of a Flat Sequence THIS plan created | - | 695 |
| `resolve_addr` | st, a, want_source | The ONE terminal row an address names. Selector order: term_uid, then name; 'inner'/'outer' (or 'side') | - | 744 |
| `graph` | st, labels=None, fs_pairs=None | fs_pairs (card 106-3): an override for the state's own 'fs_pairs' (None = the state's) - the finalize cdiff graph | - | 829 |
| `effective_consumers` | G, key | The COMPUTATION sink terminals 'key''s value reaches through scheduling relays only (forward twin of | - | 841 |
| `s1_partner` | S1, G, key | (no docstring) | - | 858 |
| `seed_base_flips` | st, cascade=False | card 112-1 T3 (PD225(h)3 (iii), brief_110-3 (e)): flips made in an EARLIER session. A base-graph tunnel of a | - | 953 |
| `seed_base_flips_modelled` | st, models | seed_base_flips under the switch that arms the same-session un-flip (the move_in model's 'unflip_on_source', | - | 979 |
| `only_sink_fate` | P, src_class | The only-sink sub-rule (card chat-S3; tools/bench/opmodels_onlysink.log): what happens to a wire whose ONLY | - | 998 |
| `only_source_fate` | P, src_class | card 101-4, the MIRROR of only_sink_fate: a CUT wire whose ONLY source sat on the MOVED node and whose one other | - | 1006 |
| `closure_of` | st, uid | (nodes, diagrams): everything a move of 'uid' carries - 'uid' itself plus every node with a terminal on a diagram | - | 1054 |
| `op_move_in` | st, a, P, S1, labels | MOVE (card 80-6 refit to the L2-A1 reads, fixture tools/bench/sim/l2a1_real_80.json): | - | 1068 |
| `termclass_table` | path=None | The measured table (termclass_table/1) or None when absent/unreadable (then measured_term_class keeps the declared class). | - | 1239 |
| `measured_term_class` | owner_class, decl, t, table=None | (term_class, note/None) for declared terminal 't' of a created 'owner_class' node whose declared terminal list is 'decl': | - | 1250 |
| `op_add_shift_reg` | st, a, P, S1, labels | (no docstring) | - | 1289 |
| `op_tunnel` | st, a, P, S1, labels | (no docstring) | - | 1352 |
| `op_delete_wire` | st, a, P, S1, labels | (no docstring) | - | 1383 |
| `op_delete_object` | st, a, P, S1, labels | (no docstring) | - | 1416 |
| `cond_row` | st, loop | card 101-3: the conditional-terminal row of a While loop a 'create' made = the body Diagram's one unnamed | - | 1445 |
| `cond_target` | st, ref | 'new:<alias>.cond' naming a WhileLoop an earlier 'create' made -> that loop's uid, else None. The conditional | - | 1456 |
| `op_wire` | st, a, P, S1, labels | (no docstring) | - | 1478 |
| `op_remove_bad_wires` | st, a, P, S1, labels | (no docstring) | - | 1576 |
| `naming_table_lt_pairs` | path | card 153-b1-1: the measured LoopTunnel source shapes recorded in a naming table -> [(loop_class, inner_src_class)]. | - | 1910 |
| `cross_face_names` | st, s, a, tunnels | card 131-1: the names LabVIEW gives the faces of the tunnels ONE crossing creates. 'tunnels' = [(cls, fin, fout, | - | 1936 |
| `naming_table_check` | path=None | card 131-1: every row of the crossing table vs cross_face_names -> {rows: [(label, bad, cite)], skipped: [label], | - | 1950 |
| `op_wire_remove_loose_ends` | st, a, P, S1, labels | card 127-2 (PD255(b)/256(b)): gscript.wire_remove_loose_ends on a pre-existing wire ('wire_uid') or on every wire the | - | 2198 |
| `op_create` | st, a, P, S1, labels | card 100-3: 'diagram' may be 'new:<alias>.body'. By class: | - | 2227 |
| `op_gate` | st, a, P, S1, labels | card 100-3: a VALUE gate on a base constant (the real run reads it and stops when it equals 'stop_if'). The graph | - | 2352 |
| `op_decide` | st, a, P, S1, labels | (no docstring) | - | 2363 |
| `uid_edges` | G, kinds=('wire', 'fs') | stagekit.uid_edges, copied (importing stagekit pulls the LabVIEW fleet in). | - | 2377 |
| `canon` | edges, base_nodes, cls_of | Edges with every NEW object named by its class only ('NEW:<class>', terminal '*') - comparison up to | - | 2387 |
| `canon_diff` | ca, cb | (no docstring) | - | 2398 |
| `cdiff_keys` | cd | (no docstring) | - | 2404 |
| `load_s1` | plan | (no docstring) | - | 2409 |
| `cdiff_inputs` | plan, st, labels=None | card 106-3 (PD217(d), facts_c104c_e3.json): the node labels + fs tunnel pairs the FINALIZE cdiff graph is built | - | 2419 |
| `open_row_class` | r | PD217(c): a plan open row's PD213(d) class - a 'class' field, else the class the finalizer wrote into 'why' | - | 2443 |
| `c4_check` | S1, G, c4 | PD217(c): for every class-(4) (node, term) row, the end graph's effective sources == S1's, on every sink key of | - | 2457 |
| `open_rows_classed` | plan, S1, G, end_pairs | card 106-3: the finalize open-row rule under PD217(c)'s classes (the E3 rule applied at plan time): every declared | - | 2474 |
| `route_report` | plan_out_path, model_dir=OPMODEL_DIR, log=print, require_final=True | card 112-1 T4: stagexec.dry_run on a just-finalized plan -> {status, first_fail, rows: [{k, op, ids, route, how, | - | 2487 |
| `fs_routes_of` | steps | card 133-1: {str(action n): {"how", "variant", "id"}} for every simulated 'wire' step whose effect is a Flat Sequence | - | 2516 |
| `simulate` | plan_path, graph_path, out_root=SIM_ROOT, plan_out_dir=BENCH, model_dir=OPMODEL_DIR, labels=None, log=print, route_ch... | card 153-b1-1 (PD370(c)): 'collect_all' (default False = the unchanged replay) - an UNMEASURED refusal takes the plan's own | - | 2542 |
| `selftest` |  | (no docstring) | - | 2837 |
| `main` | argv | (no docstring) | - | 3494 |

### tools/stagexec.py

shared module; imported by 311 file(s): `tools/bench/constsrc_l2a1_82.py`, `tools/bench/constsrc_l2a1_85.py`, `tools/bench/ctsrc_l2a1_82.py`, `tools/bench/diag_c100_6_parity.py`, `tools/bench/diag_c100_rows.py`, `tools/bench/diag_c101_resim.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `ExecStop` | (class) | The executor stops here (a difference, an unbound object, an unaddressable terminal). | - | 62 |
| `Meter` | (class) | Private bytes (MB) + handle count, stamped per op and per read. 'probe()' -> (private_bytes_int_or_None, | - | 95 |
| `Meter.summary` |  | (no docstring) | - | 122 |
| `meter_rows_from_log` | path | card 106-3: the recorded per-op meter of one run, read back from its log's 'METER <tag> k <k> private <mb> MB' lines | - | 137 |
| `mem_predict` | rows, stop_after=None, from_step=None, start_mb=None, memstop=MEM_STOP_MB, margin_mb=0.0 | card 106-3 (retrospective-cycle103 'inference-over-measurement', PD216(f)): the private-MB peak a run over ops | - | 149 |
| `md5` | p | (no docstring) | - | 172 |
| `load_final_plan` | plan_path, require_final=True | The plan, its step states (md5-checked against 'finalized.step_files') and the actions' step numbers. | - | 186 |
| `base_cond` | ref | card 139-5 (PD316): {'uid': <BASE loop uid>, 'term': 'cond'} -> that uid (int), else None. The conditional terminal | - | 212 |
| `verbs_missing` | route | The verbs a route calls that are NOT defined in the source (a text check - the dry run imports no LabVIEW side, | - | 338 |
| `precondition_failures` | plan, ctx, stop_after=None, from_step=None | card 106-3: [{k, route, acts, ids, needs, work}] - every op the run DISPATCHES (from_step < k <= stop_after) whose | - | 371 |
| `create_route` | a | The CREATE_ROUTES key for a create action, else ExecStop (no executor for that shape). | - | 389 |
| `purge_entry` | purge, uid | The junk purge's read-back entry {uid, class, label, ...} of the created node #uid, else None. | - | 461 |
| `prim_check` | a, entry, uid=None | card 141-1: (ok, detail) for ONE created primitive: read-back label == a['prim'] and class == a['class']. | - | 472 |
| `const_born_on` | real, term, diagram | card 122-3 (PD241(a)): the row of terminal 'term' when it is the OUTPUT terminal of a diagram CONSTANT (is_const) on | - | 497 |
| `tunnel_outer_face` | real, term, diagram | card 100-6 (PD213(f)3) + card 108-6 (PD222(g)): the row of terminal 'term' when it is the OUTER SOURCE face of a | - | 511 |
| `check_symbols` | A | card 100-3: every symbolic reference names an alias an EARLIER action created; '.body' only of a loop create, | - | 532 |
| `case_frame_op` | A, i, fr | card 124-2 (PD249(d)): {frame, frame_index, case} of wire action i whose end(s) carry 'frame' - read from the PLAN: | - | 593 |
| `fs_wire_ops` | A | card 126-3 (PD253(e)): {wire action index: op fields} for the wires a FLAT SEQUENCE route takes, read from the PLAN | - | 656 |
| `compile_plan` | plan | [{kind, acts:[action indices 1-based], ...}] - one entry per REAL op, in order. Raises ExecStop on a shape the | - | 729 |
| `dedupe` | terms | (no docstring) | - | 841 |
| `edges` | terms | (no docstring) | - | 845 |
| `translate` | state_terms, bind | Sim rows with created (negative) uids replaced by their bound real uids. Unbound negatives stay negative. | - | 861 |
| `compare` | sim_terms, real_terms, bind, allow_either=() | {n, only_sim_terms, only_real_terms, only_sim_edges, only_real_edges, dangling_sim_only, dangling_real_only}. | - | 872 |
| `step_soft` | d | card chat-S3 (PD328(c)): True when this step diff is LOG-only by gateclass (tunnel face rows only). | - | 899 |
| `classify_step_diff` | plan, last_act, d | PD214(c) (user-side plan decision, cycle 101): a step difference made ONLY of sourceless (dangling) terminals - | - | 921 |
| `uid_reuse` | prev_real, real | Evidence that LabVIEW re-issued a freed uid to a NEW object within one op (hyp-optunouter-uidreuse-85.md:78-82; NI: | - | 942 |
| `bind_new` | prev_real, real, sim_prev, sim_now, bind | Bind the objects the simulation created between sim_prev and sim_now to the real objects that appeared between | - | 965 |
| `tunnel_name_check` | sim_prev, sim_now, real_prev, real_now | card 132-1 (PD275(c)): the per-op TUNNEL-NAME gate. The NEW rows owned by a *Tunnel object (term_uid absent from the | - | 1068 |
| `is_crossing_op` | step_effects | card 132-1 (PD275(c)): an op is a CROSSING op when one of its plan actions' simulated steps lists created border tunnels | - | 1086 |
| `bind_by_frames` | cls, su, ru, new_sim, new_real, dg, bind | Bind several created 'cls' objects of ONE op by their faces' frames. Object key = the sorted (term_class, is_source, | - | 1097 |
| `bind_fs_tunnel` | prev_real, real, sim_prev, sim_now, bind | card 126-3: bind the FlatSequenceInnerTunnel a cross-frame wire made (stagesim._fs_frame_wire). Its FOUR rows are filed | - | 1124 |
| `bind_case_faces` | prev_real, real, sim_prev, sim_now, bind | card 120-3 R2: bind a created case SELECTOR ('Tunnel') or case DATA tunnel (SelectorTunnel) - one outer face plus ONE | - | 1161 |
| `is_ct` | r | (no docstring) | - | 1237 |
| `listed_as_node` | r | Constant / Tunnel / Terminal are OUTSIDE the Node branch of the VI Server hierarchy (gobject/constant/.., | - | 1248 |
| `is_const` | r | PD188(c) (card 85-1): a diagram CONSTANT end - outside Diagram.Nodes[] (listed_as_node), addressed by its class | - | 1263 |
| `loop_parent` | st, L | The diagram uid a loop sits on: its own non-body rows, else its registers' / tunnels' OUTER faces (one value). | - | 1270 |
| `touched_diagrams` | plan, st | Base diagram uids the plan touches: moved nodes' source diagrams, move destinations, register/tunnel parent + body, | - | 1298 |
| `listing` | rd, diag, cls | {(class, uid)} of reader rd's Nodes[] on diagram uid 'diag' (None when the reader has no such diagram). | - | 1323 |
| `reader_parity` | real_rd, sim_rd, diags, cls_real, cls_sim | [{diagram, n_real, n_sim, only_real, only_sim}] per diagram; 'n' = total one-side-only entries. | - | 1331 |
| `classes_of` | st_or_rows, objs | uid -> class, from the objects list, else from the terminal rows (node_of / node_class). | - | 1345 |
| `connect_route` | addr, real, src, dst, loop_of | The connect route BOTH backends take (so the dry run sees what the real run does): 'indicator' (panel sink, wired | - | 1358 |
| `base_registers` | st | card 112-1 T1: {register uid: {"loop": loop uid, "right": its RightShiftRegister uid, "cls": class}} for every | - | 1479 |
| `base_sr_route` | real, src, dst, base_regs | card 112-1 T1: (variant, register uid, body-side terminal) when a plain 'wire' row touches the INNER face of a | - | 1494 |
| `face_twins` | rows, r, owners | PD191(b): the owner-routed OUTER faces on the same owner structure as row r with r's (name, direction) - r included. | - | 1508 |
| `tunnel_owner` | rows, tun, owners | The structure uid owning tunnel 'tun' (via its inner frame diagrams in 'owners'), else ExecStop. | - | 1523 |
| `Addr` | (class) | Terminal -> live index triple (Diagram idx, Nodes[] idx, Terminals[] idx). 'rd' = reader with diagrams(), | - | 1533 |
| `Addr.snap_loop` | loop, diag | (no docstring) | - | 1562 |
| `Addr.track_new` | loop, r_outer, l_outer | (no docstring) | - | 1566 |
| `Addr.retrack` |  | (no docstring) | - | 1584 |
| `Addr.triple` | real, term_uid, is_source, loop_of=None | (no docstring) | - | 1613 |
| `Addr.ct` | real, term_uid | PD187(b) / 179(b): a ControlTerminal end -> {ct, diag, didx, name, is_source, wire}. term_uid == its own uid, | - | 1625 |
| `Addr.const` | real, term_uid | PD188(c): a bare diagram-CONSTANT source -> {const, cls, term}. Its terminal row must be the constant's own | - | 1650 |
| `Addr.tun` | real, term_uid | PD191(b): a structure tunnel's OUTER face -> {tun, cls, term}, addressed by the TUNNEL uid (Tunnel.Outside | - | 1666 |
| `load_binding` | src, plan_path, from_step | card 103-4 (PD215(b) Part B): the Part-A binding -> {bind, loop_of, sym_real} with INT keys. 'src' = the dict | - | 1782 |
| `bind_state` | st, bind | card 103-4: a simulated step state with every created (negative) uid replaced by its Part-A real uid - owner, | - | 1805 |
| `bound_owners` | owners, bind | card 104-2: a SIMULATED step's owners map (str(frame diagram uid) -> [structure class, structure uid]) with every | - | 1878 |
| `Executor` | (class) | PD193(a), card 86-4: 'checkpoints' = the real-op numbers k after which the whole-VI read + step diff run. None = | - | 1893 |
| `Executor.step` | n | (no docstring) | - | 1946 |
| `Executor.face_soft` | k, kind, d | card chat-S3 (PD328(c)): an E1 step diff of tunnel face rows only. One '  SOFT  ' line per step and one | - | 2053 |
| `Executor.part_a_record` |  | card 103-1 PART-A (PD215(b)), after run() with stop_after=k: (a1, a2, detail, binding). | - | 2070 |
| `Executor.resume_record` | stop_msg='' | card chat-S4 R: after an ExecStop IN op k (self.cur), the resume/1 record for from_step k-1 - the binding exactly as | - | 2089 |
| `Executor.sim_uid` | st, ref | (no docstring) | - | 2147 |
| `Executor.diag_real` | st, ref | card 100-3: a diagram field -> the REAL diagram uid (an int as is; 'new:X.body' through the binding the create | - | 2152 |
| `Executor.obj_real` | st, ref | (no docstring) | - | 2166 |
| `Executor.real_term` | st_prev, st_after, addr_ref, want_source | The plan end -> the REAL terminal uid: resolved on the simulated state (the plan's own resolver), then | - | 2173 |
| `Executor.run` |  | (no docstring) | - | 2185 |
| `Executor.execute` | op, prev, after, real | (no docstring) | - | 2497 |
| `LVReader` | (class) | (no docstring) | - | 2701 |
| `LVReader.diagrams` |  | (no docstring) | - | 2705 |
| `LVReader.node_uids` | didx | (no docstring) | - | 2708 |
| `LVReader.node_terms` | didx, nidx | (no docstring) | - | 2711 |
| `LVReader.node_term_uids` | didx, nidx | card 112-2 D2: one TERMINAL uid per Terminals[] entry of Nodes[nidx] (gscript.node_terms_uids, OpNodeTermsUid_v0), | - | 2714 |
| `LVReader.ct_uids` |  | (no docstring) | - | 2727 |
| `LVReader.obj_uids` | cls | (no docstring) | - | 2730 |
| `check_sink_gates` | sink_gates, gates | SINK GATES (card 80-3, retrospective-cycle79 device-failed at the old whitelist here): a recipe may let a | - | 2734 |
| `sink_gate_for` | tag, err, sink, decls | The declaration whose sink == 'sink' exactly, else ExecStop (the op error stops the run). | - | 2751 |
| `LVBackend` | (class) | Every mutator is a stagekit / gscript verb the L7 stages used; each is followed by the measured junk purge. | - | 2761 |
| `LVBackend.run_deferred` |  | Executor.run's last act: every deferred op error's declared gate READS its sink now; a gate that fails stops. | - | 2782 |
| `LVBackend.read` |  | (no docstring) | - | 2791 |
| `LVBackend.obj_classes` | real | (no docstring) | - | 2797 |
| `LVBackend.set_description` | uid, text | (no docstring) | - | 2803 |
| `LVBackend.get_description` | uid | (no docstring) | - | 2812 |
| `LVBackend.move_in` | uid, dest, pos, op | (no docstring) | - | 2824 |
| `LVBackend.add_sr` | loop, y, op | (no docstring) | - | 2828 |
| `LVBackend.wire_sr` | variant, loop, right, term, real, op | (no docstring) | - | 2843 |
| `LVBackend.connect` | src, dst, real, loop_of, op | (no docstring) | - | 2863 |
| `LVBackend.indicator` | rs, rd | (no docstring) | - | 2975 |
| `LVBackend.create` | route, a, args, real, op | One 'create' row -> its verb (CREATE_ROUTES). Returns {err, s, uid[, body], how}. Every verb is followed by the | - | 2996 |
| `LVBackend.stop` | loop, src, real, op | OpStopFromNode_v0 (tools/recipes/build_opcreateconstonterm_v0.py:528-537): the While loop's conditional terminal | - | 3212 |
| `LVBackend.value_gate` | uid, a, op | read_bool_const (OpConstValueB_v0, card 100-2 V4): the stage STOPS when the value equals 'stop_if'. | - | 3235 |
| `LVBackend.recheck_gate` | uid, a, op | card 103-4 PART-B ENTRY: the value gate Part A passed, READ again on the loaded file (same read, no edit). | - | 3246 |
| `LVBackend.branch` | tun, dst, real, loop_of, op, side='outer' | (no docstring) | - | 3250 |
| `LVBackend.case_frame_wire` | case, k, src, dst, real, op | card 124-2 (PD249(d)): gscript.case_frame_wire (card 124-1's verb, the contract in brief_124-2.md) wires src -> dst | - | 3263 |
| `LVBackend.connect_term_uid` | src, dst, real, op | card 124-6 (PD250(c)): gscript.connect_term_uid(work, sink=dst, src=src) for an R1/R2 tunnel group. A missing verb, | - | 3289 |
| `LVBackend.rle` | wires, op | card 127-2: gscript.wire_remove_loose_ends on each live wire; a uid echo error or a wire still Is Broken? True after | - | 3313 |
| `LVBackend.index_mode_fix` | tun, indexing | (no docstring) | - | 3330 |
| `LVBackend.delete_wire` | w, op, plan_wire=None | (no docstring) | - | 3341 |
| `LVBackend.delete_object` | cls, uid, op | (no docstring) | - | 3345 |
| `LVBackend.rbw` | op | (no docstring) | - | 3349 |
| `SimReader` | (class) | (no docstring) | - | 3355 |
| `SimReader.diagrams` |  | (no docstring) | - | 3359 |
| `SimReader.node_uids` | didx | (no docstring) | - | 3377 |
| `SimReader.node_terms` | didx, nidx | (no docstring) | - | 3394 |
| `SimReader.node_term_uids` | didx, nidx | card 112-2 D2: the offline analogue of OpNodeTermsUid_v0 - each listed entry's own terminal uid. | - | 3407 |
| `SimReader.ct_uids` |  | (no docstring) | - | 3411 |
| `SimReader.obj_uids` | cls | (no docstring) | - | 3414 |
| `SimBackend` | (class) | The DRY backend: every real op applies the plan actions it covers with stagesim's own OPS on a private state | - | 3422 |
| `SimBackend.read` |  | (no docstring) | - | 3435 |
| `SimBackend.read_owners` | uids | card chat-S4 B: the per-owner read - the rows of these owner uids only (what read() would return for them). | - | 3440 |
| `SimBackend.obj_classes` | real | (no docstring) | - | 3445 |
| `SimBackend.move_in` | uid, dest, pos, op | (no docstring) | - | 3523 |
| `SimBackend.add_sr` | loop, y, op | (no docstring) | - | 3528 |
| `SimBackend.create` | route, a, args, real, op | (no docstring) | - | 3544 |
| `SimBackend.stop` | loop, src, real, op | (no docstring) | - | 3640 |
| `SimBackend.value_gate` | uid, a, op | (no docstring) | - | 3652 |
| `SimBackend.recheck_gate` | uid, a, op | card 103-4: the dry side of a Part-B entry's gate re-read - the constant must still be a BooleanConstant of | - | 3665 |
| `SimBackend.wire_sr` | variant, loop, right, term, real, op | (no docstring) | - | 3672 |
| `SimBackend.connect` | src, dst, real, loop_of, op | (no docstring) | - | 3690 |
| `SimBackend.branch` | tun, dst, real, loop_of, op, side='outer' | (no docstring) | - | 3703 |
| `SimBackend.case_frame_wire` | case, k, src, dst, real, op | card 124-2 (PD249(d)): the dry side of gscript.case_frame_wire - the verb is defined, the case exists with a frame | - | 3715 |
| `SimBackend.connect_term_uid` | src, dst, real, op | card 124-6 (PD250(c)): the dry side of an R1/R2 group - the verb is defined; one end is a shift register's INNER | - | 3813 |
| `SimBackend.index_mode_fix` | tun, indexing | (no docstring) | - | 3852 |
| `SimBackend.delete_wire` | w, op, plan_wire=None | (no docstring) | - | 3855 |
| `SimBackend.delete_object` | cls, uid, op | (no docstring) | - | 3858 |
| `SimBackend.rbw` | op | (no docstring) | - | 3861 |
| `SimBackend.rle` | wires, op | (no docstring) | - | 3864 |
| `from_step_state` | plan_path, from_step, binding | card 103-4: the offline stand-in for the saved Part-A file - simulated step (last act of op k) with every created | - | 3879 |
| `rel_root` | p | (no docstring) | - | 3925 |
| `is_real_backend` | be | True for a backend that drives LabVIEW (LVBackend, possibly wrapped by RetireGuardBE); False for SimBackend and its | - | 3932 |
| `tag_switch` | path=None | The in-VI tag switch (default OFF): tools/bench/creation_tag.json {"enabled": false}. Missing/unreadable -> OFF. | - | 3941 |
| `tag_text` | stage, plan_id, sim_uid | The Description text of a created object: 'claude-plan:<stage>:<plan action id>:<sim id>'. | - | 3950 |
| `parse_tag` | text | (stage, plan id, sim id) of a tag_text string, else None. | - | 3955 |
| `adopt_stage_key` | path | The stage a script belongs to: basename, lower case, '_vN' and a '_scratch<N>' suffix stripped | - | 3961 |
| `adopt_verdict` | text, required=() | Pure: {ok, why, n_pass, stop_fails, log_fails, missing, stops, results} for one scratch log segment. | - | 3969 |
| `adopt_scratch` | script, log_path, artefact, input_vi, input_md5, plan_md5s, required, path=None, claudedev=None, note='', now=None | A: (ok, record / reasons). The scratch run's own log segment (the last BGRUN segment) must pass adopt_verdict; the | - | 4023 |
| `read_adoptions` | path=None | (no docstring) | - | 4062 |
| `adopted_launch` | script, plan_md5s, path=None | A, the launch gate's question: the newest non-revoked adopt/1 record of this stage (the scratch wrapper and the stage | - | 4074 |
| `prefix_fingerprint` | plan, s_act | R: sha256 of the base graph md5 + actions 1..s_act - what must be unchanged for a FIXED plan to resume at s_act. | - | 4083 |
| `plan_bed_vi` | plan | The real bed VI a plan's base graph was read from (its 'vi' key), or None. | - | 4091 |
| `write_resume` | rec, file_path, cycle, out_path=None, plan=None | R: complete a resume_record with the scratch file saved as-is (path + md5) and the cycle, refuse the bed, write JSON. | - | 4099 |
| `load_resume` | path, plan_path, cycle | R: the resume record -> the binding dict Executor(from_step=rec['stop_after'], binding=...) takes, after the checks: | - | 4117 |
| `save_for_resume` | s, x, e, cycle=None | R, a recipe's ExecStop handler (before report_stop): the resume record of the stop, the scratch SAVED AS-IS (Stage.save | - | 4141 |
| `adopt_cli` | argv | 'py tools/stagexec.py adopt --script S --log L --artefact VI --input VI --input-md5 M --required E1,PB,PS [--plan P ...]' | - | 4165 |
| `DryPlanBE` | (class) | stage_prerun's dry backend for a plan-executing recipe (stage_d1_disp.DryBE, after stage_d1_l2a1.DryBE): the plan's | - | 4190 |
| `w0_wires` | s, base, from_step, dry | W0: the pre-existing Wire uids W1 judges RBW against - S1's from the plan base graph for a PART-B run (== Part A's | - | 4208 |
| `retire_check` | rows, uids | (ok, detail) on ONE terminal read: 'uids' = the nodes one delete removes (a register pair). FAILS when a node of | - | 4223 |
| `retire_ends` | base_rows, rows, retire | (ok, detail): every wire that carried a terminal of a retired node AND a terminal of a kept node still carries, | - | 4238 |
| `RetireGuardBE` | (class) | Wraps a backend (LVBackend or DryPlanBE): delete_object first reads the graph ('read()' = the live file, or the | - | 4264 |
| `RetireGuardBE.delete_object` | cls, uid, op | (no docstring) | - | 4278 |
| `report_stop` | s, x, be, e | An ExecStop inside Executor.run: record the report / meter / step diffs, list every unroutable row, FAIL E1 fatally. | - | 4287 |
| `log_step_diffs` | s, x | Every recorded step diff as a STEP-WARN / STEP-DIFF fact; returns the FAIL-class ones (PD214(c): WARN = dangling only, | - | 4303 |
| `b1_gate` | s, x, from_step | PART-B entry gate (card 103-4): the entry read == simulated step from_step (or a WARN), gates re-read, parity, PRIME, | - | 4314 |
| `part_a_gates` | s, x, be, stop | card 103-1 PART-A (PD215(b)): ops 1..stop only, step stop real == sim (WARN only), gui_save, md5 + binding JSON. | - | 4324 |
| `w1_rbw` | s, be, w_pre | W1 (PD211(b) / PD212(f)): termless wires after the batch, then RBW on the work copy - it may remove only pre-existing | - | 4335 |
| `e3_gate` | s, plan, x, be, real, wiki, dry, tag | PD217(c) E3 (FATAL, before save) on the executor's end - also in the dry run, where a failing E3 is a FAIL | - | 4355 |
| `kill_labview_at_exit` |  | A live recipe's last act: taskkill LabVIEW and report whether it is gone (CLAUDE.md 1b grant: every cycle ends with | - | 4367 |
| `dry_run` | plan_path, fault=None, log=print, model_dir=None, require_final=True, from_step=None, binding=None | (status, first_fail, executor). No LabVIEW. require_final=False = the DIAGNOSTIC routability run (card 100-3). | - | 4378 |
| `prerun_plan` | plan_path, log=print, model_dir=None | Offline gates for a plan launch: final + step files intact (load_final_plan), compile, open_rows declared and | - | 4408 |
| `e3_wiki` | plan | The S1 wiki record whose fs tunnel pairs + graph summary build the E3 end graph (context fs_pairs_wiki, else s1_key). | - | 4443 |
| `e3_graph` | plan, ex, objs, real, wiki, tag='E3 end' | The END graph E3 compares with S1: the real (or dry) end terminals + objects, the plan's last-step loops translated | - | 4452 |
| `e3_eval` | plan, S1, G, created, deleted | PD217(c) E3, pure: cdiff(S1, G) rows == the plan open rows of PD213(d) classes (1)-(3) (want derived from each row's | - | 4467 |
| `e3_created` | plan, ex | (created, deleted) for e3_eval: created = the real uids the binding holds for SIMULATED-created ids (sim ids < 0: | - | 4490 |
| `e3_check` | plan, ex, objs, real, wiki, tag='E3 end' | PD217(c) E3 on an executor's end (live or dry): builds the end graph (e3_graph), S1 (stagesim.load_s1), the created | - | 4500 |
| `e3_line` | r | One-line E3 verdict for a gate label/detail. | - | 4510 |
| `lv_run` | plan_path, reference=None, max_min=60 | (no docstring) | - | 4518 |
| `canon_diff` | real_a, real_b, base_nodes | Two real reads compared up to new-uid naming: a node outside 'base_nodes' is its class. | - | 4572 |
| `selftest` |  | (no docstring) | - | 4771 |
| `proposed_schema` | on=True | TEST / DIAGNOSTIC ONLY (card 100-3): the installed docs/protocol/stageplan.json has integer-only diagram fields, | - | 5483 |
| `main` | argv | (no docstring) | - | 5874 |

### tools/stop_record.py

shared module; imported by 26 file(s): `tools/bench/c19_close_release_probe.py`, `tools/bench/c20_release_probe.py`, `tools/bench/c22_v1_gate_probe.py`, `tools/bench/c58c_gatecheck.py`, `tools/bench/diag_c111c_realstore.py`, `tools/bench/diag_c111c_regress.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `exempt_program` | command_string | The path of the command-position program of this SEGMENT when it is one of EXEMPT_PROGRAMS, else ''. | - | 105 |
| `offline_checker` | segment | True when this SEGMENT runs tools/stage_prerun.py --dry/--prerun in command position (bgrun-wrapped or not). | - | 143 |
| `declared_offline` | prog_path, rest | card chat-E3 (fp-37): True when the command-position program is a tools/ script whose SCOPE HEADER makes THIS | - | 157 |
| `split_segments` | cmd | Shell segments split on && // ; / newline OUTSIDE quotes (so 'py -c "a;b" X' stays one segment). Falls back | - | 254 |
| `substitutions` | text | The inner commands of the OUTERMOST '$( ... )' in 'text' (balanced parentheses; an unclosed one runs to the | - | 304 |
| `binding_name` | seg | NAME when this segment is 'for NAME in ...' or a pure 'NAME=VALUE' (nothing runs after it), else ''. | - | 323 |
| `segment_class` | seg, whole_cmd='' | 'exempt' / 'readonly' / 'build' for one segment - the command-class axis of DECISION_TABLE. | - | 350 |
| `command_keys` | command_string, _taint=None, _depth=0 | {key: strictest command class} over every path token of the command. | - | 398 |
| `StoreError` | (class) | The record store exists in principle but cannot be trusted right now. | - | 431 |
| `keys_for` | path | The match keys for one path token or record path: ('rel', <project-relative, posix, lower>) and | - | 439 |
| `sha256_of` | path | card chat-E3: a .py/.ps1 is hashed WITHOUT its scope header block (tools/scope_header.canonical_bytes) - the | - | 468 |
| `load_records` |  | Every standing record. Raises StoreError when the store cannot be trusted - callers fail closed. | - | 512 |
| `save_records` | records | (no docstring) | - | 540 |
| `verdict_slugs` | record | (no docstring) | - | 555 |
| `write_stop_record` | recipe_path, review_file, verdict, root=None | Plant a stop record for 'recipe_path', keyed to the bytes the review saw. | - | 564 |
| `novel_in_answer` | body | True iff the review's ANSWER carries 'PRIOR-ART: novel' and NO blocking slug (guard_cycle's own regex and | - | 601 |
| `write_novel_record` | recipe_path, review_file | cycle 72 firefighter (2026-09-24): a 'novel' verdict over EDITED bytes used to leave NO record, so the older | - | 612 |
| `record_state` | records, i | (kind, state, line, why, cur_sha) of records[i] - the row key of DECISION_TABLE. 'line' is the release line | - | 698 |
| `check_command` | command_string | (allow, message). The launch gate. Fails CLOSED for commands naming 'tools/recipes/', and never wedges | - | 781 |

### tools/vigraph.py

shared module; imported by 159 file(s): `tools/addrcheck.py`, `tools/bench/c73_l7r_facts.py`, `tools/bench/c73_l7r_live.py`, `tools/bench/cdiff_blindspot_74.py`, `tools/bench/ct23541_facts_80.py`, `tools/bench/dedupe_check_s2b.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `node_of` | row | The GRAPH NODE a terminal row belongs to: its owner, except a front-panel terminal, which is its | - | 57 |
| `node_class` | row | (no docstring) | - | 63 |
| `build` | terms, wires, objs=None | {adj, nodes, cls, method} - a directed node-uid graph. Pure; no LabVIEW, no mutation of the input. | - | 67 |
| `reach` | graph, starts | Every node uid reachable from 'starts' (node-level, forward). | - | 148 |
| `fp_terminals` | terms | The VI's own front-panel control/indicator terminals: leaf class 'ControlTerminal'. | - | 166 |
| `io_paths` | graph, terms, labels_in=None, labels_out=None | {output label: [input labels that can reach it]} over the front-panel terminals. | - | 178 |
| `key_parts` | key | (no docstring) | - | 248 |
| `show` | key | (no docstring) | - | 254 |
| `dedupe_rows` | terms | (rows, record): the terminal rows with a repeated 'term_uid' dropped, FIRST occurrence wins. | - | 260 |
| `build4` | terms, objs=None, loops=None, labels=None, fs_pairs=None, frame_keyed=False | The full terminal-level graph. 'terms' = OpAllTerms_v1 rows (the 7th column 'frame_diagram' is | - | 334 |
| `is_scheduling` | G, node | ASSUMPTION A. A node is SCHEDULING when its class is a tunnel / shift register / structure / | - | 632 |
| `transparent` | G, key | ASSUMPTION A, at TERMINAL level: is this terminal a scheduling RELAY to walk through? | - | 641 |
| `terminals` | G, node=None, name=None, term_uid=None, is_source=None, cls=None | Terminal KEYS matching the filter - the addressing helper the queries below take. | - | 653 |
| `wire_terminals` | G, wire_uid | (no docstring) | - | 671 |
| `reach4` | G, starts, kinds=None | Every terminal key reachable DOWNSTREAM of 'starts' (terminal keys, or node uids). | - | 675 |
| `sources_of` | G, sink, kinds=None, collapse=False | Every terminal key UPSTREAM of 'sink'. 'collapse=True' returns only COMPUTATION terminals, | - | 692 |
| `path` | G, a, b, kinds=None | One shortest terminal path a -> b as a list of terminal keys, or [] if there is none. | - | 714 |
| `diff` | A, B, kinds=DIFF_KINDS | Edges added / removed / changed between two graphs, keyed by (owner uid, terminal name) and | - | 742 |
| `effective_sources` | G, key, memo=None | The COMPUTATION terminals whose value reaches 'key' through scheduling relays only. | - | 782 |
| `computation_diff_frame` | A, B | PD180(b): computation_diff over two FRAME-KEYED graphs (build4(..., frame_keyed=True)). Refuses a mix. | - | 840 |
| `pos_keys` | G | card 153-b2-1 (gate-fp fp-70, docs/d1/ring-p4d.md PD370(d)): {terminal key: POSITION KEY (node, index, term class, | - | 847 |
| `computation_diff` | A, B | ASSUMPTION A's rule-1a question: for every COMPUTATION node (subVI, primitive, constant, | - | 877 |

### tools/violations.py

shared module; imported by 1 file(s): `tools/retro_due.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `threshold` | slug | (no docstring) | - | 79 |
| `decisions` |  | slug -> the date of its most recent decision block. A decision older than the retrospective that raised the | - | 122 |
| `is_comparison` | body | True if the archive's YAML frontmatter carries 'comparison: true'. | - | 149 |
| `scan` |  | (hits, loss) - slug -> the retrospectives that named it, and slug -> (loss_min, loss_usd, n_with_a_figure). | - | 163 |
| `main` |  | (no docstring) | - | 193 |

### tools/wiki_build.py

shared module; imported by 84 file(s): `tools/bench/build_kswap_88.py`, `tools/bench/c73_l7r_live.py`, `tools/bench/diag_c107b_bedgraph.py`, `tools/bench/diag_c108b_graph.py`, `tools/bench/diag_c108d_graph.py`, `tools/bench/diag_c108d_selind.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `subvi_rows` | target, diagram_index | 'gscript.subvis(strict=False)' returns (rows, err) - rows only, and an error on ONE diagram | - | 76 |
| `md5` | path | (no docstring) | - | 83 |
| `fact` | line | (no docstring) | - | 91 |
| `targets` |  | (no docstring) | - | 95 |
| `key_of` | path | The wiki key. NOT the bare file name: 'background VIs' carries the subfolder | - | 104 |
| `call_sites_index` |  | (no docstring) | - | 116 |
| `conpane_pass` | paths, chunk=12 | {path: [{index, label, direction, type}]} - drop each VI on a scratch EMPTY_v0 copy and read the | - | 127 |
| `read_fs_tunnels` | path, objs, uids=None | STEP 4b: every flat-sequence tunnel's two faces, READ from the machine, one op run per tunnel. | - | 202 |
| `read_live` | path, fs_pairs=None, fs_uids=None | STEP 5b: the graph INPUTS of a live (scratch) VI, without the wiki's subVI/conpane passes: the GObject | - | 233 |
| `read_one` | path, conpane, calls, main_vi | One VI -> the wiki record. Two op runs (GObject census, Terminal traverse) + one subvis per diagram. | - | 259 |
| `main` | argv=None | (no docstring) | - | 355 |

### tools/bench/bench_prep.py

shared file in the bench folder (move to tools/ later); imported by 293 file(s): `tools/bench/allterms_s4.py`, `tools/bench/allterms_v1_check.py`, `tools/bench/build_kswap_88.py`, `tools/bench/build_op_const_loopterm_77.py`, `tools/bench/build_op_termtype.py`, `tools/bench/build_opstopmode_v0.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `ps` | *args | (no docstring) | - | 26 |
| `com_alive` | timeout_s=40 | Alive = Application.Version answers AND a real VI Run (exec_state of the bench VI) returns | - | 34 |
| `labview_handles` |  | (no docstring) | - | 64 |
| `restart_labview` |  | (no docstring) | - | 74 |
| `main` |  | (no docstring) | - | 82 |

### tools/bench/build_opstopmode_v0.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/bench/build_opwiringrules_v0.py`, `tools/bench/diag_c138_6_run.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `Stop` | (class) | (no docstring) | - | 38 |
| `md5` | p | (no docstring) | - | 42 |
| `gate` | k, ok, d='', need=True | (no docstring) | - | 45 |
| `fact` | k, v | (no docstring) | - | 52 |
| `B` | (class) | (no docstring) | - | 55 |
| `B.purge` | s | (no docstring) | - | 63 |
| `B.idx` | s, cls, uid | (no docstring) | - | 71 |
| `B.terms` | s, uid | (no docstring) | - | 73 |
| `B.pn` | s, cls, props, pos | (no docstring) | - | 82 |
| `B.w` | s, su, st, du, dt, sc='Property', dc='Property', branch=False | (no docstring) | - | 85 |
| `B.panel` | s, ind | (no docstring) | - | 88 |
| `B.ind` | s, uid, term | (no docstring) | - | 90 |
| `B.ctl` | s, uid, term | (no docstring) | - | 96 |
| `B.data` | s, uid, src | (no docstring) | - | 102 |
| `B.node_with` | s, *names | (no docstring) | - | 105 |
| `finish` | b, key, lab, save=True | (no docstring) | - | 110 |
| `build_a` |  | (no docstring) | - | 119 |
| `build_b` |  | (no docstring) | - | 132 |
| `build_writer` | src_key, out, cls, pid, after | (no docstring) | - | 163 |
| `call` | path, la, target, idx, extra=None, tt=0 | (no docstring) | - | 176 |
| `rd` | key, target, idx, tt=0 | (no docstring) | - | 203 |
| `wr` | wpath, wkey, rkey, target, idx, value | A scratch writer = a copy of the reader + one write PN: its labels are the reader's plus Value/WErr. | - | 209 |
| `scratch_target` |  | (no docstring) | - | 215 |
| `main` |  | (no docstring) | - | 234 |

### tools/bench/build_ringpickslot_v2.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/build_ringseqcheck_v0.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `CMP` | o | (no docstring) | - | 21 |
| `ref` | num, last | (no docstring) | - | 22 |
| `peak` |  | (no docstring) | - | 23 |
| `kill` | tag | (no docstring) | - | 24 |
| `canon` | k | (no docstring) | - | 25 |
| `reg` | u, tag, want | (no docstring) | - | 26 |
| `tr` | R, k | (no docstring) | - | 29 |
| `Wr` | tag, snk, src | (no docstring) | - | 31 |
| `mk` | fn, u, name, src, tag | (no docstring) | - | 33 |
| `dele` | u, cls | (no docstring) | - | 39 |
| `build` |  | (no docstring) | - | 43 |
| `runs` | tag, idx | (no docstring) | - | 94 |
| `main` |  | (no docstring) | - | 102 |

### tools/bench/c131_2_reach.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/bench/c131_2_why.py`, `tools/bench/diag_c131_2_offline.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `script_touches_labview` | script, _seen=None | v2: True when the LAUNCHED 'script' can open LabVIEW (rules in the module docstring). Fails closed. | - | 154 |

### tools/bench/c60c_astcheck.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/bench/c74_gate10_report.py`, `tools/jev_preflight.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | name, ok, detail='' | (no docstring) | - | 98 |
| `defs_in` | path | (no docstring) | - | 105 |
| `allow_broken_sites` | tree | Every call that passes 'allow_broken' as anything other than literal 'False'. | - | 116 |
| `percent_format_sites` | tree, path | Every '<literal string> % <args>' site, classified. | - | 199 |
| `main` |  | (no docstring) | - | 276 |

### tools/bench/c90c_rows.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/bench/c90d_reads.py`, `tools/bench/diag_c90c_rowtable.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `tok` | s, R, t, text | (no docstring) | - | 19 |
| `t1_wires` | s, p, census, R | TASK 1: each of the 11 read WHOLE (n=8); the row dict prints VERBATIM, error columns included. | - | 24 |
| `t2_terms` | s, p, art, R | TASK 2: index -> (Terminal.Name, Terminal.Connected Wire, WIRED/BARE/UNREAD) for #48 and #10407. | - | 42 |
| `t3_owners` | s, p, R | TASK 3: 'Generic.Owner' 6327806 -> GObject UID on the four tunnels, plus each one's own class. | - | 63 |
| `controls` | s, p, art, census, pos, R | The two mandatory controls as VALUES: the negative uid must not echo; one intact wire must read. | - | 79 |
| `linemap` | R, logp | Each token's own line number in THIS run's log, so every cell of the table cites 'log:line'. | - | 98 |
| `cite` | n, m | Replace every 'src_tok' by its 'log:line'; a token the log never carried becomes 'unread'. | - | 113 |

### tools/bench/c90d_border.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_c90d_outstanding.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `borders` | s, p, art, R | MEASUREMENT 2 (BED) and 3 (CLEAN): the four old border objects - owner, every terminal's wire, and | - | 21 |
| `sr_terms` | s, p, art, uid, cls, R | A shift register's OWN terminals, found by walking 'Loop.Shift Registers[]' until the uid matches. | - | 48 |
| `lt_terms` | s, p, art, uid, R | A LoopTunnel's two faces: 'gscript.tunnels' (OpTunnels_v0), addressed by the LoopTunnel census index. | - | 98 |

### tools/bench/c90d_reads.py

shared file in the bench folder (move to tools/ later); imported by 3 file(s): `tools/bench/c90d_border.py`, `tools/bench/c90d_table.py`, `tools/bench/diag_c90d_outstanding.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `own` | s, R, art, p, uid, tag | 'Generic.Owner' 6327806 -> GObject UID, strict: a uid that does not echo yields 'unread' + its error. | - | 32 |
| `census` | s, p, art, cls | (no docstring) | - | 44 |
| `net` | s, p, art, w, R, tag | One CACHED 'Stage.net_sources' read (n=8) - every terminal row of the wire, error columns verbatim. | - | 52 |
| `srl` | s, p, art, li, ri, lfi, cls='WhileLoop' | (no docstring) | - | 74 |
| `m1` | s, p, R | MEASUREMENT 1: the four UNREAD wires on the BED, every terminal row, plus 'Generic.Owner' on every | - | 85 |

### tools/bench/c90d_table.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_c90d_outstanding.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `assemble` | s, R, src, outp, logp, inputs | (no docstring) | - | 18 |

### tools/bench/camera_contract.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/p1_bufmode_121.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `AttributeInformation` | (class) | (no docstring) | - | 49 |
| `enumerate_attributes` | sess, root='' | Every attribute under 'root', as (name, type_code, readable, writable). | - | 54 |
| `get_string` | sess, name | (no docstring) | - | 65 |
| `set_string` | sess, name, value | (no docstring) | - | 71 |
| `set_f64` | sess, name, value | (no docstring) | - | 75 |
| `read_value` | sess, name, tcode | Read an attribute whatever its type, returning a JSON-safe value. | - | 79 |
| `snapshot` | sess | The values a batch directory must record: geometry, rate, and the whole exposure group. | - | 94 |
| `main` |  | (no docstring) | - | 111 |

### tools/bench/d0_locate.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/drive_original_copy_v5.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `load` | png | (no docstring) | - | 55 |
| `red_mask` | a | (no docstring) | - | 65 |
| `clusters` | mask, gap=6 | Connected components of a boolean mask, over the True coordinates only (a few thousand). | - | 70 |
| `button_around` | a, cx, cy, maxd=90 | Walk out from (cx,cy) to the first dark neutral pixel on each side. (l,t,r,b) or None. | - | 106 |
| `face_is_light` | a, box, red, need=0.8 | (no docstring) | - | 125 |
| `locate_red_yes_button` | png, rect, wmin=15, wmax=60, hmin=8, hmax=32, maxd=90 | (best, candidates) - 'best' is the largest red caption that passed every test. | - | 142 |
| `template_score` | png, box, ref_png=REF_DONE | (no docstring) | - | 175 |
| `pick_by_template` | png, rect, ref_png=REF_DONE, max_score=12.0, ratio=0.5, caption_ref=(25, 12), caption_tol=4, **kw | The disambiguator.  Returns (winner_or_None, why, candidates). | - | 189 |
| `locate_image_display` | png, rect, minw=200, minh=150 | (no docstring) | - | 230 |
| `count_red_markers` | png, rect, wmin=8, wmax=45, hmin=8, hmax=45 | The bead markers the VI draws at each pick.  Used as the post-click READBACK for the picks. | - | 264 |
| `save_crop` | png, box, out, pad=16, scale=4 | (no docstring) | - | 277 |

### tools/bench/d1_rewire_map.py

shared file in the bench folder (move to tools/ later); imported by 9 file(s): `tools/recipes/build_d1_routeb_v0.py`, `tools/recipes/build_d1_routeb_v1.py`, `tools/recipes/build_d1_routeb_v2.py`, `tools/recipes/build_d1_routeb_v3.py`, `tools/recipes/build_d1_routeb_v4.py`, `tools/recipes/build_d1_routeb_v5.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `load` | name | (no docstring) | - | 75 |
| `build_map` | cut | The resolver, callable from a build: 'cut' = S3b's own [[uid, i, name, is_source, wire], ...] list. | - | 83 |
| `main` |  | (no docstring) | - | 90 |

### tools/bench/diag_c100_verbs_build.py

shared file in the bench folder (move to tools/ later); imported by 4 file(s): `tools/bench/diag_c124_opconnecttermuid.py`, `tools/bench/diag_c125_5_opfs.py`, `tools/bench/diag_c126_2_op.py`, `tools/bench/diag_c126_4_op.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `md5` | p | (no docstring) | - | 56 |
| `gate` | k, ok, d='' | (no docstring) | - | 59 |
| `fact` | k, v | (no docstring) | - | 63 |
| `B` | (class) | (no docstring) | - | 67 |
| `B.purge` | s | (no docstring) | - | 75 |
| `B.idx` | s, cls, uid | (no docstring) | - | 83 |
| `B.terms` | s, uid | (no docstring) | - | 85 |
| `B.pn` | s, cls, props, pos | (no docstring) | - | 94 |
| `B.w` | s, su, st, du, dt, sc='Property', dc='Property', branch=False | (no docstring) | - | 97 |
| `B.panel` | s, ind | (no docstring) | - | 100 |
| `B.ind` | s, uid, term | (no docstring) | - | 102 |
| `B.ctl` | s, uid, term | (no docstring) | - | 108 |
| `B.data` | s, uid, src | (no docstring) | - | 115 |
| `B.wired` | s, uid, name, src | (no docstring) | - | 118 |
| `B.finish` | s, key, lab | (no docstring) | - | 121 |
| `retarget` | b, key, cls, props, pos | diag_c97_tools_opbuild.retarget:104 verbatim in substance: delete the donor IndexMode PN, seed-retarget the TMSC. | - | 139 |
| `uid_echo` | b, tmsc, pos | (no docstring) | - | 163 |
| `build_nested` | key, method | (no docstring) | - | 169 |
| `prim_donor` |  | A BYTE COPY of the NI example (the original is only read); the Max & Min node FOUND by node label. | - | 200 |
| `build_primcopy` | reg | (no docstring) | - | 232 |
| `hands` |  | (no docstring) | - | 277 |
| `owner_chain` | t, uid, hops=4 | [(cls, uid), ...] from #uid up to the first Diagram, READ at every hop (OpOwnerChain_v1) - never a fallback. | - | 280 |
| `term_index` | t, uid, pred | RUN-2 FAULT FIXED (_build2.log:81-91): a border node (owner = a structure) is in no Diagram.Nodes[], so it is | - | 293 |
| `block` | name, fn | (no docstring) | - | 306 |
| `v1` | T | (no docstring) | - | 313 |
| `v1b` | T | (no docstring) | - | 323 |
| `v3` | T, newrow | (no docstring) | - | 364 |
| `v2` | T | (no docstring) | - | 382 |
| `v5` | T, dest | gscript.create_local_write = the core stagekit.create_local_write binds to (stagekit.py:685-697 adds only the | - | 425 |
| `v6` | T | (no docstring) | - | 452 |
| `selftest` |  | (no docstring) | - | 477 |
| `main` |  | (no docstring) | - | 510 |

### tools/bench/diag_c108c_graph.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_c108c_groupB.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `Graph` | (class) | (no docstring) | - | 18 |
| `Graph.cite` | term_uid | (no docstring) | - | 60 |
| `Graph.node` | t | (no docstring) | - | 65 |
| `Graph.ncls` | n | (no docstring) | - | 68 |
| `Graph.struct_of_tunnel` | u | (no docstring) | - | 71 |
| `Graph.diag` | n | (no docstring) | - | 79 |
| `Graph.chain` | n | structures enclosing node n, inner -> outer. | - | 84 |
| `Graph.loop` | n | (no docstring) | - | 94 |
| `Graph.label` | n | (no docstring) | - | 100 |
| `Graph.is_motor` | n | (no docstring) | - | 107 |
| `Graph.through_down` | t | sink terminal t of a carrier -> source terminals to continue from ([] = not a carrier). | - | 110 |
| `Graph.through_up` | t | source terminal t of a carrier -> sink terminals to continue from. | - | 127 |
| `Graph.walk` | start, down, stop | first non-carrier ends from terminal 'start'; 'stop(node)' True = end there (e.g. group-B member). | - | 145 |

### tools/bench/diag_c115d_sel.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_c115d_sel2.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `pane` | p | (no docstring) | - | 23 |
| `shift` | a, b | (dy, dx, peak): b[y, x] ~ a[y + dy, x + dx]. | - | 27 |
| `overlap` | a, b, dy, dx | views of a and b on their common area, both in b's frame: returns (a_part, b_part, (y0, y1, x0, x1) in b). | - | 37 |
| `changed` | a, b, dy, dx | (no docstring) | - | 46 |
| `main` |  | (no docstring) | - | 58 |

### tools/bench/diag_c118_p0.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/bench/diag_c118_p1.py`, `tools/recipes/stage_d1_qrt_pool.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `u8` | v | (no docstring) | - | 25 |
| `read_str` | t, uid | (no docstring) | - | 32 |
| `read_num` | t, uid | (no docstring) | - | 44 |
| `body` | _ | (no docstring) | - | 64 |
| `probe` | T | (no docstring) | - | 90 |

### tools/bench/diag_c138_6_run.py

shared file in the bench folder (move to tools/ later); imported by 6 file(s): `tools/bench/build_ringpickslot_v0.py`, `tools/bench/build_ringpickslot_v1.py`, `tools/bench/build_ringpickslot_v2.py`, `tools/bench/diag_c139_1_run.py`, `tools/bench/diag_c139_3_run.py`, `tools/bench/diag_c140_5_run.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `ldump` |  | (no docstring) | - | 34 |
| `rows` | t | (no docstring) | - | 35 |
| `one` | rs, **kw | (no docstring) | - | 36 |
| `el_count` | W, tag | (no docstring) | - | 39 |
| `step0` |  | (no docstring) | - | 45 |
| `step1` |  | (no docstring) | - | 51 |
| `step3` |  | (no docstring) | - | 61 |
| `step4` |  | (no docstring) | - | 69 |
| `cp` | dg, prim, pos, donor | (no docstring) | - | 91 |
| `step2` |  | (no docstring) | - | 93 |
| `main` |  | (no docstring) | - | 139 |

### tools/bench/diag_c153_b2_1_rescore.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_c153_b2_1_s06pos.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | label, ok, detail='' | (no docstring) | - | 32 |
| `old_vigraph` |  | (no docstring) | - | 39 |
| `score` | tag, VO, S1f, G1, stored=None | (no docstring) | - | 46 |
| `main` |  | (no docstring) | - | 66 |

### tools/bench/diag_c61_localdir_write2.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/q_m4_iterlocal.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `Stop` | (class) | (no docstring) | - | 145 |
| `gate` | name, ok, detail='', fatal=False | (no docstring) | - | 149 |
| `fact` | line | (no docstring) | - | 158 |
| `probe` | tag, path | (no docstring) | - | 163 |
| `dump` |  | (no docstring) | - | 170 |
| `read_exec_state` | rec, tag, target | ONE global ordered timeline, so 'the ExecState after every single step' is a single list. | - | 178 |
| `count_of` | target, cls | (no docstring) | - | 193 |
| `uid_set` | target, cls | (no docstring) | - | 200 |
| `close_quietly` | target | (no docstring) | - | 207 |
| `node_label_rows` | target, di, fresh=False | (no docstring) | - | 217 |
| `locate` | target, uid, fresh=False | uid -> owner / diagram index / candidate node index, ALL read off the machine. Owner comparisons accept | - | 229 |
| `terms_of_uid` | target, loc | node_terms on the located node, VERIFIED by the node's own UID; bounded scan fallback. | - | 261 |
| `term_rows_verbatim` | terms | (no docstring) | - | 302 |
| `find_create_local_invoke` | target, di | Six terminals whose (4,5) are both named 'Create Local'. Returns (node_index, node_uid, rows). | - | 309 |
| `find_property_node` | target, di, direction_name | The node carrying BOTH a terminal named 'reference' and one named <direction_name> (e.g. 'Write?'). | - | 324 |
| `one_probe` | K, target, cls, pid, is_write, pos, tag | Create ONE property node for (cls, pid, is_write) and read EVERYTHING off it. (Dispatch #2's helper, | - | 339 |
| `build_and_save` |  | (no docstring) | - | 388 |
| `st6_cold_reopen` |  | (no docstring) | - | 571 |
| `call_new_op` | target, fp_index, write_flag, bool_label, tag | (no docstring) | - | 591 |
| `s4_readback` | bool_label | (no docstring) | - | 646 |
| `hygiene` | fp_index, bool_label | (no docstring) | - | 717 |
| `st7_ordered_pass` | direction_name, saved_md5 | (no docstring) | - | 758 |
| `main` |  | (no docstring) | - | 851 |

### tools/bench/diag_c81_uidref.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_c86_norbw.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | name, ok, detail='' | (no docstring) | - | 119 |
| `fact` | line | (no docstring) | - | 126 |
| `head` | t | (no docstring) | - | 131 |
| `safe` | label, fn, default=None | (no docstring) | - | 135 |
| `md5` | path | (no docstring) | - | 144 |
| `dump` |  | (no docstring) | - | 153 |
| `left_s` |  | (no docstring) | - | 161 |
| `phase_0` |  | (no docstring) | - | 166 |
| `phase_1` |  | (no docstring) | - | 184 |
| `phase_v` |  | (no docstring) | - | 212 |
| `phase_a` |  | (no docstring) | - | 249 |
| `phase_b` |  | (no docstring) | - | 288 |
| `probe_ownerchain` | vi, lab, target, uid, quiet=False | OpOwnerChain_v1 = UID to GObject Reference.vi -> [self Class Name / self UID] + Generic.Owner -> | - | 366 |
| `probe_fsit` | vi, lab, target, uid | OpFsInnerTunnelTerm_v0 = the SAME UID to GObject Reference.vi, then a TMSC seeded | - | 415 |
| `phase_p` |  | (no docstring) | - | 438 |
| `phase_s` |  | (no docstring) | - | 514 |
| `phase_hygiene` |  | (no docstring) | - | 534 |
| `main` |  | (no docstring) | - | 586 |

### tools/bench/diag_c83_connect2x2.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/bench/diag_c83_connect2x2_r2.py`, `tools/recipes/build_d1_m3a3b_d3.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | name, ok, detail='', fatal=False | (no docstring) | - | 141 |
| `fact` | line | (no docstring) | - | 150 |
| `head` | t | (no docstring) | - | 155 |
| `safe` | label, fn, default=None | (no docstring) | - | 159 |
| `dump` |  | (no docstring) | - | 168 |
| `left_s` |  | (no docstring) | - | 176 |
| `invoke_node` | target | (Nodes[] index, uid, terminal rows) of the single 'Invoke Node' on diagram 0. | - | 180 |
| `ind_labels` | target | (no docstring) | - | 189 |
| `ctl_labels` | target | (no docstring) | - | 193 |
| `attach_error_indicator` | target, tag | STEP 0's repair, and the same repair on the scratch connect op: walk the Invoke's 'error out' chain | - | 197 |
| `attach_auto_route` | target, tag | A front-panel control on the Invoke's 'Auto Route?' terminal. Returns (label or '', note). | - | 249 |
| `fsit_call` | op_path, labels, target, fsit_uid, sink_diag, sink_node, sink_term, ar_label='', auto_route=None, inv_err_label='', c... | 'C82.fsit_connect' PARAMETERISED BY OP PATH (that function hard-wires the module global 'OP'). | - | 267 |
| `conn_call` | op_path, target, inv_node, inv_term, ws_node, ws_term, ar_label='', auto_route=None, inv_err_label='' | 'gscript.connect_terminals':2518 driven through an explicit op path - (index, index 2) is the | - | 330 |
| `phase_files` |  | (no docstring) | - | 368 |
| `phase_restart` |  | (no docstring) | - | 399 |
| `step0` |  | (no docstring) | - | 414 |
| `make_ar_connect` |  | (no docstring) | - | 456 |
| `make_ar_fsit` |  | (no docstring) | - | 483 |
| `make_swapped` |  | (no docstring) | - | 500 |
| `make_trivial` | cell | A FRESH trivial VI: two bare 'VI Server:GObject' Property nodes. SOURCE = A.'reference out', | - | 554 |
| `read_pair` | target, a, b | The two terminals' own wire uids, re-read off the machine. | - | 582 |
| `step1` | ar_label, err_label, ar_ok | (no docstring) | - | 593 |
| `step2` | labels, err_label, arf_label, arf_ok, swap_label, swap_ok | (no docstring) | - | 653 |
| `phase_hygiene` |  | (no docstring) | - | 753 |
| `summary` |  | (no docstring) | - | 812 |
| `main` |  | (no docstring) | - | 837 |

### tools/bench/diag_c83_connect2x2_r2.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_c83_connect2x2_kit.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | name, ok, detail='', fatal=False | (no docstring) | - | 130 |
| `fact` | line | (no docstring) | - | 139 |
| `head` | t | (no docstring) | - | 144 |
| `safe` | label, fn, default=None | (no docstring) | - | 148 |
| `dump` |  | (no docstring) | - | 157 |
| `left_s` |  | (no docstring) | - | 165 |
| `fsit_call2` | op_path, labels, target, fsit_uid, sink_diag, sink_node, sink_term, ar_label='', auto_route=None, inv_err_label='', p... | 'diag_c83_connect2x2.fsit_call' with the POISON PASS made optional - the review | - | 169 |
| `phase_files` |  | (no docstring) | - | 234 |
| `phase_restart` |  | (no docstring) | - | 254 |
| `step0_raw_error` |  | (no docstring) | - | 268 |
| `make_arf` |  | (no docstring) | - | 323 |
| `make_swap` |  | (no docstring) | - | 340 |
| `run_cells` | labels, arf_label, arf_ok, swap_label, swap_ok | (no docstring) | - | 417 |
| `phase_hygiene` |  | (no docstring) | - | 523 |
| `summary` |  | (no docstring) | - | 576 |
| `main` |  | (no docstring) | - | 602 |

### tools/bench/diag_c91_step4_stats.py

shared file in the bench folder (move to tools/ later); imported by 6 file(s): `tools/bench/diag_c91_step4.py`, `tools/bench/diag_c92c_abba.py`, `tools/bench/diag_c93b_abba.py`, `tools/bench/diag_c93b_flushalign.py`, `tools/bench/diag_c94_abba.py`, `tools/bench/f7911_facts_94_offline.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `load` | d | (no docstring) | - | 13 |
| `pct` | a, q | (no docstring) | - | 21 |
| `bucket` | i_ticks, s_ticks | for each stamp in s_ticks: (iteration k, delta ticks); stamps before the first i stamp are dropped. | - | 27 |
| `table` | d | (no docstring) | - | 37 |

### tools/bench/diag_c94_sites.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_c94_abba.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `meta_overflow` | sm | (no docstring) | - | 13 |
| `mean` | a | (no docstring) | - | 22 |
| `summarize` | raw | (no docstring) | - | 27 |

### tools/bench/diag_d1_execstate_preload.py

shared file in the bench folder (move to tools/ later); imported by 7 file(s): `tools/bench/c52_astcheck.py`, `tools/bench/diag_s2_scaffold.py`, `tools/bench/verify_d1_s2.py`, `tools/recipes/stage_d1_s1.py`, `tools/recipes/stage_d1_s2.py`, `tools/recipes/stage_d1_s2_loops.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | label, ok, detail='' | (no docstring) | - | 68 |
| `fact` | s | (no docstring) | - | 75 |
| `md5` | p | (no docstring) | - | 79 |
| `llb_root` | path | Nearest ancestor path component of 'path' whose name ends in .llb, or None. | - | 91 |
| `path_status` | path | OK (on disk) / IN-LLB (member of an existing .llb container) / MISSING / EMPTY. | - | 103 |
| `child` | tag, target, preload | (no docstring) | - | 116 |
| `run_condition` | tag, target, preload | (no docstring) | - | 192 |
| `main` |  | (no docstring) | - | 219 |

### tools/bench/diag_donor_census.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/c52r3_astcheck.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `Stop` | (class) | (no docstring) | - | 125 |
| `gate` | name, ok, detail='', fatal=True | (no docstring) | - | 129 |
| `fact` | line | (no docstring) | - | 139 |
| `probe` | tag, path | (no docstring) | - | 144 |
| `dump` |  | (no docstring) | - | 151 |
| `census` | tag, target | (no docstring) | - | 158 |
| `main` |  | (no docstring) | - | 165 |

### tools/bench/diag_fstunnel_preclean_twins.py

shared file in the bench folder (move to tools/ later); imported by 3 file(s): `tools/bench/diag_fstunnel_orphan_timeline.py`, `tools/bench/diag_fstunnel_wireterms_panel.py`, `tools/bench/diag_fstunnelterm_v2_panelcost.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `must` | label, ok, detail='' | (no docstring) | - | 114 |
| `note` | label, value | (no docstring) | - | 120 |
| `md5` | p | (no docstring) | - | 124 |
| `snapshot` | tag | (no docstring) | - | 135 |
| `handles` | tag | (no docstring) | - | 143 |
| `nterms` | by | (no docstring) | - | 157 |
| `orphan_wires` | target, by | (orphan uids, whole Wire census). COPIED from build_opfstunnelterm_v2.py:465-470 - a wire is an ORPHAN when | - | 161 |
| `rbw_at` | target, where | The ONLY route to remove_bad_wires_scripted in this file. Refuses unless a twin has frozen at B4 (P6). | - | 169 |
| `rbw_call_sites` |  | (no docstring) | - | 191 |
| `StopAtB4` | (class) | (no docstring) | - | 203 |
| `do_preclean` | target | Remove the donor copy's OWN orphan wires - and nothing else - with delete_object, never with RBW. | - | 219 |
| `build_to_b4` | kind, path, preclean=False | (no docstring) | - | 274 |
| `site_table` | tag | The six wire_checked records as '_v1' itself recorded them, per site. | - | 299 |
| `census_at` | target, tag | (no docstring) | - | 312 |
| `main` |  | (no docstring) | - | 321 |

### tools/bench/diag_fstunnel_rbwvictims.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_fstunnel_wireterms_panel.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `must` | label, ok, detail='' | (no docstring) | - | 103 |
| `note` | label, value | (no docstring) | - | 109 |
| `md5` | p | (no docstring) | - | 113 |
| `snapshot` | tag | (no docstring) | - | 124 |
| `handles` | tag | (no docstring) | - | 132 |
| `StopAtB4` | (class) | (no docstring) | - | 148 |
| `build_to_b4` | kind, path, census=False | (no docstring) | - | 184 |
| `check_repro` | tag, path | (no docstring) | - | 206 |
| `wire_source_owner` | target, wire_uid, n=8 | COPIED from diag_fstunnel_wirebroken.py:186-208 (itself build_opconnectfromwire_v0.py:423-447). READ-ONLY. | - | 223 |
| `connect_from_wire` | target, wire_uid, term_index, sink_diag, sink_node, sink_term, labels | COPIED from diag_fstunnel_wirebroken.py:211-248, unchanged. | - | 248 |
| `term_index_of` | target, node_uid, term_name, want_source=False | (no docstring) | - | 288 |
| `read_broken` | target, wire_uid, sinks, labels | COPIED from diag_fstunnel_wirebroken.py:260-288. 'Wire.Is Broken?' 6371004 on ONE wire through | - | 297 |
| `uid_classes` | target | {uid: [class, ...]} from report_all per candidate class - the most specific class is the non-'Node' one. | - | 323 |
| `term_map` | target | {(node_uid, term_name, term_index): wire_uid} for every terminal of every diagram-0 node, from the | - | 335 |
| `ends_of` | tmap, wire_uid | (no docstring) | - | 347 |
| `role_of` | uid | (no docstring) | - | 354 |
| `describe_wire` | target, wire_uid, tmap, idx, ucls, tag | (no docstring) | - | 358 |
| `grep_tokens` | tokens | (no docstring) | - | 383 |
| `main` |  | (no docstring) | - | 407 |

### tools/bench/diag_movein_p1_break.py

shared file in the bench folder (move to tools/ later); imported by 3 file(s): `tools/bench/c52r3_astcheck.py`, `tools/bench/diag_donor_census.py`, `tools/bench/diag_movein_set.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | name, ok, detail='' | (no docstring) | - | 71 |
| `fact` | line | (no docstring) | - | 78 |
| `read_term` | vi, labels, target, wire_uid, idx | build_opwiresource_v5.read_terminal() with ONE change: 'vi path' is a parameter, not the main VI | - | 83 |
| `main` |  | (no docstring) | - | 115 |

### tools/bench/diag_movein_set.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/c52r3_astcheck.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `Stop` | (class) | (no docstring) | - | 113 |
| `gate` | name, ok, detail='', fatal=True | (no docstring) | - | 117 |
| `fact` | line | (no docstring) | - | 127 |
| `probe` | tag, path | (no docstring) | - | 132 |
| `dump` |  | (no docstring) | - | 139 |
| `terms_by_uid` | tag, target, uid | Terminal-by-terminal reading of ONE node, addressed by uid and re-resolved at the call site (34(h)): | - | 146 |
| `wire_side` | tag, target, wire_uid, ws_vi, ws_labels | The WIRE's own Terms[] (OpWireSource_v5): per terminal Is Source?, reciprocal wire, owner class/uid. | - | 183 |
| `census` | tag, target | (no docstring) | - | 199 |
| `wire_present` | target, wire_uid | (no docstring) | - | 206 |
| `main` |  | (no docstring) | - | 210 |

### tools/bench/diag_queue_donor.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/c52_astcheck.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `Stop` | (class) | (no docstring) | - | 144 |
| `gate` | name, ok, detail='', fatal=False | (no docstring) | - | 148 |
| `fact` | line | (no docstring) | - | 158 |
| `probe` | tag, path | (no docstring) | - | 163 |
| `dump` |  | (no docstring) | - | 170 |
| `labels_of` | target, diagram_index | (no docstring) | - | 177 |
| `attempt` | shape, target, src_cls, src_index, src_name, d686, why, extra=None | ONE 'queue_node('obtain')' attempt. Records the verbatim op error, the new Function uids and the labels | - | 185 |
| `main` |  | (no docstring) | - | 211 |

### tools/bench/diag_queue_donor2.py

shared file in the bench folder (move to tools/ later); imported by 3 file(s): `tools/bench/c52r2_astcheck.py`, `tools/bench/diag_qdonor2_ia.py`, `tools/bench/diag_qdonor2_stage.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `Stop` | (class) | (no docstring) | - | 149 |
| `gate` | name, ok, detail='', fatal=False | (no docstring) | - | 153 |
| `fact` | line | (no docstring) | - | 163 |
| `probe` | tag, path | (no docstring) | - | 168 |
| `dump` |  | (no docstring) | - | 175 |
| `safe` | fn, *a, **kw | Run a measurement call and return (value, error-string) - a refusal is a reading, never a crash. | - | 182 |
| `owner` | target, uid | (no docstring) | - | 190 |
| `walk_rows` | target, diagram_index, limit=200 | [{uid, node_index, label, class_guess, in_bare, out_named}] for one diagram - the BUILT census. | - | 195 |
| `const_on_term` | target, cls_name, cls_idx, node_i, term_i, labels, value=None | 'build_opcreateconstonterm_v0.create_const_on_term' VERBATIM except that the container CLASS is an argument | - | 211 |
| `q_attempt` | shape, target, src_cls, src_index, src_name, d686, why, extra=None | (no docstring) | - | 247 |
| `wire_driver` | target, wire_uid, max_terms=6 | Every terminal of one wire through OpWireSource_v5 (UID-addressed), returning the SOURCE rows. | - | 265 |
| `dependency_of_node` | target, diagram_index, uid, label | Every INPUT wire of one node, traced to its driving object's owner - 35(a)'s actual property. | - | 286 |
| `main` |  | (no docstring) | - | 327 |

### tools/bench/diag_replay_gbtest.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_replay_test77.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `harness` | s, tag, vut | (no docstring) | - | 24 |
| `call` | s, H, lab, tag, b=None | (no docstring) | - | 45 |
| `body` | s | (no docstring) | - | 63 |
| `St` | (class) | (no docstring) | - | 92 |
| `St.close` | expect_files=None | (no docstring) | - | 93 |
| `St.summary` |  | (no docstring) | - | 96 |

### tools/bench/diag_replay_lib.py

shared file in the bench folder (move to tools/ later); imported by 9 file(s): `tools/bench/diag_c110f_dispgraph.py`, `tools/bench/diag_replay_defaults.py`, `tools/bench/diag_replay_gbtest.py`, `tools/bench/diag_replay_graph77.py`, `tools/bench/diag_replay_standins.py`, `tools/bench/diag_replay_test77.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `new1` | t, cls, before | the ONE uid of class 'cls' on 't' that is not in 'before' (raises on 0 or >1; DRY: 0) | - | 41 |
| `new_label` | t, before, indicator | (no docstring) | - | 51 |
| `copy_to` | s, cls, uid, dest_diag_uid, pos, tag | copy_top + (dest_diag_uid) move_in into that diagram + junk purge = stagekit.copy_in:779 with DRY-safe lookups | - | 60 |
| `pins` |  | (no docstring) | - | 69 |
| `walk` | t, d=0 | (no docstring) | - | 75 |
| `term` | rows, name, source | (no docstring) | - | 86 |
| `tname` | rows, pred, source | the one terminal name satisfying pred(name) with the given direction (raises on 0 or >1) | - | 90 |
| `fidx` | t, cls, uid | (no docstring) | - | 106 |
| `diag_index` | t, uid | (no docstring) | - | 110 |
| `donor_class` | uid | (no docstring) | - | 114 |
| `copy_top` | s, cls, uid, tag | stagekit.copy_in:779 minus move_in: OpMoveByIndex_v0 duplicate=True with the UID guard; the copy stays top level. | - | 123 |
| `str_array_ctl` | s, t, tag | (no docstring) | - | 137 |
| `pwire` | t, label | the wire uid on panel object 'label' (panel_wiring; raises if absent; DRY: 0) | - | 149 |
| `pidx` | t, label | (no docstring) | - | 159 |
| `pane_dirs` | t | {slot: (label, is_indicator)} over the connector pane (label + direction; K3 of 76-4) | - | 163 |
| `edges` | live, remap | (no docstring) | - | 169 |
| `census` | t | (no docstring) | - | 179 |
| `tail` | s, fxl=None, bad=() | once per run, just before the RESULT line: Moving-Objects pair restored and proven (stagekit.fixtures_check), | - | 187 |
| `frame_paths` |  | (no docstring) | - | 206 |

### tools/bench/diag_s2_scaffold.py

shared file in the bench folder (move to tools/ later); imported by 75 file(s): `tools/bench/c52r3_astcheck.py`, `tools/bench/c53_astcheck.py`, `tools/bench/diag_c60_castseed_probe.py`, `tools/bench/diag_c60_n4_localbinding.py`, `tools/bench/diag_c61_localdir.py`, `tools/bench/diag_c61_localdir_write.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `Stop` | (class) | (no docstring) | - | 109 |
| `gate` | name, ok, detail='', fatal=True | (no docstring) | - | 113 |
| `fact` | line | (no docstring) | - | 123 |
| `md5` | p | (no docstring) | - | 128 |
| `version_bytes` | path | (no docstring) | - | 136 |
| `file_facts` | tag, path | (no docstring) | - | 143 |
| `fresh` | tag | A FRESH LabVIEW instance (standing restart authority) — stage_d1_s2.py:575-586. | - | 156 |
| `Preload` | (class) | stage_d1_s2.py:589-613 verbatim: the ORIGINAL resident READ-ONLY for the duration of a phase. No panel on | - | 168 |
| `dump` |  | (no docstring) | - | 192 |
| `census_686` | target | Every node of Diagram #686 with its OUTPUT terminal names — 'walk' is the BUILT census. | - | 199 |
| `candidates_from` | rows, target | Scalar-shaped named SOURCE terminals, PREFERRED first, then census order (the brief pre-decides this). | - | 219 |
| `try_candidate` | c, target, loop_uid, body_uid, d686 | ONE attempt: OpCreateEqual_v0 (both operands = this ONE terminal) then OpStopFromNode_v0. | - | 261 |
| `read_state` | tag, target | (no docstring) | - | 344 |
| `try_save` | tag, target | (no docstring) | - | 352 |
| `main` |  | (no docstring) | - | 367 |

### tools/bench/diag_s3b_l0_localname_v2.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_c147_b1_4_run.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `Stop` | (class) | (no docstring) | - | 252 |
| `gate` | name, ok, detail='', fatal=False | (no docstring) | - | 256 |
| `fact` | line | (no docstring) | - | 265 |
| `probe` | tag, path | (no docstring) | - | 270 |
| `dump` |  | (no docstring) | - | 277 |
| `read_exec_state` | rec, tag, target | (no docstring) | - | 285 |
| `count_of` | target, cls | (no docstring) | - | 295 |
| `uid_set` | target, cls | (no docstring) | - | 302 |
| `report_uids` | target, cls | report_all order (the order every delete_object index in this fleet is resolved against). | - | 309 |
| `terms_table` | rows | (no docstring) | - | 317 |
| `node_index_of` | target, diagram_index, uid | The 34(h)-safe Nodes[] index: bounded scan with a uid echo. Returns (index, rows). | - | 322 |
| `terms_of` | target, diagram_index, uid | (no docstring) | - | 336 |
| `full_node_dump` | target, diagram_index, tag, max_nodes=SCAN_LIMIT, quiet=False | Every node on one diagram with its FULL terminal table, read off the machine. Read-only. | - | 341 |
| `owner_read` | rec, tag, uid, target | Owner of 'uid', accepting BOTH 'Diagram' and 'TopLevelDiagram' wherever it is compared. | - | 368 |
| `close_quietly` | target | (no docstring) | - | 392 |
| `fp_pairs` | target, max_n=200 | (no docstring) | - | 399 |
| `delete_wire_by_uid` | rec, tag, target, wire_uid | The ONLY form there is: resolve the uid to its report_all index, delete, and assert the gone-set. | - | 407 |
| `phase_s1` |  | Read-only on the freshly made copy. NOTHING is edited in this phase. | - | 439 |
| `phase_s2` | S | (no docstring) | - | 582 |
| `local_name` | target, index, tag='' | The READER's Python side: Traverse 'Local' by 'index' on 'target' -> Local.Control Name 6355400. | - | 928 |
| `create_local` | target, label, panel_index, tag='' | material #1's wrapper (tools/bench/diag_s3b_l0_localname.py:695-743), unchanged in substance: drive | - | 964 |
| `phase_s345` |  | (no docstring) | - | 1016 |
| `main` |  | (no docstring) | - | 1213 |

### tools/bench/diag_tunnelsource_onehop.py

shared file in the bench folder (move to tools/ later); imported by 5 file(s): `tools/bench/diag_d0_trace_path.py`, `tools/bench/diag_fstunnel_wire_semantics.py`, `tools/recipes/build_opfstunnelterm_v0.py`, `tools/recipes/build_opfstunnelterm_v1.py`, `tools/recipes/build_opfstunnelterm_v2.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | name, ok, detail='' | (no docstring) | - | 70 |
| `fact` | line | (no docstring) | - | 77 |
| `md5` | p | (no docstring) | - | 82 |
| `labels` |  | (no docstring) | - | 94 |
| `read_terminal` | target, wire_uid, idx | One terminal of one wire: (is_source, owner class, owner uid, reciprocal wire). Poison every readout | - | 102 |
| `wire_terminals` | target, wire_uid, maxn=8 | Every terminal on 'wire_uid', stopping at the end of Wire.Terminals[]. | - | 139 |
| `wire_source` | target, wire_uid | The ONE terminal on 'wire_uid' that is a source and points back at it; None when there is not exactly one. | - | 153 |
| `offline` |  | (no docstring) | - | 169 |
| `locate` | target, uid | (diagram index, node index, rows) for a node uid - read from main_vi_nodeterms.json, not from LabVIEW. | - | 185 |
| `tunnel_map` | target | (no docstring) | - | 194 |
| `resolve` | target, tunnel_uid, outer_wire, max_hops=6 | §11r: one hop at a time from Python. Returns the resolution dict. | - | 199 |
| `main` |  | (no docstring) | - | 238 |

### tools/bench/diag_vigraph_check.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/vigraph_g8_edges_74.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | label, ok, detail='' | (no docstring) | - | 37 |
| `fact` | line | (no docstring) | - | 43 |
| `newest` | pattern | The newest dated census (was: today's date only, which broke the check on every later day). | - | 47 |
| `g10_equal_top` |  | G10 (cycle 68): two LEFT registers at EQUAL TOP in one loop body - the M4b shape (#23796 / #23880 both at | - | 52 |
| `g12_diag_term` | rec_s1, A | G12 (card 74-2, Pre-decided 176(c)): a Diagram-owned 'Terminal' SOURCE (loop 'i') is its own computation node. | - | 76 |
| `load` | key | (no docstring) | - | 106 |
| `dump` | name, payload | (no docstring) | - | 141 |
| `main` |  | (no docstring) | - | 150 |

### tools/bench/drive_legguard.py

shared file in the bench folder (move to tools/ later); imported by 6 file(s): `tools/bench/diag_c104_abba.py`, `tools/bench/diag_c106b_live.py`, `tools/bench/drive_m8_replay_110.py`, `tools/bench/drive_original_copy_v5.py`, `tools/bench/selftest_c108e_tools.py`, `tools/bench/selftest_leg_guard.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `test_stop_at_l2` |  | (no docstring) | - | 19 |
| `visa_precheck` | names=PRECHECK_NAMES, dry=False, dll=None, log=print | -> {"ok", "bypassed", "dry", "rm_status", "trials": [{name, status, hex, text, close, ms}]}. Never raises. | - | 23 |
| `lv_running` |  | (no docstring) | - | 45 |
| `kill_labview` | wait_s=20.0 | direct kill (standing restart permission); -> (gone, secs). | - | 49 |
| `lv_windows` |  | -> [(hwnd, title, class, visible, enabled)] of labview.exe's top-level windows. | - | 71 |
| `modal_of` | snap, baseline | the first NEW visible enabled dialog-class window while another visible LabVIEW window is disabled, else None. | - | 84 |
| `shotwin` | h, png | (no docstring) | - | 90 |
| `ocr_text` | png | (no docstring) | - | 100 |
| `DialogWatch` | (class) | start() BEFORE Run (baseline = windows visible then); stop() after L2. .fired / .record carry the result. | - | 112 |
| `DialogWatch.run` |  | (no docstring) | - | 123 |
| `DialogWatch.stop` | timeout=60.0 | (no docstring) | - | 152 |
| `stop_reason` | arm, row | PD217(g)/PD218(d): the rule that ends the whole leg loop; None = continue. | - | 156 |
| `refusal_verdict` | gates, rows, loop_stop | card 108-5 (PD222(d); archive/peer/2026-09-27-c108a-disp107-visa-refusal.md:90, 108-1 open 2): -> (status, n_pass, | - | 164 |
| `leg_loop` | order, run_leg, log=print, max_legs=None | order = [(arm, src, _, npick)]; run_leg(slot, arm, src, attempt, npick) -> row. Returns (finals, stop). | - | 191 |

### tools/bench/drive_m8.py

shared file in the bench folder (move to tools/ later); imported by 14 file(s): `tools/bench/diag_c104_leg.py`, `tools/bench/diag_c104f_leg.py`, `tools/bench/diag_c105_leg.py`, `tools/bench/diag_c105b_leg.py`, `tools/bench/diag_c105c_leg.py`, `tools/bench/diag_c89_profiler_leg.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `md5` | p | (no docstring) | - | 43 |
| `tra_rows` | p, ncol=12 | (no docstring) | - | 46 |
| `lv_running` |  | (no docstring) | - | 51 |
| `table` | s3=False | (no docstring) | - | 55 |
| `main` |  | (no docstring) | - | 62 |

### tools/bench/drive_original_copy_v2.py

shared file in the bench folder (move to tools/ later); imported by 4 file(s): `tools/bench/d0_clickprobe.py`, `tools/bench/diag_d0_pickloop_liveness.py`, `tools/bench/drive_original_copy_v3.py`, `tools/bench/drive_original_copy_v4.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `log` | msg | (no docstring) | - | 161 |
| `rec` | step, method, ok, detail | (no docstring) | - | 165 |
| `PollCom` | (class) | (no docstring) | - | 178 |
| `PollCom.run` |  | (no docstring) | - | 188 |
| `PollCom.call` | kind, *args, timeout=COM_T | (no docstring) | - | 242 |
| `RunThread` | (class) | (no docstring) | - | 265 |
| `RunThread.run` |  | (no docstring) | - | 272 |
| `gui` | *args, timeout=60 | (no docstring) | - | 297 |
| `shot` | name | (no docstring) | - | 307 |
| `windows` |  | (no docstring) | - | 314 |
| `win_present` | sub | (no docstring) | - | 318 |
| `win_rect` | sub | (no docstring) | - | 322 |
| `dialogs` |  | (no docstring) | - | 328 |
| `blocked` |  | (no docstring) | - | 332 |
| `click` | x, y, why | (no docstring) | - | 336 |
| `keys` | sendkeys, why | (no docstring) | - | 345 |
| `focus` | sub | (no docstring) | - | 354 |
| `inside` | rect, xy, margin=25 | (no docstring) | - | 358 |
| `md5` | path | (no docstring) | - | 365 |
| `state` |  | (no docstring) | - | 373 |
| `getv` | name, timeout=COM_T | (no docstring) | - | 380 |
| `snapshot` |  | (no docstring) | - | 387 |
| `listdir_stats` | d | (n_files, total_bytes, {ext: (n, bytes)}, [non-tiff names]) | - | 391 |
| `delete_tiffs` | d | (no docstring) | - | 412 |
| `reset_controls` |  | (no docstring) | - | 431 |
| `stop_via_vi_control` | tag | P10. VI Server FIRST, re-arming every 2 s so a latch cannot swallow the write. | - | 443 |
| `bandpass_round` | tag, expect=3 | P6. Answer every 'choose bandpass' panel, one Yes click each, verify it closes. | - | 472 |
| `answer_save_dialog` | tag, base_path | P7. Type an ABSOLUTE path under our run folder. Keyboard first (the file-name edit holds | - | 522 |
| `cycle` | tag, base_path, first | One complete run: Run -> picks -> done -> bandpass -> save -> loop -> stop. | - | 563 |
| `main` |  | (no docstring) | - | 710 |
| `cleanup` |  | (no docstring) | - | 781 |
| `report` |  | (no docstring) | - | 839 |

### tools/bench/drive_original_copy_v4.py

shared file in the bench folder (move to tools/ later); imported by 3 file(s): `tools/bench/diag_d0_pickloop_liveness.py`, `tools/bench/drive_original_copy_v5.py`, `tools/bench/tmx_fallthrough_probe.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `motor_gate` | why | Run 'py tools/motor_gate.py --session start' and parse its readback. Returns (rc, text). | - | 205 |
| `parse_motor` | text | Pull the machine-readable lines out of the gate's output, without importing its parsers on a | - | 221 |
| `prelimits_from` | text | The sender's NORMALISED pre-write limit line, read with an ANCHORED whole-line regex. | - | 259 |
| `tmx_from` | text | What the controller HELD when the gate arrived, i.e. the post-LabVIEW-run TMX?.  Returns | - | 280 |
| `selftest_tmx` |  | 'py tools/bench/drive_original_copy_v4.py --selftest' - pure-function, no COM, no motor, no | - | 319 |
| `clickprobe` | title, x, y, why | (no docstring) | - | 447 |
| `delivered` | j | (no docstring) | - | 467 |
| `gated_click_hwnd` | title, x, y, why, max_attempts=2 | THE TOKEN IS THE HWND, NOT THE TITLE (v3's finding). A second attempt is issued ONLY if the | - | 477 |
| `derive_geometry` |  | Returns (ok, detail). Fills GEO with image_rect / picks / done_xy for THIS panel window. | - | 518 |
| `bandpass_yes_now` |  | (no docstring) | - | 543 |
| `control_labels` |  | The exact label bytes of the 60 front-panel CONTROLS of THIS copy, from the read-only | - | 553 |
| `record_panel` | tag | READ every control. NEVER write. Returns (n_read, n_err, dict). | - | 566 |
| `stop_single_write` | tag | The peer's discriminating test verbatim (archive/peer/2026-09-17-d0v3-stop-heuristic.md:32): | - | 595 |
| `stop_rearmed` | tag | Only reached if the single-write test did not idle the VI. Still VI SERVER ONLY. | - | 618 |
| `stop_measured` | tag | Returns (stopped_by_vi_server, mechanism, detail). Abort is NEVER used here - cleanup owns | - | 635 |
| `leg` | tag, n, base_path, cal_wait | n = the gate-number base, so leg 1 numbers 10.. and leg 2 numbers 20.. . | - | 659 |
| `main` |  | (no docstring) | - | 853 |
| `cleanup` |  | (no docstring) | - | 953 |
| `report` |  | (no docstring) | - | 1040 |

### tools/bench/drive_original_copy_v5.py

shared file in the bench folder (move to tools/ later); imported by 15 file(s): `tools/bench/diag_c104_leg.py`, `tools/bench/diag_c104f_leg.py`, `tools/bench/diag_c105_leg.py`, `tools/bench/diag_c105b_leg.py`, `tools/bench/diag_c105c_leg.py`, `tools/bench/diag_c89_profiler_leg.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `capture` | name | (no docstring) | - | 177 |
| `panel_rect` |  | (no docstring) | - | 186 |
| `probe_click` | title, x, y, why | clickprobe (the delivery-proven path) + the delivery verdict.  Returns (delivered, j). | - | 190 |
| `locate_done` | png, prect, tag | Returns (centre, detail, crop_path).  Nothing is inherited: the search rect is the panel | - | 199 |
| `locate_bandpass_yes` | png, brect | (no docstring) | - | 228 |
| `stop_with_fallback` | tag | Returns (stopped, mechanism, latency_s, detail). | - | 242 |
| `leg` | tag, n, base_path, cal_wait | (no docstring) | - | 275 |
| `main` |  | (no docstring) | - | 530 |
| `labview_running` |  | (no docstring) | - | 634 |
| `cleanup` |  | (no docstring) | - | 644 |
| `report` |  | (no docstring) | - | 735 |

### tools/bench/fntest_lib.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/bench/fntest_g1.py`, `tools/bench/fntest_g2.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `FT` | (class) | (no docstring) | - | 38 |
| `FT.case` | fns, name, fn, check=None | Run one POSITIVE case for the verb-level functions 'fns'; check(res) -> (ok, measured dict). | - | 60 |
| `FT.negcase` | fns, name, fn, expect | A NEGATIVE case (the plan's neg-double): expect(err, ops) -> (ok, measured). gscript outcomes inside it are | - | 77 |
| `FT.harness_err` | name, e | (no docstring) | - | 94 |
| `FT.verdicts` |  | (no docstring) | - | 99 |
| `FT.commit` | log, labview | (no docstring) | - | 124 |
| `Bed` | (class) | card chat-F3b: the live graph of a fntest scratch through stagexec.LVBackend, read the way the Executor reads it | - | 150 |
| `Bed.read` |  | (no docstring) | - | 159 |
| `Bed.ts` | owner, name=None, src=None, cls=None | THE one terminal uid of node #owner with that name / direction / term class, else None. | - | 177 |
| `Bed.ct` | label | The ControlTerminal (front-panel terminal on a diagram) labelled 'label': its own uid (== term uid), else None. | - | 187 |
| `Bed.wire_of` | term_uid | (no docstring) | - | 195 |
| `Bed.cls_of` | uid | (no docstring) | - | 199 |
| `Bed.wired_after` | *terms | (ok, measured) after a fresh read: every terminal in 'terms' carries a wire. | - | 202 |
| `Kit` | (class) | card chat-F3b: the case builders of a fntest runner, every verb called with the stagexec Executor's call shapes | - | 209 |
| `Kit.need` | name, *v | (no docstring) | - | 218 |
| `Kit.cnt` | c | (no docstring) | - | 221 |
| `Kit.mk` | fns, name, route, a, args, cls=None, uid=True | (no docstring) | - | 224 |
| `Kit.prim` | name, dg, donor, p, pos, cls_=None | (no docstring) | - | 239 |
| `Kit.con` | fns, name, src, dst, op=None | (no docstring) | - | 244 |
| `Kit.add_sr` | name, loop, parent | The Executor's add_sr sequence (stagexec.py:2228-2316): snap the loop's Terminals[] (on its parent diagram), add | - | 249 |
| `Kit.r0` |  | R0: count / report_all / uids / exec_state agree on the EMPTY scratch (one Diagram). Returns that Diagram's uid. | - | 272 |
| `Kit.r1` |  | R1: the node / terminal / panel / wire reads on the built bed (Diagram[0] and [1], node 0). | - | 282 |
| `owners_of` | objs, resolve=None, cache=None | str(diagram uid) -> [owner class, owner uid] for the Diagrams of a read_live objs list (the Executor's PD185 owners | - | 293 |
| `term` | real, owner, name=None, src=None, cls=None | THE one terminal row of node #owner with that name / direction / term class (harness lookup; raises if not one). | - | 324 |

### tools/bench/ground_bench.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/record_claude.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `load_gt` | ids=None | (no docstring) | - | 45 |
| `parse_xy` | text | (no docstring) | - | 50 |
| `image_size` | path | (no docstring) | - | 55 |
| `ask_gpt` | row | (no docstring) | - | 61 |
| `ask_uitars` | row | (no docstring) | - | 79 |
| `score` | row, ans | (no docstring) | - | 99 |
| `append` | rec | (no docstring) | - | 109 |
| `cmd_run` | args | (no docstring) | - | 114 |
| `cmd_record` | args | (no docstring) | - | 129 |
| `cmd_report` | args | (no docstring) | - | 142 |

### tools/bench/imaqdx_limits.py

shared file in the bench folder (move to tools/ later); imported by 14 file(s): `tools/bench/camera_contract.py`, `tools/bench/diag_c104_abba.py`, `tools/bench/diag_c91_step4.py`, `tools/bench/diag_c92_m2.py`, `tools/bench/diag_c92c_abba.py`, `tools/bench/diag_c93b_abba.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `CameraInformation` | (class) | (no docstring) | - | 31 |
| `get` | sess, name, t=I64 | (no docstring) | - | 39 |
| `limits` | sess, name, t=I64 | (minimum, maximum, increment) - the range the camera will actually accept right now. | - | 45 |
| `report` | sess, tag | (no docstring) | - | 55 |
| `main` |  | (no docstring) | - | 71 |

### tools/bench/jev_device_value_labels.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/selftest_jev_device_value.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `score` | rows, dk | (no docstring) | - | 13 |
| `measure` | path, n=None, ask=None, out_path=None | (no docstring) | - | 21 |

### tools/bench/jev_discharge_trial.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/bench/jev_priorart_trial.py`, `tools/bench/jev_run_all.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `build_rows` |  | (no docstring) | - | 164 |
| `acc` | rows, thr | (no docstring) | - | 185 |
| `report` | rows, title | (no docstring) | - | 192 |
| `main` |  | (no docstring) | - | 254 |

### tools/bench/jev_gate.py

shared file in the bench folder (move to tools/ later); imported by 16 file(s): `tools/bench/diag_c104_ladder.py`, `tools/bench/jev_discharge_trial.py`, `tools/bench/jev_gatecheck_c68.py`, `tools/bench/jev_ladder_c89.py`, `tools/bench/jev_ladder_c89b.py`, `tools/bench/jev_ladder_c90.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `summarise_review` | path, qchars=2500 | What the gate hands Jev about ONE archived peer exchange: its identity line, the first 'qchars' of the | - | 61 |
| `review_meta` | path | (agent, role, outcome) lowercased, '' where absent. | - | 82 |
| `recent_adversary_reviews` | n=N_RECENT_REVIEWS, before=None | The 'n' newest archived exchanges that guard_peer would ACCEPT as a failed-prediction review, newest first. | - | 93 |
| `covers_failure` | failure_summary, review_summary, purpose='guard-peer-discharge', n=None | Probability that 'review_summary' already covers 'failure_summary'. (p, None) or (None, error). | - | 168 |
| `answers_step` | step_sentence, review_summary, purpose='priorart-duplicate' | Probability that 'review_summary' already answers 'step_sentence'. (p, None) or (None, error). | - | 183 |
| `gate_log` | line | One line to tools/bench/jev_gate.log. Never raises: a gate must not die on a full disk. | - | 197 |
| `cite_in_review` | review_path, log_name, p, ts=None | Write the discharge citation into the review file under '## What was done with it', so the audit and | - | 206 |
| `jev_discharge` | log_path, failure_text, n=N_RECENT_REVIEWS, before=None, write=True | THE GATE CALL (guard_peer.py). Returns (allow, reason_line). | - | 231 |
| `ladder_classify` | failure_summary, gate_rows='', recent='', purpose='guard-peer-ladder', n=None | (class, mean probability, spread) for ONE failing run. (None, None, None) when there is no answer. | - | 342 |
| `ladder_allowed_line` | log_name, cls, p, ts | One JSON line per ladder ALLOW, so tools/audit_cycle.py can count builds that ran with no new review. | - | 359 |
| `cited_review` | discharge_line | archive/peer/<name>.md named by a JEV-DISCHARGE line (fresh or cached), or None. | - | 379 |
| `next_action` | cls, allowed, discharge_line=None | The NEXT-ACTION text for one gate outcome. 'allowed' is the gate's own decision, never the class alone: | - | 385 |
| `with_next` | line, action | (no docstring) | - | 395 |
| `ladder_cache_path` |  | (no docstring) | - | 408 |
| `ladder_cache_get` | key, md5 | The stored verdict for (key, md5), newest wins; None when absent or unreadable. | - | 432 |
| `ladder_cache_put` | rec | (no docstring) | - | 449 |
| `newest_ladder_line` | log_name | The newest JEV-LADDER line in GATE_LOG for this log basename (tail only), or None. | - | 457 |
| `ladder_after_discharge` | log_path, discharge_line, write=True | guard_peer calls this when the ladder did NOT act and the OLD-PATH discharge then allowed: the newest | - | 474 |
| `jev_ladder` | log_path, failure_text, n=N_RECENT_REVIEWS, before=None, write=True, gate_rows=None | THE LADDER CALL (tools/hooks/guard_peer.py), run BEFORE the ordinary discharge. | - | 489 |
| `jev_priorart_dup` | step_sentence, n=N_RECENT_REVIEWS, write=True | ADVISORY ONLY (docs/jev-integration-plan.md row #6 'as in A, but do not block'). Returns the advisory | - | 574 |

### tools/bench/jev_gaterow_q.py

shared file in the bench folder (move to tools/ later); imported by 3 file(s): `tools/bench/jev_wave2a_trials.py`, `tools/bench/jev_wave4_selftest.py`, `tools/jev_gaterow.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `run_segment` | logpath, run_index=-1 | (command, segment text, how it ended) for one BGRUN run of a log, or (None, None, None). | - | 65 |
| `fail_rows` | logpath, run_index=-1, max_rows=None | Every FAIL row of one run, as [{'line': n, 'label': 'D7', 'row': ..., 'state': {...}}, ...]. | - | 86 |

### tools/bench/jev_next_q.py

shared file in the bench folder (move to tools/ later); imported by 3 file(s): `tools/bench/jev_next_trial.py`, `tools/bench/selftest_next_gate_jev.py`, `tools/hooks/guard_bash.py`

(no public function)

### tools/bench/jev_priorart_trial.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/jev_run_all.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `main` |  | (no docstring) | - | 139 |

### tools/bench/jev_triage_q.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/bench/jev_triage_trial.py`, `tools/jev_triage.py`

(no public function)

### tools/bench/jev_wave2a_trials.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/jev_ladder_remeasure.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | ok, label, detail='' | (no docstring) | - | 64 |
| `ledger_lines` |  | (no docstring) | - | 75 |
| `out_of_time` | why | (no docstring) | - | 83 |
| `cell_a` |  | (no docstring) | - | 91 |
| `cell_b` |  | (no docstring) | - | 124 |
| `resolve_trigger` | review_path | (log basename, run index, review epoch) for one archived review, or (None, None, None). | - | 191 |
| `cell_c` |  | (no docstring) | - | 226 |
| `main` |  | (no docstring) | - | 317 |

### tools/bench/k_contract_79.py

shared file in the bench folder (move to tools/ later); imported by 36 file(s): `tools/bench/diag_c107b_bedgraph.py`, `tools/bench/diag_c108b_graph.py`, `tools/bench/diag_c110_bedgraph.py`, `tools/bench/diag_c111b_b1graph.py`, `tools/bench/diag_c112c_fixture.py`, `tools/bench/diag_c113a_b2agraph.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `mloops` | s, path | (no docstring) | - | 33 |
| `main` | s | (no docstring) | - | 48 |

### tools/bench/launch_p3b2_c135.py

shared file in the bench folder (move to tools/ later); imported by 4 file(s): `tools/bench/launch_p3b2_resume_c135.py`, `tools/bench/launch_p3b2_resume_c135_compare.py`, `tools/bench/selftest_c134_p1.py`, `tools/bench/selftest_c135_2_compare.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `recipe_cmd` | r | (no docstring) | - | 52 |
| `graph_key` | g | (no docstring) | - | 57 |
| `compare` | new, ref | (equal, diff) - diff lists per field the first differing items (never absorbed: rule 1a, PD288(e)). | - | 69 |
| `Live` | (class) | (no docstring) | - | 85 |
| `Live.child` | step, extra=None | (no docstring) | - | 88 |
| `Live.labview_gone` | kill=True | (no docstring) | - | 99 |
| `Live.write` | path, data | (no docstring) | - | 105 |
| `Live.restore_pb` |  | (no docstring) | - | 108 |
| `Dry` | (class) | Nothing spawned, nothing killed, nothing written: each child returns the branch's fixture. | - | 116 |
| `Dry.child` | step, extra=None | (no docstring) | - | 123 |
| `Dry.labview_gone` | kill=True | (no docstring) | - | 146 |
| `Dry.write` | path, data | (no docstring) | - | 150 |
| `Dry.restore_pb` |  | (no docstring) | - | 153 |
| `run` | X, branch='equal' | (no docstring) | - | 159 |

### tools/bench/launch_p3b2_c135_graph.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/selftest_c134_p1.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `patched_source` |  | (no docstring) | - | 23 |

### tools/bench/launch_p3b2_resume_c135_compare.py

shared file in the bench folder (move to tools/ later); imported by 3 file(s): `tools/bench/diag_c135_2_compare.py`, `tools/bench/launch_p3b2_resume_c135.py`, `tools/bench/selftest_c135_2_compare.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `reannotate` | g | (copy of g with fs_measured.borders = current annotation, changes {border uid: {added, removed, changed, presence}}). | - | 20 |
| `annotation_only` | ch | (no docstring) | - | 42 |
| `compare` | new, ref | (equal, diff, changes) - C135.compare on the re-annotated pair; a non-annotation re-annotation change on either side is | - | 47 |

### tools/bench/m8_dry.py

shared file in the bench folder (move to tools/ later); imported by 5 file(s): `tools/bench/diag_c104_leg.py`, `tools/bench/diag_c93b_leg.py`, `tools/bench/diag_c94_leg.py`, `tools/bench/diag_c96_leg.py`, `tools/bench/selftest_leg_guard.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `FakeCom` | (class) | (no docstring) | - | 8 |
| `FakeCom.call` | kind, *args, timeout=None | (no docstring) | - | 9 |
| `stub` | v5, d4, d0 | (no docstring) | - | 13 |

### tools/bench/m8b_replay_compare.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/drive_m8_replay_110.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `tra` | d | (no docstring) | - | 15 |
| `cal` | d | (no docstring) | - | 26 |
| `main` | a1, a3, out | (no docstring) | - | 31 |

### tools/bench/opmodels_lib.py

shared file in the bench folder (move to tools/ later); imported by 3 file(s): `tools/bench/opmodels_check_move.py`, `tools/bench/opmodels_fit.py`, `tools/bench/opmodels_measure.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `edges` | terms | (no docstring) | - | 11 |
| `snapshot_stats` | terms, objs | (no docstring) | - | 25 |
| `diff` | before, after | before/after = (terms, objs). Returns a JSON-able dict. | - | 32 |
| `apply_move` | terms, node_uid | MOVE MODEL v0 (fitted on L7-1a, S3 -> D1_l7_1a, move of SubVI #376): returns predicted terms after | - | 79 |
| `apply_delete_object` | terms, node_uid | DELETE_OBJECT MODEL v0 (delete_object #7201, #27605; plus the setup of remove_bad_wires_1, delete #1628): the node and | - | 125 |
| `summary` | d | (no docstring) | - | 141 |

### tools/bench/prep_c143_3_elrule.py

shared file in the bench folder (move to tools/ later); imported by 11 file(s): `tools/bench/prep_c142_5_pred.py`, `tools/bench/prep_c143_3_pred.py`, `tools/bench/prep_c143_5_pred.py`, `tools/bench/prep_c143_6_pred.py`, `tools/bench/prep_c143_p1_pred.py`, `tools/bench/prep_c144_1_pred.py` ...

(no public function)

### tools/bench/s1_subvi_paths.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/recipes/stage_d1_s1.py`, `tools/recipes/stage_d1_s2.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | label, ok, detail='' | (no docstring) | - | 90 |
| `fact` | s | (no docstring) | - | 97 |
| `md5` | p | (no docstring) | - | 101 |
| `child` | tag, target | (no docstring) | - | 110 |
| `run_condition` | tag, target | (no docstring) | - | 183 |
| `llb_root` | path | Nearest ancestor DIRECTORY COMPONENT of 'path' whose name ends in .llb, or None. | - | 212 |
| `main` |  | (no docstring) | - | 224 |

### tools/bench/selftest_c153_poskey_convert.py

shared file in the bench folder (move to tools/ later); imported by 3 file(s): `tools/bench/diag_c153_a2_3_run.py`, `tools/bench/diag_c153_a2_4_run.py`, `tools/bench/diag_c153_a2_5_run.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `pos_table` | G | Alias of stagekit.pos_slot_table. | - | 24 |
| `name_free` | P, s | Alias of stagekit.pos_name_free. | - | 29 |
| `slots` | G, V, nodes | Alias of stagekit.pos_slots (argument order of the old copy). | - | 34 |
| `convert` | rows, SA, SB | Alias of stagekit.pos_convert. | - | 39 |
| `sinks` | conv | Sorted distinct sinks of converted rows. | - | 44 |
| `convert_open_rows` | plan_open_rows, old_rows, new_rows | Alias of stagekit.pos_convert_open_rows. | - | 49 |

### tools/bench/selftest_guard_peer_jev.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/jev_run_all.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | ok, label, detail='' | (no docstring) | - | 42 |
| `Stub` | (class) | Replace jev_gate.covers_failure with a constant, or with a raiser. | - | 97 |
| `main` |  | (no docstring) | - | 110 |
| `read` | p | (no docstring) | - | 356 |
| `run_main` | cmd, capture=False | Drive guard_peer.main() with a PreToolUse payload; optionally capture its stderr. | - | 374 |

### tools/bench/selftest_guard_peer_ladder.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/selftest_jev_ladder_action.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | ok, label, detail='' | (no docstring) | - | 80 |
| `LadderStub` | (class) | Replace jev_gate.ladder_classify with a constant verdict, or with a raiser. | - | 90 |
| `CoversStub` | (class) | Replace jev_gate.covers_failure with a constant probability. | - | 103 |
| `read` | p | (no docstring) | - | 114 |
| `run_main` | cmd, capture=False | (no docstring) | - | 132 |
| `main` |  | (no docstring) | - | 146 |

### tools/bench/selftest_stoprecord_supersession.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/selftest_stoprecord_table.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | name, ok, detail='' | (no docstring) | - | 63 |
| `first_line` | msg | (no docstring) | - | 69 |
| `fingerprint` | p | (no docstring) | - | 73 |
| `patched` |  | Is the loaded stop_record carrying the supersession rule? Read from the source, never assumed. | - | 112 |
| `run_case` | case, want_later, later_disposed, tag | Returns (allow, msg, records). Builds a fresh isolated store, an old RELEASED record at sha s1, edits the | - | 120 |
| `exempt_patched` |  | Is the loaded stop_record carrying the COMMAND-POSITION EXEMPTION (cycle 46)? Read, never assumed. | - | 190 |
| `run_exemption_case` |  | CASE 4 - the second half of the deadlock (cycle 46). A STANDING, UNDISPOSED record refuses everything that | - | 195 |
| `run_novel_case` |  | CASE 5 (cycle 72 firefighter). Old RELEASED record at s1; bytes edited to s2; a NOVEL review of s2 written | - | 246 |
| `main` |  | (no docstring) | - | 306 |

### tools/bench/selftest_t6_poskey.py

shared file in the bench folder (move to tools/ later); imported by 4 file(s): `tools/bench/diag_c153_a2_3_run.py`, `tools/bench/diag_c153_a2_5_run.py`, `tools/bench/selftest_c147_b1_2.py`, `tools/bench/selftest_t7_ring.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | label, ok, detail='' | (no docstring) | - | 40 |
| `fact` | s | (no docstring) | - | 45 |
| `load` | plan, rj, cmap | (no docstring) | - | 49 |
| `enrich` | B, SIM, RE5, ob, tb | Real rows in READ order with the fields the stored read dropped (module docstring). Returns (rows, unbound sim uids). | - | 68 |
| `order_diffs` | B, R | (no docstring) | - | 93 |
| `names_by_node` | rows, ob=None | {node (mapped through ob): [(class, direction, name), ...] in read order} - the FACT on created objects. | - | 101 |
| `main` |  | (no docstring) | - | 111 |
| `k141` | K | selftest_td_key_c141_3.py's 141-2 case (P4 s01 scratch: LabVIEW re-used deleted uids), rebuilt exactly as there (:40-62), re-asked | selftest_td_key_c141_3.py | 213 |

### tools/bench/spec_read.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/spec_read_more.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `describe` | v, depth=0 | (no docstring) | - | 21 |
| `purge_junk` | target, before | (no docstring) | - | 32 |
| `main` |  | (no docstring) | - | 43 |

### tools/bench/subvi_harness.py

shared file in the bench folder (move to tools/ later); imported by 6 file(s): `tools/bench/blackbox_z.py`, `tools/bench/harness_probe2.py`, `tools/bench/harness_probe6.py`, `tools/bench/quad_probe.py`, `tools/bench/radial_probe.py`, `tools/bench/radial_probe2.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `build` | subvi_path, max_terms=32, force=False | (no docstring) | - | 27 |
| `run` | h, inputs, outputs | (no docstring) | - | 78 |

### tools/bench/t2_rsrc_blockdiff.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/bench/diag_c153_a2_6_rsrc.py`, `tools/bench/diag_c89_profiler_lvsr.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `recipe_constants` |  | Read ORIGINAL / ORIG_MD5 / ARM out of tools/recipes/stage_d1_s1.py WITHOUT importing it | - | 109 |
| `md5_of` | path | (no docstring) | - | 130 |
| `version_bytes` | data | PRIOR ART, reused verbatim in behaviour from tools/recipes/stage_d1_s1.py:293 -- the first 64 | - | 138 |
| `ParseError` | (class) | (no docstring) | - | 152 |
| `parse_rsrc` | data, label | Return (record, checks).  Never raises on a malformed file -- it records the failure. | - | 156 |
| `key_of` | block | (no docstring) | - | 274 |
| `main` |  | (no docstring) | - | 278 |

### tools/bench/verify_d1_s2.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/c52_astcheck.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `Stop` | (class) | (no docstring) | - | 116 |
| `gate` | name, ok, detail='', fatal=False | (no docstring) | - | 120 |
| `fact` | line | (no docstring) | - | 130 |
| `probe` | tag, path | (no docstring) | - | 135 |
| `dump` |  | (no docstring) | - | 143 |
| `cond_read` | tag, target, loop_uid | ONE conditional-terminal readback through 'OpLoopEndRef_v0', scored on its FOUR per-property ERROR COLUMNS | - | 150 |
| `owner` | target, uid | Parent traversal, with the error kept rather than swallowed. | - | 175 |
| `read_one` | tag, path, key | Everything this file reads out of ONE .vi, read-only: census, WhileLoop identity + ownership + conditional | - | 184 |
| `main` |  | (no docstring) | - | 218 |

### tools/recipes/build_d1_m3a1.py

recipe imported by another file; imported by 25 file(s): `tools/bench/c90c_rows.py`, `tools/bench/diag_c73_m3a2_rows.py`, `tools/bench/diag_c74_m3a2_verify.py`, `tools/bench/diag_c75_m3a3_endpoints.py`, `tools/bench/diag_c75_m3a3_rows.py`, `tools/bench/diag_c75b_loopterms.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `Halt` | (class) | (no docstring) | - | 399 |
| `gate` | name, ok, detail='' | (no docstring) | - | 403 |
| `fact` | line | (no docstring) | - | 411 |
| `refusal` | where, msg | A MUTATOR CALL THE MACHINE REFUSED. This is the only class of negative result that gates (63). | - | 416 |
| `probe_hash` | tag, path | (no docstring) | - | 422 |
| `dump` |  | (no docstring) | - | 429 |
| `left_s` |  | (no docstring) | - | 438 |
| `safe` | label, fn, default=None | Run one READ, record its error VERBATIM, never let it kill the run. | - | 442 |
| `read_es` | tag, target | (no docstring) | - | 452 |
| `counts` | path, tag, classes=('Node', 'Wire', 'ControlTerminal', 'Local', 'LoopTunnel', 'Tunnel') | NARROW CLASS CENSUSES ONLY - never a whole-VI GObject census (six of those took handles 34,602 -> | - | 468 |
| `sr_counts` | path, tag | (no docstring) | - | 479 |
| `node_census` | path, tag | (no docstring) | - | 487 |
| `new_nodes` | before, after | (no docstring) | - | 495 |
| `terms_at` | path, diagram_index, nodes_index, expect_uid, tag, quiet=False | The FULL terminal table of one node, with the node's own uid echoed back before it is believed. | - | 500 |
| `term_state` | t | WIRED / BARE / UNREAD for ONE terminal row (Pre-decided 14; gscript.py:874 gives the one legitimate | - | 524 |
| `wired_count` | rows | (no docstring) | - | 537 |
| `find_node` | path, uid, hints, tag, budget_s=240.0, quiet=False | Which DIAGRAM lists 'uid' in its Nodes[] - answered by the census that finds it, NEVER by owner_of | - | 541 |
| `node_view` | path, uid, hints, tag, quiet=False | (no docstring) | - | 572 |
| `delete_by_uid` | path, cls, uid, tag | report_all(cls) -> .index(uid) -> delete_object(cls, idx). The shape cycle 58 used; no new verb. | - | 583 |
| `census_and_purge` | path, nodes_before, tag, hints, keep_uids=() | 55(c): after EVERY move_in and EVERY connect_nested_v1, diff the 'Node' census and purge the junk BY | - | 614 |
| `save_artefact` | tag, dest, not_equal_to, not_equal_label | g.save writes the WORKING copy in place; the artefact is a fresh path LabVIEW has never seen. | - | 662 |
| `unit_boundary` | tag | The user's 2026-09-19 split rule, applied MECHANICALLY and not as a branch: read ExecState at every | - | 729 |
| `loop_index_of` | uid, tag | (no docstring) | - | 745 |
| `echo_reg_uid` | loop_index, reg_index, want_uid, tag | (no docstring) | - | 761 |
| `reg_index_of` | loop_index, reg_uid, tag | Map a RightShiftRegister uid to its reg_index by READING shift_reg(...) for each slot. Never assumed. | - | 770 |
| `resolve_term` | rows, want_name, want_i, want_source, tag | Address a terminal OFF THE MACHINE: by NAME when the name is non-empty and unique among terminals of | - | 792 |
| `pd85_violations` | wire_uid, walk | PRE-DECIDED 85, THE READER PRECONDITION (docs/cycle27-plan.md:3031-3038): before any assertion | - | 811 |
| `print_walk` | tag, wire_uid, walk, err='' | One FACT line per terminal of 'OpWireSource_v5(UID 2 = wire_uid)': is_source / owner_class / | - | 823 |
| `wire_walk` | tag, wire_uid | 'OpWireSource_v5(UID 2 = wire_uid)' on the LIVE target, printed terminal by terminal. | - | 844 |
| `loop_tunnel_sinks` | walk | (no docstring) | - | 851 |
| `identity_gate` | tag, source_wire, src_before, src_after, sink_wire, sink_walk, mandatory | PRE-DECIDED 70, THE WHOLE TEST, READ OFF THE MACHINE AND NOTHING ELSE. | - | 857 |
| `phase_0` |  | (no docstring) | - | 967 |
| `step_2_baseline` |  | (no docstring) | - | 998 |
| `resolve_dest` | tag | 38(e): RE-RESOLVE the destination index BY UID from a freshly-read traverse list immediately before | - | 1037 |
| `body_a_node_uids` | tag | THE AUTHORITATIVE READ: Diagram #23058's own Nodes[] census, by uid. | - | 1054 |
| `step_2_moves` | hints | (no docstring) | - | 1067 |
| `one_row` | nodes, hints, sink_uid, sink_name, sink_t, src_uid, src_name, src_t, why, tag, slot, src_hints=None | ONE 'connect_nested_v1' row, addressed off the machine at both ends and verified BY WIRE UID. | - | 1120 |
| `step_2_rows` | nodes, hints | (no docstring) | - | 1185 |
| `step_3_registers` |  | (no docstring) | - | 1196 |
| `step_4_sr_rows` | made, hints | (no docstring) | - | 1242 |
| `step_5_t1` | nodes, hints | THE FIFTH ROW, RE-CUT 2026-09-21 by the prior-art review's B3 'helper-exists'. | - | 1339 |
| `step_6_sixth_row` | nodes, hints | THE SIXTH ROW, WIRED **BEFORE** THE CENSUS SO THE A4 BARE-SINK GATE JUDGES THE FINISHED STAGE. | - | 1530 |
| `bare_sink_gate` | hints | '#10407' t6 ''position [internal units]'' has TWO sinks in the original, on net 9113: the | - | 1773 |
| `census` | tag, hints, include_registers=True | THE FULL WIRED-TERMINAL CENSUS of the seven moved nodes (and both registers) - EVERY terminal, not a | - | 1946 |
| `step_7_save` | hints | (no docstring) | - | 2002 |
| `main` |  | (no docstring) | - | 2054 |

### tools/recipes/build_d1_m3a3b_d3.py

recipe imported by another file; imported by 4 file(s): `tools/bench/diag_c86_norbw.py`, `tools/bench/opmodels_measure.py`, `tools/recipes/build_d1_m3a3b_d3b.py`, `tools/stagekit.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | name, ok, detail='', fatal=False | (no docstring) | - | 222 |
| `fact` | line | (no docstring) | - | 231 |
| `head` | t | (no docstring) | - | 236 |
| `safe` | label, fn, default=None | (no docstring) | - | 240 |
| `dump` |  | (no docstring) | - | 249 |
| `left_s` |  | (no docstring) | - | 257 |
| `labels_of` | target, indicators=False | (no docstring) | - | 261 |
| `bad_wire_count` | target, tag | The diagram-wide BROKEN-WIRE COUNT. 'remove_bad_wires_scripted' runs LabVIEW's own | - | 265 |
| `fsit_call` | op_path, labels, target, fsit_uid, sink_diag, sink_node, sink_term, ar_label='', auto_route=None, inv_err_label='erro... | One call of the connect op. Every readout is POISONED first (Pre-decided 125): a stale value can | - | 279 |
| `fsit_read` | target, uid, tag | One read of a FlatSequenceInnerTunnel's two faces through 'OpFsInnerTunnelTerm_v0'. | - | 342 |
| `phase_files` |  | (no docstring) | - | 361 |
| `phase_restart` |  | (no docstring) | - | 388 |
| `build_v1` |  | (no docstring) | - | 403 |
| `gates_23` | labels, ar | (no docstring) | - | 515 |
| `gate_s` | tag, target, d_idx, before_read, r, baseline_bad, rec, probe_bad=True | GATE S (a)-(e) on 'target' after a call. Returns (all_passed, dict of the five outcomes). | - | 581 |
| `one_call_and_gates` | tag, target, d_idx, labels, ar, auto_route, baseline_bad, rec, probe_bad=True | (no docstring) | - | 638 |
| `baseline_bad_wires` |  | (no docstring) | - | 688 |
| `run_cells` | labels, ar, baseline_bad | (no docstring) | - | 709 |
| `step3` | labels, ar, results, baseline_bad | (no docstring) | - | 757 |
| `phase_hygiene` |  | (no docstring) | - | 848 |
| `main` |  | (no docstring) | - | 902 |

### tools/recipes/build_d1_v0.py

recipe imported by another file; imported by 176 file(s): `tools/bench/build_op_const_loopterm_77.py`, `tools/bench/c52_astcheck.py`, `tools/bench/c52r2_astcheck.py`, `tools/bench/c52r3_astcheck.py`, `tools/bench/c53_astcheck.py`, `tools/bench/c73_l7r_live.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | name, ok, detail='' | (no docstring) | - | 299 |
| `fact` | line | (no docstring) | - | 305 |
| `md5` | p | (no docstring) | - | 310 |
| `move_in` | target, uid, dest_diagram_index, position | probe_move_ctlterm_v0.py:160-178 verbatim. The Move returns NO reference to the object at its new home | - | 318 |
| `owner_of` | target, uid, strict=True | (no docstring) | - | 338 |
| `diag_index` | target, uid | (no docstring) | - | 357 |
| `wmap` | target, diagram_index, fresh=False | ONE 'build_track_v6_core.walk' per diagram, cached. 'walk' is 'node_labels' + up to 80 'node_terms_uid' | - | 364 |
| `terms_of` | target, diagram_index, uid, fresh=False | {term index: (name, is_source, wire)} for one node, out of the cached walk of its diagram. | - | 375 |
| `sr_census` | target, loop_index, n_regs=14 | Every shift register of one While loop: its OUTSIDE wire (the final value that LEAVES the loop) and its | - | 383 |
| `s0` |  | (no docstring) | - | 405 |
| `s1` |  | (no docstring) | - | 437 |
| `bare_named_sinks` | target, diagram_index, fresh=False | {(node uid, terminal index): name} for every NAMED input terminal on the diagram that carries NO wire. | - | 482 |
| `s1t` |  | (no docstring) | - | 494 |
| `s2` |  | (no docstring) | - | 533 |
| `s3` | loops | (no docstring) | - | 569 |
| `s3c` | loops | (no docstring) | - | 734 |
| `s3d` | loops, kernel_uid | The 6 loop-invariant seam inputs must reach the kernel through NON-INDEXED tunnels (plan s8; rule 1a - | - | 769 |
| `loop_end_ref` | target, loop_index | A While loop's CONDITIONAL TERMINAL, through OpLoopEndRef_v0 (16/0). Driven exactly as | - | 820 |
| `s4` | loops | (no docstring) | - | 856 |
| `s5` | inv0 | (no docstring) | - | 888 |
| `s6` |  | (no docstring) | - | 907 |
| `class_index` | target, classes=('SubVI', 'Function', 'CaseStructure', 'ForLoop', 'WhileLoop', 'Comparison', 'IndexArray', 'BuildArra... | uid -> (Traverse class, index in that class's Traverse listing). 'gscript.wire' addresses a node as | - | 946 |
| `phase_full_rewire` | loops, regs, r3 | (no docstring) | - | 962 |
| `main` |  | (no docstring) | - | 1156 |

### tools/recipes/build_opcaseframes_v0.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/build_oploopendref_v0.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `prop_node` | cls, pid, label, pos | Build a property node and CENSUS its data terminal - the short name is never guessed. | - | 48 |
| `add_indicator` | uid, name, key, labels | (no docstring) | - | 62 |
| `main` |  | (no docstring) | - | 74 |
| `read_frame` | vi, labels, case_uid, idx | (no docstring) | - | 210 |
| `test` | labels | (no docstring) | - | 230 |

### tools/recipes/build_opconnectfromwire_v0.py

recipe imported by another file; imported by 54 file(s): `tools/bench/constsrc_l2a1_82.py`, `tools/bench/constsrc_l2a1_85.py`, `tools/bench/ctsrc_l2a1_82.py`, `tools/bench/diag_c113c_scratch.py`, `tools/bench/diag_c66_s3b_m3.py`, `tools/bench/diag_c66b_s3b_m3.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | name, ok, detail='', fatal=False | (no docstring) | - | 141 |
| `fact` | line | (no docstring) | - | 149 |
| `md5` | p | (no docstring) | - | 153 |
| `new_ctl` | target, before_labels | (no docstring) | - | 161 |
| `ctl_labels` | target, indicators=False | (no docstring) | - | 166 |
| `build` |  | (no docstring) | - | 171 |
| `connect_from_wire` | target, wire_uid, term_index, sink_diag, sink_node, sink_term, labels | Wire the SOURCE terminal 'Wire(uid=wire_uid).Terms[term_index]' into | - | 381 |
| `wire_source_owner` | target, wire_uid, n=6 | 'OpWireSource_v5' on 'target': the owner of the wire's single SOURCE terminal. Read-only. | - | 427 |
| `t1` | labels | (no docstring) | - | 491 |
| `t2` | labels | (no docstring) | - | 558 |
| `cleanup` |  | (no docstring) | - | 640 |
| `main` |  | (no docstring) | - | 656 |

### tools/recipes/build_opconnectnested_v1.py

recipe imported by another file; imported by 72 file(s): `tools/bench/c53_astcheck.py`, `tools/bench/diag_c120_fs.py`, `tools/bench/diag_c123_casetun.py`, `tools/bench/diag_c123_routes.py`, `tools/bench/diag_c123_struct.py`, `tools/bench/diag_c123_wired.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `Stop` | (class) | (no docstring) | - | 129 |
| `gate` | name, ok, detail='', fatal=False | (no docstring) | - | 133 |
| `fact` | line | (no docstring) | - | 141 |
| `md5` | p | (no docstring) | - | 146 |
| `walk` | target, diagram=0, limit=120 | (no docstring) | - | 154 |
| `term` | rows, name, source=None | (no docstring) | - | 165 |
| `cls_of` | uid, w | (no docstring) | - | 172 |
| `idx` | target, cls, uid | (no docstring) | - | 183 |
| `src_of` | w, wire | the node whose SOURCE terminal carries 'wire' | - | 187 |
| `connect` | target, src_uid, src_name, dst_uid, dst_name, branch=False, tag='' | Wire by NAME, verified by the SAME wire uid on BOTH ends (build_opconnectnested_v0.connect verbatim). | - | 196 |
| `del_net` | target, wire_uid, tag='' | (no docstring) | - | 212 |
| `ladder_from` | w, sink_wire, tag | IA(term) <- PN[Terms[]] <- IA(node) <- PN[Nodes[]] <- head-wire, walking back from the Invoke. | - | 221 |
| `build` |  | (no docstring) | - | 239 |
| `connect_nested_v1` | target, sink_diag, sink_node, sink_term, src_diag, src_node, src_term, labels | Wire Diagram[src_diag].Nodes[src_node].Terminals[src_term] (SOURCE) into | - | 418 |
| `test` | labels | (no docstring) | - | 463 |
| `main` |  | (no docstring) | - | 608 |

### tools/recipes/build_opconstvalue_v1.py

recipe imported by another file; imported by 59 file(s): `tools/bench/census_dnc_property_ids.py`, `tools/bench/census_hexstring_vi.py`, `tools/bench/census_selector_sources.py`, `tools/bench/census_unflatten_terms.py`, `tools/bench/diag_9775_direction.py`, `tools/bench/diag_autofocus_border.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `lv_pid` |  | (no docstring) | - | 49 |
| `com_preflight` | tries=15, gap=4.0 | Run 4 (04:13): fresh() + 8 s + reset() was NOT enough - the first call on the relaunched instance died with | - | 56 |
| `fresh` |  | (no docstring) | - | 80 |
| `cls_idx` | target, cls, uid | (no docstring) | - | 90 |
| `main` |  | (no docstring) | - | 94 |
| `test` | labels | (no docstring) | - | 212 |

### tools/recipes/build_opconstvalue_v1b.py

recipe imported by another file; imported by 5 file(s): `tools/bench/diag_constvalue_siblings.py`, `tools/gscript.py`, `tools/recipes/build_opconstvalue_v1c.py`, `tools/recipes/build_opconstvaluen_v0.py`, `tools/recipes/build_opconstvaluen_v1.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `decode_flat` | data | Flattened LabVIEW variant as emitted by Flatten To String on a variant (NI 'Understanding Flattened Variant | - | 37 |
| `main` |  | (no docstring) | - | 95 |
| `test` | labels | (no docstring) | - | 141 |

### tools/recipes/build_opconstvalue_v1c.py

recipe imported by another file; imported by 4 file(s): `tools/bench/diag_constvalue_siblings.py`, `tools/gscript.py`, `tools/recipes/build_opconstvaluen_v0.py`, `tools/recipes/build_opconstvaluen_v1.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `new_labels` | dst, before, ind | (no docstring) | - | 45 |
| `main` |  | (no docstring) | - | 49 |
| `normalize_u8` | v | pywin32 maps SAFEARRAY(VT_UI1) to a buffer-like value (bytes/memoryview), older builds to a tuple of ints | - | 118 |
| `test` | labels | (no docstring) | - | 132 |

### tools/recipes/build_opconstvaluen_v0.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/build_opconstvaluen_v1.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `new_labels` | dst, before, ind | (no docstring) | - | 46 |
| `main` |  | (no docstring) | - | 50 |
| `parse_num` | s | (no docstring) | - | 142 |
| `test` | labels | (no docstring) | - | 153 |

### tools/recipes/build_opcreateconstonterm_v0.py

recipe imported by another file; imported by 23 file(s): `tools/bench/build_op_const_loopterm_77.py`, `tools/bench/c52r2_astcheck.py`, `tools/bench/diag_c123_routes.py`, `tools/bench/diag_c123_struct.py`, `tools/bench/diag_c90_t0_step3.py`, `tools/bench/diag_c90_t0_step3b.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | name, ok, detail='' | (no docstring) | - | 108 |
| `fact` | line | (no docstring) | - | 114 |
| `md5` | p | (no docstring) | - | 119 |
| `walk` | target, diagram=0, limit=100 | (no docstring) | - | 127 |
| `term` | rows, name, source=None | (no docstring) | - | 138 |
| `cls_of` | uid, w | (no docstring) | - | 145 |
| `idx` | target, cls, uid | (no docstring) | - | 156 |
| `connect` | src_uid, src_name, dst_uid, dst_name, branch=False, tag='' | Wire by name, verified by the SAME wire uid on BOTH ends (build_opstopfromnode_v0.connect verbatim). | - | 160 |
| `owner_of` | target, uid | (no docstring) | - | 175 |
| `counts` | target | (no docstring) | - | 191 |
| `build` |  | (no docstring) | - | 197 |
| `create_const_on_term` | target, loop_index, node_index, term_index, labels, value=None | Run OpCreateConstOnTerm_v0 on 'target'. Returns {err, inv_err, created_uid} - prior-art B4's oracle | - | 364 |
| `read_const` | target, uid | The created constant's value/Representation/text through OpConstValueN_v1 (toolkit row 47), addressed by | - | 392 |
| `test` | labels | (no docstring) | - | 423 |
| `main` |  | (no docstring) | - | 569 |

### tools/recipes/build_opfsinnertunnelconnect_v0.py

recipe imported by another file; imported by 16 file(s): `tools/bench/build_op_const_loopterm_77.py`, `tools/bench/diag_c138_6_run.py`, `tools/bench/diag_c83_connect2x2.py`, `tools/bench/diag_c83_connect2x2_kit.py`, `tools/bench/diag_c83_connect2x2_r2.py`, `tools/bench/diag_c86_norbw.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | name, ok, detail='', fatal=False | (no docstring) | - | 200 |
| `fact` | line | (no docstring) | - | 209 |
| `head` | t | (no docstring) | - | 214 |
| `safe` | label, fn, default=None | (no docstring) | - | 218 |
| `md5` | p | (no docstring) | - | 227 |
| `dump` |  | (no docstring) | - | 235 |
| `left_s` |  | (no docstring) | - | 243 |
| `private_bytes` |  | LabVIEW's private bytes - the COMPANION of the handle count, which | - | 247 |
| `purge_junk` | target, nodes_before, tag, hints | The measured junk shape of the OpConnect* family: a fresh 'Invoke' node with ZERO wired terminals | - | 263 |
| `labels_of` | target, indicators=False | (no docstring) | - | 302 |
| `new_labels` | target, before, indicators=False | (no docstring) | - | 306 |
| `wire_named` | src_cls, src_uid, src_name, dst_cls, dst_uid, dst_name, branch=False, tag='' | Wire by NAME with EXPLICIT traverse classes, verified by the SAME wire uid on BOTH ends. | - | 310 |
| `data_out` | rows | The single NON-STANDARD source terminal of a property node = its data output. Read back, never | - | 329 |
| `del_wire` | target, wire_uid, tag='' | (no docstring) | - | 336 |
| `del_node` | target, cls, uid, tag='' | (no docstring) | - | 346 |
| `phase_files` |  | (no docstring) | - | 359 |
| `phase_restart` |  | (no docstring) | - | 384 |
| `build` |  | (no docstring) | - | 399 |
| `fsit_connect` | target, fsit_uid, sink_diag, sink_node, sink_term, labels, count_wires=False | Wire 'FlatSequenceInnerTunnel(uid=fsit_uid).LeftTerm' into | - | 597 |
| `gates_23` | labels | (no docstring) | - | 651 |
| `resolve_triple` | target, tag | The NEW loop's (diagram traverse index, Nodes[] index, Terminals[] index), resolved LIVE with a uid | - | 730 |
| `gate4` | labels | (no docstring) | - | 752 |
| `phase_hygiene` |  | (no docstring) | - | 837 |
| `main` |  | (no docstring) | - | 896 |

### tools/recipes/build_opfstunnelterm_v0.py

recipe imported by another file; imported by 1 file(s): `tools/bench/diag_fstunnel_wire_semantics.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `must` | label, ok, detail='' | (no docstring) | - | 157 |
| `note` | label, value | (no docstring) | - | 163 |
| `md5` | p | (no docstring) | - | 167 |
| `snapshot` | tag | (no docstring) | - | 182 |
| `handles` | tag | (no docstring) | - | 191 |
| `identity` |  | (no docstring) | - | 207 |
| `sweep` | target, n=120, diagram=0 | (no docstring) | - | 240 |
| `trow` | by, uid, name | (no docstring) | - | 250 |
| `twire` | by, uid, name | (no docstring) | - | 260 |
| `has` | by, uid, name, is_source=None | (no docstring) | - | 265 |
| `cidx` | target, cls, uid | (no docstring) | - | 270 |
| `node_index_of` | target, uid, diagram=0, n=120 | (no docstring) | - | 274 |
| `wire_checked` | op, src_cls, src_uid, src_term, dst_cls, dst_uid, dst_term, tag='' | One wire, VERIFIED BY TERMINAL IDENTITY instead of by 'gscript.wire''s wire COUNT. | - | 284 |
| `ctl_labels` | target | (no docstring) | - | 323 |
| `ind_labels` | target | (no docstring) | - | 327 |
| `build_one` | kind | Build ONE of the two ops. Identical route for both classes; only SPEC[kind] differs. | - | 331 |
| `read_tunnel` | vi, lab, target, uid | One live read of ONE tunnel uid through ONE of the two ops. Every readout is POISONED first, so a stale | - | 526 |
| `read_any` | target, uid, kind=None | The reader the CALLER sees: one function over BOTH tunnel classes. 'kind' is taken from the owner's class | - | 584 |
| `refusal` | target, uid, why | Pre-decided 3: feed a deliberately bad input to BOTH ops and record the refusal VERBATIM. | - | 600 |
| `face_cross` | target, owner_class, owner_uid, arrival_wire | A4/T2: cross ONE flat-sequence border. Returns (continuation wire or None, read, verdict text). | - | 618 |
| `walk` | target, seed_wire, tag, max_cross=6 | The backward walk. B3: the HOP LOOP IS 'diag_tunnelsource_onehop.resolve()' - this function only supplies | - | 642 |
| `crossings_of` | w | (no docstring) | - | 676 |
| `live` | target, labels_by_kind | (no docstring) | - | 680 |
| `inherit_probe` |  | RECORDED, not gated: does the OUTER class inherit 'Tunnel'? One scratch VI, unique name, deleted in the | - | 790 |
| `main` |  | (no docstring) | - | 835 |

### tools/recipes/build_opfstunnelterm_v1.py

recipe imported by another file; imported by 6 file(s): `tools/bench/diag_fstunnel_orphan_timeline.py`, `tools/bench/diag_fstunnel_orphans.py`, `tools/bench/diag_fstunnel_preclean_twins.py`, `tools/bench/diag_fstunnel_rbwvictims.py`, `tools/bench/diag_fstunnel_wirebroken.py`, `tools/bench/diag_fstunnel_wireterms_panel.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `must` | label, ok, detail='' | (no docstring) | - | 165 |
| `note` | label, value | (no docstring) | - | 171 |
| `md5` | p | (no docstring) | - | 175 |
| `snapshot` | tag | (no docstring) | - | 190 |
| `handles` | tag | (no docstring) | - | 199 |
| `identity` |  | (no docstring) | - | 215 |
| `sweep` | target, n=120, diagram=0 | (no docstring) | - | 248 |
| `trow` | by, uid, name | (no docstring) | - | 258 |
| `twire` | by, uid, name | (no docstring) | - | 268 |
| `has` | by, uid, name, is_source=None | (no docstring) | - | 273 |
| `cidx` | target, cls, uid | (no docstring) | - | 278 |
| `node_index_of` | target, uid, diagram=0, n=120 | (no docstring) | - | 282 |
| `wire_checked` | op, src_cls, src_uid, src_term, dst_cls, dst_uid, dst_term, tag='' | One wire, VERIFIED BY TERMINAL IDENTITY instead of by 'gscript.wire''s wire COUNT, plus a per-site | - | 292 |
| `ctl_labels` | target | (no docstring) | - | 368 |
| `ind_labels` | target | (no docstring) | - | 372 |
| `build_one` | kind | Build ONE of the two ops. Identical route for both classes; only SPEC[kind] differs. | - | 376 |
| `read_tunnel` | vi, lab, target, uid | One live read of ONE tunnel uid through ONE of the two ops. Every readout is POISONED first, so a stale | - | 571 |
| `read_any` | target, uid, kind=None | The reader the CALLER sees: one function over BOTH tunnel classes. 'kind' is taken from the owner's class | - | 629 |
| `refusal` | target, uid, why | Pre-decided 3: feed a deliberately bad input to BOTH ops and record the refusal VERBATIM. | - | 645 |
| `face_cross` | target, owner_class, owner_uid, arrival_wire | A4/T2: cross ONE flat-sequence border. Returns (continuation wire or None, read, verdict text). | - | 663 |
| `walk` | target, seed_wire, tag, max_cross=6 | The backward walk. B3: the HOP LOOP IS 'diag_tunnelsource_onehop.resolve()' - this function only supplies | - | 687 |
| `crossings_of` | w | (no docstring) | - | 721 |
| `live` | target, labels_by_kind | (no docstring) | - | 725 |
| `inherit_probe` |  | RECORDED, not gated: does the OUTER class inherit 'Tunnel'? One scratch VI, unique name, deleted in the | - | 835 |
| `main` |  | (no docstring) | - | 880 |

### tools/recipes/build_opfstunnelterm_v2.py

recipe imported by another file; imported by 6 file(s): `tools/bench/diag_c77_rowd_addr.py`, `tools/bench/diag_c81_uidref.py`, `tools/bench/diag_fstunnel_pairs.py`, `tools/recipes/build_d1_m3a3.py`, `tools/recipes/build_d1_m3a3b_d3.py`, `tools/wiki_build.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `must` | label, ok, detail='' | (no docstring) | - | 235 |
| `note` | label, value | (no docstring) | - | 241 |
| `md5` | p | (no docstring) | - | 245 |
| `snapshot` | tag | (no docstring) | - | 260 |
| `handles` | tag | (no docstring) | - | 269 |
| `identity` |  | (no docstring) | - | 285 |
| `sweep` | target, n=120, diagram=0 | (no docstring) | - | 318 |
| `trow` | by, uid, name | (no docstring) | - | 328 |
| `twire` | by, uid, name | (no docstring) | - | 338 |
| `has` | by, uid, name, is_source=None | (no docstring) | - | 343 |
| `cidx` | target, cls, uid | (no docstring) | - | 348 |
| `node_index_of` | target, uid, diagram=0, n=120 | (no docstring) | - | 352 |
| `wire_checked` | op, src_cls, src_uid, src_term, dst_cls, dst_uid, dst_term, tag='' | One wire, VERIFIED BY TERMINAL IDENTITY instead of by 'gscript.wire''s wire COUNT, plus a per-site | - | 362 |
| `ctl_labels` | target | (no docstring) | - | 438 |
| `ind_labels` | target | (no docstring) | - | 442 |
| `orphan_wires` | target, by | (orphan uids, whole Wire census) - a wire is an ORPHAN when NO owning-node terminal reads it at EITHER end. | - | 460 |
| `rbw_call_sites` |  | A0f: how many times THIS FILE calls the RBW helper - read from its own source text. | - | 468 |
| `rbw_repair_at_b4` | op, kind, tag | Twin-A reproduction (diag_fstunnel_preclean_twins.log), run ONLY when B4's first ExecState read is not 1: | - | 483 |
| `build_one` | kind | Build ONE of the two ops. Identical route for both classes; only SPEC[kind] differs. | - | 535 |
| `read_tunnel` | vi, lab, target, uid | One live read of ONE tunnel uid through ONE of the two ops. Every readout is POISONED first, so a stale | - | 745 |
| `read_any` | target, uid, kind=None | The reader the CALLER sees: one function over BOTH tunnel classes. 'kind' is taken from the owner's class | - | 803 |
| `refusal` | target, uid, why | Pre-decided 3: feed a deliberately bad input to BOTH ops and record the refusal VERBATIM. | - | 819 |
| `face_cross` | target, owner_class, owner_uid, arrival_wire | A4/T2: cross ONE flat-sequence border. Returns (continuation wire or None, read, verdict text). | - | 837 |
| `walk` | target, seed_wire, tag, max_cross=6 | The backward walk. B3: the HOP LOOP IS 'diag_tunnelsource_onehop.resolve()' - this function only supplies | - | 861 |
| `crossings_of` | w | (no docstring) | - | 895 |
| `live` | target, labels_by_kind | (no docstring) | - | 899 |
| `inherit_probe` |  | RECORDED, not gated: does the OUTER class inherit 'Tunnel'? One scratch VI, unique name, deleted in the | - | 1009 |
| `main` |  | (no docstring) | - | 1054 |

### tools/recipes/build_opownerchain_v1.py

recipe imported by another file; imported by 11 file(s): `tools/bench/diag_c152_a1_1_owner.py`, `tools/bench/diag_d1_step0.py`, `tools/bench/diag_hierarchy_a3.py`, `tools/bench/diag_owner_semantics.py`, `tools/bench/diag_ownerchain_hop.py`, `tools/bench/diag_stop_save_seam.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | name, ok, detail='' | (no docstring) | - | 187 |
| `md5` | p | (no docstring) | - | 192 |
| `sweep` |  | {node_uid: (node_index, rows)} for diagram 0 in ONE pass - no net_map, no creator, no junk. | - | 196 |
| `trow` | by, uid, name | (no docstring) | - | 207 |
| `twire` | by, uid, name | (no docstring) | - | 217 |
| `tindex` | by, uid, name | (no docstring) | - | 222 |
| `cls_uids` | cls | (no docstring) | - | 227 |
| `purge_junk` | before | Delete every Invoke node that appeared since 'before'. 'OpConnect2_v0' carries the erdosmiller | - | 231 |
| `read_owner` | vi, labels, uid | Drive the op: uid in -> (owner class, owner uid, cross-checks, errors). Outputs poisoned first, so a | - | 246 |
| `main` |  | (no docstring) | - | 282 |

### tools/recipes/build_opsentinel_ops.py

recipe imported by another file; imported by 13 file(s): `tools/bench/c52_astcheck.py`, `tools/bench/diag_queue_donor.py`, `tools/bench/diag_s2_scaffold.py`, `tools/recipes/build_d1_routeb_v0.py`, `tools/recipes/build_d1_routeb_v1.py`, `tools/recipes/build_d1_routeb_v2.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | name, ok, detail='' | (no docstring) | - | 143 |
| `fact` | line | (no docstring) | - | 149 |
| `md5` | p | (no docstring) | - | 154 |
| `owner_of` | target, uid | B4's reader, unchanged: OpOwnerChain_v1 through build_opownerchain_v1.read_owner. | - | 162 |
| `build` | kind | (no docstring) | - | 180 |
| `create_node` | kind, labels, target, diagram_index, location, src_cls=None, src_index=0, src_names=(), values=None | Run Op<CreateEqual/CreateConst>_v0 on 'target'. Same call shape as 'gscript.queue_node', so the wrapper | - | 387 |
| `functional_test` | built | (no docstring) | - | 409 |
| `main` |  | (no docstring) | - | 583 |

### tools/recipes/build_opstopfromnode_v0.py

recipe imported by another file; imported by 22 file(s): `tools/bench/c52_astcheck.py`, `tools/bench/c52r2_astcheck.py`, `tools/bench/c52r3_astcheck.py`, `tools/bench/c53_astcheck.py`, `tools/bench/diag_donor_census.py`, `tools/bench/diag_movein_set.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `gate` | name, ok, detail='' | (no docstring) | - | 118 |
| `fact` | line | (no docstring) | - | 124 |
| `walk` | target, diagram=0, limit=100 | (no docstring) | - | 129 |
| `term` | rows, name, source=None | (no docstring) | - | 140 |
| `cls_of` | uid, w | (no docstring) | - | 147 |
| `idx` | target, cls, uid | (no docstring) | - | 158 |
| `data_name` | uid, w=None | The property node's DATA terminal, CENSUSED - not the index-4 convention. | - | 162 |
| `connect` | src_uid, src_name, dst_uid, dst_name, branch=False, tag='' | Wire by name, verified by the SAME wire uid on BOTH ends - never by a count, never by ExecState | - | 180 |
| `pn` | cls, pid, pos | Create ONE property node and census it (B3): exactly one new 'Property' object, and 'data_name' then | - | 196 |
| `ia` | pos | (no docstring) | - | 209 |
| `make_ctl` | uid, name | (no docstring) | - | 214 |
| `counts` | target | (no docstring) | - | 226 |
| `build` |  | (no docstring) | - | 230 |
| `loop_end_ref` | target, loop_index | B2: 'build_d1_v0.loop_end_ref' verbatim - it poisons EVERY output (IsSource included) and returns the four | - | 340 |
| `wire_source` | target, wire_uid, max_terms=8 | B4(b), the POSITIVE check: 'OpWireSource_v5' (12/12, toolkit-capabilities.md:48) resolves which object | - | 350 |
| `test` | labels | (no docstring) | - | 391 |
| `main` |  | (no docstring) | - | 527 |

### tools/recipes/build_optunnelread_v0.py

recipe imported by another file; imported by 2 file(s): `tools/bench/diag_hierarchy_a3.py`, `tools/recipes/build_opcaseframes_v0.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `prop_node` | cls, pid, short, pos | (no docstring) | - | 44 |
| `add_indicator` | uid, name, key, labels | (no docstring) | - | 55 |
| `drop_wire` | uid | (no docstring) | - | 67 |
| `main` |  | (no docstring) | - | 73 |
| `read_inner` | vi, labels, tunnel_uid, idx | (no docstring) | - | 180 |
| `test` | labels | (no docstring) | - | 204 |

### tools/recipes/build_opwiresource_v0.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/build_opwiresource_v1.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `new_labels` | dst, before, ind | (no docstring) | - | 51 |
| `prop_node` | cls, pid, short, pos | (no docstring) | - | 55 |
| `drop_node` | uid, cls, tag | (no docstring) | - | 66 |
| `main` |  | (no docstring) | - | 72 |
| `read_wire` | vi, labels, wire_uid, wires | (no docstring) | - | 200 |
| `test` | labels | (no docstring) | - | 218 |
| `finally_audit` |  | (no docstring) | - | 248 |

### tools/recipes/build_opwiresource_v1.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/build_opwiresource_v2.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `handles` |  | (no docstring) | - | 56 |
| `prop_node` | cls, pid, short, pos | (no docstring) | - | 63 |
| `add_indicator` | uid, name, key, labels | (no docstring) | - | 74 |
| `main` |  | (no docstring) | - | 86 |
| `read_uid` | vi, labels, wire_uid | (no docstring) | - | 221 |
| `test` | labels | (no docstring) | - | 238 |

### tools/recipes/build_opwiresource_v2.py

recipe imported by another file; imported by 2 file(s): `tools/bench/diag_source_uid_contradiction.py`, `tools/recipes/build_opwiresource_v3.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `prop_node` | cls, pid, short, pos | (no docstring) | - | 50 |
| `add_indicator` | uid, name, key, labels | (no docstring) | - | 61 |
| `main` |  | (no docstring) | - | 73 |
| `read_uid` | vi, labels, wire_uid | (no docstring) | - | 159 |
| `test` | labels | (no docstring) | - | 177 |

### tools/recipes/build_opwiresource_v3.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/build_opwiresource_v4.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `prop_node` | cls, pid, short, pos | (no docstring) | - | 47 |
| `add_indicator` | uid, name, key, labels | (no docstring) | - | 58 |
| `main` |  | (no docstring) | - | 70 |
| `read_terminal` | vi, labels, wire_uid, idx | (no docstring) | - | 134 |
| `test` | labels | (no docstring) | - | 155 |

### tools/recipes/build_opwiresource_v4.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/build_opwiresource_v5.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `prop_node` | cls, pid, short, pos | (no docstring) | - | 47 |
| `add_indicator` | uid, name, key, labels | (no docstring) | - | 58 |
| `main` |  | (no docstring) | - | 70 |
| `read_terminal` | vi, labels, wire_uid, idx | (no docstring) | - | 126 |
| `test` | labels | (no docstring) | - | 148 |

### tools/recipes/build_opwiresource_v5.py

recipe imported by another file; imported by 18 file(s): `tools/bench/c52r2_astcheck.py`, `tools/bench/diag_9775_direction.py`, `tools/bench/diag_autofocus_border.py`, `tools/bench/diag_case5540_context.py`, `tools/bench/diag_case5540_frame_sources.py`, `tools/bench/diag_case5540_inputs.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `prop_node` | cls, pid, short, pos | (no docstring) | - | 48 |
| `add_indicator` | uid, name, key, labels | (no docstring) | - | 59 |
| `main` |  | (no docstring) | - | 71 |
| `read_terminal` | vi, labels, wire_uid, idx | (no docstring) | - | 155 |
| `test` | labels | (no docstring) | - | 177 |

### tools/recipes/build_opwiresr_v0.py

recipe imported by another file; imported by 1 file(s): `tools/bench/test_opwiresr.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `step` | name, predict, fn | (no docstring) | - | 76 |
| `check` | name, ok, detail='' | (no docstring) | - | 90 |
| `walk` | target, diagram=0, limit=100 | (no docstring) | - | 95 |
| `term` | rows, name, source=None | (no docstring) | - | 106 |
| `snap` | tag='' | (no docstring) | - | 113 |
| `idx` | cls, uid | (no docstring) | - | 118 |
| `cls_of` | uid, w | (no docstring) | - | 122 |
| `pn` | cls, pid, pos | (no docstring) | - | 133 |
| `ia` | pos | (no docstring) | - | 138 |
| `wire_uid` | uid, name, source, w=None | (no docstring) | - | 143 |
| `data_name` | uid, w=None | A property node's data terminal = index 4 (v1 recipe). | - | 149 |
| `connect` | src_uid, src_name, dst_uid, dst_name, branch=False, tag='' | wire by name, verified by the SAME wire uid on both ends (row 37: never by count, never by ExecState). | - | 155 |
| `make_ctl` | uid, name, label_key, labels | (no docstring) | - | 169 |
| `make_ind` | uid, name, label_key, labels | (no docstring) | - | 180 |
| `build` | variant | (no docstring) | - | 191 |
| `run_op` | variant, labels, target, loop_index, reg_index, **kw | (no docstring) | - | 283 |
| `test` | all_labels | (no docstring) | - | 293 |
| `add_sr_for` | target, loop_index, y | OpAddShiftRegF_v0 (built by build_opaddshiftreg_v0.py with SR_SEED=For) -> new register uid. | - | 374 |
| `test_for` | all_labels | FUNCTIONAL, For seed: HARNESS_copyloop's existing For loop (N = 1024); a NEW IMAQ Copy dropped in its body; | - | 387 |
| `main` |  | (no docstring) | - | 447 |

### tools/recipes/build_track_v6_core.py

recipe imported by another file; imported by 37 file(s): `tools/bench/census_dnc_property_ids.py`, `tools/bench/census_hexstring_vi.py`, `tools/bench/census_unflatten_terms.py`, `tools/bench/diag_c118_p1.py`, `tools/bench/diag_c122_hyg.py`, `tools/bench/diag_c123_routes.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `Stop` | (class) | (no docstring) | - | 68 |
| `arg` | name, default | (no docstring) | - | 72 |
| `must` | name, ok, detail='' | (no docstring) | - | 77 |
| `walk` | target, diagram=0 | (no docstring) | - | 84 |
| `term` | rows, name, source | (no docstring) | - | 95 |
| `sub_i` | target, uid | (no docstring) | - | 99 |
| `drop` | target, path, diagram, pos | (no docstring) | - | 103 |
| `wire_sub` | target, su, st, du, dt, dsrc, ddst, branch=False, tag='' | Wire by name and gate by wire uid. Same diagram: one Wire object, same uid on both ends. ACROSS a loop border | - | 111 |
| `string_array_control` | target, tag | (no docstring) | - | 144 |
| `tunnel_route` | target, fp_label, u_stp, body, tag | wire_control(ctl -> StrToPath.string) creates a non-indexed tunnel; set_index_mode(1) must heal the wire. | - | 159 |
| `discriminator` |  | (no docstring) | - | 174 |
| `build` |  | (no docstring) | - | 198 |
| `load_reference` |  | (no docstring) | - | 337 |
| `fixture_run` | labels, ref, frames, tag | ONE COM run over 'frames'; XYZ/GOOD/POS rows compared EXACTLY with the reference (pre-loss frames). | - | 349 |
| `main` |  | (no docstring) | - | 399 |

### tools/recipes/stage_d1_fgate.py

recipe imported by another file; imported by 3 file(s): `tools/bench/selftest_c98_rbw.py`, `tools/bench/selftest_c98_stage.py`, `tools/recipes/diag_c98_fgate.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `body` | s | (no docstring) | - | 24 |
| `St` | (class) | (no docstring) | - | 123 |
| `St.close` | expect_files=None | (no docstring) | - | 124 |

### tools/recipes/stage_d1_l2r1.py

recipe imported by another file; imported by 1 file(s): `tools/bench/diag_c115b_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `rbw` | s, target, tag | (no docstring) | - | 31 |
| `body` | s | (no docstring) | - | 36 |

### tools/recipes/stage_d1_l2r2.py

recipe imported by another file; imported by 2 file(s): `tools/bench/diag_c116b_scratch.py`, `tools/bench/diag_c116d_j3.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `rbw` | s, target, tag | (no docstring) | - | 28 |
| `body` | s | (no docstring) | - | 33 |

### tools/recipes/stage_d1_l7_r.py

recipe imported by another file; imported by 1 file(s): `tools/bench/dryrun_l7_r_address.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `lg` | s, tag, gone=() | (no docstring) | - | 16 |
| `trow` | s, dg, u, i | (no docstring) | - | 23 |
| `at` | s, dg, u, name, is_src | First resolution BY NAME (Pre-decided 174); the one ambiguous name (#2048 'length') is tie-broken by the index its S1 wire used (anchored by A0). | - | 27 |
| `nested` | s, tag, src, dst | (no docstring) | - | 35 |
| `tunnel_row` | s, tag, src_term, dst, old, TM | (no docstring) | - | 40 |
| `second` | s, sym, lab, srcs, u, t, tu | 42(b) ordered 2nd pass, the sink addressed by verify_term_uid ONLY now (Pre-decided 174); the source owner is the first listed that owns it. | - | 50 |
| `body` | s | (no docstring) | - | 59 |

### tools/recipes/stage_d1_qrt_pool.py

recipe imported by another file; imported by 1 file(s): `tools/bench/stage_d1_qrt_pool_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `body` | s | (no docstring) | - | 28 |

### tools/recipes/stage_d1_ring_p2a.py

recipe imported by another file; imported by 1 file(s): `tools/bench/stage_d1_ring_p2a_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `body` | s | (no docstring) | - | 29 |

### tools/recipes/stage_d1_ring_p2b.py

recipe imported by another file; imported by 1 file(s): `tools/bench/stage_d1_ring_p2b_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `same` | a, b | (no docstring) | - | 32 |
| `body` | s | (no docstring) | - | 41 |

### tools/recipes/stage_d1_ring_p3a.py

recipe imported by another file; imported by 1 file(s): `tools/bench/stage_d1_ring_p3a_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `body` | s | (no docstring) | - | 29 |

### tools/recipes/stage_d1_ring_p3b1.py

recipe imported by another file; imported by 1 file(s): `tools/bench/stage_d1_ring_p3b1_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `body` | s | (no docstring) | - | 34 |

### tools/recipes/stage_d1_ring_p3b2a.py

recipe imported by another file; imported by 2 file(s): `tools/bench/launch_p3b2_c135_a.py`, `tools/bench/stage_d1_ring_p3b2a_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `body` | s | (no docstring) | - | 34 |

### tools/recipes/stage_d1_ring_p3b2b.py

recipe imported by another file; imported by 2 file(s): `tools/bench/launch_p3b2_c135_b.py`, `tools/bench/stage_d1_ring_p3b2b_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `body` | s | (no docstring) | - | 36 |

### tools/recipes/stage_d1_ring_p4_rasrest.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4_rasrest_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `body` | s | (no docstring) | - | 34 |

### tools/recipes/stage_d1_ring_p4_s01.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4_s01_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `body` | s | (no docstring) | - | 38 |

### tools/recipes/stage_d1_ring_p4_s02.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4_s02_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `body` | s | (no docstring) | - | 35 |

### tools/recipes/stage_d1_ring_p4_s02v18.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4_s02v18_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `body` | s | (no docstring) | - | 33 |

### tools/recipes/stage_d1_ring_p4_s03v18.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4_s03v18_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `body` | s | (no docstring) | - | 33 |

### tools/recipes/stage_d1_ring_p4_s04v18.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4_s04v18_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `body` | s | (no docstring) | - | 34 |

### tools/recipes/stage_d1_ring_p4_s05v18.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4_s05v18_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `body` | s | (no docstring) | - | 33 |

### tools/recipes/stage_d1_ring_p4_s06v18.py

recipe imported by another file; imported by 2 file(s): `tools/bench/diag_c147_a2_1_check.py`, `tools/recipes/stage_d1_ring_p4_s06v18_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `SGBackend` | (class) | LVBackend that KEEPS its last whole-VI read (no extra read; stagexec.LVBackend.read is called exactly as before). | - | 56 |
| `SGBackend.read` |  | (no docstring) | - | 59 |
| `sg_read` | e | (ok, detail) for the deferred op error on SINK: (a) the indicator terminal exists with exactly ONE wire, (b) that wire is the net of | - | 64 |
| `body` | s | (no docstring) | - | 93 |

### tools/recipes/stage_d1_ring_p4_s06v18_scratch.py

recipe imported by another file; imported by 1 file(s): `tools/bench/diag_c147_a2_1_check.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `snap_keep` | target=None | (no docstring) | - | 41 |
| `cg_print` | label, before, after, declared | (no docstring) | - | 45 |
| `x10` |  | The X10 prediction of THIS plan: the pred file's memory_pred.peak_mb, only when the pred is keyed to the plan's md5. | - | 65 |
| `body` | s | (no docstring) | - | 77 |
| `norm_ocr` | s | (no docstring) | - | 88 |
| `elcls` | it | One Error List item -> its class (== prep_c147_a1_3_pred.py elcls): local / cond / sr / input / other:<norm_ocr(raw)>. | - | 95 |
| `el_advisory` | items, pred=None | (rc, report) for one EL read (its items) against the pred: rc 1 only for an unseen class or /total diff/ > EL_TOTAL_TOL; rc 2 when | - | 106 |
| `el_advisory_print` | rc, rep | (no docstring) | - | 126 |
| `el_selftest` |  | Three synthetic reads built from the pred's predicted per-class counts (offline): unseen class -> 1; total +4 -> 1; total +2 known -> 0. | - | 132 |

### tools/recipes/stage_d1_ring_p4_s07v18.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4_s07v18_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `SGBackend` | (class) | LVBackend that KEEPS its last whole-VI read (no extra read; stagexec.LVBackend.read is called exactly as before). | - | 81 |
| `SGBackend.read` |  | (no docstring) | - | 84 |
| `sg_read` | e, d | (ok, detail) for the deferred op error on sink d['sink']: (a) the indicator terminal exists with exactly ONE wire, (b) that wire is the | - | 89 |
| `body` | s | (no docstring) | - | 123 |

### tools/recipes/stage_d1_ring_p4_s08v18.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4_s08v18_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `SGBackend` | (class) | LVBackend that KEEPS its last whole-VI read (no extra read; stagexec.LVBackend.read is called exactly as before). | - | 81 |
| `SGBackend.read` |  | (no docstring) | - | 84 |
| `sg_read` | e, d | (ok, detail) for the deferred op error on sink d['sink']: (a) the indicator terminal exists with exactly ONE wire, (b) that wire is the | - | 89 |
| `body` | s | (no docstring) | - | 123 |

### tools/recipes/stage_d1_ring_p4_s09v18.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4_s09v18_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `SGBackend` | (class) | LVBackend that KEEPS its last whole-VI read (no extra read; stagexec.LVBackend.read is called exactly as before). | - | 83 |
| `SGBackend.read` |  | (no docstring) | - | 86 |
| `sg_read` | e, d | (ok, detail) for the deferred op error on sink d['sink']: (a) the indicator terminal exists with exactly ONE wire, (b) that wire is the | - | 91 |
| `body` | s | (no docstring) | - | 125 |

### tools/recipes/stage_d1_ring_p4s1.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4s1_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `body` | s | (no docstring) | - | 33 |

### tools/recipes/stage_d1_ring_p5s01a.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p5s01a_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `SGBackend` | (class) | LVBackend that KEEPS its last whole-VI read (no extra read; stagexec.LVBackend.read is called exactly as before). | - | 82 |
| `SGBackend.read` |  | (no docstring) | - | 85 |
| `sg_read` | e, d | (ok, detail) for the deferred op error on sink d['sink']: (a) the indicator terminal exists with exactly ONE wire, (b) that wire is the | - | 90 |
| `body` | s | (no docstring) | - | 124 |

### tools/recipes/stage_d1_s1.py

recipe imported by another file; imported by 4 file(s): `tools/bench/c53_astcheck.py`, `tools/bench/verify_d1_s2.py`, `tools/recipes/stage_d1_s2_loops.py`, `tools/recipes/stage_d1_s3_focus.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `Stop` | (class) | (no docstring) | - | 254 |
| `gate` | name, ok, detail='', fatal=True | Every gate in this file is FATAL by default: the first FAIL stops the chain and leaves its artefacts. | - | 258 |
| `fact` | line | (no docstring) | - | 267 |
| `md5` | p | (no docstring) | - | 272 |
| `labview_pid` |  | The LabVIEW process id, read EXACTLY the way 'tools/bench/bench_prep.py:64-70' reads its handle count — | - | 280 |
| `version_bytes` | path | CLAUDE.md §1's saved-version audit, WITHOUT assuming an offset: return the first 64 bytes as hex and every | - | 293 |
| `file_facts` | tag, path | md5 + size + version bytes of one artefact, recorded and logged in one place. | - | 303 |
| `fresh` | tag | A FRESH LabVIEW instance (standing restart authority, CLAUDE.md §3), then rebind every cached proxy. | - | 317 |
| `Preload` | (class) | 'tools/bench/p2_open_copy.py:22-28' verbatim: hold the ORIGINAL resident READ-ONLY for the duration of a | - | 332 |
| `dump` |  | Both artefacts are written from the SAME accumulator, and are re-written in 'main''s 'finally', so a fatal | - | 360 |
| `orig_gate` | phase | Rule 1, after EVERY phase: the ORIGINAL's md5 still equals the pin. FATAL. | - | 369 |
| `cold_subvi_table` | tag, target | ONE COLD SubVI-path census of 'target', in ITS OWN CHILD PROCESS and its OWN fresh LabVIEW instance. | - | 377 |
| `compare_subvi_tables` | got, reference, expect_missing | 'got' must be 'reference' MINUS 'expect_missing', key-for-key, in BOTH name and path. | - | 408 |
| `log_table_diff` | label, cmp_ | The FULL diff, printed line by line. Called only when a comparison fails — nothing is elided. | - | 430 |
| `phase_a` |  | NO DIAGRAM EDIT OF ANY KIND. The only question is whether 'g.save()' (default 'allow_broken') completes on | - | 451 |
| `phase_b` |  | Does the SAVED arm still call exactly the subVIs the ORIGINAL calls? | - | 495 |
| `phase_c` |  | The stage itself: a fresh copy of the ORIGINAL, the two FIXTURE TIFF nodes cut, the copy SAVED. | - | 612 |
| `phase_d` |  | The saved artefact is re-read in a FRESH instance under BOTH conditions. This is the half of Pre-decided | - | 695 |
| `main` |  | (no docstring) | - | 763 |

### tools/recipes/stage_d1_s3_focus.py

recipe imported by another file; imported by 1 file(s): `tools/bench/c53_astcheck.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `Stop` | (class) | (no docstring) | - | 287 |
| `gate` | name, ok, detail='', fatal=True | 37(i), 'docs/cycle27-plan.md:1132-1139': the DOCUMENTED format is '  FAIL  ' / '  PASS  ', which | - | 291 |
| `fact` | line | (no docstring) | - | 303 |
| `probe` | tag, path | (no docstring) | - | 308 |
| `dump` | phase=None | (no docstring) | - | 315 |
| `term_state` | r | WIRED / BARE / UNREAD for ONE 'node_terms_uid' row. | - | 327 |
| `node_state` | tag, target, uid, expect_owner=None, quiet=False | The live state of ONE node, addressed BY uid and re-resolved at the call site (34(h) / 37(b)): | - | 346 |
| `term_index` | rec, name, want_i, is_source=None | The LIVE terminal index for a (name, recorded index) pair. The NAME is the address; 'want_i' is only the | - | 391 |
| `cond_read` | tag, target, loop_uid | ONE conditional-terminal readback through 'OpLoopEndRef_v0', scored on its FOUR per-property error | - | 403 |
| `census` | tag, target | (no docstring) | - | 419 |
| `load_rewire_rows` |  | The 17 '"dest": "1.5"' rows of the MEASURED cut-terminal table, straight from the file. | - | 426 |
| `phase_0_files` |  | (no docstring) | - | 438 |
| `phase_1_baseline` |  | (no docstring) | - | 459 |
| `phase_2_move` |  | (no docstring) | - | 538 |
| `phase_3_shift_regs` |  | (no docstring) | - | 570 |
| `phase_4_rewire` |  | (no docstring) | - | 666 |
| `phase_5_cross` |  | (no docstring) | - | 708 |
| `phase_6_acceptance` |  | (no docstring) | - | 742 |
| `phase_7_save` |  | (no docstring) | - | 776 |
| `phase_8_verify` |  | (no docstring) | - | 791 |
| `main` |  | (no docstring) | - | 860 |
| `salvage` |  | CLAUDE.md "a step is not done until it has left a file": if a FATAL gate stopped the run before PHASE 7, | - | 883 |

### tools/recipes/stage_template_ring.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_template_ring_scratch.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `body` | s | (no docstring) | - | 39 |

### tools/hooks/guard_assign.py

hook - reference; imported by 4 file(s): `tools/bench/selftest_assign_flow.py`, `tools/bench/selftest_c148_guard_fp.py`, `tools/cycle_runner.py`, `tools/hooks/guard_session.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `role` |  | (no docstring) | - | 56 |
| `load_config` | path=None | (no docstring) | - | 60 |
| `state_load` | path | (no docstring) | - | 73 |
| `state_save` | path, d | (no docstring) | - | 82 |
| `open_decisions_count` | path | (no docstring) | - | 90 |
| `new_state` | path, cycle, rnd, purpose, next_md5, decisions_path, t0=None | Written by the runner before it spawns the assignment session. | - | 99 |
| `classify` | res, card_path=None | (explained_kind / None, class_key) for a FAIL/BLOCKED result/1 dict. Fails CLOSED: any classifier error -> unexplained. | - | 131 |
| `result_of` | entry | The result/1 dict beside the entry's card, written after the dispatch, or None. | - | 160 |
| `card_rows` | st | (no docstring) | - | 176 |
| `usd_estimate` | transcript_path, prices | USD of the session so far: its transcript + <stem>/subagents/*.jsonl (nested agents land there too - measured | - | 201 |
| `evaluate` | st, cfg, now=None, usd=None | {'trigger', 'detail'} for the first hand-back condition that holds over the session's results, or None. | - | 237 |
| `scope_match` | card_ids, purpose_ids | (no docstring) | - | 282 |
| `card_outside` | card, purpose, cfg | (c): '' or the reason this card leaves the purpose's plan. | - | 294 |
| `cards_dir` |  | The one directory whose cards guard_assign evaluates: tools/bench/cards (env ASSIGN_CARDS_DIR overrides, for a | - | 369 |
| `card_in_cards_dir` | cpath | (no docstring) | - | 375 |
| `check_dispatch` | st_path, sub, card, cpath, transcript_path=None, now=None, cfg=None | (0, '') allow - the dispatch is recorded in the state; (2, text) refuse. Runs under guard_session's lock. | - | 384 |
| `runner_verdict` | st_path, result_path, envelope_usd=None, rc=0, cfg=None, now=None | After the session: (outcome 'PURPOSE_MET'/'HANDBACK', trigger/None, detail, result dict/None). The hook's sticky | - | 450 |

### tools/hooks/guard_bash.py

hook - reference; imported by 13 file(s): `tools/bench/diag_c106d_jevrc2.py`, `tools/bench/diag_c130_2_baseline.py`, `tools/bench/diag_c144_a2_3_stoprec.py`, `tools/bench/selftest_c103d_hooks.py`, `tools/bench/selftest_c110_launchgate.py`, `tools/bench/selftest_c121_3_gatefp.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `note` | marked, cmd | One line per marked run and per refusal, so audit_cycle.py can count judgement-session bypasses. | - | 76 |
| `material_gate` | cmd | 0 = pass, 2 = refuse. See the docstring's SECOND RULE. | - | 90 |
| `motor_gate_check` | cmd | 0 = pass, 2 = refuse. See the THIRD RULE above. Deliberately NOT disabled by LV_GUARD_OFF or BENCH_CELL: | - | 145 |
| `stop_gate` | cmd, shell=None | 0 = pass, 2 = refuse. One call, no logic duplicated - see tools/stop_record.py. | - | 327 |
| `prerun_gate` | cmd | 0 = pass, 2 = refuse. The decision lives in tools/stage_prerun.py check_launch() (argv parsing + records). | - | 364 |
| `scope_gate` | cmd | 0 = pass, 2 = refuse: a launched tools/ script without a valid scope header, or a .py that does not compile | - | 387 |
| `retro_closes` | cmd, data | True when this retrospective launch really closes the session's cycle (see main). | - | 402 |
| `next_md5` | status_path | md5 of STATUS.md's '## NEXT' section (stripped), or '' when the file/section is missing. | - | 430 |
| `next_json_state` | root | (md5 of tools/bench/next.json bytes / 'absent', why-invalid / None). Session protocol v1 C7: the machine copy | - | 441 |
| `next_gate` |  | Refuse a retrospective launch until the cycle has written a NEW, VALID 'tools/bench/next.json'. | - | 456 |
| `jev_advisories` | cmd, data | ADVISORY ONLY. Returns the lines it printed (for the self-test); main() ignores them. Never raises. | - | 545 |
| `main` |  | RETRY CAP (user 2026-09-24, card chat-D). This hook only CHECKS the cap (prerun_gate -> check_launch). It no | - | 583 |

### tools/hooks/guard_card.py

hook - reference; imported by 4 file(s): `tools/bench/selftest_c111c_launchunit.py`, `tools/bench/selftest_c116a_landed.py`, `tools/bench/selftest_errorlist_reuse_81.py`, `tools/hooks/guard_bash.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `log` | line | (no docstring) | - | 27 |
| `pure_selftest` | cmd | True only for THIS project's tools/stagexec.py (relative 'tools/stagexec.py' or its absolute path), and a | - | 67 |
| `decide` | payload | (exit_code, message). Shared by main() and guard_bash.py. | - | 107 |
| `main` |  | (no docstring) | - | 132 |

### tools/hooks/guard_cycle.py

hook - reference; imported by 24 file(s): `tools/bench/c19_close_release_probe.py`, `tools/bench/c20_release_probe.py`, `tools/bench/c22_v1_gate_probe.py`, `tools/bench/chk_fixed_c69.py`, `tools/bench/diag_c112c_release.py`, `tools/bench/diag_c129_8_pagate.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `review_time` | path, body | (instant, basis) - the moment the review's findings existed, which a fix must post-date. | - | 99 |
| `fixed_citations` | path, body | (slugs, cited_paths, rejected) for the VALID 'FIXED:' lines of one review. | - | 126 |
| `fixed_claim` | path, body, target | (claimed, released, why) for ONE file cited by ONE review - CLAUDE.md:449's conditions, per citation. | - | 170 |
| `fixed_slugs` | path, body | Slugs released by a VALID 'FIXED:' line, and the rejected lines with the reason each was rejected. | - | 216 |
| `released_slugs` | path, body | (released, rejected) - the ONE definition of "which slugs does this review file release?". | - | 231 |
| `stamp` | p | A timestamp a BULK EDIT cannot inflate (user's instruction, 2026-09-16: "고칠 것") - and that a RE-ARCHIVE | - | 273 |
| `newest_build_log` |  | (no docstring) | - | 323 |
| `newest_retrospective` |  | The newest retrospective THAT ACTUALLY RETURNED AN ANSWER. | - | 339 |
| `running_review_recipes` | body | card chat-P1 1(c): the normcase'd absolute recipe paths the LAST 'BGRUN START' line of a prior-art log names with | - | 366 |
| `recipe_named_logs` | fp | card 148-a1-1 (fp-59): BENCH logs the recipe ASSIGNS as its own log ('LOG = ...'/'RUN_LOG = ...' holding a string | - | 383 |
| `premature_build` | cmd | THE DEVICE FOR 'premature-build' (docs/violation-decisions.md, 2026-09-16 19:16, round 3). | selftest_guard_cycle_fixed.py | 410 |
| `block` | msg | (no docstring) | - | 648 |
| `offline_only` | cmd | card 112-1 T6: True when EVERY segment of 'cmd' that BUILD_RE matches is 'stage_prerun.py --dry/--prerun' | - | 653 |
| `main` |  | (no docstring) | - | 665 |

### tools/hooks/guard_peer.py

hook - reference; imported by 25 file(s): `tools/bench/c125_1_probe.py`, `tools/bench/diag_c131_2_offline.py`, `tools/bench/diag_c144_3_check.py`, `tools/bench/diag_c146_a1_1_repro.py`, `tools/bench/jev_gate.py`, `tools/bench/jev_gatecheck_c68.py` ...

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `report_waiter_only` | cmd | (no docstring) | - | 103 |
| `log_failure` | text, mtime=None | (failed, first failure line) for the LAST run of a WHOLE log text - protocol.log_verdict with this hook's | - | 168 |
| `log_failure_file` | path | (no docstring) | - | 202 |
| `script_touches_labview` | script, _seen=None | v2 (card 131-2): True when the LAUNCHED 'script' can open LabVIEW - rules in the block above. FAILS CLOSED. | - | 390 |
| `script_touches_labview_v1` | script, _seen=None | v1, KEPT for comparison only (diag_c131_2_offline.py): True when 'script' (a path) or any PROJECT module it | - | 407 |
| `selftest_exempt` | start_line | True when a bgrun START line's run is a PURE-PYTHON self-test: every in-scope script in python command position | - | 437 |
| `in_prediction_scope` | start_line | True when a bgrun START line's command runs a tools/recipes/*.py or tools/bench/*.py script (not a Jev one). | - | 471 |
| `is_jev_ledger` | p | True for tools/bench/jev_*.log/.jsonl (BENCH resolved at call time, so a self-test's redirected BENCH counts). | - | 493 |
| `newest_failing_log` |  | (no docstring) | - | 501 |
| `superseded_by_rerun` | path, mtime, last | gate-fp fp-16 (card 130-2): a failing log whose LAST run's command is IDENTICAL (byte for byte after bgrun's | - | 570 |
| `offline_command` | cmd | True when every python script 'cmd' launches (protocol._launched_scripts) is the bgrun wrapper, an OFFLINE_MODES | - | 604 |
| `offline_new_problem` | ladder_line, text | gate-fp fp-44 / fp-46 (card 146-a1-1): '<script> labview none / hardware none' when 'ladder_line' is a JEV-LADDER | - | 638 |
| `offline_card` | payload, cmd | The card id when the CALLER is a sub-agent bound to a task/1 card with flags.labview == 'none' and 'cmd' is | - | 666 |
| `offline_cmd_lv_card` | payload, cmd, log_path | gate-fp fp-10 (card 125-1), the REVERSE of offline_card: (card id, labview flag) when the caller is bound to a card | - | 684 |
| `other_card_log` | payload, log_path, text=None | card chat-E3 (fp-36): (caller's card id, owner card id) when the caller is bound to a card and the failing log was | - | 707 |
| `failure_names` | path, text | The names a peer exchange must mention to count as a review OF this failure: the log's basename and every | - | 727 |
| `review_quality` | body | (ok, reason) - why this archived exchange does or does not count as a failed-prediction review. | - | 770 |
| `newest_bound_peer` | after_mtime, names | A peer archive file newer than 'after_mtime' that names the failure AND counts as a review. | - | 795 |
| `undisposed` | kind | The newest archived review of 'kind' whose disposition section is missing, empty or still the placeholder. | - | 838 |
| `log_script` | text | The script name a log's LAST run was started on, '_v\d+' stripped - or None. | - | 885 |
| `review_subject_scripts` | body | The set of script stems ('_v\d+' stripped) this review was dispatched ABOUT - empty when it names none. | - | 916 |
| `review_names_script` | body, stem | True when this archive's SUBJECT script (review_subject_scripts) is exactly 'stem', '_v\d+' stripped. | - | 930 |
| `same_row_review` | log_path, text, now=None | (review path, script stem, age in minutes) for the NEWEST accepted review of this failing log's own | - | 936 |
| `gaterow_advisory` | path | Print and log the per-row verdicts of the failing run. Returns the lines; the caller ignores them. | - | 1025 |
| `cite_same_row` | review_path, log_name, ts | Write 'SAME-ROW: <log> (<ts>)' into the review's disposition section, ONCE per log. | - | 1056 |
| `warm` | path | '--warm <log>': finish the Jev rungs for this log outside the hook, so their caches answer the retry. | - | 1154 |
| `main` |  | (no docstring) | - | 1169 |

### tools/hooks/guard_session.py

hook - reference; imported by 6 file(s): `tools/bench/selftest_c148_assign_leak.py`, `tools/bench/selftest_chat_p1.py`, `tools/bench/selftest_chat_p2.py`, `tools/bench/selftest_guard_session.py`, `tools/bench/selftest_guard_session_pairing.py`, `tools/hooks/guard_bash.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `in_cycle` |  | (no docstring) | - | 94 |
| `last_context_tokens` | transcript_path | Tokens the chat's last assistant turn sent as input (input + cache creation + cache read), read from the | - | 98 |
| `chat_context_refusal` | data | (f) The chat's bound: refuse a counted dispatch once its context passed CHAT_CONTEXT_LIMIT. '' = allow. | - | 123 |
| `session_id` | data=None | (no docstring) | - | 138 |
| `state_path` | sid | (no docstring) | - | 146 |
| `load` | sid | (no docstring) | - | 150 |
| `save` | sid, d | (no docstring) | - | 163 |
| `mark_retro_done` | sid | Called by tools/hooks/guard_bash.py when it sees the retrospective being run in this session. | - | 172 |
| `card_of_prompt` | prompt | (card dict / None, card abs path / None) for a 'CARD <path>' prompt. An unreadable card -> ({}, path). | - | 196 |
| `prune_live` | live, now=None | The entries still live: no result_<id>.json newer than the dispatch beside the card, and younger than | - | 211 |
| `card_writes` | card | (g) flags.write of a card dict as a list; None for an unreadable card ({}), which the caller treats as | - | 230 |
| `tool_hits` | globs | (g) the STAGE_TOOLS a write-glob list reaches. None (unknown writes) reaches all of them. | - | 239 |
| `pairing_refusal` | cid, lv, writes, live | (g) refusal text for dispatching card 'cid' (labview 'lv', write globs 'writes') beside the 'live' entries, | - | 247 |
| `send_message_refusal` | data | (c) NO RESUME BY SendMessage IN A CYCLE SESSION (docs/violation-decisions.md "repeated-failure-class - | - | 286 |
| `main` |  | (no docstring) | - | 307 |
| `escalation_refusal` | sub, card, cpath | (no docstring) | - | 357 |
| `cycle_role` |  | (h) '' (legacy / chat) / 'judgement' / 'assign' - only inside a runner cycle session. | - | 379 |
| `decide` | sid, sub, ti, data=None | The counted-dispatch decision, run under the session-state lock. 0 allow / 2 refuse. | - | 400 |

### tools/hooks/guard_write.py

hook - reference; imported by 4 file(s): `tools/bench/diag_c146_a1_1_repro.py`, `tools/bench/replay_c_e3_142_143.py`, `tools/bench/selftest_c148_guard_fp.py`, `tools/bench/selftest_c_e3.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `resumed_card_ids` | names | card 148-a1-1 (fp-57): ids of cards a LATER card took over - a task card that HAS a result file and names the id in | - | 49 |
| `open_card_pins` | path | ['card <id> pins <rel> at <md5>, disk is now <md5>'] for open cards (no result file yet) whose inputs name | - | 77 |
| `check_script` | path | (no docstring) | - | 131 |
| `check_json` | path | (no docstring) | - | 151 |
| `check_review` | path | (no docstring) | - | 177 |
| `decide` | path | [problems] for one written file (empty = clean). | - | 202 |
| `capabilities_regen` | path | 'started' / 'rerun-flagged' / 'not-shared' / 'no-cache' / 'spawn-failed: ...' for one written path (module comment above). | selftest_t7_capabilities.py | 228 |
| `main` |  | (no docstring) | - | 269 |

### tools/hooks/report_gate.py

hook - reference; imported by 2 file(s): `tools/bench/selftest_report_gate_fp31.py`, `tools/wait_runner_event.py`

| function | arguments | what it does | self-test | line |
|---|---|---|---|---|
| `newest_runner_log` |  | (no docstring) | - | 39 |
| `logs_to_read` |  | fp-31 (cycle 135): the supervisor relaunches the runner at its budget, and the OLD runner then writes its last | - | 55 |
| `events` |  | (newest log, [(md5, line), ...]) over every log logs_to_read() names; a line seen twice counts once. | - | 76 |
| `load_ack` |  | (no docstring) | - | 92 |
| `unreported` |  | (no docstring) | - | 96 |
| `decisions_block` | path=None | The OPEN user decisions (tools/bench/decisions_pending.json, schema decisions-pending/1) that every cycle-end | - | 102 |
| `ack` |  | (no docstring) | - | 123 |
| `main` |  | (no docstring) | - | 132 |

<!-- GENERATED fn-list END -->
