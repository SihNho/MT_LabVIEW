# c55-sinkrule-no-bare-input

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.5444  in 34 / out 36714 / cache-create 139149 / cache-read 2026039  (507s, 32 turn(s))
- **date:** 2026-09-20 08:29:41
- **outcome:** ANSWERED (510s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK the explanation below. It is a diagnosis formed under pressure after a failed prediction, and your job
is to find the strongest reason it is WRONG, not to agree with it.

CONTEXT (LabVIEW VI Scripting over COM, a Python "op" fleet driving built LabVIEW op VIs).

The run: tools/bench/diag_queue_typetest_control.py, log tools/bench/diag_queue_typetest_control.log,
readings tools/bench/diag_queue_typetest_control.json. `BGRUN END rc=1 after 78s`, 9 gates pass / 2 fail.
The failing lines:
  FAIL  G3 TWO bare named input terminals were resolved by the FIXED rule  matched=None mismatched=None
  FAIL  G2 both legs' source and sink share ONE diagram, uid 686 (Traverse index 19)  2 of 4 ends resolved

WHAT THE RUN WAS FOR. We cannot read a terminal's data type with any op we have. So we wanted to test types BY
CONNECTION: wire a numeric source into a numeric input (MATCHED) and a refnum source into a numeric input
(MISMATCHED), and read the property `Wire.Is Broken?` (6371004) on each resulting wire. If the mismatched wire
reads broken, LabVIEW's type propagation is a usable type checker for us. The run never got that far.

WHAT WAS MEASURED (all of it is in the log):
  * The scratch is a dated byte-identical copy of claudeDev\D1_s2_loops.vi; ExecState 1 before anything.
  * The live walk of Diagram #686 returned 24 nodes. Both SOURCES resolved:
      #8486 'Increment', Nodes[0], terminal 0 named 'x+1', is_source, already carrying wire 23519
      #250  'Property Node', Nodes[3], terminal 1 named 'IMAQdx Session', is_source, carrying wire 6910
  * owner_of read ('Diagram', 686) for #250, #7201, #8486, #9179, #25091, #25149 - every node involved.
  * The SINK rule was fixed in advance: take bare named INPUT terminals, in the order
    #7201, #8486, #9179, #25091, #25149, where "bare" = is_source False AND a non-empty name AND wire == 0.
    Measured result, node by node:
      #7201 'Multiply'  Nodes[1]  - 0 bare named inputs
      #8486 'Increment' Nodes[0]  - 0 bare named inputs
      #9179 'Decrement' Nodes[14] - 0 bare named inputs
      #25091 'Multiply' Nodes[19] - 0 bare named inputs
      #25149 'Subtract' Nodes[20] - 0 bare named inputs
  * An independent on-disk census of the ORIGINAL VI (tools/bench/main_vi_nodeterms.json, lines 6256-6295)
    shows #7201's terminals as: t0 'x*y' is_source true wire 8424; t1 'y' is_source false wire 8385;
    t2 'x' is_source false wire 8518. So its inputs ARE named, and both already carry wires.

THE EXPLANATION I FORMED, WHICH YOU MUST ATTACK:
  "The arithmetic nodes named by the fixed rule are live nodes inside a working VI, so every one of their input
   terminals is already wired. Therefore the fixed sink rule has no candidate on this target, the control pair
   could not be attempted, and the correct response is (1) to dump the full terminal census of Diagram #686 as
   pure measurement and (2) to leave the choice of a different sink to a later decision - NOT to pick a
   different sink now, and NOT to wire onto an already-wired input, because a second source on one terminal
   makes a wire broken for a reason that has nothing to do with type and would destroy the control."

SPECIFICALLY, TELL ME:
  1. The strongest reason that explanation is wrong or incomplete. In particular: is "0 bare named input
     terminals" really what was measured, or could the search itself be defective - e.g. is `wire == 0` the
     correct emptiness test for a LabVIEW terminal reference read over this path, could a terminal legitimately
     report a non-zero wire uid while still being connectable, or could `is_source` be unreliable here?
  2. An alternative explanation for the same observation.
  3. Whether the premise "wiring a second source onto an already-wired input terminal produces a broken wire
     for a non-type reason" is actually true in LabVIEW. Does `Terminal.Connect Wire` on an occupied INPUT
     terminal replace the existing wire, add a second source, or fail? Cite LabVIEW/NI documentation if you
     can. If it REPLACES, then the whole "no candidate" conclusion is wrong and the run could have proceeded.
  4. Whether a type-mismatch test needs a BARE terminal at all - is there a cheaper construction that exhibits
     a type mismatch and whose `Is Broken?` we could read, without depending on finding an unwired input?
  5. The cheapest discriminating test between your alternative and mine.

ALREADY RULED OUT (do not re-propose these):
  * Building a new op or a type reader. Forbidden by a standing project rule; no new ops this cycle.
  * Creating queue nodes first. The instrument under test (`Is Broken?`) must be validated before the subject.
  * Using a GUI click anywhere. The rig is assembled; scripted GUI is not authorised for this run.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write access is correctly denied for this role, so the review is below in full.

---

# 1. The single strongest reason the explanation is WRONG

**The reading the run was chasing is not owed. Your own active files already answer it — and one of them is the docstring of the connect op the run was using.**

- `tools/gscript.py:2412` (`OpConnect_v0`, measured **2026-09-06**): *"Semantics verified on a fresh Index Array: an already-wired source is BRANCHED (wire count unchanged, ExecState 0→1); an already-wired SINK is not safe (LabVIEW re-routes and the VI breaks) — wire only unwired sinks. **Type mismatches make a broken wire.**"*
- `docs/NAMES.md:875-879` (measured **2026-09-15**): *"LabVIEW joins type-incompatible terminals and draws a broken wire, whose uid still reads identically at both ends… ExecState 1 → 0."*
- `docs/NAMES.md:908-909` (measured **2026-09-17**): `Is Broken?` read **False on a good wire** and **True on a broken wire**.

A prior-art peer quoted the first sentence three days ago — `archive/peer/2026-09-17-priorart-d1-op-stopfromnode.md:304` — and the "already-wired SINK is not safe" line has been cited at least five times across `archive/peer/` and `tools/recipes/build_opownerchain_v1.py:37`. So "the instrument under test must be validated before the subject" (the premise that excluded queue nodes under 40(d)) rests on a validation the project already holds. The genuinely open residue is narrow and is **about the reader, not about types**: whether the `Is Broken?` readout ordering behaves on a type-mismatched wire as it did on a two-source one. Your explanation does not name that residue; it says "the run never got that far", which reads as though the whole reading is still outstanding. It is not.

**Second strike, independent of prior art: the observation was derivable before LabVIEW was opened, from a number the same log printed four lines earlier.** `diag_queue_typetest_control.log:15` records `ExecState [before the pair] = 1`. A VI whose run arrow is not broken has no unwired *required* input — NI states the broken arrow "generally mean[s] that a required input is not wired, or a wire is broken" — and `Multiply`, `Increment`, `Decrement`, `Subtract` expose **only** required inputs. So "zero bare named inputs on those five nodes" is *entailed* by `ExecState == 1`. It is a contradiction inside the fixed rule, not a property of this target. The repair's docstring (`diag_queue_typetest_control.py:66-67`) calls it "a fact about the TARGET" — that relabels a design error as a discovery, and it is the part of the explanation a peer should refuse.

**Third: the rule's success case was also a failure case.** In a non-broken VI the only bare named inputs that *can* exist are optional or variadic ones — shift registers ("both sides come back unwired", `docs/toolkit-capabilities.md:53`), structure tunnels, Build Array, Bundle. Those are exactly the terminals that **adapt** to whatever is wired, so they cannot exhibit a type mismatch. Had the fixed rule found its two candidates, the MISMATCHED leg would plausibly have read `False`, and the run would have concluded "LabVIEW type propagation is not a usable type checker for us" — a false negative, recorded as a first-class reading. The rule was under-specified in both directions: it never required the sink to be **type-constrained**.

---

# 2. Answers to the specific questions

**Q1 — is "0 bare named input terminals" really what was measured?** Yes, the search is sound, and the doubts in the brief are the wrong doubts:

- `wire == 0` **is** the documented emptiness test on this path — `gscript.py:874`: *"`wire` = connected wire UID, 0 when bare (then conn_err/wire_err carry 1055…)"*. And note the direction of error: a *failed* `Connected Wire` read would yield `wire = 0`, i.e. a **spurious extra** candidate, not the observed famine. A defective read cannot explain this failure.
- `is_source` is documented at `gscript.py:873` and was verified "on primitives and on NI's example globals" (`docs/toolkit-capabilities.md:23`). The one known `is_source` trap is structure tunnels on a body diagram (`NAMES.md:930-933`) — irrelevant to five arithmetic primitives.
- Terminal names are real: `main_vi_nodeterms.json:6256-6295` shows `'x'`/`'y'`/`'x*y'`.

But two things *are* defective, and neither is in your list:

- **The log recorded a count, not a census.** `diag_queue_typetest_control.log:39-43` prints `0 bare named input terminal(s) []` per node and no `(name, is_source, wire)` triples. The corroboration you cite is from the **ORIGINAL** VI while the target is `D1_s2_loops.vi`. The claim "their inputs are all already carrying wires" is therefore inferred, and CLAUDE.md calls that `inference-over-measurement`. (The repair adds the census — correctly.)
- **"24 nodes" is itself truncatable and was not cross-checked.** `walk()` stops at the first node index whose uid reads 0 (`build_opstopfromnode_v0.py:133-135`), so a single failed `node_terms` mid-array silently shortens the diagram. `walk` already fetches `node_labels` at `:130`; comparing `len(labels)` with `len(out)` costs zero extra COM calls and was available in run 1.

**Q2 — alternative explanation of the same evidence.** Not "the target has no bare inputs" but: **the fixed rule was logically incapable of succeeding on any non-broken VI, and the five candidates were selected for arithmetic convenience rather than for the property the experiment needed (a bare, *type-constrained* sink).** Same observation, different locus — plan, not target. This alternative also predicts something yours does not: the full census of Diagram #686 will return bare inputs only on variadic/adapting nodes, and zero bare inputs on any fixed-arity primitive.

**Q3 — is "a second source on an occupied input breaks the wire for a non-type reason" true?** **No — that mechanism is not what was measured, and the real one is already in your toolkit.** `gscript.py:2411`: *"an already-wired SINK is not safe (LabVIEW re-routes and the VI breaks)"* — LabVIEW **re-routes**, it does not quietly attach a second driver. External corroboration that scripting onto an occupied terminal is not a benign operation: in the NI thread *"Script connect existing loose wires to case tunnels"* an attempt to `Connect Wire` onto a tunnel terminal that already had a wire produced an error, and NI's Darren prescribed reading `Joints[]`, **deleting the existing wire**, and re-creating it with `Create Described Wire`. Neither NI's docs nor the LabVIEW Wiki pages for `Terminal.Connect Wire` (6349C03) or `Node.Connect Wires` state the occupied-terminal behaviour at all, so the honest position is: **replacement is not documented, your own measurement says "re-routes and the VI breaks", and the forum says "error"** — the prohibition survives, its stated reason does not. So your conclusion is right by accident, and it was not a judgement that needed making: it is a five-times-cited toolkit fact. (Also note the asymmetry the rule never justified: the run happily used *already-wired* terminals as **sources** — `#8486` carrying wire 23519, `#250` carrying 6910 — because branching a source is safe, `gscript.py:2411` again.)

**Q4 — does a type-mismatch test need a BARE terminal at all?** It needs one, and **it never needed to *find* one — it could have *made* one with ops that already exist.** No new op, no queue node, no GUI:

- `gscript.build_index_array` (`:2322-2329`) — *"the node arrives UNWIRED; wire its `array` input afterwards with `connect_terminals()`"*. Its `index` input is strictly numeric, so refnum→index is a clean mismatch and numeric→index a clean match, **on the same node**, which is what the brief said it preferred.
- `gscript.drop_subvi` (`:1225`) and `gscript.build_property` (`:2194`) both take a `diagram_index`, so a bare, strictly-typed sink can be manufactured **on Diagram #686 itself**, keeping `OpConnectNested_v1` (5/5 in cycle 54) as the writer.

Your own script lists "a freshly created arithmetic node" among the deferred options (`diag_queue_typetest_control.py:456`). Deferring the *choice* to judgement is defensible under Pre-decided 40. Saying the pair **"could not be attempted"** is not — it was not attempted.

And a sharper point: **`Is Broken?` is the noisier of the two instruments available.** `NAMES.md:912-921` records that reading it *perturbs the target* — an idempotent connect on a VI whose ExecState was 1 left it reading 0 — and the mechanism is explicitly "OPEN". Meanwhile `connect_terminals` returns `(wire delta, ExecState)` directly (`gscript.py:2431`), and `NAMES.md:879` already used `ExecState 1 → 0` as the type-mismatch detector. One wire at a time on a scratch makes ExecState fully localising. The experiment was built around the reader that its own documentation says corrupts the state it would be checked against.

**Q5 — cheapest discriminating test.** One run, ~4 op calls, a dated scratch, no new op, no queue node, no GUI:

1. `build_index_array(scratch, loc)` → `node_terms` on the new node, printing every triple. **Discriminates immediately**: if its inputs are bare and named, "no candidate on this target" was never about the target.
2. `connect_terminals(numeric source → 'index')`, record `(wire delta, ExecState)`.
3. `build_index_array` again; `connect_terminals(refnum source → 'index')`, record the same.
4. Optional, and only now: the idempotent re-connect for `Is Broken?` on each leg, so the reader's ordering is checked *against* an ExecState result already in hand.

Predicted under my reading: step 1 yields bare named inputs; matched stays `ExecState 1`; mismatched goes `1 → 0`. Under yours, step 1 is where you find out — if a freshly created node's inputs also read non-bare, my account is dead and the emptiness test is the culprit after all.

**Falsifier for my reading:** a freshly created node whose inputs do not read bare on this path, or a demonstration that `Wire.Is Broken?` distinguishes type-mismatch brokenness from two-source brokenness.

---

# 3. What the log records and the explanation does not report

Handles went **30,678 after the restart → 63,416** at the end of a 78-second run (`diag_queue_typetest_control.log:10,59`), while gate G10 passed on the Python-side count (6 opened / 6 closed). Against CLAUDE.md's "20 runs leave the handle count flat (±100)" that is a failure of the reference-hygiene rule, measured inside the run that had to restart LabVIEW *because of* the same growth at cycle 54's close (`:9`). G10 measures the client's refs, not LabVIEW's handles, and reported "no live reference" while the handle count doubled. CLAUDE.md's staged-build rule makes this a precondition, not an afterthought — it belongs in the reading.

Sources: [Terminal class — LabVIEW Wiki](https://labviewwiki.org/wiki/Terminal_class) · [Terminal class/Connect Wire method](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method) · [Node class/Connect Wires method](https://labviewwiki.org/wiki/Node_class/Connect_Wires_method) · [Script connect existing loose wires to case tunnels — NI forums](https://forums.ni.com/t5/LabVIEW/Script-connect-existing-loose-wires-to-case-tunnels/td-p/4195933) · [Debugging and Handling Errors — NI](https://www.ni.com/academic/students/learn-labview/debugging/) · [VI class/Execution.State property — LabVIEW Wiki](https://labviewwiki.org/wiki/VI_class/Execution.State_property) · [Using Wires to Link Block Diagram Objects — NI](https://www.ni.com/docs/en-TT/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

## Sources

(extract from answer)

## What was done with it

**RECORDED, NOT ACCEPTED AND NOT REJECTED — by a MATERIAL session, under `docs/cycle27-plan.md` Pre-decided
41(b)** ("Any peer review you are FORCED to dispatch is RECORDED, never accepted or rejected… Do not act on
them: do not redesign a gate, do not rebuild a measurement, do not re-run on the strength of one. The judgement
session disposes it."). This review was forced by `guard_peer` on `tools/bench/diag_queue_typetest_control.log`
(run 1, `BGRUN END rc=1 after 78s`, first failing line `FAIL  G3 …`). **Nothing in it was acted on**, and the
cycle-55 material brief explicitly reserved the branch after this measurement for judgement.

Its findings, recorded verbatim in substance so judgement can dispose them without re-reading the file:

1. **It says the reading was not owed at all** — `tools/gscript.py:2412` (measured 2026-09-06) already records
   *"an already-wired source is BRANCHED … an already-wired SINK is not safe … **Type mismatches make a broken
   wire**"*, and `docs/NAMES.md:875-879` + `:908-909` already record broken-on-mismatch and `Is Broken?`
   False/True. It calls the genuinely open residue narrow: whether the readout's ORDERING behaves on a
   type-mismatched wire as it did on a two-source one.
2. **It says "0 bare named inputs" was ENTAILED by `ExecState == 1`**, printed four lines earlier in the same
   log (`:15`): a non-broken VI has no unwired *required* input, and `Multiply`/`Increment`/`Decrement`/
   `Subtract` expose only required inputs. On that reading the fixed sink rule *could not succeed on any
   non-broken VI*, so this is "a contradiction inside the rule, not a property of the target", and the repair
   docstring's phrase "a fact about the TARGET" relabels a design error as a discovery.
3. **It says the rule's SUCCESS case would have been a false negative too**: the only bare named inputs a
   non-broken VI can have are optional/variadic (shift registers, tunnels, Build Array, Bundle), which ADAPT to
   what is wired and so cannot exhibit a mismatch. The rule never required the sink to be *type-constrained*.
4. **Q1 — the search itself is sound.** `wire == 0` is the documented emptiness test (`gscript.py:874`), and a
   FAILED read would yield `wire = 0`, i.e. a spurious EXTRA candidate, never the observed famine; `is_source`
   is documented at `:873` and its one known trap (structure tunnels on a body diagram, `NAMES.md:930-933`)
   does not apply to arithmetic primitives. Two OTHER defects are named instead: run 1 logged a **count, not a
   census** (so "their inputs are all already wired" was inference — the corroboration cited is from the
   ORIGINAL while the target is `D1_s2_loops.vi`), and **`walk()`'s 24 nodes is truncatable and uncrosschecked**
   (`build_opstopfromnode_v0.py:133-135` stops at the first uid that reads 0; comparing `len(node_labels)` with
   `len(out)` costs zero extra COM calls).
5. **Q3 — the stated PROHIBITION survives, its stated REASON does not.** LabVIEW does not attach a second
   driver to an occupied input: `gscript.py:2411` measured *"an already-wired SINK is not safe (LabVIEW
   re-routes and the VI breaks)"*, and an NI forum thread reports `Connect Wire` onto an occupied tunnel
   terminal ERRORING, with NI's own prescription being delete-then-recreate. Occupied-terminal behaviour is
   **undocumented** by NI and the LabVIEW Wiki. It also notes the run used already-wired terminals as SOURCES
   without objection, which is correct — branching a source is safe, same line.
6. **Q4/Q5 — it proposes making a bare typed sink instead of finding one**, with ops that already exist and no
   new op: `gscript.build_index_array` `:2322-2329` (arrives UNWIRED; its `index` input is strictly numeric),
   `drop_subvi` `:1225` and `build_property` `:2194` (both take a `diagram_index`, so the sink can be made on
   `Diagram #686` itself). Its discriminating test: create the node, print every terminal triple, then
   `connect_terminals` numeric→`index` and refnum→`index` recording `(wire delta, ExecState)`, and only then the
   idempotent `Is Broken?`. Its falsifier: a freshly created node whose inputs do NOT read bare.
7. **It argues `Is Broken?` is the NOISIER of the two available instruments** — `NAMES.md:912-921` records that
   reading it PERTURBS the target and calls the mechanism OPEN, while `connect_terminals` returns
   `(wire delta, ExecState)` directly (`gscript.py:2431`) and `NAMES.md:879` already used `ExecState 1 → 0` as
   the mismatch detector.
8. **One unreported fact it adds:** handles went **30,678 → 63,416 across a 78-second run**
   (`diag_queue_typetest_control.log:10,59`) while gate G10 passed — G10 counts the *client's* references
   (6 opened / 6 closed / 0 live), not LabVIEW's handles, so it cannot see this. Against CLAUDE.md's
   "20 runs leave the handle count flat (±100)" it calls this a reference-hygiene failure measured inside the
   very run that had to restart LabVIEW because of the same growth at cycle 54's close.

**Points 1, 2, 3, 6 and 7 all bear on the DESIGN of the experiment and on whether `Is Broken?` should be the
instrument at all — that is precisely the decision Pre-decided 40's closing line reserves for judgement, so no
material session may dispose them.** Point 4's second half (the `walk()` truncation cross-check) and point 8
(handles) are mechanical and are reported as facts on the material session's `OPEN:` line.
