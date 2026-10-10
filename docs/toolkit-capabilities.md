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

Outcome of every call: `ok | no_output | failed | timed_out` (tools/fncontract.py). Contract column = the declared postconditions `[measure, on_fail]` or `none - <reason>`. Record = tools/bench/fn_records/ (fresh-pass only while the function's source md5 equals the record's). 152 rows; records: fresh-fail 3, fresh-pass 54, none 66, planned 24, stale 5.

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
| `stagekit.op:add_shift_reg` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.add_shift_reg) | fresh-pass | tools/stagekit.py:782 |
| `stagekit.op:case_frame_wire` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.case_frame_wire) | planned | tools/stagexec.py:3623 |
| `stagekit.op:case_in` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.case_in) | planned | tools/stagexec.py:3353 |
| `stagekit.op:case_wired` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.case_wired) | planned | tools/stagexec.py:3353 |
| `stagekit.op:connect` | (Stage._op verb) | none - gscript.connect_nested_v2 raises at entry (its op VI was never built); the live route is op:connect_nested_v1 | planned | tools/stagekit.py:719 |
| `stagekit.op:connect_from_wire` | (Stage._op verb) | none at this level - recipes.build_opconnectfromwire_v0.connect_from_wire returns its readout; LVBackend._cfw stops on its err / wire delta | fresh-pass | tools/stagekit.py:726 |
| `stagekit.op:connect_nested_v1` | (Stage._op verb) | none at this level - recipes.build_opconnectnested_v1.connect_nested_v1 returns (wire delta, ExecState, err); LVBackend.connect stops on err | stale | tools/stagekit.py:1101 |
| `stagekit.op:connect_term_uid` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.connect_term_uid) | stale | tools/stagexec.py:3649 |
| `stagekit.op:connect_terminals` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.connect_terminals) | planned | tools/stagekit.py:1101 |
| `stagekit.op:copy_in` | (Stage._op verb) | none at this level - the copied object is bound by stagexec's next read (bind_new) | planned | tools/stagekit.py:925 |
| `stagekit.op:create_const_on_term` | (Stage._op verb) | none at this level - OpCreateConstOnTerm_v0's readout; bound by the next read | fresh-pass | tools/stagekit.py:979 |
| `stagekit.op:create_local_read` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.create_local_read) | fresh-pass | tools/stagekit.py:794 |
| `stagekit.op:create_local_write` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.create_local_write) | fresh-pass | tools/stagekit.py:817 |
| `stagekit.op:create_primitive_nested` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.create_primitive_nested) | fresh-pass | tools/stagexec.py:3353 |
| `stagekit.op:delete_object` | (Stage._op verb) | removed == 1 [inline, raise] | fresh-pass | tools/stagekit.py:700 |
| `stagekit.op:delete_wire` | (Stage._op verb) | found == 1 [inline, raise] | fresh-pass | tools/stagekit.py:687 |
| `stagekit.op:drop_subvi` | (Stage._op verb) | none at this level - stagexec create 'subvi' measures the SubVI uid diff | fresh-pass | tools/stagexec.py:3353 |
| `stagekit.op:fs_add_frame` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.fs_add_frame) | planned | tools/stagexec.py:3353 |
| `stagekit.op:indicator_nested` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.create_indicator_nested) | fresh-pass | tools/stagexec.py:3353 |
| `stagekit.op:indicator_on_const` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.create_indicator_on_const) | fresh-pass | tools/stagexec.py:3353 |
| `stagekit.op:loop_in` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.loop_in) | fresh-pass | tools/stagexec.py:3353 |
| `stagekit.op:move_in` | (Stage._op verb) | none at this level - recipes.build_d1_v0.move_in; the new owner is read by stagexec's step diff | fresh-pass | tools/stagekit.py:713 |
| `stagekit.op:queue_node` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.queue_node) | planned | tools/stagexec.py:3353 |
| `stagekit.op:set_index_mode` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.set_index_mode) | planned | tools/stagexec.py:3709 |
| `stagekit.op:stop_from_node` | (Stage._op verb) | none - OpStopFromNode_v0's error string is returned; the step diff checks the new wire | fresh-pass | tools/stagexec.py:3569 |
| `stagekit.op:struct_copy_nested` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.struct_copy_nested) | fresh-pass | tools/stagexec.py:3353 |
| `stagekit.op:wire_const` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.wire_const) | planned | tools/stagexec.py:3216 |
| `stagekit.op:wire_const_sr` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.wire_const_sr) | stale | tools/stagexec.py:3216 |
| `stagekit.op:wire_control` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.wire_control) | stale | tools/stagexec.py:3216 |
| `stagekit.op:wire_ctlsink` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.wire_ctlsink) | stale | tools/stagexec.py:3216 |
| `stagekit.op:wire_indicators` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.wire_indicators) | fresh-fail | tools/stagekit.py:773 |
| `stagekit.op:wire_remove_loose_ends` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.wire_remove_loose_ends) | fresh-pass | tools/stagexec.py:3692 |
| `stagekit.op:wire_sr` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.wire_sr) | fresh-pass | tools/stagekit.py:788 |
| `stagekit.op:wire_tunouter` | (Stage._op verb) | none at this level - measured by the gscript function it calls (row gscript.wire_tunouter) | planned | tools/stagexec.py:3216 |

<!-- GENERATED fn-table END -->

<!-- GENERATED fn-list BEGIN (tools/gen_capabilities.py - every public function of every SHARED tools file, by import graph; do not edit by hand) -->

## Every public function of the shared tools files - generated from code (card chat-T7)

A file is SHARED when at least one OTHER file under tools/ imports it (import graph, measured at generation; cache tools/bench/capabilities_shared.json). Look here before writing any logic (docs/script-writing.md rule 8). 209 files, 2630 functions: 1429 described by a docstring, 304 by docs/fn_descriptions.json (existing functions, card chat-T8), 897 undocumented (per file in the table below). Regenerated at every cycle end and when a shared file is written.

| file | kind | imported by | functions | side file | undocumented |
|---|---|---|---|---|---|
| [`tools/addrcheck.py`](#tools-addrcheck-py) | shared module | 14 | 17 | 1 | 0 |
| [`tools/allterms.py`](#tools-allterms-py) | shared module | 73 | 5 | 1 | 0 |
| [`tools/audit_cycle.py`](#tools-audit-cycle-py) | shared module | 8 | 15 | 3 | 0 |
| [`tools/bgrun.py`](#tools-bgrun-py) | shared module | 1 | 4 | 1 | 0 |
| [`tools/bgrun_reap.py`](#tools-bgrun-reap-py) | shared module | 3 | 5 | 2 | 0 |
| [`tools/card_clock.py`](#tools-card-clock-py) | shared module | 3 | 4 | 3 | 0 |
| [`tools/census_predict.py`](#tools-census-predict-py) | shared module | 46 | 7 | 4 | 0 |
| [`tools/cycle_runner.py`](#tools-cycle-runner-py) | shared module | 15 | 53 | 19 | 0 |
| [`tools/debate_loop.py`](#tools-debate-loop-py) | shared module | 1 | 10 | 0 | 0 |
| [`tools/debate_relay.py`](#tools-debate-relay-py) | shared module | 2 | 12 | 0 | 8 |
| [`tools/dispo.py`](#tools-dispo-py) | shared module | 4 | 3 | 0 | 0 |
| [`tools/doc_lint.py`](#tools-doc-lint-py) | shared module | 8 | 26 | 14 | 0 |
| [`tools/elrule.py`](#tools-elrule-py) | shared module | 35 | 10 | 1 | 0 |
| [`tools/errorlist_check.py`](#tools-errorlist-check-py) | shared module | 77 | 24 | 10 | 0 |
| [`tools/fn_records.py`](#tools-fn-records-py) | shared module | 6 | 19 | 9 | 0 |
| [`tools/fncontract.py`](#tools-fncontract-py) | shared module | 6 | 20 | 3 | 0 |
| [`tools/gate_fp.py`](#tools-gate-fp-py) | shared module | 8 | 10 | 3 | 0 |
| [`tools/gateclass.py`](#tools-gateclass-py) | shared module | 13 | 14 | 3 | 0 |
| [`tools/gen_capabilities.py`](#tools-gen-capabilities-py) | shared module | 7 | 21 | 0 | 0 |
| [`tools/gscript.py`](#tools-gscript-py) | shared module | 653 | 135 | 9 | 0 |
| [`tools/hash_probe.py`](#tools-hash-probe-py) | shared module | 64 | 2 | 2 | 0 |
| [`tools/invcheck.py`](#tools-invcheck-py) | shared module | 9 | 7 | 0 | 0 |
| [`tools/jev.py`](#tools-jev-py) | shared module | 33 | 10 | 2 | 0 |
| [`tools/jev_candidates.py`](#tools-jev-candidates-py) | shared module | 107 | 15 | 3 | 0 |
| [`tools/jev_chain.py`](#tools-jev-chain-py) | shared module | 1 | 8 | 5 | 0 |
| [`tools/jev_contradict.py`](#tools-jev-contradict-py) | shared module | 3 | 4 | 1 | 0 |
| [`tools/jev_device_value.py`](#tools-jev-device-value-py) | shared module | 2 | 4 | 4 | 0 |
| [`tools/jev_drift.py`](#tools-jev-drift-py) | shared module | 4 | 6 | 0 | 0 |
| [`tools/jev_gaterow.py`](#tools-jev-gaterow-py) | shared module | 10 | 3 | 1 | 0 |
| [`tools/jev_pairs.py`](#tools-jev-pairs-py) | shared module | 7 | 14 | 8 | 0 |
| [`tools/jev_preflight.py`](#tools-jev-preflight-py) | shared module | 3 | 5 | 1 | 0 |
| [`tools/jev_rowcheck.py`](#tools-jev-rowcheck-py) | shared module | 3 | 8 | 1 | 0 |
| [`tools/launchunit.py`](#tools-launchunit-py) | shared module | 7 | 10 | 0 | 0 |
| [`tools/lint.py`](#tools-lint-py) | shared module | 1 | 8 | 2 | 0 |
| [`tools/logclass.py`](#tools-logclass-py) | shared module | 17 | 9 | 0 | 0 |
| [`tools/lv_errorlist.py`](#tools-lv-errorlist-py) | shared module | 5 | 25 | 12 | 0 |
| [`tools/lvclick.py`](#tools-lvclick-py) | shared module | 4 | 18 | 0 | 10 |
| [`tools/motor_gate.py`](#tools-motor-gate-py) | shared module | 3 | 21 | 0 | 9 |
| [`tools/outcome_review.py`](#tools-outcome-review-py) | shared module | 3 | 6 | 0 | 3 |
| [`tools/prior_art_review.py`](#tools-prior-art-review-py) | shared module | 2 | 7 | 0 | 2 |
| [`tools/priorart_diff.py`](#tools-priorart-diff-py) | shared module | 8 | 8 | 0 | 5 |
| [`tools/protocol.py`](#tools-protocol-py) | shared module | 665 | 63 | 14 | 0 |
| [`tools/retro_due.py`](#tools-retro-due-py) | shared module | 2 | 6 | 0 | 2 |
| [`tools/retrospective.py`](#tools-retrospective-py) | shared module | 2 | 8 | 0 | 2 |
| [`tools/rules_coverage.py`](#tools-rules-coverage-py) | shared module | 2 | 11 | 0 | 6 |
| [`tools/run_mode.py`](#tools-run-mode-py) | shared module | 1 | 3 | 3 | 0 |
| [`tools/scope_header.py`](#tools-scope-header-py) | shared module | 14 | 21 | 8 | 0 |
| [`tools/stage_prerun.py`](#tools-stage-prerun-py) | shared module | 230 | 127 | 29 | 0 |
| [`tools/stage_shared.py`](#tools-stage-shared-py) | shared module | 20 | 3 | 0 | 0 |
| [`tools/stagekit.py`](#tools-stagekit-py) | shared module | 328 | 143 | 10 | 0 |
| [`tools/stagesim.py`](#tools-stagesim-py) | shared module | 194 | 68 | 25 | 0 |
| [`tools/stagexec.py`](#tools-stagexec-py) | shared module | 388 | 190 | 61 | 0 |
| [`tools/stop_record.py`](#tools-stop-record-py) | shared module | 31 | 19 | 0 | 2 |
| [`tools/vigraph.py`](#tools-vigraph-py) | shared module | 172 | 22 | 4 | 0 |
| [`tools/violations.py`](#tools-violations-py) | shared module | 2 | 5 | 0 | 2 |
| [`tools/wiki_build.py`](#tools-wiki-build-py) | shared module | 90 | 11 | 0 | 5 |
| [`tools/bench/bench_prep.py`](#tools-bench-bench-prep-py) | shared file in the bench folder (move to tools/ later) | 299 | 5 | 0 | 4 |
| [`tools/bench/build_opstopmode_v0.py`](#tools-bench-build-opstopmode-v0-py) | shared file in the bench folder (move to tools/ later) | 2 | 24 | 0 | 23 |
| [`tools/bench/build_ringpickslot_v2.py`](#tools-bench-build-ringpickslot-v2-py) | shared file in the bench folder (move to tools/ later) | 1 | 13 | 0 | 13 |
| [`tools/bench/c131_2_reach.py`](#tools-bench-c131-2-reach-py) | shared file in the bench folder (move to tools/ later) | 2 | 1 | 0 | 0 |
| [`tools/bench/c60c_astcheck.py`](#tools-bench-c60c-astcheck-py) | shared file in the bench folder (move to tools/ later) | 2 | 5 | 0 | 3 |
| [`tools/bench/c90c_rows.py`](#tools-bench-c90c-rows-py) | shared file in the bench folder (move to tools/ later) | 2 | 7 | 0 | 1 |
| [`tools/bench/c90d_border.py`](#tools-bench-c90d-border-py) | shared file in the bench folder (move to tools/ later) | 1 | 3 | 0 | 0 |
| [`tools/bench/c90d_reads.py`](#tools-bench-c90d-reads-py) | shared file in the bench folder (move to tools/ later) | 3 | 5 | 0 | 2 |
| [`tools/bench/c90d_table.py`](#tools-bench-c90d-table-py) | shared file in the bench folder (move to tools/ later) | 1 | 1 | 0 | 1 |
| [`tools/bench/camera_contract.py`](#tools-bench-camera-contract-py) | shared file in the bench folder (move to tools/ later) | 1 | 8 | 0 | 5 |
| [`tools/bench/d0_locate.py`](#tools-bench-d0-locate-py) | shared file in the bench folder (move to tools/ later) | 1 | 11 | 0 | 6 |
| [`tools/bench/d1_rewire_map.py`](#tools-bench-d1-rewire-map-py) | shared file in the bench folder (move to tools/ later) | 9 | 3 | 0 | 2 |
| [`tools/bench/diag_c100_verbs_build.py`](#tools-bench-diag-c100-verbs-build-py) | shared file in the bench folder (move to tools/ later) | 4 | 32 | 0 | 27 |
| [`tools/bench/diag_c108c_graph.py`](#tools-bench-diag-c108c-graph-py) | shared file in the bench folder (move to tools/ later) | 1 | 13 | 0 | 9 |
| [`tools/bench/diag_c115d_sel.py`](#tools-bench-diag-c115d-sel-py) | shared file in the bench folder (move to tools/ later) | 1 | 5 | 0 | 3 |
| [`tools/bench/diag_c118_p0.py`](#tools-bench-diag-c118-p0-py) | shared file in the bench folder (move to tools/ later) | 2 | 5 | 0 | 5 |
| [`tools/bench/diag_c138_6_run.py`](#tools-bench-diag-c138-6-run-py) | shared file in the bench folder (move to tools/ later) | 6 | 11 | 0 | 11 |
| [`tools/bench/diag_c153_b2_1_rescore.py`](#tools-bench-diag-c153-b2-1-rescore-py) | shared file in the bench folder (move to tools/ later) | 1 | 4 | 0 | 4 |
| [`tools/bench/diag_c156_b2_2_inv_c156a21.py`](#tools-bench-diag-c156-b2-2-inv-c156a21-py) | shared file in the bench folder (move to tools/ later) | 1 | 0 | 0 | 0 |
| [`tools/bench/diag_c159_f1_2_t2.py`](#tools-bench-diag-c159-f1-2-t2-py) | shared file in the bench folder (move to tools/ later) | 1 | 8 | 0 | 8 |
| [`tools/bench/diag_c61_localdir_write2.py`](#tools-bench-diag-c61-localdir-write2-py) | shared file in the bench folder (move to tools/ later) | 1 | 23 | 0 | 17 |
| [`tools/bench/diag_c81_uidref.py`](#tools-bench-diag-c81-uidref-py) | shared file in the bench folder (move to tools/ later) | 1 | 18 | 0 | 16 |
| [`tools/bench/diag_c83_connect2x2.py`](#tools-bench-diag-c83-connect2x2-py) | shared file in the bench folder (move to tools/ later) | 2 | 26 | 0 | 19 |
| [`tools/bench/diag_c83_connect2x2_r2.py`](#tools-bench-diag-c83-connect2x2-r2-py) | shared file in the bench folder (move to tools/ later) | 1 | 16 | 0 | 15 |
| [`tools/bench/diag_c91_step4_stats.py`](#tools-bench-diag-c91-step4-stats-py) | shared file in the bench folder (move to tools/ later) | 6 | 4 | 0 | 3 |
| [`tools/bench/diag_c94_sites.py`](#tools-bench-diag-c94-sites-py) | shared file in the bench folder (move to tools/ later) | 1 | 3 | 0 | 3 |
| [`tools/bench/diag_d1_execstate_preload.py`](#tools-bench-diag-d1-execstate-preload-py) | shared file in the bench folder (move to tools/ later) | 7 | 8 | 0 | 6 |
| [`tools/bench/diag_donor_census.py`](#tools-bench-diag-donor-census-py) | shared file in the bench folder (move to tools/ later) | 1 | 7 | 0 | 7 |
| [`tools/bench/diag_fstunnel_preclean_twins.py`](#tools-bench-diag-fstunnel-preclean-twins-py) | shared file in the bench folder (move to tools/ later) | 3 | 15 | 0 | 11 |
| [`tools/bench/diag_fstunnel_rbwvictims.py`](#tools-bench-diag-fstunnel-rbwvictims-py) | shared file in the bench folder (move to tools/ later) | 1 | 19 | 0 | 14 |
| [`tools/bench/diag_movein_p1_break.py`](#tools-bench-diag-movein-p1-break-py) | shared file in the bench folder (move to tools/ later) | 3 | 4 | 0 | 3 |
| [`tools/bench/diag_movein_set.py`](#tools-bench-diag-movein-set-py) | shared file in the bench folder (move to tools/ later) | 1 | 10 | 0 | 8 |
| [`tools/bench/diag_queue_donor.py`](#tools-bench-diag-queue-donor-py) | shared file in the bench folder (move to tools/ later) | 1 | 8 | 0 | 7 |
| [`tools/bench/diag_queue_donor2.py`](#tools-bench-diag-queue-donor2-py) | shared file in the bench folder (move to tools/ later) | 3 | 13 | 0 | 8 |
| [`tools/bench/diag_replay_gbtest.py`](#tools-bench-diag-replay-gbtest-py) | shared file in the bench folder (move to tools/ later) | 1 | 6 | 0 | 6 |
| [`tools/bench/diag_replay_lib.py`](#tools-bench-diag-replay-lib-py) | shared file in the bench folder (move to tools/ later) | 9 | 19 | 12 | 0 |
| [`tools/bench/diag_s2_scaffold.py`](#tools-bench-diag-s2-scaffold-py) | shared file in the bench folder (move to tools/ later) | 75 | 15 | 0 | 10 |
| [`tools/bench/diag_s3b_l0_localname_v2.py`](#tools-bench-diag-s3b-l0-localname-v2-py) | shared file in the bench folder (move to tools/ later) | 1 | 23 | 0 | 15 |
| [`tools/bench/diag_tunnelsource_onehop.py`](#tools-bench-diag-tunnelsource-onehop-py) | shared file in the bench folder (move to tools/ later) | 5 | 12 | 0 | 7 |
| [`tools/bench/diag_vigraph_check.py`](#tools-bench-diag-vigraph-check-py) | shared file in the bench folder (move to tools/ later) | 1 | 8 | 0 | 5 |
| [`tools/bench/drive_legguard.py`](#tools-bench-drive-legguard-py) | shared file in the bench folder (move to tools/ later) | 6 | 14 | 0 | 6 |
| [`tools/bench/drive_m8.py`](#tools-bench-drive-m8-py) | shared file in the bench folder (move to tools/ later) | 14 | 5 | 0 | 5 |
| [`tools/bench/drive_original_copy_v2.py`](#tools-bench-drive-original-copy-v2-py) | shared file in the bench folder (move to tools/ later) | 4 | 32 | 0 | 27 |
| [`tools/bench/drive_original_copy_v4.py`](#tools-bench-drive-original-copy-v4-py) | shared file in the bench folder (move to tools/ later) | 3 | 19 | 0 | 6 |
| [`tools/bench/drive_original_copy_v5.py`](#tools-bench-drive-original-copy-v5-py) | shared file in the bench folder (move to tools/ later) | 15 | 11 | 0 | 8 |
| [`tools/bench/fntest_lib.py`](#tools-bench-fntest-lib-py) | shared file in the bench folder (move to tools/ later) | 2 | 24 | 0 | 12 |
| [`tools/bench/ground_bench.py`](#tools-bench-ground-bench-py) | shared file in the bench folder (move to tools/ later) | 1 | 10 | 0 | 10 |
| [`tools/bench/imaqdx_limits.py`](#tools-bench-imaqdx-limits-py) | shared file in the bench folder (move to tools/ later) | 14 | 5 | 0 | 4 |
| [`tools/bench/jev_device_value_labels.py`](#tools-bench-jev-device-value-labels-py) | shared file in the bench folder (move to tools/ later) | 1 | 2 | 0 | 2 |
| [`tools/bench/jev_discharge_trial.py`](#tools-bench-jev-discharge-trial-py) | shared file in the bench folder (move to tools/ later) | 2 | 4 | 0 | 4 |
| [`tools/bench/jev_gate.py`](#tools-bench-jev-gate-py) | shared file in the bench folder (move to tools/ later) | 16 | 20 | 3 | 0 |
| [`tools/bench/jev_gaterow_q.py`](#tools-bench-jev-gaterow-q-py) | shared file in the bench folder (move to tools/ later) | 3 | 2 | 0 | 0 |
| [`tools/bench/jev_next_q.py`](#tools-bench-jev-next-q-py) | shared file in the bench folder (move to tools/ later) | 3 | 0 | 0 | 0 |
| [`tools/bench/jev_priorart_trial.py`](#tools-bench-jev-priorart-trial-py) | shared file in the bench folder (move to tools/ later) | 1 | 1 | 0 | 1 |
| [`tools/bench/jev_triage_q.py`](#tools-bench-jev-triage-q-py) | shared file in the bench folder (move to tools/ later) | 2 | 0 | 0 | 0 |
| [`tools/bench/jev_wave2a_trials.py`](#tools-bench-jev-wave2a-trials-py) | shared file in the bench folder (move to tools/ later) | 1 | 8 | 0 | 7 |
| [`tools/bench/k_contract_79.py`](#tools-bench-k-contract-79-py) | shared file in the bench folder (move to tools/ later) | 42 | 2 | 0 | 2 |
| [`tools/bench/launch_p3b2_c135.py`](#tools-bench-launch-p3b2-c135-py) | shared file in the bench folder (move to tools/ later) | 4 | 14 | 0 | 12 |
| [`tools/bench/launch_p3b2_c135_graph.py`](#tools-bench-launch-p3b2-c135-graph-py) | shared file in the bench folder (move to tools/ later) | 1 | 1 | 0 | 1 |
| [`tools/bench/launch_p3b2_resume_c135_compare.py`](#tools-bench-launch-p3b2-resume-c135-compare-py) | shared file in the bench folder (move to tools/ later) | 3 | 3 | 0 | 1 |
| [`tools/bench/m8_dry.py`](#tools-bench-m8-dry-py) | shared file in the bench folder (move to tools/ later) | 5 | 3 | 0 | 3 |
| [`tools/bench/m8b_replay_compare.py`](#tools-bench-m8b-replay-compare-py) | shared file in the bench folder (move to tools/ later) | 1 | 3 | 0 | 3 |
| [`tools/bench/opmodels_lib.py`](#tools-bench-opmodels-lib-py) | shared file in the bench folder (move to tools/ later) | 3 | 6 | 0 | 3 |
| [`tools/bench/prep_c143_3_elrule.py`](#tools-bench-prep-c143-3-elrule-py) | shared file in the bench folder (move to tools/ later) | 11 | 0 | 0 | 0 |
| [`tools/bench/prep_c156_a1_1_lib.py`](#tools-bench-prep-c156-a1-1-lib-py) | shared file in the bench folder (move to tools/ later) | 41 | 6 | 0 | 1 |
| [`tools/bench/prep_c156_a1_2_lib.py`](#tools-bench-prep-c156-a1-2-lib-py) | shared file in the bench folder (move to tools/ later) | 7 | 8 | 0 | 0 |
| [`tools/bench/prep_c159_c1_1_lib.py`](#tools-bench-prep-c159-c1-1-lib-py) | shared file in the bench folder (move to tools/ later) | 3 | 6 | 0 | 0 |
| [`tools/bench/prep_c164_a2_3_lib.py`](#tools-bench-prep-c164-a2-3-lib-py) | shared file in the bench folder (move to tools/ later) | 19 | 9 | 0 | 2 |
| [`tools/bench/prep_plan_flow_lib.py`](#tools-bench-prep-plan-flow-lib-py) | shared file in the bench folder (move to tools/ later) | 12 | 3 | 0 | 0 |
| [`tools/bench/s1_subvi_paths.py`](#tools-bench-s1-subvi-paths-py) | shared file in the bench folder (move to tools/ later) | 2 | 7 | 0 | 6 |
| [`tools/bench/selftest_assign_flow.py`](#tools-bench-selftest-assign-flow-py) | shared file in the bench folder (move to tools/ later) | 1 | 11 | 0 | 9 |
| [`tools/bench/selftest_c153_poskey_convert.py`](#tools-bench-selftest-c153-poskey-convert-py) | shared file in the bench folder (move to tools/ later) | 3 | 6 | 0 | 0 |
| [`tools/bench/selftest_guard_peer_jev.py`](#tools-bench-selftest-guard-peer-jev-py) | shared file in the bench folder (move to tools/ later) | 1 | 5 | 0 | 3 |
| [`tools/bench/selftest_guard_peer_ladder.py`](#tools-bench-selftest-guard-peer-ladder-py) | shared file in the bench folder (move to tools/ later) | 1 | 6 | 0 | 4 |
| [`tools/bench/selftest_stoprecord_supersession.py`](#tools-bench-selftest-stoprecord-supersession-py) | shared file in the bench folder (move to tools/ later) | 1 | 9 | 0 | 4 |
| [`tools/bench/selftest_t6_poskey.py`](#tools-bench-selftest-t6-poskey-py) | shared file in the bench folder (move to tools/ later) | 4 | 8 | 0 | 5 |
| [`tools/bench/spec_read.py`](#tools-bench-spec-read-py) | shared file in the bench folder (move to tools/ later) | 1 | 3 | 0 | 3 |
| [`tools/bench/subvi_harness.py`](#tools-bench-subvi-harness-py) | shared file in the bench folder (move to tools/ later) | 6 | 2 | 0 | 2 |
| [`tools/bench/t2_rsrc_blockdiff.py`](#tools-bench-t2-rsrc-blockdiff-py) | shared file in the bench folder (move to tools/ later) | 2 | 7 | 0 | 4 |
| [`tools/bench/verify_d1_s2.py`](#tools-bench-verify-d1-s2-py) | shared file in the bench folder (move to tools/ later) | 1 | 9 | 0 | 6 |
| [`tools/recipes/build_d1_m3a1.py`](#tools-recipes-build-d1-m3a1-py) | recipe imported by another file | 25 | 46 | 0 | 23 |
| [`tools/recipes/build_d1_m3a3b_d3.py`](#tools-recipes-build-d1-m3a3b-d3-py) | recipe imported by another file | 4 | 21 | 0 | 17 |
| [`tools/recipes/build_d1_v0.py`](#tools-recipes-build-d1-v0-py) | recipe imported by another file | 182 | 24 | 0 | 16 |
| [`tools/recipes/build_opcaseframes_v0.py`](#tools-recipes-build-opcaseframes-v0-py) | recipe imported by another file | 1 | 5 | 0 | 4 |
| [`tools/recipes/build_opconnectfromwire_v0.py`](#tools-recipes-build-opconnectfromwire-v0-py) | recipe imported by another file | 55 | 12 | 0 | 10 |
| [`tools/recipes/build_opconnectnested_v1.py`](#tools-recipes-build-opconnectnested-v1-py) | recipe imported by another file | 72 | 16 | 0 | 12 |
| [`tools/recipes/build_opconstvalue_v1.py`](#tools-recipes-build-opconstvalue-v1-py) | recipe imported by another file | 59 | 6 | 0 | 5 |
| [`tools/recipes/build_opconstvalue_v1b.py`](#tools-recipes-build-opconstvalue-v1b-py) | recipe imported by another file | 5 | 3 | 0 | 2 |
| [`tools/recipes/build_opconstvalue_v1c.py`](#tools-recipes-build-opconstvalue-v1c-py) | recipe imported by another file | 4 | 4 | 0 | 3 |
| [`tools/recipes/build_opconstvaluen_v0.py`](#tools-recipes-build-opconstvaluen-v0-py) | recipe imported by another file | 1 | 4 | 0 | 4 |
| [`tools/recipes/build_opcreateconstonterm_v0.py`](#tools-recipes-build-opcreateconstonterm-v0-py) | recipe imported by another file | 23 | 15 | 0 | 12 |
| [`tools/recipes/build_opfsinnertunnelconnect_v0.py`](#tools-recipes-build-opfsinnertunnelconnect-v0-py) | recipe imported by another file | 16 | 24 | 0 | 18 |
| [`tools/recipes/build_opfstunnelterm_v0.py`](#tools-recipes-build-opfstunnelterm-v0-py) | recipe imported by another file | 1 | 25 | 0 | 17 |
| [`tools/recipes/build_opfstunnelterm_v1.py`](#tools-recipes-build-opfstunnelterm-v1-py) | recipe imported by another file | 6 | 25 | 0 | 17 |
| [`tools/recipes/build_opfstunnelterm_v2.py`](#tools-recipes-build-opfstunnelterm-v2-py) | recipe imported by another file | 6 | 28 | 0 | 17 |
| [`tools/recipes/build_opownerchain_v1.py`](#tools-recipes-build-opownerchain-v1-py) | recipe imported by another file | 11 | 10 | 0 | 7 |
| [`tools/recipes/build_opsentinel_ops.py`](#tools-recipes-build-opsentinel-ops-py) | recipe imported by another file | 13 | 8 | 0 | 6 |
| [`tools/recipes/build_opstopfromnode_v0.py`](#tools-recipes-build-opstopfromnode-v0-py) | recipe imported by another file | 22 | 17 | 0 | 12 |
| [`tools/recipes/build_optunnelread_v0.py`](#tools-recipes-build-optunnelread-v0-py) | recipe imported by another file | 2 | 6 | 0 | 6 |
| [`tools/recipes/build_opwiresource_v0.py`](#tools-recipes-build-opwiresource-v0-py) | recipe imported by another file | 1 | 7 | 0 | 7 |
| [`tools/recipes/build_opwiresource_v1.py`](#tools-recipes-build-opwiresource-v1-py) | recipe imported by another file | 1 | 6 | 0 | 6 |
| [`tools/recipes/build_opwiresource_v2.py`](#tools-recipes-build-opwiresource-v2-py) | recipe imported by another file | 2 | 5 | 0 | 5 |
| [`tools/recipes/build_opwiresource_v3.py`](#tools-recipes-build-opwiresource-v3-py) | recipe imported by another file | 1 | 5 | 0 | 5 |
| [`tools/recipes/build_opwiresource_v4.py`](#tools-recipes-build-opwiresource-v4-py) | recipe imported by another file | 1 | 5 | 0 | 5 |
| [`tools/recipes/build_opwiresource_v5.py`](#tools-recipes-build-opwiresource-v5-py) | recipe imported by another file | 18 | 5 | 0 | 5 |
| [`tools/recipes/build_opwiresr_v0.py`](#tools-recipes-build-opwiresr-v0-py) | recipe imported by another file | 1 | 20 | 0 | 16 |
| [`tools/recipes/build_track_v6_core.py`](#tools-recipes-build-track-v6-core-py) | recipe imported by another file | 37 | 15 | 0 | 12 |
| [`tools/recipes/stage_d1_fgate.py`](#tools-recipes-stage-d1-fgate-py) | recipe imported by another file | 3 | 3 | 0 | 3 |
| [`tools/recipes/stage_d1_l2r1.py`](#tools-recipes-stage-d1-l2r1-py) | recipe imported by another file | 1 | 2 | 0 | 2 |
| [`tools/recipes/stage_d1_l2r2.py`](#tools-recipes-stage-d1-l2r2-py) | recipe imported by another file | 2 | 2 | 0 | 2 |
| [`tools/recipes/stage_d1_l7_r.py`](#tools-recipes-stage-d1-l7-r-py) | recipe imported by another file | 1 | 7 | 0 | 5 |
| [`tools/recipes/stage_d1_qrt_pool.py`](#tools-recipes-stage-d1-qrt-pool-py) | recipe imported by another file | 1 | 1 | 0 | 1 |
| [`tools/recipes/stage_d1_ring_p2a.py`](#tools-recipes-stage-d1-ring-p2a-py) | recipe imported by another file | 1 | 1 | 0 | 1 |
| [`tools/recipes/stage_d1_ring_p2b.py`](#tools-recipes-stage-d1-ring-p2b-py) | recipe imported by another file | 1 | 2 | 0 | 2 |
| [`tools/recipes/stage_d1_ring_p3a.py`](#tools-recipes-stage-d1-ring-p3a-py) | recipe imported by another file | 1 | 1 | 0 | 1 |
| [`tools/recipes/stage_d1_ring_p3b1.py`](#tools-recipes-stage-d1-ring-p3b1-py) | recipe imported by another file | 1 | 1 | 0 | 1 |
| [`tools/recipes/stage_d1_ring_p3b2a.py`](#tools-recipes-stage-d1-ring-p3b2a-py) | recipe imported by another file | 2 | 1 | 0 | 1 |
| [`tools/recipes/stage_d1_ring_p3b2b.py`](#tools-recipes-stage-d1-ring-p3b2b-py) | recipe imported by another file | 2 | 1 | 0 | 1 |
| [`tools/recipes/stage_d1_ring_p4_rasrest.py`](#tools-recipes-stage-d1-ring-p4-rasrest-py) | recipe imported by another file | 1 | 1 | 0 | 1 |
| [`tools/recipes/stage_d1_ring_p4_s01.py`](#tools-recipes-stage-d1-ring-p4-s01-py) | recipe imported by another file | 1 | 1 | 0 | 1 |
| [`tools/recipes/stage_d1_ring_p4_s02.py`](#tools-recipes-stage-d1-ring-p4-s02-py) | recipe imported by another file | 1 | 1 | 0 | 1 |
| [`tools/recipes/stage_d1_ring_p4_s02v18.py`](#tools-recipes-stage-d1-ring-p4-s02v18-py) | recipe imported by another file | 1 | 1 | 0 | 1 |
| [`tools/recipes/stage_d1_ring_p4_s03v18.py`](#tools-recipes-stage-d1-ring-p4-s03v18-py) | recipe imported by another file | 1 | 1 | 0 | 1 |
| [`tools/recipes/stage_d1_ring_p4_s04v18.py`](#tools-recipes-stage-d1-ring-p4-s04v18-py) | recipe imported by another file | 1 | 1 | 0 | 1 |
| [`tools/recipes/stage_d1_ring_p4_s05v18.py`](#tools-recipes-stage-d1-ring-p4-s05v18-py) | recipe imported by another file | 1 | 1 | 0 | 1 |
| [`tools/recipes/stage_d1_ring_p4_s06v18.py`](#tools-recipes-stage-d1-ring-p4-s06v18-py) | recipe imported by another file | 2 | 4 | 0 | 2 |
| [`tools/recipes/stage_d1_ring_p4_s06v18_scratch.py`](#tools-recipes-stage-d1-ring-p4-s06v18-scratch-py) | recipe imported by another file | 1 | 9 | 0 | 5 |
| [`tools/recipes/stage_d1_ring_p4_s07v18.py`](#tools-recipes-stage-d1-ring-p4-s07v18-py) | recipe imported by another file | 1 | 4 | 0 | 2 |
| [`tools/recipes/stage_d1_ring_p4_s08v18.py`](#tools-recipes-stage-d1-ring-p4-s08v18-py) | recipe imported by another file | 1 | 4 | 0 | 2 |
| [`tools/recipes/stage_d1_ring_p4_s09v18.py`](#tools-recipes-stage-d1-ring-p4-s09v18-py) | recipe imported by another file | 1 | 4 | 0 | 2 |
| [`tools/recipes/stage_d1_ring_p4s1.py`](#tools-recipes-stage-d1-ring-p4s1-py) | recipe imported by another file | 1 | 1 | 0 | 1 |
| [`tools/recipes/stage_d1_ring_p5s01a.py`](#tools-recipes-stage-d1-ring-p5s01a-py) | recipe imported by another file | 1 | 4 | 0 | 2 |
| [`tools/recipes/stage_d1_ring_p5s01b.py`](#tools-recipes-stage-d1-ring-p5s01b-py) | recipe imported by another file | 1 | 1 | 0 | 1 |
| [`tools/recipes/stage_d1_ring_p5s02.py`](#tools-recipes-stage-d1-ring-p5s02-py) | recipe imported by another file | 1 | 1 | 0 | 1 |
| [`tools/recipes/stage_d1_ring_p5s02a.py`](#tools-recipes-stage-d1-ring-p5s02a-py) | recipe imported by another file | 1 | 1 | 0 | 1 |
| [`tools/recipes/stage_d1_ring_p5s02b.py`](#tools-recipes-stage-d1-ring-p5s02b-py) | recipe imported by another file | 1 | 1 | 0 | 1 |
| [`tools/recipes/stage_d1_ring_p5s02c.py`](#tools-recipes-stage-d1-ring-p5s02c-py) | recipe imported by another file | 1 | 1 | 0 | 1 |
| [`tools/recipes/stage_d1_ring_p5s02d.py`](#tools-recipes-stage-d1-ring-p5s02d-py) | recipe imported by another file | 1 | 1 | 0 | 1 |
| [`tools/recipes/stage_d1_ring_p5s02e.py`](#tools-recipes-stage-d1-ring-p5s02e-py) | recipe imported by another file | 1 | 1 | 0 | 1 |
| [`tools/recipes/stage_d1_s1.py`](#tools-recipes-stage-d1-s1-py) | recipe imported by another file | 4 | 19 | 0 | 4 |
| [`tools/recipes/stage_d1_s3_focus.py`](#tools-recipes-stage-d1-s3-focus-py) | recipe imported by another file | 1 | 22 | 0 | 15 |
| [`tools/recipes/stage_template_ring.py`](#tools-recipes-stage-template-ring-py) | recipe imported by another file | 1 | 1 | 0 | 1 |
| [`tools/hooks/adapt_claude.py`](#tools-hooks-adapt-claude-py) | hook - reference | 1 | 3 | 0 | 1 |
| [`tools/hooks/adapt_codex.py`](#tools-hooks-adapt-codex-py) | hook - reference | 1 | 5 | 0 | 1 |
| [`tools/hooks/guard_assign.py`](#tools-hooks-guard-assign-py) | hook - reference | 6 | 17 | 0 | 8 |
| [`tools/hooks/guard_bash.py`](#tools-hooks-guard-bash-py) | hook - reference | 13 | 12 | 0 | 0 |
| [`tools/hooks/guard_card.py`](#tools-hooks-guard-card-py) | hook - reference | 4 | 4 | 0 | 2 |
| [`tools/hooks/guard_cycle.py`](#tools-hooks-guard-cycle-py) | hook - reference | 29 | 14 | 0 | 3 |
| [`tools/hooks/guard_peer.py`](#tools-hooks-guard-peer-py) | hook - reference | 27 | 27 | 0 | 4 |
| [`tools/hooks/guard_session.py`](#tools-hooks-guard-session-py) | hook - reference | 7 | 18 | 7 | 0 |
| [`tools/hooks/guard_write.py`](#tools-hooks-guard-write-py) | hook - reference | 6 | 8 | 0 | 4 |
| [`tools/hooks/guardcore.py`](#tools-hooks-guardcore-py) | hook - reference | 3 | 12 | 0 | 1 |
| [`tools/hooks/report_gate.py`](#tools-hooks-report-gate-py) | hook - reference | 2 | 8 | 0 | 5 |

### tools/addrcheck.py

shared module; imported by 14 file(s): `tools/bench/diag_c151_a1_1_fs.py`, `tools/bench/diag_c152_b3_1_fs.py`, `tools/bench/diag_c154_a3_3_nodes.py`, `tools/bench/diag_c155_a3_2_nodes.py`, `tools/bench/diag_c158_a3_2b_nodes.py`, `tools/bench/jev_addr_measure_s5.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `addr_key` | a | The canonical text of one plan address (dict or '<uid>.<term>' string) - the key stagesim's addr_pos records use. | docstring | - | 44 |
| `owner_rows` | rows, owner | The owner's terminal rows in READ order, one per term uid (a multi-frame tunnel lists a uid once). | docstring | - | 51 |
| `triple` | rows, term_uid | {owner, index, class, source, name} of one terminal row, index = position among its owner's rows (read order). | docstring | - | 61 |
| `pos_table` | rows | card chat-T6 (docs/d1/result-gates.md): {term uid: POSITION KEY (node, index, term class, is_source)} over one terminal table - the | docstring | selftest_t6_poskey.py | 72 |
| `resolve` | rows, owner, name, want_source=None, pos=None, owner_class=None | (row / None, how, candidates). Tier (a) on ONE address against ONE terminal table. 'pos' = the recorded triple | docstring | - | 97 |
| `real_match` | sim_rows, st, real_rows, rt, rn_owner | Tier (a) on the REAL side of a rebind: does real row 'rt' on real owner 'rn_owner' sit at the SAME position as | docstring | - | 139 |
| `real_face` | sim_rows, st, real_rows, rn_owner, face, want_source, rt, mode | (ok, why). A plan address named 'inner'/'outer' binds on the real side only when ALL hold: the sim row 'st' is of | docstring | - | 171 |
| `obj_class` | doc, uid | The class of object 'uid' in a graph doc's 'objs' (None when absent). | docstring | - | 194 |
| `cond_sinks` | doc, rows, loop | (body diagrams, sink rows) of While 'loop': stagesim.cond_row's filter (body Diagram = 'owners' entry owned by the | docstring | - | 199 |
| `cond_bind` | addr, sim_doc, sim_rows, sim_loop, real_doc, real_rows, real_loop, M | (real sink uid / None, why). The PD316 base-loop form {'uid': <While>, 'term': 'cond'} (stagexec.base_cond: exactly | docstring | - | 213 |
| `jev_same` | planned, candidate, n=1, timeout=25 | (p, verdict, err) - one typed question. Never raises; no key -> (None, 'unknown', 'no key'). | docstring | - | 252 |
| `measure` | path=LABELLED, out=MEASURE, n=1, log=print | Run tier (b) on the labelled set; write {accuracy, n, rows, switched_on} to MEASURE. Accuracy counts an 'unknown' | docstring | - | 265 |
| `jev_switched_on` | path=MEASURE | True when the Jev address advisory is on: env ADDR_JEV is not '0' and the JSON at path (default MEASURE) has a truthy 'switched_on'; an absent or unreadable file gives False. Returns bool. | side file | - | 289 |
| `advise` | items, log=print, n=1 | Tiers (b) and (c) over unresolved items [{planned, candidates:[...]}]: Jev advisory per candidate when switched on | docstring | - | 298 |
| `plan_ends` | plan | [(action n, action id, field, address)] for every address field of every action. | docstring | - | 327 |
| `split_addr` | v | (owner uid int / None, term name / None, term_uid / None) - None owner for a symbolic new:... address. | docstring | - | 337 |
| `check_plan` | plan, rows, addr_pos=None | Tier (a) over every NUMERIC-owner address of a plan against ONE terminal table (the plan's base graph). Symbolic | docstring | - | 349 |

### tools/allterms.py

shared module; imported by 73 file(s): `tools/bench/allterms_s4.py`, `tools/bench/allterms_v1_check.py`, `tools/bench/diag_c100_6_maxmin.py`, `tools/bench/diag_c103_wait_donor.py`, `tools/bench/diag_c111_b1_errorlist.py`, `tools/bench/diag_c112b_opuid.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `read_terms` | target, op=OP_ALLTERMS | Every terminal of 'target''s block diagram in ONE op run. Returns (rows, seconds). | docstring | - | 68 |
| `all_wire_uids` | target | Every Wire object's uid on 'target''s diagram, in ONE 'report_all' run. Returns (uids, seconds). | docstring | - | 94 |
| `join_wires` | rows, wire_uids=None | One row per wire, joined from the terminal table by wire_uid. Pure; no LabVIEW. | docstring | - | 106 |
| `severed` | wires | Wires missing a side - the shape the D1 bed's 11 broken wires are expected to show. | docstring | - | 145 |
| `main` | argv=None | CLI: reads every terminal of the VI (read_terms with --op, default OP_ALLTERMS) and every wire uid, joins them into a wire table, flags severed wires; writes <stem>.json (meta + terminals) and <ste... | side file | - | 150 |

### tools/audit_cycle.py

shared module; imported by 8 file(s): `tools/bench/jev_wave4_selftest.py`, `tools/bench/selftest_audit_a9_witness.py`, `tools/bench/selftest_audit_c4c_split.py`, `tools/bench/selftest_audit_c7.py`, `tools/bench/selftest_audit_cost_window.py`, `tools/bench/selftest_bgrun_reap.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `seg_failures` | seg | Failure count of ONE run segment (starts at its BGRUN START line): legacy findall count before the switch, | docstring | - | 118 |
| `log_failed` | body | A3's question for a whole log: did ANY run in it fail (legacy rule for pre-switch runs). | docstring | - | 128 |
| `window_runs` | body, cutoff, until | The parts of a bgrun log that belong to THIS window: one segment per 'BGRUN START' stamped inside it. | docstring | - | 139 |
| `cost_split` | machinery_logs, cutoff, until | Wall-clock and dollars of the MACHINERY logs, split into REVIEW spend and JUDGEMENT-SESSION spend. | docstring | - | 165 |
| `drop_jev_ledgers` | paths, bench=None | (kept, dropped): the Jev ledgers directly in 'bench' (default BENCH, resolved at call time) are dropped. | docstring | - | 234 |
| `a1_bypass` | build_logs | A1's reading: basenames of build logs carrying no 'BGRUN START' line. | docstring | - | 245 |
| `a3_unreviewed` | build_logs, reviews_glob=None | A3's reading: (failing, unreviewed) - a failing log with no archived review newer than it. | docstring | - | 250 |
| `a2_state` | body | A2's reading of one log body (card 92-4): "" (no bgrun run at all), "ended" (END or TIMEOUT present), | docstring | - | 259 |
| `a9_named_files` | lines, root, code_names | Project-relative code files a disposition names: 'tools/x/y.py' as written, or a bare 'y.py' that resolves to | docstring | - | 288 |
| `a9_unlanded` | root=None, peer_glob=A9_GLOB, code_override=None, detail=None | (absent: [review stem], n_candidates). 'code_override' {project-relative path: text} replaces a code file's | docstring | - | 307 |
| `say` | check, ok, detail | Appends {check, ok, detail} to the module RESULT list and prints a PASS / FAIL / n-a line (ok True / False / other). Returns None. | side file | - | 358 |
| `read` | p | Text of file p (utf-8, errors replaced); '' when it cannot be opened. Returns str. | side file | - | 364 |
| `parse_ts` | s | Epoch seconds, or 'YYYY-MM-DD[ HH:MM[:SS]]' in local time. Returns None for an empty value. | docstring | - | 372 |
| `c7_plan` | root=None, next_path=None | Which plan document C7 measures scope against. Returns (path or None, basis string). | docstring | selftest_audit_c7.py | 490 |
| `main` |  | CLI cycle audit over a window (--from/--to, else --since-hours; --cycle labels it): the A/C checks on bench build logs and archived reviews plus doc_lint, each via say(); prints AUDIT PASS or VIOLA... | side file | - | 534 |

### tools/bgrun.py

shared module; imported by 1 file(s): `tools/bench/replay_c6_protocol.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `relaunch_detached` | logp | Re-exec THIS runner so it survives its caller's exit (cycle 15 deliverable 1). | docstring | - | 80 |
| `is_jev_command` | cmd | True when the script this command runs (its FIRST '.py' token) is a Jev script. Never the log name. | docstring | - | 131 |
| `is_scoped_script` | cmd | True when the script this command runs (its FIRST '.py' token) is a tools/recipes or tools/bench script and | docstring | - | 140 |
| `main` |  | CLI runner: runs the command after -- with output appended to --log between BGRUN START/PID and END/TIMEOUT lines, reaps dead runners' logs, records stage runs, tree-kills at --max-min; --detach re... | side file | - | 147 |

### tools/bgrun_reap.py

shared module; imported by 3 file(s): `tools/bench/selftest_bgrun_reap.py`, `tools/bgrun.py`, `tools/cycle_runner.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `live_pids` |  | Set of running pids from ONE tasklist call; None when tasklist itself failed (then nothing is reaped). | docstring | - | 46 |
| `classify` | text | (state, pid) of the LAST run segment: 'none' (no START), 'ended' (terminal line present), | docstring | - | 59 |
| `killed_line` | pid, who | The newline-terminated 'BGRUN KILLED (external) pid=<pid> marked <now> by <who>: ...' line that reap() appends to a dead runner's log. Returns str. | side file | - | 86 |
| `reap` | bench=BENCH, exclude=(), who='bgrun_reap', max_age_days=MAX_AGE_DAYS, dry_run=False, pids=None | Mark every dead-runner log under 'bench'. Returns {"marked": [(path, pid)], "open_live": [(path, pid)], | docstring | - | 91 |
| `main` |  | CLI over reap(): marks (with --dry-run only lists) dead-runner logs under --bench, excluding $BGRUN_LOG; prints MARKED / LIVE / NO-PID lines, a scanned/marked summary and a RESULT line. Returns 0. | side file | - | 142 |

### tools/card_clock.py

shared module; imported by 3 file(s): `tools/bench/selftest_c153_cardclock_quoted.py`, `tools/bench/selftest_card_clock.py`, `tools/protocol.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `cite_text` | res | first_fail + blocked_by's strings, each with its quoted spans blanked (fp-72). | docstring | - | 41 |
| `find_bind` | log, cid | First 'BOUND agent ... (id <cid>)' line of the guard_card log: returns (datetime of its stamp, 1-based line number), or (None, None) when the log or the line is absent. | side file | - | 47 |
| `clock` | result_path, log, cards | Measures a result file's minutes (its mtime minus the card's first bind line) against the task card's budget.minutes and the claimed cost.minutes. Returns (CLOCK line, verdict OK / CLOCK-MISMATCH /... | side file | - | 59 |
| `main` | argv=None | CLI: clock() on one result_<id>.json (--log, --cards); prints the CLOCK line and a RESULT line (SKIP when unmeasured, FAIL on a mismatch). Returns clock's rc 0 / 1 / 2. | side file | - | 93 |

### tools/census_predict.py

shared module; imported by 46 file(s): `tools/bench/diag_c133_1_pred_p3b2.py`, `tools/bench/diag_c133_5_pred_p3b2b.py`, `tools/bench/diag_c134_1_finalize_b.py`, `tools/bench/plan_ring_p3b_split.py`, `tools/bench/plan_ring_p3b_split_p3b2.py`, `tools/bench/prep_c139_5_mkv13.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `md5_of` | p | MD5 hex digest of the file at p (read whole, binary). Returns str. | side file | - | 39 |
| `resolve_row` | a, by_as, samples, canon_by_donor | -> (op_key, variant_name or None, delta dict or None, why). | docstring | - | 72 |
| `predict` | plan, pred, samples | Resolves each plan action to a sampled class-count delta, sums them, and compares per class with the prediction file's census block. Returns {rows, classes (derived/declared/verdict), derived, decl... | side file | - | 121 |
| `result_line` | rep, artefacts | The 'RESULT {...}' result-line/1 string of a predict() report: FAIL on a failing class, SKIP for UNPREDICTED / UNDECLARED, else PASS, with per-class pass/fail counts and the given artefacts. Return... | side file | - | 171 |
| `check_cites` | cites, root=ROOT | Every cite {file, line, expect}: 'expect' must be a substring of that 1-based line. -> list of problems ([] = all hold). | docstring | - | 193 |
| `record_sample` | samples_p, op, variant, delta, cites, why='', plan_match=None, route=None, match=None, n=1 | Card 123-7 (PD247(e)): record a scratch run's MEASURED class census as a sample. Refuses (ValueError, nothing written) | docstring | - | 210 |
| `main` | argv | CLI: 'record <op> <variant> --delta .. --cites ..' stores a measured sample (record_sample); otherwise '<plan.json> <pred.json> [--samples] [--json]' prints ROW / CLASS / VERDICT lines and a RESULT... | side file | - | 240 |

### tools/cycle_runner.py

shared module; imported by 15 file(s): `tools/bench/diag_c159_g1_1_check.py`, `tools/bench/selftest_bgrun_reap.py`, `tools/bench/selftest_c108e_tools.py`, `tools/bench/selftest_chat_p1.py`, `tools/bench/selftest_cycle_runner.py`, `tools/bench/selftest_cycle_runner_ladder.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `spawn_env` | extra=None | Copy of os.environ for a spawned session: drops the inherited role variables (CYCLE_ROLE, ASSIGN_STATE, ASSIGN_RESULT, PURPOSE_PHASE, HANDBACK_RECORD), adds SPAWN_ENV_EXTRA, then 'extra'. Returns d... | side file | - | 114 |
| `read` | p | Text of file p (utf-8, errors replaced); '' when it cannot be opened. Returns str. | side file | - | 123 |
| `stop_marker` | status_text | The user's handle on the loop. 'STOP' at the start of a line in the head of the file, or a STOP heading. | docstring | - | 131 |
| `next_section` | status_text | Body of the '## NEXT' section of STATUS text (up to the next '## ' heading), stripped; '' when there is none. Returns str. | side file | - | 141 |
| `next_last_line` | status_text | Last non-blank line of the NEXT section, cut to 160 chars; '(no NEXT section)' when the section is empty or absent. Returns str. | side file | - | 146 |
| `session_cmd` | a, prompt, model=None, effort=None | The command bgrun will run: one headless judgement session, or the dry-run stand-in. | docstring | - | 151 |
| `result_json` | log_text | The '--output-format json' envelope out of a bgrun log, or None. | docstring | - | 163 |
| `limit_wait_s` | log_text, now=None | Seconds to sleep for a usage limit (renewal + 2 min), or None when this is not a limit message. | docstring | - | 179 |
| `log_line` | path, text | Appends text plus a newline to the log at path (creating its folder; an OSError is ignored) and prints the text. Returns None. | side file | - | 205 |
| `last_cycle_number` | runner_log | Highest N among the 'CYCLE N /' lines of the runner log; 0 when there are none. Returns int. | side file | - | 215 |
| `judge_ab_effort` | n, mode, now=None | (effort / None, why). mode on/off/auto; auto = on before JUDGE_AB_UNTIL. | docstring | - | 281 |
| `judge_choice` | level, ff_recipe, ff_rung, base_model, base_effort | (rank, model, effort): the higher of the judgement-ladder level and the firefighter rung, capped at JUDGE_TOP. | docstring | - | 290 |
| `judge_ladder_step` | level, next_moved, slugs, delivered | -> (new_level, reason, stop). Pure; the caller persists and logs. | docstring | - | 302 |
| `retro_files_in_window` | peer_dir, t_start, t_end | card chat-P1 2b: the retrospective archives CREATED inside the window (same stamp rule as retro_slugs_in_window). | docstring | - | 320 |
| `retro_slugs_in_window` | peer_dir, t_start, t_end | VIOLATION slugs from retrospective files CREATED inside the cycle window (creation time, as failed_recipes). | docstring | - | 338 |
| `goalmap_done` | path | Set of milestone ids whose status is 'done' in the goal-map JSON at path; empty set when the file is absent or unreadable. Returns set. | side file | - | 358 |
| `delivered_in_window` | cards_dir, t_start, t_end, done_before, goalmap_path | '' or a short description: a PASS result/1 card with artefacts written in the window, or a milestone newly done. | docstring | - | 366 |
| `judge_state_load` | bench | Reads <bench>/judge_ladder.json. Returns (level clamped to 0..JUDGE_TOP, reason); (0, 'start') when the file is absent or malformed. | side file | - | 391 |
| `judge_state_save` | bench, level, reason, n | Writes {level, reason (300 chars), after_cycle n, at now} to <bench>/judge_ladder.json; any failure is swallowed. Returns None. | side file | - | 399 |
| `add_judge_decision` | n, reason, blocks, path | One open decisions-pending/1 item for a judgement ladder exhausted at its top rung. (id, None) / (None, why). | docstring | - | 408 |
| `command_identity` | cmd | The SCRIPT identity of a bgrun command: every '.py' path in it, basename, '_vN' stripped, lower-cased, joined | docstring | - | 419 |
| `newest_run_passed` | bench, identity, since_mtime, skip_names=() | True when the NEWEST bgrun run of 'identity' (any log in bench with mtime >= since_mtime, by START time then | docstring | - | 430 |
| `failed_recipes` | bench, t_start, t_end | Recipe basenames whose bgrun log (mtime inside [t_start, t_end]) ended rc!=0 or TIMEOUT - unless the NEWEST | docstring | - | 463 |
| `git_commit_cycle` | n, runner_log | Commit everything the cycle left in the tree (2026-09-24: cycles 68/69 ended with 129 uncommitted files; | docstring | - | 555 |
| `capabilities_hook` | n, runner_log, doc=None, timeout=300, gen=None | Card chat-T7 item 6(c) (user 2026-10-09 "전부 적용"): at every cycle end, BEFORE the git commit, regenerate the function table + | docstring | selftest_t7_capabilities.py | 581 |
| `land_retrospective` | bench, runner_log | A retrospective the session started but did not finish is RE-RUN by the runner, synchronously. | docstring | - | 608 |
| `retro_fallback` | n, t_start, a, bench, runner_log | card chat-P1 item 2b (user 2026-09-28): the session runs its retrospective only when tools/retro_due.py says it | docstring | - | 641 |
| `motor_limits_hook` | phase, n, a, bench, runner_log, status_text | User, 2026-09-23 ("훅으로 묶어서 매 사이클마다 시작할때는 묶고, 종료시에는 풀고. 그 다음 각 싸이클 시작 및 종료 | docstring | - | 683 |
| `labview_close_hook` | n, a, bench, runner_log, status_text | User 2026-09-24 ("사이클 종료하고서는 제대로 LabVIEW 끄는것 잊지 말것, 특히 카메라가 계속 Acquisition 하면 기계에 | docstring | - | 774 |
| `bgrun_reap_hook` | n, bench, runner_log | Card 92-4 (retrospective-cycle90 'device-failed', threshold 1): at every cycle end, close the record of any | docstring | - | 813 |
| `errorlist_hook` | n, a, bench, runner_log, status_text | User decision 5, 2026-09-24 ("사이클 시작하기 전에 LabVIEW 컴파일 에러 창은 반드시 확인해야할듯"): before every | docstring | - | 833 |
| `gates_due` | bench, peer_dir, next_card | [{gate, due, detail}] - every guard_cycle 'due' check, measured at cycle start. 'due' None = the check errored. | docstring | - | 984 |
| `retro_undisposed` | peer_dir | Path of the newest archived retrospective whose disposition is missing, empty or still the placeholder, else None | docstring | - | 1033 |
| `retro_undisposed_item` | n, peer_dir, runner_log | The 'retro-undisposed' gates_due item ({gate, due: True, detail}) when retro_undisposed() names a file, else None; | docstring | - | 1057 |
| `first_fail_line` | path | '<log name>: <first failing line>' of a failed bgrun log (GATE_FAIL_RE, else the BGRUN END/TIMEOUT line). | docstring | - | 1080 |
| `debate_hook` | kind, n, a, bench, runner_log, why='', fail_lines=() | Run ONE discussion of 'kind' ('outcome' / 'stuck') before cycle n and apply its result. Dry runs dispatch it | docstring | - | 1088 |
| `gates_due_hook` | n, a, bench, runner_log, defer=None, out=None | Cycle start: gates_due(), then a DUE outcome review is RUN before the session spawns - as a Claude-GPT | docstring | - | 1115 |
| `write_cycle_card` | bench, n, status_text, model, effort, ff_recipe, motor_verdict, a, errorlist=None, steer=None, note=None, gates=None | C1: '<bench>/cards/cycle_<n>.json', validated against docs/protocol/cycle.json. Returns (path, None) or | docstring | - | 1181 |
| `next_json_reading` | bench | (md5 / 'absent', card / None, why / None) of '<bench>/next.json' - the ONE reading the runner uses. | docstring | - | 1231 |
| `note_in_status` | status_path, reason | APPEND a stop notice; never rewrite STATUS.md - it is the user's file and the next session's cold start. | docstring | - | 1236 |
| `Heartbeat` | (class) | Runner heartbeat state (current cycle, phase, cycles done, summed cost); emit() writes the HEARTBEAT line to the runner log, rewrites heartbeat_latest.md and raises a toast. | side file | - | 1256 |
| `Heartbeat.begin` | n | Marks cycle n as running and stamps its start time. Returns None. | side file | - | 1265 |
| `Heartbeat.cycle_end` | n, rc, cost | Counts one finished cycle, adds its cost (a '$x' string; an unparseable one is ignored), sets the phase to 'ended HH:MM (exit rc, cost)' and emits a cycle-end heartbeat. Returns None. | side file | - | 1268 |
| `Heartbeat.emit` | kind | Writes one 'HEARTBEAT / ...' line (cycle, last result card, hook states, open decisions, deliverables, next act) to the runner log, rewrites heartbeat_latest.md, raises a toast; an error becomes a ... | side file | - | 1333 |
| `Heartbeat.final` |  | Emits the 'final' heartbeat once; later calls do nothing. Returns None. | side file | - | 1395 |
| `run_session` | a, cmd, log, env, n, status_path, runner_log, tag | ONE session under bgrun, with the usage-limit / API-5xx rerun rule (CLAUDE.md usage-limit protocol: rerun, don't | docstring | - | 1409 |
| `newest_assign_result` | cards_dir | Path of the most recently modified assign_result_*.json in cards_dir, or None when there is none. | side file | - | 1480 |
| `purpose_from_next` | card | The assignment card's purpose dict from a next.json card: act and pass items (each cut to 200 chars), plan {path, md5} or None, advances, unblocks, task_kind, note. Returns dict. | side file | - | 1485 |
| `write_assign_card` | cards_dir, n, k, purpose, next_md5, cfg, state_path, result_path, handback_in | Builds and validates an assign/1 card (cycle, round, purpose, next_md5, caps from cfg, state / result / handback paths, ASSIGN_AGENTS) and writes cards_dir/assign_<n>_<k>.json. Returns (path, None)... | side file | - | 1493 |
| `write_handback` | cards_dir, n, k, trigger, detail, st_path, result_path, next_md5, usd, minutes | Writes cards_dir/handback_<n>_<k>.json (handback/1: trigger, detail, the assignment state's card rows, result path, next_md5, cost, minutes); a record that fails validation is replaced by a minimal... | side file | - | 1509 |
| `assign_cmd` | a, cfg, prompt | The assignment session's command (the bgrun-wrapped part), or None = skip (a dry run without a stand-in). | docstring | - | 1526 |
| `assignment_rounds` | a, n, bench, runner_log, status_path, judge_prompt, model, effort, judge_rc, next_md5_cycle_start | The purpose flow after the cycle's first judgement session. -> {'outcome', 'rounds', 'cost'}. Never raises into | docstring | - | 1535 |
| `main` |  | CLI entry of the cycle runner: parses the run options (caps, budget, models, flow, self-test switches), reads the prompt file, creates a Heartbeat and runs _loop; the final heartbeat is always emit... | side file | - | 1651 |

### tools/debate_loop.py

shared module; imported by 1 file(s): `tools/cycle_runner.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `slug_for` | n, kind, bench | 'c<n>-<kind>', with -2, -3 ... when that discussion dir already holds a relay state (a cycle number re-used | docstring | - | 68 |
| `runner_env` | base=None | The child env a discussion needs outside the app (as tools/debate_start.ps1 sets it): the Claude MSIX | docstring | - | 79 |
| `refresh_gpt_worktree` |  | The GPT speaker reads the code from the sibling worktree V6_debate (debate_relay --codex-cwd default): bring it | docstring | - | 96 |
| `cycle_lines` | runner_log, cycles, limit=90 | The runner-log lines that belong to the given cycle numbers (CYCLE / NEXT / ASSIGN / HANDBACK* / STEER / | docstring | - | 112 |
| `outcome_topic` | n, bench, runner_log, peer_dir, goalmap_path, status_path, cycles_back=CYCLES_BACK | The outcome discussion's topic (Korean; first line = doc title): goal, what the last 'cycles_back' cycles | docstring | - | 171 |
| `stuck_topic` | n, why, bench, runner_log, status_path, fail_lines=(), cycles_back=2 | The stuck discussion's topic (Korean; first line = doc title): why the runner called it (HANDBACK-LIMIT / the | docstring | - | 218 |
| `run_discussion` | kind, n, topic_text, bench, log, max_min=DEADLINE_MIN, max_rounds=MAX_ROUNDS, stub=False, stub_secs=0.0, doc='google'... | Run ONE discussion synchronously: topic -> <bench>/debate/<slug>/topic_in.md, then 'debate_gdoc.py run --auto-end' | docstring | - | 262 |
| `archive_outcome` | res, n, peer_dir | Write '<peer_dir>/<date>-outcome-review-debate-c<n>.md' so outcome_review.is_due() (and guard_cycle's outcome | docstring | - | 348 |
| `apply` | res, kind, n, bench, goalmap_path, peer_dir, log | Turn a finished discussion into the existing channels: steer/1 (protocol.steer_from_debate -> write_steer in | docstring | - | 381 |
| `selftest` |  | L1 topics carry the sources; L2 stub discussion -> summary, DEBATE line; L3 apply -> valid steer/1 + decisions + | docstring | - | 424 |

### tools/debate_relay.py

shared module; imported by 2 file(s): `tools/debate_gdoc.py`, `tools/debate_loop.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `codex_js` |  | Newest codex.js: the Claude app's MSIX copy (updated there 2026-10-09 to 0.162.0, the first build that accepts | docstring | - | 53 |
| `run_killable` | cmd, cwd, stdin_text, env, stop_path, timeout=1200 | Run cmd; poll stop_path every second and kill the whole process tree when it appears. -> (rc, out, err, stopped) | docstring | - | 70 |
| `say_claude` | st, a, prompt, stop | (undocumented) | - | - | 92 |
| `say_gpt` | st, a, prompt, stop | (undocumented) | - | - | 110 |
| `say_stub` | st, a, prompt, stop, name | (undocumented) | - | - | 144 |
| `state_of` | msg | (undocumented) | - | - | 162 |
| `summary` | d | The discussion's end state from <d>/state.json (rounds or turns mode): {rounds, converged, agreed (both sides' | docstring | selftest_rounds | 184 |
| `step` | a | (undocumented) | - | - | 217 |
| `round_` | a | Both speakers write AT THE SAME TIME (user 2026-10-09: "같은 단계에서 서로에게 질문하고 피드백하며 수렴"): | docstring | - | 292 |
| `selftest_rounds` |  | (undocumented) | - | - | 376 |
| `selftest` |  | (undocumented) | - | - | 415 |
| `main` | argv=None | (undocumented) | - | - | 453 |

### tools/dispo.py

shared module; imported by 4 file(s): `tools/audit_cycle.py`, `tools/bench/diag_c159_g1_1_check.py`, `tools/bench/selftest_c150_a3_3.py`, `tools/cycle_runner.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `heading_index` | body | Start index of the disposition heading, else -1 (card 150-a3-4). | docstring | - | 36 |
| `find_disposition` | body | (answer, disposition_text) split at the last line-anchored heading; (body, None) when there is none. | docstring | - | 51 |
| `disposition_len` | body | Characters left in the disposition after placeholder lines are removed and the rest stripped; None = no heading. | docstring | - | 59 |

### tools/doc_lint.py

shared module; imported by 8 file(s): `tools/audit_cycle.py`, `tools/bench/selftest_audit_c7.py`, `tools/bench/selftest_c116a_landed.py`, `tools/bench/selftest_chat_p2.py`, `tools/bench/selftest_doc_lint_d1.py`, `tools/bench/selftest_fn_f2.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `say` | level, check, detail | Appends (level, check, detail) to the module RESULT list. Returns None. | side file | - | 84 |
| `read` | p | Text of file p (utf-8, errors replaced); '' when it cannot be opened. Returns str. | side file | - | 88 |
| `active_docs` |  | The ACTIVE set: docs/*.md, the index directories ('docs/d1/*.md', card chat-D1 2026-10-02) and the two root | docstring | - | 96 |
| `rel` | p | Path p relative to the project root, with forward slashes. Returns str. | side file | - | 109 |
| `frontmatter` | body | The YAML block as a flat dict, or None. Deliberately not a YAML parser: these blocks are machine-written by | docstring | - | 118 |
| `check_frontmatter` |  | L1: every active doc and archive/peer/*.md has frontmatter with type, status and date; records PASS, or a WARN with the missing / incomplete counts, via say(). Returns None. | side file | - | 132 |
| `citation_candidates` | body | (path, lineno_or_None, line_number_in_the_document) for every span that is plausibly a project path. | docstring | - | 160 |
| `resolve_moved` | path, ln | card chat-X1: the path a citation resolves to. The cited path itself when it exists and (for 'path:N') has line | docstring | - | 212 |
| `check_citations` |  | L2 / L2b / L2c: every project path cited in an active doc exists (FAIL when dangling; a plan doc's missing file is a WARN) and every cited :line is inside the file (WARN). Records via say(). Return... | side file | - | 227 |
| `check_status_length` |  | L3: WARN when STATUS.md has more than STATUS_MAX_LINES lines, else PASS, via say(). Returns None. | side file | - | 270 |
| `current_plans` | docs=None | Every 'docs/cycle*-plan.md' (or 'docs/<dir>/INDEX.md') whose frontmatter says 'status: current', as ABSOLUTE paths. | docstring | - | 281 |
| `check_one_current_plan` |  | L4: FAIL when current_plans() finds more than one current plan, else PASS, via say(). Returns None. | side file | - | 302 |
| `check_predecided` |  | L8: the CURRENT cycle plan carries a '## Pre-decided' section (CLAUDE.md section 3 item 2, 2026-09-17). | docstring | - | 315 |
| `check_supersedes` |  | L5: WARN when an active doc's 'supersedes:' names a doc still marked status: current, else PASS, via say(). Returns None. | side file | - | 336 |
| `check_dispositions` |  | 'disposition: legacy' in the frontmatter is EXCLUDED, and the exclusion is the point. | docstring | - | 358 |
| `check_marked_decisions` |  | L7: WARN listing active-doc lines that use a decision / measurement word without a DECIDED: / MEASURED: / DECISION: / ANSWERED: / FAILED: mark, else PASS, via say(). Returns None. | side file | - | 396 |
| `check_decision_headers` | path=None | L8: '## <slug> - <date>' headers of docs/violation-decisions.md (or path) without a parseable HH:MM: FAIL if dated >= L8_FAIL_FROM, WARN if older with an unparseable time; via say(). Returns (fails... | side file | - | 422 |
| `predecided_items` | body | [(number, first_line_no, text)] for every numbered item inside a 'Pre-decided' section of one document. | docstring | - | 461 |
| `check_user_rules_lines` | paths=None | L9: WARN listing Pre-decided items numbered >= L9_FROM_ITEM without a 'USER-RULES:' line in the given paths (default all active docs), else PASS. Returns the list of 'path:line (item n)'. | side file | - | 489 |
| `doc_status` | p, name=None | The frontmatter status; "frozen" for a FROZEN_COPIES byte copy whose frontmatter is the original's (chat-X1). | docstring | - | 518 |
| `is_frozen` | p | True when the doc at p has frontmatter status: frozen. Returns bool. | side file | - | 525 |
| `check_line_cap` | paths=None, names=None | L10 (card chat-D1): an active doc under docs/ that is not frozen/superseded stays <= DOC_MAX_LINES lines. | docstring | - | 529 |
| `check_frozen_footer` | paths=None | L11 (card chat-D1): a 'status: frozen' doc carries its FROZEN footer, which names the index to read instead. | docstring | - | 564 |
| `check_fn_drift` | doc=None | L12 (card chat-F2, user 2026-10-06): CODE-vs-DOC drift of the generated scripting-function table in | docstring | - | 576 |
| `run` | skip_dispositions=False | Clears RESULT and runs every lint check in order, L1 to L12 (L6 replaced by a PASS note when skip_dispositions). Returns a copy of the (level, check, detail) list. | side file | - | 596 |
| `main` |  | CLI: run() (--skip-dispositions; --quiet prints FAILs only), prints each result and a 'DOC-LINT PASS/FAIL: n fail, n warn, n pass' line. Returns 1 when any check FAILed, else 0. | side file | - | 617 |

### tools/elrule.py

shared module; imported by 35 file(s): `tools/bench/diag_c149_a1_2_eladv.py`, `tools/bench/diag_c150_a3_2_elexp.py`, `tools/bench/diag_c151_a1_1_elexp.py`, `tools/bench/diag_c152_b3_1_elexp.py`, `tools/bench/diag_c154_a3_3_elexp.py`, `tools/bench/diag_c155_a3_2_elexp.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `load_requiredness` | path=None | The measured SubVI requiredness table ({'vis': {file name: {'terminals': [...]}}}); an unreadable file gives an EMPTY | docstring | - | 54 |
| `subvis_from_plan` | plan, *states | {uid: VI file name} for every SubVI the plan creates ('create' action, class SubVI, 'subvi_path'), bound through the | docstring | - | 63 |
| `subvi_rules` | rs, vi, table | ([rule or None per row of rs], how) - the measured pane rule of each terminal row of one SubVI node. | docstring | - | 78 |
| `owners_map` | *states | {body_uid: loop_uid} for every Diagram owned by a WhileLoop, merged over the given states/graphs' 'owners' maps. | docstring | - | 94 |
| `items` | state, bodies, created=(), subvis=None, table=None | (set of item keys, detail dict) for one state (sim step state or graph json: both carry 'terminals' rows). | docstring | - | 107 |
| `unwired_inputs` | state | {owner_uid: [terminal names]} of every non-source terminal in state['terminals'] that has no wire and is not a ControlTerminal. Returns a defaultdict(list). | side file | - | 162 |
| `predict` | st0, last, base_total, created, carry=(), extra_owner_states=(), subvis=None, table=None | The fixed EL prediction of one session: st0 = its base state (step_00), last = its simulated end, created = uids of the | docstring | - | 170 |
| `item_class` | text | 'local' / 'cond' / 'sr' / None for one Error List item text (raw + detail). | docstring | - | 201 |
| `session_prediction` | plan, base_total | The fixed-rule prediction of the session a finalized stageplan describes (its first/last step files), or None. | docstring | - | 217 |
| `by_design_verdict` | extra, missing, measured_total, base_total, plan=None, prediction=None | ('log'/'stop', rule, detail) - see the module docstring. 'extra'/'missing' = item texts from errorlist_check.compare; | docstring | - | 228 |

### tools/errorlist_check.py

shared module; imported by 77 file(s): `tools/bench/c109_errorlist_reverdict.py`, `tools/bench/c87_errorlist_reverdict.py`, `tools/bench/c88_reverdict.py`, `tools/bench/diag_c109c_errorlist.py`, `tools/bench/diag_c110_errorlist.py`, `tools/bench/diag_c110d_elcounts.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `md5` | p | MD5 hex digest of file p. Returns str. | side file | - | 57 |
| `not_ready` | e | True when the exception's repr carries a COM-not-ready marker ('-2147221231' or 'ClassFactory'). Returns bool. | side file | - | 95 |
| `labview_up` | R | Start (COM Dispatch launches it) / reach LabVIEW, then wait until two handle readings 5 s apart differ by | docstring | - | 100 |
| `vi_ready` | target, R | Poll a counted GetVIReference (+ ExecState) on 'target' until it answers, up to VI_READY_S; only the | docstring | - | 138 |
| `current_bed` | status_path | 'current-bed: <file.vi>' in STATUS wins; else the NEWEST-on-disk claudeDev D1_*.vi that STATUS names. | docstring | - | 159 |
| `current_bed_text` | txt, claudedev=None | current_bed() on STATUS text (pure; cycle_runner holds the text already). | docstring | - | 164 |
| `find_reusable` | bed, bed_md5, bench=None | (main_json, raw_json, None) for the newest qualifying read of 'bed' at 'bed_md5', else (None, None, reason). | docstring | - | 183 |
| `reverdict` | bed, main_json, raw_json, bench=None, out_dir=None, expected_path=None | Offline verdict of a saved read with the CURRENT checker. Writes errorlist_<stem>_<ts>_reuse.json; returns | docstring | - | 215 |
| `windows_named` | sub | [(hwnd, title)] of the LabVIEW process's top-level windows whose title contains sub, case-insensitive. Returns list. | side file | - | 248 |
| `open_diagram` | scratch, R | Makes sure '<scratch name> Block Diagram' is open: otherwise fronts the VI window and sends Ctrl+E (before/after shots and a confirm act in R['gui_acts_outer']), waiting up to 15 s. Returns True wh... | side file | - | 252 |
| `make_on_item` | scratch, R | Builds the per-item callback for lv_errorlist.read: double-clicks the Error List row, shoots the block diagram before/after and stores show_error (fronted, changed, screenshot) on the item; raises ... | side file | - | 272 |
| `count_zero` | R | A runnable VI has no highlighted row, so lv_errorlist never reads N: OCR the last dialog capture whole. | docstring | - | 302 |
| `norm` | s | Lower-cases s and drops every character outside a-z0-9 (None gives ''). Returns str. | side file | - | 315 |
| `ocr_fold` | k | Applies the OCR aliases in order ('vl' -> 'vi', then 'v' -> 'y') to a normalised key. Returns str. | side file | - | 325 |
| `norm_ocr` | s | ocr_fold(norm(s)): the alias-folded normal form used for OCR-tolerant matching. Returns str. | side file | - | 331 |
| `plan_for_bed` | bed, bench=None | stage_d1_<s>.json whose 'work' is this bed -> the stageplan plan_<s>*.json carrying open_rows. | docstring | - | 350 |
| `derive_expected` | plan | Error List licence rules from a stageplan's open_rows: per SubVI row a '<term> is not wired' rule, per other node one 'contains unwired or bad terminal' rule, plus one uncapped wire-class rule if a... | side file | - | 377 |
| `compare` | items, expected, derived=() | Explicit expected entries (file) are REQUIRED; plan-derived licences are not. Returns extra raws, missing | docstring | - | 415 |
| `license_headers` | items | Mark 'licensed_by = 'header-of <n>'' on qualifying empty-raw rows; return their positions in 'items'. | docstring | - | 448 |
| `class_counts` | items, ocr=False | {norm(raw): n} over the read items - the per-class counts a count-only read is judged by. card 127-2: ocr=True | docstring | - | 471 |
| `count_only_differs` | items, n_reported, expected, derived | (differs: bool, why: str) - a count-only read is accepted only when it matches the expectation exactly. | docstring | - | 481 |
| `read_mode` | count_only, role | 'count' only for a scratch copy; the final saved file is always 'full'. | docstring | - | 495 |
| `by_design` | R, expected, plan, record=True | card chat-S5 (PD337(c), the user's "S1" item 3): a MISMATCH whose only difference is extra session-boundary items | docstring | - | 500 |
| `main` |  | CLI: copies the bed VI (--vi or STATUS's bed) to a scratch, opens it, reads its Error List (count-only or full with a double-click per item), compares with the expected file or plan licences, delet... | side file | - | 519 |

### tools/fn_records.py

shared module; imported by 6 file(s): `tools/bench/fntest_lib.py`, `tools/bench/prep_c150_a2_4_stage_prerun_before.py`, `tools/bench/selftest_c159_b2_1.py`, `tools/bench/selftest_fn_f2.py`, `tools/gen_capabilities.py`, `tools/stage_prerun.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `rel` | p | Path p relative to the project root with forward slashes; on a ValueError (another drive) p itself with forward slashes. Returns str. | side file | - | 125 |
| `locate` | fn | (file, [def qualnames], first line) of a registry function name, or (None, [], None). | docstring | - | 166 |
| `source_md5` | fn | md5 of the function's own source text (ast.get_source_segment of each def, joined) - None when not found. | docstring | - | 196 |
| `reg_path` | fn, reg_dir=None | Registry file of function fn: <reg_dir or tools/bench/fn_records>/<fn with ':' replaced by '_'>.json. Returns the path (str). | side file | - | 216 |
| `load` | fn, reg_dir=None | The fnrec record of function fn read from its registry file, or None when the file does not exist. Returns dict or None. | side file | - | 220 |
| `write_record` | rec, reg_dir=None | Writes rec (indent 1, UTF-8, trailing newline) to the registry file of rec['function'], creating the registry folder. Returns the path written. | side file | - | 228 |
| `status` | fn, reg_dir=None, md5_now=None | 'fresh-pass' / 'fresh-fail' / 'stale' / 'planned' / 'none' (+ the record looked at). | docstring | - | 237 |
| `add_record` | fn, st, log, labview='LabVIEW 2026', card='', reg_dir=None, md5_now=None | Append ONE result record (card chat-F3 calls this after the real run). Refuses without a plan (plan first). | docstring | - | 252 |
| `plan_set` |  | The functions whose test plans this card writes: everything the P4 v18 plans route through, the base reads of a | docstring | - | 267 |
| `predicted` | fn | The 'predicted' block of a test plan from fncontract.TABLE: {postcondition: 'op value'} when the row has 'post', else a {'note': ...} saying no TABLE row / no postcondition. Returns dict. | side file | - | 323 |
| `legacy_for` | fn | scratch_verify records whose 'function' names this function (no src md5 -> evidence only, never fresh). | docstring | - | 333 |
| `make_plan` | fn, card='chat-F2', now=None | Builds the fnrec/1 test-plan record of fn: source file/defs/line/md5 (locate), plan (card, scratch bed, inputs from PLAN_INPUTS or a default, predicted, outcome contract, pass_if), empty records, l... | side file | - | 351 |
| `write_plans` | reg_dir=None, card='chat-F2' | Write (or refresh the plan of) every function in plan_set(). Existing 'records' are KEPT. | docstring | - | 375 |
| `routes_of_plan` | path | Sorted set of route names (the part before ':') of a stageplan JSON's finalized.route_check rows; the actions' op kinds when it is not finalized; [] when unreadable. Returns list. | side file | - | 393 |
| `functions_for_unit` | unit | Sorted function names a stage script / stageplan JSON uses (see module docstring). | docstring | - | 408 |
| `load_config` | path=None | The FN-gate config: JSON at path (default tools/bench/fn_records/gate_config.json), or a copy of DEFAULT_CONFIG when that file is absent. Returns dict. | side file | - | 434 |
| `switch_condition` | cfg=None, reg_dir=None | (met, missing) - every function of the plans in switch.required_from has a fresh PASS record. | docstring | - | 442 |
| `launch_gate` | unit, cfg_path=None, reg_dir=None, log_path=None, now=None | (allow, line). ADVISORY in this card: logs, allows. Refuses only when mode == 'refuse', or switch.auto and the | docstring | - | 452 |
| `main` | argv=None | CLI: --write-config, --write-plans, --status [fn ...], --advise <unit> (launch_gate; returns 2 if refused), --add-record FN STATUS --log ... --card ...; prints what it did. Returns 0, or 2 on a ref... | side file | - | 484 |

### tools/fncontract.py

shared module; imported by 6 file(s): `tools/bench/fntest_lib.py`, `tools/bench/selftest_fn_f2.py`, `tools/fn_records.py`, `tools/gen_capabilities.py`, `tools/gscript.py`, `tools/stagekit.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `PostconditionFailed` | (class) | A declared postcondition did not hold at the call. '.outcome' = the standard outcome dict. | docstring | - | 68 |
| `PostconditionValueError` | (class) | The same, for a function whose pre-existing check raised ValueError (term_index): callers that catch ValueError | docstring | - | 76 |
| `PreconditionFailed` | (class) | card chat-F3b: a DECLARED precondition (PRE) did not hold when the call failed. A RuntimeError, so every caller that | docstring | - | 85 |
| `outcome` | status, fn, reason='', measured=None, expected=None | Builds one standard outcome {outcome, fn, reason (300 chars), measured, expected}; raises ValueError when status is not in OUTCOMES. Returns dict. | side file | - | 94 |
| `classify_exception` | e | timed_out for the watchdog / poison family, else failed (an exception that already carries an outcome keeps it). | docstring | - | 101 |
| `outcome_of_exception` | e, fn=None | The standard outcome of an exception: its own '.outcome' when it has one, else a classified new one. | docstring | - | 111 |
| `outcome_of_text` | err_text, fn=None | For callers that only kept the error STRING (stagekit.Stage.safe): classify from the text. | docstring | - | 119 |
| `mark` |  | Current sequence number of the call-outcome HISTORY (pass it to since()). Returns int. | side file | - | 145 |
| `since` | m | Outcomes recorded in HISTORY after sequence mark m, oldest first. Returns list of outcome dicts. | side file | - | 149 |
| `worst` | ocs, fn=None | The most severe outcome in a list (ok when empty). | docstring | - | 153 |
| `evaluate` | fn, measured, post=None | (status, violations, expected) for 'measured' against the table's postconditions of 'fn' (or 'post'). | docstring | - | 171 |
| `check` | fn, msg='', raise_=None, exc=None, **measured | Evaluate 'fn''s declared postconditions on 'measured'; record the outcome; RAISE at this call when one fails and | docstring | - | 189 |
| `precondition_error` | fn, exc, ns, a, k | card chat-F3b: 'fn''s declared precondition measured after the call raised 'exc' -> a PreconditionFailed (its | docstring | - | 282 |
| `contract` | fn, f, ns=None | Wrap 'f' (the function the TABLE row 'fn' describes) so every call ends in ONE standard outcome. 'ns' = the module's | docstring | - | 302 |
| `install` | namespace, prefix | Wrap every function of module 'prefix' that the TABLE names, inside 'namespace' (the module's globals()). | docstring | - | 346 |
| `functions` | path=GSCRIPT, src=None | {name: ast.FunctionDef} of the module's TOP-LEVEL functions. | docstring | - | 376 |
| `lv_touching` | path=GSCRIPT, src=None | Public top-level functions whose call graph reaches lv/op/_run/_invoke/_err/_lv_gui or a COM method (closure). | docstring | - | 382 |
| `op_verbs` | paths=(STAGEKIT, STAGEXEC) | Every literal verb passed to 'Stage._op("<verb>", ...)' in stagekit/stagexec. | docstring | - | 405 |
| `coverage` |  | {'missing': [...], 'orphan': [...], 'no_reason': [...]} - every LabVIEW-touching public gscript function and every | docstring | - | 413 |
| `describe` | fn | One line for the generated capability table: the outcome contract of 'fn'. | docstring | - | 597 |

### tools/gate_fp.py

shared module; imported by 8 file(s): `tools/bench/diag_c146_a1_1_repro.py`, `tools/bench/selftest_c125_1.py`, `tools/bench/selftest_c131_2_tools.py`, `tools/bench/selftest_c133_1_gatefp_close.py`, `tools/bench/selftest_chat_p1.py`, `tools/bench/selftest_guard_peer_c146.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `is_checker_gate` | gate | True when the gate name is a checker gate: 'guard_<x>' or 'checker:<stage_prerun/stagekit/stagesim/stop_record/protocol/launchunit/doc_lint>[:label]', case-insensitive. Returns bool. | side file | - | 60 |
| `read_queue` | path=None | Every JSON row of the false-positive queue (path, default tools/bench/gate_fp_queue.jsonl or $GATE_FP_QUEUE); blank or unparsable lines skipped, [] when unreadable. Returns list of dicts. | side file | - | 64 |
| `log_fp` | gate, cmd, why, card, line='', log=None, path=None, cycle=None | (entry, created: bool) or raises ValueError on missing evidence. | docstring | - | 97 |
| `drain` | fp_id, fixed, selftest, path=None | (entry, None) or (None, why). | docstring | - | 126 |
| `close` | fp_id, reason, path=None | card 133-1 (PD276(d), PD282(b)): close an OPEN entry that is NOT a false positive (the refusal was CORRECT, or the | docstring | - | 150 |
| `note` | fp_id, text, path=None | card 131-2: attach a NOTE to an entry (why it stays open, who owns it). (entry, None) or (None, why). Status is | docstring | - | 172 |
| `blocking_ids` | cards_dir=None | fp ids named by a result/1 card's blocked_by.device == 'gate-fp:<id>'. | docstring | - | 187 |
| `due` | path=None, cards_dir=None, cycle=None | (due: bool, detail) - the runner's gates_due item 'gate-fp'. | docstring | - | 209 |
| `discharge_for_log` | log_path, first_line, path=None, cycle=None, record=True | (entry, None) when an OPEN checker entry names this failing log and may discharge it this cycle, else | docstring | - | 241 |
| `main` | argv=None | CLI subcommands: log (log_fp), drain, note, close, list [--open], due; prints LOGGED / DEDUPED / DRAINED / NOTED / CLOSED / REFUSED or the list. Returns 0, 2 on a refusal or no command, 1 when 'due... | side file | - | 269 |

### tools/gateclass.py

shared module; imported by 13 file(s): `tools/bench/prep_c150_a2_4_stage_prerun_before.py`, `tools/bench/s2_replay.py`, `tools/bench/selftest_gateclass_s2.py`, `tools/bench/selftest_gateclass_s3.py`, `tools/bench/selftest_s5.py`, `tools/bench/selftest_t3.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `is_tunnel_class` | cls | True when cls is one of TUNNEL_OBJECT_CLASSES (LoopTunnel, Tunnel, SelectorTunnel, FlatSequence inner/outer) or any 'FlatSequence...Tunnel' name. Returns bool. | side file | - | 63 |
| `tolerance` | predicted | max(5, 25 % of /predicted delta/), rounded up. | docstring | - | 90 |
| `is_semantic` | cls | True unless cls is in NON_SEMANTIC_CLASSES (Terminal, InnerTerminal, OuterTerminal, ParameterTerminal, Invoke, LooseEnds, TunnelFace): fail-closed. Returns bool. | side file | - | 95 |
| `count_verdict` | cls, measured, predicted | ('ok'/'log'/'stop', rule text) for ONE class count. | docstring | - | 99 |
| `census_verdict` | measured, declared | {'verdict': ok/log/stop, 'rows': [{class, measured, predicted, verdict, rule}]} over every class of either side. | docstring | - | 112 |
| `gate_kind` | label | (kind, why) of a gate label: the first GATE_TABLE regex matching the label (name / census / rows / arith / fixture); ('stop', fail-closed note) when none matches. Returns tuple. | side file | - | 125 |
| `classify_gate` | label, detail=None, kind=None | {'verdict': 'stop'/'log', 'kind', 'rule', 'rows'} for a FAILED gate. Never 'ok': the caller already saw ok=False; | docstring | - | 174 |
| `soft_record` | gate, cls, expected, measured, rule, script=None, path=None | Append ONE JSON line: {ts, cycle, card, script, gate, expected, measured, class, rule}. Never raises. | docstring | - | 219 |
| `record_classified` | label, c, detail=None, script=None, path=None | One soft line per non-equal class row (census/rows), or one line for a name/arith/fixture gate. | docstring | - | 232 |
| `classify_line` | line | 'log' / 'stop' for one printed '  FAIL  <label>  <detail>' line (stagekit's format); anything else -> 'stop'. | docstring | - | 258 |
| `soft_only` | segment, results | True when a failed run's ONLY failures are LOG-only gate lines: no hard marker (exception, timeout, STOP at gate, ...), | docstring | - | 272 |
| `address_only` | segment, results | True when every failing RESULT line's first_fail, and every printed FAIL / GATE FAIL line, is an address/format | docstring | - | 297 |
| `errorlist_verdict` | extra, missing, predicted_loose=0 | Error List per-class exactness is STOP for every class EXCEPT loose ends. extra/missing = item texts. | docstring | - | 317 |
| `step_face_rows_verdict` | d, sim_rows, real_rows | card chat-S3 (PD328(c), user 2026-10-03 "터널 단자행만 다를 경우 기록하자"): verdict on ONE E1 per-step diff | docstring | - | 335 |

### tools/gen_capabilities.py

shared module; imported by 7 file(s): `tools/bench/diag_c158_a2_5_check.py`, `tools/bench/diag_c158_a2_5_list.py`, `tools/bench/diag_c159_a5_1_check.py`, `tools/bench/diag_c160_h1_1_check.py`, `tools/bench/selftest_fn_f2.py`, `tools/bench/selftest_t7_capabilities.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `rows` | reg_dir=None | [(name, args, contract, record, source)] sorted by name. | docstring | - | 72 |
| `render` | reg_dir=None | The fn-table block text (markers included) from fncontract.TABLE + fn_records. Returns a str. Self-test: selftest_fn_f2.py. | docstring | selftest_fn_f2.py | 94 |
| `split` | text | (before, block, after) - block None when the markers are absent. | docstring | - | 112 |
| `write` | doc=DOC, reg_dir=None, with_list=True, root=None | Rewrite the generated fn-table block (and, card chat-T7, the fn-list block after it - with_list) in 'doc'; returns True when | docstring | selftest_fn_f2.py | 126 |
| `imported_names` | text | Top-level module names a source text imports (static and importlib / __import__ / K.mod string forms). | docstring | - | 180 |
| `shared_files` | root=None | {rel path of a SHARED file: sorted [rel paths of the OTHER files that import it]} - the import graph over every .py under | docstring | selftest_t7_capabilities.py | 195 |
| `module_functions` | path | [(name, args, first docstring line, self-test named in the docstring, line)] of a file's public top-level functions and the | docstring | - | 233 |
| `load_descriptions` | root=None, path=None | {'<module>.<function>': one-line description} from docs/fn_descriptions.json ({} when absent or malformed - stale_descriptions | docstring | selftest_t7_capabilities.py | 276 |
| `describe_row` | module, name, doc, descs | (text, source) of one fn-list row: the docstring's first line -> 'docstring'; else the side file's '<module>.<name>' entry -> | docstring | selftest_t7_capabilities.py | 282 |
| `stale_descriptions` | root=None, path=None | Sorted side-file keys whose function no longer exists (no tools .py of that module name, or no public function / Class.method | docstring | selftest_t7_capabilities.py | 291 |
| `described_rows` | root=None, path=None | [(rel path, location note, importers, [(name, args, text, source, self-test, line)])] - list_rows with each row's description | docstring | selftest_t7_capabilities.py | 312 |
| `list_rows` | root=None | [(rel path, location note, importers, [module_functions rows])] for every shared file, tools/ first then bench / recipes / | docstring | - | 323 |
| `write_shared_cache` | paths, cache=None | Write {schema capabilities-shared/1, files: [...]} to the cache guard_write reads (only when its content changes). | docstring | - | 336 |
| `render_list` | root=None | The fn-list block text (markers included): a module table of contents, then one section per shared file. | docstring | - | 351 |
| `split_list` | text | (before, list block, after) - block None when the list markers are absent. | docstring | - | 382 |
| `put_list` | text, block | 'text' with its fn-list block replaced by 'block' (appended at the end the first time). | docstring | - | 396 |
| `hook_run` | doc=DOC, state_dir=None, root=None | '--hook-run': the lock is ALREADY held by the hook that started this process. Regenerate; while the re-run flag exists, clear | docstring | - | 410 |
| `summary_line` | root=None | 'fn-table N rows; fn-list F files, M functions, S from the side file, U undocumented' - the counts cycle_runner's CAPABILITIES | docstring | - | 448 |
| `drift` | doc=DOC, reg_dir=None, with_list=True | {'block': bool, 'missing': [...], 'gone': [...], 'stale': [...], 'record_changed': [...], 'moved': [...], | docstring | - | 467 |
| `drift_line` | d | One printable line from a drift() dict ('' = no drift; doc_lint L12 prints it). Self-test: selftest_fn_f2.py. | docstring | selftest_fn_f2.py | 489 |
| `main` | argv=None | CLI: rewrite both generated blocks (default), --check (drift, exit 1 on drift), --summary (rewrite + the counts line | docstring | selftest_t7_capabilities.py | 507 |

### tools/gscript.py

shared module; imported by 653 file(s): `tools/allterms.py`, `tools/bench/allterms_s1.py`, `tools/bench/allterms_s2.py`, `tools/bench/allterms_s3.py`, `tools/bench/allterms_s4.py`, `tools/bench/allterms_tmscclass.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `COMPoisoned` | (class) | A previous COM call hit its hard timeout and is STILL OUTSTANDING inside LabVIEW. | docstring | - | 115 |
| `poisoned` |  | The poison record (dict) or None. Read-only; never touches COM. | docstring | - | 125 |
| `clear_poison` |  | Forget the poison WITHOUT restarting LabVIEW. Only correct when the abandoned call is known to | docstring | - | 130 |
| `lv` |  | The module's LabVIEW.Application COM object, dispatched on first use and cached; _check_poison runs first (raises COMPoisoned while an abandoned COM call is still outstanding). Returns the COM object. | side file | - | 220 |
| `OpHygieneRefused` | (class) | A NEW op VI (file newer than OP_HYGIENE_SINCE) has no PASS op-hygiene record matching its md5. | docstring | - | 241 |
| `hygiene_probe` | op_path | THE ONLY EXEMPTION from the op-hygiene gate: inside this block 'op(op_path)' is admitted without a record, so | docstring | - | 246 |
| `op_hygiene_record_path` | path | Path of an op VI's hygiene record: tools/bench/op_hygiene/<op file name without extension>.json. Returns str. | side file | - | 258 |
| `op_hygiene_check` | path | None if 'path' may be opened as an op VI; else the refusal text. Pure file reads, no COM. | docstring | - | 262 |
| `op` | path | A cached VI reference. Op VIs are non-reentrant, so one reference each is correct. | docstring | - | 305 |
| `lv_counts` |  | {handles, private, gdi, user} of the LabVIEW process (first instance), Nones when it is not running. | docstring | - | 329 |
| `hygiene_run` | op_path, workload, source, total=2000, per_round=100, recycle=True, check=None, warm=None, card='', log='', workload_... | THE op-hygiene measurement: 'total' calls of 'workload(copy)' (ONE op call on an open copy; returns ''/None when good, else an | docstring | - | 366 |
| `shutil_copy` | src, dst | Copies file src to dst (shutil.copyfile, data only) then sleeps 0.2 s. Returns None. | side file | - | 436 |
| `ref_counts` |  | {opened, closed, live, cached_op_vis} - VI Server references opened by THIS process through this | docstring | - | 462 |
| `vi_ref` | target | A SHORT-LIVED, COUNTED VI reference to 'target', released when the block exits. | docstring | - | 473 |
| `reset` |  | Forget the Application AND every cached op-VI proxy. Call after LabVIEW is killed/restarted mid-script: | docstring | - | 491 |
| `cluster_array` | rows | Build the COM VARIANT for a LabVIEW '1-D ARRAY OF CLUSTERS' control. | docstring | - | 523 |
| `report` | target, cls | Every object of 'cls' on target's block diagram, as dicts with class/uid/pos/owner. | docstring | - | 698 |
| `report_all` | target, cls | Every object of 'cls' on target's block diagram in ONE op run - the array-returning form of report(). | docstring | - | 731 |
| `subvis` | target, diagram_index, purge=False, strict=True, **controls | Every subVI call on ONE diagram of 'target', as [{uid, name, path}] in one op run - the cast-free identity | docstring | - | 768 |
| `node_labels` | target, diagram_index, strict=True, **controls | The LABEL TEXT of every node on one diagram of 'target', as [{uid, label}] in one op run - cast-free | docstring | - | 830 |
| `loop_cast` | target, index, class_name='ForLoop' | A ForLoop-TYPED look at the 'index'-th loop of 'target' (Traverse class 'class_name', 'ForLoop' or | docstring | - | 869 |
| `loop_par_set` | target, index, enable, class_name='ForLoop' | WRITE ForLoop 'Is Parallelism Enabled?' (6362004) on the 'index'-th loop of Traverse class 'class_name' of | docstring | selftest_opforlooppar_v0.py | 912 |
| `add_shift_reg` | target, loop_index, y_position=120, class_name='WhileLoop' | CREATE a shift register on the loop_index-th loop of Traverse class 'class_name', returning the new | docstring | - | 940 |
| `wire_sr` | variant, target, loop_index, reg_index, node_index=None, term_index=None, ctl_index=None, class_name='WhileLoop' | Wire ONE side of the reg_index-th shift register of the loop_index-th 'class_name' loop (OpWireSR_*_v0, | docstring | - | 990 |
| `shift_reg` | target, loop_index, reg_index, class_name='WhileLoop' | The reg_index-th element of Loop.Shift Registers[] of the loop_index-th loop of Traverse class 'class_name' | docstring | - | 1036 |
| `shift_reg_left` | target, loop_index, reg_index, left_index=0, class_name='WhileLoop' | OpShiftRegs_v1: everything shift_reg() returns for the reg_index-th RIGHT register PLUS its LEFT side: | docstring | - | 1069 |
| `panel_wiring` | target | Every TOP-LEVEL front-panel object of 'target' with its diagram terminal's wiring, in one op run: | docstring | - | 1109 |
| `node_terms` | target, diagram_index, node_index | Every terminal of Nodes[node_index] on the 'diagram_index'-th Diagram of 'target', in ONE op run: | docstring | - | 1153 |
| `node_terms_uid` | target, diagram_index, node_index | (node_uid, rows) - node_terms plus the node's own UID even when it has no terminals (0 = index out of range). | docstring | - | 1208 |
| `node_terms_uids` | target, diagram_index, node_index | (node_uid, rows): node_terms' rows of Nodes[node_index] on Diagram[diagram_index] PLUS 'uid' = each Terminals[] | docstring | - | 1229 |
| `tunnels` | target, index | The 'index'-th LoopTunnel of 'target' (Traverse 'LoopTunnel' order - an access index, not an identity): | docstring | - | 1270 |
| `connect_ctl` | target, panel_index, node_index, terminal_index | Wire Nodes[node_index].Terminals[terminal_index] (a SOURCE) into the terminal of front-panel object | docstring | - | 1312 |
| `connect_ctl_ind` | target, sink_panel_index, src_panel_index | Wire the terminal of front-panel object Panel.Controls[src_panel_index] (a CONTROL, the source) into the terminal | docstring | - | 1338 |
| `count` | target, cls | Number of objects of class cls on target's diagram, read by one OP_REPORT run ('# of Refs'); raises RuntimeError on an op error. Returns int. | side file | - | 1363 |
| `uids` | target, cls | Set of uids of every object of class cls on target, from one report_all() op run. Returns set of int. | side file | - | 1375 |
| `new_since` | target, cls, before | The objects of 'cls' that appeared since the 'before' uid set. | docstring | - | 1382 |
| `loop_diagram` | target, loop_pos, min_margin=4.0 | The body Diagram of the For Loop at 'loop_pos', selected deterministically. | docstring | - | 1400 |
| `find_at` | target, cls, pos, tol=40 | Index of the 'cls' object nearest 'pos' - the deterministic selector. | docstring | - | 1419 |
| `exit_while` | target, stop_control, diagram_index, node_index=0, output_names=(), node_class='SubVI', shift_names=() | Finish a scripted While loop: wire its conditional terminal from the front-panel Boolean control labelled | docstring | - | 1441 |
| `queue_node` | kind, target, src_cls, src_index, src_name, diagram_index, location, element_name=None | Place one queue primitive on Traverse 'Diagram'[diagram_index] of 'target' (erdosmiller Create Obtain Queue / | docstring | - | 1480 |
| `loop_in` | kind, target, diagram_index, location, src_cls=None, src_index=0, src_names=(), indexing=(), parallel=0 | Create a For ('for') or While ('while') loop on Traverse 'Diagram'[diagram_index] of 'target' (OpForLoopIn_v0 / | docstring | - | 1513 |
| `while_loop` | target, location, tunnels=(), indexing=() | Create a While loop on 'target''s top-level diagram at 'location' (erdosmiller Create While Loop.vi through | docstring | - | 1549 |
| `for_loop` | target, location, tunnels=(), indexing=(), parallel=0 | Creates a For Loop on target at location via OP_FORLOOP with tunnels from the named controls, their indexing flags and the static parallel-instance count; ensure_loaded first, RuntimeError on an op... | side file | - | 1568 |
| `drop_subvi` | target, subvi_path, diagram_index, location | Place 'subvi_path' on the target's 'diagram_index'-th Diagram. Get the index from find_at. | docstring | - | 1583 |
| `open_panel` | target, activate=False | Open the target's front panel - REQUIRED before wire() AND before drop_subvi(). | docstring | - | 1599 |
| `close_panel` | target | Close the target's front panel. SAVE FIRST: closing the panel of a modified VI | docstring | - | 1615 |
| `ensure_loaded` | target | Put 'target' into the state in which scripting EDITS actually land, before every edit. Idempotent, once | docstring | - | 1626 |
| `wire` | target, src_cls, src_i, src_term, dst_cls, dst_i, dst_term, branch=False | Node-to-node wire by terminal name. Call open_panel(target) first, and save | docstring | - | 1698 |
| `revert` | target | Discard a VI's in-memory changes by reloading from disk (VI method Revert). | docstring | - | 1751 |
| `copy_into` | donor, label, target, prepare=None | Copy the object labeled 'label' from 'donor' INTO 'target'. | docstring | - | 1757 |
| `restore_move_fixtures` |  | Put the two Move-example files back to their pristine bytes - ONLY when nothing of theirs is loaded (call it | docstring | - | 1823 |
| `copy_by_index` | donor, cls, index, target, expect_uid=None, finish=None | Copy the 'index'-th object of Traverse class 'cls' (report() order) from 'donor' INTO 'target' BY REFERENCE — | docstring | - | 1837 |
| `move_by_label` | donor, label, harvest_to=None | Copy the GObject labeled 'label' out of 'donor' via OpMoveByLabel_v0. | docstring | - | 1919 |
| `ensure_move_files_pristine` |  | Restore the Move example's Test-Source if a previous run left a donor in it. | docstring | - | 1965 |
| `remove_bad_wires` | target | Edit > Remove Broken Wires on 'target' (the Ctrl+B cleanup). | docstring | - | 1987 |
| `delete_by_label` | target, label, allow_broken=False | Delete the object labeled 'label' from 'target' (Generic:Delete). | docstring | - | 2023 |
| `exit_loop` | target, node_index, output_names, diagram_index, node_class='SubVI' | Create AUTO-INDEXED output tunnels for 'output_names' of a node inside a loop. | docstring | - | 2079 |
| `wire_indicators` | target, node_index, src_terms, indicator_names, diagram_index=0, node_class='SubVI' | Branch a node's output terminals onto EXISTING front-panel indicators by label. | docstring | - | 2114 |
| `loop_kernel` | target, location, control_names, kernel_path, input_names, parallel=4 | ONE call: parallel For Loop + kernel subVI inside + named tunnel wiring. | docstring | - | 2162 |
| `set_index_mode` | target, tunnel_index, mode | Write a LoopTunnel's IndexMode in 'target' (0 = regular/non-indexed, 1 = auto-indexed). | docstring | - | 2213 |
| `tunnel_indicator` | target, tunnel_index | Create a front-panel INDICATOR wired to LoopTunnel[tunnel_index] of 'target', typed by LabVIEW. | docstring | - | 2240 |
| `wire_control` | target, control_names, dst_cls, dst_i, dst_terms, branch=False, src_diagram_index=0 | Wire FRONT-PANEL CONTROLS to a node's named inputs - the one thing OpWire_v1 | docstring | - | 2286 |
| `wire_const` | target, src_cls, src_i, dst_cls, dst_i, dst_term_index, labels=None | A BARE DIAGRAM CONSTANT as the SOURCE of a new wire (card 85-1, Pre-decided 188(c)). | docstring | - | 2340 |
| `wire_const_sr` | target, const_cls, const_i, loop_cls, loop_i, face_index, labels=None | Card 123-3 S2 (PD246(e)): SHIFT-REGISTER INITIALISATION - a bare diagram constant -> the LEFT register's OUTER face. | docstring | - | 2351 |
| `loop_face_index` | target, diagram_uid, loop_uid, face_uid | The Terminals[] index of terminal #face_uid on loop #loop_uid (a node of Diagram #diagram_uid), by UID ECHO through | docstring | - | 2362 |
| `sr_init_const` | target, loop_uid, face_uid, diagram_uid, donor, pos=(40, 40), loop_cls='WhileLoop' | Card 123-3 S2 (PD246(c) A3 / (e)): INITIALISE a shift register from a VALUED constant on the loop's OWNER diagram. | docstring | - | 2377 |
| `wire_ctlsink` | target, ct_i, src_cls, src_i, src_term_index, labels=None | PD191(a): a FRONT-PANEL TERMINAL as the SINK (Connect Wire invoked on it), a bare node terminal as the source. | docstring | - | 2408 |
| `wire_tunouter` | target, tun_cls, tun_i, dst_cls, dst_i, dst_term_index, labels=None | PD191(b): a structure TUNNEL's OUTER face as the source, addressed by the TUNNEL (never by its owner's Terminals[]). | docstring | - | 2418 |
| `exec_state` | target | target's VI ExecState read through a short-lived counted vi_ref (0 = broken). Returns int. | side file | - | 2457 |
| `gui_save` | target | Save a BROKEN VI by focusing its window and sending Ctrl+S. | docstring | - | 2470 |
| `save` | target, allow_broken=False | Persist the in-memory edits. Guarded to claudeDev + explicit allowlist: an | docstring | - | 2595 |
| `build_kernel` | target, loop_at=(4000, 300), parallel=4, tunnel='Array of cal clusters', bead_vi='Track 1 of N bds xyz-kernel-reentra... | SUPERSEDED by loop_kernel(). Places an UNWIRED loop + kernel; kept for regression. | docstring | - | 2615 |
| `main` |  | CLI: 'report <vi> <class>' prints one line per object (index, class, uid, pos, owner); 'kernel <vi>' runs build_kernel; 'save <vi>' saves and prints the size. Returns 0, 2 on usage or an unknown co... | side file | - | 2664 |
| `build_invoke` | target, cls, method_id, location, diagram_index=0 | Create an Invoke Node on 'target''s diagram: class 'cls' ("VI Server:Terminal", "VI Server:VI", | docstring | - | 2692 |
| `build_property` | target, cls, props, location, diagram_index=0 | Create a Property Node on 'target''s diagram: class 'cls' ("VI Server:GObject", ...), | docstring | - | 2727 |
| `delete_object` | target, cls, index, verify=True | Delete the 'index'-th object of Traverse class 'cls' on 'target' (Generic.Delete over a | docstring | - | 2808 |
| `move_object` | target, cls, index, position | Move the 'index'-th object of class 'cls' (Traverse order, same as report()) on 'target' to the | docstring | - | 2869 |
| `build_index_array` | target, location, source_terminal_index=0 | Place an Index Array primitive on 'target''s top-level block diagram at 'location' (erdosmiller | docstring | - | 2892 |
| `node_rank` | target, uid | WRONG in general — kept as a warning. Nodes[] is CREATION order; uid rank matched it on GUIBENCH_v0 only | docstring | - | 2922 |
| `create_control` | target, node_index, terminal_index | Create a front-panel control wired to terminal 'terminal_index' (Node.Terminals[] order = the Context | docstring | - | 2930 |
| `create_indicator` | target, node_index, terminal_index | Indicator wired to terminal 'terminal_index' of Nodes[node_index] (Terminal.Create Indicator 6349C02 — | docstring | - | 2958 |
| `create_const_loop_term` | target, kind, index, value=None, term_index=0 | A DIAGRAM CONSTANT, typed by the sink and already wired, on a LOOP-OWNED terminal (task 77-2, 2026-09-25). | docstring | - | 2983 |
| `connect_terminals` | target, sink_node, sink_term, src_node, src_term | Wire Nodes[src_node].Terminals[src_term] (source) into Nodes[sink_node].Terminals[sink_term] (sink) on | docstring | - | 3028 |
| `fp_labels` | target, max_n=200 | [(index, label, is_indicator)] for every front-panel object of 'target' in tabbing order | docstring | - | 3058 |
| `node_info` | target, max_n=400 | [(Nodes[] index, style name, label text)] for the top-level block-diagram nodes of 'target' in | docstring | - | 3080 |
| `remove_bad_wires_scripted` | target | LabVIEW's Ctrl+B by script: VI.'Block Diagram:Remove Bad Wires' (410) on 'target' (OpRemoveBadWires_v0, | docstring | - | 3104 |
| `net_map` | target, diagram_index=0, max_nodes=200, max_terms=40 | Connectivity of one diagram of 'target' (Traverse "Diagram" index; 0 = top level), read headlessly with | docstring | - | 3123 |
| `print_net_map` | nodes, nets | Prints net_map() output: per node '[n] style / label', then per terminal the other node.terminals on its wire, or UNWIRED / '(wire w, no other terminal in this diagram)'. Returns None. | side file | - | 3227 |
| `set_auto_error_handling` | target, enabled | Write VI.'Automatic Error Handling' (242) of 'target' — OpSetAutoErr_v0 (2026-09-07). FALSE silences the | docstring | - | 3238 |
| `connect2` | target, diagram_index, sink_node, sink_term, src_node, src_term | Wire top-level Nodes[src_node].Terminals[src_term] into Nodes[sink_node].Terminals[sink_term] of ANY diagram | docstring | - | 3254 |
| `set_node_label` | target, diagram_index, node_index, text | Write the label of Nodes[node_index] of Traverse "Diagram"[diagram_index] on 'target' (OpSetLabel_v0, built by | docstring | - | 3277 |
| `move_out` | target, diagram_index, node_index, position | Move Nodes[node_index] of Traverse "Diagram"[diagram_index] to the TOP-LEVEL diagram of 'target' at 'position' | docstring | - | 3295 |
| `build_clfn` | target, location, dll, fn, flat_hex, calling_convention=0, reentrant=True | Place a CLFN on 'target' calling 'fn' of 'dll' with the parameter list 'flat_hex' (flattened Parameter Info array, | docstring | - | 3317 |
| `conpane` | target, max_terminals=32 | The connector pane of 'target' as {terminal index: control label}, with None for a FREE terminal (OpConPane_v0, | docstring | - | 3365 |
| `replace_object` | target, uid, new_path | Swap the object 'uid' on 'target''s diagram for the subVI (or control) at 'new_path', in place - the callee-swap | docstring | - | 3396 |
| `conpane_assign` | target, control_label, terminal_index | Assign the front-panel control 'control_label' of 'target' to connector-pane terminal 'terminal_index' | docstring | - | 3422 |
| `make_default` | target, values=None | Set 'values' ({control label: value}) on 'target' through VI Server, then make ALL current front-panel values the | docstring | - | 3456 |
| `build_case` | target, location, selector_name, input_names=(), frame_names=('0, Default', '1') | Place a Case Structure on 'target''s top-level diagram (erdosmiller 'Create Case Structure.vi' via OpBuildCase_v1, | docstring | - | 3498 |
| `connect_nested_v2` | target, sink_diag, sink_node, sink_term, src_diag, src_node, src_term, labels=None | Wire Diagram[src_diag].Nodes[src_node].Terminals[src_term] (SOURCE) into | docstring | - | 3531 |
| `case_frames` | target, case_uid | T1 READER (OpCaseFrames_v1): CaseStructure #case_uid -> {'echo', 'names' (Frame Names 6365002, frame order), | docstring | - | 3666 |
| `case_in` | target, diagram_uid, location, selector_label, frame_names=('0, Default', '1'), position=None | T1: a Case Structure OWNED BY a nested diagram (a For/While body), addressed by the diagram's UID. | docstring | - | 3695 |
| `tunnel_use_default_at` | target, cls, index, value | T5 by Traverse (cls, index): OpTunnelUseDefault_v0 casts to ConditionalTunnel, READS 5D251C00, WRITES 'value', | docstring | - | 3733 |
| `tunnel_use_default` | target, tunnel_uid, value, cls='SelectorTunnel' | T5: set 'Use Default if Unwired' (ConditionalTunnel 5D251C00, NAMES.md:1036) on case tunnel #tunnel_uid and read | docstring | - | 3749 |
| `set_control_label` | target, panel_index, text | T4: write the LABEL of front-panel object Panel.Controls[panel_index] (= panel_wiring row order) through | docstring | - | 3758 |
| `set_default_in_memory` | target, label, value, probe_value | T4 default: SetControlValue(label, value) -> OpMakeDefault_v0 (VI 'Make Current Values Default' 3F3, ALL controls) | docstring | - | 3775 |
| `c97_collapsed` | rows, tunnel_uids | {(source term uid, sink term uid)} with each tunnel in 'tunnel_uids' collapsed to a pass-through. | docstring | - | 3803 |
| `MoveIntoFrameBroken` | (class) | move_into_frame's post-edit gate refused (card 98-2 PD207(c); card 98-3 PD208(c)); '.result' holds the full | docstring | - | 3815 |
| `MoveIntoFrameRefused` | (class) | PD208(c)(1) PRECONDITION (card 98-3): ExecState was not 1 BEFORE the move, so the verb refused BEFORE ANY EDIT - | docstring | - | 3824 |
| `wire_health` | target, rows=None | READER (card 98-2): {wires, wired, termless, exec_state} of 'target'. termless = Wire objects that carry NO terminal | docstring | - | 3835 |
| `move_into_frame` | target, frame_uid, members, spot=(0, 0), log=None, expect_broken=False, _skip_rbw=False | PD208(c) (card 98-3; AMENDS card 98-2's PD207(c) termless-only deletion, which left ExecState 0 after move A - | docstring | selftest_c98_stage | 3846 |
| `move_into_frame_finish` | target, frame_uid, r, log=None, expect_broken=False, _skip_rbw=False | PD208(c)(2)-(4), the post-move step of move_into_frame (see its docstring). 'r' = _move_into_frame's result, or | docstring | - | 3877 |
| `create_indicator_nested` | target, node_uid, terminal_index | V1: an INDICATOR wired to Terminals[terminal_index] of node #node_uid on ANY diagram (Terminal.Create Indicator | docstring | - | 4166 |
| `create_control_nested` | target, node_uid, terminal_index, value=None | V2: a CONTROL wired to Terminals[terminal_index] of node #node_uid on ANY diagram (Terminal.Create Control | docstring | - | 4349 |
| `set_visible` | target, uid, visible | V3: write Control.Visible of front-panel object #uid (a panel_wiring row uid) and READ IT BACK in the same op | docstring | - | 4365 |
| `read_bool_const` | target, uid | V4: the value of BooleanConstant #uid (Constant.Value 634AC00 on a BooleanConstant-TYPED node - the base class | docstring | - | 4391 |
| `read_const_value` | target, uid | Card 118-4 R1 (PD234(j)(1)): READ-ONLY value + type of diagram constant #uid, class found by traverse membership. | docstring | - | 4417 |
| `const_class_index` | target, uid | (class, Traverse index) of constant #uid: the first CONST_IND_CLASSES listing that holds it, else ValueError. | docstring | - | 4520 |
| `create_indicator_on_const` | target, const_uid, label=None | card 122-3: a NEW indicator wired to the output terminal of diagram constant #const_uid (any diagram) through | docstring | - | 4529 |
| `const_indicator_on_diagram` | target, diagram_uid, donor, label, pos=(40, 40) | card 122-3 ROUTE (PD241(a)): a VALUED constant on Diagram #diagram_uid (any nesting depth; a flat-sequence frame | docstring | - | 4571 |
| `parse_type_descriptors` | b | The TYPE half of a flattened LabVIEW variant (layout measured, docs/NAMES.md:1153-1155): U32 version, I32 nTDs, | docstring | - | 4591 |
| `read_term_type` | target, term_uid, index=None | Card 120-2 T2 (PD237(k)): READ-ONLY data type of terminal #term_uid (any GObject of class Terminal, e.g. a node's pin, | docstring | - | 4646 |
| `wire_joints` | target, wire_uid, index=None | Card 117-1 S0a: 'Wire.Joints[]' 6371005 of Wire #wire_uid through OpWireJoints_v1 (md5 29dcb59f...; built by | docstring | - | 4679 |
| `create_local_read` | target, panel_index, dest_diagram_uid=None, position=(40, 40) | Cycle 102 (stage_d1_disp_r6.log:544,572,595): the READ twin of create_local_write - OpCreateLocalRead_v0 with | docstring | - | 4707 |
| `create_local_write` | target, panel_index, dest_diagram_uid=None, position=(40, 40) | V5 core: a Local Variable in WRITE mode bound to Panel.Controls[panel_index] (OpCreateLocalRead_v0 with | docstring | - | 4715 |
| `create_primitive_nested` | target, diagram_uid, prim_name, pos, donor=None | V6 (card 100-4, PD213(b)): place primitive 'prim_name' on Diagram #diagram_uid of 'target' (ANY nesting depth) | docstring | - | 4790 |
| `fs_donor` |  | {'donor': claudeDev\DonorFs_v0.vi, 'uid': its FS uid} for struct_copy_nested (a 1-frame, EMPTY Flat Sequence). | docstring | - | 4904 |
| `fs_frames` | target, fs_uid, max_frames=200 | OpFsDiagrams_v0: the frame Diagram uids of Flat Sequence #fs_uid, LEFT TO RIGHT (Diagrams[] index k = 0, 1, ... until the | docstring | - | 4910 |
| `fs_add_frame` | target, fs_uid, ref_index, after=True | OpFsAddFrame_v0: FlatSequence.Add Frame 3578B800 on Flat Sequence #fs_uid ('Reference Frame Index' = ref_index, 'After(T)'); the | docstring | - | 4933 |
| `wire_remove_loose_ends` | target, wire_uid, index=None | 'Wire.RemoveLooseEnds' (6370C08) on Wire #wire_uid of 'target' through OpWireRemoveLooseEnds_v0. 'index' = the | docstring | - | 4980 |
| `term_index` | target, diagram_uid, node_uid, name, is_source | Card 123-7 (PD248(b)): (diagram index, node index, terminal index, row) of the ONE terminal named 'name' with direction | docstring | - | 4999 |
| `struct_copy_nested` | target, diagram_uid, cls, donor, pos=(40, 40) | Copy structure 'donor['uid']' (class 'cls') of the claudeDev file 'donor['donor']' onto Diagram #diagram_uid of 'target' | docstring | - | 5016 |
| `case_wired` | target, diagram_uid, src_node_uid, src_term, pos=(40, 40), donor=None | Card 123-5 S1: a Case structure on Diagram #diagram_uid whose SELECTOR is wired from output terminal 'src_term' (name) | docstring | - | 5078 |
| `connect_term_uid` | target, sink_uid, src_uid | OpConnectTermUid_v0: Terminal.Connect Wire on terminal #sink_uid with Wire Source = terminal #src_uid (any owner, any | docstring | - | 5141 |
| `case_inner_face` | target, tunnel_uid, frame_index | The inner terminal of tunnel #tunnel_uid in frame 'frame_index' of its case (case_frames' Frames[] order; a boolean | docstring | - | 5166 |
| `case_frame_wire` | target, case_uid, frame_index, src, dst | A wire on frame 'frame_index' of case #case_uid. 'src' / 'dst' = {"tunnel": uid} (that tunnel's inner face in this | docstring | - | 5187 |

### tools/hash_probe.py

shared module; imported by 64 file(s): `tools/bench/c52_astcheck.py`, `tools/bench/diag_c60_castseed_probe.py`, `tools/bench/diag_c60_n4_localbinding.py`, `tools/bench/diag_c61_localdir.py`, `tools/bench/diag_c61_localdir_write.py`, `tools/bench/diag_c61_localdir_write2.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `probe` | path | One 'HASH <path> / exists=1 / size=n / md5=.. / sha256=..' line for a file read in 1 MiB chunks; 'exists=0' with '-' fields when it is not a file. Returns str. | side file | - | 19 |
| `main` |  | CLI: prints probe() for each path on argv. Returns 0, 2 (with a usage line) when no path is given. | side file | - | 36 |

### tools/invcheck.py

shared module; imported by 9 file(s): `tools/bench/diag_c156_b2_2_inv_c156a21.py`, `tools/bench/diag_c159_b1_1.py`, `tools/bench/prep_c162_a2_1_pinsweep.py`, `tools/bench/prep_c162_a2_2_check.py`, `tools/bench/prep_c162_a2_3_copies.py`, `tools/bench/prep_c162_a2_3_equiv.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `md5` | path | Full md5 hex of a file, or 'MISSING' when it does not exist. Self-test: selftest_c156_b2_2_invcheck.py (pin gates). | docstring | selftest_c156_b2_2_invcheck.py | 28 |
| `Gates` | (class) | GATE counter: g(label, ok, detail) prints 'GATE PASS/FAIL / label / detail' and records it; .rows, .passed, .failed, .first. | docstring | selftest_c156_b2_2_invcheck.py | 39 |
| `Gates.result` | artefacts=() | The RESULT line text (protocol.result_line, schema result-line/1) for the gates so far. Self-test: selftest_c156_b2_2_invcheck.py. | docstring | selftest_c156_b2_2_invcheck.py | 57 |
| `card_pins` | card_path, exempt=(), root=ROOT | Card-input pins: list of (path, md5) from the card JSON's inputs, path = os.path.join(root, input path) as written, minus 'exempt' | docstring | selftest_c156_b2_2_invcheck.py | 66 |
| `snapshot_files` | globs, exclude_names=SNAP_EXCLUDE, root=ROOT | {relpath with '/': md5} of every FILE matched by the glob patterns (relative to root, '**' recursive), basenames in | docstring | selftest_c156_b2_2_invcheck.py | 79 |
| `run_inv` | mode, pins, snap_path, snap_globs, snap_label, card_path=None, exempt=None, main_recipe=None, listing_glob=None, scra... | Run one inv check and return the Gates (caller exits with gates.failed and 1 or 0). mode 'before' writes the snapshot, 'after' | docstring | selftest_c156_b2_2_invcheck.py | 97 |
| `main_inv` | argv=None, **config | Thin-caller entry: mode from argv[1] (default 'before'), run_inv(mode, **config), returns the exit code (1 if any gate FAILED). | docstring | selftest_c156_b2_2_invcheck.py | 138 |

### tools/jev.py

shared module; imported by 33 file(s): `tools/addrcheck.py`, `tools/audit_cycle.py`, `tools/bench/diag_c106d_jevrc2.py`, `tools/bench/jev_discharge_trial.py`, `tools/bench/jev_gate.py`, `tools/bench/jev_ladder_c89.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `get_key` |  | The TypeSafe API key from env TYPESAFE_API_KEY, else from the user Environment registry key (HKCU); None when neither has it. Returns str or None. | side file | - | 33 |
| `ask` | state, questions, purpose='unspecified', timeout=60, retries=3 | POST one request. Returns (response_dict, None) or (None, error_string). Never raises. | docstring | - | 64 |
| `samples` | default=SAMPLES_DEFAULT | How many times one question is asked before its answer is used. 'JEV_SAMPLES' overrides (1..25). | docstring | - | 104 |
| `ask_n` | state, questions, n=None, purpose='unspecified', timeout=60, retries=3 | CONSENSUS: ask ONE question 'n' times (sequentially, each with ask()'s own retries) and average. | docstring | - | 115 |
| `noul` | resp, name=None | The yes-probability of a noul answer (by question name when given), or None. | docstring | - | 179 |
| `choice` | resp, name | (chosen option, probabilities dict) of a choice answer, or (None, None). | docstring | - | 199 |
| `verdict` | p | 'yes' / 'no' / 'unknown' from a probability, using the project's unknown band. | docstring | - | 208 |
| `normalise` | s | Text with volatile parts masked: 32-hex md5 -> '<md5>', timestamps -> '<ts>', '#n' and numbers of 3+ digits -> '#', the project root path -> '<root>'. Returns str. | side file | - | 229 |
| `summarise_failure` | logpath, run_index=-1 | Compact failure summary of ONE bgrun log's LAST run: script, how it ended, first FAIL line + context (or | docstring | - | 237 |
| `same_failure_class` | summary_a, summary_b, purpose='same-failure-class', n=None | Probability that two failure summaries are the same failure class (measured 92.5 % / Brier 0.059 on the | docstring | - | 305 |

### tools/jev_candidates.py

shared module; imported by 107 file(s): `tools/bench/c73_l7r_live.py`, `tools/bench/cdiff_blindspot_74.py`, `tools/bench/cdiff_frame_80_probe.py`, `tools/bench/ct23541_facts_80.py`, `tools/bench/dedupe_check_s2b.py`, `tools/bench/diag_c104_e3.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `node_labels_default` |  | {uid: label} from tools/bench/main_vi_node_labels.json (every diagram's rows); {} when the file is absent. Returns dict. | side file | - | 63 |
| `load` | key, fs=True | The step-4 graph of one wiki VI, built exactly as tools/bench/diag_vigraph_check.py builds it | docstring | - | 73 |
| `from_parts` | rec, objs, loops, labels, fs_pairs, key | The same graph from parts already in memory (a LIVE read of a scratch VI: 'rec' needs 'terminals' and, | docstring | - | 87 |
| `diagram_tree` | G | {parent: {child: parent}, exclusive: {frame: frozenset(sibling frames of the same case)}}. | docstring | - | 102 |
| `scope` | G, da, db | (relation, borders) between two diagrams. borders = structure borders a wire would cross. | docstring | - | 133 |
| `structure_terminals` | G, struct_uid | HEURISTIC: the border-tunnel group of a structure = tunnels sharing inner frames, the group chosen by a | docstring | - | 157 |
| `resolve` | G, end | An intent end -> ([node uids], method). | docstring | - | 180 |
| `sink_state` | G, r | State of a sink terminal row r in graph G: 'free' (wire_uid 0), 'half-wire' (wire in G['halfwire_nosrc']), else 'occupied'. Returns str. | side file | - | 194 |
| `cut_input_tunnel` | G, node | FACT RULE (judgement 2026-09-23 16:xx, measured by bench 5b B run 2): a Selector/Loop tunnel whose OUTER | docstring | - | 206 |
| `term_row` | G, key | Candidate dict of terminal row key in G: key, uid, term, term_uid, term_class, owner_class, diagram, wire_uid, subvi; a tunnel owner also gets outer_wire (its OuterTerminal's wire uid). Returns dict. | side file | - | 223 |
| `candidates` | G, intent | Every legal pair for ONE intent row. Returns {intent, resolved, pairs:[...], excluded:{reason: n}}. | docstring | - | 236 |
| `map_key` | G, key_other, G_other | The key in G of a terminal named by 'key_other' in another graph (Pre-decided 137: node uid + terminal | docstring | - | 272 |
| `s1_chains` | S1, node_uid | RULE-CHAIN-S1 (CLAUDE.md §3 "Stages are SIMULATED", decision 3; docs/stage-simulator-plan.md "Decide per row"): | docstring | - | 288 |
| `chain_terminals` | S1, node_uids | {(uid, term)} every terminal a RULE-CHAIN-S1 chain of these nodes owns - the node's out/in ends and the | docstring | - | 327 |
| `rule_chain_s1` | S1, node_uid, new_sr | The chain rows for 'node_uid' moved into a new loop whose new register pairs are 'new_sr' | docstring | - | 340 |

### tools/jev_chain.py

shared module; imported by 1 file(s): `tools/bench/jev_menus_step5.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `subvi_nodes_in_scope` | G, root_diagram | SubVI call nodes whose terminals sit on 'root_diagram' or on any diagram below it in the tree. | docstring | - | 47 |
| `direct_successors` | G, y | SubVI nodes reached from y's outputs without passing THROUGH another subVI node. | docstring | - | 57 |
| `reaches` | G, a, b | True when node b is among the nodes reachable from node a (vigraph.reach4). Returns bool. | side file | - | 75 |
| `true_next` | G, y, z, x | True when x is a direct subVI successor of y and x is z or reaches z. Returns bool. | side file | - | 79 |
| `subvi_line` | G, u | One text line for subVI node u: '#u name; pane: label (direction), ...' (first 16 connector-pane rows from the wiki, or '(not in the wiki)') plus the wiki summary. Returns str. | side file | - | 83 |
| `ask_link` | G, y, z, x, n=None | Asks Jev (ask_n, CHAIN_Q, purpose step5-chain) whether candidate x is the next link from y toward z, with subvi_line texts as state. Returns ask_n's (mean p, spread, err). | side file | - | 91 |
| `build_chain` | G, y, z, root_diagram, max_steps=8, n=None, th=None | Follow Jev one step at a time. Returns {steps:[{at, scored, chosen, action}], reached, jev_calls}. | docstring | - | 96 |
| `scope_counts` | G, root | {subVI name: number of call nodes} over the subVI nodes in scope below diagram root. Returns dict. | side file | - | 124 |

### tools/jev_contradict.py

shared module; imported by 3 file(s): `tools/audit_cycle.py`, `tools/bench/jev_wave2b_trials.py`, `tools/bench/jev_wave4_selftest.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `parse_items` | path=PLAN | [{'id','title','body','text'}] - every top-level numbered item in the document, in order. | docstring | - | 72 |
| `build_pairs` | items, per_item=8, min_shared=2, cap=400, df_frac=0.15 | [(score, i, j)] with j < i: the most-overlapping earlier item for each item, capped and sorted. | docstring | - | 106 |
| `ask_pair` | a_text, b_text, samples=3, timeout=25, retries=0, purpose='contradict' | (mean p, [samples], err). 3-sample consensus by default (second-wave #6). | docstring | - | 129 |
| `main` | argv=None | CLI: parses a plan's numbered items, builds token-sharing pairs (cap --pairs, max 600), asks Jev per pair (--samples), prints the top pairs and those at p >= --threshold, writes the readings JSON (... | side file | - | 158 |

### tools/jev_device_value.py

shared module; imported by 2 file(s): `tools/bench/jev_device_value_labels.py`, `tools/bench/selftest_jev_device_value.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `corpus` | since=None | Failure corpus: retrospective VIOLATION lines (with loss_min/usd) and FINDINGS paragraphs from archive/peer, plus first failing lines of failed bench bgrun logs, jev-normalised and deduplicated, op... | side file | - | 39 |
| `classify` | device, items, n=None, workers=4, ask=None | Asks Jev (default ask_n, 4 threads) for each item whether the device prevented / reduced / is unrelated to it. Returns the items with answer (winning class or 'unknown'), p and spread added. | side file | - | 70 |
| `totals` | rows | Per-class counts, loss_min/loss_usd sums for prevented plus half of reduced (expected), the date span in days and expected loss minutes per day. Returns dict. | side file | - | 81 |
| `main` | argv=None | CLI: --device text [--since/--after date, --slug, --dry, --reprint]: builds the corpus, classifies it (or reloads the saved JSON), prints one row per item and TOTALS, writes device_value_<slug>.jso... | side file | - | 93 |

### tools/jev_drift.py

shared module; imported by 4 file(s): `tools/bench/jev_wave2b_trials.py`, `tools/bench/jev_wave3a_trials.py`, `tools/bench/selftest_guard_bash_jev.py`, `tools/hooks/guard_bash.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `next_block` | status_path=STATUS, maxchars=NEXT_MAX, text=None | THE WHOLE '## NEXT' section of STATUS.md, blank lines dropped, bullets kept IN ORDER, truncated to | docstring | - | 107 |
| `first_act` | status_path=STATUS, maxchars=FIRST_ACT_MAX, text=None | SUPERSEDED IN THE LIVE PATH 2026-09-22 by next_block(); KEPT because tools/bench/jev_wave2b_trials.py is | docstring | - | 128 |
| `recent_commands` | n=5, marker_log=MARKER_LOG | The last n commands this project's material-marker recorded, oldest first. [] on any failure. | docstring | - | 158 |
| `is_run_command` | cmd | True when the command RUNS something (bgrun / a recipe or bench script / a peer dispatch). | docstring | - | 172 |
| `judge` | cmd, act=None, recent=None, timeout=20, retries=0, purpose='drift', n=None | (p, what, err). p is the CONSENSUS mean probability that the command advances something the cycle's | docstring | - | 215 |
| `advisory` | cmd, sid='0', write_log=True | The hook entry point. Returns the advisory line (also written to stderr and jev_gate.log) or None. | docstring | - | 249 |

### tools/jev_gaterow.py

shared module; imported by 10 file(s): `tools/bench/jev_gate.py`, `tools/bench/jev_ladder_c89.py`, `tools/bench/jev_ladder_c89b.py`, `tools/bench/jev_ladder_c90.py`, `tools/bench/jev_ladder_remeasure.py`, `tools/bench/jev_wave2a_trials.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `classify` | state, purpose='gaterow', n=None, timeout=60, retries=3 | (class, mean probability, spread) for ONE row's state. Never raises. | docstring | - | 37 |
| `main` | argv | CLI: '<bgrun log> [--run i] [--json out]': one Jev class per FAIL row of that run, printed as and appended to jev_gate.log as JEV-GATEROW lines; optional JSON of the verdicts. Returns 0, 2 on usage... | side file | - | 49 |
| `verdicts_for` | logpath, run_index=-1, max_rows=5, n=2, timeout=25, retries=1 | The gate-row verdicts of one run as a compact text block, for the review ladder's state. Never raises. | docstring | - | 91 |

### tools/jev_pairs.py

shared module; imported by 7 file(s): `tools/bench/jev_l7_1_offline.py`, `tools/bench/jev_menus_step5.py`, `tools/jev_chain.py`, `tools/recipes/stage_d1_l7_1.py`, `tools/recipes/stage_d1_l7_1b.py`, `tools/recipes/stage_d1_l7_r.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `thresholds` |  | The Jev menu thresholds from tools/bench/jev_menu_thresholds.json; when unreadable, defaults (pair/op/chain act 0.90, risk 0.10, none acting). Returns dict. | side file | - | 46 |
| `subvi_record` | name | The wiki JSON of a subVI by its call-node name ('X.vi'), or None when it is not in the wiki. | docstring | - | 69 |
| `wiki_line` | t | ONE line for one terminal row (jev_candidates.term_row): node, class, subVI name + the matching | docstring | - | 83 |
| `pair_state` | intent_line, c | The PAIR question state of candidate c: {intent, candidate (source -> sink text with sink state, scope, borders), src_wiki, dst_wiki (wiki_line)}. Returns dict. | side file | - | 121 |
| `ask_pair` | intent_line, c, n=None | Asks Jev (ask_n, PAIR_Q, purpose step5-pair) whether candidate c is the pair the intent line asks for. Returns (mean p, spread, err). | side file | - | 130 |
| `op_options` | c | <= 3 exclusive options, chosen by the row's CLASSES only (a hard fact, not a ranking). | docstring | - | 163 |
| `op_rule` | c, top_diagram=None | PRE-DECIDED 143 as code: the writer op chosen by the row's CLASSES; (op, variant, why) or (None, None, why) | docstring | - | 181 |
| `op_question` | opts | The Jev 'choice' question over writer ops: fixed instructions plus criteria = OP_MENU descriptions of the given option names. Returns dict. | side file | - | 223 |
| `op_state` | c | The OP question state of candidate c: {'row': 'SOURCE #uid ... -> SINK #uid ...; scope s'}. Returns dict. | side file | - | 233 |
| `ask_op` | c, n=None | Asks Jev to choose the writer op for candidate c among op_options(c). Returns (best op or None, probabilities or None, options, err). | side file | - | 241 |
| `ask_risk` | change_line, evidence, n=None | Asks Jev (RISK_Q, purpose step5-risk) whether the change line with its code-computed evidence changes the original's computation. Returns (mean p, spread, err). | side file | - | 269 |
| `risk_evidence` | G_orig, G_new, c, orig_sink_key=None | Code-computed rule-1a evidence for wiring candidate c in G_new: the effective computation sources of the | docstring | - | 275 |
| `decide` | intent_line, cand, G_orig=None, G_new=None, orig_sink_key=None, n=None, th=None, by_rule=False, risk_gates=True, top_... | Run PAIR over every candidate, then OP and RISK on the chosen one. Returns one decision dict. | docstring | - | 289 |
| `write_record` | stage, bed_md5, intents, cands, decisions, t0, extra=None | Writes tools/bench/decision_<stage>.json: bed md5, intents, candidate pairs (row keys and facts), decisions, summed jev_calls, estimated cost and seconds since t0, thresholds, plus extra. Returns (... | side file | - | 370 |

### tools/jev_preflight.py

shared module; imported by 3 file(s): `tools/bench/jev_wave2b_trials.py`, `tools/bench/selftest_guard_bash_jev.py`, `tools/hooks/guard_bash.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `static_checks` | path | The five checks. Returns (dict of results, list of one-line findings). Never raises. | docstring | - | 155 |
| `classify` | path, timeout=25, retries=0, purpose='preflight' | (cls, p, findings, res, err). ONE Jev choice over the head + the static findings. | docstring | - | 228 |
| `line_for` | path, timeout=25 | The one-line advisory, or None. Never raises. | docstring | - | 250 |
| `advisory` | script_path, write_log=True | The hook entry point: print and log one line for a recipe/stage launch. Returns the line or None. | docstring | - | 263 |
| `main` | argv=None | CLI: '<file>': classify() it, prints each finding and one 'JEV-PREFLIGHT / <file> / class p=.. / finding ids' line (or '(no reading: err)'). Returns 0, 2 with a usage line when no argument is given. | side file | - | 281 |

### tools/jev_rowcheck.py

shared module; imported by 3 file(s): `tools/bench/jev_wave2b_trials.py`, `tools/bench/jev_wave4_selftest.py`, `tools/stagekit.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `load_tables` | sources=SOURCES, nodeterms=NODETERMS | (rows, by_uid) - the 109 cut-terminal rows and a uid -> list-of-measured-entries index. | docstring | - | 79 |
| `row_text` | row | One readable line for a planned row. | docstring | - | 114 |
| `entries_for` | row, by_uid, limit=12 | (measured source entries, measured sink entries) - only the rows mentioning that uid. | docstring | - | 122 |
| `check_row` | row, by_uid, timeout=25, retries=0, purpose='rowcheck' | (p, verdict, err). verdict is 'ok' / 'suspect' / 'unknown' by the project's band. | docstring | - | 130 |
| `normalise_row` | row | Either accepted schema -> the schema 'check_row' reads (shape A), or None when neither fits. | docstring | - | 185 |
| `check_rows` | rows, by_uid=None, limit=None, budget_s=60.0, timeout=20, retries=0, purpose='rowcheck-stage' | Judge an IN-MEMORY row list. Returns [{i,label,verdict,p,err,text}]. Never raises, never blocks. | docstring | - | 206 |
| `stage_lines` | rows, stage_name, by_uid=None, limit=None, budget_s=60.0, write_log=True | The stagekit entry point: one 'JEV-ROWCHECK / <stage> / <row> / <class> p=<p>' line per row. | docstring | - | 252 |
| `main` | argv=None | CLI: '[rows json] [--limit n]' (default SOURCES): check_row on each planned row against the terminal tables, prints 'JEV-ROW / i / verdict p=..' lines and an ok/suspect/unknown TOTAL line. Returns ... | side file | - | 285 |

### tools/launchunit.py

shared module; imported by 7 file(s): `tools/bench/prep_c150_a2_4_stage_prerun_before.py`, `tools/bench/selftest_c111c_launchunit.py`, `tools/hooks/guard_bash.py`, `tools/hooks/guard_card.py`, `tools/hooks/guard_cycle.py`, `tools/stage_prerun.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `segments` | cmd | The command split into shell segments (&& // ; / newline), a line continuation (bash '\', PowerShell backtick) | docstring | - | 38 |
| `norm` | p, root=None | A path token -> normcase absolute path (relative ones against root). | docstring | - | 52 |
| `module_file` | mod, root=None | The project file '-m <mod>' would run from the project root, or None (a/b -> a/b.py / a/b/__main__.py / | docstring | - | 57 |
| `units` | cmd, root=None | Every python unit of the command: dicts {kind: 'script'/'module'/'module_arg', path, module, seg}. | docstring | - | 69 |
| `arg_is_launch` | mod, root=None | True unless '-m <mod>' only READS its arguments: mod in READONLY_MODULES and not a project-file shadow. | docstring | - | 114 |
| `launched_py` | cmd, root=None | Every script path the command RUNS: 'py X.py' (past interpreter flags, also after bgrun's '--'), a '-m' module | docstring | - | 119 |
| `module_arg_counts` | cmd, root=None | Counter {norm(path): n} of the .py tokens that are only ARGUMENTS of a read-only '-m' module. | docstring | - | 127 |
| `drop_module_args` | cmd, paths, root=None | The card-flag filter (guard_card): 'paths' = one entry per place another detector saw a launched .py. An entry | docstring | - | 133 |
| `cd_only_to_root` | cmd, root=None | True when every 'cd' segment of the command targets the project root (or there is none). | docstring | - | 155 |
| `module_arg_segment` | seg, whole_cmd='', root=None | stop_record's read-only credit for ONE segment: it is exactly 'py[thon][N.N][.exe] [flags] -m <module> args' | docstring | - | 167 |

### tools/lint.py

shared module; imported by 1 file(s): `tools/dupcheck.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `norm` | path | Project-relative forward-slash path of 'path' (absolute or relative). Returns str. Self-test: --self-test. | docstring | - | 35 |
| `load_shared` | path=SHARED_JSON | Set of project-relative paths in capabilities_shared.json (empty set if missing). Self-test: --self-test. | docstring | - | 45 |
| `classify` | path, shared | Folder class of a file: 'shared' / 'recipe' / 'bench' / 'other' (see module docstring). Self-test: --self-test. | docstring | - | 54 |
| `run_ruff` | target='tools' | Run ruff over 'target' with the project ruff.toml; returns the list of finding dicts (ruff JSON). | docstring | - | 71 |
| `tabulate` | findings, shared, codes=None | Counter keyed (code, class) plus per-class per-file lists. Returns (counts, files). Self-test: --self-test. | docstring | - | 78 |
| `table_text` | counts | Markdown table rule x class with totals. Returns str. Self-test: --self-test. | docstring | - | 92 |
| `self_test` |  | Offline self-test: classify() on 8 canned paths and tabulate()/table_text()/load_shared() on canned ruff JSON; prints each failure. Returns (ok, fail) counts. | side file | - | 104 |
| `main` |  | CLI: --self-test runs self_test; otherwise runs ruff over tools/, prints the rule x class table, with --files <class> the per-file findings (--codes filters), and a RESULT line. Returns 0, 1 when t... | side file | - | 137 |

### tools/logclass.py

shared module; imported by 17 file(s): `tools/audit_cycle.py`, `tools/bench/diag_c131_2_offline.py`, `tools/bench/diag_c78_rowd_writer.py`, `tools/bench/diag_d0_gate_probe.py`, `tools/bench/jev_discharge_trial.py`, `tools/bench/jev_trial.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `command_kind` | cmd | "review" / "jev" / "build" / "" for a bgrun command string (see the block comment above). | docstring | - | 116 |
| `log_kind` | path | The log's class from its OWN last BGRUN START command: "review" / "jev" / "build" / "" (use the filename). | docstring | - | 141 |
| `is_review_log` | path | Written by the review machinery. Excluded from build accounting AND from failure scanning. | docstring | - | 146 |
| `is_build_log` | path | Records an attempt to build or measure the artefact - the thing a cycle is made of. | docstring | selftest_logclass_recipebuild | 153 |
| `last_bgrun_command` | path | The command string of the log's LAST 'BGRUN START' line, or "" when the file has none. | docstring | - | 178 |
| `is_recipe_build_log` | path | True only when this log's OWN last run INVOKED a 'tools/recipes/*.py' file. | docstring | selftest_guard_peer_jev | 191 |
| `command_program` | cmd | The PROGRAM a bgrun command line invokes - lower-cased basename, "" for an empty command. | docstring | - | 234 |
| `is_judgement_session_log` | path | True when this log records a whole JUDGEMENT SESSION spawned by 'tools/cycle_runner.py'. | docstring | - | 248 |
| `split` | paths | (build_logs, machinery_logs) for cycle accounting - watchdog records group with the machinery. | docstring | - | 268 |

### tools/lv_errorlist.py

shared module; imported by 5 file(s): `tools/bench/diag_c100_verbs_build.py`, `tools/bench/diag_c89_profiler_leg.py`, `tools/bench/diag_errorlist_v0.py`, `tools/errorlist_check.py`, `tools/recipes/stage_d1_m3a4.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `lv_pid` |  | PID of the first LabVIEW.exe in tasklist's CSV output, None when none runs (the visible-window PID set it also collects is not used). Returns int or None. | side file | - | 87 |
| `top_windows` | pid=None | [(hwnd, title, class, (l,t,r,b))] for every visible top-level window (of 'pid' if given). | docstring | - | 106 |
| `child_windows` | hwnd | Win32 CHILD hwnds - the measurement of whether the dialog is owner-drawn (no children). | docstring | - | 127 |
| `UIA` | (class) | UI Automation client: CoInitialize, loads UIAutomationCore.dll through comtypes, creates CUIAutomation as IUIAutomation and keeps its RawViewWalker; its methods read or act on elements through UIA ... | side file | - | 147 |
| `UIA.from_hwnd` | hwnd | UIA element of window handle hwnd (IUIAutomation.ElementFromHandle). Returns the element. | side file | - | 156 |
| `UIA.focused` |  | The element with keyboard focus (GetFocusedElement); None when that raises. Returns element or None. | side file | - | 159 |
| `UIA.value` | el | CurrentValue of el's Value pattern; None when the pattern is absent or the read raises. Returns str or None. | side file | - | 172 |
| `UIA.text` | el | Whole text of el's Text pattern (DocumentRange.GetText(-1)); None when the pattern is absent or the read raises. Returns str or None. | side file | - | 179 |
| `UIA.legacy` | el | el's LegacyIAccessible properties as {name, value, role, state, childid, defaultaction, description} (None for each failed read); None when the pattern is absent. Returns dict or None. | side file | - | 186 |
| `UIA.selected` | el | CurrentIsSelected of el's SelectionItem pattern; None when the pattern is absent or the read raises. Returns bool or None. | side file | - | 199 |
| `UIA.select` | el | Calls Select() on el's SelectionItem pattern. Returns True, or False when el has no such pattern. | side file | - | 206 |
| `UIA.set_focus` | el | Calls el.SetFocus(). Returns True, or False when it raises. | side file | - | 213 |
| `UIA.node` | el | One element as a plain dict - everything we can read about it. | docstring | - | 220 |
| `UIA.tree` | el, depth=0, maxdepth=14, out=None, path='0' | Full RawView tree as a flat list of dicts with a path - scroll cannot hide a row. | docstring | - | 237 |
| `msaa_rows` | hwnd, max_children=400 | [{childid, name, value, role, role_name, state, rect}] for hwnd's client object. [] if none. | docstring | - | 269 |
| `shot` | tag, acts | Full-screen capture. Read-only, needs no gate. Returns (path, md5). | docstring | - | 334 |
| `ensure_foreground` | wtitle, hwnd, acts, tag | The dialog must BE the foreground before any keystroke; SendKeys goes to whatever is. | docstring | - | 387 |
| `send_keys` | key, acts, tag, wait_ms=900 | Sends key through gscript._lv_gui (action keys, WaitMs wait_ms, Exception Approved with the error-list EVIDENCE) and appends {act 'keys', key, tag, out} to acts. Returns lv_gui's output text. | side file | - | 409 |
| `ocr_engine` |  | (callable, name). RapidOCR if installed, else Windows.Media.Ocr, else (None, 'unavailable'). | docstring | - | 430 |
| `ocr_lines` | img, scale=3, invert=False, pad=10 | [(text, conf, y0, y1, x0)] in the ORIGINAL image's coordinates. [] when no engine. | docstring | - | 479 |
| `layout` | img | LOCATE the dialog's parts ON THE CAPTURE (never from remembered offsets). | docstring | - | 511 |
| `read_by_capture` | R, wtitle, acts, log, max_steps=None, hwnd=None, on_item=None | METHOD B. Walk the list one row at a time; each step: capture -> LOCATE the highlighted row by | docstring | - | 585 |
| `read` | vi_path, out_json=None, maxdepth=14, dump_tree=True, log=print, on_item=None, max_steps=None | Open the Error List for 'vi_path' (already in memory), read every item, close it. | docstring | - | 798 |
| `refine_rows` | R, log=print | Re-read each row from the capture in which it is NOT highlighted. OFFLINE - no LabVIEW. | docstring | - | 1088 |
| `main` |  | CLI <vi> [out.json]: opens the VI's panel, reads its Error List with read(vi, out) (default out tools/bench/errorlist_<stem>_<date>.json), prints method, uia_items_exposed, n_reported, item_count; ... | side file | - | 1163 |

### tools/lvclick.py

shared module; imported by 4 file(s): `tools/bench/m3v1_verify.py`, `tools/recipes/build_keystone.py`, `tools/recipes/build_keystone_invoke.py`, `tools/recipes/keystone_discovery.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `geom` |  | (undocumented) | - | - | 33 |
| `save_geom` | d | (undocumented) | - | - | 37 |
| `lv` | *args, timeout=60 | (undocumented) | - | - | 43 |
| `act` | action, **kw | Gated input action (click/rclick/drag/keys) — always logged by lv_gui. | docstring | - | 53 |
| `windows` |  | (undocumented) | - | - | 63 |
| `toplevel` |  | [(enabled, hwnd, (l,t,r,b), title)] for every visible window of the LabVIEW process — | docstring | - | 67 |
| `rect` | title | (undocumented) | - | - | 79 |
| `probe_runs` | x, y, x2=None, y2=None | [(start, end, 'RRGGBB'), ...] along a row (x..x2 at y) or a column (y..y2 at x). | docstring | - | 86 |
| `dominant_rgb` | runs | (undocumented) | - | - | 97 |
| `Viewport` | (class) | (undocumented) | - | - | 106 |
| `Viewport.s` | x, y | diagram -> screen | docstring | - | 110 |
| `node_pos` | target, uid, cls | (undocumented) | - | - | 118 |
| `calibrate` | target, title=None | Viewport from the BD window rect + registered (dx, dy), VERIFIED on two registered | docstring | - | 136 |
| `focus_bd` | vp | Focus + one click on registered empty canvas: clears menu mode and absorbs the swallowed | docstring | - | 165 |
| `move_node` | vp, target, uid, cls, dx, dy, tol=6 | (undocumented) | - | - | 179 |
| `place_from_palette` | vp, target, item, cls, x, y, tol=12 | (undocumented) | - | - | 203 |
| `node_menu` | vp, target, uid, cls, row, item | Right-click a node's item row, click a REGISTERED menu item, run its registered verifier. | docstring | - | 246 |
| `dialog_button` | title, button, open_with=None, bd=None, wait_ms=1500 | Optionally open a dialog with a key combo on the BD, then click a registered button inside | docstring | - | 270 |

### tools/motor_gate.py

shared module; imported by 3 file(s): `tools/bench/selftest_motor_fail_exit.py`, `tools/bench/selftest_motor_gate2.py`, `tools/cycle_runner.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `Decision` | (class) | (undocumented) | - | - | 98 |
| `rig_state` | status_text | 'disassembled' / 'assembled' / 'experiment' / 'unknown'. | docstring | - | 109 |
| `read_status` | path=None | (undocumented) | - | - | 130 |
| `load_limits` | path=None | The user-editable limit file. Returns None if missing/unreadable -> everything is refused. | docstring | - | 138 |
| `session_info` | path=None | (undocumented) | - | - | 156 |
| `decide_asi` | cmd, args, raw | (undocumented) | - | - | 193 |
| `decide_pi` | cmd, args, raw | (undocumented) | - | - | 222 |
| `decide_rotor` | cmd, args, raw | (undocumented) | - | - | 241 |
| `decide` | device, command, state=None | The whole command-class decision, with no I/O to a port. 'state' is injected so the self-test can run every | docstring | - | 253 |
| `parse_pi_limits` | text | 'LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0' -> dict, or None.  This is the POST-WRITE readback. | docstring | selftest_motor_gate2.py | 282 |
| `parse_pi_ref` | text | 'REFSTATE RON=0 FRF=1 POS=0.00000 POS_BEFORE=0.00000 ERR=0' -> dict, or None. | docstring | - | 306 |
| `parse_asi_limits` | text | 'LIMITS SL X=-3.847494 Y=-4.774393 SU X=0.152497 Y=-0.774402' -> dict, or None. | docstring | - | 322 |
| `check_pi_readback` | rb, lo, hi, tol=DEFAULT_TOL | (ok, message). rb = parse_pi_limits() output. Every readback field present must match. | docstring | - | 332 |
| `check_asi_readback` | rb, sl, su, tol=DEFAULT_TOL | (undocumented) | - | - | 345 |
| `session_start` | limits, pi_call=None, asi_call=None, session_path=None, out=print | Write the file's limits into BOTH controllers and verify by readback. rc 0 = both verified, else 3. | docstring | - | 374 |
| `session_end` | limits, pi_call=None, asi_call=None, session_path=None, out=print | Release the controller limits (PI lo..release_hi, ASI +-release) and delete the session file. | docstring | - | 429 |
| `log` | device, command, d, dry | (undocumented) | - | - | 458 |
| `transmit` | device, command, d, limits | Send ONE decided motion command. The SENDER re-reads the controller limits inside the same port open, | docstring | - | 476 |
| `main` | argv=None | (undocumented) | - | - | 535 |
| `fail_line` | rc | One 'FAIL:' line for a non-zero exit (cycle 69, device-failed repair). pi_testmove_20260923e.log:23/34 held a | docstring | - | 616 |
| `result_line` | rc | C6 (docs/session-protocol.md, user-approved 2026-09-24): the gate's verdict as its LAST line. bgrun's body scan | docstring | - | 625 |

### tools/outcome_review.py

shared module; imported by 3 file(s): `tools/bench/selftest_item34.py`, `tools/cycle_runner.py`, `tools/debate_loop.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `reviews_since_last` |  | (n_retrospectives_since, days_since, last_path_or_None) - the cadence, read from the files. | docstring | - | 95 |
| `is_due` |  | (undocumented) | - | - | 106 |
| `evidence` |  | (undocumented) | - | - | 117 |
| `last_two_reviews` |  | (latest, previous) archived outcome reviews by mtime, either None. | docstring | - | 152 |
| `steer_after_review` | write=True, cards_dir=None | STEERING CARD (user 2026-09-24, "아웃컴 리뷰에 조향카드 부여하는 것 동의"): when the newest review repeats a verdict | docstring | - | 158 |
| `main` |  | (undocumented) | - | - | 177 |

### tools/prior_art_review.py

shared module; imported by 2 file(s): `tools/bench/selftest_chat_p2.py`, `tools/bench/stop_record_selftest.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `inventory` | use_index=False | NO INDEX. This is the measured configuration, not an omission. | docstring | - | 82 |
| `record_opt_out` | review_path, reason | Write a '--no-recipe' reason into the archived review file. Returns True if it landed. | docstring | - | 168 |
| `jev_advisory` | slug, plan | One 'JEV-PRIORART-DUP' line when an archived prior-art review already answers this step. Never raises, | docstring | - | 204 |
| `user_rules_block` | path=None | (undocumented) | - | - | 239 |
| `build_task` | plan, trigger='new-op', use_index=False, status_path=None, rules_path=None | The full task text a prior-art dispatch sends (split out of main() by card chat-P2 so a self-test can check it | docstring | - | 250 |
| `main` |  | (undocumented) | - | - | 265 |
| `arm_stop_records` | slug, recipes, opt_out='' | Plant a stop record for each '--recipe' if this review's verdicts are not all 'novel'. | docstring | - | 359 |

### tools/priorart_diff.py

shared module; imported by 8 file(s): `tools/bench/diag_c147_c3_3_proven.py`, `tools/bench/diag_c148_a2_2_gate.py`, `tools/bench/diag_c158_a3_2_pascope.py`, `tools/bench/diag_c163_a2_1_pa.py`, `tools/bench/prep_c164_a2_3_pa.py`, `tools/bench/selftest_c_e3.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `pattern_key` | path | (undocumented) | - | - | 38 |
| `norm_line` | s | (undocumented) | - | - | 42 |
| `approved` | path, records=None | True when a stop record for 'path' is released or novel for the bytes on disk now. | docstring | - | 59 |
| `sibling` | recipe, records=None | (undocumented) | - | - | 74 |
| `diff_lines` | old, new | (parameter_only_count, [(new line no, old text, new text)] substantive). | docstring | - | 90 |
| `scope` | recipe, records=None, new_classes=None | (undocumented) | - | - | 114 |
| `task_text` | sc | The narrowed review subject for prior_art_review.py --diff-from. | docstring | - | 130 |
| `main` | argv=None | (undocumented) | - | - | 142 |

### tools/protocol.py

shared module; imported by 665 file(s): `tools/audit_cycle.py`, `tools/bench/build_op_const_loopterm_77.py`, `tools/bench/build_op_termtype.py`, `tools/bench/build_opstopmode_v0.py`, `tools/bench/build_opwiringrules_v0.py`, `tools/bench/c109_errorlist_reverdict.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `schema_path` | schema_name | 'task/1' -> docs/protocol/task.json ; a later 'task/2' -> docs/protocol/task.v2.json. | docstring | - | 80 |
| `load_schema` | schema_name | The JSON schema of a '<name>/<version>' schema name (schema_path), read once and cached; raises ValueError when the file is missing. Returns dict. | side file | - | 92 |
| `goal_ids` | path=GOALMAP | The ids a card may cite (requirements + milestones), or None when the goal map is absent/unreadable. | docstring | - | 173 |
| `machine_view` | doc, schema_name=None | A deep copy of 'doc' without the fields its schema marks "x-prose": true. schema_name: 'stageplan' or | docstring | - | 211 |
| `prose_fields` | schema_name | Dotted paths of every x-prose field of a schema (definitions included) - for the self-test and the docs. | docstring | - | 225 |
| `validate_obj` | obj, goal_ids=None | (True, 'OK <schema>') or (False, '<one-line reason>'). 'goal_ids': when given, every advances/unblocks/blocks | docstring | - | 247 |
| `load_card` | path, goal_ids=None | Reads a JSON card file and validates it (validate_obj, goal-map ids when goal_ids is given); raises ValueError when not JSON or invalid. Returns the card dict. | side file | - | 272 |
| `result_line` | d | The one-line text form. Validated; ASCII-escaped so a cp949 console can always print it. | docstring | - | 285 |
| `make_result` | n_pass, n_fail, first_fail=None, artefacts=(), status=None | A result-line/1 dict: status (given, else PASS when n_fail == 0 and no first_fail, else FAIL), gates {pass, fail}, first_fail cut to 200 chars, artefacts. Returns dict (result_line validates it). | side file | - | 302 |
| `all_result_lines` | text | Every 'RESULT {...}' line of text, parsed; a line that is not JSON or not a valid result-line/1 becomes a FAIL record naming it malformed. Returns list of dicts. | side file | - | 314 |
| `parse_result_line` | text | The LAST 'RESULT {...}' line of 'text' as a dict, or None when there is none. A malformed one is a FAIL. | docstring | - | 329 |
| `result_failed` | d | A RESULT line fails unless its status is PASS or SKIP AND gates.fail == 0. SKIP (card 108-5, review | docstring | - | 335 |
| `stop_kind_of` | exc_or_text | 'memstop' / 'execstop' / 'exception' for an exception object (by class name) or its text. | docstring | - | 358 |
| `stop_line` | kind, message, **extra | The one-line STOP text: 'STOP {json}' (ASCII-escaped, like result_line). kind in STOP_KINDS. | docstring | - | 369 |
| `all_stop_lines` | text | Every 'STOP {json}' line of 'text' as a dict (file order). A STOP line that is not valid stop-line/1 JSON still | docstring | - | 382 |
| `segments` | text | [(start_epoch_or_None, command_line, segment_text)] - one per 'BGRUN START', in file order. | docstring | - | 398 |
| `last_segment` | text | The last bgrun run of a log text (segments(): one per BGRUN START). Returns (start epoch or None, start line, segment text); (None, '', text) when there is no BGRUN START. | side file | - | 412 |
| `run_verdict` | segment | C6 verdict of ONE run. failed = any RESULT line fails, or the process ended rc!=0, or TIMEOUT. | docstring | - | 417 |
| `is_legacy` | start_ts, mtime=None | True when the run's start time (else mtime) is before SWITCH_TS (2026-09-24 18:25, bgrun stopped scanning bodies); False when both are None. Returns bool. | side file | - | 438 |
| `log_verdict` | text, legacy_re=None, mtime=None | Verdict of the LAST run in a (possibly appended) log. Pre-switch runs without a RESULT line keep the caller's | docstring | - | 443 |
| `first_fail_signature` | segment, legacy_re=None, start_ts=None | For cycle_runner's SAME-MISTAKE trigger: the raw first-failure text of ONE run segment, or None. | docstring | - | 463 |
| `stagekit_result_from_gates` | segment | REPLAY ONLY: what stagekit's RESULT line would have been, from its '=== GATES: n pass / m fail' line. | docstring | - | 479 |
| `offline_selftest` | path, cmd | True when 'path' (a launched script) is an OFFLINE_SELFTESTS entry and every command-position occurrence of it in | docstring | - | 535 |
| `lv_script` | path, cmd, src=None | The check_command / soft-alert notion of a LabVIEW-touching launched script: a recipe, or a script whose code | docstring | - | 557 |
| `path_in_globs` | path, globs | True when path matches a write glob: absolute globs against the absolute path, relative globs against the path relative to the project root (a path outside the root never matches a relative glob). ... | side file | - | 608 |
| `file_lock` | (class) | card chat-P1 item 1(a)/(b): a cross-process lock FILE around a read-modify-write (os.open O_CREAT/O_EXCL, retry | docstring | - | 621 |
| `write_release` | review, kind, slug, cite_path, cite_line, what, now=None | card chat-S5 (PD337(d)): write ONE release/1 record + its legacy line into a review file, VALIDATED FIRST. | docstring | - | 699 |
| `read_releases` | body | [release/1 dict] from the 'RELEASE {...}' lines of a review body (old reviews: [] - their FIXED:/REFUTED: lines | docstring | - | 743 |
| `input_md5_changes` | card | card chat-S5 (PD337(e)): ['<path>: card <md5> != disk <md5>' / '<path>: missing'] for every task/1 input that names | docstring | - | 757 |
| `bind` | agent_id, agent_type, card_path, goals='default' | Record the binding. Returns (ok, message). The card must be a VALID task/1. | docstring | - | 781 |
| `binding` | agent_id | The active.json record for agent_id (what bind() stored for that agent), None when unbound or the file is unreadable. Returns dict or None. | side file | - | 814 |
| `code_only` | src | The source with COMMENTS and DOCSTRINGS (any bare string statement) blanked, so the flag detectors see calls, | docstring | - | 829 |
| `peer_role_of` | cmd | The review role a command dispatches, or None. peer.ps1: -Role wins, else -Kind (fact/prose), else a | docstring | - | 887 |
| `src_features` | src | {'save','gui','run'} for ONE script's source, from its CALLS (judgement 2026-09-24, card chat-B4): a string | docstring | - | 922 |
| `requires_path` | card_id, cards_dir=None | Path of a card's requires record: <cards_dir or CARDS_DIR>/requires_<card_id>.json. Returns str. | side file | - | 977 |
| `check_requires` | card | {ok, missing, found} for the card's 'requires' (OFFLINE: file system + JSON, never LabVIEW). | docstring | - | 1046 |
| `requires_refusal` | card, cmd, scripts | None, or why a bgrun / LabVIEW launch is refused under a card that declares 'requires' (argv + card). | docstring | - | 1055 |
| `soft_alert_refusal` | card, cmd, scripts, srcs=None, now=None | None, or the refusal for a NEW bgrun launch of a recipe/diagnostic under a card bound > SOFT_ALERT_MIN ago. | docstring | - | 1121 |
| `check_command` | card, cmd | None = allowed, else the refusal reason. The card's flags applied to ONE Bash/PowerShell command. | docstring | - | 1139 |
| `check_write` | card, file_path | None = allowed, else the refusal reason, for Edit / Write / NotebookEdit on 'file_path'. | docstring | - | 1207 |
| `hook_decision` | payload | The PreToolUse decision for ONE tool call. Returns (allow: bool, message: str/None). | docstring | - | 1229 |
| `record_launch` | card_id, cmd | Append one ledger row per '--log' of a bgrun command run under 'card_id'. Returns the rows written. | docstring | - | 1281 |
| `card_owns_log` | card_id, log_path | True when the ledger says 'card_id' launched 'log_path' (by basename) - or when the ledger cannot be read | docstring | - | 1294 |
| `log_owner` | log_path, text=None, max_age_s=None | card chat-E3 (fp-36): the card that launched 'log_path''s LAST run - the 'card' field of its last RESULT line | docstring | - | 1315 |
| `launch_card_env` | log_path | {CARD_ID, CARD_LABVIEW} for a bgrun child, from the ledger row the PreToolUse hook wrote for this --log (the | docstring | - | 1354 |
| `review_card` | role, rid, claim, predicted='', observed='', ruled_out=(), attachments=(), note='' | Build + validate a review/1 card; returns the dict. 'attachments' = paths (md5 filled in when the file exists). | docstring | - | 1383 |
| `write_review_card` | d | Writes review card d to CARDS_DIR/review_<id>.json (UTF-8, indent 1), creating the folder. Returns the path. | side file | - | 1401 |
| `render_review` | card | The review/1 card as the text block peer.ps1 puts in front of the task, plus the verdict/1 contract. | docstring | - | 1409 |
| `verdict_contract` | card | The VERDICT CONTRACT text appended to a review prompt: the answer's last line must be one single-line 'VERDICT {verdict/1}' with this card's id and the role's allowed verdicts (ROLE_VERDICTS). Retu... | side file | - | 1425 |
| `parse_verdict` | text, want_id=None | (dict, None) for the LAST valid 'VERDICT {...}' line of the answer, else (None, reason). | docstring | - | 1436 |
| `next_state` | path=NEXT_JSON | (md5_of_bytes / 'absent', card / None, reason / None) - the runner's and next_gate's single reading. | docstring | - | 1459 |
| `open_decisions` | path=DECISIONS | Items of decisions_pending.json (path) whose status is 'open'; [] when the file is missing or invalid. Returns list. | side file | - | 1470 |
| `outcome_slugs` | md_text | The OUTCOME-VIOLATION slugs of an archived outcome review's ANSWER (after '## Answer', before '## What was | docstring | - | 1498 |
| `current_cycle` | cards_dir=CARDS_DIR | The highest n of 'cycle_<n>.json' in the cards dir (0 when none). | docstring | - | 1509 |
| `goalmap_ids` | goalmap_path=GOALMAP | (active milestone ids, open/moving requirement ids, not-done milestone ids, all known ids / None) of | docstring | tools/debate_loop.py selftest | 1522 |
| `steer_for` | latest, previous, cycle, goalmap_path=GOALMAP | (steer/1 card / None, why). A card only when a slug appears in BOTH reviews (a REPEATED verdict). | docstring | - | 1539 |
| `steer_from_debate` | summary, cycle, kind, slug, evidence, goalmap_path=GOALMAP | (steer/1 card / None, why) from a Claude-GPT discussion's summary (card chat-D2, user 2026-10-09 "둘 다 넣자"): | docstring | tools/debate_loop.py selftest | 1563 |
| `write_steer` | card, cards_dir=CARDS_DIR | Writes a steer card to <cards_dir>/steer_<cycle>.json (UTF-8, indent 1), creating the folder. Returns the path. | side file | - | 1592 |
| `active_steer` | cards_dir=CARDS_DIR, state_path=STEER_STATE | (path, card) of the newest VALID steer card that is not closed (followed / stopped) in the state file, or | docstring | - | 1616 |
| `steer_after_cycle` | steer_path, steer_card, next_card, n, state_path=STEER_STATE | Read the judgement's answer (next/1 'steer') to the steer carried in cycle n. Returns (action, detail): | docstring | - | 1640 |
| `add_decision` | question, options, by, blocks=(), recommendation=None, path=DECISIONS, skip_if_open=False | Append ONE open decisions-pending/1 item (id D-<today>-NN), validate the whole file, then write it. Returns | docstring | - | 1670 |
| `add_steer_decision` | steer_card, n, refusals, path=DECISIONS | Append ONE open decisions-pending/1 item for a steer refused twice; validate the whole file before writing. | docstring | - | 1695 |
| `main` | argv=None | CLI: bind, parse-verdict, render-review, validate, new, result-line, verdict, requires (their _cmd_* handlers) and release (write_release); no command prints help. Returns the exit code (2 = no com... | side file | - | 1843 |

### tools/retro_due.py

shared module; imported by 2 file(s): `tools/bench/selftest_chat_p1.py`, `tools/cycle_runner.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `newest_answered_retro` | peer_dir=None | (path, stamp) / None - guard_cycle.newest_retrospective with its PEER pointed at peer_dir. | docstring | - | 47 |
| `cycle_cards` | cards_dir | (undocumented) | - | - | 59 |
| `delivered` | cycle, cards_dir | [result ids] of PASS result/1 cards written since cycle_<cycle>.json with a claudeDev .vi artefact. | docstring | - | 72 |
| `near_threshold` |  | [(slug, fresh occurrences, threshold)] - slugs one occurrence below their threshold (threshold >= 2), counting | docstring | - | 100 |
| `check` | cycle, cards_dir=None, peer_dir=None, violations=True | (due: bool, reasons: [str], facts: dict). | docstring | - | 120 |
| `main` | argv=None | (undocumented) | - | - | 153 |

### tools/retrospective.py

shared module; imported by 2 file(s): `tools/bench/selftest_stamp_window.py`, `tools/doc_ingest.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `current_plan_rel` |  | Project-relative path of the ONE cycle plan whose frontmatter says 'status: current', or None. | docstring | - | 67 |
| `parse_devices` | path | Every 'DECISION: device' block in docs/violation-decisions.md -> (slug, stamp, one-line device). | docstring | - | 169 |
| `retro_archive` | n | The archive of cycle <n>'s OWN retrospective, or None. | docstring | - | 217 |
| `newest_retro_before` | now, exclude_slug=None | (path, mtime) of the newest retrospective archived strictly BEFORE 'now', or None. | docstring | - | 229 |
| `dispatch_time` | path | When a retrospective was DISPATCHED = its archive's mtime minus the elapsed seconds peer.ps1 recorded. | docstring | - | 259 |
| `cycle_window` | cycle, slug=None | (start, end, basis) - the cycle's real boundary. | docstring | - | 280 |
| `fmt` | t | (undocumented) | - | - | 339 |
| `main` |  | (undocumented) | - | - | 343 |

### tools/rules_coverage.py

shared module; imported by 2 file(s): `tools/doc_ingest.py`, `tools/retrospective.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `frozen_body` | text | The text above the FROZEN footer (the footer is not rule text). | docstring | - | 44 |
| `items` | text | [(line, kind, text)] - every heading and every bold span of 'text' (a bold span may wrap lines, never a | docstring | - | 50 |
| `topic_files` |  | (undocumented) | - | - | 94 |
| `rule_docs` |  | The rule topic files as project-relative paths ('docs/rules/<topic>.md'), sorted - what a tool attaches or | docstring | - | 99 |
| `ranges` | paths | [(a, b, relpath, line)] - every cited frozen range in the topic files. | docstring | - | 105 |
| `mapping` | its, rngs | [(item, home or None)] - home = 'path:line' of the narrowest cited range containing the item's line. | docstring | - | 119 |
| `cell` | s, n=110 | (undocumented) | - | - | 131 |
| `coverage_md` | mapped, frozen_md5 | (undocumented) | - | - | 136 |
| `check` | write=False | (undocumented) | - | - | 149 |
| `selftest` |  | (undocumented) | - | - | 171 |
| `main` |  | (undocumented) | - | - | 194 |

### tools/run_mode.py

shared module; imported by 1 file(s): `tools/hooks/guard_session.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `config` |  | tools/bench/run_mode_config.json merged over DEFAULT_CONFIG (threshold_pct 50, stale_min 90, disabled False); the defaults alone when unreadable. Returns dict. | side file | - | 27 |
| `effective` | now=None | (mode, reason): 'performance' when the config is disabled; 'economy' when the mode file is unreadable or older than stale_min; else by weekly_pct <= threshold_pct. Returns tuple. | side file | - | 35 |
| `write` | weekly_pct | Writes run_mode.json (mode from weekly_pct vs threshold_pct, atomic replace) and appends a RUN-MODE line to run_mode.log, noting a change. Returns (mode, previous mode or None). | side file | - | 51 |

### tools/scope_header.py

shared module; imported by 14 file(s): `tools/bench/diag_c146_a1_1_repro.py`, `tools/bench/diag_c148_a1_1_before.py`, `tools/bench/diag_c148_a1_1_runall.py`, `tools/bench/prep_c150_a2_4_stage_prerun_before.py`, `tools/bench/scope_honesty_census.py`, `tools/bench/selftest_c_e3.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `parse_bytes` | b | (header dict / None, error / None). Error = the block exists but is invalid; (None, None) = no block. | docstring | - | 101 |
| `read` | path | Parses a file's scope header block (parse_bytes). Returns (header dict / None, error / None); error 'unreadable: ...' on OSError. | side file | - | 129 |
| `canonical_bytes` | b | The bytes without the header block - exactly the file before the migration added it (see module doc). | docstring | - | 137 |
| `canonical_sha256` | path | SHA-256 hex of a file; a .py/.ps1 is hashed without its scope header block (canonical_bytes). Returns str. | side file | - | 158 |
| `canonical_md5` | path | MD5 hex of a file; a .py/.ps1 is hashed without its scope header block (canonical_bytes). Returns str. | side file | - | 162 |
| `render` | labview, hardware, offline_args=(), evidence=None, nl='\n' | The header block text: '# ---', '# labview: x', '# hardware: y', optional '# offline-args: ...' and '# evidence: ...', '# ---', joined by nl with a final nl. Returns str. | side file | - | 166 |
| `append_block` | b, block_text | The file bytes with the block appended so that canonical_bytes() gives 'b' back exactly. | docstring | - | 176 |
| `honesty` | path, h, src=None | Problems with a DECLARED header against the code (an empty list = honest). Only 'labview: none' (and | docstring | - | 264 |
| `compile_error` | path, src=None | None, or the syntax/parse error text. .py: compile() in memory; .ps1: the PowerShell parser (one process). | docstring | - | 342 |
| `infer` | path, src=None | The migration's scope for an existing script. labview: none when nothing in its import closure reaches LabVIEW | docstring | - | 368 |
| `in_tools` | p | True when path (quotes stripped, relative paths taken from the project root) lies under tools/. Returns bool. | side file | - | 426 |
| `launches` | cmd | [(script abs path, argv tokens after it)] for every script RUN by 'cmd': a .py in command position of a | docstring | - | 449 |
| `effective` | h, argv | (labview, hardware) for ONE run: offline-args present in its argv -> ('none', 'none'). | docstring | - | 494 |
| `launch_scope` | cmd, extra=() | [(path, labview, hardware, problem/None)] for every tools/ script 'cmd' runs. problem: missing/invalid header, | docstring | - | 501 |
| `check_launch` | flags, cmd, extra=() | None, or the refusal: a run whose declared scope exceeds the card's flags, a header missing/invalid, a compile | docstring | - | 543 |
| `offline_run` | cmd | True when 'cmd' runs at least one tools/ script and EVERY tools/ script it runs is effectively labview none | docstring | - | 562 |
| `all_scripts` |  | Every .py / .ps1 file under tools/ (skipping __pycache__ and .git), sorted absolute paths. Returns list. | side file | - | 579 |
| `tracked_scripts` |  | git-tracked tools scripts only: an untracked file belongs to a card still writing it (chat-A1 runs beside | docstring | - | 611 |
| `migrate` | apply=False, paths=None | For each script (default: git-tracked tools scripts) with no header: appends the KNOWN or inferred block with canonical bytes unchanged (asserted), written (mtime kept) only when apply; NO_TOUCH sk... | side file | - | 620 |
| `rescope` | apply=False | fp-40: re-infer every MIGRATION-written header (a tail block with no offline-args/evidence, not KNOWN, not | docstring | - | 647 |
| `main` | argv=None | CLI: check <file> (header, error, honesty, compile as JSON), infer <file>, launch <cmd>, rescope [--apply], migrate [--apply] [--summary] (counts + INVALID / motor / camera rows); -h prints usage. ... | side file | - | 680 |

### tools/stage_prerun.py

shared module; imported by 230 file(s): `tools/bench/c88_reverdict.py`, `tools/bench/diag_c101b_syntax.py`, `tools/bench/diag_c103d_jevfix.py`, `tools/bench/diag_c103d_launch.py`, `tools/bench/diag_c104_launch.py`, `tools/bench/diag_c104d_launch.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `sha256` | path | SHA-256 hex digest of a file; a .py/.ps1 is hashed WITHOUT its scope header block (scope_header.canonical_bytes) so records written before the header migration still match. Returns the hex string. | side file | - | 138 |
| `md5` | path | MD5 hex digest of the whole file at path, read in binary (no scope-header stripping, unlike sha256). Returns str. | side file | - | 151 |
| `rel` | p | Path p made absolute, then relative to the project ROOT with forward slashes; on another drive (ValueError) the absolute path with forward slashes. Returns str. | side file | - | 158 |
| `GraphShapeError` | (class) | A graph JSON that is not the terminal-list shape OfflineGraph reads. | docstring | - | 177 |
| `graph_shape_error` | d | None when 'd' is the terminal-list graph ({md5, terminals:[...], objs:[...]} with the row fields the readers | docstring | - | 181 |
| `plan_base_graphs` | recipe | card 106-5 (PD219(c)): [(path, md5 pin or None)] of the base graph every plan the recipe names records | docstring | - | 204 |
| `find_graph` | input_md5, plan_graphs=() | The terminal-list graph (graph_shape_error None; card 95-1) whose top-level 'md5' is 'input_md5': | docstring | - | 226 |
| `OfflineGraph` | (class) | The readers stagekit addresses with, answered from one graph JSON ({vi, md5, terminals, objs}). Any other | docstring | - | 277 |
| `OfflineGraph.G` |  | Lazily builds, once, the jev_candidates graph of this file's terminals and objs (jev_candidates.from_parts, named by the file's basename) and caches it in _G. Returns that graph. | side file | - | 303 |
| `OfflineGraph.report_all` | _t, cls | gscript.report_all stand-in: for 'Diagram' one {i, uid, class, pos [0,0], owner ''} per diagram (TopLevelDiagram first); for 'GObject' every obj, else the objs of that class, each copied with its i... | side file | - | 310 |
| `OfflineGraph.uids` | _t, cls | Set of the int uids of the rows report_all(_t, cls) returns. Returns set. | side file | - | 317 |
| `OfflineGraph.count` | _t, cls | Number of rows report_all(_t, cls) returns. Returns int. | side file | - | 320 |
| `OfflineGraph.nodes_in` | di | Nodes whose terminals sit on diagram 'di', plus EVERY structure (a structure's own diagram is not in the | docstring | - | 323 |
| `OfflineGraph.node_labels` | _t, di, *a, **k | gscript.node_labels stand-in: one {uid, label ''} per node nodes_in(di) lists for diagram index di (labels are not in the graph JSON). Returns list of dicts. | side file | - | 331 |
| `OfflineGraph.term_rows` | uid | (rows, how). A structure's terminal list = the OUTER terminals of its border tunnels (jev_candidates | docstring | - | 334 |
| `OfflineGraph.node_terms_uid` | _t, di, ni | gscript.node_terms_uid stand-in: the ni-th node of nodes_in(di) and its term_rows as {i, name, is_source, wire, has_wire, node_uid, uid}; (0, []) when ni is out of range. Returns (uid, rows). | side file | - | 345 |
| `OfflineGraph.read_terms` | *_a, **_k | allterms.read_terms stand-in: copies of every terminal row of the graph JSON and a read time of 0.0. Returns (list of dicts, 0.0). | side file | - | 354 |
| `OfflineGraph.read_live` | _path, fs_pairs=None, fs_uids=None | wiki_build.read_live stand-in: {terminals, objs (copies), wires (allterms.join_wires over the Wire objs, [] if that raises), fs_tunnel_pairs (fs_pairs or []), secs all 0.0}; fs_uids is ignored. Ret... | side file | - | 357 |
| `DryState` | (class) | The dry run's mutable record (module instance D, reset by D.__init__() in main): taint counters, first mutating call, calls, graph with path and error, input md5/VI, Stage ops, addresses, Jev inten... | side file | - | 369 |
| `Fake` | (class) | The permissive stand-in for anything the stub cannot know. Every use is counted (taint). | docstring | - | 400 |
| `provisional_dry_graph` | recipe | card 132-1 (gate-fp fp-21, PD275(e)): (path / None, error / None). A recipe whose plan base is PROVISIONAL (base = | docstring | - | 514 |
| `waiting_reason` | recipe, tr | card chat-E3 (brief item 4): the WAITING text when a dry on a PROVISIONAL base (provisional_dry_graph) failed ONLY | docstring | - | 548 |
| `waiting_prerun` | pr | True when every FAILING prerun gate is one that follows from a WAITING dry (X1 dry, X5 executed-ops cascade, X10 | docstring | - | 577 |
| `dry_read_only` | recipe | True when the recipe file exists and its VI-modifying stagekit calls (vi_modifying_calls) are non-empty and all in DRY_READONLY_VERBS (discard_work only); False on any exception. Returns bool. | side file | - | 592 |
| `fake_gscript` |  | A module named 'gscript': gscript.py's TOP-LEVEL constant assignments evaluated one by one (os / str only), | docstring | - | 630 |
| `fake_com` |  | Stub modules for pythoncom, win32com, win32com.client, win32com.client.dynamic, win32api, win32gui and win32con: every non-dunder attribute is a _stub; the submodules are linked as attributes. Retu... | side file | - | 660 |
| `wrap_module` | mod | Every function DEFINED in 'mod' -> a stub (a LabVIEW-touching fleet module loaded through K.mod). | docstring | - | 678 |
| `install` | graph_override=None | Dry-run setup: fake COM and gscript into sys.modules, tools, recipes and bench on sys.path, subprocess and os.system refused, writes/copies/moves/deletes outside %TEMP% sent to SINK or dropped (log... | side file | - | 696 |
| `patch_stagekit` |  | Imports stagekit under the fakes and rebinds it for a dry: offline-graph read_terms/read_live, Jev decide/check stubs, logged candidates, K.mod wrapping non-PURE_MODS, dry Stage init/gate/_op/addre... | side file | - | 751 |
| `dry_unverified_labels` | lines | card 159-a4-1 (PD387(e)): the gate labels a dry's output lines leave unverified - every 'UNVERIFIED-DRY' / 'UNVERIFIED' / | docstring | selftest_c159_a4_1.py | 955 |
| `merge_unverified` | have, labels | card 159-a4-1: 'have' (D.unverified) + every label of 'labels' not already there (same label, or one is a prefix of the | docstring | - | 971 |
| `dry` | recipe, graph=None | Run in THIS process (the caller is a fresh process: '--dry' / '--prerun'). Returns the trace dict. | docstring | - | 1014 |
| `plan_files` | recipe | (plan paths, every .json the recipe names). A plan = a named .json with a 'decisions' list of id+action rows, | docstring | - | 1100 |
| `stageplan_check` | path | (ok, detail, plan/None, compiled ops/None) for a stageplan/1 a recipe names (card 79-6). ok only when | docstring | - | 1142 |
| `control_path_lint` | plan, base=None | List of refusals (empty = the plan passes). 'base' = (cls, terms) for tests; else read from plan['base']. | docstring | - | 1229 |
| `pb_licences` | plan_path, bench=None | {node uid: licence file} from every pb-licence/1 file under tools/bench whose 'plan' names plan_path. | docstring | - | 1340 |
| `buildarray_open_sibling` | plan, base=None, licences=None | -> [{row, node, wired, open, licensed}] : every 'wire' action whose dst is an INPUT of a Build Array node while | docstring | - | 1361 |
| `recreated_wire_refs` | plan, base=None | -> (recreated, flags). recreated = [{wire, row, idx}]: every 'wire' action whose dst is a face of a tunnel an | docstring | - | 1421 |
| `replay_sample` | model_path, sample, models | -> (outcome, mismatches, detail): outcome 'PASS' / 'FAIL' / 'ERROR'; mismatches [(field, measured, simulated)]. | docstring | - | 1566 |
| `stagesim_tun1` |  | stagesim.TUN_FLIP as a tuple (the single-object tunnel classes LoopTunnel, Tunnel, SelectorTunnel). Returns tuple. | side file | - | 1686 |
| `replay_delete_sample` | model_path, sample, models, disable=() | -> (outcome, mismatches, detail) for one delete_object / delete_wire / remove_bad_wires sample (card 115-2 R0). | docstring | - | 1695 |
| `opmodel_conformance` | ops=None, model_dir=None, disable=(), log=None | X13 core. ops = the stageplan ops to check (None = every model file in model_dir). disable: ('cfw_border_rule',) | docstring | - | 1725 |
| `plan_ops` | plan | Sorted distinct op names (as str) of the dict entries of plan['actions'] that carry an op. Returns list. | side file | - | 1775 |
| `x13_gate` | plans | (ok, detail, warns) over stageplan/1 dicts: the union of their ops, one conformance run. | docstring | - | 1779 |
| `addr_offline` | OG, end, is_source | None if addressable offline, else the reason. Unwired terminals: owner node -> terminal list -> uid echo. | docstring | - | 1856 |
| `lint` | recipe, OG | Scans the recipe's AST for int literals >= 100 that are uids in OG.cls, and non-docstring string literals equal to a terminal name (>= 2 chars) of one of those uids. Returns (sorted [(uid, line)], ... | side file | - | 1885 |
| `recipe_dispatches_rows` | recipe | card 110-7 (F1, decided by judgement): True when the recipe's AST CALLS stagekit.run_rows / from_decision (as an | docstring | - | 1906 |
| `verb_preconditions` | plans, sps, work, move_dst, stop_after=None, from_step=None, rows_dispatched=True | X9 (retrospective-cycle102 'wrong-ordering'): every op / row the run DISPATCHES whose verb holds a precondition on | docstring | - | 1924 |
| `meter_records` | recipe, log_dir=None | X10's evidence: every run log of THIS recipe that carries a recorded per-op meter (stagexec.Meter's METER lines), | docstring | - | 1958 |
| `mem_margin` | recipe, stop_after=None, from_step=None, log_dir=None, records=None, margin_mb=None | X10 (retrospective-cycle103 'inference-over-measurement'; PD216(f): 103-2 r1 crossed MEMSTOP 700 at 703.8 MB): the | docstring | - | 1994 |
| `X10Probe` | (class) | card 130-1: raised by the Executor capture in probe mode (D.x10_probe) - not an Exception, so stagekit.run's | docstring | - | 2030 |
| `load_memory_model` | path=None | Loads memory_model.json (path or MEMORY_MODEL) and requires start_mb, read_mb, edit_mb, other_mb, final_read_mb and fail_above_mb each as {value: number, cite: non-empty}, else ValueError. Returns ... | side file | - | 2035 |
| `x10_capture_executors` |  | card 130-1: wrap stagexec.Executor.__init__ for the dry run - record plan path, compiled op kinds, checkpoints, | docstring | - | 2043 |
| `executor_stops` | executors | card 130-5 (PD268(b)): one FAIL text per Executor whose run() ended before its window's last op, or that was built | docstring | - | 2106 |
| `x10_start` | vi_md5, model=None | card 133-3 (PD283(b)(e)): (start_mb, cite) of a run whose INPUT VI has a measured load: load_by_vi[md5] + op0_read_mb | docstring | - | 2122 |
| `x10_plan_start` | plan_path, model=None | card 133-3: the measured start of the Executor run of 'plan_path': its (finalized) base graph's 'md5' = the input | docstring | - | 2134 |
| `x10_base_provisional` | plan_path | card 141-1: True when the plan's top-level base is provisional (a simulated graph, no measured VI load). | docstring | - | 2148 |
| `x10_model_peak` | kinds, checkpoints, stop_after=None, from_step=None, model=None, start_mb=None, partial=None | card 130-1 (PD267(b)): the predicted private-MB peak of ONE Executor run. N = ops dispatched (from_step+1 .. | docstring | - | 2157 |
| `x10_readonly` | recipe, trace | card 132-4 (PD277(a)): (ok, detail). ok True iff the dry trace shows no Executor, no Stage._op, no mutating stub | docstring | - | 2197 |
| `x10_source_reads` | recipe, names=X10_SRC_READS | card 138-2 (PD299(b)): the recipe's whole-VI reads counted from its SOURCE. Returns {"reads": n / None (None = some | docstring | - | 2267 |
| `x10_reads_line` | src, dry_n=None | card 138-2: one printable line - source count (+ sites), dry count, unbounded sites. | docstring | - | 2402 |
| `x10_edit` | recipe, trace, model | card 136-2 (fp-33): (run dict / None, why / None). why None = not an edit trace (no ops: the caller's text stands). | docstring | - | 2411 |
| `fntest_release` | path | card chat-F3 (fp-42): (declared, ok, why list). declared False = no FNTEST literal (the caller's rules stand). | docstring | - | 2476 |
| `x10_probe_release` | recipe, trace | card chat-M2 (fp-35): (declared, ok, detail). declared False = no X10_PROBE literal (the caller's rules stand). | docstring | - | 2546 |
| `x10_gate` | recipe, executors, stop_after=None, from_step=None, model=None, trace=None | card 130-1 (PD267(b)): (ok, detail dict). ok False = a predicted peak > fail_above_mb, or UNMEASURED (no Executor | docstring | - | 2609 |
| `x10_probe` | recipe, graph=None | card 130-1 self-test helper: dry-run the recipe only up to its first Executor (probe) and return the records. | docstring | - | 2687 |
| `x5_count` | verbs, rows, spc, stop_after=None, from_step=None | X5 (moved out of prerun unchanged, card 115-3 F1): (ok, detail). Wire-making verbs the dry run executed == | docstring | - | 2703 |
| `census_check` | plan_path, pred_path=None, samples_path=None | -> None (no prediction file beside the plan) or {'plan', 'pred', 'overall', 'fails': [(cls, derived, declared)], | docstring | - | 2751 |
| `census_gate` | plan_paths, pred_override=None, samples_path=None, out=print | (ok, detail, lines). ok False only on a derived != declared class (CENSUS FAIL). Prints one line per plan: | docstring | - | 2770 |
| `census_unpredicted` | recipe | card 123-7: the stageplans a recipe names whose census is CENSUS-UNPREDICTED (for --scratch-required). | docstring | - | 2799 |
| `x16_in_scope` | a | True for a create action with a declared 'terminals' list that is not a const_donor constant nor a Local. | docstring | - | 2830 |
| `termclass_undeclared` | plan | X16 core: [{action, terminal}] for every in-scope create action's declared 'terminals' entry with no term_class. | docstring | - | 2836 |
| `x16_gate` | plans | (ok, detail) of X16 over loaded stageplan dicts. | docstring | - | 2848 |
| `prim_donor_labels` | path=None | {uid: label} of the original main VI (main_vi_node_labels.json: 'diagrams' lists + 'explicit' / 'implicit' maps). | docstring | - | 2878 |
| `prim_donor_check` | plan, labels=None, registry=None, base_uids=None | X17 core: [{action, why}] for every create action with a non-const_donor 'prim' whose donor label is not the prim, is | docstring | - | 2893 |
| `x17_gate` | plans, labels=None | (ok, detail) of X17 (card 141-1) over loaded stageplan dicts. | docstring | - | 2937 |
| `prerun` | recipe, graph=None, stop_after=None, from_step=None | card 103-2 (PD216(b)): stop_after=k (the recipe's own '--stop-after k', PART-A mode) makes X5 expect only the | docstring | - | 2949 |
| `x14_advisory` | recipe, n_rows, log=None | card chat-P1 item 4 (user 2026-09-28; docs/d1-loop12-17-split-plan.md Pre-decided 'rows per step'): rows per | docstring | - | 3139 |
| `result_first` | first, warn | card 106-5 (PD219(c)): the RESULT line's first_fail carrying the X10 WARN (result-line/1 has no other free-text | docstring | - | 3155 |
| `plan_md5s` | recipe | {rel path: md5} of every plan file plan_files(recipe) finds; {} when that raises. Returns dict. | side file | - | 3168 |
| `write_record` | kind, recipe, status, first_fail, extra=None | Appends one JSON line to RECORDS (prerun_records.jsonl): t, iso, kind, script, sha256, plan_md5s, status, first_fail, plus extra; a 'dry' record gets dry_rule = DRY_RULE when absent. Returns the re... | side file | - | 3175 |
| `launched_stage_scripts` | cmd | argv only: every 'tools/recipes/stage_*.py' a command RUNS - a python token followed (past flags) by that | docstring | - | 3186 |
| `vi_modifying_calls` | path | [] or the sorted MODIFY_VERBS names the file calls, when it imports stagekit (ast; never text search). | docstring | - | 3222 |
| `offline_override_delegations` | tree | card 159-a4-1 (fp-77): {id(ast.Call)} of every parent delegation inside an override method of a class derived ONLY from | docstring | selftest_c159_a4_1.py | 3261 |
| `is_vi_modifying` | path | card chat-N1 (2): True iff the .py imports stagekit AND calls a name in MODIFY_VERBS. | docstring | - | 3283 |
| `launched_vi_modifying` | cmd | argv only: launched .py scripts that are NOT tools/recipes/stage_*.py but is_vi_modifying() -> gated alike. | docstring | - | 3288 |
| `launched_py` | cmd | argv only: every script path a python token RUNS (past interpreter flags), directly or after bgrun's '--'. | docstring | - | 3294 |
| `launched_plan_runs` | cmd | argv only (card chat-S3): every 'tools/stagexec.py run <plan.json>' a command RUNS -> [(stagexec path, plan | docstring | - | 3311 |
| `plan_record` | kind, plan, status, first_fail, extra=None | A dry/prerun record for a stagexec PLAN: script = tools/stagexec.py (its sha256), plan_md5s = {plan: md5}. | docstring | - | 3335 |
| `is_stageplan` | path | True when path ends in .json and loads as JSON whose schema is 'stageplan/1'; False on any error. Returns bool. | side file | - | 3348 |
| `read_records` |  | Every parseable JSON line of RECORDS (bad lines skipped; [] when the file cannot be opened). Returns list. | side file | - | 3355 |
| `is_prerun_segment` | start_line | True when this bgrun START line runs tools/stage_prerun.py itself (a dry/prerun/check, never a stage run). | docstring | - | 3382 |
| `last_failed_run_after` | script, t_min | Newest failing bgrun run of 'script' in a log modified after t_min (protocol.run_verdict). | docstring | - | 3388 |
| `unverified_card_names` | cmd | ([label prefixes], why/None) from the task/1 card named by '--unverified-card <path>' in the command. | docstring | - | 3439 |
| `stage_key` | script | Lower-cased basename of the script with a '_v<digits>' suffix before .py removed (stage_x_v3.py -> stage_x.py): the key the retry cap counts by. Returns str. | side file | - | 3459 |
| `cycle_key` | now=None | 'cycle <n>' from the newest tools/bench/cards/cycle_<n>.json written in the last CYCLE_FRESH_S, else | docstring | - | 3463 |
| `read_stage_runs` |  | Every parseable JSON line of STAGE_RUNS (env STAGE_RUNS or tools/bench/stage_runs.jsonl; bad lines skipped, [] when unreadable). Returns list. | side file | - | 3483 |
| `retry_card` | cmd, key, used | (card id, None) when the command carries a valid judgement card for ONE more run of 'key', else (None, why). | docstring | - | 3497 |
| `offline_run_of` | cmd, s | card 148-a1-1 (fp-52, fp-58): True when 'cmd' runs script 's' in a mode its OWN scope header declares offline | docstring | - | 3516 |
| `check_cap` | cmd, s, runs, ck | (allow, why, card id/None) for ONE stage script against RETRY_CAP in cycle 'ck'. | docstring | - | 3532 |
| `pattern_signature` | recipe | sorted list - see the block comment. [] when the recipe cannot be read. | docstring | - | 3604 |
| `proven_pattern` | recipe, runs=None, recs=None | (proven: bool, stages: [stage keys whose clean run covers this signature], signature: [..]). | docstring | - | 3641 |
| `new_structure_classes` | recipe, runs=None, recs=None, sig=None | card chat-P2 item 1 (user 2026-09-28): the STRUCTURE elements of this recipe's signature ('op:<kind>' and | docstring | - | 3662 |
| `provisional_plans` | s, plan=None | [(plan path, sim_of)] for every stageplan this unit would run whose base is provisional. | docstring | - | 3711 |
| `plan_named_uids` | plan | Every positive int the plan's actions, open rows or bindings name (stagexec._ints_in over those keys) - the uids a | docstring | - | 3741 |
| `address_report` | plan, log=print, advise=True | card chat-S5 (PD337(a)): tier (a) over a stageplan against its base graph's terminal table (finalized.base, else base) | docstring | - | 3752 |
| `negative_uids_left` | plan | card chat-S5 (PD337(d)): every negative uid still in a plan's MACHINE fields - the "no negative uid left" check of a | docstring | - | 3772 |
| `read_creation_map` | path | (header, {"obj"/"diag"/"term": {sim id: entry}}, steps {k: diff n}) of ONE creation-map/1 file (stagexec | docstring | - | 3807 |
| `load_creation_map` | sim_of, graph_doc, explicit=None, cmap_dir=None, log=print | (map / None, why, meta) - the creation map of the run that SAVED stage N's artefact (the real graph). 'explicit' = a | docstring | - | 3833 |
| `rebind` | before, prov, real, prov_doc=None, real_doc=None, before_doc=None, info=None, named=None, cmap=None | (M: {negative uid -> real uid} / None, why). See the block comment, step 2. | docstring | - | 3872 |
| `carry_fs` | prov_doc, real_doc, before_doc, M, info=None | card 132-6 (PD279(b), docs/d1/ring-p3b.md:95-100): (augmented real doc / None, why). The provisional base (stagesim's | docstring | - | 4254 |
| `rebase` | plan_path, graph_path, log=print, simulate=True, out_root=None, model_dir=None, creation_map=None, cmap_dir=None | (ok, detail) - see the block comment. Writes the rebased plan to plan_path only when every check passes. | docstring | - | 4353 |
| `record_stage_run` | s, ck, card_id, cmd, by=COUNTED_BY, extra=None | Appends one run record to STAGE_RUNS: t, iso, cycle ck, stage (stage_key), script, sha256, card id, cap RETRY_CAP, by (default 'bgrun') plus extra; cmd is not stored. Returns the record dict. | side file | - | 4582 |
| `record_started` | cmdline, log=None, pid=None | Called by tools/bgrun.py right after its child STARTED (Popen returned). Appends one COUNTED line per stage | docstring | - | 4591 |
| `unit_key` | path | Stage key of a script OR a stagexec plan: basename, lower case, '_vN' stripped (stage_key for .py). | docstring | - | 4637 |
| `failure_function` | seg | The scripting function a failed run died in, from that run's own segment (see the block comment), or None. | docstring | - | 4642 |
| `stage_run_segments` | key, now=None | [(start_ts, failed, function)] of every bgrun run of stage 'key' in LOG_DIR within SCRATCH_WINDOW_S, oldest | docstring | - | 4660 |
| `scratch_pass_after` | function, t_after | Newest scratch_verify PASS record for 'function' newer than t_after: its path, or None. | docstring | - | 4691 |
| `fn_record_gate` | unit | card chat-F2 (user 2026-10-06): (allow, why) from tools/fn_records.launch_gate - every function the unit uses | docstring | - | 4714 |
| `check_scratch` | unit, now=None | (allow, why) - refuse a stage run whose last two runs failed on the same function with no newer scratch PASS. | docstring | - | 4734 |
| `function_of_text` | text | The scripting function a first_fail / fact string names: '<module>.<fn>' / 'stagexec.op:<kind>' / 'op:<OpName>'. | docstring | - | 4768 |
| `escalation_route` | card, cards_dir=None, now=None | ('scratch-verify', function, evidence) or ('escalate', None, why) for an ESCALATION card ('retry_of_card' set). | docstring | - | 4805 |
| `scratch_requirement` | recipe, runs=None, recs=None, now=None | (required: bool, why: str, proven_stages: [..]) - see the block comment. | docstring | - | 4857 |
| `scratch_skip_log` | line | Writes line to stderr and appends it to SKIP_LOG (env SCRATCH_SKIP_LOG, default tools/bench/jev_gate.log); an OSError on the append is ignored. Returns None. | side file | - | 4888 |
| `adopted_record` | script, pm | card chat-S4 A: stagexec.adopted_launch over ADOPT_LOG (None when nothing is adopted or stagexec cannot load). | docstring | - | 4900 |
| `check_launch` | cmd | (allow, why). Refuses a stage-recipe launch without a dry PASS and a prerun PASS for its CURRENT sha256 and | docstring | - | 4911 |
| `main` | argv=None | CLI: --selftest-control-lint, --control-lint, --opmodel-conformance, --buildarray-check, --rebase, --check-launch or --scratch-required run that check; else --dry/--prerun of a recipe or a stagepla... | side file | - | 5031 |

### tools/stage_shared.py

shared module; imported by 20 file(s): `tools/bench/prep_c150_a3_1_licence.py`, `tools/bench/prep_c150_a3_6_licence.py`, `tools/bench/prep_c152_b2_1_licence.py`, `tools/bench/prep_c154_a3_2b_licence.py`, `tools/bench/prep_c154_a3_2b_pred.py`, `tools/bench/prep_c155_a2_1_licence.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `base_sink_renames` | actions, base_terms, why_fmt | Licence rename table (PD365(d)): returns (ren, own, wr) - ren = [{"node", "term_uids", "why"}] per BASE owner whose SINK terminal a plan | docstring | selftest_c162_stage_shared.py | 14 |
| `checkpoint_step_table` | ops, cps, sfn, actions=None | E1 checkpoint table: returns [{"op", "kind", "action", ["ids",] "step_file", "md5"}] for each checkpoint op number k in 'cps' (0 = base), | docstring | selftest_c162_stage_shared.py | 31 |
| `insert_stub_deletes` | actions, wire_by_id, why | Returns a new action list = 'actions' with a row {"op": "delete_wire", "id": "dw_" + id[2:], "wire_uid": wire_by_id[id], "why": why} inserted | docstring | selftest_c162_stage_shared.py | 47 |

### tools/stagekit.py

shared module; imported by 328 file(s): `tools/bench/allterms_s1.py`, `tools/bench/allterms_s2.py`, `tools/bench/allterms_s3.py`, `tools/bench/allterms_s4.py`, `tools/bench/allterms_v1.py`, `tools/bench/build_kswap_88.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `Stop` | (class) | A FATAL gate. The stage stops; 'close()' still runs the hygiene tail. | docstring | - | 104 |
| `md5` | path | build_opfsinnertunnelconnect_v0.py:227 verbatim. | docstring | - | 186 |
| `version_bytes` | path, n=1 << 16 | '19 00 80 00' = LV2019, '26 00 80 00' = LV2026 (CLAUDE.md rule 1) - diag_s2_scaffold.py:133-140. | docstring | - | 195 |
| `private_bytes` |  | LabVIEW's private bytes - the COMPANION of the handle count, which is blind to VI Server refnums | docstring | - | 203 |
| `mod` | name | Lazy import of a heavy fleet module, so a no-LabVIEW self-test can import stagekit. | docstring | - | 218 |
| `Stage` | (class) | One build/diagnostic stage: pin, copy, edit, gate, save, clean up, report. | docstring | - | 229 |
| `Stage.head` | text | Prints a section header line '---------- <text>' (ASCII-safe, flushed). Returns None. | side file | - | 264 |
| `Stage.gate` | label, ok, detail='', fatal=False, kind=None | Records one gate: a failing label that gateclass.classify_gate rules LOG-only is printed SOFT, logged to gate_soft_log.jsonl and returns True; otherwise the label goes to passes / fails with a PASS... | side file | - | 267 |
| `Stage.fact` | line | Appends line to the stage's facts and prints it as '  FACT  <line>'. Returns the line. | side file | - | 287 |
| `Stage.row` | label, observed, expected=None | A NON-GATE record. Deliberately NOT at the start of the line, so a row reporting an expected | docstring | - | 292 |
| `Stage.census_snapshot` | target=None | {uid: class} of every GObject of 'target' (default the work copy) - ONE report_all run. {} in a dry run. | docstring | - | 301 |
| `Stage.census_gate` | label, before, after, declared, unpredicted=None, judged=None | Compare the measured NEW-object census (after - before, by class) with 'declared' {class: n} (e.g. the plan's | docstring | selftest_c159_cen2_ends.py | 307 |
| `Stage.safe` | label, fn, default=None | Calls fn(); on any exception keeps it as _last_exc, records a FACT '<label> raised <Type>: <msg>' and returns (default, msg); on success returns (result, ''). | side file | - | 351 |
| `Stage.left_s` |  | Seconds left before the stage's deadline: deadline_s minus the elapsed time since t0 minus reserve_s. Returns float. | side file | - | 360 |
| `Stage.dump` |  | Writes the stage record R (plus gates {pass, fail, failing, soft}, facts, rows, elapsed_s) as JSON to out_json. Returns None. | side file | - | 363 |
| `Stage.summary` |  | Prints the closing '=== GATES: n pass / m fail' line (failing labels, SOFT list), the JSON path and elapsed time, then the C6 RESULT line last. Returns 0 when no gate failed, else 1. | side file | - | 372 |
| `Stage.file_facts` | tag, path | {path, exists[, md5, size, version_bytes]} of a file, with one FACT line (md5, size, LabVIEW version bytes, or 'IS NOT ON DISK'). Returns the dict. | side file | - | 386 |
| `Stage.pin_check` | when | Every md5 pin, reported one per line. Returns True iff all hold. | docstring | - | 397 |
| `Stage.restart` |  | Standing restart authority (CLAUDE.md 3). diag_s2_scaffold.fresh:155. | docstring | - | 409 |
| `Stage.start` |  | FILES ONLY -> restart -> Preload the ORIGINAL read-only -> the dated WORK copy -> open it. | docstring | - | 422 |
| `Stage.es` | tag, target=None | One ExecState reading, appended to the timeline. RECORDED; a criterion only where a gate says | docstring | - | 478 |
| `Stage.count` | cls, target=None | Number of objects of class cls on target (default the work copy), via gscript.count. Returns int. | side file | - | 488 |
| `Stage.census` | classes=CENSUS_CLASSES, tag='', target=None | A class census by NAME, never by index - the numbers a stage's counts gate on. | docstring | - | 491 |
| `Stage.uid_index` | cls, uid, target=None | The traverse index of 'uid' RE-READ at the call site - never cached across a mutation (34(h)). | docstring | - | 503 |
| `Stage.wired_terminals` | uid, hints=(), target=None, tag='' | Every terminal row of node #uid with its wire - 'build_d1_m3a1.node_view':572, which finds the | docstring | - | 508 |
| `Stage.net_sources` | wire_uid, n=8, target=None, tag='' | THE OWNER-IDENTITY READING (build_d1_m3a3b_d3.py:589-600). 'OpWireSource_v5' is WIRE-addressed - | docstring | - | 518 |
| `Stage.broken_wire_count` | target=None, allow_mutation=False, tag='' | THE DIAGRAM-WIDE BROKEN-WIRE COUNT (build_d1_m3a3b_d3.bad_wire_count:265). ⚠️ IT MUTATES - | docstring | - | 543 |
| `Stage.scratch` | suffix, source=None | A dated scratch COPY (unique per run, deleted by 'close()') - the only surface a mutating | docstring | - | 560 |
| `Stage.drop_scratch` | path, tag='H4' | Close and DELETE one scratch now (a diagnostic that runs several cells must not hold them all | docstring | - | 574 |
| `Stage.discard_work` |  | THIS STAGE SAVES NOTHING: the dated work copy is treated as a scratch, so 'close()' deletes it | docstring | - | 592 |
| `Stage.plan_rows` | rows, tag='' | DECLARE this stage's planned re-wiring rows: (source uid/terminal) -> (sink uid/terminal). | docstring | - | 602 |
| `Stage.node_mark` | tag='' | The Node census BEFORE a mutation - 'junk_purge()' diffs against the last mark. | docstring | - | 667 |
| `Stage.junk_purge` | tag='', hints=() | THE MEASURED PURGE (build_opfsinnertunnelconnect_v0.purge_junk:288): the OpConnect* family mints | docstring | - | 674 |
| `Stage.delete_wire` | wire_uid, tag='' | build_opfsinnertunnelconnect_v0.del_wire:336 - by uid, via the LIVE traverse order. | docstring | - | 687 |
| `Stage.delete_object` | cls, uid, tag='' | build_opfsinnertunnelconnect_v0.del_node:346 - uid -> live index -> 'g.delete_object'. | docstring | - | 700 |
| `Stage.move_in` | uid, dest_diagram_index, position | build_d1_v0.move_in:318 - move an object INTO a nested diagram by uid. | docstring | - | 713 |
| `Stage.connect` | sink_diag, sink_node, sink_term, src_diag, src_node, src_term, labels=None | gscript.connect_nested_v2:2965 = 'OpConnectNested_v2' - the nested-diagram writer. | docstring | - | 719 |
| `Stage.connect_from_wire` | sink_diag, sink_node, sink_term, wire_uid, wire_term_index, labels=None | 'OpConnectFromWire_v0' - the only writer whose SOURCE need not be a node | docstring | - | 726 |
| `Stage.fs_inner_tunnel_connect` | fsit_uid, sink_diag, sink_node, sink_term, auto_route=None, target=None, op=None | 'OpFsInnerTunnelConnect_v1' (build_d1_m3a3b_d3.fsit_call:279, the POISONED caller of Pre-decided | docstring | - | 739 |
| `Stage.fs_inner_tunnel_read` | fsit_uid, target=None, tag='' | 'OpFsInnerTunnelTerm_v0' - the FSIT's two faces, read-only (build_d1_m3a3b_d3.fsit_read:342). | docstring | - | 766 |
| `Stage.wire_indicators` | node_index, src_terms, indicator_names, diagram_index=0, node_class='SubVI' | gscript.wire_indicators:1786 - branch a node's outputs onto front-panel indicators. | docstring | - | 773 |
| `Stage.add_shift_reg` | loop_index, y_position=120, class_name='WhileLoop' | gscript.add_shift_reg:687. | docstring | - | 782 |
| `Stage.wire_sr` | variant, loop_index, reg_index, **kw | gscript.wire_sr:737. | docstring | - | 788 |
| `Stage.create_local_read` | label, panel_index=None, tag='' | The BUILT local-variable creator. Its measured implementation lives in the diagnostics that | docstring | - | 794 |
| `Stage.create_local_write` | label, panel_index=None, dest_diagram_uid=None, position=(40, 40), tag='' | The WRITE twin of create_local_read (card 100-2 V5): 'gscript.create_local_write' = OpCreateLocalRead_v0 | docstring | - | 817 |
| `Stage.expect_is_broken_false` | label, reconnect, wire_uid=None | 42(b): THE ORDERED SECOND PASS. The acceptance is asserted on a SEPARATE, idempotent re-connect, | docstring | - | 832 |
| `Stage.address` | end, is_source, objs=None | A terminal named by (node uid, terminal name, frame diagram uid) -> the LIVE index triple | docstring | - | 859 |
| `Stage.resolve` | v | '$name' / '$name.key' -> self.sym; '$wire_of:<uid>:<term i>' -> that terminal's LIVE wire uid (read now, | docstring | - | 908 |
| `Stage.copy_in` | cls, uid, dest_diagram_uid, position, tag='' | COPY a primitive that already exists on the donor into Diagram #dest by 'OpMoveByIndex_v0' (the op of | docstring | - | 925 |
| `Stage.add_sr_row` | ex, tag='' | 'add_shift_reg' on the loop named by uid, then the register PAIR read back by index: {right, left, k, | docstring | - | 959 |
| `Stage.const_row` | ex, tag='' | 'OpCreateConstOnTerm_v0' ('build_opcreateconstonterm_v0.create_const_on_term':364): a constant TYPED BY | docstring | - | 979 |
| `Stage.cfw_second_pass` | src_uid, dst | 42(b)'s ordered idempotent second pass through 'OpConnectFromWire_v0', usable for ANY new wire whose sink | docstring | - | 994 |
| `Stage.live_graph` | path, retired_rights=(), extra_rights=None | The step-4 graph of a LIVE file (stage_d1_m3a4.py:104-110's recipe): wiki_build.read_live + the bed's | docstring | - | 1012 |
| `Stage.rule_check` | d | PRE-DECIDED 143: the op the row names must be the op 'jev_pairs.op_rule' names for its classes, unless | docstring | - | 1028 |
| `Stage.from_decision` | record, tag='fd' | PLAN STEP 6 / Pre-decided 142-143: execute a decision record (tools/jev_pairs.write_record shape). | docstring | - | 1040 |
| `Stage.save_route` | exec_state, broken_ok | WHICH SAVE ROUTE, as a pure function so it is self-testable without LabVIEW. | docstring | - | 1193 |
| `Stage.save` | broken_ok=False, cold_check=True | ONE save of the work copy, by the route 'save_route' picks. Records md5, size and version bytes; | docstring | - | 1204 |
| `Stage.close` | expect_files=None | HYGIENE: panels closed, refs opened == closed, scratches deleted, the input's md5 unchanged, | docstring | - | 1243 |
| `fixtures_check` | bad_md5s=(), before_listing=None | REVIEW c68-h6 (archive/peer/2026-09-24-c68-h6-fixture-listing.md §1/§4, accepted): after a run that swapped | docstring | - | 1297 |
| `match_term_uid` | term_uid, all_rows, node_rows, is_source | Pre-decided 173 (cycle 71): a terminal addressed by its TERMINAL UID after its first resolution, because a | docstring | - | 1319 |
| `uid_edges` | G, kinds=('wire', 'fs') | A graph's edges keyed by TERMINAL UID, not by name (review archive/peer/2026-09-24-c68-m4a-p6b-rename.md §4, | docstring | - | 1342 |
| `term_key` | r | A terminal row's identity: (term uid, owner uid, term name). | docstring | - | 1372 |
| `wire_keys` | rows | {(wire uid, frozenset of its SOURCE rows' term_key)} over the wired rows. A recycled wire uid on a new source is a | docstring | - | 1377 |
| `term_identity_gates` | base, sim, real, renames=None, bind=None | TD / unwired / D of a stage's end (base = graph rows before, sim = the simulated end rows, real = the read-back end | docstring | - | 1391 |
| `term_identity_names` | base, sim, real | card 141-3 (PD325(b)) as it stood until card chat-T6 - identity (term uid, owner uid, NAME), wires (wire uid, source | docstring | - | 1401 |
| `wire_ends_pos` | rows, ob=None, tb=None | {wire uid: (frozenset of source position keys, frozenset of sink position keys)} - a wire as its two ends. | docstring | - | 1454 |
| `kept_nodes` | B, gone=() | The BASE nodes that keep at least one base position key (not all in 'gone'). Only these nodes' positions are compared | docstring | selftest_t6_poskey | 1464 |
| `term_identity_pos` | base, sim, real, bind=None, renames=None | TD / unwired / D on position keys (block comment above). Returns the keys term_identity_gates always returned - | docstring | - | 1479 |
| `licence_renames` | lic | {(term uid, owner uid): (from, to)} from a pb-licence/1 dict's 'renames' list ([{node, term_uids, from?, to?}]); | docstring | - | 1525 |
| `pb_rename_rows` | base, sim, real, renames=None, bind=None | (rows, restored, unlicensed) for PB's build4 - card chat-T6 (docs/d1/result-gates.md): every real row on a KEPT BASE node (kept_nodes) | docstring | - | 1538 |
| `d4_load` | path | The D4 JSON ({s1: {path, md5}, scope_nodes}) plus 'scope' (set), 's1_md5_got' and 'names' = {node: {name: | docstring | - | 1570 |
| `d4_ok` | node, name, d4 | D4's one test: the node is in scope and S1's graph has a terminal of that name on it. | docstring | - | 1588 |
| `d4_e1` | diffs, info, d4 | (ok, accepted, bad) over [(checkpoint k, stagexec.compare dict)]; 'info' = {term uid: (owner uid, name)}. | docstring | - | 1593 |
| `d4_pb` | got, want, real_end, sim_end, d4 | (ok, closed, grown, bad) at PB. got / want = sets of (node, sink name) of cdiff(S1, real end) / the plan's | docstring | - | 1618 |
| `d4_form` | real_end, d4 | FACTS ONLY: {scope node: 'equal to S1' / 'real-only {..} S1-only {..}'} comparing the real end's name counts on | docstring | - | 1642 |
| `fixture_listing` |  | Sorted base names of the *.vi files in the folder of gscript.MOVE_DST (the move-target fixture folder). Returns list of str. | side file | - | 1660 |
| `unload_donor` | path=None | Card 97-5 (judgement c97): after the copy_in calls, drop the donor (default 'g.MOVE_SRC') from LabVIEW's memory | docstring | - | 1664 |
| `run` | fn, stage | The standard main(): run 'fn(stage)', never let an exception skip the hygiene tail. | docstring | - | 1689 |
| `jload` | *parts | json.load of os.path.join(*parts) (utf-8) - the recipes' 'J' helper. Returns the parsed object. | docstring | - | 1720 |
| `pure` | name | A NO-LabVIEW module (stagexec, stagesim, vigraph, jev_candidates, elrule) imported DIRECTLY, as the recipes import it - not | docstring | - | 1726 |
| `pos_slot_table` | G | {term key: (node, index in the node's READ order, term class, is_source)} of a vigraph graph - the same key as | docstring | selftest_c153_poskey_convert.py | 1739 |
| `pos_name_free` | P, s | One effective source ('<key>' or '<key>@<tunnel>/f<n>+...') -> (its position in table P, frame tag); an unknown key | docstring | selftest_c153_poskey_convert.py | 1752 |
| `pos_slots` | G, nodes, V=None | {sink key: ((node, index, class), frozenset of name-free effective sources)} for the input terminals of 'nodes' in | docstring | selftest_c153_poskey_convert.py | 1763 |
| `pos_convert` | rows, SA, SB | Name-keyed cdiff sink strings -> POSITION rows [{sink, slot, name_a, name_b, before, after[, passthrough]}], sorted by | docstring | selftest_c153_poskey_convert.py | 1774 |
| `pos_convert_open_rows` | plan_open_rows, old_rows, new_rows | A plan's open_rows [{node, term}] with every row dropped whose (node, name) pair the old -> new row conversion removed | docstring | selftest_c153_poskey_convert.py | 1797 |
| `s1_frame_graph` | labels=None | S1's FRAME-KEYED vigraph graph (the wiki S1 terminals + the newest graph_objs_s1 / graph_loops_s1 reads), as every ring | docstring | selftest_t7_ring.py | 1805 |
| `pred_end_graph` | L, labels, fs_pairs | The FRAME-KEYED vigraph graph of a plan's simulated end state L (its terminals, objs, loops) - the graph a pred's cdiff rows | docstring | selftest_t7_ring.py | 1814 |
| `pb_check` | S1f, G1, Gpred, pred_rows, open_rows, unlicensed=(), V=None | PB by POSITION (card chat-T7, fp-70): cdiff(S1f, G1 = the REAL end) (vigraph.computation_diff_frame) against the pred's cdiff | docstring | selftest_t7_ring | 1821 |
| `run_bind` | bind=None, report=None | The run's bindings as ONE {sim uid: real uid} map: an Executor's x.bind ({obj, term, diag}) merged, plus the union of a recorded | docstring | selftest_c158_gates386.py | 1859 |
| `real_rows_from_record` | rows5, sim_terms, flat | (rows, record): the 5-column real end rows a run records (RingSession.gate_td 'real_end_rows': term uid, owner uid, name, wire, | docstring | selftest_c158_gates386.py | 1873 |
| `frame_tag_map` | G | {(tunnel node uid, frame ordinal): frame diagram uid} of a FRAME-KEYED vigraph graph - what a tag '<tunnel>/f<k>' means on THAT | docstring | selftest_c158_gates386.py | 1912 |
| `frame_src_resolve` | src, fmap | One frame-keyed effective source '<key>' or '<key>@<tunnel>/f<k>+...' -> (key, frozenset((tunnel uid, frame diagram uid))): every | docstring | selftest_c158_gates386.py | 1925 |
| `case_move_frames` | plan, sim_end, flat | {node uid: {frame diagram uid}} - for every plan 'move_in' whose dest_diagram is a frame 'new:<as>.f<k>' of a CaseStructure the SAME | docstring | selftest_c158_gates386.py | 1942 |
| `pb_bound_rows` | cd, G, V=None | {sink: frozenset of (source POSITION key, frozenset((tunnel, frame uid)))} of a frame-keyed cdiff's rows on graph G (its 'after' | docstring | selftest_c158_gates386.py | 1961 |
| `pb_check_bound` | S1f, G1, Gpred, Gsimb, pred_rows, open_rows, move_frames, unlicensed=(), V=None, inherit=None | PB of PD386(a): pb_check(S1f, G1 = the real end, Gpred, ...) PLUS (1) the real PB == the PB of Gsimb = the sim end re-keyed by the | docstring | selftest_c158_gates386.py | 1979 |
| `pb_inherit_ctx` | plan, flat, base_vi_md5=None, labels=None, fs_pairs=None, S1f=None, V=None, adopt_path=None | The context pb_inherited_row needs, from files only (PD394(a), PD395(b)). Returns {frames {node: {frame uid}} inherited from the | docstring | selftest_c161_pbinherit.py | 2033 |
| `pb_inherited_row` | sink, y, res, G1, S1f, bound_end, ctx | Class 1 / class 2 of ONE pred-extra PB row (docs/d1/ring-p5b.md PD394(a), PD395(b)); y = its cdiff row, res = its 'after' sources | docstring | selftest_c161_pbinherit.py | 2102 |
| `pb_386` | base_terms, L, real, objs, flat, plan, pred_rows, open_rows, labels, fs_pairs, renames=None, S1f=None, V=None, inheri... | The whole PD386(a) PB from a run's pieces - what RingSession.gate_pb calls: L = the sim end (sim uids), real = the read-back end | docstring | selftest_c158_gates386.py | 2156 |
| `wire_pairs_pos` | rows, ob=None, tb=None, base_nodes=None | (Counter of (source end, sink end) pairs, {wire uid: sorted source ends} of source-only stubs) of one terminal table, ends = position | docstring | selftest_c158_gates386.py | 2178 |
| `term_identity_pairs` | base, sim, real, bind=None, renames=None | D / TD of PD386(b): term_identity_pos's dict with d_ok / td_ok re-judged PAIR-KEYED. D: the new and the lost (source, sink) pairs | docstring | selftest_c158_gates386.py | 2200 |
| `stub_sides` | hs, hr | card 159-e1-1: the one-sided source-only stubs of a sim side and a real side - hs / hr = {wire uid: source ends} -> {sim_only: | docstring | selftest_c159_cen2_ends.py | 2227 |
| `wire_end_pairs` | rows, base_terms, base_frames | card 159-e1-1 (PD389(b), docs/d1/ring-p5b.md): (Counter of (source key, sink key, frame) end pairs, {wire uid: sorted source keys} | docstring | selftest_c159_cen2_ends.py | 2239 |
| `cen2_wire_ends` | base, sim, real, base_frames=() | card 159-e1-1 (PD389(b), docs/d1/ring-p5b.md): CEN2's Wire class judged by ENDS. base / sim / real = terminal rows (base = c0's | docstring | selftest_c159_cen2_ends.py | 2273 |
| `scratch_census` | log_path, sum_json=None, key='CENSUS-ALL new uids by class (every class) ' | (census {class: n}, whole-file line number, last-segment start line) from the ONE 'key' line in the LAST bgrun segment of a | docstring | selftest_c158_gates386.py | 2291 |
| `op_class_census` | prev_rows, rows | Class census between two whole-VI terminal reads (no extra LabVIEW read): {terms: {term class: n new term uids}, owners: {owner | docstring | selftest_c158_gates386.py | 2308 |
| `op_class_census_install` | rs, ops=(16, 17) | PRINTING ONLY (PD386(c), the PD385(b) per-op census owed): wrap the ring backend's read (sink_gate_backend_class) so the whole-VI | docstring | selftest_c158_gates386.py | 2325 |
| `op_class_census_print` | h | Print one 'OPCENSUS op <k>' line per op of an op_class_census_install holder (or why it was not measured). Returns the dict. | docstring | - | 2349 |
| `retry_card_arg` | argv, script | PRINTING ONLY: the '--retry-card <path>' / 'RETRY_CARD=<path>' judgement card in a recipe's own argv (stage_prerun.RETRY_CARD_RE, | docstring | selftest_c158_gates386.py | 2364 |
| `sink_gate_spec` | e, actions, base, sim_end | One sink-gate census row (prep_*_session.json 'sink_gate_census', needs_sink_gate) -> its declared sink gate spec | docstring | selftest_t7_ring.py | 2381 |
| `sink_gate_read` | e, d, x, rows, n_actions | (ok, detail) for the deferred op error on sink d['sink'] (stage_d1_ring_p5s01a.py:90-117 sg_read, unchanged): (a) the indicator | docstring | selftest_t7_ring.py | 2406 |
| `sink_gate_backend_class` |  | stagexec.LVBackend subclass that KEEPS its last whole-VI read in 'last_terms' (no extra read; LVBackend.read is called exactly | docstring | - | 2438 |
| `SimCensus` | (class) | card 159-a4-1 (PD387(e)): a {uid: class} census snapshot taken from a stagesim STATE, not from LabVIEW; Stage.census_gate | docstring | selftest_c159_a4_1.py | 2453 |
| `sim_census_snapshot` | state, classes=None | card 159-a4-1 (PD387(e)): the SimCensus {uid: class} of one stagesim state - objs by class, terminals by term_class, every | docstring | selftest_c159_a4_1.py | 2459 |
| `census_unpredicted_reason` | pred | card 159-a4-1 (PD387(e), docs/violation-decisions.md device-failed 2026-10-10 03:2x): None when a pred's census block covers | docstring | selftest_c159_a4_1.py | 2479 |
| `RingSession` | (class) | The inputs of one ring stage session and the gates its body runs - stage_d1_ring_p5s01a.py:31-191 as calls. A recipe builds | docstring | selftest_t7_ring.py | 2498 |
| `RingSession.stem` |  | The plan file's name without .json (gate labels name it). Returns a str. | docstring | - | 2529 |
| `RingSession.sink_read` | e, d | (ok, detail) of sink_gate_read on this session's executor and last read; (True, 'dry') in a dry run. | docstring | - | 2533 |
| `RingSession.census_snapshot` | s | {uid: class} of s.census_snapshot() kept to the pred's census classes (the recipes' 'snap'). ONE whole-VI read. | docstring | - | 2539 |
| `RingSession.handles` |  | LabVIEW's handle count now (bench_prep.labview_handles); None in a dry run is the caller's business. | docstring | - | 2543 |
| `RingSession.gate_l0` | s | L0 (FATAL): plan final + open_rows_match + plan_in == <plan>_in or <plan>_in<N> (plan_in_matches_stem); base graph md5 == pred == file; | docstring | - | 2547 |
| `RingSession.executor` | s | SG (FATAL: one declared sink gate per census row) -> the backend (stagexec.DryPlanBE in a dry run, else the SGBackend | docstring | - | 2558 |
| `RingSession.run` | s | Run the executor: E1 (every checkpoint's real graph == its simulated step). On stagexec.ExecStop: save ops 1..k-1 for a | docstring | - | 2579 |
| `RingSession.gates_ng_fr_d` | s, real | NG (crossing ops' new tunnel names == the simulator's), FR (FATAL: created objects on the sim end's frames; real frames == | docstring | - | 2596 |
| `RingSession.gate_cen2` | s, c0, c1, real=None | CEN2: the new-object census between snapshots c0 and c1 == the pred's census. Returns s.census_gate's delta. | docstring | - | 2624 |
| `RingSession.gate_td` | s, real | TD: every base terminal the sim keeps wired is still wired; identities lost == the plan's deletes (position key). Records | docstring | - | 2657 |
| `RingSession.gate_pb` | s, real | PB (FATAL, before save): pb_check(S1, real end) - by POSITION (fp-70). The real end's rows get the sim end's names on kept | docstring | - | 2671 |
| `RingSession.finish` | s, h0, rk, dc, key, level, save=True | PH / HB (handles open -> save <= +700, PD236(b)), the rule-6 GUI save (broken by design), PS (saved, md5 differs, input | docstring | - | 2688 |
| `pred_x10` | pred_path, plan_path | The X10 prediction of a plan: its pred file's memory_pred.peak_mb, ONLY when pred.plan.md5 == md5(plan) (the scratch | docstring | selftest_t7_ring.py | 2708 |
| `census_all_install` | stage_cls=None | Wrap Stage.census_snapshot / census_gate (once) so every snapshot is kept and every census gate also prints the CENSUS-ALL | docstring | selftest_t7_ring.py | 2724 |
| `el_norm_ocr` | s | An Error List text -> lower-case alphanumerics with the OCR aliases applied (== errorlist_check.norm). Returns a str. | docstring | - | 2761 |
| `el_class` | it | One Error List item {raw, detail} -> its class: elrule.item_class's local / cond / sr, else input, else | docstring | selftest_t7_ring.py | 2770 |
| `el_advisory` | items, pred_path, plan_path, pred=None | (rc, report) for one Error List read (its items) against the pred's errorlist.per_class (PD354(a), ADVISORY): rc 1 only for | docstring | selftest_t7_ring.py | 2782 |
| `el_advisory_print` | rc, rep | Print the one EL-ADVISORY line of an el_advisory result. | docstring | - | 2805 |
| `el_advisory_selftest` | pred_path, plan_path | Four synthetic Error List reads built from the pred's predicted per-class counts (offline, the scratch recipes' | docstring | - | 2812 |
| `scratch_offline_modes` | argv, pred_path, plan_path | The scratch recipes' two OFFLINE modes, before any K.Stage: '--el-advisory-selftest' -> el_advisory_selftest's rc; | docstring | - | 2840 |
| `scratch_tail` | st, rc, gone, key, tag, log, base_vi, base_md5, pred_path, plan_path, card, sum_json, fail_mb, launch_mb=680.0 | After K.run of a scratch: peak private MB from the log's METER lines vs the pinned X10 (pred_x10), and the gates MEM (peak <= | docstring | - | 2852 |
| `made_symbols` | acts | The 'new:' symbols the rows create: every 'as' alias, plus <as>L / <as>R of an add_shift_reg; returns a set. | docstring | selftest_c160_stagemap.py | 2884 |
| `used_symbols` | acts, made | Sorted earlier-step symbols the rows reference: 'new:X' (address heads) or 'new:X.f<k>' (frame diagrams), minus 'made'; returns a list. | docstring | selftest_c160_stagemap.py | 2894 |
| `map_symbols` | used, sym, bound, graph | (REAL, bad, lines): each used symbol -> sim uid (sym) -> real uid (bound); a frame symbol's real uid must be an owners entry | docstring | selftest_c160_stagemap.py | 2912 |
| `map_frames` | acts, all_acts, sym, bound, owners, default_frames=('False', 'True') | (FMAP {(action id, end uid): {...,'addr': '#<uid>'}}, bad, lines): a 'frame' name on an end whose tunnel ('tunnel' action in all_acts) | docstring | selftest_c160_stagemap.py | 2939 |
| `apply_map` | acts, REAL, FMAP | The rows with earlier-step symbols -> real uids (string address 'new:X.t' in src/dst -> {'uid': real, 'term': 't'}) and mapped frame | docstring | selftest_c160_stagemap.py | 2975 |
| `bound_from_cmap` | path | (head, {sim uid: real uid}) over the obj / diag / term entries of ONE creation-map/1 file, read by stage_prerun.read_creation_map; a sim id | docstring | selftest_c160_stagemap.py | 3001 |
| `plan_in_matches_stem` | path, stem | True when the basename of 'path' without its extension is exactly <stem>_in or <stem>_in<ASCII digits> (a numbered revision of the | docstring | selftest_c160_l0stem.py | 3015 |

### tools/stagesim.py

shared module; imported by 194 file(s): `tools/bench/dedupe_check_s2b.py`, `tools/bench/diag_c100_6_parity.py`, `tools/bench/diag_c100_6_resim.py`, `tools/bench/diag_c100_6_resim2.py`, `tools/bench/diag_c100_disp_sim.py`, `tools/bench/diag_c100_plan.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `SimError` | (class) | An action that cannot be applied: an unaddressable/ambiguous terminal, an occupied sink, a cross-diagram | docstring | - | 210 |
| `md5_file` | path | MD5 hex digest of the file at path, read in 1 MiB chunks. Returns str. | side file | - | 215 |
| `load_models` | model_dir=OPMODEL_DIR | {op name: {path, md5, data}} for every *.json op model in model_dir (default OPMODEL_DIR); the name is the file's 'op' string, else its stem; an unreadable file gives {path, md5 None, data None, er... | side file | - | 240 |
| `model_for` | op, models | (params, source string, evidence, gaps) for one op. | docstring | - | 254 |
| `cfw_border_rule` | data | card 114-3 C1/C2 (review archive/peer/2026-09-28-c114b-l2b3d.md s1): 'recreate' when the MEASURED connect_from_wire | docstring | - | 276 |
| `plan_tunnel_face` | st, row | True when 'row' is a face of a tunnel an earlier 'tunnel' action of THIS plan made (a symbolic LoopTunnel/Tunnel, | docstring | - | 298 |
| `base_state` | graph, context=None | Simulator state from a graph read: deduplicated terminals, objs, loops, fs pairs, owners (context files may replace loops / fs pairs / owners), empty sym; a previous simulated end state keeps its k... | side file | - | 307 |
| `fs_measured_state` | graph | card 134-1 (PD287(b)): the Flat Sequence map of a REAL graph from what its reader MEASURED - graph['fs_measured'] = | docstring | - | 374 |
| `fs_border_gate` | graph, uses | card 134-2 (PD288(b)): gate B SCOPED, never relaxed. Every FlatSequenceOuterTunnel of a measured graph that | docstring | - | 496 |
| `completeness_gate` | g, uses=None, st=None | card 135-2 (docs/violation-decisions.md 2026-10-02 12:2x, device (1); selftest_c134_4_owners O1-O3 made a gate): a | docstring | selftest_c134_4_owners | 516 |
| `WriteGuard` | (class) | card 135-2 (docs/violation-decisions.md 2026-10-02 12:2x, device (2); PD279(c) extended to finalize and to the step | docstring | - | 564 |
| `WriteGuard.unchanged` |  | True when the current bytes of every snapshotted file and of every file in the snapshotted dirs equal the snapshot taken at construction. Returns bool. | side file | - | 584 |
| `WriteGuard.restore` |  | Puts the snapshot back: rewrites each file (deleting one that did not exist), removes files new in the dirs, rewrites the dirs' files. Returns unchanged() afterwards. | side file | - | 587 |
| `new_uid` | st | Decrements the state's negative-uid counter st['neg'] and returns it: the next simulator-made uid. Returns int. | side file | - | 608 |
| `node_rows` | st, uid | Terminal rows of the state whose graph node (vigraph.node_of) is uid. Returns list. | side file | - | 613 |
| `wire_rows` | st, w | Terminal rows of the state on wire w; [] when w is 0 or None. Returns list. | side file | - | 617 |
| `termless_wire` | st, w | card 160-a1-1 (PD390(a)): True only when 'w' is in the CURRENT object list as class 'Wire' AND has 0 terminal rows | docstring | selftest_c160_delwire.py | 621 |
| `has_source` | st, w | True when any terminal row on wire w is a source. Returns bool. | side file | - | 628 |
| `sourceless_wire` | st, w | card 160-a2-1 (docs/d1/ring-p5b.md PD391(b)): True only when 'w' is in the CURRENT object list as class 'Wire' AND none | docstring | selftest_c160_delwire.py | 632 |
| `obj_class` | st, uid | Class of uid: from the state's objs, else from the first terminal row of that node (vigraph.node_class), else None. Returns str or None. | side file | - | 640 |
| `resolve_uid` | st, ref | Plan uid reference -> uid: an int as is, 'new:<alias>' from st['sym'] (SimError when no earlier action created it), else int(ref); an unconvertible ref raises SimError. Returns int. | side file | - | 650 |
| `resolve_diag` | st, ref | A diagram field (dest_diagram / diagram / body / parent) -> a diagram uid. An int is a base diagram; the string | docstring | - | 663 |
| `parse_addr` | a | Terminal address -> {'uid': head, 'term': terminal}: a dict is copied, a '<uid>.<terminal>' / 'new:<kind><n>.<terminal>' string is split at its first '.'; anything else raises SimError. | side file | - | 684 |
| `base_case_frames` | owners, case | card 155-a1-1 (PD378(a)): the frame diagram uids of CaseStructure #case, read from an owner map ({uid: [owner class, | docstring | selftest_c155_basecase_frame.py | 696 |
| `case_frame_names` | st, case | card 155-a1-1 (PD378(a)): [[name, frame diagram uid], ...] of CaseStructure #case in frame-index order. A case THIS | docstring | selftest_c155_basecase_frame.py | 706 |
| `case_frame_of` | st, frame_diag | card 124-2 (PD249(d)): (case uid, frame index, frame name) of 'frame_diag' when it is a frame of a case THIS plan | docstring | selftest_c155_basecase_frame.py | 717 |
| `fs_of` | st, frame_diag | card 126-3: (FS uid, frame index left to right) when 'frame_diag' is a frame of a Flat Sequence THIS plan created | docstring | - | 733 |
| `resolve_addr` | st, a, want_source | The ONE terminal row an address names. Selector order: term_uid, then name; 'inner'/'outer' (or 'side') | docstring | - | 782 |
| `graph` | st, labels=None, fs_pairs=None | fs_pairs (card 106-3): an override for the state's own 'fs_pairs' (None = the state's) - the finalize cdiff graph | docstring | - | 873 |
| `effective_consumers` | G, key | The COMPUTATION sink terminals 'key''s value reaches through scheduling relays only (forward twin of | docstring | - | 885 |
| `s1_partner` | S1, G, key | Maps a graph key to the S1 key (jev_candidates.map_key) and lists its S1 wire partners: direct sinks and effective consumers for a source, direct and effective sources for a sink. Returns {s1_key, ... | side file | - | 902 |
| `seed_base_flips` | st, cascade=False | card 112-1 T3 (PD225(h)3 (iii), brief_110-3 (e)): flips made in an EARLIER session. A base-graph tunnel of a | docstring | - | 997 |
| `seed_base_flips_modelled` | st, models | seed_base_flips under the switch that arms the same-session un-flip (the move_in model's 'unflip_on_source', | docstring | - | 1023 |
| `only_sink_fate` | P, src_class | The only-sink sub-rule (card chat-S3; tools/bench/opmodels_onlysink.log): what happens to a wire whose ONLY | docstring | - | 1042 |
| `only_source_fate` | P, src_class | card 101-4, the MIRROR of only_sink_fate: a CUT wire whose ONLY source sat on the MOVED node and whose one other | docstring | - | 1050 |
| `closure_of` | st, uid | (nodes, diagrams): everything a move of 'uid' carries - 'uid' itself plus every node with a terminal on a diagram | docstring | - | 1098 |
| `op_move_in` | st, a, P, S1, labels | MOVE (card 80-6 refit to the L2-A1 reads, fixture tools/bench/sim/l2a1_real_80.json): | docstring | - | 1112 |
| `termclass_table` | path=None | The measured table (termclass_table/1) or None when absent/unreadable (then measured_term_class keeps the declared class). | docstring | - | 1283 |
| `measured_term_class` | owner_class, decl, t, table=None | (term_class, note/None) for declared terminal 't' of a created 'owner_class' node whose declared terminal list is 'decl': | docstring | - | 1294 |
| `op_add_shift_reg` | st, a, P, S1, labels | Simulates add_shift_reg: new Right/Left shift-register objects with inner faces on the body and outer faces on the parent, registered in st['loops'] (right_uids, left_of). Returns ({right, left sym... | side file | - | 1333 |
| `op_tunnel` | st, a, P, S1, labels | Simulates a tunnel: on a CaseStructure delegates to _case_tunnel, else makes a LoopTunnel with its outer face on the parent and inner face on the body (dir 'in' = inner source) and its indexing fla... | side file | - | 1396 |
| `op_delete_wire` | st, a, P, S1, labels | Simulates delete_wire on wire_uid or the one wire at address 'at' (SimError on 0 or several, or an absent wire): unwires its rows and drops DROP_WHEN_UNWIRED tunnels left unwired. Returns ({wire, n... | side file | - | 1427 |
| `op_delete_object` | st, a, P, S1, labels | Simulates delete_object: removes uid (missing_ok gives already_absent, else SimError) with its shift-register partner, applies the only-sink rule to its wires, optionally flips orphaned tunnels. Re... | side file | - | 1467 |
| `cond_row` | st, loop | card 101-3: the conditional-terminal row of a While loop a 'create' made = the body Diagram's one unnamed | docstring | - | 1496 |
| `cond_target` | st, ref | 'new:<alias>.cond' naming a WhileLoop an earlier 'create' made -> that loop's uid, else None. The conditional | docstring | - | 1507 |
| `op_wire` | st, a, P, S1, labels | Simulates a wire src -> dst: a While '.cond' sink, Flat Sequence frame / border / exit routes, else same-diagram only; a sink on a sourced wire is a SimError, a sourceless stub is detached or joine... | side file | - | 1529 |
| `op_remove_bad_wires` | st, a, P, S1, labels | Simulates Remove Bad Wires: unwires every wire whose rows have no source, several sources or no sink; with drop_unconnected_fsit also drops FlatSequenceInnerTunnels left unwired. Returns ({removed_... | side file | - | 1627 |
| `naming_table_lt_pairs` | path | card 153-b1-1: the measured LoopTunnel source shapes recorded in a naming table -> [(loop_class, inner_src_class)]. | docstring | - | 1961 |
| `cross_face_names` | st, s, a, tunnels | card 131-1: the names LabVIEW gives the faces of the tunnels ONE crossing creates. 'tunnels' = [(cls, fin, fout, | docstring | - | 1987 |
| `naming_table_check` | path=None | card 131-1: every row of the crossing table vs cross_face_names -> {rows: [(label, bad, cite)], skipped: [label], | docstring | - | 2001 |
| `op_wire_remove_loose_ends` | st, a, P, S1, labels | card 127-2 (PD255(b)/256(b)): gscript.wire_remove_loose_ends on a pre-existing wire ('wire_uid') or on every wire the | docstring | - | 2249 |
| `op_create` | st, a, P, S1, labels | card 100-3: 'diagram' may be 'new:<alias>.body'. By class: | docstring | - | 2278 |
| `op_gate` | st, a, P, S1, labels | card 100-3: a VALUE gate on a base constant (the real run reads it and stops when it equals 'stop_if'). The graph | docstring | - | 2403 |
| `op_decide` | st, a, P, S1, labels | Records an undecided choice among the action's options (no state change). Returns ({undecided: True, options}, [one candidate with intent, per-option pairs, undecided]). | side file | - | 2414 |
| `uid_edges` | G, kinds=('wire', 'fs') | stagekit.uid_edges, copied (importing stagekit pulls the LabVIEW fleet in). | docstring | - | 2428 |
| `canon` | edges, base_nodes, cls_of | Edges with every NEW object named by its class only ('NEW:<class>', terminal '*') - comparison up to | docstring | - | 2438 |
| `canon_diff` | ca, cb | Multiset difference of two canon() Counters. Returns {only_sim, only_ref (sorted elements), n = total count of both}. | side file | - | 2449 |
| `cdiff_keys` | cd | Sorted set of the 'sink' values of a computation-diff record's rows. Returns list. | side file | - | 2455 |
| `load_s1` | plan | The S1 (original computation) graph of a plan: context s1_graph file built with vigraph.build4, else context s1_key via jev_candidates.load, else None. Returns graph dict or None. | side file | - | 2460 |
| `cdiff_inputs` | plan, st, labels=None | card 106-3 (PD217(d), facts_c104c_e3.json): the node labels + fs tunnel pairs the FINALIZE cdiff graph is built | docstring | - | 2470 |
| `open_row_class` | r | PD217(c): a plan open row's PD213(d) class - a 'class' field, else the class the finalizer wrote into 'why' | docstring | - | 2494 |
| `c4_check` | S1, G, c4 | PD217(c): for every class-(4) (node, term) row, the end graph's effective sources == S1's, on every sink key of | docstring | - | 2508 |
| `open_rows_classed` | plan, S1, G, end_pairs | card 106-3: the finalize open-row rule under PD217(c)'s classes (the E3 rule applied at plan time): every declared | docstring | - | 2525 |
| `route_report` | plan_out_path, model_dir=OPMODEL_DIR, log=print, require_final=True | card 112-1 T4: stagexec.dry_run on a just-finalized plan -> {status, first_fail, rows: [{k, op, ids, route, how, | docstring | - | 2538 |
| `fs_routes_of` | steps | card 133-1: {str(action n): {"how", "variant", "id"}} for every simulated 'wire' step whose effect is a Flat Sequence | docstring | - | 2567 |
| `simulate` | plan_path, graph_path, out_root=SIM_ROOT, plan_out_dir=BENCH, model_dir=OPMODEL_DIR, labels=None, log=print, route_ch... | card 153-b1-1 (PD370(c)): 'collect_all' (default False = the unchanged replay) - an UNMEASURED refusal takes the plan's own | docstring | - | 2593 |
| `selftest` |  | Offline self-test: runs the G-numbered gates on a synthetic graph in a temp dir, printing PASS / FAIL per gate, a GATES line and a RESULT line. Returns 0 when every gate passed, else 1. | side file | - | 2888 |
| `main` | argv | CLI: 'selftest', or 'simulate <plan> <graph> [--out-root, --plan-out, --naming-table, --collect-all]' printing a SUMMARY and a RESULT line. Returns 0 final, 1 not final or collect-all, 2 (doc print... | side file | - | 3545 |

### tools/stagexec.py

shared module; imported by 388 file(s): `tools/bench/constsrc_l2a1_82.py`, `tools/bench/constsrc_l2a1_85.py`, `tools/bench/ctsrc_l2a1_82.py`, `tools/bench/diag_c100_6_parity.py`, `tools/bench/diag_c100_rows.py`, `tools/bench/diag_c101_resim.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `ExecStop` | (class) | The executor stops here (a difference, an unbound object, an unaddressable terminal). | docstring | - | 62 |
| `Meter` | (class) | Private bytes (MB) + handle count, stamped per op and per read. 'probe()' -> (private_bytes_int_or_None, | docstring | - | 95 |
| `Meter.summary` |  | Summary of the meter rows: n, first / peak private MB, last row, summed and mean MB deltas for 'op' and 'read' stamps, warned_at. Returns dict. | side file | - | 122 |
| `meter_rows_from_log` | path | card 106-3: the recorded per-op meter of one run, read back from its log's 'METER <tag> k <k> private <mb> MB' lines | docstring | - | 137 |
| `mem_predict` | rows, stop_after=None, from_step=None, start_mb=None, memstop=MEM_STOP_MB, margin_mb=0.0 | card 106-3 (retrospective-cycle103 'inference-over-measurement', PD216(f)): the private-MB peak a run over ops | docstring | - | 149 |
| `md5` | p | MD5 hex digest of file p (stagesim.md5_file). Returns str. | side file | - | 172 |
| `load_final_plan` | plan_path, require_final=True | The plan, its step states (md5-checked against 'finalized.step_files') and the actions' step numbers. | docstring | - | 186 |
| `base_cond` | ref | card 139-5 (PD316): {'uid': <BASE loop uid>, 'term': 'cond'} -> that uid (int), else None. The conditional terminal | docstring | - | 212 |
| `verbs_missing` | route | The verbs a route calls that are NOT defined in the source (a text check - the dry run imports no LabVIEW side, | docstring | - | 340 |
| `precondition_failures` | plan, ctx, stop_after=None, from_step=None | card 106-3: [{k, route, acts, ids, needs, work}] - every op the run DISPATCHES (from_step < k <= stop_after) whose | docstring | - | 373 |
| `create_route` | a | The CREATE_ROUTES key for a create action, else ExecStop (no executor for that shape). | docstring | - | 391 |
| `purge_entry` | purge, uid | The junk purge's read-back entry {uid, class, label, ...} of the created node #uid, else None. | docstring | - | 463 |
| `prim_check` | a, entry, uid=None | card 141-1: (ok, detail) for ONE created primitive: read-back label == a['prim'] and class == a['class']. | docstring | - | 474 |
| `const_born_on` | real, term, diagram | card 122-3 (PD241(a)): the row of terminal 'term' when it is the OUTPUT terminal of a diagram CONSTANT (is_const) on | docstring | - | 499 |
| `tunnel_outer_face` | real, term, diagram | card 100-6 (PD213(f)3) + card 108-6 (PD222(g)): the row of terminal 'term' when it is the OUTER SOURCE face of a | docstring | - | 513 |
| `check_symbols` | A | card 100-3: every symbolic reference names an alias an EARLIER action created; '.body' only of a loop create, | docstring | - | 534 |
| `base_case_named` | owners, case | card 155-a1-1 (PD378(a)): (case uid, ['#<frame diagram uid>', ...]) of a BASE-graph CaseStructure #case from the base | docstring | selftest_c155_basecase_frame.py | 604 |
| `base_case_of_frame` | owners, frame | card 155-a1-1 (PD378(a)): (case uid, frame names) when 'frame' is '#<diagram uid>' (FS_FACE_RE, the form a Flat | docstring | selftest_c155_basecase_frame.py | 615 |
| `plan_base_owners` | plan | card 155-a1-1 (PD378(a)): the owner map {uid: [owner class, owner uid]} of the plan's BASE graph - plan['base'] or | docstring | selftest_c155_basecase_frame.py | 626 |
| `plan_base_docs` | plan | card 160-a2-1 (extracted from plan_base_owners, card 155-a1-1): yields the loaded JSON of the plan's pinned BASE file(s), | docstring | selftest_c160_regface.py | 640 |
| `plan_base_state` | plan | card 160-a2-1 (PD391(c)): stagesim.base_state of the plan's pinned BASE graph (a graph JSON, or a step file's 'state') - | docstring | selftest_c160_regface.py | 651 |
| `base_register_end` | st, end, want_source | card 160-a2-1 (docs/d1/ring-p5b.md PD391(c)): 'srR' / 'srL' when the plain plan end 'end' names, on the BASE state 'st' | docstring | selftest_c160_regface.py | 662 |
| `case_frame_op` | A, i, fr, owners=None | card 124-2 (PD249(d)): {frame, frame_index, case} of wire action i whose end(s) carry 'frame' - read from the PLAN: | docstring | - | 692 |
| `fs_wire_ops` | A | card 126-3 (PD253(e)): {wire action index: op fields} for the wires a FLAT SEQUENCE route takes, read from the PLAN | docstring | - | 768 |
| `compile_plan` | plan, owners=None | [{kind, acts:[action indices 1-based], ...}] - one entry per REAL op, in order. Raises ExecStop on a shape the | docstring | selftest_c155_basecase_frame.py | 841 |
| `dedupe` | terms | The terminal rows with repeated term_uids dropped, first wins (vigraph.dedupe_rows without its record). Returns list. | side file | - | 977 |
| `edges` | terms | Groups terminal rows by wire_uid; returns (E, dang): E = set of (source term_uid, sink term_uid) pairs of every wire, dang = term_uids on a wire that has no source or no sink. | side file | - | 981 |
| `translate` | state_terms, bind | Sim rows with created (negative) uids replaced by their bound real uids. Unbound negatives stay negative. | docstring | - | 997 |
| `compare` | sim_terms, real_terms, bind, allow_either=() | {n, only_sim_terms, only_real_terms, only_sim_edges, only_real_edges, dangling_sim_only, dangling_real_only}. | docstring | - | 1008 |
| `step_soft` | d | card chat-S3 (PD328(c)): True when this step diff is LOG-only by gateclass (tunnel face rows only). | docstring | - | 1035 |
| `classify_step_diff` | plan, last_act, d | PD214(c) (user-side plan decision, cycle 101): a step difference made ONLY of sourceless (dangling) terminals - | docstring | - | 1057 |
| `uid_reuse` | prev_real, real | Evidence that LabVIEW re-issued a freed uid to a NEW object within one op (hyp-optunouter-uidreuse-85.md:78-82; NI: | docstring | - | 1078 |
| `bind_new` | prev_real, real, sim_prev, sim_now, bind | Bind the objects the simulation created between sim_prev and sim_now to the real objects that appeared between | docstring | - | 1101 |
| `tunnel_name_check` | sim_prev, sim_now, real_prev, real_now | card 132-1 (PD275(c)): the per-op TUNNEL-NAME gate. The NEW rows owned by a *Tunnel object (term_uid absent from the | docstring | - | 1204 |
| `is_crossing_op` | step_effects | card 132-1 (PD275(c)): an op is a CROSSING op when one of its plan actions' simulated steps lists created border tunnels | docstring | - | 1222 |
| `bind_by_frames` | cls, su, ru, new_sim, new_real, dg, bind | Bind several created 'cls' objects of ONE op by their faces' frames. Object key = the sorted (term_class, is_source, | docstring | - | 1233 |
| `bind_fs_tunnel` | prev_real, real, sim_prev, sim_now, bind | card 126-3: bind the FlatSequenceInnerTunnel a cross-frame wire made (stagesim._fs_frame_wire). Its FOUR rows are filed | docstring | - | 1260 |
| `bind_case_faces` | prev_real, real, sim_prev, sim_now, bind | card 120-3 R2: bind a created case SELECTOR ('Tunnel') or case DATA tunnel (SelectorTunnel) - one outer face plus ONE | docstring | - | 1297 |
| `is_ct` | r | True when the terminal row is a front-panel ControlTerminal node (vigraph.node_class == 'ControlTerminal'). Returns bool. | side file | - | 1373 |
| `listed_as_node` | r | Constant / Tunnel / Terminal are OUTSIDE the Node branch of the VI Server hierarchy (gobject/constant/.., | docstring | - | 1384 |
| `is_const` | r | PD188(c) (card 85-1): a diagram CONSTANT end - outside Diagram.Nodes[] (listed_as_node), addressed by its class | docstring | - | 1399 |
| `loop_parent` | st, L | The diagram uid a loop sits on: its own non-body rows, else its registers' / tunnels' OUTER faces (one value). | docstring | - | 1406 |
| `touched_diagrams` | plan, st | Base diagram uids the plan touches: moved nodes' source diagrams, move destinations, register/tunnel parent + body, | docstring | - | 1434 |
| `listing` | rd, diag, cls | {(class, uid)} of reader rd's Nodes[] on diagram uid 'diag' (None when the reader has no such diagram). | docstring | - | 1459 |
| `reader_parity` | real_rd, sim_rd, diags, cls_real, cls_sim | [{diagram, n_real, n_sim, only_real, only_sim}] per diagram; 'n' = total one-side-only entries. | docstring | - | 1467 |
| `classes_of` | st_or_rows, objs | uid -> class, from the objects list, else from the terminal rows (node_of / node_class). | docstring | - | 1481 |
| `connect_route` | addr, real, src, dst, loop_of | The connect route BOTH backends take (so the dry run sees what the real run does): 'indicator' (panel sink, wired | docstring | - | 1494 |
| `base_registers` | st | card 112-1 T1: {register uid: {"loop": loop uid, "right": its RightShiftRegister uid, "cls": class}} for every | docstring | - | 1623 |
| `base_sr_route` | real, src, dst, base_regs | card 112-1 T1: (variant, register uid, body-side terminal) when a plain 'wire' row touches the INNER face of a | docstring | - | 1638 |
| `face_twins` | rows, r, owners | PD191(b): the owner-routed OUTER faces on the same owner structure as row r with r's (name, direction) - r included. | docstring | - | 1652 |
| `tunnel_owner` | rows, tun, owners | The structure uid owning tunnel 'tun' (via its inner frame diagrams in 'owners'), else ExecStop. | docstring | - | 1667 |
| `loop_inner_face_route` | rows, rs, owners | card 157-a1-1 (docs/d1/ring-p5.md PD381(b)): the info fields of the 'cfw' route for an UNWIRED inner face of a While / | docstring | selftest_c157_innerface.py | 1677 |
| `struct_parent_diags` | rows, struct, owners | card 158-a2-1: the diagram uid(s) structure 'struct' sits on, read from the graph alone - the OUTER faces of the tunnels | docstring | selftest_c158_wire0face.py | 1699 |
| `loop_face_wire0_act` | rows, rs, rd, owners | card 158-a2-1 (PD385(a)(b)): the act for an UNWIRED While/For LoopTunnel inner face routed 'cfw' by | docstring | selftest_c158_wire0face.py | 1719 |
| `state_addr` | st, zero_terms=() | card 158-a2-1 (extracted from route_on_state, card 157-a1-1): a deep copy of a simulated / recorded STATE with the wire | docstring | selftest_c158_wire0face.py | 1742 |
| `route_on_state` | st, src, dst, zero_terms=() | card 157-a1-1: connect_route on a simulated / recorded STATE, addressed as the dry backend addresses it (Addr over | docstring | selftest_c157_innerface.py | 1757 |
| `Addr` | (class) | Terminal -> live index triple (Diagram idx, Nodes[] idx, Terminals[] idx). 'rd' = reader with diagrams(), | docstring | - | 1770 |
| `Addr.snap_loop` | loop, diag | Stores the loop's current Terminals[] list ((name, is_source, wire) per entry, _loop_list) as its key snapshot, creating its slot {diag, keys, track} if absent. Returns None. | side file | - | 1799 |
| `Addr.track_new` | loop, r_outer, l_outer | After add_shift_reg on loop: difflib of the snapshot vs a fresh Terminals[] list; anything but insertions, or not exactly one inserted source + one sink, raises ExecStop; tracks r_outer / l_outer a... | side file | - | 1803 |
| `Addr.retrack` |  | Re-reads every tracked loop's Terminals[] list and remaps its tracked face indexes (identity when the count is unchanged, else a difflib match on (direction, wire)); an unmatched face becomes None.... | side file | - | 1821 |
| `Addr.triple` | real, term_uid, is_source, loop_of=None | Live address of term_uid: exactly one row in 'real' with the wanted is_source, else ExecStop; resolved by _triple and cached as (node uid, terminal index) when wired. Returns ((diagram idx, node id... | side file | - | 1850 |
| `Addr.ct` | real, term_uid | PD187(b) / 179(b): a ControlTerminal end -> {ct, diag, didx, name, is_source, wire}. term_uid == its own uid, | docstring | - | 1862 |
| `Addr.const` | real, term_uid | PD188(c): a bare diagram-CONSTANT source -> {const, cls, term}. Its terminal row must be the constant's own | docstring | - | 1887 |
| `Addr.tun` | real, term_uid | PD191(b): a structure tunnel's OUTER face -> {tun, cls, term}, addressed by the TUNNEL uid (Tunnel.Outside | docstring | - | 1903 |
| `load_binding` | src, plan_path, from_step | card 103-4 (PD215(b) Part B): the Part-A binding -> {bind, loop_of, sym_real} with INT keys. 'src' = the dict | docstring | - | 2019 |
| `bind_state` | st, bind | card 103-4: a simulated step state with every created (negative) uid replaced by its Part-A real uid - owner, | docstring | - | 2042 |
| `bound_owners` | owners, bind | card 104-2: a SIMULATED step's owners map (str(frame diagram uid) -> [structure class, structure uid]) with every | docstring | - | 2115 |
| `required_checkpoints` | ops, lo=0, hi=None | card 161-a1-1 (docs/d1/ring-p5b.md PD393(a)): the ops a checkpoint set MUST hold when ops lo+1..hi of a compiled op | docstring | selftest_c161_delckpt.py | 2139 |
| `move_in_runs` | ops | card 158-a1-2 (docs/d1/ring-p5.md PD384(b)): the maximal runs of consecutive READ_KINDS (move_in) ops of a compiled op | docstring | selftest_c158_runcheck.py | 2152 |
| `checkpoint_ops` | ops | card 157-a1-1 (docs/d1/ring-p5.md PD379(e), PD381(d)), rule changed by card 158-a1-2 (PD384(b)) and card 161-a1-1 | docstring | selftest_c158_runcheck.py | 2168 |
| `run_fate_lines` | run, ops, step_of, read_rows, bind_term=None | card 158-a1-2 (docs/d1/ring-p5.md PD384(b)): the FATE lines of one run of consecutive move_in ops ('run' = op numbers, | docstring | selftest_c158_runcheck.py | 2178 |
| `fate_lines` | n, eff, prev_terms, read_rows, bind_term=None | card 157-a1-1 (docs/d1/ring-p5.md PD381(c)): the FATE record of plan step n (a move_in) - one line per wire the sim | docstring | selftest_c157_innerface.py | 2192 |
| `Executor` | (class) | PD193(a), card 86-4: 'checkpoints' = the real-op numbers k after which the whole-VI read + step diff run. None = | docstring | - | 2216 |
| `Executor.step` | n | The simulated step n's JSON file (step_paths[n] from load_final_plan; 0 = base), loaded. Returns the step dict ('state', 'effect'). | side file | - | 2273 |
| `Executor.face_soft` | k, kind, d | card chat-S3 (PD328(c)): an E1 step diff of tunnel face rows only. One '  SOFT  ' line per step and one | docstring | - | 2380 |
| `Executor.part_a_record` |  | card 103-1 PART-A (PD215(b)), after run() with stop_after=k: (a1, a2, detail, binding). | docstring | - | 2397 |
| `Executor.resume_record` | stop_msg='' | card chat-S4 R: after an ExecStop IN op k (self.cur), the resume/1 record for from_step k-1 - the binding exactly as | docstring | - | 2416 |
| `Executor.sim_uid` | st, ref | A simulated uid: an int ref as is, else st['sym'][ref] (KeyError when the symbol is unknown). Returns int. | side file | - | 2474 |
| `Executor.diag_real` | st, ref | card 100-3: a diagram field -> the REAL diagram uid (an int as is; 'new:X.body' through the binding the create | docstring | - | 2479 |
| `Executor.obj_real` | st, ref | Plan object ref -> REAL uid: stagesim.resolve_uid on state st, then the 'obj' binding (a positive uid passes through); a still-negative uid raises ExecStop. Returns int. | side file | - | 2493 |
| `Executor.real_term` | st_prev, st_after, addr_ref, want_source | The plan end -> the REAL terminal uid: resolved on the simulated state (the plan's own resolver), then | docstring | - | 2500 |
| `Executor.run` |  | Runs the compiled ops: base / FROM-STEP read vs its simulated step, reader PARITY, PRIME address proofs, CHECKPOINT set; per op execute, read (whole or per owner), bind, retrack, compare to the sim... | side file | - | 2512 |
| `Executor.execute` | op, prev, after, real | One compiled op -> its backend call by kind (move_in, create, gate, stop, add_sr, wire_sr, tunnel, connect_term_uid, wire_remove_loose_ends, case_frame_wire, branch, connect, delete_wire, delete_ob... | side file | - | 2842 |
| `LVReader` | (class) | Live reader over gscript on the work copy that Addr addresses through (diagrams, node_uids, node_terms, node_term_uids, ct_uids, obj_uids); SimReader is its offline analogue. | side file | - | 3054 |
| `LVReader.diagrams` |  | Uids of every Diagram of the work copy (gscript.report_all 'Diagram'), in traverse order. Returns list of int. | side file | - | 3058 |
| `LVReader.node_uids` | didx | Uids of the nodes of diagram index didx, from gscript.node_labels. Returns list of int. | side file | - | 3061 |
| `LVReader.node_terms` | didx, nidx | The terminal list of node nidx on diagram didx as gscript.node_terms_uid returns it. Returns its result unchanged. | side file | - | 3064 |
| `LVReader.node_term_uids` | didx, nidx | card 112-2 D2: one TERMINAL uid per Terminals[] entry of Nodes[nidx] (gscript.node_terms_uids, OpNodeTermsUid_v0), | docstring | - | 3067 |
| `LVReader.ct_uids` |  | Set of uids of every ControlTerminal of the work copy (gscript.report_all). Returns set of int. | side file | - | 3080 |
| `LVReader.obj_uids` | cls | Uids of every object of class cls on the work copy (gscript.report_all), traverse order. Returns list of int. | side file | - | 3083 |
| `check_sink_gates` | sink_gates, gates | SINK GATES (card 80-3, retrospective-cycle79 device-failed at the old whitelist here): a recipe may let a | docstring | - | 3087 |
| `sink_gate_for` | tag, err, sink, decls | The declaration whose sink == 'sink' exactly, else ExecStop (the op error stops the run). | docstring | - | 3104 |
| `LVBackend` | (class) | Every mutator is a stagekit / gscript verb the L7 stages used; each is followed by the measured junk purge. | docstring | - | 3114 |
| `LVBackend.run_deferred` |  | Executor.run's last act: every deferred op error's declared gate READS its sink now; a gate that fails stops. | docstring | - | 3135 |
| `LVBackend.read` |  | Live terminal read of the work copy via wiki_build.read_live (with the fs pairs); stores its secs and objs, returns the deduplicated terminal rows. Returns list. | side file | - | 3144 |
| `LVBackend.obj_classes` | real | {uid: class} for the read rows, objects from the last live read first (classes_of). Returns dict. | side file | - | 3150 |
| `LVBackend.set_description` | uid, text | In-VI tag write via gscript.set_description(work, uid, text); raises ExecStop when gscript has no such verb yet or the op returns err. Returns the op record. | side file | - | 3156 |
| `LVBackend.get_description` | uid | In-VI tag read via gscript.get_description(work, uid); raises ExecStop when gscript has no such verb yet. Returns its 'text' (str or None). | side file | - | 3165 |
| `LVBackend.move_in` | uid, dest, pos, op | Stage.move_in of uid into the diagram index of dest at pos, then the junk purge; an op error raises ExecStop. Returns {err, s}. | side file | - | 3177 |
| `LVBackend.add_sr` | loop, y, op | Stage.add_shift_reg on the WhileLoop loop (its traverse index) at y_position y, then the junk purge; an op error raises ExecStop. Returns {err, s}. | side file | - | 3181 |
| `LVBackend.wire_sr` | variant, loop, right, term, real, op | Wires a shift register face: register index of 'right' in the WhileLoop's Shift Registers[] (ExecStop if absent), Addr.triple of term (source iff RightIn), Stage.wire_sr, junk purge; op error raise... | side file | - | 3196 |
| `LVBackend.connect` | src, dst, real, loop_of, op | Wires src -> dst by connect_route's kind: indicator, ctlsink/ctltun (wire_ctlsink), tunouter, ctl (wire_control), const_sr, const, cfw (connect_from_wire; loop_face_wire0 when the source has no wir... | side file | - | 3216 |
| `LVBackend.indicator` | rs, rd | Stage.wire_indicators from a WIRED source to a panel sink on the source's diagram (bare source: ExecStop); an op error is DEFERRED to the declared sink gate (sink_gate_for) instead of stopping. Ret... | side file | - | 3332 |
| `LVBackend.create` | route, a, args, real, op | One 'create' row -> its verb (CREATE_ROUTES). Returns {err, s, uid[, body], how}. Every verb is followed by the | docstring | - | 3353 |
| `LVBackend.stop` | loop, src, real, op | OpStopFromNode_v0 (tools/recipes/build_opcreateconstonterm_v0.py:528-537): the While loop's conditional terminal | docstring | - | 3569 |
| `LVBackend.value_gate` | uid, a, op | read_bool_const (OpConstValueB_v0, card 100-2 V4): the stage STOPS when the value equals 'stop_if'. | docstring | - | 3592 |
| `LVBackend.recheck_gate` | uid, a, op | card 103-4 PART-B ENTRY: the value gate Part A passed, READ again on the loaded file (same read, no edit). | docstring | - | 3603 |
| `LVBackend.branch` | tun, dst, real, loop_of, op, side='outer' | Branches off tunnel tun's wired source face (outer, or inner when side='inner') to dst: a panel sink via indicator, else connect_from_wire (_cfw) on the face's wire; no wired face raises ExecStop. ... | side file | - | 3607 |
| `LVBackend.case_frame_wire` | case, k, src, dst, real, op | card 124-2 (PD249(d)): gscript.case_frame_wire (card 124-1's verb, the contract in brief_124-2.md) wires src -> dst | docstring | - | 3623 |
| `LVBackend.connect_term_uid` | src, dst, real, op | card 124-6 (PD250(c)): gscript.connect_term_uid(work, sink=dst, src=src) for an R1/R2 tunnel group. A missing verb, | docstring | - | 3649 |
| `LVBackend.loop_face_wire0` | rs, rd, real, op | card 158-a2-1 (PD385(a)): the live act for an UNWIRED While/For LoopTunnel inner face (connect_route 'cfw' with | docstring | selftest_c158_wire0face.py | 3674 |
| `LVBackend.loop_face_sink` | a, real, op | card 165-1-1 (PD400(b)): the live act for an UNWIRED While/For LoopTunnel inner face as the SINK (loop_inner_face_sink's | docstring | selftest_c165_innerface.py | 3684 |
| `LVBackend.rle` | wires, op | card 127-2: gscript.wire_remove_loose_ends on each live wire; a uid echo error or a wire still Is Broken? True after | docstring | - | 3692 |
| `LVBackend.index_mode_fix` | tun, indexing | Sets LoopTunnel #tun's IndexMode to 1 (indexing) or 0 with gscript.set_index_mode when it differs, re-reads it and raises ExecStop if it still differs. Returns the wanted mode (int). | side file | - | 3709 |
| `LVBackend.delete_wire` | w, op, plan_wire=None | Stage.delete_wire of wire w, then the junk purge; an op error raises ExecStop. Returns {err, s}. | side file | - | 3720 |
| `LVBackend.delete_object` | cls, uid, op | Stage.delete_object of class cls #uid, then the junk purge; an op error raises ExecStop. Returns {err, s}. | side file | - | 3724 |
| `LVBackend.rbw` | op | Remove Bad Wires through Stage.broken_wire_count(allow_mutation=True). Returns {'rbw': its result}. | side file | - | 3728 |
| `SimReader` | (class) | Offline analogue of LVReader over a SimBackend state: lists diagrams, nodes (owner-routed tunnel faces on their owner, loops on their parent), node terminals, ControlTerminals and objects as LabVIE... | side file | - | 3734 |
| `SimReader.diagrams` |  | Sorted union of every terminal row's frame_diagram and the diagrams the plan made (st['diagrams'] keys). Returns list of int. | side file | - | 3738 |
| `SimReader.node_uids` | didx | Offline Nodes[] of diagram index didx: uids of rows listed as nodes, owners of owner-routed tunnel faces, then loops whose parent is this diagram (or unplaceable), first-seen order. Returns list of... | side file | - | 3756 |
| `SimReader.node_terms` | didx, nidx | Offline Terminals[] of node nidx on diagram didx: its own rows (no NOT_NODES class, no ControlTerminal), its routed tunnel outer faces and, for a loop, its registers' outer faces. Returns (node uid... | side file | - | 3773 |
| `SimReader.node_term_uids` | didx, nidx | card 112-2 D2: the offline analogue of OpNodeTermsUid_v0 - each listed entry's own terminal uid. | docstring | - | 3786 |
| `SimReader.ct_uids` |  | Set of term_uids of the state's ControlTerminal rows (the report_all 'ControlTerminal' analogue). Returns set. | side file | - | 3790 |
| `SimReader.obj_uids` | cls | Owner uids of the state's terminal rows whose owner_class is cls, first-seen order (the report_all analogue). Returns list of int. | side file | - | 3793 |
| `SimBackend` | (class) | The DRY backend: every real op applies the plan actions it covers with stagesim's own OPS on a private state | docstring | - | 3801 |
| `SimBackend.read` |  | Deep copy of the private state's deduplicated terminal rows. Returns list. | side file | - | 3814 |
| `SimBackend.read_owners` | uids | card chat-S4 B: the per-owner read - the rows of these owner uids only (what read() would return for them). | docstring | - | 3819 |
| `SimBackend.obj_classes` | real | {uid: class} for the given rows, the private state's objs first (classes_of). Returns dict. | side file | - | 3824 |
| `SimBackend.move_in` | uid, dest, pos, op | Dry move_in: a destination diagram not in the reader's diagram list is recorded via _unroutable, else the op's plan actions are applied (_apply). Returns {applied, check}. | side file | - | 3902 |
| `SimBackend.add_sr` | loop, y, op | Dry add_sr: applies the op's plan actions on the private state (_apply), no check. Returns {applied, check None}. | side file | - | 3907 |
| `SimBackend.create` | route, a, args, real, op | Dry create: checks the route's real-backend preconditions (verbs defined, diagram listed, per-route end / owner / label checks; failure -> _unroutable), then _apply and adds the uid(s) LVBackend wo... | side file | - | 3923 |
| `SimBackend.stop` | loop, src, real, op | Dry stop: stop verb defined, loop in the loop table, source a Nodes[] node end (_node_end), else _unroutable; then _apply with that check. Returns {applied, check}. | side file | - | 4019 |
| `SimBackend.value_gate` | uid, a, op | Dry value gate: gate verb defined and uid a BooleanConstant of the reader, else _unroutable; then _apply (no value offline). Returns {applied, check, value None}. | side file | - | 4031 |
| `SimBackend.recheck_gate` | uid, a, op | card 103-4: the dry side of a Part-B entry's gate re-read - the constant must still be a BooleanConstant of | docstring | - | 4044 |
| `SimBackend.wire_sr` | variant, loop, right, term, real, op | Dry wire_sr: the terminal's Addr triple and resolved name (_check, source iff RightIn) plus route / loop / right, else _unroutable; then _apply. Returns {applied, check}. | side file | - | 4051 |
| `SimBackend.connect` | src, dst, real, loop_of, op | Dry connect: the real backend's connect_route, the sink's address checked (_check) unless indicator (ctlsink: source triple), the loop_face_wire0 act added for a cfw from an unwired face; failure -... | side file | - | 4069 |
| `SimBackend.branch` | tun, dst, real, loop_of, op, side='outer' | Dry branch: tunnel tun needs exactly one wired source face (outer, or inner when side='inner') and an addressable sink (_check, skipped for a ControlTerminal), else _unroutable; then _apply. Return... | side file | - | 4087 |
| `SimBackend.case_frame_wire` | case, k, src, dst, real, op | card 124-2 (PD249(d)): the dry side of gscript.case_frame_wire - the verb is defined, the case exists with a frame | docstring | - | 4103 |
| `SimBackend.connect_term_uid` | src, dst, real, op | card 124-6 (PD250(c)): the dry side of an R1/R2 group - the verb is defined; one end is a shift register's INNER | docstring | - | 4201 |
| `SimBackend.index_mode_fix` | tun, indexing | Dry IndexMode fix: nothing is read or set. Returns 1 when indexing, else 0. | side file | - | 4243 |
| `SimBackend.delete_wire` | w, op, plan_wire=None | Applies the op's plan actions with stagesim OPS on the private state (_apply: created ids renumbered positive). Returns {applied, check None}. | side file | - | 4246 |
| `SimBackend.delete_object` | cls, uid, op | Applies the op's plan actions with stagesim OPS on the private state (_apply: created ids renumbered positive). Returns {applied, check None}. | side file | - | 4249 |
| `SimBackend.rbw` | op | Applies the op's plan actions (remove_bad_wires) with stagesim OPS on the private state via _apply. Returns {applied, check None}. | side file | - | 4252 |
| `SimBackend.rle` | wires, op | Dry wire_remove_loose_ends: verb missing -> _unroutable; else _apply, then ExecStop unless the simulator's own wires for the row (last_effects 'wires') are non-empty and equal the executor's live w... | side file | - | 4255 |
| `from_step_state` | plan_path, from_step, binding | card 103-4: the offline stand-in for the saved Part-A file - simulated step (last act of op k) with every created | docstring | - | 4270 |
| `rel_root` | p | Absolute path of p relative to the project root with forward slashes; the absolute path when on another drive. Returns str. | side file | - | 4316 |
| `is_real_backend` | be | True for a backend that drives LabVIEW (LVBackend, possibly wrapped by RetireGuardBE); False for SimBackend and its | docstring | - | 4323 |
| `tag_switch` | path=None | The in-VI tag switch (default OFF): tools/bench/creation_tag.json {"enabled": false}. Missing/unreadable -> OFF. | docstring | - | 4332 |
| `tag_text` | stage, plan_id, sim_uid | The Description text of a created object: 'claude-plan:<stage>:<plan action id>:<sim id>'. | docstring | - | 4341 |
| `parse_tag` | text | (stage, plan id, sim id) of a tag_text string, else None. | docstring | - | 4346 |
| `adopt_stage_key` | path | The stage a script belongs to: basename, lower case, '_vN' and a '_scratch<N>' suffix stripped | docstring | - | 4352 |
| `adopt_verdict` | text, required=() | Pure: {ok, why, n_pass, stop_fails, log_fails, missing, stops, results} for one scratch log segment. | docstring | - | 4360 |
| `adopt_scratch` | script, log_path, artefact, input_vi, input_md5, plan_md5s, required, path=None, claudedev=None, note='', now=None | A: (ok, record / reasons). The scratch run's own log segment (the last BGRUN segment) must pass adopt_verdict; the | docstring | - | 4414 |
| `read_adoptions` | path=None | Every JSON row of the adoption log (path, default tools/bench/adopted_scratch.jsonl); unparsable lines skipped, [] when absent. Returns list of dicts. | side file | - | 4453 |
| `adopted_launch` | script, plan_md5s, path=None | A, the launch gate's question: the newest non-revoked adopt/1 record of this stage (the scratch wrapper and the stage | docstring | - | 4465 |
| `prefix_fingerprint` | plan, s_act | R: sha256 of the base graph md5 + actions 1..s_act - what must be unchanged for a FIXED plan to resume at s_act. | docstring | - | 4474 |
| `plan_bed_vi` | plan | The real bed VI a plan's base graph was read from (its 'vi' key), or None. | docstring | - | 4482 |
| `write_resume` | rec, file_path, cycle, out_path=None, plan=None | R: complete a resume_record with the scratch file saved as-is (path + md5) and the cycle, refuse the bed, write JSON. | docstring | - | 4490 |
| `load_resume` | path, plan_path, cycle | R: the resume record -> the binding dict Executor(from_step=rec['stop_after'], binding=...) takes, after the checks: | docstring | - | 4508 |
| `save_for_resume` | s, x, e, cycle=None | R, a recipe's ExecStop handler (before report_stop): the resume record of the stop, the scratch SAVED AS-IS (Stage.save | docstring | - | 4532 |
| `adopt_cli` | argv | 'py tools/stagexec.py adopt --script S --log L --artefact VI --input VI --input-md5 M --required E1,PB,PS [--plan P ...]' | docstring | - | 4556 |
| `DryPlanBE` | (class) | stage_prerun's dry backend for a plan-executing recipe (stage_d1_disp.DryBE, after stage_d1_l2a1.DryBE): the plan's | docstring | - | 4581 |
| `w0_wires` | s, base, from_step, dry | W0: the pre-existing Wire uids W1 judges RBW against - S1's from the plan base graph for a PART-B run (== Part A's | docstring | - | 4599 |
| `retire_check` | rows, uids | (ok, detail) on ONE terminal read: 'uids' = the nodes one delete removes (a register pair). FAILS when a node of | docstring | - | 4614 |
| `retire_ends` | base_rows, rows, retire | (ok, detail): every wire that carried a terminal of a retired node AND a terminal of a kept node still carries, | docstring | - | 4629 |
| `RetireGuardBE` | (class) | Wraps a backend (LVBackend or DryPlanBE): delete_object first reads the graph ('read()' = the live file, or the | docstring | - | 4655 |
| `RetireGuardBE.delete_object` | cls, uid, op | Re-reads the graph and runs retire_check on uid's pair (pairs[uid] or [uid]), records it as an LC gate; a FAIL raises ExecStop before anything is deleted, else the wrapped backend's delete_object. ... | side file | - | 4669 |
| `report_stop` | s, x, be, e | An ExecStop inside Executor.run: record the report / meter / step diffs, list every unroutable row, FAIL E1 fatally. | docstring | - | 4678 |
| `log_step_diffs` | s, x | Every recorded step diff as a STEP-WARN / STEP-DIFF fact; returns the FAIL-class ones (PD214(c): WARN = dangling only, | docstring | - | 4694 |
| `b1_gate` | s, x, from_step | PART-B entry gate (card 103-4): the entry read == simulated step from_step (or a WARN), gates re-read, parity, PRIME, | docstring | - | 4705 |
| `part_a_gates` | s, x, be, stop | card 103-1 PART-A (PD215(b)): ops 1..stop only, step stop real == sim (WARN only), gui_save, md5 + binding JSON. | docstring | - | 4715 |
| `w1_rbw` | s, be, w_pre | W1 (PD211(b) / PD212(f)): termless wires after the batch, then RBW on the work copy - it may remove only pre-existing | docstring | - | 4726 |
| `e3_gate` | s, plan, x, be, real, wiki, dry, tag | PD217(c) E3 (FATAL, before save) on the executor's end - also in the dry run, where a failing E3 is a FAIL | docstring | - | 4746 |
| `kill_labview_at_exit` |  | A live recipe's last act: taskkill LabVIEW and report whether it is gone (CLAUDE.md 1b grant: every cycle ends with | docstring | - | 4758 |
| `dry_run` | plan_path, fault=None, log=print, model_dir=None, require_final=True, from_step=None, binding=None, checkpoints=None | (status, first_fail, executor). No LabVIEW. require_final=False = the DIAGNOSTIC routability run (card 100-3). | docstring | selftest_c158_runcheck.py | 4769 |
| `prerun_plan` | plan_path, log=print, model_dir=None | Offline gates for a plan launch: final + step files intact (load_final_plan), compile, open_rows declared and | docstring | - | 4803 |
| `e3_wiki` | plan | The S1 wiki record whose fs tunnel pairs + graph summary build the E3 end graph (context fs_pairs_wiki, else s1_key). | docstring | - | 4838 |
| `e3_graph` | plan, ex, objs, real, wiki, tag='E3 end' | The END graph E3 compares with S1: the real (or dry) end terminals + objects, the plan's last-step loops translated | docstring | - | 4847 |
| `e3_eval` | plan, S1, G, created, deleted | PD217(c) E3, pure: cdiff(S1, G) rows == the plan open rows of PD213(d) classes (1)-(3) (want derived from each row's | docstring | - | 4862 |
| `e3_created` | plan, ex | (created, deleted) for e3_eval: created = the real uids the binding holds for SIMULATED-created ids (sim ids < 0: | docstring | - | 4885 |
| `e3_check` | plan, ex, objs, real, wiki, tag='E3 end' | PD217(c) E3 on an executor's end (live or dry): builds the end graph (e3_graph), S1 (stagesim.load_s1), the created | docstring | - | 4895 |
| `e3_line` | r | One-line E3 verdict for a gate label/detail. | docstring | - | 4905 |
| `lv_run` | plan_path, reference=None, max_min=60 | LabVIEW run of a finalized plan: Stage on its base VI (pins, deadline max_min-3), scratch copy discarded, LVBackend + Executor.run, gates E1 (ops == steps), E2 (ExecState 1), E3 (end graph), E4 (op... | side file | - | 4913 |
| `canon_diff` | real_a, real_b, base_nodes | Two real reads compared up to new-uid naming: a node outside 'base_nodes' is its class. | docstring | - | 4967 |
| `selftest` |  | Offline self-test: builds a synthetic graph + plan in a temp dir, simulates it and runs the Executor / SimBackend gates T01.. and the from_step, create, c106c, c112, c127_4, c128 suites; prints gat... | side file | - | 5166 |
| `proposed_schema` | on=True | TEST / DIAGNOSTIC ONLY (card 100-3): the installed docs/protocol/stageplan.json has integer-only diagram fields, | docstring | - | 5883 |
| `main` | argv | CLI: selftest; adopt; dry <plan> [--from-step k --binding f] [--nonfinal] and prerun <plan> (RESULT line each); run <plan> [--reference vi md5] [--max-min n] (lv_run); else prints the module doc. R... | side file | - | 6274 |
| `case_pass_wire` | A, i, k, created, base_owners | card 156-a1-2 (PD379(b)): True when wire action k is the PASS WIRE of the case in-tunnel group that starts at tunnel | docstring | selftest_c156_passwire.py | 6305 |
| `loop_inner_face_sink` | rows, rs, rd, owners | card 165-1-1 (PD400(b)): the connect_term_uid act when the DST is the INNER face of a While / For LoopTunnel with wire 0 | docstring | selftest_c165_innerface.py | 6353 |
| `prime_deleted_face_skip` | A, ops, checkpoints, i, r, lo=0 | card 165-3-1 (docs/d1/ring-p5c.md PD402(b)): whether the Executor's base PRIME pass may leave plan action i's end 'r' | docstring | selftest_c165_prime.py | 6384 |

### tools/stop_record.py

shared module; imported by 31 file(s): `tools/bench/c19_close_release_probe.py`, `tools/bench/c20_release_probe.py`, `tools/bench/c22_v1_gate_probe.py`, `tools/bench/c58c_gatecheck.py`, `tools/bench/diag_c111c_realstore.py`, `tools/bench/diag_c111c_regress.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `exempt_program` | command_string | The path of the command-position program of this SEGMENT when it is one of EXEMPT_PROGRAMS, else ''. | docstring | - | 105 |
| `offline_checker` | segment | True when this SEGMENT runs tools/stage_prerun.py --dry/--prerun in command position (bgrun-wrapped or not). | docstring | - | 143 |
| `declared_offline` | prog_path, rest | card chat-E3 (fp-37): True when the command-position program is a tools/ script whose SCOPE HEADER makes THIS | docstring | - | 157 |
| `split_segments` | cmd | Shell segments split on && // ; / newline OUTSIDE quotes (so 'py -c "a;b" X' stays one segment). Falls back | docstring | - | 254 |
| `substitutions` | text | The inner commands of the OUTERMOST '$( ... )' in 'text' (balanced parentheses; an unclosed one runs to the | docstring | - | 304 |
| `binding_name` | seg | NAME when this segment is 'for NAME in ...' or a pure 'NAME=VALUE' (nothing runs after it), else ''. | docstring | - | 323 |
| `segment_class` | seg, whole_cmd='' | 'exempt' / 'readonly' / 'build' for one segment - the command-class axis of DECISION_TABLE. | docstring | - | 350 |
| `command_keys` | command_string, _taint=None, _depth=0 | {key: strictest command class} over every path token of the command. | docstring | - | 398 |
| `StoreError` | (class) | The record store exists in principle but cannot be trusted right now. | docstring | - | 431 |
| `keys_for` | path | The match keys for one path token or record path: ('rel', <project-relative, posix, lower>) and | docstring | - | 439 |
| `sha256_of` | path | card chat-E3: a .py/.ps1 is hashed WITHOUT its scope header block (tools/scope_header.canonical_bytes) - the | docstring | - | 468 |
| `load_records` |  | Every standing record. Raises StoreError when the store cannot be trusted - callers fail closed. | docstring | - | 512 |
| `save_records` | records | (undocumented) | - | - | 540 |
| `verdict_slugs` | record | (undocumented) | - | - | 555 |
| `write_stop_record` | recipe_path, review_file, verdict, root=None | Plant a stop record for 'recipe_path', keyed to the bytes the review saw. | docstring | - | 564 |
| `novel_in_answer` | body | True iff the review's ANSWER carries 'PRIOR-ART: novel' and NO blocking slug (guard_cycle's own regex and | docstring | - | 601 |
| `write_novel_record` | recipe_path, review_file | cycle 72 firefighter (2026-09-24): a 'novel' verdict over EDITED bytes used to leave NO record, so the older | docstring | - | 612 |
| `record_state` | records, i | (kind, state, line, why, cur_sha) of records[i] - the row key of DECISION_TABLE. 'line' is the release line | docstring | - | 698 |
| `check_command` | command_string | (allow, message). The launch gate. Fails CLOSED for commands naming 'tools/recipes/', and never wedges | docstring | - | 781 |

### tools/vigraph.py

shared module; imported by 172 file(s): `tools/addrcheck.py`, `tools/bench/c73_l7r_facts.py`, `tools/bench/c73_l7r_live.py`, `tools/bench/cdiff_blindspot_74.py`, `tools/bench/ct23541_facts_80.py`, `tools/bench/dedupe_check_s2b.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `node_of` | row | The GRAPH NODE a terminal row belongs to: its owner, except a front-panel terminal, which is its | docstring | - | 57 |
| `node_class` | row | Class of the graph node a terminal row belongs to: 'ControlTerminal' for a front-panel terminal row, else the row's owner_class. Returns str. | side file | - | 63 |
| `build` | terms, wires, objs=None | {adj, nodes, cls, method} - a directed node-uid graph. Pure; no LabVIEW, no mutation of the input. | docstring | - | 67 |
| `reach` | graph, starts | Every node uid reachable from 'starts' (node-level, forward). | docstring | - | 148 |
| `fp_terminals` | terms | The VI's own front-panel control/indicator terminals: leaf class 'ControlTerminal'. | docstring | - | 166 |
| `io_paths` | graph, terms, labels_in=None, labels_out=None | {output label: [input labels that can reach it]} over the front-panel terminals. | docstring | - | 178 |
| `key_parts` | key | Splits a terminal key 'node/class/name/ordinal' (name may contain '/') into (int node uid, class, name, int ordinal). Returns tuple. | side file | - | 248 |
| `show` | key | Readable form of a terminal key: '#<node> <class> <repr(name) or (unnamed)>' plus ' [<ordinal>]' when the ordinal is not 0. Returns str. | side file | - | 254 |
| `dedupe_rows` | terms | (rows, record): the terminal rows with a repeated 'term_uid' dropped, FIRST occurrence wins. | docstring | - | 260 |
| `build4` | terms, objs=None, loops=None, labels=None, fs_pairs=None, frame_keyed=False | The full terminal-level graph. 'terms' = OpAllTerms_v1 rows (the 7th column 'frame_diagram' is | docstring | - | 334 |
| `is_scheduling` | G, node | ASSUMPTION A. A node is SCHEDULING when its class is a tunnel / shift register / structure / | docstring | - | 632 |
| `transparent` | G, key | ASSUMPTION A, at TERMINAL level: is this terminal a scheduling RELAY to walk through? | docstring | - | 641 |
| `terminals` | G, node=None, name=None, term_uid=None, is_source=None, cls=None | Terminal KEYS matching the filter - the addressing helper the queries below take. | docstring | - | 653 |
| `wire_terminals` | G, wire_uid | Sorted terminal keys of graph G whose row sits on wire wire_uid. Returns list. | side file | - | 671 |
| `reach4` | G, starts, kinds=None | Every terminal key reachable DOWNSTREAM of 'starts' (terminal keys, or node uids). | docstring | - | 675 |
| `sources_of` | G, sink, kinds=None, collapse=False | Every terminal key UPSTREAM of 'sink'. 'collapse=True' returns only COMPUTATION terminals, | docstring | - | 692 |
| `path` | G, a, b, kinds=None | One shortest terminal path a -> b as a list of terminal keys, or [] if there is none. | docstring | - | 714 |
| `diff` | A, B, kinds=DIFF_KINDS | Edges added / removed / changed between two graphs, keyed by (owner uid, terminal name) and | docstring | - | 742 |
| `effective_sources` | G, key, memo=None | The COMPUTATION terminals whose value reaches 'key' through scheduling relays only. | docstring | - | 782 |
| `computation_diff_frame` | A, B | PD180(b): computation_diff over two FRAME-KEYED graphs (build4(..., frame_keyed=True)). Refuses a mix. | docstring | - | 840 |
| `pos_keys` | G | card 153-b2-1 (gate-fp fp-70, docs/d1/ring-p4d.md PD370(d)): {terminal key: POSITION KEY (node, index, term class, | docstring | - | 847 |
| `computation_diff` | A, B | ASSUMPTION A's rule-1a question: for every COMPUTATION node (subVI, primitive, constant, | docstring | - | 877 |

### tools/violations.py

shared module; imported by 2 file(s): `tools/bench/selftest_c156_b2_1_violations.py`, `tools/retro_due.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `threshold` | slug | (undocumented) | - | - | 79 |
| `decisions` |  | slug -> the date of its most recent decision block. A decision older than the retrospective that raised the | docstring | - | 125 |
| `is_comparison` | body | True if the archive's YAML frontmatter carries 'comparison: true'. | docstring | - | 152 |
| `scan` |  | (hits, loss) - slug -> the retrospectives that named it, and slug -> (loss_min, loss_usd, n_with_a_figure). | docstring | - | 166 |
| `main` |  | (undocumented) | - | - | 196 |

### tools/wiki_build.py

shared module; imported by 90 file(s): `tools/bench/build_kswap_88.py`, `tools/bench/c73_l7r_live.py`, `tools/bench/diag_c107b_bedgraph.py`, `tools/bench/diag_c108b_graph.py`, `tools/bench/diag_c108d_graph.py`, `tools/bench/diag_c108d_selind.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `subvi_rows` | target, diagram_index | 'gscript.subvis(strict=False)' returns (rows, err) - rows only, and an error on ONE diagram | docstring | - | 76 |
| `md5` | path | (undocumented) | - | - | 83 |
| `fact` | line | (undocumented) | - | - | 91 |
| `targets` |  | (undocumented) | - | - | 95 |
| `key_of` | path | The wiki key. NOT the bare file name: 'background VIs' carries the subfolder | docstring | - | 104 |
| `call_sites_index` |  | (undocumented) | - | - | 116 |
| `conpane_pass` | paths, chunk=12 | {path: [{index, label, direction, type}]} - drop each VI on a scratch EMPTY_v0 copy and read the | docstring | - | 127 |
| `read_fs_tunnels` | path, objs, uids=None | STEP 4b: every flat-sequence tunnel's two faces, READ from the machine, one op run per tunnel. | docstring | - | 202 |
| `read_live` | path, fs_pairs=None, fs_uids=None | STEP 5b: the graph INPUTS of a live (scratch) VI, without the wiki's subVI/conpane passes: the GObject | docstring | - | 233 |
| `read_one` | path, conpane, calls, main_vi | One VI -> the wiki record. Two op runs (GObject census, Terminal traverse) + one subvis per diagram. | docstring | - | 259 |
| `main` | argv=None | (undocumented) | - | - | 355 |

### tools/bench/bench_prep.py

shared file in the bench folder (move to tools/ later); imported by 299 file(s): `tools/bench/allterms_s4.py`, `tools/bench/allterms_v1_check.py`, `tools/bench/build_kswap_88.py`, `tools/bench/build_op_const_loopterm_77.py`, `tools/bench/build_op_termtype.py`, `tools/bench/build_opstopmode_v0.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `ps` | *args | (undocumented) | - | - | 26 |
| `com_alive` | timeout_s=40 | Alive = Application.Version answers AND a real VI Run (exec_state of the bench VI) returns | docstring | - | 34 |
| `labview_handles` |  | (undocumented) | - | - | 64 |
| `restart_labview` |  | (undocumented) | - | - | 74 |
| `main` |  | (undocumented) | - | - | 82 |

### tools/bench/build_opstopmode_v0.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/bench/build_opwiringrules_v0.py`, `tools/bench/diag_c138_6_run.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `Stop` | (class) | (undocumented) | - | - | 38 |
| `md5` | p | (undocumented) | - | - | 42 |
| `gate` | k, ok, d='', need=True | (undocumented) | - | - | 45 |
| `fact` | k, v | (undocumented) | - | - | 52 |
| `B` | (class) | (undocumented) | - | - | 55 |
| `B.purge` | s | (undocumented) | - | - | 63 |
| `B.idx` | s, cls, uid | (undocumented) | - | - | 71 |
| `B.terms` | s, uid | (undocumented) | - | - | 73 |
| `B.pn` | s, cls, props, pos | (undocumented) | - | - | 82 |
| `B.w` | s, su, st, du, dt, sc='Property', dc='Property', branch=False | (undocumented) | - | - | 85 |
| `B.panel` | s, ind | (undocumented) | - | - | 88 |
| `B.ind` | s, uid, term | (undocumented) | - | - | 90 |
| `B.ctl` | s, uid, term | (undocumented) | - | - | 96 |
| `B.data` | s, uid, src | (undocumented) | - | - | 102 |
| `B.node_with` | s, *names | (undocumented) | - | - | 105 |
| `finish` | b, key, lab, save=True | (undocumented) | - | - | 110 |
| `build_a` |  | (undocumented) | - | - | 119 |
| `build_b` |  | (undocumented) | - | - | 132 |
| `build_writer` | src_key, out, cls, pid, after | (undocumented) | - | - | 163 |
| `call` | path, la, target, idx, extra=None, tt=0 | (undocumented) | - | - | 176 |
| `rd` | key, target, idx, tt=0 | (undocumented) | - | - | 203 |
| `wr` | wpath, wkey, rkey, target, idx, value | A scratch writer = a copy of the reader + one write PN: its labels are the reader's plus Value/WErr. | docstring | - | 209 |
| `scratch_target` |  | (undocumented) | - | - | 215 |
| `main` |  | (undocumented) | - | - | 234 |

### tools/bench/build_ringpickslot_v2.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/build_ringseqcheck_v0.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `CMP` | o | (undocumented) | - | - | 21 |
| `ref` | num, last | (undocumented) | - | - | 22 |
| `peak` |  | (undocumented) | - | - | 23 |
| `kill` | tag | (undocumented) | - | - | 24 |
| `canon` | k | (undocumented) | - | - | 25 |
| `reg` | u, tag, want | (undocumented) | - | - | 26 |
| `tr` | R, k | (undocumented) | - | - | 29 |
| `Wr` | tag, snk, src | (undocumented) | - | - | 31 |
| `mk` | fn, u, name, src, tag | (undocumented) | - | - | 33 |
| `dele` | u, cls | (undocumented) | - | - | 39 |
| `build` |  | (undocumented) | - | - | 43 |
| `runs` | tag, idx | (undocumented) | - | - | 94 |
| `main` |  | (undocumented) | - | - | 102 |

### tools/bench/c131_2_reach.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/bench/c131_2_why.py`, `tools/bench/diag_c131_2_offline.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `script_touches_labview` | script, _seen=None | v2: True when the LAUNCHED 'script' can open LabVIEW (rules in the module docstring). Fails closed. | docstring | - | 154 |

### tools/bench/c60c_astcheck.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/bench/c74_gate10_report.py`, `tools/jev_preflight.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | name, ok, detail='' | (undocumented) | - | - | 98 |
| `defs_in` | path | (undocumented) | - | - | 105 |
| `allow_broken_sites` | tree | Every call that passes 'allow_broken' as anything other than literal 'False'. | docstring | - | 116 |
| `percent_format_sites` | tree, path | Every '<literal string> % <args>' site, classified. | docstring | - | 199 |
| `main` |  | (undocumented) | - | - | 276 |

### tools/bench/c90c_rows.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/bench/c90d_reads.py`, `tools/bench/diag_c90c_rowtable.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `tok` | s, R, t, text | (undocumented) | - | - | 19 |
| `t1_wires` | s, p, census, R | TASK 1: each of the 11 read WHOLE (n=8); the row dict prints VERBATIM, error columns included. | docstring | - | 24 |
| `t2_terms` | s, p, art, R | TASK 2: index -> (Terminal.Name, Terminal.Connected Wire, WIRED/BARE/UNREAD) for #48 and #10407. | docstring | - | 42 |
| `t3_owners` | s, p, R | TASK 3: 'Generic.Owner' 6327806 -> GObject UID on the four tunnels, plus each one's own class. | docstring | - | 63 |
| `controls` | s, p, art, census, pos, R | The two mandatory controls as VALUES: the negative uid must not echo; one intact wire must read. | docstring | - | 79 |
| `linemap` | R, logp | Each token's own line number in THIS run's log, so every cell of the table cites 'log:line'. | docstring | - | 98 |
| `cite` | n, m | Replace every 'src_tok' by its 'log:line'; a token the log never carried becomes 'unread'. | docstring | - | 113 |

### tools/bench/c90d_border.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_c90d_outstanding.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `borders` | s, p, art, R | MEASUREMENT 2 (BED) and 3 (CLEAN): the four old border objects - owner, every terminal's wire, and | docstring | - | 21 |
| `sr_terms` | s, p, art, uid, cls, R | A shift register's OWN terminals, found by walking 'Loop.Shift Registers[]' until the uid matches. | docstring | - | 48 |
| `lt_terms` | s, p, art, uid, R | A LoopTunnel's two faces: 'gscript.tunnels' (OpTunnels_v0), addressed by the LoopTunnel census index. | docstring | - | 98 |

### tools/bench/c90d_reads.py

shared file in the bench folder (move to tools/ later); imported by 3 file(s): `tools/bench/c90d_border.py`, `tools/bench/c90d_table.py`, `tools/bench/diag_c90d_outstanding.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `own` | s, R, art, p, uid, tag | 'Generic.Owner' 6327806 -> GObject UID, strict: a uid that does not echo yields 'unread' + its error. | docstring | - | 32 |
| `census` | s, p, art, cls | (undocumented) | - | - | 44 |
| `net` | s, p, art, w, R, tag | One CACHED 'Stage.net_sources' read (n=8) - every terminal row of the wire, error columns verbatim. | docstring | - | 52 |
| `srl` | s, p, art, li, ri, lfi, cls='WhileLoop' | (undocumented) | - | - | 74 |
| `m1` | s, p, R | MEASUREMENT 1: the four UNREAD wires on the BED, every terminal row, plus 'Generic.Owner' on every | docstring | - | 85 |

### tools/bench/c90d_table.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_c90d_outstanding.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `assemble` | s, R, src, outp, logp, inputs | (undocumented) | - | - | 18 |

### tools/bench/camera_contract.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/p1_bufmode_121.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `AttributeInformation` | (class) | (undocumented) | - | - | 49 |
| `enumerate_attributes` | sess, root='' | Every attribute under 'root', as (name, type_code, readable, writable). | docstring | - | 54 |
| `get_string` | sess, name | (undocumented) | - | - | 65 |
| `set_string` | sess, name, value | (undocumented) | - | - | 71 |
| `set_f64` | sess, name, value | (undocumented) | - | - | 75 |
| `read_value` | sess, name, tcode | Read an attribute whatever its type, returning a JSON-safe value. | docstring | - | 79 |
| `snapshot` | sess | The values a batch directory must record: geometry, rate, and the whole exposure group. | docstring | - | 94 |
| `main` |  | (undocumented) | - | - | 111 |

### tools/bench/d0_locate.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/drive_original_copy_v5.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `load` | png | (undocumented) | - | - | 55 |
| `red_mask` | a | (undocumented) | - | - | 65 |
| `clusters` | mask, gap=6 | Connected components of a boolean mask, over the True coordinates only (a few thousand). | docstring | - | 70 |
| `button_around` | a, cx, cy, maxd=90 | Walk out from (cx,cy) to the first dark neutral pixel on each side. (l,t,r,b) or None. | docstring | - | 106 |
| `face_is_light` | a, box, red, need=0.8 | (undocumented) | - | - | 125 |
| `locate_red_yes_button` | png, rect, wmin=15, wmax=60, hmin=8, hmax=32, maxd=90 | (best, candidates) - 'best' is the largest red caption that passed every test. | docstring | - | 142 |
| `template_score` | png, box, ref_png=REF_DONE | (undocumented) | - | - | 175 |
| `pick_by_template` | png, rect, ref_png=REF_DONE, max_score=12.0, ratio=0.5, caption_ref=(25, 12), caption_tol=4, **kw | The disambiguator.  Returns (winner_or_None, why, candidates). | docstring | - | 189 |
| `locate_image_display` | png, rect, minw=200, minh=150 | (undocumented) | - | - | 230 |
| `count_red_markers` | png, rect, wmin=8, wmax=45, hmin=8, hmax=45 | The bead markers the VI draws at each pick.  Used as the post-click READBACK for the picks. | docstring | - | 264 |
| `save_crop` | png, box, out, pad=16, scale=4 | (undocumented) | - | - | 277 |

### tools/bench/d1_rewire_map.py

shared file in the bench folder (move to tools/ later); imported by 9 file(s): `tools/recipes/build_d1_routeb_v0.py`, `tools/recipes/build_d1_routeb_v1.py`, `tools/recipes/build_d1_routeb_v2.py`, `tools/recipes/build_d1_routeb_v3.py`, `tools/recipes/build_d1_routeb_v4.py`, `tools/recipes/build_d1_routeb_v5.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `load` | name | (undocumented) | - | - | 75 |
| `build_map` | cut | The resolver, callable from a build: 'cut' = S3b's own [[uid, i, name, is_source, wire], ...] list. | docstring | - | 83 |
| `main` |  | (undocumented) | - | - | 90 |

### tools/bench/diag_c100_verbs_build.py

shared file in the bench folder (move to tools/ later); imported by 4 file(s): `tools/bench/diag_c124_opconnecttermuid.py`, `tools/bench/diag_c125_5_opfs.py`, `tools/bench/diag_c126_2_op.py`, `tools/bench/diag_c126_4_op.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `md5` | p | (undocumented) | - | - | 56 |
| `gate` | k, ok, d='' | (undocumented) | - | - | 59 |
| `fact` | k, v | (undocumented) | - | - | 63 |
| `B` | (class) | (undocumented) | - | - | 67 |
| `B.purge` | s | (undocumented) | - | - | 75 |
| `B.idx` | s, cls, uid | (undocumented) | - | - | 83 |
| `B.terms` | s, uid | (undocumented) | - | - | 85 |
| `B.pn` | s, cls, props, pos | (undocumented) | - | - | 94 |
| `B.w` | s, su, st, du, dt, sc='Property', dc='Property', branch=False | (undocumented) | - | - | 97 |
| `B.panel` | s, ind | (undocumented) | - | - | 100 |
| `B.ind` | s, uid, term | (undocumented) | - | - | 102 |
| `B.ctl` | s, uid, term | (undocumented) | - | - | 108 |
| `B.data` | s, uid, src | (undocumented) | - | - | 115 |
| `B.wired` | s, uid, name, src | (undocumented) | - | - | 118 |
| `B.finish` | s, key, lab | (undocumented) | - | - | 121 |
| `retarget` | b, key, cls, props, pos | diag_c97_tools_opbuild.retarget:104 verbatim in substance: delete the donor IndexMode PN, seed-retarget the TMSC. | docstring | - | 139 |
| `uid_echo` | b, tmsc, pos | (undocumented) | - | - | 163 |
| `build_nested` | key, method | (undocumented) | - | - | 169 |
| `prim_donor` |  | A BYTE COPY of the NI example (the original is only read); the Max & Min node FOUND by node label. | docstring | - | 200 |
| `build_primcopy` | reg | (undocumented) | - | - | 232 |
| `hands` |  | (undocumented) | - | - | 277 |
| `owner_chain` | t, uid, hops=4 | [(cls, uid), ...] from #uid up to the first Diagram, READ at every hop (OpOwnerChain_v1) - never a fallback. | docstring | - | 280 |
| `term_index` | t, uid, pred | RUN-2 FAULT FIXED (_build2.log:81-91): a border node (owner = a structure) is in no Diagram.Nodes[], so it is | docstring | - | 293 |
| `block` | name, fn | (undocumented) | - | - | 306 |
| `v1` | T | (undocumented) | - | - | 313 |
| `v1b` | T | (undocumented) | - | - | 323 |
| `v3` | T, newrow | (undocumented) | - | - | 364 |
| `v2` | T | (undocumented) | - | - | 382 |
| `v5` | T, dest | gscript.create_local_write = the core stagekit.create_local_write binds to (stagekit.py:685-697 adds only the | docstring | - | 425 |
| `v6` | T | (undocumented) | - | - | 452 |
| `selftest` |  | (undocumented) | - | - | 477 |
| `main` |  | (undocumented) | - | - | 510 |

### tools/bench/diag_c108c_graph.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_c108c_groupB.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `Graph` | (class) | (undocumented) | - | - | 18 |
| `Graph.cite` | term_uid | (undocumented) | - | - | 60 |
| `Graph.node` | t | (undocumented) | - | - | 65 |
| `Graph.ncls` | n | (undocumented) | - | - | 68 |
| `Graph.struct_of_tunnel` | u | (undocumented) | - | - | 71 |
| `Graph.diag` | n | (undocumented) | - | - | 79 |
| `Graph.chain` | n | structures enclosing node n, inner -> outer. | docstring | - | 84 |
| `Graph.loop` | n | (undocumented) | - | - | 94 |
| `Graph.label` | n | (undocumented) | - | - | 100 |
| `Graph.is_motor` | n | (undocumented) | - | - | 107 |
| `Graph.through_down` | t | sink terminal t of a carrier -> source terminals to continue from ([] = not a carrier). | docstring | - | 110 |
| `Graph.through_up` | t | source terminal t of a carrier -> sink terminals to continue from. | docstring | - | 127 |
| `Graph.walk` | start, down, stop | first non-carrier ends from terminal 'start'; 'stop(node)' True = end there (e.g. group-B member). | docstring | - | 145 |

### tools/bench/diag_c115d_sel.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_c115d_sel2.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `pane` | p | (undocumented) | - | - | 23 |
| `shift` | a, b | (dy, dx, peak): b[y, x] ~ a[y + dy, x + dx]. | docstring | - | 27 |
| `overlap` | a, b, dy, dx | views of a and b on their common area, both in b's frame: returns (a_part, b_part, (y0, y1, x0, x1) in b). | docstring | - | 37 |
| `changed` | a, b, dy, dx | (undocumented) | - | - | 46 |
| `main` |  | (undocumented) | - | - | 58 |

### tools/bench/diag_c118_p0.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/bench/diag_c118_p1.py`, `tools/recipes/stage_d1_qrt_pool.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `u8` | v | (undocumented) | - | - | 25 |
| `read_str` | t, uid | (undocumented) | - | - | 32 |
| `read_num` | t, uid | (undocumented) | - | - | 44 |
| `body` | _ | (undocumented) | - | - | 64 |
| `probe` | T | (undocumented) | - | - | 90 |

### tools/bench/diag_c138_6_run.py

shared file in the bench folder (move to tools/ later); imported by 6 file(s): `tools/bench/build_ringpickslot_v0.py`, `tools/bench/build_ringpickslot_v1.py`, `tools/bench/build_ringpickslot_v2.py`, `tools/bench/diag_c139_1_run.py`, `tools/bench/diag_c139_3_run.py`, `tools/bench/diag_c140_5_run.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `ldump` |  | (undocumented) | - | - | 34 |
| `rows` | t | (undocumented) | - | - | 35 |
| `one` | rs, **kw | (undocumented) | - | - | 36 |
| `el_count` | W, tag | (undocumented) | - | - | 39 |
| `step0` |  | (undocumented) | - | - | 45 |
| `step1` |  | (undocumented) | - | - | 51 |
| `step3` |  | (undocumented) | - | - | 61 |
| `step4` |  | (undocumented) | - | - | 69 |
| `cp` | dg, prim, pos, donor | (undocumented) | - | - | 91 |
| `step2` |  | (undocumented) | - | - | 93 |
| `main` |  | (undocumented) | - | - | 139 |

### tools/bench/diag_c153_b2_1_rescore.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_c153_b2_1_s06pos.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | label, ok, detail='' | (undocumented) | - | - | 32 |
| `old_vigraph` |  | (undocumented) | - | - | 39 |
| `score` | tag, VO, S1f, G1, stored=None | (undocumented) | - | - | 46 |
| `main` |  | (undocumented) | - | - | 66 |

### tools/bench/diag_c156_b2_2_inv_c156a21.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/selftest_c156_b2_2_invcheck.py`

(no public function)

### tools/bench/diag_c159_f1_2_t2.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_c160_f1_1_bisect.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `md5b` | b | (undocumented) | - | - | 37 |
| `src_bytes` | spec, name | (undocumented) | - | - | 41 |
| `Serve` | (class) | (undocumented) | - | - | 48 |
| `Serve.find_spec` | name, path=None, target=None | (undocumented) | - | - | 52 |
| `Serve.create_module` | spec | (undocumented) | - | - | 57 |
| `Serve.exec_module` | module | (undocumented) | - | - | 60 |
| `child` | cfg_i | (undocumented) | - | - | 66 |
| `main` |  | (undocumented) | - | - | 87 |

### tools/bench/diag_c61_localdir_write2.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/q_m4_iterlocal.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `Stop` | (class) | (undocumented) | - | - | 145 |
| `gate` | name, ok, detail='', fatal=False | (undocumented) | - | - | 149 |
| `fact` | line | (undocumented) | - | - | 158 |
| `probe` | tag, path | (undocumented) | - | - | 163 |
| `dump` |  | (undocumented) | - | - | 170 |
| `read_exec_state` | rec, tag, target | ONE global ordered timeline, so 'the ExecState after every single step' is a single list. | docstring | - | 178 |
| `count_of` | target, cls | (undocumented) | - | - | 193 |
| `uid_set` | target, cls | (undocumented) | - | - | 200 |
| `close_quietly` | target | (undocumented) | - | - | 207 |
| `node_label_rows` | target, di, fresh=False | (undocumented) | - | - | 217 |
| `locate` | target, uid, fresh=False | uid -> owner / diagram index / candidate node index, ALL read off the machine. Owner comparisons accept | docstring | - | 229 |
| `terms_of_uid` | target, loc | node_terms on the located node, VERIFIED by the node's own UID; bounded scan fallback. | docstring | - | 261 |
| `term_rows_verbatim` | terms | (undocumented) | - | - | 302 |
| `find_create_local_invoke` | target, di | Six terminals whose (4,5) are both named 'Create Local'. Returns (node_index, node_uid, rows). | docstring | - | 309 |
| `find_property_node` | target, di, direction_name | The node carrying BOTH a terminal named 'reference' and one named <direction_name> (e.g. 'Write?'). | docstring | - | 324 |
| `one_probe` | K, target, cls, pid, is_write, pos, tag | Create ONE property node for (cls, pid, is_write) and read EVERYTHING off it. (Dispatch #2's helper, | docstring | - | 339 |
| `build_and_save` |  | (undocumented) | - | - | 388 |
| `st6_cold_reopen` |  | (undocumented) | - | - | 571 |
| `call_new_op` | target, fp_index, write_flag, bool_label, tag | (undocumented) | - | - | 591 |
| `s4_readback` | bool_label | (undocumented) | - | - | 646 |
| `hygiene` | fp_index, bool_label | (undocumented) | - | - | 717 |
| `st7_ordered_pass` | direction_name, saved_md5 | (undocumented) | - | - | 758 |
| `main` |  | (undocumented) | - | - | 851 |

### tools/bench/diag_c81_uidref.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_c86_norbw.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | name, ok, detail='' | (undocumented) | - | - | 119 |
| `fact` | line | (undocumented) | - | - | 126 |
| `head` | t | (undocumented) | - | - | 131 |
| `safe` | label, fn, default=None | (undocumented) | - | - | 135 |
| `md5` | path | (undocumented) | - | - | 144 |
| `dump` |  | (undocumented) | - | - | 153 |
| `left_s` |  | (undocumented) | - | - | 161 |
| `phase_0` |  | (undocumented) | - | - | 166 |
| `phase_1` |  | (undocumented) | - | - | 184 |
| `phase_v` |  | (undocumented) | - | - | 212 |
| `phase_a` |  | (undocumented) | - | - | 249 |
| `phase_b` |  | (undocumented) | - | - | 288 |
| `probe_ownerchain` | vi, lab, target, uid, quiet=False | OpOwnerChain_v1 = UID to GObject Reference.vi -> [self Class Name / self UID] + Generic.Owner -> | docstring | - | 366 |
| `probe_fsit` | vi, lab, target, uid | OpFsInnerTunnelTerm_v0 = the SAME UID to GObject Reference.vi, then a TMSC seeded | docstring | - | 415 |
| `phase_p` |  | (undocumented) | - | - | 438 |
| `phase_s` |  | (undocumented) | - | - | 514 |
| `phase_hygiene` |  | (undocumented) | - | - | 534 |
| `main` |  | (undocumented) | - | - | 586 |

### tools/bench/diag_c83_connect2x2.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/bench/diag_c83_connect2x2_r2.py`, `tools/recipes/build_d1_m3a3b_d3.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | name, ok, detail='', fatal=False | (undocumented) | - | - | 141 |
| `fact` | line | (undocumented) | - | - | 150 |
| `head` | t | (undocumented) | - | - | 155 |
| `safe` | label, fn, default=None | (undocumented) | - | - | 159 |
| `dump` |  | (undocumented) | - | - | 168 |
| `left_s` |  | (undocumented) | - | - | 176 |
| `invoke_node` | target | (Nodes[] index, uid, terminal rows) of the single 'Invoke Node' on diagram 0. | docstring | - | 180 |
| `ind_labels` | target | (undocumented) | - | - | 189 |
| `ctl_labels` | target | (undocumented) | - | - | 193 |
| `attach_error_indicator` | target, tag | STEP 0's repair, and the same repair on the scratch connect op: walk the Invoke's 'error out' chain | docstring | - | 197 |
| `attach_auto_route` | target, tag | A front-panel control on the Invoke's 'Auto Route?' terminal. Returns (label or '', note). | docstring | - | 249 |
| `fsit_call` | op_path, labels, target, fsit_uid, sink_diag, sink_node, sink_term, ar_label='', auto_route=None, inv_err_label='', c... | 'C82.fsit_connect' PARAMETERISED BY OP PATH (that function hard-wires the module global 'OP'). | docstring | - | 267 |
| `conn_call` | op_path, target, inv_node, inv_term, ws_node, ws_term, ar_label='', auto_route=None, inv_err_label='' | 'gscript.connect_terminals':2518 driven through an explicit op path - (index, index 2) is the | docstring | - | 330 |
| `phase_files` |  | (undocumented) | - | - | 368 |
| `phase_restart` |  | (undocumented) | - | - | 399 |
| `step0` |  | (undocumented) | - | - | 414 |
| `make_ar_connect` |  | (undocumented) | - | - | 456 |
| `make_ar_fsit` |  | (undocumented) | - | - | 483 |
| `make_swapped` |  | (undocumented) | - | - | 500 |
| `make_trivial` | cell | A FRESH trivial VI: two bare 'VI Server:GObject' Property nodes. SOURCE = A.'reference out', | docstring | - | 554 |
| `read_pair` | target, a, b | The two terminals' own wire uids, re-read off the machine. | docstring | - | 582 |
| `step1` | ar_label, err_label, ar_ok | (undocumented) | - | - | 593 |
| `step2` | labels, err_label, arf_label, arf_ok, swap_label, swap_ok | (undocumented) | - | - | 653 |
| `phase_hygiene` |  | (undocumented) | - | - | 753 |
| `summary` |  | (undocumented) | - | - | 812 |
| `main` |  | (undocumented) | - | - | 837 |

### tools/bench/diag_c83_connect2x2_r2.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_c83_connect2x2_kit.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | name, ok, detail='', fatal=False | (undocumented) | - | - | 130 |
| `fact` | line | (undocumented) | - | - | 139 |
| `head` | t | (undocumented) | - | - | 144 |
| `safe` | label, fn, default=None | (undocumented) | - | - | 148 |
| `dump` |  | (undocumented) | - | - | 157 |
| `left_s` |  | (undocumented) | - | - | 165 |
| `fsit_call2` | op_path, labels, target, fsit_uid, sink_diag, sink_node, sink_term, ar_label='', auto_route=None, inv_err_label='', p... | 'diag_c83_connect2x2.fsit_call' with the POISON PASS made optional - the review | docstring | - | 169 |
| `phase_files` |  | (undocumented) | - | - | 234 |
| `phase_restart` |  | (undocumented) | - | - | 254 |
| `step0_raw_error` |  | (undocumented) | - | - | 268 |
| `make_arf` |  | (undocumented) | - | - | 323 |
| `make_swap` |  | (undocumented) | - | - | 340 |
| `run_cells` | labels, arf_label, arf_ok, swap_label, swap_ok | (undocumented) | - | - | 417 |
| `phase_hygiene` |  | (undocumented) | - | - | 523 |
| `summary` |  | (undocumented) | - | - | 576 |
| `main` |  | (undocumented) | - | - | 602 |

### tools/bench/diag_c91_step4_stats.py

shared file in the bench folder (move to tools/ later); imported by 6 file(s): `tools/bench/diag_c91_step4.py`, `tools/bench/diag_c92c_abba.py`, `tools/bench/diag_c93b_abba.py`, `tools/bench/diag_c93b_flushalign.py`, `tools/bench/diag_c94_abba.py`, `tools/bench/f7911_facts_94_offline.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `load` | d | (undocumented) | - | - | 13 |
| `pct` | a, q | (undocumented) | - | - | 21 |
| `bucket` | i_ticks, s_ticks | for each stamp in s_ticks: (iteration k, delta ticks); stamps before the first i stamp are dropped. | docstring | - | 27 |
| `table` | d | (undocumented) | - | - | 37 |

### tools/bench/diag_c94_sites.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_c94_abba.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `meta_overflow` | sm | (undocumented) | - | - | 13 |
| `mean` | a | (undocumented) | - | - | 22 |
| `summarize` | raw | (undocumented) | - | - | 27 |

### tools/bench/diag_d1_execstate_preload.py

shared file in the bench folder (move to tools/ later); imported by 7 file(s): `tools/bench/c52_astcheck.py`, `tools/bench/diag_s2_scaffold.py`, `tools/bench/verify_d1_s2.py`, `tools/recipes/stage_d1_s1.py`, `tools/recipes/stage_d1_s2.py`, `tools/recipes/stage_d1_s2_loops.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | label, ok, detail='' | (undocumented) | - | - | 68 |
| `fact` | s | (undocumented) | - | - | 75 |
| `md5` | p | (undocumented) | - | - | 79 |
| `llb_root` | path | Nearest ancestor path component of 'path' whose name ends in .llb, or None. | docstring | - | 91 |
| `path_status` | path | OK (on disk) / IN-LLB (member of an existing .llb container) / MISSING / EMPTY. | docstring | - | 103 |
| `child` | tag, target, preload | (undocumented) | - | - | 116 |
| `run_condition` | tag, target, preload | (undocumented) | - | - | 192 |
| `main` |  | (undocumented) | - | - | 219 |

### tools/bench/diag_donor_census.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/c52r3_astcheck.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `Stop` | (class) | (undocumented) | - | - | 125 |
| `gate` | name, ok, detail='', fatal=True | (undocumented) | - | - | 129 |
| `fact` | line | (undocumented) | - | - | 139 |
| `probe` | tag, path | (undocumented) | - | - | 144 |
| `dump` |  | (undocumented) | - | - | 151 |
| `census` | tag, target | (undocumented) | - | - | 158 |
| `main` |  | (undocumented) | - | - | 165 |

### tools/bench/diag_fstunnel_preclean_twins.py

shared file in the bench folder (move to tools/ later); imported by 3 file(s): `tools/bench/diag_fstunnel_orphan_timeline.py`, `tools/bench/diag_fstunnel_wireterms_panel.py`, `tools/bench/diag_fstunnelterm_v2_panelcost.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `must` | label, ok, detail='' | (undocumented) | - | - | 114 |
| `note` | label, value | (undocumented) | - | - | 120 |
| `md5` | p | (undocumented) | - | - | 124 |
| `snapshot` | tag | (undocumented) | - | - | 135 |
| `handles` | tag | (undocumented) | - | - | 143 |
| `nterms` | by | (undocumented) | - | - | 157 |
| `orphan_wires` | target, by | (orphan uids, whole Wire census). COPIED from build_opfstunnelterm_v2.py:465-470 - a wire is an ORPHAN when | docstring | - | 161 |
| `rbw_at` | target, where | The ONLY route to remove_bad_wires_scripted in this file. Refuses unless a twin has frozen at B4 (P6). | docstring | - | 169 |
| `rbw_call_sites` |  | (undocumented) | - | - | 191 |
| `StopAtB4` | (class) | (undocumented) | - | - | 203 |
| `do_preclean` | target | Remove the donor copy's OWN orphan wires - and nothing else - with delete_object, never with RBW. | docstring | - | 219 |
| `build_to_b4` | kind, path, preclean=False | (undocumented) | - | - | 274 |
| `site_table` | tag | The six wire_checked records as '_v1' itself recorded them, per site. | docstring | - | 299 |
| `census_at` | target, tag | (undocumented) | - | - | 312 |
| `main` |  | (undocumented) | - | - | 321 |

### tools/bench/diag_fstunnel_rbwvictims.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_fstunnel_wireterms_panel.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `must` | label, ok, detail='' | (undocumented) | - | - | 103 |
| `note` | label, value | (undocumented) | - | - | 109 |
| `md5` | p | (undocumented) | - | - | 113 |
| `snapshot` | tag | (undocumented) | - | - | 124 |
| `handles` | tag | (undocumented) | - | - | 132 |
| `StopAtB4` | (class) | (undocumented) | - | - | 148 |
| `build_to_b4` | kind, path, census=False | (undocumented) | - | - | 184 |
| `check_repro` | tag, path | (undocumented) | - | - | 206 |
| `wire_source_owner` | target, wire_uid, n=8 | COPIED from diag_fstunnel_wirebroken.py:186-208 (itself build_opconnectfromwire_v0.py:423-447). READ-ONLY. | docstring | - | 223 |
| `connect_from_wire` | target, wire_uid, term_index, sink_diag, sink_node, sink_term, labels | COPIED from diag_fstunnel_wirebroken.py:211-248, unchanged. | docstring | - | 248 |
| `term_index_of` | target, node_uid, term_name, want_source=False | (undocumented) | - | - | 288 |
| `read_broken` | target, wire_uid, sinks, labels | COPIED from diag_fstunnel_wirebroken.py:260-288. 'Wire.Is Broken?' 6371004 on ONE wire through | docstring | - | 297 |
| `uid_classes` | target | {uid: [class, ...]} from report_all per candidate class - the most specific class is the non-'Node' one. | docstring | - | 323 |
| `term_map` | target | {(node_uid, term_name, term_index): wire_uid} for every terminal of every diagram-0 node, from the | docstring | - | 335 |
| `ends_of` | tmap, wire_uid | (undocumented) | - | - | 347 |
| `role_of` | uid | (undocumented) | - | - | 354 |
| `describe_wire` | target, wire_uid, tmap, idx, ucls, tag | (undocumented) | - | - | 358 |
| `grep_tokens` | tokens | (undocumented) | - | - | 383 |
| `main` |  | (undocumented) | - | - | 407 |

### tools/bench/diag_movein_p1_break.py

shared file in the bench folder (move to tools/ later); imported by 3 file(s): `tools/bench/c52r3_astcheck.py`, `tools/bench/diag_donor_census.py`, `tools/bench/diag_movein_set.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | name, ok, detail='' | (undocumented) | - | - | 71 |
| `fact` | line | (undocumented) | - | - | 78 |
| `read_term` | vi, labels, target, wire_uid, idx | build_opwiresource_v5.read_terminal() with ONE change: 'vi path' is a parameter, not the main VI | docstring | - | 83 |
| `main` |  | (undocumented) | - | - | 115 |

### tools/bench/diag_movein_set.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/c52r3_astcheck.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `Stop` | (class) | (undocumented) | - | - | 113 |
| `gate` | name, ok, detail='', fatal=True | (undocumented) | - | - | 117 |
| `fact` | line | (undocumented) | - | - | 127 |
| `probe` | tag, path | (undocumented) | - | - | 132 |
| `dump` |  | (undocumented) | - | - | 139 |
| `terms_by_uid` | tag, target, uid | Terminal-by-terminal reading of ONE node, addressed by uid and re-resolved at the call site (34(h)): | docstring | - | 146 |
| `wire_side` | tag, target, wire_uid, ws_vi, ws_labels | The WIRE's own Terms[] (OpWireSource_v5): per terminal Is Source?, reciprocal wire, owner class/uid. | docstring | - | 183 |
| `census` | tag, target | (undocumented) | - | - | 199 |
| `wire_present` | target, wire_uid | (undocumented) | - | - | 206 |
| `main` |  | (undocumented) | - | - | 210 |

### tools/bench/diag_queue_donor.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/c52_astcheck.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `Stop` | (class) | (undocumented) | - | - | 144 |
| `gate` | name, ok, detail='', fatal=False | (undocumented) | - | - | 148 |
| `fact` | line | (undocumented) | - | - | 158 |
| `probe` | tag, path | (undocumented) | - | - | 163 |
| `dump` |  | (undocumented) | - | - | 170 |
| `labels_of` | target, diagram_index | (undocumented) | - | - | 177 |
| `attempt` | shape, target, src_cls, src_index, src_name, d686, why, extra=None | ONE 'queue_node('obtain')' attempt. Records the verbatim op error, the new Function uids and the labels | docstring | - | 185 |
| `main` |  | (undocumented) | - | - | 211 |

### tools/bench/diag_queue_donor2.py

shared file in the bench folder (move to tools/ later); imported by 3 file(s): `tools/bench/c52r2_astcheck.py`, `tools/bench/diag_qdonor2_ia.py`, `tools/bench/diag_qdonor2_stage.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `Stop` | (class) | (undocumented) | - | - | 149 |
| `gate` | name, ok, detail='', fatal=False | (undocumented) | - | - | 153 |
| `fact` | line | (undocumented) | - | - | 163 |
| `probe` | tag, path | (undocumented) | - | - | 168 |
| `dump` |  | (undocumented) | - | - | 175 |
| `safe` | fn, *a, **kw | Run a measurement call and return (value, error-string) - a refusal is a reading, never a crash. | docstring | - | 182 |
| `owner` | target, uid | (undocumented) | - | - | 190 |
| `walk_rows` | target, diagram_index, limit=200 | [{uid, node_index, label, class_guess, in_bare, out_named}] for one diagram - the BUILT census. | docstring | - | 195 |
| `const_on_term` | target, cls_name, cls_idx, node_i, term_i, labels, value=None | 'build_opcreateconstonterm_v0.create_const_on_term' VERBATIM except that the container CLASS is an argument | docstring | - | 211 |
| `q_attempt` | shape, target, src_cls, src_index, src_name, d686, why, extra=None | (undocumented) | - | - | 247 |
| `wire_driver` | target, wire_uid, max_terms=6 | Every terminal of one wire through OpWireSource_v5 (UID-addressed), returning the SOURCE rows. | docstring | - | 265 |
| `dependency_of_node` | target, diagram_index, uid, label | Every INPUT wire of one node, traced to its driving object's owner - 35(a)'s actual property. | docstring | - | 286 |
| `main` |  | (undocumented) | - | - | 327 |

### tools/bench/diag_replay_gbtest.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_replay_test77.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `harness` | s, tag, vut | (undocumented) | - | - | 24 |
| `call` | s, H, lab, tag, b=None | (undocumented) | - | - | 45 |
| `body` | s | (undocumented) | - | - | 63 |
| `St` | (class) | (undocumented) | - | - | 92 |
| `St.close` | expect_files=None | (undocumented) | - | - | 93 |
| `St.summary` |  | (undocumented) | - | - | 96 |

### tools/bench/diag_replay_lib.py

shared file in the bench folder (move to tools/ later); imported by 9 file(s): `tools/bench/diag_c110f_dispgraph.py`, `tools/bench/diag_replay_defaults.py`, `tools/bench/diag_replay_gbtest.py`, `tools/bench/diag_replay_graph77.py`, `tools/bench/diag_replay_standins.py`, `tools/bench/diag_replay_test77.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `new1` | t, cls, before | the ONE uid of class 'cls' on 't' that is not in 'before' (raises on 0 or >1; DRY: 0) | docstring | - | 41 |
| `new_label` | t, before, indicator | Label of the last front-panel object of t (g.fp_labels order) whose indicator flag equals indicator and whose label is not in before; RuntimeError when none ('' in DRY). Returns str. | side file | - | 51 |
| `copy_to` | s, cls, uid, dest_diag_uid, pos, tag | copy_top + (dest_diag_uid) move_in into that diagram + junk purge = stagekit.copy_in:779 with DRY-safe lookups | docstring | - | 60 |
| `pins` |  | The pinned inputs as (name, path, md5): IMAQdx Get Image, the IMAQdx lvlib, get-buff copy and original, frames manifest (md5 read now), pane base and S1 (fixed md5 constants). Returns tuple of tuples. | side file | - | 69 |
| `walk` | t, d=0 | Node table of diagram d of VI t: {uid: (index n, label, terminal rows)} from g.node_terms_uid for n = 0..79 until a 0 uid; a missing key raises KeyError, or gives (0, '', []) in DRY. Returns _Walk ... | side file | - | 75 |
| `term` | rows, name, source | First terminal row of rows with that name and is_source == source; None when absent (a copy of DUMMY in DRY). Returns dict or None. | side file | - | 86 |
| `tname` | rows, pred, source | the one terminal name satisfying pred(name) with the given direction (raises on 0 or >1) | docstring | - | 90 |
| `fidx` | t, cls, uid | Index of uid among the uids of g.report_all(t, cls) (ValueError when absent; 0 in DRY). Returns int. | side file | - | 106 |
| `diag_index` | t, uid | Index of diagram uid among g.report_all(t, 'Diagram') (ValueError when absent; 0 in DRY). Returns int. | side file | - | 110 |
| `donor_class` | uid | 'Function' or 'Node': the first of those classes whose report_all on g.MOVE_SRC holds uid; None when neither; always 'Function' in DRY. Returns str or None. | side file | - | 114 |
| `copy_top` | s, cls, uid, tag | stagekit.copy_in:779 minus move_in: OpMoveByIndex_v0 duplicate=True with the UID guard; the copy stays top level. | docstring | - | 123 |
| `str_array_ctl` | s, t, tag | Makes a free String[] control on t: drops Get Controls.vi, creates a control on its 'Control Names' input, deletes that wire and the subVI, removes bad wires; fatal gate that the control has no wir... | side file | - | 137 |
| `pwire` | t, label | the wire uid on panel object 'label' (panel_wiring; raises if absent; DRY: 0) | docstring | - | 149 |
| `pidx` | t, label | Index of label among the front-panel labels of t (g.fp_labels order; ValueError when absent, 0 in DRY). Returns int. | side file | - | 159 |
| `pane_dirs` | t | {slot: (label, is_indicator)} over the connector pane (label + direction; K3 of 76-4) | docstring | - | 163 |
| `edges` | live, remap | Edge set of a live graph read: (source owner, source terminal name, sink owner, sink terminal name) for every source/sink pair on one wire, owners mapped through remap. Returns set of tuples. | side file | - | 169 |
| `census` | t | {subVI uid: path} over every diagram of t (g.subvis per diagram index). Returns dict. | side file | - | 179 |
| `tail` | s, fxl=None, bad=() | once per run, just before the RESULT line: Moving-Objects pair restored and proven (stagekit.fixtures_check), | docstring | - | 187 |
| `frame_paths` |  | The N_FR (10044) replay frame paths f00000.tif, f00001.tif, ... under FR (G:\m8_replay_frames), in index order. Returns list of str. | side file | - | 206 |

### tools/bench/diag_s2_scaffold.py

shared file in the bench folder (move to tools/ later); imported by 75 file(s): `tools/bench/c52r3_astcheck.py`, `tools/bench/c53_astcheck.py`, `tools/bench/diag_c60_castseed_probe.py`, `tools/bench/diag_c60_n4_localbinding.py`, `tools/bench/diag_c61_localdir.py`, `tools/bench/diag_c61_localdir_write.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `Stop` | (class) | (undocumented) | - | - | 109 |
| `gate` | name, ok, detail='', fatal=True | (undocumented) | - | - | 113 |
| `fact` | line | (undocumented) | - | - | 123 |
| `md5` | p | (undocumented) | - | - | 128 |
| `version_bytes` | path | (undocumented) | - | - | 136 |
| `file_facts` | tag, path | (undocumented) | - | - | 143 |
| `fresh` | tag | A FRESH LabVIEW instance (standing restart authority) — stage_d1_s2.py:575-586. | docstring | - | 156 |
| `Preload` | (class) | stage_d1_s2.py:589-613 verbatim: the ORIGINAL resident READ-ONLY for the duration of a phase. No panel on | docstring | - | 168 |
| `dump` |  | (undocumented) | - | - | 192 |
| `census_686` | target | Every node of Diagram #686 with its OUTPUT terminal names — 'walk' is the BUILT census. | docstring | - | 199 |
| `candidates_from` | rows, target | Scalar-shaped named SOURCE terminals, PREFERRED first, then census order (the brief pre-decides this). | docstring | - | 219 |
| `try_candidate` | c, target, loop_uid, body_uid, d686 | ONE attempt: OpCreateEqual_v0 (both operands = this ONE terminal) then OpStopFromNode_v0. | docstring | - | 261 |
| `read_state` | tag, target | (undocumented) | - | - | 344 |
| `try_save` | tag, target | (undocumented) | - | - | 352 |
| `main` |  | (undocumented) | - | - | 367 |

### tools/bench/diag_s3b_l0_localname_v2.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/diag_c147_b1_4_run.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `Stop` | (class) | (undocumented) | - | - | 252 |
| `gate` | name, ok, detail='', fatal=False | (undocumented) | - | - | 256 |
| `fact` | line | (undocumented) | - | - | 265 |
| `probe` | tag, path | (undocumented) | - | - | 270 |
| `dump` |  | (undocumented) | - | - | 277 |
| `read_exec_state` | rec, tag, target | (undocumented) | - | - | 285 |
| `count_of` | target, cls | (undocumented) | - | - | 295 |
| `uid_set` | target, cls | (undocumented) | - | - | 302 |
| `report_uids` | target, cls | report_all order (the order every delete_object index in this fleet is resolved against). | docstring | - | 309 |
| `terms_table` | rows | (undocumented) | - | - | 317 |
| `node_index_of` | target, diagram_index, uid | The 34(h)-safe Nodes[] index: bounded scan with a uid echo. Returns (index, rows). | docstring | - | 322 |
| `terms_of` | target, diagram_index, uid | (undocumented) | - | - | 336 |
| `full_node_dump` | target, diagram_index, tag, max_nodes=SCAN_LIMIT, quiet=False | Every node on one diagram with its FULL terminal table, read off the machine. Read-only. | docstring | - | 341 |
| `owner_read` | rec, tag, uid, target | Owner of 'uid', accepting BOTH 'Diagram' and 'TopLevelDiagram' wherever it is compared. | docstring | - | 368 |
| `close_quietly` | target | (undocumented) | - | - | 392 |
| `fp_pairs` | target, max_n=200 | (undocumented) | - | - | 399 |
| `delete_wire_by_uid` | rec, tag, target, wire_uid | The ONLY form there is: resolve the uid to its report_all index, delete, and assert the gone-set. | docstring | - | 407 |
| `phase_s1` |  | Read-only on the freshly made copy. NOTHING is edited in this phase. | docstring | - | 439 |
| `phase_s2` | S | (undocumented) | - | - | 582 |
| `local_name` | target, index, tag='' | The READER's Python side: Traverse 'Local' by 'index' on 'target' -> Local.Control Name 6355400. | docstring | - | 928 |
| `create_local` | target, label, panel_index, tag='' | material #1's wrapper (tools/bench/diag_s3b_l0_localname.py:695-743), unchanged in substance: drive | docstring | - | 964 |
| `phase_s345` |  | (undocumented) | - | - | 1016 |
| `main` |  | (undocumented) | - | - | 1213 |

### tools/bench/diag_tunnelsource_onehop.py

shared file in the bench folder (move to tools/ later); imported by 5 file(s): `tools/bench/diag_d0_trace_path.py`, `tools/bench/diag_fstunnel_wire_semantics.py`, `tools/recipes/build_opfstunnelterm_v0.py`, `tools/recipes/build_opfstunnelterm_v1.py`, `tools/recipes/build_opfstunnelterm_v2.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | name, ok, detail='' | (undocumented) | - | - | 70 |
| `fact` | line | (undocumented) | - | - | 77 |
| `md5` | p | (undocumented) | - | - | 82 |
| `labels` |  | (undocumented) | - | - | 94 |
| `read_terminal` | target, wire_uid, idx | One terminal of one wire: (is_source, owner class, owner uid, reciprocal wire). Poison every readout | docstring | - | 102 |
| `wire_terminals` | target, wire_uid, maxn=8 | Every terminal on 'wire_uid', stopping at the end of Wire.Terminals[]. | docstring | - | 139 |
| `wire_source` | target, wire_uid | The ONE terminal on 'wire_uid' that is a source and points back at it; None when there is not exactly one. | docstring | - | 153 |
| `offline` |  | (undocumented) | - | - | 169 |
| `locate` | target, uid | (diagram index, node index, rows) for a node uid - read from main_vi_nodeterms.json, not from LabVIEW. | docstring | - | 185 |
| `tunnel_map` | target | (undocumented) | - | - | 194 |
| `resolve` | target, tunnel_uid, outer_wire, max_hops=6 | §11r: one hop at a time from Python. Returns the resolution dict. | docstring | - | 199 |
| `main` |  | (undocumented) | - | - | 238 |

### tools/bench/diag_vigraph_check.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/vigraph_g8_edges_74.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | label, ok, detail='' | (undocumented) | - | - | 37 |
| `fact` | line | (undocumented) | - | - | 43 |
| `newest` | pattern | The newest dated census (was: today's date only, which broke the check on every later day). | docstring | - | 47 |
| `g10_equal_top` |  | G10 (cycle 68): two LEFT registers at EQUAL TOP in one loop body - the M4b shape (#23796 / #23880 both at | docstring | - | 52 |
| `g12_diag_term` | rec_s1, A | G12 (card 74-2, Pre-decided 176(c)): a Diagram-owned 'Terminal' SOURCE (loop 'i') is its own computation node. | docstring | - | 76 |
| `load` | key | (undocumented) | - | - | 106 |
| `dump` | name, payload | (undocumented) | - | - | 141 |
| `main` |  | (undocumented) | - | - | 150 |

### tools/bench/drive_legguard.py

shared file in the bench folder (move to tools/ later); imported by 6 file(s): `tools/bench/diag_c104_abba.py`, `tools/bench/diag_c106b_live.py`, `tools/bench/drive_m8_replay_110.py`, `tools/bench/drive_original_copy_v5.py`, `tools/bench/selftest_c108e_tools.py`, `tools/bench/selftest_leg_guard.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `test_stop_at_l2` |  | (undocumented) | - | - | 19 |
| `visa_precheck` | names=PRECHECK_NAMES, dry=False, dll=None, log=print | -> {"ok", "bypassed", "dry", "rm_status", "trials": [{name, status, hex, text, close, ms}]}. Never raises. | docstring | - | 23 |
| `lv_running` |  | (undocumented) | - | - | 45 |
| `kill_labview` | wait_s=20.0 | direct kill (standing restart permission); -> (gone, secs). | docstring | - | 49 |
| `lv_windows` |  | -> [(hwnd, title, class, visible, enabled)] of labview.exe's top-level windows. | docstring | - | 71 |
| `modal_of` | snap, baseline | the first NEW visible enabled dialog-class window while another visible LabVIEW window is disabled, else None. | docstring | - | 84 |
| `shotwin` | h, png | (undocumented) | - | - | 90 |
| `ocr_text` | png | (undocumented) | - | - | 100 |
| `DialogWatch` | (class) | start() BEFORE Run (baseline = windows visible then); stop() after L2. .fired / .record carry the result. | docstring | - | 112 |
| `DialogWatch.run` |  | (undocumented) | - | - | 123 |
| `DialogWatch.stop` | timeout=60.0 | (undocumented) | - | - | 152 |
| `stop_reason` | arm, row | PD217(g)/PD218(d): the rule that ends the whole leg loop; None = continue. | docstring | - | 156 |
| `refusal_verdict` | gates, rows, loop_stop | card 108-5 (PD222(d); archive/peer/2026-09-27-c108a-disp107-visa-refusal.md:90, 108-1 open 2): -> (status, n_pass, | docstring | - | 164 |
| `leg_loop` | order, run_leg, log=print, max_legs=None | order = [(arm, src, _, npick)]; run_leg(slot, arm, src, attempt, npick) -> row. Returns (finals, stop). | docstring | - | 191 |

### tools/bench/drive_m8.py

shared file in the bench folder (move to tools/ later); imported by 14 file(s): `tools/bench/diag_c104_leg.py`, `tools/bench/diag_c104f_leg.py`, `tools/bench/diag_c105_leg.py`, `tools/bench/diag_c105b_leg.py`, `tools/bench/diag_c105c_leg.py`, `tools/bench/diag_c89_profiler_leg.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `md5` | p | (undocumented) | - | - | 43 |
| `tra_rows` | p, ncol=12 | (undocumented) | - | - | 46 |
| `lv_running` |  | (undocumented) | - | - | 51 |
| `table` | s3=False | (undocumented) | - | - | 55 |
| `main` |  | (undocumented) | - | - | 62 |

### tools/bench/drive_original_copy_v2.py

shared file in the bench folder (move to tools/ later); imported by 4 file(s): `tools/bench/d0_clickprobe.py`, `tools/bench/diag_d0_pickloop_liveness.py`, `tools/bench/drive_original_copy_v3.py`, `tools/bench/drive_original_copy_v4.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `log` | msg | (undocumented) | - | - | 161 |
| `rec` | step, method, ok, detail | (undocumented) | - | - | 165 |
| `PollCom` | (class) | (undocumented) | - | - | 178 |
| `PollCom.run` |  | (undocumented) | - | - | 188 |
| `PollCom.call` | kind, *args, timeout=COM_T | (undocumented) | - | - | 242 |
| `RunThread` | (class) | (undocumented) | - | - | 265 |
| `RunThread.run` |  | (undocumented) | - | - | 272 |
| `gui` | *args, timeout=60 | (undocumented) | - | - | 297 |
| `shot` | name | (undocumented) | - | - | 307 |
| `windows` |  | (undocumented) | - | - | 314 |
| `win_present` | sub | (undocumented) | - | - | 318 |
| `win_rect` | sub | (undocumented) | - | - | 322 |
| `dialogs` |  | (undocumented) | - | - | 328 |
| `blocked` |  | (undocumented) | - | - | 332 |
| `click` | x, y, why | (undocumented) | - | - | 336 |
| `keys` | sendkeys, why | (undocumented) | - | - | 345 |
| `focus` | sub | (undocumented) | - | - | 354 |
| `inside` | rect, xy, margin=25 | (undocumented) | - | - | 358 |
| `md5` | path | (undocumented) | - | - | 365 |
| `state` |  | (undocumented) | - | - | 373 |
| `getv` | name, timeout=COM_T | (undocumented) | - | - | 380 |
| `snapshot` |  | (undocumented) | - | - | 387 |
| `listdir_stats` | d | (n_files, total_bytes, {ext: (n, bytes)}, [non-tiff names]) | docstring | - | 391 |
| `delete_tiffs` | d | (undocumented) | - | - | 412 |
| `reset_controls` |  | (undocumented) | - | - | 431 |
| `stop_via_vi_control` | tag | P10. VI Server FIRST, re-arming every 2 s so a latch cannot swallow the write. | docstring | - | 443 |
| `bandpass_round` | tag, expect=3 | P6. Answer every 'choose bandpass' panel, one Yes click each, verify it closes. | docstring | - | 472 |
| `answer_save_dialog` | tag, base_path | P7. Type an ABSOLUTE path under our run folder. Keyboard first (the file-name edit holds | docstring | - | 522 |
| `cycle` | tag, base_path, first | One complete run: Run -> picks -> done -> bandpass -> save -> loop -> stop. | docstring | - | 563 |
| `main` |  | (undocumented) | - | - | 710 |
| `cleanup` |  | (undocumented) | - | - | 781 |
| `report` |  | (undocumented) | - | - | 839 |

### tools/bench/drive_original_copy_v4.py

shared file in the bench folder (move to tools/ later); imported by 3 file(s): `tools/bench/diag_d0_pickloop_liveness.py`, `tools/bench/drive_original_copy_v5.py`, `tools/bench/tmx_fallthrough_probe.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `motor_gate` | why | Run 'py tools/motor_gate.py --session start' and parse its readback. Returns (rc, text). | docstring | - | 205 |
| `parse_motor` | text | Pull the machine-readable lines out of the gate's output, without importing its parsers on a | docstring | - | 221 |
| `prelimits_from` | text | The sender's NORMALISED pre-write limit line, read with an ANCHORED whole-line regex. | docstring | - | 259 |
| `tmx_from` | text | What the controller HELD when the gate arrived, i.e. the post-LabVIEW-run TMX?.  Returns | docstring | - | 280 |
| `selftest_tmx` |  | 'py tools/bench/drive_original_copy_v4.py --selftest' - pure-function, no COM, no motor, no | docstring | - | 319 |
| `clickprobe` | title, x, y, why | (undocumented) | - | - | 447 |
| `delivered` | j | (undocumented) | - | - | 467 |
| `gated_click_hwnd` | title, x, y, why, max_attempts=2 | THE TOKEN IS THE HWND, NOT THE TITLE (v3's finding). A second attempt is issued ONLY if the | docstring | - | 477 |
| `derive_geometry` |  | Returns (ok, detail). Fills GEO with image_rect / picks / done_xy for THIS panel window. | docstring | - | 518 |
| `bandpass_yes_now` |  | (undocumented) | - | - | 543 |
| `control_labels` |  | The exact label bytes of the 60 front-panel CONTROLS of THIS copy, from the read-only | docstring | - | 553 |
| `record_panel` | tag | READ every control. NEVER write. Returns (n_read, n_err, dict). | docstring | - | 566 |
| `stop_single_write` | tag | The peer's discriminating test verbatim (archive/peer/2026-09-17-d0v3-stop-heuristic.md:32): | docstring | - | 595 |
| `stop_rearmed` | tag | Only reached if the single-write test did not idle the VI. Still VI SERVER ONLY. | docstring | - | 618 |
| `stop_measured` | tag | Returns (stopped_by_vi_server, mechanism, detail). Abort is NEVER used here - cleanup owns | docstring | - | 635 |
| `leg` | tag, n, base_path, cal_wait | n = the gate-number base, so leg 1 numbers 10.. and leg 2 numbers 20.. . | docstring | - | 659 |
| `main` |  | (undocumented) | - | - | 853 |
| `cleanup` |  | (undocumented) | - | - | 953 |
| `report` |  | (undocumented) | - | - | 1040 |

### tools/bench/drive_original_copy_v5.py

shared file in the bench folder (move to tools/ later); imported by 15 file(s): `tools/bench/diag_c104_leg.py`, `tools/bench/diag_c104f_leg.py`, `tools/bench/diag_c105_leg.py`, `tools/bench/diag_c105b_leg.py`, `tools/bench/diag_c105c_leg.py`, `tools/bench/diag_c89_profiler_leg.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `capture` | name | (undocumented) | - | - | 177 |
| `panel_rect` |  | (undocumented) | - | - | 186 |
| `probe_click` | title, x, y, why | clickprobe (the delivery-proven path) + the delivery verdict.  Returns (delivered, j). | docstring | - | 190 |
| `locate_done` | png, prect, tag | Returns (centre, detail, crop_path).  Nothing is inherited: the search rect is the panel | docstring | - | 199 |
| `locate_bandpass_yes` | png, brect | (undocumented) | - | - | 228 |
| `stop_with_fallback` | tag | Returns (stopped, mechanism, latency_s, detail). | docstring | - | 242 |
| `leg` | tag, n, base_path, cal_wait | (undocumented) | - | - | 275 |
| `main` |  | (undocumented) | - | - | 530 |
| `labview_running` |  | (undocumented) | - | - | 634 |
| `cleanup` |  | (undocumented) | - | - | 644 |
| `report` |  | (undocumented) | - | - | 735 |

### tools/bench/fntest_lib.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/bench/fntest_g1.py`, `tools/bench/fntest_g2.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `FT` | (class) | (undocumented) | - | - | 38 |
| `FT.case` | fns, name, fn, check=None | Run one POSITIVE case for the verb-level functions 'fns'; check(res) -> (ok, measured dict). | docstring | - | 60 |
| `FT.negcase` | fns, name, fn, expect | A NEGATIVE case (the plan's neg-double): expect(err, ops) -> (ok, measured). gscript outcomes inside it are | docstring | - | 77 |
| `FT.harness_err` | name, e | (undocumented) | - | - | 94 |
| `FT.verdicts` |  | (undocumented) | - | - | 99 |
| `FT.commit` | log, labview | (undocumented) | - | - | 124 |
| `Bed` | (class) | card chat-F3b: the live graph of a fntest scratch through stagexec.LVBackend, read the way the Executor reads it | docstring | - | 150 |
| `Bed.read` |  | (undocumented) | - | - | 159 |
| `Bed.ts` | owner, name=None, src=None, cls=None | THE one terminal uid of node #owner with that name / direction / term class, else None. | docstring | - | 177 |
| `Bed.ct` | label | The ControlTerminal (front-panel terminal on a diagram) labelled 'label': its own uid (== term uid), else None. | docstring | - | 187 |
| `Bed.wire_of` | term_uid | (undocumented) | - | - | 195 |
| `Bed.cls_of` | uid | (undocumented) | - | - | 199 |
| `Bed.wired_after` | *terms | (ok, measured) after a fresh read: every terminal in 'terms' carries a wire. | docstring | - | 202 |
| `Kit` | (class) | card chat-F3b: the case builders of a fntest runner, every verb called with the stagexec Executor's call shapes | docstring | - | 209 |
| `Kit.need` | name, *v | (undocumented) | - | - | 218 |
| `Kit.cnt` | c | (undocumented) | - | - | 221 |
| `Kit.mk` | fns, name, route, a, args, cls=None, uid=True | (undocumented) | - | - | 224 |
| `Kit.prim` | name, dg, donor, p, pos, cls_=None | (undocumented) | - | - | 239 |
| `Kit.con` | fns, name, src, dst, op=None | (undocumented) | - | - | 244 |
| `Kit.add_sr` | name, loop, parent | The Executor's add_sr sequence (stagexec.py:2228-2316): snap the loop's Terminals[] (on its parent diagram), add | docstring | - | 249 |
| `Kit.r0` |  | R0: count / report_all / uids / exec_state agree on the EMPTY scratch (one Diagram). Returns that Diagram's uid. | docstring | - | 272 |
| `Kit.r1` |  | R1: the node / terminal / panel / wire reads on the built bed (Diagram[0] and [1], node 0). | docstring | - | 282 |
| `owners_of` | objs, resolve=None, cache=None | str(diagram uid) -> [owner class, owner uid] for the Diagrams of a read_live objs list (the Executor's PD185 owners | docstring | - | 293 |
| `term` | real, owner, name=None, src=None, cls=None | THE one terminal row of node #owner with that name / direction / term class (harness lookup; raises if not one). | docstring | - | 324 |

### tools/bench/ground_bench.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/record_claude.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `load_gt` | ids=None | (undocumented) | - | - | 45 |
| `parse_xy` | text | (undocumented) | - | - | 50 |
| `image_size` | path | (undocumented) | - | - | 55 |
| `ask_gpt` | row | (undocumented) | - | - | 61 |
| `ask_uitars` | row | (undocumented) | - | - | 79 |
| `score` | row, ans | (undocumented) | - | - | 99 |
| `append` | rec | (undocumented) | - | - | 109 |
| `cmd_run` | args | (undocumented) | - | - | 114 |
| `cmd_record` | args | (undocumented) | - | - | 129 |
| `cmd_report` | args | (undocumented) | - | - | 142 |

### tools/bench/imaqdx_limits.py

shared file in the bench folder (move to tools/ later); imported by 14 file(s): `tools/bench/camera_contract.py`, `tools/bench/diag_c104_abba.py`, `tools/bench/diag_c91_step4.py`, `tools/bench/diag_c92_m2.py`, `tools/bench/diag_c92c_abba.py`, `tools/bench/diag_c93b_abba.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `CameraInformation` | (class) | (undocumented) | - | - | 31 |
| `get` | sess, name, t=I64 | (undocumented) | - | - | 39 |
| `limits` | sess, name, t=I64 | (minimum, maximum, increment) - the range the camera will actually accept right now. | docstring | - | 45 |
| `report` | sess, tag | (undocumented) | - | - | 55 |
| `main` |  | (undocumented) | - | - | 71 |

### tools/bench/jev_device_value_labels.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/selftest_jev_device_value.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `score` | rows, dk | (undocumented) | - | - | 13 |
| `measure` | path, n=None, ask=None, out_path=None | (undocumented) | - | - | 21 |

### tools/bench/jev_discharge_trial.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/bench/jev_priorart_trial.py`, `tools/bench/jev_run_all.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `build_rows` |  | (undocumented) | - | - | 164 |
| `acc` | rows, thr | (undocumented) | - | - | 185 |
| `report` | rows, title | (undocumented) | - | - | 192 |
| `main` |  | (undocumented) | - | - | 254 |

### tools/bench/jev_gate.py

shared file in the bench folder (move to tools/ later); imported by 16 file(s): `tools/bench/diag_c104_ladder.py`, `tools/bench/jev_discharge_trial.py`, `tools/bench/jev_gatecheck_c68.py`, `tools/bench/jev_ladder_c89.py`, `tools/bench/jev_ladder_c89b.py`, `tools/bench/jev_ladder_c90.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `summarise_review` | path, qchars=2500 | What the gate hands Jev about ONE archived peer exchange: its identity line, the first 'qchars' of the | docstring | - | 61 |
| `review_meta` | path | (agent, role, outcome) lowercased, '' where absent. | docstring | - | 82 |
| `recent_adversary_reviews` | n=N_RECENT_REVIEWS, before=None | The 'n' newest archived exchanges that guard_peer would ACCEPT as a failed-prediction review, newest first. | docstring | - | 93 |
| `covers_failure` | failure_summary, review_summary, purpose='guard-peer-discharge', n=None | Probability that 'review_summary' already covers 'failure_summary'. (p, None) or (None, error). | docstring | - | 168 |
| `answers_step` | step_sentence, review_summary, purpose='priorart-duplicate' | Probability that 'review_summary' already answers 'step_sentence'. (p, None) or (None, error). | docstring | - | 183 |
| `gate_log` | line | One line to tools/bench/jev_gate.log. Never raises: a gate must not die on a full disk. | docstring | - | 197 |
| `cite_in_review` | review_path, log_name, p, ts=None | Write the discharge citation into the review file under '## What was done with it', so the audit and | docstring | - | 206 |
| `jev_discharge` | log_path, failure_text, n=N_RECENT_REVIEWS, before=None, write=True | THE GATE CALL (guard_peer.py). Returns (allow, reason_line). | docstring | - | 231 |
| `ladder_classify` | failure_summary, gate_rows='', recent='', purpose='guard-peer-ladder', n=None | (class, mean probability, spread) for ONE failing run. (None, None, None) when there is no answer. | docstring | - | 342 |
| `ladder_allowed_line` | log_name, cls, p, ts | One JSON line per ladder ALLOW, so tools/audit_cycle.py can count builds that ran with no new review. | docstring | - | 359 |
| `cited_review` | discharge_line | archive/peer/<name>.md named by a JEV-DISCHARGE line (fresh or cached), or None. | docstring | - | 379 |
| `next_action` | cls, allowed, discharge_line=None | The NEXT-ACTION text for one gate outcome. 'allowed' is the gate's own decision, never the class alone: | docstring | - | 385 |
| `with_next` | line, action | The JEV line with ' / NEXT-ACTION: <action>' appended. Returns str. | side file | - | 395 |
| `ladder_cache_path` |  | Path of jev_ladder_cache.jsonl in the same folder as GATE_LOG (a redirected GATE_LOG moves the cache too). Returns str. | side file | - | 408 |
| `ladder_cache_get` | key, md5 | The stored verdict for (key, md5), newest wins; None when absent or unreadable. | docstring | - | 432 |
| `ladder_cache_put` | rec | Appends rec as one JSON line to the ladder cache file; an OSError is ignored. Returns None. | side file | - | 449 |
| `newest_ladder_line` | log_name | The newest JEV-LADDER line in GATE_LOG for this log basename (tail only), or None. | docstring | - | 457 |
| `ladder_after_discharge` | log_path, discharge_line, write=True | guard_peer calls this when the ladder did NOT act and the OLD-PATH discharge then allowed: the newest | docstring | - | 474 |
| `jev_ladder` | log_path, failure_text, n=N_RECENT_REVIEWS, before=None, write=True, gate_rows=None | THE LADDER CALL (tools/hooks/guard_peer.py), run BEFORE the ordinary discharge. | docstring | - | 489 |
| `jev_priorart_dup` | step_sentence, n=N_RECENT_REVIEWS, write=True | ADVISORY ONLY (docs/jev-integration-plan.md row #6 'as in A, but do not block'). Returns the advisory | docstring | - | 574 |

### tools/bench/jev_gaterow_q.py

shared file in the bench folder (move to tools/ later); imported by 3 file(s): `tools/bench/jev_wave2a_trials.py`, `tools/bench/jev_wave4_selftest.py`, `tools/jev_gaterow.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `run_segment` | logpath, run_index=-1 | (command, segment text, how it ended) for one BGRUN run of a log, or (None, None, None). | docstring | - | 65 |
| `fail_rows` | logpath, run_index=-1, max_rows=None | Every FAIL row of one run, as [{'line': n, 'label': 'D7', 'row': ..., 'state': {...}}, ...]. | docstring | - | 86 |

### tools/bench/jev_next_q.py

shared file in the bench folder (move to tools/ later); imported by 3 file(s): `tools/bench/jev_next_trial.py`, `tools/bench/selftest_next_gate_jev.py`, `tools/hooks/guard_bash.py`

(no public function)

### tools/bench/jev_priorart_trial.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/jev_run_all.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `main` |  | (undocumented) | - | - | 139 |

### tools/bench/jev_triage_q.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/bench/jev_triage_trial.py`, `tools/jev_triage.py`

(no public function)

### tools/bench/jev_wave2a_trials.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/jev_ladder_remeasure.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | ok, label, detail='' | (undocumented) | - | - | 64 |
| `ledger_lines` |  | (undocumented) | - | - | 75 |
| `out_of_time` | why | (undocumented) | - | - | 83 |
| `cell_a` |  | (undocumented) | - | - | 91 |
| `cell_b` |  | (undocumented) | - | - | 124 |
| `resolve_trigger` | review_path | (log basename, run index, review epoch) for one archived review, or (None, None, None). | docstring | - | 191 |
| `cell_c` |  | (undocumented) | - | - | 226 |
| `main` |  | (undocumented) | - | - | 317 |

### tools/bench/k_contract_79.py

shared file in the bench folder (move to tools/ later); imported by 42 file(s): `tools/bench/diag_c107b_bedgraph.py`, `tools/bench/diag_c108b_graph.py`, `tools/bench/diag_c110_bedgraph.py`, `tools/bench/diag_c111b_b1graph.py`, `tools/bench/diag_c112c_fixture.py`, `tools/bench/diag_c113a_b2agraph.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `mloops` | s, path | (undocumented) | - | - | 33 |
| `main` | s | (undocumented) | - | - | 48 |

### tools/bench/launch_p3b2_c135.py

shared file in the bench folder (move to tools/ later); imported by 4 file(s): `tools/bench/launch_p3b2_resume_c135.py`, `tools/bench/launch_p3b2_resume_c135_compare.py`, `tools/bench/selftest_c134_p1.py`, `tools/bench/selftest_c135_2_compare.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `recipe_cmd` | r | (undocumented) | - | - | 52 |
| `graph_key` | g | (undocumented) | - | - | 57 |
| `compare` | new, ref | (equal, diff) - diff lists per field the first differing items (never absorbed: rule 1a, PD288(e)). | docstring | - | 69 |
| `Live` | (class) | (undocumented) | - | - | 85 |
| `Live.child` | step, extra=None | (undocumented) | - | - | 88 |
| `Live.labview_gone` | kill=True | (undocumented) | - | - | 99 |
| `Live.write` | path, data | (undocumented) | - | - | 105 |
| `Live.restore_pb` |  | (undocumented) | - | - | 108 |
| `Dry` | (class) | Nothing spawned, nothing killed, nothing written: each child returns the branch's fixture. | docstring | - | 116 |
| `Dry.child` | step, extra=None | (undocumented) | - | - | 123 |
| `Dry.labview_gone` | kill=True | (undocumented) | - | - | 146 |
| `Dry.write` | path, data | (undocumented) | - | - | 150 |
| `Dry.restore_pb` |  | (undocumented) | - | - | 153 |
| `run` | X, branch='equal' | (undocumented) | - | - | 159 |

### tools/bench/launch_p3b2_c135_graph.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/selftest_c134_p1.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `patched_source` |  | (undocumented) | - | - | 23 |

### tools/bench/launch_p3b2_resume_c135_compare.py

shared file in the bench folder (move to tools/ later); imported by 3 file(s): `tools/bench/diag_c135_2_compare.py`, `tools/bench/launch_p3b2_resume_c135.py`, `tools/bench/selftest_c135_2_compare.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `reannotate` | g | (copy of g with fs_measured.borders = current annotation, changes {border uid: {added, removed, changed, presence}}). | docstring | - | 20 |
| `annotation_only` | ch | (undocumented) | - | - | 42 |
| `compare` | new, ref | (equal, diff, changes) - C135.compare on the re-annotated pair; a non-annotation re-annotation change on either side is | docstring | - | 47 |

### tools/bench/m8_dry.py

shared file in the bench folder (move to tools/ later); imported by 5 file(s): `tools/bench/diag_c104_leg.py`, `tools/bench/diag_c93b_leg.py`, `tools/bench/diag_c94_leg.py`, `tools/bench/diag_c96_leg.py`, `tools/bench/selftest_leg_guard.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `FakeCom` | (class) | (undocumented) | - | - | 8 |
| `FakeCom.call` | kind, *args, timeout=None | (undocumented) | - | - | 9 |
| `stub` | v5, d4, d0 | (undocumented) | - | - | 13 |

### tools/bench/m8b_replay_compare.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/drive_m8_replay_110.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `tra` | d | (undocumented) | - | - | 15 |
| `cal` | d | (undocumented) | - | - | 26 |
| `main` | a1, a3, out | (undocumented) | - | - | 31 |

### tools/bench/opmodels_lib.py

shared file in the bench folder (move to tools/ later); imported by 3 file(s): `tools/bench/opmodels_check_move.py`, `tools/bench/opmodels_fit.py`, `tools/bench/opmodels_measure.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `edges` | terms | (undocumented) | - | - | 11 |
| `snapshot_stats` | terms, objs | (undocumented) | - | - | 25 |
| `diff` | before, after | before/after = (terms, objs). Returns a JSON-able dict. | docstring | - | 32 |
| `apply_move` | terms, node_uid | MOVE MODEL v0 (fitted on L7-1a, S3 -> D1_l7_1a, move of SubVI #376): returns predicted terms after | docstring | - | 79 |
| `apply_delete_object` | terms, node_uid | DELETE_OBJECT MODEL v0 (delete_object #7201, #27605; plus the setup of remove_bad_wires_1, delete #1628): the node and | docstring | - | 125 |
| `summary` | d | (undocumented) | - | - | 141 |

### tools/bench/prep_c143_3_elrule.py

shared file in the bench folder (move to tools/ later); imported by 11 file(s): `tools/bench/prep_c142_5_pred.py`, `tools/bench/prep_c143_3_pred.py`, `tools/bench/prep_c143_5_pred.py`, `tools/bench/prep_c143_6_pred.py`, `tools/bench/prep_c143_p1_pred.py`, `tools/bench/prep_c144_1_pred.py` ...

(no public function)

### tools/bench/prep_c156_a1_1_lib.py

shared file in the bench folder (move to tools/ later); imported by 41 file(s): `tools/bench/diag_c160_g1_1.py`, `tools/bench/diag_c162_a1_1_hash.py`, `tools/bench/diag_c162_a1_2_hash.py`, `tools/bench/diag_c163_a2_1_hash.py`, `tools/bench/diag_c163_a2_2_hash.py`, `tools/bench/diag_c164_a3_5_hash.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `Gate` | (class) | Gate counter: g(label, ok, detail, fatal=True) prints 'GATE PASS/FAIL / label / detail'; a fatal FAIL prints the C6 RESULT line and | docstring | - | 30 |
| `Gate.result` | arts=None | (undocumented) | - | - | 46 |
| `step_facts` | tag, R_, quiet=False | {step n: md5 of the step file's state} for a stagesim.simulate result; prints one 'FACT STEP' line per step (op, id, ok/PROVISIONAL/ | docstring | - | 51 |
| `tie_rows` | SA, ACTS, ok_pairs, key_parts, card | (ties, untied, open_rows): every end cdiff row of a pass-A sim tied to the FIRST action of the unbroken run of steps that carry it (or to a | docstring | - | 66 |
| `main_of` | n, KINDS, SX, SPR, MODEL, START, reads=2 | (MAIN MB, x10_model_peak dict, checkpoints) of the op prefix 1..n: Executor peak at START with a checkpoint at every op of the SHARED | docstring | - | 95 |
| `sg_census` | p, SX | The ControlTerminal-sink rows of a FINAL plan: every wire action whose sim effect's dst terminal is a ControlTerminal (stagexec.is_ct) | docstring | - | 104 |

### tools/bench/prep_c156_a1_2_lib.py

shared file in the bench folder (move to tools/ later); imported by 7 file(s): `tools/bench/diag_c160_f3_2.py`, `tools/bench/diag_c163_a3_1_read.py`, `tools/bench/prep_c156_a1_2_measure.py`, `tools/bench/prep_c156_a1_2_regress.py`, `tools/bench/prep_c157_a1_1_regress.py`, `tools/bench/selftest_c156_passwire.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `md5` | p | md5 hex digest of file p. | docstring | - | 45 |
| `jload` | p | The JSON object stored at p (utf-8). | docstring | - | 51 |
| `k_actions` | groups=('K3', 'K3f', 'K4', 'K4f'), pass_frame=None | (top-level plan dict without actions, action list): the 60 all-plan actions of plan_ring_p5s02r_in.json followed by | docstring | selftest_c156_passwire.py | 57 |
| `sim_plan` | top, acts, name, route_check=False | stagesim.simulate of 'top' + 'acts' written to tools/bench/sim/ring_p5s02pw/<name>/plan_<name>_in.json on the P5-1 graph | docstring | selftest_c156_passwire.py | 77 |
| `last_state` | R | The simulated state of the last step a simulate() result R recorded (the state BEFORE a failing action). | docstring | - | 88 |
| `term_brief` | r | (term_uid, owner_uid, owner_class, term_class, frame_diagram, wire_uid) of a terminal row. | docstring | - | 93 |
| `compile_all` | pattern='plan_*.json' | {repo-relative plan path: {md5, ops} / {md5, error} / {skip}} - stagexec.compile_plan over every stored plan matching | docstring | - | 98 |
| `run_suite` | tag, outdir=HERE | [(name, rc, pass_lines, fail_lines, last RESULT/summary line)] - each SUITE self-test run as a child (offline), its | docstring | - | 115 |

### tools/bench/prep_c159_c1_1_lib.py

shared file in the bench folder (move to tools/ later); imported by 3 file(s): `tools/bench/diag_c160_g1_1.py`, `tools/bench/prep_c159_c1_1_mk.py`, `tools/bench/selftest_c160_stagemap.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `made_symbols` | acts | The 'new:' symbols the rows create: every 'as' alias, plus <as>L / <as>R of an add_shift_reg. Self-test: --selftest. | docstring | - | 31 |
| `used_symbols` | acts, made | Sorted earlier-step symbols the rows reference: 'new:X' (address heads) or 'new:X.f<k>' (frame diagrams), minus 'made'. Self-test: --selftest. | docstring | - | 40 |
| `map_symbols` | used, sym, bound, graph | (REAL, bad, lines): each used symbol -> sim uid (sym) -> real uid (bound); a frame symbol's real uid must be an owners entry | docstring | - | 57 |
| `map_frames` | acts, all_acts, sym, bound, owners, default_frames=('False', 'True') | (FMAP {(action id, end uid): {...,'addr': '#<uid>'}}, bad, lines): a 'frame' name on an end whose tunnel ('tunnel' action in all_acts) | docstring | - | 84 |
| `apply_map` | acts, REAL, FMAP | The rows with earlier-step symbols -> real uids (string address 'new:X.t' in src/dst -> {'uid': real, 'term': 't'}) and mapped frame | docstring | - | 120 |
| `bound_from_cmap` | path | {sim uid: real uid} over the obj / diag / term entries of ONE creation-map/1 file, read by stage_prerun.read_creation_map; a sim id in | docstring | - | 146 |

### tools/bench/prep_c164_a2_3_lib.py

shared file in the bench folder (move to tools/ later); imported by 19 file(s): `tools/bench/prep_c164_a2_3_el.py`, `tools/bench/prep_c164_a2_3_licence.py`, `tools/bench/prep_c164_a2_3_md5.py`, `tools/bench/prep_c164_a2_3_pred.py`, `tools/bench/prep_c164_a3_4_el.py`, `tools/bench/prep_c164_a3_4_licence.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `base_uids` | a | Base (int) uids a plan action names: loop / body / parent / diagram, a delete row's uid / wire_uid, and a dict end's uid / term_uid. | docstring | - | 32 |
| `is_stale` | row, aids | (stale, action name): a row whose clears_by names an ACTION ('A70 w_k3f') that is not in this plan's ids 'aids'. | docstring | - | 42 |
| `attached_wires` | state, uid | Wire uids on the terminal rows owned by object 'uid' in a sim state. | docstring | - | 49 |
| `wires_of` | s | (undocumented) | - | - | 54 |
| `objs_of` | s | (undocumented) | - | - | 58 |
| `licence` | cfg | cfg: PLAN, LIC, X11LOG, SESS, STAGE, CARD, STEP_TXT, PD, PRECEDENT, MAKER. Writes the pb-licence/1 file; returns the gate rc. | docstring | - | 68 |
| `el` | cfg | cfg: PLAN, SESS, EXPF, OUT, PINS, A0 (A number of action 1), STEP_TXT, CARD, MAKER, UNPRED_WHY, ELR_SPAN. Writes the predicted | docstring | - | 118 |
| `pred` | cfg | cfg: RRP, PP, SESS, SGF, ELF, LIC, GRAPH, PINS, BEDVI_MD5_PREFIX, A0, LIMIT, MAIN_SRC_READS, CARD, STEP_TXT, NOTE, N_DW, N_DO. Writes the | docstring | - | 239 |
| `unchanged` | pins, outs | U: every pinned file's md5 starts with its pin; prints the md5 of every output. Returns the gate rc. | docstring | - | 411 |

### tools/bench/prep_plan_flow_lib.py

shared file in the bench folder (move to tools/ later); imported by 12 file(s): `tools/bench/prep_c164_a1_1_mk.py`, `tools/bench/prep_c164_a2_1_cmp.py`, `tools/bench/prep_c164_a2_1_mk.py`, `tools/bench/prep_c164_a2_2_mk.py`, `tools/bench/prep_c164_a3_1_cmp.py`, `tools/bench/prep_c164_a3_1_hash.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `leaves` | x, pre='' | {'/path': scalar} of a JSON value (dict keys / list indices joined by '/'). Same as prep_c163_a1_1_mk.py:74-79. | docstring | - | 35 |
| `bind_sources` | gate, sources, used, GR | (REAL {symbol: real uid}, per-source info): each used symbol is bound by the ONE adopted step whose actions make it - that step's last sim step | docstring | - | 44 |
| `make_step_plan` | gate, rin, groups, graph, base_vi, base_plan, sources, card, stage, plan_in, session, goal_fn, probe_goal, plan_out_d... | Make plan_<stage>.json (written ONLY by stagesim.simulate) from the rows of the whole 'groups' (census names, in plan order) of 'rin', on the | docstring | - | 79 |

### tools/bench/s1_subvi_paths.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/recipes/stage_d1_s1.py`, `tools/recipes/stage_d1_s2.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | label, ok, detail='' | (undocumented) | - | - | 90 |
| `fact` | s | (undocumented) | - | - | 97 |
| `md5` | p | (undocumented) | - | - | 101 |
| `child` | tag, target | (undocumented) | - | - | 110 |
| `run_condition` | tag, target | (undocumented) | - | - | 183 |
| `llb_root` | path | Nearest ancestor DIRECTORY COMPONENT of 'path' whose name ends in .llb, or None. | docstring | - | 212 |
| `main` |  | (undocumented) | - | - | 224 |

### tools/bench/selftest_assign_flow.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/selftest_runner_debate.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | label, ok, detail='' | (undocumented) | - | - | 65 |
| `hook` | env_extra, sub, prompt, sid, transcript=None | (undocumented) | - | - | 70 |
| `mk_card` | d, cid, advances=('M3',), write=('tools/bench/x_*.py',), goal='build step', retry=None, unblocks=None | (undocumented) | - | - | 85 |
| `mk_result` | d, cid, status='PASS', ff=None, blocked=None | (undocumented) | - | - | 101 |
| `fresh_state` | tmp, name, purpose=None, t0=None, decisions=None | (undocumented) | - | - | 109 |
| `env_for` | st, cfg | (undocumented) | - | - | 115 |
| `hook_tests` | tmp, cfg | (undocumented) | - | - | 122 |
| `runner_stubs` | tmp | Write the judge / assign stand-ins and the space-free hook launcher into 'tmp'. -> dict of their paths. Shared | docstring | selftest_runner_debate.py | 305 |
| `runner_case` | tmp, st, name, jmode, amode, cfg_path, extra=(), seed_next=False, cycles=1 | Run tools/cycle_runner.py --dry-cmd <judge stub> [--assign-dry-cmd <assign stub>] on a fresh bench under | docstring | - | 320 |
| `runner_tests` | tmp, cfg | (undocumented) | - | - | 348 |
| `main` |  | (undocumented) | - | - | 404 |

### tools/bench/selftest_c153_poskey_convert.py

shared file in the bench folder (move to tools/ later); imported by 3 file(s): `tools/bench/diag_c153_a2_3_run.py`, `tools/bench/diag_c153_a2_4_run.py`, `tools/bench/diag_c153_a2_5_run.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `pos_table` | G | Alias of stagekit.pos_slot_table. | docstring | - | 24 |
| `name_free` | P, s | Alias of stagekit.pos_name_free. | docstring | - | 29 |
| `slots` | G, V, nodes | Alias of stagekit.pos_slots (argument order of the old copy). | docstring | - | 34 |
| `convert` | rows, SA, SB | Alias of stagekit.pos_convert. | docstring | - | 39 |
| `sinks` | conv | Sorted distinct sinks of converted rows. | docstring | - | 44 |
| `convert_open_rows` | plan_open_rows, old_rows, new_rows | Alias of stagekit.pos_convert_open_rows. | docstring | - | 49 |

### tools/bench/selftest_guard_peer_jev.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/jev_run_all.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | ok, label, detail='' | (undocumented) | - | - | 42 |
| `Stub` | (class) | Replace jev_gate.covers_failure with a constant, or with a raiser. | docstring | - | 97 |
| `main` |  | (undocumented) | - | - | 110 |
| `read` | p | (undocumented) | - | - | 356 |
| `run_main` | cmd, capture=False | Drive guard_peer.main() with a PreToolUse payload; optionally capture its stderr. | docstring | - | 374 |

### tools/bench/selftest_guard_peer_ladder.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/selftest_jev_ladder_action.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | ok, label, detail='' | (undocumented) | - | - | 80 |
| `LadderStub` | (class) | Replace jev_gate.ladder_classify with a constant verdict, or with a raiser. | docstring | - | 90 |
| `CoversStub` | (class) | Replace jev_gate.covers_failure with a constant probability. | docstring | - | 103 |
| `read` | p | (undocumented) | - | - | 114 |
| `run_main` | cmd, capture=False | (undocumented) | - | - | 132 |
| `main` |  | (undocumented) | - | - | 146 |

### tools/bench/selftest_stoprecord_supersession.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/selftest_stoprecord_table.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | name, ok, detail='' | (undocumented) | - | - | 63 |
| `first_line` | msg | (undocumented) | - | - | 69 |
| `fingerprint` | p | (undocumented) | - | - | 73 |
| `patched` |  | Is the loaded stop_record carrying the supersession rule? Read from the source, never assumed. | docstring | - | 112 |
| `run_case` | case, want_later, later_disposed, tag | Returns (allow, msg, records). Builds a fresh isolated store, an old RELEASED record at sha s1, edits the | docstring | - | 120 |
| `exempt_patched` |  | Is the loaded stop_record carrying the COMMAND-POSITION EXEMPTION (cycle 46)? Read, never assumed. | docstring | - | 190 |
| `run_exemption_case` |  | CASE 4 - the second half of the deadlock (cycle 46). A STANDING, UNDISPOSED record refuses everything that | docstring | - | 195 |
| `run_novel_case` |  | CASE 5 (cycle 72 firefighter). Old RELEASED record at s1; bytes edited to s2; a NOVEL review of s2 written | docstring | - | 246 |
| `main` |  | (undocumented) | - | - | 306 |

### tools/bench/selftest_t6_poskey.py

shared file in the bench folder (move to tools/ later); imported by 4 file(s): `tools/bench/diag_c153_a2_3_run.py`, `tools/bench/diag_c153_a2_5_run.py`, `tools/bench/selftest_c147_b1_2.py`, `tools/bench/selftest_t7_ring.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | label, ok, detail='' | (undocumented) | - | - | 40 |
| `fact` | s | (undocumented) | - | - | 45 |
| `load` | plan, rj, cmap | (undocumented) | - | - | 49 |
| `enrich` | B, SIM, RE5, ob, tb | Real rows in READ order with the fields the stored read dropped (module docstring). Returns (rows, unbound sim uids). | docstring | - | 68 |
| `order_diffs` | B, R | (undocumented) | - | - | 93 |
| `names_by_node` | rows, ob=None | {node (mapped through ob): [(class, direction, name), ...] in read order} - the FACT on created objects. | docstring | - | 101 |
| `main` |  | (undocumented) | - | - | 111 |
| `k141` | K | selftest_td_key_c141_3.py's 141-2 case (P4 s01 scratch: LabVIEW re-used deleted uids), rebuilt exactly as there (:40-62), re-asked | docstring | selftest_td_key_c141_3.py | 213 |

### tools/bench/spec_read.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/spec_read_more.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `describe` | v, depth=0 | (undocumented) | - | - | 21 |
| `purge_junk` | target, before | (undocumented) | - | - | 32 |
| `main` |  | (undocumented) | - | - | 43 |

### tools/bench/subvi_harness.py

shared file in the bench folder (move to tools/ later); imported by 6 file(s): `tools/bench/blackbox_z.py`, `tools/bench/harness_probe2.py`, `tools/bench/harness_probe6.py`, `tools/bench/quad_probe.py`, `tools/bench/radial_probe.py`, `tools/bench/radial_probe2.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `build` | subvi_path, max_terms=32, force=False | (undocumented) | - | - | 27 |
| `run` | h, inputs, outputs | (undocumented) | - | - | 78 |

### tools/bench/t2_rsrc_blockdiff.py

shared file in the bench folder (move to tools/ later); imported by 2 file(s): `tools/bench/diag_c153_a2_6_rsrc.py`, `tools/bench/diag_c89_profiler_lvsr.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `recipe_constants` |  | Read ORIGINAL / ORIG_MD5 / ARM out of tools/recipes/stage_d1_s1.py WITHOUT importing it | docstring | - | 109 |
| `md5_of` | path | (undocumented) | - | - | 130 |
| `version_bytes` | data | PRIOR ART, reused verbatim in behaviour from tools/recipes/stage_d1_s1.py:293 -- the first 64 | docstring | - | 138 |
| `ParseError` | (class) | (undocumented) | - | - | 152 |
| `parse_rsrc` | data, label | Return (record, checks).  Never raises on a malformed file -- it records the failure. | docstring | - | 156 |
| `key_of` | block | (undocumented) | - | - | 274 |
| `main` |  | (undocumented) | - | - | 278 |

### tools/bench/verify_d1_s2.py

shared file in the bench folder (move to tools/ later); imported by 1 file(s): `tools/bench/c52_astcheck.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `Stop` | (class) | (undocumented) | - | - | 116 |
| `gate` | name, ok, detail='', fatal=False | (undocumented) | - | - | 120 |
| `fact` | line | (undocumented) | - | - | 130 |
| `probe` | tag, path | (undocumented) | - | - | 135 |
| `dump` |  | (undocumented) | - | - | 143 |
| `cond_read` | tag, target, loop_uid | ONE conditional-terminal readback through 'OpLoopEndRef_v0', scored on its FOUR per-property ERROR COLUMNS | docstring | - | 150 |
| `owner` | target, uid | Parent traversal, with the error kept rather than swallowed. | docstring | - | 175 |
| `read_one` | tag, path, key | Everything this file reads out of ONE .vi, read-only: census, WhileLoop identity + ownership + conditional | docstring | - | 184 |
| `main` |  | (undocumented) | - | - | 218 |

### tools/recipes/build_d1_m3a1.py

recipe imported by another file; imported by 25 file(s): `tools/bench/c90c_rows.py`, `tools/bench/diag_c73_m3a2_rows.py`, `tools/bench/diag_c74_m3a2_verify.py`, `tools/bench/diag_c75_m3a3_endpoints.py`, `tools/bench/diag_c75_m3a3_rows.py`, `tools/bench/diag_c75b_loopterms.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `Halt` | (class) | (undocumented) | - | - | 399 |
| `gate` | name, ok, detail='' | (undocumented) | - | - | 403 |
| `fact` | line | (undocumented) | - | - | 411 |
| `refusal` | where, msg | A MUTATOR CALL THE MACHINE REFUSED. This is the only class of negative result that gates (63). | docstring | - | 416 |
| `probe_hash` | tag, path | (undocumented) | - | - | 422 |
| `dump` |  | (undocumented) | - | - | 429 |
| `left_s` |  | (undocumented) | - | - | 438 |
| `safe` | label, fn, default=None | Run one READ, record its error VERBATIM, never let it kill the run. | docstring | - | 442 |
| `read_es` | tag, target | (undocumented) | - | - | 452 |
| `counts` | path, tag, classes=('Node', 'Wire', 'ControlTerminal', 'Local', 'LoopTunnel', 'Tunnel') | NARROW CLASS CENSUSES ONLY - never a whole-VI GObject census (six of those took handles 34,602 -> | docstring | - | 468 |
| `sr_counts` | path, tag | (undocumented) | - | - | 479 |
| `node_census` | path, tag | (undocumented) | - | - | 487 |
| `new_nodes` | before, after | (undocumented) | - | - | 495 |
| `terms_at` | path, diagram_index, nodes_index, expect_uid, tag, quiet=False | The FULL terminal table of one node, with the node's own uid echoed back before it is believed. | docstring | - | 500 |
| `term_state` | t | WIRED / BARE / UNREAD for ONE terminal row (Pre-decided 14; gscript.py:874 gives the one legitimate | docstring | - | 524 |
| `wired_count` | rows | (undocumented) | - | - | 537 |
| `find_node` | path, uid, hints, tag, budget_s=240.0, quiet=False | Which DIAGRAM lists 'uid' in its Nodes[] - answered by the census that finds it, NEVER by owner_of | docstring | - | 541 |
| `node_view` | path, uid, hints, tag, quiet=False | (undocumented) | - | - | 572 |
| `delete_by_uid` | path, cls, uid, tag | report_all(cls) -> .index(uid) -> delete_object(cls, idx). The shape cycle 58 used; no new verb. | docstring | - | 583 |
| `census_and_purge` | path, nodes_before, tag, hints, keep_uids=() | 55(c): after EVERY move_in and EVERY connect_nested_v1, diff the 'Node' census and purge the junk BY | docstring | - | 614 |
| `save_artefact` | tag, dest, not_equal_to, not_equal_label | g.save writes the WORKING copy in place; the artefact is a fresh path LabVIEW has never seen. | docstring | - | 662 |
| `unit_boundary` | tag | The user's 2026-09-19 split rule, applied MECHANICALLY and not as a branch: read ExecState at every | docstring | - | 729 |
| `loop_index_of` | uid, tag | (undocumented) | - | - | 745 |
| `echo_reg_uid` | loop_index, reg_index, want_uid, tag | (undocumented) | - | - | 761 |
| `reg_index_of` | loop_index, reg_uid, tag | Map a RightShiftRegister uid to its reg_index by READING shift_reg(...) for each slot. Never assumed. | docstring | - | 770 |
| `resolve_term` | rows, want_name, want_i, want_source, tag | Address a terminal OFF THE MACHINE: by NAME when the name is non-empty and unique among terminals of | docstring | - | 792 |
| `pd85_violations` | wire_uid, walk | PRE-DECIDED 85, THE READER PRECONDITION (docs/cycle27-plan.md:3031-3038): before any assertion | docstring | - | 811 |
| `print_walk` | tag, wire_uid, walk, err='' | One FACT line per terminal of 'OpWireSource_v5(UID 2 = wire_uid)': is_source / owner_class / | docstring | - | 823 |
| `wire_walk` | tag, wire_uid | 'OpWireSource_v5(UID 2 = wire_uid)' on the LIVE target, printed terminal by terminal. | docstring | - | 844 |
| `loop_tunnel_sinks` | walk | (undocumented) | - | - | 851 |
| `identity_gate` | tag, source_wire, src_before, src_after, sink_wire, sink_walk, mandatory | PRE-DECIDED 70, THE WHOLE TEST, READ OFF THE MACHINE AND NOTHING ELSE. | docstring | - | 857 |
| `phase_0` |  | (undocumented) | - | - | 967 |
| `step_2_baseline` |  | (undocumented) | - | - | 998 |
| `resolve_dest` | tag | 38(e): RE-RESOLVE the destination index BY UID from a freshly-read traverse list immediately before | docstring | - | 1037 |
| `body_a_node_uids` | tag | THE AUTHORITATIVE READ: Diagram #23058's own Nodes[] census, by uid. | docstring | - | 1054 |
| `step_2_moves` | hints | (undocumented) | - | - | 1067 |
| `one_row` | nodes, hints, sink_uid, sink_name, sink_t, src_uid, src_name, src_t, why, tag, slot, src_hints=None | ONE 'connect_nested_v1' row, addressed off the machine at both ends and verified BY WIRE UID. | docstring | - | 1120 |
| `step_2_rows` | nodes, hints | (undocumented) | - | - | 1185 |
| `step_3_registers` |  | (undocumented) | - | - | 1196 |
| `step_4_sr_rows` | made, hints | (undocumented) | - | - | 1242 |
| `step_5_t1` | nodes, hints | THE FIFTH ROW, RE-CUT 2026-09-21 by the prior-art review's B3 'helper-exists'. | docstring | - | 1339 |
| `step_6_sixth_row` | nodes, hints | THE SIXTH ROW, WIRED **BEFORE** THE CENSUS SO THE A4 BARE-SINK GATE JUDGES THE FINISHED STAGE. | docstring | - | 1530 |
| `bare_sink_gate` | hints | '#10407' t6 ''position [internal units]'' has TWO sinks in the original, on net 9113: the | docstring | - | 1773 |
| `census` | tag, hints, include_registers=True | THE FULL WIRED-TERMINAL CENSUS of the seven moved nodes (and both registers) - EVERY terminal, not a | docstring | - | 1946 |
| `step_7_save` | hints | (undocumented) | - | - | 2002 |
| `main` |  | (undocumented) | - | - | 2054 |

### tools/recipes/build_d1_m3a3b_d3.py

recipe imported by another file; imported by 4 file(s): `tools/bench/diag_c86_norbw.py`, `tools/bench/opmodels_measure.py`, `tools/recipes/build_d1_m3a3b_d3b.py`, `tools/stagekit.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | name, ok, detail='', fatal=False | (undocumented) | - | - | 222 |
| `fact` | line | (undocumented) | - | - | 231 |
| `head` | t | (undocumented) | - | - | 236 |
| `safe` | label, fn, default=None | (undocumented) | - | - | 240 |
| `dump` |  | (undocumented) | - | - | 249 |
| `left_s` |  | (undocumented) | - | - | 257 |
| `labels_of` | target, indicators=False | (undocumented) | - | - | 261 |
| `bad_wire_count` | target, tag | The diagram-wide BROKEN-WIRE COUNT. 'remove_bad_wires_scripted' runs LabVIEW's own | docstring | - | 265 |
| `fsit_call` | op_path, labels, target, fsit_uid, sink_diag, sink_node, sink_term, ar_label='', auto_route=None, inv_err_label='erro... | One call of the connect op. Every readout is POISONED first (Pre-decided 125): a stale value can | docstring | - | 279 |
| `fsit_read` | target, uid, tag | One read of a FlatSequenceInnerTunnel's two faces through 'OpFsInnerTunnelTerm_v0'. | docstring | - | 342 |
| `phase_files` |  | (undocumented) | - | - | 361 |
| `phase_restart` |  | (undocumented) | - | - | 388 |
| `build_v1` |  | (undocumented) | - | - | 403 |
| `gates_23` | labels, ar | (undocumented) | - | - | 515 |
| `gate_s` | tag, target, d_idx, before_read, r, baseline_bad, rec, probe_bad=True | GATE S (a)-(e) on 'target' after a call. Returns (all_passed, dict of the five outcomes). | docstring | - | 581 |
| `one_call_and_gates` | tag, target, d_idx, labels, ar, auto_route, baseline_bad, rec, probe_bad=True | (undocumented) | - | - | 638 |
| `baseline_bad_wires` |  | (undocumented) | - | - | 688 |
| `run_cells` | labels, ar, baseline_bad | (undocumented) | - | - | 709 |
| `step3` | labels, ar, results, baseline_bad | (undocumented) | - | - | 757 |
| `phase_hygiene` |  | (undocumented) | - | - | 848 |
| `main` |  | (undocumented) | - | - | 902 |

### tools/recipes/build_d1_v0.py

recipe imported by another file; imported by 182 file(s): `tools/bench/build_op_const_loopterm_77.py`, `tools/bench/c52_astcheck.py`, `tools/bench/c52r2_astcheck.py`, `tools/bench/c52r3_astcheck.py`, `tools/bench/c53_astcheck.py`, `tools/bench/c73_l7r_live.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | name, ok, detail='' | (undocumented) | - | - | 299 |
| `fact` | line | (undocumented) | - | - | 305 |
| `md5` | p | (undocumented) | - | - | 310 |
| `move_in` | target, uid, dest_diagram_index, position | probe_move_ctlterm_v0.py:160-178 verbatim. The Move returns NO reference to the object at its new home | docstring | - | 318 |
| `owner_of` | target, uid, strict=True | (undocumented) | - | - | 338 |
| `diag_index` | target, uid | (undocumented) | - | - | 357 |
| `wmap` | target, diagram_index, fresh=False | ONE 'build_track_v6_core.walk' per diagram, cached. 'walk' is 'node_labels' + up to 80 'node_terms_uid' | docstring | - | 364 |
| `terms_of` | target, diagram_index, uid, fresh=False | {term index: (name, is_source, wire)} for one node, out of the cached walk of its diagram. | docstring | - | 375 |
| `sr_census` | target, loop_index, n_regs=14 | Every shift register of one While loop: its OUTSIDE wire (the final value that LEAVES the loop) and its | docstring | - | 383 |
| `s0` |  | (undocumented) | - | - | 405 |
| `s1` |  | (undocumented) | - | - | 437 |
| `bare_named_sinks` | target, diagram_index, fresh=False | {(node uid, terminal index): name} for every NAMED input terminal on the diagram that carries NO wire. | docstring | - | 482 |
| `s1t` |  | (undocumented) | - | - | 494 |
| `s2` |  | (undocumented) | - | - | 533 |
| `s3` | loops | (undocumented) | - | - | 569 |
| `s3c` | loops | (undocumented) | - | - | 734 |
| `s3d` | loops, kernel_uid | The 6 loop-invariant seam inputs must reach the kernel through NON-INDEXED tunnels (plan s8; rule 1a - | docstring | - | 769 |
| `loop_end_ref` | target, loop_index | A While loop's CONDITIONAL TERMINAL, through OpLoopEndRef_v0 (16/0). Driven exactly as | docstring | - | 820 |
| `s4` | loops | (undocumented) | - | - | 856 |
| `s5` | inv0 | (undocumented) | - | - | 888 |
| `s6` |  | (undocumented) | - | - | 907 |
| `class_index` | target, classes=('SubVI', 'Function', 'CaseStructure', 'ForLoop', 'WhileLoop', 'Comparison', 'IndexArray', 'BuildArra... | uid -> (Traverse class, index in that class's Traverse listing). 'gscript.wire' addresses a node as | docstring | - | 946 |
| `phase_full_rewire` | loops, regs, r3 | (undocumented) | - | - | 962 |
| `main` |  | (undocumented) | - | - | 1156 |

### tools/recipes/build_opcaseframes_v0.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/build_oploopendref_v0.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `prop_node` | cls, pid, label, pos | Build a property node and CENSUS its data terminal - the short name is never guessed. | docstring | - | 48 |
| `add_indicator` | uid, name, key, labels | (undocumented) | - | - | 62 |
| `main` |  | (undocumented) | - | - | 74 |
| `read_frame` | vi, labels, case_uid, idx | (undocumented) | - | - | 210 |
| `test` | labels | (undocumented) | - | - | 230 |

### tools/recipes/build_opconnectfromwire_v0.py

recipe imported by another file; imported by 55 file(s): `tools/bench/constsrc_l2a1_82.py`, `tools/bench/constsrc_l2a1_85.py`, `tools/bench/ctsrc_l2a1_82.py`, `tools/bench/diag_c113c_scratch.py`, `tools/bench/diag_c66_s3b_m3.py`, `tools/bench/diag_c66b_s3b_m3.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | name, ok, detail='', fatal=False | (undocumented) | - | - | 141 |
| `fact` | line | (undocumented) | - | - | 149 |
| `md5` | p | (undocumented) | - | - | 153 |
| `new_ctl` | target, before_labels | (undocumented) | - | - | 161 |
| `ctl_labels` | target, indicators=False | (undocumented) | - | - | 166 |
| `build` |  | (undocumented) | - | - | 171 |
| `connect_from_wire` | target, wire_uid, term_index, sink_diag, sink_node, sink_term, labels | Wire the SOURCE terminal 'Wire(uid=wire_uid).Terms[term_index]' into | docstring | - | 381 |
| `wire_source_owner` | target, wire_uid, n=6 | 'OpWireSource_v5' on 'target': the owner of the wire's single SOURCE terminal. Read-only. | docstring | - | 427 |
| `t1` | labels | (undocumented) | - | - | 491 |
| `t2` | labels | (undocumented) | - | - | 558 |
| `cleanup` |  | (undocumented) | - | - | 640 |
| `main` |  | (undocumented) | - | - | 656 |

### tools/recipes/build_opconnectnested_v1.py

recipe imported by another file; imported by 72 file(s): `tools/bench/c53_astcheck.py`, `tools/bench/diag_c120_fs.py`, `tools/bench/diag_c123_casetun.py`, `tools/bench/diag_c123_routes.py`, `tools/bench/diag_c123_struct.py`, `tools/bench/diag_c123_wired.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `Stop` | (class) | (undocumented) | - | - | 129 |
| `gate` | name, ok, detail='', fatal=False | (undocumented) | - | - | 133 |
| `fact` | line | (undocumented) | - | - | 141 |
| `md5` | p | (undocumented) | - | - | 146 |
| `walk` | target, diagram=0, limit=120 | (undocumented) | - | - | 154 |
| `term` | rows, name, source=None | (undocumented) | - | - | 165 |
| `cls_of` | uid, w | (undocumented) | - | - | 172 |
| `idx` | target, cls, uid | (undocumented) | - | - | 183 |
| `src_of` | w, wire | the node whose SOURCE terminal carries 'wire' | docstring | - | 187 |
| `connect` | target, src_uid, src_name, dst_uid, dst_name, branch=False, tag='' | Wire by NAME, verified by the SAME wire uid on BOTH ends (build_opconnectnested_v0.connect verbatim). | docstring | - | 196 |
| `del_net` | target, wire_uid, tag='' | (undocumented) | - | - | 212 |
| `ladder_from` | w, sink_wire, tag | IA(term) <- PN[Terms[]] <- IA(node) <- PN[Nodes[]] <- head-wire, walking back from the Invoke. | docstring | - | 221 |
| `build` |  | (undocumented) | - | - | 239 |
| `connect_nested_v1` | target, sink_diag, sink_node, sink_term, src_diag, src_node, src_term, labels | Wire Diagram[src_diag].Nodes[src_node].Terminals[src_term] (SOURCE) into | docstring | - | 418 |
| `test` | labels | (undocumented) | - | - | 463 |
| `main` |  | (undocumented) | - | - | 608 |

### tools/recipes/build_opconstvalue_v1.py

recipe imported by another file; imported by 59 file(s): `tools/bench/census_dnc_property_ids.py`, `tools/bench/census_hexstring_vi.py`, `tools/bench/census_selector_sources.py`, `tools/bench/census_unflatten_terms.py`, `tools/bench/diag_9775_direction.py`, `tools/bench/diag_autofocus_border.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `lv_pid` |  | (undocumented) | - | - | 49 |
| `com_preflight` | tries=15, gap=4.0 | Run 4 (04:13): fresh() + 8 s + reset() was NOT enough - the first call on the relaunched instance died with | docstring | - | 56 |
| `fresh` |  | (undocumented) | - | - | 80 |
| `cls_idx` | target, cls, uid | (undocumented) | - | - | 90 |
| `main` |  | (undocumented) | - | - | 94 |
| `test` | labels | (undocumented) | - | - | 212 |

### tools/recipes/build_opconstvalue_v1b.py

recipe imported by another file; imported by 5 file(s): `tools/bench/diag_constvalue_siblings.py`, `tools/gscript.py`, `tools/recipes/build_opconstvalue_v1c.py`, `tools/recipes/build_opconstvaluen_v0.py`, `tools/recipes/build_opconstvaluen_v1.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `decode_flat` | data | Flattened LabVIEW variant as emitted by Flatten To String on a variant (NI 'Understanding Flattened Variant | docstring | - | 37 |
| `main` |  | (undocumented) | - | - | 95 |
| `test` | labels | (undocumented) | - | - | 141 |

### tools/recipes/build_opconstvalue_v1c.py

recipe imported by another file; imported by 4 file(s): `tools/bench/diag_constvalue_siblings.py`, `tools/gscript.py`, `tools/recipes/build_opconstvaluen_v0.py`, `tools/recipes/build_opconstvaluen_v1.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `new_labels` | dst, before, ind | (undocumented) | - | - | 45 |
| `main` |  | (undocumented) | - | - | 49 |
| `normalize_u8` | v | pywin32 maps SAFEARRAY(VT_UI1) to a buffer-like value (bytes/memoryview), older builds to a tuple of ints | docstring | - | 118 |
| `test` | labels | (undocumented) | - | - | 132 |

### tools/recipes/build_opconstvaluen_v0.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/build_opconstvaluen_v1.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `new_labels` | dst, before, ind | (undocumented) | - | - | 46 |
| `main` |  | (undocumented) | - | - | 50 |
| `parse_num` | s | (undocumented) | - | - | 142 |
| `test` | labels | (undocumented) | - | - | 153 |

### tools/recipes/build_opcreateconstonterm_v0.py

recipe imported by another file; imported by 23 file(s): `tools/bench/build_op_const_loopterm_77.py`, `tools/bench/c52r2_astcheck.py`, `tools/bench/diag_c123_routes.py`, `tools/bench/diag_c123_struct.py`, `tools/bench/diag_c90_t0_step3.py`, `tools/bench/diag_c90_t0_step3b.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | name, ok, detail='' | (undocumented) | - | - | 108 |
| `fact` | line | (undocumented) | - | - | 114 |
| `md5` | p | (undocumented) | - | - | 119 |
| `walk` | target, diagram=0, limit=100 | (undocumented) | - | - | 127 |
| `term` | rows, name, source=None | (undocumented) | - | - | 138 |
| `cls_of` | uid, w | (undocumented) | - | - | 145 |
| `idx` | target, cls, uid | (undocumented) | - | - | 156 |
| `connect` | src_uid, src_name, dst_uid, dst_name, branch=False, tag='' | Wire by name, verified by the SAME wire uid on BOTH ends (build_opstopfromnode_v0.connect verbatim). | docstring | - | 160 |
| `owner_of` | target, uid | (undocumented) | - | - | 175 |
| `counts` | target | (undocumented) | - | - | 191 |
| `build` |  | (undocumented) | - | - | 197 |
| `create_const_on_term` | target, loop_index, node_index, term_index, labels, value=None | Run OpCreateConstOnTerm_v0 on 'target'. Returns {err, inv_err, created_uid} - prior-art B4's oracle | docstring | - | 364 |
| `read_const` | target, uid | The created constant's value/Representation/text through OpConstValueN_v1 (toolkit row 47), addressed by | docstring | - | 392 |
| `test` | labels | (undocumented) | - | - | 423 |
| `main` |  | (undocumented) | - | - | 569 |

### tools/recipes/build_opfsinnertunnelconnect_v0.py

recipe imported by another file; imported by 16 file(s): `tools/bench/build_op_const_loopterm_77.py`, `tools/bench/diag_c138_6_run.py`, `tools/bench/diag_c83_connect2x2.py`, `tools/bench/diag_c83_connect2x2_kit.py`, `tools/bench/diag_c83_connect2x2_r2.py`, `tools/bench/diag_c86_norbw.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | name, ok, detail='', fatal=False | (undocumented) | - | - | 200 |
| `fact` | line | (undocumented) | - | - | 209 |
| `head` | t | (undocumented) | - | - | 214 |
| `safe` | label, fn, default=None | (undocumented) | - | - | 218 |
| `md5` | p | (undocumented) | - | - | 227 |
| `dump` |  | (undocumented) | - | - | 235 |
| `left_s` |  | (undocumented) | - | - | 243 |
| `private_bytes` |  | LabVIEW's private bytes - the COMPANION of the handle count, which | docstring | - | 247 |
| `purge_junk` | target, nodes_before, tag, hints | The measured junk shape of the OpConnect* family: a fresh 'Invoke' node with ZERO wired terminals | docstring | - | 263 |
| `labels_of` | target, indicators=False | (undocumented) | - | - | 302 |
| `new_labels` | target, before, indicators=False | (undocumented) | - | - | 306 |
| `wire_named` | src_cls, src_uid, src_name, dst_cls, dst_uid, dst_name, branch=False, tag='' | Wire by NAME with EXPLICIT traverse classes, verified by the SAME wire uid on BOTH ends. | docstring | - | 310 |
| `data_out` | rows | The single NON-STANDARD source terminal of a property node = its data output. Read back, never | docstring | - | 329 |
| `del_wire` | target, wire_uid, tag='' | (undocumented) | - | - | 336 |
| `del_node` | target, cls, uid, tag='' | (undocumented) | - | - | 346 |
| `phase_files` |  | (undocumented) | - | - | 359 |
| `phase_restart` |  | (undocumented) | - | - | 384 |
| `build` |  | (undocumented) | - | - | 399 |
| `fsit_connect` | target, fsit_uid, sink_diag, sink_node, sink_term, labels, count_wires=False | Wire 'FlatSequenceInnerTunnel(uid=fsit_uid).LeftTerm' into | docstring | - | 597 |
| `gates_23` | labels | (undocumented) | - | - | 651 |
| `resolve_triple` | target, tag | The NEW loop's (diagram traverse index, Nodes[] index, Terminals[] index), resolved LIVE with a uid | docstring | - | 730 |
| `gate4` | labels | (undocumented) | - | - | 752 |
| `phase_hygiene` |  | (undocumented) | - | - | 837 |
| `main` |  | (undocumented) | - | - | 896 |

### tools/recipes/build_opfstunnelterm_v0.py

recipe imported by another file; imported by 1 file(s): `tools/bench/diag_fstunnel_wire_semantics.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `must` | label, ok, detail='' | (undocumented) | - | - | 157 |
| `note` | label, value | (undocumented) | - | - | 163 |
| `md5` | p | (undocumented) | - | - | 167 |
| `snapshot` | tag | (undocumented) | - | - | 182 |
| `handles` | tag | (undocumented) | - | - | 191 |
| `identity` |  | (undocumented) | - | - | 207 |
| `sweep` | target, n=120, diagram=0 | (undocumented) | - | - | 240 |
| `trow` | by, uid, name | (undocumented) | - | - | 250 |
| `twire` | by, uid, name | (undocumented) | - | - | 260 |
| `has` | by, uid, name, is_source=None | (undocumented) | - | - | 265 |
| `cidx` | target, cls, uid | (undocumented) | - | - | 270 |
| `node_index_of` | target, uid, diagram=0, n=120 | (undocumented) | - | - | 274 |
| `wire_checked` | op, src_cls, src_uid, src_term, dst_cls, dst_uid, dst_term, tag='' | One wire, VERIFIED BY TERMINAL IDENTITY instead of by 'gscript.wire''s wire COUNT. | docstring | - | 284 |
| `ctl_labels` | target | (undocumented) | - | - | 323 |
| `ind_labels` | target | (undocumented) | - | - | 327 |
| `build_one` | kind | Build ONE of the two ops. Identical route for both classes; only SPEC[kind] differs. | docstring | - | 331 |
| `read_tunnel` | vi, lab, target, uid | One live read of ONE tunnel uid through ONE of the two ops. Every readout is POISONED first, so a stale | docstring | - | 526 |
| `read_any` | target, uid, kind=None | The reader the CALLER sees: one function over BOTH tunnel classes. 'kind' is taken from the owner's class | docstring | - | 584 |
| `refusal` | target, uid, why | Pre-decided 3: feed a deliberately bad input to BOTH ops and record the refusal VERBATIM. | docstring | - | 600 |
| `face_cross` | target, owner_class, owner_uid, arrival_wire | A4/T2: cross ONE flat-sequence border. Returns (continuation wire or None, read, verdict text). | docstring | - | 618 |
| `walk` | target, seed_wire, tag, max_cross=6 | The backward walk. B3: the HOP LOOP IS 'diag_tunnelsource_onehop.resolve()' - this function only supplies | docstring | - | 642 |
| `crossings_of` | w | (undocumented) | - | - | 676 |
| `live` | target, labels_by_kind | (undocumented) | - | - | 680 |
| `inherit_probe` |  | RECORDED, not gated: does the OUTER class inherit 'Tunnel'? One scratch VI, unique name, deleted in the | docstring | - | 790 |
| `main` |  | (undocumented) | - | - | 835 |

### tools/recipes/build_opfstunnelterm_v1.py

recipe imported by another file; imported by 6 file(s): `tools/bench/diag_fstunnel_orphan_timeline.py`, `tools/bench/diag_fstunnel_orphans.py`, `tools/bench/diag_fstunnel_preclean_twins.py`, `tools/bench/diag_fstunnel_rbwvictims.py`, `tools/bench/diag_fstunnel_wirebroken.py`, `tools/bench/diag_fstunnel_wireterms_panel.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `must` | label, ok, detail='' | (undocumented) | - | - | 165 |
| `note` | label, value | (undocumented) | - | - | 171 |
| `md5` | p | (undocumented) | - | - | 175 |
| `snapshot` | tag | (undocumented) | - | - | 190 |
| `handles` | tag | (undocumented) | - | - | 199 |
| `identity` |  | (undocumented) | - | - | 215 |
| `sweep` | target, n=120, diagram=0 | (undocumented) | - | - | 248 |
| `trow` | by, uid, name | (undocumented) | - | - | 258 |
| `twire` | by, uid, name | (undocumented) | - | - | 268 |
| `has` | by, uid, name, is_source=None | (undocumented) | - | - | 273 |
| `cidx` | target, cls, uid | (undocumented) | - | - | 278 |
| `node_index_of` | target, uid, diagram=0, n=120 | (undocumented) | - | - | 282 |
| `wire_checked` | op, src_cls, src_uid, src_term, dst_cls, dst_uid, dst_term, tag='' | One wire, VERIFIED BY TERMINAL IDENTITY instead of by 'gscript.wire''s wire COUNT, plus a per-site | docstring | - | 292 |
| `ctl_labels` | target | (undocumented) | - | - | 368 |
| `ind_labels` | target | (undocumented) | - | - | 372 |
| `build_one` | kind | Build ONE of the two ops. Identical route for both classes; only SPEC[kind] differs. | docstring | - | 376 |
| `read_tunnel` | vi, lab, target, uid | One live read of ONE tunnel uid through ONE of the two ops. Every readout is POISONED first, so a stale | docstring | - | 571 |
| `read_any` | target, uid, kind=None | The reader the CALLER sees: one function over BOTH tunnel classes. 'kind' is taken from the owner's class | docstring | - | 629 |
| `refusal` | target, uid, why | Pre-decided 3: feed a deliberately bad input to BOTH ops and record the refusal VERBATIM. | docstring | - | 645 |
| `face_cross` | target, owner_class, owner_uid, arrival_wire | A4/T2: cross ONE flat-sequence border. Returns (continuation wire or None, read, verdict text). | docstring | - | 663 |
| `walk` | target, seed_wire, tag, max_cross=6 | The backward walk. B3: the HOP LOOP IS 'diag_tunnelsource_onehop.resolve()' - this function only supplies | docstring | - | 687 |
| `crossings_of` | w | (undocumented) | - | - | 721 |
| `live` | target, labels_by_kind | (undocumented) | - | - | 725 |
| `inherit_probe` |  | RECORDED, not gated: does the OUTER class inherit 'Tunnel'? One scratch VI, unique name, deleted in the | docstring | - | 835 |
| `main` |  | (undocumented) | - | - | 880 |

### tools/recipes/build_opfstunnelterm_v2.py

recipe imported by another file; imported by 6 file(s): `tools/bench/diag_c77_rowd_addr.py`, `tools/bench/diag_c81_uidref.py`, `tools/bench/diag_fstunnel_pairs.py`, `tools/recipes/build_d1_m3a3.py`, `tools/recipes/build_d1_m3a3b_d3.py`, `tools/wiki_build.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `must` | label, ok, detail='' | (undocumented) | - | - | 235 |
| `note` | label, value | (undocumented) | - | - | 241 |
| `md5` | p | (undocumented) | - | - | 245 |
| `snapshot` | tag | (undocumented) | - | - | 260 |
| `handles` | tag | (undocumented) | - | - | 269 |
| `identity` |  | (undocumented) | - | - | 285 |
| `sweep` | target, n=120, diagram=0 | (undocumented) | - | - | 318 |
| `trow` | by, uid, name | (undocumented) | - | - | 328 |
| `twire` | by, uid, name | (undocumented) | - | - | 338 |
| `has` | by, uid, name, is_source=None | (undocumented) | - | - | 343 |
| `cidx` | target, cls, uid | (undocumented) | - | - | 348 |
| `node_index_of` | target, uid, diagram=0, n=120 | (undocumented) | - | - | 352 |
| `wire_checked` | op, src_cls, src_uid, src_term, dst_cls, dst_uid, dst_term, tag='' | One wire, VERIFIED BY TERMINAL IDENTITY instead of by 'gscript.wire''s wire COUNT, plus a per-site | docstring | - | 362 |
| `ctl_labels` | target | (undocumented) | - | - | 438 |
| `ind_labels` | target | (undocumented) | - | - | 442 |
| `orphan_wires` | target, by | (orphan uids, whole Wire census) - a wire is an ORPHAN when NO owning-node terminal reads it at EITHER end. | docstring | - | 460 |
| `rbw_call_sites` |  | A0f: how many times THIS FILE calls the RBW helper - read from its own source text. | docstring | - | 468 |
| `rbw_repair_at_b4` | op, kind, tag | Twin-A reproduction (diag_fstunnel_preclean_twins.log), run ONLY when B4's first ExecState read is not 1: | docstring | - | 483 |
| `build_one` | kind | Build ONE of the two ops. Identical route for both classes; only SPEC[kind] differs. | docstring | - | 535 |
| `read_tunnel` | vi, lab, target, uid | One live read of ONE tunnel uid through ONE of the two ops. Every readout is POISONED first, so a stale | docstring | - | 745 |
| `read_any` | target, uid, kind=None | The reader the CALLER sees: one function over BOTH tunnel classes. 'kind' is taken from the owner's class | docstring | - | 803 |
| `refusal` | target, uid, why | Pre-decided 3: feed a deliberately bad input to BOTH ops and record the refusal VERBATIM. | docstring | - | 819 |
| `face_cross` | target, owner_class, owner_uid, arrival_wire | A4/T2: cross ONE flat-sequence border. Returns (continuation wire or None, read, verdict text). | docstring | - | 837 |
| `walk` | target, seed_wire, tag, max_cross=6 | The backward walk. B3: the HOP LOOP IS 'diag_tunnelsource_onehop.resolve()' - this function only supplies | docstring | - | 861 |
| `crossings_of` | w | (undocumented) | - | - | 895 |
| `live` | target, labels_by_kind | (undocumented) | - | - | 899 |
| `inherit_probe` |  | RECORDED, not gated: does the OUTER class inherit 'Tunnel'? One scratch VI, unique name, deleted in the | docstring | - | 1009 |
| `main` |  | (undocumented) | - | - | 1054 |

### tools/recipes/build_opownerchain_v1.py

recipe imported by another file; imported by 11 file(s): `tools/bench/diag_c152_a1_1_owner.py`, `tools/bench/diag_d1_step0.py`, `tools/bench/diag_hierarchy_a3.py`, `tools/bench/diag_owner_semantics.py`, `tools/bench/diag_ownerchain_hop.py`, `tools/bench/diag_stop_save_seam.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | name, ok, detail='' | (undocumented) | - | - | 187 |
| `md5` | p | (undocumented) | - | - | 192 |
| `sweep` |  | {node_uid: (node_index, rows)} for diagram 0 in ONE pass - no net_map, no creator, no junk. | docstring | - | 196 |
| `trow` | by, uid, name | (undocumented) | - | - | 207 |
| `twire` | by, uid, name | (undocumented) | - | - | 217 |
| `tindex` | by, uid, name | (undocumented) | - | - | 222 |
| `cls_uids` | cls | (undocumented) | - | - | 227 |
| `purge_junk` | before | Delete every Invoke node that appeared since 'before'. 'OpConnect2_v0' carries the erdosmiller | docstring | - | 231 |
| `read_owner` | vi, labels, uid | Drive the op: uid in -> (owner class, owner uid, cross-checks, errors). Outputs poisoned first, so a | docstring | - | 246 |
| `main` |  | (undocumented) | - | - | 282 |

### tools/recipes/build_opsentinel_ops.py

recipe imported by another file; imported by 13 file(s): `tools/bench/c52_astcheck.py`, `tools/bench/diag_queue_donor.py`, `tools/bench/diag_s2_scaffold.py`, `tools/recipes/build_d1_routeb_v0.py`, `tools/recipes/build_d1_routeb_v1.py`, `tools/recipes/build_d1_routeb_v2.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | name, ok, detail='' | (undocumented) | - | - | 143 |
| `fact` | line | (undocumented) | - | - | 149 |
| `md5` | p | (undocumented) | - | - | 154 |
| `owner_of` | target, uid | B4's reader, unchanged: OpOwnerChain_v1 through build_opownerchain_v1.read_owner. | docstring | - | 162 |
| `build` | kind | (undocumented) | - | - | 180 |
| `create_node` | kind, labels, target, diagram_index, location, src_cls=None, src_index=0, src_names=(), values=None | Run Op<CreateEqual/CreateConst>_v0 on 'target'. Same call shape as 'gscript.queue_node', so the wrapper | docstring | - | 387 |
| `functional_test` | built | (undocumented) | - | - | 409 |
| `main` |  | (undocumented) | - | - | 583 |

### tools/recipes/build_opstopfromnode_v0.py

recipe imported by another file; imported by 22 file(s): `tools/bench/c52_astcheck.py`, `tools/bench/c52r2_astcheck.py`, `tools/bench/c52r3_astcheck.py`, `tools/bench/c53_astcheck.py`, `tools/bench/diag_donor_census.py`, `tools/bench/diag_movein_set.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `gate` | name, ok, detail='' | (undocumented) | - | - | 118 |
| `fact` | line | (undocumented) | - | - | 124 |
| `walk` | target, diagram=0, limit=100 | (undocumented) | - | - | 129 |
| `term` | rows, name, source=None | (undocumented) | - | - | 140 |
| `cls_of` | uid, w | (undocumented) | - | - | 147 |
| `idx` | target, cls, uid | (undocumented) | - | - | 158 |
| `data_name` | uid, w=None | The property node's DATA terminal, CENSUSED - not the index-4 convention. | docstring | - | 162 |
| `connect` | src_uid, src_name, dst_uid, dst_name, branch=False, tag='' | Wire by name, verified by the SAME wire uid on BOTH ends - never by a count, never by ExecState | docstring | - | 180 |
| `pn` | cls, pid, pos | Create ONE property node and census it (B3): exactly one new 'Property' object, and 'data_name' then | docstring | - | 196 |
| `ia` | pos | (undocumented) | - | - | 209 |
| `make_ctl` | uid, name | (undocumented) | - | - | 214 |
| `counts` | target | (undocumented) | - | - | 226 |
| `build` |  | (undocumented) | - | - | 230 |
| `loop_end_ref` | target, loop_index | B2: 'build_d1_v0.loop_end_ref' verbatim - it poisons EVERY output (IsSource included) and returns the four | docstring | - | 340 |
| `wire_source` | target, wire_uid, max_terms=8 | B4(b), the POSITIVE check: 'OpWireSource_v5' (12/12, toolkit-capabilities.md:48) resolves which object | docstring | - | 350 |
| `test` | labels | (undocumented) | - | - | 391 |
| `main` |  | (undocumented) | - | - | 527 |

### tools/recipes/build_optunnelread_v0.py

recipe imported by another file; imported by 2 file(s): `tools/bench/diag_hierarchy_a3.py`, `tools/recipes/build_opcaseframes_v0.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `prop_node` | cls, pid, short, pos | (undocumented) | - | - | 44 |
| `add_indicator` | uid, name, key, labels | (undocumented) | - | - | 55 |
| `drop_wire` | uid | (undocumented) | - | - | 67 |
| `main` |  | (undocumented) | - | - | 73 |
| `read_inner` | vi, labels, tunnel_uid, idx | (undocumented) | - | - | 180 |
| `test` | labels | (undocumented) | - | - | 204 |

### tools/recipes/build_opwiresource_v0.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/build_opwiresource_v1.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `new_labels` | dst, before, ind | (undocumented) | - | - | 51 |
| `prop_node` | cls, pid, short, pos | (undocumented) | - | - | 55 |
| `drop_node` | uid, cls, tag | (undocumented) | - | - | 66 |
| `main` |  | (undocumented) | - | - | 72 |
| `read_wire` | vi, labels, wire_uid, wires | (undocumented) | - | - | 200 |
| `test` | labels | (undocumented) | - | - | 218 |
| `finally_audit` |  | (undocumented) | - | - | 248 |

### tools/recipes/build_opwiresource_v1.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/build_opwiresource_v2.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `handles` |  | (undocumented) | - | - | 56 |
| `prop_node` | cls, pid, short, pos | (undocumented) | - | - | 63 |
| `add_indicator` | uid, name, key, labels | (undocumented) | - | - | 74 |
| `main` |  | (undocumented) | - | - | 86 |
| `read_uid` | vi, labels, wire_uid | (undocumented) | - | - | 221 |
| `test` | labels | (undocumented) | - | - | 238 |

### tools/recipes/build_opwiresource_v2.py

recipe imported by another file; imported by 2 file(s): `tools/bench/diag_source_uid_contradiction.py`, `tools/recipes/build_opwiresource_v3.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `prop_node` | cls, pid, short, pos | (undocumented) | - | - | 50 |
| `add_indicator` | uid, name, key, labels | (undocumented) | - | - | 61 |
| `main` |  | (undocumented) | - | - | 73 |
| `read_uid` | vi, labels, wire_uid | (undocumented) | - | - | 159 |
| `test` | labels | (undocumented) | - | - | 177 |

### tools/recipes/build_opwiresource_v3.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/build_opwiresource_v4.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `prop_node` | cls, pid, short, pos | (undocumented) | - | - | 47 |
| `add_indicator` | uid, name, key, labels | (undocumented) | - | - | 58 |
| `main` |  | (undocumented) | - | - | 70 |
| `read_terminal` | vi, labels, wire_uid, idx | (undocumented) | - | - | 134 |
| `test` | labels | (undocumented) | - | - | 155 |

### tools/recipes/build_opwiresource_v4.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/build_opwiresource_v5.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `prop_node` | cls, pid, short, pos | (undocumented) | - | - | 47 |
| `add_indicator` | uid, name, key, labels | (undocumented) | - | - | 58 |
| `main` |  | (undocumented) | - | - | 70 |
| `read_terminal` | vi, labels, wire_uid, idx | (undocumented) | - | - | 126 |
| `test` | labels | (undocumented) | - | - | 148 |

### tools/recipes/build_opwiresource_v5.py

recipe imported by another file; imported by 18 file(s): `tools/bench/c52r2_astcheck.py`, `tools/bench/diag_9775_direction.py`, `tools/bench/diag_autofocus_border.py`, `tools/bench/diag_case5540_context.py`, `tools/bench/diag_case5540_frame_sources.py`, `tools/bench/diag_case5540_inputs.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `prop_node` | cls, pid, short, pos | (undocumented) | - | - | 48 |
| `add_indicator` | uid, name, key, labels | (undocumented) | - | - | 59 |
| `main` |  | (undocumented) | - | - | 71 |
| `read_terminal` | vi, labels, wire_uid, idx | (undocumented) | - | - | 155 |
| `test` | labels | (undocumented) | - | - | 177 |

### tools/recipes/build_opwiresr_v0.py

recipe imported by another file; imported by 1 file(s): `tools/bench/test_opwiresr.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `step` | name, predict, fn | (undocumented) | - | - | 76 |
| `check` | name, ok, detail='' | (undocumented) | - | - | 90 |
| `walk` | target, diagram=0, limit=100 | (undocumented) | - | - | 95 |
| `term` | rows, name, source=None | (undocumented) | - | - | 106 |
| `snap` | tag='' | (undocumented) | - | - | 113 |
| `idx` | cls, uid | (undocumented) | - | - | 118 |
| `cls_of` | uid, w | (undocumented) | - | - | 122 |
| `pn` | cls, pid, pos | (undocumented) | - | - | 133 |
| `ia` | pos | (undocumented) | - | - | 138 |
| `wire_uid` | uid, name, source, w=None | (undocumented) | - | - | 143 |
| `data_name` | uid, w=None | A property node's data terminal = index 4 (v1 recipe). | docstring | - | 149 |
| `connect` | src_uid, src_name, dst_uid, dst_name, branch=False, tag='' | wire by name, verified by the SAME wire uid on both ends (row 37: never by count, never by ExecState). | docstring | - | 155 |
| `make_ctl` | uid, name, label_key, labels | (undocumented) | - | - | 169 |
| `make_ind` | uid, name, label_key, labels | (undocumented) | - | - | 180 |
| `build` | variant | (undocumented) | - | - | 191 |
| `run_op` | variant, labels, target, loop_index, reg_index, **kw | (undocumented) | - | - | 283 |
| `test` | all_labels | (undocumented) | - | - | 293 |
| `add_sr_for` | target, loop_index, y | OpAddShiftRegF_v0 (built by build_opaddshiftreg_v0.py with SR_SEED=For) -> new register uid. | docstring | - | 374 |
| `test_for` | all_labels | FUNCTIONAL, For seed: HARNESS_copyloop's existing For loop (N = 1024); a NEW IMAQ Copy dropped in its body; | docstring | - | 387 |
| `main` |  | (undocumented) | - | - | 447 |

### tools/recipes/build_track_v6_core.py

recipe imported by another file; imported by 37 file(s): `tools/bench/census_dnc_property_ids.py`, `tools/bench/census_hexstring_vi.py`, `tools/bench/census_unflatten_terms.py`, `tools/bench/diag_c118_p1.py`, `tools/bench/diag_c122_hyg.py`, `tools/bench/diag_c123_routes.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `Stop` | (class) | (undocumented) | - | - | 68 |
| `arg` | name, default | (undocumented) | - | - | 72 |
| `must` | name, ok, detail='' | (undocumented) | - | - | 77 |
| `walk` | target, diagram=0 | (undocumented) | - | - | 84 |
| `term` | rows, name, source | (undocumented) | - | - | 95 |
| `sub_i` | target, uid | (undocumented) | - | - | 99 |
| `drop` | target, path, diagram, pos | (undocumented) | - | - | 103 |
| `wire_sub` | target, su, st, du, dt, dsrc, ddst, branch=False, tag='' | Wire by name and gate by wire uid. Same diagram: one Wire object, same uid on both ends. ACROSS a loop border | docstring | - | 111 |
| `string_array_control` | target, tag | (undocumented) | - | - | 144 |
| `tunnel_route` | target, fp_label, u_stp, body, tag | wire_control(ctl -> StrToPath.string) creates a non-indexed tunnel; set_index_mode(1) must heal the wire. | docstring | - | 159 |
| `discriminator` |  | (undocumented) | - | - | 174 |
| `build` |  | (undocumented) | - | - | 198 |
| `load_reference` |  | (undocumented) | - | - | 337 |
| `fixture_run` | labels, ref, frames, tag | ONE COM run over 'frames'; XYZ/GOOD/POS rows compared EXACTLY with the reference (pre-loss frames). | docstring | - | 349 |
| `main` |  | (undocumented) | - | - | 399 |

### tools/recipes/stage_d1_fgate.py

recipe imported by another file; imported by 3 file(s): `tools/bench/selftest_c98_rbw.py`, `tools/bench/selftest_c98_stage.py`, `tools/recipes/diag_c98_fgate.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 24 |
| `St` | (class) | (undocumented) | - | - | 123 |
| `St.close` | expect_files=None | (undocumented) | - | - | 124 |

### tools/recipes/stage_d1_l2r1.py

recipe imported by another file; imported by 1 file(s): `tools/bench/diag_c115b_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `rbw` | s, target, tag | (undocumented) | - | - | 31 |
| `body` | s | (undocumented) | - | - | 36 |

### tools/recipes/stage_d1_l2r2.py

recipe imported by another file; imported by 2 file(s): `tools/bench/diag_c116b_scratch.py`, `tools/bench/diag_c116d_j3.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `rbw` | s, target, tag | (undocumented) | - | - | 28 |
| `body` | s | (undocumented) | - | - | 33 |

### tools/recipes/stage_d1_l7_r.py

recipe imported by another file; imported by 1 file(s): `tools/bench/dryrun_l7_r_address.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `lg` | s, tag, gone=() | (undocumented) | - | - | 16 |
| `trow` | s, dg, u, i | (undocumented) | - | - | 23 |
| `at` | s, dg, u, name, is_src | First resolution BY NAME (Pre-decided 174); the one ambiguous name (#2048 'length') is tie-broken by the index its S1 wire used (anchored by A0). | docstring | - | 27 |
| `nested` | s, tag, src, dst | (undocumented) | - | - | 35 |
| `tunnel_row` | s, tag, src_term, dst, old, TM | (undocumented) | - | - | 40 |
| `second` | s, sym, lab, srcs, u, t, tu | 42(b) ordered 2nd pass, the sink addressed by verify_term_uid ONLY now (Pre-decided 174); the source owner is the first listed that owns it. | docstring | - | 50 |
| `body` | s | (undocumented) | - | - | 59 |

### tools/recipes/stage_d1_qrt_pool.py

recipe imported by another file; imported by 1 file(s): `tools/bench/stage_d1_qrt_pool_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 28 |

### tools/recipes/stage_d1_ring_p2a.py

recipe imported by another file; imported by 1 file(s): `tools/bench/stage_d1_ring_p2a_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 29 |

### tools/recipes/stage_d1_ring_p2b.py

recipe imported by another file; imported by 1 file(s): `tools/bench/stage_d1_ring_p2b_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `same` | a, b | (undocumented) | - | - | 32 |
| `body` | s | (undocumented) | - | - | 41 |

### tools/recipes/stage_d1_ring_p3a.py

recipe imported by another file; imported by 1 file(s): `tools/bench/stage_d1_ring_p3a_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 29 |

### tools/recipes/stage_d1_ring_p3b1.py

recipe imported by another file; imported by 1 file(s): `tools/bench/stage_d1_ring_p3b1_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 34 |

### tools/recipes/stage_d1_ring_p3b2a.py

recipe imported by another file; imported by 2 file(s): `tools/bench/launch_p3b2_c135_a.py`, `tools/bench/stage_d1_ring_p3b2a_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 34 |

### tools/recipes/stage_d1_ring_p3b2b.py

recipe imported by another file; imported by 2 file(s): `tools/bench/launch_p3b2_c135_b.py`, `tools/bench/stage_d1_ring_p3b2b_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 36 |

### tools/recipes/stage_d1_ring_p4_rasrest.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4_rasrest_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 34 |

### tools/recipes/stage_d1_ring_p4_s01.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4_s01_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 38 |

### tools/recipes/stage_d1_ring_p4_s02.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4_s02_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 35 |

### tools/recipes/stage_d1_ring_p4_s02v18.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4_s02v18_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 33 |

### tools/recipes/stage_d1_ring_p4_s03v18.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4_s03v18_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 33 |

### tools/recipes/stage_d1_ring_p4_s04v18.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4_s04v18_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 34 |

### tools/recipes/stage_d1_ring_p4_s05v18.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4_s05v18_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 33 |

### tools/recipes/stage_d1_ring_p4_s06v18.py

recipe imported by another file; imported by 2 file(s): `tools/bench/diag_c147_a2_1_check.py`, `tools/recipes/stage_d1_ring_p4_s06v18_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `SGBackend` | (class) | LVBackend that KEEPS its last whole-VI read (no extra read; stagexec.LVBackend.read is called exactly as before). | docstring | - | 56 |
| `SGBackend.read` |  | (undocumented) | - | - | 59 |
| `sg_read` | e | (ok, detail) for the deferred op error on SINK: (a) the indicator terminal exists with exactly ONE wire, (b) that wire is the net of | docstring | - | 64 |
| `body` | s | (undocumented) | - | - | 93 |

### tools/recipes/stage_d1_ring_p4_s06v18_scratch.py

recipe imported by another file; imported by 1 file(s): `tools/bench/diag_c147_a2_1_check.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `snap_keep` | target=None | (undocumented) | - | - | 41 |
| `cg_print` | label, before, after, declared | (undocumented) | - | - | 45 |
| `x10` |  | The X10 prediction of THIS plan: the pred file's memory_pred.peak_mb, only when the pred is keyed to the plan's md5. | docstring | - | 65 |
| `body` | s | (undocumented) | - | - | 77 |
| `norm_ocr` | s | (undocumented) | - | - | 88 |
| `elcls` | it | One Error List item -> its class (== prep_c147_a1_3_pred.py elcls): local / cond / sr / input / other:<norm_ocr(raw)>. | docstring | - | 95 |
| `el_advisory` | items, pred=None | (rc, report) for one EL read (its items) against the pred: rc 1 only for an unseen class or /total diff/ > EL_TOTAL_TOL; rc 2 when | docstring | - | 106 |
| `el_advisory_print` | rc, rep | (undocumented) | - | - | 126 |
| `el_selftest` |  | Three synthetic reads built from the pred's predicted per-class counts (offline): unseen class -> 1; total +4 -> 1; total +2 known -> 0. | docstring | - | 132 |

### tools/recipes/stage_d1_ring_p4_s07v18.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4_s07v18_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `SGBackend` | (class) | LVBackend that KEEPS its last whole-VI read (no extra read; stagexec.LVBackend.read is called exactly as before). | docstring | - | 81 |
| `SGBackend.read` |  | (undocumented) | - | - | 84 |
| `sg_read` | e, d | (ok, detail) for the deferred op error on sink d['sink']: (a) the indicator terminal exists with exactly ONE wire, (b) that wire is the | docstring | - | 89 |
| `body` | s | (undocumented) | - | - | 123 |

### tools/recipes/stage_d1_ring_p4_s08v18.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4_s08v18_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `SGBackend` | (class) | LVBackend that KEEPS its last whole-VI read (no extra read; stagexec.LVBackend.read is called exactly as before). | docstring | - | 81 |
| `SGBackend.read` |  | (undocumented) | - | - | 84 |
| `sg_read` | e, d | (ok, detail) for the deferred op error on sink d['sink']: (a) the indicator terminal exists with exactly ONE wire, (b) that wire is the | docstring | - | 89 |
| `body` | s | (undocumented) | - | - | 123 |

### tools/recipes/stage_d1_ring_p4_s09v18.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4_s09v18_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `SGBackend` | (class) | LVBackend that KEEPS its last whole-VI read (no extra read; stagexec.LVBackend.read is called exactly as before). | docstring | - | 83 |
| `SGBackend.read` |  | (undocumented) | - | - | 86 |
| `sg_read` | e, d | (ok, detail) for the deferred op error on sink d['sink']: (a) the indicator terminal exists with exactly ONE wire, (b) that wire is the | docstring | - | 91 |
| `body` | s | (undocumented) | - | - | 125 |

### tools/recipes/stage_d1_ring_p4s1.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p4s1_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 33 |

### tools/recipes/stage_d1_ring_p5s01a.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p5s01a_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `SGBackend` | (class) | LVBackend that KEEPS its last whole-VI read (no extra read; stagexec.LVBackend.read is called exactly as before). | docstring | - | 82 |
| `SGBackend.read` |  | (undocumented) | - | - | 85 |
| `sg_read` | e, d | (ok, detail) for the deferred op error on sink d['sink']: (a) the indicator terminal exists with exactly ONE wire, (b) that wire is the | docstring | - | 90 |
| `body` | s | (undocumented) | - | - | 124 |

### tools/recipes/stage_d1_ring_p5s01b.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p5s01b_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 40 |

### tools/recipes/stage_d1_ring_p5s02.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p5s02_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 40 |

### tools/recipes/stage_d1_ring_p5s02a.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p5s02a_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 36 |

### tools/recipes/stage_d1_ring_p5s02b.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p5s02b_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 38 |

### tools/recipes/stage_d1_ring_p5s02c.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p5s02c_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 38 |

### tools/recipes/stage_d1_ring_p5s02d.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p5s02d_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 41 |

### tools/recipes/stage_d1_ring_p5s02e.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_d1_ring_p5s02e_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 40 |

### tools/recipes/stage_d1_s1.py

recipe imported by another file; imported by 4 file(s): `tools/bench/c53_astcheck.py`, `tools/bench/verify_d1_s2.py`, `tools/recipes/stage_d1_s2_loops.py`, `tools/recipes/stage_d1_s3_focus.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `Stop` | (class) | (undocumented) | - | - | 254 |
| `gate` | name, ok, detail='', fatal=True | Every gate in this file is FATAL by default: the first FAIL stops the chain and leaves its artefacts. | docstring | - | 258 |
| `fact` | line | (undocumented) | - | - | 267 |
| `md5` | p | (undocumented) | - | - | 272 |
| `labview_pid` |  | The LabVIEW process id, read EXACTLY the way 'tools/bench/bench_prep.py:64-70' reads its handle count — | docstring | - | 280 |
| `version_bytes` | path | CLAUDE.md §1's saved-version audit, WITHOUT assuming an offset: return the first 64 bytes as hex and every | docstring | - | 293 |
| `file_facts` | tag, path | md5 + size + version bytes of one artefact, recorded and logged in one place. | docstring | - | 303 |
| `fresh` | tag | A FRESH LabVIEW instance (standing restart authority, CLAUDE.md §3), then rebind every cached proxy. | docstring | - | 317 |
| `Preload` | (class) | 'tools/bench/p2_open_copy.py:22-28' verbatim: hold the ORIGINAL resident READ-ONLY for the duration of a | docstring | - | 332 |
| `dump` |  | Both artefacts are written from the SAME accumulator, and are re-written in 'main''s 'finally', so a fatal | docstring | - | 360 |
| `orig_gate` | phase | Rule 1, after EVERY phase: the ORIGINAL's md5 still equals the pin. FATAL. | docstring | - | 369 |
| `cold_subvi_table` | tag, target | ONE COLD SubVI-path census of 'target', in ITS OWN CHILD PROCESS and its OWN fresh LabVIEW instance. | docstring | - | 377 |
| `compare_subvi_tables` | got, reference, expect_missing | 'got' must be 'reference' MINUS 'expect_missing', key-for-key, in BOTH name and path. | docstring | - | 408 |
| `log_table_diff` | label, cmp_ | The FULL diff, printed line by line. Called only when a comparison fails — nothing is elided. | docstring | - | 430 |
| `phase_a` |  | NO DIAGRAM EDIT OF ANY KIND. The only question is whether 'g.save()' (default 'allow_broken') completes on | docstring | - | 451 |
| `phase_b` |  | Does the SAVED arm still call exactly the subVIs the ORIGINAL calls? | docstring | - | 495 |
| `phase_c` |  | The stage itself: a fresh copy of the ORIGINAL, the two FIXTURE TIFF nodes cut, the copy SAVED. | docstring | - | 612 |
| `phase_d` |  | The saved artefact is re-read in a FRESH instance under BOTH conditions. This is the half of Pre-decided | docstring | - | 695 |
| `main` |  | (undocumented) | - | - | 763 |

### tools/recipes/stage_d1_s3_focus.py

recipe imported by another file; imported by 1 file(s): `tools/bench/c53_astcheck.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `Stop` | (class) | (undocumented) | - | - | 287 |
| `gate` | name, ok, detail='', fatal=True | 37(i), 'docs/cycle27-plan.md:1132-1139': the DOCUMENTED format is '  FAIL  ' / '  PASS  ', which | docstring | - | 291 |
| `fact` | line | (undocumented) | - | - | 303 |
| `probe` | tag, path | (undocumented) | - | - | 308 |
| `dump` | phase=None | (undocumented) | - | - | 315 |
| `term_state` | r | WIRED / BARE / UNREAD for ONE 'node_terms_uid' row. | docstring | - | 327 |
| `node_state` | tag, target, uid, expect_owner=None, quiet=False | The live state of ONE node, addressed BY uid and re-resolved at the call site (34(h) / 37(b)): | docstring | - | 346 |
| `term_index` | rec, name, want_i, is_source=None | The LIVE terminal index for a (name, recorded index) pair. The NAME is the address; 'want_i' is only the | docstring | - | 391 |
| `cond_read` | tag, target, loop_uid | ONE conditional-terminal readback through 'OpLoopEndRef_v0', scored on its FOUR per-property error | docstring | - | 403 |
| `census` | tag, target | (undocumented) | - | - | 419 |
| `load_rewire_rows` |  | The 17 '"dest": "1.5"' rows of the MEASURED cut-terminal table, straight from the file. | docstring | - | 426 |
| `phase_0_files` |  | (undocumented) | - | - | 438 |
| `phase_1_baseline` |  | (undocumented) | - | - | 459 |
| `phase_2_move` |  | (undocumented) | - | - | 538 |
| `phase_3_shift_regs` |  | (undocumented) | - | - | 570 |
| `phase_4_rewire` |  | (undocumented) | - | - | 666 |
| `phase_5_cross` |  | (undocumented) | - | - | 708 |
| `phase_6_acceptance` |  | (undocumented) | - | - | 742 |
| `phase_7_save` |  | (undocumented) | - | - | 776 |
| `phase_8_verify` |  | (undocumented) | - | - | 791 |
| `main` |  | (undocumented) | - | - | 860 |
| `salvage` |  | CLAUDE.md "a step is not done until it has left a file": if a FATAL gate stopped the run before PHASE 7, | docstring | - | 883 |

### tools/recipes/stage_template_ring.py

recipe imported by another file; imported by 1 file(s): `tools/recipes/stage_template_ring_scratch.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `body` | s | (undocumented) | - | - | 39 |

### tools/hooks/adapt_claude.py

hook - reference; imported by 1 file(s): `tools/bench/selftest_guardcore.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `to_event` | p | Claude PreToolUse payload -> guardcore event. | docstring | - | 27 |
| `render` | verdict, why | (stderr text, exit code): Claude's native form. | docstring | - | 51 |
| `main` |  | (undocumented) | - | - | 58 |

### tools/hooks/adapt_codex.py

hook - reference; imported by 1 file(s): `tools/bench/selftest_guardcore.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `find_patch` | obj | The first string inside 'obj' (dict/list/str, any depth) that contains '*** Begin Patch', else None. | docstring | - | 39 |
| `parse_patch` | body | [{op, old, new, content}] from an apply_patch body; [] when no file header is found. | docstring | - | 53 |
| `to_event` | p | Codex PreToolUse payload -> guardcore event. | docstring | - | 97 |
| `render` | verdict, why | (stdout text, exit code). Allow = empty stdout, exit 0. Deny = the three-field JSON, exit 0. | docstring | - | 125 |
| `main` |  | (undocumented) | - | - | 134 |

### tools/hooks/guard_assign.py

hook - reference; imported by 6 file(s): `tools/bench/prep_c162_check_outside.py`, `tools/bench/selftest_assign_flow.py`, `tools/bench/selftest_c148_guard_fp.py`, `tools/bench/selftest_runner_debate.py`, `tools/cycle_runner.py`, `tools/hooks/guard_session.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `role` |  | (undocumented) | - | - | 56 |
| `load_config` | path=None | (undocumented) | - | - | 60 |
| `state_load` | path | (undocumented) | - | - | 73 |
| `state_save` | path, d | (undocumented) | - | - | 82 |
| `open_decisions_count` | path | (undocumented) | - | - | 90 |
| `new_state` | path, cycle, rnd, purpose, next_md5, decisions_path, t0=None | Written by the runner before it spawns the assignment session. | docstring | - | 99 |
| `classify` | res, card_path=None | (explained_kind / None, class_key) for a FAIL/BLOCKED result/1 dict. Fails CLOSED: any classifier error -> unexplained. | docstring | - | 131 |
| `result_of` | entry | The result/1 dict beside the entry's card, written after the dispatch, or None. | docstring | - | 160 |
| `card_rows` | st | (undocumented) | - | - | 176 |
| `usd_estimate` | transcript_path, prices | USD of the session so far: its transcript + <stem>/subagents/*.jsonl (nested agents land there too - measured | docstring | - | 201 |
| `evaluate` | st, cfg, now=None, usd=None | {'trigger', 'detail'} for the first hand-back condition that holds over the session's results, or None. | docstring | - | 237 |
| `scope_match` | card_ids, purpose_ids | (undocumented) | - | - | 282 |
| `card_outside` | card, purpose, cfg | (c): '' or the reason this card leaves the purpose's plan. | docstring | - | 294 |
| `cards_dir` |  | The one directory whose cards guard_assign evaluates: tools/bench/cards (env ASSIGN_CARDS_DIR overrides, for a | docstring | - | 369 |
| `card_in_cards_dir` | cpath | (undocumented) | - | - | 375 |
| `check_dispatch` | st_path, sub, card, cpath, transcript_path=None, now=None, cfg=None | (0, '') allow - the dispatch is recorded in the state; (2, text) refuse. Runs under guard_session's lock. | docstring | - | 384 |
| `runner_verdict` | st_path, result_path, envelope_usd=None, rc=0, cfg=None, now=None | After the session: (outcome 'PURPOSE_MET'/'HANDBACK', trigger/None, detail, result dict/None). The hook's sticky | docstring | - | 450 |

### tools/hooks/guard_bash.py

hook - reference; imported by 13 file(s): `tools/bench/diag_c106d_jevrc2.py`, `tools/bench/diag_c130_2_baseline.py`, `tools/bench/diag_c144_a2_3_stoprec.py`, `tools/bench/selftest_c103d_hooks.py`, `tools/bench/selftest_c110_launchgate.py`, `tools/bench/selftest_c121_3_gatefp.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `note` | marked, cmd | One line per marked run and per refusal, so audit_cycle.py can count judgement-session bypasses. | docstring | - | 76 |
| `material_gate` | cmd | 0 = pass, 2 = refuse. See the docstring's SECOND RULE. | docstring | - | 90 |
| `motor_gate_check` | cmd | 0 = pass, 2 = refuse. See the THIRD RULE above. Deliberately NOT disabled by LV_GUARD_OFF or BENCH_CELL: | docstring | - | 145 |
| `stop_gate` | cmd, shell=None | 0 = pass, 2 = refuse. One call, no logic duplicated - see tools/stop_record.py. | docstring | - | 327 |
| `prerun_gate` | cmd | 0 = pass, 2 = refuse. The decision lives in tools/stage_prerun.py check_launch() (argv parsing + records). | docstring | - | 364 |
| `scope_gate` | cmd | 0 = pass, 2 = refuse: a launched tools/ script without a valid scope header, or a .py that does not compile | docstring | - | 387 |
| `retro_closes` | cmd, data | True when this retrospective launch really closes the session's cycle (see main). | docstring | - | 402 |
| `next_md5` | status_path | md5 of STATUS.md's '## NEXT' section (stripped), or '' when the file/section is missing. | docstring | - | 430 |
| `next_json_state` | root | (md5 of tools/bench/next.json bytes / 'absent', why-invalid / None). Session protocol v1 C7: the machine copy | docstring | - | 441 |
| `next_gate` |  | Refuse a retrospective launch until the cycle has written a NEW, VALID 'tools/bench/next.json'. | docstring | - | 456 |
| `jev_advisories` | cmd, data | ADVISORY ONLY. Returns the lines it printed (for the self-test); main() ignores them. Never raises. | docstring | - | 545 |
| `main` |  | RETRY CAP (user 2026-09-24, card chat-D). This hook only CHECKS the cap (prerun_gate -> check_launch). It no | docstring | - | 583 |

### tools/hooks/guard_card.py

hook - reference; imported by 4 file(s): `tools/bench/selftest_c111c_launchunit.py`, `tools/bench/selftest_c116a_landed.py`, `tools/bench/selftest_errorlist_reuse_81.py`, `tools/hooks/guard_bash.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `log` | line | (undocumented) | - | - | 27 |
| `pure_selftest` | cmd | True only for THIS project's tools/stagexec.py (relative 'tools/stagexec.py' or its absolute path), and a | docstring | - | 67 |
| `decide` | payload | (exit_code, message). Shared by main() and guard_bash.py. | docstring | - | 107 |
| `main` |  | (undocumented) | - | - | 132 |

### tools/hooks/guard_cycle.py

hook - reference; imported by 29 file(s): `tools/bench/c19_close_release_probe.py`, `tools/bench/c20_release_probe.py`, `tools/bench/c22_v1_gate_probe.py`, `tools/bench/chk_fixed_c69.py`, `tools/bench/diag_c112c_release.py`, `tools/bench/diag_c129_8_pagate.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `review_time` | path, body | (instant, basis) - the moment the review's findings existed, which a fix must post-date. | docstring | - | 99 |
| `fixed_citations` | path, body | (slugs, cited_paths, rejected) for the VALID 'FIXED:' lines of one review. | docstring | - | 126 |
| `fixed_claim` | path, body, target | (claimed, released, why) for ONE file cited by ONE review - CLAUDE.md:449's conditions, per citation. | docstring | - | 170 |
| `fixed_slugs` | path, body | Slugs released by a VALID 'FIXED:' line, and the rejected lines with the reason each was rejected. | docstring | - | 216 |
| `released_slugs` | path, body | (released, rejected) - the ONE definition of "which slugs does this review file release?". | docstring | - | 231 |
| `stamp` | p | A timestamp a BULK EDIT cannot inflate (user's instruction, 2026-09-16: "고칠 것") - and that a RE-ARCHIVE | docstring | - | 273 |
| `newest_build_log` |  | (undocumented) | - | - | 323 |
| `newest_retrospective` |  | The newest retrospective THAT ACTUALLY RETURNED AN ANSWER. | docstring | - | 339 |
| `running_review_recipes` | body | card chat-P1 1(c): the normcase'd absolute recipe paths the LAST 'BGRUN START' line of a prior-art log names with | docstring | - | 366 |
| `recipe_named_logs` | fp | card 148-a1-1 (fp-59): BENCH logs the recipe ASSIGNS as its own log ('LOG = ...'/'RUN_LOG = ...' holding a string | docstring | - | 383 |
| `premature_build` | cmd | THE DEVICE FOR 'premature-build' (docs/violation-decisions.md, 2026-09-16 19:16, round 3). | docstring | selftest_guard_cycle_fixed.py | 410 |
| `block` | msg | (undocumented) | - | - | 648 |
| `offline_only` | cmd | card 112-1 T6: True when EVERY segment of 'cmd' that BUILD_RE matches is 'stage_prerun.py --dry/--prerun' | docstring | - | 653 |
| `main` |  | (undocumented) | - | - | 665 |

### tools/hooks/guard_peer.py

hook - reference; imported by 27 file(s): `tools/bench/c125_1_probe.py`, `tools/bench/diag_c131_2_offline.py`, `tools/bench/diag_c144_3_check.py`, `tools/bench/diag_c146_a1_1_repro.py`, `tools/bench/diag_c160_d4_1_gate.py`, `tools/bench/jev_gate.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `report_waiter_only` | cmd | (undocumented) | - | - | 103 |
| `log_failure` | text, mtime=None | (failed, first failure line) for the LAST run of a WHOLE log text - protocol.log_verdict with this hook's | docstring | - | 168 |
| `log_failure_file` | path | (undocumented) | - | - | 202 |
| `script_touches_labview` | script, _seen=None | v2 (card 131-2): True when the LAUNCHED 'script' can open LabVIEW - rules in the block above. FAILS CLOSED. | docstring | - | 390 |
| `script_touches_labview_v1` | script, _seen=None | v1, KEPT for comparison only (diag_c131_2_offline.py): True when 'script' (a path) or any PROJECT module it | docstring | - | 407 |
| `selftest_exempt` | start_line | True when a bgrun START line's run is a PURE-PYTHON self-test: every in-scope script in python command position | docstring | - | 437 |
| `in_prediction_scope` | start_line | True when a bgrun START line's command runs a tools/recipes/*.py or tools/bench/*.py script (not a Jev one). | docstring | - | 471 |
| `is_jev_ledger` | p | True for tools/bench/jev_*.log/.jsonl (BENCH resolved at call time, so a self-test's redirected BENCH counts). | docstring | - | 493 |
| `newest_failing_log` |  | (undocumented) | - | - | 501 |
| `superseded_by_rerun` | path, mtime, last | gate-fp fp-16 (card 130-2): a failing log whose LAST run's command is IDENTICAL (byte for byte after bgrun's | docstring | - | 570 |
| `offline_command` | cmd | True when every python script 'cmd' launches (protocol._launched_scripts) is the bgrun wrapper, an OFFLINE_MODES | docstring | - | 604 |
| `offline_new_problem` | ladder_line, text | gate-fp fp-44 / fp-46 (card 146-a1-1): '<script> labview none / hardware none' when 'ladder_line' is a JEV-LADDER | docstring | - | 638 |
| `offline_card` | payload, cmd | The card id when the CALLER is a sub-agent bound to a task/1 card with flags.labview == 'none' and 'cmd' is | docstring | - | 666 |
| `offline_cmd_lv_card` | payload, cmd, log_path | gate-fp fp-10 (card 125-1), the REVERSE of offline_card: (card id, labview flag) when the caller is bound to a card | docstring | - | 684 |
| `other_card_log` | payload, log_path, text=None | card chat-E3 (fp-36): (caller's card id, owner card id) when the caller is bound to a card and the failing log was | docstring | - | 707 |
| `failure_names` | path, text | The names a peer exchange must mention to count as a review OF this failure: the log's basename and every | docstring | - | 727 |
| `review_quality` | body | (ok, reason) - why this archived exchange does or does not count as a failed-prediction review. | docstring | - | 770 |
| `newest_bound_peer` | after_mtime, names | A peer archive file newer than 'after_mtime' that names the failure AND counts as a review. | docstring | - | 795 |
| `undisposed` | kind | The newest archived review of 'kind' whose disposition section is missing, empty or still the placeholder. | docstring | - | 838 |
| `log_script` | text | The script name a log's LAST run was started on, '_v\d+' stripped - or None. | docstring | - | 885 |
| `review_subject_scripts` | body | The set of script stems ('_v\d+' stripped) this review was dispatched ABOUT - empty when it names none. | docstring | - | 916 |
| `review_names_script` | body, stem | True when this archive's SUBJECT script (review_subject_scripts) is exactly 'stem', '_v\d+' stripped. | docstring | - | 930 |
| `same_row_review` | log_path, text, now=None | (review path, script stem, age in minutes) for the NEWEST accepted review of this failing log's own | docstring | - | 936 |
| `gaterow_advisory` | path | Print and log the per-row verdicts of the failing run. Returns the lines; the caller ignores them. | docstring | - | 1025 |
| `cite_same_row` | review_path, log_name, ts | Write 'SAME-ROW: <log> (<ts>)' into the review's disposition section, ONCE per log. | docstring | - | 1056 |
| `warm` | path | '--warm <log>': finish the Jev rungs for this log outside the hook, so their caches answer the retry. | docstring | - | 1154 |
| `main` |  | (undocumented) | - | - | 1169 |

### tools/hooks/guard_session.py

hook - reference; imported by 7 file(s): `tools/bench/selftest_c148_assign_leak.py`, `tools/bench/selftest_chat_p1.py`, `tools/bench/selftest_chat_p2.py`, `tools/bench/selftest_guard_session.py`, `tools/bench/selftest_guard_session_pairing.py`, `tools/bench/selftest_guardcore.py` ...

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `in_cycle` |  | True when env CYCLE_SESSION is set and non-empty (a runner cycle session). Returns bool. | side file | - | 94 |
| `last_context_tokens` | transcript_path | Tokens the chat's last assistant turn sent as input (input + cache creation + cache read), read from the | docstring | - | 98 |
| `chat_context_refusal` | data | (f) The chat's bound: refuse a counted dispatch once its context passed CHAT_CONTEXT_LIMIT. '' = allow. | docstring | - | 123 |
| `session_id` | data=None | data['session_id'], else env CLAUDE_SESSION_ID, else 'unknown', with characters outside [A-Za-z0-9._-] replaced by '_' and cut to 80. Returns str. | side file | - | 138 |
| `state_path` | sid | Path of the session state file tools/bench/session_<sid>.json. Returns str. | side file | - | 146 |
| `load` | sid | Session state from state_path(sid) with defaults dispatches 0 and retro_done False; {dispatches: 0, retro_done: False} when missing, unreadable or not a dict. Returns dict. | side file | - | 150 |
| `save` | sid, d | Writes d as JSON to state_path(sid), creating tools/bench if needed; an OSError is ignored. Returns None. | side file | - | 163 |
| `mark_retro_done` | sid | Called by tools/hooks/guard_bash.py when it sees the retrospective being run in this session. | docstring | - | 172 |
| `card_of_prompt` | prompt | (card dict / None, card abs path / None) for a 'CARD <path>' prompt. An unreadable card -> ({}, path). | docstring | - | 196 |
| `prune_live` | live, now=None | The entries still live: no result_<id>.json newer than the dispatch beside the card, and younger than | docstring | - | 211 |
| `card_writes` | card | (g) flags.write of a card dict as a list; None for an unreadable card ({}), which the caller treats as | docstring | - | 230 |
| `tool_hits` | globs | (g) the STAGE_TOOLS a write-glob list reaches. None (unknown writes) reaches all of them. | docstring | - | 239 |
| `pairing_refusal` | cid, lv, writes, live | (g) refusal text for dispatching card 'cid' (labview 'lv', write globs 'writes') beside the 'live' entries, | docstring | - | 247 |
| `send_message_refusal` | data | (c) NO RESUME BY SendMessage IN A CYCLE SESSION (docs/violation-decisions.md "repeated-failure-class - | docstring | - | 286 |
| `main` |  | PreToolUse hook: BENCH_CELL or unreadable stdin -> 0; SendMessage in a cycle refused (2); counts SendMessage resumes (not to main), Agent calls of COUNTED types and Workflow; outside a cycle the ch... | side file | - | 307 |
| `escalation_refusal` | sub, card, cpath | Refusal text when an escalation-rung dispatch (material-opus-max / material-fable-*) of a card with retry_of_card is routed 'scratch-verify' by stage_prerun.escalation_route; '' otherwise or when t... | side file | - | 357 |
| `cycle_role` |  | (h) '' (legacy / chat) / 'judgement' / 'assign' - only inside a runner cycle session. | docstring | - | 379 |
| `decide` | sid, sub, ti, data=None | The counted-dispatch decision, run under the session-state lock. 0 allow / 2 refuse. | docstring | - | 400 |

### tools/hooks/guard_write.py

hook - reference; imported by 6 file(s): `tools/bench/diag_c146_a1_1_repro.py`, `tools/bench/prep_c164_a2_1_pins.py`, `tools/bench/prep_c165_a2_1_close.py`, `tools/bench/replay_c_e3_142_143.py`, `tools/bench/selftest_c148_guard_fp.py`, `tools/bench/selftest_c_e3.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `resumed_card_ids` | names | card 148-a1-1 (fp-57): ids of cards a LATER card took over - a task card that HAS a result file and names the id in | docstring | - | 49 |
| `open_card_pins` | path | ['card <id> pins <rel> at <md5>, disk is now <md5>'] for open cards (no result file yet) whose inputs name | docstring | - | 77 |
| `check_script` | path | (undocumented) | - | - | 131 |
| `check_json` | path | (undocumented) | - | - | 151 |
| `check_review` | path | (undocumented) | - | - | 177 |
| `decide` | path | [problems] for one written file (empty = clean). | docstring | - | 202 |
| `capabilities_regen` | path | 'started' / 'rerun-flagged' / 'not-shared' / 'no-cache' / 'spawn-failed: ...' for one written path (module comment above). | docstring | selftest_t7_capabilities.py | 228 |
| `main` |  | (undocumented) | - | - | 270 |

### tools/hooks/guardcore.py

hook - reference; imported by 3 file(s): `tools/bench/selftest_guardcore.py`, `tools/hooks/adapt_claude.py`, `tools/hooks/adapt_codex.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `event` | backend, tool_name, kind, command='', shell=None, timeout_ms=None, background=False, paths=(), content=None, cwd=None... | A normalized event dict. paths = [{"op": add/modify/delete/rename/write/edit, "old": p/None, "new": p/None}] | docstring | - | 86 |
| `vi_family_ban` | ev | R1: reason or None. | docstring | - | 113 |
| `originals_ban` | ev | R2: reason or None. | docstring | - | 123 |
| `runner_globs` |  | never_in_runner_globs from tools/bench/assign/assign_config.json + RUNNER_EXTRA_GLOBS (unreadable: tools/hooks/**). | docstring | - | 131 |
| `runner_hook_ban` | ev | R3: reason or None. Only when the session is a runner cycle session (CYCLE_SESSION set). | docstring | - | 141 |
| `labview_running` |  | True when the LabVIEW process image is in tasklist (or GUARDCORE_ASSUME_LABVIEW=1). Read-only process list; | docstring | - | 163 |
| `labview_launches` | cmd | [(rel path, labview level)] of tools/ scripts this command RUNS whose scope header says labview read/build. | docstring | - | 176 |
| `concurrency_ban` | ev, probe=None | R4: reason or None. | docstring | - | 185 |
| `call_guard` | modname, payload, env=None | (rc, reason) of one existing hook's main() on 'payload'. rc 2 = deny. An exception inside the guard is reported | docstring | - | 216 |
| `claude_payload` | ev, tool_name, tool_input | (undocumented) | - | - | 253 |
| `judge` | ev, probe=None | ('allow' / 'deny', reason). The order: own path rules (R6, R1-R3), then the existing guards, then R4. | docstring | - | 276 |
| `log` | ev, verdict, why | One line per decision (tools/hooks/guardcore.log). Never raises. | docstring | - | 320 |

### tools/hooks/report_gate.py

hook - reference; imported by 2 file(s): `tools/bench/selftest_report_gate_fp31.py`, `tools/wait_runner_event.py`

| function | arguments | what it does | from | self-test | line |
|---|---|---|---|---|---|
| `newest_runner_log` |  | (undocumented) | - | - | 39 |
| `logs_to_read` |  | fp-31 (cycle 135): the supervisor relaunches the runner at its budget, and the OLD runner then writes its last | docstring | - | 55 |
| `events` |  | (newest log, [(md5, line), ...]) over every log logs_to_read() names; a line seen twice counts once. | docstring | - | 76 |
| `load_ack` |  | (undocumented) | - | - | 92 |
| `unreported` |  | (undocumented) | - | - | 96 |
| `decisions_block` | path=None | The OPEN user decisions (tools/bench/decisions_pending.json, schema decisions-pending/1) that every cycle-end | docstring | - | 102 |
| `ack` |  | (undocumented) | - | - | 123 |
| `main` |  | (undocumented) | - | - | 132 |

<!-- GENERATED fn-list END -->
