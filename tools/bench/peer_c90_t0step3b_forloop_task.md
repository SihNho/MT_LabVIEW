ATTACK this claim (failed prediction, card 90-6, log tools/bench/diag_c90_t0_step3b.log, script tools/bench/diag_c90_t0_step3b.py, run 1).

CONTEXT: PD197(g) (docs/d1-loop12-17-split-plan.md:1106-1118) instruments a byte copy of claudeDev\D1_s1_copy.vi with t0stamp
CLFN nodes: build_clfn at top level -> stagekit.move_in (GObject.Move by uid) into the site diagram -> OpCreateConstOnTerm_v0
creates the I32 `site` constant IN PLACE on the moved CLFN's t6 (addressed <loop class>[i].Diagram.Nodes[n].Terms[6]) ->
OpConnectFromWire_v0 branches the site wire into t8 -> ExecState read after EVERY site. The op OpCreateConstOnTerm_v0
(tools/recipes/build_opcreateconstonterm_v0.py, docs/toolkit-capabilities.md:70) was built and measured 22/0 with
`Class Name` = 'WhileLoop' only; its ladder is Traverse(<Class Name>)[index] -> To More Specific Class -> Loop.Diagram 6361401
-> Nodes[] -> Terms[]. Run 1 passed 'ForLoop' as the class for the five For-body sites.

OBSERVED (diag_c90_t0_step3b.log):
 - Sites 0 and 2 (While body #637, Class Name 'WhileLoop'): constant created (uid #23202 / #23441, err ''), t6 wired, branch
   Is Broken? False, sink count +1, t8 wire == site wire, ExecState 1 after each site (:58-79, :114-135).
 - Site 3 (For body Diagram[50] #29894, owner read live = ForLoop #..., Class Name 'ForLoop'): the invoke's own error
   `error 1055: Invoke Node in OpCreateConstOnTerm_v0.vi` (:172), the op's UID indicator read back #23441 = the PREVIOUS
   site's constant although it was set to 0 before the run, CLFN t6 wire 0 (:173), ExecState 0 (:175). Same 1055 on sites
   4, 5, 16, 17 (:213, :253, :573, :613).
 - Sites 8, 10-13, 20 (While bodies) after that: constant + branch all PASS but ExecState stays 0 (:312, :368, :424, :480,
   :536, :672). ES TABLE :673. cdiff rows 0, added 21 = CallLibrary + DigitalNumericConstant only (no Invoke junk) (:677).

MY EXPLANATION (the claim to attack):
 1. OpCreateConstOnTerm_v0 cannot address a For-loop body: with `Class Name` = 'ForLoop' the ladder's To More Specific Class
    (or the Loop.Diagram property on the cast) raises 1055 because the op's cast target is WhileLoop-specific (it was built
    from the OpStopFromNode_v0 donor whose class constant is WhileLoop), so a For-body terminal needs a different creator
    route (e.g. review archive/peer/2026-09-26-c90-t0step3-movewire.md section 5: constant at top level, move both, then
    OpConnectNested on the body diagram).
 2. ExecState 0 from site 3 onward is the bare CLFN left in the For body (t6 and t8 unwired, an unwired required input);
    the zeros after sites 8-20 are inherited from sites 3/4/5, not caused by those sites (sites 0 and 2 alone left
    ExecState 1). So a run with the eight While-body sites only should end ExecState 1 and save.
 3. The UID readback #23441 on error is history-determined (the op's uid indicator keeps its last value when the invoke
    errors before the uid write; my SetControlValue(...,0) before the run did not take) - a reader defect, not a created
    object.

ALREADY RULED OUT: the moves failing (err '', find_node lists the CLFN on the For-body diagram by uid echo); owner_of not
answering (strict uid echo, 'ForLoop' with the right uid); junk Invokes (every purge deleted exactly one Invoke, cdiff adds no
Invoke); Adapt-to-Type refusal on the While-body wires w3268/w5859 (ExecState 1 after those two sites).

Give: the strongest reason any of 1-3 is wrong; an alternative explanation for the 1055 on ForLoop and for ExecState 0
staying 0 after site 8; what would falsify each; the cheapest discriminating test. Also: with the ops this project owns
(docs/toolkit-capabilities.md rows 69-72, tools/gscript.py connect_nested_v2), what is the cheapest route to a typed, wired
I32 constant on a CLFN terminal inside a For-loop body?
