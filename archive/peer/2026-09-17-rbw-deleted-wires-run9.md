# rbw-deleted-wires-run9

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-17
- **outcome:** ANSWERED (133s)
- **why asked:** mandatory review of the FAILED PREDICTION in `tools/bench/build_d1_v0_run9.log` gate F1v
  ("every index-addressed wire SURVIVES Remove Bad Wires"; observed 3 of 8 deleted)
- **verdict:** REFUTED — our reading is not established by the evidence we have; the GATE is unsound

## Question

LabVIEW VI Scripting (LabVIEW 2026, VI Server via COM). Attack the reading below of a FAILED PREDICTION.

## The prediction that failed
`tools/bench/build_d1_v0_run9.log` gate F1v: "every index-addressed wire SURVIVES Remove Bad Wires (i.e. none is
broken)". Observed: **3 of 8 deleted**. The 8 wires were made by our op `OpConnectNested_v1.vi`, which wires two
terminals addressed purely BY INDEX (`VI.Block Diagram -> Diagram.Nodes[] -> Node.Terminals[]` on each side, one
`To More Specific Class` per side, then `Terminal.Connect Wire` 6349C03).

## OUR READING, which you must try to destroy
"A branch into an already-multi-sink net across a loop boundary is created by Connect Wire as a BROKEN wire (wrong
type or wrong direction) rather than being declined with an error, and Remove Bad Wires then deletes it."

## The raw machine facts (verbatim from build_d1_v0_run9.log)
Creation rows (source -> sink, both by index; `delta` = change in the VI's total Wire count across the call;
ExecState was 0 throughout because the build is mid-relocation and reads ExecState only at the end):

    WIRED #1359  t4 ''  <- same-loop 8885   D[24].N[24].T[0] -> D[24].N[16].T[4]  wire 26189 (delta 1)
    WIRED #1359  t9 'Magnet position output' <- from-tunnel 28343
                                            D[19].N[16].T[0] -> D[24].N[16].T[9]  wire 26412 (delta 1)
    WIRED #29874 t4 ''  <- same-loop 8885   D[24].N[24].T[0] -> D[24].N[30].T[4]  wire 26189 (delta 0)

After every row the recipe ran `remove_bad_wires_scripted` (VI method Remove Bad Wires) once, then re-read each
sink terminal's `Terminal.Connected Wire` uid and compared it to the uid recorded right after creation:

    F1v: 8 made, 5 SURVIVED remove_bad_wires_scripted, 3 deleted by it; ExecState before RBW 0, after 0
    RBW-DELETED #1359  t4 ''                        wire 26189 -> 26412
    RBW-DELETED #1359  t9 'Magnet position output'  wire 26412 -> 0
    RBW-DELETED #29874 t4 ''                        wire 26189 -> 0

The classifier is literally `(survived if after == wire else died)` ??a uid-equality test
(`tools/recipes/build_d1_v0.py:1118-1127`). Note row 1 ended with a NON-ZERO wire (26412) on its terminal.
`#8885` is an `x*y` Multiply; `#1359` and `#29874` are For loops; D[24] is the new While loop's body diagram,
D[19] the diagram that holds it; `#27605` (D[19].N[16]) is a SubVI whose `Magnet position output` is the source
of the one cross-diagram row. The 5 survivors include 4 same-diagram rows into single-sink nets and one retry row.

## Already ruled out here (do not spend your answer on these)
* Not an addressing failure: every call returned an object and a wire uid; `Connect Wire` raised no error.
* Not "ExecState 0 proves brokenness": ExecState is 0 for the whole build because nodes are mid-relocation.
* Not a stale reference: node/terminal indices are re-read (`node_terms`) immediately before and after each call.

## What we need from you
1. The strongest reason our reading is WRONG, stated concretely in terms of LabVIEW's scripting semantics.
2. At least one alternative explanation for the same three rows ??in particular, whether LabVIEW RENUMBERS or
   REPLACES a wire object when a second branch is added to an existing net (so that the creation-time uid becomes
   stale without anything being deleted), and whether `Terminal.Connect Wire` on a source terminal that already
   drives a wire returns the EXISTING net's wire or a new one (the `delta 0` row).
3. What observation would falsify our reading.
4. The cheapest discriminating test we can run through VI Server scripting to separate "the wire was broken and
   deleted" from "the wire is fine and the uid moved" ??name the properties/methods by name (and numeric ID where
   you know it), e.g. `Wire.Is Broken?`, `Wire.Terminals[]`, `Diagram.Wires[]`, `VI.Get Errors`.
5. Whether a uid-equality test over a NET (as opposed to counting wires or reading `Wire.Is Broken?`) can ever be
   a sound RBW-survival gate.
Cite LabVIEW documentation or NI forum sources by URL where you have them.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

1. **The claim is wrong because the gate never measured brokenness or deletion.** `Terminal.Connect Wire` (`6349C03`) has **no return value**. The “creation-time wire UID” is therefore a later read of `Terminal.Connected Wire`, not an identity token returned by the operation. `Connected Wire` merely reports the wire currently connected to that terminal. Comparing that object’s UID after a topology-changing operation tests object identity—not whether the logical connection survived. [Connect Wire semantics](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method) · [Connected Wire property](https://labviewwiki.org/wiki/Terminal_class/Connected_Wire_property)

This distinction is decisive for row 1:

```text
#1359 t4: Connected Wire 26189 → 26412
```

That terminal was not observed becoming disconnected. The classifier called it “deleted” solely because its current wire object differed. Therefore “3 deleted by RBW” is not established; at most, two became null and one changed identity.

2. **The strongest alternative is net canonicalization plus index drift.**

LabVIEW defines a wire as having one source and potentially many sinks, while `Wire.Terminals[]` (`6371003`) returns all terminals connected by that wire. A second sink is therefore normally an enlargement of an existing wire/net, not necessarily creation of another wire object. [NI’s wire model](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html) · [Wire properties](https://labviewwiki.org/wiki/Wire_class)

That fits the `delta 0` row directly:

```text
Multiply source already drives wire 26189
second sink added
sink Connected Wire = 26189
total wire count delta = 0
```

`Connect Wire` does not “return the existing wire” or “return a new wire”—again, it returns nothing. The subsequent `Connected Wire` read apparently found the existing multi-terminal wire `26189`.

On renumbering versus replacement:

- LabVIEW does **not renumber a surviving object**. A UID remains associated with the same object, including across saves.
- If `26189 → 26412` was read from the same terminal object, then either LabVIEW replaced/reassociated the wire object while canonicalizing the net, or the terminal became connected to a different wire.
- But your code re-resolves `Node.Terminals[index]`. That prevents a stale reference while introducing another ambiguity: after tunnel creation/removal, does `T[4]` still identify the same logical loop terminal? The documented way to interpret `Terminals[]` indices is by the connector information, supplemented with `Is Source?` and datatype; re-reading the same numeric index alone does not prove semantic identity. [UID semantics](https://labviewwiki.org/wiki/GObject_class/UID_property) · [terminal-index guidance](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/td-p/4303374) · [NI Context Help terminal-number option](https://www.ni.com/docs/ar-SD/csh?context=lvcore_lvdialog_vi_server_config_options)

The highly suspicious fact is that row 1’s `T[4]` changed specifically to `26412`, the UID associated with the later cross-diagram connection. That is more suggestive of terminal-index movement or topology reassociation than simple deletion of a broken branch.

The two `→0` cases remain compatible with actual deletion, but also with:

- re-resolving a different terminal after dynamic tunnel changes;
- RBW removing a loose intermediary segment while the intended net survives through another tunnel-side wire object;
- the attempted connection being silently absent and a transient/bad segment being removed.

`Diagram.Wires[]` only enumerates wires connecting top-level objects in that particular diagram, which matters across structure boundaries. A cross-boundary logical connection can involve distinct diagram-local wire objects and tunnel terminals. [AbstractDiagram.Wires[] (`6375805`)](https://labviewwiki.org/wiki/AbstractDiagram_class)

3. **The observation that falsifies your reading is:**

Immediately after `Connect Wire`, before RBW:

```text
Wire.Is Broken? == FALSE
Wire.Terminals[] contains the intended source and sink terminal identities
```

and after RBW:

```text
the same source and sink remain in one connected component,
even if Connected Wire UID changes
```

That would directly falsify “Connect Wire created a broken wire which RBW deleted.” `Wire.Is Broken?` (`6371004`) is the property that actually asks the proposed question; NI also defines RBW (`VI.Block Diagram:Remove Bad Wires`, method `0x410`) as removing broken wires. [Wire.Is Broken?](https://labviewwiki.org/wiki/Wire_class) · [Remove Bad Wires](https://labviewwiki.org/wiki/VI_class)

Conversely, your reading would gain strong support if, before RBW, the exact wire object reports `Is Broken? = TRUE`, `Terminals[]` contains the intended endpoints, and afterward that UID is absent from every relevant `Diagram.Wires[]` and the held sink terminal’s `Connected Wire` is null.

4. **A UID-equality gate over a net is not sound.**

A UID answers “is this the exact same GObject?” It does not answer:

- whether a source still reaches a sink;
- whether a wire is broken;
- whether a branch survived;
- whether LabVIEW replaced or canonicalized its wire representation;
- whether an index now denotes a different terminal.

UID reuse is even permitted after deletion. Use UID only as one field in an object snapshot, not as the survival criterion. [UID documentation](https://labviewwiki.org/wiki/GObject_class/UID_property)

**Cheapest discriminating test:** for one minimal two-sink case, retain the exact source and sink terminal references—do not re-index them—then snapshot these immediately before RBW:

```text
sink.Connected Wire            634A000
wire.UID                       632A813
wire.Is Broken?                6371004
wire.Terminals[]               6371003
each terminal.UID              632A813
each terminal.Is Source?       634A003
each terminal.Diagram          634A002
```

Optionally snapshot each relevant diagram’s `Wires[]` (`6375805`) and `VI.Get Errors` (`0x452`). Invoke RBW (`0x410`), then repeat the same reads from both the **held terminal reference** and a freshly indexed terminal reference.

- `Is Broken? = TRUE` before RBW and disappearance afterward supports your claim.
- `Is Broken? = FALSE`, preserved endpoint connectivity, or disagreement between held-reference and fresh-index results refutes it and identifies UID movement/index drift as the failure in F1v.

## Sources

(extract from answer)

## What was done with it

**verdict: REFUTED MY READING — accepted in full, and it invalidates the GATE, not just the explanation.**
Dispatched as the mandatory review of the failed prediction in `tools/bench/build_d1_v0_run9.log:272`
(`**FAIL** F1v every index-addressed wire SURVIVES Remove Bad Wires ... 3 of 8 deleted`). codex, `-Kind review`,
ANSWERED in 133 s (`tools/bench/peer_rbw_deletions.log`, `BGRUN END rc=0 after 134s`).

What it changes, stated narrowly and checked against our own code:

1. **The gate measures object identity, not survival.** `tools/recipes/build_d1_v0.py:1118-1121` classifies with
   `(survived if after == wire else died)`, where both values are reads of `Terminal.Connected Wire` 634A000 —
   `Terminal.Connect Wire` 6349C03 returns nothing, so the "creation-time wire uid" was never an identity token.
   CONFIRMED against the log: `RBW-DELETED #1359 t4 ... wire 26189 -> 26412` ends with a **NON-ZERO** wire on the
   terminal. That row is not a deletion at all. So the honest count is **at most 2 of 8 became null, and 1 of 8
   changed wire identity** — not "3 deleted".
2. **`Wire.Is Broken?` 6371004 is the property that actually asks our question, and we never called it.** This is
   the second time a broken-wire cause has been reached by inference rather than read from the machine
   (CLAUDE.md, "When a diagnosis is GUESSED twice, build the reader" — which already names `Wire.Is Broken?`
   6371004 and `VI.Get Errors` 452 as the readers identified and still missing).
3. **A second, independent alternative we had not considered: terminal-INDEX drift.** The recipe re-resolves
   `Diagram[d].Nodes[n].Terminals[t]` after every call, and LabVIEW creates/removes border tunnels as wires cross
   structures (measured in this project: `LoopTunnel 0 -> 2`, `toolkit-capabilities.md` OpConnectNested_v1 row).
   `T[4]` after the edits need not denote the terminal `T[4]` denoted before them, so a null read can mean "we
   looked at a different terminal", not "the wire is gone". The suspicious detail codex points at is real: row 1's
   `T[4]` came back holding **26412**, the uid of the *later* cross-diagram connection.
4. **The `delta 0` row is explained without any defect.** `#29874 t4 <- 8885` reported wire 26189 with a total
   Wire-count delta of 0 because a second sink on an existing net enlarges the net; NI's wire model is one source,
   many sinks. This matches `docs/NAMES.md:52` ("already-wired source -> silent BRANCH (Wire count unchanged)").

**Actions taken here:** (a) the F1v gate is recorded as UNSOUND in `docs/d1-build-plan.md` §11u and
`docs/d1-route-b-plan.md` §6 R2, and must not be cited as evidence that `OpConnectNested_v1` makes broken wires;
(b) the claim "3 of 8 wires were deleted by RBW" is withdrawn from STATUS OPEN 36 and replaced by the measured
statement in point 1; (c) the reader codex prescribes (`Wire.Is Broken?` 6371004 + `Wire.Terminals[]` 6371003 +
`Terminal.Diagram` 634A002, snapshotted from a HELD terminal reference rather than a re-indexed one) is written
into `docs/d1-route-b-plan.md` as the acceptance instrument route B's wiring needs. It is **not built here** — a
material session may not authorise a new op beyond the one its brief names (CLAUDE.md §3), and this one is a
second op.

**Not adopted, and why:** nothing. The four points above are all either confirmable against files already in this
repository (points 1 and 4, confirmed above) or are explicitly labelled here as unmeasured alternatives (points 2
and 3). No property id from this exchange is written into `docs/NAMES.md` until it is attached and measured.
