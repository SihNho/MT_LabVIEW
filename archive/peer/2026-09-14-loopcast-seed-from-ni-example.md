---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# loopcast-seed-from-ni-example

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (63s)
- **why asked:** failed prediction in build_oploopcast_v0.log (Create For Loop.vi has no ForLoop-typed output) and the plan change to seed from NI's Structures example
- **verdict:** unverified

## Question

PLAN CHANGE review (attack; one paragraph). Previous plan (archive/peer/2026-09-14-loopcast-typed-terminal-seed-plan.md, you said YES to the key claim): make a ForLoop-typed refnum CONTROL with Terminal.Create Control on erdosmiller Create For Loop.vi's typed output, feed it to To More Specific Class 'target class'. FAILED PREDICTION (tools/bench/build_oploopcast_v0.log): Create For Loop.vi has NO ForLoop-typed output - its terminals are Diagram in/out, Inputs (tunnel array), Shift Registers (array), Loop Counter (terminal ref), Loop Count Terminal (input), Number of Static Parallel Instances, error in/out, three unnamed sinks. NEW SEED SOURCE: NI's shipped example '<LabVIEW 2026>\examples\Application Control\VI Scripting\Structures\VI Scripting with Structures - For Loop.vi' (offline byte scan: contains the strings 'ForLoop' and 'Loop Count' - presumably New VI Object with a ForLoop class-specifier constant, then ForLoop properties). PLAN: (1) copy the example to a scratch (never touch the original); (2) locate the New VI Object node and its ForLoop-typed 'new object' output (or any ForLoop-typed wire/terminal) by node_terms/node_labels; (3) Terminal.Create Control on that OUTPUT terminal - QUESTION: does Terminal.Create Control on a SOURCE (output) terminal create a control at all (the GUI offers only Create Indicator on outputs), and if it creates an indicator instead, is there a scripted way to get a CONTROL of that refnum type (e.g. Create Control on an INPUT terminal that is ForLoop-typed downstream, such as a ForLoop property node's 'reference' input in the same example)? (4) copy_into(scratch, <control label>, OpLoopCast) - our proven object mover by label (front-panel objects included) - to bring the typed control into the op; (5) wire it to TMSC 'target class' as before. ALTERNATIVE: move the example's ForLoop class-specifier CONSTANT itself into the op (it is a GObject under Constant, NOT in Diagram.Nodes[], and our label-setter works only on Nodes[] - so we cannot label it for the mover; is 'Constant' reachable via Traverse and GObject.Label writable through a GObject-typed ref? yes in principle - but that is another op build). ATTACK: which is cheaper/safer; any NI documentation on Terminal.Create Control applied to output terminals; and confirm that a refnum control created from a property node's ForLoop-typed 'reference' INPUT carries the ForLoop class.

## Answer

Attack verdict: use the property node?셲 ForLoop-typed `reference` **input**, not `New VI Object.new object`, as the seed. NI?셲 public documentation does not appear to specify what `Terminal.Create Control` does when invoked on a source terminal; NI consistently documents the editor operation as **Create Control on inputs** and **Create Indicator on outputs**, so expecting `Create Control` on `new object` either to succeed or silently substitute an indicator is an unsupported gamble ([NI example](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000015BHlSAM), [NI manual](https://download.ni.com/support/manuals/320999b.pdf)). Conversely, creating a refnum control from the property node?셲 `reference` input should preserve the terminal?셲 compile-time ForLoop class: NI says a refnum?셲 selected VI Server class determines which object class it accepts, and that wiring a typed reference selects the Property Node?셲 class ([NI Core 2 manual](https://download.ni.com/evaluation/training/lvcore2_coursemanual_english_sample.pdf)); NI also explicitly says a class-specifier constant can be created from a control-refnum control or terminal ([Class Specifier Constant](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/constants/class-specifier.html)). The cheapest safe sequence is therefore: find a property/invoke node whose `reference` **input is demonstrably ForLoop-typed**, invoke `Create Control` there, verify the resulting FP object is a control and that wiring it to TMSC `target class` is unbroken, then move that labeled control into `OpLoopCast`. Do not assume that merely belonging to a ?쏤orLoop property node??proves the input remained ForLoop-typed?봠onfirm by terminal datatype/class or by the successful TMSC wire after save/reopen. Moving and relabeling the class-specifier constant is a reasonable fallback, but it adds Traverse/cast/label machinery and therefore has a larger bootstrap surface than the typed-input route.

## Sources

(extract from answer)

## What was done with it

Followed exactly: the probe (probe_example_forloop.log) showed the example's ForLoop class constant feeding five
ForLoop property nodes over one wire; the wire was deleted on a scratch copy, Create Control on the LpCount node's
'reference' input produced a control labelled 'reference', the other four nodes were deleted so the scratch stayed
runnable for a COM save, copy_into moved the control onto OpLoopCast_v0, and the TMSC wire from it compiled
(build_oploopcast_v0.log run 2, ExecState 1 throughout). Verdict: correct; the input-terminal route worked first time.
