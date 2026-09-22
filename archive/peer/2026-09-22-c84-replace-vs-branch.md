# c84-replace-vs-branch

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $4.9020  in 32 / out 47389 / cache-create 233869 / cache-read 2396660  (655s, 28 turn(s))
- **date:** 2026-09-22 14:04:14
- **outcome:** ANSWERED (656s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK the claim below. It is about to drive a real build against a real VI, so the job is to find the
reason it is WRONG, not to improve it.

## The failing record

`tools/bench/diag_c83_connect2x2_r2.log` (rc=1, 27 pass / 14 fail, 151 s) and its script
`tools/bench/diag_c83_connect2x2_r2.py`. The first failing line the gate names is:

    **FAIL**  R0 the border terminal's own `Wire` property read returned NO error  wire_err 1055

and every cell that DELETED wire 7506 first returned
`error 1055: Invoke Node ... | Method Name: Connect Wire` together with
`error 1055: To More Specific Class in UID to GObject Reference.vi`.

## The machine facts, all from that log (cite them back if you dispute them)

* `:56`, `:66` — cells R0 / R0b: wire 7506 ALIVE, the Invoke on the terminal named by the INDEX TRIPLE
  (`WhileLoop #23032`, `Nodes[21]`, `Terminals[1]`, owner `RightShiftRegister #23868`), the
  `FlatSequenceInnerTunnel #7468` `LeftTerm` `#7488` handed in as `Wire Source`. Result:
  `term_uid=7488 uid_back=7468`, NO error, `UID 2 = 7506`, the border terminal went `0 -> 7506`,
  `wire_delta 0`, `is_broken True`. Poison ON and poison OFF were identical.
* `:77`, `:89`, `:101`, `:113` — cells R1 / R2 / R3 / R4: wire 7506 DELETED first. All four return
  `error 1055` at the Invoke AND at `To More Specific Class in UID to GObject Reference.vi`,
  `term_uid=0 uid_back=0`, `UID 2 = 0`, border wire stays 0, `wire_delta 0`, one junk `Invoke` minted.
  R3/R4 are the SWAPPED op (`:36-46`: nets `w572 #239.'element'` and `w1337 #183.'LeftTerm'` exchanged
  onto the Invoke, the two other consumers re-branched, Remove Bad Wires removed 0, ExecState 1).
* `:54`, `:64`, `:75`, `:87`, `:99`, `:111` — in EVERY cell the border terminal's own `Wire` property
  read carries `wire_err: 1055` while that terminal is BARE, and 0 once it is wired.
* Earlier, `tools/bench/build_harness_copyloop2.log:31-40` records `Terminal.Connect Wire` 6349C03
  CREATING a wire between two BARE terminals (wire census 9 -> 10, both ends on wire 346,
  `ExecState` 0 -> 1).
* `tools/gscript.py:2521-2523` states: "an already-wired source is BRANCHED ... an already-wired SINK is
  not safe (LabVIEW re-routes and the VI breaks) — wire only unwired sinks."

## THE CLAIM UNDER ATTACK

1. Delete-then-connect is dead for this sink: deleting wire 7506 makes `FlatSequenceInnerTunnel #7468`
   itself unresolvable, so no configuration that deletes first can work.
2. Every connect-with-the-wire-ALIVE cell ever run put the Invoke on the SOURCE terminal, which is why it
   BRANCHED (net 7506 ending with three source terminals) instead of replacing.
3. Therefore the configuration NEVER RUN — the Invoke sitting on the SINK terminal (the FSIT `LeftTerm`
   `#7488`, which is `is_source=False`) with wire 7506 LEFT ALIVE, the loop border terminal handed in as
   `Wire Source` — will REPLACE the existing wire, because in LabVIEW's editor wiring a new source onto an
   input that is already wired replaces the wire that was there.
4. The border row's `wire_err: 1055` on a BARE terminal means `wire: 0` there is the error path's DEFAULT,
   so that column is a refusal rather than a measurement, and the FSIT's own faces (read through
   `OpFsInnerTunnelTerm_v0`) must be used instead.

## What to do with it

State the STRONGEST reason claim 3 is wrong. Name an ALTERNATIVE explanation of the R0/R0b branch that does
not predict a replacement in the swapped-with-wire-alive cell. Say what OBSERVATION would falsify claim 3
before anything is saved. Name the CHEAPEST discriminating test. Specific questions worth your search:

* Does `Terminal.Connect Wire` (method id 6349C03) REPLACE the existing wire on an already-wired sink
  terminal, REFUSE, BRANCH, or leave the VI broken? Is there NI or community documentation of its behaviour
  on a wired input? Is `Auto Route?` relevant to any of those outcomes?
* Does `tools/gscript.py:2521-2523` ("an already-wired SINK is not safe — LabVIEW re-routes and the VI
  breaks") refute claim 3 outright, and if so what evidence stands behind that line?
* If the method DOES replace, what happens to the OTHER end of the displaced wire — the old source
  `RightShiftRegister #4334` — does LabVIEW delete the old wire, leave a broken stub, or re-route it? A
  broken stub would raise the diagram-wide broken-wire count, which is the gate this build is about to use.
* Is `is_source=False` on `#7488` actually the right way to decide which side is the SINK for this method,
  given that a `FlatSequenceInnerTunnel`'s left terminal sits on the OUTER diagram?

You have read-only access to the project directory and the web. Cite `file:line` or a URL for every factual
claim. "Cannot tell from here" is an acceptable answer for any sub-question; say so rather than guessing.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled here (read-only review session), so the review is below rather than in a file.

# Claim 3 is REFUTED — and claim 1, the premise it rests on, has a measured alternative cause this project already found and banned

---

## 1. The single strongest reason claim 3 is wrong

**LabVIEW does not replace a wire on an already-wired terminal. It MERGES — not in scripting, and not in the editor either, which is the only argument claim 3 offers.**

Claim 3's mechanism is *"in LabVIEW's editor wiring a new source onto an input that is already wired replaces the wire that was there."* That is false about the editor. NI's Idea Exchange carries a request to make it true, and the request exists precisely because it is not:

> *"I have actually seen several LV programmers wire on top of another wire into a terminal, then being surprised that the wires **merged** instead of **switched**."* — Steen Schmidt, [NI Idea Exchange](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/When-wiring-to-an-already-wired-terminal-gt-replace-wire-gt/idc-p/2364136/highlight/true)

The scripting API has no replace and no disconnect at all. NI's Darren, answering exactly this question:

> *"Get a reference to the wire and call the Delete method. If the wire is connected to multiple sinks, you could get references to the source and (other sinks), delete the wire, then reconnect it…"* — [Disconnect wire through VI scripting](https://forums.ni.com/t5/LabVIEW/Disconnect-wire-through-VI-scripting/td-p/3046807)

So **delete-then-connect is the documented workflow, not the dead end claim 1 declares.**

And the configuration claim 3 calls "NEVER RUN" has been run **four times on this very VI by this op's own donor** — Invoke on an already-wired SINK, other terminal as `Wire Source`. Result, four times:

- `tools/bench/build_d1_m3a1.log:1174` (also `:1875`, `:2593`, `:3311`; indexed at `docs/cycle27-plan.md:3295-3300`): *"sink terminal t1 of CaseStructure #12589 carries wire 9113 ; WIRED-terminal count 3 -> 3 ; `Wire.Is Broken?` False ; **LANDED False**"* — the sink kept its OLD wire, the write changed nothing and raised nothing.
- The thinner, older datum behind `gscript.py:2522-2523` is `docs/keystone-op-spec.md:444-446`, on `IA534`: *"no wire, VI breaks"*.

Two sinks, two sessions, five occurrences, **zero replacements.**

## 2. An alternative explanation of R0/R0b that predicts NO replacement in the swapped cell

Claim 2 says R0 branched *"because the Invoke was on the SOURCE terminal."* It was not. The Invoke sat on the index-triple terminal — the loop border terminal — which was **BARE** (`:54`, `wire=0`), and the already-wired #7488 was the one passed as `Wire Source` (`build_opfsinnertunnelconnect_v0.py:36-38`). Source-vs-sink is not the variable that moved.

**Model that fits every measurement:** `Connect Wire` attaches the **reference** terminal to the `Wire Source` terminal's net. A terminal holds at most one wire (`Connected Wire` 634A000, *"Reference to the connected wire"*, [Terminal class](https://labviewwiki.org/wiki/Terminal_class)), so:

| reference terminal | observed | citation |
|---|---|---|
| BARE | joins the source's existing net; `wire_delta 0`; `UID 2` = the **old** wire 7506 | `diag_c83_connect2x2_r2.log:56`, `:66` |
| ALREADY WIRED | nothing happens; sink keeps its old wire; no error | `build_d1_m3a1.log:1174` ×4 |
| ALREADY WIRED | "no wire, VI breaks" | `keystone-op-spec.md:444-446` |

Claim 3's cell puts the Invoke on **#7488, already on net 7506** — the middle row. Prediction: **silent no-op**, `UID 2` = 7506, `wire_delta 0`, border still bare.

Note R0 is a *merge*, not a benign branch: the border terminal is `is_source: True` (`:53`) and joined a net sourced by `#4334` — two sources, LabVIEW's classic broken wire, matching `is_broken=True` at `:56` and the IA534 "VI breaks" signature. Editor merge, API merge and R0 are one behaviour.

## 3. Claim 1's premise: a measured, already-banned alternative cause

Every deleting cell runs **two** mutations one line apart:

```
diag_c83_connect2x2_r2.py:449   C82.del_wire(scratch, ROWD_WIRE, ...)
diag_c83_connect2x2_r2.py:450   g.remove_bad_wires_scripted(scratch)
```

and the second one's effect here is already on record:

> *"deleting t1's wire + `remove_bad_wires_scripted` **DELETES THE TUNNEL**, so every higher index drops by one and the map goes 7 → 6 terminals."* — `archive/2026-09-17-status-d1-route-b-2.md:44-46`

`docs/cycle27-plan.md:1860-1862` cites that line to **REFUSE** `remove_bad_wires_scripted` as a rule-1a hazard — and this script calls it anyway, in exactly the four cells that then could not resolve #7468. A deleted `FlatSequenceInnerTunnel` is a dead uid, and a dead uid is what `UID to GObject Reference.vi` reports as **1055, "Object reference is invalid"** (`:77`, `:89`, `:101`, `:113`); the Invoke's own 1055 is just the null refnum arriving downstream.

Same symptom, opposite consequence: **gone** ≠ **unresolvable**. If it is gone, delete-first is alive and the repair is to stop running Remove Bad Wires after the delete, not to abandon the route.

**Cannot tell from here** which line killed it — the run never re-read #7468 between them.

## 4. Claim 4 is refuted by the log it cites

`wire_err: 1055` on a bare terminal is not a refusal masking a measurement — **it is the measurement**, and it flips inside one cell: `:139` R0 — `border BEFORE wire=0 err={...'wire_err': 1055}` | `border AFTER wire=7506 err={...'wire_err': 0}`. `:142` repeats it for R0b. 1055 ⇔ bare, 0 ⇔ wired, 12/12 readings.

So the gate written on the review's behalf — *"the border terminal's own `Wire` property read returned NO error"* — **can never pass on a terminal that is bare by design**, and it manufactured **6 of the 14 failures** (`:55`, `:65`, `:76`, `:88`, `:100`, `:112`). Honest predicate: `(wire == 0 and wire_err == 1055) or (wire != 0 and wire_err == 0)`. Real score: 27 pass / 8 fail, and those 8 are four cells failing twice for one upstream reason.

## 5. What would FALSIFY claim 3

| | claim 3 (replace) | this review (merge/no-op) |
|---|---|---|
| border terminal after | **new** wire uid ≠ 7506 | still 0 (`wire_err` 1055) |
| op's `UID 2` | new uid | **7506** |
| Wire census | 7506 **gone** | 7506 still present |
| source owners on the sink's net | `[#23868]` only | `[#4334]` only |

**Claim 3 dies the moment `UID 2` returns 7506, or 7506 is still in the census.**

## 6. Cheapest discriminating test — the cell this run built and never fired

The run created the swapped op and proved it legal (`:46`, ExecState 1), then only ever fired it with the wire deleted. `diag_c83_connect2x2_r2.py:109-111` crosses {roles} × {Auto Route} with **delete held TRUE across the whole swap arm** — the 2×2 the file is named after was never run. One row:

```python
("R5", "swap", False, None, False)      # swapped roles, 7506 ALIVE, poison OFF
```

Plus, in the same run: (a) read #7468 with `OpFsInnerTunnelTerm_v0` **between** `del_wire` and `remove_bad_wires_scripted` in one deleting cell, to separate §3's two causes; (b) drop the `if neww and do_del` guard at `:483` — the only cells that ever connected anything are the only cells whose net was never walked. No new op, no new method id, one script run.

## 7. The specific questions

**Replace / refuse / branch / break?** On this project's record: **merge, or nothing** — silent no-op ×4, "no wire, VI breaks" ×1, merge-onto-the-existing-net ×2. No replacement anywhere, local or documented. `Auto Route?` is a routing parameter and **this run measured nothing about it**: R1/R2 and R3/R4 differ only in that flag and all four died upstream of the method.

**Does `gscript.py:2521-2523` refute claim 3 outright?** Not by itself — "re-routes" is a 2026-09-06 *interpretation* of "no wire, VI breaks" on one Index Array, thinner than it reads. Its conclusion is over-determined by the later four-fold CaseStructure measurement. Re-word the line to what was seen.

**If it replaced, what happens to #4334's end?** Unmeasured; cannot tell from here. But the acceptance would not catch a stub: `G4g/G4i/G4j` (`build_opfsinnertunnelconnect_v0.py:808-833`) read `Wire.Is Broken?` and owner identity **on the new net only**. Add a diagram-wide Wire count and `ExecState` bracket before this touches the bed.

**Is `is_source=False` the right sink test?** It is the right property (`Is Source?` 634A003) and topology corroborates it: a Wire object never spans two diagrams, and 7506's source is `Diagram #686 Nodes[4] #637 t10 is_source=True` (`docs/cycle27-plan.md:3358-3362`), so **#7488 is on #686 too** — same diagram as the border terminal, no boundary crossed, no tunnel needed for the new wire. The brief's "left terminal sits on the OUTER diagram" does not change which side is the sink. Caveat from our own files: after a structure is MOVED by our scripts, `Is Source?` has read FALSE on outputs as well (`archive/2026-09-17-status-d1-route-b-2.md:53`); #7468 was not moved, so it should hold here.

## 8. What would change my mind

R5 returning a `UID 2` that is **not** 7506, with 7506 absent from the Wire census. One reading — the one this run should have taken instead of four cells that all died at the same resolver.

**Sources:** [NI Idea Exchange — wiring to an already wired terminal](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/When-wiring-to-an-already-wired-terminal-gt-replace-wire-gt/idc-p/2364136/highlight/true) · [Disconnect wire through VI scripting](https://forums.ni.com/t5/LabVIEW/Disconnect-wire-through-VI-scripting/td-p/3046807) · [Terminal class — LabVIEW Wiki](https://labviewwiki.org/wiki/Terminal_class) · [Scripting: Connect a Terminal to a Flat Sequence Structure](https://forums.ni.com/t5/LabVIEW/Scripting-Connect-a-Terminal-to-a-Flat-Sequence-Structure/td-p/2672239) · [Automatically delete wires that are not connected at either end](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Automatically-delete-wires-that-are-not-connected-at-either-end/idi-p/2266080)

## Sources

(extract from answer)

## What was done with it

ANSWERED (656 s, $4.9020, opus / role `hypothesis` / effort max), `tools/bench/peer_c84_replace.log`
`BGRUN END rc=0 after 657s`. Disposed in full by the cycle-84 MATERIAL session; nothing is left unanswered
and nothing that belongs to judgement was acted on.

ACCEPTED AND BUILT INTO `tools/recipes/build_d1_m3a3b_d3.py` BEFORE IT RAN:
1. §1/§7 — the replacement premise is WITHDRAWN as fact and restated as the hypothesis under test
   (`:12-30`), with the review's editor citation (NI Idea Exchange: the wires *merged*, not switched), the
   "no replace and no disconnect in the scripting API" point, and the four `build_d1_m3a1.log:1174` no-ops
   quoted. The cell is still fired because the uid-addressed FSIT `LeftTerm` sink is genuinely unmeasured —
   which the review itself names as the one real difference.
2. §5 — the FALSIFICATION TABLE is now PRINTED PER CELL (`:620-631`): the op's `UID 2` against 7506, and
   whether wire 7506 is still in the Wire census afterwards. The review's own words: "Claim 3 dies the
   moment `UID 2` returns 7506, or 7506 is still in the census."
3. §7 last answer — "add a diagram-wide Wire count and `ExecState` bracket before this touches the bed" is
   implemented as a NON-MUTATING bracket around every call (Wire census before/after, `ExecState`
   before/after) beside GATE S(d)'s broken-wire count, so a source-less fragment at `#4334`'s end cannot
   pass unseen.
4. §2's model (a terminal holds at most one wire; `Connect Wire` joins the `reference` terminal to the
   `Wire Source` terminal's net) is the prediction this dispatch reports against. It predicts a silent
   no-op for this cell, which GATE S(a) fails on — so a failing run is a RESULT, not a defect.

RECORDED, NOT ACTED ON — these are judgement's and the brief forbids re-opening the route:
5. §3 — the competing cause for the `error 1055`: every deleting cell ran `remove_bad_wires_scripted` one
   line after `del_wire` (`diag_c83_connect2x2_r2.py:449-450`), and that verb is on record as having
   DELETED A TUNNEL (`archive/2026-09-17-status-d1-route-b-2.md:44-46`; refused as a rule-1a hazard at
   `docs/cycle27-plan.md:1860-1862`). "Gone" ≠ "unresolvable", so delete-first may still be alive. Written
   into the plan as entry **111a** (`docs/cycle27-plan.md:3372`) and raised to judgement in this session's
   `OPEN:` line. The discriminating read it asks for — `OpFsInnerTunnelTerm_v0` on `#7468` BETWEEN the
   delete and Remove Bad Wires — is NOT run here: this dispatch is forbidden to delete wire 7506 anywhere.
6. §4 — the c83 gate "the border terminal's own `Wire` property read returned NO error" is shown to be
   unpassable on a bare-by-design terminal and to have manufactured 6 of that run's 14 failures; the honest
   predicate is `(wire == 0 and wire_err == 1055) or (wire != 0 and wire_err == 0)`. This file does not use
   that column in any gate, so no repair was needed here; rewriting c83's score is judgement's.
7. §7 — "re-word `tools/gscript.py:2522-2523` to what was actually seen" ('re-routes' is a 2026-09-06
   interpretation of "no wire, VI breaks" on one Index Array). Not touched: editing a toolkit docstring on a
   review's say-so is a decision, and the line is quoted verbatim in the recipe instead.
