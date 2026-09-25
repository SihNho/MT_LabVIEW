---
type: peer-review
status: historical
date: 2026-09-17
tags: [peer-review, archive, labview]
disposition: legacy
legacy_note: closed as legacy 2026-09-25 by card chat-L1 (cutoff 2026-09-22; user 2026-09-25 lint order before runner resume)
---

# d1-s3-stale-traverse-index

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-17
- **outcome:** ANSWERED (166s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

A node landed in the wrong container and I want my explanation attacked before I change the addressing scheme.

FACTS from tools/bench/build_d1_v0_run2.log (2026-09-17, LabVIEW 2026 VI Scripting over COM, read-only quotes):
- Three While loops were created one after another on the same parent diagram. The creation step reports, for each, the new body diagram and the Traverse index that a fresh 'new_since' read gave AT THAT MOMENT:
    ':19  1.2: WhileLoop #1133, body Diagram #1170 at Traverse index 20'
    ':20  1.5: WhileLoop #1134, body Diagram #1194 at Traverse index 20'
    ':21  1.7: WhileLoop #1135, body Diagram #1215 at Traverse index 20'
  All three report index 20.
- Afterwards the Traverse list of WhileLoops reads [1135, 1134, 1133, 25380, 637, 15173] - the three new ones in REVERSE creation order, ahead of the three pre-existing ones.
- The first node move then used the index cached for 1.2 (20) and the node landed in Diagram #1215 owned by WhileLoop #1135, i.e. in the loop created LAST: 'S3 #5540 -> 1.2 owner Diagram#1215 (want Diagram#1170); owner(owner) WhileLoop#1135 (want WhileLoop#1133)'.
- The move operation addresses its destination by Traverse CLASS+INDEX, not by UID. The owner readback is by UID and is independently verified (it echoes the object's own UID and class).

MY EXPLANATION, which I want refuted: a Traverse index is not a stable handle. Each newly created diagram is inserted at the same position (20) and pushes the previously created one down, so an index captured before any later creation addresses a different object by the time it is used. The fix is to re-resolve the destination index from the destination's UID immediately before every move, and never to cache it.

COMPETING EXPLANATIONS I CONSIDERED:
(i) the move silently failed and the node stayed put - ruled out: it moved, just into the wrong diagram, and the owner chain resolves cleanly;
(ii) the index is interpreted against a different class list by the move op - possible, and I cannot separate it from mine using these lines alone, because both predict 'index 20 is not #1170';
(iii) the creation step reported the index wrongly at capture time - I have no evidence either way.

WHAT I NEED: the strongest reason my explanation is wrong; an alternative account of three different diagrams all reporting index 20; what would falsify mine; and the cheapest discriminating test. Also: is re-resolving by UID before every mutation sufficient, or is there a known case where a Traverse index shifts DURING a single operation? Do not restate my reasoning back to me.

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

1. **Strongest reason the explanation is wrong:** it infers the ordering of the `Diagram` traversal from the final ordering of a different class, `WhileLoop`. The mutation indexes `Traverse("Diagram")`; `[1135,1134,1133,…]` describes `Traverse("WhileLoop")`. Nothing presented proves that loop bodies undergo the same permutation as their owner loops. Moreover, capture, re-resolution, and mutation use three separate implementations—`OpReport`, `OpReportAll`, and `OpMoveIn`—so their traversal roots/options/order have not been shown equivalent ([gscript.py](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:261), [build_d1_v0.py](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_d1_v0.py:260)). The observations prove that `(class="Diagram", index=20)` did not reliably identify `#1170`; they do not yet prove insertion-and-pushing caused it.

2. **Alternative explanation:** `OpMoveIn` and the reporter enumerate different effective lists—because of a different traversal target, recursion/callback configuration, stale loaded VI reference, or implementation detail—so index 20 means `#1170` to the capture path but `#1215` to the mutation path. Traverse is normally used by enumerating returned references and matching an identity such as UID, rather than treating array position as identity ([NI Community example](https://forums.ni.com/t5/LabVIEW/finding-insane-objects/m-p/3844242)). NI explicitly defines UID—not an enumeration index—as the persistent identity and recommends checking class or label as protection against UID reuse after deletion ([NI UID documentation](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/uid.html)).

3. **Falsification:** your insertion account is falsified if full `Diagram` UID vectors, obtained through the same traversal path after each creation, do not show:

   - after 1.2: `20 → #1170`
   - after 1.5: `20 → #1194`, `21 → #1170`
   - after 1.7: `20 → #1215`, `21 → #1194`, `22 → #1170`

   It is also falsified more decisively if `OpMoveIn` reads back its selected destination as `#1170` immediately before invoking `Move`, yet the node ends under `#1215`; that would implicate `Move`, an invalid/stale reference, or uncontrolled concurrent mutation—not index displacement.

4. **Re-resolving externally before every mutation is not sufficient in principle.** The current `diag_index()` traverses with `OpReportAll`, returns an integer to Python, and then `OpMoveIn` performs another traversal. That remains a time-of-check/time-of-use boundary and does not eliminate traversal-path mismatch. The robust operation accepts the destination UID, resolves that UID to a `Diagram` reference inside the same VI invocation, verifies UID and class, and wires that exact reference directly into `Move`; then it verifies the resulting owner chain. NI documents UID as unique within a VI and stable for an existing object, subject to possible reuse only after deletion ([NI UID documentation](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/uid.html)).

I found no documented case of a Traverse array’s index “shifting underneath” an already-selected reference during one properly data-dependent operation. Once Traverse has produced its reference array and the selected reference is wired into `Move`, LabVIEW dataflow requires the consumer to execute after its input producer completes ([NI dataflow documentation](https://www.ni.com/docs/en-US/bundle/labview/page/block-diagram-data-flow.html)). A concurrent, unordered editor could still mutate the target because LabVIEW permits simultaneous execution; closing the parent VI or deleting the referenced object can invalidate a child reference ([NI reference-lifetime documentation](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html)). Under this project’s single-execution-path rule, a fused UID-to-reference-to-Move operation should close that exposure.

After the attack, I still think the narrow conclusion—**never persist a Traverse index as object identity**—holds. I do **not** think “new diagrams push older ones down” is proven, and I would replace the proposed integer re-resolution with direct UID-to-reference mutation.

**Cheapest discriminating test:** on one scratch target, after each of the three loop creations print `Diagram` indices 18–23 from the exact reporter used by `new_since`; immediately before one sacrificial move, have a read-only/preflight copy of `OpMoveIn` expose the UID of the destination reference selected by index 20. Matching vectors plus `#1215` from both paths supports insertion/pushing; disagreement at index 20 proves traversal-path mismatch. This follows the project’s LabVIEW automation skill guidance to treat Traverse order as non-identity and verify by UID/owner.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)

## What was done with it

**OUTCOME: ANSWERED (codex, gpt-5.6-sol, 167 s).** It granted the narrow conclusion — **never persist a Traverse
index as object identity** — and attacked two things:

1. **It does NOT accept "new diagrams push older ones down" as proven.** Fair: three creations each reporting
   index 20 is equally consistent with a traversal-path mismatch between the reporter and the move op. **Not
   adopted as a fact anywhere** — the recipe's comment states what was *observed* (all three reported 20; the
   move landed in the last-created body), not a mechanism.
2. **It rejects integer re-resolution as sufficient in principle**: `diag_index()` traverses in one VI call and
   `OpMoveIn` traverses again, so a time-of-check/time-of-use window remains, and the robust form is an op that
   takes the destination **UID**, resolves it to a reference *inside the same call*, checks UID and class, and
   wires that reference into `Move`.

**Disposition:** finding 1 accepted (nothing claimed). Finding 2 **accepted and ESCALATED** — a UID-addressed
`OpMoveIn` is a new op variant, frozen for D1's duration by `cycle15-plan.md:102-104`, and changing an op's
interface is not a material session's call. **What makes the residual risk tolerable now, and it is not an
argument from probability:** every move is followed by an owner-chain readback **by UID**
(`OpOwnerChain_v1`, with the identity echo), and the S3 gate fails the run on a mismatch — which is exactly how
run 2 caught this. A TOCTOU slip cannot pass silently; it can only cost a run.

**Applied:** `tools/recipes/build_d1_v0.py` re-resolves the destination from its UID immediately before every
move, before the GPU-kernel drop, before every after-pass walk, and re-resolves `frame_i`/`outer_i` after the
moves. No cached index survives a mutation anywhere in the file.

**Failure budget: 1 of 2 used for this class** (an object addressed by a stale index).
