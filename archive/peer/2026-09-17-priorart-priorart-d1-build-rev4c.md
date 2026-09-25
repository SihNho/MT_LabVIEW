---
type: peer-review
status: historical
date: 2026-09-17
tags: [peer-review, archive, labview]
disposition: legacy
legacy_note: closed as legacy 2026-09-25 by card chat-L1 (cutoff 2026-09-22; user 2026-09-25 lint order before runner resume)
---

# priorart-priorart-d1-build-rev4c

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $5.0036  in 50 / out 40387 / cache-create 198101 / cache-read 4025301  (544s, 33 turn(s))
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
reviewed_by: [archive/peer/2026-09-17-priorart-priorart-d1-build.md, archive/peer/2026-09-17-priorart-d1-build-rev3.md, archive/peer/2026-09-17-priorart-priorart-d1-build-rev4.md]
supersedes: []
recipe: tools/recipes/build_d1_v0.py
measured_in: [tools/bench/diag_d1_step0.log, tools/bench/diag_d1_step0_reclass.log, tools/bench/d1_step0_census.json, tools/bench/build_oploopendref_v0.log, tools/bench/loopendref_637.json, tools/bench/diag_stop_save_seam.log, tools/bench/probe_move_into_v0.log, tools/bench/probe_move_ctlterm_v0.log, tools/bench/ctlterm_owners.json, tools/bench/gpu_kernel_v1_fp.json, tools/bench/gpu_n1_deltas.json, tools/bench/drive_original_copy_v3.log]
build_status: NOT READY - 짠11c decided the transport (queues only), but the rev4b prior-art review (6 findings,
  0 novel, all accepted) found the STOP it specifies is not buildable with today's ops (B1), its 1-element-queue
  wake-up is drop-NEW where the project decided latest-wins (A3), and its reverse-crossing poll needs a Case the
  counts do not contain (A2). Relocation phase MEASURED 2026-09-17; PHASE "full" blocked on those three.
reviewed_by_latest: archive/peer/2026-09-17-priorart-priorart-d1-build-rev4b.md
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

## 0-BLOCKER. ??**RESOLVED by 짠11c (2026-09-17): TRANSPORT = QUEUES ONLY.** The record of why is kept below

> **This section no longer blocks the build.** 짠11c is binding: a **1-element DBL queue** for 1.5's wake-up
> (written by 1.2 on the 25-frame tick, **timeout 0**), a **1-element queue** for the reverse crossing polled by
> 1.1 with **timeout 0** (**`#12589` stays on 1.1**, 짠11.3 resolved), and **end-of-stream sentinels** for the three
> new loops' stop, so **no second reader of `stop (end)` is needed** and `ControlTerminal #642` stays in 1.1.
> No Local, no user event, no DVR. Everything below is the measurement that led there, kept verbatim.

?좑툘 **This section said "cannot be built by this fleet" and that was WRONG ??corrected after
`archive/peer/2026-09-17-priorart-d1-build-rev4.md` A1.** This project *formally withdrew* that exact claim on the
same day (`archive/peer/2026-09-17-priorart-ctlterm-move.md:601-608`: *"a false 'impossible' that I wrote ??the
citation is **withdrawn** ??짠0d now reads **UNMEASURED, NOT IMPOSSIBLE**"*, carried in STATUS OPEN 24b), and rev 4
reinstated it as the thing that stops the build. **The recorded state is UNMEASURED.** Keep the two apart:

* **MEASURED (a fact about the fleet's contents today):** no op creates a `Local`, and none writes `Control Name`.
* **UNMEASURED (a fact about nobody having tried):** whether one *can* be built. No gate may be keyed to
  "impossible", and `build_d1_v0.py`'s S0 no longer is.

**짠11b.1 is binding for rev 4 and its closing clause is still false as written.** It reads
*"`restructure-plan-4.6.md:225-226` already adopts locals; **the Local creator exists**."* It does not exist:

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

?좑툘 **Item 3 is an INFERENCE, not a measurement** (rev-4 review B2). "Three new loops ??three readers of
`stop (end)` ??a Local" ignores the two live-mode stop mechanisms this project already recorded:
`stage2-assembly-step-c.md:45` ??*"Live mode (step D) is where the While tracker, an **end-of-stream token** and a
timeout-gated Case are unavoidable"* (1.2 and 1.7 are queue **consumers** of 1.1, so a token ends them with no
second panel reader at all) ??and `frame-ownership-design.md:102-103` ??*"First error wins: capture it,
**broadcast stop**, let each loop drain and release its own resources."* `pre-rig-master-plan.md:95` asks for
*"every loop stops from a Boolean read inside it"* and *"seven stops and one order"*; it never asks for seven
**panel-terminal** readers, and `stage2-plan.md:92-94` offers terminal/local as **examples**, not an exhaustive
list.

**What building one would actually cost, so the judgement session is choosing between priced options.** The
archived exchange this plan must check before re-asking (`archive/peer/2026-09-17-priorart-ctlterm-move.md:521`)
already states the condition precisely: *"a Local's binding is re-pointable **given a typed reference**"* ??and a
typed `Local` reference is exactly what the fleet does not hold. The route is the documented **typed-control seed**
(`toolkit-capabilities.md:64-77`: *"the same trick yields any class an NI example or library VI exposes on a
property-node input ??check the example folder first"*), so an `OpLocal` family is **three** pieces: a `Local` seed
harvested from an NI scripting example, a **creator**, and a `Control Name` **writer**. ?좑툘 **The writer is NOT a
new family** (rev-4 review B1): it is the `OpSetIndexMode_v0` shape ??*"Traverse('LoopTunnel', index) ??cast ??
IndexMode **WRITE property node** ??a control"* (`gscript.py:1661-1662`) ??built a second time as `OpSetLabel_v0`
(`gscript.py:2451-2454`, `Node.Label` 6359001 ??`Text.Text` write), and deriving from those front halves is this
fleet's normal move: `OpTunnelInd_v0` was *"built from OpSetIndexMode_v0, whose front half ??was already proven"*
(`gscript.py:1690-1692`), and `OpLoopEndRef_v0` is an *"additive build on OpWhileCast_v0"*, 16/16, **this cycle**
(`toolkit-capabilities.md:50`). So the writer is one additive op against a proven template. What is genuinely
unpriced is the **creator** (whether `New VI Object` even has a `Local` style is
**unlikely** ??the skill's own externally-sourced line is
`.claude/skills/labview-automation/references/vi-scripting.md:308`, *"`New VI Object` cannot create most node
types (error 1054), and NI's own advice is to copy from a donor"*, and `:465` records the 0??99 style sweep
creating nothing; `archive/peer/2026-08-28-wire-indicators-api.md:59` records it only for *front-panel* objects,
so the realistic creator is copy-from-donor, which lands on the **top-level** diagram and still needs the
re-point).

### 0-BLOCKER.b ??the FOUR candidate transports, after the census the first draft never ran

?좑툘 Rev 4 first wrote *"queues ??that is the only transport with evidence"* off a four-place census (`gscript.py`,
`claudeDev\Op*.vi`, `tools/recipes/`, `vi-server-ids.json`). **It never opened the donor library every writer op in
this fleet was wrapped from** (rev-4 review A3): `docs/REFERENCES.md:29-30` ??LV-Scripting at
`vi.lib\Erdos Miller\LV-Scripting\`, **84 VIs** ??and `docs/stage2-plan.md:110` records the four queue ops as
wrappers of `Create Obtain Queue / Enqueue Element / Dequeue Element / Release Queue.vi` from **that folder**.
**Listed 2026-09-17** (`ls` of that folder, 85 entries), it also ships a complete event set and a DVR set:

| candidate | creator VIs that exist on disk | status |
|---|---|---|
| **queue** | `Create Obtain Queue` 쨌 `Enqueue Element` 쨌 `Dequeue Element` 쨌 `Release Queue` | **EXERCISED**, 4 ops built, core 162/162 |
| **1-element queue** (latest-value) | the same four | **the project's own recorded latest-value transport** ??`restructure-plan-4.6.md:55`: *"\| 2 ??6 \| **local variable / 1-element queue** \| lossy by design; the display only needs the newest \|"*. A queue and a local are tabled as **alternatives for the same duty**, which refutes rev 4's "a queue contradicts freshest-wins" (review A2). `decisions.md:21`'s "no `Lossy Enqueue Element`" is scoped to the **acquisition** path, not a 3.6 Hz focus wake-up |
| **user event** | `Create Create User Event` 쨌 `Create Generate User Event` 쨌 `Create Register for Events` 쨌 `Create Unregister for Events` 쨌 `Create Destroy User Event` 쨌 `Create Event Structure` 쨌 `Construct Dynamic Event` 쨌 `Get Event Data In` 쨌 `Wire Event Data Out` 쨌 `Exit Event Structure` | **UNEXERCISED but present** ??`stage2-plan.md:114` already shelved `Create Event Structure.vi` as *"not needed in stage 2"*. `Generate User Event` never blocks the generator, which is the property 짠6 wants |
| **DVR** | `Create New DVR` 쨌 `Create In Place Element DVR` 쨌 `Create Delete DVR` | **UNEXERCISED but present** |
| **Local** | **none in the library** ??no `Create Local.vi` | no creator anywhere; route = seed + creator + writer (above) |

`toolkit-capabilities.md:14-15` is the distinction rev 4 collapsed: **exercised** (queues) is not the same set as
**buildable**. `ARCHITECTURE.md:60`'s "no Queue/Notifier primitive appears in the original" is not an obstacle
either ??the queue ops needed no donor, only a creator.

**Which of these D1 uses is a design decision with a rule-1a consequence, and a material session may not take it**
(CLAUDE.md 짠3). `build_d1_v0.py`'s gate **S0** refuses to run until `TRANSPORT` is set by the judgement session,
and it now refuses on "unset / no creator built yet", never on "impossible".

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
| **a `Local` node** | **NO CREATOR** ??and ??**D1 needs none** (짠11c: queues + sentinels) | 짠0-BLOCKER |
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
other half ??"and locals in the others" ??is the thing 짠0-BLOCKER found no creator for, and 짠11c makes it
**unnecessary**: the other loops stop on sentinels, so `#642` moves nowhere and stays in 1.1.**

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
| **1.5 FOCUS** | a NEW While loop on `Diagram #686` | `CaseStructure #10407` + `#48 ASI_adjust focus-subvi.vi` **only** (짠11c: `#12589` **stays on 1.1**), 2 shift registers (one carries the **VISA session**); woken by the 1-element `Q_focus` |
| **1.7 WRITER** | a NEW While loop on `Diagram #686` | `#376 save trace.vi` (짠11b.3 ??it *is* the accumulator), the streaming TSV write, 2 shift registers |
| **1.9 STOP** | ??| paths A and B of 짠4 stay **whole on 1.1**; the three new loops stop on **end-of-stream sentinels** (짠11c), not on a panel read |

## 4. The stop, measured ??row 1.9

??**`WhileLoop #637`'s conditional terminal is uid 648**, a SINK carrying **wire 3457**, whose single source is
`CompoundArithmetic` **#11639** ??all inside `Diagram #639`. Read by `OpLoopEndRef_v0.vi`
(`WhileLoop.Loop End Ref` **6362C00**, data terminal **`LpEndRef`**), 16 pass / 0 fail
(`tools/bench/build_oploopendref_v0.log`, raw `loopendref_637.json`). The same run read #25380 ??25410 / wire 1737
and #15173 ??15276 / wire 19456.

| path | wiring (measured) | D1 |
|---|---|---|
| **A** | panel `stop (end)` **#7** ??terminal (`ControlTerminal #642`) wire 6929 ??`CompoundArithmetic` **#11639** t2, OR-ed with wire 12070 ??`#12589` t2 and wire 10249 ??`x = y?` #10019 ??**wire 3457** ??**#637 cond. terminal uid 648**; also ??panel indicator `TurnOff` #24423 | **stays 1.1 WHOLE** (짠11c): `#11639`, `#12589` and `ControlTerminal #642` all stay, so w12070 and w6929 are **not cut**. The only crossing is **into** `#12589` t1: `#10407` t6 (now on 1.5) ??`Q_focusback` (1 element, timeout 0) ??dequeued by 1.1 each iteration |
| **B** | panel `stop (end) 2` **#19587** ??wire 15230 ??`CompoundArithmetic` **#17883** t1 (with w18092 ??`.not. x?` #17837, w18056 ??`x = y?` #22284) ??**wire 15229** ??`Tunnel` **#22085** of **`CaseStructure #22082`** | **#22082 stays on 1.1 with path B intact** ??nothing in the kernel's forward slice feeds it |

**Rule (NI's infinite-loop mistake, `stage2-plan.md:90-94`):** a front-panel Boolean wired in from outside a loop
becomes an input tunnel read **once**. Every new loop therefore reads its stop from a terminal **inside** its own
body. `exit_while` / `OpExitWhile_v0` is verified 5/5 (ExecState 0 ??1, the VI runs and stops) ??**on a fresh VI
whose Boolean control terminal is at the TOP LEVEL**. ??**짠11c removes the need for a second panel reader
entirely**: the only `stop (end)` terminal stays in 1.1, and 1.2 / 1.5 / 1.7 each stop on the **end-of-stream
sentinel** that arrives on the queue they already consume (짠9a). Nothing reads `stop (end)` but `#11639`.
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
| **12589** | Case Structure | **stays 1.1** (짠11c, 짠11.3 RESOLVED) | t1 ??`#10407` t6 w9113 (**the reverse crossing**, 짠0b). Keeping it on 1.1 keeps w12070 ??`#11639` uncut; the crossing becomes `Q_focusback`, a **1-element queue** written by 1.5 and polled by 1.1 with timeout 0 |
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

**Count contract (REV 4 + 짠11c): 20 nodes move off diagram 43** ??**17 ??1.2** (the 18 rows above minus `#5058`,
which is **deleted**, not moved), **2 ??1.5** (`#10407`, `#48`; `#12589` **stays** per 짠11c), **1 ??1.7**
??**20 moves + 1 delete + 1 drop**. **27 of the 47 stay.** (Rev 4 before 짠11c said 21 / 3 / 26.)

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

### 5d. Control terminals ??**6 move; the seventh (`stop (end)`) stays, and 짠11c makes that sufficient**

?좑툘 **COUNT CORRECTED 2026-09-17** (folding 짠11c in): the heading said *"5 move, and the sixth is the blocker"*
while its own table lists **six** moving rows (`Auto-Reset`, `Reset Tracking`, `Z/dZ`, `Correction Factor`,
`min value`, `Force (pN) vs Extension (nm) `) plus `stop (end)`. **6 move, 1 stays.** `build_d1_v0.py`'s
`CTLTERM_CONTROLS_12` already listed six; the S3c gate below now says 6 too.

| wire | panel object | read/written by | D1 |
|---:|---|---|---|
| 9806 | control `Auto-Reset` uid 17472 | `#9647` t1 | terminal **moves** into 1.2 |
| 10312 | control `Reset Tracking` uid 5605 | `#10247` t1 | terminal **moves** into 1.2 |
| 730 | control `Z/dZ` uid 47 | `#2222` t0 | terminal **moves** into 1.2 |
| 6096 | control `Correction Factor` uid 9289 | `#2222` t5 | terminal **moves** into 1.2 |
| 17287 | indicator `min value` uid 17257 | `#10969` t3 (writer), `#17289` (reader) | terminal **moves** into 1.2 ??both ends go together |
| 10908 | indicator `Force (pN) vs Extension (nm) ` uid 8038 | `#11261` t0 | terminal **moves** into 1.2 |
| 6929 | control **`stop (end)` uid 7** (`ControlTerminal #642`) | `#11639` t2 on 1.1 | **stays 1.1, and that is now sufficient** (짠11c): 1.2/1.5/1.7 stop on **end-of-stream sentinels**, so they need **no** panel reader and **no** Local. ??짠0-BLOCKER item 3 closed |

These terminals are inside `Diagram#639` **on purpose** (짠4's read-once rule), and the user flips `Reset Tracking`
during a run ??routing it through a tunnel would change *when* it is read, a computation change, not scheduling.
**The build must plan for 31 terminals on `Diagram#639`, not 6**: the six above are those step 0 could see from a
*wired* boundary wire, and `ctlterm_owners.json` lists the rest. Any terminal left behind whose node moved shows up
in the census diff (짠8) as a wired?뭕are terminal and is re-wired or moved there.

---

## 6. Row 1.5 ??the autofocus loop

* **`CaseStructure #10407` and `#48 ASI_adjust focus-subvi.vi` move to their own While loop** (짠11c: `#12589`
  **stays on 1.1**), which owns the ASI VISA session's shift-register pair. Nothing on the frame path can block on
  it ??rule 1c is satisfied **by construction**, not by being fast enough: every queue op on the frame path takes
  **timeout 0**.
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
* ??**WAKE-UP TRANSPORT ??DECIDED (짠11c): a 1-element DBL queue `Q_focus`.** 1.2 owns the frame counter, so 1.2
  evaluates the 25-frame cadence and enqueues the slice index **only on a tick, with timeout 0** ??a full queue
  means the previous wake-up is still unconsumed, so the enqueue is skipped and the frame loop never waits. That is
  the "freshest wins, never blocks" property, realised with the one transport this fleet has exercised
  (`restructure-plan-4.6.md:55` tables local / 1-element queue as alternatives for exactly this duty).
  `build_d1_v0.py` sets `TRANSPORT = "queue"`.
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
2b. ?뵶 **`#376`'s OTHER inputs sit on SHARED NETS whose remaining sinks STAY on 1.1** ??measured, and rev 4 first
   tabled only its two shift registers (rev-4 review B3). This is **the exact failure class that stopped phase P's
   run 2** (짠2a: *"wire 464 is ONE net"* whose collateral sinks `#237`/`#240` were bared, **pinning ExecState at
   0**, with *no broken wire and nothing for Remove Bad Wires* ??a silent bare terminal):

   | wire | `#376` terminal | the other sinks on the same net | where they go |
   |---|---|---|---|
   | **w3268** (`frame-loop-wire-graph.md:151`) | t7 `x` | `#2136` t3 쨌 `#3191` t1 쨌 `#10068` t3 쨌 `#1114` t0 쨌 `#29240` t3 | **all five STAY on 1.1** (짠5a) |
   | **w5090** (`:167`) | t11 `selected path` | `#23175` t0 (Strip Path) | **stays on 1.1** (짠5a) |
   | w3629 (`:158`) | t6 `cal cluster path` | ??| ??|
   | w1581 (`:145`) | t9 `file size` | ??| ??|

   **So moving `#376` bares six terminals on nodes that never move**, and gate S3b as first written censused
   *"every moving node"* only ??the collateral sinks fall outside it on **both** passes, while `ExecState` is not
   read until S5. **S3b is widened**: the census covers every node that carries **any wire a moving node's
   terminal carries**, on both sides, so a net with a staying sink is visible. Whether `#376` should move at all
   is `짠11b.3`'s rule-1a decomposition call and is **not** reopened here.

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
| **`Q_focus`** ??1.5's wake-up | 1 DBL (짠6), the slice index | `#10757 .element` | **1** (짠11c) | written by **1.2** on the 25-frame tick, **timeout 0**; full ??skip. Never blocks the frame path |
| **`Q_focusback`** ??the reverse crossing | 1 DBL, `#10407` t6's value | `#10407` t6 (w9113) | **1** (짠11c) | written by **1.5**, **polled by 1.1 with timeout 0** into `#12589` t1; `timed out?` ??keep the previous value |

**Eight queues in total** (짠11c): `Q_free`, `Q_work` (bound **20**), `Q_meta`, `Q_res`, `Q_good`, `Q_rmeta`,
`Q_focus` (**1**), `Q_focusback` (**1**).

Every enqueue takes a **finite** timeout and its `timed out?` is read (`frame-ownership-design.md:80-83`); every
queue op that sits on the **frame acquisition path** takes timeout **0** (rule 1c).
**Slot ledger:** every exit path returns the slot exactly once ??normal completion, kernel error, enqueue timeout,
shutdown, writer error.

### 9a. The stop, by end-of-stream SENTINEL (짠11c) ??the encoding, and the one writer rule

The sentinel is **a value the kernel can never produce**, so no real row can be mistaken for it and no extra
Boolean channel is needed:

| queue | sentinel value | who writes it | who exits on it |
|---|---|---|---|
| `Q_meta` | **buffer number ??** (`#6810 current image number` is a frame index ??0) | 1.1, once, after `stop (end)` ends the frame loop | 1.2 |
| `Q_work` | the pool slot that carries the ?? row (the image itself is ignored) | 1.1 | 1.2 |
| `Q_rmeta` | **buffer number ??** | 1.2, once, after it sees the ?? | 1.7 |
| `Q_res` / `Q_good` | **empty array** (the kernel always returns one element per bead, N ??1) | 1.2 | 1.7 |
| `Q_focus` | **??** (a slice index is ??0) | 1.2, once, after it sees the ?? | 1.5 |

**The writer must not write the sentinel row.** 1.7 tests the dequeued `Q_rmeta` value **before** appending: ?? ??
leave the loop, do **not** append a TSV line and do **not** extend the accumulator; then drain, then call `#6384`.
Order is "stop the users ??drain ??release", so no error 1122 (`frame-ownership-design.md:68-72`), and the
sentinel travels the same queues the data travels ??no second reader of `stop (end)` anywhere.

---

## 10. Prediction contract

### S ??structural (`build_d1_v0.py`, one run, one log)

| gate | assertion, with counts |
|---|---|
| **S0** | `TRANSPORT` is set to a mechanism with a **creator built in the fleet today** ????`"queue"` (짠11c). Original md5 `2a78e17c449cacdaf5da389818526859` read **before**; `OpMoveIn_v0.vi` present, UID control `'UID 3'`; LabVIEW handles recorded |
| **S1** | the D1 target opens with, **before** any edit: `Diagram 171`, `Node 626`, `Wire 1902`, `LoopTunnel 132`, `ControlTerminal 114`, `WhileLoop 3`, `Local 8` |
| **S1q** | **8 queues obtained** (짠9): `Q_free` / `Q_work` bounded **20**, `Q_meta`, `Q_res`, `Q_good`, `Q_rmeta` unbounded, **`Q_focus` and `Q_focusback` bounded 1**. Each Obtain's `max queue size` read back from the created node; **no `Local`, no user event, no DVR is created ??`Local` stays 8** |
| **S2** | **three** new While loops on `Diagram #686`: `WhileLoop 3 ??6`, `Diagram 171 ??174`; `#637` still exists, still owns `#6810`, `#22700` and `CaseStructure #22082` |
| **S3** | **20 nodes reparented** (17 ??1.2, **2** ??1.5, 1 ??1.7 ??짠11c keeps `#12589` on 1.1), each verified by `OpOwnerChain_v1` reading `uid ??<body Diagram> ??<the right WhileLoop>`; **`#12589`, `#11639` and `ControlTerminal #642` still owned by `Diagram #639`**; total `Diagram` count unchanged **by the moves** (structures keep their frames); `#5058` deleted, `GPU_kernel_v1.vi` dropped into 1.2 (`SubVI 98 ??98`) |
| **S3b** | **census diff = the re-wire list** (짠11a.2): `node_terms` **before** and **after**, over every moving node **AND every node that shares a wire with one** (rev-4 review B3 ??a net's *staying* sinks are bared silently and a moving-nodes-only census cannot see it, which is how phase P run 2 died); the set that went wired?뭕are is the authoritative list; gate ??that set **??짠8's 13 crossings**, **includes `#376`'s w3268/w5090 collateral sinks**, and **every member is re-wired** (tunnel, queue or SR) before ExecState is read. **wires cut == wires re-wired** |
| **S3c** | **8 shift registers** created and wired (4 on 1.2, 2 on 1.5, 2 on 1.7); **6 `ControlTerminal`s** reparented into 1.2 (짠5d, count corrected from 5), total `ControlTerminal` still **114**, all 114 `panel_wiring` labels present |
| **S3d** | whole-array parameters cross **non-indexed**: `tunnels()` reports `IndexMode 0` for `cross size`, `# of bead 4 packs`, `4 pack remainder`, `Array of cal clusters`, `Real-space cosine window`, `Cosine bandpass\nfor Hilbert ` (**6 tunnels**) |
| **S4** | each of the three NEW loops' conditional terminals is **written and driven by its own sentinel test** (짠9a), read back by `OpLoopEndRef_v0`: a non-zero `CondWireUID` on each of 1.2 / 1.5 / 1.7. **For `#637` nothing changed**: `OpLoopEndRef_v0` must still read terminal **648 ??wire 3457 ??`#11639`** after the build |
| **S4s** | **the sentinel path exists and is one-way**: the enqueue that publishes each sentinel is present on its writer's diagram and its element is the literal sentinel (**??** for `Q_meta` / `Q_rmeta` / `Q_focus`, **empty array** for `Q_res` / `Q_good`); **1.7's append is gated by the ?? test** (the writer never writes the sentinel row); **no new panel object** was created for any of it (`ControlTerminal` still 114, `Local` still 8) |
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
??118 MB/s at 90 Hz** (STATUS OPEN 18), so 5 min ??**35 GB**.
?좑툘 **ARITHMETIC CORRECTED** (rev-4 review A4): rev 4 first wrote "60 s ??4 GB", which does not use its own rate.
**Measured**, in a log this plan already lists: `tools/bench/drive_original_copy_v3.log:81` ??`.tif`:
**2041 files / 2,675,689,770 B** from a ~20??2 s frame loop ??**??122 MB/s**. So **60 s ??7.3 GB**, not 4 GB, and
the run must have that much free **and delete in the same run** (STATUS OPEN 18: *"bound it or the disk fills"*).
60 s proves the plumbing; the 5-minute run is scheduled once the user decides how the harness handles TIFF
writing. Flagged ??OPEN 4.

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
**All four loops exit** ??1.1 on the panel Boolean, then **1.2 / 1.5 / 1.7 on the sentinels 1.1 publishes** (짠9a),
in that order (each loop's iteration counter frozen, read twice 2 s apart); **no error 1122**; the `.tra`
is written and **re-openable**; **restart 15 s**; stop again; close **without saving**; scratch deleted; TIFFs
deleted; original md5 unchanged.
?좑툘 **F2 inherits STATUS OPEN 17b**: v3's R11 scored the *restart*, not the stop, so "the stop works" is
**unproven** ??F2 gates on the stop itself, not on the fact that a restart succeeded afterwards.
?좑툘 **No `VISA Close` gate** (짠6/짠11b.2): the original has none and D1 adds none.

---

## 11c. DECIDED (judgement session, 2026-09-17, after the rev-4 review) ??TRANSPORT = QUEUES ONLY. Resolves 짠0-BLOCKER and 짠11.1/짠11.3

짠11b.1's "the Local creator exists" was **false** (asserted without checking ??the rev-4 review's A1, a repeat of a
claim this project withdrew the same day). Retracted. Of the five measured candidates (queue 쨌 1-element queue 쨌
user event 쨌 DVR 쨌 Local-without-creator), D1 uses **the queue family only** ??the one transport exercised 162/162,
needing no new op under the cycle-15 freeze. "A queue contradicts freshest-wins" is refuted by
`restructure-plan-4.6.md:55` (rev-4 review A2), which tables local / 1-element queue as alternatives for this duty.

- **1.5 wake-up:** a **1-element queue** of DBL (the slice index, 짠0b). The TRACKING loop evaluates the 25-frame
  cadence (it owns the frame counter) and enqueues **only on a tick, with timeout 0** ??full ??skip, never block.
- **Reverse crossing** (#10407 ??#12589 ??#11639 ??#637's stop): **#12589 stays on 1.1** (짠11.3 resolved); the
  FOCUS loop writes #10407's t6 value into a **1-element queue**, and the ACQUISITION loop **polls it with timeout 0**
  each iteration into #12589's input. Same value, different carrier.
- **Stop of the three new loops:** no panel readers and no Local ??the **end-of-stream token** pattern
  (`stage2-assembly-step-c.md:45`, `frame-ownership-design.md:102-103`): on stop the acquisition loop enqueues a
  sentinel into `Q_work`/`Q_meta` (a value the kernel can never produce: buffer number ??, empty image ref);
  tracking exits on it and forwards a sentinel into `Q_res`/`Q_good`/`Q_rmeta` (empty array / ??); the writer
  exits on that, then drains, writes nothing for the sentinel, and calls #6384; the focus loop gets its own sentinel
  (??) on its wake-up queue. Order "stop users ??drain ??release" holds by construction. The single `stop (end)`
  ControlTerminal #642 stays in the acquisition loop.
- Local, user event and DVR: **not used in D1** (recorded as measured alternatives, not refuted).

## 11. OPEN ??what this plan still does not decide

1. ??**짠0-BLOCKER ??the transport.** Resolved by 짠11c (queues only). *Was:* 짠11b.1 decided locals; the fleet has no Local creator and no
   `Local.Control Name` writer, and a new op is frozen. It blocks 1.5's wake-up, the reverse crossing, and the
   stop read in all three new loops. The only buildable alternative is a queue, which contradicts 짠6's own
   requirement. **One decision, three consequences.**
2. ?뵶 **Is the GPU's whole-fixture divergence acceptable?** (STATUS OPEN 16.) D1 proceeds under 짠11a.1's written
   assumption; N1 reports both ranges.
3. ??**`#12589`'s placement ??RESOLVED by 짠11c: it STAYS ON 1.1**, and the crossing is a **1-element queue**
   (`Q_focusback`) written by 1.5 and polled by 1.1 with timeout 0. *Was:* 짠11b.1's "a Boolean local written by
   the focus loop" read as *#12589 goes to 1.5*, rev 3 짠4 put it on 1.2, and the DBL/Boolean question hung on it.
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
`archive/2026-09-17-status-cycle15-narrative.md`**. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this from disk.

## START HERE
1. **`docs/pre-rig-master-plan.md` is THE plan**; settled decisions **`docs/decisions.md`**; cycle plan
   `docs/cycle15-plan.md`; **the build plan is `docs/d1-build-plan.md` REV 4 ??read 짠0-BLOCKER first**, then 짠5
   (the node-by-node move table) and 짠10 (the S/N1/F1/F2 contract). Recipe: `tools/recipes/build_d1_v0.py`.
2. ??Prior-art gate live (`REFUTED:`/`FIXED:`); `premature_build` (b) exempts a RE-RUN (22). Retrospectives 10??4.
3. ??**Scripting EDITS are silently declined until the target's FRONT PANEL has been opened** ??`ensure_loaded()`.
4. ??**A fixed op PATH is served from LabVIEW's memory, not from disk** ??unique working-copy filename per run.

## LabVIEW execution lock

```yaml
labview-lock:
  status: acquired
  owner: material/cycle15-d1-build-rev4b
  since: 2026-09-17 06:5x
  purpose: build_d1_v0.py PHASE "relocate" on a COPY under claudeDev (3 loops, 20 moves, S3b cut census).
           Original READ-ONLY, md5 asserted before and after. LabVIEW restarted first (handles 54,380).
# 2026-09-17 06:2x-  material/cycle15-d1-build-rev4: NEVER ACQUIRED. Docs + recipe + prior-art dispatch only;
# no COM call, no edit, no hardware. The build STOPPED at its own S0 gate before any LabVIEW work (OPEN 25).
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
no acquisition, no stop). **THE GAP:** 168 ops, 116 recipes, 220 peers ??**zero runnable experimental VIs**.

## OPEN ??one line each; long forms in `archive/2026-09-17-status-cycle15-narrative.md`
1??, 5, 9??2, 18 ??**all in archive 짠9**: PERIODIC auto-reset ungated 쨌 autofocus CLOSED (every 25 frames ??3.6 Hz)
   쨌 27 undisposed peer archives 쨌 startup drives instruments (blocker at assembly) 쨌 A2 54/54, A3 112/170 쨌 doc
   lint 2/4/3 쨌 **TIFF 1.3 MB/frame ??MEASURED ??22 MB/s (2041 files / 2.68 GB in ~20 s) ??bound it or the disk fills**.
13. ??**STOP MEASURED**: `#637` cond. term **648 ??w3457 ??`#11639`**; `stop (end) 2` SEPARATE. ??archive 짠1, 짠10.
14. ?뵶 cycle-15 prior-art only PARTLY disposed (A7/B3 = judgement) ??짠2. 15. ??`bgrun --detach`; 15b. ?뵶 its kill
   misses an ORPHANED grandchild ??짠3. 17. ??D0 16/0; 17b. ?뵶 v3's R11 scored the *restart* ??"stop works" UNPROVEN.
16. ?뵶 **GPU whole-fixture divergence OUTSIDE `decisions.md:38` ??JUDGEMENT.** Now exact (`gpu_n1_deltas.json`):
   beads 0?? **0 exceedances over all 10,043**; **only bead 4** ??10 x, 9 y, 1 flip, n_valid 10,029. ??짠4.
   20/21. ??**CLOSED** ??`py tools/violations.py`: **0 slugs awaiting a response**; devices built. ??짠8.
19. ??**REV 4 WRITTEN** ??the plan is now the build order: 짠11a/짠11b folded in, the node-by-node move table on the
   BEFORE census keys (**21 moves + 1 delete + 1 drop**; 8 of 14 SRs; 5 of 31 ControlTerminals), F1 **60 s**, A5 ??
   **D2**, #376 in 1.7, S/N1/F1/F2 with counts. Recipe `tools/recipes/build_d1_v0.py`. Rev 3's 8 findings disposed.
25. ??**TRANSPORT DECIDED ??짠11c, QUEUES ONLY, folded into rev 4's body** (짠0-BLOCKER/짠11.1/짠11.3 resolved;
   짠3 짠4 짠5a 짠5d 짠6 짠9+짠9a 짠10 rewritten): 1-elem DBL `Q_focus` (1.2 enqueues on the 25-frame tick, timeout 0);
   1-elem `Q_focusback` (1.5 writes, 1.1 polls timeout 0) and **`#12589` STAYS on 1.1**, so w12070/w6929 are
   never cut; **end-of-stream sentinels** stop 1.2/1.5/1.7 (`Q_meta`/`Q_rmeta`/`Q_focus` = **??**,
   `Q_res`/`Q_good` = **empty array**; the writer must not write the sentinel row), so **`ControlTerminal #642`
   stays in 1.1 and no `Local` is needed**. Move table is now **20 moves** (17/2/1) + 1 delete + 1 drop.
26. ??**REV-4 REVIEW DISPOSED** (`archive/peer/2026-09-17-priorart-priorart-d1-build-rev4.md`, 548 s, $6.67):
   **7 findings, 0 novel, all ACCEPTED.** FIXED **A1** (false "impossible"), **A4** (measured **122 MB/s** ??F1
   60 s ??**7.3 GB**, not 4), **B1** (the `Control Name` writer is the `OpSetIndexMode_v0` shape ??one additive
   op), **B3** the costly one: **`#376`'s w3268/w5090 are shared nets whose 6 other sinks STAY on 1.1**, so moving
   it bares them silently (phase P run 2's exact death) and S3b saw only moving nodes ??S3b now walks the net and
   a new **`S3b-collateral`** gate fails the build if a staying node loses a wire. ESCALATED **A2 A3 B2** ??25.
19b/19c/24. ??**THE THREE RELOCATION FACTS, measured, now in plan 짠2/짠5**: phase P 12/0 (a `CaseStructure` moves
   **with its frames**, 171??71; `OpMoveIn_v0` UID control `'UID 3'`; the move **CUTS** border wires ??/??, so
   ExecState is read only at the end); ctlterm 9/0 (`#642` reparents, 114??14; **31** terminals in `Diagram#639`);
   step 0 12/12 + 8/8 (payload **1 DBL**; 14 SRs tabled; a wire graph alone mislabels 6 of 7 backward-slice nodes).
22. ??`premature_build` (b) exempts a RE-RUN (4/4). 23. ??handles CLEARED by a restart (51,220 ??37,290).

## NEXT
?뵶 **JUDGEMENT ??ONE question, and the rest of D1 is written and ready behind it** (`d1-build-plan.md`
짠0-BLOCKER.b): **which of the five candidate transports does D1 use?** It settles 1.5's wake-up, the reverse
crossing `#10407??12589??11639??637`, and the three new loops' stop **at once**. Queue = exercised but a lossless
FIFO; **1-element queue** = the project's own recorded latest-value transport; **user event** = present on disk,
never exercised, and `Generate` never blocks its writer ??which is exactly 짠6's requirement; DVR = present,
unexercised; Local = no creator, unmeasured. And the stop may need no extra reader (end-of-stream token /
broadcast stop). Also open: OPEN 16 the GPU tail (beads 0?? clean over all 10,043; **only bead 4** exceeds ??10 x,
9 y, 1 flip); F1 60 s (**??.3 GB**) vs the user's 5 min (**??5 GB**); `#12589` ??1.5 or 1.2 (plan 짠11.3).
?윟 Then MATERIAL, unchanged: set `TRANSPORT` in `tools/recipes/build_d1_v0.py`, one bgrun, S0?밪6 ??N1 ??F1 ??F2.

## Where to look
`CLAUDE.md` 쨌 **`docs/decisions.md`** settled 쨌 `docs/NAMES.md` strings 쨌 `docs/toolkit-capabilities.md` API 쨌
**`docs/d1-build-plan.md` REV 4 = the build order, blocked at S0** 쨌 `tools/recipes/build_d1_v0.py` the recipe 쨌
`docs/restructure-plan-4.6.md` 쨌 `docs/pre-rig-master-plan.md` 쨌 `docs/diagram-hierarchy.md` 쨌
`docs/gpu-backend.md` 쨌 the three status archives (rule 4).


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Prior-art review complete — read-only, no lock taken, nothing built, run or edited. **6 findings, zero `novel`.**

The plan under review carries three escalated blockers from the rev4b review (the timeout-gated Case, drop-new vs latest-wins, the conditional-terminal writer), and the `new-op` trigger means the next step builds an op to lift them. Four of the five artefacts that would require are already specified, named, priced or built in this project's own **current** files, and the plan cites none of them.

---

# PART A — THE DIRECTION

## A1 `unread-evidence` — the ops §11c needs are already named, scoped and cost-estimated in an ACTIVE document the plan never cites

`docs/stage2-assembly-step-e.md` (`status: current`, 2026-09-15) has a section titled *"Construction (after E0), **with the primitives the fleet lacks named up front**"*:

- `:209-210` — "the fleet can build **Cases and comparison primitives only at a VI's top level**, so it is a sub-VI" — the constraint *and* the recorded remedy.
- `:215-216` — "a **Boolean Case** (`Create Case Structure (Boolean).vi` → **`OpBuildCaseBool_v0`**, selector from the detector's output — **`build_case` today takes a CONTROL as selector, so a variant fed by `Get Outputs` is needed**)".
- `:217-218` — "**Case output tunnels** (`Exit Structure.vi`/`Exit Multi Frame Structure.vi` → **`OpExitCase_v0`**)".
- `:221-222` — "Toolkit gaps … `OpBuildLess_v0`/`OpBuildEqual_v0`, `OpBuildOrArray_v0`, **`OpBuildCaseBool_v0` (selector from a node output)**, `OpExitCase_v0`. **Estimated 4 ops.**"
- `:39-40` — which creators the donor library ships: "**`Create Less?.vi` does not exist** in the library (**Equal / Or Array / And Array / Index Array / Case (Boolean) / Exit Structure do**)", missing primitives coming from "`copy_by_index` of a donor".

That is item-for-item what the plan says it lacks: `docs/d1-build-plan.md:16` ("its reverse-crossing poll needs **a Case** the counts do not contain"), `:523` and `:545` ("**1.7's append is gated by the −1 test**"), `:544` (each new loop's conditional terminal "**driven by its own sentinel test**"). A `−1` test is a comparison primitive; a gated append is a Boolean-selector Case plus output tunnels.

`stage2-assembly-step-e.md`, `OpBuildCaseBool_v0` and `OpExitCase_v0` appear **nowhere** in `docs/d1-build-plan.md` or `tools/recipes/build_d1_v0.py` (project-wide grep; the only hits are step-e itself, `HOME.md:16`, `pre-rig-master-plan.md`, `camera-acquisition-facts.md` and the archives).

**Scope:** covers the plan's and the recipe's account of what is missing for §9a's sentinel test and §11c's poll, and step-e's absence from the evidence base. It does **not** claim those four ops are built — step-e calls them gaps — nor that step-e's `Reseed.vi` design should be adopted.

## A2 `settled-already` — "no new general-purpose op VIs" is already decided for the duration of D1, and this plan leans on it three times

`docs/cycle15-plan.md:102-104` — "## Frozen while D1 is built (**outcome review Q7, adopted**) — **No new general-purpose op VIs**, no hierarchy completion beyond what D1 needs, …"

The plan does not merely coexist with it; it uses it as a premise:

- `docs/d1-build-plan.md:65` — the Local route is "a **new general-purpose op**, which `docs/cycle15-plan.md:104` **freezes for the duration of D1**";
- `docs/d1-build-plan.md:602` — §11c picks queues as "the one transport exercised 162/162, **needing no new op under the cycle-15 freeze**";
- `tools/recipes/build_d1_v0.py:42-43` — `Terminal.Create Constant` "is CATALOGUED ONLY … and an op for it is a **NEW op, frozen by `docs/cycle15-plan.md:104`**".

So "build a new op to unblock D1" is a question already decided the other way, by the outcome review, after two outcome reviews found zero runnable experimental VIs. Lifting it belongs to the authority that set it — and if it is lifted, the plan loses the premise it used to rule out the Local at `:65` and the constant op at recipe `:42-43`; both then need re-arguing on merits.

**Scope:** covers creating a new op inside cycle 15 and the three places this plan uses the freeze as a premise. It does **not** say the needed op is unbuildable, and takes no position on whether the freeze should be lifted.

## A3 `contradicted` — §6 calls three objects "Locals" that this project measured as CONTROL REFERENCES, while §0-BLOCKER's central argument is a census of the VI's Locals

The plan, `docs/d1-build-plan.md:383-384`:

> "`#48` t0/t1/t2 ← **Locals** `- Inc (PgDn)` **`#3529`**, `+ Inc (PgUp)` **`#3560`**, `Focus Step (F1)` **`#3447`**"

The measurement:

- `docs/main-vi-panel-map.md:403` — "Class census by Traverse: **`Local` 8**"; `:409-416` tables all eight by uid — **2991, 4277, 11574, 3160, 3097, 2143, 16942, 25805**. `#3529`, `#3560`, `#3447` are **not among them**.
- `docs/main-vi-panel-map.md:418-419` — "Bare-terminal objects **with NO local either**: **`+ Inc (PgUp)`, `- Inc (PgDn)`, `Focus Step (F1)`** … **Resolved 14:5x** … the rest by **control references**".
- `docs/camera-acquisition-facts.md:333-334` — "the first three of those eight (**`Focus Step (F1)`, `+ Inc`, `- Inc`**) are the **control references handed to `ASI_adjust focus-subvi.vi`**".

Two reasons this is not a naming slip:

1. **§0-BLOCKER's argument is a Local census.** `docs/d1-build-plan.md:53` rules the Local route out partly because "the VI's **8** Locals are bound to `Total Lost Frames` ×2, `File # Saved`, `Focus Pos (Track)`, `Rot pos (deg)`, `Trans Pos (mm)`, `Picture`, `Color table`. **None** is `stop (end)`, a slice index, a frame counter or a spare Boolean." §6 then asserts three *further* Locals in the same VI. Both cannot be a complete account of the same eight objects; the panel-map table is the measured one.
2. **All three feed `#48`, which moves to 1.5.** They appear in no row of §5a's 47-node move table (`:279-311`), in no line of the "20 moves / 27 stay" contract (`:313-315`), and in no gate of §10 — yet three refnum sources of a moving node are exactly §7.2b's own failure class (`:444-460`, "moving `#376` bares six terminals on nodes that never move", the death of phase P run 2). A control reference also crosses a border differently (`docs/NAMES.md:762` — "Wiring a refnum output from the top level into a node inside a loop **auto-creates the tunnel**"), and the plan names neither the class, nor the route, nor the three tunnels.

**Scope:** covers the word "Locals" at `:383-384` and the absence of `#3447`/`#3529`/`#3560` from §5a, the counts and §10. It does **not** say `#48` should stay on 1.1, and does not reopen §0-BLOCKER's conclusion — only the premise that its eight-Local census is a complete account of the autofocus chain's inputs.

---

# PART B — THE ARTIFACT

## B1 `helper-exists` — the conditional-terminal writer is a FRONT-HALF swap on an existing op, and this fleet has already built that exact swap four times

- `docs/toolkit-capabilities.md:31` — `exit_while` "**wires a While loop's conditional terminal** from the Boolean control named `stop_control` (**Get Controls → Index Array → Exit While Loop `Stop Condition`**)", `test_opexitwhile.log` **5/5: ExecState 0 → 1, the VI runs and stops**. The terminal is already written by a built, verified op; what is bound is the **source**.
- `docs/NAMES.md:751-752` — the donor's pane, measured: "`Exit While Loop.vi` connector: 0 `Diagram in`, 1 `Conditional Terminals`, 2 `Loop Terminal Types`, 5/6 `Outputs` in/out, 7/8 `Shift Registers` in/out, **9 `Stop Condition`**, 11/15 error." `Stop Condition` is a **terminal refnum input**, not a control name.
- `archive/bench-2026-09-14-stage2-toolkit/build_opexitwhile.py:2-3` — our own op header: "'Stop Condition' fed from a front-panel control chosen **BY NAME**: VI.Block Diagram → Get Controls(Control Names) → Index Array[0] → Stop Condition." The restriction is **our recipe's front half**.
- `docs/toolkit-capabilities.md:42` — swapping that front half is routine here, already done four times in one family: `OpWireSR_*` "wires ONE side of a register with `Terminal.Connect Wire` on the sink: **body node via `Loop.Diagram→Nodes[]→Terminals[]`**, **top-level node** via `VI.Block Diagram`, **control** via `Panel.Controls[]` — indices, never names".
- `docs/NAMES.md:747-750` records the precedent verbatim for the sibling creator: "`Create For Loop.vi` / `Create While Loop.vi` `Control Names` **DO work** … hence the morning's 'Control Names route not available' — **a defect of OUR op, not of the library**."

**Scope:** covers the claim that a sentinel-driven conditional terminal needs a **new op family** or a missing capability. It does **not** claim the swap has been built or measured — it has not — and it leaves `OpLoopEndRef_v0`'s read path (16/0) and A1's separate Case question untouched. It says the price is one derived variant against a proven front half, and that a verdict of "unreachable" would be the third false *impossible* in this plan's own three days (`docs/d1-build-plan.md:36-38`; `archive/peer/2026-09-17-priorart-priorart-d1-build-rev4.md:789-791`).

## B2 `already-built` — a Case creator exists and is functionally verified; its two limits are recorded, not undiscovered

- `tools/gscript.py:2616-2625` — `build_case(target, location, selector_name, input_names, frame_names)` via **`OpBuildCase_v1`**: "**Functional contract (tools/bench/case_v1_test.py, 2026-09-10): +1 CaseStructure, +2 Diagrams … +1 wire per name … ExecState 1, no dialog, ~0.1 s**".
- `docs/NAMES.md:369,:383-385` — "built + **functionally verified** 2026-09-10 … Diagrams 1→3, Wires +3, ExecState 1", with the `Frames`-array trap (`:379-382`, error 1302 behind an 8 s modal) already written down; `docs/toolkit-capabilities.md:124`.
- Its limits are recorded: selector must be a panel control (`stage2-assembly-step-e.md:216`), and it lands on the **top-level** diagram (`:209-210`) — and this cycle measured the answer to the second: `docs/d1-build-plan.md:195`, "**`CaseStructure #12589` → owner `Diagram #1170`, total `Diagram` count UNCHANGED 171 → 171** — the frames came with it", 12/0.

So "a Case inside a loop body" composes from two existing, measured ops (`build_case` + `move_in`). What §10 lacks is the **accounting**: S2 fixes `Diagram 171 → 174` (`:539`) and S3 asserts Diagram count "unchanged **by the moves**" (`:540`), while every Case adds **+2 Diagrams** at creation (`gscript.py:2623`). A counting gap in the contract, not a missing capability.

**Scope:** covers treating "a Case" as unbuildable, and §10's Diagram counts. It does **not** claim a **node-output-selector** Case is built, nor that Case output tunnels exist — A1's citation says both are named gaps.

## B3 `already-measured` — the sentinel literals and the poll's guard already have measured, no-new-op routes

- **The literals.** `tools/recipes/build_d1_v0.py:43-47` — "a route exists with BUILT ops: the original itself carries donor constants of exactly the needed values (`tools/bench/opconstvaluen_scan.json`, 180 numerics: value 0 ×69, 1 ×36, **20 ×2** …, **−1 ×1** (uid 4609 rep 3), 25 ×1), so `copy_by_index` (row 39, verified on built-in primitives) + `move_in` (12/0) places them **with no new op**. **MEASURED, UNWRITTEN**." Sentinel `−1`, bounds `20`/`1`, timeout `0` are all in that scan.
- **The poll's guard.** `docs/NAMES.md:755-756` — "`Create Dequeue Element.vi` 5 `queue`, 7 `timeout in ms (-1)`, 8 `element`, **14 `timed out?`**"; created-node terminal names at `:761-762`; op built and verified at `docs/toolkit-capabilities.md:32` (`test_opqueue.log` 7/7).

**Scope:** covers any new op proposed for **placing constant values** or for **reading a dequeue's `timed out?`**. It does **not** cover the Case that consumes the guard (A1/B2), and does not claim the literals route has been executed — the recipe's own word is *UNWRITTEN*.

---

## Checked and cleared — so the next round does not re-derive it

1. **rev4b's six findings still stand and are honestly recorded** (`docs/d1-build-plan.md:14-18`; disposition at `archive/peer/2026-09-17-priorart-priorart-d1-build-rev4b.md:944-962`). None of my six duplicates one of theirs.
2. **End-of-stream sentinels are the right prior art**, cited correctly (`docs/stage2-assembly-step-c.md:45`, `docs/frame-ownership-design.md:102-103`). Not challenged.
3. **`move_in` (12/0) and the ControlTerminal reparent (9/0)** are this cycle's own measured product, not re-derivable prior art.
4. **Addendum to rev4b's B2, deliberately not a new slug.** `build_d1_v0.py:48-50` concludes "no donor in this project holds an open/write/close chain" from two options. Besides the `drop_subvi`-of-vi.lib route rev4b named, the project's own node census of the main VI was not opened: `tools/bench/main_vi_node_labels.json` records **`Write to Binary File`** (`:2799`), `Refnum to Path` (`:214`), `Path To String` (`:218`), `String To Path` (`:244`), `Build Path` (`:1001`), `Strip Path` (`:1005`) — and `copy_by_index` copies built-in primitives (`docs/toolkit-capabilities.md:44`). A binary write is not a TSV text write, so this does **not** establish a route; it establishes that the census which would settle it was never consulted.
5. **Not slugged, one line.** `docs/frame-ownership-design.md:89-95` names what latest-wins mechanically *is* — "`IMAQdx Get Image` with **`Buffer Number Mode = Last`** … **no `Lossy Enqueue Element`**". rev4b's A3 cited `:89-93` for the policy; `:92-95` also carries the mechanism, and §11c's "freshest wins" sentence consults neither. Already escalated under rev4b A3 — re-slugging would block the same sentence twice.

---

```
PRIOR-ART: unread-evidence  (A1 — docs/stage2-assembly-step-e.md:39-40,:209-210,:215-218,:221-222 vs docs/d1-build-plan.md:16,:523,:544,:545 and tools/recipes/build_d1_v0.py — covers the plan's account of which primitives are missing for the sentinel test and the timeout-gated poll, not whether step-e's four named ops are built)
PRIOR-ART: settled-already  (A2 — docs/cycle15-plan.md:102-104 vs docs/d1-build-plan.md:65,:602 and tools/recipes/build_d1_v0.py:42-43 — covers creating a new general-purpose op inside cycle 15 and the three places this plan uses the freeze as a premise; takes no position on lifting it)
PRIOR-ART: contradicted     (A3 — docs/main-vi-panel-map.md:403,:409-416,:418-419 + docs/camera-acquisition-facts.md:333-334 vs docs/d1-build-plan.md:383-384, with the omission at :279-311,:313-315 — covers the word "Locals" for #3447/#3529/#3560 and their absence from the move table, the counts and s10)
PRIOR-ART: helper-exists    (B1 — docs/toolkit-capabilities.md:31,:42 + docs/NAMES.md:747-750,:751-752 + archive/bench-2026-09-14-stage2-toolkit/build_opexitwhile.py:2-3 — covers the claim that a sentinel-driven conditional terminal needs a new op family; does not claim the front-half swap has been built or measured)
PRIOR-ART: already-built    (B2 — tools/gscript.py:2616-2625 + docs/NAMES.md:369,:379-385 + docs/toolkit-capabilities.md:124 + docs/d1-build-plan.md:195 vs docs/d1-build-plan.md:16,:539-540 — covers treating "a Case" as unbuildable and s10's Diagram counts; does NOT cover a node-output selector or Case output tunnels, which A1 shows are named gaps)
PRIOR-ART: already-measured (B3 — tools/recipes/build_d1_v0.py:43-47 + tools/bench/opconstvaluen_scan.json + docs/NAMES.md:755-756,:761-762 + docs/toolkit-capabilities.md:32,:44 — covers a new op for placing constant literals or for reading a dequeue's `timed out?`; does not cover the Case that consumes the guard)
```

**The two that change what happens next.** **A1** — before any op is built, open `docs/stage2-assembly-step-e.md:207-222`: four ops are already named, scoped and priced there, and one of them (`OpBuildCaseBool_v0`, "selector from a node output") *is* the blocker, so the next build should be that op under its recorded name rather than a fresh invention. **A2** — that build is frozen by `docs/cycle15-plan.md:104`, and this plan leans on the freeze three times; either the authority that set it lifts it, or §0-BLOCKER's Local refusal and the recipe's constant-op refusal both have to be re-argued without it.

Two notes on this session's mechanics: the `Write` tool is disabled here, so the review exists only in this reply — it needs archiving under `archive/peer/` by the dispatching session to count as a gate-visible review. And the plan-mode scaffolding this session was started with expects an `ExitPlanMode` call that is not in my tool set; there is nothing to implement in any case, since this review is read-only by brief.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)

---

## What was done with it (material session, 2026-09-17 07:1x)

**All six findings ACCEPTED. 0 novel. No citation refuted.** This review was dispatched because
`guard_cycle.py` requires a prior-art review newer than the recipe, and the recipe had been edited to implement
rev4b's A1/B3. It did not repeat rev4b — it attacked the opposite side, and **it lifts two of rev4b's three
blockers**:

| # | verdict | disposition |
|---|---|---|
| **A1** | `unread-evidence` | **ACCEPTED, escalated.** `docs/stage2-assembly-step-e.md:39-40,:209-222` already names, scopes and costs the ops §11c's stop and poll need; the plan cites it nowhere and the recipe's header asserted "no construction route" without reading it. **That assertion is withdrawn** (it is the same false-"impossible" shape this project withdrew on 2026-09-17, OPEN 24b). What replaces it: PHASE "full" needs the step-e ops, and whether to build them inside cycle 15 is A2's freeze question — judgement. |
| **A2** | `settled-already` | **ACCEPTED, escalated.** `cycle15-plan.md:102-104` freezes new general-purpose ops for D1's duration, and this plan leans on the freeze three times. Only judgement can lift it; the material session records that PHASE "full" is blocked **by a freeze**, not by a capability. |
| **A3** | `contradicted` | **ACCEPTED — measured defect in the plan, escalated because it changes the MOVE TABLE.** §6's "`#48` t0/t1/t2 ← **Locals** `#3529` `#3560` `#3447`" is wrong: `main-vi-panel-map.md:409-416` tables all **8** Locals by uid (2991, 4277, 11574, 3160, 3097, 2143, 16942, 25805) and none of the three is among them; `:418-419` and `camera-acquisition-facts.md:333-334` measure them as **control references**. They feed `#48`, which moves to 1.5, and they appear in **no** row of §5a, **no** line of the 20/27 contract and **no** gate of §10 — §7.2b's own failure class. **A material session may not add rows to the move table**, so this is escalated; this run's widened S3b census (rev4b A1) will *measure* whether moving `#48` bares them. |
| **B1** | `helper-exists` | **ACCEPTED — this LIFTS rev4b's B1.** A sentinel-driven conditional terminal is a **front-half swap** on `OpExitWhile_v0`, the swap this fleet has built four times (`toolkit-capabilities.md:31,:42`; `OpTunnelInd_v0` from `OpSetIndexMode_v0`; `OpLoopEndRef_v0` from `OpWhileCast_v0`). So §11c's stop is **not unbuildable** — it is one additive op, gated by A2's freeze. |
| **B2** | `already-built` | **ACCEPTED — this LIFTS rev4b's A2.** `g.build_case` (`gscript.py:2616`) creates a Case and is functionally verified, so the timeout-gated Case §11c's poll needs is not a missing capability. Its two recorded limits (no node-output selector, no output tunnels) are named gaps, not unknowns. |
| **B3** | `already-measured` | **ACCEPTED.** The sentinel literals and the poll's `timed out?` guard have measured, no-new-op routes — the donor-constant route this session measured (`CONST_DONORS`, `opconstvaluen_scan.json`: 0×69, 1×36, 20×2, −1×1, 25×1) plus `copy_by_index` + `move_in`. |

**Net effect on the blockers.** rev4b left three (A2 poll-Case, A3 drop-new, B1 stop). rev4c lifts the **Case**
(B2) and the **stop** (B1, as one additive op under a freeze). **A3 — the 1-element queue's skipping enqueue is
drop-NEW where `decisions.md:25` decided latest-wins — is untouched and stands.** That one is a rule-1a /
data-quality decision, and it is the single thing PHASE "full" cannot be written around.

**What was run under this disposition:** `build_d1_v0.py` PHASE "relocate" only. No recipe edit followed this
review (an edit would re-trigger `guard_cycle`); A3's move-table question is *measured* by the run, not patched.

FIXED: unread-evidence - docs/d1-build-plan.md:651 - §11d now cites stage2-assembly-step-e.md:39-40,:209-222 as the active document that already names, scopes and costs the ops §11c's stop and poll need, and the recipe's "no construction route" claim is withdrawn there.
FIXED: settled-already - docs/d1-build-plan.md:645 - OPEN §11.8 records that PHASE "full" is blocked by cycle15-plan.md:102-104's op freeze, not by a missing capability, and that only judgement lifts a freeze.
FIXED: contradicted - docs/d1-build-plan.md:385 - §6's "Locals #3529 #3560 #3447" is corrected to CONTROL REFERENCES with main-vi-panel-map.md:409-416's eight-Local census, and their absence from §5a/the counts/§10 is raised as OPEN §11.6 (docs/d1-build-plan.md:640).
FIXED: helper-exists - docs/d1-build-plan.md:651 - §11d records that the sentinel-driven conditional terminal is a front-half swap on OpExitWhile_v0 (toolkit-capabilities.md:31,:42), so it is one additive op, not a new family.
FIXED: already-built - docs/d1-build-plan.md:651 - §11d records that the timeout-gated Case is g.build_case (gscript.py:2616), functionally verified, with its two recorded limits named.
FIXED: already-measured - docs/d1-build-plan.md:651 - §11d records the donor-constant route for the literals (opconstvaluen_scan.json: 0x69, 1x36, 20x2, -1x1, 25x1) through copy_by_index + move_in, no new op.
