---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, archive, labview]
disposition: legacy
legacy_note: closed as legacy 2026-09-25 by card chat-L1 (cutoff 2026-09-22; user 2026-09-25 lint order before runner resume)
---

# frameloop-seam-77-crossings

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **date:** 2026-09-15
- **outcome:** ANSWERED (194s)
- **why asked:** `boundary_manifest.py 43` had just run, and my reading of it was about to decide the project's
  strategy (graft into a copy of the original vs. the fresh seven-loop rebuild). Dispatched before acting, per
  rule 5.
- **verdict:** REFUTED, and the refutation was right on both counts — confirmed by measurement the same hour
  (`tools/bench/slice_cutset_acq_track.py`). (1) The manifest audited all 75 nodes of diagram 43, so it could say
  nothing about a smaller slice; the kernel's measured backward+forward slice is **22 nodes**, and the ASI focus
  subVI #48 and the EventStructure #10153 are both **outside** it — my "no clean acquisition/tracking region
  exists" was wrong. (2) `to_invisible_object` (77) is `len(net) == 1`, "only one end was visible to the node
  walk"; it never resolves the far end, so it conflates a loop-border tunnel with a constant or a front-panel
  terminal, and `leaves_the_seam` was 0 by construction because the seam was every uid in the diagram. The
  corrected numbers: **21** nets cross from the slice to sibling nodes, 18 are internal, 49 already run to the
  loop border. Consequence: subVI EXTRACTION of the slice is still impossible (21 + 49 ≈ 70 terminals against a
  28-terminal connector pane), but IN-PLACE replacement is not blocked by interface width at all.

## Question

ATTACK THIS READING of a measurement. Log: tools/bench/boundary_manifest_frameloop.log, script tools/bench/boundary_manifest.py, prior art docs/restructure-plan-4.6.md section 4. MEASURED on diagram 43 (the main VIs frame loop, 75 nodes): 77 wires classified to_invisible_object (a net with exactly one member inside the seam); 0 leaves_the_seam; INSIDE the seam 1 EventStructure, 10 Property nodes, 6 SubVIs including the tracking kernel 5058, get-buff-image 6810 and uid 48 which carries VISA resource name / In position terminals; 0 Locals, 0 Globals, 0 FeedbackNodes. Tool verdict: HAZARD INSIDE - move the seam. MY READING, attack it: (1) the 28-terminal connector-pane limit that killed the 2026-09-13 seam does NOT directly apply here, because replacing the frame loops CONTENTS in place needs tunnels and shift registers, not a subVI connector pane, so 77 crossings is legal-but-ugly rather than impossible; (2) the decisive finding is instead that the frame loop is NOT a clean acquisition-plus-tracking unit - it also contains motor VISA I/O and an Event Structure - so the outcome reviews instruction to replace only the acquisition/tracking hot path does not correspond to any actual region of this VI; (3) therefore the copy-the-original-and-graft strategy is not a small surgical change, and the standing plan to rebuild the seven-loop top level fresh still stands. ALSO CHALLENGE: is to_invisible_object even the right metric for an in-place replacement, or am I reusing a number that was defined for subVI extraction?

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The claim is wrong because the measurement audited the whole of diagram 43, not the proposed acquisition/tracking hot-path seam.

1. Strongest reason

The existing wire graph already identifies a real acquisition/tracking slice: `get buff image` #6810 directly feeds kernel #5058, whose measured backward and forward slices contain neither motor/focus #48 nor EventStructure #10153. Therefore, their presence elsewhere in diagram 43 does not establish that they must participate in an in-place graft. See [frame-loop-wire-graph.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/frame-loop-wire-graph.md>).

This also matches 짠4?셲 own statement that functional grouping remains recoverable topologically despite the scrambled layout ([restructure-plan-4.6.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/restructure-plan-4.6.md:111>)). The manifest selected every UID in diagram 43, so it cannot answer whether a smaller topology-defined selection exists.

2. Alternative explanation

Diagram 43 is a mixed container holding several sibling activities. Acquisition/tracking is one subgraph; motor/focus and UI-event handling merely share the enclosing frame loop.

Indeed, the prior graph places EventStructure #10153 in its own one-node component after the documented plumbing cut. That is evidence for separability, not evidence that the hot path necessarily includes the Event Structure.

The verdict also means only ?쐔his whole-diagram seam contains an EventStructure.??Its code ignores Property and SubVI nodes when calculating `clean` and says nothing about whether a smaller seam or direct node substitution is viable ([boundary_manifest.py](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/boundary_manifest.py:93>)).

3. What would falsify the claim

A resolved, node-selected boundary manifest showing that the minimal subgraph from acquisition #6810 through kernel #5058 to the required consumers:

- excludes #48 and #10153,
- has no indispensable paths through them, and
- has a manageable set of actual cut nets/state carriers,

would falsify ?쐍o actual acquisition/tracking region exists.??The existing backward/forward slice is already substantial evidence in that direction.

The converse?봢very valid acquisition/kernel slice necessarily pulling in #48 or #10153?봶ould support the claim, but that observation has not been produced.

4. `to_invisible_object` is the wrong metric

It is explicitly defined as `len(mem) == 1`, meaning only one terminal was visible to `net_map`; it never resolves the missing endpoint or tests whether it lies outside a node selection ([boundary_manifest.py](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/boundary_manifest.py:82>)). Furthermore, `leaves_the_seam` compares nodes returned from diagram 43 against a set containing every diagram-43 UID, making zero the expected result for this invocation.

More decisively, the earlier complete accounting explains all 83 such half-edges as:

- 29 frame-loop tunnels,
- 22 shift-register connections,
- 7 nested-structure tunnels,
- 17 front-panel terminals,
- 8 constants.

Thus `to_invisible_object` conflates genuine loop-boundary state with entirely internal invisible endpoints. Neither 77 connector terminals nor 77 in-place tunnels follows from it. NI also documents that one wire may fan out to multiple consumers, reinforcing that wire-object counts are not automatically interface-terminal counts ([NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)).

The fresh seven-loop rebuild may remain preferable for readability or broader architectural reasons, but this measurement does not establish it.

Cheapest discriminating test: using the already-saved `main_vi_nodeterms.json`, compute an offline UID-selected cut around #6810 ??#5058 plus only its required state feeders, then report the resolved cut nets and whether #48 or #10153 enters that slice?봭o LabVIEW rerun required.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
