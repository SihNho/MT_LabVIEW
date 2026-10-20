# Plan under prior-art review - card chat-PI1c (retry of chat-PI1b), 2026-10-16

Same goal as chat-PI1b (brief `tools/bench/cards/brief_chat-PI1.md`: readable PNG crops of the key part of three VIs'
block diagrams for the PI; read-only on the sources; no hardware; no VI under study is ever run).

## What changed since the chat-PI1b review (archive/peer/2026-10-16-priorart-op-getimage.md, verdict novel)
- chat-PI1b FAILED at M1: no Image output among VI Server:GObject methods 632A401..40F (tools/bench/build_op_getimage_v0.log:8-23).
- External source (labviewwiki Node_class/Get_Image_method): Get Image is a NODE-class method, ID 6358C01, inputs Image
  Depth / Background Color, output Image Data. Hypothesis review archive/peer/2026-10-16-hypothesis-op-getimage.md
  ("partly": the brief mixed Control.Get Image 6331C0C with Node.Get Image).
- New donor: `OpSetIndexMode_v0.vi` (Traverse(Class Name, index) -> Index Array -> To More Specific Class), retargeted
  with a Node-typed control seed (the c97 route, tools/bench/diag_c97_tools_opbuild.py retarget()), because the GObject
  output of `UID to GObject Reference.vi` cannot feed a Node-class Invoke. TMSC -> Node PN Position 632A800 + Bounds
  632A803, TMSC -> Invoke Node.Get Image 6358C01 -> Write PNG File.vi, TMSC -> GObject.UID 632A813 echo.
- Recipe `tools/recipes/build_op_getimage_v0.py` (rewritten), helpers `tools/bench/pi_shots_lib.py` (OpBuilder /
  retarget are a marked copy of diag_c97_tools_opbuild.py:43-125 - that file runs its build at import time and gscript.py
  is outside this card's write globs).
- After the build: `gscript.hygiene_run` 2,000 calls -> tools/bench/op_hygiene/OpGetImage_v0.json.

## Question for this review
Is the Node-seed retarget on OpSetIndexMode_v0 already built, failed, or covered for a Node-class Invoke (as opposed to
a property node)? Is there an existing op that already yields a Node-typed reference by UID? Anything recorded about
Get Image / image data / Write PNG File.vi in this project?
