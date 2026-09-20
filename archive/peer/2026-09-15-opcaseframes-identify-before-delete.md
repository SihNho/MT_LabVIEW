---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, vi-scripting]
---

# opcaseframes-identify-before-delete

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (22s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

VERY BRIEF (LabVIEW 2026 VI Scripting, confirm or refute). tools/bench/build_opcaseframes_v0.log run 2: your prescription was applied - the inherited TERMINAL readers were deleted (Terminal.Is Source? 634A003, Terminal.Connected Wire 634A000, Terminal.Diagram 634A002) because the Index Array element now carries Diagram references. The run then stopped on my own gate: I looked for the orphaned GObject.UID node by searching for a node whose reference sink wire is 0, and found none. MY EXPLANATION: deleting a node leaves its wire as a STUB (I measured that earlier in this session - the stub made a later connection a BRANCH), so the UID node fed by the deleted Terminal.Diagram still reports a non-zero reference wire and my search could not see it. FIX: identify that UID node BEFORE the deletions - it is the one whose reference wire equals Terminal.Diagram output wire - then delete the node, delete the stub wire explicitly, and wire the Index Array element into it. QUESTIONS: (1) confirm that in LabVIEW scripting a deleted node leaves the wire object behind rather than removing it, so post-deletion searches for unwired sinks are unreliable; (2) is deleting the stub wire explicitly the right move before rewiring that sink, or is it safe to wire into a sink whose wire has lost its source; (3) does Generic.Owner on a Diagram element really return the owning CaseStructure (you suggested it as a provenance check - I plan to gate that both frames report owner uid 5540). Read-only.

## Answer

1. **Confirm, with terminology caveat.** Your measured behavior supports it, and NI documents that loose/broken wire branches persist and require explicit removal. ?쏰rphaned/loose wire??is clearer than ?쐓tub,??which NI uses for the terminal?셲 wiring hint. Thus searching for `Connected Wire == 0` after deletion is unreliable. [NI wire documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

2. **Explicitly delete the cached wire first.** Identify/cache the UID node and wire reference before deleting `Terminal.Diagram`; delete that reader, delete the cached wire via `Generic.Delete`, then connect Index Array. NI?셲 accepted scripting prescription for disconnecting terminals is to delete the wire object. [NI Community](https://forums.ni.com/t5/LabVIEW/Disconnect-wire-through-VI-scripting/m-p/3047457)

3. **Refute the direct-owner assumption.** For a node inside a case frame, `Generic.Owner` returns the **Diagram/frame**; that Diagram?셲 `Owner` returns the **CaseStructure**. Therefore gate UID `5540` on `element.Owner.Owner`, with casts `Diagram` then `CaseStructure`, not directly on `element.Owner`. [NI Community example](https://forums.ni.com/t5/LabVIEW/Access-name-of-case-from-indicator-inside-case-using-VI/m-p/2329972)

## Sources

(extract from answer)

## What was done with it

(annotation below)

Applied exactly: the frame-uid node is identified and CACHED before the deletions (found by the wire that fed it),
then the reader node is deleted, the loose stub wire is deleted explicitly, and the Index Array element is wired in
fresh. `docs/NAMES.md` gained the general rule — a deleted node leaves its wire behind, so a post-deletion search
for "unwired sinks" cannot find the orphan it created. The owner-chain correction (a node's Owner is its frame
Diagram; that Diagram's Owner is the CaseStructure) is recorded there too.
