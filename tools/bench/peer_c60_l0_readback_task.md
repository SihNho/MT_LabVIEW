ATTACK the claim below. It is the explanation formed under pressure for two FAILED gates in
`tools/bench/diag_s3b_l0_createlocal.log` (run 1, `BGRUN END rc=1 after 106s`, 30 pass / 2 fail). Your job is
to find the strongest reason it is WRONG, to name an alternative explanation, to say what would falsify it, and
to name the CHEAPEST discriminating test. Do not confirm it.

Files you may read (read-only): `tools/bench/diag_s3b_l0_createlocal.log`, `tools/bench/diag_s3b_l0_createlocal.py`
(the diagnostic itself; the function at issue is `read_back()`), `tools/bench/diag_s3b_l0_createlocal.json`,
`tools/gscript.py` (`node_labels` :587, `report_all` :488, `build_invoke` :2159), `tools/recipes/build_d1_v0.py`
(`owner_of` :338, `diag_index` :357), `docs/cycle27-plan.md` Pre-decided 49.

== THE TWO FAILING GATES, VERBATIM FROM THE LOG
  FAIL  L0_b5 the new Local's class, owner and bound label were READ off the machine  class 'Local' owner ('TopLevelDiagram', 536) bound None
  FAIL  L0_b6 the bound label equals the label asked for  *** THE L0 PASS CRITERION (49(e)) ***  None vs 'index'

== THE CLAIM UNDER ATTACK
"Both failures are a defect in the READER, not a fact about the machine. `read_back()` resolves a Traverse
diagram index only when `owner_of` answers the literal class string `'Diagram'`; the new Local was born owned by
`'TopLevelDiagram'` #536, so the `else` branch left the index None, `gscript.node_labels()` was NEVER CALLED,
and `bound_label` stayed None by construction. The machine was never asked whether the Local is bound to
`'index'`. Widening that test to `('Diagram', 'TopLevelDiagram')` - `diag_index(#536)` is measured to resolve to
0 (cycle 58's gate B1_A2) - is the whole repair, and the gate should then read the binding off the machine."

== ALREADY RULED OUT (do not spend your answer on these)
1. "The op never ran / the local was never created": the op's own `Text` indicator read `'index'` OFF THE
   MACHINE (the label it walked to), the error cluster read `(False, 0, '')`, the whole-VI `Local` uid census
   went 8 -> 9 with NEW uid [23507], and 20/20 later consecutive calls each added exactly one more Local.
2. "The uid is wrong": `report_all(target,'Local')` returns the row for #23507 with class `'Local'`, and
   `owner_of(#23507)` echoes its own uid back under the strict identity guard.
3. "No diagram index exists for the top level": cycle 58's gate `B1_A2 diag_index(#536) resolves to 0` passed
   on this same VI lineage.

== THE THREE OTHER READINGS FROM THE SAME RUN - attack these too if they are weaker than they look
(a) 49(d)'s RIDER. The wiki says `Control -> Create:Local Variable` 6331C02 "takes NO input parameters and
    returns only a Local refnum" (page self-declares its parameter table incomplete). The Invoke node this run
    created carries SIX terminals, read off the machine:
      [(0,'reference',sink), (1,'reference out',SOURCE), (2,'error in (no error)',sink),
       (3,'error out',SOURCE), (4,'Create Local',sink), (5,'Create Local',SOURCE)]
    Both extra terminals were left UNWIRED and the call still created a correctly-classed Local. Is the sink
    terminal at index 4 an INPUT PARAMETER the wiki omitted, or an artefact of how the erdosmiller creator
    lays out a method node? What reading would separate those two?
(b) The self-test VI's `ExecState` went 1 -> 0 after ONE unwired Local was created (and stayed 0 after a
    second). The run attributes that to the unwired Local, the only mutation made. Is that attribution sound?
(c) 20 consecutive calls left the LabVIEW handle count at 51418 -> 51418 (delta 0) with `ref_counts` reading
    opened 12 / closed 12 / live 0. Given that Pre-decided 44(e)/49(j) measured ~24-33k UNEXPLAINED handle
    growth per scripting run on this machine with the same client-side counter reading 0 live, does a delta of
    0 across 20 calls actually establish reference hygiene, or is the metric blind here?

== WHAT A USEFUL ANSWER LOOKS LIKE
The strongest reason the claim is wrong; one alternative explanation that fits the same log; the reading that
would falsify the claim outright; and the single cheapest discriminating test. Nothing is to be rebuilt or
re-run on your side - you are read-only.
