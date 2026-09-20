---
type: plan
status: superseded
superseded_by: docs/cycle14-plan.md
date: 2026-09-16
cycle: 12
tags: [cycle-plan, owner-semantics, A2]
---

# Cycle 12 — the two round-3 devices, then A2 (owner semantics per structure class)

> **STATE, 2026-09-16 19:30 — sections 1, 2 and 3 are DONE and on disk; only §4 remains.** The prior-art review
> (`archive/peer/2026-09-16-priorart-priorart-cycle12-a2.md`, opus, ANSWERED 481 s) read them as `already-built`,
> which is true and is an artefact of ordering: they were written before the review was dispatched, and the plan
> below still described them as work to do. The code, with the reviewer's own citations:
> **§1** `tools/hooks/guard_cycle.py:204-266` (`premature_build()`), wired at `:310-312`, `BUILD_RE` group at `:40`
> — tested 4/4 on fake files in a scratch tree and once live (it refused a real recipe command while this very
> review was still running). **§2** `tools/audit_cycle.py:227-273` (C7) + `--cycle` at `:75-77`; first run: 62
> files not named in `docs/cycle11-plan.md`. **§3** `tools/bgrun.py:69`
> (`scan_inner = not logclass.is_review_log(logp)`); measured both ways on `retro_cycle11.log:102`'s sentence —
> review-named log `rc=0`, build-named log `rc=1` unchanged.

Scope, in order. The devices come first because `guard_cycle.py` will not let a recipe run while a slug sits at
threshold, and because both were DECIDED — not proposed — in `docs/violation-decisions.md` (round 3, dated
2026-09-16 19:16). Nothing in this cycle re-opens those two decisions.

## 1. Device for `premature-build` — `tools/hooks/guard_cycle.py`

Refuse a RECIPE build (command-position `tools/recipes/*.py`, the existing `BUILD_RE`) while either

* (a) any `tools/bench/priorart_*.log` newer than the newest retrospective carries no `BGRUN END` / `BGRUN TIMEOUT`
  line — i.e. a prior-art review has not returned; or
* (b) no `archive/peer/*priorart*.md` is newer than the **recipe file's own mtime** — no review has seen the text
  about to run, or the recipe was edited after the review that did.

Diagnostics (`tools/bench/*.py`), doc writes, peer dispatches and the reviews themselves stay open. The refusal
names the running log or the missing review. Tested against fake files in a scratch tree.

## 2. Device for `scope-creep` — `tools/audit_cycle.py`

A new cost line (C7) listing every file under the project modified inside the audit window whose path is not named
in `docs/cycle<N>-plan.md` (N from `--cycle`, else the newest plan). Excluded: `archive/`, `tools/bench/*.log|json`,
`.claude/`. A **counter, not a refusal** — the decision says so explicitly, because an out-of-plan change is
sometimes right and the verdict belongs to the retrospective; only the list is taken away from Claude.

## 3. `bgrun` false positive on REVIEW logs — STATUS OPEN 8

`tools/bgrun.py` scans every line it pumps for an inner failure and has no review-log exclusion, so
`retro_cycle11.log:102` ended `rc=1` on the reviewer's own sentence quoting the OPEN-6 regex bug. Apply
`logclass.is_review_log(--log)` and skip the inner-failure scan for `peer_*` / `priorart_*` / `retro_*` logs; the
process's own exit code still decides.

## 4. A2 — validate owner semantics per structure class  (`pre-rig-master-plan.md:69`)

**The measurement, and only the measurement.** The owner fact the walk depends on is scoped to `CaseStructure`
(`docs/NAMES.md:916-917`: a node's `Generic.Owner` is its frame **Diagram**, and that Diagram's `Owner` is the
**CaseStructure**). The VI holds **84 structures across six classes** — 3 WhileLoop, 17 ForLoop, 37 CaseStructure,
21 FlatSequence, 4 Sequence, 2 EventStructure (`docs/diagram-hierarchy.md:14-22`).

⚠️ **CORRECTED after the prior-art review (`contradicted`, A3-ii), and the correction narrows the work.** This
plan said "five of the six classes have never been checked". That is **false at the class level**: the owner
**class** is measured for every one of the 170 diagrams, across all six classes —
`tools/bench/diagram_hierarchy.json` carries `owner_class` per diagram, `build_diagram_hierarchy_run3.log:2-9`
produced it, and `gscript.py:261-281` fills that field from `Generic.Owner`'s class name, the very property A2 is
about. **Genuinely unmeasured, and therefore what A2 now IS:**

* the owner **UID** read from the machine — `report()` returns the owner's class and never its uid
  (`archive/peer/2026-09-15-priorart-ownerchain.md:68`), so every diagram→structure uid the project holds comes
  from **position matching** (`diagram_hierarchy.json` carries a `distance` field), which this project's own notes
  call invalid on a Clean-Up'd diagram — that is the whole reason A3 exists;
* the **structure → parent diagram** hop, which has never returned for any class.

Diagnostic script `tools/bench/diag_owner_semantics.py`, read-only on the main VI, md5 bracketed
(`2a78e17c449cacdaf5da389818526859`), one `MATERIAL=1` bgrun. It uses `OpOwnerChain_v1.vi` **unchanged**.

Per class, up to 3 diagrams (FlatSequence: **one**, `already-failed`):

1. every diagram uid + its owner class comes from **one** `g.report_all(MAIN,'Diagram')` run (`helper-exists`,
   B3 — an earlier draft walked node→Diagram for this, 18 op runs, on the false premise that only
   `diagram_tree_main.json` existed);
2. diagram uid → its owner: class (tripwire) and **UID** (the new fact) — **this is the A2 question**;
3. the structure uid → its owner should be a `Diagram` (the parent hop that has never returned).

Cross-checks that cost nothing: the structure uid against `structures[<class>]` in `diagram_tree_main.json` (five
classes; FlatSequence is absent, which is the round trip the plan names), and against the **position-matched**
`owner_uid` in `diagram_hierarchy.json` — reported and counted, never gated, because the position match is the
thing under suspicion, not the reference. The class census and the 170-row histogram stay only as **tripwires**
and are labelled as such (`already-measured`, B4).

**The FlatSequence question, stated as a prediction and not as an action.** `diag_ownerchain_hop.log:7` measured
`Diagram#686 → FlatSequenceFrame`, owner uid **0**, `error 1055`, empty cast-class echo; codex's review
(`archive/peer/2026-09-16-ownerchain-flatseqframe-1055-r2.md`) hypothesises `FlatSequenceFrame` is a sibling of
`GObject` under `Generic`, so it has no `GObject.UID` at all. That hypothesis is **no longer wiki-only**
(prior-art `contradicted`, A3-iii): `build_diagram_hierarchy_run3.log:8` records the machine refusing
`FlatSequenceFrame` as a traverse class with **error 1092**, which `docs/NAMES.md:578-590` defines as *the string
is not in the VI Server GObject hierarchy at all* — our own evidence, pointing the same way. It is still not the
same as reading the class tree.

So the FlatSequence arm runs **once**, reproduces or refutes the 1055, and **also reads `errCO`** — the cast
node's own error, labelled `"error out 10"` in `tools/bench/opwiresource_v5_labels.json` and never read by
`read_owner`, which is why "the cast failed" has been implied and never measured. Reading one more existing
indicator is not an op change: **`OpOwnerChain_v1` is NOT modified in this cycle.**

**Carried to OPEN, not done here** (prior-art `unread-evidence`, A4): `docs/NAMES.md:611-622` records
**`ClassSpecifierConstant.AllTypes[]`** — it enumerates LabVIEW's VI Server classes with their class IDs and
**parents**, straight from the machine. That is the discriminating test for "is `FlatSequenceFrame` a sibling of
`GObject`?", and it settles the class-string guessing generally. Whether it is worth a build is judgement.

Also read here, because they are three reads on the same op and STATUS OPEN 1 is waiting on them: the owners of
**`Function` 10068**, **`LoopTunnel` 10114** and **`LoopTunnel` 10177** — they settle whether the PERIODIC modulo
sits inside diagram 43.

**Interpretation is not part of this cycle.** The per-class table goes into `STATUS.md` and
`docs/diagram-hierarchy.md` as facts; what it means for A3, for STATUS OPEN 1, and whether the uncast reader is
worth a build cycle goes under `OPEN:` for judgement.

## Files this cycle expects to touch

`tools/hooks/guard_cycle.py` · `tools/audit_cycle.py` · `tools/bgrun.py` · `tools/bench/diag_owner_semantics.py` ·
`tools/bench/owner_semantics.json` · `docs/cycle12-plan.md` · `docs/diagram-hierarchy.md` · `STATUS.md` ·
`docs/toolkit-capabilities.md` · `archive/peer/` (the cycle's reviews).

## Out of scope, deliberately

A1 is done. A3 (the 170-diagram hierarchy) waits for A2's verdict. `OpOwnerChain_v1` is not rebuilt, the uncast
`Generic` reader is not built, and no op VI is created or saved in this cycle.
