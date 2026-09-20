---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, plan]
---

# opnodeterms-v0-plan

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (63s)
- **why asked:** plan review before building OpNodeTerms_v0 (per-terminal Name / Is Source? / wire UID of one node; the globals' read/write direction and a junk-free node reader).
- **verdict:** ACTED ON. (s4, strongest) each property on its OWN node with its own error chain: PN_N[Name] → PN_S[Is Source?] → PN_C[Connected Wire] → PN_W[UID] chained by `reference out`, each node's `error out` tunnelled as an explicit column. (s1) the global nodes' terminal shape is OBSERVED first: the test compares the op's rows against the walker's per-index tuples on the same nodes and prints count/Name/IsSource/wire before any direction claim; "exactly one data terminal" is an observation, not an assertion. (s2) Is Source? semantics checked on an Index Array primitive (inputs FALSE, `element` TRUE) and on an unwired terminal. (s3) exact indexed-tuple equality with the walker, not name sets. (s5) `Terms[]` used (the recipe accepts either short name it finds on the donor).

## Question

ATTACK this build plan (refute, do not confirm; be concrete and brief). GOAL: OpNodeTerms_v0.vi - for ONE node (diagram , Nodes[] ) of a target VI return arrays over Node.Terminals[]: terminal Name, Is Source?, connected-wire UID (0 = unwired), plus the Terminal node's error out - in ONE run, cast-free. TWO USES: (1) read/write DIRECTION of the main VI's global-variable nodes (: Trans/Rot/Focus position; the netmap cache already places them by terminal name, e.g. Trans position on diagrams 5/19/83) - a global node whose data terminal Is Source? = TRUE is a READ, FALSE a WRITE (NI manual: read globals behave like controls, write globals like indicators; a previous peer review 2026-09-14 endorsed Node.Terminals[] -> Terminal.Is Source? per terminal, no Global cast); (2) a faster, junk-free replacement for the per-terminal walker net_map (one run per node instead of one per terminal). DONOR: OpNetInfo_v1.vi (tools/recipes/build_opnetinfo.py): Traverse Diagram(index) -> IA -> TMSC -> Diagram -> PN Diagram.Nodes[] -> IA_n[index 2] -> PN Node[Terminals[]] -> IA_t[index 3] -> PN Terminal[Name, Connected Wire] -> PN Wire[UID, Is Broken?] -> Clear Errors; plus PN Node[Label, Style] <- IA_n.element (branch) -> PN Text.Text; plus an erdosmiller Create Invoke Node creator that drops junk on the target - which was DELETED cleanly from a copy this morning (OpSubVIs_v1, build_opsubvis_v1.log step 2b, 0 junk per call measured). RECIPE (same pattern as tools/recipes/build_opsubvis_v0.py which is functionally verified 14/14): copy donor; net_map diagram 0; delete the creator (terminal signature Inputs/Outputs/ID String); delete downstream of Node[Terminals[]]: the Wire PN, the Terminal PN, IA_t (downstream first, Remove Bad Wires) so the 'Terms[]' output is free (short name per docs/NAMES.md: Node.Terminals[] -> 'Terms[]'); for_loop; inside body PN_T class Terminal [Name 634A004, Is Source? 634A003, Connected Wire 634A000] (check rows by net_map), wire 'Terms[]' -> PN_T.reference (auto-indexed input); PN_W class GObject [UID 632A813] <- PN_T 'Wire'; exit_loop PN_T ['Name','IsSource'], PN_W ['UID'], plus 'error out' of PN_T and PN_W as explicit error columns (this worked for OpPanelWiring_v0 today: exit_loop accepts 'error out', arrays of error clusters read over COM); auto error handling off; save iff ExecState 1. TEST: scratch copy of OpFPLabels_v0 - node = its Open VI Reference primitive (terminal names known from a walk: 'vi path','vi reference','error out',... ) -> names == the walker's names for that node in order, wire UIDs equal the walker's, Is Source? TRUE exactly for outputs; main VI: the three global nodes on diagram 19 (uids from the cache) -> exactly one data terminal each; Trans/Rot written at init & read by the motor loop, Focus written by the frame loop (docs/main-vi-state.md) -> predicted Is Source? per node stated before the run; handle audit 20 runs. ATTACK: (a) does Node.Terminals[] on a Global node include only the data terminal, or also hidden/reserved terminals - and how is the data terminal identified without the Global cast (Name == the field name? datatype?); (b) is 'Is Source?' defined from the NODE's point of view (output terminal = source) - NI/LabVIEWwiki wording; (c) the ORDER of Terminals[] vs net_map's per-index reads - same order? (d) any reason Terminal.Name errors for unlabeled terminals (e.g. a Wire PN's error out?) that would default the whole row; (e) 'Terms[]' vs 'Terminals[]' as the output short name on a Node-class node - which is right? Give a failure scenario and the cheapest discriminator per point.

## Answer

Do not build this as specified yet. The global-variable test is under-specified, and the proposed error plumbing can silently manufacture plausible rows.

1. Global-node terminal membership

Failure: `Node.Terminals[]` may expose more than the visible data terminal, or the data terminal?셲 `Name` may be empty/generic rather than the selected global field. I found no NI contract guaranteeing ?쐎ne terminal, named after the selected global item.??The only documentation-level statement is that a global instance selects one variable; that does not define its VI Scripting terminal array. [NI?셲 global-variable reference](https://download.ni.com/support/manuals/321526a.pdf)

Cheapest discriminator: before building the loop, run the existing walker on one known read and one known write of the same global field and record, by index: terminal count, `Name`, `Is Source?`, connected-wire UID, and datatype. Do not accept ?쐃xactly one terminal??as a test expectation; make it an observed prerequisite. If multiple terminals exist, identify the data terminal by the known connected-wire UID plus datatype/direction?봭ot `Name` alone.

2. `Is Source?` direction semantics

Failure: the semantic prediction is probably right, but the cited manual proves dataflow behavior, not the scripting property?셲 precise viewpoint. LabVIEW defines node outputs as producing data and wire sources as the producer; community scripting examples use `Terminal.Is Source?` to distinguish terminal direction. [NI block-diagram explanation](https://www.ni.com/en/support/documentation/supplemental/08/labview-block-diagram-explained.html), [NI Community terminal-scripting example](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/td-p/4303374)

Cheapest discriminator: use a primitive with one undeniable input and output?볾dd is better than Open VI Reference because it avoids optional/error-terminal ambiguity. Assert inputs `FALSE`, output `TRUE`; then test one read-global and one write-global. Also test an unwired terminal, proving `Is Source?` is independent of wire presence.

3. Terminal ordering

Failure: `Terminals[]` is indexed, but NI does not promise a stable semantic ordering beyond using the Context Help terminal index to locate a terminal. A growable or polymorphic node can defeat assumptions derived from visual position. [LabVIEW Wiki `Node.Terminals[]`](https://labviewwiki.org/wiki/Node_class/Terminals%28%29_property), [NI Community discussion](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/td-p/4303374)

Cheapest discriminator: compare complete indexed tuples from the old walker and new op on the same unchanged node. Do not compare names as sets. Include duplicate names and empty names. If the old walker also indexes the same `Node.Terminals[]`, ordering equivalence is almost tautological; the meaningful test is exact tuple equality at every index.

4. `Terminal.Name` and row corruption

This is the strongest defect. If `Name`, `Is Source?`, and `Connected Wire` are rows of one Property Node, an error in an earlier property can suppress later properties unless ?쏧gnore Errors Inside Node??is enabled. The resulting outputs may be defaults or stale values, while your single terminal error column reports only the first failure. [NI Community explanation of Property Node execution](https://forums.ni.com/t5/LabVIEW/Problem-with-Executables/m-p/1134075), [NI discussion of stale property outputs](https://forums.ni.com/t5/LabVIEW/Property-node-standard-error-in-functionality-odd-behavior/td-p/1966029)

Failure: an unnamed/unsupported terminal makes `Name` fail; `Is Source?` and `Connected Wire` then appear as `FALSE` and invalid reference. PN_W converts that into UID `0`, making a failed row indistinguishable from a legitimate unwired sink.

Cheapest discriminator: call a deliberately unnamed terminal twice after a named/wired terminal and poison output defaults between calls. Better design: separate PN_T nodes/error chains for `Name`, `Is Source?`, and `Connected Wire`, or explicitly enable ?쏧gnore Errors Inside Node??and still return validity/error per property. A single PN_T error column is not enough for a trustworthy net map.

5. `Terms[]` versus `Terminals[]`

`Terms[]` is correct for wiring by short/data name; `Terminals[]` is the long display name. The published metadata lists Data Name and Short Name as `Terms[]`, Long Name as `Terminals[]`. [LabVIEW Wiki property metadata](https://labviewwiki.org/wiki/Node_class/Terminals%28%29_property)

Failure: using `Terminals[]` with tooling that resolves exact short terminal names fails to find the output, while UI/report text may display it successfully.

Cheapest discriminator: inspect the donor net map for the actual output-terminal label and perform one no-save wire attempt using `Terms[]`. There is no reason to test both names in the production recipe.

Bottom line: the cast-free direction idea survives as a hypothesis, but the current build is unsafe as a replacement net mapper because it conflates ?쐕nwired??with ?쐏roperty evaluation failed.??Split the property error paths first, then establish the global-node terminal shape empirically before encoding the one-terminal assumption.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
