# priorart-priorart-cycle12-a2

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $5.1157  in 68 / out 34052 / cache-create 191640 / cache-read 4695234  (477s, 48 turn(s))
- **date:** 2026-09-16
- **outcome:** ANSWERED (481s)
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
cycle: 12
tags: [cycle-plan, owner-semantics, A2]
---

# Cycle 12 ??the two round-3 devices, then A2 (owner semantics per structure class)

Scope, in order. The devices come first because `guard_cycle.py` will not let a recipe run while a slug sits at
threshold, and because both were DECIDED ??not proposed ??in `docs/violation-decisions.md` (round 3, dated
2026-09-16 19:16). Nothing in this cycle re-opens those two decisions.

## 1. Device for `premature-build` ??`tools/hooks/guard_cycle.py`

Refuse a RECIPE build (command-position `tools/recipes/*.py`, the existing `BUILD_RE`) while either

* (a) any `tools/bench/priorart_*.log` newer than the newest retrospective carries no `BGRUN END` / `BGRUN TIMEOUT`
  line ??i.e. a prior-art review has not returned; or
* (b) no `archive/peer/*priorart*.md` is newer than the **recipe file's own mtime** ??no review has seen the text
  about to run, or the recipe was edited after the review that did.

Diagnostics (`tools/bench/*.py`), doc writes, peer dispatches and the reviews themselves stay open. The refusal
names the running log or the missing review. Tested against fake files in a scratch tree.

## 2. Device for `scope-creep` ??`tools/audit_cycle.py`

A new cost line (C7) listing every file under the project modified inside the audit window whose path is not named
in `docs/cycle<N>-plan.md` (N from `--cycle`, else the newest plan). Excluded: `archive/`, `tools/bench/*.log|json`,
`.claude/`. A **counter, not a refusal** ??the decision says so explicitly, because an out-of-plan change is
sometimes right and the verdict belongs to the retrospective; only the list is taken away from Claude.

## 3. `bgrun` false positive on REVIEW logs ??STATUS OPEN 8

`tools/bgrun.py` scans every line it pumps for an inner failure and has no review-log exclusion, so
`retro_cycle11.log:102` ended `rc=1` on the reviewer's own sentence quoting the OPEN-6 regex bug. Apply
`logclass.is_review_log(--log)` and skip the inner-failure scan for `peer_*` / `priorart_*` / `retro_*` logs; the
process's own exit code still decides.

## 4. A2 ??validate owner semantics per structure class  (`pre-rig-master-plan.md:69`)

**The measurement, and only the measurement.** The owner fact the walk depends on is scoped to `CaseStructure`
(`docs/NAMES.md:916-917`: a node's `Generic.Owner` is its frame **Diagram**, and that Diagram's `Owner` is the
**CaseStructure**). The VI holds **84 structures across six classes** ??3 WhileLoop, 17 ForLoop, 37 CaseStructure,
21 FlatSequence, 4 Sequence, 2 EventStructure (`docs/diagram-hierarchy.md:14-22`) ??so five of the six classes have
never been checked, and A3's 170-diagram hierarchy is built on the unchecked five.

Diagnostic script `tools/bench/diag_owner_semantics.py`, read-only on the main VI, md5 bracketed
(`2a78e17c449cacdaf5da389818526859`), one `MATERIAL=1` bgrun. It uses `OpOwnerChain_v1.vi` **unchanged**.

Per class, up to 3 instances, each measured as a three-read chain:

1. a node uid taken from a diagram that `tools/bench/diagram_tree_main.json` says is owned by that class ??
   its owner should be a `Diagram` (this is how a real sub-diagram **uid** is obtained; the tree stores diagram
   *indices*, not uids);
2. that Diagram uid ??its owner is the structure (class + uid) ??**this is the A2 question**;
3. the structure uid ??its owner should be a `Diagram` (the parent).

Round-trip against `diagram_tree_main.json`: the class measured at step 2 must equal the tree's `owners[i]` string
for that diagram index, and the structure uid must appear in `structures[<class>]` where that list exists (it lists
five classes; FlatSequence is absent from it, which is the round trip the plan names).

**The FlatSequence question, stated as a prediction and not as an action.** `diag_ownerchain_hop.log` measured
`Diagram#686 ??FlatSequenceFrame`, owner uid **0**, `error 1055`, empty cast-class echo; codex's review
(`archive/peer/2026-09-16-ownerchain-flatseqframe-1055-r2.md`) hypothesises `FlatSequenceFrame` is a sibling of
`GObject` under `Generic`, so it has no `GObject.UID` at all ??**unverified, from labviewwiki, not the machine**.
So FlatSequence-owned diagrams are predicted to reproduce the 1055 and terminate the chain. If they do,
**`OpOwnerChain_v1` is NOT modified in this cycle**: codex's uncast `Generic.Class Name` / `Class ID` / `Owner`
test is a separate BUILD and belongs under OPEN for the judgement session.

Also read here, because they are three reads on the same op and STATUS OPEN 1 is waiting on them: the owners of
**`Function` 10068**, **`LoopTunnel` 10114** and **`LoopTunnel` 10177** ??they settle whether the PERIODIC modulo
sits inside diagram 43.

**Interpretation is not part of this cycle.** The per-class table goes into `STATUS.md` and
`docs/diagram-hierarchy.md` as facts; what it means for A3, for STATUS OPEN 1, and whether the uncast reader is
worth a build cycle goes under `OPEN:` for judgement.

## Files this cycle expects to touch

`tools/hooks/guard_cycle.py` 쨌 `tools/audit_cycle.py` 쨌 `tools/bgrun.py` 쨌 `tools/bench/diag_owner_semantics.py` 쨌
`tools/bench/owner_semantics.json` 쨌 `docs/cycle12-plan.md` 쨌 `docs/diagram-hierarchy.md` 쨌 `STATUS.md` 쨌
`docs/toolkit-capabilities.md` 쨌 `archive/peer/` (the cycle's reviews).

## Out of scope, deliberately

A1 is done. A3 (the 170-diagram hierarchy) waits for A2's verdict. `OpOwnerChain_v1` is not rebuilt, the uncast
`Generic` reader is not built, and no op VI is created or saved in this cycle.


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
7. ?뵶 **Two slugs are DUE and the next RECIPE build is gated on them** (`guard_cycle.py`): `scope-creep` and
   `premature-build`, 3 each. Each needs a dated block in `docs/violation-decisions.md` (`DECISION: device` or
   `DECISION: no-device` + reason), newer than `2026-09-16-retrospective-cycle11.md`. **Not written by the
   material session** ??choosing device vs no-device is judgement. Diagnostics, docs and peers still pass the gate.
8. ?윞 **`bgrun` flags REVIEW logs on the reviewer's prose.** `retro_cycle11.log:102` ended
   `BGRUN END rc=1 (inner failure)` because the peer's answer quoted the very regex bug fixed in OPEN 6.
   `tools/logclass.py` already solves this class of error for `guard_peer`/`audit_cycle` (`REVIEW_LOG_RE` ??
   "a reviewer's prose is not a build's output"); `bgrun.py` has no such exclusion and scans every line it pumps.
   The cheap candidate is to skip inner-failure scanning when `--log` matches `logclass.is_review_log`. Not
   patched: OPEN 6's brief authorised narrowing ONE regex, and this is a second change to the same device.
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

Read-only review complete — no lock taken, nothing built, run or edited. (Write is disabled in this cell, so the review is the answer text below.)

**Headline: three of the cycle's four numbered items are already finished on disk, and the fourth (A2) rests on a premise our own measurement files contradict.**

---

## PART A — THE DIRECTION

### A1 `already-built` — items 1, 2 and 3 are already in the repository

**§1, the `premature-build` device.** `tools/hooks/guard_cycle.py:204-266` is a function named `premature_build()` implementing the plan's two conditions verbatim — (a) `:226-239` walks `tools/bench/priorart_*.log` newer than the newest retrospective and refuses while any lacks `BGRUN END`/`BGRUN TIMEOUT`; (b) `:251-265` refuses when no `archive/peer/*priorart*.md` is newer than the recipe file's own mtime. It is wired into the gate at `:310-312`, and `BUILD_RE` already carries the capture group it needs (`:40`, whose comment reads *"added 2026-09-16 for the `premature-build` device below"*). Diagnostics stay open exactly as §1 requires (`:221-222`).

**§2, the `scope-creep` C7 line.** `tools/audit_cycle.py:227-271` is C7: `--cycle` selects `docs/cycle<N>-plan.md`, else the newest plan (`:237-244`); exclusions are `archive/`, `.claude/` et al. (`:249`) plus `tools/bench/*.log|*.json` (`:256`); it prints a list and no verdict, and `:229-231` states the counter-not-refusal rationale in the decision's own words. The `--cycle` argument is at `:75-77`.

**§3, the `bgrun` review-log exclusion.** `tools/bgrun.py:69` is literally `scan_inner = not logclass.is_review_log(logp)`, with the OPEN-8 story at `:61-68`, the import at `:28`, and coverage of `peer_` / `retro` / `prior?art` / `outcome_review` / `audit_cycle` / `violations` at `tools/logclass.py:46-54`, `:61-63`. The plan's proposal *"Apply `logclass.is_review_log(--log)` and skip the inner-failure scan"* is the line already there.

What is **not** on disk is any record of §1's *"Tested against fake files in a scratch tree"* — no log under `tools/bench/` mentions `premature_build` or C7. That is a disposition question for the cycle audit, not prior art; the code exists.

**Cheap release:** strike items 1–3 from `docs/cycle12-plan.md` citing the three files, then one `FIXED: already-built - docs/cycle12-plan.md:<line> - …` under *"What was done with it"* — the plan edit post-dates this review, so the gate accepts it.

### A3 `contradicted` (i) — §3 and `STATUS.md` OPEN 8 assert a defect `bgrun.py` no longer has
- plan §3: *"`tools/bgrun.py` … **has no review-log exclusion**"*.
- `STATUS.md` OPEN 8: *"`bgrun.py` has no such exclusion and scans every line it pumps… **Not patched**"*.
- `tools/bgrun.py:69`: the exclusion, applied, `:61-68` naming OPEN 8.

STATUS OPEN 8 is stale, and it is the source the plan copied.

### A3 `contradicted` (ii) — §4's premise "five of the six classes have never been checked" is false at the class level
- `tools/bench/build_diagram_hierarchy_run3.log:2` `diagrams: 170`; `:9` `owner 'FlatSequenceFrame' -> class 'FlatSequence': 21`; `:12-36` prints each unresolved diagram **with its measured owner class**.
- `tools/bench/diagram_hierarchy.json` carries `"owner_class"` for every resolved diagram, spanning all six: `FlatSequenceFrame` `:7`, `Sequence` `:14`, `CaseStructure` `:21`, `ForLoop` `:42`, `WhileLoop` `:112`, `EventStructure` `:245`.
- `tools/bench/diagram_tree_main.py:52` stores the same string for all 170 into the `owners` array §4 proposes to round-trip against.
- Read from the machine, not inferred: `tools/gscript.py:261-281` fills `"owner"` from `Class Name 3`, i.e. `Generic.Owner`'s class — the very property A2 is about.

**Scope it precisely:** the owner **class** is measured for every diagram in all six classes, so gates P0, S1 and the class half of S2 re-derive a measured fact. Genuinely unmeasured: the owner **UID** (`report()` never returns it — our own `archive/peer/2026-09-15-priorart-ownerchain.md:68`) and step 3's structure→parent-diagram hop, which has never returned for any class (`tools/bench/diag_ownerchain_hop.log:7`). A2 should be narrowed to those two, not dropped.

### A3 `contradicted` (iii) — `NAMES.md` lists `FlatSequenceFrame` as a confirmed traversable class; the machine refused it
- `docs/NAMES.md:564-570`: *"Confirmed working on the main VI: … `Sequence`, **`FlatSequenceFrame`**, `EventStructure`."*
- `tools/bench/build_diagram_hierarchy_run3.log:8`: `probe class 'FlatSequenceFrame': … **error 1092** … Traverse for GObjects.vi->OpReportAll_v0.vi`; `:9` shows the working name is `FlatSequence`.

Load-bearing for §4: `docs/NAMES.md:578-590` explains that **1092 means the string is not in the VI Server GObject hierarchy at all** (the `PropertyNode` case). Our own machine has already produced evidence for the hypothesis §4 dismisses as *"unverified, from labviewwiki, not the machine"*.

### A4 `unread-evidence` — `docs/NAMES.md:611-622` is never cited
`:617-619`: *"**`ClassSpecifierConstant.AllTypes[]`** enumerates LabVIEW's VI Server classes programmatically — class IDs, parents, localized and unlocalized names. That is the way to stop guessing class strings entirely: read the list from the machine rather than from a palette label or a wiki."* That is the discriminating test for *"is `FlatSequenceFrame` a sibling of `GObject`, so it has no `GObject.UID`?"* — the question §4 defers to a future op build. `:578-590` is equally uncited, and `:624-628` is that section's own warning that not reading it has already cost one cycle.

---

## PART B — THE ARTIFACT

**B1 `already-built`** — as A1. Also `tools/bench/diag_owner_semantics.py` already exists on disk, complete, with its header at `:1-55`.

**B3 `helper-exists` — step 1 is unnecessary.** `diag_owner_semantics.py:11-13` justifies it: *"`diagram_tree_main.json` … stores diagram INDICES, never diagram uids, **which is why step 1 below exists at all**."* True of that file, false of the other: `tools/bench/diagram_hierarchy.json:5-9` stores `"diagram_uid"` **and** `"diagram_index"` **and** `"owner_class"` in the same index space, and `g.report(target,"Diagram")` (`tools/gscript.py:261-281`, catalogued `docs/toolkit-capabilities.md:104`) returns uid + owner class for all 170 in one call. Delete the node→Diagram hop and gate S1 with it.

**B4 `already-measured`.** `diag_owner_semantics.py:119-132` re-counts each class and gates on `{WhileLoop 3, ForLoop 17, CaseStructure 37, FlatSequence 21, Sequence 4, EventStructure 2}` — the table at `docs/diagram-hierarchy.md:16-24`, measured by `build_diagram_hierarchy_run3.log:3-9`. Defensible as a tripwire; label it as one rather than as A2 content.

**B2 `already-failed` — the FlatSequence arm reproduces a known failure with the explaining read still missing.** `tools/bench/diag_ownerchain_hop.log:7` already measured `Diagram#686 → 'FlatSequenceFrame'`, owner uid 0, `error 1055`, empty cast echo. §4 predicts up to **three** instances of exactly that with `OpOwnerChain_v1` **unchanged** — and unchanged means `read_owner` still reads only `("errL","errT","errO","errU","errG")` (`tools/recipes/build_opownerchain_v1.py:268-269`), imported verbatim at `diag_owner_semantics.py:65`. The cast node's own error already has a label on disk: `tools/bench/opwiresource_v5_labels.json:20` `"errCO": "error out 10"`. Cheapest fix: FS arm at **one** instance plus `errCO` in the tuple — no op change, no new build, and it does not pre-empt the judgement call on codex's uncast reader.

---

PRIOR-ART: already-built     (A1/B1 — guard_cycle.py:204-266 & :310-312; audit_cycle.py:227-271 & :75-77; bgrun.py:69 with logclass.py:46-54)
PRIOR-ART: contradicted      (A3-i — cycle12-plan.md §3 and STATUS.md OPEN 8 "Not patched" vs bgrun.py:69)
PRIOR-ART: contradicted      (A3-ii — "five of six classes never checked" vs diagram_hierarchy.json:7,14,21,42,112,245 and build_diagram_hierarchy_run3.log:2-9)
PRIOR-ART: contradicted      (A3-iii — NAMES.md:564-570 lists FlatSequenceFrame as traversable vs build_diagram_hierarchy_run3.log:8 error 1092)
PRIOR-ART: unread-evidence   (A4 — NAMES.md:611-622 ClassSpecifierConstant.AllTypes[]; NAMES.md:578-590 what 1092 means)
PRIOR-ART: helper-exists     (B3 — diagram_hierarchy.json:5-9 diagram_uid; gscript.py:261-281 report(); toolkit-capabilities.md:104)
PRIOR-ART: already-measured  (B4 — diagram-hierarchy.md:16-24 census re-gated at diag_owner_semantics.py:119-132)
PRIOR-ART: already-failed    (B2 — diag_ownerchain_hop.log:7 1055 reproduced 3×; errCO unread at build_opownerchain_v1.py:268-269 though labelled at opwiresource_v5_labels.json:20)

## Sources

(extract from answer)

## What was done with it

Dispatched at the cycle-12 start over `docs/cycle12-plan.md`; **ANSWERED in 481 s**, opus/high, 8 verdicts across
7 distinct slugs. **All eight accepted; none argued.** Four of them changed the A2 script before it was ever run,
which is the whole point of dispatching before the build.

| finding | verdict | what was actually done |
|---|---|---|
| A1/B1 items 1-3 already on disk | `already-built` | **True, and an ordering artefact**: the three devices were written before the review was dispatched and the plan still described them as future work. The plan now opens with a STATE block naming the three files and their line numbers. Nothing was rebuilt. |
| A3-i STATUS OPEN 8 + plan §3 assert a defect `bgrun.py` no longer has | `contradicted` | Correct and already half-fixed: `STATUS.md` OPEN 8 was rewritten to RESOLVED (with the two-way measurement) before this review returned; the plan's §3 is now in the STATE block as done. |
| A3-ii "five of six classes never checked" is false at the CLASS level | `contradicted` | **The most valuable finding — it narrowed A2 rather than killing it.** The owner *class* is measured for all 170 diagrams; what was never read from the machine is the owner **UID** (`report()` does not return it, so every diagram→structure uid we hold is POSITION-MATCHED, the thing A3 exists to replace) and the structure→parent hop. The script's gates were re-cut around those two, and the class checks are now labelled TRIPWIRE. |
| A3-iii `NAMES.md` lists `FlatSequenceFrame` as traversable; the machine gave 1092 | `contradicted` | Fixed in `docs/NAMES.md` with the log line and the working name (`FlatSequence`). It also **upgrades codex's FlatSequenceFrame hypothesis from wiki-only to machine-supported** — 1092 means "not in the VI Server GObject hierarchy", which is what that hypothesis predicts. |
| A4 `ClassSpecifierConstant.AllTypes[]` never cited | `unread-evidence` | Cited in the plan and **carried to OPEN**: it is the discriminating test for the class tree, and whether it earns a build is judgement, not a material call. |
| B3 the node→Diagram hop is unnecessary | `helper-exists` | **Taken: 18 op runs deleted.** `g.report_all(MAIN,'Diagram')` returns uid + owner class for all 170 in ONE run; the earlier draft's justification ("the tree stores indices, never uids") was true of one file and false of the toolkit. |
| B4 the census re-measures `diagram-hierarchy.md:16-24` | `already-measured` | Kept, relabelled `T1 TRIPWIRE` in the gate names themselves so it cannot be quoted as an A2 result. |
| B2 the FlatSequence arm reproduces a known failure 3× with the explaining read still missing | `already-failed` | Taken in both halves: the arm runs **once**, and `read_owner_plus()` now also reads **`errCO`** (`"error out 10"`), the cast node's own error that `read_owner` omits — so "the cast failed" stops being an inference. No VI was modified; it is one more read of an indicator the op already has. |

**Not done, deliberately:** `OpOwnerChain_v1` was not changed, and codex's uncast `Generic.Class Name` / `Class ID`
/ `Owner` reader was not built. Both are judgement calls under `STATUS.md` OPEN.

FIXED: already-built - docs/cycle12-plan.md:11 - a STATE block records items 1-3 as built and tested, with the reviewer's own file:line citations, instead of describing them as work to do.
FIXED: contradicted - docs/NAMES.md:572 - the traversable-class list no longer claims `FlatSequenceFrame` works; the 1092 measurement and the working name `FlatSequence` are recorded in its place.
FIXED: unread-evidence - docs/cycle12-plan.md:103 - `ClassSpecifierConstant.AllTypes[]` (NAMES.md:611-622) is cited as the discriminating test for the class tree and carried to OPEN.
FIXED: helper-exists - tools/bench/diag_owner_semantics.py:22 - the node->Diagram hop was deleted; diagram uids now come from one `report_all(MAIN,'Diagram')` run.
FIXED: already-measured - tools/bench/diag_owner_semantics.py:31 - the per-class census is relabelled T1 TRIPWIRE in the gate names, not presented as A2 content.
FIXED: already-failed - tools/bench/diag_owner_semantics.py:32 - the FlatSequence arm runs once instead of three times and now reads `errCO`, the cast node's own error.
