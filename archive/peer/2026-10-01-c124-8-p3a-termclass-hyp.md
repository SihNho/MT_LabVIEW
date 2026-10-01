# c124-8-p3a-termclass-hyp

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.5558  in 34 / out 12575 / cache-create 112192 / cache-read 1894217  (150s, 29 turn(s))
- **date:** 2026-10-01 17:28:31
- **outcome:** ANSWERED (153s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** failed prediction stage_d1_ring_p3a_scratch_pin.log:71 (BINDING term_class at op 1), Jev ladder new-problem p=0.664, review owed (card 124-8 S0)
- **verdict:** unverified

## Question

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


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Partly. The missing class declaration does fully explain the op-1 stop. But the fix will only work if each terminal's class is copied from its own measured row, not assumed to be `ParameterTerminal` everywhere. And nothing has yet read back the classes of freshly copied primitives, apart from Wait (ms) in this run.

**1. Strongest reason the claim is wrong as stated**

The classes are not the same across primitives. In the base VI graph, Increment's output is a different class from its input:
- `x+1` (row 2037) is `OverridableParameterTerminal`.
- `x` (row 2042) is `ParameterTerminal`.

That class is the one carrying a Representation (output-configuration) override in VI Scripting ([labviewwiki](https://labviewwiki.org/wiki/OverridableParameterTerminal_class/Representation_property)). The Q&R and Equal? terminals are all plain `ParameterTerminal`. So any fix that copies "ParameterTerminal" from the Wait/Equal? pattern will stop again at the Increment create.

Also note how the check behaves once the classes differ. With one `Overridable` and one `Parameter` terminal, `bind_new` compares the class alone (`tools/stagexec.py:756-764`), not the class and name. Any difference in class between the donor and the copy is then fatal, and the name can't rescue it.

**2. Alternative explanation of the same evidence**

The plan's omission is the immediate cause. The deeper fault is that the offline check let a primitive be created with no class declared, and that was knowable before any LabVIEW run:
- In the base VI graph, no row owned by a `Function` or `Comparison` has the class `Terminal`. I counted 0 matches. So the simulator's default `t.get("term_class") or "Terminal"` (`tools/stagesim.py:1317`) can never match a created primitive.
- Earlier plans did declare it: `tools/bench/sim/disp/plan_disp.json:630-643` gives the same Wait (ms) `ParameterTerminal` on both terminals, and `plan_qrt_pool_in.json:31-59` does the same. The p3a plan dropped it in v1, v2 and v3.

Regenerating this one plan fixes this run, but not the cause. The next plan can make the same mistake and cost another LabVIEW run. Leaving `stagesim.py`'s default unchanged is fine, but the pre-run should refuse a primitive create (`Function`/`Comparison` with `prim`) that has an undeclared class.

**3. Your specific questions**

- **Constants (`p3a_k_prev`, `p3a_k_cnt`, `K20`, and `WK1` from the constant-on-terminal step):** every DigitalNumericConstant row in the base graph is `Terminal`, and each constant has exactly one row. The check therefore compares the class alone, and the default matches. The derived `WK1` row (named "milliseconds to wait", class `Terminal`) is fine for the same reason. Low risk.
- **Case selector and case tunnels (`TI1`, `TO1`):** these go through `bind_case_faces` (`stagexec.py:776-820`), which matches by frame and by `Inner`/`OuterTerminal`. The simulator builds `SelectorTunnel` objects with those classes (`stagesim.py:864-866`). The diagnostic run measured exactly that shape (`diag_c124_p3a_scratch.log:53,61`). Low risk.
- **Donor vs fresh copy:** this is untested. The diagnostic created Equal? E1, Increment I1 and Q&R Q1 on the same base VI (`diag_c124_p3a_scratch.log:36-49`) but never read their terminal classes back. Since a Representation override is a per-terminal setting, the `Overridable` class is most likely tied to the primitive's terminal type rather than to the copy, so a duplicate of #1978 should keep it. I haven't verified that on a fresh copy.
- **Wait (ms):** this run measured it (`log:66-67`), and that agrees with plan_disp.

**4. What would falsify the fix**

Either of these, read on a fresh copy:
- Increment's `x+1` comes back as anything other than `OverridableParameterTerminal`.
- Any Q&R or Equal? terminal comes back as anything other than `ParameterTerminal`.

Or the regenerated plan carries a class that wasn't copied row by row from its donor.

**5. Cheapest test that separates the claim from the alternative (offline, no LabVIEW)**

Run `bind_new`'s key logic (`stagexec.py:756-764`) on the regenerated plan's created rows from `stagesim` and compare against:
- donor rows #10019, #1978 and #2136 in `graph_ring_p2b_20261001_154542.json`,
- the Wait (ms) rows in plan_disp,
- one base-graph DigitalNumericConstant row.

It passes if, for every create action, the counts of `(term_class, is_source, name)` are equal on both sides. It also confirms the "Overridable" point in seconds.

The only part this can't settle is donor vs fresh copy. If that needs settling before the stage run, the cheapest LabVIEW act is a short scratch check: copy #1978 and #2136 once and read their terminal tables back. Otherwise it is settled by the rerun itself, which now stops at the first mismatch.

I still believe the cause is correct. I'd stop believing it if the rerun with per-row measured classes failed BINDING at Wait (ms) or Equal? again.

Sources:
- [OverridableParameterTerminal class / Representation property — LabVIEW Wiki](https://labviewwiki.org/wiki/OverridableParameterTerminal_class/Representation_property)

## Sources

(extract from answer)

## What was done with it

Not a refutation (card 124-8 S0): the reviewer keeps the cause (undeclared term_class on created-primitive terminals) and
sharpens the fix to ROW-BY-ROW classes. Applied: `tools/bench/plan_ring_p3a_make_v3b.py` copies each declared terminal's class
from its own measured row by (name, direction) - Equal?/Increment/Q&R from donor rows #10019/#1978/#2136 of
graph_ring_p2b_20261001_154542.json (Increment `x+1` = OverridableParameterTerminal, `x` = ParameterTerminal), Wait (ms) from the
124-7 scratch real table, constants from the base graph's DigitalNumericConstant rows (all Terminal). Donor-vs-fresh-copy is settled
by the scratch rerun, which stops at the first BINDING mismatch. The suggested pre-run refusal of an undeclared class on a primitive
create is a tooling change outside this card's write flags; reported to the judgement session as an open item.

JEV-DISCHARGE: plan_ring_p3a_make_v3b.log (2026-10-01 17:29:42, p=0.804)
  This failing run was released without a NEW peer review: Jev judged, at the probability shown, that the failure above is the one this review already attacks (tools/bench/jev_gate.py, docs/jev-integration-plan.md row #1). The review itself is the evidence; this line only records which failure was charged to it.
