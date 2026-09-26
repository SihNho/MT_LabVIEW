# c97-g3-locallabel

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.5728  in 38 / out 13684 / cache-create 104868 / cache-read 2039597  (163s, 28 turn(s))
- **date:** 2026-09-26 15:46:57
- **outcome:** ANSWERED (166s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** failed prediction G3 in tools/bench/diag_c97_gatefacts.log (card 97-1 step-0 STOP gate); JEV-LADDER new-problem p=0.856, NEXT-ACTION hypothesis review owed
- **verdict:** unverified

## Question

ATTACK this claim about a failed prediction in tools/bench/diag_c97_gatefacts.log (script tools/bench/diag_c97_gatefacts.py, card 97-1).

The run read Node.Label of every node on all 170 diagrams of a scratch byte copy of D1_s1_copy.vi (OpNodeLabels_v0, gscript.node_labels, docs/toolkit-capabilities.md:26) and compared the 145 Property/Invoke/ControlReferenceConstant/Local/Global/EventStructure nodes with an older sweep of a sibling VI file 'Min_Track N beads V6_ParallelLoop.vi' (tools/bench/main_vi_node_labels.json, 2026-09-14).

Prediction G3 was: all 145 labels equal. Observed (log line 26): 137 equal, 8 differ, and the 8 are exactly the 8 `Local` nodes (2143, 2991, 3097, 3160, 4277, 11574, 16942, 25805); each old label is 'Min_Track N beads V6_ParallelLoop.vi', each new label is 'D1_s1_copy.vi'.

CLAIM: G3's contract was wrong, not the machine: a Local node's Node.Label text reads the OWNING VI's file name (not the linked control), so it changes with the file name and is uninformative about linkage. Therefore G3 says nothing about which objects link to indicator 'Force (pN) vs Extension (nm) ' (terminal #8323, panel object #8038), and the STOP-gate conclusion stands: G4 found exactly one node labelled with that name, Invoke #10313 'Reinit To Dflt' on diagram #3628 (a flat-sequence frame), all 6 terminals unwired (tools/bench/par1359_95_graph.json rows for owner 10313); no Local names the indicator by its terminal names (tools/bench/diag_c97_gatefacts_off2.log CAND lines: Local outputs name 'Rot pos (deg)', 'Trans Pos (mm)', 'Color table').

Already ruled out: a LabVIEW crash (ExecState 1, handles flat, H2-H6 PASS, log lines 20-62); a wrong input file (K1 md5 3e3d23ce... PASS).

Questions: (1) Is it true that a Local variable's Node.Label reads the VI name? If not, what else explains exactly these 8 differences? (2) Could a Local, Property node, Invoke node or control reference link to #8323 WITHOUT carrying the indicator's name in Node.Label (e.g. an explicitly referenced property node fed by a reference wire, a Local whose label is not shown, an event-structure registration on the indicator, a VI Server 'Controls[]' lookup by name)? Name the cheapest read that would expose one in this VI. (3) What would falsify "no non-display reader of #8323"?


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict: the mechanism in the claim is right, and it was already known. The conclusion does not follow from the evidence the brief cites, and there is still one gap nobody has read.**

**1. The strongest reason the claim is wrong as written: the evidence for "no Local names the indicator" covers only 3 of the 8 Locals.**
- `diag_c97_gatefacts_off2.py:32` builds `outs` from output terminals that have a wire attached. So its CAND lines show a name only for the three read-mode Locals: 3160, 3097 and 25805.
- The other five show `outs []` (`off2.log:13,29,101,111,140`). That is not evidence about their linkage.
- The gap closes, but from a different file. `par1359_95_graph.json` gives every Local exactly one terminal:
  - 2991 and 2143 → `Total Lost Frames` (lines 1967 and 28947)
  - 4277 → `File # Saved` (8337)
  - 11574 → `Focus Pos (Track)` (24077)
  - 16942 → `Picture` (41727)
- The only terminal in the whole graph named `Force (pN) vs Extension (nm) ` is #8323 itself (line 27577).
- So all 8 Locals are accounted for and none is linked to #8038, but the argument has to cite the graph file, not the CAND lines.

**Q1: does a Local's `Node.Label` read the VI name? Yes. This was measured before, and G3's failure is a missed-prior-art fault.**
- `docs/cycle27-plan.md:2300-2315` (from `diag_c60_n4_localbinding.log`) records it. `node_terms` on these same eight Locals gave one control-named terminal each, matching `main-vi-panel-map.md:409-416` 8/8. A newly created Local's `Node.Label` read the VI file name.
- My likely cause for the wrong contract: `docs/frame-loop-wire-graph.md:13` says "a Local's is its control". That line is stale and contradicts the measurement. It should be corrected, or G3-style contracts will fail the same way again.
- The label reliably tracks the file name. The name of the control a Local points to is available through `Local.Control Name` (property 6355400, [labviewwiki](https://labviewwiki.org/wiki/Local_class/Control_Name_property)) or through the Local's terminal name. The label never gives it.
- **The alternative explanation of the same 8 differences** is that `OpNodeLabels_v0` falls back to the owning VI's name whenever `Label.Text` is empty or hidden. That produces identical evidence, and nothing measured so far separates the two. It also does not matter: under either one, the label says nothing about what the Local is linked to.

**Q2: what could reach #8038 without carrying its name in `Node.Label`?**
- **Explicit property/invoke nodes:** ruled out. The three generic `Property Node`s (250, 9775, 22388) are IMAQdx session nodes (`off2.log:62,115,147`). Every other Property/Invoke node has its `reference` input unwired, which means it is implicitly linked and its label names its control.
- **Control reference constants:** ruled out. All of them name other controls.
- **Event structures #10153 and #15544: NOT ruled out. This is the real gap.**
  - The static event sources of each case appear nowhere in labels or in the terminal graph.
  - Event Data Node #15628 exposes `CtlRef` and `Coords` (`par1359_95_graph.json:42617-42630`), so some mouse event is registered on a control that has not been identified.
  - A mouse event on the XY graph would couple that event loop to #8038 even though no value is read from it.
  - A static Value Change event on an indicator fires only on a `Value (Signaling)` write, and none was seen, so a Value Change reader is unlikely.
- **Lookup by name through VI Server** (Controls[] or Get Control Value with a string): not checked.
  - The graph has about 20 `StringConstant` nodes whose values were never read.
  - My class grep found no This-VI or VI-server constant class, but that grep used a guessed class-name pattern, so I don't count it as negative evidence.

**Q3: what would falsify "no non-display reader of #8323"?**
- An event case whose selector names `Force (pN) vs Extension (nm)`, or
- a string constant with that text feeding a VI Server call, or
- a subVI that receives a VI or panel reference and walks `Controls[]`.

**Cheapest test that separates the claim from the alternative:**
- Read `EventStructure.Event Selectors` on #10153 and #15544: two property reads, about 1 second in total. The property returns each case's human-readable name ([labviewwiki EventStructure class](https://labviewwiki.org/wiki/EventStructure_class)). `Get Handled Events` gives the full per-case detail if the selector names are ambiguous.
- Second, read the values of all `StringConstant` nodes and search them for `Force`.
- If both come back clean, the STOP-gate conclusion holds. It then rests on the graph file plus these two reads, not on G3 or G4.
- If either shows #8038, the conclusion is falsified.

**Still unverified:**
- Whether LabVIEW lets two panel objects share the label `Force (pN) vs Extension (nm) `, which would weaken G4's match of Invoke #10313 by label.
- Whether this project has an op that can read `Event Selectors`. I did not check `docs/vi-server-ids.json`.

Sources:
- [Local class / Control Name property – LabVIEW Wiki](https://labviewwiki.org/wiki/Local_class/Control_Name_property)
- [EventStructure class – LabVIEW Wiki](https://labviewwiki.org/wiki/EventStructure_class)
- [Event structure – LabVIEW Wiki](https://labviewwiki.org/wiki/Event_structure)

## Sources

(extract from answer)

## What was done with it

Material session 97-1, 2026-09-26. Facts only; nothing built, no rerun of the COM script (failure budget 1 of 2 used).
- **Accepted (Q1, point 1):** G3 was a prediction-contract error of ours (a Local's Node.Label = owning VI file name,
  already recorded at docs/cycle27-plan.md:2300-2315). The Local argument is now cited from the graph file, not the CAND
  lines: tools/bench/diag_c97_gatefacts_final.py lists every Local's terminal names from par1359_95_graph.json into
  tools/bench/f1359_gate_facts_97.json (`A.locals_terminals`); none names 'Force (pN) vs Extension (nm) '.
- **Accepted as an OPEN gap, not closed (Q2, event structures):** no op in this fleet reads `EventStructure` event
  specifiers (grep of tools/ and docs/ for "Event Selector"/"Get Handled Events": no hits). The card forbids building one,
  so the result reports "event registration NOT READ" and puts the reader question under OPEN for judgement.
- **Partly answered (Q2, name lookup):** the only Invoke is #10313; the three generic `Property Node`s are IMAQdx
  (diag_c97_gatefacts_off2.log); no VI-class reference constant exists (GenClassTagRefConstant #66 = IMAQ 'Image Name').
  The prior StringConstant read of the main VI (tools/bench/build_opconstvalue_v1.log:86-107) shows no 'Force' among
  its 11 non-empty values; 11 read '' there, so that read is not complete.
- **Not acted on:** the stale sentence at docs/frame-loop-wire-graph.md:13 ("a Local's is its control") - reported
  as a fact to judgement; this card's write flags do not cover docs/.
