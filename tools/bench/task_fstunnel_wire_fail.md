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
