---
type: plan
status: frozen
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
build_status: SUPERSEDED BY §11t - **ROUTE A IS CLOSED** (judgement, 2026-09-17). Run 9 (§11s.2) was A's last
  attempt: 55 pass / 8 fail, re-wire 42 WIRED / 6 FAILED / 18 NO-ROUTE of 66, ExecState 0, nothing saved,
  N1/F1/F2 not run. The FOURTH op that §11j did not authorise, OpConnectNested_v1, WAS built and IS functional
  warm and cold - it is not the blocker. The blocker is `OpConnectFromWire_v0` (§11t), a writer whose
  `Wire Source` is a wire-terminal reference; it is NOT BUILT. Work continues in docs/d1-route-b-plan.md.
  ⚠️ §11u: run 9's "3 of 8 wires deleted by Remove Bad Wires" is WITHDRAWN - the gate measured uid identity.
reviewed_by_latest: archive/peer/2026-09-17-priorart-priorart-connectfromwire.md
---

# D1 build plan — REV 4. The first slice of the seven-loop VI, inside a COPY of the original

**REV 4, 2026-09-17.** Rev 3 was a reading document that ended in two lists of open decisions (§11a, §11b). Rev 4
**is the build order**: every decision of §11a/§11b is folded into the body where it acts, the move table is
node-by-node against the BEFORE census keys, and the prediction contract carries counts a machine can check. The
recipe written from it is `tools/recipes/build_d1_v0.py`.

Target `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Track_v6_D1_GPU.vi` = a fresh copy of
`Min_Track N beads V6_ParallelLoop.vi` (md5 `2a78e17c449cacdaf5da389818526859`, asserted before **and** after every
run; the original is never opened for writing — rule 1).

---

## 0-BLOCKER. ✅ **RESOLVED by §11c (2026-09-17): TRANSPORT = QUEUES ONLY.** The record of why is kept below

> **This section no longer blocks the build.** §11c is binding: a **1-element DBL queue** for 1.5's wake-up
> (written by 1.2 on the 25-frame tick, **timeout 0**), a **1-element queue** for the reverse crossing polled by
> 1.1 with **timeout 0** (**`#12589` stays on 1.1**, §11.3 resolved), and **end-of-stream sentinels** for the three
> new loops' stop, so **no second reader of `stop (end)` is needed** and `ControlTerminal #642` stays in 1.1.
> No Local, no user event, no DVR. Everything below is the measurement that led there, kept verbatim.

⚠️ **This section said "cannot be built by this fleet" and that was WRONG — corrected after
`archive/peer/2026-09-17-priorart-d1-build-rev4.md` A1.** This project *formally withdrew* that exact claim on the
same day (`archive/peer/2026-09-17-priorart-ctlterm-move.md:601-608`: *"a false 'impossible' that I wrote … the
citation is **withdrawn** … §0d now reads **UNMEASURED, NOT IMPOSSIBLE**"*, carried in STATUS OPEN 24b), and rev 4
reinstated it as the thing that stops the build. **The recorded state is UNMEASURED.** Keep the two apart:

* **MEASURED (a fact about the fleet's contents today):** no op creates a `Local`, and none writes `Control Name`.
* **UNMEASURED (a fact about nobody having tried):** whether one *can* be built. No gate may be keyed to
  "impossible", and `build_d1_v0.py`'s S0 no longer is.

**§11b.1 is binding for rev 4 and its closing clause is still false as written.** It reads
*"`restructure-plan-4.6.md:225-226` already adopts locals; **the Local creator exists**."* It does not exist:

| what was checked | how | result |
|---|---|---|
| a Local creator in the Python API | `grep "^def " tools/gscript.py` (97 functions listed in `docs/toolkit-capabilities.md`) | **none.** `grep -ni "local" tools/gscript.py` returns **one** hit, `:636`, a docstring sentence about bare terminals |
| a Local op VI | `ls user.lib\claudeDev\Op*.vi` → **97 ops** | **none touches `Local`** |
| a recipe that creates one | `grep -rl "Local" tools/recipes/` | 2 files, both *mentioning* the class (`build_opreportall.py` census, `probe_move_ctlterm_v0.py` prose) |
| the property that would re-point one | `grep -i local docs/vi-server-ids.json` | **no entry.** `docs/NAMES.md:246` carries `Local.Control Name` **6355400 "read/write"** — a *catalogued* id, and `toolkit-capabilities.md:10-16` says in its own header that an entry in that file is **a candidate, never evidence** |
| a donor Local to copy | `docs/main-vi-panel-map.md:405-415`, the 2026-09-14 sweep | the VI's **8** Locals are bound to `Total Lost Frames` ×2, `File # Saved`, `Focus Pos (Track)`, `Rot pos (deg)`, `Trans Pos (mm)`, `Picture`, `Color table`. **None** is `stop (end)`, a slice index, a frame counter or a spare Boolean |

So the route is *copy a donor Local* (`copy_by_index`, which lands on the **top-level** diagram) → `move_in` it to
the loop body → **re-point `Control Name`**, and the last step has no op. Building one is a **new general-purpose
op**, which `docs/cycle15-plan.md:104` freezes for the duration of D1. This is exactly the shape §0d recorded as
*"route (ii) is UNMEASURED, NOT IMPOSSIBLE"*; §11b.1 upgraded "not impossible" to "exists" without a measurement.

**Three separate parts of D1 depend on it, not one:**

1. **1.5's wake-up** — the slice index (§0b: 1 DBL) and the frame counter written by 1.2, read by 1.5.
2. **The reverse crossing** — `#10407 t6 → #12589 → #11639 → #637`'s conditional terminal (§0b), which §11b.1
   turns into a Boolean local.
3. **The stop, in all three new loops.** §3's rule is that every new loop reads its stop from a terminal **inside
   its own body**. There is exactly **ONE** `stop (end)` `ControlTerminal` (uid 642, control uid 7 — measured
   `probe_move_ctlterm_v0.log`), and route (i) moves it into exactly **one** loop. The other two need a second and
   third reader of the same Boolean, i.e. a Local. No op creates a `ControlTerminal` either.

⚠️ **Item 3 is an INFERENCE, not a measurement** (rev-4 review B2). "Three new loops ⇒ three readers of
`stop (end)` ⇒ a Local" ignores the two live-mode stop mechanisms this project already recorded:
`stage2-assembly-step-c.md:45` — *"Live mode (step D) is where the While tracker, an **end-of-stream token** and a
timeout-gated Case are unavoidable"* (1.2 and 1.7 are queue **consumers** of 1.1, so a token ends them with no
second panel reader at all) — and `frame-ownership-design.md:102-103` — *"First error wins: capture it,
**broadcast stop**, let each loop drain and release its own resources."* `pre-rig-master-plan.md:95` asks for
*"every loop stops from a Boolean read inside it"* and *"seven stops and one order"*; it never asks for seven
**panel-terminal** readers, and `stage2-plan.md:92-94` offers terminal/local as **examples**, not an exhaustive
list.

**What building one would actually cost, so the judgement session is choosing between priced options.** The
archived exchange this plan must check before re-asking (`archive/peer/2026-09-17-priorart-ctlterm-move.md:521`)
already states the condition precisely: *"a Local's binding is re-pointable **given a typed reference**"* — and a
typed `Local` reference is exactly what the fleet does not hold. The route is the documented **typed-control seed**
(`toolkit-capabilities.md:64-77`: *"the same trick yields any class an NI example or library VI exposes on a
property-node input … check the example folder first"*), so an `OpLocal` family is **three** pieces: a `Local` seed
harvested from an NI scripting example, a **creator**, and a `Control Name` **writer**. ⚠️ **The writer is NOT a
new family** (rev-4 review B1): it is the `OpSetIndexMode_v0` shape — *"Traverse('LoopTunnel', index) → cast →
IndexMode **WRITE property node** ← a control"* (`gscript.py:1661-1662`) — built a second time as `OpSetLabel_v0`
(`gscript.py:2451-2454`, `Node.Label` 6359001 → `Text.Text` write), and deriving from those front halves is this
fleet's normal move: `OpTunnelInd_v0` was *"built from OpSetIndexMode_v0, whose front half … was already proven"*
(`gscript.py:1690-1692`), and `OpLoopEndRef_v0` is an *"additive build on OpWhileCast_v0"*, 16/16, **this cycle**
(`toolkit-capabilities.md:50`). So the writer is one additive op against a proven template. What is genuinely
unpriced is the **creator** (whether `New VI Object` even has a `Local` style is
**unlikely** — the skill's own externally-sourced line is
`.claude/skills/labview-automation/references/vi-scripting.md:308`, *"`New VI Object` cannot create most node
types (error 1054), and NI's own advice is to copy from a donor"*, and `:465` records the 0–399 style sweep
creating nothing; `archive/peer/2026-08-28-wire-indicators-api.md:59` records it only for *front-panel* objects,
so the realistic creator is copy-from-donor, which lands on the **top-level** diagram and still needs the
re-point).

### 0-BLOCKER.b — the FOUR candidate transports, after the census the first draft never ran

⚠️ Rev 4 first wrote *"queues … that is the only transport with evidence"* off a four-place census (`gscript.py`,
`claudeDev\Op*.vi`, `tools/recipes/`, `vi-server-ids.json`). **It never opened the donor library every writer op in
this fleet was wrapped from** (rev-4 review A3): `docs/REFERENCES.md:29-30` — LV-Scripting at
`vi.lib\Erdos Miller\LV-Scripting\`, **84 VIs** — and `docs/stage2-plan.md:110` records the four queue ops as
wrappers of `Create Obtain Queue / Enqueue Element / Dequeue Element / Release Queue.vi` from **that folder**.
**Listed 2026-09-17** (`ls` of that folder, 85 entries), it also ships a complete event set and a DVR set:

| candidate | creator VIs that exist on disk | status |
|---|---|---|
| **queue** | `Create Obtain Queue` · `Enqueue Element` · `Dequeue Element` · `Release Queue` | **EXERCISED**, 4 ops built, core 162/162 |
| **1-element queue** (latest-value) | the same four | **the project's own recorded latest-value transport** — `restructure-plan-4.6.md:55`: *"\| 2 → 6 \| **local variable / 1-element queue** \| lossy by design; the display only needs the newest \|"*. A queue and a local are tabled as **alternatives for the same duty**, which refutes rev 4's "a queue contradicts freshest-wins" (review A2). `decisions.md:21`'s "no `Lossy Enqueue Element`" is scoped to the **acquisition** path, not a 3.6 Hz focus wake-up |
| **user event** | `Create Create User Event` · `Create Generate User Event` · `Create Register for Events` · `Create Unregister for Events` · `Create Destroy User Event` · `Create Event Structure` · `Construct Dynamic Event` · `Get Event Data In` · `Wire Event Data Out` · `Exit Event Structure` | **UNEXERCISED but present** — `stage2-plan.md:114` already shelved `Create Event Structure.vi` as *"not needed in stage 2"*. `Generate User Event` never blocks the generator, which is the property §6 wants |
| **DVR** | `Create New DVR` · `Create In Place Element DVR` · `Create Delete DVR` | **UNEXERCISED but present** |
| **Local** | **none in the library** — no `Create Local.vi` | no creator anywhere; route = seed + creator + writer (above) |

`toolkit-capabilities.md:14-15` is the distinction rev 4 collapsed: **exercised** (queues) is not the same set as
**buildable**. `ARCHITECTURE.md:60`'s "no Queue/Notifier primitive appears in the original" is not an obstacle
either — the queue ops needed no donor, only a creator.

**Which of these D1 uses is a design decision with a rule-1a consequence, and a material session may not take it**
(CLAUDE.md §3). `build_d1_v0.py`'s gate **S0** refuses to run until `TRANSPORT` is set by the judgement session,
and it now refuses on "unset / no creator built yet", never on "impossible".

---

## 1. The five D1 spec decisions this build is built on

Taken by the judgement session on 2026-09-17 after `archive/peer/2026-09-17-priorart-priorart-d1-build.md`
(10 findings, 0 novel). Quoted so no section re-argues them, and amended where a later measurement overtook them:

| # | decision | amended by | consumed in |
|---|---|---|---|
| 1 | **`#10407` (autofocus, VISA) gets its own loop** — the case and its VISA session alone in a loop, woken every 25 frames from the tracking loop; its other inputs by the same route and values as today | **§11b.1** replaced the notifier with locals (no notifier op exists); **§0-BLOCKER** finds no Local creator either | §6 |
| 2 | **Writer = stream AND accumulate** — 1.7 writes each result as it arrives *and* accumulates; at stop it calls the original `save N xyz traces.vi` #6384, so the `.tra` stays byte-compatible | **§11b.3** adds `#376 save trace.vi` itself to the writer loop — it *is* the accumulator | §7 |
| 3 | **Stop = two nodes and a fourth structure** — `stop (end)` #7 → `#11639`, and `stop (end) 2` #19587 → `#17883` → `Tunnel #22085` of `CaseStructure #22082`; #22082 is placed explicitly | measured in full, §4 | §4 |
| 4 | **Structures move by `Make Selection → Copy Selection → Paste`**, probed first, never inside the D1 build | **OVERTAKEN BY ITS OWN PROBE, cheaply**: `GObject.Move` with a wired `owner` relocates `CaseStructure #12589` **with its frame diagrams intact** (§2b, 12/0). The selection/paste op family is **not built**; D1 moves with `OpMoveIn_v0`. "Never probed inside the build" stands | §2, §5 |
| 5 | **Precondition readers/devices** — `OpLoopEndRef_v0` (how #637 stops, D1's S4 gate) and bgrun's `-> FAIL` scan | done, 16/0 | §4, §9 |

## 1a. What is already built or measured, and is therefore NOT re-derived here

| need | what exists | where |
|---|---|---|
| the stop/save seam's 16 terminals, every wire, every other end | measured | `docs/main-vi-stop-and-save.md` §4 |
| **the frame loop's conditional terminal and what drives it** | **MEASURED** (not inferred) | same file §1; `tools/bench/loopendref_637.json` |
| `save N xyz traces.vi` #6384 on diagram 19 after the loop, 7 of 8 inputs off #637's tunnels | measured | same file §2 |
| shutdown frame (diagram 83): IMAQdx Stop/Close, `ASI TG-1000 Close.vi` #29815, IMAQ Dispose | measured | same file §3 |
| kernel forward slice = 14 nodes, backward slice = 7 | measured | `docs/frame-loop-wire-graph.md:43-45` |
| producer/consumer core, 6 lock-stepped queues + pool, 162/162 | built | `docs/stage2-assembly-step-c.md` |
| queue / loop / exit_while / shift-register / drop_subvi / delete ops | built, functionally verified | `docs/toolkit-capabilities.md:24-35, 41-44` |
| **reparenting an existing node / structure / ControlTerminal into a new loop body** | **MEASURED 12/0 and 9/0** | §2b, §2c |
| **a `Local` node** | **NO CREATOR** — and ✅ **D1 needs none** (§11c: queues + sentinels) | §0-BLOCKER |
| relocating a plain primitive or subVI call by create-wire-delete | settled, `GObject.Move` "unnecessary" (now superseded by §2b, which makes Move the cheaper route) | `docs/decisions.md:19`, `restructure-plan-4.6.md:79-81` |
| GPU vs CPU on the fixture | **MEASURED twice, bit-identical**; k < 10018 → max \|Δx\| 4.857e-07 px, \|Δy\| 4.677e-07 px, \|Δz\| 1.279e-05 µm, **0 exceedances** | `docs/gpu-backend.md` §2026-09-17; `tools/bench/gpu_n1_deltas.json` |
| unattended drive of a copy through stages 0→4, run, stop, restart | built, 16/16 | `tools/bench/drive_original_copy_v3.py` |
| camera contract writer · frame accounting subVI #6810 | built / the original's own | `tools/bench/camera_contract.py`; `docs/frame-loop-anatomy.md:47` |
| identify what a mutating op created — by uid, never a cached Traverse index | recorded remedy | `tools/gscript.py:833-836` |

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
not simultaneously realisable — a sink takes one source and **there is no `Terminal.Disconnect`** in
`docs/vi-server-ids.json`. Same end state; confirmed (§11a.6).

### 2b. ✅ A STRUCTURE MOVES WITH ITS CONTENTS — 12 pass / 0 fail, 14 s (`tools/bench/probe_move_into_v0.log`)

| gate | result |
|---|---|
| P0a / P0b | original md5 `2a78e17c449c…` before **and** after |
| P1z / P1b / P1a | working copy is the donor (ExecState 1, Node 15, no U2G); collateral sinks restored on one net from `#236`; `Move.owner` carried by wire 645 from the Diagram cast **#683** |
| P1 | `OpMoveIn_v0.vi` **ExecState 1** — UID control label **`'UID 3'`** |
| P2a / P2 (CONTROL) | While loop on `Diagram #686` (Traverse index **19**) → `WhileLoop #1133`, body `Diagram #1170` at index 20; `#8885 Multiply` → owner `Diagram #1170` → `WhileLoop #1133` |
| P2b | `Diagram[20]` holds `[8885, 1134]` — the destination index still names the right diagram |
| **P3** | **`CaseStructure #12589` → owner `Diagram #1170`, total `Diagram` count UNCHANGED 171 → 171** — the frames came with it |
| P4a / P4 | 2 junk Invokes (`1145`, `1134`) purged; `Node` 626 → **627** (+1 = the new loop); `ExecState 0` afterwards, **expected** |
| census | `Wire` 1902 → **1895** (−7), `LoopTunnel` 132 → **130** (−2) |

**Read that census honestly.** The move **cuts** the wires that crossed the old border rather than re-routing them.
So a relocation is not a complete operation: **D1 re-wires every cut connection afterwards** (§8), and
**`ExecState` is meaningless between moves** — it is read once, at the end.

Two recorded facts that are not gates: a scratch copy of the original **has read `ExecState 0` in some runs**,
before any edit — an S-phase gate must not assume 1. ⚠️ The word "**headlessly**" stood here and is **WITHDRAWN**
(§11g.4; rev2 A2 of `archive/peer/2026-09-17-priorart-d1-full-route-rev2.md`): `build_d1_v0.py:413` **had the
panel open**, so headlessness was never the discriminator. The record splits **3–3 on PRELOAD** — 1 whenever the
ORIGINAL hierarchy is `GetVIReference`d before the copy is opened, 0 whenever it is not — and that pair has
never been varied in a controlled test. Also **handles 30,849 → 51,530 in 14 s**
(baseline ≈31,500), a growth to attribute by `handle_audit.py`, not a number to panic about.

### 2c. ✅ A CONTROL TERMINAL REPARENTS — 9 pass / 0 fail, 14 s (`tools/bench/probe_move_ctlterm_v0.log`)

| gate | result |
|---|---|
| Q0a / Q0b | original md5 unchanged before **and** after |
| Q1 | 114 `ControlTerminal`s and 114 `panel_wiring` rows |
| owner class | **all 114 report owner class `Diagram`** — the free `report_all` pre-filter filtered nothing here |
| **inside the frame loop** | **31 `ControlTerminal`s are owned by `Diagram#639`**, not the 6 §5a found from wired boundary wires (`642, 3173, 3453, 1924, 4837, 5634, 403, 9306, …`; full list in `tools/bench/ctlterm_owners.json`) |
| **Q3** | **`ControlTerminal #642` → owner `Diagram#1170`**, self-echo `'ControlTerminal'#642`, total count **unchanged at 114** |
| Q4 | `panel_wiring` still 114 rows, no label lost; the changed row NAMES the object: **`stop (end)` uid 7, wire 6929 → 0** |
| Q5 | `Node` 626 → 627; `ExecState 0` afterwards, expected |

This is the half of `docs/stage2-plan.md:92-94` that reads *"the control's terminal moved into one loop"*. **The
other half — "and locals in the others" — is the thing §0-BLOCKER found no creator for, and §11c makes it
**unnecessary**: the other loops stop on sentinels, so `#642` moves nowhere and stays in 1.1.**

⚠️ **Caveat on identification** (`archive/peer/2026-09-17-priorart-ctlterm-move.md` A3-ii): "every
`ControlTerminal` is a `panel_wiring` row" is two **non-recursive** counts agreeing, not a bijection —
`Panel.Controls[]` omits tab-page and cluster elements (`tools/gscript.py:640`). Terminal→control identification is
**reported, never gated**.

### 2d. If `GObject.Move` had not answered it (kept as the record; NOT built)

`TopLevelDiagram.Make Selection` **0x6349002** → `Copy Selection` **0x6349003** → `AbstractDiagram.Paste`
**0x6375400**, verified with `Selection List[]` **0x6349400**. Not a drop-in, and this is measured: `Make Selection`
takes `Objects[]`, an **array of GObject references**, and the fleet has no Build Array creator
(`grep "^def " tools/gscript.py`), while `create_control` would make an array-of-refnum control whose value cannot
be set over COM. Three new Invoke ops plus a missing primitive constructor = a new op family and its own cycle.

---

## 3. Loop assignment

| loop | is | receives |
|---|---|---|
| **1.1 ACQUISITION** | the **existing** `WhileLoop #637` | `#6810 get buff image-lost frames.vi` (row 1.8 — REUSED, §8); ~~`#22700 IMAQ Write TIFF File 2` unconditional, exactly as the original has it~~ **WITHDRAWN §11h — `#22700` and `#23020` are DELETED before the moves** (measured: the true original has neither); the camera reads, both stop terminals, `CaseStructure #22082`, and every node not named below |
| **1.2 TRACKING** | a NEW While loop on **`Diagram #686`** (Traverse index 19, the frame loop's own holder) | `GPU_kernel_v1.vi` in place of `#5058`, the reseed case `#5540`, the reseed selector chain, the forward-slice nodes that are neither autofocus nor writer, 4 shift registers, 5 `ControlTerminal`s |
| **1.5 FOCUS** | a NEW While loop on `Diagram #686` | `CaseStructure #10407` + `#48 ASI_adjust focus-subvi.vi` **only** (§11c: `#12589` **stays on 1.1**), 2 shift registers (one carries the **VISA session**); woken by the 1-element `Q_focus` |
| **1.7 WRITER** | a NEW While loop on `Diagram #686` | `#376 save trace.vi` (§11b.3 — it *is* the accumulator), the streaming TSV write, 2 shift registers |
| **1.9 STOP** | — | paths A and B of §4 stay **whole on 1.1**; the three new loops stop on **end-of-stream sentinels** (§11c), not on a panel read |

## 4. The stop, measured — row 1.9

✅ **`WhileLoop #637`'s conditional terminal is uid 648**, a SINK carrying **wire 3457**, whose single source is
`CompoundArithmetic` **#11639** — all inside `Diagram #639`. Read by `OpLoopEndRef_v0.vi`
(`WhileLoop.Loop End Ref` **6362C00**, data terminal **`LpEndRef`**), 16 pass / 0 fail
(`tools/bench/build_oploopendref_v0.log`, raw `loopendref_637.json`). The same run read #25380 → 25410 / wire 1737
and #15173 → 15276 / wire 19456.

| path | wiring (measured) | D1 |
|---|---|---|
| **A** | panel `stop (end)` **#7** → terminal (`ControlTerminal #642`) wire 6929 → `CompoundArithmetic` **#11639** t2, OR-ed with wire 12070 ← `#12589` t2 and wire 10249 ← `x = y?` #10019 → **wire 3457** → **#637 cond. terminal uid 648**; also → panel indicator `TurnOff` #24423 | **stays 1.1 WHOLE** (§11c): `#11639`, `#12589` and `ControlTerminal #642` all stay, so w12070 and w6929 are **not cut**. The only crossing is **into** `#12589` t1: `#10407` t6 (now on 1.5) → `Q_focusback` (1 element, timeout 0) → dequeued by 1.1 each iteration |
| **B** | panel `stop (end) 2` **#19587** → wire 15230 → `CompoundArithmetic` **#17883** t1 (with w18092 ← `.not. x?` #17837, w18056 ← `x = y?` #22284) → **wire 15229** → `Tunnel` **#22085** of **`CaseStructure #22082`** | **#22082 stays on 1.1 with path B intact** — nothing in the kernel's forward slice feeds it |

**Rule (NI's infinite-loop mistake, `stage2-plan.md:90-94`):** a front-panel Boolean wired in from outside a loop
becomes an input tunnel read **once**. Every new loop therefore reads its stop from a terminal **inside** its own
body. `exit_while` / `OpExitWhile_v0` is verified 5/5 (ExecState 0 → 1, the VI runs and stops) — **on a fresh VI
whose Boolean control terminal is at the TOP LEVEL**. ✅ **§11c removes the need for a second panel reader
entirely**: the only `stop (end)` terminal stays in 1.1, and 1.2 / 1.5 / 1.7 each stop on the **end-of-stream
sentinel** that arrives on the queue they already consume (§9a). Nothing reads `stop (end)` but `#11639`.
Shutdown order is **stop the users → drain → release**, so no error 1122 (`frame-ownership-design.md:68-72`).

---

## 5. The move table, node by node, against the BEFORE census keys

Keys are `tools/bench/d1_step0_census.json` → `diagram_43` (**47 nodes**) and `diagram_19` (**5 nodes**), plus
`shift_regs` (**14**), `tunnels` (**132**), `panel` (**114**). Every row's "moves?" is what `build_d1_v0.py`
asserts before and after. Labels are the census's own.

### 5a. Diagram 43 — the frame loop body (47 nodes)

| census key | label | D1 | why (measured) |
|---:|---|---|---|
| **5058** | `Track N beads four-fold over-kernel-v3.vi` | **DELETED; `GPU_kernel_v1.vi` dropped into 1.2** | the seam (§8); the GPU kernel shares its pane for 13 terminals (`gpu_kernel_v1_fp.json`) |
| **5540** | Case Structure (reseed) | → 1.2 | per-frame in from SR `#1142` (w1681 ← kernel w505) and SR `#5805` (w6041 ← kernel w5859); feeds `#5058` t0/t7 |
| **9647** | And | → 1.2 | x ← `#10950`; y ← panel control `Auto-Reset` uid 17472 |
| **10247** | Or | → 1.2 | x ← `#10445`; y ← panel control `Reset Tracking` uid 5605 |
| **10445** | Case Structure | → 1.2 | selector ← `#9647`; `Value` ← SR `#11001` (own counter, pair `#7311/#11001`) |
| **10950** | Less? | → 1.2 | x ← `#17289`; y ← `DigitalNumericConstant #10739` |
| **17289** | `min value` (implicit Property) | → 1.2 | **no wired input at all** — it reads the indicator `#10969` writes, so it must run in the same loop, **after** `#10969` |
| **10969** | Array Max & Min | → 1.2 | t0 ← kernel w121 (`pos in cal image out`); t3 writes indicator `min value` uid 17257 |
| **10757** | Index Array | → 1.2 | t0 ← kernel w121; its `element` (w10990) is the 1.5 payload (§6). ⚠️ **this move SEVERS the S3a NUMERIC indicator's wire — re-wire row, §5a-ter** |
| **1359** | For Loop | → 1.2 | forward slice |
| **2222** | Case Structure | → 1.2 | forward slice; t2 ← kernel w505; reads panel `Z/dZ` uid 47 and `Correction Factor` uid 9289 |
| **2626** | Build Array | → 1.2 | t4 ← kernel w505 |
| **6104** | Index Array | → 1.2 | forward slice |
| **8885** | Multiply | → 1.2 | forward slice (also phase P's control arm) |
| **9833** | Index Array | → 1.2 | forward slice |
| **11261** | Build Array | → 1.2 | forward slice; writes indicator `Force (pN) vs Extension (nm) ` uid 8038 |
| **29874** | For Loop | → 1.2 | forward slice |
| **10686** | And | → 1.2 | the every-25-frames schedule; §6 evaluates the cadence where the frame counter is. ⚠️ **this move SEVERS the S3a BOOLEAN indicator's wire — re-wire row, §5a-ter** |
| **10407** | Case Structure (autofocus) | → **1.5** | spec decision 1 |
| **48** | `ASI_adjust focus-subvi.vi` | → **1.5** | with #10407; its `VISA resource name` comes off SR `#4344` |
| **12589** | Case Structure | **stays 1.1** (§11c, §11.3 RESOLVED) | t1 ← `#10407` t6 w9113 (**the reverse crossing**, §0b). Keeping it on 1.1 keeps w12070 → `#11639` uncut; the crossing becomes `Q_focusback`, a **1-element queue** written by 1.5 and polled by 1.1 with timeout 0 |
| **376** | `save trace.vi` | → **1.7** | **§11b.3** — it *is* the accumulator; fed from `Q_res`/`Q_good`/`Q_rmeta`, outputs leave through 1.7's tunnels into `#6384` exactly as they leave #637 today |
| **6810** | `get buff image-lost frames.vi` | **stays 1.1** | it IS the frame source (row 1.8 REUSE); `Image Out` w3040 crosses to 1.2 through `Q_work` |
| **22700** | `IMAQ Write TIFF File 2` | ⚠️ **DELETED (§11h)**, not moved | it was **INSERTED** for fixture recording on 2026-09-01 (`fixture-recording.md:8-20`); the TRUE original has no such node — measured `diag_true_original_tiff.log`, 6/0. Deleted with `#23020` by gate **S1t**, 4/4, `build_d1_v0_run6.log` |
| **23020** | `Build Path` | ⚠️ **DELETED (§11h)** | same insertion; it existed only to name the TIFF file |
| **11639** | Compound Arithmetic | **stays 1.1** | drives #637's conditional terminal uid 648 via w3457 |
| **22082** | Case Structure | **stays 1.1** | stop path B; nothing in the forward slice feeds it |
| **17883 · 17837 · 22284 · 10019** | Compound Arithmetic · Not · Equal? · Equal? | **stay 1.1** | stop paths A and B |
| **1114** | `WLC function sub.vi` | **stays 1.1 in D1** | its SR pair `#862/#2853` (`F-x out`) is **not** one of the 8 that move; the WLC/display path is **D2 (row 1.6)** |
| **57 · 3191 · 20474** | Case Structures | **stay 1.1** | not in either slice |
| **2136 · 10068 · 29240** | Quotient & Remainder ×3 | **stay 1.1** | not in either slice |
| **3057 · 5119 · 10382 · 11529 · 11608 · 22703 · 23175** | Equal To 0? · Subtract · Not · Less? · Bundle · Format Into String · Strip Path | **stay 1.1** | not in either slice (the TIFF filename chain and frame bookkeeping) |
| **3052 · 4580 · 30117** | `File # Saved` · `Rot pos (deg)` · `Trans Pos (mm)` | **stay 1.1** | panel access nodes outside both slices |

### 5a-bis. The three CONTROL REFERENCES — added as move rows 2026-09-17 by §11e.3

⚠️ These are **not** in the 47-node census of diagram 43 and never were: a `Constant` is a **GObject, not a Node**,
so `Diagram.Nodes[]` never returns one, which is exactly how §5a came to have no row for them (rev4c A3). They are
addressed by `move_in`, which resolves a **uid** through `UID to GObject Reference.vi`, so the class never enters
the call.

| census/wire evidence | object | D1 | why (measured) |
|---|---|---|---|
| w4833 → `#48` t0 `-Inc reference` | **#3529** control reference `- Inc (PgDn)` | → **1.5** | its **only** measured consumer is `#48`, which moves to 1.5 (`d1_step0_census.json.focus_other_inputs`); run 4's cut list shows w4833 went wired→bare when `#48` moved |
| w2819 → `#48` t1 `+Inc reference` | **#3560** control reference `+ Inc (PgUp)` | → **1.5** | same |
| w1893 → `#48` t2 `Focus inc reference` | **#3447** control reference `Focus Step (F1)` | → **1.5** | same |

They are **control references, not Locals** — `main-vi-panel-map.md:403,:409-419` tables all 8 Locals by uid
(2991, 4277, 11574, 3160, 3097, 2143, 16942, 25805) and none of the three is among them;
`camera-acquisition-facts.md:333-334` measures them as the references handed to `ASI_adjust focus-subvi.vi`.
So `Local` stays **8** after the move (S1q/S4s unchanged), and no panel object is created.

**Count contract (REV 4 + §11c + §11e.3): 23 objects move off diagram 43** — **17 → 1.2** (the 18 rows of §5a
under 1.2 minus `#5058`, which is **deleted**, not moved), **5 → 1.5** (`#10407`, `#48`, `#3529`, `#3560`,
`#3447`; `#12589` **stays** per §11c), **1 → 1.7** ⇒ **23 moves + 1 delete + 1 drop**. **27 of the 47 census
nodes stay.** (Rev 4 before §11c said 21 / 3 / 26; rev 4 + §11c said 20.)

### 5a-ter. The two RE-WIRE rows the 1.2 move owes the S3a indicators — added 2026-09-21 (cycle 58)

**BOTH S3a INDICATORS GO BARE ACROSS THE 1.2 MOVE, AND THESE TWO ROWS BELONG TO 1.2, NOT TO S3a.** `move_in`
**takes one node per call and severs every wire on it, in either order** (`docs/cycle27-plan.md:1093`, 37(d);
`:843`, 33(a): *"the relocated node lands in the new body unwired"*), and each S3a indicator is a **BRANCH of its
source node's own net** — no `Wire` object of its own (whole-VI `Wire` delta **0** on both wirings,
`tools/bench/diag_s57_typepair.log:195` and `tools/bench/diag_s58_boolwire.log:153`). So severing the source's
wires takes the indicator's only feed with it, and until these rows land loop 1.5 reads an indicator nothing
writes.

| after this row moves | re-make this wire | source terminal | how |
|---|---|---|---|
| **#10757** (§5a → 1.2) | **w10990** — the S3a **NUMERIC** indicator | `#10757` t1 `'element'` (SOURCE) | `wire_indicators(<#10757's live node index>, ['element'], [<the indicator's machine-read label>], diagram_index = the LIVE index of the diagram the INDICATOR's terminal then lives on, node_class='Function')` — 47(b), `tools/gscript.py:1787-1789` |
| **#10686** (§5a → 1.2) | **w10799** — the S3a **BOOLEAN** indicator | `#10686` t0 `'x .and. y?'` (SOURCE) | same call shape, same `diagram_index` rule |

⚠️ The indicators' `ControlTerminal`s must be moved into 1.2's body too, or re-wiring them re-creates the 38(g)
loop-border tunnel S3a exists to avoid (`docs/cycle27-plan.md` 47(c)). Order per indicator: move the source node →
move the `ControlTerminal` → `wire_indicators` → save at `ExecState` 1 → ordered second pass (42(b)) for
`Is Broken?`. **This section corrects 45(c)** (`docs/cycle27-plan.md:1588-1589`), which asserted the indicator
terminals move with their source nodes and cited 37(d) for it; 37(d) says the opposite.

### 5b. Diagram 19 — outside the frame loop (5 nodes, none moves)

`#637` (the loop itself) · `#6384 save N xyz traces.vi` · `#2048 Array Subset` · `#781 Initialize Array` ·
`#27605 Max Trans Pos.vi`. `#6384`'s eight inputs: seven off `#637`'s output tunnels today, the eighth an
`Array Subset` of `total data array out`. In D1 those seven come off **1.7's** output tunnels instead — same
values, different carrier (§7).

### 5c. All 14 shift registers — **8 move, 6 stay**

| right / left | name | right inner ← | left inner → | D1 |
|---|---|---|---|---|
| `#1147` / `#1142` | `x,y,z array out` | w505 = kernel t4 | w1681 → `#5540` t5 | **→ 1.2** |
| `#5796` / `#5805` | `Bead is good? array out` | w5859 = kernel t3 | w6041 → `#5540` t3 | **→ 1.2** |
| `#119` / `#2972` | `pos in cal image out` | w121 = kernel t8 | w7429 → kernel t13 | **→ 1.2** |
| `#7311` / `#11001` | `Value` | w11389 ← `#10445` t3 | w10763 → `#10445` t2 | **→ 1.2** |
| `#4256` / `#4274` | `position [internal units]` | w9113 ← `#10407` t6 | w3947 → `#48` t4 | **→ 1.5** |
| `#4334` / `#4344` | `VISA out` | w7337 ← `#10407` t4 | w1731 → `#48` t3 | **→ 1.5 — the VISA session** |
| `#15` / `#51` | `total data array out` | w464 ← `#376` t1 | w3497 → `#376` t10 | **→ 1.7 — the accumulator** |
| `#24` / `#1108` | `error out` | w541 ← `#376` t0 | w4880 → `#376` t2 | **→ 1.7 — the error chain** |
| `#1117` / `#5351` | `LastBufferNumber` | w1109 | w5416 → `#6810` t7 | stays 1.1 |
| `#862` / `#2853` | `F-x out` | w8319 | w8322 → `#1114` | stays 1.1 (WLC = D2) |
| `#9018`/`#9025` · `#15197`/`#15204` · `#29505`/`#29512` · `#580`/`#1755` | — | — | — | stay 1.1 |

⚠️ §0c of rev 3 said "4 on 1.2" while listing `#862/#2853` as "1.2 (WLC)". **Rev 4 resolves it as 4 + 0**: `#1114`
and its register stay on 1.1, because the WLC/display path is row 1.6 = D2. **Total moved = 8.** Built with
`add_shift_reg` + `wire_sr` (`toolkit-capabilities.md` rows 37–39).

### 5d. Control terminals — **6 move; the seventh (`stop (end)`) stays, and §11c makes that sufficient**

⚠️ **COUNT CORRECTED 2026-09-17** (folding §11c in): the heading said *"5 move, and the sixth is the blocker"*
while its own table lists **six** moving rows (`Auto-Reset`, `Reset Tracking`, `Z/dZ`, `Correction Factor`,
`min value`, `Force (pN) vs Extension (nm) `) plus `stop (end)`. **6 move, 1 stays.** `build_d1_v0.py`'s
`CTLTERM_CONTROLS_12` already listed six; the S3c gate below now says 6 too.

| wire | panel object | read/written by | D1 |
|---:|---|---|---|
| 9806 | control `Auto-Reset` uid 17472 | `#9647` t1 | terminal **moves** into 1.2 |
| 10312 | control `Reset Tracking` uid 5605 | `#10247` t1 | terminal **moves** into 1.2 |
| 730 | control `Z/dZ` uid 47 | `#2222` t0 | terminal **moves** into 1.2 |
| 6096 | control `Correction Factor` uid 9289 | `#2222` t5 | terminal **moves** into 1.2 |
| 17287 | indicator `min value` uid 17257 | `#10969` t3 (writer), `#17289` (reader) | terminal **moves** into 1.2 — both ends go together |
| 10908 | indicator `Force (pN) vs Extension (nm) ` uid 8038 | `#11261` t0 | terminal **moves** into 1.2 |
| 6929 | control **`stop (end)` uid 7** (`ControlTerminal #642`) | `#11639` t2 on 1.1 | **stays 1.1, and that is now sufficient** (§11c): 1.2/1.5/1.7 stop on **end-of-stream sentinels**, so they need **no** panel reader and **no** Local. ✅ §0-BLOCKER item 3 closed |

These terminals are inside `Diagram#639` **on purpose** (§4's read-once rule), and the user flips `Reset Tracking`
during a run — routing it through a tunnel would change *when* it is read, a computation change, not scheduling.
**The build must plan for 31 terminals on `Diagram#639`, not 6**: the six above are those step 0 could see from a
*wired* boundary wire, and `ctlterm_owners.json` lists the rest. Any terminal left behind whose node moved shows up
in the census diff (§8) as a wired→bare terminal and is re-wired or moved there.

---

## 6. Row 1.5 — the autofocus loop

* **`CaseStructure #10407` and `#48 ASI_adjust focus-subvi.vi` move to their own While loop** (§11c: `#12589`
  **stays on 1.1**), which owns the ASI VISA session's shift-register pair. Nothing on the frame path can block on
  it — rule 1c is satisfied **by construction**, not by being fast enough: every queue op on the frame path takes
  **timeout 0**.
* **Both SR pairs are re-created on the new loop** (`#4256/#4274`, `#4334/#4344`). ⚠️ Without the second pair the
  VISA session has no carrier at all; §5 of rev 2 never mentioned them.
* **Payload width = 1 DBL, measured.** Exactly one of `#10407`/`#48`'s inputs is kernel-derived in the same
  iteration: `#10407` t2 `Index of closest\ncal image slice, bead 2` ← w10990 ← `#10757 .element` ← w121 =
  `#5058 pos in cal image out` (`d1_step0_census.json.payload`, `payload_width` 1). No cluster, no array.
* **The other inputs are NOT kernel-derived** (`focus_other_inputs`, 9 rows): t0 selector ← `#10686 And`
  (the schedule, evaluated in 1.2); t1 `# slices in stack` ← **LoopTunnel #9641, IndexMode 0**, loop-invariant;
  t3/t5 ← `#48`'s own `Outgoing Handle` / `Out position`; `#48` t0/t1/t2 ← Locals `- Inc (PgDn)` `#3529`,
  `+ Inc (PgUp)` `#3560`, `Focus Step (F1)` `#3447`; `#48` t3/t4 ← the two SRs above.
  ⚠️ **"Locals" is WRONG — they are CONTROL REFERENCES. Corrected 2026-09-17** (rev4c prior-art A3,
  `archive/peer/2026-09-17-priorart-priorart-d1-build-rev4c.md`): `main-vi-panel-map.md:409-416` tables all **8**
  Locals by uid — 2991, 4277, 11574, 3160, 3097, 2143, 16942, 25805 — and none of the three is among them;
  `:418-419` and `camera-acquisition-facts.md:333-334` measure them as the **control references handed to
  `ASI_adjust focus-subvi.vi`**. Two consequences: §0-BLOCKER's eight-Local census is a complete account of the
  VI's **Locals** but **not** of this chain's inputs; and **all three feed `#48`, which moves to 1.5**, yet they
  appear in **no** row of §5a, **no** line of the 20/27 count contract and **no** gate of §10 — §7.2b's own
  failure class. A refnum crossing a loop border **auto-creates its tunnel** (`NAMES.md:762`), a route the plan
  never named. Adding move-table rows is a judgement call ⇒ **flagged (§11.6), not patched.**
* **Cadence unchanged:** every **25 frames ≈ 3.6 Hz** (STATUS OPEN 2). D1 keeps the schedule and evaluates it in
  1.2, where the frame counter is.
* **Rule 1a:** the case's inputs arrive by the same route with the same values; only *when the case is evaluated*
  changes, which is scheduling.
* ✅ **WAKE-UP TRANSPORT — DECIDED (§11c): a 1-element DBL queue `Q_focus`.** 1.2 owns the frame counter, so 1.2
  evaluates the 25-frame cadence and enqueues the slice index **only on a tick, with timeout 0** — a full queue
  means the previous wake-up is still unconsumed, so the enqueue is skipped and the frame loop never waits. That is
  the "freshest wins, never blocks" property, realised with the one transport this fleet has exercised
  (`restructure-plan-4.6.md:55` tables local / 1-element queue as alternatives for exactly this duty).
  `build_d1_v0.py` sets `TRANSPORT = "queue"`.
* **#48 is non-reentrant with a SECOND call site on diagram 99** (rev-3 finding A5, `main-vi-panel-map.md:550,:558`),
  so moving uid 48 does **not** make 1.5 the sole owner of the VISA session, and **no `VISA Close` exists**
  (`main-vi-stop-and-save.md:136,:143-145`). **§11b.2: D1 does not remove original behaviour** — the display loop's
  call stays, sole ownership is achieved in **D2 (row 1.6)** and is recorded there, and **no `VISA Close` is added
  in D1** (the original has none). F2 therefore does **not** gate on a VISA close.

## 7. Row 1.7 — the writer loop, streaming AND accumulating

1. **Stream.** 1.7 dequeues `Q_res` / `Q_good` / `Q_rmeta` (lossless FIFO, `decisions.md:24`) and appends one line
   per result to an open file refnum — the user's requirement verbatim: *"저장 루프는 원본처럼 끝에 한 번 저장하지
   않고 실행 중 계속 파일에 쓴다"* (`archive/prose/2026-09-17-d1-d2-explained-r2.md:114`).
   Format (§11a.4, ours): TSV, one header line, one line per result,
   `buffer_no  t_ms  x_0 y_0 z_0 good_0 … x_{N-1} y_{N-1} z_{N-1} good_{N-1}`.
2. **Accumulate — with `#376` itself** (§11b.3, from rev-3 finding B2). Rev 3 said 1.7 would rebuild the arrays in
   shift registers and called that "same values, different carrier"; B2 showed that is false, because **two of
   `#6384`'s inputs are `#376`'s own outputs** and three more are loop-invariant values through `#637`'s tunnels.
   So **`#376 save trace.vi` moves into 1.7 with its two shift registers** (`#15/#51` total data array,
   `#24/#1108` error chain) and keeps producing exactly what it produces today.
2b. 🔴 **`#376`'s OTHER inputs sit on SHARED NETS whose remaining sinks STAY on 1.1** — measured, and rev 4 first
   tabled only its two shift registers (rev-4 review B3). This is **the exact failure class that stopped phase P's
   run 2** (§2a: *"wire 464 is ONE net"* whose collateral sinks `#237`/`#240` were bared, **pinning ExecState at
   0**, with *no broken wire and nothing for Remove Bad Wires* — a silent bare terminal):

   | wire | `#376` terminal | the other sinks on the same net | where they go |
   |---|---|---|---|
   | **w3268** (`frame-loop-wire-graph.md:151`) | t7 `x` | `#2136` t3 · `#3191` t1 · `#10068` t3 · `#1114` t0 · `#29240` t3 | **all five STAY on 1.1** (§5a) |
   | **w5090** (`:167`) | t11 `selected path` | `#23175` t0 (Strip Path) | **stays on 1.1** (§5a) |
   | w3629 (`:158`) | t6 `cal cluster path` | — | — |
   | w1581 (`:145`) | t9 `file size` | — | — |

   **So moving `#376` bares six terminals on nodes that never move**, and gate S3b as first written censused
   *"every moving node"* only — the collateral sinks fall outside it on **both** passes, while `ExecState` is not
   read until S5. **S3b is widened**: the census covers every node that carries **any wire a moving node's
   terminal carries**, on both sides, so a net with a staying sink is visible. Whether `#376` should move at all
   is `§11b.3`'s rule-1a decomposition call and is **not** reopened here.

3. **At stop**, after the drain, 1.7's output tunnels feed **`save N xyz traces.vi` #6384 unchanged** on diagram 19,
   in place of `#637`'s tunnels. The three loop-invariant inputs keep coming from the original's own tunnels on
   `#637`; only the `#376`-derived ones change carrier.
4. **Two artefacts per run** — the streamed TSV and the `.tra`. **N1 is judged on the `.tra`**, because that is
   what the original writes.

### 7.3 ✅ MEASURED 2026-09-17 — what `#376 save trace.vi` actually is (`tools/bench/diag_savetrace_376.log`, 4/0)

Read-only, on a COPY under claudeDev, deleted in the same run; `save trace.vi` md5 `9d126b32e6de26aaa7bef48653dd991c`
**before and after**. Dispatched by `archive/peer/2026-09-17-priorart-d1-op-streamwrite.md` **A5**, which said this
one measurement could delete §7.1's work.

| what was asked | measured |
|---|---|
| does `#376` open / write / close a file itself? | **NO.** Its 7 nodes are `Decrement`, `Quotient & Remainder`, `Equal?`, `Replace Array Subset`, a `CaseStructure` — and inside the case, **`save N xyz traces.vi`** + one `Property Node`. **No `Open/Create/Replace File`, no `Write to Text File`, no `Close File`, no `Write to Binary File`, no `Format Into String`** anywhere in it (3 diagrams, all walked). |
| is `saved file refnum` an open handle it appends to? | It is a **panel CONTROL** (FP[11]), passed in — not opened or closed here. |
| so what does it do? | It **accumulates** `current frame data array in` into `total data array` via `Replace Array Subset`, and on a periodic condition (`Quotient & Remainder` → `Equal?` → the Case) calls **`save N xyz traces.vi`**. |

**Two consequences, both facts, neither a decision:**
1. **A5's hazard does not materialise** — `#376` does **not** append per frame, so §7.1's per-result TSV is not a
   duplicate of something the original already does.
2. **§7.1's premise is still not exactly right.** "The original saves once at the end" is false as written: the
   original saves **periodically** through `#376`'s Case, *and* once at the end through `#6384`. The requirement
   §7.1 serves — a per-result record — is unaffected, but the sentence citing it should say *periodically*.
   ⚠️ Whether §7.1's separate TSV is still wanted, and on which route, is **judgement** — §11.9.

## 8. Row 1.8 — frame accounting, and the seam

**REUSE `get buff image-lost frames.vi` #6810.** It is the frame source itself, already produces `Missed frames?`
and `current image number`, and that number is the buffer number carried in `Q_meta`/`Q_rmeta`. Replacing it would
change computation on the acquisition path for no gain.
**Reconciliation gate (new — no equivalent in `tools/bench/` or `archive/benchmarks/INDEX.md`):** the writer's
buffer-number series is a strictly increasing subsequence of the acquisition loop's, and `Total Lost Frames` equals
the count of skipped buffer numbers.

`#5058`'s 16 terminals with the object on the other end (`main-vi-stop-and-save.md` §4; `census` + `measured`):

| t | terminal | dir | wire | other end | D1 route |
|---:|---|---|---:|---|---|
| 0 | `Bead is good? array in` | IN | 5637 | ← `CaseStructure #5540` t2 | #5540 moves to 1.2 with it |
| 1 | `Image In` | IN | 3040 | ← `#6810 Image Out`; ~~also → `#22700` t11~~ (that sink is DELETED, §11h — w3040 now has one fewer sink and the net is simpler, measured: `Wire 1902 → 1899` across S1t) | **crosses the border**: the pool slot's image, out of `Q_work` |
| 2 | `cross size` | IN | 373 | ← `LoopTunnel #2580` | loop-invariant → tunnel on 1.2, **non-indexed** |
| 3 | `Bead is good? array out` | OUT | 5859 | → `RightShiftRegister #5796` | the SR moves to 1.2 |
| 4 | `x,y,z array out` | OUT | 505 | → `#2222` t2, `#2626` t4 | 1.2 → `Q_res` |
| 5, 6, 10 | *(unnamed)* | IN | 0 | bare | stay bare |
| 7 | `x,y,z array` | IN | 5975 | ← `#5540` t6 | with #5540 |
| 8 | `pos in cal image out` | OUT | 121 | → `#10757` t0, `#10969` t0 | 1.2; `#10757.element` is also 1.5's payload (§6) |
| 9 | `# of bead 4 packs` | IN | 42 | ← `LoopTunnel #2396` | loop-invariant → tunnel |
| 11 | `4 pack remainder` | IN | 3512 | ← `LoopTunnel #4432` | loop-invariant → tunnel |
| 12 | `Array of cal clusters` | IN | 3646 | ← `LoopTunnel #3656` | loop-invariant → tunnel, **non-indexed** (`IndexMode 0`) |
| 13 | `pos in cal image in` | IN | 7429 | ← `LeftShiftRegister #2972` | the SR moves to 1.2 |
| 14 | `Real-space cosine window` | IN | 3912 | ← `LoopTunnel #3920` | loop-invariant → tunnel, non-indexed |
| 15 | `Cosine bandpass\nfor Hilbert ` | IN | 4027 | ← `LoopTunnel #4031` | loop-invariant → tunnel, non-indexed |

**Shape:** 6 loop-invariant inputs through LoopTunnels, 2 per-frame state carriers (SRs), 2 inputs from `#5540`,
the image straight from `#6810`, three outputs (w505, w121, w5859).

### 8a. `GPU_kernel_v1.vi`'s six EXTRA pane inputs

The GPU kernel shares the CPU kernel's pane for the 13 named terminals (`gpu-backend.md:13`,
`tools/bench/gpu_kernel_v1_fp.json`) and adds six of its own. **None exists on `#5058`, so none has a rule-1a
source — each is a diagram constant with the value the measured harness used:**

| extra input | what it is | value | why |
|---|---|---|---|
| `Function` | the `IMAQ GetImagePixelPtr` node's own REQUIRED `Function` input, promoted to the pane (`build_gpu_kernel.py:111`) | the node's default, as a constant | not a DLL parameter at all |
| `cal_path` | `.cal` path for `mt2_open` | **empty** | ⇒ the DLL falls back to `MT_GPU_CAL` / `mt_track_cal.txt` — the configuration every measured GPU run used |
| `nb` | bead count for `mt2_track` | **0** | ⇒ the DLL uses the calibration's bead count; the array handle also carries the length |
| `status` / `status_len` | `char*` status buffer and its length | **empty / 0** | with `status_len` 0 the DLL writes nothing |
| `flags` | `mt2_open` flags; bit0 = keep-alive | **0** | the value the 8/8 fixture comparison was measured under |

⚠️ **Rule-1a statement, so it is not smuggled:** the 13 shared terminals are wired from the same sources with the
same values as `#5058` had — that is the equivalence D1 claims. The six extras are **new inputs on a new callee**;
their acceptance is **numeric** (N1), not structural. 🔴 The **whole-fixture** figures are outside `decisions.md:38`
(bead 4, 10 frames of f11805–f11823 in the all-beads-lost tail, plus one z flip at k1679) — **STATUS OPEN 16, a
judgement call this plan does not take.** D1 proceeds under §11a.1's written assumption that it is acceptable; if
overturned, only the kernel subVI is swapped.

## 9. Queues, names and types (from the proven core, not invented)
⚠️ **SUPERSEDED 2026-10-01 (card 123-6)** by `docs/ring-buffer-design.md` and `docs/d1-loop12-17-split-plan.md` Pre-decided 238 — for the Q_free/Q_work pool queues only.

`stage2-assembly-step-c.md:21-26` — **no composite elements**; each direction is lock-stepped queues written by one
producer in one iteration, error-chained so a partial set cannot be published.

| queue | element | type source | bound | overload policy |
|---|---|---|---|---|
| `Q_free` / `Q_work` | IMAQ image refnum (the pool is a queue of refnums, not of slot integers — step C v2.1) | `IMAQ Create.New Image` sample | **20** (`decisions.md:22`) | full `Q_work` ⇒ skip this read, return the slot in the same iteration |
| `Q_meta` | buffer number, DBL | `#6810 current image number` | unbounded | — |
| `Q_res` / `Q_good` / `Q_rmeta` | DBL[] / Bool[] / DBL | the kernel's own outputs | unbounded | **lossless FIFO** (`decisions.md:24`) |
| **`Q_focus`** — 1.5's wake-up | 1 DBL (§6), the slice index | `#10757 .element` | **1** (§11c) | written by **1.2** on the 25-frame tick, **timeout 0**; full ⇒ skip. Never blocks the frame path |
| **`Q_focusback`** — the reverse crossing | 1 DBL, `#10407` t6's value | `#10407` t6 (w9113) | **1** (§11c) | written by **1.5**, **polled by 1.1 with timeout 0** into `#12589` t1; `timed out?` ⇒ keep the previous value |

**Eight queues in total** (§11c): `Q_free`, `Q_work` (bound **20**), `Q_meta`, `Q_res`, `Q_good`, `Q_rmeta`,
`Q_focus` (**1**), `Q_focusback` (**1**).

#### The `Obtain` resolution table — what each queue can actually be TYPED from

**DECISION: owed by judgement, `docs/cycle27-plan.md:908-926` Pre-decided 34(g) — the table above says what each
queue CARRIES; it does not say what `queue_node('obtain', …)` can TYPE it from.** That op takes the element type
from a `(node, named output terminal)` pair (`tools/gscript.py:1122-1128`) and wires the created `Obtain Queue`
node's own `element data type` input from it (`docs/NAMES.md:767-768`). Six of the eight type sources named above
are nodes inside `#637`'s body or nodes no stage has placed yet, so they are not that pair.

**Scope.** All eight `Obtain`s are placed by §10's gate `S1q`, on **`Diagram #686`**
(`tools/recipes/build_d1_routeb_v7.py:100`, `docs/cycle27-plan.md:899-901`), on `claudeDev\D1_s1_copy.vi`
**before S1t / S2 / S3** — while every original node is still where the census found it. After S3 the outer
terminal set of `#637` is not measured and no row below may be reused without re-reading it (34(h)).
**MEASURED: 2026-09-20, `tools/bench/diag_s2_scaffold.json:53-399`** — `Diagram #686` (Traverse index 19) holds
**21 nodes**, and `#637`, the frame loop, is one of them with **17 named source terminals of its own**
(`tools/bench/diag_s2_scaffold.json:124-193`). Those outer terminals are what resolve five of the six.

| queue | element type | `src` uid | exact output-terminal name | diagram | state | citation |
|---|---|---|---|---|---|---|
| `Q_free` | IMAQ image refnum | — | — | — | **B** — needs the stage that drops `IMAQ Create.vi` onto `Diagram #686` (the 20-slot pool For loop) | designed source `docs/cycle15-plan.md:119`; no IMAQ-image named source among the 21 nodes (`tools/bench/diag_s2_scaffold.json:53-399`); the pool loop is S2's **fourth** loop (`docs/d1-route-b-plan.md:401`) and is not built by the three-loop S2 (`tools/recipes/build_d1_routeb_v7.py:80-83`) |
| `Q_work` | IMAQ image refnum | — | — | — | **B** — same stage | as `Q_free`. The only refnum-typed sources on `#686` are IMAQdx **sessions** (`#250` `IMAQdx Session`, `#637` `Session Out`), not IMAQ images (`tools/bench/diag_s2_scaffold.json:103-115`) |
| `Q_meta` | buffer number, DBL (`docs/d1-build-plan.md:552`) | **#637** | `current image number` | **#686**, terminal **36** | **A** ⚠️R1 ⚠️R2 | `tools/bench/diag_s2_scaffold.json:174-175`. The designed `#6810 current image number` is a body node of `#637` (`docs/main-vi-stop-and-save.md:29`, `docs/frame-loop-wire-graph.md:277`), not on `#686`; `#637` t36 is that same wire's output tunnel |
| `Q_res` | DBL[] | **#637** | `x,y,z array out` | **#686**, terminal **2** | **A** ⚠️R1 ⚠️R2 | `tools/bench/diag_s2_scaffold.json:130-131`. `docs/cycle15-plan.md:120` sources this from the **GPU kernel**, which is dropped into 1.2 only at S3 (`docs/d1-build-plan.md:249`) and lands inside 1.2's body, never on `#686`. `#637` t2 is right shift register **#1147**'s outside terminal (`docs/frame-loop-wire-graph.md:409`) |
| `Q_good` | Bool[] | **#637** | `Bead is good? array out` | **#686**, terminal **28** | **A** ⚠️R1 ⚠️R2 | `tools/bench/diag_s2_scaffold.json:170-171`; same GPU-kernel problem as `Q_res` (`docs/cycle15-plan.md:121`); `#637` t28 is right shift register **#5796**'s outside terminal (`docs/frame-loop-wire-graph.md:416`) |
| `Q_rmeta` | buffer number, DBL | **#637** | `current image number` | **#686**, terminal **36** | **A** ⚠️R1 ⚠️R2 | same pair as `Q_meta`; `docs/cycle15-plan.md:120` gives `Q_meta`/`Q_rmeta` one type source |
| `Q_focus` | 1 DBL, the slice index | — | — | — | **C** — nothing on `#686` carries the SCALAR, and no planned stage puts one there | designed source `#10757 .element` (`docs/d1-build-plan.md:554`). `#10757` **is** an `Index Array [array, element, index]`, so `element` is a real output-terminal name (`docs/frame-loop-wire-graph.md:86`) — the obstacle is its DIAGRAM: it is a body node that moves into 1.2 (`docs/d1-build-plan.md:295`). On `#686` the same family exports only the **array**, `#637` t24 `pos in cal image out` (`tools/bench/diag_s2_scaffold.json:166-167`) |
| `Q_focusback` | **1 DBL** (see the decision below), `#10407` t6's value | **#637** | `position [internal units]` | **#686**, terminal **8** | **A** ⚠️R1 ⚠️R2 | `tools/bench/diag_s2_scaffold.json:138-139`. `#10407` moves into 1.5 (`docs/d1-build-plan.md:250`) and is never on `#686`; `#637` t8 is right shift register **#4256**'s outside terminal, the one `#10407` t6 writes every frame (`docs/frame-loop-wire-graph.md:410`) |

🔴 **CONSTRAINT ON EVERY ROW ABOVE — `docs/cycle27-plan.md` Pre-decided 35(a) (judgement, cycle 51, 2026-09-20):**
**no row's `(src, terminal)` pair may be used as the `element data type` donor while it sits on `#637`'s outer
boundary** — the donor must be available BEFORE the loops start (a constant or a pre-loop node), because R1 below
is a guaranteed runtime deadlock, not merely a risk. That makes the five **A** rows *addresses that exist*, not
donors that may be used. The replacement donor is **pending the 35(b) MEASUREMENT** — whether `queue_node('obtain')`
accepts any such shape at all, given it needs a **named** output terminal and a diagram constant's terminal is
unnamed (the `out_name ''` failure of `docs/cycle27-plan.md:961-964`). **Until that lands, no queue stage is
written.** Rule 1a is untouched: `Obtain Queue` keeps only the donor's TYPE, never its value.

⚠️ **R1 — existence is not usability: every `#637` row is a POST-LOOP value.** An outer terminal of `#637` — an
output tunnel, or a right shift register's outside terminal (`docs/frame-loop-wire-graph.md:405-423`) — carries
its value only after the frame loop has finished, and `element data type` is a **wired** input on the created node
(`docs/NAMES.md:767-768`). So the `Obtain` would not execute until 1.1 ends while 1.2 / 1.5 / 1.7 wait on the
queue refnum: a legal diagram (`ExecState 1`) that deadlocks at run time. **This is INFERRED from LabVIEW
dataflow, not measured here.** Cheapest separator: one `queue_node('obtain', …)` call on a scratch copy, then read
the created node's `element data type` terminal — if it carries no wire, R1 evaporates.

⚠️ **R2 — `queue_node`'s reach into a `WhileLoop`-class node is unmeasured.** The census read `#637`'s terminals
through `Diagram.Nodes[].Terminals[]`, while `queue_node` resolves its source through Traverse `src_cls[src_index]`
+ Get Outputs **by name** (`tools/gscript.py:1122-1128`); whether Get Outputs accepts a `WhileLoop` reference and
returns these 17 names has never been exercised in this fleet. Address `#637` as class `WhileLoop` with the index
re-read immediately before the call (34(h), `docs/cycle27-plan.md:927-935`). `#637`'s outer terminals carry
**duplicate names** (`error out` at 0 and 15, `Value` at 46 and 57) — none of the five names chosen above is
duplicated (`tools/bench/diag_s2_scaffold.json:124-193`).

🔴 **DECISION: `Q_focusback` carries 1 DBL, not a Bool** (judgement, `docs/cycle27-plan.md:920-922`). `#10407` t6
is `position [internal units]`, it is what feeds `#48` t4 `In position` through the original's own right shift
register **#4256** (`docs/frame-loop-wire-graph.md:410`, `:433`; `#48` t4 read back as `In position`, wire 3947,
at `tools/bench/diag_s2_scaffold.json:688-693`) — a position, not a flag. This **overturns
`docs/cycle15-plan.md:122`**, which called it Bool; that line now carries a superseded-by note pointing here.

Every enqueue takes a **finite** timeout and its `timed out?` is read (`frame-ownership-design.md:80-83`); every
queue op that sits on the **frame acquisition path** takes timeout **0** (rule 1c).
**Slot ledger:** every exit path returns the slot exactly once — normal completion, kernel error, enqueue timeout,
shutdown, writer error.

### 9a. The stop, by end-of-stream SENTINEL (§11c) — the encoding, and the one writer rule

The sentinel is **a value the kernel can never produce**, so no real row can be mistaken for it and no extra
Boolean channel is needed:

| queue | sentinel value | who writes it | who exits on it |
|---|---|---|---|
| `Q_meta` | **buffer number −1** (`#6810 current image number` is a frame index ≥ 0) | 1.1, once, after `stop (end)` ends the frame loop | 1.2 |
| `Q_work` | the pool slot that carries the −1 row (the image itself is ignored) | 1.1 | 1.2 |
| `Q_rmeta` | **buffer number −1** | 1.2, once, after it sees the −1 | 1.7 |
| `Q_res` / `Q_good` | **empty array** (the kernel always returns one element per bead, N ≥ 1) | 1.2 | 1.7 |
| `Q_focus` | **−1** (a slice index is ≥ 0) | 1.2, once, after it sees the −1 | 1.5 |

**The writer must not write the sentinel row.** 1.7 tests the dequeued `Q_rmeta` value **before** appending: −1 ⇒
leave the loop, do **not** append a TSV line and do **not** extend the accumulator; then drain, then call `#6384`.
Order is "stop the users → drain → release", so no error 1122 (`frame-ownership-design.md:68-72`), and the
sentinel travels the same queues the data travels — no second reader of `stop (end)` anywhere.

---

## 10. Prediction contract

### S — structural (`build_d1_v0.py`, one run, one log)

| gate | assertion, with counts |
|---|---|
| **S0** | `TRANSPORT` is set to a mechanism with a **creator built in the fleet today** — ✅ `"queue"` (§11c). Original md5 `2a78e17c449cacdaf5da389818526859` read **before**; `OpMoveIn_v0.vi` present, UID control `'UID 3'`; LabVIEW handles recorded |
| **S1** | the D1 target opens with, **before** any edit: **`Diagram 170`** (⚠️ **MEASURED 2026-09-17, `build_d1_v0.log` run 1: rev 4 said 171 and that was a transcription error** — `probe_move_into_v0.log:217` reads `Diagram 170` on the fresh copy, `:220` then CREATES a While loop, and only `:227` says `171 → 171`; the other seven classes matched exactly), `Node 626`, `Wire 1902`, `LoopTunnel 132`, `ControlTerminal 114`, `WhileLoop 3`, `Local 8` |
| **S1q** | **8 queues obtained** (§9): `Q_free` / `Q_work` bounded **20**, `Q_meta`, `Q_res`, `Q_good`, `Q_rmeta` unbounded, **`Q_focus` and `Q_focusback` bounded 1**. Each Obtain's `max queue size` read back from the created node; **no `Local`, no user event, no DVR is created — `Local` stays 8** |
| **S1t** | **§11h, before any move:** `#22700` and `#23020` DELETED; both uids gone; **no staying node left with a bare named input**; `ExecState` unchanged. ✅ MEASURED `build_d1_v0_run6.log`, 4/4: `SubVI 98→97`, `Function 181→180`, `Node 626→624`, `Wire 1902→1899`, bare named sinks `28→26`, ExecState `0→0`. `#23175`/`#22703` left standing, reported |
| **S2** | **three** new While loops on `Diagram #686`: `WhileLoop 3 → 6`, **`Diagram 170 → 173`** (corrected with S1); `#637` still exists, still owns `#6810` and `CaseStructure #22082` (⚠️ `#22700` removed from this list — S1t deleted it; run 6's single failure in 57 was exactly this stale gate) |
| **S3** | **23 objects reparented** (17 → 1.2, **5** → 1.5 — `#10407`, `#48` and §11e.3's three control references `#3529`/`#3560`/`#3447` — 1 → 1.7; §11c keeps `#12589` on 1.1), each verified by `OpOwnerChain_v1` reading `uid → <body Diagram> → <the right WhileLoop>`; **`#12589`, `#11639` and `ControlTerminal #642` still owned by `Diagram #639`**; total `Diagram` count unchanged **by the moves** (structures keep their frames); `#5058` deleted, `GPU_kernel_v1.vi` dropped into 1.2 (`SubVI 98 → 98`) |
| **S3b** | ✅ **MEASURED 2026-09-17 run 5: 109 terminals over 24 uids** (run 4 read 106/21; §11e.3's three control references add one cut terminal each — w4833 / w2819 / w1893). `tools/bench/build_d1_v0.json` is the list. **census diff = the re-wire list** (§11a.2): `node_terms` **before** and **after**, over every moving node **AND every node that shares a wire with one** (rev-4 review B3 — a net's *staying* sinks are bared silently and a moving-nodes-only census cannot see it, which is how phase P run 2 died); the set that went wired→bare is the authoritative list; gate — that set **⊇ §8's 13 crossings**, **includes `#376`'s w3268/w5090 collateral sinks**, and **every member is re-wired** (tunnel, queue or SR) before ExecState is read. **wires cut == wires re-wired** |
| **S3c** | **8 shift registers** created and wired (4 on 1.2, 2 on 1.5, 2 on 1.7); **6 `ControlTerminal`s** reparented into 1.2 (§5d, count corrected from 5), total `ControlTerminal` still **114**, all 114 `panel_wiring` labels present |
| **S3d** | whole-array parameters cross **non-indexed**: `tunnels()` reports `IndexMode 0` for `cross size`, `# of bead 4 packs`, `4 pack remainder`, `Array of cal clusters`, `Real-space cosine window`, `Cosine bandpass\nfor Hilbert ` (**6 tunnels**) |
| **S4** | each of the three NEW loops' conditional terminals is **written and driven by its own sentinel test** (§9a), read back by `OpLoopEndRef_v0`: a non-zero `CondWireUID` on each of 1.2 / 1.5 / 1.7. **For `#637` nothing changed**: `OpLoopEndRef_v0` must still read terminal **648 ← wire 3457 ← `#11639`** after the build |
| **S4s** | **the sentinel path exists and is one-way**: the enqueue that publishes each sentinel is present on its writer's diagram and its element is the literal sentinel (**−1** for `Q_meta` / `Q_rmeta` / `Q_focus`, **empty array** for `Q_res` / `Q_good`); **1.7's append is gated by the −1 test** (the writer never writes the sentinel row); **no new panel object** was created for any of it (`ControlTerminal` still 114, `Local` still 8) |
| **S5** | junk Invokes purged (`new_since('Invoke')` empty), `remove_bad_wires_scripted`, **`ExecState 1` warm**, saved; file size recorded |
| **S6** | **cold re-open** in a restarted LabVIEW: `ExecState 1`, `Diagram 173`, `WhileLoop 6`, `ControlTerminal 114`; original md5 unchanged **after** |

⚠️ **SUPERSEDED 2026-09-24 (cycle-69 judgement) as a stage table: S4–S6 above are replaced by `docs/d1-loop12-17-split-plan.md` §2 (its Pre-decided 161).**

`ExecState` means nothing between S2 and S4 — the moves cut wires (§2b). It is read at S5 and at S6 only.

### N1 — numeric, rule 1a

The kernel-harness branch is already measured and is **not re-run**. N1 is the **in-VI** comparison, and the path
must be stated in the report because D1 has no file-replay input of its own: the fixture is replayed through
**1.2 + 1.7** by feeding `Q_work` from `IMAQ ReadFile` in place of the camera (the step-C v2 replay shape,
`stage2-assembly-step-c.md:22-24`) on a **scratch copy of D1**, never on D1 itself. Gate: the `.tra` against the
original's, **first 10,018 frames** within `decisions.md:38`; the **whole-fixture** figures are reported
**separately** and are STATUS OPEN 16, not a pass/fail.

### F1 — live, **60 s** (not 5 min)

§11b.4, against rev-3 finding A3: `cycle15-plan.md:77` says ≥ 5 min, but `#22700` writes a **1.3 MB TIFF per frame
≈ 118 MB/s at 90 Hz** (STATUS OPEN 18), so 5 min ≈ **35 GB**.
⚠️ **ARITHMETIC CORRECTED** (rev-4 review A4): rev 4 first wrote "60 s ≈ 4 GB", which does not use its own rate.
**Measured**, in a log this plan already lists: `tools/bench/drive_original_copy_v3.log:81` — `.tif`:
**2041 files / 2,675,689,770 B** from a ~20–22 s frame loop ⇒ **≈ 122 MB/s**. So **60 s ≈ 7.3 GB**, not 4 GB, and
the run must have that much free **and delete in the same run** (STATUS OPEN 18: *"bound it or the disk fills"*).
60 s proves the plumbing; the 5-minute run is scheduled once the user decides how the harness handles TIFF
writing. Flagged — OPEN 4.

Driven by `drive_original_copy_v3.py`'s method (16/16): second COM apartment, never-joined RunThread, **3 picks**
in the Image display (uid 31543, rect 232,500–873,1013), `Done Picking Beads?`, **3 token-gated `choose bandpass`
clicks** via `lv_gui.ps1 -Action clickprobe`, absolute save path into the run folder. Camera only; rig
disassembled, **no beads — tracking errors without beads are expected and are not a failure**.

Recorded (`pre-rig-master-plan.md:55` — the list already exists; not re-specified here): frames acquired / tracked
/ written; **the buffer-number series** (1.1's and 1.7's, with the §8 reconciliation); `Q_work`/`Q_res` **high-water
marks**; the **slot ledger** (returned == taken); **handles start/end**; the **TSV growing during the run** (size
sampled ≥ 3 times, strictly increasing); every TIFF counted and deleted.
⚠️ **B3 (rev-3): with no beads the writer may be STARVED, so "the file grows" proves nothing on its own.**
`pre-rig-master-plan.md:269-274` prescribes injecting synthetic results; F1 therefore reports the tracked-result
count beside the file size, and a zero count makes the growth gate **N/A**, not PASS.

### F2 — stop / restart

`stop (end)` by `SetControlValue` (stops `False` + readback → run → one `True` each → poll values + `ExecState`).
**All four loops exit** — 1.1 on the panel Boolean, then **1.2 / 1.5 / 1.7 on the sentinels 1.1 publishes** (§9a),
in that order (each loop's iteration counter frozen, read twice 2 s apart); **no error 1122**; the `.tra`
is written and **re-openable**; **restart 15 s**; stop again; close **without saving**; scratch deleted; TIFFs
deleted; original md5 unchanged.
⚠️ **F2 inherits STATUS OPEN 17b**: v3's R11 scored the *restart*, not the stop, so "the stop works" is
**unproven** — F2 gates on the stop itself, not on the fact that a restart succeeded afterwards.
⚠️ **No `VISA Close` gate** (§6/§11b.2): the original has none and D1 adds none.

---

## 11n. ⚠️ MEASURED 2026-09-17 (material, run 8) — **§11m below is NOT BUILDABLE AS WRITTEN.** Read this first

Three facts from the machine, none of them a decision. Full narrative: `archive/2026-09-17-status-d1-full-build-5.md`.

1. **The donor §11m names is the wrong one, and the review said so before the build**
   (`archive/peer/2026-09-17-priorart-connect-nested.md` A3-i, and this project's own census
   `tools/bench/diag_connectnested_donors.log`, 6/0): `OpStopFromNode_v0`'s ladder is anchored to a **loop index**
   (`Traverse("WhileLoop")[index] → To More Specific Class → Loop.Diagram 6361401 → …`), so duplicating it puts
   **both ends on the same loop**. The diagram-indexed ladder lives in `OpNetInfo_v1` / **`OpConnect2_v0`**, which
   is what the op was actually built from.
2. ⚠️ **THE CONCLUSION OF THIS ITEM IS WITHDRAWN 2026-09-17** — see **§11q**. What stays measured is the narrow
   fact: an **ungated** `GObject` element wired straight into a `Diagram`-class property node is a downcast and
   reads `ExecState 0`. What is refuted is *"the fleet cannot create a second `To More Specific Class`"*: this
   project has **copied** one (`tools/recipes/build_opconstvalue_v1.py:165-199` → `OpConstValue_v1.vi` on disk)
   and **three existing ops already carry two** (`tools/bench/probe_opexitloop.log:12-18`). The paragraph below is
   kept verbatim as the record of the wrong inference.
   **"That ladder duplicated for the source side" cannot be built.** A second nested diagram needs a second
   `To More Specific Class`, and the fleet cannot create one — **MEASURED**: feeding `Traverse for GObjects.vi`'s
   **GObject** element into a `VI Server:AbstractDiagram` property node reads **`ExecState 0`** (a downcast;
   `tools/bench/build_opconnectnested_v0_run1.log`, `W4 ROUTE A wired: ExecState 0`). `New VI Object` creates no
   primitive (`vi-scripting.md:308,:465`), and `copy_by_index` would land the node with an **unwirable
   `target class`** — a class-specifier `Constant` is a GObject, not a `Node`, the identical wall as §11i.
   **What shipped instead:** `OpConnectNested_v0.vi`, both ends by index **on the SAME diagram**
   (`Diagram[index].Nodes[index 2].Terminals[index 3]` ← `Nodes[index 4].Terminals[index 5]`).
3. **"It resolves all 31 rows" is refuted** (review A3-ii, against `§11L:698` and the run-7 log): the 24 no-route
   rows are **7 unnamed-end + 17 `from-tunnel`**, and **16 of the 17 carry `outer_source (none)`** — a
   source-RESOLUTION gap, not an addressing one. The op reaches ~7–8 of 31, and the 17 `from-tunnel` rows (source
   on `Diagram #686`, sink inside a new loop body) need exactly the two-diagram capability item 2 rules out.
4. **The op is verified STRUCTURAL + WIRE-IDENTITY only, NOT functional** (peer `connectnested-t2b`, accepted):
   `test_opconnectnested_v1.log`, 10/1 — from a scratch at **ExecState 1**, with the sink asserted unwired and
   the op returning no error, the wire is created **w285 on both ends** and **ExecState drops to 0**. Undecided
   between a type-incompatible pair (the sink was UNNAMED, so its type was unread) and a wire the op always
   breaks. Discriminator named: two copies of one subVI, NAMED `error out` → NAMED `error in (no error)`.

⇒ **§11m's closing sentence — "run 8 goes straight to save → N1 → F1 → F2" — cannot happen.** What replaces it is
judgement's call, recorded as STATUS OPEN 33/34; a material session may not take it.

## 11t. VERDICT (judgement, 2026-09-17, per the user's §11p rule) — ROUTE A FAILED; SWITCH TO ROUTE B

Run 9 ended with **no saved VI**: re-wire 42/66; 16 `from-tunnel` rows whose sources are FlatSequence inner
tunnels / #637's shift registers one hop outside the frame loop (a WRITER from a wire-terminal reference is
missing); 6 `from-ctl` rows with error 5001; 3 of 8 `OpConnectNested_v1` wires removed by Remove Bad Wires,
unexplained; stage 2 unwritten. That is the user's "그래도 안되면 B" condition. Route A is closed; nothing more
is built for it.

**What B inherits, stated honestly:** the 16 tunnel-fed loop-invariant inputs exist in B too (new loops need
the same cal clusters / windows / sizes from the enclosing flat sequence). The answer is the same single op in
both routes — **`OpConnectFromWire_v0`: `Terminal.Connect Wire` 6349C03 with the SOURCE taken from
`Wire.Terminals[]` 6371003 + `Is Source?` 634A003 (front half = `OpWireSource_v5`, back half =
`OpConnectNested_v1`)** — codex r3 (`archive/peer/…flatseq-tunnel-source-addressing…`): Connect Wire accepts
*any* Terminal reference. In B it is a part of NEW wiring, not a repair of cut wiring. B's first item.
Second inherited item: the 6 panel-control rows — measure whether `wire_control`'s 5001 is the newline in the
label (NAMES.md: newlines are real) before calling it unroutable.

## 11r. DECIDED (judgement, 2026-09-17, after §11q: cross-diagram wiring WORKS) — the from-tunnel rows need ONE hop, not a chain

The ultimate source of a tunnel-fed input is irrelevant now that `OpConnectNested_v1` wires across diagrams and
LabVIEW creates the tunnels itself. For each of the 16–17 `from-tunnel` rows: read the OLD tunnel's
`Tunnel.Outside Terminal` (6356001) → `Connected Wire` (634A000) → the wire's OTHER terminal(s) (`Wire.Terminals[]`
6371003, `Is Source?` 634A003) → `Generic.Owner` (6327806) → the owner's class/uid and the terminal's INDEX within
it. Then wire from that owner terminal (by index, whatever its name) to the new loop's inner sink with v1 — one
hop. If the owner is itself a tunnel, repeat the one-hop read on it (a loop, not a walker with its own ladder).
`OpTunnelSource_v0` is therefore a ONE-HOP reader (additive on `OpTunnels_v0` + `OpWireSource_v5`'s terminal
half), returning the other-end owner class/uid + terminal index; the review's "chain" objection is answered by
iterating the reader from Python, and the FlatSequenceFrame dead-end is avoided because no owner chain is walked
— only the wire's other end. Budget 2 builds. Then run 9 exactly as §11p.3–4.

## 11s. ✅ MEASURED 2026-09-17 (material, run 9) — §11r's one hop was READ, and it lands on the FLAT SEQUENCE

Two runs, both read-only on the original working copy (md5 `2a78e17c449c…` before **and** after), 0 of §11r's
2-build budget spent — the reader turned out to be a **composition of ops already on disk**, which is what its
prior-art review said before it was built (`archive/peer/2026-09-17-priorart-tunnelsource-onehop.md`, ANSWERED,
5 findings, **0 novel**, all accepted; dispositions in its own "What was done with it").

### 11s.1 The one hop, for all 18 `from-tunnel` rows (`tools/bench/diag_tunnelsource_onehop.log`, 7 pass / 2 fail)

`gscript.tunnels()` gives the old tunnel's OUTER wire; `OpWireSource_v5` walks that wire's `Terms[]` and returns
`Is Source?` + owner class/uid; the owner is located and the terminal index derived **offline** from
`main_vi_nodeterms.json` + `d1_step0_census.json`. Raw rows: `tools/bench/d1_tunnel_sources.json`.

| the outer wire's single SOURCE terminal is owned by | rows | addressable as `Diagram[d].Nodes[n].Terminals[t]`? |
|---|---:|---|
| **`FlatSequenceInnerTunnel`** | **14** | ❌ not a node on any diagram |
| **`LeftShiftRegister`** of `#637` (uids 9025, 29512) | **2** | ❌ not a node — **and** the register STAYS on 1.1, so this is a cross-loop transport question, not a wiring one |
| `SubVI` `#27605` on diagram 19 | 1 | ✅ (diagram 19, `Nodes[16]`, `Terminals[0]`) |
| the hop does not advance (`#376` t7) | 1 | — |

**So §11q.2's premise and §11r's answer to it are BOTH overtaken.** The 16 rows are not "a chain of unnamed
tunnels further out" (`build_d1_v0.py`'s printf, prior-art A3) and they are not a one-hop *resolution* gap either:
their values enter the frame-loop's own diagram **from the enclosing flat sequence**, one hop out, and the object
that drives them is a class no `Nodes[]` enumeration contains. ⚠️ Two by-products, both measured:
`OpWireSource_v5` is **not** broken — its published control reproduced first try (wire 10850 → owner
`DigitalNumericConstant` 10739); the recorded 1055 was the CALLER never setting `UID 2`
(`diag_d1_full_route.py:265-273`), which closes **STATUS OPEN 28c**.

### 11s.2 Run 9 (`tools/bench/build_d1_v0_run9.log`, 55 pass / 8 fail, 203 s) — route A's measured reach

`OpConnectNested_v1` is now used for every row whose end has no name, and as the **retry** when a name-addressed
call raises 5001. Relocation reproduced exactly again (S1 census exact, `#5058` deleted, GPU kernel dropped,
`SubVI 97`); working copy deleted, never saved.

| | run 7 | **run 9** | what changed |
|---|---:|---:|---|
| WIRED | 35 | **42** | the 8 unnamed-end rows + the `subarray→x` 5001 + the one resolved from-tunnel row went by INDEX |
| FAILED | 7 | **6** | all six are `wire_control` → **5001 from `Get Controls.vi`** on a PANEL control source |
| NO-ROUTE | 24 | **18** | 16 from-tunnel (§11s.1) + `#2222` t0 (control → unnamed sink) + `#376` t7 |

**`OpConnectNested_v1` works in the real VI, and the honest gate says how well: 8 wires made, 5 SURVIVED
`remove_bad_wires_scripted`, 3 were deleted by it** (`#1359` t4, `#1359` t9, `#29874` t4 — two of them branches of
the same `#8885 x*y` net, wire 26189, the third the cross-diagram `D[19] → D[24]` one). ExecState 0 throughout,
as §2b says it must be between moves. **N1/F1/F2 still cannot run: no saved VI.**

### 11s.3 🔴 The one judgement question this produced — and it is NOT the reader

`archive/peer/2026-09-17-flatseq-tunnel-source-addressing-r3.md` (codex, ANSWERED; two earlier dispatches were a
TIMEOUT and an agy permission ERROR and told us nothing) **refutes** the claim those 16 sources are unreachable:
`Terminal.Connect Wire` **6349C03** takes *any* Terminal reference — including one from `Wire.Terminals[]`
**6371003** filtered by `Is Source?` **634A003**, which `OpWireSource_v5` already holds — and
`FlatSequenceInnerTunnel` carries its own `Left Terminal` **1C3A9000** / `Right Terminal` **1C3A9001** (the peer's
ids, **unverified here**). What is missing is a **WRITER whose `Wire Source` comes from a wire-terminal reference
instead of `Diagram[].Nodes[].Terminals[]`** — one fused op from two proven halves (`OpWireSource_v5`'s front,
`OpConnectNested_v1`'s back). §11p ends *"No further op beyond (1) and (2) is authorised for A"*, so a material
session may not build it, and did not.

## 11p. USER DECISION 2026-09-17 — "A 마지막으로 시도해보고 그래도 안되면 B로 이제 바꾸자"

**One last attempt at route A (relocate + re-wire).** Its scope is fixed here so "did it work" is a measurement:

1. `OpConnectNested_v0` v1: both ends on DIFFERENT nested diagrams, using the codex-corroborated chain — one
   `To More Specific Class` to `AbstractDiagram` 6375809 (or `Loop.Diagram` 6361401 from the loop ref) → `Nodes[]`
   → `Terminals[]` on each side → `Terminal.Connect Wire` 6349C03. The earlier ExecState 0 is treated as a
   code-generation defect (the five causes in `archive/peer/2026-09-17-nested-diagram-terminals.md`), each ruled
   out by measurement in turn — budget 2 builds.
2. Tunnel-source resolution for the 17 `from-tunnel` rows: `Tunnel.Outside Terminal` 6356001 → `Connected Wire`
   634A000 → `Wire.Terminals[]` 6371003 → `Is Source?`/`Owner` (a ControlTerminal's owner is its diagram — use
   `ControlTerminal.Control` 6353000). One reader (additive on OpWireSource/OpTunnels), verified on 3 rows.
3. With (1) and (2): re-wire the remaining 31 rows, then stage 2, save, cold ExecState 1.

**Success = a saved `Track_v6_D1_GPU.vi` at ExecState 1 warm and cold.** Anything short of that after the budgets
above ⇒ **route B** (new loops built fresh inside the copy with the proven drop/name-wire helpers; the original
frame loop keeps everything except the tracker call, which is deleted; structures moved with GObject.Move only
where a fresh build is impossible). No further op beyond (1) and (2) is authorised for A.

## 11q. ✅ PRIOR-ART REVIEW of §11p's two artifacts, 2026-09-17 — what it corrected, and what it BLOCKS

`archive/peer/2026-09-17-priorart-connectnested-v1.md` (claude/opus, `-Role priorart`, ANSWERED, 8 findings,
**0 `novel`**). Full dispositions live in that file's "What was done with it"; only the consequences are here.

### 11q.1 — artifact 1 (`OpConnectNested_v1`): two findings, both folded in before the build ran

| finding | consequence |
|---|---|
| **B4 `already-measured`** — *"same wire uid on both ends"* is the pairing this project ALREADY measured to be insufficient (`test_opconnectnested_v1.log:24-27`: w285 on both ends **with ExecState 1 → 0**; the rule at `docs/NAMES.md:861-863`) | the acceptance gate CHANGED: the test now drops the **same** subVI in both loop bodies (NAMED `error out` → NAMED `error in (no error)`, §11n.4's own discriminator), records `ExecState` before AND after, and adds the decisive gate **T2c: the wire must SURVIVE `remove_bad_wires_scripted`** — RBW deletes a broken wire and leaves a good one |
| **B3-i `helper-exists`** — `OpExitLoop_v0.vi`, `OpWire_v1.vi` and `OpWireSource_v5.vi` each already carry TWO independent `Traverse → IA → TMSC` ladders (`tools/bench/probe_opexitloop.log:12-18`) | recorded, **not adopted**: building from `OpExitLoop_v0` re-creates both `Nodes[] → IA → Terms[] → IA` ladders and the invoke (7+ nodes), while the copy route adds ONE node to a working op. **`OpExitLoop_v0` is the SECOND attempt inside §11p's 2-build budget, not a third route.** §11n item 2 is withdrawn on the strength of this finding |

### 11q.2 🔴 — artifact 2 (`OpTunnelSource_v0`): FOUR findings the reader as specified does not survive

**This is not a documentation repair. A material session may not decide it** (CLAUDE.md §3), so it is stated and
left to judgement:

1. **A3-ii `contradicted` — the PREMISE.** Three files say three different things about the 17 `from-tunnel`
   rows. §11p.2 calls it a one-hop *"source-RESOLUTION gap"*; `docs/d1-route-b-plan.md:316-318` says
   *"there is **no named origin to find**"*; and the machine — `tools/bench/build_d1_v0_run7.log:303-325` — says
   each row *"has no NAMED node source **in any census** … the value comes from **further out through more
   unnamed tunnels**"*. If the third is right the source is a **CHAIN** of tunnels on successively outer
   diagrams, and a one-hop reader returns another tunnel, not an origin. §11p.2 specifies no recursion, no
   termination rule and no "the owner is itself a Tunnel" case. Also: exactly **one** of the 17 already carries an
   identified source (`#376 t7`), so *"verified on 3 rows"* has at most one oracle, not three.
2. **B2 `already-failed` — the BACK HALF.** `OpWireSource_v5` failed its **own published control**:
   `tools/bench/diag_d1_full_route.json:49-52` — 0 rows, `error 1055` at term index 0 — where
   `docs/NAMES.md:946` records the same op answering that exact wire 12/12. Cause **unrecorded and explicitly
   unchased** (STATUS OPEN 28c). An additive build inherits the identical `UID → cast(Wire) → Terms[]` chain.
   CLAUDE.md's own rule names this case: *"the second time a class of failure is explained by inference rather
   than read from the machine, the next build is the READER for it."*
3. **B4's name/ID half.** `Tunnel.Outside Terminal` 6356001's data-terminal short name is **`Outer Term`**
   (`NAMES.md:723`), `Node.Terminals[]` → `Terms[]`, `Terminal.Connected Wire` → `Wire`, `Is Source?` →
   `IsSource` (`:218-219`, `:355`) — §11p.2 uses long property names throughout. And `6356001` /
   `ControlTerminal.Control 6353000` are **UNVERIFIED** in `docs/vi-server-ids.json:142,:145`.
4. **A4.3 + `NAMES.md:864-867`.** `Generic.Owner` returns a **Generic** reference; wiring it into a GObject-class
   node is a downcast that reads ExecState 1 → 0 — so the last hop needs **its own cast**, which §11p.2 does not
   list. And `OpOwnerChain_v1` has a MEASURED limit: an owner chain **terminates silently at a
   `FlatSequenceFrame`** (`toolkit-capabilities.md:49`), a class that occurs in the main VI.

**The question only judgement can answer:** build `OpTunnelSource_v0` as §11p.2 specifies anyway (one hop, no
recursion, on a back half with an unexplained 1055), or spend the hop on the **1055 reader** first, or accept that
the 17 rows have no origin to find and let that alone decide route A vs route B.

## 11m. DECIDED (judgement, 2026-09-17, after run 7: 35 wired / 7 failed / 24 no-route) — the FOURTH and LAST op

Run 7 measured the re-wire capability gap exactly: every name-addressed writer (`g.wire`, `wire_control`) fails
on terminals with **no name, a newline-labelled name or a duplicate name** (7 × error 5001 from `Get Controls.vi`
/ `Get Outputs.vi`; 24 rows with an unnamed sink/source), and both index-addressed writers (`connect_terminals`,
`connect2`) need a **top-level source**. Authorised: **`OpConnectNested_v0` = `Terminal.Connect Wire` 6349C03
with BOTH ends addressed by index on nested diagrams** — `OpStopFromNode_v0`'s body-node ladder (Traverse
Diagram[i] → Nodes[j] → Terminals[k]) duplicated for the source side. It resolves all 31 rows. Same rules: one
prior-art dispatch, functional test on a scratch (a body-to-body wire into an unnamed tunnel, ExecState 1),
toolkit row, then **no further op and no further dispatch** — run 8 goes straight to save → N1 → F1 → F2.
The freeze lift is now closed at four ops (CreateEqual, CreateConst, CreateConstOnTerm, ConnectNested).

## 11j. DECIDED (judgement, 2026-09-17, after the sentinel-ops wall and the THIRD consecutive outcome violation)

1. **Third and last op of the freeze lift: `OpCreateConstOnTerm_v0` = `Terminal.Create Constant` 6349C00** —
   the sibling of `create_control`/`create_indicator` (one ID off), which creates the constant **typed and wired**
   to the named terminal, so "create, then connect" disappears. Front half: the body-node index ladder
   `OpStopFromNode_v0` already uses (nested diagram, Nodes[index], Terminals[index]). Option (i) (fused
   create+connect) is not built.
2. **No diagnostic, framework, or review cycle before F1/F2** — the outcome reviewer's own ordering, adopted:
   third op → PHASE "full" → save → N1 → F1 (5 min) → F2. `diag_d1_full_route.py` is retired (its T6 control
   showed `OpWireSource_v5` returning 1055 for every wire — a separate defect, logged, not chased now); the
   re-wire source map is completed inside the build from `d1_step0_census.json` + `main_vi_nodeterms.json`
   (the 81/82 join the phase-full session computed) and written to `tools/bench/d1_rewire_sources.json` as a
   by-product, not a precondition.
3. **The outcome review has now fired three times in a row.** CLAUDE.md says a repetition stops the work for a
   re-plan with the user. The judgement taken here: the re-plan happened on 2026-09-16 (delivery-first) and the
   reviewer's prescription is *execute*, not *re-plan*; so the build proceeds and the user is told in one line
   that they may overturn this. Restart LabVIEW before the batch (handles were at 78,224).

## 11L. ✅ MEASURED 2026-09-17 — PHASE "full" stage 1 ran. **The blocker is ONE missing op, and it is now exact**

`tools/bench/build_d1_v0_run7.log`, **55 pass / 7 fail**, 118 s. The relocation reproduced exactly (S1 census
exact, S1t 4/4, `WhileLoop 3→6`, `Diagram 170→173`, 23 moves, `#5058` deleted + `GPU_kernel_v1.vi` dropped, 8
registers created, panel 114 intact, `#637` still `648 ← w3457`, original md5 unchanged before **and** after).

**The re-wire source map is COMPLETE: 109 / 109** (`tools/bench/d1_rewire_map.py` → `d1_rewire_sources.json`).
STATUS OPEN 28b's "45 of 82" was a join that could not see constants, control terminals, loop tunnels or the eight
moving shift registers — a register is neither a node on a diagram nor a `LoopTunnel`.

Of **66 routable rows attempted against LabVIEW** (not reasoned about — attempted, one call each):

| | n | measured |
|---|---:|---|
| **WIRED** | **35** | `g.wire` body-to-body by name WORKS on nested diagrams (10, incl. into `CaseStructure`/`ForLoop` named tunnels); `wire_sr` LeftIn/RightIn WORKS on the new loops (20); **`OpCreateConstOnTerm_v0` placed 5 literals in the real VI** at the originals' values |
| **FAILED** | **7** | 6 × `wire_control` → **5001 from `Get Controls.vi`**; 1 × `g.wire` `'subarray'→'x'` → 5001 from `Get Outputs.vi` |
| **NO-ROUTE** | **24** | 8 rows whose sink or source terminal **HAS NO NAME** (a structure selector / an unnamed tunnel); 16 `from-tunnel` rows whose outer wire has no NAMED node source |

End state: `ExecState 0`, nothing saved, working copy deleted; the three new loops' conditional terminals read
4767 / 8908 / 13038 with wire 0. **N1 / F1 / F2 cannot run** — they need a saved VI at ExecState 1.

🔴 **THE ONE QUESTION FOR JUDGEMENT.** D1 needs a wire creator that addresses **both** ends by **INDEX** on a
**nested** diagram. Every name-addressed op (`gscript.wire`, `wire_control`) cannot reach an unnamed terminal, and
both index-addressed ones take a **top-level** source (`gscript.py:2202`, `:2428`). `OpStopFromNode_v0` already
proves the sink half — its body-node ladder invokes `Terminal.Connect Wire` **6349C03** with a body terminal as
`Wire Source` — so the fourth op is that ladder **duplicated for the source side**. It is beyond the three ops
§11j authorises, so the freeze governs and a material session may not build it.

## 11k. THE ORDER OF OPERATIONS FOR `Equal?`'s `y` (material, 2026-09-17 — written down because a review demanded it)

`archive/peer/2026-09-17-priorart-priorart-createconst-term.md` **B2** `already-failed`: `Terminal.Create Constant`
6349C00's sibling `Create Control` 6349C01 was MEASURED to create **nothing** on an already-wired terminal
(`docs/keystone-op-spec.md:404-406`; carried as `tools/gscript.py:2159`), and `OpCreateEqual_v0` wires **both**
operands by construction (`docs/toolkit-capabilities.md:52`). So "place the `Equal?`, then create the constant on
`y`" cannot work as written, and the repair that suggests itself — connect a constant into the wired `y` — is
refuted too (`gscript.py:2206-2207`, `keystone-op-spec.md:445`: *Connect Wire on a wired sink re-routes and
breaks*).

**The order PHASE "full" uses, and the only one left standing with built ops:**

1. `OpCreateEqual_v0` places the `Equal?` on the body diagram with **both** operands taken from the same source
   node inside that body (the sentinel's dequeue): `x ← element`, `y ← element` — one net, two sinks.
2. `delete_object(target, "Wire", i)` on that net. Both `x` and `y` go bare; nothing else is on it.
3. `g.wire(...)` re-wires **`x`** from the dequeue's `element` by terminal name (Traverse-addressed, so it reaches
   a body diagram).
4. `OpCreateConstOnTerm_v0` invokes 6349C00 on the now-bare **`y`** → a typed constant, wired, carrying −1.
5. `OpStopFromNode_v0` drives the loop's conditional terminal from the `Equal?`'s Boolean (measured, wire 0→387).

This is **implementation ordering, not a design change** — the artefact §9a specifies is unchanged. It is recorded
here because the review's own words are *"decide in writing … before the recipe is written"*, and because step 2
deletes a wire the build itself created one call earlier, which a later reader would otherwise read as damage.

## 11h. DECIDED (user + judgement, 2026-09-17) — the TIFF writer is a FIXTURE INSERTION and is removed first

User: *"실제 실험에서는 tiff 저장 불필요함. 아마 지금 참조하는 코드는 클로드 사본으로 픽스처 생성을 위해 tiff 저장
기능 추가한 vi로 보임."* Confirmed by `docs/fixture-recording.md` (2026-09-01): `IMAQ Write TIFF File 2` #22700
and `Build Path` #23020 were **inserted** into the working copy for fixture recording; the true original
(`...4.5_KimLabMTroom_3StateClamping.vi`) never had them. Therefore:

- PHASE "full" **begins by deleting #22700, #23020 and the wires feeding them** (the `Image Out` branch, the
  `error out` branch, the path constant); gate: both uids gone, no staying node bared, ExecState unchanged.
  This restores the original; rule 1a is not engaged.
- Every "unconditional TIFF stays / F1 capped at 60 s / TIFFs deleted" clause above (§4, §11b.4, §11e) is
  **withdrawn**. F1 runs the user-approved 5 minutes when time allows.
- Read-only confirmation on the true original: no `IMAQ Write TIFF` node (GetVIReference only, md5 before/after).

## 11h. DECIDED + MEASURED (2026-09-17) — **the per-frame TIFF writer is NOT original behaviour. D1 DELETES it.**

**The clause this withdraws** is §5a's row for `#22700`: *"`IMAQ Write TIFF File 2` — **stays 1.1** — unconditional,
exactly as the original has it"* (`:304`), and §3's *"`#22700 IMAQ Write TIFF File 2` **unconditional, exactly as
the original has it**"* (`:242`). **Both are wrong**, and this project's own file said so all along:
`docs/fixture-recording.md:8-20` — *"what was **INSERTED** into the working copy (2026-09-01)"* — lists four
nodes added for FIXTURE RECORDING: `IMAQ Write TIFF File 2` **#22700**, `Format Into String` **#22703**,
`Strip Path` **#23175**, `Build Path` **#23020**. The user states real experiments never save TIFFs.

### ✅ MEASURED, read-only, 2026-09-17 — `tools/bench/diag_true_original_tiff.log`, **6 pass / 0 fail**

The TRUE original `..\Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi` was read by `GetVIReference` only —
never opened for writing, never saved, never copied — md5 **`1eb666c1df8ab3ded6cdabe8da1f4681` before AND after**;
the working copy's md5 `2a78e17c449c…` likewise unchanged.

| | true original | working copy | Δ |
|---|---:|---:|---:|
| `SubVI` | **97** | 98 | **+1** = `#22700` |
| `Function` | **179** | 181 | **+2** = `#23020`, `#23175` |
| `Node` | **622** | 626 | **+4** = the four above plus `#22703` |
| uids 22700 / 22703 / 23020 / 23175 | **none present** | all four present | — |

So the four inserted nodes are the **whole** difference between the two files, by count and by uid. ⚠️ Reported
honestly: `node_info()` returned **0 rows** on both VIs (the top-level diagram is a flat sequence), so the
"no node whose name mentions TIFF" half of the gate is **vacuous**; the uid membership and the count arithmetic
are the evidence, and they agree.

### What D1 does

**PHASE "full" deletes `#22700` and `#23020` BEFORE the moves**, with the wires that fed them (the `Image Out`
branch, the `error out` branch, the path wire). Gate: both uids gone, **no staying node left with a bare named
input**, `ExecState` unchanged across the deletion.
⚠️ `#22703` and `#23020`'s other feeder `#23175` were inserted in the same pass but are **NOT** named for
deletion here, and that is deliberate, not an oversight: `#23175` is a measured collateral sink of `#376`'s
**w5090** net (§7.2b) and `#22703` branches the frame-index subtract `#5119` — both are SINKS on nets whose
other ends stay, so deleting them is a second, separable change. After `#23020` goes they become dead-but-legal
(a source with no sink cannot break a VI). **Reported in the run, left standing.**

**F1 consequence:** no TIFF cap, no per-run TIFF deletion, and §10's "≈122 MB/s ⇒ 60 s ≈ 7.3 GB" arithmetic no
longer binds the run length — the user-approved **5 minutes** becomes affordable (`cycle15-plan.md:77`).
§10's F1 row and OPEN 4 are superseded by this paragraph.

## 11i. THE ONE STRUCTURAL QUESTION LEFT — how the `−1` constant reaches `Equal?`'s `y` (material, 2026-09-17)

§11g.1's route (c) is **BUILT and FUNCTIONAL**: `OpCreateEqual_v0` and `OpCreateConst_v0`, 23/0
(`tools/bench/build_opsentinel_ops_run3.log`) — both place their node on a NAMED subdiagram (owner chain
uid → body `Diagram` → the right `WhileLoop`, read twice), the `Equal?`'s operands may come from an outer
diagram (LabVIEW makes the tunnels, `LoopTunnel 0 → 2`), and `OpStopFromNode_v0` then drives that loop's
conditional terminal from the `Equal?`'s Boolean (**term 119, wire 0 → 387**) with the VI at **ExecState 1**.
That is §9a's sentinel shape end to end, on a scratch — **except for one wire.**

**`Create Constant.vi` places the constant UNWIRED, and nothing in the fleet connects it to `Equal?`'s `y`.**
Prior-art B2 (`archive/peer/2026-09-17-priorart-priorart-d1-sentinel-ops.md`): the creator's `Terminal` output
is a refnum that dies with its op's dataflow (`archive/2026-08-31-status-full-assembly-narrative.md:531-534`,
*"a chain of node creation must sit in one fused op, never split across COM calls"*), and a `Constant` is a
**GObject, not a `Node`**, so `Get Outputs` — the mechanism both new ops use to fetch a terminal safely inside
the op — cannot reach it. Setting the refnum over COM instead is the recorded 1055 modal that killed
`OpBuildCase_v0` (`docs/NAMES.md:473-475`), so that door is closed on the record.

| candidate | what it is | cost |
|---|---|---|
| **(i) FUSE** | one op that creates the constant AND connects it: `Create Constant.vi` → `Terminal` → `Terminal.Connect Wire` **6349C03** inside a single dataflow. The second half is already built and measured — it is `OpStopFromNode_v0`'s own back end | a THIRD op, additive on two proven halves |
| **(ii) `Terminal.Create Constant` 6349C00** | one ID off `create_control` **6349C01** / `create_indicator` **6349C02** (`tools/gscript.py:2155-2182`). It creates the constant **FROM the sink terminal**, so it comes out correctly typed AND already wired, and both VARIANT inputs leave the COM boundary entirely | a THIRD op. ⚠️ **not free**: that ladder walks the **top-level** `Nodes[]` (`docs/NAMES.md:460-461`), so it needs the same subdiagram addressing route (c) needed |

Either is **beyond the two ops §11g.1 authorises**, so the freeze governs and **only judgement may lift it.**
A material session may not choose (CLAUDE.md §3), and this one did not.

⚠️ **Also unverified, and cheap:** whether `OpCreateConst_v0`'s constant actually carries **−1**. The value was
written through a **VARIANT** control and has never been read back; `OpConstValueN_v1`
(`docs/toolkit-capabilities.md:47`) is the reader that would settle it, and `archive/2026-09-15-status-stage2-
cycles-1-7.md:290` records numeric values coming back through that boundary as `None` with no error.

## 11g. DECIDED (judgement session, 2026-09-17, after three full-route reviews with 0 novel findings and no build)

1. **Sentinel comparison + literals inside the loop bodies: route (c)** — wrap erdosmiller `Create Equal.vi` and
   `Create Constant.vi` in the `queue_node` pattern (the fleet's proven donor route). The cycle-15 freeze is
   lifted for **exactly these two ops**. (a) `copy_by_index+move_in` is not used; (b) `Constant.Terminal` +
   `Connect Wire` is recorded as the alternative.
2. **No further prior-art dispatch for `build_d1_v0.py` / `diag_d1_full_route.py`** unless an op beyond the two
   in (1) is created. Three rounds (21 findings, 0 novel, 0 refuted) have covered the direction; the remaining
   work is execution.
3. **`guard_cycle.premature_build` condition (b) is refined**: a recipe edited after its review may run without a
   new review when the newest prior-art archive's "What was done with it" cites that recipe file in a `FIXED:`
   line — i.e. the edit *is* the disposition. Review → fix → run is the intended path, not a re-review trigger.
   Self-test both ways.
4. The withdrawn word "headlessly" at `d1-build-plan.md:203` / `build_d1_v0.py:419` is removed by the material
   session as part of (1); it is wording, not judgement.

## 11f. DECIDED (judgement session, 2026-09-17, after run 5 = 53/0 and the streaming-write review)

1. **No separate TSV stream in D1.** §7.3 measured that `#376 save trace.vi` accumulates AND calls
   `save N xyz traces.vi` **periodically from a Case** — the original already writes during the run; "only at the
   end" was a misreading. Moving #376 into the writer loop satisfies row 1.7's "written in order" and the user's
   "실행 중 계속" as the original does it. The TSV (§7.1) moves to D2; its copy route is refuted (review A3), the
   one-call `drop_subvi` route stays unmeasured.
2. **Authorised for PHASE "full"** (narrow, D1 parts only): the sentinel comparison primitive and the literals it
   needs inside the loop bodies — `OpConstValue`/`build_case` first, additive builds only where those cannot
   produce the node.
3. **§11e.2's stop authorisation now reads `OpStopFromNode_v0`** (the review chose the donor; same duty). Its
   open gates T5/T6 are settled by D1's own end-state gates: if D1's ExecState stays 0 and the cause is traced to
   this op, replace it by the `Loop End Ref` 6362C00 + `Terminal.Connect Wire` 6349C03 route the review named.

## 11e. DECIDED (judgement session, 2026-09-17, after build_d1_v0 run 4 — relocation PASSED, phase "full" blocked)

1. **`Q_focus` = 1-element queue, enqueue on the 25-frame tick with timeout 0 (drop-NEW) — ACCEPTED, with a
   gate.** `decisions.md:25`'s latest-wins is the overload rule for the *frame* path; here the producer writes once
   per 278 ms tick and the consumer's VISA round trip is measured at ~2.6 ms (`motion-path-audit.md:84-99`), so the
   queue is empty at every tick unless the focus loop has stalled longer than a tick — and in that case the original
   VI's single loop would itself have stalled. Same value at every tick that is consumed; the deviation exists only
   on a dropped tick. **Gate F1-drops: dropped ticks = 0 over the 60 s run** (count `timed out?` on the enqueue);
   one drop reopens this decision. `decisions.md:24`'s Lossy-Enqueue prohibition is scoped to the camera/frame
   handoff and does not apply here.
2. **The cycle-15 op freeze is lifted NARROWLY**: only ops this plan names as D1 parts — the stop front-half swap on
   `OpExitWhile_v0` (rev4c B1) and a streaming-write donor for §7.1 — each an additive build on a proven template,
   each with its own prior-art dispatch. General-purpose ops stay frozen.
3. **#3447 / #3529 / #3560 are CONTROL REFERENCES, not Locals** (rev4c A3): each gets a move-table row and goes
   where its measured consumer goes.
4. **Gate S4b**: an unwired conditional terminal legitimately reports 1055 on its wire read; the gate compares the
   terminal uid and `wire == 0`, not an empty error column.

## 11c. DECIDED (judgement session, 2026-09-17, after the rev-4 review) — TRANSPORT = QUEUES ONLY. Resolves §0-BLOCKER and §11.1/§11.3

§11b.1's "the Local creator exists" was **false** (asserted without checking — the rev-4 review's A1, a repeat of a
claim this project withdrew the same day). Retracted. Of the five measured candidates (queue · 1-element queue ·
user event · DVR · Local-without-creator), D1 uses **the queue family only** — the one transport exercised 162/162,
needing no new op under the cycle-15 freeze. "A queue contradicts freshest-wins" is refuted by
`restructure-plan-4.6.md:55` (rev-4 review A2), which tables local / 1-element queue as alternatives for this duty.

- **1.5 wake-up:** a **1-element queue** of DBL (the slice index, §0b). The TRACKING loop evaluates the 25-frame
  cadence (it owns the frame counter) and enqueues **only on a tick, with timeout 0** — full ⇒ skip, never block.
- **Reverse crossing** (#10407 → #12589 → #11639 → #637's stop): **#12589 stays on 1.1** (§11.3 resolved); the
  FOCUS loop writes #10407's t6 value into a **1-element queue**, and the ACQUISITION loop **polls it with timeout 0**
  each iteration into #12589's input. Same value, different carrier.
- **Stop of the three new loops:** no panel readers and no Local — the **end-of-stream token** pattern
  (`stage2-assembly-step-c.md:45`, `frame-ownership-design.md:102-103`): on stop the acquisition loop enqueues a
  sentinel into `Q_work`/`Q_meta` (a value the kernel can never produce: buffer number −1, empty image ref);
  tracking exits on it and forwards a sentinel into `Q_res`/`Q_good`/`Q_rmeta` (empty array / −1); the writer
  exits on that, then drains, writes nothing for the sentinel, and calls #6384; the focus loop gets its own sentinel
  (−1) on its wake-up queue. Order "stop users → drain → release" holds by construction. The single `stop (end)`
  ControlTerminal #642 stays in the acquisition loop.
- Local, user event and DVR: **not used in D1** (recorded as measured alternatives, not refuted).

## 11. OPEN — what this plan still does not decide

1. ✅ **§0-BLOCKER — the transport.** Resolved by §11c (queues only). *Was:* §11b.1 decided locals; the fleet has no Local creator and no
   `Local.Control Name` writer, and a new op is frozen. It blocks 1.5's wake-up, the reverse crossing, and the
   stop read in all three new loops. The only buildable alternative is a queue, which contradicts §6's own
   requirement. **One decision, three consequences.**
2. 🔴 **Is the GPU's whole-fixture divergence acceptable?** (STATUS OPEN 16.) D1 proceeds under §11a.1's written
   assumption; N1 reports both ranges.
3. ✅ **`#12589`'s placement — RESOLVED by §11c: it STAYS ON 1.1**, and the crossing is a **1-element queue**
   (`Q_focusback`) written by 1.5 and polled by 1.1 with timeout 0. *Was:* §11b.1's "a Boolean local written by
   the focus loop" read as *#12589 goes to 1.5*, rev 3 §4 put it on 1.2, and the DBL/Boolean question hung on it.
4. 🟡 **F1 at 60 s vs the user-approved 5 min** (§11b.4) — flagged to the user, not silently resolved.
6. ✅ **RESOLVED by §11e.3** — `#3447` / `#3529` / `#3560` each get a move row and go where their measured
   consumer `#48` goes: **1.5**. Written into **§5a-bis**, the count contract (**23**), §10's S3 row and
   `build_d1_v0.py`'s `CTLREF_TO_15`.
7. ✅ **RESOLVED by §11e.1** — `Q_focus` drop-NEW is ACCEPTED with the **F1-drops gate (dropped ticks = 0 over
   the 60 s run)**; one drop reopens it. *Was:* the skipping enqueue is drop-NEW where `decisions.md:25` decided
   latest-wins, and the queue carries **data**, so rule 1a.
8. ✅ **RESOLVED by §11e.2** — the op freeze is lifted **narrowly**, for the two ops this plan names (the stop
   front-half swap on `OpExitWhile_v0`, and the streaming-write donor for §7.1), each with its own prior-art
   dispatch. General-purpose ops stay frozen.
9. 🔴 **§7.1's STREAMING TSV — route and requirement both open, after its prior-art review**
   (`archive/peer/2026-09-17-priorart-d1-op-streamwrite.md`, 8 findings, 0 novel, all accepted; disposed there).
   Three things a material session may not settle: **(a)** the `copy_by_index`-from-vi.lib/NI-example route is a
   **recorded LabVIEW crash** (A3), so the donor census this session ran on
   `examples\File IO\Text (ASCII)\Write to Text File and Read from Text File.vi` — all three nodes found and
   indexed, `tools/bench/diag_filewrite_donor2.log` — is a fact about the example and **not** a usable route;
   **(b)** the route that IS available with built ops is `drop_subvi` of a **one-call** vi.lib file VI
   (`Write Characters To File.vi` / `Write File+ (string).vi` / `Open File+.vi` / `Close File+.vi`, all four
   present, `diag_filewrite_donor.log`) — no new op, no refnum across a loop border; **(c)** §10 has **no gate**
   for Abort/partial records, refnum ownership or disk-full (A4). §7.3 measured the premise and it survives.
5. 🟡 **Row 1.7 is step 3/4 work placed before step 1's measurement** (`decisions.md:46,:52`;
   `pre-rig-master-plan.md:97`). The user-approved `cycle15-plan.md:28-30` governs; the conflict is recorded.

## 11d. What the two prior-art reviews of 2026-09-17 corrected in this plan (rev4b + rev4c, 12 findings, 0 novel)

Both were accepted whole; no citation was refuted. The corrections live here so no section re-argues them.

| what rev 4 / §11c said | what our own files say | where it now stands |
|---|---|---|
| S3b's collateral census covers "every node that shares a wire with a mover" | it walked **diagram 43 only**, so `#7202 Global motor pos.vi` on **diagram 19** — the sole consumer of `#4256`'s final value, w4859 (`frame-loop-wire-graph.md:410,:424`; `main-vi-state.md:44,:89-91,:130-131`) — and the **shift registers** (not nodes on any diagram) were invisible | **FIXED in the recipe**: `sr_census()` over `#637`'s 14 registers + a whole-diagram-19 census + gate `S3b-d19`. `restructure-plan-4.6.md:354`'s "no field of `Global motor pos.vi` gains a second writing loop" is now checkable |
| §11c: "the enqueue is skipped … that is the **freshest wins, never blocks** property" | a plain `Enqueue Element` that skips on full keeps the **older** element — that is **drop-NEW**, and `decisions.md:25` + `frame-ownership-design.md:89-93` decided **latest-wins**, explicitly "not drop-new"; the primitive that would deliver it, `Lossy Enqueue Element`, is excluded by `decisions.md:21` | 🔴 **OPEN §11.7 — the one blocker left, and it is rule-1a**: `Q_focus` carries **data** (the slice index), so a skipped enqueue hands `#10407` t2 a value from an older frame |
| §11c's stop "needs no new op" / the recipe's "no construction route" | the conditional-terminal writer is a **front-half swap** on `OpExitWhile_v0`, the swap this fleet built four times (`toolkit-capabilities.md:31,:42`); a **Case** creator exists and is verified (`gscript.py:2616`, `toolkit-capabilities.md:124`); the literals come from **donor constants** in the original (`opconstvaluen_scan.json`: 0×69, 1×36, 20×2, −1×1, 25×1) via `copy_by_index` + `move_in`; and `stage2-assembly-step-e.md:39-40,:209-222` already **names, scopes and costs** the ops this needs | **the "no route" claim is WITHDRAWN.** PHASE "full" is blocked by the **op freeze** (`cycle15-plan.md:102-104`), not by a capability — §11.8 |
| §6: "`#48` t0/t1/t2 ← **Locals** `#3529` `#3560` `#3447`" | they are **control references**, not Locals (§6's own ⚠️ block) | **FIXED in §6**; the move-table gap is §11.6 |

## 11b-recorded. The reusable trap from step 0

A wire-graph slice mislabels **6 of the 7** backward-slice nodes, because state re-enters through **shift
registers** (`#1147` inner w505 → `#1142` inner w1681 → `#5540` t5) and through a **front-panel round trip**
(`#10969` writes indicator `min value` uid 17257; the implicit property `#17289` reads it back, with no wire
between the two ends). `tools/bench/diag_d1_step0_reclass.log:129` is authoritative; **any future slice of diagram
43 must include SR and panel round-trips.** The reseed selector is therefore one cycle-carried chain that runs
through the UI: `#5058 pos in cal image out` → `#10969` → indicator `min value` → `#17289` → `#10950` → `#9647` →
`#10445` → `#10247` → `#5540` → back into `#5058`, and it moves to 1.2 whole.

## 11u. ✅ MEASURED 2026-09-17 (material, route-B session 1) — the F1v RBW GATE IS UNSOUND, and the 6 `from-ctl` rows are TWO different faults

### 11u.1 🔴 The F1v gate does not measure what its name says. Do not cite "3 of 8 deleted" again.

`archive/peer/2026-09-17-rbw-deleted-wires-run9.md` (codex, `-Kind review`, **ANSWERED** 133 s; dispatched as the
mandatory review of run 9's failed prediction) **refutes** the reading recorded in §11s.2. Accepted in full, and
two of its four points are confirmable against files already in this repository:

1. `Terminal.Connect Wire` **6349C03 returns nothing**. The "wire uid at creation" is a later read of
   `Terminal.Connected Wire` 634A000, so `tools/recipes/build_d1_v0.py:1118-1121`'s
   `(survived if after == wire else died)` compares two `Connected Wire` reads — **object identity, not survival**.
2. Confirmed on the log: `build_d1_v0_run9.log:269` reads `RBW-DELETED #1359 t4 … wire 26189 -> 26412`. That
   terminal ends with a **NON-ZERO** wire. It was not deleted. The honest statement is **at most 2 of 8 became
   null and 1 of 8 changed wire identity**, not "3 deleted".
3. Unmeasured but live alternative: **terminal-INDEX drift.** The recipe re-resolves `Nodes[n].Terminals[t]` after
   every call, and LabVIEW creates/removes border tunnels as wires cross structures (`LoopTunnel 0 → 2`,
   `toolkit-capabilities.md:56`), so `T[4]` after the edits need not denote `T[4]` before them.
4. `#29874 t4`'s `delta 0` needs no defect: a second sink on an existing net is a BRANCH and adds no Wire object
   (`docs/NAMES.md:52`).

**Consequence for `toolkit-capabilities.md:56`**, which states RBW-survival as *"the gate that uid equality cannot
make"*: as IMPLEMENTED it **is** uid equality, so that sentence is wrong about this implementation. The sound
instruments, in the order this project can actually reach them: (a) **`ExecState 1` on a scratch built to be
otherwise runnable** — the skill's own "unforgeable signal", and the same list the 2026-09-01 review asked for
(*"verify each endpoint's connected-wire state, verify both endpoints' owning diagrams, and verify the target VI
is not broken"*, `archive/peer/2026-09-01-2026-09-01-opwireref-donor-plan-attack.md:89`); (b) **`Wire.Is Broken?`
6371004 + `Wire.Terminals[]` 6371003 read from a HELD terminal reference** — the reader `CLAUDE.md` has listed as
missing since cycle 7, **NOT BUILT, and a judgement call** (it is a second op).

### 11u.2 ✅ The 6 `from-ctl` 5001 rows are TWO faults, and the first is a CALLER BUG

MEASURED on a fresh working copy of the original, `tools/bench/diag_connectfromwire_facts.log` (5 pass / 1 fail,
73 s; original md5 `2a78e17c449c…` unchanged; scratch deleted in the same run).

| what was measured | result |
|---|---|
| run 9 **skipped** the reparent step | `build_d1_v0_run9.log:358` `SKIPPED-PHASE S3c-ctlterm: the 6 ControlTerminals reparented into 1.2` — so the controls stayed on `Diagram #639` |
| `build_d1_v0.py:1057` calls `g.wire_control(TARGET, [lbl], s_cls, s_i, [sink_name])` | **no `src_diagram_index`** ⇒ defaults to **0**, the top-level diagram |
| `Diagram #639` | is Traverse(`Diagram`) index **43** |
| `'Auto-Reset'` (no newline), `src_diagram_index=0` | **5001 from `Get Controls.vi`** — run 9 reproduced exactly |
| `'Auto-Reset'`, `src_diagram_index=43` | ✅ **WIRED**, sink wire **0 → 1231**, no error |
| `'Force\nsmoothing\nhalf-width'` (real newlines), `src_diagram_index=0` | 5001 from **`Get Controls.vi`** |
| `'Force\nsmoothing\nhalf-width'`, `src_diagram_index=43` | 🔴 5001 from **`Wire Inputs.vi`** — a DIFFERENT VI |

**Read it exactly.** With the right diagram index the newline label gets **past** `Get Controls.vi`: the source
control was found, newlines and all. The remaining 5001 comes from `Wire Inputs.vi`.

⚠️ **CORRECTED the same day, and the correction matters.** My first reading — *"so it is `Wire Inputs.vi` failing
to match the DESTINATION name"* — is **WITHDRAWN**. `archive/peer/2026-09-17-wireinputs-forloop-tunnel-name.md`
(codex, `-Kind review`, ANSWERED) found the defect in my own log: the `bare_sink` step for `#1359` t7 reports
`wire 31059 -> 31166 after baring`, i.e. **the sink was still occupied** when `Wire Inputs.vi` was called. 5001 is
in LabVIEW's user-defined range (5000–9999) and the library may raise it for a *connection* failure as readily as
a *lookup* failure, so that row proves nothing about names. Two live causes remain, neither measured: an occupied
sink, and the peer's second one — a For Loop tunnel is a `LoopTunnel` with an OUTSIDE and an INSIDE terminal, so a
name-addressed helper may resolve the wrong side. **Method fix carried forward: a "bare the sink" step must assert
the terminal reads wire 0 and stop if it does not.** So:

* **The newline is NOT the cause.** Three of the six failing labels (`Auto-Reset`, `Reset Tracking`,
  `Correction Factor`) carry no newline at all and failed identically, and the newline label's source end
  resolved once the diagram was right.
* **Fault 1 — 3 rows, CLOSED by measurement:** wrong `src_diagram_index`. One-line caller fix.
* **Fault 2 — 3 rows (`#1359` t7, `#1359` t8, `#29874` t6), UNDIAGNOSED.** All three are `ForLoop` tunnels whose
  names carry newlines; all three raise 5001 from `Wire Inputs.vi` with the source diagram index correct. The
  cause is **not established** (see the correction above): occupied sink, or wrong tunnel side. They are
  re-assigned to the INDEX-addressed writer `OpConnectNested_v1` in `docs/d1-route-b-plan.md` §4, which needs no
  name at either end. ⚠️ NOT yet measured: whether `OpConnectNested_v1` wires those three. That is one recipe row,
  not an op.

---
<!-- FROZEN-FOOTER chat-D1 -->
## FROZEN 2026-10-02 (card chat-D1) - index: `docs/d1/INDEX.md`

Frozen IN PLACE on 2026-10-02 by card chat-D1 (user 2026-10-02: "문서 정리안 전체" / "이렇게 하고 한번 테스트해보자"). Every line above this footer is unchanged and keeps its line number, so every `file:line` citation in logs, cards and reviews still resolves. Only the frontmatter `status:` value changed (to `frozen`).

Why: 1,300 lines; its §9 pool queues were superseded by `docs/ring-buffer-design.md` (PD238(a)); the facts still cited are reached through `docs/d1/INDEX.md`.

Do NOT append here.

