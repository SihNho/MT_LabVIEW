---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# display-harness-build-run2

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (29s)
- **why asked:** failed prediction at build steps 7/10 of the display harness.
- **verdict:** explanation accepted; fixes applied (exact 'Image Pixels (U8)', node_terms for terminal reads, save only when every step succeeded); run 3 built all five harnesses.

## Question

FAILED PREDICTION check, brief. tools/bench/build_harness_display.log run 2 (recipe tools/recipes/build_harness_display.py): step 7 raised 'no terminal among (Image Pixels, Pixels) on uid 9' - the IMAQ ImageToArray node lists 'Image Pixels (U8)', '(U16)', '(I16)', '(Float)' so my substring match was ambiguous (fix: exact 'Image Pixels (U8)' for the 8-bit fixture); and step 10 found NO terminals on the Draw Flattened Pixmap.vi node - the walker net_map stops after 3 consecutive empty (unassigned connector-pane) slots, so a VI whose pane starts with unassigned slots reports as terminal-less (fix: read terminals with node_terms, which returns the whole Node.Terminals[] array). The recipe then saved a disp3 with the tail UNWIRED (Create->ReadFile->ImageToArray only, plus dangling Flatten/Draw nodes) because its final ExecState check passed - the four files are deleted at the start of every run, so run 3 rebuilds from scratch. ATTACK: (1) is 'Image Pixels (U8)' the correct output of the polymorphic IMAQ ImageToArray for an 8-bit grayscale IMAQ image (does a polymorphic node placed by script select the instance by the wired type, or must the U8 instance VI be dropped explicitly?) (2) any reason Draw Flattened Pixmap.vi's Terminals[] would be genuinely empty (e.g. the VI failed to load - broken/missing dependency - rather than a walker artefact), and the cheapest check (node_terms count; ExecState after wiring); (3) the recipe should FAIL, not save, when a planned wire step raised - agree that 'all planned steps ok' must be part of the save gate? One paragraph.

## Answer

(1) **Prediction partly fails:** U8 is the correct array type for an 8-bit grayscale fixture, but wiring the IMAQ image reference alone may not select U8 because every instance accepts that same reference; polymorphic selection depends on a uniquely determining wired type, otherwise the instance must be selected explicitly?봲o drop/select the U8 instance or constrain its output to U8, then require exactly `Image Pixels (U8)` ([NI polymorphic-VI behavior](https://download.ni.com/support/manuals/320999e.pdf), [NI ImageToArray description](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000kEYnSAM&l=zh-CN)). (2) A successfully loaded Draw Flattened Pixmap subVI should not genuinely have zero assigned connector terminals; `node_terms` count is the cheapest discriminator, while zero should trigger inspection of the node?셲 resolved VI/path and load error?봭ot be treated as usable. `ExecState` after complete wiring is the secondary check because missing dependencies or broken subVIs make a caller nonexecutable, but dangling nodes or optional unwired terminals need not break it ([NI connector panes](https://www.ni.com/docs/en-AS/bundle/labview/page/assigning-terminals-to-controls-and-indicators.html), [NI broken-VI causes](https://www.ni.com/en/support/documentation/supplemental/12/debugging-techniques-in-labview.html)). (3) Yes: saving must require **every planned operation succeeded**, all expected wires were positively verified, and final `ExecState != Bad`; `ExecState` alone only reports executability, not recipe completeness or intended topology ([NI execution-state meanings](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YIEJCA4)).

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
