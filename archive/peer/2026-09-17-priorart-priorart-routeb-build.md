# priorart-priorart-routeb-build

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $5.4703  in 34 / out 36774 / cache-create 298475 / cache-read 3132010  (501s, 31 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (505s)
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
# PRIOR-ART REVIEW: `tools/recipes/build_d1_routeb_v0.py` ??route B's first BUILD (cycle 15)

Route A is closed (`docs/d1-build-plan.md` 짠11t). This is the build script for `docs/d1-route-b-plan.md`.
Please read the recipe itself ??it is written and on disk ??as well as this summary.

## What it does, in order

1. **S1** copy `Min_Track N beads V6_ParallelLoop.vi` (md5 `2a78e17c449cacdaf5da389818526859`) to a uniquely
   named scratch under `user.lib\claudeDev`; assert the BEFORE census (Diagram 170 / Node 626 / Wire 1902 /
   LoopTunnel 132 / ControlTerminal 114 / WhileLoop 3 / Local 8 / SubVI 98 / Function 181).
2. **S1t** delete `#22700` `#23020` (the fixture TIFF writer, 짠11h) ??SubVI 97 / Function 180 / Node 624 /
   Wire 1899.
3. **S1d ??new to route B** capture every wired terminal of `#5058` `#48` `#376`, then DELETE all three
   (SubVI 97 ??94). Those captured rows become the re-wire list, replacing route A's "the move cut it".
4. **S2** three fresh While loops on `Diagram #686` via `gscript.loop_in('while', ??` ??WhileLoop 3??,
   Diagram 170??73.
5. **S2d** `drop_subvi` of `GPU_kernel_v1.vi`, `??Madcity\ASI_adjust focus-subvi.vi` and
   `??background VIs\save trace.vi` into the three bodies ??SubVI 94??7.
6. **S3** `move_in` (`OpMoveIn_v0`, `GObject.Move`) of 21 nodes (17??.2, 4??.5, 0??.7) plus 8 ControlTerminals;
   census diff over movers + net-neighbours + diagram 19 + `#637`'s shift registers.
7. **S3c** 8 shift registers with `add_shift_reg`.
8. **F0/S3w** `tools/bench/d1_rewire_map.build_map()` classifies every cut terminal, then each row is connected
   by `gscript.wire` (name), `wire_sr`, `wire_control`, `OpCreateConstOnTerm_v0`, `OpConnectNested_v1` (index,
   same or cross diagram) or `OpConnectFromWire_v0` (from-tunnel). Gate: 0 FAILED and 0 NO-ROUTE.
9. **S1q/S4/S5/S6** queues (skipped unless S3w is clean), conditional terminals, junk-Invoke purge,
   Remove Bad Wires, ExecState 1 warm, save as `Track_v6_D1_GPU.vi`, cold re-open.

No new op VI is created. The original is only READ; the working copy is deleted unless it saves at ExecState 1.

## The three things I believe are NEW, and they are the ones to attack

**(1) A ControlTerminal-uid resolver with no new op.** `tools/recipes/probe_move_ctlterm_v0.py:68-72` records
that there is no reader from a `ControlTerminal` uid to its panel object, because `panel_wiring` returns the
CONTROL's uid and the WIRE's uid, never the terminal's ??and it identified its own target BY EFFECT instead.
But 짠4 of the route-B plan requires reparenting 8 named control terminals BEFORE any `wire_control`, and a
`GObject.Move` is addressed BY UID. My route: `panel_wiring(label) -> wire`, then `OpWireSource_v5(wire)` ->
the owner of that wire's SOURCE terminal, which for a control's own wire should be the `ControlTerminal`. It is
gated on `owner_class == 'ControlTerminal'`.
Has this composition been done or tried here before? Is the premise ??that a control terminal is the SOURCE end
of the wire on its own terminal ??contradicted anywhere in our files? Is there a reader I have missed?

**(2) The SINK RULE applied per row, by reading the sink live.** Before every `OpConnectFromWire_v0` write the
recipe reads that exact terminal and REFUSES unless it reads `is_source == False` and `wire == 0`; afterwards it
reads the op's own ordered `Wire.Is Broken?` 6371004. Is this already implemented somewhere (a "bare the sink"
assertion was demanded by `archive/peer/2026-09-17-wireinputs-forloop-tunnel-name.md`)? Does any existing helper
already do the refuse-if-source check?

**(3) Re-targeting the deleted subVIs.** `tools/bench/d1_rewire_map.py` still lists `#5058`/`#48`/`#376` in its
MOVE table, so its rows resolve exactly as in route A; the recipe then maps sink/source uid `5058 -> the fresh
GPU kernel`, `48 -> the fresh ASI subVI`, `376 -> the fresh save-trace subVI` at wiring time, and resolves the
terminal INDEX by NAME from a live census rather than from the stored one. Is that re-targeting recorded as
already tried, or as already failed?

## The five questions

1. Has any of this been **built** already under another name ??in particular a route-B build script, a
   ControlTerminal-uid resolver, or a sink-side guard?
2. Has it been **measured or answered** already in a doc or a log ??e.g. is there a recorded measurement of
   whether `wire_control` works with a reparented ControlTerminal, or of whether `drop_subvi` of
   `ASI_adjust focus-subvi.vi` / `save trace.vi` into a loop body succeeds?
3. Has it been **tried and failed** already, and is the failure recorded? (Route A ran nine times; which of its
   failures does this recipe reproduce?)
4. Does an existing **helper** already do part of it, so this code is redundant?
5. Which of the facts I cite are **contradicted elsewhere** in our own files? Specifically: the BEFORE census
   numbers; "SubVI 97 ??94"; "Diagram 170 ??173"; the claim that 1.7 receives no moved node; the 8-item
   ControlTerminal list; and the claim that `OpConnectFromWire_v0` is functional.

End with machine-readable verdicts (`already-built`, `already-measured`, `already-failed`, `helper-exists`,
`novel`), each with a file:line citation.


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

I read the recipe, the route‑B plan, the ops it calls, the route‑A logs, and the archived reviews. Verdict: **NOT novel — 7 findings, 0 `novel`.** The centre of it is finding (1): the ControlTerminal resolver's premise is contradicted by a measurement already on disk, and the project already wrote down the hop it would actually need.

---

# PRIOR‑ART REVIEW — `tools/recipes/build_d1_routeb_v0.py`

## PART A — THE DIRECTION

### A1 `settled-already` — the ControlTerminal‑uid hop was already specified this cycle, and the property it needs is recorded UNVERIFIED and unbuilt

`docs/d1-build-plan.md:787-788` (§11p.2, 2026‑09‑17) specifies this exact chain and then says what breaks it, in the same sentence:

> `Wire.Terminals[]` 6371003 → `Is Source?`/`Owner` (**a ControlTerminal's owner is its diagram — use `ControlTerminal.Control` 6353000**)

`docs/vi-server-ids.json:137` carries the same fact as a **VERIFIED‑HERE** entry:

> `"Generic.Owner": "6327806 VERIFIED-HERE (Basic Development Environment scope; a ControlTerminal's Owner is the DIAGRAM, not a node)"`

and `:145` records the replacement hop as unbuilt: `"ControlTerminal.Control": "6353000 UNVERIFIED"`. `docs/d1-build-plan.md:830` repeats that `6353000` is UNVERIFIED.

So the answer to *"is there a reader I have missed?"* is **no — and the project already wrote down which property a reader would have to use, and it is not `Owner`.**

*Scope:* covers `resolve_ctlterms()`'s route (`build_d1_routeb_v0.py:348-375`). Does **not** say a ControlTerminal cannot be reparented — `probe_move_ctlterm_v0.log:132` measures that it can (Q3, `#642 → Diagram#1170`, count 114 → 114).

### A3 `contradicted` — "the wire's SOURCE terminal's owner is the ControlTerminal" is contradicted by this project's own measurement, twice over

**Plan's side**, `build_d1_routeb_v0.py:31-33` and the gate at `:368`:

> `panel_wiring(label) -> wire` then `OpWireSource_v5(wire)` -> the wire's SOURCE terminal's owner, **which for a control's own wire IS the `ControlTerminal`** … GATED on `owner_class == 'ControlTerminal'`

**Other side (i) — the same `Generic.Owner` hop, measured on a real ControlTerminal.** `OpWireSource_v5` reads `Generic.Owner` **6327806** of the indexed `Wire.Terms[]` element (`docs/toolkit-capabilities.md:48`; `tools/recipes/build_opwiresource_v5.py:92-93,:155-160`), and `OpOwnerChain_v1` is *"`OpWireSource_v5` with the `Wire` cast and the whole `Wire.Terms[]` front section removed"* (`docs/toolkit-capabilities.md:49`) — the identical hop. Run it on the `stop (end)` terminal, `tools/bench/probe_move_ctlterm_v0.log:47`:

```
OBSERVED uid 642 -> owner 'Diagram' uid 639 | self 'ControlTerminal'#642 | 482 says 'Diagram' cast 'Diagram'
```

`owner_class` comes back **`'Diagram'`**. The op returns the owner only — it has no output for the terminal's *own* uid (`build_opwiresource_v5.py:92-93`: the identity node *"describes the TRAVERSED object"*, i.e. the wire). So the gate at `:368` cannot fire, `out` stays empty, all eight `S3-ct` gates FAIL, and **no control terminal is reparented**.

**Other side (ii) — independent of how `Owner` behaves: two of the eight labels are INDICATORS.** `tools/recipes/probe_move_ctlterm_v0.py:7-8`:

> indicators `min value` #17257 (w17287 **<-** #10969, read back by the implicit property #17289) and `Force (pN) vs Extension (nm) ` #8038 (w10908 **<-** #11261)

On an indicator's wire the `Is Source?` terminal is owned by the driving **node** (#10969 / #11261), never by the terminal. Both labels are in `CTLTERM_LABELS_12` (`build_d1_routeb_v0.py:156-158`). Correspondingly, `tools/bench/d1_rewire_sources.json` has **7 `from-ctl` rows** (`:10`) and every one is `"indicator": false` over six controls — `Auto-Reset` (`:231-235`), `Reset Tracking` (`:303-308`), `Force\nsmoothing\nhalf-width` (`:854-859`), `Extension\nmedian filter\nhalf-width` (`:879-884`, `:1640-1645`), `Z/dZ` (`:920-925`), `Correction Factor` (`:1037-1042`). Neither indicator label appears.

*Scope:* covers the resolver's premise and the 8‑label list. Does **not** cover `panel_wiring(label) → wire` (that half is sound, `tools/gscript.py:772-809`), nor the claim that reparenting is required by §4.

### A3‑b `contradicted` — the from‑tunnel SOURCE index *is* cached across the moves, contrary to the recipe's own header

**Plan's side**, `build_d1_routeb_v0.py:42-45`:

> **The from-tunnel SOURCE is re-read at wiring time, never cached.** … the outer wire is re-resolved as *the wire currently on `#637`'s own outside terminal for that tunnel*

**What the code does.** `by_wire637` is built from a read of `#637` taken **before any move** (`:396-403`, the comment says so: *"read on Diagram #686 BEFORE any move"*), returned at `:490`, and `from_tunnel()` uses it to pick the terminal **index**: `ti = r3["by_wire637"].get(ts["outer_wire"])` (`:601`), then re-reads `live637` fresh and indexes it with that pre‑move `ti` (`:607-609`). Only the *wire value* is re‑read; the *index* is cached.

**And the same function measures that those indices move.** `:462-467`:

> `#637` itself legitimately loses outside terminals: its tunnels die with the wires the moves cut.

`tools/bench/probe_move_into_v0.log:231` measured it for **two** moves: `Wire 1902 -> 1895, LoopTunnel 132 -> 130`. Route B performs 21 node moves plus 8 terminal moves (`MOVE_TABLE`, `:148-153`). A stale `ti` selects a *different, live* tunnel's wire, `w_now` is non‑zero, and the SINK RULE checks only the sink (`:623-629`) — so a wrong‑but‑valid source is wired silently and no gate sees it.

*Scope:* covers `from_tunnel`'s source addressing only. Does **not** touch the sink‑side read, which is correct as written.

### A4 `unread-evidence` — the project's own "valid route" for this join, and the candidate list, are both on disk and neither is cited

**(a)** `docs/main-vi-panel-map.md:242-245`:

> The valid route is `Traverse('ControlTerminal')` → `Terminal.Connected Wire` (634A000) **with the terminal's label**

repeated verbatim at `docs/main-vi-startup.md:70-72`. Joined to `panel_wiring`'s `label → wire` this gives `label → ControlTerminal uid` with **no `Owner` hop at all**. (I checked: no built reader does it — `grep ControlTerminal tools/gscript.py` returns only creators, `:1845-1857`, `:2300-2336`. So this is evidence of the right shape, not a helper you can call today.)

**(b)** The candidate set is already enumerated. `docs/d1-build-plan.md:220`:

> **31 `ControlTerminal`s are owned by `Diagram#639`** … `642, 3173, 3453, 1924, 4837, 5634, 403, 9306, …`; full list in `tools/bench/ctlterm_owners.json`

measured at `tools/bench/probe_move_ctlterm_v0.log:123`. Eight targets out of 31 known uids is a bounded search; the recipe re-derives from zero.

---

## PART B — THE ARTIFACT

### B1 `already-built` — an identification route from a panel label to its ControlTerminal uid exists and is MEASURED 9/0. It identifies *by effect*

`tools/recipes/probe_move_ctlterm_v0.py:327-351` moves a candidate and reads which `panel_wiring` row lost its wire. It worked on the first try, `tools/bench/probe_move_ctlterm_v0.log:134`:

> moved ControlTerminal uid(s) `[642]`; panel rows whose connected wire changed …: `[((7, 'stop (end)'), 6929, 0)]`

— control uid 7, terminal uid 642, one move, 14 s for the whole run (`:155`). The design note at `:68-75` states the premise the recipe restates as if new.

*Scope:* this identifies **after** the move, which §4's ordering (`docs/d1-route-b-plan.md:193-195`) does not forbid — a candidate can be moved, checked, and moved back with the same `move_in`. It does **not** give a pre‑move lookup, and the log's own caveat holds (`:73-75`): a bare or tab‑nested terminal changes no row.

### B2 `already-failed` — the `from-ctl` branch as written repeats run 9's failure exactly, because it assumes the reparent that A3 shows will not happen

`build_d1_routeb_v0.py:688-698` sets `sd = diag_index(TARGET, loops["1.2"]["body"])` **unconditionally** — the comment at `:688-689` says *"After S3-ct that is 1.2's body"* — and passes it to `wire_control`. When `resolve_ctlterms` returns `{}` the terminals are still on `Diagram #639`, and `Get Controls.vi` looks on the wrong diagram. That is precisely run 9, `tools/bench/build_d1_v0_run9.log:315-316`:

```
FAILED  #9647  t1 'y' <- from-ctl 17472  wire_control ['Auto-Reset'] -> Function.['y']: error 5001: LV-Scripting.lvlib:Get Controls.vi
FAILED  #10247 t1 'y' <- from-ctl 5605   wire_control ['Reset Tracking'] -> Function.['y']: error 5001: …
```

and the recorded cause, `docs/d1-build-plan.md:1169`:

> run 9 **skipped** the reparent step — `build_d1_v0_run9.log:358` `SKIPPED-PHASE S3c-ctlterm: the 6 ControlTerminals reparented into 1.2` — so the controls stayed on `Diagram #639`

The new plan addresses that cause **only** through `resolve_ctlterms`. With that gate unable to fire, six rows fail 5001 again and S3w's "0 FAILED" gate cannot be met.

*Scope:* covers the `from-ctl` branch's dependency on the reparent. Does **not** claim `src_diagram_index` is the wrong parameter — §11u.2's diagnosis stands (`'Auto-Reset'` wires cleanly with index **43**, `docs/d1-route-b-plan.md:73-78`).

### B4 `already-measured` — re-targeting a deleted subVI to a fresh drop has already been run, and it measured **uid reuse**

Route A already did the delete‑and‑re‑drop for the kernel: `tools/recipes/build_d1_v0.py:648-661` (S3e, `#5058` deleted, `GPU_kernel_v1.vi` dropped into 1.2), and `d1_rewire_map.py:184-185` already classifies those rows `from-kernel` — *"`#5058` is DELETED; the GPU kernel takes its place in 1.2"*. So `RETARGET` is not a new idea; what is new is extending it to `#48`/`#376`.

The measurement that extension has to survive, `tools/recipes/build_d1_v0.py:719-726`:

> ⚠️ uid REUSE: after the delete, `drop_subvi(GPU_kernel_v1.vi)` came back with **uid 5058 again** (run 4, `S3e` FACT)

Route B deletes three uids and then drops three subVIs (`s1d` `:260-290`, `s2d` `:321-344`). The ordering is safe as written — every delete precedes every drop, and `S1d`'s "all three uids are gone" gate (`:281-284`) runs in between — but the recipe never records the hazard, and `S3b-collateral`'s `staying` filter (`:487-489`) keys on those same uids.

*Scope:* covers the re-targeting mechanism and the uid-reuse fact. This is **not** a record of the extension failing — I found no run that deleted `#48`/`#376`.

---

## Checked and CLEAN — so the next round does not re-derive it

- **BEFORE census, including `Function 181`** — measured exactly, `tools/bench/build_d1_v0_run9.log:19`: `{'SubVI': 98, 'Function': 181, 'Node': 626, 'Wire': 1902}` plus `:14` for the other five classes. ✅
- **S1t deltas `SubVI 98→97, Function 181→180, Node 626→624, Wire 1902→1899`** — measured, `build_d1_v0_run9.log:24`. ✅
- **`Diagram 170 → 173` / `WhileLoop 3 → 6` for three While loops** — measured (`STATUS.md` OPEN 28 headline; `build_d1_v0_run3.log:13` reads a restructured copy at `Diagram 173, WhileLoop 6`). ✅ ⚠️ *Prose note, no slug:* `docs/d1-route-b-plan.md:327` and `:339` gate on **Diagram 174** because §2b `:113` includes a **fourth** loop (the 20‑slot pool For loop). The recipe builds three and gates on 173 (`:307-310`, `:843-846`), and `s1q` is explicitly not executed (`:768-770`). The counts are right for what is built; the plan's S2/S6 rows are not what this recipe asserts.
- **"1.7 receives no moved node"** — consistent: `MOVE_TABLE["1.7"] = []` (`:152`) and `#376` is deleted then re-dropped, while `d1_rewire_map.MOVE["1.7"] = [376]` (`d1_rewire_map.py:44`) only supplies `dest` for its rows. ✅
- **`OpConnectFromWire_v0` is functional** — as far as T1: `docs/toolkit-capabilities.md:58` records BUILT + SAVED, 16,524 B, ExecState 1, T1 `Is Broken? FALSE`. T2c2 is still red and `STATUS.md` OPEN 37 is open, but the recipe says so. ✅
- **The SINK RULE** — already blessed: `archive/peer/2026-09-17-priorart-priorart-routeb-census.md:370` records *"Route B's build recipe … was already reading the sink's `is_source`/`wire` live before every from-tunnel write, which is exactly the defence this finding calls for."* No gscript helper does a refuse‑if‑source check; the nearest built shape is `bare()` at `tools/recipes/build_opconnectfromwire_v0.py:530-545`. Keep it as written — but note `docs/NAMES.md:905`, *"A `(node, terminal index)` pair does not name the SIDE"*: the read makes the write safe, it does not prove the index names the intended tunnel side.

---

```
PRIOR-ART: settled-already   (A1 — docs/d1-build-plan.md:787-788 + docs/vi-server-ids.json:137,:145,:830 vs tools/recipes/build_d1_routeb_v0.py:27-33 — covers the question "is there a reader I have missed?": §11p.2 already specified this exact hop on 2026-09-17 and recorded in the same sentence that a ControlTerminal's Owner is its DIAGRAM, so the route needs ControlTerminal.Control 6353000, which vi-server-ids.json:145 marks UNVERIFIED and nothing builds. Does NOT say a ControlTerminal cannot be reparented — probe_move_ctlterm_v0.log:132 measures that it can)
PRIOR-ART: contradicted      (A3 — tools/recipes/build_d1_routeb_v0.py:31-33,:368 vs tools/bench/probe_move_ctlterm_v0.log:47 + docs/toolkit-capabilities.md:48,:49 + tools/recipes/build_opwiresource_v5.py:92-93,:155-160, and independently tools/recipes/probe_move_ctlterm_v0.py:7-8 + tools/bench/d1_rewire_sources.json:10,:231-235,:303-308,:854-859,:879-884,:920-925,:1037-1042 — covers the premise "a control's own wire's SOURCE terminal is owned by the ControlTerminal": the identical Generic.Owner 6327806 hop returns owner 'Diagram'#639 for ControlTerminal #642, and two of the eight labels are INDICATORS whose wire source is owned by the driving node, so the owner_class=='ControlTerminal' gate cannot fire and all 8 reparents are skipped. Does NOT cover panel_wiring(label)->wire, which is sound)
PRIOR-ART: contradicted      (A3-b — tools/recipes/build_d1_routeb_v0.py:42-45 vs :396-403,:490,:601,:607-609 and :462-467 + tools/bench/probe_move_into_v0.log:231 — covers the header claim "the from-tunnel SOURCE is re-read at wiring time, never cached": only the wire VALUE is re-read; the terminal INDEX ti on #637 comes from a read taken before any move, while the same function measures that #637's tunnels die with the wires the moves cut, and two moves alone were measured at Wire 1902->1895, LoopTunnel 132->130. A drifted ti selects a live wrong tunnel and the SINK RULE, which checks only the sink, cannot see it. Does NOT touch the sink-side read)
PRIOR-ART: already-failed    (B2 — tools/recipes/build_d1_routeb_v0.py:688-698 vs tools/bench/build_d1_v0_run9.log:315-316 + docs/d1-build-plan.md:1169 — covers the from-ctl branch: it passes src_diagram_index = 1.2's body unconditionally, which is correct only if S3-ct reparented the terminals; run 9 skipped that step and the same two labels failed with error 5001 from Get Controls.vi. With A3 standing, the recipe reproduces that failure and S3w's "0 FAILED" gate cannot be met. Does NOT claim src_diagram_index is the wrong parameter — §11u.2's measurement that 'Auto-Reset' wires cleanly with index 43 stands)
PRIOR-ART: unread-evidence   (A4 — docs/main-vi-panel-map.md:242-245 + docs/main-vi-startup.md:70-72 + docs/d1-build-plan.md:220 + tools/bench/ctlterm_owners.json, none cited in tools/recipes/build_d1_routeb_v0.py:27-33 — covers (a) the project's own recorded "valid route" for this join, Traverse('ControlTerminal') -> Terminal.Connected Wire 634A000 with the terminal's label, which needs no Owner hop; and (b) the candidate set already being enumerated as 31 ControlTerminals owned by Diagram#639. Does NOT claim a built reader exists for (a) — I checked gscript.py and there is none)
PRIOR-ART: already-built     (B1 — tools/recipes/probe_move_ctlterm_v0.py:68-75,:327-351 + tools/bench/probe_move_ctlterm_v0.log:134 — covers identification of which ControlTerminal belongs to which panel label: the by-EFFECT route is built and measured 9 pass / 0 fail in 14 s, naming control uid 7 'stop (end)' as ControlTerminal #642. Does NOT provide a pre-move lookup, and the log's own caveat holds that a bare or tab-nested terminal changes no panel row)
PRIOR-ART: already-measured  (B4 — tools/recipes/build_d1_v0.py:648-661,:719-726 + tools/bench/d1_rewire_map.py:184-185 — covers the re-targeting mechanism: delete-then-drop-fresh plus a from-kernel row class already exists and was run in route A, and that run MEASURED uid reuse, drop_subvi returning the deleted node's uid 5058 again. Route B's ordering happens to be safe (all deletes precede all drops, gated at :281-284) but the hazard is unrecorded. Does NOT record any failure of extending this to #48/#376 — no run has done that)
```

I took no lock, opened no VI, ran nothing, and modified no project file.

## Sources

(extract from answer)

## What was done with it

**ACCEPTED IN FULL — all seven verdicts, 0 refuted, and the recipe was rewritten before it ran.** Two of them
were build-stopping and neither was visible from inside my own reasoning: the ControlTerminal resolver's gate
**could never fire** (`Generic.Owner` of a ControlTerminal is its Diagram, measured on `#642` itself), which
would have skipped all eight reparents and then reproduced run 9's six `5001`s exactly; and the from-tunnel
SOURCE index was cached across 29 moves while the same function's own comment says `#637`'s tunnels die with the
wires a move cuts — a drifted index would have wired a live but WRONG tunnel with every gate passing.

FIXED: contradicted - tools/recipes/build_d1_routeb_v0.py:392 - the `Generic.Owner` resolver is gone; `resolve_ctlterms()` is now `probe_move_ctlterm_v0`'s measured BY-EFFECT route (move a candidate, read which `panel_wiring` row's wire changed) run on a separate THROWAWAY copy, so the destructive search never touches the build target, and the candidate set comes from `tools/bench/ctlterm_owners.json`'s 31 terminals owned by `Diagram #639` instead of being re-derived.
FIXED: settled-already - tools/recipes/build_d1_routeb_v0.py:27 - the header now records `docs/d1-build-plan.md:787-788` and `docs/vi-server-ids.json:145`: a ControlTerminal's Owner is its DIAGRAM and the property a real lookup would need, `ControlTerminal.Control` 6353000, is UNVERIFIED and unbuilt — so no reader is invented here and the by-effect route is used instead.
FIXED: unread-evidence - tools/recipes/build_d1_routeb_v0.py:188 - the label set drops from 8 to the SIX controls `d1_rewire_sources.json`'s seven `from-ctl` rows actually name; `min value` and `Force (pN) vs Extension (nm) ` are INDICATORS (`probe_move_ctlterm_v0.py:7-8`), so they can never be a `from-ctl` source, and route B §2c's "8, not 6" is wrong about those two while right about the two half-width controls.
FIXED: already-built - tools/recipes/build_d1_routeb_v0.py:393 - the identification is no longer presented as new: the docstring cites `probe_move_ctlterm_v0.py:327-351` and its 9/0 measurement, and the implementation is that same route with a throwaway copy added because a move cuts the wire and moving back does not restore it.
FIXED: already-failed - tools/recipes/build_d1_routeb_v0.py:794 - the `from-ctl` branch no longer assumes the reparent happened: `src_diagram_index` follows what S3-ct MEASURED (1.2's body when the terminal really moved, `Diagram #639` otherwise), the other index is tried when the sink stays bare, and every attempt is reported — so run 9's cause cannot recur silently.
FIXED: already-measured - tools/recipes/build_d1_routeb_v0.py:344 - the uid-reuse hazard is now recorded and counted in S2d (`drop_subvi` returned the deleted uid 5058 again in route A), with the ordering argument written down: every delete in S1d precedes every drop in S2d and S1d's "all three uids are gone" gate runs between them.
FIXED: contradicted - tools/recipes/build_d1_routeb_v0.py:696 - nothing about the from-tunnel SOURCE is cached any more: `#637`'s outside terminals are re-read at wiring time and matched BY WIRE UID against `outer_wire`, and a row whose wire is no longer on exactly one of them is reported NO-ROUTE with that measurement instead of being wired from whatever now sits at the old index.
