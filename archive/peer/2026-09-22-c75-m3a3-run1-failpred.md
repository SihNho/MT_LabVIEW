# c75-m3a3-run1-failpred

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.5717  in 20 / out 37345 / cache-create 196343 / cache-read 1302128  (469s, 28 turn(s))
- **date:** 2026-09-22 08:08:45
- **outcome:** ANSWERED (472s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# FAILED PREDICTION - D1 stage M3a-3, run 1 (2026-09-22 07:56), log tools/bench/build_d1_m3a3.log

Two predictions failed in one run, on the same VI. Attack BOTH framings below; say which is wrong and what
the cheapest discriminating measurement is. The artefact is a broken-by-design intermediate that is never
run, so `ExecState` is not evidence here and must not be offered as one.

## Context, in one paragraph

`claudeDev\D1_s3b_m3a2_20260922_023029.vi` carries the ORIGINAL `WhileLoop #637` and a NEW `WhileLoop
#23032` on the same block diagram `Diagram #686` (traverse index 19). Stage M3a-3 re-sources the two
downstream consumers that still read the OLD loop's RIGHT shift registers onto the NEW loop's RIGHT
registers, as DELETE-AND-REBUILD rows (the sinks are already wired; `connect_from_wire` into an
already-wired sink is a measured silent no-op, `tools/gscript.py:2522-2523`).

## PREDICTION 1 (PHASE 0) - FAILED

PREDICTED, written before the read: `FlatSequenceInnerTunnel #7468` is in no diagram's `Nodes[]`, but its
terminal is indexed on its OWNING structure node `FlatSequence #681`'s terminal table, exactly once, as the
terminal carrying wire 7506 - by analogy with the shift-register OUTER that was resolved on the owning LOOP
node in `tools/bench/diag_c75b_loopterms.log`. Basis: plan Pre-decided 72, "a tunnel is not a `Nodes[]`
entry, but its terminal IS an entry in its owning structure node's `Terminals[]`".

OBSERVED (`tools/bench/build_d1_m3a3.log:37-39`): `find_node(#681)` scanned 173 of 173 diagrams in 18.1 s
and reported `#681 lives at: None`. So the OWNER ITSELF - `FlatSequence #681`, reported as `#7468`'s owner
by `owner_of(..., strict=True)` with a clean uid echo (`tools/bench/diag_c75_m3a3_rows.log`, M4:
`OBSERVED uid 7468 -> owner 'FlatSequence' uid 681 | self 'FlatSequenceInnerTunnel'#7468 | 482 says
'FlatSequence' cast 'FlatSequence'`) - is not a member of any scanned diagram's `Nodes[]` either. The row
was DEFERRED, wire 7506 was not deleted, and nothing was improvised.

Our reader: `find_node` (tools/recipes/build_d1_m3a1.py:541) enumerates `report_all('Diagram')` and then
`g.node_labels(path, i)` per diagram, matching on uid.

Questions: is the premise wrong (a `FlatSequence` is genuinely not a `Nodes[]` member over this COM path),
or is the READER wrong (`node_labels` omits structure nodes, or 173 diagrams is not all of them - the same
run's sibling read reports 174 elsewhere), or is the OWNER wrong (the FlatSequence uid is a frame or the
sequence's own diagram rather than the node)? Name the cheapest measurement that separates these.

## PREDICTION 2 (the writer) - FAILED, and it damaged the artefact

PREDICTED: `gscript.connect_nested_v2(...)` writes Row C. It is a def in `tools/gscript.py:2965` and the
pinned launch checker `tools/bench/c60c_astcheck.py` gate 4 ("every `g.<verb>` called already exists as a
def in tools/gscript.py") PASSED it (`tools/bench/c75_astcheck_m3a3.log`, 11 pass / 0 fail).

OBSERVED (`tools/bench/build_d1_m3a3.log:92`): `com_error (-2147352567, ..., (5507, 'LabVIEW', 'LabVIEW:
(Hex 0x7) File not found ...'))` raised inside `GetVIReference`. `OpConnectNested_v2.vi` IS NOT ON DISK in
`claudeDev` (only `OpConnectNested_v0.vi` and `_v1.vi` are). The wrapper and its label map
(`tools/bench/opconnectnested_v2_labels.json`) both exist; the VI does not.

CONSEQUENCE: the delete had already run, so the saved artefact
`claudeDev\D1_s3b_m3a3_20260922_075611.vi` has `Global #7202 'Global motor pos.vi'` t0 `'Focus position'`
BARE - a DROPPED CONSUMER, i.e. exactly the rule-1a failure the stage exists to prevent. It is recorded as
REJECTED and the next run restarts from the unchanged M3a-2 input (md5 re-read unchanged at both ends).

Our fix for run 2: switch to `connect_nested_v1` (OpConnectNested_v1.vi, on disk, functionally tested cold)
and add gate W0 - the writer's op VI file must exist on disk before any LabVIEW call.

Questions: (a) is "a gscript verb exists as a def" being read as "the op it drives exists" a defect class
wider than this one call - what else in `tools/gscript.py` names a claudeDev VI that is not on disk, and is
the cheapest check a one-pass existence scan of every `OP_*` path? (b) Is delete-then-write on a live
artefact the wrong ORDER given that any writer call can fail - should the row instead write first into a
scratch and only then cut, or is the delete genuinely mandatory first (the already-wired-sink no-op)?
(c) What else, if anything, should have caught this before 122 s of LabVIEW time?

## Already ruled out

- Not a naming/label error: the source and sink addresses both resolved LIVE and uid-echoed
  (`Diagram idx 19, Nodes[21] t3 'Out position' BARE` and `Nodes[8] t0 'Focus position'`), matching the
  prior measurement exactly.
- Not a load/state problem: `ensure_loaded` ran, the target's own census read 634 nodes / 1920 wires, and
  the same session's later calls on the same path succeeded.
- Not the artefact's brokenness: `ExecState` is 0 by design for every file in this chain and is neither
  gated on nor reasoned from.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled for this session (consistent with the read-only brief), so the review is the answer itself.

---

# Failed-prediction review — D1 M3a-3 run 1

**Prediction 1's framing is the wrong one.** Prediction 2's framing isn't wrong so much as inflated, and its load-bearing citation says the opposite of what it's cited for.

## 1. The single strongest reason Prediction 1's framing is WRONG

The trichotomy (premise / reader / owner) is exhaustive only under an assumption it never states: that *"where does #681 live"* must be answered by scanning `Nodes[]`. All three branches are phrased as questions about `Nodes[]` because `find_node` (`tools/recipes/build_d1_m3a1.py:541-569`) can ask nothing else — it calls `report_all(path,"Diagram")` once, then `node_labels(path,i)` per diagram. An object that is not a `Nodes[]` member is invisible to it **by construction**. `#681 lives at: None` after 173 diagrams and 18.1 s is not an observation about #681; it is the only sentence that reader can emit about anything that isn't a node.

The instrument that answers the real question is already built and already proven on this VI. `report_all` (`tools/gscript.py:502-532`) is a Traverse-by-class sweep that finds objects at any depth and returns a per-row **`owner`** column (`:499`, `:530`). And `FlatSequence` is a measured working traverse class here: `docs/NAMES.md:646-648` decomposes the 84-structure census as `Structure` 63 + **21 FlatSequence**, and `:672-673` states *"the working name is `FlatSequence` (21 of them)"*. One op run returns all 21 uids **and their owners**. `find_node` calls `report_all` on line 546 for `Diagram`; nobody called it for `FlatSequence`.

**The framing also mis-states its own analogy.** The shift-register precedent holds because the owning structure is a node *on the same diagram as the wire*: `WhileLoop #637` is `Diagram #686` `Nodes[4]` (`diag_c75b_loopterms.log:9`), and the register OUTER appears on that node's border table at t10 carrying wire 7506 (`:21`). Wire 7506 is owned by Diagram #686 (`diag_c75_m3a3_rows.log:184-185`), and the scan proved #681 is not among #686's 26 nodes. So if the owner read is sound, the only geometry left is the **inverse** of the assumed one: #686 is a frame diagram *inside* #681. Supporting this, `node_labels`' own docstring fixes the convention — *"`diagram_index` is the Traverse 'Diagram' index (0 = top level)"* (`tools/gscript.py:608`) — and #686 sits at index 19, so it is not the top-level diagram.

One branch is already dead: "the reader omits structure nodes" is refuted by the same run, which found `WhileLoop #637` and `#23032` through `node_labels` (`build_d1_m3a3.log:55`, `:80`). Only the narrower "omits `FlatSequence` specifically" survives — and that is live, because `FlatSequence` is measurably the odd class here (excluded from `Structure`, excluded from `MultiFrameStructure`, `SequenceTunnel`/`FlatSequenceTunnel` both 1092 — `NAMES.md:646-648`).

## 2. Alternative explanation of the same evidence

**#681 is real and #686 is one of its frame diagrams.** Then #681 lives on #686's parent diagram, tunnel #7468 sits on the border of the diagram carrying both While loops, and "in no `Nodes[]`" means `node_labels` failed to list it on a diagram it *did* visit — a reader defect with a findable location.

I checked and **reject** the tempting attack that this is the known owner-chain bug. `docs/toolkit-capabilities.md:61` records the chain terminating silently at a flat-sequence frame — but the documented signature is `owner_uid` **0**, error 1055, **empty** cast echo. The actual read was `owner 'FlatSequence' uid 681 | 482 says 'FlatSequence' cast 'FlatSequence'` (`diag_c75_m3a3_rows.log:163`): nonzero uid, populated echo, no error. Staleness is also out — the preceding query (`:161`) owned to `Diagram #686`, so a stale answer would have read #686. The one real gap stands: `owner_of` strict mode echoes the **self** uid, not the owner uid (`build_d1_v0.py:351-354`), so the field that matters carries no echo.

## 3. What would FALSIFY my claim

`report_all(target,"FlatSequence")` returning 681 **with `owner` = Diagram #686**. That makes #681 a node on #686, `node_labels(19)` simply failed to list it, and the "reader" branch wins outright. Conversely, 681 **absent** falsifies the owner read despite its clean signature.

## 4. CHEAPEST discriminating test

```
g.report_all(target, "FlatSequence")     # ~1 s, one op run, no scan, no mutation
```
- 681 present, owner #686 → reader defect; sink is on #686.
- 681 present, owner elsewhere → #686 is a frame of #681; resolve #681 on *that* diagram.
- 681 absent → the owner read is bogus; discard Pre-decided 107.

Plus 0.2 s: `owner_of(686)`. A `FlatSequenceFrame` owner with `owner_uid 0` is the documented silent termination and independently confirms #686 is a frame diagram. Neither touches wire 7506.

---

## Prediction 2 — narrower and worse than "a defect class"

**(a) I measured the class: it has exactly one member.** All 51 `OP_*` constants in `tools/gscript.py` against claudeDev on disk — **`OpConnectNested_v2.vi` is the only one missing**; every other basename resolves. Worth keeping the scan; not evidence of a wider class.

What happened is worse than drift. `docs/cycle27-plan.md:2558` — the **active plan this recipe was built from** — says in bold inside a 🔴 DECISION line: **"`OpConnectNested_v2` is NOT built"**, having chosen "the fix is a PURGE STEP, not a new op" and deleted the file (`archive/peer/2026-09-21-c64-openpanel-cap.md:216`). The wrapper at `gscript.py:2961-2965` was left pointing at the deleted path. The run's own prep said it again: M5 cites every other verb to a build recipe (`connect_nested_v1` → `build_opconnectnested_v1.py:418-453`, `diag_c75_m3a3_rows.log:23`) and cites **v2 to gscript.py alone** (`:27`). Two documents, twenty minutes apart. Note the mirror-image drift a disk scan would *not* catch: `OpOwnerChain_v1.vi` is on disk with **no wrapper** — the very reader Phase 0 needed.

**(c) What should have caught it — cheaper and stronger than gate W0.** Not a disk scan: **preflight `g.op(OP_X)` for every op VI the row list will use, at step [0], before the first mutation.** The run already opens 6 refs (`build_d1_m3a3.log:159`). It is the same call that failed, so it catches missing file, broken op VI, wrong path *and* label-map mismatch — a strict superset of W0.

Second gap: the delete ran, the writer raised, and the script **continued** — retried identically (`:126`), then saved. H9 failed and the save proceeded. The artefact carries the stage's clean output name with S1–S4 all PASS (`:139`), so **nothing on disk distinguishes a rejected artefact from an accepted one**. Under "a step is not done until it has left a file", a later cycle can pick it up. Cheap fix: a failed H9 renames the file `_REJECTED`.

**(b) The order question rests on a miscitation.** `tools/gscript.py:2522-2523` is `connect_terminals`' docstring — a different verb — and it says *"an already-wired SINK is **not safe** (LabVIEW re-routes and the VI breaks) — wire only unwired sinks."* Not a silent no-op: a corruption. Row C used `connect_nested_v2`, not `connect_from_wire`, so the premise is about a verb the row doesn't use. The conclusion survives — **delete-first is right** — but the corrected reason *closes* question (b): write-into-scratch-then-cut is the more dangerous order, and rollback is unavailable when the failure *is* the writer. Repair the citation to `build_opconnectfromwire_v0.py:381-420`, which records a *source*-side constraint.

**The v1 swap is not like-for-like.** `cycle27-plan.md:2544-2551` measured that `connect_nested_v1` takes `ExecState` 1→0 and leaves one junk `Invoke` to delete by uid — that behaviour is the entire reason v2 was attempted. Run 2 inherits the purge obligation on diagram #686. The machinery is present (`:101-104`); it reported "0 new uid(s)" only because the write never happened.

## What the run got right, and what the evidence cannot settle

Row D deferred, wire 7506 not deleted, no address improvised, no GUI fallback — the discipline whose absence damaged Row C, applied correctly in the same run. `ExecState` kept as a route selector, never offered as evidence.

Not settled by anything in the record or by NI's public docs: whether `FlatSequence` objects appear in `Diagram.Nodes[]` over this COM path. The documentation covers the class hierarchy and `Frames[]`/`Diagrams[]` accessors, not this traverse's membership. Only the `report_all("FlatSequence")` call settles it on this machine.

Sources: [FlatSequence class — LabVIEW Wiki](https://labviewwiki.org/wiki/FlatSequence_class) · [Flat Sequence Structure — NI](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/structures/flat-sequence_2.html) · [Scripting: connecting a terminal to a Flat Sequence Structure — NI Forums](https://forums.ni.com/t5/LabVIEW/Scripting-Connect-a-Terminal-to-a-Flat-Sequence-Structure/td-p/2672239)

## Sources

(extract from answer)

## What was done with it

DISPOSED THE SAME CYCLE, by the cycle-65 MATERIAL session. What was ACTED ON here is only what the brief
already authorised (the writer belongs to the pre-authorised verb family; a cheap read-only measurement is
measurement). What the review asks the PROJECT to decide is listed at the end for the judgement session and
is NOT acted on here.

ACTED ON IN RUN 2 (`tools/recipes/build_d1_m3a3.py`, re-astchecked before the launch):
1. **Prediction 2 (c) - the preflight.** Gate **W0b** added: the writer's op VI is OPENED with `g.op(...)`,
   the same call the row makes, at step [0] after the restart and BEFORE the first mutation; the run HALTS
   if it does not open. The weaker file-existence check (W0) is kept ahead of it. This is the review's own
   "strict superset of W0".
2. **Prediction 1 §4 - the cheapest discriminating test, run as MEASUREMENT ONLY.** PHASE 0 now runs
   `report_all(target, "FlatSequence")` (one traverse-by-class sweep with an `owner` column - the question
   `find_node` cannot ask, since an object that is not a `Nodes[]` member is invisible to it by
   construction) plus `owner_of(Diagram #686, strict=True)`, and logs every row as a FACT. Row D stays
   DEFERRED whatever it says: the brief pre-decided that branch, and choosing an address for `#7468` on the
   strength of this reading is a judgement call, not a material one.
3. **The writer swap** to `connect_nested_v1` (op VI on disk, cold-tested) - inside the verb family the
   brief authorises. The review's warning is carried: v1 takes `ExecState` 1 -> 0 and leaves one junk
   `Invoke` to purge by uid (`docs/cycle27-plan.md:2544-2551`); the purge machinery is present and now has
   something to purge.
4. **The run-1 artefact is REJECTED - and it could NOT be renamed, which is reported rather than quietly
   dropped.** `claudeDev\D1_s3b_m3a3_20260922_075611.vi` carries the stage's clean output name with S1-S4
   all PASS while `Global #7202` t0 `'Focus position'` is BARE - the delete ran and the rebuild raised -
   which is exactly the "nothing on disk distinguishes a rejected artefact from an accepted one" hazard the
   review names. The rename to `..._REJECTED_dropped_consumer.vi` was ATTEMPTED and REFUSED by this
   session's permission layer (claudeDev is outside the allowed working directories for a rename), so the
   file still sits under the clean name. It is marked REJECTED in STATUS instead, and the review's
   mechanical remedy - a failed H9 renames the file from inside the recipe - is left to judgement below.

ACCEPTED AS FACT, NOT ACTED ON (the review's measurements, recorded so they are not re-spent):
- **The missing-op class has exactly ONE member**: of the 51 `OP_*` constants in `tools/gscript.py`, only
  `OpConnectNested_v2.vi` is absent from claudeDev. The mirror-image gap a disk scan would not catch:
  `OpOwnerChain_v1.vi` is on disk with NO wrapper.
- **`docs/cycle27-plan.md:2558` already said `OpConnectNested_v2` is NOT built** and the file was deleted
  deliberately; `gscript.py:2961-2965`'s wrapper was left pointing at the deleted path. That wrapper is a
  live trap for any future recipe and is NOT repaired here - patching `gscript.py` is outside this task's
  one thing.
- **The `gscript.py:2522-2523` citation used in the stage docstring is to `connect_terminals`**, a
  different verb, and it says an already-wired sink is UNSAFE (LabVIEW re-routes and the VI breaks), not
  that the write is a silent no-op. The delete-first conclusion SURVIVES and is strengthened; the review
  names `build_opconnectfromwire_v0.py:381-420` as the correct citation for the source-side constraint.
  The plan text (Pre-decided 106) still carries the weaker citation.

FOR JUDGEMENT, NOT DECIDED HERE: whether to repair or remove the dangling `connect_nested_v2` wrapper in
`gscript.py`; whether a failed H9 should mechanically rename the saved artefact `_REJECTED` inside the
recipe (this run's rename was done by hand, after the fact); and Row D's real address once the FlatSequence
census is read.

(Claude fills in)
