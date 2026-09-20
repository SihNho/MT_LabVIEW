# fstunnel-wire-fail-codex

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-18 09:08:18
- **outcome:** ANSWERED (112s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# FAILED PREDICTION — refute this framing

## What was predicted
`tools/recipes/build_opfstunnelterm_v0.py` (LabVIEW 2026 VI Scripting, driven from Python over ActiveX/COM via
`tools/gscript.py`) would build two operation VIs — `OpFsTunnelTerm_v0` (FlatSequence **outer** tunnel →
terminal) and `OpFsInnerTunnelTerm_v0` (inner tunnel) — and then perform a live read: given a tunnel UID on a
real VI, return the terminal reference and its owner. The recipe had passed its prior-art release (4/4) and the
launch gate said ALLOW. Prediction: the build completes and the live read happens.

## What was observed — twice, byte-identical, in two independent runs
Both runs: `BGRUN END rc=1` after 91 s / 92 s. Gates 7 pass / 1 fail; the failing gate is only
"the run completed without an unhandled exception". Gates B4/B5/L1/L1b/L2/L3/L3b/L3c/I2/T2/L4/L4b never executed.

Both runs die at the same line with identical numbers:

```
build_opfstunnelterm_v0.py:392 -> gscript.py:1330
RuntimeError: wire specific class reference->reference: wire count 40->40 with 0 new tunnel(s),
expected 41 (if the source is already wired this may be a successful BRANCH - re-call with branch=True)
```

The wire being attempted is: the **cast output of a "To More Specific Class" (TMSC) node → the `reference`
input of a Property Node (called PN_A in the recipe)**.

The log lines immediately before it, identical in both runs:

```
:46  deleted Node #145
:47  deleted Node #151
:53  PN_A uid 145 (Nodes[17], OuterTerminal); new control(s) ['reference 4']
:55  deleted the seed->PN_A wire #1651
:56  seed 'reference 4' -> TMSC 'target class' wire 1457
:58  RuntimeError (above)
```

Note line :46 vs line :53 — **the newly created Property Node was assigned UID 145, the UID a node deleted
moments earlier in the same VI had held.** The recipe addresses PN_A afterwards by a uid-indexed lookup of the
form `cidx(op, "Property", 145)`.

## The two explanations already on the table (attack both — neither has been discriminated)
- **(a) UID reuse.** LabVIEW re-issued uid 145 to the new Property Node after the old node holding it was
  deleted, so the later uid-indexed lookup resolves to the wrong or a stale object, and `Connect Wire` silently
  declines (0 new wires rather than an error).
- **(b) Already-wired source/sink.** `create_control` left PN_A's `reference` input in a state the wire helper
  reads as needing `branch=True` — i.e. the attempt really was a branch, and the helper's before/after wire
  count is simply the wrong success test for a branch.

## Already ruled out
- Not a gate/permission problem: no gate (guard_cycle / guard_peer / prior-art launch gate / guard_bash) refused
  either launch; the failure is inside the recipe.
- Not nondeterminism or a dirty instance: two independent runs produced identical uids, identical wire counts
  and an identical failure line; handle count did not grow (30,735 → 31,319; run 2 → 30,941; fresh ≈31,500).
- Not damage to the source material: both original VIs are byte-identical before and after both runs (md5
  `c39f36e0675339673b707c59f0784fee`, `2a78e17c449cacdaf5da389818526859`); nothing was saved.
- Not a missing class: a separate probe in the same run confirms `VI Server:FlatSequenceOuterTunnel` exists and
  is reachable (uid 43605 is one; n=58 in the file).

## A separate measured fact from the same run — say whether it changes the picture
On class `VI Server:FlatSequenceOuterTunnel`, the property ids `6356001` (Tunnel.Outside Terminal), `6356000`
(Tunnel.Inside Terminals[]) and `7CC75C00` (OuterTerminal.Tunnel) are **all refused with error 1077**. The
recipe instead relies on FlatSequence-specific ids measured earlier (`FlatSequenceOuterTunnel` `3195B800/1/2`,
`FlatSequenceInnerTunnel` `1C3A9000-3`).

## What you are asked to do
Do not confirm any of the above. Give: the strongest reason this framing is wrong; at least one alternative
cause neither (a) nor (b) covers (including the possibility that the *wire helper's success test* — counting
wires on the diagram before and after — is invalid for this node pair, or that a Property Node's `reference`
input cannot accept a wire while the node still carries a class-typed property list); what observation would
falsify each candidate; and the single cheapest discriminating test, stated as a concrete read we can run
against LabVIEW rather than a comparison of options.



--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The strongest reason the framing is wrong is that the exception reports a failed Python assertion, not a failed LabVIEW connection. `gscript.wire()` considers every non-boundary, non-`branch=True` connection successful only if the diagram gains a Wire object ([gscript.py](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:1322)). But LabVIEW wires have one source and potentially many destinations, so adding a destination can modify an existing Wire object without increasing the object count. [NI describes that one-source/many-reader wire model explicitly](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html).

More importantly, the recipe itself supplies a concrete untested source of such a branch:

- It discovers `tmsc` by requiring its `specific class reference` output to share the wire entering the soon-to-be-deleted `pn_terms` ([recipe line 327](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_opfstunnelterm_v0.py:327)).
- It deletes `pn_terms`, `w_terms`, `el_w`, and `w_targetclass`, but never records or deletes the wire on the TMSC output ([recipe line 342](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_opfstunnelterm_v0.py:342)).
- Gate B2 checks the old consumers and TMSC’s `target class`; it does not check TMSC’s `specific class reference` output ([recipe line 359](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_opfstunnelterm_v0.py:359)).

Thus the best alternative is a residual/dangling donor wire still attached to the TMSC output. Connecting PN_A could have successfully added a sink to that existing Wire object, yielding exactly `40 → 40`. That is neither UID corruption nor evidence that `create_control` left PN_A wired.

UID reuse is especially weak causally because `cidx()` does not pass UID 145 to the wiring Op. It performs a fresh `report_all("Property")`, converts UID 145 into the current class-list index, and passes that index ([recipe line 270](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_opfstunnelterm_v0.py:270)). Reuse matters only if that fresh enumeration resolves to the wrong live object—not merely because 145 belonged to an earlier, deleted object.

Falsifiers:

- **UID/stale-object explanation:** falsified if the fresh Property enumeration at `cidx`’s returned index reports UID 145, property `OuterTerminal`, and the expected `reference` terminal.
- **`create_control` left PN_A already wired:** falsified if PN_A’s `reference` terminal reports Connected Wire UID 0 immediately before the attempted connection.
- **Residual donor-wire/helper false-negative explanation:** falsified if TMSC’s `specific class reference` terminal reports Connected Wire UID 0 immediately before the call, or if after the raw call PN_A remains unwired.
- **Property Node cannot accept the typed wire while carrying its property list:** falsified if both endpoints report the same nonzero Connected Wire UID after the call. It is also contrary to NI’s documented TMSC pattern, which specifically wires the cast output into a class-specific Property Node ([NI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YHhtCAG)).
- **Wrong endpoint/class mismatch:** falsified by that same shared-wire read plus the expected UID/property identity.

The error-1077 measurement does not change this diagnosis. Error 1077 means “invalid property value,” so it says those generic IDs are invalid for that class/context; it says nothing about whether this wiring operation succeeded ([NI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P6FSSA0&l=en-US)). It supports retaining the measured FlatSequence-specific IDs, but is orthogonal to the `40 → 40` exception.

**Cheapest discriminating test:** at the failing state, invoke the raw OpWire once without `gscript.wire()`’s count assertion, then make one reporter read returning the `wire` fields for TMSC `specific class reference` and PN_A `reference`. If they are the same nonzero UID, the connection succeeded and the helper’s wire-count test is the failure; if TMSC is nonzero and PN_A is zero, LabVIEW declined the connection; if both are zero, there was no branch and the endpoint resolution must be investigated.

## Sources

(extract from answer)

## What was done with it

ACCEPTED, and since CONFIRMED FUNCTIONALLY by the cycle-22 judgement session, 2026-09-18. The diagnosis that the
`:392` failure was a FALSE NEGATIVE of `gscript.wire`'s Wire-count test on a branch — `tools/gscript.py:1327-1329`
says so in its own comment — was acted on: the six wire sites were rewritten to pass `branch=True` and verify by
effect (equal, non-zero wire uid at both ends). In the first run of the patched recipe **all six sites passed**
(`tools/bench/build_opfstunnelterm_v1_run1.log:57-68`: `src 384 -> dst 384`, `1694/1694`, `1719/1719`,
`1766/1766`), where the unpatched bytes had died at the first of them twice. So the count test was the defect and
the branch semantics were right.

Two limits of that acceptance, recorded so the next cycle does not overread it:
- Verifying by effect is NOT sufficient — equal uids also read identically across a BROKEN type-incompatible wire
  (`docs/NAMES.md:861-867`). The recipe still fails at gate B4 with `ExecState 0`, and the leading hypothesis is now
  the un-deleted residual stub wire #384 this branch was taken from
  (`archive/peer/2026-09-18-fstunnel-v1-b4-execstate0-{codex,opus}.md`, both ANSWERED and both refuting the
  unwired-terminal explanation).
- `gscript.py` was deliberately NOT patched, so the count test still misreads a successful branch for every other
  caller; only this recipe's local helper avoids it.
