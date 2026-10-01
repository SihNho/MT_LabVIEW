ATTACK this claim (failed prediction in tools/bench/stage_d1_ring_p3a_scratch.py -> tools/bench/stage_d1_ring_p3a_scratch_pin.log:65-71).

Setting: LabVIEW 2026 VI Scripting driven over COM from Python. Before any LabVIEW edit, an offline simulator
(tools/stagesim.py) applies a stage plan (tools/bench/plan_ring_p3a.json, built from plan_ring_p3a_in_v3.json) to a graph
of terminal rows read earlier from the real VI (rows keyed by owner_class, term_class, is_source, term_name). The executor
(tools/stagexec.py) then runs each plan op on a scratch copy and, after each op, compares the simulator's terminal keys of the
NEW node with the real terminal table read back from LabVIEW ("BINDING" check).

Observed: op 1 (create primitive `Wait (ms)` from donor OpWaitDonor_v0 uid 163 onto Diagram #639) succeeded, err '', new
Function #26747 with two terminals 'millisecond timer value' (source) and 'milliseconds to wait' (sink), both read back as
class `ParameterTerminal` (log:65-67). The simulator keyed them `('Terminal', ...)` (log:71) and the run stopped there.

The explanation formed:
 (1) Cause on the PLAN side: plan_ring_p3a_in_v3.json:28-37 declares p3a_wait's terminals with name + is_source only, no
     `term_class`; tools/stagesim.py:1317 uses `t.get("term_class") or "Terminal"` for a declared terminal. LabVIEW reports a
     primitive Function's / Comparison's terminals as ParameterTerminal (also seen in the bed graph
     tools/bench/graph_ring_p2b_20261001_154542.json for the Equal? donor #10019: three ParameterTerminal rows).
 (2) Fix: regenerate the plan with an explicit, MEASURED `term_class` on every terminal each created node declares (Wait (ms),
     Equal?, Increment, Quotient & Remainder from the bed graph rows of their $work donors #10019/#1978/#2136, and the three
     I32 constants from measured constant rows), leave stagesim.py's default unchanged (other plans rely on it), re-simulate
     (predicted census and Error List unchanged, since a class key changes no census count), then rerun the scratch.

Already ruled out: the create op itself failing (err '', node present, 2 terminals, refs balanced 4/4, bed md5 unchanged);
a wrong donor (label 'Wait (ms)' read back).

Questions to attack: Is the binding mismatch fully explained by the missing declaration, or could other created nodes in the
same plan (DigitalNumericConstant terminals; the CaseStructure's selector made by a case route; the const_on_term constant
WK1 whose terminal is derived from its sink, not declared) still hit the same check with a different real class after the fix?
Could the bed-graph donor rows differ in class from a freshly created copy (e.g. polymorphic primitives, or a copied node
reading as a different class)? What would falsify the fix before spending a LabVIEW run, and what is the cheapest test?
