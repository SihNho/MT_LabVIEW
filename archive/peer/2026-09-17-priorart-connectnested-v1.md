# priorart-connectnested-v1

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $5.1763  in 46 / out 34856 / cache-create 244586 / cache-read 3717573  (489s, 37 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (493s)
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
# PLAN under review: `OpConnectNested_v1` (cross-diagram wire creator) + `OpTunnelSource_v0` (tunnel-source reader)

Context: `docs/d1-build-plan.md` 짠11p is the user's decision ??ONE last attempt at route A for D1. Two artifacts
are authorised, nothing else.

## Artifact 1 ??`OpConnectNested_v1.vi`

**Duty.** Wire a SOURCE terminal on nested diagram P into a SINK terminal on a DIFFERENT nested diagram Q, both
ends addressed purely by INDEX (`Diagram[i].Nodes[j].Terminals[k]`), because the terminals have no usable name.
`Terminal.Connect Wire` 6349C03 is the writer.

**What exists today.** `OpConnectNested_v0.vi` (built 2026-09-17, `tools/recipes/build_opconnectnested_v0.py`,
`docs/toolkit-capabilities.md` row 55) does this with BOTH ends constrained to the SAME nested diagram: it keeps
`OpConnect2_v0`'s sink ladder `Traverse('Diagram')[index] -> To More Specific Class -> AbstractDiagram.Nodes[]
6375809 -> IndexArray -> Node.Terms[] 6359000 -> IndexArray` and BRANCHES that one TMSC's `specific class
reference` into the source `Nodes[]` property node. Row 56 of the same file records the measured limit and its
claimed cause.

**Why v0 is limited, as recorded.** `build_opconnectnested_v0_run1.log:45` ??ROUTE A (a second `Index Array` on
`Traverse for GObjects.vi`'s `References` array feeding the source `Nodes[]` node directly) measured
`ExecState 0`: `References` is `GObject[]`, the property node is `Diagram`-class, and GObject -> Diagram is a
downcast. `docs/toolkit-capabilities.md:56` then states: *"A second TMSC has no creator: `New VI Object` makes no
primitive, and `copy_by_index` would land it with an unwirable `target class` (a class-specifier `Constant` is a
GObject, not a Node)"*, and `docs/d1-build-plan.md` 짠11n item 2 repeats it as **MEASURED "cannot be built"**.

**The plan, and the two claims it rests on.**

1. That "no creator" statement appears to be wrong on our own record, in two independent places:
   - `tools/recipes/build_opconstvalue_v1.py:171-199` **copies a `To More Specific Class` node** out of the NI
     example `Navigating Nodes and Wires.vi` with `copy_by_index(EX, "Function", i_tmsc, OP, ...)` and then feeds
     its `target class` from a **typed refnum CONTROL seed** created with `create_control` on the copied property
     node's `reference` (`wire_control(dst, [seed], "Function", i_tmsc, ["target class"])`, gate F2). So the
     `target class` input is NOT wired from a class-specifier Constant at all, and `docs/toolkit-capabilities.md:72`
     states the rule: *"`To More Specific Class`'s `target class` accepts ANY wire of the target type"*.
   - `C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting\` contains
     **`Create To More Specific Class.vi`** (listed 2026-09-17, 84 VIs). Every writer op in this fleet is a wrapper
     of a VI from that folder.

2. Therefore v1 = v0 + a SECOND cast, built additively:
   - copy a second `To More Specific Class` into the op (`copy_by_index`, the proven route);
   - feed its `target class` by BRANCHING the wire that already feeds the first TMSC's `target class` in
     `OpConnectNested_v0` (same target type on both sides ??both are diagrams), or from the same seed control;
   - feed its `reference` from a second `Index Array` on the same Traverse `References` array, with its own
     front-panel index control (`create_control`);
   - its `specific class reference` -> the SOURCE `Nodes[]` property node's `reference` (replacing the branch
     from the first TMSC).
   - Gate: `ExecState 1`, then a functional test on a scratch: body(loop A) -> body(loop B), ExecState 1, same
     wire uid on both ends; and into an unnamed tunnel of a CaseStructure nested inside A.

3. Codex's API answer (`archive/peer/2026-09-17-nested-diagram-terminals.md`, `-Kind fact`, ANSWERED) says the
   downcast `GObject -> AbstractDiagram` is ONE cast, that `Nodes[]` is owned by `AbstractDiagram` (6375809, an ID
   already in `docs/vi-server-ids.json`), and lists five CODE-GENERATION causes for an ExecState 0 after adding a
   second ladder: wrong class-specifier configuration, wrong terminal index on the TMSC, a property node
   configured for another class, an alternate/localized property name, and the Index Array output wired past the
   downcast. The build rules each out by measurement (reading back the TMSC's class, its terminal names, the
   property node's data-terminal name, and the wire uid on both ends of every connection).

## Artifact 2 ??`OpTunnelSource_v0.vi`

**Duty.** For a `LoopTunnel`/`Tunnel` given by index or UID, return what feeds it from OUTSIDE:
`Tunnel.Outside Terminal` 6356001 -> `Terminal.Connected Wire` 634A000 -> `Wire.Terminals[]` 6371003 ->
per terminal `Terminal.Is Source?` 634A003 + `Generic.Owner` 6327806, plus `ControlTerminal.Control` 6353000
when the owner is a diagram (a ControlTerminal's Owner is its diagram, not a node).

**Why.** `docs/d1-build-plan.md` 짠11L: of 66 re-wire rows in run 7, 24 had NO ROUTE and 17 of those are
`from-tunnel` rows; 짠11n item 3 says **16 of the 17 print `outer_source (none)`** ??a source-RESOLUTION gap.
`tools/bench/d1_rewire_sources.json` is the map, `tools/bench/d1_step0_census.json` the oracle for 3 known rows.

**What exists today.** `tunnels(target, index)` / `OpTunnels_v0` (row 24) already returns the outer terminal's
name / is-source? / wire. `OpWireSource_v5` (row 48) resolves "which object drives a wire" from a wire UID and is
recorded as returning **error 1055 for every wire** in one control (`diag_d1_full_route` T6, STATUS OPEN 28c).
`OpOwnerChain_v1` (row 49) gives owner class + owner UID from any UID. The plan is an ADDITIVE build on
`OpTunnels_v0`/`OpWireSource_v5` rather than a new family.

## What the review is asked to check

Only "has this already been done here": whether either artifact already exists under another name, whether either
has already been attempted and failed (and whether this plan repeats that cause), whether the "no TMSC creator"
claim in `toolkit-capabilities.md:56` / 짠11n is contradicted or corroborated elsewhere in our files, whether
`OpWireSource_v5`'s 1055 has a recorded cause that this plan would walk into, and which existing document should
obviously have been read for this direction.


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-17
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.
Narrative ??the `archive/2026-09-17-status-*.md` set (**`??d1-full-build-5.md` = the latest session**)
+ `archive/2026-09-16-??. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this.

## START HERE
1. **`docs/pre-rig-master-plan.md` is THE plan**; decisions **`docs/decisions.md`**; cycle `docs/cycle15-plan.md`;
   **build plan `docs/d1-build-plan.md` (REV 4 + 짠11c?벬?1m)** ??짠5/짠5a-bis (moves), 짠10 (S/N1/F1/F2), **짠11m is
   MEASURED UNBUILDABLE as written, OPEN 33**. 2. ?좑툘 A prior-art dispatcher's log MUST be named `priorart_*` /
   `peer_*` (`tools/logclass.py`) or the guards read the reviewer's prose as a build failure. 3. ??Scripting EDITS
   need the target's FRONT PANEL open. 4. ??A fixed op PATH is served from LabVIEW's MEMORY ??unique name/run.
5. ??`guard_cycle` releases on a `FIXED:` line under a prior-art archive's "What was done with it" (짠11g.3).
6. ?좑툘 **`peer.ps1` must be launched as `powershell -Command "& 'tools/peer.ps1' ??-Task (Get-Content -Raw <f>)"`**
   ??the `-File` form silently loses a multi-line `-Task` and exits 2 in 4 s (measured twice today).

## LabVIEW execution lock

```yaml
labview-lock:
  status: acquired
  owner: material/cycle15-d1-route-A-last
  since: 2026-09-17 13:0x
  purpose: 짠11p route A LAST attempt - OpConnectNested_v1 (2nd TMSC), OpTunnelSource_v0, build_d1_v0 run 9.
# 2026-09-17 12:2x material/open35-run-poison-fix: RELEASED. Two 3-second runs of tools/bench/test_run_poison.py
# (11 pass / 0 fail). LabVIEW NOT restarted. Scratch `SCRATCHPOISON_1220*/1221*.vi` created and DELETED in the
# same run, verified gone. ORIGINAL never opened; md5 2a78e17c449cacdaf5da389818526859 read before AND after.
# OpReport_v3 / OpWire_v1 md5 unchanged. Nothing saved, no GUI, no hardware. Handles 31,276 -> 31,381.
# 2026-09-17 11:0x-12:1x material/cycle15-d1-full-build-5: RELEASED. LabVIEW restarted twice (31,561 / 31,669 ->
# ~34,000). `OpConnectNested_v0` BUILT + SAVED (ExecState 1, 14,234 B). 4 scratches: 3 self-deleted, 1 orphaned by
# the bgrun kill and deleted by hand -> `claudeDev\SCRATCH*` is EMPTY, verified. ORIGINAL never opened; md5
# 2a78e17c449cacdaf5da389818526859 verified after. No GUI, no hardware. build_d1_v0 NOT run (see NEXT). Handles
# 31,285 -> 31,632. -> facts in OPEN 33/34/35.
# Earlier sessions, all RELEASED, originals md5 2a78e17c449... before AND after, no leftovers, no GUI, no
# hardware: build-4 (OpCreateConstOnTerm_v0 22/0, run 7 55/7) 쨌 build-3 (run 6 56/1) 쨌 phase-full-2 쨌 run 5 53/0.
# -> archive/2026-09-17-status-d1-full-build-{4,5}.md and the 09-16/17 set.
```
**Never assume an instance exited**: `tasklist | grep -i labview`. Fresh ??1,500 handles; unique scratch name/run.

## HARDWARE ??permission follows the RIG STATE. Current: **遺꾪빐 / DISASSEMBLED ??everything allowed**
**遺꾪빐 ??WE ARE HERE** = motors ??ASI ??camera ??쨌 議곕┰ = ??????쨌 ?ㅽ뿕以?= ?????? ?좑툘 The ASI carve-out is
**RETIRED** (rule 1b); **only the user announces a state change**. Rotor counter **0** 쨌 magnet full travel 쨌
camera 1280횞1024, offsets 0, 90.0009 Hz, never write `BinningHorizontal`; **a session open RESETS ROI *and*
exposure** ??the acquisition loop applies `tools/bench/camera_contract.py`. **No beads while disassembled.**

## Where things stand
**Stage 1 CLOSED**. **Stage 2**: `?쪪PU_core_v0` 69/69 쨌 `??queue_v0` 162/162 ??**say it exactly:** bit-identical
for the **first 10,018 frames only**, both **replay** artefacts. **THE GAP:** 172 ops, 120 recipes, 230 peers ??
**zero runnable experimental VIs**.

## OPEN ??one line each; long forms in `archive/2026-09-17-status-cycle15-narrative.md` (+ `??d1-phase-full-?? 짠0c)
1??, 5, 9??2 ??**all in archive 짠9**: PERIODIC auto-reset ungated 쨌 autofocus CLOSED (3.6 Hz) 쨌 27 undisposed
   peer archives 쨌 startup drives instruments 쨌 A2 54/54, A3 112/170 쨌 doc lint 2/4/3. **18 CLOSED by 짠11h ??no
   TIFF is written any more.** 13/14/15b/17b: ??stop measured (`#637` term **648 ??w3457 ??#11639**) 쨌
   ?뵶 `bgrun --detach` misses an orphaned grandchild 쨌 ?뵶 v3's R11 scored the *restart*, so the stop is unproven.
16 쨌 19/25/26 쨌 20??3 쨌 27 쨌 28 쨌 28b 쨌 28c/d/e 쨌 29 쨌 30/30b/30c ????CLOSED, relocated VERBATIM to
   `archive/2026-09-17-status-d1-full-build-5.md`: GPU kernel accepted for now 쨌 PLAN = REV 4 + 짠11c?벬?1h,
   transport = queues only 쨌 relocation MEASURED (`WhileLoop 3??`, `Diagram 170??73`, 23 moves, 8 SRs, panel 114;
   re-wire list `tools/bench/build_d1_v0.json`, **109 terminals / 24 uids**) 쨌 `OpCreateConstOnTerm_v0` 22/0 and
   `OpCreateConst_v0` is NOT the literal placer 쨌 source map **109/109** 쨌 `diag_d1_full_route` retired
   (`copy_by_index` of a constant copied nothing; `OpWireSource_v5` = 1055 here) 쨌 `OpStopFromNode_v0` T5 closed
   (0 ??387, ExecState 1) 쨌 `audit_cycle.FAILURE_RE` repaired 쨌 짠11h: the TIFF writer is not original, F1 uncapped.
28f 쨌 31 쨌 32 쨌 34 ??**relocated VERBATIM to `archive/2026-09-17-status-open-28f-35.md`**, one line each:
28f. ?뵶 run 7 of PHASE "full" stage 1: 66 routable rows ??**35 WIRED, 7 FAILED (5001), 24 NO-ROUTE** (17 of them
   `from-tunnel`), ExecState **0**, nothing saved ??**N1/F1/F2 still NOT RUN** (they need a saved ExecState 1).
31. ?뵶 retrospective still reviews the WRONG window (`retrospective.py:282-286`); no `docs/cycle16-plan.md`.
32. ?뵶?뵶 outcome review 2026-09-17: **six `OUTCOME-VIOLATION`s, SECOND consecutive time** ??the work stops for a
   re-plan with the USER. Not answerable by a device. Zero new user-runnable deliverables.
34. ?뵶 `OpConnectNested_v0`'s wire is PRESENT but the VI BREAKS (1 ??0): undecided whether my sink TYPE choice or
   the op. One 3-second discriminator named and **not yet run**.
33. ?뵶 **the 17 `from-tunnel` rows still have no BUILT route** ??but a candidate now exists and is unverified
   here: peer `nested-diagram-terminals` (codex, `-Kind fact`, ANSWERED) says `Nodes[]` belongs to
   **AbstractDiagram 6375809** ??*already in our own `docs/vi-server-ids.json`* ??so ONE `To More Specific
   Class` suffices, and `Loop.Diagram` **6361401** / `Structure.Diagrams[]` **6360803** are the intended
   structure-owned route; from-tunnel sources resolve via `Tunnel.Outside Terminal 6356001 ??Terminal.Connected
   Wire 634A000 ??Wire.Terminals[] 6371003 ??Terminal.Is Source? 634A003 ??Generic.Owner 6327806`. **6 of 18 IDs
   match our file exactly, 0 conflict, the rest UNVERIFIED; NOTHING BUILT.** Whether to build it = judgement.
35. ??**FIXED + MEASURED** (`tools/bench/test_run_poison.log`, **11 pass / 0 fail**). `gscript` now carries a
   module POISON flag: `_deadline_call()` sets it on every expiry (`_run` AND `_invoke`), `_check_poison()` runs
   first in `lv` / `op` (cache hit included ??the unguarded path) / `_invoke` / `_run` / `_err`. With a REAL
   outstanding COM call the next `op()` raised **`COMPoisoned` in 0 ms** instead of blocking; it self-clears once
   the abandoned worker is measurably dead. `GSCRIPT_POISON_RECOVER=1` restarts LabVIEW instead (opt-in).

## NEXT
?뵶 **JUDGEMENT, two questions, both measured not argued.** **(1)** OPEN 34: is the broken wire my type choice or
the op? ONE 3-second run settles it (two copies of one subVI, NAMED `error out` ??NAMED `error in (no error)`);
until then `OpConnectNested_v0` may not be wired into `build_d1_v0`. **(2)** OPEN 33: the 17 `from-tunnel` rows
have no route and none is buildable ??"run 8 ??save ??N1 ??F1 ??F2" **cannot happen as written**. Choices:
(i) resolve those sources at run time with `OpWireSource_v5` (its 1055 is OPEN 28c, unchased), (ii) re-scope D1
to a slice whose every cut terminal is routable, (iii) accept a second cast op, **(iv) NEW 12:2x ??build the
route codex names (cast GObject ??**AbstractDiagram**, `Nodes[]` 6375809; or `Loop.Diagram` 6361401 from the
loop itself), which contradicts "not buildable" but is UNVERIFIED here ??see OPEN 33.** **Material, unblocked, NOT
started:** reparent the 6 `ControlTerminal`s per 짠5d before wiring them; PHASE "full" stage 2 (8 queues,
endpoints, sentinels, `#376`/`#6384` carriers, GPU kernel 13+6) is **still entirely unwritten**. ?좑툘 OPEN 32:
no diagnostic or framework cycle before F1/F2.

## Where to look
`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** (new op + its measured
limit at the end of the table) 쨌 **`docs/d1-build-plan.md`** = the build order 쨌 `tools/recipes/build_d1_v0.py`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Prior-art review complete — read-only: no lock taken, no build, no edit, no `.vi` opened, no hardware touched.

**8 findings, 0 `novel`.** Both artifacts are genuinely unbuilt and the method is not refuted anywhere. But the plan's central claim ("the 'no second TMSC' statement is wrong") is *understated* — our own files hold a shipped VI with two independent Traverse→cast ladders, so no node needs copying at all; the plan's acceptance gate is the exact gate this project already measured to be insufficient; a standing decision blocks building on `OpConnectNested_v0` until OPEN 34's discriminator runs; and artifact 2's back half rests on an op whose own control is currently failing.

---

# PART A — THE DIRECTION

## A1 `settled-already` — there is a standing decision that `OpConnectNested_v0` is unproven, and v1 inherits its whole sink half

`STATUS.md:90-92` (NEXT, today): *"OPEN 34: is the broken wire my type choice or the op? ONE 3-second run settles it (two copies of one subVI, NAMED `error out` → NAMED `error in (no error)`); **until then `OpConnectNested_v0` may not be wired into `build_d1_v0`**."* `STATUS.md:74` carries the same as OPEN 34; `docs/d1-build-plan.md:674-678` states it as measurement: *"the op is verified STRUCTURAL + WIRE-IDENTITY only, NOT functional … the wire is created w285 on both ends and **ExecState drops to 0**. Undecided between a type-incompatible pair … and a wire the op always breaks."*

v1 as planned keeps v0's `Terminal.Connect Wire` invoke, v0's sink ladder and v0's cast, and adds a second cast on the **source** side. If OPEN 34's answer is "the op", v1 inherits the defect and the second build of the §11p budget is spent discovering it. The discriminator is 3 seconds and is named in two places; the brief mentions OPEN 34 nowhere.

**Scope:** the *ordering* — settle OPEN 34 before or inside the v1 build. It does **not** say v1 is the wrong artifact, and §11p (`docs/d1-build-plan.md:683-700`) does authorise exactly these two artifacts, so the direction itself is cleared.

## A2 — no surviving refutation of the v1 route

`tools/bench/build_opconnectnested_v0_run1.log:45` (`W4 ROUTE A wired: ExecState 0`) refutes feeding a raw `GObject` element into a `Diagram`-class property node — a downcast. Adding a cast is precisely the fix for that cause, so run 1 does not refute v1. The 2026-09-06 attack on `Terminal.Connect Wire` with two traversed terminals (`archive/peer/2026-09-06-connect-ladder-plan-attack.md:115`) concluded *"Connect Wire probably works for an unoccupied compatible sink"*, objecting only to node-index stability. Cleared.

## A3-i `contradicted` — "a second TMSC has no creator / cannot be built" is refuted by three places in our own record, and one of them is 20 lines below it in the same file

> `docs/toolkit-capabilities.md:56`: *"A second TMSC has no creator: `New VI Object` makes no primitive, and `copy_by_index` would land it with an **unwirable `target class`** (a class-specifier `Constant` is a GObject, not a Node)"* — repeated as **MEASURED "cannot be built"** at `docs/d1-build-plan.md:662-667`.

Against it:

- `docs/toolkit-capabilities.md:72` — same file, 16 lines later: *"`To More Specific Class`'s `target class` accepts **any wire of the target type**, not only a class-specifier constant"*, with the typed-refnum-seed recipe at `:73-83`. The class-specifier constant is not needed, so its GObject-ness cannot make a copied TMSC unwirable.
- `tools/bench/build_opconstvalue_v1.log:45-51` — it was **done and it compiled**: `PASS C2 exactly one new To More Specific Class (by added uid) [331]`, `PASS F2 seed -> TMSC.'target class' on both ends`, `PASS F2 TMSC -> PN.reference on both ends 543/543`, `F2: ExecState 1`. (The plan cites the *recipe*, `build_opconstvalue_v1.py:171-199`; the **log** is the measurement and is cited nowhere.)
- `tools/recipes/build_opconstvaluen_v0.py:96-101` — a TMSC's target class is *re-typed* after the fact by deleting the seed wire and wiring a new seed (`must("C new control -> TMSC.'target class' on both ends"`).

**Scope:** the sentence at `toolkit-capabilities.md:56` and `d1-build-plan.md:662-667`, which must be corrected before either is cited again. It does **not** touch run 1's ROUTE-A measurement (`ExecState 0` for the ungated downcast), which stands.

## A3-ii `contradicted` — three different accounts of what the 17 `from-tunnel` rows actually are, and the plan cites only the one that makes a reader work

| file | claim |
|---|---|
| `docs/d1-build-plan.md:692-694` (§11p.2, the plan's basis) | a **source-RESOLUTION gap** — one reader, `Outside Terminal → Connected Wire → Wire.Terminals[] → Is Source?/Owner`, *"verified on 3 rows"* |
| `docs/d1-route-b-plan.md:316-318` (same day) | *"MEASURED that 16 of them end at `outer_source: null` — **there is no named origin to find**"* |
| `tools/bench/build_d1_v0_run7.log:303-325` (the machine) | 17 rows, each *"has no NAMED node source **in any census**… **the value comes from further out through more unnamed tunnels**"* |

The third is the decisive one and it is neither of the first two: the source is reached through a **chain** of unnamed tunnels on successively outer diagrams. `OpTunnelSource_v0` as specified is a **one-hop** reader — tunnel → outer terminal → wire → terminals → owner. One hop on `#5058 t12 'Array of cal clusters'` (`:323`) returns another tunnel or its owning structure, not an origin. The plan states no recursion, no termination rule, and no gate for "the owner is itself a Tunnel".

Also on record, against "verified on 3 rows": exactly **one** of the 17 already carries an identified source in the offline map — `#376 t7` (`:317`, `{'kind':'node','diagram':'19','uid':637,'i':37}`) — and that row's problem is *addressing*, not resolution.

**Scope:** the premise and the hop-count of artifact 2, and the "16 rows will be resolved" expectation. It does **not** say the outer-terminal hop is wrong or that no row resolves.

## A4 `unread-evidence` — three documents written for this exact question, none cited

1. **`tools/bench/probe_opexitloop.log:12-18`** — the answer to "where do we get a second cast": see B3-i. Written 2026-09-14, never cited in the connect-nested line of work, and the 6-donor census that concluded "no second TMSC" (`tools/bench/diag_connectnested_donors.py`) censuses `OpNetInfo_v1`, `OpNodeTerms_v0`, `OpConnect_v0`, `OpStopFromNode_v0`, `OpCreateConstOnTerm_v0`, `OpWhileCast_v0` — **not** `OpExitLoop_v0`, `OpWire_v1` or `OpWireSource_v5`, the three that carry two.
2. **`tools/bench/diag_connectnested_v1_facts.log`** — the v1 fact run from **13:19 today**, written by this same cycle and cited nowhere in the brief. It already prints the copy address (`:37`, NI example TMSC uid 99 = `Function[6]`) and, more importantly, contradicts one construction step: `:29` — *"D2 TMSC 'target class' <- w772 from node **#None** … panel object on that wire: **None**"*. The plan's step 2 says *"feed its `target class` by BRANCHING the wire that already feeds the first TMSC's `target class`"*; the project's own walk could not identify that wire's source, and the gate that passed it (`:30`) is hard-coded `True` in `diag_connectnested_v1_facts.py:136`, so D2 is **not** actually established. The log also ends at `:41` (`D6a`) with **no `BGRUN END` line** — the run died before printing `Create To More Specific Class.vi`'s connector pane, so the plan's second donor route is unmeasured.
3. **`docs/toolkit-capabilities.md:49`** — `OpOwnerChain_v1`'s MEASURED LIMIT: when the owner's class is **`FlatSequenceFrame`** the class comes back but *"the **UID does not** — `owner_uid 0`, `error 1055: Property Node`"*, i.e. *"an owner chain **terminates silently at a flat-sequence frame**"* (`tools/bench/diag_ownerchain_hop.log`; peer `ownerchain-flatseqframe-1055`). Artifact 2's last hop is `Generic.Owner` 6327806 on objects inside the main VI, which traverses `FlatSequenceFrame` as a valid class (`toolkit-capabilities.md:271`). The plan neither cites this limit nor gates on it.

---

# PART B — THE ARTIFACTS

## B1 — cleared on existence

`claudeDev` holds 104 `Op*.vi`; there is no `OpConnectNested_v1` and no `OpTunnelSource*`. `connect_terminals` (`tools/gscript.py:2202`) and `connect2` (`:2428`) still require a top-level source. Both capability gaps are real as stated.

## B3-i `helper-exists` — a VI with **two** independent Traverse→IndexArray→`To More Specific Class` ladders, each with its own `Class Name`/`index` control, is already on disk

`tools/bench/probe_opexitloop.log`, `OpExitLoop_v0.vi`:

```
:2   panel: 'Class Name', 'Class Name 2', 'index', 'index 2' …
:12  node 1 uid 124 'Traverse for GObjects.vi'  Class Name <- w373 ; References -> w600
:13  node 2 uid 170 'Traverse for GObjects.vi'  Class Name <- w536 ; References -> w611
:15  node 4 uid 308 'Index Array'  array <- w600 ; index <- w1066 ; element -> w605
:16  node 5 uid 327 'Index Array'  array <- w611 ; index <- w1108 ; element -> w823
:17  node 6 uid 683 'To More Specific Class'  reference <- w605 ; target class <- w772
:18  node 7 uid 788 'To More Specific Class'  reference <- w823 ; target class <- w851
```

and `:21` shows #788's output (w349) feeding `Exit For Loop.vi`'s **`Diagram in`** — i.e. #788 is **Diagram-typed**, addressed by its own `Class Name 2`/`index 2` pair. `tools/recipes/build_opexitwhile.py:7-8` and `tools/recipes/build_oploopin.py:9` (*"TMSC 788 (Class Name 2 = 'Diagram', index 2) -> 'Diagram in'"*) both already use it that way, and `tools/recipes/build_opconnect_gateway_attempt.py:10-11,:16` records the same pair (683 + 788) in `OpWire_v1.vi`, which is also still on disk. A third instance: `tools/recipes/build_opownerchain_v0.py:14,:17` — `OpWireSource_v5` carries TMSC #1044 (→`Wire`) **and** #1221 (→`GObject`).

So "two independent nested-diagram ladders in one op" needs **no creation and no `copy_by_index`**: copy a donor that already has both and delete the tail, which is exactly how `OpExitWhile_v0`, `OpForLoopIn_v0`, `OpWhileLoopIn_v0` and `OpConnect_v0` were each built.

**Scope:** the construction route (which donor), and the cost of the build. It does **not** claim the copied-TMSC route fails — `build_opconstvalue_v1.log:45-51` shows it works; it claims the plan is choosing the more expensive of two proven routes without knowing the cheap one exists. It also does not settle #683's target type in `OpExitLoop_v0` (consumed as `Node in` at `:14`), so the second ladder's seed may still need the re-type step at `build_opconstvaluen_v0.py:96-101`.

## B3-ii `helper-exists` — artifact 2's front half exists twice, and its output for all 17 rows is already on disk

- `tunnels(target, index)` / `OpTunnels_v0`, `docs/toolkit-capabilities.md:24`: *"the index-th `LoopTunnel`: tunnel UID, IndexMode, **outer terminal (name / source? / wire)**, inner terminals as arrays"*, 132 tunnels censused.
- `OpTunnelRead_v0`, `docs/toolkit-capabilities.md:57` — the **UID-addressed** `Tunnel` cast (`cast(Tunnel) → Inside Terminals[] → IA → Connected Wire`), the nearest donor for an `Outside Terminal` variant and the one the plan does not name.
- `OpTunnelInd_v0` — `archive/bench-2026-09-13-array-reporter/build_optunnelind.py:16,:109-110` already builds `Tunnel.Outside Terminal 6356001 → Terminal` in a shipped op.
- And the per-row answer is already written down: `tools/bench/build_d1_v0_run7.log:303-325` names each tunnel **and its outer wire uid** (`#5569 → w5812`, `#5752 → w2731`, `#9087 → w9097`, … `#4031 → w4029`).

So the only hop this fleet does not have is **wire → driving object**, which is `OpWireSource_v5`'s job — see B2.

**Scope:** the front half and the addressing. It does not say the reader is unnecessary; it says ~all of it but one hop is built, and that hop has a recorded failure.

## B2 `already-failed` — `OpWireSource_v5` failed its own CONTROL, and no cause is on record

`tools/recipes/diag_d1_full_route.py:413-415` ran T6 as a **control**: reproduce the op's published, verified answer (`docs/NAMES.md:946`, *"wire 10850 -> source `DigitalNumericConstant` 10739"*, 12/12). Result, `tools/bench/diag_d1_full_route.json:49-52`:

```
"t6_control": { "rows": [], "stop": "error column at t0: error 1055: Property Node in OpWireSource_v5.vi …", "ok": false }
```

Zero terminals at `term index 0`, where `docs/NAMES.md:944` defines 1055 as *"past the end"*. In the same run the target read `ExecState 0` at all three sample points (`:44-47`) — an untested candidate cause that nobody has written down. The record says only *"a separate defect, logged, **not chased now**"* (`docs/d1-build-plan.md:722-723`; `STATUS.md` OPEN 28c).

The plan proposes *"an ADDITIVE build on `OpTunnels_v0`/`OpWireSource_v5`"*. The back half it would inherit is the identical `UID to GObject Reference.vi → cast(Wire) → Terms[] → Is Source?/Owner` chain (`tools/recipes/build_opownerchain_v0.py:12-17`), so a v0 built on it reproduces the failure unless the 1055 is read first. CLAUDE.md's own rule applies here by name — *"the second time a class of failure is explained by inference rather than read from the machine, the next build is the READER for it"* — and `toolkit-capabilities.md:218-221` is explicit that a failed control means *"print INVALID and conclude nothing"*.

**Scope:** the back half of artifact 2 only. It does not touch artifact 1, and it is not an argument that the 1055 is unfixable — it is that the cause is unrecorded and the plan neither reads it nor budgets for it.

## B4 `already-measured` — the plan's acceptance gate is the one pairing this project has already measured to be insufficient, and three of its names/IDs are already settled or flagged

- **The gate.** Plan step 2: *"Gate: `ExecState 1`, then a functional test … same wire uid on both ends"*. `tools/bench/test_opconnectnested_v1.log:24-27` measured that exact pair on v0: op error `''`, `V6a … sink w285 / source w285` PASS, `V6b 0 -> 285` PASS, and `**FAIL** V6c … ExecState 1 -> 0`. The general rule is already written: `docs/NAMES.md:861-863` — *"**A wire-uid-equality gate does NOT prove a wire is GOOD** … LabVIEW joins type-incompatible terminals and draws a broken wire, whose uid still reads identically at both ends. Gate `exec_state == 1` after any wire whose types are not obviously compatible."* The v1 test must therefore fix **both** endpoint types in advance (the discriminator §11n.4 already specifies) rather than reuse v0's unnamed sink.
- **Names.** `Tunnel.Outside Terminal` 6356001's data-terminal short name is **`Outer Term`** (`docs/NAMES.md:723`, again at `:274`, `:281`); `Node.Terminals[]` → `Terms[]` and `Terminal.Connected Wire` → `Wire` (`:218-219`); `Is Source?` → `IsSource` (`:355`). The brief uses long property names throughout, against `docs/toolkit-capabilities.md:60-61` (*"match terminal names the walk printed, never a guessed variant"*).
- **ID status.** `docs/vi-server-ids.json:142` — `Tunnel.Outside Terminal` **UNVERIFIED**; `:145` — `ControlTerminal.Control 6353000` **UNVERIFIED**. `Wire.Terminals[] 6371003`, `Terminal.Connected Wire 634A000` and `Generic.Owner 6327806` are `VERIFIED-HERE` (`:135-137`), with `:137` already recording the plan's own caveat (*"a ControlTerminal's Owner is the DIAGRAM, not a node"*). And `docs/NAMES.md:864-867`: `Generic.Owner` returns a **Generic** reference; wiring it into a GObject-class node *is a downcast* that reads ExecState 1 → 0 — so artifact 2 needs a cast on that hop too, which the brief does not list.

**Scope:** the gate's sufficiency and the name/ID inputs. It does not question either artifact's necessity.

---

```
PRIOR-ART: settled-already   (A1    — STATUS.md:74,:90-92 + docs/d1-build-plan.md:674-678 — covers ORDERING: a standing decision says OpConnectNested_v0 may not be wired into build_d1_v0 until OPEN 34's 3-second discriminator runs, and v1 keeps v0's sink ladder, cast and Connect Wire invoke; does NOT say v1 is the wrong artifact — §11p:683-700 authorises it)
PRIOR-ART: contradicted      (A3-i  — docs/toolkit-capabilities.md:72,:73-83 + tools/bench/build_opconstvalue_v1.log:45-51 + tools/recipes/build_opconstvaluen_v0.py:96-101 vs docs/toolkit-capabilities.md:56 + docs/d1-build-plan.md:662-667 — covers the "a second TMSC has no creator / cannot be built" sentence, which must be corrected before it is cited again; does NOT touch run 1's measured ExecState 0 for the ungated GObject→Diagram downcast)
PRIOR-ART: contradicted      (A3-ii — docs/d1-route-b-plan.md:316-318 + tools/bench/build_d1_v0_run7.log:303-325 vs docs/d1-build-plan.md:692-694 — covers artifact 2's PREMISE and HOP COUNT: one file says there is no named origin to find, the log says the source lies further out through more unnamed tunnels, and the specified reader is one hop with no recursion or termination rule; does NOT say the outer-terminal hop is wrong)
PRIOR-ART: unread-evidence   (A4    — tools/bench/probe_opexitloop.log:12-18 + tools/bench/diag_connectnested_v1_facts.log:29,:37,:41 (with diag_connectnested_v1_facts.py:136, a hard-coded PASS) + docs/toolkit-capabilities.md:49 — the two-cast donor, this cycle's own 13:19 fact run (which shows the target-class wire's source UNIDENTIFIED and died before measuring the erdosmiller creator), and OpOwnerChain_v1's FlatSequenceFrame limit are all uncited)
PRIOR-ART: helper-exists     (B3-i  — tools/bench/probe_opexitloop.log:2,:12-18,:21 + tools/recipes/build_oploopin.py:9 + tools/recipes/build_opexitwhile.py:7-8 + tools/recipes/build_opconnect_gateway_attempt.py:10-11 + tools/recipes/build_opownerchain_v0.py:14,:17 — covers HOW to get the second cast: OpExitLoop_v0 (and OpWire_v1, OpWireSource_v5) already carry two independent Traverse→IA→TMSC ladders with their own Class Name/index controls, #788 Diagram-typed, so no node need be created or copied; does NOT claim the copy_by_index route fails)
PRIOR-ART: helper-exists     (B3-ii — docs/toolkit-capabilities.md:24,:57 + archive/bench-2026-09-13-array-reporter/build_optunnelind.py:16,:109-110 + tools/bench/build_d1_v0_run7.log:303-325 — covers artifact 2's FRONT HALF: OpTunnels_v0 already returns the outer terminal's name/is-source/wire, OpTunnelRead_v0 is the UID-addressed Tunnel cast donor, OpTunnelInd_v0 already reads 6356001, and every one of the 17 outer wire uids is already on disk; does NOT cover the wire→source hop)
PRIOR-ART: already-failed    (B2    — tools/bench/diag_d1_full_route.json:44-52 + tools/recipes/diag_d1_full_route.py:413-415 + docs/NAMES.md:944-946 + docs/d1-build-plan.md:722-723 + tools/recipes/build_opownerchain_v0.py:12-17 — covers artifact 2's BACK HALF: OpWireSource_v5 failed to reproduce its own published control answer (0 rows, 1055 at term index 0) in a run where the target read ExecState 0 at all three samples, cause unrecorded and explicitly unchased; an additive build inherits the identical UID→cast(Wire)→Terms[] chain)
PRIOR-ART: already-measured  (B4    — tools/bench/test_opconnectnested_v1.log:24-27 + docs/NAMES.md:861-867,:218-219,:355,:723 + docs/vi-server-ids.json:142,:145 + docs/toolkit-capabilities.md:60-61 — covers the ACCEPTANCE GATE ("same wire uid on both ends" was measured to coexist with ExecState 1→0) and the input names/IDs (`Outer Term`, `Terms[]`, `Wire`, `IsSource`; 6356001 and 6353000 UNVERIFIED; Generic.Owner needs its own cast); does NOT question either artifact's necessity)
```

**The three that change what happens next.** **B3-i** — the second cast does not have to be made: `OpExitLoop_v0` already has two, wired to two `Class Name`/`index` pairs, one of them Diagram-typed; that is a copy-and-delete build instead of a copy-a-primitive-plus-seed build, and the §11p budget is two builds. **A1** — run OPEN 34's named 3-second discriminator inside the same batch, before or immediately after v1's build, or a `ExecState 0` result will again be undecidable between the op and the endpoint types. **B2 + A3-ii** — artifact 2 as specified is one hop against a multi-hop chain, resting on an op whose control currently fails; the cheap first step is reading *why* `OpWireSource_v5` returned 1055 on its own published wire, not wrapping it.

**Checked and cleared:** neither op exists under another name (104 `Op*.vi` in `claudeDev`, no `OpConnectNested_v1`, no `OpTunnelSource*`); `Terminal.Connect Wire` 6349C03 with two traversed terminals is refuted nowhere, and the 2026-09-06 attack on it objected only to index stability; the copied-TMSC + typed-seed route the plan proposes is corroborated by our own measurement (`build_opconstvalue_v1.log:45-51`), so claim 1 of the plan is right — it is merely not the cheapest true version of itself; `AbstractDiagram.Nodes[] 6375809` and the other five IDs codex named are consistent with `docs/vi-server-ids.json`.

## Sources

(extract from answer)

## What was done with it

FIXED: already-measured - tools/recipes/build_opconnectnested_v1.py:522 - the acceptance gate is no longer wire-uid
equality: T2 drops the SAME subVI in both bodies (NAMED `error out` -> NAMED `error in (no error)`) and T2c
(`:528`) requires the wire to SURVIVE `remove_bad_wires_scripted`, which is the discriminator uid equality cannot
make (NAMES.md:861-863).

FIXED: helper-exists - docs/d1-build-plan.md:713 - §11q.1 records `OpExitLoop_v0` / `OpWire_v1` /
`OpWireSource_v5` as already carrying two independent Traverse->IA->TMSC ladders, names `OpExitLoop_v0` as the
SECOND attempt inside §11p's 2-build budget, and the recipe's docstring
(tools/recipes/build_opconnectnested_v1.py:70) states why the copy route is taken first. For artifact 2, §11q.2
(`:720`) records that `OpTunnels_v0` / `OpTunnelRead_v0` / `OpTunnelInd_v0` already hold its front half.

FIXED: contradicted - docs/toolkit-capabilities.md:56 - the sentence "a second TMSC has no creator / not buildable
by this fleet" is WITHDRAWN there and at docs/d1-build-plan.md:662 (§11n item 2), with the three refutations from
our own files; what run 1 actually measured (an UNGATED GObject -> Diagram-class property node reads ExecState 0)
is kept. A3-ii is recorded at docs/d1-build-plan.md:720 (§11q.2 item 1) as a blocker on artifact 2's premise.

FIXED: already-failed - docs/d1-build-plan.md:720 - §11q.2 item 2 records `OpWireSource_v5`'s failure of its own
published control (diag_d1_full_route.json:49-52, 0 rows / error 1055) as a PRECONDITION on artifact 2, with
CLAUDE.md's "build the reader" rule cited; no additive build on that chain is started in this session.

FIXED: unread-evidence - tools/recipes/build_opconnectnested_v1.py:70 - the recipe now cites
`tools/bench/probe_opexitloop.log:12-18` (the two-cast donor) and this cycle's own
`tools/bench/diag_connectnested_v1_facts.log`; `OpOwnerChain_v1`'s FlatSequenceFrame limit is cited at
docs/d1-build-plan.md:720 (§11q.2 item 4), where it bears on artifact 2's last hop.

REFUTED: settled-already - STATUS.md:90-92 says `OpConnectNested_v0` "may not be wired into `build_d1_v0`" until
OPEN 34's discriminator runs, which does not cover building v1: it governs USING v0 in the D1 build, while
docs/d1-build-plan.md:683-700 (§11p, the USER's decision of the same day) authorises this artifact by name. The
discriminator that citation waits on - "two copies of one subVI, NAMED `error out` -> NAMED `error in (no error)`"
- is now gate T2/T2c of this very build (tools/recipes/build_opconnectnested_v1.py:482,:528), so the run answers
OPEN 34 rather than bypassing it.

**Verdict: 8 findings, 0 `novel`. Two were ADOPTED into the recipe before it ran, four are RECORDED against
artifact 2 and carried to judgement, one is a documentation repair, one is scope-checked and released.**

1. **B4 `already-measured` — ADOPTED, it changed the acceptance gate.** The reviewer is right that
   "same wire uid on both ends" is the pairing this project already measured to be insufficient
   (`test_opconnectnested_v1.log:24-27`, w285 on both ends with ExecState 1 → 0; the rule at
   `docs/NAMES.md:861-863`). `FIXED: tools/recipes/build_opconnectnested_v1.py` — T1 now drops the **same**
   subVI in both loop bodies so the pair under test is NAMED `error out` → NAMED `error in (no error)`
   (§11n.4's own discriminator), T2 records ExecState before **and** after, and the decisive gate is new:
   **T2c, the wire must SURVIVE `remove_bad_wires_scripted`** — RBW deletes a broken wire and leaves a good one,
   which uid equality cannot distinguish. The op's own `Is Broken?` / `UID` / `Name` indicators are read back and
   REPORTED, not gated, because their dataflow order relative to the `Connect Wire` invoke is not fixed.

2. **B3-i `helper-exists` — RECORDED, NOT ADOPTED, and the reason is written into the recipe's docstring.**
   The finding is factually right and is new information to this line of work: `OpExitLoop_v0.vi` already carries
   TWO independent `Traverse → IndexArray → To More Specific Class` ladders with their own `Class Name`/`index`
   pairs (`tools/bench/probe_opexitloop.log:12-18`, #683 and #788, the latter Diagram-typed), as do `OpWire_v1`
   and `OpWireSource_v5` — and the 6-donor census that concluded "no second TMSC exists"
   (`tools/bench/diag_connectnested_donors.log`) censused none of those three. It is not adopted because
   building from `OpExitLoop_v0` means re-creating both `Nodes[] → IA → Terms[] → IA` ladders and the
   `Connect Wire` invoke from scratch (7+ nodes, 10+ wires), whereas the route taken adds ONE node to an op that
   already works and whose copy step is itself measured (`build_opconstvalue_v1.log:45-51`; `OpConstValue_v1.vi`
   is on disk). **`OpExitLoop_v0` is designated the SECOND attempt within the 2-build budget, not a third route.**
   The review's own scope line says it "does not claim the copied-TMSC route fails".

3. **A3-i `contradicted` — ACCEPTED as a documentation repair.** `docs/toolkit-capabilities.md:56` and
   `docs/d1-build-plan.md` §11n item 2 both state that a second `To More Specific Class` "has no creator" and
   that the cross-diagram op "cannot be built by this fleet". The reason given (an unwirable class-specifier
   `Constant`) is refuted by `toolkit-capabilities.md:72` — *"`target class` accepts any wire of the target
   type"* — and by `build_opconstvalue_v1.py`, which copied a TMSC and fed `target class` from a
   `create_control` seed. Corrected where each sentence lives once this build's own measurement is in.

4. **A3-ii `contradicted` + B2 `already-failed` + B4's name/ID half + A4.3 — CARRIED, they are about ARTIFACT 2
   and they are material.** The 17 `from-tunnel` sources are recorded three different ways, and the machine's
   own account (`build_d1_v0_run7.log:303-325`) says the value comes *"from further out through more unnamed
   tunnels"* — a CHAIN, which a one-hop reader cannot resolve; `OpWireSource_v5` failed its own published
   control with error 1055 and the cause is unrecorded (STATUS OPEN 28c); `Generic.Owner` returns a **Generic**
   reference, so that hop needs its own cast (`NAMES.md:864-867`); and `OpOwnerChain_v1` terminates silently at a
   `FlatSequenceFrame`. Whether artifact 2 is still the right build, or whether the 1055 reader comes first
   (CLAUDE.md's "when a diagnosis is GUESSED twice, build the reader"), is a judgement call and is reported as
   such rather than taken here.

5. **A1 `settled-already` — scope-checked and RELEASED by opening the citation, as the protocol requires.**
   `STATUS.md:90-92` says `OpConnectNested_v0` "may not be wired into `build_d1_v0`" until OPEN 34's discriminator
   runs. That citation is about **wiring v0 into the D1 build**; it does not forbid building v1, and
   `docs/d1-build-plan.md:683-700` (§11p, the USER's decision of the same day) explicitly authorises exactly this
   artifact. Moreover the discriminator OPEN 34 asks for — "two copies of one subVI, NAMED `error out` → NAMED
   `error in (no error)`" — is now **inside this build as gate T2/T2c**, so the open question is answered by the
   same run rather than deferred.

6. **A4.2 — corrected.** The reviewer read `tools/bench/diag_connectnested_v1_facts.log` while it was still
   running (it completed 10 pass / 0 fail with a `BGRUN END` line, and D6 did print the erdosmiller creator's
   connector pane). The substantive half stands and is acted on: D2's gate was hard-coded `True`, and the walk
   could not identify the source of the old TMSC's `target class` wire w772 — because it IS a class-specifier
   `Constant`, which is a GObject and therefore absent from both `Diagram.Nodes[]` and `panel_wiring`. The recipe
   no longer proposes branching w772; it creates its own typed seed with `Terminal.Create Control` taken from the
   very property node the cast has to satisfy.
