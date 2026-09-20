# priorart-priorart-d1-build-rev4

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $6.6714  in 66 / out 37769 / cache-create 258597 / cache-read 6281687  (545s, 45 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (548s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PRIOR-ART REVIEW (trigger: new-op).

You are checking ONE thing: has this already been done here? Do not review the plan's merits -
other reviews do that. Answer in two parts, naming a FILE and LINE for every finding. A finding without a citation
cannot be acted on, because the only way this review is released is by someone opening your citation and showing in
writing that it does not cover their case.

PART A - THE DIRECTION (this is the part that matters most)
 A1 SETTLED ALREADY. Has this direction, or its central question, already been decided or answered in STATUS.md,
    docs/ or archive/? Quote the decision and its date.
 A2 REFUTED ALREADY. Has this direction already been tried, abandoned, or argued against - in an archived peer
    review, a retrospective, or a superseded plan section? Say what killed it and whether that still applies.
 A3 CONTRADICTED. Does any fact the plan cites conflict with something else in these files? Quote BOTH sides. A
    summary line that contradicts its own section 40 lines earlier counts, and has happened here.
 A4 UNREAD EVIDENCE. Which existing document should obviously have been consulted for this direction and clearly
    was not? Name it.

PART B - THE ARTIFACT, if the plan builds or changes one
 B1 ALREADY BUILT. Does an op, recipe, helper or VI already do this, possibly under another name? Check
    tools/gscript.py's functions, tools/recipes/, docs/toolkit-capabilities.md and the claudeDev VI names.
 B2 ALREADY FAILED. Has this exact build been attempted and failed? What did the record say was the cause, and
    does the new plan address that cause or repeat it?
 B3 HELPER EXISTS. Is the plan hand-rolling something the toolkit already provides - indexing, identification,
    wiring, saving, censusing? Name the call.
 B4 ALREADY MEASURED. Has the question this artifact would answer already been measured and written down?

End with machine-readable lines, one per finding:
  PRIOR-ART: settled-already | refuted-already | contradicted | unread-evidence
  PRIOR-ART: already-built | already-failed | helper-exists | already-measured
  PRIOR-ART: novel
`novel` only if none apply. Do not invent slugs.

THESE VERDICTS STOP THE WORK. Any slug other than `novel` blocks the next build until someone opens your citation
and refutes it in writing. So be precise about what your citation actually covers: an over-broad match costs real
work, and a missed one costs a whole build cycle.

=== WHAT IS UNDER REVIEW ===
---
type: plan
status: current
date: 2026-09-17
cycle: 15
kind: build
tags: [d1, delivery, seven-loop, acquisition, tracking, writer, stop, autofocus]
parent: docs/cycle15-plan.md
spec_rows: [pre-rig-master-plan.md 1.1, 1.2, 1.5, 1.7, 1.8, 1.9]
reviewed_by: [archive/peer/2026-09-17-priorart-priorart-d1-build.md, archive/peer/2026-09-17-priorart-d1-build-rev3.md, archive/peer/2026-09-17-priorart-d1-build-rev4.md]
supersedes: []
recipe: tools/recipes/build_d1_v0.py
measured_in: [tools/bench/diag_d1_step0.log, tools/bench/diag_d1_step0_reclass.log, tools/bench/d1_step0_census.json, tools/bench/build_oploopendref_v0.log, tools/bench/loopendref_637.json, tools/bench/diag_stop_save_seam.log, tools/bench/probe_move_into_v0.log, tools/bench/probe_move_ctlterm_v0.log, tools/bench/ctlterm_owners.json, tools/bench/gpu_kernel_v1_fp.json, tools/bench/gpu_n1_deltas.json, tools/bench/drive_original_copy_v3.log]
build_status: BLOCKED at S0 - the transport 짠11b.1 decided (LOCAL variables) has NO creator in the fleet; see 짠0-BLOCKER
---

# D1 build plan ??REV 4. The first slice of the seven-loop VI, inside a COPY of the original

**REV 4, 2026-09-17.** Rev 3 was a reading document that ended in two lists of open decisions (짠11a, 짠11b). Rev 4
**is the build order**: every decision of 짠11a/짠11b is folded into the body where it acts, the move table is
node-by-node against the BEFORE census keys, and the prediction contract carries counts a machine can check. The
recipe written from it is `tools/recipes/build_d1_v0.py`.

Target `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Track_v6_D1_GPU.vi` = a fresh copy of
`Min_Track N beads V6_ParallelLoop.vi` (md5 `2a78e17c449cacdaf5da389818526859`, asserted before **and** after every
run; the original is never opened for writing ??rule 1).

---

## 0-BLOCKER. ?뵶 MEASURED 2026-09-17 ??the transport 짠11b.1 decided cannot be built by this fleet

**짠11b.1 is binding for rev 4 and it rests on a premise that is false on this machine.** Its closing clause reads
*"`restructure-plan-4.6.md:225-226` already adopts locals; **the Local creator exists**."* It does not.

| what was checked | how | result |
|---|---|---|
| a Local creator in the Python API | `grep "^def " tools/gscript.py` (97 functions listed in `docs/toolkit-capabilities.md`) | **none.** `grep -ni "local" tools/gscript.py` returns **one** hit, `:636`, a docstring sentence about bare terminals |
| a Local op VI | `ls user.lib\claudeDev\Op*.vi` ??**97 ops** | **none touches `Local`** |
| a recipe that creates one | `grep -rl "Local" tools/recipes/` | 2 files, both *mentioning* the class (`build_opreportall.py` census, `probe_move_ctlterm_v0.py` prose) |
| the property that would re-point one | `grep -i local docs/vi-server-ids.json` | **no entry.** `docs/NAMES.md:246` carries `Local.Control Name` **6355400 "read/write"** ??a *catalogued* id, and `toolkit-capabilities.md:10-16` says in its own header that an entry in that file is **a candidate, never evidence** |
| a donor Local to copy | `docs/main-vi-panel-map.md:405-415`, the 2026-09-14 sweep | the VI's **8** Locals are bound to `Total Lost Frames` 횞2, `File # Saved`, `Focus Pos (Track)`, `Rot pos (deg)`, `Trans Pos (mm)`, `Picture`, `Color table`. **None** is `stop (end)`, a slice index, a frame counter or a spare Boolean |

So the route is *copy a donor Local* (`copy_by_index`, which lands on the **top-level** diagram) ??`move_in` it to
the loop body ??**re-point `Control Name`**, and the last step has no op. Building one is a **new general-purpose
op**, which `docs/cycle15-plan.md:104` freezes for the duration of D1. This is exactly the shape 짠0d recorded as
*"route (ii) is UNMEASURED, NOT IMPOSSIBLE"*; 짠11b.1 upgraded "not impossible" to "exists" without a measurement.

**Three separate parts of D1 depend on it, not one:**

1. **1.5's wake-up** ??the slice index (짠0b: 1 DBL) and the frame counter written by 1.2, read by 1.5.
2. **The reverse crossing** ??`#10407 t6 ??#12589 ??#11639 ??#637`'s conditional terminal (짠0b), which 짠11b.1
   turns into a Boolean local.
3. **The stop, in all three new loops.** 짠3's rule is that every new loop reads its stop from a terminal **inside
   its own body**. There is exactly **ONE** `stop (end)` `ControlTerminal` (uid 642, control uid 7 ??measured
   `probe_move_ctlterm_v0.log`), and route (i) moves it into exactly **one** loop. The other two need a second and
   third reader of the same Boolean, i.e. a Local. No op creates a `ControlTerminal` either.

**What the fleet CAN build for a cross-loop value, measured:** queues ??4 creators, functionally verified, and a
6-queue lock-stepped core at 162/162 (`docs/stage2-assembly-step-c.md`). That is the only transport with evidence.
Choosing it for the wake-up contradicts 짠5's own reasoning (per-frame traffic for a UI Boolean; a lossless FIFO
where "freshest wins" was wanted) ??**so the choice is a design decision and this plan does not take it**
(CLAUDE.md 짠3). `build_d1_v0.py`'s gate **S0** refuses to run until `TRANSPORT` is set by the judgement session.

---

## 1. The five D1 spec decisions this build is built on

Taken by the judgement session on 2026-09-17 after `archive/peer/2026-09-17-priorart-priorart-d1-build.md`
(10 findings, 0 novel). Quoted so no section re-argues them, and amended where a later measurement overtook them:

| # | decision | amended by | consumed in |
|---|---|---|---|
| 1 | **`#10407` (autofocus, VISA) gets its own loop** ??the case and its VISA session alone in a loop, woken every 25 frames from the tracking loop; its other inputs by the same route and values as today | **짠11b.1** replaced the notifier with locals (no notifier op exists); **짠0-BLOCKER** finds no Local creator either | 짠6 |
| 2 | **Writer = stream AND accumulate** ??1.7 writes each result as it arrives *and* accumulates; at stop it calls the original `save N xyz traces.vi` #6384, so the `.tra` stays byte-compatible | **짠11b.3** adds `#376 save trace.vi` itself to the writer loop ??it *is* the accumulator | 짠7 |
| 3 | **Stop = two nodes and a fourth structure** ??`stop (end)` #7 ??`#11639`, and `stop (end) 2` #19587 ??`#17883` ??`Tunnel #22085` of `CaseStructure #22082`; #22082 is placed explicitly | measured in full, 짠4 | 짠4 |
| 4 | **Structures move by `Make Selection ??Copy Selection ??Paste`**, probed first, never inside the D1 build | **OVERTAKEN BY ITS OWN PROBE, cheaply**: `GObject.Move` with a wired `owner` relocates `CaseStructure #12589` **with its frame diagrams intact** (짠2b, 12/0). The selection/paste op family is **not built**; D1 moves with `OpMoveIn_v0`. "Never probed inside the build" stands | 짠2, 짠5 |
| 5 | **Precondition readers/devices** ??`OpLoopEndRef_v0` (how #637 stops, D1's S4 gate) and bgrun's `-> FAIL` scan | done, 16/0 | 짠4, 짠9 |

## 1a. What is already built or measured, and is therefore NOT re-derived here

| need | what exists | where |
|---|---|---|
| the stop/save seam's 16 terminals, every wire, every other end | measured | `docs/main-vi-stop-and-save.md` 짠4 |
| **the frame loop's conditional terminal and what drives it** | **MEASURED** (not inferred) | same file 짠1; `tools/bench/loopendref_637.json` |
| `save N xyz traces.vi` #6384 on diagram 19 after the loop, 7 of 8 inputs off #637's tunnels | measured | same file 짠2 |
| shutdown frame (diagram 83): IMAQdx Stop/Close, `ASI TG-1000 Close.vi` #29815, IMAQ Dispose | measured | same file 짠3 |
| kernel forward slice = 14 nodes, backward slice = 7 | measured | `docs/frame-loop-wire-graph.md:43-45` |
| producer/consumer core, 6 lock-stepped queues + pool, 162/162 | built | `docs/stage2-assembly-step-c.md` |
| queue / loop / exit_while / shift-register / drop_subvi / delete ops | built, functionally verified | `docs/toolkit-capabilities.md:24-35, 41-44` |
| **reparenting an existing node / structure / ControlTerminal into a new loop body** | **MEASURED 12/0 and 9/0** | 짠2b, 짠2c |
| **a `Local` node** | ?뵶 **NO CREATOR** | 짠0-BLOCKER |
| relocating a plain primitive or subVI call by create-wire-delete | settled, `GObject.Move` "unnecessary" (now superseded by 짠2b, which makes Move the cheaper route) | `docs/decisions.md:19`, `restructure-plan-4.6.md:79-81` |
| GPU vs CPU on the fixture | **MEASURED twice, bit-identical**; k < 10018 ??max \|?x\| 4.857e-07 px, \|?y\| 4.677e-07 px, \|?z\| 1.279e-05 쨉m, **0 exceedances** | `docs/gpu-backend.md` 짠2026-09-17; `tools/bench/gpu_n1_deltas.json` |
| unattended drive of a copy through stages 0??, run, stop, restart | built, 16/16 | `tools/bench/drive_original_copy_v3.py` |
| camera contract writer 쨌 frame accounting subVI #6810 | built / the original's own | `tools/bench/camera_contract.py`; `docs/frame-loop-anatomy.md:47` |
| identify what a mutating op created ??by uid, never a cached Traverse index | recorded remedy | `tools/gscript.py:833-836` |

---

## 2. The three relocation facts the build stands on (all measured, none inferred)

### 2a. What phase P cost, and the two defects it found in itself

Three runs, all stopped in **phase 1** (building `OpMoveIn_v0` from `OpMoveOut_v0`), each for a **measured** cause:
`net_map` returned 4 of `UID to GObject Reference.vi`'s 12 terminals and its VI-reference input is named
`Owning VI` (`diag_u2g_terminals.log`, 5/5); **wire 464 is ONE net** whose collateral sinks `#237`/`#240` were
bared by the delete, pinning ExecState at 0 (`diag_movein_p1_break.log`, 5/5; peer
`archive/peer/2026-09-17-moveinto-p1-execstate0.md`, whose THIRD explanation was right); and the "fresh donor copy"
was the previous run's in-memory artefact, fixed by a **uniquely named working copy per run** plus gate P1z.

The repair in the file now: delete the net, **immediately re-wire** `#237.reference`/`#240.reference` from
`IndexArray #236`, gated by P1b. The judgement decision's literal wording was *"do not delete wire 464"*, which is
not simultaneously realisable ??a sink takes one source and **there is no `Terminal.Disconnect`** in
`docs/vi-server-ids.json`. Same end state; confirmed (짠11a.6).

### 2b. ??A STRUCTURE MOVES WITH ITS CONTENTS ??12 pass / 0 fail, 14 s (`tools/bench/probe_move_into_v0.log`)

| gate | result |
|---|---|
| P0a / P0b | original md5 `2a78e17c449c?? before **and** after |
| P1z / P1b / P1a | working copy is the donor (ExecState 1, Node 15, no U2G); collateral sinks restored on one net from `#236`; `Move.owner` carried by wire 645 from the Diagram cast **#683** |
| P1 | `OpMoveIn_v0.vi` **ExecState 1** ??UID control label **`'UID 3'`** |
| P2a / P2 (CONTROL) | While loop on `Diagram #686` (Traverse index **19**) ??`WhileLoop #1133`, body `Diagram #1170` at index 20; `#8885 Multiply` ??owner `Diagram #1170` ??`WhileLoop #1133` |
| P2b | `Diagram[20]` holds `[8885, 1134]` ??the destination index still names the right diagram |
| **P3** | **`CaseStructure #12589` ??owner `Diagram #1170`, total `Diagram` count UNCHANGED 171 ??171** ??the frames came with it |
| P4a / P4 | 2 junk Invokes (`1145`, `1134`) purged; `Node` 626 ??**627** (+1 = the new loop); `ExecState 0` afterwards, **expected** |
| census | `Wire` 1902 ??**1895** (??), `LoopTunnel` 132 ??**130** (??) |

**Read that census honestly.** The move **cuts** the wires that crossed the old border rather than re-routing them.
So a relocation is not a complete operation: **D1 re-wires every cut connection afterwards** (짠8), and
**`ExecState` is meaningless between moves** ??it is read once, at the end.

Two recorded facts that are not gates: a scratch copy of the original reads **`ExecState 0`** when opened
headlessly, before any edit ??an S-phase gate must not assume 1; and **handles 30,849 ??51,530 in 14 s**
(baseline ??1,500), a growth to attribute by `handle_audit.py`, not a number to panic about.

### 2c. ??A CONTROL TERMINAL REPARENTS ??9 pass / 0 fail, 14 s (`tools/bench/probe_move_ctlterm_v0.log`)

| gate | result |
|---|---|
| Q0a / Q0b | original md5 unchanged before **and** after |
| Q1 | 114 `ControlTerminal`s and 114 `panel_wiring` rows |
| owner class | **all 114 report owner class `Diagram`** ??the free `report_all` pre-filter filtered nothing here |
| **inside the frame loop** | **31 `ControlTerminal`s are owned by `Diagram#639`**, not the 6 짠5a found from wired boundary wires (`642, 3173, 3453, 1924, 4837, 5634, 403, 9306, ??; full list in `tools/bench/ctlterm_owners.json`) |
| **Q3** | **`ControlTerminal #642` ??owner `Diagram#1170`**, self-echo `'ControlTerminal'#642`, total count **unchanged at 114** |
| Q4 | `panel_wiring` still 114 rows, no label lost; the changed row NAMES the object: **`stop (end)` uid 7, wire 6929 ??0** |
| Q5 | `Node` 626 ??627; `ExecState 0` afterwards, expected |

This is the half of `docs/stage2-plan.md:92-94` that reads *"the control's terminal moved into one loop"*. **The
other half ??"and locals in the others" ??is the thing 짠0-BLOCKER says cannot be built.**

?좑툘 **Caveat on identification** (`archive/peer/2026-09-17-priorart-ctlterm-move.md` A3-ii): "every
`ControlTerminal` is a `panel_wiring` row" is two **non-recursive** counts agreeing, not a bijection ??
`Panel.Controls[]` omits tab-page and cluster elements (`tools/gscript.py:640`). Terminal?뭖ontrol identification is
**reported, never gated**.

### 2d. If `GObject.Move` had not answered it (kept as the record; NOT built)

`TopLevelDiagram.Make Selection` **0x6349002** ??`Copy Selection` **0x6349003** ??`AbstractDiagram.Paste`
**0x6375400**, verified with `Selection List[]` **0x6349400**. Not a drop-in, and this is measured: `Make Selection`
takes `Objects[]`, an **array of GObject references**, and the fleet has no Build Array creator
(`grep "^def " tools/gscript.py`), while `create_control` would make an array-of-refnum control whose value cannot
be set over COM. Three new Invoke ops plus a missing primitive constructor = a new op family and its own cycle.

---

## 3. Loop assignment

| loop | is | receives |
|---|---|---|
| **1.1 ACQUISITION** | the **existing** `WhileLoop #637` | `#6810 get buff image-lost frames.vi` (row 1.8 ??REUSED, 짠8), `#22700 IMAQ Write TIFF File 2` **unconditional, exactly as the original has it**, the camera reads, both stop terminals, `CaseStructure #22082`, and every node not named below |
| **1.2 TRACKING** | a NEW While loop on **`Diagram #686`** (Traverse index 19, the frame loop's own holder) | `GPU_kernel_v1.vi` in place of `#5058`, the reseed case `#5540`, the reseed selector chain, the forward-slice nodes that are neither autofocus nor writer, 4 shift registers, 5 `ControlTerminal`s |
| **1.5 FOCUS** | a NEW While loop on `Diagram #686` | `CaseStructure #10407` + `#48 ASI_adjust focus-subvi.vi` + `CaseStructure #12589`, 2 shift registers (one carries the **VISA session**) |
| **1.7 WRITER** | a NEW While loop on `Diagram #686` | `#376 save trace.vi` (짠11b.3 ??it *is* the accumulator), the streaming TSV write, 2 shift registers |
| **1.9 STOP** | ??| paths A and B of 짠4; each new loop stops from a Boolean read **inside** it |

## 4. The stop, measured ??row 1.9

??**`WhileLoop #637`'s conditional terminal is uid 648**, a SINK carrying **wire 3457**, whose single source is
`CompoundArithmetic` **#11639** ??all inside `Diagram #639`. Read by `OpLoopEndRef_v0.vi`
(`WhileLoop.Loop End Ref` **6362C00**, data terminal **`LpEndRef`**), 16 pass / 0 fail
(`tools/bench/build_oploopendref_v0.log`, raw `loopendref_637.json`). The same run read #25380 ??25410 / wire 1737
and #15173 ??15276 / wire 19456.

| path | wiring (measured) | D1 |
|---|---|---|
| **A** | panel `stop (end)` **#7** ??terminal (`ControlTerminal #642`) wire 6929 ??`CompoundArithmetic` **#11639** t2, OR-ed with wire 12070 ??`#12589` t2 and wire 10249 ??`x = y?` #10019 ??**wire 3457** ??**#637 cond. terminal uid 648**; also ??panel indicator `TurnOff` #24423 | stays 1.1. `#11639` stays. `#12589` **leaves** (to 1.5, 짠6), so w12070 becomes a cross-loop Boolean ??**짠0-BLOCKER item 2** |
| **B** | panel `stop (end) 2` **#19587** ??wire 15230 ??`CompoundArithmetic` **#17883** t1 (with w18092 ??`.not. x?` #17837, w18056 ??`x = y?` #22284) ??**wire 15229** ??`Tunnel` **#22085** of **`CaseStructure #22082`** | **#22082 stays on 1.1 with path B intact** ??nothing in the kernel's forward slice feeds it |

**Rule (NI's infinite-loop mistake, `stage2-plan.md:90-94`):** a front-panel Boolean wired in from outside a loop
becomes an input tunnel read **once**. Every new loop therefore reads its stop from a terminal **inside** its own
body. `exit_while` / `OpExitWhile_v0` is verified 5/5 (ExecState 0 ??1, the VI runs and stops) ??**on a fresh VI
whose Boolean control terminal is at the TOP LEVEL**. Here the only `stop (end)` terminal is inside `Diagram#639`
and moves into exactly one loop, so the other two loops need a second reader: **짠0-BLOCKER item 3.**
Shutdown order is **stop the users ??drain ??release**, so no error 1122 (`frame-ownership-design.md:68-72`).

---

## 5. The move table, node by node, against the BEFORE census keys

Keys are `tools/bench/d1_step0_census.json` ??`diagram_43` (**47 nodes**) and `diagram_19` (**5 nodes**), plus
`shift_regs` (**14**), `tunnels` (**132**), `panel` (**114**). Every row's "moves?" is what `build_d1_v0.py`
asserts before and after. Labels are the census's own.

### 5a. Diagram 43 ??the frame loop body (47 nodes)

| census key | label | D1 | why (measured) |
|---:|---|---|---|
| **5058** | `Track N beads four-fold over-kernel-v3.vi` | **DELETED; `GPU_kernel_v1.vi` dropped into 1.2** | the seam (짠8); the GPU kernel shares its pane for 13 terminals (`gpu_kernel_v1_fp.json`) |
| **5540** | Case Structure (reseed) | ??1.2 | per-frame in from SR `#1142` (w1681 ??kernel w505) and SR `#5805` (w6041 ??kernel w5859); feeds `#5058` t0/t7 |
| **9647** | And | ??1.2 | x ??`#10950`; y ??panel control `Auto-Reset` uid 17472 |
| **10247** | Or | ??1.2 | x ??`#10445`; y ??panel control `Reset Tracking` uid 5605 |
| **10445** | Case Structure | ??1.2 | selector ??`#9647`; `Value` ??SR `#11001` (own counter, pair `#7311/#11001`) |
| **10950** | Less? | ??1.2 | x ??`#17289`; y ??`DigitalNumericConstant #10739` |
| **17289** | `min value` (implicit Property) | ??1.2 | **no wired input at all** ??it reads the indicator `#10969` writes, so it must run in the same loop, **after** `#10969` |
| **10969** | Array Max & Min | ??1.2 | t0 ??kernel w121 (`pos in cal image out`); t3 writes indicator `min value` uid 17257 |
| **10757** | Index Array | ??1.2 | t0 ??kernel w121; its `element` (w10990) is the 1.5 payload (짠6) |
| **1359** | For Loop | ??1.2 | forward slice |
| **2222** | Case Structure | ??1.2 | forward slice; t2 ??kernel w505; reads panel `Z/dZ` uid 47 and `Correction Factor` uid 9289 |
| **2626** | Build Array | ??1.2 | t4 ??kernel w505 |
| **6104** | Index Array | ??1.2 | forward slice |
| **8885** | Multiply | ??1.2 | forward slice (also phase P's control arm) |
| **9833** | Index Array | ??1.2 | forward slice |
| **11261** | Build Array | ??1.2 | forward slice; writes indicator `Force (pN) vs Extension (nm) ` uid 8038 |
| **29874** | For Loop | ??1.2 | forward slice |
| **10686** | And | ??1.2 | the every-25-frames schedule; 짠6 evaluates the cadence where the frame counter is |
| **10407** | Case Structure (autofocus) | ??**1.5** | spec decision 1 |
| **48** | `ASI_adjust focus-subvi.vi` | ??**1.5** | with #10407; its `VISA resource name` comes off SR `#4344` |
| **12589** | Case Structure | ??**1.5** | t1 ??`#10407` t6 w9113 (**the reverse crossing**, 짠0b); its w12070 then crosses back to `#11639` on 1.1 |
| **376** | `save trace.vi` | ??**1.7** | **짠11b.3** ??it *is* the accumulator; fed from `Q_res`/`Q_good`/`Q_rmeta`, outputs leave through 1.7's tunnels into `#6384` exactly as they leave #637 today |
| **6810** | `get buff image-lost frames.vi` | **stays 1.1** | it IS the frame source (row 1.8 REUSE); `Image Out` w3040 crosses to 1.2 through `Q_work` |
| **22700** | `IMAQ Write TIFF File 2` | **stays 1.1** | unconditional, exactly as the original has it (짠8 caveat) |
| **11639** | Compound Arithmetic | **stays 1.1** | drives #637's conditional terminal uid 648 via w3457 |
| **22082** | Case Structure | **stays 1.1** | stop path B; nothing in the forward slice feeds it |
| **17883 쨌 17837 쨌 22284 쨌 10019** | Compound Arithmetic 쨌 Not 쨌 Equal? 쨌 Equal? | **stay 1.1** | stop paths A and B |
| **1114** | `WLC function sub.vi` | **stays 1.1 in D1** | its SR pair `#862/#2853` (`F-x out`) is **not** one of the 8 that move; the WLC/display path is **D2 (row 1.6)** |
| **57 쨌 3191 쨌 20474** | Case Structures | **stay 1.1** | not in either slice |
| **2136 쨌 10068 쨌 29240** | Quotient & Remainder 횞3 | **stay 1.1** | not in either slice |
| **3057 쨌 5119 쨌 10382 쨌 11529 쨌 11608 쨌 22703 쨌 23175** | Equal To 0? 쨌 Subtract 쨌 Not 쨌 Less? 쨌 Bundle 쨌 Format Into String 쨌 Strip Path | **stay 1.1** | not in either slice (the TIFF filename chain and frame bookkeeping) |
| **3052 쨌 4580 쨌 30117** | `File # Saved` 쨌 `Rot pos (deg)` 쨌 `Trans Pos (mm)` | **stay 1.1** | panel access nodes outside both slices |

**Count contract: 21 nodes move off diagram 43** (18 ??1.2, 3 ??1.5, 1 ??1.7 = 22 rows, minus `#5058` which is
deleted rather than moved ??**21 moves + 1 delete + 1 drop**). 26 of the 47 stay.

### 5b. Diagram 19 ??outside the frame loop (5 nodes, none moves)

`#637` (the loop itself) 쨌 `#6384 save N xyz traces.vi` 쨌 `#2048 Array Subset` 쨌 `#781 Initialize Array` 쨌
`#27605 Max Trans Pos.vi`. `#6384`'s eight inputs: seven off `#637`'s output tunnels today, the eighth an
`Array Subset` of `total data array out`. In D1 those seven come off **1.7's** output tunnels instead ??same
values, different carrier (짠7).

### 5c. All 14 shift registers ??**8 move, 6 stay**

| right / left | name | right inner ??| left inner ??| D1 |
|---|---|---|---|---|
| `#1147` / `#1142` | `x,y,z array out` | w505 = kernel t4 | w1681 ??`#5540` t5 | **??1.2** |
| `#5796` / `#5805` | `Bead is good? array out` | w5859 = kernel t3 | w6041 ??`#5540` t3 | **??1.2** |
| `#119` / `#2972` | `pos in cal image out` | w121 = kernel t8 | w7429 ??kernel t13 | **??1.2** |
| `#7311` / `#11001` | `Value` | w11389 ??`#10445` t3 | w10763 ??`#10445` t2 | **??1.2** |
| `#4256` / `#4274` | `position [internal units]` | w9113 ??`#10407` t6 | w3947 ??`#48` t4 | **??1.5** |
| `#4334` / `#4344` | `VISA out` | w7337 ??`#10407` t4 | w1731 ??`#48` t3 | **??1.5 ??the VISA session** |
| `#15` / `#51` | `total data array out` | w464 ??`#376` t1 | w3497 ??`#376` t10 | **??1.7 ??the accumulator** |
| `#24` / `#1108` | `error out` | w541 ??`#376` t0 | w4880 ??`#376` t2 | **??1.7 ??the error chain** |
| `#1117` / `#5351` | `LastBufferNumber` | w1109 | w5416 ??`#6810` t7 | stays 1.1 |
| `#862` / `#2853` | `F-x out` | w8319 | w8322 ??`#1114` | stays 1.1 (WLC = D2) |
| `#9018`/`#9025` 쨌 `#15197`/`#15204` 쨌 `#29505`/`#29512` 쨌 `#580`/`#1755` | ??| ??| ??| stay 1.1 |

?좑툘 짠0c of rev 3 said "4 on 1.2" while listing `#862/#2853` as "1.2 (WLC)". **Rev 4 resolves it as 4 + 0**: `#1114`
and its register stay on 1.1, because the WLC/display path is row 1.6 = D2. **Total moved = 8.** Built with
`add_shift_reg` + `wire_sr` (`toolkit-capabilities.md` rows 37??9).

### 5d. Control terminals ??**5 move, and the sixth is the blocker**

| wire | panel object | read/written by | D1 |
|---:|---|---|---|
| 9806 | control `Auto-Reset` uid 17472 | `#9647` t1 | terminal **moves** into 1.2 |
| 10312 | control `Reset Tracking` uid 5605 | `#10247` t1 | terminal **moves** into 1.2 |
| 730 | control `Z/dZ` uid 47 | `#2222` t0 | terminal **moves** into 1.2 |
| 6096 | control `Correction Factor` uid 9289 | `#2222` t5 | terminal **moves** into 1.2 |
| 17287 | indicator `min value` uid 17257 | `#10969` t3 (writer), `#17289` (reader) | terminal **moves** into 1.2 ??both ends go together |
| 10908 | indicator `Force (pN) vs Extension (nm) ` uid 8038 | `#11261` t0 | terminal **moves** into 1.2 |
| 6929 | control **`stop (end)` uid 7** (`ControlTerminal #642`) | `#11639` t2 on 1.1 | **stays 1.1**; 1.2/1.5/1.7 each need their own reader ???뵶 짠0-BLOCKER |

These terminals are inside `Diagram#639` **on purpose** (짠4's read-once rule), and the user flips `Reset Tracking`
during a run ??routing it through a tunnel would change *when* it is read, a computation change, not scheduling.
**The build must plan for 31 terminals on `Diagram#639`, not 6**: the six above are those step 0 could see from a
*wired* boundary wire, and `ctlterm_owners.json` lists the rest. Any terminal left behind whose node moved shows up
in the census diff (짠8) as a wired?뭕are terminal and is re-wired or moved there.

---

## 6. Row 1.5 ??the autofocus loop

* **`CaseStructure #10407`, `#48 ASI_adjust focus-subvi.vi` and `CaseStructure #12589` move to their own While
  loop**, which owns the ASI VISA session's shift-register pair. Nothing on the frame path can block on it ??rule
  1c is satisfied **by construction**, not by being fast enough.
* **Both SR pairs are re-created on the new loop** (`#4256/#4274`, `#4334/#4344`). ?좑툘 Without the second pair the
  VISA session has no carrier at all; 짠5 of rev 2 never mentioned them.
* **Payload width = 1 DBL, measured.** Exactly one of `#10407`/`#48`'s inputs is kernel-derived in the same
  iteration: `#10407` t2 `Index of closest\ncal image slice, bead 2` ??w10990 ??`#10757 .element` ??w121 =
  `#5058 pos in cal image out` (`d1_step0_census.json.payload`, `payload_width` 1). No cluster, no array.
* **The other inputs are NOT kernel-derived** (`focus_other_inputs`, 9 rows): t0 selector ??`#10686 And`
  (the schedule, evaluated in 1.2); t1 `# slices in stack` ??**LoopTunnel #9641, IndexMode 0**, loop-invariant;
  t3/t5 ??`#48`'s own `Outgoing Handle` / `Out position`; `#48` t0/t1/t2 ??Locals `- Inc (PgDn)` `#3529`,
  `+ Inc (PgUp)` `#3560`, `Focus Step (F1)` `#3447`; `#48` t3/t4 ??the two SRs above.
* **Cadence unchanged:** every **25 frames ??3.6 Hz** (STATUS OPEN 2). D1 keeps the schedule and evaluates it in
  1.2, where the frame counter is.
* **Rule 1a:** the case's inputs arrive by the same route with the same values; only *when the case is evaluated*
  changes, which is scheduling.
* ?뵶 **WAKE-UP TRANSPORT ??UNRESOLVED.** 짠11b.1 decided **locals**; 짠0-BLOCKER measures that none can be built.
  The only buildable transport is a **queue**, which contradicts the "freshest wins, never blocks" requirement this
  loop was designed around. `build_d1_v0.py` gate **S0** refuses until judgement sets `TRANSPORT`.
* **#48 is non-reentrant with a SECOND call site on diagram 99** (rev-3 finding A5, `main-vi-panel-map.md:550,:558`),
  so moving uid 48 does **not** make 1.5 the sole owner of the VISA session, and **no `VISA Close` exists**
  (`main-vi-stop-and-save.md:136,:143-145`). **짠11b.2: D1 does not remove original behaviour** ??the display loop's
  call stays, sole ownership is achieved in **D2 (row 1.6)** and is recorded there, and **no `VISA Close` is added
  in D1** (the original has none). F2 therefore does **not** gate on a VISA close.

## 7. Row 1.7 ??the writer loop, streaming AND accumulating

1. **Stream.** 1.7 dequeues `Q_res` / `Q_good` / `Q_rmeta` (lossless FIFO, `decisions.md:24`) and appends one line
   per result to an open file refnum ??the user's requirement verbatim: *"???猷⑦봽???먮낯泥섎읆 ?앹뿉 ??踰???ν븯吏
   ?딄퀬 ?ㅽ뻾 以?怨꾩냽 ?뚯씪???대떎"* (`archive/prose/2026-09-17-d1-d2-explained-r2.md:114`).
   Format (짠11a.4, ours): TSV, one header line, one line per result,
   `buffer_no  t_ms  x_0 y_0 z_0 good_0 ??x_{N-1} y_{N-1} z_{N-1} good_{N-1}`.
2. **Accumulate ??with `#376` itself** (짠11b.3, from rev-3 finding B2). Rev 3 said 1.7 would rebuild the arrays in
   shift registers and called that "same values, different carrier"; B2 showed that is false, because **two of
   `#6384`'s inputs are `#376`'s own outputs** and three more are loop-invariant values through `#637`'s tunnels.
   So **`#376 save trace.vi` moves into 1.7 with its two shift registers** (`#15/#51` total data array,
   `#24/#1108` error chain) and keeps producing exactly what it produces today.
3. **At stop**, after the drain, 1.7's output tunnels feed **`save N xyz traces.vi` #6384 unchanged** on diagram 19,
   in place of `#637`'s tunnels. The three loop-invariant inputs keep coming from the original's own tunnels on
   `#637`; only the `#376`-derived ones change carrier.
4. **Two artefacts per run** ??the streamed TSV and the `.tra`. **N1 is judged on the `.tra`**, because that is
   what the original writes.

## 8. Row 1.8 ??frame accounting, and the seam

**REUSE `get buff image-lost frames.vi` #6810.** It is the frame source itself, already produces `Missed frames?`
and `current image number`, and that number is the buffer number carried in `Q_meta`/`Q_rmeta`. Replacing it would
change computation on the acquisition path for no gain.
**Reconciliation gate (new ??no equivalent in `tools/bench/` or `archive/benchmarks/INDEX.md`):** the writer's
buffer-number series is a strictly increasing subsequence of the acquisition loop's, and `Total Lost Frames` equals
the count of skipped buffer numbers.

`#5058`'s 16 terminals with the object on the other end (`main-vi-stop-and-save.md` 짠4; `census` + `measured`):

| t | terminal | dir | wire | other end | D1 route |
|---:|---|---|---:|---|---|
| 0 | `Bead is good? array in` | IN | 5637 | ??`CaseStructure #5540` t2 | #5540 moves to 1.2 with it |
| 1 | `Image In` | IN | 3040 | ??`#6810 Image Out`; also ??`#22700` t11 | **crosses the border**: the pool slot's image, out of `Q_work` |
| 2 | `cross size` | IN | 373 | ??`LoopTunnel #2580` | loop-invariant ??tunnel on 1.2, **non-indexed** |
| 3 | `Bead is good? array out` | OUT | 5859 | ??`RightShiftRegister #5796` | the SR moves to 1.2 |
| 4 | `x,y,z array out` | OUT | 505 | ??`#2222` t2, `#2626` t4 | 1.2 ??`Q_res` |
| 5, 6, 10 | *(unnamed)* | IN | 0 | bare | stay bare |
| 7 | `x,y,z array` | IN | 5975 | ??`#5540` t6 | with #5540 |
| 8 | `pos in cal image out` | OUT | 121 | ??`#10757` t0, `#10969` t0 | 1.2; `#10757.element` is also 1.5's payload (짠6) |
| 9 | `# of bead 4 packs` | IN | 42 | ??`LoopTunnel #2396` | loop-invariant ??tunnel |
| 11 | `4 pack remainder` | IN | 3512 | ??`LoopTunnel #4432` | loop-invariant ??tunnel |
| 12 | `Array of cal clusters` | IN | 3646 | ??`LoopTunnel #3656` | loop-invariant ??tunnel, **non-indexed** (`IndexMode 0`) |
| 13 | `pos in cal image in` | IN | 7429 | ??`LeftShiftRegister #2972` | the SR moves to 1.2 |
| 14 | `Real-space cosine window` | IN | 3912 | ??`LoopTunnel #3920` | loop-invariant ??tunnel, non-indexed |
| 15 | `Cosine bandpass\nfor Hilbert ` | IN | 4027 | ??`LoopTunnel #4031` | loop-invariant ??tunnel, non-indexed |

**Shape:** 6 loop-invariant inputs through LoopTunnels, 2 per-frame state carriers (SRs), 2 inputs from `#5540`,
the image straight from `#6810`, three outputs (w505, w121, w5859).

### 8a. `GPU_kernel_v1.vi`'s six EXTRA pane inputs

The GPU kernel shares the CPU kernel's pane for the 13 named terminals (`gpu-backend.md:13`,
`tools/bench/gpu_kernel_v1_fp.json`) and adds six of its own. **None exists on `#5058`, so none has a rule-1a
source ??each is a diagram constant with the value the measured harness used:**

| extra input | what it is | value | why |
|---|---|---|---|
| `Function` | the `IMAQ GetImagePixelPtr` node's own REQUIRED `Function` input, promoted to the pane (`build_gpu_kernel.py:111`) | the node's default, as a constant | not a DLL parameter at all |
| `cal_path` | `.cal` path for `mt2_open` | **empty** | ??the DLL falls back to `MT_GPU_CAL` / `mt_track_cal.txt` ??the configuration every measured GPU run used |
| `nb` | bead count for `mt2_track` | **0** | ??the DLL uses the calibration's bead count; the array handle also carries the length |
| `status` / `status_len` | `char*` status buffer and its length | **empty / 0** | with `status_len` 0 the DLL writes nothing |
| `flags` | `mt2_open` flags; bit0 = keep-alive | **0** | the value the 8/8 fixture comparison was measured under |

?좑툘 **Rule-1a statement, so it is not smuggled:** the 13 shared terminals are wired from the same sources with the
same values as `#5058` had ??that is the equivalence D1 claims. The six extras are **new inputs on a new callee**;
their acceptance is **numeric** (N1), not structural. ?뵶 The **whole-fixture** figures are outside `decisions.md:38`
(bead 4, 10 frames of f11805?밼11823 in the all-beads-lost tail, plus one z flip at k1679) ??**STATUS OPEN 16, a
judgement call this plan does not take.** D1 proceeds under 짠11a.1's written assumption that it is acceptable; if
overturned, only the kernel subVI is swapped.

## 9. Queues, names and types (from the proven core, not invented)

`stage2-assembly-step-c.md:21-26` ??**no composite elements**; each direction is lock-stepped queues written by one
producer in one iteration, error-chained so a partial set cannot be published.

| queue | element | type source | bound | overload policy |
|---|---|---|---|---|
| `Q_free` / `Q_work` | IMAQ image refnum (the pool is a queue of refnums, not of slot integers ??step C v2.1) | `IMAQ Create.New Image` sample | **20** (`decisions.md:22`) | full `Q_work` ??skip this read, return the slot in the same iteration |
| `Q_meta` | buffer number, DBL | `#6810 current image number` | unbounded | ??|
| `Q_res` / `Q_good` / `Q_rmeta` | DBL[] / Bool[] / DBL | the kernel's own outputs | unbounded | **lossless FIFO** (`decisions.md:24`) |
| **1.5 wake-up** | 1 DBL (짠6) | `#10757 .element` | ??| ?뵶 **transport unresolved ??짠0-BLOCKER** |

Every enqueue takes a **finite** timeout and its `timed out?` is read (`frame-ownership-design.md:80-83`).
**Slot ledger:** every exit path returns the slot exactly once ??normal completion, kernel error, enqueue timeout,
shutdown, writer error.

---

## 10. Prediction contract

### S ??structural (`build_d1_v0.py`, one run, one log)

| gate | assertion, with counts |
|---|---|
| **S0** | `TRANSPORT` is set to a mechanism the fleet can build. ?뵶 **Unset ??the run STOPS here** (짠0-BLOCKER). Original md5 `2a78e17c449cacdaf5da389818526859` read **before**; `OpMoveIn_v0.vi` present, UID control `'UID 3'`; LabVIEW handles recorded |
| **S1** | the pool + **6 queues** obtained, and the D1 target opens: `Diagram 171`, `Node 626`, `Wire 1902`, `LoopTunnel 132`, `ControlTerminal 114`, `WhileLoop 3`, `Local 8` **before** any edit |
| **S2** | **three** new While loops on `Diagram #686`: `WhileLoop 3 ??6`, `Diagram 171 ??174`; `#637` still exists, still owns `#6810`, `#22700` and `CaseStructure #22082` |
| **S3** | **21 nodes reparented** (18 ??1.2, 3 ??1.5, 1 ??1.7 minus the deleted `#5058`), each verified by `OpOwnerChain_v1` reading `uid ??<body Diagram> ??<the right WhileLoop>`; total `Diagram` count unchanged **by the moves** (structures keep their frames); `#5058` deleted, `GPU_kernel_v1.vi` dropped into 1.2 (`SubVI 98 ??98`) |
| **S3b** | **census diff = the re-wire list** (짠11a.2): `node_terms` of every moving node **before** and **after**; the set that went wired?뭕are is the authoritative list; gate ??that set **??짠8's 13 crossings** and **every member is re-wired** (tunnel, queue or SR) before ExecState is read. **wires cut == wires re-wired** |
| **S3c** | **8 shift registers** created and wired (4 on 1.2, 2 on 1.5, 2 on 1.7); **5 `ControlTerminal`s** reparented into 1.2, total `ControlTerminal` still **114**, all 114 `panel_wiring` labels present |
| **S3d** | whole-array parameters cross **non-indexed**: `tunnels()` reports `IndexMode 0` for `cross size`, `# of bead 4 packs`, `4 pack remainder`, `Array of cal clusters`, `Real-space cosine window`, `Cosine bandpass\nfor Hilbert ` (**6 tunnels**) |
| **S4** | each of the three NEW loops' conditional terminals is written (`exit_while`), and **for `#637` the reader exists**: `OpLoopEndRef_v0` must still read terminal **648 ??wire 3457 ??`#11639`** after the build |
| **S5** | junk Invokes purged (`new_since('Invoke')` empty), `remove_bad_wires_scripted`, **`ExecState 1` warm**, saved; file size recorded |
| **S6** | **cold re-open** in a restarted LabVIEW: `ExecState 1`, `Diagram 174`, `WhileLoop 6`, `ControlTerminal 114`; original md5 unchanged **after** |

`ExecState` means nothing between S2 and S4 ??the moves cut wires (짠2b). It is read at S5 and at S6 only.

### N1 ??numeric, rule 1a

The kernel-harness branch is already measured and is **not re-run**. N1 is the **in-VI** comparison, and the path
must be stated in the report because D1 has no file-replay input of its own: the fixture is replayed through
**1.2 + 1.7** by feeding `Q_work` from `IMAQ ReadFile` in place of the camera (the step-C v2 replay shape,
`stage2-assembly-step-c.md:22-24`) on a **scratch copy of D1**, never on D1 itself. Gate: the `.tra` against the
original's, **first 10,018 frames** within `decisions.md:38`; the **whole-fixture** figures are reported
**separately** and are STATUS OPEN 16, not a pass/fail.

### F1 ??live, **60 s** (not 5 min)

짠11b.4, against rev-3 finding A3: `cycle15-plan.md:77` says ??5 min, but `#22700` writes a **1.3 MB TIFF per frame
??118 MB/s at 90 Hz** (STATUS OPEN 18), so 5 min ??**35 GB**. **60 s ??4 GB, deleted in the same run**, proves the
plumbing; the 5-minute run is scheduled once the user decides how the harness handles TIFF writing. Flagged.

Driven by `drive_original_copy_v3.py`'s method (16/16): second COM apartment, never-joined RunThread, **3 picks**
in the Image display (uid 31543, rect 232,500??73,1013), `Done Picking Beads?`, **3 token-gated `choose bandpass`
clicks** via `lv_gui.ps1 -Action clickprobe`, absolute save path into the run folder. Camera only; rig
disassembled, **no beads ??tracking errors without beads are expected and are not a failure**.

Recorded (`pre-rig-master-plan.md:55` ??the list already exists; not re-specified here): frames acquired / tracked
/ written; **the buffer-number series** (1.1's and 1.7's, with the 짠8 reconciliation); `Q_work`/`Q_res` **high-water
marks**; the **slot ledger** (returned == taken); **handles start/end**; the **TSV growing during the run** (size
sampled ??3 times, strictly increasing); every TIFF counted and deleted.
?좑툘 **B3 (rev-3): with no beads the writer may be STARVED, so "the file grows" proves nothing on its own.**
`pre-rig-master-plan.md:269-274` prescribes injecting synthetic results; F1 therefore reports the tracked-result
count beside the file size, and a zero count makes the growth gate **N/A**, not PASS.

### F2 ??stop / restart

`stop (end)` by `SetControlValue` (stops `False` + readback ??run ??one `True` each ??poll values + `ExecState`).
**All four loops exit** (each loop's iteration counter frozen, read twice 2 s apart); **no error 1122**; the `.tra`
is written and **re-openable**; **restart 15 s**; stop again; close **without saving**; scratch deleted; TIFFs
deleted; original md5 unchanged.
?좑툘 **F2 inherits STATUS OPEN 17b**: v3's R11 scored the *restart*, not the stop, so "the stop works" is
**unproven** ??F2 gates on the stop itself, not on the fact that a restart succeeded afterwards.
?좑툘 **No `VISA Close` gate** (짠6/짠11b.2): the original has none and D1 adds none.

---

## 11. OPEN ??what this plan still does not decide

1. ?뵶 **짠0-BLOCKER ??the transport.** 짠11b.1 decided locals; the fleet has no Local creator and no
   `Local.Control Name` writer, and a new op is frozen. It blocks 1.5's wake-up, the reverse crossing, and the
   stop read in all three new loops. The only buildable alternative is a queue, which contradicts 짠6's own
   requirement. **One decision, three consequences.**
2. ?뵶 **Is the GPU's whole-fixture divergence acceptable?** (STATUS OPEN 16.) D1 proceeds under 짠11a.1's written
   assumption; N1 reports both ranges.
3. ?윞 **`#12589`'s placement.** 짠11b.1's "the reverse crossing becomes a Boolean local written by the focus loop"
   reads as *#12589 goes to 1.5*, and 짠5a records it that way; rev 3 짠4 put it on 1.2. If it instead stays on 1.1
   the crossing is a DBL, not a Boolean, and the transport requirement changes.
4. ?윞 **F1 at 60 s vs the user-approved 5 min** (짠11b.4) ??flagged to the user, not silently resolved.
5. ?윞 **Row 1.7 is step 3/4 work placed before step 1's measurement** (`decisions.md:46,:52`;
   `pre-rig-master-plan.md:97`). The user-approved `cycle15-plan.md:28-30` governs; the conflict is recorded.

## 11b-recorded. The reusable trap from step 0

A wire-graph slice mislabels **6 of the 7** backward-slice nodes, because state re-enters through **shift
registers** (`#1147` inner w505 ??`#1142` inner w1681 ??`#5540` t5) and through a **front-panel round trip**
(`#10969` writes indicator `min value` uid 17257; the implicit property `#17289` reads it back, with no wire
between the two ends). `tools/bench/diag_d1_step0_reclass.log:129` is authoritative; **any future slice of diagram
43 must include SR and panel round-trips.** The reseed selector is therefore one cycle-carried chain that runs
through the UI: `#5058 pos in cal image out` ??`#10969` ??indicator `min value` ??`#17289` ??`#10950` ??`#9647` ??
`#10445` ??`#10247` ??`#5540` ??back into `#5058`, and it moves to 1.2 whole.


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-17
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.

Narrative relocated **verbatim** (rule 4): cycle 11??3 ??`archive/2026-09-16-status-cycles-11-13-narrative.md`;
D0 + GPU ??`archive/2026-09-17-status-d0-and-gpu-narrative.md`; **cycle 15's long forms (incl. 짠10/짠10a, step 0) ??
`archive/2026-09-17-status-cycle15-narrative.md`**. Open one only when a line here is ambiguous.
?좑툘 **ONE SESSION AT A TIME** ??**re-read `CLAUDE.md` and this from disk.**

## START HERE

1. **`docs/pre-rig-master-plan.md` is THE plan**; settled decisions **`docs/decisions.md`**; cycle plan
   `docs/cycle15-plan.md`; **the build plan is `docs/d1-build-plan.md` REV 3 ??read 짠0-MEASURED then 짠0-REVIEWED**.
2. ??Prior-art gate live (`REFUTED:` / `FIXED:`); `premature_build` (b) exempts a RE-RUN (OPEN 22).
   ??Retrospectives 10??4 done; `retrospective.py` **v2**.
3. ??**Scripting EDITS are silently declined until the target's FRONT PANEL has been opened** ??`ensure_loaded()`.
4. ??**A fixed op PATH is served from LabVIEW's memory, not from disk** ??unique working-copy filename per run.

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  owner:
  since:
  purpose:
# 2026-09-17 05:3x-06:1x material/cycle15-d1-build: RELEASED. Two runs, both md5 2a78e17c449... before AND after:
# diag_d1_step0 12/12 (35 s, read-only, LabVIEW restarted first 51,220 -> 37,290) + offline reclass 8/8; then
# probe_move_ctlterm_v0 rev 2 9/0 (14 s) on SCRATCH_d1ctlterm_*, created and deleted in the same run. No edit to
# any original, no GUI, no hardware. ?좑툘 HANDLES 34,113 -> 54,690 again (+20,577) - restart before the next batch.
# 2026-09-17 05:1x-05:3x material/cycle15-movein-rev3: RELEASED. probe_move_into_v0 rev 7c 12/0; md5 asserted
# before AND after; scratch created+deleted in the same run. Earlier holders: the two 2026-09-17 archives, then
# the 2026-09-16 one.
```
**Never assume an instance exited**: `tasklist | grep -i labview`, kill strays. Fresh instances ??1,500 handles;
unique scratch VI name per run, deleted in the same run.

## HARDWARE ??permission follows the RIG STATE. Current state: **遺꾪빐 / DISASSEMBLED ??everything allowed**

| rig state | motors (PI 쨌 rotor 쨌 magnet) | **ASI piezo** | camera |
|---|---|---|---|
| **遺꾪빐 ??disassembled ??WE ARE HERE** | ??| ??| ??|
| 議곕┰ ??assembled | ??| ??| ??|
| ?ㅽ뿕以???experiment running | ??| ??| ??|

?좑툘 **The ASI carve-out is RETIRED** (rule 1b). **Only the user announces a state change**; never infer one, never
ask per incident. Instruments: rotor counter **0** 쨌 magnet full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz,
never write `BinningHorizontal`; **a session open RESETS ROI *and* exposure** ??the acquisition loop applies the
contract itself (`tools/bench/camera_contract.py`). **No beads while disassembled**; fixture work unaffected
(10,043 frames, `archive/bench-2026-09-07-fixture/`).

## Where things stand

**Stage 1 (analysis) CLOSED** ??the seven `docs/main-vi-*` files; raw `archive/benchmarks/INDEX.md` 22??1.
**Stage 2 (assembly) IN PROGRESS**: `Track_v6_CPU_core_v0.vi` 69/69 쨌 `??queue_v0.vi` 162/162 ??**say it exactly:**
bit-identical for the **first 10,018 frames only**, and both are **replay** artefacts (recorded TIFFs, `FOR` loops,
no acquisition, no stop). **THE GAP:** 168 ops, 116 recipes, 219 peers ??**zero runnable experimental VIs**.

## OPEN ??one line each; long forms in `archive/2026-09-17-status-cycle15-narrative.md`

1??, 5, 9??2, 18 ??**all in archive 짠9**: PERIODIC auto-reset ungated 쨌 autofocus CLOSED (every 25 frames ??3.6 Hz)
   쨌 27 undisposed peer archives 쨌 startup drives instruments (blocker at assembly) 쨌 A2 54/54, A3 112/170 쨌 doc
   lint 2/4/3 쨌 **the original writes 1.3 MB of TIFF per frame, ~118 MB/s at 90 Hz ??bound it or the disk fills**.
13. ??**STOP MEASURED**: `#637` cond. term **648 ??w3457 ??`#11639`**; `stop (end) 2` SEPARATE. ??archive 짠1, 짠10.
14. ?뵶 The cycle-15 prior-art review is only PARTLY disposed ??A7/B3 block on purpose (judgement). ??짠2.
   15. ??`bgrun.py --detach` built. 15b. ?뵶 its deadline kill misses an ORPHANED grandchild ??judgement. ??짠3.
16. ?뵶 **GPU whole-fixture divergence is OUTSIDE `decisions.md:38`** (bead 4, 10 frames of the all-beads-lost tail,
   1 flip at k1679); first 10,018 frames **0 exceedances**. **Acceptability is JUDGEMENT.** ??짠4.
17. ??D0 CLOSED, 16/0. 17b. ?뵶 v3's R11 scored the *restart*, not the stop ??"stop works" UNPROVEN. ??짠5.
   20/21. ??**CLOSED 2026-09-17** ??`py tools/violations.py`: **0 slugs awaiting a response**; devices built. ??짠8.
19. ?뵶 **D1 REV 3 REVIEWED ??THE REVIEW STOPPED THE BUILD.** `archive/peer/2026-09-17-priorart-d1-build-rev3.md`
   ($4.56): **8 findings, 0 novel**, disposed ??**A1/A2 FIXED** (= plan 짠0-MEASURED); **A3 A4 A5 B1 B2 B3 ACCEPTED,
   escalated.** The three that change what gets built: **B1** no notifier exists in the fleet (4 queue creators
   only) and new ops hit the freeze; **A5** `#48` is non-reentrant with a **2nd call site on diagram 99**, so 1.5
   is *not* the VISA session's only owner, and **no `VISA Close` exists**; **B2** `#6384`'s inputs are not
   writer-register values and 짠4 places `#376` nowhere. ??plan 짠0-REVIEWED.
19c. ??**STEP 0 DONE, 12/12 + 8/8** (`tools/bench/diag_d1_step0{,_reclass}.log`, raw `d1_step0_census.json`):
   payload **= 1 DBL**; **6 of the 7 backward-slice nodes move with the kernel**, `#6810` stays ??but only under a
   corrected edge model (a wire graph alone says the opposite: state re-enters through **shift registers**, the
   reseed selector runs **through the panel indicator `min value`**). **All 14 SRs tabled ??4 on 1.2, 2 on 1.5
   (one is the VISA session), 2 on 1.7; 짠8 named 2.** ??plan 짠0-MEASURED; archive 짠10a.
24. ??**BLOCKER CLOSED, 9/0 in 14 s** (`tools/bench/probe_move_ctlterm_v0.log`): **`GObject.Move` reparents a
   `ControlTerminal`** ??`#642` ??the new loop body, count unchanged 114, all labels survive, changed row NAMES it
   (`stop (end)` uid 7, w6929 ??0) = the half of `stage2-plan.md:92-94` already planned. **31 terminals sit inside
   `Diagram#639`, not 6.** 24b. ?윞 the other half, a **`Local`** in the loops that do not get the terminal, is
   **unmeasured, not impossible** ("no Local creator" was WRONG, withdrawn; `restructure-plan-4.6.md:225-226`
   already adopts locals). ??짠0d/짠0e.
19b. ??**PHASE P ANSWERED 12/0** ??`GObject.Move` with a wired `owner` reparents `CaseStructure #12589` **with its
   contents** (Diagram 171??71); `OpMoveIn_v0.vi` BUILT (UID control `'UID 3'`). ?좑툘 **the move CUTS border wires**
   (Wire ??, LoopTunnel ??) so D1 re-wires afterwards and `ExecState` means nothing until the end. ??archive 짠10.
22. ??`premature_build` (b) exempts a RE-RUN (4/4). 23. ??handles CLEARED by a restart (51,220 ??37,290).

## NEXT
?뵶 **JUDGEMENT ??the D1 build is STOPPED until these are decided** (read `d1-build-plan.md` 짠0-MEASURED then
짠0-REVIEWED): (1) **B1 what transport wakes 1.5** ??no notifier exists and the freeze forbids new ops, while
lock-stepped queues are built 162/162; (2) **A5 `#48`'s 2nd non-reentrant call site** ??can 1.5 claim VISA
exclusivity, and where does the missing `VISA Close` go; (3) **B2 where `#376` lives** and how `#6384`'s 8 inputs
are fed; (4) **A3 F1 20 s or the user's 5 min** against 118 MB/s of TIFF; (5) OPEN 16 the GPU tail divergence.
**OPEN 24 is now measured, so it is NOT on this list** ??route (i) works; only the `Local` half (24b) is open.
?윟 Then MATERIAL: the D1 recipe against a **rev 4** ??one script, S1?밪6 ??N1 ??F1 ??F2, on a copy in claudeDev.

## Where to look
`CLAUDE.md` 쨌 **`docs/decisions.md`** settled 쨌 `docs/NAMES.md` strings 쨌 `docs/toolkit-capabilities.md` API 쨌
**`docs/d1-build-plan.md` the build, STOPPED** 쨌 `docs/restructure-plan-4.6.md` 쨌 `docs/pre-rig-master-plan.md` 쨌
`docs/diagram-hierarchy.md` 쨌 `docs/gpu-backend.md` 쨌 the three status archives (rule 4).


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Prior-art review complete — read-only, no lock taken, nothing built or run. **7 findings, zero `novel`.** The most costly is B3: the exact failure class that stopped phase P's run 2 (a shared net whose collateral sinks stay behind) is present and **already measured** inside rev 4's own move table, and gate S3b is scoped so it cannot see it.

---

# PART A — THE DIRECTION

## A1 `contradicted` — "the Local creator does NOT exist" is a claim this project formally **withdrew** the same day, and rev 4 reinstates it as the thing that stops the build

- `docs/d1-build-plan.md:14` (frontmatter) — *"build_status: BLOCKED at S0 — the transport §11b.1 decided (LOCAL variables) has **NO creator in the fleet**"*; `:30` — *"the transport §11b.1 decided **cannot be built by this fleet**"*; `:91` — *"| a `Local` node | 🔴 **NO CREATOR** |"*.
- Against it, an **accepted and FIXED** prior-art disposition of 2026-09-17: `archive/peer/2026-09-17-priorart-ctlterm-move.md:601-608` — *"`A3-i` `contradicted` — **a false 'impossible' that I wrote**, caught exactly where CLAUDE.md says to look for one … The citation is **withdrawn** in both files … §0d now reads **'UNMEASURED, NOT IMPOSSIBLE'**."* Its evidence: `docs/toolkit-capabilities.md:263` (`Local` is a valid Traverse class, 8 objects), `docs/NAMES.md:246` (`Local.Control Name` **6355400**) with `archive/peer/2026-09-14-implicit-property-node-linked-object.md:28-29` recording it **read/write**, and `docs/restructure-plan-4.6.md:242-243` (copy-from-donor is the recorded route for a node the fleet cannot create).
- `STATUS.md` OPEN **24b** still carries that correction verbatim: *"the other half, a **`Local`** … is **unmeasured, not impossible** (\"no Local creator\" was WRONG, withdrawn; `restructure-plan-4.6.md:225-226` already adopts locals)"*.
- The plan **knows this** — `docs/d1-build-plan.md:45-46` says *"This is exactly the shape §0d recorded as 'route (ii) is UNMEASURED, NOT IMPOSSIBLE'"* — and then its heading, its frontmatter and its §1a row state the stronger claim anyway. `tools/recipes/build_d1_v0.py:119` hard-codes the stronger one into the machine: `"local": ("create_local", "NONE - no Local creator exists in the fleet")`, so S0 refuses **even after** judgement picks locals.

**Scope:** covers the words "NO CREATOR" / "cannot be built" and the S0 refusal *as written*. It does **not** claim a Local can be created — nobody has measured that either way; it claims "unmeasured" is the recorded state and a build gate may not be keyed to "impossible".

## A2 `contradicted` — "a queue contradicts freshest-wins" is refuted by this project's own transport table

`docs/d1-build-plan.md:76-77` — *"Choosing it for the wake-up contradicts §5's own reasoning (per-frame traffic for a UI Boolean; **a lossless FIFO where 'freshest wins' was wanted**)"*, repeated at `:470-471` (OPEN 1: *"The only buildable alternative is a queue, which contradicts §6's own requirement"*).

`docs/restructure-plan-4.6.md:55`, the inter-loop transport table: *"| 2 → 6 | **local variable / 1-element queue** | lossy by design; the display only needs the newest |"* — a queue and a local are recorded **as alternatives for the same latest-value duty**, not as opposites.

**Scope:** covers only the claim that a queue is *necessarily* the wrong semantics. It does not say a 1-element queue is right here, and it does not touch `docs/decisions.md:21` (*"no `Lossy Enqueue Element`"*), which is scoped to the **acquisition** path (the camera must never be gated), not to a 3.6 Hz focus wake-up.

## A3 `unread-evidence` — the transport census never opened the creator library every writer op in this fleet was wrapped from

`docs/d1-build-plan.md:74-75` — *"**What the fleet CAN build for a cross-loop value, measured:** queues — 4 creators … **That is the only transport with evidence**"*, and `:63-71` prices an `OpLocal` family. Four places were checked (`:37-41`): `gscript.py`, `claudeDev\Op*.vi`, `tools/recipes/`, `vi-server-ids.json`. The **donor library** was not.

- `docs/REFERENCES.md:29-30` — LV-Scripting is installed at `vi.lib\Erdos Miller\LV-Scripting\`, **84 VIs**; `docs/stage2-plan.md:110` records that the four queue ops were built by wrapping `Create Obtain Queue / Enqueue Element / Dequeue Element / Release Queue.vi` from exactly that folder.
- That same folder ships `Create Create User Event.vi`, `Create Generate User Event.vi`, `Create Register for Events.vi`, `Create Destroy User Event.vi` and `Create Event Structure.vi` — and the project already recorded one of them as on the shelf: `docs/stage2-plan.md:114` — *"| Event structure (stage 5) | erdosmiller `Create Event Structure.vi` — **not needed in stage 2** |"*.
- The distinction the plan collapses is the one `docs/toolkit-capabilities.md:14-15` exists to enforce (*"an entry … is a **candidate**. Only use counts as evidence"*): **exercised** (queues, 162/162) is not the same set as **buildable**. Neither is `ARCHITECTURE.md:60`'s "no Queue/Notifier primitive appears in the original" an obstacle — the queue ops needed no donor either, only a creator.

**Scope:** covers the sentence "that is the only transport with evidence" only insofar as it is used at `:44` and `:470` to conclude *only a queue is buildable*. It asserts nothing about whether user events are appropriate or cheap.

## A4 `contradicted` — F1's disk budget contradicts its own rate line and a measurement in the plan's own `measured_in:`

`docs/d1-build-plan.md:453-454` — *"`#22700` writes a **1.3 MB TIFF per frame ≈ 118 MB/s at 90 Hz** … so 5 min ≈ **35 GB**. **60 s ≈ 4 GB**, deleted in the same run"*. 118 MB/s × 60 s ≈ **7.1 GB**, not 4 GB — the 5-minute figure uses the rate, the 60-second figure does not.

Measured, in a file the plan lists at `:13`: `tools/bench/drive_original_copy_v3.log:81` — *"`.tif`: (**2041**, **2675689770**)"* = 2.68 GB of TIFF from roughly 22 s of frame loop (`archive/2026-09-17-status-d0-and-gpu-narrative.md:211`, *"frame loop, 20 s … 2 041 TIFFs / 2.68 GB"*). Scaled to 60 s that is ~7–8 GB.

**Scope:** one number, and it matters because F1 is an **unattended overnight** run that deletes in the same run (`STATUS.md` OPEN 18 — *"bound it or the disk fills"*). It does not reopen the 60 s vs 5 min question, which the plan already flags as OPEN 4.

---

# PART B — THE ARTIFACT

## B1 `helper-exists` — the "`Control Name` **writer**" piece is the `OpSetIndexMode_v0` pattern, which is already built twice

`docs/d1-build-plan.md:63-72` prices the Local route as three pieces — a seed, a creator, and *"a `Control Name` **writer**. That is a new op family and its own cycle"*. The writer is the one piece the fleet already owns a working template for:

- `tools/gscript.py:1658-1679` `set_index_mode()` → `OpSetIndexMode_v0`, described at `:1661-1662` as *"Traverse('LoopTunnel', index) -> cast -> IndexMode **WRITE property node** <- 'index 2' control"* — i.e. Traverse a named class by index, cast, write one property from a front-panel control. That is the shape a `Local.Control Name` write takes.
- `tools/gscript.py:2451-2454` `set_node_label()` → `OpSetLabel_v0`, a second property **write** op (`Node.Label` 6359001 → `Text.Text` write).
- Deriving a new op from those front halves is the fleet's normal move, recorded twice: `tools/gscript.py:1690-1692` — `OpTunnelInd_v0` was *"built 2026-09-13 from OpSetIndexMode_v0, whose front half `Traverse(…) -> IndexArray -> To More Specific Class` was **already proven**"* — and `docs/toolkit-capabilities.md:50`, where `OpLoopEndRef_v0` is an *"additive build on OpWhileCast_v0 (nothing deleted)"*, 16/16, done **this cycle**.
- And the rule for a catalogued-but-unexercised id is not a blocker: `docs/toolkit-capabilities.md:549-553` — *"it must name where that capability was last exercised. If the answer is 'it is in the list' … the plan has an untested assumption in it and **should say so out loud — as a gate, with a cheap test** scheduled before the work that depends on it."*

**Scope:** the **writer** piece only. The seed and the creator pieces of `:63-70` are untouched by this, and whether such an op falls under `docs/cycle15-plan.md:104`'s freeze is a judgement call — but "its own cycle" is priced against a template that already exists.

## B2 `unread-evidence` — §0-BLOCKER item 3 assumes three Boolean readers without citing the two stop mechanisms this project already recorded for live mode

`docs/d1-build-plan.md:53-56` — *"**The stop, in all three new loops.** §3's rule is that every new loop reads its stop from a terminal inside its own body … The other two need a second and third reader of the same Boolean, **i.e. a Local**."*

- `docs/stage2-assembly-step-c.md:45` — *"**Live mode (step D) is where the While tracker, an end-of-stream token and a timeout-gated Case are unavoidable**; none of that is built here."* 1.2 and 1.7 are queue **consumers** of 1.1; a token is the recorded live-mode mechanism for ending them, and it needs no second reader of the panel Boolean.
- `docs/frame-ownership-design.md:102-103` — *"A consumer that dies must stop acquisition … First error wins: capture it, **broadcast stop**, let each loop drain and release its own resources."*
- `docs/pre-rig-master-plan.md:95` (row 1.9) states the requirement as *"every loop stops from a Boolean read **inside** it"* and *"**Seven loops need seven stops and one order**"* — it never says seven panel-terminal readers, and `docs/stage2-plan.md:92-94` offers the local/terminal pair as **examples**, not as an exhaustive list.

**Scope:** covers only the inference "three new loops ⇒ three readers of `stop (end)` ⇒ a Local is required". The read-once rule itself (`stage2-plan.md:90-91`) is correct and is not challenged.

## B3 `already-measured` — `#376`'s non-register inputs sit on **shared nets whose other sinks stay on 1.1**, and S3b is scoped so it cannot detect the break that class caused in phase P

`docs/d1-build-plan.md:246` moves `#376 save trace.vi` to 1.7 and describes it only as *"fed from `Q_res`/`Q_good`/`Q_rmeta`, outputs leave through 1.7's tunnels"*. §5c (`:278-279`) tables its two shift registers. **No section tables `#376`'s other inputs**, which are measured:

| wire | `#376` terminal | other sinks on the same net | those nodes in D1 |
|---|---|---|---|
| `docs/frame-loop-wire-graph.md:151` w3268 | t7 `x` | `#2136` t3, `#3191` t1, `#10068` t3, `#1114` t0, `#29240` t3 | **all stay 1.1** (`d1-build-plan.md:251-255`) |
| `:167` w5090 | t11 `selected path` | `#23175` t0 (Strip Path) | **stays 1.1** (`:255`) |
| `:158` w3629 | t6 `cal cluster path` | — | not tabled |
| `:145` w1581 | t9 `file size` | — | not tabled |

This is the exact failure the plan's own §2a records: `docs/d1-build-plan.md:127-131` — *"**wire 464 is ONE net** whose collateral sinks `#237`/`#240` were bared by the delete, **pinning ExecState at 0**"* (`tools/bench/diag_movein_p1_break.log`, 5/5; `archive/peer/2026-09-17-moveinto-p1-execstate0.md`, whose third explanation was right). Its signature is *no broken wire and nothing for Remove Bad Wires* — a silent bare terminal.

And the gate cannot catch it: `docs/d1-build-plan.md:433` (S3b) censuses *"`node_terms` of **every moving node** before and after"*. On w3268 the collateral sinks are on nodes that **do not move**, so they fall outside the census on both passes, and `ExecState` is explicitly not read until S5 (`:440`).

**Scope:** covers §5a's `#376` row, §7, and S3b's census scope. It does not say `#376` should stay on 1.1 — that is a rule-1a decomposition call (`§11b.3`), untouched here.

---

## Checked and cleared — so the next round does not re-derive it

1. **The move-count arithmetic is fixed.** `:258-259` now reads *"17 → 1.2 … 21 moves + 1 delete + 1 drop"*, and `tools/recipes/build_d1_v0.py:147-152` holds 17 / 3 / 1. Rev 3's mismatch is gone.
2. **Rev 3's six escalated findings are all carried, not dropped**: A3→`:451-456` + OPEN 4; A4→`:463` cites `pre-rig-master-plan.md:55` instead of re-listing; A5→`§11b.2` + `:313-316` (no VISA close added, second call site recorded); B1→§0-BLOCKER; B2→`:246`, `§11b.3`; B3→`:468-471`'s N/A rule for a starved writer.
3. **No op is re-invented.** `build_d1_v0.py:105-109` imports `gscript`, `read_owner` (`OpOwnerChain_v1`) and `labview_handles` rather than re-implementing them — the duplication `archive/peer/2026-09-17-priorart-ctlterm-move.md:579` flagged is not repeated.
4. **`#22700` being unconditional is measured, not assumed** — `archive/2026-09-17-status-d0-and-gpu-narrative.md:180-182`: *"no front-panel CONTROL gates the TIFF writer (0/60 labels; uid 22700 sits directly on the frame `WhileLoop`'s diagram, not in a Case)"*.
5. **Not slugged, but worth one edit:** `docs/d1-build-plan.md:10` lists `archive/peer/2026-09-17-priorart-d1-build-rev4.md` under `reviewed_by:` — **this review, which did not exist when the line was written**; `archive/peer/` holds no such file. Since `tools/doc_lint.py` checks that every cited path exists, that line will fail the cycle-close lint. I have left it un-slugged because blocking a build over frontmatter would be over-broad.

---

```
PRIOR-ART: contradicted    (A1 — docs/d1-build-plan.md:14,:30,:91 and tools/recipes/build_d1_v0.py:119 vs archive/peer/2026-09-17-priorart-ctlterm-move.md:601-608 "the citation is WITHDRAWN … UNMEASURED, NOT IMPOSSIBLE", STATUS.md OPEN 24b, and the plan's own :45-46 — covers ONLY "NO CREATOR"/"cannot be built" and S0's refusal keyed to it)
PRIOR-ART: contradicted    (A2 — docs/restructure-plan-4.6.md:55 "local variable / 1-element queue … lossy by design" vs docs/d1-build-plan.md:76-77,:470-471 — covers only "a queue contradicts freshest-wins")
PRIOR-ART: unread-evidence (A3 — docs/REFERENCES.md:29-30 + docs/stage2-plan.md:110,:114 and the installed vi.lib\Erdos Miller\LV-Scripting folder's user-event/event-structure creators vs docs/d1-build-plan.md:37-41,:74-75 — the four-place census omitted the creator library the queue ops came from)
PRIOR-ART: contradicted    (A4 — docs/d1-build-plan.md:453-454 "118 MB/s … 60 s ≈ 4 GB" vs its own 5-min arithmetic and tools/bench/drive_original_copy_v3.log:81 "2041 TIFFs / 2675689770 B" in ~22 s)
PRIOR-ART: helper-exists   (B1 — tools/gscript.py:1658-1679,:1690-1692,:2451-2454 and docs/toolkit-capabilities.md:50,:549-553 vs docs/d1-build-plan.md:63-72 — covers the "Control Name writer = a new op family and its own cycle" pricing only)
PRIOR-ART: unread-evidence (B2 — docs/stage2-assembly-step-c.md:45 end-of-stream token, docs/frame-ownership-design.md:102-103 broadcast stop, docs/pre-rig-master-plan.md:95 vs docs/d1-build-plan.md:53-56 — covers "the other two need a second and third reader of the same Boolean, i.e. a Local")
PRIOR-ART: already-measured (B3 — docs/frame-loop-wire-graph.md:145,:151,:158,:167 (#376 t6/t7/t9/t11 and w3268's five staying sinks) + the plan's own :127-131 / tools/bench/diag_movein_p1_break.log vs docs/d1-build-plan.md:246,:433 — covers §5a's #376 row and S3b's moving-nodes-only census scope)
```

One note for whoever disposes of this: **A1 and B3 are the two that change what happens next.** A1 is cheap — the honest state is "unmeasured", so S0's refusal should be keyed to *"TRANSPORT undecided"* (which is true and is judgement's call) rather than to *"a Local cannot exist"* (which this project withdrew in writing on the same day). B3 is not cheap and is not a wording fix: S3b's census is scoped to moving nodes, and phase P measured that this exact class of break leaves no broken wire to find.

## Sources

(extract from answer)

## What was done with it

Disposed 2026-09-17 by the MATERIAL session `cycle15-d1-build-rev4`. **7 findings, 0 novel. ALL SEVEN ACCEPTED —
none refuted.** Four are FIXED here; three change **which transport D1 uses**, which is a design decision with a
rule-1a consequence, so they are **ESCALATED** (CLAUDE.md §3 — a material session may not take it). Files edited:
`docs/d1-build-plan.md` (§0-BLOCKER rewritten, new §0-BLOCKER.b, §7.2b, §10 S3b, §10 F1), `tools/recipes/
build_d1_v0.py` (S0, `TRANSPORT_CREATORS`, S3b + the new `S3b-collateral` gate), `STATUS.md`.
**The build did not start** — `guard_cycle` correctly refused every build command while this review was live, and
S0 still refuses on the undecided transport. No LabVIEW lock was taken; the original was never opened.

**FIXED — `A1` `contradicted`, and it is the finding that matters most, because the error is mine and it is a
repeat.** Rev 4's frontmatter, heading and §1a row said *"NO CREATOR"* / *"cannot be built by this fleet"*, and
`build_d1_v0.py:119` hard-coded that into the machine. This project **formally withdrew that exact claim about
`Local` the same day** (`archive/peer/2026-09-17-priorart-ctlterm-move.md:601-608`, carried in STATUS OPEN 24b),
and rev 4's own §2 even quotes the correction before contradicting it. The two statements are now separated
everywhere: **MEASURED** = no op creates a `Local` and none writes `Control Name` *today* (a fact about the
fleet's contents); **UNMEASURED** = whether one can be built. `build_status:` now reads *"no creator today"*, and
S0 refuses on **"undecided / creator not built yet"**, never on a capability claim. This is the second time in one
day that a false "impossible" reached a build gate; the trigger sentence in CLAUDE.md caught neither, the peer
caught both.

**FIXED — `A4` `contradicted`.** *"118 MB/s … 5 min ≈ 35 GB … 60 s ≈ 4 GB"* did not use its own rate. The measured
figure is in a log the plan already lists: `tools/bench/drive_original_copy_v3.log:81`, `.tif` **2041 files /
2,675,689,770 B** from a ~20–22 s frame loop ⇒ **≈122 MB/s**, so **60 s ≈ 7.3 GB**, not 4. §10 F1 now carries the
measurement and the free-space consequence (STATUS OPEN 18). The 60 s vs 5 min question itself stays OPEN 4.

**FIXED — `B1` `helper-exists`.** §0-BLOCKER priced the `Control Name` **writer** as *"a new op family and its own
cycle"*. It is the `OpSetIndexMode_v0` shape — *"Traverse(class, index) → cast → WRITE property node ← a control"*
(`gscript.py:1661-1662`) — already built twice (`OpSetLabel_v0`, `gscript.py:2451-2454`), and deriving from those
front halves is this fleet's normal move (`OpTunnelInd_v0` from `OpSetIndexMode_v0`, `gscript.py:1690-1692`;
`OpLoopEndRef_v0` additive on `OpWhileCast_v0`, 16/16, **this cycle**). The plan now prices the writer as **one
additive op against a proven template** and isolates the **creator** as the genuinely unpriced piece.

**FIXED — `B3` `already-measured`, the most expensive one if it had shipped.** `#376`'s non-register inputs sit on
**shared nets whose other sinks stay on 1.1**: w3268 t7 `x` → `#2136 #3191 #10068 #1114 #29240` (all five stay),
w5090 t11 `selected path` → `#23175` (stays). Moving `#376` bares six terminals on nodes that never move, and gate
S3b censused *"every moving node"* only — so the collateral sinks were outside the census on **both** passes,
while `ExecState` is not read until S5. That is precisely the failure that killed phase P run 2 (one net, silently
bared required inputs, nothing for Remove Bad Wires, ExecState pinned at 0). **S3b now walks the net**: it
censuses the moving nodes **plus every node on diagram 43 that shares a wire with one**, tags each cut row
`moved` / `STAYED-BUT-BARED`, and a new gate **`S3b-collateral`** fails the build if any staying node lost a wire.
§7 gains item **2b** with the measured table. Whether `#376` should move at all is §11b.3's rule-1a call and is
**not** reopened.

**ESCALATED — `A2`, `A3`, `B2`: together they dissolve the premise that the transport choice is "local vs queue".**
Each is accepted as fact and recorded in the plan, but choosing among the options is judgement:

* **`A2` `contradicted`** — *"a queue contradicts freshest-wins"* is refuted by the project's own inter-loop
  transport table, `docs/restructure-plan-4.6.md:55`: *"| 2 → 6 | **local variable / 1-element queue** | lossy by
  design; the display only needs the newest |"*. A local and a 1-element queue are tabled as **alternatives for
  the same latest-value duty**. `decisions.md:21`'s "no `Lossy Enqueue Element`" is scoped to the **acquisition**
  path, not a 3.6 Hz focus wake-up.
* **`A3` `unread-evidence`** — the four-place census (`gscript.py`, `claudeDev\Op*.vi`, `tools/recipes/`,
  `vi-server-ids.json`) never opened **the donor library every writer op in this fleet was wrapped from**
  (`docs/REFERENCES.md:29-30`; `docs/stage2-plan.md:110` records the queue ops as wrappers of VIs in that folder).
  **Measured in this session** — `ls "vi.lib\Erdos Miller\LV-Scripting\"`, 85 entries — it ships a **complete user
  event set** (`Create Create User Event` · `Generate User Event` · `Register for Events` · `Unregister for
  Events` · `Destroy User Event` · `Create Event Structure` · `Construct Dynamic Event` · `Get Event Data In` ·
  `Wire Event Data Out` · `Exit Event Structure`) and a **DVR set** (`Create New DVR` · `In Place Element DVR` ·
  `Delete DVR`) — and **no `Create Local.vi`**. So "only a queue is buildable" was false, and the distinction
  `toolkit-capabilities.md:14-15` exists to enforce (**exercised** ≠ **buildable**) had been collapsed. New
  §0-BLOCKER.b tables all five candidates with what is on disk for each.
* **`B2` `unread-evidence`** — *"three new loops ⇒ three readers of `stop (end)` ⇒ a Local"* is an inference that
  ignores two recorded live-mode mechanisms: the **end-of-stream token** (`stage2-assembly-step-c.md:45` — 1.2 and
  1.7 are queue *consumers* of 1.1, so a token ends them with no second panel reader) and **broadcast stop**
  (`frame-ownership-design.md:102-103`). `pre-rig-master-plan.md:95` asks for *"seven stops and one order"*, never
  for seven panel-terminal readers. The read-once rule itself (`stage2-plan.md:90-91`) is unchallenged and stands.

**Also fixed, un-slugged (the reviewer's item 5):** `reviewed_by:` cited
`archive/peer/2026-09-17-priorart-d1-build-rev4.md`, a path that does not exist — the archive prefixes the slug, so
it is `…-priorart-priorart-d1-build-rev4.md`. Corrected; `tools/doc_lint.py` would have failed the cycle close.

**Net effect on the build.** §0-BLOCKER is *weakened but not lifted*: the blocker is no longer "the decided
mechanism is impossible" but **"five candidate transports exist, only one is exercised, and picking one settles
1.5's wake-up, the reverse crossing and the three loops' stop at once."** Everything not downstream of that choice
— the move table, the shift registers, the control terminals, the seam, the census-diff re-wiring, S1–S6 — is
written and ready. **Returned to judgement.**
