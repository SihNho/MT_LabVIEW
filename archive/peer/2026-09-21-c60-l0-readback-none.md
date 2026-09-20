# c60-l0-readback-none

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $4.3505  in 30 / out 38562 / cache-create 240740 / cache-read 1787107  (503s, 25 turn(s))
- **date:** 2026-09-21 03:03:19
- **outcome:** ANSWERED (504s)
- **why asked:** `guard_peer` owed a hypothesis review for the two FAILED gates of cycle 60 attempt 1's L0 run (`L0_b5 bound None`, `L0_b6 None vs 'index'`). The claim put up for attack was that both are a READER defect in `read_back()` — an owner-class test that only fires on literal `'Diagram'` — and that widening it to `('Diagram','TopLevelDiagram')` is "the whole repair".
- **verdict:** unverified

## Question

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


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled in this session, which matches the brief — so the review is the answer itself, below. No build, no edit, no LabVIEW lock was taken.

---

# The claim is wrong where it matters, and this project's own files already prove it

## 1. The strongest reason the claim is wrong

The claim's operative half — *"widening that test to `('Diagram','TopLevelDiagram')` is the whole repair, and the gate should then read the binding off the machine"* — is **falsified by a measurement already on disk**, dated 2026-09-14.

`gscript.node_labels()` reads `Node.Label` 6359001 → `Text.Text`, i.e. **the node's own label** (`tools/gscript.py:588-594`). For a `Local`, that is not the bound control's name. Join two files that are already saved:

- `tools/bench/state_carriers.json:2-82` lists the main VI's eight `Local`s: uid **2991** (diagram 1), **4277** (17), **11574** (73), **2143 / 3097 / 3160** (83), **16942** (99), **25805** (167).
- `tools/bench/main_vi_node_labels.json` — the `OpNodeLabels_v0` sweep of that same VI (`:2`) — returns, for every one of those uids, the label **`"Min_Track N beads V6_ParallelLoop.vi"`**: `:7-8`, `:350-351`, `:1473-1474`, `:1569-1570`, `:1577-1578`, `:1585-1586`, `:1976-1977`, `:2742-2743`. The two `Global`s on the same diagram 83 return **`"Global motor pos.vi"`** (`:1581-1582`) — the same pattern, the variable's source VI, never the control.

The diagram keys cross-check against `state_carriers.json` exactly (2991 under `"1"`; 2143/3097/3160 under `"83"`), so the join is sound and it is the same uid space, the same lineage `D1_s3a_focus_ind.vi` descends from.

**Eight of eight genuinely-bound Locals: `node_labels` answers with a FILE NAME.** So widen the class test, re-run, and `bound_label` becomes `'SCRATCH_L0_20260921_….vi'`. `L0_b5` flips to PASS — it only requires `is not None` — and **`L0_b6`, the actual L0 pass criterion, fails a second time**: 31 pass / 1 fail instead of 30 / 2, same gate, next cycle. That is precisely the `repeated-failure-class` shape the runner's firefighter rule exists to catch, bought with a whole cycle.

The error that produced the claim is visible in the script's own words. `diag_s3b_l0_createlocal.py:65-66` asserts *"an implicit node's LABEL IS the bound control's name, gscript.py:589-592"*. What `gscript.py:590-592` actually says is that an implicit **property node's** header is its label — verified 88/88 on the main VI's implicit `Value` nodes (`docs/main-vi-panel-map.md:563`, `docs/toolkit-capabilities.md:26`). "Implicit property node" silently became "implicit node". That is inference over measurement — the same fault the claim accuses run 1 of.

And the script knew. `:66-68` states in writing: *"A G-SIDE readback of the bound name would need `Local.Control Name` 6355400 … so the readback is taken with the fleet's existing readers. **Stated as a deviation from 49(d) AS WRITTEN.**"* 49(d) (`docs/cycle27-plan.md:2019-2021`) specifies the readback as uid, class and **bound name**. The run knowingly substituted an instrument that cannot answer its own pass criterion, and the claim proposes to repair the substitute.

## 2. An alternative explanation that fits the same log

Not *"the reader was never called"* but **"the fleet has no reader for a Local's binding at all, so the run never had an instrument for `L0_b6`."**

Under this reading the two FAILs are a correct report of an **absent measurement**, and the machine is probably fine — but nobody has shown it, and the claim's "widen and read it off the machine" does not show it either. The positive evidence that the Local is bound is: the Invoke's `reference` terminal carries wire 193 branched from the same `element` source whose `Control.Label → Text.Text` read `'index'` off the machine (log `:39`, `:62`); the op compiled at `ExecState 1` (`:42`) and ran with `(False, 0, '')`. The wiki and the NI forum thread both say `Create:Local Variable` binds to the control it is invoked on. So the likely truth is: local created, bound to `'index'`, **unreadable by any verb the fleet owns**.

Two things that look like symptoms and are not, so they are not spent again:

- **Birth on `TopLevelDiagram #536` is normal here.** `docs/toolkit-capabilities.md:275` records scripted `ControlTerminal`s as *"BORN owned by `'TopLevelDiagram'` #536"* and then relocated. It says nothing about binding.
- **`ExecState 1 → 0` does not discriminate.** Bound-but-unwired and unbound both break the VI. `docs/cycle27-plan.md:2044` wrote the warning in advance — *"MEASURE, DO NOT ASSUME, whether an unwired Local leaves the VI legal"* — and 0 is the outcome that entry anticipated.

## 3. The observation that would falsify the claim outright

`node_labels` returning anything other than the bound control's name for a Local that is known to be bound. **That observation already exists**, for 8 of 8, in the files cited in §1. Conversely the claim would have survived had those rows read `'Focus position'` or similar; they read a `.vi` file name.

## 4. The cheapest discriminating test

**Zero mutation, zero construction, one op call on a file already saved:**

`g.node_labels(D1_s3a_focus_ind.vi, <index of a diagram holding a pre-existing Local>)`, then read the row for that Local's uid. Resolve the index **by uid** via `diag_index`, not by reusing 83 — S2/S3a mutations shift Traverse indices (the script's own risk (iv)). A control name ⇒ the claim survives. A file name or `''` ⇒ the claim is dead and `node_labels` is the wrong instrument for `L0_b6` whatever the class test says.

Then the test that actually answers the pass criterion — the one 49(d) asked for, and that CLAUDE.md's *"when a diagnosis is GUESSED twice, build the READER"* rule now mandates: a one-property reader op for **`Local.Control Name` 6355400**, the same shape as `OpNodeLabels_v0` (Traverse `Local` by index → property → string indicator). Run 1 already measured that the creator accepts that class + ID (`L0_d1 resolves=True`, error `''` — log `:115`). Note what that exposes: **"ROUTE B, report only" was a category error.** Route B is *create by `New VI Object` style 2061 **plus a write to** `Control Name`*. **Reading** `Control Name` is not Route B and was never fenced by 49(d). That misclassification is the reason the run shipped without an instrument for its own gate, and it is a bigger finding than the class string.

---

## The three other readings

**(a) The two `Create Local` terminals — the measurement does not settle this, and it should not be scored as if it did.** Two things weigh against "an input parameter the wiki omitted": LabVIEW names an invoke node's *parameter* terminals after the parameter and its *return-value* terminal after the method, and the wiki's table for 6331C02 carries exactly one row — `Create:Local Variable`, Local Refnum, return value (the page does self-declare the table incomplete). Both machine terminals carry the **method's** name, not a parameter name, and the node's other two rows are in/out pairs (`reference`/`reference out`, `error in (no error)`/`error out`), so a third in/out pair for the method row is the more economical reading. **Cheapest separator, no build:** dump `node_terms_uid` for an invoke node the fleet has *already* built with a method of known signature (e.g. the Move method behind `move_in`, or `build_opconpaneassign`'s). If a parameter-taking method names its terminals after its parameters while value-returning ones show a duplicated method-name pair, terminal 4 is layout, not a parameter. There is no such table in `tools/bench/` today — this run's is the only invoke terminal table on disk, which is itself why the question is open.

**(b) The `ExecState` attribution is sound about *which* and unsound about *why*.** The Local was the only mutation, so it broke the VI; but "the unwired Local" names one of at least two causes the run cannot separate (unwired write-mode local vs unbound local), and the plan itself flagged the first as expected. The second call adding a second unwired local and leaving it 0 is equally consistent with both.

**(c) A delta of 0 across the 20 calls establishes nothing, and `L0_c2`/`L0_c3` as written cannot fail.** From the same log: **34167** → **30687** after the pre-batch restart → **51418** before the 20 calls → **34761** at the end (`:4`, `:16`, `:109`, `:125`). The metric moved **+20,731 then −16,657 inside one 106-second run** against a **±100** tolerance — roughly 170× coarser than its own in-run noise. The bracket is **1.6 s wide** (`:108`), and `ref_counts` is byte-identical either side (`opened 12 / closed 12 / live 0`, `:109`), i.e. **no reference was opened during the window at all**, so "opened == closed, 0 live" is vacuously true there; and it counts the Python wrapper's opens, not the op VI's internal `Open VI Reference`/Traverse refs, which is exactly where 44(e)/49(j)'s 24–33 k lives. A real hygiene measurement needs a bracket wide enough to contain the growth and a **positive control** — a run known to leak that this gate actually flags.

**Minor, but it undoes the word "whole":** the same literal `'Diagram'` comparison survives at `tools/bench/diag_s3b_l0_createlocal.py:608` in `relocate_if_needed` (`if rb.get("owner") == ("Diagram", dest_uid)`), which is why CALL 1 executed a pointless `move_in` of a Local that was already on its destination (log `:75`). The patch at `:573-574` fixed one of two sites.

---

**What would change my mind:** a reading of `node_labels` on a known-bound Local in this lineage that returns the control's name rather than the VI's file name. The eight rows cited above are the evidence against it; if they were produced by a sweep that skipped or mislabelled Locals, show that and the refutation collapses.

Sources: [Control class/Create.Local Variable method — LabVIEW Wiki](https://labviewwiki.org/wiki/Control_class/Create.Local_Variable_method) · [Local class — LabVIEW Wiki](https://labviewwiki.org/wiki/Local_class) (`Control Name` 6355400 read/write; `Control` 6355403; `Label` 6355402) · [VI Server Class Hierarchy — LabVIEW Wiki](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy) (`Local` ClassID 16398 descends from `Node` → `GObject`, so it does appear in `Diagram.Nodes[]` — the reader reaches it and still cannot answer) · [create local variable using labview scripting — NI Community](https://forums.ni.com/t5/LabVIEW/create-local-variable-using-labview-scripting/td-p/2616645)

## Sources

(extract from answer)

## What was done with it

Disposed by the cycle-60 (attempt 2) judgement session, 2026-09-21. This is one of the few reviews whose
load-bearing half is **ACCEPTED AND ACTED ON IN THE SAME CYCLE**; the parts that are not acted on are named
with the reason, as 41(b) requires.

**ACCEPTED, AND IT CHANGED THIS CYCLE'S BUILD.** The refutation is correct and is settled by evidence already on
disk, not by argument: `node_labels()` reads `Node.Label` 6359001 → the node's OWN label (`tools/gscript.py:588-594`),
and all eight of the main VI's pre-existing `Local` objects return the VI's FILE NAME there
(`tools/bench/main_vi_node_labels.json`, the eight uid rows this review cites). So `L0_b5`/`L0_b6` report an
**ABSENT INSTRUMENT**, not a failed binding, and the proposed widening to `('Diagram','TopLevelDiagram')` would
have produced 31 pass / 1 fail — the `repeated-failure-class` shape — while measuring nothing new. The whole of
cycle 60's remaining work was re-aimed on this: the deliverable became the **reader**, `claudeDev\OpLocalName_v0.vi`
(Traverse `Local` by index → `Local.Control Name` **6355400** → string), which is this review's §5 route taken as a
READER only. CLAUDE.md's "when a diagnosis is GUESSED twice, build the reader" is the standing rule it satisfies.

**ACCEPTED — the category correction.** "Reading `Control Name` is not Route B" is right, and the judgement session
so rules: 49(d) fences route B as a *creation* mechanism (`New VI Object` style 2061 **plus a write** to
`Control Name`). A read of that property to verify route A's product is a different act and was never fenced.
Run 1's own `L0_d1 resolves=True, error ''` (log `:115`) is the measurement that makes it buildable today.

**ACCEPTED AS FACT, BUT THE CONSEQUENCE IS NOT THIS REVIEW'S.** "Bound-but-unwired and unbound both break the VI"
is correct and it means `ExecState` 0 does not discriminate. The decision it forces — **49(e)'s M1 folds into M2**,
because one unwired Local on this very VI lineage took the scratch from `ExecState` 1 to 0 — rests on that
measurement, which 49(e) demanded in advance, not on the review. Recorded as Pre-decided **50(c)**.

**ACTED ON.** The residual literal-`'Diagram'` comparison at `tools/bench/diag_s3b_l0_createlocal.py:608`
(`relocate_if_needed`, the pointless `move_in` at log `:75`) is NOT patched — run 1's file is a finished record and
editing it would rewrite evidence. Instead the rule is carried forward into the next diagnostic by brief: owner
comparisons accept **both** `'Diagram'` and `'TopLevelDiagram'`, and every diagram index is resolved **by uid via
`diag_index`**, never by reusing a number. (The review flags that second point as its own inference; it is adopted
because it is cheap and independently correct, not on the review's authority.)

**IMPLEMENTED AS A READING, NOT A CONCLUSION.** The six-terminal question — whether `i=4`/`i=5`, both named
`'Create Local'`, are an in/out pair of the method row rather than an omitted input — is left **UNSETTLED**, exactly
as the review says it must be. Its separator is implemented as a report-only step (`R4`): dump `node_terms_uid` for
an Invoke node this fleet has already built with a method of known signature and print the tables side by side. No
conclusion is drawn from it this cycle, and 49(d)'s rider stands — if 6331C02 takes parameters, that is a
measurement, never a failure.

**NOT ACTED ON, WITH THE REASON.** The named "cheapest discriminating test" (run `node_labels` on a diagram holding
a pre-existing Local and read that row) is **not run**: its answer is already on disk in the very file the review
cites, and the new reader is validated against those same eight Locals, which is a strictly stronger test of the
same question. Nothing in `tools/gscript.py`, `OpNodeLabels_v0` or run 1's artefacts was modified on this review's
say-so; `claudeDev\OpCreateLocal_v0.vi` (md5 `58275b21…`) **stands as built** — it creates reliably (20/20, handles
flat, refs 12/12/0 live) and only its readback was wrong, so the readback moved out into the new op rather than the
creator being rebuilt. 49(i)'s promise — "the op will be revised on any review that gates it" — is what this is.
