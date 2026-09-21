# ATTACK this claim. Do not confirm it.

## The record

`tools/bench/c65_astcheck.log` is the static gate on a build script that has not been launched yet. It ran
`tools/bench/c60c_astcheck.py` over that script and came back **11 of 12 PASS, 1 FAIL**:

```
FAIL  7 move_in is neither imported nor called  called=True imported=True
=== ASTCHECK FAILED; failing: 7 move_in is neither imported nor called
```

`c60c_astcheck.py:99-101` is that check, verbatim:

```python
gate("7 move_in is neither imported nor called",
     "move_in" not in called and "move_in" not in imported, ...)
```

The build script under the gate mandates `move_in` at its step 3: an object created by one helper lands on
the top-level diagram and is then relocated onto a nested diagram before it can be joined to a terminal
that lives there.

**This is the THIRD consecutive cycle in which this exact line is the first failing gate line.** The same
normalised line appears at `tools/bench/c62f_astcheck.log:11`, `tools/bench/c64e_astcheck.log:11`, and now
`tools/bench/c65_astcheck.log:11`. `tools/cycle_runner.py:253` builds its repeated-failure signature from
precisely "the first failing GATE line of the run, normalised, uids dropped, lower-cased, 60 chars", and
`tools/bench/cycle_runner.log:97` already carries `gate:fail 7 move_in is neither imported nor called
called=true im` for an earlier cycle. Under this project's rules, the same first-failing gate line in two
consecutive cycles converts the next cycle to a different, cheaper model; a third conversion stops the
runner and asks the human.

**What changed since the last time this was reviewed.** The previous cycle ran the same route to completion
and it WORKED. Two files are on disk, both carrying the edits, and the final one re-opens cold, in a freshly
restarted LabVIEW, at execution state 1, with an ordered not-broken read on the new wire, 51 checks passed
and 1 failed (that one failure was a mis-written expectation, separately reviewed and settled). The
relocation step ran inside that success. So `move_in` is no longer a step whose safety is unknown; it is a
step that has shipped an artefact.

**What has NOT changed.** The previous review of this same gate failure
(`archive/peer/2026-09-21-c64-astcheck-gate7-movein.md`) argued something I am not disputing and do not want
re-argued: that "what scripting creates lands on the top-level diagram and must be moved in" is a property
of how the creating helper was WIRED, not a law of LabVIEW — `New VI Object` takes an `owner refnum`, and
this fleet's own `build_invoke` / `build_property` already expose a `diagram_index`. Its falsification test
(set the creating helper's second navigation pair to the destination diagram and see whether the object is
born there) is UNRUN. Its other discriminating test — running `c60c_astcheck.py` against a script that is
known to have built the WRONG thing, predicting 12/12 PASS — is also UNRUN, because the gate's own failure
now blocks every command that would run it.

## THE CLAIM YOU MUST TRY TO DESTROY

"Gate 7 fails BY CONSTRUCTION and reports nothing about this script's correctness. It encodes a prohibition
written for a different cycle, the route it forbids has since shipped a working artefact, and the right
handling is to report the failure verbatim, leave the gate file untouched, and run the build. Repeating the
same failing line for a third cycle is a cosmetic accounting artefact, not a signal that the work is going
wrong."

## Already ruled out (do not spend your answer on these)

- "Edit the gate, rename the argument, alias the call, or set the override env var": all four are forbidden
  here and none is under consideration. The question is only whether the failure MEANS anything.
- "The relocation is avoidable in principle": granted, and argued in the prior review. I am asking whether
  it should be avoided NOW, in this script, given the artefact that already shipped through it.
- "The other 11 gates passing is reassurance": the prior review already attacked that and I am not leaning
  on it.

## What I want back

1. The strongest reason the claim is WRONG — in particular, any reading in which a THIRD identical failing
   gate line is genuine evidence that this route is the wrong route, and not an accounting artefact.
2. A DIFFERENT explanation of why this line keeps recurring that I have not considered.
3. What observation would falsify the claim.
4. The cheapest discriminating test that separates your explanation from mine — runnable, not an argument.
   It must be READ-ONLY with respect to every pre-existing `.vi` file.

Answer one thing directly: when a static gate encodes a prohibition that a LATER, SUCCEEDING build
deliberately violates, is the correct repair to (a) retire the gate, (b) parameterise it so the brief
declares which route it is on, (c) leave it failing forever as a standing reminder, or (d) something else?
Say which, and say what it costs when the same line is also the machine's repeated-failure signal.
