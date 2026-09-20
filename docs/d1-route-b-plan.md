---
decided_2026_09_17: "SINK RULE (judgement): a from-tunnel row's sink is ALWAYS a terminal with Is Source? = FALSE — the consuming node's input inside the new loop (LabVIEW creates the tunnel) or, for a MOVED structure, its INPUT tunnel's OUTSIDE terminal; an OUTPUT tunnel is never a sink (T2c2's two-source broken wire). Gate per row: sink Is Source? FALSE and bare before, wire Is Broken? FALSE after. One read-only Terminals[] census of #5540 (pre/post move) is allowed to settle tunnel-side addressing."
type: plan
status: current
date: 2026-09-18
cycle: 15
kind: build
tags: [d1, route-b, seven-loop, tracking, focus, writer, queues, sentinels]
parent: docs/d1-build-plan.md
authorises: the D1 route-B build — STATUS.md "Where to look" calls this file "= the build order", and STATUS NEXT
  (user, 2026-09-18 21:3x) makes a D1 build dispatch the next cycle's FIRST ACT. §11p's reservation is DISCHARGED.
  <!-- REVISED 2026-09-18 (finding unread-evidence + settled-already): the old line read "authorises: nothing —
       §11p reserves the start of B to the judgement session", which is no longer true of the project's state. -->
spec_rows: [pre-rig-master-plan.md 1.1, 1.2, 1.5, 1.7, 1.8, 1.9]
measured_in: [tools/bench/build_d1_v0_run7.log, tools/bench/build_d1_routeb_v0_run3.log,
  tools/bench/d1_rewire_sources.json, tools/bench/d1_step0_census.json,
  tools/bench/gpu_kernel_v1_fp.json, tools/bench/probe_move_into_v0.log, tools/bench/probe_move_ctlterm_v0.log,
  tools/bench/build_opcreateconstonterm_v0.log, tools/bench/build_opsentinel_ops_run3.log,
  tools/bench/test_opconnectnested_v0.log, tools/bench/loopendref_637.json,
  tools/bench/diag_d1_execstate_preload.log]
decided_in: [docs/cycle27-plan.md]   # Pre-decided 13 / 14 / 14a / 16 bind this build; see §9, §11, §11a
prior_art_review: [archive/peer/2026-09-17-priorart-priorart-connectfromwire.md,
  archive/peer/2026-09-17-priorart-priorart-routeb-census.md,
  archive/peer/2026-09-17-priorart-priorart-routeb-build.md,
  archive/peer/2026-09-17-priorart-routeb-run3-codex.md,
  archive/peer/2026-09-17-priorart-routeb-run3-opus.md,
  archive/peer/2026-09-18-priorart-d1-routeb-v1.md]
  <!-- REVISED 2026-09-18 (finding unread-evidence): the old line claimed only B's FIRST ITEM had been reviewed
       and that "the PLAN AS A WHOLE is still NOT DISPATCHED". FOUR route-B prior-art reviews exist (25 findings,
       0 novel, all ANSWERED and ACCEPTED IN FULL), one of them on this plan's own build script, plus the 2026-09-18
       review of v1 whose six-point revision list produced this revision. -->
revised: 2026-09-17 (material, route-B session 1) — §1 bottom line, §4 mechanism table, §6 R1 disposition,
  §6 R2 replaced, §7 S3w. Measured in tools/bench/diag_connectfromwire_facts.log and
  archive/peer/2026-09-17-rbw-deleted-wires-run9.md.
  2026-09-18 (material, cycle 36) — §1, §2c, §4, §6 R2/R4, §7 S3/S3w/S5/S6, §9, §10, §11, §11a rewritten from
  tools/bench/build_d1_routeb_v0_run3.log and archive/peer/2026-09-18-priorart-d1-routeb-v1.md:902-911
---

# D1 — ROUTE B. Build the new loops FRESH inside the copy; move only what has no creator

`docs/d1-build-plan.md` §11p: *"Anything short of [a saved `Track_v6_D1_GPU.vi` at ExecState 1 warm and cold]
after the budgets above ⇒ **route B** (new loops built fresh inside the copy with the proven drop/name-wire helpers;
the original frame loop keeps everything except the tracker call, which is deleted; structures moved with
`GObject.Move` only where a fresh build is impossible)."* This file is that route written as a build order.
Target, md5 discipline, queues, sentinels, N1/F1/F2 are **unchanged from REV 4** and are not re-argued here.

**Sections:** §1 what changes vs route A · §2 node-by-node (fresh / move / delete / stays) · §3 the structures, one
verdict each · §4 every wire, by mechanism · §5 the wires made BY NAME · §6 residual risks · §7 prediction contract
S/N1/F1/F2 · §8 what B does NOT need.

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
| rows belonging to `#5058` / `#48` / `#376` | **32**, and **all 32 carry a NAME** (the subVI panes) | fresh drop ⇒ the sink name is guaranteed; 22 of the 32 are then routable with `wire` / `wire_sr` / a queue |
| rows belonging to the 21 moved nodes | **77**, of which **19 have an unnamed end** | unchanged from A |
| total | **109 over 24 uids** | |

So B does **not** make the re-wire disappear. It makes the three biggest, most-named nodes free, and it replaces
"resolve a cut wire" with "make a wire that never existed" for 59 fresh objects.

🔴 **The bottom line. REVISED AGAIN 2026-09-18 (material, cycle 36) — the ledger below is no longer a FORECAST of
63 routed / 19 NO-ROUTE; it is what route-B **run 3 MEASURED** on the real working copy**
(`tools/bench/build_d1_routeb_v0_run3.log:532`):

```
S3w ledger: attempted 66, WIRED 63, FAILED 0, NO-ROUTE 3; SINK RULE 16 OK / 0 REFUSED / 0 BAD
```

| | rows | route |
|---|---:|---|
| **WIRED, MEASURED in the real VI** | **63 of 66 attempted** | name-wires (`wire` / `wire_control`, incl. the 3 `ForLoop` newline-named sinks AFTER the control reparent) · `wire_sr` · `OpCreateConstOnTerm_v0` · `OpConnectNested_v1` (same-diagram and cross-diagram) · **`OpConnectFromWire_v0` for 16 from-tunnel rows, `SINK RULE 16 OK / 0 REFUSED / 0 BAD`, every one `Is Broken? FALSE`** |
| **FAILED** | **0** | — |
| **NO ROUTE** | **3** | the two `LeftShiftRegister` rows (`#1359` t1, `#29874` t3) + `#2222` t0 ← control `Z/dZ` — all three now DECIDED by `docs/cycle27-plan.md` Pre-decided 13 (registers move with their nodes; `Z/dZ` is a REORDER), so they are open *construction*, not open *questions* |

<!-- REVISED 2026-09-18, finding already-measured: the previous table forecast "route BUILT and MEASURED 63 /
     NO route 19 (18 R1 + 1 R3)". Run 3 wired all 18 R1 rows with `OpConnectFromWire_v0`, so R1 is not the
     blocker this file was written around, and the residue is 3 rows, not 19. -->

Three things changed on 2026-09-17, each MEASURED, none of them an opinion:

* **R8 is CLOSED.** `OpConnectNested_v1.vi` is built, saved (14,666 B) and functional **warm and cold**
  (`tools/bench/test_opconnectnested_v1_cold.log`, 7/0), and it made a real cross-diagram `D[19] → D[24]` wire in
  the working copy (`build_d1_v0_run9.log:287`). R8's 2 rows are exactly that shape. ⚠️ What is NOT closed is how
  to **certify** such a wire — see R2, the gate is unsound.
* **The `from-ctl` rows split in two** (`docs/d1-build-plan.md` §11u.2, `tools/bench/diag_connectfromwire_facts.log`):
  3 of run 9's six 5001s were a **caller bug** — `wire_control` called without `src_diagram_index` while the
  control terminal lives on `Diagram #639` (index **43**) — and wire correctly once it is passed (`'Auto-Reset'`,
  sink wire **0 → 1231**). The other 3 get past `Get Controls.vi` and then fail in **`Wire Inputs.vi`** on the
  **DEST** name (`ForLoop` tunnels labelled `Force\nsmoothing\nhalf-width` /
  `Extension\nmedian filter\nhalf-width`), so they are re-assigned to the index-addressed writer. **The newline is
  not the cause** — three of the six failing labels have no newline at all.
* **R1 did NOT shrink**, and its two in-plan candidates are refuted for 14 of 16 rows (see the R1 disposition in
  §6). It needs `OpConnectFromWire_v0` (`docs/d1-build-plan.md` §11t), which is **BUILT + SAVED 2026-09-17,
  16,524 B, `ExecState 1`** (`docs/toolkit-capabilities.md:70`), and which **run 3 used for 16 from-tunnel rows,
  `SINK RULE 16 OK / 0 REFUSED / 0 BAD`, every wire `Is Broken? FALSE`**
  (`tools/bench/build_d1_routeb_v0_run3.log:365,:367-368,:380,:532`).
  <!-- CORRECTED 2026-09-18, finding contradicted (A3-a): this sentence read "which is NOT BUILT". The op was
       built the same day this file was written, and §6's own R1 disposition already treats it as the answer. -->

A's run 9 left **18 NO-ROUTE + 6 FAILED = 24** (MEASURED, `build_d1_v0_run9.log:339`). B **measured 63 WIRED /
0 FAILED / 3 NO-ROUTE** on run 3 (`…routeb_v0_run3.log:532`); the arithmetic "24 → 19, and 19 → 1 the moment
`OpConnectFromWire_v0` exists" is SUPERSEDED by that measurement.
<!-- CORRECTED 2026-09-18, findings contradicted + already-measured: the forecast arithmetic was written before
     the op existed and before run 3 ran. -->

The residue is **3 rows, all DECIDED** (`docs/cycle27-plan.md` Pre-decided 13): `#1359`/`#29874`'s shift registers
MOVE WITH THEIR NODES into 1.2 (`add_shift_reg` + `wire_sr`, `index_mode 1` kept), and `Z/dZ` → `#2222` t0 is
REORDERED before the S3-ct reparent of `ControlTerminal #403`. **Both authorisation flags stay `False`
permanently** — the answer is "no", not "not yet".

---

## 2. Node-by-node — fresh drop, move, delete, stays

Keys are `d1_step0_census.json → diagram_43` (47 nodes) (MEASURED). "Fresh" = created by this build; "move" =
`OpMoveIn_v0` / `GObject.Move` (MEASURED 12/0 on a `CaseStructure`, `probe_move_into_v0.log`).

### 2a. DELETED from the frame loop — 5

| uid | what | why | evidence |
|---:|---|---|---|
| **5058** | `Track N beads four-fold over-kernel-v3.vi` | replaced by a fresh `GPU_kernel_v1.vi` in 1.2 | MEASURED §8 of REV 4 (16 terminals) |
| **48** | `ASI_adjust focus-subvi.vi` | replaced by a fresh drop in 1.5 | MEASURED run 7 wired t0–t5 by name |
| **376** | `save trace.vi` | replaced by a fresh drop in 1.7 | MEASURED `diag_savetrace_376.log` 4/0 |
| **22700 · 23020** | `IMAQ Write TIFF File 2` · `Build Path` | fixture insertions, not original | MEASURED §11h, `build_d1_v0_run6.log` S1t 4/4 |

⚠️ Deleting `#48` and `#376` is **new to B** and bares the sinks that their outputs feed (`#6384`'s error chain via
w541; `#12589` t1 via w9113). Both are re-made in §4 — but the delete must precede the `ExecState` read, exactly as
§2b of REV 4 says (`ExecState` is meaningless between edits).

### 2b. FRESH — 59 objects, 3 of them subVIs

| n | what | helper (all MEASURED functional) |
|---:|---|---|
| 3 | `GPU_kernel_v1.vi` → 1.2 · `ASI_adjust focus-subvi.vi` → 1.5 · `save trace.vi` → 1.7 | `drop_subvi(target, path, diagram_index, location)` — takes a **diagram index**, so a loop body is legal (`gscript.py:1171`) |
| 3 | While loops 1.2 / 1.5 / 1.7 on `Diagram #686` | `loop_in('while', …, diagram_index, …)` — *"stage 2 needs loops INSIDE loops"* (`gscript.py:1101`) |
| 1 | pool For loop (20 `IMAQ Create` → `Q_free`) | `loop_in('for', …)`; shape proven in step C v2.1 (162/162) — **ASSUMED** applicable at bound 20 |
| 16 | 8 `Obtain` + 8 `Release` | `queue_node('obtain'/'release', …, diagram_index, …)` (`gscript.py:1068`) |
| 22 | 8 `Dequeue` + 8 data `Enqueue` + 6 sentinel `Enqueue` | same helper |
| 6 | 3 sentinel `Equal?` + 3 sentinel literals (−1) | `OpCreateEqual_v0` 23/0 · `OpCreateConstOnTerm_v0` 22/0 (`toolkit-capabilities.md:52,:54`) |
| 6 | the GPU kernel's 6 extra pane inputs as constants | `OpCreateConstOnTerm_v0` — **typed by the sink and already wired** (MEASURED 22/0, value read back −1) |
| 2 | 1 `IMAQ Create` + 1 pool-seed `Enqueue` | step C v2.1 |
| 8 | shift registers (4 on 1.2, 2 on 1.5, 2 on 1.7) | `add_shift_reg` + `wire_sr` (rows 37–39) — registers are **created fresh, never moved** |

The 6 extras and their values are MEASURED (`gpu_kernel_v1_fp.json`, 19 pane items = 13 shared + 6 extra):
`Function` = the node default · `cal_path` = empty · `nb` = 0 · `status` = empty · `status_len` = 0 · `flags` = 0.

### 2c. MOVED — 21 nodes + 6 CONTROL terminals (7 `from-ctl` rows)
<!-- CORRECTED 2026-09-18, finding contradicted (A3-c): heading read "8 control/indicator terminals". -->

**→ 1.2 (17):** `5540` `9647` `10247` `10445` `10950` `17289` `10969` `10757` `1359` `2222` `2626` `6104` `8885`
`9833` `11261` `29874` `10686`. (= REV 4 §5a's 18 rows under 1.2 minus `#5058`, which is deleted.)
**→ 1.5 (4):** `10407` + the three control references `3529` / `3560` / `3447` (MEASURED §11e.3; `#48` is **not**
moved in B, it is dropped fresh).
**→ 1.7 (0):** `#376` is dropped fresh, so 1.7 receives no moved node at all.

**Control terminals — SIX CONTROLS over SEVEN `from-ctl` rows. NOT eight.** REV 4 §5d lists six (`Auto-Reset`
17472, `Reset Tracking` 5605, `Z/dZ` 47, `Correction Factor` 9289, `min value` 17257, `Force (pN) vs Extension
(nm) ` 8038), and §2c's real correction to it is that **two of those six are wrong and two others are missing**:
**`min value` #17257 and `Force (pN) vs Extension (nm) ` #8038 are INDICATORS** — driven by `#10969` and `#11261`
respectively (`tools/recipes/probe_move_ctlterm_v0.py:7-8`) — so they are SINKS of a node and can **never** be the
source of a `from-ctl` row; while **`Force\nsmoothing\nhalf-width` uid 28148** (→ `#1359` t7) and
**`Extension\nmedian filter\nhalf-width` uid 28996** (→ `#1359` t8 and `#29874` t6) are real `from-ctl` sources
that §5d never lists, and run 7 FAILED both with 5001 (`build_d1_v0_run7.log:297,298,301`).
MEASURED: `d1_rewire_sources.json` has exactly **7 `from-ctl` rows**, every one `"indicator": false`, over these
**six** labels — `Auto-Reset`, `Reset Tracking`, `Z/dZ`, `Correction Factor`, `Force\nsmoothing\nhalf-width`,
`Extension\nmedian filter\nhalf-width` (`tools/recipes/build_d1_routeb_v0.py:224-232`, the list the built recipe
actually carries). Run 3 wired all three half-width rows by `wire_control` AFTER the reparent
(`tools/bench/build_d1_routeb_v0_run3.log:363,:364,:379`). Reparenting is MEASURED 9/0
(`probe_move_ctlterm_v0.log`, `#642 → Diagram#1170`, total `ControlTerminal` unchanged at 114).
<!-- CORRECTED 2026-09-18, finding contradicted (A3-c): the heading read "8, not 6" and added the two indicators
     on top of the six. The two half-width controls this section found ARE real; adding the indicators was the
     error. Corrected in the recipe before run 3 ever ran. -->

### 2d. STAYS on 1.1 — everything else

`#6810` (the frame source, row 1.8 REUSE) · `#12589` (§11c) · `#11639` · `#22082` · `#17883` `#17837` `#22284`
`#10019` (stop paths A and B) · `#1114` WLC (= D2) · `#57` `#3191` `#20474` · `#2136` `#10068` `#29240` · `#3057`
`#5119` `#10382` `#11529` `#11608` `#22703` `#23175` · `#3052` `#4580` `#30117` · `ControlTerminal #642`.
`#637`'s conditional terminal is untouched: **648 ← w3457 ← `#11639`** (MEASURED, `loopendref_637.json`).

---

## 3. The structures — one verdict each, with the reason

| structure | verdict | reason (MEASURED unless marked) |
|---|---|---|
| **`#5540`** reseed Case | **`GObject.Move`** | `build_case` places the Case on the **top-level diagram** and takes a **front-panel CONTROL** as selector (`gscript.py:2756-2764`); 1.2's body is neither. Its selector is `#10247`'s Boolean, and its two frames are pure pass-throughs whose tunnels carry outer values (`stage2-assembly-step-e.md` CENSUS B) — a fresh build would have to re-create 2 frames, 4 input tunnels and 2 `SelectorTunnel`s, and no op creates a `SelectorTunnel` |
| **`#10445`** Case | **`GObject.Move`** | same wall; its frames are uncensused (`stage2-assembly-step-e.md` calls Census A *still required*) |
| **`#2222`** Case | **`GObject.Move`** | same wall; frame contents uncensused |
| **`#1359`** For loop | **`GObject.Move`** | `loop_in('for', …)` can create a For loop on a nested diagram, but its **body contents are not censused** (`d1_step0_census.json` covers diagram 43 only) — a fresh loop would be an empty one |
| **`#29874`** For loop | **`GObject.Move`** | same |
| **`#10407`** autofocus Case | **`GObject.Move`** | the brief's "rebuilt with `build_case`" is **refuted by measurement**: top-level-only + control-selector-only (above), and the case's frame contents are uncensused. A move is MEASURED to carry frames intact (`probe_move_into_v0.log` P3: `Diagram` count 171 → 171) |
| **`#12589`** Case | **stays on 1.1** | §11c — keeping it keeps w12070 → `#11639` uncut; the crossing becomes `Q_focusback` |
| the loop bodies of 1.2 / 1.5 / 1.7 | **fresh** | `loop_in('while', …)` |

⇒ **fresh structures 4 (3 While + 1 For); moved structures 6; 0 structures rebuilt with `build_case`.**
This is the single largest correction B makes to the brief, and the reason is a docstring, not an opinion.

---

## 4. Every connection, by mechanism — 82 of the 109 cut terminals need one

27 of the 109 are `source-side` rows (a moving node's **output**, re-connected from its sink's side) and need no
call of their own (MEASURED, `by_action.source-side = 27`). The other 82:

| mechanism | n | addressing | status |
|---|---:|---|---|
| **`wire` / `wire_control` by NAME** | **27** (was 30) | both ends by name | MEASURED WORKS on nested diagrams — run 7 wired 10 body-to-body by name, incl. into `CaseStructure`/`ForLoop` named tunnels. ⚠️ `wire_control` **must** be given `src_diagram_index` (§11u.2). ✅ **The 3 `ForLoop` newline-named rows are BACK IN this row** — run 3 wired all three by `wire_control` after the reparent (`…routeb_v0_run3.log:363,:364,:379`) <!-- CORRECTED 2026-09-18, finding already-measured (B4): they had been moved out onto `OpConnectNested_v1`. --> |
| **`wire_sr` LeftIn / RightIn** | **20** | register by index, node terminal by name | MEASURED 20/20 WIRED in run 7 |
| **`OpCreateConstOnTerm_v0`** | **5** | node + terminal by INDEX on a nested diagram | MEASURED 22/0; run 7 placed 5 literals in the real VI |
| **`OpConnectNested_v0`, SAME diagram** | **6** | both ends by INDEX, both inside 1.2's body | BUILT + wire-identity verified, **NOT ExecState-verified** — §6 R2 |
| **unnamed sink, source on ANOTHER diagram** | **2** | both ends by INDEX, different diagrams | ✅ **ROUTE BUILT 2026-09-17: `OpConnectNested_v1`** (cold `ExecState 1`, and one such wire made in the real VI, `build_d1_v0_run9.log:287`) — §6 R8 CLOSED |
| **`ForLoop` sink whose NAME carries newlines** | **3** | ~~both ends by INDEX~~ → **both ends BY NAME, after the reparent** | ✅ **MEASURED WIRED BY `wire_control`, not by `OpConnectNested_v1`** — `#1359` t7 / `#1359` t8 / `#29874` t6, each `reparented=True`, `attempts [(24, 'no error', …)]`, sink wire `0 → 28990 / 28995 / 28995` (`tools/bench/build_d1_routeb_v0_run3.log:363,:364,:379`). The newline was never the obstacle; **the missing `src_diagram_index` and the un-reparented control terminal were** (§11u.2) <!-- CORRECTED 2026-09-18, finding already-measured (B4): this row assigned the 3 to `OpConnectNested_v1`. --> |
| **unnamed sink, source = a control terminal** | **1** | by INDEX, sink `is_source` FALSE | 🔴 **NO ROUTE in run 3 — and DECIDED since**: `docs/cycle27-plan.md` Pre-decided 13 = **REORDER** `Z/dZ` → `#2222` t0 **before** the S3-ct reparent of `ControlTerminal #403` (`docs/cycle15-plan.md` Pre-decided 3), `OpConnectNested_v1` by index. `TEMP_SINK_AUTHORISED` stays **False permanently** — §6 R3, §11a |
| **tunnel-source rows** | **18** | source is not a named node — **a WIRE terminal is** | ✅ **MEASURED WIRED by `OpConnectFromWire_v0`** — all 18, every one `Is Broken? FALSE`, `SINK RULE 16 OK / 0 REFUSED / 0 BAD` (`…routeb_v0_run3.log:365,:367-368,:380,:532`). R1 is CLOSED as a route question <!-- CORRECTED 2026-09-18, findings contradicted (A3-a) + already-measured (B4): this row read "🔴 NO BUILT ROUTE — §6 R1". --> |

The **6** index rows are all **inside one body diagram** (1.2's), all `Node → Node`: `#5540` t0 ← `#10247`
`x .or. y?` · `#10247` t2 ← `#10445` · `#10445` t0 ← `#9647` `x .and. y?` · `#1359` t4 ← `#8885` `x*y` ·
`#29874` t4 ← `#8885` `x*y` · `#11261` t1 ← `#1359`. **Same-diagram is exactly what `OpConnectNested_v0` does**
(MEASURED: *"both ends by index on THAT diagram"*, `toolkit-capabilities.md:55`).

⚠️ The other three unnamed-sink rows are **not** same-diagram and are new findings of this reading (MEASURED,
`d1_rewire_sources.json`): `#1359` t5 ← `#10068` `x-y*floor(x/y)` and `#29874` t2 ← `#29240` `x-y*floor(x/y)` —
both sources **stay on `Diagram #639`** while the sink moves into 1.2's body (**R8**); and `#2222` t0 ← control
`Z/dZ` uid 47, a `ControlTerminal`, which `Diagram.Nodes[]` does not list (**R3**).

Ordering that is already decided and must be kept: **reparent the 6 control terminals BEFORE any `wire_control`**
<!-- CORRECTED 2026-09-18, finding contradicted (A3-c): "8" → "6". -->
— and, per `docs/cycle27-plan.md` Pre-decided 13, **the `Z/dZ` → `#2222` t0 wire is made BEFORE the S3-ct reparent
of `ControlTerminal #403`**, which is the one ordering exception —
(run 7's six 5001s are `Get Controls.vi` looking on the wrong diagram — STATUS NEXT, "Material, unblocked"); and
§11k's create → delete-the-wire → re-wire order for each sentinel `Equal?`.

---

## 5. The wires made BY NAME — the list, with the name's source

All names below are MEASURED, either in `docs/NAMES.md` or by a successful `wire` call in run 7.

**1.2 — the fresh `GPU_kernel_v1.vi` (13 shared terminals, `gpu_kernel_v1_fp.json`):**

| terminal | source | mechanism |
|---|---|---|
| `Image In` | `Q_work` `Dequeue`.`element` | name (step C, 162/162) |
| `x,y,z array` | `#5540`.`x,y,z array` | name (MEASURED source-side row) |
| `Bead is good? array in` | `#5540`.`Bead is good? array out` | name |
| `pos in cal image in` | left SR `#2972` | `wire_sr LeftIn` (MEASURED WIRED) |
| `x,y,z array out` → | right SR `#1147` | `wire_sr RightIn` (MEASURED WIRED) |
| `Bead is good? array out` → | right SR `#5796` | `wire_sr RightIn` (MEASURED WIRED) |
| `pos in cal image out` → | right SR `#119`, and `#10757`/`#10969` by name | `wire_sr RightIn` + name |
| `cross size` · `# of bead 4 packs` · `4 pack remainder` · `Array of cal clusters` · `Real-space cosine window` · `Cosine bandpass\nfor Hilbert ` | `#637`'s LoopTunnels `#2580` `#2396` `#4432` `#3656` `#3920` `#4031` | 🔴 **R1** — the sink name is known, the **source has none** |

**1.5 — the fresh `ASI_adjust focus-subvi.vi`** (names MEASURED by run 7's six WIRED rows):
`-Inc reference` ← `#3529` · `+Inc reference` ← `#3560` · `Focus inc reference` ← `#3447` (all three moved into
1.5) · `VISA resource name` ← SR `#4344` (`wire_sr LeftIn`) · `In position` ← SR `#4274` (`wire_sr LeftIn`) ·
`Out position` → `#10407` t5 (name) · `#10407` t6 `position [internal units]` → SR `#4256` (`wire_sr RightIn`) and
→ `Q_focusback`. `#10407` t1 `# slices in stack` ← LoopTunnel `#9641` is 🔴 **R1**.

**1.7 — the fresh `save trace.vi`** (pane verified by probe, `NAMES.md:111-118`):
`total data array in` ← SR `#51` · `total data array out` → SR `#15` · `error in` ← SR `#1108` · `error out` → SR
`#24` · `current frame data array in` ← the `Q_res`/`Q_good` dequeue chain (name) · `frame index` ← `Q_rmeta`
dequeue `element` (name — **B's improvement**: in A this was a from-tunnel NO-ROUTE, `#376` t7) ·
`cal cluster path` / `file size` / `selected path` / `base path/filename` / `file # to append` ← LoopTunnels
`#3644` `#2294` `#5096` — 🔴 **R1**.
**1.7 → `#6384 save N xyz traces.vi`** (same diagram `#686`): `#6384`'s inputs are **named**
(`desired # data points`, `cal cluster path`, `actual # data points`, `error in`, `data array`, `file # to append`,
`base path/filename` — MEASURED `main-vi-stop-and-save.md:110-121`), and 1.7's output tunnels are named by
`exit_while(output_names=…)`, so this seam is **all name-wire**. Three of `#6384`'s inputs keep coming off `#637`'s
own tunnels unchanged.

---

## 6. Residual risks — named, with what would settle each

**R1 — 🔴 the one that decides B: 18 rows whose SOURCE is an unnamed tunnel.** MEASURED: 16 of the 17 A-era
`from-tunnel` rows carry `outer_source: null` (`d1_rewire_sources.json`; run 7: *"no NAMED node source in any
census"*), i.e. the value arrives on `Diagram #686` from something that is **not a node** (`stage2-assembly-step-e.md`
found `FlatSequenceInnerTunnel` in the same position for w2731/w5812). `loop_in` and `wire` both address the source
BY NAME (`gscript.py:1101,:1284`), so neither can create the tunnel.
**What B can offer that A could not** (ASSUMED, unmeasured): the value **is** readable as `#637`'s own **outer
terminal**, which is a `Node` terminal index-addressable on `Diagram #686` — run 7 itself printed one
(`{'kind':'node','diagram':'19','uid':637,'i':37,'name':'','is_source':True}`). Both that terminal and the new
loop's tunnel terminal live on `Diagram #686`, so the wire is **same-diagram** and `OpConnectNested_v0` can express
it — **provided the sink tunnel already exists**, which a fresh loop has no way to create from an unnamed source.
Two candidate resolutions, neither built:
 (i) create the tunnel with `loop_in` from **any** named node output of the right type on `#686`, delete that wire,
 then re-point by index (§11k's proven create → delete → re-wire shape; MEASURED that Connect Wire on an
 **already-wired** sink re-routes and breaks, `gscript.py:2206-2207`, so the delete is mandatory);
 (ii) `GObject.Move` the six `LoopTunnel` objects themselves — **unmeasured**, and a tunnel's owner is a structure,
 not a diagram.
**This is a judgement call and this plan does not take it.**

> **🔴 R1 DISPOSITION, MEASURED 2026-09-17 (material, route-B session 1) — candidates (i) and (ii) are REFUTED for
> 14 of the 16 rows, and R1's "What B can offer that A could not" paragraph above is WRONG as written.**
> Its premise is that the value is readable as **`#637`'s own outer terminal**, which would be an index-addressable
> `Node` terminal on `Diagram #686`. `tools/bench/d1_tunnel_sources.json` (18 rows, produced by
> `gscript.tunnels()` + `OpWireSource_v5`, `docs/d1-build-plan.md` §11s.1) measures the opposite for the rows that
> matter: on each of those outer wires the terminal with **`Is Source?` TRUE** is owned by
> **`FlatSequenceInnerTunnel`** (14 rows) or **`LeftShiftRegister`** of `#637` (2 rows) — e.g. row 1,
> *"owner uid 5818 (`FlatSequenceInnerTunnel`) is neither a node on diagrams (19, 43, 0) nor a `LoopTunnel`"*.
> `#637`'s own outer terminal on an INPUT tunnel is therefore the wire's **SINK**, not its source, and a branch
> must be taken from a source. The one run-7 print the paragraph generalises from
> (`{'kind':'node','diagram':'19','uid':637,'i':37,'is_source':True}`) is an OUTPUT tunnel, a different case; and
> the single row that resolves to a named node (`SubVI #27605`) was already wired by index in run 9.
> (ii) `GObject.Move` of the six `LoopTunnel`s is unchanged — still unmeasured, and a tunnel's owner is a
> structure, so it is not a diagram move. **So R1 needs the WRITER, not a re-reading of the tunnels**: the
> `OpConnectFromWire_v0` of `docs/d1-build-plan.md` §11t, whose `Wire Source` is a wire-terminal reference.
> Raised by `archive/peer/2026-09-17-priorart-priorart-connectfromwire.md` A4 (`unread-evidence`), which asked for
> exactly this disposition in writing.

**R2 — ✅ CLOSED as written, and REPLACED by an instrument problem (2026-09-17, material route-B session 1).**
The original R2 ("`OpConnectNested_v0` is not ExecState-verified") is answered: **`OpConnectNested_v1` is
FUNCTIONAL warm AND cold** — `tools/bench/test_opconnectnested_v1_cold.log`, 7 pass / 0 fail in a restarted
LabVIEW, cold `ExecState 1`, 14,666 B — and it made 8 wires in the real VI (`build_d1_v0_run9.log`).

🔴 **What replaces it: the ACCEPTANCE INSTRUMENT is unsound.** `docs/d1-build-plan.md` §11u.1 and
`archive/peer/2026-09-17-rbw-deleted-wires-run9.md` (codex, ANSWERED, accepted in full): the
"wire SURVIVES `remove_bad_wires_scripted`" gate is IMPLEMENTED at `tools/recipes/build_d1_v0.py:1118-1121` as
**uid equality of two `Terminal.Connected Wire` reads**, which measures object identity, not survival —
`Terminal.Connect Wire` 6349C03 returns nothing, and run 9's row 1 (`#1359` t4, `26189 -> 26412`) ended with a
**non-zero** wire while being counted as deleted. So **no gate in this plan may cite RBW-survival as evidence
that a wire is good**, and `toolkit-capabilities.md:56`'s sentence about it is wrong about its own implementation.
Use, in this order: **`ExecState 1` on a scratch built to be otherwise runnable** (the skill's unforgeable
signal), plus each endpoint's connected-wire state and owning diagram.

🔴 **CORRECTED 2026-09-18 (finding contradicted, A3-b) — the second half of this paragraph was wrong twice over.**
It said the `Wire.Is Broken?` reader is "not built and is a judgement call". In fact:
* **`Wire.Is Broken?` 6371004 IS BUILT AND MEASURED, and it never needed a new op** (`docs/NAMES.md:888-891`):
  `OpConnectNested_v0/v1` and `OpConnectFromWire_v0` all carry it already, surfaced as `UID 2` / `Is Broken?`.
  The whole trick is **ORDER** — branch the Invoke's own `error out` into the reader (gate **W7b**), or it runs
  before the write and reports the OLD wire. Run 3 used it on all 18 from-tunnel rows (`Is Broken? FALSE`).
* **The real constraint is the opposite one: READING IT PERTURBS THE TARGET** (`docs/NAMES.md:898-911`, measured
  2026-09-18). The only way to make the ordered readout run is to perform a `Terminal.Connect Wire` — and an
  **idempotent** connect (0 new `Wire` objects) on a scratch whose `ExecState` was **1** left it reading **0**
  afterwards. So the reader **must not sit on a recipe's success path**, and it was **WITHDRAWN as a read-only
  instrument** (`docs/cycle27-plan.md` Pre-decided 14, which first mandated it and then withdrew it by
  measurement). An orphan wire no node terminal carries has no sink terminal at all and cannot be read this way.

**R2's main holding is UNCHANGED and stands:** no gate in this plan may cite RBW-survival as evidence that a wire
is good — that check is uid equality of two `Terminal.Connected Wire` reads and misreports
(`docs/toolkit-capabilities.md:68`, `docs/d1-build-plan.md` §11u.1).

**R3 — a control terminal is not a `Node`.** `#2222` t0's source is control `Z/dZ` uid 47 with an **unnamed sink**,
so neither `wire_control` (name on both ends) nor `OpConnectNested_v0` (`Nodes[]`) is known to reach it. 1 row.

**R8 — 🔴 two rows ARE cross-diagram, so §8's claim 1 is not absolute.** MEASURED: `#1359` t5 ← `#10068` and
`#29874` t2 ← `#29240`; both sources **stay on `Diagram #639`** (REV 4 §5a: the three `Quotient & Remainder` nodes
stay on 1.1) while both sinks move into 1.2's body, and **both sinks are unnamed**. That is exactly A's
unbuildable shape (two nested diagrams, second `To More Specific Class`, MEASURED `ExecState 0`). Three ways out,
all unmeasured and all judgement: move `#10068`/`#29240` into 1.2 as well (they are *Q&R* nodes that REV 4 says are
in neither slice — moving them is a scope change); route the two values through a queue or tunnel whose sink end is
named; or accept the fifth op. **2 of B's 82 connections.**

**R4 — the reparent set is SIX CONTROLS over SEVEN `from-ctl` rows** (§2c). ~~"8, not 6"~~
<!-- CORRECTED 2026-09-18, finding contradicted (A3-c): `min value` #17257 and `Force (pN) vs Extension (nm) `
     #8038 are INDICATORS and can never be a `from-ctl` source; the two half-width CONTROLS are real and replace
     them in the six. -->
Correcting §5d is still bookkeeping and **missing it still costs 3 more 5001s**, which is what run 7 measured —
and run 3 confirmed the fix: all three half-width rows WIRED once the controls were reparented
(`tools/bench/build_d1_routeb_v0_run3.log:363,:364,:379`).

**R5 — deleting `#48` and `#376` is new.** It bares `#6384` t8 (w541 `error in`) and `#12589` t1 (w9113). Both are
re-made in §4/§5, but the S3b census must be widened to them, exactly as REV 4 §7.2b requires for shared nets.

**R6 — the pool.** B's `Q_free`/`Q_work` pool of 20 images is fresh construction that the original does not have;
step C proved the shape at 8 slots in **replay**, never at 20 in **live** mode (`decisions.md:22` sets 20).
ASSUMED transferable.

**R7 — the `Local` count.** No step here creates a `Local` or a panel object; `Local` stays **8**,
`ControlTerminal` stays **114**. MEASURED as a gate in A (S1q/S4s) and carried unchanged.

---

## 7. Prediction contract

### S — structural, one run, one log — **the recipe IS WRITTEN**: `tools/recipes/build_d1_routeb_v0.py` (run 3 = 84 pass / 3 fail, `tools/bench/build_d1_routeb_v0_run3.log`) and `tools/recipes/build_d1_routeb_v1.py` (2026-09-18, encodes Pre-decided 13's disposition of the 3 NO-ROUTE rows and the S1b baseline read; UNRUN at the time of this revision)
<!-- CORRECTED 2026-09-18, finding already-built (B1): this heading read "(`tools/recipes/build_d1_route_b.py`,
     not written)". The script exists under a different name, has run three times, and was itself rewritten in
     response to its own prior-art review. -->

| gate | assertion, with counts |
|---|---|
| **S0** | `TRANSPORT = "queue"`; original md5 `2a78e17c449cacdaf5da389818526859` read **before**; `OpMoveIn_v0` (UID control `'UID 3'`), `OpCreateEqual_v0`, `OpCreateConstOnTerm_v0`, `OpStopFromNode_v0`, `OpConnectNested_v0` all present; handles recorded |
| **S1** | fresh copy, before any edit: `Diagram 170`, `Node 626`, `Wire 1902`, `LoopTunnel 132`, `ControlTerminal 114`, `WhileLoop 3`, `Local 8`, `SubVI 98`, `Function 181` (MEASURED exact in run 7) |
| **S1t** | `#22700`, `#23020` deleted → `SubVI 98→97`, `Function 181→180`, `Node 626→624`, `Wire 1902→1899`, bare named sinks `28→26` (MEASURED 4/4, run 6) |
| **S1d** | **new in B**: `#5058`, `#48`, `#376` deleted → `SubVI 97→94`, all three uids gone; the bared sinks of w541 / w9113 enumerated and carried into S3b |
| **S2** | 3 new While loops + 1 pool For loop on `Diagram #686` → `WhileLoop 3→6`, `ForLoop +1`, **`Diagram 170→174`** (A predicted 173 for three loops; the pool loop is the fourth body — ASSUMED). `#637` still exists and still owns `#6810` and `#22082` |
| **S2d** | 3 fresh `drop_subvi` → `SubVI 94→97`; each new subVI's owner chain reads `uid → <body Diagram> → <the right WhileLoop>` (`OpOwnerChain_v1`) |
| **S1q** | 8 `Obtain`: `Q_free`/`Q_work` bounded **20**, `Q_meta`/`Q_res`/`Q_good`/`Q_rmeta` unbounded, `Q_focus`/`Q_focusback` bounded **1**; `Local` still **8**, `ControlTerminal` still **114** |
| **S3** | **21 objects reparented** (17 → 1.2, 4 → 1.5, 0 → 1.7) + **6 CONTROL terminals** (7 `from-ctl` rows) into their loops <!-- CORRECTED 2026-09-18, finding contradicted A3-c: "8 control/indicator terminals" -->, each verified by `OpOwnerChain_v1`; `#12589`, `#11639`, `ControlTerminal #642` still owned by `Diagram #639`; `Diagram` count unchanged **by the moves** |
| **S3b** | census over every moving node **and every node sharing a wire with one** **and** the sinks bared by S1d; **wires cut == wires re-wired**; the cut set ⊇ the 13 §8 crossings |
| **S3c** | 8 shift registers created and wired (4 / 2 / 2); `ControlTerminal` still 114; all 114 `panel_wiring` labels present |
| **S3d** | `IndexMode 0` on the 6 whole-array tunnels: `cross size`, `# of bead 4 packs`, `4 pack remainder`, `Array of cal clusters`, `Real-space cosine window`, `Cosine bandpass\nfor Hilbert ` |
| **S3w** | **the connection ledger, REVISED 2026-09-18 from run 3's OWN MEASUREMENT** (`tools/bench/build_d1_routeb_v0_run3.log:532`): `attempted 66, WIRED 63, FAILED 0, NO-ROUTE 3; SINK RULE 16 OK / 0 REFUSED / 0 BAD`. The 18 from-tunnel rows go by `OpConnectFromWire_v0` (all `Is Broken? FALSE`) and the 3 `ForLoop` newline-named rows by `wire_control` after the reparent. **Gate for the next run: 66 attempted, 0 FAILED, and the 3 remaining NO-ROUTE rows CONSTRUCTED per `docs/cycle27-plan.md` Pre-decided 13** (registers move with their nodes, `index_mode 1` kept; `Z/dZ` REORDERED before the `#403` reparent) ⇒ **0 NO-ROUTE**. ⚠️ Every `wire_control` call MUST pass `src_diagram_index` = the Traverse(`Diagram`) index of the diagram the control terminal actually lives on (**43** for `Diagram #639` before any reparent) — §11u.2; omitting it is what produced run 9's six 5001s <!-- CORRECTED 2026-09-18, finding already-measured (B4): the row carried the forecast "63 routed / 19 cannot meet". --> |
| **S3g** | the fresh kernel's 6 extra inputs each carry a constant with the `gpu_kernel_v1_fp.json` value, read back by `OpConstValueN_v1` |
| **S4** | each new loop's conditional terminal is driven by its own sentinel `Equal?` — non-zero `CondWireUID` on 1.2 / 1.5 / 1.7 via `OpLoopEndRef_v0`; **`#637` unchanged: terminal 648 ← wire 3457 ← `#11639`** |
| **S4s** | sentinel enqueues present on their writers' diagrams, literals **−1** (`Q_meta`/`Q_rmeta`/`Q_focus`) and **empty array** (`Q_res`/`Q_good`); 1.7's append gated by the −1 test; no new panel object |
| **S1b** | 🆕 **BASELINE `ExecState` of the UNTOUCHED working copy**, restored from `tools/recipes/build_d1_v0.py:461` (which `build_d1_routeb_v0.py:302-316` had dropped). Read in the recipe's OWN instance and flow **before a single construction call**, so "born 0" is separated from "the build made it 0". It is a **COLD** read and is therefore logged **UNREAD** as a verdict on legality (`docs/cycle27-plan.md` Pre-decided 14a) — it is a CONTROL for S5, not an acceptance |
| **S5** | `new_since('Invoke')` empty, `remove_bad_wires_scripted`, `ExecState` read and **reported as a PAIR with S1b's baseline** — a cold `ExecState 0` is **UNREAD**, never "broken" (14a: three BYTE-IDENTICAL files each read 0 cold and 1 with the ORIGINAL preloaded, `tools/bench/diag_d1_execstate_preload.log:13,:33`); saved, size recorded. **Any value returned beside an error is reported UNREAD, never as a value** (Pre-decided 14) |
| **S5c** | 🆕 **MEASURE BEFORE DELETING** (Pre-decided 14). If S5 reads `ExecState 0`, `preload_reread()` re-reads the **LIVE** copy in a restarted instance **with the ORIGINAL preloaded READ-ONLY** (the `tools/bench/p2_open_copy.py` pattern) **BEFORE any delete**, and **both** readings go to the log. Run 3 deleted its working copy and destroyed the evidence; that must not repeat |
| **S6** | cold re-open in a restarted LabVIEW: `Diagram 174`, `WhileLoop 6`, `ControlTerminal 114`; original md5 unchanged **after**. `ExecState` here is read with the ORIGINAL preloaded read-only, and a cold value is UNREAD |

🔴 **NO PRELOAD IS ADDED TO THE BUILD ITSELF** (`docs/cycle27-plan.md` Pre-decided 14 item (b), the recipe's
"14(b)"): a preloaded original can **cross-link** the working copy to the in-memory original's subVIs, and
`g.save(TARGET)` would write that cross-linking to disk. Preload is confined to **read-only** diagnostics in a
step that never saves. A preloaded `1` is **necessary, never sufficient** — it can also MASK a genuine break by
supplying subVIs the saved VI would not resolve alone.
<!-- REVISED 2026-09-18, finding already-failed (B2): S5/S6 previously gated on a bare "`ExecState 1` warm" /
     "cold `ExecState 1`" read with nothing preloaded, which 14a measures as reading subVI LINKAGE. -->

`ExecState` is meaningless between S1d and S4 (the deletes and moves cut wires — MEASURED §2b). Read it at
S1b (baseline) and S5/S5c/S6.

### N1 — numeric, rule 1a — **unchanged from REV 4 §10**

Fixture replayed through **1.2 + 1.7** on a **scratch copy of D1** by feeding `Q_work` from `IMAQ ReadFile`; gate =
the `.tra` against the original's, **first 10,018 frames** within `decisions.md:38`; whole-fixture figures reported
separately (STATUS OPEN 16). ⚠️ **B changes the rule-1a claim's shape**: in A the 13 shared kernel inputs were
*re-wired from the same sources*; in B the kernel is a **fresh node wired to the same sources by name**, and the 18
R1 rows are the ones where "the same source" is not yet demonstrable — so N1 is the **only** acceptance for them.

### F1 — live, 5 min (uncapped since §11h deleted the TIFF writer) — **unchanged**

`drive_original_copy_v3.py`'s method (16/16): second COM apartment, 3 picks in the Image display, `Done Picking
Beads?`, 3 token-gated `choose bandpass` clicks, absolute save path. Camera only, rig disassembled, **no beads** —
tracking errors without beads are expected and are not a failure. Records: frames acquired / tracked / written; both
buffer-number series with the §8 reconciliation; `Q_work`/`Q_res` high-water marks; the slot ledger; handles;
the TSV growing (N/A if the tracked-result count is 0).

### F2 — stop / restart — **unchanged**

`stop (end)` by `SetControlValue`; **all four loops exit** — 1.1 on the panel Boolean, then 1.2 / 1.5 / 1.7 on the
sentinels, in that order; no error 1122; the `.tra` written and re-openable; restart 15 s; stop again; close without
saving; scratch deleted; original md5 unchanged. Inherits STATUS OPEN 17b (score the **stop**, not the restart).
No `VISA Close` gate — the original has none and D1 adds none.

---

## 8. What B does NOT need

1. **Almost no cross-diagram index wiring — 2 rows, not 17.** A's wall (`d1-build-plan.md` §11n.2) was a wire whose
   **source is on `Diagram #686`** and whose **sink is inside a new loop body** — two nested diagrams, needing a
   second `To More Specific Class`, **MEASURED unbuildable** (`build_opconnectnested_v0_run1.log`:
   `W4 ROUTE A wired: ExecState 0`). In B that shape survives in **exactly two rows** (R8); the 6 index rows of §4
   are inside 1.2's body and R1's candidate (i) is inside `Diagram #686`, both of which `OpConnectNested_v0`
   expresses as built. ⚠️ Stated exactly: the claim is **17 → 2**, not zero.
2. **No tunnel-source resolution.** A had to walk `Tunnel.Outside Terminal 6356001 → Connected Wire 634A000 →
   Wire.Terminals[] 6371003 → Is Source? → Owner` to find a named origin for 17 rows, and MEASURED that 16 of them
   end at `outer_source: null` — there is no named origin to find. B never asks the question: it branches from
   `#637`'s own outer terminal, which it addresses **by index**, on the same diagram. (This is what makes R1 a
   *tunnel-creation* problem rather than a *source-resolution* one — a strictly smaller open question, but still
   open.)
3. **No `Local`, no user event, no DVR** — §11c stands: 8 queues and end-of-stream sentinels. `Local` stays 8.
4. **No second reader of `stop (end)`** — `ControlTerminal #642` stays in 1.1 (§11c).
5. **No fifth op is authorised by this plan.** B uses the four the freeze lift closed at (`CreateEqual`,
   `CreateConst`, `CreateConstOnTerm`, `ConnectNested`) plus `OpStopFromNode_v0`, `OpMoveIn_v0`, `OpLoopEndRef_v0`
   and `OpOwnerChain_v1`. R1's resolution may need one; that is the judgement session's call, not this file's.

---

## 9. What this plan does not decide — **two of the four are now DECIDED, and the other two are ANSWERED**

<!-- REVISED 2026-09-18, finding settled-already (A1): the first two bullets were reserved questions that
     `docs/cycle27-plan.md` Pre-decided 13 and STATUS NEXT had already answered; the last two were genuinely
     open and are answered here by the cycle-36 judgement session. -->

* ~~whether route B is started at all (§11p reserves it)~~ — ✅ **DECIDED.** STATUS NEXT (user, 2026-09-18 21:3x)
  makes a D1 build dispatch the next cycle's **first act**, and `docs/cycle27-plan.md` Pre-decided 1/6 sets the
  order D0 → D1 → D2 with N1 already satisfied. §11p's reservation is discharged.
* ~~R1's resolution (tunnel creation from an unnamed source) — (i), (ii) or a new op~~ — ✅ **DECIDED AND
  MEASURED.** Neither (i) nor (ii): `OpConnectFromWire_v0` branches from the **wire's** source terminal, and run 3
  wired all 18 rows with it, every one `Is Broken? FALSE` (`…routeb_v0_run3.log:532`). The three rows that
  remained are dispatched by `docs/cycle27-plan.md` Pre-decided 13 (shift registers move with their nodes;
  `Z/dZ` is a REORDER), with **both authorisation flags `False` permanently**.

**The two genuinely open bullets — ANSWERED 2026-09-18 by the cycle-36 JUDGEMENT session:**

* **`GObject.Move` of the six structures IS ACCEPTABLE UNDER RULE 1a.** ✅ *Decision of the cycle-36 judgement
  session.* Moving a structure **carries its frames intact** — MEASURED `probe_move_into_v0.log` P3, `Diagram`
  count **171 → 171** across the move — so what changes is **which loop the node is scheduled in**, not the
  per-bead maths, the parameters that reach it, or the numbers that come out. Rule 1a permits exactly that
  ("only *scheduling* may change"). B's "build fresh" premise is weakened as a description of B, and that is a
  bookkeeping fact about this file, not a rule-1a problem.
* **N1 ALONE DOES NOT CARRY THE 18 R1 ROWS' EQUIVALENCE.** ✅ *Decision of the cycle-36 judgement session.* N1
  measured `GPU_kernel_v1.vi` against the CPU kernel **on the fixture** — it did not exercise the assembled D1 VI,
  so it says nothing about whether the 18 from-tunnel rows deliver the same values by the same route. **A
  D1-level numeric fixture run is REQUIRED before D1 is accepted**; N1's acceptance (cycle 34) clears the kernel,
  not the assembly.

---

## 11. R1's two `LeftShiftRegister` rows — the queue is REFUTED; the register moves with its node

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
| what the right-inside wire's SOURCE actually is | **`LoopTunnel #9227`** — not a node at all | **`LoopTunnel #29616`** |

Three consequences, none of them an opinion:

1. **`queue_node('obtain', …)` cannot be typed here.** It takes the element type from a NAMED OUTPUT of a node
   (`tools/gscript.py:1068-1074`), and the only candidate — the writer of the partner right register — is
   unnamed; on the machine its wire's source is a `LoopTunnel`, which is not a node. The queue plan could not
   have passed its own gate.
2. **The sink AUTO-INDEXES.** `index_mode 1` means `#1359` t1 feeds the For loop an ARRAY and sets its N. A
   queue delivering one element per frame-loop iteration is a different computation (rule 1a), and gate **S3d**
   asserts `IndexMode 0` on six OTHER tunnels — these two have no index-mode gate at all. **Any future design
   for these rows must state what happens to `index_mode`.**
3. **These are READ-WRITE registers.** The moving node reads t1/t3 and writes t2/t5. A transport that carries
   only the read side silently stops the loop-carried state from updating.

**The mechanism this project already decided** (`docs/frame-loop-wire-graph.md:397` "each must live in exactly
one loop"; `docs/d1-build-plan.md:446`, where `#376` moves into 1.7 **with its two shift registers**) is: the
register moves with the node, built by `add_shift_reg` + `wire_sr`, which §2b already budgets 8 of. The queue
form was dispatched, attacked and abandoned on 2026-09-14
(`archive/peer/2026-09-14-stage2-shiftreg-primitive.md:126-129` — replaced by `Loop.Add Shift Register`
**6361000** = `OpAddShiftReg_v0`). **Honest limit, not to be read as a free fix:** `wire_sr`'s `LeftOutNode`
variant reaches a *top-level* node via `VI.Block Diagram` (`docs/toolkit-capabilities.md:42`), and the two
initialisers sit on `Diagram #686`, which `docs/diagram-hierarchy.md:95-97` measures as a **FlatSequenceFrame**
diagram, not the top level. Which route is cheaper is NOT settled by any evidence on disk.

~~**The one question judgement must answer:** do `#1359` and `#29874`'s registers move into 1.2 with their nodes
(making `1.2` the single writer, as the rule says), or does the value cross some other way?~~
✅ **ANSWERED — `docs/cycle27-plan.md` Pre-decided 13** (judgement, cycle 35, resting on `docs/cycle15-plan.md`
Pre-decided 1/2 at `:118-129`, which its own frontmatter `:5-7` keeps authoritative): **the registers MOVE WITH
THEIR NODES into loop 1.2**, built with `add_shift_reg` + `wire_sr`, **`index_mode 1` kept exactly as the original
has it**. `SR_QUEUE_AUTHORISED` stays **`False` permanently** — "the answer is no, not not-yet"; a build that
needs it True is the wrong build.
<!-- REVISED 2026-09-18, finding settled-already (A1): this paragraph reserved a question already decided. -->
The three consequences above are unchanged and are the reason the queue form was refused, not superseded by it.

### 11a. `#2222` t0 ← `Z/dZ` (R3) — MEASURED, and the temporary sink turns out to be optional

`tools/bench/diag_sr_transport.log`: `Z/dZ` is on the panel exactly once as a CONTROL (uid 47) and **it already
drives wire w730**; `#2222` t0's wire **is w730** — the same net, whose three terminals are the control terminal
(source, owner `Diagram #639`), `Tunnel #2276` (sink) and one empty slot. **No named sink on the net**, which is
exactly why `wire_control` cannot reach it.
So the branch source exists on the pristine original and the temporary sink is only needed if the moves cut
w730. `from_ctl_unnamed` therefore reads the control's own wire first and only then considers a temporary.

🔴 **THE CONDITIONAL IS RESOLVED — AND IT RESOLVES THE OTHER WAY** (MEASURED, run 3): `Z/dZ` carries w730 on the
**pristine** copy but **NO wire on the BUILT one** — the moves do cut it. So the answer is **not** a temporary
sink: it is `docs/cycle27-plan.md` Pre-decided 13's **REORDER** — make the `Z/dZ` → `#2222` t0 wire **by index
(`OpConnectNested_v1`, sink `is_source` FALSE) BEFORE the S3-ct reparent of `ControlTerminal #403`**
(`docs/cycle15-plan.md` Pre-decided 3), while the control's own wire still exists to branch from.
<!-- REVISED 2026-09-18, findings already-measured (B4) + settled-already (A1): this section left the choice
     conditional on whether the moves cut w730; run 3 measured that they do, and Pre-decided 13 chose the
     reorder rather than the temporary. -->

#### CURRENT STATE OF THIS ROW after RUN 5 (2026-09-19) — the cut is a WRONG-DIAGRAM SOURCE LOOKUP, measured

Run 5 turned `TEMP_SINK_AUTHORISED` on for this row (Pre-decided 13a) and the row got **further than ever and
still died**. What the run measured, in order:

- The reorder-by-index retry is **impossible in principle for this row**, and it now says so instead of
  returning silently: `tools/bench/build_d1_routeb_v2_run5.log:331` — *"RETRY not possible - ControlTerminal #403
  is not in Diagram[24].Nodes[] (index None, terminals []), and OpConnectNested_v1 addresses
  Diagram[].Nodes[].Terminals[] only"* — i.e. **R3** again, from the machine.
- The temporary sink was then created **well-formed**, refuting the predicted silent-default-refnum failure:
  `Equal? #10104` on `Diagram[24]`, census `{0: ('x = y?', True, 0), 1: ('y', False, 0), 2: ('x', False, 0)}`
  (`…run5.log:332`).
- The row died one step later at **`wire_control ['Z/dZ'] -> Function.['x']: error 5001
  LV-Scripting.lvlib:Get Controls.vi`** (`…run5.log:402`).

**THE CAUSE (FACT, from the failed-prediction review `archive/peer/2026-09-19-zdz-wirecontrol-5001.md`, which
REFUTED the sink-side reading and whose account matches the recipe's own text).** `Get Controls.vi` is the
**SOURCE-side** resolver, so the name it could not find is `'Z/dZ'`, not `'x'`, and `Wire Inputs.vi` never ran —
the `:332` census and the `:402` error address different objects, so there is no contradiction between them. The
temp-sink branch passes `src_diagram_index = diag_index(TARGET, FRAME_BODY_UID)`
(`tools/recipes/build_d1_routeb_v2.py:1376-1377`) with `FRAME_BODY_UID = 639` (`:288`) — **the STAY diagram** —
while S3-ct had already reparented `ControlTerminal #403` to `Diagram#567` (`…run5.log:171`) and the temporary
sink was created on `Diagram[24]` (`:332`). The source is looked for on the diagram it no longer lives on. This
is a **repeat of run 9's six 5001s**, the failure class `§11u.2` already records.

🔵 **CANDIDATE FIX — BUILT 2026-09-19 (cycle 38, P1), UNRUN.** The recipe already contained a two-index retry
that solves exactly this for the five sibling labels, which all succeeded on index 24:
`tools/recipes/build_d1_routeb_v3.py:1736-1753` builds `order = [sd_moved, sd_stay]` (or the reverse, from what
S3-ct measured) and tries each, verifying **by effect** on the sink terminal's own wire. The temp-sink branch did
not use it and passed one fixed index; it now runs the same retry at
`tools/recipes/build_d1_routeb_v3.py:1479-1498`. **v3 IS THE LAUNCH TARGET** (v2 is blocked by its own stop
record and carries the same code two lines lower, `:1738-1755` / `:1481-1500`, plus one extra header
correction).
⚠️ **CITATIONS CORRECTED 2026-09-19** (prior-art F3, `archive/peer/2026-09-19-priorart-d1-routeb-run6.md`): the
old `:1567-1584` / `:1376-1377` / `:1386-1389` cites are all stale — P1/P2/P3 shifted the file — and the warning
they carried was **FALSE**. `wire_source_owner` HAS been measured on a `ControlTerminal` source, by this build's
own diagnostic: `tools/bench/diag_hierarchy_a3.log:106` and `:110` (2026-09-16) each return exactly one
reciprocal source terminal, `source=True owner 'Diagram' uid 639`, for two of these six labels. The row that
died at `…run5.log:404` is therefore not evidence about that op; the census logged before the call
(`tools/recipes/build_d1_routeb_v3.py:1533-1546`, v2 `:1535-1548`) is what separates the reparent/temp-sink
state from it.

⚠️ **The temporary is DISARMED PERMANENTLY** (`TEMP_SINK_AUTHORISED = False`, Pre-decided 13 — "the answer is no,
not not-yet"; only the judgement session could turn it on and it has declined): creating a bare `Equal?` with `src_names=()`
contradicts `OpCreateEqual_v0`'s recorded contract (both operands come from `Get Outputs`,
`docs/toolkit-capabilities.md:52`) and `docs/NAMES.md:468-480` records that an invalid terminal refnum produces
an **error-1055 MODAL DIALOG that an error-out indicator does not silence** — disqualifying unattended.
The delete step itself is safe and needs no new measurement: a branched net is ONE `Wire` object, so deleting
the disposable SINK NODE (never the wire) plus Remove Bad Wires keeps the branch
(`archive/peer/2026-09-15-opwiresource-fail3-branch-wire-is-one-object.md:24,:32-35,:49-52`).

---

## 10. `OpGetErrors_v0` — the third attempt at `VI.Get Errors` 452, and WHAT IS DIFFERENT NOW

> 🔴 **NOT AUTHORISED — STOPPED BY ITS OWN PRIOR-ART REVIEW, 2026-09-17 16:48/16:56, and nothing below was
> built.** `-Dual`, both arms independently: `archive/peer/2026-09-17-priorart-opgeterrors-codex.md`
> (`refuted-already`, `already-failed`) and `…-opus.md` (`settled-already`, `refuted-already`, 5 ×
> `contradicted`, `helper-exists`, `already-measured`). The stop rests on `docs/d1-build-plan.md:917-918` (re-measured 2026-09-20, was `:859-860`) —
> *"No diagnostic, framework, or review cycle before F1/F2 … third op → PHASE "full" → save → N1 → F1 → F2"* —
> a judgement decision taken THE SAME DAY. That file was opened and the citation covers this case exactly, so
> the "refute the citation" override is not available. Two corrections the review made to the text below stand
> regardless: **§10b.1 is confirmed** by `tools/gscript.py:2094-2123` vs `:2156-2158`, and **§10c.2's "no donor
> is known to exist" is CONTRADICTED** by `docs/toolkit-capabilities.md:187-189` plus the NI thread's snippet —
> a snippet is a PNG carrying diagram code, so the donor is *manufacturable*, not merely findable.
> The section is kept so a future judgement session inherits the plan instead of re-deriving it.
>
> 🆕 **TWO FURTHER CORRECTIONS, ADDED 2026-09-18 (finding refuted-already, A2) — both fallbacks have since DIED,
> and they are written in here so no future session inherits a plan whose escape routes are already closed:**
> 1. **The bare-terminal census discriminates NOTHING.** `docs/cycle15-plan.md` item 4's "count the bare named
>    input terminals" fallback returned an **IDENTICAL 375 bare named input terminals over 170/170 diagrams on a
>    KNOWN-GOOD copy** (`tools/bench/diag_d0_execstate_preload.log:26-36,:65-75`), so it cannot tell a broken VI
>    from a legal one. **WITHDRAWN** by `docs/cycle27-plan.md` Pre-decided 14.
> 2. **`Get Errors` 452 is ABSENT from the exported `VirtualInstrument` ActiveX interface**
>    (`archive/peer/2026-09-18-fstunnel-v1-b4-execstate0-codex.md:156,:191`), so direct COM invocation of it is
>    unlikely to be reachable over this project's path at all — it is off the critical path, not merely
>    unauthorised. `docs/cycle27-plan.md:106-112` carries the same conclusion.
>
> Neither correction re-authorises §10. The section remains **NOT AUTHORISED**.

Authorised by the judgement session (brief, 2026-09-17, decision 3) as the reader for "why is this VI
`ExecState 0`", which OPEN 39 names as the missing instrument. **Budget: 2 attempts.** This section exists to be
attacked by the prior-art review before a line is built — the two previous attempts are recorded FAILURES and
CLAUDE.md's "when a diagnosis is GUESSED twice, build the reader" is not a licence to rebuild the same thing the
same way.

### 10a. What FAILED, twice, and exactly how — read from our own files, not remembered

| attempt | record | symptom |
|---|---|---|
| 2026-09-09 | `docs/toolkit-capabilities.md:259` | "Invoke node created with only reference/error terminals, with and without the private ini tokens" |
| 2026-09-14 | `docs/toolkit-capabilities.md:157` | same signature: "node created with only `reference out` / `error out` — **no `Errors`, no `Details`**" |

The recipe from those attempts is still on disk: `tools/recipes/build_opgeterrors.py` (107 lines). It calls
`g.build_invoke(OP, "VI Server:VI", "452", …)` at line 34 and then *probes for output terminals by creating
indicators on terminal indices 0–7* (lines 49–59), i.e. it infers attachment from what a later walker can see.

### 10b. The four things that are different, each with its citation

1. **THE CREATOR'S ERROR IS NOW A RAISE — but only on the PROPERTY path.** `OpBuildPN_v1` exposes the creator's
   real `error out` (pane index 15; index 10 with the same name is a sink) and `build_property()` **raises** on it
   (`tools/gscript.py:2150-2163`). `build_invoke()` does NOT: it drives `OpBuildInvoke_v0.vi`, whose "`error out`
   indicator is now unwired, so read creator errors from the dialog watchdog" (`tools/gscript.py:2094-2123`).
   ⇒ **The first build is `OpBuildInvoke_v1`, not `OpGetErrors_v0`.** `docs/toolkit-capabilities.md:247-249` says
   this in as many words: *"an `OpBuildInvoke_v1` with the same exposure is needed for the Invoke case"*. Without
   it a third attempt would produce the same uninterpretable result as the first two, which is the definition of
   `repeated-failure-class`.
2. **"No error" is NOT a verdict that a member attached** (`docs/toolkit-capabilities.md`, prior-art A3-iv,
   2026-09-16): `Control.Value` 633200D — a *valid* ID on the wrong class — created a node with no `Value`
   terminal and **no error at all**. The robust check is the **data-terminal-name census** on the created node
   (`tools/recipes/build_opcaseframes_v0.py:49-58`: exactly one data SOURCE terminal, its name printed, never
   guessed). So the acceptance here is: after creating the 452 Invoke, enumerate the node's terminals and print
   their NAMES; `Errors` / `Details` present = attached, `reference out` / `error out` only = refused.
3. **The three probes that "proved" private members unreachable were VOID, and the reason is known**:
   `net_map` / `OpNetInfo_v1` "does not see nodes created by another op in the same session"
   (`docs/toolkit-capabilities.md`, RESOLVED 2026-09-14, `tools/bench/probe_stale_nodes.log`). The old
   `build_opgeterrors.py` verifies exactly through that broken route. ⇒ read terminals with `node_terms()` on a
   re-read report, not with the walker, and carry a **CONTROL** (a known-good public method, `Terminal.Create
   Indicator` 6349C02) through the identical code path in the same run — the discipline
   `docs/toolkit-capabilities.md` imposed after probe run 1 concluded a limitation from a broken reader.
4. **The COM poison guard is in** (STATUS OPEN 34, `…-d1-route-b-1.md` §2, 11/0), so a refused creator call no
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
   `Create from Reference` from a donor — **not attempted this session; it needs a donor VI that contains the
   node, and none is known to exist in this project.**
3. **Functional test before any use**: a scratch VI deliberately broken in two independent ways — one unwired
   REQUIRED input on a subVI call, and one type-mismatched wire — and the op must NAME the broken object's uid
   and print the error text. A `Get Errors` that returns an empty list on a VI whose `ExecState` is 0 is a FAILED
   op, not a clean VI.
4. **Budget 2.** Two failed builds ⇒ stop, write both logs' failure lines, hand back. Nothing in route B's
   build order depends on this op existing.

### 10d. What this op does NOT decide

It reports; it repairs nothing. The route-B run may use its output to name what is broken, and only rows the op
NAMES may be fixed — the budget-2 rule in the brief exists so that "ExecState 0" never again becomes a licence to
guess at 63 wires.
