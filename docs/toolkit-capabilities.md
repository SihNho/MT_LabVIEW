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
| `loop_in('for'|'while', target, diagram, location, src_cls, src_i, [names], [indexing], parallel)` (WRITER) | `OpForLoopIn_v0` / `OpWhileLoopIn_v0` | a loop on ANY diagram (Traverse index), input tunnels from a node's named outputs, static parallel instances — the nesting the stage-2 kernel loop needs | `test_oploopin.log` 6/6 (nested For and While; a control wired through two borders → one tunnel per border) | 0.1 s |
| **wiring a For loop's N by script** = `connect_terminals(target, loop_node, 0, src_node, src_term)` | existing `OpConnect` route | an EMPTY For loop's `Node.Terminals[]` has exactly one entry (unnamed sink) = the count tunnel's outside terminal; an I32 source wired onto it makes the loop runnable. Verify by the same wire uid on both terminals (`node_terms`) + ExecState 1. `Create For Loop`'s Control Names does NOT wire an existing control (measured) | `build_harness_copyloop2.log` run 2 (wire 346 on both ends, ExecState 0→1); functional in `run_copyloop_bench.log` | 0.1 s |
| **`replace_object(target, uid, new_path)`** (WRITER, callee swap; card 75-4, 2026-09-25) | `OpReplaceGObj_v0` (md5 `a3723240…`; donor OpOwnerChain_v1 + Invoke `GObject.Replace` 632A402 (Path) → `GObject.UID` 632A813 → Close Reference on the returned ref; built by `tools/bench/diag_swap_build.py`, labels `tools/bench/swap_verb_75_oplabels.json`) | swaps the VI a subVI node calls, IN PLACE. MEASURED on a scratch of `D1_s1_copy.vi`, #6810 → byte copy under a new name: **node uid CHANGES** (6810 → 23006; returned as `new_uid`), every wire kept (name-keyed edge diff with the node remapped = ∅; raw term uids 16 renewed), callee census diff = that node only, ExecState 1. `computation_diff(S1, swapped)` = **9 rows**, all from the uid change (cdiff keys nodes by uid, `tools/vigraph.py:205`). `SubVI.Replace` 635E001 NOT needed/not tried | `tools/bench/swap_verb_75.log` 13/0; build `swap_verb_75_build.log` 8/0 (cold ExecState 1) ; 20 back-and-forth swaps clean, handles range 38 | ~1 s |

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
| `for_loop(target, loc, tunnels=[labels], indexing=[...])` | `OpForLoop_v1` | For loop with input tunnels from EXISTING controls, auto-indexed when asked (an ARRAY control; a scalar silently stays regular); an indexed input alone sets N | row 39 |
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
| **`OpConnectNested_v0.vi`** (`vi path`, `Class Name`='Diagram'/**`index`** = the diagram, **`index 2`/`index 3`** = SINK `Nodes[]`/`Terminals[]`, **`index 4`/`index 5`** = SOURCE `Nodes[]`/`Terminals[]` — both ends on THAT diagram) — **WRITER** | `Terminal.Connect Wire` **6349C03**. Donor = **`OpConnect2_v0`** (chosen by `archive/peer/2026-09-17-priorart-connect-nested.md` B3-i over §11m's named `OpStopFromNode_v0`, which is **loop**-anchored and cannot express a diagram index): its nested SINK ladder `Traverse('Diagram')[index] → To More Specific Class → Nodes[] → IA → Terms[] → IA` is kept, its source head `VI[Block Diagram 23C]` is **deleted**, and the same TMSC's `specific class reference` is **branched** into the source `Nodes[]` node | **wires two terminals addressed purely by INDEX on a NESTED diagram** — the only route to a terminal with **no name**, which `gscript.wire` / `wire_control` (name-addressed, 5001 from `Get Controls.vi`/`Get Outputs.vi`), `connect_terminals` (both ends TOP-LEVEL) and `connect2` (top-level SOURCE) all miss. Built 2026-09-17, `tools/recipes/build_opconnectnested_v0.py` | **BUILT + WIRE-IDENTITY VERIFIED, NOT ExecState-verified — say it exactly.** Build 10/1 (`tools/bench/build_opconnectnested_v0.log`, ExecState 1, saved, 14 234 B); test 7/1 (`tools/bench/test_opconnectnested_v0.log`): body→body on a nested diagram **wire 0 → 206, same uid on both ends**, and an **UNNAMED** terminal of a body node reached by index, also w206 (a BRANCH, so `wire delta 0` is expected). 🔴 The scratch read **ExecState 0** — the test paired `error out` into a `path` input and a fresh While loop's unwired conditional terminal is a broken VI by itself (`build_opstopfromnode_v0.py:438-441`), so the ExecState gate was invalid; peer `connectnested-t2b` | ~0.2 s |
| ✅ **`OpConnectNested_v1.vi`** (`vi path`, `Class Name`='Diagram'; SINK = **`index`**/`index 2`/`index 3` = diagram/`Nodes[]`/`Terminals[]`; SOURCE = **`index 6`**/`index 4`/`index 5` — **a DIFFERENT diagram**) — **WRITER** | `Terminal.Connect Wire` **6349C03** with **TWO** independent `Traverse('Diagram')[i] → To More Specific Class → AbstractDiagram.Nodes[] → IA → Node.Terms[] → IA` ladders. Built **additively on `OpConnectNested_v0`**: the single TMSC's output net is deleted, a **TYPED SEED** refnum control is made by `Terminal.Create Control` **on the source `Nodes[]` node's own `reference`** (so its class is that node's by construction, never a typed string), a **second `To More Specific Class`** is brought in with `copy_by_index` from the NI example `Navigating Nodes and Wires.vi` (`Function[6]`, uid 99 — the route `build_opconstvalue_v1.py` proved), and a second `Index Array` on the same Traverse `References` array carries the source-diagram index | **wires two terminals by INDEX on two DIFFERENT nested diagrams.** LabVIEW creates the border tunnels itself (`LoopTunnel 0 → 2`, wire delta 3), so the sink and source wire uids **differ** — a cross-boundary wire is several segments. Built 2026-09-17, `tools/recipes/build_opconnectnested_v1.py` (run 1 died on a Python `TypeError` in the recipe's own hook; run 2 **31 pass / 1 fail**, the one failure a test-harness stale diagram index) | ✅ **FUNCTIONAL, WARM AND COLD — `tools/bench/test_opconnectnested_v1_cold.log`, 7 pass / 0 fail** in a RESTARTED LabVIEW: cold `ExecState 1`, 14 666 B, two casts, `index 6` present; body(A) `error out` → body(B) `error in (no error)` across diagrams, op error `''`, sink w268, and the wire **SURVIVES `remove_bad_wires_scripted`** — 🔴 **THIS SENTENCE IS WRONG ABOUT ITS OWN IMPLEMENTATION, corrected 2026-09-17** (`docs/d1-build-plan.md` §11u.1, `archive/peer/2026-09-17-rbw-deleted-wires-run9.md`, codex ANSWERED, accepted in full): the "survives RBW" check at `tools/recipes/build_d1_v0.py:1118-1121` IS uid equality — it compares two `Terminal.Connected Wire` 634A000 reads, and `Terminal.Connect Wire` 6349C03 returns nothing, so it measures object identity, not survival. **Do not cite RBW-survival as evidence a wire is good.** Use `ExecState 1` on an otherwise-runnable scratch; the sound reader, `Wire.Is Broken?` **6371004** + `Wire.Terminals[]` 6371003 from a HELD terminal reference, is **NOT BUILT** (`NAMES.md:861-863`) 🔴 **CORRECTED 2026-09-23 — this "NOT BUILT" is STALE, and it is the third copy of a sentence already corrected once on 2026-09-18 at `docs/d1-route-b-plan.md:340-345`.** `docs/NAMES.md:992` records *"`Wire.Is Broken?` 6371004 IS BUILT AND MEASURED, 2026-09-17 — and it never needed a new op"*. The true distinction, which every copy of this sentence has lost: what is built reads **ONE** wire and only **AFTER** a `Terminal.Connect Wire` write (the readback embedded in the connect ops, `docs/NAMES.md:1003-1017`), so it cannot be used read-only and it perturbs the target. **A write-free, whole-VI, per-wire `Is Broken?` census is what is absent** — conceded as genuinely unbuilt by `archive/peer/2026-09-23-priorart-allwires.md` A3, which is also where this correction was raised. Cite the distinction, never the bare "not built"; and an **UNNAMED** For-loop count terminal on diagram P wired from a source on diagram Q, wire **0 → 414**, op error `''`. ✅ **NOW MEASURED IN THE REAL VI** (`tools/bench/build_d1_v0_run9.log`, §11s.2): 8 wires made on the D1 working copy — 7 same-diagram body wires and 1 cross-diagram `D[19] → D[24]` — of which **5 SURVIVED `remove_bad_wires_scripted`** and 3 were deleted by it (`#1359` t4, `#1359` t9, `#29874` t4; two are branches of one `#8885 x*y` net, wire 26189). It moved the re-wire from 35 to **42 of 66**. ✅ **REVISED 2026-09-17: "3 were deleted" is not what was measured.** One of the three (`#1359` t4) ended with a **non-zero** wire (`26189 -> 26412`, `build_d1_v0_run9.log:269`) and was counted as deleted only because the uid changed. The honest statement is **at most 2 of 8 became null and 1 of 8 changed wire identity**; terminal-INDEX drift across tunnel creation is a live, unmeasured alternative (§11u.1) | ~0.2 s |
| 🔴 **SUPERSEDED BY THE ROW ABOVE — the v0 limit was ONE diagram index, not two.** `docs/d1-build-plan.md` §11m specifies "both ends by index on **nested diagrams**", i.e. sink and source on DIFFERENT nested diagrams. That is **not buildable by this fleet** | Two independent nested diagrams need a **second `To More Specific Class`**. Run 1 built the alternative the prior-art review prescribed — a second `Index Array` on `Traverse for GObjects.vi`'s `References` array feeding the source `Nodes[]` node — and **measured ExecState 0**: `References` is an array of **GObject** refs, the property node is **Diagram**-class, and GObject→Diagram is a downcast | So the op ships with the source constrained to the sink's diagram. ⚠️ **"A second TMSC has no creator" is WITHDRAWN 2026-09-17** (prior-art review `archive/peer/2026-09-17-priorart-connectnested-v1.md`, A3-i `contradicted` + B3-i `helper-exists`). Three refutations, all from our own files: (1) `:72` of this file — *"`target class` accepts **any wire of the target type**"* — so it never has to be a class-specifier `Constant`; (2) `tools/recipes/build_opconstvalue_v1.py:165-199` **copied** a TMSC with `copy_by_index` and fed `target class` from a `create_control` seed (`OpConstValue_v1.vi`, 13,499 B, on disk); (3) **`OpExitLoop_v0.vi`, `OpWire_v1.vi` and `OpWireSource_v5.vi` each already carry TWO independent `Traverse → IA → TMSC` ladders** (`tools/bench/probe_opexitloop.log:12-18`: #683 and #788, the latter Diagram-typed, each with its own `Class Name`/`index` pair) — the 6-donor census that concluded otherwise (`diag_connectnested_donors.log`) censused none of those three. What run 1 actually measured is narrower and stands: an **ungated** `GObject` element wired straight into a `Diagram`-class property node is a downcast and reads ExecState 0 | `tools/bench/build_opconnectnested_v0_run1.log` (`W4 ROUTE A wired: ExecState 0`); consequence for D1's 17 `from-tunnel` rows is STATUS OPEN |
| ✅ **`OpConnectFromWire_v0.vi`** (`vi path`, `Class Name`='Diagram'; SINK = **`index`**/`index 2`/`index 3` = diagram/`Nodes[]`/`Terminals[]`; SOURCE = **`UID 3`** = an existing WIRE's uid + **`index 7`** = which terminal on that wire → `UID 2`, `Is Broken?`, `Name`, `error out 2`/`error out 3`) — **WRITER** | `Terminal.Connect Wire` **6349C03** whose `Wire Source` is a terminal taken from `Wire.Terms[]` **6371003**, not from `Nodes[]`. Built ADDITIVELY on `OpConnectNested_v1` (nothing deleted but ONE wire): `UID to GObject Reference.vi` (`vi.lib\VIServer\`) → a THIRD `To More Specific Class` (`copy_by_index` from the NI example, uid 99) fed by a **Wire-typed seed** made with `create_control` on a `"VI Server:Wire"` property node's own `reference` → `Wire.Terms[]` → Index Array → `Wire Source`. The old `Nodes[]`-based source ladder is left in place and DEAD (its `error out`s are unwired, so it cannot poison the Invoke; `index 4/5/6` may stay 0) | **the only writer whose SOURCE need not be a node** — what the 16 `FlatSequenceInnerTunnel` / `LeftShiftRegister` from-tunnel rows need (`d1_tunnel_sources.json`, `d1-build-plan.md` §11t). ✅ It also carries the project's first ORDERED `Wire.Is Broken?` **6371004** readout: the donor already had the reader (#241→#242) but its `error in` was unwired, so it ran before the write and always printed `UID 2: 0` — gate W7b branches the Invoke's own `error out` into it | **BUILT + SAVED 2026-09-17, 16,524 B, ExecState 1; `tools/recipes/build_opconnectfromwire_v0.py`, run 2 42 pass / 1 fail** (`tools/bench/build_opconnectfromwire_v0_run2.log`). ✅ **T1 FUNCTIONAL**: on a scratch, branched an OUTER-diagram wire's source terminal into a node inside a NEW While loop body — op error `''`, sink wire **0 → 229**, **`Is Broken? FALSE`**, `LoopTunnel 0 → 1` (LabVIEW made the border tunnel itself). ✅ **T2a**: on a copy of the real VI it ACCEPTED a source terminal owned by `FlatSequenceInnerTunnel` **#5818** (wire w5812) and created a wire, op error `''`, sink **0 → 1231** — the capability §11s.1 said did not exist. 🔴 **T2c2 FAILED: that wire reads `Is Broken? TRUE`**, and w1231 has **TWO** terminals reporting `Is Source? TRUE` (`SelectorTunnel` #5680, `LoopTunnel` #2497). The sink terminal the op resolved is named **`Bead is good? array out`** — an OUTPUT tunnel — because terminal index 1 came from a census of the RESTRUCTURED copy and was applied to an UNRESTRUCTURED one. Reading under peer review, slug `cfw-t2c2-broken-wire`; **not** diagnosed here | ~0.3 s |
| 🎉 **`OpCreateLocalRead_v0.vi`** (`vi path`, the panel control to bind to, **`Write?`** = Boolean → a new `Local` **in the mode asked for**) — **WRITER** | Built **ADDITIVELY on `OpCreateLocal_v0`** (donor md5 `58275b21…` byte-unchanged — `docs/cycle27-plan.md` Pre-decided 51(h)): the donor's `Create:Local Variable` **6331C02** Invoke is kept whole, and its **`i=5 'Create Local'` SOURCE** — the created object's own reference — feeds a **write-mode `'VI Server:Local'` property node** carrying `Local.Write?` **6355401** (short name `Write?`, Boolean, terminal i=4 = SINK in write mode, SOURCE in read mode), whose value comes from a front-panel Boolean made by `create_control` on that SINK (`ControlTerminal` #434, label `'Write?'` read off the machine). 🎉 **NO `To More Specific Class` anywhere**: the Invoke's own output is already `Local`-class, ordered `Is Broken?` **False** on the reference wire (#339 `reference` ← #306 i=5, wire 390) | **creates a Local Variable ALREADY IN READ MODE** — the one thing S3b needs and this fleet could not do. A Local is born WRITE (`is_source` False), while `#10407` t0/t2 are SINKs fed from SOURCEs, so their replacements must READ (Pre-decided **52(a)**, measured off `c53_row_class.json` + the rewire JSON + `main_vi_nodeterms.json`, all three agreeing). Built 2026-09-21 by `tools/bench/diag_c61_localdir_write2.py`, after the same cycle repaired `build_property`'s **mode-blind post-condition** — it asserted write items against `Outputs`, where an input can never appear, and refused the known-good 6355400 identically (`tools/gscript.py`, +37/−2, 5/5 self-test + the `VI Server:VI` 242 regression unchanged) | **BUILT + SAVED + FUNCTIONALLY EXERCISED 2026-09-21**, md5 `f695d97a36ae127cd2dd3ca6b1fc1089`, 10,192 B, LV2026 `26 00 80 00`: `ExecState` **1 at the save and 1 COLD** in a freshly restarted LabVIEW (`tools/bench/diag_c61_localdir_write2.log`, **38 pass / 0 fail**). On a scratch of `D1_s3a_focus_ind.vi`: `Write?`=False → Local **#23507** bound to **`'index'`** (hex `696e646578`), **`is_source` True = READ**; `Write?`=True → **#23508**, `'index'`, **False = WRITE** — the Boolean steers the mode; both error clusters `(False, 0, '')`, census 8→9→10, refs 26/26/**0 live**, four md5 pins PASS before and after. ⚠️ The `Write?` wire itself has **no `Is Broken?` route** here (its source is a panel object; the reader addresses sources as `Nodes[]` positions) — `ExecState` 1 COLD covers every wire in the VI and is the stronger statement, **52(g)**: no reader is built | ~0.05 s/call (20 calls in 0.9 s) |
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

## `tools/stagekit.py` — THE STAGE-SCRIPT SKELETON AS A LIBRARY (built 2026-09-22, Pre-decided 103)

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

## The rule this file encodes

Before a plan depends on a capability, it must name **where that capability was last exercised**. If the answer is
"it is in the list" or "the library ships a VI called that", the plan has an untested assumption in it and should say
so out loud — as a gate, with a cheap test scheduled before the work that depends on it.
