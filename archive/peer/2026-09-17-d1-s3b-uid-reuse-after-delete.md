# d1-s3b-uid-reuse-after-delete

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-17
- **outcome:** ANSWERED (68s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

A gate designed to catch silently-bared terminals fired, and I believe it fired on an artefact rather than on the defect it was built for. Attack that before I weaken the gate.

FACTS from tools/bench/build_d1_v0_run4.log (LabVIEW 2026, VI Scripting over COM, one client, read-only quotes):
- Setup: a subVI call with UID 5058 was DELETED from a diagram, and immediately afterwards a different subVI was dropped onto another diagram in the same VI.
- ':108 S3e #5058 deleted and GPU_kernel_v1 dropped into 1.2  new subVI [{i: 20, class: SubVI, uid: 5058, pos: (5493, 3118), owner: Diagram}], SubVI count 98 (want 98)' - the NEW subVI came back with UID **5058**, the uid the deleted one had.
- A census compares each watched node's terminals before and after the edits and reports any that went wired -> bare. It reported exactly 13, ALL on uid 5058, and they are exactly the deleted node's 13 wired terminals (wires 5637, 3040, 373, 5859, 505, 5975, 121, 42, 3512, 3646, 7429, 3912, 4027).
- Every other watched node that did NOT move kept every wire: the same run reports ':110 S3b-d19 ... []' and a shift-register census with no change.
- The gate's purpose: catch the case where a wire is a NET and a move bares a terminal on a node that never moved - a silent bare terminal, no broken wire, nothing for Remove Bad Wires.

MY EXPLANATION, which I want refuted: LabVIEW reused UID 5058 for the newly dropped subVI, so the 'after' read addressed a DIFFERENT object than the 'before' read, and the 13 entries are the deleted node's own terminals, not collateral damage. The fix is to exclude a deliberately deleted uid from the census, keyed on the delete, not to relax the gate.

COMPETING EXPLANATIONS I CONSIDERED:
(i) the new subVI really was dropped onto the old node's terminals somehow - I see no mechanism, but both explanations predict 'uid 5058 has 13 bare terminals afterwards';
(ii) the delete did not happen and what I see is the ORIGINAL node with its wires cut by the moves - the SubVI count returning to 98 after a delete plus a drop is consistent with either;
(iii) uid reuse did not occur and the reporter is misreporting the new node's uid.

WHAT I NEED: is UID reuse after deletion within one VI documented behaviour in LabVIEW 2026, and how quickly - same session, same edit batch? The strongest reason my explanation is wrong; what would falsify it; and the cheapest discriminating test that distinguishes (i)/(ii)/(iii) from a log line alone. Also: if uids are reused this readily, what is the correct stable identity for a before/after census of a mutated diagram? Do not restate my reasoning back to me.

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

1. **Strongest reason the claim is wrong as a conclusion**

The log never establishes object continuity or replacement independently of UID 5058. Both the “new subVI” classification and terminal census appear to rely on the identifier whose reuse is in dispute. That makes the evidence circular: it proves that two observations resolved to `5058`, not that the second observation was a newly allocated object.

NI documents that deleted-object UIDs *might* later be assigned to another object, but gives no guarantee that reuse is immediate, same-session, or same-batch. NI specifically recommends checking class or label in addition to UID. Because both objects are SubVIs—and labels may be absent—those checks would still be too weak here. [NI: GObject UID property](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/uid.html)

Therefore, immediate reuse is permitted by the documented contract, but this log does not prove that it happened.

2. **Alternative explanation**

The strongest alternative is reporter aliasing or stale reference resolution: the drop returned a different live object, but the reporting path associated it with `5058` through a stale COM/GObject reference, cached lookup, or UID-keyed table. The same contaminated lookup could then compare the deleted node’s saved terminal records against the new node’s bare terminals.

A less likely but still viable alternative is an incomplete/failed delete: the original `5058` survived while another operation failed, replaced an object, or was omitted from the count. The final count of 98 alone cannot prove the intermediate `98 → 97 → 98` transition.

3. **Observation that would falsify UID-reuse**

Any one of these would falsify the proposed sequence:

- Immediately after deletion and before dropping, a fresh full traversal still finds live object `5058`.
- The retained reference to the deleted call remains valid and reports its original callee and bounds.
- The direct reference returned by the drop reports a UID other than `5058`, while the reporter prints `5058`.
- The alleged new `5058` reports the original callee, original bounds, and original terminal/wire relationships.

Conversely, the convincing reuse signature is: old reference invalid, fresh traversal contains no `5058`, then the drop’s direct returned reference reports `5058` with the new callee and new bounds.

4. **Stable census identity**

There is no documented permanent built-in identity across deletion and recreation: NI explicitly allows a deleted UID to be reassigned. [NI: GObject UID property](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/uid.html)

For this gate:

- Retain the original GObject references for watched survivors; do not rediscover them by UID after mutation.
- Tombstone deliberately deleted references before comparing terminals.
- Give each census entry a harness-generated generation identity.
- Log a fingerprint alongside UID: class, owner identity, callee’s qualified VI path, bounds, connector/terminal signature, and label if present.
- Treat `(VI, UID)` only as a lookup hint, never as identity across destructive edits.

I still think UID reuse is the leading explanation, but it is not established by the quoted line. Proof of the intermediate absence plus the drop’s direct returned-reference properties would change that from plausible to demonstrated.

**Cheapest discriminating test:** add one compact log record containing three snapshots taken from direct references:

```text
old-before=(valid,uid,callee,bounds,wires);
old-after-delete=(valid/error);
fresh-after-delete uid5058=(absent|callee,bounds);
drop-return=(uid,callee,bounds,wires);
fresh-after-drop uid5058=(callee,bounds,wires)
```

That single record separates the cases: absence followed by a direct drop-return of `5058` proves reuse; a surviving old reference supports failed deletion; disagreement between `drop-return.uid` and traversal/reporter UID proves reporter misreporting; connected old wire IDs on the new call supports the “dropped onto old terminals” alternative.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)

## What was done with it

**OUTCOME: ANSWERED (codex, gpt-5.6-sol, 68 s).** It did not accept the explanation and the objection is right:
**the evidence is circular.** Both the "before" census and the "new subVI" classification resolve through uid
5058 itself, so the log proves that two observations resolved to 5058 — not that the second is a newly allocated
object. NI's contract *permits* a deleted uid to be reassigned and recommends checking class or label as well,
but both objects here are `SubVI`s, so that check is too weak.

**ACCEPTED, and the claim is downgraded in writing:** uid reuse is the **leading explanation, not a measured
fact**. Nothing in STATUS, the plan or the recipe asserts it as established; STATUS OPEN 27b says LabVIEW
"REUSED uid 5058" and that wording is corrected to *appears to have reused* with this file cited.

**The test that would settle it, for whoever writes PHASE "full"** (the peer's own, and it costs two reads):
traverse `SubVI` **after the delete and before the drop** — 5058 must be ABSENT — then read the drop's **directly
returned reference** and its callee/bounds. Absence followed by a drop-return of 5058 proves reuse; a surviving
old reference proves the delete failed; a disagreement between the drop-return and the reporter proves the
reporter misreports. Until then the S3b census must key the deleted node by **uid + the fact that we deleted it**,
excluding it explicitly, which is what the gate will do — it must not be relaxed.

**Failure budget: 1 of 2 used for this class** (a gate firing on an identity artefact).
