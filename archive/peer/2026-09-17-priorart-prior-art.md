# priorart-prior-art

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.1846  in 38 / out 32369 / cache-create 213105 / cache-read 2488274  (430s, 30 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (432s)
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
  status: released
  owner:
  since:
  purpose:
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

Write is disabled in this session, so here is the review as text — which is the reviewer's product anyway.

# PRIOR-ART REVIEW — `OpConnectNested_v1` + `OpTunnelSource_v0` (trigger: new-op)

Read-only: no lock, no build, no edit, no `.vi` opened, no hardware.

**7 findings, 0 `novel`.** Neither artifact exists. But the claim this plan is built to overturn — "a second `To More Specific Class` has no creator" — was **already overturned by measurement in this project on 2026-09-15**, and the plan cites weaker evidence than the log that settles it. In the other direction, the plan treats `OpConnectNested_v0`'s same-diagram case as sound when the only ExecState measurement of it says the wire it makes breaks the VI, and it inherits `OpWireSource_v5`'s "1055 for every wire" without noticing that the run producing that 1055 drove the op on the wrong control.

---

## PART A — THE DIRECTION

### A1 — cleared, in favour

`docs/d1-build-plan.md:683-700` (§11p, user decision 2026-09-17) authorises **exactly these two artifacts**: item 1 with "budget 2 builds", item 2 "additive on OpWireSource/OpTunnels, verified on 3 rows", and `:700` — *"No further op beyond (1) and (2) is authorised for A."* The plan's scope matches line for line.

### A2 `refuted-already` — the direction is on record as MEASURED-IMPOSSIBLE, and that record is itself wrong

`docs/toolkit-capabilities.md:56` and `docs/d1-build-plan.md:662-667` both declare the two-diagram op not buildable, the second calling it **MEASURED**:

> `toolkit-capabilities.md:56` — *"A second TMSC has no creator: `New VI Object` makes no primitive …, and `copy_by_index` would land it with an **unwirable `target class`** (a class-specifier `Constant` is a GObject, not a Node)"*

Refuted by this project's own bench log, in the op family the plan builds on:

> `tools/bench/build_opwiresource_v2.log:31-35` — `PASS B exactly one new To More Specific Class (from copy_by_index's own 'added') [1221]` · `PASS B GObject seed -> TMSC2.'target class'` · `PASS B Generic.'Owner' -> TMSC2.'reference' (branch) on both ends 523/523` · `PASS B the target is runnable again`
> `:40` — `OBSERVED ExecState per step: [… ('TMSC2 copied and wired', 1), ('indicators added', 1)]`

Recipe: `tools/recipes/build_opwiresource_v2.py:7-8`, `:16-18` (*"copy a fresh To More Specific Class from the NI example (`copy_by_index`), wire seed → 'target class' (**a BRANCH**: the Wire-typed seed already feeds TMSC #1)"*), gated `:142`. **That is the plan's construction, already executed and gated ExecState 1.**

**Scope:** the "no creator" blocker only. It does **not** show the `GObject → AbstractDiagram` downcast is legal in `OpConnectNested`'s ladder — `build_opconnectnested_v0_run1.log:45` still stands for the *uncast* route.

### A3 `contradicted` — "`OpWireSource_v5` returns 1055 for every wire"

- Plan side / `d1-build-plan.md:723`: *"1055 for every wire — a separate defect, logged, not chased"*, from `tools/bench/diag_d1_full_route_run2.log:27-28` (`T6 control wire_source(10850) -> 0 terminals, stop='error … 1055: Property Node in OpWireSource_v5.vi'`) and `:29-65`.
- Other side, same op, **same subject VI**: `tools/bench/diag_d1_step0.log:23` — `OBSERVED: wire 8165 Terms[0] source=True owner 'FlatSequenceOuterTunnel' uid 16579 …`, folded in at `:26`.

The difference is the drive. `docs/toolkit-capabilities.md:48` and `docs/NAMES.md:940-941`: the op is addressed **by UID** — *"so no traverse index is involved"* — through control `"uid_in": "UID 2"` (`tools/bench/opwiresource_v5_labels.json:7`). The sibling driver does that (`tools/recipes/build_opcaseframes_v0.py:215`). The failing one does not: `tools/recipes/diag_d1_full_route.py:266-273` sets `vi path`, `Class Name`="Wire", `index`=`wi`, `index 2`=t — **`uid_in` is never written**. And `docs/NAMES.md:486`: *"Ops do not agree on what `index` means, and passing the wrong one gives error 1055 at a To More Specific Class."*

**Scope:** the cause of the 1055. It does **not** prove the op resolves the 17 rows.

### A4 `unread-evidence` — two archived exchanges answer "how do you create a typed TMSC", neither cited, both with empty dispositions

- `archive/peer/2026-09-07-tmsc-class-bootstrap-attack.md:25-35` — *"`Create To More Specific Class.vi`: use the numeric VI Server Class ID … `ClassSpecifierConstant` = 16452, `Node` = 16421, `Terminal` = 16385"*; `:69` *"test the erdosmiller helper with target class 16452"* — never recorded as run. `## What was done with it` empty (`:75-77`).
- `archive/peer/2026-08-31-…-classspecifierconstant-scriptable.md:25-31` — *"**Yes — directly settable.** `Class Name` (`566EFC02`) — **Read/Write** … `Set Type` (`566EF800`)"*; `:33` *"no special 'Create' VI is necessary"*. Empty at `:48-50`.

The plan supports claim 1 with a **folder listing** of the very VI whose numeric input the archive already documents.

---

## PART B — THE ARTIFACTS

### B1 `already-built` — two casts in one op already ship

`docs/toolkit-capabilities.md:48` — `OpWireSource_v5` = `UID to GObject Reference.vi` → **cast(`Wire`)** → … → `Generic.Owner` → `ClassName` + **cast(GObject)** → `UID`, FUNCTIONAL 12/12. `:49` — `OpOwnerChain_v1` is the same minus the Wire cast, 20 gates. **Scope:** the technique; the `OpConnectNested_v1` op itself is genuinely unbuilt.

### B2 `already-failed` — v0's wire has been measured to break a VI that compiled before it

> `tools/bench/test_opconnectnested_v1.log:22-27` — `PASS V4 PRECONDITION: the scratch reads ExecState 1 BEFORE the op under test runs` · `PASS V5 PRE-CALL: the chosen sink terminal is UNWIRED` · `FACT V6 … op error '', wire delta 1, **ExecState 1 -> 0**` · `**FAIL** V6c THE DISCRIMINATOR: ExecState is STILL 1`

That is the peer-prescribed three-postcondition test (`archive/peer/2026-09-17-connectnested-t2b.md:93`, adopted `:114-121`), failing the third postcondition. `d1-build-plan.md:674-678` leaves it undecided and names the discriminator — *"two copies of one subVI, NAMED `error out` → NAMED `error in (no error)`"* — and `STATUS.md` OPEN 34 carries it as **not yet run**, with *"until then `OpConnectNested_v0` may not be wired into `build_d1_v0`"*. The v1 plan keeps that invoke and sink ladder unchanged. Smaller repeat risk in the same family: `build_opwiresource_v2.log:14,16` `FAIL B exactly one new To More Specific Class (by added uid) []` → `STOP at gate`; the fix is identification from `copy_by_index`'s own `added` (`:31`).

### B3 `helper-exists` — artifact 2 is two shipped ops composed

`tools/gscript.py:887-894` — `tunnels()` / `OpTunnels_v0` returns *"out_name, out_is_source, out_wire …"* from `Tunnel[Outside Terminal, …]`. `toolkit-capabilities.md:48` — `OpWireSource_v5` takes that wire and returns `Is Source?`, reciprocal wire, owner class + owner UID. `:49` — `OpOwnerChain_v1` for the Owner hop alone. Correct drive: `build_opcaseframes_v0.py:215`. Only `ControlTerminal.Control` 6353000 has no wrapper; `docs/vi-server-ids.json:135-136` marks `Wire.Terminals[]`/`Connected Wire` VERIFIED-HERE, `:142-144` marks the tunnel IDs UNVERIFIED.

### B4 `already-measured` — the tunnel hop is stored; the missing piece is RECURSION

`tools/bench/diag_d1_step0.log:82` — `{'kind': 'LoopTunnel', 'uid': **5569**, … '**out_wire': 5812**, …}` (also `:84, :91-95, :135`); `diag_d1_full_route_run2.log:16` — stored resolution covers `{'LoopTunnel': 22, …}`. Tunnel #5569 is exactly run 7's "unresolvable" row: `build_d1_v0_run7.log:303`. And the same lines (`:303,:304,:307,:310,:311,:313`) say the rest lie *"further out through **more unnamed tunnels**"* — so a one-level reader gated on "3 rows" can pass while the deep rows stay unresolved.

---

```
PRIOR-ART: refuted-already  (A2 — tools/bench/build_opwiresource_v2.log:31-35,:40-41 + tools/recipes/build_opwiresource_v2.py:7-8,:16-18,:142 vs docs/toolkit-capabilities.md:56 + docs/d1-build-plan.md:662-667 — covers the "second TMSC has no creator / copy_by_index lands an unwirable target class" blocker: it was copied, its target class branched from the existing seed, and the VI read ExecState 1 on 2026-09-15; does NOT show the GObject->AbstractDiagram downcast is legal in OpConnectNested's ladder)
PRIOR-ART: contradicted     (A3 — tools/bench/diag_d1_step0.log:23,:26 + tools/bench/opwiresource_v5_labels.json:7 + tools/recipes/build_opcaseframes_v0.py:215 + docs/NAMES.md:486,:940-941 + docs/toolkit-capabilities.md:48 vs tools/bench/diag_d1_full_route_run2.log:27-28 + docs/d1-build-plan.md:723 — covers "OpWireSource_v5 returns 1055 for every wire": the op is UID-addressed via control `UID 2`, diag_d1_full_route.py:266-273 never sets uid_in, and the op answered correctly on the same VI earlier; does NOT prove it resolves the 17 from-tunnel rows)
PRIOR-ART: unread-evidence  (A4 — archive/peer/2026-09-07-tmsc-class-bootstrap-attack.md:25-35,:69,:75-77 + archive/peer/2026-08-31-2026-08-31-classspecifierconstant-scriptable.md:25-31,:33,:48-50 — the ClassID input of Create To More Specific Class.vi (16452/16421/16385) and the writable ClassSpecifierConstant.Class Name 566EFC02 / Set Type 566EF800, both dispositions empty; the plan cites only a folder listing)
PRIOR-ART: already-built    (B1 — docs/toolkit-capabilities.md:48,:49 + tools/recipes/build_opwiresource_v2.py:114-146 — covers the TECHNIQUE of two To More Specific Class nodes in one op; does NOT cover the OpConnectNested_v1 op, which is genuinely unbuilt)
PRIOR-ART: already-failed   (B2 — tools/bench/test_opconnectnested_v1.log:22-27 + docs/d1-build-plan.md:674-678 + STATUS.md OPEN 34 + tools/bench/build_opwiresource_v2.log:14,:16,:31 — covers the premise "v0 works on one diagram": from an ExecState-1 scratch with an unwired sink the wire took ExecState 1 -> 0, the named 3-second discriminator is unrun, and STATUS forbids using v0 until it is; does NOT say the second cast is wrong)
PRIOR-ART: helper-exists    (B3 — tools/gscript.py:887-894 + docs/toolkit-capabilities.md:48,:49 + tools/recipes/build_opcaseframes_v0.py:215 + docs/vi-server-ids.json:135-136,:142-144 — covers artifact 2's whole chain except ControlTerminal.Control 6353000; does NOT cover the recursion in B4)
PRIOR-ART: already-measured (B4 — tools/bench/diag_d1_step0.log:82,:84,:91-95,:135 + tools/bench/diag_d1_full_route_run2.log:16 vs tools/bench/build_d1_v0_run7.log:303,:304,:307,:310,:311,:313 — covers the tunnel->outer-wire hop incl. #5569 -> w5812, already stored; the remaining sources lie "further out through more unnamed tunnels"; does NOT say the reader is unnecessary)
```

**The three that change what happens next.**

1. **B2 first, and it costs 3 seconds.** The existing run used a **bare, unnamed** sink (`#45 t0`, name `''` — `test_opconnectnested_v1.log:10`) while claiming a compatible pair. Run it with two copies of one subVI, NAMED `error out` → NAMED `error in (no error)`, before any v1 build. If v0 breaks an ExecState-1 VI on a provably compatible pair, the second cast is not the defect and budget 2 buys the wrong thing.
2. **A2 changes how artifact 1 is built.** Don't spend exploratory builds against "no creator" — copy `build_opwiresource_v2.py:114-146`: `copy_by_index` the TMSC, identify from its own `added`, branch the existing seed into `target class`, wire `reference`, gate ExecState 1. That sequence is already green in a log.
3. **A3 + B3 may remove artifact 2 entirely.** Drive `OpWireSource_v5` through `uid_in` on one outer wire (w5812) first. If it answers, the from-tunnel gap is a join defect in `build_d1_v0.py`, not a missing op.

**Checked and cleared:** neither artifact exists under any name (`toolkit-capabilities.md:55-57`; `OpTunnelRead_v0` reads *inside* terminals); `Terminal.Connect Wire` 6349C03 with two traversed terminals is unrefuted (`archive/peer/2026-09-06-connect-ladder-plan-attack.md:115`); §11p authorises exactly this scope (`d1-build-plan.md:700`); the 1055-over-COM refnum trap (`docs/NAMES.md:473-475`) is avoided by both artifacts keeping every refnum inside the op.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
