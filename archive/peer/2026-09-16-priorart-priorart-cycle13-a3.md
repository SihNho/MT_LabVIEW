# priorart-priorart-cycle13-a3

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $5.1239  in 56 / out 42363 / cache-create 206406 / cache-read 4000957  (588s, 44 turn(s))
- **date:** 2026-09-16
- **outcome:** ANSWERED (591s)
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
type: plan
status: current
date: 2026-09-16
cycle: 13
tags: [cycle-plan, diagram-hierarchy, A3]
---

# Cycle 13 ??A3: complete the 170-diagram hierarchy from the machine, replacing position matching

`docs/pre-rig-master-plan.md:66-72`, row **A3**: *"Complete the 170-diagram hierarchy ??the 41 unresolved plus
every FlatSequence link, replacing position matching (the diagram was Clean-Up'd, so position means nothing)."*
A3's dependency A2 is **DONE** (`docs/diagram-hierarchy.md`, "A2 ??OWNER SEMANTICS PER STRUCTURE CLASS";
`tools/bench/owner_semantics.json`; 54 gates pass / 0 fail).

## The judgement calls that opened this cycle, already taken (do not re-open)

The three calls A2 left under `STATUS.md` OPEN 9 were answered by the judgement session before this cycle started:

1. **A3 proceeds now, on the five clean classes, with `OpOwnerChain_v1` unchanged.** A2 measured that
   WhileLoop 쨌 ForLoop 쨌 CaseStructure 쨌 Sequence 쨌 EventStructure all return a non-zero owner uid AND complete the
   structure ??parent-diagram hop, with no error (`owner_semantics.json`, 14/14 rows).
2. **FlatSequence is handled TOP-DOWN, by measurement** ??asking the machine whether anything we already own
   returns a flat sequence's frames' diagram uids. It is **not** handled by modifying `OpOwnerChain_v1`, and
   **`ClassSpecifierConstant.AllTypes[]` is NOT built in this cycle** (`docs/NAMES.md:611-622`; it stays under
   OPEN ??it answers "is `FlatSequenceFrame` outside the `GObject` subtree?", which is a *why*, not the *link*
   A3 needs).
3. **STATUS OPEN 1's next read is the inputs of `ForLoop 1359`** ??A2 measured `LoopTunnel #10177 ??ForLoop#1359`
   and `ForLoop#1359 ??Diagram#639`, so the modulo remainder crosses into a For loop that sits on the frame loop's
   own diagram. What drives 1359's other input tunnels has never been read.

## Scope ??ONE diagnostic, read-only on the main VI, no op built or modified

`tools/bench/diag_hierarchy_a3.py`, one `MATERIAL=1` bgrun, main VI md5 `2a78e17c449cacdaf5da389818526859`
asserted **before and after**, lock block in `STATUS.md` held across the run. Every name resolved from
`docs/NAMES.md` and `docs/toolkit-capabilities.md` at planning time. **Nothing in `user.lib\claudeDev` is saved
except a scratch VI created and deleted in the same run (3b).**

### 3a ??the full hierarchy for the five clean classes

`g.report_all(MAIN,'Diagram')` returns all **170** diagram uids with their owner **class** in ONE op run
(`gscript.py:294`; the prior-art review of cycle 12 established this as the helper, deleting 18 op runs from A2).
For every diagram whose owner class is **not** `FlatSequenceFrame` and not `''` (the top-level diagram),
`OpOwnerChain_v1` runs twice: diagram ??structure uid, structure ??parent diagram uid. The structure ??parent hop
is memoised per structure uid, so the cost is ~112 + ~63 op runs, not 224.

Output: a machine table `diagram_uid ??structure_uid ??parent_diagram_uid` written to
`tools/bench/diagram_tree_a3.json`, plus a **diff against `tools/bench/diagram_tree_main.json` and
`tools/bench/diagram_hierarchy.json`** ??the position-matched tree A3 exists to replace: agree / disagree /
newly-resolved counts, with **every disagreement listed individually**.

**Prediction: 0 disagreements**, from A2's 14/14. A disagreement is a failed prediction and owes a peer review.

### 3b ??FlatSequence, top-down, and the branch has an explicit STOP

The 57 `FlatSequenceFrame`-owned diagrams cannot be walked upward: A2 measured owner uid **0**, `error 1055` and
an empty cast echo, twice, on two different diagrams (113 and 686). So the question is asked from the structure
end instead, on **3** of the 21 `FlatSequence` uids: does any reader or VI-Server property we **already own**
return that structure's frames' **diagram uids**?

Checked, in this order, and all of it is a read:
`docs/vi-server-ids.json` (it contains **no** frame/sequence entry) 쨌 `docs/toolkit-capabilities.md` 쨌
`subvis()` / `tunnels()` / `node_terms()` / `report_all()` 쨌 and `g.build_property(...)` used **only as an
attach test on a scratch copy**, because `OpBuildPN_v1` reports the creator's own error and an unsupported
property ID raises **1077** (`gscript.py:1989-2030`) ??that is a machine verdict on whether
`MultiFrameStructure.Frames[]` **6363801** (`docs/NAMES.md:841`) attaches to `VI Server:FlatSequence` /
`VI Server:MultiFrameStructure`, at the cost of one scratch VI.

**STOP condition, written in advance:** if no existing reader returns the uids and getting them would require a
**new op VI**, the branch stops there, the candidate property IDs go under `OPEN:`, and nothing is built. In
particular `OpCaseFrames_v0` **failed five times** and `pre-rig-master-plan.md:286` says do not retry it ??this
cycle does not.

### 3c ??where the 1055 comes from (one read)

On one `FlatSequenceFrame` case, read the error output of the node **upstream** of the cast ??the `Owner` property
node, label `errO` = `"error out 4"` (`tools/bench/opwiresource_v5_labels.json`) ??alongside `errCO`
(`"error out 10"`, the cast node's own error, first read in cycle 12). If the upstream error already carries 1055,
the cast **propagated** it; if the upstream is clean, the cast **generated** it. Facts only; no conclusion here.

### 3d ??STATUS OPEN 1: the inputs of `ForLoop 1359`

`ForLoop#1359` sits on `Diagram#639` (the frame loop's own diagram) and receives the PERIODIC modulo remainder
through input `LoopTunnel #10177`. Read **all** of 1359's tunnels with `g.tunnels()` (uid, direction from
`out_is_source` / `in_is_source`, outer and inner wire uids, `index_mode`), then `OpWireSource_v5` on each
**outer INPUT** wire to name its driving node's class, uid and label (`node_labels` for the label,
`panel_wiring` / `fp_labels` for a control's name). Membership of a tunnel in 1359 is established by
`OpOwnerChain_v1` on the tunnel uid, never by position.

Reported: which sources are `ControlTerminal` (and whether any is labelled `Auto-Reset`), which are
`Function`/`And` nodes. **Facts only ??what it means for "is the PERIODIC auto-reset gated by `Auto-Reset`?"
goes under `OPEN:` for judgement.**

## Gates this cycle passes through first

1. Cycle-12 **retrospective** (`tools/audit_cycle.py --cycle 12` + `tools/retrospective.py --cycle 12`), every
   `VIOLATION:` line disposed, `py tools/violations.py --due` clean. If a slug is DUE, the device for it is the
   next cycle's first work and A3 does not run.
2. **Prior-art review**, trigger `cycle-start`, slug `priorart-cycle13-a3`, released only by `REFUTED:` or
   `FIXED:` lines with citations (`CLAUDE.md`, "Review has THREE layers").

## Files this cycle expects to touch

`docs/cycle13-plan.md` 쨌 `tools/bench/diag_hierarchy_a3.py` 쨌 `tools/bench/diagram_tree_a3.json` 쨌
`tools/bench/diag_hierarchy_a3.log` 쨌 `tools/bench/retro_cycle12.log` 쨌 `docs/diagram-hierarchy.md` 쨌
`docs/NAMES.md` 쨌 `STATUS.md` 쨌 `archive/peer/` (this cycle's reviews).

## Out of scope, deliberately

No op VI is built, modified or saved. `ClassSpecifierConstant.AllTypes[]` is not built. `OpCaseFrames_v0` is not
retried. A4 (the frame loop's true membership) waits for A3's table. No hardware, no GUI action.


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-16
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.

## ?좑툘 ONE SESSION AT A TIME

Two Claude sessions ran concurrently on 2026-09-16 and both edited the active documents; the second session's copy
of `CLAUDE.md` was stale for its whole run. Before starting: check for another live session, and **re-read
`CLAUDE.md` and this file from disk** rather than trusting a summary.

## START HERE

1. **`docs/pre-rig-master-plan.md` is THE plan** (`docs/cycle10-plan.md` is superseded ??it is that plan's Phase A).
   Settled decisions that must not be re-opened: **`docs/decisions.md`**.
2. ??**Gate: prior-art layer OPEN, rev6 NOT bought.** All 13 rev5 findings accepted (none argued) and the plan
   corrected ??new rows 1.9 stop/shutdown, Phase A9, A10, two 2A rows, banners in `restructure-plan-4.6.md:42` and
   `rotor-scheduler-design.md:74-75`. `REFUTED:` lines + per-finding table: end of
   `archive/peer/2026-09-16-priorart-master-plan-rev5.md`. ??**Gate hole FIXED 2026-09-16**: `guard_cycle.py` now
   accepts a second release form, `FIXED: <slug> - <path>:<line> - <what changed>`, valid only if the path exists,
   was changed after the review (frontmatter date, else the file's stamp) and sits under "What was done with it".
   Tested 5/5 (valid releases 쨌 nonexistent path does not 쨌 pre-review mtime does not 쨌 wrong section does not 쨌
   FIXED+REFUTED mix). Both forms are in `CLAUDE.md` 짠"Review has THREE layers".
2b. ??**Cycle-10 retrospective done, 7 VIOLATIONs, all answered.** Six slugs are at 4 occurrences across cycles
   7쨌8쨌9쨌10. Answers: `docs/violation-decisions.md` ??Round 2 (2 devices, 4 reasoned no-devices). Both devices are
   **built and tested**: the undisposed-review dispatch gate in `guard_peer.py`, and `audit_cycle.py` C4/C5 review
   cost. `violations.py` now compares decision **timestamps** (user: ??꾩뒪?ы봽 鍮꾧탳濡?怨좎튇??. Headline the
   retrospective found: **six reviews, 48 min 40 s, $28.55 ??and the declared reader never launched.**
2c. ??**Cycle-11 retrospective DONE ??`archive/peer/2026-09-16-retrospective-cycle11.md`, codex, ANSWERED 258 s,
   and it fired ALL NINE slugs**, including the first-ever `judgement-in-material` (question 7's first use).
   Every citation was re-checked against the file named and all nine are **factually true**; the per-slug
   disposition is in that file's "What was done with it". `py tools/violations.py --due` now reports **two** slugs
   at threshold with no newer decision: **`scope-creep` (3)** and **`premature-build` (3)** ??the other seven are
   held below the line only by the round-2 decision blocks dated `2026-09-16 15:05`, which compare NEWER than a
   retrospective whose stamp is a bare date. Hardest verified fact: `priorart_cycle11.log` ran 16:24:00 ??16:31:07
   while `build_opdelete_v1.log` started **16:26:10** ??the build ran five minutes inside its own prior-art review.
3. ??**SOLVED ??the delete tool was never broken. Scripting EDITS are SILENTLY DECLINED until the target's FRONT
   PANEL HAS BEEN OPENED.** ?좑툘 **Say it that way, not "until the diagram is loaded"** ??that was an inference and
   it is now REFUTED by measurement (`tools/bench/diag_load_vs_editmode.log`, 2026-09-16, `rc=0 after 112s`,
   fresh copy of `OpFPLabels_v0.vi` per arm, same raw op, class `Property`, index 0):

   | first | delete |
   |---|---|
   | nothing | `4 ??4` nothing |
   | **read `VI.Block Diagram` (23C), the documented load primitive, NO window** | **`4 ??4` nothing** |
   | `OpenFrontPanel(activate=False)` | `4 ??3`, removed uid 115 |
   | 23C-loaded, panel-less, **`GObject.Move`** instead of Delete | `(853,300) ??(853,300)` did not move |

   What is **MEASURED**: only `OpenFrontPanel` makes an edit land; the decline is **general across mutator
   families** (Delete *and* Move), not delete-specific; `ensure_loaded()` therefore keeps `open_panel` and the
   name is a misnomer. What is **NOT established ??do not write it as if it were** (codex,
   `archive/peer/2026-09-16-load-vs-editmode-23c-r2.md`, ANSWERED 69 s): *"A2 did not establish diagram residency
   at mutation time??the separate loader returning creates an unload race"* ??NI closes a top-level VI's
   references when it goes idle, so the 23C-reading op may have taken the diagram back out of memory before the
   delete ran. **"Edit mode is the variable" is an inference, not a result.** Same file: no Open VI Reference flag
   pins the diagram (`0x01` = record modifications, `0x20` = hide dialogs), and a wire-count delta of 0 IS
   consistent with a successful branch.
   ?뵶 **The flag reader is at the 2-failure stop.** `Metrics:Block Diagram Loaded` = **292** and
   `Metrics:Front Panel Loaded` = **291** are verified to ATTACH (`build_property('VI Server:VI',??` ??terminals
   `DiagramLoaded` / `PanelLoaded`), but both attempts to build a reader around them died the same way
   (`tools/bench/diag_bdloaded_reader.log`): after `build_property` the VI is still **ExecState 1**, `connect2`
   DOES wire `reference` (wire uid 467) and the VI then goes **ExecState 0**, and `remove_bad_wires` does not
   clear it ??i.e. the branch from `OpReportAll_v0`'s `Open VI Reference.vi reference` into a `VI Server:VI`
   Property Node lands as a **bad wire**. Next move is codex's own design, and it is a BUILD, not a diagnostic:
   ONE op VI that reads 23C, reads `DiagramLoaded`, and deletes, holding the diagram ref live by data dependency,
   with no window ever opened.

   The A/B that put the call in 26 wrappers stands as a measurement ??`tools/bench/diag_delete_matrix.log`, same
   op / target / class / index, only `OpenFrontPanel(target)` differing:

   | | without | with |
   |---|---|---|
   | OpWireSource_v5 쨌 Property | 12 ??12, **nothing** | 12 ??**11** |
   | OpFPLabels_v0 쨌 Property | 4 ??4, **nothing** | 4 ??**3** |

   With it, **every class works** (Constant 쨌 Property 쨌 SubVI 쨌 IndexArray 쨌 Wire 쨌 ControlTerminal ??all
   removed exactly one, none removed an object of another class). The error cluster stayed `(False,0,'')` in
   *every* case, deleting or not: *"`Generic.Delete` has no semantic return value at all ??its contract is the
   side effect"* (codex). The mechanism was already in our code, in `open_panel`'s docstring, **2026-08-28**:
   *"silently declined (count unchanged, no error): the diagram is not fully in memory"* ??never generalised
   beyond `wire()`/`drop_subvi()`.
   ??**Fixed in `tools/gscript.py`**: new `ensure_loaded(target)` (idempotent, cached, cleared by `reset()`) now
   guards **26 mutating wrappers**; readers are deliberately untouched (they work unloaded, and the main VI is
   read constantly ??rule 1d).
   ?좑툘 **The old note "assume every `verify=False` delete did nothing" was WRONG** and is withdrawn: deletes
   against targets another operation had already opened *did* work ??`keystone-op-spec.md:527-529,짠33` records six
   node deletions and a 1,403-junk purge succeeding.
   ?뵶 **The same mechanism very likely explains A1's failures**: `build_opownerchain_v0.py` never calls
   `open_panel`, so its `connect2` calls were being declined too. A1 is **2 pass / 3 fail** (not "1 left").
   Reviews archived **and annotated**: prior-art cycle-11 (16 verdicts, 15 accepted), delete-silent-noop2 (codex),
   plus the earlier B2/B3, delete no-op and uid 9775 exchanges. Plan: `docs/cycle11-plan.md` **rev2**.

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  owner:
  since:
  purpose:
# last held by material/cycle12-A2, 2026-09-16 19:34-19:36: diag_owner_semantics.py (bgrun END rc=0 after 73 s,
# 54 gates pass / 0 fail). READ-ONLY: main VI md5 2a78e17c449cacdaf5da389818526859 before AND after (re-verified
# out-of-band after the run). No op built, modified or saved; no scratch VI. LabVIEW pid 23668 (started by
# fresh()) exited with its client - verified 19:36, no LabVIEW process.
# last held by material/cycle11-closeout, 2026-09-16 19:03-19:04: diag_ownerchain_hop.py (bgrun END rc=1 after
# 34 s, 8 gates pass / 3 fail - a REAL failed prediction, peer dispatched). READ-ONLY: main VI md5
# 2a78e17c449cacdaf5da389818526859 before and after. No op built, no VI saved, no scratch VI. LabVIEW pid 14952
# (started by fresh()) exited with its client - verified 19:0x, no LabVIEW process.
# last held by material/cycle11-A1-run, 2026-09-16 18:52-19:0x: build_opownerchain_v1.py (20 pass / 0 fail,
# 90 s, bgrun rc=1 is the regex false positive in OPEN 6) and diag_reset_gate_outer.py (rc=0, 46 s). Main VI
# md5 2a78e17c449cacdaf5da389818526859 BEFORE and AFTER both runs. OpOwnerChain_v1.vi saved (17 151 bytes),
# OpDelete_v1.vi deleted, no scratch VI left. Verified 19:0x: no LabVIEW process (both fresh() instances exited).
# last held by material/cycle11-A1, 2026-09-16 18:00-18:45: wrote tools/recipes/build_opownerchain_v1.py (NOT run -
# prior-art gate), 3 prior-art dispatches, and re-ran diag_save_persists.py (rc=0, 82 s, W2). No original opened,
# no hardware, no scratch VI left on disk. LabVIEW pid 5476 (started by the diagnostic's second fresh()) EXITED
# with its client - verified at 18:47, no LabVIEW process. Main VI md5 2a78e17c449cacdaf5da389818526859, the
# recorded baseline (docs/diagram-hierarchy.md:85), unchanged.
# last held by material/cycle11-loadmode, 2026-09-16 17:2x-17:4x: diag_load_vs_editmode.py (rc=0, 112s) +
# diag_bdloaded_reader.py (rc=1, 66s, 2-failure stop). LabVIEW pid 23084 left running, no scratch VIs on disk.
```

**Verified, not assumed:** no LabVIEW process at 15:4x ??the last diagnostic's instance (pid 14352) did **not**
exit with its client and was killed explicitly. So the old note *"a COM-launched LabVIEW with no panel exits with
its client"* is **not reliable**: always `tasklist | grep -i labview` and kill a stray rather than trusting it or
this file. Fresh instances sit at ~31,500 handles; use a unique scratch VI name per run, and delete the scratch in
the same run that creates it.

## HARDWARE ??permission follows the RIG STATE. Current state: **遺꾪빐 / DISASSEMBLED ??everything allowed**

| rig state | motors (PI 쨌 rotor 쨌 magnet) | **ASI piezo** | camera |
|---|---|---|---|
| **遺꾪빐 ??disassembled ??WE ARE HERE** | ??| ??| ??|
| 議곕┰ ??assembled | ??| ??| ??|
| ?ㅽ뿕以???experiment running | ??| ??| ??|

?좑툘 **The ASI carve-out is RETIRED** (user, 2026-09-16; quote and table in CLAUDE.md rule 1b). Do not re-introduce
"the piezo is the one exception", and do not reinstate the 2026-08-27 motor ban, from any older summary. **Only the
user announces a state change**; never infer one, and do not ask per incident inside a declared state.

Instruments: rotor counter **0** (not the old 100,000 baseline ??the original VI's first absolute move would be a
200-turn trip) 쨌 magnet motor full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz, never write
`BinningHorizontal`. **A camera session open RESETS ROI *and* exposure**, so the acquisition loop must apply the
contract itself (`tools/bench/camera_contract.py` reads and verifies; it cannot pre-set a later run).

**No beads while disassembled**, so bead-dependent acceptance waits. Fixture work is unaffected (10,043 frames,
`archive/bench-2026-09-07-fixture/`, 13 real lost-bead frames).

## Where things stand

**Stage 1 (analysis) CLOSED** ??`docs/` holds `instrument-libraries`, `main-vi-subvi-identity` (98 call sites, 0
mismatches), `main-vi-panel-map`, `main-vi-state`, `main-vi-startup`, `frame-loop-wire-graph`,
`rotor-sign-diagnosis`. Raw data: `archive/benchmarks/INDEX.md` rows 22??1.

**Stage 2 (assembly) IN PROGRESS**, cycles 1?? done (`docs/stage2-plan.md`, `stage2-assembly-step-{a,a3,b,c,e}.md`).
`Track_v6_CPU_core_v0.vi` 69/69 PASS (INDEX row 40) 쨌 `Track_v6_CPU_queue_v0.vi` 162/162 PASS (row 41).
**Say it exactly:** both are bit-identical to the reference for the **first 10,018 frames ??those before the first
bead loss**, not all 10,043, and both are **replay** artefacts: recorded TIFFs, `FOR` loops, no live acquisition,
no stop protocol.

**THE GAP (outcome review, 2026-09-15):** 168 op VIs, 116 recipes, 217 peer exchanges produced two replay VIs and
**zero runnable experimental VIs**. *"The next problem is not missing tooling; it is failure to cross the boundary
from replay proof to experiment product."*

## OPEN

1. ?윞 **Is the PERIODIC auto-reset gated by `Auto-Reset`?** It decides whether an hours-long dry run terminates
   itself on `Limit of Program`. Measured 2026-09-16 (`tools/bench/diag_reset_arm.log`): the period **enters** the
   frame loop through `LoopTunnel` #10114 and the remainder **leaves** through `LoopTunnel` #10177 ??the decision is
   assembled **outside diagram 43**, so it needs A1's owner chain. The lost-bead arm *is* gated, by `And` #9647.
   **?좑툘 CORRECTED 2026-09-16 19:5x (judgement, from the A2 owner reads below):** the modulo `Function` #10068 sits on
   **Diagram 639 = the frame loop's own body**; #10114 is an **input** tunnel of WhileLoop 637 (the period enters);
   #10177 is an **input** tunnel of **ForLoop 1359, which itself sits on 639**. So the remainder does not *leave*
   the frame loop ??the reset decision is computed **inside** it and fed into an inner ForLoop. "Assembled outside
   diagram 43" was wrong. Whether `Auto-Reset` gates it is now one read: the sources of ForLoop 1359's input
   tunnels (cycle 13, task 3d).
   ?좑툘 **A cheaper route may exist and has never been run** (prior-art review, 2026-09-16, rev3 finding 4 /
   rev2 finding 4): `tunnels()` gives #10114's **outer** terminal and wire, `OpWireSource_v5` gives that wire's
   **driving object's uid**, and `diagram_tree_main.json`'s per-diagram lists are net_map's FULL node lists (not
   just structures), so the driver's home diagram may already be a lookup. Two op runs. It does not remove the
   need for A1 in general (the JSON walk is capped at `max_nodes=120` per diagram and holds neither 10114 nor
   10177), but it might answer THIS question without it ??a scope call for a judgement session.
   ??**The cheap route has now been RUN ??`tools/bench/diag_reset_gate_outer.log`, 2026-09-16 19:0x, rc=0, 46 s,
   4/4 wires resolved, census agreement 2/2, main VI md5 unchanged. MEASURED WIRE SOURCES ONLY, no conclusion:**

   | wire | source (owner class, uid) | sinks |
   |---|---|---|
   | **9000** ??10114 outer, never read before | `('Diagram', 686)` | `('GrowableFunction', 8953)`, `('LoopTunnel', 10114)` |
   | 10103 ??10114 inner (re-read, agrees with `diag_reset_arm.log`) | `('LoopTunnel', 10114)` | `('Function', 10068)` |
   | 10187 ??10177's other side (re-read, agrees) | `('Function', 10068)` | `('LoopTunnel', 10177)` |
   | **10166** ??10177's remaining side, never read before | `('LoopTunnel', 10177)` | `('GrowableFunction', 8634)` |

   Against the script's own prediction contract: 10114's outer source matched **NEITHER** signature (class
   `Diagram`, i.e. a terminal owned by diagram 686 ??not a combiner, not one of `Terminal`/`ControlTerminal`/
   `Constant`); 10177's outer source matched the **GATED** signature by class alone (`Function` #10068 ??but that
   is the modulo itself, so the class test is not sufficient here). **What these two rows mean for "is the
   PERIODIC auto-reset gated by `Auto-Reset`", and which wire to read next, is judgement ??not written here.**

   ??**ONE MORE HOP ??`tools/bench/diag_ownerchain_hop.log`, 2026-09-16 19:03, `BGRUN END rc=1 after 34s`,
   8 gates pass / 3 fail, `OpOwnerChain_v1.vi`, main VI md5 unchanged. MEASURED, NO INTERPRETATION:**

   | uid asked | its own class (op self-read) | owner class | owner uid | error |
   |---|---|---|---|---|
   | **686** | `Diagram` | **`FlatSequenceFrame`** | **0 ??not returned** | `error 1055: Property Node in OpOwnerChain_v1.vi`; the op's cast-class echo came back **empty** (`''`), where the two rows below echo `'Diagram'` |
   | **8634** | `GrowableFunction` | `Diagram` | **7911** | none |
   | **8953** | `GrowableFunction` | `Diagram` | **686** | none |

   ?뵶 **The second hop was NOT reachable**: hop 1 returned owner uid 0, so "the owner of 686's owner" is
   unmeasured. Three predictions failed ??P1a (686 resolves with no error), P2 (686's owner is a structure or the
   VI; `FlatSequenceFrame` was not in the contract's list), P3 (the second hop returns). Mandatory peer review:
   the first dispatch **TIMED OUT at 180 s and told us nothing** (`peer_ownerchain-flatseqframe-1055.log`,
   `BGRUN END rc=2`); re-dispatched with `-TimeoutSec 700` and **ANSWERED in 147 s** ??
   `archive/peer/2026-09-16-ownerchain-flatseqframe-1055-r2.md`, annotated. (Saying only "dispatched" was the
   `unreported-fact` the cycle-11 retrospective caught; dispatch is not completion.)
   **Confirmed in our own code, and it is a measurement gap, not an opinion:** `read_owner()` reads
   `("errL","errT","errO","errU","errG")` (`build_opownerchain_v1.py:269`) and never reads **`errCO`**, the cast
   node's own error, which the labels file does define. So *"the cast to `GObject` failed"* is **implied, never
   measured**. Codex's hypothesis ??`FlatSequenceFrame` is a sibling of `GObject` under `Generic`, so it has no
   `GObject.UID` to read at all ??is **unverified** (labviewwiki, not the machine). Its cheapest discriminating
   test, not run: branch the RAW `Generic.Owner` with no cast and read `Class Name`, `Class ID`, and that owner's
   own `Generic.Owner` class name; predicted `FlatSequenceFrame` ??`FlatSequence`, no 1055.

   ??**THE THREE OWNERS ARE NOW READ ??`tools/bench/diag_owner_semantics.log`, 2026-09-16 19:34, `BGRUN END
   rc=0 after 73 s`, 54 gates pass / 0 fail, main VI md5 unchanged. MEASURED, NO INTERPRETATION:**

   | uid asked | its own class | owner class | owner uid | error |
   |---|---|---|---|---|
   | **10068** | `Function` (the PERIODIC modulo) | **`Diagram`** | **639** | none |
   | **10114** | `LoopTunnel` | **`WhileLoop`** | **637** | none |
   | **10177** | `LoopTunnel` | **`ForLoop`** | **1359** | none |

   For scale, from the same run: `Diagram#639`'s owner is `WhileLoop#637` ??the frame loop ??and `ForLoop#1359`'s
   own diagram is 7911, whose owner is `ForLoop#1359`??i.e. 1359 is a ForLoop that **sits on diagram 639**
   (`docs/diagram-hierarchy.md`, A2 table row ForLoop 7911 ??`ForLoop#1359` ??parent `Diagram#639`).
   **What this says about "is the PERIODIC auto-reset gated by `Auto-Reset`" is judgement and is NOT written here.**

   **Tunnel direction ??MEASURED, and the reporter is `g.tunnels()`** (`tools/gscript.py:747`; it already returns
   `out_is_source` for the outer terminal and `in_is_source` for the inner ones. `node_terms()` also reports
   `is_source` but is addressed by (diagram index, node index), which is recorded for neither tunnel, so
   `tunnels()` is the one that answers with the access index `main_vi_tunnels.json` already holds):

   | tunnel | outer terminal `Is Source?` (wire) | inner terminal `Is Source?` (wire) | index_mode | direction |
   |---|---|---|---|---|
   | **#10114** (idx 62, name `'# FD points'`) | **False** (9000) | **True** (10103) | 0 | data flows **INTO** the loop |
   | **#10177** (idx 33, name `''`) | **False** (10187) | **True** (10166) | 0 | data flows **INTO** the loop |

   ?좑툘 **Two corrections to the wording above, from the census the run re-verified (P5 passed 2/2):** for #10177
   the OUTER wire is **10187** and the INNER wire is **10166** ??calling 10166 "10177's outer wire" is wrong. And
   both tunnels measure as **input** tunnels, so "the remainder **leaves** through `LoopTunnel #10177`" is an
   inference the measurement does not support.
2. ?윟 **Autofocus decision path ??closed.** `CaseStructure #10407` fires on `(frame counter mod 25) == 0 AND
   NOT(Fix to a Certain Pattern)` ??**every 25 frames ??3.6 Hz at 90 Hz** ??and transacts serial when it fires.
   But `Fix to a Certain Pattern` is **written by code every iteration** (Property Node #1469) from
   `NOT( Auto-Focus AND NOT(reseed-And 9921) AND (counter < Limit of Auto-Focus) )`, so **the switch that stops the
   piezo is `Auto-Focus` (uid 24266)**, exactly as the user said. Derivation: `docs/camera-acquisition-facts.md`.
2c. ?윟 **uid 9775 READS the camera geometry ??and the size the VI WRITES is the FRONT-PANEL display area, not the
   camera ROI.** MEASURED 2026-09-16, both halves (the second confirms the user from memory: read the camera frame
   size, then set the IMAQ display size). Chain, divisor and caveats: `docs/camera-acquisition-facts.md`,
   "MEASURED 2026-09-16 ??uid 9775 READS the geometry". **Consequence: the plan?셲 1280횞1024 budget basis is safe.**
   ?좑툘 Do NOT widen it to "the VI does not set frame size" ??the codex review refuses that (archived, annotated);
   the residual test is `Property Items[] ??Is Write` across the 106 Property nodes. The fresh-session 640횞512 ROI
   reading stays **unexplained** and is a different thing from the 첨2 display size.
3. **19 archived reviews lack frontmatter and annotation** (audit A4 ??the cycle-10 audit counts **23**). The bulk
   `frontmatter.py` pass is safe to run now; the annotations are judgement work, not a formatting pass, and they
   are now the subject of a device (`violation-decisions.md`, Round 2, `repeated-failure-class`).
4. `Global motor pos.vi` ??write-only here; **user: a readability container covering all motors, keep it**.
6. ??**RESOLVED 2026-09-16 ??`tools/bgrun.py:56` regex narrowed.** The summary alternative is now
   `=== .*?\b[1-9]\d*\s+fail(?:ed|ure)?\b` (was `=== .*?\bfail(?:ed|ure)?\b`): a non-zero count must precede the
   word. The other two alternatives (`\b(?:exit|rc)\s*=\s*([1-9]\d*)`, `^\s*\*\*FAIL\*\*`) are byte-identical.
   The pattern is **not shared** ??`logclass.py` holds no failure regex, and `audit_cycle.py:53` /
   `guard_peer.py:67` have their own separate `FAILURE_RE`, untouched. Tested 11/11:

   | line | before | after |
   |---|---|---|
   | `=== OpOwnerChain_v1 build: 20 pass, 0 fail ===` | match (the bug) | **no match** |
   | `=== build: 17 pass, 3 fail ===` | match | match |
   | `=== build: 0 failed ===` / `=== build: 20 pass, 0 failure ===` | match | **no match** |
   | `=== build: 2 failed ===` 쨌 `probe exit=1` 쨌 `rc=2` 쨌 `**FAIL** ?? | match | match |
   | `-> FAIL  B2 ...` | **no match** | **no match** |

   ?좑툘 **Fact that corrects the brief:** `-> FAIL` was **never** a bgrun pattern ??bgrun only ever matched
   `**FAIL**` at line start. `^\s*(?:->\s*)?FAIL\b` lives in `audit_cycle.py:53` and `guard_peer.py:67`, and both
   still match `-> FAIL  B2 ...` (verified in the same test). Whether bgrun should ALSO gain that alternative is a
   widening, not a narrowing, and was not done.
7. ??**RESOLVED 2026-09-16 (cycle 12) ??both round-3 slugs answered and BOTH DEVICES BUILT AND TESTED.**
   `py tools/violations.py --due` now exits 0 with no output. The decisions are `docs/violation-decisions.md`
   round 3 (`2026-09-16 19:16`), both `DECISION: device`:
   - **`premature-build` ??`tools/hooks/guard_cycle.py:premature_build()`**, checked before the verdict gate (a
     review still in flight has no verdicts to refute, which is exactly the cycle-11 case). Refuses a RECIPE build
     while (a) a `tools/bench/priorart_*.log` newer than the newest retrospective has no `BGRUN END|TIMEOUT` line,
     or (b) no `archive/peer/*priorart*.md` is newer than the recipe FILE's mtime. **Tested 4/4 on fake files in a
     scratch tree**: running review ??REFUSED 쨌 ended review + archive newer than recipe ??ALLOWED 쨌 recipe edited
     after its review ??REFUSED 쨌 no priorart archive at all ??REFUSED.
   - **`scope-creep` ??`tools/audit_cycle.py` line C7** (counter, not refusal, by the decision's own wording):
     every file modified in the window not named in `docs/cycle<N>-plan.md` (`--cycle`, else the newest plan);
     excludes `archive/`, `tools/bench/*.log|json`, `.claude/`, and the plan file itself. First run:
     **62 files not named in `docs/cycle11-plan.md`**.
8. ??**RESOLVED 2026-09-16 ??`tools/bgrun.py` now skips the inner-failure scan for REVIEW logs**
   (`logclass.is_review_log(--log)`; the process's own exit code still decides). Measured both ways on the exact
   sentence from `retro_cycle11.log:102`: review-named log ??**`BGRUN END rc=0`** (was rc=1), build-named log ??
   **`rc=1` unchanged**, so no failure-detection capability was lost. The probe logs were deleted in the same run.
9. ?윟 **A2 IS DONE ??owner semantics measured for all six structure classes** (`tools/bench/diag_owner_semantics.log`,
   54/54, 73 s; table and the five numbered facts: `docs/diagram-hierarchy.md`, "A2 ??OWNER SEMANTICS PER STRUCTURE
   CLASS"). **Five classes behave exactly like `CaseStructure`** (diagram ??structure returns a non-zero uid; the
   structure ??parent-diagram hop returns, for the first time ever). **`FlatSequence` is the one exception**,
   reproduced on a second diagram (113, not just 686): owner class `FlatSequenceFrame`, uid **0**, `error 1055`,
   empty cast echo ??and `errCO` (the cast node's own error, read for the first time) carries **the same** 1055
   string while the op's `error out` stays empty. **Position matching agreed with the machine 14/14.**
   **Three judgement calls fall out of this and none was taken here:**
   (a) does A3 now proceed on the five classes and treat FlatSequence separately, or wait for the reader?
   (b) codex's uncast `Generic.Class Name` / `Class ID` / `Owner` test is still unrun ??and the prior-art review
   named a cheaper route nobody has cited: **`ClassSpecifierConstant.AllTypes[]`** (`docs/NAMES.md:611-622`)
   enumerates the VI Server classes **with their parents**, which answers "is `FlatSequenceFrame` outside the
   `GObject` subtree?" from the machine instead of from labviewwiki. Supporting evidence found the same day:
   the machine refuses `FlatSequenceFrame` as a *traverse* class with **error 1092** = "not in the VI Server
   GObject hierarchy" (`build_diagram_hierarchy_run3.log:8`; `docs/NAMES.md` corrected accordingly).
   (c) whether the 1055 in `errCO` is generated by the cast or propagated into it.
   ?좑툘 **brief pre-scripted: none** ??the brief asked only for the measurement, and the FlatSequence arm was
   predicted to fail from the earlier measurement, so gate FS passing is a reproduction, not a surprise.
5. **Startup drives instruments**, which is *allowed* while the rig is apart and becomes a hard blocker at
   assembly: ASI `Initialize` + `Move Axis to Position` on diagrams 10 and 88, position read on 12, PI init/`MOV`/
   `GOH`/`VEL` on 1/3/4/5 (`main-vi-startup.md:22-33`). Record what each run touched; excise only when the state
   changes, and then node-by-node in the build log (rule 1a).

## NEXT

?윞 **Judgement call first (cycle 11, stage "load vs edit mode"):** the operational rule is settled and unchanged ??
edits need `open_panel`, so nothing in the fleet needs editing ??but the MECHANISM is open and the cheap route to
it is closed (flag reader at the 2-failure stop; see item 3). The remaining test is a BUILD: one op VI that reads
23C + `Metrics:Block Diagram Loaded` (292) + `Generic.Delete`, diagram ref held live by data dependency, no window.
**Is that worth a build cycle at all?** It changes no code; it changes what we write. A1 does not depend on it.

?윟 **SAVE WORKS ??measured 2026-09-16 18:41, `tools/bench/diag_save_persists.log` (`rc=0, 82 s`).** One
`delete_object(..., verify=True)` on a fresh donor copy returned `gone=[1319]`, the class count went `12 ??11`,
and after `save()` (18 021 bytes vs the donor's 18 163) **and a killed/restarted LabVIEW** the uid was still gone
and `ExecState 1`. **Verdict W2: saving is not the defect; v0's edits never happened.** This diagnostic had
aborted at 15:22 on the silent-decline bug and was never re-run ??the prior-art reviewer found that.

??**A1 IS BUILT AND WORKS ??`OpOwnerChain_v1.vi`, 20 gates pass / 0 fail, `tools/bench/build_opownerchain_v1.log`
(2026-09-16 18:52, 90 s).** Released by the three archives' new `FIXED:` lines. Nine deletes each returned exactly
the wanted uid; wire 1081 survived (B3c `{990,307,310} ??1081`); R1 gave 241.`reference` = 1081, R2 `Owner` wire
672 read by all three consumers 163/1221/482; junk purge `[154,151,148,145]`; `ExecState 1` before and after
`save()` (17 151 bytes) **and after a killed/restarted LabVIEW** (B5/B5b). **FUNCTIONAL, on the main VI read-only
(B6):** uid `10407 ??owner Diagram#639`, uid `1359 ??Diagram#639`, and `639 ??WhileLoop#637` ??the hop
`docs/diagram-hierarchy.md:36` predicted. `OpDelete_v1.vi` deleted (B7); main VI md5 unchanged (B8).
?좑툘 The runner said `rc=1` on a **passing** run: `tools/bgrun.py:56`'s inner-failure regex `=== .*?\bfail?? matches
the summary line *"=== OpOwnerChain_v1 build: 20 pass, 0 fail ==="*. A false positive in a device built the same
day; not patched here (see OPEN 6).

The A1 rewrite, all four changes justified by measurement or review:
1. **`ensure_loaded` is now automatic** in `connect2`/`delete_object`, so the silent declines should stop.
2. ?좑툘 **CORRECTED 2026-09-16: delete by class `Node` (nodes) and `Wire` (wires), NOT `GObject`.** The `GObject`
   prescription was never measured ??`diag_delete_matrix.py:65` swept seven concrete classes and not that one ??
   and it cannot work: `GObject` also enumerates Terminals (`toolkit-capabilities.md:103`, 10030 vs `Terminal`
   5763), so deleting a node removes objects inside the same class list and a `gone == {uid}` check can never
   hold. The `#1044` question is answered by measurement instead: `diag_ownerchain_state.log:13-19` lists all
   seven delete targets under `Node` (1044 ONLY there), which is also the class five existing recipes delete by.
3. **Deletes FIRST, then connects.** Removing the Wire-only front section leaves the three `reference` sinks bare,
   which is the only safe state to connect into. Node 241's `reference` needs its feeding **wire** deleted too.
4. **Node 482 is the third consumer of wire 751** ??predicted 2026-09-15 (`archive/peer/2026-09-15-priorart-ownerchain.md:117`), confirmed by `build_opownerchain_v0.log:143`
   (`consumers {163: 751, 1221: 751, 482: 1444}`), and missing from every fix list since.
5. **No `net_map`.** The v0 recipe walks it ~14 times through `nodes_by_uid()`; replace with one `node_terms_uid`
   sweep (creator-free, drops no junk).

??**CYCLE 12 (this one): both round-3 devices built and tested, the bgrun review-log false positive fixed, and
A2 measured.** Plan: `docs/cycle12-plan.md`. Prior-art review
`archive/peer/2026-09-16-priorart-priorart-cycle12-a2.md` (opus, ANSWERED 481 s, **8 verdicts / 7 slugs, all
accepted, none argued**) ??it deleted 18 op runs from the A2 script before it ran (`helper-exists`:
`report_all('Diagram')` returns uid + owner class for all 170 in ONE run), narrowed A2 to the two things genuinely
unmeasured (`contradicted`: the owner **uid** and the parent hop, not the owner class), cut the FlatSequence arm
from three instances to one, and added the `errCO` read. **After A2 comes A3** ??with the judgement calls in
OPEN 9 answered first.

**A7 is NOT next.** `pre-rig-master-plan.md:66-77` gives A7 `needs: A4, A6`, and A4?륚3?륚2?륚1; two of its three
audits are defined over A4's membership. The audits are also largely **already measured** ??the VISA census is
`motion-path-audit.md:30-99`, the UI-thread count is `g9-core-budget.md:32` (106 nodes, 88 implicit), reentrancy
property 288 and the `ASI_adjust focus-subvi.vi` instance are both on disk. **After A1 comes A2.**

## Where to look

`CLAUDE.md` rules 쨌 **`docs/decisions.md` settled decisions** 쨌 `docs/NAMES.md` verified strings 쨌
`docs/toolkit-capabilities.md` API 쨌 `docs/restructure-plan-4.6.md` target + stages 쨌
`docs/pre-rig-master-plan.md` the plan 쨌 `archive/2026-09-16-status-session-gate-and-autofocus.md` and
`archive/2026-09-16-status-cycles-8-10-narrative.md` the reasoning behind all of it 쨌
`archive/` history (rule 4: not read in normal work).


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Review complete — read-only; no lock, no build, no edits. `Write` is disabled in this session, so the review is delivered here as text for the dispatcher to archive.

# PRIOR-ART REVIEW — `priorart-cycle13-a3` (trigger: cycle-start)

Subject: `docs/cycle13-plan.md` (cycle 13, A3 — complete the 170-diagram hierarchy).

## PART A — THE DIRECTION

### A1 · SETTLED ALREADY — nothing blocking
The direction is decided **in the plan's favour** and no file retires it: `docs/pre-rig-master-plan.md:70` carries A3 with `needs: A2`, and A2 is closed (`docs/diagram-hierarchy.md:71-109`, 54 gates / 0 fail). No slug.

### A2 · REFUTED ALREADY — none for the direction
The *route* chosen for 3b has a refuted sibling (B2), but no file argues against completing the hierarchy from the machine. No slug.

### A3 · CONTRADICTED — four

**(i) `errCO` is NOT "the cast node's own error", so 3c cannot decide what it is written to decide.**

> `docs/cycle13-plan.md:76-79` — *"read the error output of the node **upstream** of the cast … alongside `errCO` (`"error out 10"`, the cast node's own error…)"*

> `tools/recipes/build_opwiresource_v4.py:108-109` — `pnCO = prop_node("VI Server:Generic", "6327803", "ClassName", …)` then `g.wire(OP, "Function", fi("Function", cast), "specific class reference", "Property", fi("Property", pnCO), "reference", branch=True)`; `:115` — `add_indicator(pnCO, "error out", "errCO", labels)`

`errCO` is the error of a **`Generic.ClassName` Property Node hanging off the cast's OUTPUT** — downstream of the cast. The cast is a `To More Specific Class` **Function** with **no error indicator anywhere in the op**. So both indicators 3c reasons over (`errCO`, and `errG` on the UID node) are downstream: "the cast generated it" and "a downstream node generated it" are not separable by this test. The mislabel is already propagated into `docs/diagram-hierarchy.md:99` and `tools/bench/diag_owner_semantics.py:114`.

**(ii) The `Auto-Reset` gating question is asserted closed in one active doc and held open in another.**

> `docs/camera-acquisition-facts.md:238-242` — *"the periodic auto-reset is real, it is driven by frame count, and **it is not gated by the `Auto-Reset` control**."*

> `docs/pre-rig-master-plan.md:224-227` — *"Until it is walked, "the periodic arm is ungated" and "it is gated somewhere outside" are both live, **so the plan may not assert either**."*

Both current, both 2026-09-16. 3d (`docs/cycle13-plan.md:90-91`) proceeds on the master plan's side — which I think is right — but one of the two documents is wrong and neither is listed for correction.

**(iii) An active doc still carries the claim STATUS has already corrected.**

> `docs/stage2-assembly-step-e.md:76-79` — *"remainder 10187 → **`LoopTunnel` #10177 — it LEAVES the frame loop**" … "**So the periodic term is assembled outside diagram 43**"*

`STATUS.md` OPEN 1 records the opposite from measurement (#10177 is an **input** tunnel of `ForLoop 1359`, which sits on diagram 639). That file is not in "Files this cycle expects to touch".

**(iv) "An unsupported property ID raises 1077" is not established for a valid ID on the wrong class.**

> `docs/cycle13-plan.md:65` — *"an unsupported property ID raises **1077** … that is a machine verdict"*

> `docs/toolkit-capabilities.md:226` — the measured 1077 came from a **deliberately bogus** id `FFFFFFF`. `:131` — `Control.Value` `633200D`, a **valid** ID: *"node created, property did not attach: no `Value` terminal"* — silently. `:233-235` — *"Whether `Control.Value` 633200D and `VI:Get Errors` 452 were walker artefacts or genuine 1077s is **now a one-call question each**."*

The fleet's robust check is the **data-terminal-name census**, already in use at `tools/bench/build_opcaseframes_v0.log:10-11`.

### A4 · UNREAD EVIDENCE

**`docs/frame-loop-wire-graph.md` is cited nowhere in the plan and already answers much of 3d:**
- `:440` — **#1359 t1** (wire **9097**) is fed by **left shift register 9018**, initialised by `#8953 Initialize Array` — not a control terminal.
- `:417` — **#1359 t2** (wire 9215) writes right register 8.
- `:264` — frame-loop input tunnel **28343** comes from `subVI Max Trans Pos.vi · Magnet position output` → **#1359 · `Magnet position output`**.
- `:236` — *"31 LoopTunnels belong to the frame loop (25 inputs, 6 outputs)"*; `:451` — the census covered *"all 132 tunnels of the VI"*.

**`docs/main-vi-panel-map.md` is likewise uncited, although `docs/NAMES.md:848-851` names it as mandatory** (*"Before building a reader for the main VI, read `docs/main-vi-panel-map.md`"*), and `docs/main-vi-panel-map.md:317` already pins `Auto-Reset` (uid 17472) to **wire 9806**. 3d's *"whether any is labelled `Auto-Reset`"* is a wire-uid membership test against a number already on disk.

## PART B — THE ARTIFACT

### B1 · ALREADY BUILT — not for 3a
3a (machine-read owner **uid** for the 112 non-FlatSequence diagrams) is new; the existing artefacts are what it replaces (`tools/bench/diagram_hierarchy.json`; `tools/bench/which_loop_owns_motor.log:4-22`, which stops at exactly the hop A3 supplies). No slug.

### B2 · ALREADY FAILED — 3b is the first step of the route that failed five times
The plan knows `OpCaseFrames_v0` failed (`docs/cycle13-plan.md:71`) but attributes it to the wrong step: the **attach passed in every run**; the failures were downstream.

> `archive/2026-09-15-status-stage2-cycles-1-7.md:536-539` — *"the op inherits a TERMINAL-reader chain from its donor and the Index Array now carries DIAGRAM references"*; `:544-547` — *"Still ExecState 0 … the SAME downcast trap one level up: the seed came from the MultiFrameStructure node"*

So 3b buys exactly one uncovered fact (does `6363801` attach to `VI Server:FlatSequence`); everything after it re-enters the recorded failure and the plan's STOP condition fires.

### B3 · HELPER EXISTS — two

**(a) 3d's membership step.** The plan sweeps `g.tunnels()` — a **VI-wide** access index over all 132 tunnels (`tools/gscript.py:747-754`) — then runs `OpOwnerChain_v1` per tunnel uid (`docs/cycle13-plan.md:84-88`). `tools/gscript.py:731-740` `node_terms_uid()` returns *"node_terms plus the node's own UID"*: one op run gives 1359's terminals with identity proof and no ownership walk. The rows are already on disk at `tools/bench/main_vi_nodeterms.json:12295-12333` (uid 1359, terms with `is_source` and wire uids).

**(b) 3a's ~63 memoised structure→parent hops.** `tools/bench/diagram_tree_main.json:3-29` keys each diagram by index with `owner` class and a `uids` node list, so *structure → home diagram* is a file lookup for catalogued structures. Raised twice, never disposed:

> `archive/peer/2026-09-15-priorart-ownerchain.md:125` — *"structure→home-diagram is already available … only for catalogued nodes … partial, not general."*
> `archive/peer/2026-09-16-priorart-priorart-a1-ownerchain-v1.md:334-342` — *"diagram **43** … `uids` list contains **1359** (:389) and **10407** (:397) … for the five catalogued structure classes, structure → home diagram is a lookup in a file we already have"*

Scope: does **not** cover FlatSequence, tunnels, or nodes past net_map's cap; re-measuring is defensible as verification — but the plan neither cites the file nor says why.

### B4 · ALREADY MEASURED — two

**(a) `MultiFrameStructure.Frames[]` 6363801 attaches — measured five times.**
> `tools/bench/build_opcaseframes_v0.log:9-11` — *"PASS exactly one new Property node (MultiFrameStructure.Frames[] 6363801) [1780]"* / *"exactly one data SOURCE terminal (Frames[])"* / *"CENSUS VI Server:MultiFrameStructure 6363801 -> data terminal 'Frames[]'"*; repeated at `:36-38`, `:61-63`, `:90-92`, `:120-122`.

The `VI Server:MultiFrameStructure` half of 3b is answered, and `docs/NAMES.md:841` ("short name UNKNOWN") is stale against this log. Only the `VI Server:FlatSequence` half is new.

**(b) `errO` is already read, and already came back dirty on this exact case.**
> `tools/recipes/build_opownerchain_v1.py:268-269` — `errs = " ".join(… for k in ("errL","errT","errO","errU","errG") …)`
> `tools/bench/diag_owner_semantics.log:96-98` — diagram 113: *"errs 'error 1055: Property Node in OpOwnerChain_v1.vi' cast '' errCO 'error 1055: …'"*

`errs` **excludes** `errCO`, so A2 already measured that one of `errL/errT/errO/errU/errG` carries the 1055. The only new information in 3c is **which** — so de-merge all five; `errG` (the UID node downstream of the cast) is the competing candidate and the one codex's mechanism predicts (`archive/peer/2026-09-16-ownerchain-flatseqframe-1055-r2.md:74` — *"that produces `Not A Refnum`; the downstream UID Property Node dereferences it and emits 1055"*). Reading `errO` alone does not settle it.

---

```
PRIOR-ART: contradicted        (A3-i  errCO is a downstream ClassName node, not the cast)
PRIOR-ART: contradicted        (A3-ii Auto-Reset gating asserted closed vs held open)
PRIOR-ART: contradicted        (A3-iii stage2-assembly-step-e.md:76-79 vs the measured correction)
PRIOR-ART: contradicted        (A3-iv 1077 is not a verdict for a valid ID on the wrong class)
PRIOR-ART: unread-evidence     (A4  frame-loop-wire-graph.md, main-vi-panel-map.md)
PRIOR-ART: already-failed      (B2  the Frames[] route = OpCaseFrames_v0, 5 runs)
PRIOR-ART: helper-exists       (B3a node_terms_uid for 3d membership)
PRIOR-ART: helper-exists       (B3b diagram_tree_main.json for structure -> parent)
PRIOR-ART: already-measured    (B4a Frames[] 6363801 attach on MultiFrameStructure)
PRIOR-ART: already-measured    (B4b errO already read and merged into errs)
```

**Cheapest way through, if it helps the release:** 3a stands (novel, and the plan's own cost note is sound); 3c should de-merge all five error indicators rather than read `errO` as if new, and should stop describing `errCO` as the cast's error; 3b should test only the `VI Server:FlatSequence` attach and cite the five `MultiFrameStructure` passes for the rest; 3d should start from `main_vi_nodeterms.json:12295` + `node_terms_uid`, and test the `Auto-Reset` question as "is wire 9806 among 1359's input wires".

## Sources

(extract from answer)

## What was done with it

**All ten verdicts accepted; none argued.** Every citation was opened and re-checked against the file named, and
every one of them is true. The plan and the diagnostic were changed before either ran — no LabVIEW run had
started when this review returned. Disposition, one line per verdict:

| verdict | what changed |
|---|---|
| `contradicted` A3-i | 3c rewritten: `errCO` is the `error out` of a `Generic.ClassName` Property Node **downstream** of the cast, and the cast has no error indicator at all, so the run cannot separate cast-generated from downstream-generated. The script now prints that caveat next to its own result |
| `contradicted` A3-ii | the withdrawn clause in `camera-acquisition-facts.md` |
| `contradicted` A3-iii | the struck claims in `stage2-assembly-step-e.md` |
| `contradicted` A3-iv | the attach test's verdict is now the data-terminal-name census, never "no 1077" |
| `unread-evidence` A4 | `main-vi-panel-map.md:317` (Auto-Reset → wire **9806**) and `frame-loop-wire-graph.md:440` (#1359 t1 ← `#8953 Initialize Array`) are now cited and used as the test, not re-derived |
| `already-failed` B2 | the `Frames[]` route is cut to ONE attach census; the frame-uid attempt uses `OpTunnelRead_v0`, a different and working op, and the STOP condition stands |
| `helper-exists` B3a | 3d's ~40-run ownership walk deleted; membership is `main_vi_nodeterms.json` + one `node_terms_uid` read |
| `helper-exists` B3b | `diagram_tree_main.json`'s `uids` lookup added to 3a as a third cross-check, with the reason for still measuring written down |
| `already-measured` B4a | `VI Server:MultiFrameStructure` dropped from the attach test; `docs/NAMES.md` corrected |
| `already-measured` B4b | 3c de-merges all eight indicators instead of reading `errO` as if new |

```
FIXED: contradicted-A3-i - docs/diagram-hierarchy.md:99 - the "errCO is the cast node's own error" sentence is struck and replaced with the measured build_opwiresource_v4.py:108-115 fact that errCO is a Generic.ClassName Property Node downstream of the cast, which has no error indicator at all.
FIXED: contradicted-A3-ii - docs/camera-acquisition-facts.md:242 - the clause "it is not gated by the Auto-Reset control" is WITHDRAWN and marked open-and-under-measurement, resolving the contradiction with pre-rig-master-plan.md:224-227.
FIXED: contradicted-A3-iii - docs/stage2-assembly-step-e.md:76 - "LoopTunnel #10177 - it LEAVES the frame loop" and "the periodic term is assembled outside diagram 43" are struck, with the measured owner_semantics.json rows (#10177 -> ForLoop#1359 -> Diagram#639, out_is_source False) written above them.
FIXED: contradicted-A3-iv - docs/toolkit-capabilities.md:232 - a warning now states that "no 1077" is not an attach verdict (the 1077 came from a bogus id; valid-id-wrong-class produced a terminal-less node silently) and that the data-terminal-name census is the check.
FIXED: unread-evidence-A4 - docs/cycle13-plan.md:120 - 3d now cites main-vi-panel-map.md:317 (Auto-Reset = wire 9806) and frame-loop-wire-graph.md:440, and tests Auto-Reset as wire-membership instead of re-deriving it.
FIXED: already-failed-B2 - docs/cycle13-plan.md:100 - the Frames[] arm is reduced to one attach census on the single untested class, the frame-uid route is stated to be OpTunnelRead_v0 and not OpCaseFrames_v0, and the STOP condition is kept.
FIXED: helper-exists-B3a - tools/bench/diag_hierarchy_a3.py:435 - part D's per-tunnel OpOwnerChain_v1 walk is replaced by main_vi_nodeterms.json diagram "43" node 16 plus one node_terms_uid read.
FIXED: helper-exists-B3b - tools/bench/diag_hierarchy_a3.py:201 - part A builds struct_home_from_tree from diagram_tree_main.json's per-diagram uids lists and diffs the machine's parent hop against it, with the file's partiality written in the comment.
FIXED: already-measured-B4a - docs/NAMES.md:841 - the "short name UNKNOWN" for MultiFrameStructure.Frames[] 6363801 is replaced with the measured terminal name Frames[], citing build_opcaseframes_v0.log's five passes; ATTACH_CLASSES in the diagnostic is cut to VI Server:FlatSequence alone.
FIXED: already-measured-B4b - docs/cycle13-plan.md:110 - 3c de-merges all eight error indicators and names errG as the competing candidate, instead of reading errO as if it were new.
```
