---
card: 171-a2-4
date: 2026-10-13
---
# Prior-art review input: the name-taint criterion patched into tools/stage_prerun.py (cards 171-a1-1 / 171-a1-2, PD412(b), PD413(a))

## What changed
`tools/stage_prerun.py` (now md5 af6937e84fbe857e571f19bb55301465; was db81a1d3) - the change is the diff
`tools/bench/diag_c171_a1_2_patch.diff` (read it in full). The offline dry-run (`stage_prerun.py --dry`) executes a
recipe against stubbed COM objects (`Fake`) plus a simulated graph. Before the patch, a gate (an assertion in the
recipe) was scored UNVERIFIED only when the gate's OWN statement touched a stub (card 134-1, per-statement taint);
a gate FALSE on simulated (non-stub) data FAILS the dry.

The patch adds a NAME taint: a name bound by a statement that touched a stub is TAINTED when its bound VALUE is
stub-shaped (`_stub_shaped`: a Fake, a container holding a Fake two levels deep, an EMPTY container, or unbound);
scalars and non-empty Fake-free containers stay CLEAN. A gate whose statement READS a tainted name is UNVERIFIED
instead of FAIL. Taint does not propagate through a clean statement (`x = c0` -> x clean). Names are per frame.

## Why
fp-103 (`tools/bench/gate_fp_queue.jsonl`): plan-170 dry gate A2 FAILed on `{6810: None, 22692: None}`, data that
came from a stub census (`tools/recipes/stage_replay_swap.py:39-42`), not from the graph. After the patch plan-170 A2
is UNVERIFIED (`tools/bench/diag_c171_a2_2_dry170.log:10,28`); self-tests `selftest_c134_1_dry` 11/0 (a FALSE gate
on simulated data still FAILS) and `tools/bench/selftest_c171_a1_1_taint.py` 9/0.

## The question for this review
1. Does an established dry-run / taint-tracking / mock-data approach (in this project's files first: earlier
   stage_prerun cards 134-1, 159-a4-1, fp-35/fp-100, docs/, archive/peer/; then the general practice of taint
   analysis / mock-object test doubles) already handle "a value read from a stub is tainted, a gate on it is
   unverified, a gate on simulated data still fails"?
2. Does the patch's VALUE criterion (stub-shaped values tainted; scalars and non-empty Fake-free data clean; no
   propagation through clean statements) match or contradict that approach - in particular, is there a case where
   it lets a FALSE gate on real/simulated data pass as UNVERIFIED (a false pass), or a stub-derived scalar gate
   FAIL (a false fail)?

This review has no recipe: the change is to the checker tool `tools/stage_prerun.py` itself.
