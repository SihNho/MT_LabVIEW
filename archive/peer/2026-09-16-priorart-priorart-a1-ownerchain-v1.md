# priorart-priorart-a1-ownerchain-v1

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.9719  in 48 / out 42809 / cache-create 210372 / cache-read 3595338  (595s, 43 turn(s))
- **date:** 2026-09-16
- **outcome:** ANSWERED (600s)
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
THE BUILD UNDER REVIEW (cycle 11, Stage 3, Phase A1 ??second attempt).

NEW OP: `OpOwnerChain_v1.vi` in claudeDev, built by `tools/recipes/build_opownerchain_v1.py` (not yet run).
WHAT IT DOES: a UID of any object on a target VI's block diagram goes in; that object's OWNER's class name and
UID come out. It is the missing link in `docs/diagram-hierarchy.md:71-80` ("which diagram a STRUCTURE itself
lives on"), which blocks Phase A2-A4 and STATUS.md OPEN 1 (is the periodic auto-reset gated by `Auto-Reset`?
the period crosses the frame loop through LoopTunnel #10114 / #10177, so the decision is assembled OUTSIDE
diagram 43 and needs an owner chain to find).

HOW IT IS BUILT (donor surgery, no new nodes created at all):
  copy `OpWireSource_v5.vi` -> `OpOwnerChain_v1.vi`. That donor ALREADY contains the whole
  owner -> ClassName + cast(GObject) -> UID chain (wire 751 and everything downstream:
  nodes 163 `ClassName`, 1221 `To More Specific Class`, 1186 `UID`, 482 `ClassName`, 1554 `ClassName`).
  Only the SOURCE of that chain is wrong: it is the owner of an INDEXED WIRE TERMINAL. So:
  1. DELETE, by Traverse class `GObject`, index resolved from `report_all(target,"GObject")`, highest index
     first, each delete asserted by a before/after uid-set diff (`gone == {uid}`):
       the seven Wire-only nodes 1044 (To More Specific Class -> Wire), 145 (Property `Terms[]`),
       151 (Index Array), 157 (Property `Owner`), 1319 (`IsSource`), 1326 (`Wire`/Connected Wire),
       1329 (UID of the connected wire) ??AND the Wire object (expected uid 318) feeding node 241's
       `reference`, so that sink is bare. Then `remove_bad_wires_scripted`.
  2. CONNECT with `connect2` (terminal INDICES resolved by NAME from the sweep, not names passed as indices):
       R1  node 241 `reference`  <-  node 990 `GObject`   (the UID-addressed object)
       R2  node 241 `Owner`      ->  the `reference` of ALL THREE consumers of old wire 751: 163, 1221, 482.
  3. Gates: B1 copy ExecState 1 쨌 B4 none of the eight uids remain 쨌 B3a all four sinks bare BEFORE connecting
     (never connect into a wired sink) 쨌 B2 241.`reference` == 990.`GObject` wire 쨌 B3 241.`Owner` wire != 0 and
     equal to all three consumers' `reference` wires 쨌 B5 ExecState 1, save, reset, reopen, still 1 쨌
     B6 FUNCTIONAL against the main VI, read-only, md5 before/after: uid 10407 (CaseStructure) must report owner
     class `Diagram` uid 639 (`docs/diagram-hierarchy.md:46`, `docs/keystone-op-spec.md:593`), and a second
     recorded pair `ForLoop#1359` -> `Diagram` 639 (`docs/diagram-hierarchy.md:47`).
  4. `OpDelete_v1.vi` is deleted from claudeDev (STATUS: behaviourally identical to v0, measured A4 in
     `tools/bench/diag_delete_matrix.log`).

WHY THIS IS NOT A REPEAT OF THE v0 RUN (`tools/bench/build_opownerchain_v0.log`, 2 pass / 3 fail). Three
independent defects were measured today and each has a named fix here:
  (a) every edit was SILENTLY DECLINED because the target's front panel was never opened ??
      `gscript.ensure_loaded()` now does it inside all 26 mutating wrappers (`tools/bench/diag_delete_matrix.log`);
  (b) v0 passed terminal NAMES ("reference", "Owner", "GObject") to `connect2`, which takes terminal INDICES
      (`tools/gscript.py:2428` ??`index 3` / `index 5`); v1 resolves every index by name from the sweep;
  (c) v0 deleted `#1044` as class `SubVI` and died with "1044 is not in list" (the census says it is class
      `Function`); v1 deletes by base class `GObject` and asserts the class list contains all eight uids first.
  (d) v0 called `net_map` ~14 times (166 junk Invokes purged per pass); v1 uses ONE
      `node_terms_uid(target,0,n)` sweep (creator-free, drops no junk) and re-sweeps only after deletes and
      after connects.
  (e) node 482 ??the THIRD consumer of wire 751, predicted in
      `archive/peer/2026-09-15-priorart-ownerchain.md:117` and confirmed at `build_opownerchain_v0.log:143`
      (`consumers {163: 751, 1221: 751, 482: 1444}`) ??is in both the delete-bare check and the rewire list.

WHAT I BELIEVE AND WANT ATTACKED:
 - that no op already returns an arbitrary object's OWNER UID (report/report_all give the owner's CLASS only);
 - that `OpWireSource_v5` is still the right donor and that deleting its Wire front section is the whole change;
 - that deletes must come before connects because `connect2` into an already-wired sink re-routes and breaks
   the VI (`tools/gscript.py:2110-2111`);
 - that `GObject` is the right Traverse class for deleting a mixed set of Property/Function/IndexArray/Wire
   objects by index (`tools/bench/diag_delete_matrix.log` Part C swept the classes with open_panel);
 - that the B6 oracle values (10407 -> Diagram 639; ForLoop#1359 -> Diagram 639) are already measured twice and
   are a real answer rather than a self-check.


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
   `archive/peer/2026-09-16-priorart-master-plan-rev5.md`. ?좑툘 Gate hole recorded, not fixed: `guard_cycle.py`
   advises "change the plan instead" but accepts only `REFUTED:` ??a `FIXED:` form is the obvious repair.
2b. ??**Cycle-10 retrospective done, 7 VIOLATIONs, all answered.** Six slugs are at 4 occurrences across cycles
   7쨌8쨌9쨌10. Answers: `docs/violation-decisions.md` ??Round 2 (2 devices, 4 reasoned no-devices). Both devices are
   **built and tested**: the undisposed-review dispatch gate in `guard_peer.py`, and `audit_cycle.py` C4/C5 review
   cost. `violations.py` now compares decision **timestamps** (user: ??꾩뒪?ы봽 鍮꾧탳濡?怨좎튇??. Headline the
   retrospective found: **six reviews, 48 min 40 s, $28.55 ??and the declared reader never launched.**
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
  status: acquired
  owner: material/cycle11-A1
  since: 2026-09-16 18:00
  purpose: build+run tools/recipes/build_opownerchain_v1.py (OpOwnerChain_v1.vi); reads the main VI headlessly
           for the functional gate (rule 1d, md5 checked before/after); no original is modified, no hardware.
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

?뵶 **RE-RUN A1 as `build_opownerchain_v1.py`, and expect the `ensure_loaded` fix to carry most of it.** Do NOT
rebuild `OpDelete` ??that premise is dead, and `OpDelete_v1.vi` is byte-for-byte behaviourally identical to v0
(measured, A4 in `diag_delete_matrix.log`): the `wire_indicators` call that made it silently no-op'd. Delete it.

The A1 rewrite, all four changes justified by measurement or review:
1. **`ensure_loaded` is now automatic** in `connect2`/`delete_object`, so the silent declines should stop.
2. **Delete by Traverse class `GObject`**, resolving each uid's index from `report_all(target,"GObject")` ??this
   removes the `#1044` class question (`SubVI` vs `Node`) entirely instead of guessing it again.
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

**Verdict: 8 blocking findings. Two of them (the Remove-Bad-Wires placement and the `GObject` delete class) will break this build on its own evidence, and three more are prescriptions written in the reviews this plan is built on.** Three of the plan's five stated beliefs I release explicitly.

---

# PART A — THE DIRECTION

## A1 · SETTLED ALREADY

**Not a blocking finding, stated so it is on the record:** the direction is decided *in the plan's favour*. `STATUS.md` → "NEXT" → *"🔶 **RE-RUN A1 as `build_opownerchain_v1.py`**, and expect the `ensure_loaded` fix to carry most of it"*, and `docs/cycle11-plan.md:112-125` scopes Stage 3 as exactly this. Step 4 (delete `OpDelete_v1.vi`) is likewise already decided at `docs/cycle11-plan.md:65` and in STATUS's NEXT. No slug.

**(1) The STRUCTURE half of the justification is already answered on disk, and the review that said so was never disposed.**

The plan inherits `docs/diagram-hierarchy.md:71-80` — *"which diagram that structure itself lives on is not [known]"*. But:

> `tools/bench/diagram_tree_main.json:370-397` — diagram **43** `"owner": "WhileLoop"`, `uids` list contains **1359** (:389) and **10407** (:397).

`10407` appears in exactly one diagram's `uids` list (its other occurrence, `:2059`, is the `structures` → `CaseStructure` roster, not a second diagram). So for the five catalogued structure classes, *structure → home diagram* is a lookup in a file we already have. This was raised eleven months-of-cycles ago in your own prior-art layer:

> `archive/peer/2026-09-15-priorart-ownerchain.md:125` — *"The reviewed belief says the opposite—that structure→home-diagram is already available. The JSON supports that only for catalogued nodes, such as 10407 on diagram 43 … Thus the claimed availability is partial, not general."*

That review's "What was done with it" is still `(Claude fills in)` (`:137`), and `archive/peer/2026-09-16-priorart-priorart-cycle11-delete.md:477` records it as still unannotated.

**Scope, precisely:** this does *not* kill the op. I grepped `diagram_tree_main.json` for `10114` and `10177` — **no hits**, so OPEN 1's LoopTunnels are outside the JSON, and `docs/diagram-hierarchy.md:66-69` puts every FlatSequence link under an explicit "unverified" banner. **Release path:** say in the recipe's docstring that the structure case is a JSON lookup and that the op exists for tunnels, FlatSequence and uncatalogued classes. Cheap.

## A2 · REFUTED ALREADY

**(2) `remove_bad_wires_scripted` sits between the deletes and the connects. That exact placement was refuted on 2026-09-15, on this donor lineage, and it ate these same node uids.**

The plan: *"…each delete asserted by a before/after uid-set diff … Then `remove_bad_wires_scripted`. 2. CONNECT with `connect2`…"*

> `archive/peer/2026-09-15-optunnelread-removebadwires-ate-the-chain.md:18` — *"**REPAIR: no Remove Bad Wires anywhere inside the transient window** — delete, rewire, and only then clean up"*, after *"the unwired-sink dump after the retarget shows the terminal-reader chain disconnected (the **Owner node 157** and two more property nodes had lost their reference)"*
> `:26` (codex, confirming) — *"once the array input is removed, the element-output net can no longer resolve its … type; its downstream wires become broken and **eligible for removal**"* … *"the orphan set contains **Owner 157 and property nodes 1319/1326**"*
> `:47` — *"delete obsolete connections/node, **rewire the Index Array input before any cleanup**, then clean once"*
> `:55` — *"Run Remove Bad Wires **once, after the graph is complete**"*

Nodes 157, 1319, 1326 are three of the seven this plan deletes. After the deletions, the surviving chain (163 → 1221 → 1186 → 482 → 1554) has unfed `reference` inputs — the identical transient state — and the plan calls Remove Bad Wires while it is in it. **Still applies; nothing since has narrowed it.** Release path: move the call to the very end, after the connects, and keep the topology gates (B2/B3) *before* it, per `:60`.

## A3 · CONTRADICTED

**(3) "`GObject` is the right Traverse class … `diag_delete_matrix.log` Part C swept the classes with open_panel" — Part C never swept `GObject`.**

> plan: *"that `GObject` is the right Traverse class for deleting a mixed set of Property/Function/IndexArray/Wire objects by index (`tools/bench/diag_delete_matrix.log` Part C swept the classes with open_panel)"*
> `tools/bench/diag_delete_matrix.py:65` — `CENSUS_CLASSES = ["Constant", "Property", "Invoke", "SubVI", "IndexArray", "Wire", "ControlTerminal"]`
> `tools/bench/diag_delete_matrix.log:109-118` — the seven Part-C cells, one per class above. **No `GObject` row exists.**

The cited measurement covers seven concrete classes and says nothing about the base class the plan actually chose. It also contradicts the recorded fix for this same gate: `docs/cycle11-plan.md:120` — *"| B4 | `#1044` typed as class `SubVI` | **class `Node`** |"*, and `archive/peer/2026-09-16-ownerchain-b2-b3-failed-prediction.md:176` — *"`#1044`'s class: it is a *To More Specific Class* primitive, **enumerated only under `Node`**, never `SubVI`"*, confirmed by measurement at `tools/bench/diag_ownerchain_state.log:19` (`uid 1044 classes: ['Node']`). The plan's own evidence for `Function` (`tools/bench/census_opwiresource_v5.log:21`) is a *reported class name*, not proof that Traverse class `GObject` enumerates or deletes that object.

**(4) Citation defect, third repetition of the same one — release costs nothing.**

> plan: *"deletes must come before connects because `connect2` into an already-wired sink re-routes and breaks the VI (`tools/gscript.py:2110-2111`)"*
> `tools/gscript.py:2110-2111` — `if "modal dialog" not in str(e):` / `raise` — the exception handler inside **`move_object`**.
> The sentence is at `tools/gscript.py:2206-2207` — *"an already-wired **SINK** is not safe (LabVIEW re-routes and the VI breaks) — wire only unwired sinks."*

The claim itself is TRUE and I release it. But the pointer has now been wrong three times in a row: `:2084` (STATUS.md, `docs/cycle11-plan.md:136`) → "corrected" to `:2110-2111` (`archive/peer/2026-09-16-priorart-priorart-cycle11-delete.md:378, 476`) → actual `:2206-2207`. Fix the number in the recipe and in STATUS; no rework.

## A4 · UNREAD EVIDENCE

**(5) The b2b3 review prescribes a refresh of node 241 *between* R1 and R2. The plan's sweep policy does not have one.**

> plan: *"v1 uses ONE `node_terms_uid(target,0,n)` sweep … and **re-sweeps only after deletes and after connects**"*
> `archive/peer/2026-09-16-ownerchain-b2-b3-failed-prediction.md:99-108` — *"Therefore **refresh after R1**: `Property Items[]` … `Terminals[]` … terminal name … `Is Source?` … connected-wire UID. **Do not reuse a terminal index/reference captured before the reference class changed.**"*
> and `:95` — *"changing the reference class can invalidate property items that the new class does not support"*

R1 changes node 241's `reference` source from the `Wire.Terms[]` Index-Array element (class **Terminal**) to `UID to GObject Reference.vi`'s output (class **GObject** — `tools/bench/census_opwiresource_v5.log:191`, `t2 'GObject' wire 1081`). That is precisely the retype the reviewer warned about, and R2 then addresses the `Owner` terminal by an index resolved before it. Release path: re-sweep node 241 after R1 and resolve `Owner` from that sweep — or show in writing that the index is stable across the retype.

**(6) Only wire 318 is deleted. Wires 751 and 1081 are left to Remove Bad Wires, which was measured this cycle not to clear a bad wire.**

> `archive/peer/2026-09-15-opcaseframes-identify-before-delete.md:22` — *"NI documents that loose/broken wire branches **persist and require explicit removal** … searching for `Connected Wire == 0` after deletion is unreliable"*
> `:24` — *"**Explicitly delete the cached wire first.** … delete that reader, **delete the cached wire via `Generic.Delete`**, then connect"*

The plan deletes node 157 (source of wire **751**, whose three sinks are 163 / 1221 / 482 — `tools/bench/diag_ownerchain_state.log:57-59`) and node 1044 (sink of wire **1081** from 990 — `:60-61`), but names neither wire in its delete list. Its B3a gate ("all four sinks bare BEFORE connecting") then depends entirely on Remove Bad Wires clearing them, and this cycle already measured it failing to:

> `docs/cycle11-plan.md:104-105` — *"lands as a **bad wire** — wire uid 467 present, `ExecState 0`, **`remove_bad_wires` will not clear it**"*

Predicted outcome as written: B3a fails and the run stops with nothing built. Release path: add 751 and 1081 to the explicit delete list (both are single wire objects — 751's fan-out to three sinks is one object per `archive/peer/2026-09-16-ownerchain-b2-b3-failed-prediction.md:71`).

**(7) The delete *selection* is a cross-op Traverse index, which this project measured to be non-transferable — and the one sweep that could have validated it only ever used index 0.**

The plan resolves each delete index from `report_all(target,"GObject")` (op family `OpReportAll_v0`) and passes it to `delete_object`, which runs its **own** Traverse inside `OpDelete_v0`.

> `archive/peer/2026-09-15-opwiresource-fail5-traverse-index-order-mismatch.md:28` — *"**Do not assume indices from `OpReportAll_v0` select the same objects in `OpReport_v3`-derived operations.**"*
> `:29` — *"Do not assume a cached index remains stable across executions, reloads, **edits**, or sessions."* (this recipe edits between every resolution)
> `:30` — *"If index selection remains anywhere, **retain the UID identity gate on every read**."*

`diag_delete_matrix` did not close this: every cell hard-codes `vi.SetControlValue("index", 0)` (`tools/bench/diag_delete_matrix.py:177`), and its gate only checks class, not identity — `:237`, *"C1 no cell removed an object of a **DIFFERENT class** than asked for"*. So cross-op index agreement at non-zero indices is still unmeasured. The plan's `gone == {uid}` diff detects a wrong deletion only **after** it happens; `gscript.py:2036` is explicit that the argument is *"the `index`-th object of Traverse class `cls`"*, and `move_object`'s sibling docstring pins the order to a different reader — `gscript.py:2095`, *"(Traverse order, **same as `report()`**)"*, i.e. the per-object family, not `report_all`.

---

# PART B — THE ARTIFACT

## B1 · ALREADY BUILT

**Released:** no op returns an arbitrary object's owner UID. `report`/`report_all` carry the owner as a **class string** only (`tools/gscript.py:322`, `owner: cols["owner"][i]`; schema at `:302`), exactly as `archive/peer/2026-09-15-priorart-ownerchain.md:93-99` found, and nothing built since changes that. The plan's first belief survives.

**(8) For the motivating case the plan cites — OPEN 1's LoopTunnels — an op already resolves a UID to a Diagram UID.**

> `docs/toolkit-capabilities.md:49` — *"`OpTunnelRead_v0.vi` (`vi path`, **tunnel `UID`**, `term index` → inner wire, **frame diagram `UID`**, owner) | cast(`Tunnel`) → `Inside Terminals[]` 6356000 → Index Array → `Connected Wire`, **`Terminal.Diagram` 634A002 → `UID`** … row 43: both #5540 output tunnels, **24/24**"*
> `:24` — *"`tunnels(target, index)` | `OpTunnels_v0` | the index-th `LoopTunnel`: tunnel UID, IndexMode, **outer terminal (name / source? / wire)**, inner terminals as arrays … 132 tunnels censused"*

The plan justifies itself with *"the period crosses the frame loop through LoopTunnel #10114 / #10177, so the decision is assembled OUTSIDE diagram 43 and needs an owner chain"* — but two verified ops already address a tunnel by UID, give its diagram, and give its outer terminal and wire, and nothing in the plan says why they are insufficient. **Release path (likely available in one sentence):** state that `Terminal.Diagram` gives the *inner frame*, and that what OPEN 1 needs is the home diagram of the **node driving the outer terminal**, which no existing op reaches. Say it, and this releases.

## B2 · ALREADY FAILED

See findings (3) and (7): the v0 run's B4 failure (`tools/bench/build_opownerchain_v0.log:144`, *"delete #1044 (SubVI) raised: 1044 is not in list"*, final tally `:295, :299`) is being fixed with an untested base class rather than the class the record settled on (`docs/cycle11-plan.md:120`).

## B3 · HELPER EXISTS

Nothing over-broad to report. `connect2`, `delete_object`, `report_all`, `node_terms_uid`, `remove_bad_wires_scripted` and `save` are the right calls and the plan uses them. One prescription it does not use, recorded as the *safe* producer swap: per-sink `Wire.Disconnect Terminal` `6370C0D` (`archive/peer/2026-09-15-optunnelread-removebadwires-ate-the-chain.md:38-43`, registry entry `docs/NAMES.md:749`) — flagged there as needing functional verification first, so I do not treat it as an existing helper.

## B4 · ALREADY MEASURED

**(9) The plan's per-delete assertion `gone == {uid}` and `delete_object`'s own verify are incompatible with class `GObject`, and the collateral that breaks them is already measured.**

> `tools/gscript.py:2085-2087` — `gone = before - uids(target, cls)` … `if len(gone) != 1: raise RuntimeError(f"delete_object({cls}[{index}]): expected 1 object gone, got {len(gone)}")`
> `tools/bench/diag_delete_matrix.log:112` — deleting **one** SubVI removed *three* objects: `elsewhere={'SubVI': [990], 'Wire': [1068, 1208]}`
> `:115` — the ControlTerminal cell likewise: `elsewhere={'Wire': [106], 'ControlTerminal': [96]}`

Wires are GObjects, so under `cls="GObject"` those diffs are **visible** and `len(gone)` is 3, not 1 — the wrapper raises on the first such delete. Additional exposure the census never covered: `GObject` also enumerates Terminals — `tools/bench/probe_builder_artifact.log:6`, *"objects ADDED by net_map: {'Node': (8, 83), 'Invoke': (0, 75), 'Terminal': (60, 510), **'GObject': (85, 610)**}"* (610 ≈ 83 + 510 + the rest), corroborated by `docs/toolkit-capabilities.md:103` (*"`Terminal` 5763, `GObject` 10030"*). Deleting a node removes its terminals, and every one of them is in the `GObject` before-set. Release path: delete under a concrete class (`Node` for 1044, per the record), or change the assertion to `uid in gone` and state the expected collateral — but the wrapper's own `len(gone) != 1` raise must be dealt with either way.

**Released — the B6 oracle is sound and is not a self-check.** Both pairs are measured by methods independent of the op under test:
> `docs/keystone-op-spec.md:592-594` — *"**diagram 43 = the tracking WhileLoop 637's diagram** (**uid 639**; … the autofocus Case **10407**…)"*
> `docs/diagram-hierarchy.md:46-47` — `CaseStructure#10407` and `ForLoop#1359` each *"lives on **diagram 43**"*, *"each … confirmed by **two independent measurements**: the position-matched hierarchy, and the wire-graph slice"* (`:41-42`)
> `tools/bench/diagram_tree_main.json:389, 397` — both uids in diagram 43's list

**Released — premise (a).** `connect2` does call `ensure_loaded` (`tools/gscript.py:2432`), so the silent-decline fix does reach the connects, and `ensure_loaded` (`:1072-1089`) keeps `open_panel`, the only route measured to work.

---

```
PRIOR-ART: unread-evidence
PRIOR-ART: refuted-already
PRIOR-ART: contradicted
PRIOR-ART: contradicted
PRIOR-ART: unread-evidence
PRIOR-ART: unread-evidence
PRIOR-ART: unread-evidence
PRIOR-ART: already-built
PRIOR-ART: already-measured
```

**Cheapest release path:** findings (2), (6) and (9) are one edit each to the recipe's ordering and delete list — move Remove Bad Wires to the end, add wires 751 and 1081 to the explicit deletes, and drop class `GObject` for `Node`. Findings (1), (4) and (8) release in a sentence each of written argument. Finding (5) releases by adding one re-sweep; finding (7) releases only by a measurement or by moving the identity guard ahead of the delete.

## Sources

(extract from answer)

## What was done with it

**Five findings implemented in `tools/recipes/build_opownerchain_v1.py` before it was ever run, three released in
writing, two refuted.** Nothing here is an assertion without a file: every row names what changed or which line of
the citation fails to cover this build.

| # | verdict | disposition |
|---|---|---|
| 1 | unread-evidence | **ACCEPTED as scope, not as a blocker**, and written into the recipe's docstring: for the five catalogued structure classes `structure → home diagram` IS a lookup in `tools/bench/diagram_tree_main.json` (10407 at `:397`, 1359 at `:389`). The op exists for what that file does not hold — LoopTunnels (no hits for 10114 / 10177), the FlatSequence links `docs/diagram-hierarchy.md:66-69` marks unverified, and uncatalogued classes. The 2026-09-15 review it says was never disposed is now annotated in full. |
| 2 | refuted-already | **ACCEPTED, and it is the most load-bearing change.** `remove_bad_wires_scripted` no longer sits between the deletes and the connects; there is ONE call, after the connects, and a new gate **B3b** re-reads node 241's `reference` / `Owner` and all three consumers afterwards to catch exactly the failure `archive/peer/2026-09-15-optunnelread-removebadwires-ate-the-chain.md:18,26` recorded (its orphan set was Owner 157 and property nodes 1319/1326 — three of the seven nodes this build deletes). |
| 3 | contradicted | **ACCEPTED in full.** `diag_delete_matrix.py:65` does not contain `GObject`, so the plan's citation was wrong. Deletes now go by class **`Node`** for the seven nodes and **`Wire`** for the two wires — measured, not chosen: `tools/bench/diag_ownerchain_state.log:19-24` lists all seven under `Node` (1044 and 1221 ONLY there), which is also what `docs/cycle11-plan.md:120` settled on. |
| 4 | contradicted | **ACCEPTED.** The recipe now cites `tools/gscript.py:2206-2207` for "an already-wired SINK is not safe", and says in the same sentence that `:2084` and `:2110-2111` (which is `move_object`'s exception handler) are the two wrong pointers this project has repeated. |
| 5 | unread-evidence | **REFUTED — the code already does what `2026-09-16-ownerchain-b2-b3-failed-prediction.md:99-108` prescribes.** The finding reads the plan's prose ("re-sweeps after connects") as one sweep after ALL connects. The recipe calls `by = sweep()` immediately after R1 and resolves R2's node and terminal indices from that sweep, so no index survives node 241's reference retype. The prose was ambiguous; the build is not. |
| 6 | unread-evidence | **SPLIT. Wire 751: ACCEPTED** — it is now deleted explicitly (class `Wire`), with 318, before the nodes, so B3a's bareness no longer depends on Remove Bad Wires (`archive/peer/2026-09-15-opcaseframes-identify-before-delete.md:22-24`). **Wire 1081: REFUTED** — `tools/bench/census_opwiresource_v5.log` (nodes 11 and 12, `reference` wire 1081) shows 1081 also feeds Property Nodes 307 and 310, whose `reference` is a required input, so deleting it would break the op and cost the two indicators `UID 3` / `Class Name 5`; and R1 *branches* 1081 into node 241, a branch that preserves the wire uid per this same review's own citation at `2026-09-16-ownerchain-b2-b3-failed-prediction.md:71` — which is exactly what gate B2 asserts. Deleting it would falsify the gate it was supposed to protect. |
| 7 | unread-evidence | **ACCEPTED, and answered with a measurement rather than an argument** — new gate **B4b** compares `report(OP, cls)` and `report_all(OP, cls)` uid order for `Wire` and `Node` immediately before the deletes, and the run stops if they disagree. `archive/peer/2026-09-15-opwiresource-fail5-traverse-index-order-mismatch.md:28-30` asked for exactly this rather than a cached assumption; the per-delete `gone == {uid}` check stays as the identity gate, and the loop now STOPS on the first mismatch instead of continuing with guessed indices. |
| 8 | already-built | **REFUTED by its own citation.** `docs/toolkit-capabilities.md:49` describes `OpTunnelRead_v0` as `cast(Tunnel) → Inside Terminals[] → Connected Wire, Terminal.Diagram → UID` — the **inner frame** the tunnel opens onto. OPEN 1 needs the home diagram of the node **driving the outer terminal**, a different object that neither `OpTunnelRead_v0` nor `tunnels()` (`:24`, which returns the outer terminal's wire, not its driver's owner) reaches. The sentence the reviewer said would release this is now in the recipe's docstring. |
| 9 | already-measured | **ACCEPTED, via the reviewer's own first release path.** With `cls="GObject"` the collateral in `diag_delete_matrix.log:112,115` (`elsewhere={'SubVI': [990], 'Wire': [1068, 1208]}`) is visible and `len(gone) != 1` would raise. The build deletes under concrete classes, uses `verify=False`, and does its own **class-scoped** before/after diff, so cross-class collateral is outside the diff by construction; `GObject` also enumerating Terminals (`docs/toolkit-capabilities.md:103`) stops being relevant for the same reason. |

**Level of verification: structural only, and not even that until the run.** This annotation records what the
recipe now says, not what LabVIEW did — `tools/bench/build_opownerchain_v1.log` is the evidence.

REFUTED: unread-evidence - findings (5) and (6b). `2026-09-16-ownerchain-b2-b3-failed-prediction.md:99-108` asks
for a refresh between R1 and R2, and the recipe's `by = sweep()` after R1 (the sweep R2's indices come from) is
that refresh, so the citation does not cover this build; and `census_opwiresource_v5.log` nodes 11/12 show wire
1081 feeding the required `reference` inputs of Property Nodes 307/310, so "add 1081 to the delete list" would
break the VI and destroy the branch gate B2 exists to verify. Findings (1) and (7) are ACCEPTED and implemented
(scope sentence in the docstring; new gate B4b).

REFUTED: already-built - `docs/toolkit-capabilities.md:49` gives `OpTunnelRead_v0` the tunnel's INNER frame
diagram (`Terminal.Diagram` on an `Inside Terminals[]` element). OPEN 1 asks for the home diagram of the node
DRIVING the outer terminal, which is a different object; `:24` (`tunnels()`) returns that outer terminal's wire,
never its driver's owner. No existing op closes that hop.

**The other three slugs are released as FIXED, not refuted** (`guard_cycle.py` gained that form on 2026-09-16;
CLAUDE.md §"Review has THREE layers"). Each names the file the fix is in, and each file was changed after this
review:

FIXED: refuted-already - tools/recipes/build_opownerchain_v1.py:445 - finding (2): there is now ONE `remove_bad_wires_scripted` call and it runs AFTER the connects, with new gate B3b at :451 re-reading node 241's `reference`/`Owner` and all three consumers to catch the exact failure the cited 2026-09-15 exchange recorded.

FIXED: contradicted - tools/recipes/build_opownerchain_v1.py:176 - findings (3) and (4): deletes go by class `Node` (:176) for the seven nodes and `Wire` (:182) for the two wires instead of `GObject`, and the "an already-wired SINK is not safe" pointer is now `gscript.py:2206-2207` (:37 and the B3a stop message at :391).

FIXED: already-measured - tools/recipes/build_opownerchain_v1.py:363 - finding (9): the deletes run under concrete classes with `verify=False` and a class-scoped before/after diff, so `GObject`'s cross-class collateral can no longer reach a `len(gone)==1` check; the wire collateral that a Node-scoped diff cannot see is caught by the `wires_before` snapshot at :353 and gate B3c at :401.
