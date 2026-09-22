# c88-nodeside-zero

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.9893  in 20 / out 42826 / cache-create 226696 / cache-read 1109190  (529s, 21 turn(s))
- **date:** 2026-09-22 16:47:15
- **outcome:** ANSWERED (533s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

FAILED PREDICTION, cycle 88 part 2 (LabVIEW 2026 26.3.1f1, VI Scripting over ActiveX/COM). Attack the reading below.

THE RUN: tools/bench/diag_c88_nodeside.log (11 pass / 1 fail, BGRUN END rc=1 after 119s), read-only on a dated
scratch COPY of claudeDev\D1_s3b_m3a3b_rowD_20260922_161040.vi. JSON: tools/bench/diag_c88_nodeside.json. It is
the verbatim execution of section (d) of archive/peer/2026-09-22-c88-walk-1055.md (ANSWERED).

WHAT WAS PREDICTED:
  N2 "all four wires that the WIRE-SIDE walk answered for (1731, 3947, 9635, 7337) are found on the NODE side."
  N3 "none of the other seven (1893, 2819, 4833, 7388, 11232, 23502, 23540) is found."

WHAT WAS OBSERVED:
  - `Diagram #639` = traverse index 48, 68 nodes. `g.node_terms(work, 48, k)` ran for k = 0..67: 68 of 68 nodes
    scanned, 0 read errors, 8 s total.
  - `g.panel_wiring(work)`: 116 front-panel rows, error column ''.
  - NOT ONE of the 11 broken wire uids appears as a `wire` value in ANY of those node terminal rows, and NOT ONE
    appears in the 116 panel rows. answered-found 0/4, silent-found 0/7. N3 passed vacuously; N2 FAILED.
  - Yet the wire-side reader `OpWireSource_v5` had, on a byte-identical copy in the previous run
    (tools/bench/diag_c88_brokenwires.log:67-87), named real endpoint owners for four of them:
      w1731 -> LeftShiftRegister#4344 (is_source True), w3947 -> LeftShiftRegister#4274 (True),
      w9635 -> LoopTunnel#9641 (True), w7337 -> RightShiftRegister#4334 (is_source False).
  - The 11 uids are LabVIEW's OWN verdict: they are the set difference of `report_all('Wire')` around
    `remove_bad_wires_scripted` on a scratch (Wire objects 1920 -> 1909).
  - `build_d1_v0.owner_of` (strict uid echo) put ALL 11 on 'Diagram'#639, every error column empty.

ALREADY RULED OUT (do not re-derive):
  1. Sweep truncation - 68/68 nodes scanned, 0 read errors, well inside a 600 s budget.
  2. A junk-node or reader artefact - `gscript.node_terms` is documented and measured at 0 junk nodes per call.
  3. A stale or wrong uid set - the uids come from LabVIEW's own Remove Bad Wires delete set, and a second,
     independent op (`owner_of`) resolved every one of them on the unmutated copy.

THE READING UNDER ATTACK: "these 11 wires are attached to nothing that `Diagram #639`'s `Nodes[]` sweep or the
panel-wiring table can see, so both readers agree they have no node-side endpoint."

ANSWER: (a) the strongest reason that reading is wrong; (b) an alternative that explains a wire whose
`Wire.Terms[]` names `LeftShiftRegister#4344` while no node terminal on its own owning diagram carries it -
in particular, whether a shift register's / a tunnel's terminals are reachable at all through
`Diagram.Nodes[] -> Node.Terminals[]`, and if not, which class and property DOES reach them; (c) what would
falsify (a)/(b); (d) the CHEAPEST discriminating test that needs no mutation and no new op, naming the exact
existing readout and what each outcome would mean.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled in this session (read-only peer role), so the review is below rather than in a file.

---

**The reading is refuted: the node-side sweep could not have found those wires whatever their topology, and this project's own log already records one of the four sitting on a terminal.**

# (a) The single strongest reason the reading is wrong

**The machine has already recorded wire 7337 on a terminal — and it is a terminal `Diagram.Nodes[]` can never enumerate.**

`tools/bench/test_opshiftregs.log:2-6`, frame loop uid **637**, 14 shift registers:

```
reg  2 uid 4334 RightShiftRegister OUT 'VISA out' src=True wire 7506 | IN [('VISA out', False, 7337)]
```

Wire **7337** is the inside (body-side) feed of the VISA-session register **#4334**. That identity carries into the c88 artefact: `tools/recipes/stage_d1_m3a3_rowD.py:3-4` addresses the same `#4334` through the same OUTER wire `7506` on that exact bed — uid and outer wire both survive the staging, so the inside wire number is the same number the sweep declared unattached.

Why no `Diagram.Nodes[] → Node.Terminals[]` sweep can reach it:

- [Tunnel class — LabVIEW Wiki](https://labviewwiki.org/wiki/Tunnel_class), inheritance verbatim: **"Generic → GObject → Tunnel"**, subclasses ConditionalTunnel, **LeftShiftRegister**, **LoopTunnel**, RegionTunnel, **RightShiftRegister**.
- [VI Server Class Hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy): `Node` and `Tunnel` are *sibling* direct children of GObject (so are `Constant`, `Terminal`, `Wire`, `FlatSequenceInnerTunnel`, `FlatSequenceOuterTunnel`).
- [AbstractDiagram.Nodes[]](https://labviewwiki.org/wiki/AbstractDiagram_class/Nodes()_property): *"Returns references to all the nodes in the diagram."* Nodes. A Tunnel-descendant is not one; its terminals hang off `Tunnel.Outside Terminal` 6356001 / `Inside Terminals[]` 6356000 — which `docs/NAMES.md:263-264` already records for both register classes.

**4 of 4 endpoints the wire side named are Tunnel-descendants; 0 of 4 are Nodes.** The sweep is not a second opinion — it is a reader structurally incapable of returning anything else.

**This was measured here five days earlier, on this same VI.** `tools/bench/diag_tunnelsource_onehop.log:37` — *"UNRESOLVED owner uid 9025 (**LeftShiftRegister**) is **neither a node on diagrams (19, 43, 0)** nor a LoopTunnel"*; :28, :33, :46, :50, :58, :63, :73, :78 say the same for `FlatSequenceInnerTunnel` — 16 of 18 rows. `tools/recipes/build_d1_v0.py:204-209` wrote the conclusion into the recipe that built the artefact: *"Only the NODE case is addressable as `Diagram[].Nodes[].Terminals[]`."* And :246: *"They are NOT `Diagram.Nodes[]` members (a Constant is a GObject, not a Node)."* N2 predicted the opposite of a fact already in the build file — and :55 of that log even names **tunnel #9641**, the same tunnel c88 found for w9635.

**The experiment had zero discriminating power.** P(sweep silent | attached only to a border object) = 1; P(sweep silent | attached to nothing) = 1. Likelihood ratio 1. N3's "PASS" is not weak evidence, it is *no* evidence — and the log prints it as PASS, which is how it got read as corroboration.

**The pre-registered criterion failed and the conclusion was rewritten after.** `archive/peer/2026-09-22-c88-walk-1055.md:92` set confirmation as *"no node terminal … references any of the 7 uids, **while all 4 answering uids are referenced**."* The 4 were not referenced. By the review's own rule this outcome maps to `:104` — *"the wire-side walk is unreliable and 'zero rows' carries no topological meaning."* "Both readers agree" is a new claim built after the stated criterion was missed.

**A second, independent scope error.** `build_d1_v0.py:216-218`: `FRAME_LOOP_UID = 637`, **`FRAME_BODY_UID = 639`** — Diagram #639 is the *body* of WhileLoop #637 (corroborated by `diag_index → 48`, not 0; `gscript.py:618` says index 0 = top level). The structure that owns #4344/#4274/#4334/#9641 is node **#637**, which lives on Diagram **#686** (27 nodes, index 19 — `diag_c88_brokenwires.log:27`). Sweeping #639's own 68 nodes excludes the owning structure by construction. Sweeping #686 would not rescue it either: `docs/NAMES.md:313-317` measured that a structure node's `Terminals[]` lists the **outside** terminal only (empty For Loop = one entry, the count tunnel's outside terminal; *"`i` is not listed (inner terminal)"*), and these wires are on the inside.

# (b) Alternative explanation of the same evidence

**ALT-1 (primary) — the 11 are half-wires left by the S3 reparenting: each keeps a border-object endpoint on #639 and has lost its node endpoint.**

| wire | surviving end | what it is | recorded at |
|---|---|---|---|
| 1731 | SRC LeftShiftRegister **#4344** | VISA session entering the body | `build_d1_m3a2.log:136,139` (#4344 fed by FlatSequenceInnerTunnel #4194 via outer w4185); pair #4334/#4344 `build_d1_routeb_v0.log:304` |
| 3947 | SRC LeftShiftRegister **#4274** | `position [internal units]` entering the body | `build_d1_m3a2.log:200,203`; pair #4256/#4274 `build_d1_routeb_v0.log:303` |
| 7337 | SINK RightShiftRegister **#4334** | `VISA out` leaving the body | `test_opshiftregs.log:6` |
| 9635 | SRC LoopTunnel **#9641** | `# slices in stack`; outer w9649 → node #10407 t1 | `diag_tunnelsource_onehop.log:55-58`; #10407 is on the move list `build_d1_v0.py:253` |

Everything follows: RBW deletes them (a one-ended wire is broken); `Terms[]` names one owner and no partner; the node sweep sees nothing (no node end left, surviving end is a Tunnel-descendant); `panel_wiring` sees nothing (they are not ControlTerminals). Note the symmetry the reading never addressed — **w1731 lost its sink, w7337 lost its source.** That is the signature of producers/consumers being moved out of the loop body, not of litter.

**ALT-2 — `Wire.Terms[]` retains or fabricates owners on broken wires**, and the border objects do not really carry them. This is the only hypothesis that rescues the reading; (d) separates it in one op run.

**ALT-3 — the seven silent wires are untested in both directions.** `Terms[]` errored at index 0 for them, and the node sweep is blind to ≥9 non-Node endpoint classes (Tunnel ×5, FlatSequenceInner/OuterTunnel, SequenceLocal, Constant). No border-side reader has been asked about them at all.

**The stake:** the walk review's table (`…:104`) calls the "4 present / 7 absent" branch *"safe to delete without re-wiring."* Under ALT-1 those four wires **are** the VISA session, the position register and `# slices in stack` crossing the loop border. Deleting them without re-establishing the crossing drops real data paths — CLAUDE.md rule 1a.

# (c) What would falsify (a)/(b)

- **Rescues the reading / falsifies ALT-1:** a border-side read of #4334, #4344, #4274, #9641 **on this artefact** returning wire 0 (or a different wire) on every terminal.
- **Falsifies the reading:** any one of them carrying 1731 / 3947 / 7337 / 9635.
- **Falsifies my class argument specifically** (and I would drop it): any measurement on this machine returning a LeftShiftRegister or LoopTunnel uid *inside* `Diagram.Nodes[]`. `diag_tunnelsource_onehop.log:28-78` is 16 consecutive measurements of the opposite.
- The c88 run settles none of these — it contains no border-side read at all.

# (d) Cheapest discriminating test — existing ops, read-only, ≤5 runs

**Step 0 — free, zero LabVIEW calls:** `test_opshiftregs.log:6`, `build_d1_m3a2.log:136/200`, `diag_tunnelsource_onehop.log:55` already contradict "attached to nothing". Honest caveat: those were taken on the main-VI bed, not the dated artefact — which is exactly what step 1 fixes.

**Step 1 — `gscript.shift_reg_left()` (`tools/gscript.py:826`, `OpShiftRegs_v1`) on the same dated artefact.** It already returns, in ONE op run, a right register's `out`/`inside` terminals *and* its left partner's, each with the connected wire uid:

1. `li = [o["uid"] for o in g.report_all(work, "WhileLoop")].index(637)` — the `build_d1_v0.diag_index():357` one-liner, one run.
2. `g.shift_reg_left(work, li, reg_index=2, left_index=0)` → #4334 + #4344, covering **w7337** and **w1731**. Verify identity from the returned `uid` / `left_uids`, never from reg order (`ShiftRegUIDs` = `[1147, 4256, 4334, …]`, `test_opshiftregs.log:3`).
3. `g.shift_reg_left(work, li, reg_index=1, left_index=0)` → #4256/#4274, covering **w3947**.
4. `idx = [o["uid"] for o in g.report_all(work, "LoopTunnel")].index(9641)`; `g.tunnels(work, idx)` (`gscript.py:981`) → #9641's `out_wire` + `in_wires`, covering **w9635**.

≤5 op runs, ~10 s, no mutation, no new op, nothing saved — against 68 runs that could not answer.

| outcome | meaning |
|---|---|
| any of 1731/3947/7337/9635 on a border terminal | **reading refuted.** N2 measured the reader's scope, not the topology. D3's delete-then-connect must take endpoints from the border side, and each stub names a crossing to re-establish |
| every border terminal reads wire 0 | reading survives for those four, and `Wire.Terms[]` invents owners on broken wires — a worse finding, and D3 must not trust `Terms[]` either |
| mixed | neither reader is trustworthy alone; census every broken wire from **both** sides before any delete |

**Do not** re-run the node sweep against Diagram #686 hoping to catch loop node #637: `NAMES.md:313-317` says a structure node exposes its outside terminals only, and these wires are inside. That is the wasted run this analysis saves.

**What would change my mind:** only step 1 returning wire 0 on all four border objects. Nothing inside the c88 run can do it — a reader that cannot enumerate the class of object in question produces identical silence under both hypotheses.

**Sources:** [Tunnel class](https://labviewwiki.org/wiki/Tunnel_class) · [VI Server Class Hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy) · [AbstractDiagram.Nodes()](https://labviewwiki.org/wiki/AbstractDiagram_class/Nodes()_property) · [GObject class](https://labviewwiki.org/wiki/GObject_class) · [Loop.Shift Registers()](https://labviewwiki.org/wiki/Loop_class/Shift_Registers()_property) · local: `test_opshiftregs.log:2-6`, `diag_tunnelsource_onehop.log:28-78`, `build_d1_v0.py:204-209,216-218,246,253,357`, `NAMES.md:263-264,313-317`, `gscript.py:618,826,981`, `build_d1_m3a2.log:136-139,200-203`, `build_d1_routeb_v0.log:303-304`, `stage_d1_m3a3_rowD.py:3-4`, `2026-09-22-c88-walk-1055.md:92,104`

## Sources

(extract from answer)

## What was done with it

Classified **ANSWERED** (claude / role `hypothesis` / opus effort max, 533 s, $3.9893, `tools/bench/peer_c88_nodeside.log`
`BGRUN END rc=0 after 533s`). **ACCEPTED AS A READING OF THE INSTRUMENT, NOT ACTED ON AS A DESIGN CHANGE** — this is a
MEASUREMENT-ONLY dispatch and the material session's failure budget (2) was spent on gates G3 and N2, so it STOPPED here
by CLAUDE.md §3 rather than running a third measurement.

- **Its central point is accepted and is the most useful fact this cycle produced:** `Diagram.Nodes[]` cannot enumerate a
  `Tunnel`/`ShiftRegister`/`FlatSequence*Tunnel` terminal at all, and all four endpoint owners the wire-side walk named
  (`LeftShiftRegister#4344`, `LeftShiftRegister#4274`, `LoopTunnel#9641`, `RightShiftRegister#4334`) are of exactly those
  classes — so gate N2 could not have passed whatever the topology is, and gate **N3's PASS carries no information**
  (likelihood ratio 1). Both are recorded as such in the hand-back; neither is cited as evidence for anything.
- **The pre-registered-criterion criticism is accepted**: `archive/peer/2026-09-22-c88-walk-1055.md:92` made confirmation
  conditional on the four being referenced, they were not, so `:104` ("the wire-side walk is unreliable and 'zero rows'
  carries no topological meaning") is the branch that actually fired.
- **(d) step 1 — `gscript.shift_reg_left()` on the same dated artefact — is NOT RUN.** It is one read-only op run and it
  is the right next measurement, but it is a THIRD attempt inside a spent failure budget and its outcome selects between
  ALT-1 (the 11 are half-wires still holding a border endpoint, i.e. **deleting them would drop real data paths — rule
  1a**) and ALT-2 (`Wire.Terms[]` fabricates owners on broken wires). Handed to judgement with the citation intact.
- **Its warning against re-running the node sweep on Diagram #686 is recorded** (`NAMES.md:313-317`: a structure node
  exposes its OUTSIDE terminals only) so a future cycle does not pay for that run.

(Claude fills in)
