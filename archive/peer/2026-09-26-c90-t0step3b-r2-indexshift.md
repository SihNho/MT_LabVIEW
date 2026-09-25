# c90-t0step3b-r2-indexshift

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.5585  in 14 / out 18024 / cache-create 122390 / cache-read 770871  (229s, 11 turn(s))
- **date:** 2026-09-26 05:20:07
- **outcome:** ANSWERED (233s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim (failed prediction, card 90-6, log tools/bench/diag_c90_t0_step3b_r2.log, script tools/bench/diag_c90_t0_step3b.py, run 2 = the eight While-body sites only).

CONTEXT: per site the script does build_clfn (top level) -> junk_purge -> ExecState read -> move_in(uid -> Diagram[d]) ->
find_node(uid) gives Nodes index n -> ExecState read -> OpCreateConstOnTerm_v0 on WhileLoop[i].Diagram.Nodes[n].Terms[6]
-> junk_purge (deletes the one zero-wired Invoke that move_in leaves) -> node_terms(d, n) reads t6 -> gate S.3 (t6 wire != 0)
-> connect_from_wire(sink d, n, t8 <- site wire) -> ExecState read. Run 1 (diag_c90_t0_step3b.log) passed all of this on
While-body sites 0 and 2 with ExecState 1 after each.

OBSERVED in run 2 (diag_c90_t0_step3b_r2.log):
 - ExecState is 0 right after build_clfn while the new CLFN sits BARE at top level (:42, and at every site :84,:143,...) and
   still 0 after move_in (:45). In run 1 ExecState came back to 1 after site 0's constant + branch (step3b.log:79) and after
   site 2 (:135).
 - Site 0: move_in's junk Invoke #22989 lives at Diagram[43] Nodes[73] (:48), find_node put the CLFN #22968 at N[74]; the
   constant #23202 was created on WhileLoop[1].N[74].t6 (err '' :61) BEFORE the purge; the purge deleted the Invoke at N[73]
   (:57); node_terms(43, 74) then read t6 wire 0 (:62) -> gate S00.3 FAIL -> no branch -> ExecState 0 after the site (:63).
 - Site 11: the same shape - Invoke #23543 at Diagram[99] N[23] (:268), CLFN at N[24], constant #23801 on N[24].t6 (:280),
   purge, node_terms(99, 24) t6 wire 0 (:281). Site 12's CLFN was then found at N[24] (:322) and site 13's at N[25].
 - Sites 2, 8, 10, 12, 13, 20: constant, t6 wired, branch Is Broken? False, sink +1, t8 == site wire - all PASS, but
   ExecState 0 after each (:124,:183,:242,:342,:401,:460). Final: 6/8 sites, ExecState 0, cdiff rows 0 added 16 (8 CLFN +
   8 constants, :465), not saved.
 - In run 1 the junk Invoke landed AFTER the CLFN in Nodes[] (Nodes[78] with the CLFN at 76, step3b.log:41-ish), so no shift.

MY EXPLANATION (the claim to attack):
 1. A CLFN with an unwired input (`site` I32 and/or `any` Adapt-to-Type, both pass-by-value) BREAKS the VI: ExecState is 0
    the moment it exists bare at top level, and returns to 1 only when both inputs are wired (run 1 sites 0/2). So the
    ExecState 0 after sites 2..20 in run 2 is INHERITED from site 0's CLFN, whose t8 was never branched.
 2. Site 0's and site 11's "t6 wire 0" are a READER fault of my script, not a creation failure: the constant WAS created on
    the CLFN (N[74] was the CLFN when the op ran), then the purge deleted the Invoke at a LOWER Nodes index, the CLFN shifted
    to N[73], and node_terms read the node now at N[74] (an original node), whose t6 is unwired. Fix: re-run find_node after
    every purge and use the fresh index for node_terms and connect_from_wire.
 3. Whether the junk Invoke sorts before or after the CLFN in Diagram.Nodes[] depends on position (Invoke at (2639,933) or
    (-14936,658) vs the CLFN at (1400+30k, 900+60(k%4))), so run 1 was lucky, not different.

ALREADY RULED OUT: the moves failing (err '', find_node uid echo on the site diagram); junk left behind (every purge deleted
exactly one Invoke; cdiff adds no Invoke); the constant op erroring (err '' / '' at both sites); Adapt-to-Type refusal on
w3268/w5859/w541/w19372/w19468/w19429/w34066 (branches landed, Is Broken? False, and run 1 read ExecState 1 after sites 0/2).

Give: the strongest reason any of 1-3 is wrong; an alternative explanation for ExecState 0 after a bare CLFN and for the
t6-wire-0 reads; what would falsify each; the cheapest discriminating test. Also: with a third LabVIEW run (~7 min), is
"re-find after every purge, then read t6 and branch" enough for all eight While-body sites to end ExecState 1, or is there
another index hazard in the sequence above?


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

I've finished reading both logs and the script. **Verdict: point 3 is refuted by your own two runs, point 2 is right in outline but wrong in one detail that hides a gate weakness, and point 1 is unproven for six of the eight sites.** Re-finding after every purge is necessary, but it is not enough to be confident of ExecState 1 in a third run.

## 1. The strongest reason the claim is wrong: point 3

Run 1 and run 2 did the same thing at site 0 and got opposite orders:

- **Same inputs in both runs:** CLFN uid #22968 (`step3b.log:26`, `r2:26`), same target Diagram[43] at (1400, 900) (`step3b.log:43`, `r2:44`), same junk Invoke uid #22989.
- **Run 1:** the Invoke was at N[74] (`step3b.log:46`), after the CLFN at N[73] (`:58`).
- **Run 2:** the Invoke was at N[73] (`r2:49`), before the CLFN at N[74] (`r2:61`).

So the order does not depend on position, and "run 1 was lucky" should be "the order is not controlled by anything we set".

Two more facts point the same way:
- Both "Invoke before CLFN" cases in run 2 were at y=900 (sites 0 and 11). But run 1's site 5 was also at y=900, at (1520, 900), and there the Invoke came after the CLFN (`step3b.log:238,241,253`).
- The same Invoke sat at census index 157 in run 1 (`step3b.log:55`) and 158 in run 2 (`r2:58`), even though its place in the diagram moved the other way. So the census order is not Nodes[] order either.

The practical consequence: **any Nodes[] index can go stale after any edit.** This includes edits made inside an op VI that you hand an index to, not only edits your script makes.

## 2. An alternative reading of the "t6 wire 0" results

After the purge, `node_terms(43, 74)` did not read an original node. It read nothing, because N[74] was past the end of the array:

- **Site 0:** Diagram[43] has 73 nodes of its own. Site 2 shows 76 nodes = 73 + CLFN0 + CLFN2 + Invoke (`r2:91`). So after site 0's purge there were 74 nodes, N[0]..N[73].
- **Site 11:** Diagram[99] has 22 nodes of its own (`r2:209`: 24 = 22 + CLFN10 + Invoke). After site 11's purge there were 24 nodes, and N[24] is again out of range.
- The same arithmetic shows constants are not counted in Nodes[] (a constant was present at `r2:49`, yet the node count still adds up to 75 without it).
- `gscript.py:966-967` says `node_terms` returns empty rows when the index is out of range. Line 102 of the script turns those empty rows into `w6 = 0` through `next(..., 0)`.

So gate S.3 cannot tell "the terminal is unwired" from "no such node". The re-find in lines 97–101 fixes this case, but the gate still has the weakness: it never checks which node it actually read.

Also, "the constant WAS created on the CLFN" is plausible but was never read back. S.2 only checks that a uid came back with no error.

## 3. An alternative for ExecState 0 after sites 2–20

"Inherited from site 0" fits the data, but so does "each of these sites breaks the VI on its own". Your ruled-out list overstates what was shown:

- Only w3268 and w5859 (sites 0 and 2) have ever been seen with ExecState 1 after their branch.
- Sites 8 and 10 read 0 in run 1 too (`step3b.log:311,367`), but by then the run had already been broken by the For-body sites.
- `Is Broken? False` is a property of the wire. It does not show that the CLFN parameter accepts the wire's type. An Adapt to Type parameter can reject some types; in one NI forum case, an array of strings inside a cluster broke the node ([NI forum 3832312](https://forums.ni.com/t5/LabVIEW/Call-Library-Function-Adapt-Interface-to-Data-Breaking/td-p/3832312?profile.language=en)).

So whether Adapt to Type accepts w541, w19372, w19468, w19429 and w34066 is still an open question.

For the bare CLFN at top level (`r2:42`), a narrower explanation also fits: only the unwired Adapt to Type input `any` (t8) breaks the VI, because its type is not yet known. An unwired input `site` (t6) of plain I32 type is normally fine; the node uses the default value. Your "and/or" does not choose between these.

## 4. What would falsify each point

| point | falsified if |
|---|---|
| 1 (inherited) | With both of site 0's inputs verifiably wired, some later site still reads ExecState 0 after its own branch, and deleting that site's CLFN and constant brings ExecState back to 1 (a per-site type rejection). |
| 1 (t6 matters) | ExecState stays 0 after the constant goes on t6 and turns 1 only after the t8 branch. That would mean t8 alone is what breaks it. |
| 2 | Re-finding by uid shows CLFN0 at N[73] with t6 unwired. That would mean the constant op itself missed. |
| 3 | Already falsified by the run 1 / run 2 site-0 comparison above. |

## 5. Cheapest discriminating test (inside the planned third run, no extra LabVIEW time)

1. Purge immediately after `move_in`, then call `find_node`, so no junk node exists while an index is being used.
2. Replace `node_terms` with `node_terms_uid` and require the returned node uid to equal the CLFN's uid. An out-of-range index then fails loudly instead of reading as "unwired".
3. Read ExecState once after the constant is on t6 and before the branch. This separates t6 from t8.
4. After each branch, check which node the new sink on the site wire belongs to: its owner uid must equal the CLFN's uid, not just "sinks went up by 1". `connect_from_wire` creates its own junk Invoke (`r2:108`). If that Invoke is created before the op looks up Nodes[n] and it sorts ahead of the CLFN, the op wires the site wire into a different node. That would be an original node, which is a rule-1a hazard. "Sinks +1" and "Is Broken? False" would both still pass, so neither check catches it.
5. On the first site that reads ExecState 0, delete that site's CLFN and constant by uid and read ExecState again. This separates "inherited" from "this site's own type".

## 6. Is "re-find after every purge" enough for all eight While-body sites to end at ExecState 1?

**Not with confidence.** It fixes the out-of-range read at sites 0 and 11, and that is the only index hazard your run actually hit. Two gaps remain:

- **Index hazard:** the stale-index risk inside the connect op (step 5.4 above).
- **Not an index issue:** whether Adapt to Type accepts the wire types at sites 8–20 has never been shown.

Without steps 5.2, 5.4 and 5.5, a third run could end at ExecState 0 again and not tell you why.

Sources:
- [NI forum: Call Library Function – Adapt / Interface to Data breaking](https://forums.ni.com/t5/LabVIEW/Call-Library-Function-Adapt-Interface-to-Data-Breaking/td-p/3832312?profile.language=en)
- [LabVIEW Wiki: AbstractDiagram Firing Order](https://labviewwiki.org/wiki/AbstractDiagram_class/Firing_Order_property). I found no NI document that guarantees any Nodes[] order; the evidence for that is the two runs above.

## Sources

(extract from answer)

## What was done with it

Read by the card 90-6 material session (fable/low) at 05:21, AFTER its failure budget (2 LabVIEW runs) was spent - so
NO third run was launched; the script was patched for the next session and the rest is recorded for judgement.
- §1 accepted: Nodes[] order is not controlled by position (site 0: Invoke N[74] in run 1 vs N[73] in run 2, same uids,
  same target); my "run 1 was lucky" is withdrawn -> "any Nodes[] index can go stale after any edit".
- §2 accepted: N[74]/N[24] were OUT OF RANGE after the purge (`gscript.node_terms` returns empty rows -> w6 = 0), so gate
  S.3 conflated "unwired" with "no such node". Applied to `tools/bench/diag_c90_t0_step3b.py`: (5.1) the purge now runs
  right after `move_in` and `find_node` runs after it, so no junk exists while an index is used; a re-find by uid after
  the post-const purge and after the post-branch purge; (5.3) one ExecState read after the constant and before the branch.
- NOT applied (gate/route changes, judgement): (5.2) `node_terms_uid` with a uid-equality gate; (5.4) after each branch,
  the new sink's owner uid must equal the CLFN uid (rule-1a hazard: the connect op's own junk Invoke could shift Nodes[n]
  INSIDE the op and wire the site wire into an original node - "sinks +1" does not catch it); (5.5) on the first ExecState
  0, delete that site's CLFN + constant by uid and re-read.
- §3 recorded: Adapt-to-Type acceptance is shown only for w3268 and w5859 (run 1, ExecState 1 after sites 0/2); sites 8,
  10-13, 20 remain unshown, and "t8 alone breaks a bare CLFN" (I32 `site` uses its default) is the narrower reading.
