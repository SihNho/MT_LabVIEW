---
type: archive
status: historical
date: 2026-09-17
tags: [status-narrative, cycle15, d1, phase-full]
parent: STATUS.md
---

# Cycle 15, session "D1 phase full" — the narrative, relocated verbatim from STATUS.md (rule 4)

Material session, 2026-09-17 07:3x–08:xx. Lock acquired and released; original
`Min_Track N beads V6_ParallelLoop.vi` md5 `2a78e17c449cacdaf5da389818526859` asserted before and after every run;
`save trace.vi` md5 `9d126b32e6de26aaa7bef48653dd991c` before and after; no GUI; no hardware; every scratch copy
created and deleted in the same run.

## 0. Relocated verbatim from STATUS.md, session "D1 phase full (2)", 2026-09-17 09:0x (rule 4, ≤110 lines)

STATUS OPEN 27b/27c, in full as it stood before compression:

> 27b/27c. ✅ **RUN 5: 53 PASS / 0 FAIL, 43 s** (`build_d1_v0_run5.log`; copy created+deleted in the run, not saved,
>    md5 before AND after, handles 31,002→33,225). The five gate specs are fixed (S3b-collateral excludes the
>    **deleted** `#5058`, whose 13 cut terminals ARE §8's crossings — the dropped GPU kernel **reused uid 5058**;
>    S3d SKIPPED-PHASE; S4b ×3 per §11e.4 → terms **1183/1204/1225, wire 0**, 1055 reported not gated). **All 23
>    moves pass**, incl. §11e.3's `#3529`/`#3560`/`#3447` → `Diagram#1194`→`WhileLoop#1134` = **1.5**.
>    **Re-wire list is now 109 terminals over 24 uids** (was 106/21); collateral 0, d19 clean, no SR changed.

STATUS OPEN 30, in full:

> 30. 🔴 **STREAMING TSV (§7.1) NOT BUILT — its review stopped it** (8 findings, 0 novel): A3 kills the
>    copy-from-NI-example route I had just measured; B1 leaves `drop_subvi` of a **one-call** vi.lib file VI (4/4
>    present); B2 withdraws "D1 cannot build this"; A4 finds **no gate** for Abort/disk-full. → plan §11.9.

STATUS OPEN 29's long form, in full:

> 29. 🟡 **`OpStopFromNode_v0.vi` BUILT + SAVED, 20/2** (`build_opstopfromnode_v0_run3.log`); route chosen by its own
>    prior-art review (B1: `Loop End Ref` **6362C00** returns a `Terminal`, `Terminal.Connect Wire` **6349C03** is
>    built — erdosmiller not needed; A3: "additive" is gated by W8b). ✅ **The write is MEASURED**: cond. terminal
>    **119, wire 0 → 147**, the SAME uid on the body node's Boolean output, op `error out` empty. 🔴 **T5** ExecState
>    0→0→0 and **T6** `OpWireSource_v5` returned no terminals for w147 — budget spent, 2 explanations each in
>    narrative §3b. **Not closed.**

**T5 is now CLOSED on the record, without a run** (prior-art review `2026-09-17-priorart-d1-full-route.md` B4):
`docs/NAMES.md:788` — *"Never gate on `ExecState` while a required input is still unwired — it cannot
discriminate"* — plus `.claude/skills/labview-automation/references/com-driving.md:206` (*"A node with unwired
required inputs makes the VI BROKEN"*). `Is Path and Not Empty.vi`'s `path` is required, so run 3's
`ExecState 0 → 0 → 0` says **nothing** about `OpStopFromNode_v0`: explanation A was a standing rule all along, and
the T5 gate as written could never have discriminated. T6's expected answer is likewise published
(`docs/toolkit-capabilities.md:48`, `tools/bench/diag_d1_step0.log:21-22`), so it survives only as a **control**.

## 0b. Session "D1 phase full (2)", 2026-09-17 08:3x–09:5x — three prior-art rounds, 21 findings, 0 novel

Material session. Lock acquired and released; original md5 `2a78e17c449cacdaf5da389818526859` **never changed**
(only read); **no LabVIEW edit was made at all** — no working copy was created, because the run was stopped by
its own reviews before it started. No GUI, no hardware.

`tools/recipes/diag_d1_full_route.py` was written, reviewed, rewritten, reviewed, corrected, reviewed. All three
exchanges are archived and **individually disposed** (`archive/peer/2026-09-17-priorart-d1-full-route.md`,
`…-rev2.md`, `…-rev3.md`): 6 + 8 + 7 findings, **0 novel in any round, none refuted**. That count is the
session's main result: every question the diagnostic was built to ask was already answered in our own files.

**The re-wire source map, complete at 82/82 with no LabVIEW run.** 81 wires resolve by joining
`main_vi_nodeterms.json` (3,328 node terminals of all 170 diagrams) with `d1_step0_census.json` `.tunnels` (132
LoopTunnels, outer + inner + `in_is_source`), `.shift_regs` (14 registers, both sides), `.panel` (114
ControlTerminals) and `opconstvaluen_scan.json` (180 numeric constants). Source classes: **Node 41 · LoopTunnel
15 · LeftSR 10 · ControlTerminal 6 · DigitalNumericConstant 5**. Two collapses were needed and are worth keeping:
a LoopTunnel's INNER terminal is a source when it feeds the body (read `in_is_source`, never assume), and a
structure's output tunnel is ONE connection seen twice — as a source terminal of the structure node and as the
tunnel's outer terminal (`docs/frame-loop-wire-graph.md:17`) — which is collapsed to the Node view.

The 82nd wire, **w3268**, needed no run either: measured 2026-09-16 with the same op
(`tools/bench/diag_autofocus_border.log:19-26`, published `docs/camera-acquisition-facts.md:225-230`) —
`wire 3268 driven by ('Diagram', 639); sinks [Function 2136, SelectorTunnel 3045, LoopTunnel 2213, Function
10068, SubVI 1114]`. **I had predicted the opposite on both halves** (no source at all; owner `WhileLoop #637`
⇒ the loop's iteration terminal `i`), so the rule-1a hazard I was carrying about moving `#376` to 1.7 — that
1.7's own `i` would count writer iterations rather than frames — **is refuted before it was tested.**

**Addressing.** 109 cut terminals: **81 by name, 28 by index** (19 empty-named + 9 whose name is not unique in
their node — `#5540` t2/t3 and t5/t6, `#10445` t2/t3, `#2626` t1/t2/t3). My "19 unreachable" was a derivation and
is withdrawn: the record already stores `term_index` and `is_source`, and `wire_sr` (`gscript.py:523-528`) and
`OpStopFromNode_v0` both address a **body** node's `Terminals[index]` by index.

**ExecState of a fresh copy — the discriminator is PRELOAD** (rev3 A4), and it has never been varied in a
controlled pair. The record splits 3–3 with no exceptions: **1** whenever the ORIGINAL hierarchy is
`GetVIReference`d before the copy is opened (`drive_original_copy_v3.log:7-12`, `v2.log:8-13`,
`d0_clickprobe.log:7-12`), **0** whenever it is not (`build_d1_v0_run5.log:13-16`, `run4.log:18`,
`probe_move_into_v0.log:217`). The ~1.3–1.4 s panel-open-to-read gap is present in **all three** of the 1s, so
elapsed time is fully confounded with preload; varying only a settle cannot separate them. The controlled pair —
same instance, one copy read with the original resident and one without — is one line and is the measurement
still worth buying.

**Why the recipe was not run even though its gate would have passed.** `copy_by_index` must start on a **fresh
LabVIEW instance** or it hits a recorded **Errno 22** (`build_track_v6_queue.py:105-114`; `gscript.py:1304-1307`
states the rule about itself), and the file had no restart. Running it would have spent a failure-budget slot on
a defect already in the record. The file now refuses P2 unless `FRESH_INSTANCE_DONE` is set. Two further
corrections are in it: its ExecState citation pointed at `gscript.py:1351`, which reads `exec_state(MOVE_DST)` —
the Move-example **fixture**, not the target (rev3 A3) — and `restore_move_fixtures()` had been placed in a
`finally`, which `gscript.py:1268-1272` forbids outright and which
`archive/peer/2026-09-15-strtopath-fail4-gui-save-of-broken-target.md:81` calls "the primary protocol defect".

**Two premises I inherited and repeated without opening the citation, both now withdrawn:** "`copy_*` from
vi.lib/NI examples is a recorded crash" (the prohibition is **vi.lib only**, `keystone-op-spec.md:136-143`; an
NI-example donor is recorded working twice through `copy_by_index`, `build_opconstvalue_v1.log:21-25,:45-49`),
and "§11f.2 authorises exactly this" (it authorises the **objective** and orders `OpConstValue`/`build_case`
**first** — both now discharged in writing: they are readers, and a top-level Case creator taking a front-panel
selector by name).

## 1. The five gate specs of run 4 — FIXED, and why each was a gate defect and not a build defect

`tools/recipes/build_d1_v0.py`, against `tools/bench/build_d1_v0_run4.log` (46 pass / 5 fail):

| gate | run 4 said | the defect | the fix |
|---|---|---|---|
| **S3b-collateral** | 13 "bared staying terminals", all on uid **5058** | `neighbours` = "shares a net with a mover AND is not in `MOVE_TABLE`", and `#5058` satisfies both because it is **DELETED**, not moved. A deleted node is not a staying node — and those 13 wires **are** plan §8's 13 crossings, which the gate two lines above *requires* to be in the cut set | `staying = [u for u in neighbours if u != KERNEL_UID]`; the 13 stay in `cut`. A FACT line records the **uid reuse** (the dropped GPU kernel was re-issued uid 5058) and that the after-pass reads 5058 on the FRAME diagram, where the new kernel does not live, so nothing resolves circularly |
| **S3d** (6 seam tunnels) | all six `unresolved` | the six non-indexed tunnels are created by PHASE **"full"**; in PHASE "relocate" nothing is re-wired at all, so the gate tested the phase boundary | armed only when `PHASE == "full"`; prints `SKIPPED-PHASE` otherwise |
| **S4b** ×3 (1.2 / 1.5 / 1.7) | term **1183 / 1204 / 1225**, wire **0** — the correct relocate-phase answer — failed on `errs 'error 1055: Property Node'` | an **unwired** conditional terminal has no wire to return a reference for, so `Connected Wire` legitimately reports 1055 | plan §11e.4: compare the **terminal uid** and `wire == 0`; the error text is reported, never gated (both phases) |

## 2. The three control references — move rows added (plan §11e.3 / §5a-bis)

`#3529` `- Inc (PgDn)` (w4833), `#3560` `+ Inc (PgUp)` (w2819), `#3447` `Focus Step (F1)` (w1893) all feed
`#48 ASI_adjust focus-subvi.vi` t0/t1/t2, and `#48` moves to 1.5 — so they move to **1.5**.

**Why §5a never had a row for them, measured rather than guessed:** they are in neither `d1_step0_census.json`'s
47-node `diagram_43` list nor `ctlterm_owners.json`'s 114 `ControlTerminal`s. A LabVIEW `Constant` is a **GObject,
not a Node**, so `Diagram.Nodes[]` never returns one. `move_in` resolves a **uid** through
`UID to GObject Reference.vi`, so the class never enters the call. Run 4's own cut list already showed all three
wires going wired→bare when `#48` moved.

Count contract: **23 moves + 1 delete + 1 drop** (17 → 1.2, 5 → 1.5, 1 → 1.7).

## 3. The stop op — the prior-art review replaced the design before a line was built

Dispatched `archive/peer/2026-09-17-priorart-d1-op-exitwhile-node.md` (slug `d1-op-exitwhile-node`), 5 findings,
0 novel, all accepted and disposed in that file. The proposal was a front-half swap on `OpExitWhile_v0`
(delete `Get Controls.vi`, feed the stop `Index Array` from a third `Get Outputs.vi`). Two verdicts changed it:

* **B1 `helper-exists`** — the erdosmiller `Exit While Loop.vi` `Stop Condition` is not the only route.
  `WhileLoop.Loop End Ref` **6362C00** already hands back a `Terminal` (`NAMES.md:246-249`, verified by
  `OpLoopEndRef_v0`, 16/0) and `Terminal.Connect Wire` **6349C03** on a sink is built four times over.
* **A3 `contradicted`** — the build was authorised as *additive* (§11e.2) and the proposal deleted a subVI.

So the op is `OpStopFromNode_v0.vi`, an **additive** build on `OpLoopEndRef_v0.vi`, and
`tools/recipes/build_opexitwhilenode_v0.py` was **deleted unrun**. Two read-only censuses paid the discovery up
front: `tools/bench/diag_exitwhile_front.log` (6/0 — the whole `OpExitWhile_v0` front half by uid and terminal)
and `tools/bench/diag_loopendref_front.log` (`#683 specific class reference` = the WhileLoop-typed reference;
`#657` data terminal **`LpEndRef`** = the conditional terminal; `#738 UID`, `#743 IsSource`, `#745 Wire` = the
read path that must survive the branch).

## 4. The streaming write — NOT built, and the review is why

`archive/peer/2026-09-17-priorart-d1-op-streamwrite.md`, 8 findings, 0 novel, all accepted and disposed there.

* I had **measured a donor**: `examples\File IO\Text (ASCII)\Write to Text File and Read from Text File.vi` holds
  `Open/Create/Replace File` (#194, #508), `Write to Text File` (#108, #1097, #1186, #1249, #5370) and
  `Close File` (#414, #2039) on its Case frames, with the whole-VI `report_all('Node')` index space
  `copy_by_index` addresses (`tools/bench/diag_filewrite_donor2.log`). **A3 `already-failed` kills the route**: a
  vi.lib / NI-example VI as a `copy_*` donor is a recorded LabVIEW crash. The census stands as a fact; the route
  does not.
* Run 1 of that census had its own gate defect worth recording: `node_labels(target, 0)` reads the **top-level**
  diagram only, so 14 of the VI's 19 nodes — the whole file chain, inside a Case — were invisible. Fixed by
  walking every `Diagram`.
* **B1** — the route that IS available with built ops is `drop_subvi` of a **one-call** vi.lib file VI.
  Measured present: `Open File+.vi`, `Close File+.vi`, `Write File+ (string).vi`, `Write Characters To File.vi`
  (`tools/bench/diag_filewrite_donor.log`, 4/4).
* **B2** — "the ONE thing D1 cannot build today" is **withdrawn**: file-I/O nodes have already been placed and
  wired into a working copy of the original — by a **GUI** route, which is a CLAUDE.md §3 decision, so it is
  named and not used.
* **A4** — §10 has no gate for Abort/partial records, refnum ownership or disk-full.

### 4b. A5's premise check — MEASURED, and it does not delete the work

`tools/bench/diag_savetrace_376.log`, 4/0, read-only on a COPY, md5 unchanged. `save trace.vi` (`#376`) has
**7 nodes and no file I/O whatsoever**: `Decrement`, `Quotient & Remainder`, `Equal?`, `Replace Array Subset`, a
`CaseStructure`, and inside the case `save N xyz traces.vi` + one `Property Node`. `saved file refnum` is a panel
**control** (FP[11]), passed through. So `#376` **accumulates** and calls the bulk saver **periodically** — it
does not append per frame. §7.1's TSV is therefore not a duplicate; but "the original saves once at the end" is
still wrong as written (periodically through `#376`'s Case, *and* once at the end through `#6384`). Recorded in
plan §7.3.

## 3b. `OpStopFromNode_v0` — BUILT and SAVED; the write is measured, two gates are UNRESOLVED

`tools/bench/build_opstopfromnode_v0_run3.log`, **20 pass / 2 fail**, 46 s. The op is
`C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\OpStopFromNode_v0.vi`, 16,833 bytes,
ExecState 1; labels in `tools/bench/opstopfromnode_labels.json` (`index 3` = body `Nodes[]` index, `index 4` =
that node's `Terminals[]` index). The build is **additive and gated as such**: Node 14→20, Property 8→11,
Wire 25→33, ControlTerminal 20→23, Invoke 0→1, IndexArray 1→3; W8b asserts no class lost a member. Each property
node was CENSUSED at creation (B3): `VI Server:Loop` 6361401 → data terminal `'Diagram'`,
`VI Server:AbstractDiagram` 6375809 → `'Nodes[]'`, `VI Server:Node` 6359000 → `'Terms[]'`.

**What is measured — the thing the op exists to do:** on a scratch While loop (EMPTY_v0 copy, `Is Path and Not
Empty.vi` in the body), the conditional terminal went **term 119, wire 0 → wire 147**, the same terminal uid, and
**w147 is the same wire uid on the body node's Boolean output** `Is Path and Not Empty?`. The op's `error out` was
empty. That is T3 / T3b / T4, all PASS.

**What is NOT resolved, with the competing explanations, because the failure budget for this test is spent (3
runs):**

| gate | observed | explanation A | explanation B | cheapest separator |
|---|---|---|---|---|
| **T5** ExecState 0 → 0, and still 0 after Remove Bad Wires | the scratch never compiles | **`Is Path and Not Empty.vi`'s `path` input is REQUIRED**, so the body node breaks the VI regardless of the stop — the op is innocent | the wire the op created is not a wire LabVIEW accepts on a conditional terminal (but then RBW should have removed it, and w147 survived) | read the donor VI's connector pane for required terminals, or repeat with a body node that has no required input |
| **T6** `OpWireSource_v5` returned **zero** terminals for w147 | the positive direction check could not run | my driver breaks out of the term walk on the FIRST non-empty error column, and I chose the columns `errS`/`errWU`/`errG` while the donor's own `read_wire` uses `errT`/`errO`/`errU` — so a legitimate read can look like the end of the walk | the wire index is wrong (I switched from `g.uids()`, which returns a **set**, to `report_all` order in this run — that fixed an `AttributeError`, not necessarily the index space) | run `OpWireSource_v5` on a wire whose source is already known (`wire 10850 → constant 10739`, its own 12/12 case) through the same driver |

Two earlier runs are recorded as non-results: run 1 died at `loop_in("while", …)` with
`error 1055: To More Specific Class in OpWhileLoopIn_v0.vi` — `loop_in` takes its tunnels from Traverse
`src_cls`[`src_index`] and **defaults `src_cls` to `"SubVI"`** (`gscript.py:978`), and EMPTY_v0 has no SubVI;
`while_loop()` is the right creator on an empty VI. Run 2 died in my own helper with
`AttributeError: 'set' object has no attribute 'index'` — `g.uids()` returns a **set**.

## 3c. `build_d1_v0.py` run 5 — **53 pass / 0 fail, 43 s** (`tools/bench/build_d1_v0_run5.log`)

PHASE "relocate", on a uniquely named copy created and deleted in the same run, **not saved**; original md5
`2a78e17c449cacdaf5da389818526859` **before and after**; handles 31,002 → 33,225.

* S1 BEFORE census exact: `Diagram 170, Node 626, Wire 1902, LoopTunnel 132, ControlTerminal 114, WhileLoop 3,
  Local 8, SubVI 98`.
* S2 `WhileLoop 3 → 6`, `Diagram 170 → 173`; 1.2 = `#1133`/body `#1170`, 1.5 = `#1134`/`#1194`,
  1.7 = `#1135`/`#1215`. S2c the six stayers still on `Diagram#639`.
* **S3: all 23 moves pass**, including the three new rows — `#3529`, `#3560`, `#3447` → owner `Diagram#1194` →
  `WhileLoop#1134`, i.e. 1.5, exactly where `#48` went.
* S3a Diagram still 173 (structures kept their frames). S3e `#5058` deleted, `GPU_kernel_v1.vi` dropped into 1.2 —
  and **re-issued uid 5058**, SubVI 98 → 98.
* **S3b census diff = 109 terminals over 24 uids** (was 106 over 21): the three control references contribute one
  cut terminal each (w4833 / w2819 / w1893). ⊇ §8's 13 crossings; **S3b-collateral now 0** with `#5058` correctly
  excluded from "staying nodes"; d19 clean; **no shift register changed**.
* S3c 8 shift registers created; ControlTerminal still 114, all 114 `panel_wiring` labels present.
* S3d **SKIPPED-PHASE** (its tunnels do not exist until PHASE "full"). S4a `#637` still term 648 / wire 3457.
  **S4b ×3 PASS**: terms **1183 / 1204 / 1225**, all wire 0; the 1055 is reported beside them, not gated.
* ExecState after the relocation: **0, expected** — the moves cut border wires and nothing is re-wired in this
  phase. The re-wire list is `tools/bench/build_d1_v0.json`.

## 5. What PHASE "full" still needs, measured rather than estimated

Beyond the two ops §11e.2 unfroze, the sentinel test itself needs a **comparison primitive inside each new loop
body** and the literals beside it. Neither is covered by the two unfrozen ops, and the `copy_*`-from-vi.lib route
is refuted (§4 above). The one route that touches no original and no vi.lib donor is **`copy_by_index` with the
D1 working copy as BOTH donor and target** — the original's own `Equal?` (#10019, #22284) and its donor constants
(`opconstvaluen_scan.json`: 0×69, 1×36, 20×2, −1×1, 25×1) are already inside the copy — followed by `move_in`.
**Unmeasured, not impossible**; it is the cheapest thing for the next cycle to test, and whether it is inside or
outside §11e.2's narrow unfreeze is judgement.

## 0c. Session "D1 full build (3)", 2026-09-17 09:2x–10:xx — the two sentinel ops, §11h, and the one question left

Material session. Lock acquired and released. Original `Min_Track N beads V6_ParallelLoop.vi` md5
`2a78e17c449cacdaf5da389818526859` before **and** after every run; the TRUE original
`Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi` md5 `1eb666c1df8ab3ded6cdabe8da1f4681` before and after
its one read-only census — `GetVIReference` only, never opened for writing, never saved, never copied. No GUI,
no hardware. Every working copy uniquely named and deleted in the same run.

### 1. `guard_cycle.premature_build` (b) — the disposition exemption (plan §11g.3)

`fixed_slugs()` was split into `fixed_citations()`, which returns the **paths** a valid `FIXED:` line cites as
well as its slugs; condition (b) now also releases when the newest prior-art archive's "What was done with it"
cites the recipe being run. Nothing was loosened: the same line must sit under the disposition heading, cite a
path that EXISTS, and that path must have changed AFTER the review — all three already enforced for the verdict
gate. `tools/bench/selftest_guard_cycle_fixed.py` isolates ROOT/BENCH/PEER into a temp tree and scores **6/6**:
T1 cited → ALLOWED; T2 no citation → REFUSED; T3 no review → REFUSED; T4 the line above the heading → REFUSED;
T5 a path that does not exist → REFUSED; T6 a path last changed BEFORE the review → REFUSED. It then released
the real case twice in this session (`build_opsentinel_ops.py`, `build_d1_v0.py`), which is the review→fix→run
order STATUS "START HERE" 5 had priced at ~10 min a round.

### 2. The two ops, and the wall they stop at

`tools/recipes/build_opsentinel_ops.py` = `build_opqueue.py`'s donor route (`OpExitLoop_v0`, whose `Diagram in`
already comes from `Traverse('Diagram')[index 2]`) + `build_opcreator.py`'s required-input probe loop. Three
runs, and the first two failures were both in the TEST, not the ops:

| run | result | what it measured |
|---|---|---|
| 1 | 20/2 | both ops ExecState 1 and saved. F3/F6 gated on `ExecState` **while the fresh While loop's conditional terminal was unwired** — `docs/NAMES.md:788`, a gate that could not discriminate. Also: the probe loop stops at ExecState 1 and `Value` is OPTIONAL, so `OpCreateConst_v0` could only ever make a DEFAULT-valued constant |
| 2 | 21/1 | `Value` forced to a control. Crash: reading `CondWireUID` off `OpStopFromNode_v0` raised LabVIEW **5005** — the `read_*` keys of `opstopfromnode_labels.json` belong to the separate reader `OpLoopEndRef_v0`, which is what `build_opstopfromnode_v0.py:458` uses |
| 3 | **23/0** | the whole sentinel shape on a scratch `EMPTY_v0` copy |

Run 3, in full: constant **#354** and `Comparison` **#46** both land on body `Diagram#110` of `WhileLoop#43`
(owner chain read twice with `OpOwnerChain_v1`); `Equal?`'s operands come from a node on the OUTER diagram and
LabVIEW makes the tunnels (`LoopTunnel 0 → 2`); `OpStopFromNode_v0` then writes the Boolean into the loop's
conditional terminal (**term 119, wire 0 → 387**) and the scratch reads **ExecState 1**. That last line also
**closes `OpStopFromNode_v0`'s T5** on a measurement rather than on a rule.

**The wall, and it is the prior-art review's B2.** `Create Constant.vi` returns the new constant's `Terminal`,
a refnum that dies with its op's dataflow, and a `Constant` is a GObject, not a `Node`, so no `Get Outputs`
reaches it. So the constant is placed **unwired** and nothing in the fleet connects it to `Equal?`'s `y`. Both
candidate answers — a FUSED create-const-and-connect op, or `Constant.Terminal` **634AC04** →
`Terminal.Connect Wire` **6349C03** (both halves already built, inside `OpConstValueN_v1` and
`OpStopFromNode_v0`) — are a **THIRD** op, beyond the two §11g.1 authorises. Not taken: judgement.

### 3. §11h — the TIFF writer, measured on the true original

`tools/bench/diag_true_original_tiff.log`, **6/0**: true original **SubVI 97 / Function 179 / Node 622** against
the working copy's **98 / 181 / 626**, and uids 22700 / 22703 / 23020 / 23175 present in the copy, **none** in
the original. The four inserted nodes are the whole difference, by count and by uid. ⚠️ Reported honestly:
`node_info()` returned **0 rows** on both files (the top-level diagram is a flat sequence), so the "no node
named TIFF" half of the gate is vacuous — the uid membership and the arithmetic carry it.

`build_d1_v0.py` gained gate **S1t**, which runs before any move. Run 6 (`build_d1_v0_run6.log`): **56 pass /
1 fail**, S1t itself **4/4** — `SubVI 98→97`, `Function 181→180`, `Node 626→624`, `Wire 1902→1899`, bare named
sinks **28→26** (the deletion REMOVED two, it bared none), `ExecState 0→0`. The single failure was
`S2c #22700 still owned by the frame loop body`, a **stale gate** — `STAY_ON_11` still listed the node S1t had
just deleted; the owner read echoed `'SubVI'#6810`, i.e. whatever now sits at that Traverse position. Fixed.

### 4. The re-wire source map: 45/82, not 82/82 — and the two are not the same claim

`diag_d1_full_route.py` P1 (offline, no LabVIEW) joined `d1_step0_census.json.resolved_boundary` to the
post-run-5 cut set and covered **45 of 82** wires — `LoopTunnel` 22 · `leftShiftRegister` 8 · `PanelTerminal` 6 ·
`rightShiftRegister` 4 · `OpWireSource_v5` 5 — leaving **37** uncovered, including w121, w505, w3040, w3268,
w5090, w5637 and the three control-reference wires w1893/w2819/w4833. STATUS 28b's "**82/82**" came from a
RICHER join the previous session computed in memory (adding `main_vi_nodeterms.json`'s 3,328 node terminals and
`opconstvaluen_scan.json`) and **never wrote to a file**. Both numbers can be true; only the 45 is reproducible
from what is on disk today. Addressing was re-confirmed: **81 by name, 28 by index**, the 28 listed in the log.

P2 (`copy_by_index` + `move_in`) did **not** run: its own gate refuses without a restart *in the same process*,
and the file never called `tools/lv_restart.py` — an exported `FRESH_INSTANCE_DONE` could not satisfy it, so the
gate could only ever refuse. It also crashed on `return res` before `res = {}`. Both fixed; the run is pending.
