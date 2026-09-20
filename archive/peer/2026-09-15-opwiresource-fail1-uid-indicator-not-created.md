---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, vi-scripting]
---

# opwiresource-fail1-uid-indicator-not-created

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (71s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS (LabVIEW 2026 VI Scripting over COM). tools/recipes/build_opwiresource_v0.py run 1 (log tools/bench/build_opwiresource_v0.log): every structural gate passed - the Constant-value tail was deleted, the Wire-typed seed control was made from the Wire.Terms[] node reference and retyped the To More Specific Class target, Terms[] -> Index Array -> Generic.Owner 6327806 -> Generic.ClassName 6327803 and GObject.UID 632A813 all wired with equal wire uids on both ends - and creating an indicator on the ClassName terminal worked (new front-panel label Class Name 4, i.e. LabVIEW derives the label from the property LONG name and disambiguates with a number; the donor already had Class Name, Class Name 2, Class Name 3). The NEXT step, Terminal.Create Indicator (the fleet op OpCreateIndicator_v0, gscript.create_indicator(target, node_index, terminal_index)) on the GObject.UID node output terminal (short name UID), produced NO new INDICATOR label at all: my gate diffs the front-panel indicator label set before/after and got the empty list, so the recipe stopped (nothing saved). The donor VI already has an indicator labelled UID (from OpReport_v3). FAILED PREDICTION: create_indicator always yields exactly one new indicator whose auto-label is unique. Candidates: (H1) LabVIEW created the object as a CONTROL, not an indicator (my diff only looked at indicators); (H2) the label collided with the existing UID indicator and LabVIEW silently declined to create; (H3) the creation succeeded but the label is identical to an existing one so the set-difference is empty (duplicate labels are normally impossible on one panel - is that guaranteed?); (H4) the node index I passed was stale: I re-walk the diagram before each create, but my walker enumerates only the first 80 nodes of Diagram.Nodes[] - if the VI now has more nodes, a later node could be invisible (yet the preceding gates found this same node, so this is weak); (H5) Terminal.Create Indicator declines for an I32 property output already having no wire? Questions (cite what you read): (1) rank; (2) what does Terminal.Create Indicator actually do when the derived label already exists - rename, fail with an error, or create a duplicate label? are duplicate front-panel labels possible in LabVIEW? (3) is there any documented case where Create Indicator produces a CONTROL (e.g. on a property node input vs output terminal)? (4) the cheapest read-only discriminator - I intend to print the op error out, the new ControlTerminal uids before/after (gscript.uids(target, ControlTerminal)) and the full control AND indicator label lists, plus the panel object count; better ideas? (5) any risk that the half-built in-memory op (never saved; the on-disk file is still the unmodified donor copy) corrupts the next run - the recipe starts with a LabVIEW restart (fresh()) and re-copies the donor.

## Answer

My attack: the strongest explanation is missing from H1?밐5??OpCreateIndicator_v0` returned an error or an invalid/null created-object reference, and the wrapper did not make that failure observable. Among the listed hypotheses, H3 is strongest because duplicate labels are legal.

### 1. Ranking

1. **Unlisted H6: the invoke failed or returned no valid object.**  
   `Terminal.Create Indicator` returns the created control reference, so success should be tested directly from that reference?봭ot inferred from label-set changes. The API description says it ?쐁reates an indicator for the terminal and returns a reference to it.??[LabVIEW Wiki API entry](https://labviewwiki.org/wiki/Terminal_class/Create_Indicator_method)

2. **H3: it created an indicator labelled exactly `UID`, making your set difference empty.**  
   Duplicate owned labels are legal. NI?셲 VI Analyzer explicitly detects VIs whose front-panel controls share labels, and NI?셲 Unit Test Framework can reject such VIs. [NI VI Analyzer manual](https://download.ni.com/support/manuals/323631a.pdf), [NI duplicate-label article](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA0VU0000003Vgn0AE&l=en-US). An NI forum example also calls same-labelled controls ?쐁ompletely legal.??[NI forum](https://forums.ni.com/t5/LabVIEW/Duplicate-control-labels-found-when-enumerating-controls/m-p/496098/highlight/true)

3. **H4: stale/wrong node or terminal selection.**  
   Still possible, especially because positional node/terminal indices are weak identities after structural mutation. But your fresh re-walk and successful identification of that node immediately beforehand make it secondary. The 80-node truncation remains a needless uncertainty.

4. **H2: collision caused silent refusal.**  
   Weak. Duplicate labels are permitted, while normal copy/create workflows commonly append a number to generated names. [NI duplicate-label evidence](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA0VU0000003Vgn0AE&l=en-US), [NI naming discussion](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Smart-er-automatic-label-names-on-copy/idc-p/1882117). I found no documentation saying `Create Indicator` silently declines on a collision.

5. **H1: it created a control.**  
   The scripting method specifically promises an indicator and returns a control-refnum-class reference to it. ?쏞ontrol Refnum??is the reference hierarchy, not proof that the resulting panel object has control polarity. [API entry](https://labviewwiki.org/wiki/Terminal_class/Create_Indicator_method)

6. **H5: an unwired I32 property output is ineligible.**  
   This is contrary to the ordinary purpose of Create Indicator: create an indicator and wire it to an output terminal. [NI LabVIEW User Manual](https://download.ni.com/support/manuals/320999b.pdf). An unwired output should be the normal case, not a reason to decline.

### 2. Collision and duplicate-label behavior

Duplicate front-panel owned labels are unquestionably possible; uniqueness is recommended and tested, not enforced. [NI VI Analyzer manual](https://download.ni.com/support/manuals/323631a.pdf)

What is not documented is the exact collision policy of the scripting method. Evidence shows at least two LabVIEW behaviors:

- Normal automatic creation/copy often appends a number. [NI naming discussion](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Smart-er-automatic-label-names-on-copy/idc-p/1882117)
- Users can produce distinct objects with identical owned labels. [NI forum](https://forums.ni.com/t5/LabVIEW/Duplicate-control-labels-found-when-enumerating-controls/m-p/496098/highlight/true)

Therefore your failed prediction was too strong: **label-set cardinality is not a valid creation-success oracle**. Your own `Class Name 4` result establishes auto-disambiguation for that particular call, but it does not prove that every data type, node terminal, or scripting path uses the same naming routine.

I found no source establishing whether a collision in `Terminal.Create Indicator` specifically means suffix, duplicate, or error. The returned reference and error cluster are the authoritative experiment.

### 3. Can it produce a control?

I found no documented case where `Terminal.Create Indicator` intentionally creates a control based on input/output polarity. The method contract says indicator. [API entry](https://labviewwiki.org/wiki/Terminal_class/Create_Indicator_method)

There is an old report of incorrect control/indicator labeling around iteration terminals and conversion of an unlabeled numeric constant, described as a probable bug?봭ot normal polarity-dependent behavior. [NI forum](https://forums.ni.com/t5/LabVIEW/LV2017-Indicators-are-labeled-as-controls/td-p/3760685)

Thus H1 is worth measuring, but it should be treated as a LabVIEW 2026 regression/API bug if confirmed.

### 4. Cheapest discriminator

Your proposed diagnostics are good, but the most valuable datum is the method?셲 direct return value:

- Error status, code, and source from `OpCreateIndicator_v0`.
- Whether the returned created-object reference is valid.
- Returned object?셲 UID, class name, label text, and control/indicator polarity.
- Target terminal UID before invocation and its connected-wire UID afterward.
- Multisets?봭ot sets?봮f `(UID, label, polarity, class)` before/after.
- Panel object count and `ControlTerminal` UID multiset before/after.
- Full, untruncated diagram-node inventory or at least the selected node UID/class plus selected terminal UID.

Use a `Counter`/sorted tuple list for labels. A set necessarily hides duplicate creation.

The minimal decision table is:

- Error + invalid return: H6.
- No error + valid new UID + label `UID`: H3.
- No error + valid new UID + control polarity: H1/regression.
- Returned UID already existed: wrong invocation or wrapper-output bug.
- New panel/terminal UID but invalid return: likely fleet-op reporting bug.
- Nothing new and target UID differs from the gated UID: H4.
- Nothing new, correct target UID, no error: strongest evidence of a LabVIEW scripting defect.

### 5. Next-run contamination

With no save, a genuine LabVIEW process restart, and a fresh donor copy, the half-built in-memory VI should not affect the next run. The unsaved object graph belongs to the old editor process; your next run does not reuse it. The cheap verification is to log the LabVIEW process/application-instance identity and donor-copy timestamp/hash before construction.

The remaining risks are operational rather than VI corruption: `fresh()` might reconnect to a surviving automation instance, or the recipe might accidentally reuse an already-open target path. Confirming a new process/application identity and zero pre-existing target references settles both.

## Sources

(extract from answer)

## What was done with it

Accepted, including the unlisted H6 and the methodological point: a label SET is not a creation oracle because
duplicate panel labels are legal. The recipe now diffs panel rows by **UID** (`panel_wiring`, a multiset keyed by
object uid), keeps the op's own return value in the diagnostic line, and gates two separate things — exactly one
new panel object, and that object being an INDICATOR whose label is unique on the panel (uniqueness matters here
beyond style: the op is driven by `SetControlValue`/`GetControlValue` on labels, so a duplicate label would make
every later read ambiguous). The 80-node walker limit the reviewer flagged as needless uncertainty is now an
explicit gate (`Node` count < 80). If the next run shows an error or an invalid reference from the create call,
that is H6 and the op itself gets fixed rather than the recipe. Rerun: `tools/bench/build_opwiresource_v0.log` run 2.
