# c164-a3-5-mkgraph-termidentity

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.2494  in 24 / out 10388 / cache-create 102796 / cache-read 1096062  (140s, 19 turn(s))
- **date:** 2026-10-10 15:38:55
- **outcome:** ANSWERED (144s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about a failed prediction in tools/bench/diag_c164_a3_5_mkgraph.py (log tools/bench/diag_c164_a3_5_mkgraph.log, card 164-3-5).

Context: the helper is OFFLINE (no LabVIEW). It writes the decision-row plan for a read-only graph read of an adopted LabVIEW VI. Its gate W predicted
len(term_identity.new) == 7, where term_identity comes from tools/bench/diag_c164_p5s02d_scratch.json (written by the PASSED scratch run,
tools/bench/diag_c164_p5s02d_scratch.log RESULT PASS 21/0 at :269). Measured: term_identity.new = 9 wires [12150, 23519, 31712, 31744, 31749, 31792,
31818, 31825, 31884]; CENSUS-ALL new uids by class says Wire 7 (log :223); the D gate PASSED with 8 new (source, sink) pairs (log :220).
The same helper for the previous step (tools/bench/diag_c163_a2_2_mkgraph.py:71) predicted 6 and saw 6, matching CENSUS-ALL Wire 6 there.

CLAIM: this is a prediction error in MY helper, not a defect in the VI or the scratch: term_identity.new is the set of wire uids whose (source, sink)
identity is new after the run, which includes OLD wire uids that were re-ended by this step (23519 lost one sink to wire_remove_loose_ends at op 5;
12150 and 31712 are pre-existing uids that gained or lost an end), so it need not equal the count of new Wire uids. In step 3 it equalled 6 only
because no old wire was re-ended. Fix: gate W on the D gate (8 pairs) and record len(new) as measured (>= 7), then continue.

Find the code that builds term_identity["new"] (tools/stagekit.py, search term_identity) and check whether it really includes re-ended old uids.
Give: the strongest reason the claim is wrong; an alternative explanation (e.g. a wire that should have been deleted survived, or a duplicate wire
was created); what would falsify it; the cheapest discriminating test (which uids to look up in tools/bench/graph_ring_p5s02c_20261010_131658.json,
the base graph, and in tools/bench/plan_ring_p5s02d.json).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict: the claim mostly holds, but one of its three supporting examples is wrong, and the proposed fix is too loose to keep.** The count does come out right: 9 = 7 newly created wire uids + 2 old wire uids that were re-ended. But 12150 is not an old wire; it is one of the 7 new ones.

**What the code does.** `term_identity_pos` (`tools/stagekit.py:1506-1519`) computes `new` as the wire end-pairs found in the read-back graph but not in the base graph. It then reports `new` as the real wire uids holding those pairs: `uids(re_, new)` at `:1511` and `:1519`. So yes, an old uid whose ends changed lands in `new`, and its old end-pair lands in `lost_w` (`:1508`). The mechanism the claim relies on is real.

## 1. Strongest reason the claim is wrong: 12150 is a new wire
- 12150 appears **nowhere** in the base graph `tools/bench/graph_ring_p5s02c_20261010_131658.json`. A grep for it found 0 matches.
- It is also **not** in `wires_lost` (`diag_c164_p5s02d_scratch.log:220`). A pre-existing wire that "gained or lost an end" would show up in both `wires_new` and `wires_lost`.
- Its ends in the scratch JSON (`diag_c164_p5s02d_scratch.json:9874-9885`): source is term 31816 on the new register 31807, sink is term 31810 'file progress' on the new tunnel 31803. That makes it the step's own new wire `w_k3pass`. LabVIEW gave it a low recycled uid, just as it gave 12169 and 12170 to the new Local and Equal? nodes (log :113, :143).
- The correct split, checked against the base graph:

| group | uids | evidence |
|---|---|---|
| new (7) | 12150, 31744, 31749, 31792, 31818, 31825, 31884 | none in the base graph; matches CENSUS-ALL Wire 7 (log :223) |
| re-ended (2) | 23519, 31712 | in the base graph, and in **both** `wires_new` and `wires_lost` (log :220) |

- The step-3 comparison holds: there `wires_lost` was `[]` and `wires_new` was 6 = CENSUS Wire 6 (`diag_c163_p5s02c_scratch.log:139,142`).

So the diagnosis "a helper prediction error, not a defect in the VI" survives. The stated reasoning does not, and it should be corrected before it goes into the plan's cite text.

## 2. Alternative explanation (now ruled out)
- **A duplicate wire.** Two real uids holding the same end-pair would make the uid list longer than the pair count. That would show up as a new uid that is not counted in CENSUS-ALL, or as old uids in `new` that are missing from `lost_w`. Neither happened: 7 new uids match the census exactly, and the 2 old uids are both in `lost_w`.
- **A wire that should have been deleted survived.** Also ruled out. `lost_w` minus `new` gives 23460, 23489 and 24330. 24330 is the base wire from term 5704 (SubVI 376 'file progress') to control terminal 3453. It was replaced when op 14 connected #5704 into the K3 register (log :203). The D gate's lost pairs, 4 == sim's 4, show the simulator expected that loss.
- **One loose end:** the helper's DW gate (`diag_c164_a3_5_mkgraph.py:76`) never names 24330. That is not a defect, but it is an unchecked loss.

## 3. What would falsify the claim
Any of these:
- an uid in `new` that is in the base graph but not in `lost_w` (an old wire that kept its ends yet was counted as new, which would mean a duplicate);
- the count of uids in `new` that are absent from the base graph differing from CENSUS-ALL "Wire" new uids;
- an old uid appearing in `new` but missing from `wires_lost`.

None of these occurs in the recorded data.

## 4. Cheapest discriminating test, and why the fix is too weak
Done above with three greps. The proposed gate, `len(new) >= 7`, would also pass on 10 uids with a real duplicate wire in them, so it hides exactly the alternative it is meant to rule out. Gate W should check the split itself:
- `N = set(new) − base_wire_uids`, with `len(N) == CENSUS-ALL Wire` (7);
- `O = set(new) ∩ base_wire_uids`, with `O ⊆ set(lost_w)` (here {23519, 31712});
- D gate `pairs 8 == 8` still required.

The helper on disk already carries the `>= 7` form (`diag_c164_a3_5_mkgraph.py:73-74`). It should be tightened to the check above, and the wording "12150 pre-existing" should be dropped from any record.

**What would change my mind:** a base graph other than `graph_ring_p5s02c_20261010_131658.json` turning out to be the true base for step 4, if that graph contains 12150.

I did not run anything. Evidence is local files only; no web claims were needed.

## Sources

(extract from answer)

## What was done with it

ACCEPTED in full (card 164-3-5, material session). The review is right that 12150 is a NEW wire (w_k3pass), not an old re-ended one; the
re-ended old uids are 23519 and 31712. The `>= 7` form was dropped: gate W of tools/bench/diag_c164_a3_5_mkgraph.py now checks the split itself -
`new` minus the base graph's wire uids == 7 (CENSUS-ALL Wire 7), `new` ∩ base wire uids ⊆ `lost_w`, D gate pairs 8 == 8. 24330 (replaced by
op 14's connect of #5704) is recorded as a fact in tools/bench/diag_c164_a3_5_facts.md. Run 1's log kept as diag_c164_a3_5_mkgraph_run1.log.
