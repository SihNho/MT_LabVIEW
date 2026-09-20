# moveinto-stale-in-memory-vi

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-17
- **outcome:** ANSWERED (97s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

FAILED PREDICTION. Attack the diagnosis below; I am not asking whether it sounds reasonable.

WHAT WAS PREDICTED. tools/recipes/probe_move_into_v0.py phase 1 begins by making a FRESH working copy of a donor
op VI and reading it:
    if os.path.exists(OPIN): os.remove(OPIN)
    shutil.copyfile(DONOR_OP, OPIN)          # DONOR_OP = ...\claudeDev\OpMoveOut_v0.vi ; OPIN = ...\OpMoveIn_v0.vi
    g.open_panel(OPIN); walk(OPIN, 0)
The prediction (gate P1b, rev 7) was that `walk()` would report the DONOR's 15 nodes - including Property uid 744
(VI.Block Diagram) feeding the Move's `owner`, and IndexArray uid 236 feeding a 3-sink net (Property 237,
Property 240, Invoke 741) - because that is what OpMoveOut_v0.vi contains on disk (ExecState 1, Node 15, Wire 29,
measured 2026-09-17 in tools/bench/diag_movein_p1_break.log).

WHAT WAS OBSERVED (tools/bench/probe_move_into_v0.log, the block after `BGRUN START 2026-09-17 05:15:56`):
  donor copy ExecState 0  nodes 15 wires 29
  node[14] uid 148: ... 'GObject'>=w970 ... 'UID'<=w978, 'Owning VI'<=w467      <- `UID to GObject Reference.vi`
  node[13] uid 741: 0:'reference'<=w970 ... 8:'owner'<=w645
  (uid 744 ABSENT; uid 683 present; uid 236 'element'>=w0 i.e. BARE; 237/240 'reference'<=w0 BARE)
  FACT wire 970 net: SOURCE [(148, 2, 'GObject', True)], collateral SINKS (besides the Move) []
  **FAIL** P1b ... {} (0 = still bare)
That is NOT OpMoveOut_v0.vi. It is EXACTLY the artefact the PREVIOUS run (2026-09-17 04:55, same log) left in
memory: U2G dropped as uid 148, `Move.reference` fed from it, `Move.owner` fed from the Diagram cast 683, wire 464
already deleted, Property 744 already deleted, ExecState 0.

MY DIAGNOSIS, which I want attacked: the SAME LabVIEW process (pid 21512, alive since before 04:55; handle count
30,812 read at the start of this run) still holds `...\claudeDev\OpMoveIn_v0.vi` OPEN IN MEMORY with run 2's
unsaved edits, because run 2 called g.open_panel(OPIN), failed at gate P1, and returned without closing it. The
Python side then deleted and re-created the FILE, but `Application.GetVIReference(path)` returned the VI ALREADY
IN MEMORY under that path, so every subsequent read and edit went to run 2's in-memory object and the disk
overwrite was invisible.

ALREADY RULED OUT (do not re-raise):
 - the wrong donor path: DONOR_OP is a literal, and the same literal produced the correct donor in run 2
   ("donor copy ExecState 1 nodes 15 wires 29", uid 744 present);
 - a partial copy: shutil.copyfile raised nothing and the file exists;
 - the original VI - never opened for writing, md5 2a78e17c449cacdaf5da389818526859 verified before and after.

WHAT I NEED: the strongest reason this diagnosis is WRONG; an alternative explanation of the same evidence; the
observation that would FALSIFY it; and the CHEAPEST discriminating test. Also: what is the CORRECT way, in VI
Server scripting from an out-of-process client, to guarantee that a path is re-read FROM DISK - VI.Revert? closing
every reference? a uniquely-named working copy per run? - and which of those actually EVICTS a VI from LabVIEW's
memory rather than merely closing its front panel.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

## 1. Strongest reason the diagnosis is wrong

The evidence does **not identify the failed `g.open_panel()` call as the thing retaining the VI**. It establishes only that `GetVIReference(OPIN)` returned a previously edited in-memory instance. The same instance could instead be retained by another automation reference, an open panel, a project/application hierarchy, or another caller. NI explicitly warns that a VI remains resident while references or other ownership relationships exist, and that reference closure does not necessarily dispose it immediately. [NI: Closing References in LabVIEW](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html)

Thus, “stale in-memory VI” is strongly supported; “specifically the reference leaked by `g.open_panel()`” is not yet demonstrated.

The PID and handle count add almost nothing: neither identifies which VI is resident or which reference owns it.

## 2. Alternative explanation

A competing explanation is a **post-copy disk race**:

1. `copyfile()` successfully copied the donor.
2. Another still-active helper or cleanup path subsequently rewrote `OPIN` with run 2’s modified state.
3. `GetVIReference()` then loaded that state legitimately from disk.

“No exception from `copyfile()`” proves that the copy completed, but not that the destination remained unchanged until `GetVIReference()`. This alternative predicts the same nodes, UIDs, and `ExecState 0`.

A second alternative is that the VI was resident for a reason other than the returned top-level COM object—such as another VI reference or an open hierarchy. NI documents that closing one reference is insufficient when another reference or ownership relationship remains. [NI: Closing References in LabVIEW](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html)

## 3. Observation that would falsify the diagnosis

The diagnosis is falsified if, immediately before `GetVIReference(OPIN)`:

- a helper executing inside the relevant application instance reports that `OPIN` is absent from **All VIs in Memory**;
- the donor and destination have identical byte hashes;
- and `walk(OPIN)` nevertheless returns run 2’s graph.

NI specifically recommends **All VIs in Memory** to determine when a VI has actually left memory; ordinary reference closure is insufficient because disposal can be asynchronous. The property may require a helper running inside LabVIEW because remote access to it is restricted. [NI: Closing References in LabVIEW](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html), [NI: calling internal properties externally](https://forums.ni.com/t5/Developer-Center-Resources/Calling-Internal-LabVIEW-Properties-Externally/ta-p/3518788)

Restarting the same LabVIEW application instance and reproducing the stale graph from a hash-verified donor copy would also falsify same-process retention.

## Correct disk-reload procedure

- **`Revert VI`**: This is the direct operation for an already-resident VI. It discards its in-memory edits and reloads the VI from disk. It refreshes the existing VI object; it does **not evict** it. [NI’s changed-on-disk guidance](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000kEssSAE)

- **Close every reference**: This can permit eviction only after every explicit reference and other reason for residency is gone. Disposal may occur asynchronously, so closing and immediately reopening introduces a race. Confirm absence through **All VIs in Memory** before reusing the pathname. [NI: Closing References in LabVIEW](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html)

- **Close Front Panel**: This closes the window, not the VI Server references. It is not an eviction guarantee. NI treats closing a panel and closing references as distinct operations. [NI: programmatically closing VI panels](https://knowledge.ni.com/KnowledgeArticleDetails?OpenDocument=&id=kA00Z0000019SItSAM)

- **Unique working copy per run**: Use a unique **filename**, not merely a unique directory. This does not evict anything, but it prevents a previous object under the old identity from satisfying the new `GetVIReference()` request. Open VI Reference either returns an existing in-memory VI or dynamically loads one from disk. [NI: Creating a VI Server Application](https://www.ni.com/docs/tr-CY/csh?context=lvcore_lvhowto_vi_server)

For a production recipe, unique per-run names are the most deterministic approach. For deliberate reuse of one path, use `Revert VI`, or release everything and wait until the VI is observably absent before replacing and reopening it.

After all four attacks, I still think the **broad stale-in-memory diagnosis is the best fit**. What remains unproved is the narrower attribution to `g.open_panel()` rather than some other retaining reference. Seeing `OPIN` absent from All VIs in Memory immediately before the bad read would change my mind.

**Cheapest discriminating test:** in the same LabVIEW process, copy the same hash-verified donor bytes to both `OpMoveIn_v0.vi` and a nonce filename such as `OpMoveIn_probe_051556.vi`; open and walk the nonce copy first, then the fixed-name copy. If the nonce shows uid 744/236/237/240 correctly while the fixed name shows run 2’s state, the disk-race alternative loses and in-memory identity reuse wins.

## Sources

(extract from answer)

## What was done with it

ANSWERED (codex, review). **Adopted, with its narrowing accepted.** The peer agrees the broad diagnosis
(stale in-memory VI served by `GetVIReference(path)`) is the best fit and refuses the narrow attribution to
`g.open_panel()` specifically — that attribution is dropped from the recipe's comment, which now says only that the
same process still held the path in memory with run 2's unsaved edits.

Acted on, in `tools/recipes/probe_move_into_v0.py` rev 7b, before this answer arrived and unchanged by it:

* **A unique working-copy FILENAME per run** — `OpMoveIn_v0_<epoch>.vi` — which is exactly the remedy the peer
  ranks first (*"For a production recipe, unique per-run names are the most deterministic approach"*); it prevents
  identity reuse rather than trying to evict anything. The canonical `OpMoveIn_v0.vi` is written at the END as a
  byte copy (`retire_working_copy()`), never by a LabVIEW save, so no instance holds it open.
* **Gate P1z** — the working copy must read ExecState 1, 15 nodes and NO `UID to GObject Reference.vi` before a
  single edit is made. Nothing in runs 1-3 ever checked WHICH VI it was editing.

**The peer's cheapest discriminating test is what P1z now runs.** Its prediction: the nonce copy shows the donor
(uid 744 / 236 / 237 / 240, ExecState 1) while the fixed name would still show run 2's state ⇒ in-memory identity
reuse wins and the disk-race alternative loses. Result in `tools/bench/probe_move_into_v0.log`, the block after
`BGRUN START 2026-09-17 05:2x`.

Recorded and NOT acted on (it is a new reader, and the frozen-scope rule of `cycle15-plan.md:102-105` applies):
**`Application.All VIs in Memory`** is the only honest test of "has this VI actually left memory"; a closed
reference and a closed front panel are neither of them evictions, and disposal is asynchronous. If a future cycle
ever needs to REUSE a fixed op path inside one LabVIEW session, that reader is the precondition.
