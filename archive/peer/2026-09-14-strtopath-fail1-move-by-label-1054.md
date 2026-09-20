---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# strtopath-fail1-move-by-label-1054

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (65s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS DIAGNOSIS (LabVIEW 2026 VI Scripting over COM, zero GUI). Log: tools/bench/cycle3_toolkit.log item 3 (script tools/recipes/cycle3_toolkit.py -> tools/recipes/build_strtopath.py). Items 1, 2a, 2b of that batch passed.
FAILURE: gscript.copy_into(DONOR="claudeDev/background VIs_COPY/save N xyz traces.vi", label="STP", target=StrToPath.vi, prepare=lambda src: set_node_label(src, 0, 7, "STP")) raised behind a modal: the screenshot shows the LabVIEW dialog "Error 1054 occurred at Open VI Object Reference in OpMoveByLabel_v0.vi - The specified object was not found". copy_into's mechanism (tools/gscript.py, def copy_into / move_by_label): byte-substitute the donor into NI's Move example 'Test-Source' file, revert it, call prepare() (which sets Node.Label text on Nodes[7] of diagram 0 in memory), then run OpMoveByLabel_v0 whose 'Open VI Object Reference' looks the object up by that label ('Add Label' control) and moves/copies it into 'Test-Target'. The same prepare= trick worked on 2026-09-08 for an unlabeled donor primitive (grep prepare= under tools/ for the precedent and note which node class it labelled). The census (tools/bench/census_savetraces_terms.log) shows the donor's top-level Nodes[7] is 'String To Path' (terminals 'string' sink, 'path' source).
Candidate causes to rank: (H1) Node.Label write on a PRIMITIVE without an existing owned label creates no findable label (Open VI Object Reference by name needs the object's owned label text; a primitive may have no Label object until one is created - is Node.Label 6359001 writable on a function primitive?); (H2) the set_node_label op's node index space differs from node_terms_uid's Nodes[] order (so a different node got the label); (H3) Open VI Object Reference in OpMoveByLabel_v0 is class-filtered (e.g. to Control or a specific node class) and cannot return a Function; (H4) the in-memory label edit was discarded because the op's static VI reference to Test-Source loaded a second copy / the revert happened after prepare (read the code order); (H5) name matching is exact and 'STP' vs the label with a trailing newline/space.
Questions: which is most likely and why; the cheapest read-only discriminating test (e.g. after prepare, read node_labels of Test-Source in memory and check which uid carries 'STP'; read OpMoveByLabel_v0's Open VI Object Reference 'vi object class' input); and the minimal repair (e.g. label via set_node_label on a SAVED copy of the donor first, then use that copy as DONOR without prepare). Read-only; do not open LabVIEW; cite what you read.


## Answer

The leading cause is not H1?밐5. It is a missing edit-state prerequisite: `prepare()` attempted to mutate `Test-Source` before opening its front panel, so `Node.Label` was probably declined silently.

Ranking:

1. **Missing `OpenFrontPanel` before `set_node_label` ??most likely.** The failed log contains no evidence that `STP` was ever written. The successful precedent explicitly calls `open_panel(src)` before labeling a Call Library Function Node ([copy_clfn2.py](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/copy_clfn2.py:13)). The current repair already adopts that prerequisite and verifies the result ([build_strtopath.py](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_strtopath.py:65)).
2. **H2, wrong node index ??plausible but secondary.** The census establishes index 7/UID 194 as `String To Path` ([census_savetraces_terms.log](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/census_savetraces_terms.log:4)), but only an immediate UID/label readback proves both operations use identical ordering.
3. **H1, primitive cannot acquire a label ??possible, but weakened substantially.** The precedent labeled a `CallLibrary` node, not a generic arithmetic primitive, so it is not a perfect class match. However, an NI employee explicitly says For Loops and Compound Arithmetic functions have names and can be found by `Open VI Object Reference`; functions are therefore not categorically excluded from name lookup. [NI forum](https://forums.ni.com/t5/LabVIEW-APIs-Discussions/Feedback-Request-Open-VI-Object-Reference/m-p/3401796)
4. **H3, class filter excludes Function ??unlikely.** The same NI evidence shows that `Open VI Object Reference` can return function objects by name. A restrictive class input inside this particular Op remains possible, but it would likely have broken the successful CallLibrary precedent too.
5. **H4, revert/static-reference race ??very unlikely.** Code order is substitute ??revert/load ??`prepare()` ??run Op; there is no revert after `prepare()` ([gscript.py](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:1125)). LabVIEW identifies already-loaded VIs by their in-memory identity/name, so a static reference should normally see that same loaded instance; NI documents name-based reference lookup as searching VIs already in memory. [NI reference-loading documentation](https://www.ni.com/en/support/documentation/supplemental/06/calling-a-labview-vi-by-reference.html)
6. **H5, whitespace mismatch ??least likely.** Both write and lookup receive the same Python literal `"STP"`; there is no transformation between them.

Cheapest discriminating test:

- Open `Test-Source`?셲 panel.
- Run `set_node_label(src, 0, 7, "STP")`.
- Immediately call `node_labels(src, 0)`.
- Require specifically `UID 194 ??"STP"`, not merely that some node contains `STP`.
- Only then run `OpMoveByLabel_v0`.

The current recipe tests ?쐓ome UID has `STP`?? tighten lines 71??4 to require `labs.get(194) == "STP"`. This separates the missing-open-panel cause, H1, and H2 in one readback.

If UID 194 reads `STP` but lookup still returns 1054, request reporter output for `OpMoveByLabel_v0` showing the `Open VI Object Reference` node?셲 `vi object class` input and its source. Do not open the compiled Op. At that point H3 becomes the leading candidate. NI community guidance also recommends `TRef Find Object By Label.vi` over `Open VI Object Reference` because the latter is fragile. [NI forum](https://forums.ni.com/t5/LabVIEW/add-event-cases-to-an-event-structure-using-scripting/m-p/3098775/highlight/true)

Minimal repair: keep the newly added `open_panel(src)` plus UID-specific readback inside `prepare()`. A saved donor copy is unnecessary unless the readback proves an in-memory label still cannot be found; it adds another save/load boundary without addressing the presently observed missing edit-state prerequisite.

## Sources

(extract from answer)

## What was done with it

Agreed: the leading cause is the missing `open_panel(src)` before `set_node_label` (the fleet's silent-decline rule
for edits on a closed panel; the one prior `prepare=` success, `tools/bench/copy_clfn2.py`, opened the panel). The
recipe's `prepare` now opens the panel, writes the label, and requires **uid 194 == 'STP'** on readback (the
reviewer's tightening — it separates 'declined' from 'wrong index' in one read) before the Move op runs. No saved
donor copy (unnecessary). Rerun: `tools/bench/build_strtopath.log`. `TRef Find Object By Label.vi` noted as the
sturdier lookup if 1054 ever recurs with the label verified present.
