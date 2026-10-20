# hypothesis-op-getimage

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $0.5478  in 10 / out 5520 / cache-create 37590 / cache-read 223986  (91s, 12 turn(s))
- **date:** 2026-10-16 14:08:20
- **outcome:** ANSWERED (94s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

HYPOTHESIS REVIEW (failed prediction, card chat-PI1b -> retry chat-PI1c). Short answer wanted (<= 40 lines).

FAILED PREDICTION: tools/recipes/build_op_getimage_v0.py gate M1 "one candidate ID among VI Server:GObject Invoke
methods 632A401, 632A403..632A40F has an Image-named output terminal". Measured (tools/bench/build_op_getimage_v0.log:8-23):
632A401 = Highlight Object, 632A403 = RepNoAttrib/Param 0/Param 1/PaletteString, 632A407 = GetObjHelp/helpPath/helpTag/
hasExample; 632A404..406 and 632A408..40F give an Invoke whose only terminal is 'Method' (no such method). No Image output.

MY HYPOTHESIS for why the class was wrong: the brief (tools/bench/cards/brief_chat-PI1.md "How") said "GObject reference ->
VI Scripting method Get Image", and the recipe took the class from the brief and the ID range from the two GObject methods
already recorded (docs/vi-server-ids.json: GObject.Move 632A400, Replace 632A402) instead of searching externally first
(docs/rules/reviews.md: every factual claim about a tool/API gets an external search). The judgement session's external
source (https://labviewwiki.org/wiki/Node_class/Get_Image_method, 2026-10-16) says: Get Image is a method of the NODE class
(owning class id 16421), method ID 6358C01, VI Scripting scope; inputs Image Depth (I32: 1/4/8/24, default 8), Background
Color (U32); output Image Data (the Graphics-Formats image cluster, e.g. for Write PNG File.vi).

THE RETRY PLAN (attack this too):
1. Falsifier first: on a scratch copy of an empty VI, build an Invoke of class "VI Server:Node" with ID 6358C01 and read its
   terminal names. Prediction: Image Depth (in), Background Color (in), Image Data (out). Different names -> stop.
2. Typing problem: `UID to GObject Reference.vi` outputs a GObject-typed reference; wiring a GObject wire into a
   Node-class Invoke would make LabVIEW adapt the node's class to GObject (Get Image not there -> broken). So the op is built
   on donor OpSetIndexMode_v0 (Traverse(Class Name, index) -> Index Array -> To More Specific Class), and the TMSC is
   retargeted with a Node-typed seed (create_control on the `reference` input of a "VI Server:Node" property node of
   GObject Position 632A800 + Bounds 632A803) - the proven c97 route (tools/bench/diag_c97_tools_opbuild.py retarget()).
   TMSC output -> that Position/Bounds PN, a GObject.UID echo PN, and the Get Image Invoke; Image Data -> Write PNG File.vi.
   The caller maps a UID to the Traverse index with gscript._uid_index (report_all order) and checks the UID echo.

QUESTIONS: (a) Is the hypothesis right, or is there a better explanation (e.g. Get Image also exists on GObject under
another ID)? (b) What would falsify the class claim beyond the terminal names? (c) Any flaw in step 2 - e.g. does a
structure (While Loop, Flat Sequence) Traverse class + TMSC(Node) work, does Get Image on a structure return the whole
structure including its subdiagram, does Image Depth 24 need anything else for Write PNG File.vi?
End with one line: HYPOTHESIS: confirmed | refuted | partly, and one line ALTERNATIVE: <cause or none>.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**The class explanation is mostly right. The "process" explanation is only partly right, and your sweep could not have shown on its own that GObject has no Get Image.**

**1. Strongest objection.** The M1 sweep could not tell a method that does not exist from one that exists but this tool cannot see. LabVIEW Wiki lists 632A404 Launch Config Page, 632A405 Invalidate and 632A406 Replace Preferring Stub as real GObject methods ([GObject class](https://labviewwiki.org/wiki/GObject_class)). In your log those three gave the same empty `'Method'` terminal as the IDs 408..40F that do not exist (`tools/bench/build_op_getimage_v0.log:10-12` vs `:14-21`). So a negative from the sweep proves nothing. "Get Image is not on GObject" rests on the wiki's list of eight methods (632A400..632A407, no Get Image), not on your measurement. Your hypothesis is about how the class was chosen; it does not explain why the measurement looked the way it did.

**2. Alternative explanations of the same evidence.**
- (i) Some IDs in the range are hidden or private and not readable through this route. That makes the sweep blind to them; it does not prove they are absent.
- (ii) Get Image exists on more than one class. Besides Node (6358C01), the Control class has its own Get Image, ID 6331C0C, class id 6, Basic Development Environment scope ([Control.Get Image](https://labviewwiki.org/wiki/Control_class/Get_Image_method)). The "GObject -> Get Image" line in the brief most likely mixed up the Control/front-panel version with the diagram version. So the root cause is the brief's wrong class, which the recipe copied, more than "no external search". Both are true.
- Node is the right class for diagram objects: parent GObject, children include Structure and SubVI, methods 6358C00 Connect Wires and 6358C01 Get Image ([Node class](https://labviewwiki.org/wiki/Node_class), [Node.Get Image](https://labviewwiki.org/wiki/Node_class/Get_Image_method)).

**3. What would falsify the class claim, beyond terminal names.**
- (a) Terminal names cannot test direction. The reporter lists every parameter as both IN and OUT (`log:8-9`), so "Image Data (out)" cannot be checked that way.
- (b) A stronger check has two halves:
  - The Node-class Invoke with 6358C01, run on a real node, returns error 0 and a non-empty Image Data cluster whose width and height match that node's Bounds (632A803).
  - The same ID 6358C01 on a GObject-class Invoke gives `'Method'`. That shows the method belongs to Node, not that the reporter got lucky.
- If (b) fails while the names match, the claim is refuted.

**4. Flaws in step 2 of the retry plan.**
- TMSC(Node) on a While Loop reference is valid at runtime, because Structure is a child of Node ([Node class](https://labviewwiki.org/wiki/Node_class)).
- **Unknown, no source found:** whether Get Image on a structure includes its subdiagram contents. Treat it as a measurement, not a prediction.
- **Unknown:** whether rendering works on a VI opened through ActiveX with no diagram window. The wiki says only that the method loads the diagram into memory.
- The plan maps a UID to the Traverse index with `_uid_index`. It re-reads the order at the call site (`tools/gscript.py:3639-3644`), which is good, but only if `report_all` walks the same Traverse order with the same class string. The UID echo PN is what catches a mismatch, so it must be a hard gate, not just a log line.
- Depth 24 is the right choice. 24-bit data is 3 bytes per pixel in R,G,B order, and the documented path wires Image Data straight into Write PNG File ([NI: images of front panel objects](https://www.ni.com/docs/en-NR/bundle/labview/page/generating-images-of-individual-front-panel-objects.html)). The search summary also said the PNG writer handles only 24-bit images; that rests on a [LAVA thread](https://lavag.org/topic/18067-alternative-image-data-to-png-conversion-vi/) I did not open, so I have not checked it. Either way, choose 24 deliberately: the default is 8, not 24.

**5. Cheapest test that separates the claim from the alternatives.** It takes one scratch build:
1. On an empty VI, drop a Node-class Invoke 6358C01 and a GObject-class Invoke 6358C01 side by side. Read both terminal lists.
2. Run the Node one on a single Add function at depth 24.
3. Gates: names match; the GObject one shows `'Method'`; Image Data width and height equal the Add node's Bounds.
4. Only then repeat on a While Loop that contains a node, to measure whether the subdiagram is included.

I did not run anything, take the LabVIEW lock, or edit any file; this rests on the log, `gscript.py` and the wiki/NI pages above.

HYPOTHESIS: partly
ALTERNATIVE: the brief confused Node.Get Image (6358C01) with Control.Get Image (6331C0C), and the M1 sweep could not prove absence because existing hidden methods (632A404..406) look exactly like IDs that do not exist.

## Sources

(extract from answer)

## What was done with it

Disposed 2026-10-16 by card chat-PI1c (material session). HYPOTHESIS: partly - accepted as stated.
- (1) ACCEPTED: the 632A4xx sweep proves no absence (hidden methods look like missing IDs). No claim "not on GObject" is
  made from it; the class comes from the wiki source in the card.
- (2) ACCEPTED as the root cause: the brief's "GObject -> Get Image" mixed Control.Get Image (6331C0C, front panel) with
  Node.Get Image (6358C01, diagram). Recorded in the result facts.
- (3b) ACCEPTED: tools/recipes/build_op_getimage_v0.py gate M1b builds a GObject-class Invoke with 6358C01 beside the
  Node one and records its terminals (expected 'Method' only); M1 needs the three names on the Node one. The image size
  vs the node's Bounds is MEASURED in the shots script (recorded per shot, not predicted).
- (4) ACCEPTED: the UID echo is a hard check in every shot (tools/bench/pi_shots_20261016.py: a shot whose echo != uid
  is a FAIL); subdiagram inclusion is a measurement; Image Depth 24 is set explicitly (pi_shots_lib.get_image depth=24).
- (5) PARTLY: the side-by-side Node/GObject scratch test is M1/M1b; the run on a single Add node is replaced by the op's
  hygiene workload on a real node of a byte copy (the op's own build gates come first).
