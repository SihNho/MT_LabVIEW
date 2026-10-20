# hypothesis-op-getbdimage

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $0.7004  in 18 / out 8610 / cache-create 46999 / cache-read 483270  (117s, 15 turn(s))
- **date:** 2026-10-19 10:45:26
- **outcome:** ANSWERED (121s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** failed prediction M1 in tools/bench/build_op_getbdimage_v0.log (card chat-PI2), owed per JEV-LADDER before the retry chat-PI2b
- **verdict:** hypothesis supported (method right; short names) - weakest point the loosened M1 gate (R1), applied

## Question

HYPOTHESIS REVIEW (failed prediction, card chat-PI2 -> retry chat-PI2b). Short answer wanted (<= 40 lines).
Failing log: tools/bench/build_op_getbdimage_v0.log

FAILED PREDICTION: tools/recipes/build_op_getbdimage_v0.py gate M1 (lines 70-71): a `VI Server:VI` Invoke with method ID
42C (Block Diagram: Get Image Scaled, https://labviewwiki.org/wiki/VI_class/Block_Diagram.Get_Image_Scaled_method) has
terminals named exactly "Image Depth" and "Image Data" plus one containing "Width" and one containing "Height".
Measured (tools/bench/build_op_getbdimage_v0.log:8): Invoke #43 terminals reference / reference out / error in (no error) /
error out / GetDiagramImageScaled (IN,OUT) / img depth (IN,OUT) / img data (IN,OUT) / max width (IN,OUT) /
max height (IN,OUT). The gate is case-sensitive on long names, so it failed on "img depth" / "img data"; "Width"/"Height"
failed too because the short names are lower-case "width"/"height".

MY HYPOTHESIS: the method is the right one; LabVIEW's scripting terminal Name property returns the SHORT names of a
method's parameters (same as Node.Get Image 6358C01, which read "BG Color" for the wiki's "Background Color",
tools/bench/build_op_getimage_v0c.log, accepted in card chat-PI1d). The gate wrongly assumed long names. Judgement
already accepted the short names (card chat-PI2b).

THE RETRY PLAN (attack this):
1. Gate M1 becomes case-insensitive and accepts short OR long names: {img depth | image depth}, {img data | image data},
   any name containing "width", any containing "height" (lower-cased).
2. Builder B3/B4 use the measured short names: b.ctl(gi, "img depth") for the Image Depth control (set to 24 by the
   caller), b.w(gi, "img data", WritePNG, <image sink>), max width / max height left UNWIRED (wiki: unwired = actual size).
3. Each terminal name appears TWICE (IN and OUT) as on every VI Server Invoke parameter; the wiring helper picks the
   sink row (is_source False) for ctl and the source row (is_source True) for the wire, as in OpGetImage_v0 where
   "Image Data" OUT went to Write PNG File.vi `image data` (build_op_getimage_v0d.log).
Questions: (a) is any risk that the IN-side "img data" row is picked as the wire source, or that the OUT-side "img depth"
row gets the control? (b) is there evidence that Get Image Scaled needs the front panel/diagram window open or the VI
idle (so the call would fail headless), and what error would LabVIEW give? (c) anything else in the plan likely to fail?
Answer with: VERDICT (hypothesis supported / refuted / unclear), the risks ranked, and a falsifier for each.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**VERDICT: supported on which method this is. Not proven on why the names are short, but that doesn't change the fix. The weakest part of the retry is the loosened M1 gate.** Nothing was run, built or edited, and no lock was taken. I couldn't write the review file because Write is turned off in this session, so the full review is here.

**1. Strongest reason the claim may be wrong.** "The terminal Name returns short names" is a guess made after the result, not a measured mechanism.
- Node.Get Image read `Image Depth` for that parameter (`tools/bench/build_op_getimage_v0d.log:8`). Here the same parameter reads `img depth`.
- So either NI gave this method its own abbreviations, or something else picks the name format.
- I couldn't check NI's short-name list: the documentation.help copy of the NI page returned 403. The wiki gives only long names: [labviewwiki](https://labviewwiki.org/wiki/VI_class/Block_Diagram.Get_Image_Scaled_method).

**2. Alternative explanation.** The node's display name setting (short or long names) may decide the names, rather than something fixed in Name itself.
- This run can't tell the two apart.
- It doesn't matter for the retry: the builder creates the node through the same `g.build_invoke` call (`tools/recipes/build_op_getbdimage_v0.py:66` and `:88`), so it should see the same names.
- The method itself is clearly right. The return terminal is named `GetDiagramImageScaled`, which matches NI's page name VI_Get_Diagram_ImageScaled. The four parameters match the wiki's four.

**3. Risks in the retry plan, worst first, each with what would show it:**
- **R1. The new M1 can't fail.** Ignoring case, accepting short or long names, and "any name containing width" would pass almost anything.
  - Fix: require exactly the list measured at `build_op_getbdimage_v0.log:8`.
  - Shows it: any other list fails the gate.
- **R2. Labels file key (your question c).** `pi_shots_lib.py:187` reads `c["Image Depth"]`.
  - Keep that key and store whatever label `b.ctl` returns. The new control is probably labelled with the long name: in v0d, `BG Color` became a control labelled `Background Color` (`build_op_getimage_v0d.log:53`).
  - Renaming the key to `img depth` would make the first F1 call fail with a KeyError.
  - Shows it: the labels JSON after B5.
- **R3. Picking the IN or OUT row (your question a): low risk.**
  - `B.ctl` takes only the input row (`tools/bench/diag_c100_verbs_build.py:110`), so `img depth` gets row 6 (IN), which is correct.
  - `B.w` wires by name through OpWire. The same route wired the duplicated `Image Data` correctly in v0d (`build_op_getimage_v0d.log:50`).
  - A wrong pick would be an input wired to an input. That is a broken wire, so B6 (ExecState 1) would fail.
  - Gap: B4c only checks that Write PNG's input is wired, not where the wire comes from. Add a check that row 9 (`img data` OUT) carries a wire.
- **R4. Running with no window open (your question b): medium risk.**
  - The wiki says the method "Must wait until user interface is idle" and loads both the front panel and block diagram into memory itself, so neither needs to be open.
  - It also says it isn't available in the Run-Time Engine. NI's documentation also excludes control VIs, global VIs, polymorphic VIs and strict type definitions ([labviewwiki](https://labviewwiki.org/wiki/VI_class/Block_Diagram.Get_Image_Scaled_method), [NI help copy](https://documentation.help/NI-LabView-Local-Project-Settings/VI_Get_Diagram_ImageScaled.html)).
  - I found no published error code for a busy interface. The likely failure is a hang, not an error.
  - Counter-evidence: Node.Get Image ran 2,000 calls with no window open (card chat-PI1d).
  - Shows it: F1 running past its time limit while the error stays empty.
- **R5. Image depth 1 crashed this method in LabVIEW 2014–2015**, fixed in 2017 ([NI 2017 bug fixes](https://www.ni.com/en/support/documentation/bugs/17/labview-2017-bug-fixes.html)). This doesn't matter at depth 24; just never default it to 1.

**4. What would refute the hypothesis.** The cold re-read (B7) or the F1 build showing different names for the same 42C node, or F1 returning an error or a blank PNG with depth 24 wired. Either would mean the names or the method are not what M1 assumes.

**5. Cheapest test that separates the two causes.** It costs nothing extra in the retry: log the node's display name setting next to the terminal names in step [1].
- If it reads "short names", both explanations still hold and nothing changes.
- If it reads "long names" while the terminals still show `img depth`, the display setting is ruled out and your explanation stands.

What would change my mind: F1 fails with no error while using the same names. That would point at R4 (the busy-interface wait), not at the names.

## Sources

(extract from answer)

## What was done with it

Card chat-PI2b (material), 2026-10-19:
- R1 ACCEPTED: M1 now requires EXACTLY {GetDiagramImageScaled, img depth|image depth, img data|image data,
  max width|maximum width, max height|maximum height} (lower-cased set, nothing else) - tools/recipes/build_op_getbdimage_v0.py check_method().
- R2 ACCEPTED: the labels key stays "Image Depth" (pi_shots_lib.get_bd_image reads it); the measured terminal name
  (input row) is passed to b.ctl.
- R3 ACCEPTED: B4c also checks that the Invoke's OUT-side img data row carries the same wire as Write PNG's image sink.
- R4 noted: F1 and the hygiene run are the falsifier (a hang shows as a bgrun TIMEOUT with no error).
- R5 n/a (depth 24 / 8 only). The display-name probe (point 5) not added: no verified property name for it.
- Judgement (card chat-PI2b) had already accepted the short names; this review gated the retry.
