# priorart-priorart-routeb-census

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $5.1198  in 68 / out 35983 / cache-create 208667 / cache-read 4266499  (498s, 46 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (502s)
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
# PRIOR-ART REVIEW: the "moved structure Terminals[] census" recipe (cycle 15, route B, Part 1)

## What is about to be built and run

`tools/recipes/diag_moved_structure_terminals.py` ??ONE run that:

1. copies the original `Min_Track N beads V6_ParallelLoop.vi` (md5 `2a78e17c449cacdaf5da389818526859`) to a
   uniquely-named scratch A under `user.lib\claudeDev`, opens its panel, and reads
   `gscript.node_terms()` ??`Name` 634A004, `Is Source?` 634A003, `Connected Wire` 634A000 per terminal ??for the
   FIVE structures route B moves: `#5540`, `#2222`, `#1359`, `#29874`, `#10407`, all on `Diagram #639`
   (Traverse index 43);
2. copies the original again to scratch B, creates 3 fresh While loops on `Diagram #686` with
   `gscript.loop_in('while', ??`, moves the same five structures into those loop bodies with
   `build_d1_v0.move_in` (`GObject.Move` via `OpMoveIn_v0`), and re-reads the same census on the new diagrams;
3. compares the terminal INDEX ??(`name`, `is_source`) map before vs after, and applies the route-B plan's
   SINK RULE to all 18 rows of `tools/bench/d1_tunnel_sources.json`;
4. deletes both scratches in the same run, re-reads the original's md5, writes
   `tools/bench/d1_moved_structure_terminals.json`.

No new op VI is created. No `.vi` is saved. No hardware, no GUI.

## Why it is being run ??the claim it settles

`STATUS.md` OPEN 37 (MEASURED 2026-09-17, `tools/bench/build_opconnectfromwire_v0_run2.log` T2):
`OpConnectFromWire_v0` wired a source into `#5540` terminal index **1** with no error, the sink wire went
`0 ??1231`, and that wire reads `Wire.Is Broken? TRUE` with TWO `Is Source? TRUE` terminals. The terminal at
index 1 is named `Bead is good? array out` ??an OUTPUT tunnel's outside terminal, so the write was
source-onto-source. My explanation at the time ??"the terminal index drifted when the copy was restructured" ??
was **withdrawn as unmeasured**. `archive/peer/2026-09-17-rbw-deleted-wires-run9.md` point 3 names terminal-INDEX
drift as a live, unmeasured alternative for a different failure. This run measures the index map directly, on
both a pre-move and a post-move copy.

## Facts I am relying on ??please check each against the project's own files

* `gscript.node_terms(target, diagram_index, node_index)` (`tools/gscript.py:816-868`) already returns Name /
  Is Source? / Connected Wire per terminal, each on its own error chain, plus the node's own UID. I am claiming
  **no reader needs to be built** for this question.
* `gscript.node_labels` (`tools/gscript.py:533-564`) returns `Diagram.Nodes[]` rows in Nodes[] order, so it
  yields the node INDEX without `build_track_v6_core.walk`'s per-node loop (47 nodes 횞 ~0.8 s).
* `gscript.tunnels()` (`tools/gscript.py:887-922`) is deliberately NOT used: its own docstring says it is
  `LoopTunnel`-only and does not cover shift registers, and four of the five structures are Case/For structures.
* `build_d1_v0.move_in` (`tools/recipes/build_d1_v0.py:318-335`) and `build_opownerchain_v1.read_owner` are the
  measured move + verification primitives; `tools/bench/probe_move_into_v0.log` records 12/0 on a `CaseStructure`.
* `tools/bench/d1_tunnel_sources.json` already holds all 18 from-tunnel rows with their measured outer-wire
  source owners, so the run joins onto it instead of re-deriving it.

## The five questions

1. Has this census ??`Node.Terminals[]` of `#5540` (or of the other four moved structures), pre-move and/or
   post-move, with `Is Source?` per index ??**already been measured and written down** anywhere in `docs/`,
   `tools/bench/*.json`, `tools/bench/*.log` or `archive/`? If so, name the file and line and this run is
   cancelled.
2. Has a reader or recipe for this **already been built** under another name?
3. Has this been **tried and failed** already, and is that failure recorded?
4. Does an existing **helper** already do it, so this code is redundant ??in particular, is there an existing
   census artefact (`d1_step0_census.json`, `main_vi_nodeterms.json`, `stage2-assembly-step-e.md`'s CENSUS A/B)
   that already carries the per-index `Is Source?` for these five uids?
5. Which of the facts I cite above are **contradicted elsewhere** in our own files?

End with machine-readable verdicts: `already-built`, `already-measured`, `already-failed`, `helper-exists`,
`novel`, each with a file:line citation.


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
   **build plan `docs/d1-build-plan.md` (REV 4 + 짠11c?벬?1u)** ??짠5/짠5a-bis (moves), 짠10 (S/N1/F1/F2).
   ?좑툘 **짠11t CLOSED ROUTE A; work continues in `docs/d1-route-b-plan.md` (revised 2026-09-17).** 짠11u says the
   run-9 "Remove Bad Wires deleted 3 of 8" gate was UNSOUND ??never cite it. 2. ?좑툘 A prior-art dispatcher's log MUST be named `priorart_*` /
   `peer_*` (`tools/logclass.py`) or the guards read the reviewer's prose as a build failure. 3. ??Scripting EDITS
   need the target's FRONT PANEL open; a fixed op PATH is served from LabVIEW's MEMORY ??unique scratch name/run.
4. ??`guard_cycle` releases on a `FIXED: <slug> - <path>:<line> - ?? line under a prior-art archive's "What was
   done with it" (짠11g.3) ??ONE PER SLUG, or `REFUTED:` with the citation opened. 5. ?좑툘 `peer.ps1` only as
   `powershell -Command "& 'tools/peer.ps1' ??-Task (Get-Content -Raw <f>)"` ??`-File` loses a multi-line `-Task`;
   and `tools/prior_art_review.py` must be launched from **PowerShell**, not the Bash tool (rc 127 there today).

## LabVIEW execution lock

```yaml
labview-lock:
  status: acquired
  owner: material/cycle15-d1-route-B-2
  since: 2026-09-17 15:3x
  purpose: route B ??Part 1 the #5540/#2222/#1359/#29874/#10407 Terminals[] census (pre/post move), then Part 2
           tools/recipes/build_d1_routeb_v0.py. Scratches unique per run, deleted in the same run; original
           md5 2a78e17c449cacdaf5da389818526859 read before AND after every run; nothing saved but
           Track_v6_D1_GPU.vi under claudeDev.
# 2026-09-17 14:2x-15:1x material/cycle15-d1-route-B-1: RELEASED. ??**`OpConnectFromWire_v0.vi` BUILT + SAVED**
# (16,524 B, ExecState 1) ??the writer whose `Wire Source` is a WIRE-terminal reference. Runs:
# `diag_connectfromwire_facts.log` 5/1, 73 s 쨌 `build_opconnectfromwire_v0.log` 37/2 (T2's new FATAL bare-check
# fired) 쨌 `build_opconnectfromwire_v0_run2.log` **42/1, 132 s** (only T2c2). 4 scratches, ALL created and deleted
# in the same run; nothing saved but the op. ORIGINAL never opened; md5 2a78e17c449cacdaf5da389818526859 before
# AND after EVERY run. No GUI, no hardware. Handles 30,xxx ??34,112. Peers, ALL ANSWERED and ALL disposed:
# `rbw-deleted-wires-run9` (codex, REFUTED our RBW reading) 쨌 `wireinputs-forloop-tunnel-name` (codex, REFUTED
# our 5001 reading) 쨌 `cfw-t2c2-broken-wire` (codex, cause withdrawn) 쨌 `priorart-connectfromwire` (6 findings) 쨌
# `priorart-cfw-recipe` (5 findings, all folded in BEFORE the run). Also filled in the blank disposition of
# `2026-09-01-??opwireref-donor-plan-attack.md`.
# Earlier sessions (route-A-run-9, route-A-last, open35-run-poison-fix, d1-full-build-5/4/3,
# phase-full-2, run 5): ALL RELEASED, originals md5 2a78e17c449... before AND after, no leftovers,
# no GUI, no hardware. Relocated VERBATIM -> archive/2026-09-17-status-d1-route-b-1.md 짠1
```
**Never assume an instance exited**: `tasklist | grep -i labview`. Fresh ??1,500 handles; unique scratch name/run.
## HARDWARE ??permission follows the RIG STATE. Current: **遺꾪빐 / DISASSEMBLED ??everything allowed**
**遺꾪빐 ??WE ARE HERE** = motors ??ASI ??camera ??쨌 議곕┰ = ??????쨌 ?ㅽ뿕以?= ?????? ?좑툘 The ASI carve-out is
**RETIRED** (rule 1b); **only the user announces a state change**. Rotor counter **0** 쨌 magnet full travel 쨌 camera
1280횞1024, offsets 0, 90.0009 Hz, never write `BinningHorizontal`; **a session open RESETS ROI *and* exposure** ??
the acquisition loop applies `tools/bench/camera_contract.py`. **No beads while disassembled.**

## Where things stand
**Stage 1 CLOSED**. **Stage 2**: `?쪪PU_core_v0` 69/69 쨌 `??queue_v0` 162/162 ??**say it exactly:** bit-identical
for the **first 10,018 frames only**, both **replay** artefacts. **THE GAP:** 173 ops, 121 recipes, 231 peers ??**zero runnable experimental VIs**.

## OPEN ??one line each; long forms in `archive/2026-09-17-status-cycle15-narrative.md` (+ `??d1-phase-full-?? 짠0c)
1??, 5, 9??2 ??**archive 짠9**: PERIODIC auto-reset ungated 쨌 autofocus CLOSED (3.6 Hz) 쨌 27 undisposed peer
   archives 쨌 startup drives instruments 쨌 A2 54/54, A3 112/170 쨌 doc lint 2/4/3. **18 CLOSED by 짠11h ??no TIFF is
   written any more.** 13/14/15b/17b: ??stop measured (`#637` term **648 ??w3457 ??#11639**) 쨌 ?뵶 `bgrun --detach`
   misses an orphaned grandchild 쨌 ?뵶 v3's R11 scored the *restart*, so the stop is unproven.
16 쨌 19/25/26 쨌 20??3 쨌 27 쨌 28 쨌 28b 쨌 28c/d/e 쨌 29 쨌 30/30b/30c ????ALL CLOSED; text in
   `archive/2026-09-17-status-d1-full-build-5.md` and `??d1-route-b-1.md` 짠5. Headlines: relocation MEASURED
   (`WhileLoop 3??`, `Diagram 170??73`, source map **109/109**) 쨌 `OpCreateConstOnTerm_v0` 22/0 쨌 28c was the
   CALLER never setting `UID 2` 쨌 짠11h: the TIFF writer is not original, F1 uncapped.
28f 쨌 31 쨌 32 ??one line each, full text in `archive/2026-09-17-status-d1-route-b-1.md` 짠4 and
   `??status-open-28f-35.md`: 28f run 7's 35/7/24 is SUPERSEDED by run 9's 42/6/18 쨌 ?뵶 31 the retrospective
   still reviews the WRONG window (`retrospective.py:282-286`; cause = `guard_cycle.stamp()` = min(ctime,
   mtime)), no cycle-16 plan yet 쨌 ?뵶?뵶 **32 outcome review: six `OUTCOME-VIOLATION`s, SECOND consecutive
   time ??the work stops for a re-plan with the USER.** Not answerable by a device.
33 쨌 34 쨌 35 ????CLOSED; relocated VERBATIM to `archive/2026-09-17-status-d1-route-b-1.md` 짠2: `OpConnectNested_v1` built+saved and measured in the real VI 쨌 gscript's COM poison flag fixed (11/0). ?좑툘 its "survives RBW" gate is RETIRED by 짠11u.
36. ??**LARGELY CLOSED 2026-09-17 (짠11u + `OpConnectFromWire_v0`).** (a) the 16 `from-tunnel` rows now have a
   WRITER ??built, saved, ExecState 1, and it ACCEPTED a `FlatSequenceInnerTunnel` source on the real VI.
   (b) the 6 `from-ctl` rows split: **3 were a caller bug** (`wire_control` without `src_diagram_index`;
   `'Auto-Reset'` wires cleanly with index 43) and **3 are UNDIAGNOSED `ForLoop` tunnels**, re-assigned to
   `OpConnectNested_v1`. **The newline is NOT the cause.** (c) run 9's "3 of 8 wires deleted by RBW" is
   **WITHDRAWN** ??that gate compared uids; at most 2 went null and 1 changed identity.
37. ?뵶 **NEW, MEASURED 2026-09-17 ??a `from-tunnel` sink needs a SIDE, not just an index.**
   `build_opconnectfromwire_v0_run2.log` T2: the op wired w5812 (source owned by `FlatSequenceInnerTunnel`
   **#5818**) into `#5540` t1 with **no error**, sink wire **0 ??1231** ??and that wire reads
   **`Wire.Is Broken? TRUE`**, with TWO `Is Source? TRUE` terminals (`SelectorTunnel` #5680, `LoopTunnel` #2497).
   The terminal the op resolved is named **`Bead is good? array out`** ??an OUTPUT tunnel. codex (ANSWERED,
   `archive/peer/2026-09-17-cfw-t2c2-broken-wire.md`) confirms two sources = broken and supplies the mechanism: a
   tunnel has an OUTSIDE and one INSIDE terminal per frame, and a source onto an OUTPUT tunnel's outside terminal
   is a source-to-source conflict. My "the index drifted when the copy was restructured" cause is **withdrawn as
   unmeasured**. The cheapest settling test ??a read-only `Node.Terminals[]` census of `#5540` on an
   unrestructured AND a restructured copy, comparing `Terminal.Name` 634A004 and `Is Source?` 634A003 ??was NOT
   run (third build attempt; the budget is two).

## NEXT
??**Route A is closed (짠11t) and B's FIRST ITEM IS BUILT.** `OpConnectFromWire_v0.vi` (16,524 B, ExecState 1,
`tools/recipes/build_opconnectfromwire_v0.py`, run 2 **42 pass / 1 fail**) is the writer 짠11t asked for, and it
carries the project's first ORDERED `Wire.Is Broken?` **6371004** readout ??which was never a missing op, only a
missing error-chain branch (prior-art A1). T1 is fully functional on a scratch (outer wire ??into a new While
loop body, `Is Broken? FALSE`, `LoopTunnel 0 ??1`).
?뵶 **THE ONE JUDGEMENT QUESTION (OPEN 37): how does a route-B recipe address a `from-tunnel` SINK?** The op takes
`(diagram, node, terminal index)`; a structure tunnel has an outside terminal and one inside terminal per frame,
and T2 put a source onto an OUTPUT tunnel's outside terminal and got a broken wire. Either (i) the recipe derives
the correct SIDE first (`Tunnel.Outside Terminal` 6356001 / `Inside Terminals[]` 6356000 ??`OpTunnelRead_v0`
already reads both), or (ii) the sink addressing changes shape. **That is a design decision, not a build.** The
read-only two-copy census above is the measurement that should precede it.
?좑툘 `docs/d1-route-b-plan.md` is REVISED but still `authorises: nothing` ??B is not started. Its ledger is now
**63 of 82 routed / 19 not** (18 R1 + 1 R3), and R1's own in-plan candidates (i)/(ii) are **refuted by
measurement** for 14 of 16 rows. Stage 2 (8 queues, sentinels, carriers, GPU kernel 13+6) is still unwritten, and
OPEN 32 (two consecutive outcome reviews demanding a re-plan with the USER) stands above all of this.

## Where to look
`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** (new ops at the end
of the table) 쨌 **`docs/d1-build-plan.md`** = the build order 쨌 `tools/recipes/build_d1_v0.py`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

# PRIOR-ART REVIEW — `tools/recipes/diag_moved_structure_terminals.py` (cycle 15, route B, Part 1)

**Verdict: NOT novel. 6 findings, 0 `novel`.**

The half already on disk is **pass A** (the pre-move census, all five structures) and the **side** question the run says it settles. The genuinely unmeasured half is **pass B** — but the recipe blames the wrong cause for the failure it exists to explain, and this project's own files contain the measurement that identifies the right one.

---

## PART A — THE DIRECTION

### A1 `settled-already` — "a `(node, terminal index)` pair does not name the SIDE" is already a written decision, and the chosen instrument cannot change it

`docs/NAMES.md:900-905`, dated 2026-09-17 — *this cycle*, written from the same T2c2 failure:

> **Two terminals on one wire both reporting `Terminal.Is Source?` 634A003 TRUE = the wire is BROKEN** (two drivers). MEASURED 2026-09-17 on `w1231` (`SelectorTunnel` #5680 + `LoopTunnel` #2497, `Is Broken? True`). ⚠️ A structure TUNNEL has an OUTSIDE terminal and one INSIDE terminal per frame (`Tunnel.Outside Terminal` **6356001**, `Tunnel.Inside Terminals[]` **6356000**) … **A `(node, terminal index)` pair does not name the SIDE.**

The decision the recipe cites (`docs/d1-route-b-plan.md:2`) allows the census *"to settle tunnel-side addressing"*. The census as built reads only `Name` 634A004, `Is Source?` 634A003 and `Connected Wire` 634A000 per index (`tools/recipes/diag_moved_structure_terminals.py:129,:136`). It never reads `Structure.Tunnels[]` 6360801, `Tunnel.Outside Terminal` 6356001 or `Inside Terminals[]` 6356000 — so it cannot report which tunnel an index belongs to, or which side of it.

The peer who prescribed this test wrote five numbered steps and only the first two were implemented — `archive/peer/2026-09-17-cfw-t2c2-broken-wire.md:126-141`: step 3 *"Read Case `Tunnels[]` — `6360801`"*, step 4 *"For every tunnel, read `Outside Terminal` — `6356001`, `Inside Terminals[]` — `6356000`"*, step 5 *"Compare the terminal-1 reference against each outside and inside terminal reference, then report the matched side and that side's `Is Source?`"*. Steps 3–5 are the side.

*Scope:* covers the claim that this census settles tunnel-side addressing. Does **not** say the `is_source` column is useless — it is the SINK RULE's precondition and the run reports it correctly.

### A3 `contradicted` — "index 1 is named `Bead is good? array out`" is contradicted by the project's own pristine census, and by the failing log itself

**Plan's side** (`tools/recipes/diag_moved_structure_terminals.py:12-14`):

> *"the terminal at index 1 is named `Bead is good? array out` — an **OUTPUT** tunnel's outside terminal, i.e. already a source."*

**Other side** — the identity-gated census of the *unmodified original*, `tools/bench/main_vi_nodeterms.json:11292-11315`:

```
 t1   name ""                          is_source false   wire 5979
 t2   name "Bead is good? array out"   is_source TRUE    wire 5637
```

On the pristine VI index 1 is an **unnamed sink** — it already satisfies the SINK RULE. The named output tunnel is index **2**.

**And the failing log records how index 1 became index 2's terminal.** `tools/bench/build_opconnectfromwire_v0_run2.log:96`:

> `FACT  T2 candidate sink #5540 t1 on Diagram[43].N[6]: wire sequence [5979, 5637, 0]`

`5979` is t1's pristine wire, `5637` is **t2's**. The step that produced that sequence is `bare()` — `tools/recipes/build_opconnectfromwire_v0.py:530-545` — which **deletes a Wire object and runs `remove_bad_wires_scripted` between reads**. And `tools/recipes/build_opconnectfromwire_v0.py:522` is `shutil.copyfile(ORIGINAL, WORK)`: the T2 copy was **never moved and never restructured**.

So the drift is real, and its measured trigger is *wire deletion + Remove Bad Wires on one copy* — not a move. Pass A opens an unrestructured copy, pass B a moved copy, and **neither bares a sink**. `P3` can return "IDENTICAL" and OPEN 37 will still be open.

*Does NOT cover* whether a move also drifts indices — that is open; see A4(b).

*Prose note, no slug:* the docstring's *"all 18 from-tunnel rows"* (`:28-29,:47`) reinstates a denominator already corrected and dispositioned — `archive/peer/2026-09-17-priorart-priorart-cfw-recipe.md:454` (*"The measured target set is 16"*), accepted and *"fixed … before it ran"* (`:467-468`), and `STATUS.md` OPEN 36(a). It affects reporting only, since `sink_rule()` branches by membership.

### A4 `unread-evidence` — three files answer this directly; none is cited

**(a) `docs/stage2-assembly-step-e.md:137-147`** — "CENSUS B MEASURED (2026-09-15)", `OpTunnelRead_v0` 24/24, identity-checked, main VI byte-identical. It already names #5540's tunnel *sides*: output tunnels **SelectorTunnel 6016** → `x,y,z array` (wire **5975**) and **SelectorTunnel 5680** → `Bead is good? array in` (wire **5637**); input tunnels 5825/5702 (outer **1681**/**6041**) and 5725/5967 (outer **5746**/**5979**).

Joined to `main_vi_nodeterms.json:11279-11363` **by wire uid**, the complete index → side → tunnel map falls out with **no LabVIEW run**:

```
 t0 w5709 sink                     t4 w5746 IN  tunnel 5725
 t1 w5979 IN  tunnel 5967          t5 w1681 IN  tunnel 5825
 t2 w5637 OUT SelectorTunnel 5680  t6 w5975 OUT SelectorTunnel 6016
 t3 w6041 IN  tunnel 5702
```

`SelectorTunnel 5680` is exactly the terminal the broken wire w1231 reported (`build_opconnectfromwire_v0_run2.log:104`).

**(b) `tools/bench/probe_move_into_v0.log:221` vs `:231`** — a measured `move_in` of a `CaseStructure` into a fresh sibling While loop: `Wire 1902 -> 1895, LoopTunnel 132 -> 130`, and `:232` *"ExecState now 0 (0 expected: wires were cut)"*. A move is already measured to destroy 7 wires and 2 loop tunnels. P3 (`:43-46`) predicts the map is *IDENTICAL* after the move and, on failure, budgets a `-Dual` FAILED-PREDICTION review. The `wire` column is already known to change.

**(c) `docs/cycle13-plan.md:126-130`** — the precedent, about one of these same five structures:

> ⚠️ **Rewritten after prior-art B3a and A4 — the ~40-run ownership walk is gone.** `tools/bench/main_vi_nodeterms.json` **already holds ForLoop #1359's ten terminals** under diagram `"43"`, node 16, each with `is_source` and its wire uid. So membership is a file lookup confirmed by **one** `g.node_terms_uid(MAIN, 43, 16)` read …

---

## PART B — THE ARTIFACT

### B4 `already-measured` — pass A already exists on disk, for all five structures, from the same original

`tools/bench/main_vi_nodeterms.json:2` is the same file the recipe copies (`diag_moved_structure_terminals.py:73`). Diagram key `"43"` starts at `:11110`, and all five uids are inside it with per-index `name`, `is_source`, `wire` **and** the four error columns P1d gates on: `#5540` `:11275-11364` (n 6) · `#2222` `:11996` (n 13) · `#1359` `:12293` (n 16) · `#10407` `:12805` · `#29874` `:14383`.

Validity: 626 nodes / 3,328 terminals, **identity verified per node by UID** (`docs/main-vi-panel-map.md:403`), and recorded as current for today's original — `archive/peer/2026-09-16-stop-condterm-failed-prediction.md:33`: *"…(tools/bench/main_vi_nodeterms.json, 2026-09-14, **same md5**)"*. P1b too: `tools/bench/diag_connectfromwire_facts.log:64` — *"B0 Diagram #639 is Traverse('Diagram') index 43"*.

*Scope:* **pass A only**. Does not cover pass B, and does not forbid five confirming `node_terms_uid` reads (~4 s), which is what `docs/cycle13-plan.md:128-130` settled on.

### B3 `helper-exists` — the side reader is built, verified, and was already run on these structures

`docs/toolkit-capabilities.md:59`: `OpTunnelRead_v0.vi` … cast(`Tunnel`) → `Inside Terminals[]` 6356000 → `Connected Wire`, `Terminal.Diagram` 634A002 → `UID` | **"row 43: both #5540 output tunnels, 24/24"**. Also `archive/2026-09-15-status-stage2-cycles-1-7.md:509` and `STATUS.md:102` (*"`OpTunnelRead_v0` already reads both"*).

The recipe rejects `gscript.tunnels()` (`:30-32`) correctly — it is LoopTunnel-only (`tools/gscript.py:887-894`, `:908` hard-codes the class) — and then reaches for no side reader at all, though the one that produced A4(a) is not LoopTunnel-seeded.

*Scope:* the side question only. `OpTunnelRead_v0` carries no `Nodes[]` index, so it does not replace `node_terms`; the two join by wire uid.

### B1 `already-built` — pass A's census machinery is `sweep_nodeterms_main.py`, and the two disagree on one convention

`tools/bench/sweep_nodeterms_main.py:44-77` already does what `census()` + `node_index_map()` do (`diag_moved_structure_terminals.py:115-142`): node index from a stored Nodes[] uid list, `node_terms_uid`'s own UID echo as identity gate (`:50-62`), the four error columns (`:63-64`), recorded rather than absorbed mismatches.

One divergence bites P3a — `sweep_nodeterms_main.py:65-66` **trims trailing empty terminals**:

```python
while terms and not terms[-1]["name"] and not terms[-1]["wire"]:
    terms.pop()          # trailing empties (past the end of Terminals[])
```

`census()` does not. So `len(out)` and the stored census count different things; "terminal COUNT unchanged" (`:222`) is meaningful only within this run, never against the file.

*Scope:* pass A's machinery only. Pass B (loop creation + `move_in` + re-census on the new body) has no precedent I found.

---

## What the citations leave, if it helps

(1) Take pass A from `main_vi_nodeterms.json` + `stage2-assembly-step-e.md:137-147`, confirmed by five `node_terms_uid` identity reads. (2) Keep pass B, re-predicting P3 against `probe_move_into_v0.log:221/:231`. (3) Add the arm the evidence points at — **bare + Remove Bad Wires on an unmoved copy**, the sequence `build_opconnectfromwire_v0_run2.log:96` already caught drifting. (4) If the side is the goal, read 6360801 / 6356001 / 6356000 through `OpTunnelRead_v0`, per `cfw-t2c2-broken-wire.md:126-141` steps 3–5.

---

```
PRIOR-ART: settled-already   (A1 — docs/NAMES.md:900-905 + archive/peer/2026-09-17-cfw-t2c2-broken-wire.md:126-141 vs tools/recipes/diag_moved_structure_terminals.py:129,:136 — covers the claim that this census settles tunnel-SIDE addressing: "a (node, terminal index) pair does not name the SIDE" is already decided in writing this cycle, and the run reads only Name/Is Source?/Connected Wire, never Structure.Tunnels[] 6360801 / Outside Terminal 6356001 / Inside Terminals[] 6356000. Does NOT claim the is_source column is worthless - it is the SINK RULE's precondition)
PRIOR-ART: contradicted      (A3 — tools/recipes/diag_moved_structure_terminals.py:12-14 vs tools/bench/main_vi_nodeterms.json:11292-11315 + tools/bench/build_opconnectfromwire_v0_run2.log:96 + tools/recipes/build_opconnectfromwire_v0.py:522,:530-545 — covers the premise "#5540 terminal index 1 is the OUTPUT tunnel 'Bead is good? array out'": on the pristine original t1 is an unnamed sink (is_source false, wire 5979) and t2 is the named source (wire 5637); the T2 copy was a plain copyfile of the original, never restructured, and the index moved only after bare()'s wire delete + Remove Bad Wires. The pre/post-MOVE design therefore cannot reproduce the one drift mechanism this project has measured. Does NOT claim a move cannot also drift indices)
PRIOR-ART: unread-evidence   (A4 — docs/stage2-assembly-step-e.md:137-147 + tools/bench/probe_move_into_v0.log:221,:231,:232 + docs/cycle13-plan.md:126-130, none cited in tools/recipes/diag_moved_structure_terminals.py:18-32 — covers (a) #5540's tunnel SIDES already measured by OpTunnelRead_v0 24/24 and joinable to main_vi_nodeterms.json by wire uid with zero LabVIEW runs; (b) a measured move already cutting Wire 1902->1895 and LoopTunnel 132->130, against which P3 predicts "IDENTICAL"; (c) the accepted precedent that replaced a LabVIEW walk over #1359 with a file lookup plus ONE identity read. Does NOT assert (a) covers the other four structures' frame contents)
PRIOR-ART: already-measured  (B4 — tools/bench/main_vi_nodeterms.json:2,:11110,:11275-11364,:11996,:12293,:12805,:14383 + docs/main-vi-panel-map.md:403 + archive/peer/2026-09-16-stop-condterm-failed-prediction.md:33 + tools/bench/diag_connectfromwire_facts.log:64 — covers PASS A in full: per-index name / Is Source? / wire / error columns for all five structures on Diagram "43" of the same original, identity-verified per node by UID and recorded at the same md5, plus P1b. Does NOT cover pass B, and does not forbid five confirming node_terms_uid reads)
PRIOR-ART: helper-exists     (B3 — docs/toolkit-capabilities.md:59 + archive/2026-09-15-status-stage2-cycles-1-7.md:509 + STATUS.md:102 vs tools/recipes/diag_moved_structure_terminals.py:30-32 — covers the SIDE half: OpTunnelRead_v0.vi is built, 24/24, and its row 43 result is "both #5540 output tunnels"; the recipe rules out gscript.tunnels() for being LoopTunnel-only (true, tools/gscript.py:887-894,:908) and then builds no side reader at all. Does NOT claim OpTunnelRead_v0 replaces node_terms - it carries no Nodes[] index)
PRIOR-ART: already-built     (B1 — tools/bench/sweep_nodeterms_main.py:44-77, esp. :50-62 and :65-66, vs tools/recipes/diag_moved_structure_terminals.py:115-142,:222 — covers pass A's census/index/identity-gate machinery, already implemented whole-VI, and flags one live divergence: the sweep trims trailing empty terminals and census() does not, so P3a's "terminal COUNT unchanged" is comparable only within this run, never against the stored file. Does NOT cover pass B's loop creation + move_in + re-census, for which I found no precedent)
```

Note: `Write` is disabled in this session, so this review exists only as this answer — the dispatcher's archive file is the copy of record. I took no lock, opened no VI, and ran nothing.

## Sources

(extract from answer)

## What was done with it

**ACCEPTED IN FULL — all six verdicts, 0 refuted.** The recipe was rewritten before it ever ran, and the review
changed the CONCLUSION, not just the cost: `#5540` t1 is an unnamed SINK on the pristine original, so STATUS
OPEN 37's "the op wrote onto an OUTPUT tunnel" premise is dead at the source, and the index shift was made by the
failing run's own `bare()` (wire delete + Remove Bad Wires), not by any move. Route B's build recipe
(`tools/recipes/build_d1_routeb_v0.py`) was already reading the sink's `is_source`/`wire` live before every
from-tunnel write, which is exactly the defence this finding calls for; it is unchanged by it.

FIXED: already-measured - tools/recipes/diag_moved_structure_terminals.py:158 - pass A no longer re-measures anything: `arm_a()` READS `tools/bench/main_vi_nodeterms.json` diagram key "43" for all five structures, and PA3 confirms it with five `node_terms_uid` identity reads instead of a fresh sweep (`docs/cycle13-plan.md:126-130`'s shape).
FIXED: contradicted - tools/recipes/diag_moved_structure_terminals.py:349 - the false premise is deleted from the docstring and replaced by the measurement, and arm C now REPRODUCES `bare()`'s wire-delete + Remove Bad Wires on an UNMOVED copy and predicts a SHIFT, which is the only drift mechanism this project has measured.
FIXED: settled-already - tools/recipes/diag_moved_structure_terminals.py:205 - the run no longer claims to settle tunnel-SIDE addressing by reading Name/Is Source?/Connected Wire; `CENSUS_B_TUNNELS` carries `OpTunnelRead_v0`'s own 24/24 result from `docs/stage2-assembly-step-e.md:137-147` and arm D joins it by wire uid.
FIXED: helper-exists - tools/recipes/diag_moved_structure_terminals.py:217 - `arm_d()` uses the side reader that already exists rather than building one, and prints index -> side -> tunnel for `#5540` with no LabVIEW call at all.
FIXED: unread-evidence - tools/recipes/diag_moved_structure_terminals.py:30 - `tools/bench/probe_move_into_v0.log:221,:231` is now cited in the contract, and P3's "IDENTICAL after the move" is replaced by PB2, which gates only that no SINK becomes a SOURCE and REPORTS the wire/tunnel losses that log already measured.
FIXED: already-built - tools/recipes/diag_moved_structure_terminals.py:129 - `trim()` adopts `tools/bench/sweep_nodeterms_main.py:65-66`'s trailing-empty trim verbatim, so this run's terminal counts are comparable with the stored census instead of only with themselves.
