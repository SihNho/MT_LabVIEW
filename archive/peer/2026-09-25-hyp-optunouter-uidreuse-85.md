# hyp-optunouter-uidreuse-85

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.2434  in 28 / out 12265 / cache-create 90725 / cache-read 1292629  (148s, 22 turn(s))
- **date:** 2026-09-25 21:35:55
- **outcome:** ANSWERED (151s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

FAILED PREDICTION, card 85-2: tools/recipes/build_optunouter_v1.py run 1, log tools/bench/unroutable_l2a1_85_build_tun.log.

Prediction (gate B1): after deleting Property #136 (Constant.Terminal) from a copy of ops\OpConstWire_v1.vi and building a new
`VI Server:Tunnel` property node (Outside Terminal 6356001) with gscript.build_property, the walk shows #136 absent AND the new
PN has exactly one data output.
Observed: "FAIL B1 PN #136 gone; Tunnel PN #136 has ONE data output ['Outer Term']" - the NEW property node itself got uid 136,
so `136 not in walk` was False while the new PN had exactly one data output 'Outer Term' (as docs/NAMES.md:856 predicts).

My explanation: a SCRIPT bug, not a LabVIEW fault - LabVIEW re-issued the freed uid 136 to the next object created in the same
VI, and the gate tested absence of a uid number instead of the deleted object's identity. The sibling recipe
build_opctlsinkwire_v1.py (same donor, same delete) checked deletion BEFORE creating anything and passed 24/0
(tools/bench/unroutable_l2a1_85_build_ctl.log). Fix already applied: deletion gated before build_property; B1 only checks the
new PN's outputs.

Question: is uid reuse after delete a known LabVIEW 2026 VI Scripting behaviour (search our docs/NAMES.md, archive, and the web),
and does anything else in this recipe (or in stagexec's uid-keyed bindings, tools/stagexec.py bind_new) depend on a deleted uid
never coming back? Cheapest test that separates "uid reuse" from "the delete silently failed and the PN build returned the old
node's uid".


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**I don't accept your framing as written.** Your conclusion is probably right: LabVIEW most likely gave the freed uid 136 to the new node. But the run-1 log does not measure that. And the alternative you asked me to separate (the delete silently failed) is one your own code already rules out. What makes the reuse account plausible is prior evidence plus the code path, not this log.

## 1. Strongest reason the claim is wrong: nothing in the log shows reuse
- The log has no line between "B0 donor holds…" and the B1 failure (`tools/bench/unroutable_l2a1_85_build_tun.log:34-35`). It doesn't record:
  - the set of uids that `delete_object` reported gone;
  - the Property uids after the delete;
  - the uid that `build_property` returned.
- The recipe was patched in place under the same name (`build_optunouter_v1.py:33-34`), so the code that produced this log can no longer be inspected. "Reused 136" is read from one gate string.
- The same criticism was accepted on 2026-09-17 for uid 5058: reuse was "the leading explanation, not a measured" fact (`archive/peer/2026-09-17-d1-s3b-uid-reuse-after-delete.md:118-124`). Label this one the same way.

## 2. Alternative explanations
- **Your alternative is already excluded, if run 1 used the defaults.** "The delete silently failed and the build returned the old node's uid" conflicts with the code in three places:
  - `delete_object` defaults to `verify=True` and raises when zero objects are gone (`tools/gscript.py:2511-2513`).
  - `build_property` takes its "before" set after the delete (`gscript.py:2388`) and returns only uids not in that set (`gscript.py:2427`, `new_since` at `:1094-1102`). It cannot return 136 if 136 still existed.
  - Node #136's only data output after the build was `'Outer Term'` (log:35). That is the Tunnel property's name, not the output of a Constant.Terminal node.
- **Remaining alternative 1:** run 1 called `delete_object(..., verify=False)`, or used a different order than the code now shows. Only the original file or its git history can settle this.
- **Remaining alternative 2:** `uids()` uses `report_all` (`gscript.py:1091`) but `new_since` uses `report` (`:1102`). The two were verified identical only on 2026-09-13. If they disagree about 136, the "new" test is wrong in both directions.

## 3. Reuse is documented, and this project has seen it before
- **LabVIEW help** (the NI UID page returned only navigation; the LabVIEW Wiki quotes it): UIDs are unique within a VI, "however, if you delete an object, LabVIEW might assign the UID for that deleted object to a different object in the future." It recommends also checking Class Name or Label. https://labviewwiki.org/wiki/GObject_class/UID_property
- **Local precedents:**
  - On the same donor family, a new property node got uid 145 again (`archive/2026-09-18-status-cycle21-wire-semantics.md:36`).
  - uid 5058 came back after a delete (`tools/bench/build_d1_v0_run9.log:238`).
  - Newly created nodes reused low uids (`docs/keystone-op-spec.md:407`, `.claude/skills/labview-automation/references/vi-scripting.md:601`).
  - Wire uids are recycled too (`docs/cycle27-plan.md:3090-3091`).
- So "PN #136 gone" in contract line B was a prior-art miss when the plan was written. It was not a new LabVIEW behaviour.

## 4. What else depends on a deleted uid never coming back
**In the recipe:**
- **`old_seed` at `build_optunouter_v1.py:30`** is a wire uid captured before the delete, `remove_bad_wires_scripted`, `link` (which creates a wire) and `create_control`. It is used at `:49`. Wire uids are recycled, so a stale `old_seed` could name a different wire, and `del_net` would delete that wire. Fix: read TMSC #683's `target class` wire again right before `:49`, and assert it is the net coming from the old seed control.
- **Safe:** `link`/`N.connect`, `N.idx` and the new B1 gate all look up uids again at the time they are used, so reuse can't mislead them.

**In `tools/stagexec.py`, `bind_new` (`:215-249`):**
- `old_t` is the set of terminal uids from before the step (`:223`). If one step deletes and creates, the new object's reused terminal uids fall into `old_t` and its rows are dropped (`:226`).
- The owner filter `not in bind["obj"].values()` drops a new object whose uid was freed by an object bound earlier.
- Both cases end in `ExecStop` from the class or terminal-class comparison (`:230`, `:242`). That is a loud failure, not a silent wrong binding, but it will be misreported as a simulation/real mismatch.
- Neither this file nor `compare()` (`:192`) checks for reuse. Add a note or check that a real uid present before the step and absent after it may reappear later.

## 5. Observation that would falsify the claim
Any one of these, from a run that logs the facts below:
- 136 is still in `uids(op, "Property")` after `delete_object` returns without raising;
- `build_property` returns 136 while 136 was in its "before" set;
- the old reference to #136 is still valid after the delete.

## 6. Cheapest discriminating test
- **No LabVIEW needed, do first:** check whether run 1's recipe called `delete_object` with the default `verify=True`, from git history or the card's copy of it. If it did, `gscript.py:2511-2513` plus `:2427` already rule out "delete silently failed". What remains is reuse, or the `report`/`report_all` disagreement.
- **Then, in the re-run (no extra LabVIEW run):** log one line per step:
  - the `delete_object` return, expected `{136}`;
  - `sorted(uids(op, "Property"))` after the delete, expected to lack 136;
  - the uid `build_property` returned, with that node's label and its non-standard output names.
- "136 absent, then 136 returned with `Outer Term`" demonstrates reuse. Anything else refutes it.
- Following NI's own advice, change B1a to identify the node by output name (`Terminal` vs `Outer Term`) as well as by uid.

## Sources

(extract from answer)

## What was done with it

Card 85-2 (material), 2026-09-25 ~21:4x. ACCEPTED; recipe patched, NOT re-run (card rule: review owed -> review, then stop).
- Point 1 accepted: "uid 136 reused" is labelled the leading explanation, not measured; the patched recipe logs the
  `delete_object` return and the Property uid list after the delete, and gates the new PN by its output name `Outer Term`.
- Point 4 (recipe) accepted: `old_seed` is now re-read right before its `del_net` and gated to be the old seed control's
  own wire (`build_optunouter_v1.py` B2a). The sibling `build_opctlsinkwire_v1.py` carries the same stale capture; it passed
  24/0 with ExecState 1 (`unroutable_l2a1_85_build_ctl.log`), so no wrong wire was deleted there; not patched.
- Point 4 (stagexec `bind_new` drops a reused uid -> loud ExecStop misreported as a mismatch): reported as OPEN to judgement,
  not changed (outside this card's one fix).
- Card 85-3: re-run MEASURED reuse (unroutable_l2a1_85_build_tun2.log:35-37: delete_object -> {136}, Property uids after
  [139], build_property -> #136 with 'Outer Term'); build PASS 28/0. Point 4 (stagexec) now done: stagexec.uid_reuse +
  bind_new raises 'UID-REUSE' first (selftest T32/T32b/T32c, selftest_stagexec_85c.log 50/0; dry_l2a1_85d.log 42/42 diff 0).
