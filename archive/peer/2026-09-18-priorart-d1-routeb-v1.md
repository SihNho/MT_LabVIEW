# priorart-d1-routeb-v1

- **agent:** claude
- **role:** priorart
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $5.5237  in 30 / out 37221 / cache-create 338804 / cache-read 2409880  (467s, 26 turn(s))
- **date:** 2026-09-18 21:42:16
- **outcome:** ANSWERED (468s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PRIOR-ART REVIEW (trigger: cycle-start).

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
decided_2026_09_17: "SINK RULE (judgement): a from-tunnel row's sink is ALWAYS a terminal with Is Source? = FALSE ??the consuming node's input inside the new loop (LabVIEW creates the tunnel) or, for a MOVED structure, its INPUT tunnel's OUTSIDE terminal; an OUTPUT tunnel is never a sink (T2c2's two-source broken wire). Gate per row: sink Is Source? FALSE and bare before, wire Is Broken? FALSE after. One read-only Terminals[] census of #5540 (pre/post move) is allowed to settle tunnel-side addressing."
type: plan
status: proposed
date: 2026-09-17
cycle: 15
kind: build
tags: [d1, route-b, seven-loop, tracking, focus, writer, queues, sentinels]
parent: docs/d1-build-plan.md
authorises: nothing ??짠11p reserves the start of B to the judgement session
spec_rows: [pre-rig-master-plan.md 1.1, 1.2, 1.5, 1.7, 1.8, 1.9]
measured_in: [tools/bench/build_d1_v0_run7.log, tools/bench/d1_rewire_sources.json, tools/bench/d1_step0_census.json,
  tools/bench/gpu_kernel_v1_fp.json, tools/bench/probe_move_into_v0.log, tools/bench/probe_move_ctlterm_v0.log,
  tools/bench/build_opcreateconstonterm_v0.log, tools/bench/build_opsentinel_ops_run3.log,
  tools/bench/test_opconnectnested_v0.log, tools/bench/loopendref_637.json]
prior_art_review: archive/peer/2026-09-17-priorart-priorart-connectfromwire.md (B's FIRST ITEM only ??the op
  `OpConnectFromWire_v0`; 6 findings, 0 novel, dispositions in that file). The PLAN AS A WHOLE is still
  NOT DISPATCHED ??the judgement session decides whether B is started (brief, 2026-09-17)
revised: 2026-09-17 (material, route-B session 1) ??짠1 bottom line, 짠4 mechanism table, 짠6 R1 disposition,
  짠6 R2 replaced, 짠7 S3w. Measured in tools/bench/diag_connectfromwire_facts.log and
  archive/peer/2026-09-17-rbw-deleted-wires-run9.md
---

# D1 ??ROUTE B. Build the new loops FRESH inside the copy; move only what has no creator

`docs/d1-build-plan.md` 짠11p: *"Anything short of [a saved `Track_v6_D1_GPU.vi` at ExecState 1 warm and cold]
after the budgets above ??**route B** (new loops built fresh inside the copy with the proven drop/name-wire helpers;
the original frame loop keeps everything except the tracker call, which is deleted; structures moved with
`GObject.Move` only where a fresh build is impossible)."* This file is that route written as a build order.
Target, md5 discipline, queues, sentinels, N1/F1/F2 are **unchanged from REV 4** and are not re-argued here.

**Sections:** 짠1 what changes vs route A 쨌 짠2 node-by-node (fresh / move / delete / stays) 쨌 짠3 the structures, one
verdict each 쨌 짠4 every wire, by mechanism 쨌 짠5 the wires made BY NAME 쨌 짠6 residual risks 쨌 짠7 prediction contract
S/N1/F1/F2 쨌 짠8 what B does NOT need.

Every line is marked **MEASURED** (with its citation) or **ASSUMED**. Nothing here was run against LabVIEW.

---

## 1. The one idea, and the arithmetic behind it

Route A relocated the tracker's whole neighbourhood and then had to **re-connect 109 cut terminals over 24 uids**
(MEASURED, `d1_rewire_sources.json`: `cut_terminals 109, resolved 109`). Run 7 attempted the 66 routable rows and
got **35 WIRED / 7 FAILED / 24 NO-ROUTE** (MEASURED, `build_d1_v0_run7.log:280-325`), because both name-addressed
writers miss an unnamed end and both index-addressed writers need a top-level source.

B removes the three **subVI calls** from that census and drops them fresh instead. The split, computed from the same
file (MEASURED):

| | rows | where they go in B |
|---|---:|---|
| rows belonging to `#5058` / `#48` / `#376` | **32**, and **all 32 carry a NAME** (the subVI panes) | fresh drop ??the sink name is guaranteed; 22 of the 32 are then routable with `wire` / `wire_sr` / a queue |
| rows belonging to the 21 moved nodes | **77**, of which **19 have an unnamed end** | unchanged from A |
| total | **109 over 24 uids** | |

So B does **not** make the re-wire disappear. It makes the three biggest, most-named nodes free, and it replaces
"resolve a cut wire" with "make a wire that never existed" for 59 fresh objects.

?뵶 **The bottom line, stated before the tables so it is not buried. REVISED 2026-09-17 (material, route-B session
1) ??the numbers below replace the earlier "61 / 21".** Of B's **82** connections:

| | rows | route |
|---|---:|---|
| **route BUILT and MEASURED** | **63** | 27 name-wires 쨌 20 `wire_sr` 쨌 5 `OpCreateConstOnTerm_v0` 쨌 6 `OpConnectNested_v0` (same diagram) 쨌 **2 R8 cross-diagram unnamed sinks, now `OpConnectNested_v1`** 쨌 **3 `ForLoop` newline-named sinks moved off `wire_control` onto `OpConnectNested_v1`** |
| **NO route** | **19** | **18 R1 tunnel-source rows** + **1 R3** (`#2222` t0 ??control `Z/dZ` uid 47, unnamed sink) |

Three things changed today, each MEASURED, none of them an opinion:

* **R8 is CLOSED.** `OpConnectNested_v1.vi` is built, saved (14,666 B) and functional **warm and cold**
  (`tools/bench/test_opconnectnested_v1_cold.log`, 7/0), and it made a real cross-diagram `D[19] ??D[24]` wire in
  the working copy (`build_d1_v0_run9.log:287`). R8's 2 rows are exactly that shape. ?좑툘 What is NOT closed is how
  to **certify** such a wire ??see R2, the gate is unsound.
* **The `from-ctl` rows split in two** (`docs/d1-build-plan.md` 짠11u.2, `tools/bench/diag_connectfromwire_facts.log`):
  3 of run 9's six 5001s were a **caller bug** ??`wire_control` called without `src_diagram_index` while the
  control terminal lives on `Diagram #639` (index **43**) ??and wire correctly once it is passed (`'Auto-Reset'`,
  sink wire **0 ??1231**). The other 3 get past `Get Controls.vi` and then fail in **`Wire Inputs.vi`** on the
  **DEST** name (`ForLoop` tunnels labelled `Force\nsmoothing\nhalf-width` /
  `Extension\nmedian filter\nhalf-width`), so they are re-assigned to the index-addressed writer. **The newline is
  not the cause** ??three of the six failing labels have no newline at all.
* **R1 did NOT shrink**, and its two in-plan candidates are refuted for 14 of 16 rows (see the R1 disposition in
  짠6). It needs `OpConnectFromWire_v0` (`docs/d1-build-plan.md` 짠11t), which is **NOT BUILT**.

A's run 9 left **18 NO-ROUTE + 6 FAILED = 24** (MEASURED, `build_d1_v0_run9.log:339`). B on today's fleet is
**24 ??19**, and **19 ??1** the moment `OpConnectFromWire_v0` exists. It is still **not** a route that closes by
itself.

---

## 2. Node-by-node ??fresh drop, move, delete, stays

Keys are `d1_step0_census.json ??diagram_43` (47 nodes) (MEASURED). "Fresh" = created by this build; "move" =
`OpMoveIn_v0` / `GObject.Move` (MEASURED 12/0 on a `CaseStructure`, `probe_move_into_v0.log`).

### 2a. DELETED from the frame loop ??5

| uid | what | why | evidence |
|---:|---|---|---|
| **5058** | `Track N beads four-fold over-kernel-v3.vi` | replaced by a fresh `GPU_kernel_v1.vi` in 1.2 | MEASURED 짠8 of REV 4 (16 terminals) |
| **48** | `ASI_adjust focus-subvi.vi` | replaced by a fresh drop in 1.5 | MEASURED run 7 wired t0?뱓5 by name |
| **376** | `save trace.vi` | replaced by a fresh drop in 1.7 | MEASURED `diag_savetrace_376.log` 4/0 |
| **22700 쨌 23020** | `IMAQ Write TIFF File 2` 쨌 `Build Path` | fixture insertions, not original | MEASURED 짠11h, `build_d1_v0_run6.log` S1t 4/4 |

?좑툘 Deleting `#48` and `#376` is **new to B** and bares the sinks that their outputs feed (`#6384`'s error chain via
w541; `#12589` t1 via w9113). Both are re-made in 짠4 ??but the delete must precede the `ExecState` read, exactly as
짠2b of REV 4 says (`ExecState` is meaningless between edits).

### 2b. FRESH ??59 objects, 3 of them subVIs

| n | what | helper (all MEASURED functional) |
|---:|---|---|
| 3 | `GPU_kernel_v1.vi` ??1.2 쨌 `ASI_adjust focus-subvi.vi` ??1.5 쨌 `save trace.vi` ??1.7 | `drop_subvi(target, path, diagram_index, location)` ??takes a **diagram index**, so a loop body is legal (`gscript.py:1171`) |
| 3 | While loops 1.2 / 1.5 / 1.7 on `Diagram #686` | `loop_in('while', ?? diagram_index, ??` ??*"stage 2 needs loops INSIDE loops"* (`gscript.py:1101`) |
| 1 | pool For loop (20 `IMAQ Create` ??`Q_free`) | `loop_in('for', ??`; shape proven in step C v2.1 (162/162) ??**ASSUMED** applicable at bound 20 |
| 16 | 8 `Obtain` + 8 `Release` | `queue_node('obtain'/'release', ?? diagram_index, ??` (`gscript.py:1068`) |
| 22 | 8 `Dequeue` + 8 data `Enqueue` + 6 sentinel `Enqueue` | same helper |
| 6 | 3 sentinel `Equal?` + 3 sentinel literals (??) | `OpCreateEqual_v0` 23/0 쨌 `OpCreateConstOnTerm_v0` 22/0 (`toolkit-capabilities.md:52,:54`) |
| 6 | the GPU kernel's 6 extra pane inputs as constants | `OpCreateConstOnTerm_v0` ??**typed by the sink and already wired** (MEASURED 22/0, value read back ??) |
| 2 | 1 `IMAQ Create` + 1 pool-seed `Enqueue` | step C v2.1 |
| 8 | shift registers (4 on 1.2, 2 on 1.5, 2 on 1.7) | `add_shift_reg` + `wire_sr` (rows 37??9) ??registers are **created fresh, never moved** |

The 6 extras and their values are MEASURED (`gpu_kernel_v1_fp.json`, 19 pane items = 13 shared + 6 extra):
`Function` = the node default 쨌 `cal_path` = empty 쨌 `nb` = 0 쨌 `status` = empty 쨌 `status_len` = 0 쨌 `flags` = 0.

### 2c. MOVED ??21 nodes + 8 control/indicator terminals

**??1.2 (17):** `5540` `9647` `10247` `10445` `10950` `17289` `10969` `10757` `1359` `2222` `2626` `6104` `8885`
`9833` `11261` `29874` `10686`. (= REV 4 짠5a's 18 rows under 1.2 minus `#5058`, which is deleted.)
**??1.5 (4):** `10407` + the three control references `3529` / `3560` / `3447` (MEASURED 짠11e.3; `#48` is **not**
moved in B, it is dropped fresh).
**??1.7 (0):** `#376` is dropped fresh, so 1.7 receives no moved node at all.

**Control/indicator terminals ??8, not 6.** REV 4 짠5d lists six (`Auto-Reset` 17472, `Reset Tracking` 5605, `Z/dZ`
47, `Correction Factor` 9289, `min value` 17257, `Force (pN) vs Extension (nm) ` 8038). MEASURED contradiction:
`d1_rewire_sources.json` has **7 `from-ctl` rows**, and two of them name controls 짠5d never lists ??
**`Force\nsmoothing\nhalf-width` uid 28148** (??`#1359` t7) and **`Extension\nmedian filter\nhalf-width` uid 28996**
(??`#1359` t8 and `#29874` t6) ??both of which run 7 FAILED with 5001 (`build_d1_v0_run7.log:297,298,301`). So the
reparent set is at least **8**. Reparenting is MEASURED 9/0 (`probe_move_ctlterm_v0.log`, `#642 ??Diagram#1170`,
total `ControlTerminal` unchanged at 114).

### 2d. STAYS on 1.1 ??everything else

`#6810` (the frame source, row 1.8 REUSE) 쨌 `#12589` (짠11c) 쨌 `#11639` 쨌 `#22082` 쨌 `#17883` `#17837` `#22284`
`#10019` (stop paths A and B) 쨌 `#1114` WLC (= D2) 쨌 `#57` `#3191` `#20474` 쨌 `#2136` `#10068` `#29240` 쨌 `#3057`
`#5119` `#10382` `#11529` `#11608` `#22703` `#23175` 쨌 `#3052` `#4580` `#30117` 쨌 `ControlTerminal #642`.
`#637`'s conditional terminal is untouched: **648 ??w3457 ??`#11639`** (MEASURED, `loopendref_637.json`).

---

## 3. The structures ??one verdict each, with the reason

| structure | verdict | reason (MEASURED unless marked) |
|---|---|---|
| **`#5540`** reseed Case | **`GObject.Move`** | `build_case` places the Case on the **top-level diagram** and takes a **front-panel CONTROL** as selector (`gscript.py:2756-2764`); 1.2's body is neither. Its selector is `#10247`'s Boolean, and its two frames are pure pass-throughs whose tunnels carry outer values (`stage2-assembly-step-e.md` CENSUS B) ??a fresh build would have to re-create 2 frames, 4 input tunnels and 2 `SelectorTunnel`s, and no op creates a `SelectorTunnel` |
| **`#10445`** Case | **`GObject.Move`** | same wall; its frames are uncensused (`stage2-assembly-step-e.md` calls Census A *still required*) |
| **`#2222`** Case | **`GObject.Move`** | same wall; frame contents uncensused |
| **`#1359`** For loop | **`GObject.Move`** | `loop_in('for', ??` can create a For loop on a nested diagram, but its **body contents are not censused** (`d1_step0_census.json` covers diagram 43 only) ??a fresh loop would be an empty one |
| **`#29874`** For loop | **`GObject.Move`** | same |
| **`#10407`** autofocus Case | **`GObject.Move`** | the brief's "rebuilt with `build_case`" is **refuted by measurement**: top-level-only + control-selector-only (above), and the case's frame contents are uncensused. A move is MEASURED to carry frames intact (`probe_move_into_v0.log` P3: `Diagram` count 171 ??171) |
| **`#12589`** Case | **stays on 1.1** | 짠11c ??keeping it keeps w12070 ??`#11639` uncut; the crossing becomes `Q_focusback` |
| the loop bodies of 1.2 / 1.5 / 1.7 | **fresh** | `loop_in('while', ??` |

??**fresh structures 4 (3 While + 1 For); moved structures 6; 0 structures rebuilt with `build_case`.**
This is the single largest correction B makes to the brief, and the reason is a docstring, not an opinion.

---

## 4. Every connection, by mechanism ??82 of the 109 cut terminals need one

27 of the 109 are `source-side` rows (a moving node's **output**, re-connected from its sink's side) and need no
call of their own (MEASURED, `by_action.source-side = 27`). The other 82:

| mechanism | n | addressing | status |
|---|---:|---|---|
| **`wire` / `wire_control` by NAME** | **27** (was 30) | both ends by name | MEASURED WORKS on nested diagrams ??run 7 wired 10 body-to-body by name, incl. into `CaseStructure`/`ForLoop` named tunnels. ?좑툘 `wire_control` **must** be given `src_diagram_index` (짠11u.2). 3 rows whose `ForLoop` sink name carries newlines moved OUT of this row and onto `OpConnectNested_v1` ??`Wire Inputs.vi` does not match them |
| **`wire_sr` LeftIn / RightIn** | **20** | register by index, node terminal by name | MEASURED 20/20 WIRED in run 7 |
| **`OpCreateConstOnTerm_v0`** | **5** | node + terminal by INDEX on a nested diagram | MEASURED 22/0; run 7 placed 5 literals in the real VI |
| **`OpConnectNested_v0`, SAME diagram** | **6** | both ends by INDEX, both inside 1.2's body | BUILT + wire-identity verified, **NOT ExecState-verified** ??짠6 R2 |
| **unnamed sink, source on ANOTHER diagram** | **2** | both ends by INDEX, different diagrams | ??**ROUTE BUILT 2026-09-17: `OpConnectNested_v1`** (cold `ExecState 1`, and one such wire made in the real VI, `build_d1_v0_run9.log:287`) ??짠6 R8 CLOSED |
| **`ForLoop` sink whose NAME carries newlines** | **3** | both ends by INDEX | ??`OpConnectNested_v1` ??`wire_control` reaches the SOURCE control fine but `Wire Inputs.vi` will not match the DEST name (짠11u.2, MEASURED) |
| **unnamed sink, source = a control terminal** | **1** | ??| ?뵶 **NO BUILT ROUTE** ??짠6 R3. Candidate, UNMEASURED: the control `Z/dZ` uid 47 already drives a wire, so `OpConnectFromWire_v0` (짠11t) could branch from that wire's source terminal |
| **tunnel-source rows** | **18** | source is not a named node | ?뵶 **NO BUILT ROUTE** ??짠6 R1 |

The **6** index rows are all **inside one body diagram** (1.2's), all `Node ??Node`: `#5540` t0 ??`#10247`
`x .or. y?` 쨌 `#10247` t2 ??`#10445` 쨌 `#10445` t0 ??`#9647` `x .and. y?` 쨌 `#1359` t4 ??`#8885` `x*y` 쨌
`#29874` t4 ??`#8885` `x*y` 쨌 `#11261` t1 ??`#1359`. **Same-diagram is exactly what `OpConnectNested_v0` does**
(MEASURED: *"both ends by index on THAT diagram"*, `toolkit-capabilities.md:55`).

?좑툘 The other three unnamed-sink rows are **not** same-diagram and are new findings of this reading (MEASURED,
`d1_rewire_sources.json`): `#1359` t5 ??`#10068` `x-y*floor(x/y)` and `#29874` t2 ??`#29240` `x-y*floor(x/y)` ??
both sources **stay on `Diagram #639`** while the sink moves into 1.2's body (**R8**); and `#2222` t0 ??control
`Z/dZ` uid 47, a `ControlTerminal`, which `Diagram.Nodes[]` does not list (**R3**).

Ordering that is already decided and must be kept: **reparent the 8 control terminals BEFORE any `wire_control`**
(run 7's six 5001s are `Get Controls.vi` looking on the wrong diagram ??STATUS NEXT, "Material, unblocked"); and
짠11k's create ??delete-the-wire ??re-wire order for each sentinel `Equal?`.

---

## 5. The wires made BY NAME ??the list, with the name's source

All names below are MEASURED, either in `docs/NAMES.md` or by a successful `wire` call in run 7.

**1.2 ??the fresh `GPU_kernel_v1.vi` (13 shared terminals, `gpu_kernel_v1_fp.json`):**

| terminal | source | mechanism |
|---|---|---|
| `Image In` | `Q_work` `Dequeue`.`element` | name (step C, 162/162) |
| `x,y,z array` | `#5540`.`x,y,z array` | name (MEASURED source-side row) |
| `Bead is good? array in` | `#5540`.`Bead is good? array out` | name |
| `pos in cal image in` | left SR `#2972` | `wire_sr LeftIn` (MEASURED WIRED) |
| `x,y,z array out` ??| right SR `#1147` | `wire_sr RightIn` (MEASURED WIRED) |
| `Bead is good? array out` ??| right SR `#5796` | `wire_sr RightIn` (MEASURED WIRED) |
| `pos in cal image out` ??| right SR `#119`, and `#10757`/`#10969` by name | `wire_sr RightIn` + name |
| `cross size` 쨌 `# of bead 4 packs` 쨌 `4 pack remainder` 쨌 `Array of cal clusters` 쨌 `Real-space cosine window` 쨌 `Cosine bandpass\nfor Hilbert ` | `#637`'s LoopTunnels `#2580` `#2396` `#4432` `#3656` `#3920` `#4031` | ?뵶 **R1** ??the sink name is known, the **source has none** |

**1.5 ??the fresh `ASI_adjust focus-subvi.vi`** (names MEASURED by run 7's six WIRED rows):
`-Inc reference` ??`#3529` 쨌 `+Inc reference` ??`#3560` 쨌 `Focus inc reference` ??`#3447` (all three moved into
1.5) 쨌 `VISA resource name` ??SR `#4344` (`wire_sr LeftIn`) 쨌 `In position` ??SR `#4274` (`wire_sr LeftIn`) 쨌
`Out position` ??`#10407` t5 (name) 쨌 `#10407` t6 `position [internal units]` ??SR `#4256` (`wire_sr RightIn`) and
??`Q_focusback`. `#10407` t1 `# slices in stack` ??LoopTunnel `#9641` is ?뵶 **R1**.

**1.7 ??the fresh `save trace.vi`** (pane verified by probe, `NAMES.md:111-118`):
`total data array in` ??SR `#51` 쨌 `total data array out` ??SR `#15` 쨌 `error in` ??SR `#1108` 쨌 `error out` ??SR
`#24` 쨌 `current frame data array in` ??the `Q_res`/`Q_good` dequeue chain (name) 쨌 `frame index` ??`Q_rmeta`
dequeue `element` (name ??**B's improvement**: in A this was a from-tunnel NO-ROUTE, `#376` t7) 쨌
`cal cluster path` / `file size` / `selected path` / `base path/filename` / `file # to append` ??LoopTunnels
`#3644` `#2294` `#5096` ???뵶 **R1**.
**1.7 ??`#6384 save N xyz traces.vi`** (same diagram `#686`): `#6384`'s inputs are **named**
(`desired # data points`, `cal cluster path`, `actual # data points`, `error in`, `data array`, `file # to append`,
`base path/filename` ??MEASURED `main-vi-stop-and-save.md:110-121`), and 1.7's output tunnels are named by
`exit_while(output_names=??`, so this seam is **all name-wire**. Three of `#6384`'s inputs keep coming off `#637`'s
own tunnels unchanged.

---

## 6. Residual risks ??named, with what would settle each

**R1 ???뵶 the one that decides B: 18 rows whose SOURCE is an unnamed tunnel.** MEASURED: 16 of the 17 A-era
`from-tunnel` rows carry `outer_source: null` (`d1_rewire_sources.json`; run 7: *"no NAMED node source in any
census"*), i.e. the value arrives on `Diagram #686` from something that is **not a node** (`stage2-assembly-step-e.md`
found `FlatSequenceInnerTunnel` in the same position for w2731/w5812). `loop_in` and `wire` both address the source
BY NAME (`gscript.py:1101,:1284`), so neither can create the tunnel.
**What B can offer that A could not** (ASSUMED, unmeasured): the value **is** readable as `#637`'s own **outer
terminal**, which is a `Node` terminal index-addressable on `Diagram #686` ??run 7 itself printed one
(`{'kind':'node','diagram':'19','uid':637,'i':37,'name':'','is_source':True}`). Both that terminal and the new
loop's tunnel terminal live on `Diagram #686`, so the wire is **same-diagram** and `OpConnectNested_v0` can express
it ??**provided the sink tunnel already exists**, which a fresh loop has no way to create from an unnamed source.
Two candidate resolutions, neither built:
 (i) create the tunnel with `loop_in` from **any** named node output of the right type on `#686`, delete that wire,
 then re-point by index (짠11k's proven create ??delete ??re-wire shape; MEASURED that Connect Wire on an
 **already-wired** sink re-routes and breaks, `gscript.py:2206-2207`, so the delete is mandatory);
 (ii) `GObject.Move` the six `LoopTunnel` objects themselves ??**unmeasured**, and a tunnel's owner is a structure,
 not a diagram.
**This is a judgement call and this plan does not take it.**

> **?뵶 R1 DISPOSITION, MEASURED 2026-09-17 (material, route-B session 1) ??candidates (i) and (ii) are REFUTED for
> 14 of the 16 rows, and R1's "What B can offer that A could not" paragraph above is WRONG as written.**
> Its premise is that the value is readable as **`#637`'s own outer terminal**, which would be an index-addressable
> `Node` terminal on `Diagram #686`. `tools/bench/d1_tunnel_sources.json` (18 rows, produced by
> `gscript.tunnels()` + `OpWireSource_v5`, `docs/d1-build-plan.md` 짠11s.1) measures the opposite for the rows that
> matter: on each of those outer wires the terminal with **`Is Source?` TRUE** is owned by
> **`FlatSequenceInnerTunnel`** (14 rows) or **`LeftShiftRegister`** of `#637` (2 rows) ??e.g. row 1,
> *"owner uid 5818 (`FlatSequenceInnerTunnel`) is neither a node on diagrams (19, 43, 0) nor a `LoopTunnel`"*.
> `#637`'s own outer terminal on an INPUT tunnel is therefore the wire's **SINK**, not its source, and a branch
> must be taken from a source. The one run-7 print the paragraph generalises from
> (`{'kind':'node','diagram':'19','uid':637,'i':37,'is_source':True}`) is an OUTPUT tunnel, a different case; and
> the single row that resolves to a named node (`SubVI #27605`) was already wired by index in run 9.
> (ii) `GObject.Move` of the six `LoopTunnel`s is unchanged ??still unmeasured, and a tunnel's owner is a
> structure, so it is not a diagram move. **So R1 needs the WRITER, not a re-reading of the tunnels**: the
> `OpConnectFromWire_v0` of `docs/d1-build-plan.md` 짠11t, whose `Wire Source` is a wire-terminal reference.
> Raised by `archive/peer/2026-09-17-priorart-priorart-connectfromwire.md` A4 (`unread-evidence`), which asked for
> exactly this disposition in writing.

**R2 ????CLOSED as written, and REPLACED by an instrument problem (2026-09-17, material route-B session 1).**
The original R2 ("`OpConnectNested_v0` is not ExecState-verified") is answered: **`OpConnectNested_v1` is
FUNCTIONAL warm AND cold** ??`tools/bench/test_opconnectnested_v1_cold.log`, 7 pass / 0 fail in a restarted
LabVIEW, cold `ExecState 1`, 14,666 B ??and it made 8 wires in the real VI (`build_d1_v0_run9.log`).

?뵶 **What replaces it: the ACCEPTANCE INSTRUMENT is unsound.** `docs/d1-build-plan.md` 짠11u.1 and
`archive/peer/2026-09-17-rbw-deleted-wires-run9.md` (codex, ANSWERED, accepted in full): the
"wire SURVIVES `remove_bad_wires_scripted`" gate is IMPLEMENTED at `tools/recipes/build_d1_v0.py:1118-1121` as
**uid equality of two `Terminal.Connected Wire` reads**, which measures object identity, not survival ??
`Terminal.Connect Wire` 6349C03 returns nothing, and run 9's row 1 (`#1359` t4, `26189 -> 26412`) ended with a
**non-zero** wire while being counted as deleted. So **no gate in this plan may cite RBW-survival as evidence
that a wire is good**, and `toolkit-capabilities.md:56`'s sentence about it is wrong about its own implementation.
Use, in this order: **`ExecState 1` on a scratch built to be otherwise runnable** (the skill's unforgeable
signal), plus each endpoint's connected-wire state and owning diagram; and, when judgement authorises the second
op, **`Wire.Is Broken?` 6371004 + `Wire.Terminals[]` 6371003 from a HELD terminal reference**. That reader is
**not built** and is a judgement call, not this plan's.

**R3 ??a control terminal is not a `Node`.** `#2222` t0's source is control `Z/dZ` uid 47 with an **unnamed sink**,
so neither `wire_control` (name on both ends) nor `OpConnectNested_v0` (`Nodes[]`) is known to reach it. 1 row.

**R8 ???뵶 two rows ARE cross-diagram, so 짠8's claim 1 is not absolute.** MEASURED: `#1359` t5 ??`#10068` and
`#29874` t2 ??`#29240`; both sources **stay on `Diagram #639`** (REV 4 짠5a: the three `Quotient & Remainder` nodes
stay on 1.1) while both sinks move into 1.2's body, and **both sinks are unnamed**. That is exactly A's
unbuildable shape (two nested diagrams, second `To More Specific Class`, MEASURED `ExecState 0`). Three ways out,
all unmeasured and all judgement: move `#10068`/`#29240` into 1.2 as well (they are *Q&R* nodes that REV 4 says are
in neither slice ??moving them is a scope change); route the two values through a queue or tunnel whose sink end is
named; or accept the fifth op. **2 of B's 82 connections.**

**R4 ??the reparent set is 8, not 6** (짠2c). Correcting 짠5d is bookkeeping; **missing it costs 3 more 5001s**,
which is what run 7 measured.

**R5 ??deleting `#48` and `#376` is new.** It bares `#6384` t8 (w541 `error in`) and `#12589` t1 (w9113). Both are
re-made in 짠4/짠5, but the S3b census must be widened to them, exactly as REV 4 짠7.2b requires for shared nets.

**R6 ??the pool.** B's `Q_free`/`Q_work` pool of 20 images is fresh construction that the original does not have;
step C proved the shape at 8 slots in **replay**, never at 20 in **live** mode (`decisions.md:22` sets 20).
ASSUMED transferable.

**R7 ??the `Local` count.** No step here creates a `Local` or a panel object; `Local` stays **8**,
`ControlTerminal` stays **114**. MEASURED as a gate in A (S1q/S4s) and carried unchanged.

---

## 7. Prediction contract

### S ??structural, one run, one log (`tools/recipes/build_d1_route_b.py`, not written)

| gate | assertion, with counts |
|---|---|
| **S0** | `TRANSPORT = "queue"`; original md5 `2a78e17c449cacdaf5da389818526859` read **before**; `OpMoveIn_v0` (UID control `'UID 3'`), `OpCreateEqual_v0`, `OpCreateConstOnTerm_v0`, `OpStopFromNode_v0`, `OpConnectNested_v0` all present; handles recorded |
| **S1** | fresh copy, before any edit: `Diagram 170`, `Node 626`, `Wire 1902`, `LoopTunnel 132`, `ControlTerminal 114`, `WhileLoop 3`, `Local 8`, `SubVI 98`, `Function 181` (MEASURED exact in run 7) |
| **S1t** | `#22700`, `#23020` deleted ??`SubVI 98??7`, `Function 181??80`, `Node 626??24`, `Wire 1902??899`, bare named sinks `28??6` (MEASURED 4/4, run 6) |
| **S1d** | **new in B**: `#5058`, `#48`, `#376` deleted ??`SubVI 97??4`, all three uids gone; the bared sinks of w541 / w9113 enumerated and carried into S3b |
| **S2** | 3 new While loops + 1 pool For loop on `Diagram #686` ??`WhileLoop 3??`, `ForLoop +1`, **`Diagram 170??74`** (A predicted 173 for three loops; the pool loop is the fourth body ??ASSUMED). `#637` still exists and still owns `#6810` and `#22082` |
| **S2d** | 3 fresh `drop_subvi` ??`SubVI 94??7`; each new subVI's owner chain reads `uid ??<body Diagram> ??<the right WhileLoop>` (`OpOwnerChain_v1`) |
| **S1q** | 8 `Obtain`: `Q_free`/`Q_work` bounded **20**, `Q_meta`/`Q_res`/`Q_good`/`Q_rmeta` unbounded, `Q_focus`/`Q_focusback` bounded **1**; `Local` still **8**, `ControlTerminal` still **114** |
| **S3** | **21 objects reparented** (17 ??1.2, 4 ??1.5, 0 ??1.7) + **8 control/indicator terminals** into their loops, each verified by `OpOwnerChain_v1`; `#12589`, `#11639`, `ControlTerminal #642` still owned by `Diagram #639`; `Diagram` count unchanged **by the moves** |
| **S3b** | census over every moving node **and every node sharing a wire with one** **and** the sinks bared by S1d; **wires cut == wires re-wired**; the cut set ??the 13 짠8 crossings |
| **S3c** | 8 shift registers created and wired (4 / 2 / 2); `ControlTerminal` still 114; all 114 `panel_wiring` labels present |
| **S3d** | `IndexMode 0` on the 6 whole-array tunnels: `cross size`, `# of bead 4 packs`, `4 pack remainder`, `Array of cal clusters`, `Real-space cosine window`, `Cosine bandpass\nfor Hilbert ` |
| **S3w** | **the connection ledger, REVISED 2026-09-17**: 27 name-wires + 20 `wire_sr` + 5 `OpCreateConstOnTerm_v0` + 6 `OpConnectNested_v0` (same diagram) + **2 R8 + 3 `ForLoop` newline-named sinks by `OpConnectNested_v1`** + 18 R1 + 1 R3 = **82**; every row reports WIRED or names its blocker. **Gate: 0 rows NO-ROUTE** ??which, on today's fleet, **19 rows cannot meet** (18 R1 + 1 R3), down from 21. ?좑툘 Every `wire_control` call MUST pass `src_diagram_index` = the Traverse(`Diagram`) index of the diagram the control terminal actually lives on (**43** for `Diagram #639` before any reparent) ??짠11u.2; omitting it is what produced run 9's six 5001s |
| **S3g** | the fresh kernel's 6 extra inputs each carry a constant with the `gpu_kernel_v1_fp.json` value, read back by `OpConstValueN_v1` |
| **S4** | each new loop's conditional terminal is driven by its own sentinel `Equal?` ??non-zero `CondWireUID` on 1.2 / 1.5 / 1.7 via `OpLoopEndRef_v0`; **`#637` unchanged: terminal 648 ??wire 3457 ??`#11639`** |
| **S4s** | sentinel enqueues present on their writers' diagrams, literals **??** (`Q_meta`/`Q_rmeta`/`Q_focus`) and **empty array** (`Q_res`/`Q_good`); 1.7's append gated by the ?? test; no new panel object |
| **S5** | `new_since('Invoke')` empty, `remove_bad_wires_scripted`, **`ExecState 1` warm**, saved, size recorded |
| **S6** | cold re-open in a restarted LabVIEW: `ExecState 1`, `Diagram 174`, `WhileLoop 6`, `ControlTerminal 114`; original md5 unchanged **after** |

`ExecState` is meaningless between S1d and S4 (the deletes and moves cut wires ??MEASURED 짠2b). Read it at S5/S6.

### N1 ??numeric, rule 1a ??**unchanged from REV 4 짠10**

Fixture replayed through **1.2 + 1.7** on a **scratch copy of D1** by feeding `Q_work` from `IMAQ ReadFile`; gate =
the `.tra` against the original's, **first 10,018 frames** within `decisions.md:38`; whole-fixture figures reported
separately (STATUS OPEN 16). ?좑툘 **B changes the rule-1a claim's shape**: in A the 13 shared kernel inputs were
*re-wired from the same sources*; in B the kernel is a **fresh node wired to the same sources by name**, and the 18
R1 rows are the ones where "the same source" is not yet demonstrable ??so N1 is the **only** acceptance for them.

### F1 ??live, 5 min (uncapped since 짠11h deleted the TIFF writer) ??**unchanged**

`drive_original_copy_v3.py`'s method (16/16): second COM apartment, 3 picks in the Image display, `Done Picking
Beads?`, 3 token-gated `choose bandpass` clicks, absolute save path. Camera only, rig disassembled, **no beads** ??
tracking errors without beads are expected and are not a failure. Records: frames acquired / tracked / written; both
buffer-number series with the 짠8 reconciliation; `Q_work`/`Q_res` high-water marks; the slot ledger; handles;
the TSV growing (N/A if the tracked-result count is 0).

### F2 ??stop / restart ??**unchanged**

`stop (end)` by `SetControlValue`; **all four loops exit** ??1.1 on the panel Boolean, then 1.2 / 1.5 / 1.7 on the
sentinels, in that order; no error 1122; the `.tra` written and re-openable; restart 15 s; stop again; close without
saving; scratch deleted; original md5 unchanged. Inherits STATUS OPEN 17b (score the **stop**, not the restart).
No `VISA Close` gate ??the original has none and D1 adds none.

---

## 8. What B does NOT need

1. **Almost no cross-diagram index wiring ??2 rows, not 17.** A's wall (`d1-build-plan.md` 짠11n.2) was a wire whose
   **source is on `Diagram #686`** and whose **sink is inside a new loop body** ??two nested diagrams, needing a
   second `To More Specific Class`, **MEASURED unbuildable** (`build_opconnectnested_v0_run1.log`:
   `W4 ROUTE A wired: ExecState 0`). In B that shape survives in **exactly two rows** (R8); the 6 index rows of 짠4
   are inside 1.2's body and R1's candidate (i) is inside `Diagram #686`, both of which `OpConnectNested_v0`
   expresses as built. ?좑툘 Stated exactly: the claim is **17 ??2**, not zero.
2. **No tunnel-source resolution.** A had to walk `Tunnel.Outside Terminal 6356001 ??Connected Wire 634A000 ??
   Wire.Terminals[] 6371003 ??Is Source? ??Owner` to find a named origin for 17 rows, and MEASURED that 16 of them
   end at `outer_source: null` ??there is no named origin to find. B never asks the question: it branches from
   `#637`'s own outer terminal, which it addresses **by index**, on the same diagram. (This is what makes R1 a
   *tunnel-creation* problem rather than a *source-resolution* one ??a strictly smaller open question, but still
   open.)
3. **No `Local`, no user event, no DVR** ??짠11c stands: 8 queues and end-of-stream sentinels. `Local` stays 8.
4. **No second reader of `stop (end)`** ??`ControlTerminal #642` stays in 1.1 (짠11c).
5. **No fifth op is authorised by this plan.** B uses the four the freeze lift closed at (`CreateEqual`,
   `CreateConst`, `CreateConstOnTerm`, `ConnectNested`) plus `OpStopFromNode_v0`, `OpMoveIn_v0`, `OpLoopEndRef_v0`
   and `OpOwnerChain_v1`. R1's resolution may need one; that is the judgement session's call, not this file's.

---

## 9. What this plan does not decide

* whether route B is started at all (짠11p reserves it);
* R1's resolution (tunnel creation from an unnamed source) ??(i), (ii) or a new op;
* whether `GObject.Move` for the six structures is acceptable under rule 1a given that B's premise was "build
  fresh" ??it is the *same* mechanism A used, so the rule-1a position is unchanged, but the **premise** of B is
  weakened and the judgement session should say so explicitly;
* whether N1 alone may carry the 18 R1 rows' rule-1a equivalence.

---

## 11. R1's two `LeftShiftRegister` rows ??the queue is REFUTED; the register moves with its node

**MEASURED 2026-09-17 18:0x** (`tools/bench/diag_sr_transport.log`, 10 pass / 0 fail, original md5 unchanged
before and after; `tools/bench/sr_transport.json`), after `archive/peer/2026-09-17-priorart-routeb-run3-{codex,
opus}.md` refuted the queue. These are the numbers a future session should start from:

| | row 8 | row 12 |
|---|---|---|
| sink (moves to 1.2) | `#1359` t1, unnamed, `index_mode` **1** (auto-indexing) | `#29874` t3, unnamed, `index_mode` **1** |
| LEFT register (stays on 1.1) | **#9025**, inside wire **w9097** | **#29512**, inside wire **w28039** |
| RIGHT register | **#9018**, inside wire **w9215** | **#29505**, inside wire **w29591** |
| initialiser = the register's NAMED source | `#8953 Initialize Array`.`initialized array`, w**9051** | `#28124 Initialize Array`.`initialized array`, w**29122** |
| the WRITER of the right register | `#1359` **t2**, **unnamed** | `#29874` **t5**, **unnamed** |
| what the right-inside wire's SOURCE actually is | **`LoopTunnel #9227`** ??not a node at all | **`LoopTunnel #29616`** |

Three consequences, none of them an opinion:

1. **`queue_node('obtain', ??` cannot be typed here.** It takes the element type from a NAMED OUTPUT of a node
   (`tools/gscript.py:1068-1074`), and the only candidate ??the writer of the partner right register ??is
   unnamed; on the machine its wire's source is a `LoopTunnel`, which is not a node. The queue plan could not
   have passed its own gate.
2. **The sink AUTO-INDEXES.** `index_mode 1` means `#1359` t1 feeds the For loop an ARRAY and sets its N. A
   queue delivering one element per frame-loop iteration is a different computation (rule 1a), and gate **S3d**
   asserts `IndexMode 0` on six OTHER tunnels ??these two have no index-mode gate at all. **Any future design
   for these rows must state what happens to `index_mode`.**
3. **These are READ-WRITE registers.** The moving node reads t1/t3 and writes t2/t5. A transport that carries
   only the read side silently stops the loop-carried state from updating.

**The mechanism this project already decided** (`docs/frame-loop-wire-graph.md:397` "each must live in exactly
one loop"; `docs/d1-build-plan.md:446`, where `#376` moves into 1.7 **with its two shift registers**) is: the
register moves with the node, built by `add_shift_reg` + `wire_sr`, which 짠2b already budgets 8 of. The queue
form was dispatched, attacked and abandoned on 2026-09-14
(`archive/peer/2026-09-14-stage2-shiftreg-primitive.md:126-129` ??replaced by `Loop.Add Shift Register`
**6361000** = `OpAddShiftReg_v0`). **Honest limit, not to be read as a free fix:** `wire_sr`'s `LeftOutNode`
variant reaches a *top-level* node via `VI.Block Diagram` (`docs/toolkit-capabilities.md:42`), and the two
initialisers sit on `Diagram #686`, which `docs/diagram-hierarchy.md:95-97` measures as a **FlatSequenceFrame**
diagram, not the top level. Which route is cheaper is NOT settled by any evidence on disk.

**The one question judgement must answer:** do `#1359` and `#29874`'s registers move into 1.2 with their nodes
(making `1.2` the single writer, as the rule says), or does the value cross some other way? A material session
may not make that call ??it is the computation, not the scheduling.

### 11a. `#2222` t0 ??`Z/dZ` (R3) ??MEASURED, and the temporary sink turns out to be optional

`tools/bench/diag_sr_transport.log`: `Z/dZ` is on the panel exactly once as a CONTROL (uid 47) and **it already
drives wire w730**; `#2222` t0's wire **is w730** ??the same net, whose three terminals are the control terminal
(source, owner `Diagram #639`), `Tunnel #2276` (sink) and one empty slot. **No named sink on the net**, which is
exactly why `wire_control` cannot reach it.
So the branch source exists on the pristine original and the temporary sink is only needed if the moves cut
w730. `from_ctl_unnamed` therefore reads the control's own wire first and only then considers a temporary.
?좑툘 **The temporary is DISARMED** (`TEMP_SINK_AUTHORISED = False`): creating a bare `Equal?` with `src_names=()`
contradicts `OpCreateEqual_v0`'s recorded contract (both operands come from `Get Outputs`,
`docs/toolkit-capabilities.md:52`) and `docs/NAMES.md:468-480` records that an invalid terminal refnum produces
an **error-1055 MODAL DIALOG that an error-out indicator does not silence** ??disqualifying unattended.
The delete step itself is safe and needs no new measurement: a branched net is ONE `Wire` object, so deleting
the disposable SINK NODE (never the wire) plus Remove Bad Wires keeps the branch
(`archive/peer/2026-09-15-opwiresource-fail3-branch-wire-is-one-object.md:24,:32-35,:49-52`).

---

## 10. `OpGetErrors_v0` ??the third attempt at `VI.Get Errors` 452, and WHAT IS DIFFERENT NOW

> ?뵶 **NOT AUTHORISED ??STOPPED BY ITS OWN PRIOR-ART REVIEW, 2026-09-17 16:48/16:56, and nothing below was
> built.** `-Dual`, both arms independently: `archive/peer/2026-09-17-priorart-opgeterrors-codex.md`
> (`refuted-already`, `already-failed`) and `??opus.md` (`settled-already`, `refuted-already`, 5 횞
> `contradicted`, `helper-exists`, `already-measured`). The stop rests on `docs/d1-build-plan.md:859-860` ??
> *"No diagnostic, framework, or review cycle before F1/F2 ??third op ??PHASE "full" ??save ??N1 ??F1 ??F2"* ??
> a judgement decision taken THE SAME DAY. That file was opened and the citation covers this case exactly, so
> the "refute the citation" override is not available. Two corrections the review made to the text below stand
> regardless: **짠10b.1 is confirmed** by `tools/gscript.py:2094-2123` vs `:2156-2158`, and **짠10c.2's "no donor
> is known to exist" is CONTRADICTED** by `docs/toolkit-capabilities.md:187-189` plus the NI thread's snippet ??
> a snippet is a PNG carrying diagram code, so the donor is *manufacturable*, not merely findable.
> The section is kept so a future judgement session inherits the plan instead of re-deriving it.

Authorised by the judgement session (brief, 2026-09-17, decision 3) as the reader for "why is this VI
`ExecState 0`", which OPEN 39 names as the missing instrument. **Budget: 2 attempts.** This section exists to be
attacked by the prior-art review before a line is built ??the two previous attempts are recorded FAILURES and
CLAUDE.md's "when a diagnosis is GUESSED twice, build the reader" is not a licence to rebuild the same thing the
same way.

### 10a. What FAILED, twice, and exactly how ??read from our own files, not remembered

| attempt | record | symptom |
|---|---|---|
| 2026-09-09 | `docs/toolkit-capabilities.md:259` | "Invoke node created with only reference/error terminals, with and without the private ini tokens" |
| 2026-09-14 | `docs/toolkit-capabilities.md:157` | same signature: "node created with only `reference out` / `error out` ??**no `Errors`, no `Details`**" |

The recipe from those attempts is still on disk: `tools/recipes/build_opgeterrors.py` (107 lines). It calls
`g.build_invoke(OP, "VI Server:VI", "452", ??` at line 34 and then *probes for output terminals by creating
indicators on terminal indices 0??* (lines 49??9), i.e. it infers attachment from what a later walker can see.

### 10b. The four things that are different, each with its citation

1. **THE CREATOR'S ERROR IS NOW A RAISE ??but only on the PROPERTY path.** `OpBuildPN_v1` exposes the creator's
   real `error out` (pane index 15; index 10 with the same name is a sink) and `build_property()` **raises** on it
   (`tools/gscript.py:2150-2163`). `build_invoke()` does NOT: it drives `OpBuildInvoke_v0.vi`, whose "`error out`
   indicator is now unwired, so read creator errors from the dialog watchdog" (`tools/gscript.py:2094-2123`).
   ??**The first build is `OpBuildInvoke_v1`, not `OpGetErrors_v0`.** `docs/toolkit-capabilities.md:247-249` says
   this in as many words: *"an `OpBuildInvoke_v1` with the same exposure is needed for the Invoke case"*. Without
   it a third attempt would produce the same uninterpretable result as the first two, which is the definition of
   `repeated-failure-class`.
2. **"No error" is NOT a verdict that a member attached** (`docs/toolkit-capabilities.md`, prior-art A3-iv,
   2026-09-16): `Control.Value` 633200D ??a *valid* ID on the wrong class ??created a node with no `Value`
   terminal and **no error at all**. The robust check is the **data-terminal-name census** on the created node
   (`tools/recipes/build_opcaseframes_v0.py:49-58`: exactly one data SOURCE terminal, its name printed, never
   guessed). So the acceptance here is: after creating the 452 Invoke, enumerate the node's terminals and print
   their NAMES; `Errors` / `Details` present = attached, `reference out` / `error out` only = refused.
3. **The three probes that "proved" private members unreachable were VOID, and the reason is known**:
   `net_map` / `OpNetInfo_v1` "does not see nodes created by another op in the same session"
   (`docs/toolkit-capabilities.md`, RESOLVED 2026-09-14, `tools/bench/probe_stale_nodes.log`). The old
   `build_opgeterrors.py` verifies exactly through that broken route. ??read terminals with `node_terms()` on a
   re-read report, not with the walker, and carry a **CONTROL** (a known-good public method, `Terminal.Create
   Indicator` 6349C02) through the identical code path in the same run ??the discipline
   `docs/toolkit-capabilities.md` imposed after probe run 1 concluded a limitation from a broken reader.
4. **The COM poison guard is in** (STATUS OPEN 34, `??d1-route-b-1.md` 짠2, 11/0), so a refused creator call no
   longer leaves the client in a state where every later read lies.

### 10c. The order, and the two stopping rules

1. `OpBuildInvoke_v1` = `OpBuildInvoke_v0` + the creator's real `error out` and `Outputs` surfaced, built by the
   same additive-on-a-proven-front-half pattern as `tools/recipes/build_oploopendref_v0.py`. Gate: the control
   (`Terminal.Create Indicator` 6349C02) attaches and its terminal names print; a deliberately bogus ID `FFFFFFF`
   raises 1077.
2. `OpGetErrors_v0`: create the 452 Invoke on `VI Server:VI` through v1. **If the creator raises, the answer is
   "the ordinary setter refuses a private member" and the next step is `Invoke.Set Method (Allow Private)`
   6370003 with `ID String = "Get Errors"` and `Allow Alternate Names? = TRUE`** (`toolkit-capabilities.md`, the
   three points from `archive/peer/2026-09-14-private-method-attach.md`: set the CLASS first, the setter takes an
   ID *String*, no special VI-reference option is needed). If THAT refuses, the recorded fallback is
   `Create from Reference` from a donor ??**not attempted this session; it needs a donor VI that contains the
   node, and none is known to exist in this project.**
3. **Functional test before any use**: a scratch VI deliberately broken in two independent ways ??one unwired
   REQUIRED input on a subVI call, and one type-mismatched wire ??and the op must NAME the broken object's uid
   and print the error text. A `Get Errors` that returns an empty list on a VI whose `ExecState` is 0 is a FAILED
   op, not a clean VI.
4. **Budget 2.** Two failed builds ??stop, write both logs' failure lines, hand back. Nothing in route B's
   build order depends on this op existing.

### 10d. What this op does NOT decide

It reports; it repairs nothing. The route-B run may use its output to name what is broken, and only rows the op
NAMES may be fixed ??the budget-2 rule in the brief exists so that "ExecState 0" never again becomes a licence to
guess at 63 wires.


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-18
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this. Narrative ??`archive/2026-09-18-status-cycle34-n1.md` (latest) + `??cycle23-close.md` + the `archive/2026-09-1[678]-status-*.md` set.
?럦 **D0 IS DELIVERED** (cycle 31) 쨌 **N1 IS ACCEPTED** (cycle 34) **??D1 is open.** Banner VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠3; facts `??cycle31-d0-delivered.md` 짠1?벬? (read **짠4** before the first D1 click).
?넅 **USER RULE 17:5x = `docs/cycle27-plan.md` Pre-decided 9 ??EVERY GUI action is capture ??locate ??act ??capture ??confirm; derived or remembered coordinates are NEVER clicked blind.** It turned v4's 13/3 into v5's 39/1.
## START HERE
1. **Cycle plan = `docs/cycle27-plan.md`** (cycle20/21 plans `superseded`; motor plan `docs/motor-limit-assurance-plan.md` **짠A.1 + "P2 live findings"**; master `docs/pre-rig-master-plan.md`; decisions `docs/decisions.md`; D1 `docs/d1-route-b-plan.md`, paused).
2. ?뵶 **NEVER patch a file with a `py - <<'EOF'` heredoc** ??one truncated **this file to 0 bytes** on 2026-09-17.
3. ?좑툘 `peer.ps1` only as `powershell -Command "& 'tools/peer.ps1' ??-TaskFile <f>"`, `-TimeoutSec >= 780`. ?넅 **2026-09-18 (user, TRIAL): codex's roles ??claude roles** ??failed prediction = `-Agent claude -Role hypothesis` SINGLE arm (`-Dual` only for a second opinion on our own tools); `-Kind fact`/`-Kind prose` with no `-Agent` ??fable/low thin; `outcome_review.py` ??fable/medium thin. Check routing free with `-DryRun`.
4. Six more operating hints (prior-art log naming 쨌 front panel open for edits 쨌 `guard_cycle`'s `FIXED:` release 쨌 `py_compile` tripping BUILD_RE 쨌 짠11u unsound 쨌 짠10 not authorised): **`archive/2026-09-18-status-cycle1-census.md` 짠1**. ?좑툘 `BUILD_RE` also fires on a plain `cp a.py tools/recipes/b.py` ??quote both paths (cycle23-close 짠3).

## LabVIEW execution lock

```yaml
labview-lock:
  status: released   # cycle-35 dispatches 3+4 (read-only) finished 20:17 / 20:25, LabVIEW left killed, originals' md5 unchanged. MEASURED on BOTH originals: a byte-identical claudeDev copy reads **ExecState 0 COLD / 1 with the ORIGINAL preloaded read-only** ??the linkage artefact belongs to the READING INSTANCE, not the file (`tools/bench/diag_d0_execstate_preload.log` 9/0 rc=0; `tools/bench/diag_d1_execstate_preload.log` 7/0 rc=0). Prose VERBATIM (md5s, handle counts, per-dispatch detail) ??`archive/2026-09-18-status-cycle36-relocate.md` 짠1.
  owner:
  since:
  purpose_now:   # ??**N1 IS ACCEPTED (cycle-34 judgement) ??D1 IS UNBLOCKED**: pre-bead-loss window k<10018 = ZERO exceedances over 50,201 valid bead-frames (max |dx| 4.857e-07 / |dy| 4.677e-07 / |dz| 1.279e-05 vs tol 1e-6 x,y and ~1e-4 z); the VI-level run reproduces the DLL numbers exactly, so the LabVIEW wrapper is numerically transparent (`tools/bench/n1_gpuk_vi_fixture.log`, 7/7, rc=0). ?좑툘 TWO items FLAGGED TO THE USER, NOT closed: (a) acceptance is on the PRE-BEAD-LOSS WINDOW, not the whole fixture; (b) the single z-LUT index flip at k1679/bead 4 (dz -4.667e-03, above the z tolerance) excluded by the FLIP mask. VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠2; record ??`archive/2026-09-18-status-cycle34-n1.md` 짠1/짠4.
  purpose_relocated:   # cycle-35/36 lock prose ??`archive/2026-09-18-status-cycle36-relocate.md` 짠1/짠2. cycle-34/32/30 ??`archive/2026-09-18-status-cycle34-n1.md` 짠1 쨌 23 ???쫈ycle23-close.md 짠1/짠2/짠3 쨌 22 ???쫈ycle22-close.md 짠1 쨌 21 ???쫈ycle21-wire-semantics.md 짠8/짠9/짠9a 쨌 20 ???쫈ycle20-close.md.
  motor:     # limits LEFT ON since 2026-09-18 15:37 (PI TMN 0 / TMX 39 in RAM, ASI SL/SU 짹2 mm), ports closed; an 18:13 D0 run then moved the magnet to 30 mm and they held. VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠2; detail ??`archive/2026-09-18-status-cycle34-n1.md` 짠1.
```
**Never assume an instance exited**: `tasklist | grep -i labview`. Fresh ??1,500 handles; unique scratch name/run.

## HARDWARE ??permission follows the RIG STATE. Current: **議곕┰ / ASSEMBLED** (machine key `rig-state:` below)
遺꾪빐 = motors ??ASI ??camera ??쨌 **議곕┰ ??WE ARE HERE** = camera ?? motors/ASI ONLY through `tools/motor_gate.py`
inside the envelope 쨌 ?ㅽ뿕以?= ?????? ?좑툘 ASI carve-out **RETIRED** (rule 1b); **only the user announces a state
change**. Rotor counter **0** 쨌 magnet full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz, never write
`BinningHorizontal`; **a session open RESETS ROI *and* exposure** ??the acquisition loop applies
`tools/bench/camera_contract.py`. **No beads on the rig.**
?넅 **SAFE MOTION ENVELOPE = THE CONTROLLER LIMITS + the gate's command-class denies** (user, 2026-09-18 15:2x at the
rig). PI `SPA 1 0x15/0x30` ??TMN 0 / TMX 39 (RAM, **never WPA**) 쨌 ASI `SL/SU` absolute mm X ??.8475??.1525,
Y ??.7744?╈닋0.7744 (persistent, **never SS Z**), written+verified by `py tools/motor_gate.py --session start|end`
from the user-editable `tools/bench/motor_limits.json`; `--execute` refuses without `tools/bench/motor_session.json`
**and** a fresh matching readback. The gate still refuses ?ㅽ뿕以? every ASI home/zero/save, PI
GOH/FRF/DFH/RON/POS/SPA/WPA and all rotor motion (self-test `selftest_motor_gate2.py` 74/74).
??The 15:37 run (8/10, L4 a FALSE PASS) is SUPERSEDED by the 16:0x retest ??`??cycle29-retro-trap.md` 짠7. Limits LEFT ON (PI TMN 0 / TMX 39 **in RAM**, ASI SL/SU persistent); **an 18:13 D0 run then moved the magnet to 30 mm and they held**.
rig-state: 議곕┰   <!-- set 2026-09-17 23:0x on the user's words ("?ㅽ뿕 1李⑤줈 ?앸궗?붾뜲, 由ш렇???좎??섎뒗 以? + "議곕┰ ?곹깭?먯꽌????踰붿쐞 ?덉씠硫?紐⑦꽣 ?덉슜??) 쨌 the gate's ONE machine-readable key, parsed by motor_gate.rig_state(); ONLY the user's announcement may set it to 遺꾪빐 / 議곕┰ / ?ㅽ뿕以? Keep it at the start of the line, unquoted. -->

## Where things stand ??the three ??lines VERBATIM in `archive/2026-09-18-status-cycle36-relocate.md` 짠4
??tunnel ops BUILT + FUNCTIONALLY VERIFIED (38/38, ?좑툘 **do NOT re-run the recipe, run 1 is the record**) 쨌 ??the "ZERO runnable experimental VIs" gap is BROKEN ??`tools/bench/drive_original_copy_v5.py` drives a plain copy of the original unattended end to end, twice 쨌 ??N1 accepted ??the GPU kernel is cleared for D1 (lock block above). **Order is D0 ??D1 ??D2** (`docs/cycle27-plan.md` Pre-decided 1). Earlier: `archive/2026-09-18-status-cycle22-close.md` 짠2 쨌 `?쫈ycle20-close.md` 짠1?벬? 쨌 `?쫈ycle21-wire-semantics.md` 짠9/짠9a/짠10 쨌 `?쫈ycle19-flatseq.md`.

## OPEN ??**items 1??0 VERBATIM in `archive/2026-09-17-status-runner-build.md` 짠2**; only the live ones below
??**CLOSED ??all five VERBATIM in `archive/2026-09-18-status-cycle36-relocate.md`**: **32** D0 delivered 18:13, 짠5 (?좑툘 the next outcome review judges whether it answers "zero runnable VIs" ??do NOT close it unilaterally) 쨌 **55** `tmx_from` rule 4 deleted, 17/0, 짠6 쨌 **56** `audit_cycle` C7 repointed at the `status: current` plan, 짠7 (?좑툘 **STILL OPEN from retrospective-cycle31 F4: C4 understates spend** ??judgement `claude -p` sessions carry no COST line) 쨌 **51/52/52a** 짠8 쨌 **53's mechanical half** (16:0x, retest 10/10, self-test 76/76) 짠9.
38/39/41. ?윞 **DECIDED cycle 35 ??the flags are no longer an open question: both stay False PERMANENTLY** (Pre-decided 13), and the 3 NO-ROUTE rows follow `docs/cycle15-plan.md` Pre-decided 1/2/3. Run 3 was 63 WIRED / 0 FAILED / 3 NO-ROUTE at ExecState 0, but that ExecState was read **cold and therefore measures subVI linkage** (Pre-decided 14a/16, two independent controls); it was equally **over-determined** by the skipped `s1q`/S4b, so run 3 is neither exonerated nor convicted until the baseline read lands ??**`docs/d1-route-b-plan.md` 짠11/짠11a**, archive 짠3 쨌 `VI.Get Errors` 452 NOT built (prior-art stopped it, `docs/d1-build-plan.md:859-860`; 짠10 NOT AUTHORISED) 쨌 **judgement only ??the stall watchdog's liveness test**, both arms ANSWERED and REFUSING "false positive", remedy not built (`archive/peer/2026-09-17-stall-preexperiment-sleep-{codex,opus}.md`).
53. ?뵶 **The JUDGEMENT half STAYS OPEN, both review arms:** `POS` only declares the present location to be a coordinate and PI's `0x15/0x30` are relative to that zero, so **nothing we can read proves the controller zero still equals the ORIGINAL physical zero** ??i.e. that 0??9 still fences the intended physical window. VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠9; dispositions `archive/peer/2026-09-18-pi-err5-unreferenced-{codex,opus}.md`.
54. ?뵶 **`retro_done` is armed by an INTENTION, not by an answer** ??`guard_bash.py:226-227` marks the session closed the instant a `retrospective.py` command is typed, while the gate it mirrors, `guard_cycle.newest_retrospective()`, requires an **ANSWERED** archive; nothing ever clears the mark (`{"dispatches":0,"retro_done":true}` in **3 of 17** session files). **Repair NAMED, deliberately NOT BUILT**: `guard_session` should read `guard_cycle`'s own predicate. ?좑툘 The "over-trigger / gate deadlock" reading was REFUTED ??`retrospective.py:299` "END IS ALWAYS NOW"; **the retrospective is the LAST thing a session runs**, and a measurement dispatch never waits on one. ?넅 THE SAME TRAP WITH A DIFFERENT MOUTH ??**a `claude -p` session CANNOT "take results as they arrive"**: cycle 33 ended its turn on two backgrounded hypothesis peers, both paid opus/max cells were killed at 600 s with no `COST:` line, cycle 33 closed with no retrospective, and cycle 34 spent $5.88 re-asking. **THE RULE: dispatch in the FOREGROUND and wait ??and when something must run in the background, HOLD THE TURN OPEN until it lands.** An orphan detector is deliberately NOT built (Pre-decided 2). VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠10; reviews `archive/peer/2026-09-18-retro-closes-session.md` + `archive/peer/2026-09-18-retrospective-cycle34.md`.
42/43/46/47. **VERBATIM in `archive/2026-09-18-status-cycle20-open-items.md`** ??42 ?좑툘 39 undisposed reviews + `audit_cycle` A2/A3 SELF-REFERENTIAL, not fixed 쨌 43 ??`guard_cycle.fixed_claim()` FIXED (step 1, T1?밫6 + B1/B2) 쨌 46 ?좑툘 `SetCommand_signed.vi` is on NO disk 쨌 **47 ?뵶 JUDGEMENT: the audit A1/A2/A3 remedy is NOT a `logclass` entry; opus reads `device-failed`, threshold 1.** 쨌 48/48a/49/50 ??ALL FOUR CLOSED, verbatim in `archive/2026-09-18-status-cycle22-close.md` 짠3.

## NEXT
?뵶 **USER, 2026-09-18 21:3x (after watching the D0 copy run its experiment loop live ??"?곷떦??怨좊Т?곸씤??吏湲덉? 萸?
?섍퀬?덈뒗嫄곗엫?"): TWO CYCLES SINCE D0 HAVE NOT TOUCHED D1. The next cycle's FIRST ACT is a D1 BUILD dispatch
(`docs/cycle27-plan.md` Pre-decided 1/6; route B per `docs/d1-route-b-plan.md`, ExecState read WITH the original
preloaded ??Pre-decided 14a/16). NO machinery repairs, NO watchdog reviews, NO audit fixes, NO doc relocation
before that dispatch has RUN; those go AFTER the D1 dispatch returns, or into the retrospective as findings. A
cycle that ends without a D1 build log is a wrong-ordering cycle by definition.**
??**N1 IS ACCEPTED AND D1 IS OPEN FOR BUILDING** (cycle 34) ??Pre-decided 6's "fixture comparison N1 before any D1
build" is **satisfied**: pre-bead-loss (k<10018) max |dx| 4.857e-07 쨌 |dy| 4.677e-07 쨌 |dz| 1.279e-05 vs 1e-6 (x,y)
/ ~1e-4 (z), **0 exceedances over 50,201 valid bead-frames**, DLL numbers reproduced exactly, so `GPU_kernel_v1.vi`
is numerically transparent (`tools/bench/n1_gpuk_vi_fixture.log`, 7/7, rc=0). ?좑툘 The retrospective is the **LAST**
thing a session runs (OPEN 54); `peer.ps1` runs ONLY inside `py tools/bgrun.py ??-- powershell -Command "&
'tools/peer.ps1' ??` (`??cycle29-retro-trap.md` 짠4).

??**Dispatch 1 DONE (cycle 35, read-only) ??`Count` is NOT an indicator: it is CONTROL uid 28051** (`is_source`
True) driving w30530 into `Equal?` #29111 term `x` and `SelectorTunnel` #31929 of `CaseStructure` #28709, on
Diagram #15795 inside `Sequence` #15649 inside **`EventStructure` #15544**; WRITTEN by two implicit `Property`
nodes labelled `Count` (`Value` = SINK): #32191 on Diagram #12960 and #30688 on Diagram #28741. Table, the 8
Locals and the two measured limits ??**`docs/NAMES.md` 짠`Count`**; `tools/bench/diag_count_indicator_run4.log`
16/0 rc=0. Meaning settled ??**Pre-decided 15**: a control the event structure writes, **never a bead count**, so
no harness may gate on it and D1 must not "fix" it; v5's red-marker counting stands. ??That run's alarming
side-note ??the D0 copy reading **ExecState 0 on disk** ??was chased the same cycle and is a READING artefact, not
damage: the file is byte-identical to the original and reads 1 under preload, so **D0's delivery record stands**.

??**Dispatch 2 DONE ??and D1's blockers are decided, not open.** `SR_QUEUE_AUTHORISED` and `TEMP_SINK_AUTHORISED`
stay **False permanently** ??the answer is "no", not "not yet" (**`docs/cycle27-plan.md` Pre-decided 13**),
because `docs/cycle15-plan.md` Pre-decided 1/2/3 (`:118-129`, still authoritative by its own frontmatter `:5-7`)
already decide all three NO-ROUTE rows: `#1359`/`#29874`'s shift registers **MOVE WITH THEIR NODES** into loop 1.2
(`add_shift_reg` + `wire_sr`, `index_mode 1` kept), and `Z/dZ` ??`#2222` t0 is **REORDERED** before the S3-ct
reparent of `ControlTerminal #403`. A build needing either flag True is the wrong build.

?뵶 **STEP 0 ??two one-line REPAIRS, or this session pays the same tax the last one did** (retrospective-cycle35,
`VIOLATION: repeated-failure-class | loss_min=16 | loss_usd=5.78`, **DISPOSED**): cycle 35 spent its first 20
minutes and $5.78 buying two paid reviews to clear two machinery faults whose repairs were already on file.
(i) `tools/lv_stallcheck.ps1` ??bind the command-line read to `(pid, CreationDate)` and skip leaves with no bgrun
log, so a benign sleep-poller stops being labelled a STALLED LabVIEW client and `guard_peer` stops blocking the
build; (ii) `tools/bgrun.py` ??set `BGRUN_LOG`, the one line that makes `audit_cycle` A2/A3's self-exemption work
(OPEN 42), and while in there fix (e) below. **Both are REPAIRS of existing devices, so Pre-decided 2 does NOT
block them** ??the same ground on which C7 was repaired this cycle. Each ships with its own test; an unverified
patch to gate machinery is worse than the fault. Run `py tools/violations.py` first: if `repeated-failure-class`
has reached 3, record a FINDING in `docs/violation-decisions.md` ??the device threshold stays SUSPENDED (line 10),
and a repair is not a device.

?뵶 **STEP 1 ??ONE LINE OF CODE, before any further 9-minute run. Restore the BASELINE `ExecState` read into
route B's `s1()`**: `tools/recipes/build_d1_v0.py:461` has it, `build_d1_routeb_v0.py:302-316` dropped it. Then
run route B with the two constructions above. **Why it comes first:** a cold-opened claudeDev copy reads
**ExecState 0 while byte-identical to an original that reads 1** ??measured on BOTH originals
(`tools/bench/diag_d0_execstate_preload.log` 9/9 rc=0; `??diag_d1_execstate_preload.log` 7/7 rc=0 on route B's own
`Min_Track N beads V6_ParallelLoop.vi`, md5 = the recipe's pinned `ORIG_MD5` at `:173`) ??and route B never
preloads, so its S5 gate (`:1289`, `gscript.py:1920-1921`) has been reading **subVI linkage**. The baseline read
separates "born 0" from "the build made it 0" inside the recipe's own instance, costs nothing, and makes the
recipe self-diagnosing. ?좑툘 **Do NOT add a preload to the build** ??it can cross-link and `g.save(TARGET)`
(`:1291`) would write that; preload is for read-only diagnostics only. Run 3's ExecState 0 was **over-determined**
(unwired conditional terminals from the skipped `s1q`/S4b), so this does not mean run 3 succeeded ??it means the
gate could not tell. Reasoning, the three accepted corrections and the rivals still unexcluded: **Pre-decided 14 /
14a / 16**; review `archive/peer/2026-09-18-execstate-linkage.md` (ANSWERED, opus/max, $2.8794, **DISPOSED**).

?뱦 **Before the first D1 click or stop read `archive/2026-09-18-status-cycle31-d0-delivered.md` 짠4** ??nine measured
facts D1 would otherwise re-derive (stop Booleans in `Diagram#639`; control positions unreadable over COM; ??.

?뱦 **Owed from retrospective-cycle35, cheap, do them in STEP 0's runner.** (i) **THIS FILE IS ~130 LINES** against
the ~100 rule ??relocate the cycle-31/34 narrative to `archive/` **before** adding anything new to it. (ii) The
stall reviewer's four sub-second falsification probes F1?밊4 (`tools/bench/peer_stall_c35.log:50-53`) were never
run; run them before any further review of that class. (iii) LabVIEW held **~57,800 handles** during the Count
runs (`diag_count_indicator_run2.log:59`) against the ~31,500 fresh baseline and no line remarks on it ??measure
it, do not pass over it (CLAUDE.md reference hygiene). (iv) A sub-session that finds it needs a NEW tool reports
the need and stops; it does not build it (finding 7, `tools/wait_logs.py`).

**Small, owed, not gates.** (a)(b) ??**DONE cycle 35** ??`tmx_from` rule 4 deleted + docstring + pin case
(`tools/bench/tmx_selftest3.log:19`, 17 pass / 0 fail, rc=0), and `audit_cycle` C7 repointed at the
`status: current` plan via the new `doc_lint.current_plans()` (`tools/bench/audit_c35.log:23` names
`docs/cycle27-plan.md`). (e) ?넅 **`bgrun`'s "always writes `BGRUN END|TIMEOUT`" guarantee FAILED on 4 logs**
(`diag_fstunnelterm_v2_panelcost`, `p2_open_copy`, `prose_cycle25`, `wait_runner_exit`) ??4th occurrence of the
OPEN-54 class, and it is a **repair of an existing device**, so Pre-decided 2 does not block it.
(c) `tmx_sendmode_probe.log` rc=1 is a throwaway
fixture, **no hypothesis review owed**; never `CYCLE_GUARD_OFF`. (d) `doc_lint` L6/A4 ??archived reviews still
blank. ?좑툘 `.claude/agents/material.md:26-29` still mandates the DEAD `MATERIAL=1` prefix and cannot be edited from
a cycle session, so **every material brief must carry**
`py tools/bgrun.py --material --max-min N --log tools/bench/<name>.log -- py -u <script>` (cycles 26/28/35 all
tripped on this ??do not redo the repair).

### FOR THE USER ??calls to overturn if you disagree
1. ?넅 **Route B's two authorisation flags are OFF PERMANENTLY now ??the answer is "no", not "not yet".** The three
   crossings they existed for are solved the way `docs/cycle15-plan.md` already decided: the shift registers move
   with their nodes, the `Z/dZ` wire is reordered. Nothing new was invented, and no build may ask for them again.
2. ?넅 **A sub-session created `tools/wait_logs.py` and I kept it.** Under `claude -p` a material session had NO
   permitted way to wait for its own background job ??the `until grep ??sleep` loop its own agent file mandates
   AND the Monitor tool are both refused by the allow list ??which is exactly the hole that killed two paid peer
   cells in cycle 33, and which I hit myself this cycle. I judged it plumbing, not one of the process "?μ튂" you
   told me to stop building. Say if you want it gone, or the allow list widened instead.
3. **Unchanged from cycle 34, still yours to overturn:** the harness RECORDS all 60 front-panel controls and SETS
   none (inventing values would be a rule-1a computation change); the VI moved the PI magnet 0 ??30.000 mm under
   its own control inside 0??9 with `TMX?=39` / `TMN?=0` holding; and I accepted the GPU kernel on the
   **pre-bead-loss window** ??over the whole fixture max |dy| is 3.135e-05, 31횞 your 1e-6, but all 19 exceedances
   are bead 4 at k??0023, after that bead's own first loss at k=10018, the other four clean at identical k; plus
   **1 bead-frame of 50,215** where CPU and GPU sit on adjacent z-lookup indices (k1679, dz ??.667e-03), excluded
   by the FLIP mask. Say so if any of it is too loose.

## Where to look ??`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** 쨌 **`docs/motor-call-site-census.md`** (P1) 쨌 **`docs/d1-route-b-plan.md`** = the build order 쨌 `tools/recipes/build_d1_routeb_v0.py`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

`Write` is disabled in this session, so this review exists only as this answer — the dispatcher's archive file is the copy of record. I took no lock, opened no VI, ran nothing, and modified no project file.

# PRIOR-ART REVIEW — `docs/d1-route-b-plan.md` (route B, the D1 build order)

**Verdict: NOT novel. 8 findings, 0 `novel`.**

The centre of it is one fact: **this plan describes a build that has since been written, run three times and measured.** Its §1 ledger, §4 mechanism table, §6 risk list and §7 contract were overtaken on 2026-09-17/18. Eighteen rows it calls "🔴 NO BUILT ROUTE" were wired — `Is Broken? FALSE` — by an op it says is "NOT BUILT". Four questions it hands to "the judgement session" were answered by name. The one gate it still rests on, `ExecState 1`, is the gate this project measured last night to be reading subVI linkage.

---

## PART A — THE DIRECTION

### A1 `settled-already` — every question §9, §11 and §11a reserve for judgement is decided, and on record as "no", not "not yet"

**Plan's side.** `:392-397` (§9) reserves four things; `:439-441` (§11): *"The one question judgement must answer: do `#1359` and `#29874`'s registers move into 1.2 with their nodes … A material session may not make that call"*; `:451-457` (§11a) leaves the `Z/dZ` temporary pending the same session.

**Other side**, `docs/cycle27-plan.md:89-100` (Pre-decided 13, judgement, cycle 35, 2026-09-18):

> **`docs/cycle15-plan.md`'s `## Pre-decided` 1–4 (`:118-130`) BIND the next D1 build, and BOTH authorisation flags stay `False`.** … `#1359`/`#29874`'s shift registers **MOVE WITH THEIR NODES** into loop 1.2 (`add_shift_reg` + `wire_sr`, `index_mode 1` kept …), and `Z/dZ` → `#2222` t0 is **REORDERED** before the S3-ct reparent … **the judgement session declines, and the answer is "no", not "not yet".** … a build that needs either to be True is the wrong build.

binding `docs/cycle15-plan.md:124-128`. Whether B starts at all (`:392`, and `authorises: nothing` at `:10`) is settled the other way too: `STATUS.md` NEXT makes a **D1 build dispatch the next cycle's first act**, and its "Where to look" line already calls this file **"= the build order"**.

*Scope:* covers §9 bullets 1–2, §11's closing question, §11a's temporary. Does **NOT** cover §9's third and fourth bullets — rule-1a acceptability of `GObject.Move` for the six structures, and whether N1 alone carries the R1 rows' equivalence. I found no decision on either; those stay open.

### A2 `refuted-already` — §10's `OpGetErrors_v0` route was stopped by its own dual review, and both of its fallbacks have since been measured away

**Plan's side.** `:461-542` keeps §10 *"so a future judgement session inherits the plan"*, ordering `OpBuildInvoke_v1` → 452 → `Invoke.Set Method (Allow Private)` (`:518-530`).

Beyond its own quoted stop (`:463-473`) and `docs/cycle15-plan.md:129-130` (Pre-decided 4), two things have changed:

- **The named fallback is useless.** `docs/cycle27-plan.md:106-112`: the bare-terminal census *"returned an IDENTICAL 375 bare named input terminals over 170/170 diagrams on a KNOWN-GOOD copy, so it discriminates nothing"* (`tools/bench/diag_d0_execstate_preload.log:26-36,:65-75`).
- **The method is probably unreachable on our transport.** `archive/peer/2026-09-18-fstunnel-v1-b4-execstate0-codex.md:156` — *"absent a LabVIEW-side Invoke Node/helper, direct COM invocation is unlikely … an inference from the exported interface"*; disposition `:191` — *"452 leaves the critical path"*.

*Scope:* covers §10 **as an inheritable plan**. Does **NOT** claim it is current work — the plan already marks it NOT AUTHORISED; the ask is that both corrections be written in before anyone inherits it.

### A3-a `contradicted` — "`OpConnectFromWire_v0` … is **NOT BUILT**" contradicts the toolkit table, this plan's own §6, and the run that used it 16 times

**Plan's side**, `:80-81` (§1, listed as MEASURED): *"It needs `OpConnectFromWire_v0` …, which is **NOT BUILT**."*

**Other side (i)** `docs/toolkit-capabilities.md:70`: *"✅ **`OpConnectFromWire_v0.vi`** … **BUILT + SAVED 2026-09-17, 16,524 B, ExecState 1**; run 2 42 pass / 1 fail"*.
**(ii)** The same file 190 lines later — `:269-271` treats the op as the answer: *"So R1 needs the WRITER … the `OpConnectFromWire_v0` of §11t"*.
**(iii)** It did the work — `tools/bench/build_d1_routeb_v0_run3.log:322`:

```
WIRED  #5058 t2 'cross size' <- from-tunnel 2580  OpConnectFromWire_v0 w3853 -> D[24].N[0].T[2] wire 26032, Is Broken? FALSE
```

and fifteen more (`:326-331,:340-344,:346,:348,:365,:367-368,:380`), with `:532` `SINK RULE 16 OK / 0 REFUSED / 0 BAD`.

*Scope:* covers §1's third bullet and the "19 → 1 the moment it exists" arithmetic at `:83-85`. Does **NOT** touch the R1 DISPOSITION block `:256-272`, correct as written.

### A3-b `contradicted` — §6 R2's "that reader is **not built**", and the live constraint is the opposite one

**Plan**, `:286-289`: *"**`Wire.Is Broken?` 6371004 + `Wire.Terminals[]` 6371003 from a HELD terminal reference**. That reader is **not built**…"*

**`docs/NAMES.md:888-891`**: *"✅ **`Wire.Is Broken?` 6371004 IS BUILT AND MEASURED, 2026-09-17** — and it never needed a new op. … `OpConnectNested_v0/v1` and `OpConnectFromWire_v0` all carry the reader already"* — confirmed by every `Is Broken? FALSE` column in run 3.

⚠️ Not "so use it freely": `docs/NAMES.md:898-911` measures that **reading it perturbs the target** (an idempotent connect took an `ExecState 1` scratch to 0), and `docs/cycle27-plan.md:110-112` withdrew it as a read-only instrument. The sentence is wrong in both directions at once.

*Scope:* the one sentence at `:288-289`. Does **NOT** disturb R2's main holding — RBW-survival is never evidence a wire is good — which is right (`docs/toolkit-capabilities.md:68`).

### A3-c `contradicted` — "the reparent set is 8, not 6" was corrected back to 6: two of the eight are INDICATORS

**Plan**, `:132-138` and the S3 gate `:330`, with R4 (`:302-303`) warning *"missing it costs 3 more 5001s"*.

**`tools/recipes/build_d1_routeb_v0.py:224-231`**: *"… says '8, not 6' and adds `min value` #17257 and `Force (pN) vs Extension (nm) ` #8038 - but both are **INDICATORS**"* (`probe_move_ctlterm_v0.py:7-8`). An indicator's wire is driven by the node feeding it, so neither can ever be a `from-ctl` **source**; the measured set is 7 rows over **six** controls, fixed before run 3 (`archive/peer/2026-09-17-priorart-priorart-routeb-build.md:402`), resolved in run 3 at `…run3.log:492-493`.

*Scope:* the count "8". §2c is **right** about the two half-width controls being missing from REV 4 §5d — run 3 wired all three of their rows (`…run3.log:363-364,:379`).

### A4 `unread-evidence` — four accepted route-B prior-art reviews exist; the frontmatter says none does

**Plan**, `:16-18`: *"B's FIRST ITEM only … The PLAN AS A WHOLE is still NOT DISPATCHED"*.

| file | scope | outcome |
|---|---|---|
| `archive/peer/2026-09-17-priorart-priorart-routeb-census.md:365-377` | route B Part 1 census | 6 findings, 0 novel, 6 × `FIXED:` |
| `archive/peer/2026-09-17-priorart-priorart-routeb-build.md:393-406` | **this plan's own build script** | 7 findings, 0 novel, 7 × `FIXED:` |
| `archive/peer/2026-09-17-priorart-routeb-run3-{codex,opus}.md:376-409` | run 3's two decisions | 12 findings, 0 novel; **build stopped before it ran** |

Also uncited: `docs/cycle27-plan.md` (the `status: current` plan superseding the cycle-15 framing this file inherits) and `tools/bench/build_d1_routeb_v0_run3.log` (the measurement of this plan's §7).

*Scope:* the frontmatter's claim. Does **NOT** say the body is unreviewed — §6 R1/R2 were revised from the connectfromwire review and say so.

---

## PART B — THE ARTIFACT

### B1 `already-built` — §7's script is written, has run three times, and a v1 for run 4 is on disk

**Plan**, `:319`: *"### S — structural, one run, one log (`tools/recipes/build_d1_route_b.py`, **not written**)"*.

`tools/recipes/build_d1_routeb_v0.py` (logs `…v0.log`, `…_run2.log`, `…_run3.log`; run 3 = `84 pass, 3 fail`, `…run3.log:541`) and **`tools/recipes/build_d1_routeb_v1.py`**, header `:148-149` — *"v1 — RUN 4, 2026-09-18 (cycle 36). EXACTLY FOUR CHANGES over v0"* — whose `:162-169` already implements Pre-decided 13's disposition of the three NO-ROUTE rows.

*Scope:* the "not written" parenthesis. Does **NOT** claim v1 has run — I found no run-4 log.

### B2 `already-failed` — §7's S5/S6 `ExecState` gates were attempted in run 3, ended 0, and the plan reproduces the cause it does not name

**Plan**, `:338-339`: S5 *"**`ExecState 1` warm**, saved"*; S6 *"cold re-open … `ExecState 1`"*.

`docs/cycle27-plan.md:128-138`: *"`build_d1_routeb_v0.py` copies from … and **never preloads it** … while its S5 gate is `g.exec_state(TARGET)` at `:1289` … **that gate has been reading linkage**."* Measured on route B's **own** original: a byte-identical scratch reads **cold 0** (`tools/bench/diag_d1_execstate_preload.log:13`) and **preloaded 1** (`:33`), 7/7 rc=0. The remedy is named at `:156-159` (restore `build_d1_v0.py:461`'s baseline read into `s1()`; `build_d1_routeb_v0.py:302-316` dropped it) and `:149-155` forbids preloading the build itself. §7 carries neither the baseline read nor the UNREAD labelling — and run 3 also **deleted its working copy with the evidence** (`:101-105`).

*Scope:* S5/S6 as acceptance gates. Does **NOT** claim run 3 succeeded: `docs/cycle27-plan.md:142-148` records the 0 as **over-determined** (skipped `s1q`/S4b ⇒ unwired conditional terminals), itself measured-with-error. Nothing is settled either way — the plan simply cannot tell.

### B4 `already-measured` — the "63 / 19" ledger was measured, and three of §4's four disputed rows disagree with the machine

**Plan**: `:60-65` (63 routed / **19** not), the S3w gate `:334` (*"**19 rows cannot meet**"*), table `:174-181`.
**Measured**, `…run3.log:532`: `S3w ledger: attempted 66, WIRED 63, FAILED 0, NO-ROUTE 3; SINK RULE 16 OK / 0 REFUSED / 0 BAD`.

| plan row | plan's verdict | measured |
|---|---|---|
| `:181` 18 tunnel-source rows | 🔴 NO BUILT ROUTE (R1) | **all wired**, `Is Broken? FALSE` (`…run3.log:322,:326-331,:340-344,:346,:348,:365,:367-368,:380`) |
| `:179` 3 `ForLoop` newline sinks → `OpConnectNested_v1` | index writer | **`wire_control` wired all three** after reparent: `:363`, `:364`, `:379`, each `reparented=True`, `attempts [(24, 'no error', …)]` |
| `:178` 2 R8 cross-diagram | `OpConnectNested_v1` | **correct** (`:362`, `:378`) |
| `:180` R3 `#2222` t0 ← `Z/dZ` | no route; control "already drives a wire" | NO-ROUTE for a **different** measured reason: `:386` — *"`'Z/dZ'` carries **NO wire on this copy**"* |

That resolves §11a's own conditional (`:449-450`, *"only needed **if the moves cut w730**"*): `Z/dZ` does carry w730 on a pristine copy (`tools/bench/diag_sr_transport.log:20,:25-26`) and not on the built one. **The moves cut it** — which is exactly why Pre-decided 3's answer is the REORDER, not a later read of the control's wire.

*Scope:* §1's table, S3w's gate sentence, §4's four rows. Does **NOT** dispute the denominator — 66 attempted / 109 cut / 27 source-side reconcile with `…run3.log:529`.

---

## Checked and CLEAN — so the next round does not re-derive it

- **§3's six `GObject.Move` verdicts and the `build_case` refutation** (`:151-163`) — the docstring reason holds (`gscript.py:2756-2764`); untouched since. ✅
- **§2a's five deletions** — `…run3.log:504` records the post-delete state with `#6384`'s w541 chain and `#12589` t1 among the 26 bare named sinks, exactly as R5 (`:305-306`) requires. ✅
- **The SINK RULE** (frontmatter `:2`) — implemented, 16 OK / 0 REFUSED / 0 BAD. ⚠️ Read `build_d1_routeb_v1.py:47-55` first: after a `GObject.Move` **every** terminal of a moved structure reads `is_source` FALSE, output tunnels included — a necessary precondition, not an identification.
- *Prose note, no slug:* **§7's `Diagram 170→174`** (`:327`, `:339`) counts §2b's fourth loop (the 20-slot pool For loop, `:113`); the built recipe makes three and gates **173** with `s1q` unexecuted — already stated rather than silently diverged at `build_d1_routeb_v1.py:80-83`. Both are right about different things, and a build driven from §7 would gate on a number the recipe does not produce.

---

```
PRIOR-ART: settled-already   (A1 — docs/cycle27-plan.md:89-100 + docs/cycle15-plan.md:124-128 + STATUS.md NEXT vs docs/d1-route-b-plan.md:392-397,:439-441,:451-457,:10 — covers the plan's reserved judgement questions: the registers MOVE WITH THEIR NODES into 1.2 with index_mode 1 kept, Z/dZ -> #2222 t0 is REORDERED before the S3-ct reparent, both authorisation flags stay False permanently ("the answer is no, not not-yet"), and STATUS makes a D1 build dispatch the next cycle's first act. Does NOT cover §9's third and fourth bullets - rule-1a acceptability of GObject.Move for the six structures, and whether N1 alone carries the R1 rows' equivalence - which I found undecided)
PRIOR-ART: refuted-already   (A2 — docs/d1-route-b-plan.md:463-473 itself + docs/cycle15-plan.md:129-130 + docs/cycle27-plan.md:106-112 + archive/peer/2026-09-18-fstunnel-v1-b4-execstate0-codex.md:156,:191 vs docs/d1-route-b-plan.md:461-542 — covers §10 as an inheritable plan: its own -Dual prior-art stopped it, and since then BOTH fallbacks died - the bare-terminal census returned an IDENTICAL 375 bare sinks over 170/170 diagrams on a KNOWN-GOOD copy so it discriminates nothing, and 452 is absent from the exported VirtualInstrument ActiveX interface so direct COM invocation is unlikely. Does NOT claim §10 is currently authorised work - the plan already marks it NOT AUTHORISED; the ask is that both corrections be written in before a future session inherits it)
PRIOR-ART: contradicted      (A3-a — docs/d1-route-b-plan.md:80-81 vs docs/toolkit-capabilities.md:70 + docs/d1-route-b-plan.md:269-271 + tools/bench/build_d1_routeb_v0_run3.log:322,:326-331,:340-344,:346,:348,:365,:367-368,:380,:532 — covers §1's claim that OpConnectFromWire_v0 is NOT BUILT and the "19 -> 1 the moment it exists" arithmetic at :83-85: the op was BUILT + SAVED 2026-09-17 at 16,524 B ExecState 1, this same file's §6 disposition already treats it as the answer, and run 3 used it for 16 from-tunnel rows with SINK RULE 16 OK / 0 REFUSED / 0 BAD. Does NOT touch the R1 DISPOSITION block :256-272, which is correct as written)
PRIOR-ART: contradicted      (A3-b — docs/d1-route-b-plan.md:286-289 vs docs/NAMES.md:888-891 and :898-911 + docs/cycle27-plan.md:110-112 — covers R2's sentence "that reader is not built": Wire.Is Broken? 6371004 IS BUILT AND MEASURED and needed no new op, because OpConnectNested_v0/v1 and OpConnectFromWire_v0 all carry it; the real constraint is the opposite one, that reading it PERTURBS the target (an idempotent connect took an ExecState-1 scratch to 0), so it was withdrawn as a read-only instrument. Does NOT disturb R2's main holding that RBW-survival is never evidence a wire is good - that is right and is repeated at docs/toolkit-capabilities.md:68)
PRIOR-ART: contradicted      (A3-c — docs/d1-route-b-plan.md:132-138,:330,:302-303 vs tools/recipes/build_d1_routeb_v0.py:224-231 + tools/recipes/probe_move_ctlterm_v0.py:7-8 + archive/peer/2026-09-17-priorart-priorart-routeb-build.md:402 — covers the count "8, not 6" in §2c and gate S3: `min value` #17257 and `Force (pN) vs Extension (nm) ` #8038 are INDICATORS whose wire source is the driving node, so neither can ever be a from-ctl source; the measured set is 7 from-ctl rows over SIX controls and the label list was corrected to six before run 3. Does NOT touch §2c's other half - the two half-width controls missing from REV 4 §5d are real, and run 3 wired all three of their rows after reparenting, …run3.log:363-364,:379)
PRIOR-ART: unread-evidence   (A4 — archive/peer/2026-09-17-priorart-priorart-routeb-census.md:365-377 + archive/peer/2026-09-17-priorart-priorart-routeb-build.md:393-406 + archive/peer/2026-09-17-priorart-routeb-run3-codex.md and -opus.md:376-409 + docs/cycle27-plan.md + tools/bench/build_d1_routeb_v0_run3.log, none cited in docs/d1-route-b-plan.md:16-18 — covers the frontmatter's claim that only B's FIRST ITEM has been reviewed and "the PLAN AS A WHOLE is still NOT DISPATCHED": four route-B prior-art reviews exist, 25 findings, 0 novel, all ANSWERED and all ACCEPTED IN FULL, one of them on this plan's own build script, plus the status: current cycle plan that supersedes the cycle-15 framing this file inherits. Does NOT claim the body is unreviewed - §6's R1 and R2 blocks were revised from the connectfromwire review and say so)
PRIOR-ART: already-built     (B1 — tools/recipes/build_d1_routeb_v0.py + tools/recipes/build_d1_routeb_v1.py:148-149,:162-169 + tools/bench/build_d1_routeb_v0_run3.log:541 vs docs/d1-route-b-plan.md:319 — covers §7's parenthesis "tools/recipes/build_d1_route_b.py, not written": the script is written under a different name, has run three times (run 3 = 84 pass / 3 fail), was rewritten before it ran in response to its own prior-art review, and a v1 for run 4 dated 2026-09-18 already encodes Pre-decided 13's disposition of the three NO-ROUTE rows. Does NOT claim v1 has run - I found no run-4 log)
PRIOR-ART: already-failed    (B2 — docs/d1-route-b-plan.md:338-339 vs docs/cycle27-plan.md:128-138,:156-159,:149-155,:101-105 + tools/bench/diag_d1_execstate_preload.log:13,:33 — covers §7's S5/S6 ExecState acceptance gates: run 3 read ExecState 0 through g.exec_state(TARGET) on an instance with nothing preloaded, and a BYTE-IDENTICAL scratch copy of route B's own original reads cold 0 / preloaded 1, so that gate has been measuring subVI linkage; the remedy - restore build_d1_v0.py:461's baseline read into s1(), add NO preload to the build - is named and is absent from this contract, and run 3 deleted its working copy with the evidence. Does NOT claim run 3 succeeded: the 0 was OVER-DETERMINED by the skipped s1q/S4b, itself measured-with-error, so nothing is settled either way)
PRIOR-ART: already-measured  (B4 — docs/d1-route-b-plan.md:60-65,:334,:174-181,:449-450 vs tools/bench/build_d1_routeb_v0_run3.log:532,:322,:326-331,:340-344,:346,:348,:362-365,:367-368,:378-380,:386 + tools/bench/diag_sr_transport.log:20,:25-26 — covers the "63 routed / 19 NO-ROUTE" ledger and S3w's "19 rows cannot meet": the measured result is 66 attempted, 63 WIRED, 0 FAILED, 3 NO-ROUTE; the 18 R1 rows all wired with Is Broken? FALSE; the 3 ForLoop newline-named sinks were wired by wire_control after the reparent, not by OpConnectNested_v1 as §4 assigns; and §11a's conditional is resolved the other way - Z/dZ carries w730 on the pristine copy but NO wire on the built one, which is why the answer is the REORDER. Does NOT dispute the denominator: 66 attempted / 109 cut / 27 source-side reconcile with …run3.log:529)
```

---

## What the citations leave, if it helps

The cheapest release here is not a refutation — it is a **revision of this file from run 3's own log**, since STATUS already calls it "the build order":

1. §1 and S3w — replace the 63/19 ledger with `…run3.log:532`'s 63 / 0 / 3; strike "NOT BUILT" at `:81`.
2. §4 — move the 18 tunnel-source rows and the 3 newline rows onto their measured mechanisms.
3. §6 R2 — the reader exists and perturbs; cite `docs/NAMES.md:898-911`, not "not built".
4. §7 S5/S6 — add the baseline `ExecState` read and 14a's UNREAD labelling; do **not** add a preload to the build.
5. §9/§11/§11a — replace the reserved questions with the Pre-decided 13 citation, keeping §9's two genuinely open bullets.
6. Frontmatter — list the four route-B reviews; set `authorises:`/`status:` to what STATUS now says.

## Sources

(extract from answer)

## What was done with it

SUPERSEDED 2026-09-18 by the same cycle's judgement session, after the user's 21:3x order that a D1 build
dispatch is the cycle's first act (`STATUS.md:56-61`) and after reading the review in full:

HELD — no release line written, by judgement, cycle 36 (2026-09-18). The verdict (NOT novel, 0 of 8 findings novel) was ACCEPTED rather than released: writing seven `REFUTED:`/`FIXED:` lines would have launched a build that the same cycle's outcome review, answering independently and from `project-requirements/` alone, said does not move the deliverable (5 OUTCOME-VIOLATIONs). Two reviewers with opposite evidence bases agreeing is the cheapest signal this cycle produced, and what CLAUDE.md §5 prescribes on repetition is a re-plan with the user, not a release. `tools/recipes/build_d1_routeb_v1.py` is written, compiles and is UNRUN; it stays stopped by `tools/stop_record.py` until the user's re-plan says whether D1 route B is still the next build. Finding B2 ('the baseline ExecState read is absent from this contract') is in fact answered by that recipe — the read is restored at `:379` — but that is recorded here rather than as a `FIXED:` release, because a release would launch the build.

The review is ACCEPTED IN FULL and released as FIXED — every finding was about the stale plan document, not the
recipe, and the reviewer's own six-point revision list (`:902-911`) was applied.

FIXED: settled-already - docs/d1-route-b-plan.md:475 - §9/§11/§11a now cite cycle27-plan Pre-decided 13 instead of reserving the questions, and §9's two genuinely open bullets carry the cycle-36 judgement answers.
FIXED: refuted-already - docs/d1-route-b-plan.md:597 - §10 now carries both corrections before anyone inherits it: the bare-terminal census discriminates nothing, and method 452 is absent from the exported VirtualInstrument interface.
FIXED: contradicted - docs/d1-route-b-plan.md:106 - "OpConnectFromWire_v0 is NOT BUILT" struck (it is built and wired 16 rows in run 3), R2's "that reader is not built" replaced by "built, and it perturbs the target", and the reparent count corrected from 8 to 6 controls.
FIXED: unread-evidence - docs/d1-route-b-plan.md:22 - the frontmatter now lists the four route-B prior-art reviews, docs/cycle27-plan.md and the run-3 log.
FIXED: already-built - docs/d1-route-b-plan.md:390 - §7 names the written recipes tools/recipes/build_d1_routeb_v0.py and v1.py instead of "not written".
FIXED: already-failed - docs/d1-route-b-plan.md:412 - §7's S5/S6 gates now carry the baseline ExecState read and Pre-decided 14a's UNREAD labelling, with no preload added to the build.
FIXED: already-measured - docs/d1-route-b-plan.md:79 - §1 and S3w now carry run 3's measured 66/63/0/3 ledger, §4's rows sit on their measured mechanisms, and §11a's conditional is resolved by the Z/dZ REORDER.
