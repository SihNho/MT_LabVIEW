# priorart-d1-full-route

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $6.2260  in 68 / out 47365 / cache-create 223429 / cache-read 5614542  (632s, 44 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (636s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PRIOR-ART REVIEW (trigger: direction-change).

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
# Plan under review ??`tools/recipes/diag_d1_full_route.py` (cycle 15, D1 PHASE "full", direction change)

## What I was told to do, and why I am not doing exactly that

The brief: write and run PHASE "full" of `tools/recipes/build_d1_v0.py` ??build the 8 queues on Diagram 19,
**re-wire every entry of `tools/bench/build_d1_v0.json` (109 terminals)**, wire the 8 shift registers, wire the
GPU kernel's 13 shared inputs + 6 constant extras, the Q_focus tick logic and the Q_focusback poll, the
end-of-stream sentinels with `OpStopFromNode_v0`, then purge / RBW / ExecState 1 / save / cold re-open, then run
N1, F1 (60 s live) and F2.

Before writing a line I read `build_d1_v0.json` and counted it. Two things say the instruction is not executable
as written:

1. **The re-wire list records only the terminal that went BARE, not what to wire it to.** Its 109 terminals span
   82 distinct wire uids. 58 of those 82 have exactly ONE end in the file; 21 have two; 3 have more. So for most
   nets the file does not name the other end.
2. **19 of the 109 cut terminals have an EMPTY name**, because they are structure tunnel terminals on
   `CaseStructure #5540 / #10445 / #2222 / #10407` and `ForLoop #1359 / #29874`. And `#5540` additionally has
   DUPLICATE terminal names (t2/t3 both `'Bead is good? array out'`, t5/t6 both `'x,y,z array out'`).
   `gscript.wire()` ??the only fleet writer that reaches a node on a NESTED diagram ??addresses a terminal BY
   NAME. `connect_terminals()` is index-addressed but TOP-LEVEL only; `connect2()` is index-addressed on the sink
   side but its SOURCE ladder is `VI ??Block Diagram (23C) ??Nodes[] ??Terminals[]`, i.e. top level
   (`tools/recipes/build_opconnect2.py:3-5`).

## What I propose to run instead ??ONE diagnostic, one bgrun, one log

`tools/recipes/diag_d1_full_route.py`:

* **R1 (offline, no LabVIEW).** Close gap 1 by JOINING measurements the project already owns:
  `tools/bench/main_vi_nodeterms.json` (every terminal of all 626 nodes of all 170 diagrams, with wire uid and
  direction), `tools/bench/d1_step0_census.json` `.tunnels` / `.shift_regs` / `.panel` / `.resolved_boundary`,
  and `tools/bench/opconstvaluen_scan.json` (180 numeric constants and the wire each drives). Prediction: all 82
  cut wires resolve to exactly one source end. Output `tools/bench/d1_rewire_sources.json`.
* **R2 (offline).** Classify all 109 cut terminals by whether `wire()` can address them: name non-empty AND
  unique within the node. Prediction: exactly 19 empty-named.
* **R3 (measured, on a uniquely named working copy of the original, deleted in the same run).** One new While
  loop on `Diagram#686`; move `#10950 #9647 #10247 #5540` into it, reproducing the D1 cut geometry; then
  * CONTROL: `wire(#10950 'x < y?' ??#9647 'x')` ??a fully NAMED pair ??must land.
  * TEST: `wire(#10247 'x .or. y?' ??#5540 t0, name '')` ??predicted REFUSED.
  The control runs through the identical code path, per `docs/toolkit-capabilities.md:213`.
* **R4.** The two separators STATUS OPEN 29 names for `OpStopFromNode_v0`: `wire_source(copy, 10850)` must
  reproduce its own 12/12 answer (source `DigitalNumericConstant #10739`); and a fresh `EMPTY_v0` copy with only
  `Is Path and Not Empty.vi` dropped at top level ??if ExecState goes 1 ??0, the donor's required `path` input
  breaks the VI by itself and run 3's T5 says nothing about the stop op.

Original md5 `2a78e17c449cacdaf5da389818526859` asserted before and after; nothing saved outside
`user.lib\claudeDev`; both working copies deleted in the run.

## The questions for you

1. Has the **re-wire source map** (wire ??its driving object) already been BUILT or MEASURED under another name?
   I found `frame_loop_graph_43.json`, `frame_loop_border.json`, `boundary_manifest.json`,
   `d1_step0_census.json.resolved_boundary`, `case5540_frame_sources.json`, `case5540_tunnel_uids.json` ??is one
   of them already this answer, making R1 redundant?
2. Has "can a fleet op wire an UNNAMED / DUPLICATE-named structure tunnel terminal?" already been **measured or
   tried and failed**? Is there an op or a route I have missed ??`OpTunnelRead_v0`, `OpTunnelInd_v0`,
   `OpConnectCtl_v0`, `copy_by_index`, erdosmiller `Wire Inputs.vi`, `Terminal.Connect Wire` 6349C03 driven some
   other way?
3. Are the two `OpStopFromNode_v0` separators already run, or already answered in an archived exchange?
4. Which of my cited facts are contradicted elsewhere in our own files? Specifically: my claim that `connect2`'s
   source side is top-level-only, and my claim that `wire()` is name-addressed with no index fallback.
5. Is stopping PHASE "full" to run this measurement the wrong call ??i.e. is there a route by which the 109
   re-wires could be written today with built ops, so that the cheapest next step is the build after all?


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-17
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.
Narrative relocated **verbatim** (rule 4) to `archive/2026-09-16-status-cycles-11-13-narrative.md` + the four
`archive/2026-09-17-status-*.md` (**`??d1-phase-full-narrative.md`** = this session).
?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this from disk.

## START HERE
1. **`docs/pre-rig-master-plan.md` is THE plan**; settled decisions **`docs/decisions.md`**; cycle plan
   `docs/cycle15-plan.md`; **build plan `docs/d1-build-plan.md` (REV 4 + 짠11c/짠11d/짠11e)** ??짠5 + 짠5a-bis (moves),
   짠10 (S/N1/F1/F2). Recipe: `tools/recipes/build_d1_v0.py`.
2. ?좑툘 A prior-art dispatcher's log MUST be named `priorart_*` / `peer_*` (`tools/logclass.py`) or the guards read
   the reviewer's prose as a build failure ??it blocked this session, the 6th of its recorded class.
3. ??**Scripting EDITS are silently declined until the target's FRONT PANEL has been opened** ??`ensure_loaded()`.
4. ??**A fixed op PATH is served from LabVIEW's memory, not from disk** ??unique working-copy filename per run.

## LabVIEW execution lock

```yaml
labview-lock:
  status: acquired
  owner: material/cycle15-d1-phase-full-2
  since: 2026-09-17
  purpose: diag_d1_full_route.py - the PHASE "full" route measurement (re-wire source map, wire() addressability
    with a control, OpStopFromNode T5/T6 separators). Read-only on the original; one uniquely named working copy,
    created and DELETED in the run.
# 2026-09-17 07:3x-08:2x material/cycle15-d1-phase-full: RELEASED. `build_d1_v0.py` run 5 PHASE "relocate"
# (53/0), `build_opstopfromnode_v0.py` x3, and four read-only censuses. Every scratch/working copy uniquely
# named, created and DELETED in the same run. Original md5 2a78e17c449... before AND after run 5;
# `save trace.vi` md5 9d126b32e6de... before AND after. No original edited, no GUI, no hardware.
# Handles 31,002 -> 33,225 (baseline ~31,500).
# Earlier holders (all RELEASED, all md5-clean, none touched an original; run-4 handles 30,682 -> 38,336 after a
# restart) -> the status archives of 2026-09-16/17.
```
**Never assume an instance exited**: `tasklist | grep -i labview`, kill strays. Fresh instances ??1,500 handles;
unique scratch VI name per run, deleted in the same run.

## HARDWARE ??permission follows the RIG STATE. Current state: **遺꾪빐 / DISASSEMBLED ??everything allowed**

| rig state | motors (PI 쨌 rotor 쨌 magnet) | **ASI piezo** | camera |
|---|---|---|---|
| **遺꾪빐 ??disassembled ??WE ARE HERE** | ??| ??| ??|
| 議곕┰ ??assembled | ??| ??| ??|
| ?ㅽ뿕以???experiment running | ??| ??| ??|

?좑툘 **The ASI carve-out is RETIRED** (rule 1b). **Only the user announces a state change.** Instruments: rotor
counter **0** 쨌 magnet full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz, never write `BinningHorizontal`;
**a session open RESETS ROI *and* exposure** ??the acquisition loop applies `tools/bench/camera_contract.py`.
**No beads while disassembled**; fixture work unaffected.

## Where things stand
**Stage 1 CLOSED** (the seven `docs/main-vi-*`). **Stage 2 IN PROGRESS**: `Track_v6_CPU_core_v0.vi` 69/69 쨌
`??queue_v0.vi` 162/162 ??**say it exactly:** bit-identical for the **first 10,018 frames only**, both **replay**
artefacts (recorded TIFFs, `FOR` loops, no acquisition, no stop). **THE GAP:** 169 ops, 118 recipes, 223 peers ??
**zero runnable experimental VIs**.

## OPEN ??one line each; long forms in `archive/2026-09-17-status-cycle15-narrative.md`
1??, 5, 9??2, 18 ??**all in archive 짠9**: PERIODIC auto-reset ungated 쨌 autofocus CLOSED (25 frames ??3.6 Hz) 쨌
   27 undisposed peer archives 쨌 startup drives instruments 쨌 A2 54/54, A3 112/170 쨌 doc lint 2/4/3 쨌 **TIFF
   1.3 MB/frame, ??22 MB/s measured ??bound it or the disk fills**.
13/14/15b/17b. ??stop measured (`#637` term **648 ??w3457 ??#11639**; `stop (end) 2` separate) 쨌 ?뵶 cycle-15
   prior-art partly disposed 쨌 ?뵶 `bgrun --detach` misses an orphaned grandchild 쨌 ?뵶 v3's R11 scored the *restart*.
16. ?뵶 **GPU whole-fixture divergence OUTSIDE `decisions.md:38` ??JUDGEMENT** (`gpu_n1_deltas.json`): beads 0??
   **0 exceedances over all 10,043**; **only bead 4** ??10 x, 9 y, 1 flip, n_valid 10,029. ??짠4.
19/25/26. ??**PLAN = REV 4 + 짠11c/짠11d/짠11e**; TRANSPORT = **queues only**, sentinels stop 1.2/1.5/1.7,
   `#12589`/`#642` stay on 1.1; **six prior-art reviews disposed, 0 novel**. 19b/19c/24 in plan 짠2/짠5.
20??3. ??CLOSED ??0 slugs awaiting a response; `premature_build` (b) exempts a RE-RUN; handles clear on a restart.

27. ??**D1 RELOCATION MEASURED** ??run 4 (46/5) then **run 5 (53/0)**: S1 **Diagram 170** 쨌 S2 `WhileLoop 3??`,
   `Diagram 170??73`, 1.2=#1133/1170, 1.5=#1134/1194, 1.7=#1135/1215 쨌 S2c the six stayers on `Diagram#639` 쨌
   8 SRs 쨌 ControlTerminal 114 intact. **Re-wire list = `tools/bench/build_d1_v0.json`.**
27b/27c. ??**RUN 5: 53 PASS / 0 FAIL, 43 s** (`build_d1_v0_run5.log`; copy created+deleted in the run, not saved,
   md5 before AND after, handles 31,002??3,225). The five gate specs are fixed (S3b-collateral excludes the
   **deleted** `#5058`, whose 13 cut terminals ARE 짠8's crossings ??the dropped GPU kernel **reused uid 5058**;
   S3d SKIPPED-PHASE; S4b 횞3 per 짠11e.4 ??terms **1183/1204/1225, wire 0**, 1055 reported not gated). **All 23
   moves pass**, incl. 짠11e.3's `#3529`/`#3560`/`#3447` ??`Diagram#1194`??WhileLoop#1134` = **1.5**.
   **Re-wire list is now 109 terminals over 24 uids** (was 106/21); collateral 0, d19 clean, no SR changed.
28. ?뵶 **PHASE "full" STILL NOT WRITTEN. N1 / F1 / F2 NOT RUN ??nothing to report on them.** 짠11e.2's two ops do
   **not** cover the sentinel test: it needs a comparison primitive + literals **inside** each loop body, and
   `copy_*` from vi.lib/NI examples is a **recorded crash**. Untried route touching no original: `copy_by_index`
   with the D1 **working copy as both donor and target** + `move_in`. ??narrative 짠5.
29. ?윞 **`OpStopFromNode_v0.vi` BUILT + SAVED, 20/2** (`build_opstopfromnode_v0_run3.log`); route chosen by its own
   prior-art review (B1: `Loop End Ref` **6362C00** returns a `Terminal`, `Terminal.Connect Wire` **6349C03** is
   built ??erdosmiller not needed; A3: "additive" is gated by W8b). ??**The write is MEASURED**: cond. terminal
   **119, wire 0 ??147**, the SAME uid on the body node's Boolean output, op `error out` empty. ?뵶 **T5** ExecState
   0???? and **T6** `OpWireSource_v5` returned no terminals for w147 ??budget spent, 2 explanations each in
   narrative 짠3b. **Not closed.**
30. ?뵶 **STREAMING TSV (짠7.1) NOT BUILT ??its review stopped it** (8 findings, 0 novel): A3 kills the
   copy-from-NI-example route I had just measured; B1 leaves `drop_subvi` of a **one-call** vi.lib file VI (4/4
   present); B2 withdraws "D1 cannot build this"; A4 finds **no gate** for Abort/disk-full. ??plan 짠11.9.
30b. ??**A5's premise MEASURED** (`diag_savetrace_376.log` 4/0, md5 unchanged): `#376 save trace.vi` has **7 nodes
   and NO file I/O** ??it accumulates and calls `save N xyz traces.vi` **periodically** from a Case. ??plan 짠7.3.
31. ?뵶 **RETROSPECTIVE WINDOWS BROKEN ??`repeated-failure-class` 횞2 today (threshold 3).** `retrospective.py` takes
   the cycle start from the PREVIOUS retrospective's timestamp, so cycles 15 and 16 each reviewed a <1-min window
   with **zero builds**; `--since-hours` does NOT override it (`tools/retrospective.py:282-286`). Fix: make it
   override, or use the oldest unreviewed build log (`guard_cycle.py:427-436`). Also **no `docs/cycle16-plan.md`**
   ??the scope check cannot run. Disposed in `??retrospective-cycle16.md` / `??cycle16b.md`.

## NEXT
?뵶 **JUDGEMENT ??three questions** (all of the relocation is measured and depends on none of them):
1. **Is 짠7.1's TSV still wanted, and on which route?** 짠7.3 shows `#376` does not stream, so the requirement
   survives ??but the copy route is refuted, `drop_subvi` one-call is unmeasured, 짠10 has no Abort/disk-full gate.
2. **Does 짠11e.2's narrow unfreeze cover the sentinel test's comparison primitive and literals inside a loop
   body?** PHASE "full" cannot be written without them. (OPEN 28)
3. Behind them: OPEN 16 the GPU tail (only bead 4); F1 60 s (**??.3 GB**) vs the user's 5 min (**??5 GB**).
?윟 MATERIAL: close `OpStopFromNode_v0`'s T5/T6 (narrative 짠3b names the two separators, one run each) ??
PHASE "full" against `tools/bench/build_d1_v0.json` (**109 terminals**) ??N1 ??F1 ??F2.

## Where to look
`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 `docs/toolkit-capabilities.md` 쨌 **`docs/d1-build-plan.md`
= the build order; relocation DONE, PHASE "full" open** 쨌 `tools/recipes/build_d1_v0.py` 쨌 `docs/gpu-backend.md` 쨌
`docs/pre-rig-master-plan.md` 쨌 the status archives.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Write is disabled here, so the review is delivered as text. No lock taken, nothing built, edited or run.

---

# PRIOR-ART REVIEW — `tools/recipes/diag_d1_full_route.py` (cycle 15, D1 PHASE "full", direction change)

**6 findings, 0 novel.**

---

## PART A — THE DIRECTION

### A1 `settled-already` — R1 is not a new join. It is `diag_d1_step0.py`'s own join, which already ran and PASSED

The plan proposes (`tools/recipes/diag_d1_full_route.py:44-45`) to close gap (i) by joining `main_vi_nodeterms.json` + `d1_step0_census.json.tunnels/.shift_regs/.panel` into a wire→source map, predicting 82/82. That join is already code, already ran, and already passed:

- `tools/bench/diag_d1_step0.py:357-358` — `resolved = {}  # wire -> {"kind":..., "detail":...}` with `tun_rows, sr_rows, panel_rows, ws_rows` — the same four inputs, same order.
- `tools/bench/diag_d1_step0.py:440-457` — what tunnels/SRs/panel cannot resolve falls through to `OpWireSource_v5`, recording `{"kind": "OpWireSource_v5", "owner_class":…, "owner_uid":…, "sinks":[…]}` — the driving object **and** every other sink of the net.
- `tools/bench/diag_d1_step0.py:631` — written as `"resolved_boundary"`; present at `tools/bench/d1_step0_census.json:4243`.
- **It passed.** `tools/bench/diag_d1_step0.log:18` — *"after tunnels/SRs/panel: **81/91 boundary wires resolved**; 10 left"*; `:21-22` the ten resolved individually; `:59` — *"**PASS G6 every boundary wire of the step-0 subject set is resolved** — unresolved on subject set: []; overall still open: []"*.
- The offline re-run R1 wants is already a flag: `diag_d1_step0.py:359-369` (`--offline` *"re-runs ONLY the classification, from the census this script wrote on its LabVIEW pass … re-measuring the same read-only facts to re-run 30 lines of graph code would be a LabVIEW batch for nothing"*).

A second, older implementation of the same join is `tools/bench/wiregraph_frame_loop.py:57-63` (`src[wire] → [(uid, term index, name)]` off `main_vi_nodeterms.json`), already parameterised by diagram (`:16`, `:27`), already gating one-source-per-wire (`:68`), and already documenting the gap the plan re-discovers (`:66-67`: *"A singleton (one side only) is an UNRESOLVED HALF-EDGE, not a proven boundary"*; 83 on diagram 43 — `docs/frame-loop-wire-graph.md:15`).

**Scope.** Covers R1 as *new* code and its `d1_rewire_sources.json` output. It does **not** cover re-running the resolution over the post-run-5 cut set: step 0 resolved 91 *pre-move* boundary wires, the current list is 82 cut wires (`archive/2026-09-17-status-d1-phase-full-narrative.md:130,:137`), and those sets are not proven identical. Re-running is legitimate — as `diag_d1_step0.py --offline` over the new list, not as new code.

### A2 — nothing refutes measuring before building

No archived exchange, retrospective or superseded section argues against inserting a measurement here. The claims it rests on are another matter → A3.

### A3 `contradicted` — two load-bearing sentences, one contradicted by the plan itself 18 lines later

**A3-i. "the only fleet writer that reaches a node on a NESTED diagram addresses a terminal BY NAME."**

- Plan: `diag_d1_full_route.py:15-16`. All of blocker (ii), and R3, rest on it.
- Its own file: `:31-33` — *"`connect2` (index-addressed sink on ANY diagram …)"*.
- Machine: `tools/gscript.py:2429-2431` — *"Wire top-level `Nodes[src_node].Terminals[src_term]` into `Nodes[sink_node].Terminals[sink_term]` of **ANY diagram** (… a loop's inner diagram included)"*; ladders at `tools/recipes/build_opconnect2.py:2-5`.
- Two more index-addressed writers reaching a **body node's** terminal, both absent from the census at `:31-35`: `tools/gscript.py:523-524,527-528` (`wire_sr` `LeftIn`/`RightIn`: *"`Terminals[term_index]` of `Nodes[node_index]` **INSIDE the loop body (Loop.Diagram)**" … "Indices are creation-order Nodes[] / Terminals[]"*), recorded as *"indices, never names"* at `docs/toolkit-capabilities.md:42`; and `docs/toolkit-capabilities.md:51` (`OpStopFromNode_v0`: *"`index 3` = body `Nodes[]` index, `index 4` = that node's `Terminals[]` index"*).
- Already written down this cycle: `archive/peer/2026-09-17-priorart-priorart-d1-build-rev4b.md:877` — *"every wiring op in the fleet addresses sinks through `Nodes[]→Terminals[]` (`tools/gscript.py:519-529` …)"*.

**Scope.** Covers `:15-16` and the framing of blocker (ii). It does **not** assert a nested→nested index-addressed writer exists — `:35`'s narrower claim is untouched.

**A3-ii. "PHASE 'full' is not executable as written."** The recipe this is a phase of says the opposite about the re-wiring: `tools/recipes/build_d1_v0.py:37-39` — *"(a) 8 queues + enqueue/dequeue + **element wiring** + tunnels + SR wiring + ControlTerminal moves + exit_while → **every op EXISTS and is verified** … the pattern is `tools/recipes/build_track_v6_queue.py` (162/162). **UNWRITTEN**."* Unwritten ≠ unexecutable. The recorded blocker is a different one, untouched by this run: `archive/2026-09-17-status-d1-phase-full-narrative.md:141-147` — the sentinel test's **comparison primitive and literals inside each loop body**, whose one untried route is *"`copy_by_index` with the D1 working copy as BOTH donor and target … followed by `move_in` … **it is the cheapest thing for the next cycle to test**"*.

### A4 `unread-evidence` — four documents that answer "what do I wire it to", none in the plan's "WHAT ALREADY EXISTS"

`diag_d1_full_route.py:22-38` names `main_vi_nodeterms.json`, `d1_step0_census.json`, `opconstvaluen_scan.json`, `move_in`, `wire_source`, `walk`. It does not name:

1. `tools/bench/diag_d1_step0.py` — the script that produced `.resolved_boundary`, which the plan cites only as *"wire → the boundary object that carries it"* (`:27-28`). The stored value is the driving object **plus every sink** (`diag_d1_step0.py:454-456`) — the map R1 says does not exist.
2. `tools/bench/wiregraph_frame_loop.py` (A1).
3. `docs/d1-build-plan.md:496-511` — `#5058`'s 16 terminals *with the object on the other end and its D1 carrier*; `:377-389` — all 14 shift registers with the node and terminal each inner wire reaches; `:402-410` — the 7 control terminals with their reader. And the D1 carrier for most cut nets is a **queue or a new tunnel** (`:537-556`), not the original's source object at all.
4. `tools/recipes/build_track_v6_queue.py` (162/162), named at `build_d1_v0.py:39` as the pattern for exactly this wiring.

---

## PART B — THE ARTIFACT

### B1 — no op does R1/R2/R3 under another name; but the *ladder* R3b uses was measured and rejected on 2026-09-13

No `OpTunnelConnect`/`OpRewire` exists in `claudeDev` (the tunnel family is `OpTunnels_v0`, `OpTunnelRead_v0`, `OpTunnelInd_v0` — readers plus one indicator-creator). But the ladder R3b uses to declare the 19 terminals unreachable is already measured as the wrong one:

`tools/gscript.py:1693-1698` — *"**WHY `create_indicator()` CANNOT DO THIS, measured 2026-09-13**: it addresses `Nodes[]→Terminals[]`, and a sweep of a For Loop's `Terminals[0..13]` produced **DANGLING** indicators for 0-7 … `ForLoop.Terminals[]` are the loop's own infrastructure terminals, and **a Tunnel is a GObject, not a Terminal**, so it inherits no Terminal methods. The documented route adds one hop … `Tunnel.'Outer Term' (6356001) → Terminal ref → Terminal.'Create Indicator' (6349C02)"*.

Both sides of every structure tunnel are already readable on that ladder — `docs/toolkit-capabilities.md:24` (`tunnels()`, 132 censused) and `:52` (`OpTunnelRead_v0`, verified on **both `#5540` output tunnels, 24/24**). A writer is the `6349C02 → 6349C03` swap on a front half proven twice (`tools/gscript.py:1690-1692`), the same additive shape as `OpStopFromNode_v0` (`docs/toolkit-capabilities.md:51`). ⚠️ That is a **new general-purpose op**, frozen for D1 (`tools/recipes/build_d1_v0.py:42-43`, citing `docs/cycle15-plan.md:104`) — a route to price, not a build to start.

**Scope.** Covers R3b's conclusion that the 19 terminals have no route. It does **not** claim a tunnel-terminal writer has been built or measured.

### B3 `helper-exists` — the terminal INDEX and the direction are already in the file the plan calls source-less

`tools/bench/build_d1_v0.json:137-144` stores each cut row as `[node_uid, term_index, name, is_source, wire]` (first row: `5540, 0, "", false, 5709`). So:

- **empty names** are not an addressing problem — the index is in the record, and every index-addressed writer above takes exactly `Terminals[index]`. The remedy is already written: `archive/peer/2026-09-14-stage2-a3-wire-shiftreg-plan.md:129` — *"Prefer terminal name plus direction where names are unique; **use terminal index only when duplicate or empty names force it**."*
- **`#5540`'s "duplicates"** are its outer/inner pair, disambiguated by `is_source`, which the file carries: `docs/frame-loop-wire-graph.md:17` — *"Nested structures' tunnels appear as terminals of the structure node with BOTH sides (outer wire on the source-flagged entry, inner wire on the sink-flagged entry) — observed on the case structure #5540"*. The `(name, is_source)` rule is this project's own recorded fix (`archive/peer/2026-09-14-opexitwhile-fail1-duplicate-terminal-names.md:24-29`), already imported by the sibling recipe: `tools/recipes/build_d1_v0.py:66-67` — *"**NEVER key a terminal by name alone**"*.

### B4 `already-measured` — an unnamed terminal has been wired by this fleet twice; both R4 separators re-derive recorded facts

**(i) R3's capability question.**
- `docs/toolkit-capabilities.md:35` — *"an EMPTY For loop's `Node.Terminals[]` has exactly one entry (**unnamed sink**) … an I32 source wired onto it makes the loop runnable"*, evidence `build_harness_copyloop2.log` run 2, **wire 346 on both ends, ExecState 0→1**; disposition `archive/peer/2026-09-14-copyloop2-forloop-terminals-unnamed.md:93-97`.
- An **unnamed source** terminal wired into a node on a **nested** diagram, by index, numerically accepted: `docs/keystone-op-spec.md:577-580` (`connect2(FIX,1,0,0,3,1)` / `(FIX,1,0,1,3,2)` — Decimate outputs 1/2, which `docs/NAMES.md:61` records as *"outputs unnamed"* — into the kernel inside the P=4 loop, ExecState 1), accepted at `:582-586`.

**(ii) R4's separators.**
- **T5sep**: `docs/NAMES.md:788` — *"**Never gate on `ExecState` while a required input is still unwired — it cannot discriminate.**"* With `.claude/skills/labview-automation/references/com-driving.md:206` (*"A node with unwired required inputs makes the VI BROKEN"*), explanation A is a standing rule, not an open question. The narrative's own recorded cheapest separator is cheaper than the plan's: `archive/2026-09-17-status-d1-phase-full-narrative.md:108` — *"**read the donor VI's connector pane** for required terminals, or repeat with a body node that has no required input"* — and the reader exists: `tools/gscript.py:2539-2542` (`conpane`).
- **T6sep**: the answer it must reproduce is published — `docs/toolkit-capabilities.md:48` (*"wire 10850 → constant 10739 / sink `Comparison` 10950, **12/12**"*) and the raw line `tools/bench/diag_d1_step0.log:21-22`.

**Scope.** Covers the separators as sources of *new information*. It does **not** forbid re-running T6sep as a **control** — `docs/toolkit-capabilities.md:213` requires exactly that, and this finding releases on that citation.

---

## The five questions, answered

1. **Yes** — `diag_d1_step0.py:440-457` → `d1_step0_census.json.resolved_boundary`, PASSED 91/91 (`diag_d1_step0.log:18,:59`); `wiregraph_frame_loop.py:57-63` is the same join per diagram. R1 is a re-run, not a build.
2. **Partly measured, and the route you missed is the Tunnel class.** Unnamed terminals have been wired by index twice (`toolkit-capabilities.md:35`; `keystone-op-spec.md:577-586`), and `gscript.py:1693-1698` measured that `Nodes[]→Terminals[]` is the wrong ladder for a tunnel, naming `Tunnel.Outer Term 6356001` as the right one. Ops absent from your census: `wire_sr` (`gscript.py:523-528`), `OpStopFromNode_v0` (`toolkit-capabilities.md:51`), `OpTunnels_v0`/`OpTunnelRead_v0`/`OpTunnelInd_v0` (`:24,:52`, `gscript.py:1685-1698`).
3. **T6's fact is published** (`toolkit-capabilities.md:48`, `diag_d1_step0.log:21-22`); **T5's confound is a standing rule** (`NAMES.md:788`) whose recorded cheapest separator is a `conpane()` read, not a built copy.
4. **Neither cited fact is contradicted.** `connect2`'s source side *is* top-level-only (`build_opconnect2.py:4`, `gscript.py:2429`); `wire()` *is* name-addressed with no index fallback (`gscript.py:1145,1174,1177`; `docs/NAMES.md:52` — `Wire Inputs.vi`: `Names`, `Inputs`). What is contradicted is the sentence you **derived** from them at `:15-16` (A3-i).
5. **The stated blocker is not the recorded blocker.** `build_d1_v0.py:37-39` says the re-wiring's ops all exist and are merely **UNWRITTEN**, with `build_track_v6_queue.py` (162/162) as the pattern; the recorded blocker is the sentinel comparison primitive + literals inside a loop body, whose one untried route (`copy_by_index` donor==target + `move_in`) this run does not test (`archive/2026-09-17-status-d1-phase-full-narrative.md:141-147`, STATUS OPEN 28).

---

```
PRIOR-ART: settled-already   (A1 — tools/bench/diag_d1_step0.py:357-358,:440-457,:631 + tools/bench/diag_d1_step0.log:18,:21-22,:59 + tools/bench/diag_d1_step0.py:359-369 + tools/bench/wiregraph_frame_loop.py:16,:27,:57-63,:66-67 vs tools/recipes/diag_d1_full_route.py:44-45 — covers R1 as new code and d1_rewire_sources.json; does NOT cover re-running the resolution over the post-run-5 82-wire set)
PRIOR-ART: contradicted      (A3-i — tools/recipes/diag_d1_full_route.py:15-16 vs :31-33 + tools/gscript.py:2429-2431,:523-528 + tools/recipes/build_opconnect2.py:2-5 + docs/toolkit-capabilities.md:42,:51 + archive/peer/2026-09-17-priorart-priorart-d1-build-rev4b.md:877 — covers the "only fleet writer / BY NAME" sentence and blocker (ii); does NOT assert a nested->nested index writer exists)
PRIOR-ART: contradicted      (A3-ii — tools/recipes/build_d1_v0.py:37-39 + archive/2026-09-17-status-d1-phase-full-narrative.md:141-147 vs tools/recipes/diag_d1_full_route.py:8-16 — covers "not executable as written" for the re-wire half; does NOT dispute that the list is source-less as stored)
PRIOR-ART: unread-evidence   (A4 — tools/bench/diag_d1_step0.py + tools/bench/wiregraph_frame_loop.py + docs/d1-build-plan.md:377-389,:402-410,:496-511,:537-556 + tools/recipes/build_track_v6_queue.py via build_d1_v0.py:39 vs tools/recipes/diag_d1_full_route.py:22-38 — covers the "WHAT ALREADY EXISTS" census)
PRIOR-ART: helper-exists     (B3 — tools/bench/build_d1_v0.json:137-144 + archive/peer/2026-09-14-stage2-a3-wire-shiftreg-plan.md:129 + archive/peer/2026-09-14-opexitwhile-fail1-duplicate-terminal-names.md:24-29 + tools/recipes/build_d1_v0.py:66-67 + docs/frame-loop-wire-graph.md:17 vs tools/recipes/diag_d1_full_route.py:14-16,:46-48 — covers R2's "unreachable" classification; the record already carries term_index and is_source)
PRIOR-ART: already-measured  (B4 — docs/toolkit-capabilities.md:35,:48 + archive/peer/2026-09-14-copyloop2-forloop-terminals-unnamed.md:93-97 + docs/keystone-op-spec.md:577-586 + docs/NAMES.md:61,:788 + .claude/skills/labview-automation/references/com-driving.md:206 + archive/2026-09-17-status-d1-phase-full-narrative.md:108 + tools/gscript.py:2539-2542 + tools/bench/diag_d1_step0.log:21-22 vs tools/recipes/diag_d1_full_route.py:55,:57-63 — covers R3b's capability question and both R4 separators as sources of NEW information; does NOT forbid re-running T6sep as a control per docs/toolkit-capabilities.md:213)
```

**The one that changes what happens next: A1.** The map R1 exists to build already exists, in a script with an `--offline` mode, and it passed on its subject set. The cheapest next step is to point `diag_d1_step0.py --offline` at the 82 post-move wires and spend the saved run on the blocker the record actually names (A3-ii).

## Sources

(extract from answer)

## What was done with it

**ALL SIX FINDINGS ACCEPTED. NONE REFUTED.** No citation was opened and shown not to cover its case, so nothing
here is released on the override route. Disposed 2026-09-17 08:5x by the material session that dispatched it.

The review's central correction is that my blocker (ii) was **my own derivation, not a fact about the fleet** —
and the derivation was wrong. Disposition per finding:

**FIXED: A3-i `contradicted` — "wire() is the only fleet writer reaching a nested diagram, and it addresses
terminals BY NAME".** Withdrawn. The fleet has **index-addressed writers that reach a body node's own
`Terminals[]`**: `tools/gscript.py:523-528` (`wire_sr` `LeftIn`/`RightIn` — *"`Terminals[term_index]` of
`Nodes[node_index]` INSIDE the loop body (Loop.Diagram)"*, recorded as *"indices, never names"* at
`docs/toolkit-capabilities.md:42`) and `OpStopFromNode_v0` (`docs/toolkit-capabilities.md:51` — `index 3` = body
`Nodes[]` index, `index 4` = that node's `Terminals[]` index). `connect2`'s SINK side also reaches any diagram by
index (`tools/gscript.py:2429-2431`). My sentence survives only as the narrower claim at `:35` — that no
**nested→nested** index-addressed writer exists — which the review explicitly leaves untouched.

**FIXED: B3 `helper-exists` — the 19 empty names are not an addressing problem.** `tools/bench/build_d1_v0.json`
stores every cut row as `[node_uid, term_index, name, is_source, wire]`, so **the index is already in the record**
and every index-addressed writer takes exactly `Terminals[index]`. The project's own rule was already written:
`archive/peer/2026-09-14-stage2-a3-wire-shiftreg-plan.md:129` — *"use terminal index only when duplicate or empty
names force it"*. And `#5540`'s 9 "duplicate" names are its **outer/inner pairs**, disambiguated by the
`is_source` flag the file already carries (`docs/frame-loop-wire-graph.md:17`). My R2 gate on "19 unreachable"
is deleted; the classification is rewritten as **addressing MODE (name vs index)**, which is not a blocker at all.

**FIXED: B4 `already-measured` — R3 and T5sep deleted.** An unnamed terminal has been wired by this fleet twice:
`docs/toolkit-capabilities.md:35` (an empty For loop's single **unnamed sink**, wire 346 on both ends,
ExecState 0→1) and `docs/keystone-op-spec.md:577-586` (`connect2` onto Decimate's **unnamed** outputs into the
kernel **inside** the P=4 loop, ExecState 1). T5sep re-derives a standing rule — `docs/NAMES.md:788`: *"Never gate
on `ExecState` while a required input is still unwired — it cannot discriminate."* **T6sep is KEPT, as a control
only**, which this finding's own scope note releases (`docs/toolkit-capabilities.md:213`).

**FIXED: A1 `settled-already` — R1 deleted as new code.** The join already exists and passed
(`tools/bench/diag_d1_step0.py:357-358,:440-457,:631` → `d1_step0_census.json.resolved_boundary`;
`diag_d1_step0.log:18,:59` 91/91), and `.resolved_boundary` stores the driving object **plus every sink**, which is
more than my `d1_rewire_sources.json` would have held. Per A1's own scope note the legitimate remainder is
**re-running the resolution over the post-run-5 82-wire cut set**, so the recipe now *joins the existing
`resolved_boundary`* to that set and calls `OpWireSource_v5` **only for what it does not cover** — measured
offline as exactly **w3268** (six sinks: `#376 frame index`, `#1114 index i`, `#2136`, `#3191`, `#10068`,
`#29240`; no source in nodes, tunnels, registers, constants or panel terminals).

**FIXED: A4 `unread-evidence`.** `tools/bench/diag_d1_step0.py`, `tools/bench/wiregraph_frame_loop.py`,
`docs/d1-build-plan.md:377-389,:402-410,:496-511,:537-556` and `tools/recipes/build_track_v6_queue.py` are now
named in the recipe's "WHAT ALREADY EXISTS" block. A4's fourth point is the one that matters most and I had
missed it: **for most cut nets the D1 carrier is a queue or a NEW tunnel, not the original's source object** —
so the source map is context, not the re-wire instruction.

**ACCEPTED, AND IT SETS THE NEXT RUN: A3-ii `contradicted` — "PHASE 'full' is not executable as written".**
Withdrawn. `tools/recipes/build_d1_v0.py:37-39` records that the re-wiring's ops **all exist and are verified**,
with `build_track_v6_queue.py` (162/162) as the pattern, and are merely **UNWRITTEN**. *Unwritten ≠ unexecutable*,
and my run would not have touched the **recorded** blocker at all:
`archive/2026-09-17-status-d1-phase-full-narrative.md:141-147` / STATUS OPEN 28 — the sentinel test's **comparison
primitive and the literals beside it, inside each loop body**, whose one untried route is *"`copy_by_index` with
the D1 working copy as BOTH donor and target … followed by `move_in`"*, called there *"the cheapest thing for the
next cycle to test"*. That route is authorised by `docs/d1-build-plan.md` §11f.2. **So the diagnostic is
re-pointed at it**, and that phase (P2) is the run this review bought.

**NOT REFUTED, recorded as a route to price, not to build (B1):** a tunnel-terminal writer is the
`6349C02 → 6349C03` swap on `Tunnel.'Outer Term' 6356001` — `tools/gscript.py:1693-1698` measured on 2026-09-13
that `Nodes[]→Terminals[]` is the **wrong ladder for a tunnel** ("a Tunnel is a GObject, not a Terminal"). That is
a **new general-purpose op**, frozen for D1 by `docs/cycle15-plan.md:104`, and is left frozen.
