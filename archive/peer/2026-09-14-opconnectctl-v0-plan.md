---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, plan]
---

# opconnectctl-v0-plan

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (50s)
- **why asked:** plan review before building OpConnectCtl_v0.
- **verdict:** ACTED ON: verification order (invoke error -> display terminal wire present and ImageToArray wire intact -> ExecState 1 -> nothing else) implemented in build_harness_dispI.py step 8; built and functionally verified (build_harness_dispI.log run 4: wire 259 on the Image terminal, branch kept). Negative test softened per the peer (a wrong terminal may yield a broken wire, not an error).

## Question

PLAN REVIEW (attack; brief). GOAL: OpConnectCtl_v0 - wire a NODE's output terminal to a FRONT-PANEL object's terminal by script, which the fleet cannot do for a Vision IMAQ Image Display control (erdosmiller Wire Indicators/Wire Inputs raise 5001 - a ControlTerminal is a Terminal, not a Node; archive/peer/2026-09-14-dispI-controlterminal-route.md recommended Terminal.Connect Wire on the control's terminal). Needed only to finish HARNESS_dispI (Image Display route measurement). PLAN: donor OpFPLabels_v0 (Open VI Reference -> VI.Front Panel 23D -> Panel.Controls[] 6348801 -> Index Array() -> Control[Label, Indicator] -> Text.Text); in a copy: (1) add Control[Terminal 6332006] fed from the Control node's  (cast-free, proven today) = the SINK terminal ref; (2) build the SOURCE chain from the same Open VI Reference: VI.Block Diagram 23C -> AbstractDiagram.Nodes[] 6375809 -> Index Array() -> Node.Terminals[] 6359000 -> Index Array() -> Terminal ref; (3) Invoke Terminal.Connect Wire (the method OpConnect_v0 already uses on node terminals; ID from docs/vi-server-ids.json) with reference = the sink (control terminal), 'Wire Source' = the source terminal; (4) expose the invoke's error out as an indicator; auto error handling off; controls: vi path, index (panel object), index 2 (node), index 3 (terminal). TEST: scratch = a copy of HARNESS_disp1 (Create -> ReadFile -> ImageToArray, Image Out already wired) plus an extra indicator? no - test target = the prepared dispI copy (Image Display 'Image' at panel index 0; ReadFile node index 1, 'Image Out' terminal index from node_terms): run op -> panel_wiring shows the Image control's terminal wire != 0, ExecState 1; negative control: a wrong terminal index (an input) must error, not silently wire. ATTACK: (1) Connect Wire semantics when the SOURCE is already wired (Image Out -> ImageToArray): branch (desired) or re-route? (NI/labviewwiki wording); (2) invoking Connect Wire on the SINK (control terminal) with the source as 'Wire Source' - is that the right direction (OpConnect_v0 invokes on the sink) and does an Image Display's terminal accept an IMAQ image wire from ReadFile (type compatibility: Image Display terminal datatype = IMAQ image ref)?; (3) any reason Panel.Controls[] index != fp_labels tabbing index (the fleet reads labels with the same route so consistent); (4) failure scenario where the op wires but the VI breaks (type mismatch shows as ExecState 0 - Remove Bad Wires would delete it: state the check order). One paragraph.

## Answer

Plan is sound, with two corrections: `Terminal.Connect Wire` is explicitly invoked on the destination terminal and its `Wire Source` parameter accepts another terminal, so sink-reference/source-terminal direction is correct; because LabVIEW permits one source to feed multiple readers, connecting `Image Out` to the display should create a branch rather than reroute the existing `ImageToArray` connection ([Connect Wire](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method), [NI wiring semantics](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)). The IMAQ Image Display accepts the IMAQ image datatype, so the proposed pair is type-compatible provided the selected ReadFile terminal really is `Image Out` ([NI Image Display Control](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YI6eCAG&l=en-US)); Panel.Controls[] indexing is internally consistent with `fp_labels` because both use the identical array, but do not generalize that index to pane/tab-contained controls, whose enumeration can differ ([NI tab-control access](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019O8LSAU)). Most importantly, weaken the negative-test requirement: an input/wrong-type terminal may yield either a scripting error or a created broken wire?봏I documents incompatible wiring as a dashed broken wire?봲o ?쐌ust error??is too strict ([NI wiring semantics](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)). Verification order should be: capture invoke error first; confirm the display terminal gained a wire and the original `ImageToArray` wire remains; confirm the new wire is not broken and VI executability remains valid; only then run/remove bad wires?봮therwise cleanup can erase the primary evidence.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
